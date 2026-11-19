//! Independent exact fiscal accounting references; every amount and rate is invented.

use dapane_decision_fiscal::fiscal::{
    SCHEDULE_SCHEMA_VERSION, evaluate_equity_json, evaluate_fiscal_json, export_perspective_table,
};
use serde_json::{Value, json};

fn r(n: &str, d: &str) -> Value {
    json!({"numerator": n, "denominator": d})
}

fn fixture() -> Value {
    serde_json::from_str(include_str!("../fixtures/fiscal-nz-synthetic.json")).unwrap()
}

fn result(input: &Value) -> Value {
    serde_json::from_str(&evaluate_fiscal_json(&input.to_string()).unwrap()).unwrap()
}

fn set_view(input: &mut Value, perspective: &str, rule: &str) {
    input["perspective"] = json!(perspective);
    input["key"]["perspective"] = json!(perspective);
    input["aggregation_rule"] = json!(rule);
    // These invented references assume equal economic and budgetary amounts.
    // The runtime supplies no conversion by merely changing a perspective label.
    let basis = if perspective == "societal" {
        "economic_cost"
    } else {
        "public_expenditure"
    };
    input["resource_basis"] = json!(basis);
    for line in input["lines"].as_array_mut().unwrap() {
        if line["kind"] != "discounted_tax_transfer" {
            line["basis"] = json!(basis);
        }
    }
    if perspective == "public_finance" {
        input["health"] = Value::Null;
    }
}

fn set_australia(input: &mut Value) {
    input["jurisdiction"] = json!("AU");
    input["currency"] = json!("AUD");
    input["key"]["scenario_id"] = json!("synthetic-AU");
    input["key"]["subgroup_id"] = json!("First Nations / SEIFA-1");
    for line in input["lines"].as_array_mut().unwrap() {
        line["undiscounted_amount"]["currency"] = json!("AUD");
    }
    if !input["health"].is_null() {
        input["health"]["threshold"]["currency"] = json!("AUD");
    }
}

#[test]
fn nz_differential_discounting_and_perspectives_have_independent_exact_answers() {
    // Resources (100+20) and transfers (40+10) use 4/5; health uses 1.
    // Medical=80, enforcement=16, receipts=40, payer=-40; internal net=0.
    let input = fixture();
    let report = result(&input);
    assert_eq!(
        report["resources"]["health_system_direct_cost"],
        r("80", "1")
    );
    assert_eq!(
        report["resources"]["enforcement_resource_cost"],
        r("16", "1")
    );
    assert_eq!(report["tax_transfers"]["government_receipts"], r("40", "1"));
    assert_eq!(report["tax_transfers"]["payer_outflows"], r("-40", "1"));
    assert_eq!(report["tax_transfers"]["net_within_boundary"], r("0", "1"));
    assert_eq!(report["selected_resource_cost"], r("80", "1"));
    assert_eq!(report["net_monetary_benefit"], r("20", "1"));
    assert_eq!(report["net_public_outlay"], Value::Null);
    assert_eq!(
        report["excluded_line_ids"],
        json!(["enforcement", "excise", "gst"])
    );

    let mut societal = input.clone();
    set_view(&mut societal, "societal", "societal_net_domestic_transfers");
    let report = result(&societal);
    assert_eq!(report["selected_resource_cost"], r("96", "1"));
    assert_eq!(report["net_monetary_benefit"], r("4", "1"));
    assert_eq!(report["net_public_outlay"], Value::Null);

    let mut fiscal = input;
    set_view(&mut fiscal, "public_finance", "public_finance_net_outlay");
    let report = result(&fiscal);
    assert_eq!(report["net_public_outlay"], r("56", "1"));
    assert_eq!(report["net_monetary_benefit"], Value::Null);
}

#[test]
fn au_uniform_discounting_keeps_tax_and_health_resource_totals_distinct() {
    let mut input = fixture();
    set_australia(&mut input);
    input["discount"]["health_rate"] = r("1", "4");
    let health = result(&input);
    assert_eq!(health["discounted_qalys"], r("4", "5"));
    assert_eq!(health["net_monetary_benefit"], r("0", "1"));
    assert_eq!(health["currency"], "AUD");
    set_view(&mut input, "societal", "societal_net_domestic_transfers");
    assert_eq!(result(&input)["net_monetary_benefit"], r("-16", "1"));
}

