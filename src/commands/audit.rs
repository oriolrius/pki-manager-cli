//! `pki audit`, `pki report` and `pki domain` — the audit/reporting surface.
//!
//! Wraps three REST groups:
//!
//! * `GET  /audit`   — the tamper-evident operation log, with filters
//! * `POST /reports` — CSV report generation (inventory / revocation / CA ops)
//! * `GET  /domains` — the domain inventory aggregated from certificate SANs

use std::path::PathBuf;

use anyhow::{Result, bail};
use chrono::{FixedOffset, NaiveDate, NaiveDateTime, NaiveTime, TimeZone};
use clap::Subcommand;
use serde_json::{Map, Value, json};

use super::bulk::{parse_uuid, py_repr, py_str};
use super::{Format, body, write_file};
use crate::api::Api;
use crate::output::{self, Tone};

const AUDIT_COLUMNS: [&str; 6] = [
    "timestamp",
    "operation",
    "entityType",
    "entityId",
    "status",
    "ipAddress",
];
const DOMAIN_COLUMNS: [&str; 7] = [
    "domain",
    "isWildcard",
    "certificateCount",
    "activeCertificateCount",
    "revokedCertificateCount",
    "caCount",
    "lastCertificateDate",
];

#[derive(Subcommand, Debug)]
pub enum AuditCmd {
    /// List audit log entries.
    List {
        /// Filter by operation, e.g. ca.create
        #[arg(long)]
        operation: Option<String>,
        /// Filter by entity type: ca, certificate, audit, report
        #[arg(long)]
        entity_type: Option<String>,
        /// Filter by a specific entity ID
        #[arg(long)]
        entity_id: Option<String>,
        /// Filter by status: success, failure
        #[arg(short, long, value_parser = ["failure", "success"])]
        status: Option<String>,
        /// Start date (Unix timestamp or ISO-8601)
        #[arg(long)]
        start: Option<String>,
        /// End date (Unix timestamp or ISO-8601)
        #[arg(long)]
        end: Option<String>,
        /// Max results (1-200)
        #[arg(short, long, default_value_t = 100, allow_negative_numbers = true)]
        limit: i64,
        /// Number of entries to skip
        #[arg(long, default_value_t = 0, allow_negative_numbers = true)]
        offset: i64,
        /// Output format: table, json
        #[arg(short, long, value_enum, default_value_t)]
        output: Format,
    },
}

#[derive(Subcommand, Debug)]
pub enum ReportCmd {
    /// Generate a compliance report.
    Generate {
        /// certificate_inventory, revocation, or ca_operations
        #[arg(short = 't', long = "type", value_parser = ["ca_operations", "certificate_inventory", "revocation"])]
        report_type: String,
        /// Report format: csv (pdf is not implemented server-side)
        #[arg(short = 'f', long = "format", default_value = "csv", value_parser = ["csv", "pdf"])]
        format: String,
        /// Restrict the report to one CA
        #[arg(long = "ca")]
        ca_id: Option<String>,
        /// Start date (Unix timestamp or ISO-8601)
        #[arg(long)]
        start: Option<String>,
        /// End date (Unix timestamp or ISO-8601)
        #[arg(long)]
        end: Option<String>,
        /// Write the report body to a file
        #[arg(long)]
        output_file: Option<PathBuf>,
        /// Output format: table, json
        #[arg(short, long, value_enum, default_value_t)]
        output: Format,
    },
}

#[derive(Subcommand, Debug)]
pub enum DomainCmd {
    /// List domains seen across issued certificates.
    List {
        /// Filter domains by name
        #[arg(short = 'q', long)]
        search: Option<String>,
        /// Filter by issuing CA
        #[arg(long = "ca")]
        ca_id: Option<String>,
        /// Max results (1-200)
        #[arg(short, long, default_value_t = 50, allow_negative_numbers = true)]
        limit: i64,
        /// Number of domains to skip
        #[arg(long, default_value_t = 0, allow_negative_numbers = true)]
        offset: i64,
        /// Output format: table, json
        #[arg(short, long, value_enum, default_value_t)]
        output: Format,
    },
}

