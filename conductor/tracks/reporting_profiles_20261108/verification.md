# E1–E2 executed verification

## Qualified source and limits

The exact implementation commit is [8f7c5dcbe14287759d62fd41d0804a92b734b75f](https://github.com/edithatogo/dapane/commit/8f7c5dcbe14287759d62fd41d0804a92b734b75f), tree `7bbc79089737c462460ba3029a901e60f86ff68d`, based on main `e34f87c9df39a2132fecee142431cdeefb732471`. It was fetched from the published branch and tested from a clean checkout on 15 November 2026. The subsequent handoff commit changes only this track's documentation and evidence. The PR description identifies that final head separately.

Qualification is limited to this repository-local synthetic adapter on CPython 3.12.14, Linux x86_64, glibc 2.41. The exact environment is recorded in [environment.json](evidence/environment.json). The adapter is not part of the ordinary native wheel or CLI. No real patient, programme, payroll or other private records were used.

The implementation was reconstructed after an execution-environment interruption, then executed again. Earlier prototype and pre-reconstruction passes are not used as evidence for this published source. [execution.json](evidence/execution.json) records the actual commands, UTC times, exit codes, logs, and every adapter file's byte count, SHA-256 and Git blob identity.

## Results on the exact implementation

| Check | Actual outcome | Retained evidence |
| --- | --- | --- |
| Reporting acceptance | **41 passed**, 27.030 seconds reported by unittest | [Full test log](evidence/reporting-unittest.log) |
| Existing native interval validator with the retained CLI | Passed; independent exact segment/reference values, parent lineage, conservation, immutable digests, scalar replay and ordering; 9 schema-negative cases, 11 runtime rejections and 15 tampered-report controls | [Native interval log](evidence/native-intervals.log) |
| Ruff 0.17.4 lint | Passed | [Lint log](evidence/ruff-check.log) |
| Ruff format check | Passed; eight Python files already formatted | [Format log](evidence/ruff-format.log) |
| Existing Conductor lifecycle unit tests | **12 passed** | [Lifecycle log](evidence/conductor-lifecycle.log) |
| Installed dependency consistency | Passed; 16 installed packages compatible | [Dependency log](evidence/dependency-check.log) |
| Native source equivalence, release artifact source versus base | No differences in core/CLI/Python source directories, Python module or Cargo.lock | [Execution receipt](evidence/execution.json) |
| Whole-repository Conductor validation with final track records | **Failed: one registry marker/status mismatch** | [Conductor log](evidence/conductor-validation.log) and [REP-IR-01](handoff.md) |

The Conductor failure is retained. The track is correctly `in_progress`, but the shared registry still says `new`. The integrator owns that row. This is an integration blocker, not a passed or waived gate.

## Source qualification

The adapter verifies all seven local source files against SHA-256, byte counts and Git blob IDs before parsing. The pinned UOGTO import receipt must name the same standards_check commit and exact registry/mapping hashes.

| Source | Exact commit | Observed status |
| --- | --- | --- |
| UOGTO | `7e9075b8fd77543fc8853fab20319415cb86597d` | [PR #128](https://github.com/edithatogo/UOGTO/pull/128) open/unmerged; not a released-pack claim |
| standards_check | `d1f1137edfa5375e0225ca2216903ce5583a44f0` | Matching import snapshot; catalogue [PR #65](https://github.com/edithatogo/standards_check/pull/65) merged; selected files byte-identical to observed main `d592bb3fa7972f421a1a68ec28e1938fd3d52136` |
| Dapane schemas | `e34f87c9df39a2132fecee142431cdeefb732471` | Ten unchanged native/bundle/interval schema files |

The [source lock](../../../adapters/reporting_profiles/sources.lock.json) is the complete file manifest. Runtime checks establish 26 source records, 20 instrument versions, six contextual publications, 31 domains, 106 original item IDs, 125 topic mappings and 12 project-defined profiles. There are no full-checklist transcriptions. The [contract map](../../../adapters/reporting_profiles/contract-map.json) accounts for 281 property occurrences across 49 object-schema locations, with explicit unmapped reasons where a direct RDF projection would lose meaning.

These are repository identity and declared extraction checks. They do not independently verify publisher content, endorse profiles, turn protocols into reporting checklists, or complete the upstream editorial review.

## Exact installed native artifact

This lane used the release owner's existing artifact; it did not build or publish a new native package.

- Source: `a4ddde7ae7a799e37a5d594cde9c195ff057bc5e`, tree `740c1f379e69db746a5d56ec7212e7676924b473`.
- [Release-assurance run 43677159295](https://github.com/edithatogo/dapane/actions/runs/43677159295), [artifact 14145769688](https://github.com/edithatogo/dapane/actions/runs/43677159295/artifacts/14145769688), `candidate-python-3.12`.
- Downloaded ZIP SHA-256: `6fb1f614edc8d8fba524aadf2f97d4968922cdb54e1cf91fc18abbe9085e9120`. All 20 listed member checksums were verified during recovery; member paths were normalized only to remove a leading `./`.
- Wheel: `dapane-0.1.0-cp312-cp312-manylinux_2_34_x86_64.whl`, 722,186 bytes, SHA-256 `17421cb91cd68fde202eaadc361a4f7d5395efb12042d539cf1f82da2033e46c`.
- CLI: 1,446,888 bytes, SHA-256 `2d3f3c5b54399a3613d4b6d97e8538cadc3074192fdd076f261118d1a67b03a2`.
- Artifact evidence JSON SHA-256: `65c063e9541bcb3bc2aa277d5458c396a2733469ea3cdffb39d0ceee670fd49e`.

The selected native source directories and Cargo.lock match the base. Release packaging metadata and licence/notice files differ, so no whole-tree identity is claimed. The wheel was installed with `--no-deps`; the optional reporting dependencies were installed with hash checking and binary-only packages from the dedicated lock. The reporting commit is not relabelled as the wheel's build source. [native-artifact.json](evidence/native-artifact.json) retains these identities and limits.

## What the 41 tests establish

The immutable positive fixture replays the existing synthetic 150.00 total and 60.00/90.00 infant views through installed Rust. The newborn profile contains 89 mapped requirements: one partial assertion with a resolved evidence pointer, and 88 unresolved/not-assessed defaults. The actual pinned upstream SHACL conforms.

Negative cases include missing evidence, missing not-applicable rationale, wrong source and original instrument versions, unknown IDs/states/fields, duplicate assertions/profiles/nodes, private or non-synthetic source declarations, unresolved profile applicability, invalid/empty pointers, duplicate JSON keys, nonfinite values, source tampering and symbolic links. Two tests remove evidence or rationale directly from generated JSON-LD and require nonconformance from the actual upstream shapes.

The native boundary tests reject schema/replay changes, altered history checkpoints and inactive/retracted snapshots. They preserve native JSON through RDF JSON-literal round trips, exact rational `106/3` versus rounded `35.34`, and four half-even `0.005` lines whose rounded total is `0.00` while the exact total is `0.02`. The separate existing interval validator exercises the accepted per-generated-segment behavior. The adapter performs no monetary calculation.

Additional controls reject remote/nested contexts, unknown classes and predicates, ontology classes used as properties and upstream node redefinitions. A network tripwire covers source loading/export. An isolated `python -I -S` subprocess loads only the installed native module and executes the static baseline with RDF/reporting imports absent. CLI success produces complete JSON; contract failure returns exit 2 with no financial stdout.

## Unexecuted or unresolved

- Hosted execution of this new test directory: not supplied by existing CI; requested in REP-IR-02.
- Final integrated-head qualification after registry/CI changes or rebasing: must be performed by the integrator.
- Installed reporting SDK extra, shared reporting schema registration and interval-to-bundle export: not implemented.
- Other Python versions/platforms, fresh native build/Cargo suite in this lane, optional-dependency advisory/licensing qualification and offline security: no new execution claim.
- Independent review of scientific sources/editorial mappings, broader item extraction, methodological appraisal, empirical validation and E3 curation: open.
- RDFLib emits a visible `ConjunctiveGraph` deprecation warning during JSON-LD parsing. It is not suppressed and did not fail the checks.

SHACL validates graph conformance. It does not validate truth, native replay or the contents of arbitrary embedded JSON. The exporter separately invokes the existing native bundle verifier before creating a graph. Source labels and review statements remain declarations.

See the [adapter README](../../../adapters/reporting_profiles/README.md) for reproduction commands and the [handoff](handoff.md) for the concrete shared changes.