#[test]
fn annual_and_half_year_steps_agree_at_the_same_explicit_effective_rate() {
    // (4/5)^2=16/25; equivalent annual effective rate is 9/16, not 1/4.
    let mut half_year = fixture();
    half_year["discount"]["step_years"] = r("1", "2");
    for line in half_year["lines"].as_array_mut().unwrap() {
        line["time_step"] = json!(2);
    }
    half_year["health"]["flows"][0]["time_step"] = json!(2);
    let mut annual = fixture();
    annual["discount"]["resource_rate"] = r("9", "16");
    annual["discount"]["transfer_rate"] = r("9", "16");
    let a = result(&annual);
    let h = result(&half_year);
    assert_eq!(h["resources"], a["resources"]);
    assert_eq!(h["tax_transfers"], a["tax_transfers"]);
    assert_eq!(h["resources"]["health_system_direct_cost"], r("64", "1"));
    assert_eq!(h["net_monetary_benefit"], r("36", "1"));
    for line in h["valued_lines"].as_array().unwrap() {
        assert_eq!(line["valuation_time_years"], r("1", "1"));
        assert_eq!(line["discount_factor"], r("16", "25"));
    }
}

#[test]
fn each_flow_uses_its_own_time_and_explicit_zero_is_not_missing() {
    let mut input = fixture();
    input["lines"][0]["time_step"] = json!(0);
    input["lines"][1]["time_step"] = json!(2);
    input["lines"][2]["undiscounted_amount"]["amount"] = r("0", "1");
    let result = result(&input);
    assert_eq!(
        result["resources"]["health_system_direct_cost"],
        r("100", "1")
    );
    assert_eq!(
        result["resources"]["enforcement_resource_cost"],
        r("64", "5")
    );
    assert_eq!(result["tax_transfers"]["government_receipts"], r("8", "1"));
    assert_eq!(result["net_monetary_benefit"], r("0", "1"));
}

#[test]
fn transfer_changes_do_not_change_societal_or_health_nmb() {
    for (perspective, rule) in [
        ("health_system", "health_system_direct_only"),
        ("societal", "societal_net_domestic_transfers"),
    ] {
        let mut input = fixture();
        set_view(&mut input, perspective, rule);
        let expected = result(&input)["net_monetary_benefit"].clone();
        for amount in ["-1000", "0", "1000"] {
            input["lines"][2]["undiscounted_amount"]["amount"] = r(amount, "1");
            let actual = result(&input);
            assert_eq!(actual["net_monetary_benefit"], expected);
            assert_eq!(actual["tax_transfers"]["net_within_boundary"], r("0", "1"));
        }
    }
}

#[test]
fn reduced_tax_receipts_raise_public_outlay_with_the_correct_sign() {
    let mut input = fixture();
    set_view(&mut input, "public_finance", "public_finance_net_outlay");
    input["lines"][2]["undiscounted_amount"]["amount"] = r("-40", "1");
    input["lines"][3]["undiscounted_amount"]["amount"] = r("-10", "1");
    let report = result(&input);
    assert_eq!(
        report["tax_transfers"]["government_receipts"],
        r("-40", "1")
    );
    assert_eq!(report["tax_transfers"]["payer_outflows"], r("40", "1"));
    assert_eq!(report["net_public_outlay"], r("136", "1"));
}

#[test]
fn invalid_perspective_rule_combinations_fail_closed() {
    for (view, wrong_rule) in [
        ("health_system", "public_finance_net_outlay"),
        ("public_finance", "societal_net_domestic_transfers"),
        ("societal", "health_system_direct_only"),
    ] {
        let mut input = fixture();
        set_view(&mut input, view, wrong_rule);
        assert_eq!(
            evaluate_fiscal_json(&input.to_string()).unwrap_err().code,
            "perspective_rule"
        );
    }
    let mut input = fixture();
    input["key"]["perspective"] = json!("societal");
    assert_eq!(
        evaluate_fiscal_json(&input.to_string()).unwrap_err().code,
        "perspective_key"
    );
}

#[test]
fn accounting_kind_cannot_silently_relabel_a_transfer_as_a_cost() {
    for mode in [
        "kind",
        "missing_transfer",
        "source_perspective",
        "unlabelled_addition",
    ] {
        let mut input = fixture();
        match mode {
            "kind" => input["lines"][2]["kind"] = json!("health_system_direct_cost"),
            "missing_transfer" => input["lines"][2]["transfer"] = Value::Null,
            "source_perspective" => input["lines"][2]["perspective"] = json!("health_system"),
            _ => input["add_tax_to_societal_cost"] = json!(true),
        }
        assert!(evaluate_fiscal_json(&input.to_string()).is_err(), "{mode}");
    }
}

