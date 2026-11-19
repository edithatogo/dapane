"""Hand-derived expectations for the synthetic decision-slice experiment."""

import unittest

from benchmarks.static.decision_slice import run


class DecisionSliceTests(unittest.TestCase):
    def test_staff_time_outranks_the_smaller_paired_question_and_capacity_binds_once(self):
        # Paired matrix EVPI is (max(2, 0) + max(0, 3)) / 2 - max(1, 1.5) = 1.
        # Staff-time EVPI is (max(-60, -80) + max(-120, -80)) / 2 - max(-90, -80) = 10.
        # Adoption of 4 then 1, at 2 hours each and capacity 5, leaves backlog 3 then 0.
        report = run()
        self.assertEqual(report["paired_nmb_evpi"], 1.0)
        self.assertEqual(report["staff_time_evpi_per_assay"], 10.0)
        self.assertEqual(report["measurement_priority"], "staff_time_per_assay")
        self.assertEqual(report["capacity_exceeded_periods"], ["2026-01"])
        self.assertEqual(report["voiage_execution"], "not_executed")
        self.assertEqual(report["study_execution"], "not_executed")
        self.assertEqual(report["adoption_execution"], "externally_supplied_trajectory")
