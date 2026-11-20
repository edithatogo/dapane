"""Arrange a fiscal perspective table for Voiage without dropping joint keys.

The array passed to ``value_of_perspective`` is only the net-benefit numbers.
The returned ledger keeps scenario, strategy, draw, replication, perspective
and subgroup on every cell, in the same order as the array.
"""

from __future__ import annotations

from collections.abc import Callable
from fractions import Fraction
from typing import Any, NoReturn

from bridge import D2Error, _f64, _fraction

SAMPLE_FIELDS = ("scenario_id", "draw_id", "replication_id", "subgroup_id")


class PerspectiveTableError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


def _bad(code: str, message: str) -> NoReturn:
    raise PerspectiveTableError(code, message)


def _text(row: dict[str, Any], name: str) -> str:
    value = row.get(name)
    if not isinstance(value, str) or not value:
        _bad("invalid_identifier", f"Row is missing {name}")
    return value


def _amount(value: Any) -> Fraction:
    try:
        return _fraction(value, "/net_monetary_benefit", max_digits=1234)
    except D2Error as error:
        raise PerspectiveTableError("invalid_amount", str(error)) from error


def _rows(table: dict[str, Any]) -> list[dict[str, Any]]:
    if (
        not isinstance(table, dict)
        or table.get("schema_version") != "dapane-fiscal-perspective-table/0.1"
    ):
        _bad("unsupported_schema", "Expected a fiscal perspective table")
    rows = table.get("rows")
    if not isinstance(rows, list) or not rows or any(not isinstance(row, dict) for row in rows):
        _bad("invalid_request", "Expected a nonempty list of fiscal rows")
    return rows


def arrange(table: dict[str, Any]) -> dict[str, Any]:
    """Arrange one scenario and subgroup into a sample × strategy × perspective grid."""
    rows = _rows(table)
    if len({(_text(row, "scenario_id"), _text(row, "subgroup_id")) for row in rows}) != 1:
        _bad("mixed_strata", "A decision grid requires one scenario and subgroup")
    samples: list[tuple[str, str, str, str]] = []
    strategies: list[str] = []
    perspectives: list[str] = []
    amounts: dict[tuple[tuple[str, str, str, str], str, str], Fraction] = {}
    for row in rows:
        if not isinstance(row, dict):
            _bad("invalid_request", "Perspective row must be an object")
        sample = tuple(_text(row, name) for name in SAMPLE_FIELDS)
        strategy = _text(row, "strategy_id")
        perspective = _text(row, "perspective")
        if sample not in samples:
            samples.append(sample)
        if strategy not in strategies:
            strategies.append(strategy)
        if perspective not in perspectives:
            perspectives.append(perspective)
        cell = (sample, strategy, perspective)
        if cell in amounts:
            _bad("duplicate_key", "A joint key is repeated in the perspective table")
        amounts[cell] = _amount(row.get("net_monetary_benefit"))
    if len(amounts) != len(samples) * len(strategies) * len(perspectives):
        _bad("incomplete_panel", "Every sample must carry every strategy and perspective")
    ledger = []
    grid: list[list[list[str]]] = []
    for sample in samples:
        strategy_rows = []
        for strategy in strategies:
            perspective_cells = []
            for perspective in perspectives:
                amount = amounts[(sample, strategy, perspective)]
                perspective_cells.append(f"{amount.numerator}/{amount.denominator}")
                ledger.append(
                    {
                        "scenario_id": sample[0],
                        "draw_id": sample[1],
                        "replication_id": sample[2],
                        "subgroup_id": sample[3],
                        "strategy_id": strategy,
                        "perspective": perspective,
                        "net_monetary_benefit": f"{amount.numerator}/{amount.denominator}",
                    }
                )
            strategy_rows.append(perspective_cells)
        grid.append(strategy_rows)
    return {
        "samples": [dict(zip(SAMPLE_FIELDS, sample, strict=True)) for sample in samples],
        "strategy_ids": strategies,
        "perspective_ids": perspectives,
        "net_monetary_benefit": grid,
        "cells": ledger,
    }


def _by_stratum(table: dict[str, Any], evaluate: Callable) -> dict[str, Any]:
    groups: dict[tuple[str, str], list] = {}
    for row in _rows(table):
        key = (_text(row, "scenario_id"), _text(row, "subgroup_id"))
        groups.setdefault(key, []).append(row)
    results = []
    for (scenario, subgroup), group in groups.items():
        grid = arrange({"schema_version": table["schema_version"], "rows": group})
        results.append({"scenario_id": scenario, "subgroup_id": subgroup, **evaluate(grid)})
    if len(results) == 1:
        return results[0]
    return {
        "provider": results[0]["provider"],
        "provider_function": results[0]["provider_function"],
        "strata": results,
        "cells": [cell for result in results for cell in result["cells"]],
    }


def _provider_grid(arranged: dict[str, Any]) -> list[list[list[float]]]:
    # Enforce the existing D2 conversion budget, preserving distinct payoffs even within it.
    seen: dict[float, Fraction] = {}

    def convert(cell: str) -> float:
        amount = Fraction(cell)
        try:
            value = _f64(amount, "/net_monetary_benefit")
        except D2Error as error:
            raise PerspectiveTableError(error.code, str(error)) from error
        if seen.setdefault(value, amount) != amount:
            _bad("precision_loss", "Distinct exact payoffs round to the same provider value")
        return value

    return [
        [[convert(cell) for cell in row] for row in sample]
        for sample in arranged["net_monetary_benefit"]
    ]


def value_of_perspective(table: dict[str, Any]) -> dict[str, Any]:
    """Evaluate each scenario/subgroup independently, preserving the single-stratum summary."""
    return _by_stratum(table, _voiage_summary)


def _voiage_summary(arranged: dict[str, Any]) -> dict[str, Any]:
    grid = _provider_grid(arranged)
    try:
        import numpy as np
        from voiage.methods.perspective import value_of_perspective as voiage_value
    except ImportError as error:
        _bad("provider_unavailable", str(error))
    values = np.array(grid, dtype=np.float64)
    result = voiage_value(
        values,
        strategy_names=arranged["strategy_ids"],
        perspective_names=arranged["perspective_ids"],
    )
    if list(result.strategy_names) != arranged["strategy_ids"]:
        _bad("identity_lost", "Voiage changed the strategy order")
    if list(result.perspective_ids) != arranged["perspective_ids"]:
        _bad("identity_lost", "Voiage changed the perspective order")
    return {
        "provider": "voiage",
        "provider_function": "voiage.methods.perspective.value_of_perspective",
        "optimal_strategy_names": list(result.optimal_strategy_names),
        "samples": arranged["samples"],
        "strategy_ids": arranged["strategy_ids"],
        "perspective_ids": arranged["perspective_ids"],
        "cells": arranged["cells"],
    }
