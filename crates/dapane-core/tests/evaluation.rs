use dapane_core::{DapaneError, MeasureKind, Rational, Report, Request, evaluate, evaluate_json};
use serde_json::{Value, json};

fn source() -> Value {
    json!({
        "id": "synthetic-fixture", "version": "1",
        "evidence": "synthetic", "access": "public", "validation": "unvalidated"
    })
}

fn base() -> Value {
    json!({
        "schema_version": "0.1", "run_id": "independent-example",
        "knowledge_cutoff": "2026-11-08",
        "policy": {
            "id": "synthetic-provider-cost", "version": "1",
            "currency": "AUD", "price_year": 2026, "perspective": "provider",
            "basis": "financial_cost", "rounding": {"scale": 2, "mode": "half_even"}
        },
        "quotes": [{
            "id": "staff-rate", "kind": "resource_use", "target": "clinical_staff",
            "unit": "hour", "amount": "31.20", "per_quantity": "1",
            "currency": "AUD", "price_year": 2026, "basis": "financial_cost",
            "components": ["salary"], "valid_from": "2026-01-01", "valid_to": "2027-01-01",
            "known_from": "2025-12-01", "source": source()
        }],
        "usage": [{
            "id": "staff-line", "use_id": "staff-use", "kind": "resource_use",
            "target": "clinical_staff", "unit": "hour",
            "quantity": {"numerator": "1", "denominator": "3"},
            "service_date": "2026-06-01", "quote_id": "staff-rate", "source": source()
        }]
    })
}

fn report(value: &Value) -> Report {
    serde_json::from_str(&evaluate_json(&value.to_string()).unwrap()).unwrap()
}

fn error(value: &Value) -> DapaneError {
    evaluate_json(&value.to_string()).unwrap_err()
}

fn ratio(numerator: &str, denominator: &str) -> Rational {
    Rational {
        numerator: numerator.to_owned(),
        denominator: denominator.to_owned(),
    }
}

fn pool(value: &mut Value, amount: &str) {
    value["usage"][0]["quantity"] = json!("1");
    value["quotes"][0]["amount"] = json!(amount);
    value["objects"] = json!([
        {"id":"c","kind":"recipient"}, {"id":"a","kind":"recipient"}, {"id":"b","kind":"recipient"}
    ]);
    value["allocations"] = json!([{
        "id": "shared-pool", "source_line_ids": ["staff-line"],
        "weights": [
            {"object_id":"c","weight":"1"}, {"object_id":"b","weight":"1"}, {"object_id":"a","weight":"1"}
        ]
    }]);
}

#[test]
fn rational_duration_and_decimal_rate_remain_exact() {
    // Independently: one third of 31.20 = 10.40 = 52/5.
    let output = report(&base());
    assert_eq!(output.lines[0].quantity, ratio("1", "3"));
    assert_eq!(output.lines[0].exact, ratio("52", "5"));
    assert_eq!(output.totals.rounded, "10.40");
    assert_eq!(output.totals.rounding_adjustment, ratio("0", "1"));
}

#[test]
fn half_even_ties_and_line_then_sum_policy_are_explicit() {
    for (amount, expected) in [
        ("0.005", "0.00"),
        ("0.015", "0.02"),
        ("0.025", "0.02"),
        ("0.035", "0.04"),
        ("1.225", "1.22"),
        ("1.235", "1.24"),
    ] {
        let mut input = base();
        input["usage"][0]["quantity"] = json!("1");
        input["quotes"][0]["amount"] = json!(amount);
        assert_eq!(report(&input).totals.rounded, expected);
    }
    let mut input = base();
    input["quotes"][0]["amount"] = json!("0.005");
    input["usage"][0]["quantity"] = json!("1");
    let mut second = input["usage"][0].clone();
    second["id"] = json!("second-line");
    second["use_id"] = json!("second-use");
    input["usage"].as_array_mut().unwrap().push(second);
    let output = report(&input);
    assert_eq!(output.totals.exact, ratio("1", "100"));
    assert_eq!(output.totals.rounded, "0.00");
    assert_eq!(output.totals.rounding_adjustment, ratio("-1", "100"));
}

