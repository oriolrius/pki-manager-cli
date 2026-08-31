from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_ssh_principals_stale_hosts_response_200_item import (
    GetSshPrincipalsStaleHostsResponse200Item,
)
from ...models.get_ssh_principals_stale_hosts_response_400 import (
    GetSshPrincipalsStaleHostsResponse400,
)
from ...models.get_ssh_principals_stale_hosts_response_500 import (
    GetSshPrincipalsStaleHostsResponse500,
)
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/ssh/principals/stale-hosts",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    GetSshPrincipalsStaleHostsResponse400
    | GetSshPrincipalsStaleHostsResponse500
    | list[GetSshPrincipalsStaleHostsResponse200Item]
    | None
):
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = GetSshPrincipalsStaleHostsResponse200Item.from_dict(
                response_200_item_data
            )

            response_200.append(response_200_item)

        return response_200

    if response.status_code == 400:
        response_400 = GetSshPrincipalsStaleHostsResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = GetSshPrincipalsStaleHostsResponse500.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    GetSshPrincipalsStaleHostsResponse400
    | GetSshPrincipalsStaleHostsResponse500
    | list[GetSshPrincipalsStaleHostsResponse200Item]
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[
    GetSshPrincipalsStaleHostsResponse400
    | GetSshPrincipalsStaleHostsResponse500
    | list[GetSshPrincipalsStaleHostsResponse200Item]
]:
    """Hosts whose principal maps changed after the last push

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetSshPrincipalsStaleHostsResponse400 | GetSshPrincipalsStaleHostsResponse500 | list[GetSshPrincipalsStaleHostsResponse200Item]]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
) -> (
    GetSshPrincipalsStaleHostsResponse400
    | GetSshPrincipalsStaleHostsResponse500
    | list[GetSshPrincipalsStaleHostsResponse200Item]
    | None
):
    """Hosts whose principal maps changed after the last push

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetSshPrincipalsStaleHostsResponse400 | GetSshPrincipalsStaleHostsResponse500 | list[GetSshPrincipalsStaleHostsResponse200Item]
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[
    GetSshPrincipalsStaleHostsResponse400
    | GetSshPrincipalsStaleHostsResponse500
    | list[GetSshPrincipalsStaleHostsResponse200Item]
]:
    """Hosts whose principal maps changed after the last push

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetSshPrincipalsStaleHostsResponse400 | GetSshPrincipalsStaleHostsResponse500 | list[GetSshPrincipalsStaleHostsResponse200Item]]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
) -> (
    GetSshPrincipalsStaleHostsResponse400
    | GetSshPrincipalsStaleHostsResponse500
    | list[GetSshPrincipalsStaleHostsResponse200Item]
    | None
):
    """Hosts whose principal maps changed after the last push

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetSshPrincipalsStaleHostsResponse400 | GetSshPrincipalsStaleHostsResponse500 | list[GetSshPrincipalsStaleHostsResponse200Item]
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
