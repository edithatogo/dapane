//! Independent synthetic acceptance for the separately versioned interval method.

use dapane_core::{evaluate_intervals_json, evaluate_json};
use serde_json::{Value, json};

fn base() -> Value {
    serde_json::from_str(include_str!("../../../fixtures/intervals/rate-boundary.json")).unwrap()
}

fn output(input: &Value) -> Value {
    serde_json::from_str(&evaluate_intervals_json(&input.to_string()).unwrap()).unwrap()
}

fn reject(input: &Value) {
    let error = evaluate_intervals_json(&input.to_string()).unwrap_err();
    assert!(!error.code.is_empty());
    assert!(!error.message.is_empty());
    assert!(error.path.starts_with('/'));
}

fn rational(numerator: &str, denominator: &str) -> Value {
    json!({"numerator": numerator, "denominator": denominator})
}

#[test]
fn independent_rate_boundary_and_parent_lineage_are_preserved() {
    // Three calendar days: (1/3 hour * 90) + (2/3 hour * 120) = 110.
    let input = base();
    let result = output(&input);
    assert_eq!(result["method_version"], "dapane-intervals-v0.1.0");
    assert_eq!(result["report"]["status"], "complete");
    assert_eq!(result["report"]["totals"]["exact"], rational("110", "1"));
    assert_eq!(result["report"]["totals"]["rounded"], "110.00");
    assert_eq!(result["request_snapshot"]["usage"], json!([]));
    let segments = result["segments"].as_array().unwrap();
    assert_eq!(segments.len(), 2);
    for (start, end, quote, quantity, expected) in [
        ("2026-01-31", "2026-02-01", "before", rational("1", "3"), "30.00"),
        ("2026-02-01", "2026-02-03", "after", rational("2", "3"), "80.00"),
    ] {
        let segment = segments.iter().find(|s| s["start"] == start).unwrap();
        assert_eq!(segment["end"], end);
        assert_eq!(segment["quote_id"], quote);
        assert_eq!(segment["quantity"], quantity);
        assert_eq!(segment["interval_id"], "scientist-line");
        assert_eq!(segment["use_id"], "scientist-use");
        let line = result["report"]["lines"]
            .as_array()
            .unwrap()
            .iter()
            .find(|line| line["id"] == segment["line_id"])
            .unwrap();
        assert_eq!(line["quantity"], quantity);
        assert_eq!(line["rounded"], expected);
        assert_eq!(
            line["source"]["id"],
            input["intervals"][0]["source"]["id"]
        );
    }
    assert_eq!(result["interval_snapshots"][0]["quantity"], "1");
    let replay: Value = serde_json::from_str(
        &evaluate_json(&result["expanded_request"].to_string()).unwrap(),
    )
    .unwrap();
    assert_eq!(replay, result["report"]);
}

#[test]
fn boundaries_are_half_open_and_leap_days_are_calendar_days() {
    let mut input = base();
    input["intervals"][0]["start"] = json!("2026-02-01");
    input["intervals"][0]["quote_ids"] = json!(["after"]);
    let result = output(&input);
    assert_eq!(result["segments"].as_array().unwrap().len(), 1);
    assert_eq!(result["report"]["totals"]["rounded"], "120.00");

    let mut input = base();
    input["intervals"][0]["start"] = json!("2024-02-28");
    input["intervals"][0]["end"] = json!("2024-03-02");
    input["request"]["quotes"][0]["valid_from"] = json!("2024-01-01");
    input["request"]["quotes"][0]["valid_to"] = json!("2024-03-01");
    input["request"]["quotes"][1]["valid_from"] = json!("2024-03-01");
    let result = output(&input);
    assert_eq!(result["report"]["totals"]["rounded"], "100.00");
    assert!(result["segments"].as_array().unwrap().iter().any(|segment| {
        segment["quote_id"] == "before" && segment["quantity"] == rational("2", "3")
    }));
}

#[test]
fn segment_rounding_is_explicit_and_does_not_claim_split_invariance() {
    let mut input = base();
    input["intervals"][0]["end"] = json!("2026-02-02");
    for quote in input["request"]["quotes"].as_array_mut().unwrap() {
        quote["amount"] = json!("0.01");
    }
    let result = output(&input);
    assert_eq!(result["report"]["totals"]["exact"], rational("1", "100"));
    assert_eq!(result["report"]["totals"]["rounded"], "0.00");
    assert_eq!(
        result["report"]["totals"]["rounding_adjustment"],
        rational("-1", "100")
    );
}

