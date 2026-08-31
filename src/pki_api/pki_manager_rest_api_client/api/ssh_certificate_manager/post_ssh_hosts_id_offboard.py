from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_ssh_hosts_id_offboard_body import PostSshHostsIdOffboardBody
from ...models.post_ssh_hosts_id_offboard_response_200 import (
    PostSshHostsIdOffboardResponse200,
)
from ...models.post_ssh_hosts_id_offboard_response_400 import (
    PostSshHostsIdOffboardResponse400,
)
from ...models.post_ssh_hosts_id_offboard_response_500 import (
    PostSshHostsIdOffboardResponse500,
)
from ...types import Response


def _get_kwargs(
    id: str,
    *,
    body: PostSshHostsIdOffboardBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/ssh/hosts/{id}/offboard".format(
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
    PostSshHostsIdOffboardResponse200
    | PostSshHostsIdOffboardResponse400
    | PostSshHostsIdOffboardResponse500
    | None
):
    if response.status_code == 200:
        response_200 = PostSshHostsIdOffboardResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = PostSshHostsIdOffboardResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = PostSshHostsIdOffboardResponse500.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    PostSshHostsIdOffboardResponse200
    | PostSshHostsIdOffboardResponse400
    | PostSshHostsIdOffboardResponse500
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
    body: PostSshHostsIdOffboardBody,
) -> Response[
    PostSshHostsIdOffboardResponse200
    | PostSshHostsIdOffboardResponse400
    | PostSshHostsIdOffboardResponse500
]:
    """Offboard a host (terminal: retires its per-host KRL lineage)

    Args:
        id (str):
        body (PostSshHostsIdOffboardBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostSshHostsIdOffboardResponse200 | PostSshHostsIdOffboardResponse400 | PostSshHostsIdOffboardResponse500]
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
    body: PostSshHostsIdOffboardBody,
) -> (
    PostSshHostsIdOffboardResponse200
    | PostSshHostsIdOffboardResponse400
    | PostSshHostsIdOffboardResponse500
    | None
):
    """Offboard a host (terminal: retires its per-host KRL lineage)

    Args:
        id (str):
        body (PostSshHostsIdOffboardBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostSshHostsIdOffboardResponse200 | PostSshHostsIdOffboardResponse400 | PostSshHostsIdOffboardResponse500
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
    body: PostSshHostsIdOffboardBody,
) -> Response[
    PostSshHostsIdOffboardResponse200
    | PostSshHostsIdOffboardResponse400
    | PostSshHostsIdOffboardResponse500
]:
    """Offboard a host (terminal: retires its per-host KRL lineage)

    Args:
        id (str):
        body (PostSshHostsIdOffboardBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostSshHostsIdOffboardResponse200 | PostSshHostsIdOffboardResponse400 | PostSshHostsIdOffboardResponse500]
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
    body: PostSshHostsIdOffboardBody,
) -> (
    PostSshHostsIdOffboardResponse200
    | PostSshHostsIdOffboardResponse400
    | PostSshHostsIdOffboardResponse500
    | None
):
    """Offboard a host (terminal: retires its per-host KRL lineage)

    Args:
        id (str):
        body (PostSshHostsIdOffboardBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostSshHostsIdOffboardResponse200 | PostSshHostsIdOffboardResponse400 | PostSshHostsIdOffboardResponse500
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
