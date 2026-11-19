# MCHS and Atlas M1/M2 handoff

Owner: **Dapane — MCHS and atlas adapters**. Recipient: the existing sole
**Dapane — Release assurance and consolidation** integrator.

## Scope and immutable baseline

- Base main: `e34f87c9df39a2132fecee142431cdeefb732471`.
- Base tree: `c07a6b2589b9d665f619f5d977d66e513180bab4`.
- Ownership map inspected: PR #20 at
  `e615454c9f3f41f96e9e310f446d2440d98cf5eb`.
- Changed roots: this track and `adapters/mchs_sources/` only.
- Runtime import namespace: `dapane_mchs_atlas`.
- Implementation commit: [`44b33969ed8254964dc95d3dbc74732d62bc8529`](https://github.com/edithatogo/dapane/commit/44b33969ed8254964dc95d3dbc74732d62bc8529).
- Implementation tree: `8d3e0c62fc0e630bc7bf9dba79a773824bef0935`.
- All 22 uploaded implementation/track files were read back at that immutable
  commit and matched the submitted content. This checks publication integrity,
  not Python execution. The final PR head is a documentation-only successor.
- The [machine-readable receipt](receipt.json) pins code blobs, native artifact
  identities and pending qualification. The PR description records its final head.

The source candidate contains strict MCHS activity and Atlas exact-supplement
adapters; separate funding, tariff and resource-cost native requests; payment
observation/model records without aggregation; 34 synthetic tests; and an
installed-native smoke check. No numerical formula is reproduced in Python.

## Evidence and unfinished acceptance

An earlier uncommitted working version passed 24 tests, including native CLI
valuation, and used a checksum-verified existing native artifact. The execution
environment became unavailable before final verification. The source was
recovered through GitHub after that outage. **The recovered final head, added
review fixes, 34-test suite and installed package have not executed.**

[Verification](verification.md) retains exact native artifact identities and the
scope of every executed and unexecuted check. [Review](review.md) records the
resource-rights and future-payment findings and their source fixes. Earlier
results are not promoted to final-head evidence.

M1.1/M1.2 source inspection/mapping are complete. M1.3 and M2 acceptance remain
open pending exact-source replay and optional package qualification. M3 is outside
this bounded lane and remains open. Neither provider was executed or modified.

## Required integration actions

Apply the three concrete [shared-change requests](shared-change-requests.md):

1. Reconcile the central registry to in_progress without changing acceptance.
2. Execute the lane suite and installed-wheel/default-native checks on the exact
   recovered head; add explicit coverage through integrator-owned CI.
3. Review tariff-to-charge semantics and retain the proposed exact-provider
   exporter requirements for later M3.

The central registry mismatch remains a real Conductor gate until reconciled;
it is not waived. Existing offline-security/release gates remain intact. The PR
is intentionally a draft while final qualification is unavailable.

## Compatibility and rollback

The root Cargo/lock/toolchain, existing core/CLI/Python code, schemas, CI, common
fixtures, expected outputs and root docs are unchanged. The accepted interval
method keeps half-even rounding per generated segment. Upstream repositories are
read-only; no new worker, merge, release, credential or infrastructure change is
part of this handoff.

The package is opt-in and independent of ordinary Dapane imports. A future rollback
can stop selecting the optional adapter and retain the previous pinned contract
and source snapshots; no shared engine or provider migration needs reversal.
Synthetic fixtures are not official classification or rate releases.
