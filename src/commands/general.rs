//! Top-level commands: dashboard, search, health, diagnostics, config, login, logout.

use anyhow::{Result, bail};
use clap::Subcommand;
use serde_json::Value;

use super::{Format, render};
use crate::api::Api;
use crate::output::{self, ListTable, Panel, Tone};
use crate::{API_VERSION, PKI_MANAGER_VERSION, VERSION};

#[derive(Subcommand, Debug)]
pub enum GeneralCmd {
    /// Show dashboard statistics.
    Stats {
        /// Output format: table, json
        #[arg(short, long, value_enum, default_value_t)]
        output: Format,
    },
    /// Show expiring certificates.
    Expiring {
        /// Max results
        #[arg(short, long, default_value_t = 5)]
        limit: u32,
        /// Output format: table, json
        #[arg(short, long, value_enum, default_value_t)]
        output: Format,
    },
    /// Search CAs and certificates.
    Search {
        /// Search query
        query: String,
        /// Max results
        #[arg(short, long, default_value_t = 50)]
        limit: u32,
        /// Output format: table, json
        #[arg(short, long, value_enum, default_value_t)]
        output: Format,
    },
    /// Check API health status.
    Health {
        /// Output format: table, json
        #[arg(short, long, value_enum, default_value_t)]
        output: Format,
    },
    /// Show current configuration (credentials are masked).
    Config,
    /// Test authentication and cache token.
    Login,
    /// Clear cached authentication token.
    Logout,
}

#[derive(Subcommand, Debug)]
pub enum DiagnosticsCmd {
    /// Show the state of the X.509 key store (OpenBao Transit).
    ///
    /// Tells why X.509 operations answer KEY_STORE_UNAVAILABLE: sealed, not initialised,
    /// token refused, or no answer. Exits 1 when the state is not `ready`. Needs the
    /// admin role when the server has OIDC on. `pki health` does not depend on it.
    KeyStore {
        /// Output format: table, json
        #[arg(short, long, value_enum, default_value_t)]
        output: Format,
    },
}

/// The API returns `totalCAs`/`activeCAs`; other keys exist only on some deployments.
const STAT_LABELS: [(&str, &str, Tone); 7] = [
    ("totalCAs", "Total CAs", Tone::Plain),
    ("activeCAs", "Active CAs", Tone::Plain),
    ("totalCertificates", "Total Certificates", Tone::Plain),
    ("activeCertificates", "Active Certificates", Tone::Plain),
    ("revokedCertificates", "Revoked Certificates", Tone::Plain),
    ("expiredCertificates", "Expired Certificates", Tone::Plain),
    ("expiringSoon", "Expiring Soon", Tone::Yellow),
];

pub fn run(api: &Api, cmd: GeneralCmd) -> Result<()> {
    match cmd {
        GeneralCmd::Stats { output } => {
            let data = api.get("/dashboard/stats").value()?;
            render(&data, output, print_stats);
        }
        GeneralCmd::Expiring { limit, output } => {
            let data = api
                .get("/dashboard/expiring")
                .query("limit", limit)
                .value()?;
            let items = match &data {
                Value::Array(a) => a.clone(),
                _ => Vec::new(),
            };
            if output.is_json() {
                output::json(&Value::Array(items));
            } else if items.is_empty() {
                output::line("No certificates expiring soon", Tone::Green);
            } else {
                print_expiring(&items);
            }
        }
        GeneralCmd::Search {
            query,
            limit,
            output,
        } => {
            let data = api
                .get("/search")
                .query("query", query)
                .query("limit", limit)
                .value()?;
            render(&data, output, print_search_results);
        }
        GeneralCmd::Health { output } => {
            let data = api
                .get("/health")
                .value()
                .map_err(|e| anyhow::anyhow!("API health check failed: {e:#}"))?;
            render(&data, output, |d| output::kv(d, Some("API Health")));
            match data.get("status").and_then(Value::as_str) {
                Some("ok") => output::success("API is healthy"),
                other => bail!("API reports status '{}'", other.unwrap_or("None")),
            }
        }
        GeneralCmd::Config => show_config(api),
        GeneralCmd::Login => {
            let s = api.settings();
            if !s.has_oidc() {
                let mode = if s.token.is_some() {
                    "a static PKI_TOKEN"
                } else {
                    "anonymous access"
                };
                bail!("Nothing to log in with — the CLI is configured for {mode}.");
            }
            s.validate()?;
            api.clear_token_cache();
            api.fetch_token()
                .map_err(|e| anyhow::anyhow!("Authentication failed: {e:#}"))?;
            output::success("Authentication successful! Token cached.");
        }
        GeneralCmd::Logout => {
            api.clear_token_cache();
            output::success("Token cache cleared.");
        }
    }
    Ok(())
}

