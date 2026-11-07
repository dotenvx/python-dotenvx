[![dotenvx](https://dotenvx.com/better-banner.png)](https://dotenvx.com)

*a better dotenv*–from the creator of [`dotenv`](https://github.com/motdotla/dotenv).

* run anywhere (cross-platform)
* multi-environment
* encrypted envs

&nbsp;


### Quickstart [![PyPI version](https://badge.fury.io/py/python-dotenvx.svg)](http://badge.fury.io/py/python-dotenvx)

Keep the familiar `load_dotenv()` entry point with dotenvx loading semantics.

```sh
pip install python-dotenvx
```

The wheel includes native dotenvx Rust primitives. No dotenvx executable or
post-install download is required.

```python
# main.py
import os
from dotenvx import load_dotenv

load_dotenv()  # take environment variables from .env

print(os.getenv("S3_BUCKET"))
```

You can also parse values without changing the environment:

```python
from dotenvx import dotenv_values

values = dotenv_values(".env")
```

Encrypted values are decrypted using `DOTENV_PRIVATE_KEY` from the environment
or a neighboring `.env.keys` file.

&nbsp;

### Loading errors and policy

The main entry points use the shared `dotenvx-ll` Rust loader. Errors are printed
to stderr and available values still load by default. Use `strict=True`, or set
strictness in the current directory's Dotenvxfile, to raise before changing
`os.environ`. Dotenvxfile required/type/file validation is shared with the CLI.
Ignore selected diagnostics with `ignore=["DECRYPTION_FAILED"]`.

The loader returns redaction metadata without changing application values;
the adapter does not install application-output redaction hooks.

### Deliberately smaller Python API

`load_dotenv()` and `dotenv_values()` accept an optional file path, or `stream=`
for text input. Loading supports `override=`, `strict=`, and `ignore=`. Options
after the file path are keyword-only. `load_dotenvx(path, override=False)` remains
available and returns the resolved mapping after loading it.

Parsing, expansion, UTF-8 file decoding, and local key discovery belong to the
shared Rust loader. Python no longer implements a second parser for bare keys
or rewrites dollar signs to disable interpolation. Bare keys without `=` are
ignored; use `KEY=` for an empty string. Single quotes preserve literal dollars.

The legacy `interpolate`, `encoding`, and `verbose` options, and the no-op
`find_dotenv(usecwd=...)` option, are no longer supported. `find_dotenv()` still
searches upward from the current directory.

### Shared file selection

The Rust loader owns file discovery, directory expansion, conventions, and
key-based filename inference. Pass one path or a list of paths; use
`convention="nextjs"` or `convention="flow"`, and `key_files="custom.keys"` when
needed. The same file-selection and error-ignore environment variables used by
the CLI are supported. `find_dotenv()` delegates upward searching to Rust.

```python
load_dotenv(convention="nextjs")
load_dotenv([".env.production", ".env"])
load_dotenv("app", key_files="shared/.env.keys")
```
