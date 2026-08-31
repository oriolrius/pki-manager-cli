from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_ssh_hosts_id_revoke_body import PostSshHostsIdRevokeBody
from ...models.post_ssh_hosts_id_revoke_response_200 import (
    PostSshHostsIdRevokeResponse200,
)
from ...models.post_ssh_hosts_id_revoke_response_400 import (
    PostSshHostsIdRevokeResponse400,
)
from ...models.post_ssh_hosts_id_revoke_response_500 import (
    PostSshHostsIdRevokeResponse500,
)
from ...types import Response


def _get_kwargs(
    id: str,
    *,
    body: PostSshHostsIdRevokeBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/ssh/hosts/{id}/revoke".format(
            id=quote(str(id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    PostSshHostsIdRevokeResponse200
    | PostSshHostsIdRevokeResponse400
    | PostSshHostsIdRevokeResponse500
    | None
):
    if response.status_code == 200:
        response_200 = PostSshHostsIdRevokeResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = PostSshHostsIdRevokeResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = PostSshHostsIdRevokeResponse500.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    PostSshHostsIdRevokeResponse200
    | PostSshHostsIdRevokeResponse400
    | PostSshHostsIdRevokeResponse500
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
    body: PostSshHostsIdRevokeBody,
) -> Response[
    PostSshHostsIdRevokeResponse200
    | PostSshHostsIdRevokeResponse400
    | PostSshHostsIdRevokeResponse500
]:
    """Revoke the host's current certificate

    Args:
        id (str):
        body (PostSshHostsIdRevokeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostSshHostsIdRevokeResponse200 | PostSshHostsIdRevokeResponse400 | PostSshHostsIdRevokeResponse500]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostSshHostsIdRevokeBody,
) -> (
    PostSshHostsIdRevokeResponse200
    | PostSshHostsIdRevokeResponse400
    | PostSshHostsIdRevokeResponse500
    | None
):
    """Revoke the host's current certificate

    Args:
        id (str):
        body (PostSshHostsIdRevokeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostSshHostsIdRevokeResponse200 | PostSshHostsIdRevokeResponse400 | PostSshHostsIdRevokeResponse500
    """

    return sync_detailed(
        id=id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostSshHostsIdRevokeBody,
) -> Response[
    PostSshHostsIdRevokeResponse200
    | PostSshHostsIdRevokeResponse400
    | PostSshHostsIdRevokeResponse500
]:
    """Revoke the host's current certificate

    Args:
        id (str):
        body (PostSshHostsIdRevokeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostSshHostsIdRevokeResponse200 | PostSshHostsIdRevokeResponse400 | PostSshHostsIdRevokeResponse500]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostSshHostsIdRevokeBody,
) -> (
    PostSshHostsIdRevokeResponse200
    | PostSshHostsIdRevokeResponse400
    | PostSshHostsIdRevokeResponse500
    | None
):
    """Revoke the host's current certificate

    Args:
        id (str):
        body (PostSshHostsIdRevokeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostSshHostsIdRevokeResponse200 | PostSshHostsIdRevokeResponse400 | PostSshHostsIdRevokeResponse500
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
