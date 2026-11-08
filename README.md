# Dapane

**Microcosting and valuation with a shared Rust core.**

Dapane is being developed to turn measured or modelled resource use and classified
activity into explicit, reproducible valuations. Workforce, genomics, hospital
funding and newborn-screening packages will supply specialist rules and data;
Dapane will own the common numerical contracts, allocation ledger and evidence
bundle. Python is the first planned binding, followed by R and Julia.

## Current status

This repository contains the initial Conductor project context, requirements,
design, roadmap and executable implementation tracks. **The costing runtime and
language packages are not implemented or released here yet.** Documentation
validation does not establish economic, clinical or numerical validity.

The next engineering milestone is a minimal Rust implementation used by one
workforce calculation and one genomic workflow through independently installed
Python packages. Newborn screening is the first planned new domain.

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
state and the dependency graph. Runtime build, installation and release commands
will be established by their implementation tracks.

## Origin and publication

The starting design was developed in [MCHS PR 411](https://github.com/edithatogo/mchs/pull/411).
Dapane now owns the shared framework plan; the related ontology and source
catalogue remain in [UOGTO PR 128](https://github.com/edithatogo/UOGTO/pull/128) and
[standards_check PR 65](https://github.com/edithatogo/standards_check/pull/65).
Their merge/release status is recorded as a dated observation in the ecosystem
document, not assumed from a planning dependency.

No software release or package-name reservation is asserted. No licence was
present in the empty repository at setup; choosing and recording the project
licence is an explicit release prerequisite.