#[test]
fn currency_price_year_units_and_jurisdiction_are_mandatory_and_consistent() {
    for field in ["currency", "price_year", "unit"] {
        let mut input = fixture();
        input["lines"][0]["undiscounted_amount"]
            .as_object_mut()
            .unwrap()
            .remove(field);
        assert!(
            evaluate_fiscal_json(&input.to_string()).is_err(),
            "missing {field}"
        );
    }
    for (path, wrong) in [
        ("/lines/0/undiscounted_amount/currency", json!("AUD")),
        ("/lines/0/undiscounted_amount/price_year", json!(2025)),
        (
            "/lines/0/undiscounted_amount/unit",
            json!("currency_per_qaly"),
        ),
        ("/health/threshold/currency", json!("AUD")),
        ("/health/threshold/unit", json!("currency")),
        ("/price_year", json!(0)),
        ("/jurisdiction", json!("AU")),
    ] {
        let mut input = fixture();
        *input.pointer_mut(path).unwrap() = wrong;
        assert!(evaluate_fiscal_json(&input.to_string()).is_err(), "{path}");
    }
}

#[test]
fn duplicate_flows_and_unknown_accounts_are_rejected() {
    let mut input = fixture();
    let line = input["lines"][0].clone();
    input["lines"].as_array_mut().unwrap().push(line);
    assert_eq!(
        evaluate_fiscal_json(&input.to_string()).unwrap_err().code,
        "duplicate_identity"
    );
    for (path, wrong) in [
        ("/lines/2/transfer/boundary", "cross_border"),
        ("/lines/2/transfer/payer", "unknown"),
        ("/lines/2/transfer/tax", "unlabelled_tax"),
        ("/lines/0/kind", "funding"),
    ] {
        let mut input = fixture();
        *input.pointer_mut(path).unwrap() = json!(wrong);
        assert!(evaluate_fiscal_json(&input.to_string()).is_err(), "{path}");
    }
}

#[test]
fn signed_costs_and_health_changes_remain_exact() {
    let mut input = fixture();
    input["lines"][0]["undiscounted_amount"]["amount"] = r("-100", "1");
    input["health"]["flows"][0]["value"] = r("-1", "2");
    // -50 health - (-80 costs) = +30 NMB.
    assert_eq!(result(&input)["net_monetary_benefit"], r("30", "1"));
    input["health"]["threshold"]["amount"] = r("-100", "1");
    assert_eq!(
        evaluate_fiscal_json(&input.to_string()).unwrap_err().code,
        "negative_threshold"
    );
}

#[test]
fn health_inputs_are_required_only_for_explicit_health_valuation_views() {
    let mut input = fixture();
    input["health"] = Value::Null;
    assert_eq!(
        evaluate_fiscal_json(&input.to_string()).unwrap_err().code,
        "health_contract"
    );
    let mut input = fixture();
    input["perspective"] = json!("public_finance");
    input["key"]["perspective"] = json!("public_finance");
    input["aggregation_rule"] = json!("public_finance_net_outlay");
    assert_eq!(
        evaluate_fiscal_json(&input.to_string()).unwrap_err().code,
        "health_contract"
    );
}

#[test]
fn order_and_unicode_subgroup_identity_are_preserved_without_pooling() {
    let input = fixture();
    let mut reversed = input.clone();
    reversed["lines"].as_array_mut().unwrap().reverse();
    assert_eq!(
        evaluate_fiscal_json(&input.to_string()).unwrap(),
        evaluate_fiscal_json(&reversed.to_string()).unwrap(),
    );
    assert_eq!(result(&input)["key"], input["key"]);
    let mut changed = input.clone();
    changed["key"]["subgroup_id"] = json!("non-Māori / NZDep-1");
    assert_ne!(
        result(&input)["input_digest"],
        result(&changed)["input_digest"]
    );
    assert_eq!(
        result(&changed)["key"]["subgroup_id"],
        "non-Māori / NZDep-1"
    );
}

#[test]
fn unsupported_discounting_and_precision_fail_closed() {
    for (path, bad) in [
        ("/discount/method", json!("continuous_provider_method")),
        ("/discount/resource_rate", r("-1", "10")),
        ("/discount/health_rate", r("2", "1")),
        ("/discount/transfer_rate", r("1", "0")),
        ("/discount/step_years", r("0", "1")),
        ("/lines/0/time_step", json!(1201)),
        (
            "/lines/0/undiscounted_amount/amount",
            r(&"9".repeat(97), "1"),
        ),
    ] {
        let mut input = fixture();
        *input.pointer_mut(path).unwrap() = bad;
        assert!(evaluate_fiscal_json(&input.to_string()).is_err(), "{path}");
    }
    let mut input = fixture();
    input["discount"]["resource_rate"] = r("1", &"9".repeat(96));
    input["lines"][0]["time_step"] = json!(1200);
    assert_eq!(
        evaluate_fiscal_json(&input.to_string()).unwrap_err().code,
        "precision_limit"
    );
}

