from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_ssh_trust_anchors_response_200 import GetSshTrustAnchorsResponse200
from ...models.get_ssh_trust_anchors_response_400 import GetSshTrustAnchorsResponse400
from ...models.get_ssh_trust_anchors_response_500 import GetSshTrustAnchorsResponse500
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/ssh/trust-anchors",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    GetSshTrustAnchorsResponse200
    | GetSshTrustAnchorsResponse400
    | GetSshTrustAnchorsResponse500
    | None
):
    if response.status_code == 200:
        response_200 = GetSshTrustAnchorsResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = GetSshTrustAnchorsResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = GetSshTrustAnchorsResponse500.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    GetSshTrustAnchorsResponse200
    | GetSshTrustAnchorsResponse400
    | GetSshTrustAnchorsResponse500
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[
    GetSshTrustAnchorsResponse200
    | GetSshTrustAnchorsResponse400
    | GetSshTrustAnchorsResponse500
]:
    """SSH trust anchors (TrustedUserCAKeys / @cert-authority)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetSshTrustAnchorsResponse200 | GetSshTrustAnchorsResponse400 | GetSshTrustAnchorsResponse500]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
) -> (
    GetSshTrustAnchorsResponse200
    | GetSshTrustAnchorsResponse400
    | GetSshTrustAnchorsResponse500
    | None
):
    """SSH trust anchors (TrustedUserCAKeys / @cert-authority)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetSshTrustAnchorsResponse200 | GetSshTrustAnchorsResponse400 | GetSshTrustAnchorsResponse500
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[
    GetSshTrustAnchorsResponse200
    | GetSshTrustAnchorsResponse400
    | GetSshTrustAnchorsResponse500
]:
    """SSH trust anchors (TrustedUserCAKeys / @cert-authority)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetSshTrustAnchorsResponse200 | GetSshTrustAnchorsResponse400 | GetSshTrustAnchorsResponse500]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
) -> (
    GetSshTrustAnchorsResponse200
    | GetSshTrustAnchorsResponse400
    | GetSshTrustAnchorsResponse500
    | None
):
    """SSH trust anchors (TrustedUserCAKeys / @cert-authority)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetSshTrustAnchorsResponse200 | GetSshTrustAnchorsResponse400 | GetSshTrustAnchorsResponse500
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
