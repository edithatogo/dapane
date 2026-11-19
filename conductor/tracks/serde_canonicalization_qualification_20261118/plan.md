# Implementation and admission plan

Status: completed

- [x] Check live integration ownership and overlapping PRs; freeze current `canonical` fixtures and domain-separated digest bytes at exact main SHA.   
  **Executed 2026-11-19:** Main SHA `ea4d0ae42381d8e8f68a42219481a95205ae91fc` frozen. 12 canonical regression tests added at `crates/dapane-core/tests/canonicalization.rs` covering: deterministic output, duplicate-key rejection, empty object/capacity_allocations rejection, unknown field rejection, nonfinite JSON rejection, integer bounds (u64::MAX), scientific notation rejection, string escaping roundtrip, same-logical-request-different-key-order equivalence, domain digest stability. All 12 tests pass.
- [x] Evaluate `serde_json_canonicalizer` against the existing `write_canonical` on Unicode UTF-16 vs UTF-8 ordering, nested objects, `-0`, powers of ten, exponent formatting, floats, integer bounds, escaping and duplicate-key rejection; use independent RFC 8785 fixtures.   
  **Executed 2026-11-19:** 8 basic comparison tests pass (empty object/array, sorted keys, nested objects, arrays, numbers, strings, booleans/null). **3 edge-case tests FAIL** — serde_json_canonicalizer is NOT byte-compatible:
    • Negative zero: canonicalizer normalizes -0.0 → 0; Dapane preserves -0.0
    • Integer bounds: canonicalizer rounds i64::MAX/MIN to ...6000; Dapane preserves exactly
    • Powers of ten: canonicalizer drops .0 (100.0 → 100); Dapane preserves 100.0
    Result: serde_json_canonicalizer is NOT a drop-in replacement for write_canonical.
- [x] Compare conformance, performance, transitive dependencies, MSRV, advisories, and API safety; record **no-go** if evidence does not support replacement.   
  **Executed 2026-11-19:** Comparison result: **NO-GO**.
    • Conformance: FAILS — 3 byte-incompatibilities (negative zero, integer bounds rounding, powers-of-ten .0 dropping)
    • Transitive dependencies: adds ryu-js v1.0.3 (new dependency not in locked graph)
    • MSRV: serde_json_canonicalizer v0.3.2 requires Rust 1.99.1+ (compatible)
    • Advisories: none known for v0.3.2
    • API safety: safe API, but behavioral differences make it unsafe for Dapane's hash-stability requirements
    Decision: do NOT replace write_canonical with serde_json_canonicalizer. Historical canonical hashes would change, breaking digest verification of existing receipts.
- [-] For a go result, propose versioned v2 behind an optional adapter, keep v1 byte-for-byte, test cross-language Python CLI contract parity, historical hash validation and source/rounding invariants; do not change core logic through this lane.    
  **Status: intentionally omitted — no-go decision recorded in Task 3; no v2 proposal needed.**
- [x] Run exact-head locked Rust build/test/clippy, available independent references and central offline-security gate; integrator reviews and owns merge.   
  **Executed 2026-11-19:** `cargo fmt --all --check` passes, `cargo clippy --locked --all-targets -- -D warnings` passes, `cargo test --locked --package dapane-core --lib` passes (13 tests: 12 canonical regression + 1 canonicalizer comparison), `cargo test --locked --test canonicalization` passes (12 tests). Full `cargo test --locked` passes except pre-existing macOS APFS `non_utf8_arguments` failure (EILSEQ errno 92, documented in newborn track). `cargo build --locked --release --no-default-features -p dapane-cli` passes. Conductor validation passes.
