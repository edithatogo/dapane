//! Minimal strict RFC 8259 JSON parser and deterministic serializer.

use std::collections::BTreeMap;
use std::fmt::Write;

use crate::model::{ErrorCode, ModelError};

const MAX_JSON_DEPTH: usize = 32;

/// Strict JSON value preserving object key ordering (`BTreeMap`) and exact number lexemes.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum JsonValue {
    /// JSON `null`.
    Null,
    /// JSON boolean (`true` or `false`).
    Bool(bool),
    /// Validated RFC 8259 JSON number text.
    Number(String),
    /// JSON string.
    String(String),
    /// JSON array.
    Array(Vec<JsonValue>),
    /// JSON object with unique keys.
    Object(BTreeMap<String, JsonValue>),
}

impl JsonValue {
    /// Borrow object map or emit structured error.
    pub fn as_object(&self, path: &str) -> Result<&BTreeMap<String, JsonValue>, ModelError> {
        match self {
            Self::Object(map) => Ok(map),
            _ => Err(ModelError::new(
                ErrorCode::MalformedJson,
                path,
                "Expected JSON object",
            )),
        }
    }

    /// Borrow array or emit structured error.
    pub fn as_array(&self, path: &str) -> Result<&[JsonValue], ModelError> {
        match self {
            Self::Array(items) => Ok(items),
            _ => Err(ModelError::new(
                ErrorCode::MalformedJson,
                path,
                "Expected JSON array",
            )),
        }
    }

    /// Borrow string or emit structured error.
    pub fn as_str(&self, path: &str) -> Result<&str, ModelError> {
        match self {
            Self::String(s) => Ok(s),
            _ => Err(ModelError::new(
                ErrorCode::MalformedJson,
                path,
                "Expected JSON string",
            )),
        }
    }

    /// Extract boolean or emit structured error.
    pub fn as_bool(&self, path: &str) -> Result<bool, ModelError> {
        match self {
            Self::Bool(b) => Ok(*b),
            _ => Err(ModelError::new(
                ErrorCode::MalformedJson,
                path,
                "Expected JSON boolean",
            )),
        }
    }

    /// Parse nonnegative integer JSON number into `u64`.
    pub fn as_u64(&self, path: &str) -> Result<u64, ModelError> {
        let Self::Number(raw) = self else {
            return Err(ModelError::new(
                ErrorCode::MalformedJson,
                path,
                "Expected JSON integer",
            ));
        };
        if raw.contains('.') || raw.contains('e') || raw.contains('E') || raw.starts_with('-') {
            return Err(ModelError::new(
                ErrorCode::MalformedJson,
                path,
                "Expected nonnegative integer JSON number",
            ));
        }
        raw.parse::<u64>()
            .map_err(|_| ModelError::new(ErrorCode::MalformedJson, path, "Integer out of range"))
    }

    /// Parse signed integer JSON number into `i64`.
    pub fn as_i64(&self, path: &str) -> Result<i64, ModelError> {
        let Self::Number(raw) = self else {
            return Err(ModelError::new(
                ErrorCode::MalformedJson,
                path,
                "Expected JSON integer",
            ));
        };
        if raw.contains('.') || raw.contains('e') || raw.contains('E') {
            return Err(ModelError::new(
                ErrorCode::MalformedJson,
                path,
                "Expected exact integer JSON number",
            ));
        }
        raw.parse::<i64>()
            .map_err(|_| ModelError::new(ErrorCode::MalformedJson, path, "Integer out of range"))
    }

    /// Serialize to indented deterministic UTF-8 JSON with trailing newline.
    pub fn to_pretty_string(&self) -> String {
        let mut out = String::new();
        write_pretty(&mut out, self, 0);
        out.push('\n');
        out
    }

    /// Serialize to compact canonical UTF-8 JSON without extra whitespace.
    pub fn to_compact_string(&self) -> String {
        let mut out = String::new();
        write_compact(&mut out, self);
        out
    }
}

/// Borrow required field from a JSON object.
pub fn req_field<'a>(
    obj: &'a BTreeMap<String, JsonValue>,
    key: &str,
    path: &str,
) -> Result<&'a JsonValue, ModelError> {
    obj.get(key).ok_or_else(|| {
        ModelError::new(
            ErrorCode::MalformedJson,
            format!("{path}/{key}"),
            format!("Missing required JSON field `{key}`"),
        )
    })
}

