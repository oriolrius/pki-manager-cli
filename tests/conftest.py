"""Shared fixtures."""

from __future__ import annotations

from typing import Callable

import pytest
from typer.testing import CliRunner

from pki_cli import client, config, http
from pki_cli.main import app


@pytest.fixture
def cli(monkeypatch):
    """Run `pki` against a fake server: ``cli(httpx_args_factory, *argv)``.

    ``httpx_args_factory(retries=..., max_wait=...)`` returns the ``httpx.Client``
    arguments (a mock transport) used for every request of the command, for the
    generated client and for the helpers in ``pki_cli.http``.
    """
    state: dict = {}
    unset = ("OIDC_URL", "CLIENT_ID", "CLIENT_SECRET", "TOKEN", "RATE_LIMIT_RETRIES")
    for name in (f"PKI_{suffix}" for suffix in unset):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("PKI_API_URL", "http://pki.test/api/v1")
    monkeypatch.setitem(config.Settings.model_config, "env_file", None)

    def fake_args(settings=None):
        settings = settings or config.get_settings()
        return state["factory"](
            retries=settings.rate_limit_retries, max_wait=settings.rate_limit_max_wait
        )

    monkeypatch.setattr(http, "rate_limit_httpx_args", fake_args)
    monkeypatch.setattr(client, "rate_limit_httpx_args", fake_args)

    def invoke(factory: Callable[..., dict], *argv: str):
        state["factory"] = factory
        return CliRunner().invoke(app, list(argv))

    return invoke