#[test]
fn synthetic_evidence_and_explicit_comparator_are_required() {
    for (path, wrong) in [
        ("/lines/0/source/evidence", json!("observed")),
        ("/health/model/content_digest", json!("unknown")),
        ("/comparator_strategy_id", json!("alternative")),
        ("/key/replication_id", json!("")),
        ("/draw_set_digest", json!("")),
    ] {
        let mut input = fixture();
        *input.pointer_mut(path).unwrap() = wrong;
        assert!(evaluate_fiscal_json(&input.to_string()).is_err(), "{path}");
    }
}

#[test]
fn duplicate_keys_unlabelled_float_and_oversized_inputs_are_rejected() {
    let wire = fixture().to_string();
    let duplicate = wire.replacen(
        "\"price_year\":2026",
        "\"price_year\":2026,\"price_year\":2025",
        1,
    );
    assert_eq!(
        evaluate_fiscal_json(&duplicate).unwrap_err().code,
        "invalid_json"
    );
    let mut input = fixture();
    input["lines"][0]["undiscounted_amount"]["amount"] = json!(100.0);
    assert!(evaluate_fiscal_json(&input.to_string()).is_err());
    assert_eq!(
        evaluate_fiscal_json(&" ".repeat(4 * 1024 * 1024 + 1))
            .unwrap_err()
            .code,
        "input_limit",
    );
}

#[test]
fn output_digest_and_input_snapshot_support_independent_replay() {
    use sha2::{Digest, Sha256};
    let report = result(&fixture());
    assert_eq!(result(&report["input_snapshot"]), report);
    let mut unsigned = report.clone();
    let declared = unsigned
        .as_object_mut()
        .unwrap()
        .remove("output_digest")
        .unwrap();
    let mut hash = Sha256::new();
    hash.update(b"dapane:fiscal-output:0.1\n");
    hash.update(serde_json::to_vec(&unsigned).unwrap());
    let hex: String = hash.finalize().iter().map(|b| format!("{b:02x}")).collect();
    assert_eq!(declared, format!("sha256:{hex}"));
}

#[test]
fn resource_values_do_not_silently_become_budgetary_outlays() {
    let mut input = fixture();
    set_view(&mut input, "public_finance", "public_finance_net_outlay");
    input["resource_basis"] = json!("economic_cost");
    assert_eq!(
        evaluate_fiscal_json(&input.to_string()).unwrap_err().code,
        "resource_basis"
    );
    let mut input = fixture();
    set_view(&mut input, "societal", "societal_net_domestic_transfers");
    input["resource_basis"] = json!("public_expenditure");
    assert_eq!(
        evaluate_fiscal_json(&input.to_string()).unwrap_err().code,
        "resource_basis"
    );
    let mut input = fixture();
    input["lines"][0]["basis"] = json!("economic_cost");
    assert_eq!(
        evaluate_fiscal_json(&input.to_string()).unwrap_err().code,
        "accounting_kind"
    );
    input["lines"][0]["basis"] = json!("funding");
    assert!(evaluate_fiscal_json(&input.to_string()).is_err());
}

#[test]
fn absent_accounting_categories_do_not_become_zero() {
    for removed in ["medical", "enforcement", "excise", "gst"] {
        let mut input = fixture();
        input["lines"]
            .as_array_mut()
            .unwrap()
            .retain(|line| line["id"] != removed);
        assert_eq!(
            evaluate_fiscal_json(&input.to_string()).unwrap_err().code,
            "incomplete_ledger",
            "{removed}",
        );
    }
    let mut input = fixture();
    for line in input["lines"].as_array_mut().unwrap() {
        line["undiscounted_amount"]["amount"] = r("0", "1");
    }
    assert_eq!(result(&input)["net_monetary_benefit"], r("100", "1"));
}

#[test]
fn fiscal_v01_fixture_retains_its_wire_identity() {
    // Digests produced by the fiscal 0.1 evaluator at 5c035f6.
    let mut input = fixture();
    let report = result(&input);
    assert_eq!(
        report["input_digest"],
        "sha256:528f554e98f2cde96331f4710b7179eb37e00d5024a972693eb2830d8dd88751"
    );
    assert_eq!(
        report["output_digest"],
        "sha256:de7f7fffcbc683655249d3a488af6e24fef6d1a36a995ce161259c72bc709628"
    );
    assert!(report.get("valued_cohort_states").is_none());
    assert!(report.get("valued_cessation_resources").is_none());
    input["cohort_states"] = json!([]);
    let error = evaluate_fiscal_json(&input.to_string()).unwrap_err();
    assert_eq!(error.code, "invalid_request");
    assert_eq!(error.path, "/cohort_states");
}

fn schedule_fixture() -> Value {
    let mut input = fixture();
    input["schema_version"] = json!(SCHEDULE_SCHEMA_VERSION);
    input
}

