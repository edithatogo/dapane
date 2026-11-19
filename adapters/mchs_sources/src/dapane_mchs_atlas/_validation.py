"""Strict bounded transport checks; this module does no valuation arithmetic."""

from __future__ import annotations

import copy
import json
import re
from datetime import date, datetime
from typing import Any, NoReturn

MAX_BYTES = 4 * 1024 * 1024
MAX_ROWS = 10_000


class AdapterError(ValueError):
    """A fail-closed adapter diagnostic with a JSON-pointer-like input path."""

    def __init__(self, code: str, message: str, path: str = "/") -> None:
        self.code = code
        self.message = message
        self.path = path or "/"
        super().__init__(f"{code} at {self.path}: {message}")

    def as_dict(self) -> dict[str, str]:
        """Return a machine-readable diagnostic without exposing input records."""
        return {"code": self.code, "message": self.message, "path": self.path}


def fail(code: str, message: str, path: str) -> NoReturn:
    raise AdapterError(code, message, path)


def object_at(value: Any, required: str, optional: str, path: str) -> dict[str, Any]:
    if type(value) is not dict:
        fail("invalid_type", "Expected an object.", path)
    required_keys = set(required.split())
    unknown = set(value) - required_keys - set(optional.split())
    missing = required_keys - set(value)
    if unknown:
        fail("unknown_field", "Unknown field.", f"{path}/{sorted(unknown)[0]}")
    if missing:
        fail("missing_field", "Required field is absent.", f"{path}/{sorted(missing)[0]}")
    return value


def rows(value: Any, path: str, *, nonempty: bool = False) -> list[Any]:
    if type(value) is not list or len(value) > MAX_ROWS:
        fail("invalid_collection", "Expected a bounded array.", path)
    if nonempty and not value:
        fail("missing_input", "At least one record is required.", path)
    return value


def text(value: Any, path: str, *, limit: int = 128) -> str:
    if (
        type(value) is not str
        or not value
        or value != value.strip()
        or any(ord(char) < 32 or 127 <= ord(char) <= 159 for char in value)
    ):
        fail("invalid_text", "Expected nonempty trimmed text without controls.", path)
    try:
        size = len(value.encode("utf-8"))
    except UnicodeError:
        fail("invalid_text", "Text must contain valid Unicode scalar values.", path)
    if size > limit:
        fail("input_limit", "Text exceeds the field limit.", path)
    return value


def choice(value: Any, choices: tuple[str, ...], path: str, code: str) -> str:
    if type(value) is not str or value not in choices:
        fail(code, "Unsupported or unknown value.", path)
    return value


def integer(value: Any, lower: int, upper: int, path: str) -> int:
    if type(value) is not int or not lower <= value <= upper:
        fail("invalid_integer", "Expected an integer within the supported bounds.", path)
    return value


def day(value: Any, path: str) -> str:
    if type(value) is not str or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        fail("invalid_date", "Expected a YYYY-MM-DD date.", path)
    try:
        date.fromisoformat(value)
    except ValueError:
        fail("invalid_date", "Invalid calendar date.", path)
    return value


def timestamp(value: Any, path: str) -> str:
    value = text(value, path)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        fail("invalid_date", "Expected an ISO retrieval timestamp with timezone.", path)
    if parsed.tzinfo is None:
        fail("invalid_date", "Retrieval timestamp requires a timezone.", path)
    return value


def digest(value: Any, path: str, *, prefix: bool = False) -> str:
    pattern = r"sha256:[0-9a-f]{64}" if prefix else r"[0-9a-f]{64}"
    if type(value) is not str or not re.fullmatch(pattern, value):
        fail("invalid_digest", "Expected a lowercase SHA256 digest.", path)
    return value


