"""Lock in the CLI's promise: one command per documented API operation.

``openapi.json`` is the server's OpenAPI document, checked in alongside the
generated ``pki_api`` client. When the server grows an endpoint, refreshing that
file makes this test fail until a command is added and mapped here — which is
the whole point.
"""

from __future__ import annotations

import json
from pathlib import Path

import click
import pytest
import typer

from pki_cli.main import app

SPEC_PATH = Path(__file__).resolve().parent.parent / "openapi.json"
HTTP_METHODS = ("get", "post", "put", "patch", "delete", "head")

# (method, path) -> the `pki ...` command that exercises it.
OPERATION_COMMANDS: dict[tuple[str, str], str] = {
    # Dashboard / search
    ("get", "/health"): "pki health",
    ("get", "/dashboard/stats"): "pki stats",
    ("get", "/dashboard/expiring"): "pki expiring",
    ("get", "/search"): "pki search",
    # Certificate Authorities
    ("get", "/cas/"): "pki ca list",
    ("post", "/cas/"): "pki ca create",
    ("get", "/cas/{id}"): "pki ca get",
    ("delete", "/cas/{id}"): "pki ca delete",
    ("post", "/cas/{id}/revoke"): "pki ca revoke",
    ("get", "/cas/{id}/certificates"): "pki ca certs",
    ("get", "/cas/{id}/download"): "pki ca download",
    ("get", "/cas/{id}/crls"): "pki crl list",
    ("post", "/cas/{id}/crls"): "pki crl generate",
    # Certificates
    ("get", "/certificates/"): "pki cert list",
    ("post", "/certificates/"): "pki cert issue",
    ("get", "/certificates/{id}"): "pki cert get",
    ("delete", "/certificates/{id}"): "pki cert delete",
    ("get", "/certificates/{id}/download"): "pki cert download",
    ("post", "/certificates/{id}/renew"): "pki cert renew",
    ("post", "/certificates/{id}/revoke"): "pki cert revoke",
    # Bulk operations
    ("post", "/certificates/bulk/issue"): "pki cert bulk issue",
    ("post", "/certificates/bulk/renew"): "pki cert bulk renew",
    ("post", "/certificates/bulk/revoke"): "pki cert bulk revoke",
    ("delete", "/certificates/bulk/"): "pki cert bulk delete",
    ("post", "/certificates/bulk/download"): "pki cert bulk download",
    # Domains / audit / reports
    ("get", "/domains"): "pki domain list",
    ("get", "/audit"): "pki audit list",
    ("post", "/reports"): "pki report generate",
    # SSH Certificate Manager
    ("get", "/ssh/cas"): "pki ssh ca list",
    ("post", "/ssh/cas"): "pki ssh ca create",
    ("post", "/ssh/cas/import"): "pki ssh ca import",
    ("get", "/ssh/cas/{caId}"): "pki ssh ca get",
    ("post", "/ssh/cas/{caId}/revoke"): "pki ssh ca revoke",
    ("post", "/ssh/cas/{caId}/rotate"): "pki ssh ca rotate",
    ("post", "/ssh/cas/{caId}/retire"): "pki ssh ca retire",
    ("get", "/ssh/cas/{caId}/reissue-report"): "pki ssh ca reissue-report",
    ("post", "/ssh/cas/{caId}/revoke-serial"): "pki ssh ca revoke-serial",
    ("post", "/ssh/cas/{caId}/revoke-key"): "pki ssh ca revoke-key",
    ("post", "/ssh/cas/{caId}/krl"): "pki ssh ca krl-generate",
    ("get", "/ssh/cas/{caId}/krl.bin"): "pki ssh ca krl",
    ("get", "/ssh/cas/{caId}/revocations"): "pki ssh ca revocations",
    ("get", "/ssh/hosts"): "pki ssh host list",
    ("post", "/ssh/hosts"): "pki ssh host register",
    ("post", "/ssh/hosts/issue"): "pki ssh host issue",
    ("get", "/ssh/hosts/{id}"): "pki ssh host get",
    ("get", "/ssh/hosts/{id}/deploy-bundle"): "pki ssh host deploy-bundle",
    ("post", "/ssh/hosts/{id}/revoke"): "pki ssh host revoke",
    ("post", "/ssh/hosts/{id}/ecies-key"): "pki ssh host ecies-key",
    ("post", "/ssh/hosts/{id}/offboard"): "pki ssh host offboard",
    ("get", "/ssh/hosts/{id}/access"): "pki ssh host access",
    ("get", "/ssh/hosts/{id}/auth-principals"): "pki ssh host auth-principals",
    ("post", "/ssh/hosts/{id}/auth-principals/pushed"): "pki ssh host mark-pushed",
    ("get", "/ssh/hosts/{id}/blocks"): "pki ssh host blocks",
    ("get", "/ssh/hosts/{id}/principal-maps"): "pki ssh host principal-maps",
    ("get", "/ssh/identities"): "pki ssh identity list",
    ("post", "/ssh/identities"): "pki ssh identity create",
    ("post", "/ssh/identities/{id}/disable"): "pki ssh identity disable",
    ("post", "/ssh/identities/{id}/offboard"): "pki ssh identity offboard",
    ("get", "/ssh/identities/{id}/blocks"): "pki ssh identity blocks",
    ("get", "/ssh/identities/{id}/collisions"): "pki ssh identity collisions",
    ("get", "/ssh/identities/{id}/grants"): "pki ssh identity grants",
    ("post", "/ssh/users/issue"): "pki ssh user issue",
    ("get", "/ssh/users/certificates"): "pki ssh user certificates",
    ("get", "/ssh/principals"): "pki ssh principal list",
    ("post", "/ssh/principals"): "pki ssh principal create",
    ("post", "/ssh/principals/map"): "pki ssh principal map",
    ("post", "/ssh/principals/grant"): "pki ssh principal grant",
    ("post", "/ssh/principals/unmap"): "pki ssh principal unmap",
    ("post", "/ssh/principals/revoke-grant"): "pki ssh principal revoke-grant",
    ("get", "/ssh/principals/mappings"): "pki ssh principal mappings",
    ("get", "/ssh/principals/stale-hosts"): "pki ssh principal stale-hosts",
    ("delete", "/ssh/principals/{id}"): "pki ssh principal delete",
    ("get", "/ssh/tokens"): "pki ssh token list",
    ("post", "/ssh/tokens"): "pki ssh token mint",
    ("post", "/ssh/tokens/{id}/revoke"): "pki ssh token revoke",
    ("post", "/ssh/blocks"): "pki ssh block create",
    ("post", "/ssh/blocks/unblock"): "pki ssh block unblock",
    ("get", "/ssh/blocks/fleet"): "pki ssh block fleet",
    ("post", "/ssh/certs/{id}/revoke"): "pki ssh cert revoke",
    ("delete", "/ssh/certs/{id}"): "pki ssh cert purge",
    ("get", "/ssh/bulk/expiring"): "pki ssh bulk expiring",
    ("post", "/ssh/bulk/renew"): "pki ssh bulk renew",
    ("post", "/ssh/bulk/revoke"): "pki ssh bulk revoke",
    ("get", "/ssh/zones"): "pki ssh zone list",
    ("post", "/ssh/zones"): "pki ssh zone create",
    ("get", "/ssh/zones/{ref}"): "pki ssh zone get",
    ("post", "/ssh/zones/{ref}"): "pki ssh zone update",
    ("post", "/ssh/zones/{ref}/archive"): "pki ssh zone archive",
    ("post", "/ssh/zones/{ref}/unarchive"): "pki ssh zone unarchive",
    ("get", "/ssh/metrics"): "pki ssh metrics",
    ("get", "/ssh/trust-anchors"): "pki ssh trust-anchors",
    # External issuer (cluster token)
    ("get", "/external/health"): "pki external health",
    ("get", "/external/ca-bundle"): "pki external ca-bundle",
    ("post", "/external/sign"): "pki external sign",
    ("post", "/external/revoke"): "pki external revoke",
    ("get", "/external/certificate-status/{serial}"): "pki external certificate-status",
    # SCEP registration authority (SCEP integration token)
    ("get", "/external/ra/state"): "pki external ra state",
    ("post", "/external/ra/provision"): "pki external ra provision",
    ("post", "/external/ra/renew"): "pki external ra renew",
    ("post", "/external/ra/sign"): "pki external ra sign",
    ("post", "/external/ra/decrypt"): "pki external ra decrypt",
    # SSH external issuer (fleet token)
    ("post", "/external/ssh/sign-host"): "pki external ssh sign-host",
    ("post", "/external/ssh/sign-user"): "pki external ssh sign-user",
    ("post", "/external/ssh/register-host-pubkey"): "pki external ssh register-host-pubkey",
    ("post", "/external/ssh/krl"): "pki external ssh krl",
    ("get", "/external/ssh/hosts/{fqdn}/auth-principals"): "pki external ssh auth-principals",
    ("post", "/external/ssh/hosts/{fqdn}/principals-pushed"): "pki external ssh principals-pushed",
}

