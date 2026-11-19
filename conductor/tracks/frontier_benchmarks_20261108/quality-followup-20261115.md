# Static benchmark quality follow-up — 15 November 2026

The five received Python formatting failures are fixed at
[`7137bb5e87b7e79e8c780e9c0576434606072065`](https://github.com/edithatogo/dapane/commit/7137bb5e87b7e79e8c780e9c0576434606072065).
Its tree is `e8935161f9e2c42c5adb2013feabf8feab45b756`.
Local execution and the existing hosted standalone workflow passed on this
exact source. This is bounded synthetic-lane qualification, with the upstream
holds below still open.

The documentation commit carrying this record is a separate source revision.
Its final SHA, fresh hosted execution and read-back scope checks belong in the
head-specific [PR #24 handoff](https://github.com/edithatogo/dapane/pull/24).
No earlier result is relabelled as execution of that later head.

## Received failure and repair

The fresh inspection found PR #24 at
`237ddb238997b0babe12266cb7775207c597dfd4`, main at
`e34f87c9df39a2132fecee142431cdeefb732471`, and the existing owner intact.
The integrator's [immutable receipt](https://github.com/edithatogo/dapane/blob/497cd6472b1eb282ea6bd79271a7c76a881e9cec/conductor/roadmap-evidence-2026-11-15/attempt-2/pr24/qualification.json)
records a failed overall result: native build, 23 tests, fixed protocol and
verification passed, but Python formatting failed.

Pinned Ruff 0.17.4 reproduced exactly five failures. Its output was applied to
`build.py`, `oracle.py`, `run.py`, `verify.py` and
`tests/test_bundle_gate.py` under `benchmarks/static/`.
The [reproduced failed diff](evidence/quality-20261115/received-237ddb2-format-failure.log)
is retained. The older initial diagnostic failures, reconstruction history and
unexecuted publication observations remain unchanged.

All five edited files have identical Python syntax trees and COMMENT tokens
before and after formatting. Each edited file equals Ruff's formatting of the
received Git blob. The [source review](evidence/quality-20261115/source-review.json)
records these separately executed checks. No fixture, expected outcome, protocol,
cache rule, production source or shared qualification file changed.

## Executed checks on the formatting source

| Check | Local result | Hosted result |
| --- | --- | --- |
| Ruff 0.17.4 lint and formatting | Passed; all 14 Python files formatted | Passed |
| Same-source locked offline CLI build | Passed; fresh isolated target, Rust 1.99.1 | Passed |
| Benchmark acceptance suite | 23 passed | 23 passed |
| Fixed paired protocol | 24 comparisons passed | 24 comparisons passed |
| Saved-bundle verifier | 144 pairs, 70 distinct request/report checks, 24 mutations | Same counts passed |
| Conductor validation | Passed: 14 tracks, 12 requirements, 154 tasks | Passed |
| Conductor lifecycle regressions | 12 passed | Existing workflow passed |
| Shared qualification failure/provenance controls | 20 passed | 20 passed |
| Ordinary Runtime, installed providers, privacy, CodeQL | Not rerun locally for this formatting repair | Passed |

The [standalone run](https://github.com/edithatogo/dapane/actions/runs/43697346539)
passed all 15 required commands and its aggregate verifier. The
[command statuses](evidence/quality-20261115/hosted-7137bb5-command-statuses.log)
and [derived execution receipt](evidence/quality-20261115/qualification-summary.json)
retain exact source identities and observations. Local Python was 3.12.14;
the hosted lane used Python 3.12.16. These are separate executions.

Capacity was checked before compilation. The workspace had about 5 MiB available;
the isolated memory filesystem had 3.4 GiB available after copying the dependency
cache. The build used that isolated location. No existing work was deleted.

## Artifact review and complete-run retention

The downloaded hosted archive was checked against its API digest and byte count.
All **251** source-file SHA-256 values matched immutable Git blobs; all **22**
retained-file hashes and sizes matched. The shared receipt verifier and the
independent arithmetic bundle verifier both passed when rerun locally.
The local and hosted `inputs.json` and `reports.json` were byte-identical.
The hosted native executable also has the same digest as the received-head
hosted binary.

| Identity | Value |
| --- | --- |
| [Hosted artifact](https://github.com/edithatogo/dapane/actions/runs/43697346539/artifacts/14154424008) | `14154424008`, `roadmap-lane-static` |
| Archive | 774,796 bytes |
| Archive SHA-256 | `6887fd2fa4e2c99b300c049dc421a8623e28639f33c9e0fa32b59ee9f2adb3cd` |
| Raw qualification receipt SHA-256 | `6cba089615862161940e25404d6010ef58ff5e46854d2d87ba1def8c813f3b84` |
| Hosted native binary SHA-256 | `5eaab52309ff9162360a9c82dd1bded8e163118fd573ff45fb8dd607a334991c` |
| Recorded artifact expiry | 15 December 2026, 09:04:11 UTC |

The archive contains the complete inputs, reports, all timing pairs, build
receipt, qualification receipt, logs and native binary. This durable derived
handoff does not replace that archive. The integrator should retain its exact
bytes before expiry under the existing evidence/privacy process.

After these checks passed, the local execution environment disconnected. A
subsequent attempt to copy scratch evidence into track files did not execute.
The original raw local files are not claimed as durably saved. The hosted archive
remains available, and the tool-observed local results are recorded separately.
Documentation was then prepared through the repository connection; its final
head requires its own hosted execution.

## Nulls and limits

Both executions accepted all seven controls and rejected all twelve contract
violations. All five source-truth defects were accepted: **0/5 detected**.
Omissions, aliased duplicate identities, a wrong positive denominator and
consistent false declarations cannot be credited as native detection.

Complete cached and fully recomputed report bytes agreed. Per-generated-segment
half-even remains unchanged: two 0.005 segments produce 0.00; two 0.015 segments
produce 0.04. The experiment reuses complete independent requests and sends every
changed valuation through the unchanged CLI.

Both runs retained slower rows. The local run was slower for 8-request
`all_rates`, 32-request `cold` and 32-request `all_rates`; the hosted run
was slower for 8-request `cold`, 8-request `all_rates` and 32-request
`cold`. Exact descriptive ratios and result digests are in the receipt;
the complete artifact retains every row. These uncontrolled single-host
observations do not establish a general speed advantage.

Per-method memory, analyst effort, diagnosis/repair effort, external validity,
transportability and disclosure risk remain **null**. Whole-run RSS is retained
with its measured boundary. No frontier, empirical, clinical, human-adoption,
cross-platform or release claim follows.

## Review and integrator boundary

The review combined a separate mechanical source-equivalence check, an
implementation-owner diff review, independently computed artifact/source hashes,
the independent arithmetic oracle, and hosted execution of the unchanged
shared qualification controller. No second worker or independent human reviewer
was created. Independent human/integrator acceptance remains open.

The sole integrator remains **Dapane — Release assurance and consolidation**,
chat `6af8e445-ffd4-83ec-8e51-ff6b596f11b1`.

- Both observed offline-security jobs remain queued, **not passed**.
- [PR #20's privacy findings](https://github.com/edithatogo/dapane/blob/497cd6472b1eb282ea6bd79271a7c76a881e9cec/conductor/roadmap-evidence-2026-11-15/privacy-review.md)
  remain independent and blocking; this lane's passes do not clear them.
- The protocol runtime baseline remains `e34f87c`. Combining PR #17 requires
  the existing owner's reviewed receiving-tree provenance/baseline update and
  fresh qualification. The identity guard is unchanged.
- F1 and F2.1–2 are complete for this authorised synthetic static slice.
  F2.3–5 and F3 retain their broader open acceptance.
- Shared CI, registry, root manifests and other lanes remain owned by the
  integrator. No shared change, gate waiver, merge or release is performed.
