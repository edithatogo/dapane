#!/usr/bin/env python3
"""Qualify installed domain consumers; all valuation stays in the Rust engine.

This is verification tooling, not an alternative costing implementation.
Expected values are independently specified constants. Generated requests,
workbook observations and reports stay in the caller's temporary output directory.
"""

from __future__ import annotations

import argparse
import copy
import importlib
import importlib.machinery
import importlib.metadata
import importlib.util
import json
import subprocess
import sys
from datetime import date
from fractions import Fraction
from pathlib import Path


def exact(value):
    """Read a report's exact rational for comparison with an independent oracle."""
    return Fraction(int(value["numerator"]), int(value["denominator"]))


def installed(module_name, distribution_name, source_root):
    """Require an independently installed distribution, never a source-tree import."""
    module = importlib.import_module(module_name)
    distribution = importlib.metadata.distribution(distribution_name)
    location = Path(module.__file__).resolve()
    installation = Path(distribution.locate_file("")).resolve()
    assert location.is_relative_to(installation), (module_name, location, installation)
    assert not location.is_relative_to(source_root.resolve()), (module_name, location)
    return module


def native_parity(request, cli, report):
    """Compare the complete installed Python report with the native CLI report."""
    result = subprocess.run(
        [str(cli), "evaluate", "-"],
        input=json.dumps(request, allow_nan=False),
        text=True,
        capture_output=True,
        check=True,
    )
    assert json.loads(result.stdout) == report


def rejected(operation, code=None):
    """A negative case cannot pass by returning a partial or missing result."""
    try:
        operation()
    except ValueError as error:
        if code is not None:
            assert getattr(error, "code", None) == code, str(error)
    else:
        raise AssertionError("Expected a rejected request")


def native_boundary(args):
    """Exercise actual extension loading, retained ownership and exact transport."""
    dapane = installed("dapane", "dapane", args.dapane_root)
    native = installed("dapane._native", "dapane", args.dapane_root)
    assert any(
        native.__file__.endswith(suffix) for suffix in importlib.machinery.EXTENSION_SUFFIXES
    )
    request = json.loads((args.dapane_root / "fixtures/subcent-allocation.json").read_text())
    before = copy.deepcopy(request)
    report = dapane.evaluate(request)
    assert request == before
    assert [share["rounded"] for share in report["allocations"][0]["shares"]] == [
        "0.02",
        "0.02",
        "0.01",
    ]
    assert report["totals"]["rounded"] == "0.05"
    native_parity(request, args.cli, report)
    return dapane


