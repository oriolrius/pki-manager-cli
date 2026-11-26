//! `pki external` — machine-facing issuer endpoints.
//!
//! Two token-authenticated surfaces the CLI can drive for automation/testing:
//!
//! * `/api/v1/external/*` — the cert-manager issuer API, authenticated with a
//!   **cluster token** (`pkimg_...`, one token per CA). Set via `--token` or
//!   `PKI_CLUSTER_TOKEN`.
//! * `/api/v1/external/ssh/*` — the SSH fleet automation API, authenticated with a
//!   **fleet token** (minted via `pki ssh token mint`). Set via `--token` or
//!   `PKI_FLEET_TOKEN`. The ECIES `krl` endpoint takes no token.
//!
//! These bypass the OIDC login the rest of the CLI uses — they carry their own
//! bearer token ([`crate::api::Req::bearer`]).

use std::path::PathBuf;

use anyhow::{Result, bail};
use clap::{Args, Subcommand};
use serde_json::{Value, json};

use super::{Format, body, non_empty, read_value_or_file, write_file};
use crate::api::Api;
use crate::output;

#[derive(Args, Debug)]
pub struct ClusterToken {
    /// Cluster bearer token (pkimg_...)
    #[arg(long = "token", env = "PKI_CLUSTER_TOKEN", hide_env_values = true)]
    token: Option<String>,
}

impl ClusterToken {
    fn require(self) -> Result<Option<String>> {
        require(self.token, "PKI_CLUSTER_TOKEN")
    }
}

#[derive(Args, Debug)]
pub struct FleetToken {
    /// Fleet bearer token
    #[arg(long = "token", env = "PKI_FLEET_TOKEN", hide_env_values = true)]
    token: Option<String>,
}

impl FleetToken {
    fn require(self) -> Result<Option<String>> {
        require(self.token, "PKI_FLEET_TOKEN")
    }
}

/// `-o/--output`, JSON by default for these machine-facing commands.
#[derive(Args, Debug)]
pub struct Out {
    /// Output format: table, json
    #[arg(short, long, value_enum, default_value_t = Format::Json)]
    output: Format,
}

#[derive(Subcommand, Debug)]
pub enum ExternalCmd {
    /// Liveness check + cluster identity for a cluster token.
    Health {
        #[command(flatten)]
        token: ClusterToken,
        #[command(flatten)]
        out: Out,
    },
    /// Fetch the PEM chain of the cluster's CA.
    CaBundle {
        #[command(flatten)]
        token: ClusterToken,
        /// Write the PEM chain to a file
        #[arg(long)]
        output_file: Option<PathBuf>,
        #[command(flatten)]
        out: Out,
    },
    /// Sign a CSR with the cluster's CA (returns cert + chain).
    Sign {
        /// CSR in PEM (or @file)
        #[arg(long)]
        csr: String,
        /// Idempotency key for this signing request
        #[arg(long)]
        request_uid: String,
        #[command(flatten)]
        token: ClusterToken,
        /// Certificate lifetime in days (1-825)
        #[arg(long, allow_negative_numbers = true)]
        duration_days: Option<i64>,
        /// server, client, or dual
        #[arg(short = 't', long = "type")]
        cert_type: Option<String>,
        /// k8s namespace (recorded)
        #[arg(long)]
        k8s_namespace: Option<String>,
        /// k8s resource (recorded)
        #[arg(long)]
        k8s_resource: Option<String>,
        /// DNS SAN (repeatable; usually taken from the CSR)
        #[arg(short, long)]
        dns: Vec<String>,
        /// IP SAN (repeatable)
        #[arg(long)]
        ip: Vec<String>,
        #[command(flatten)]
        out: Out,
    },
    /// Revoke a certificate (by serial) that this cluster issued.
    Revoke {
        /// Serial number of the certificate to revoke
        #[arg(long)]
        serial: String,
        #[command(flatten)]
        token: ClusterToken,
        /// Revocation reason
        #[arg(short, long)]
        reason: Option<String>,
        #[command(flatten)]
        out: Out,
    },
    /// Check that a certificate this integration issued is active (the SCEP renewal check).
    ///
    /// `active` is false for a missing, expired or revoked certificate, and for
    /// one that another integration owns.
    CertificateStatus {
        /// Certificate serial number (hex)
        serial: String,
        #[command(flatten)]
        token: ClusterToken,
        #[command(flatten)]
        out: Out,
    },
    /// Fleet-token SSH automation (sign-host, sign-user, KRL)
    #[command(subcommand, arg_required_else_help = true)]
    Ssh(SshExtCmd),
    /// SCEP registration authority key operations (SCEP integration token)
    #[command(subcommand, arg_required_else_help = true)]
    Ra(RaCmd),
}