#[test]
fn largest_remainder_conserves_subcent_three_way_pool() {
    let mut input = base();
    pool(&mut input, "0.05");
    let output = report(&input);
    let allocated = &output.allocations[0];
    assert_eq!(allocated.pool_rounded, "0.05");
    assert_eq!(allocated.residual, "0.00");
    assert_eq!(
        allocated
            .shares
            .iter()
            .map(|s| (s.object_id.as_str(), s.rounded.as_str()))
            .collect::<Vec<_>>(),
        vec![("a", "0.02"), ("b", "0.02"), ("c", "0.01")]
    );
    assert!(
        allocated
            .shares
            .iter()
            .all(|s| s.exact_share == ratio("1", "60"))
    );
    assert_eq!(output.totals.allocated, "0.05");
    assert_eq!(output.totals.unattributed, "0.00");
}

#[test]
fn equal_weight_allocation_conserves_many_pool_sizes_without_floats() {
    for minor in 0..=101 {
        let mut input = base();
        pool(&mut input, &format!("{}.{:02}", minor / 100, minor % 100));
        let output = report(&input);
        let shares = &output.allocations[0].shares;
        let actual: Vec<u32> = shares
            .iter()
            .map(|share| share.rounded.replace('.', "").parse().unwrap())
            .collect();
        assert_eq!(actual.iter().sum::<u32>(), minor);
        // Independent quotient/remainder oracle for three equal recipients.
        let expected: Vec<u32> = (0..3)
            .map(|index| minor / 3 + u32::from(index < minor % 3))
            .collect();
        assert_eq!(actual, expected);
    }
}

#[test]
fn zero_weight_is_not_given_a_rounding_residual() {
    let mut input = base();
    pool(&mut input, "0.01");
    input["allocations"][0]["weights"] = json!([
        {"object_id":"a","weight":"0"}, {"object_id":"b","weight":"1"}, {"object_id":"c","weight":"0"}
    ]);
    let output = report(&input);
    assert_eq!(
        output.allocations[0]
            .shares
            .iter()
            .map(|s| s.rounded.as_str())
            .collect::<Vec<_>>(),
        ["0.00", "0.01", "0.00"]
    );
}

#[test]
fn weighted_activity_funding_does_not_invent_resource_use() {
    let mut input = base();
    input["policy"]["basis"] = json!("funding");
    input["quotes"][0]["basis"] = json!("funding");
    input["quotes"][0]["kind"] = json!("activity_measure");
    input["quotes"][0]["target"] = json!("weighted_activity");
    input["quotes"][0]["unit"] = json!("weighted_unit");
    input["quotes"][0]["amount"] = json!("17.00");
    input["quotes"][0]["components"] = json!(["funding"]);
    input["usage"][0]["kind"] = json!("activity_measure");
    input["usage"][0]["target"] = json!("weighted_activity");
    input["usage"][0]["unit"] = json!("weighted_unit");
    input["usage"][0]["quantity"] = json!("2.50");
    let output = report(&input);
    assert_eq!(output.totals.exact, ratio("85", "2"));
    assert_eq!(output.totals.rounded, "42.50");
    assert!(
        output
            .lines
            .iter()
            .all(|line| line.kind == MeasureKind::ActivityMeasure)
    );
}

