from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_external_ssh_hosts_fqdn_principals_pushed_body import (
    PostExternalSshHostsFqdnPrincipalsPushedBody,
)
from ...models.post_external_ssh_hosts_fqdn_principals_pushed_response_200 import (
    PostExternalSshHostsFqdnPrincipalsPushedResponse200,
)
from ...types import Response


def _get_kwargs(
    fqdn: str,
    *,
    body: PostExternalSshHostsFqdnPrincipalsPushedBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/external/ssh/hosts/{fqdn}/principals-pushed".format(
            fqdn=quote(str(fqdn), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PostExternalSshHostsFqdnPrincipalsPushedResponse200 | None:
    if response.status_code == 200:
        response_200 = PostExternalSshHostsFqdnPrincipalsPushedResponse200.from_dict(
            response.json()
        )

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PostExternalSshHostsFqdnPrincipalsPushedResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    fqdn: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostExternalSshHostsFqdnPrincipalsPushedBody,
) -> Response[PostExternalSshHostsFqdnPrincipalsPushedResponse200]:
    """Acknowledge that a host's principal files were installed (fleet token; sha256 must match the current
    render)

    Args:
        fqdn (str):
        body (PostExternalSshHostsFqdnPrincipalsPushedBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostExternalSshHostsFqdnPrincipalsPushedResponse200]
    """

    kwargs = _get_kwargs(
        fqdn=fqdn,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    fqdn: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostExternalSshHostsFqdnPrincipalsPushedBody,
) -> PostExternalSshHostsFqdnPrincipalsPushedResponse200 | None:
    """Acknowledge that a host's principal files were installed (fleet token; sha256 must match the current
    render)

    Args:
        fqdn (str):
        body (PostExternalSshHostsFqdnPrincipalsPushedBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostExternalSshHostsFqdnPrincipalsPushedResponse200
    """

    return sync_detailed(
        fqdn=fqdn,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    fqdn: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostExternalSshHostsFqdnPrincipalsPushedBody,
) -> Response[PostExternalSshHostsFqdnPrincipalsPushedResponse200]:
    """Acknowledge that a host's principal files were installed (fleet token; sha256 must match the current
    render)

    Args:
        fqdn (str):
        body (PostExternalSshHostsFqdnPrincipalsPushedBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostExternalSshHostsFqdnPrincipalsPushedResponse200]
    """

    kwargs = _get_kwargs(
        fqdn=fqdn,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    fqdn: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostExternalSshHostsFqdnPrincipalsPushedBody,
) -> PostExternalSshHostsFqdnPrincipalsPushedResponse200 | None:
    """Acknowledge that a host's principal files were installed (fleet token; sha256 must match the current
    render)

    Args:
        fqdn (str):
        body (PostExternalSshHostsFqdnPrincipalsPushedBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostExternalSshHostsFqdnPrincipalsPushedResponse200
    """

    return (
        await asyncio_detailed(
            fqdn=fqdn,
            client=client,
            body=body,
        )
    ).parsed
