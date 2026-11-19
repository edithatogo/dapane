//! Strict JSON loading and explicit canonicalization for reproducibility.

use std::fmt;

use serde::de::{self, MapAccess, SeqAccess, Visitor};
use serde::{Deserialize, Deserializer, Serialize};
use serde_json::{Map, Number, Value};
use sha2::{Digest, Sha256};

use crate::{DapaneError, MAX_JSON_BYTES, Request};

struct UniqueValue(Value);

impl<'de> Deserialize<'de> for UniqueValue {
    fn deserialize<D: Deserializer<'de>>(deserializer: D) -> Result<Self, D::Error> {
        struct UniqueVisitor;
        impl<'de> Visitor<'de> for UniqueVisitor {
            type Value = UniqueValue;
            fn expecting(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
                formatter.write_str("JSON with unique object keys")
            }
            fn visit_bool<E: de::Error>(self, value: bool) -> Result<Self::Value, E> {
                Ok(UniqueValue(Value::Bool(value)))
            }
            fn visit_i64<E: de::Error>(self, value: i64) -> Result<Self::Value, E> {
                Ok(UniqueValue(Value::Number(value.into())))
            }
            fn visit_u64<E: de::Error>(self, value: u64) -> Result<Self::Value, E> {
                Ok(UniqueValue(Value::Number(value.into())))
            }
            fn visit_f64<E: de::Error>(self, value: f64) -> Result<Self::Value, E> {
                Number::from_f64(value)
                    .map(|number| UniqueValue(Value::Number(number)))
                    .ok_or_else(|| E::custom("Non-finite JSON number"))
            }
            fn visit_str<E: de::Error>(self, value: &str) -> Result<Self::Value, E> {
                Ok(UniqueValue(Value::String(value.to_owned())))
            }
            fn visit_string<E: de::Error>(self, value: String) -> Result<Self::Value, E> {
                Ok(UniqueValue(Value::String(value)))
            }
            fn visit_none<E: de::Error>(self) -> Result<Self::Value, E> {
                Ok(UniqueValue(Value::Null))
            }
            fn visit_unit<E: de::Error>(self) -> Result<Self::Value, E> {
                Ok(UniqueValue(Value::Null))
            }
            fn visit_seq<A: SeqAccess<'de>>(
                self,
                mut sequence: A,
            ) -> Result<Self::Value, A::Error> {
                let mut result = Vec::new();
                while let Some(value) = sequence.next_element::<UniqueValue>()? {
                    result.push(value.0);
                }
                Ok(UniqueValue(Value::Array(result)))
            }
            fn visit_map<A: MapAccess<'de>>(self, mut map: A) -> Result<Self::Value, A::Error> {
                let mut result = Map::new();
                while let Some(key) = map.next_key::<String>()? {
                    if result.contains_key(&key) {
                        return Err(de::Error::custom("Duplicate JSON object key"));
                    }
                    let value = map.next_value::<UniqueValue>()?;
                    result.insert(key, value.0);
                }
                Ok(UniqueValue(Value::Object(result)))
            }
        }
        deserializer.deserialize_any(UniqueVisitor)
    }
}

pub(crate) fn parse_value(input: &str) -> Result<Value, DapaneError> {
    if input.len() > MAX_JSON_BYTES {
        return Err(DapaneError::new(
            "input_limit",
            "JSON request exceeds 4 MiB",
            "/",
        ));
    }
    let value: UniqueValue = serde_json::from_str(input)
        .map_err(|error| DapaneError::new("invalid_json", &error.to_string(), "/"))?;
    Ok(value.0)
}

pub(crate) fn parse(input: &str) -> Result<Request, DapaneError> {
    let value = parse_value(input)?;
    if value.get("schema_version").and_then(Value::as_str) == Some("0.1")
        && value.get("capacity_allocations").is_some()
    {
        return Err(DapaneError::new(
            "invalid_request",
            "capacity_allocations requires schema_version 0.2; 0.1 remains full-pool only",
            "/capacity_allocations",
        ));
    }
    serde_json::from_value(value)
        .map_err(|error| DapaneError::new("invalid_request", &error.to_string(), "/"))
}