# Root-level routes marked `hide: true` on the server, so absent from the spec.
PUBLIC_ROUTE_COMMANDS = {
    "GET /cas/{caId}.{format}": "pki ca pem",
    "GET /crl/{caId}.{format}": "pki crl download",
    "GET /krl/{caId}.bin": "pki ssh krl",
    "GET /krl/hosts/{hostId}.bin": "pki ssh krl-host",
    "GET /ssh/cas/{id}/ca.pub": "pki ssh ca pub",
    "GET /ssh/cert-authority": "pki ssh cert-authority",
    "GET /ssh/host-ca-keys": "pki ssh host-ca-keys",
    "GET /ssh/hosts/{id}/cert.pub": "pki ssh host cert",
    "GET /ssh/hosts/{id}/sshd-config": "pki ssh host sshd-config",
    "GET /ssh/trusted-user-ca-keys": "pki ssh trusted-user-ca-keys",
}

# Commands that exist for the CLI's own sake, not for an API operation.
LOCAL_COMMANDS = {"pki config", "pki login", "pki logout"}


def _spec_operations() -> set[tuple[str, str]]:
    spec = json.loads(SPEC_PATH.read_text())
    return {
        (method, path)
        for path, item in spec["paths"].items()
        for method in item
        if method in HTTP_METHODS
    }


