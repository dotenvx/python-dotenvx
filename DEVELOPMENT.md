# Development

`python-dotenvx` is a mixed Python/Rust project. Maturin compiles the PyO3
extension in `rust/lib.rs` and places it inside the `dotenvx` Python package.
The extension uses the private `dotenvx-ll` loader, which depends on published
`dotenvx-primitives`.

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

The shared loader owns the `dotenvx-primitives` dependency version. Update it
in Forge when the consumers should embed a newer primitives release.

## Security audits

Audit Rust dependencies in `Cargo.lock` with RustSec:

```sh
cargo install cargo-audit --locked
cargo audit
```

Python's equivalent of `npm audit` is `pip-audit`:

```sh
python -m pip install pip-audit
pip-audit .
```

This project currently has no runtime Python dependencies, but `pip-audit`
should still be run whenever Python dependencies are added. Native dependencies
embedded in the wheel are covered by `cargo audit`, not `pip-audit`.

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

## Shared loader checkout

The native extension currently depends on private `dotenvx-ll` through a local
Cargo path. Keep this checkout beside `forge/`, which contains `dotenvx-ll/`.
It embeds published primitives 4.x through that loader, instead of depending on
primitives directly. Rebuild the extension after changing the loader.

These are local development paths, not a finished release-distribution setup.
Standalone CI/source-package builds need private access to the loader source
before publishing. Do not publish `dotenvx-ll` publicly; compiled platform gems
and wheels can embed it without distributing its Rust source.
