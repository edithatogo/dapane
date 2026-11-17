# D2 optional decision-provider preparation — isolated candidate

This directory is a **candidate** for the existing Dapane
[`decision_integrations_20261108`](../../conductor/tracks/decision_integrations_20261108/index.md)
Phase D2, stacked on D1/T1 draft PR #23. No source, schema, root workflow or
common numerical kernel is changed. The new path needs the **sole integrator's
explicit ownership and namespace decision** before acceptance. No provider
method is registered in Dapane's released CLI or Python package.

## Scope of the four D2 leaves

| Leaf | Present in this candidate | Remains outside this candidate |
| --- | --- | --- |
| D2.1 | Admit an independently selected D1 output digest and complete six-key panel; accept externally valued net-benefit cells with identical price-year/basis and no missing or duplicated keys; prepare Voiage's already defined `voiage-domain::ValueArray` fields with an exact-amount ledger and bounded rational-to-f64 conversion. | Native installed Voiage adapter execution, scientific EVPI/EVPPI/EVSI qualification, clinical outcome valuation, and Voiage O01–O08. |
| D2.2 | Convert an **externally supplied** Innovate adoption trajectory to exact resource demand, finite per-period capacity, served demand and backlog; require a separately selected prior receipt and explicit external valuation trigger for any later price-feedback iteration. | Innovate model fitting, native trajectory execution, Kairos resource scheduling, Dapane monetary evaluation, empirical calibration and automatic convergence. |
| D2.3 | Admit Paignia's actual supported `static-finite-perfect-information-sparse-zero/1.0.0` profile; build a two-or-more-action single-decision **native struct construction blueprint** with explicitly supplied independent utilities, while rejecting raw cost-as-utility and nonzero domestic transfer contribution. | Paignia solver calls, an assumed JSON wire format (none is registered for these Rust structs), real game semantics, multi-player games, and installed application acceptance. |
| D2.4 | Fail closed on provider names, exact source-commit format, profile/method versions, pairing, money basis/price year, nonrepresentable f64, transfer treatment, absent feedback receipts and unsupported requests. Independent synthetic reference (EVPI = 1 from a 2×2 already-valued matrix). | Installed provider artifacts/revisions, full D1 acceptance, fiscal T2/T3 source admission, and production finance/VOI/strategy decisions. |

## Pre-existing ownership preserved

- `microcosting_genomics`: assays, workbook interpretation, resource recipes.
- `microcosting_healthworkforce`: dated wage-source evidence, classifications and eligibility.
- Dapane core: exact quantities, quotations, valuation/allocation, ledger and rollback.
- Innovate: adoption/competition/price-response model semantics and native execution.
- Voiage: net-benefit/VOI numerical methods; D2 does not implement EVPI.
- Paignia: finite game representation, validation and solution; D2 does not solve games.
- Kairos: optional neutral DES/ABM scheduling and RNG.
- Applications/CareOps: scenario mapping, feedback policy and economic interpretation.

All synthetic fixture identities are *declarations*, not proof of authoritative
execution or provider provenance. Hashes are content-integrity checks, not
signatures. Any apparent connection to a published result requires a separate
actual, source-bound application execution receipt.

## Run the bounded tests

Python **3.12–3.15** standard library; no Dapane wheel, Voiage, Innovate, or
Paignia installed or imported. From this directory:

```sh
python -m unittest discover -s tests -v
python -m compileall -q bridge.py tests
```

The first tests-first run failed with `ModuleNotFoundError: bridge`; after the
implementation and a provider-error code correction, **34 local tests passed**
on CPython 3.13.5. This is a local contract result, not a hosted Dapane/Voiage/
Innovate/Paignia test. There were no skipped tests. Keep existing shared gates.

## Receiving integrator's exact next gates

1. Adopt or amend the proposed path under existing `conductor/parallel-ownership.md`
   without displacing the original D1/T1 owner or changing phase-one evidence.
2. Accept and merge D1/T1 only after its independent gates. Pin an **installed**
   D1 evaluator/wheel and generate a real D1 report rather than only the invented
   structural report used by the standalone guards.
3. Run this adapter against that exact D1 artifact; verify its D1 source/output
   digest and six-key conservation. Install an actual qualified Voiage artifact
   to admit the `ValueArray` and call a supported method; retain independently
   derived numerical acceptance and provider-specific failure diagnostics.
4. Run Innovate's exact native forecast with an independently reviewed model,
   time grid and outcome contract. Compare resource-use translation and explicit
   capacity feedback to independently derived expectations; retain original
   adoption output and separate Dapane core valuations.
5. Construct and validate the game natively through `paignia-core`'s
   `GameSpecification::validate_for_profile` using a fixed qualified Paignia
   package/revision; execute an application test if a solver is claimed. The
   `game_specification` dictionary is a **blueprint**, not a Paignia parser or
   an asserted serialized native format.
6. Add accepted standalone tests to the integrator-owned CI, run normal
   dependency/security/offline release checks on the **receiving source**, and
   reconcile the D2 plan/metadata/index/central registry only for genuinely
   accepted leaves. Preserve the default static costing path and rollback.

D2.1–D2.4 are **implemented as a bounded preparation adapter**, not completed
at the provider-consumer acceptance level. The pending statuses should not be
changed to `[x]` until the real-provider gates above pass.
