# Rust dependency rationalisation — dapane (2026-11-13)

**Status:** proposal and review contract, reconciled with the existing PR #2 runtime
on 14 November 2026. This document is not runtime or benchmark evidence; see
[runtime verification](../docs/runtime-verification.md) for the candidate's scope
and dated results.

## Repository-specific decisions

- **Historical observation (13 November, main):** Conductor and scripts were present without a Cargo workspace. PR #2 already contained the candidate runtime at `14b34896b983e53fc053b405ff800504b2add678`; the integration preserves that work rather than starting another kernel.
- **Existing owned core:** Serde provides versioned valuation ledgers and stable interchange; bounded exact rational arithmetic and unit constraints are implemented. The core already has a typed `DapaneError`; adopting Thiserror requires a concrete benefit, not a second error system. Review the locked graph in [the dependency inventory](../docs/dependencies.json) before changing dependencies.
- **Binding:** PyO3 is in a separate Python adapter. R/Julia adapters remain independent of core and are still planned.
- **Evaluate later:** Polars for optional large workforce/resource tabulations, Criterion for benchmark fixtures, Proptest for allocation conservation, sum reconciliation, rounding and monotonicity.
- **Reject as new direct base-core dependencies:** Tokio, Reqwest, SQLx, Ratatui, Crossbeam, Syn/Quote and Rayon without a concrete adapter/workflow or proven benefit. Existing transitive Syn/Quote use by derive/binding macros is recorded in the inventory; this is not a requirement to remove those transitive dependencies.
- **Scientific guard:** physical resources, weighted activity, tariffs, payments, financing and opportunity costs must remain distinct; do not introduce binary floating-point arithmetic for monetary rules.

## Evidence and release gate
1. Discover actual source, package boundary, MSRV, lockfile, existing tests and Conductor ownership; avoid speculative dependencies.
2. For runtime behaviour, write failing contract tests before implementation, run targeted and full suites; preserve stable schemas, errors, CLI semantics and deterministic outputs.
3. Record `cargo tree -d`, feature selections, security/licensing/advisory reviews, transitive dependency cost and rollback before accepting an adoption.
4. For performance changes, benchmark identical inputs and correctness/invariance oracles; do not claim improvements without measurements.
5. This document is a planning entry, NOT proof of compilation, hosted CI or scientific validation; update status only after a revision-bound receipt.
