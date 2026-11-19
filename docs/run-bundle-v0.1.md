# Run-bundle contract 0.1

This independently versioned envelope completes the core-contract definition of
immutable run evidence. It wraps existing valuation requests/reports 0.1 or 0.2;
it does not change their numerical methods, schemas or historical digests.
The supported envelope qualification is **synthetic_candidate**. It is not a
production publisher, signed attestation, clinical programme or economic validation.

## Records and verification

The [strict schema](../schemas/bundles/0.1.schema.json) contains a full request,
full native report, source revision declaration, observation window, rate releases,
exclusions, optional asset-treatment annotations and a manifest digest. No field
is silently ignored. All references resolve to locally registered schemas, never
to network content. JSON Schema establishes structure; the
[verifier](../scripts/verify_run_bundle.py) additionally checks dates, references,
release coverage, exclusive asset treatments, lifecycle and exact Rust replay.
All valuation and allocation remain in Rust via an independently installed wheel.
The Python script validates/compares transport and evidence; it has no financial
formula implementation and is repository tooling, not part of the installed SDK.

| Concept | Representation |
| --- | --- |
| ResourceUse / ActivityMeasure | Request `usage.kind`, distinct targets and units; no activity-to-resource inference. |
| UnitQuote | Request `quotes`; report `quote_snapshots`; exact amount and denominator. |
| RateRelease | Envelope source ID/version, quote IDs, publication and retrieval dates. Every supplied quote belongs to exactly one release. |
| ValuationPolicy | Request/report policy plus explicitly declared capital treatment and observation scope. |
| ValuationLine / ComponentLedger | Unchanged native lines, components, allocations, capacity residual and object views. |
| RunBundle | This envelope binds the whole snapshot and its lineage without summing versions. |

Evidence/access/validation remain separate source declarations. A fabricated
`observed` label in a transport test is not actual observed data. Excluded,
missing and unsupported items appear in `excluded_inputs`, each with a reason.
Their IDs cannot also be valued line/use IDs. They are outside the calculated
scope, not imputed zeros or a claim of complete economic coverage.

## Immutable corrections and retractions

A series has an ordered chain of distinct bundle IDs:

- `create`: full request/report, null predecessor and reason.
- `replace`: a new full request/report, immediate predecessor digest and a reason.
  The prior snapshot is retained unchanged. Changes to quantities, sources or
  methods create a replacement; neither delta values nor negative costs are used.
- `retract`: a tombstone with predecessor/reason, null request/report/window and
  empty releases, exclusions and capital annotations. It withdraws the series;
  it does not generate a zero-cost report, refund or financial reversal.

The current profile rejects a second create, missing or reordered predecessors,
branching within one chain, duplicate IDs, decreasing recording dates, and any
revision after retraction. Restoration requires a future version or a new series
with an explicit external relationship; it is not silently inferred.

`verify_history(records, expected_head_digest=..., as_of=...)` verifies the entire
chain against a separately retained head checkpoint before selecting a snapshot.
That checkpoint detects a missing suffix, including an omitted retraction. It is
not proof of authorship: hashes/checkpoints supplied by the same untrusted producer
can be rewritten together. Signed provenance belongs to release qualification.
Selection uses `recorded_on <= as_of`; same-day revisions follow chain order.
Before the first record the result is `not_yet_known`; after a tombstone it is
`retracted`. Only `active` returns a native report. Never add historical reports
together. This is snapshot correction, not line-level event retraction.

## Dates and explicit preparation

Observation windows are half-open and nonempty; every service date must lie
inside them. Knowledge cutoff cannot exceed the recording date. Rate applicability
continues to use the native quote's effective dates, independently of price year.
Release dates satisfy publication <= quote known-from <= retrieval <= recording.
Retrieval can occur after a historical cutoff when reconstructing an as-known
analysis; it never permits use of a quote known after that cutoff.

