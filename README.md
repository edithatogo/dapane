# Dapane

**Microcosting and valuation with an independent Rust core.**

Dapane turns explicit resource use and classified activity into reproducible
valuations. Its first working candidate contains an exact Rust kernel, a JSON
CLI, thin Python bindings, versioned schemas and independent synthetic fixtures.
Workforce, genomics, hospital funding and newborn-screening packages retain their
specialist rules and source data. Installed R and Julia candidates exercise the same Rust boundary. Their host coverage is recorded in the [binding verification](conductor/tracks/polyglot_bindings_20261108/verification.md).

## Current status

This is an **unpublished 0.1.0 candidate**, implementing a bounded subset of the
Conductor requirements and roadmap. It supports nonnegative point-date quantities,
exact quotation application, conserving allocation and event/process/object context.
Wire profile 0.1 retains full-pool allocation; [profile 0.2](docs/contract-v0.2.md)
adds explicit incomplete instrument-capacity allocation, preserving unknown
observations and unallocated value. The package remains an unpublished candidate.
Documentation validation alone does not establish numerical or empirical validity.

The separate [run-bundle profile 0.1](docs/run-bundle-v0.1.md) adds immutable
snapshots, replacement histories and nonfinancial withdrawal tombstones. Its
repository verifier checks declared release consistency and replays each full
valuation snapshot through the installed Rust wheel. The
[core-contract evidence](conductor/tracks/core_contracts_20261108/verification.md)
records the reviewed revision, executed checks and qualification limits.

The separate [interval profile 0.1](docs/interval-contract-v0.1.md) adds native/CLI
rate-boundary segmentation for explicitly declared uniform calendar-day exposure.
It preserves the original point/capacity methods and returns parent snapshots,
exact segment quantities and a replayable scalar request. The
[kernel qualification](conductor/tracks/rust_kernel_20261108/verification.md)
records independent review, installed artifacts and the supported bounds.

The selected [installed provider composition](docs/python-provider-verification.md)
connects a dated workforce base-pay quotation to manual DNA-extraction labour,
with canonical/legacy compatibility and an explicit historical calculator path.
The two provider environments keep their exact Python 3.15.2 and 3.15.1 pins.
The [release handoff record](docs/release-handoff-2026-11-15.md) confirms that the
setup, contracts, kernel and Python/provider archives are incorporated, and
[post-merge `main` qualification](docs/release-qualification-2026-11-19.md)
records verified `0658d94` candidate artifacts and signed trusted-main provenance.
Release qualification consumes their existing records and checks the exact candidate
artifacts; publication remains disabled.

Optional adapters now cover bounded process models, reporting exports, fiscal decision tables and adoption forecasts. The manual CareOps file exchange replays the installed CLI and wheel. Its target-tenant round trip and public package distribution remain open. The [track registry](conductor/tracks.md) lists the evidence and remaining work.

## Kairos and the three contexts

Kairos is an optional DES/ABM producer of simulated resource use. Dapane does not
depend on it. Observed data and static recipes use the same core directly. Kairos's
inspected neutral usage export is still pending; a real adapter is not implied
by a synthetic fixture.

Event, process and object views coexist over one ledger. An assay-run event can
belong to a screening execution and link to a batch, specimens and infants. The
batch is charged once; explicit allocation assigns shares to infants. Merely
relating the batch to two infants does not duplicate its cost. Read the
[event/process/object model](docs/event-process-object-model.md) and
[pinned provider review](docs/provider-boundaries.md).

## Run an example

```sh
cargo build --locked --release -p dapane-cli
target/release/dapane evaluate fixtures/newborn-screening.json
```

The synthetic newborn example values collections at 10 each, a shared batch at
100 and one confirmation at 30: a source total of **150**, with infant views of
**60 and 90**. Other fixtures cover fractional workforce time, genomics,
activity-only funding and sub-cent allocation. None contains an official rate
or real patient data.

An explicitly declared interval can use pinned quotations across a rate boundary:

```sh
target/release/dapane evaluate-intervals fixtures/intervals/rate-boundary.json
```

