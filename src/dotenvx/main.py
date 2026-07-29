import os
from pathlib import Path
from typing import Dict, List, Optional, TextIO, Tuple, Union

from ._native import parse_dotenv

StrPath = Union[str, os.PathLike]


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
        encoding: Optional[str] = "utf-8"
) -> Tuple[Dict[str, str], Dict[str, str], bool]:
    source, path = _source(dotenv_path, stream, encoding)
    if path is None and not source:
        return {}, {}, False

    parsed, injected = parse_dotenv(
        source,
        dict(os.environ),
        override,
        _key_files(path),
    )
    return parsed, injected, bool(parsed)


def dotenv_values(
        dotenv_path: Optional[StrPath] = None,
        stream: Optional[TextIO] = None,
        verbose: bool = False,
        interpolate: bool = True,
        encoding: Optional[str] = "utf-8"
) -> Dict[str, str]:
    """Parse a dotenv source without changing ``os.environ``."""
    del verbose, interpolate
    parsed, _, _ = _parse(
        dotenv_path=dotenv_path,
        stream=stream,
        override=True,
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
    del verbose, interpolate

    if os.environ.get("PYTHON_DOTENV_DISABLED", "").lower() in {
        "1", "true", "t", "yes", "y"
    }:
        return False

    _, injected, found = _parse(
        dotenv_path=dotenv_path,
        stream=stream,
        override=override,
        encoding=encoding,
    )
    os.environ.update(injected)
    return found


def load_dotenvx(
        dotenv_path: Optional[StrPath] = None,
        override: bool = False
) -> Dict[str, str]:
    """Backward-compatible dotenvx loader returning the parsed mapping."""
    parsed, injected, _ = _parse(
        dotenv_path=dotenv_path,
        override=override,
    )
    os.environ.update(injected)
    return parsed
