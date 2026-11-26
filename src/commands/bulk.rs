//! `pki cert bulk` — the Bulk Operations REST group.
//!
//! Five endpoints that act on up to 100 certificates in one call:
//! issue (from CSV), renew, revoke, delete and download (as a ZIP).
//!
//! Certificate IDs are accepted as repeatable `--id` flags, as a comma-separated
//! list, or via `--ids-file` (one ID per line) so the commands compose with
//! `pki cert list -o json | jq -r '.items[].id'`.

use std::io::{IsTerminal, Read};
use std::path::{Path, PathBuf};

use anyhow::{Context, Result, bail};
use base64::Engine;
use clap::{Args, Subcommand};
use serde_json::{Value, json};

use super::{Format, body, confirm, write_file};
use crate::api::Api;
use crate::output;

const MAX_BATCH: usize = 100;

const REVOKE_REASONS: [&str; 8] = [
    "affiliationChanged",
    "caCompromise",
    "certificateHold",
    "cessationOfOperation",
    "keyCompromise",
    "privilegeWithdrawn",
    "superseded",
    "unspecified",
];

const DOWNLOAD_FORMATS: [&str; 15] = [
    "pem",
    "crt",
    "der",
    "cer",
    "pem-chain",
    "pem-key",
    "pkcs7",
    "p7b",
    "pkcs12",
    "pfx",
    "p12",
    "jks-keystore",
    "jks-truststore",
    "docker-volume",
    "all",
];

#[derive(Args, Debug)]
pub struct Ids {
    /// Certificate ID (repeatable; also accepts a comma-separated list)
    #[arg(short = 'i', long = "id")]
    ids: Vec<String>,
    /// File with one certificate ID per line ('-' reads stdin)
    #[arg(long)]
    ids_file: Option<PathBuf>,
}

#[derive(Subcommand, Debug)]
pub enum BulkCmd {
    /// Issue certificates in bulk from a CSV file.
    ///
    /// Each line is `certificateType,CN,O,C,SANs,validityDays`. Only the first
    /// four fields are required; SANs are semicolon-separated and classified into
    /// DNS / IP / email by their shape. The API treats every line as data, so a
    /// `certificateType,...` header line is stripped here before sending.
    Issue {
        /// CA ID to issue from
        #[arg(long = "ca")]
        ca_id: String,
        /// CSV file: certificateType,CN,O,C,SANs,validityDays ('-' reads stdin)
        #[arg(long = "csv")]
        csv_file: PathBuf,
        /// Default validity in days for rows that omit it
        #[arg(short, long, allow_negative_numbers = true)]
        validity: Option<i64>,
        /// Output format: table, json
        #[arg(short, long, value_enum, default_value_t)]
        output: Format,
    },
    /// Renew certificates in bulk.
    Renew {
        #[command(flatten)]
        ids: Ids,
        /// Validity in days (defaults to the original validity)
        #[arg(short, long, allow_negative_numbers = true)]
        validity: Option<i64>,
        /// Generate a fresh key pair for the renewal [default]
        #[arg(long, overrides_with = "same_key")]
        new_key: bool,
        /// Reuse the existing key pair for the renewal
        #[arg(long, overrides_with = "new_key")]
        same_key: bool,
        /// Revoke each original certificate after renewal
        #[arg(long)]
        revoke_original: bool,
        /// Output format: table, json
        #[arg(short, long, value_enum, default_value_t)]
        output: Format,
    },
    /// Revoke certificates in bulk.
    Revoke {
        /// Revocation reason (e.g. keyCompromise, superseded)
        #[arg(short, long, value_parser = REVOKE_REASONS)]
        reason: String,
        #[command(flatten)]
        ids: Ids,
        /// Free-text detail recorded with the revocation
        #[arg(long)]
        details: Option<String>,
        /// Regenerate the CRL afterwards [default]
        #[arg(long, overrides_with = "no_generate_crl")]
        generate_crl: bool,
        /// Do not regenerate the CRL afterwards
        #[arg(long, overrides_with = "generate_crl")]
        no_generate_crl: bool,
        /// Skip confirmation
        #[arg(short, long)]
        force: bool,
        /// Output format: table, json
        #[arg(short, long, value_enum, default_value_t)]
        output: Format,
    },
    /// Delete certificates in bulk (irreversible).
    Delete {
        #[command(flatten)]
        ids: Ids,
        /// Also destroy the private key in the KMS [default]
        #[arg(long, overrides_with = "keep_key")]
        destroy_key: bool,
        /// Keep the private key in the KMS
        #[arg(long, overrides_with = "destroy_key")]
        keep_key: bool,
        /// Drop the entries from the CRL (not recommended)
        #[arg(long)]
        remove_from_crl: bool,
        /// Skip confirmation
        #[arg(short, long)]
        force: bool,
        /// Output format: table, json
        #[arg(short, long, value_enum, default_value_t)]
        output: Format,
    },
    /// Download certificates in bulk as a ZIP archive.
    Download {
        #[command(flatten)]
        ids: Ids,
        /// pem, crt, der, cer, pem-chain, pem-key, pkcs7, p7b, pkcs12, pfx, p12, jks-keystore, jks-truststore, docker-volume, all
        #[arg(short = 'f', long = "format", default_value = "pem", value_parser = DOWNLOAD_FORMATS)]
        format: String,
        /// Password for encrypted formats (min 8 chars)
        #[arg(short, long)]
        password: Option<String>,
        /// Encrypt the private key with the password [default]
        #[arg(long, overrides_with = "no_encrypt_key")]
        encrypt_key: bool,
        /// Do not encrypt the private key
        #[arg(long, overrides_with = "encrypt_key")]
        no_encrypt_key: bool,
        /// ZIP destination (defaults to the server-suggested name)
        #[arg(long)]
        output_file: Option<PathBuf>,
    },
}

