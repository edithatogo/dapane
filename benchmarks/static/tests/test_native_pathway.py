"""Literal oracles for shared consumption, repeats and unresolved capacity in the native pipeline."""

import os
import unittest

from benchmarks.static.native_pathway import run


class NativePathwayTests(unittest.TestCase):
    def test_native_representations(self):
        cli, process = os.environ.get("DAPANE_CLI"), os.environ.get("DAPANE_PROCESS_CLI")
        if not cli or not process:
            self.skipTest("Set both native CLI paths for the cross-adapter benchmark")
        cases = run(cli, process)
        # Shared batch costs 100 once, added repeat 20 once in either representation.
        # Capacity blocks cost 100 each; three recipients share two blocks above threshold.
        expected = {
            "composed-two-infant": ("150.00", "250.00", "0.00"),
            "failed-assay-repeat": ("170.00", "270.00", "0.00"),
            "capacity-at": ("120.00", "220.00", "0.00"),
            "capacity-above": ("230.00", "630.00", "50.00"),
            "capacity-unknown": ("120.00", "220.00", "100.00"),
            # The executed PNML trace has 12.5 minutes at 4 plus two packs at 15.
            "process-shared-batch": ("80.00", "160.00", "0.00"),
        }
        for name, (original, flat, residual) in expected.items():
            with self.subTest(name=name):
                case = cases[name]
                self.assertEqual(
                    (case["object_total"], case["flat_total"], case["object_unattributed"]),
                    (original, flat, residual),
                )
                self.assertEqual(case["flat_unattributed"], "0.00")
                self.assertGreater(case["flat_lines"], case["object_lines"])
        self.assertEqual(cases["process-shared-batch"]["trace_uses"], 3)
        self.assertEqual(cases["process-shared-batch"]["valued_uses"], 2)