/// Reject unknown keys on strict configuration objects.
pub fn reject_unknown_keys(
    obj: &BTreeMap<String, JsonValue>,
    allowed: &[&str],
    path: &str,
) -> Result<(), ModelError> {
    for key in obj.keys() {
        if !allowed.contains(&key.as_str()) {
            return Err(ModelError::new(
                ErrorCode::MalformedJson,
                format!("{path}/{key}"),
                format!("Unsupported JSON field `{key}`"),
            ));
        }
    }
    Ok(())
}

struct JsonParser<'a> {
    bytes: &'a [u8],
    pos: usize,
}

impl<'a> JsonParser<'a> {
    fn new(bytes: &'a [u8]) -> Self {
        Self { bytes, pos: 0 }
    }

    fn err(&self, path: &str, message: impl Into<String>) -> ModelError {
        ModelError::new(ErrorCode::MalformedJson, path, message)
    }

    fn skip_ws(&mut self) {
        while let Some(b) = self.bytes.get(self.pos) {
            if matches!(b, b' ' | b'\t' | b'\r' | b'\n') {
                self.pos += 1;
            } else {
                break;
            }
        }
    }

    fn parse_value(&mut self, depth: usize, path: &str) -> Result<JsonValue, ModelError> {
        if depth > MAX_JSON_DEPTH {
            return Err(ModelError::new(
                ErrorCode::SizeLimitExceeded,
                path,
                "JSON nesting exceeds maximum depth",
            ));
        }
        self.skip_ws();
        let Some(b) = self.bytes.get(self.pos).copied() else {
            return Err(self.err(path, "Unexpected end of JSON input"));
        };
        match b {
            b'{' => self.parse_object(depth, path),
            b'[' => self.parse_array(depth, path),
            b'"' => Ok(JsonValue::String(self.parse_string(path)?)),
            b't' => self.consume_literal(b"true", JsonValue::Bool(true), path),
            b'f' => self.consume_literal(b"false", JsonValue::Bool(false), path),
            b'n' => self.consume_literal(b"null", JsonValue::Null, path),
            b'-' | b'0'..=b'9' => self.parse_number(path),
            _ => Err(self.err(path, "Invalid JSON token")),
        }
    }

    fn consume_literal(
        &mut self,
        lit: &[u8],
        val: JsonValue,
        path: &str,
    ) -> Result<JsonValue, ModelError> {
        if self.bytes[self.pos..].starts_with(lit) {
            self.pos += lit.len();
            Ok(val)
        } else {
            Err(self.err(path, "Invalid JSON literal"))
        }
    }

    fn parse_number(&mut self, path: &str) -> Result<JsonValue, ModelError> {
        let start = self.pos;
        if self.bytes.get(self.pos) == Some(&b'-') {
            self.pos += 1;
        }
        match self.bytes.get(self.pos).copied() {
            Some(b'0') => {
                self.pos += 1;
                if matches!(self.bytes.get(self.pos), Some(b'0'..=b'9')) {
                    return Err(self.err(path, "Leading zeros are invalid in JSON numbers"));
                }
            }
            Some(b'1'..=b'9') => {
                while matches!(self.bytes.get(self.pos), Some(b'0'..=b'9')) {
                    self.pos += 1;
                }
            }
            _ => return Err(self.err(path, "Invalid JSON number")),
        }
        if self.bytes.get(self.pos) == Some(&b'.') {
            self.pos += 1;
            if !matches!(self.bytes.get(self.pos), Some(b'0'..=b'9')) {
                return Err(self.err(path, "Missing fractional digits in JSON number"));
            }
            while matches!(self.bytes.get(self.pos), Some(b'0'..=b'9')) {
                self.pos += 1;
            }
        }
        if matches!(self.bytes.get(self.pos), Some(b'e' | b'E')) {
            self.pos += 1;
            if matches!(self.bytes.get(self.pos), Some(b'+' | b'-')) {
                self.pos += 1;
            }
            if !matches!(self.bytes.get(self.pos), Some(b'0'..=b'9')) {
                return Err(self.err(path, "Missing exponent digits in JSON number"));
            }
            while matches!(self.bytes.get(self.pos), Some(b'0'..=b'9')) {
                self.pos += 1;
            }
        }
        let text = std::str::from_utf8(&self.bytes[start..self.pos])
            .map_err(|_| self.err(path, "Non-UTF-8 JSON number"))?;
        Ok(JsonValue::Number(text.to_owned()))
    }

