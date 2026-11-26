# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Independent synthetic checks for the original workbook's formula dialect."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from io import BytesIO
from zipfile import ZipFile

import pytest
from openpyxl import Workbook
from openpyxl.formula import Tokenizer

from dapane_genomics import v15_pathways, v15_replay, workbook_ledger
from dapane_genomics.v15_replay import CellError, WorkbookReplay, replay_workbook
from dapane_genomics.workbook_ledger import inventory_workbook


def test_replay_resolves_exact_arithmetic_and_ignores_formula_caches():
    ledger = {
        "sheets": [
            {
                "catalogue": {"sheet": "Rates and activity"},
                "cells": [
                    {"coordinate": "A1", "stored_type": "n", "stored_value": "0.1"},
                    {"coordinate": "A2", "stored_type": "n", "stored_value": "0.2"},
                    {
                        "coordinate": "A3",
                        "stored_type": "s",
                        "stored_value": "0",
                        "text": "rate",
                    },
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
    formulas = [
        "=PMT(10%,2,-210)",
        "=PMT(0,3,-210)",
        "=1/(A6-A6)",
        "=SUM(#REF!,1)",
        "=A4*4",
    ]
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


def test_formula_transport_keeps_types_errors_and_exact_text_inputs():
    ledger = {
        "source_sha256": "synthetic",
        "sheets": [
            {
                "catalogue": {"id": "B1", "sheet": "Costs"},
                "cells": [
                    {"coordinate": "B1", "stored_type": "e", "stored_value": "#REF!"},
                    {"coordinate": "B2", "stored_type": "b", "stored_value": "1"},
                    {
                        "coordinate": "B3",
                        "stored_type": "str",
                        "stored_value": "unsupplied",
                    },
                    {"coordinate": "B5", "stored_type": "n", "stored_value": None},
                    *(
                        {
                            "coordinate": f"A{row}",
                            "stored_type": "n",
                            "stored_value": None,
                            "formula": expression,
                        }
                        for row, expression in enumerate(
                            (
                                "=B1",
                                "=B2",
                                "=B3",
                                "=-(+5)+B4+B5",
                                "=B3*1",
                                "=SUM(B4:B5)",
                                "=AVERAGE(B3:B5)",
                                "=PMT(-100%,2,100)",
                                "=PMT(#REF!,2,100)",
                                "=B2+B1",
                                "=B5",
                                "=B4:B5",
                                "=B4:B5+1",
                            ),
                            1,
                        )
                    ),
                ],
            }
        ],
    }
    results = replay_workbook(ledger)
    assert results["counts"] == {"formulas": 13, "errors": 8}
    values = results["sheets"][0]["formulas"]
    assert values["A1"] == {"error": "#REF!"}
    assert values["A2"] == {"value": True}
    assert values["A3"] == {"value": "unsupplied"}
    assert values["A4"] == {"numerator": "-5", "denominator": "1"}
    assert values["A5"] == {"error": "#VALUE!"}
    assert values["A6"] == {"numerator": "0", "denominator": "1"}
    assert values["A7"] == {"error": "#DIV/0!"}
    assert values["A8"] == {"error": "#NUM!"}
    assert values["A9"] == values["A10"] == {"error": "#REF!"}
    assert values["A11"] == {"numerator": "0", "denominator": "1"}
    assert values["A12"] == values["A13"] == {"error": "#VALUE!"}


@pytest.mark.parametrize(
    ("expression", "message"),
    [
        ("=A1", "Circular reference"),
        ("=SUM('Unlinked'!A:A)", "bounded v15 cell range"),
        ("=ABS(1)", "Unsupported v15 function"),
        ("=SUM(1 2)", "Expected close of v15 func"),
        ('="unknown"', "Unsupported v15 token"),
        ("=", "Unexpected end of v15 formula"),
        ("=1 2", "Unconsumed tokens"),
    ],
)
def test_unsupported_or_circular_formulas_fail_at_their_coordinate(expression, message):
    replay = WorkbookReplay(
        {
            "sheets": [
                {
                    "catalogue": {"sheet": "Costs"},
                    "cells": [{"coordinate": "A1", "formula": expression}],
                }
            ]
        }
    )
    with pytest.raises(ValueError, match=rf"Costs!A1: .*{message}"):
        replay.value("Costs", "A1")


def test_workbook_inventory_checks_identity_and_totals_before_acceptance():
    output = BytesIO()
    book = Workbook()
    book.active.append([1, "=A1*10"])
    book.save(output)
    book.close()
    payload = output.getvalue()
    sheet = {
        "id": "Synthetic",
        "sheet": "Sheet",
        "state": "visible",
        "nonempty_cells": 2,
        "formulas": 1,
    }
    catalogue = {
        "source_sha256": sha256(payload).hexdigest(),
        "sheet_count": 1,
        "formula_count": 1,
        "sheets": [sheet],
    }
    assert inventory_workbook(payload, catalogue)["counts"]["formula_cells"] == 1
    with pytest.raises(ValueError, match="source digests differ"):
        inventory_workbook(payload, {**catalogue, "source_sha256": "invalid"})
    with pytest.raises(ValueError, match="sheet identity differs"):
        inventory_workbook(
            payload, {**catalogue, "sheets": [{**sheet, "state": "hidden"}]}
        )
    with pytest.raises(ValueError, match="Workbook, reader and catalogue disagree"):
        inventory_workbook(payload, {**catalogue, "sheets": [{**sheet, "formulas": 2}]})
    with pytest.raises(ValueError, match="Workbook totals disagree"):
        inventory_workbook(payload, {**catalogue, "formula_count": 2})


def test_replay_rejects_binary_float_overrides_and_keeps_broken_sheet_references():
    inputs = {
        "sheets": [
            {
                "catalogue": {"sheet": "Costs"},
                "cells": [
                    {"coordinate": "A1", "stored_type": "n", "stored_value": "0.1"},
                    {"coordinate": "A2", "formula": "=Removed!A1"},
                ],
            }
        ]
    }
    assert WorkbookReplay(inputs).value("Costs", "A2") == CellError("#REF!")
    with pytest.raises(ValueError, match="exact strings"):
        WorkbookReplay(inputs, overrides={("Costs", "A1"): 0.2})


def test_replay_rejects_an_unrecognised_postfix_token(monkeypatch):
    tokens = Tokenizer("=1%")
    tokens.items[-1].value = "#"
    monkeypatch.setattr(v15_replay, "Tokenizer", lambda _: tokens)
    ledger = {
        "sheets": [
            {
                "catalogue": {"sheet": "Costs"},
                "cells": [{"coordinate": "A1", "formula": "=1#"}],
            }
        ]
    }
    with pytest.raises(ValueError, match="Unsupported v15 postfix operation"):
        WorkbookReplay(ledger).value("Costs", "A1")


def test_ledger_detects_inconsistent_archive_layout(monkeypatch):
    output = BytesIO()
    book = Workbook()
    book.active.append([1, "=A1*10"])
    book.save(output)
    book.close()
    payload = output.getvalue()
    catalogue = {
        "source_sha256": sha256(payload).hexdigest(),
        "sheet_count": 1,
        "formula_count": 1,
        "sheets": [
            {
                "id": "Synthetic",
                "sheet": "Sheet",
                "state": "visible",
                "nonempty_cells": 2,
                "formulas": 1,
            }
        ],
    }
    rewritten = BytesIO()
    with ZipFile(BytesIO(payload)) as original, ZipFile(rewritten, "w") as archive:
        for part in original.namelist():
            content = original.read(part)
            if part == "xl/worksheets/sheet1.xml":
                row = b'<c r="A1" t="n"><v>1</v></c>'
                assert row in content
                content = content.replace(row, row * 2)
            archive.writestr(part, content)
    invalid = rewritten.getvalue()
    with pytest.raises(ValueError, match="Duplicate coordinate Synthetic:A1"):
        inventory_workbook(
            invalid, {**catalogue, "source_sha256": sha256(invalid).hexdigest()}
        )
    monkeypatch.setattr(workbook_ledger, "_sheet_parts", lambda _: {})
    with pytest.raises(ValueError, match="reader and raw sheet relationships differ"):
        inventory_workbook(payload, catalogue)


def test_sheet_relationship_must_point_to_an_internal_worksheet():
    workbook = Workbook()
    output = BytesIO()
    workbook.save(output)
    workbook.close()
    layout = BytesIO()
    with ZipFile(output) as original, ZipFile(layout, "w") as changed:
        for name in original.namelist():
            item = original.read(name)
            if name == "xl/_rels/workbook.xml.rels":
                assert b"/xl/worksheets/sheet1.xml" in item
                item = item.replace(
                    b"/xl/worksheets/sheet1.xml",
                    b"/xl/not-a-worksheet.xml",
                )
            changed.writestr(name, item)
    with ZipFile(layout) as archive:
        with pytest.raises(ValueError, match="internal worksheet part"):
            workbook_ledger._sheet_parts(archive)


def test_pathway_sources_reject_an_incomplete_component_breakdown(monkeypatch):
    workbook = WorkbookReplay(
        {
            "sheets": [
                {
                    "catalogue": {"sheet": "Detailed Table"},
                    "cells": [
                        {"coordinate": "N5", "formula": "=N6+N7", "references": ["N6"]},
                        {"coordinate": "N6", "formula": "=10", "references": []},
                        {"coordinate": "N7", "formula": "=20", "references": []},
                    ],
                },
                {
                    "catalogue": {"sheet": "Summary Table"},
                    "cells": [{"coordinate": "B5", "formula": "='Detailed Table'!N5"}],
                },
            ],
        }
    )
    with pytest.raises(ValueError, match="Detailed booked charges do not reconcile"):
        v15_pathways._component_charges(workbook, "B5")
    monkeypatch.setattr(v15_pathways, "_detail_charges", lambda *_: [])
    with pytest.raises(ValueError, match="Summary component and detail disagree"):
        v15_pathways._component_charges(workbook, "B5")


@pytest.mark.parametrize(
    ("coordinate", "replacement", "error"),
    [
        (
            "B81",
            {"stored_type": "str", "stored_value": "untagged"},
            "numeric workbook value",
        ),
        (
            "B5",
            {"stored_type": "str", "stored_value": "unresolved"},
            "summary component at B5",
        ),
        (
            "B5",
            {"stored_type": "n", "stored_value": "20"},
            "booked charge reference at B5",
        ),
        (
            "K5",
            {"stored_type": "n", "stored_value": "4.9"},
            "overhead base differs at K5",
        ),
        (
            "N5",
            {"stored_type": "n", "stored_value": "28"},
            "workbook subtotal disagree at N5",
        ),
        (
            "N15",
            {"stored_type": "n", "stored_value": "28"},
            "pathway subtotal disagree at N15",
        ),
    ],
)
def test_pathway_validation_rejects_disagreement_at_each_ledger_level(
    monkeypatch, coordinate, replacement, error
):
    monkeypatch.setattr(v15_pathways, "WORKBOOK_SHA256", "synthetic")
    summary = {
        "B81": {"stored_type": "n", "stored_value": "0.7"},
        "B5": {"formula": "='Detailed Table'!N5"},
        "K5": {"stored_type": "n", "stored_value": "5.4"},
        "N5": {"stored_type": "n", "stored_value": "25.4"},
        "N15": {"stored_type": "n", "stored_value": "25.4"},
        **{
            f"{column}{row}": {"stored_type": "n", "stored_value": "0"}
            for row in range(6, 15)
            for column in ("K", "N")
        },
    }
    summary[coordinate] = replacement
    ledger = {
        "source_sha256": "synthetic",
        "sheets": [
            {
                "catalogue": {"sheet": "Summary Table"},
                "cells": [
                    {"coordinate": key, **fields} for key, fields in summary.items()
                ],
            },
            {
                "catalogue": {"sheet": "Detailed Table"},
                "cells": [
                    {"coordinate": "N5", "formula": "=20", "references": []},
                ],
            },
        ],
    }
    with pytest.raises(ValueError, match=error):
        v15_pathways.pathway_requests(ledger)


def test_native_pathways_require_the_expected_revision_and_reconcile_all_stages(
    monkeypatch,
):
    with pytest.raises(ValueError, match="original v15 workbook ledger"):
        v15_pathways.pathway_requests({"source_sha256": "different"})
    exact = {"numerator": "10", "denominator": "1"}
    changed = {"numerator": "9", "denominator": "1"}
    pathway = {
        "request": {},
        "expected_total": exact,
        "stages": {
            "x": {"lines": ["cost"], "exact": exact, "source": "Synthetic cell"}
        },
    }
    monkeypatch.setattr(
        v15_pathways,
        "pathway_requests",
        lambda _, **kwargs: {"pathways": {"x": pathway}},
    )
    report = {
        "status": "complete",
        "totals": {"exact": changed},
        "lines": [{"id": "cost", "exact": changed}],
    }
    monkeypatch.setattr(v15_pathways, "evaluate_native_request", lambda _: report)
    with pytest.raises(ValueError, match="original pathway"):
        v15_pathways.evaluate_pathways({})
    report["totals"]["exact"] = exact
    with pytest.raises(ValueError, match="reconcile at Synthetic cell"):
        v15_pathways.evaluate_pathways({})
    report["lines"][0]["exact"] = exact
    assert v15_pathways.evaluate_pathways({})["pathways"]["x"]["report"] == report


def test_adjustment_rate_requires_the_complete_set_before_editing():
    formula = "=SUM(1,2,3)*0.27"
    cells = [{"coordinate": "A1", "formula": formula}]
    ledger = {"sheets": [{"catalogue": {"sheet": "Synthetic"}, "cells": cells}]}
    with pytest.raises(ValueError, match="nonnegative exact decimal string"):
        v15_replay.apply_adjustment_rate(ledger, "-1")
    with pytest.raises(ValueError, match="Expected 2,927 adjustment formulas"):
        v15_replay.apply_adjustment_rate(ledger, "0.1375")
    assert cells[0]["formula"] == formula

    cells.extend(
        {"coordinate": f"A{row}", "formula": formula} for row in range(2, 2928)
    )
    cells.append({"coordinate": "B1", "formula": "=SUM(1,2)*0.27"})
    assert v15_replay.apply_adjustment_rate(ledger, "0.1375") == Fraction(11, 80)
    assert all(cell["formula"] == "=SUM(1,2,3)*0.1375" for cell in cells[:-1])
    assert cells[-1]["formula"] == "=SUM(1,2)*0.27"
    assert WorkbookReplay(ledger).value("Synthetic", "A1") == Fraction(33, 40)


def test_one_calculation_pattern_uses_each_sheet_and_each_literal():
    inputs = [
        {"coordinate": "A1", "stored_type": "n", "stored_value": "4"},
        {"coordinate": "B2", "stored_type": "n", "stored_value": "3"},
        {"coordinate": "C1", "formula": "=A1*1.25"},
        {"coordinate": "C2", "formula": "=B2*0.5"},
        {"coordinate": "C3", "formula": "=12/A1"},
        {"coordinate": "C4", "formula": "=A1/#REF!"},
    ]
    ledger = {
        "sheets": [
            {"catalogue": {"sheet": "First"}, "cells": inputs},
            {
                "catalogue": {"sheet": "Second"},
                "cells": [inputs[0] | {"stored_value": "8"}, *inputs[1:]],
            },
        ]
    }
    book = WorkbookReplay(ledger)
    assert book.value("First", "C1") == 5
    assert book.value("First", "C2") == Fraction(3, 2)
    assert book.value("First", "C3") == 3
    assert book.value("First", "C4") == CellError("#REF!")
    assert book.value("Second", "C1") == 10
    assert len(book._rules) == 1
    changed = WorkbookReplay(ledger, overrides={("First", "A1"): "2.8"})
    assert changed.value("First", "C1") == Fraction(7, 2)
    assert changed.value("Second", "C1") == 10


def test_rule_variations_keep_precedence_argument_order_and_error_handling():
    formulas = (
        "=SUM(2,4)",
        "=AVERAGE(2,4)",
        "=PMT(2,4)",
        "=12/3*2",
        "=12/(3*2)",
        "=1+3*2",
        "=1*3+2",
        "=#REF!+#DIV/0!",
        "=#DIV/0!+#REF!",
        "=" + "+".join(["1"] * 1100),
    )
    book = WorkbookReplay(
        {
            "sheets": [
                {
                    "catalogue": {"sheet": "Cases"},
                    "cells": [
                        {"coordinate": f"A{i}", "formula": formula}
                        for i, formula in enumerate(formulas, 1)
                    ],
                }
            ]
        }
    )
    assert book.value("Cases", "A1") == 6
    assert book.value("Cases", "A2") == 3
    with pytest.raises(ValueError, match="Unsupported v15 function: PMT"):
        book.value("Cases", "A3")
    assert len(book._rules) == 1
    assert [book.value("Cases", f"A{i}") for i in range(4, 11)] == [
        8,
        2,
        7,
        5,
        CellError("#REF!"),
        CellError("#DIV/0!"),
        1100,
    ]


def test_shared_calculations_bind_ordered_sources_per_replay(monkeypatch):
    calls = Counter()
    compute = v15_replay._compute

    def count(operation, operands):
        calls[operation] += 1
        return compute(operation, operands)

    monkeypatch.setattr(v15_replay, "_compute", count)
    inputs = [
        {"coordinate": f"A{row}", "stored_type": "n", "stored_value": value}
        for row, value in enumerate(("12", "2", "6"), 1)
    ]
    formulas = {
        "B1": "=SUM(A1,A2,A3)*0.1",
        "B2": "=SUM($A$1,$A$2,$A$3,B1)",
        "B3": "=A1/A2",
        "B4": "=(A1/A2)*3",
        "B5": "=PMT(10%,2,-(A1/A2))",
        "B6": "=PMT(10%,2,-(A1/A2))",
        "B7": "=A2",
        "C1": "=SUM(A1,#REF!,A3,#DIV/0!)",
        "C2": "=SUM(A1,#DIV/0!,A3,#REF!)",
    }
    ledger = {
        "sheets": [
            {
                "catalogue": {"sheet": "Costs"},
                "cells": [
                    *inputs,
                    *(
                        {"coordinate": address, "formula": formula}
                        for address, formula in formulas.items()
                    ),
                ],
            },
            {
                "catalogue": {"sheet": "Other"},
                "cells": [
                    *inputs,
                    {"coordinate": "B1", "formula": "=('Costs'!$A$1/Costs!A2)*4"},
                    {"coordinate": "B2", "formula": "=A1/A2"},
                ],
            },
        ],
    }
    book = WorkbookReplay(ledger)
    assert [book.value("Costs", f"B{row}") for row in range(1, 8)] == [
        2,
        22,
        6,
        18,
        Fraction(121, 35),
        Fraction(121, 35),
        2,
    ]
    assert (calls["SUM"], calls["/"], calls["PMT"]) == (2, 1, 1)
    assert book.value("Other", "B1") == 24 and calls["/"] == 1
    assert book.value("Other", "B2") == 6 and calls["/"] == 2
    assert book.value("Costs", "C1") == CellError("#REF!")
    assert book.value("Costs", "C2") == CellError("#DIV/0!")

    changed = WorkbookReplay(ledger, overrides={("Costs", "A2"): "0"})
    assert changed.value("Costs", "B2") == Fraction(99, 5)
    assert changed.value("Costs", "B5") == CellError("#DIV/0!")
    assert changed.value("Costs", "B7") == 0
    assert changed.value("Other", "B2") == 6
