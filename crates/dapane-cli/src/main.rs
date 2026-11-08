use std::env;
use std::fs::File;
use std::io::{self, Read};
use std::process::ExitCode;

const MAX_INPUT_BYTES: u64 = 4 * 1024 * 1024;
const HELP: &str = "Dapane: exact microcosting and valuation\n\nUsage:\n  dapane evaluate <request.json|->\n  dapane --version\n  dapane --help\n\nResults are JSON on stdout. Errors are JSON on stderr with a nonzero exit status.\nUse - to read a request from stdin. No network access or implicit date selection.\n";

fn read_request(mut input: impl Read) -> Result<String, String> {
    let mut bytes = Vec::new();
    input
        .by_ref()
        .take(MAX_INPUT_BYTES + 1)
        .read_to_end(&mut bytes)
        .map_err(|error| error.to_string())?;
    if bytes.len() as u64 > MAX_INPUT_BYTES {
        return Err("request exceeds the 4 MiB input limit".to_string());
    }
    String::from_utf8(bytes).map_err(|_| "request must be UTF-8 JSON".to_string())
}

fn fail(code: &str, message: &str, path: &str) -> ExitCode {
    eprintln!(
        "{}",
        serde_json::json!({"code": code, "message": message, "path": path})
    );
    ExitCode::FAILURE
}

fn main() -> ExitCode {
    let arguments: Vec<_> = env::args_os().skip(1).collect();
    if matches!(arguments.as_slice(), [flag] if flag == "--help" || flag == "-h") {
        print!("{HELP}");
        return ExitCode::SUCCESS;
    }
    if matches!(arguments.as_slice(), [flag] if flag == "--version" || flag == "-V") {
        println!("dapane {} (contract 0.1)", env!("CARGO_PKG_VERSION"));
        return ExitCode::SUCCESS;
    }
    let [command, path] = arguments.as_slice() else {
        return fail(
            "invalid_arguments",
            "use: dapane evaluate <request.json|->",
            "/arguments",
        );
    };
    if command != "evaluate" {
        return fail(
            "invalid_arguments",
            "unknown command; use --help",
            "/arguments/0",
        );
    }
    let request = if path == "-" {
        read_request(io::stdin().lock())
    } else {
        match File::open(path) {
            Ok(file) => read_request(file),
            Err(error) => Err(error.to_string()),
        }
    };
    let request = match request {
        Ok(request) => request,
        Err(message) => return fail("input_error", &message, "/input"),
    };
    match dapane_core::evaluate_json(&request) {
        Ok(report) => {
            println!("{report}");
            ExitCode::SUCCESS
        }
        Err(error) => {
            match serde_json::to_string(&error) {
                Ok(diagnostic) => eprintln!("{diagnostic}"),
                Err(_) => return fail("internal_error", "could not encode error", "/"),
            }
            ExitCode::FAILURE
        }
    }
}
