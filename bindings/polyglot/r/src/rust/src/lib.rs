//! Direct Rust calls for R. No numerical operations or cross-host dependencies.
//!
//! extendr owns temporary R objects. Owned Rust input and output strings stay
//! within each synchronous call on the R main thread; no R handle is retained.

use dapane_core::DapaneError;
use extendr_api::prelude::*;

#[cfg(not(panic = "unwind"))]
compile_error!("dapane-r requires panic=unwind to contain Rust panics");

fn evaluate_owned(
    input: &str,
    evaluate: fn(&str) -> std::result::Result<String, DapaneError>,
) -> std::result::Result<String, DapaneError> {
    std::panic::catch_unwind(|| evaluate(input)).unwrap_or_else(|_| {
        Err(DapaneError::new(
            "internal_error",
            "The valuation engine failed unexpectedly.",
            "/",
        ))
    })
}

fn transport(
    request: Robj,
    evaluate: fn(&str) -> std::result::Result<String, DapaneError>,
) -> List {
    // Keep native entry points defensive even if an R caller bypasses R helpers.
    let result = String::try_from(&request)
        .map_err(|_| {
            DapaneError::new(
                "invalid_host_input",
                "Expected one non-missing JSON string.",
                "/",
            )
        })
        .and_then(|input| evaluate_owned(&input, evaluate));
    match result {
        Ok(json) => list!(ok = true, json = json, code = "", message = "", path = ""),
        Err(error) => list!(
            ok = false,
            json = error.to_string(),
            code = error.code,
            message = error.message,
            path = error.path
        ),
    }
}

/// Internal registered entry point; R converts the structured result to a condition.
#[extendr]
fn evaluate_json_native(request: Robj) -> List {
    transport(request, dapane_core::evaluate_json)
}

/// Internal interval entry point; retains the kernel's method and rounding points.
#[extendr]
fn evaluate_intervals_json_native(request: Robj) -> List {
    transport(request, dapane_core::evaluate_intervals_json)
}

extendr_module! {
    mod dapaneR;
    fn evaluate_json_native;
    fn evaluate_intervals_json_native;
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn core_panic_becomes_error_without_a_partial_result() {
        let error = evaluate_owned("{}", |_| panic!("synthetic panic")).unwrap_err();
        assert_eq!(error.code, "internal_error");
        assert_eq!(error.path, "/");
        assert!(!error.message.contains("synthetic"));
    }
}
