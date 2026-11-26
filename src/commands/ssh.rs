//! `pki ssh` — SSH Certificate Manager commands (port of `src/pki_cli/ssh.py`).
//!
//! Wraps the authenticated `/api/v1/ssh/*` surface (CAs, hosts, user identities,
//! principals, fleet tokens, per-host blocks, revocation) plus the
//! unauthenticated public trust-material and KRL download routes served at the
//! server root.

use std::io::Write;
use std::path::{Path, PathBuf};

use anyhow::{Context, Result, bail};
use clap::Subcommand;
use serde_json::{Value, json};

use super::{Format, body, confirm, non_empty, read_value_or_file, write_file};
use crate::api::Api;
use crate::output;

const CA_COLUMNS: &[&str] = &[
    "id",
    "caType",
    "label",
    "keyAlgorithm",
    "status",
    "nextSerial",
    "createdAt",
];
const HOST_COLUMNS: &[&str] = &[
    "id",
    "fqdn",
    "displayName",
    "status",
    "hasPubkey",
    "hostKeyAlgorithm",
    "lastKrlVersion",
    "enrolledAt",
];
const FLEET_COLUMNS: &[&str] = &[
    "fqdn",
    "status",
    "blockCount",
    "krlNumber",
    "lastKrlVersion",
    "lastKrlFetchAt",
];
const IDENTITY_COLUMNS: &[&str] = &["id", "subject", "email", "status", "createdAt"];
const ZONE_COLUMNS: &[&str] = &[
    "id",
    "name",
    "displayName",
    "status",
    "description",
    "createdAt",
];
const USER_CERT_COLUMNS: &[&str] = &[
    "id",
    "serial",
    "keyId",
    "principals",
    "status",
    "validAfter",
    "validBefore",
];

// ---------------------------------------------------------------------------
// Command definitions
// ---------------------------------------------------------------------------

#[derive(Subcommand, Debug)]
pub enum SshCmd {
    /// SSH CA management
    #[command(subcommand, arg_required_else_help = true)]
    Ca(CaCmd),
    /// SSH host registration & certificates
    #[command(subcommand, arg_required_else_help = true)]
    Host(HostCmd),
    /// SSH user certificate issuance
    #[command(subcommand, arg_required_else_help = true)]
    User(UserCmd),
    /// SSH user identities
    #[command(subcommand, arg_required_else_help = true)]
    Identity(IdentityCmd),
    /// SSH principals (roles) & mappings
    #[command(subcommand, arg_required_else_help = true)]
    Principal(PrincipalCmd),
    /// Fleet automation tokens
    #[command(subcommand, arg_required_else_help = true)]
    Token(TokenCmd),
    /// Per-host access blocks
    #[command(subcommand, arg_required_else_help = true)]
    Block(BlockCmd),
    /// SSH certificate revocation & purge
    #[command(subcommand, arg_required_else_help = true)]
    Cert(CertCmd),
    /// Bulk SSH certificate lifecycle
    #[command(subcommand, arg_required_else_help = true)]
    Bulk(BulkCmd),
    /// SSH zones (multi-tenant scoping)
    #[command(subcommand, arg_required_else_help = true)]
    Zone(ZoneCmd),

    /// Show SSH trust anchors (TrustedUserCAKeys / @cert-authority).
    ///
    /// Unlike the list commands this resolves a single zone server-side, so
    /// ``--zone`` becomes required as soon as a second zone is active.
    TrustAnchors {
        /// Zone ID or name (required once more than one zone is active)
        #[arg(long)]
        zone: Option<String>,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Json)]
        output: Format,
    },
    /// Show SSH cert/KRL health metrics (expiring, stale KRLs, non-pulling hosts).
    Metrics {
        /// Restrict to one zone (ID or name)
        #[arg(long)]
        zone: Option<String>,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Json)]
        output: Format,
    },
    /// Print the TrustedUserCAKeys file contents (public endpoint).
    TrustedUserCaKeys {
        /// Write output to a file instead of stdout
        #[arg(short = 'o', long = "output", value_name = "PATH")]
        output_file: Option<PathBuf>,
    },
    /// Print the Host CA public key(s) — the KRL puller trust anchor (public endpoint).
    HostCaKeys {
        /// Write output to a file instead of stdout
        #[arg(short = 'o', long = "output", value_name = "PATH")]
        output_file: Option<PathBuf>,
    },
    /// Print @cert-authority known_hosts lines for the Host CA(s) (public endpoint).
    CertAuthority {
        /// known_hosts host pattern
        #[arg(short = 'p', long, default_value = "*")]
        pattern: String,
        /// Write output to a file instead of stdout
        #[arg(short = 'o', long = "output", value_name = "PATH")]
        output_file: Option<PathBuf>,
    },
    /// Download a CA's public KRL (unauthenticated root endpoint).
    Krl {
        /// SSH CA ID
        ca_id: String,
        /// bin (raw KRL bytes) or json (signed envelope)
        #[arg(
            short = 'f',
            long = "format",
            value_name = "FORMAT",
            default_value = "bin"
        )]
        fmt: String,
        /// Write output to a file instead of stdout
        #[arg(short = 'o', long = "output", value_name = "PATH")]
        output_file: Option<PathBuf>,
    },
    /// Download a host's composed public KRL (gated by SSH_HOST_KRL_PUBLIC on the server).
    KrlHost {
        /// Host ID or FQDN
        host_id: String,
        /// bin or json
        #[arg(
            short = 'f',
            long = "format",
            value_name = "FORMAT",
            default_value = "bin"
        )]
        fmt: String,
        /// Write output to a file instead of stdout
        #[arg(short = 'o', long = "output", value_name = "PATH")]
        output_file: Option<PathBuf>,
    },
}

