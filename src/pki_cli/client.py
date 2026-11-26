"""PKI Manager API client wrapper with OIDC authentication."""

import json
import time
from typing import Optional

import httpx

from pki_api.pki_manager_rest_api_client import AuthenticatedClient, Client

from . import ratelimit
from .config import Settings, get_settings


def _notify(message: str) -> None:
    from .output import print_warning

    print_warning(message)


def rate_limit_httpx_args(settings: Optional[Settings] = None) -> dict:
    """``httpx.Client`` arguments for the HTTP 429 handling, from the settings."""
    settings = settings or get_settings()
    return ratelimit.httpx_args(
        retries=settings.rate_limit_retries,
        max_wait=settings.rate_limit_max_wait,
        notify=_notify,
    )


class TokenManager:
    """Manages OIDC token acquisition and caching."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.cache_file = settings.token_cache_file

    def _get_cached_token(self) -> Optional[str]:
        """Get cached token if still valid."""
        if not self.cache_file.exists():
            return None

        try:
            data = json.loads(self.cache_file.read_text())
            # Check if token expires in more than 30 seconds
            if data.get("expires_at", 0) > time.time() + 30:
                return data.get("access_token")
        except (json.JSONDecodeError, KeyError):
            pass

        return None

    def _cache_token(self, token: str, expires_in: int) -> None:
        """Cache the token to disk."""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "access_token": token,
            "expires_at": time.time() + expires_in,
        }
        self.cache_file.write_text(json.dumps(data))
        self.cache_file.chmod(0o600)

    def clear_cache(self) -> None:
        """Clear the cached token."""
        if self.cache_file.exists():
            self.cache_file.unlink()

    def get_token(self) -> Optional[str]:
        """Get a valid access token, using cache if available.

        Returns ``None`` when the CLI is configured for anonymous access (no
        ``PKI_TOKEN`` and no OIDC credentials), which is what deployments
        running with ``OIDC_ENABLED=false`` expect.
        """
        # Validate configuration is complete
        self.settings.validate_config()

        # A pre-obtained token short-circuits the OIDC exchange entirely
        if self.settings.token:
            return self.settings.token

        if not self.settings.has_oidc:
            return None

        # Try cache first
        cached = self._get_cached_token()
        if cached:
            return cached

        # Fetch new token via client credentials flow
        with httpx.Client() as client:
            response = client.post(
                self.settings.oidc_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.settings.client_id,
                    "client_secret": self.settings.client_secret,
                },
            )

            if response.status_code != 200:
                raise RuntimeError(f"Failed to get token: {response.status_code} - {response.text}")

            data = response.json()

        token = data["access_token"]
        expires_in = data.get("expires_in", 300)

        # Cache for future use
        self._cache_token(token, expires_in)

        return token


class PKIClientWrapper:
    """Wrapper that creates authenticated clients for API calls."""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.token_manager = TokenManager(self.settings)

    def get_client(self) -> AuthenticatedClient | Client:
        """Get a client instance, authenticated when credentials are available."""
        token = self.token_manager.get_token()
        if token is None:
            return Client(
                base_url=self.settings.api_url,
                raise_on_unexpected_status=True,
                httpx_args=rate_limit_httpx_args(self.settings),
            )
        return AuthenticatedClient(
            base_url=self.settings.api_url,
            token=token,
            raise_on_unexpected_status=True,
            httpx_args=rate_limit_httpx_args(self.settings),
        )

    def refresh_token(self) -> AuthenticatedClient | Client:
        """Clear cache and get a fresh token."""
        self.token_manager.clear_cache()
        return self.get_client()


# Global wrapper instance
_wrapper: Optional[PKIClientWrapper] = None


def get_wrapper() -> PKIClientWrapper:
    """Get or create the global client wrapper."""
    global _wrapper
    if _wrapper is None:
        _wrapper = PKIClientWrapper()
    return _wrapper


def get_client() -> AuthenticatedClient | Client:
    """Get a client for API calls (authenticated when credentials are set)."""
    return get_wrapper().get_client()


def reset_wrapper() -> None:
    """Drop the cached wrapper so a new configuration takes effect."""
    global _wrapper
    _wrapper = None
