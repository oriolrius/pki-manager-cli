from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_ssh_hosts_id_auth_principals_pushed_response_200 import (
    PostSshHostsIdAuthPrincipalsPushedResponse200,
)
from ...models.post_ssh_hosts_id_auth_principals_pushed_response_400 import (
    PostSshHostsIdAuthPrincipalsPushedResponse400,
)
from ...models.post_ssh_hosts_id_auth_principals_pushed_response_500 import (
    PostSshHostsIdAuthPrincipalsPushedResponse500,
)
from ...types import Response


def _get_kwargs(
    id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/ssh/hosts/{id}/auth-principals/pushed".format(
            id=quote(str(id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    PostSshHostsIdAuthPrincipalsPushedResponse200
    | PostSshHostsIdAuthPrincipalsPushedResponse400
    | PostSshHostsIdAuthPrincipalsPushedResponse500
    | None
):
    if response.status_code == 200:
        response_200 = PostSshHostsIdAuthPrincipalsPushedResponse200.from_dict(
            response.json()
        )

        return response_200

    if response.status_code == 400:
        response_400 = PostSshHostsIdAuthPrincipalsPushedResponse400.from_dict(
            response.json()
        )

        return response_400

    if response.status_code == 500:
        response_500 = PostSshHostsIdAuthPrincipalsPushedResponse500.from_dict(
            response.json()
        )

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    PostSshHostsIdAuthPrincipalsPushedResponse200
    | PostSshHostsIdAuthPrincipalsPushedResponse400
    | PostSshHostsIdAuthPrincipalsPushedResponse500
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
    PostSshHostsIdAuthPrincipalsPushedResponse200
    | PostSshHostsIdAuthPrincipalsPushedResponse400
    | PostSshHostsIdAuthPrincipalsPushedResponse500
]:
    """Mark a host's rendered principal files as pushed (clears Stale)

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostSshHostsIdAuthPrincipalsPushedResponse200 | PostSshHostsIdAuthPrincipalsPushedResponse400 | PostSshHostsIdAuthPrincipalsPushedResponse500]
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
    PostSshHostsIdAuthPrincipalsPushedResponse200
    | PostSshHostsIdAuthPrincipalsPushedResponse400
    | PostSshHostsIdAuthPrincipalsPushedResponse500
    | None
):
    """Mark a host's rendered principal files as pushed (clears Stale)

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostSshHostsIdAuthPrincipalsPushedResponse200 | PostSshHostsIdAuthPrincipalsPushedResponse400 | PostSshHostsIdAuthPrincipalsPushedResponse500
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
    PostSshHostsIdAuthPrincipalsPushedResponse200
    | PostSshHostsIdAuthPrincipalsPushedResponse400
    | PostSshHostsIdAuthPrincipalsPushedResponse500
]:
    """Mark a host's rendered principal files as pushed (clears Stale)

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostSshHostsIdAuthPrincipalsPushedResponse200 | PostSshHostsIdAuthPrincipalsPushedResponse400 | PostSshHostsIdAuthPrincipalsPushedResponse500]
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
    PostSshHostsIdAuthPrincipalsPushedResponse200
    | PostSshHostsIdAuthPrincipalsPushedResponse400
    | PostSshHostsIdAuthPrincipalsPushedResponse500
    | None
):
    """Mark a host's rendered principal files as pushed (clears Stale)

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostSshHostsIdAuthPrincipalsPushedResponse200 | PostSshHostsIdAuthPrincipalsPushedResponse400 | PostSshHostsIdAuthPrincipalsPushedResponse500
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
        )
    ).parsed
