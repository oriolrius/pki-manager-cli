//! `pki cert` — certificate management.

use std::path::PathBuf;

use anyhow::{Result, bail};
use clap::{Args, Subcommand};
use serde_json::{Value, json};

use super::ca::{REVOCATION_REASON_HELP, REVOCATION_REASONS, opt, suggested};
use super::{Format, body, bulk, confirm, non_empty, render, write_base64};
use crate::api::Api;
use crate::output::{self, Panel, Tone};

pub const CERT_TYPES: [&str; 5] = ["server", "client", "dual", "code_signing", "email"];

const DOWNLOAD_FORMAT_HELP: &str = "Download format: pem, der, chain-pem, full-pem, full-der, csr-pem, \
     key-pem, key-der, pkcs8-pem, pkcs8-der, pkcs8-encrypted, p12/pfx, jks-keystore, jks-truststore";

const DOWNLOAD_FORMATS: [&str; 15] = [
    "pem",
    "der",
    "p12",
    "pfx",
    "jks-keystore",
    "jks-truststore",
    "chain-pem",
    "key-pem",
    "key-der",
    "pkcs8-pem",
    "pkcs8-der",
    "pkcs8-encrypted",
    "full-pem",
    "full-der",
    "csr-pem",
];

/// Friendly aliases for the API's format enum.
fn download_format(input: &str) -> Option<&'static str> {
    let lower = input.to_lowercase();
    let api = match lower.as_str() {
        "pkcs12" => "p12",
        "jks" => "jks-keystore",
        "chain" => "chain-pem",
        "key" => "key-pem",
        "csr" => "csr-pem",
        "full" => "full-pem",
        other => other,
    };
    DOWNLOAD_FORMATS.iter().copied().find(|f| *f == api)
}

/// Formats the server refuses without a password.
const PASSWORD_REQUIRED_FORMATS: [&str; 4] = ["p12", "pfx", "jks-keystore", "pkcs8-encrypted"];

#[derive(Subcommand, Debug)]
pub enum CertCmd {
    /// List certificates.
    List(ListArgs),
    /// Get certificate details.
    Get {
        /// Certificate ID (UUID)
        cert_id: String,
        /// Output format: table, json
        #[arg(short, long, value_enum, default_value_t)]
        output: Format,
    },
    /// Issue a new certificate.
    Issue(IssueArgs),
    /// Renew a certificate, optionally updating its subject or SANs.
    Renew(RenewArgs),
    /// Revoke a certificate.
    Revoke {
        /// Certificate ID (UUID)
        cert_id: String,
        #[arg(short, long, default_value = "unspecified", help = REVOCATION_REASON_HELP, value_parser = REVOCATION_REASONS)]
        reason: String,
        /// Free-text detail recorded with the revocation
        #[arg(long)]
        details: Option<String>,
        /// Unix timestamp for the effective revocation date
        #[arg(long)]
        effective_date: Option<i64>,
        /// Regenerate the CA's CRL immediately
        #[arg(long)]
        generate_crl: bool,
        /// Skip confirmation
        #[arg(short, long)]
        force: bool,
    },
    /// Delete a certificate.
    Delete {
        /// Certificate ID (UUID)
        cert_id: String,
        /// Also destroy the private key in the KMS
        #[arg(long)]
        destroy_key: bool,
        /// Drop the CRL entry (not recommended)
        #[arg(long)]
        remove_from_crl: bool,
        /// Skip confirmation
        #[arg(short, long)]
        force: bool,
    },
    /// Download a certificate, its chain, its key, or a keystore bundle.
    Download {
        /// Certificate ID (UUID)
        cert_id: String,
        /// Output file path (defaults to the server-suggested name)
        #[arg(short, long)]
        output: Option<PathBuf>,
        #[arg(short, long, default_value = "pem", help = DOWNLOAD_FORMAT_HELP)]
        format: String,
        /// Password for keystore / encrypted-key formats
        #[arg(short, long)]
        password: Option<String>,
        /// Encrypt the exported private key with --password
        #[arg(long)]
        encrypt_key: bool,
        /// Exclude the issuing chain from bundle formats
        #[arg(long)]
        no_chain: bool,
    },
    /// Bulk certificate operations (max 100 per call)
    #[command(subcommand, arg_required_else_help = true)]
    Bulk(bulk::BulkCmd),
}

