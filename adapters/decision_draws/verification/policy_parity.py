"""Installed-provider qualification for invented NZ and AU policy schedules."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from fractions import Fraction
from importlib.util import find_spec
from pathlib import Path

from tobac import health

ADAPTERS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ADAPTERS / "decision_provider_d2"))
from perspective_table import credal_dominance, value_of_perspective  # noqa: E402

FIXTURE = ADAPTERS / "decision_draws/fixtures/fiscal-nz-synthetic.json"
RULES = {
    "health_system": "health_system_direct_only",
    "societal": "societal_net_domestic_transfers",
    "public_finance": "public_finance_net_outlay",
}
KEYS = ("scenario_id", "strategy_id", "draw_id", "replication_id", "perspective", "subgroup_id")


def wire(value):
    value = Fraction(value)
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def amount(value):
    return Fraction(int(value["numerator"]), int(value["denominator"]))


def native(operation, payload):
    output = subprocess.run(
        [os.environ["DAPANE_FISCAL_BIN"], operation],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=20,
    )
    if output.returncode:
        raise AssertionError(output.stderr)
    return json.loads(output.stdout)


def packet(
    country,
    perspective,
    population=10,
    group="synthetic-group-A",
    strategy="alternative",
    draw="draw-a",
):
    value = json.loads(FIXTURE.read_text(encoding="utf-8"))
    active = strategy == "alternative"
    years = Fraction(1, 2) if country == "AU" else Fraction(1)
    quitters = Fraction(population, 2) if active else Fraction(0)
    currency = {"NZ": "NZD", "AU": "AUD"}[country]
    basis = "economic_cost" if perspective == "societal" else "public_expenditure"
    value.update(
        schema_version="dapane-fiscal/0.2",
        jurisdiction=country,
        currency=currency,
        resource_basis=basis,
        perspective=perspective,
        aggregation_rule=RULES[perspective],
        comparator_strategy_id="no-programme",
    )
    value["key"].update(
        scenario_id="synthetic-" + country,
        perspective=perspective,
        strategy_id=strategy,
        subgroup_id=group,
        draw_id=draw,
    )
    value["discount"].update(
        step_years=wire(years), health_rate=wire(Fraction(1, 4) if country == "AU" else 0)
    )
    for line in value["lines"]:
        money = line["undiscounted_amount"]
        money["currency"] = currency
        if not active:
            money["amount"] = wire(0)
        if line["kind"] != "discounted_tax_transfer":
            line["basis"] = basis

    def schedule_row(identity, cost):
        return {
            "id": identity,
            "time_step": 1,
            "perspective": perspective,
            "basis": basis,
            "source": value["lines"][0]["source"],
            "undiscounted_amount": {
                "amount": wire(cost),
                "currency": currency,
                "price_year": 2026,
                "unit": "currency",
            },
        }

    value["cohort_states"] = [
        dict(
            schedule_row("transition", 100 * quitters),
            from_state="smoker",
            to_state="quit",
            population_count=wire(quitters),
        )
    ]
    value["cessation_resources"] = [
        dict(
            schedule_row("counselling", 50 * quitters),
            resource_type="counselling",
            quantity=wire(quitters),
        )
    ]
    if perspective == "public_finance":
        value["health"] = None
    else:
        value["health"]["threshold"].update(currency=currency, amount=wire(300))
        value["health"]["flows"][0].update(time_step=2, value=wire(quitters * years / 2))
    return value


def oracle(country, population):
    """Propagate survivor states in Tobac and value both periods at their end."""
    years = 0.5 if country == "AU" else 1.0
    annual_rate = 0.5625 if country == "AU" else 0.25
    population = {"smoker": float(population), "quit": 0.0}
    hazards = {"smoker": (0.0,), "quit": (0.0,)}
    stay = {"smoker": {"smoker": 1.0, "quit": 0.0}, "quit": {"smoker": 0.0, "quit": 1.0}}
    quit_half = {**stay, "smoker": {"smoker": 0.5, "quit": 0.5}}
    unchanged = health.ExposureInterval(years, hazards, stay)
    action = (health.ExposureInterval(years, hazards, quit_half), unchanged)
    reference = (unchanged, unchanged)
    utilities = ({"smoker": 0.5, "quit": 1.0},) * 2
    quitters = health.exposure_health_trajectory(population, action)[0].population["quit"]
    qaly = health.incremental_exposure_qalys(
        population,
        action,
        reference,
        utilities,
        (years, 2 * years),
        annual_rate if country == "AU" else 0.0,
    )

    def cost(flow):
        return health.discounted_resource_cost((flow,), (years,), annual_rate)

    receipts, outflows = health.discounted_tax_transfer((40.0, 10.0), (years, years), annual_rate)
    return quitters, qaly, cost, receipts, outflows


class PolicyParity(unittest.TestCase):
    def test_country_schedules_and_each_perspective(self):
        for country in ("NZ", "AU"):
            quitters, qaly, cost, receipts, outflows = oracle(country, 10)
            for view in RULES:
                with self.subTest(country=country, view=view):
                    source = packet(country, view)
                    report = native("evaluate", source)
                    self.assertEqual(report["key"], source["key"])
                    (cohort,) = report["valued_cohort_states"]
                    (cessation,) = report["valued_cessation_resources"]
                    self.assertEqual(amount(cohort["population_count"]), quitters)
                    self.assertEqual(amount(cessation["quantity"]), quitters)
                    self.assertAlmostEqual(
                        float(amount(cohort["discounted_amount"])), cost(100 * quitters)
                    )
                    self.assertAlmostEqual(
                        float(amount(cessation["discounted_amount"])), cost(50 * quitters)
                    )
                    self.assertAlmostEqual(
                        float(amount(report["tax_transfers"]["government_receipts"])), receipts
                    )
                    self.assertAlmostEqual(
                        float(amount(report["tax_transfers"]["payer_outflows"])), outflows
                    )
                    selected = cost(100 if view == "health_system" else 120)
                    self.assertAlmostEqual(
                        float(amount(report["selected_resource_cost"])), selected
                    )
                    if view == "public_finance":
                        self.assertIsNone(report["discounted_qalys"])
                        self.assertIsNone(report["net_monetary_benefit"])
                        self.assertAlmostEqual(
                            float(amount(report["net_public_outlay"])), selected - receipts
                        )
                    else:
                        self.assertAlmostEqual(float(amount(report["discounted_qalys"])), qaly)
                        self.assertAlmostEqual(
                            float(amount(report["net_monetary_benefit"])), 300 * qaly - selected
                        )

    def test_population_equity(self):
        sizes = {"synthetic-group-A": 10, "synthetic-group-B": 6}
        for country in ("NZ", "AU"):
            per_person = {group: oracle(country, n)[1] / n for group, n in sizes.items()}
            gains = health.aggregate_qaly_gains(per_person, sizes, sum(sizes.values()))
            for weights in ((1, 1), (1, 2)):
                by_group = dict(zip(sizes, weights, strict=True))
                result = native(
                    "equity",
                    {
                        "schema_version": "dapane-fiscal-equity/0.1",
                        "packets": [
                            {
                                "weight": wire(by_group[group]),
                                "fiscal": packet(country, "health_system", n, group),
                            }
                            for group, n in sizes.items()
                        ],
                    },
                )
                expected = health.equity_weighted_qaly_score(gains, by_group)
                self.assertAlmostEqual(
                    float(amount(result["weighted_sum"]["discounted_qalys"])), expected
                )
                if weights == (1, 1):
                    self.assertEqual(result["unweighted_sum"], result["weighted_sum"])

    def test_installed_producer_to_both_consumers(self):
        for country in ("NZ", "AU"):
            rows = []
            for draw, population in (("draw-a", 10), ("draw-b", 12)):
                for strategy in ("alternative", "reference"):
                    for view in ("health_system", "societal"):
                        source = packet(country, view, population, strategy=strategy, draw=draw)
                        exported = native("export", native("evaluate", source))
                        (row,) = exported["rows"]
                        self.assertEqual({k: row[k] for k in KEYS}, source["key"])
                        rows.append(row)
            table = {"schema_version": exported["schema_version"], "rows": rows}
            voiage, tobac = value_of_perspective(table), credal_dominance(table)
            self.assertEqual(voiage["optimal_strategy_names"], ["alternative", "alternative"])
            for item in tobac["perspectives"]:
                self.assertEqual(item["common_optimal_actions"], ["alternative"])
            expected = {tuple(row[k] for k in KEYS) for row in rows}
            for result in (voiage, tobac):
                self.assertEqual({tuple(row[k] for k in KEYS) for row in result["cells"]}, expected)
                self.assertEqual(len(result["cells"]), 8)

    def test_standalone_provider_environment(self):
        self.assertIsNone(
            find_spec("dapane"), "Use a clean provider environment for the fallback check"
        )
        self.assertAlmostEqual(oracle("NZ", 10)[1], 2.5)
        import numpy as np
        from voiage._runtime import compute_evpi

        self.assertEqual(compute_evpi(np.array([[20.0, 0.0], [0.0, 20.0]])), 10.0)


if __name__ == "__main__":
    unittest.main()
