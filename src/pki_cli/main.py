"""PKI CLI - Main entry point using OpenAPI generated client."""

from pathlib import Path
from typing import Annotated, Optional
from uuid import UUID

import typer
from rich.console import Console
from rich.table import Table

from pki_api.pki_manager_rest_api_client.api.certificate_authorities import (
    delete_cas_id,
    get_cas,
    get_cas_id,
    get_cas_id_certificates,
    get_cas_id_download,
    post_cas,
    post_cas_id_revoke,
)
from pki_api.pki_manager_rest_api_client.api.certificates import (
    delete_certificates_id,
    get_certificates,
    get_certificates_id,
    get_certificates_id_download,
    post_certificates,
    post_certificates_id_renew,
    post_certificates_id_revoke,
)
from pki_api.pki_manager_rest_api_client.api.dashboard import (
    get_dashboard_expiring,
    get_dashboard_stats,
    get_health,
)
from pki_api.pki_manager_rest_api_client.api.search import get_search
from pki_api.pki_manager_rest_api_client.models import (
    GetCasIdCertificatesCertificateType,
    GetCasIdCertificatesStatus,
    GetCasIdDownloadFormat,
    GetCasSortBy,
    GetCasSortOrder,
    GetCasStatus,
    GetCertificatesSortBy,
    GetCertificatesSortOrder,
    GetCertificatesStatus,
    GetCertificatesType,
    PostCasBody,
    PostCasBodyKeyAlgorithm,
    PostCasBodySubject,
    PostCasIdRevokeBody,
    PostCasIdRevokeBodyReason,
    PostCertificatesBody,
    PostCertificatesBodyCertificateType,
    PostCertificatesBodyKeyAlgorithm,
    PostCertificatesBodySubject,
    PostCertificatesIdRenewBody,
    PostCertificatesIdRenewBodySubject,
    PostCertificatesIdRevokeBody,
    PostCertificatesIdRevokeBodyReason,
)
from pki_api.pki_manager_rest_api_client.models.get_certificates_id_download_format import (
    GetCertificatesIdDownloadFormat,
)
from pki_api.pki_manager_rest_api_client.types import UNSET

from . import API_VERSION, PKI_MANAGER_VERSION, __version__
from .audit import audit_app, domain_app, report_app
from .bulk import bulk_app
from .client import get_client, reset_wrapper
from .config import configure
from .crl import crl_app
from .external import external_app
from .http import public, unwrap
from .output import (
    print_ca_detail,
    print_ca_table,
    print_cert_detail,
    print_cert_table,
    print_error,
    print_expiring,
    print_json,
    print_kv,
    print_records,
    print_search_results,
    print_stats,
    print_success,
)
from .ssh import ssh_app

console = Console()

# Main app
app = typer.Typer(
    name="pki",
    help="PKI Manager CLI - Manage X.509 certificates",
    no_args_is_help=True,
)

# Subcommand groups
ca_app = typer.Typer(help="Certificate Authority management")
cert_app = typer.Typer(help="Certificate management")

cert_app.add_typer(bulk_app, name="bulk")

app.add_typer(ca_app, name="ca")
app.add_typer(cert_app, name="cert")
app.add_typer(crl_app, name="crl")
app.add_typer(domain_app, name="domain")
app.add_typer(audit_app, name="audit")
app.add_typer(report_app, name="report")
app.add_typer(ssh_app, name="ssh")
app.add_typer(external_app, name="external")


# Common type aliases
OutputFormat = Annotated[str, typer.Option("--output", "-o", help="Output format: table, json")]

# The API uses RFC 5280 camelCase reason codes, not snake_case.
REVOCATION_REASON_HELP = (
    "Revocation reason: unspecified, keyCompromise, caCompromise, affiliationChanged, "
    "superseded, cessationOfOperation, certificateHold, removeFromCRL"
)


