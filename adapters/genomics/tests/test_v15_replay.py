# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Independent synthetic checks for the original workbook's formula dialect."""

from fractions import Fraction

import pytest
from dapane_genomics.v15_replay import CellError, WorkbookReplay


def test_replay_resolves_exact_arithmetic_and_ignores_formula_caches():
    ledger = {
        "sheets": [
            {
                "catalogue": {"sheet": "Rates and activity"},
                "cells": [
                    {"coordinate": "A1", "stored_type": "n", "stored_value": "0.1"},
                    {"coordinate": "A2", "stored_type": "n", "stored_value": "0.2"},
                    {"coordinate": "A3", "stored_type": "s", "stored_value": "0", "text": "rate"},
                ],
            },
            {
                "catalogue": {"sheet": "Summary"},
                "cells": [
                    {
                        "coordinate": "A1",
                        "stored_type": "n",
                        "stored_value": "999",
                        "formula": "=SUM('Rates and activity'!$A$1:$A$3)",
                    },
                    {
                        "coordinate": "A2",
                        "stored_type": "n",
                        "stored_value": "999",
                        "formula": "=A1*(1+27%)*3",
                    },
                    {
                        "coordinate": "A3",
                        "stored_type": "n",
                        "stored_value": "999",
                        "formula": "=AVERAGE('Rates and activity'!A1:A4)",
                    },
                ],
            },
        ],
    }
    replay = WorkbookReplay(ledger)
    assert replay.value("Summary", "A1") == Fraction(3, 10)
    assert replay.value("Summary", "A2") == Fraction(1143, 1000)
    assert replay.value("Summary", "A3") == Fraction(3, 20)

    variant = WorkbookReplay(ledger, overrides={("Rates and activity", "A2"): "0.3"})
    assert variant.value("Summary", "A2") == Fraction(381, 250)
    assert replay.value("Summary", "A2") == Fraction(1143, 1000)
    with pytest.raises(ValueError, match="numeric input"):
        WorkbookReplay(ledger, overrides={("Summary", "A1"): "5"})


def test_replay_preserves_distinct_cached_errors_and_recalculates_annuity():
    # Two end-of-period payments of 121 have discounted values 110 and 100
    # at 10%, giving an exact present value of 210.
    formulas = ["=PMT(10%,2,-210)", "=PMT(0,3,-210)", "=1/(A6-A6)", "=SUM(#REF!,1)", "=A4*4"]
    ledger = {
        "sheets": [
            {
                "catalogue": {"sheet": "Equipment"},
                "cells": [
                    {
                        "coordinate": f"A{row}",
                        "stored_type": "n",
                        "stored_value": "0",
                        "formula": formula,
                    }
                    for row, formula in enumerate(formulas, 1)
                ],
            }
        ]
    }
    replay = WorkbookReplay(ledger)
    assert replay.value("Equipment", "A1") == Fraction(121)
    assert replay.value("Equipment", "A2") == Fraction(70)
    assert replay.value("Equipment", "A3") == CellError("#DIV/0!")
    assert replay.value("Equipment", "A4") == CellError("#REF!")
    assert replay.value("Equipment", "A5") == CellError("#REF!")
