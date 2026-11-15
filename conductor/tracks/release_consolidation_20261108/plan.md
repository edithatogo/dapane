# Implementation plan: Release assurance and conditional consolidation

Status: blocked

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — First release candidate

- [x] L1.1 Select the exact first capability set: qualified Rust core, CLI and Python with workforce/genomics evidence; list all other tracks as optional or planned.
  - The manifest selects core/CLI/Python, profiles 0.1/0.2, Rust/CLI intervals 0.1, run-bundles 0.1, independent synthetic cases and the selected QLD HP3.1/manual-extraction provider subset. Existing owners' durable records and exact pins are consumed; all four prerequisite archives are incorporated. Broader providers and optional tracks remain separate.
- [!] L1.2 Resolve repository/package licensing, registry identities, supported matrix and source redistribution terms before public package publication.
  - Apache-2.0 project licensing is resolved. Complete locked dependency and Rust standard-library notices are generated with authenticated provenance and package-byte checks. The optional Python aggregate licence expression is omitted under the documented metadata boundary. Channel/account choices remain open; publication stays disabled and external provider assets are excluded.
- [x] L1.3 Configure reproducible artifacts, dependency/advisory/licence checks, scoped CI permissions and provenance/SBOM generation using maintained tooling.
  - Source 5f03f28 passed all four hosted dual builds, advisory/licence checks, three SBOMs and the aggregate matrix. All five downloaded artifact archives and 100 member checksums were inspected. The main-only attestation route is configured; central offline security remains a separate unexecuted gate.
- [x] L1.4 Verify a clean build and installed-consumer reference runs for every advertised target; retain exact commands and artifact identities.
  - Source 5f03f28 passed 133 installed tests on each of CPython 3.12.16, 3.13.18, 3.14.10 and 3.15.2, ten independent references and installed interval controls per target. The release provider job consumed the verified candidate artifact 14145643783 and passed in the existing separate environments. Aggregate success includes this exact-artifact result; names/digests are retained in the hosted receipt.

## Phase 2 — Operational quality

- [x] L2.1 Measure representative throughput/memory and document numerical, scale and platform limits; add acceleration only through its own parity/performance evidence.
  - Source 5f03f28 completed the 10/1,000/5,000-row CLI benchmark. Median 5,000-row times were 0.203711 seconds for valuation and 0.317516 for allocation; peak child RSS across the run was 86,384 KiB. Raw measurements, identities and single-runner synthetic limits are retained; no acceleration, empirical or cross-host claim is added.
- [x] L2.2 Document API/schema deprecation, source corrections, capability negotiation and rollback to previous qualified releases.
  - [Migration and recovery](../../../docs/release-migration.md) preserves schema/method/source/artifact identities and the qualified providers' canonical/legacy entry points and bounded historical replay. Broader cutover/removal remains outside this increment; no earlier public Dapane runtime is assumed.
- [x] L2.3 Verify minimal-feature installation and optional-dependency absence; record release evidence without upgrading planned features to supported.
  - All four 5f03f28 wheels passed installed byte/RECORD, exact legal payload and zero-runtime-dependency checks. Receipts retain the 29-package minimal native closure and exact supported runner/interpreters. Actual wheel/sdist metadata omits the optional aggregate licence fields and declares all three legal files. Planned capabilities remain unqualified.

## Phase 3 — Conditional consolidation

- [x] L3.1 Inventory unique code, workbooks, datasets, research and citations in hwcc, cobra-costing, tutorial_microcosting_genomics and checklist_microcosting; verify current repository status.
  - Bounded authenticated inspection covered current trees and relevant retained branches. Public-safe findings preserve restricted details and establish that no candidate can be treated as empty or fully migrated.
- [x] L3.2 Preserve mchs, workforce and genomics as domain owners; retain voi_sequencing_costs as a research consumer and the maintained CareOps module as its operational owner.
  - [Owner boundaries and pinned public sources](../../../docs/release-consolidation.md) record this disposition.
- [-] L3.3 Prepare successor links and migration/recovery evidence for any selected archive; execute an archive only under its subsequently authorised scope.
  - No external archive is selected. Existing owner links are retained; no cutover, deletion or repository archival is performed.
- [-] L3.4 Verify consumer reproduction and preserved scholarly/source assets before removing duplicated machinery or recording an archive as complete.
  - No machinery removal or external archive is selected. The qualified workforce/manual-extraction subset does not establish full reproduction, rights or successor behaviour for those external archive candidates.

## Review, fixes and archival

- [x] L4.1 Review the implementation against the original acceptance criteria, apply concrete fixes and retain exact-source verification.
  - The earlier five findings and integration null-state fix remain covered. All 64 release-control tests and Ruff pass. Independent notice, integration and documentation reviews found no material defect. The original acceptance section is unchanged; completed source-specific native/artifact checks are recorded under L1.3/L1.4.
- [!] L4.2 Archive this track after all mandatory acceptance criteria have evidence.
  - Archival is already authorised. Channel/account choices and the queued central security execution remain outstanding; trusted-main provenance follows eligible main-branch qualification. Ordinary exact-source hosted results and bounded provider acceptance are complete. Do not weaken the remaining criteria to obtain an archive marker.

## Evidence record

See [execution and review evidence](evidence.md) and the
[current handoff receipt](../../../docs/release-handoff-2026-11-15.md). Candidate reports bind actual
source, artifacts, platform, methods and synthetic data versions; they do not
establish scientific validity or registry entitlement. Provider and source scope
remain separately bounded by their owners' records. Update [metadata](metadata.json), [track index](index.md) and
[registry](../../tracks.md) together when status changes.
