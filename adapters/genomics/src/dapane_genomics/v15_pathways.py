# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Compose historical pathway cost requests from the exact v15 workbook."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

from genomics_microcosting.dapane_adapter import WORKBOOK_SHA256, evaluate_native_request
from genomics_microcosting.dapane_workbook import historical_use, new_historical_request

from .v15_replay import WorkbookReplay

_SUMMARY = "Summary Table"
_DETAIL = "Detailed Table"
_COST_COLUMNS = {"B": "equipment", "E": "consumables", "H": "labour"}
_PATHWAYS = {"panel": 5, "ea-p": 20, "ea-t": 35, "wga-p": 50, "wga-t": 65}
_SENSITIVITY = (
    "WB10",
    "WB11",
    "WB12",
    "WB13",
    "WB14",
    "WB15",
    "WB16",
    "WB19",
    "WB20",
    "WB22",
    "WB23",
    "WB24",
    "WB25",
)
_DIRECT_CHARGE = re.compile(r"^=\(?'([^']+)'!(N\d+|Q\d+)\)?$")
_DETAIL_RANGE = re.compile(r"^\$?N\$?(\d+)(?::\$?N\$?(\d+))?$")


@dataclass(frozen=True)
class _Charge:
    sheet: str
    coordinate: str
    quantity: Fraction
    rate: Fraction

    @property
    def value(self) -> Fraction:
        return self.quantity * self.rate


def _exact(value: Fraction) -> dict[str, str]:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def _fraction(value: dict[str, str]) -> Fraction:
    return Fraction(int(value["numerator"]), int(value["denominator"]))


def _number(book: WorkbookReplay, sheet: str, coordinate: str) -> Fraction:
    value = book.value(sheet, coordinate)
    if not isinstance(value, Fraction):
        raise ValueError(f"Expected a numeric workbook value at {sheet}!{coordinate}")
    return value


def _detail_charges(book: WorkbookReplay, coordinate: str) -> list[_Charge]:
    cell = book.cells[_DETAIL][coordinate]
    source = _number(book, _DETAIL, coordinate)
    formula = cell["formula"]
    row = coordinate[1:]
    if formula in {f"=F{row}*J{row}", f"=J{row}*F{row}"}:
        return [
            _Charge(
                _DETAIL,
                coordinate,
                _number(book, _DETAIL, f"F{row}"),
                _number(book, _DETAIL, f"J{row}"),
            )
        ]
    ranges = [_DETAIL_RANGE.fullmatch(reference) for reference in cell["references"]]
    if ranges and all(ranges):
        charges = []
        for first, last in (item.groups() for item in ranges if item is not None):
            for index in range(int(first), int(last or first) + 1):
                target = f"N{index}"
                if isinstance(book.value(_DETAIL, target), Fraction):
                    charges.extend(_detail_charges(book, target))
        if sum((charge.value for charge in charges), Fraction(0)) != source:
            raise ValueError(f"Detailed booked charges do not reconcile at {coordinate}")
        return charges
    # These formulas already state the booked charge. Keep its coordinates and
    # dependency formula instead of assigning it a conjectural quantity or rate.
    return [_Charge(_DETAIL, coordinate, Fraction(1), source)]


def _component_charges(book: WorkbookReplay, coordinate: str) -> list[_Charge]:
    value = book.value(_SUMMARY, coordinate)
    if value is None or value == 0 or value == "-":
        return []
    if not isinstance(value, Fraction):
        raise ValueError(f"Unexpected summary component at {coordinate}")
    record = book.cells[_SUMMARY][coordinate]
    match = _DIRECT_CHARGE.fullmatch(record.get("formula", ""))
    if match is None:
        raise ValueError(f"Unexpected booked charge reference at {coordinate}")
    sheet, cell = match.groups()
    if sheet == _DETAIL:
        charges = _detail_charges(book, cell)
    else:
        charges = [_Charge(sheet, cell, Fraction(1), _number(book, sheet, cell))]
    if sum((charge.value for charge in charges), Fraction(0)) != value:
        raise ValueError(f"Summary component and detail disagree at {coordinate}")
    return charges


def _append_charge(
    request: dict[str, Any],
    charge: _Charge,
    line_id: str,
    component: str,
    summary_cell: str,
    fx: Fraction,
) -> None:
    currency = request["policy"]["currency"]
    locator = f"{charge.sheet}!{charge.coordinate} booked at {_SUMMARY}!{summary_cell}"
    if currency == "USD":
        locator += f" with {_SUMMARY}!B81"
    quote = {
        "id": line_id,
        "kind": "resource_use",
        "currency": currency,
        "target": line_id,
        "unit": "booked_quantity",
        "amount": _exact(charge.rate * fx),
        "per_quantity": "1",
        "price_year": 2023,
        "basis": "financial_cost",
        "components": [component],
        "valid_from": "2023-09-02",
        "valid_to": "2023-09-03",
        "known_from": "2023-09-02",
        "source": {
            "id": "vcgs-workbook-v15",
            "version": "preserved-v15",
            "evidence": "derived",
            "access": "restricted",
            "validation": "source_verified",
            "content_digest": f"sha256:{WORKBOOK_SHA256}",
            "locator": locator,
        },
    }
    request["quotes"].append(quote)
    request["usage"].append(
        historical_use(line_id, _exact(charge.quantity), quote, locator=locator)
    )


