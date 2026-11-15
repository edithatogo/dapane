# Implementation plan: Conductor setup and source-of-truth handoff

Status: archived

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

- [x] S3.1 Publish the reviewed setup to the empty repository without changing provider repositories or claiming package release.
- [x] S3.2 Verify the remote file/commit state and any configured documentation CI; record the actual outcome.
- [x] S3.3 Synchronise setup metadata, index and registry; mark setup complete only after its acceptance checks pass.

## Phase 4 — Review and archival, 15 November 2026

- [x] S4.1 Reconcile current main, active pull requests and original publication evidence; preserve the completed setup and separate implementation owners.
- [x] S4.2 Reject unfinished or unverified archival and inconsistent or ambiguous status declarations; verify valid in-place archival with the existing dependency links.
- [x] S4.3 Review the corrections independently, apply findings and record focused verification with its limits.
- [x] S4.4 Archive the completed track in place, synchronise its lifecycle records and retain the original setup evidence and stable links.

## Evidence record

Local setup checks and review resolutions are recorded in [verification](../../verification.md).
No runtime acceptance evidence is recorded by this initial plan.
The later [review record](review.md) records the bounded corrections and archival checks.
Update [metadata](metadata.json), [track index](index.md) and [registry](../../tracks.md) together when the status changes.