def _print_pagination(data: dict, shown: int, noun: str) -> None:
    """Print a '25 of 312' footer so truncated listings are obvious."""
    total = (data.get("pagination") or {}).get("total")
    if total is not None and total != shown:
        console.print(f"[dim]{shown} of {total} {noun} (use --limit/--offset to page)[/dim]")


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"pki-cli version {__version__}")
        console.print(
            f"[dim]built for PKI Manager {PKI_MANAGER_VERSION} (REST API v{API_VERSION})[/dim]"
        )
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option("--version", "-v", callback=version_callback, is_eager=True, help="Show version"),
    ] = False,
    api_url: Annotated[
        Optional[str],
        typer.Option("--api-url", envvar="PKI_API_URL", help="PKI Manager API URL"),
    ] = None,
    oidc_url: Annotated[
        Optional[str],
        typer.Option("--oidc-url", envvar="PKI_OIDC_URL", help="OIDC token endpoint URL"),
    ] = None,
    client_id: Annotated[
        Optional[str],
        typer.Option("--client-id", envvar="PKI_CLIENT_ID", help="OIDC client ID"),
    ] = None,
    client_secret: Annotated[
        Optional[str],
        typer.Option("--client-secret", envvar="PKI_CLIENT_SECRET", help="OIDC client secret"),
    ] = None,
    token: Annotated[
        Optional[str],
        typer.Option("--token", envvar="PKI_TOKEN", help="Pre-obtained bearer token (skips the OIDC exchange)"),
    ] = None,
) -> None:
    """PKI Manager CLI - Manage X.509 certificates.

    Configuration can be provided via:
    - CLI options (--api-url, --client-id, --client-secret, --token)
    - Environment variables (PKI_API_URL, PKI_CLIENT_ID, PKI_CLIENT_SECRET, PKI_TOKEN)
    - .env file in current directory or ~/.config/pki-cli/.env

    Only PKI_API_URL is mandatory. Supply either a full OIDC client-credentials
    configuration or a PKI_TOKEN; omit both to call a server that runs with
    OIDC disabled.
    """
    # Configure settings with any CLI overrides
    configure(
        api_url=api_url,
        oidc_url=oidc_url,
        client_id=client_id,
        client_secret=client_secret,
        token=token,
    )
    reset_wrapper()


# =============================================================================
# CA Commands
# =============================================================================


