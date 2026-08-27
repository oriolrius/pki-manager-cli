from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_ssh_hosts_body import PostSshHostsBody
from ...models.post_ssh_hosts_response_200 import PostSshHostsResponse200
from ...models.post_ssh_hosts_response_400 import PostSshHostsResponse400
from ...models.post_ssh_hosts_response_500 import PostSshHostsResponse500
from ...types import Response


def _get_kwargs(
    *,
    body: PostSshHostsBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/ssh/hosts",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PostSshHostsResponse200 | PostSshHostsResponse400 | PostSshHostsResponse500 | None:
    if response.status_code == 200:
        response_200 = PostSshHostsResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = PostSshHostsResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = PostSshHostsResponse500.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    PostSshHostsResponse200 | PostSshHostsResponse400 | PostSshHostsResponse500
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
    body: PostSshHostsBody,
) -> Response[
    PostSshHostsResponse200 | PostSshHostsResponse400 | PostSshHostsResponse500
]:
    """Register a host by its public host key

    Args:
        body (PostSshHostsBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostSshHostsResponse200 | PostSshHostsResponse400 | PostSshHostsResponse500]
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
    body: PostSshHostsBody,
) -> PostSshHostsResponse200 | PostSshHostsResponse400 | PostSshHostsResponse500 | None:
    """Register a host by its public host key

    Args:
        body (PostSshHostsBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostSshHostsResponse200 | PostSshHostsResponse400 | PostSshHostsResponse500
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PostSshHostsBody,
) -> Response[
    PostSshHostsResponse200 | PostSshHostsResponse400 | PostSshHostsResponse500
]:
    """Register a host by its public host key

    Args:
        body (PostSshHostsBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostSshHostsResponse200 | PostSshHostsResponse400 | PostSshHostsResponse500]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: PostSshHostsBody,
) -> PostSshHostsResponse200 | PostSshHostsResponse400 | PostSshHostsResponse500 | None:
    """Register a host by its public host key

    Args:
        body (PostSshHostsBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostSshHostsResponse200 | PostSshHostsResponse400 | PostSshHostsResponse500
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
