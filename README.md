# Dapane

**Microcosting and valuation with an independent Rust core.**

Dapane turns explicit resource use and classified activity into reproducible
valuations. Its first working candidate contains an exact Rust kernel, a JSON
CLI, thin Python bindings, versioned schemas and independent synthetic fixtures.
Workforce, genomics, hospital funding and newborn-screening packages retain their
specialist rules and source data. R and Julia remain planned bindings.

## Current status

This is an **unpublished 0.1.0 candidate**, implementing a bounded subset of the
Conductor requirements and roadmap. It supports nonnegative point-date quantities,
exact quotation application, conserving allocation and event/process/object context.
Documentation validation alone does not establish numerical or empirical validity.

Installed provider adapters, automatic interval segmentation, richer economic
methods, R/Julia, reporting exports, Power Apps and process execution remain
separate work. See the [implemented contract](docs/contract-v0.1.md),
[compatibility policy](docs/compatibility.md) and
[runtime verification](docs/runtime-verification.md) for exact limits and evidence.

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
python3 scripts/validate_conductor.py
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

No registry release, package-name reservation, app deployment or repository archive
is asserted. The project licence remains an explicit release prerequisite;
workspace packages disable Cargo publication until it is resolved.
