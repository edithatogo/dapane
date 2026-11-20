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

- [x] B3.1 Specify and implement the versioned ABI, owned-buffer/handle lifecycle, error transport and panic boundary.
  The integration reviewer examined the Rust FFI, registry lifecycle and C header independently of the implementation lane. The source review and instrumented C host checks passed for ABI v1. [Review and host evidence](verification.md#macos-host-and-abi-review)
- [x] B3.2 Exercise a minimal C consumer with allocation/free, malformed input and version-mismatch cases before binding Julia.
- [x] B3.3 Implement Julia direct calls, GC preservation and target-native artifact resolution; use BinaryBuilder/JLL packaging when selected for release.  
  **Executed 2026-11-20:** `julia --project=bindings/polyglot/julia -e 'using Pkg; Pkg.test()'` passed 20 tests on Julia 1.13.4 against the release `libdapane_abi.dylib` built from this checkout. Workforce and interval JSON match the same-checkout CLI bytes. The caller preserves the request across the foreign call, copies the result, frees the handle, and rejects a library name for another platform. `GC.gc()` ran after the input buffer was overwritten. BinaryBuilder/JLL packaging is not selected.
- [x] B3.4 Install the Julia package against its packaged library and verify shared fixtures, lifetime cases and artifact resolution.  
  **Executed 2026-11-20:** `prepare_cases.py` wrote 24 cases. `julia --startup-file=no bindings/polyglot/julia/test/installed.jl` developed a staged copy outside the checkout, with `libdapane_abi.dylib` under that copy's `artifacts/`. The installed package resolved that file with no explicit path. All 24 cases matched the CLI bytes, including core errors, and the first success survived input overwrite plus `GC.gc()`. The install assertions were 2 artifact checks and 44 case checks. This is one host library copied beside the package, not a BinaryBuilder/JLL artifact.

## Phase 4 — Independent publication readiness

- [x] B4.1 Record separate R, ABI and Julia compatibility/maturity states, reproduction commands and deprecation/rollback rules.
- [!] B4.2 Verify each selected release surface independently; do not delay a qualified R capability for unrelated Julia/C ABI work.  
  The installed R 4.6.2 candidate passed 24 parity cases on macOS arm64. The Julia candidate also has installed parity. Registry channels, release accounts and any JLL distribution remain unselected under L1.2.

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
source-bound. B3.1 passed the separate integration review. B4.2 is blocked on release selection.

The integrator accepted `bindings/polyglot/`, reconciled the blocked registry and
added standalone CI. Those shared requests are no longer blockers. Original
recovery/outage evidence remains in [verification](verification.md).

## Bounded owner quality follow-up — 2026-11-15

- [x] B5.1 Correct ABI lint-group precedence and apply pinned Python formatting without changing behaviour or weakening gates.
- [x] B5.2 Re-run exact-source quality/native acceptance and independently inspect the semantic diff and shared-file preservation.
- [x] B5.3 Record source/artifact identities, actual outcomes and remaining ABI/release requirements in the existing handoff.