pub fn run_audit(api: &Api, cmd: AuditCmd) -> Result<()> {
    let AuditCmd::List {
        operation,
        entity_type,
        entity_id,
        status,
        start,
        end,
        limit,
        offset,
        output,
    } = cmd;
    let start = epoch(start.as_deref(), "--start")?;
    let end = epoch(end.as_deref(), "--end")?;
    let data = api
        .get("/audit")
        .query_opt("operation", set(operation))
        .query_opt("entityType", set(entity_type))
        .query_opt("entityId", set(entity_id))
        .query_opt("status", set(status))
        .query_opt("startDate", start)
        .query_opt("endDate", end)
        .query("limit", limit)
        .query("offset", offset)
        .value()?;
    if output.is_json() {
        output::json(&data);
        return Ok(());
    }
    let items = list_items(&data);
    output::records(&items, Some(&AUDIT_COLUMNS), Some("Audit Log"));
    if let Some(total) = data.get("totalCount").filter(|t| !t.is_null()) {
        output::line(
            &format!("{} of {} entries", items.len(), py_str(total)),
            Tone::Dim,
        );
    }
    Ok(())
}

pub fn run_report(api: &Api, cmd: ReportCmd) -> Result<()> {
    let ReportCmd::Generate {
        report_type,
        format,
        ca_id,
        start,
        end,
        output_file,
        output,
    } = cmd;
    let ca_id = set(ca_id).map(|c| parse_uuid(&c)).transpose()?;
    let req = body([
        ("reportType", json!(report_type)),
        ("format", json!(format)),
        ("caId", json!(ca_id)),
        ("startDate", json!(epoch(start.as_deref(), "--start")?)),
        ("endDate", json!(epoch(end.as_deref(), "--end")?)),
    ]);
    let data = api.post("/reports").json(req).value()?;

    // Python: `data.get("reportName", "Report")` — absent gives "Report", null gives no title.
    let title = match data.get("reportName") {
        None => Some("Report".to_string()),
        Some(Value::Null) => None,
        Some(v) => Some(py_str(v)),
    };
    let summary = Value::Object(
        data.as_object()
            .map(|m| {
                m.iter()
                    .filter(|(k, _)| k.as_str() != "content")
                    .map(|(k, v)| (k.clone(), v.clone()))
                    .collect()
            })
            .unwrap_or_else(Map::new),
    );
    let content = data.get("content").and_then(Value::as_str).unwrap_or("");

    if let Some(path) = output_file {
        write_file(&path, content.as_bytes())?;
        output::success(&format!("Report written to {}", path.display()));
        output::kv(&summary, title.as_deref());
        return Ok(());
    }
    if output.is_json() {
        output::json(&data);
        return Ok(());
    }
    output::kv(&summary, title.as_deref());
    if !content.is_empty() {
        println!("{content}");
    }
    Ok(())
}

pub fn run_domain(api: &Api, cmd: DomainCmd) -> Result<()> {
    let DomainCmd::List {
        search,
        ca_id,
        limit,
        offset,
        output,
    } = cmd;
    let ca_id = set(ca_id).map(|c| parse_uuid(&c)).transpose()?;
    let data = api
        .get("/domains")
        .query_opt("search", set(search))
        .query_opt("caId", ca_id)
        .query("limit", limit)
        .query("offset", offset)
        .value()?;
    if output.is_json() {
        output::json(&data);
        return Ok(());
    }
    let items = list_items(&data);
    output::records(&items, Some(&DOMAIN_COLUMNS), Some("Domains"));
    if let Some(total) = data
        .get("pagination")
        .and_then(|p| p.get("total"))
        .filter(|t| !t.is_null())
    {
        output::line(
            &format!("{} of {} domains", items.len(), py_str(total)),
            Tone::Dim,
        );
    }
    Ok(())
}

/// `value or UNSET`: an empty string counts as unset.
fn set(value: Option<String>) -> Option<String> {
    value.filter(|v| !v.is_empty())
}

fn list_items(data: &Value) -> Vec<Value> {
    data.get("items")
        .and_then(Value::as_array)
        .cloned()
        .unwrap_or_default()
}

