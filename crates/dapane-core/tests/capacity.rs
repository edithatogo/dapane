//! Independent synthetic candidate cases, not validated economic formulae.

use dapane_core::evaluate_json;
use serde_json::{Value, json};

fn fixture(name: &str) -> Value {
    let path = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("../../fixtures/genomics-capacity")
        .join(name);
    serde_json::from_str(&std::fs::read_to_string(path).unwrap()).unwrap()
}

fn run(request: &Value) -> Value {
    serde_json::from_str(&evaluate_json(&request.to_string()).unwrap()).unwrap()
}

fn reject(request: &Value, code: &str) {
    assert_eq!(evaluate_json(&request.to_string()).unwrap_err().code, code);
}

#[test]
fn synthetic_time_and_sample_cases_match_independent_expected_values() {
    for (name, expected) in fixture("expected.json")["cases"].as_object().unwrap() {
        let report = run(&fixture(name));
        assert_eq!(report["schema_version"], expected["schema_version"]);
        for (actual, oracle) in [
            ("rounded", "total"),
            ("allocated", "allocated"),
            ("unattributed", "unattributed"),
        ] {
            assert_eq!(
                report["totals"][actual], expected[oracle],
                "{name}: {actual}"
            );
        }
        let capacity = expected["schema_version"] == "0.2";
        let pool = &report[if capacity {
            "capacity_allocations"
        } else {
            "allocations"
        }][0];
        assert_eq!(pool["pool_rounded"], expected["pool"]);
        assert_eq!(
            pool[if capacity { "unallocated" } else { "residual" }],
            expected["unallocated"]
        );
        for share in pool["shares"].as_array().unwrap() {
            assert_eq!(
                share["rounded"],
                expected["shares"][share["object_id"].as_str().unwrap()]
            );
        }
    }
}

#[test]
fn unknown_use_and_known_zero_remain_distinct() {
    let mut request = fixture("time-missing-use.json");
    let unknown = run(&request);
    let share = &unknown["capacity_allocations"][0]["shares"][1];
    assert_eq!(share["quantity"]["status"], "unknown");
    assert!(share["exact_share"].is_null());
    assert!(share["rounded"].is_null());
    request["capacity_allocations"][0]["use_records"][1]["quantity"] =
        json!({"status":"known","quantity":"0"});
    let zero = run(&request);
    assert_eq!(
        zero["capacity_allocations"][0]["shares"][1]["rounded"],
        "0.00"
    );
    assert_eq!(
        zero["capacity_allocations"][0]["shares"][1]["exact_share"],
        json!({"numerator":"0","denominator":"1"})
    );
    assert_eq!(zero["totals"], unknown["totals"]);
    assert_ne!(zero["input_digest"], unknown["input_digest"]);
}

#[test]
fn unknown_capacity_preserves_observations_without_inventing_a_denominator() {
    let report = run(&fixture("time-unknown-capacity.json"));
    let pool = &report["capacity_allocations"][0];
    assert_eq!(pool["available_capacity"]["status"], "unknown");
    assert_eq!(
        pool["accounted_quantity"],
        json!({"numerator":"10","denominator":"1"})
    );
    assert!(pool["unaccounted_quantity"].is_null());
    assert_eq!(
        pool["unallocated_exact"],
        json!({"numerator":"300","denominator":"1"})
    );
    assert!(
        pool["shares"]
            .as_array()
            .unwrap()
            .iter()
            .all(|x| x["rounded"].is_null())
    );
    assert!(pool.get("utilization").is_none());
}

#[test]
fn capacity_rounding_includes_unallocated_bucket_with_explicit_tie_priority() {
    let mut request = fixture("time-known.json");
    request["usage"]
        .as_array_mut()
        .unwrap()
        .retain(|x| x["id"] == "device-period");
    request["quotes"]
        .as_array_mut()
        .unwrap()
        .retain(|x| x["id"] == "device-period-quote");
    request["quotes"][0]["amount"] = json!("0.05");
    let pool = &mut request["capacity_allocations"][0];
    pool["source_line_ids"] = json!(["device-period"]);
    pool["available_capacity"]["quantity"] = json!("3");
    for record in pool["use_records"].as_array_mut().unwrap() {
        record["quantity"]["quantity"] = json!("1");
    }
    let report = run(&request);
    let result = &report["capacity_allocations"][0];
    // Three exact 1/60 shares: two extra cents go to unallocated, then cohort-a.
    assert_eq!(
        result["shares"][0]["exact_share"],
        json!({"numerator":"1","denominator":"60"})
    );
    assert_eq!(
        result["unallocated_exact"],
        json!({"numerator":"1","denominator":"60"})
    );
    assert_eq!(result["shares"][0]["rounded"], "0.02");
    assert_eq!(result["shares"][1]["rounded"], "0.01");
    assert_eq!(result["unallocated"], "0.02");
    assert_eq!(report["totals"]["allocated"], "0.03");
    assert_eq!(report["totals"]["unattributed"], "0.02");
}

