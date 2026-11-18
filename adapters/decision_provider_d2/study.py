"""Dapane D3: source-bound measurement-evidence intake, not a VOI estimator.

The optional provider owns EVPI numerical execution; the domain owner owns the
resource/cost model and study-specific assumptions. No reference to Voiage is
imported at module import time. Synthetic fixtures cannot imply a clinical or
scientific acceptance status.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
import math
from pathlib import Path
import re
import subprocess
from typing import Any

_SHA = re.compile(r"sha256:[0-9a-f]{64}\Z")
_REVISION = re.compile(r"[0-9a-f]{40}\Z")
_INTEGER = re.compile(r"(?:0|[1-9][0-9]*|-[1-9][0-9]*)\Z")
_FIELDS = ("scenario_id", "strategy_id", "draw_id", "replication_id", "perspective", "subgroup_id")
_PACKET_MAX = 16 * 1024 * 1024


class StudyError(ValueError):
    """Stable fail-closed study admission diagnostic."""

    def __init__(self, code: str, path: str, message: str = "") -> None:
        self.code = code
        self.path = path
        super().__init__(f"{code} at {path}: {message}")


def _require(condition: bool, code: str, path: str, message: str = "") -> None:
    if not condition:
        raise StudyError(code, path, message)


def _object(value: Any, fields: set[str], path: str) -> dict[str, Any]:
    _require(isinstance(value, dict) and set(value) == fields, "invalid_request", path,
             f"Expected exactly {sorted(fields)}")
    return value


def _str(value: Any, path: str) -> str:
    _require(isinstance(value, str) and value and value == value.strip()
             and len(value.encode("utf-8")) <= 128
             and all(ord(c) >= 32 and ord(c) != 127 for c in value),
             "invalid_identity", path)
    return value


def _digest(value: Any, path: str) -> str:
    _require(isinstance(value, str) and _SHA.fullmatch(value) is not None,
             "invalid_digest", path)
    return value


def _number(value: Any, path: str) -> float:
    _require(type(value) in (int, float) and math.isfinite(value), "invalid_number", path)
    return float(value)


def _exact(value: Any, path: str) -> Fraction:
    x = _object(value, {"numerator", "denominator"}, path)
    n, d = x["numerator"], x["denominator"]
    _require(isinstance(n, str) and isinstance(d, str)
             and _INTEGER.fullmatch(n) is not None
             and _INTEGER.fullmatch(d) is not None
             and not d.startswith("-") and int(d) != 0
             and len(n.lstrip("-")) <= 96 and len(d) <= 96,
             "invalid_exact", path)
    q = Fraction(int(n), int(d))
    _require(max(q.numerator.bit_length(), q.denominator.bit_length()) <= 4096,
             "precision_limit", path)
    return q


def canonical_digest(domain: str, value: Any) -> str:
    """Versioned domain-separated JSON fingerprint; not a signature.

    Input callers strip the output_digest field before hashing.
    """
    try:
        body = json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False)
    except (ValueError, TypeError, UnicodeError, OverflowError, RecursionError) as exc:
        raise StudyError("invalid_number", "/", "Cannot canonicalize input") from exc
    return "sha256:" + sha256((domain + body).encode("utf-8")).hexdigest()


def _verify_packet(packet: Any) -> dict[str, Any]:
    required = {"schema_version", "provider", "provider_execution", "input_d1_digest",
                "group", "valuation", "draw_id_order", "pair_keys", "exact_net_benefit",
                "value_array", "conversion", "output_digest"}
    p = _object(packet, required, "/d2_packet")
    _require(p["schema_version"] == "dapane-d2-voiage/0.1", "unsupported_schema", "/d2_packet/schema_version")
    _require(p["provider_execution"] == "not_executed", "provider_execution", "/d2_packet/provider_execution")
    provider = _object(p["provider"], {"provider", "revision", "artifact_digest", "contract", "method", "state"}, "/provider")
    _require(provider["provider"] == "edithatogo/voiage" and provider["contract"] == "voiage-domain/ValueArray"
             and provider["method"] == "evpi" and provider["state"] == "prepared_not_executed",
             "unsupported_provider_method", "/provider")
    _require(isinstance(provider["revision"], str) and _REVISION.fullmatch(provider["revision"]) is not None,
             "invalid_provider_revision", "/provider/revision")
    _digest(provider["artifact_digest"], "/provider/artifact_digest")
    _digest(p["input_d1_digest"], "/input_d1_digest")
    _digest(p["output_digest"], "/output_digest")
    # Check numbers before fingerprinting, so nonfinite input produces a typed error.
    a = _object(p["value_array"], {"value_array_id", "sample_count", "strategy_names", "net_benefit"}, "/value_array")
    _str(a["value_array_id"], "/value_array/value_array_id")
    matrix = a["net_benefit"]
    _require(isinstance(matrix, list) and matrix, "invalid_matrix", "/value_array/net_benefit")
    for i, row in enumerate(matrix):
        _require(isinstance(row, list), "invalid_matrix", f"/value_array/net_benefit/{i}")
        for j, v in enumerate(row):
            _number(v, f"/value_array/net_benefit/{i}/{j}")
    expected = canonical_digest("dapane:d2-voiage:0.1\n", {k:v for k,v in p.items() if k != "output_digest"})
    _require(p["output_digest"] == expected, "d2_digest_mismatch", "/output_digest")
    return p


def prepare_evidence_question(d2_packet: Any, protocol: Any) -> dict[str, Any]:
    """Bind a measurement question to D2's complete paired VOI input.

    This function prepares a fixed, equal-weight EVPI question. It neither
    generates draws nor calculates EVPI, EVSI, EVPPI, net benefit or costs.
    """
    p = _verify_packet(d2_packet)
    spec = _object(protocol, {"schema_version", "study_id", "question", "evidence_target",
                              "perspective", "data_status", "design", "reference", "intent"}, "/protocol")
    _require(spec["schema_version"] == "dapane-d3-study/0.1", "unsupported_schema", "/protocol/schema_version")
    _str(spec["study_id"], "/protocol/study_id")
    _str(spec["question"], "/protocol/question")
    _require(spec["intent"] == "evpi_upper_bound_only", "unsupported_estimand", "/protocol/intent")
    target = _object(spec["evidence_target"], {"parameter_id", "unit", "uncertainty", "study_design",
                                                    "measurement_likelihood"}, "/evidence_target")
    _str(target["parameter_id"], "/evidence_target/parameter_id")
    _str(target["unit"], "/evidence_target/unit")
    _require(target["uncertainty"] == "epistemic" and target["study_design"] == "prospective_time_and_motion",
             "unsupported_measurement_model", "/evidence_target")
    _require(target["measurement_likelihood"] == "not_supplied", "unsupported_measurement_model",
             "/evidence_target/measurement_likelihood")
    data = _object(spec["data_status"], {"resource", "clinical_outcomes", "utilisation", "rights"}, "/data_status")
    _require(data == {"resource": "synthetic", "clinical_outcomes": "not_modelled",
                      "utilisation": "not_modelled", "rights": "not_assessed"}, "source_status", "/data_status")
    context = _object(spec["perspective"], {"name", "currency", "price_year", "basis", "unit"}, "/perspective")
    _require(context["unit"] == "per_assay", "unsupported_unit", "/perspective/unit")
    money = p["valuation"]
    _require(context["name"] == p["group"]["perspective"]
             and all(context[k] == money[k] for k in ("currency", "price_year", "basis")),
             "perspective_mismatch", "/perspective")
    d = _object(spec["design"], {"strategies", "draws", "draw_weights", "replication_id", "subgroup_id"}, "/design")
    _require(d["draw_weights"] == "equal", "unsupported_weights", "/design/draw_weights")
    value = p["value_array"]
    _require(d["strategies"] == value["strategy_names"] and d["draws"] == p["draw_id_order"]
             and d["replication_id"] == p["group"]["replication_id"]
             and d["subgroup_id"] == p["group"]["subgroup_id"], "pairing_mismatch", "/design")
    for axis in (d["strategies"], d["draws"]):
        _require(isinstance(axis, list) and 1 <= len(axis) <= 256
                 and len(set(axis)) == len(axis), "pairing_mismatch", "/design")
        for token in axis:
            _str(token, "/design")
    _require(type(value["sample_count"]) is int and value["sample_count"] == len(d["draws"])
             and len(value["net_benefit"]) == len(d["draws"])
             and all(len(row) == len(d["strategies"]) for row in value["net_benefit"]),
             "invalid_matrix", "/value_array")
    keys = p["pair_keys"]
    needed = [dict(zip(_FIELDS, (p["group"]["scenario_id"], s, draw, d["replication_id"],
                                  context["name"], d["subgroup_id"])))
              for draw, s in product(d["draws"], d["strategies"])]
    _require(isinstance(keys, list) and keys == needed, "pairing_mismatch", "/pair_keys")
    exact = p["exact_net_benefit"]
    _require(isinstance(exact, list) and len(exact) == len(needed), "numeric_mismatch", "/exact_net_benefit")
    for i, (entry, actual) in enumerate(zip(exact,
                       (v for row in value["net_benefit"] for v in row), strict=True)):
        q = _exact(entry, f"/exact_net_benefit/{i}")
        _require(abs(Fraction.from_float(float(actual)) - q) <= Fraction(1, 10**9),
                 "numeric_mismatch", f"/exact_net_benefit/{i}")
    reference = _object(spec["reference"], {"method", "per_assay", "proof_digest", "absolute_tolerance"}, "/reference")
    _require(reference["method"] == "independently_derived_evpi", "unsupported_estimand", "/reference/method")
    _digest(reference["proof_digest"], "/reference/proof_digest")
    expected = _exact(reference["per_assay"], "/reference/per_assay")
    _require(expected >= 0, "invalid_reference", "/reference/per_assay")
    tolerance = reference["absolute_tolerance"]
    _require(isinstance(tolerance, str), "invalid_reference", "/reference/absolute_tolerance")
    try:
        tol = Fraction(tolerance)
    except (ValueError, ZeroDivisionError) as exc:
        raise StudyError("invalid_reference", "/reference/absolute_tolerance") from exc
    _require(0 < tol <= Fraction(1, 1000), "invalid_reference", "/reference/absolute_tolerance")
    output = {
        "schema_version": "dapane-d3-prepared/0.1", "study_id": spec["study_id"],
        "question_type": "value_of_perfect_information_upper_bound",
        "question": spec["question"], "target": target, "cost_context": context,
        "source_status": data, "design": d, "value_array": value,
        "input_d2_digest": p["output_digest"], "input_d1_digest": p["input_d1_digest"],
        "provider": p["provider"], "provider_execution": "not_executed",
        "selected_native_entrypoint": "voiage._runtime.compute_evpi",
        "reference_evpi_per_assay": reference["per_assay"],
        "reference_tolerance": tolerance, "reference_proof_digest": reference["proof_digest"],
        "limitations": {"evsi_estimated": False, "cost_of_measurement_included": False,
                        "clinical_outcomes_validated": False, "producer_method_qualified": False,
                        "real_cost_or_utilisation_data": False},
    }
    output["prepared_digest"] = canonical_digest("dapane:d3-prepared:0.1\n", output)
    return output


def verify_native_evpi_receipt(prepared: Any, receipt: Any, *, expected_wheel: str,
                               expected_extension: str) -> dict[str, Any]:
    """Verify a declared native provider observation, without self-certification.

    A candidate receipt cannot authenticate its own origin. The receiving owner
    must independently inspect the *actual* installed artifact, invocation, and
    native extension, and re-execute the qualified numerical method.
    """
    q = _object(prepared, {"schema_version", "study_id", "question_type", "question", "target",
                           "cost_context", "source_status", "design", "value_array", "input_d2_digest",
                           "input_d1_digest", "provider", "provider_execution",
                           "selected_native_entrypoint", "reference_evpi_per_assay",
                           "reference_tolerance", "reference_proof_digest", "limitations",
                           "prepared_digest"}, "/prepared")
    _require(q["schema_version"] == "dapane-d3-prepared/0.1", "unsupported_schema", "/prepared/schema_version")
    selected = q["prepared_digest"]
    _digest(selected, "/prepared/prepared_digest")
    _require(selected == canonical_digest("dapane:d3-prepared:0.1\n", {k:v for k,v in q.items()
                                                                  if k!="prepared_digest"}),
             "input_mismatch", "/prepared/prepared_digest")
    expected_receipt = {"schema_version", "method", "input_digest", "provider_revision",
                        "wheel_digest", "native_extension_digest", "evpi_per_assay",
                        "execution", "source"}
    _require(isinstance(receipt, dict) and set(receipt) == expected_receipt,
             "invalid_receipt", "/receipt", "Unexpected or missing fields")
    r = receipt
    _require(r["schema_version"] == "dapane-d3-native-evpi/0.1", "unsupported_schema", "/receipt/schema_version")
    _require(r["method"] == "voiage._runtime.compute_evpi", "unsupported_method", "/receipt/method")
    _require(r["source"] == "externally_run_installed_wheel"
             and r["execution"] == "native_extension_invoked", "provider_execution", "/receipt/execution")
    _require(r["input_digest"] == selected, "input_mismatch", "/receipt/input_digest")
    _require(r["provider_revision"] == q["provider"]["revision"], "revision_mismatch", "/receipt/provider_revision")
    _digest(expected_wheel, "/expected_wheel")
    _digest(expected_extension, "/expected_extension")
    _require(q["provider"]["artifact_digest"] == expected_wheel,
             "wheel_identity", "/prepared/provider/artifact_digest")
    _require(r["wheel_digest"] == expected_wheel, "wheel_identity", "/receipt/wheel_digest")
    _require(r["native_extension_digest"] == expected_extension, "native_identity", "/receipt/native_extension_digest")
    actual = _number(r["evpi_per_assay"], "/receipt/evpi_per_assay")
    _require(actual >= 0, "invalid_number", "/receipt/evpi_per_assay")
    expected = _exact(q["reference_evpi_per_assay"], "/prepared/reference_evpi_per_assay")
    tol = Fraction(q["reference_tolerance"])
    _require(abs(Fraction.from_float(actual) - expected) <= tol,
             "reference_mismatch", "/receipt/evpi_per_assay")
    return {"schema_version": "dapane-d3-native-review/0.1",
            "state": "verified_declaration_not_installed_acceptance",
            "input_digest": selected, "provider_revision": r["provider_revision"],
            "wheel_digest": expected_wheel, "native_extension_digest": expected_extension,
            "evpi_per_assay": actual, "evsi_estimated": False,
            "independent_source_and_execution_review_required": True}


def run_static_without_providers(cli: Path, request: bytes, expected_executable_sha: str) -> dict[str, Any]:
    """Actually execute a selected *standalone native* Dapane CLI.

    This is no Voiage or game fallback: native Dapane computes the request itself.
    The call is bounded, isolated from optional provider Python import paths and
    requires an independent expected executable digest. A synthetic fake-CLI
    unit test is not a delivered binary qualification.
    """
    _digest(expected_executable_sha, "/expected_executable_sha")
    if not cli.is_absolute() or not cli.is_file() or cli.is_symlink():
        raise StudyError("native_unavailable", "/cli", "Absolute regular executable required")
    _require(isinstance(request, bytes) and len(request) <= 4 * 1024 * 1024,
             "input_limit", "/request")
    actual = "sha256:" + sha256(cli.read_bytes()).hexdigest()
    _require(actual == expected_executable_sha, "native_binary_mismatch", "/cli")
    try:
        run = subprocess.run([str(cli), "evaluate", "-"], input=request,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env={"LC_ALL": "C.UTF-8", "LANG": "C.UTF-8", "PATH": "/usr/bin:/bin"},
                             check=False, timeout=15)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise StudyError("native_execution_failed", "/cli") from exc
    _require(run.returncode == 0 and len(run.stdout) <= _PACKET_MAX,
             "native_execution_failed", "/cli")
    try:
        report = json.loads(run.stdout)
    except (UnicodeError, ValueError) as exc:
        raise StudyError("invalid_native_report", "/stdout") from exc
    _require(isinstance(report, dict) and report.get("status") == "complete"
             and report.get("method_version") == "dapane-exact-v0.1.0"
             and isinstance(report.get("output_digest"), str)
             and _SHA.fullmatch(report["output_digest"]) is not None,
             "invalid_native_report", "/stdout")
    return {"schema_version": "dapane-d3-static-fallback/0.1",
            "execution_mode": "standalone_cli_no_optional_providers",
            "native_binary_digest": expected_executable_sha,
            "request_digest": "sha256:" + sha256(request).hexdigest(),
            "native_report": report,
            "qualification": "synthetic_process_only"}
