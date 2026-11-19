//! T1 independent exact accounting references; every amount and rate is invented.

use dapane_decision_fiscal::fiscal::evaluate_fiscal_json;
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
