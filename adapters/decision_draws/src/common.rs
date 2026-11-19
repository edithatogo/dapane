//! Shared transport and exact-value checks for the optional contracts.

use std::fmt;
use std::io::Write;

use dapane_core::{DapaneError, Rational};
use num_bigint::BigInt;
use num_rational::BigRational;
use serde::de::{DeserializeOwned, MapAccess, SeqAccess, Visitor};
use serde::{Deserialize, Deserializer, Serialize};
use serde_json::{Map, Value};
use sha2::{Digest, Sha256};

pub(crate) const INPUT_BYTES: usize = 4 * 1024 * 1024;
pub(crate) const OUTPUT_BYTES: usize = 16 * 1024 * 1024;

pub(crate) fn error(code: &str, message: &str, path: &str) -> DapaneError {
    DapaneError::new(code, message, path)
}

// Validate before conversion: Value and BTreeMap alone lose duplicate keys.
struct UniqueJson(Value);

impl<'de> Deserialize<'de> for UniqueJson {
    fn deserialize<D: Deserializer<'de>>(deserializer: D) -> Result<Self, D::Error> {
        struct JsonVisitor;
        impl<'de> Visitor<'de> for JsonVisitor {
            type Value = UniqueJson;

            fn expecting(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
                f.write_str("JSON with unique object keys and no floating-point numbers")
            }

            fn visit_bool<E: serde::de::Error>(self, v: bool) -> Result<Self::Value, E> {
                Ok(UniqueJson(Value::Bool(v)))
            }

            fn visit_i64<E: serde::de::Error>(self, v: i64) -> Result<Self::Value, E> {
                Ok(UniqueJson(Value::Number(v.into())))
            }

            fn visit_u64<E: serde::de::Error>(self, v: u64) -> Result<Self::Value, E> {
                Ok(UniqueJson(Value::Number(v.into())))
            }

            fn visit_str<E: serde::de::Error>(self, v: &str) -> Result<Self::Value, E> {
                Ok(UniqueJson(Value::String(v.to_owned())))
            }

            fn visit_string<E: serde::de::Error>(self, v: String) -> Result<Self::Value, E> {
                Ok(UniqueJson(Value::String(v)))
            }

            fn visit_unit<E: serde::de::Error>(self) -> Result<Self::Value, E> {
                Ok(UniqueJson(Value::Null))
            }

            fn visit_seq<A: SeqAccess<'de>>(self, mut seq: A) -> Result<Self::Value, A::Error> {
                let mut values = Vec::new();
                while let Some(value) = seq.next_element::<UniqueJson>()? {
                    values.push(value.0);
                }
                Ok(UniqueJson(Value::Array(values)))
            }

            fn visit_map<A: MapAccess<'de>>(self, mut map: A) -> Result<Self::Value, A::Error> {
                let mut values = Map::new();
                while let Some(key) = map.next_key::<String>()? {
                    if values.contains_key(&key) {
                        return Err(serde::de::Error::custom("duplicate JSON object key"));
                    }
                    values.insert(key, map.next_value::<UniqueJson>()?.0);
                }
                Ok(UniqueJson(Value::Object(values)))
            }
        }
        deserializer.deserialize_any(JsonVisitor)
    }
}

pub(crate) fn parse<T: DeserializeOwned>(input: &str) -> Result<T, DapaneError> {
    if input.len() > INPUT_BYTES {
        return Err(error("input_limit", "Input exceeds 4 MiB", "/"));
    }
    let raw: UniqueJson =
        serde_json::from_str(input).map_err(|e| error("invalid_json", &e.to_string(), "/"))?;
    serde_json::from_value(raw.0).map_err(|e| error("invalid_request", &e.to_string(), "/"))
}

pub(crate) fn value<T: Serialize>(v: &T) -> Result<Value, DapaneError> {
    serde_json::to_value(v).map_err(|e| error("serialization_error", &e.to_string(), "/"))
}

pub(crate) fn canonical(v: &Value) -> Result<String, DapaneError> {
    fn write(v: &Value, out: &mut String) -> Result<(), serde_json::Error> {
        match v {
            Value::Object(map) => {
                let mut entries: Vec<_> = map.iter().collect();
                entries.sort_by_key(|(key, _)| *key);
                out.push('{');
                for (i, (key, v)) in entries.into_iter().enumerate() {
                    if i > 0 {
                        out.push(',');
                    }
                    out.push_str(&serde_json::to_string(key)?);
                    out.push(':');
                    write(v, out)?;
                }
                out.push('}');
            }
            Value::Array(array) => {
                out.push('[');
                for (i, v) in array.iter().enumerate() {
                    if i > 0 {
                        out.push(',');
                    }
                    write(v, out)?;
                }
                out.push(']');
            }
            _ => out.push_str(&serde_json::to_string(v)?),
        }
        Ok(())
    }
    let mut out = String::new();
    write(v, &mut out).map_err(|e| error("serialization_error", &e.to_string(), "/"))?;
    Ok(out)
}