#[derive(Subcommand, Debug)]
pub enum RaCmd {
    /// Show the state of the integration's SCEP RA key and certificate.
    State {
        #[command(flatten)]
        token: ClusterToken,
        #[command(flatten)]
        out: Out,
    },
    /// Create the integration's SCEP RA key and certificate.
    Provision {
        #[command(flatten)]
        token: ClusterToken,
        #[command(flatten)]
        out: Out,
    },
    /// Renew the integration's SCEP RA certificate.
    Renew {
        #[command(flatten)]
        token: ClusterToken,
        #[command(flatten)]
        out: Out,
    },
    /// Sign a digest with the RA key (the result is base64 in `data`).
    Sign {
        /// Digest to sign, base64 (or @file)
        #[arg(long)]
        digest: String,
        #[command(flatten)]
        token: ClusterToken,
        #[command(flatten)]
        out: Out,
    },
    /// Decrypt a value with the RA key (the result is base64 in `data`).
    Decrypt {
        /// Ciphertext to decrypt, base64 (or @file)
        #[arg(long)]
        data: String,
        /// Expected CMS content-encryption key length in bytes: 16, 24 or 32
        /// (16: AES-128, 24: 3DES, 32: AES-256). Omit it to send the legacy request.
        #[arg(long, value_name = "BYTES", value_parser = parse_session_key_length)]
        session_key_length: Option<u8>,
        #[command(flatten)]
        token: ClusterToken,
        #[command(flatten)]
        out: Out,
    },
}

#[derive(Subcommand, Debug)]
pub enum SshExtCmd {
    /// Register (upsert) a host and issue its host certificate.
    SignHost {
        /// Host FQDN
        #[arg(long)]
        fqdn: String,
        /// OpenSSH host public key (or @file)
        #[arg(short = 'k', long)]
        pubkey: String,
        #[command(flatten)]
        token: FleetToken,
        /// Host address (repeatable)
        #[arg(short, long)]
        address: Vec<String>,
        /// Validity in seconds
        #[arg(long, visible_alias = "ttl", allow_negative_numbers = true)]
        valid_for_seconds: Option<i64>,
        /// Certificate key_id
        #[arg(long)]
        key_id: Option<String>,
        /// Idempotency-Key header
        #[arg(long)]
        idempotency_key: Option<String>,
        #[command(flatten)]
        out: Out,
    },
    /// Ensure an identity exists and issue a user certificate.
    SignUser {
        /// Identity subject
        #[arg(short, long)]
        subject: String,
        /// User's SSH public key (or @file)
        #[arg(short = 'k', long)]
        pubkey: String,
        #[command(flatten)]
        token: FleetToken,
        /// Principal/role (repeatable, at least one)
        #[arg(short, long)]
        principal: Vec<String>,
        /// SSH extension (repeatable)
        #[arg(short, long)]
        extension: Vec<String>,
        /// force-command restriction
        #[arg(long)]
        force_command: Option<String>,
        /// source-address CIDR list
        #[arg(long)]
        source_address: Option<String>,
        /// Validity in seconds
        #[arg(long, visible_alias = "ttl", allow_negative_numbers = true)]
        valid_for_seconds: Option<i64>,
        /// Certificate key_id
        #[arg(long)]
        key_id: Option<String>,
        /// Idempotency-Key header
        #[arg(long)]
        idempotency_key: Option<String>,
        #[command(flatten)]
        out: Out,
    },
    /// Confirm a host is eligible for encrypted (ECIES) KRL distribution.
    RegisterHostPubkey {
        /// Host FQDN
        #[arg(long)]
        fqdn: String,
        #[command(flatten)]
        token: FleetToken,
        #[command(flatten)]
        out: Out,
    },
    /// Fetch a host's rendered AuthorizedPrincipalsFile map (host self-serve).
    AuthPrincipals {
        /// Host FQDN
        fqdn: String,
        #[command(flatten)]
        token: FleetToken,
        #[command(flatten)]
        out: Out,
    },
    /// Confirm that a host installed its principal files (clears its Stale flag).
    ///
    /// The server accepts the confirmation only when `--sha256` matches the
    /// current render; if the maps changed in the meantime it answers 409.
    PrincipalsPushed {
        /// Host FQDN
        fqdn: String,
        /// sha256 of the installed principal files (the value `auth-principals` gave)
        #[arg(long)]
        sha256: String,
        #[command(flatten)]
        token: FleetToken,
        #[command(flatten)]
        out: Out,
    },
    /// Fetch a host's ECIES-encrypted KRL envelope (no token; only the host can decrypt).
    Krl {
        /// Host FQDN whose encrypted KRL to fetch
        #[arg(long)]
        host_id: String,
        /// Zone ID or name (required once more than one zone is active)
        #[arg(long)]
        zone: Option<String>,
        /// Output file for the ECIES ciphertext
        #[arg(short = 'o', long = "output")]
        output_file: Option<PathBuf>,
    },
}