pub fn run(api: &Api, cmd: BulkCmd) -> Result<()> {
    match cmd {
        BulkCmd::Issue {
            ca_id,
            csv_file,
            validity,
            output,
        } => {
            let mut csv_data = read_text(&csv_file)?;
            if csv_data.trim().is_empty() {
                bail!("CSV data is empty");
            }
            let lines = splitlines(csv_data.trim());
            let is_header = lines.first().is_some_and(|l| {
                l.split(',').next().unwrap_or("").trim().to_lowercase() == "certificatetype"
            });
            if is_header {
                output::note("Skipping CSV header row");
                csv_data = lines[1..].join("\n");
                if csv_data.trim().is_empty() {
                    bail!("CSV contains only a header row");
                }
            }
            let req = body([
                ("caId", json!(parse_uuid(&ca_id)?)),
                ("csvData", json!(csv_data)),
                ("defaultValidityDays", json!(validity.filter(|v| *v != 0))),
            ]);
            let data = api.post("/certificates/bulk/issue").json(req).value()?;
            report(&data, output, "Bulk issue results")
        }
        BulkCmd::Renew {
            ids,
            validity,
            new_key: _,
            same_key,
            revoke_original,
            output,
        } => {
            let req = body([
                ("certificateIds", json!(collect_ids(&ids)?)),
                ("generateNewKey", json!(!same_key)),
                ("validityDays", json!(validity.filter(|v| *v != 0))),
                ("revokeOriginal", json!(revoke_original)),
            ]);
            let data = api.post("/certificates/bulk/renew").json(req).value()?;
            report(&data, output, "Bulk renew results")
        }
        BulkCmd::Revoke {
            reason,
            ids,
            details,
            generate_crl: _,
            no_generate_crl,
            force,
            output,
        } => {
            let cert_ids = collect_ids(&ids)?;
            confirm(
                &format!(
                    "Revoke {} certificate(s) with reason '{reason}'?",
                    cert_ids.len()
                ),
                force,
            )?;
            let req = body([
                ("certificateIds", json!(cert_ids)),
                ("reason", json!(reason)),
                ("details", json!(details.filter(|d| !d.is_empty()))),
                ("generateCrl", json!(!no_generate_crl)),
            ]);
            let data = api.post("/certificates/bulk/revoke").json(req).value()?;
            report(&data, output, "Bulk revoke results")
        }
        BulkCmd::Delete {
            ids,
            destroy_key: _,
            keep_key,
            remove_from_crl,
            force,
            output,
        } => {
            let cert_ids = collect_ids(&ids)?;
            confirm(
                &format!(
                    "DELETE {} certificate(s)? This is irreversible!",
                    cert_ids.len()
                ),
                force,
            )?;
            let req = body([
                ("certificateIds", json!(cert_ids)),
                ("destroyKey", json!(!keep_key)),
                ("removeFromCrl", json!(remove_from_crl)),
            ]);
            let data = api.delete("/certificates/bulk/").json(req).value()?;
            report(&data, output, "Bulk delete results")
        }
        BulkCmd::Download {
            ids,
            format,
            password,
            encrypt_key: _,
            no_encrypt_key,
            output_file,
        } => {
            let req = body([
                ("certificateIds", json!(collect_ids(&ids)?)),
                ("format", json!(format)),
                ("password", json!(password.filter(|p| !p.is_empty()))),
                ("encryptPrivateKey", json!(!no_encrypt_key)),
            ]);
            let data = api.post("/certificates/bulk/download").json(req).value()?;
            let Some(b64) = data
                .get("data")
                .and_then(Value::as_str)
                .filter(|s| !s.is_empty())
            else {
                output::warning("The server returned no archive data");
                return Err(super::SilentExit.into());
            };
            let path = output_file.unwrap_or_else(|| {
                PathBuf::from(
                    data.get("filename")
                        .and_then(Value::as_str)
                        .filter(|s| !s.is_empty())
                        .unwrap_or("certificates.zip"),
                )
            });
            let clean: String = b64.chars().filter(|c| !c.is_whitespace()).collect();
            let payload = base64::engine::general_purpose::STANDARD
                .decode(clean)
                .context("The response data is not valid base64")?;
            write_file(&path, &payload)?;
            output::success(&format!(
                "Saved {} bytes to {}",
                payload.len(),
                path.display()
            ));
            Ok(())
        }
    }
}

