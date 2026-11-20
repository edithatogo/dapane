//! Stream one synthetic fiscal request or evaluated report through the optional Rust adapter.
use std::env;
use std::error::Error;
use std::io::{self, Read, Write};
use std::process::ExitCode;

use dapane_decision_fiscal::fiscal::{
    evaluate_equity_json, evaluate_fiscal_json, export_perspective_table,
};

fn run() -> Result<(), Box<dyn Error>> {
    let mut args = env::args().skip(1);
    let operation = args
        .next()
        .ok_or("usage: dapane-fiscal evaluate|equity|export < input.json")?;
    if args.next().is_some() {
        return Err("expected one operation and JSON on stdin".into());
    }
    let (limit, transform): (u64, fn(&str) -> _) = match operation.as_str() {
        "evaluate" => (4 << 20, evaluate_fiscal_json),
        "equity" => (4 << 20, evaluate_equity_json),
        "export" => (16 << 20, export_perspective_table),
        _ => return Err("unknown operation; use evaluate, equity or export".into()),
    };
    let mut bytes = Vec::new();
    io::stdin().lock().take(limit + 1).read_to_end(&mut bytes)?;
    if bytes.len() as u64 > limit {
        return Err("input exceeds the operation's byte limit".into());
    }
    let output = transform(std::str::from_utf8(&bytes)?)?;
    writeln!(io::stdout().lock(), "{output}")?;
    Ok(())
}

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => {
            eprintln!("{error}");
            ExitCode::FAILURE
        }
    }
}
