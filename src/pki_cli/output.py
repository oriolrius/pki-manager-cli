"""Output formatting for PKI CLI."""

import json
from datetime import datetime
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# Status lines go to stderr so `-o json` output stays pipeable into jq.
err_console = Console(stderr=True)


def format_date(dt: datetime | str | None) -> str:
    """Format a datetime for display."""
    if dt is None:
        return "-"
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
    return dt.strftime("%Y-%m-%d %H:%M")


def format_status(status: str) -> str:
    """Format status with color."""
    colors = {
        "active": "[green]active[/green]",
        "revoked": "[red]revoked[/red]",
        "expired": "[yellow]expired[/yellow]",
    }
    return colors.get(status.lower(), status)


def extract_cn(subject: str) -> str:
    """Extract Common Name from subject DN."""
    for part in subject.split(","):
        part = part.strip()
        if part.startswith("CN="):
            return part[3:]
    return subject[:40]


def print_json(data: Any) -> None:
    """Print data as formatted JSON."""
    console.print_json(json.dumps(data, default=str, indent=2))


def print_ca_table(cas: list[dict]) -> None:
    """Print CAs as a table."""
    table = Table(title="Certificate Authorities")
    table.add_column("ID", style="dim", max_width=36)
    table.add_column("Common Name", style="cyan")
    table.add_column("Algorithm", style="magenta")
    table.add_column("Status")
    table.add_column("Certs", justify="right")
    table.add_column("Expires", style="yellow")

    for ca in cas:
        count = ca.get("certificateCount", ca.get("issuedCertificateCount"))
        table.add_row(
            ca.get("id", "-"),
            extract_cn(subject_of(ca)),
            ca.get("keyAlgorithm", "-"),
            format_status(ca.get("status", "-")),
            str(count) if count is not None else "-",
            format_date(ca.get("notAfter")),
        )

    console.print(table)


def subject_of(entity: dict) -> str:
    """Return an entity's subject DN.

    List endpoints return a flat ``subject`` string; detail endpoints return
    ``subjectDn`` plus a structured ``subject`` object. Accept either.
    """
    subject = entity.get("subjectDn") or entity.get("subject")
    if isinstance(subject, dict):
        parts = [
            f"CN={subject['commonName']}" if subject.get("commonName") else None,
            f"OU={subject['organizationalUnit']}" if subject.get("organizationalUnit") else None,
            f"O={subject['organization']}" if subject.get("organization") else None,
            f"L={subject['locality']}" if subject.get("locality") else None,
            f"ST={subject['state']}" if subject.get("state") else None,
            f"C={subject['country']}" if subject.get("country") else None,
        ]
        return ",".join(p for p in parts if p) or "-"
    return subject or "-"


def _sans(entity: dict) -> str:
    """Join every SAN type into one display string."""
    values: list[str] = []
    for key in ("sanDns", "sanIp", "sanEmail"):
        values.extend(entity.get(key) or [])
    return ", ".join(values) if values else "-"


def print_ca_detail(ca: dict) -> None:
    """Print CA details."""
    table = Table(show_header=False, box=None)
    table.add_column("Field", style="bold cyan")
    table.add_column("Value", overflow="fold")

    table.add_row("ID", ca.get("id", "-"))
    table.add_row("Subject", subject_of(ca))
    if ca.get("issuerDn") and ca.get("issuerDn") != subject_of(ca):
        table.add_row("Issuer", ca["issuerDn"])
    table.add_row("Serial Number", ca.get("serialNumber", "-"))
    table.add_row("Key Algorithm", ca.get("keyAlgorithm", "-"))
    table.add_row("Status", format_status(ca.get("status", "-")))
    if ca.get("validityStatus"):
        table.add_row("Validity", ca["validityStatus"])
    table.add_row("Valid From", format_date(ca.get("notBefore")))
    table.add_row("Valid Until", format_date(ca.get("notAfter")))
    # Detail responses call this issuedCertificateCount; list items certificateCount.
    count = ca.get("issuedCertificateCount", ca.get("certificateCount"))
    table.add_row("Certificates", str(count) if count is not None else "-")
    fingerprints = ca.get("fingerprints") or {}
    if fingerprints.get("sha256"):
        table.add_row("SHA-256", fingerprints["sha256"])
    if ca.get("revocationDate"):
        table.add_row("Revoked At", format_date(ca["revocationDate"]))
        table.add_row("Revocation Reason", ca.get("revocationReason") or "-")
    table.add_row("Created", format_date(ca.get("createdAt")))

    console.print(Panel(table, title="Certificate Authority", border_style="blue"))


