#!/usr/bin/env python3
# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Transfer cached workbook tables and verify both compatibility exports."""

import argparse
import json
import sys
from hashlib import sha256
from pathlib import Path

from dapane_genomics.legacy_workbooks import csv_ready
from genomics_microcosting.data_manager import DataManager
from genomics_microcosting.sheet_manager import SheetManager

TRANSFER_TEST = '''# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Verify that the transferred workbook tables match their frozen receipt."""

import json
from hashlib import sha256
from pathlib import Path


def test_transferred_workbook_tables():
    directory = Path(__file__).resolve().parent
    receipt = json.loads((directory / "table-transfer.json").read_bytes())
    assert receipt["tables"], "Expected at least one transferred worksheet"
    for table in receipt["tables"]:
        for name, expected in table["exports"].items():
            payload = (directory / "prepared" / name).read_bytes()
            assert sha256(payload).hexdigest() == expected, name
'''


def main() -> int:
    """Verify selected tables after saving them in both local formats."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--sheet", action="append")
    parser.add_argument(
        "--emit-test",
        action="store_true",
        help="Write a portable verification test beside the receipt",
    )
    args = parser.parse_args()
    sheets = SheetManager(args.workbook)
    try:
        manager = DataManager(args.data_dir)
        selected = args.sheet or sheets.get_sheet_names()
        if not selected or len(set(selected)) != len(selected):
            raise ValueError("Expected one or more distinct source worksheets")
        records = []
        filenames = [manager.sanitize_sheet_name(name) for name in selected]
        if len(set(filenames)) != len(filenames):
            raise ValueError(
                "Selected worksheet names produce duplicate export filenames"
            )
        for name, stem in zip(selected, filenames, strict=True):
            frame = csv_ready(sheets.get_ground_truth(name))
            if frame.is_empty() or not manager.save_sheet_polars(name, frame):
                raise ValueError(f"{name}: no rows or export failed")
            parquet = manager.load_sheet_polars(name)
            table = manager.load_sheet_polars(
                name, "csv", csv_schema=dict(frame.schema)
            )
            if (
                parquet is None
                or table is None
                or not frame.equals(parquet)
                or not frame.equals(table)
            ):
                raise ValueError(f"{name}: readback differs from its source")
            records.append(
                {
                    "sheet": name,
                    "rows": frame.height,
                    "columns": frame.width,
                    "exports": {
                        filename: sha256(
                            (manager.prepared_dir / filename).read_bytes()
                        ).hexdigest()
                        for filename in (f"{stem}.csv", f"{stem}.parquet")
                    },
                }
            )
        output = {
            "source_sha256": sha256(sheets.excel_file_path.read_bytes()).hexdigest(),
            "tables": records,
        }
        (args.data_dir / "table-transfer.json").write_text(
            json.dumps(output, indent=2) + "\n", encoding="utf-8"
        )
        if args.emit_test:
            (args.data_dir / "test_table_transfer.py").write_text(
                TRANSFER_TEST, encoding="utf-8"
            )
    finally:
        sheets.close()
    sys.stdout.write(f"Verified {len(records)} CSV and Parquet table round trips\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
