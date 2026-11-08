# Implementation plan: Release assurance and conditional consolidation

Status: new

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — First release candidate

- [ ] L1.1 Select the exact first capability set: qualified Rust core, CLI and Python with workforce/genomics evidence; list all other tracks as optional or planned.
- [ ] L1.2 Resolve repository/package licensing, registry identities, supported matrix and source redistribution terms before public package publication.
- [ ] L1.3 Configure reproducible artifacts, dependency/advisory/licence checks, scoped CI permissions and provenance/SBOM generation using maintained tooling.
- [ ] L1.4 Verify a clean build and installed-consumer reference runs for every advertised target; retain exact commands and artifact identities.

## Phase 2 — Operational quality

- [ ] L2.1 Measure representative throughput/memory and document numerical, scale and platform limits; add acceleration only through its own parity/performance evidence.
- [ ] L2.2 Document API/schema deprecation, source corrections, capability negotiation and rollback to previous qualified releases.
- [ ] L2.3 Verify minimal-feature installation and optional-dependency absence; record release evidence without upgrading planned features to supported.

## Phase 3 — Conditional consolidation

- [ ] L3.1 Inventory unique code, workbooks, datasets, research and citations in hwcc, cobra-costing, tutorial_microcosting_genomics and checklist_microcosting; verify current repository status.
- [ ] L3.2 Preserve mchs, workforce and genomics as domain owners; retain voi_sequencing_costs as a research consumer and the maintained CareOps module as its operational owner.
- [ ] L3.3 Prepare successor links and migration/recovery evidence for any selected archive; execute an archive only under its subsequently authorised scope.
- [ ] L3.4 Verify consumer reproduction and preserved scholarly/source assets before removing duplicated machinery or recording an archive as complete.

## Evidence record

No runtime acceptance evidence is recorded by this initial plan.
Update [metadata](metadata.json), [track index](index.md) and [registry](../../tracks.md) together when the status changes.