@ca_app.command("list")
def ca_list(
    status: Annotated[Optional[str], typer.Option("--status", "-s", help="Filter by status: active, revoked, expired")] = None,
    search: Annotated[Optional[str], typer.Option("--search", "-q", help="Search by subject or serial number")] = None,
    sort_by: Annotated[Optional[str], typer.Option("--sort-by", help="Sort field: name, issuedDate, expiryDate")] = None,
    sort_order: Annotated[Optional[str], typer.Option("--sort-order", help="Sort direction: asc, desc")] = None,
    limit: Annotated[int, typer.Option("--limit", "-l", help="Max results (1-100)")] = 50,
    offset: Annotated[int, typer.Option("--offset", help="Number of CAs to skip")] = 0,
    output: OutputFormat = "table",
) -> None:
    """List all Certificate Authorities."""
    try:
        client = get_client()
        result = get_cas.sync(
            client=client,
            status=GetCasStatus(status) if status else UNSET,
            search=search or UNSET,
            sort_by=GetCasSortBy(sort_by) if sort_by else UNSET,
            sort_order=GetCasSortOrder(sort_order) if sort_order else UNSET,
            limit=limit,
            offset=offset,
        )

        if result is None:
            print_error("Failed to fetch CAs")
            raise typer.Exit(1)

        if output == "json":
            print_json(result.to_dict())
        else:
            items = [item.to_dict() for item in result.items]
            if items:
                print_ca_table(items)
                _print_pagination(result.to_dict(), len(items), "CAs")
            else:
                console.print("[dim]No CAs found[/dim]")
    except typer.Exit:
        raise
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@ca_app.command("get")
def ca_get(
    ca_id: Annotated[str, typer.Argument(help="CA ID (UUID)")],
    output: OutputFormat = "table",
) -> None:
    """Get CA details."""
    try:
        client = get_client()
        result = get_cas_id.sync(client=client, id=ca_id)

        if result is None:
            print_error(f"CA {ca_id} not found")
            raise typer.Exit(1)

        if output == "json":
            print_json(result.to_dict())
        else:
            print_ca_detail(result.to_dict())
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@ca_app.command("create")
def ca_create(
    common_name: Annotated[str, typer.Option("--cn", help="Common Name")],
    organization: Annotated[str, typer.Option("--org", "-O", help="Organization")] = "YMBIHQ",
    country: Annotated[str, typer.Option("--country", "-c", help="Country (2-letter)")] = "ES",
    state: Annotated[Optional[str], typer.Option("--state", help="State/Province")] = None,
    locality: Annotated[Optional[str], typer.Option("--locality", "-l", help="City")] = None,
    ou: Annotated[Optional[str], typer.Option("--ou", help="Organizational Unit")] = None,
    algorithm: Annotated[str, typer.Option("--algorithm", "-a", help="Key algorithm: RSA-2048 or RSA-4096")] = "RSA-4096",
    validity_years: Annotated[int, typer.Option("--validity-years", "-v", help="Validity in years (1-30)")] = 20,
    tag: Annotated[Optional[list[str]], typer.Option("--tag", help="Tag (repeatable)")] = None,
    output: OutputFormat = "table",
) -> None:
    """Create a new Certificate Authority."""
    try:
        client = get_client()

        subject = PostCasBodySubject(
            common_name=common_name,
            organization=organization,
            country=country,
            state=state if state else UNSET,
            locality=locality if locality else UNSET,
            organizational_unit=ou if ou else UNSET,
        )

        body = PostCasBody(
            subject=subject,
            key_algorithm=PostCasBodyKeyAlgorithm(algorithm),
            validity_years=validity_years,
            tags=list(tag) if tag else UNSET,
        )

        result = post_cas.sync(client=client, body=body)

        if result is None:
            print_error("Failed to create CA")
            raise typer.Exit(1)

        if output == "json":
            print_json(result.to_dict())
        else:
            print_success(f"CA created: {result.id}")
            print_ca_detail(result.to_dict())
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@ca_app.command("revoke")
def ca_revoke(
    ca_id: Annotated[str, typer.Argument(help="CA ID (UUID)")],
    reason: Annotated[str, typer.Option("--reason", "-r", help=REVOCATION_REASON_HELP)] = "unspecified",
    details: Annotated[Optional[str], typer.Option("--details", help="Free-text detail recorded with the revocation")] = None,
    force: Annotated[bool, typer.Option("--force", "-f", help="Skip confirmation")] = False,
) -> None:
    """Revoke a Certificate Authority."""
    if not force:
        confirm = typer.confirm(f"Are you sure you want to revoke CA {ca_id}?")
        if not confirm:
            raise typer.Abort()

    try:
        client = get_client()
        body = PostCasIdRevokeBody(
            reason=PostCasIdRevokeBodyReason(reason),
            details=details if details else UNSET,
        )
        result = post_cas_id_revoke.sync(client=client, id=ca_id, body=body)

        if result is None:
            print_error(f"Failed to revoke CA {ca_id}")
            raise typer.Exit(1)

        print_success(f"CA {ca_id} revoked")
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@ca_app.command("delete")
def ca_delete(
    ca_id: Annotated[str, typer.Argument(help="CA ID (UUID)")],
    destroy_key: Annotated[bool, typer.Option("--destroy-key", help="Also destroy the CA private key in the KMS")] = False,
    force: Annotated[bool, typer.Option("--force", "-f", help="Skip confirmation")] = False,
) -> None:
    """Delete a Certificate Authority."""
    if not force:
        confirm = typer.confirm(f"Are you sure you want to DELETE CA {ca_id}? This is irreversible!")
        if not confirm:
            raise typer.Abort()

    try:
        client = get_client()
        unwrap(delete_cas_id.sync(client=client, id=ca_id, destroy_key=destroy_key), what="CA deletion")
        print_success(f"CA {ca_id} deleted")
    except typer.Exit:
        raise
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


CA_CERT_COLUMNS = [
    "id",
    "subjectDn",
    "certificateType",
    "serialNumber",
    "status",
    "expiryStatus",
    "notAfter",
]


