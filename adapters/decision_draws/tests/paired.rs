//! Independent synthetic references and rejection controls for D1.

use dapane_decision_fiscal::paired::{draw_set_digest_json, evaluate_paired_json};
use serde_json::{Value, json};

fn rational(n: &str, d: &str) -> Value {
    json!({"numerator": n, "denominator": d})
}

fn fixture() -> Value {
    serde_json::from_str(include_str!("../fixtures/paired-synthetic.json")).unwrap()
}

fn output(input: &Value) -> Value {
    serde_json::from_str(&evaluate_paired_json(&input.to_string()).unwrap()).unwrap()
}

fn refresh_draw_digest(input: &mut Value) {
    input["outcomes"]["draw_set_digest"] =
        json!(draw_set_digest_json(&input["draws"].to_string()).unwrap());
}

#[test]
fn actual_cost_model_uses_correlated_draws_and_independent_outcomes() {
    // Joint support: (hours, rate) = (1/3, 30), (2/3, 60).
    // Costs: 10,40; a two-use alternative: 20,80. No independent shuffling.
    let report = output(&fixture());
    let rows = report["rows"].as_array().unwrap();
    assert_eq!(rows.len(), 4);
    let observed: Vec<_> = rows
        .iter()
        .map(|r| {
            (
                r["key"]["strategy_id"].as_str().unwrap(),
                r["key"]["draw_id"].as_str().unwrap(),
                r["cost_report"]["totals"]["rounded"].as_str().unwrap(),
                r["outcome"]["value"].clone(),
            )
        })
        .collect();
    assert_eq!(
        observed,
        vec![
            ("alternative", "draw-a", "20.00", rational("3", "2")),
            ("alternative", "draw-b", "80.00", rational("5", "2")),
            ("reference", "draw-a", "10.00", rational("1", "1")),
            ("reference", "draw-b", "40.00", rational("2", "1")),
        ]
    );
    assert_eq!(
        report["outcome_contract"]["model"]["id"],
        "synthetic-health-model"
    );
    assert_eq!(report["draws"]["axis"], "epistemic_parameters");
    assert_eq!(
        report["design"]["replication_axis"],
        "conditional_replication"
    );
}

#[test]
fn outer_row_and_axis_reordering_is_byte_reproducible() {
    let original = fixture();
    let mut changed = original.clone();
    for path in [
        "/draws/rows",
        "/models",
        "/outcomes/rows",
        "/design/strategies",
    ] {
        changed
            .pointer_mut(path)
            .unwrap()
            .as_array_mut()
            .unwrap()
            .reverse();
    }
    for model in changed["models"].as_array_mut().unwrap() {
        model["bindings"].as_array_mut().unwrap().reverse();
    }
    assert_eq!(
        evaluate_paired_json(&original.to_string()).unwrap(),
        evaluate_paired_json(&changed.to_string()).unwrap(),
    );
}

#[test]
fn missing_extra_and_duplicate_outcomes_are_rejected() {
    for mode in ["missing", "extra", "duplicate"] {
        let mut input = fixture();
        let rows = input["outcomes"]["rows"].as_array_mut().unwrap();
        match mode {
            "missing" => {
                rows.pop();
            }
            "extra" => {
                rows[0]["key"]["draw_id"] = json!("not-in-draw-set");
            }
            _ => {
                rows.push(rows[0].clone());
            }
        }
        assert_eq!(
            evaluate_paired_json(&input.to_string()).unwrap_err().code,
            "pairing_mismatch",
        );
    }
}

#[test]
fn joint_draw_identity_cannot_be_replaced_by_marginal_labels() {
    let mut input = fixture();
    input["draws"]["rows"][0]["values"]["rate"] = rational("31", "1");
    assert_eq!(
        evaluate_paired_json(&input.to_string()).unwrap_err().code,
        "draw_digest_mismatch",
    );
    refresh_draw_digest(&mut input);
    assert_eq!(
        output(&input)["rows"][0]["cost_report"]["totals"]["rounded"],
        "20.66"
    );
}

#[test]
fn incomplete_draw_values_and_duplicate_draws_fail_closed() {
    let mut input = fixture();
    input["draws"]["rows"][0]["values"]
        .as_object_mut()
        .unwrap()
        .remove("rate");
    assert_eq!(
        evaluate_paired_json(&input.to_string()).unwrap_err().code,
        "draw_parameters"
    );
    let mut input = fixture();
    let second = input["draws"]["rows"][0].clone();
    input["draws"]["rows"][1] = second;
    assert_eq!(
        evaluate_paired_json(&input.to_string()).unwrap_err().code,
        "duplicate_identity"
    );
}

#[test]
fn missing_model_cell_or_silently_pooled_subgroup_is_rejected() {
    let mut input = fixture();
    input["models"].as_array_mut().unwrap().pop();
    assert_eq!(
        evaluate_paired_json(&input.to_string()).unwrap_err().code,
        "model_panel_mismatch"
    );
    let mut input = fixture();
    input["outcomes"]["rows"][0]["key"]["subgroup_id"] = json!("pooled");
    assert_eq!(
        evaluate_paired_json(&input.to_string()).unwrap_err().code,
        "pairing_mismatch"
    );
}

