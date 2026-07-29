import os
import re
from pathlib import Path
from typing import Dict, List, Optional, TextIO, Tuple, Union

from ._native import parse_dotenv

StrPath = Union[str, os.PathLike]
Values = Dict[str, Optional[str]]


def find_dotenv(
        filename: str = ".env",
        raise_error_if_not_found: bool = False,
        usecwd: bool = False
) -> str:
    """Find ``filename`` by walking from the current directory toward root."""
    del usecwd  # The package intentionally uses cwd for predictable discovery.
    directory = Path.cwd()

    for candidate_directory in (directory, *directory.parents):
        candidate = candidate_directory / filename
        if candidate.is_file():
            return str(candidate)

    if raise_error_if_not_found:
        raise IOError("File not found")
    return ""


def _source(
        dotenv_path: Optional[StrPath],
        stream: Optional[TextIO],
        encoding: Optional[str]
) -> Tuple[str, Optional[Path]]:
    if stream is not None:
        return stream.read(), None

    path = Path(dotenv_path) if dotenv_path is not None else Path(find_dotenv())
    if not str(path) or not path.is_file():
        return "", None
    return path.read_text(encoding=encoding or "utf-8"), path


def _key_files(path: Optional[Path]) -> List[str]:
    if path is None:
        return []

    candidates = [path.with_name(f"{path.name}.keys")]
    if path.name != ".env":
        candidates.append(path.with_name(".env.keys"))
    return [str(candidate) for candidate in candidates if candidate.is_file()]


def _parse(
        dotenv_path: Optional[StrPath] = None,
        stream: Optional[TextIO] = None,
        override: bool = False,
        interpolate: bool = True,
        encoding: Optional[str] = "utf-8"
) -> Tuple[Values, Dict[str, str], bool]:
    source, path = _source(dotenv_path, stream, encoding)
    if path is None and not source:
        return {}, {}, False

    parsed, injected = parse_dotenv(
        source,
        dict(os.environ),
        override,
        _key_files(path),
        interpolate,
    )
    has_values = bool(parsed)
    for key in _bare_keys(source):
        parsed.setdefault(key, None)
    return parsed, injected, has_values


def _bare_keys(source: str) -> List[str]:
    pattern = re.compile(
        r"^([A-Za-z_][A-Za-z0-9_.-]*)\s*(?:#.*)?$"
    )
    keys = []
    multiline_quote = None

    for raw_line in source.splitlines():
        if multiline_quote is not None:
            if _has_unescaped_quote(raw_line, multiline_quote):
                multiline_quote = None
            continue

        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()

        if "=" in line:
            value = line.split("=", 1)[1].lstrip()
            if value[:1] in {"'", '"', "`"}:
                quote = value[0]
                if not _has_unescaped_quote(value[1:], quote):
                    multiline_quote = quote
            continue

        match = pattern.fullmatch(line)
        if match:
            keys.append(match.group(1))

    return keys


def _has_unescaped_quote(value: str, quote: str) -> bool:
    escaped = False
    for character in value:
        if character == quote and not escaped:
            return True
        if character == "\\":
            escaped = not escaped
        else:
            escaped = False
    return False


def dotenv_values(
        dotenv_path: Optional[StrPath] = None,
        stream: Optional[TextIO] = None,
        verbose: bool = False,
        interpolate: bool = True,
        encoding: Optional[str] = "utf-8"
) -> Values:
    """Parse a dotenv source without changing ``os.environ``."""
    del verbose
    parsed, _, _ = _parse(
        dotenv_path=dotenv_path,
        stream=stream,
        override=True,
        interpolate=interpolate,
        encoding=encoding,
    )
    return parsed


def load_dotenv(
        dotenv_path: Optional[StrPath] = None,
        stream: Optional[TextIO] = None,
        verbose: bool = False,
        override: bool = False,
        interpolate: bool = True,
        encoding: Optional[str] = "utf-8"
) -> bool:
    """Load dotenv values into ``os.environ`` using native Rust primitives."""
    del verbose

    if os.environ.get("PYTHON_DOTENV_DISABLED", "").lower() in {
        "1", "true", "t", "yes", "y"
    }:
        return False

    _, injected, found = _parse(
        dotenv_path=dotenv_path,
        stream=stream,
        override=override,
        interpolate=interpolate,
        encoding=encoding,
    )
    os.environ.update(injected)
    return found


def load_dotenvx(
        dotenv_path: Optional[StrPath] = None,
        override: bool = False
) -> Values:
    """Backward-compatible dotenvx loader returning the parsed mapping."""
    parsed, injected, _ = _parse(
        dotenv_path=dotenv_path,
        override=override,
    )
    os.environ.update(injected)
    return parsed
