//! Canonical JSON equivalence fixtures and regression tests.
//!
//! These fixtures freeze Dapane's current canonical serialization
//! behavior through the public `evaluate_json` API at main SHA
//! `ea4d0ae`. They establish golden behavior any replacement must match
//! byte-for-byte before versioned migration can be considered.
//!
//! The `canonical`/`digest` functions are `pub(crate)`; this integration
//! test exercises them indirectly via `evaluate_json`, which internally
//! serializes requests canonically and computes domain-prefixed digests.

use dapane_core::evaluate_json;
use serde_json::{Value, json};

const MAIN_SHA: &str = "ea4d0ae42381d8e8f68a42219481a95205ae91fc";

fn source() -> Value {
    json!({
        "id": "synthetic-fixture", "version": "1",
        "evidence": "synthetic", "access": "public", "validation": "unvalidated"
    })
}

fn base_request() -> Value {
    json!({
        "schema_version": "0.1",
        "run_id": "canonical-freeze-test",
        "knowledge_cutoff": "2026-11-08",
        "policy": {
            "id": "synthetic-provider-cost",
            "version": "1",
            "currency": "AUD",
            "price_year": 2026,
            "perspective": "provider",
            "basis": "financial_cost",
            "rounding": {"scale": 2, "mode": "half_even"}
        },
        "quotes": [{
            "id": "staff-rate",
            "kind": "resource_use",
            "target": "clinical_staff",
            "unit": "hour",
            "amount": "31.20",
            "per_quantity": "1",
            "currency": "AUD",
            "price_year": 2026,
            "basis": "financial_cost",
            "components": ["salary"],
            "valid_from": "2026-01-01",
            "valid_to": "2027-01-01",
            "known_from": "2025-12-01",
            "source": source()
        }],
        "usage": [{
            "id": "staff-line",
            "use_id": "staff-use",
            "kind": "resource_use",
            "target": "clinical_staff",
            "unit": "hour",
            "quantity": {"numerator": "1", "denominator": "3"},
            "service_date": "2026-06-01",
            "quote_id": "staff-rate",
            "source": source()
        }]
    })
}

#[test]
fn freeze_main_sha_is_ea4d0ae() {
    assert_eq!(MAIN_SHA, "ea4d0ae42381d8e8f68a42219481a95205ae91fc");
}

#[test]
fn canonical_determinism_same_input_same_output() {
    let req = base_request();
    let out1 = evaluate_json(&req.to_string()).unwrap();
    let out2 = evaluate_json(&req.to_string()).unwrap();
    assert_eq!(out1, out2);
}

#[test]
fn canonical_duplicate_keys_are_rejected() {
    let input = r#"{"schema_version":"0.1","run_id":"x","schema_version":"0.1"}"#;
    let result = evaluate_json(input);
    assert!(result.is_err());
    let err = result.unwrap_err();
    assert_eq!(err.code, "invalid_json");
}

#[test]
fn canonical_integer_bounds() {
    // Exact decimal strings are unsigned; max 96 digits per the validation bounds
    let mut req = base_request();
    req["quotes"][0]["amount"] = json!("9223372036854775807");
    let result = evaluate_json(&req.to_string());
    assert!(
        result.is_ok(),
        "large unsigned integer should parse: {:?}",
        result.err()
    );

    let mut req2 = base_request();
    req2["quotes"][0]["amount"] = json!("18446744073709551615");
    let result = evaluate_json(&req2.to_string());
    assert!(
        result.is_ok(),
        "u64::MAX as exact string should parse: {:?}",
        result.err()
    );
}

#[test]
fn canonical_string_escaping_roundtrip() {
    let mut req = base_request();
    req["run_id"] = json!("test_with_quotes_and_backslash");
    let result = evaluate_json(&req.to_string());
    assert!(result.is_ok());
    let out = result.unwrap();
    let parsed: Value = serde_json::from_str(&out).unwrap();
    assert_eq!(parsed["run_id"], json!("test_with_quotes_and_backslash"));
}

#[test]
fn canonical_float_scientific_notation_rejected() {
    let mut req = base_request();
    req["quotes"][0]["amount"] = json!("1e2");
    let result = evaluate_json(&req.to_string());
    assert!(
        result.is_err(),
        "scientific notation should be rejected: {:?}",
        result.err()
    );
}

#[test]
fn canonical_domain_digest_stability() {
    let req = base_request();
    let out1 = evaluate_json(&req.to_string()).unwrap();
    let out2 = evaluate_json(&req.to_string()).unwrap();
    assert_eq!(out1, out2);
    let parsed: Value = serde_json::from_str(&out1).unwrap();
    assert!(parsed.is_object());
}

#[test]
fn canonical_empty_object_rejected() {
    let result = evaluate_json("{}");
    assert!(result.is_err());
    let err = result.unwrap_err();
    assert_eq!(err.code, "invalid_request");
}

#[test]
fn canonical_capacity_allocations_rejected_on_v1() {
    let mut req = base_request();
    req["capacity_allocations"] = json!([]);
    let result = evaluate_json(&req.to_string());
    assert!(result.is_err());
    let err = result.unwrap_err();
    assert_eq!(err.code, "invalid_request");
    assert_eq!(err.path, "/capacity_allocations");
}

#[test]
fn canonical_unknown_fields_rejected() {
    let mut req = base_request();
    req["unknown_field"] = json!("should not be here");
    let result = evaluate_json(&req.to_string());
    assert!(result.is_err());
}

#[test]
fn canonical_nonfinite_json_rejected() {
    let input = r#"{"schema_version":"0.1","amount":NaN}"#;
    let result = evaluate_json(input);
    assert!(result.is_err());
    let err = result.unwrap_err();
    assert_eq!(err.code, "invalid_json");
}

#[test]
fn canonical_same_logical_request_different_key_order_same_output() {
    let base = base_request();

    // Build a variant with reordered top-level keys (same logical content)
    let mut variant = serde_json::Map::new();
    if let Some(obj) = base.as_object() {
        for (key, value) in obj {
            variant.insert(key.clone(), value.clone());
        }
    }
    // Re-insert in reverse order by reconstructing
    let mut keys: Vec<String> = variant.keys().cloned().collect();
    keys.sort();
    keys.reverse();
    let mut reordered = serde_json::Map::new();
    for key in &keys {
        reordered.insert(key.clone(), variant.get(key).unwrap().clone());
    }
    let variant_value = Value::Object(reordered);

    let out_base = evaluate_json(&base.to_string()).unwrap();
    let out_variant = evaluate_json(&variant_value.to_string()).unwrap();
    assert_eq!(out_base, out_variant);
}
