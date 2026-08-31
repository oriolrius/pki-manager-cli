from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_ssh_identities_id_offboard_body import (
    PostSshIdentitiesIdOffboardBody,
)
from ...models.post_ssh_identities_id_offboard_response_200 import (
    PostSshIdentitiesIdOffboardResponse200,
)
from ...models.post_ssh_identities_id_offboard_response_400 import (
    PostSshIdentitiesIdOffboardResponse400,
)
from ...models.post_ssh_identities_id_offboard_response_500 import (
    PostSshIdentitiesIdOffboardResponse500,
)
from ...types import Response


def _get_kwargs(
    id: str,
    *,
    body: PostSshIdentitiesIdOffboardBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/ssh/identities/{id}/offboard".format(
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
    PostSshIdentitiesIdOffboardResponse200
    | PostSshIdentitiesIdOffboardResponse400
    | PostSshIdentitiesIdOffboardResponse500
    | None
):
    if response.status_code == 200:
        response_200 = PostSshIdentitiesIdOffboardResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = PostSshIdentitiesIdOffboardResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = PostSshIdentitiesIdOffboardResponse500.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    PostSshIdentitiesIdOffboardResponse200
    | PostSshIdentitiesIdOffboardResponse400
    | PostSshIdentitiesIdOffboardResponse500
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
    body: PostSshIdentitiesIdOffboardBody,
) -> Response[
    PostSshIdentitiesIdOffboardResponse200
    | PostSshIdentitiesIdOffboardResponse400
    | PostSshIdentitiesIdOffboardResponse500
]:
    """Offboard an identity (disable + revoke its live certs)

    Args:
        id (str):
        body (PostSshIdentitiesIdOffboardBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostSshIdentitiesIdOffboardResponse200 | PostSshIdentitiesIdOffboardResponse400 | PostSshIdentitiesIdOffboardResponse500]
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
    body: PostSshIdentitiesIdOffboardBody,
) -> (
    PostSshIdentitiesIdOffboardResponse200
    | PostSshIdentitiesIdOffboardResponse400
    | PostSshIdentitiesIdOffboardResponse500
    | None
):
    """Offboard an identity (disable + revoke its live certs)

    Args:
        id (str):
        body (PostSshIdentitiesIdOffboardBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostSshIdentitiesIdOffboardResponse200 | PostSshIdentitiesIdOffboardResponse400 | PostSshIdentitiesIdOffboardResponse500
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
    body: PostSshIdentitiesIdOffboardBody,
) -> Response[
    PostSshIdentitiesIdOffboardResponse200
    | PostSshIdentitiesIdOffboardResponse400
    | PostSshIdentitiesIdOffboardResponse500
]:
    """Offboard an identity (disable + revoke its live certs)

    Args:
        id (str):
        body (PostSshIdentitiesIdOffboardBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostSshIdentitiesIdOffboardResponse200 | PostSshIdentitiesIdOffboardResponse400 | PostSshIdentitiesIdOffboardResponse500]
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
    body: PostSshIdentitiesIdOffboardBody,
) -> (
    PostSshIdentitiesIdOffboardResponse200
    | PostSshIdentitiesIdOffboardResponse400
    | PostSshIdentitiesIdOffboardResponse500
    | None
):
    """Offboard an identity (disable + revoke its live certs)

    Args:
        id (str):
        body (PostSshIdentitiesIdOffboardBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostSshIdentitiesIdOffboardResponse200 | PostSshIdentitiesIdOffboardResponse400 | PostSshIdentitiesIdOffboardResponse500
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
