# Release migration and recovery

This procedure extends the existing [compatibility policy](compatibility.md).
No provider API is removed or redirected by candidate release assurance.

## Before adopting a candidate

Keep the consumer's existing provider package and entry point available.
Pin its version, source release, quotation/recipe identities and source rights.
Pin Dapane's source commit, Cargo.lock, toolchain, target, wheel/CLI hashes and
reference receipt separately. Version 0.1.0 alone does not distinguish different
unpublished candidates.

Select a declared wire schema and its paired method in the
[capability manifest](../release/capabilities.json). Confirm the exact executed
platform in the receipt. Unsupported methods, fields and versions must fail;
do not infer support from a package version, wheel tag or optional-track plan.
The manifest identifies candidates; it is not runtime negotiation with an
uninstalled provider.

Preserve the old request, report, source snapshots and immutable identities.
Run the consumer's independently calculated examples and invalid-input cases
through both paths. Compare source totals, attribution, residuals, component
inclusion, dates, units and source identities. CLI/Python equality alone only
demonstrates interface parity. Establish an explicit explanation for any
intentional result change.

The archived Python track supplies the existing workforce namespace/entry-point
adapter, dated workforce/genomics composition and bounded historical reproduction.
Use its [durable qualification](python-provider-verification.md) and
[immutable provider lock](provider-consumers.lock.json). The source revisions stay
pinned to the qualified trees even when the receiving merge commit has a different
identity. The genomics development wheel also embeds its qualified revision.
The selected base-salary/manual-extraction qualification does not cover a whole
assay, the entire historical workbook or unrelated provider migration.

## Change categories

| Change | Required behaviour |
| --- | --- |
| New candidate build | New source and artifact identities; retain prior artifacts and receipts. |
| Source correction | Preserve the original pack; issue a new source version and new run identity. Never silently overwrite the historical source. |
| Different financial method | Use a new explicit method identity and independent expectations. Explain numerical differences. |
| Schema change | Qualify an explicit migration; preserve the prior reader or replay path until affected consumers are verified. |
| Deprecated public entry point | Document the replacement and consumer-owned compatibility adapter before removal. Preserve the old package path and historical inputs. |
| Optional adapter | Keep installation/import isolated and qualify its own provider, rights, runtime and platform evidence. |

Contract 0.1 full-pool normalisation must not become contract 0.2 capacity
allocation implicitly. Unknown use/capacity remains unknown; observed throughput
does not supply available instrument hours. Device useful life, maintenance
duration and one-time/recurrent costs retain their separate meanings.

## Recover a failed migration

1. Stop promotion of the changed candidate. Retain its inputs, reports and failure
   diagnostics; do not repair historical reports in place.
2. Reinstall the previously retained wheel/CLI into its original compatible
   environment, after checking its recorded digest and provenance.
3. Restore the pinned provider and source/recipe pack with their access
   restrictions intact.
4. Replay the preserved inputs and compare the expected report identities and
   independently known values. A matching digest is an identity check, not new
   empirical validation.
5. Publish a corrective version only through a subsequently qualified release
   path. Keep the failed candidate's identity and migration explanation visible.

No earlier public Dapane runtime is assumed to exist. This is a candidate recovery
procedure. The selected provider record preserves canonical/legacy entry points
and historical calculator access; no shared machinery is removed. Any broader
cutover/rollback still requires its own preserved inputs and executed evidence.

## Retention

Retain source archives, exact lockfiles, toolchain details, package artifacts,
SBOMs, advisory/rights review outcomes, receipts, reference inputs and expected
results together. CI artifact retention is bounded and is not a permanent
scholarly archive. Before a public release, select a durable release archive and
verify restore/replay. Private workbooks, datasets and research histories remain
with their existing owner and access controls.