pub(crate) fn digest<T: Serialize>(domain: &str, v: &T) -> Result<String, DapaneError> {
    let mut hasher = Sha256::new();
    hasher.update(domain.as_bytes());
    hasher.update(canonical(&value(v)?)?.as_bytes());
    let hex: String = hasher
        .finalize()
        .iter()
        .map(|byte| format!("{byte:02x}"))
        .collect();
    Ok(format!("sha256:{hex}"))
}

pub(crate) fn encoded_size<T: Serialize>(v: &T, limit: usize) -> Result<usize, DapaneError> {
    struct Counter {
        bytes: usize,
        limit: usize,
    }
    impl Write for Counter {
        fn write(&mut self, bytes: &[u8]) -> std::io::Result<usize> {
            self.bytes = self.bytes.saturating_add(bytes.len());
            if self.bytes > self.limit {
                return Err(std::io::Error::other("Encoded size bound exceeded"));
            }
            Ok(bytes.len())
        }

        fn flush(&mut self) -> std::io::Result<()> {
            Ok(())
        }
    }
    let mut counter = Counter { bytes: 0, limit };
    serde_json::to_writer(&mut counter, v)
        .map_err(|_| error("input_limit", "Encoded size bound exceeded", "/"))?;
    Ok(counter.bytes)
}

pub(crate) fn identifier(s: &str, path: &str) -> Result<(), DapaneError> {
    if s.is_empty() || s.len() > 128 || s.trim() != s || s.chars().any(char::is_control) {
        return Err(error(
            "invalid_identity",
            "Expected 1..128 UTF-8 bytes without outer whitespace or controls",
            path,
        ));
    }
    Ok(())
}

pub(crate) fn digest_field(s: &str, path: &str) -> Result<(), DapaneError> {
    if !s.strip_prefix("sha256:").is_some_and(|h| {
        h.len() == 64
            && h.bytes()
                .all(|c| c.is_ascii_digit() || (b'a'..=b'f').contains(&c))
    }) {
        return Err(error(
            "invalid_digest",
            "Expected sha256 and 64 lowercase hexadecimal characters",
            path,
        ));
    }
    Ok(())
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub(crate) enum Evidence {
    Synthetic,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub(crate) struct Identity {
    pub id: String,
    pub version: String,
    pub content_digest: String,
    pub evidence: Evidence,
}

impl Identity {
    pub fn validate(&self, path: &str) -> Result<(), DapaneError> {
        identifier(&self.id, path)?;
        identifier(&self.version, path)?;
        digest_field(&self.content_digest, path)
    }
}

pub(crate) fn exact(v: &Rational, path: &str) -> Result<BigRational, DapaneError> {
    fn integer(s: &str, signed: bool, path: &str) -> Result<BigInt, DapaneError> {
        let digits = if signed {
            s.strip_prefix('-').unwrap_or(s)
        } else {
            s
        };
        if digits.is_empty()
            || !digits.bytes().all(|b| b.is_ascii_digit())
            || (digits.len() > 1 && digits.starts_with('0'))
            || s == "-0"
        {
            return Err(error(
                "invalid_number",
                "Expected canonical integer digits, optional minus for numerator",
                path,
            ));
        }
        if digits.len() > 96 {
            return Err(error(
                "precision_limit",
                "Exact input exceeds 96 digits",
                path,
            ));
        }
        BigInt::parse_bytes(s.as_bytes(), 10)
            .ok_or_else(|| error("invalid_number", "Invalid integer", path))
    }
    let numerator = integer(&v.numerator, true, path)?;
    let denominator = integer(&v.denominator, false, path)?;
    if denominator <= BigInt::from(0) {
        return Err(error(
            "zero_denominator",
            "Denominator must be positive",
            path,
        ));
    }
    bounded(BigRational::new(numerator, denominator), path)
}

pub(crate) fn bounded(v: BigRational, path: &str) -> Result<BigRational, DapaneError> {
    if v.numer().bits() > 4096 || v.denom().bits() > 4096 {
        return Err(error(
            "precision_limit",
            "Exact intermediate exceeds 4096 bits",
            path,
        ));
    }
    Ok(v)
}

pub(crate) fn wire(v: &BigRational) -> Rational {
    Rational {
        numerator: v.numer().to_string(),
        denominator: v.denom().to_string(),
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, PartialOrd, Ord)]
#[serde(deny_unknown_fields)]
pub(crate) struct PairKey {
    pub scenario_id: String,
    pub strategy_id: String,
    pub draw_id: String,
    pub replication_id: String,
    pub perspective: String,
    pub subgroup_id: String,
}

impl PairKey {
    pub fn validate(&self, path: &str) -> Result<(), DapaneError> {
        for field in [
            &self.scenario_id,
            &self.strategy_id,
            &self.draw_id,
            &self.replication_id,
            &self.perspective,
            &self.subgroup_id,
        ] {
            identifier(field, path)?;
        }
        Ok(())
    }
}