#[derive(Args, Debug)]
pub struct ListArgs {
    /// Filter by CA ID
    #[arg(long = "ca")]
    ca_id: Option<String>,
    /// Filter by status
    #[arg(short, long, value_parser = ["active", "revoked", "expired"])]
    status: Option<String>,
    /// Filter by type: server, client, dual, code_signing, email
    #[arg(short = 't', long = "type", value_parser = CERT_TYPES)]
    cert_type: Option<String>,
    /// Search by subject DN, serial number, or SANs
    #[arg(short = 'q', long)]
    search: Option<String>,
    /// Sort field: createdAt, notAfter, subjectDn
    #[arg(long, value_parser = ["createdAt", "notAfter", "subjectDn"])]
    sort_by: Option<String>,
    /// Sort direction: asc, desc
    #[arg(long, value_parser = ["asc", "desc"])]
    sort_order: Option<String>,
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

#[derive(Args, Debug)]
pub struct IssueArgs {
    /// CA ID to issue from
    #[arg(long = "ca")]
    ca_id: String,
    /// Common Name
    #[arg(long = "cn")]
    common_name: String,
    /// Certificate type: server, client, dual, email, code_signing
    #[arg(short = 't', long = "type", default_value = "server", value_parser = CERT_TYPES)]
    cert_type: String,
    /// Organization
    #[arg(short = 'O', long = "org", default_value = "YMBIHQ")]
    organization: String,
    /// Country
    #[arg(short, long, default_value = "ES")]
    country: String,
    /// Organizational Unit
    #[arg(long)]
    ou: Option<String>,
    /// State/Province
    #[arg(long)]
    state: Option<String>,
    /// City
    #[arg(short, long)]
    locality: Option<String>,
    /// Key algorithm: RSA-2048, RSA-4096, ECDSA-P256, ECDSA-P384
    #[arg(short, long, default_value = "RSA-2048", value_parser = ["RSA-2048", "RSA-4096", "ECDSA-P256", "ECDSA-P384"])]
    algorithm: String,
    /// Validity in days (1-825)
    #[arg(short, long, default_value_t = 365)]
    validity: u32,
    /// DNS SANs (repeatable)
    #[arg(short, long)]
    dns: Vec<String>,
    /// IP SANs (repeatable)
    #[arg(long)]
    ip: Vec<String>,
    /// Email SANs (repeatable)
    #[arg(long)]
    email: Vec<String>,
    /// Tag (repeatable)
    #[arg(long)]
    tag: Vec<String>,
    /// Do not add the CN to the DNS SANs automatically
    #[arg(long)]
    no_cn_san: bool,
    /// Output format: table, json
    #[arg(short, long, value_enum, default_value_t)]
    output: Format,
}

#[derive(Args, Debug)]
pub struct RenewArgs {
    /// Certificate ID (UUID)
    cert_id: String,
    /// Validity in days
    #[arg(short, long, default_value_t = 365)]
    validity: u32,
    /// Generate a fresh key pair for the renewal (default)
    #[arg(long, overrides_with = "same_key")]
    new_key: bool,
    /// Keep the current key pair
    #[arg(long, overrides_with = "new_key")]
    same_key: bool,
    /// Revoke the original certificate after renewal
    #[arg(long)]
    revoke_original: bool,
    /// Apply the --cn/--org/--dns/... overrides below
    #[arg(long)]
    update_info: bool,
    /// New Common Name (implies --update-info)
    #[arg(long = "cn")]
    common_name: Option<String>,
    /// New Organization (implies --update-info)
    #[arg(short = 'O', long = "org")]
    organization: Option<String>,
    /// New Organizational Unit (implies --update-info)
    #[arg(long)]
    ou: Option<String>,
    /// New Country (implies --update-info)
    #[arg(short, long)]
    country: Option<String>,
    /// New State/Province (implies --update-info)
    #[arg(long)]
    state: Option<String>,
    /// New City (implies --update-info)
    #[arg(short, long)]
    locality: Option<String>,
    /// New DNS SAN (repeatable; implies --update-info)
    #[arg(short, long)]
    dns: Vec<String>,
    /// New IP SAN (repeatable; implies --update-info)
    #[arg(long)]
    ip: Vec<String>,
    /// New email SAN (repeatable; implies --update-info)
    #[arg(long)]
    email: Vec<String>,
    /// Output format: table, json
    #[arg(short, long, value_enum, default_value_t)]
    output: Format,
}

/// DNS SANs with the CN first (modern clients ignore the CN, so it must be a SAN too).
fn dns_with_cn(cn: &str, mut dns: Vec<String>, no_cn_san: bool) -> Vec<String> {
    if !no_cn_san && !dns.iter().any(|d| d == cn) {
        dns.insert(0, cn.to_string());
    }
    dns
}

fn renew_body(a: &RenewArgs) -> Value {
    let subject = body([
        ("commonName", opt(&a.common_name)),
        ("organization", opt(&a.organization)),
        ("organizationalUnit", opt(&a.ou)),
        ("country", opt(&a.country)),
        ("state", opt(&a.state)),
        ("locality", opt(&a.locality)),
    ]);
    let has_subject = subject.as_object().is_some_and(|m| !m.is_empty());
    // Any override implies updateInfo — the server ignores them otherwise.
    let update_info = a.update_info
        || has_subject
        || !a.dns.is_empty()
        || !a.ip.is_empty()
        || !a.email.is_empty();
    body([
        ("validityDays", json!(a.validity)),
        ("generateNewKey", json!(!a.same_key)),
        ("revokeOriginal", json!(a.revoke_original)),
        ("updateInfo", json!(update_info)),
        ("subject", if has_subject { subject } else { Value::Null }),
        ("sanDns", json!(non_empty(a.dns.clone()))),
        ("sanIp", json!(non_empty(a.ip.clone()))),
        ("sanEmail", json!(non_empty(a.email.clone()))),
    ])
}

pub fn run(api: &Api, cmd: CertCmd) -> Result<()> {
    match cmd {
        CertCmd::List(a) => {
            let data = api
                .get("/certificates/")
                .query_opt("caId", a.ca_id)
                .query_opt("status", a.status)
                .query_opt("type", a.cert_type)
                .query_opt("search", a.search.filter(|s| !s.is_empty()))
                .query_opt("sortBy", a.sort_by)
                .query_opt("sortOrder", a.sort_order)
                .query("limit", a.limit)
                .query("offset", a.offset)
                .value()?;
            render(&data, a.output, |d| {
                let items = output::items(d);
                if items.is_empty() {
                    output::line("No certificates found", Tone::Dim);
                } else {
                    print_cert_table(&items);
                    output::pagination(d, items.len(), "certificates");
                }
            });
        }
        CertCmd::Get { cert_id, output } => {
            let data = api.get(format!("/certificates/{cert_id}")).value()?;
            render(&data, output, print_cert_detail);
        }
        CertCmd::Issue(a) => {
            let dns = dns_with_cn(&a.common_name, a.dns, a.no_cn_san);
            let payload = body([
                ("caId", json!(a.ca_id)),
                ("certificateType", json!(a.cert_type)),
                (
                    "subject",
                    body([
                        ("commonName", json!(a.common_name)),
                        ("organization", json!(a.organization)),
                        ("country", json!(a.country)),
                        ("organizationalUnit", opt(&a.ou)),
                        ("state", opt(&a.state)),
                        ("locality", opt(&a.locality)),
                    ]),
                ),
                ("keyAlgorithm", json!(a.algorithm)),
                ("validityDays", json!(a.validity)),
                ("sanDns", json!(non_empty(dns))),
                ("sanIp", json!(non_empty(a.ip))),
                ("sanEmail", json!(non_empty(a.email))),
                ("tags", json!(non_empty(a.tag))),
            ]);
            let data = api.post("/certificates/").json(payload).value()?;
            if a.output.is_json() {
                output::json(&data);
            } else {
                output::success(&format!(
                    "Certificate issued: {}",
                    output::text(&data, "id")
                ));
                print_cert_detail(&data);
            }
        }
        CertCmd::Renew(a) => {
            let data = api
                .post(format!("/certificates/{}/renew", a.cert_id))
                .json(renew_body(&a))
                .value()?;
            if a.output.is_json() {
                output::json(&data);
            } else {
                output::success(&format!(
                    "Certificate renewed: {}",
                    output::text(&data, "id")
                ));
                print_cert_detail(&data);
            }
        }
        CertCmd::Revoke {
            cert_id,
            reason,
            details,
            effective_date,
            generate_crl,
            force,
        } => {
            confirm(
                &format!("Are you sure you want to revoke certificate {cert_id}?"),
                force,
            )?;
            api.post(format!("/certificates/{cert_id}/revoke"))
                .json(body([
                    ("reason", json!(reason)),
                    ("details", opt(&details)),
                    ("effectiveDate", json!(effective_date.filter(|d| *d != 0))),
                    ("generateCrl", json!(generate_crl)),
                ]))
                .value()?;
            output::success(&format!("Certificate {cert_id} revoked"));
        }
        CertCmd::Delete {
            cert_id,
            destroy_key,
            remove_from_crl,
            force,
        } => {
            confirm(
                &format!("Are you sure you want to DELETE certificate {cert_id}?"),
                force,
            )?;
            api.delete(format!("/certificates/{cert_id}"))
                .query("destroyKey", destroy_key)
                .query("removeFromCrl", remove_from_crl)
                .value()?;
            output::success(&format!("Certificate {cert_id} deleted"));
        }
        CertCmd::Download {
            cert_id,
            output: out,
            format,
            password,
            encrypt_key,
            no_chain,
        } => {
            let Some(api_format) = download_format(&format) else {
                bail!("Unknown format '{format}'. {DOWNLOAD_FORMAT_HELP}");
            };
            let password = password.filter(|p| !p.is_empty());
            if PASSWORD_REQUIRED_FORMATS.contains(&api_format) && password.is_none() {
                bail!("Password required for {format} format");
            }
            let data = api
                .get(format!("/certificates/{cert_id}/download"))
                .query("format", api_format)
                .query("encryptPrivateKey", encrypt_key)
                .query("includeChain", !no_chain)
                .header_opt("X-Export-Password", password)
                .value()?;
            let path = out.unwrap_or_else(|| suggested(&data, &format!("cert.{api_format}")));
            write_base64(&data, &path)?;
            output::success(&format!("Certificate saved to {}", path.display()));
        }
        CertCmd::Bulk(c) => bulk::run(api, c)?,
    }
    Ok(())
}

fn sans(cert: &Value) -> String {
    let values: Vec<String> = ["sanDns", "sanIp", "sanEmail"]
        .iter()
        .filter_map(|k| cert.get(*k).and_then(Value::as_array))
        .flatten()
        .map(output::scalar)
        .collect();
    if values.is_empty() {
        "-".into()
    } else {
        values.join(", ")
    }
}

pub fn print_cert_table(certs: &[Value]) {
    let mut t = output::ListTable::new(
        Some("Certificates"),
        &[
            ("ID", Tone::Dim),
            ("Common Name", Tone::Cyan),
            ("Type", Tone::Magenta),
            ("Status", Tone::Plain),
            ("Expires", Tone::Yellow),
        ],
    );
    for c in certs {
        let kind = output::first(c, &["certificateType", "type"])
            .map(output::scalar)
            .unwrap_or("-".into());
        let status = output::first(c, &["expiryStatus", "status"])
            .map(output::scalar)
            .unwrap_or("-".into());
        t.row(vec![
            output::cell(output::text(c, "id"), Tone::Dim),
            output::cell(output::extract_cn(&output::subject_of(c)), Tone::Cyan),
            output::cell(kind, Tone::Magenta),
            output::status_cell(&status),
            output::cell(output::format_date(c.get("notAfter")), Tone::Yellow),
        ]);
    }
    t.print();
}

pub fn print_cert_detail(c: &Value) {
    let mut p = Panel::new(Some("Certificate"));
    p.row("ID", output::text(c, "id"));
    p.row("CA ID", output::text(c, "caId"));
    p.row(
        "Type",
        output::first(c, &["certificateType", "type"])
            .map(output::scalar)
            .unwrap_or("-".into()),
    );
    p.row("Subject", output::subject_of(c));
    if let Some(issuer) = output::first(c, &["issuerDn"]) {
        p.row("Issuer", output::scalar(issuer));
    }
    p.row("SANs", sans(c));
    p.row("Serial Number", output::text(c, "serialNumber"));
    p.cell_row("Status", output::status_cell(&output::text(c, "status")));
    if let Some(v) = output::first(c, &["validityStatus"]) {
        p.row("Validity", output::scalar(v));
    }
    p.row("Valid From", output::format_date(c.get("notBefore")));
    p.row("Valid Until", output::format_date(c.get("notAfter")));
    if let Some(days) = c.get("remainingDays").filter(|d| !d.is_null()) {
        p.cell_row("Days Remaining", output::days_cell(days));
    }
    if let Some(eku) = c
        .get("extendedKeyUsage")
        .and_then(Value::as_array)
        .filter(|a| !a.is_empty())
    {
        p.row(
            "Extended Key Usage",
            eku.iter()
                .map(output::scalar)
                .collect::<Vec<_>>()
                .join(", "),
        );
    }
    if let Some(sha) = c
        .get("fingerprints")
        .and_then(|f| f.get("sha256"))
        .and_then(Value::as_str)
    {
        p.row("SHA-256", sha);
    }
    if let Some(from) = output::first(c, &["renewedFromId"]) {
        p.row("Renewed From", output::scalar(from));
    }
    if let Some(to) = c
        .get("renewedTo")
        .and_then(Value::as_array)
        .filter(|a| !a.is_empty())
    {
        p.row(
            "Renewed To",
            to.iter().map(output::scalar).collect::<Vec<_>>().join(", "),
        );
    }
    p.row("Created", output::format_date(c.get("createdAt")));
    // Detail responses use revocationDate; some list shapes use revokedAt.
    if let Some(revoked) = output::first(c, &["revocationDate", "revokedAt"]) {
        p.row("Revoked At", output::format_date(Some(revoked)));
        p.row(
            "Revocation Reason",
            output::first(c, &["revocationReason"])
                .map(output::scalar)
                .unwrap_or("-".into()),
        );
    }
    p.print();
}

#[cfg(test)]
mod tests {
    use super::*;
    use clap::Parser;

