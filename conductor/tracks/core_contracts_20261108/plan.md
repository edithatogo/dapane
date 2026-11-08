# Implementation plan: Core contracts and independent reference cases

Status: new

Use `[ ]` pending, `[~]` active, `[x]` verified complete, `[!]` blocked and `[-]` intentionally omitted with a recorded reason.
Check a task only when its acceptance evidence is available. Provider capabilities and conditional options retain their own status.

## Phase 1 — Inventory and reference cases

- [ ] C1.1 Inspect the first workforce, genomics and MCHS capabilities; freeze one bounded example from each and label demonstration-only analyses.
- [ ] C1.2 Derive expected exact quantities, rates, costs and allocation totals independently; retain any official/reference-source restrictions.
- [ ] C1.3 Verify fixture provenance and reconcile discrepancies before adopting a baseline.

## Phase 2 — Contract definition

- [ ] C2.1 Specify record fields, identities, units, activity kinds, valuation bases, component inclusion and structured errors.
- [ ] C2.2 Specify decimal coefficient/scale or string encoding, numerator/denominator encoding, precision/overflow bounds and explicit conversion/rounding.
- [ ] C2.3 Specify effective/knowledge dates, correction/retraction handling, schema versions and reproducible bundle manifests.
- [ ] C2.4 Validate schemas against positive and negative reference fixtures; reject unsupported semantics rather than coercing them.

## Phase 3 — Consumer mapping

- [ ] C3.1 Map one workforce, genomic and weighted-activity record to the contract; document intentional information loss or unsupported fields.
- [ ] C3.2 Record extension namespacing, backward compatibility and deprecation behaviour without designing a native dynamic plugin ABI.
- [ ] C3.3 Run the contract-fixture checks, document the accepted first kernel scope and update requirement/decision records.

## Evidence record

No runtime acceptance evidence is recorded by this initial plan.
Update [metadata](metadata.json), [track index](index.md) and [registry](../../tracks.md) together when the status changes.
