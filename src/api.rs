//! HTTP client for the four auth surfaces of the PKI Manager API.
//!
//! * OIDC bearer (or `PKI_TOKEN`, or anonymous) for `/api/v1/*`: [`Api::get`] & co.
//! * a raw bearer token for `/api/v1/external/*`: [`Req::bearer`].
//! * no auth, at the server ROOT (`/ssh/*`, `/krl/*`, `/cas/*`): [`Req::public`].
//!
//! Every response is kept as `serde_json::Value`: the CLI renders the server's
//! JSON as it comes, so a field the server adds is never dropped.

use std::cell::RefCell;
use std::fmt;
use std::fs;
use std::io::Write;
use std::sync::Arc;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use anyhow::{Context, Result, anyhow};
use serde_json::Value;
use ureq::Agent;
use ureq::tls::{Certificate, PemItem, RootCerts, TlsConfig};

use crate::config::Settings;
use crate::output;
use crate::ratelimit;

pub const DEFAULT_TIMEOUT: Duration = Duration::from_secs(30);

/// A non-2xx API response (or a client-side failure), with the parsed message.
#[derive(Debug, Clone)]
pub struct ApiError {
    /// HTTP status; 0 when no response came back. (Only the tests read it now.)
    #[allow(dead_code)]
    pub status: u16,
    pub message: String,
}

impl fmt::Display for ApiError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.message)
    }
}

impl std::error::Error for ApiError {}

impl ApiError {
    pub fn new(status: u16, message: impl Into<String>) -> Self {
        ApiError {
            status,
            message: message.into(),
        }
    }
}

/// Pull the API's `{error:{code,message}}` shape out of an error body.
pub fn extract_error(status: u16, body: &str) -> String {
    let text = body.trim();
    let fallback = || {
        if text.is_empty() {
            format!("HTTP {status}")
        } else {
            text.to_string()
        }
    };
    let Ok(data) = serde_json::from_str::<Value>(body) else {
        return fallback();
    };
    match data.get("error") {
        Some(Value::Object(err)) => {
            let code = err.get("code").and_then(Value::as_str).unwrap_or("ERROR");
            let message = err.get("message").and_then(Value::as_str).unwrap_or(text);
            format!("{code}: {message}")
        }
        // Fastify's own errors: {"statusCode":400,"error":"Bad Request","message":"..."}
        Some(Value::String(err)) => match data.get("message").and_then(Value::as_str) {
            Some(m) if !m.is_empty() => format!("{err}: {m}"),
            _ => err.clone(),
        },
        Some(Value::Null) | None => fallback(),
        Some(other) => other.to_string(),
    }
}

/// What a 503 adds to the error: the status, the server's `Retry-After`, and where an
/// admin finds the cause of `KEY_STORE_UNAVAILABLE`. The CLI never resends the request:
/// the server made nothing, so the user sends it again when the key store is back.
fn unavailable_hint(body: &str, retry_after: Option<&str>) -> String {
    let mut hint = " (HTTP 503).".to_string();
    if let Some(delay) = ratelimit::parse_retry_after(retry_after) {
        hint.push_str(&format!(" Retry after {}.", ratelimit::seconds(delay)));
    }
    let code = serde_json::from_str::<Value>(body)
        .ok()
        .and_then(|v| v.get("error")?.get("code")?.as_str().map(str::to_string));
    if code.as_deref() == Some("KEY_STORE_UNAVAILABLE") {
        hint.push_str(" An admin sees the cause with `pki diagnostics key-store`.");
    }
    hint
}

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
enum Base {
    Api,
    Root,
}

#[derive(Clone, Debug)]
enum Auth {
    /// The management API credentials (OIDC, `PKI_TOKEN`, or anonymous).
    Management,
    /// A raw bearer token (cluster/fleet token), or none.
    Bearer(Option<String>),
}

pub struct Response {
    pub content_type: String,
    pub body: Vec<u8>,
}

