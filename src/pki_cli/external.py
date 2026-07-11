"""`pki external` — machine-facing issuer endpoints.

Two token-authenticated surfaces the CLI can drive for automation/testing:

* ``/api/v1/external/*``      — the cert-manager issuer API, authenticated with a
  **cluster token** (``pkimg_...``, one token per CA). Set via ``--token`` or
  ``PKI_CLUSTER_TOKEN``.
* ``/api/v1/external/ssh/*``  — the SSH fleet automation API, authenticated with a
  **fleet token** (minted via ``pki ssh token mint``). Set via ``--token`` or
  ``PKI_FLEET_TOKEN``. The ECIES ``krl`` endpoint takes no token.

These bypass the OIDC login the rest of the CLI uses — they carry their own
bearer token — so they go through :func:`pki_cli.http.token_call`.
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

from .http import ApiError, read_value_or_file, token_call
from .output import print_error, print_json, print_kv, print_records, print_success

console = Console()

external_app = typer.Typer(
    name="external",
    help="Machine-facing issuer API (cluster-token X.509 + fleet-token SSH)",
    no_args_is_help=True,
)
ssh_ext_app = typer.Typer(help="Fleet-token SSH automation (sign-host, sign-user, KRL)", no_args_is_help=True)
external_app.add_typer(ssh_ext_app, name="ssh")

OutputFormat = Annotated[str, typer.Option("--output", "-o", help="Output format: table, json")]

CLUSTER_TOKEN = Annotated[
    Optional[str],
    typer.Option("--token", envvar="PKI_CLUSTER_TOKEN", help="Cluster bearer token (pkimg_...)"),
]
FLEET_TOKEN = Annotated[
    Optional[str],
    typer.Option("--token", envvar="PKI_FLEET_TOKEN", help="Fleet bearer token"),
]


@contextmanager
def _api():
    try:
        yield
    except typer.Exit:
        raise
    except ApiError as exc:
        print_error(str(exc))
        raise typer.Exit(1)
    except Exception as exc:  # noqa: BLE001
        print_error(str(exc))
        raise typer.Exit(1)


def _body(**kwargs) -> dict:
    return {k: v for k, v in kwargs.items() if v is not None}


def _render(data, output: str, *, title: str | None = None) -> None:
    if output == "json":
        print_json(data)
    elif isinstance(data, list):
        print_records(data, title=title)
    elif isinstance(data, dict):
        print_kv(data, title=title)
    else:
        console.print(str(data))


def _require(token: Optional[str], env_name: str) -> str:
    if not token:
        print_error(f"A bearer token is required — pass --token or set {env_name}")
        raise typer.Exit(1)
    return token


# ---------------------------------------------------------------------------
# Cluster-token X.509 issuer API (/api/v1/external)
# ---------------------------------------------------------------------------
@external_app.command("health")
def health(token: CLUSTER_TOKEN = None, output: OutputFormat = "json") -> None:
    """Liveness check + cluster identity for a cluster token."""
    with _api():
        _render(token_call("GET", "/external/health", _require(token, "PKI_CLUSTER_TOKEN")), output)


@external_app.command("ca-bundle")
def ca_bundle(
    token: CLUSTER_TOKEN = None,
    output_file: Annotated[Optional[Path], typer.Option("--output-file", help="Write the PEM chain to a file")] = None,
    output: OutputFormat = "json",
) -> None:
    """Fetch the PEM chain of the cluster's CA."""
    with _api():
        data = token_call("GET", "/external/ca-bundle", _require(token, "PKI_CLUSTER_TOKEN"))
        if output_file and isinstance(data, dict) and data.get("chainPem"):
            Path(output_file).write_text(data["chainPem"])
            print_success(f"CA chain written to {output_file}")
        else:
            _render(data, output)


@external_app.command("sign")
def sign(
    csr: Annotated[str, typer.Option("--csr", help="CSR in PEM (or @file)")],
    request_uid: Annotated[str, typer.Option("--request-uid", help="Idempotency key for this signing request")],
    token: CLUSTER_TOKEN = None,
    duration_days: Annotated[Optional[int], typer.Option("--duration-days", help="Certificate lifetime in days (1-825)")] = None,
    cert_type: Annotated[Optional[str], typer.Option("--type", "-t", help="server, client, or dual")] = None,
    k8s_namespace: Annotated[Optional[str], typer.Option("--k8s-namespace", help="k8s namespace (recorded)")] = None,
    k8s_resource: Annotated[Optional[str], typer.Option("--k8s-resource", help="k8s resource (recorded)")] = None,
    dns: Annotated[Optional[list[str]], typer.Option("--dns", "-d", help="DNS SAN (repeatable; usually taken from the CSR)")] = None,
    ip: Annotated[Optional[list[str]], typer.Option("--ip", help="IP SAN (repeatable)")] = None,
    output: OutputFormat = "json",
) -> None:
    """Sign a CSR with the cluster's CA (returns cert + chain)."""
    with _api():
        body = _body(
            csrPem=read_value_or_file(csr),
            requestUid=request_uid,
            durationDays=duration_days,
            certificateType=cert_type,
            k8sNamespace=k8s_namespace,
            k8sResource=k8s_resource,
            sanDns=dns,
            sanIp=ip,
        )
        data = token_call("POST", "/external/sign", _require(token, "PKI_CLUSTER_TOKEN"), json=body)
        print_success("CSR signed")
        _render(data, output)


