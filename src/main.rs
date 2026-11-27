//! `pki` — command-line client for the PKI Manager REST API.

mod api;
mod commands;
mod config;
#[cfg(test)]
mod coverage;
mod output;
mod ratelimit;

use std::path::PathBuf;
use std::process::ExitCode;

use clap::{Parser, Subcommand};

use crate::api::Api;
use crate::commands::{Aborted, SilentExit, audit, ca, cert, crl, external, general, ssh};
use crate::config::Settings;

pub const VERSION: &str = env!("CARGO_PKG_VERSION");
/// The PKI Manager release this CLI was built and checked against.
pub const PKI_MANAGER_VERSION: &str = "3.19.0";
/// The REST API generation, as in the `/api/v1` URL prefix.
pub const API_VERSION: &str = "1";

const ABOUT: &str = "PKI Manager CLI - Manage X.509 certificates";
const LONG_ABOUT: &str = "PKI Manager CLI - Manage X.509 certificates.

Configuration can be provided via:
- CLI options (--api-url, --client-id, --client-secret, --token)
- Environment variables (PKI_API_URL, PKI_CLIENT_ID, PKI_CLIENT_SECRET, PKI_TOKEN)
- .env file in current directory or ~/.config/pki-cli/.env

Only PKI_API_URL is mandatory. Supply either a full OIDC client-credentials
configuration or a PKI_TOKEN; omit both to call a server that runs with
OIDC disabled.";

#[derive(Parser, Debug)]
#[command(name = "pki", about = ABOUT, long_about = LONG_ABOUT, disable_version_flag = true, arg_required_else_help = true)]
struct Cli {
    /// Show version
    #[arg(short = 'v', long = "version")]
    version: bool,

    /// PKI Manager API URL
    #[arg(long, env = "PKI_API_URL", hide_env_values = true)]
    api_url: Option<String>,

    /// OIDC token endpoint URL
    #[arg(long, env = "PKI_OIDC_URL", hide_env_values = true)]
    oidc_url: Option<String>,

    /// OIDC client ID
    #[arg(long, env = "PKI_CLIENT_ID", hide_env_values = true)]
    client_id: Option<String>,

    /// OIDC client secret
    #[arg(long, env = "PKI_CLIENT_SECRET", hide_env_values = true)]
    client_secret: Option<String>,

    /// Pre-obtained bearer token (skips the OIDC exchange)
    #[arg(long = "token", env = "PKI_TOKEN", hide_env_values = true)]
    management_token: Option<String>,

    /// On HTTP 429, wait for Retry-After and retry this many times (default 0: fail at once)
    #[arg(long, env = "PKI_RATE_LIMIT_RETRIES")]
    rate_limit_retries: Option<u32>,

    /// Longest Retry-After delay, in seconds, the CLI waits for (default 120)
    #[arg(long, env = "PKI_RATE_LIMIT_MAX_WAIT", hide = true)]
    rate_limit_max_wait: Option<f64>,

    /// PEM file with the CA certificates to trust for HTTPS (default: the bundled Mozilla roots)
    #[arg(long, env = "PKI_CA_BUNDLE")]
    ca_bundle: Option<PathBuf>,

    #[command(subcommand)]
    command: Option<Command>,
}

#[derive(Subcommand, Debug)]
enum Command {
    /// Certificate Authority management
    #[command(subcommand, arg_required_else_help = true)]
    Ca(ca::CaCmd),
    /// Certificate management
    #[command(subcommand, arg_required_else_help = true)]
    Cert(cert::CertCmd),
    /// Certificate Revocation Lists
    #[command(subcommand, arg_required_else_help = true)]
    Crl(crl::CrlCmd),
    /// Domain inventory
    #[command(subcommand, arg_required_else_help = true)]
    Domain(audit::DomainCmd),
    /// Audit log
    #[command(subcommand, arg_required_else_help = true)]
    Audit(audit::AuditCmd),
    /// Compliance reports (CSV)
    #[command(subcommand, arg_required_else_help = true)]
    Report(audit::ReportCmd),
    /// SSH Certificate Manager (CAs, hosts, users, tokens, blocks)
    #[command(subcommand, arg_required_else_help = true)]
    Ssh(ssh::SshCmd),
    /// Machine-facing issuer API (cluster-token X.509 + fleet-token SSH)
    #[command(subcommand, arg_required_else_help = true)]
    External(external::ExternalCmd),
    /// Operator diagnostics (admin role)
    #[command(subcommand, arg_required_else_help = true)]
    Diagnostics(general::DiagnosticsCmd),
    #[command(flatten)]
    General(general::GeneralCmd),
}

fn main() -> ExitCode {
    // `pki ... | head` must end quietly, as other Unix tools do, not panic on EPIPE.
    #[cfg(unix)]
    // SAFETY: called once at start-up, before any thread exists.
    unsafe {
        libc::signal(libc::SIGPIPE, libc::SIG_DFL);
    }
    config::load_dotenv();
    let cli = Cli::parse();

    if cli.version {
        println!("pki-cli version {VERSION}");
        output::line(
            &format!("built for PKI Manager {PKI_MANAGER_VERSION} (REST API v{API_VERSION})"),
            output::Tone::Dim,
        );
        return ExitCode::SUCCESS;
    }
    let Some(command) = cli.command else {
        return ExitCode::SUCCESS;
    };

    let settings = Settings::new(
        cli.api_url,
        cli.oidc_url,
        cli.client_id,
        cli.client_secret,
        cli.management_token,
        cli.rate_limit_retries,
        cli.rate_limit_max_wait,
        cli.ca_bundle,
    );
    let result = Api::new(settings).and_then(|api| match command {
        Command::Ca(c) => ca::run(&api, c),
        Command::Cert(c) => cert::run(&api, c),
        Command::Crl(c) => crl::run(&api, c),
        Command::Domain(c) => audit::run_domain(&api, c),
        Command::Audit(c) => audit::run_audit(&api, c),
        Command::Report(c) => audit::run_report(&api, c),
        Command::Ssh(c) => ssh::run(&api, c),
        Command::External(c) => external::run(&api, c),
        Command::Diagnostics(c) => general::run_diagnostics(&api, c),
        Command::General(c) => general::run(&api, c),
    });

    match result {
        Ok(()) => ExitCode::SUCCESS,
        Err(e) if e.is::<SilentExit>() => ExitCode::FAILURE,
        Err(e) if e.is::<Aborted>() => {
            eprintln!("Aborted!");
            ExitCode::FAILURE
        }
        Err(e) => {
            output::error(&format!("{e:#}"));
            ExitCode::FAILURE
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use clap::CommandFactory;

    #[test]
    fn cli_definition_is_valid() {
        Cli::command().debug_assert();
    }
}
