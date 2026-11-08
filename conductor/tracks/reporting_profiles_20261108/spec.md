# Reporting profiles and evidence exports

## Outcome and users

Consume UOGTO costing semantics and the standards_check source catalogue to produce evidence-linked, conditionally applicable reporting coverage from Dapane run bundles.

This is a planned work specification. Repository setup does not establish the capabilities below.

## Scope and requirements

Owning requirements: **RQ-07, RQ-01** in [requirements](../../requirements.md).
The [design](../../design.md) and [decisions](../../decisions.md) define the common boundary.

- Retain UOGTO as the ontology owner and standards_check as the instrument/source owner.
- Map Dapane contracts to the optional costing-valuation pack and reporting profiles.
- Keep reporting, method appraisal, computational verification and empirical validation separate.

## Deliverables

- A pinned source manifest and versioned Dapane-to-UOGTO mapping.
- Optional JSON-LD/evidence export and reporting coverage output.
- Positive and negative profile fixtures with explicit extraction and review status.

## Prerequisites and interfaces

Local track dependencies:

- [core_contracts_20261108](../core_contracts_20261108/index.md)

External readiness, checked separately from the local dependency graph:

- edithatogo/UOGTO: costing-valuation applied pack, SHACL, explicit HTA bridge and reporting-profile semantics; qualify a pinned revision.
- edithatogo/standards_check: original reporting instrument catalogue, verified item IDs and extraction qualifications; qualify the matching source revision.

## Acceptance criteria

1. The importer/exporter records exact upstream source versions and checks source content/counts where supported.
2. Original instrument/version/item IDs and extraction qualifications survive export; project profiles do not claim universal endorsement.
3. Reported requirements cite evidence; not-applicable assertions carry rationales; partial, missing, unassessed and unresolved states remain distinguishable.
4. Protocols/reviews are evidence artefacts, not silently promoted into operational reporting checklists.
5. SHACL conformance is not described as methodological correctness, truth of sources or empirical validity.
6. Static valuation and the minimal Rust build remain usable without an RDF reasoner or reporting dependency.

## Risks and constraints

Coverage counts can imply a complete or endorsed standard when only topic mappings exist. Restricted templates and source documents must not be redistributed merely because their metadata is public.

## Migration and rollback

Preserve every source/profile version used by a historical report. A new mapping is a new snapshot; consumers can continue to reproduce the earlier snapshot.

## Open implementation decisions

Choose the first evidence export and profile subset from available verified source mappings. Independent content review and remaining detailed item extraction stay upstream tasks.

## Execution and verification

Follow the [phased plan](plan.md) and [repository workflow](../../workflow.md).
Commands described by pending tasks are future acceptance instructions, not executed evidence.
Record actual commands, source/artifact identities and outcomes in the metadata when work is performed.