impl Response {
    /// JSON body as a value; any other content type as a JSON string.
    pub fn value(self) -> Value {
        if self.content_type.contains("application/json") {
            serde_json::from_slice(&self.body)
                .unwrap_or_else(|_| Value::String(String::from_utf8_lossy(&self.body).into_owned()))
        } else {
            Value::String(String::from_utf8_lossy(&self.body).into_owned())
        }
    }
}

pub struct Api {
    settings: Settings,
    agent: Agent,
    token: RefCell<Option<Option<String>>>,
}

impl Api {
    pub fn new(settings: Settings) -> Result<Self> {
        let agent = build_agent(&settings)?;
        Ok(Api {
            settings,
            agent,
            token: RefCell::new(None),
        })
    }

    pub fn settings(&self) -> &Settings {
        &self.settings
    }

    pub fn request(&self, method: &'static str, path: impl Into<String>) -> Req<'_> {
        Req {
            api: self,
            method,
            path: path.into(),
            base: Base::Api,
            auth: Auth::Management,
            query: Vec::new(),
            headers: Vec::new(),
            body: None,
        }
    }

    pub fn get(&self, path: impl Into<String>) -> Req<'_> {
        self.request("GET", path)
    }
    pub fn post(&self, path: impl Into<String>) -> Req<'_> {
        self.request("POST", path)
    }
    pub fn delete(&self, path: impl Into<String>) -> Req<'_> {
        self.request("DELETE", path)
    }

    fn api_url(&self) -> Result<&str, ApiError> {
        self.settings.api_url.as_deref().ok_or_else(|| {
            ApiError::new(
                0,
                "PKI_API_URL is not set (configure it via --api-url, env, or .env)",
            )
        })
    }

    // ---- OIDC token --------------------------------------------------------

    /// The bearer token for the management API, or `None` for anonymous access.
    pub fn token(&self) -> Result<Option<String>> {
        if let Some(t) = self.token.borrow().as_ref() {
            return Ok(t.clone());
        }
        let t = self.resolve_token()?;
        *self.token.borrow_mut() = Some(t.clone());
        Ok(t)
    }

    fn resolve_token(&self) -> Result<Option<String>> {
        self.settings.validate()?;
        if let Some(t) = &self.settings.token {
            return Ok(Some(t.clone()));
        }
        if !self.settings.has_oidc() {
            return Ok(None);
        }
        if let Some(t) = self.cached_token() {
            return Ok(Some(t));
        }
        self.fetch_token().map(Some)
    }

    fn cached_token(&self) -> Option<String> {
        let data: Value =
            serde_json::from_str(&fs::read_to_string(&self.settings.token_cache_file).ok()?)
                .ok()?;
        let expires_at = data.get("expires_at")?.as_f64()?;
        (expires_at > now() + 30.0)
            .then(|| data.get("access_token")?.as_str().map(str::to_string))?
    }

    /// OIDC client-credentials exchange; the token is cached (mode 0600).
    pub fn fetch_token(&self) -> Result<String> {
        let s = &self.settings;
        let url = s
            .oidc_url
            .as_deref()
            .ok_or_else(|| anyhow!("PKI_OIDC_URL is not set"))?;
        let mut resp = self
            .agent
            .post(url)
            .send_form([
                ("grant_type", "client_credentials"),
                ("client_id", s.client_id.as_deref().unwrap_or_default()),
                (
                    "client_secret",
                    s.client_secret.as_deref().unwrap_or_default(),
                ),
            ])
            .map_err(|e| anyhow!("Failed to get token: {e}"))?;
        let status = resp.status().as_u16();
        let text = resp.body_mut().read_to_string().unwrap_or_default();
        if status != 200 {
            return Err(anyhow!("Failed to get token: {status} - {text}"));
        }
        let data: Value =
            serde_json::from_str(&text).context("Failed to get token: the response is not JSON")?;
        let token = data
            .get("access_token")
            .and_then(Value::as_str)
            .ok_or_else(|| anyhow!("Failed to get token: no access_token in the response"))?
            .to_string();
        let expires_in = data
            .get("expires_in")
            .and_then(Value::as_f64)
            .unwrap_or(300.0);
        self.cache_token(&token, expires_in);
        *self.token.borrow_mut() = Some(Some(token.clone()));
        Ok(token)
    }

    fn cache_token(&self, token: &str, expires_in: f64) {
        let path = &self.settings.token_cache_file;
        if let Some(dir) = path.parent() {
            let _ = fs::create_dir_all(dir);
        }
        let data = serde_json::json!({ "access_token": token, "expires_at": now() + expires_in });
        let mut opts = fs::OpenOptions::new();
        opts.write(true).create(true).truncate(true);
        #[cfg(unix)]
        {
            use std::os::unix::fs::OpenOptionsExt;
            opts.mode(0o600);
        }
        if let Ok(mut f) = opts.open(path) {
            let _ = f.write_all(data.to_string().as_bytes());
            #[cfg(unix)]
            {
                use std::os::unix::fs::PermissionsExt;
                let _ = fs::set_permissions(path, fs::Permissions::from_mode(0o600));
            }
        }
    }

    pub fn clear_token_cache(&self) {
        let _ = fs::remove_file(&self.settings.token_cache_file);
        *self.token.borrow_mut() = None;
    }

    // ---- sending -------------------------------------------------------------

    fn send(&self, req: &Req<'_>) -> Result<Response> {
        let base = match req.base {
            Base::Api => self.api_url()?.to_string(),
            Base::Root => self.api_url()?.replace("/api/v1", ""),
        };
        let mut url = format!("{base}{}", req.path);
        if !req.query.is_empty() {
            url.push(if url.contains('?') { '&' } else { '?' });
            let q: Vec<String> = req
                .query
                .iter()
                .map(|(k, v)| format!("{}={}", encode(k), encode(v)))
                .collect();
            url.push_str(&q.join("&"));
        }
        let bearer = match &req.auth {
            Auth::Management => self.token()?,
            Auth::Bearer(t) => t.clone(),
        };
        let body = req.body.as_ref().map(serde_json::to_vec).transpose()?;

        let mut attempt = 0;
        loop {
            let mut builder = ureq::http::Request::builder().method(req.method).uri(&url);
            if let Some(t) = &bearer {
                builder = builder.header("Authorization", format!("Bearer {t}"));
            }
            for (k, v) in &req.headers {
                builder = builder.header(k.as_str(), v.as_str());
            }
            let result = match &body {
                Some(b) => {
                    let r = builder
                        .header("Content-Type", "application/json")
                        .body(b.clone())?;
                    self.agent.run(r)
                }
                None => self.agent.run(builder.body(())?),
            };
            let mut resp =
                result.map_err(|e| ApiError::new(0, format!("Request to {url} failed: {e}")))?;
            let status = resp.status().as_u16();
            let header = |name: &str| {
                resp.headers()
                    .get(name)
                    .and_then(|v| v.to_str().ok())
                    .map(str::to_string)
            };
            let content_type = header("content-type").unwrap_or_default();
            let retry_after = header("retry-after");
            let bytes = resp
                .body_mut()
                .with_config()
                .limit(512 * 1024 * 1024)
                .read_to_vec()
                .map_err(|e| ApiError::new(status, format!("Reading the response failed: {e}")))?;

            if status == 429 {
                if let Some(delay) = ratelimit::retry_delay(
                    attempt,
                    self.settings.rate_limit_retries,
                    self.settings.rate_limit_max_wait,
                    retry_after.as_deref(),
                ) {
                    attempt += 1;
                    output::warning(&format!(
                        "Rate limited (HTTP 429): wait {}, then retry {attempt} of {}",
                        ratelimit::seconds(delay),
                        self.settings.rate_limit_retries
                    ));
                    std::thread::sleep(Duration::from_secs_f64(delay));
                    continue;
                }
                let text = String::from_utf8_lossy(&bytes);
                return Err(ApiError::new(
                    status,
                    ratelimit::rate_limit_message(&text, retry_after.as_deref()),
                )
                .into());
            }
            if status >= 400 {
                let text = String::from_utf8_lossy(&bytes);
                let mut message = extract_error(status, &text);
                if status == 503 {
                    message.push_str(&unavailable_hint(&text, retry_after.as_deref()));
                }
                return Err(ApiError::new(status, message).into());
            }
            if req.base == Base::Root && content_type.contains("text/html") {
                return Err(ApiError::new(
                    502,
                    format!(
                        "{} returned an HTML page, not API data — the public SSH/KRL routes are served \
                         at the server root and appear to be shadowed by the web frontend on this deployment.",
                        req.path
                    ),
                )
                .into());
            }
            return Ok(Response {
                content_type,
                body: bytes,
            });
        }
    }
}

