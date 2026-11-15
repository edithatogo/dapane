"""Export synthetic run-bundle reporting evidence using explicit local source snapshots."""

import argparse
import json
import sys
from pathlib import Path

from .transport import ReportingError, canonical, read_json


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("history", type=Path)
    parser.add_argument("declarations", type=Path)
    parser.add_argument("--uogto", required=True, type=Path, help="local exact UOGTO snapshot")
    parser.add_argument("--standards-check", required=True, type=Path, help="local exact catalogue")
    parser.add_argument("--head", required=True, help="independently retained history head digest")
    parser.add_argument("--as-of", required=True, help="YYYY-MM-DD knowledge date")
    args = parser.parse_args()
    try:
        from scripts.verify_run_bundle import BundleError, read_history

        from .catalogue import load_catalogue
        from .evidence import export_evidence
    except ImportError:
        print(
            json.dumps(
                {
                    "error": {
                        "code": "reporting_dependencies_unavailable",
                        "path": "/",
                        "message": "install optional reporting requirements and matching Dapane wheel",
                    }
                }
            ),
            file=sys.stderr,
        )
        return 2
    try:
        catalogue = load_catalogue(args.uogto, args.standards_check)
        result = export_evidence(
            read_history(args.history),
            read_json(args.declarations),
            catalogue,
            expected_head_digest=args.head,
            as_of=args.as_of,
        )
    except (ReportingError, BundleError) as exc:
        print(
            json.dumps({"error": {"code": exc.code, "path": exc.path, "message": exc.message}}),
            file=sys.stderr,
        )
        return 2
    print(canonical(result).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