def workforce(args, dapane):
    """Export a real provider release and price explicit synthetic staff exposure."""
    assert sys.version_info[:3] == (3, 15, 2), sys.version
    installed(
        "microcosting_healthworkforce",
        "microcosting-healthworkforce",
        args.provider_root,
    )
    adapter = importlib.import_module("microcosting_healthworkforce.dapane_adapter")
    quotes = importlib.import_module("microcosting_healthworkforce.unit_quotes")
    legacy = importlib.import_module("src.unit_quotes")
    assert quotes is legacy
    assert quotes.UnitQuoteRelease is legacy.UnitQuoteRelease

    example = args.provider_root / "examples/dapane"
    release = quotes.UnitQuoteRelease.model_validate_json(
        (example / "qld-hp3p1-release.json").read_text()
    )
    binding_data = json.loads((example / "qld-hp3p1-bindings.json").read_text())
    if isinstance(binding_data, dict):
        binding_data = binding_data["bindings"]
    bindings = tuple(
        adapter.DapaneQuoteBinding(**{**row, "components": tuple(row["components"])})
        for row in binding_data
    )
    artifact = adapter.export_dapane_quotes(release, bindings)
    encoded = json.dumps(artifact, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    digest = artifact["artifact_sha256"]
    pins = json.loads((args.dapane_root / "docs/provider-consumers.lock.json").read_text())
    assert digest == pins["workforce"]["artifact_sha256"]
    loaded = adapter.load_dapane_quotes_json(encoded, expected_sha256=digest)
    assert loaded == artifact
    hour = next(quote for quote in artifact["quotes"] if quote["unit"] == "hour")
    minute = next(quote for quote in artifact["quotes"] if quote["unit"] == "minute")
    assert hour["amount"] == minute["amount"] == "46.0658"
    assert hour["per_quantity"] == "1"
    assert minute["per_quantity"] == "60"
    assert hour["components"] == minute["components"] == ["base_salary"]
    assert minute["source"]["content_digest"] == (
        "sha256:6948663378e34af05b8dbf91d8799ad1dc14ee831136dc57165d3241d1af17ff"
    )

    quantity = quotes.QuoteQuantity(
        quantity_id="qualification-20min",
        quote_id=hour["id"],
        unit="hour",
        quantity=Fraction(1, 3),
        valued_on=date(2026, 11, 15),
        quantity_kind="analyst_assumption",
        basis="Synthetic twenty-minute exposure for installed-adapter qualification",
    )
    options = {
        "expected_sha256": digest,
        "run_id": "installed-workforce-qualification",
        "knowledge_cutoff": date(2026, 11, 15),
    }
    quantity_before = quantity.model_dump()
    request = adapter.build_dapane_request(encoded, (quantity,), **options)
    before = copy.deepcopy(request)
    report = dapane.evaluate(request)
    assert request == before
    assert report == adapter.evaluate_dapane(encoded, (quantity,), **options)
    assert quantity.model_dump() == quantity_before
    assert exact(report["totals"]["exact"]) == Fraction(230329, 15000)
    assert report["totals"]["rounded"] == "15.36"
    native_parity(request, args.cli, report)

    original_binding = next(binding for binding in bindings if binding.quote_id == hour["id"])
    old_quantity = quotes.QuoteQuantity(
        quantity_id=quantity.quantity_id,
        quote_id=original_binding.provider_quote_id,
        unit="hour",
        quantity=Fraction(1, 3),
        valued_on=quantity.valued_on,
        quantity_kind=quantity.quantity_kind,
        basis=quantity.basis,
    )
    assert legacy.price_units(release, (old_quantity,)).total == Fraction(230329, 15000)
    duplicate = copy.deepcopy(request)
    line = copy.deepcopy(duplicate["usage"][0])
    line["id"] += "-duplicate"
    duplicate["usage"].append(line)
    rejected(lambda: dapane.evaluate(duplicate), "component_overlap")
    altered = copy.deepcopy(artifact)
    altered["quotes"][0]["amount"] = "999"
    rejected(lambda: adapter.load_dapane_quotes_json(json.dumps(altered), expected_sha256=digest))
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "workforce-release.json").write_text(encoded, encoding="utf-8")
    (args.output / "handoff.json").write_text(
        json.dumps({"sha256": digest, "quote_id": minute["id"]}),
        encoding="utf-8",
    )
    return [
        "installed-workforce-and-legacy-identity",
        "source-selected-dated-release",
        "exact-nonterminating-exposure-and-native-parity",
        "legacy-pricing-parity",
        "duplicate-components-and-tampered-artifact-rejected",
        "exact-hour-minute-transport",
    ]


