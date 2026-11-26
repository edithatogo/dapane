# Implementation plan

Status: completed

## Phase 1 — Freeze the workbook and feature scope

- [x] G1.1 Freeze the read-only v15 workbook, provider and Dapane revisions, relevant maintained plan/issue versions, legacy invocation and source rights. Retain the exact source and a runnable legacy comparator. [Freeze and comparator](verification.md#frozen-sources)
- [x] G1.2 Start from the existing workbook catalogue. Enumerate all worksheet regions, inputs, formula coordinates, references, branches, errors and output views. Reconcile 35 sheets and 36,411 formula cells against the original bytes. [Workbook ledger evidence](verification.md#workbook-ledger)
- [x] G1.3 Inventory the actual public and compatibility surfaces from package entry points, source, docs and tests. Reconcile every documented planned deliverable against implementation and tests and map each distinct outcome to this plan. [Feature coverage record](feature-coverage.md)
- [x] G1.4 Verify both ledgers against the frozen sources. Link the existing replay evidence to the rows it covers and leave every gap visible. [Replay cross-reference](verification.md#prior-replay-cross-reference)

## Phase 2 — Complete workbook parity

- [x] G2.1 Establish baseline and branch comparison cases from the original workbook and its legacy evaluator. Add independent reference cases for units, rates, allocations, subtotals, branch arithmetic and rounding before extending the costing paths. [Independent formula baseline](verification.md#independent-formula-baseline)
- [x] G2.2 Reuse the workbook reader and formula engine to reproduce every original input, formula dependency, result and error. Close the missing subtotals and qualify all historical reference and division-error cases. [Exact formula replay](verification.md#exact-historical-formula-replay)
- [x] G2.3 Compose the full detailed pathway and resource ledger, including equipment and capital, throughput, bioinformatics compute and storage. Reproduce every summary, graph input and sensitivity branch with the original currency, units and denominators. [Pathway and resource evidence](verification.md#detailed-pathway-and-resource-costing)
- [x] G2.4 Verify every workbook ledger entry and compare independent totals, branches and rounding through the installed CLI and Python paths. Require complete accounting of affected cells and evaluated outcomes. [Branch and native parity](verification.md#formula-branch-and-installed-native-verification)

## Phase 3 — Deliver full legacy feature coverage

- [x] G3.1 Lock normal-entry-point tests for the frozen feature ledger, including imports, command options, configuration and input templates, supported workbook variants, error and recovery behaviour, and all user-facing outputs. [Installed legacy baseline](verification.md#installed-legacy-feature-contract)
- [x] G3.2 Incorporate the provider's remaining calculation, data-preparation, scenario, workflow and analysis paths. Reuse existing code and dependencies and use Dapane for common valuation and reconciliation. [Dapane-built runtime](verification.md#dapane-built-legacy-runtime)
- [x] G3.3 Incorporate the legacy reports, table exports, visualization, web interactions, workbook revision handling and plugins. Qualify the appropriate native or browser entry points and their configuration and error behaviour. [Report and web qualification](verification.md#reports-web-and-compatibility-tools)
- [x] G3.4 Deliver every remaining active outcome in the feature ledger, including compute and storage detail, scaling, extensible input and external price interfaces, advanced allocation and prediction, and quality, security, monitoring and performance commitments. [Implementation findings](feature-audit.md#findings)
- [x] G3.5 Audit all frozen feature rows against installed behaviour and the original acceptance or documented contract. Record each reproduced result and the outstanding implementation, evidence or native work for G3.4 and G4. [Feature audit and crosswalk](feature-audit.md)

## Phase 4 — Qualify an installable successor

- [x] G4.1 Package the optional genomics component and legacy entry points under Dapane ownership. Verify its dependencies and notices and preserve ingestion of authorised, versioned sources. [Standalone installed artifacts](verification.md#standalone-installed-artifacts)
- [x] G4.2 Run the full workbook and active feature ledgers from clean installed artifacts with the legacy checkout absent. Require reproducible evidence for every shipped and active planned outcome. Reconcile any historical or statistical differences against their recorded oracle and keep all restricted source data outside public artifacts. [Clean-install qualification and remaining outcomes](g4-2-qualification.md)
- [x] G4.3 Review and fix the candidate, run the normal release and exact-head GitHub-hosted offline-security gates, and record both verified coverage counts with their supporting evidence. [Acceptance counts and GitHub controls](g4-3-acceptance.md) and [remaining outcome verification](g4-closeout.md)

All 112 active outcomes are qualified. The
[representative lab pilot](../../roadmap.md#representative-genomics-lab-pilot)
and [live dashboard promotion](../../roadmap.md#live-genomics-dashboard-promotion)
moved to the roadmap on 26 November 2026. Both remain in the frozen
114-outcome inventory. [Acceptance evidence](g4-closeout.md)

## Phase 5 — Preserve assets and rehearse cutover

- [x] G5.1 Inventory unique code, refs, tags, scholarly citations, study sources and workbook assets. Record preservation location, digest, rights, successor links and consumer migration steps. [Preservation and restoration](verification.md#preservation-and-restoration)
- [x] G5.2 Rehearse clean restoration and rollback. Compare representative restored historical outputs and check that the successor runs with the provider checkout and public fetch unavailable. [Preservation and restoration](verification.md#preservation-and-restoration)
- [x] G5.3 Record the repository retirement decision and any remaining rights or consumer dependencies. Prepare the evidence for a later authorised archive or visibility change. [Retention decision](verification.md#retirement-decision)

## Phase 6 — Reuse workbook formula and valuation rules

- [x] G6.1 Apply one workbook formula to declared ranges and reuse calculation patterns across the replay. [Formula families and range readback](verification.md#shared-workbook-calculations)
- [x] G6.2 Share booked inputs across currency variants and build reports from the native valued lines. [Valuation and reporting evidence](verification.md#shared-workbook-calculations)
- [x] G6.3 Verify the frozen workbook, changed inputs and installed artifact. [Exact comparisons and installed tests](verification.md#shared-workbook-calculations)
- [x] G6.4 Reuse ordered subexpressions across formula families and qualify six workbook scenarios with exact error parity. [Nested calculations and six-scenario parity](verification.md#nested-calculations-and-six-scenario-parity)
- [x] G6.5 Reproduce all six comparisons in a maintained local runner using two installed versions. [Repeatable scenario verification](verification.md#repeatable-scenario-verification)
- [x] G6.6 Carry the zero and 13.75% adjustment-rate scenarios through native costing and the pathway report. [Native adjustment scenarios](verification.md#native-adjustment-scenarios)

Integration requires the official offline-security check on the exact PR head
and the receiving `main` revision. GitHub Actions retains the run for each
commit. [Hosted workflow](../../../.github/workflows/offline-ai-security.yml)
