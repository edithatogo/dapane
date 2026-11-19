# Implementation plan: R and Julia bindings

Status: blocked

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Shared boundary preparation

- [x] B1.1 Select supported host versions and exact numeric/error representations from the core fixtures; record capability and platform scope.
- [x] B1.2 Verify which operations are available to each host without widening the core or copying formulas.

## Phase 2 — R branch — independent of C ABI

- [x] B2.1 Create the thin extendr wrapper and rextendr package around direct Rust calls.
- [x] B2.2 Implement missing-value, ownership/lifetime and main-thread API handling with exact quantity/rate transport.
- [x] B2.3 Build and install the source package in a clean R environment; run shared fixtures and host-specific negative cases.

## Phase 3 — C ABI and Julia branch

- [~] B3.1 Specify and implement the versioned ABI, owned-buffer/handle lifecycle, error transport and panic boundary.
- [x] B3.2 Exercise a minimal C consumer with allocation/free, malformed input and version-mismatch cases before binding Julia.
- [ ] B3.3 Implement Julia direct calls, GC preservation and target-native artifact resolution; use BinaryBuilder/JLL packaging when selected for release.
- [ ] B3.4 Install the Julia package against its packaged library and verify shared fixtures, lifetime cases and artifact resolution.

## Phase 4 — Independent publication readiness

- [x] B4.1 Record separate R, ABI and Julia compatibility/maturity states, reproduction commands and deprecation/rollback rules.
- [ ] B4.2 Verify each selected release surface independently; do not delay a qualified R capability for unrelated Julia/C ABI work.

## Evidence record

[Current owner evidence](owner-quality-20261115.md) and its
[structured receipt](owner-quality-20261115.json) distinguish each tested source.
The received integrator source `8716c423f15c6449940df902fbabfab870d38f4d` passed installed R
and native C cases in hosted execution, with two owner quality failures retained.
B2.3 and the bounded B3.2 consumer exercise are complete for that recorded Linux
matrix. They do not establish total ABI or release qualification.

The correction source `988e41158a17d6613006b9bffe59cd59a3aa9cca` fixes only lint precedence and
Python formatting. Local exact-source quality checks and ordinary native C
acceptance passed; the local sanitizer attempt failed under traced execution.
The correction source then passed all 41 hosted binding commands, including
installed R and ASan/UBSan C acceptance. Final-head execution remains separately
source-bound. B3.1 stays partial pending
unsafe-boundary acceptance. B3.3/B3.4 and B4.2 remain open.

The integrator accepted `bindings/polyglot/`, reconciled the blocked registry and
added standalone CI. Those shared requests are no longer blockers. Original
recovery/outage evidence remains in [verification](verification.md).

## Bounded owner quality follow-up — 2026-11-15

- [x] B5.1 Correct ABI lint-group precedence and apply pinned Python formatting without changing behaviour or weakening gates.
- [x] B5.2 Re-run exact-source quality/native acceptance and independently inspect the semantic diff and shared-file preservation.
- [x] B5.3 Record source/artifact identities, actual outcomes and remaining ABI/release requirements in the existing handoff.