/// Read a file, or stdin for `-`.
fn read_text(path: &Path) -> Result<String> {
    if path.as_os_str() == "-" {
        let mut s = String::new();
        std::io::stdin()
            .read_to_string(&mut s)
            .context("Cannot read stdin")?;
        Ok(s)
    } else {
        std::fs::read_to_string(path).with_context(|| format!("Cannot read {}", path.display()))
    }
}

/// Merge `--id` flags and `--ids-file` into a validated, de-duplicated list.
fn collect_ids(ids: &Ids) -> Result<Vec<String>> {
    let mut raw: Vec<String> = Vec::new();
    for value in &ids.ids {
        raw.extend(value.split(',').map(|p| p.trim().to_string()));
    }
    if let Some(file) = &ids.ids_file {
        let text = read_text(file)?;
        raw.extend(splitlines(&text).into_iter().map(|l| l.trim().to_string()));
    }
    let mut seen: Vec<String> = Vec::new();
    for value in raw {
        if !value.is_empty() && !seen.contains(&value) {
            seen.push(value);
        }
    }
    if seen.is_empty() {
        bail!("No certificate IDs given — pass --id (repeatable) and/or --ids-file");
    }
    if seen.len() > MAX_BATCH {
        bail!(
            "{} IDs given, but the API accepts at most {MAX_BATCH} per call",
            seen.len()
        );
    }
    seen.iter()
        .map(|v| parse_uuid(v).map_err(|e| anyhow::anyhow!("Invalid certificate ID: {e}")))
        .collect()
}

