"""Exercise both installed packages from outside the repository source directory."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import sys
from pathlib import Path

import dapane
import dapane_mchs_atlas


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", required=True, type=Path)
    args = parser.parse_args()
    for module in (dapane, dapane_mchs_atlas):
        assert Path(module.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()), module
    bundle = dapane_mchs_atlas.loads(args.fixture.read_text(encoding="utf-8"))
    result = dapane_mchs_atlas.evaluate(bundle)
    assert result["views"]["funding"]["totals"]["rounded"] == "42.50"
    assert result["views"]["tariff"]["totals"]["rounded"] == "50.00"
    assert result["views"]["resource_cost"]["totals"]["rounded"] == "15.00"
    assert result["views"]["payment"]["records"][0]["amount"] == "40.00"
    invalid = json.loads(args.fixture.read_text())
    invalid["resource_cost"]["usage"][0]["quantity"] = {"numerator": "1", "denominator": "0"}
    try:
        dapane_mchs_atlas.evaluate(invalid)
    except dapane_mchs_atlas.AdapterError as error:
        assert error.path.startswith("/requests/resource_cost/"), error
    else:
        raise AssertionError("Invalid native input must not return a complete result.")
    print(json.dumps({
        "status": "passed",
        "python": sys.version.split()[0],
        "adapter": importlib.metadata.version("dapane-mchs-atlas"),
        "native": dapane.__version__,
        "adapter_path": dapane_mchs_atlas.__file__,
        "native_path": dapane.__file__,
    }, indent=2))


if __name__ == "__main__":
    main()
