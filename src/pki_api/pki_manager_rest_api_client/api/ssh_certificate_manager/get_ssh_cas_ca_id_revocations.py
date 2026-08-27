from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_ssh_cas_ca_id_revocations_response_200_item import (
    GetSshCasCaIdRevocationsResponse200Item,
)
from ...models.get_ssh_cas_ca_id_revocations_response_400 import (
    GetSshCasCaIdRevocationsResponse400,
)
from ...models.get_ssh_cas_ca_id_revocations_response_500 import (
    GetSshCasCaIdRevocationsResponse500,
)
from ...types import Response


def _get_kwargs(
    ca_id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/ssh/cas/{ca_id}/revocations".format(
            ca_id=quote(str(ca_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    GetSshCasCaIdRevocationsResponse400
    | GetSshCasCaIdRevocationsResponse500
    | list[GetSshCasCaIdRevocationsResponse200Item]
    | None
):
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = GetSshCasCaIdRevocationsResponse200Item.from_dict(
                response_200_item_data
            )

            response_200.append(response_200_item)

        return response_200

    if response.status_code == 400:
        response_400 = GetSshCasCaIdRevocationsResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = GetSshCasCaIdRevocationsResponse500.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    GetSshCasCaIdRevocationsResponse400
    | GetSshCasCaIdRevocationsResponse500
    | list[GetSshCasCaIdRevocationsResponse200Item]
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
    GetSshCasCaIdRevocationsResponse400
    | GetSshCasCaIdRevocationsResponse500
    | list[GetSshCasCaIdRevocationsResponse200Item]
]:
    """List revocations for a CA

    Args:
        ca_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetSshCasCaIdRevocationsResponse400 | GetSshCasCaIdRevocationsResponse500 | list[GetSshCasCaIdRevocationsResponse200Item]]
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
    GetSshCasCaIdRevocationsResponse400
    | GetSshCasCaIdRevocationsResponse500
    | list[GetSshCasCaIdRevocationsResponse200Item]
    | None
):
    """List revocations for a CA

    Args:
        ca_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetSshCasCaIdRevocationsResponse400 | GetSshCasCaIdRevocationsResponse500 | list[GetSshCasCaIdRevocationsResponse200Item]
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
    GetSshCasCaIdRevocationsResponse400
    | GetSshCasCaIdRevocationsResponse500
    | list[GetSshCasCaIdRevocationsResponse200Item]
]:
    """List revocations for a CA

    Args:
        ca_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetSshCasCaIdRevocationsResponse400 | GetSshCasCaIdRevocationsResponse500 | list[GetSshCasCaIdRevocationsResponse200Item]]
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
    GetSshCasCaIdRevocationsResponse400
    | GetSshCasCaIdRevocationsResponse500
    | list[GetSshCasCaIdRevocationsResponse200Item]
    | None
):
    """List revocations for a CA

    Args:
        ca_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetSshCasCaIdRevocationsResponse400 | GetSshCasCaIdRevocationsResponse500 | list[GetSshCasCaIdRevocationsResponse200Item]
    """

    return (
        await asyncio_detailed(
            ca_id=ca_id,
            client=client,
        )
    ).parsed
