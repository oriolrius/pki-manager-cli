"""HTTP 429: a clear error by default, an optional wait for ``Retry-After``.

PKI Manager 3.18.0 rate-limits the API per IP and per token. Every request the
CLI sends goes through :mod:`pki_cli.ratelimit`, for the generated client and
for the thin helpers in :mod:`pki_cli.http` alike.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from email.utils import format_datetime

import httpx
import pytest

from pki_api.pki_manager_rest_api_client import Client
from pki_api.pki_manager_rest_api_client.api.dashboard import get_health
from pki_cli import ratelimit
from pki_cli.ratelimit import RateLimitedError, RateLimitTransport, parse_retry_after

LIMITED = {"error": {"code": "RATE_LIMITED", "message": "Too many requests for this token"}}


class Server:
    """Answer 429 ``limited`` times, then 200. Record what happened."""

    def __init__(self, limited: int, retry_after: str | None = "2") -> None:
        self.limited = limited
        self.retry_after = retry_after
        self.requests: list[httpx.Request] = []
        self.slept: list[float] = []
        self.notes: list[str] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if len(self.requests) <= self.limited:
            headers = {"Retry-After": self.retry_after} if self.retry_after else {}
            return httpx.Response(429, json=LIMITED, headers=headers)
        return httpx.Response(200, json={"status": "ok", "body": request.content.decode()})

    def args(self, **kwargs) -> dict:
        return ratelimit.httpx_args(
            inner=httpx.MockTransport(self),
            sleep=self.slept.append,
            notify=self.notes.append,
            **kwargs,
        )

    def client(self, **kwargs) -> httpx.Client:
        return httpx.Client(base_url="http://pki.test/api/v1", **self.args(**kwargs))


# --- Retry-After parsing ------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("60", 60.0),
        (" 1.5 ", 1.5),
        ("0", 0.0),
        ("-3", 0.0),
        (None, None),
        ("", None),
        ("soon", None),
    ],
)
def test_parse_retry_after_seconds(value, expected):
    assert parse_retry_after(value) == expected


def test_parse_retry_after_http_date():
    when = datetime.now(timezone.utc) + timedelta(seconds=30)
    assert 25 < parse_retry_after(format_datetime(when, usegmt=True)) <= 30
    past = datetime.now(timezone.utc) - timedelta(hours=1)
    assert parse_retry_after(format_datetime(past, usegmt=True)) == 0.0


# --- default: no wait, a clear error -------------------------------------------


def test_429_raises_a_clear_error_by_default():
    server = Server(limited=1, retry_after="60")
    with server.client() as client, pytest.raises(RateLimitedError) as exc:
        client.get("/health")
    assert exc.value.status == 429
    assert exc.value.retry_after == 60.0
    message = str(exc.value)
    assert "RATE_LIMITED: Too many requests for this token (HTTP 429)" in message
    assert "Retry after 60 s" in message
    assert "PKI_RATE_LIMIT_RETRIES" in message
    assert len(server.requests) == 1 and server.slept == []


def test_429_without_retry_after_or_json_body():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, text="slow down")

    args = ratelimit.httpx_args(inner=httpx.MockTransport(handler), retries=3, sleep=lambda _: None)
    with httpx.Client(base_url="http://pki.test", **args) as client:
        expected = r"Too many requests \(HTTP 429\)\. Retry later\."
        with pytest.raises(RateLimitedError, match=expected):
            client.get("/x")


def test_other_statuses_are_not_touched():
    args = ratelimit.httpx_args(inner=httpx.MockTransport(lambda r: httpx.Response(400, json={})))
    with httpx.Client(base_url="http://pki.test", **args) as client:
        assert client.get("/x").status_code == 400


# --- opt-in: wait for Retry-After, then send again -----------------------------


def test_waits_for_retry_after_and_sends_the_same_request_again():
    server = Server(limited=2, retry_after="2")
    with server.client(retries=3) as client:
        response = client.post("/external/sign", json={"csrPem": "x"})
    assert response.status_code == 200
    assert response.json()["body"] == '{"csrPem":"x"}'  # the body is sent again, complete
    assert server.slept == [2.0, 2.0]
    assert len(server.requests) == 3
    assert "wait 2 s, then retry 1 of 3" in server.notes[0]


def test_gives_up_when_the_retries_are_used():
    server = Server(limited=5)
    with server.client(retries=2) as client, pytest.raises(RateLimitedError):
        client.get("/health")
    assert len(server.requests) == 3 and server.slept == [2.0, 2.0]


def test_does_not_wait_longer_than_max_wait():
    server = Server(limited=1, retry_after="600")
    with server.client(retries=3, max_wait=120) as client, pytest.raises(RateLimitedError):
        client.get("/health")
    assert len(server.requests) == 1 and server.slept == []


def test_transport_returns_the_429_when_it_cannot_retry():
    inner = httpx.MockTransport(Server(limited=9, retry_after=None))
    transport = RateLimitTransport(inner, retries=3)
    assert transport.handle_request(httpx.Request("GET", "http://pki.test/x")).status_code == 429


# --- the two ways the CLI sends requests ---------------------------------------


def test_generated_client_reports_429_the_same_way():
    server = Server(limited=1, retry_after="7")
    client = Client(
        base_url="http://pki.test/api/v1", raise_on_unexpected_status=True, httpx_args=server.args()
    )
    with pytest.raises(RateLimitedError, match="Retry after 7 s"):
        get_health.sync(client=client)


def test_cli_prints_the_rate_limit_error_and_exits_1(cli):
    server = Server(limited=1, retry_after="60")
    result = cli(server.args, "external", "health", "--token", "pkimg_x")
    assert result.exit_code == 1
    assert "RATE_LIMITED" in result.output and "Retry after 60 s" in result.output
    assert "Traceback" not in result.output


def test_cli_rate_limit_retries_option_waits_and_succeeds(cli):
    server = Server(limited=1, retry_after="3")
    argv = ("--rate-limit-retries", "1", "external", "health", "--token", "pkimg_x")
    result = cli(server.args, *argv)
    assert result.exit_code == 0, result.output
    assert server.slept == [3.0]
    assert '"status": "ok"' in result.output
