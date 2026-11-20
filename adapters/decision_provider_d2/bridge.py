"""Dapane D2: optional provider-bound *preparation*, never scientific execution.

This is a standalone standard-library contract adapter. It consumes D1's unchanged
native result, externally produced adoption/valuation records and explicit game
utilities. It does not fit an Innovate model, price resources, run Voiage methods,
solve Paignia games or convert financial transfers into utilities.
When qualified native provider binaries are available, D2 can invoke them
through subprocess for provider-backed execution.
"""

from __future__ import annotations

import json
import math
import os
import re
import shutil
import subprocess
import tempfile
from fractions import Fraction
from hashlib import file_digest, sha256
from itertools import product
from typing import Any

SCHEMA = "dapane-d2/0.1"
KEY_FIELDS = (
    "scenario_id",
    "strategy_id",
    "draw_id",
    "replication_id",
    "perspective",
    "subgroup_id",
)
SUPPORTED = {
    "edithatogo/voiage": ("voiage-domain/ValueArray", "evpi"),
    "edithatogo/innovate": ("declared-innovation-trajectory/0.1", "provided_trajectory"),
    "edithatogo/paignia": (
        "paignia/static-finite-perfect-information-sparse-zero/1.0.0",
        "static_game_input",
    ),
}
_DIGEST = re.compile(r"sha256:[0-9a-f]{64}\Z")
_REVISION = re.compile(r"[0-9a-f]{40}\Z")
_PERIOD = re.compile(r"(\d{4})-(\d{2})\Z")
_INT = re.compile(r"(?:0|[1-9][0-9]*|-[1-9][0-9]*)\Z")


class D2Error(ValueError):
    """Stable code and path for a rejected or unsupported D2 request."""

    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        super().__init__(f"{code} at {path}: {message}")


def _bad(code: str, path: str, message: str) -> None:
    raise D2Error(code, path, message)