pub(crate) fn value<T: Serialize>(value: &T) -> Result<Value, DapaneError> {
    serde_json::to_value(value)
        .map_err(|error| DapaneError::new("serialization_error", &error.to_string(), "/"))
}

fn write_canonical(value: &Value, output: &mut String) -> Result<(), DapaneError> {
    match value {
        Value::Array(array) => {
            output.push('[');
            for (index, item) in array.iter().enumerate() {
                if index > 0 {
                    output.push(',');
                }
                write_canonical(item, output)?;
            }
            output.push(']');
        }
        Value::Object(map) => {
            output.push('{');
            let mut entries: Vec<_> = map.iter().collect();
            entries.sort_by_key(|(key, _)| *key);
            for (index, (key, item)) in entries.into_iter().enumerate() {
                if index > 0 {
                    output.push(',');
                }
                output.push_str(&serde_json::to_string(key).map_err(|error| {
                    DapaneError::new("serialization_error", &error.to_string(), "/")
                })?);
                output.push(':');
                write_canonical(item, output)?;
            }
            output.push('}');
        }
        _ => {
            output.push_str(&serde_json::to_string(value).map_err(|error| {
                DapaneError::new("serialization_error", &error.to_string(), "/")
            })?)
        }
    }
    Ok(())
}

pub(crate) fn canonical(value: &Value) -> Result<String, DapaneError> {
    let mut output = String::new();
    write_canonical(value, &mut output)?;
    Ok(output)
}

pub(crate) fn digest(domain: &str, value: &Value) -> Result<String, DapaneError> {
    let mut hasher = Sha256::new();
    hasher.update(domain.as_bytes());
    hasher.update(canonical(value)?.as_bytes());
    let hexadecimal: String = hasher
        .finalize()
        .iter()
        .map(|byte| format!("{byte:02x}"))
        .collect();
    Ok(format!("sha256:{hexadecimal}"))
}

pub(crate) fn encoded_size<T: Serialize>(request: &T) -> Result<usize, DapaneError> {
    struct LimitWriter(usize);
    impl std::io::Write for LimitWriter {
        fn write(&mut self, buffer: &[u8]) -> std::io::Result<usize> {
            self.0 = self.0.saturating_add(buffer.len());
            if self.0 > MAX_JSON_BYTES {
                return Err(std::io::Error::other("Typed request exceeds 4 MiB"));
            }
            Ok(buffer.len())
        }
        fn flush(&mut self) -> std::io::Result<()> {
            Ok(())
        }
    }
    let mut writer = LimitWriter(0);
    serde_json::to_writer(&mut writer, request)
        .map_err(|_| DapaneError::new("input_limit", "Typed request exceeds 4 MiB", "/"))?;
    Ok(writer.0)
}

pub(crate) fn check_typed_size<T: Serialize>(request: &T) -> Result<(), DapaneError> {
    encoded_size(request).map(|_| ())
}

#[cfg(test)]
mod canonical_comparison_tests {
    //! Golden byte-level unit tests for `write_canonical`.
    //!
    //! The 2026-11-19 comparison against `serde_json_canonicalizer` concluded
    //! **NO-GO** (see `conductor/tracks/serde_canonicalization_qualification_20261118/plan.md`)
    //! due to byte-incompatibilities on negative zero, integer bounds, and
    //! whole-number floats; the dev-dependency was removed while retaining
    //! these regression assertions on Dapane's canonical output.

    use super::*;
    use serde_json::json;

    fn canonical_str(value: &Value) -> String {
        let mut out = String::new();
        write_canonical(value, &mut out).unwrap();
        out
    }

    #[test]
    fn serde_json_canonicalizer_matches_dapane_on_empty_object() {
        assert_eq!(canonical_str(&json!({})), "{}");
    }

    #[test]
    fn serde_json_canonicalizer_matches_dapane_on_empty_array() {
        assert_eq!(canonical_str(&json!([])), "[]");
    }

