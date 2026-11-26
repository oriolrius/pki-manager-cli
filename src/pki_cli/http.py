"""Thin HTTP helpers for endpoints the generated client can't fully model.

The live OpenAPI spec under-specifies the SSH Certificate Manager and external
issuer routes (no request bodies / typed responses), so the generated
``pki_api`` client can only issue empty, body-less requests for them. These
helpers talk to the API directly while reusing the same base URL and — where
applicable — the same OIDC token the rest of the CLI uses.

Four call styles map to the four auth surfaces of the API:

* :func:`authed`  — ``/api/v1/ssh/*``       OIDC bearer (reuses ``get_client``)
* :func:`token_call` — ``/api/v1/external/*`` cluster or fleet bearer token
* :func:`public`  — server ROOT (``/ssh/*``, ``/krl/*``) — no auth, not ``/api/v1``
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import httpx

from .client import get_client, rate_limit_httpx_args
from .config import get_settings
from .ratelimit import ApiError, RateLimitedError

__all__ = [
    "ApiError",
    "RateLimitedError",
    "authed",
    "public",
    "raise_on_error",
    "read_value_or_file",
    "token_call",
    "unwrap",
]

DEFAULT_TIMEOUT = 30.0


def _clean(params: Optional[dict]) -> Optional[dict]:
    """Drop ``None`` values so unset query params are omitted."""
    if not params:
        return None
    cleaned = {k: v for k, v in params.items() if v is not None}
    return cleaned or None


def _extract_error(resp: httpx.Response) -> str:
    """Pull the API's ``{error:{code,message}}`` shape out of a response."""
    try:
        data = resp.json()
    except Exception:
        return resp.text.strip() or f"HTTP {resp.status_code}"
    if isinstance(data, dict):
        err = data.get("error")
        if isinstance(err, dict):
            return f"{err.get('code', 'ERROR')}: {err.get('message', resp.text)}"
        if err is not None:
            return str(err)
    return resp.text.strip() or f"HTTP {resp.status_code}"


def _handle(resp: httpx.Response, *, expect_bytes: bool) -> Any:
    if resp.status_code >= 400:
        raise ApiError(resp.status_code, _extract_error(resp))
    if expect_bytes:
        return resp.content
    ctype = resp.headers.get("content-type", "")
    if "application/json" in ctype:
        return resp.json()
    return resp.text


def _client(base_url: str) -> httpx.Client:
    """A one-shot client with the shared HTTP 429 handling."""
    return httpx.Client(base_url=base_url, timeout=DEFAULT_TIMEOUT, **rate_limit_httpx_args())


def _api_url() -> str:
    settings = get_settings()
    if not settings.api_url:
        raise ApiError(0, "PKI_API_URL is not set (configure it via --api-url, env, or .env)")
    return settings.api_url


def authed(
    method: str,
    path: str,
    *,
    json: Any = None,
    params: Optional[dict] = None,
    expect_bytes: bool = False,
) -> Any:
    """Call an OIDC-authenticated ``/api/v1`` route (SSH Certificate Manager)."""
    client = get_client()
    resp = client.get_httpx_client().request(method, path, json=json, params=_clean(params))
    return _handle(resp, expect_bytes=expect_bytes)


def token_call(
    method: str,
    path: str,
    token: Optional[str],
    *,
    json: Any = None,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
    expect_bytes: bool = False,
) -> Any:
    """Call an ``/api/v1/external`` route with a raw bearer token.

    Used for the cluster-token issuer API (``/external/*``) and the
    fleet-token SSH automation API (``/external/ssh/*``). ``token`` may be
    ``None`` for the unauthenticated ECIES ``/external/ssh/krl`` endpoint.
    """
    h: dict[str, str] = {}
    if token:
        h["Authorization"] = f"Bearer {token}"
    if headers:
        h.update({k: v for k, v in headers.items() if v is not None})
    with _client(_api_url()) as client:
        resp = client.request(method, path, json=json, params=_clean(params), headers=h)
    return _handle(resp, expect_bytes=expect_bytes)


def public(
    method: str,
    path: str,
    *,
    params: Optional[dict] = None,
    expect_bytes: bool = False,
) -> Any:
    """Call an unauthenticated public route served at the server ROOT.

    The trust-material and KRL download routes (``/ssh/*``, ``/krl/*``) are
    mounted outside the ``/api/v1`` prefix, so strip it from the base URL.
    """
    root = _api_url().replace("/api/v1", "")
    with _client(root) as client:
        resp = client.request(method, path, params=_clean(params))
    # These trust-material routes live at the backend root; some deployments serve
    # a web app there and shadow them, returning index.html. Fail clearly instead
    # of dumping HTML as if it were key material.
    if resp.status_code < 400 and "text/html" in resp.headers.get("content-type", ""):
        raise ApiError(
            502,
            f"{path} returned an HTML page, not API data — the public SSH/KRL routes are "
            "served at the server root and appear to be shadowed by the web frontend on this "
            "deployment.",
        )
    return _handle(resp, expect_bytes=expect_bytes)


def unwrap(result: Any, *, what: str) -> Any:
    """Return a generated-client result, or raise on the API's error shape.

    ``sync()`` on the generated client returns the *parsed union* of every
    documented response, so a 4xx/5xx comes back as a model carrying an
    ``error`` object rather than raising. Collapse that into an
    :class:`ApiError` so every command reports failures the same way.
    """
    if result is None:
        raise ApiError(0, f"{what} failed (no response body)")
    raise_on_error(result)
    return result


def raise_on_error(result: Any) -> None:
    """Raise :class:`ApiError` when a generated-client result is the API's error shape.

    For commands that handle a ``None`` result themselves. Without this check a
    documented 4xx (for example the 400 of a rejected SAN value) is parsed into
    an error model, and the command fails on a missing attribute instead of
    showing the server's message.
    """
    error = getattr(result, "error", None)
    if error is None:
        return
    code = getattr(error, "code", "ERROR")
    message = getattr(error, "message", str(error))
    if not isinstance(code, str):
        code = "ERROR"
    if not isinstance(message, str):
        message = str(error)
    raise ApiError(0, f"{code}: {message}")


def read_value_or_file(value: Optional[str]) -> Optional[str]:
    """Return ``value`` verbatim, or the contents of ``path`` for ``@path``.

    Lets flags like ``--pubkey`` / ``--csr`` accept either an inline string or
    an ``@/path/to/file`` reference (handy for multi-line PEM / OpenSSH keys).
    """
    if value is None:
        return None
    if value.startswith("@"):
        return Path(value[1:]).expanduser().read_text()
    return value
