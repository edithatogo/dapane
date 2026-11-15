# Exact-source polyglot handoff

## Source and disposition

- Repository: [edithatogo/dapane](https://github.com/edithatogo/dapane).
- Implementation candidate:
  [`9904252c1e3a94f63ff5dd89c4e855a2ef617f4d`](https://github.com/edithatogo/dapane/commit/9904252c1e3a94f63ff5dd89c4e855a2ef617f4d).
- Candidate tree: `d82b6b4fa097018710f4288879d5fa99a93050a0`.
- Base/core: `e34f87c9df39a2132fecee142431cdeefb732471`.
- Branch: `feat/polyglot-r-abi-20261115`.
- Sole integration/release owner: the existing “Dapane — Release assurance and
  consolidation” workstream, represented by PRs #17 and #20.
- Disposition: **draft, blocked; no merge, release or publication authority is
  exercised by this lane**. The PR description identifies its final documentation
  head separately from the implementation commit pinned above.

All 27 files in the implementation tree were read back through the GitHub
connector and compared with the recovery payload. That verifies the persisted
source contents, not compilation or host acceptance. See
[verification](verification.md) for the executed/unexecuted distinction and
[plan](plan.md) for unchanged task identifiers.

## Delivered scope

Only `bindings/polyglot/` and this track are changed. The new R package calls the
unchanged core directly through extendr 0.9.0, with exact JSON, structured errors,
main-thread R use and independent source-package staging. The new standalone ABI
crate proposes v1 opaque result handles, length/copy/free symmetry, deterministic
transport statuses, bounded retained storage and panic containment. A native C
consumer and complete local reproduction command are supplied.

R is independent of C ABI, Julia and Python. Julia is absent because actual C
consumer qualification did not complete. No original core/CLI/Python/provider
manifest, schema, common fixture, root Cargo/lock/CI or root documentation file
is changed. Upstream repositories were read-only.

## Requests to the integrator

### 1. Reconcile the dedicated path claim

At initial tree/PR inspection, main had no binding namespace and only release PR
#17 was open. This lane chose `bindings/polyglot/`. Coordination PR #20 was
observed subsequently at `e615454c9f3f41f96e9e310f446d2440d98cf5eb`, with
`bindings/r/`, `bindings/cabi/` and `bindings/julia/` reserved to this same
owner. Please record the actual existing `bindings/polyglot/` claim in
`conductor/parallel-ownership.md`. No competing namespace is implemented.

### 2. Reconcile the registry, preserving the consistency gate

In the integrator-owned `conductor/tracks.md`, locate the row for track
`polyglot_bindings_20261108` (display name “R and Julia bindings”) and change:

| Column | Current | Requested |
| --- | --- | --- |
| Marker | `[ ]` | `[!]` |
| Status | `new` | `blocked` |

Retain that row's existing link and `RQ-09, RQ-02` requirement columns.

Track index, plan and metadata already agree on blocked. Run the existing
Conductor validator and lifecycle suite after reconciliation. An unreconciled
row is an expected gate failure, not a reason to suppress the validator.

### 3. Replay the exact source before accepting R or the ABI

The environment disconnected before the C consumer ran. Source and lane lockfiles
were reconstructed, so the published commit has no final-source execution result.
Historical R acceptance (24 cases plus host/GC/process checks), three packaging
tests, the R panic test/Clippy, and five ABI Rust tests/release build must not be
relabelled as results for this SHA.

The concrete Linux replay is:

```sh
bash bindings/polyglot/qualify.sh /absolute/new-qualification
```

It requires a clean checkout, R 4.5.0, Rust 1.99.1, Cargo, Python 3.11+, a C
toolchain and sanitizer support. The script itself is new/unexecuted and must
be reviewed/executed; it fails at missing tools, changed locks or failed checks.
Keep its source SHA, full log, exported symbols and artifact checksums.
The native library used by the C consumer must be exactly the library later
packaged for Julia. Only the same lane may proceed to Julia after this gate.

The optional crate workspaces build independently; no root workspace membership
change is required for local acceptance. If integrating them into the main
workspace is later preferred, that is an explicit integrator change with a new
lock and qualification record.

### 4. Add targeted hosted coverage and dependency/release accounting

Existing root Cargo checks do not traverse these standalone workspaces; root
CI success cannot qualify them. Add explicit R and ABI jobs through the shared
CI owner, retaining ordinary numerical, privacy and offline-security gates.
The smallest initial target is Linux x86_64, with the recorded host/tool versions.
Other operating systems/architectures, R versions and Julia/JLL targets stay
unqualified until their own installed evidence exists.

The R graph adds these exact registry packages beyond the relevant root graph:

| Package | Version |
| --- | --- |
| extendr-api | 0.9.0 |
| extendr-ffi | 0.9.0 |
| extendr-macros | 0.9.0 |
| lazy_static | 1.5.1 |
| paste | 1.0.15 |
| readonly | 0.2.14 |
| syn | 2.0.119 |

The shared core packages retain the main lock's versions/checksums. The ABI adds
no registry dependency beyond its core graph. Reconstructed lockfiles include
official registry checksums, but Cargo must validate them; no advisory pass is
inferred. Extend dependency/advisory/SBOM/notice accounting to both optional
manifests and their actual distributions. The vendored R install is local
qualification, not a declaration that publication rights/notices are complete.

Review the ABI's narrow unsafe pointer boundary separately from the core; no
core unsafe restriction or workspace gate is relaxed. The header documents valid
caller buffers, alignment, lifetime and non-overlap obligations, and the limits
of panic containment.

## Acceptance and rollback

B1 preparation and B2 wrapper implementation are delivered. B2.3 remains blocked
for the final installed candidate. B3.1 remains a proposed ABI implementation;
B3.2 is blocked until the native C consumer runs. B3.3/B3.4 (Julia) are pending.
B4.1 records independent maturity and rollback rules; publication readiness is
not complete.

The accepted numerical method remains unchanged, including the 150/60/90 newborn
reference and half-even rounding per generated interval segment. No empirical,
clinical, provider-wide or cross-platform claim follows from these fixtures.

Leave the PR draft/unmerged until the shared requests and exact-head checks are
satisfied. Rollback is to omit this optional namespace and keep the existing
Rust/CLI/Python interfaces. Preserve this evidence, the recovery source and any
recovered local `efbe2a310de4ba1f223649bcd094462a05e2222f` history; do not blanket
reset or prune it.
