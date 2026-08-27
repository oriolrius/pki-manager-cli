from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_ssh_tokens_response_200_item import GetSshTokensResponse200Item
from ...models.get_ssh_tokens_response_400 import GetSshTokensResponse400
from ...models.get_ssh_tokens_response_500 import GetSshTokensResponse500
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/ssh/tokens",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    GetSshTokensResponse400
    | GetSshTokensResponse500
    | list[GetSshTokensResponse200Item]
    | None
):
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = GetSshTokensResponse200Item.from_dict(
                response_200_item_data
            )

            response_200.append(response_200_item)

        return response_200

    if response.status_code == 400:
        response_400 = GetSshTokensResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = GetSshTokensResponse500.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    GetSshTokensResponse400
    | GetSshTokensResponse500
    | list[GetSshTokensResponse200Item]
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
    GetSshTokensResponse400
    | GetSshTokensResponse500
    | list[GetSshTokensResponse200Item]
]:
    """List fleet tokens (metadata only, no secrets)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetSshTokensResponse400 | GetSshTokensResponse500 | list[GetSshTokensResponse200Item]]
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
    GetSshTokensResponse400
    | GetSshTokensResponse500
    | list[GetSshTokensResponse200Item]
    | None
):
    """List fleet tokens (metadata only, no secrets)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetSshTokensResponse400 | GetSshTokensResponse500 | list[GetSshTokensResponse200Item]
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[
    GetSshTokensResponse400
    | GetSshTokensResponse500
    | list[GetSshTokensResponse200Item]
]:
    """List fleet tokens (metadata only, no secrets)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetSshTokensResponse400 | GetSshTokensResponse500 | list[GetSshTokensResponse200Item]]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
) -> (
    GetSshTokensResponse400
    | GetSshTokensResponse500
    | list[GetSshTokensResponse200Item]
    | None
):
    """List fleet tokens (metadata only, no secrets)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetSshTokensResponse400 | GetSshTokensResponse500 | list[GetSshTokensResponse200Item]
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
