# Synthetic reporting fixtures

All persons, resource assumptions and amounts are fictional. These files use the
existing Dapane newborn example and retain its 150.00 total and 60.00/90.00 infant
views. They provide no programme, clinical or empirical evidence.

| File | Expected result |
| --- | --- |
| [synthetic-history.json](synthetic-history.json) | One complete synthetic bundle; current installed Rust must reproduce the stored report exactly |
| [synthetic-declarations.json](synthetic-declarations.json) | Version-bound profile selection, one partial assertion, 88 unresolved/not-assessed defaults; conforms to pinned upstream SHACL |
| [reported-without-evidence.json](reported-without-evidence.json) | `missing_evidence`; no output |
| [not-applicable-without-rationale.json](not-applicable-without-rationale.json) | `missing_rationale`; no output |
| [wrong-source-version.json](wrong-source-version.json) | `source_version_mismatch`; no output |

The negative declaration files deliberately contain invalid assertions. Tests
also remove evidence or rationale directly from a generated RDF graph and
require nonconformance from the actual upstream shapes. No shapes or instrument
definitions are duplicated here.

Source-revision and evidence/access/validation fields are declarations. Native
replay verifies transport and computation; it does not certify the binary's build
origin or turn these synthetic sources into observed evidence.
