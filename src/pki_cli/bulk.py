"""`pki cert bulk` — the Bulk Operations REST group.

Five endpoints that act on up to 100 certificates in one call:
issue (from CSV), renew, revoke, delete and download (as a ZIP).

Certificate IDs are accepted as repeatable ``--id`` flags, as a comma-separated
list, or via ``--ids-file`` (one ID per line) so the commands compose with
``pki cert list -o json | jq -r '.items[].id'``.
"""

from __future__ import annotations

import base64
from contextlib import contextmanager
from pathlib import Path
from typing import Annotated, Optional
from uuid import UUID

import typer
from rich.console import Console

from pki_api.pki_manager_rest_api_client.api.bulk_operations import (
    delete_certificates_bulk,
    post_certificates_bulk_download,
    post_certificates_bulk_issue,
    post_certificates_bulk_renew,
    post_certificates_bulk_revoke,
)
from pki_api.pki_manager_rest_api_client.models import (
    DeleteCertificatesBulkBody,
    PostCertificatesBulkDownloadBody,
    PostCertificatesBulkDownloadBodyFormat,
    PostCertificatesBulkIssueBody,
    PostCertificatesBulkRenewBody,
    PostCertificatesBulkRevokeBody,
    PostCertificatesBulkRevokeBodyReason,
)
from pki_api.pki_manager_rest_api_client.types import UNSET

from .client import get_client
from .http import ApiError, unwrap
from .output import print_error, print_json, print_note, print_records, print_success, print_warning

console = Console()

bulk_app = typer.Typer(help="Bulk certificate operations (max 100 per call)", no_args_is_help=True)

OutputFormat = Annotated[str, typer.Option("--output", "-o", help="Output format: table, json")]
IdOption = Annotated[
    Optional[list[str]],
    typer.Option("--id", "-i", help="Certificate ID (repeatable; also accepts a comma-separated list)"),
]
IdsFileOption = Annotated[
    Optional[Path],
    typer.Option("--ids-file", help="File with one certificate ID per line ('-' reads stdin)"),
]

MAX_BATCH = 100


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


def _collect_ids(ids: Optional[list[str]], ids_file: Optional[Path]) -> list[UUID]:
    """Merge --id flags and --ids-file into a validated, de-duplicated list."""
    raw: list[str] = []
    for value in ids or []:
        raw.extend(part.strip() for part in value.split(","))
    if ids_file:
        text = typer.get_text_stream("stdin").read() if str(ids_file) == "-" else Path(ids_file).read_text()
        raw.extend(line.strip() for line in text.splitlines())

    seen: list[str] = []
    for value in raw:
        if value and value not in seen:
            seen.append(value)

    if not seen:
        print_error("No certificate IDs given — pass --id (repeatable) and/or --ids-file")
        raise typer.Exit(1)
    if len(seen) > MAX_BATCH:
        print_error(f"{len(seen)} IDs given, but the API accepts at most {MAX_BATCH} per call")
        raise typer.Exit(1)

    try:
        return [UUID(value) for value in seen]
    except ValueError as exc:
        print_error(f"Invalid certificate ID: {exc}")
        raise typer.Exit(1)


def _report(data: dict, output: str, *, title: str) -> None:
    """Render a bulk {successful, failed, results[]} response."""
    if output == "json":
        print_json(data)
    else:
        print_records(data.get("results", []), title=title)
        successful, failed = data.get("successful", 0), data.get("failed", 0)
        console.print(f"[green]{successful} succeeded[/green], " + (f"[red]{failed} failed[/red]" if failed else "0 failed"))
    if data.get("failed"):
        raise typer.Exit(1)


@bulk_app.command("issue")
def bulk_issue(
    ca_id: Annotated[str, typer.Option("--ca", help="CA ID to issue from")],
    csv_file: Annotated[
        Path,
        typer.Option("--csv", help="CSV file: certificateType,CN,O,C,SANs,validityDays ('-' reads stdin)"),
    ],
    validity: Annotated[Optional[int], typer.Option("--validity", "-v", help="Default validity in days for rows that omit it")] = None,
    output: OutputFormat = "table",
) -> None:
    """Issue certificates in bulk from a CSV file.

    Each line is ``certificateType,CN,O,C,SANs,validityDays``. Only the first
    four fields are required; SANs are semicolon-separated and classified into
    DNS / IP / email by their shape. The API treats every line as data, so a
    ``certificateType,...`` header line is stripped here before sending.
    """
    with _api():
        csv_data = typer.get_text_stream("stdin").read() if str(csv_file) == "-" else Path(csv_file).read_text()
        if not csv_data.strip():
            print_error("CSV data is empty")
            raise typer.Exit(1)

        lines = csv_data.strip().splitlines()
        if lines and lines[0].split(",")[0].strip().lower() == "certificatetype":
            print_note("Skipping CSV header row")
            csv_data = "\n".join(lines[1:])
            if not csv_data.strip():
                print_error("CSV contains only a header row")
                raise typer.Exit(1)

        body = PostCertificatesBulkIssueBody(
            ca_id=UUID(ca_id),
            csv_data=csv_data,
            default_validity_days=validity if validity else UNSET,
        )
        result = unwrap(post_certificates_bulk_issue.sync(client=get_client(), body=body), what="Bulk issue")
        _report(result.to_dict(), output, title="Bulk issue results")


