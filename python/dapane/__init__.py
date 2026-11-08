"""Python transport for the shared Dapane Rust costing and valuation kernel.

``evaluate_json`` preserves the core's JSON interface. ``evaluate`` accepts the
same request as a dictionary and returns a decoded report; it additionally
transports ``Decimal`` values as decimal strings and ``Fraction`` values as exact
rational pairs. No valuation or allocation formulas are implemented in Python.

The Python version requirement describes the package boundary. Tested native
interpreter/platform combinations are recorded separately in the repository's
verification evidence; no stable-ABI or source-provider support is implied.
"""

from __future__ import annotations

import json
from decimal import Decimal
from fractions import Fraction
from typing import Any

from . import _native
from ._native import __version__

__all__ = ["DapaneError", "__version__", "evaluate", "evaluate_json"]


class DapaneError(ValueError):
    """A structured request, transport or engine diagnostic.

    ``code`` identifies the failure category; ``message`` explains the problem;
    ``path`` is a JSON-pointer-like request location, with ``/`` for the root.
    ``invalid_transport`` is a Python-boundary error; other core diagnostics pass
    through unchanged.
    """

    def __init__(self, code: str, message: str, path: str = "/") -> None:
        self.code = code
        self.message = message
        self.path = path
        super().__init__(f"{code} at {path}: {message}")

    def as_dict(self) -> dict[str, str]:
        """Return the same diagnostic fields as the Rust JSON error contract."""
        return {"code": self.code, "message": self.message, "path": self.path}

    def __reduce__(self) -> tuple[type[DapaneError], tuple[str, str, str]]:
        return type(self), (self.code, self.message, self.path)


def evaluate_json(request_json: str) -> str:
    """Evaluate a versioned JSON request in Rust and return its JSON report.

    Exact numbers in JSON use decimal strings or numerator/denominator objects.
    JSON numbers are not accepted for quantities or monetary values. Unknown
    fields and unsupported methods fail in the core with a ``DapaneError``.
    """
    if not isinstance(request_json, str):
        raise DapaneError("invalid_transport", "request_json must be a string.")
    try:
        return _native.evaluate_json(request_json)
    except _native.CoreError as error:
        try:
            diagnostic = json.loads(str(error))
        except (ValueError, TypeError) as malformed:
            raise DapaneError(
                "internal_error", "The native engine returned malformed error data."
            ) from malformed
        if not isinstance(diagnostic, dict) or not all(
            isinstance(diagnostic.get(key), str) for key in ("code", "message", "path")
        ):
            raise DapaneError(
                "internal_error", "The native engine returned malformed error data."
            ) from error
        raise DapaneError(diagnostic["code"], diagnostic["message"], diagnostic["path"]) from None
    except UnicodeError as error:
        raise DapaneError(
            "invalid_transport", "request_json must contain valid Unicode scalar values."
        ) from error


def evaluate(request: dict[str, Any]) -> dict[str, Any]:
    """Evaluate a request dictionary through the same native JSON entry point.

    Decimal and Fraction conversion is exact transport only. Binary floats,
    nonfinite decimals, cyclic containers and non-string object keys are rejected.
    Integers remain JSON integers for fields such as ``price_year`` and rounding
    scale; represent exact quantities as strings, Decimal or Fraction instead.
    """
    if not isinstance(request, dict):
        raise DapaneError("invalid_transport", "request must be a dictionary.")
    prepared = _prepare_transport(request, "", set(), 0)
    try:
        request_json = json.dumps(prepared, allow_nan=False, separators=(",", ":"))
    except (TypeError, ValueError, RecursionError) as error:
        raise DapaneError("invalid_transport", "The request cannot be encoded as JSON.") from error
    report = json.loads(evaluate_json(request_json))
    if not isinstance(report, dict):
        raise DapaneError("internal_error", "The native engine returned a non-object report.")
    return report


def _prepare_transport(value: Any, path: str, ancestors: set[int], depth: int) -> Any:
    """Convert host values without interpreting costing fields or doing maths."""
    if depth > 128:
        raise DapaneError("invalid_transport", "The request is nested too deeply.", path or "/")
    if isinstance(value, float):
        raise DapaneError(
            "invalid_transport",
            "Binary floats are unsupported; use a decimal string, Decimal or Fraction.",
            path or "/",
        )
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise DapaneError("invalid_transport", "Decimal values must be finite.", path or "/")
        decimal_tuple = value.as_tuple()
        # Bound string expansion before formatting a hostile huge exponent. This
        # ceiling exceeds every decimal representable by the core 0.1 contract;
        # the core still owns its stricter precision and sign validation.
        if len(decimal_tuple.digits) + abs(int(decimal_tuple.exponent)) > 4096:
            raise DapaneError(
                "invalid_transport", "Decimal expansion exceeds the transport limit.", path or "/"
            )
        return format(value, "f")
    if isinstance(value, Fraction):
        try:
            return {"numerator": str(value.numerator), "denominator": str(value.denominator)}
        except ValueError as error:
            raise DapaneError(
                "invalid_transport", "Fraction exceeds the transport limit.", path or "/"
            ) from error
    if isinstance(value, (dict, list, tuple)):
        identity = id(value)
        if identity in ancestors:
            raise DapaneError(
                "invalid_transport", "Cyclic containers are unsupported.", path or "/"
            )
        ancestors.add(identity)
        try:
            if isinstance(value, dict):
                converted = {}
                for key, item in value.items():
                    if not isinstance(key, str):
                        raise DapaneError(
                            "invalid_transport", "JSON object keys must be strings.", path or "/"
                        )
                    escaped_key = key.replace("~", "~0").replace("/", "~1")
                    converted[key] = _prepare_transport(
                        item, f"{path}/{escaped_key}", ancestors, depth + 1
                    )
                return converted
            return [
                _prepare_transport(item, f"{path}/{index}", ancestors, depth + 1)
                for index, item in enumerate(value)
            ]
        finally:
            ancestors.remove(identity)
    raise DapaneError(
        "invalid_transport",
        f"Values of type {type(value).__name__} are unsupported by the JSON transport.",
        path or "/",
    )