@ca_app.command("certs")
def ca_certs(
    ca_id: Annotated[str, typer.Argument(help="CA ID (UUID)")],
    status: Annotated[Optional[str], typer.Option("--status", "-s", help="Filter by status: active, revoked, expired")] = None,
    cert_type: Annotated[Optional[str], typer.Option("--type", "-t", help="Filter by type: server, client, dual, code_signing, email")] = None,
    search: Annotated[Optional[str], typer.Option("--search", "-q", help="Search subject DN, serial number, or SANs")] = None,
    limit: Annotated[int, typer.Option("--limit", "-l", help="Max results (1-100)")] = 50,
    offset: Annotated[int, typer.Option("--offset", help="Number of certificates to skip")] = 0,
    output: OutputFormat = "table",
) -> None:
    """List the certificates issued by a CA."""
    try:
        result = unwrap(
            get_cas_id_certificates.sync(
                UUID(ca_id),
                client=get_client(),
                status=GetCasIdCertificatesStatus(status) if status else UNSET,
                certificate_type=GetCasIdCertificatesCertificateType(cert_type) if cert_type else UNSET,
                search=search or UNSET,
                limit=limit,
                offset=offset,
            ),
            what="CA certificate listing",
        )
        data = result.to_dict()
        if output == "json":
            print_json(data)
            return
        print_records(data.get("items", []), columns=CA_CERT_COLUMNS, title=f"Certificates issued by {ca_id}")
        total = (data.get("pagination") or {}).get("total")
        if total is not None:
            console.print(f"[dim]{len(data.get('items', []))} of {total} certificates[/dim]")
    except typer.Exit:
        raise
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@ca_app.command("download")
def ca_download(
    ca_id: Annotated[str, typer.Argument(help="CA ID (UUID)")],
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="pem, crt, der, cer, p12-truststore, p12-keystore, jks-truststore, jks-keystore"),
    ] = "pem",
    password: Annotated[
        Optional[str],
        typer.Option("--password", "-p", help="Password for P12/JKS (required for keystores, defaults to 'changeit' for truststores)"),
    ] = None,
    output_file: Annotated[Optional[Path], typer.Option("--output", "-o", help="Output file path")] = None,
) -> None:
    """Download a CA certificate (or a truststore/keystore bundle)."""
    import base64

    try:
        if format.endswith("keystore") and not password:
            print_error(f"Password required for {format} format")
            raise typer.Exit(1)

        result = unwrap(
            get_cas_id_download.sync(
                UUID(ca_id),
                client=get_client(),
                format_=GetCasIdDownloadFormat(format),
                password=password if password else UNSET,
            ),
            what="CA download",
        )
        data = result.to_dict()
        if not data.get("data"):
            print_error("No certificate data in response")
            raise typer.Exit(1)

        payload = base64.b64decode(data["data"])
        path = Path(output_file) if output_file else Path(data.get("filename") or f"ca.{format}")
        path.write_bytes(payload)
        print_success(f"CA certificate saved to {path}")
    except typer.Exit:
        raise
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@ca_app.command("pem")
def ca_pem(
    ca_id: Annotated[str, typer.Argument(help="CA ID (UUID)")],
    format: Annotated[str, typer.Option("--format", "-f", help="pem/crt (text) or der/cer (binary)")] = "pem",
    output_file: Annotated[Optional[Path], typer.Option("--output", "-o", help="Output file path")] = None,
) -> None:
    """Fetch a CA certificate from its public, unauthenticated URL.

    This is the same ``/cas/<id>.pem`` link an AIA extension points at, so it
    works without credentials — handy for bootstrapping trust on a new host.
    """
    try:
        data = public("GET", f"/cas/{ca_id}.{format}", expect_bytes=True)
        if output_file:
            Path(output_file).write_bytes(data)
            print_success(f"Saved {len(data)} bytes to {output_file}")
        elif format in ("pem", "crt"):
            typer.echo(data.decode().rstrip("\n"))
        else:
            path = Path(f"{ca_id}.{format}")
            path.write_bytes(data)
            print_success(f"Saved {len(data)} bytes to {path}")
    except typer.Exit:
        raise
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


# =============================================================================
# Certificate Commands
# =============================================================================


