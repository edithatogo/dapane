"""Object-centric versus flattened pathway comparison for the static slice.

The numbers below are invented. Shared-batch and repeat totals use the existing
point oracle. The capacity case is exact quantity arithmetic because that oracle
rejects ``capacity_allocations``. This is not an XES import, a newborn-programme
result, or a Kairos execution.
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
    """Copy the one shared batch onto each recipient instead of allocating it."""
    result = deepcopy(request)
    batch = next(row for row in result["usage"] if row["id"] == "batch")
    result["usage"] = [row for row in result["usage"] if row["id"] != "batch"]
    result["usage"].extend(_batch_copy(batch, object_id) for object_id in ("a", "b"))
    result["allocations"] = []
    return result


def with_repeat_labour(request: dict) -> dict:
    """Add one extra third of an hour. Do not copy the shared batch."""
    result = deepcopy(request)
    labour = next(row for row in result["usage"] if row["id"] == "labour")
    extra = deepcopy(labour)
    extra["id"] = "repeat-labour"
    extra["use_id"] = "use-repeat-labour"
    result["usage"].append(extra)
    return result


def representations() -> dict:
    base = _baseline()
    shared_object = point_reference(base)
    shared_flat = point_reference(flattened_shared_batch(base))
    repeat_object = point_reference(with_repeat_labour(base))
    repeat_flat = point_reference(flattened_shared_batch(with_repeat_labour(base)))
    occupied = Fraction(1, 2)
    infants = 2
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
            "object_centric_batch_lines": 1,
            "flattened_batch_lines": 2,
        },
        "repeat": {
            "object_centric_rounded": repeat_object["totals"]["rounded"],
            "flattened_rounded": repeat_flat["totals"]["rounded"],
        },
        "capacity": {
            "object_centric_hours": occupied,
            "flattened_hours": occupied * infants,
            "object_centric_cost": occupied * rate,
            "flattened_cost": occupied * infants * rate,
            "oracle": capacity_oracle,
        },
    }