    #[test]
    fn serde_json_canonicalizer_matches_dapane_on_sorted_keys() {
        let value = json!({"zebra": 1, "alpha": 2, "Mammal": 3});
        let dapane = canonical_str(&value);
        // Sorted by Unicode code point (UTF-8 / char order): Mammal < alpha < zebra
        assert_eq!(dapane, r#"{"Mammal":3,"alpha":2,"zebra":1}"#);
    }

    #[test]
    fn serde_json_canonicalizer_matches_dapane_on_nested_objects() {
        let value = json!({"c": {"z": 1, "a": 2}, "a": {"b": 1, "c": 2}});
        assert_eq!(
            canonical_str(&value),
            r#"{"a":{"b":1,"c":2},"c":{"a":2,"z":1}}"#
        );
    }

    #[test]
    fn serde_json_canonicalizer_matches_dapane_on_arrays() {
        let value = json!({"items": [3, 1, 2]});
        assert_eq!(canonical_str(&value), r#"{"items":[3,1,2]}"#);
    }

    #[test]
    fn serde_json_canonicalizer_matches_dapane_on_numbers() {
        let value = json!({"int": 42, "float": 123.456, "zero": 0});
        assert_eq!(
            canonical_str(&value),
            r#"{"float":123.456,"int":42,"zero":0}"#
        );
    }

    #[test]
    fn serde_json_canonicalizer_matches_dapane_on_strings() {
        let value = json!({"text": "hello\nworld", "quote": "say \"hi\""});
        assert_eq!(
            canonical_str(&value),
            r#"{"quote":"say \"hi\"","text":"hello\nworld"}"#
        );
    }

    #[test]
    fn serde_json_canonicalizer_matches_dapane_on_booleans_and_null() {
        let value = json!({"true": true, "false": false, "null": null});
        assert_eq!(
            canonical_str(&value),
            r#"{"false":false,"null":null,"true":true}"#
        );
    }

    #[test]
    fn serde_json_canonicalizer_matches_dapane_on_powers_of_ten() {
        // KNOWN INCOMPATIBILITY documented in no-go evaluation:
        // serde_json_canonicalizer drops `.0` (100.0 -> 100); Dapane preserves `100.0`.
        let value = json!({"hundred": 100.0, "thousandth": 0.001, "large": 1.5e10});
        let dapane = canonical_str(&value);
        assert_eq!(
            dapane,
            r#"{"hundred":100.0,"large":15000000000.0,"thousandth":0.001}"#
        );
    }

    #[test]
    fn serde_json_canonicalizer_matches_dapane_on_unicode_escape() {
        let value = json!({"cafe": "caf\u{e9}", "emoji": "\u{1f600}"});
        assert_eq!(
            canonical_str(&value),
            "{\"cafe\":\"café\",\"emoji\":\"😀\"}"
        );
    }

    #[test]
    fn serde_json_canonicalizer_matches_dapane_on_negative_zero() {
        // KNOWN INCOMPATIBILITY documented in no-go evaluation:
        // serde_json_canonicalizer normalizes `-0.0` to `0`; Dapane preserves `-0.0`.
        let value = json!({"neg_zero": -0.0_f64, "zero": 0.0_f64});
        let dapane = canonical_str(&value);
        assert_eq!(dapane, r#"{"neg_zero":-0.0,"zero":0.0}"#);
    }

    #[test]
    fn serde_json_canonicalizer_matches_dapane_on_integer_bounds() {
        // KNOWN INCOMPATIBILITY documented in no-go evaluation:
        // serde_json_canonicalizer rounds i64::MAX/MIN; Dapane preserves exact integer values.
        let value = json!({"max_i64": 9223372036854775807i64, "min_i64": -9223372036854775808i64});
        let dapane = canonical_str(&value);
        assert_eq!(
            dapane,
            r#"{"max_i64":9223372036854775807,"min_i64":-9223372036854775808}"#
        );
    }

    #[test]
    fn serde_json_canonicalizer_duplicate_key_handling() {
        // Note: Dapane's parse_value uses UniqueValue visitor which rejects duplicates;
        // serde_json::from_str::<Value> keeps last by default.
        let input = "{\"a\": 1, \"a\": 2}";
        let parsed = serde_json::from_str::<Value>(input).unwrap();
        assert_eq!(canonical_str(&parsed), r#"{"a":2}"#);
        let strict = parse_value(input);
        assert!(strict.is_err());
    }
}
