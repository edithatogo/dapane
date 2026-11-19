"""Strict IO helpers used only by the synthetic benchmark harness."""

import hashlib
import json
from pathlib import Path


class Failure(ValueError):
    """A benchmark contract or independent check failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Failure(message)


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _unique(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _nonfinite(value: str) -> None:
    raise Failure(f"Nonfinite JSON constant: {value}")


def decode(raw: bytes) -> object:
    try:
        return json.loads(raw, object_pairs_hook=_unique, parse_constant=_nonfinite)
    except (ValueError, UnicodeError) as error:
        raise Failure(f"Invalid JSON: {error}") from error


def load(path: Path) -> object:
    return decode(path.read_bytes())


def digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def file_digest(path: Path) -> str:
    with path.open("rb") as stream:
        return "sha256:" + hashlib.file_digest(stream, "sha256").hexdigest()