fn now() -> f64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs_f64())
        .unwrap_or(0.0)
}

/// Percent-encode a query component (RFC 3986 unreserved characters kept).
fn encode(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    for b in s.bytes() {
        match b {
            b'A'..=b'Z' | b'a'..=b'z' | b'0'..=b'9' | b'-' | b'_' | b'.' | b'~' => {
                out.push(b as char)
            }
            _ => out.push_str(&format!("%{b:02X}")),
        }
    }
    out
}

fn build_agent(settings: &Settings) -> Result<Agent> {
    let mut tls = TlsConfig::builder();
    let bundle = settings
        .ca_bundle
        .clone()
        .or_else(|| std::env::var_os("SSL_CERT_FILE").map(Into::into));
    if let Some(path) = bundle {
        let pem = fs::read(&path)
            .with_context(|| format!("Cannot read the CA bundle {}", path.display()))?;
        let certs: Vec<Certificate<'static>> = ureq::tls::parse_pem(&pem)
            .filter_map(|item| match item {
                Ok(PemItem::Certificate(c)) => Some(c),
                _ => None,
            })
            .collect();
        if certs.is_empty() {
            return Err(anyhow!(
                "The CA bundle {} has no PEM certificate",
                path.display()
            ));
        }
        tls = tls.root_certs(RootCerts::Specific(Arc::new(certs)));
    }
    Ok(Agent::config_builder()
        .http_status_as_error(false)
        .timeout_global(Some(DEFAULT_TIMEOUT))
        .user_agent(format!("pki-cli/{}", env!("CARGO_PKG_VERSION")))
        .tls_config(tls.build())
        .build()
        .into())
}

