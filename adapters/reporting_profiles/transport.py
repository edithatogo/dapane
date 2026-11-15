"""Bounded, explicit transport failures for the optional reporting adapter."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import NoReturn

MAX_DECLARATION_BYTES = 1024 * 1024
MAX_SOURCE_BYTES = 4 * 1024 * 1024


class ReportingError(ValueError):
    """A stable error with no partial report or financial output."""

    def __init__(self, code: str, path: str, message: str):
        self.code, self.path, self.message = code, path, message
        super().__init__(f"{code} at {path}: {message}")


def fail(code: str, path: str, message: str) -> NoReturn:
    raise ReportingError(code, path, message)


def canonical(value: object) -> bytes:
    """Serialize transport without coercing decimal strings or rational pairs."""
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeError, RecursionError) as exc:
        raise ReportingError("invalid_json", "/", "expected bounded JSON values") from exc


def _pairs(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            fail("duplicate_key", "/", "duplicate JSON object key")
        result[key] = value
    return result


def _nonfinite(_: str) -> NoReturn:
    fail("invalid_json", "/", "non-finite JSON constants are unsupported")


def parse_json(raw: bytes, *, limit: int = MAX_DECLARATION_BYTES) -> object:
    if len(raw) > limit:
        fail("limit_exceeded", "/", "JSON input exceeds its byte limit")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_nonfinite)
    except (ValueError, UnicodeError, RecursionError) as exc:
        if isinstance(exc, ReportingError):
            raise
        raise ReportingError("invalid_json", "/", "expected bounded UTF-8 JSON") from exc


def read_json(path: Path, *, limit: int = MAX_DECLARATION_BYTES) -> object:
    """Read only the explicit local path; never follow document locators."""
    try:
        with path.open("rb") as stream:
            return parse_json(stream.read(limit + 1), limit=limit)
    except OSError as exc:
        raise ReportingError("input_unavailable", "/", "cannot read local JSON input") from exc


def fields(value: object, expected: set[str], path: str) -> dict:
    if not isinstance(value, dict) or set(value) != expected:
        fail("invalid_fields", path, "missing or unknown fields in reporting declaration")
    return value


def text(value: object, path: str, *, limit: int = 2048) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        fail("invalid_text", path, "expected nonempty trimmed text")
    try:
        if len(value.encode("utf-8")) > limit or any(
            ord(c) < 32 or 127 <= ord(c) <= 159 for c in value
        ):
            fail("invalid_text", path, "text exceeds bounds or contains control characters")
    except UnicodeError as exc:
        raise ReportingError("invalid_text", path, "text must be valid UTF-8") from exc
    return value


def pointer_value(document: object, pointer: str) -> object:
    """Resolve strict RFC 6901 locations inside the selected bundle, with no IO."""
    text(pointer, "/evidence/pointer")
    if not pointer.startswith("/") or re.search(r"~(?![01])", pointer):
        fail("invalid_pointer", "/evidence/pointer", "expected an RFC 6901 JSON pointer")
    value = document
    for token in pointer[1:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(value, dict) and token in value:
            value = value[token]
        elif isinstance(value, list) and re.fullmatch(r"0|[1-9][0-9]*", token):
            if len(token) > 8 or int(token) >= len(value):
                fail("invalid_pointer", "/evidence/pointer", "array index does not resolve")
            value = value[int(token)]
        else:
            fail("invalid_pointer", "/evidence/pointer", "location does not resolve in bundle")
    if value is None or value == [] or value == {} or value == "":
        fail("empty_evidence", "/evidence/pointer", "evidence location has no content")
    return value