#[test]
fn weighted_activity_is_valued_without_manufacturing_resource_use() {
    let mut input = base();
    input["request"]["policy"]["basis"] = json!("funding");
    input["intervals"][0]["quantity"] = json!("2.50");
    input["intervals"][0]["start"] = json!("2026-02-01");
    input["intervals"][0]["quote_ids"] = json!(["after"]);
    input["intervals"][0]["kind"] = json!("activity_measure");
    input["intervals"][0]["unit"] = json!("weighted_unit");
    for quote in input["request"]["quotes"].as_array_mut().unwrap() {
        quote["amount"] = json!("17.00");
        quote["basis"] = json!("funding");
        quote["kind"] = json!("activity_measure");
        quote["unit"] = json!("weighted_unit");
    }
    let result = output(&input);
    assert_eq!(result["report"]["totals"]["rounded"], "42.50");
    assert_eq!(result["report"]["lines"][0]["kind"], "activity_measure");
}

#[test]
fn request_order_does_not_change_output_and_decimal_provenance_does() {
    let input = base();
    let reference = output(&input);
    let mut reordered = input.clone();
    reordered["request"]["quotes"].as_array_mut().unwrap().reverse();
    reordered["intervals"][0]["quote_ids"].as_array_mut().unwrap().reverse();
    assert_eq!(output(&reordered), reference);
    let mut respelled = input;
    respelled["intervals"][0]["quantity"] = json!("1.00");
    let changed = output(&respelled);
    assert_eq!(changed["report"]["totals"], reference["report"]["totals"]);
    assert_ne!(changed["input_digest"], reference["input_digest"]);
    assert_ne!(changed["output_digest"], reference["output_digest"]);
}

#[test]
fn parent_pool_expands_and_conserves_value_and_zero_residual() {
    let mut input = base();
    input["request"]["objects"] = json!([
        {"id":"a", "kind":"recipient"}, {"id":"b", "kind":"recipient"}
    ]);
    input["request"]["allocations"] = json!([{
        "id":"pool", "source_line_ids":["scientist-line"],
        "weights":[{"object_id":"a", "weight":"1"}, {"object_id":"b", "weight":"1"}]
    }]);
    let result = output(&input);
    let pool = &result["report"]["allocations"][0];
    assert_eq!(pool["source_line_ids"].as_array().unwrap().len(), 2);
    assert_eq!(pool["pool_rounded"], "110.00");
    assert_eq!(pool["shares"][0]["rounded"], "55.00");
    assert_eq!(pool["shares"][1]["rounded"], "55.00");
    assert_eq!(pool["residual"], "0.00");
    assert_eq!(
        result["request_snapshot"]["allocations"][0]["source_line_ids"],
        json!(["scientist-line"])
    );
    let mut duplicate = input.clone();
    duplicate["request"]["allocations"][0]["source_line_ids"] =
        json!(["scientist-line", "scientist-line"]);
    reject(&duplicate);
    input["intervals"][0]["attribution_object_id"] = json!("a");
    reject(&input);
}

#[test]
fn capacity_expansion_retains_unknown_usage_and_unallocated_value() {
    let mut input = base();
    input["request"]["objects"] = json!([
        {"id":"a", "kind":"recipient"}, {"id":"b", "kind":"recipient"}
    ]);
    input["request"]["capacity_allocations"] = json!([{
        "id":"capacity", "source_line_ids":["scientist-line"],
        "unit":"instrument_hour", "observation_coverage":"incomplete",
        "available_capacity":{"status":"known", "quantity":"10"},
        "use_records":[
            {"object_id":"a", "quantity":{"status":"known", "quantity":"3"}},
            {"object_id":"b", "quantity":{"status":"unknown", "reason":"Missing observation"}}
        ],
        "source":input["intervals"][0]["source"]
    }]);
    let result = output(&input);
    let pool = &result["report"]["capacity_allocations"][0];
    assert_eq!(pool["source_line_ids"].as_array().unwrap().len(), 2);
    assert_eq!(pool["pool_rounded"], "110.00");
    assert_eq!(pool["shares"][0]["rounded"], "33.00");
    assert!(pool["shares"][1]["rounded"].is_null());
    assert!(pool["shares"][1]["exact_share"].is_null());
    assert_eq!(pool["unallocated"], "77.00");
    assert_eq!(result["report"]["totals"]["unattributed"], "77.00");
    assert_eq!(result["report"]["totals"]["allocated"], "33.00");
    let replay: Value = serde_json::from_str(
        &evaluate_json(&result["expanded_request"].to_string()).unwrap(),
    )
    .unwrap();
    assert_eq!(replay, result["report"]);
}

