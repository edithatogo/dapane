#!/usr/bin/env python3
# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Check installed dashboard markup and assets from a local consumer directory."""

import argparse
from pathlib import Path

from genomics_microcosting.web import create_app


def main() -> int:
    """Check the home page, model wizard and its packaged client code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path)
    args = parser.parse_args()
    app = create_app(args.data_dir)
    expected = {
        "/": b"Available Data Tables",
        "/models": b"model_templates.js",
        "/static/model_templates.js": b"addEventListener",
    }
    with app.test_client() as client:
        for route, marker in expected.items():
            response = client.get(route)
            if response.status_code != 200 or marker not in response.data:
                parser.error(f"Installed dashboard smoke check failed at {route}")
    parser.exit(0, "Installed home page, model wizard and bundled asset passed.\n")


if __name__ == "__main__":
    raise SystemExit(main())
