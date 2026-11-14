//! Independent acceptance cases for explicitly uniform calendar-day exposure.

use dapane_core::{DapaneError, evaluate_json};
use serde_json::{Value, json};

fn source() -> Value {
    json!({"id":"independent-interval-case","version":"1","evidence":"synthetic",
        "access":"public","validation":"unvalidated"})
}

fn base() -> Value {
    let old = json!({"id":"old","kind":"resource_use","target":"staff","unit":"hour",
        "amount":"2","per_quantity":"1","currency":"AUD","price_year":2026,
        "basis":"financial_cost","components":["salary"],"valid_from":"2026-01-01",
        "valid_to":"2026-01-05","known_from":"2025-12-01","source":source()});
    let mut new = old.clone();
    new["id"] = json!("new");
    new["amount"] = json!("3");
    new["valid_from"] = json!("2026-01-05");
    new["valid_to"] = json!("2026-01-11");
    json!({"schema_version":"0.3","run_id":"independent-interval-run",
        "knowledge_cutoff":"2026-11-08",
        "policy":{"id":"provider-cost","version":"1","currency":"AUD","price_year":2026,
            "perspective":"provider","basis":"financial_cost","rounding":{"scale":2,"mode":"half_even"}},
        "quotes":[old,new],"usage":[],
        "interval_usage":[{"id":"staff-line","use_id":"staff-use","kind":"resource_use",
            "target":"staff","unit":"hour","quantity":"10","start_date":"2026-01-01",
            "end_date":"2026-01-11","exposure":"uniform_calendar_days","quote_ids":["old","new"],
            "source":source()}]})
}

fn report(input: &Value) -> Value {
    serde_json::from_str(
        &evaluate_json(&input.to_string()).expect("valid independent interval case"),
    )
    .unwrap()
}

fn error(input: &Value) -> DapaneError {
    evaluate_json(&input.to_string()).expect_err("invalid interval case must be rejected")
}

fn rejected(input: &Value, code: &str) {
    let failure = error(input);
    assert_eq!(failure.code, code, "{failure}");
    assert!(failure.path.starts_with('/'));
    assert!(!failure.message.is_empty());
}

fn ratio(numerator: &str, denominator: &str) -> Value {
    json!({"numerator":numerator,"denominator":denominator})
}

fn point(id: &str, use_id: &str, quantity: &str) -> Value {
    json!({"id":id,"use_id":use_id,"kind":"resource_use","target":"staff","unit":"hour",
        "quantity":quantity,"service_date":"2026-01-02","quote_id":"old","source":source()})
}

#[test]
fn rate_change_preserves_independent_values_and_parent_lineage() {
    // Four of ten days at 2, then six at 3: 4 * 2 + 6 * 3 = 26.
    let output = report(&base());
    assert_eq!(output["schema_version"], "0.3");
    assert_eq!(output["method_version"], "dapane-exact-v0.3.0");
    assert_eq!(output["status"], "complete");
    assert_eq!(output["lines"], json!([]));
    let line = &output["interval_lines"][0];
    assert_eq!(line["id"], "staff-line");
    assert_eq!(line["use_id"], "staff-use");
    assert_eq!(line["source"]["id"], "independent-interval-case");
    assert_eq!(line["quantity"], ratio("10", "1"));
    assert_eq!(line["exposure"], "uniform_calendar_days");
    assert_eq!(line["components"], json!(["salary"]));
    assert_eq!(
        line["segments"],
        json!([
            {"quote_id":"old","start_date":"2026-01-01","end_date":"2026-01-05",
                "quantity":ratio("4","1"),"exact":ratio("8","1")},
            {"quote_id":"new","start_date":"2026-01-05","end_date":"2026-01-11",
                "quantity":ratio("6","1"),"exact":ratio("18","1")}
        ])
    );
    assert_eq!(line["exact"], ratio("26", "1"));
    assert_eq!(line["rounded"], "26.00");
    assert_eq!(output["totals"]["exact"], ratio("26", "1"));
    assert_eq!(output["totals"]["rounded"], "26.00");
    assert_eq!(output["totals"]["unattributed"], "26.00");
}

