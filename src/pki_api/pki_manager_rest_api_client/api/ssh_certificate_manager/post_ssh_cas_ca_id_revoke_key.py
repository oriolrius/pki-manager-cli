from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_ssh_cas_ca_id_revoke_key_body import PostSshCasCaIdRevokeKeyBody
from ...models.post_ssh_cas_ca_id_revoke_key_response_200 import (
    PostSshCasCaIdRevokeKeyResponse200,
)
from ...models.post_ssh_cas_ca_id_revoke_key_response_400 import (
    PostSshCasCaIdRevokeKeyResponse400,
)
from ...models.post_ssh_cas_ca_id_revoke_key_response_500 import (
    PostSshCasCaIdRevokeKeyResponse500,
)
from ...types import Response


def _get_kwargs(
    ca_id: str,
    *,
    body: PostSshCasCaIdRevokeKeyBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/ssh/cas/{ca_id}/revoke-key".format(
            ca_id=quote(str(ca_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    PostSshCasCaIdRevokeKeyResponse200
    | PostSshCasCaIdRevokeKeyResponse400
    | PostSshCasCaIdRevokeKeyResponse500
    | None
):
    if response.status_code == 200:
        response_200 = PostSshCasCaIdRevokeKeyResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = PostSshCasCaIdRevokeKeyResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = PostSshCasCaIdRevokeKeyResponse500.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    PostSshCasCaIdRevokeKeyResponse200
    | PostSshCasCaIdRevokeKeyResponse400
    | PostSshCasCaIdRevokeKeyResponse500
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    ca_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostSshCasCaIdRevokeKeyBody,
) -> Response[
    PostSshCasCaIdRevokeKeyResponse200
    | PostSshCasCaIdRevokeKeyResponse400
    | PostSshCasCaIdRevokeKeyResponse500
]:
    """Revoke a public key by fingerprint under a CA (rebuilds the KRL)

    Args:
        ca_id (str):
        body (PostSshCasCaIdRevokeKeyBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostSshCasCaIdRevokeKeyResponse200 | PostSshCasCaIdRevokeKeyResponse400 | PostSshCasCaIdRevokeKeyResponse500]
    """

    kwargs = _get_kwargs(
        ca_id=ca_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    ca_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostSshCasCaIdRevokeKeyBody,
) -> (
    PostSshCasCaIdRevokeKeyResponse200
    | PostSshCasCaIdRevokeKeyResponse400
    | PostSshCasCaIdRevokeKeyResponse500
    | None
):
    """Revoke a public key by fingerprint under a CA (rebuilds the KRL)

    Args:
        ca_id (str):
        body (PostSshCasCaIdRevokeKeyBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostSshCasCaIdRevokeKeyResponse200 | PostSshCasCaIdRevokeKeyResponse400 | PostSshCasCaIdRevokeKeyResponse500
    """

    return sync_detailed(
        ca_id=ca_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    ca_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostSshCasCaIdRevokeKeyBody,
) -> Response[
    PostSshCasCaIdRevokeKeyResponse200
    | PostSshCasCaIdRevokeKeyResponse400
    | PostSshCasCaIdRevokeKeyResponse500
]:
    """Revoke a public key by fingerprint under a CA (rebuilds the KRL)

    Args:
        ca_id (str):
        body (PostSshCasCaIdRevokeKeyBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostSshCasCaIdRevokeKeyResponse200 | PostSshCasCaIdRevokeKeyResponse400 | PostSshCasCaIdRevokeKeyResponse500]
    """

    kwargs = _get_kwargs(
        ca_id=ca_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    ca_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostSshCasCaIdRevokeKeyBody,
) -> (
    PostSshCasCaIdRevokeKeyResponse200
    | PostSshCasCaIdRevokeKeyResponse400
    | PostSshCasCaIdRevokeKeyResponse500
    | None
):
    """Revoke a public key by fingerprint under a CA (rebuilds the KRL)

    Args:
        ca_id (str):
        body (PostSshCasCaIdRevokeKeyBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostSshCasCaIdRevokeKeyResponse200 | PostSshCasCaIdRevokeKeyResponse400 | PostSshCasCaIdRevokeKeyResponse500
    """

    return (
        await asyncio_detailed(
            ca_id=ca_id,
            client=client,
            body=body,
        )
    ).parsed