/// Parse `--start/--end` as a Unix timestamp or an ISO-8601 date (naive = UTC).
///
/// Mirrors the Python `_epoch`: all-digit input is the timestamp itself, other
/// input goes through `datetime.fromisoformat` (after `Z` → `+00:00`).
fn epoch(value: Option<&str>, flag: &str) -> Result<Option<i64>> {
    let Some(value) = value.filter(|v| !v.is_empty()) else {
        return Ok(None);
    };
    if value.bytes().all(|b| b.is_ascii_digit()) {
        if let Ok(n) = value.parse::<i64>() {
            return Ok(Some(n));
        }
    } else if let Some(ts) = from_isoformat(&value.replace('Z', "+00:00")) {
        return Ok(Some(ts));
    }
    bail!(
        "{flag} must be a Unix timestamp or an ISO-8601 date (got {})",
        py_repr(value)
    )
}

/// A subset of Python 3.11 `datetime.fromisoformat`, as epoch seconds (truncated
/// toward zero, like `int(dt.timestamp())`). Naive values are taken as UTC.
///
/// Date: `YYYY-MM-DD` or `YYYYMMDD`. Then optionally any one separator character
/// and a time `HH[:MM[:SS[.f]]]` / `HH[MM[SS[.f]]]`, then an offset `±HH[:MM[:SS]]`.
fn from_isoformat(s: &str) -> Option<i64> {
    if !s.is_ascii() {
        return None;
    }
    let (date, rest) = if s.len() >= 10 && s.as_bytes()[4] == b'-' {
        (
            NaiveDate::parse_from_str(&s[..10], "%Y-%m-%d").ok()?,
            &s[10..],
        )
    } else if s.len() >= 8 && s[..8].bytes().all(|b| b.is_ascii_digit()) {
        (NaiveDate::parse_from_str(&s[..8], "%Y%m%d").ok()?, &s[8..])
    } else {
        return None;
    };
    let (time, offset) = if rest.is_empty() {
        (NaiveTime::MIN, 0)
    } else {
        let t = &rest[1..];
        let (clock, off) = match t.find(['+', '-']) {
            Some(i) => (&t[..i], Some(&t[i..])),
            None => (t, None),
        };
        let time = parse_clock(clock)?;
        let offset = match off {
            Some(o) => parse_offset(o)?,
            None => 0,
        };
        (time, offset)
    };
    let tz = FixedOffset::east_opt(offset)?;
    let dt = tz
        .from_local_datetime(&NaiveDateTime::new(date, time))
        .single()?;
    let secs = dt.timestamp();
    Some(if secs < 0 && dt.timestamp_subsec_nanos() > 0 {
        secs + 1
    } else {
        secs
    })
}

/// `HH`, `HH:MM`, `HH:MM:SS`, `HH:MM:SS.ffffff` (or the same without colons).
fn parse_clock(clock: &str) -> Option<NaiveTime> {
    let (main, frac) = match clock.find(['.', ',']) {
        Some(i) => (&clock[..i], Some(&clock[i + 1..])),
        None => (clock, None),
    };
    let fields = split_fields(main)?;
    if fields.is_empty() || fields.len() > 3 || (frac.is_some() && fields.len() != 3) {
        return None;
    }
    let nanos = match frac {
        Some(f) if !f.is_empty() && f.len() <= 9 && f.bytes().all(|b| b.is_ascii_digit()) => {
            let digits = format!("{f:0<6}");
            digits[..6].parse::<u32>().ok()? * 1000
        }
        Some(_) => return None,
        None => 0,
    };
    let get = |i: usize| fields.get(i).copied().unwrap_or(0);
    NaiveTime::from_hms_nano_opt(get(0), get(1), get(2), nanos)
}

/// `±HH`, `±HH:MM`, `±HHMM`, `±HH:MM:SS` → seconds east of UTC.
fn parse_offset(off: &str) -> Option<i32> {
    let sign = if off.starts_with('-') { -1 } else { 1 };
    let fields = split_fields(&off[1..])?;
    if fields.is_empty() || fields.len() > 3 {
        return None;
    }
    let get = |i: usize| fields.get(i).copied().unwrap_or(0);
    if get(0) > 23 || get(1) > 59 || get(2) > 59 {
        return None;
    }
    Some(sign * (get(0) * 3600 + get(1) * 60 + get(2)) as i32)
}

