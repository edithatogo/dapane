# Repository instructions

## Project context

Start at [conductor/index.md](conductor/index.md). Resolve work through
[conductor/tracks.md](conductor/tracks.md), then the selected track's index,
specification, plan and metadata. Dapane is currently a planning repository;
do not describe planned runtime, language or deployment capabilities as delivered.

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
- Current check: `python3 scripts/validate_conductor.py`.

Runtime test commands must be added when the runtime exists; an empty test suite
or a documentation-only check cannot qualify a numerical implementation.
