//! HTTP 429 handling shared by every request the CLI sends.
//!
//! PKI Manager 3.18.0+ rate-limits its API. A limited request gets `429` with
//! `{"error":{"code":"RATE_LIMITED",...}}` and, in most cases, `Retry-After`.
//! The CLI waits and retries only when asked (`PKI_RATE_LIMIT_RETRIES`, default 0).

use std::time::{Duration, SystemTime};

/// Seconds to wait from a `Retry-After` header (delta-seconds or HTTP-date).
pub fn parse_retry_after(value: Option<&str>) -> Option<f64> {
    let value = value?.trim();
    if value.is_empty() {
        return None;
    }
    if let Ok(secs) = value.parse::<f64>() {
        return secs.is_finite().then_some(secs.max(0.0));
    }
    let when = httpdate::parse_http_date(value).ok()?;
    Some(
        when.duration_since(SystemTime::now())
            .unwrap_or(Duration::ZERO)
            .as_secs_f64(),
    )
}

/// Format seconds like Python's `f"{value:g} s"` (no trailing `.0`).
pub fn seconds(value: f64) -> String {
    if value.fract() == 0.0 && value.abs() < 1e15 {
        format!("{} s", value as i64)
    } else {
        let s = format!("{value:.6}");
        format!("{} s", s.trim_end_matches('0').trim_end_matches('.'))
    }
}

/// Error text for a 429 response body + `Retry-After` header.
pub fn rate_limit_message(body: &str, retry_after: Option<&str>) -> String {
    let detail = serde_json::from_str::<serde_json::Value>(body)
        .ok()
        .and_then(|v| v.get("error")?.get("message")?.as_str().map(str::to_string))
        .filter(|m| !m.is_empty())
        .unwrap_or_else(|| "Too many requests".to_string());
    match parse_retry_after(retry_after) {
        None => format!("RATE_LIMITED: {detail} (HTTP 429). Retry later."),
        Some(delay) => format!(
            "RATE_LIMITED: {detail} (HTTP 429). Retry after {}. Set PKI_RATE_LIMIT_RETRIES \
             (or --rate-limit-retries) to wait and retry automatically.",
            seconds(delay)
        ),
    }
}

/// What to do with a 429: `Some(delay)` to wait and retry, `None` to give up.
pub fn retry_delay(
    attempt: u32,
    retries: u32,
    max_wait: f64,
    retry_after: Option<&str>,
) -> Option<f64> {
    if attempt >= retries {
        return None;
    }
    parse_retry_after(retry_after).filter(|d| *d <= max_wait)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_delta_seconds() {
        assert_eq!(parse_retry_after(Some("7")), Some(7.0));
        assert_eq!(parse_retry_after(Some(" 1.5 ")), Some(1.5));
        assert_eq!(parse_retry_after(Some("-3")), Some(0.0));
        assert_eq!(parse_retry_after(None), None);
        assert_eq!(parse_retry_after(Some("")), None);
        assert_eq!(parse_retry_after(Some("soon")), None);
    }

    #[test]
    fn parses_http_date() {
        let future = SystemTime::now() + Duration::from_secs(30);
        let header = httpdate::fmt_http_date(future);
        let d = parse_retry_after(Some(&header)).unwrap();
        assert!((25.0..=31.0).contains(&d), "{d}");
        assert_eq!(
            parse_retry_after(Some("Wed, 21 Oct 2015 07:28:00 GMT")),
            Some(0.0)
        );
    }

    #[test]
    fn message_with_and_without_retry_after() {
        let body = r#"{"error":{"code":"RATE_LIMITED","message":"Slow down"}}"#;
        let m = rate_limit_message(body, Some("5"));
        assert!(
            m.starts_with("RATE_LIMITED: Slow down (HTTP 429). Retry after 5 s."),
            "{m}"
        );
        assert!(m.contains("PKI_RATE_LIMIT_RETRIES"));
        let m = rate_limit_message("<html>", None);
        assert_eq!(
            m,
            "RATE_LIMITED: Too many requests (HTTP 429). Retry later."
        );
    }

    #[test]
    fn retry_policy() {
        assert_eq!(retry_delay(0, 0, 120.0, Some("1")), None, "off by default");
        assert_eq!(retry_delay(0, 2, 120.0, Some("1")), Some(1.0));
        assert_eq!(retry_delay(2, 2, 120.0, Some("1")), None, "no retry left");
        assert_eq!(retry_delay(0, 2, 120.0, None), None, "no Retry-After");
        assert_eq!(retry_delay(0, 2, 10.0, Some("60")), None, "too long");
    }

    #[test]
    fn seconds_format() {
        assert_eq!(seconds(5.0), "5 s");
        assert_eq!(seconds(1.5), "1.5 s");
    }
}
