from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_external_ssh_sign_host_body import PostExternalSshSignHostBody
from ...models.post_external_ssh_sign_host_response_200 import (
    PostExternalSshSignHostResponse200,
)
from ...types import Response


def _get_kwargs(
    *,
    body: PostExternalSshSignHostBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/external/ssh/sign-host",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PostExternalSshSignHostResponse200 | None:
    if response.status_code == 200:
        response_200 = PostExternalSshSignHostResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PostExternalSshSignHostResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PostExternalSshSignHostBody,
) -> Response[PostExternalSshSignHostResponse200]:
    """Sign a host certificate (fleet token; idempotent on Idempotency-Key)

    Args:
        body (PostExternalSshSignHostBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostExternalSshSignHostResponse200]
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
    body: PostExternalSshSignHostBody,
) -> PostExternalSshSignHostResponse200 | None:
    """Sign a host certificate (fleet token; idempotent on Idempotency-Key)

    Args:
        body (PostExternalSshSignHostBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostExternalSshSignHostResponse200
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PostExternalSshSignHostBody,
) -> Response[PostExternalSshSignHostResponse200]:
    """Sign a host certificate (fleet token; idempotent on Idempotency-Key)

    Args:
        body (PostExternalSshSignHostBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostExternalSshSignHostResponse200]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: PostExternalSshSignHostBody,
) -> PostExternalSshSignHostResponse200 | None:
    """Sign a host certificate (fleet token; idempotent on Idempotency-Key)

    Args:
        body (PostExternalSshSignHostBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostExternalSshSignHostResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
