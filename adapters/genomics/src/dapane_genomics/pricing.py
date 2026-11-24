# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Compose external price releases and exact volume tiers with native valuation."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
from typing import TYPE_CHECKING, Any

from genomics_microcosting.dapane_adapter import evaluate_native_request
from genomics_microcosting.onprem_cost import (
    OnPremCost,
    OnPremPricing,
    calculate_onprem_cost,
    calculate_onprem_cost_with_life,
)

from .model_tables import LabProfile

if TYPE_CHECKING:
    from genomics_microcosting.compute_cost import ComputeCostContext

type FetchPrices = Callable[[tuple[str, ...]], bytes]


@dataclass(frozen=True)
class VolumeDiscount:
    """A discount that applies at or above a declared order volume."""

    minimum_units: int
    fraction: str


def _fraction(value: str | dict[str, str]) -> Fraction:
    if isinstance(value, str):
        return Fraction(value)
    if isinstance(value, dict) and set(value) == {"numerator", "denominator"}:
        if all(isinstance(part, str) for part in value.values()):
            return Fraction(int(value["numerator"]), int(value["denominator"]))
    raise ValueError("Quote amounts must use exact strings or rational pairs")


def _exact(value: Fraction) -> dict[str, str]:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def _select_tier(tiers: Sequence[VolumeDiscount], units: int) -> VolumeDiscount | None:
    thresholds = set()
    for tier in tiers:
        if type(tier.minimum_units) is not int or tier.minimum_units < 1:
            raise ValueError("Volume tiers require positive integer thresholds")
        if tier.minimum_units in thresholds or not 0 <= _fraction(tier.fraction) <= 1:
            raise ValueError(
                "Volume tier thresholds must be unique and discounts between zero and one"
            )
        thresholds.add(tier.minimum_units)
    return max(
        (tier for tier in tiers if units >= tier.minimum_units),
        key=lambda tier: tier.minimum_units,
        default=None,
    )


def _external_quotes(payload: bytes, wanted: tuple[str, ...]) -> list[dict[str, Any]]:
    if not isinstance(payload, bytes):
        raise ValueError("Price providers must return versioned JSON bytes")
    catalog = json.loads(payload)
    if not isinstance(catalog, dict) or catalog.get("schema_version") != "0.1":
        raise ValueError("Unknown external price release schema")
    quotes = catalog.get("quotes")
    if not isinstance(quotes, list) or any(
        not isinstance(quote, dict) or not isinstance(quote.get("id"), str)
        for quote in quotes
    ):
        raise ValueError("External price release requires an identified quotation list")
    identifiers = [quote["id"] for quote in quotes]
    if len(set(identifiers)) != len(identifiers) or set(identifiers) != set(wanted):
        raise ValueError(
            "External price release must supply every requested quote exactly once"
        )
    return quotes


def value_with_prices(
    request: dict[str, Any],
    *,
    fetch: FetchPrices,
    volume: int,
    discounts: Mapping[str, Sequence[VolumeDiscount]] | None = None,
    lab_profile: LabProfile | None = None,
    labour_quote_ids: Sequence[str] = (),
) -> dict[str, Any]:
    """Preserve fetched price identity, then value the resulting exact request.

    The caller supplies the external price reader and its access configuration.
    Every invocation requests the missing quote IDs. Keep the returned request
    and release digest to replay the same valuation without contacting the source.
    """
    if type(volume) is not int or volume < 1:
        raise ValueError("Volume must be a positive integer")
    prepared = deepcopy(request)
    criteria = discounts or {}
    supplied = {quote["id"] for quote in prepared["quotes"]}
    needed = tuple(sorted({use["quote_id"] for use in prepared["usage"]} - supplied))
    digest = None
    if needed:
        payload = fetch(needed)
        prepared["quotes"].extend(_external_quotes(payload, needed))
        digest = sha256(payload).hexdigest()
    if set(criteria) - {quote["id"] for quote in prepared["quotes"]}:
        raise ValueError("Volume discounts must name a supplied quotation")

    lab_changes = {}
    if lab_profile is not None:
        profile_digest = sha256(lab_profile.model_dump_json().encode()).hexdigest()
        labour_quotes = {
            quote["id"]: quote
            for quote in prepared["quotes"]
            if quote["components"] == ["labour"]
        }
        multiplier = _fraction(lab_profile.cost_adjustments.labor_multiplier)
        selected = set(labour_quote_ids)
        if len(selected) != len(labour_quote_ids) or selected - labour_quotes.keys():
            raise ValueError("Select distinct labour-only quotations for lab pricing")
        if multiplier != 1 and not selected:
            raise ValueError(
                "Select the quotations covered by the lab labour multiplier"
            )
        if multiplier != 1:
            for quote_id in sorted(selected):
                quote = labour_quotes[quote_id]
                source_amount = _fraction(quote["amount"])
                source = quote["source"]
                lab_changes[quote_id] = {
                    "profile_sha256": profile_digest,
                    "original_amount": _exact(source_amount),
                    "original_source": source,
                    "multiplier": _exact(multiplier),
                }
                quote["amount"] = _exact(source_amount * multiplier)
                quote["source"] = {
                    "id": "lab-adjusted-labour",
                    "version": profile_digest,
                    "evidence": "derived",
                    "access": source["access"],
                    "validation": "unvalidated",
                    "content_digest": f"sha256:{profile_digest}",
                    "locator": "cost_adjustments.labor_multiplier",
                }
    elif labour_quote_ids:
        raise ValueError("Labour quotation selection requires a lab profile")

    applied = {}
    for quote in prepared["quotes"]:
        tier = _select_tier(criteria.get(quote["id"], ()), volume)
        if tier is None:
            continue
        price = _fraction(quote["amount"])
        discount = _fraction(tier.fraction)
        if price < 0:
            raise ValueError("A volume discount requires a nonnegative source price")
        quote["amount"] = _exact(price * (1 - discount))
        applied[quote["id"]] = {
            "minimum_units": tier.minimum_units,
            "discount": _exact(discount),
            "original_amount": _exact(price),
        }
    return {
        "external_release_sha256": digest,
        "volume": volume,
        "applied_discounts": applied,
        "applied_lab_adjustments": lab_changes,
        "request": prepared,
        "report": evaluate_native_request(prepared),
    }


def calculate_lab_equipment_cost(
    pricing: OnPremPricing,
    context: ComputeCostContext,
    profile: LabProfile,
) -> OnPremCost:
    """Value equipment with the lab's declared depreciation life when supplied."""
    life = profile.cost_adjustments.equipment_depreciation_years
    if life is None:
        return calculate_onprem_cost(pricing, context)
    return calculate_onprem_cost_with_life(pricing, context, life)
