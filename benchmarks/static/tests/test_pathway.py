"""Literal expectations for the object-centric and flattened comparison."""

import unittest
from fractions import Fraction

from benchmarks.static.pathway import representations


class PathwayTests(unittest.TestCase):
    def test_shared_batch_is_counted_once_only_in_the_object_centric_view(self):
        report = representations()["shared_batch"]
        # 30.00 + 3.00 + one 5.05 batch = 38.05. A copy on each recipient is 43.10.
        self.assertEqual(report["object_centric_rounded"], "38.05")
        self.assertEqual(report["flattened_rounded"], "43.10")
        self.assertEqual(report["object_centric_batch_lines"], 1)
        self.assertEqual(report["flattened_batch_lines"], 2)

    def test_repeat_labour_does_not_copy_the_shared_batch(self):
        report = representations()["repeat"]
        # Another 30.00 of labour: 68.05 object-centric, 73.10 if the batch is copied too.
        self.assertEqual(report["object_centric_rounded"], "68.05")
        self.assertEqual(report["flattened_rounded"], "73.10")

    def test_flattened_capacity_multiplies_the_same_instrument_hour(self):
        report = representations()["capacity"]
        self.assertEqual(report["object_centric_hours"], Fraction(1, 2))
        self.assertEqual(report["flattened_hours"], Fraction(1))
        self.assertEqual(report["object_centric_cost"], Fraction(45))
        self.assertEqual(report["flattened_cost"], Fraction(90))
        self.assertEqual(report["oracle"], "Unqualified oracle scope: capacity_allocations")
