# M1/M2 scoped review

This is the implementation owner's review, not an independent reviewer or a
security certification. No additional worker was created.

## Findings and source fixes

1. **Resource-source evidence gap.** The first implementation accepted a separate
   core resource-cost request without the richer rights/status declarations used
   by activity and Atlas imports. Added required `resource_sources`, exact
   source-identity matching, and rejection of absent, conflicting, duplicate or
   unreferenced declarations. Resource-cost transport is explicitly limited to
   core 0.1.
2. **Future observation gap.** A payment observation could have a date after the
   run's knowledge cutoff. Added an explicit rejection. Modelled payments retain
   their distinct named-model path.
3. **Test inheritance duplication.** Review tests initially inherited the original
   test methods. Extracted a diagnostic assertion base to avoid duplicated test
   counts. There are 34 authored test methods in the recovered candidate.
4. **Fixture rights ambiguity.** Replaced a real licence identifier used as dummy
   metadata with `SYNTHETIC-RIGHTS-FIXTURE`, explicitly fictional and not a
   licence grant.
5. **Empty resource-source type check.** Recovery review made the no-resource
   branch validate a supplied `resource_sources` collection even when empty or
   otherwise false-like.

The source fixes and their added tests are present. They have **not executed on
the recovered final source**, because the execution environment became
unavailable. The earlier 24-test pass predates these fixes and is not relabelled
as final-head evidence.

## Boundaries reviewed

- Monetary arithmetic stays in the existing Rust evaluator.
- No provider equations, parsers, raw schedules or private records are copied.
- MCHS weighted activity produces only activity measures.
- Missing quotations cannot select the MCHS default NEP or its comparison total.
- Tariff maps explicitly to native charge; payment records remain outside native
  valuation and are not summed with funding, tariff or cost.
- Exact source values cannot be recovered by converting a binary float to text.
- Rich provenance lives in a separate versioned envelope; shared schemas stay
  unchanged.
- No interval or allocation code changes; per-generated-segment half-even
  semantics remain the accepted native contract.
- Scope is the owned track and `adapters/mchs_sources/`; all shared changes are
  requests to the sole integrator.

The final syntax/lint, behavioural replay, installed package checks and required
hosted gates remain open. See [verification](verification.md) and
[handoff](handoff.md).
