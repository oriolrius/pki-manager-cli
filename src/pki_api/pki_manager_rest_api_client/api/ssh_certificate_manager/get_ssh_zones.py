from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_ssh_zones_response_200_item import GetSshZonesResponse200Item
from ...models.get_ssh_zones_response_400 import GetSshZonesResponse400
from ...models.get_ssh_zones_response_500 import GetSshZonesResponse500
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/ssh/zones",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    GetSshZonesResponse400
    | GetSshZonesResponse500
    | list[GetSshZonesResponse200Item]
    | None
):
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = GetSshZonesResponse200Item.from_dict(
                response_200_item_data
            )

            response_200.append(response_200_item)

        return response_200

    if response.status_code == 400:
        response_400 = GetSshZonesResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = GetSshZonesResponse500.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    GetSshZonesResponse400 | GetSshZonesResponse500 | list[GetSshZonesResponse200Item]
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
    GetSshZonesResponse400 | GetSshZonesResponse500 | list[GetSshZonesResponse200Item]
]:
    """List zones (?includeArchived=true to include archived)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetSshZonesResponse400 | GetSshZonesResponse500 | list[GetSshZonesResponse200Item]]
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
    GetSshZonesResponse400
    | GetSshZonesResponse500
    | list[GetSshZonesResponse200Item]
    | None
):
    """List zones (?includeArchived=true to include archived)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetSshZonesResponse400 | GetSshZonesResponse500 | list[GetSshZonesResponse200Item]
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[
    GetSshZonesResponse400 | GetSshZonesResponse500 | list[GetSshZonesResponse200Item]
]:
    """List zones (?includeArchived=true to include archived)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetSshZonesResponse400 | GetSshZonesResponse500 | list[GetSshZonesResponse200Item]]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
) -> (
    GetSshZonesResponse400
    | GetSshZonesResponse500
    | list[GetSshZonesResponse200Item]
    | None
):
    """List zones (?includeArchived=true to include archived)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetSshZonesResponse400 | GetSshZonesResponse500 | list[GetSshZonesResponse200Item]
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
