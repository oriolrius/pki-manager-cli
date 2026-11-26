//! Output: tables and panels on stdout, status lines on stderr.
//!
//! Status lines (`✓`, `✗`, `⚠`, notes) go to stderr so `-o json` output stays
//! pipeable into `jq`. Colours appear only on a terminal and never with `NO_COLOR`.

use std::io::IsTerminal;

use chrono::{DateTime, Utc};
use comfy_table::presets::{NOTHING, UTF8_FULL_CONDENSED};
use comfy_table::{Attribute, Cell, CellAlignment, Color, ContentArrangement, Table};
use serde_json::Value;

/// Max width of a cell in [`records`] tables (longer values end with `…`).
const RECORD_CELL_MAX: usize = 44;

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Tone {
    Plain,
    Dim,
    Bold,
    Cyan,
    BoldCyan,
    Magenta,
    Yellow,
    Green,
    Red,
}

fn no_color() -> bool {
    std::env::var_os("NO_COLOR").is_some_and(|v| !v.is_empty())
}

fn ansi(tone: Tone) -> &'static str {
    match tone {
        Tone::Plain => "",
        Tone::Dim => "\x1b[2m",
        Tone::Bold => "\x1b[1m",
        Tone::Cyan => "\x1b[36m",
        Tone::BoldCyan => "\x1b[1;36m",
        Tone::Magenta => "\x1b[35m",
        Tone::Yellow => "\x1b[33m",
        Tone::Green => "\x1b[32m",
        Tone::Red => "\x1b[31m",
    }
}

fn paint(text: &str, tone: Tone, terminal: bool) -> String {
    if tone == Tone::Plain || !terminal || no_color() {
        text.to_string()
    } else {
        format!("{}{text}\x1b[0m", ansi(tone))
    }
}

/// A line on stdout in a tone (for example the `12 of 300` footers).
pub fn line(text: &str, tone: Tone) {
    println!("{}", paint(text, tone, std::io::stdout().is_terminal()));
}

fn status_line(symbol: &str, message: &str, tone: Tone) {
    let tty = std::io::stderr().is_terminal();
    eprintln!(
        "{} {}",
        paint(symbol, tone, tty),
        paint(
            message,
            if tone == Tone::Green {
                Tone::Plain
            } else {
                tone
            },
            tty
        )
    );
}

pub fn success(message: &str) {
    status_line("✓", message, Tone::Green);
}

pub fn error(message: &str) {
    status_line("✗", message, Tone::Red);
}

pub fn warning(message: &str) {
    status_line("⚠", message, Tone::Yellow);
}

/// A dim informational note (stderr).
pub fn note(message: &str) {
    eprintln!(
        "{}",
        paint(message, Tone::Dim, std::io::stderr().is_terminal())
    );
}

/// Pretty JSON on stdout (2-space indent, keys in server order).
pub fn json(data: &Value) {
    println!(
        "{}",
        serde_json::to_string_pretty(data).unwrap_or_else(|_| data.to_string())
    );
}

// ---- value helpers -------------------------------------------------------------

/// `obj[key]` as display text, `-` when absent or null.
pub fn text(obj: &Value, key: &str) -> String {
    match obj.get(key) {
        None | Some(Value::Null) => "-".into(),
        Some(v) => scalar(v),
    }
}

/// The first of `keys` that is present and not null/empty.
pub fn first<'a>(obj: &'a Value, keys: &[&str]) -> Option<&'a Value> {
    keys.iter()
        .filter_map(|k| obj.get(*k))
        .find(|v| !v.is_null() && v.as_str() != Some(""))
}

/// Any value as a single table cell.
pub fn scalar(value: &Value) -> String {
    match value {
        Value::Null => "-".into(),
        Value::Bool(b) => b.to_string(),
        Value::String(s) => s.clone(),
        Value::Number(n) => n.to_string(),
        other => serde_json::to_string(other).unwrap_or_default(),
    }
}

/// `2026-01-02T03:04:05Z` → `2026-01-02 03:04`. Epoch seconds/ms work too.
pub fn format_date(value: Option<&Value>) -> String {
    match value {
        None | Some(Value::Null) => "-".into(),
        Some(Value::String(s)) => DateTime::parse_from_rfc3339(s)
            .map(|d| d.with_timezone(&Utc).format("%Y-%m-%d %H:%M").to_string())
            .unwrap_or_else(|_| s.clone()),
        Some(Value::Number(n)) => {
            let raw = n.as_f64().unwrap_or(0.0);
            let secs = if raw > 1e12 { raw / 1000.0 } else { raw };
            DateTime::<Utc>::from_timestamp(secs as i64, 0)
                .map(|d| d.format("%Y-%m-%d %H:%M").to_string())
                .unwrap_or_else(|| n.to_string())
        }
        Some(other) => scalar(other),
    }
}

