"""Synthetic acceptance; DAPANE_BENCH_CLI is mandatory for native cases."""

import json
import os
import unittest
from copy import deepcopy
from decimal import ROUND_HALF_EVEN, Decimal
from fractions import Fraction
from pathlib import Path

from benchmarks.static.cache import Incremental, NativeCli, NativeRejection, WorkItem, full
from benchmarks.static.common import Failure, canonical, load, require
from benchmarks.static.oracle import check, number, point_reference
from benchmarks.static.suite import FIXTURES, mutations, portfolio, scenario


class FakeCli:
    """Transport-only double with no valuation logic."""

    def __init__(self):
        self.identity = "binary-a"
        self.calls = 0

    def fingerprint(self):
        return self.identity

    def invoke(self, item):
        self.calls += 1
        if item.payload == b"reject":
            raise NativeRejection({"code": "synthetic_error", "message": "bad", "path": "/"})
        return canonical({"command": item.command, "input": item.payload.decode()})


def item(value, command="evaluate"):
    return WorkItem(command, canonical(value))


class ReferenceTests(unittest.TestCase):
    def test_authored_point_and_pool(self):
        ref = point_reference(load(FIXTURES / "point.json"))
        self.assertEqual(ref["totals"]["rounded"], "38.05")
        self.assertEqual(ref["objects"]["a"]["total"], "32.53")
        self.assertEqual(ref["objects"]["b"]["total"], "5.52")
        self.assertEqual(ref["allocations"]["shared"]["shares"]["a"]["rounded"], "2.53")

    def test_line_half_even_is_not_aggregate_rounding(self):
        request = load(FIXTURES / "point-ties.json")
        ref = point_reference(request)
        self.assertEqual(ref["lines"]["a"]["rounded"], "0.00")
        self.assertEqual(ref["lines"]["b"]["rounded"], "0.02")
        request["quotes"][1]["amount"] = "0.005"
        ref = point_reference(request)
        self.assertEqual(ref["totals"]["rounded"], "0.00")
        self.assertEqual(ref["totals"]["exact"], {"numerator": "1", "denominator": "100"})

    def test_fraction_rounding_matches_independent_decimal_ties(self):
        for numerator in range(1, 401, 2):
            with self.subTest(numerator=numerator):
                exact = Fraction(numerator, 200)
                decimal = Decimal(numerator) / Decimal(200)
                self.assertEqual(
                    round(exact * 100),
                    int(decimal.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN) * 100),
                )

    def test_binary_float_and_nonfinite_are_rejected_by_reference_transport(self):
        for value in (0.1, float("nan"), True, 1):
            with self.subTest(value=value):
                with self.assertRaises(Failure):
                    number(value)

    def test_missing_is_not_converted_to_zero(self):
        request = load(FIXTURES / "point.json")
        del request["usage"][0]["quantity"]
        with self.assertRaises((KeyError, Failure)):
            point_reference(request)

    def test_reference_rejects_unqualified_scope(self):
        request = load(FIXTURES / "point.json")
        request["schema_version"] = "0.2"
        with self.assertRaises(Failure):
            point_reference(request)


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.runner = FakeCli()
        self.cache = Incremental(self.runner)
        self.base = {"a": item({"quantity": "1"}), "b": item({"quantity": "2"})}

    def test_cold_and_warm_full_report_identity(self):
        reference = full(self.runner, self.base)
        cold = self.cache.evaluate(self.base)
        warm = self.cache.evaluate(self.base)
        self.assertEqual(cold.reports, reference.reports)
        self.assertEqual(warm.reports, reference.reports)
        self.assertEqual((cold.native_calls, warm.native_calls, warm.hits), (2, 0, 2))

    def test_entire_payload_and_command_participate(self):
        self.cache.evaluate(self.base)
        for replacement in (
            item({"quantity": "1", "source": {"version": "2"}}),
            item({"quantity": "1", "unused_quotes": ["changed"]}),
            item({"quantity": "1"}, "evaluate-intervals"),
            WorkItem("evaluate", b'{ "quantity" : "1" }'),
        ):
            with self.subTest(replacement=replacement):
                changed = {**self.base, "a": replacement}
                got = self.cache.evaluate(changed)
                self.assertEqual(got.native_calls, 1)
                self.assertEqual(got.reports, full(self.runner, changed).reports)
                self.cache.evaluate(self.base)

    def test_binary_identity_change_invalidates_all(self):
        self.cache.evaluate(self.base)
        self.runner.identity = "binary-b"
        self.assertEqual(self.cache.evaluate(self.base).native_calls, 2)

    def test_transactional_failure_and_recovery(self):
        baseline = self.cache.evaluate(self.base)
        changed = {"a": item({"quantity": "3"}), "z": WorkItem("evaluate", b"reject")}
        with self.assertRaises(NativeRejection):
            self.cache.evaluate(changed)
        replay = self.cache.evaluate(self.base)
        self.assertEqual(replay.native_calls, 0)
        self.assertEqual(replay.reports, baseline.reports)
        recovery = self.cache.evaluate({**self.base, "a": changed["a"]})
        self.assertEqual(recovery.native_calls, 1)

    def test_cached_reports_cannot_be_mutated_through_returned_map(self):
        expected = full(self.runner, self.base).reports
        result = self.cache.evaluate(self.base)
        result.reports["a"] = b"corrupted by caller"
        self.assertEqual(self.cache.evaluate(self.base).reports, expected)

    def test_removed_requests_are_evicted_and_empty_portfolio_is_explicit(self):
        self.cache.evaluate(self.base)
        trimmed = self.cache.evaluate({"a": self.base["a"]})
        self.assertEqual(trimmed.native_calls, 0)
        self.assertEqual(set(trimmed.reports), {"a"})
        self.assertEqual(self.cache.evaluate(self.base).native_calls, 1)
        empty = self.cache.evaluate({})
        self.assertEqual((empty.reports, empty.cache_payload_bytes), ({}, 0))
        self.assertEqual(self.cache.evaluate(self.base).native_calls, 2)

    def test_binary_change_during_batch_is_rejected_without_cache_commit(self):
        invoke = self.runner.invoke

        def replace_during_call(work):
            output = invoke(work)
            self.runner.identity = "changed-during-call"
            return output

        self.runner.invoke = replace_during_call
        with self.assertRaises(Failure):
            self.cache.evaluate(self.base)
        self.runner.invoke = invoke
        self.assertEqual(self.cache.evaluate(self.base).native_calls, 2)

    def test_unknown_commands_are_rejected_before_execution(self):
        with self.assertRaises(Failure):
            WorkItem("shell-command", b"{}")

    def test_binary_input_identity_is_not_lossy_json_normalization(self):
        a = WorkItem("evaluate", b'{"x":1}')
        b = WorkItem("evaluate", b'{"x":1,"x":2}')
        self.cache.evaluate({"one": a})
        self.assertEqual(self.cache.evaluate({"one": b}).native_calls, 1)


class NativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = os.environ.get("DAPANE_BENCH_CLI")
        require(path is not None, "Set DAPANE_BENCH_CLI; native acceptance must not silently skip")
        cls.runner = NativeCli(Path(path))

    def test_frozen_mutation_inventory_and_honest_nulls(self):
        result = mutations(self.runner)
        self.assertEqual(len(result["cases"]), 24)
        self.assertTrue(result["passed"])
        self.assertEqual(result["summary"]["source_truth"]["rejected"], 0)
        self.assertEqual(result["summary"]["source_truth"]["count"], 5)
        self.assertEqual(result["summary"]["control"]["rejected"], 0)

    def test_every_update_matches_full_reports_and_independent_oracle(self):
        protocol = load(FIXTURES.parent / "protocol.json")
        base = portfolio(8)
        for name in protocol["scenarios"]:
            with self.subTest(scenario=name):
                target, misses = scenario(base, name)
                cache = Incremental(self.runner)
                if name != "cold":
                    cache.evaluate(base)
                actual = cache.evaluate(target)
                expected = full(self.runner, target)
                self.assertEqual(actual.native_calls, misses)
                self.assertEqual(actual.reports, expected.reports)
                for key, report in actual.reports.items():
                    check(target[key].command, json.loads(target[key].payload), json.loads(report))

    def test_native_error_never_reuses_prior_valid_report(self):
        base = portfolio(2)
        cache = Incremental(self.runner)
        baseline = cache.evaluate(base)
        request = json.loads(base["request-0000"].payload)
        request["usage"][0]["unit"] = "wrong-unit"
        changed = {**base, "request-0000": item(request)}
        with self.assertRaises(NativeRejection) as error:
            cache.evaluate(changed)
        self.assertEqual(error.exception.diagnostic["code"], "quote_mismatch")
        after = cache.evaluate(base)
        self.assertEqual(after.native_calls, 0)
        self.assertEqual(after.reports, baseline.reports)

    def test_oracle_rejects_corrupted_line_even_when_total_is_retained(self):
        request = load(FIXTURES / "point.json")
        report = json.loads(self.runner.invoke(item(request)))
        altered = deepcopy(report)
        altered["lines"][0]["rounded"] = "999.00"
        with self.assertRaises(Failure):
            check("evaluate", request, altered)

    def test_reordered_input_retains_normalized_report_identity(self):
        a = WorkItem("evaluate", (FIXTURES / "cases/baseline.json").read_bytes())
        b = WorkItem("evaluate", (FIXTURES / "cases/valid-reorder.json").read_bytes())
        self.assertNotEqual(a.payload, b.payload)
        self.assertEqual(self.runner.invoke(a), self.runner.invoke(b))

    def test_interval_output_replays_through_unchanged_point_evaluator(self):
        request = load(FIXTURES / "interval.json")
        outer = json.loads(self.runner.invoke(item(request, "evaluate-intervals")))
        point = json.loads(self.runner.invoke(item(outer["expanded_request"])))
        self.assertEqual(point, outer["report"])
        self.assertEqual(point["totals"]["rounded"], "0.00")


if __name__ == "__main__":
    unittest.main()
