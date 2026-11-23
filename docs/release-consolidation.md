# Conditional consolidation review

Review date: **15 November 2026**. Decision: **no repository archive, deletion or
removal of duplicated machinery is selected by this increment**.

The [existing ecosystem plan](../conductor/ecosystem.md) identified conditional
candidates. A fresh authenticated inspection covered repository state, current
trees, relevant retained branches, provenance/citation entry points and public
successor documentation. The public record below contains the decision and
owner boundaries. Restricted source files, detailed private asset inventories,
private commit locators and research excerpts are not copied into Dapane.

## Candidate disposition

| Existing candidate | Current disposition | Evidence still needed for a future archive |
| --- | --- | --- |
| hwcc | Retain all existing branches and assets. | Unique employment rules, workbooks and restricted evidence need preserved ownership, qualified successor behaviour and recovery. |
| cobra-costing | Retain; a minimal default branch does not establish an empty repository. | Review retained implementation/research history, intended use, rights and a functioning successor before any cleanup. |
| tutorial_microcosting_genomics | Preserve scholarly identity and historical analyses. | Citations, manuscript/source assets and independently reproduced historical results need their own preservation and migration evidence. |
| checklist_microcosting | Preserve methods research and protocol history. | Source instrument rights, research status and reusable-software boundaries must be established before any extraction. |

The inspected repositories remain active; no predecessor was converted into a
qualified successor merely by adding documentation. Existing parallel work and
retained branches were left untouched. This is a bounded inventory, not an
assertion that every historical asset has been cleared for redistribution.

## Retained owners

| Owner | Role retained | Public source inspected |
| --- | --- | --- |
| MCHS | Classification, activity/funding rules and source interpretation | [354dbe7e](https://github.com/edithatogo/mchs/tree/354dbe7ebd0e8bc657915115d399838127fef01d) |
| microcosting_healthworkforce | Employment rules, dated rate releases and public compatibility APIs | [ba86fdf6](https://github.com/edithatogo/microcosting_healthworkforce/tree/ba86fdf6843d070d257f799e061ea14d18fba387) |
| microcosting_genomics | Recipes, batch/repeat assumptions and historical domain interpretation | [de090424](https://github.com/edithatogo/microcosting_genomics/tree/de09042469fce2f48b1227283a9e2daa08fc7c79) |
| voi_sequencing_costs | Research consumer and study artifacts | Retain the existing research owner and access restrictions. |
| CareOps costing module | Maintained operational module | [module README at 11f5b224](https://github.com/edithatogo/careops/blob/11f5b224fdd0263cc9ec7f27441231eb72674a24/modules/careops-costing/README.md) |

The CareOps public source explicitly excludes private operational/source assets.
Its presence does not establish preservation of those assets, deployment or
costing parity. Dapane's Apache-2.0 decision and domain code licences do not
clear every source dataset, rate, workbook or instrument for redistribution.

## Conditional steps not executed

No archive has been selected, so successor cutover, historical-consumer
reproduction and restore testing for these external archive candidates, and
removal of shared machinery, are not asserted as complete. The separately
[qualified workforce/genomics subset](python-provider-verification.md) does not
establish those candidates' full preservation or successor behaviour. Any future
selected archive must retain the unique history,
scholarly/source assets, rights, known-good artifacts and a demonstrated
successor/recovery path, then use authority for that particular repository action.

The user's request to archive the Dapane Conductor track is separate from
archiving these repositories. Track completion still depends on the release
acceptance criteria and evidence.

## Successor and recovery follow-up — 24 November 2026

GitHub readback confirmed that the four candidates above still have active
private repositories and retained branches. Both historical CareOps costing
repositories are already archived. The maintained module link resolved at its
recorded revision. [CareOps costing module](https://github.com/edithatogo/careops/blob/11f5b224fdd0263cc9ec7f27441231eb72674a24/modules/careops-costing/README.md)

| Candidate | Maintained route to evaluate | Evidence required before cutover |
| --- | --- | --- |
| `hwcc` | Use the retained workforce package for the qualified dated quotation. [Workforce and genomics handoff](python-provider-verification.md) | Restore the original rules, rate editions, workbook inputs and historical outputs within their existing access controls. Replay the affected public entry points against independent expected values. |
| `cobra-costing` | Establish a consumer and method match before naming a successor. | Restore retained branches and research sources. Trace every proposed removal to a supported call and replay its historical examples. |
| `tutorial_microcosting_genomics` | Use the genomics provider for the qualified manual-extraction labour slice. [Genomics handoff](python-provider-verification.md#historical-interpretation) | Preserve citation targets, manuscripts, workbook/model inputs and historical environments. Reproduce the published results that depend on any proposed removal. |
| `checklist_microcosting` | Use the existing reporting catalogue and semantic profile for their respective roles. [Retained owners](../conductor/ecosystem.md#source-of-truth) | Preserve the study protocol, instrument editions, rights and analysis receipts. Verify item-level provenance and replay against the preserved instrument before extracting code. |

For an approved cutover, retain the predecessor's exact refs, binaries,
environment locks and restore instructions with its owner. Inventory any
LFS objects, release assets and owner-held records separately from Git blobs.
Restore the inputs under their existing access controls and compare old and
new outputs under the same source, method and rounding identities. Retain the
prior entry point and report identities as the rollback target.
[Migration and recovery](release-migration.md#recover-a-failed-migration)

### Executed recovery

- Downloaded all ten assets from the [GitHub prerelease](https://github.com/edithatogo/dapane/releases/tag/v0.1.0).
  The nine manifest entries and the independently returned manifest SHA-256
  matched. The source archive SHA-256 was
  `9838d66e499f8b73340a12c0b3647e87aa7561b0a5c7973663d0b4a66c7da4b5`.
  `gh attestation verify --bundle` accepted the source at
  `5a24196c6e3b8905613dcf5100c239018c919b7a` from GitHub-hosted `main`.
- Restored the archive to an isolated directory and compared 620 tracked blobs
  to the tagged Git tree. Built the restored CLI using Rust 1.99.1 on
  aarch64 macOS with `cargo build --locked --offline --no-default-features -p dapane-cli`.
  With CPython 3.15.1, `scripts/validate_contract.py --cli` verified five
  independent reports, 14 runtime rejection cases and three identity/context
  cases. This exercise covers source recovery and reference replay.
- Both installed-provider jobs on `a66e9bc28969578078ac61210b132c80bac30e06`
  installed the pinned consumers, exported the workforce quotation and
  reproduced the manual extraction labour composition. The supported slice
  and its historical references are recorded with the original provider
  recipes and source pack. [Provider job](https://github.com/edithatogo/dapane/actions/runs/45197381257)
  · [Release-candidate job](https://github.com/edithatogo/dapane/actions/runs/45197381351)

The recovered source and installed provider evidence support that bounded
handoff. Each proposed external archive still needs its own authorised asset
restore and historical consumer replay. The candidate disposition above
continues to apply.