#[test]
fn cohort_state_occupancy_entries_are_evaluated_with_draw_identity_preserved() {
    let mut input = schedule_fixture();
    input["cohort_states"] = json!([
        {
            "id": "smoker_to_quit",
            "time_step": 1,
            "from_state": "smoker",
            "to_state": "quit",
            "population_count": {"numerator": "100", "denominator": "1"},
            "perspective": "health_system",
            "basis": "economic_cost",
            "undiscounted_amount": {
                "amount": {"numerator": "500", "denominator": "1"},
                "currency": "NZD",
                "price_year": 2026,
                "unit": "currency"
            },
            "source": {
                "id": "invented-cohort-data",
                "version": "1",
                "evidence": "synthetic",
                "content_digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000"
            }
        }
    ]);
    input["cessation_resources"] = json!([]);
    let report = result(&input);
    let row = &report["valued_cohort_states"][0];
    assert_eq!(row["id"], "smoker_to_quit");
    assert_eq!(row["from_state"], "smoker");
    assert_eq!(row["to_state"], "quit");
    assert_eq!(row["population_count"], r("100", "1"));
    // 500 * 1/(1+1/4) = 400. The schedule is reported separately from the ledger.
    assert_eq!(row["discounted_amount"], r("400", "1"));
    assert_eq!(row["draw_id"], "draw-a");
    assert_eq!(row["strategy_id"], "alternative");
    assert_eq!(row["subgroup_id"], "Māori / NZDep-1");
    assert_eq!(row["perspective"], "health_system");
    assert_eq!(report["key"]["strategy_id"], "alternative");
    assert_eq!(report["key"]["perspective"], "health_system");
    assert_eq!(report["key"]["subgroup_id"], "Māori / NZDep-1");
    // Discounted amount: 500 * (4/5)^1 = 400
    assert_eq!(
        report["valued_cohort_states"][0]["time_step_years"]["numerator"],
        "1"
    );
    assert_eq!(
        report["valued_cohort_states"][0]["time_step_years"]["denominator"],
        "1"
    );
    // Draw identity preserved
    assert_eq!(report["key"]["draw_id"], "draw-a");
    assert_eq!(report["key"], input["key"]);
    assert_eq!(result(&report["input_snapshot"]), report);
}

#[test]
fn cessation_resource_entries_are_evaluated_with_draw_identity_preserved() {
    let mut input = schedule_fixture();
    input["cohort_states"] = json!([]);
    input["cessation_resources"] = json!([
        {
            "id": "cessation_counseling",
            "time_step": 1,
            "resource_type": "counseling",
            "quantity": {"numerator": "5", "denominator": "1"},
            "perspective": "public_finance",
            "basis": "public_expenditure",
            "undiscounted_amount": {
                "amount": {"numerator": "250", "denominator": "1"},
                "currency": "NZD",
                "price_year": 2026,
                "unit": "currency"
            },
            "source": {
                "id": "invented-cessation-data",
                "version": "1",
                "evidence": "synthetic",
                "content_digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000"
            }
        }
    ]);
    let report = result(&input);
    let row = &report["valued_cessation_resources"][0];
    assert_eq!(row["id"], "cessation_counseling");
    assert_eq!(row["resource_type"], "counseling");
    assert_eq!(row["quantity"], r("5", "1"));
    assert_eq!(row["perspective"], "public_finance");
    assert_eq!(row["draw_id"], "draw-a");
    assert_eq!(row["strategy_id"], "alternative");
    assert_eq!(row["subgroup_id"], "Māori / NZDep-1");
    // The packet key stays the valuation perspective; the row keeps its own tag.
    assert_eq!(report["key"]["perspective"], "health_system");
    assert_eq!(report["key"]["draw_id"], "draw-a");
    assert_eq!(report["key"]["strategy_id"], "alternative");
    assert_eq!(report["key"]["subgroup_id"], "Māori / NZDep-1");
    // 250 * 1/(1+1/4) = 200.
    assert_eq!(row["discounted_amount"], r("200", "1"));
    assert_eq!(
        report["resources"]["health_system_direct_cost"],
        r("80", "1")
    );
}

#[test]
fn cohort_state_entries_must_have_unique_ids() {
    let mut input = schedule_fixture();
    input["cohort_states"] = json!([
        {
            "id": "smoker_to_quit",
            "time_step": 1,
            "from_state": "smoker",
            "to_state": "quit",
            "population_count": {"numerator": "100", "denominator": "1"},
            "perspective": "health_system",
            "basis": "economic_cost",
            "undiscounted_amount": {
                "amount": {"numerator": "500", "denominator": "1"},
                "currency": "NZD",
                "price_year": 2026,
                "unit": "currency"
            },
            "source": {
                "id": "invented-cohort-data",
                "version": "1",
                "evidence": "synthetic",
                "content_digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000"
            }
        },
        {
            "id": "smoker_to_quit",
            "time_step": 2,
            "from_state": "smoker",
            "to_state": "quit",
            "population_count": {"numerator": "50", "denominator": "1"},
            "perspective": "health_system",
            "basis": "economic_cost",
            "undiscounted_amount": {
                "amount": {"numerator": "250", "denominator": "1"},
                "currency": "NZD",
                "price_year": 2026,
                "unit": "currency"
            },
            "source": {
                "id": "invented-cohort-data",
                "version": "1",
                "evidence": "synthetic",
                "content_digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000"
            }
        }
    ]);
    input["cessation_resources"] = json!([]);
    assert_eq!(
        evaluate_fiscal_json(&input.to_string()).unwrap_err().code,
        "duplicate_identity"
    );
}