fn require(token: Option<String>, env_name: &str) -> Result<Option<String>> {
    match token.filter(|t| !t.is_empty()) {
        Some(t) => Ok(Some(t)),
        None => bail!("A bearer token is required — pass --token or set {env_name}"),
    }
}

/// JSON verbatim, or a table for a list, a panel for an object, the text otherwise.
fn render(data: &Value, format: Format, title: Option<&str>) {
    if format.is_json() {
        output::json(data);
        return;
    }
    match data {
        Value::Array(items) => output::records(items, None, title),
        Value::Object(_) => output::kv(data, title),
        Value::String(s) => println!("{s}"),
        other => println!("{}", super::bulk::py_str(other)),
    }
}

/// `read_value_or_file(v).strip()`.
fn stripped(value: String) -> Result<String> {
    Ok(read_value_or_file(Some(value))?
        .unwrap_or_default()
        .trim()
        .to_string())
}

pub fn run(api: &Api, cmd: ExternalCmd) -> Result<()> {
    match cmd {
        ExternalCmd::Health { token, out } => {
            render(
                &api.get("/external/health")
                    .bearer(token.require()?)
                    .value()?,
                out.output,
                None,
            );
        }
        ExternalCmd::CaBundle {
            token,
            output_file,
            out,
        } => {
            let data = api
                .get("/external/ca-bundle")
                .bearer(token.require()?)
                .value()?;
            let chain = data
                .get("chainPem")
                .and_then(Value::as_str)
                .filter(|s| !s.is_empty());
            match (output_file, chain) {
                (Some(path), Some(pem)) => {
                    write_file(&path, pem.as_bytes())?;
                    output::success(&format!("CA chain written to {}", path.display()));
                }
                _ => render(&data, out.output, None),
            }
        }
        ExternalCmd::Sign {
            csr,
            request_uid,
            token,
            duration_days,
            cert_type,
            k8s_namespace,
            k8s_resource,
            dns,
            ip,
            out,
        } => {
            let req = body([
                ("csrPem", json!(read_value_or_file(Some(csr))?)),
                ("requestUid", json!(request_uid)),
                ("durationDays", json!(duration_days)),
                ("certificateType", json!(cert_type)),
                ("k8sNamespace", json!(k8s_namespace)),
                ("k8sResource", json!(k8s_resource)),
                ("sanDns", json!(non_empty(dns))),
                ("sanIp", json!(non_empty(ip))),
            ]);
            let data = api
                .post("/external/sign")
                .bearer(token.require()?)
                .json(req)
                .value()?;
            output::success("CSR signed");
            render(&data, out.output, None);
        }
        ExternalCmd::Revoke {
            serial,
            token,
            reason,
            out,
        } => {
            let req = body([("serialNumber", json!(serial)), ("reason", json!(reason))]);
            let data = api
                .post("/external/revoke")
                .bearer(token.require()?)
                .json(req)
                .value()?;
            output::success("Certificate revoked");
            render(&data, out.output, None);
        }
        ExternalCmd::CertificateStatus { serial, token, out } => {
            let data = api
                .get(format!("/external/certificate-status/{serial}"))
                .bearer(token.require()?)
                .value()?;
            render(&data, out.output, None);
        }
        ExternalCmd::Ra(c) => run_ra(api, c)?,
        ExternalCmd::Ssh(c) => run_ssh(api, c)?,
    }
    Ok(())
}

