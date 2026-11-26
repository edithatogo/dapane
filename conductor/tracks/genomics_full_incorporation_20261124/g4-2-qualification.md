# G4.2 clean-install qualification

The 26 November 2026 qualification accounts for all 114 outcomes in the
[frozen feature audit](feature-audit.md). **95 outcomes qualify for their
recorded scope.** Thirteen still need code or local evidence, and six need
external evidence or acceptance. The 71 previously qualified outcomes
retain their original results and were checked against the fresh regression
and package inventory. The table below reassesses the other 43 using the
[same source crosswalk](feature-audit-crosswalk.tsv).

## Installed candidate and replay

The candidate was built from Dapane
[`876db60e9d5a829ae39e78095c0b6dfac68564d0`](https://github.com/edithatogo/dapane/commit/876db60e9d5a829ae39e78095c0b6dfac68564d0).
The archived adapter was synced from its lock and built offline with
CPython 3.15.1. Its wheel and source distribution passed the package check.
A fresh environment installed `genomics-microcosting 0.2.1.dev0` and the
retained native `dapane 0.1.0` wheel without editable installs. Dependency
readback found 91 compatible packages.

The installed consumer ran outside both checkouts with filesystem access
to the checkouts and archived runtime source denied. Probe reads failed
for four source locations. A network connection attempt also failed.
All runtime imports resolved inside the fresh environment. The inherited
harness contained test code and authorised test fixtures. Its package
lookup resolved to the installed wheel.

Both full suites ran under that isolation with `coverage run
--parallel-mode -m pytest --disable-socket`. **194 packaged and 1,339
inherited tests passed**, with zero skips. Combined installed Python line
coverage was **12,986 of 16,740 lines (77.57%)**. The package contained all
109 frozen legacy modules. The declaration check found 1,128 unchanged
signatures and one compatible addition. `DataManager` still accepts its
original calls and adds the optional `create_directories` keyword with the
legacy default. All 21 legacy route and method entries, two console targets,
nine resources and 19 source-distribution configuration assets matched.
Seventeen configuration assets also ship in the wheel.

The wheel digest matches the earlier dashboard qualification. The retained
[workbook replay](verification.md#exact-historical-formula-replay) still
matches its recorded fingerprints and accounts for **35 sheets and 36,411
formula coordinates**, including all seven original formula errors. All
ten booked AUD and USD pathways retain their comparator results. The
dependent workbook paths in the fresh run independently validated all 35
sheets and checked the headers and row counts of 35 Parquet and 35 CSV
exports. The formula replay results were reused. The
[official offline-security run](https://github.com/edithatogo/dapane/actions/runs/45613406601)
and [hosted installed package run](https://github.com/edithatogo/dapane/actions/runs/45613406731)
both passed on the candidate revision.

## Outstanding outcomes from the frozen audit

| Outcome | Disposition | Installed result and remaining acceptance |
| --- | --- | --- |
| `prepare-migration` | Qualified | The installed `prepare-data` uses the reference sheet extractor and pipeline loaders. It produced the expected CSV and Parquet outputs and preserved the legacy filenames. |
| `api-extraction` | Qualified | The installed API extractor accepts a caller-supplied, read-only JSON response, preserves the declared decimal values and rejects inexact or ambiguous records. |
| `data-governance` | Open | Two same-name CSVs with different digests registered in the same second received the same version ID. Reading the second registration returned the first value, 4 instead of 7. Version identity and end-to-end governance need qualification. |
| `publication-rights` | External | The synthetic publication export remains qualified. Authorised publication of the study exports and supporting sources requires rights evidence. |
| `compute-stage-coverage` | Qualified | The five installed stage charges were AUD 20, 8, 6, 4 and 2. The sum, allocation and signed bill residual matched the [planned costing cases](verification.md#planned-feature-implementations). |
| `storage-stage-coverage` | Qualified | Separate raw, processed and archive allocations retained 12, 10 and 10 byte-seconds and exact AUD 3, 4 and 1 valuations. |
| `price-provider-operation` | Qualified | A pinned price file reproduced the original request and result. Changed bytes, a missing file and a quote beyond its validity date were rejected. |
| `profile-yaml` | Qualified | The configured lab YAML applied the exact multiplier and preserved original quote identity in the valuation receipt. |
| `taxonomy` | Qualified | The workbook-backed reader retained 96 original subcategory label cells. Across five models and 959 component or unpriced rows, shared categories were 3/3 (100%) and shared subcategories 18/20 (90%). Both exceed the frozen targets. Restricting the comparison to 839 priced rows gives 17/20 (85%) for subcategories, which fails the strict greater-than-85% target for that subset. |
| `model-config` | Qualified | The typed model configuration applied hours per case and a resource multiplier. Ten cases produced 20 hours and AUD 225 at the declared volume tier with configuration provenance. |
| `template-time` | Open | The installed 22-row template generated in about 0.68 seconds and validated in 0.34 seconds. The automated path took 1.15 seconds. The 30-minute setup target still needs a new-lab receipt. |
| `config-rollback` | Qualified | Restoring the previous lab configuration reproduced the entire original valuation, with AUD 60.00 → 75.00 → 60.00 across the three runs. |
| `full-analysis-chain` | Open | Cost drivers, DSA and archived-draw PSA have independent source-backed report results below. The seeded VOI check uses a declared synthetic case. The remaining demonstration reports need source-fed numerical comparators. |
| `distribution-quality` | Open | Two synthetic standardized models reproduced totals 10 and 20 and medians 5 and 10, with no nulls or violations. The greater-than-99.5% quality target needs an agreed validated dataset and scoring receipt. |
| `request-tracing` | Qualified | One authenticated diagnostics request traversed the four analytical modules. Its response, persisted result and audit entry shared the trace ID after app recreation. |
| `secured-web` | Qualified | Installed tests exercised authenticated viewer and analyst access and verified that export and diagnostics remained unavailable to viewers. [Dashboard controls](verification.md#dashboard-and-operational-controls) |
| `rate-limits` | Qualified | Installed requests hit the per-account limit and succeeded again after the declared window. |
| `lab-management-api` | Open | Local authenticated versioned diagnostic and receipt readback passed. A lab-management system still needs to reproduce a versioned exchange using its expected request and result. |
| `advanced-chart-variants` | Qualified | The trend and box plots contained the expected means and medians and reopened as PNGs. A synthetic chart bundle produced all five expected PNG and interactive HTML outputs. |
| `responsive-ui` | Qualified | The identical wheel's internal-browser run exercised the model wizard at 390 by 844 pixels and downloaded the expected 22-row template. |
| `drag-and-drop` | Qualified | The packaged drag handler preserved exact profile text and retained the prior profile after oversized or rejected input. |
| `setup-wizard` | Qualified | The wizard produced the expected Panel template with added costs and blank input prices. |
| `configuration-builder` | Qualified | The installed editor preserved the decimal multiplier `"1.125"` and six-year equipment life in the downloaded workflow. |
| `strategy-plugin` | Qualified | A caller registered a local strategy through the installed engine. Cost 8 became 12 and the custom validation rule rejected 11. |
| `workbook-migration` | Open | Distinct workbook layouts restored byte-for-byte and preserved value 8 at their declared coordinates. The frozen migration-script requirement (I-252) still needs an installed migration path. |
| `operational-monitoring` | Qualified | An authenticated local consumer read health, metric count 3 and an alert. The stored diagnostic receipt was available after app recreation. |
| `test-service-api` | Qualified | Installed endpoints executed the documented integration, end-to-end and performance diagnostics and returned the persisted result for matching filters. |
| `benchmark-service-api` | Qualified | The installed HTTP benchmark measured 37 cost-driver rows and 321 seeded simulation draws. |
| `monitoring-api-contract` | Qualified | Installed endpoints returned versioned health and filtered metric results to the authenticated consumer. |
| `quality-service-api` | Qualified | Installed validation reported a negative cost, an identifier mismatch and a missing companion file. UTC date and sheet filters selected the stored reports. |
| `analysis-performance` | Open | The recorded 1k, 5k and 10k cost-driver comparisons met the same-host threshold. Two seeded 50,000-draw synthetic runs reproduced identical draws with mean 3.9989 against 4. Per-module timing and memory thresholds still need paired results. |
| `deployment-pipeline` | External | AWS and Azure promotion command fixtures verified exact image promotion and readback. The target environments and live identity-bound execution still need evidence. |
| `api-docs` | Open | Packaged entry points, configuration, provider, model, reporting and operational HTTP usage have maintained instructions. Complete generated reference coverage of all public interfaces remains open. |
| `guides` | Open | The install, workbook, lab setup, valuation, report and dashboard walkthroughs have executable evidence. Full analysis tutorials and a troubleshooting and contribution walkthrough still need readback. |
| `training` | Qualified | The source archive carried the 38-second lab setup tutorial. Its terminal walkthrough reproduced the browser's synthetic download byte for byte. |
| `research-reporting` | Open | Source, comparators and software citation are indexed. A complete current journal reporting cross-check needs the actual study delivery edition. |
| `pilot-acceptance` | External | The synthetic lab workflow passed. A representative lab still needs to run the workflow and record acceptance. |
| `source-command-behavior` | Open | 71 of 74 command paths have recorded behavior at their documented scopes. The three remaining paths are named below. |
| `coverage-targets` | Open | Combined installed coverage reached 77.57%. The greater-than-90% target for all new components and the other named scopes need their own coverage receipts. |
| `extended-ci` | Open | Standard hosted gates and installed behavior passed. The planned mutation, metamorphic and contract test applicability and scheduled results remain open. |
| `branch-controls` | External | GitHub's read-only check reported an unprotected `main` with zero active branch rules. Required checks, deletion and force-push protection still need native evidence. |
| `dependency-updates` | External | Dependabot is present. The frozen Renovate and Dependency Dashboard handoff still needs native acceptance. |
| `coverage-oidc` | External | The installed coverage job produced XML and the workflow includes gated OIDC upload. Repository variables were unset and there is no Codecov commit receipt. |

## Command readback

Twenty-seven of the 30 command paths with previously outstanding checks
have new results. The other 44 retain [their original evidence](feature-audit.md#reproduction).
The eight analysis commands produced reports. Independent calculations
matched 96 source-based cost-driver groups and derived the DSA report's
20 assay and parameter summaries from 70 workbook scenarios. The PSA
report's means, medians and two quantiles matched all five sets of 10,000
archived draws at the reported precision. The benchmark, break-even,
budget-impact, cost-effectiveness and VOI command checks covered their
generated sections. The numerical component checks for those analyses are
recorded separately in the frozen audit.

The diagnostics read the original 35-sheet inventory and the expected
synthetic cell value 17. The two parser commands reopened three cost tables
and eight supporting tables. The configuration and extension demos wrote
their expected reports. The visualization and general report generators
produced their expected formats. The comprehensive report wrote six analyses
and their combined report. The optimizer wrote its simulation benchmark.
The coverage helper emitted JSON, XML and HTML. The T1 scenario assembler
wrote a valid 35-sheet workbook. The installed-command receipt tool recorded
the pinned lock, installed `prepare-data` path, a successful exit and digests
for the outputs in a separate scratch repository.

- `scripts/run_web.py` hands Flask the local host and disables the debugger
  and reloader. Its default path resolves inside the installed environment
  and health returned 503 even with prepared data in the consumer directory.
  `genomics-web --data-dir` accepts an explicit data directory, and that
  configured app's test client returned 200.
- `scripts/test_web_ui.py` uses a source directory and launches the system
  browser. The clean-install check used the installed dashboard tests and
  the earlier internal-browser result from the identical wheel.
- `tools/screen_release.py` is a repository utility. Its trained spaCy model
  and Presidio dependencies were outside the installed adapter environment.
  The official GitHub Actions result remains the security evidence for this
  candidate.

## Retained receipts

The 26 November clean-install receipts are in the restricted
`full-genomics-baseline.JxOhgH/g4-2-standalone.FIG6mc` catalogue entry.
The formula replay receipts were created on 25 November and their digests
were checked again for this qualification. The workbook, notebook, test
reports and object-level checks remain in authorised storage.

| Artefact | Edition and provenance | SHA-256 |
| --- | --- | --- |
| Frozen feature inventory | Legacy `fc8d4178bc3f5ce67cfc0547f7417272562c18a8` and retained issues | `aa17ce9b28b137c67ad58741681fb56840f07cabbcfd792a76314eef81d3c11e` |
| Genomics wheel | Dapane candidate `876db60`, 26 November | `68a744698434b216485c21e5652b4ad3c8ea771296257094963814ba826268f7` |
| Genomics source distribution | Dapane candidate `876db60`, 26 November | `b0fd937c1c33a8fac4df6d0ebfe8648a81c80a05e82bf590cfdeda36a94268fe` |
| Native Dapane wheel | Retained 0.1.0 comparator binding | `4bd6f77ba2c6c12e8674ded7e86cd6daa3d45fad0e387bc2cdc3d7feb74bd900` |
| Dependency lock | Adapter lock at `876db60` | `f5961d848b50537342ec4c6ce84a0feba8c91b10c10388c46b918caa18acdd66` |
| Full workbook replay | `exact-formula-replay.json`, 25 November | `2e8fb6133b913dfd103759eb36cedee6853a53c13c27e2f13e3fcc544b2dff4a` |
| Workbook comparator | `exact-formula-comparison.json`, 25 November | `616a67279b67f309993f93421b9c14e35ae032ab06d777057b28d99f15c488cc` |
| Native pathways | `exact-pathway-ledger.json`, 25 November | `f3a729ad81f1c0d2f86dc33e627377c9cf385cda66d4fc08342b6cead2568f90` |
| Consumer isolation | `results/isolation.json`, source and network denials | `ce6da1e6a1d927cf9fe909847eb5e3bf6390c7f9b47df859acbb420852f6f8b4` |
| Package surface comparison | `results/installed-surfaces.json`, frozen declarations and resources | `a15a994df003dff3702f68a90a6ec7e76be571848c75f1613e8f120f4d8ed683` |
| Packaged JUnit | `results/packaged.xml`, clean wheel | `42c60bcba87c551c2c396a3dfd165a69c90dbd6f70121d72ae038b5885d98c17` |
| Inherited JUnit | `results/inherited.xml`, frozen harness and clean wheel | `9d86fcdc3d189b40a602352ca2a5e7144414b5f1bc6dad1553c809c837369856` |
| Combined coverage | `results/combined.xml`, both isolated suites | `554c61b3b192a4de14f006b034d6f2581a577b0afd23e502d82dc0d358b3f14b` |
| Focused outcomes | `probes/focused-outcomes.json`, synthetic acceptance cases | `9b97f8b27b2be2b3c5c8e904bdcac5ce6f794eb6ea32009c68859b4efa0da295` |
| Taxonomy | `probes/actual-taxonomy/summary.json`, original label coverage | `ab81bf6dc198feb0abec124cdfa520aa76532ba3f37e0501fad60f0cbc8f00b7` |
| Command readback | `results/command-readback.json`, source and output comparisons | `067d69b5e66f4ff22a632b2247a952d001b1e6f6b6480d0c8a1a5f1a575b183e` |
| Compatibility and gaps | `results/follow-up-probes.json`, installed behavior with synthetic inputs | `d928515d426b4df7a6db535efee0d172c6609a5497ab6dbc79d45e9461059225` |