#[test]
fn fractional_total_exposure_is_not_coerced_to_float() {
    // One third over three days: (2/9)*3 + (1/9)*6 = 4/3.
    let mut input = base();
    input["interval_usage"][0]["quantity"] = ratio("1", "3");
    input["interval_usage"][0]["end_date"] = json!("2026-01-04");
    input["quotes"][0]["amount"] = json!("3");
    input["quotes"][0]["valid_to"] = json!("2026-01-03");
    input["quotes"][1]["amount"] = json!("6");
    input["quotes"][1]["valid_from"] = json!("2026-01-03");
    let output = report(&input);
    let line = &output["interval_lines"][0];
    assert_eq!(line["segments"][0]["quantity"], ratio("2", "9"));
    assert_eq!(line["segments"][1]["quantity"], ratio("1", "9"));
    assert_eq!(line["exact"], ratio("4", "3"));
    assert_eq!(line["rounded"], "1.33");
    assert_eq!(line["rounding_adjustment"], ratio("-1", "300"));
}

#[test]
fn equivalent_rate_subdivision_rounds_once_per_parent() {
    // The two segment amounts are 0.005 each; parent rounding must produce 0.01.
    let mut split = base();
    split["interval_usage"][0]["quantity"] = json!("2");
    split["interval_usage"][0]["end_date"] = json!("2026-01-03");
    split["quotes"][0]["valid_to"] = json!("2026-01-02");
    split["quotes"][1]["valid_from"] = json!("2026-01-02");
    for quote in split["quotes"].as_array_mut().unwrap() {
        quote["amount"] = json!("0.005");
    }
    let split_report = report(&split);
    assert_eq!(
        split_report["interval_lines"][0]["segments"][0]["exact"],
        ratio("1", "200")
    );
    assert_eq!(
        split_report["interval_lines"][0]["segments"][1]["exact"],
        ratio("1", "200")
    );
    assert_eq!(split_report["totals"]["rounded"], "0.01");
    let mut whole = split.clone();
    whole["quotes"][0]["valid_to"] = json!("2026-01-03");
    whole["interval_usage"][0]["quote_ids"] = json!(["old"]);
    let whole_report = report(&whole);
    assert_eq!(whole_report["totals"], split_report["totals"]);
    assert_ne!(whole_report["input_digest"], split_report["input_digest"]);
}

#[test]
fn half_open_clipping_preserves_only_actual_exposure() {
    let mut input = base();
    input["interval_usage"][0]["start_date"] = json!("2026-01-03");
    input["interval_usage"][0]["end_date"] = json!("2026-01-07");
    input["interval_usage"][0]["quantity"] = json!("4");
    let output = report(&input);
    assert_eq!(output["totals"]["rounded"], "10.00");
    assert_eq!(
        output["interval_lines"][0]["segments"][0]["start_date"],
        "2026-01-03"
    );
    assert_eq!(
        output["interval_lines"][0]["segments"][1]["end_date"],
        "2026-01-07"
    );
    input["interval_usage"][0]["end_date"] = json!("2026-01-05");
    input["interval_usage"][0]["quote_ids"] = json!(["old"]);
    assert_eq!(report(&input)["totals"]["rounded"], "8.00");
}

#[test]
fn schedule_gaps_and_overlaps_are_errors_even_for_zero_quantity() {
    for quantity in ["0", "10"] {
        let mut input = base();
        input["interval_usage"][0]["quantity"] = json!(quantity);
        input["quotes"][1]["valid_from"] = json!("2026-01-06");
        rejected(&input, "interval_gap");
        input["quotes"][1]["valid_from"] = json!("2026-01-04");
        rejected(&input, "interval_overlap");
    }
}

#[test]
fn quote_selection_is_explicit_known_and_nonduplicating() {
    let mut input = base();
    input["interval_usage"][0]["quote_ids"] = json!(["old"]);
    rejected(&input, "interval_gap");
    input["interval_usage"][0]["quote_ids"] = json!(["old", "absent"]);
    rejected(&input, "missing_quote");
    input["interval_usage"][0]["quote_ids"] = json!(["old", "new", "old"]);
    rejected(&input, "duplicate_reference");
    input = base();
    input["quotes"][1]["known_from"] = json!("2026-11-09");
    rejected(&input, "quote_not_known");
}

#[test]
fn exposure_is_required_and_cannot_silently_downgrade() {
    let mut input = base();
    input["interval_usage"][0]
        .as_object_mut()
        .unwrap()
        .remove("exposure");
    rejected(&input, "invalid_request");
    input["interval_usage"][0]["exposure"] = json!("infer_equipment_hours");
    rejected(&input, "invalid_request");
    for version in ["0.1", "0.2"] {
        input = base();
        input["schema_version"] = json!(version);
        rejected(&input, "invalid_request");
    }
}

