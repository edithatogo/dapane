# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Qualify exact external valuation and the cost prediction's held-out outputs."""

import json
from hashlib import sha256

import polars as pl
import pytest

from dapane_genomics.prediction import fit_cost_model
from dapane_genomics.pricing import VolumeDiscount, value_with_prices
from genomics_microcosting.dapane_workbook import historical_use, new_historical_request


def _catalogue():
    quote = {
        "id": "quoted-compute",
        "target": "compute",
        "unit": "hour",
        "kind": "resource_use",
        "amount": "12.50",
        "per_quantity": "1",
        "currency": "AUD",
        "price_year": 2023,
        "basis": "financial_cost",
        "components": ["compute"],
        "valid_from": "2023-09-02",
        "valid_to": "2023-09-03",
        "known_from": "2023-09-02",
        "source": {
            "id": "synthetic-price-catalogue",
            "version": "1",
            "evidence": "synthetic",
            "access": "public",
            "validation": "unvalidated",
        },
    }
    request = new_historical_request("synthetic-volume-and-allocation")
    request["usage"] = [historical_use("compute-line", "4", quote, locator="synthetic")]
    request["objects"] = [
        {"id": "case-a", "kind": "test"},
        {"id": "case-b", "kind": "test"},
    ]
    request["allocations"] = [
        {
            "id": "shared-compute",
            "source_line_ids": ["compute-line"],
            "weights": [
                {"object_id": "case-a", "weight": "1"},
                {"object_id": "case-b", "weight": "2"},
            ],
        }
    ]
    return request, json.dumps({"schema_version": "0.1", "quotes": [quote]}).encode()


def test_price_release_selects_exact_volume_tier_and_allocates_booked_pool():
    request, payload = _catalogue()
    calls = []

    def fetch(identifiers):
        calls.append(identifiers)
        return payload

    result = value_with_prices(
        request,
        fetch=fetch,
        volume=300,
        discounts={
            "quoted-compute": [VolumeDiscount(50, "0.05"), VolumeDiscount(100, "0.125")]
        },
    )
    assert calls == [("quoted-compute",)]
    assert not request["quotes"]
    assert result["external_release_sha256"] == sha256(payload).hexdigest()
    assert result["applied_discounts"]["quoted-compute"]["minimum_units"] == 100
    assert result["report"]["totals"]["rounded"] == "43.75"
    assert {
        share["object_id"]: share["rounded"]
        for share in result["report"]["allocations"][0]["shares"]
    } == {
        "case-a": "14.58",
        "case-b": "29.17",
    }
    assert result["report"]["allocations"][0]["residual"] == "0.00"

    with pytest.raises(ValueError, match="every requested quote"):
        value_with_prices(
            request, fetch=lambda _: b'{"schema_version":"0.1","quotes":[]}', volume=300
        )


def test_prediction_reproduces_independent_holdout_values():
    training = pl.DataFrame(
        {
            "orders": [1, 2, 3, 4, 4],
            "hours": [1, 1, 2, 3, 2],
            "cost": [27, 30, 37, 44, 40],
        }
    )
    model = fit_cost_model(training, features=("orders", "hours"), response="cost")
    holdout = pl.DataFrame({"orders": [5, 6], "hours": [4, 1]})
    assert model.predict(holdout).to_list() == pytest.approx([51, 42])
    with pytest.raises(ValueError, match="identify the model"):
        fit_cost_model(
            training.with_columns(pl.col("orders").alias("hours")),
            features=("orders", "hours"),
            response="cost",
        )
