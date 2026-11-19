"""Negative-first tests for D3; every input and number is invented."""

from __future__ import annotations

import stat
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path

from study import (
    StudyError,
    canonical_digest,
    prepare_evidence_question,
    run_static_without_providers,
    verify_native_evpi_receipt,
)

SHA = "sha256:" + "a" * 64
PIN = "b" * 40
REF = "sha256:" + "c" * 64


def packet():
    keys = []
    matrix = [[-60.0, -80.0], [-120.0, -80.0]]
    for d in ("short", "long"):
        for s in ("change", "current"):
            keys.append(
                {
                    "scenario_id": "base",
                    "strategy_id": s,
                    "draw_id": d,
                    "replication_id": "one",
                    "perspective": "health_system",
                    "subgroup_id": "all",
                }
            )
    p = {
        "schema_version": "dapane-d2-voiage/0.1",
        "provider": {
            "provider": "edithatogo/voiage",
            "revision": PIN,
            "artifact_digest": SHA,
            "contract": "voiage-domain/ValueArray",
            "method": "evpi",
            "state": "prepared_not_executed",
        },
        "provider_execution": "not_executed",
        "input_d1_digest": REF,
        "group": {
            "scenario_id": "base",
            "replication_id": "one",
            "perspective": "health_system",
            "subgroup_id": "all",
        },
        "valuation": {
            "currency": "AUD",
            "price_year": 2026,
            "basis": "economic_cost",
            "unit": "currency",
            "source": {"id": "synthetic-cost-model", "version": "1", "digest": SHA},
        },
        "draw_id_order": ["short", "long"],
        "pair_keys": keys,
        "exact_net_benefit": [
            {"numerator": str(int(v)), "denominator": "1"} for row in matrix for v in row
        ],
        "value_array": {
            "value_array_id": "staff-time-voi",
            "sample_count": 2,
            "strategy_names": ["change", "current"],
            "net_benefit": matrix,
        },
        "conversion": {
            "method": "exact_rational_to_f64",
            "absolute_tolerance": "1e-9",
            "source": "external_valued_outcome",
        },
    }
    p["output_digest"] = canonical_digest(
        "dapane:d2-voiage:0.1\n", {k: v for k, v in p.items() if k != "output_digest"}
    )
    return p


def protocol():
    return {
        "schema_version": "dapane-d3-study/0.1",
        "study_id": "synthetic-laboratory-time-observation",
        "question": "Would perfect information about staff time change the preferred process?",
        "evidence_target": {
            "parameter_id": "staff_time_per_assay",
            "unit": "hour_per_assay",
            "uncertainty": "epistemic",
            "study_design": "prospective_time_and_motion",
            "measurement_likelihood": "not_supplied",
        },
        "perspective": {
            "name": "health_system",
            "currency": "AUD",
            "price_year": 2026,
            "basis": "economic_cost",
            "unit": "per_assay",
        },
        "data_status": {
            "resource": "synthetic",
            "clinical_outcomes": "not_modelled",
            "utilisation": "not_modelled",
            "rights": "not_assessed",
        },
        "design": {
            "strategies": ["change", "current"],
            "draws": ["short", "long"],
            "draw_weights": "equal",
            "replication_id": "one",
            "subgroup_id": "all",
        },
        "reference": {
            "method": "independently_derived_evpi",
            "per_assay": {"numerator": "10", "denominator": "1"},
            "proof_digest": SHA,
            "absolute_tolerance": "0.00000001",
        },
        "intent": "evpi_upper_bound_only",
    }


def receipt(prepared):
    return {
        "schema_version": "dapane-d3-native-evpi/0.1",
        "method": "voiage._runtime.compute_evpi",
        "input_digest": prepared["prepared_digest"],
        "provider_revision": PIN,
        "wheel_digest": SHA,
        "native_extension_digest": REF,
        "evpi_per_assay": 10.0,
        "execution": "native_extension_invoked",
        "source": "externally_run_installed_wheel",
    }


