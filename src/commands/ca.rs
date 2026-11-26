//! `pki ca` — Certificate Authority management.

use std::path::PathBuf;

use anyhow::{Result, bail};
use clap::{Args, Subcommand};
use serde_json::{Value, json};

use super::{Format, body, confirm, non_empty, render, write_base64, write_file};
use crate::api::Api;
use crate::output::{self, Panel, Tone};

pub const REVOCATION_REASONS: [&str; 8] = [
    "unspecified",
    "keyCompromise",
    "caCompromise",
    "affiliationChanged",
    "superseded",
    "cessationOfOperation",
    "certificateHold",
    "removeFromCRL",
];

pub const REVOCATION_REASON_HELP: &str = "Revocation reason: unspecified, keyCompromise, caCompromise, \
     affiliationChanged, superseded, cessationOfOperation, certificateHold, removeFromCRL";

#[derive(Subcommand, Debug)]
pub enum CaCmd {
    /// List all Certificate Authorities.
    List(ListArgs),
    /// Get CA details.
    Get {
        /// CA ID (UUID)
        ca_id: String,
        /// Output format: table, json
        #[arg(short, long, value_enum, default_value_t)]
        output: Format,
    },
    /// Create a new Certificate Authority.
    Create(CreateArgs),
    /// Revoke a Certificate Authority.
    Revoke {
        /// CA ID (UUID)
        ca_id: String,
        #[arg(short, long, default_value = "unspecified", help = REVOCATION_REASON_HELP, value_parser = REVOCATION_REASONS)]
        reason: String,
        /// Free-text detail recorded with the revocation
        #[arg(long)]
        details: Option<String>,
        /// Skip confirmation
        #[arg(short, long)]
        force: bool,
    },
    /// Delete a Certificate Authority.
    Delete {
        /// CA ID (UUID)
        ca_id: String,
        /// Also destroy the CA private key in the KMS
        #[arg(long)]
        destroy_key: bool,
        /// Skip confirmation
        #[arg(short, long)]
        force: bool,
    },
    /// List the certificates issued by a CA.
    Certs(CertsArgs),
    /// Download a CA certificate (or a truststore/keystore bundle).
    Download {
        /// CA ID (UUID)
        ca_id: String,
        /// pem, crt, der, cer, p12-truststore, p12-keystore, jks-truststore, jks-keystore
        #[arg(short, long, default_value = "pem", value_parser = ["pem", "crt", "der", "cer", "p12-truststore", "p12-keystore", "jks-truststore", "jks-keystore"])]
        format: String,
        /// Password for P12/JKS (required for keystores, defaults to 'changeit' for truststores)
        #[arg(short, long)]
        password: Option<String>,
        /// Output file path
        #[arg(short, long)]
        output: Option<PathBuf>,
    },
    /// Fetch a CA certificate from its public, unauthenticated URL.
    ///
    /// This is the same `/cas/<id>.pem` link an AIA extension points at, so it
    /// works without credentials — handy for bootstrapping trust on a new host.
    Pem {
        /// CA ID (UUID)
        ca_id: String,
        /// pem/crt (text) or der/cer (binary)
        #[arg(short, long, default_value = "pem", value_parser = ["pem", "crt", "der", "cer"])]
        format: String,
        /// Output file path
        #[arg(short, long)]
        output: Option<PathBuf>,
    },
}

#[derive(Args, Debug)]
pub struct ListArgs {
    /// Filter by status: active, revoked, expired
    #[arg(short, long, value_parser = ["active", "revoked", "expired"])]
    status: Option<String>,
    /// Search by subject or serial number
    #[arg(short = 'q', long)]
    search: Option<String>,
    /// Sort field: name, issuedDate, expiryDate
    #[arg(long, value_parser = ["name", "issuedDate", "expiryDate"])]
    sort_by: Option<String>,
    /// Sort direction: asc, desc
    #[arg(long, value_parser = ["asc", "desc"])]
    sort_order: Option<String>,
    /// Max results (1-100)
    #[arg(short, long, default_value_t = 50)]
    limit: u32,
    /// Number of CAs to skip
    #[arg(long, default_value_t = 0)]
    offset: u32,
    /// Output format: table, json
    #[arg(short, long, value_enum, default_value_t)]
    output: Format,
}

#[derive(Args, Debug)]
pub struct CreateArgs {
    /// Common Name
    #[arg(long = "cn")]
    common_name: String,
    /// Organization
    #[arg(short = 'O', long = "org", default_value = "YMBIHQ")]
    organization: String,
    /// Country (2-letter)
    #[arg(short, long, default_value = "ES")]
    country: String,
    /// State/Province
    #[arg(long)]
    state: Option<String>,
    /// City
    #[arg(short, long)]
    locality: Option<String>,
    /// Organizational Unit
    #[arg(long)]
    ou: Option<String>,
    /// Key algorithm: RSA-2048 or RSA-4096
    #[arg(short, long, default_value = "RSA-4096", value_parser = ["RSA-2048", "RSA-4096"])]
    algorithm: String,
    /// Validity in years (1-30)
    #[arg(short, long, default_value_t = 20)]
    validity_years: u32,
    /// Tag (repeatable)
    #[arg(long)]
    tag: Vec<String>,
    /// Output format: table, json
    #[arg(short, long, value_enum, default_value_t)]
    output: Format,
}