def exact(value: Any, path: str, *, positive: bool = False) -> Any:
    """Check syntax and bounds only; quantities are never multiplied or rounded."""
    if type(value) is str:
        if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", value):
            fail("invalid_exact", "Expected an unsigned exact decimal string.", path)
        digits = value.replace(".", "")
        if len(digits) > 96 or ("." in value and len(value.split(".")[1]) > 36):
            fail("invalid_exact", "Exact decimal exceeds core precision bounds.", path)
        nonzero = bool(digits.lstrip("0"))
    elif type(value) is dict and set(value) == {"numerator", "denominator"}:
        for key in ("numerator", "denominator"):
            atom = value[key]
            if type(atom) is not str or not re.fullmatch(r"[0-9]{1,96}", atom):
                fail("invalid_exact", "Expected bounded unsigned rational strings.", path)
        if not value["denominator"].lstrip("0"):
            fail("invalid_exact", "The rational denominator must be positive.", path)
        nonzero = bool(value["numerator"].lstrip("0"))
    else:
        fail("invalid_exact", "Use an exact string or rational, never a JSON number.", path)
    if positive and not nonzero:
        fail("invalid_exact", "This exact quantity must be positive.", path)
    return value


def currency(value: Any, path: str) -> str:
    if type(value) is not str or not re.fullmatch(r"[A-Z]{3}", value):
        fail("invalid_currency", "Expected three uppercase ASCII currency letters.", path)
    return value


def equal(left: Any, right: Any, path: str, *, code: str = "source_mismatch") -> None:
    if left != right:
        fail(code, "Linked evidence or applicability does not match.", path)


def snapshot(value: Any) -> dict[str, Any]:
    """Bound a JSON-shaped graph before copying; reject cycles and host objects."""
    ancestors: set[int] = set()
    budget = [0]

    def visit(item: Any, depth: int, path: str) -> None:
        budget[0] += 1
        if depth > 64 or budget[0] > 100_000:
            fail("input_limit", "Input exceeds nesting or node bounds.", path)
        if type(item) in (dict, list):
            if id(item) in ancestors:
                fail("invalid_transport", "Cyclic input is unsupported.", path)
            if len(item) > MAX_ROWS:
                fail("input_limit", "Input collection is too large.", path)
            ancestors.add(id(item))
            if type(item) is dict:
                for key, nested in item.items():
                    if type(key) is not str:
                        fail("invalid_transport", "Object keys must be strings.", path)
                    escaped = key.replace("~", "~0").replace("/", "~1")
                    visit(nested, depth + 1, f"{path}/{escaped}")
            else:
                for index, nested in enumerate(item):
                    visit(nested, depth + 1, f"{path}/{index}")
            ancestors.remove(id(item))
        elif item is not None and type(item) not in (str, bool, int, float):
            fail("invalid_transport", "Unsupported host value; use exact JSON transport.", path)

    visit(value, 0, "")
    try:
        encoded = json.dumps(value, allow_nan=False, ensure_ascii=False).encode("utf-8")
    except (ValueError, TypeError, UnicodeError, RecursionError):
        fail("invalid_transport", "Input cannot be represented as finite UTF-8 JSON.", "/")
    if len(encoded) > MAX_BYTES:
        fail("input_limit", "Input exceeds 4 MiB.", "/")
    if type(value) is not dict:
        fail("invalid_type", "Expected a top-level object.", "/")
    return copy.deepcopy(value)


def loads(payload: str) -> dict[str, Any]:
    """Read bounded JSON while rejecting duplicate keys and nonfinite constants."""
    if type(payload) is not str:
        fail("invalid_transport", "JSON input must be text.", "/")
    try:
        if len(payload.encode("utf-8")) > MAX_BYTES:
            fail("input_limit", "Input exceeds 4 MiB.", "/")
    except UnicodeError:
        fail("invalid_transport", "JSON must contain valid Unicode.", "/")

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                fail("duplicate_key", "Duplicate JSON object key.", "/")
            result[key] = value
        return result

    def constant(_: str) -> None:
        fail("invalid_transport", "Nonfinite JSON values are unsupported.", "/")

    try:
        value = json.loads(payload, object_pairs_hook=pairs, parse_constant=constant)
    except (json.JSONDecodeError, RecursionError, ValueError) as error:
        if isinstance(error, AdapterError):
            raise
        fail("invalid_transport", "Malformed or excessive JSON input.", "/")
    return snapshot(value)
