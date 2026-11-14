use std::io::Write;
use std::process::{Command, Output, Stdio};

use serde_json::{Value, json};

fn request() -> Value {
    let source = json!({"id":"cli-interval-fixture","version":"1","evidence":"synthetic",
        "access":"public","validation":"unvalidated"});
    let old = json!({"id":"old","kind":"activity_measure","target":"weighted_activity",
        "unit":"weighted_unit","amount":"17.00","per_quantity":"1","currency":"AUD",
        "price_year":2026,"basis":"funding","components":["funding"],
        "valid_from":"2026-01-01","valid_to":"2026-01-03","known_from":"2025-12-01",
        "source":source});
    let mut new = old.clone();
    new["id"] = json!("new");
    new["valid_from"] = json!("2026-01-03");
    new["valid_to"] = json!("2026-01-05");
    json!({"schema_version":"0.3","run_id":"cli-interval-run","knowledge_cutoff":"2026-11-08",
        "policy":{"id":"funding","version":"1","currency":"AUD","price_year":2026,
            "perspective":"funder","basis":"funding","rounding":{"scale":2,"mode":"half_even"}},
        "quotes":[old,new],"usage":[],
        "interval_usage":[{"id":"activity-line","use_id":"activity-use","kind":"activity_measure",
            "target":"weighted_activity","unit":"weighted_unit","quantity":"2.50",
            "start_date":"2026-01-01","end_date":"2026-01-05","exposure":"uniform_calendar_days",
            "quote_ids":["old","new"],"source":source}]})
}

fn evaluate(input: &str) -> Output {
    let mut process = Command::new(env!("CARGO_BIN_EXE_dapane"))
        .args(["evaluate", "-"])
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    process
        .stdin
        .take()
        .unwrap()
        .write_all(input.as_bytes())
        .unwrap();
    process.wait_with_output().unwrap()
}

#[test]
fn interval_funding_round_trips_exactly_and_repeats_without_resource_use() {
    let input = request().to_string();
    let first = evaluate(&input);
    assert!(
        first.status.success(),
        "{}",
        String::from_utf8_lossy(&first.stderr)
    );
    assert!(first.stderr.is_empty());
    let second = evaluate(&input);
    assert!(second.status.success());
    assert_eq!(first.stdout, second.stdout);
    let report: Value = serde_json::from_slice(&first.stdout).unwrap();
    assert_eq!(report["schema_version"], "0.3");
    assert_eq!(report["status"], "complete");
    assert_eq!(report["totals"]["rounded"], "42.50");
    assert_eq!(
        report["totals"]["exact"],
        json!({"numerator":"85","denominator":"2"})
    );
    assert_eq!(report["lines"], json!([]));
    assert_eq!(report["interval_lines"][0]["kind"], "activity_measure");
    assert_eq!(
        report["interval_lines"][0]["segments"]
            .as_array()
            .unwrap()
            .len(),
        2
    );
}

#[test]
fn interval_errors_never_publish_partial_financial_stdout() {
    for (value, expected) in [
        ("2026-01-04", "interval_gap"),
        ("2026-01-02", "interval_overlap"),
    ] {
        let mut input = request();
        input["quotes"][1]["valid_from"] = json!(value);
        let result = evaluate(&input.to_string());
        assert!(!result.status.success());
        assert!(result.stdout.is_empty());
        let error: Value = serde_json::from_slice(&result.stderr).unwrap();
        assert_eq!(error["code"], expected);
        assert!(error["message"].is_string());
        assert!(error["path"].as_str().unwrap().starts_with('/'));
    }
}

#[test]
fn interval_file_and_stdin_paths_produce_identical_exact_reports() {
    let input = request().to_string();
    let path =
        std::env::temp_dir().join(format!("dapane-interval-cli-{}.json", std::process::id()));
    let mut file = std::fs::OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&path)
        .unwrap();
    file.write_all(input.as_bytes()).unwrap();
    drop(file);
    let from_file = Command::new(env!("CARGO_BIN_EXE_dapane"))
        .arg("evaluate")
        .arg(&path)
        .output()
        .unwrap();
    std::fs::remove_file(&path).unwrap();
    assert!(from_file.status.success());
    assert!(from_file.stderr.is_empty());
    let from_stdin = evaluate(&input);
    assert!(from_stdin.status.success());
    assert_eq!(from_file.stdout, from_stdin.stdout);
}

#[test]
fn old_versions_reject_interval_data_without_silent_field_loss() {
    for version in ["0.1", "0.2"] {
        let mut input = request();
        input["schema_version"] = json!(version);
        let result = evaluate(&input.to_string());
        assert!(!result.status.success());
        assert!(result.stdout.is_empty());
        let error: Value = serde_json::from_slice(&result.stderr).unwrap();
        assert_eq!(error["code"], "invalid_request");
    }
}
