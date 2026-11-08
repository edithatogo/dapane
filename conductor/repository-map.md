# Repository map

## Observed starting point

On 8 November 2026 the GitHub repository `edithatogo/dapane` was public and empty,
with no branch commits, instructions, manifests, licence, source, tests or existing
Conductor records. Its configured default branch was `main`. No content needed
migration or deletion.

Current repository areas:

| Path | Current responsibility |
| --- | --- |
| `README.md` | Entry point and honest maturity statement |
| `AGENTS.md` | Repository-specific navigation and working practices |
| `conductor/index.md` | Authoritative project-context index |
| `conductor/*.md` | Product, requirements, architecture, decisions, workflow and roadmap |
| `conductor/code_styleguides/` | Rust, Python/FFI and document conventions |
| `conductor/tracks/` | Coherent implementation/research specs, task plans and metadata |
| `conductor/archive/` | Archive policy; no archived tracks at setup |
| `scripts/validate_conductor.py` | Dependency-free structural and consistency check |
| `.github/workflows/conductor.yml` | Read-only documentation CI |
| `Cargo.toml`, `Cargo.lock`, `rust-toolchain.toml` | Native workspace and pinned toolchain/dependency graph |
| `crates/dapane-core/` | Exact contract, validation, valuation, allocation and deterministic digests |
| `crates/dapane-cli/` | Offline file/stdin JSON interface and CLI boundary checks |
| `crates/dapane-python/`, `python/dapane/`, `pyproject.toml` | Thin PyO3 extension and Python exact-value transport |
| `schemas/0.1/` | Request, report, error and shared JSON schemas |
| `fixtures/` | Five synthetic inputs and independently authored expected results |
| `tests/python/` | Installed-wheel consumer, transport, error and concurrency checks |
| `scripts/validate_contract.py` | Structural checks and independent CLI result/digest verification |
| `scripts/benchmark_cli.py` | Bounded synthetic valuation/allocation measurements |
| `docs/` | Implemented contract, provider review, quickstart, compatibility and runtime evidence |
| `.github/workflows/runtime.yml` | Native and four-interpreter installed-wheel CI |

The first runtime candidate is implemented and locally built; its precise scope
is recorded in [the contract](../docs/contract-v0.1.md) and
[verification](../docs/runtime-verification.md). Build outputs remain outside
version control. There is no registry release or deployment, and provider
adapters, R/Julia, reporting and process execution remain planned.

## Source-of-truth boundaries

Dapane owns this framework's requirements, architecture and coordinated roadmap.
The original MCHS design is a source snapshot; MCHS retains its domain adapter and
calculator ownership. UOGTO owns semantics and reporting-profile mappings;
standards_check owns original reporting-source records. See
[ecosystem](ecosystem.md) for exact reviewed snapshots and readiness.

## Keeping this map current

Update this file when implementation areas or public entry points are added or
removed. Record actual build/test commands in the workflow and affected track.
Do not replace executable discovery with a speculative exhaustive file tree.
