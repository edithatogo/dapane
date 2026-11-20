# Process track review

## Scope and review fixes

The selected raw provider is roxmltree 0.21.2 with no DTD or external resolver.
The JSON provider is serde_json 1.0.154 with typed object-only deserialization
and explicit attribute checks. The review found that Serde's struct visitor
could accept positional arrays. The parser now requires JSON records to be
objects. Timestamp parsing rejects unknown offsets, leap seconds and precision
beyond the native nanosecond DTO. XES interval anchors must match lifecycle
roles, trace and activity. Original bytes remain available for audit.

The separate [Kairos provider PR](https://github.com/edithatogo/kairos/pull/400)
merged at `cdda891`. Its tree is identical to the checked PR head. It adds
scheduler-backed occupancy and binds its physical unit. Independent review
required explicit units and observation-window bounds in slice identity. The
upstream fixes preserve strict FIFO, checked atomic quantity acquisition, causal
events and sealed observation windows. The adapter rejects unclosed occupancy
and retains causal anchors and model/run identity. It computes exact
resource-unit-time quantities. Dapane's existing core applies the prices.

## Verification

- The observed adapter ran 42 Rust integration tests, including the existing
  raw XES and OCEL positive, reordered, duplicate, missing-time and censoring
  cases. The tested batch retains eight objects, eight relationships and three
  uses. The complete original raw bytes and their independent fixture digests
  are retained. The 12 existing Python fixture audits also passed.
- The scoped Kairos candidate passed its DES suite, warnings-denied Clippy and
  six Time Warp regression cases. Staged usage is forward-only. The Time Warp
  tests verify the unchanged upstream path.
- The downstream locked Kairos adapter ran two tests. One native execution with
  three occupied ticks and two ticks per hour gives 1.5 instrument-hours.
  Changing the quoted rate from 12 to 20 produces 18.00 and 30.00 NZD from the
  same usage identity. The second test rejects censored occupancy and mismatched
  time units.
- Cargo advisory, bans, licence and source checks passed for both separate crates.
  The optional Kairos policy allows its exact revision-pinned source. The default
  core lock and dependency policy are unchanged.
- The [X2 verification](x2-verification.md) retains the executed PNML/BPMN tests and
  their named profiles. Root tests and packages keep the process adapters optional.

The selected profiles cover uncompressed XES 2.0 and OCEL 2.0 JSON, the existing
bounded PNML and BPMN paths, and committed staged lease occupancy. OCEL XML and
SQLite, full-format interchange, engine movement and optimistic usage export have
their own qualification scope.