#[test]
fn rates_with_different_components_cannot_form_one_schedule() {
    let mut input = base();
    input["quotes"][1]["components"] = json!(["salary", "oncost"]);
    rejected(&input, "inconsistent_components");
}

#[test]
fn intervals_and_point_lines_cannot_alias_one_underlying_use() {
    let mut input = base();
    input["usage"] = json!([point("point-line", "staff-use", "10")]);
    rejected(&input, "inconsistent_use");
}

#[test]
fn gregorian_leap_days_and_century_rules_determine_exposure() {
    for (year, expected, first_quantity, second_quantity) in [
        (2024, "8.00", ratio("2", "1"), ratio("1", "1")),
        (2100, "9.00", ratio("3", "2"), ratio("3", "2")),
    ] {
        // Three total units: Feb 28 to Mar 2 spans three days in 2024,
        // but two in 2100. The rate changes on March 1 from 2 to 4.
        let mut input = base();
        input["knowledge_cutoff"] = json!(format!("{year}-12-31"));
        input["interval_usage"][0]["quantity"] = json!("3");
        input["interval_usage"][0]["start_date"] = json!(format!("{year}-02-28"));
        input["interval_usage"][0]["end_date"] = json!(format!("{year}-03-02"));
        input["quotes"][0]["valid_from"] = json!(format!("{year}-02-01"));
        input["quotes"][0]["valid_to"] = json!(format!("{year}-03-01"));
        input["quotes"][1]["valid_from"] = json!(format!("{year}-03-01"));
        input["quotes"][1]["valid_to"] = json!(format!("{year}-04-01"));
        input["quotes"][1]["amount"] = json!("4");
        for quote in input["quotes"].as_array_mut().unwrap() {
            quote["known_from"] = json!(format!("{year}-01-01"));
        }
        let output = report(&input);
        assert_eq!(output["totals"]["rounded"], expected);
        let segments = &output["interval_lines"][0]["segments"];
        assert_eq!(segments[0]["quantity"], first_quantity);
        assert_eq!(segments[1]["quantity"], second_quantity);
    }
}

#[test]
fn empty_reversed_and_malformed_intervals_fail_explicitly() {
    for end in ["2026-01-01", "2025-12-31"] {
        let mut input = base();
        input["interval_usage"][0]["end_date"] = json!(end);
        rejected(&input, "invalid_interval");
    }
    for start in [
        "2026-02-30",
        "2026-1-01",
        "0000-01-01",
        "2026-01-01T00:00:00Z",
    ] {
        let mut input = base();
        input["interval_usage"][0]["start_date"] = json!(start);
        rejected(&input, "invalid_date");
    }
}

#[test]
fn unused_selected_quote_is_rejected_but_unselected_snapshot_is_preserved() {
    let mut input = base();
    let mut outside = input["quotes"][0].clone();
    outside["id"] = json!("outside");
    outside["valid_from"] = json!("2026-01-11");
    outside["valid_to"] = json!("2026-02-01");
    input["quotes"].as_array_mut().unwrap().push(outside);
    assert_eq!(
        report(&input)["quote_snapshots"].as_array().unwrap().len(),
        3
    );
    input["interval_usage"][0]["quote_ids"] = json!(["old", "new", "outside"]);
    rejected(&input, "invalid_interval_quote");
}

#[test]
fn unit_target_kind_and_valuation_basis_cannot_change_mid_interval() {
    for (field, value) in [
        ("unit", "minute"),
        ("target", "equipment"),
        ("kind", "activity_measure"),
    ] {
        let mut input = base();
        input["quotes"][1][field] = json!(value);
        rejected(&input, "quote_mismatch");
    }
    // Global policy validation owns currency, basis and price-year consistency.
    for (field, value) in [("currency", "NZD"), ("basis", "funding")] {
        let mut input = base();
        input["quotes"][1][field] = json!(value);
        assert!(evaluate_json(&input.to_string()).is_err());
    }
}

