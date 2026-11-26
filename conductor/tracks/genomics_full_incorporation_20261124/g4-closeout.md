# Remaining genomics acceptance

The [G4.3 record](g4-3-acceptance.md) established 99 of 114 verified
outcomes. This checkpoint verifies nine additional outcomes, bringing
the verified count to **108 of 114 frozen outcomes (94.74%)**. The
representative lab pilot moved to the [roadmap](../../roadmap.md#representative-genomics-lab-pilot)
on 26 November 2026. The active ledger now contains 113 outcomes.
The original workbook retains **35 of 35 worksheets, 36,411 of 36,411
formula coordinates and 10 of 10 valuation pathways**.

## Implementation and evidence

| Outcome | Status | Acceptance evidence |
| --- | --- | --- |
| `data-governance` | Qualified | Concurrent versions retained distinct identifiers and private metadata. A restart recovered both versions. Loading a changed source failed its registered checksum. |
| `template-time` | Qualified | In a fresh synthetic consumer workspace, the installed tools generated a 22-row customized template in 0.54 s, validated the input in 0.47 s and completed the profile, data and app setup in 1.16 s. The original limits were 10, 5 and 30 minutes respectively. |
| `full-analysis-chain` | Qualified | The installed planning command connected selected source components and declared cost draws to cost drivers, DSA, PSA, cost-only VOI, budget impact, break-even, benchmark and cost per diagnosis. Independent results matched every handoff in the synthetic case. Original workbook and archived-draw comparators remain in the G4.2 record. |
| `distribution-quality` | Open | All 1,091 historical export rows reconciled to the workbook under their source cost bases. The strict editable-data scores on those same tables range from 41.60% to 60.28%. The validated operational dataset outcome remains open. [Full-model quality](#full-model-quality) |
| `lab-management-api` | Qualified | A separate standard-library HTTP client read two synthetic records, preserving leading zeros and decimal text, and recovered its stored version 1 validation receipt. An unauthenticated request received 401. Live lab acceptance remains a separate outcome. |
| `workbook-migration` | Qualified | The installed model command copied static data to declared cells in a new XLSX layout. Independent readback verified the numeric value, a leading-zero text field and retained formulas. Duplicate targets, formula input or replacement, and output overwrite were rejected. |
| `analysis-performance` | Qualified | All eight analytical workloads met the less-than-5% regression limit. The first comparison identified a cost-driver timing difference with identical code. After simplifying finite-value validation, a paired comparison in the same runtime improved median cost-driver times by 7.91%, 12.31% and 3.82% at 1,000, 5,000 and 10,000 rows. The cost-driver results matched exactly. |
| `api-docs` | Qualified | The generator produced a reference with docstrings for 1,213 public declarations across 127 installed modules. All 1,129 declarations across the 109 frozen legacy modules mapped to their documented installed names. |
| `guides` | Qualified | The installed commands executed the guide's standardization, planning and migration examples. The checks also exercised rejected inputs, authenticated HTTP readback and contribution verification from the source distribution. [Analyst guide](../../../adapters/genomics/deploy/analyst-guide.md) |
| `research-reporting` | Audit completed with open findings | The published article, PDF supplement and table workbook were located and checked. The audit identifies which deterministic results reproduce and which uncertainty values still need their original run. [Reporting evidence](#study-reporting-evidence) |
| `source-command-behavior` | Qualified | The updated source smoke command verified the installed home page, model wizard and client asset. The original repository-only release-screen command passed a numeric-only fixture and blocked a reserved-domain identifier fixture with exit 1. This brings the source-command audit to 74 of 74. |
| `coverage-targets` | Open | Each of eight analytical modules exceeded 90%. Both modules added in this checkpoint reached 100%. The inherited library and full added-module targets remain open. [Coverage measurements](#coverage-measurements) |

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

## Full-model quality

Use the existing `validation_pipeline.py --workbook` command for enhanced
historical exports. It records the workbook and output digests and checks all
rows, source row identities, taxonomy, schema and exported values. The five
original exports passed all 1,091 rows and 8,287 populated cells. Changed
values, omitted rows and missing models fail workbook validation. The separate
exact replay qualifies the workbook's original formulas and cached totals.

The editable-data check reports three cost failure counts alongside the
strict multi-field score. The original exports have 293 multiplication
disagreements, 62 rows outside the editable bounds, 170 missing or
nonfinite amount rows and 29 identity failures. Counts can overlap. For
example, labour quantity is in minutes while wages are hourly, and equipment
rows pair purchase prices and throughput with annualized per-test values.
Subtotals and headings can legitimately lack a standalone unit price. The
original values, broken references and missing inputs retain their workbook
lineage. The 839 priced amounts pass their separate distribution check.

The Q-184 target applies to validated editable input datasets. A named
operational dataset requires documented row roles, authorised values for
unresolved component inputs and a strict score above 99.5%.

## Coverage measurements

The combined statement coverage includes the packaged and inherited suites,
the exact workbook replay, the installed analytical and guard cases,
workbook preparation, 2,894 passing unit-cost comparisons, model export
validation, and standard report generation in four formats.

| Scope | Covered statements | Coverage | Frozen target |
| --- | ---: | ---: | --- |
| All 127 installed modules | 14,070 / 16,895 | 83.28% | Whole-package comparison |
| 109 inherited modules | 12,344 / 14,998 | 82.30% | At least 85% |
| 18 modules added since the predecessor | 1,726 / 1,897 | 90.99% | Greater than 90% for new components, with 100% under R-271 |
| Eight analytical modules | 891 / 977 | 91.20% | Greater than 90% in every module. Observed 90.15% to 92.81%. |
| Two modules added in this checkpoint | 105 / 105 | 100% | 100% for these new components |

The retained coverage XML identifies the executable lines for the remaining
tests. Reaching 85% in the inherited modules requires at least 405 more
covered statements at the measured denominator. The added-module aggregate
exceeds 90%. Individual coverage varies, and 171 statements remain
uncovered across that group.

## Study reporting evidence

The results edition is Mordaunt et al., *Genetics in Medicine* 26(4),
101058, DOI `10.1016/j.gim.2023.101058`. It was accepted on 22 December
2023, appeared online on 30 December 2023 and was assigned to the April
2024 issue. The BMJ Open paper is the separately published protocol.
The retained Study 1 assumptions v4 dated 23 July 2023 by filename are a
separate source edition. [Results article](https://doi.org/10.1016/j.gim.2023.101058)
[University record](https://researchnow.flinders.edu.au/en/publications/the-cost-of-proband-and-trio-exome-and-genome-analysis-in-rare-di/)
[Study protocol](https://doi.org/10.1136/bmjopen-2022-069441)

| Asset inspected on 26 November 2026 | Contents | SHA-256 |
| --- | --- | --- |
| [Results version of record](https://researchnow-admin.flinders.edu.au/ws/portalfiles/portal/105066454/Mordaunt_Cost_P2023.pdf) | Journal PDF, eight pages, CC BY 4.0 | `6c1bf8cb92d59dd167053d132287d775642acf912acd9a4cd31cfe218a0c3b71` |
| [Publisher supplement PDF](https://ars.els-cdn.com/content/image/1-s2.0-S1098360023010742-mmc1.pdf) | Two figures and three documents covering assumptions, computing configuration and jurisdictional labour factors | `bd613e2f9bfc68884f1886bf5c74d382a63b488321e41c85f15450c8b5b65600` |
| [Publisher supplement XLSX](https://ars.els-cdn.com/content/image/1-s2.0-S1098360023010742-mmc2.xlsx) | Eight tables covering detailed inputs, wages, estimates, four deterministic sensitivity analyses and PSA | `28170c95181393a96b8bfcc66e19cc5bd5f732e2ec3ed36cfa60fa6c2fd31eda` |

The study reports cost per rare-disease test in 2023 AUD. Tables 1 and 2
display five assay estimates. At published precision, the original
`Summary Table` matches all five central AUD figures, 20 of 20 resource
categories and 48 of 50 stage figures. Supplemental Table 3's unrounded
proband exome total differs from the workbook by AUD 0.25. The 14 scenarios
for the five assays reproduce all 70 midpoint entries from `DSA - Summary`
through Supplemental Tables 4–7 and article Table 3. The article intervals
and Supplemental Table 8 percentiles differ for all five assays. A December
2023 legacy notebook uses an unseeded sampler and references a separate final
MLE input. Exact publication PSA reproduction requires the publication's
original draws or a documented deterministic run with matching inputs.

The published edition includes a structured abstract, setting and test
denominators, price date, process exclusions, methods and limitations. Its
declarations cover ethics, funding, contributions, competing interests and
data availability. The last identifies the public supplements and confidential
price redactions. Version-of-record identity was reconciled to DOI metadata.
Manual table and citation-callout inspection, SourceRight 0.1.20 and Textstat
0.7.13 receipts are retained for the audited materials. Current author
guidance calls for CHEERS for new submissions in the economic-evaluation
category. The original submitted checklist and the reproducible publication
PSA run remain outstanding for full reporting acceptance. [Genetics in Medicine author guidance](https://www.gimjournal.org/content/authorinfo)

## External verification

| Outcome | Required evidence |
| --- | --- |
| `publication-rights` | Linking the published article and supplements is available now. For any republication, record the exact bytes, license or permission, attribution and exclusions. For releasing the original workbook, restricted source inputs or any derivative that reveals confidential prices, obtain written authority from the relevant custodians and rights holders. Specify the artifact, audience, destination, licensing terms, required redactions and embargo. Retain the approval and check the final export against it. [Published article license](https://creativecommons.org/licenses/by/4.0/) |
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
| Combined coverage XML | Expanded statement results by module and line | `c39fd8cc944fe6ed0a1e3b4b6cc376429f5aabd3ae1300d1911503ed9633d798` |
| Coverage populations | Original module set, added modules and analytical thresholds | `8af2ed9af78dae30e8ca84842d148b6c2b5d8cbfb241d5da20601bb22918ca1a` |
| Model quality | Five strict multi-field scores and outcomes | `acdade52acd35f30a30756443a956d668221ca46258a35994f0d2c07ca1998cd` |
| Model parity | Five model comparisons against cached workbook values | `de3329c88464b4d907ae0ff867753f2007d8799f2ddd5ba3f4a60dd4dedeb833` |
| Cost-driver comparison | Alternating samples, runtime and both source fingerprints | `011122206fd10edb43df46cefe9180aa8b1bee39f11a6bee4ecb929e077c503e` |
| Guide receipt | Installed commands and expected outputs, bound to the guide bytes | `a9c50695839b6b829f8c23006ef3dce12e0106d08e86dac89ba99e35ddda9319` |
