# Repository instructions

## Project context

Start at [conductor/index.md](conductor/index.md). Resolve work through
[conductor/tracks.md](conductor/tracks.md), then the selected track's index,
specification, plan and metadata. Dapane has a bounded Rust/CLI/Python candidate;
read [the implemented contract](docs/contract-v0.1.md) and
[verification](docs/runtime-verification.md) before describing capabilities.
For capacity work, also read [contract 0.2](docs/contract-v0.2.md) and
[its scoped verification](docs/genomics-capacity-verification.md).
Do not describe planned provider, language or deployment capabilities as delivered.

## Working practices

- Inspect git status and preserve unrelated work before editing.
- Keep requirements, design decisions and implementation plans consistent with the
  actual change. Use the existing track before creating overlapping work.
- Use the task markers and evidence conventions in
  [conductor/workflow.md](conductor/workflow.md).
- Prefer established dependencies when they meet the numerical and source-rights
  requirements. Keep adapters out of the minimal Rust core.
- Keep arithmetic in Rust; wrappers and user interfaces must not reproduce it.
- Treat reference outputs, reporting completeness, computational verification and
  empirical validation as distinct evidence.
- Keep real patient data, credentials and restricted source artefacts out of this
  public repository. Use explicitly labelled synthetic fixtures.
- Verify the affected behaviour and the documentation check proportionately.
  Record actual commands and outcomes; do not turn planned checks into evidence.
- Keep changes bounded and reviewable. Use the user's existing authorisation for
  routine reversible work; do not introduce per-task approval paperwork.

## Navigation and checks

- Product and scope: [conductor/product.md](conductor/product.md).
- Numerical and API design: [conductor/design.md](conductor/design.md).
- Dependency policy: [conductor/tech-stack.md](conductor/tech-stack.md).
- Domain/provider boundaries: [conductor/ecosystem.md](conductor/ecosystem.md).
- Style guides: [conductor/code_styleguides/index.md](conductor/code_styleguides/index.md).
- Context check: `python3 scripts/validate_conductor.py`.
- Native checks: `cargo fmt --all --check`, `cargo clippy --locked --all-targets -- -D warnings`, `cargo test --locked`.
- Public-contract check: `python scripts/validate_contract.py --cli target/release/dapane`.
- Python: build/install a native wheel and run `tests/python` from outside the checkout, as in [the quickstart](docs/quickstart.md).

Keep the installed-artifact matrix and independent synthetic references current.
An empty test suite or documentation-only check cannot qualify a numerical implementation.
