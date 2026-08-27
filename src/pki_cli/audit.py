"""`pki audit`, `pki report` and `pki domain` — the audit/reporting surface.

Wraps three REST groups that had no CLI equivalent:

* ``GET  /audit``   — the tamper-evident operation log, with filters
* ``POST /reports`` — CSV report generation (inventory / revocation / CA ops)
* ``GET  /domains`` — the domain inventory aggregated from certificate SANs
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Optional
from uuid import UUID

import typer
from rich.console import Console

from pki_api.pki_manager_rest_api_client.api.audit import get_audit, post_reports
from pki_api.pki_manager_rest_api_client.api.domains import get_domains
from pki_api.pki_manager_rest_api_client.models import (
    GetAuditStatus,
    PostReportsBody,
    PostReportsBodyFormat,
    PostReportsBodyReportType,
)
from pki_api.pki_manager_rest_api_client.types import UNSET

from .client import get_client
from .http import ApiError, unwrap
from .output import print_error, print_json, print_kv, print_records, print_success

console = Console()

audit_app = typer.Typer(help="Audit log", no_args_is_help=True)
report_app = typer.Typer(help="Compliance reports (CSV)", no_args_is_help=True)
domain_app = typer.Typer(help="Domain inventory", no_args_is_help=True)

OutputFormat = Annotated[str, typer.Option("--output", "-o", help="Output format: table, json")]

AUDIT_COLUMNS = ["timestamp", "operation", "entityType", "entityId", "status", "ipAddress"]
DOMAIN_COLUMNS = [
    "domain",
    "isWildcard",
    "certificateCount",
    "activeCertificateCount",
    "revokedCertificateCount",
    "caCount",
    "lastCertificateDate",
]


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


def _epoch(value: Optional[str], flag: str) -> int | object:
    """Parse ``--start/--end`` as a Unix timestamp or an ISO-8601 date."""
    if not value:
        return UNSET
    if value.isdigit():
        return int(value)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        print_error(f"{flag} must be a Unix timestamp or an ISO-8601 date (got {value!r})")
        raise typer.Exit(1)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return int(parsed.timestamp())


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------
@audit_app.command("list")
def audit_list(
    operation: Annotated[Optional[str], typer.Option("--operation", help="Filter by operation, e.g. ca.create")] = None,
    entity_type: Annotated[Optional[str], typer.Option("--entity-type", help="Filter by entity type: ca, certificate, audit, report")] = None,
    entity_id: Annotated[Optional[str], typer.Option("--entity-id", help="Filter by a specific entity ID")] = None,
    status: Annotated[Optional[str], typer.Option("--status", "-s", help="Filter by status: success, failure")] = None,
    start: Annotated[Optional[str], typer.Option("--start", help="Start date (Unix timestamp or ISO-8601)")] = None,
    end: Annotated[Optional[str], typer.Option("--end", help="End date (Unix timestamp or ISO-8601)")] = None,
    limit: Annotated[int, typer.Option("--limit", "-l", help="Max results (1-200)")] = 100,
    offset: Annotated[int, typer.Option("--offset", help="Number of entries to skip")] = 0,
    output: OutputFormat = "table",
) -> None:
    """List audit log entries."""
    with _api():
        result = unwrap(
            get_audit.sync(
                client=get_client(),
                operation=operation or UNSET,
                entity_type=entity_type or UNSET,
                entity_id=entity_id or UNSET,
                status=GetAuditStatus(status) if status else UNSET,
                start_date=_epoch(start, "--start"),
                end_date=_epoch(end, "--end"),
                limit=limit,
                offset=offset,
            ),
            what="Audit log query",
        )
        data = result.to_dict()
        if output == "json":
            print_json(data)
            return
        print_records(data.get("items", []), columns=AUDIT_COLUMNS, title="Audit Log")
        total = data.get("totalCount")
        if total is not None:
            console.print(f"[dim]{len(data.get('items', []))} of {total} entries[/dim]")


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------
@report_app.command("generate")
def report_generate(
    report_type: Annotated[str, typer.Option("--type", "-t", help="certificate_inventory, revocation, or ca_operations")],
    fmt: Annotated[str, typer.Option("--format", "-f", help="Report format: csv (pdf is not implemented server-side)")] = "csv",
    ca_id: Annotated[Optional[str], typer.Option("--ca", help="Restrict the report to one CA")] = None,
    start: Annotated[Optional[str], typer.Option("--start", help="Start date (Unix timestamp or ISO-8601)")] = None,
    end: Annotated[Optional[str], typer.Option("--end", help="End date (Unix timestamp or ISO-8601)")] = None,
    output_file: Annotated[Optional[Path], typer.Option("--output-file", help="Write the report body to a file")] = None,
    output: OutputFormat = "table",
) -> None:
    """Generate a compliance report."""
    with _api():
        body = PostReportsBody(
            report_type=PostReportsBodyReportType(report_type),
            format_=PostReportsBodyFormat(fmt),
            ca_id=UUID(ca_id) if ca_id else UNSET,
            start_date=_epoch(start, "--start"),
            end_date=_epoch(end, "--end"),
        )
        result = unwrap(post_reports.sync(client=get_client(), body=body), what="Report generation")
        data = result.to_dict()

        if output_file:
            Path(output_file).write_text(data.get("content", ""))
            print_success(f"Report written to {output_file}")
            summary = {k: v for k, v in data.items() if k != "content"}
            print_kv(summary, title=data.get("reportName", "Report"))
            return

        if output == "json":
            print_json(data)
            return

        print_kv({k: v for k, v in data.items() if k != "content"}, title=data.get("reportName", "Report"))
        if data.get("content"):
            console.print(data["content"])


# ---------------------------------------------------------------------------
# Domains
# ---------------------------------------------------------------------------
@domain_app.command("list")
def domain_list(
    search: Annotated[Optional[str], typer.Option("--search", "-q", help="Filter domains by name")] = None,
    ca_id: Annotated[Optional[str], typer.Option("--ca", help="Filter by issuing CA")] = None,
    limit: Annotated[int, typer.Option("--limit", "-l", help="Max results (1-200)")] = 50,
    offset: Annotated[int, typer.Option("--offset", help="Number of domains to skip")] = 0,
    output: OutputFormat = "table",
) -> None:
    """List domains seen across issued certificates."""
    with _api():
        result = unwrap(
            get_domains.sync(
                client=get_client(),
                search=search or UNSET,
                ca_id=UUID(ca_id) if ca_id else UNSET,
                limit=limit,
                offset=offset,
            ),
            what="Domain listing",
        )
        data = result.to_dict()
        if output == "json":
            print_json(data)
            return
        print_records(data.get("items", []), columns=DOMAIN_COLUMNS, title="Domains")
        total = (data.get("pagination") or {}).get("total")
        if total is not None:
            console.print(f"[dim]{len(data.get('items', []))} of {total} domains[/dim]")