class PreparationTests(unittest.TestCase):
    def test_bounded_staff_time_plan_has_numeric_reference_without_new_evpi_method(self):
        q = prepare_evidence_question(packet(), protocol())
        self.assertEqual(q["question_type"], "value_of_perfect_information_upper_bound")
        self.assertEqual(q["value_array"]["net_benefit"], [[-60.0, -80.0], [-120.0, -80.0]])
        self.assertEqual(q["selected_native_entrypoint"], "voiage._runtime.compute_evpi")
        self.assertEqual(q["provider_execution"], "not_executed")
        self.assertEqual(q["reference_evpi_per_assay"], {"numerator": "10", "denominator": "1"})
        self.assertTrue(q["prepared_digest"].startswith("sha256:"))
        self.assertEqual(q["limitations"]["evsi_estimated"], False)

    def test_reproducible_prepared_digest(self):
        self.assertEqual(
            prepare_evidence_question(packet(), protocol()),
            prepare_evidence_question(packet(), protocol()),
        )

    def test_wrong_packet_digest_is_rejected(self):
        p = packet()
        p["value_array"]["net_benefit"][0][0] = -81.0
        with self.assertRaisesRegex(StudyError, "d2_digest_mismatch"):
            prepare_evidence_question(p, protocol())

    def test_wrong_provider_method_rejected_even_with_rehash(self):
        p = packet()
        p["provider"]["method"] = "evsi"
        p["output_digest"] = canonical_digest(
            "dapane:d2-voiage:0.1\n", {k: v for k, v in p.items() if k != "output_digest"}
        )
        with self.assertRaisesRegex(StudyError, "unsupported_provider_method"):
            prepare_evidence_question(p, protocol())

    def test_untrusted_provider_revision_rejected(self):
        p = packet()
        p["provider"]["revision"] = "main"
        p["output_digest"] = canonical_digest(
            "dapane:d2-voiage:0.1\n", {k: v for k, v in p.items() if k != "output_digest"}
        )
        with self.assertRaisesRegex(StudyError, "invalid_provider_revision"):
            prepare_evidence_question(p, protocol())

    def test_wrong_valuation_basis_rejected(self):
        d = protocol()
        d["perspective"]["basis"] = "public_expenditure"
        with self.assertRaisesRegex(StudyError, "perspective_mismatch"):
            prepare_evidence_question(packet(), d)

    def test_wrong_currency_rejected(self):
        d = protocol()
        d["perspective"]["currency"] = "NZD"
        with self.assertRaisesRegex(StudyError, "perspective_mismatch"):
            prepare_evidence_question(packet(), d)

    def test_wrong_price_year_rejected(self):
        d = protocol()
        d["perspective"]["price_year"] = 2025
        with self.assertRaisesRegex(StudyError, "perspective_mismatch"):
            prepare_evidence_question(packet(), d)

    def test_wrong_subgroup_rejected(self):
        d = protocol()
        d["design"]["subgroup_id"] = "other"
        with self.assertRaisesRegex(StudyError, "pairing_mismatch"):
            prepare_evidence_question(packet(), d)

    def test_wrong_draw_order_rejected(self):
        d = protocol()
        d["design"]["draws"].reverse()
        with self.assertRaisesRegex(StudyError, "pairing_mismatch"):
            prepare_evidence_question(packet(), d)

    def test_wrong_strategy_order_rejected(self):
        d = protocol()
        d["design"]["strategies"].reverse()
        with self.assertRaisesRegex(StudyError, "pairing_mismatch"):
            prepare_evidence_question(packet(), d)

    def test_row_position_permutation_rejected(self):
        p = packet()
        p["pair_keys"].reverse()
        p["output_digest"] = canonical_digest(
            "dapane:d2-voiage:0.1\n", {k: v for k, v in p.items() if k != "output_digest"}
        )
        with self.assertRaisesRegex(StudyError, "pairing_mismatch"):
            prepare_evidence_question(p, protocol())

    def test_tampered_exact_numbers_rejected(self):
        p = packet()
        p["exact_net_benefit"][0]["numerator"] = "-79"
        p["output_digest"] = canonical_digest(
            "dapane:d2-voiage:0.1\n", {k: v for k, v in p.items() if k != "output_digest"}
        )
        with self.assertRaisesRegex(StudyError, "numeric_mismatch"):
            prepare_evidence_question(p, protocol())

    def test_nonfinite_matrix_rejected(self):
        p = packet()
        p["value_array"]["net_benefit"][0][0] = float("nan")
        with self.assertRaisesRegex(StudyError, "invalid_number"):
            prepare_evidence_question(p, protocol())

    def test_surplus_strategy_columns_rejected(self):
        p = packet()
        p["value_array"]["net_benefit"][0].append(5)
        p["output_digest"] = canonical_digest(
            "dapane:d2-voiage:0.1\n", {k: v for k, v in p.items() if k != "output_digest"}
        )
        with self.assertRaisesRegex(StudyError, "invalid_matrix"):
            prepare_evidence_question(p, protocol())

    def test_no_unequal_draw_weights_without_methods(self):
        d = protocol()
        d["design"]["draw_weights"] = "nonuniform"
        with self.assertRaisesRegex(StudyError, "unsupported_weights"):
            prepare_evidence_question(packet(), d)

    def test_no_unverified_evsi_promotion(self):
        d = protocol()
        d["intent"] = "evsi"
        with self.assertRaisesRegex(StudyError, "unsupported_estimand"):
            prepare_evidence_question(packet(), d)

    def test_reject_empirical_claim_in_invented_fixture(self):
        d = protocol()
        d["data_status"]["resource"] = "empirical"
        with self.assertRaisesRegex(StudyError, "source_status"):
            prepare_evidence_question(packet(), d)

    def test_reject_clinical_outcome_claim_in_invented_fixture(self):
        d = protocol()
        d["data_status"]["clinical_outcomes"] = "observed"
        with self.assertRaisesRegex(StudyError, "source_status"):
            prepare_evidence_question(packet(), d)

    def test_reject_unknown_protocol_version(self):
        d = protocol()
        d["schema_version"] = "dapane-d3-study/0.2"
        with self.assertRaisesRegex(StudyError, "unsupported_schema"):
            prepare_evidence_question(packet(), d)

    def test_reject_invented_observation_likelihood(self):
        d = protocol()
        d["evidence_target"]["measurement_likelihood"] = "normal_model"
        with self.assertRaisesRegex(StudyError, "unsupported_measurement_model"):
            prepare_evidence_question(packet(), d)

    def test_no_auto_population_scaling(self):
        d = protocol()
        d["perspective"]["unit"] = "population"
        with self.assertRaisesRegex(StudyError, "unsupported_unit"):
            prepare_evidence_question(packet(), d)


