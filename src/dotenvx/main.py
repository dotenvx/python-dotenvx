import json
import os
import sys
from typing import Dict, Optional, Sequence, TextIO, Union

from ._native import find_file, load_env
from ._output import redact_stdout

StrPath = Union[str, os.PathLike]
PathInput = Union[StrPath, Sequence[StrPath]]
Values = Dict[str, str]


def find_dotenv(
        filename: str = ".env",
        raise_error_if_not_found: bool = False
) -> str:
    """Find ``filename`` by walking from the current directory toward root."""
    path = find_file(os.getcwd(), os.fspath(filename))
    if not path and raise_error_if_not_found:
        raise IOError("File not found")
    return path


def _paths(value):
    if value is None:
        return []
    values = [value] if isinstance(value, (str, os.PathLike)) else value
    return [os.fspath(path) for path in values]


def _load(dotenv_path=None, *, stream=None, override=False, strict=False,
          ignore=(), convention=None, key_files=None, resolve_references=False):
    if stream is not None:
        sources = [{"type": "inline", "value": stream.read()}]
    else:
        sources = [{"type": "file", "value": path} for path in _paths(dotenv_path)]
    result = json.loads(load_env(json.dumps({
        "sources": sources,
        "implicit_files": stream is None,
        "search_upwards": True,
        "convention": convention,
        "key_files": None if key_files is None else _paths(key_files),
        "cwd": os.getcwd(),
        "process_env": dict(os.environ),
        "overload": override,
        "strict": strict,
        "ignore": [ignore] if isinstance(ignore, str) else list(ignore),
        "adjacent_keys": True,
        "resolve_references": resolve_references,
    })))
    for error in result["diagnostics"]:
        if error["strict"]:
            raise RuntimeError(error["message"])
        print("☠ " + error["message"], file=sys.stderr)
    return result


def dotenv_values(
        dotenv_path: Optional[PathInput] = None,
        *, stream: Optional[TextIO] = None,
        strict: bool = False,
        ignore=(),
        convention: Optional[str] = None,
        key_files=None,
        resolve_references: bool = False
) -> Values:
    """Load resolved values without changing ``os.environ``."""
    return _load(dotenv_path, stream=stream, override=True,
                 strict=strict, ignore=ignore, convention=convention, key_files=key_files,
                 resolve_references=resolve_references)["values"]


def _disabled():
    return os.environ.get("PYTHON_DOTENV_DISABLED", "").lower() in {
        "1", "true", "t", "yes", "y"
    }


def load_dotenv(
        dotenv_path: Optional[PathInput] = None,
        *, stream: Optional[TextIO] = None,
        override: bool = False,
        strict: bool = False,
        ignore=(),
        convention: Optional[str] = None,
        key_files=None,
        resolve_references: bool = False
) -> bool:
    """Load values into ``os.environ`` using the shared Rust loader."""
    if _disabled():
        return False
    result = _load(dotenv_path, stream=stream, override=override,
                   strict=strict, ignore=ignore, convention=convention, key_files=key_files,
                   resolve_references=resolve_references)
    os.environ.update(result["injected"])
    redact_stdout(result["secrets"])
    if result["inject_summary"] is not None:
        print(result["inject_summary"], file=sys.stderr)
    return bool(result["values"])


def load_dotenvx(
        dotenv_path: Optional[PathInput] = None,
        override: bool = False,
        *, strict: bool = False, ignore=(), convention=None, key_files=None,
        resolve_references: bool = False
) -> Values:
    """Load into ``os.environ`` and return the resolved values."""
    if _disabled():
        return {}
    result = _load(dotenv_path, override=override, strict=strict, ignore=ignore,
                   convention=convention, key_files=key_files,
                   resolve_references=resolve_references)
    os.environ.update(result["injected"])
    redact_stdout(result["secrets"])
    if result["inject_summary"] is not None:
        print(result["inject_summary"], file=sys.stderr)
    return result["values"]
