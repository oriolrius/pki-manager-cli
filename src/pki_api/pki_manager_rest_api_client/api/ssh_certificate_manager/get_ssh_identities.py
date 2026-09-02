from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_ssh_identities_response_200_item import (
    GetSshIdentitiesResponse200Item,
)
from ...models.get_ssh_identities_response_400 import GetSshIdentitiesResponse400
from ...models.get_ssh_identities_response_500 import GetSshIdentitiesResponse500
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/ssh/identities",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    GetSshIdentitiesResponse400
    | GetSshIdentitiesResponse500
    | list[GetSshIdentitiesResponse200Item]
    | None
):
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = GetSshIdentitiesResponse200Item.from_dict(
                response_200_item_data
            )

            response_200.append(response_200_item)

        return response_200

    if response.status_code == 400:
        response_400 = GetSshIdentitiesResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = GetSshIdentitiesResponse500.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    GetSshIdentitiesResponse400
    | GetSshIdentitiesResponse500
    | list[GetSshIdentitiesResponse200Item]
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
    GetSshIdentitiesResponse400
    | GetSshIdentitiesResponse500
    | list[GetSshIdentitiesResponse200Item]
]:
    """List user identities (optionally filter by ?zoneId=)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetSshIdentitiesResponse400 | GetSshIdentitiesResponse500 | list[GetSshIdentitiesResponse200Item]]
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
    GetSshIdentitiesResponse400
    | GetSshIdentitiesResponse500
    | list[GetSshIdentitiesResponse200Item]
    | None
):
    """List user identities (optionally filter by ?zoneId=)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetSshIdentitiesResponse400 | GetSshIdentitiesResponse500 | list[GetSshIdentitiesResponse200Item]
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[
    GetSshIdentitiesResponse400
    | GetSshIdentitiesResponse500
    | list[GetSshIdentitiesResponse200Item]
]:
    """List user identities (optionally filter by ?zoneId=)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetSshIdentitiesResponse400 | GetSshIdentitiesResponse500 | list[GetSshIdentitiesResponse200Item]]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
) -> (
    GetSshIdentitiesResponse400
    | GetSshIdentitiesResponse500
    | list[GetSshIdentitiesResponse200Item]
    | None
):
    """List user identities (optionally filter by ?zoneId=)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetSshIdentitiesResponse400 | GetSshIdentitiesResponse500 | list[GetSshIdentitiesResponse200Item]
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