/// Two-digit fields, either `aa:bb:cc` or `aabbcc` (not mixed).
fn split_fields(s: &str) -> Option<Vec<u32>> {
    let parts: Vec<&str> = if s.contains(':') {
        s.split(':').collect()
    } else {
        if !s.len().is_multiple_of(2) {
            return None;
        }
        (0..s.len()).step_by(2).map(|i| &s[i..i + 2]).collect()
    };
    parts
        .iter()
        .map(|p| {
            (p.len() == 2 && p.bytes().all(|b| b.is_ascii_digit()))
                .then(|| p.parse().ok())
                .flatten()
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    use clap::{CommandFactory, Parser};

    #[derive(Parser)]
    struct TA {
        #[command(subcommand)]
        c: AuditCmd,
    }
    #[derive(Parser)]
    struct TR {
        #[command(subcommand)]
        c: ReportCmd,
    }
    #[derive(Parser)]
    struct TD {
        #[command(subcommand)]
        c: DomainCmd,
    }

    #[test]
    fn command_definitions_are_valid() {
        TA::command().debug_assert();
        TR::command().debug_assert();
        TD::command().debug_assert();
    }

    #[test]
    fn enum_values() {
        assert!(TA::try_parse_from(["t", "list", "-s", "success"]).is_ok());
        assert!(TA::try_parse_from(["t", "list", "-s", "ok"]).is_err());
        assert!(TR::try_parse_from(["t", "generate", "-t", "revocation"]).is_ok());
        assert!(TR::try_parse_from(["t", "generate", "-t", "x"]).is_err());
        assert!(TR::try_parse_from(["t", "generate", "-t", "revocation", "-f", "xml"]).is_err());
    }

    fn ep(v: &str) -> Option<i64> {
        epoch(Some(v), "--start").unwrap()
    }

    #[test]
    fn epoch_parsing() {
        assert_eq!(epoch(None, "--start").unwrap(), None);
        assert_eq!(epoch(Some(""), "--start").unwrap(), None);
        assert_eq!(ep("1767323045"), Some(1767323045));
        assert_eq!(ep("0"), Some(0));
        assert_eq!(ep("2026-01-02"), Some(1767312000));
        // All digits: a Unix timestamp, as in Python (never the basic date form).
        assert_eq!(ep("20260102"), Some(20260102));
        assert_eq!(ep("20260102T00:00"), Some(1767312000));
        assert_eq!(ep("2026-01-02T03:04:05"), Some(1767323045));
        assert_eq!(ep("2026-01-02 03:04:05"), Some(1767323045));
        assert_eq!(ep("2026-01-02T03:04:05Z"), Some(1767323045));
        assert_eq!(ep("2026-01-02T03:04:05.999Z"), Some(1767323045));
        assert_eq!(ep("2026-01-02T03:04"), Some(1767323040));
        assert_eq!(ep("2026-01-02T03"), Some(1767322800));
        assert_eq!(ep("2026-01-02T030405"), Some(1767323045));
        assert_eq!(ep("2026-01-02T05:04:05+02:00"), Some(1767323045));
        assert_eq!(ep("2026-01-02T05:04:05+0200"), Some(1767323045));
        assert_eq!(ep("2026-01-02T01:04:05-02:00"), Some(1767323045));
        assert_eq!(ep("1969-12-31T23:59:59.5"), Some(0));
    }

    #[test]
    fn epoch_errors() {
        for bad in [
            "yesterday",
            "2026-13-01",
            "2026-01-02T25:00",
            "-5",
            "2026-01-02T03:04:05+25:00",
            "12.5",
        ] {
            let err = epoch(Some(bad), "--end").unwrap_err().to_string();
            assert_eq!(
                err,
                format!("--end must be a Unix timestamp or an ISO-8601 date (got '{bad}')")
            );
        }
    }
}