#[test]
fn every_key_axis_survives_multiple_cells_and_replications() {
    let mut input = fixture();
    input["design"]["replications"] = json!(["rep-a", "rep-b"]);
    input["design"]["subgroups"] = json!(["Māori", "non-Māori"]);
    input["design"]["scenarios"] = json!(["scenario-a", "scenario-b"]);
    let old_models = input["models"].as_array().unwrap().clone();
    let old_outcomes = input["outcomes"]["rows"].as_array().unwrap().clone();
    let mut models = vec![];
    let mut outcomes = vec![];
    for rep in ["rep-a", "rep-b"] {
        for subgroup in ["Māori", "non-Māori"] {
            for scenario in ["scenario-a", "scenario-b"] {
                for model in &old_models {
                    let mut m = model.clone();
                    m["cell"]["replication_id"] = json!(rep);
                    m["cell"]["subgroup_id"] = json!(subgroup);
                    m["cell"]["scenario_id"] = json!(scenario);
                    models.push(m);
                }
                for row in &old_outcomes {
                    let mut r = row.clone();
                    r["key"]["replication_id"] = json!(rep);
                    r["key"]["subgroup_id"] = json!(subgroup);
                    r["key"]["scenario_id"] = json!(scenario);
                    outcomes.push(r);
                }
            }
        }
    }
    input["models"] = json!(models);
    input["outcomes"]["rows"] = json!(outcomes);
    let result = output(&input);
    assert_eq!(result["rows"].as_array().unwrap().len(), 32);
    for row in result["rows"].as_array().unwrap() {
        assert_eq!(row["key"], row["outcome"]["key"]);
        assert_eq!(row["key"]["perspective"], "health_system");
    }
}

#[test]
fn unsupported_method_unknown_fields_and_numeric_floats_are_rejected() {
    for path in ["/schema_version", "/models/0/method"] {
        let mut input = fixture();
        *input.pointer_mut(path).unwrap() = json!("unqualified-provider-method");
        assert!(evaluate_paired_json(&input.to_string()).is_err());
    }
    let mut input = fixture();
    input["outcomes"]["model"]["qualified"] = json!(true);
    assert!(evaluate_paired_json(&input.to_string()).is_err());
    let mut input = fixture();
    input["outcomes"]["rows"][0]["value"] = json!(1.5);
    assert!(evaluate_paired_json(&input.to_string()).is_err());
}

#[test]
fn duplicate_json_keys_are_rejected_at_every_boundary() {
    let valid = fixture().to_string();
    for (before, after) in [
        (
            "\"draw_id\":\"draw-a\"",
            "\"draw_id\":\"draw-a\",\"draw_id\":\"draw-a\"",
        ),
        (
            "\"quantity\":\"1\"",
            "\"quantity\":\"1\",\"quantity\":\"2\"",
        ),
        (
            "\"numerator\":\"30\"",
            "\"numerator\":\"30\",\"numerator\":\"60\"",
        ),
    ] {
        assert!(valid.contains(before));
        let bad = valid.replacen(before, after, 1);
        assert_eq!(evaluate_paired_json(&bad).unwrap_err().code, "invalid_json");
    }
}

#[test]
fn binding_targets_and_units_must_be_unambiguous_and_compatible() {
    for mode in ["missing", "duplicate", "unit", "parameter"] {
        let mut input = fixture();
        match mode {
            "missing" => input["models"][0]["bindings"][0]["target_id"] = json!("absent"),
            "unit" => input["draws"]["parameters"]["hours"] = json!("day"),
            "parameter" => input["models"][0]["bindings"][0]["parameter_id"] = json!("absent"),
            _ => {
                let b = input["models"][0]["bindings"][0].clone();
                input["models"][0]["bindings"]
                    .as_array_mut()
                    .unwrap()
                    .push(b);
            }
        }
        refresh_draw_digest(&mut input);
        assert!(evaluate_paired_json(&input.to_string()).is_err(), "{mode}");
    }
}

#[test]
fn embedded_core_errors_abort_the_entire_batch() {
    let mut input = fixture();
    input["models"][1]["request"]["quotes"][0]["valid_to"] = json!("2025-01-01");
    let error = evaluate_paired_json(&input.to_string()).unwrap_err();
    assert!(error.path.starts_with("/models/"));
    let mut input = fixture();
    input["models"][0]["request"]["capacity_allocations"] = json!([]);
    assert!(
        evaluate_paired_json(&input.to_string()).is_err(),
        "raw 0.1 must stay strict"
    );
}

#[test]
fn perspective_currency_and_source_mismatches_are_rejected() {
    for mode in ["perspective", "currency", "source", "year", "basis"] {
        let mut input = fixture();
        match mode {
            "perspective" => {
                input["models"][0]["request"]["policy"]["perspective"] = json!("societal")
            }
            "currency" => input["models"][0]["request"]["policy"]["currency"] = json!("NZD"),
            "year" => input["models"][0]["request"]["policy"]["price_year"] = json!(2025),
            "basis" => input["models"][0]["request"]["policy"]["basis"] = json!("funding"),
            _ => {
                input["models"][0]["request"]["quotes"][0]["source"]["evidence"] = json!("observed")
            }
        }
        assert!(evaluate_paired_json(&input.to_string()).is_err(), "{mode}");
    }
}

