"""Object-centric versus flattened pathway comparison for the static slice.

Shared-batch and repeat totals use the invented point fixture and its reference
oracle. The capacity case is a separate demonstration of duplicate quantities.
The point oracle rejects populated ``capacity_allocations``.
"""

from copy import deepcopy
from fractions import Fraction
from pathlib import Path

from .common import Failure, load
from .oracle import point_reference

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _baseline() -> dict:
    return load(FIXTURES / "point.json")


def _batch_copy(batch: dict, object_id: str) -> dict:
    row = deepcopy(batch)
    row["id"] = f"batch-{object_id}"
    row["use_id"] = f"use-batch-{object_id}"
    row["attribution_object_id"] = object_id
    return row


def flattened_shared_batch(request: dict) -> dict:
    """Replace the fixture's shared allocation with one batch line per recipient."""
    result = deepcopy(request)
    batch = next(row for row in result["usage"] if row["id"] == "batch")
    pool = next(pool for pool in result["allocations"] if pool["id"] == "shared")
    result["usage"] = [row for row in result["usage"] if row["id"] != "batch"]
    result["usage"].extend(_batch_copy(batch, row["object_id"]) for row in pool["weights"])
    result["allocations"].remove(pool)
    return result


def with_repeat_labour(request: dict) -> dict:
    """Add one repeat of the fixture's labour use."""
    result = deepcopy(request)
    labour = next(row for row in result["usage"] if row["id"] == "labour")
    extra = deepcopy(labour)
    extra["id"] = "repeat-labour"
    extra["use_id"] = "use-repeat-labour"
    result["usage"].append(extra)
    return result


def _batch_line_count(report: dict) -> int:
    return sum(name == "batch" or name.startswith("batch-") for name in report["lines"])


def representations() -> dict:
    """Compare the fixture's attributed and duplicated costs and quantities."""
    base = _baseline()
    shared_object = point_reference(base)
    shared_flat = point_reference(flattened_shared_batch(base))
    repeat_object = point_reference(with_repeat_labour(base))
    repeat_flat = point_reference(flattened_shared_batch(with_repeat_labour(base)))
    occupied = Fraction(1, 2)
    recipients = _batch_line_count(shared_flat)
    rate = Fraction(90)
    capacity_request = deepcopy(base)
    capacity_request["capacity_allocations"] = [
        {"id": "instrument", "quantity": {"numerator": "1", "denominator": "2"}}
    ]
    try:
        point_reference(capacity_request)
    except Failure as error:
        capacity_oracle = str(error)
    else:
        raise Failure("Point oracle accepted a capacity field")
    return {
        "shared_batch": {
            "object_centric_rounded": shared_object["totals"]["rounded"],
            "flattened_rounded": shared_flat["totals"]["rounded"],
            "object_centric_batch_lines": _batch_line_count(shared_object),
            "flattened_batch_lines": recipients,
        },
        "repeat": {
            "object_centric_rounded": repeat_object["totals"]["rounded"],
            "flattened_rounded": repeat_flat["totals"]["rounded"],
        },
        "capacity": {
            "object_centric_hours": occupied,
            "flattened_hours": occupied * recipients,
            "object_centric_cost": occupied * rate,
            "flattened_cost": occupied * recipients * rate,
            "oracle": capacity_oracle,
        },
    }