/// A request being built. Finish it with [`Req::value`], [`Req::bytes`] or [`Req::send`].
pub struct Req<'a> {
    api: &'a Api,
    method: &'static str,
    path: String,
    base: Base,
    auth: Auth,
    query: Vec<(String, String)>,
    headers: Vec<(String, String)>,
    body: Option<Value>,
}

impl<'a> Req<'a> {
    /// Add a query parameter.
    pub fn query(mut self, key: &str, value: impl ToString) -> Self {
        self.query.push((key.to_string(), value.to_string()));
        self
    }

    /// Add a query parameter when it is `Some`.
    pub fn query_opt<T: ToString>(self, key: &str, value: Option<T>) -> Self {
        match value {
            Some(v) => self.query(key, v),
            None => self,
        }
    }

    /// Add a header when it is `Some`.
    pub fn header_opt(mut self, key: &str, value: Option<impl ToString>) -> Self {
        if let Some(v) = value {
            self.headers.push((key.to_string(), v.to_string()));
        }
        self
    }

    /// Send this JSON body.
    pub fn json(mut self, body: Value) -> Self {
        self.body = Some(body);
        self
    }

    /// Authenticate with this raw bearer token (cluster/fleet token) instead
    /// of the management credentials. `None` sends no `Authorization` header.
    pub fn bearer(mut self, token: Option<String>) -> Self {
        self.auth = Auth::Bearer(token);
        self
    }

    /// An unauthenticated route served at the server ROOT, outside `/api/v1`.
    pub fn public(mut self) -> Self {
        self.base = Base::Root;
        self.auth = Auth::Bearer(None);
        self
    }

    pub fn send(self) -> Result<Response> {
        self.api.send(&self)
    }

    /// The response as JSON (a non-JSON body comes back as a JSON string).
    pub fn value(self) -> Result<Value> {
        Ok(self.send()?.value())
    }