def pathway_requests(ledger: dict[str, Any]) -> dict[str, Any]:
    """Return exact AUD and USD inputs with source links for each booked charge."""
    if ledger["source_sha256"] != WORKBOOK_SHA256:
        raise ValueError("Pathway mapping requires the original v15 workbook ledger")
    book = WorkbookReplay(ledger)
    fx = _number(book, _SUMMARY, "B81")
    pathways = {}
    for pathway, start in _PATHWAYS.items():
        for currency, conversion, total_col in (("AUD", Fraction(1), "N"), ("USD", fx, "O")):
            name = f"historical-v15-{pathway}-{currency.lower()}"
            request = new_historical_request(name)
            request["policy"]["currency"] = currency
            request["policy"]["id"] = "historical-v15-exact-pathway"
            stages = {}
            source_occurrences: dict[tuple[str, str], list[str]] = defaultdict(list)
            for row in range(start, start + 10):
                first = len(request["usage"])
                direct = Fraction(0)
                line_occurrences: Counter[str] = Counter()
                for col, component in _COST_COLUMNS.items():
                    coordinate = f"{col}{row}"
                    for charge in _component_charges(book, coordinate):
                        base_id = f"{coordinate}-{charge.coordinate}"
                        line_occurrences[base_id] += 1
                        line_id = f"{base_id}-{line_occurrences[base_id]}"
                        source_occurrences[charge.sheet, charge.coordinate].append(line_id)
                        _append_charge(request, charge, line_id, component, coordinate, conversion)
                        direct += charge.value
                overhead = _number(book, _SUMMARY, f"K{row}")
                if overhead != direct * Fraction("0.27"):
                    raise ValueError(f"Historical overhead base differs at K{row}")
                _append_charge(
                    request,
                    _Charge(_SUMMARY, f"K{row}", direct, Fraction("0.27")),
                    f"K{row}-overhead",
                    "overhead",
                    f"K{row}",
                    conversion,
                )
                expected = _number(book, _SUMMARY, f"{total_col}{row}")
                if expected != (direct + overhead) * conversion:
                    raise ValueError(f"Stage and workbook subtotal disagree at {total_col}{row}")
                stages[str(row)] = {
                    "stage": book.value(_SUMMARY, f"A{row}"),
                    "source": f"{_SUMMARY}!{total_col}{row}",
                    "exact": _exact(expected),
                    "lines": [use["id"] for use in request["usage"][first:]],
                }
            expected_pathway = _number(book, _SUMMARY, f"{total_col}{start + 10}")
            if expected_pathway != sum(
                (_fraction(stage["exact"]) for stage in stages.values()), Fraction(0)
            ):
                raise ValueError(f"Stages and pathway subtotal disagree at {total_col}{start + 10}")
            pathways[name] = {
                "denominator": "historical workbook test pathway",
                "request": request,
                "stages": stages,
                "expected_total": _exact(expected_pathway),
                "repeated_source_bookings": [
                    {"sheet": sheet, "cell": coordinate, "lines": lines}
                    for (sheet, coordinate), lines in source_occurrences.items()
                    if len(lines) > 1
                ],
            }

    # Keep the catalogue's original display/branch boundaries. These are
    # alternate views of the same ledger and are never added to its booked costs.
    sheets = {source["catalogue"]["id"]: source["catalogue"] for source in ledger["sheets"]}
    return {
        "source_sha256": WORKBOOK_SHA256,
        "aud_to_usd": _exact(fx),
        "pathways": pathways,
        "detailed_table": sheets["WB17"],
        "resource_tables": [sheets[f"WB{index}"] for index in range(28, 36)],
        "sensitivity_views": [sheets[identifier] for identifier in _SENSITIVITY],
    }


def evaluate_pathways(ledger: dict[str, Any]) -> dict[str, Any]:
    """Value each request in the native kernel and reconcile every recorded stage."""
    result = pathway_requests(ledger)
    for pathway in result["pathways"].values():
        report = evaluate_native_request(pathway["request"])
        if report["status"] != "complete" or report["totals"]["exact"] != pathway["expected_total"]:
            raise ValueError("Native total does not reconcile with the original pathway")
        lines = {line["id"]: _fraction(line["exact"]) for line in report["lines"]}
        for stage in pathway["stages"].values():
            actual = sum((lines[line_id] for line_id in stage["lines"]), Fraction(0))
            if actual != _fraction(stage["exact"]):
                raise ValueError(f"Native total does not reconcile at {stage['source']}")
        pathway["report"] = report
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    parser.add_argument("output", type=Path, help="New restricted file for the exact reports")
    args = parser.parse_args()
    result = evaluate_pathways(json.loads(args.ledger.read_bytes()))
    args.output.touch(mode=0o600, exist_ok=False)
    args.output.write_text(json.dumps(result, separators=(",", ":")) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