    #[derive(Parser)]
    struct T {
        #[command(subcommand)]
        c: CertCmd,
    }

    fn renew(args: &[&str]) -> Value {
        let mut argv = vec!["t", "renew", "id-1"];
        argv.extend_from_slice(args);
        match T::parse_from(argv).c {
            CertCmd::Renew(a) => renew_body(&a),
            _ => unreachable!(),
        }
    }

    #[test]
    fn cn_is_added_to_dns_sans() {
        assert_eq!(dns_with_cn("a", vec!["b".into()], false), vec!["a", "b"]);
        assert_eq!(
            dns_with_cn("a", vec!["b".into(), "a".into()], false),
            vec!["b", "a"]
        );
        assert_eq!(dns_with_cn("a", vec![], true), Vec::<String>::new());
    }

    #[test]
    fn renew_defaults() {
        assert_eq!(
            renew(&[]),
            json!({"validityDays": 365, "generateNewKey": true, "revokeOriginal": false, "updateInfo": false})
        );
    }

    #[test]
    fn renew_overrides_imply_update_info() {
        let b = renew(&["--same-key", "--cn", "new", "-d", "x.example"]);
        assert_eq!(b["generateNewKey"], json!(false));
        assert_eq!(b["updateInfo"], json!(true));
        assert_eq!(b["subject"], json!({"commonName": "new"}));
        assert_eq!(b["sanDns"], json!(["x.example"]));
        assert_eq!(
            renew(&["--same-key", "--new-key"])["generateNewKey"],
            json!(true)
        );
    }

    #[test]
    fn format_aliases() {
        assert_eq!(download_format("PKCS12"), Some("p12"));
        assert_eq!(download_format("chain"), Some("chain-pem"));
        assert_eq!(download_format("full-der"), Some("full-der"));
        assert_eq!(download_format("zip"), None);
    }
}
