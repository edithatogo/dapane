//! Compare the adapter with fingerprints derived from CLI and installed Python reports.

use dapane_canonical_v2::{PROFILE, fingerprint_report};
use serde_json::Value;

#[test]
fn historical_point_reports_keep_v1_and_match_independent_v2() {
    let historical: Value = serde_json::from_str(include_str!(
        "../../../fixtures/genomics-capacity/v0.1-digests.json"
    ))
    .unwrap();
    let references = &historical["fixtures"];
    let cases = [
        (
            "activity-funding.json",
            include_str!("../../../fixtures/activity-funding.json"),
            "sha256:d971321c12dc603ac172de1b73a2a2a5affd6c718c7e64bd5d88afcda6154271",
        ),
        (
            "genomics.json",
            include_str!("../../../fixtures/genomics.json"),
            "sha256:c2e6e7ba73796d929f0d278e277c4ed3e5638cf3071ba631918ae5bf33a912a3",
        ),
        (
            "newborn-screening.json",
            include_str!("../../../fixtures/newborn-screening.json"),
            "sha256:a2f285a0cac74b86e2f344d7cc675bbd2140fd6b1e1d58d710b60818475cee07",
        ),
        (
            "subcent-allocation.json",
            include_str!("../../../fixtures/subcent-allocation.json"),
            "sha256:1c19b210aa0d56ce3ae281b19b6e5046e1108456575f3b9bda5c358bc90264de",
        ),
        (
            "workforce.json",
            include_str!("../../../fixtures/workforce.json"),
            "sha256:1caa9a3f90cd0d7b3ab5a07c12fe9df1ab14e6c596adbe5ef5aad806e78d2e6e",
        ),
    ];
    for (name, request, expected) in cases {
        let fingerprint = fingerprint_report(PROFILE, request).unwrap();
        assert_eq!(fingerprint.profile, PROFILE);
        assert_eq!(
            fingerprint.v1_output_digest,
            references[name]["output_digest"].as_str().unwrap(),
            "{name}"
        );
        assert_eq!(fingerprint.v2_fingerprint, expected, "{name}");
    }
}

#[test]
fn capacity_report_matches_the_independent_fingerprint() {
    let request = include_str!("../../../fixtures/genomics-capacity/time-known.json");
    let fingerprint = fingerprint_report(PROFILE, request).unwrap();
    assert_eq!(
        fingerprint.v1_output_digest,
        "sha256:2e01e2a8161d9419f3a51bdeb6e6efa007c1b13cef4bcde525c3b3dc09d69c70"
    );
    assert_eq!(
        fingerprint.v2_fingerprint,
        "sha256:ed844972e68958e58652efaf9252a134908c12371eb25879aded0e4515ec9842"
    );
}
