#!/usr/bin/env python3
# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Export all installed model templates and a field reference."""

import argparse
import json
import sys
from pathlib import Path

from dapane_genomics.model_tables import MODELS, LabProfile, model_template_bytes


def main() -> int:
    """Export maintained templates with optional lab-specific settings."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("config/templates"))
    parser.add_argument(
        "--documentation", type=Path, default=Path("docs/standardized_templates.md")
    )
    parser.add_argument("--profile", type=Path)
    options = parser.parse_args()
    profile = (
        LabProfile.model_validate_json(options.profile.read_bytes())
        if options.profile
        else None
    )
    options.output_dir.mkdir(parents=True, exist_ok=True)
    docs = ["# Model templates", ""]
    for model in MODELS:
        template = model_template_bytes(model, "json", profile)
        (options.output_dir / f"{model}_template.json").write_bytes(template)
        parsed = json.loads(template)
        required = ", ".join(parsed["required_columns"])
        docs.extend([f"## {model}", "", f"Required fields are {required}.", ""])
    (options.output_dir / "template_examples.csv").write_bytes(
        model_template_bytes("base", "csv", profile)
    )
    options.documentation.parent.mkdir(parents=True, exist_ok=True)
    options.documentation.write_text("\n".join(docs), encoding="utf-8")
    sys.stdout.write(f"Generated {len(MODELS)} templates\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
