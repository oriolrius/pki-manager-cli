from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_ssh_certs_id_revoke_body import PostSshCertsIdRevokeBody
from ...models.post_ssh_certs_id_revoke_response_200 import (
    PostSshCertsIdRevokeResponse200,
)
from ...models.post_ssh_certs_id_revoke_response_400 import (
    PostSshCertsIdRevokeResponse400,
)
from ...models.post_ssh_certs_id_revoke_response_500 import (
    PostSshCertsIdRevokeResponse500,
)
from ...types import Response


def _get_kwargs(
    id: str,
    *,
    body: PostSshCertsIdRevokeBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/ssh/certs/{id}/revoke".format(
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
    PostSshCertsIdRevokeResponse200
    | PostSshCertsIdRevokeResponse400
    | PostSshCertsIdRevokeResponse500
    | None
):
    if response.status_code == 200:
        response_200 = PostSshCertsIdRevokeResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = PostSshCertsIdRevokeResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = PostSshCertsIdRevokeResponse500.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    PostSshCertsIdRevokeResponse200
    | PostSshCertsIdRevokeResponse400
    | PostSshCertsIdRevokeResponse500
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
    body: PostSshCertsIdRevokeBody,
) -> Response[
    PostSshCertsIdRevokeResponse200
    | PostSshCertsIdRevokeResponse400
    | PostSshCertsIdRevokeResponse500
]:
    """Revoke an SSH certificate (rebuilds the CA KRL)

    Args:
        id (str):
        body (PostSshCertsIdRevokeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostSshCertsIdRevokeResponse200 | PostSshCertsIdRevokeResponse400 | PostSshCertsIdRevokeResponse500]
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
    body: PostSshCertsIdRevokeBody,
) -> (
    PostSshCertsIdRevokeResponse200
    | PostSshCertsIdRevokeResponse400
    | PostSshCertsIdRevokeResponse500
    | None
):
    """Revoke an SSH certificate (rebuilds the CA KRL)

    Args:
        id (str):
        body (PostSshCertsIdRevokeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostSshCertsIdRevokeResponse200 | PostSshCertsIdRevokeResponse400 | PostSshCertsIdRevokeResponse500
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
    body: PostSshCertsIdRevokeBody,
) -> Response[
    PostSshCertsIdRevokeResponse200
    | PostSshCertsIdRevokeResponse400
    | PostSshCertsIdRevokeResponse500
]:
    """Revoke an SSH certificate (rebuilds the CA KRL)

    Args:
        id (str):
        body (PostSshCertsIdRevokeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostSshCertsIdRevokeResponse200 | PostSshCertsIdRevokeResponse400 | PostSshCertsIdRevokeResponse500]
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
    body: PostSshCertsIdRevokeBody,
) -> (
    PostSshCertsIdRevokeResponse200
    | PostSshCertsIdRevokeResponse400
    | PostSshCertsIdRevokeResponse500
    | None
):
    """Revoke an SSH certificate (rebuilds the CA KRL)

    Args:
        id (str):
        body (PostSshCertsIdRevokeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostSshCertsIdRevokeResponse200 | PostSshCertsIdRevokeResponse400 | PostSshCertsIdRevokeResponse500
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
