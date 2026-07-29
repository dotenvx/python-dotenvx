use dotenvx_primitives::{keyring, parse, KeyringOptions, ParseOptions, ParseResult, Value};
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use std::collections::HashMap;
use std::path::PathBuf;

type StringMap = HashMap<String, String>;

fn scalar_values(values: HashMap<String, Value>) -> StringMap {
    values
        .into_iter()
        .filter_map(|(key, value)| match value {
            Value::Scalar(value) => Some((key, value)),
            Value::Array(_) => None,
        })
        .collect()
}

fn parse_result(result: ParseResult) -> PyResult<(StringMap, StringMap)> {
    if !result.errors.is_empty() {
        let message = result
            .errors
            .iter()
            .map(ToString::to_string)
            .collect::<Vec<_>>()
            .join("\n");
        return Err(PyRuntimeError::new_err(message));
    }

    Ok((scalar_values(result.parsed), scalar_values(result.injected)))
}

#[pyfunction]
#[pyo3(signature = (source, process_env=None, override_=false, key_files=None))]
fn parse_dotenv(
    source: &str,
    process_env: Option<StringMap>,
    override_: bool,
    key_files: Option<Vec<String>>,
) -> PyResult<(StringMap, StringMap)> {
    let process_env = process_env.unwrap_or_default();
    let ring = keyring(&KeyringOptions {
        process_env: process_env.clone(),
        key_files: key_files
            .unwrap_or_default()
            .into_iter()
            .map(PathBuf::from)
            .collect(),
        ..Default::default()
    })
    .map_err(|error| PyRuntimeError::new_err(error.to_string()))?;

    parse_result(parse(
        source,
        &ParseOptions {
            process_env,
            overload: override_,
            ring,
            ..Default::default()
        },
    ))
}

#[pymodule]
fn _native(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(parse_dotenv, module)?)?;
    Ok(())
}