fn newborn() -> Value {
    let mut input = base();
    input["quotes"][0]["unit"] = json!("minute");
    input["quotes"][0]["amount"] = json!("2");
    let mut kit = input["quotes"][0].clone();
    kit["id"] = json!("kit-rate");
    kit["target"] = json!("batch_kit");
    kit["unit"] = json!("kit");
    kit["amount"] = json!("100");
    kit["components"] = json!(["consumable"]);
    input["quotes"].as_array_mut().unwrap().push(kit);
    input["objects"] = json!([
        {"id":"infant-a","kind":"infant"}, {"id":"infant-b","kind":"infant"},
        {"id":"specimen-a","kind":"specimen"}, {"id":"specimen-b","kind":"specimen"},
        {"id":"batch","kind":"batch"}
    ]);
    input["processes"] =
        json!([{"id":"screening-run","model_id":"synthetic-newborn-pathway","model_version":"1"}]);
    input["events"] = json!([
        {"id":"collection-a","occurred_on":"2026-06-01","process_id":"screening-run","activity_id":"collection","object_ids":["infant-a","specimen-a"]},
        {"id":"collection-b","occurred_on":"2026-06-01","process_id":"screening-run","activity_id":"collection","object_ids":["infant-b","specimen-b"]},
        {"id":"assay","occurred_on":"2026-06-01","process_id":"screening-run","activity_id":"assay","object_ids":["batch","specimen-a","specimen-b"]},
        {"id":"confirmation-b","occurred_on":"2026-06-01","process_id":"screening-run","activity_id":"confirmation","object_ids":["infant-b","specimen-b"]}
    ]);
    input["object_relations"] = json!([
        {"from_object_id":"infant-a","to_object_id":"specimen-a","relationship":"has_specimen"},
        {"from_object_id":"infant-b","to_object_id":"specimen-b","relationship":"has_specimen"},
        {"from_object_id":"specimen-a","to_object_id":"batch","relationship":"processed_in"},
        {"from_object_id":"specimen-b","to_object_id":"batch","relationship":"processed_in"}
    ]);
    let template = input["usage"][0].clone();
    let mut usage = Vec::new();
    for (id, quantity, object) in [
        ("collection-a", "5", "infant-a"),
        ("collection-b", "5", "infant-b"),
        ("confirmation-b", "15", "infant-b"),
    ] {
        let mut line = template.clone();
        line["id"] = json!(id);
        line["use_id"] = json!(format!("use-{id}"));
        line["unit"] = json!("minute");
        line["quantity"] = json!(quantity);
        line["event_id"] = json!(id);
        line["attribution_object_id"] = json!(object);
        usage.push(line);
    }
    let mut batch = template;
    batch["id"] = json!("batch-line");
    batch["use_id"] = json!("batch-kit-use");
    batch["unit"] = json!("kit");
    batch["target"] = json!("batch_kit");
    batch["quantity"] = json!("1");
    batch["quote_id"] = json!("kit-rate");
    batch["event_id"] = json!("assay");
    batch["object_ids"] = json!(["batch", "infant-a", "infant-b", "specimen-a", "specimen-b"]);
    usage.push(batch);
    input["usage"] = Value::Array(usage);
    input["allocations"] = json!([{
        "id":"batch-share","source_line_ids":["batch-line"],
        "weights":[{"object_id":"infant-a","weight":"1"},{"object_id":"infant-b","weight":"1"}]
    }]);
    input
}

#[test]
fn newborn_shared_batch_conserves_150_as_60_and_90() {
    // Collection: 5*2 each. Shared batch:100. B confirmation:15*2.
    let output = report(&newborn());
    assert_eq!(output.lines.len(), 4);
    assert_eq!(output.totals.exact, ratio("150", "1"));
    assert_eq!(output.totals.rounded, "150.00");
    assert_eq!(output.totals.directly_attributed, "50.00");
    assert_eq!(output.totals.allocated, "100.00");
    assert_eq!(output.totals.unattributed, "0.00");
    let object_total = |id: &str| {
        output
            .object_totals
            .iter()
            .find(|object| object.object_id == id)
            .unwrap()
            .total
            .as_str()
    };
    assert_eq!(object_total("infant-a"), "60.00");
    assert_eq!(object_total("infant-b"), "90.00");
    assert_eq!(object_total("batch"), "0.00");
    assert_eq!(object_total("specimen-a"), "0.00");
    assert_eq!(output.lines[0].process_id.as_deref(), Some("screening-run"));
}

