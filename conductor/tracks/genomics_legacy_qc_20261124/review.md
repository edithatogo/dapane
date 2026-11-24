# Review report — Genomics legacy quality-control costing

## Summary

The installed replay meets the historical workbook acceptance criteria after
strengthening its component and rounding checks. The review started from Dapane
`main` at `7d03828d8d0fbed56b96efb2008195e4b8eb5171`, which passed its exact
[official offline-security run](https://github.com/edithatogo/dapane/actions/runs/45325060431).
The [verification record](verification.md) retains the original source identity,
case results and historical limits.

## Verification checks

- [x] **Plan compliance** covers the nine original QC lines and all 13 expanded
  workbook replays. The installed provider module matched the source bytes
  at the pinned revision in the [provider lock](../../../docs/provider-consumers.lock.json).
- [x] **Style compliance** passed Ruff 0.17.4 lint and format checks.
- [x] **New checks** reject swapped equipment charges and swapped labour
  components even when the totals agree. They also reject a changed rounded
  value and a changed workbook total with identifier-only diagnostics.
- [x] **Test coverage** checks each equipment charge and each of the 11 loaded
  labour components against the workbook, plus exact and rounded reconciliation
  for every expanded report.
- [x] **Test results** on CPython 3.15.1 include 86 provider regression tests,
  215 installed Dapane tests and the installed workbook replay with identical
  native CLI and wheel reports.

## Findings and fixes

The [verification fix](https://github.com/edithatogo/dapane/commit/e8344b3aec452d29a774f04cfda5e05f335a0378)
addresses the findings in the
[installed consumer verifier](../../../scripts/verify_provider_consumers.py).

### Component and rounding regressions

Totals alone could match while individual equipment charges or hourly
components were assigned incorrectly. The verifier now derives the expected
values from the original workbook through the historical reader. It requires
complete reports and checks exact line sums, half-even line rounding and
rounded report totals. The original workbook-cache tolerance of AUD `1e-12`
applies only to comparisons with the saved workbook numbers.

### Workbook amounts in failure diagnostics

A failed stage comparison could print both exact amounts in public Actions
logs. Its assertion now identifies the affected replay by ID. The amounts
stay in the private workbook and replay output.

### Scanner workflow reference

The [first archive PR run](https://github.com/edithatogo/dapane/actions/runs/45382873227)
stopped before starting a job after the original scanner source branch had
been pruned. The merged revision from
[Scanner PR #183](https://github.com/edithatogo/repository-standards/pull/183)
resolved on GitHub and matched the original Git tree. The
[next run](https://github.com/edithatogo/dapane/actions/runs/45383151551)
found that the signed Wolfi index offered a newer libexpat1 than the one in
the checksum-locked bundle.

[Scanner PR #184](https://github.com/edithatogo/repository-standards/pull/184)
derives exact constraints for all 50 entries in the reviewed inventory. Its
[official hosted image run](https://github.com/edithatogo/repository-standards/actions/runs/45384546540)
passed the offline controls and collected the image inventory and vulnerability
evidence. Dapane pins the merged scanner revision `64f7c59790df12fafe4773857cc1bec21269b7ac`.
The merged tree matches the qualified PR tree, and the immutable policy
checkout succeeded in a fresh fetch. The build still uses signed index
verification, package checksums and a network-disabled installation.
