//! Python transport boundary. All valuation and allocation belongs to dapane-core.

use pyo3::exceptions::PyException;
use pyo3::prelude::*;

pyo3::create_exception!(
    _native,
    CoreError,
    PyException,
    "Private native error carrying the core's structured JSON diagnostic."
);

/// Evaluate an owned JSON request without holding Python's interpreter lock.
#[pyfunction]
fn evaluate_json(py: Python<'_>, request_json: String) -> PyResult<String> {
    let result =
        py.detach(move || std::panic::catch_unwind(|| dapane_core::evaluate_json(&request_json)));
    match result {
        Ok(Ok(report)) => Ok(report),
        Ok(Err(error)) => Err(CoreError::new_err(error.to_string())),
        Err(_) => Err(CoreError::new_err(
            r#"{"code":"internal_error","message":"The valuation engine failed unexpectedly.","path":"/"}"#,
        )),
    }
}

#[pymodule]
fn _native(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add("__version__", env!("CARGO_PKG_VERSION"))?;
    module.add("CoreError", module.py().get_type::<CoreError>())?;
    module.add_function(wrap_pyfunction!(evaluate_json, module)?)?;
    Ok(())
}
