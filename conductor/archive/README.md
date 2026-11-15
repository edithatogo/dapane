# Track archive

No tracks were archived at initialisation on 8 November 2026.

Completed tracks normally remain in place with their evidence and stable links.
Move a track only when it improves navigation and its links, dependency references
and source history are preserved. Do not delete a plan to conceal incomplete work.

For in-place archival, retain `conductor/tracks/<track_id>/` as the authoritative
record, set metadata, registry, index and plan status to `archived`, and keep the
original task and verification evidence. Archived tracks must have only completed
or explicitly omitted tasks and passed verification. Unfinished and cancelled
work retains its own status. Archival does not change capability qualification
or remove a completed prerequisite from the local dependency graph.

Record each archived track below with its review evidence; do not copy its files
into a second authoritative location.

## Archived tracks

| Track | Completed scope | Archived | Evidence |
| --- | --- | --- | --- |
| [Conductor setup](../tracks/conductor_setup_20261108/index.md) | Project context and source-of-truth handoff | 2026-11-15 | [Review and verification](../tracks/conductor_setup_20261108/review.md) |
| [Core contracts and independent reference cases](../tracks/core_contracts_20261108/index.md) | Synthetic core contracts and independent reference cases | 2026-11-15 | [Acceptance and verification](../tracks/core_contracts_20261108/verification.md); [PR #9 integration](https://github.com/edithatogo/dapane/commit/224cf91dbcf513feaa022b2cf5aa310a965472ce). Original criteria, plan, review records and dependency links remain at the original path. |
| [Rust kernel](../tracks/rust_kernel_20261108/index.md) | Bounded Rust valuation kernel and CLI | 2026-11-15 | [Qualification](../tracks/rust_kernel_20261108/verification.md) and [independent review](../tracks/rust_kernel_20261108/review.md); original specification, plan, metadata, logs and dependency links retained. |

The core-contract archive closes synthetic contract/reference acceptance.
Kernel qualification retains its separately recorded scope and evidence.
Core-contract and kernel archival do not establish real provider qualification,
economic validation or production publication. Other tracks retain their own
status and owners.

## Repository archival

Repository archival is a separate task in the
[release and consolidation track](../tracks/release_consolidation_20261108/index.md).
It requires a functioning successor and review of unique research/source assets;
this directory grants no authority to archive external repositories.
