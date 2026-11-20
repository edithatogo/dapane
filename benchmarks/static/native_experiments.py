"""Run the installed providers and persist full synthetic experiment inputs and outputs."""

from __future__ import annotations

import argparse
import copy
import gzip
import json
import platform
import subprocess
import sys
from hashlib import file_digest, sha256
from pathlib import Path

from . import native_pathway
from .decision_slice import _ADAPTER, d1_fixture, d2_voiage, packet, protocol, voiage_packet

sys.path.insert(0, str(_ADAPTER))
from bridge import innovate_adoption_capacity_native  # noqa: E402
from native_voiage import run_evpi  # noqa: E402
from study import canonical_digest, prepare_evidence_question, verify_native_evpi_receipt  # noqa: E402
from test_innovate_prediction import FIXTURE, scenario  # noqa: E402

VOIAGE_REVISION = "0978497b5047de9459ed2fca9b349a4e2a9c45d3"
WHEEL = "sha256:71d3c657b876e5fd7b207f473c6b41583a451d51361919b0d6e766d604baa140"


def digest(path):
    with path.open("rb") as stream:
        return "sha256:" + file_digest(stream, "sha256").hexdigest()


def decision(wheel, innovate, fiscal):
    import numpy as np
    from voiage._runtime import compute_evpi

    declared = packet()
    declared["provider"].update(revision=VOIAGE_REVISION, artifact_digest=WHEEL)
    declared["output_digest"] = canonical_digest(
        "dapane:d2-voiage:0.1\n", {k: v for k, v in declared.items() if k != "output_digest"}
    )
    question = prepare_evidence_question(declared, protocol())
    staff = run_evpi(question, wheel, WHEEL, expected_revision=VOIAGE_REVISION)
    verify_native_evpi_receipt(
        question, staff, expected_wheel=WHEEL, expected_extension=staff["native_extension_digest"]
    )
    paired = d1_fixture()
    companion = d2_voiage(paired)
    companion["provider"].update(revision=VOIAGE_REVISION, artifact_digest=WHEEL)
    comparison = voiage_packet(json.dumps(paired), paired["output_digest"], companion)
    control = compute_evpi(np.asarray(comparison["value_array"]["net_benefit"], dtype=np.float64))
    base = scenario()
    base["provider"]["artifact_digest"] = digest(innovate)
    first = innovate_adoption_capacity_native(base, str(innovate))
    fiscal_input = json.loads(FIXTURE.read_bytes())
    valuation = native_pathway.call([fiscal, "evaluate"], fiscal_input)
    second = copy.deepcopy(base)
    second.update(
        iteration=1,
        previous_evaluation_digest=first["output_digest"],
        feedback={
            "price_affects_adoption": True,
            "mode": "external_recomputed",
            "valuation_digest": valuation["output_digest"],
        },
    )
    second["model"]["p"]["numerator"] = "1"
    revised = innovate_adoption_capacity_native(
        second, str(innovate), previous_evaluation=first, valuation=valuation
    )
    trips = [
        [r["period"] for r in receipt["periods"] if r["capacity_exceeded"]]
        for receipt in (first, revised)
    ]
    if (staff["evpi_per_assay"], control, trips) != (10.0, 1.0, [["2026-01", "2026-02"], []]):
        raise ValueError(
            "native outputs differ from the pre-specified study and capacity expectations"
        )
    summary = {
        "unit": "AUD per synthetic assay at 2026 prices",
        "staff_time_evpi": staff["evpi_per_assay"],
        "control_evpi": control,
        "measurement_priority": "staff_time_per_assay",
        "capacity_exceeded": trips,
    }
    return summary, {
        "staff_packet": declared,
        "study_protocol": protocol(),
        "staff_prepared": question,
        "staff_receipt": staff,
        "comparison_input": paired,
        "comparison_valuation": companion,
        "comparison_packet": comparison,
        "comparison_evpi": control,
        "initial_request": base,
        "initial_forecast": first,
        "fiscal_input": fiscal_input,
        "fiscal_report": valuation,
        "revised_request": second,
        "revised_forecast": revised,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("cli", "process-cli", "fiscal", "innovate", "wheel", "out"):
        parser.add_argument("--" + arg, required=True, type=Path)
    args = parser.parse_args()
    evidence = {}
    pathway = native_pathway.run(args.cli, args.process_cli, evidence)
    outcome, decisions = decision(args.wheel, args.innovate, args.fiscal)
    full = {"pathway": evidence, "decisions": decisions}
    raw = json.dumps(
        full, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode()
    zipped = gzip.compress(raw, mtime=0)
    summary = {
        "qualification": "synthetic",
        "python": platform.python_version(),
        "system": platform.system(),
        "architecture": platform.machine(),
        "rust": subprocess.check_output(["rustc", "--version"], text=True).strip(),
        "binary_sha256": {
            name: digest(getattr(args, name))
            for name in ("cli", "process_cli", "fiscal", "innovate", "wheel")
        },
        "bundle": "native-experiments.json.gz",
        "bundle_sha256": sha256(zipped).hexdigest(),
        "pathway": pathway,
        "decision": outcome,
    }
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / summary["bundle"]).write_bytes(zipped)
    (args.out / "native-experiments.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    )


if __name__ == "__main__":
    main()
