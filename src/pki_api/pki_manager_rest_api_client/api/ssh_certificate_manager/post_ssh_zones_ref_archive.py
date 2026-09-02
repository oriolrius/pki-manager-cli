from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_ssh_zones_ref_archive_response_200 import (
    PostSshZonesRefArchiveResponse200,
)
from ...models.post_ssh_zones_ref_archive_response_400 import (
    PostSshZonesRefArchiveResponse400,
)
from ...models.post_ssh_zones_ref_archive_response_500 import (
    PostSshZonesRefArchiveResponse500,
)
from ...types import Response


def _get_kwargs(
    ref: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/ssh/zones/{ref}/archive".format(
            ref=quote(str(ref), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    PostSshZonesRefArchiveResponse200
    | PostSshZonesRefArchiveResponse400
    | PostSshZonesRefArchiveResponse500
    | None
):
    if response.status_code == 200:
        response_200 = PostSshZonesRefArchiveResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = PostSshZonesRefArchiveResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = PostSshZonesRefArchiveResponse500.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    PostSshZonesRefArchiveResponse200
    | PostSshZonesRefArchiveResponse400
    | PostSshZonesRefArchiveResponse500
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    ref: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[
    PostSshZonesRefArchiveResponse200
    | PostSshZonesRefArchiveResponse400
    | PostSshZonesRefArchiveResponse500
]:
    """Archive a zone (blocks new entities/issuance; keeps serving existing trust material)

    Args:
        ref (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostSshZonesRefArchiveResponse200 | PostSshZonesRefArchiveResponse400 | PostSshZonesRefArchiveResponse500]
    """

    kwargs = _get_kwargs(
        ref=ref,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    ref: str,
    *,
    client: AuthenticatedClient | Client,
) -> (
    PostSshZonesRefArchiveResponse200
    | PostSshZonesRefArchiveResponse400
    | PostSshZonesRefArchiveResponse500
    | None
):
    """Archive a zone (blocks new entities/issuance; keeps serving existing trust material)

    Args:
        ref (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostSshZonesRefArchiveResponse200 | PostSshZonesRefArchiveResponse400 | PostSshZonesRefArchiveResponse500
    """

    return sync_detailed(
        ref=ref,
        client=client,
    ).parsed


async def asyncio_detailed(
    ref: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[
    PostSshZonesRefArchiveResponse200
    | PostSshZonesRefArchiveResponse400
    | PostSshZonesRefArchiveResponse500
]:
    """Archive a zone (blocks new entities/issuance; keeps serving existing trust material)

    Args:
        ref (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostSshZonesRefArchiveResponse200 | PostSshZonesRefArchiveResponse400 | PostSshZonesRefArchiveResponse500]
    """

    kwargs = _get_kwargs(
        ref=ref,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    ref: str,
    *,
    client: AuthenticatedClient | Client,
) -> (
    PostSshZonesRefArchiveResponse200
    | PostSshZonesRefArchiveResponse400
    | PostSshZonesRefArchiveResponse500
    | None
):
    """Archive a zone (blocks new entities/issuance; keeps serving existing trust material)

    Args:
        ref (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostSshZonesRefArchiveResponse200 | PostSshZonesRefArchiveResponse400 | PostSshZonesRefArchiveResponse500
    """

    return (
        await asyncio_detailed(
            ref=ref,
            client=client,
        )
    ).parsed