    /// The raw response body.
    pub fn bytes(self) -> Result<Vec<u8>> {
        Ok(self.send()?.body)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::{BufRead, BufReader, Read};
    use std::net::TcpListener;
    use std::sync::mpsc;

    /// A one-thread HTTP server that answers `responses` in order and sends
    /// back each raw request it got.
    fn serve(responses: Vec<String>) -> (String, mpsc::Receiver<String>) {
        let listener = TcpListener::bind("127.0.0.1:0").unwrap();
        let url = format!("http://{}/api/v1", listener.local_addr().unwrap());
        let (tx, rx) = mpsc::channel();
        std::thread::spawn(move || {
            for resp in responses {
                let (stream, _) = listener.accept().unwrap();
                let mut reader = BufReader::new(stream);
                let mut head = String::new();
                let mut len = 0;
                loop {
                    let mut l = String::new();
                    reader.read_line(&mut l).unwrap();
                    if let Some(v) = l.to_lowercase().strip_prefix("content-length:") {
                        len = v.trim().parse().unwrap();
                    }
                    head.push_str(&l);
                    if l == "\r\n" {
                        break;
                    }
                }
                let mut body = vec![0; len];
                reader.read_exact(&mut body).unwrap();
                head.push_str(&String::from_utf8_lossy(&body));
                tx.send(head).unwrap();
                reader.get_mut().write_all(resp.as_bytes()).unwrap();
            }
        });
        (url, rx)
    }

    fn reply(status: &str, ctype: &str, extra: &str, body: &str) -> String {
        format!(
            "HTTP/1.1 {status}\r\nContent-Type: {ctype}\r\nContent-Length: {}\r\n{extra}Connection: close\r\n\r\n{body}",
            body.len()
        )
    }

    fn api(url: &str, token: Option<&str>, retries: u32) -> Api {
        let mut s = Settings::new(
            Some(url.into()),
            None,
            None,
            None,
            token.map(Into::into),
            Some(retries),
            None,
            None,
        );
        s.token_cache_file = std::env::temp_dir().join("pki-cli-test-unused-token");
        Api::new(s).unwrap()
    }

    #[test]
    fn sends_bearer_query_and_json_body() {
        let (url, rx) = serve(vec![reply(
            "200 OK",
            "application/json",
            "",
            r#"{"id":"x"}"#,
        )]);
        let v = api(&url, Some("tok"), 0)
            .post("/cas/")
            .query("limit", 5)
            .query_opt::<String>("skip", None)
            .json(serde_json::json!({"a": 1}))
            .value()
            .unwrap();
        assert_eq!(v["id"], "x");
        let req = rx.recv().unwrap();
        assert!(
            req.starts_with("POST /api/v1/cas/?limit=5 HTTP/1.1"),
            "{req}"
        );
        assert!(
            req.to_lowercase().contains("authorization: bearer tok"),
            "{req}"
        );
        assert!(req.ends_with(r#"{"a":1}"#), "{req}");
    }

    #[test]
    fn api_error_shape_and_status() {
        let body = r#"{"error":{"code":"NOT_FOUND","message":"no such CA"}}"#;
        let (url, _rx) = serve(vec![reply("404 Not Found", "application/json", "", body)]);
        let err = api(&url, None, 0).get("/cas/x").value().unwrap_err();
        let e = err.downcast_ref::<ApiError>().unwrap();
        assert_eq!(
            (e.status, e.message.as_str()),
            (404, "NOT_FOUND: no such CA")
        );
    }

    #[test]
    fn key_store_unavailable_is_not_retried() {
        let body = r#"{"error":{"code":"KEY_STORE_UNAVAILABLE","message":"The key store is unavailable; retry later"}}"#;
        let (url, rx) = serve(vec![reply(
            "503 Service Unavailable",
            "application/json",
            "Retry-After: 30\r\n",
            body,
        )]);
        // Rate-limit retries on: a 503 still fails at once, and the create is sent once.
        let err = api(&url, None, 3)
            .post("/cas/")
            .json(serde_json::json!({"a": 1}))
            .value()
            .unwrap_err();
        let e = err.downcast_ref::<ApiError>().unwrap();
        assert_eq!(e.status, 503);
        assert_eq!(
            e.message,
            "KEY_STORE_UNAVAILABLE: The key store is unavailable; retry later (HTTP 503). \
             Retry after 30 s. An admin sees the cause with `pki diagnostics key-store`."
        );
        assert!(rx.recv().unwrap().starts_with("POST /api/v1/cas/ "));
        assert!(rx.try_recv().is_err(), "the request was sent once");
    }

    #[test]
    fn other_errors_keep_their_message() {
        assert_eq!(unavailable_hint("<html>", None), " (HTTP 503).");
        let conflict = r#"{"error":{"code":"KEY_MIGRATION_REQUIRED","message":"m"}}"#;
        let (url, _rx) = serve(vec![reply(
            "409 Conflict",
            "application/json",
            "",
            conflict,
        )]);
        let err = api(&url, None, 0)
            .get("/cas/x/download")
            .value()
            .unwrap_err();
        let e = err.downcast_ref::<ApiError>().unwrap();
        assert_eq!(
            (e.status, e.message.as_str()),
            (409, "KEY_MIGRATION_REQUIRED: m")
        );
    }

    #[test]
    fn rate_limit_waits_then_succeeds() {
        let limited = reply(
            "429 Too Many Requests",
            "application/json",
            "Retry-After: 0\r\n",
            "{}",
        );
        let ok = reply("200 OK", "application/json", "", r#"{"ok":true}"#);
        let (url, _rx) = serve(vec![limited, ok]);
        assert_eq!(
            api(&url, None, 1).get("/health").value().unwrap()["ok"],
            true
        );
    }

    #[test]
    fn rate_limit_without_retries_fails() {
        let body = r#"{"error":{"code":"RATE_LIMITED","message":"Slow down"}}"#;
        let (url, _rx) = serve(vec![reply(
            "429 Too Many Requests",
            "application/json",
            "Retry-After: 3\r\n",
            body,
        )]);
        let err = api(&url, None, 0).get("/health").value().unwrap_err();
        let e = err.downcast_ref::<ApiError>().unwrap();
        assert_eq!(e.status, 429);
        assert!(
            e.message
                .starts_with("RATE_LIMITED: Slow down (HTTP 429). Retry after 3 s."),
            "{}",
            e.message
        );
    }

    #[test]
    fn public_route_at_root_rejects_html() {
        let (url, rx) = serve(vec![reply("200 OK", "text/html", "", "<html></html>")]);
        let err = api(&url, Some("tok"), 0)
            .get("/ssh/cert-authority")
            .public()
            .bytes()
            .unwrap_err();
        assert_eq!(err.downcast_ref::<ApiError>().unwrap().status, 502);
        let req = rx.recv().unwrap();
        assert!(req.starts_with("GET /ssh/cert-authority HTTP/1.1"), "{req}");
        assert!(
            !req.to_lowercase().contains("authorization"),
            "public routes send no token"
        );
    }

    #[test]
    fn error_shapes() {
        assert_eq!(
            extract_error(
                400,
                r#"{"error":{"code":"VALIDATION_ERROR","message":"bad SAN"}}"#
            ),
            "VALIDATION_ERROR: bad SAN"
        );
        assert_eq!(
            extract_error(
                400,
                r#"{"statusCode":400,"error":"Bad Request","message":"body/x is required"}"#
            ),
            "Bad Request: body/x is required"
        );
        assert_eq!(extract_error(502, ""), "HTTP 502");
        assert_eq!(extract_error(500, "boom\n"), "boom");
        assert_eq!(
            extract_error(404, r#"{"message":"nope"}"#),
            r#"{"message":"nope"}"#
        );
    }

    #[test]
    fn encodes_query() {
        assert_eq!(encode("a b&c=d/é"), "a%20b%26c%3Dd%2F%C3%A9");
        assert_eq!(encode("CN-1_x.y~"), "CN-1_x.y~");
    }
}
