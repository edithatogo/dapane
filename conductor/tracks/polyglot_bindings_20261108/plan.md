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
- [!] B2.3 Build and install the source package in a clean R environment; run shared fixtures and host-specific negative cases.

## Phase 3 — C ABI and Julia branch

- [~] B3.1 Specify and implement the versioned ABI, owned-buffer/handle lifecycle, error transport and panic boundary.
- [!] B3.2 Exercise a minimal C consumer with allocation/free, malformed input and version-mismatch cases before binding Julia.
- [ ] B3.3 Implement Julia direct calls, GC preservation and target-native artifact resolution; use BinaryBuilder/JLL packaging when selected for release.
- [ ] B3.4 Install the Julia package against its packaged library and verify shared fixtures, lifetime cases and artifact resolution.

## Phase 4 — Independent publication readiness

- [x] B4.1 Record separate R, ABI and Julia compatibility/maturity states, reproduction commands and deprecation/rollback rules.
- [ ] B4.2 Verify each selected release surface independently; do not delay a qualified R capability for unrelated Julia/C ABI work.

## Evidence record

The [verification record](verification.md) distinguishes executed local evidence
from the reconstructed candidate's pending exact-head checks. The local installed
R package passed 24 synthetic cases, host rejection, GC stress and two independent
R processes before the executor disconnected. Five ABI Rust unit tests and a
release build passed; the native C consumer did not run. Julia remains gated.

B2.3 stays blocked until the published source is rebuilt and installed. B3.1 is a
proposed implementation with historical Rust unit evidence; B3.2 requires the
actual native consumer and source-bound artifact hashes. B3.3/B3.4 remain pending.
B4.1 records separate maturity/rollback states; B4.2 remains outside this bounded,
non-publication handoff.

The lane owns `bindings/polyglot/` and this track only, selected after inspecting
main at `e34f87c9df39a2132fecee142431cdeefb732471`. The subsequently inspected
coordination PR #20 reserves alternate binding roots; reconcile this existing
dedicated path claim through the integrator, without duplicate implementations.

The integrator must change the central registry row to `[!]` / `blocked`.
This lane intentionally does not edit that shared file. The Conductor consistency
gate remains mandatory and is expected to reject the unreconciled row.
