"""Synthetic measurement-priority and adoption-capacity experiment.

The expected values are derived here before the adapter is called. No Voiage or
Innovate wheel is executed. Provider packets stay labelled as not executed or
as an externally supplied trajectory.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

_ADAPTER = Path(__file__).resolve().parents[2] / "adapters" / "decision_provider_d2"
sys.path.insert(0, str(_ADAPTER))
sys.path.insert(0, str(_ADAPTER / "tests"))

from bridge import adoption_capacity, voiage_packet  # noqa: E402
from study import prepare_evidence_question  # noqa: E402
from test_bridge import d1_fixture, d2_innovate, d2_voiage  # noqa: E402
from test_study import packet, protocol  # noqa: E402


def _evpi(matrix: list[list[float]]) -> float:
    """Equal-weight EVPI: mean of per-draw maxima minus the best mean strategy."""
    per_draw = [max(row) for row in matrix]
    means = [sum(row[i] for row in matrix) / len(matrix) for i in range(len(matrix[0]))]
    return sum(per_draw) / len(per_draw) - max(means)


def _adoption_reference() -> list[dict[str, object]]:
    """Two staff hours per adoption and a capacity of five hours, with backlog."""
    hours_per_adoption = 2
    capacity = 5
    backlog = 0
    rows = []
    for period, adoptions in (("2026-01", 4), ("2026-02", 1)):
        demand = adoptions * hours_per_adoption + backlog
        served = min(demand, capacity)
        backlog = demand - served
        rows.append(
            {
                "period": period,
                "demand": demand,
                "served": served,
                "backlog": backlog,
                "capacity_exceeded": demand > capacity,
            }
        )
    return rows


def run() -> dict[str, object]:
    paired = [[2.0, 0.0], [0.0, 3.0]]
    staff = [[-60.0, -80.0], [-120.0, -80.0]]
    paired_evpi = _evpi(paired)
    staff_evpi = _evpi(staff)
    d1 = d1_fixture()
    voiage = voiage_packet(json.dumps(d1), d1["output_digest"], d2_voiage(d1))
    question = prepare_evidence_question(packet(), protocol())
    adoption = adoption_capacity(d2_innovate())
    reference = _adoption_reference()
    observed = [
        {
            "period": row["period"],
            "demand": Fraction(int(row["demand"]["numerator"]), int(row["demand"]["denominator"])),
            "served": Fraction(int(row["served"]["numerator"]), int(row["served"]["denominator"])),
            "backlog": Fraction(
                int(row["backlog"]["numerator"]), int(row["backlog"]["denominator"])
            ),
            "capacity_exceeded": row["capacity_exceeded"],
        }
        for row in adoption["periods"]
    ]
    if observed != reference:
        raise AssertionError((observed, reference))
    if voiage["value_array"]["net_benefit"] != paired:
        raise AssertionError(voiage["value_array"]["net_benefit"])
    if question["value_array"]["net_benefit"] != staff:
        raise AssertionError(question["value_array"]["net_benefit"])
    priority = "staff_time_per_assay" if staff_evpi > paired_evpi else "paired_nmb"
    exceeded = [row["period"] for row in reference if row["capacity_exceeded"]]
    return {
        "paired_nmb_evpi": paired_evpi,
        "staff_time_evpi_per_assay": staff_evpi,
        "measurement_priority": priority,
        "capacity_exceeded_periods": exceeded,
        "voiage_execution": voiage["provider_execution"],
        "study_execution": question["provider_execution"],
        "adoption_execution": adoption["provider_execution"],
    }
