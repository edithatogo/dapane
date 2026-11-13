# Rust dependency rationalisation — dapane (2026-11-13)

**Status:** proposal and review contract; no code adoption, runtime verification or benchmark result is claimed here.

## Repository-specific decisions

- **Verified:** Dapane repository currently has Conductor and scripts only, not a Rust Cargo workspace; do not claim or install runtime packages before the core is implemented.
- **Future owned core:** Serde for versioned valuation ledgers and stable interchange; Thiserror for typed economic/costing errors; exact decimal/rational arithmetic and unit constraints must be preserved.
- **Binding:** PyO3 only in a separate Python adapter once the Rust calculation contract is stable. R/Julia adapters remain independent of core.
- **Evaluate later:** Polars for optional large workforce/resource tabulations, Criterion for benchmark fixtures, Proptest for allocation conservation, sum reconciliation, rounding and monotonicity.
- **Reject for base core:** Tokio, Reqwest, SQLx, Ratatui, Crossbeam, Syn/Quote and Rayon without a concrete adapter/workflow or proven benefit.
- **Scientific guard:** physical resources, weighted activity, tariffs, payments, financing and opportunity costs must remain distinct; do not introduce binary floating-point arithmetic for monetary rules.

## Evidence and release gate
1. Discover actual source, package boundary, MSRV, lockfile, existing tests and Conductor ownership; avoid speculative dependencies.
2. For runtime behaviour, write failing contract tests before implementation, run targeted and full suites; preserve stable schemas, errors, CLI semantics and deterministic outputs.
3. Record `cargo tree -d`, feature selections, security/licensing/advisory reviews, transitive dependency cost and rollback before accepting an adoption.
4. For performance changes, benchmark identical inputs and correctness/invariance oracles; do not claim improvements without measurements.
5. This document is a planning entry, NOT proof of compilation, hosted CI or scientific validation; update status only after a revision-bound receipt.
