use dotenvx_primitives::{parse, ParseOptions, ParseResult};
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use std::collections::HashMap;
use std::path::PathBuf;

type StringMap = HashMap<String, String>;
const INTERPOLATION_SENTINEL: &str = "\u{e000}";

fn restore_interpolation(values: StringMap, interpolate: bool) -> StringMap {
    if interpolate {
        return values;
    }
    values
        .into_iter()
        .map(|(key, value)| (key, value.replace(INTERPOLATION_SENTINEL, "$")))
        .collect()
}

fn parse_result(result: ParseResult, interpolate: bool) -> PyResult<(StringMap, StringMap)> {
    if !result.errors.is_empty() {
        let message = result
            .errors
            .iter()
            .map(ToString::to_string)
            .collect::<Vec<_>>()
            .join("\n");
        return Err(PyRuntimeError::new_err(message));
    }

    Ok((
        restore_interpolation(result.parsed, interpolate),
        restore_interpolation(result.injected, interpolate),
    ))
}

#[pyfunction]
#[pyo3(signature = (
    source,
    process_env=None,
    override_=false,
    key_files=None,
    interpolate=true
))]
fn parse_dotenv(
    source: &str,
    process_env: Option<StringMap>,
    override_: bool,
    key_files: Option<Vec<String>>,
    interpolate: bool,
) -> PyResult<(StringMap, StringMap)> {
    let process_env = process_env.unwrap_or_default();
    let source = if interpolate {
        source.to_owned()
    } else {
        source.replace('$', INTERPOLATION_SENTINEL)
    };

    parse_result(
        parse(
            &source,
            &ParseOptions {
                process_env,
                overload: override_,
                key_files: key_files
                    .unwrap_or_default()
                    .into_iter()
                    .map(PathBuf::from)
                    .collect(),
                ..Default::default()
            },
        ),
        interpolate,
    )
}

#[pymodule]
fn _native(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(parse_dotenv, module)?)?;
    Ok(())
}