fn run_ra(api: &Api, cmd: RaCmd) -> Result<()> {
    match cmd {
        RaCmd::State { token, out } => {
            render(
                &api.get("/external/ra/state")
                    .bearer(token.require()?)
                    .value()?,
                out.output,
                None,
            );
        }
        RaCmd::Provision { token, out } => {
            let data = api
                .post("/external/ra/provision")
                .bearer(token.require()?)
                .json(json!({}))
                .value()?;
            output::success("RA provisioned");
            render(&data, out.output, None);
        }
        RaCmd::Renew { token, out } => {
            let data = api
                .post("/external/ra/renew")
                .bearer(token.require()?)
                .json(json!({}))
                .value()?;
            output::success("RA renewed");
            render(&data, out.output, None);
        }
        RaCmd::Sign { digest, token, out } => {
            let req = json!({ "digest": stripped(digest)? });
            render(
                &api.post("/external/ra/sign")
                    .bearer(token.require()?)
                    .json(req)
                    .value()?,
                out.output,
                None,
            );
        }
        RaCmd::Decrypt {
            data,
            session_key_length,
            token,
            out,
        } => {
            let req = decrypt_body(stripped(data)?, session_key_length);
            render(
                &api.post("/external/ra/decrypt")
                    .bearer(token.require()?)
                    .json(req)
                    .value()?,
                out.output,
                None,
            );
        }
    }
    Ok(())
}

/// Session-key lengths (bytes) the RA decrypt endpoint accepts: 16 (AES-128), 24 (3DES), 32 (AES-256).
const SESSION_KEY_LENGTHS: [u8; 3] = [16, 24, 32];

fn parse_session_key_length(s: &str) -> std::result::Result<u8, String> {
    s.parse::<u8>()
        .ok()
        .filter(|n| SESSION_KEY_LENGTHS.contains(n))
        .ok_or_else(|| format!("must be 16, 24 or 32 (got `{s}`)"))
}

/// Body of `POST /external/ra/decrypt`. Without a session-key length it is the
/// legacy `{"data": ...}` request; with one it adds a numeric `sessionKeyLength`.
fn decrypt_body(data: String, session_key_length: Option<u8>) -> Value {
    let mut req = json!({ "data": data });
    if let Some(n) = session_key_length {
        req["sessionKeyLength"] = json!(n);
    }
    req
}