def _cli_commands() -> set[str]:
    def walk(cmd: click.Command, prefix: str = "pki"):
        if isinstance(cmd, click.Group):
            for name, sub in cmd.commands.items():
                yield from walk(sub, f"{prefix} {name}")
        else:
            yield prefix

    return set(walk(typer.main.get_command(app)))


def test_every_documented_operation_has_a_command():
    uncovered = sorted(_spec_operations() - set(OPERATION_COMMANDS))
    assert not uncovered, (
        "The OpenAPI document has operations with no CLI command:\n  "
        + "\n  ".join(f"{m.upper()} {p}" for m, p in uncovered)
    )


def test_no_stale_operation_mappings():
    stale = sorted(set(OPERATION_COMMANDS) - _spec_operations())
    assert not stale, (
        "These mappings point at operations the server no longer documents:\n  "
        + "\n  ".join(f"{m.upper()} {p}" for m, p in stale)
    )


@pytest.mark.parametrize(
    "command",
    sorted(set(OPERATION_COMMANDS.values()) | set(PUBLIC_ROUTE_COMMANDS.values())),
)
def test_mapped_command_exists(command: str):
    assert command in _cli_commands(), f"{command!r} is mapped but not registered"


def test_no_unmapped_commands():
    """Every registered command is accounted for — no orphans, no surprises."""
    mapped = set(OPERATION_COMMANDS.values()) | set(PUBLIC_ROUTE_COMMANDS.values()) | LOCAL_COMMANDS
    orphans = sorted(_cli_commands() - mapped)
    assert not orphans, (
        "These commands are not mapped to an endpoint — add them to "
        f"OPERATION_COMMANDS or PUBLIC_ROUTE_COMMANDS:\n  {orphans}"
    )