#[test]
fn context_associations_do_not_multiply_or_attribute_values() {
    let mut input = base();
    input["objects"] = json!([{"id":"a","kind":"patient"},{"id":"b","kind":"patient"}]);
    input["usage"][0]["object_ids"] = json!(["a", "b"]);
    let output = report(&input);
    assert_eq!(output.totals.rounded, "10.40");
    assert_eq!(output.totals.unattributed, "10.40");
    assert!(
        output
            .object_totals
            .iter()
            .all(|object| object.total == "0.00")
    );
}

#[test]
fn repeated_runs_and_collection_permutations_are_identical() {
    let input = newborn();
    let first = evaluate_json(&input.to_string()).unwrap();
    assert_eq!(evaluate_json(&input.to_string()).unwrap(), first);
    let mut reversed = input;
    for field in [
        "quotes",
        "usage",
        "objects",
        "processes",
        "events",
        "object_relations",
        "allocations",
    ] {
        reversed[field].as_array_mut().unwrap().reverse();
    }
    for event in reversed["events"].as_array_mut().unwrap() {
        event["object_ids"].as_array_mut().unwrap().reverse();
    }
    reversed["allocations"][0]["weights"]
        .as_array_mut()
        .unwrap()
        .reverse();
    assert_eq!(evaluate_json(&reversed.to_string()).unwrap(), first);
    reversed["policy"]["version"] = json!("2");
    assert_ne!(
        report(&reversed).output_digest,
        serde_json::from_str::<Report>(&first)
            .unwrap()
            .output_digest
    );
}

#[test]
fn exact_zero_is_distinct_from_missing_or_unavailable_input() {
    let mut input = base();
    input["usage"][0]["quantity"] = json!("0");
    assert_eq!(report(&input).totals.rounded, "0.00");
    input["usage"][0]
        .as_object_mut()
        .unwrap()
        .remove("quantity");
    assert_eq!(error(&input).code, "invalid_request");
    input["usage"][0]["quantity"] = Value::Null;
    assert_eq!(error(&input).code, "invalid_request");
}

#[test]
fn dates_are_strict_and_quote_validity_is_half_open() {
    let mut input = base();
    input["usage"][0]["service_date"] = json!("2026-01-01");
    assert!(evaluate_json(&input.to_string()).is_ok());
    input["usage"][0]["service_date"] = json!("2027-01-01");
    assert_eq!(error(&input).code, "quote_not_effective");
    input["usage"][0]["service_date"] = json!("2025-12-31");
    assert_eq!(error(&input).code, "quote_not_effective");
    for invalid in [
        "2026-02-29",
        "2026-2-01",
        "0000-01-01",
        "2026-01-01T00:00:00Z",
    ] {
        input["usage"][0]["service_date"] = json!(invalid);
        assert_eq!(error(&input).code, "invalid_date");
    }
    input["usage"][0]["service_date"] = json!("2026-01-01");
    input["knowledge_cutoff"] = json!("2025-11-30");
    assert_eq!(error(&input).code, "quote_not_known");
    input["knowledge_cutoff"] = json!("2025-12-01");
    assert!(evaluate_json(&input.to_string()).is_ok());
}

#[test]
fn kind_target_unit_and_valuation_context_must_match() {
    for (field, value) in [
        ("kind", "activity_measure"),
        ("target", "different"),
        ("unit", "minute"),
    ] {
        let mut input = base();
        input["usage"][0][field] = json!(value);
        assert_eq!(error(&input).code, "quote_mismatch");
    }
    for (field, value) in [
        ("basis", json!("funding")),
        ("currency", json!("USD")),
        ("price_year", json!(2025)),
    ] {
        let mut input = base();
        input["quotes"][0][field] = value;
        assert_eq!(error(&input).code, "valuation_mismatch");
    }
}

