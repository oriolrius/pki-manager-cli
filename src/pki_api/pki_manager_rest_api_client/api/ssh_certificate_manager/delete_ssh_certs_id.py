from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_ssh_certs_id_response_200 import DeleteSshCertsIdResponse200
from ...models.delete_ssh_certs_id_response_400 import DeleteSshCertsIdResponse400
from ...models.delete_ssh_certs_id_response_409 import DeleteSshCertsIdResponse409
from ...models.delete_ssh_certs_id_response_500 import DeleteSshCertsIdResponse500
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: str,
    *,
    force: bool | Unset = UNSET,
    drop_revocation: bool | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["force"] = force

    params["dropRevocation"] = drop_revocation

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/ssh/certs/{id}".format(
            id=quote(str(id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    DeleteSshCertsIdResponse200
    | DeleteSshCertsIdResponse400
    | DeleteSshCertsIdResponse409
    | DeleteSshCertsIdResponse500
    | None
):
    if response.status_code == 200:
        response_200 = DeleteSshCertsIdResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = DeleteSshCertsIdResponse400.from_dict(response.json())

        return response_400

    if response.status_code == 409:
        response_409 = DeleteSshCertsIdResponse409.from_dict(response.json())

        return response_409

    if response.status_code == 500:
        response_500 = DeleteSshCertsIdResponse500.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    DeleteSshCertsIdResponse200
    | DeleteSshCertsIdResponse400
    | DeleteSshCertsIdResponse409
    | DeleteSshCertsIdResponse500
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
    force: bool | Unset = UNSET,
    drop_revocation: bool | Unset = UNSET,
) -> Response[
    DeleteSshCertsIdResponse200
    | DeleteSshCertsIdResponse400
    | DeleteSshCertsIdResponse409
    | DeleteSshCertsIdResponse500
]:
    r"""Purge (hard-delete) an SSH certificate — erase all DB trace of a mis-issued cert

     Permanently deletes the certificate row and every DB trace of it. Use this to undo a certificate
    that was created by mistake and never left the server — NOT to decommission a deployed host
    (offboard the host instead). Always writes an `ssh.cert.purge` audit_log entry.

    A certificate is a self-contained signed credential: once issued, copies may exist outside this
    database (on hosts, in ~/.ssh, in backups, or in an attacker's hands). Deleting the row does NOT
    recall those copies. The KRL — which is *rebuilt from DB state* — is the only thing that stops a
    still-valid copy. Behaviour therefore depends on the cert's state:

    • active (never revoked): PURE PURGE. Its serial was never in the KRL, so removal is KRL-neutral.
      This is the intended case. `force` is not required.
    • revoked + still valid: requires `force=true`. By DEFAULT the serial is preserved in the KRL (via a
      standalone directive) so it stays revoked until it expires — the record is gone, the kill-switch
      survives. Add `dropRevocation=true` to ALSO remove it from the KRL, which RE-ENABLES any copy
    still
      in the wild — only safe if the certificate truly never left the server.
    • expired: purged freely; the clock already rejects it.

    Idempotent: purging an unknown id returns 404. Reason (optional) may be sent as `{ \"reason\":
    \"...\" }`.

    Args:
        id (str):
        force (bool | Unset):
        drop_revocation (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteSshCertsIdResponse200 | DeleteSshCertsIdResponse400 | DeleteSshCertsIdResponse409 | DeleteSshCertsIdResponse500]
    """

    kwargs = _get_kwargs(
        id=id,
        force=force,
        drop_revocation=drop_revocation,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    force: bool | Unset = UNSET,
    drop_revocation: bool | Unset = UNSET,
) -> (
    DeleteSshCertsIdResponse200
    | DeleteSshCertsIdResponse400
    | DeleteSshCertsIdResponse409
    | DeleteSshCertsIdResponse500
    | None
):
    r"""Purge (hard-delete) an SSH certificate — erase all DB trace of a mis-issued cert

     Permanently deletes the certificate row and every DB trace of it. Use this to undo a certificate
    that was created by mistake and never left the server — NOT to decommission a deployed host
    (offboard the host instead). Always writes an `ssh.cert.purge` audit_log entry.

    A certificate is a self-contained signed credential: once issued, copies may exist outside this
    database (on hosts, in ~/.ssh, in backups, or in an attacker's hands). Deleting the row does NOT
    recall those copies. The KRL — which is *rebuilt from DB state* — is the only thing that stops a
    still-valid copy. Behaviour therefore depends on the cert's state:

    • active (never revoked): PURE PURGE. Its serial was never in the KRL, so removal is KRL-neutral.
      This is the intended case. `force` is not required.
    • revoked + still valid: requires `force=true`. By DEFAULT the serial is preserved in the KRL (via a
      standalone directive) so it stays revoked until it expires — the record is gone, the kill-switch
      survives. Add `dropRevocation=true` to ALSO remove it from the KRL, which RE-ENABLES any copy
    still
      in the wild — only safe if the certificate truly never left the server.
    • expired: purged freely; the clock already rejects it.

    Idempotent: purging an unknown id returns 404. Reason (optional) may be sent as `{ \"reason\":
    \"...\" }`.

    Args:
        id (str):
        force (bool | Unset):
        drop_revocation (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteSshCertsIdResponse200 | DeleteSshCertsIdResponse400 | DeleteSshCertsIdResponse409 | DeleteSshCertsIdResponse500
    """

    return sync_detailed(
        id=id,
        client=client,
        force=force,
        drop_revocation=drop_revocation,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    force: bool | Unset = UNSET,
    drop_revocation: bool | Unset = UNSET,
) -> Response[
    DeleteSshCertsIdResponse200
    | DeleteSshCertsIdResponse400
    | DeleteSshCertsIdResponse409
    | DeleteSshCertsIdResponse500
]:
    r"""Purge (hard-delete) an SSH certificate — erase all DB trace of a mis-issued cert

     Permanently deletes the certificate row and every DB trace of it. Use this to undo a certificate
    that was created by mistake and never left the server — NOT to decommission a deployed host
    (offboard the host instead). Always writes an `ssh.cert.purge` audit_log entry.

    A certificate is a self-contained signed credential: once issued, copies may exist outside this
    database (on hosts, in ~/.ssh, in backups, or in an attacker's hands). Deleting the row does NOT
    recall those copies. The KRL — which is *rebuilt from DB state* — is the only thing that stops a
    still-valid copy. Behaviour therefore depends on the cert's state:

    • active (never revoked): PURE PURGE. Its serial was never in the KRL, so removal is KRL-neutral.
      This is the intended case. `force` is not required.
    • revoked + still valid: requires `force=true`. By DEFAULT the serial is preserved in the KRL (via a
      standalone directive) so it stays revoked until it expires — the record is gone, the kill-switch
      survives. Add `dropRevocation=true` to ALSO remove it from the KRL, which RE-ENABLES any copy
    still
      in the wild — only safe if the certificate truly never left the server.
    • expired: purged freely; the clock already rejects it.

    Idempotent: purging an unknown id returns 404. Reason (optional) may be sent as `{ \"reason\":
    \"...\" }`.

    Args:
        id (str):
        force (bool | Unset):
        drop_revocation (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteSshCertsIdResponse200 | DeleteSshCertsIdResponse400 | DeleteSshCertsIdResponse409 | DeleteSshCertsIdResponse500]
    """

    kwargs = _get_kwargs(
        id=id,
        force=force,
        drop_revocation=drop_revocation,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    force: bool | Unset = UNSET,
    drop_revocation: bool | Unset = UNSET,
) -> (
    DeleteSshCertsIdResponse200
    | DeleteSshCertsIdResponse400
    | DeleteSshCertsIdResponse409
    | DeleteSshCertsIdResponse500
    | None
):
    r"""Purge (hard-delete) an SSH certificate — erase all DB trace of a mis-issued cert

     Permanently deletes the certificate row and every DB trace of it. Use this to undo a certificate
    that was created by mistake and never left the server — NOT to decommission a deployed host
    (offboard the host instead). Always writes an `ssh.cert.purge` audit_log entry.

    A certificate is a self-contained signed credential: once issued, copies may exist outside this
    database (on hosts, in ~/.ssh, in backups, or in an attacker's hands). Deleting the row does NOT
    recall those copies. The KRL — which is *rebuilt from DB state* — is the only thing that stops a
    still-valid copy. Behaviour therefore depends on the cert's state:

    • active (never revoked): PURE PURGE. Its serial was never in the KRL, so removal is KRL-neutral.
      This is the intended case. `force` is not required.
    • revoked + still valid: requires `force=true`. By DEFAULT the serial is preserved in the KRL (via a
      standalone directive) so it stays revoked until it expires — the record is gone, the kill-switch
      survives. Add `dropRevocation=true` to ALSO remove it from the KRL, which RE-ENABLES any copy
    still
      in the wild — only safe if the certificate truly never left the server.
    • expired: purged freely; the clock already rejects it.

    Idempotent: purging an unknown id returns 404. Reason (optional) may be sent as `{ \"reason\":
    \"...\" }`.

    Args:
        id (str):
        force (bool | Unset):
        drop_revocation (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteSshCertsIdResponse200 | DeleteSshCertsIdResponse400 | DeleteSshCertsIdResponse409 | DeleteSshCertsIdResponse500
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            force=force,
            drop_revocation=drop_revocation,
        )
    ).parsed
