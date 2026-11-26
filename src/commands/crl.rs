//! `pki crl` — Certificate Revocation List management and distribution.
//!
//! Covers the two authenticated CA-scoped CRL routes (`GET`/`POST
//! /cas/{id}/crls`) plus the unauthenticated CDP download served at the server
//! root (`/crl/{caId}.crl` and `.der`), which relying parties fetch directly.

use std::path::PathBuf;

use anyhow::{Result, bail};
use clap::Subcommand;
use serde_json::{Value, json};

use super::bulk::{parse_uuid, py_str};
use super::{Format, write_file};
use crate::api::Api;
use crate::output::{self, Tone};

const CRL_COLUMNS: [&str; 6] = [
    "id",
    "crlNumber",
    "thisUpdate",
    "nextUpdate",
    "validityStatus",
    "revokedCount",
];

#[derive(Subcommand, Debug)]
pub enum CrlCmd {
    /// List the CRLs a CA has published.
    List {
        /// CA ID (UUID)
        ca_id: String,
        /// Max results (1-100)
        #[arg(short, long, default_value_t = 50, allow_negative_numbers = true)]
        limit: i64,
        /// Number of CRLs to skip
        #[arg(long, default_value_t = 0, allow_negative_numbers = true)]
        offset: i64,
        /// Output format: table, json
        #[arg(short, long, value_enum, default_value_t)]
        output: Format,
    },
    /// Generate a new CRL for a CA.
    Generate {
        /// CA ID (UUID)
        ca_id: String,
        /// Days until the new CRL expires (1-365)
        #[arg(short = 'n', long, default_value_t = 7, allow_negative_numbers = true)]
        next_update_days: i64,
        /// Output format: table, json
        #[arg(short, long, value_enum, default_value_t)]
        output: Format,
    },
    /// Download a CA's current CRL from its public distribution point.
    Download {
        /// CA ID (UUID)
        ca_id: String,
        /// crl (PEM) or der (binary)
        #[arg(short = 'f', long = "format", default_value = "crl")]
        format: String,
        /// Destination file
        #[arg(short = 'o', long)]
        output_file: Option<PathBuf>,
    },
}

pub fn run(api: &Api, cmd: CrlCmd) -> Result<()> {
    match cmd {
        CrlCmd::List {
            ca_id,
            limit,
            offset,
            output,
        } => {
            let id = parse_uuid(&ca_id)?;
            let data = api
                .get(format!("/cas/{id}/crls"))
                .query("limit", limit)
                .query("offset", offset)
                .value()?;
            if output.is_json() {
                output::json(&data);
                return Ok(());
            }
            let items = data
                .get("items")
                .and_then(Value::as_array)
                .cloned()
                .unwrap_or_default();
            output::records(
                &items,
                Some(&CRL_COLUMNS),
                Some(&format!("CRLs for CA {ca_id}")),
            );
            if let Some(total) = data
                .get("pagination")
                .and_then(|p| p.get("total"))
                .filter(|t| !t.is_null())
            {
                output::line(
                    &format!("{} of {} CRLs", items.len(), py_str(total)),
                    Tone::Dim,
                );
            }
            Ok(())
        }
        CrlCmd::Generate {
            ca_id,
            next_update_days,
            output,
        } => {
            let id = parse_uuid(&ca_id)?;
            let data = api
                .post(format!("/cas/{id}/crls"))
                .json(json!({ "nextUpdateDays": next_update_days }))
                .value()?;
            let number = data
                .get("crlNumber")
                .map(py_str)
                .unwrap_or_else(|| "?".into());
            output::success(&format!("CRL #{number} generated"));
            if output.is_json() {
                output::json(&data)
            } else {
                output::kv(&data, Some("CRL"))
            }
            Ok(())
        }
        CrlCmd::Download {
            ca_id,
            format,
            output_file,
        } => {
            if !matches!(format.as_str(), "crl" | "der" | "pem") {
                bail!("--format must be 'crl' (PEM) or 'der'");
            }
            let suffix = if format == "pem" {
                "crl"
            } else {
                format.as_str()
            };
            let data = api.get(format!("/crl/{ca_id}.{suffix}")).public().bytes()?;
            let path = output_file.unwrap_or_else(|| PathBuf::from(format!("{ca_id}.{suffix}")));
            write_file(&path, &data)?;
            output::success(&format!("Saved {} bytes to {}", data.len(), path.display()));
            Ok(())
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use clap::{CommandFactory, Parser};

    #[derive(Parser)]
    struct T {
        #[command(subcommand)]
        c: CrlCmd,
    }

    #[test]
    fn command_definition_is_valid() {
        T::command().debug_assert();
    }

    #[test]
    fn download_flags() {
        let t = T::try_parse_from(["t", "download", "x", "-f", "der", "-o", "out.der"]).unwrap();
        match t.c {
            CrlCmd::Download {
                format,
                output_file,
                ..
            } => {
                assert_eq!(format, "der");
                assert_eq!(output_file.unwrap(), PathBuf::from("out.der"));
            }
            _ => panic!(),
        }
    }
}