#[test]
fn point_and_interval_source_lines_share_one_conserving_allocation_ledger() {
    let mut input = base();
    input["usage"] = json!([point("point-line", "point-use", "1")]);
    input["objects"] = json!([{"id":"b","kind":"recipient"},{"id":"a","kind":"recipient"}]);
    input["allocations"] = json!([{"id":"mixed-pool","source_line_ids":["staff-line","point-line"],
        "weights":[{"object_id":"b","weight":"1"},{"object_id":"a","weight":"3"}]}]);
    let output = report(&input);
    // 26 interval + 2 point = 28; 3:1 shares are 21 and 7.
    assert_eq!(output["totals"]["rounded"], "28.00");
    assert_eq!(output["totals"]["allocated"], "28.00");
    assert_eq!(output["totals"]["unattributed"], "0.00");
    let allocation = &output["allocations"][0];
    assert_eq!(allocation["pool_exact"], ratio("28", "1"));
    assert_eq!(allocation["pool_rounded"], "28.00");
    assert_eq!(allocation["residual"], "0.00");
    assert_eq!(allocation["shares"][0]["object_id"], "a");
    assert_eq!(allocation["shares"][0]["rounded"], "21.00");
    assert_eq!(allocation["shares"][1]["rounded"], "7.00");
    assert_eq!(output["object_totals"][0]["total"], "21.00");
    assert_eq!(output["object_totals"][1]["total"], "7.00");
}

#[test]
fn interval_direct_attribution_does_not_duplicate_expenditure() {
    let mut input = base();
    input["objects"] = json!([{"id":"a","kind":"recipient"},{"id":"context","kind":"context"}]);
    input["interval_usage"][0]["object_ids"] = json!(["a", "context"]);
    input["interval_usage"][0]["attribution_object_id"] = json!("a");
    input["usage"] = json!([point("point-line", "point-use", "1")]);
    let output = report(&input);
    assert_eq!(output["totals"]["rounded"], "28.00");
    assert_eq!(output["totals"]["directly_attributed"], "26.00");
    assert_eq!(output["totals"]["unattributed"], "2.00");
    assert_eq!(output["object_totals"][0]["total"], "26.00");
    assert_eq!(output["object_totals"][1]["total"], "0.00");
    input["allocations"] = json!([{"id":"duplicate-view","source_line_ids":["staff-line"],
        "weights":[{"object_id":"a","weight":"1"}]}]);
    assert!(evaluate_json(&input.to_string()).is_err());
}

#[test]
fn interval_pool_can_retain_unknown_capacity_without_recovery_assumptions() {
    let mut input = base();
    input["objects"] = json!([{"id":"a","kind":"recipient"}]);
    input["capacity_allocations"] = json!([{"id":"capacity","source_line_ids":["staff-line"],
        "unit":"instrument_hour","observation_coverage":"incomplete",
        "available_capacity":{"status":"unknown","reason":"availability not observed"},
        "use_records":[{"object_id":"a","quantity":{"status":"known","quantity":"1"}}],
        "source":source()}]);
    let output = report(&input);
    assert_eq!(output["totals"]["rounded"], "26.00");
    assert_eq!(output["totals"]["unattributed"], "26.00");
    assert_eq!(output["capacity_allocations"][0]["unallocated"], "26.00");
    assert!(output["capacity_allocations"][0]["shares"][0]["rounded"].is_null());
}

fn disjoint_components() -> Value {
    let mut input = base();
    let mut oncost_old = input["quotes"][0].clone();
    oncost_old["id"] = json!("oncost-old");
    oncost_old["amount"] = json!("1");
    oncost_old["components"] = json!(["oncost"]);
    oncost_old["valid_to"] = json!("2026-01-07");
    let mut oncost_new = oncost_old.clone();
    oncost_new["id"] = json!("oncost-new");
    oncost_new["valid_from"] = json!("2026-01-07");
    oncost_new["valid_to"] = json!("2026-01-11");
    input["quotes"]
        .as_array_mut()
        .unwrap()
        .extend([oncost_old, oncost_new]);
    let mut second = input["interval_usage"][0].clone();
    second["id"] = json!("oncost-line");
    second["quote_ids"] = json!(["oncost-old", "oncost-new"]);
    input["interval_usage"].as_array_mut().unwrap().push(second);
    input
}

#[test]
fn disjoint_components_may_have_different_rate_boundaries() {
    let output = report(&disjoint_components());
    assert_eq!(output["interval_lines"].as_array().unwrap().len(), 2);
    assert_eq!(output["totals"]["exact"], ratio("36", "1"));
    assert_eq!(output["totals"]["rounded"], "36.00");
}