#[test]
fn cohort_state_entries_validate_entry_and_exit_states() {
    // from_state must be a valid state, to_state must be a valid state
    let mut input = schedule_fixture();
    input["cohort_states"] = json!([
        {
            "id": "smoker_to_quit",
            "time_step": 1,
            "from_state": "",
            "to_state": "quit",
            "population_count": {"numerator": "100", "denominator": "1"},
            "perspective": "health_system",
            "basis": "economic_cost",
            "undiscounted_amount": {
                "amount": {"numerator": "500", "denominator": "1"},
                "currency": "NZD",
                "price_year": 2026,
                "unit": "currency"
            },
            "source": {
                "id": "invented-cohort-data",
                "version": "1",
                "evidence": "synthetic",
                "content_digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000"
            }
        }
    ]);
    input["cessation_resources"] = json!([]);
    assert_eq!(
        evaluate_fiscal_json(&input.to_string()).unwrap_err().code,
        "invalid_identity"
    );
}

#[test]
fn cessation_resource_entries_validate_resource_type() {
    let mut input = schedule_fixture();
    input["cohort_states"] = json!([]);
    input["cessation_resources"] = json!([
        {
            "id": "cessation_counseling",
            "time_step": 1,
            "resource_type": "",
            "quantity": {"numerator": "5", "denominator": "1"},
            "perspective": "public_finance",
            "basis": "public_expenditure",
            "undiscounted_amount": {
                "amount": {"numerator": "250", "denominator": "1"},
                "currency": "NZD",
                "price_year": 2026,
                "unit": "currency"
            },
            "source": {
                "id": "invented-cessation-data",
                "version": "1",
                "evidence": "synthetic",
                "content_digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000"
            }
        }
    ]);
    assert_eq!(
        evaluate_fiscal_json(&input.to_string()).unwrap_err().code,
        "invalid_identity"
    );
    input["cessation_resources"][0]["resource_type"] = json!("counseling");
    input["cessation_resources"][0]["basis"] = json!("fiscal_transfer");
    let error = evaluate_fiscal_json(&input.to_string()).unwrap_err();
    assert_eq!(error.code, "resource_basis");
    assert_eq!(error.path, "/cessation_resources/0/basis");
}

fn equity_input(weights: &[(&str, Value)]) -> Value {
    let packets: Vec<_> = weights
        .iter()
        .map(|(weight, fiscal)| {
            json!({
                "weight": r(weight, "1"),
                "fiscal": fiscal,
            })
        })
        .collect();
    json!({
        "schema_version": "dapane-fiscal-equity/0.1",
        "packets": packets,
    })
}

fn equity_report(weights: &[(&str, Value)]) -> Value {
    let input = equity_input(weights);
    serde_json::from_str(&evaluate_equity_json(&input.to_string()).unwrap()).unwrap()
}

#[test]
fn unity_equity_weights_conserve_the_unweighted_subgroup_sum() {
    // Each invented packet has cost 80, one undiscounted QALY and NMB 100*1-80=20.
    let maori = fixture();
    let mut other = fixture();
    other["key"]["subgroup_id"] = json!("non-Māori / NZDep-1");
    let report = equity_report(&[("1", maori), ("1", other)]);
    assert_eq!(report["subgroups"][0]["subgroup_id"], "Māori / NZDep-1");
    assert_eq!(report["subgroups"][1]["subgroup_id"], "non-Māori / NZDep-1");
    assert_eq!(
        report["unweighted_sum"]["selected_resource_cost"],
        r("160", "1")
    );
    assert_eq!(
        report["weighted_sum"]["selected_resource_cost"],
        r("160", "1")
    );
    assert_eq!(report["unweighted_sum"]["discounted_qalys"], r("2", "1"));
    assert_eq!(report["weighted_sum"]["discounted_qalys"], r("2", "1"));
    assert_eq!(
        report["unweighted_sum"]["net_monetary_benefit"],
        r("40", "1")
    );
    assert_eq!(report["weighted_sum"]["net_monetary_benefit"], r("40", "1"));
    assert_eq!(report["subgroups"][0]["draw_id"], "draw-a");
    assert_eq!(report["subgroups"][1]["strategy_id"], "alternative");
}

