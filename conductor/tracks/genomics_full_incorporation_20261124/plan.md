# Implementation plan

Status: in_progress

## Phase 1 — Freeze the workbook and feature scope

- [x] G1.1 Freeze the read-only v15 workbook, provider and Dapane revisions, relevant maintained plan/issue versions, legacy invocation and source rights. Retain the exact source and a runnable legacy comparator. [Freeze and comparator](verification.md#frozen-sources)
- [x] G1.2 Start from the existing workbook catalogue. Enumerate all worksheet regions, inputs, formula coordinates, references, branches, errors and output views. Reconcile 35 sheets and 36,411 formula cells against the original bytes. [Workbook ledger evidence](verification.md#workbook-ledger)
- [x] G1.3 Inventory the actual public and compatibility surfaces from package entry points, source, docs and tests. Reconcile every documented planned deliverable against implementation and tests and map each distinct outcome to this plan. [Feature coverage record](feature-coverage.md)
- [x] G1.4 Verify both ledgers against the frozen sources. Link the existing replay evidence to the rows it covers and leave every gap visible. [Replay cross-reference](verification.md#prior-replay-cross-reference)

## Phase 2 — Complete workbook parity

- [x] G2.1 Establish baseline and branch comparison cases from the original workbook and its legacy evaluator. Add independent reference cases for units, rates, allocations, subtotals, branch arithmetic and rounding before extending the costing paths. [Independent formula baseline](verification.md#independent-formula-baseline)
- [x] G2.2 Reuse the workbook reader and formula engine to reproduce every original input, formula dependency, result and error. Close the missing subtotals and qualify all historical reference and division-error cases. [Exact formula replay](verification.md#exact-historical-formula-replay)
- [x] G2.3 Compose the full detailed pathway and resource ledger, including equipment and capital, throughput, bioinformatics compute and storage. Reproduce every summary, graph input and sensitivity branch with the original currency, units and denominators. [Pathway and resource evidence](verification.md#detailed-pathway-and-resource-costing)
- [~] G2.4 Verify every workbook ledger entry and compare independent totals, branches and rounding through the installed CLI and Python paths. Require complete accounting of affected cells and evaluated outcomes.

## Phase 3 — Deliver full legacy feature coverage

- [ ] G3.1 Lock normal-entry-point tests for the frozen feature ledger, including imports, command options, configuration and input templates, supported workbook variants, error and recovery behaviour, and all user-facing outputs.
- [ ] G3.2 Incorporate the provider's remaining calculation, data-preparation, scenario, workflow and analysis paths. Reuse existing code and dependencies and use Dapane for common valuation and reconciliation.
- [ ] G3.3 Incorporate the legacy reports, table exports, visualization, web interactions, workbook revision handling and plugins. Qualify the appropriate native or browser entry points and their configuration and error behaviour.
- [ ] G3.4 Deliver every remaining planned outcome in the feature ledger, including compute and storage detail, scaling, extensible input and external price interfaces, advanced allocation and prediction, and quality, security, monitoring and performance commitments.
- [ ] G3.5 Check all feature rows against installed behaviour and the original acceptance or documented contract. Require reproducible evidence for every shipped and planned outcome.

## Phase 4 — Qualify an installable successor

- [ ] G4.1 Package the optional genomics component and legacy entry points under Dapane ownership. Verify its dependencies and notices and preserve ingestion of authorised, versioned sources.
- [ ] G4.2 Run the full workbook and feature ledgers from clean installed artifacts with the legacy checkout absent. Reconcile any historical or statistical differences against their recorded oracle and keep all restricted source data outside public artifacts.
- [ ] G4.3 Review and fix the candidate, run the normal release and exact-head GitHub-hosted offline-security gates, and record both verified coverage counts with their supporting evidence.

## Phase 5 — Preserve assets and rehearse cutover

- [ ] G5.1 Inventory unique code, refs, tags, scholarly citations, study sources and workbook assets. Record preservation location, digest, rights, successor links and consumer migration steps.
- [ ] G5.2 Rehearse clean restoration and rollback. Compare representative restored historical outputs and check that the successor runs with the provider checkout and public fetch unavailable.
- [ ] G5.3 Record the repository retirement decision and any remaining rights or consumer dependencies. Prepare the evidence for a later authorised archive or visibility change.
