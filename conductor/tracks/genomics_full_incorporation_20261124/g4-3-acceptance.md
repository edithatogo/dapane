# G4.3 acceptance record

The 26 November 2026 checkpoint accounts for every workbook and feature
entry. The verified scope covers the complete original workbook ledger
and **99 of 114 feature outcomes (86.84%)**. Twelve outcomes still need
implementation or evidence, and three need external acceptance. Full
incorporation remains in progress under the
[track acceptance criteria](spec.md#acceptance).

| Ledger | Verified | Scope and source |
| --- | ---: | --- |
| Original workbook worksheets | 35 of 35 | Frozen catalogue and exact workbook replay. |
| Original workbook formula coordinates | 36,411 of 36,411 | Includes all seven original formula errors and the separately recorded numerical comparison rules. [Replay and comparator](verification.md#exact-historical-formula-replay) |
| Booked valuation pathways | 10 of 10 | Retained AUD and USD comparator results. [Pathway verification](verification.md#detailed-pathway-and-resource-costing) |
| Frozen feature outcomes | 99 of 114 | The [G4.2 qualification](g4-2-qualification.md) established 95. The four outcomes below add verified controls and bounded CI evidence. |
| Legacy source-command behaviours | 72 of 74 | The installed legacy web launcher now passes. The system-browser helper and repository release-screening utility remain open in the command audit. |

## Installed candidate

The adapter was rebuilt from the archived
[`406e55bac4500305ca68b2e3abfd43343f61a6e8`](https://github.com/edithatogo/dapane/commit/406e55bac4500305ca68b2e3abfd43343f61a6e8)
source, adapter tree `513636d7ed7a6b433933fcaee47cf5650e355f2d`.
The noneditable distribution and retained Dapane binding passed the
package and dependency checks on CPython 3.15.1. The consumer could read
the installed runtime and authorised fixtures. Reads from both source
checkouts and the archived runtime source failed, as did a network
connection attempt.

All **196 packaged and 1,339 inherited tests passed** without skips.
Combined installed Python line coverage was **13,001 of 16,741 lines
(77.66%)**. The formula evaluators and native valuation sources match
the G4.2 candidate. The three retained replay and pathway receipts
matched their [recorded hashes](g4-2-qualification.md#retained-receipts).

Same-second dataset registrations now receive different identifiers.
Reopening their metadata preserved independent values 4 and 7 and
verified both digests. A default read returned the later registration.
The legacy web launcher used prepared tables from the clean consumer
directory. The installed app returned health status 200 and the
expected synthetic table while retaining the local-only launch options.

## GitHub controls

| Outcome | Verified result |
| --- | --- |
| `branch-controls` | The active `Protect main` ruleset requires a PR and blocks deletion and force-pushes. Its required GitHub Actions checks are `offline-ai-security / offline-security`, `validate` and `privacy-and-secrets`. Human approvals, Code Owners and standing bypass actors are absent. The owner retains ruleset administration and can restore the recorded settings if a repair is needed. A read of the unrelated follow-up branch returned no rules from this ruleset. [GitHub ruleset](https://github.com/edithatogo/dapane/rules/28132375) |
| `dependency-updates` | The bot-authored dashboard readback on 26 November confirms the installed Renovate app detects Dapane's GitHub Actions, Cargo and Python dependencies. The repository inherits `local>edithatogo/renovate-config`. The redundant Dependabot GitHub Actions version schedule was retired after that readback. GitHub's independent Dependabot security updates remain enabled. [Renovate dashboard](https://github.com/edithatogo/dapane/issues/6) |
| `coverage-oidc` | GitHub read back `GENOMICS_CODECOV_ENABLED=true`. The OIDC dispatch on `be6f5909986900bf451a266db169c3b1a1897fa2` activated Codecov. Its API returned a completed report for that exact SHA and flag `genomics-installed`, with 4,767 of 16,740 lines covered by the packaged synthetic suite. GitHub recorded `codecov/patch` as successful from `codecov[bot]`. [OIDC Actions run](https://github.com/edithatogo/dapane/actions/runs/45747197844) · [Codecov commit](https://app.codecov.io/gh/edithatogo/dapane/commit/be6f5909986900bf451a266db169c3b1a1897fa2) |
| `extended-ci` | The installed prediction test verified held-out values, row permutation, doubled training costs, zero values and the rank and residual-degree checks. It detected all eight comparison mutants of the installed prediction module. The mutation check runs weekly or through a main dispatch and retains the result. The packaged PR suite exercises the metamorphic prediction and the operational API contracts. [Installed package workflow](../../../.github/workflows/genomics-package.yml) |

GitHub also reports secret scanning, push protection and private
vulnerability reporting enabled. Dapane inherits the maintained account
security policy and retains its contributing instructions, PR template,
issue template and one-command Conductor validation. CodeQL, privacy checks
and the release-assurance dependency advisory and licence gates retain
their existing scope. [Inherited security policy](https://github.com/edithatogo/.github/blob/main/SECURITY.md)
· [Contributing](../../../CONTRIBUTING.md)
· [Release assurance workflow](../../../.github/workflows/release-assurance.yml)

The hosted offline workflow qualifies the exact PR head and resulting
`main` revision. The main package dispatch uses the same selected
revision for the bounded mutation check and Codecov upload. The delivery
PR retains the exact hosted run and provider links for this checkpoint.

## Remaining acceptance

The twelve local or evidence outcomes are data governance, template
setup time, the complete source-fed analysis chain, distribution quality,
lab-management exchange, workbook migration, analysis performance, API
documentation, guides, research reporting, source-command behaviour and
named coverage targets. The dataset version fix and launcher fix close
their reproduced failure cases within that ledger.

The three external outcomes are study publication rights, representative
lab pilot acceptance and live cloud promotion. The
[complete source crosswalk](feature-audit-crosswalk.tsv) retains their
original acceptance scope.

## Retained receipts

Build, installed test and native control receipts are in the authorised
26 November 2026 qualification catalogue. The workbook and populated
research artifacts remain in the retained G4.2 source store.

| Artefact | Edition and provenance | SHA-256 |
| --- | --- | --- |
| Genomics wheel | Locked archive build from adapter tree `513636d` | `f2d5f80deeecf0a35972d8b23e09ada93b08c366ae07fc1d61c7aa68f7060b50` |
| Source distribution | Same archive build and installed test inputs | `d1a66c446b406cec48005e6d465fbd6c1b4bdd128f6e685ae382a36d800ec262` |
| Packaged JUnit | Installed suite with 196 cases | `c2a33cdf5ee8901999ecd7e8a87bd844afd83b9a702bf3130b06d11e81ced6b9` |
| Inherited JUnit | Retained harness and fresh installed package with 1,339 cases | `031b7702bf21961429202a12582a74f477ec44e4e83dc5294538f8cfbd95dc28` |
| Combined line coverage | Both suites scoped to installed modules | `d13283e99112683e2a04c6ebebae787e8b3418a7ca6f6e82b9ec693ddd99af88` |
