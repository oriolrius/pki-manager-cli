"""`pki ssh` — SSH Certificate Manager commands.

Wraps the authenticated ``/api/v1/ssh/*`` surface (CAs, hosts, user identities,
principals, fleet tokens, per-host blocks, revocation) plus the unauthenticated
public trust-material and KRL download routes served at the server root.

These routes are not modelled by the generated OpenAPI client (the spec omits
their request/response schemas), so commands talk to the API through the thin
helpers in :mod:`pki_cli.http`, reusing the same OIDC token as the rest of the CLI.
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

from .http import ApiError, authed, public, read_value_or_file
from .output import print_error, print_json, print_kv, print_records, print_success

console = Console()

ssh_app = typer.Typer(
    name="ssh",
    help="SSH Certificate Manager (CAs, hosts, users, tokens, blocks)",
    no_args_is_help=True,
)

ca_app = typer.Typer(help="SSH CA management", no_args_is_help=True)
host_app = typer.Typer(help="SSH host registration & certificates", no_args_is_help=True)
user_app = typer.Typer(help="SSH user certificate issuance", no_args_is_help=True)
identity_app = typer.Typer(help="SSH user identities", no_args_is_help=True)
principal_app = typer.Typer(help="SSH principals (roles) & mappings", no_args_is_help=True)
token_app = typer.Typer(help="Fleet automation tokens", no_args_is_help=True)
block_app = typer.Typer(help="Per-host access blocks", no_args_is_help=True)
cert_app = typer.Typer(help="SSH certificate revocation", no_args_is_help=True)

ssh_app.add_typer(ca_app, name="ca")
ssh_app.add_typer(host_app, name="host")
ssh_app.add_typer(user_app, name="user")
ssh_app.add_typer(identity_app, name="identity")
ssh_app.add_typer(principal_app, name="principal")
ssh_app.add_typer(token_app, name="token")
ssh_app.add_typer(block_app, name="block")
ssh_app.add_typer(cert_app, name="cert")

OutputFormat = Annotated[str, typer.Option("--output", "-o", help="Output format: table, json")]
OutFile = Annotated[Optional[Path], typer.Option("--output", "-o", help="Write output to a file instead of stdout")]


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
@contextmanager
def _api():
    """Turn API/transport errors into a clean CLI error + non-zero exit."""
    try:
        yield
    except typer.Exit:
        raise
    except ApiError as exc:
        print_error(str(exc))
        raise typer.Exit(1)
    except Exception as exc:  # noqa: BLE001 - surface any client error uniformly
        print_error(str(exc))
        raise typer.Exit(1)


def _body(**kwargs) -> dict:
    """Build a request body, omitting keys whose value is ``None``."""
    return {k: v for k, v in kwargs.items() if v is not None}


def _render(data, output: str, *, columns: list[str] | None = None, title: str | None = None) -> None:
    if output == "json":
        print_json(data)
    elif isinstance(data, list):
        print_records(data, columns=columns, title=title)
    elif isinstance(data, dict):
        print_kv(data, title=title)
    else:
        console.print(str(data))


def _emit_text(text: str, output_file: Optional[Path]) -> None:
    if output_file:
        Path(output_file).write_text(text)
        print_success(f"Saved to {output_file}")
    else:
        typer.echo(text, nl=not text.endswith("\n"))


def _emit_bytes(data: bytes, output_file: Optional[Path], default_name: str) -> None:
    path = Path(output_file) if output_file else Path(default_name)
    path.write_bytes(data)
    print_success(f"Saved {len(data)} bytes to {path}")


# ---------------------------------------------------------------------------
# CA
# ---------------------------------------------------------------------------
CA_COLUMNS = ["id", "caType", "label", "keyAlgorithm", "status", "nextSerial", "createdAt"]
HOST_COLUMNS = ["id", "fqdn", "displayName", "status", "hasPubkey", "hostKeyAlgorithm", "lastKrlVersion", "enrolledAt"]
FLEET_COLUMNS = ["fqdn", "status", "blockCount", "krlNumber", "lastKrlVersion", "lastKrlFetchAt"]


@ca_app.command("list")
def ca_list(output: OutputFormat = "table") -> None:
    """List SSH CAs (user + host)."""
    with _api():
        _render(authed("GET", "/ssh/cas"), output, columns=CA_COLUMNS, title="SSH CAs")


@ca_app.command("create")
def ca_create(
    ca_type: Annotated[str, typer.Option("--type", "-t", help="CA type: user or host")],
    label: Annotated[Optional[str], typer.Option("--label", "-l", help="Human-readable label")] = None,
    output: OutputFormat = "table",
) -> None:
    """Create an SSH CA (user or host)."""
    with _api():
        data = authed("POST", "/ssh/cas", json=_body(caType=ca_type, label=label))
        print_success("SSH CA created")
        _render(data, output)


@ca_app.command("pub")
def ca_pub(
    ca_id: Annotated[str, typer.Argument(help="SSH CA ID")],
    output_file: OutFile = None,
) -> None:
    """Print a CA's OpenSSH public key (public endpoint)."""
    with _api():
        _emit_text(public("GET", f"/ssh/cas/{ca_id}/ca.pub"), output_file)