#[test]
fn duplicate_loaded_components_are_rejected_and_disjoint_components_allowed() {
    let mut input = base();
    input["quotes"][0]["components"] = json!(["salary", "oncost"]);
    let mut duplicate = input["usage"][0].clone();
    duplicate["id"] = json!("additional-oncost");
    input["usage"].as_array_mut().unwrap().push(duplicate);
    assert_eq!(error(&input).code, "component_overlap");
    let mut oncost = input["quotes"][0].clone();
    oncost["id"] = json!("oncost-rate");
    oncost["components"] = json!(["oncost"]);
    oncost["amount"] = json!("6");
    input["quotes"].as_array_mut().unwrap().push(oncost);
    input["usage"][1]["quote_id"] = json!("oncost-rate");
    assert_eq!(error(&input).code, "component_overlap");
    input["quotes"][0]["components"] = json!(["salary"]);
    assert_eq!(report(&input).totals.rounded, "12.40");
    input["usage"][1]["quantity"] = json!("2");
    assert_eq!(error(&input).code, "inconsistent_use");
}

#[test]
fn duplicate_ids_are_rejected_in_each_registry() {
    for field in [
        "quotes",
        "usage",
        "objects",
        "processes",
        "events",
        "allocations",
    ] {
        let mut input = newborn();
        let duplicate = input[field][0].clone();
        input[field].as_array_mut().unwrap().push(duplicate);
        assert_eq!(error(&input).code, "duplicate_id", "{field}");
    }
}

#[test]
fn source_lines_cannot_be_counted_in_two_allocation_views() {
    let mut input = base();
    pool(&mut input, "0.05");
    input["allocations"][0]["source_line_ids"] = json!(["staff-line", "staff-line"]);
    assert_eq!(error(&input).code, "allocation_overlap");
    input["allocations"][0]["source_line_ids"] = json!(["staff-line"]);
    let mut duplicate = input["allocations"][0].clone();
    duplicate["id"] = json!("second-pool");
    input["allocations"].as_array_mut().unwrap().push(duplicate);
    assert_eq!(error(&input).code, "allocation_overlap");
    input["allocations"].as_array_mut().unwrap().pop();
    input["usage"][0]["attribution_object_id"] = json!("a");
    assert_eq!(error(&input).code, "allocation_overlap");
}

#[test]
fn invalid_contexts_are_rejected_with_structured_paths() {
    let mut input = base();
    input["usage"][0]["event_id"] = json!("missing-event");
    let failure = error(&input);
    assert_eq!(failure.code, "unknown_reference");
    assert_eq!(failure.path, "/usage/0/event_id");
    let structured: Value = serde_json::from_str(&failure.to_string()).unwrap();
    assert_eq!(structured["code"], "unknown_reference");
    input["usage"][0]
        .as_object_mut()
        .unwrap()
        .remove("event_id");
    input["usage"][0]["activity_id"] = json!("activity-without-process");
    assert_eq!(error(&input).code, "invalid_context");
    let mut input = newborn();
    input["processes"]
        .as_array_mut()
        .unwrap()
        .push(json!({"id":"other","model_id":"other-model","model_version":"1"}));
    input["usage"][0]["process_id"] = json!("other");
    assert_eq!(error(&input).code, "invalid_context");
    input["usage"][0]["process_id"] = Value::Null;
    input["usage"][0]["activity_id"] = json!("contradictory-activity");
    assert_eq!(error(&input).code, "invalid_context");
    input["usage"][0]["activity_id"] = Value::Null;
    input["object_relations"][0]["to_object_id"] = json!("missing");
    assert_eq!(error(&input).code, "unknown_reference");
}

#[test]
fn numeric_literals_unknown_fields_and_duplicate_json_keys_are_rejected() {
    let mut input = base();
    input["usage"][0]["quantity"] = json!(0.3333333333);
    assert_eq!(error(&input).code, "invalid_request");
    input["usage"][0]["quantity"] = json!("1");
    input["usage"][0]["duration"] = json!("1");
    assert_eq!(error(&input).code, "invalid_request");
    let raw = base().to_string().replacen(
        "\"schema_version\":\"0.1\"",
        "\"schema_version\":\"0.1\",\"schema_version\":\"0.1\"",
        1,
    );
    assert_eq!(evaluate_json(&raw).unwrap_err().code, "invalid_json");
    let mut input = base();
    input["schema_version"] = json!("next");
    assert_eq!(error(&input).code, "unsupported_schema");
    input = base();
    input["policy"]["rounding"]["mode"] = json!("half_up");
    assert_eq!(error(&input).code, "invalid_request");
}

