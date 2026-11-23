"""Replay the CMS aggregate funding transport and held-out calibration benchmarks."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from fractions import Fraction
from pathlib import Path

DATASET = "2941ab09-8cee-49d8-9703-f3c5b854e388"
ENDPOINT = (
    f"https://data.cms.gov/data-api/v1/dataset/{DATASET}/data?size=200&filter%5BDRG_Cd%5D=470"
)
PIN = "73019bb07a322643b09859d1239f038a777c525a9953d91e0931f24e7138b8a7"
STATES = frozenset(
    "01 02 04 05 06 08 09 10 11 12 13 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 "
    "30 31 32 33 34 35 36 37 38 39 40 41 42 44 45 46 47 48 49 50 51 53 54 55 56".split()
)
AS_OF = "2026-11-20"


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def rows_from(raw: bytes) -> tuple[dict[str, tuple[str, str]], dict[str, list[str]]]:
    if digest(raw) != PIN:
        raise ValueError("CMS response differs from the preregistered input edition")
    rows = {}
    excluded = {}
    seen = set()
    for row in json.loads(raw):
        if row["DRG_Cd"] != "470":
            raise ValueError("CMS response contains rows outside the selected DRG")
        level, state = row["Rndrng_Prvdr_Geo_Lvl"], row["Rndrng_Prvdr_Geo_Cd"]
        if (level, state) == ("National", ""):
            key = "national"
        elif level == "State" and state in STATES:
            key = state
        else:
            continue
        if key in seen:
            raise ValueError("CMS response contains a duplicate geography")
        seen.add(key)
        amount, count = row.get("Avg_Mdcr_Pymt_Amt"), row.get("Tot_Dschrgs")
        missing = []
        if not isinstance(amount, str) or not re.fullmatch(
            r"[0-9]{1,60}(?:\.[0-9]{1,36})?", amount
        ):
            missing.append("mean_medicare_payment")
        if not isinstance(count, str) or not re.fullmatch(r"[1-9][0-9]{0,11}", count):
            missing.append("discharges")
        if missing:
            excluded[key] = missing
        else:
            rows[key] = (count, amount)
    if "national" not in rows:
        raise ValueError("published national rate is unusable")
    return rows, excluded


def source(key: str, evidence: str) -> dict:
    return {
        "id": f"cms-2024-drg470-{key}",
        "version": PIN,
        "evidence": evidence,
        "access": "public",
        "validation": "unvalidated",
        "content_digest": f"sha256:{PIN}",
        "locator": ENDPOINT,
    }


def request(rows: dict[str, tuple[str, str]], pooled: bool) -> dict:
    quotes = []
    uses = []
    for key, (count, local_amount) in sorted(rows.items()):
        if key == "national":
            continue
        geo = "national" if pooled else key
        quotes.append(
            {
                "id": f"rate-{key}",
                "kind": "activity_measure",
                "target": f"drg470-{key}",
                "unit": "discharge",
                "amount": rows["national"][1] if pooled else local_amount,
                "per_quantity": "1",
                "currency": "USD",
                "price_year": 2024,
                "basis": "funding",
                "components": ["medicare-payment"],
                "valid_from": "2024-01-01",
                "valid_to": "2025-01-01",
                "known_from": AS_OF,
                "source": source(geo, "derived"),
            }
        )
        uses.append(
            {
                "id": f"state-{key}",
                "use_id": f"state-{key}",
                "kind": "activity_measure",
                "target": f"drg470-{key}",
                "unit": "discharge",
                "quantity": count,
                "service_date": "2024-12-31",
                "quote_id": f"rate-{key}",
                "source": source(key, "observed"),
            }
        )
    return {
        "schema_version": "0.1",
        "run_id": "cms-national-rate-transfer" if pooled else "cms-state-rate-reconstruction",
        "knowledge_cutoff": AS_OF,
        "policy": {
            "id": "cms-medicare-payment-reconstruction",
            "version": "1",
            "currency": "USD",
            "price_year": 2024,
            "perspective": "medicare-payer",
            "basis": "funding",
            "rounding": {"scale": 2, "mode": "half_even"},
        },
        "quotes": quotes,
        "usage": uses,
    }


def verify_valuation(cli: Path, mapped: dict, expected: dict[str, int]) -> str:
    payload = json.dumps(mapped, sort_keys=True, separators=(",", ":")).encode()
    output = subprocess.run(
        [cli, "evaluate", "-"], input=payload, check=True, capture_output=True, timeout=30
    ).stdout
    report = json.loads(output)
    actual = {row["id"]: Fraction(row["rounded"]) * 100 for row in report["lines"]}
    if (
        report["status"] != "complete"
        or len(report["lines"]) != len(expected)
        or expected != actual
    ):
        raise ValueError("native state amounts differ from the independent exact oracle")
    if Fraction(report["totals"]["rounded"]) * 100 != sum(expected.values()):
        raise ValueError("native total differs from the sum of independent rounded state amounts")
    return digest(output)


def check(cli: Path, rows: dict[str, tuple[str, str]], pooled: bool) -> tuple[dict[str, int], str]:
    expected = {
        f"state-{key}": round(
            Fraction(count) * Fraction(rows["national"][1] if pooled else amount) * 100
        )
        for key, (count, amount) in rows.items()
        if key != "national"
    }
    return expected, verify_valuation(cli, request(rows, pooled), expected)


def transport(cli: Path, rows: dict[str, tuple[str, str]]) -> dict:
    local, local_report = check(cli, rows, False)
    pooled, pooled_report = check(cli, rows, True)
    total = sum(local.values())
    if not local or total <= 0:
        raise ValueError("the aggregate benchmark requires positive funding in disclosed states")
    difference = {key: pooled[key] - value for key, value in local.items()}
    return {
        "local_payment_cents": total,
        "national_rate_payment_cents": sum(pooled.values()),
        "sum_absolute_state_error_cents": sum(map(abs, difference.values())),
        "negative_state_differences": sum(value < 0 for value in difference.values()),
        "positive_state_differences": sum(value > 0 for value in difference.values()),
        "zero_state_differences": sum(value == 0 for value in difference.values()),
        "sum_absolute_relative_error": {
            "numerator": sum(map(abs, difference.values())),
            "denominator": total,
        },
        "local_report_sha256": local_report,
        "national_rate_report_sha256": pooled_report,
    }


def calibration_request(states: dict[str, tuple[str, str]]) -> dict:
    if len(states) < 2:
        raise ValueError("calibration requires at least two usable geographies")
    contributions = {
        key: (int(count), Fraction(amount) * int(count)) for key, (count, amount) in states.items()
    }
    total_count = sum(count for count, _ in contributions.values())
    total_amount = sum(amount for _, amount in contributions.values())
    mapped = request(states, pooled=False)
    mapped["run_id"] = "cms-held-out-state-rate-calibration"
    for quote in mapped["quotes"]:
        key = quote["id"].removeprefix("rate-")
        count, amount = contributions[key]
        rate = (total_amount - amount) / (total_count - count)
        quote["amount"] = {"numerator": str(rate.numerator), "denominator": str(rate.denominator)}
        quote["source"]["id"] = f"cms-2024-drg470-calibration-excluding-{key}"
    return mapped


def calibrate(cli: Path, rows: dict[str, tuple[str, str]]) -> dict:
    states = {key: value for key, value in rows.items() if key != "national"}
    mapped = calibration_request(states)
    local, local_report = check(cli, rows, False)
    total = sum(local.values())
    if total <= 0:
        raise ValueError("the aggregate benchmark requires positive funding in disclosed states")

    predictions = {}
    for key, (count, _) in sorted(states.items()):
        training = [values for other, values in states.items() if other != key]
        training_payment = sum(Fraction(size) * Fraction(mean) for size, mean in training)
        training_count = sum(int(size) for size, _ in training)
        predictions[f"state-{key}"] = round(training_payment * int(count) * 100 / training_count)
    fitted_report = verify_valuation(cli, mapped, predictions)
    folds = [
        {
            "geography": key.removeprefix("state-"),
            "reference_cents": local[key],
            "prediction_cents": prediction,
            "error_cents": prediction - local[key],
        }
        for key, prediction in predictions.items()
    ]
    absolute_error = sum(abs(fold["error_cents"]) for fold in folds)
    return {
        "local_payment_cents": total,
        "held_out_payment_cents": sum(predictions.values()),
        "sum_absolute_state_error_cents": absolute_error,
        "sum_absolute_relative_error": {"numerator": absolute_error, "denominator": total},
        "local_report_sha256": local_report,
        "held_out_report_sha256": fitted_report,
        "folds": folds,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--cli", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--calibrate", action="store_true", help="Fit and score held-out states")
    args = parser.parse_args()
    if args.source.stat().st_size > 2_000_000:
        raise ValueError("CMS input exceeds the bounded replay budget")
    rows, excluded = rows_from(args.source.read_bytes())
    outcome = calibrate(args.cli, rows) if args.calibrate else transport(args.cli, rows)
    states = STATES & rows.keys()
    payload = {
        "protocol": "cms-funding-calibration-v1" if args.calibrate else "cms-funding-transport-v1",
        "source_url": ENDPOINT,
        "source_sha256": PIN,
        "retrieved_on": AS_OF,
        "cli_sha256": digest(args.cli.read_bytes()),
        "eligible_geographies": len(STATES),
        "tested_geographies": len(states),
        "absent_geographies": sorted(STATES - rows.keys() - excluded.keys()),
        "excluded_fields": excluded,
        "discharges": sum(int(rows[key][0]) for key in states),
        **outcome,
    }
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2)
        stream.write("\n")


if __name__ == "__main__":
    main()
