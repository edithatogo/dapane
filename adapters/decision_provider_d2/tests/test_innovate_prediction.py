"""Monthly whole-person predictions and capacity feedback from the pinned provider."""

import copy
import hashlib
import json
import os
import subprocess
import unittest
from pathlib import Path

from bridge import INNOVATE_PREDICTION, D2Error, innovate_adoption_capacity_native
from innovate_prediction import REVISION, SCHEMA
from test_bridge import d2_innovate

FIXTURE = Path(__file__).resolve().parents[2] / "decision_draws/fixtures/fiscal-nz-synthetic.json"


def scenario():
    fixture = json.loads(FIXTURE.read_text())
    request = d2_innovate()
    request["schema_version"] = SCHEMA
    request["key"] = fixture["key"]
    request["run_id"] = fixture["run_id"]
    request["provider"].update(
        revision=REVISION, contract=INNOVATE_PREDICTION[0], method=INNOVATE_PREDICTION[1]
    )
    request["periods"] = [row["period"] for row in request.pop("observations")]
    request["model"] = {
        "model_key": "bass",
        "p": {"numerator": "3", "denominator": "100"},
        "q": {"numerator": "19", "denominator": "50"},
        "m": 100,
        "count_policy": "floor_cumulative",
    }
    return request


class InnovatePredictionTests(unittest.TestCase):
    def test_gaps_rejected_before_runner(self):
        request = scenario()
        request["periods"][1] = "2026-03"
        with self.assertRaisesRegex(D2Error, "invalid_period_sequence"):
            innovate_adoption_capacity_native(request, "unused")

    def test_observations_and_missing_feedback_are_rejected(self):
        with self.assertRaisesRegex(D2Error, "unsupported_schema"):
            innovate_adoption_capacity_native(d2_innovate(), "unused")
        request = scenario()
        request["iteration"] = 1
        with self.assertRaisesRegex(D2Error, "feedback_chain"):
            innovate_adoption_capacity_native(request, "unused")

    def test_installed_predictor_and_fiscal_trigger(self):
        binary, fiscal = os.environ.get("DAPANE_INNOVATE_BIN"), os.environ.get("DAPANE_FISCAL_BIN")
        if not binary or not fiscal:
            self.skipTest("Set DAPANE_INNOVATE_BIN and DAPANE_FISCAL_BIN for installed feedback")
        request = scenario()
        with open(binary, "rb") as stream:
            request["provider"]["artifact_digest"] = (
                "sha256:" + hashlib.file_digest(stream, "sha256").hexdigest()
            )
        base = innovate_adoption_capacity_native(request, binary)
        self.assertEqual([r["new_adoptions"] for r in base["periods"]], [3, 5])
        self.assertEqual([r["backlog"]["numerator"] for r in base["periods"]], ["1", "6"])
        self.assertEqual([r["capacity_exceeded"] for r in base["periods"]], [True, True])
        self.assertEqual(base["provider"]["method"], "predict_model:bass")
        valued = json.loads(
            subprocess.check_output([fiscal, "evaluate"], input=FIXTURE.read_bytes(), timeout=20)
        )
        feedback = copy.deepcopy(request)
        feedback.update(
            iteration=1,
            previous_evaluation_digest=base["output_digest"],
            feedback={
                "mode": "external_recomputed",
                "price_affects_adoption": True,
                "valuation_digest": valued["output_digest"],
            },
        )
        # The scenario owner supplies this hypothetical price response. Innovate forecasts both paths.
        feedback["model"]["p"]["numerator"] = "1"
        revised = innovate_adoption_capacity_native(
            feedback, binary, previous_evaluation=base, valuation=valued
        )
        self.assertEqual([r["new_adoptions"] for r in revised["periods"]], [1, 1])
        self.assertEqual([r["capacity_exceeded"] for r in revised["periods"]], [False, False])
        self.assertEqual(revised["triggering_valuation_digest"], valued["output_digest"])
        self.assertEqual(revised["previous_evaluation_digest"], base["output_digest"])
        for report, field in ((base, "iteration"), (valued, "price_year")):
            invalid = {**report, field: 99}
            with self.assertRaisesRegex(D2Error, "feedback_chain"):
                innovate_adoption_capacity_native(
                    feedback,
                    binary,
                    previous_evaluation=invalid if report is base else base,
                    valuation=invalid if report is valued else valued,
                )