@bulk_app.command("renew")
def bulk_renew(
    ids: IdOption = None,
    ids_file: IdsFileOption = None,
    validity: Annotated[Optional[int], typer.Option("--validity", "-v", help="Validity in days (defaults to the original validity)")] = None,
    new_key: Annotated[bool, typer.Option("--new-key/--same-key", help="Generate a fresh key pair for the renewal")] = True,
    revoke_original: Annotated[bool, typer.Option("--revoke-original", help="Revoke each original certificate after renewal")] = False,
    output: OutputFormat = "table",
) -> None:
    """Renew certificates in bulk."""
    with _api():
        body = PostCertificatesBulkRenewBody(
            certificate_ids=_collect_ids(ids, ids_file),
            generate_new_key=new_key,
            validity_days=validity if validity else UNSET,
            revoke_original=revoke_original,
        )
        result = unwrap(post_certificates_bulk_renew.sync(client=get_client(), body=body), what="Bulk renew")
        _report(result.to_dict(), output, title="Bulk renew results")


@bulk_app.command("revoke")
def bulk_revoke(
    reason: Annotated[str, typer.Option("--reason", "-r", help="Revocation reason (e.g. keyCompromise, superseded)")],
    ids: IdOption = None,
    ids_file: IdsFileOption = None,
    details: Annotated[Optional[str], typer.Option("--details", help="Free-text detail recorded with the revocation")] = None,
    generate_crl: Annotated[bool, typer.Option("--generate-crl/--no-generate-crl", help="Regenerate the CRL afterwards")] = True,
    force: Annotated[bool, typer.Option("--force", "-f", help="Skip confirmation")] = False,
    output: OutputFormat = "table",
) -> None:
    """Revoke certificates in bulk."""
    cert_ids = _collect_ids(ids, ids_file)
    if not force and not typer.confirm(f"Revoke {len(cert_ids)} certificate(s) with reason '{reason}'?"):
        raise typer.Abort()

    with _api():
        body = PostCertificatesBulkRevokeBody(
            certificate_ids=cert_ids,
            reason=PostCertificatesBulkRevokeBodyReason(reason),
            details=details if details else UNSET,
            generate_crl=generate_crl,
        )
        result = unwrap(post_certificates_bulk_revoke.sync(client=get_client(), body=body), what="Bulk revoke")
        _report(result.to_dict(), output, title="Bulk revoke results")


@bulk_app.command("delete")
def bulk_delete(
    ids: IdOption = None,
    ids_file: IdsFileOption = None,
    destroy_key: Annotated[bool, typer.Option("--destroy-key/--keep-key", help="Also destroy the private key in the KMS")] = True,
    remove_from_crl: Annotated[bool, typer.Option("--remove-from-crl", help="Drop the entries from the CRL (not recommended)")] = False,
    force: Annotated[bool, typer.Option("--force", "-f", help="Skip confirmation")] = False,
    output: OutputFormat = "table",
) -> None:
    """Delete certificates in bulk (irreversible)."""
    cert_ids = _collect_ids(ids, ids_file)
    if not force and not typer.confirm(f"DELETE {len(cert_ids)} certificate(s)? This is irreversible!"):
        raise typer.Abort()

    with _api():
        body = DeleteCertificatesBulkBody(
            certificate_ids=cert_ids,
            destroy_key=destroy_key,
            remove_from_crl=remove_from_crl,
        )
        result = unwrap(delete_certificates_bulk.sync(client=get_client(), body=body), what="Bulk delete")
        _report(result.to_dict(), output, title="Bulk delete results")


@bulk_app.command("download")
def bulk_download(
    ids: IdOption = None,
    ids_file: IdsFileOption = None,
    fmt: Annotated[
        str,
        typer.Option("--format", "-f", help="pem, crt, der, cer, pem-chain, pem-key, pkcs7, p7b, pkcs12, pfx, p12, jks-keystore, jks-truststore, docker-volume, all"),
    ] = "pem",
    password: Annotated[Optional[str], typer.Option("--password", "-p", help="Password for encrypted formats (min 8 chars)")] = None,
    encrypt_key: Annotated[bool, typer.Option("--encrypt-key/--no-encrypt-key", help="Encrypt the private key with the password")] = True,
    output_file: Annotated[Optional[Path], typer.Option("--output-file", help="ZIP destination (defaults to the server-suggested name)")] = None,
) -> None:
    """Download certificates in bulk as a ZIP archive."""
    with _api():
        body = PostCertificatesBulkDownloadBody(
            certificate_ids=_collect_ids(ids, ids_file),
            format_=PostCertificatesBulkDownloadBodyFormat(fmt),
            password=password if password else UNSET,
            encrypt_private_key=encrypt_key,
        )
        result = unwrap(
            post_certificates_bulk_download.sync(client=get_client(), body=body),
            what="Bulk download",
        )
        data = result.to_dict()
        if not data.get("data"):
            print_warning("The server returned no archive data")
            raise typer.Exit(1)

        path = Path(output_file) if output_file else Path(data.get("filename") or "certificates.zip")
        payload = base64.b64decode(data["data"])
        path.write_bytes(payload)
        print_success(f"Saved {len(payload)} bytes to {path}")
