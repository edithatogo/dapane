# Observed-event imports and contracts

This optional package decodes a bounded XES 2.0 XML and OCEL 2.0 JSON profile
into validated observation contracts. Original bytes remain the authority for
native attributes, object history and evidence. The adapter computes no prices.

- XES uses UTF-8, the XES namespace, explicit trace and event identity, offset
  timestamps and scalar event attributes. Interval anchors must have the
  appropriate start and complete labels on the same activity and trace. Supply
  a separately versioned sidecar with object identities, qualified links and
  explicit pairings. The trace structure supplies none of those associations.
- OCEL permits declared string, time, signed 64-bit integer, floating and Boolean
  attributes. It checks typed declarations, history instants, relationships and
  identifier uniqueness, with source order and offsets preserved in original bytes.
- Both paths accept up to 8 MiB of uncompressed UTF-8. Timestamps require a known
  offset and at most nine fractional digits. XES disables DTDs and external
  resolution and caps XML nodes. The JSON decoder requires object records and
  rejects duplicate or unknown fields. The typed validation bounds collections.
- The import returns a retained source slice and source-digest-bound typed
  projection. Preserve the separate mapping revision with the source snapshot.
  The adapter supplies no default quantities, calendar dates or attribution.

The XES provider is MIT/Apache-2.0 roxmltree 0.21.2, with serde_json 1.0.154 for
OCEL and time 0.3.55 for offsets. Their immutable crate versions and transitive
closure are recorded in Cargo.lock. The provider is isolated from the core.
[Raw import and Kairos review](../../conductor/tracks/process_models_20261108/native-and-kairos-review.md)

## Implemented contract

`validate_contract(Snapshot)` checks a caller-prepared typed projection and
returns an immutable `ValidatedContract`. The projection contains source
identity, observation coverage, event/object references, qualified relationships
and one assertion per underlying use. Native attributes/history remain in the
retained source artifact; this projection does not replace that native model.

`require_costing_ready()` requires every assertion to have complete observed
anchors, an explicit quantity and a costable kind. It returns the full borrowed
assertion list or an error; it never returns a partially acceptable list. This
is only pre-valuation completeness. It does not verify the source, qualify the
decoder/dependencies, select a quotation or service date, allocate expenditure
or produce a monetary result.

### Identity and corrections

Identity is the source namespace, immutable snapshot revision and source-native
ID. Neither time, activity name nor array/trace position synthesizes an ID. A
raw SHA-256 digest is retained; this typed API checks its spelling only, since
no source bytes enter it. The fixture auditor separately hashes the committed
raw fixture bytes.

Duplicate object/event/use IDs fail, including exact copies. There is no
last-write-wins behavior or silent deduplication. An identical snapshot may be
validated in another invocation, but repeated use rows in one invocation fail.
Event and object IDs occupy separate typed domains. Unicode and case remain
literal. Similar-looking simultaneous uses are not merged.

Replace/retract actions fail visibly. A negative quantity cannot silently
encode a correction. A future correction protocol must retain supersession
and replay lineage; choosing a new revision alone does not reconcile uses.
Different aliases for the same real use cannot be detected reliably from names
or timestamps. A future source adapter must supply stable source identity or a
qualified explicit alias mapping.

### Time, ordering and censoring

Instants are already-decoded UTC Unix seconds plus nanoseconds. Years
0001–9999 and fractional nanoseconds below one billion are accepted. String
timestamp parsing, timezone conversion, leap seconds and raw format precision
are still native-decoder qualification work. Original offset spelling stays in
the retained source. No current time or local timezone is consulted.

Observed anchors are within the inclusive window endpoints. A completion at the
cutoff can close an occupancy interval; occupancy itself is half-open
`[start, end)` and requires `start < end`. Missing timestamps and out-of-window
anchors fail. Same-time events keep distinct IDs, with no inferred causal order.

Intervals explicitly name their anchor event IDs. Adjacent events or matching
activity names never establish a pair. Missing anchors must agree with censoring:

| Start | End | Censoring | Complete observed assertion selection |
| --- | --- | --- | --- |
| Present | Present | None | Eligible if all other checks pass |
| Absent | Present | Left | Blocked |
| Present | Absent | Right | Blocked |
| Absent | Absent | Both | Blocked |

