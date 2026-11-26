"""HTTP 429 handling shared by every request the CLI sends.

PKI Manager 3.18.0 rate-limits its API: per source IP on every route, and per
token on the ``/api/v1/external`` and SSH fleet routes. A limited request gets
``429`` with ``{"error": {"code": "RATE_LIMITED", ...}}`` and, in most cases, a
``Retry-After`` header.

Two pieces, both attached to the ``httpx`` clients in :mod:`pki_cli.client` and
:mod:`pki_cli.http`, so the generated ``pki_api`` client and the thin helpers
behave the same:

* :class:`RateLimitTransport` waits for ``Retry-After`` and sends the request
  again. It is off by default (``PKI_RATE_LIMIT_RETRIES=0``): a CLI that sleeps
  for a minute without being asked is a surprise.
* :func:`raise_on_rate_limit` turns a 429 that reaches the caller into a
  :class:`RateLimitedError` with a message that says what to do.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Callable, Optional

import httpx


class ApiError(Exception):
    """A non-2xx API response, carrying the parsed status + message."""

    def __init__(self, status: int, message: str) -> None:
        self.status = status
        super().__init__(message)


class RateLimitedError(ApiError):
    """The server answered HTTP 429 and the CLI did not (or could not) wait."""

    def __init__(self, message: str, retry_after: Optional[float] = None) -> None:
        self.retry_after = retry_after
        super().__init__(429, message)


def parse_retry_after(value: Optional[str]) -> Optional[float]:
    """Seconds to wait from a ``Retry-After`` header (delta-seconds or HTTP-date)."""
    if not value:
        return None
    value = value.strip()
    try:
        return max(0.0, float(value))
    except ValueError:
        pass
    try:
        when = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return max(0.0, (when - datetime.now(timezone.utc)).total_seconds())


def _seconds(value: float) -> str:
    return f"{value:g} s"


def rate_limit_message(response: httpx.Response) -> str:
    """Build the error text for a 429 response (the body must be readable)."""
    detail = "Too many requests"
    try:
        error = response.json().get("error")
        if isinstance(error, dict) and error.get("message"):
            detail = str(error["message"])
    except Exception:  # noqa: BLE001 - a 429 from a proxy may have any body
        pass
    retry_after = parse_retry_after(response.headers.get("retry-after"))
    if retry_after is None:
        # No Retry-After: the CLI cannot know how long to wait, so it offers no auto-retry.
        return f"RATE_LIMITED: {detail} (HTTP 429). Retry later."
    return (
        f"RATE_LIMITED: {detail} (HTTP 429). Retry after {_seconds(retry_after)}. "
        "Set PKI_RATE_LIMIT_RETRIES (or --rate-limit-retries) to wait and retry automatically."
    )


def raise_on_rate_limit(response: httpx.Response) -> None:
    """``httpx`` response hook: raise :class:`RateLimitedError` on a 429."""
    if response.status_code != 429:
        return
    response.read()
    raise RateLimitedError(
        rate_limit_message(response),
        parse_retry_after(response.headers.get("retry-after")),
    )


class RateLimitTransport(httpx.BaseTransport):
    """Send a 429-limited request again after its ``Retry-After`` delay.

    A 429 means the server refused the request before it ran it, so a second
    send is safe for every method. The transport gives the 429 back unchanged
    when no retry is left, when there is no usable ``Retry-After``, or when the
    delay is longer than ``max_wait``.
    """

    def __init__(
        self,
        inner: Optional[httpx.BaseTransport] = None,
        *,
        retries: int = 0,
        max_wait: float = 120.0,
        sleep: Callable[[float], None] = time.sleep,
        notify: Optional[Callable[[str], None]] = None,
    ) -> None:
        self._inner = inner or httpx.HTTPTransport()
        self.retries = max(0, retries)
        self.max_wait = max_wait
        self._sleep = sleep
        self._notify = notify

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        attempt = 0
        while True:
            response = self._inner.handle_request(request)
            if response.status_code != 429 or attempt >= self.retries:
                return response
            delay = parse_retry_after(response.headers.get("retry-after"))
            if delay is None or delay > self.max_wait:
                return response
            response.close()
            attempt += 1
            if self._notify:
                self._notify(
                    f"Rate limited (HTTP 429): wait {_seconds(delay)}, "
                    f"then retry {attempt} of {self.retries}"
                )
            self._sleep(delay)

    def close(self) -> None:
        self._inner.close()


def httpx_args(
    *,
    retries: int = 0,
    max_wait: float = 120.0,
    notify: Optional[Callable[[str], None]] = None,
    inner: Optional[httpx.BaseTransport] = None,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    """Keyword arguments that give an ``httpx.Client`` the 429 behaviour above."""
    return {
        "transport": RateLimitTransport(
            inner, retries=retries, max_wait=max_wait, notify=notify, sleep=sleep
        ),
        "event_hooks": {"response": [raise_on_rate_limit]},
    }