    fn parse_string(&mut self, path: &str) -> Result<String, ModelError> {
        if self.bytes.get(self.pos) != Some(&b'"') {
            return Err(self.err(path, "Expected JSON string"));
        }
        self.pos += 1;
        let mut out = String::new();
        while let Some(b) = self.bytes.get(self.pos).copied() {
            if b == b'"' {
                self.pos += 1;
                return Ok(out);
            }
            if b < 0x20 {
                return Err(self.err(path, "Unescaped control character in JSON string"));
            }
            if b == b'\\' {
                self.pos += 1;
                let Some(esc) = self.bytes.get(self.pos).copied() else {
                    return Err(self.err(path, "Unterminated escape in JSON string"));
                };
                self.pos += 1;
                match esc {
                    b'"' => out.push('"'),
                    b'\\' => out.push('\\'),
                    b'/' => out.push('/'),
                    b'b' => out.push('\u{0008}'),
                    b'f' => out.push('\u{000C}'),
                    b'n' => out.push('\n'),
                    b'r' => out.push('\r'),
                    b't' => out.push('\t'),
                    b'u' => {
                        let code = self.read_hex4(path)?;
                        if (0xD800..=0xDBFF).contains(&code) {
                            if self.bytes.get(self.pos..self.pos + 2) != Some(b"\\u") {
                                return Err(self.err(path, "Unpaired UTF-16 high surrogate"));
                            }
                            self.pos += 2;
                            let low = self.read_hex4(path)?;
                            if !(0xDC00..=0xDFFF).contains(&low) {
                                return Err(self.err(path, "Invalid UTF-16 low surrogate"));
                            }
                            let cp = 0x1_0000
                                + (((u32::from(code) - 0xD800) << 10) | (u32::from(low) - 0xDC00));
                            let ch = char::from_u32(cp)
                                .ok_or_else(|| self.err(path, "Invalid Unicode code point"))?;
                            out.push(ch);
                        } else {
                            let ch = char::from_u32(u32::from(code))
                                .ok_or_else(|| self.err(path, "Invalid Unicode surrogate"))?;
                            out.push(ch);
                        }
                    }
                    _ => return Err(self.err(path, "Invalid JSON string escape")),
                }
            } else {
                let tail = std::str::from_utf8(&self.bytes[self.pos..])
                    .map_err(|_| self.err(path, "Invalid UTF-8 inside JSON string"))?;
                let ch = tail
                    .chars()
                    .next()
                    .ok_or_else(|| self.err(path, "Unexpected EOF inside JSON string"))?;
                out.push(ch);
                self.pos += ch.len_utf8();
            }
        }
        Err(self.err(path, "Unterminated JSON string"))
    }

    fn read_hex4(&mut self, path: &str) -> Result<u16, ModelError> {
        let Some(slice) = self.bytes.get(self.pos..self.pos + 4) else {
            return Err(self.err(path, "Incomplete `\\u` escape in JSON string"));
        };
        let s = std::str::from_utf8(slice).map_err(|_| self.err(path, "Invalid hex escape"))?;
        self.pos += 4;
        u16::from_str_radix(s, 16).map_err(|_| self.err(path, "Invalid hex digit in `\\u` escape"))
    }

    fn parse_array(&mut self, depth: usize, path: &str) -> Result<JsonValue, ModelError> {
        self.pos += 1; // '['
        let mut items = Vec::new();
        self.skip_ws();
        if self.bytes.get(self.pos) == Some(&b']') {
            self.pos += 1;
            return Ok(JsonValue::Array(items));
        }
        let mut idx = 0usize;
        loop {
            let item_path = format!("{path}/{idx}");
            items.push(self.parse_value(depth + 1, &item_path)?);
            idx += 1;
            self.skip_ws();
            match self.bytes.get(self.pos) {
                Some(b',') => self.pos += 1,
                Some(b']') => {
                    self.pos += 1;
                    return Ok(JsonValue::Array(items));
                }
                _ => return Err(self.err(path, "Expected `,` or `]` in JSON array")),
            }
        }
    }