Within a complete history, `(source_id, version)` identifies an immutable release:
its publication date and any declared non-null content digests must agree.
Repeated `(source_id, version, quote_id)` identities retain the exact supplied
quote snapshot, including decimal spelling and provenance declarations. A corrected
quote requires a new source version and a replacement bundle; recalculating a
report and its digest cannot legitimise conflicting release content. This check
remembers all prior snapshots, so dropping a quote from one snapshot and restoring
it later does not erase its identity. Conflicts return `release_conflict`.

Supplied quote subsets, quote/release list order and retrieval dates can change.
An undeclared content digest remains unknown, not proof of a different release;
declaring conflicting non-null digests is rejected even for different quote IDs
in the same snapshot. Exact snapshot preservation means changes to a repeated
quote's optional fields also require a new version. The verifier cannot establish
source authenticity, recognise undisclosed aliases, or compare histories that
the caller has not supplied. The independent correction reference changes a rate
from 90 to 100 under a new version: 1/2 hour at 100 plus 2/3 hour at 120 is 130.

An interval crossing a rate boundary must be explicitly segmented by its producer.
The independent reference uses 1/3 hour at 90 plus 2/3 hour at 120: 30 + 80 = 110.
Correcting the first duration to 1/2 gives 45 + 80 = 125. The interval/time model
is not inferred by the evaluator. Automatic interval integration stays in the
[Rust-kernel track](../conductor/tracks/rust_kernel_20261108/index.md).

`capital_treatments` selects one treatment for each declared asset in a view:
`acquisition_expenditure`, `prepared_accounting_charge` or
`prepared_economic_charge`. The first two require a financial-cost policy, the
third an economic-cost policy. Referenced resource lines exist and map once.
A synthetic acquisition quote of 12,000 and an independently prepared accounting
charge of 200 are alternative views, not a 12,200 total. The verifier rejects two
treatments for the same declared asset. It cannot identify undisclosed/aliased
assets or validate a prepared price. Depreciation, discounting, annuities and
other economic methods are not implemented by this envelope. Maintenance duration,
device life and one-time/recurrent preparation remain separate in the existing
[genomics cases](../fixtures/genomics-capacity/README.md).

## Identity, bounds and compatibility

`bundle_digest` is SHA-256 over UTF-8 `dapane:run-bundle:0.1\n` plus canonical JSON
of the envelope with only `bundle_digest` omitted. Canonical JSON sorts object keys,
preserves array order and exact string spellings, uses no insignificant whitespace,
and emits Unicode as UTF-8. Its separate namespace does not replace native input
or output digests. The entire stored report must reproduce exactly, including
engine/method identity, source/context and digests; a different implementation that
only happens to return the same total is insufficient. Source revision is a caller
declaration, not a certificate that the installed binary was built from that commit.

Limits: 16 MiB per canonical bundle, 64 MiB for a history, at most 100 revisions,
and the stricter existing request/numeric limits. Raw file input rejects duplicate
keys, non-finite constants and malformed UTF-8. No URL, command or file reference
inside a manifest is followed. Use only trusted local repository schemas and a
matching installed wheel. Unsupported envelope versions fail; retain this version
and its references when defining a later contract. The source numerical request
versions remain unchanged, including all v0.1 fixture digests.

## Run

After installing the matching wheel and existing development requirements:

```sh
python scripts/verify_run_bundle.py synthetic-history.json \
  --head sha256:RETAINED_HEAD_DIGEST --as-of 2026-02-10 \
  --output verified-selection.json
```

The head argument must be an actual retained digest, not the illustrative placeholder.
The CLI prints a verification status on stdout. Use `--output` to save the
canonical selection and its report to a new JSON file with owner-only mode
on POSIX systems. Store the file in a directory suitable for the underlying data.
Errors return exit 2 with a structured diagnostic on stderr and no financial stdout.
The installed-wheel acceptance suite constructs synthetic snapshots and an independent
manifest digest, then exercises replacement, withdrawal, corrupt/resealed payloads,
release mismatch, exclusions, alternate capital views and rate-boundary reference values.
