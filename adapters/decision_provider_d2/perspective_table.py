"""Arrange a fiscal perspective table for Voiage without dropping joint keys.

The array passed to ``value_of_perspective`` is only the net-benefit numbers.
The returned ledger keeps scenario, strategy, draw, replication, perspective
and subgroup on every cell, in the same order as the array.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, NoReturn

KEY_FIELDS = (
    "scenario_id",
    "strategy_id",
    "draw_id",
    "replication_id",
    "perspective",
    "subgroup_id",
)
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
    if not isinstance(value, dict):
        _bad("invalid_amount", "Net monetary benefit must be an exact rational")
    try:
        return Fraction(int(value["numerator"]), int(value["denominator"]))
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        _bad("invalid_amount", "Net monetary benefit must be an exact rational")


def arrange(table: dict[str, Any]) -> dict[str, Any]:
    """Return the complete sample × strategy × perspective grid and its key ledger."""
    if table.get("schema_version") != "dapane-fiscal-perspective-table/0.1":
        _bad("unsupported_schema", "Expected a fiscal perspective table")
    rows = table.get("rows")
    if not isinstance(rows, list) or not rows:
        _bad("invalid_request", "Perspective table requires at least one row")
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
    missing = [
        (sample, strategy, perspective)
        for sample in samples
        for strategy in strategies
        for perspective in perspectives
        if (sample, strategy, perspective) not in amounts
    ]
    if missing:
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


def value_of_perspective(table: dict[str, Any]) -> dict[str, Any]:
    """Call the installed Voiage function and return its summary beside the key ledger."""
    arranged = arrange(table)
    try:
        import numpy as np
        from voiage.methods.perspective import value_of_perspective as voiage_value
    except ImportError as error:
        _bad("provider_unavailable", str(error))
    values = np.array(
        [
            [[float(Fraction(cell)) for cell in perspectives] for perspectives in strategies]
            for strategies in arranged["net_monetary_benefit"]
        ],
        dtype=np.float64,
    )
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