@ca_app.command("krl-generate")
def ca_krl_generate(
    ca_id: Annotated[str, typer.Argument(help="SSH CA ID")],
    output: OutputFormat = "table",
) -> None:
    """Generate / rebuild the KRL for a CA."""
    with _api():
        data = authed("POST", f"/ssh/cas/{ca_id}/krl")
        print_success("KRL generated")
        _render(data, output)


@ca_app.command("revocations")
def ca_revocations(
    ca_id: Annotated[str, typer.Argument(help="SSH CA ID")],
    output: OutputFormat = "table",
) -> None:
    """List revocations recorded for a CA."""
    with _api():
        _render(authed("GET", f"/ssh/cas/{ca_id}/revocations"), output, title="Revocations")


@ca_app.command("krl")
def ca_krl(
    ca_id: Annotated[str, typer.Argument(help="SSH CA ID")],
    output_file: OutFile = None,
) -> None:
    """Download the CA's bare KRL bytes (authenticated)."""
    with _api():
        data = authed("GET", f"/ssh/cas/{ca_id}/krl.bin", expect_bytes=True)
        _emit_bytes(data, output_file, f"revoked_keys-{ca_id}.krl")


# ---------------------------------------------------------------------------
# Host
# ---------------------------------------------------------------------------
@host_app.command("list")
def host_list(
    fqdn: Annotated[Optional[str], typer.Option("--fqdn", help="Filter by FQDN")] = None,
    output: OutputFormat = "table",
) -> None:
    """List registered SSH hosts."""
    with _api():
        _render(authed("GET", "/ssh/hosts", params={"fqdn": fqdn}), output, columns=HOST_COLUMNS, title="SSH Hosts")


@host_app.command("register")
def host_register(
    fqdn: Annotated[str, typer.Option("--fqdn", help="Host FQDN")],
    pubkey: Annotated[str, typer.Option("--pubkey", "-k", help="OpenSSH host public key (or @file)")],
    display_name: Annotated[Optional[str], typer.Option("--display-name", help="Display name")] = None,
    address: Annotated[Optional[list[str]], typer.Option("--address", "-a", help="Host address (repeatable)")] = None,
    output: OutputFormat = "table",
) -> None:
    """Register a host by its OpenSSH host public key."""
    with _api():
        body = _body(
            fqdn=fqdn,
            displayName=display_name,
            addresses=address,
            opensshHostPubkey=read_value_or_file(pubkey),
        )
        data = authed("POST", "/ssh/hosts", json=body)
        print_success("Host registered")
        _render(data, output)


@host_app.command("issue")
def host_issue(
    host_id: Annotated[str, typer.Option("--host-id", help="Host ID")],
    ca_id: Annotated[Optional[str], typer.Option("--ca-id", help="Host CA ID (defaults to active host CA)")] = None,
    valid_for_seconds: Annotated[Optional[int], typer.Option("--valid-for-seconds", "--ttl", help="Validity in seconds")] = None,
    key_id: Annotated[Optional[str], typer.Option("--key-id", help="Certificate key_id (logged by sshd)")] = None,
    serial: Annotated[Optional[str], typer.Option("--serial", help="Explicit serial (integer string)")] = None,
    output: OutputFormat = "table",
) -> None:
    """Issue a host certificate."""
    with _api():
        body = _body(hostId=host_id, caId=ca_id, validForSeconds=valid_for_seconds, keyId=key_id, serial=serial)
        data = authed("POST", "/ssh/hosts/issue", json=body)
        print_success("Host certificate issued")
        _render(data, output)


@host_app.command("access")
def host_access(host_id: Annotated[str, typer.Argument(help="Host ID")], output: OutputFormat = "json") -> None:
    """Show who can reach a host (entitlements + blocks + distribution state)."""
    with _api():
        _render(authed("GET", f"/ssh/hosts/{host_id}/access"), output)


@host_app.command("blocks")
def host_blocks(host_id: Annotated[str, typer.Argument(help="Host ID")], output: OutputFormat = "table") -> None:
    """Show a host's block history (active + lifted)."""
    with _api():
        _render(authed("GET", f"/ssh/hosts/{host_id}/blocks"), output, title="Host blocks")


