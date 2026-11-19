"""Independent end-to-end oracle verification for X2 PNML and BPMN adapters."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ADAPTER_DIR = ROOT / "adapters/process_models"
FIXTURES = ADAPTER_DIR / "fixtures"
EXPECTED = json.loads((FIXTURES / "expected.json").read_text(encoding="utf-8"))
QUOTES_V1 = FIXTURES / "quotes-release-2026-v1.json"
QUOTES_V2 = FIXTURES / "quotes-release-2026-v2.json"

PROCESS_CLI = Path(
    os.environ.get(
        "DAPANE_PROCESS_MODELS_CLI",
        ADAPTER_DIR / "target/release/dapane-process-models",
    )
)
DAPANE_CLI = Path(os.environ.get("DAPANE_CLI", ROOT / "target/release/dapane"))

try:
    import dapane  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    dapane = None


def parse_trace_exact(node: dict[str, str]) -> Fraction:
    return Fraction(int(node["numerator"]), int(node["denominator"]))


def run_process_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(PROCESS_CLI), *args],
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )


def evaluate_dapane_cli(request_payload: dict) -> dict:
    proc = subprocess.run(
        [str(DAPANE_CLI), "evaluate", "-"],
        input=json.dumps(request_payload),
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    return json.loads(proc.stdout)


def quote_price_map(valuation_path: Path) -> dict[str, Fraction]:
    doc = json.loads(valuation_path.read_text(encoding="utf-8"))
    prices: dict[str, Fraction] = {}
    for q in doc["quotes"]:
        prices[q["id"]] = Fraction(q["amount"]) / Fraction(q["per_quantity"])
    return prices


def parse_dapane_number(value: object) -> Fraction:
    if isinstance(value, str):
        return Fraction(value)
    if isinstance(value, dict):
        return Fraction(int(value["numerator"]), int(value["denominator"]))
    raise AssertionError(f"Unexpected numeric encoding: {value!r}")


class ProcessModelOracleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not PROCESS_CLI.is_file():
            raise RuntimeError(f"Missing dapane-process-models binary at {PROCESS_CLI}")
        if not DAPANE_CLI.is_file():
            raise RuntimeError(f"Missing dapane binary at {DAPANE_CLI}")

    def test_validate_positive_models_report_sha256_and_counts(self) -> None:
        seen_models: set[tuple[str, str, str]] = set()
        for spec in EXPECTED["positive_cases"].values():
            seen_models.add((spec["kind"], spec["model"], spec["profile"]))

        for kind, rel_model, profile in sorted(seen_models):
            model_path = FIXTURES / rel_model
            expected_digest = f"sha256:{hashlib.sha256(model_path.read_bytes()).hexdigest()}"
            with self.subTest(model=rel_model, profile=profile):
                if kind == "pnml":
                    res = run_process_cli("validate-pnml", str(model_path))
                else:
                    res = run_process_cli("validate-bpmn", str(model_path), "--profile", profile)
                self.assertEqual(res.returncode, 0, msg=res.stderr)
                payload = json.loads(res.stdout)
                self.assertTrue(payload["valid"])
                self.assertEqual(payload["profile_id"], profile)
                self.assertEqual(payload["model_sha256"], expected_digest)

    def test_negative_fixtures_fail_with_expected_codes(self) -> None:
        for case in EXPECTED["negative_cases"]:
            model = str(FIXTURES / case["model"])
            with self.subTest(model=case["model"], profile=case.get("profile")):
                if case["kind"] == "pnml":
                    res = run_process_cli("validate-pnml", model)
                else:
                    res = run_process_cli(
                        "validate-bpmn",
                        model,
                        "--profile",
                        case["profile"],
                    )
                self.assertEqual(res.returncode, 1, msg=res.stdout)
                err = json.loads(res.stderr)
                self.assertEqual(err["code"], case["expected_error"])

    def test_all_positive_cases_value_and_revalue_with_cli_and_wheel_parity(self) -> None:
        prices_v1 = quote_price_map(QUOTES_V1)
        prices_v2 = quote_price_map(QUOTES_V2)

        for name, spec in EXPECTED["positive_cases"].items():
            model_path = FIXTURES / spec["model"]
            config_path = FIXTURES / spec["config"]
            with self.subTest(case=name):
                exec_sub = "execute-pnml" if spec["kind"] == "pnml" else "execute-bpmn"
                exec_res = run_process_cli(exec_sub, str(model_path), str(config_path))
                self.assertEqual(exec_res.returncode, 0, msg=exec_res.stderr)
                trace = json.loads(exec_res.stdout)

                self.assertEqual(trace["profile_id"], spec["profile"])
                self.assertEqual(trace["status"]["state"], spec["status"])
                self.assertEqual(len(trace["steps"]), spec["step_count"])
                self.assertEqual(len(trace["usages"]), spec["trace_usage_count"])
                self.assertEqual(
                    parse_trace_exact(trace["total_elapsed_minutes"]),
                    Fraction(spec["elapsed_minutes"]),
                )

                # Project trace under two separate quotation releases without re-executing.
                with tempfile.TemporaryDirectory(prefix="dapane-x2-trace-") as tmpdir:
                    trace_file = Path(tmpdir) / f"{name}-trace.json"
                    trace_file.write_text(exec_res.stdout, encoding="utf-8")
                    p1 = run_process_cli("project-dapane", str(trace_file), str(QUOTES_V1))
                    p2 = run_process_cli("project-dapane", str(trace_file), str(QUOTES_V2))

                self.assertEqual(p1.returncode, 0, msg=p1.stderr)
                self.assertEqual(p2.returncode, 0, msg=p2.stderr)
                req1 = json.loads(p1.stdout)
                req2 = json.loads(p2.stdout)

                self.assertEqual(len(req1["usage"]), spec["dapane_usage_count"])
                self.assertEqual(len(req2["usage"]), spec["dapane_usage_count"])

                # AC 4: physical use & context identities unchanged under quotation release update.
                for shared_key in (
                    "processes",
                    "events",
                    "objects",
                    "object_relations",
                    "allocations",
                ):
                    self.assertEqual(req1[shared_key], req2[shared_key])
                for line1, line2 in zip(req1["usage"], req2["usage"], strict=True):
                    for inv_key in (
                        "id",
                        "use_id",
                        "event_id",
                        "process_id",
                        "activity_id",
                        "target",
                        "unit",
                        "quantity",
                        "object_ids",
                        "attribution_object_id",
                    ):
                        self.assertEqual(line1[inv_key], line2[inv_key])
                    self.assertNotEqual(line1["quote_id"], line2["quote_id"])

                # Evaluate both requests via Rust CLI and independently check Fraction totals.
                rep1 = evaluate_dapane_cli(req1)
                rep2 = evaluate_dapane_cli(req2)

                self.assertEqual(rep1["totals"]["rounded"], spec["v1_total_rounded"])
                self.assertEqual(rep2["totals"]["rounded"], spec["v2_total_rounded"])

                expected_exact_v1 = sum(
                    parse_dapane_number(u["quantity"]) * prices_v1[u["quote_id"]]
                    for u in req1["usage"]
                )
                expected_exact_v2 = sum(
                    parse_dapane_number(u["quantity"]) * prices_v2[u["quote_id"]]
                    for u in req2["usage"]
                )
                self.assertEqual(
                    parse_dapane_number(rep1["totals"]["exact"]),
                    expected_exact_v1,
                )
                self.assertEqual(
                    parse_dapane_number(rep2["totals"]["exact"]),
                    expected_exact_v2,
                )

                obj_map1 = {o["object_id"]: o["total"] for o in rep1["object_totals"]}
                obj_map2 = {o["object_id"]: o["total"] for o in rep2["object_totals"]}
                for oid, want in spec["v1_object_totals"].items():
                    self.assertEqual(obj_map1[oid], want)
                for oid, want in spec["v2_object_totals"].items():
                    self.assertEqual(obj_map2[oid], want)

                # Conserve totals across direct + allocated object totals on non-pooled/full-pool studies.
                sum_objects_v1 = sum(Fraction(v) for v in obj_map1.values())
                sum_objects_v2 = sum(Fraction(v) for v in obj_map2.values())
                self.assertEqual(sum_objects_v1, Fraction(rep1["totals"]["rounded"]))
                self.assertEqual(sum_objects_v2, Fraction(rep2["totals"]["rounded"]))

                if os.environ.get("REQUIRE_DAPANE_WHEEL") == "1":
                    self.assertIsNotNone(dapane, "Expected installed dapane wheel")

                # Verify CLI and installed Python wheel exact parity when wheel is installed.
                if dapane is not None:
                    wheel_rep1 = json.loads(dapane.evaluate_json(json.dumps(req1)))
                    wheel_rep2 = json.loads(dapane.evaluate_json(json.dumps(req2)))
                    self.assertEqual(wheel_rep1, rep1)
                    self.assertEqual(wheel_rep2, rep2)
