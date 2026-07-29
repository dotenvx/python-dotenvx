# Development

`python-dotenvx` is a mixed Python/Rust project. Maturin compiles the PyO3
extension in `rust/lib.rs` and places it inside the `dotenvx` Python package.
The extension uses the published `dotenvx-primitives` crate.

## Local setup

```sh
python3 -m venv .venv
.venv/bin/python -m pip install maturin pytest
.venv/bin/maturin develop
.venv/bin/pytest
```

Build a wheel for the current platform:

```sh
.venv/bin/maturin build --release
```

The resulting wheel is written to `target/wheels`.

## Version changes

`Cargo.toml` is the single source of truth for the package version:

```toml
[package]
version = "2.0.1"
```

Maturin uses that value for the PyPI distribution because `pyproject.toml`
declares `version` as dynamic. At runtime, `dotenvx.__version__` reads the
installed distribution metadata. `Cargo.lock` is generated from
`Cargo.toml`.

After changing the version, refresh the lockfile:

```sh
cargo check
```

The `dotenvx-primitives` dependency version is independent. Change it only
when this package should embed a newer primitives release.

## Publishing

Git tags matching `v*` trigger wheel builds for Linux, macOS, and Windows and
publish the collected wheels to PyPI. Before tagging:

```sh
.venv/bin/maturin develop
.venv/bin/pytest
.venv/bin/maturin build --release
```

Then:

```sh
git tag v0.0.0
git push origin v0.0.0
```

The tag version must match `Cargo.toml`.
