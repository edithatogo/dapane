# X1 independent observation contracts

**Raw XES/OCEL import remains blocked by dependency qualification.** This package
implements the independent contracts/fixtures fallback authorised for Dapane's
[process track](../../conductor/tracks/process_models_20261108/index.md). It is
not a raw-file decoder, a substitute native OCEL model or a process execution
engine. There is no XES/OCEL file input API.

**Verification notice:** the local candidate passed contract and fixture checks,
but its execution environment became unavailable before commit/push. This
snapshot was reconstructed through the GitHub connector and placed under the
integrator's newly reserved `adapters/observed_events/` namespace. Repeat the
commands below on the exact published head; earlier local successes do not
qualify these recovered bytes. See the
[evidence record](../../conductor/tracks/process_models_20261108/verification.md).

The crate has no external dependencies, monetary arithmetic or default
workspace/CLI/Python integration. Its separate Cargo workspace preserves the
integrator-owned root manifest and lock. Package publication is disabled.

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

Valid set-like collections are sorted after checking. Typed enums exclude
unknown labels. There is no JSON transport for this projection. Duplicate raw
JSON members, unknown native fields, full schema validation, XML entities,
external resolution, byte/decompression budgets and native malformed-input
handling require the actual qualified decoder. The prepared negative inputs
are not claims of implemented raw-parser guards.

## Proposed native mapping and actual status

| Source feature | Required mapping | Status here |
| --- | --- | --- |
| XES identity | Explicit source event/trace IDs; names and positions cannot invent identity | Synthetic input and contract only |
| XES time/lifecycle | Explicit timestamp and declared start/complete pairing; no implied quantity | Synthetic input and contract only |
| XES object graph | Explicit source mapping/sidecar; trace membership cannot reconstruct the OCEL graph | Sidecar expectation only |
| OCEL 2.0 JSON | Retain native IDs, types, typed attributes/history and qualified E2O/O2O | Raw fixtures retained; native import blocked |
| Unprojected native content | Retain the source/native model; reject unsupported meaningful data rather than silently discard it | Native fidelity and round-trip blocked |
| OCEL XML/SQLite/2.1, PNML/BPMN | Separate qualification | Outside X1 |
| Kairos | Qualified provider contract and execution evidence | No integration/execution claim |

[expected.json](fixtures/expected.json) pins all 13 raw fixtures by SHA-256 and
marks their native decoder cases unexecuted. The Rust cases exercise a typed
contract. The Python auditor reads only the fixed synthetic XML/JSON fixtures
and checks content against explicit expectations. It does not connect a raw
decoder to the Rust contract or implement a runtime alternative to Rust4PM.
Full XES XSD/OCEL schema conformance and native round-trips are unexecuted.

## Dependency gate and integration

Read-only inspection pinned Mailweft main at
[`14b3de557a7654708f6066f70f4d8bc1e3d1e564`](https://github.com/edithatogo/mailweft/commit/14b3de557a7654708f6066f70f4d8bc1e3d1e564).
Its lock has `process_mining 0.6.2` and `quick-xml 0.37.5`. The Rust4PM
dependency is optional in that main's core manifest; optionality does not
qualify XES/OCEL imports. [Issue #4](https://github.com/edithatogo/mailweft/issues/4)
remains open. The old draft [PR #3](https://github.com/edithatogo/mailweft/pull/3)
head, `520d545951e9c722fff857674081608427ca2ec5`, is recorded separately.

This lane adds no dependency patch, replacement XML/OCEL runtime, advisory
suppression or upstream edit. `RAW_IMPORT_STATUS` remains
`blocked_dependency_qualification`; no flag enables a raw decoder.

The [integration requests](../../conductor/tracks/process_models_20261108/integration-requests.md)
cover qualified dependency adoption, explicit CI coverage, native mapping and
shared schema/API decisions. The existing core's per-generated-segment half-even
method is unchanged. This crate has no quotations and performs no money or
segment arithmetic.

## Verification commands

With Rust 1.99.1, Python 3.12+ and the repository's Ruff version available:

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

Root `cargo test` and existing CI do not discover this separate package.
X1-IR-01 requests adoption rather than claiming that existing green checks ran
the new tests. Repeat all commands on the recovered exact head before promotion.

## Primary specification references

- [OCEL 2.0 JSON format](https://www.ocel-standard.org/specification/formats/json/)
- [OCEL 2.0 specification](https://www.ocel-standard.org/2.0/ocel20_specification.pdf)
- [XES Time extension](https://www.tf-pm.org/resources/xes-standard/about-xes/standard-extensions/time)
- [XES Lifecycle extension](https://www.tf-pm.org/resources/xes-standard/about-xes/standard-extensions/lifecycle)

These informed fixture and mapping requirements. Upstream definitions retain
their ownership; these links are not completed conformance evidence.