@external_app.command("revoke")
def revoke(
    serial: Annotated[str, typer.Option("--serial", help="Serial number of the certificate to revoke")],
    token: CLUSTER_TOKEN = None,
    reason: Annotated[Optional[str], typer.Option("--reason", "-r", help="Revocation reason")] = None,
    output: OutputFormat = "json",
) -> None:
    """Revoke a certificate (by serial) that this cluster issued."""
    with _api():
        body = _body(serialNumber=serial, reason=reason)
        data = token_call("POST", "/external/revoke", _require(token, "PKI_CLUSTER_TOKEN"), json=body)
        print_success("Certificate revoked")
        _render(data, output)


# ---------------------------------------------------------------------------
# Fleet-token SSH automation API (/api/v1/external/ssh)
# ---------------------------------------------------------------------------
@ssh_ext_app.command("sign-host")
def sign_host(
    fqdn: Annotated[str, typer.Option("--fqdn", help="Host FQDN")],
    pubkey: Annotated[str, typer.Option("--pubkey", "-k", help="OpenSSH host public key (or @file)")],
    token: FLEET_TOKEN = None,
    address: Annotated[Optional[list[str]], typer.Option("--address", "-a", help="Host address (repeatable)")] = None,
    valid_for_seconds: Annotated[Optional[int], typer.Option("--valid-for-seconds", "--ttl", help="Validity in seconds")] = None,
    key_id: Annotated[Optional[str], typer.Option("--key-id", help="Certificate key_id")] = None,
    idempotency_key: Annotated[Optional[str], typer.Option("--idempotency-key", help="Idempotency-Key header")] = None,
    output: OutputFormat = "json",
) -> None:
    """Register (upsert) a host and issue its host certificate."""
    with _api():
        body = _body(
            fqdn=fqdn,
            addresses=address,
            opensshHostPubkey=read_value_or_file(pubkey),
            validForSeconds=valid_for_seconds,
            keyId=key_id,
        )
        data = token_call(
            "POST",
            "/external/ssh/sign-host",
            _require(token, "PKI_FLEET_TOKEN"),
            json=body,
            headers={"Idempotency-Key": idempotency_key},
        )
        print_success("Host certificate signed")
        _render(data, output)


@ssh_ext_app.command("sign-user")
def sign_user(
    subject: Annotated[str, typer.Option("--subject", "-s", help="Identity subject")],
    pubkey: Annotated[str, typer.Option("--pubkey", "-k", help="User's SSH public key (or @file)")],
    token: FLEET_TOKEN = None,
    principal: Annotated[Optional[list[str]], typer.Option("--principal", "-p", help="Principal/role (repeatable, at least one)")] = None,
    extension: Annotated[Optional[list[str]], typer.Option("--extension", "-e", help="SSH extension (repeatable)")] = None,
    force_command: Annotated[Optional[str], typer.Option("--force-command", help="force-command restriction")] = None,
    source_address: Annotated[Optional[str], typer.Option("--source-address", help="source-address CIDR list")] = None,
    valid_for_seconds: Annotated[Optional[int], typer.Option("--valid-for-seconds", "--ttl", help="Validity in seconds")] = None,
    key_id: Annotated[Optional[str], typer.Option("--key-id", help="Certificate key_id")] = None,
    idempotency_key: Annotated[Optional[str], typer.Option("--idempotency-key", help="Idempotency-Key header")] = None,
    output: OutputFormat = "json",
) -> None:
    """Ensure an identity exists and issue a user certificate."""
    if not principal:
        print_error("At least one --principal (role) is required")
        raise typer.Exit(1)
    with _api():
        body = _body(
            subject=subject,
            sshPublicKey=read_value_or_file(pubkey),
            principals=principal,
            extensions=extension,
            forceCommand=force_command,
            sourceAddress=source_address,
            validForSeconds=valid_for_seconds,
            keyId=key_id,
        )
        data = token_call(
            "POST",
            "/external/ssh/sign-user",
            _require(token, "PKI_FLEET_TOKEN"),
            json=body,
            headers={"Idempotency-Key": idempotency_key},
        )
        print_success("User certificate signed")
        _render(data, output)


@ssh_ext_app.command("register-host-pubkey")
def register_host_pubkey(
    fqdn: Annotated[str, typer.Option("--fqdn", help="Host FQDN")],
    token: FLEET_TOKEN = None,
    output: OutputFormat = "json",
) -> None:
    """Confirm a host is eligible for encrypted (ECIES) KRL distribution."""
    with _api():
        data = token_call(
            "POST",
            "/external/ssh/register-host-pubkey",
            _require(token, "PKI_FLEET_TOKEN"),
            json=_body(fqdn=fqdn),
        )
        _render(data, output)


@ssh_ext_app.command("auth-principals")
def ext_auth_principals(
    fqdn: Annotated[str, typer.Argument(help="Host FQDN")],
    token: FLEET_TOKEN = None,
    output: OutputFormat = "json",
) -> None:
    """Fetch a host's rendered AuthorizedPrincipalsFile map (host self-serve)."""
    with _api():
        _render(token_call("GET", f"/external/ssh/hosts/{fqdn}/auth-principals", _require(token, "PKI_FLEET_TOKEN")), output)


@ssh_ext_app.command("krl")
def ext_krl(
    host_id: Annotated[str, typer.Option("--host-id", help="Host FQDN whose encrypted KRL to fetch")],
    output_file: Annotated[Optional[Path], typer.Option("--output", "-o", help="Output file for the ECIES ciphertext")] = None,
) -> None:
    """Fetch a host's ECIES-encrypted KRL envelope (no token; only the host can decrypt)."""
    with _api():
        data = token_call("POST", "/external/ssh/krl", None, json={"host_id": host_id}, expect_bytes=True)
        path = Path(output_file) if output_file else Path(f"krl-{host_id}.enc")
        path.write_bytes(data)
        print_success(f"Saved {len(data)} bytes to {path}")
