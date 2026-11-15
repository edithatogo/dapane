# Contract 0.2: explicit incomplete instrument capacity

Status: bounded synthetic candidate extension. This is computational allocation,
not a validated economic costing method, a capital annualisation method or a
measurement of equipment utilisation. The [0.1 contract](contract-v0.1.md) remains
supported with unchanged full-pool weighting. Package release and schema versions
are independent: the unpublished workspace remains 0.1.0; this wire/method profile
is explicitly 0.2 / `dapane-exact-v0.2.0`.

## Compatibility and scope

A request selects `schema_version: "0.2"` to add `capacity_allocations`. All other
fields retain their 0.1 meaning. Existing `allocations` always normalise weights
to their sum, distributing the entire rounded pool with zero residual, in either
version. Weights `0.1` and `0.2` assign one third and two thirds; they are not
capacity percentages. No automatic upgrade or downgrade is performed.

In a 0.1 JSON request, even `capacity_allocations: []` is rejected. A typed Rust
0.1 request must have an empty capacity vector. Serialization omits empty capacity
vectors, preserving 0.1 canonical input and output identities. The five existing
fixture digests are frozen against the runtime integrated in PR #2. Rust callers
constructing `Request` literals must initialise the new vector; this is an
unpublished pre-1.0 source API addition, not a claim of source compatibility for
struct literals. JSON/CLI/Python 0.1 behaviour is retained.

The first capacity profile supports only `unit: "instrument_hour"` and
`observation_coverage: "incomplete"`. It deliberately does not claim a complete
utilisation/idle-time model, infer equipment availability from samples, convert
other units, reconstruct missing durations, or prorate economic inputs. Sample
counts can be explicit full-pool weights under a separately stated assumption.
Other capacity units, coverage modes and fields are rejected.

## Request

Each `capacity_allocations` entry has these required fields:

| Field | Meaning |
| --- | --- |
| `id` | Unique across both allocation arrays. |
| `source_line_ids` | Nonempty pool of valuation lines, each exclusively assigned to this one pool and never also directly attributed. |
| `unit` | `instrument_hour`; applies to availability and every use record. |
| `observation_coverage` | `incomplete`; known entries do not establish complete instrument use. |
| `available_capacity` | Explicit known positive quantity or unknown with a reason. It must describe the same equipment and period as the pool. |
| `use_records` | Nonempty array of unique known objects and explicit known/unknown quantities. Known use is nonnegative. |
| `source` | Existing versioned source declaration for the capacity assumptions and observations. No source truth is verified by the runtime. |

Quantity states are strict tagged objects:

```json
{"status": "known", "quantity": "10"}
```

```json
{"status": "unknown", "reason": "instrument-duration-not-recorded"}
```

The known form accepts the existing exact decimal string or rational pair. The
unknown form requires a reason identifier and rejects a quantity. Missing states,
`null`, numeric literals, negative values and extra fields are rejected. A known
availability of zero is rejected; an explicitly known use of zero is valid.
Known recorded use must not exceed known available capacity, even if the rest
of the record set is incomplete. When availability is unknown, this comparison
cannot be performed; the observations are retained without estimating it.

Capacity is supplied explicitly. The engine checks the numeric contract, not
whether availability was measured appropriately or whether all economic/source
period assumptions are justified. Those qualification obligations stay with the
source/recipe owner and the scenario bundle.

## Allocation and conserving remainder

Let `P` be the sum of rounded source-line monetary values, `C` the independently
supplied known available instrument-hours, and `q_i` a known use quantity.
The exact candidate assigned share is `P * q_i / C`. An unknown use receives
no computed share (`null`), and the unallocated exact amount is
`P - sum(known exact assigned shares)`. This amount can contain unobserved use;
it is not labelled idle cost, waste, an avoidable cost or a cash saving.

If `C` is unknown, all shares are `null` and the entire pool is unallocated.
Known use quantities remain in the report. There is no fallback to observed
hours, sample throughput, equal weights or a guessed utilisation factor.

Rounding uses largest remainders across **known assigned shares plus one
unallocated bucket**. Start with the floor of each nonnegative minor-unit value;
distribute remaining minor units by descending fractional remainder. Ties go to
the unallocated bucket first, then object IDs in lexical order. Unknown shares
do not receive rounding units. A 0.05 pool split into equal thirds for two
objects and unallocated capacity therefore yields 0.02, 0.01 and 0.02.

`pool_exact` retains the source exact sum. As in 0.1, `exact_share` means the
exact rational share of the **rounded source pool**, not unrounded source cost.
`unallocated_exact` uses the same rounded pool. Both source rounding and
allocation rounding can therefore be inspected without confusing them.

For every capacity pool:

```text
sum(known rounded assigned shares) + unallocated = pool_rounded
```

`totals.allocated` includes assigned shares from both modes.
`totals.unattributed` includes capacity unallocated value plus entirely unassigned
source lines. The pool's unallocated amount is a view of that total, not an
additional cost. Object totals are amounts assigned in this run; a zero object
total with a `null` capacity share does not establish zero true resource cost.

## Report, identity and rejection

Reports add `capacity_allocations` only when used. Each result preserves its ID,
source line IDs, unit, coverage, source and availability state; pool exact/rounded
amounts; known `accounted_quantity`; `unaccounted_quantity` (null when availability
is unknown); recipient quantity states and nullable exact/rounded shares; and
exact/rounded unallocated value. `unaccounted_quantity` is available capacity less
known recorded use, not established idle time. No utilisation field is emitted.

`status: "complete"` still means the supported valuation request completed. It
does not establish complete observations, complete economic scope, source
verification or empirical validity. Those limits remain explicit in capacity
states, coverage, source declarations and the candidate manifest.

Canonicalisation additionally sorts capacity pools by ID, source lines by ID,
and use records by object ID. Decimal spelling and unknown-reason text remain
part of input identity. Digest domains are `dapane:input:0.2\n` and
`dapane:output:0.2\n`; 0.1 domains and method labels remain unchanged.

The existing JSON byte, collection, aggregate, exact numeric and intermediate
precision limits apply. Capacity pools count towards aggregate records. Duplicate
IDs/recipients, unknown references, repeated source lines across either pool
type, direct-plus-pooled attribution, invalid source declarations and unsupported
fields fail with structured errors and no partial financial report.

## Synthetic preparation and consumer boundary

[The genomics cases](../fixtures/genomics-capacity/README.md) independently
stipulate a monthly device charge, a maintenance charge based on its own contract
duration, and a separate one-time implementation cost. Those prepared quotes
exercise the allocator; the Rust core does not derive a depreciation policy,
maintenance amortisation, recurrence schedule, discount rate or useful life.
The strict `dapane-synthetic-genomics-v0.1` fixture manifest documents these
assumptions and is rejected if supplied as a valuation request.

Python transports this contract to Rust without valuation formulas. CareOps
should consume a qualified bundle containing the exact versioned request,
report, scenario/provenance, source revision and qualification scope; it should
display unknown and unallocated values explicitly. No CareOps-owned file or
application calculation is introduced here. Production bundle publication and
real provider integration remain separate work.
