"""Behaviour the CLI needs for PKI Manager 3.18.0, checked against a fake server."""

from __future__ import annotations

import base64
import json

import httpx
import pytest

from pki_cli import ratelimit
from pki_cli.http import ApiError, raise_on_error

UUID = "1c7c296f-4b6d-4150-b5ab-9e48705c87c9"


class Recorder:
    """A fake API: answer with ``reply`` and keep the requests."""

    def __init__(self, status: int = 200, reply: object = None) -> None:
        self.status = status
        self.reply = {"ok": True} if reply is None else reply
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return httpx.Response(self.status, json=self.reply)

    def args(self, **kwargs) -> dict:
        return ratelimit.httpx_args(inner=httpx.MockTransport(self), **kwargs)

    @property
    def last(self) -> httpx.Request:
        return self.requests[-1]

    @property
    def body(self) -> dict:
        return json.loads(self.last.content)


def test_rejected_san_shows_the_server_message(cli):
    """3.18.0 validates SAN values more strictly; the 400 must reach the user."""
    api = Recorder(
        400,
        {"error": {"code": "VALIDATION_ERROR", "message": "Invalid SANs: Invalid SAN IP address"}},
    )
    result = cli(api.args, "cert", "issue", "--ca", UUID, "--cn", "a.test", "--ip", "999.1.1.1")
    assert result.exit_code == 1
    assert "VALIDATION_ERROR: Invalid SANs: Invalid SAN IP address" in result.output
    assert "has no attribute" not in result.output


def test_raise_on_error_leaves_success_and_none_alone():
    raise_on_error(None)
    raise_on_error(type("Ok", (), {"id": "x"})())
    bad = type("Bad", (), {"error": type("E", (), {"code": "NOPE", "message": "no"})()})()
    with pytest.raises(ApiError, match="NOPE: no"):
        raise_on_error(bad)


@pytest.mark.parametrize(
    "argv",
    [
        ("cert", "download", UUID, "-f", "p12", "-p", "s3cret-pass", "-o", "out.bin"),
        ("ca", "download", UUID, "-f", "p12-truststore", "-p", "s3cret-pass", "-o", "out.bin"),
    ],
)
def test_export_password_goes_in_a_header_not_in_the_url(cli, tmp_path, monkeypatch, argv):
    monkeypatch.chdir(tmp_path)
    api = Recorder(reply={"data": base64.b64encode(b"bundle").decode(), "filename": "x.p12"})
    result = cli(api.args, *argv)
    assert result.exit_code == 0, result.output
    assert api.last.headers["x-export-password"] == "s3cret-pass"
    assert "s3cret-pass" not in str(api.last.url) and "password" not in api.last.url.params
    assert (tmp_path / "out.bin").read_bytes() == b"bundle"


def test_token_mint_sends_the_new_limits(cli):
    api = Recorder(reply={"token": "pkimg_x"})
    result = cli(
        api.args, "ssh", "token", "mint", "--name", "ci", "--op", "sign-user",
        "--allowed-principal", "deploy", "--allowed-principal", "ops", "--max-ttl", "3600",
    )  # fmt: skip
    assert result.exit_code == 0, result.output
    assert api.body == {
        "name": "ci",
        "opSet": ["sign-user"],
        "allowedPrincipals": ["deploy", "ops"],
        "maxValidForSeconds": 3600,
    }


def test_token_mint_without_limits_sends_no_limit_fields(cli):
    api = Recorder(reply={"token": "pkimg_x"})
    assert cli(api.args, "ssh", "token", "mint", "--name", "ci", "--op", "sign-host").exit_code == 0
    assert api.body == {"name": "ci", "opSet": ["sign-host"]}


@pytest.mark.parametrize(
    ("argv", "method", "path", "body"),
    [
        (("ssh", "ca", "reissue-report", "ca1"), "GET", "/ssh/cas/ca1/reissue-report", None),
        (("ssh", "host", "principal-maps", "h1"), "GET", "/ssh/hosts/h1/principal-maps", None),
        (("ssh", "identity", "grants", "i1"), "GET", "/ssh/identities/i1/grants", None),
        (
            ("ssh", "principal", "unmap", "--host-id", "h1", "--principal-id", "p1",
             "--local-account", "root"),
            "POST", "/ssh/principals/unmap",
            {"hostId": "h1", "principalId": "p1", "localAccount": "root"},
        ),
        (
            ("ssh", "principal", "revoke-grant", "--identity-id", "i1", "--principal-id", "p1"),
            "POST", "/ssh/principals/revoke-grant", {"identityId": "i1", "principalId": "p1"},
        ),
        (("ssh", "cert", "purge", "c1", "--force"), "DELETE", "/ssh/certs/c1", None),
        (
            ("external", "certificate-status", "0a1b", "--token", "t"),
            "GET", "/external/certificate-status/0a1b", None,
        ),
        (("external", "ra", "state", "--token", "t"), "GET", "/external/ra/state", None),
        (("external", "ra", "provision", "--token", "t"), "POST", "/external/ra/provision", {}),
        (("external", "ra", "renew", "--token", "t"), "POST", "/external/ra/renew", {}),
        (
            ("external", "ra", "sign", "--token", "t", "--digest", "QUJD"),
            "POST", "/external/ra/sign", {"digest": "QUJD"},
        ),
        (
            ("external", "ra", "decrypt", "--token", "t", "--data", "QUJD"),
            "POST", "/external/ra/decrypt", {"data": "QUJD"},
        ),
        (
            ("external", "ssh", "principals-pushed", "web1.test", "--token", "t",
             "--sha256", "ab" * 32),
            "POST", "/external/ssh/hosts/web1.test/principals-pushed", {"sha256": "ab" * 32},
        ),
    ],
)  # fmt: skip
def test_new_commands_call_the_right_operation(cli, argv, method, path, body):
    api = Recorder()
    result = cli(api.args, *argv)
    assert result.exit_code == 0, result.output
    assert (api.last.method, api.last.url.path) == (method, f"/api/v1{path}")
    if body is None:
        assert api.last.content == b""
    else:
        assert api.body == body
    if argv[0] == "external":
        assert api.last.headers["authorization"] == "Bearer t"


def test_cert_purge_flags(cli):
    api = Recorder()
    argv = ("ssh", "cert", "purge", "c1", "--force", "--force-revoked", "--drop-revocation")
    assert cli(api.args, *argv).exit_code == 0
    assert dict(api.last.url.params) == {"force": "true", "dropRevocation": "true"}

    api = Recorder()
    result = cli(api.args, "ssh", "cert", "purge", "c1", "--force", "--drop-revocation")
    assert result.exit_code == 1 and api.requests == []