def genomics(args, dapane):
    """Consume the workforce file in the independently pinned genomic environment."""
    assert sys.version_info[:3] == (3, 15, 1), sys.version
    installed("genomics_microcosting", "genomics-microcosting", args.provider_root)
    assert importlib.util.find_spec("microcosting_healthworkforce") is None
    adapter = importlib.import_module("genomics_microcosting.dapane_adapter")
    encoded = (args.output / "workforce-release.json").read_text(encoding="utf-8")
    handoff = json.loads((args.output / "handoff.json").read_text())
    options = {
        "release_digest": handoff["sha256"],
        "quote_id": handoff["quote_id"],
        "service_date": "2026-11-15",
        "knowledge_cutoff": "2026-11-15",
        "role_mapping_basis": (
            "Qualification scenario maps historical extraction tasks to QLD HP3.1 "
            "base pay; this does not assert classification or payroll equivalence."
        ),
    }
    expected_shares = [
        ["26.87"],
        ["13.44", "13.43"],
        ["8.96", "8.96", "8.95"],
        ["6.72", "6.72", "6.72", "6.71"],
        ["5.38", "5.38", "5.37", "5.37", "5.37"],
        ["4.48", "4.48", "4.48", "4.48", "4.48", "4.47"],
    ]
    full_report = None
    for count, expected in enumerate(expected_shares, 1):
        specimens = tuple(f"specimen-{index:02}" for index in range(count))
        batches = (adapter.ExtractionBatch(f"batch-{count}", specimens),)
        case = {**options, "run_id": f"installed-genomics-{count}", "batches": batches}
        batches_before = copy.deepcopy(batches)
        request = adapter.manual_dna_extraction_request(encoded, **case)
        before = copy.deepcopy(request)
        report = dapane.evaluate(request)
        assert request == before
        assert report == adapter.evaluate_manual_dna_extraction(encoded, **case)
        assert batches == batches_before
        assert exact(report["totals"]["exact"]) == Fraction(1612303, 60000)
        assert report["totals"]["rounded"] == "26.87"
        assert len(report["lines"]) == 2
        assert len(report["allocations"]) == 1
        assert [item["rounded"] for item in report["allocations"][0]["shares"]] == expected
        assert report["totals"]["unattributed"] == "0.00"
        native_parity(request, args.cli, report)
        full_report = report

    specimens = ("specimen-00", "specimen-01", "specimen-02")
    attempts = (
        adapter.ExtractionBatch("attempt-1", specimens, outcome="failed"),
        adapter.ExtractionBatch("attempt-2", specimens, outcome="completed", repeat_of="attempt-1"),
    )
    case = {**options, "run_id": "installed-failed-retry", "batches": attempts}
    request = adapter.manual_dna_extraction_request(encoded, **case)
    report = adapter.evaluate_manual_dna_extraction(encoded, **case)
    assert exact(report["totals"]["exact"]) == Fraction(1612303, 30000)
    assert report["totals"]["rounded"] == "53.74"
    assert len(report["lines"]) == 4
    assert len(report["allocations"]) == 2
    totals = [item["total"] for item in report["object_totals"] if item["object_id"] in specimens]
    assert totals == ["17.92", "17.92", "17.90"]
    native_parity(request, args.cli, report)
    duplicate = copy.deepcopy(request)
    line = copy.deepcopy(duplicate["usage"][0])
    line["id"] += "-duplicate"
    duplicate["usage"].append(line)
    rejected(lambda: dapane.evaluate(duplicate), "component_overlap")
    for overrides in (
        {"knowledge_cutoff": "2026-11-14"},
        {"service_date": "2026-11-16"},
        {"role_mapping_basis": ""},
        {"release_digest": "0" * 64},
    ):
        invalid = {**case, **overrides}
        rejected(lambda invalid=invalid: adapter.evaluate_manual_dna_extraction(encoded, **invalid))

    # Isolate ledger-granularity changes from the separate source/rate change.
    # These are synthetic normalized per-specimen rows under the CURRENT quote,
    # not a relabelled historical price or an additional real resource ledger.
    control = {
        "schema_version": "0.1",
        "run_id": "same-rate-per-specimen-rounding-control",
        "knowledge_cutoff": options["knowledge_cutoff"],
        "policy": copy.deepcopy(full_report["policy"]),
        "quotes": copy.deepcopy(full_report["quote_snapshots"]),
        "usage": [],
        "objects": [],
    }
    selected_quote = control["quotes"][0]
    for index in range(6):
        specimen = f"control-specimen-{index}"
        control["objects"].append({"id": specimen, "kind": "specimen"})
        for step, quantity in (
            ("labwork", "5"),
            ("admin", {"numerator": "5", "denominator": "6"}),
        ):
            identity = f"{specimen}-{step}"
            control["usage"].append(
                {
                    "id": identity,
                    "use_id": identity,
                    "kind": "resource_use",
                    "target": selected_quote["target"],
                    "unit": "minute",
                    "quantity": quantity,
                    "service_date": options["service_date"],
                    "quote_id": selected_quote["id"],
                    "source": {
                        "id": "synthetic-rounding-control",
                        "version": "1",
                        "evidence": "synthetic",
                        "access": "public",
                        "validation": "unvalidated",
                        "locator": "Independent nominal-six-specimen ledger comparison",
                    },
                    "object_ids": [specimen],
                    "attribution_object_id": specimen,
                }
            )
    control_report = dapane.evaluate(control)
    assert exact(control_report["totals"]["exact"]) == Fraction(1612303, 60000)
    assert control_report["totals"]["rounded"] == "26.88"
    assert full_report["totals"]["rounded"] == "26.87"
    assert {item["total"] for item in control_report["object_totals"]} == {"4.48"}
    native_parity(control, args.cli, control_report)

    workbook = args.provider_root / (
        "data/Microcosting - Study 1 - Utilisation and Microcosts v15 (20230902).xlsm"
    )
    history = importlib.import_module("genomics_microcosting.dapane_workbook")
    observations = history.inspect_manual_extraction_workbook(workbook)
    historical_request = history.historical_manual_extraction_request(workbook)
    historical_report = dapane.evaluate(historical_request)
    native_parity(historical_request, args.cli, historical_report)
    comparison = history.compare_manual_extraction_workbook(workbook, full_report)
    sheet_module = importlib.import_module("genomics_microcosting.sheet_manager")
    engine_module = importlib.import_module("genomics_microcosting.calculation_engine")
    manager = sheet_module.SheetManager(workbook)
    legacy_engine = engine_module.CalculationEngine(manager)
    legacy_values = adapter.historical_manual_extraction(legacy_engine)
    for cell in ("AB22", "AB23", "AB24"):
        assert legacy_values[cell] is not None
        assert abs(
            Fraction(str(legacy_values[cell])) - Fraction(observations["cells"][cell]["cached"])
        ) <= Fraction(1, 10**12)
    assert observations["workbook_sha256"] == (
        "2990ff57504a51c5a9152b053a8e7cfa0e490f27a75bb356810f3564f96b5eb4"
    )
    assert observations["repairs_applied"] == []
    cells = observations["cells"]
    assert Fraction(cells["D22"]["cached"]) == 30
    assert Fraction(cells["D23"]["cached"]) == 5
    assert Fraction(cells["E22"]["cached"]) == Fraction(cells["E23"]["cached"]) == 6
    lab_rate = Fraction(cells["L22"]["cached"])
    admin_rate = Fraction(cells["L23"]["cached"])
    expected_lab = Fraction(5, 60) * lab_rate
    expected_admin = Fraction(5, 6 * 60) * admin_rate
    assert exact(historical_report["totals"]["exact"]) == expected_lab + expected_admin
    # Original spreadsheet caches use binary arithmetic. Compare that historical
    # representation independently; it is not the exact engine's rounding policy.
    assert abs(Fraction(cells["AB22"]["cached"]) - expected_lab) <= Fraction(1, 10**12)
    assert abs(Fraction(cells["AB23"]["cached"]) - expected_admin) <= Fraction(1, 10**12)
    assert comparison["mechanical_extraction"] == observations
    assert comparison["historical_replay"] == historical_report
    assert comparison["current_revaluation"] == full_report
    assert comparison["classification"]["formula_repairs_applied"] == []
    assert comparison["classification"]["changed_rate_or_components"] is True
    assert comparison["classification"]["scientific_validation"] is False
    # Provider-owned assertions qualify the precise mechanical/replay distinction;
    # retain the full result only as an ephemeral receipt, never a public artifact.
    (args.output / "historical-comparison.json").write_text(
        json.dumps(comparison, ensure_ascii=False, default=str), encoding="utf-8"
    )
    return [
        "installed-genomics-without-workforce-import",
        "six-batch-occupancies-and-native-parity",
        "failed-attempt-and-retry-per-batch-allocation",
        "source-ledger-and-allocated-views-not-double-counted",
        "same-rate-rounding-granularity-difference-separated-from-source-change",
        "source-dates-digest-and-role-mapping-rejections",
        "historical-workbook-inspection-and-native-replay",
        "installed-legacy-calculator-entry-point-and-cache-parity",
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("workforce", "genomics"))
    parser.add_argument("--provider-root", type=Path, required=True)
    parser.add_argument("--dapane-root", type=Path, required=True)
    parser.add_argument("--cli", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert not Path.cwd().resolve().is_relative_to(args.dapane_root.resolve())
    assert not Path.cwd().resolve().is_relative_to(args.provider_root.resolve())
    dapane = native_boundary(args)
    checks = workforce(args, dapane) if args.stage == "workforce" else genomics(args, dapane)
    print(
        json.dumps(
            {
                "status": "passed",
                "stage": args.stage,
                "python": sys.version.split()[0],
                "engine_version": dapane.__version__,
                "checks": ["native-extension-and-subcent-parity", *checks],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