/// `CN=...` out of a subject DN, else the first 40 characters.
pub fn extract_cn(subject: &str) -> String {
    for part in subject.split(',') {
        if let Some(cn) = part.trim().strip_prefix("CN=") {
            return cn.to_string();
        }
    }
    subject.chars().take(40).collect()
}

/// An entity's subject DN: flat `subject`/`subjectDn` string, or a structured `subject` object.
pub fn subject_of(entity: &Value) -> String {
    match first(entity, &["subjectDn", "subject"]) {
        Some(Value::Object(s)) => {
            let parts: Vec<String> = [
                ("CN", "commonName"),
                ("OU", "organizationalUnit"),
                ("O", "organization"),
                ("L", "locality"),
                ("ST", "state"),
                ("C", "country"),
            ]
            .iter()
            .filter_map(|(short, key)| {
                s.get(*key)
                    .and_then(Value::as_str)
                    .filter(|v| !v.is_empty())
                    .map(|v| format!("{short}={v}"))
            })
            .collect();
            if parts.is_empty() {
                "-".into()
            } else {
                parts.join(",")
            }
        }
        Some(v) => scalar(v),
        None => "-".into(),
    }
}

// ---- cells and tables -----------------------------------------------------------

fn color(tone: Tone) -> Option<Color> {
    match tone {
        Tone::Cyan | Tone::BoldCyan => Some(Color::Cyan),
        Tone::Magenta => Some(Color::Magenta),
        Tone::Yellow => Some(Color::Yellow),
        Tone::Green => Some(Color::Green),
        Tone::Red => Some(Color::Red),
        Tone::Dim => Some(Color::DarkGrey),
        Tone::Plain | Tone::Bold => None,
    }
}

pub fn cell(text: impl Into<String>, tone: Tone) -> Cell {
    let mut c = Cell::new(text.into());
    if no_color() {
        return c;
    }
    if let Some(col) = color(tone) {
        c = c.fg(col);
    }
    if matches!(tone, Tone::Bold | Tone::BoldCyan) {
        c = c.add_attribute(Attribute::Bold);
    }
    c
}

/// A status cell: active green, revoked red, expired yellow.
pub fn status_cell(status: &str) -> Cell {
    let tone = match status.to_lowercase().as_str() {
        "active" | "valid" | "ok" => Tone::Green,
        "revoked" => Tone::Red,
        "expired" | "expiring" | "expiring_soon" => Tone::Yellow,
        _ => Tone::Plain,
    };
    cell(status, tone)
}

/// A days-remaining cell: ≤7 red, ≤30 yellow, else green.
pub fn days_cell(days: &Value) -> Cell {
    let n = days.as_i64().unwrap_or(0);
    let tone = if n <= 7 {
        Tone::Red
    } else if n <= 30 {
        Tone::Yellow
    } else {
        Tone::Green
    };
    cell(scalar(days), tone)
}

/// A list table with a title and tinted columns.
pub struct ListTable {
    title: Option<String>,
    table: Table,
}

impl ListTable {
    pub fn new(title: Option<&str>, columns: &[(&str, Tone)]) -> Self {
        let mut table = Table::new();
        table
            .load_style(UTF8_FULL_CONDENSED)
            .set_content_arrangement(ContentArrangement::Dynamic)
            .set_header(columns.iter().map(|(name, _)| cell(*name, Tone::Bold)));
        ListTable {
            title: title.map(str::to_string),
            table,
        }
    }

    pub fn right_align(&mut self, column: usize) -> &mut Self {
        if let Some(c) = self.table.column_mut(column) {
            c.set_cell_alignment(CellAlignment::Right);
        }
        self
    }

    pub fn row(&mut self, cells: Vec<Cell>) -> &mut Self {
        self.table.add_row(cells);
        self
    }

    pub fn print(&self) {
        if let Some(t) = &self.title {
            line(t, Tone::Bold);
        }
        println!("{}", self.table.trim_fmt());
    }
}

/// A key/value panel (the detail views).
pub struct Panel {
    title: Option<String>,
    table: Table,
}

impl Panel {
    pub fn new(title: Option<&str>) -> Self {
        let mut table = Table::new();
        table.load_style(if title.is_some() {
            UTF8_FULL_CONDENSED
        } else {
            NOTHING
        });
        table.set_content_arrangement(ContentArrangement::Dynamic);
        Panel {
            title: title.map(str::to_string),
            table,
        }
    }

    pub fn row(&mut self, field: &str, value: impl Into<String>) -> &mut Self {
        self.cell_row(field, Cell::new(value.into()))
    }

    pub fn cell_row(&mut self, field: &str, value: Cell) -> &mut Self {
        self.table.add_row(vec![cell(field, Tone::BoldCyan), value]);
        self
    }

    pub fn print(&self) {
        if let Some(t) = &self.title {
            line(t, Tone::Bold);
        }
        println!("{}", self.table.trim_fmt());
    }
}

fn truncate(s: String, max: usize) -> String {
    if s.chars().count() <= max {
        s
    } else {
        let mut t: String = s.chars().take(max - 1).collect();
        t.push('…');
        t
    }
}