#[derive(Subcommand, Debug)]
pub enum CaCmd {
    /// List SSH CAs (user + host).
    List {
        /// Restrict to one zone (ID or name)
        #[arg(long)]
        zone: Option<String>,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Create an SSH CA (user or host).
    Create {
        /// CA type: user or host
        #[arg(short = 't', long = "type")]
        ca_type: String,
        /// Human-readable label
        #[arg(short = 'l', long)]
        label: Option<String>,
        /// Zone ID or name (required once more than one zone is active)
        #[arg(long)]
        zone: Option<String>,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Print a CA's OpenSSH public key (public endpoint).
    Pub {
        /// SSH CA ID
        ca_id: String,
        /// Write output to a file instead of stdout
        #[arg(short = 'o', long = "output", value_name = "PATH")]
        output_file: Option<PathBuf>,
    },
    /// Generate / rebuild the KRL for a CA.
    KrlGenerate {
        /// SSH CA ID
        ca_id: String,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// List revocations recorded for a CA.
    Revocations {
        /// SSH CA ID
        ca_id: String,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Download the CA's bare KRL bytes (authenticated).
    Krl {
        /// SSH CA ID
        ca_id: String,
        /// Write output to a file instead of stdout
        #[arg(short = 'o', long = "output", value_name = "PATH")]
        output_file: Option<PathBuf>,
    },
    /// Show one SSH CA.
    Get {
        /// SSH CA ID
        ca_id: String,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Import an existing KMS keypair as an SSH CA.
    Import {
        /// CA type: user or host
        #[arg(short = 't', long = "type")]
        ca_type: String,
        /// KMS private key ID
        #[arg(long)]
        kms_key_id: String,
        /// KMS public key ID
        #[arg(long)]
        kms_public_key_id: String,
        /// Human-readable label
        #[arg(short = 'l', long)]
        label: Option<String>,
        /// Zone ID or name (required once more than one zone is active)
        #[arg(long)]
        zone: Option<String>,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Revoke an SSH CA (its certificates stop being trusted).
    Revoke {
        /// SSH CA ID
        ca_id: String,
        /// Reason
        #[arg(short = 'r', long)]
        reason: Option<String>,
        /// Skip confirmation
        #[arg(short = 'f', long)]
        force: bool,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Rotate an SSH CA — new keypair, predecessor linked and kept for trust.
    Rotate {
        /// SSH CA ID
        ca_id: String,
        /// Skip confirmation
        #[arg(short = 'f', long)]
        force: bool,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Retire an SSH CA — stops issuance, keeps existing certificates trusted.
    Retire {
        /// SSH CA ID
        ca_id: String,
        /// Skip confirmation
        #[arg(short = 'f', long)]
        force: bool,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Show which certificates still depend on a CA (the gate before `retire`).
    ReissueReport {
        /// SSH CA ID
        ca_id: String,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Json)]
        output: Format,
    },
    /// Revoke a serial under a CA without holding its certificate row (rebuilds the KRL).
    RevokeSerial {
        /// SSH CA ID
        ca_id: String,
        /// Certificate serial (integer string)
        #[arg(short = 's', long)]
        serial: String,
        /// Reason
        #[arg(short = 'r', long)]
        reason: Option<String>,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Revoke a public key by fingerprint — the only way to deny a key this PKI never issued.
    RevokeKey {
        /// SSH CA ID
        ca_id: String,
        /// Public key fingerprint (SHA256:...)
        #[arg(long)]
        fingerprint: String,
        /// Reason
        #[arg(short = 'r', long)]
        reason: Option<String>,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
}

#[derive(Subcommand, Debug)]
pub enum HostCmd {
    /// List registered SSH hosts.
    List {
        /// Filter by FQDN
        #[arg(long)]
        fqdn: Option<String>,
        /// Restrict to one zone (ID or name)
        #[arg(long)]
        zone: Option<String>,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Register a host by its OpenSSH host public key.
    Register {
        /// Host FQDN
        #[arg(long)]
        fqdn: String,
        /// OpenSSH host public key (or @file)
        #[arg(short = 'k', long)]
        pubkey: String,
        /// Display name
        #[arg(long)]
        display_name: Option<String>,
        /// Host address (repeatable)
        #[arg(short = 'a', long)]
        address: Vec<String>,
        /// Zone ID or name (required once more than one zone is active)
        #[arg(long)]
        zone: Option<String>,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Issue a host certificate.
    Issue {
        /// Host ID
        #[arg(long)]
        host_id: String,
        /// Host CA ID (defaults to active host CA)
        #[arg(long)]
        ca_id: Option<String>,
        /// Validity in seconds
        #[arg(long = "valid-for-seconds", visible_alias = "ttl")]
        valid_for_seconds: Option<i64>,
        /// Certificate key_id (logged by sshd)
        #[arg(long)]
        key_id: Option<String>,
        /// Explicit serial (integer string)
        #[arg(long)]
        serial: Option<String>,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Show who can reach a host (entitlements + blocks + distribution state).
    Access {
        /// Host ID
        host_id: String,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Json)]
        output: Format,
    },
    /// Show a host's block history (active + lifted).
    Blocks {
        /// Host ID
        host_id: String,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Render a host's AuthorizedPrincipalsFile contents (authenticated).
    AuthPrincipals {
        /// Host ID
        host_id: String,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Json)]
        output: Format,
    },
    /// Mark a host's rendered principal files as pushed (clears its Stale flag).
    ///
    /// Call this after your config-management run has actually copied the files
    /// from ``pki ssh host auth-principals`` onto the host.
    MarkPushed {
        /// Host ID
        host_id: String,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Json)]
        output: Format,
    },
    /// List a host's principal -> local account mappings.
    PrincipalMaps {
        /// Host ID
        host_id: String,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Print a host's current certificate (public endpoint).
    Cert {
        /// Host ID
        host_id: String,
        /// Write output to a file instead of stdout
        #[arg(short = 'o', long = "output", value_name = "PATH")]
        output_file: Option<PathBuf>,
    },
    /// Print the ready-to-paste sshd_config drop-in for a host (public endpoint).
    SshdConfig {
        /// Host ID
        host_id: String,
        /// Write output to a file instead of stdout
        #[arg(short = 'o', long = "output", value_name = "PATH")]
        output_file: Option<PathBuf>,
    },
    /// Show one registered host.
    Get {
        /// Host ID
        host_id: String,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Build a host's deploy bundle (sshd drop-in, CA keys, on-host paths).
    DeployBundle {
        /// Host ID
        host_id: String,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Json)]
        output: Format,
    },
    /// Revoke a host's current certificate (rebuilds the CA KRL).
    Revoke {
        /// Host ID
        host_id: String,
        /// Reason
        #[arg(short = 'r', long)]
        reason: Option<String>,
        /// Skip confirmation
        #[arg(short = 'f', long)]
        force: bool,
    },
    /// Register the host's ECDSA public key as its ECIES/KRL recipient.
    EciesKey {
        /// Host ID
        host_id: String,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Offboard a host — terminal: retires its per-host KRL lineage.
    Offboard {
        /// Host ID
        host_id: String,
        /// Reason
        #[arg(short = 'r', long)]
        reason: Option<String>,
        /// Skip confirmation
        #[arg(short = 'f', long)]
        force: bool,
    },
}

#[derive(Subcommand, Debug)]
pub enum IdentityCmd {
    /// Create a user identity.
    Create {
        /// Identity subject
        #[arg(short = 's', long)]
        subject: String,
        /// Email
        #[arg(long)]
        email: Option<String>,
        /// External IdP subject
        #[arg(long)]
        external_subject: Option<String>,
        /// Zone ID or name (required once more than one zone is active)
        #[arg(long)]
        zone: Option<String>,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Show an identity's active blocks with per-host distribution state.
    Blocks {
        /// Identity ID
        identity_id: String,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// List identities sharing a certified public key with this one.
    Collisions {
        /// Identity ID
        identity_id: String,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// List the principals an identity is granted.
    Grants {
        /// Identity ID
        identity_id: String,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// List user identities.
    List {
        /// Restrict to one zone (ID or name)
        #[arg(long)]
        zone: Option<String>,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Disable an identity (blocks further issuance; existing certs stay valid).
    Disable {
        /// Identity ID
        identity_id: String,
        /// Skip confirmation
        #[arg(short = 'f', long)]
        force: bool,
    },
    /// Offboard an identity — disable it and revoke its live certificates.
    Offboard {
        /// Identity ID
        identity_id: String,
        /// Reason
        #[arg(short = 'r', long)]
        reason: Option<String>,
        /// Skip confirmation
        #[arg(short = 'f', long)]
        force: bool,
    },
}

#[derive(Subcommand, Debug)]
pub enum UserCmd {
    /// Issue a user certificate.
    Issue {
        /// Identity ID
        #[arg(long)]
        identity_id: String,
        /// User's SSH public key (or @file)
        #[arg(short = 'k', long)]
        pubkey: String,
        /// Principal/role (repeatable, at least one)
        #[arg(short = 'p', long)]
        principal: Vec<String>,
        /// User CA ID (defaults to active user CA)
        #[arg(long)]
        ca_id: Option<String>,
        /// SSH extension, e.g. permit-pty (repeatable)
        #[arg(short = 'e', long)]
        extension: Vec<String>,
        /// force-command restriction
        #[arg(long)]
        force_command: Option<String>,
        /// source-address CIDR list
        #[arg(long)]
        source_address: Option<String>,
        /// Validity in seconds
        #[arg(long = "valid-for-seconds", visible_alias = "ttl")]
        valid_for_seconds: Option<i64>,
        /// Certificate key_id (logged by sshd)
        #[arg(long)]
        key_id: Option<String>,
        /// Enforce principal entitlements
        #[arg(long, overrides_with = "no_enforce_entitlement")]
        enforce_entitlement: bool,
        /// Do not enforce principal entitlements
        #[arg(long, overrides_with = "enforce_entitlement")]
        no_enforce_entitlement: bool,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// List user certificates (optionally for one identity).
    Certificates {
        /// Filter by identity ID
        #[arg(long)]
        identity_id: Option<String>,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
}

#[derive(Subcommand, Debug)]
pub enum PrincipalCmd {
    /// List SSH principals (roles).
    List {
        /// Restrict to one zone (ID or name)
        #[arg(long)]
        zone: Option<String>,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Create an SSH principal (role).
    Create {
        /// Principal name
        #[arg(short = 'n', long)]
        name: String,
        /// Description
        #[arg(short = 'd', long)]
        description: Option<String>,
        /// Zone ID or name (required once more than one zone is active)
        #[arg(long)]
        zone: Option<String>,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Map a principal to a local account on a host.
    Map {
        /// Host ID
        #[arg(long)]
        host_id: String,
        /// Principal ID
        #[arg(long)]
        principal_id: String,
        /// Local account name on the host
        #[arg(long)]
        local_account: String,
    },
    /// Grant an identity the entitlement to encode a principal.
    Grant {
        /// Identity ID
        #[arg(long)]
        identity_id: String,
        /// Principal ID
        #[arg(long)]
        principal_id: String,
    },
    /// Remove a principal -> local account mapping from a host (the host becomes Stale until pushed).
    Unmap {
        /// Host ID
        #[arg(long)]
        host_id: String,
        /// Principal ID
        #[arg(long)]
        principal_id: String,
        /// Local account name on the host
        #[arg(long)]
        local_account: String,
    },
    /// Remove a principal from an identity's grants (existing certificates stay valid).
    RevokeGrant {
        /// Identity ID
        #[arg(long)]
        identity_id: String,
        /// Principal ID
        #[arg(long)]
        principal_id: String,
    },
    /// Show principal -> (host, local account) mappings across the fleet.
    Mappings {
        /// Restrict to one zone (ID or name)
        #[arg(long)]
        zone: Option<String>,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Json)]
        output: Format,
    },
    /// List hosts whose principal maps changed after the last push.
    StaleHosts {
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Delete a principal (rejected while entitlements or host maps reference it).
    Delete {
        /// Principal ID
        principal_id: String,
        /// Skip confirmation
        #[arg(short = 'f', long)]
        force: bool,
    },
}

#[derive(Subcommand, Debug)]
pub enum TokenCmd {
    /// List fleet tokens (metadata only, no secrets).
    List {
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Mint a fleet token (plaintext secret shown once).
    Mint {
        /// Token name
        #[arg(short = 'n', long)]
        name: String,
        /// Allowed op (repeatable): sign-host, sign-user, register-host-pubkey, get-principals
        #[arg(long)]
        op: Vec<String>,
        /// User CA the token may sign for
        #[arg(long)]
        user_ca_id: Option<String>,
        /// Host CA the token may sign for
        #[arg(long)]
        host_ca_id: Option<String>,
        /// Zone ID or name (required once more than one zone is active)
        #[arg(long)]
        zone: Option<String>,
        /// Principal the token may put in a user certificate (repeatable; omit for no restriction)
        #[arg(long)]
        allowed_principal: Vec<String>,
        /// Longest certificate validity, in seconds, the token may ask for
        #[arg(long = "max-valid-for-seconds", visible_alias = "max-ttl",
              value_parser = clap::value_parser!(i64).range(1..))]
        max_valid_for_seconds: Option<i64>,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Json)]
        output: Format,
    },
    /// Revoke a fleet token.
    Revoke {
        /// Fleet token ID
        token_id: String,
        /// Skip confirmation
        #[arg(short = 'f', long)]
        force: bool,
    },
}

#[derive(Subcommand, Debug)]
pub enum BulkCmd {
    /// List SSH certificates expiring within a window (default 7 days).
    Expiring {
        /// Window in seconds
        #[arg(short = 'w', long, default_value_t = 604800)]
        within_seconds: i64,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Renew many SSH certificates by ID.
    Renew {
        /// Certificate ID (repeatable)
        #[arg(short = 'i', long)]
        cert_id: Vec<String>,
        /// File with one certificate ID per line
        #[arg(long)]
        ids_file: Option<PathBuf>,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Json)]
        output: Format,
    },
    /// Revoke many SSH certificates by ID (rebuilds the affected KRLs).
    Revoke {
        /// Certificate ID (repeatable)
        #[arg(short = 'i', long)]
        cert_id: Vec<String>,
        /// File with one certificate ID per line
        #[arg(long)]
        ids_file: Option<PathBuf>,
        /// Reason
        #[arg(short = 'r', long)]
        reason: Option<String>,
        /// Skip confirmation
        #[arg(short = 'f', long)]
        force: bool,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Json)]
        output: Format,
    },
}

#[derive(Subcommand, Debug)]
pub enum BlockCmd {
    /// Block an identity on a host (per-host KRL deny; certs stay valid elsewhere).
    Create {
        /// Host ID
        #[arg(long)]
        host_id: String,
        /// Identity ID
        #[arg(long)]
        identity_id: String,
        /// Reason
        #[arg(short = 'r', long)]
        reason: Option<String>,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Lift a block (enforced on the next host KRL pull).
    Unblock {
        /// Host ID
        #[arg(long)]
        host_id: String,
        /// Identity ID
        #[arg(long)]
        identity_id: String,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Fleet-wide per-host block counts + KRL distribution state.
    Fleet {
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
}

#[derive(Subcommand, Debug)]
pub enum CertCmd {
    /// Revoke an SSH certificate (rebuilds the CA KRL).
    Revoke {
        /// SSH certificate ID
        cert_id: String,
        /// Reason
        #[arg(short = 'r', long)]
        reason: Option<String>,
        /// Skip confirmation
        #[arg(short = 'f', long)]
        force: bool,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Purge (hard-delete) an SSH certificate that was issued by mistake.
    ///
    /// This erases the database row; it does not recall copies of the certificate.
    /// To take a deployed host or a user out of service, offboard it instead.
    Purge {
        /// SSH certificate ID
        cert_id: String,
        /// Also purge a certificate that is revoked AND still within its validity window
        #[arg(long)]
        force_revoked: bool,
        /// With --force-revoked, also remove the serial from the KRL. DANGEROUS: a copy of the certificate works again
        #[arg(long)]
        drop_revocation: bool,
        /// Skip confirmation
        #[arg(short = 'f', long)]
        force: bool,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Json)]
        output: Format,
    },
}

/// A zone scopes SSH CAs, hosts, identities, principals and fleet tokens so one
/// installation can serve several tenants (server decision-017). Zone resolution
/// is fail-closed: the server picks the zone implicitly only while exactly one
/// is active, and errors once several are, so every creating command takes `--zone`.
#[derive(Subcommand, Debug)]
pub enum ZoneCmd {
    /// List SSH zones.
    List {
        /// Also list archived zones
        #[arg(long)]
        include_archived: bool,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Show one SSH zone by ID or name.
    Get {
        /// Zone ID or name
        #[arg(value_name = "REF")]
        zone_ref: String,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Create an SSH zone.
    ///
    /// Creating a second zone makes zone resolution ambiguous server-side, so from
    /// then on every `--zone`-bearing command must name one explicitly.
    Create {
        /// Zone slug — immutable once created
        #[arg(short = 'n', long)]
        name: String,
        /// Human-readable name
        #[arg(long)]
        display_name: Option<String>,
        /// Description
        #[arg(short = 'd', long)]
        description: Option<String>,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Update a zone's display name or description (the slug is immutable).
    Update {
        /// Zone ID or name
        #[arg(value_name = "REF")]
        zone_ref: String,
        /// New human-readable name
        #[arg(long)]
        display_name: Option<String>,
        /// New description
        #[arg(short = 'd', long)]
        description: Option<String>,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Archive a zone — blocks new entities and issuance, keeps serving existing trust material.
    Archive {
        /// Zone ID or name
        #[arg(value_name = "REF")]
        zone_ref: String,
        /// Skip confirmation
        #[arg(short = 'f', long)]
        force: bool,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
    /// Reactivate an archived zone.
    Unarchive {
        /// Zone ID or name
        #[arg(value_name = "REF")]
        zone_ref: String,
        /// Output format: table, json
        #[arg(short = 'o', long = "output", value_enum, default_value_t = Format::Table)]
        output: Format,
    },
}

// ---------------------------------------------------------------------------
// Shared helpers
// ---------------------------------------------------------------------------

/// JSON verbatim, a list as a table, an object as a panel, anything else as text.
fn render(data: &Value, format: Format, columns: Option<&[&str]>, title: Option<&str>) {
    if format.is_json() {
        output::json(data);
        return;
    }
    match data {
        Value::Array(items) => output::records(items, columns, title),
        Value::Object(_) => output::kv(data, title),
        Value::String(s) => println!("{s}"),
        other => println!("{}", output::scalar(other)),
    }
}

/// A text body as a string (a JSON body is pretty-printed).
fn as_text(data: &Value) -> String {
    match data {
        Value::String(s) => s.clone(),
        other => serde_json::to_string_pretty(other).unwrap_or_default(),
    }
}

/// `text` with a trailing newline unless it already ends with one.
fn with_newline(text: &str) -> String {
    if text.ends_with('\n') {
        text.to_string()
    } else {
        format!("{text}\n")
    }
}

/// Write text to `output_file`, or print it on stdout.
fn emit_text(data: &Value, output_file: Option<&Path>) -> Result<()> {
    let text = as_text(data);
    match output_file {
        Some(path) => {
            write_file(path, text.as_bytes())?;
            output::success(&format!("Saved to {}", path.display()));
        }
        None => {
            let mut out = std::io::stdout().lock();
            out.write_all(with_newline(&text).as_bytes())?;
            out.flush()?;
        }
    }
    Ok(())
}

/// Write bytes to `output_file`, or to `default_name` in the current directory.
fn emit_bytes(data: &[u8], output_file: Option<PathBuf>, default_name: String) -> Result<()> {
    let path = output_file.unwrap_or_else(|| PathBuf::from(default_name));
    write_file(&path, data)?;
    output::success(&format!("Saved {} bytes to {}", data.len(), path.display()));
    Ok(())
}

/// Non-blank, trimmed lines of an IDs file.
fn parse_ids(text: &str) -> Vec<String> {
    text.lines()
        .map(str::trim)
        .filter(|l| !l.is_empty())
        .map(str::to_string)
        .collect()
}

/// Merge repeated `--cert-id` flags with an optional one-ID-per-line file.
fn collect_ids(ids: Vec<String>, ids_file: Option<&Path>) -> Result<Vec<String>> {
    let mut collected = ids;
    if let Some(path) = ids_file {
        let text = std::fs::read_to_string(path)
            .with_context(|| format!("Cannot read {}", path.display()))?;
        collected.extend(parse_ids(&text));
    }
    if collected.is_empty() {
        bail!("At least one --cert-id (or --ids-file) is required");
    }
    Ok(collected)
}

/// A `--x/--no-x` pair as a tri-state (unset when neither flag is given).
fn tri_state(yes: bool, no: bool) -> Option<bool> {
    match (yes, no) {
        (true, _) => Some(true),
        (_, true) => Some(false),
        _ => None,
    }
}

/// `"true"` when the flag is set, else unset (the query parameter is omitted).
fn flag_param(set: bool) -> Option<&'static str> {
    set.then_some("true")
}

// ---------------------------------------------------------------------------
// Dispatch
// ---------------------------------------------------------------------------

pub fn run(api: &Api, cmd: SshCmd) -> Result<()> {
    match cmd {
        SshCmd::Ca(c) => run_ca(api, c),
        SshCmd::Host(c) => run_host(api, c),
        SshCmd::User(c) => run_user(api, c),
        SshCmd::Identity(c) => run_identity(api, c),
        SshCmd::Principal(c) => run_principal(api, c),
        SshCmd::Token(c) => run_token(api, c),
        SshCmd::Block(c) => run_block(api, c),
        SshCmd::Cert(c) => run_cert(api, c),
        SshCmd::Bulk(c) => run_bulk(api, c),
        SshCmd::Zone(c) => run_zone(api, c),
        SshCmd::TrustAnchors { zone, output } => {
            let data = api
                .get("/ssh/trust-anchors")
                .query_opt("zoneId", zone)
                .value()?;
            render(&data, output, None, None);
            Ok(())
        }
        SshCmd::Metrics { zone, output } => {
            let data = api.get("/ssh/metrics").query_opt("zoneId", zone).value()?;
            render(&data, output, None, None);
            Ok(())
        }
        SshCmd::TrustedUserCaKeys { output_file } => emit_text(
            &api.get("/ssh/trusted-user-ca-keys").public().value()?,
            output_file.as_deref(),
        ),
        SshCmd::HostCaKeys { output_file } => emit_text(
            &api.get("/ssh/host-ca-keys").public().value()?,
            output_file.as_deref(),
        ),
        SshCmd::CertAuthority {
            pattern,
            output_file,
        } => emit_text(
            &api.get("/ssh/cert-authority")
                .public()
                .query("pattern", pattern)
                .value()?,
            output_file.as_deref(),
        ),
        SshCmd::Krl {
            ca_id,
            fmt,
            output_file,
        } => {
            if fmt == "json" {
                output::json(&api.get(format!("/krl/{ca_id}.json")).public().value()?);
                Ok(())
            } else {
                let data = api.get(format!("/krl/{ca_id}.bin")).public().bytes()?;
                emit_bytes(&data, output_file, format!("revoked_keys-{ca_id}.krl"))
            }
        }
        SshCmd::KrlHost {
            host_id,
            fmt,
            output_file,
        } => {
            if fmt == "json" {
                output::json(
                    &api.get(format!("/krl/hosts/{host_id}.json"))
                        .public()
                        .value()?,
                );
                Ok(())
            } else {
                let data = api
                    .get(format!("/krl/hosts/{host_id}.bin"))
                    .public()
                    .bytes()?;
                emit_bytes(
                    &data,
                    output_file,
                    format!("revoked_keys-host-{host_id}.krl"),
                )
            }
        }
    }
}

fn run_ca(api: &Api, cmd: CaCmd) -> Result<()> {
    match cmd {
        CaCmd::List { zone, output } => {
            let data = api.get("/ssh/cas").query_opt("zoneId", zone).value()?;
            render(&data, output, Some(CA_COLUMNS), Some("SSH CAs"));
        }
        CaCmd::Create {
            ca_type,
            label,
            zone,
            output,
        } => {
            let b = body([
                ("caType", json!(ca_type)),
                ("label", json!(label)),
                ("zone", json!(zone)),
            ]);
            let data = api.post("/ssh/cas").json(b).value()?;
            output::success("SSH CA created");
            render(&data, output, None, None);
        }
        CaCmd::Pub { ca_id, output_file } => {
            emit_text(
                &api.get(format!("/ssh/cas/{ca_id}/ca.pub"))
                    .public()
                    .value()?,
                output_file.as_deref(),
            )?;
        }
        CaCmd::KrlGenerate { ca_id, output } => {
            let data = api.post(format!("/ssh/cas/{ca_id}/krl")).value()?;
            output::success("KRL generated");
            render(&data, output, None, None);
        }
        CaCmd::Revocations { ca_id, output } => {
            let data = api.get(format!("/ssh/cas/{ca_id}/revocations")).value()?;
            render(&data, output, None, Some("Revocations"));
        }
        CaCmd::Krl { ca_id, output_file } => {
            let data = api.get(format!("/ssh/cas/{ca_id}/krl.bin")).bytes()?;
            emit_bytes(&data, output_file, format!("revoked_keys-{ca_id}.krl"))?;
        }
        CaCmd::Get { ca_id, output } => {
            let data = api.get(format!("/ssh/cas/{ca_id}")).value()?;
            render(&data, output, None, Some("SSH CA"));
        }
        CaCmd::Import {
            ca_type,
            kms_key_id,
            kms_public_key_id,
            label,
            zone,
            output,
        } => {
            let b = body([
                ("caType", json!(ca_type)),
                ("label", json!(label)),
                ("kmsKeyId", json!(kms_key_id)),
                ("kmsPublicKeyId", json!(kms_public_key_id)),
                ("zone", json!(zone)),
            ]);
            let data = api.post("/ssh/cas/import").json(b).value()?;
            output::success("SSH CA imported");
            render(&data, output, None, None);
        }
        CaCmd::Revoke {
            ca_id,
            reason,
            force,
            output,
        } => {
            confirm(&format!("Revoke SSH CA {ca_id}?"), force)?;
            let data = api
                .post(format!("/ssh/cas/{ca_id}/revoke"))
                .json(body([("reason", json!(reason))]))
                .value()?;
            output::success("SSH CA revoked");
            render(&data, output, None, None);
        }
        CaCmd::Rotate {
            ca_id,
            force,
            output,
        } => {
            confirm(&format!("Rotate SSH CA {ca_id}?"), force)?;
            let data = api.post(format!("/ssh/cas/{ca_id}/rotate")).value()?;
            output::success("SSH CA rotated — distribute the new public key");
            render(&data, output, None, None);
        }
        CaCmd::Retire {
            ca_id,
            force,
            output,
        } => {
            confirm(&format!("Retire SSH CA {ca_id}?"), force)?;
            let data = api.post(format!("/ssh/cas/{ca_id}/retire")).value()?;
            output::success("SSH CA retired");
            render(&data, output, None, None);
        }
        CaCmd::ReissueReport { ca_id, output } => {
            let data = api
                .get(format!("/ssh/cas/{ca_id}/reissue-report"))
                .value()?;
            render(&data, output, None, Some("Re-issue report"));
        }
        CaCmd::RevokeSerial {
            ca_id,
            serial,
            reason,
            output,
        } => {
            let b = body([("serial", json!(serial)), ("reason", json!(reason))]);
            let data = api
                .post(format!("/ssh/cas/{ca_id}/revoke-serial"))
                .json(b)
                .value()?;
            output::success(&format!("Serial {serial} revoked (CA KRL rebuilt)"));
            render(&data, output, None, None);
        }
        CaCmd::RevokeKey {
            ca_id,
            fingerprint,
            reason,
            output,
        } => {
            let b = body([
                ("fingerprint", json!(fingerprint)),
                ("reason", json!(reason)),
            ]);
            let data = api
                .post(format!("/ssh/cas/{ca_id}/revoke-key"))
                .json(b)
                .value()?;
            output::success("Key fingerprint revoked (CA KRL rebuilt)");
            render(&data, output, None, None);
        }
    }
    Ok(())
}

fn run_host(api: &Api, cmd: HostCmd) -> Result<()> {
    match cmd {
        HostCmd::List { fqdn, zone, output } => {
            let data = api
                .get("/ssh/hosts")
                .query_opt("fqdn", fqdn)
                .query_opt("zoneId", zone)
                .value()?;
            render(&data, output, Some(HOST_COLUMNS), Some("SSH Hosts"));
        }
        HostCmd::Register {
            fqdn,
            pubkey,
            display_name,
            address,
            zone,
            output,
        } => {
            let b = body([
                ("fqdn", json!(fqdn)),
                ("displayName", json!(display_name)),
                ("addresses", json!(non_empty(address))),
                (
                    "opensshHostPubkey",
                    json!(read_value_or_file(Some(pubkey))?),
                ),
                ("zone", json!(zone)),
            ]);
            let data = api.post("/ssh/hosts").json(b).value()?;
            output::success("Host registered");
            render(&data, output, None, None);
        }
        HostCmd::Issue {
            host_id,
            ca_id,
            valid_for_seconds,
            key_id,
            serial,
            output,
        } => {
            let b = body([
                ("hostId", json!(host_id)),
                ("caId", json!(ca_id)),
                ("validForSeconds", json!(valid_for_seconds)),
                ("keyId", json!(key_id)),
                ("serial", json!(serial)),
            ]);
            let data = api.post("/ssh/hosts/issue").json(b).value()?;
            output::success("Host certificate issued");
            render(&data, output, None, None);
        }
        HostCmd::Access { host_id, output } => {
            render(
                &api.get(format!("/ssh/hosts/{host_id}/access")).value()?,
                output,
                None,
                None,
            );
        }
        HostCmd::Blocks { host_id, output } => {
            let data = api.get(format!("/ssh/hosts/{host_id}/blocks")).value()?;
            render(&data, output, None, Some("Host blocks"));
        }
        HostCmd::AuthPrincipals { host_id, output } => {
            render(
                &api.get(format!("/ssh/hosts/{host_id}/auth-principals"))
                    .value()?,
                output,
                None,
                None,
            );
        }
        HostCmd::MarkPushed { host_id, output } => {
            let data = api
                .post(format!("/ssh/hosts/{host_id}/auth-principals/pushed"))
                .value()?;
            output::success("Host marked as pushed");
            render(&data, output, None, None);
        }
        HostCmd::PrincipalMaps { host_id, output } => {
            let data = api
                .get(format!("/ssh/hosts/{host_id}/principal-maps"))
                .value()?;
            render(&data, output, None, Some("Host principal maps"));
        }
        HostCmd::Cert {
            host_id,
            output_file,
        } => {
            emit_text(
                &api.get(format!("/ssh/hosts/{host_id}/cert.pub"))
                    .public()
                    .value()?,
                output_file.as_deref(),
            )?;
        }
        HostCmd::SshdConfig {
            host_id,
            output_file,
        } => {
            emit_text(
                &api.get(format!("/ssh/hosts/{host_id}/sshd-config"))
                    .public()
                    .value()?,
                output_file.as_deref(),
            )?;
        }
        HostCmd::Get { host_id, output } => {
            render(
                &api.get(format!("/ssh/hosts/{host_id}")).value()?,
                output,
                None,
                Some("SSH Host"),
            );
        }
        HostCmd::DeployBundle { host_id, output } => {
            render(
                &api.get(format!("/ssh/hosts/{host_id}/deploy-bundle"))
                    .value()?,
                output,
                None,
                None,
            );
        }
        HostCmd::Revoke {
            host_id,
            reason,
            force,
        } => {
            confirm(
                &format!("Revoke the current certificate of host {host_id}?"),
                force,
            )?;
            api.post(format!("/ssh/hosts/{host_id}/revoke"))
                .json(body([("reason", json!(reason))]))
                .value()?;
            output::success("Host certificate revoked");
        }
        HostCmd::EciesKey { host_id, output } => {
            let data = api
                .post(format!("/ssh/hosts/{host_id}/ecies-key"))
                .value()?;
            output::success("ECIES recipient key registered");
            render(&data, output, None, None);
        }
        HostCmd::Offboard {
            host_id,
            reason,
            force,
        } => {
            confirm(
                &format!("Offboard host {host_id}? This is terminal."),
                force,
            )?;
            api.post(format!("/ssh/hosts/{host_id}/offboard"))
                .json(body([("reason", json!(reason))]))
                .value()?;
            output::success("Host offboarded");
        }
    }
    Ok(())
}

fn run_identity(api: &Api, cmd: IdentityCmd) -> Result<()> {
    match cmd {
        IdentityCmd::Create {
            subject,
            email,
            external_subject,
            zone,
            output,
        } => {
            let b = body([
                ("subject", json!(subject)),
                ("email", json!(email)),
                ("externalSubject", json!(external_subject)),
                ("zone", json!(zone)),
            ]);
            let data = api.post("/ssh/identities").json(b).value()?;
            output::success("Identity created");
            render(&data, output, None, None);
        }
        IdentityCmd::Blocks {
            identity_id,
            output,
        } => {
            let data = api
                .get(format!("/ssh/identities/{identity_id}/blocks"))
                .value()?;
            render(&data, output, None, Some("Identity blocks"));
        }
        IdentityCmd::Collisions {
            identity_id,
            output,
        } => {
            let data = api
                .get(format!("/ssh/identities/{identity_id}/collisions"))
                .value()?;
            render(&data, output, None, Some("Key collisions"));
        }
        IdentityCmd::Grants {
            identity_id,
            output,
        } => {
            let data = api
                .get(format!("/ssh/identities/{identity_id}/grants"))
                .value()?;
            render(&data, output, None, Some("Identity grants"));
        }
        IdentityCmd::List { zone, output } => {
            let data = api
                .get("/ssh/identities")
                .query_opt("zoneId", zone)
                .value()?;
            render(
                &data,
                output,
                Some(IDENTITY_COLUMNS),
                Some("SSH Identities"),
            );
        }
        IdentityCmd::Disable { identity_id, force } => {
            confirm(&format!("Disable identity {identity_id}?"), force)?;
            api.post(format!("/ssh/identities/{identity_id}/disable"))
                .value()?;
            output::success("Identity disabled");
        }
        IdentityCmd::Offboard {
            identity_id,
            reason,
            force,
        } => {
            confirm(
                &format!("Offboard identity {identity_id}? Live certificates will be revoked."),
                force,
            )?;
            api.post(format!("/ssh/identities/{identity_id}/offboard"))
                .json(body([("reason", json!(reason))]))
                .value()?;
            output::success("Identity offboarded");
        }
    }
    Ok(())
}

fn run_user(api: &Api, cmd: UserCmd) -> Result<()> {
    match cmd {
        UserCmd::Issue {
            identity_id,
            pubkey,
            principal,
            ca_id,
            extension,
            force_command,
            source_address,
            valid_for_seconds,
            key_id,
            enforce_entitlement,
            no_enforce_entitlement,
            output,
        } => {
            if principal.is_empty() {
                bail!("At least one --principal (role) is required");
            }
            let b = body([
                ("identityId", json!(identity_id)),
                ("caId", json!(ca_id)),
                ("sshPublicKey", json!(read_value_or_file(Some(pubkey))?)),
                ("principals", json!(principal)),
                ("extensions", json!(non_empty(extension))),
                ("forceCommand", json!(force_command)),
                ("sourceAddress", json!(source_address)),
                ("validForSeconds", json!(valid_for_seconds)),
                ("keyId", json!(key_id)),
                (
                    "enforceEntitlement",
                    json!(tri_state(enforce_entitlement, no_enforce_entitlement)),
                ),
            ]);
            let data = api.post("/ssh/users/issue").json(b).value()?;
            output::success("User certificate issued");
            render(&data, output, None, None);
        }
        UserCmd::Certificates {
            identity_id,
            output,
        } => {
            let data = api
                .get("/ssh/users/certificates")
                .query_opt("identityId", identity_id)
                .value()?;
            render(
                &data,
                output,
                Some(USER_CERT_COLUMNS),
                Some("User Certificates"),
            );
        }
    }
    Ok(())
}

fn run_principal(api: &Api, cmd: PrincipalCmd) -> Result<()> {
    match cmd {
        PrincipalCmd::List { zone, output } => {
            let data = api
                .get("/ssh/principals")
                .query_opt("zoneId", zone)
                .value()?;
            render(&data, output, None, Some("SSH Principals"));
        }
        PrincipalCmd::Create {
            name,
            description,
            zone,
            output,
        } => {
            let b = body([
                ("name", json!(name)),
                ("description", json!(description)),
                ("zone", json!(zone)),
            ]);
            let data = api.post("/ssh/principals").json(b).value()?;
            output::success("Principal created");
            render(&data, output, None, None);
        }
        PrincipalCmd::Map {
            host_id,
            principal_id,
            local_account,
        } => {
            let b = body([
                ("hostId", json!(host_id)),
                ("principalId", json!(principal_id)),
                ("localAccount", json!(local_account)),
            ]);
            api.post("/ssh/principals/map").json(b).value()?;
            output::success("Principal mapped to host account");
        }
        PrincipalCmd::Grant {
            identity_id,
            principal_id,
        } => {
            let b = body([
                ("identityId", json!(identity_id)),
                ("principalId", json!(principal_id)),
            ]);
            api.post("/ssh/principals/grant").json(b).value()?;
            output::success("Entitlement granted");
        }
        PrincipalCmd::Unmap {
            host_id,
            principal_id,
            local_account,
        } => {
            let b = body([
                ("hostId", json!(host_id)),
                ("principalId", json!(principal_id)),
                ("localAccount", json!(local_account)),
            ]);
            api.post("/ssh/principals/unmap").json(b).value()?;
            output::success("Principal unmapped from host account");
        }
        PrincipalCmd::RevokeGrant {
            identity_id,
            principal_id,
        } => {
            let b = body([
                ("identityId", json!(identity_id)),
                ("principalId", json!(principal_id)),
            ]);
            api.post("/ssh/principals/revoke-grant").json(b).value()?;
            output::success("Entitlement removed");
        }
        PrincipalCmd::Mappings { zone, output } => {
            // This route takes `zone` (ID or slug), not `zoneId` like the lists.
            let data = api
                .get("/ssh/principals/mappings")
                .query_opt("zone", zone)
                .value()?;
            render(&data, output, None, Some("Principal mappings"));
        }
        PrincipalCmd::StaleHosts { output } => {
            let data = api.get("/ssh/principals/stale-hosts").value()?;
            render(&data, output, None, Some("Stale hosts"));
        }
        PrincipalCmd::Delete {
            principal_id,
            force,
        } => {
            confirm(&format!("Delete principal {principal_id}?"), force)?;
            api.delete(format!("/ssh/principals/{principal_id}"))
                .value()?;
            output::success("Principal deleted");
        }
    }
    Ok(())
}

fn run_token(api: &Api, cmd: TokenCmd) -> Result<()> {
    match cmd {
        TokenCmd::List { output } => {
            render(
                &api.get("/ssh/tokens").value()?,
                output,
                None,
                Some("Fleet Tokens"),
            );
        }
        TokenCmd::Mint {
            name,
            op,
            user_ca_id,
            host_ca_id,
            zone,
            allowed_principal,
            max_valid_for_seconds,
            output,
        } => {
            if op.is_empty() {
                bail!("At least one --op is required");
            }
            let b = body([
                ("name", json!(name)),
                ("opSet", json!(op)),
                ("userCaId", json!(user_ca_id)),
                ("hostCaId", json!(host_ca_id)),
                ("zone", json!(zone)),
                ("allowedPrincipals", json!(non_empty(allowed_principal))),
                ("maxValidForSeconds", json!(max_valid_for_seconds)),
            ]);
            let data = api.post("/ssh/tokens").json(b).value()?;
            output::success("Fleet token minted — copy the secret now, it is not shown again");
            render(&data, output, None, None);
        }
        TokenCmd::Revoke { token_id, force } => {
            confirm(&format!("Revoke fleet token {token_id}?"), force)?;
            api.post(format!("/ssh/tokens/{token_id}/revoke")).value()?;
            output::success(&format!("Token {token_id} revoked"));
        }
    }
    Ok(())
}

fn run_bulk(api: &Api, cmd: BulkCmd) -> Result<()> {
    match cmd {
        BulkCmd::Expiring {
            within_seconds,
            output,
        } => {
            let data = api
                .get("/ssh/bulk/expiring")
                .query("withinSeconds", within_seconds)
                .value()?;
            render(&data, output, None, Some("Expiring SSH certificates"));
        }
        BulkCmd::Renew {
            cert_id,
            ids_file,
            output,
        } => {
            let ids = collect_ids(cert_id, ids_file.as_deref())?;
            let n = ids.len();
            let data = api
                .post("/ssh/bulk/renew")
                .json(json!({ "certIds": ids }))
                .value()?;
            output::success(&format!("Renew requested for {n} certificate(s)"));
            render(&data, output, None, None);
        }
        BulkCmd::Revoke {
            cert_id,
            ids_file,
            reason,
            force,
            output,
        } => {
            let ids = collect_ids(cert_id, ids_file.as_deref())?;
            let n = ids.len();
            confirm(&format!("Revoke {n} SSH certificate(s)?"), force)?;
            let b = body([("certIds", json!(ids)), ("reason", json!(reason))]);
            let data = api.post("/ssh/bulk/revoke").json(b).value()?;
            output::success(&format!("Revoke requested for {n} certificate(s)"));
            render(&data, output, None, None);
        }
    }
    Ok(())
}

fn run_block(api: &Api, cmd: BlockCmd) -> Result<()> {
    match cmd {
        BlockCmd::Create {
            host_id,
            identity_id,
            reason,
            output,
        } => {
            let b = body([
                ("hostId", json!(host_id)),
                ("identityId", json!(identity_id)),
                ("reason", json!(reason)),
            ]);
            let data = api.post("/ssh/blocks").json(b).value()?;
            output::success("Identity blocked on host");
            render(&data, output, None, None);
        }
        BlockCmd::Unblock {
            host_id,
            identity_id,
            output,
        } => {
            let b = body([
                ("hostId", json!(host_id)),
                ("identityId", json!(identity_id)),
            ]);
            let data = api.post("/ssh/blocks/unblock").json(b).value()?;
            output::success("Block lifted");
            render(&data, output, None, None);
        }
        BlockCmd::Fleet { output } => {
            let data = api.get("/ssh/blocks/fleet").value()?;
            render(
                &data,
                output,
                Some(FLEET_COLUMNS),
                Some("Fleet block distribution"),
            );
        }
    }
    Ok(())
}

fn run_cert(api: &Api, cmd: CertCmd) -> Result<()> {
    match cmd {
        CertCmd::Revoke {
            cert_id,
            reason,
            force,
            output,
        } => {
            confirm(&format!("Revoke SSH certificate {cert_id}?"), force)?;
            let data = api
                .post(format!("/ssh/certs/{cert_id}/revoke"))
                .json(body([("reason", json!(reason))]))
                .value()?;
            output::success("SSH certificate revoked (CA KRL rebuilt)");
            render(&data, output, None, None);
        }
        CertCmd::Purge {
            cert_id,
            force_revoked,
            drop_revocation,
            force,
            output,
        } => {
            if drop_revocation && !force_revoked {
                bail!("--drop-revocation needs --force-revoked");
            }
            confirm(
                &format!("Purge SSH certificate {cert_id}? This cannot be undone."),
                force,
            )?;
            let data = api
                .delete(format!("/ssh/certs/{cert_id}"))
                .query_opt("force", flag_param(force_revoked))
                .query_opt("dropRevocation", flag_param(drop_revocation))
                .value()?;
            output::success("SSH certificate purged");
            render(&data, output, None, None);
        }
    }
    Ok(())
}

fn run_zone(api: &Api, cmd: ZoneCmd) -> Result<()> {
    match cmd {
        ZoneCmd::List {
            include_archived,
            output,
        } => {
            let data = api
                .get("/ssh/zones")
                .query_opt("includeArchived", flag_param(include_archived))
                .value()?;
            render(&data, output, Some(ZONE_COLUMNS), Some("SSH Zones"));
        }
        ZoneCmd::Get { zone_ref, output } => {
            render(
                &api.get(format!("/ssh/zones/{zone_ref}")).value()?,
                output,
                None,
                Some("SSH Zone"),
            );
        }
        ZoneCmd::Create {
            name,
            display_name,
            description,
            output,
        } => {
            let b = body([
                ("name", json!(name)),
                ("displayName", json!(display_name)),
                ("description", json!(description)),
            ]);
            let data = api.post("/ssh/zones").json(b).value()?;
            output::success(&format!("Zone {name} created"));
            render(&data, output, None, None);
        }
        ZoneCmd::Update {
            zone_ref,
            display_name,
            description,
            output,
        } => {
            if display_name.is_none() && description.is_none() {
                bail!("Nothing to update — pass --display-name and/or --description");
            }
            let b = body([
                ("displayName", json!(display_name)),
                ("description", json!(description)),
            ]);
            let data = api.post(format!("/ssh/zones/{zone_ref}")).json(b).value()?;
            output::success(&format!("Zone {zone_ref} updated"));
            render(&data, output, None, None);
        }
        ZoneCmd::Archive {
            zone_ref,
            force,
            output,
        } => {
            confirm(&format!("Archive zone {zone_ref}?"), force)?;
            let data = api.post(format!("/ssh/zones/{zone_ref}/archive")).value()?;
            output::success(&format!("Zone {zone_ref} archived"));
            render(&data, output, None, None);
        }
        ZoneCmd::Unarchive { zone_ref, output } => {
            let data = api
                .post(format!("/ssh/zones/{zone_ref}/unarchive"))
                .value()?;
            output::success(&format!("Zone {zone_ref} reactivated"));
            render(&data, output, None, None);
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use clap::{CommandFactory, Parser};

    #[derive(Parser, Debug)]
    struct T {
        #[command(subcommand)]
        c: SshCmd,
    }

    #[test]
    fn command_definition_is_valid() {
        T::command().debug_assert();
    }

    fn parse(args: &[&str]) -> SshCmd {
        T::try_parse_from(std::iter::once("t").chain(args.iter().copied()))
            .unwrap()
            .c
    }

    #[test]
    fn ids_file_lines() {
        assert_eq!(parse_ids("a\n  b  \n\n\tc\n"), vec!["a", "b", "c"]);
        assert!(parse_ids("\n \n").is_empty());
    }

    #[test]
    fn collect_ids_merges_flags_and_file() {
        let dir = tempfile::tempdir().unwrap();
        let p = dir.path().join("ids.txt");
        std::fs::write(&p, "x\n\ny\n").unwrap();
        assert_eq!(
            collect_ids(vec!["a".into()], Some(&p)).unwrap(),
            vec!["a", "x", "y"]
        );
        let err = collect_ids(vec![], None).unwrap_err().to_string();
        assert_eq!(err, "At least one --cert-id (or --ids-file) is required");
    }

    #[test]
    fn tri_state_flags() {
        assert_eq!(tri_state(false, false), None);
        assert_eq!(tri_state(true, false), Some(true));
        assert_eq!(tri_state(false, true), Some(false));
    }

    #[test]
    fn enforce_entitlement_last_flag_wins() {
        let SshCmd::User(UserCmd::Issue {
            enforce_entitlement,
            no_enforce_entitlement,
            ..
        }) = parse(&[
            "user",
            "issue",
            "--identity-id",
            "i",
            "-k",
            "k",
            "--enforce-entitlement",
            "--no-enforce-entitlement",
        ])
        else {
            panic!("wrong command");
        };
        assert_eq!(
            tri_state(enforce_entitlement, no_enforce_entitlement),
            Some(false)
        );
    }

    #[test]
    fn text_newline() {
        assert_eq!(with_newline("a"), "a\n");
        assert_eq!(with_newline("a\n"), "a\n");
        assert_eq!(as_text(&json!("k")), "k");
        assert_eq!(as_text(&json!({"a": 1})), "{\n  \"a\": 1\n}");
    }

    #[test]
    fn flag_params() {
        assert_eq!(flag_param(true), Some("true"));
        assert_eq!(flag_param(false), None);
    }

    #[test]
    fn aliases_defaults_and_ranges() {
        let SshCmd::Host(HostCmd::Issue {
            valid_for_seconds,
            output,
            ..
        }) = parse(&["host", "issue", "--host-id", "h", "--ttl", "60"])
        else {
            panic!("wrong command");
        };
        assert_eq!(valid_for_seconds, Some(60));
        assert_eq!(output, Format::Table);

        let SshCmd::Bulk(BulkCmd::Expiring { within_seconds, .. }) = parse(&["bulk", "expiring"])
        else {
            panic!("wrong command");
        };
        assert_eq!(within_seconds, 604800);

        assert!(
            T::try_parse_from([
                "t",
                "token",
                "mint",
                "-n",
                "x",
                "--op",
                "sign-host",
                "--max-ttl",
                "0"
            ])
            .is_err()
        );
        let SshCmd::Token(TokenCmd::Mint {
            max_valid_for_seconds,
            op,
            output,
            ..
        }) = parse(&[
            "token",
            "mint",
            "-n",
            "x",
            "--op",
            "a",
            "--op",
            "b",
            "--max-ttl",
            "5",
        ])
        else {
            panic!("wrong command");
        };
        assert_eq!(max_valid_for_seconds, Some(5));
        assert_eq!(op, vec!["a", "b"]);
        assert_eq!(output, Format::Json);

        let SshCmd::Krl { fmt, .. } = parse(&["krl", "ca1"]) else {
            panic!("wrong command")
        };
        assert_eq!(fmt, "bin");
        let SshCmd::CertAuthority { pattern, .. } = parse(&["cert-authority"]) else {
            panic!("wrong command")
        };
        assert_eq!(pattern, "*");
    }

    #[test]
    fn user_issue_body_drops_unset_fields() {
        let b = body([
            ("identityId", json!("i")),
            ("principals", json!(vec!["root"])),
            ("extensions", json!(non_empty(Vec::<String>::new()))),
            ("enforceEntitlement", json!(tri_state(false, false))),
            ("validForSeconds", json!(Some(30))),
        ]);
        assert_eq!(
            b,
            json!({"identityId": "i", "principals": ["root"], "validForSeconds": 30})
        );
    }
}