@cert_app.command("list")
def cert_list(
    ca_id: Annotated[Optional[str], typer.Option("--ca", help="Filter by CA ID")] = None,
    status: Annotated[Optional[str], typer.Option("--status", "-s", help="Filter by status")] = None,
    cert_type: Annotated[Optional[str], typer.Option("--type", "-t", help="Filter by type: server, client, dual, code_signing, email")] = None,
    search: Annotated[Optional[str], typer.Option("--search", "-q", help="Search by subject DN, serial number, or SANs")] = None,
    sort_by: Annotated[Optional[str], typer.Option("--sort-by", help="Sort field: createdAt, notAfter, subjectDn")] = None,
    sort_order: Annotated[Optional[str], typer.Option("--sort-order", help="Sort direction: asc, desc")] = None,
    limit: Annotated[int, typer.Option("--limit", "-l", help="Max results (1-100)")] = 50,
    offset: Annotated[int, typer.Option("--offset", help="Number of certificates to skip")] = 0,
    output: OutputFormat = "table",
) -> None:
    """List certificates."""
    try:
        client = get_client()

        result = get_certificates.sync(
            client=client,
            ca_id=UUID(ca_id) if ca_id else UNSET,
            status=GetCertificatesStatus(status) if status else UNSET,
            type_=GetCertificatesType(cert_type) if cert_type else UNSET,
            search=search or UNSET,
            sort_by=GetCertificatesSortBy(sort_by) if sort_by else UNSET,
            sort_order=GetCertificatesSortOrder(sort_order) if sort_order else UNSET,
            limit=limit,
            offset=offset,
        )

        if result is None:
            print_error("Failed to fetch certificates")
            raise typer.Exit(1)

        if output == "json":
            print_json(result.to_dict())
        else:
            items = [item.to_dict() for item in result.items]
            if items:
                print_cert_table(items)
                _print_pagination(result.to_dict(), len(items), "certificates")
            else:
                console.print("[dim]No certificates found[/dim]")
    except typer.Exit:
        raise
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@cert_app.command("get")
def cert_get(
    cert_id: Annotated[str, typer.Argument(help="Certificate ID (UUID)")],
    output: OutputFormat = "table",
) -> None:
    """Get certificate details."""
    try:
        client = get_client()
        result = get_certificates_id.sync(client=client, id=cert_id)

        if result is None:
            print_error(f"Certificate {cert_id} not found")
            raise typer.Exit(1)

        if output == "json":
            print_json(result.to_dict())
        else:
            print_cert_detail(result.to_dict())
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@cert_app.command("issue")
def cert_issue(
    ca_id: Annotated[str, typer.Option("--ca", help="CA ID to issue from")],
    common_name: Annotated[str, typer.Option("--cn", help="Common Name")],
    cert_type: Annotated[str, typer.Option("--type", "-t", help="Certificate type: server, client, dual, email, code_signing")] = "server",
    organization: Annotated[str, typer.Option("--org", "-O", help="Organization")] = "YMBIHQ",
    country: Annotated[str, typer.Option("--country", "-c", help="Country")] = "ES",
    ou: Annotated[Optional[str], typer.Option("--ou", help="Organizational Unit")] = None,
    state: Annotated[Optional[str], typer.Option("--state", help="State/Province")] = None,
    locality: Annotated[Optional[str], typer.Option("--locality", "-l", help="City")] = None,
    algorithm: Annotated[str, typer.Option("--algorithm", "-a", help="Key algorithm: RSA-2048, RSA-4096, ECDSA-P256, ECDSA-P384")] = "RSA-2048",
    validity: Annotated[int, typer.Option("--validity", "-v", help="Validity in days (1-825)")] = 365,
    dns: Annotated[Optional[list[str]], typer.Option("--dns", "-d", help="DNS SANs (repeatable)")] = None,
    ip: Annotated[Optional[list[str]], typer.Option("--ip", help="IP SANs (repeatable)")] = None,
    email: Annotated[Optional[list[str]], typer.Option("--email", help="Email SANs (repeatable)")] = None,
    tag: Annotated[Optional[list[str]], typer.Option("--tag", help="Tag (repeatable)")] = None,
    no_cn_san: Annotated[bool, typer.Option("--no-cn-san", help="Do not add the CN to the DNS SANs automatically")] = False,
    output: OutputFormat = "table",
) -> None:
    """Issue a new certificate."""
    try:
        client = get_client()

        # Build DNS names list - include CN automatically (modern clients ignore
        # the CN, so the CN must also appear as a SAN to be trusted).
        dns_names = list(dns) if dns else []
        if not no_cn_san and common_name not in dns_names:
            dns_names.insert(0, common_name)

        subject = PostCertificatesBodySubject(
            common_name=common_name,
            organization=organization,
            country=country,
            organizational_unit=ou if ou else UNSET,
            state=state if state else UNSET,
            locality=locality if locality else UNSET,
        )

        body = PostCertificatesBody(
            ca_id=UUID(ca_id),
            certificate_type=PostCertificatesBodyCertificateType(cert_type),
            subject=subject,
            key_algorithm=PostCertificatesBodyKeyAlgorithm(algorithm),
            validity_days=validity,
            san_dns=dns_names if dns_names else UNSET,
            san_ip=list(ip) if ip else UNSET,
            san_email=list(email) if email else UNSET,
            tags=list(tag) if tag else UNSET,
        )

        result = post_certificates.sync(client=client, body=body)

        if result is None:
            print_error("Failed to issue certificate")
            raise typer.Exit(1)

        if output == "json":
            print_json(result.to_dict())
        else:
            print_success(f"Certificate issued: {result.id}")
            print_cert_detail(result.to_dict())
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@cert_app.command("renew")
def cert_renew(
    cert_id: Annotated[str, typer.Argument(help="Certificate ID (UUID)")],
    validity: Annotated[int, typer.Option("--validity", "-v", help="Validity in days")] = 365,
    new_key: Annotated[bool, typer.Option("--new-key/--same-key", help="Generate a fresh key pair for the renewal")] = True,
    revoke_original: Annotated[bool, typer.Option("--revoke-original", help="Revoke the original certificate after renewal")] = False,
    update_info: Annotated[bool, typer.Option("--update-info", help="Apply the --cn/--org/--dns/... overrides below")] = False,
    common_name: Annotated[Optional[str], typer.Option("--cn", help="New Common Name (implies --update-info)")] = None,
    organization: Annotated[Optional[str], typer.Option("--org", "-O", help="New Organization (implies --update-info)")] = None,
    ou: Annotated[Optional[str], typer.Option("--ou", help="New Organizational Unit (implies --update-info)")] = None,
    country: Annotated[Optional[str], typer.Option("--country", "-c", help="New Country (implies --update-info)")] = None,
    state: Annotated[Optional[str], typer.Option("--state", help="New State/Province (implies --update-info)")] = None,
    locality: Annotated[Optional[str], typer.Option("--locality", "-l", help="New City (implies --update-info)")] = None,
    dns: Annotated[Optional[list[str]], typer.Option("--dns", "-d", help="New DNS SAN (repeatable; implies --update-info)")] = None,
    ip: Annotated[Optional[list[str]], typer.Option("--ip", help="New IP SAN (repeatable; implies --update-info)")] = None,
    email: Annotated[Optional[list[str]], typer.Option("--email", help="New email SAN (repeatable; implies --update-info)")] = None,
    output: OutputFormat = "table",
) -> None:
    """Renew a certificate, optionally updating its subject or SANs."""
    try:
        client = get_client()

        subject_fields = {
            "common_name": common_name,
            "organization": organization,
            "organizational_unit": ou,
            "country": country,
            "state": state,
            "locality": locality,
        }
        given = {k: v for k, v in subject_fields.items() if v}
        # Any override implies updateInfo — the server ignores them otherwise.
        if given or dns or ip or email:
            update_info = True

        body = PostCertificatesIdRenewBody(
            validity_days=validity,
            generate_new_key=new_key,
            revoke_original=revoke_original,
            update_info=update_info,
            subject=PostCertificatesIdRenewBodySubject(**given) if given else UNSET,
            san_dns=list(dns) if dns else UNSET,
            san_ip=list(ip) if ip else UNSET,
            san_email=list(email) if email else UNSET,
        )
        result = post_certificates_id_renew.sync(client=client, id=cert_id, body=body)

        if result is None:
            print_error(f"Failed to renew certificate {cert_id}")
            raise typer.Exit(1)

        if output == "json":
            print_json(result.to_dict())
        else:
            print_success(f"Certificate renewed: {result.id}")
            print_cert_detail(result.to_dict())
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@cert_app.command("revoke")
def cert_revoke(
    cert_id: Annotated[str, typer.Argument(help="Certificate ID (UUID)")],
    reason: Annotated[str, typer.Option("--reason", "-r", help=REVOCATION_REASON_HELP)] = "unspecified",
    details: Annotated[Optional[str], typer.Option("--details", help="Free-text detail recorded with the revocation")] = None,
    effective_date: Annotated[Optional[int], typer.Option("--effective-date", help="Unix timestamp for the effective revocation date")] = None,
    generate_crl: Annotated[bool, typer.Option("--generate-crl", help="Regenerate the CA's CRL immediately")] = False,
    force: Annotated[bool, typer.Option("--force", "-f", help="Skip confirmation")] = False,
) -> None:
    """Revoke a certificate."""
    if not force:
        confirm = typer.confirm(f"Are you sure you want to revoke certificate {cert_id}?")
        if not confirm:
            raise typer.Abort()

    try:
        client = get_client()
        body = PostCertificatesIdRevokeBody(
            reason=PostCertificatesIdRevokeBodyReason(reason),
            details=details if details else UNSET,
            effective_date=effective_date if effective_date else UNSET,
            generate_crl=generate_crl,
        )
        result = post_certificates_id_revoke.sync(client=client, id=cert_id, body=body)

        if result is None:
            print_error(f"Failed to revoke certificate {cert_id}")
            raise typer.Exit(1)

        print_success(f"Certificate {cert_id} revoked")
    except typer.Exit:
        raise
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@cert_app.command("delete")
def cert_delete(
    cert_id: Annotated[str, typer.Argument(help="Certificate ID (UUID)")],
    destroy_key: Annotated[bool, typer.Option("--destroy-key", help="Also destroy the private key in the KMS")] = False,
    remove_from_crl: Annotated[bool, typer.Option("--remove-from-crl", help="Drop the CRL entry (not recommended)")] = False,
    force: Annotated[bool, typer.Option("--force", "-f", help="Skip confirmation")] = False,
) -> None:
    """Delete a certificate."""
    if not force:
        confirm = typer.confirm(f"Are you sure you want to DELETE certificate {cert_id}?")
        if not confirm:
            raise typer.Abort()

    try:
        client = get_client()
        unwrap(
            delete_certificates_id.sync(
                client=client,
                id=cert_id,
                destroy_key=destroy_key,
                remove_from_crl=remove_from_crl,
            ),
            what="Certificate deletion",
        )
        print_success(f"Certificate {cert_id} deleted")
    except typer.Exit:
        raise
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


