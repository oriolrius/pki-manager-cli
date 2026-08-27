"""Auth-mode resolution: OIDC, static token, or anonymous.

A *partial* OIDC configuration must be rejected loudly — silently downgrading to
anonymous would surface much later as an opaque 401.
"""

from __future__ import annotations

import pytest

from pki_cli.config import Settings

OIDC = {
    "oidc_url": "https://iam.example/token",
    "client_id": "svc",
    "client_secret": "s3cr3t",
}


def _settings(**overrides) -> Settings:
    # _env_file=None keeps a developer's real ~/.config/pki-cli/.env out of the test.
    return Settings(_env_file=None, **overrides)


def test_api_url_is_the_only_hard_requirement():
    with pytest.raises(ValueError, match="PKI_API_URL"):
        _settings().validate_config()


def test_anonymous_is_allowed():
    settings = _settings(api_url="http://localhost:52081/api/v1")
    settings.validate_config()
    assert not settings.has_oidc


def test_full_oidc_is_allowed():
    settings = _settings(api_url="https://pki.example/api/v1", **OIDC)
    settings.validate_config()
    assert settings.has_oidc


def test_static_token_is_allowed():
    settings = _settings(api_url="https://pki.example/api/v1", token="eyJhbG")
    settings.validate_config()
    assert not settings.has_oidc


@pytest.mark.parametrize("dropped", sorted(OIDC))
def test_partial_oidc_is_rejected(dropped: str):
    partial = {k: v for k, v in OIDC.items() if k != dropped}
    settings = _settings(api_url="https://pki.example/api/v1", **partial)
    with pytest.raises(ValueError, match="Incomplete OIDC configuration"):
        settings.validate_config()


def test_static_token_wins_over_partial_oidc():
    """An explicit token means the half-set OIDC values are simply unused."""
    settings = _settings(api_url="https://pki.example/api/v1", token="eyJhbG", client_id="svc")
    settings.validate_config()