@host_app.command("auth-principals")
def host_auth_principals(host_id: Annotated[str, typer.Argument(help="Host ID")], output: OutputFormat = "json") -> None:
    """Render a host's AuthorizedPrincipalsFile contents (authenticated)."""
    with _api():
        _render(authed("GET", f"/ssh/hosts/{host_id}/auth-principals"), output)


@host_app.command("cert")
def host_cert(host_id: Annotated[str, typer.Argument(help="Host ID")], output_file: OutFile = None) -> None:
    """Print a host's current certificate (public endpoint)."""
    with _api():
        _emit_text(public("GET", f"/ssh/hosts/{host_id}/cert.pub"), output_file)


@host_app.command("sshd-config")
def host_sshd_config(host_id: Annotated[str, typer.Argument(help="Host ID")], output_file: OutFile = None) -> None:
    """Print the ready-to-paste sshd_config drop-in for a host (public endpoint)."""
    with _api():
        _emit_text(public("GET", f"/ssh/hosts/{host_id}/sshd-config"), output_file)


# ---------------------------------------------------------------------------
# Identities
# ---------------------------------------------------------------------------
@identity_app.command("create")
def identity_create(
    subject: Annotated[str, typer.Option("--subject", "-s", help="Identity subject")],
    email: Annotated[Optional[str], typer.Option("--email", help="Email")] = None,
    external_subject: Annotated[Optional[str], typer.Option("--external-subject", help="External IdP subject")] = None,
    output: OutputFormat = "table",
) -> None:
    """Create a user identity."""
    with _api():
        body = _body(subject=subject, email=email, externalSubject=external_subject)
        data = authed("POST", "/ssh/identities", json=body)
        print_success("Identity created")
        _render(data, output)


@identity_app.command("blocks")
def identity_blocks(identity_id: Annotated[str, typer.Argument(help="Identity ID")], output: OutputFormat = "table") -> None:
    """Show an identity's active blocks with per-host distribution state."""
    with _api():
        _render(authed("GET", f"/ssh/identities/{identity_id}/blocks"), output, title="Identity blocks")


@identity_app.command("collisions")
def identity_collisions(identity_id: Annotated[str, typer.Argument(help="Identity ID")], output: OutputFormat = "table") -> None:
    """List identities sharing a certified public key with this one."""
    with _api():
        _render(authed("GET", f"/ssh/identities/{identity_id}/collisions"), output, title="Key collisions")


# ---------------------------------------------------------------------------
# User certificate issuance
# ---------------------------------------------------------------------------
@user_app.command("issue")
def user_issue(
    identity_id: Annotated[str, typer.Option("--identity-id", help="Identity ID")],
    pubkey: Annotated[str, typer.Option("--pubkey", "-k", help="User's SSH public key (or @file)")],
    principal: Annotated[Optional[list[str]], typer.Option("--principal", "-p", help="Principal/role (repeatable, at least one)")] = None,
    ca_id: Annotated[Optional[str], typer.Option("--ca-id", help="User CA ID (defaults to active user CA)")] = None,
    extension: Annotated[Optional[list[str]], typer.Option("--extension", "-e", help="SSH extension, e.g. permit-pty (repeatable)")] = None,
    force_command: Annotated[Optional[str], typer.Option("--force-command", help="force-command restriction")] = None,
    source_address: Annotated[Optional[str], typer.Option("--source-address", help="source-address CIDR list")] = None,
    valid_for_seconds: Annotated[Optional[int], typer.Option("--valid-for-seconds", "--ttl", help="Validity in seconds")] = None,
    key_id: Annotated[Optional[str], typer.Option("--key-id", help="Certificate key_id (logged by sshd)")] = None,
    enforce_entitlement: Annotated[Optional[bool], typer.Option("--enforce-entitlement/--no-enforce-entitlement", help="Enforce principal entitlements")] = None,
    output: OutputFormat = "table",
) -> None:
    """Issue a user certificate."""
    if not principal:
        print_error("At least one --principal (role) is required")
        raise typer.Exit(1)
    with _api():
        body = _body(
            identityId=identity_id,
            caId=ca_id,
            sshPublicKey=read_value_or_file(pubkey),
            principals=principal,
            extensions=extension,
            forceCommand=force_command,
            sourceAddress=source_address,
            validForSeconds=valid_for_seconds,
            keyId=key_id,
            enforceEntitlement=enforce_entitlement,
        )
        data = authed("POST", "/ssh/users/issue", json=body)
        print_success("User certificate issued")
        _render(data, output)


