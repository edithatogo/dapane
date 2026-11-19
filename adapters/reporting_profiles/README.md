# Reporting evidence candidate 0.1

This optional, repository-local adapter implements E1–E2 of the
[reporting track](../../conductor/tracks/reporting_profiles_20261108/index.md).
It reads a verified **synthetic** run-bundle history and explicit reporting
declarations, then writes a separate JSON-LD 1.1 evidence document. The installed
Dapane wheel performs all valuation and allocation. Importing Dapane does not
import this adapter or an RDF dependency.

The candidate does not change the native request, report, interval or bundle
schemas. It is not included in the ordinary Dapane wheel or CLI. Its current
executed host is CPython 3.12 on Linux; additional hosts and installation as an
SDK extra require integration qualification.

## Pinned source products

| Owner | Exact source | Observed status on 15 November 2026 |
| --- | --- | --- |
| UOGTO | `7e9075b8fd77543fc8853fab20319415cb86597d` | [PR #128](https://github.com/edithatogo/UOGTO/pull/128) open and unmerged; no released-pack claim |
| standards_check | `d1f1137edfa5375e0225ca2216903ce5583a44f0` | Catalogue incorporated through [PR #65](https://github.com/edithatogo/standards_check/pull/65); both selected JSON files match observed main `d592bb3fa7972f421a1a68ec28e1938fd3d52136` |
| Dapane | `e34f87c9df39a2132fecee142431cdeefb732471` | Native schema baseline used by the field map |

[sources.lock.json](sources.lock.json) records seven exact files with SHA-256,
byte counts and Git blob identities. No upstream ontology, context, shapes,
instrument wording or catalogue content is vendored into this directory.
Supply local snapshots containing those files. The loader performs no downloads,
OWL imports or execution of upstream scripts.

[catalogue-map.json](catalogue-map.json) contains identity joins only: 26 source
records, 106 original item identifiers and 12 project-defined profile IRIs. The
loader checks these against the actual pinned RDF and catalogue, including the
distinction between 20 instrument versions and six contextual publications,
31 domains and 125 topic mappings. Source extraction qualifications and original
instrument/version/item identifiers survive the export. Identifier verification
and editorial mapping review remain upstream declarations. File hashes do not
verify publisher text, scientific truth or a source's authority.

The snapshot has **no full-checklist transcriptions**. A profile with a
domain-only instrument records that extraction gap explicitly; zero mapped
items is never described as complete coverage. Protocols and reviews remain
evidence artefacts. Appraisal profiles are rejected by this reporting-only
candidate. Selecting a UOGTO composition does not imply external endorsement.

## Native and semantic boundary

[contract-map.json](contract-map.json) accounts for all 281 property occurrences
in 49 object-schema locations across ten native/bundle/interval schema files.
Each field has an explicit reference rule or an unmapped reason. A changed
native schema fails the source-map check until its mapping is reviewed.

The exporter instantiates UOGTO study, policy, reporting-assertion and evidence
classes. It references existing instrument/profile/requirement IRIs and never
declares their meanings. The full selected native bundle is retained as an
`rdf:JSON` literal, including decimal strings, rational pairs, source states,
excluded inputs, exact/rounded totals and method/digest identities.

Numerical and many-to-many context records are not forced into a lossy RDF
ledger. For example, UOGTO's current decimal allocation shapes do not represent
every largest-remainder share or multi-object native record directly. The
adapter therefore does not reinterpret those allocations or replace native
per-generated-segment half-even rounding with aggregate rounding. Interval
envelopes themselves are not accepted by bundle 0.1; this adapter does not invent
an interval-to-bundle conversion.

Valuation basis is an explicit declaration. `economic_cost` permits
`economic-opportunity`; `financial_cost` requires an explicit choice between
`financial-expenditure` and `accounting-cost`; funding permits only
`funding-valuation`; charge permits an explicitly justified `tariff-valuation`.
Observed payment has no accepted native counterpart in this candidate. These
compatibility checks do not establish the economic appropriateness of the
caller's choice. A costing method must also be chosen explicitly from UOGTO;
it is not inferred from the native calculation-method identifier.

## Reporting declarations and coverage

The input format is `dapane-reporting-declarations/0.1`. See the complete
[synthetic declaration](fixtures/synthetic-declarations.json). Unknown and
missing fields are rejected.

| Field | Contract |
| --- | --- |
| `format` | Exact reporting declaration version |
| `bundle_digest` | The selected native snapshot, independently of the history head |
| `source_commits` | Both exact commits from the source lock |
| `study` | Label, explicit UOGTO costing method, compatible basis and rationale |
| `profiles` | One to twelve distinct pinned profile IDs, each with explicit applicability and rationale |
| `assertions` | At most 106 distinct original instrument/version/item declarations |

Each assertion supplies `applicability`, `reporting_status`, `rationale`,
`review_status` and `evidence`. Review is `not-reviewed` or `reviewed`, always
labelled as caller-declared. The separate upstream editorial-review qualification
is retained even when the caller marks their assertion reviewed.

The applicability and reporting-status enumerations are read directly from the
pinned upstream SHACL. Reporting distinguishes `reported`, `partial`,
`not-reported` and `not-assessed`; applicability independently distinguishes
`applicable`, `not-applicable` and `unresolved`. A reported/partial assertion
requires nonempty evidence; a not-applicable assertion requires a rationale.
Omitted selected items remain unresolved and not assessed. An unresolved profile
does not automatically make its items applicable. Overlapping profiles are
deduplicated by original instrument/item identity.

Evidence comprises a strict RFC 6901 pointer into the selected bundle and a
note. The pointer must resolve to nonempty content; explicit zero remains valid.
The exported evidence location combines the bundle's local instance IRI and
that pointer. These are local evidence addresses, not fetched web resources.
Only public synthetic source declarations are supported in this candidate;
the labels themselves are not a privacy classifier or source certification.

Coverage is a matrix of applicability and reporting states over **mapped**
items, with separate domain-only instrument gaps. It produces no compliance,
quality or methodological score. Methodological appraisal, native computational
verification and empirical validation remain distinct dimensions.

## Reproduce the synthetic example

Use an isolated environment, the exact candidate Dapane wheel identified in
the track's [verification record](../../conductor/tracks/reporting_profiles_20261108/verification.md),
and the locked optional dependencies:

```sh
python -m pip install --no-deps /path/to/exact/dapane-candidate.whl
python -m pip install --require-hashes -r adapters/reporting_profiles/requirements.lock
```

Prepare read-only local source snapshots through ordinary Git checkout/archive
at the commits in the source lock. They must have this layout:

```text
/path/to/reporting-sources/uogto/ontologies/...
/path/to/reporting-sources/uogto/shapes/...
/path/to/reporting-sources/uogto/jsonld/...
/path/to/reporting-sources/uogto/validation/...
/path/to/reporting-sources/standards_check/reconciliations/costing/...
```

From the Dapane repository root, run:

```sh
python -m adapters.reporting_profiles \
  adapters/reporting_profiles/fixtures/synthetic-history.json \
  adapters/reporting_profiles/fixtures/synthetic-declarations.json \
  --uogto /path/to/reporting-sources/uogto \
  --standards-check /path/to/reporting-sources/standards_check \
  --head sha256:7b62013bb19a70da8654fba7a4e8dccfe239b75660a4cc363c8eec8fafb9e58f \
  --as-of 2026-11-15 > synthetic-evidence.jsonld
```

The static fixture is explicitly synthetic. Its native result is 150.00 with
60.00/90.00 infant views. The declaration demonstrates one partial item, leaving
the other 88 selected items unresolved and not assessed. It does not assert
complete reporting of a newborn programme.

The exporter invokes the existing [bundle verifier](../../scripts/verify_run_bundle.py)
to check schema, lifecycle, retained history checkpoint and exact installed-Rust
replay before exporting the selected snapshot. The caller supplies the retained
head checkpoint; a digest supplied alongside a rewritten history is not proof
of authorship. Retractions and not-yet-known selections produce no report.

Output is written to stdout only after all validation succeeds. Contract failures
return exit 2 and structured stderr with no financial stdout. The shell may still
create an empty redirected file when a command fails; inspect the exit status.

## SHACL and negative fixtures

The exporter checks its graph against the actual pinned UOGTO shapes, ontology
and source catalogue with network retrieval, OWL imports, inference, advanced
rules and JavaScript disabled. It accepts only the fixed inline prefix context,
known export classes/properties and local instance subjects. Unknown predicates,
nested contexts, duplicate nodes and attempted upstream redefinitions fail.

`validate_jsonld` reports graph conformance. It is not a native replay verifier,
source-authenticity check or validator of the truth of the embedded JSON claims.
Use `export_evidence` with the original history and retained checkpoint to obtain
replayed output. SHACL success is not methodological correctness or empirical
validity. The current RDFLib JSON-LD parser emits a dependency deprecation warning
about `ConjunctiveGraph`; the tests leave that warning visible.

The [negative declarations](fixtures/README.md) and tests cover missing evidence,
unjustified not-applicable assertions and mismatched source versions. Additional
tests mutate generated graphs and require **actual upstream SHACL failure** for
missing evidence and a missing applicability rationale.

```sh
DAPANE_REPORTING_SOURCES=/path/to/reporting-sources \
  python -m unittest discover -s adapters/reporting_profiles/tests -v
ruff check adapters/reporting_profiles
ruff format --check adapters/reporting_profiles
```

The tests also cover source tampering, duplicate/unknown fields, original version
mismatches, native schema/replay errors, retractions, rational values, half-even
rounding, no-network operation and static native valuation without reporting
dependencies. Existing CI does not discover this new directory automatically.
The [handoff](../../conductor/tracks/reporting_profiles_20261108/handoff.md) requests
the required registry and optional CI integration from the sole integrator.

E3 consumer curation, independent content review, broader item extraction,
installed SDK integration and shared schema promotion remain separate work.

## Format references

- [W3C JSON-LD 1.1 Recommendation](https://www.w3.org/TR/2020/REC-json-ld11-20200716/), including JSON literals.
- [W3C SHACL Recommendation](https://www.w3.org/TR/shacl/), for graph conformance rather than empirical validity.
- [Pinned UOGTO reporting semantics](https://github.com/edithatogo/UOGTO/blob/7e9075b8fd77543fc8853fab20319415cb86597d/docs/costing-valuation-reporting.md).
- [Pinned standards catalogue](https://github.com/edithatogo/standards_check/tree/d1f1137edfa5375e0225ca2216903ce5583a44f0/reconciliations/costing).
