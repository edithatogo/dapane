# Remaining genomics acceptance

The [G4.3 record](g4-3-acceptance.md) established 99 of 114 verified
outcomes. This checkpoint verifies ten additional outcomes, bringing
the candidate to **109 of 114 outcomes (95.61%)**. Research reporting,
the broader coverage targets and the three external outcomes remain open.
The original workbook retains **35 of 35 worksheets, 36,411 of 36,411
formula coordinates and 10 of 10 valuation pathways**.

## Implementation and evidence

| Outcome | Status | Acceptance evidence |
| --- | --- | --- |
| `data-governance` | Qualified | Concurrent versions retained distinct identifiers and private metadata. A restart recovered both versions. Loading a changed source failed its registered checksum. |
| `template-time` | Qualified | In a fresh synthetic consumer workspace, the installed tools generated a 22-row customized template in 0.54 s, validated the input in 0.47 s and completed the profile, data and app setup in 1.16 s. The original limits were 10, 5 and 30 minutes respectively. |
| `full-analysis-chain` | Qualified | The installed planning command connected selected source components and declared cost draws to cost drivers, DSA, PSA, cost-only VOI, budget impact, break-even, benchmark and cost per diagnosis. Independent results matched every handoff in the synthetic case. Original workbook and archived-draw comparators remain in the G4.2 record. |
| `distribution-quality` | Qualified for validated priced components | The same preselected 839 priced components from the workbook role ledger had 839 finite nonnegative costs. The expanded 959-row view had 911 of 959 valid amounts (94.99%). Separately calculated quartiles for all five models and the preserved amounts matched. The expanded view includes unpriced rows and headings. |
| `lab-management-api` | Qualified | A separate standard-library HTTP client read two synthetic records, preserving leading zeros and decimal text, and recovered its stored version 1 validation receipt. An unauthenticated request received 401. Live lab acceptance remains a separate outcome. |
| `workbook-migration` | Qualified | The installed model command copied static data to declared cells in a new XLSX layout. Independent readback verified the numeric value, a leading-zero text field and retained formulas. Duplicate targets, formula input or replacement, and output overwrite were rejected. |
| `analysis-performance` | Qualified | All eight analytical workloads met the less-than-5% regression limit. The first comparison identified a cost-driver timing difference with identical code. After simplifying finite-value validation, a paired comparison in the same runtime improved median cost-driver times by 7.91%, 12.31% and 3.82% at 1,000, 5,000 and 10,000 rows. The cost-driver results matched exactly. |
| `api-docs` | Qualified | The generator produced a reference with docstrings for 1,213 public declarations across 127 installed modules. All 1,129 declarations across the 109 frozen legacy modules mapped to their documented installed names. |
| `guides` | Qualified | The installed commands executed the guide's standardization, planning and migration examples. The checks also exercised rejected inputs, authenticated HTTP readback and contribution verification from the source distribution. [Analyst guide](../../../adapters/genomics/deploy/analyst-guide.md) |
| `research-reporting` | Open | The source, methods and output trail is documented. Completing the journal audit requires the actual study delivery edition and its supporting declarations. [Reporting evidence](#study-reporting-evidence) |
| `source-command-behavior` | Qualified | The updated source smoke command verified the installed home page, model wizard and client asset. The original repository-only release-screen command passed a numeric-only fixture and blocked a reserved-domain identifier fixture with exit 1. This brings the source-command audit to 74 of 74. |
| `coverage-targets` | Open | Each of eight analytical modules exceeded 90%. Both modules added in this checkpoint reached 100%. The inherited library and full set of modules added since the predecessor still fall short. [Coverage measurements](#coverage-measurements) |

## Installed qualification

The source archive was built at `cf67a08df41df76bcab138aecce3929a86015998`
on CPython 3.15.1. The clean consumer could load both installed distributions.
Source checkouts, the runtime source in the distribution archive and network
access were denied for the installed suites. **201 packaged tests and 1,339
inherited tests passed**. The independent lab client used an ephemeral
loopback server with the installed wheel. The workbook inventory, formula
results and native pathway output matched the retained files byte for byte.

The seven other performance workloads had median elapsed changes from
−1.35% to +3.43% against the prior installed candidate. Their numerical
results matched and peak resident memory changes ranged from −0.84% to
+0.66%. The controlled cost-driver comparison alternated the baseline
and final candidate for 16 pairs per size with the same Python process
and Polars threads. Two seeded 50,000-draw runs also matched byte for byte,
with mean 3.9989 against an independent expectation of 4.

The legacy release-screening command used isolated synthetic Git ranges.
Presidio flagged a variable-style fixture as a person name during the
first run. A numeric-only control passed, and the separate identifier
control was blocked as intended. The delivery PR retains its authoritative
GitHub Actions checks separately from these command tests.

## Coverage measurements

The combined statement coverage includes the packaged and inherited suites,
the exact workbook replay and the installed analytical and guard cases.

| Scope | Covered statements | Coverage | Frozen target |
| --- | ---: | ---: | --- |
| All 127 installed modules | 13,664 / 16,895 | 80.88% | Whole-package comparison |
| 109 inherited modules | 12,164 / 14,998 | 81.10% | At least 85% |
| 18 modules added since the predecessor | 1,500 / 1,897 | 79.07% | Greater than 90%, with 100% under R-271 |
| Eight analytical modules | 891 / 977 | 91.20% | Greater than 90% in every module. Observed 90.15% to 92.81%. |
| Two modules added in this checkpoint | 105 / 105 | 100% | 100% for these new components |

The retained coverage XML identifies the executable lines for the remaining
tests. Reaching 85% in the inherited modules requires at least 585 more
covered statements at the measured denominator. The broader added-module
requirement still has 397 uncovered statements.

## Study reporting evidence

The frozen source contains the Study 1 assumptions, version 4 dated
23 July 2023 by its filename, with SHA-256
`2ded2931a596169ce5676e2bad963e06aadf98d481bfd160a77c99a8ae8be71a`.
The catalogue inspection found the assumptions edition and the software
citation. The submission edition and its supplement inventory remain needed.

The reproducibility entries can be filled from the exact workbook replay,
software citation, installed artifact manifest and versioned output receipts.
For an original-research submission, reconcile the actual manuscript and
supplements to the applicable reporting checklist, study design, protocol and
relevant registration, structured abstract and methodological limitations,
ethics and involvement statements, funding, interests, contributorship and
data availability. Confirm the approved statement and access terms against
the rights decision below. [BMJ Open author instructions](https://bmjopen.bmj.com/pages/authors)

## External verification

| Outcome | Required evidence |
| --- | --- |
| `publication-rights` | Identify the exact study edition, workbook, supporting tables and intended publication destinations. Retain the data owner's written redistribution decision for each asset, including any redaction or embargo. Verify the approved export contents, provenance and checksums against that decision. |
| `pilot-acceptance` | Name a representative laboratory, a designated participant and the exact installed revision. Have the participant complete setup, customized template generation, input validation and report retrieval with approved inputs. Retain timings against the 30-, 10- and 5-minute targets, observed issues and the laboratory's dated acceptance decision. |
| `deployment-pipeline` | Identify the authorised target environment, existing AWS or Azure service, environment identity and immutable image digest. Retain the live promotion receipt, provider readback of the running digest, health and access results, and a rollback rehearsal. Record the execution and rollback authority for that target before a live operation. [Deployment instructions](../../../adapters/genomics/deploy/README.md) |

## Retained receipts

The 26 November 2026 qualification catalogue retains these artifacts and
their producing commands in authorised storage.

| Artifact | Edition or content | SHA-256 |
| --- | --- | --- |
| Genomics wheel | Installed from the archived candidate source | `5e786cb9697e15370312a42e1b6a4412a409e3f49cabe49813bb1cefaf0425d3` |
| Genomics source distribution | Archive of the same adapter and its packaged tests | `e273a16b542304c8c374dcf2c2900f9adde5b88de0ad19afd1aaec62ecf2f5d3` |
| Packaged JUnit | All 201 packaged cases | `d4bdc9473929af68a94cea2ad67c23656c2ad5a8940705962ae3383a5d6b569c` |
| Inherited JUnit | All 1,339 inherited cases | `cf4c81eebe0c4b21cf1b876a5f86c34521b53352465ddcb1ab726a8ad7ae6b6c` |
| Combined coverage XML | Statement results by module and line | `017c81d5dc192c70c9dd47857b5aa20c9633fb91aa9804a6a67eb39c06652005` |
| Coverage populations | Original module set, added modules and analytical thresholds | `c39abd76bfc6ea462f3279dacb6fc3ab269e1487bff9fa57fadae39f058f8de3` |
| Cost-driver comparison | Alternating samples, runtime and both source fingerprints | `011122206fd10edb43df46cefe9180aa8b1bee39f11a6bee4ecb929e077c503e` |
| Guide receipt | Installed commands and expected outputs, bound to the guide bytes | `a9c50695839b6b829f8c23006ef3dce12e0106d08e86dac89ba99e35ddda9319` |
