#!/usr/bin/env python3
# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Model Consistency Analysis Script.

This script analyzes the consistency of categories and subcategories across
the five genomic testing models to establish a baseline for standardization.

Models analyzed:
- Panel (Targeted gene panel testing)
- WES (P) (Whole Exome Sequencing - Proband)
- WES (T) (Whole Exome Sequencing - Trio)
- WGS (Whole Genome Sequencing - Singleton)
- WGS (T) (Whole Genome Sequencing - Trio)
"""

import argparse
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import polars as pl

from dapane_genomics.legacy_models import model_rows, read_model_source

HIGH_CONSISTENCY = 0.8
MODERATE_CONSISTENCY = 0.5


@dataclass
class ModelAnalysis:
    """Container for model analysis results."""

    name: str
    categories: set[str]
    subcategories: dict[str, set[str]]
    total_rows: int
    unique_combinations: int


class ModelConsistencyAnalyzer:
    """Analyzes consistency across genomic testing models."""

    def __init__(self, data_path: str = "data/Detailed Table.csv") -> None:
        """Select the detailed table for consistency checks."""
        self.data_path = Path(data_path)
        self.models = [
            "Panel",
            "WES (P)",  # Whole Exome Sequencing - Proband
            "WES (T)",  # Whole Exome Sequencing - Trio
            "WGS",  # Whole Genome Sequencing - Singleton
            "WGS (T)",  # Whole Genome Sequencing - Trio
        ]

    def load_data(self) -> pl.DataFrame:
        """Load the detailed table data."""
        return read_model_source(self.data_path)

    def extract_model_data(self, df: pl.DataFrame) -> dict[str, pl.DataFrame]:
        """Extract data for each model."""
        grouped = model_rows(df).group_by("Test", maintain_order=True)
        return {name: frame for (name,), frame in grouped}

    def analyze_model_categories(self, model_df: pl.DataFrame) -> ModelAnalysis:
        """Analyze categories and subcategories for a single model."""
        # Get unique categories
        categories = set(model_df["Category"].drop_nulls().unique())

        # Get subcategories by category
        subcategories = defaultdict(set)
        for row in model_df.iter_rows(named=True):
            category = row["Category"]
            subcategory = row["Sub-Category"]
            if category is not None and subcategory is not None:
                subcategories[category].add(subcategory)

        # Calculate metrics
        total_rows = len(model_df)
        unique_combinations = (
            model_df.select("Category", "Sub-Category").drop_nulls().unique().height
        )

        return ModelAnalysis(
            name=model_df["Test"][0] if not model_df.is_empty() else "Unknown",
            categories=categories,
            subcategories=dict(subcategories),
            total_rows=total_rows,
            unique_combinations=unique_combinations,
        )

    def analyze_all_models(self) -> dict[str, ModelAnalysis]:
        """Analyze all models and return results."""
        df = self.load_data()
        model_data = self.extract_model_data(df)

        results = {}
        for model_name, model_df in model_data.items():
            results[model_name] = self.analyze_model_categories(model_df)

        return results

    def calculate_consistency_metrics(self, analyses: dict[str, ModelAnalysis]) -> dict:
        """Calculate consistency metrics across all models."""
        if not analyses:
            return {}

        # Get all unique categories across models
        all_categories = set()
        for analysis in analyses.values():
            all_categories.update(analysis.categories)

        # Calculate category overlap
        category_counts = Counter()
        for analysis in analyses.values():
            for category in analysis.categories:
                category_counts[category] += 1

        # Calculate subcategory consistency
        subcategory_consistency = {}
        for category in all_categories:
            models_with_category = [
                analysis
                for analysis in analyses.values()
                if category in analysis.categories
            ]

            if len(models_with_category) > 1:
                # Get all subcategories for this category across models
                all_subcats = set()
                for analysis in models_with_category:
                    all_subcats.update(analysis.subcategories.get(category, set()))

                # Calculate overlap
                subcat_counts = Counter()
                for analysis in models_with_category:
                    for subcat in analysis.subcategories.get(category, set()):
                        subcat_counts[subcat] += 1

                max_models = len(models_with_category)
                common_subcats = sum(
                    1 for count in subcat_counts.values() if count == max_models
                )
                total_subcats = len(subcat_counts)

                subcategory_consistency[category] = {
                    "total_subcategories": total_subcats,
                    "common_subcategories": common_subcats,
                    "consistency_ratio": common_subcats / total_subcats
                    if total_subcats > 0
                    else 0,
                    "models_with_category": len(models_with_category),
                }

        return {
            "total_categories": len(all_categories),
            "categories_by_model": {
                name: len(analysis.categories) for name, analysis in analyses.items()
            },
            "category_overlap": dict(category_counts),
            "subcategory_consistency": subcategory_consistency,
            "model_count": len(analyses),
        }

    def _append_model_breakdown(
        self,
        report: list[str],
        analyses: dict[str, ModelAnalysis],
    ) -> None:
        # Model breakdown
        report.append("## Model Breakdown")
        for name, analysis in analyses.items():
            report.append(f"### {name}")
            report.append(f"- **Total Rows**: {analysis.total_rows}")
            report.append(f"- **Categories**: {len(analysis.categories)}")
            report.append(
                (
                    "- **Unique Category-Subcategory Combinations**: "
                    f"{analysis.unique_combinations}"
                ),
            )
            report.append(f"- **Categories**: {', '.join(sorted(analysis.categories))}")
            report.append("")

            if analysis.subcategories:
                report.append("**Subcategories by Category:**")
                for category, subcats in sorted(analysis.subcategories.items()):
                    report.append(f"  - **{category}**: {', '.join(sorted(subcats))}")
                report.append("")

    def generate_report(self, analyses: dict[str, ModelAnalysis], metrics: dict) -> str:
        """Generate a comprehensive analysis report."""
        report = []
        report.append("# Model Consistency Analysis Report")
        report.append(f"Generated: {datetime.now(UTC).isoformat()}")
        report.append("")

        # Summary section
        report.append("## Summary")
        report.append(f"- **Models Analyzed**: {len(analyses)}")
        report.append(f"- **Total Categories**: {metrics.get('total_categories', 0)}")
        report.append("")

        self._append_model_breakdown(report, analyses)

        # Consistency analysis
        report.append("## Consistency Analysis")
        report.append("### Category Overlap")
        for category, count in sorted(metrics.get("category_overlap", {}).items()):
            report.append(
                f"- {category}: {count} models ("
                f"{(count / len(analyses) * 100 if analyses else 0):.1f}%)",
            )
        report.append("")

        # Subcategory consistency
        if metrics.get("subcategory_consistency"):
            report.append("### Subcategory Consistency")
            for category, data in sorted(metrics["subcategory_consistency"].items()):
                report.append(f"**{category}**:")
                report.append(
                    f"  - Models with category: {data['models_with_category']}",
                )
                report.append(f"  - Total subcategories: {data['total_subcategories']}")
                report.append(
                    f"  - Common subcategories: {data['common_subcategories']}",
                )
                report.append(
                    f"  - Consistency: {data['consistency_ratio'] * 100:.1f}%",
                )
                report.append("")

        # Recommendations
        report.append("## Recommendations for Standardization")
        report.append("### High Priority Categories (>80% consistency)")
        high_priority = [
            cat
            for cat, data in metrics.get("subcategory_consistency", {}).items()
            if data["consistency_ratio"] >= HIGH_CONSISTENCY
        ]
        if high_priority:
            report.extend(f"- {category}" for category in sorted(high_priority))
        else:
            report.append("- No categories with >80% consistency found")
        report.append("")

        report.append("### Medium Priority Categories (50-80% consistency)")
        medium_priority = [
            cat
            for cat, data in metrics.get("subcategory_consistency", {}).items()
            if MODERATE_CONSISTENCY <= data["consistency_ratio"] < HIGH_CONSISTENCY
        ]
        if medium_priority:
            report.extend(f"- {category}" for category in sorted(medium_priority))
        else:
            report.append("- No categories with 50-80% consistency found")
        report.append("")

        report.append("### Low Priority Categories (<50% consistency)")
        low_priority = [
            cat
            for cat, data in metrics.get("subcategory_consistency", {}).items()
            if data["consistency_ratio"] < MODERATE_CONSISTENCY
        ]
        if low_priority:
            report.extend(f"- {category}" for category in sorted(low_priority))
        else:
            report.append("- No categories with <50% consistency found")
        report.append("")

        return "\n".join(report)

    def save_report(
        self,
        report: str,
        output_path: str = "docs/model_standardization.md",
    ) -> None:
        """Save the analysis report to a file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with Path(output_file).open("w", encoding="utf-8") as f:
            f.write(report)

        sys.stdout.write(f"Report saved to: {output_file}" + "\n")


def main() -> int:
    """Write a reproducible cross-model consistency report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="data/Detailed Table.csv")
    parser.add_argument("--report", default="docs/model_standardization.md")
    args = parser.parse_args()
    analyzer = ModelConsistencyAnalyzer(args.source)
    analyses = analyzer.analyze_all_models()
    metrics = analyzer.calculate_consistency_metrics(analyses)
    analyzer.save_report(analyzer.generate_report(analyses, metrics), args.report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
