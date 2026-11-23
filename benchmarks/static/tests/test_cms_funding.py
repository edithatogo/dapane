"""Check independent held-out predictions and prevent target leakage."""

import json
import os
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from benchmarks.static.cms_funding_transport import calibrate, calibration_request

STATES = {"01": ("2", "100"), "02": ("3", "200"), "04": ("5", "400")}


class CmsCalibrationTests(unittest.TestCase):
    def test_hand_calculated_held_out_predictions(self):
        cli = Path(os.environ["DAPANE_BENCH_CLI"]).resolve(strict=True)
        result = calibrate(cli, {**STATES, "national": ("10", "9999")})
        self.assertEqual(
            result["folds"],
            [
                {
                    "geography": "01",
                    "reference_cents": 20000,
                    "prediction_cents": 65000,
                    "error_cents": 45000,
                },
                {
                    "geography": "02",
                    "reference_cents": 60000,
                    "prediction_cents": 94286,
                    "error_cents": 34286,
                },
                {
                    "geography": "04",
                    "reference_cents": 200000,
                    "prediction_cents": 80000,
                    "error_cents": -120000,
                },
            ],
        )
        self.assertEqual(result["sum_absolute_state_error_cents"], 199286)

    def test_calibration_rejects_unrounded_drift_with_matching_cents(self):
        cli = Path(os.environ["DAPANE_BENCH_CLI"]).resolve(strict=True)

        def evaluate_with_drift(*args, **kwargs):
            completed = subprocess.run(*args, **kwargs)
            if json.loads(kwargs["input"])["run_id"] == "cms-held-out-state-rate-calibration":
                report = json.loads(completed.stdout)
                line = next(line for line in report["lines"] if line["id"] == "state-01")
                self.assertEqual(line["rounded"], "650.00")
                line["exact"] = {"numerator": "650001", "denominator": "1000"}
                completed.stdout = json.dumps(report).encode()
            return completed

        with patch("benchmarks.static.cms_funding_transport.subprocess") as native:
            native.run.side_effect = evaluate_with_drift
            with self.assertRaisesRegex(ValueError, "unrounded state amounts"):
                calibrate(cli, {**STATES, "national": ("10", "9999")})

    def test_holdout_rate_is_independent_of_its_published_mean(self):
        revised = {**STATES, "01": ("2", "9999")}
        old_quotes = calibration_request(STATES)["quotes"]
        new_quotes = calibration_request(revised)["quotes"]
        self.assertEqual(old_quotes[0], new_quotes[0])
        self.assertNotEqual(old_quotes[1]["amount"], new_quotes[1]["amount"])

    def test_training_requires_another_usable_state(self):
        with self.assertRaisesRegex(ValueError, "at least two usable geographies"):
            calibration_request({"01": ("2", "100")})


if __name__ == "__main__":
    unittest.main()