Censored records remain inspectable. The cutoff is never substituted for a
missing endpoint, and neither elapsed duration nor a missing quantity is filled
in. Timestamp-to-calendar segmentation and exposure methods remain separate
integration decisions.

### Physical use and object context

Each assertion supplies its resource, case-sensitive unit, observed/assumed/
simulated basis and exact quantity. Quantity is an unsigned rational pair of
decimal strings, each at most 96 digits, with a nonzero denominator. This
boundary does not reduce, calculate, split or round it. Explicit zero differs
from an unknown quantity.

Assumed/simulated quantities retain their labels and cannot pass the complete
observed selection. All committed fixtures are synthetic, including their
fictional assertions labelled observed. Such a label is not evidence of a real
observation or source verification.

Consumption, occupancy and transfer remain distinct. Occupancy needs an
explicit interval; elapsed time alone is not measured resource use. Transfers
remain visible but block the complete costing selection instead of silently
becoming consumption or disappearing from the selection.

Event-to-object and directed object-to-object edges preserve qualifiers,
including empty qualifiers. Different qualifiers may relate the same pair;
exact repeated edges fail. Use-object links carry context, not allocation
weights or multipliers. One batch shared by two specimens and two assays
remains one use.

The independent synthetic expectation is two collection kits plus one half-hour
instrument use: eight objects, four events, eight object relationships and three
use assertions. Seven batch-use object associations do not multiply its
`1/2 hour`. The amount is an explicit hand-stated observation, not a calculation
from event timestamps.

### Bounds and unsupported transport

Top-level collections are limited to 10,000 records each and 20,000 in aggregate.
Nested event/use object references have a separate aggregate limit of 20,000
and a per-collection limit of 10,000. Tokens are trimmed, control-free UTF-8 of
at most 128 bytes; empty relationship qualifiers are allowed. References must
resolve before normalization.

The original no-dependency X1 contract was qualified in PR #21. The historical
[fixture expectations](fixtures/expected.json) retain their unexecuted-at-the-time
status. The Rust integration tests now exercise their native inputs directly
through the supported profiles. OCEL XML, SQLite, 2.1, compressed input, nested XES
event attributes and general schema conformance remain outside the profiles.

Mailweft issue #4 tracks its separate Rust4PM qualification. The new adapter
uses maintained XML and JSON libraries under the existing validation boundary.
The alternative keeps the vulnerable graph out of Dapane and leaves the upstream
dependency work with its owner.

## Verification commands

Use Rust 1.99.1, the repository's CPython 3.15.1 environment and Ruff.

```sh
cargo fmt --manifest-path adapters/observed_events/Cargo.toml --check
cargo clippy --manifest-path adapters/observed_events/Cargo.toml --locked --offline --all-targets -- -D warnings
cargo test --manifest-path adapters/observed_events/Cargo.toml --locked --offline
python3 -m unittest discover -s adapters/observed_events/tests -p 'test_fixtures.py' -v
ruff check adapters/observed_events/tests/test_fixtures.py
ruff format --check adapters/observed_events/tests/test_fixtures.py
python3 scripts/validate_conductor.py
python3 -m unittest discover -s tests -p 'test_conductor_validation.py' -v
```

Root `cargo test` does not discover this separate package. The coordinator has
added explicit standalone CI using the package manifest and fixture-audit path
(X1-IR-01). Shared CI aggregation remains coordinator-owned. Repeat the checks
for each proposed head with the locked adapter dependencies.

## Primary specification references

- [OCEL 2.0 JSON format](https://www.ocel-standard.org/specification/formats/json/)
- [OCEL 2.0 specification](https://www.ocel-standard.org/2.0/ocel20_specification.pdf)
- [XES Time extension](https://www.tf-pm.org/resources/xes-standard/about-xes/standard-extensions/time)
- [XES Lifecycle extension](https://www.tf-pm.org/resources/xes-standard/about-xes/standard-extensions/lifecycle)

These informed fixture and mapping requirements. Upstream definitions retain
their ownership; these links are not completed conformance evidence.
