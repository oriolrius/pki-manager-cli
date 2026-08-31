from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_ssh_hosts_id_response_200 import GetSshHostsIdResponse200
from ...models.get_ssh_hosts_id_response_400 import GetSshHostsIdResponse400
from ...models.get_ssh_hosts_id_response_500 import GetSshHostsIdResponse500
from ...types import Response


def _get_kwargs(
    id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/ssh/hosts/{id}".format(
            id=quote(str(id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    GetSshHostsIdResponse200
    | GetSshHostsIdResponse400
    | GetSshHostsIdResponse500
    | None
):
    if response.status_code == 200:
        response_200 = GetSshHostsIdResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = GetSshHostsIdResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = GetSshHostsIdResponse500.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    GetSshHostsIdResponse200 | GetSshHostsIdResponse400 | GetSshHostsIdResponse500
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[
    GetSshHostsIdResponse200 | GetSshHostsIdResponse400 | GetSshHostsIdResponse500
]:
    """Get one host

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetSshHostsIdResponse200 | GetSshHostsIdResponse400 | GetSshHostsIdResponse500]
    """

    kwargs = _get_kwargs(
        id=id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: str,
    *,
    client: AuthenticatedClient | Client,
) -> (
    GetSshHostsIdResponse200
    | GetSshHostsIdResponse400
    | GetSshHostsIdResponse500
    | None
):
    """Get one host

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetSshHostsIdResponse200 | GetSshHostsIdResponse400 | GetSshHostsIdResponse500
    """

    return sync_detailed(
        id=id,
        client=client,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[
    GetSshHostsIdResponse200 | GetSshHostsIdResponse400 | GetSshHostsIdResponse500
]:
    """Get one host

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetSshHostsIdResponse200 | GetSshHostsIdResponse400 | GetSshHostsIdResponse500]
    """

    kwargs = _get_kwargs(
        id=id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient | Client,
) -> (
    GetSshHostsIdResponse200
    | GetSshHostsIdResponse400
    | GetSshHostsIdResponse500
    | None
):
    """Get one host

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetSshHostsIdResponse200 | GetSshHostsIdResponse400 | GetSshHostsIdResponse500
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
        )
    ).parsed