#[test]
fn non_unit_equity_weights_scale_each_subgroup_before_summing() {
    let maori = schedule_fixture();
    let mut other = schedule_fixture();
    other["key"]["subgroup_id"] = json!("non-Māori / NZDep-1");
    other["lines"][0]["undiscounted_amount"]["amount"] = r("50", "1");
    other["health"]["flows"][0]["value"] = r("2", "1");
    let other_digest = result(&other)["output_digest"].clone();
    let report = equity_report(&[("1", maori), ("3", other)]);
    // Subgroup values are (80, 1, 20) and (40, 2, 160) for cost, QALYs and NMB.
    assert_eq!(
        report["unweighted_sum"]["selected_resource_cost"],
        r("120", "1")
    );
    assert_eq!(report["unweighted_sum"]["discounted_qalys"], r("3", "1"));
    assert_eq!(
        report["unweighted_sum"]["net_monetary_benefit"],
        r("180", "1")
    );
    assert_eq!(
        report["weighted_sum"]["selected_resource_cost"],
        r("200", "1")
    );
    assert_eq!(report["weighted_sum"]["discounted_qalys"], r("7", "1"));
    assert_eq!(
        report["weighted_sum"]["net_monetary_benefit"],
        r("500", "1")
    );
    assert_eq!(report["subgroups"][1]["fiscal_output_digest"], other_digest);
}

#[test]
fn equity_aggregation_rejects_a_repeated_subgroup_or_a_different_draw() {
    let packet = fixture();
    let mut repeated = fixture();
    repeated["run_id"] = json!("synthetic-nz-repeated-subgroup");
    let input = json!({
        "schema_version": "dapane-fiscal-equity/0.1",
        "packets": [
            {"weight": r("1", "1"), "fiscal": packet},
            {"weight": r("1", "1"), "fiscal": repeated},
        ],
    });
    assert_eq!(
        evaluate_equity_json(&input.to_string()).unwrap_err().code,
        "duplicate_identity"
    );

    let mut other_draw = fixture();
    other_draw["key"]["subgroup_id"] = json!("non-Māori / NZDep-1");
    other_draw["key"]["draw_id"] = json!("draw-b");
    let input = json!({
        "schema_version": "dapane-fiscal-equity/0.1",
        "packets": [
            {"weight": r("1", "1"), "fiscal": fixture()},
            {"weight": r("1", "1"), "fiscal": other_draw},
        ],
    });
    assert_eq!(
        evaluate_equity_json(&input.to_string()).unwrap_err().code,
        "subgroup_axis"
    );
}

#[test]
fn equity_weights_must_be_strictly_positive() {
    let input = json!({
        "schema_version": "dapane-fiscal-equity/0.1",
        "packets": [{"weight": r("0", "1"), "fiscal": fixture()}],
    });
    assert_eq!(
        evaluate_equity_json(&input.to_string()).unwrap_err().code,
        "invalid_weight"
    );
}

#[test]
fn equity_aggregation_rejects_incompatible_valuation_contexts() {
    let baseline = fixture();
    let mut economic = baseline.clone();
    economic["resource_basis"] = json!("economic_cost");
    for line in &mut economic["lines"].as_array_mut().unwrap()[..2] {
        line["basis"] = json!("economic_cost");
    }
    let mut cases = vec![("resource basis", economic)];
    for (pointer, value) in [
        ("/comparator_strategy_id", json!("different-comparator")),
        (
            "/draw_set_digest",
            json!(format!("sha256:{}", "7".repeat(64))),
        ),
        ("/discount/resource_rate", r("0", "1")),
        ("/health/threshold/amount", r("101", "1")),
        ("/schema_version", json!(SCHEDULE_SCHEMA_VERSION)),
    ] {
        let mut changed = baseline.clone();
        *changed.pointer_mut(pointer).unwrap() = value;
        cases.push((pointer, changed));
    }
    for (field, mut changed) in cases {
        changed["key"]["subgroup_id"] = json!("non-Māori / NZDep-1");
        result(&changed); // Each alternative must be valid when evaluated on its own.
        let input = equity_input(&[("1", baseline.clone()), ("1", changed)]);
        assert_eq!(
            evaluate_equity_json(&input.to_string()).unwrap_err().code,
            "subgroup_axis",
            "{field}"
        );
    }
}

