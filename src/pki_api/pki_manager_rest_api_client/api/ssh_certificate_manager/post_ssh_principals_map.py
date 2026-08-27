from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_ssh_principals_map_body import PostSshPrincipalsMapBody
from ...models.post_ssh_principals_map_response_200 import (
    PostSshPrincipalsMapResponse200,
)
from ...models.post_ssh_principals_map_response_400 import (
    PostSshPrincipalsMapResponse400,
)
from ...models.post_ssh_principals_map_response_500 import (
    PostSshPrincipalsMapResponse500,
)
from ...types import Response


def _get_kwargs(
    *,
    body: PostSshPrincipalsMapBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/ssh/principals/map",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    PostSshPrincipalsMapResponse200
    | PostSshPrincipalsMapResponse400
    | PostSshPrincipalsMapResponse500
    | None
):
    if response.status_code == 200:
        response_200 = PostSshPrincipalsMapResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = PostSshPrincipalsMapResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = PostSshPrincipalsMapResponse500.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    PostSshPrincipalsMapResponse200
    | PostSshPrincipalsMapResponse400
    | PostSshPrincipalsMapResponse500
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
    body: PostSshPrincipalsMapBody,
) -> Response[
    PostSshPrincipalsMapResponse200
    | PostSshPrincipalsMapResponse400
    | PostSshPrincipalsMapResponse500
]:
    """Map a principal to a local account on a host

    Args:
        body (PostSshPrincipalsMapBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostSshPrincipalsMapResponse200 | PostSshPrincipalsMapResponse400 | PostSshPrincipalsMapResponse500]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: PostSshPrincipalsMapBody,
) -> (
    PostSshPrincipalsMapResponse200
    | PostSshPrincipalsMapResponse400
    | PostSshPrincipalsMapResponse500
    | None
):
    """Map a principal to a local account on a host

    Args:
        body (PostSshPrincipalsMapBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostSshPrincipalsMapResponse200 | PostSshPrincipalsMapResponse400 | PostSshPrincipalsMapResponse500
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PostSshPrincipalsMapBody,
) -> Response[
    PostSshPrincipalsMapResponse200
    | PostSshPrincipalsMapResponse400
    | PostSshPrincipalsMapResponse500
]:
    """Map a principal to a local account on a host

    Args:
        body (PostSshPrincipalsMapBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostSshPrincipalsMapResponse200 | PostSshPrincipalsMapResponse400 | PostSshPrincipalsMapResponse500]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: PostSshPrincipalsMapBody,
) -> (
    PostSshPrincipalsMapResponse200
    | PostSshPrincipalsMapResponse400
    | PostSshPrincipalsMapResponse500
    | None
):
    """Map a principal to a local account on a host

    Args:
        body (PostSshPrincipalsMapBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostSshPrincipalsMapResponse200 | PostSshPrincipalsMapResponse400 | PostSshPrincipalsMapResponse500
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
