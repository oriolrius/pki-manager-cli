from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_ssh_cas_ca_id_response_200 import GetSshCasCaIdResponse200
from ...models.get_ssh_cas_ca_id_response_400 import GetSshCasCaIdResponse400
from ...models.get_ssh_cas_ca_id_response_500 import GetSshCasCaIdResponse500
from ...types import Response


def _get_kwargs(
    ca_id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/ssh/cas/{ca_id}".format(
            ca_id=quote(str(ca_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    GetSshCasCaIdResponse200
    | GetSshCasCaIdResponse400
    | GetSshCasCaIdResponse500
    | None
):
    if response.status_code == 200:
        response_200 = GetSshCasCaIdResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = GetSshCasCaIdResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = GetSshCasCaIdResponse500.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    GetSshCasCaIdResponse200 | GetSshCasCaIdResponse400 | GetSshCasCaIdResponse500
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    ca_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[
    GetSshCasCaIdResponse200 | GetSshCasCaIdResponse400 | GetSshCasCaIdResponse500
]:
    """Get one SSH CA

    Args:
        ca_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetSshCasCaIdResponse200 | GetSshCasCaIdResponse400 | GetSshCasCaIdResponse500]
    """

    kwargs = _get_kwargs(
        ca_id=ca_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    ca_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> (
    GetSshCasCaIdResponse200
    | GetSshCasCaIdResponse400
    | GetSshCasCaIdResponse500
    | None
):
    """Get one SSH CA

    Args:
        ca_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetSshCasCaIdResponse200 | GetSshCasCaIdResponse400 | GetSshCasCaIdResponse500
    """

    return sync_detailed(
        ca_id=ca_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    ca_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[
    GetSshCasCaIdResponse200 | GetSshCasCaIdResponse400 | GetSshCasCaIdResponse500
]:
    """Get one SSH CA

    Args:
        ca_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetSshCasCaIdResponse200 | GetSshCasCaIdResponse400 | GetSshCasCaIdResponse500]
    """

    kwargs = _get_kwargs(
        ca_id=ca_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    ca_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> (
    GetSshCasCaIdResponse200
    | GetSshCasCaIdResponse400
    | GetSshCasCaIdResponse500
    | None
):
    """Get one SSH CA

    Args:
        ca_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetSshCasCaIdResponse200 | GetSshCasCaIdResponse400 | GetSshCasCaIdResponse500
    """

    return (
        await asyncio_detailed(
            ca_id=ca_id,
            client=client,
        )
    ).parsed
