from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_ssh_principals_id_response_200 import (
    DeleteSshPrincipalsIdResponse200,
)
from ...models.delete_ssh_principals_id_response_400 import (
    DeleteSshPrincipalsIdResponse400,
)
from ...models.delete_ssh_principals_id_response_500 import (
    DeleteSshPrincipalsIdResponse500,
)
from ...types import Response


def _get_kwargs(
    id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/ssh/principals/{id}".format(
            id=quote(str(id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    DeleteSshPrincipalsIdResponse200
    | DeleteSshPrincipalsIdResponse400
    | DeleteSshPrincipalsIdResponse500
    | None
):
    if response.status_code == 200:
        response_200 = DeleteSshPrincipalsIdResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = DeleteSshPrincipalsIdResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = DeleteSshPrincipalsIdResponse500.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    DeleteSshPrincipalsIdResponse200
    | DeleteSshPrincipalsIdResponse400
    | DeleteSshPrincipalsIdResponse500
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
    DeleteSshPrincipalsIdResponse200
    | DeleteSshPrincipalsIdResponse400
    | DeleteSshPrincipalsIdResponse500
]:
    """Delete a principal (rejected while entitlements or host maps reference it)

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteSshPrincipalsIdResponse200 | DeleteSshPrincipalsIdResponse400 | DeleteSshPrincipalsIdResponse500]
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
    DeleteSshPrincipalsIdResponse200
    | DeleteSshPrincipalsIdResponse400
    | DeleteSshPrincipalsIdResponse500
    | None
):
    """Delete a principal (rejected while entitlements or host maps reference it)

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteSshPrincipalsIdResponse200 | DeleteSshPrincipalsIdResponse400 | DeleteSshPrincipalsIdResponse500
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
    DeleteSshPrincipalsIdResponse200
    | DeleteSshPrincipalsIdResponse400
    | DeleteSshPrincipalsIdResponse500
]:
    """Delete a principal (rejected while entitlements or host maps reference it)

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteSshPrincipalsIdResponse200 | DeleteSshPrincipalsIdResponse400 | DeleteSshPrincipalsIdResponse500]
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
    DeleteSshPrincipalsIdResponse200
    | DeleteSshPrincipalsIdResponse400
    | DeleteSshPrincipalsIdResponse500
    | None
):
    """Delete a principal (rejected while entitlements or host maps reference it)

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteSshPrincipalsIdResponse200 | DeleteSshPrincipalsIdResponse400 | DeleteSshPrincipalsIdResponse500
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
        )
    ).parsed