/// A list of objects as a table, columns inferred when not given.
///
/// Schema-agnostic on purpose: it never fails on a missing key.
pub fn records(items: &[Value], columns: Option<&[&str]>, title: Option<&str>) {
    if items.is_empty() {
        line("No results", Tone::Dim);
        return;
    }
    let cols: Vec<String> = match columns {
        Some(c) => c.iter().map(|s| s.to_string()).collect(),
        None => {
            let mut cols: Vec<String> = Vec::new();
            for item in items {
                if let Value::Object(map) = item {
                    for k in map.keys() {
                        if !cols.contains(k) {
                            cols.push(k.clone());
                        }
                    }
                }
            }
            cols
        }
    };
    if cols.is_empty() {
        let mut t = ListTable::new(title, &[("Value", Tone::Plain)]);
        for item in items {
            t.row(vec![Cell::new(truncate(scalar(item), RECORD_CELL_MAX))]);
        }
        t.print();
        return;
    }
    let header: Vec<(&str, Tone)> = cols.iter().map(|c| (c.as_str(), Tone::Plain)).collect();
    let mut t = ListTable::new(title, &header);
    for item in items {
        let row = if item.is_object() {
            cols.iter()
                .map(|c| {
                    Cell::new(truncate(
                        item.get(c).map(scalar).unwrap_or_else(|| "-".into()),
                        RECORD_CELL_MAX,
                    ))
                })
                .collect()
        } else {
            let mut r = vec![Cell::new(truncate(scalar(item), RECORD_CELL_MAX))];
            r.extend((1..cols.len()).map(|_| Cell::new("")));
            r
        };
        t.row(row);
    }
    t.print();
}

/// One object as a key/value panel (anything else as JSON).
pub fn kv(obj: &Value, title: Option<&str>) {
    let Value::Object(map) = obj else {
        json(obj);
        return;
    };
    let mut p = Panel::new(title);
    for (k, v) in map {
        p.row(k, scalar(v));
    }
    p.print();
}

/// `items` of a list response: the array itself, or its `items`/`data` field.
pub fn items(data: &Value) -> Vec<Value> {
    match data {
        Value::Array(a) => a.clone(),
        Value::Object(_) => first(data, &["items", "data", "results"])
            .and_then(Value::as_array)
            .cloned()
            .unwrap_or_default(),
        _ => Vec::new(),
    }
}

/// `25 of 312 CAs (use --limit/--offset to page)` when a listing is truncated.
pub fn pagination(data: &Value, shown: usize, noun: &str) {
    if let Some(total) = data
        .get("pagination")
        .and_then(|p| p.get("total"))
        .and_then(Value::as_u64)
        && total != shown as u64
    {
        line(
            &format!("{shown} of {total} {noun} (use --limit/--offset to page)"),
            Tone::Dim,
        );
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn cn_extraction() {
        assert_eq!(
            extract_cn("CN=web.example.com,O=Acme,C=ES"),
            "web.example.com"
        );
        assert_eq!(extract_cn("O=Acme, CN=x"), "x");
        assert_eq!(extract_cn("O=Acme"), "O=Acme");
    }

    #[test]
    fn subject_flat_and_structured() {
        assert_eq!(subject_of(&json!({"subject": "CN=a,O=b"})), "CN=a,O=b");
        assert_eq!(
            subject_of(
                &json!({"subjectDn": "", "subject": {"commonName": "a", "organization": "b", "country": "ES"}})
            ),
            "CN=a,O=b,C=ES"
        );
        assert_eq!(subject_of(&json!({})), "-");
    }

    #[test]
    fn dates() {
        assert_eq!(
            format_date(Some(&json!("2026-01-02T03:04:05.000Z"))),
            "2026-01-02 03:04"
        );
        assert_eq!(format_date(Some(&json!(1767323045))), "2026-01-02 03:04");
        assert_eq!(
            format_date(Some(&json!(1767323045000u64))),
            "2026-01-02 03:04"
        );
        assert_eq!(format_date(None), "-");
        assert_eq!(format_date(Some(&json!("not a date"))), "not a date");
    }

    #[test]
    fn scalars() {
        assert_eq!(scalar(&json!(null)), "-");
        assert_eq!(scalar(&json!(true)), "true");
        assert_eq!(scalar(&json!([1, "a"])), r#"[1,"a"]"#);
        assert_eq!(scalar(&json!({"k": 1})), r#"{"k":1}"#);
    }

    #[test]
    fn list_items() {
        assert_eq!(items(&json!([1, 2])).len(), 2);
        assert_eq!(items(&json!({"items": [1], "pagination": {}})).len(), 1);
        assert_eq!(items(&json!({"other": 1})).len(), 0);
    }

    #[test]
    fn truncation() {
        assert_eq!(truncate("abc".into(), 5), "abc");
        assert_eq!(truncate("abcdef".into(), 4), "abc…");
    }
}
