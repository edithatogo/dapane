# Implementation plan: Release assurance and conditional consolidation

Status: in_progress

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — First release candidate

- [~] L1.1 Select the exact first capability set: qualified Rust core, CLI and Python with workforce/genomics evidence; list all other tracks as optional or planned.
  - The machine-readable manifest selects candidate core/CLI/Python, profiles 0.1/0.2 and synthetic cases. The real-provider prerequisite remains mandatory and open.
- [!] L1.2 Resolve repository/package licensing, registry identities, supported matrix and source redistribution terms before public package publication.
  - No project licence or verified registry ownership is established. Publication remains disabled; provider assets are excluded. The requested four-interpreter matrix requires exact-run evidence.
- [~] L1.3 Configure reproducible artifacts, dependency/advisory/licence checks, scoped CI permissions and provenance/SBOM generation using maintained tooling.
  - New release-assurance workflow and dependency policy require hosted execution and review; existing runtime/privacy workflows are preserved.
- [~] L1.4 Verify a clean build and installed-consumer reference runs for every advertised target; retain exact commands and artifact identities.
  - Candidate verification covers fresh installations and independent synthetic cases. Actual workforce/genomics composition and historical consumer parity remain with the required Python track.

## Phase 2 — Operational quality

- [~] L2.1 Measure representative throughput/memory and document numerical, scale and platform limits; add acceleration only through its own parity/performance evidence.
  - The existing bounded CLI benchmark will run on the exact candidate in CI. No acceleration or cross-host claim is added.
- [x] L2.2 Document API/schema deprecation, source corrections, capability negotiation and rollback to previous qualified releases.
  - [Migration and recovery](../../../docs/release-migration.md) preserves schema/method/source/artifact identities and provider-owned entry points. No earlier public Dapane runtime or completed provider cutover is assumed.
- [~] L2.3 Verify minimal-feature installation and optional-dependency absence; record release evidence without upgrading planned features to supported.
  - Installed-wheel byte/RECORD checks and native default-member dependency closure are implemented; exact-run qualification is pending.

## Phase 3 — Conditional consolidation

- [x] L3.1 Inventory unique code, workbooks, datasets, research and citations in hwcc, cobra-costing, tutorial_microcosting_genomics and checklist_microcosting; verify current repository status.
  - Bounded authenticated inspection covered current trees and relevant retained branches. Public-safe findings preserve restricted details and establish that no candidate can be treated as empty or fully migrated.
- [x] L3.2 Preserve mchs, workforce and genomics as domain owners; retain voi_sequencing_costs as a research consumer and the maintained CareOps module as its operational owner.
  - [Owner boundaries and pinned public sources](../../../docs/release-consolidation.md) record this disposition.
- [-] L3.3 Prepare successor links and migration/recovery evidence for any selected archive; execute an archive only under its subsequently authorised scope.
  - No external archive is selected. Existing owner links are retained; no cutover, deletion or repository archival is performed.
- [-] L3.4 Verify consumer reproduction and preserved scholarly/source assets before removing duplicated machinery or recording an archive as complete.
  - No machinery removal or external archive is selected. Consumer reproduction remains an open release/provider criterion; it is not claimed complete by this conditional omission.

## Review, fixes and archival

- [~] L4.1 Review the implementation against the original acceptance criteria, apply concrete fixes and retain exact-source verification.
- [!] L4.2 Archive this track after all mandatory acceptance criteria have evidence.
  - Archival is already authorised by the user. It is held by L1.2 and the required real-consumer evidence, not by an additional approval form. Do not weaken those criteria to obtain an archive marker.

## Evidence record

See [execution and review evidence](evidence.md). Candidate reports bind actual
source, artifacts, platform, methods and synthetic data versions; they do not
establish scientific validity, registry entitlement, source rights or real
provider migration. Update [metadata](metadata.json), [track index](index.md) and
[registry](../../tracks.md) together when status changes.
