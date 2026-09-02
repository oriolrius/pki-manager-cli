from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_ssh_zones_body import PostSshZonesBody
from ...models.post_ssh_zones_response_200 import PostSshZonesResponse200
from ...models.post_ssh_zones_response_400 import PostSshZonesResponse400
from ...models.post_ssh_zones_response_500 import PostSshZonesResponse500
from ...types import Response


def _get_kwargs(
    *,
    body: PostSshZonesBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/ssh/zones",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PostSshZonesResponse200 | PostSshZonesResponse400 | PostSshZonesResponse500 | None:
    if response.status_code == 200:
        response_200 = PostSshZonesResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = PostSshZonesResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = PostSshZonesResponse500.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    PostSshZonesResponse200 | PostSshZonesResponse400 | PostSshZonesResponse500
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
    body: PostSshZonesBody,
) -> Response[
    PostSshZonesResponse200 | PostSshZonesResponse400 | PostSshZonesResponse500
]:
    """Create a zone

    Args:
        body (PostSshZonesBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostSshZonesResponse200 | PostSshZonesResponse400 | PostSshZonesResponse500]
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
    body: PostSshZonesBody,
) -> PostSshZonesResponse200 | PostSshZonesResponse400 | PostSshZonesResponse500 | None:
    """Create a zone

    Args:
        body (PostSshZonesBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostSshZonesResponse200 | PostSshZonesResponse400 | PostSshZonesResponse500
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PostSshZonesBody,
) -> Response[
    PostSshZonesResponse200 | PostSshZonesResponse400 | PostSshZonesResponse500
]:
    """Create a zone

    Args:
        body (PostSshZonesBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostSshZonesResponse200 | PostSshZonesResponse400 | PostSshZonesResponse500]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: PostSshZonesBody,
) -> PostSshZonesResponse200 | PostSshZonesResponse400 | PostSshZonesResponse500 | None:
    """Create a zone

    Args:
        body (PostSshZonesBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostSshZonesResponse200 | PostSshZonesResponse400 | PostSshZonesResponse500
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
