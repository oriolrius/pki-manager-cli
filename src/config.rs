//! Configuration: CLI options > environment > `./.env` > `~/.config/pki-cli/.env`.

use std::path::PathBuf;

use anyhow::{Result, bail};

/// Load the `.env` files into the process environment.
///
/// A variable that is already set is never replaced, so the order of
/// precedence is: real environment, then `./.env`, then the global file.
/// `clap` reads every `PKI_*` option from the environment after this.
pub fn load_dotenv() {
    let _ = dotenvy::from_path(".env");
    if let Some(dir) = dirs::config_dir().or_else(|| dirs::home_dir().map(|h| h.join(".config"))) {
        let _ = dotenvy::from_path(dir.join("pki-cli").join(".env"));
    }
    // ~/.config is the documented place on every OS (dirs::config_dir differs on macOS/Windows).
    if let Some(home) = dirs::home_dir() {
        let _ = dotenvy::from_path(home.join(".config").join("pki-cli").join(".env"));
    }
}

#[derive(Debug, Clone, Default)]
pub struct Settings {
    pub api_url: Option<String>,
    pub oidc_url: Option<String>,
    pub client_id: Option<String>,
    pub client_secret: Option<String>,
    pub token: Option<String>,
    pub rate_limit_retries: u32,
    pub rate_limit_max_wait: f64,
    pub ca_bundle: Option<PathBuf>,
    pub token_cache_file: PathBuf,
}

pub fn default_token_cache() -> PathBuf {
    dirs::home_dir()
        .unwrap_or_else(|| PathBuf::from("."))
        .join(".cache")
        .join("pki-cli")
        .join("token")
}

fn non_empty(v: Option<String>) -> Option<String> {
    v.filter(|s| !s.is_empty())
}

impl Settings {
    #[allow(clippy::too_many_arguments)]
    pub fn new(
        api_url: Option<String>,
        oidc_url: Option<String>,
        client_id: Option<String>,
        client_secret: Option<String>,
        token: Option<String>,
        rate_limit_retries: Option<u32>,
        rate_limit_max_wait: Option<f64>,
        ca_bundle: Option<PathBuf>,
    ) -> Self {
        Settings {
            api_url: non_empty(api_url).map(|u| u.trim_end_matches('/').to_string()),
            oidc_url: non_empty(oidc_url),
            client_id: non_empty(client_id),
            client_secret: non_empty(client_secret),
            token: non_empty(token),
            rate_limit_retries: rate_limit_retries.unwrap_or(0),
            rate_limit_max_wait: rate_limit_max_wait.unwrap_or(120.0).max(0.0),
            ca_bundle,
            token_cache_file: std::env::var_os("PKI_TOKEN_CACHE_FILE")
                .map(PathBuf::from)
                .unwrap_or_else(default_token_cache),
        }
    }

    /// True when a full client-credentials configuration is available.
    pub fn has_oidc(&self) -> bool {
        self.oidc_url.is_some() && self.client_id.is_some() && self.client_secret.is_some()
    }

    /// Only `PKI_API_URL` is required. A *partial* OIDC configuration is an
    /// error: it would silently fall back to anonymous and fail later with 401.
    pub fn validate(&self) -> Result<()> {
        if self.api_url.is_none() {
            bail!(
                "Missing required configuration: PKI_API_URL. \
                 Set it via environment variable, .env file, or --api-url."
            );
        }
        if self.token.is_some() || self.has_oidc() {
            return Ok(());
        }
        let missing: Vec<&str> = [
            ("PKI_OIDC_URL", &self.oidc_url),
            ("PKI_CLIENT_ID", &self.client_id),
            ("PKI_CLIENT_SECRET", &self.client_secret),
        ]
        .iter()
        .filter(|(_, v)| v.is_none())
        .map(|(n, _)| *n)
        .collect();
        if missing.len() != 3 {
            bail!(
                "Incomplete OIDC configuration: {} not set. Provide all three, set PKI_TOKEN, \
                 or omit them entirely to call the API anonymously (only works when the server \
                 has OIDC disabled).",
                missing.join(", ")
            );
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn s(
        api: Option<&str>,
        oidc: Option<&str>,
        id: Option<&str>,
        secret: Option<&str>,
        tok: Option<&str>,
    ) -> Settings {
        Settings::new(
            api.map(Into::into),
            oidc.map(Into::into),
            id.map(Into::into),
            secret.map(Into::into),
            tok.map(Into::into),
            None,
            None,
            None,
        )
    }

    #[test]
    fn api_url_required() {
        assert!(s(None, None, None, None, None).validate().is_err());
    }

    #[test]
    fn anonymous_ok() {
        assert!(
            s(Some("http://x/api/v1"), None, None, None, None)
                .validate()
                .is_ok()
        );
    }

    #[test]
    fn token_ok() {
        assert!(
            s(Some("http://x"), None, Some("id"), None, Some("t"))
                .validate()
                .is_ok()
        );
    }

    #[test]
    fn partial_oidc_rejected() {
        let err = s(Some("http://x"), Some("http://idp"), None, None, None)
            .validate()
            .unwrap_err();
        let msg = err.to_string();
        assert!(
            msg.contains("PKI_CLIENT_ID") && msg.contains("PKI_CLIENT_SECRET"),
            "{msg}"
        );
        assert!(!msg.contains("PKI_OIDC_URL"));
    }

    #[test]
    fn full_oidc_ok() {
        let st = s(Some("http://x/"), Some("o"), Some("i"), Some("s"), None);
        assert!(st.validate().is_ok());
        assert!(st.has_oidc());
        assert_eq!(st.api_url.as_deref(), Some("http://x"));
    }
}
