from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_ssh_identities_id_collisions_response_200_item import (
    GetSshIdentitiesIdCollisionsResponse200Item,
)
from ...models.get_ssh_identities_id_collisions_response_400 import (
    GetSshIdentitiesIdCollisionsResponse400,
)
from ...models.get_ssh_identities_id_collisions_response_500 import (
    GetSshIdentitiesIdCollisionsResponse500,
)
from ...types import Response


def _get_kwargs(
    id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/ssh/identities/{id}/collisions".format(
            id=quote(str(id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    GetSshIdentitiesIdCollisionsResponse400
    | GetSshIdentitiesIdCollisionsResponse500
    | list[GetSshIdentitiesIdCollisionsResponse200Item]
    | None
):
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = GetSshIdentitiesIdCollisionsResponse200Item.from_dict(
                response_200_item_data
            )

            response_200.append(response_200_item)

        return response_200

    if response.status_code == 400:
        response_400 = GetSshIdentitiesIdCollisionsResponse400.from_dict(
            response.json()
        )

        return response_400

    if response.status_code == 500:
        response_500 = GetSshIdentitiesIdCollisionsResponse500.from_dict(
            response.json()
        )

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    GetSshIdentitiesIdCollisionsResponse400
    | GetSshIdentitiesIdCollisionsResponse500
    | list[GetSshIdentitiesIdCollisionsResponse200Item]
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
    GetSshIdentitiesIdCollisionsResponse400
    | GetSshIdentitiesIdCollisionsResponse500
    | list[GetSshIdentitiesIdCollisionsResponse200Item]
]:
    """Identities sharing a certified public key with this one (over-block pre-check)

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetSshIdentitiesIdCollisionsResponse400 | GetSshIdentitiesIdCollisionsResponse500 | list[GetSshIdentitiesIdCollisionsResponse200Item]]
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
    GetSshIdentitiesIdCollisionsResponse400
    | GetSshIdentitiesIdCollisionsResponse500
    | list[GetSshIdentitiesIdCollisionsResponse200Item]
    | None
):
    """Identities sharing a certified public key with this one (over-block pre-check)

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetSshIdentitiesIdCollisionsResponse400 | GetSshIdentitiesIdCollisionsResponse500 | list[GetSshIdentitiesIdCollisionsResponse200Item]
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
    GetSshIdentitiesIdCollisionsResponse400
    | GetSshIdentitiesIdCollisionsResponse500
    | list[GetSshIdentitiesIdCollisionsResponse200Item]
]:
    """Identities sharing a certified public key with this one (over-block pre-check)

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetSshIdentitiesIdCollisionsResponse400 | GetSshIdentitiesIdCollisionsResponse500 | list[GetSshIdentitiesIdCollisionsResponse200Item]]
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
    GetSshIdentitiesIdCollisionsResponse400
    | GetSshIdentitiesIdCollisionsResponse500
    | list[GetSshIdentitiesIdCollisionsResponse200Item]
    | None
):
    """Identities sharing a certified public key with this one (over-block pre-check)

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetSshIdentitiesIdCollisionsResponse400 | GetSshIdentitiesIdCollisionsResponse500 | list[GetSshIdentitiesIdCollisionsResponse200Item]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
        )
    ).parsed