#[test]
fn negative_outcomes_are_preserved_but_negative_cost_parameters_are_rejected() {
    let mut input = fixture();
    input["outcomes"]["rows"][0]["value"] = rational("-1", "2");
    let r = output(&input);
    assert!(
        r["rows"]
            .as_array()
            .unwrap()
            .iter()
            .any(|r| r["outcome"]["value"] == rational("-1", "2"))
    );
    input["draws"]["rows"][0]["values"]["hours"] = rational("-1", "3");
    refresh_draw_digest(&mut input);
    assert_eq!(
        evaluate_paired_json(&input.to_string()).unwrap_err().code,
        "negative_cost_parameter",
    );
}

#[test]
fn malformed_exact_values_and_resource_bounds_fail_closed() {
    for bad in [
        rational("1", "0"),
        rational("+1", "1"),
        rational("1", "-2"),
        rational("1e3", "1"),
        rational(&"9".repeat(97), "1"),
    ] {
        let mut input = fixture();
        input["outcomes"]["rows"][0]["value"] = bad;
        assert!(evaluate_paired_json(&input.to_string()).is_err());
    }
    let mut input = fixture();
    input["design"]["replications"] =
        json!((0..300).map(|i| format!("rep-{i}")).collect::<Vec<_>>());
    assert_eq!(
        evaluate_paired_json(&input.to_string()).unwrap_err().code,
        "input_limit"
    );
    assert_eq!(
        evaluate_paired_json(&" ".repeat(4 * 1024 * 1024 + 1))
            .unwrap_err()
            .code,
        "input_limit",
    );
}

#[test]
fn interval_evaluation_retains_per_generated_segment_rounding() {
    let mut input = fixture();
    let mut envelope: Value = serde_json::from_str(include_str!(
        "../../../fixtures/intervals/rate-boundary.json"
    ))
    .unwrap();
    envelope["request"]["policy"]["perspective"] = json!("health_system");
    envelope["request"]["quotes"][0]["amount"] = json!("0.01");
    envelope["request"]["quotes"][1]["amount"] = json!("0.01");
    envelope["intervals"][0]["end"] = json!("2026-02-02");
    for model in input["models"].as_array_mut().unwrap() {
        model["method"] = json!("intervals");
        model["request"] = envelope.clone();
        model["bindings"] = json!([]);
    }
    let result = output(&input);
    for row in result["rows"].as_array().unwrap() {
        assert_eq!(
            row["cost_report"]["method_version"],
            "dapane-intervals-v0.1.0"
        );
        assert_eq!(
            row["cost_report"]["report"]["totals"]["exact"],
            rational("1", "100")
        );
        assert_eq!(row["cost_report"]["report"]["totals"]["rounded"], "0.00");
    }
}

#[test]
fn prepared_requests_replay_to_identical_native_reports() {
    let result = output(&fixture());
    for row in result["rows"].as_array().unwrap() {
        let replay: Value = serde_json::from_str(
            &dapane_core::evaluate_json(&row["prepared_request"].to_string()).unwrap(),
        )
        .unwrap();
        assert_eq!(replay, row["cost_report"]);
    }
}

#[test]
fn capacity_contract_and_unknown_values_survive_the_adapter() {
    let mut input = fixture();
    let mut request: Value = serde_json::from_str(include_str!(
        "../../../fixtures/genomics-capacity/time-unknown-capacity.json"
    ))
    .unwrap();
    request["policy"]["perspective"] = json!("health_system");
    input["money"] = json!({
        "currency": request["policy"]["currency"],
        "price_year": request["policy"]["price_year"],
        "basis": request["policy"]["basis"],
        "rounding": request["policy"]["rounding"],
    });
    for model in input["models"].as_array_mut().unwrap() {
        model["request"] = request.clone();
        model["bindings"] = json!([]);
    }
    let expected: Value =
        serde_json::from_str(&dapane_core::evaluate_json(&request.to_string()).unwrap()).unwrap();
    for row in output(&input)["rows"].as_array().unwrap() {
        assert_eq!(row["cost_report"], expected);
        assert_eq!(
            row["cost_report"]["capacity_allocations"][0]["available_capacity"]["status"],
            "unknown",
        );
    }
}

#[test]
fn output_digest_is_independently_reconstructible() {
    use sha2::{Digest, Sha256};
    let mut result = output(&fixture());
    let stored = result
        .as_object_mut()
        .unwrap()
        .remove("output_digest")
        .unwrap();
    let mut hash = Sha256::new();
    hash.update(b"dapane:paired-output:0.1\n");
    hash.update(serde_json::to_vec(&result).unwrap());
    let hex: String = hash.finalize().iter().map(|b| format!("{b:02x}")).collect();
    assert_eq!(stored, format!("sha256:{hex}"));
}
