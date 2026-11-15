# Reporting candidate review and fixes

Reviewed scope: E1–E2 at implementation commit `8f7c5dcbe14287759d62fd41d0804a92b734b75f`. This is an implementation-owner review. No extra worker or independent reviewer was created, and no independent-review claim is made.

## Findings resolved

| Finding | Reproduction or evidence | Resolution and regression |
| --- | --- | --- |
| Unknown JSON-LD classes could pass the graph boundary | `test_unknown_node_class_is_rejected` initially failed because `ReportingError` was not raised | Accept only the supported upstream export instance classes; the regression now passes |
| Unrecognized nested predicates could disappear during JSON-LD expansion | Review of nested node handling showed validation only covered the outer nodes | Recursively require known predicates before RDF parsing; `test_nested_unknown_predicate_is_rejected` passes |
| An existing ontology class could be accepted as a predicate merely because the term existed | Term-existence checking did not distinguish a property from a class | Require an upstream OWL object/datatype property, or the explicitly supported RDF/RDFS/DCTERMS properties; the class-as-predicate regression passes |
| Duplicate node identities could merge assertions | JSON-LD/RDF merges descriptions with identical subjects | Reject duplicate top-level node IDs; retain a regression; reject nested subjects outside the local reporting namespace |
| A regenerated positive fixture would provide a weaker native replay oracle | Earlier setup produced its expected report from the current native function | Commit immutable synthetic history/declaration files; require actual native replay of the stored report and fixed 150/60/90 reference values |
| Import ordering/format findings | Ruff reported imports and later three long fixture-loading expressions | Corrected; final lint and format checks both pass |

The complete 41-test suite was rerun from the clean, published implementation commit after these fixes. Two separate graph mutations still fail the actual upstream SHACL, so the negative acceptance does not rely solely on adapter-side exceptions.

## Boundary review

The source manifests contain exact identities and references, not copied ontology definitions, reporting wording or shapes. The importer reads the external files from local snapshots and never executes upstream scripts or follows imports. Applicability/status enumerations come from upstream SHACL. Contextual publications remain evidence artefacts.

The native field map accounts for every property in the ten pinned schema files. It explicitly preserves source evidence/access/validation meanings and leaves unsupported numerical/context projections unmapped. Native run-bundle 0.1 remains strict and unchanged. All monetary results come from the installed Rust implementation; the exporter embeds them without recomputation.

The record distinguishes reporting coverage, caller-declared review, upstream mapping review, computational replay, methodology and empirical validation. Domain-only instruments are explicit extraction gaps. Unknowns are rejected or retained as unresolved/unassessed; zero is not substituted for missing input.

Graph conformance alone does not certify the embedded JSON. The documentation states this limitation and directs callers through `export_evidence` with the original history and retained checkpoint. The standalone graph checker is not represented as a native replay or authenticity verifier.

## Remaining findings and decisions

1. **Registry consistency blocks integration.** This track has started and must be `in_progress`; the shared registry has not been changed by this lane. REP-IR-01 gives the exact row edit.
2. **Hosted coverage is absent.** Existing CI does not discover this test path. REP-IR-02 proposes explicit pinned optional qualification; no green root workflow may substitute for it.
3. **Upstream readiness remains qualified.** The selected UOGTO pack is an open PR, while the standards catalogue is merged. Source hashes establish the chosen snapshot, not a release or independent content review.
4. **Dependency warning retained.** RDFLib's parser reports a `ConjunctiveGraph` deprecation warning. No exception filter or gate change hides it.
5. **Broader integration is deferred.** Shared schema promotion, public installed verifier API, interval bundle representation and E3 consumer curation remain separate integrator/upstream work.

No shared core, CLI, Python module, schema, Cargo manifest/lock, workflow, root document, registry or other owner's files were changed. No upstream write, merge, release or infrastructure/credential change was performed.