#[test]
fn duplicate_components_and_inconsistent_underlying_intervals_are_rejected() {
    let mut input = disjoint_components();
    for quote in &mut input["quotes"].as_array_mut().unwrap()[2..] {
        quote["components"] = json!(["salary"]);
    }
    rejected(&input, "component_overlap");
    for (field, value) in [
        ("quantity", "11"),
        ("start_date", "2026-01-02"),
        ("end_date", "2026-01-10"),
    ] {
        let mut input = disjoint_components();
        input["interval_usage"][1][field] = json!(value);
        rejected(&input, "inconsistent_use");
    }
    input = disjoint_components();
    input["interval_usage"][1]["source"]["version"] = json!("different-observation");
    rejected(&input, "inconsistent_use");
}

#[test]
fn inherited_and_explicit_equivalent_context_remain_one_underlying_interval() {
    let mut input = disjoint_components();
    input["processes"] = json!([{"id":"process","model_id":"synthetic","model_version":"1"}]);
    input["events"] = json!([{"id":"event","occurred_on":"2026-01-01",
        "process_id":"process","activity_id":"activity"}]);
    for line in input["interval_usage"].as_array_mut().unwrap() {
        line["event_id"] = json!("event");
    }
    input["interval_usage"][1]["process_id"] = json!("process");
    input["interval_usage"][1]["activity_id"] = json!("activity");
    let output = report(&input);
    for line in output["interval_lines"].as_array().unwrap() {
        assert_eq!(line["process_id"], "process");
        assert_eq!(line["activity_id"], "activity");
    }
    assert_eq!(output["totals"]["rounded"], "36.00");
    input["interval_usage"][1]["activity_id"] = json!("contradictory-activity");
    assert!(evaluate_json(&input.to_string()).is_err());
}

#[test]
fn valid_zero_exposure_has_complete_zero_financial_result() {
    let mut input = base();
    input["interval_usage"][0]["quantity"] = json!("0");
    let output = report(&input);
    assert_eq!(output["status"], "complete");
    assert_eq!(output["totals"]["exact"], ratio("0", "1"));
    assert_eq!(output["totals"]["rounded"], "0.00");
    for segment in output["interval_lines"][0]["segments"].as_array().unwrap() {
        assert_eq!(segment["quantity"], ratio("0", "1"));
        assert_eq!(segment["exact"], ratio("0", "1"));
    }
}

#[test]
fn collection_and_schedule_permutations_do_not_change_identity() {
    let original = disjoint_components();
    let mut reordered = original.clone();
    reordered["quotes"].as_array_mut().unwrap().reverse();
    reordered["interval_usage"]
        .as_array_mut()
        .unwrap()
        .reverse();
    for interval in reordered["interval_usage"].as_array_mut().unwrap() {
        interval["quote_ids"].as_array_mut().unwrap().reverse();
    }
    assert_eq!(report(&original), report(&reordered));
    let mut respelled = original.clone();
    for interval in respelled["interval_usage"].as_array_mut().unwrap() {
        interval["quantity"] = json!("10.00");
    }
    let original = report(&original);
    let respelled = report(&respelled);
    assert_eq!(original["totals"], respelled["totals"]);
    assert_eq!(original["interval_lines"], respelled["interval_lines"]);
    assert_ne!(original["input_digest"], respelled["input_digest"]);
}

#[test]
fn equivalent_rate_splits_preserve_financial_results_across_boundaries() {
    for amount in ["0.005", "1.235", "999999.123456789"] {
        let mut whole = base();
        whole["quotes"].as_array_mut().unwrap().truncate(1);
        whole["quotes"][0]["amount"] = json!(amount);
        whole["quotes"][0]["valid_to"] = json!("2026-01-11");
        whole["interval_usage"][0]["quote_ids"] = json!(["old"]);
        whole["interval_usage"][0]["quantity"] = ratio("7", "3");
        let expected = report(&whole)["totals"].clone();
        for day in 2..=10 {
            let boundary = format!("2026-01-{day:02}");
            let mut split = whole.clone();
            let mut next = split["quotes"][0].clone();
            next["id"] = json!("new");
            next["valid_from"] = json!(boundary);
            split["quotes"][0]["valid_to"] = json!(boundary);
            split["quotes"].as_array_mut().unwrap().push(next);
            split["interval_usage"][0]["quote_ids"] = json!(["new", "old"]);
            assert_eq!(
                report(&split)["totals"],
                expected,
                "{amount} split at {day}"
            );
        }
    }
}

