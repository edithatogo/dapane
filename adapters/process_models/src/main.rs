//! CLI entry point for the X2 bounded PNML and BPMN process-model adapters.

use std::collections::BTreeMap;
use std::env;
use std::fs;
use std::process::ExitCode;

use dapane_process_models::bpmn::{
    BPMN_CORE_PROFILE_ID, BpmnProfile, execute_bpmn, parse_bpmn_bytes, parse_bpmn_config,
};
use dapane_process_models::json_io::{JsonValue, parse_json_bytes};
use dapane_process_models::model::{
    CONTRACT_VERSION, ErrorCode, ExecutionTrace, ModelError, ValuationAttachment,
    project_to_dapane_request,
};
use dapane_process_models::pnml::{
    PNML_PROFILE_ID, execute_petri_net, parse_pnml_bytes, parse_pnml_config,
};

fn read_bytes(path: &str) -> Result<Vec<u8>, ModelError> {
    fs::read(path).map_err(|exc| {
        ModelError::new(
            ErrorCode::MalformedJson,
            path,
            format!("Unable to read `{path}`: {exc}"),
        )
    })
}

fn validate_pnml_cmd(args: &[String]) -> Result<JsonValue, ModelError> {
    if args.len() != 1 {
        return Err(ModelError::new(
            ErrorCode::MalformedJson,
            "/cli",
            "Usage: validate-pnml <pnml_path>",
        ));
    }
    let net = parse_pnml_bytes(&read_bytes(&args[0])?)?;
    let mut obj = BTreeMap::new();
    obj.insert(
        "arcs".to_owned(),
        JsonValue::Number(net.arcs.len().to_string()),
    );
    obj.insert(
        "contract_version".to_owned(),
        JsonValue::String(CONTRACT_VERSION.to_owned()),
    );
    obj.insert("model_id".to_owned(), JsonValue::String(net.id));
    obj.insert(
        "model_sha256".to_owned(),
        JsonValue::String(net.model_sha256),
    );
    obj.insert(
        "places".to_owned(),
        JsonValue::Number(net.places.len().to_string()),
    );
    obj.insert(
        "profile_id".to_owned(),
        JsonValue::String(PNML_PROFILE_ID.to_owned()),
    );
    obj.insert(
        "transitions".to_owned(),
        JsonValue::Number(net.transitions.len().to_string()),
    );
    obj.insert("valid".to_owned(), JsonValue::Bool(true));
    Ok(JsonValue::Object(obj))
}

fn validate_bpmn_cmd(args: &[String]) -> Result<JsonValue, ModelError> {
    let (model_path, profile_raw) = match args {
        [p] => (p.as_str(), BPMN_CORE_PROFILE_ID),
        [p, flag, val] if flag == "--profile" => (p.as_str(), val.as_str()),
        _ => {
            return Err(ModelError::new(
                ErrorCode::MalformedJson,
                "/cli",
                "Usage: validate-bpmn <bpmn_path> [--profile <profile_id>]",
            ));
        }
    };
    let profile = BpmnProfile::parse(profile_raw, "/cli/profile")?;
    let model = parse_bpmn_bytes(&read_bytes(model_path)?, profile)?;
    let mut obj = BTreeMap::new();
    obj.insert(
        "contract_version".to_owned(),
        JsonValue::String(CONTRACT_VERSION.to_owned()),
    );
    obj.insert(
        "flows".to_owned(),
        JsonValue::Number(model.process.flows.len().to_string()),
    );
    obj.insert("model_id".to_owned(), JsonValue::String(model.process.id));
    obj.insert(
        "model_sha256".to_owned(),
        JsonValue::String(model.model_sha256),
    );
    obj.insert(
        "nodes".to_owned(),
        JsonValue::Number(model.process.nodes.len().to_string()),
    );
    obj.insert(
        "profile_id".to_owned(),
        JsonValue::String(profile.as_str().to_owned()),
    );
    obj.insert("valid".to_owned(), JsonValue::Bool(true));
    Ok(JsonValue::Object(obj))
}

fn execute_pnml_cmd(args: &[String]) -> Result<JsonValue, ModelError> {
    if args.len() != 2 {
        return Err(ModelError::new(
            ErrorCode::MalformedJson,
            "/cli",
            "Usage: execute-pnml <pnml_path> <config_json_path>",
        ));
    }
    let net = parse_pnml_bytes(&read_bytes(&args[0])?)?;
    let cfg = parse_pnml_config(&read_bytes(&args[1])?)?;
    let trace = execute_petri_net(&net, &cfg)?;
    Ok(trace.to_json())
}

fn execute_bpmn_cmd(args: &[String]) -> Result<JsonValue, ModelError> {
    if args.len() != 2 {
        return Err(ModelError::new(
            ErrorCode::MalformedJson,
            "/cli",
            "Usage: execute-bpmn <bpmn_path> <config_json_path>",
        ));
    }
    let cfg = parse_bpmn_config(&read_bytes(&args[1])?)?;
    let model = parse_bpmn_bytes(&read_bytes(&args[0])?, cfg.profile)?;
    let trace = execute_bpmn(&model, &cfg)?;
    Ok(trace.to_json())
}

fn project_dapane_cmd(args: &[String]) -> Result<JsonValue, ModelError> {
    if args.len() != 2 {
        return Err(ModelError::new(
            ErrorCode::MalformedJson,
            "/cli",
            "Usage: project-dapane <trace_json_path> <valuation_json_path>",
        ));
    }
    let trace_json = parse_json_bytes(&read_bytes(&args[0])?)?;
    let val_json = parse_json_bytes(&read_bytes(&args[1])?)?;
    let trace = ExecutionTrace::from_json(&trace_json)?;
    let valuation = ValuationAttachment::from_json(&val_json)?;
    project_to_dapane_request(&trace, &valuation)
}

fn run() -> Result<JsonValue, ModelError> {
    let args: Vec<String> = env::args().skip(1).collect();
    let Some((sub, rest)) = args.split_first() else {
        return Err(ModelError::new(
            ErrorCode::MalformedJson,
            "/cli",
            "Expected subcommand: validate-pnml | validate-bpmn | execute-pnml | execute-bpmn | project-dapane",
        ));
    };
    match sub.as_str() {
        "validate-pnml" => validate_pnml_cmd(rest),
        "validate-bpmn" => validate_bpmn_cmd(rest),
        "execute-pnml" => execute_pnml_cmd(rest),
        "execute-bpmn" => execute_bpmn_cmd(rest),
        "project-dapane" => project_dapane_cmd(rest),
        other => Err(ModelError::new(
            ErrorCode::MalformedJson,
            "/cli",
            format!("Unknown subcommand `{other}`"),
        )),
    }
}

fn main() -> ExitCode {
    match run() {
        Ok(val) => {
            print!("{}", val.to_pretty_string());
            ExitCode::SUCCESS
        }
        Err(err) => {
            eprint!("{}", err.to_json().to_pretty_string());
            ExitCode::from(1)
        }
    }
}