/// Render a bulk `{successful, failed, results[]}` response; exit 1 when any failed.
fn report(data: &Value, format: Format, title: &str) -> Result<()> {
    if format.is_json() {
        output::json(data);
    } else {
        let results = data
            .get("results")
            .and_then(Value::as_array)
            .cloned()
            .unwrap_or_default();
        output::records(&results, None, Some(title));
        let successful = data
            .get("successful")
            .map(py_str)
            .unwrap_or_else(|| "0".into());
        let failed_text = data.get("failed").map(py_str).unwrap_or_else(|| "0".into());
        let tty = std::io::stdout().is_terminal()
            && std::env::var_os("NO_COLOR").is_none_or(|v| v.is_empty());
        let paint = |s: String, code: &str| {
            if tty {
                format!("\x1b[{code}m{s}\x1b[0m")
            } else {
                s
            }
        };
        let failed_part = if truthy(data.get("failed")) {
            paint(format!("{failed_text} failed"), "31")
        } else {
            "0 failed".into()
        };
        println!(
            "{}, {failed_part}",
            paint(format!("{successful} succeeded"), "32")
        );
    }
    if truthy(data.get("failed")) {
        // Exit 1 with no extra message: the summary above says what failed.
        return Err(super::SilentExit.into());
    }
    Ok(())
}

/// Python truthiness of a JSON value (`None`/absent is false).
fn truthy(v: Option<&Value>) -> bool {
    match v {
        None | Some(Value::Null) => false,
        Some(Value::Bool(b)) => *b,
        Some(Value::Number(n)) => n.as_f64().is_some_and(|f| f != 0.0),
        Some(Value::String(s)) => !s.is_empty(),
        Some(Value::Array(a)) => !a.is_empty(),
        Some(Value::Object(o)) => !o.is_empty(),
    }
}

// ---- helpers shared with crl.rs / audit.rs ---------------------------------------

/// Python `str()` of a JSON value, for messages ported from f-strings.
pub(super) fn py_str(v: &Value) -> String {
    match v {
        Value::Null => "None".into(),
        Value::Bool(true) => "True".into(),
        Value::Bool(false) => "False".into(),
        Value::String(s) => s.clone(),
        other => output::scalar(other),
    }
}

/// Python `repr()` of a string.
pub(super) fn py_repr(s: &str) -> String {
    let quote = if s.contains('\'') && !s.contains('"') {
        '"'
    } else {
        '\''
    };
    let mut out = String::from(quote);
    for c in s.chars() {
        match c {
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if c == quote => {
                out.push('\\');
                out.push(c);
            }
            c => out.push(c),
        }
    }
    out.push(quote);
    out
}

/// Python `uuid.UUID(value)` then `str()`: braces, `urn:uuid:` and hyphens are
/// accepted; the result is the canonical lowercase form.
pub(super) fn parse_uuid(value: &str) -> Result<String> {
    let s = value.replace("urn:", "").replace("uuid:", "");
    let hex: String = s.trim_matches(|c| c == '{' || c == '}').replace('-', "");
    if hex.len() != 32 || !hex.bytes().all(|b| b.is_ascii_hexdigit()) {
        bail!("badly formed hexadecimal UUID string");
    }
    let h = hex.to_lowercase();
    Ok(format!(
        "{}-{}-{}-{}-{}",
        &h[0..8],
        &h[8..12],
        &h[12..16],
        &h[16..20],
        &h[20..32]
    ))
}

/// Python `str.splitlines()`: split on every line boundary, drop the terminators.
pub(super) fn splitlines(text: &str) -> Vec<&str> {
    let mut lines = Vec::new();
    let mut start = 0;
    let mut chars = text.char_indices().peekable();
    while let Some((i, c)) = chars.next() {
        let is_break = matches!(
            c,
            '\n' | '\r'
                | '\x0b'
                | '\x0c'
                | '\x1c'
                | '\x1d'
                | '\x1e'
                | '\u{85}'
                | '\u{2028}'
                | '\u{2029}'
        );
        if is_break {
            lines.push(&text[start..i]);
            let mut end = i + c.len_utf8();
            if c == '\r'
                && let Some(&(j, '\n')) = chars.peek()
            {
                chars.next();
                end = j + 1;
            }
            start = end;
        }
    }
    if start < text.len() {
        lines.push(&text[start..]);
    }
    lines
}