That synthetic example distributes one hour over three calendar days and produces
`(1/3 × 90) + (2/3 × 120) = 110`. Exposure is supplied by the caller; the engine
does not infer working hours or utilisation from dates. Interval access is currently
Rust/CLI; the Python wrapper continues to expose the existing scalar methods.

The [synthetic genomics capacity cases](fixtures/genomics-capacity/README.md)
compare declared time-based and sample-based allocation, distinguish maintenance
contract duration from device useful life, and keep one-time implementation
costs separate from recurring costs. Their preparation assumptions are candidate
scenarios, not validated economic formulae. See the [increment verification](docs/genomics-capacity-verification.md).

After building and installing the Python wheel using the [quickstart](docs/quickstart.md):

```python
import json
from pathlib import Path
from dapane import evaluate

request = json.loads(Path("fixtures/newborn-screening.json").read_text())
report = evaluate(request)
assert report["totals"]["rounded"] == "150.00"
```

Python transports exact values and structured errors; Rust performs valuation
and allocation. Python has no runtime package dependencies. Its actual tested
interpreter/platform matrix is recorded in the verification document.

## Start here

- [Conductor index](conductor/index.md): authoritative project context.
- [Requirements](conductor/requirements.md): stable requirements and acceptance criteria.
- [Design](conductor/design.md): contracts, component boundaries and data flow.
- [Roadmap](conductor/roadmap.md): milestones, prerequisites and optional delivery paths.
- [Tracks](conductor/tracks.md): specifications and task-level implementation plans.
- [Ecosystem](conductor/ecosystem.md): provider ownership, migration and source snapshots.
- [Research and validation](conductor/research-validation.md): reference cases and research hypotheses.

## Direction

- Keep physical resource consumption, weighted activity, tariffs, funding, payments
  and opportunity cost distinguishable.
- Preserve exact decimal/rational inputs, explicit units, rate dates, rounding and
  shared-cost reconciliation.
- Make domain packages, process models, reporting, cloud delivery and decision
  libraries optional at the core boundary.
- Use thin Python/R/Julia interfaces to the same Rust calculation implementation.
- Offer CLI/file exchange first; retain a standard-connector Power Apps route and
  optional worker, premium API and qualified browser-component routes.
- Reuse UOGTO semantics and standards_check reporting sources rather than copy
  their ontology or checklist ownership into this repository.

## Working on the repository

Read [AGENTS.md](AGENTS.md) and the [workflow](conductor/workflow.md), then select a
ready task from its track. The current dependency-free documentation check is:

```sh
.venv/bin/python scripts/validate_conductor.py
```

This command checks Conductor structure, local links, requirement coverage, track
state and the dependency graph. The quickstart also documents native tests,
independent schema/fixture checks and installed-wheel tests outside the checkout.

## Origin and publication

The starting design was developed in [MCHS PR 411](https://github.com/edithatogo/mchs/pull/411).
Dapane now owns the shared framework plan; the related ontology and source
catalogue remain in [UOGTO PR 128](https://github.com/edithatogo/UOGTO/pull/128) and
[standards_check PR 65](https://github.com/edithatogo/standards_check/pull/65).
Their merge/release status is recorded as a dated observation in the ecosystem
document, not assumed from a planning dependency.

## Licence

Dapane is licensed under the [Apache License, Version 2.0](LICENSE), selected by
the project owner on 15 November 2026. [NOTICE](NOTICE) records project attribution.
The Rust workspace and citation metadata declare `Apache-2.0` for project material.
[THIRD_PARTY_NOTICES.txt](THIRD_PARTY_NOTICES.txt) retains the locked dependencies'
and Rust standard library's licence and attribution texts. All three legal files
accompany crate sources, wheels, Python source distributions and candidate CLI
bundles. Python's optional aggregate distribution licence expression is omitted;
the [controls guide](docs/release-controls.md) explains that metadata boundary.
Separately obtained provider assets retain their own terms and are excluded.

No registry release, package-name reservation or app deployment is asserted.
Workspace publication remains disabled pending registry ownership and release
qualification. The [release handoff record](docs/release-handoff-2026-11-15.md)
and [post-merge `main` qualification](docs/release-qualification-2026-11-19.md)
identify the incorporated archives, attested `0658d94` artifacts and remaining
publication/security gates.
