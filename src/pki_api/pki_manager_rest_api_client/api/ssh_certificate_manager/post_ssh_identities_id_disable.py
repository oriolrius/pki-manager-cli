from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_ssh_identities_id_disable_response_200 import (
    PostSshIdentitiesIdDisableResponse200,
)
from ...models.post_ssh_identities_id_disable_response_400 import (
    PostSshIdentitiesIdDisableResponse400,
)
from ...models.post_ssh_identities_id_disable_response_500 import (
    PostSshIdentitiesIdDisableResponse500,
)
from ...types import Response


def _get_kwargs(
    id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/ssh/identities/{id}/disable".format(
            id=quote(str(id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    PostSshIdentitiesIdDisableResponse200
    | PostSshIdentitiesIdDisableResponse400
    | PostSshIdentitiesIdDisableResponse500
    | None
):
    if response.status_code == 200:
        response_200 = PostSshIdentitiesIdDisableResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = PostSshIdentitiesIdDisableResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = PostSshIdentitiesIdDisableResponse500.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    PostSshIdentitiesIdDisableResponse200
    | PostSshIdentitiesIdDisableResponse400
    | PostSshIdentitiesIdDisableResponse500
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
    PostSshIdentitiesIdDisableResponse200
    | PostSshIdentitiesIdDisableResponse400
    | PostSshIdentitiesIdDisableResponse500
]:
    """Disable an identity (blocks further issuance)

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostSshIdentitiesIdDisableResponse200 | PostSshIdentitiesIdDisableResponse400 | PostSshIdentitiesIdDisableResponse500]
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
    PostSshIdentitiesIdDisableResponse200
    | PostSshIdentitiesIdDisableResponse400
    | PostSshIdentitiesIdDisableResponse500
    | None
):
    """Disable an identity (blocks further issuance)

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostSshIdentitiesIdDisableResponse200 | PostSshIdentitiesIdDisableResponse400 | PostSshIdentitiesIdDisableResponse500
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
    PostSshIdentitiesIdDisableResponse200
    | PostSshIdentitiesIdDisableResponse400
    | PostSshIdentitiesIdDisableResponse500
]:
    """Disable an identity (blocks further issuance)

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostSshIdentitiesIdDisableResponse200 | PostSshIdentitiesIdDisableResponse400 | PostSshIdentitiesIdDisableResponse500]
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
    PostSshIdentitiesIdDisableResponse200
    | PostSshIdentitiesIdDisableResponse400
    | PostSshIdentitiesIdDisableResponse500
    | None
):
    """Disable an identity (blocks further issuance)

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostSshIdentitiesIdDisableResponse200 | PostSshIdentitiesIdDisableResponse400 | PostSshIdentitiesIdDisableResponse500
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
        )
    ).parsed