#[test]
fn interval_precision_and_collection_limits_fail_without_partial_results() {
    let mut input = base();
    input["interval_usage"][0]["quantity"] = json!("9".repeat(97));
    rejected(&input, "precision_limit");
    input = base();
    input["interval_usage"][0]["quantity"] = json!({"numerator":"1","denominator":"0"});
    rejected(&input, "zero_denominator");
    input = base();
    let interval = input["interval_usage"][0].clone();
    input["interval_usage"] = json!(vec![interval; 10_001]);
    rejected(&input, "input_limit");
}

#[test]
fn numeric_literals_unknown_fields_and_duplicate_json_keys_are_not_accepted() {
    let mut input = base();
    input["interval_usage"][0]["quantity"] = json!(1.0);
    rejected(&input, "invalid_request");
    input = base();
    input["interval_usage"][0]["inferred_availability"] = json!(true);
    rejected(&input, "invalid_request");
    let raw = base().to_string();
    let duplicate = raw.replace(
        "\"uniform_calendar_days\"",
        "\"uniform_calendar_days\",\"exposure\":\"uniform_calendar_days\"",
    );
    assert!(evaluate_json(&duplicate).is_err());
}

#[test]
fn component_overlap_diagnostic_points_to_the_actual_interval_field() {
    let mut input = disjoint_components();
    for quote in &mut input["quotes"].as_array_mut().unwrap()[2..] {
        quote["components"] = json!(["salary"]);
    }
    let failure = error(&input);
    assert_eq!(failure.code, "component_overlap");
    assert_eq!(failure.path, "/interval_usage/1/quote_ids");
    assert!(input.pointer(&failure.path).is_some());
}

#[test]
fn interval_precision_errors_retain_caller_indices_after_normalization() {
    // Distinct prime denominators cannot cancel from their reciprocal sum.
    // Five hundred day-long periods exceed the 4096-bit accumulated bound.
    let primes: Vec<usize> = (2..5000)
        .filter(|candidate| {
            (2..)
                .take_while(|divisor| divisor * divisor <= *candidate)
                .all(|divisor| candidate % divisor != 0)
        })
        .take(500)
        .collect();
    assert_eq!(primes.len(), 500);
    let start = chrono::NaiveDate::from_ymd_opt(2026, 1, 1).unwrap();
    let mut input = base();
    let template = input["quotes"][0].clone();
    let ids: Vec<_> = (0..500).map(|index| format!("rate-{index:04}")).collect();
    input["quotes"] = Value::Array(
        primes
            .iter()
            .enumerate()
            .map(|(index, prime)| {
                let mut quote = template.clone();
                quote["id"] = json!(ids[index]);
                quote["amount"] = json!("1");
                quote["per_quantity"] = json!(prime.to_string());
                quote["valid_from"] =
                    json!((start + chrono::Duration::days(index as i64)).to_string());
                quote["valid_to"] =
                    json!((start + chrono::Duration::days(index as i64 + 1)).to_string());
                quote
            })
            .collect(),
    );
    let mut simple = input["interval_usage"][0].clone();
    simple["id"] = json!("z-simple");
    simple["use_id"] = json!("simple-use");
    simple["quantity"] = json!("1");
    simple["end_date"] = json!((start + chrono::Duration::days(1)).to_string());
    simple["quote_ids"] = json!([ids[0]]);
    let mut overflow = input["interval_usage"][0].clone();
    overflow["id"] = json!("a-overflow");
    overflow["use_id"] = json!("overflow-use");
    overflow["quantity"] = json!("500");
    overflow["end_date"] = json!((start + chrono::Duration::days(500)).to_string());
    overflow["quote_ids"] = json!(ids);
    input["interval_usage"] = json!([simple, overflow]);
    for expected in ["/interval_usage/1", "/interval_usage/0"] {
        let failure = error(&input);
        assert_eq!(failure.code, "precision_limit");
        assert_eq!(failure.path, expected);
        assert_eq!(input.pointer(&failure.path).unwrap()["id"], "a-overflow");
        input["interval_usage"].as_array_mut().unwrap().reverse();
    }
}