DOWNLOAD_FORMAT_HELP = (
    "Download format: pem, der, chain-pem, full-pem, full-der, csr-pem, "
    "key-pem, key-der, pkcs8-pem, pkcs8-der, pkcs8-encrypted, "
    "p12/pfx, jks-keystore, jks-truststore"
)

# Friendly aliases for the API's format enum.
DOWNLOAD_FORMAT_ALIASES = {
    "pkcs12": "p12",
    "jks": "jks-keystore",
    "chain": "chain-pem",
    "key": "key-pem",
    "csr": "csr-pem",
    "full": "full-pem",
}

# Formats the server refuses without a password.
PASSWORD_REQUIRED_FORMATS = {"p12", "pfx", "jks-keystore", "pkcs8-encrypted"}


@cert_app.command("download")
def cert_download(
    cert_id: Annotated[str, typer.Argument(help="Certificate ID (UUID)")],
    output_file: Annotated[Optional[Path], typer.Option("--output", "-o", help="Output file path (defaults to the server-suggested name)")] = None,
    format: Annotated[str, typer.Option("--format", "-f", help=DOWNLOAD_FORMAT_HELP)] = "pem",
    password: Annotated[Optional[str], typer.Option("--password", "-p", help="Password for keystore / encrypted-key formats")] = None,
    encrypt_key: Annotated[bool, typer.Option("--encrypt-key", help="Encrypt the exported private key with --password")] = False,
    no_chain: Annotated[bool, typer.Option("--no-chain", help="Exclude the issuing chain from bundle formats")] = False,
) -> None:
    """Download a certificate, its chain, its key, or a keystore bundle."""
    import base64

    try:
        api_format = DOWNLOAD_FORMAT_ALIASES.get(format.lower(), format.lower())
        try:
            format_enum = GetCertificatesIdDownloadFormat(api_format)
        except ValueError:
            print_error(f"Unknown format {format!r}. {DOWNLOAD_FORMAT_HELP}")
            raise typer.Exit(1)

        if api_format in PASSWORD_REQUIRED_FORMATS and not password:
            print_error(f"Password required for {format} format")
            raise typer.Exit(1)

        client = get_client()
        parsed = unwrap(
            get_certificates_id_download.sync(
                client=client,
                id=cert_id,
                format_=format_enum,
                password=password if password else UNSET,
                encrypt_private_key=encrypt_key,
                include_chain=not no_chain,
            ),
            what="Certificate download",
        )

        if parsed.data is UNSET or not parsed.data:
            print_error("No certificate data in response")
            raise typer.Exit(1)

        cert_data = base64.b64decode(parsed.data)

        if output_file is None:
            suggested = parsed.filename if parsed.filename and parsed.filename is not UNSET else None
            output_file = Path(suggested or f"cert.{api_format}")

        output_file.write_bytes(cert_data)
        print_success(f"Certificate saved to {output_file}")
    except typer.Exit:
        raise
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


