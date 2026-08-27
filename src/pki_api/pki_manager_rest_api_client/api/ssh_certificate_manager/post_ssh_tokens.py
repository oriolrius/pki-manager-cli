from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_ssh_tokens_body import PostSshTokensBody
from ...models.post_ssh_tokens_response_200 import PostSshTokensResponse200
from ...models.post_ssh_tokens_response_400 import PostSshTokensResponse400
from ...models.post_ssh_tokens_response_500 import PostSshTokensResponse500
from ...types import Response


def _get_kwargs(
    *,
    body: PostSshTokensBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/ssh/tokens",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    PostSshTokensResponse200
    | PostSshTokensResponse400
    | PostSshTokensResponse500
    | None
):
    if response.status_code == 200:
        response_200 = PostSshTokensResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = PostSshTokensResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = PostSshTokensResponse500.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    PostSshTokensResponse200 | PostSshTokensResponse400 | PostSshTokensResponse500
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
    body: PostSshTokensBody,
) -> Response[
    PostSshTokensResponse200 | PostSshTokensResponse400 | PostSshTokensResponse500
]:
    """Mint a fleet token (plaintext shown once)

    Args:
        body (PostSshTokensBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostSshTokensResponse200 | PostSshTokensResponse400 | PostSshTokensResponse500]
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
    body: PostSshTokensBody,
) -> (
    PostSshTokensResponse200
    | PostSshTokensResponse400
    | PostSshTokensResponse500
    | None
):
    """Mint a fleet token (plaintext shown once)

    Args:
        body (PostSshTokensBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostSshTokensResponse200 | PostSshTokensResponse400 | PostSshTokensResponse500
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PostSshTokensBody,
) -> Response[
    PostSshTokensResponse200 | PostSshTokensResponse400 | PostSshTokensResponse500
]:
    """Mint a fleet token (plaintext shown once)

    Args:
        body (PostSshTokensBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostSshTokensResponse200 | PostSshTokensResponse400 | PostSshTokensResponse500]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: PostSshTokensBody,
) -> (
    PostSshTokensResponse200
    | PostSshTokensResponse400
    | PostSshTokensResponse500
    | None
):
    """Mint a fleet token (plaintext shown once)

    Args:
        body (PostSshTokensBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostSshTokensResponse200 | PostSshTokensResponse400 | PostSshTokensResponse500
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
