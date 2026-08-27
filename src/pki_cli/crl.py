"""`pki crl` — Certificate Revocation List management and distribution.

Covers the two authenticated CA-scoped CRL routes (``GET``/``POST
/cas/{id}/crls``) plus the unauthenticated CDP download served at the server
root (``/crl/{caId}.crl`` and ``.der``), which relying parties fetch directly.
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Annotated, Optional
from uuid import UUID

import typer
from rich.console import Console

from pki_api.pki_manager_rest_api_client.api.certificate_authorities import (
    get_cas_id_crls,
    post_cas_id_crls,
)
from pki_api.pki_manager_rest_api_client.models import PostCasIdCrlsBody

from .client import get_client
from .http import ApiError, public, unwrap
from .output import print_error, print_json, print_kv, print_records, print_success

console = Console()

crl_app = typer.Typer(help="Certificate Revocation Lists", no_args_is_help=True)

OutputFormat = Annotated[str, typer.Option("--output", "-o", help="Output format: table, json")]

CRL_COLUMNS = ["id", "crlNumber", "thisUpdate", "nextUpdate", "validityStatus", "revokedCount"]


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


@crl_app.command("list")
def crl_list(
    ca_id: Annotated[str, typer.Argument(help="CA ID (UUID)")],
    limit: Annotated[int, typer.Option("--limit", "-l", help="Max results (1-100)")] = 50,
    offset: Annotated[int, typer.Option("--offset", help="Number of CRLs to skip")] = 0,
    output: OutputFormat = "table",
) -> None:
    """List the CRLs a CA has published."""
    with _api():
        result = unwrap(
            get_cas_id_crls.sync(UUID(ca_id), client=get_client(), limit=limit, offset=offset),
            what="CRL listing",
        )
        data = result.to_dict()
        if output == "json":
            print_json(data)
            return
        print_records(data.get("items", []), columns=CRL_COLUMNS, title=f"CRLs for CA {ca_id}")
        total = (data.get("pagination") or {}).get("total")
        if total is not None:
            console.print(f"[dim]{len(data.get('items', []))} of {total} CRLs[/dim]")


@crl_app.command("generate")
def crl_generate(
    ca_id: Annotated[str, typer.Argument(help="CA ID (UUID)")],
    next_update_days: Annotated[int, typer.Option("--next-update-days", "-n", help="Days until the new CRL expires (1-365)")] = 7,
    output: OutputFormat = "table",
) -> None:
    """Generate a new CRL for a CA."""
    with _api():
        body = PostCasIdCrlsBody(next_update_days=next_update_days)
        result = unwrap(
            post_cas_id_crls.sync(UUID(ca_id), client=get_client(), body=body),
            what="CRL generation",
        )
        data = result.to_dict()
        print_success(f"CRL #{data.get('crlNumber', '?')} generated")
        print_json(data) if output == "json" else print_kv(data, title="CRL")


@crl_app.command("download")
def crl_download(
    ca_id: Annotated[str, typer.Argument(help="CA ID (UUID)")],
    fmt: Annotated[str, typer.Option("--format", "-f", help="crl (PEM) or der (binary)")] = "crl",
    output_file: Annotated[Optional[Path], typer.Option("--output-file", "-o", help="Destination file")] = None,
) -> None:
    """Download a CA's current CRL from its public distribution point."""
    if fmt not in ("crl", "der", "pem"):
        print_error("--format must be 'crl' (PEM) or 'der'")
        raise typer.Exit(1)
    suffix = "crl" if fmt == "pem" else fmt

    with _api():
        data = public("GET", f"/crl/{ca_id}.{suffix}", expect_bytes=True)
        path = Path(output_file) if output_file else Path(f"{ca_id}.{suffix}")
        path.write_bytes(data)
        print_success(f"Saved {len(data)} bytes to {path}")
