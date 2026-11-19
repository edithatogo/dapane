"""Synthetic contract tests; live-provider qualification is a separate gate."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import unittest
from pathlib import Path

from dapane_mchs_atlas import AdapterError, evaluate, loads, prepare

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def fixture():
    return json.loads((FIXTURES / "parallel-views.json").read_text())


class DiagnosticAssertions(unittest.TestCase):
    def assert_rejected(self, data, code):
        with self.assertRaises(AdapterError) as raised:
            prepare(data)
        self.assertEqual(raised.exception.code, code)
        self.assertTrue(raised.exception.path.startswith("/"))


class ContractTests(DiagnosticAssertions):
    def test_preparation_keeps_economic_views_and_metadata_separate(self):
        data = fixture()
        original = copy.deepcopy(data)
        prepared = prepare(data)
        self.assertEqual(data, original)
        self.assertEqual(set(prepared["requests"]), {"funding", "tariff", "resource_cost"})
        self.assertNotIn("total", prepared)
        funding = prepared["requests"]["funding"]
        self.assertEqual(funding["policy"]["basis"], "funding")
        self.assertTrue(all(row["kind"] == "activity_measure" for row in funding["usage"]))
        self.assertEqual(funding["policy"]["price_year"], 2024)
        self.assertEqual(funding["quotes"][0]["known_from"], "2026-01-01")
        saved = prepared["provenance"]["activities"][0]
        self.assertEqual(saved["context"]["pricing_edition"], "synthetic-NEP26")
        self.assertEqual(saved["context"]["classification_edition"], "fixture-v1")
        self.assertEqual(saved["result"]["total_funding"], "999.99")
        self.assertEqual(prepared["payments"][0]["amount"], "40.00")
        data["activities"][0]["context"]["pricing_edition"] = "mutated-after-prepare"
        self.assertEqual(saved["context"]["pricing_edition"], "synthetic-NEP26")

    def test_all_fixture_source_digests_match_synthetic_bytes(self):
        raw = (FIXTURES / "source-synthetic.json").read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        source = json.loads(raw)
        pack = fixture()["quote_packs"][0]
        self.assertEqual(pack["snapshot"]["checksum_sha256"], digest)
        self.assertEqual(pack["source_version"]["checksum_sha256"], digest)
        for quote in pack["quotes"]:
            self.assertEqual(quote["exact"]["snapshot_sha256"], digest)
            self.assertEqual(quote["exact"]["amount"], source[quote["exact"]["source_field"]])

    def test_missing_rate_never_uses_upstream_default_or_total_funding(self):
        data = fixture()
        data["views"][0]["selections"][0]["quote_id"] = "absent"
        self.assert_rejected(data, "missing_quote")

    def test_unknown_fields_revisions_and_methods_fail_closed(self):
        cases = [
            (lambda d: d.update(extra=True), "unknown_field"),
            (
                lambda d: d["activities"][0].update(provider_revision="0" * 40),
                "provider_revision",
            ),
            (
                lambda d: d["quote_packs"][0].update(provider_revision="0" * 40),
                "provider_revision",
            ),
            (
                lambda d: d["activities"][0].update(method="calculate_acute_2025"),
                "unsupported_method",
            ),
            (lambda d: d["activities"][0]["result"].update(unknown="1"), "unknown_field"),
        ]
        for mutate, code in cases:
            with self.subTest(code=code):
                data = fixture()
                mutate(data)
                self.assert_rejected(data, code)

    def test_provider_error_is_not_a_zero_activity(self):
        data = fixture()
        data["activities"][0]["result"].update(error_code=1, nwau="0")
        self.assert_rejected(data, "provider_error")

    def test_exact_transport_rejects_float_and_other_lossy_values(self):
        for value in [2.5, 2, True, None, "NaN", "1e2", "-1", " 2", "2."]:
            with self.subTest(value=value):
                data = fixture()
                data["activities"][0]["result"]["nwau"] = value
                self.assert_rejected(data, "invalid_exact")

    def test_atlas_normalized_float_is_not_recovered_by_stringifying(self):
        data = fixture()
        data["quote_packs"][0]["quotes"][0]["item"]["payment_amount"] = 17.0
        self.assert_rejected(data, "lossy_atlas_amount")

    def test_missing_exact_evidence_is_not_a_zero_quote(self):
        data = fixture()
        del data["quote_packs"][0]["quotes"][0]["exact"]
        self.assert_rejected(data, "missing_field")

    def test_zero_amount_and_zero_activity_are_explicitly_allowed(self):
        data = fixture()
        data["activities"][0]["result"]["nwau"] = "0"
        data["quote_packs"][0]["quotes"][0]["exact"]["amount"] = "0"
        prepared = prepare(data)
        self.assertEqual(prepared["requests"]["funding"]["usage"][0]["quantity"], "0")

    def test_unknown_rights_and_synthetic_official_promotion_are_rejected(self):
        for location in ("activity", "atlas", "payment"):
            data = fixture()
            source = {
                "activity": data["activities"][0]["source"],
                "atlas": data["quote_packs"][0]["metadata"],
                "payment": data["payments"][0]["source"],
            }[location]
            source["rights"]["status"] = "unknown"
            with self.subTest(location=location):
                self.assert_rejected(data, "source_rights")
        data = fixture()
        data["quote_packs"][0]["metadata"]["official_status"] = "official"
        self.assert_rejected(data, "source_status")

    def test_source_release_snapshot_and_item_identity_cannot_drift(self):
        for section, field, value in [
            ("snapshot", "source_version_id", "other"),
            ("snapshot", "checksum_sha256", "0" * 64),
            ("source_version", "source_id", "other"),
        ]:
            with self.subTest(section=section, field=field):
                data = fixture()
                data["quote_packs"][0][section][field] = value
                self.assert_rejected(data, "source_mismatch")
        data = fixture()
        data["quote_packs"][0]["quotes"][0]["exact"]["snapshot_sha256"] = "0" * 64
        self.assert_rejected(data, "source_mismatch")

    def test_applicability_is_half_open_and_knowledge_is_independent(self):
        for service_date in ("2027-01-01", "2025-12-31"):
            data = fixture()
            data["activities"][0]["service_date"] = service_date
            self.assert_rejected(data, "stale_quote")
        data = fixture()
        data["quote_packs"][0]["metadata"]["known_from"] = "2026-07-01"
        self.assert_rejected(data, "not_known")

    def test_classification_and_pricing_editions_are_exact_match_boundaries(self):
        for field in ("classification_edition", "pricing_edition", "classification_system"):
            with self.subTest(field=field):
                data = fixture()
                data["activities"][0]["context"][field] += "-other"
                self.assert_rejected(data, "incompatible_quote")

    def test_quote_kind_basis_and_unit_are_not_coerced(self):
        data = fixture()
        data["views"][0]["policy"]["basis"] = "economic_cost"
        self.assert_rejected(data, "view_basis")
        data = fixture()
        data["quote_packs"][0]["quotes"][0]["application"]["unit"] = "hour"
        self.assert_rejected(data, "incompatible_quote")
        data = fixture()
        data["quote_packs"][0]["quotes"][0]["application"]["view"] = "resource_cost"
        self.assert_rejected(data, "unsupported_view")

    def test_ambiguous_end_dates_restrictions_and_patient_components_are_rejected(self):
        data = fixture()
        data["quote_packs"][0]["metadata"]["effective_to_convention"] = "unknown"
        self.assert_rejected(data, "date_convention")
        for field, value in [
            ("restriction_text", "only in eligible settings"),
            ("patient_amount", 1.0),
        ]:
            data = fixture()
            data["quote_packs"][0]["quotes"][0]["item"][field] = value
            self.assert_rejected(data, "unsupported_item")

    def test_resource_cost_view_cannot_contain_activity_measures(self):
        data = fixture()
        data["resource_cost"]["usage"][0]["kind"] = "activity_measure"
        self.assert_rejected(data, "resource_view")

    def test_payment_requires_observation_or_named_model(self):
        data = fixture()
        data["payments"][0]["observation_ref"] = None
        self.assert_rejected(data, "payment_evidence")
        data = fixture()
        data["payments"][0].update(
            record_kind="model", observation_ref=None, model={"id": "demo", "version": "1"}
        )
        self.assertEqual(prepare(data)["payments"][0]["record_kind"], "model")

    def test_duplicate_and_unpriced_activity_identities_fail(self):
        data = fixture()
        data["activities"].append(copy.deepcopy(data["activities"][0]))
        self.assert_rejected(data, "duplicate_id")
        data = fixture()
        other = copy.deepcopy(data["activities"][0])
        other["id"] = "other"
        data["activities"].append(other)
        self.assert_rejected(data, "unpriced_activity")

    def test_json_rejects_duplicate_keys_nonfinite_and_excessive_depth(self):
        for payload in [
            '{"profile":"a","profile":"b"}',
            '{"amount":NaN}',
            "[" * 70 + "0" + "]" * 70,
        ]:
            with self.subTest(payload=payload[:50]), self.assertRaises(AdapterError):
                loads(payload)


class NativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cli = os.environ.get("DAPANE_TEST_CLI")
        if not cls.cli:
            raise RuntimeError(
                "Set DAPANE_TEST_CLI to a qualified native Dapane CLI; no silent skips."
            )

    def engine(self, request):
        result = subprocess.run(
            [self.cli, "evaluate", "-"],
            input=json.dumps(request),
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )
        if result.returncode:
            diagnostic = json.loads(result.stderr)
            raise AdapterError(diagnostic["code"], diagnostic["message"], diagnostic["path"])
        return json.loads(result.stdout)

    def test_independent_parallel_results_and_no_default_sum(self):
        result = evaluate(fixture(), evaluator=self.engine)
        expected = json.loads((FIXTURES / "expected.json").read_text())
        for view in ("funding", "tariff", "resource_cost"):
            self.assertEqual(result["views"][view]["totals"]["rounded"], expected[view])
        self.assertEqual(
            result["views"]["payment"]["records"][0]["amount"], expected["payment_amount"]
        )
        self.assertEqual(result["views"]["payment"]["aggregation"], "not_performed")
        self.assertNotIn("totals", result)
        self.assertNotIn("total", result["views"]["payment"])
        self.assertEqual(result["status"], "complete")

    def test_activity_only_funding_generates_zero_resource_use_rows(self):
        data = fixture()
        data["resource_cost"] = None
        data["resource_sources"] = []
        data["payments"] = []
        data["views"] = data["views"][:1]
        result = evaluate(data, evaluator=self.engine)
        self.assertEqual(set(result["views"]), {"funding"})
        self.assertEqual(result["views"]["funding"]["totals"]["rounded"], "42.50")
        self.assertTrue(
            all(row["kind"] == "activity_measure" for row in result["views"]["funding"]["lines"])
        )

    def test_half_even_is_owned_by_the_unchanged_rust_engine(self):
        data = fixture()
        data["activities"][0]["result"]["nwau"] = "1"
        data["quote_packs"][0]["quotes"][0]["exact"]["amount"] = "0.005"
        data["quote_packs"][0]["quotes"][1]["exact"]["amount"] = "0.015"
        result = evaluate(data, evaluator=self.engine)
        self.assertEqual(result["views"]["funding"]["totals"]["rounded"], "0.00")
        self.assertEqual(result["views"]["tariff"]["totals"]["rounded"], "0.02")
        self.assertEqual(result["views"]["funding"]["method_version"], "dapane-exact-v0.1.0")

    def test_failures_never_return_a_partial_complete_view(self):
        data = fixture()
        data["resource_cost"]["usage"][0]["quantity"] = {"numerator": "1", "denominator": "0"}
        with self.assertRaises(AdapterError):
            evaluate(data, evaluator=self.engine)

    def test_core_still_rejects_double_counted_components(self):
        data = fixture()
        data["views"][0]["selections"].append(
            dict(data["views"][0]["selections"][0], line_id="duplicate")
        )
        with self.assertRaises(AdapterError):
            evaluate(data, evaluator=self.engine)

    def test_rational_quote_denominator_is_preserved_for_native_evaluation(self):
        data = fixture()
        data["quote_packs"][0]["quotes"][0]["exact"]["amount"] = {
            "numerator": "1",
            "denominator": "3",
        }
        data["quote_packs"][0]["quotes"][0]["exact"]["per_quantity"] = "2"
        result = evaluate(data, evaluator=self.engine)
        self.assertEqual(
            result["views"]["funding"]["totals"]["exact"], {"numerator": "5", "denominator": "12"}
        )
        self.assertEqual(result["views"]["funding"]["totals"]["rounded"], "0.42")


class ReviewRegressionTests(DiagnosticAssertions):
    """Additional semantic failures found during review, without provider records."""

    def test_resource_cost_requires_matching_rights_and_status_evidence(self):
        data = fixture()
        del data["resource_sources"]
        self.assert_rejected(data, "source_rights")
        data = fixture()
        data["resource_sources"][0]["rights"]["status"] = "unknown"
        self.assert_rejected(data, "source_rights")
        data = fixture()
        data["resource_sources"][0]["content_digest"] = "sha256:" + "0" * 64
        self.assert_rejected(data, "source_mismatch")

    def test_future_payment_cannot_be_relabelled_as_an_observation(self):
        data = fixture()
        data["payments"][0]["date"] = "2026-07-01"
        self.assert_rejected(data, "payment_evidence")

    def test_missing_rights_fields_and_unqualified_parser_status_fail(self):
        data = fixture()
        del data["quote_packs"][0]["metadata"]["rights"]
        self.assert_rejected(data, "missing_field")
        for status in ("planned", "stubbed", "unknown", None):
            data = fixture()
            data["quote_packs"][0]["source_version"]["parser_status"] = status
            self.assert_rejected(data, "source_status")

    def test_quote_end_boundary_start_boundary_and_invalid_dates(self):
        data = fixture()
        data["activities"][0]["service_date"] = "2026-01-01"
        self.assertEqual(prepare(data)["status"], "prepared")
        for invalid in ("2026-02-30", "2026-1-01", "0000-01-01"):
            data = fixture()
            data["activities"][0]["service_date"] = invalid
            self.assert_rejected(data, "invalid_date")

    def test_denominator_precision_and_truthy_nonintegers_are_rejected(self):
        for value in ["0", "0.0", {"numerator": "1", "denominator": "0"}]:
            data = fixture()
            data["quote_packs"][0]["quotes"][0]["exact"]["per_quantity"] = value
            self.assert_rejected(data, "invalid_exact")
        data = fixture()
        data["activities"][0]["result"]["error_code"] = False
        self.assert_rejected(data, "invalid_integer")
        for value in ["1" * 97, "0." + "1" * 37]:
            data = fixture()
            data["quote_packs"][0]["quotes"][0]["exact"]["amount"] = value
            self.assert_rejected(data, "invalid_exact")

    def test_every_requested_view_needs_all_activities_and_a_unique_name(self):
        data = fixture()
        data["views"][0]["selections"] = []
        self.assert_rejected(data, "missing_input")
        data = fixture()
        data["views"].append(copy.deepcopy(data["views"][0]))
        self.assert_rejected(data, "duplicate_id")

    def test_payment_observation_is_not_duplicated_under_another_id(self):
        data = fixture()
        data["payments"].append(dict(data["payments"][0], id="alias"))
        self.assert_rejected(data, "duplicate_id")

    def test_incompatible_native_report_cannot_acquire_complete_status(self):
        for report in [{}, {"status": "partial"}, {"status": "complete", "policy": {}}]:
            with self.subTest(report=report), self.assertRaises(AdapterError) as error:
                evaluate(fixture(), evaluator=lambda request: report)
            self.assertEqual(error.exception.code, "invalid_native_report")

    def test_preparation_rejects_cycles_and_unsupported_host_objects(self):
        data = fixture()
        data["payments"].append(data)
        self.assert_rejected(data, "invalid_transport")
        data = fixture()
        data["activities"][0]["id"] = object()
        self.assert_rejected(data, "invalid_transport")


if __name__ == "__main__":
    unittest.main()
