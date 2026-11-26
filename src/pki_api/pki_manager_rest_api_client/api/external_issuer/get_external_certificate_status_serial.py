from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_external_certificate_status_serial_response_200 import (
    GetExternalCertificateStatusSerialResponse200,
)
from ...types import Response


def _get_kwargs(
    serial: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/external/certificate-status/{serial}".format(
            serial=quote(str(serial), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetExternalCertificateStatusSerialResponse200 | None:
    if response.status_code == 200:
        response_200 = GetExternalCertificateStatusSerialResponse200.from_dict(
            response.json()
        )

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetExternalCertificateStatusSerialResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    serial: str,
    *,
    client: AuthenticatedClient,
) -> Response[GetExternalCertificateStatusSerialResponse200]:
    """Check whether a service-owned certificate is active for SCEP renewal

    Args:
        serial (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetExternalCertificateStatusSerialResponse200]
    """

    kwargs = _get_kwargs(
        serial=serial,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    serial: str,
    *,
    client: AuthenticatedClient,
) -> GetExternalCertificateStatusSerialResponse200 | None:
    """Check whether a service-owned certificate is active for SCEP renewal

    Args:
        serial (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetExternalCertificateStatusSerialResponse200
    """

    return sync_detailed(
        serial=serial,
        client=client,
    ).parsed


async def asyncio_detailed(
    serial: str,
    *,
    client: AuthenticatedClient,
) -> Response[GetExternalCertificateStatusSerialResponse200]:
    """Check whether a service-owned certificate is active for SCEP renewal

    Args:
        serial (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetExternalCertificateStatusSerialResponse200]
    """

    kwargs = _get_kwargs(
        serial=serial,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    serial: str,
    *,
    client: AuthenticatedClient,
) -> GetExternalCertificateStatusSerialResponse200 | None:
    """Check whether a service-owned certificate is active for SCEP renewal

    Args:
        serial (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetExternalCertificateStatusSerialResponse200
    """

    return (
        await asyncio_detailed(
            serial=serial,
            client=client,
        )
    ).parsed