#[test]
fn invalid_dates_exposure_precision_and_coverage_never_return_a_report() {
    for (pointer, value) in [
        ("/schema_version", json!("2.0")),
        ("/intervals/0/start", json!("2026-02-30")),
        ("/intervals/0/end", json!("2026-01-31")),
        ("/intervals/0/exposure", json!("infer_uniform")),
        ("/intervals/0/quantity", json!(0.5)),
        ("/intervals/0/quantity", json!({"numerator":"1", "denominator":"0"})),
        ("/intervals/0/quote_ids", json!([])),
        ("/intervals/0/quote_ids", json!(["before", "before", "after"])),
        ("/intervals/0/quote_ids", json!(["missing"])),
        ("/request/quotes/1/valid_from", json!("2026-02-02")),
        ("/request/quotes/1/valid_from", json!("2026-01-31")),
        ("/request/quotes/1/known_from", json!("2026-02-04")),
        ("/request/quotes/1/components", json!(["other-component"])),
        ("/request/quotes/1/unit", json!("minute")),
        ("/request/quotes/1/basis", json!("funding")),
        ("/intervals/0/use_id", json!("é".repeat(65))),
    ] {
        let mut input = base();
        *input.pointer_mut(pointer).unwrap() = value;
        reject(&input);
    }
    let mut irrelevant = base();
    irrelevant["intervals"][0]["start"] = json!("2026-02-01");
    reject(&irrelevant);
    let mut missing = base();
    missing["intervals"][0].as_object_mut().unwrap().remove("exposure");
    reject(&missing);
    let mut empty = base();
    empty["intervals"] = json!([]);
    reject(&empty);
}

#[test]
fn parent_identity_blocks_duplicate_component_charges_before_child_ids_are_made() {
    let mut input = base();
    let mut duplicate = input["intervals"][0].clone();
    duplicate["id"] = json!("second-line");
    input["intervals"].as_array_mut().unwrap().push(duplicate);
    reject(&input);
    input["intervals"][1]["end"] = json!("2026-02-04");
    reject(&input);

    let mut input = base();
    input["request"]["usage"] = json!([{
        "id":"point-line", "use_id":"scientist-use", "kind":"resource_use",
        "target":"scientist-time", "unit":"hour", "quantity":"1",
        "service_date":"2026-01-31", "quote_id":"before",
        "source": input["intervals"][0]["source"]
    }]);
    reject(&input);
}

#[test]
fn disjoint_component_lines_share_a_parent_without_double_counting() {
    let mut input = base();
    let mut second = input["intervals"][0].clone();
    second["id"] = json!("overhead-line");
    second["quote_ids"] = json!(["overhead"]);
    let mut quote = input["request"]["quotes"][0].clone();
    quote["id"] = json!("overhead");
    quote["amount"] = json!("3");
    quote["components"] = json!(["overhead"]);
    quote["valid_to"] = json!("2027-01-01");
    input["request"]["quotes"].as_array_mut().unwrap().push(quote);
    input["intervals"].as_array_mut().unwrap().push(second);
    let result = output(&input);
    assert_eq!(result["report"]["totals"]["rounded"], "113.00");
    assert_eq!(result["segments"].as_array().unwrap().len(), 3);
}

#[test]
fn strict_transport_rejects_duplicate_keys_and_legacy_implicit_intervals() {
    let input = base();
    let mut duplicate = input.to_string();
    duplicate.pop();
    duplicate.push_str(",\"schema_version\":\"0.1\"}");
    assert_eq!(evaluate_intervals_json(&duplicate).unwrap_err().code, "invalid_json");
    for version in ["0.1", "0.2"] {
        let mut legacy = input["request"].clone();
        legacy["schema_version"] = json!(version);
        legacy["intervals"] = input["intervals"].clone();
        assert!(evaluate_json(&legacy.to_string()).is_err());
    }
    let mut nested = base();
    nested["request"]["schema_version"] = json!("0.1");
    nested["request"]["capacity_allocations"] = json!([]);
    reject(&nested);
}

#[test]
fn exact_quantity_conservation_holds_for_many_independent_durations() {
    // Each split is one day before, N days after; total quantity is (N+1)/7.
    // Therefore exact segment quantities must always be 1/7 and N/7.
    for days_after in 1..=25 {
        let mut input = base();
        input["intervals"][0]["end"] = json!(format!("2026-02-{:02}", days_after + 1));
        input["intervals"][0]["quantity"] = rational(&(days_after + 1).to_string(), "7");
        let result = output(&input);
        let before = result["segments"]
            .as_array()
            .unwrap()
            .iter()
            .find(|segment| segment["quote_id"] == "before")
            .unwrap();
        assert_eq!(before["quantity"], rational("1", "7"));
        let exact = &result["report"]["totals"]["exact"];
        let numerator: i64 = exact["numerator"].as_str().unwrap().parse().unwrap();
        let denominator: i64 = exact["denominator"].as_str().unwrap().parse().unwrap();
        assert_eq!(numerator * 7, (90 + 120 * days_after) * denominator);
    }
}
