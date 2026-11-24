# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Compatibility entry point for the installed native report generator."""

from dapane_genomics.reporting import (
    create_cost_analysis_plots,
    generate_html_report,
    generate_json_report,
    generate_markdown_report,
    generate_pdf_report,
    main,
)

__all__ = [
    "create_cost_analysis_plots",
    "generate_html_report",
    "generate_json_report",
    "generate_markdown_report",
    "generate_pdf_report",
    "main",
]

if __name__ == "__main__":
    raise SystemExit(main())