    fn parse_object(&mut self, depth: usize, path: &str) -> Result<JsonValue, ModelError> {
        self.pos += 1; // '{'
        let mut map = BTreeMap::new();
        self.skip_ws();
        if self.bytes.get(self.pos) == Some(&b'}') {
            self.pos += 1;
            return Ok(JsonValue::Object(map));
        }
        loop {
            self.skip_ws();
            let key = self.parse_string(path)?;
            if map.contains_key(&key) {
                return Err(ModelError::new(
                    ErrorCode::MalformedJson,
                    format!("{path}/{key}"),
                    format!("Duplicate JSON object key `{key}`"),
                ));
            }
            self.skip_ws();
            if self.bytes.get(self.pos) != Some(&b':') {
                return Err(self.err(path, "Expected `:` after JSON object key"));
            }
            self.pos += 1;
            let val_path = format!("{path}/{key}");
            let value = self.parse_value(depth + 1, &val_path)?;
            map.insert(key, value);
            self.skip_ws();
            match self.bytes.get(self.pos) {
                Some(b',') => self.pos += 1,
                Some(b'}') => {
                    self.pos += 1;
                    return Ok(JsonValue::Object(map));
                }
                _ => return Err(self.err(path, "Expected `,` or `}` in JSON object")),
            }
        }
    }
}

/// Parse strict UTF-8 JSON bytes, rejecting duplicate keys, NaN/Infinity, and trailing data.
pub fn parse_json_bytes(bytes: &[u8]) -> Result<JsonValue, ModelError> {
    if std::str::from_utf8(bytes).is_err() {
        return Err(ModelError::new(
            ErrorCode::MalformedJson,
            "/",
            "Input JSON is not valid UTF-8",
        ));
    }
    let mut parser = JsonParser::new(bytes);
    let value = parser.parse_value(0, "")?;
    parser.skip_ws();
    if parser.pos != bytes.len() {
        return Err(ModelError::new(
            ErrorCode::MalformedJson,
            "/",
            "Trailing non-whitespace characters after JSON root value",
        ));
    }
    Ok(value)
}

fn write_escaped_str(out: &mut String, value: &str) {
    out.push('"');
    for ch in value.chars() {
        match ch {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\u{0008}' => out.push_str("\\b"),
            '\u{000C}' => out.push_str("\\f"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if (c as u32) < 0x20 => {
                let _ = write!(out, "\\u{:04x}", c as u32);
            }
            c => out.push(c),
        }
    }
    out.push('"');
}

fn write_compact(out: &mut String, value: &JsonValue) {
    match value {
        JsonValue::Null => out.push_str("null"),
        JsonValue::Bool(b) => out.push_str(if *b { "true" } else { "false" }),
        JsonValue::Number(n) => out.push_str(n),
        JsonValue::String(s) => write_escaped_str(out, s),
        JsonValue::Array(items) => {
            out.push('[');
            for (idx, item) in items.iter().enumerate() {
                if idx > 0 {
                    out.push(',');
                }
                write_compact(out, item);
            }
            out.push(']');
        }
        JsonValue::Object(map) => {
            out.push('{');
            for (idx, (k, v)) in map.iter().enumerate() {
                if idx > 0 {
                    out.push(',');
                }
                write_escaped_str(out, k);
                out.push(':');
                write_compact(out, v);
            }
            out.push('}');
        }
    }
}

fn write_pretty(out: &mut String, value: &JsonValue, indent: usize) {
    match value {
        JsonValue::Array(items) if !items.is_empty() => {
            out.push_str("[\n");
            for (idx, item) in items.iter().enumerate() {
                push_indent(out, indent + 2);
                write_pretty(out, item, indent + 2);
                if idx + 1 < items.len() {
                    out.push(',');
                }
                out.push('\n');
            }
            push_indent(out, indent);
            out.push(']');
        }
        JsonValue::Object(map) if !map.is_empty() => {
            out.push_str("{\n");
            for (idx, (k, v)) in map.iter().enumerate() {
                push_indent(out, indent + 2);
                write_escaped_str(out, k);
                out.push_str(": ");
                write_pretty(out, v, indent + 2);
                if idx + 1 < map.len() {
                    out.push(',');
                }
                out.push('\n');
            }
            push_indent(out, indent);
            out.push('}');
        }
        _ => write_compact(out, value),
    }
}

fn push_indent(out: &mut String, spaces: usize) {
    for _ in 0..spaces {
        out.push(' ');
    }
}