#[test]
fn capacity_inputs_reject_invalid_denominators_units_and_overlapping_costs() {
    let base = fixture("time-known.json");
    for value in ["0", "-1"] {
        let mut request = base.clone();
        request["capacity_allocations"][0]["available_capacity"]["quantity"] = json!(value);
        let error = evaluate_json(&request.to_string()).unwrap_err();
        assert!(["invalid_capacity", "invalid_number"].contains(&error.code.as_str()));
    }
    let mut request = base.clone();
    request["capacity_allocations"][0]["available_capacity"]["quantity"] = json!("29");
    reject(&request, "capacity_exceeded");
    let mut request = base.clone();
    request["capacity_allocations"][0]["unit"] = json!("sample");
    reject(&request, "invalid_request");
    let mut request = base.clone();
    request["capacity_allocations"][0]
        .as_object_mut()
        .unwrap()
        .remove("available_capacity");
    reject(&request, "invalid_request");
    let mut request = base.clone();
    request["capacity_allocations"][0]["use_records"][0]["quantity"] =
        json!({"status":"unknown","quantity":"10","reason":"missing"});
    reject(&request, "invalid_request");
    let mut request = base.clone();
    request["capacity_allocations"][0]["use_records"][1]["object_id"] = json!("cohort-a");
    reject(&request, "duplicate_recipient");
    let mut request = base.clone();
    request["usage"][0]["attribution_object_id"] = json!("cohort-a");
    reject(&request, "allocation_overlap");
    let mut request = base;
    request["allocations"] = fixture("sample-full-first.json")["allocations"].clone();
    reject(&request, "allocation_overlap");
}

#[test]
fn capacity_order_is_canonical_and_units_are_never_derived_from_sample_weights() {
    let mut request = fixture("time-known.json");
    let before = run(&request);
    request["capacity_allocations"][0]["use_records"]
        .as_array_mut()
        .unwrap()
        .reverse();
    request["capacity_allocations"][0]["source_line_ids"]
        .as_array_mut()
        .unwrap()
        .reverse();
    assert_eq!(run(&request), before);
    request["capacity_allocations"][0]["sample_throughput"] = json!("50");
    reject(&request, "invalid_request");
}

#[test]
fn v01_weights_still_allocate_the_whole_pool_and_reject_capacity_extensions() {
    let mut request = fixture("sample-full-first.json");
    request["allocations"][0]["weights"][0]["weight"] = json!("0.1");
    request["allocations"][0]["weights"][1]["weight"] = json!("0.2");
    let report = run(&request);
    assert_eq!(report["allocations"][0]["shares"][0]["rounded"], "100.00");
    assert_eq!(report["allocations"][0]["shares"][1]["rounded"], "200.00");
    assert_eq!(report["allocations"][0]["residual"], "0.00");
    assert!(report.get("capacity_allocations").is_none());
    request["capacity_allocations"] = json!([]);
    reject(&request, "invalid_request");
    request["capacity_allocations"] = fixture("time-known.json")["capacity_allocations"].clone();
    reject(&request, "invalid_request");
}

#[test]
fn all_five_v01_fixture_digests_are_unchanged_from_integrated_runtime() {
    for (name, expected) in fixture("v0.1-digests.json")["fixtures"]
        .as_object()
        .unwrap()
    {
        let path = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("../../fixtures")
            .join(name);
        let result: Value =
            serde_json::from_str(&evaluate_json(&std::fs::read_to_string(path).unwrap()).unwrap())
                .unwrap();
        assert_eq!(result["input_digest"], expected["input_digest"], "{name}");
        assert_eq!(result["output_digest"], expected["output_digest"], "{name}");
    }
}

#[test]
fn direct_full_pool_and_partial_capacity_views_compose_without_double_counting() {
    let mut request = fixture("time-known.json");
    request["usage"][2]["attribution_object_id"] = json!("cohort-a");
    let mut quote = request["quotes"][2].clone();
    quote["id"] = json!("batch-quote");
    quote["target"] = json!("assay-batch");
    quote["unit"] = json!("batch");
    quote["amount"] = json!("50.00");
    quote["components"] = json!(["assay-batch"]);
    request["quotes"].as_array_mut().unwrap().push(quote);
    let mut usage = request["usage"][0].clone();
    usage["id"] = json!("batch");
    usage["use_id"] = json!("batch-use");
    usage["target"] = json!("assay-batch");
    usage["unit"] = json!("batch");
    usage["quote_id"] = json!("batch-quote");
    request["usage"].as_array_mut().unwrap().push(usage);
    request["allocations"] = json!([{"id":"batch-full","source_line_ids":["batch"],"weights":[{"object_id":"cohort-a","weight":"1"},{"object_id":"cohort-b","weight":"1"}]}]);
    let report = run(&request);
    // 600 direct + 50 full pool + (30+60) capacity + 210 unallocated = 950.
    assert_eq!(report["totals"]["rounded"], "950.00");
    assert_eq!(report["totals"]["directly_attributed"], "600.00");
    assert_eq!(report["totals"]["allocated"], "140.00");
    assert_eq!(report["totals"]["unattributed"], "210.00");
    assert_eq!(report["object_totals"][0]["total"], "655.00");
    assert_eq!(report["object_totals"][1]["total"], "85.00");
    assert_eq!(report["allocations"][0]["residual"], "0.00");
    assert_eq!(report["capacity_allocations"][0]["unallocated"], "210.00");
}
