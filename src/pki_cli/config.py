"""Configuration management for PKI CLI."""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """PKI CLI configuration settings.

    Configuration can be set via:
    1. Environment variables (prefixed with PKI_)
    2. .env file in current directory
    3. ~/.config/pki-cli/.env file
    4. CLI options (--api-url, --client-id, --client-secret)

    Environment variables:
        PKI_API_URL: PKI Manager API base URL
        PKI_OIDC_URL: Keycloak token endpoint
        PKI_CLIENT_ID: OIDC client ID
        PKI_CLIENT_SECRET: OIDC client secret
        PKI_TOKEN: pre-obtained bearer token (skips the OIDC exchange)
        PKI_RATE_LIMIT_RETRIES: times to wait for Retry-After and retry on HTTP 429 (default 0)
        PKI_RATE_LIMIT_MAX_WAIT: longest Retry-After, in seconds, the CLI waits for (default 120)
    """

    model_config = SettingsConfigDict(
        env_prefix="PKI_",
        env_file=(".env", str(Path.home() / ".config" / "pki-cli" / ".env")),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API Configuration
    api_url: Optional[str] = Field(
        default=None,
        description="PKI Manager API base URL (required)",
    )

    # OIDC Configuration
    oidc_url: Optional[str] = Field(
        default=None,
        description="OIDC token endpoint (required)",
    )
    client_id: Optional[str] = Field(
        default=None,
        description="OIDC client ID (required)",
    )
    client_secret: Optional[str] = Field(
        default=None,
        description="OIDC client secret (required)",
    )
    token: Optional[str] = Field(
        default=None,
        description="Pre-obtained bearer token; skips the OIDC client-credentials exchange",
    )

    # HTTP 429 handling (PKI Manager 3.18.0+ rate-limits the API)
    rate_limit_retries: int = Field(
        default=0,
        ge=0,
        description="Times to wait for Retry-After and retry on HTTP 429 (0 = fail at once)",
    )
    rate_limit_max_wait: float = Field(
        default=120.0,
        ge=0,
        description="Longest Retry-After delay, in seconds, the CLI waits for",
    )

    # Output Configuration
    output_format: str = Field(
        default="table",
        description="Default output format: table, json",
    )

    # Token cache
    token_cache_file: Path = Field(
        default=Path.home() / ".cache" / "pki-cli" / "token",
        description="Path to token cache file",
    )

    @property
    def has_oidc(self) -> bool:
        """True when a full client-credentials configuration is available."""
        return bool(self.oidc_url and self.client_id and self.client_secret)

    def validate_config(self) -> None:
        """Validate that enough configuration is set to reach the API.

        Only ``PKI_API_URL`` is strictly required: deployments that run with
        OIDC disabled (``OIDC_ENABLED=false``) accept anonymous calls, and a
        pre-obtained ``PKI_TOKEN`` is an alternative to the OIDC exchange.
        A *partial* OIDC configuration is always an error — it would silently
        downgrade to anonymous and fail later with an opaque 401.
        """
        if not self.api_url:
            raise ValueError(
                "Missing required configuration: PKI_API_URL. "
                "Set it via environment variable, .env file, or --api-url."
            )

        if self.token or self.has_oidc:
            return

        partial = [
            name
            for name, value in (
                ("PKI_OIDC_URL", self.oidc_url),
                ("PKI_CLIENT_ID", self.client_id),
                ("PKI_CLIENT_SECRET", self.client_secret),
            )
            if not value
        ]
        if len(partial) != 3:  # some OIDC settings given, but not all
            raise ValueError(
                f"Incomplete OIDC configuration: {', '.join(partial)} not set. "
                "Provide all three, set PKI_TOKEN, or omit them entirely to call "
                "the API anonymously (only works when the server has OIDC disabled)."
            )


# Global settings instance (lazy initialization)
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the current settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def configure(
    api_url: Optional[str] = None,
    oidc_url: Optional[str] = None,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    token: Optional[str] = None,
    rate_limit_retries: Optional[int] = None,
) -> Settings:
    """Configure settings with optional overrides from CLI.

    CLI options take precedence over environment variables.
    """
    global _settings

    # Start fresh from environment/files
    _settings = Settings()

    # Apply CLI overrides
    if api_url:
        _settings.api_url = api_url
    if oidc_url:
        _settings.oidc_url = oidc_url
    if client_id:
        _settings.client_id = client_id
    if client_secret:
        _settings.client_secret = client_secret
    if token:
        _settings.token = token
    if rate_limit_retries is not None:
        _settings.rate_limit_retries = rate_limit_retries

    return _settings