fn run_ssh(api: &Api, cmd: SshExtCmd) -> Result<()> {
    match cmd {
        SshExtCmd::SignHost {
            fqdn,
            pubkey,
            token,
            address,
            valid_for_seconds,
            key_id,
            idempotency_key,
            out,
        } => {
            let req = body([
                ("fqdn", json!(fqdn)),
                ("addresses", json!(non_empty(address))),
                (
                    "opensshHostPubkey",
                    json!(read_value_or_file(Some(pubkey))?),
                ),
                ("validForSeconds", json!(valid_for_seconds)),
                ("keyId", json!(key_id)),
            ]);
            let data = api
                .post("/external/ssh/sign-host")
                .bearer(token.require()?)
                .header_opt("Idempotency-Key", idempotency_key)
                .json(req)
                .value()?;
            output::success("Host certificate signed");
            render(&data, out.output, None);
        }
        SshExtCmd::SignUser {
            subject,
            pubkey,
            token,
            principal,
            extension,
            force_command,
            source_address,
            valid_for_seconds,
            key_id,
            idempotency_key,
            out,
        } => {
            if principal.is_empty() {
                bail!("At least one --principal (role) is required");
            }
            let req = body([
                ("subject", json!(subject)),
                ("sshPublicKey", json!(read_value_or_file(Some(pubkey))?)),
                ("principals", json!(principal)),
                ("extensions", json!(non_empty(extension))),
                ("forceCommand", json!(force_command)),
                ("sourceAddress", json!(source_address)),
                ("validForSeconds", json!(valid_for_seconds)),
                ("keyId", json!(key_id)),
            ]);
            let data = api
                .post("/external/ssh/sign-user")
                .bearer(token.require()?)
                .header_opt("Idempotency-Key", idempotency_key)
                .json(req)
                .value()?;
            output::success("User certificate signed");
            render(&data, out.output, None);
        }
        SshExtCmd::RegisterHostPubkey { fqdn, token, out } => {
            let data = api
                .post("/external/ssh/register-host-pubkey")
                .bearer(token.require()?)
                .json(json!({ "fqdn": fqdn }))
                .value()?;
            render(&data, out.output, None);
        }
        SshExtCmd::AuthPrincipals { fqdn, token, out } => {
            let data = api
                .get(format!("/external/ssh/hosts/{fqdn}/auth-principals"))
                .bearer(token.require()?)
                .value()?;
            render(&data, out.output, None);
        }
        SshExtCmd::PrincipalsPushed {
            fqdn,
            sha256,
            token,
            out,
        } => {
            let data = api
                .post(format!("/external/ssh/hosts/{fqdn}/principals-pushed"))
                .bearer(token.require()?)
                .json(json!({ "sha256": sha256 }))
                .value()?;
            output::success("Principal files confirmed as installed");
            render(&data, out.output, None);
        }
        SshExtCmd::Krl {
            host_id,
            zone,
            output_file,
        } => {
            let req = body([("host_id", json!(host_id)), ("zone", json!(zone))]);
            let data = api
                .post("/external/ssh/krl")
                .bearer(None)
                .json(req)
                .bytes()?;
            let path = output_file.unwrap_or_else(|| PathBuf::from(format!("krl-{host_id}.enc")));
            write_file(&path, &data)?;
            output::success(&format!("Saved {} bytes to {}", data.len(), path.display()));
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use clap::{CommandFactory, Parser};

    #[derive(Parser)]
    struct T {
        #[command(subcommand)]
        c: ExternalCmd,
    }

    #[test]
    fn command_definition_is_valid() {
        T::command().debug_assert();
    }

    #[test]
    fn defaults_and_aliases() {
        let t = T::try_parse_from(["t", "health", "--token", "x"]).unwrap();
        let ExternalCmd::Health { out, token } = t.c else {
            panic!()
        };
        assert!(out.output.is_json());
        assert_eq!(token.token.as_deref(), Some("x"));
        let t = T::try_parse_from([
            "t",
            "ssh",
            "sign-host",
            "--fqdn",
            "h",
            "-k",
            "k",
            "--ttl",
            "60",
        ])
        .unwrap();
        let ExternalCmd::Ssh(SshExtCmd::SignHost {
            valid_for_seconds, ..
        }) = t.c
        else {
            panic!()
        };
        assert_eq!(valid_for_seconds, Some(60));
        let t = T::try_parse_from(["t", "ssh", "krl", "--host-id", "h", "-o", "f.enc"]).unwrap();
        let ExternalCmd::Ssh(SshExtCmd::Krl { output_file, .. }) = t.c else {
            panic!()
        };
        assert_eq!(output_file.unwrap(), PathBuf::from("f.enc"));
    }

    #[test]
    fn token_required() {
        assert_eq!(
            require(None, "PKI_FLEET_TOKEN").unwrap_err().to_string(),
            "A bearer token is required — pass --token or set PKI_FLEET_TOKEN"
        );
        assert!(require(Some(String::new()), "X").is_err());
        assert_eq!(
            require(Some("t".into()), "X").unwrap().as_deref(),
            Some("t")
        );
    }

    fn decrypt(args: &[&str]) -> std::result::Result<Value, clap::Error> {
        let mut argv = vec![
            "t", "ra", "decrypt", "--data", " QUJD\n", "--token", "pkimg_x",
        ];
        argv.extend_from_slice(args);
        match T::try_parse_from(argv)?.c {
            ExternalCmd::Ra(RaCmd::Decrypt {
                data,
                session_key_length,
                ..
            }) => Ok(decrypt_body(stripped(data).unwrap(), session_key_length)),
            _ => unreachable!(),
        }
    }

    #[test]
    fn decrypt_without_flag_is_the_legacy_request() {
        let body = decrypt(&[]).unwrap();
        assert_eq!(body, json!({ "data": "QUJD" }));
        assert_eq!(serde_json::to_string(&body).unwrap(), r#"{"data":"QUJD"}"#);
    }

    #[test]
    fn decrypt_sends_numeric_session_key_length() {
        for n in ["16", "24", "32"] {
            let body = decrypt(&["--session-key-length", n]).unwrap();
            assert_eq!(
                serde_json::to_string(&body).unwrap(),
                format!(r#"{{"data":"QUJD","sessionKeyLength":{n}}}"#)
            );
            assert!(body["sessionKeyLength"].is_u64());
        }
    }

    #[test]
    fn decrypt_rejects_other_session_key_lengths() {
        for bad in ["0", "8", "15", "17", "64", "256", "-16", "aes256", ""] {
            let arg = format!("--session-key-length={bad}");
            let err = decrypt(&[&arg]).unwrap_err();
            assert_eq!(err.kind(), clap::error::ErrorKind::ValueValidation, "{bad}");
        }
    }
}