#[test]
fn invalid_numbers_and_precision_limits_are_bounded() {
    for invalid in [
        "-1", "+1", "1e3", " 1", "1.", ".5", "NaN", "Infinity", "1.2.3",
    ] {
        let mut input = base();
        input["usage"][0]["quantity"] = json!(invalid);
        assert_eq!(error(&input).code, "invalid_number", "{invalid}");
    }
    let mut input = base();
    input["usage"][0]["quantity"] = json!({"numerator":"1","denominator":"0"});
    assert_eq!(error(&input).code, "zero_denominator");
    input["usage"][0]["quantity"] = json!("1".repeat(97));
    assert_eq!(error(&input).code, "precision_limit");
    input["usage"][0]["quantity"] = json!(format!("0.{}1", "0".repeat(36)));
    assert_eq!(error(&input).code, "precision_limit");
    input = base();
    input["policy"]["rounding"]["scale"] = json!(13);
    assert_eq!(error(&input).code, "unsupported_rounding");
    assert_eq!(
        evaluate_json(&" ".repeat(dapane_core::MAX_JSON_BYTES + 1))
            .unwrap_err()
            .code,
        "input_limit"
    );
}

#[test]
fn invalid_sources_zero_denominators_and_zero_pools_are_explicit() {
    let mut input = base();
    input["quotes"][0]["source"]["version"] = json!("");
    assert_eq!(error(&input).code, "invalid_identifier");
    input = base();
    input["quotes"][0]["source"]["content_digest"] = json!("sha256:fake");
    assert_eq!(error(&input).code, "invalid_source_digest");
    input = base();
    input["quotes"][0]["per_quantity"] = json!("0");
    assert_eq!(error(&input).code, "invalid_quote");
    input = base();
    pool(&mut input, "0.00");
    assert_eq!(report(&input).totals.rounded, "0.00");
    for weight in input["allocations"][0]["weights"].as_array_mut().unwrap() {
        weight["weight"] = json!("0");
    }
    assert_eq!(error(&input).code, "zero_weights");
}

#[test]
fn typed_and_json_entry_points_agree_and_empty_ledger_is_explicit() {
    let value = base();
    let typed: Request = serde_json::from_value(value.clone()).unwrap();
    assert_eq!(evaluate(&typed).unwrap(), report(&value));
    let mut empty = value;
    empty["usage"] = json!([]);
    empty["quotes"] = json!([]);
    let output = report(&empty);
    assert_eq!(output.totals.rounded, "0.00");
    assert!(output.lines.is_empty());
}

#[test]
fn rational_accumulation_has_a_real_intermediate_precision_bound() {
    // Distinct prime denominators cannot cancel out of this harmonic-like sum:
    // modulo each prime, exactly one numerator term is nonzero.
    let mut input = base();
    input["quotes"][0]["amount"] = json!("1");
    let template = input["usage"][0].clone();
    let primes: Vec<usize> = (2..5000)
        .filter(|candidate| {
            (2..)
                .take_while(|divisor| divisor * divisor <= *candidate)
                .all(|divisor| candidate % divisor != 0)
        })
        .take(500)
        .collect();
    assert_eq!(primes.len(), 500);
    input["usage"] = Value::Array(
        primes
            .iter()
            .enumerate()
            .map(|(index, prime)| {
                let mut line = template.clone();
                line["id"] = json!(format!("line-{index:04}"));
                line["use_id"] = json!(format!("use-{index:04}"));
                line["quantity"] = json!({"numerator":"1","denominator":prime.to_string()});
                line
            })
            .collect(),
    );
    assert_eq!(error(&input).code, "precision_limit");
    input["usage"].as_array_mut().unwrap().reverse();
    assert_eq!(error(&input).code, "precision_limit");
}

