# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

## [Unreleased](https://github.com/dotenvx/python-dotenvx/compare/v2.0.0...main)

## [2.0.0](https://github.com/dotenvx/python-dotenvx/compare/v0.3.0...v2.0.0)

### Added

- Add `load_dotenv`, `dotenv_values`, and `find_dotenv` with the same public
  arguments and defaults as `python-dotenv`.
- Add native dotenv parsing, expansion, command substitution, and decryption
  through `dotenvx-primitives` 2.1.1.
- Add automatic decryption using `DOTENV_PRIVATE_KEY` environment variables
  or a neighboring `.env.keys` file.
- Add conformance tests against `python-dotenv` 1.2.2, plus dotenvx encrypted
  loading behavior.

### Changed

- Package the Rust implementation as a PyO3 native extension inside each
  Python wheel.
- Build and publish Linux, macOS, and Windows wheels using Maturin.
- Use Python ABI3 wheels compatible with CPython 3.8 and newer.
- Keep `load_dotenvx` as a backward-compatible API returning parsed values.

### Removed

- Remove the `dotenvx-postinstall` command and runtime dotenvx CLI download.
- Remove the external dotenvx executable dependency.
- Remove the legacy setuptools build configuration.

## [0.3.0](https://github.com/dotenvx/dotenvx/compare/v0.2.6...v0.3.0)

### Added

* Add `dotenv_path` and `override` arguments ([#4](https://github.com/dotenvx/python-dotenvx/pull/4))

## [0.2.6](https://github.com/dotenvx/dotenvx/compare/v0.2.5...v0.2.6)

### Changed

* Add force to the binary install

## [0.2.5](https://github.com/dotenvx/dotenvx/compare/v0.2.4...v0.2.5)

### Added

* Add additional bin/* candidate to check for dotenvx binary

## [0.2.4](https://github.com/dotenvx/dotenvx/compare/v0.2.3...v0.2.4)

### Added

* Add the ability to specify the `os` and `arch` on `dotenvx-postinstall`

## [0.2.3](https://github.com/dotenvx/dotenvx/compare/v0.2.2...v0.2.3)

### Changed

* Patch `dotenvx` binary install across multiple edge cases

## [0.2.2](https://github.com/dotenvx/dotenvx/compare/v0.2.1...v0.2.2)

### Changed

* Adjust installation of `dotenvx` binary on demand

## [0.2.1](https://github.com/dotenvx/dotenvx/compare/v0.2.1...v0.2.1)

### Added

* Install the `dotenvx` binary on install of the python package

## 0.2.0

Please see commit history.
