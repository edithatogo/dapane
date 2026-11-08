# Dapane Conductor

This is the authoritative index for Dapane's project context and execution plan.
The setup is dated **8 November 2026**. Shared-framework coordination now lives
here; specialist implementations, ontology semantics and reporting sources retain
their repository owners.

## Project context

| Document | Purpose |
| --- | --- |
| [Product](product.md) | Users, outcomes, scope and initial delivery boundary |
| [Product guidelines](product-guidelines.md) | Inputs, results, explanations and research claims |
| [Requirements](requirements.md) | Stable RQ identifiers and acceptance criteria |
| [Design](design.md) | Architecture, records, numeric rules and adapter contracts |
| [Decisions](decisions.md) | Architectural choices and unresolved implementation decisions |
| [Technology stack](tech-stack.md) | Selected directions, dependency qualification and actual tooling |
| [Workflow](workflow.md) | Agent-executable tasks, evidence, review and synchronisation |
| [Style guides](code_styleguides/index.md) | Rust, Python, FFI and documentation conventions |
| [Repository map](repository-map.md) | Actual files, provenance and planned implementation areas |
| [Ecosystem](ecosystem.md) | Source owners, provider readiness, migration and rollback |
| [Research and validation](research-validation.md) | Independent cases, comparators and frontier hypotheses |

## Execution

- [Roadmap](roadmap.md): capability milestones and optional delivery paths.
- [Track registry](tracks.md): status and entry points for all tracks.
- [Setup record](tracks/conductor_setup_20261108/index.md): what this initialisation delivers.
- [Core contracts](tracks/core_contracts_20261108/index.md): first runtime implementation prerequisite.
- [Verification record](verification.md): checks performed on this setup and their limits.
- [Archive policy](archive/README.md): retention without premature archival.

The registry and each track's metadata describe the same state. Plans record
task-level progress. A completed setup track means the project context is ready;
it does not advance any runtime or research capability.
