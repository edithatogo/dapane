# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Check annual platform costs and capacity allocation against exact oracles."""

from datetime import date
from fractions import Fraction
from hashlib import sha256
from pathlib import Path

from dapane_genomics.model_tables import LabProfile
from dapane_genomics.pricing import calculate_lab_equipment_cost
from genomics_microcosting.compute_cost import ComputeCostContext
from genomics_microcosting.onprem_cost import (
    OnPremBinding,
    OnPremPricing,
    Role,
    calculate_onprem_cost,
)
from genomics_microcosting.provenance_ledger import (
    Parameter,
    ParameterQualification,
    ParameterSet,
    QualificationLedger,
    SourceRecord,
    SourceValidity,
)


def platform_inputs(
    tmp_path: Path,
    **overrides: str,
) -> tuple[OnPremPricing, ComputeCostContext]:
    """Provide explicit synthetic annual costs and capacities, not observed prices."""
    data: dict[Role, tuple[str, str]] = {
        "acquisition": ("1000", "AUD"),
        "residual": ("0", "AUD"),
        "life": ("5", "year"),
        "interest": ("0", "fraction"),
        "support": ("100", "AUD/year"),
        "licensing": ("50", "AUD/year"),
        "power": ("100", "kWh/year"),
        "cooling": ("50", "kWh/year"),
        "energy_rate": ("2", "AUD/kWh"),
        "facilities": ("50", "AUD/year"),
        "available": ("100", "core_s/year"),
        "used": ("60", "core_s/year"),
        "workload": ("20", "core_s/year"),
    }
    params: list[Parameter] = []
    quals: list[ParameterQualification] = []
    validity: list[SourceValidity] = []
    paths: dict[str, Path] = {}
    bindings: list[OnPremBinding] = []
    for role, (default, unit) in data.items():
        value = overrides.get(role, default)
        path = tmp_path / f"{role}.txt"
        path.write_text(value + "\n", encoding="utf-8")
        digest = sha256(path.read_bytes()).hexdigest()
        source = SourceRecord(
            source_id=role,
            sha256=digest,
            edition="synthetic",
            locator="line 1",
            limitations="synthetic",
        )
        p = Parameter(
            parameter_id=role,
            raw_value=value,
            derived_value=value,
            unit=unit,
            source_sha256=digest,
            source_locator="line 1",
            transformation="identity",
            uncertainty="synthetic",
            status="reported",
        )
        params.append(p)
        quals.append(
            ParameterQualification(
                parameter=p,
                source=source,
                exact_support=value,
                dimensional_basis=unit,
                applicability="synthetic",
                qualification="qualified",
                blockers=(),
            ),
        )
        validity.append(
            SourceValidity(
                source=source,
                retrieved=date(2026, 11, 6),
                effective_from=date(2026, 1, 1),
                effective_until=date(2026, 12, 31),
                date_basis="synthetic",
            ),
        )
        paths[role] = path
        bindings.append(OnPremBinding(role=role, parameter_id=role))
    context = ComputeCostContext(
        QualificationLedger(
            parameter_set=ParameterSet(
                version_id="v1",
                workbook_sha256="f" * 64,
                parameters=tuple(params),
            ),
            qualifications=tuple(quals),
        ),
        paths,
        tuple(validity),
        date(2026, 6, 1),
    )
    pricing = OnPremPricing(
        platform_id="synthetic-host",
        workload_id="w1",
        currency="AUD",
        price_year=2026,
        tax_basis="inclusive",
        capacity_unit="core_s",
        annualization="straight_line",
        allocation_basis="available_capacity",
        bindings=tuple(bindings),
        assumption_basis="synthetic annual platform scope; no empirical claim",
    )
    return pricing, context


def test_lab_equipment_life_revalues_only_the_declared_capital_assumption(
    tmp_path: Path,
) -> None:
    """Use the original cost model and preserve the original source identity."""
    pricing, context = platform_inputs(tmp_path, residual="100")
    baseline = calculate_onprem_cost(pricing, context)
    profile = LabProfile.model_validate(
        {"cost_adjustments": {"equipment_depreciation_years": 9}}
    )
    revised = calculate_lab_equipment_cost(pricing, context, profile)
    assert calculate_lab_equipment_cost(pricing, context, LabProfile()) == baseline

    assert dict(baseline.annual_components)["capital"] == Fraction(180)
    assert dict(revised.annual_components)["capital"] == Fraction(100)
    assert revised.total_annual_cost == Fraction(600)
    assert revised.workload_cost == Fraction(120)
    assert revised.input_sha256 != baseline.input_sha256
    assert calculate_onprem_cost(pricing, context) == baseline
