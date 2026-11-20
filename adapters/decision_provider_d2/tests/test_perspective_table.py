"""The Voiage handoff keeps every joint key beside the numeric array."""

import unittest

from perspective_table import PerspectiveTableError, arrange, value_of_perspective


def _row(strategy, perspective, draw, amount):
    numerator, denominator = amount.split("/")
    return {
        "scenario_id": "synthetic-NZ",
        "strategy_id": strategy,
        "draw_id": draw,
        "replication_id": "rep-a",
        "perspective": perspective,
        "subgroup_id": "Māori / NZDep-1",
        "net_monetary_benefit": {"numerator": numerator, "denominator": denominator},
    }


def table():
    rows = []
    for draw, alternative, reference in (
        ("draw-a", ("20/1", "4/1"), ("0/1", "0/1")),
        ("draw-b", ("10/1", "2/1"), ("5/1", "1/1")),
    ):
        for strategy, amounts in (("alternative", alternative), ("reference", reference)):
            for perspective, amount in zip(("health_system", "societal"), amounts, strict=True):
                rows.append(_row(strategy, perspective, draw, amount))
    return {"schema_version": "dapane-fiscal-perspective-table/0.1", "rows": rows}


class PerspectiveTableTests(unittest.TestCase):
    def test_every_cell_keeps_its_joint_key_in_array_order(self):
        arranged = arrange(table())
        self.assertEqual([row["draw_id"] for row in arranged["samples"]], ["draw-a", "draw-b"])
        self.assertEqual(arranged["strategy_ids"], ["alternative", "reference"])
        self.assertEqual(arranged["perspective_ids"], ["health_system", "societal"])
        self.assertEqual(len(arranged["cells"]), 8)
        self.assertEqual(
            arranged["cells"][0],
            {
                "scenario_id": "synthetic-NZ",
                "draw_id": "draw-a",
                "replication_id": "rep-a",
                "subgroup_id": "Māori / NZDep-1",
                "strategy_id": "alternative",
                "perspective": "health_system",
                "net_monetary_benefit": "20/1",
            },
        )
        self.assertEqual(arranged["net_monetary_benefit"][1][1][1], "1/1")

    def test_a_missing_or_repeated_cell_is_rejected(self):
        payload = table()
        payload["rows"].pop()
        with self.assertRaises(PerspectiveTableError) as missing:
            arrange(payload)
        self.assertEqual(missing.exception.code, "incomplete_panel")
        payload = table()
        payload["rows"].append(payload["rows"][0])
        with self.assertRaises(PerspectiveTableError) as duplicate:
            arrange(payload)
        self.assertEqual(duplicate.exception.code, "duplicate_key")

    def test_lossy_payoffs_fail_before_provider_dispatch(self):
        payload = table()
        payload["rows"][0]["net_monetary_benefit"]["numerator"] = "9007199254740993"
        with self.assertRaises(PerspectiveTableError) as error:
            value_of_perspective(payload)
        self.assertEqual(error.exception.code, "precision_loss")

    def test_strata_have_separate_optima(self):
        payload = table()
        for row in table()["rows"]:
            row["subgroup_id"] = "other"
            row["net_monetary_benefit"]["numerator"] = (
                "20" if row["strategy_id"] == "reference" else "0"
            )
            payload["rows"].append(row)
        try:
            result = value_of_perspective(payload)
        except PerspectiveTableError as error:
            if error.code == "provider_unavailable":
                self.skipTest(str(error))
            raise
        self.assertEqual(
            [part["optimal_strategy_names"] for part in result["strata"]],
            [["alternative", "alternative"], ["reference", "reference"]],
        )
        self.assertEqual(len(result["cells"]), 16)

    def test_installed_voiage_receives_the_same_labels(self):
        try:
            result = value_of_perspective(table())
        except PerspectiveTableError as error:
            if error.code == "provider_unavailable":
                self.skipTest(str(error))
            raise
        self.assertEqual(result["optimal_strategy_names"], ["alternative", "alternative"])
        self.assertEqual(len(result["cells"]), 8)
        self.assertEqual(result["cells"][7]["draw_id"], "draw-b")
        self.assertEqual(result["cells"][7]["strategy_id"], "reference")
        self.assertEqual(result["cells"][7]["perspective"], "societal")
