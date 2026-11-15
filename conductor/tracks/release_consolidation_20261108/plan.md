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
  - The d37575ec hosted baseline passed all four dual builds, advisory/licence checks, three SBOMs and the aggregate matrix. The main-only attestation route is configured. New notice/provider artifacts require the next exact-source run; the central offline security job remains a separate unexecuted gate.
- [~] L1.4 Verify a clean build and installed-consumer reference runs for every advertised target; retain exact commands and artifact identities.
  - At d37575ec all four hosted interpreters passed 133 installed tests each, independent references and interval checks. Existing provider qualification is merged and archived. The revised release workflow makes aggregate success depend on the existing verifier consuming the exact release CLI/wheel. Fresh execution must qualify the changed notice bytes and reusable path.

## Phase 2 — Operational quality

- [~] L2.1 Measure representative throughput/memory and document numerical, scale and platform limits; add acceleration only through its own parity/performance evidence.
  - The 10/1,000/5,000-row benchmark passed on both historical local source 354df1 and hosted d37575ec. Raw timings and peak child RSS retain their source/host identity. Re-run the changed candidate; no acceleration, empirical or cross-host claim is added.
- [x] L2.2 Document API/schema deprecation, source corrections, capability negotiation and rollback to previous qualified releases.
  - [Migration and recovery](../../../docs/release-migration.md) preserves schema/method/source/artifact identities and the qualified providers' canonical/legacy entry points and bounded historical replay. Broader cutover/removal remains outside this increment; no earlier public Dapane runtime is assumed.
- [~] L2.3 Verify minimal-feature installation and optional-dependency absence; record release evidence without upgrading planned features to supported.
  - All four hosted d37575ec wheels passed installed byte/RECORD and zero-runtime-dependency checks. Receipts retain the minimal native closure. Fresh notice-bearing artifacts require the same checks; planned capabilities remain unqualified.

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
  - The earlier five findings and integration null-state fix remain covered. This handoff adds authenticated notice generation and exact-release-artifact provider verification. All 64 release-control tests and Ruff pass; independent notice review found no material defect. Source-specific native/artifact qualification remains separately recorded under L1.3/L1.4.
- [!] L4.2 Archive this track after all mandatory acceptance criteria have evidence.
  - Archival is already authorised. Channel/account choices, fresh exact-source results and the queued central security execution remain outstanding. Provider acceptance is resolved within its recorded subset. Do not weaken the remaining criteria to obtain an archive marker.

## Evidence record

See [execution and review evidence](evidence.md) and the
[current handoff receipt](../../../docs/release-handoff-2026-11-15.md). Candidate reports bind actual
source, artifacts, platform, methods and synthetic data versions; they do not
establish scientific validity or registry entitlement. Provider and source scope
remain separately bounded by their owners' records. Update [metadata](metadata.json), [track index](index.md) and
[registry](../../tracks.md) together when status changes.