#[test]
fn typed_interval_api_matches_json_and_rejects_earlier_profile_versions() {
    let input = base();
    let typed: dapane_core::Request = serde_json::from_value(input.clone()).unwrap();
    let result = dapane_core::evaluate(&typed).unwrap();
    assert_eq!(serde_json::to_value(result).unwrap(), report(&input));
    for version in ["0.1", "0.2"] {
        let mut downgraded = typed.clone();
        downgraded.schema_version = version.to_owned();
        let failure = dapane_core::evaluate(&downgraded).unwrap_err();
        assert_eq!(failure.code, "invalid_request");
        assert_eq!(failure.path, "/interval_usage");
    }
}

#[test]
fn independent_duration_oracle_conserves_quantity_and_values_the_parent() {
    // One day before the change, N days after, total quantity (N+1)/7:
    // quantities are 1/7 and N/7; exact parent value is (90 + 120*N)/7.
    // Adapted from the independent duration case inspected in PR #16;
    // the rounded oracle here uses this contract's parent rounding.
    for days_after in 1..=25 {
        let mut input = base();
        input["quotes"][0]["amount"] = json!("90");
        input["quotes"][0]["valid_to"] = json!("2026-01-02");
        input["quotes"][1]["amount"] = json!("120");
        input["quotes"][1]["valid_from"] = json!("2026-01-02");
        input["quotes"][1]["valid_to"] = json!("2026-02-01");
        input["interval_usage"][0]["quantity"] = ratio(&(days_after + 1).to_string(), "7");
        input["interval_usage"][0]["end_date"] = json!(format!("2026-01-{:02}", days_after + 2));
        let output = report(&input);
        let line = &output["interval_lines"][0];
        assert_eq!(line["segments"][0]["quantity"], ratio("1", "7"));
        let after = &line["segments"][1]["quantity"];
        let after_numerator: i64 = after["numerator"].as_str().unwrap().parse().unwrap();
        let after_denominator: i64 = after["denominator"].as_str().unwrap().parse().unwrap();
        assert_eq!(after_numerator * 7, days_after * after_denominator);
        let total = &line["quantity"];
        let total_numerator: i64 = total["numerator"].as_str().unwrap().parse().unwrap();
        let total_denominator: i64 = total["denominator"].as_str().unwrap().parse().unwrap();
        assert_eq!(total_numerator * 7, (days_after + 1) * total_denominator);
        let exact = &output["totals"]["exact"];
        let numerator: i64 = exact["numerator"].as_str().unwrap().parse().unwrap();
        let denominator: i64 = exact["denominator"].as_str().unwrap().parse().unwrap();
        assert_eq!(numerator * 7, (90 + 120 * days_after) * denominator);
        // Sevenths cannot be half-cent ties. Adding three before integer
        // division by seven independently gives the nearest whole cent.
        let cents = ((90 + 120 * days_after) * 100 + 3) / 7;
        assert_eq!(
            output["totals"]["rounded"],
            format!("{}.{:02}", cents / 100, cents % 100)
        );
    }
}

#[test]
fn computed_segment_may_exceed_input_digits_within_the_intermediate_bound() {
    // A 96-digit input denominator D = 10^96 - 1 is permitted. Dividing
    // quantity 1/D across three days produces denominator 3D, which has
    // 97 decimal digits but is less than 2^323 and therefore well below
    // the 4096-bit computed-value limit. It is not a new scalar input.
    let mut input = base();
    input["interval_usage"][0]["quantity"] = ratio("1", &"9".repeat(96));
    input["interval_usage"][0]["end_date"] = json!("2026-01-04");
    input["quotes"][0]["valid_to"] = json!("2026-01-02");
    input["quotes"][1]["valid_from"] = json!("2026-01-02");
    let output = report(&input);
    let denominator = format!("2{}7", "9".repeat(95));
    assert_eq!(denominator.len(), 97);
    let line = &output["interval_lines"][0];
    assert_eq!(line["segments"][0]["quantity"], ratio("1", &denominator));
    assert_eq!(line["segments"][1]["quantity"], ratio("2", &denominator));
    // Rates are 2 and 3: (1/(3D))*2 + (2/(3D))*3 = 8/(3D).
    assert_eq!(line["exact"], ratio("8", &denominator));
    assert_eq!(output["totals"]["exact"], ratio("8", &denominator));
    assert_eq!(output["totals"]["rounded"], "0.00");
    assert_eq!(output["status"], "complete");
}
