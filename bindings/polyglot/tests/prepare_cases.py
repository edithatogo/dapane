#!/usr/bin/env python3
"""Check independent synthetic assertions, then capture full Rust parity reports.

The projection assertions are independent expected values. Complete reports are
CLI regression oracles, never described as independent numerical references.
"""

from __future__ import annotations

import argparse
import copy
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def prepare(cli: Path, output: Path) -> int:
    output.mkdir(parents=True, exist_ok=False)
    cases = []
    expected = json.loads((ROOT / "fixtures/expected.json").read_text())["fixtures"]
    for filename, assertions in expected.items():
        request = json.loads((ROOT / "fixtures" / filename).read_text())
        cases.append((filename.removesuffix(".json"), "point", request, assertions, "ok"))
    baseline = copy.deepcopy(cases[0][2])
    for name, quantity, amount, exact, rounded in [
        (
            "large-integer",
            "9007199254740993",
            "1",
            ("9007199254740993", "1"),
            "9007199254740993.00",
        ),
        ("rational", {"numerator": "1", "denominator": "3"}, "1", ("1", "3"), "0.33"),
        ("zero", "0", "90", ("0", "1"), "0.00"),
    ]:
        request = copy.deepcopy(baseline)
        request["usage"][0]["quantity"] = quantity
        request["quotes"][0]["amount"] = amount
        cases.append(
            (
                name,
                "point",
                request,
                {
                    "totals": {
                        "exact": dict(zip(("numerator", "denominator"), exact)),
                        "rounded": rounded,
                    }
                },
                "ok",
            )
        )
    request = copy.deepcopy(baseline)
    request["run_id"] = "synthetic-\u03b4-\u6f22\u5b57"
    cases.append(("unicode", "point", request, {"run_id": request["run_id"]}, "ok"))
    for filename in sorted((ROOT / "fixtures/genomics-capacity").glob("*.json")):
        if filename.name in {"expected.json", "scenario.json", "v0.1-digests.json"}:
            continue
        request = json.loads(filename.read_text())
        cases.append((filename.stem, "point", request, {}, "ok"))
    interval = json.loads((ROOT / "fixtures/intervals/rate-boundary.json").read_text())
    cases.append(
        (
            "rate-boundary",
            "interval",
            interval,
            {
                "method_version": "dapane-intervals-v0.1.0",
                "report": {
                    "totals": {
                        "rounded": "110.00",
                        "exact": {"numerator": "110", "denominator": "1"},
                    }
                },
            },
            "ok",
        )
    )
    half_even = copy.deepcopy(interval)
    for quote in half_even["request"]["quotes"]:
        quote["amount"] = "0.01"
    half_even["intervals"][0].update(start="2026-01-31", end="2026-02-02", quantity="1")
    cases.append(
        (
            "segment-half-even",
            "interval",
            half_even,
            {
                "report": {
                    "totals": {"rounded": "0.00", "exact": {"numerator": "1", "denominator": "100"}}
                }
            },
            "ok",
        )
    )
    invalid = [
        ("float-quantity", lambda r: r["usage"][0].update(quantity=0.5), "invalid_request"),
        ("null-quantity", lambda r: r["usage"][0].update(quantity=None), "invalid_request"),
        ("missing-quantity", lambda r: r["usage"][0].pop("quantity"), "invalid_request"),
        ("unknown-field", lambda r: r.update(unknown=True), "invalid_request"),
        ("v01-capacity", lambda r: r.update(capacity_allocations=[]), "invalid_request"),
        ("unknown-version", lambda r: r.update(schema_version="99.0"), "unsupported_schema"),
    ]
    for name, change, code in invalid:
        request = copy.deepcopy(baseline)
        change(request)
        cases.append((name, "point", request, {}, code))
    cases += [
        (
            "duplicate-keys",
            "point",
            '{"schema_version":"0.1","schema_version":"0.2"}',
            {},
            "invalid_json",
        ),
        ("malformed", "point", "{", {}, "invalid_json"),
    ]

    def subset(actual, assertions):
        for key, value in assertions.items():
            if isinstance(value, dict):
                child = actual[key]
                if isinstance(child, list):
                    child = {item.get("id", item.get("object_id")): item for item in child}
                subset(child, value)
            else:
                assert actual[key] == value, (key, actual[key], value)

    index = ["name\toperation\tstatus"]
    for name, operation, request, assertions, status in cases:
        raw = request if isinstance(request, str) else json.dumps(request, ensure_ascii=False)
        command = "evaluate" if operation == "point" else "evaluate-intervals"
        result = subprocess.run(
            [str(cli), command, "-"], input=raw, text=True, capture_output=True, check=False
        )
        if status == "ok":
            assert result.returncode == 0, (name, result.stderr)
            report = result.stdout.strip()
            subset(json.loads(report), assertions)
        else:
            assert result.returncode != 0 and not result.stdout, (name, result)
            report = result.stderr.strip()
            assert json.loads(report)["code"] == status, (name, report, status)
        (output / f"{name}.input.json").write_text(raw, encoding="utf-8")
        (output / f"{name}.output.json").write_text(report, encoding="utf-8")
        index.append(f"{name}\t{operation}\t{status}")
    (output / "cases.tsv").write_text("\n".join(index) + "\n")
    return len(cases)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(f"Prepared {prepare(args.cli.resolve(), args.output.resolve())} synthetic parity cases")
