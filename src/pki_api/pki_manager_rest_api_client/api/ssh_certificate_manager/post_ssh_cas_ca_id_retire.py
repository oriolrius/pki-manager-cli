from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_ssh_cas_ca_id_retire_response_200 import (
    PostSshCasCaIdRetireResponse200,
)
from ...models.post_ssh_cas_ca_id_retire_response_400 import (
    PostSshCasCaIdRetireResponse400,
)
from ...models.post_ssh_cas_ca_id_retire_response_500 import (
    PostSshCasCaIdRetireResponse500,
)
from ...types import Response


def _get_kwargs(
    ca_id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/ssh/cas/{ca_id}/retire".format(
            ca_id=quote(str(ca_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    PostSshCasCaIdRetireResponse200
    | PostSshCasCaIdRetireResponse400
    | PostSshCasCaIdRetireResponse500
    | None
):
    if response.status_code == 200:
        response_200 = PostSshCasCaIdRetireResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = PostSshCasCaIdRetireResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = PostSshCasCaIdRetireResponse500.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    PostSshCasCaIdRetireResponse200
    | PostSshCasCaIdRetireResponse400
    | PostSshCasCaIdRetireResponse500
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
) -> Response[
    PostSshCasCaIdRetireResponse200
    | PostSshCasCaIdRetireResponse400
    | PostSshCasCaIdRetireResponse500
]:
    """Retire an SSH CA (stops issuance, keeps trust)

    Args:
        ca_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostSshCasCaIdRetireResponse200 | PostSshCasCaIdRetireResponse400 | PostSshCasCaIdRetireResponse500]
    """

    kwargs = _get_kwargs(
        ca_id=ca_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    ca_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> (
    PostSshCasCaIdRetireResponse200
    | PostSshCasCaIdRetireResponse400
    | PostSshCasCaIdRetireResponse500
    | None
):
    """Retire an SSH CA (stops issuance, keeps trust)

    Args:
        ca_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostSshCasCaIdRetireResponse200 | PostSshCasCaIdRetireResponse400 | PostSshCasCaIdRetireResponse500
    """

    return sync_detailed(
        ca_id=ca_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    ca_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[
    PostSshCasCaIdRetireResponse200
    | PostSshCasCaIdRetireResponse400
    | PostSshCasCaIdRetireResponse500
]:
    """Retire an SSH CA (stops issuance, keeps trust)

    Args:
        ca_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PostSshCasCaIdRetireResponse200 | PostSshCasCaIdRetireResponse400 | PostSshCasCaIdRetireResponse500]
    """

    kwargs = _get_kwargs(
        ca_id=ca_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    ca_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> (
    PostSshCasCaIdRetireResponse200
    | PostSshCasCaIdRetireResponse400
    | PostSshCasCaIdRetireResponse500
    | None
):
    """Retire an SSH CA (stops issuance, keeps trust)

    Args:
        ca_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PostSshCasCaIdRetireResponse200 | PostSshCasCaIdRetireResponse400 | PostSshCasCaIdRetireResponse500
    """

    return (
        await asyncio_detailed(
            ca_id=ca_id,
            client=client,
        )
    ).parsed