class ProviderTests(unittest.TestCase):
    def test_matching_native_receipt_checked_but_not_assumed_qualified(self):
        q = prepare_evidence_question(packet(), protocol())
        r = verify_native_evpi_receipt(q, receipt(q), expected_wheel=SHA, expected_extension=REF)
        self.assertEqual(r["state"], "verified_declaration_not_installed_acceptance")
        self.assertEqual(r["evpi_per_assay"], 10.0)
        self.assertFalse(r["evsi_estimated"])

    def test_wrong_wheel_digest_rejected(self):
        q = prepare_evidence_question(packet(), protocol())
        with self.assertRaisesRegex(StudyError, "wheel_identity"):
            verify_native_evpi_receipt(q, receipt(q), expected_wheel=REF, expected_extension=REF)

    def test_d2_artifact_pin_cannot_be_replaced_by_consistent_self_claim(self):
        q = prepare_evidence_question(packet(), protocol())
        r = receipt(q)
        r["wheel_digest"] = REF
        with self.assertRaisesRegex(StudyError, "wheel_identity"):
            verify_native_evpi_receipt(q, r, expected_wheel=REF, expected_extension=REF)

    def test_wrong_native_module_digest_rejected(self):
        q = prepare_evidence_question(packet(), protocol())
        with self.assertRaisesRegex(StudyError, "native_identity"):
            verify_native_evpi_receipt(q, receipt(q), expected_wheel=SHA, expected_extension=SHA)

    def test_wrong_provider_revision_rejected(self):
        q = prepare_evidence_question(packet(), protocol())
        r = receipt(q)
        r["provider_revision"] = "a" * 40
        with self.assertRaisesRegex(StudyError, "revision_mismatch"):
            verify_native_evpi_receipt(q, r, expected_wheel=SHA, expected_extension=REF)

    def test_changed_input_digest_rejected(self):
        q = prepare_evidence_question(packet(), protocol())
        r = receipt(q)
        r["input_digest"] = REF
        with self.assertRaisesRegex(StudyError, "input_mismatch"):
            verify_native_evpi_receipt(q, r, expected_wheel=SHA, expected_extension=REF)

    def test_wrong_evpi_rejected(self):
        q = prepare_evidence_question(packet(), protocol())
        r = receipt(q)
        r["evpi_per_assay"] = 0.0
        with self.assertRaisesRegex(StudyError, "reference_mismatch"):
            verify_native_evpi_receipt(q, r, expected_wheel=SHA, expected_extension=REF)

    def test_nan_evpi_rejected(self):
        q = prepare_evidence_question(packet(), protocol())
        r = receipt(q)
        r["evpi_per_assay"] = float("nan")
        with self.assertRaisesRegex(StudyError, "invalid_number"):
            verify_native_evpi_receipt(q, r, expected_wheel=SHA, expected_extension=REF)

    def test_untrusted_python_fallback_rejected(self):
        q = prepare_evidence_question(packet(), protocol())
        r = receipt(q)
        r["execution"] = "numpy_fallback"
        with self.assertRaisesRegex(StudyError, "provider_execution"):
            verify_native_evpi_receipt(q, r, expected_wheel=SHA, expected_extension=REF)

    def test_unknown_method_rejected(self):
        q = prepare_evidence_question(packet(), protocol())
        r = receipt(q)
        r["method"] = "voiage._runtime.compute_evsi"
        with self.assertRaisesRegex(StudyError, "unsupported_method"):
            verify_native_evpi_receipt(q, r, expected_wheel=SHA, expected_extension=REF)

    def test_no_self_certifying_promotion(self):
        q = prepare_evidence_question(packet(), protocol())
        r = receipt(q)
        r["qualified"] = True
        with self.assertRaisesRegex(StudyError, "invalid_receipt"):
            verify_native_evpi_receipt(q, r, expected_wheel=SHA, expected_extension=REF)


