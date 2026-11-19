//! Adversarial regressions from interval-contract review.

use dapane_core::{evaluate_intervals_json, evaluate_json};
use serde_json::{Value, json};
use time::{Date, Duration, Month};

const LIMIT: usize = 4 * 1024 * 1024;

fn base() -> Value {
    serde_json::from_str(include_str!(
        "../../../fixtures/intervals/rate-boundary.json"
    ))
    .unwrap()
}

fn output(input: &Value) -> Value {
    serde_json::from_str(&evaluate_intervals_json(&input.to_string()).unwrap()).unwrap()
}

fn reject(input: &Value) -> dapane_core::DapaneError {
    let error = evaluate_intervals_json(&input.to_string()).unwrap_err();
    assert!(!error.code.is_empty());
    assert!(error.path.starts_with('/'));
    error
}

#[test]
fn modest_interval_input_cannot_expand_past_the_exact_byte_budget() {
    let mut input = base();
    let first = Date::from_calendar_date(2026, Month::January, 1).unwrap();
    let template = input["request"]["quotes"][0].clone();
    let mut quotes = Vec::new();
    let mut selected = Vec::new();
    for day in 0..100 {
        let mut quote = template.clone();
        let id = format!("daily-{day}");
        quote["id"] = json!(id);
        quote["amount"] = json!("1");
        quote["valid_from"] = json!((first + Duration::days(day)).to_string());
        quote["valid_to"] = json!((first + Duration::days(day + 1)).to_string());
        selected.push(json!(id));
        quotes.push(quote);
    }
    input["request"]["quotes"] = json!(quotes);
    input["intervals"][0]["start"] = json!(first.to_string());
    input["intervals"][0]["end"] = json!((first + Duration::days(100)).to_string());
    input["intervals"][0]["quote_ids"] = json!(selected);
    let ids: Vec<_> = (0..5000)
        .map(|index| format!("object-{index:04}"))
        .collect();
    input["request"]["objects"] = json!(
        ids.iter()
            .map(|id| json!({"id": id, "kind": "recipient"}))
            .collect::<Vec<_>>()
    );
    input["intervals"][0]["object_ids"] = json!(ids);
    let encoded = input.to_string();
    assert!(encoded.len() < LIMIT);
    // Even the repeated object arrays alone would exceed the transformed bound.
    assert!(input["intervals"][0]["object_ids"].to_string().len() * 100 > LIMIT);
    assert_eq!(reject(&input).code, "input_limit");
}

#[test]
fn generated_line_and_use_id_collisions_are_rejected() {
    let input = base();
    let result = output(&input);
    let generated = result["expanded_request"]["usage"][0].clone();
    for collide_on in ["id", "use_id"] {
        let mut collision = input.clone();
        let mut point = generated.clone();
        point["quantity"] = json!("0");
        point["id"] = json!("ordinary-zero-line");
        point["use_id"] = json!("ordinary-zero-use");
        point[collide_on] = generated[collide_on].clone();
        collision["request"]["usage"] = json!([point]);
        // The added point is independently valid. It fails only when combined
        // with the generated interval identities.
        assert!(evaluate_json(&collision["request"].to_string()).is_ok());
        reject(&collision);
    }
}

#[test]
fn duplicate_keys_inside_the_nested_request_are_rejected() {
    let text = base().to_string();
    let duplicate = text.replacen(
        "\"request\":{",
        "\"request\":{\"schema_version\":\"0.2\",",
        1,
    );
    assert_ne!(duplicate, text);
    let error = evaluate_intervals_json(&duplicate).unwrap_err();
    assert_eq!(error.code, "invalid_json");
}

#[test]
fn component_set_order_does_not_change_segment_selection_or_identity() {
    let mut input = base();
    for quote in input["request"]["quotes"].as_array_mut().unwrap() {
        quote["components"] = json!(["labour", "overhead"]);
    }
    let reference = output(&input);
    input["request"]["quotes"][1]["components"] = json!(["overhead", "labour"]);
    let reordered = output(&input);
    assert_eq!(reordered, reference);
    assert_eq!(reordered["report"]["totals"]["rounded"], "110.00");
}

#[test]
fn one_parent_cannot_claim_different_interval_ends_for_disjoint_components() {
    let mut input = base();
    let originals = input["request"]["quotes"].as_array().unwrap().clone();
    let mut selected = Vec::new();
    for mut quote in originals {
        let id = format!("{}-overhead", quote["id"].as_str().unwrap());
        quote["id"] = json!(id);
        quote["components"] = json!(["overhead"]);
        selected.push(json!(id));
        input["request"]["quotes"]
            .as_array_mut()
            .unwrap()
            .push(quote);
    }
    let mut second = input["intervals"][0].clone();
    second["id"] = json!("overhead-line");
    second["end"] = json!("2026-02-04");
    second["quote_ids"] = json!(selected);
    input["intervals"].as_array_mut().unwrap().push(second);
    reject(&input);
}

#[test]
fn generated_rational_must_fit_the_replayable_scalar_input_contract() {
    let mut input = base();
    input["intervals"][0]["quantity"] = json!({
        "numerator": "1",
        "denominator": "9".repeat(96)
    });
    // Dividing 1/(10^96 - 1) by three has an irreducible 97-digit
    // denominator, exceeding scalar input precision despite valid source input.
    assert_eq!(reject(&input).code, "precision_limit");
}

#[test]
fn parent_source_cannot_belong_to_both_full_and_capacity_pools() {
    let mut input = base();
    input["request"]["objects"] = json!([
        {"id": "a", "kind": "recipient"},
        {"id": "b", "kind": "recipient"}
    ]);
    input["request"]["allocations"] = json!([{
        "id": "full", "source_line_ids": ["scientist-line"],
        "weights": [{"object_id": "a", "weight": "1"}]
    }]);
    input["request"]["capacity_allocations"] = json!([{
        "id": "capacity", "source_line_ids": ["scientist-line"],
        "unit": "instrument_hour", "observation_coverage": "incomplete",
        "available_capacity": {"status": "known", "quantity": "10"},
        "use_records": [{
            "object_id": "b", "quantity": {"status": "known", "quantity": "1"}
        }],
        "source": input["intervals"][0]["source"]
    }]);
    reject(&input);
}

#[test]
fn selected_references_plus_original_points_have_a_combined_bound() {
    let mut input = base();
    input["request"]["usage"] = json!(
        (0..9999)
            .map(|index| {
                let id = format!("p{index}");
                json!({
                    "id": id, "use_id": id, "kind": "resource_use",
                    "target": "scientist-time", "unit": "hour", "quantity": "0",
                    "service_date": "2026-01-31", "quote_id": "before",
                    "source": {
                        "id": "s", "version": "1", "evidence": "synthetic",
                        "access": "public", "validation": "unvalidated"
                    }
                })
            })
            .collect::<Vec<_>>()
    );
    // Each collection is individually legal and the raw input is below 4 MiB.
    // Two selected quote references plus 9999 original points exceed 10000.
    assert!(input.to_string().len() < LIMIT);
    assert_eq!(reject(&input).code, "input_limit");
}
