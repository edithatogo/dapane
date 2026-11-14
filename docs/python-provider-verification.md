# Python provider qualification

Track: [python_two_consumers_20261108](../conductor/tracks/python_two_consumers_20261108/index.md).
Status: implementation and verification in progress, 15 November 2026.

## Reconciled scope

| Repository | Inspected main | Provider boundary |
| --- | --- | --- |
| Dapane | `d7063cecc26abe96a3f28fca575b99b450241430` | Existing exact Rust valuation and allocation; native Python and CLI. |
| Workforce | `ba86fdf6843d070d257f799e061ea14d18fba387` | Canonical import namespace, preserved legacy entry points, source-selected quotation export. |
| Genomics | `de09042469fce2f48b1227283a9e2daa08fc7c79` | Manual DNA extraction recipe, explicit batch attempts and historical comparison. |

The existing Dapane core-contract PR and the conditional offline-security drafts
remain separate work. Neither provider's dependency requirements are widened.

Workforce requires CPython **3.15.2**; genomics requires **3.15.1**. Build and
install each provider wheel into a separate environment using its locked runtime
dependencies. Pass a digest-pinned exact JSON quotation artifact between them.
Both consumers invoke the same installed Dapane native extension. A file exchange
does not establish co-installability of these differently pinned providers.

## Selected source and model boundary

The workforce source is Queensland Health's [health practitioners wage
table](https://www.health.qld.gov.au/hrpolicies/wage-rates/health-practitioners):
HP3, pay point 1, the displayed hourly base reference effective 1 September 2026.
The provider retains the observed source hash, knowledge date, bounded
applicability, classification, original release snapshot and explicit component
coverage. The hourly column is a reference figure; no employment eligibility or
payroll result follows from this integration.

The genomic adapter retains the original workbook identity and selected manual
extraction mappings. The use of the selected QLD role is an explicit analysis
assumption, not a classification equivalence claim. Each actual batch attempt
incurs its declared resources once, including failed and repeated attempts.
Specimen allocation is a view of that ledger. It does not add another source cost
or imply unused capacity from specimen count.

Keep source acquisition files, workbooks and generated research receipts in their
existing restricted locations. Provider changes contain software, documentation
and synthetic tests. Dapane records source identities and qualification results;
it does not redistribute the source workbooks.

## Acceptance to execute

- Build and install all three distributions; assert imports resolve outside each
  source checkout, correct native extension and exact provider interpreter.
- Compare workforce and genomic requests with the installed CLI using the same
  Rust source and independent exact expectations, including nonterminating
  exposure and sub-cent pool allocation.
- Preserve quote dates, units, loaded-component coverage and source identity.
  Reject stale or altered releases and duplicate source components.
- Exercise full, partial, failed and repeated batch attempts; demonstrate that
  per-batch rounding and source-ledger totals remain distinct from allocation
  views and historical per-test workbook outputs.
- Separate mechanical source extraction, historical arithmetic replay and
  intentional rate/component/allocation differences. Do not claim full workbook,
  economic-method or clinical validation.
- Verify the old workforce namespace/class identity and previous pricing entry
  point, and the genomics legacy calculator route.
- Run provider checks, Dapane native and installed-wheel matrix, independent
  review and remediation before marking completion or archiving.

## Current evidence

Local repositories and package pins were inspected. Provider locked dependency
installation completed before the execution workspace became unavailable.
Dapane's isolated Rust 1.99.1 toolchain installed; the interrupted wheel setup and
unconfirmed local edits are **not** acceptance evidence.

Implementation continues in bounded GitHub branches. Hosted checks must verify
the exact submitted revisions. No completion, archive, published release or new
platform support is claimed at this stage.