pub fn run_diagnostics(api: &Api, cmd: DiagnosticsCmd) -> Result<()> {
    match cmd {
        DiagnosticsCmd::KeyStore { output } => {
            let data = api.get("/diagnostics/key-store").value()?;
            render(&data, output, |d| output::kv(d, Some("Key Store")));
            key_store_verdict(&data)?;
            output::success("Key store is ready");
        }
    }
    Ok(())
}

/// `Ok` when the key store is `ready`; otherwise the error says what an operator checks.
fn key_store_verdict(data: &Value) -> Result<()> {
    let state = data.get("state").and_then(Value::as_str).unwrap_or("None");
    if data.get("configured").and_then(Value::as_bool) == Some(false) {
        bail!(
            "Key store is not configured (state '{state}'): the OpenBao settings of the server are missing or invalid"
        );
    }
    let reason = match state {
        "ready" => return Ok(()),
        "sealed" => "OpenBao is sealed; an operator unseals it",
        "uninitialized" => "OpenBao is not initialised",
        "unauthorized" => "the backend token file is missing or OpenBao refuses the token",
        "unavailable" => "OpenBao does not answer",
        other => bail!("Key store reports state '{other}'"),
    };
    bail!("Key store is not ready (state '{state}'): {reason}")
}

fn mask(value: &Option<String>, keep: usize) -> String {
    match value {
        Some(v) => format!("{}****", v.chars().take(keep).collect::<String>()),
        None => "Not set".into(),
    }
}

fn show_config(api: &Api) {
    let s = api.settings();
    let auth_mode = if s.token.is_some() {
        "static bearer token (PKI_TOKEN)"
    } else if s.has_oidc() {
        "OIDC client credentials"
    } else {
        "anonymous (only works when the server has OIDC disabled)"
    };
    let mut p = Panel::new(Some("PKI CLI Configuration"));
    p.row(
        "API URL",
        s.api_url.clone().unwrap_or_else(|| "Not set".into()),
    );
    p.row("Auth Mode", auth_mode);
    p.row(
        "OIDC URL",
        s.oidc_url.clone().unwrap_or_else(|| "Not set".into()),
    );
    p.row(
        "Client ID",
        s.client_id.clone().unwrap_or_else(|| "Not set".into()),
    );
    p.row("Client Secret", mask(&s.client_secret, 4));
    p.row("Bearer Token", mask(&s.token, 6));
    p.row(
        "CA Bundle",
        s.ca_bundle
            .as_ref()
            .map(|b| b.display().to_string())
            .unwrap_or_else(|| "bundled Mozilla roots".into()),
    );
    p.row("Token Cache", s.token_cache_file.display().to_string());
    p.row(
        "CLI Version",
        format!("{VERSION} (for PKI Manager {PKI_MANAGER_VERSION}, API v{API_VERSION})"),
    );
    p.print();

    if s.api_url.is_none() {
        println!();
        output::line(
            "PKI_API_URL is required. Set it via environment, .env, or --api-url.",
            Tone::Red,
        );
        return;
    }
    let given = [
        s.oidc_url.is_some(),
        s.client_id.is_some(),
        s.client_secret.is_some(),
    ];
    if given.iter().any(|g| *g) && !given.iter().all(|g| *g) {
        println!();
        output::line(
            "Warning: incomplete OIDC configuration. Set PKI_OIDC_URL, PKI_CLIENT_ID and PKI_CLIENT_SECRET together.",
            Tone::Yellow,
        );
    }
}

