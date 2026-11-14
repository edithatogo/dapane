use std::io::Write;
use std::path::PathBuf;
use std::process::{Command, Stdio};

fn executable() -> Command {
    Command::new(env!("CARGO_BIN_EXE_dapane"))
}

fn fixture(name: &str) -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../../fixtures")
        .join(name)
}

#[test]
fn installed_protocol_accepts_files_and_stdin_with_identical_results() {
    let input = std::fs::read(fixture("workforce.json")).expect("reference fixture");
    let file = executable()
        .args(["evaluate", fixture("workforce.json").to_str().unwrap()])
        .output()
        .unwrap();
    assert!(
        file.status.success(),
        "{}",
        String::from_utf8_lossy(&file.stderr)
    );
    assert!(file.stderr.is_empty());
    let mut stdin = executable()
        .args(["evaluate", "-"])
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    stdin.stdin.take().unwrap().write_all(&input).unwrap();
    let stdin = stdin.wait_with_output().unwrap();
    assert!(stdin.status.success());
    assert_eq!(file.stdout, stdin.stdout);
    let report: serde_json::Value = serde_json::from_slice(&stdin.stdout).unwrap();
    assert_eq!(report["totals"]["rounded"], "30.00");
    assert_eq!(report["status"], "complete");
}

#[test]
fn malformed_input_has_no_financial_stdout_and_a_structured_failure() {
    let mut child = executable()
        .args(["evaluate", "-"])
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    child.stdin.take().unwrap().write_all(b"{broken").unwrap();
    let output = child.wait_with_output().unwrap();
    assert!(!output.status.success());
    assert!(output.stdout.is_empty());
    let error: serde_json::Value = serde_json::from_slice(&output.stderr).unwrap();
    for field in ["code", "message", "path"] {
        assert!(error[field].is_string());
    }
}

#[test]
fn capacity_cli_preserves_unknown_shares_and_rejects_silent_downgrades() {
    let path = fixture("genomics-capacity/time-missing-use.json");
    let output = executable().arg("evaluate").arg(&path).output().unwrap();
    assert!(output.status.success());
    assert!(output.stderr.is_empty());
    let report: serde_json::Value = serde_json::from_slice(&output.stdout).unwrap();
    assert_eq!(report["schema_version"], "0.2");
    assert_eq!(report["capacity_allocations"][0]["unallocated"], "270.00");
    assert!(report["capacity_allocations"][0]["shares"][1]["rounded"].is_null());
    let mut request: serde_json::Value =
        serde_json::from_slice(&std::fs::read(path).unwrap()).unwrap();
    request["schema_version"] = serde_json::json!("0.1");
    let mut child = executable()
        .args(["evaluate", "-"])
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(request.to_string().as_bytes())
        .unwrap();
    let rejected = child.wait_with_output().unwrap();
    assert!(!rejected.status.success());
    assert!(rejected.stdout.is_empty());
    let error: serde_json::Value = serde_json::from_slice(&rejected.stderr).unwrap();
    assert_eq!(error["code"], "invalid_request");
}

#[test]
fn invalid_arguments_and_missing_files_fail_without_panicking() {
    for arguments in [
        vec![],
        vec!["unknown"],
        vec!["evaluate", "/definitely-absent-dapane-input.json"],
    ] {
        let output = executable().args(arguments).output().unwrap();
        assert!(!output.status.success());
        assert!(output.stdout.is_empty());
        let error: serde_json::Value = serde_json::from_slice(&output.stderr).unwrap();
        assert!(error["code"].is_string());
    }
}

#[test]
fn help_and_version_do_not_require_a_request() {
    for flag in ["--help", "--version"] {
        let output = executable().arg(flag).output().unwrap();
        assert!(output.status.success());
        assert!(output.stderr.is_empty());
        assert!(!output.stdout.is_empty());
    }
}

#[cfg(unix)]
#[test]
fn non_utf8_arguments_do_not_panic_and_file_paths_remain_usable() {
    use std::ffi::OsString;
    use std::os::unix::ffi::OsStringExt;

    let invalid_command = executable()
        .arg(OsString::from_vec(vec![0xff]))
        .output()
        .unwrap();
    assert!(!invalid_command.status.success());
    let error: serde_json::Value = serde_json::from_slice(&invalid_command.stderr).unwrap();
    assert_eq!(error["code"], "invalid_arguments");
    assert!(invalid_command.stdout.is_empty());

    let mut name = format!("dapane-cli-fixture-{}-", std::process::id()).into_bytes();
    name.extend_from_slice(&[0xff, b'.', b'j', b's', b'o', b'n']);
    let path = std::env::temp_dir().join(OsString::from_vec(name));
    let mut file = std::fs::OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&path)
        .unwrap();
    file.write_all(&std::fs::read(fixture("workforce.json")).unwrap())
        .unwrap();
    drop(file);
    let result = executable().arg("evaluate").arg(&path).output().unwrap();
    std::fs::remove_file(&path).unwrap();
    assert!(result.status.success());
    assert!(result.stderr.is_empty());
    let report: serde_json::Value = serde_json::from_slice(&result.stdout).unwrap();
    assert_eq!(report["totals"]["rounded"], "30.00");
}
