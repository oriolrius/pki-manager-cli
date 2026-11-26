from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_ssh_identities_id_grants_response_200_item import (
    GetSshIdentitiesIdGrantsResponse200Item,
)
from ...models.get_ssh_identities_id_grants_response_400 import (
    GetSshIdentitiesIdGrantsResponse400,
)
from ...models.get_ssh_identities_id_grants_response_500 import (
    GetSshIdentitiesIdGrantsResponse500,
)
from ...types import Response


def _get_kwargs(
    id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/ssh/identities/{id}/grants".format(
            id=quote(str(id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    GetSshIdentitiesIdGrantsResponse400
    | GetSshIdentitiesIdGrantsResponse500
    | list[GetSshIdentitiesIdGrantsResponse200Item]
    | None
):
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = GetSshIdentitiesIdGrantsResponse200Item.from_dict(
                response_200_item_data
            )

            response_200.append(response_200_item)

        return response_200

    if response.status_code == 400:
        response_400 = GetSshIdentitiesIdGrantsResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = GetSshIdentitiesIdGrantsResponse500.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    GetSshIdentitiesIdGrantsResponse400
    | GetSshIdentitiesIdGrantsResponse500
    | list[GetSshIdentitiesIdGrantsResponse200Item]
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
    GetSshIdentitiesIdGrantsResponse400
    | GetSshIdentitiesIdGrantsResponse500
    | list[GetSshIdentitiesIdGrantsResponse200Item]
]:
    """List the principals an identity is granted

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetSshIdentitiesIdGrantsResponse400 | GetSshIdentitiesIdGrantsResponse500 | list[GetSshIdentitiesIdGrantsResponse200Item]]
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
    GetSshIdentitiesIdGrantsResponse400
    | GetSshIdentitiesIdGrantsResponse500
    | list[GetSshIdentitiesIdGrantsResponse200Item]
    | None
):
    """List the principals an identity is granted

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetSshIdentitiesIdGrantsResponse400 | GetSshIdentitiesIdGrantsResponse500 | list[GetSshIdentitiesIdGrantsResponse200Item]
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
    GetSshIdentitiesIdGrantsResponse400
    | GetSshIdentitiesIdGrantsResponse500
    | list[GetSshIdentitiesIdGrantsResponse200Item]
]:
    """List the principals an identity is granted

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetSshIdentitiesIdGrantsResponse400 | GetSshIdentitiesIdGrantsResponse500 | list[GetSshIdentitiesIdGrantsResponse200Item]]
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
    GetSshIdentitiesIdGrantsResponse400
    | GetSshIdentitiesIdGrantsResponse500
    | list[GetSshIdentitiesIdGrantsResponse200Item]
    | None
):
    """List the principals an identity is granted

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetSshIdentitiesIdGrantsResponse400 | GetSshIdentitiesIdGrantsResponse500 | list[GetSshIdentitiesIdGrantsResponse200Item]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
        )
    ).parsed
