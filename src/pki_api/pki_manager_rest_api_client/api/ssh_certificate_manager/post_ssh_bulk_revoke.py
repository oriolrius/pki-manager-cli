from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_ssh_bulk_revoke_body import PostSshBulkRevokeBody
from ...models.post_ssh_bulk_revoke_response_200 import PostSshBulkRevokeResponse200
from ...models.post_ssh_bulk_revoke_response_400 import PostSshBulkRevokeResponse400
from ...models.post_ssh_bulk_revoke_response_500 import PostSshBulkRevokeResponse500
from ...types import Response


def _get_kwargs(
    *,
    body: PostSshBulkRevokeBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/ssh/bulk/revoke",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    PostSshBulkRevokeResponse200
    | PostSshBulkRevokeResponse400
    | PostSshBulkRevokeResponse500
    | None
):
    if response.status_code == 200:
        response_200 = PostSshBulkRevokeResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = PostSshBulkRevokeResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = PostSshBulkRevokeResponse500.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    PostSshBulkRevokeResponse200
    | PostSshBulkRevokeResponse400
    | PostSshBulkRevokeResponse500
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
    body: PostSshBulkRevokeBody,
) -> Response[
    PostSshBulkRevokeResponse200
    | PostSshBulkRevokeResponse400
    | PostSshBulkRevokeResponse500
]:
    """Revoke many certificates by id

    Args:
        body (PostSshBulkRevokeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostSshBulkRevokeResponse200 | PostSshBulkRevokeResponse400 | PostSshBulkRevokeResponse500]
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
    body: PostSshBulkRevokeBody,
) -> (
    PostSshBulkRevokeResponse200
    | PostSshBulkRevokeResponse400
    | PostSshBulkRevokeResponse500
    | None
):
    """Revoke many certificates by id

    Args:
        body (PostSshBulkRevokeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostSshBulkRevokeResponse200 | PostSshBulkRevokeResponse400 | PostSshBulkRevokeResponse500
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PostSshBulkRevokeBody,
) -> Response[
    PostSshBulkRevokeResponse200
    | PostSshBulkRevokeResponse400
    | PostSshBulkRevokeResponse500
]:
    """Revoke many certificates by id

    Args:
        body (PostSshBulkRevokeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostSshBulkRevokeResponse200 | PostSshBulkRevokeResponse400 | PostSshBulkRevokeResponse500]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: PostSshBulkRevokeBody,
) -> (
    PostSshBulkRevokeResponse200
    | PostSshBulkRevokeResponse400
    | PostSshBulkRevokeResponse500
    | None
):
    """Revoke many certificates by id

    Args:
        body (PostSshBulkRevokeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostSshBulkRevokeResponse200 | PostSshBulkRevokeResponse400 | PostSshBulkRevokeResponse500
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