# =============================================================================
# Dashboard Commands
# =============================================================================


@app.command("stats")
def stats(output: OutputFormat = "table") -> None:
    """Show dashboard statistics."""
    try:
        client = get_client()
        result = get_dashboard_stats.sync(client=client)

        if result is None:
            print_error("Failed to fetch statistics")
            raise typer.Exit(1)

        if output == "json":
            print_json(result.to_dict())
        else:
            print_stats(result.to_dict())
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("expiring")
def expiring(
    limit: Annotated[int, typer.Option("--limit", "-l", help="Max results")] = 5,
    output: OutputFormat = "table",
) -> None:
    """Show expiring certificates."""
    try:
        client = get_client()
        result = get_dashboard_expiring.sync(client=client, limit=limit)

        if result is None:
            print_error("Failed to fetch expiring certificates")
            raise typer.Exit(1)

        # Result is a list directly
        if isinstance(result, list):
            items = [item.to_dict() for item in result]
        else:
            items = []

        if output == "json":
            print_json(items)
        else:
            if items:
                print_expiring(items)
            else:
                console.print("[green]No certificates expiring soon[/green]")
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("search")
def search(
    query: Annotated[str, typer.Argument(help="Search query")],
    limit: Annotated[int, typer.Option("--limit", "-l", help="Max results")] = 50,
    output: OutputFormat = "table",
) -> None:
    """Search CAs and certificates."""
    try:
        client = get_client()
        result = get_search.sync(client=client, query=query, limit=limit)

        if result is None:
            print_error("Failed to search")
            raise typer.Exit(1)

        if output == "json":
            print_json(result.to_dict())
        else:
            print_search_results(result.to_dict())
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("health")
def health(output: OutputFormat = "table") -> None:
    """Check API health status."""
    try:
        result = unwrap(get_health.sync(client=get_client()), what="Health check")
        data = result.to_dict()
        print_json(data) if output == "json" else print_kv(data, title="API Health")
        if data.get("status") == "ok":
            print_success("API is healthy")
        else:
            print_error(f"API reports status '{data.get('status')}'")
            raise typer.Exit(1)
    except typer.Exit:
        raise
    except Exception as e:
        print_error(f"API health check failed: {e}")
        raise typer.Exit(1)


