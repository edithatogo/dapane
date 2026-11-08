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

pub(crate) fn parse(input: &str) -> Result<Request, DapaneError> {
    if input.len() > MAX_JSON_BYTES {
        return Err(DapaneError::new(
            "input_limit",
            "JSON request exceeds 4 MiB",
            "/",
        ));
    }
    let value: UniqueValue = serde_json::from_str(input)
        .map_err(|error| DapaneError::new("invalid_json", &error.to_string(), "/"))?;
    serde_json::from_value(value.0)
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

pub(crate) fn check_typed_size(request: &Request) -> Result<(), DapaneError> {
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
    serde_json::to_writer(LimitWriter(0), request)
        .map_err(|_| DapaneError::new("input_limit", "Typed request exceeds 4 MiB", "/"))
}