#[test]
fn equity_sums_retain_the_fiscal_precision_bound() {
    let mut packet = fixture();
    set_view(&mut packet, "public_finance", "public_finance_net_outlay");
    packet["discount"]["resource_rate"] = r("1", "1");
    packet["lines"][0]["time_step"] = json!(400);
    packet["lines"][0]["undiscounted_amount"]["amount"] = r("1", "1");
    packet["lines"][1]["undiscounted_amount"]["amount"] = r("0", "1");
    let mut other = packet.clone();
    other["key"]["subgroup_id"] = json!("non-Māori / NZDep-1");
    let report = equity_report(&[("1", packet), ("1", other)]);
    // Two costs of 2^-400 sum exactly to 2^-399, beyond the input digit limit.
    let denominator = num_bigint::BigInt::from(2u8).pow(399).to_string();
    assert_eq!(
        report["unweighted_sum"]["selected_resource_cost"],
        r("1", &denominator)
    );
    assert_eq!(report["weighted_sum"], report["unweighted_sum"]);
    assert_eq!(report["weighted_sum"]["discounted_qalys"], Value::Null);
    assert_eq!(report["weighted_sum"]["net_monetary_benefit"], Value::Null);
}

#[test]
fn perspective_table_keeps_the_joint_draw_key() {
    let fiscal = evaluate_fiscal_json(&fixture().to_string()).unwrap();
    let table: Value = serde_json::from_str(&export_perspective_table(&fiscal).unwrap()).unwrap();
    let row = &table["rows"][0];
    assert_eq!(row["scenario_id"], "synthetic-NZ");
    assert_eq!(row["strategy_id"], "alternative");
    assert_eq!(row["draw_id"], "draw-a");
    assert_eq!(row["replication_id"], "rep-a");
    assert_eq!(row["perspective"], "health_system");
    assert_eq!(row["subgroup_id"], "Māori / NZDep-1");
    assert_eq!(row["selected_resource_cost"], r("80", "1"));
    assert_eq!(row["net_monetary_benefit"], r("20", "1"));

    let mut other = fixture();
    other["key"]["subgroup_id"] = json!("non-Māori / NZDep-1");
    let equity =
        evaluate_equity_json(&equity_input(&[("1", fixture()), ("1", other)]).to_string()).unwrap();
    let table: Value = serde_json::from_str(&export_perspective_table(&equity).unwrap()).unwrap();
    assert_eq!(table["rows"].as_array().unwrap().len(), 2);
    assert_eq!(table["rows"][0]["draw_id"], "draw-a");
    assert_eq!(table["rows"][1]["draw_id"], "draw-a");
    assert_eq!(table["rows"][0]["replication_id"], "rep-a");
    assert_eq!(table["rows"][1]["scenario_id"], "synthetic-NZ");
    assert_ne!(
        table["rows"][0]["subgroup_id"],
        table["rows"][1]["subgroup_id"]
    );
    assert_eq!(
        export_perspective_table("{}").unwrap_err().code,
        "unsupported_schema"
    );
}

#[test]
fn tobac_published_transfer_identity_matches_exact_steps() {
    // Tobac 891f79e health.discounted_resource_cost((100, -55), (0, 1), 0.10) is 50.
    // discounted_tax_transfer((66, 22), (0, 1), 0.10) is (86, -86). The resource
    // total remains after the transfer pair cancels. Equity scoring is a different
    // contract and is not compared here.
    let mut input = fixture();
    input["discount"]["resource_rate"] = r("1", "10");
    input["discount"]["transfer_rate"] = r("1", "10");
    input["lines"][0]["time_step"] = json!(0);
    input["lines"][1]["time_step"] = json!(0);
    input["lines"][1]["undiscounted_amount"]["amount"] = r("0", "1");
    input["lines"][2]["time_step"] = json!(0);
    input["lines"][2]["undiscounted_amount"]["amount"] = r("66", "1");
    input["lines"][3]["undiscounted_amount"]["amount"] = r("22", "1");
    let mut later = input["lines"][0].clone();
    later["id"] = json!("later-medical");
    later["time_step"] = json!(1);
    later["undiscounted_amount"]["amount"] = r("-55", "1");
    input["lines"].as_array_mut().unwrap().push(later);

    let report = result(&input);
    assert_eq!(
        report["resources"]["health_system_direct_cost"],
        r("50", "1")
    );
    assert_eq!(
        report["resources"]["enforcement_resource_cost"],
        r("0", "1")
    );
    assert_eq!(report["tax_transfers"]["government_receipts"], r("86", "1"));
    assert_eq!(report["tax_transfers"]["payer_outflows"], r("-86", "1"));
    assert_eq!(report["tax_transfers"]["net_within_boundary"], r("0", "1"));
    assert_eq!(report["selected_resource_cost"], r("50", "1"));

    set_view(&mut input, "societal", "societal_net_domestic_transfers");
    let report = result(&input);
    assert_eq!(report["selected_resource_cost"], r("50", "1"));
    assert_eq!(report["net_monetary_benefit"], r("50", "1"));
}
