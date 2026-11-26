//! Command groups. Each module has a `clap` subcommand enum and a `run` function.
//!
//! Conventions every module follows:
//! * Return `anyhow::Result<()>`; `main` prints the error as `✗ <message>` and exits 1.
//! * `-o/--output table|json` picks the view. JSON is the server's JSON, verbatim.
//! * Status lines (`output::success`/`note`) go to stderr; data goes to stdout.
//! * Build request bodies with [`body`]: `null` fields are dropped, as unset options.

pub mod audit;
pub mod bulk;
pub mod ca;
pub mod cert;
pub mod crl;
pub mod external;
pub mod general;
pub mod ssh;

use std::io::{BufRead, IsTerminal, Write};
use std::path::Path;

use anyhow::{Context, Result, bail};
use clap::ValueEnum;
use serde_json::{Map, Value};

use crate::output;

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq, ValueEnum)]
pub enum Format {
    #[default]
    Table,
    Json,
}

impl Format {
    pub fn is_json(self) -> bool {
        self == Format::Json
    }
}

/// Render `data` as JSON, or call `table` with it.
pub fn render(data: &Value, format: Format, table: impl FnOnce(&Value)) {
    if format.is_json() {
        output::json(data)
    } else {
        table(data)
    }
}

/// The user declined a confirmation prompt (exit 1, like `typer.Abort`).
#[derive(Debug)]
pub struct Aborted;

impl std::fmt::Display for Aborted {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str("Aborted!")
    }
}

impl std::error::Error for Aborted {}

/// Exit 1 without a message (the command already printed why).
#[derive(Debug)]
pub struct SilentExit;

impl std::fmt::Display for SilentExit {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str("exit 1")
    }
}

impl std::error::Error for SilentExit {}

/// Ask `prompt [y/N]` on stderr unless `force`. A "no" (or no TTY input) aborts.
pub fn confirm(prompt: &str, force: bool) -> Result<()> {
    if force {
        return Ok(());
    }
    eprint!("{prompt} [y/N]: ");
    std::io::stderr().flush().ok();
    let mut answer = String::new();
    std::io::stdin().lock().read_line(&mut answer).ok();
    let yes = matches!(answer.trim().to_lowercase().as_str(), "y" | "yes");
    if !yes {
        if !std::io::stdin().is_terminal() && answer.is_empty() {
            eprintln!();
        }
        return Err(Aborted.into());
    }
    Ok(())
}

/// A JSON object from `(key, value)` pairs; `null` values are dropped.
pub fn body<const N: usize>(pairs: [(&str, Value); N]) -> Value {
    let mut map = Map::new();
    for (k, v) in pairs {
        if !v.is_null() {
            map.insert(k.to_string(), v);
        }
    }
    Value::Object(map)
}

/// `Some(vec)` only when the vector has items (an empty repeatable flag is "unset").
pub fn non_empty<T>(v: Vec<T>) -> Option<Vec<T>> {
    if v.is_empty() { None } else { Some(v) }
}

/// `value` verbatim, or the contents of `path` for `@path` (multi-line PEM / OpenSSH keys).
pub fn read_value_or_file(value: Option<String>) -> Result<Option<String>> {
    match value {
        Some(v) if v.starts_with('@') => {
            let path = expand_home(&v[1..]);
            Ok(Some(
                std::fs::read_to_string(&path).with_context(|| format!("Cannot read {path}"))?,
            ))
        }
        other => Ok(other),
    }
}

pub fn expand_home(path: &str) -> String {
    if let (Some(rest), Some(home)) = (path.strip_prefix("~/"), dirs::home_dir()) {
        return home.join(rest).display().to_string();
    }
    path.to_string()
}

/// Decode a base64 `data` field and write it to `path`.
pub fn write_base64(data: &Value, path: &Path) -> Result<usize> {
    use base64::Engine;
    let Some(b64) = data
        .get("data")
        .and_then(Value::as_str)
        .filter(|s| !s.is_empty())
    else {
        bail!("No certificate data in response");
    };
    let bytes = base64::engine::general_purpose::STANDARD
        .decode(b64.trim())
        .context("The response data is not valid base64")?;
    std::fs::write(path, &bytes).with_context(|| format!("Cannot write {}", path.display()))?;
    Ok(bytes.len())
}

/// Write bytes to a file, with the path in the error.
pub fn write_file(path: &Path, bytes: &[u8]) -> Result<()> {
    std::fs::write(path, bytes).with_context(|| format!("Cannot write {}", path.display()))
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn body_drops_nulls() {
        let b = body([
            ("a", json!(1)),
            ("b", Value::Null),
            ("c", json!(Option::<String>::None)),
        ]);
        assert_eq!(b, json!({"a": 1}));
    }

    #[test]
    fn value_or_file() {
        let dir = tempfile::tempdir().unwrap();
        let p = dir.path().join("k.pub");
        std::fs::write(&p, "ssh-ed25519 AAAA").unwrap();
        assert_eq!(
            read_value_or_file(Some(format!("@{}", p.display())))
                .unwrap()
                .unwrap(),
            "ssh-ed25519 AAAA"
        );
        assert_eq!(
            read_value_or_file(Some("inline".into())).unwrap().unwrap(),
            "inline"
        );
        assert!(read_value_or_file(None).unwrap().is_none());
    }
}
