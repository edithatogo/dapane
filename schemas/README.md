# Dapane contract schemas

Versioned JSON Schema 2020-12 documents are in [`0.1/`](0.1/):

- `request.schema.json`: the public valuation request.
- `report.schema.json`: a complete successful report.
- `error.schema.json`: the structured error shape, with no partial totals.
- `common.schema.json`: shared exact numeric, provenance, context and policy definitions.

Every object rejects unknown fields. Exact input quantities and prices are
decimal strings or numerator/denominator string pairs. JSON numeric literals
are not accepted for these values. Enumerations, required fields, date formats,
per-collection limits, numeric text precision and several local positivity and
uniqueness constraints are checked structurally.

Schema IDs identify files in this repository. The validation script registers
all four schemas locally using `referencing.Registry`; it performs no network
retrieval. Date validation requires the included `FormatChecker` because JSON
Schema tools may otherwise treat `format` as an annotation.

## Validate

With `jsonschema==4.26.0` installed, run from the repository root:

```sh
python scripts/validate_contract.py
```

This validates the schema documents, all five synthetic request fixtures,
authored report/error shape examples and negative structural/parser examples.
It does not claim that the runtime has run. To exercise the compiled Rust CLI:

```sh
python scripts/validate_contract.py --cli target/release/dapane
```

The latter also checks the hand-derived reference values in
[`fixtures/expected.json`](../fixtures/expected.json), allocations, preserved
source/context lineage, conservation, canonical rational outputs and independently
computed input/output digests. Reordering equivalent collections must preserve
the report. Changing a supplied decimal spelling must change its identity while
preserving its value. Runtime rejection cases deliberately include structurally
valid requests, such as expired quotes and duplicate economic components.

## What remains a Rust check

JSON Schema does not establish valid economic calculations or source truth.
The kernel separately checks referential integrity, unique record identities,
activity/process consistency, matching measure kind/target/unit, currency,
valuation basis and price year, quote applicability, knowledge cutoff, overlapping
included components, repeated allocation sources, positive total allocation
weight and conservation. It also rejects duplicate JSON object keys before
deserializing; validating an already-parsed dictionary cannot recover duplicates.

The runtime enforces the authoritative 4 MiB request limit, 20,000 aggregate
top-level records, UTF-8 byte lengths and 4,096-bit intermediate arithmetic bound.
Schema `maxLength` counts Unicode characters, so it cannot alone enforce the
documented byte limit. Output rational reduction, exact rounding scale,
canonical serialization and correct digest content are semantic properties.
The executable validation script checks the relevant output properties against
the small fixtures; the schema alone does not.

Source evidence/access/validation labels are preserved caller declarations.
Neither structural validation nor a successful arithmetic result verifies an
external source or confers empirical validation.
