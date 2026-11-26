//! Opt-in JCS fingerprints of evaluated Dapane reports.

use dapane_core::{DapaneError, evaluate_json};
use serde::Serialize;
use serde_json::Value;
use sha2::{Digest, Sha256};

/// Required identifier for this optional fingerprint profile.
pub const PROFILE: &str = "dapane-canonical-v2";
const REPORT_DOMAIN: &[u8] = b"dapane:report:canonical-v2\n";
const MAX_SAFE_INTEGER: i64 = (1 << 53) - 1;

/// A detached fingerprint and the native report identity it refers to.
#[derive(Debug, Serialize, PartialEq, Eq)]
pub struct ReportFingerprint {
    /// The explicitly selected fingerprint profile.
    pub profile: &'static str,
    /// The output digest emitted by the native evaluator.
    pub v1_output_digest: String,
    /// SHA-256 of the domain prefix followed by the JCS report bytes.
    pub v2_fingerprint: String,
}

/// Evaluate a point or capacity request and fingerprint the complete native report.
///
/// The native evaluator validates the request and generates its usual report,
/// including the v1 input and output digests. The adapter covers the complete
/// report in a distinct domain. Exact amounts and rational components stay
/// encoded as JSON strings.
///
/// # Errors
///
/// Returns a structured error for an unknown profile, an invalid native
/// request, or a report containing numbers outside the safe-integer range.
pub fn fingerprint_report(profile: &str, request: &str) -> Result<ReportFingerprint, DapaneError> {
    if profile != PROFILE {
        return Err(DapaneError::new(
            "unsupported_fingerprint_profile",
            "Select dapane-canonical-v2 explicitly",
            "/profile",
        ));
    }

    let report: Value = serde_json::from_str(&evaluate_json(request)?).map_err(|_| {
        DapaneError::new(
            "invalid_native_report",
            "Could not read the native report",
            "/",
        )
    })?;
    let v1_digest = report
        .get("output_digest")
        .and_then(Value::as_str)
        .ok_or_else(|| {
            DapaneError::new(
                "invalid_native_report",
                "The native report has no output digest",
                "/output_digest",
            )
        })?;
    let canonical = canonical_report(&report)?;
    let mut hash = Sha256::new();
    hash.update(REPORT_DOMAIN);
    hash.update(canonical);
    let hexadecimal: String = hash
        .finalize()
        .iter()
        .map(|byte| format!("{byte:02x}"))
        .collect();
    Ok(ReportFingerprint {
        profile: PROFILE,
        v1_output_digest: v1_digest.to_owned(),
        v2_fingerprint: format!("sha256:{hexadecimal}"),
    })
}

fn canonical_report(report: &Value) -> Result<Vec<u8>, DapaneError> {
    if !has_safe_numbers(report) {
        return Err(DapaneError::new(
            "unsupported_fingerprint_number",
            "The fingerprint profile requires JSON numbers to be safe integers",
            "/",
        ));
    }
    serde_json_canonicalizer::to_vec(report).map_err(|_| {
        DapaneError::new(
            "fingerprint_serialization",
            "Could not canonicalize the native report",
            "/",
        )
    })
}

fn has_safe_numbers(value: &Value) -> bool {
    match value {
        Value::Number(number) => number
            .as_i64()
            .is_some_and(|number| (-MAX_SAFE_INTEGER..=MAX_SAFE_INTEGER).contains(&number)),
        Value::Array(items) => items.iter().all(has_safe_numbers),
        Value::Object(fields) => fields.values().all(has_safe_numbers),
        _ => true,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn jcs_orders_names_by_utf16_and_preserves_exact_strings() {
        let value = json!({
            "\u{fb33}": "1.00",
            "\u{1f600}": {"numerator": "1", "denominator": "3"},
            "\r": 9_007_199_254_740_991_i64,
        });
        let expected = "{\"\\r\":9007199254740991,\"😀\":{\"denominator\":\"3\",\"numerator\":\"1\"},\"דּ\":\"1.00\"}";
        assert_eq!(canonical_report(&value).unwrap(), expected.as_bytes());
    }

    #[test]
    fn jcs_rejects_lossy_numbers_in_nested_fields() {
        for number in [
            json!(-0.0),
            json!(100.0),
            json!(9_007_199_254_740_992_u64),
            json!(-9_007_199_254_740_992_i64),
            json!(i64::MAX),
            json!(i64::MIN),
            json!(u64::MAX),
        ] {
            assert_eq!(
                canonical_report(&json!({"nested": [{"value": number}]}))
                    .unwrap_err()
                    .code,
                "unsupported_fingerprint_number"
            );
        }
    }

    #[test]
    fn version_and_native_validation_fail_closed() {
        assert_eq!(
            fingerprint_report("dapane-canonical-v1", "{}")
                .unwrap_err()
                .code,
            "unsupported_fingerprint_profile"
        );
        let duplicate = r#"{"schema_version":"0.1","schema_version":"0.1"}"#;
        assert_eq!(
            fingerprint_report(PROFILE, duplicate).unwrap_err().code,
            "invalid_json"
        );
    }
}