#[derive(Args, Debug)]
pub struct CertsArgs {
    /// CA ID (UUID)
    ca_id: String,
    /// Filter by status: active, revoked, expired
    #[arg(short, long, value_parser = ["active", "revoked", "expired"])]
    status: Option<String>,
    /// Filter by type: server, client, dual, code_signing, email
    #[arg(short = 't', long = "type", value_parser = super::cert::CERT_TYPES)]
    cert_type: Option<String>,
    /// Search subject DN, serial number, or SANs
    #[arg(short = 'q', long)]
    search: Option<String>,
    /// Max results (1-100)
    #[arg(short, long, default_value_t = 50)]
    limit: u32,
    /// Number of certificates to skip
    #[arg(long, default_value_t = 0)]
    offset: u32,
    /// Output format: table, json
    #[arg(short, long, value_enum, default_value_t)]
    output: Format,
}

const CA_CERT_COLUMNS: [&str; 7] = [
    "id",
    "subjectDn",
    "certificateType",
    "serialNumber",
    "status",
    "expiryStatus",
    "notAfter",
];

/// Strings or nothing, for optional subject fields (empty = unset).
pub fn opt(v: &Option<String>) -> Value {
    match v {
        Some(s) if !s.is_empty() => json!(s),
        _ => Value::Null,
    }
}

pub fn run(api: &Api, cmd: CaCmd) -> Result<()> {
    match cmd {
        CaCmd::List(a) => {
            let data = api
                .get("/cas/")
                .query_opt("status", a.status)
                .query_opt("search", a.search.filter(|s| !s.is_empty()))
                .query_opt("sortBy", a.sort_by)
                .query_opt("sortOrder", a.sort_order)
                .query("limit", a.limit)
                .query("offset", a.offset)
                .value()?;
            render(&data, a.output, |d| {
                let items = output::items(d);
                if items.is_empty() {
                    output::line("No CAs found", Tone::Dim);
                } else {
                    print_ca_table(&items);
                    output::pagination(d, items.len(), "CAs");
                }
            });
        }
        CaCmd::Get { ca_id, output } => {
            let data = api.get(format!("/cas/{ca_id}")).value()?;
            render(&data, output, print_ca_detail);
        }
        CaCmd::Create(a) => {
            let payload = body([
                (
                    "subject",
                    body([
                        ("commonName", json!(a.common_name)),
                        ("organization", json!(a.organization)),
                        ("country", json!(a.country)),
                        ("state", opt(&a.state)),
                        ("locality", opt(&a.locality)),
                        ("organizationalUnit", opt(&a.ou)),
                    ]),
                ),
                ("keyAlgorithm", json!(a.algorithm)),
                ("validityYears", json!(a.validity_years)),
                ("tags", json!(non_empty(a.tag))),
            ]);
            let data = api.post("/cas/").json(payload).value()?;
            if a.output.is_json() {
                output::json(&data);
            } else {
                output::success(&format!("CA created: {}", output::text(&data, "id")));
                print_ca_detail(&data);
            }
        }
        CaCmd::Revoke {
            ca_id,
            reason,
            details,
            force,
        } => {
            confirm(
                &format!("Are you sure you want to revoke CA {ca_id}?"),
                force,
            )?;
            api.post(format!("/cas/{ca_id}/revoke"))
                .json(body([
                    ("reason", json!(reason)),
                    ("details", opt(&details)),
                ]))
                .value()?;
            output::success(&format!("CA {ca_id} revoked"));
        }
        CaCmd::Delete {
            ca_id,
            destroy_key,
            force,
        } => {
            confirm(
                &format!("Are you sure you want to DELETE CA {ca_id}? This is irreversible!"),
                force,
            )?;
            api.delete(format!("/cas/{ca_id}"))
                .query("destroyKey", destroy_key)
                .value()?;
            output::success(&format!("CA {ca_id} deleted"));
        }
        CaCmd::Certs(a) => {
            let data = api
                .get(format!("/cas/{}/certificates", a.ca_id))
                .query_opt("status", a.status)
                .query_opt("certificateType", a.cert_type)
                .query_opt("search", a.search.filter(|s| !s.is_empty()))
                .query("limit", a.limit)
                .query("offset", a.offset)
                .value()?;
            render(&data, a.output, |d| {
                let items = output::items(d);
                output::records(
                    &items,
                    Some(&CA_CERT_COLUMNS),
                    Some(&format!("Certificates issued by {}", a.ca_id)),
                );
                if let Some(total) = d.get("pagination").and_then(|p| p.get("total")) {
                    output::line(
                        &format!("{} of {} certificates", items.len(), output::scalar(total)),
                        Tone::Dim,
                    );
                }
            });
        }
        CaCmd::Download {
            ca_id,
            format,
            password,
            output: out,
        } => {
            if format.ends_with("keystore") && password.as_deref().is_none_or(str::is_empty) {
                bail!("Password required for {format} format");
            }
            let data = api
                .get(format!("/cas/{ca_id}/download"))
                .query("format", &format)
                .header_opt("X-Export-Password", password.filter(|p| !p.is_empty()))
                .value()?;
            let path = out.unwrap_or_else(|| suggested(&data, &format!("ca.{format}")));
            write_base64(&data, &path)?;
            output::success(&format!("CA certificate saved to {}", path.display()));
        }
        CaCmd::Pem {
            ca_id,
            format,
            output: out,
        } => {
            let data = api.get(format!("/cas/{ca_id}.{format}")).public().bytes()?;
            match out {
                Some(path) => {
                    write_file(&path, &data)?;
                    output::success(&format!("Saved {} bytes to {}", data.len(), path.display()));
                }
                None if format == "pem" || format == "crt" => {
                    println!("{}", String::from_utf8_lossy(&data).trim_end_matches('\n'));
                }
                None => {
                    let path = PathBuf::from(format!("{ca_id}.{format}"));
                    write_file(&path, &data)?;
                    output::success(&format!("Saved {} bytes to {}", data.len(), path.display()));
                }
            }
        }
    }
    Ok(())
}

