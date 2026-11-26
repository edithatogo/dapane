# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Verify cell-level parity failures independently of the restricted workbook."""

import pytest

from tools.verify_v15_scenarios import _compare


@pytest.mark.parametrize(
    ("sheet", "address", "before", "after", "kind"),
    [
        (
            "Synthetic1",
            "B1",
            {"numerator": "1", "denominator": "3"},
            {"numerator": "1", "denominator": "4"},
            "value",
        ),
        ("Synthetic1", "B2", {"value": True}, {"value": 1}, "value"),
        ("Synthetic2", "B1", {"error": "#REF!"}, {"error": "#DIV/0!"}, "Excel error"),
    ],
)
def test_comparison_reports_the_changed_cell(sheet, address, before, after, kind):
    target = sheet, address
    with pytest.raises(
        ValueError, match=rf"example: exact {kind} differs at {sheet}!{address}"
    ):
        _compare("example", {target}, {target: before}, {target: after})


def test_matching_outputs_must_cover_every_original_formula():
    target = ("Synthetic", "A1")
    _compare(
        "example", {target}, {target: {"error": "#REF!"}}, {target: {"error": "#REF!"}}
    )
    with pytest.raises(
        ValueError, match="baseline is missing formula address Synthetic!A1"
    ):
        _compare("example", {target}, {}, {})