#[cfg(test)]
mod tests {
    use super::*;
    use clap::{CommandFactory, Parser};

    #[derive(Parser)]
    struct T {
        #[command(subcommand)]
        c: BulkCmd,
    }

    #[test]
    fn command_definition_is_valid() {
        T::command().debug_assert();
    }

    #[test]
    fn flag_pairs() {
        let t = T::try_parse_from(["t", "renew", "-i", "a", "--same-key", "--new-key"]).unwrap();
        let BulkCmd::Renew { same_key, .. } = t.c else {
            panic!()
        };
        assert!(!same_key);
        let t = T::try_parse_from(["t", "renew", "-i", "a", "--new-key", "--same-key"]).unwrap();
        let BulkCmd::Renew { same_key, .. } = t.c else {
            panic!()
        };
        assert!(same_key);
        assert!(T::try_parse_from(["t", "revoke", "-r", "bogus", "-i", "a"]).is_err());
        assert!(T::try_parse_from(["t", "download", "-f", "zip", "-i", "a"]).is_err());
    }

    #[test]
    fn uuids() {
        let c = "12345678-1234-1234-1234-1234567890ab";
        assert_eq!(parse_uuid(c).unwrap(), c);
        assert_eq!(
            parse_uuid("{12345678123412341234123456789ABC}").unwrap(),
            "12345678-1234-1234-1234-123456789abc"
        );
        assert_eq!(parse_uuid(&format!("urn:uuid:{c}")).unwrap(), c);
        assert_eq!(
            parse_uuid("nope").unwrap_err().to_string(),
            "badly formed hexadecimal UUID string"
        );
    }

    #[test]
    fn collects_ids() {
        let a = "12345678-1234-1234-1234-1234567890ab";
        let b = "22345678-1234-1234-1234-1234567890ab";
        let dir = tempfile::tempdir().unwrap();
        let f = dir.path().join("ids");
        std::fs::write(&f, format!("{b}\r\n\n{a}\n")).unwrap();
        let ids = Ids {
            ids: vec![format!("{a}, {b}"), a.into()],
            ids_file: Some(f),
        };
        assert_eq!(
            collect_ids(&ids).unwrap(),
            vec![a.to_string(), b.to_string()]
        );
        let empty = Ids {
            ids: vec![" , ".into()],
            ids_file: None,
        };
        assert!(
            collect_ids(&empty)
                .unwrap_err()
                .to_string()
                .starts_with("No certificate IDs given")
        );
        let bad = Ids {
            ids: vec!["x".into()],
            ids_file: None,
        };
        assert_eq!(
            collect_ids(&bad).unwrap_err().to_string(),
            "Invalid certificate ID: badly formed hexadecimal UUID string"
        );
        let many = Ids {
            ids: (0..101).map(|i| format!("{i:032x}")).collect(),
            ids_file: None,
        };
        assert_eq!(
            collect_ids(&many).unwrap_err().to_string(),
            "101 IDs given, but the API accepts at most 100 per call"
        );
    }

    #[test]
    fn python_helpers() {
        assert_eq!(splitlines("a\r\nb\rc\nd\n"), vec!["a", "b", "c", "d"]);
        assert_eq!(splitlines("a\n\nb"), vec!["a", "", "b"]);
        assert!(splitlines("").is_empty());
        assert_eq!(py_repr("x"), "'x'");
        assert_eq!(py_repr("it's"), "\"it's\"");
        assert_eq!(py_str(&json!(null)), "None");
        assert_eq!(py_str(&json!(3)), "3");
        assert!(truthy(Some(&json!(2))));
        assert!(!truthy(Some(&json!(0))));
        assert!(!truthy(None));
    }
}