/// The server-suggested `filename` of a download, or `fallback`.
///
/// Only the file name is kept: a server value can never write outside the
/// current directory.
pub fn suggested(data: &Value, fallback: &str) -> PathBuf {
    data.get("filename")
        .and_then(Value::as_str)
        .and_then(|f| std::path::Path::new(f).file_name())
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from(fallback))
}

pub fn print_ca_table(cas: &[Value]) {
    let mut t = output::ListTable::new(
        Some("Certificate Authorities"),
        &[
            ("ID", Tone::Dim),
            ("Common Name", Tone::Cyan),
            ("Algorithm", Tone::Magenta),
            ("Status", Tone::Plain),
            ("Certs", Tone::Plain),
            ("Expires", Tone::Yellow),
        ],
    );
    t.right_align(4);
    for ca in cas {
        let count = output::first(ca, &["certificateCount", "issuedCertificateCount"]);
        t.row(vec![
            output::cell(output::text(ca, "id"), Tone::Dim),
            output::cell(output::extract_cn(&output::subject_of(ca)), Tone::Cyan),
            output::cell(output::text(ca, "keyAlgorithm"), Tone::Magenta),
            output::status_cell(&output::text(ca, "status")),
            output::cell(
                count.map(output::scalar).unwrap_or_else(|| "-".into()),
                Tone::Plain,
            ),
            output::cell(output::format_date(ca.get("notAfter")), Tone::Yellow),
        ]);
    }
    t.print();
}

pub fn print_ca_detail(ca: &Value) {
    let mut p = Panel::new(Some("Certificate Authority"));
    let subject = output::subject_of(ca);
    p.row("ID", output::text(ca, "id"));
    p.row("Subject", subject.clone());
    if let Some(issuer) = ca
        .get("issuerDn")
        .and_then(Value::as_str)
        .filter(|i| !i.is_empty() && *i != subject)
    {
        p.row("Issuer", issuer);
    }
    p.row("Serial Number", output::text(ca, "serialNumber"));
    p.row("Key Algorithm", output::text(ca, "keyAlgorithm"));
    p.cell_row("Status", output::status_cell(&output::text(ca, "status")));
    if let Some(v) = output::first(ca, &["validityStatus"]) {
        p.row("Validity", output::scalar(v));
    }
    p.row("Valid From", output::format_date(ca.get("notBefore")));
    p.row("Valid Until", output::format_date(ca.get("notAfter")));
    let count = output::first(ca, &["issuedCertificateCount", "certificateCount"]);
    p.row(
        "Certificates",
        count.map(output::scalar).unwrap_or_else(|| "-".into()),
    );
    if let Some(sha) = ca
        .get("fingerprints")
        .and_then(|f| f.get("sha256"))
        .and_then(Value::as_str)
    {
        p.row("SHA-256", sha);
    }
    if let Some(revoked) = output::first(ca, &["revocationDate"]) {
        p.row("Revoked At", output::format_date(Some(revoked)));
        p.row(
            "Revocation Reason",
            output::first(ca, &["revocationReason"])
                .map(output::scalar)
                .unwrap_or("-".into()),
        );
    }
    p.row("Created", output::format_date(ca.get("createdAt")));
    p.print();
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn suggested_name_is_a_bare_file_name() {
        assert_eq!(
            suggested(&json!({"filename": "../../etc/x.pem"}), "ca.pem"),
            PathBuf::from("x.pem")
        );
        assert_eq!(
            suggested(&json!({"filename": "root.crt"}), "ca.pem"),
            PathBuf::from("root.crt")
        );
        assert_eq!(suggested(&json!({}), "ca.pem"), PathBuf::from("ca.pem"));
    }
}