def print_cert_table(certs: list[dict]) -> None:
    """Print certificates as a table."""
    table = Table(title="Certificates")
    table.add_column("ID", style="dim", max_width=36)
    table.add_column("Common Name", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Status")
    table.add_column("Expires", style="yellow")

    for cert in certs:
        table.add_row(
            cert.get("id", "-"),
            extract_cn(subject_of(cert)),
            cert.get("certificateType", cert.get("type", "-")),
            format_status(cert.get("expiryStatus") or cert.get("status", "-")),
            format_date(cert.get("notAfter")),
        )

    console.print(table)


def print_cert_detail(cert: dict) -> None:
    """Print certificate details."""
    table = Table(show_header=False, box=None)
    table.add_column("Field", style="bold cyan")
    table.add_column("Value", overflow="fold")

    table.add_row("ID", cert.get("id", "-"))
    table.add_row("CA ID", cert.get("caId", "-"))
    table.add_row("Type", cert.get("certificateType", cert.get("type", "-")))
    table.add_row("Subject", subject_of(cert))
    if cert.get("issuerDn"):
        table.add_row("Issuer", cert["issuerDn"])
    table.add_row("SANs", _sans(cert))
    table.add_row("Serial Number", cert.get("serialNumber", "-"))
    table.add_row("Status", format_status(cert.get("status", "-")))
    if cert.get("validityStatus"):
        table.add_row("Validity", cert["validityStatus"])
    table.add_row("Valid From", format_date(cert.get("notBefore")))
    table.add_row("Valid Until", format_date(cert.get("notAfter")))
    if cert.get("remainingDays") is not None:
        days = cert["remainingDays"]
        style = "red" if days <= 7 else "yellow" if days <= 30 else "green"
        table.add_row("Days Remaining", f"[{style}]{days}[/{style}]")
    if cert.get("extendedKeyUsage"):
        table.add_row("Extended Key Usage", ", ".join(cert["extendedKeyUsage"]))
    fingerprints = cert.get("fingerprints") or {}
    if fingerprints.get("sha256"):
        table.add_row("SHA-256", fingerprints["sha256"])
    if cert.get("renewedFromId"):
        table.add_row("Renewed From", cert["renewedFromId"])
    if cert.get("renewedTo"):
        table.add_row("Renewed To", ", ".join(str(v) for v in cert["renewedTo"]))
    table.add_row("Created", format_date(cert.get("createdAt")))

    # Detail responses use revocationDate; some list shapes use revokedAt.
    revoked_at = cert.get("revocationDate") or cert.get("revokedAt")
    if revoked_at:
        table.add_row("Revoked At", format_date(revoked_at))
        table.add_row("Revocation Reason", cert.get("revocationReason") or "-")

    console.print(Panel(table, title="Certificate", border_style="green"))


# The API returns "totalCAs"/"activeCAs" (capitalised acronym); the other keys
# are only present on deployments that compute them, so they render as blank.
_STAT_LABELS = [
    ("totalCAs", "Total CAs", None),
    ("activeCAs", "Active CAs", None),
    ("totalCertificates", "Total Certificates", None),
    ("activeCertificates", "Active Certificates", None),
    ("revokedCertificates", "Revoked Certificates", None),
    ("expiredCertificates", "Expired Certificates", None),
    ("expiringSoon", "Expiring Soon", "yellow"),
]


def print_stats(stats: dict) -> None:
    """Print dashboard statistics."""
    table = Table(title="PKI Dashboard Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right", style="bold")

    for key, label, colour in _STAT_LABELS:
        if key not in stats:
            continue
        value = str(stats[key])
        table.add_row(label, f"[{colour}]{value}[/{colour}]" if colour else value)

    # Surface anything the server added that this CLI doesn't know about yet.
    for key, value in stats.items():
        if key not in {k for k, _, _ in _STAT_LABELS}:
            table.add_row(key, _scalar(value))

    console.print(table)


def print_expiring(items: list[dict]) -> None:
    """Print expiring items."""
    table = Table(title="Expiring Certificates")
    table.add_column("ID", style="dim", max_width=36)
    table.add_column("Type", style="magenta")
    table.add_column("Common Name", style="cyan")
    table.add_column("Expires", style="yellow")
    table.add_column("Days Left", justify="right")

    for item in items:
        days = item.get("daysRemaining", 0)
        days_style = "red" if days <= 7 else "yellow" if days <= 30 else "green"
        table.add_row(
            item.get("id", "-"),
            item.get("type", "-"),
            item.get("cn", "-"),
            format_date(item.get("notAfter")),
            f"[{days_style}]{days}[/{days_style}]",
        )

    console.print(table)


def print_search_results(data: dict) -> None:
    """Print search results."""
    results = data.get("results", {})
    cas = results.get("cas", [])
    certs = results.get("certificates", [])
    domains = results.get("domains", [])

    total = len(cas) + len(certs) + len(domains)
    if total == 0:
        console.print("[dim]No results found[/dim]")
        return

    if cas:
        table = Table(title="Certificate Authorities")
        table.add_column("ID", style="dim", max_width=36)
        table.add_column("Title", style="cyan")
        table.add_column("Subtitle", style="dim")
        table.add_column("Status")

        for item in cas:
            table.add_row(
                item.get("id", "-"),
                item.get("title", "-"),
                item.get("subtitle", "-"),
                format_status(item.get("status", "-")),
            )
        console.print(table)

    if certs:
        table = Table(title="Certificates")
        table.add_column("ID", style="dim", max_width=36)
        table.add_column("Title", style="cyan")
        table.add_column("Subtitle", style="dim")
        table.add_column("Status")

        for item in certs:
            table.add_row(
                item.get("id", "-"),
                item.get("title", "-"),
                item.get("subtitle", "-"),
                format_status(item.get("status", "-")),
            )
        console.print(table)

    if domains:
        table = Table(title="Domains")
        table.add_column("Domain", style="cyan")
        table.add_column("Certificate ID", style="dim", max_width=36)

        for item in domains:
            table.add_row(
                item.get("domain", "-"),
                item.get("certificateId", "-"),
            )
        console.print(table)


def _scalar(value: Any) -> str:
    """Render any value as a single table cell."""
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return json.dumps(value, default=str, ensure_ascii=False)
    return str(value)


def print_records(items: Any, columns: list[str] | None = None, title: str | None = None) -> None:
    """Render a list of dicts as a table, inferring columns when not given.

    Deliberately schema-agnostic: the SSH/external responses are not typed, so
    this tolerates arbitrary shapes and never raises on a missing key.
    """
    items = list(items or [])
    if not items:
        console.print("[dim]No results[/dim]")
        return

    if columns is None:
        columns = []
        for item in items:
            if isinstance(item, dict):
                for key in item:
                    if key not in columns:
                        columns.append(key)
    if not columns:  # list of scalars
        table = Table(title=title)
        table.add_column("Value")
        for item in items:
            table.add_row(_scalar(item))
        console.print(table)
        return

    table = Table(title=title)
    for col in columns:
        table.add_column(col, overflow="ellipsis", max_width=44)
    for item in items:
        if isinstance(item, dict):
            table.add_row(*[_scalar(item.get(col)) for col in columns])
        else:
            table.add_row(_scalar(item), *[""] * (len(columns) - 1))
    console.print(table)


def print_kv(obj: Any, title: str | None = None) -> None:
    """Render a single object as a key/value panel (falls back to JSON)."""
    if not isinstance(obj, dict):
        print_json(obj)
        return
    table = Table(show_header=False, box=None)
    table.add_column("Field", style="bold cyan")
    table.add_column("Value", overflow="fold")
    for key, value in obj.items():
        table.add_row(key, _scalar(value))
    console.print(Panel(table, title=title, border_style="blue") if title else table)


def print_success(message: str) -> None:
    """Print a success message (to stderr, so JSON output stays pipeable)."""
    err_console.print(f"[green]✓[/green] {message}")


def print_error(message: str) -> None:
    """Print an error message (to stderr)."""
    err_console.print(f"[red]✗[/red] {message}", style="red")


def print_warning(message: str) -> None:
    """Print a warning message (to stderr)."""
    err_console.print(f"[yellow]⚠[/yellow] {message}", style="yellow")


def print_note(message: str) -> None:
    """Print a dim informational note (to stderr)."""
    err_console.print(f"[dim]{message}[/dim]")