# ---------------------------------------------------------------------------
# Principals
# ---------------------------------------------------------------------------
@principal_app.command("list")
def principal_list(output: OutputFormat = "table") -> None:
    """List SSH principals (roles)."""
    with _api():
        _render(authed("GET", "/ssh/principals"), output, title="SSH Principals")


@principal_app.command("create")
def principal_create(
    name: Annotated[str, typer.Option("--name", "-n", help="Principal name")],
    description: Annotated[Optional[str], typer.Option("--description", "-d", help="Description")] = None,
    output: OutputFormat = "table",
) -> None:
    """Create an SSH principal (role)."""
    with _api():
        data = authed("POST", "/ssh/principals", json=_body(name=name, description=description))
        print_success("Principal created")
        _render(data, output)


@principal_app.command("map")
def principal_map(
    host_id: Annotated[str, typer.Option("--host-id", help="Host ID")],
    principal_id: Annotated[str, typer.Option("--principal-id", help="Principal ID")],
    local_account: Annotated[str, typer.Option("--local-account", help="Local account name on the host")],
) -> None:
    """Map a principal to a local account on a host."""
    with _api():
        authed(
            "POST",
            "/ssh/principals/map",
            json=_body(hostId=host_id, principalId=principal_id, localAccount=local_account),
        )
        print_success("Principal mapped to host account")


@principal_app.command("grant")
def principal_grant(
    identity_id: Annotated[str, typer.Option("--identity-id", help="Identity ID")],
    principal_id: Annotated[str, typer.Option("--principal-id", help="Principal ID")],
) -> None:
    """Grant an identity the entitlement to encode a principal."""
    with _api():
        authed("POST", "/ssh/principals/grant", json=_body(identityId=identity_id, principalId=principal_id))
        print_success("Entitlement granted")


# ---------------------------------------------------------------------------
# Fleet tokens
# ---------------------------------------------------------------------------
@token_app.command("list")
def token_list(output: OutputFormat = "table") -> None:
    """List fleet tokens (metadata only, no secrets)."""
    with _api():
        _render(authed("GET", "/ssh/tokens"), output, title="Fleet Tokens")


@token_app.command("mint")
def token_mint(
    name: Annotated[str, typer.Option("--name", "-n", help="Token name")],
    op: Annotated[Optional[list[str]], typer.Option("--op", help="Allowed op (repeatable): sign-host, sign-user, register-host-pubkey, get-principals")] = None,
    user_ca_id: Annotated[Optional[str], typer.Option("--user-ca-id", help="User CA the token may sign for")] = None,
    host_ca_id: Annotated[Optional[str], typer.Option("--host-ca-id", help="Host CA the token may sign for")] = None,
    output: OutputFormat = "json",
) -> None:
    """Mint a fleet token (plaintext secret shown once)."""
    if not op:
        print_error("At least one --op is required")
        raise typer.Exit(1)
    with _api():
        data = authed("POST", "/ssh/tokens", json=_body(name=name, opSet=op, userCaId=user_ca_id, hostCaId=host_ca_id))
        print_success("Fleet token minted — copy the secret now, it is not shown again")
        _render(data, output)


@token_app.command("revoke")
def token_revoke(
    token_id: Annotated[str, typer.Argument(help="Fleet token ID")],
    force: Annotated[bool, typer.Option("--force", "-f", help="Skip confirmation")] = False,
) -> None:
    """Revoke a fleet token."""
    if not force and not typer.confirm(f"Revoke fleet token {token_id}?"):
        raise typer.Abort()
    with _api():
        authed("POST", f"/ssh/tokens/{token_id}/revoke")
        print_success(f"Token {token_id} revoked")


# ---------------------------------------------------------------------------
# Per-host blocks
# ---------------------------------------------------------------------------
@block_app.command("create")
def block_create(
    host_id: Annotated[str, typer.Option("--host-id", help="Host ID")],
    identity_id: Annotated[str, typer.Option("--identity-id", help="Identity ID")],
    reason: Annotated[Optional[str], typer.Option("--reason", "-r", help="Reason")] = None,
    output: OutputFormat = "table",
) -> None:
    """Block an identity on a host (per-host KRL deny; certs stay valid elsewhere)."""
    with _api():
        data = authed("POST", "/ssh/blocks", json=_body(hostId=host_id, identityId=identity_id, reason=reason))
        print_success("Identity blocked on host")
        _render(data, output)