@app.command("config")
def show_config() -> None:
    """Show current configuration (credentials are masked)."""
    from .config import get_settings

    settings = get_settings()

    table = Table(title="PKI CLI Configuration", show_header=False)
    table.add_column("Setting", style="cyan")
    table.add_column("Value")

    if settings.token:
        auth_mode = "static bearer token (PKI_TOKEN)"
    elif settings.has_oidc:
        auth_mode = "OIDC client credentials"
    else:
        auth_mode = "[yellow]anonymous[/yellow] (only works when the server has OIDC disabled)"

    table.add_row("API URL", settings.api_url or "[red]Not set[/red]")
    table.add_row("Auth Mode", auth_mode)
    table.add_row("OIDC URL", settings.oidc_url or "[dim]Not set[/dim]")
    table.add_row("Client ID", settings.client_id or "[dim]Not set[/dim]")
    table.add_row(
        "Client Secret",
        f"{settings.client_secret[:4]}****" if settings.client_secret else "[dim]Not set[/dim]",
    )
    table.add_row("Bearer Token", f"{settings.token[:6]}****" if settings.token else "[dim]Not set[/dim]")
    table.add_row("Token Cache", str(settings.token_cache_file))
    table.add_row("CLI Version", f"{__version__} (for PKI Manager {PKI_MANAGER_VERSION}, API v{API_VERSION})")

    console.print(table)

    if not settings.api_url:
        console.print("\n[red]PKI_API_URL is required.[/red] Set it via environment, .env, or --api-url.")
        return

    # A half-filled OIDC block silently downgrades to anonymous — call it out.
    oidc_given = [bool(settings.oidc_url), bool(settings.client_id), bool(settings.client_secret)]
    if any(oidc_given) and not all(oidc_given):
        console.print(
            "\n[yellow]Warning: incomplete OIDC configuration.[/yellow] "
            "Set PKI_OIDC_URL, PKI_CLIENT_ID and PKI_CLIENT_SECRET together."
        )


@app.command("login")
def login() -> None:
    """Test authentication and cache token."""
    try:
        from .client import get_wrapper
        from .config import get_settings

        settings = get_settings()
        if not settings.has_oidc:
            mode = "a static PKI_TOKEN" if settings.token else "anonymous access"
            print_error(f"Nothing to log in with — the CLI is configured for {mode}.")
            raise typer.Exit(1)

        wrapper = get_wrapper()
        wrapper.token_manager.clear_cache()  # Clear any cached token
        wrapper.token_manager.get_token()  # Try to get a fresh token
        print_success("Authentication successful! Token cached.")
    except typer.Exit:
        raise
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Authentication failed: {e}")
        raise typer.Exit(1)


@app.command("logout")
def logout() -> None:
    """Clear cached authentication token."""
    from .client import get_wrapper

    wrapper = get_wrapper()
    wrapper.token_manager.clear_cache()
    print_success("Token cache cleared.")


if __name__ == "__main__":
    app()