class StaticTests(unittest.TestCase):
    def test_unavailable_native_binary_fails_closed(self):
        with self.assertRaisesRegex(StudyError, "native_unavailable"):
            run_static_without_providers(Path("/not-a-real-dapane-cli"), b"{}", SHA)

    def test_untrusted_native_binary_hash_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            exe = Path(d) / "dapane"
            exe.write_text("#!/bin/sh\necho true\n")
            exe.chmod(exe.stat().st_mode | stat.S_IXUSR)
            with self.assertRaisesRegex(StudyError, "native_binary_mismatch"):
                run_static_without_providers(exe, b"{}", SHA)

    def test_static_fallback_runs_only_pinned_explicit_binary(self):
        with tempfile.TemporaryDirectory() as d:
            exe = Path(d) / "dapane"
            exe.write_text(
                '#!/bin/sh\ncat >/dev/null\nprintf \'{"status":"complete","method_version":"dapane-exact-v0.1.0","output_digest":"sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"}\\n\'\n'
            )
            exe.chmod(exe.stat().st_mode | stat.S_IXUSR)
            digest = "sha256:" + sha256(exe.read_bytes()).hexdigest()
            result = run_static_without_providers(exe, b'{"schema_version":"0.1"}', digest)
            self.assertEqual(result["qualification"], "synthetic_process_only")
            self.assertEqual(result["native_report"]["status"], "complete")
            self.assertEqual(result["execution_mode"], "standalone_cli_no_optional_providers")

    def test_nonexistent_source_request_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            exe = Path(d) / "dapane"
            exe.write_text("#!/bin/sh\necho notjson\n")
            exe.chmod(exe.stat().st_mode | stat.S_IXUSR)
            dg = "sha256:" + sha256(exe.read_bytes()).hexdigest()
            with self.assertRaisesRegex(StudyError, "invalid_native_report"):
                run_static_without_providers(exe, b"{}", dg)


if __name__ == "__main__":
    unittest.main()
