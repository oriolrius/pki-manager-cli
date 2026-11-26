from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_external_ca_bundle_response_200 import GetExternalCaBundleResponse200
from ...models.get_external_ca_bundle_response_404 import GetExternalCaBundleResponse404
from ...models.get_external_ca_bundle_response_409 import GetExternalCaBundleResponse409
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/external/ca-bundle",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    GetExternalCaBundleResponse200
    | GetExternalCaBundleResponse404
    | GetExternalCaBundleResponse409
    | None
):
    if response.status_code == 200:
        response_200 = GetExternalCaBundleResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 404:
        response_404 = GetExternalCaBundleResponse404.from_dict(response.json())

        return response_404

    if response.status_code == 409:
        response_409 = GetExternalCaBundleResponse409.from_dict(response.json())

        return response_409

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    GetExternalCaBundleResponse200
    | GetExternalCaBundleResponse404
    | GetExternalCaBundleResponse409
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[
    GetExternalCaBundleResponse200
    | GetExternalCaBundleResponse404
    | GetExternalCaBundleResponse409
]:
    """PEM chain of the integration's bound CA

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetExternalCaBundleResponse200 | GetExternalCaBundleResponse404 | GetExternalCaBundleResponse409]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
) -> (
    GetExternalCaBundleResponse200
    | GetExternalCaBundleResponse404
    | GetExternalCaBundleResponse409
    | None
):
    """PEM chain of the integration's bound CA

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetExternalCaBundleResponse200 | GetExternalCaBundleResponse404 | GetExternalCaBundleResponse409
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[
    GetExternalCaBundleResponse200
    | GetExternalCaBundleResponse404
    | GetExternalCaBundleResponse409
]:
    """PEM chain of the integration's bound CA

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetExternalCaBundleResponse200 | GetExternalCaBundleResponse404 | GetExternalCaBundleResponse409]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
) -> (
    GetExternalCaBundleResponse200
    | GetExternalCaBundleResponse404
    | GetExternalCaBundleResponse409
    | None
):
    """PEM chain of the integration's bound CA

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetExternalCaBundleResponse200 | GetExternalCaBundleResponse404 | GetExternalCaBundleResponse409
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