def _object(value: Any, path: str, required: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != required:
        _bad("invalid_request", path, f"Expected exactly {sorted(required)}")
    return value


def _ident(value: Any, path: str) -> str:
    if (
        not isinstance(value, str)
        or not 1 <= len(value.encode("utf-8")) <= 128
        or value != value.strip()
        or any(ord(c) < 32 or ord(c) == 127 for c in value)
    ):
        _bad(
            "invalid_identity", path, "Nonblank 1..128 UTF-8 bytes, no edge whitespace or controls"
        )
    return value


def _sha(value: Any, path: str) -> str:
    if not isinstance(value, str) or _DIGEST.fullmatch(value) is None:
        _bad("invalid_digest", path, "Expected sha256: followed by 64 lowercase hex characters")
    return value


def _fraction(
    value: Any, path: str, *, nonnegative: bool = False, max_digits: int = 96
) -> Fraction:
    wire = _object(value, path, {"numerator", "denominator"})
    num, den = wire["numerator"], wire["denominator"]
    if (
        not isinstance(num, str)
        or not isinstance(den, str)
        or _INT.fullmatch(num) is None
        or _INT.fullmatch(den) is None
        or den.startswith("-")
        or len(num.lstrip("-")) > max_digits
        or len(den) > max_digits
    ):
        _bad("invalid_exact_number", path, "Canonical bounded integer strings required")
    if int(den) == 0:
        _bad("invalid_exact_number", path, "Denominator must be positive")
    value = Fraction(int(num), int(den))
    if max(value.numerator.bit_length(), value.denominator.bit_length()) > 4096:
        _bad("precision_limit", path, "Exact quantity exceeds the 4096-bit bound")
    if nonnegative and value < 0:
        _bad("invalid_exact_number", path, "Expected nonnegative value")
    return value


def _wire(value: Fraction) -> dict[str, str]:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def _f64(value: Fraction, path: str) -> float:
    try:
        converted = float(value)
    except OverflowError:
        _bad("precision_loss", path, "Cannot represent value as finite f64")
    if not math.isfinite(converted) or abs(Fraction.from_float(converted) - value) > Fraction(
        1, 10**9
    ):
        _bad("precision_loss", path, "f64 conversion exceeds 1e-9 absolute unit tolerance")
    return converted


def _canonical(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )


def _digest(domain: str, value: Any) -> str:
    return "sha256:" + sha256((domain + _canonical(value)).encode("utf-8")).hexdigest()


def _closed_output(domain: str, value: dict[str, Any]) -> dict[str, Any]:
    value["output_digest"] = _digest(domain, value)
    if len(_canonical(value).encode("utf-8")) > 16 * 1024 * 1024:
        _bad("output_limit", "/", "Output exceeds 16 MiB")
    return value


def _loads_unique(text: str) -> Any:
    if not isinstance(text, str) or len(text.encode("utf-8")) > 16 * 1024 * 1024:
        _bad("input_limit", "/", "D1 input must be UTF-8 text no larger than 16 MiB")

    def hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                _bad("duplicate_key", "/", f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    def floating(_: str) -> None:
        _bad("invalid_json_number", "/", "D1 exact JSON cannot contain floating numbers")

    try:
        return json.loads(
            text, object_pairs_hook=hook, parse_float=floating, parse_constant=floating
        )
    except (json.JSONDecodeError, UnicodeError, RecursionError) as error:
        _bad("invalid_json", "/", str(error))


def _key(value: Any, path: str) -> tuple[str, ...]:
    row = _object(value, path, set(KEY_FIELDS))
    return tuple(_ident(row[k], f"{path}/{k}") for k in KEY_FIELDS)


def negotiate(pin: Any) -> dict[str, str]:
    """Admit an exact *declaration*. It never attests a provider's installation."""
    fields = {"repository", "revision", "artifact_digest", "contract", "method"}
    if not isinstance(pin, dict) or set(pin) != fields:
        _bad("invalid_provider", "/provider", f"Expected exactly {sorted(fields)}")
    p = pin
    repo = p["repository"]
    if not isinstance(repo, str) or repo not in SUPPORTED:
        _bad(
            "unsupported_provider", "/provider/repository", "No adapter for the requested provider"
        )
    if not isinstance(p["revision"], str) or _REVISION.fullmatch(p["revision"]) is None:
        _bad("invalid_provider", "/provider/revision", "Pin exact 40-character lowercase commit")
    _sha(p["artifact_digest"], "/provider/artifact_digest")
    expected_contract, expected_method = SUPPORTED[repo]
    if p["contract"] != expected_contract:
        _bad("unsupported_contract", "/provider/contract", f"Only {expected_contract} is prepared")
    if p["method"] != expected_method:
        _bad("unsupported_method", "/provider/method", f"Only {expected_method} is prepared")
    return {
        "provider": repo,
        "revision": p["revision"],
        "artifact_digest": p["artifact_digest"],
        "contract": expected_contract,
        "method": expected_method,
        "state": "prepared_not_executed",
    }


def _d1_rows(
    raw: str, expected: str
) -> tuple[dict[str, Any], dict[tuple[str, ...], dict[str, Any]]]:
    _sha(expected, "/expected_d1_digest")
    report = _loads_unique(raw)
    if not isinstance(report, dict):
        _bad("invalid_d1", "/", "D1 report must be an object")
    if (
        report.get("schema_version") != "dapane-paired-draws/0.1"
        or report.get("method_version") != "dapane-paired-draws-v0.1.0"
        or report.get("status") != "complete"
    ):
        _bad("unsupported_d1", "/schema_version", "Requires completed D1 0.1 native report")
    provided = report.get("output_digest")
    body = {k: v for k, v in report.items() if k != "output_digest"}
    if provided != expected or _digest("dapane:paired-output:0.1\n", body) != expected:
        _bad(
            "d1_digest_mismatch",
            "/output_digest",
            "D1 bytes differ from independently selected digest",
        )
    if not isinstance(report.get("money"), dict) or not isinstance(report.get("design"), dict):
        _bad("invalid_d1", "/", "Missing D1 money/design contexts")
    design, draws = report["design"], report.get("draws")
    if not isinstance(draws, dict) or not isinstance(draws.get("rows"), list):
        _bad("invalid_d1", "/draws", "Missing explicit parameter draws")
    axes = [
        design.get(name)
        for name in ("scenarios", "strategies", "replications", "perspectives", "subgroups")
    ]
    if any(not isinstance(axis, list) or not axis for axis in axes):
        _bad("invalid_d1", "/design", "Every design axis is required")
    draw_ids = [d.get("draw_id") for d in draws["rows"] if isinstance(d, dict)]
    if len(draw_ids) != len(draws["rows"]) or not draw_ids or len(set(draw_ids)) != len(draw_ids):
        _bad("invalid_d1", "/draws/rows", "Draw identities must be unique and complete")
    for axis in [*axes, draw_ids]:
        if any(not isinstance(v, str) or not v for v in axis) or len(set(axis)) != len(axis):
            _bad("invalid_d1", "/design", "Duplicate or invalid axis values")
    expected_keys = {(s, t, d, r, p, g) for s, t, r, p, g, d in product(*axes, draw_ids)}
    rows = report.get("rows")
    if not isinstance(rows, list) or len(rows) != len(expected_keys):
        _bad("d1_pairing_mismatch", "/rows", "D1 report is not a complete Cartesian panel")
    keyed = {}
    for i, row in enumerate(rows):
        if (
            not isinstance(row, dict)
            or not isinstance(row.get("outcome"), dict)
            or not isinstance(row.get("cost_report"), dict)
        ):
            _bad("invalid_d1", f"/rows/{i}", "Missing D1 outcome or native cost report")
        k = _key(row.get("key"), f"/rows/{i}/key")
        if (
            k in keyed
            or k not in expected_keys
            or _key(row["outcome"].get("key"), f"/rows/{i}/outcome/key") != k
        ):
            _bad(
                "d1_pairing_mismatch",
                f"/rows/{i}",
                "Duplicated, missing, or mispaired native/outcome key",
            )
        keyed[k] = row
    return report, keyed


def voiage_packet(d1_json: str, expected_d1_digest: str, payload: Any) -> dict[str, Any]:
    """Prepare a keyed native ValueArray from externally valued net benefits.

    Voiage is not imported or invoked; external NMB values must be sourced and
    checked independently. The exact provenance ledger remains in the packet.
    """
    p = _object(payload, "/", {"provider", "group", "valuation", "value_array_id", "net_benefits"})
    pin = negotiate(p["provider"])
    if pin["provider"] != "edithatogo/voiage":
        _bad("unsupported_provider", "/provider", "Expected Voiage")
    report, rows = _d1_rows(d1_json, expected_d1_digest)
    group = _object(
        p["group"], "/group", {"scenario_id", "replication_id", "perspective", "subgroup_id"}
    )
    for k, v in group.items():
        _ident(v, f"/group/{k}")
    money = report["money"]
    valuation = _object(
        p["valuation"], "/valuation", {"currency", "price_year", "basis", "unit", "source"}
    )
    for name in ("currency", "price_year", "basis"):
        if valuation[name] != money.get(name):
            _bad(
                "money_context",
                f"/valuation/{name}",
                "D1 money context and outcome valuation must agree",
            )
    if valuation["unit"] != "currency":
        _bad(
            "money_context",
            "/valuation/unit",
            "ValueArray requires named net-benefit currency units",
        )
    source = _object(valuation["source"], "/valuation/source", {"id", "version", "digest"})
    _ident(source["id"], "/valuation/source/id")
    _ident(source["version"], "/valuation/source/version")
    _sha(source["digest"], "/valuation/source/digest")
    value_array_id = _ident(p["value_array_id"], "/value_array_id")
    desired = {
        k: r
        for k, r in rows.items()
        if all(k[KEY_FIELDS.index(field)] == value for field, value in group.items())
    }
    if not desired:
        _bad("pairing_mismatch", "/group", "No D1 rows for selected group")
    vals = p["net_benefits"]
    if not isinstance(vals, list) or len(vals) != len(desired):
        _bad(
            "pairing_mismatch",
            "/net_benefits",
            "Net benefits must cover every paired strategy/draw",
        )
    valued: dict[tuple[str, ...], Fraction] = {}
    for i, item in enumerate(vals):
        v = _object(item, f"/net_benefits/{i}", {"key", "value"})
        key = _key(v["key"], f"/net_benefits/{i}/key")
        if key in valued or key not in desired:
            _bad("pairing_mismatch", f"/net_benefits/{i}/key", "Invalid pair")
        valued[key] = _fraction(v["value"], f"/net_benefits/{i}/value")
    draws = sorted({k[2] for k in desired})
    strategies = sorted({k[1] for k in desired})
    if len(draws) * len(strategies) != len(desired):
        _bad("pairing_mismatch", "/group", "Incomplete strategy-by-draw panel")
    matrix = []
    keys = []
    exact = []
    for draw in draws:
        matrix_row = []
        for strategy in strategies:
            key = (
                group["scenario_id"],
                strategy,
                draw,
                group["replication_id"],
                group["perspective"],
                group["subgroup_id"],
            )
            if key not in valued:
                _bad("pairing_mismatch", "/net_benefits", "Missing explicitly keyed net benefit")
            value = valued[key]
            matrix_row.append(_f64(value, "/net_benefits/value"))
            keys.append(dict(zip(KEY_FIELDS, key)))
            exact.append(_wire(value))
        matrix.append(matrix_row)
    return _closed_output(
        "dapane:d2-voiage:0.1\n",
        {
            "schema_version": "dapane-d2-voiage/0.1",
            "provider": pin,
            "provider_execution": "not_executed",
            "input_d1_digest": expected_d1_digest,
            "group": group,
            "valuation": valuation,
            "draw_id_order": draws,
            "pair_keys": keys,
            "exact_net_benefit": exact,
            "value_array": {
                "value_array_id": value_array_id,
                "sample_count": len(draws),
                "strategy_names": strategies,
                "net_benefit": matrix,
            },
            "conversion": {
                "method": "exact_rational_to_f64",
                "absolute_tolerance": "1e-9",
                "source": "external_valued_outcome",
            },
        },
    )


def adoption_capacity(
    payload: Any, *, expected_previous_digest: str | None = None
) -> dict[str, Any]:
    """Convert externally supplied Innovate volumes into resource-demand envelopes.

    Capacity is a transparent bounded application arithmetic example, not a
    Kairos scheduler or a Dapane monetary valuation. Price feedback must arrive
    as a *new* externally recalculated Innovate output and explicit chain receipt.
    """
    p = _object(
        payload,
        "/",
        {
            "schema_version",
            "provider",
            "run_id",
            "iteration",
            "previous_evaluation_digest",
            "key",
            "resource",
            "observations",
            "feedback",
        },
    )
    if p["schema_version"] != "dapane-d2-innovate/0.1":
        _bad("unsupported_schema", "/schema_version", "Only dapane-d2-innovate/0.1")
    pin = negotiate(p["provider"])
    if pin["provider"] != "edithatogo/innovate":
        _bad("unsupported_provider", "/provider", "Expected Innovate")
    _ident(p["run_id"], "/run_id")
    key = dict(zip(KEY_FIELDS, _key(p["key"], "/key")))
    iteration = p["iteration"]
    if type(iteration) is not int or not 0 <= iteration <= 16:
        _bad("invalid_iteration", "/iteration", "Expected integer iteration 0..16")
    prev = p["previous_evaluation_digest"]
    feedback = _object(
        p["feedback"], "/feedback", {"price_affects_adoption", "mode", "valuation_digest"}
    )
    if type(feedback["price_affects_adoption"]) is not bool:
        _bad("invalid_feedback", "/feedback/price_affects_adoption", "Explicit Boolean required")
    if iteration == 0:
        if prev is not None or expected_previous_digest is not None:
            _bad(
                "feedback_chain", "/previous_evaluation_digest", "Initial trajectory has no parent"
            )
        if feedback != {"price_affects_adoption": False, "mode": "none", "valuation_digest": None}:
            _bad(
                "feedback_requires_external_revision",
                "/feedback",
                "No implicit price response allowed",
            )
    else:
        if (
            not isinstance(prev, str)
            or expected_previous_digest is None
            or prev != expected_previous_digest
        ):
            _bad(
                "feedback_chain",
                "/previous_evaluation_digest",
                "Independent prior output digest required",
            )
        _sha(prev, "/previous_evaluation_digest")
        if (
            feedback["price_affects_adoption"] is not True
            or feedback["mode"] != "external_recomputed"
            or not isinstance(feedback["valuation_digest"], str)
        ):
            _bad(
                "feedback_requires_external_revision",
                "/feedback",
                "Supply explicit externally recalculated model and valuation trigger",
            )
        _sha(feedback["valuation_digest"], "/feedback/valuation_digest")
    resource = _object(
        p["resource"], "/resource", {"id", "unit", "quantity_per_adoption", "capacity_per_period"}
    )
    for field in ("id", "unit"):
        _ident(resource[field], f"/resource/{field}")
    per_adoption = _fraction(
        resource["quantity_per_adoption"], "/resource/quantity_per_adoption", nonnegative=True
    )
    capacity = _fraction(
        resource["capacity_per_period"], "/resource/capacity_per_period", nonnegative=True
    )
    if capacity == 0 or per_adoption == 0:
        _bad("invalid_capacity", "/resource", "Positive capacity and intensity required")
    observations = p["observations"]
    if not isinstance(observations, list) or not 1 <= len(observations) <= 120:
        _bad("invalid_adoption", "/observations", "1..120 externally supplied periods required")
    backlog = Fraction(0)
    last = ""
    steps = []
    for i, obs in enumerate(observations):
        row = _object(obs, f"/observations/{i}", {"period", "new_adoptions"})
        period = row["period"]
        m = _PERIOD.fullmatch(period) if isinstance(period, str) else None
        if not m or not 1 <= int(m.group(2)) <= 12 or period <= last:
            _bad(
                "invalid_period_sequence",
                f"/observations/{i}/period",
                "Strict ascending YYYY-MM periods required",
            )
        last = period
        adopted = row["new_adoptions"]
        if type(adopted) is not int or adopted < 0 or adopted > 10**9:
            _bad(
                "invalid_adoption",
                f"/observations/{i}/new_adoptions",
                "Nonnegative integer count required",
            )
        demand = adopted * per_adoption + backlog
        served = min(demand, capacity)
        backlog = demand - served
        if any(
            v.numerator.bit_length() > 4096 or v.denominator.bit_length() > 4096
            for v in (demand, served, backlog)
        ):
            _bad(
                "precision_limit", f"/observations/{i}", "Derived resource total exceeds 4096 bits"
            )
        steps.append(
            {
                "period": period,
                "new_adoptions": adopted,
                "new_resource_use": _wire(adopted * per_adoption),
                "demand": _wire(demand),
                "served": _wire(served),
                "backlog": _wire(backlog),
                "capacity_exceeded": demand > capacity,
            }
        )
    return _closed_output(
        "dapane:d2-adoption:0.1\n",
        {
            "schema_version": p["schema_version"],
            "run_id": p["run_id"],
            "provider": pin,
            "provider_execution": "externally_supplied_trajectory",
            "key": key,
            "iteration": iteration,
            "previous_evaluation_digest": prev,
            "feedback_mode": feedback["mode"],
            "triggering_valuation_digest": feedback["valuation_digest"],
            "resource": resource,
            "periods": steps,
            "pricing_execution": "not_executed",
        },
    )


def paignia_packet(payload: Any) -> dict[str, Any]:
    """Build a typed static-game construction blueprint, without invoking Paignia.

    A Paignia application must construct native GameSpecification/Node types and
    run validate_for_profile. There is no assumed Paignia JSON wire protocol.
    """
    p = _object(
        payload,
        "/",
        {"schema_version", "provider", "game_id", "player_id", "key", "payoff_mapping", "actions"},
    )
    if p["schema_version"] != "dapane-d2-paignia/0.1":
        _bad("unsupported_schema", "/schema_version", "Only dapane-d2-paignia/0.1")
    pin = negotiate(p["provider"])
    if pin["provider"] != "edithatogo/paignia":
        _bad("unsupported_provider", "/provider", "Expected Paignia")
    game_id = _ident(p["game_id"], "/game_id")
    player_id = _ident(p["player_id"], "/player_id")
    key = dict(zip(KEY_FIELDS, _key(p["key"], "/key")))
    m = _object(
        p["payoff_mapping"],
        "/payoff_mapping",
        {
            "source_digest",
            "method",
            "unit",
            "price_basis",
            "transfer_treatment",
            "domestic_transfer_balance",
        },
    )
    _sha(m["source_digest"], "/payoff_mapping/source_digest")
    if (
        m["method"] != "explicit_assessed_utility"
        or m["unit"] != "utility"
        or m["price_basis"] != "not_applicable"
        or m["transfer_treatment"] != "excluded"
    ):
        _bad(
            "payoff_semantics",
            "/payoff_mapping",
            "Payoffs must be externally justified utilities; transfers excluded",
        )
    if _fraction(m["domestic_transfer_balance"], "/payoff_mapping/domestic_transfer_balance") != 0:
        _bad(
            "transfer_imbalance",
            "/payoff_mapping/domestic_transfer_balance",
            "Domestic transfer cannot create societal net benefit",
        )
    actions = p["actions"]
    if not isinstance(actions, list) or not 2 <= len(actions) <= 32:
        _bad("invalid_request", "/actions", "Two to 32 explicit actions required")
    ids = set()
    terminals = {}
    edges = []
    exact_payoffs = []
    for i, row in enumerate(actions):
        a = _object(row, f"/actions/{i}", {"id", "utility"})
        action = _ident(a["id"], f"/actions/{i}/id")
        if action in ids:
            _bad("duplicate_action", f"/actions/{i}/id", "Each decision action must be unique")
        ids.add(action)
        terminal = f"terminal:{action}"
        if len(terminal.encode("utf-8")) > 128:
            _bad("invalid_identity", f"/actions/{i}/id", "Terminal identity would exceed 128 bytes")
        v = _fraction(a["utility"], f"/actions/{i}/utility")
        terminals[terminal] = {
            "kind": "Terminal",
            "payoffs": {player_id: _f64(v, f"/actions/{i}/utility")},
        }
        edges.append({"action": action, "target": terminal})
        exact_payoffs.append({"action": action, "utility": _wire(v)})
    graph = {
        "root": "start",
        "nodes": {"start": {"kind": "Decision", "player": player_id, "edges": edges}, **terminals},
    }
    return _closed_output(
        "dapane:d2-paignia:0.1\n",
        {
            "schema_version": p["schema_version"],
            "provider": pin,
            "provider_execution": "not_executed",
            "native_wire_supported": False,
            "key": key,
            "payoff_mapping": m,
            "exact_payoffs": exact_payoffs,
            "game_specification": {"schema_version": "1.0.0", "id": game_id, "game": graph},
            "application_requirement": "Construct Paignia native structs and validate_for_profile on qualified artifacts",
        },
    )


def innovate_adoption_capacity_native(payload: Any, innovate_binary: str) -> dict[str, Any]:
    """Call Innovate's native execute_json for adoption-capacity evaluation.

    Converts Dapane's d2-innovate input to Innovate's execute_json format,
    calls the innovate-native binary via subprocess, and returns the result
    wrapped in Dapane's d2-innovate output envelope.
    """
    p = _object(
        payload,
        "/",
        {
            "schema_version",
            "provider",
            "run_id",
            "iteration",
            "previous_evaluation_digest",
            "key",
            "resource",
            "observations",
            "feedback",
        },
    )
    if p["schema_version"] != "dapane-d2-innovate/0.1":
        _bad("unsupported_schema", "/schema_version", "Only dapane-d2-innovate/0.1")
    pin = negotiate(p["provider"])
    if pin["provider"] != "edithatogo/innovate":
        _bad("unsupported_provider", "/provider", "Expected Innovate")

    run_id = _ident(p["run_id"], "/run_id")
    iteration = p["iteration"]
    if type(iteration) is not int or not 0 <= iteration <= 16:
        _bad("invalid_iteration", "/iteration", "Expected integer iteration 0..16")

    key = dict(zip(KEY_FIELDS, _key(p["key"], "/key")))

    # Build Innovate execute_json request
    innovate_request = {
        "schema_version": "2.0",
        "operation": "dapane_adoption_capacity",
        "model_key": "dapane-adoption-capacity",
        "payload": {
            "run_id": run_id,
            "iteration": iteration,
            "previous_evaluation_digest": p["previous_evaluation_digest"],
            "key": key,
            "resource": p["resource"],
            "observations": p["observations"],
            "feedback": p["feedback"],
        },
    }

    # Write request to temp file and call innovate-native
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as req_file:
        req_file.write(json.dumps(innovate_request))
        req_path = req_file.name
    out_path = req_path + ".out"
    try:
        result = subprocess.run(
            [innovate_binary, "predict", "--request", req_path, "--output", out_path],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            _bad(
                "native_provider_failed",
                "/",
                f"Innovate native exited {result.returncode}: {result.stderr.strip()}",
            )
        with open(out_path, encoding="utf-8") as f:
            innovate_response = json.loads(f.read())
    finally:
        for path in (req_path, out_path):
            try:
                os.unlink(path)
            except OSError:
                pass

    if innovate_response.get("error") is not None:
        err = innovate_response["error"]
        _bad(
            "native_provider_error",
            "/",
            f"Innovate error: {err.get('code', 'unknown')}: {err.get('message', 'unknown')}",
        )

    result_data = innovate_response.get("result", {})

    return _closed_output(
        "dapane:d2-adoption:0.1\n",
        {
            "schema_version": p["schema_version"],
            "run_id": run_id,
            "provider": pin,
            "provider_execution": "native_invoked",
            "key": key,
            "iteration": iteration,
            "previous_evaluation_digest": p["previous_evaluation_digest"],
            "feedback_mode": p["feedback"].get("mode", "none"),
            "triggering_valuation_digest": p["feedback"].get("valuation_digest"),
            "resource": result_data.get("resource", p["resource"]),
            "periods": result_data.get("periods", []),
            "pricing_execution": "native_invoked",
            "innovate_response": innovate_response,
        },
    )


def _provider_executable(binary: str, expected: str) -> str:
    path = shutil.which(binary)
    if not path:
        _bad("provider_unavailable", "/provider", "Cannot locate the selected provider executable")
    with open(path, "rb") as stream:
        actual = "sha256:" + file_digest(stream, "sha256").hexdigest()
    if actual != expected:
        _bad("provider_digest_mismatch", "/provider/artifact_digest", "Executable digest differs")
    return path


def paignia_game_solve_native(payload: Any, paignia_binary: str) -> dict[str, Any]:
    """Run a profile-qualified caller on the same validated game used for preparation."""
    packet = paignia_packet(payload)
    graph = packet["game_specification"]
    paignia_binary = _provider_executable(paignia_binary, packet["provider"]["artifact_digest"])
    with tempfile.TemporaryDirectory() as directory:
        request = os.path.join(directory, "game.json")
        response = os.path.join(directory, "solution.json")
        with open(request, "w", encoding="utf-8") as stream:
            json.dump(graph, stream)
        result = subprocess.run(
            [paignia_binary, "solve", "--request", request, "--output", response],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode:
            _bad("native_provider_failed", "/", f"Paignia native exited {result.returncode}")
        with open(response, encoding="utf-8") as stream:
            envelope = json.load(stream)
            solution = envelope.get("solution") if isinstance(envelope, dict) else None
    if not isinstance(solution, dict):
        _bad("native_provider_error", "/", "Paignia returned no solution")
    provider = packet["provider"]
    root = graph["game"]["root"]
    node = graph["game"]["nodes"][root]
    payoffs = {
        edge["action"]: graph["game"]["nodes"][edge["target"]]["payoffs"][node["player"]]
        for edge in node["edges"]
    }
    action = solution.get("selected_action")
    payoff = solution.get("expected_payoff")
    if (
        solution.get("profile") != provider["contract"]
        or solution.get("source_revision") != provider["revision"]
        or solution.get("root") != root
        or not isinstance(action, str)
        or action not in payoffs
        or type(payoff) not in (float, int)
        or payoff != payoffs[action]
    ):
        _bad("native_provider_error", "/", "Paignia returned an inconsistent solution or source")
    del packet["output_digest"]
    packet.update(
        provider_execution="native_invoked",
        native_wire_supported=True,
        paignia_solution=solution,
        application_requirement=None,
    )
    return _closed_output("dapane:d2-paignia:0.1\n", packet)
