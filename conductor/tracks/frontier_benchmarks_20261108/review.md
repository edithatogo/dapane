# Scoped review — 2026-11-15

This is an implementation-owner review, not an independent human or security audit.
The independent arithmetic oracle is separate computational evidence.

## Findings addressed

1. **Two diagnostic predictions were wrong.** The first native run returned
   `invalid_request` for an unsupported policy field and enum variant. The
   original failed expectation count and exact diagnostics are retained in
   [history](../../../benchmarks/static/HISTORY.md) and the observation record.
   Revised expectations follow the typed deserialisation boundary. Production
   behavior and numerical expectations were unchanged.
2. **A moved/reconstructed head cannot inherit local qualification.** The original
   21-test run is tied to local SHA `5cc42f41d1713afab9348d781a38717d515b6b75`.
   The publication namespace and locator bytes changed after environment loss.
   F2.1/F2.2 remain blocked and the PR is a draft.
3. **Cache reuse must preserve hidden dependencies and source identity.** The
   chosen cache unit is a complete request, including every allocation, unused
   quotation, policy and source field. Earlier tests exercised invalidation,
   removal, immutable output, executable changes and transactional failure.
4. **A failed comparison must not generate a speed summary.** The proposed runner
   retains partial observations, requires full report equality and independent
   checks, and leaves its summary null on failure. Two added gate tests and the
   new bundle verifier are authored but unexecuted.
5. **Strict transport must reject a malformed successful envelope.** A type check
   for the nested financial report was added during static reconstruction review.
   Its publication-head execution remains part of the outstanding test gate.

## Remaining findings / acceptance blockers

- **Exact-head execution unavailable:** rebuild, tests, lint/format, fixed timing
  protocol and bundle verification must run after restoring an execution host.
  The 32-request case and measured timing pairs have never been executed.
- **Source receipt incomplete for the historical run:** no retained CLI digest,
  complete original raw outputs or remotely available local commits. The summary
  is useful history, not complete reproducibility evidence.
- **Registry mismatch pending integrator:** track status is now `in_progress`;
  this lane cannot change the shared registry. The resulting Conductor failure
  must be resolved by the integrator, not ignored.
- **Hosted coverage not connected:** existing CI does not discover this namespace.
  Commands and an artifact request are provided in the handoff.

## Review boundary

Only this existing track and new `benchmarks/static/` files are proposed.
All valuation remains in the unchanged Rust CLI. Source-truth defects are not
credited as detected, and half-even remains per generated segment. No performance
or empirical conclusion is supported yet. A full independent publication-head
review remains an integrator step after execution is restored.
