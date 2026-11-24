# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Replicates the calculations from the 'BI - Comp+Stor Costs - VCGS' sheet."""

import sys
from pathlib import Path

import polars as pl


def replicate_bi_comp_stor_costs() -> None:
    """Replicates the calculations from the 'BI - Comp+Stor Costs - VCGS' sheet."""
    # Define the data as a dictionary of lists, similar to the Excel sheet
    server_data = {
        "Description": [
            "PowerEdge R760 Server",
            "Xenon NItro GPU Server, 2U, X12, A30 GPU",
        ],
        "CPUs": [2, 2],
        "Cores/CPU": [16, 16],
        "Threads/CPU": [32, 32],
        "Memory": [1024, 1024],
        "ex-GST": [54321.28, 49380.00],
    }

    # Create a DataFrame for server costs
    df_server = pl.DataFrame(server_data)

    # --- Server Cost Calculations ---
    df_server = df_server.with_columns(
        (pl.col("CPUs") * pl.col("Cores/CPU")).alias("Total Cores")
    )
    df_server = df_server.with_columns(
        (pl.col("CPUs") * pl.col("Threads/CPU")).alias("Total Threads")
    )
    df_server = df_server.with_columns((pl.col("ex-GST") * 1.1).alias("inc. GST"))
    df_server = df_server.with_columns((pl.col("ex-GST") / 3).alias("3-yr"))
    df_server = df_server.with_columns((pl.col("ex-GST") / 5).alias("5-yr"))
    df_server = df_server.with_columns(
        (pl.col("ex-GST") / pl.col("CPUs")).alias("Cost/CPU")
    )
    df_server = df_server.with_columns(
        (pl.col("ex-GST") / pl.col("Total Cores")).alias("Cost/Core")
    )
    df_server = df_server.with_columns(
        (pl.col("inc. GST") / pl.col("Total Threads")).alias("Cost/Thread")
    )
    df_server = df_server.with_columns(
        (pl.col("ex-GST") / pl.col("Memory")).alias("Cost/GB")
    )

    ul_total_hours = 5 * 365 * 24
    ll_total_hours = ul_total_hours * 0.7

    df_server = df_server.with_columns((pl.lit(ul_total_hours)).alias("UL Total Hours"))
    df_server = df_server.with_columns((pl.lit(ll_total_hours)).alias("LL Total Hours"))

    df_server = df_server.with_columns(
        (pl.col("Cost/CPU") / pl.col("LL Total Hours")).alias("Cost/CPU/hr - 70%")
    )
    df_server = df_server.with_columns(
        (pl.col("Cost/Core") / pl.col("LL Total Hours")).alias("Cost/Core/hr - 70%")
    )
    df_server = df_server.with_columns(
        (pl.col("Cost/Thread") / pl.col("LL Total Hours")).alias("Cost/thread/hr - 70%")
    )
    df_server = df_server.with_columns(
        (pl.col("Cost/GB") / pl.col("LL Total Hours")).alias("cost/gb/hr - 70%")
    )
    df_server = df_server.with_columns(
        (pl.col("Cost/CPU") / pl.col("UL Total Hours")).alias("Cost/CPU/hr - 100%")
    )
    df_server = df_server.with_columns(
        (pl.col("Cost/Core") / pl.col("UL Total Hours")).alias("Cost/Core/hr - 100%")
    )
    df_server = df_server.with_columns(
        (pl.col("Cost/Thread") / pl.col("UL Total Hours")).alias(
            "Cost/thread/hr - 100%"
        )
    )
    df_server = df_server.with_columns(
        (pl.col("Cost/GB") / pl.col("UL Total Hours")).alias("cost/gb/hr - 100%")
    )

    # --- Equipment Cost Calculations ---
    equipment_data = {
        "Equipment": ["Dragan Hardware", "Dragan Software"],
        "List Price (AUD)": [40165, 21450],
        "Useful Life": [5, 1],
        "WES/Panel": ["n", "n"],
        "WGS": ["y", "y"],
        "Initial Estimate": [2000, 2000],
        "Max": [50000, 50000],
    }
    df_equipment = pl.DataFrame(equipment_data)
    df_equipment = df_equipment.with_columns(
        (pl.col("List Price (AUD)") / pl.col("Useful Life")).alias("Annualised cost")
    )
    df_equipment = df_equipment.with_columns(
        (pl.col("Max") * 0.7).alias("Actual (0.7)")
    )
    df_equipment = df_equipment.with_columns(
        (pl.col("Annualised cost") / pl.col("Initial Estimate")).alias(
            "Unit Cost ($/sample) - Initial"
        )
    )
    df_equipment = df_equipment.with_columns(
        (pl.col("Annualised cost") / pl.col("Actual (0.7)")).alias(
            "Unit Cost ($/sample) - Actual (0.7)"
        )
    )
    df_equipment = df_equipment.with_columns(
        (pl.col("Annualised cost") / pl.col("Max")).alias("Unit Cost ($/sample) - Max")
    )

    # --- Storage Cost Calculations ---
    storage_data = {
        "Description": [
            "2U R-Series with integrateed controller (96TB, 50.8 TB Useable in RAID-6)",
            "LTO-7 or LTO-8 Tape Drive Module",
            "LTO 7 Tape (uncompressed)",
            "LTO 8 Tape (uncompressed)",
        ],
        "Total Space (GB)": [50800, None, 6000, 12000],
        "ex-GST": [23800, 21000, 75, 115],
        "Useable life (years)": [5, 5, 5, 5],
    }
    df_storage = pl.DataFrame(storage_data)
    df_storage = df_storage.with_columns(
        (pl.col("ex-GST") / pl.col("Total Space (GB)")).alias("Cost/GB")
    )
    df_storage = df_storage.with_columns(
        (pl.col("Cost/GB") / pl.col("Useable life (years)")).alias("Cost/GB/year")
    )

    # Special case for 'LTO-7 or LTO-8 Tape Drive Module'
    lto_module_cost = 21000 / 5 / 20000
    df_storage = df_storage.with_columns(
        pl.Series("Cost/test", [None, lto_module_cost, None, None], dtype=pl.Float64)
    )

    # --- Save outputs ---
    output_dir = Path("data/replicated")
    output_dir.mkdir(parents=True, exist_ok=True)
    df_server.write_csv(output_dir / "server_costs.csv")
    df_equipment.write_csv(output_dir / "equipment_costs.csv")
    df_storage.write_csv(output_dir / "storage_costs.csv")

    sys.stdout.write(
        "Replicated BI Comp+Stor Costs and saved to data/replicated/" + "\n",
    )


if __name__ == "__main__":
    replicate_bi_comp_stor_costs()
