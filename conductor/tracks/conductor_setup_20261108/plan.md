# Implementation plan: Conductor setup and source-of-truth handoff

Status: in_progress

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Context

- [x] S1.1 Inspect repository state and existing instructions; create product, requirements, design, technology and workflow context.
- [x] S1.2 Record the prior MCHS design and current UOGTO/standards_check source ownership, with immutable references where available.
- [x] S1.3 Verify that documented facts, assumptions and planned capabilities are distinguished.

## Phase 2 — Executable programme

- [x] S2.1 Create the 13 track specifications, phased plans, indexes and metadata; map requirements and local prerequisites.
- [x] S2.2 Document the first-release path, optional branches and the next executable task.
- [x] S2.3 Validate local links, required metadata, task/status consistency, requirement coverage and dependency acyclicity; inspect the diff.

## Phase 3 — Publication and handoff

- [~] S3.1 Publish the reviewed setup to the empty repository without changing provider repositories or claiming package release.
- [ ] S3.2 Verify the remote file/commit state and any configured documentation CI; record the actual outcome.
- [ ] S3.3 Synchronise setup metadata, index and registry; mark setup complete only after its acceptance checks pass.

## Evidence record

Local setup checks and review resolutions are recorded in [verification](../../verification.md).
No runtime acceptance evidence is recorded by this initial plan.
Update [metadata](metadata.json), [track index](index.md) and [registry](../../tracks.md) together when the status changes.
