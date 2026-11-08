# Implementation plan: R and Julia bindings

Status: new

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Shared boundary preparation

- [ ] B1.1 Select supported host versions and exact numeric/error representations from the core fixtures; record capability and platform scope.
- [ ] B1.2 Verify which operations are available to each host without widening the core or copying formulas.

## Phase 2 — R branch — independent of C ABI

- [ ] B2.1 Create the thin extendr wrapper and rextendr package around direct Rust calls.
- [ ] B2.2 Implement missing-value, ownership/lifetime and main-thread API handling with exact quantity/rate transport.
- [ ] B2.3 Build and install the source package in a clean R environment; run shared fixtures and host-specific negative cases.

## Phase 3 — C ABI and Julia branch

- [ ] B3.1 Specify and implement the versioned ABI, owned-buffer/handle lifecycle, error transport and panic boundary.
- [ ] B3.2 Exercise a minimal C consumer with allocation/free, malformed input and version-mismatch cases before binding Julia.
- [ ] B3.3 Implement Julia direct calls, GC preservation and target-native artifact resolution; use BinaryBuilder/JLL packaging when selected for release.
- [ ] B3.4 Install the Julia package against its packaged library and verify shared fixtures, lifetime cases and artifact resolution.

## Phase 4 — Independent publication readiness

- [ ] B4.1 Record separate R, ABI and Julia compatibility/maturity states, reproduction commands and deprecation/rollback rules.
- [ ] B4.2 Verify each selected release surface independently; do not delay a qualified R capability for unrelated Julia/C ABI work.

## Evidence record

No runtime acceptance evidence is recorded by this initial plan.
Update [metadata](metadata.json), [track index](index.md) and [registry](../../tracks.md) together when the status changes.