@block_app.command("unblock")
def block_unblock(
    host_id: Annotated[str, typer.Option("--host-id", help="Host ID")],
    identity_id: Annotated[str, typer.Option("--identity-id", help="Identity ID")],
    output: OutputFormat = "table",
) -> None:
    """Lift a block (enforced on the next host KRL pull)."""
    with _api():
        data = authed("POST", "/ssh/blocks/unblock", json=_body(hostId=host_id, identityId=identity_id))
        print_success("Block lifted")
        _render(data, output)


@block_app.command("fleet")
def block_fleet(output: OutputFormat = "table") -> None:
    """Fleet-wide per-host block counts + KRL distribution state."""
    with _api():
        _render(authed("GET", "/ssh/blocks/fleet"), output, columns=FLEET_COLUMNS, title="Fleet block distribution")


# ---------------------------------------------------------------------------
# SSH certificate revocation
# ---------------------------------------------------------------------------
@cert_app.command("revoke")
def ssh_cert_revoke(
    cert_id: Annotated[str, typer.Argument(help="SSH certificate ID")],
    reason: Annotated[Optional[str], typer.Option("--reason", "-r", help="Reason")] = None,
    force: Annotated[bool, typer.Option("--force", "-f", help="Skip confirmation")] = False,
    output: OutputFormat = "table",
) -> None:
    """Revoke an SSH certificate (rebuilds the CA KRL)."""
    if not force and not typer.confirm(f"Revoke SSH certificate {cert_id}?"):
        raise typer.Abort()
    with _api():
        data = authed("POST", f"/ssh/certs/{cert_id}/revoke", json=_body(reason=reason))
        print_success("SSH certificate revoked (CA KRL rebuilt)")
        _render(data, output)


# ---------------------------------------------------------------------------
# Top-level: trust material, metrics, public KRL downloads
# ---------------------------------------------------------------------------
@ssh_app.command("trust-anchors")
def trust_anchors(output: OutputFormat = "json") -> None:
    """Show SSH trust anchors (TrustedUserCAKeys / @cert-authority)."""
    with _api():
        _render(authed("GET", "/ssh/trust-anchors"), output)


@ssh_app.command("metrics")
def metrics(output: OutputFormat = "json") -> None:
    """Show SSH cert/KRL health metrics (expiring, stale KRLs, non-pulling hosts)."""
    with _api():
        _render(authed("GET", "/ssh/metrics"), output)


@ssh_app.command("trusted-user-ca-keys")
def trusted_user_ca_keys(output_file: OutFile = None) -> None:
    """Print the TrustedUserCAKeys file contents (public endpoint)."""
    with _api():
        _emit_text(public("GET", "/ssh/trusted-user-ca-keys"), output_file)


@ssh_app.command("host-ca-keys")
def host_ca_keys(output_file: OutFile = None) -> None:
    """Print the Host CA public key(s) — the KRL puller trust anchor (public endpoint)."""
    with _api():
        _emit_text(public("GET", "/ssh/host-ca-keys"), output_file)


@ssh_app.command("cert-authority")
def cert_authority(
    pattern: Annotated[str, typer.Option("--pattern", "-p", help="known_hosts host pattern")] = "*",
    output_file: OutFile = None,
) -> None:
    """Print @cert-authority known_hosts lines for the Host CA(s) (public endpoint)."""
    with _api():
        _emit_text(public("GET", "/ssh/cert-authority", params={"pattern": pattern}), output_file)


@ssh_app.command("krl")
def krl_public(
    ca_id: Annotated[str, typer.Argument(help="SSH CA ID")],
    fmt: Annotated[str, typer.Option("--format", "-f", help="bin (raw KRL bytes) or json (signed envelope)")] = "bin",
    output_file: OutFile = None,
) -> None:
    """Download a CA's public KRL (unauthenticated root endpoint)."""
    with _api():
        if fmt == "json":
            print_json(public("GET", f"/krl/{ca_id}.json"))
        else:
            data = public("GET", f"/krl/{ca_id}.bin", expect_bytes=True)
            _emit_bytes(data, output_file, f"revoked_keys-{ca_id}.krl")


@ssh_app.command("krl-host")
def krl_host(
    host_id: Annotated[str, typer.Argument(help="Host ID or FQDN")],
    fmt: Annotated[str, typer.Option("--format", "-f", help="bin or json")] = "bin",
    output_file: OutFile = None,
) -> None:
    """Download a host's composed public KRL (gated by SSH_HOST_KRL_PUBLIC on the server)."""
    with _api():
        if fmt == "json":
            print_json(public("GET", f"/krl/hosts/{host_id}.json"))
        else:
            data = public("GET", f"/krl/hosts/{host_id}.bin", expect_bytes=True)
            _emit_bytes(data, output_file, f"revoked_keys-host-{host_id}.krl")