fn print_stats(stats: &Value) {
    let mut t = ListTable::new(
        Some("PKI Dashboard Statistics"),
        &[("Metric", Tone::Cyan), ("Value", Tone::Bold)],
    );
    t.right_align(1);
    for (key, label, tone) in STAT_LABELS {
        if let Some(v) = stats.get(key) {
            t.row(vec![
                output::cell(label, Tone::Cyan),
                output::cell(
                    output::scalar(v),
                    if tone == Tone::Plain {
                        Tone::Bold
                    } else {
                        tone
                    },
                ),
            ]);
        }
    }
    // Show what the server added that this CLI does not know about yet.
    if let Value::Object(map) = stats {
        for (k, v) in map {
            if !STAT_LABELS.iter().any(|(key, _, _)| key == k) {
                t.row(vec![
                    output::cell(k.as_str(), Tone::Cyan),
                    output::cell(output::scalar(v), Tone::Bold),
                ]);
            }
        }
    }
    t.print();
}

fn print_expiring(items: &[Value]) {
    let mut t = ListTable::new(
        Some("Expiring Certificates"),
        &[
            ("ID", Tone::Dim),
            ("Type", Tone::Magenta),
            ("Common Name", Tone::Cyan),
            ("Expires", Tone::Yellow),
            ("Days Left", Tone::Plain),
        ],
    );
    t.right_align(4);
    for i in items {
        t.row(vec![
            output::cell(output::text(i, "id"), Tone::Dim),
            output::cell(output::text(i, "type"), Tone::Magenta),
            output::cell(output::text(i, "cn"), Tone::Cyan),
            output::cell(output::format_date(i.get("notAfter")), Tone::Yellow),
            output::days_cell(i.get("daysRemaining").unwrap_or(&Value::from(0))),
        ]);
    }
    t.print();
}

fn print_search_results(data: &Value) {
    let results = data.get("results").cloned().unwrap_or(Value::Null);
    let list = |k: &str| {
        results
            .get(k)
            .and_then(Value::as_array)
            .cloned()
            .unwrap_or_default()
    };
    let (cas, certs, domains) = (list("cas"), list("certificates"), list("domains"));
    if cas.is_empty() && certs.is_empty() && domains.is_empty() {
        output::line("No results found", Tone::Dim);
        return;
    }
    for (title, rows) in [("Certificate Authorities", &cas), ("Certificates", &certs)] {
        if rows.is_empty() {
            continue;
        }
        let mut t = ListTable::new(
            Some(title),
            &[
                ("ID", Tone::Dim),
                ("Title", Tone::Cyan),
                ("Subtitle", Tone::Dim),
                ("Status", Tone::Plain),
            ],
        );
        for i in rows {
            t.row(vec![
                output::cell(output::text(i, "id"), Tone::Dim),
                output::cell(output::text(i, "title"), Tone::Cyan),
                output::cell(output::text(i, "subtitle"), Tone::Dim),
                output::status_cell(&output::text(i, "status")),
            ]);
        }
        t.print();
    }
    if !domains.is_empty() {
        let mut t = ListTable::new(
            Some("Domains"),
            &[("Domain", Tone::Cyan), ("Certificate ID", Tone::Dim)],
        );
        for i in &domains {
            t.row(vec![
                output::cell(output::text(i, "domain"), Tone::Cyan),
                output::cell(output::text(i, "certificateId"), Tone::Dim),
            ]);
        }
        t.print();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn key_store_states() {
        use serde_json::json;
        let check = |state: &str, configured: bool| {
            key_store_verdict(
                &json!({"provider": "openbao", "configured": configured, "state": state}),
            )
            .map_err(|e| e.to_string())
        };
        assert!(check("ready", true).is_ok());
        assert_eq!(
            check("sealed", true).unwrap_err(),
            "Key store is not ready (state 'sealed'): OpenBao is sealed; an operator unseals it"
        );
        for state in ["uninitialized", "unauthorized", "unavailable"] {
            let e = check(state, true).unwrap_err();
            assert!(
                e.starts_with(&format!("Key store is not ready (state '{state}'): ")),
                "{e}"
            );
        }
        assert!(
            check("unavailable", false)
                .unwrap_err()
                .starts_with("Key store is not configured (state 'unavailable')")
        );
        assert_eq!(
            check("melted", true).unwrap_err(),
            "Key store reports state 'melted'"
        );
        assert!(
            key_store_verdict(&json!({})).is_err(),
            "no state is not ready"
        );
    }

    #[test]
    fn masking() {
        assert_eq!(mask(&Some("supersecret".into()), 4), "supe****");
        assert_eq!(mask(&None, 4), "Not set");
    }
}
