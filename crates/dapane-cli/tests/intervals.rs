use std::io::Write;
use std::path::PathBuf;
use std::process::{Command, Output, Stdio};

fn fixture() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../fixtures/intervals/rate-boundary.json")
}

fn stdin(input: &[u8]) -> Output {
    let mut child = Command::new(env!("CARGO_BIN_EXE_dapane"))
        .args(["evaluate-intervals", "-"])
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    child.stdin.take().unwrap().write_all(input).unwrap();
    child.wait_with_output().unwrap()
}

#[test]
fn interval_file_stdin_and_repeat_runs_have_identical_exact_output() {
    let file = Command::new(env!("CARGO_BIN_EXE_dapane"))
        .arg("evaluate-intervals")
        .arg(fixture())
        .output()
        .unwrap();
    assert!(
        file.status.success(),
        "{}",
        String::from_utf8_lossy(&file.stderr)
    );
    assert!(file.stderr.is_empty());
    let bytes = std::fs::read(fixture()).unwrap();
    for _ in 0..3 {
        let result = stdin(&bytes);
        assert!(result.status.success());
        assert_eq!(result.stdout, file.stdout);
        assert!(result.stderr.is_empty());
    }
    let result: serde_json::Value = serde_json::from_slice(&file.stdout).unwrap();
    assert_eq!(result["report"]["totals"]["rounded"], "110.00");
    assert_eq!(result["report"]["status"], "complete");
}

#[test]
fn interval_failures_emit_only_structured_errors() {
    let mut missing: serde_json::Value =
        serde_json::from_slice(&std::fs::read(fixture()).unwrap()).unwrap();
    missing["intervals"][0]["quote_ids"] = serde_json::json!(["before"]);
    for bytes in [
        b"{broken".to_vec(),
        missing.to_string().into_bytes(),
        vec![0xff],
    ] {
        let result = stdin(&bytes);
        assert!(!result.status.success());
        assert!(result.stdout.is_empty());
        let error: serde_json::Value = serde_json::from_slice(&result.stderr).unwrap();
        for key in ["code", "message", "path"] {
            assert!(error[key].is_string());
        }
    }
}
