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

Keep these versions synchronized:

- `pyproject.toml`: Python distribution version
- `Cargo.toml`: native extension version
- `src/dotenvx/__version__.py`: Python runtime version

Unlike npm, Python packaging has no built-in `npm version patch` equivalent.
Update all three files to the chosen semantic version before tagging.

The `dotenvx-primitives` dependency version in `Cargo.toml` is independent. It
should identify the crate release that this Python package embeds.

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

The tag version must match `pyproject.toml`, `Cargo.toml`, and
`src/dotenvx/__version__.py`.
