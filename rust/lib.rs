use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;

#[pyfunction]
fn load_env(input_json: &str) -> PyResult<String> {
    let options = serde_json::from_str::<dotenvx_ll::LoadOptions>(input_json)
        .map_err(|error| PyRuntimeError::new_err(error.to_string()))?;
    serde_json::to_string(&dotenvx_ll::load(&options))
        .map_err(|error| PyRuntimeError::new_err(error.to_string()))
}

#[pyfunction]
fn find_file(cwd: &str, filename: &str) -> String {
    dotenvx_ll::find_file(std::path::Path::new(cwd), filename)
        .map(|path| path.to_string_lossy().into_owned())
        .unwrap_or_default()
}

#[pymodule]
fn _native(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(load_env, module)?)?;
    module.add_function(wrap_pyfunction!(find_file, module)?)?;
    Ok(())
}
