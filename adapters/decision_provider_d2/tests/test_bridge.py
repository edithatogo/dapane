"""D2 negative-first contract cases. All identities and values are invented."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import unittest

from bridge import (
    D2Error,
    adoption_capacity,
    negotiate,
    paignia_game_solve_native,
    paignia_packet,
    voiage_packet,
)

HEX40 = "a" * 40
DIGEST = "sha256:" + "b" * 64
KEY_FIELDS = (
    "scenario_id",
    "strategy_id",
    "draw_id",
    "replication_id",
    "perspective",
    "subgroup_id",
)


def d1_fixture():
    results = []
    for strategy in ("alternative", "reference"):
        for draw in ("draw-a", "draw-b"):
            key = dict(zip(KEY_FIELDS, ("base", strategy, draw, "rep-1", "health_system", "all")))
            results.append(
                {
                    "key": key,
                    "outcome": {"key": key.copy(), "value": {"numerator": "1", "denominator": "1"}},
                    "cost_method": "point",
                    "cost_report": {"method": "dapane-point-v0.1", "cost": "not-used"},
                }
            )
    value = {
        "schema_version": "dapane-paired-draws/0.1",
        "method_version": "dapane-paired-draws-v0.1.0",
        "status": "complete",
        "run_id": "synthetic-d1",
        "draw_set_digest": DIGEST,
        "money": {
            "currency": "AUD",
            "price_year": 2026,
            "basis": "economic_cost",
            "rounding": {"scale": 2, "mode": "half_even"},
        },
        "design": {
            "scenarios": ["base"],
            "strategies": ["alternative", "reference"],
            "replications": ["rep-1"],
            "perspectives": ["health_system"],
            "subgroups": ["all"],
            "replication_axis": "conditional_replication",
        },
        "draws": {"rows": [{"draw_id": "draw-a"}, {"draw_id": "draw-b"}]},
        "outcome_contract": {"measure_id": "qaly", "unit": "QALY"},
        "rows": results,
    }
    value["output_digest"] = sha("dapane:paired-output:0.1\n", value)
    return value


def sha(prefix, value):
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256((prefix + data).encode()).hexdigest()


def provider(repo, contract, method):
    return {
        "repository": repo,
        "revision": HEX40,
        "artifact_digest": DIGEST,
        "contract": contract,
        "method": method,
    }


def d2_voiage(d1):
    values = [
        ("alternative", "draw-a", "2"),
        ("alternative", "draw-b", "0"),
        ("reference", "draw-a", "0"),
        ("reference", "draw-b", "3"),
    ]
    return {
        "provider": provider("edithatogo/voiage", "voiage-domain/ValueArray", "evpi"),
        "group": {
            "scenario_id": "base",
            "replication_id": "rep-1",
            "perspective": "health_system",
            "subgroup_id": "all",
        },
        "valuation": {
            "currency": "AUD",
            "price_year": 2026,
            "basis": "economic_cost",
            "unit": "currency",
            "source": {"id": "synthetic-nmb-model", "version": "1", "digest": DIGEST},
        },
        "value_array_id": "paired-nmb-base",
        "net_benefits": [
            {
                "key": dict(
                    zip(KEY_FIELDS, ("base", strategy, draw, "rep-1", "health_system", "all"))
                ),
                "value": {"numerator": amount, "denominator": "1"},
            }
            for strategy, draw, amount in values
        ],
    }


def d2_innovate():
    return {
        "schema_version": "dapane-d2-innovate/0.1",
        "provider": provider(
            "edithatogo/innovate", "declared-innovation-trajectory/0.1", "provided_trajectory"
        ),
        "run_id": "synthetic-volume",
        "iteration": 0,
        "previous_evaluation_digest": None,
        "key": dict(
            zip(KEY_FIELDS, ("base", "reference", "draw-a", "rep-1", "health_system", "all"))
        ),
        "resource": {
            "id": "laboratory-time",
            "unit": "staff_hours",
            "quantity_per_adoption": {"numerator": "2", "denominator": "1"},
            "capacity_per_period": {"numerator": "5", "denominator": "1"},
        },
        "observations": [
            {"period": "2026-01", "new_adoptions": 4},
            {"period": "2026-02", "new_adoptions": 1},
        ],
        "feedback": {"price_affects_adoption": False, "mode": "none", "valuation_digest": None},
    }


def d2_paignia():
    return {
        "schema_version": "dapane-d2-paignia/0.1",
        "provider": provider(
            "edithatogo/paignia",
            "paignia/static-finite-perfect-information-sparse-zero/1.0.0",
            "static_game_input",
        ),
        "game_id": "synthetic-adoption-choice",
        "player_id": "planner",
        "key": dict(
            zip(KEY_FIELDS, ("base", "reference", "draw-a", "rep-1", "health_system", "all"))
        ),
        "payoff_mapping": {
            "source_digest": DIGEST,
            "method": "explicit_assessed_utility",
            "unit": "utility",
            "price_basis": "not_applicable",
            "transfer_treatment": "excluded",
            "domestic_transfer_balance": {"numerator": "0", "denominator": "1"},
        },
        "actions": [
            {"id": "adopt", "utility": {"numerator": "3", "denominator": "2"}},
            {"id": "hold", "utility": {"numerator": "0", "denominator": "1"}},
        ],
    }


class TestD2Bridge(unittest.TestCase):
    def test_voiage_matrix_preserves_draw_and_strategy_pairing(self):
        d1 = d1_fixture()
        packet = voiage_packet(json.dumps(d1), d1["output_digest"], d2_voiage(d1))
        self.assertEqual(packet["value_array"]["strategy_names"], ["alternative", "reference"])
        self.assertEqual(packet["value_array"]["net_benefit"], [[2.0, 0.0], [0.0, 3.0]])
        self.assertEqual(packet["pair_keys"][0]["draw_id"], "draw-a")
        self.assertEqual(packet["group"]["subgroup_id"], "all")
        self.assertEqual(packet["provider_execution"], "not_executed")
        self.assertEqual(packet["input_d1_digest"], d1["output_digest"])
        self.assertTrue(packet["output_digest"].startswith("sha256:"))
        # Independent EVPI analytic reference: (max(2,0)+max(0,3))/2 - max(1,1.5) = 1.
        matrix = packet["value_array"]["net_benefit"]
        reference = sum(max(row) for row in matrix) / len(matrix) - max(
            sum(row[i] for row in matrix) / len(matrix) for i in range(2)
        )
        self.assertEqual(reference, 1.0)

    def test_voiage_permutation_invariance(self):
        d1 = d1_fixture()
        p = d2_voiage(d1)
        a = voiage_packet(json.dumps(d1), d1["output_digest"], p)
        p["net_benefits"].reverse()
        d1["rows"].reverse()
        d1["output_digest"] = sha(
            "dapane:paired-output:0.1\n", {k: v for k, v in d1.items() if k != "output_digest"}
        )
        b = voiage_packet(json.dumps(d1), d1["output_digest"], p)
        self.assertEqual(a["value_array"], b["value_array"])
        self.assertNotEqual(a["input_d1_digest"], b["input_d1_digest"])

    def test_voiage_rejects_wrong_selected_digest(self):
        d1 = d1_fixture()
        with self.assertRaisesRegex(D2Error, "d1_digest_mismatch"):
            voiage_packet(json.dumps(d1), DIGEST, d2_voiage(d1))

    def test_voiage_rejects_tampered_d1(self):
        d1 = d1_fixture()
        expected = d1["output_digest"]
        d1["rows"][0]["outcome"]["value"]["numerator"] = "99"
        with self.assertRaisesRegex(D2Error, "d1_digest_mismatch"):
            voiage_packet(json.dumps(d1), expected, d2_voiage(d1))

    def test_voiage_rejects_bad_outcome_pairing_even_if_rehashed(self):
        d1 = d1_fixture()
        d1["rows"][0]["outcome"]["key"]["draw_id"] = "incorrect"
        d1["output_digest"] = sha(
            "dapane:paired-output:0.1\n", {k: v for k, v in d1.items() if k != "output_digest"}
        )
        with self.assertRaisesRegex(D2Error, "d1_pairing_mismatch"):
            voiage_packet(json.dumps(d1), d1["output_digest"], d2_voiage(d1))

    def test_voiage_rejects_incomplete_keyset(self):
        d1 = d1_fixture()
        p = d2_voiage(d1)
        p["net_benefits"].pop()
        with self.assertRaisesRegex(D2Error, "pairing_mismatch"):
            voiage_packet(json.dumps(d1), d1["output_digest"], p)

    def test_voiage_rejects_duplicate_benefits(self):
        d1 = d1_fixture()
        p = d2_voiage(d1)
        p["net_benefits"][1] = copy.deepcopy(p["net_benefits"][0])
        with self.assertRaisesRegex(D2Error, "pairing_mismatch"):
            voiage_packet(json.dumps(d1), d1["output_digest"], p)

    def test_voiage_rejects_mismatched_price_year(self):
        d1 = d1_fixture()
        p = d2_voiage(d1)
        p["valuation"]["price_year"] = 2025
        with self.assertRaisesRegex(D2Error, "money_context"):
            voiage_packet(json.dumps(d1), d1["output_digest"], p)

    def test_voiage_rejects_nonrepresentable_large_f64(self):
        d1 = d1_fixture()
        p = d2_voiage(d1)
        p["net_benefits"][0]["value"]["numerator"] = str(2**63 + 5)
        with self.assertRaisesRegex(D2Error, "precision_loss"):
            voiage_packet(json.dumps(d1), d1["output_digest"], p)

    def test_voiage_rejects_unsupported_method(self):
        d1 = d1_fixture()
        p = d2_voiage(d1)
        p["provider"]["method"] = "evsi"
        with self.assertRaisesRegex(D2Error, "unsupported_method"):
            voiage_packet(json.dumps(d1), d1["output_digest"], p)

    def test_d2_rejects_duplicate_json_keys_and_floating_json_numbers(self):
        d1 = d1_fixture()
        p = d2_voiage(d1)
        with self.assertRaisesRegex(D2Error, "duplicate_key"):
            voiage_packet(
                '{"schema_version":"dapane-paired-draws/0.1","schema_version":"oops"}',
                d1["output_digest"],
                p,
            )
        with self.assertRaisesRegex(D2Error, "invalid_json_number"):
            voiage_packet('{"a":3.5}', d1["output_digest"], p)

    def test_adoption_capacity_exact_backlog_and_threshold(self):
        r = adoption_capacity(d2_innovate())
        self.assertEqual(
            [x["demand"] for x in r["periods"]],
            [{"numerator": "8", "denominator": "1"}, {"numerator": "5", "denominator": "1"}],
        )
        self.assertEqual(
            [x["served"] for x in r["periods"]],
            [{"numerator": "5", "denominator": "1"}, {"numerator": "5", "denominator": "1"}],
        )
        self.assertEqual(
            [x["backlog"] for x in r["periods"]],
            [{"numerator": "3", "denominator": "1"}, {"numerator": "0", "denominator": "1"}],
        )
        self.assertEqual([x["capacity_exceeded"] for x in r["periods"]], [True, False])
        self.assertEqual(r["provider_execution"], "externally_supplied_trajectory")

    def test_adoption_rejects_unacknowledged_price_feedback(self):
        p = d2_innovate()
        p["feedback"]["price_affects_adoption"] = True
        with self.assertRaisesRegex(D2Error, "feedback_requires_external_revision"):
            adoption_capacity(p)

    def test_adoption_feedback_requires_previous_digest(self):
        p = d2_innovate()
        p["iteration"] = 1
        p["feedback"] = {
            "price_affects_adoption": True,
            "mode": "external_recomputed",
            "valuation_digest": DIGEST,
        }
        with self.assertRaisesRegex(D2Error, "feedback_chain"):
            adoption_capacity(p, expected_previous_digest=DIGEST)

    def test_adoption_feedback_accepts_explicit_revision_receipt(self):
        prior = adoption_capacity(d2_innovate())
        p = d2_innovate()
        p["iteration"] = 1
        p["previous_evaluation_digest"] = prior["output_digest"]
        p["feedback"] = {
            "price_affects_adoption": True,
            "mode": "external_recomputed",
            "valuation_digest": DIGEST,
        }
        r = adoption_capacity(p, expected_previous_digest=prior["output_digest"])
        self.assertEqual(r["previous_evaluation_digest"], prior["output_digest"])
        self.assertEqual(r["feedback_mode"], "external_recomputed")

    def test_adoption_rejects_duplicate_periods(self):
        p = d2_innovate()
        p["observations"][1]["period"] = "2026-01"
        with self.assertRaisesRegex(D2Error, "invalid_period_sequence"):
            adoption_capacity(p)

    def test_adoption_rejects_missing_native_provenance(self):
        p = d2_innovate()
        p["provider"].pop("revision")
        with self.assertRaisesRegex(D2Error, "invalid_provider"):
            adoption_capacity(p)

    def test_adoption_rejects_negative_volume(self):
        p = d2_innovate()
        p["observations"][0]["new_adoptions"] = -1
        with self.assertRaisesRegex(D2Error, "invalid_adoption"):
            adoption_capacity(p)

    def test_paignia_requires_explicit_utility_and_builds_finite_graph(self):
        r = paignia_packet(d2_paignia())
        g = r["game_specification"]
        self.assertEqual(g["schema_version"], "1.0.0")
        self.assertEqual(g["game"]["root"], "start")
        self.assertEqual(g["game"]["nodes"]["start"]["kind"], "Decision")
        self.assertEqual(g["game"]["nodes"]["terminal:adopt"]["payoffs"], {"planner": 1.5})
        self.assertEqual(r["provider_execution"], "not_executed")

    def test_pinned_paignia_selects_the_higher_explicit_utility(self):
        binary = os.environ.get("DAPANE_PAIGNIA_BIN")
        if not binary:
            self.skipTest("DAPANE_PAIGNIA_BIN is not set")
        payload = d2_paignia()
        payload["actions"] = [
            {"id": "A", "utility": {"numerator": "10", "denominator": "1"}},
            {"id": "B", "utility": {"numerator": "20", "denominator": "1"}},
        ]
        result = paignia_game_solve_native(payload, binary)
        self.assertEqual(result["provider_execution"], "native_invoked")
        self.assertEqual(result["paignia_solution"]["selected_action"], "B")
        self.assertEqual(result["paignia_solution"]["expected_payoff"], 20.0)
        self.assertEqual(
            result["paignia_solution"]["profile"],
            "paignia/static-finite-perfect-information-sparse-zero/1.0.0",
        )
        self.assertEqual(result["key"]["draw_id"], "draw-a")

    def test_paignia_rejects_monetary_payoff_without_explicit_transformation(self):
        p = d2_paignia()
        p["payoff_mapping"]["method"] = "raw_cost_as_utility"
        with self.assertRaisesRegex(D2Error, "payoff_semantics"):
            paignia_packet(p)

    def test_paignia_rejects_net_nonzero_domestic_transfer(self):
        p = d2_paignia()
        p["payoff_mapping"]["domestic_transfer_balance"]["numerator"] = "1"
        with self.assertRaisesRegex(D2Error, "transfer_imbalance"):
            paignia_packet(p)

    def test_paignia_rejects_normal_form_claim(self):
        p = d2_paignia()
        p["provider"]["contract"] = "paignia/normal-form/1.0.0"
        with self.assertRaisesRegex(D2Error, "unsupported_contract"):
            paignia_packet(p)

    def test_paignia_rejects_duplicate_action_ids(self):
        p = d2_paignia()
        p["actions"][1]["id"] = "adopt"
        with self.assertRaisesRegex(D2Error, "duplicate_action"):
            paignia_packet(p)

    def test_paignia_rejects_implicit_missing_player_utility(self):
        p = d2_paignia()
        p["actions"][1].pop("utility")
        with self.assertRaisesRegex(D2Error, "invalid_request"):
            paignia_packet(p)

    def test_adoption_uses_exact_fractional_resource_quantities(self):
        p = d2_innovate()
        p["resource"]["quantity_per_adoption"] = {"numerator": "1", "denominator": "3"}
        p["resource"]["capacity_per_period"] = {"numerator": "2", "denominator": "3"}
        p["observations"] = [{"period": "2026-01", "new_adoptions": 3}]
        r = adoption_capacity(p)
        self.assertEqual(r["periods"][0]["demand"], {"numerator": "1", "denominator": "1"})
        self.assertEqual(r["periods"][0]["served"], {"numerator": "2", "denominator": "3"})
        self.assertEqual(r["periods"][0]["backlog"], {"numerator": "1", "denominator": "3"})

    def test_voiage_rejects_wrong_d1_complete_panel(self):
        d1 = d1_fixture()
        d1["rows"].pop()
        d1["output_digest"] = sha(
            "dapane:paired-output:0.1\n", {k: v for k, v in d1.items() if k != "output_digest"}
        )
        with self.assertRaisesRegex(D2Error, "d1_pairing_mismatch"):
            voiage_packet(json.dumps(d1), d1["output_digest"], d2_voiage(d1))

    def test_voiage_rejects_unsupported_d1_method(self):
        d1 = d1_fixture()
        d1["method_version"] = "dapane-paired-draws-v9"
        d1["output_digest"] = sha(
            "dapane:paired-output:0.1\n", {k: v for k, v in d1.items() if k != "output_digest"}
        )
        with self.assertRaisesRegex(D2Error, "unsupported_d1"):
            voiage_packet(json.dumps(d1), d1["output_digest"], d2_voiage(d1))

    def test_voiage_rejects_financial_currency_substitution(self):
        d1 = d1_fixture()
        p = d2_voiage(d1)
        p["valuation"]["currency"] = "NZD"
        with self.assertRaisesRegex(D2Error, "money_context"):
            voiage_packet(json.dumps(d1), d1["output_digest"], p)

    def test_adoption_declares_no_monetary_valuation(self):
        r = adoption_capacity(d2_innovate())
        self.assertEqual(r["pricing_execution"], "not_executed")
        self.assertNotIn("total_cost", r)
        self.assertNotIn("price_response", r)

    def test_adoption_rejects_unselected_parent_digest(self):
        p = d2_innovate()
        p["iteration"] = 1
        p["previous_evaluation_digest"] = DIGEST
        p["feedback"] = {
            "price_affects_adoption": True,
            "mode": "external_recomputed",
            "valuation_digest": DIGEST,
        }
        with self.assertRaisesRegex(D2Error, "feedback_chain"):
            adoption_capacity(p, expected_previous_digest="sha256:" + "f" * 64)

    def test_paignia_distinguishes_fee_from_social_utility(self):
        p = d2_paignia()
        p["payoff_mapping"]["transfer_treatment"] = "government_receipts_as_utility"
        with self.assertRaisesRegex(D2Error, "payoff_semantics"):
            paignia_packet(p)

    def test_provider_negotiation_rejects_future_contract(self):
        p = provider("edithatogo/voiage", "voiage-domain/ValueArray-v2", "evpi")
        with self.assertRaisesRegex(D2Error, "unsupported_contract"):
            negotiate(p)

    def test_provider_negotiation_rejects_wrong_revision_format(self):
        p = provider("edithatogo/voiage", "voiage-domain/ValueArray", "evpi")
        p["revision"] = "main"
        with self.assertRaisesRegex(D2Error, "invalid_provider"):
            negotiate(p)

    def test_provider_negotiation_returns_selected_capability(self):
        p = provider(
            "edithatogo/paignia",
            "paignia/static-finite-perfect-information-sparse-zero/1.0.0",
            "static_game_input",
        )
        r = negotiate(p)
        self.assertEqual(r["provider"], "edithatogo/paignia")
        self.assertEqual(r["state"], "prepared_not_executed")
        self.assertEqual(r["revision"], HEX40)


if __name__ == "__main__":
    unittest.main()