#[test]
fn collection_and_typed_byte_limits_stop_oversized_requests() {
    let mut input = base();
    input["objects"] = Value::Array(
        (0..10_001)
            .map(|index| {
                json!({
                    "id":format!("object-{index}"),"kind":"test"
                })
            })
            .collect(),
    );
    let failure = error(&input);
    assert_eq!(failure.code, "input_limit");
    assert_eq!(failure.path, "/objects");
    input["objects"].as_array_mut().unwrap().pop();
    input["processes"] = Value::Array(
        (0..10_000)
            .map(|index| {
                json!({
                    "id":format!("process-{index}"),"model_id":"model","model_version":"1"
                })
            })
            .collect(),
    );
    assert_eq!(error(&input).code, "input_limit");
    let mut typed: Request = serde_json::from_value(base()).unwrap();
    typed.run_id = "x".repeat(dapane_core::MAX_JSON_BYTES + 1);
    assert_eq!(evaluate(&typed).unwrap_err().code, "input_limit");
}

#[test]
fn identifier_limits_count_utf8_bytes_and_evidence_remains_declarative() {
    let mut input = base();
    input["run_id"] = json!("é".repeat(64));
    assert!(evaluate_json(&input.to_string()).is_ok());
    input["run_id"] = json!("é".repeat(65));
    assert_eq!(error(&input).code, "invalid_identifier");
    input["run_id"] = json!("derived-example");
    input["usage"][0]["source"]["evidence"] = json!("derived");
    input["quotes"][0]["source"]["validation"] = json!("source_verified");
    let output = report(&input);
    assert_eq!(
        output.lines[0].source.evidence,
        dapane_core::Evidence::Derived
    );
    assert_eq!(
        output.lines[0].source.validation,
        dapane_core::SourceValidation::Unvalidated
    );
    assert_eq!(
        output.quote_snapshots[0].source.validation,
        dapane_core::SourceValidation::SourceVerified
    );
}

fn inherited_component_context() -> Value {
    let mut input = base();
    input["quotes"][0]["amount"] = json!("90");
    input["processes"] = json!([{"id":"p","model_id":"synthetic-work","model_version":"1"}]);
    input["events"] = json!([{
        "id":"e","occurred_on":"2026-06-01","process_id":"p","activity_id":"work"
    }]);
    input["usage"][0]["event_id"] = json!("e");
    let mut oncost_quote = input["quotes"][0].clone();
    oncost_quote["id"] = json!("oncost-rate");
    oncost_quote["amount"] = json!("9");
    oncost_quote["components"] = json!(["oncost"]);
    input["quotes"].as_array_mut().unwrap().push(oncost_quote);
    let mut oncost_use = input["usage"][0].clone();
    oncost_use["id"] = json!("oncost-line");
    oncost_use["quote_id"] = json!("oncost-rate");
    oncost_use["process_id"] = json!("p");
    oncost_use["activity_id"] = json!("work");
    input["usage"].as_array_mut().unwrap().push(oncost_use);
    input
}

#[test]
fn disjoint_components_can_mix_inherited_and_explicit_equivalent_context() {
    // Independent calculation: 1/3 hour * (90 salary + 9 oncost) = 33.
    let output = report(&inherited_component_context());
    assert_eq!(output.totals.rounded, "33.00");
    assert_eq!(output.totals.exact, ratio("33", "1"));
    assert_eq!(output.lines.len(), 2);
    for line in output.lines {
        assert_eq!(line.event_id.as_deref(), Some("e"));
        assert_eq!(line.process_id.as_deref(), Some("p"));
        assert_eq!(line.activity_id.as_deref(), Some("work"));
    }
}

#[test]
fn disjoint_components_still_reject_contradictory_resolved_context() {
    let mut input = inherited_component_context();
    input["processes"]
        .as_array_mut()
        .unwrap()
        .push(json!({"id":"q","model_id":"synthetic-work","model_version":"1"}));
    input["usage"][1]["process_id"] = json!("q");
    assert_eq!(error(&input).code, "invalid_context");
    input["usage"][1]["process_id"] = json!("p");
    input["usage"][1]["activity_id"] = json!("contradictory-work");
    assert_eq!(error(&input).code, "invalid_context");
}
