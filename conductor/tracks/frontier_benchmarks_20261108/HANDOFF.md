# Current bounded handoff — 15 November 2026

**The five formatting failures are fixed and the static lane passes on
`7137bb5e87b7e79e8c780e9c0576434606072065`.** See the
[quality follow-up](quality-followup-20261115.md) and
[derived exact-source receipt](evidence/quality-20261115/qualification-summary.json).

Local and hosted acceptance each passed 23 tests, the same-source offline build,
the fixed 24-comparison protocol and bundle verification. The downloaded hosted
artifact passed source/file identity review. The initial shared registry and
hosted invocation requests below have been fulfilled by the integrator.

The documentation revision carrying this record receives separate exact-head
qualification. Its final SHA and new execution receipt are pinned in
[PR #24](https://github.com/edithatogo/dapane/pull/24) and handed to
[coordination PR #20](https://github.com/edithatogo/dapane/pull/20).
The sole integrator remains chat `6af8e445-ffd4-83ec-8e51-ff6b596f11b1`.

Offline security remains queued, not passed. PR #20's independent privacy
findings, the PR #17 receiving-tree provenance review and all release/publication
holds remain open. Retain complete hosted artifacts before their stated expiry.
No broader capability, within-request incremental engine, frontier or empirical
claim is made.

## Historical initial handoff — preserved as originally published

The following record describes the initial publication and its then-unexecuted
head. Its blocked/unexecuted statements are historical; they are not the current
formatting-source result. Failed history is retained without relabelling.

# Independent static benchmarks — integrator handoff

Lane: **Dapane — Independent static benchmarks**. Scope: F1/F2.1–2 only.
Status: implementation published as a draft; exact-head acceptance blocked.

## Identities and ownership

- Runtime/main base: `e34f87c9df39a2132fecee142431cdeefb732471`.
- Base tree: `c07a6b2589b9d665f619f5d977d66e513180bab4`.
- Original local protocol: `b9485ef60799ed0a809d9c416c8b984065c7590e`.
- Earlier locally tested counterpart: `5cc42f41d1713afab9348d781a38717d515b6b75`.
- Published implementation: [`a6ccbacf458cd9785397b0771052d5e8ca29de7d`](https://github.com/edithatogo/dapane/commit/a6ccbacf458cd9785397b0771052d5e8ca29de7d).
- Implementation tree: `62e2bde1367a6784839cfbd69c5aa53a39f1b7a4`.
- This follow-up handoff commit changes documentation/metadata only; its exact
  final head is pinned in the PR description. Implementation-source identity above
  is retained independently of the later documentation commit.
- Owned paths: this track and `benchmarks/static/`.
- Sole integrator/release owner remains the existing release-assurance lane
  (chat `6af8e445-ffd4-83ec-8e51-ff6b596f11b1`).

The initial live inspection found main at the above SHA, only release PR #17
open, and no benchmark branch/PR. The later ownership map in PR #20 reserves
`benchmarks/static/`; this publication conforms to that path. No duplicate worker
was created. Other repositories, shared core/CLI/Python, schemas, fixtures,
root Cargo/lock/toolchain, CI and central Conductor records remain unchanged.

## Delivered interface

The experiment wraps CLI `evaluate` and `evaluate-intervals`. Complete requests
are the cache unit. This preserves every within-request allocation dependency
without inferring a partial dependency graph. All changed values still come from
Rust. Cached and recomputed **complete report bytes** must agree.

The oracle is a separate, restricted Python Fraction implementation with
hand-derived literals. It covers source lines, half-even, conserving allocations,
objects, provenance/digests and explicit uniform-day intervals. It is test
evidence, not a production pricing implementation or independent human review.

The 24-case mutation inventory separates native contract rejection from omitted
or untrue source facts. The timing protocol covers 8/32 independent requests,
twelve update scenarios and five measured pairs after one warmup pair.

## Executed observations and limits

The [observation record](../../../benchmarks/static/evidence/local-observations.json)
retains commands and outcomes. Before environment loss:

- A locked, offline Rust 1.99.1 CLI build completed.
- The earlier local suite passed 21 tests after two diagnostic-expectation
  corrections; all 24 case expectations then passed.
- All twelve cache scenarios at eight requests matched full native reports
  byte for byte and passed the independent arithmetic/provenance checks.
- All twelve contract defects were rejected; all seven valid controls were
  accepted. All five source-truth defects were accepted, an explicitly retained
  null detection result.
- Accepted per-generated-segment half-even was retained: two 0.005 segments sum
  to rounded 0.00; two 0.015 segments sum to rounded 0.04.

The original raw mutation artifact, binary digest and local commits became
inaccessible before upload. They are not represented as a complete durable bundle.
The published code was reconstructed and its namespace/fixture locators changed.
Its exact head, 32-request comparisons, paired timings, memory observations,
build-receipt runner, bundle verifier and two additional tests are **unexecuted**.
There is no performance, frontier, empirical or release qualification claim.

## Concrete shared-change requests

| Integrator-owned path | Requested change |
| --- | --- |
| `conductor/tracks.md` | Change only this track's marker/status from `[ ] / new` to `[~] / in_progress`, preserving all other owners' current entries. Until then the strict registry check is expected to fail. |
| `.github/workflows/runtime.yml` or a suitable shared qualification job | After building the CLI and installing the existing pinned tooling, run the benchmark unittest command and Ruff commands below. The present job's explicit tooling selection does not discover this namespace. |
| Shared qualification artifact collection, if accepted | Run the fixed protocol against the exact built CLI and retain the result/build receipts as artifacts. Keep the benchmark optional for unrelated release capabilities and preserve all current gates. |

No shared API, schema, Cargo, lockfile, dependency or production evaluator change
is requested. No central file is edited by this lane. Do not reinterpret a green
existing job as evidence that these new tests executed.

## Exact-head continuation

Use a clean checkout of the final published head. First restore a usable execution
environment; no new infrastructure or credential change is authorised here.
[Reproduction commands](../../../benchmarks/static/README.md) are provided for:

1. Locked offline CLI build plus binary/source receipt.
2. `DAPANE_BENCH_CLI=<exact-cli> python3 -m unittest discover -s benchmarks/static/tests -v`.
3. `ruff check benchmarks/static` and `ruff format --check benchmarks/static`.
4. The paired runner and offline bundle verifier, retaining failures and nulls.
5. Integrator registry reconciliation, Conductor validation, applicable hosted
   checks and exact-head review.

Address any reconstruction/formatting defect in the lane namespace, rerun the
affected acceptance, then update F2.1/F2.2 only with executed evidence.
The original broader acceptance criteria remain intact. F2.3–5 and F3 are open.
No merge, release publication, gate waiver or Power Platform work is performed.

## Publication verification

The GitHub tree was read back and all **50 implementation/track blobs** were
checked against the authored UTF-8 content by Git blob SHA1 (with standard empty
and `abc` digest controls). Changed blob paths exactly matched the two owned
namespaces. All production/shared blobs equal the pinned main tree. Thirty JSON
documents parsed, all 24 listed fixtures exist, and the deliberate duplicate-key
negative fixture retains both keys. These are source-transfer/scope checks, not
Python/Rust execution or a substitute for the blocked acceptance run.

See [publication receipt](publication-receipt.json). No native report, timing,
memory or passing final-head test evidence has been manufactured.
