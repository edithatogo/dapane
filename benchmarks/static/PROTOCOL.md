# Static synthetic protocol v1.2

Dated 2026-11-15. This is the publication revision of the F1/F2.1–2 protocol.
The original protocol and literal expectations were locally committed before
native comparison at `b9485ef60799ed0a809d9c416c8b984065c7590e`. After two diagnostic
corrections, the local counterpart passed its acceptance suite at
`5cc42f41d1713afab9348d781a38717d515b6b75`. Those local commits were not pushed
before the execution environment became unavailable. [History](HISTORY.md)
separates that observation from this reconstructed, unexecuted publication.

The active runtime pin is `9a03eea4656115da38dec4d8a802406c482511b5`. Among
the tracked runtime files, this revision updates only the core package's
registry and file inclusion metadata relative to the historical pin
`2311d6028f30ff7af01f064a76234cb0db7d1236`. The frozen mutation inventory,
workloads and acceptance conditions apply to this revision.

## Questions and comparators

1. Which deliberately introduced costing defects does the unchanged CLI reject,
   and which remain accepted because source truth is absent from its contract?
2. Does reusing complete reports for byte-identical independent requests give
   exactly the same answers as full recomputation?
3. How do call counts and observed latency change when zero, one or all requests
   change? No positive speed effect is required for acceptance.

Full recomputation and request caching use the same executable, commands, complete
inputs and policies. A separate Python Fraction oracle checks submitted-input
arithmetic. Literal, hand-derived expectations check the oracle. The
[comparator review](COMPARATORS.md) does not claim that this is a survey of the
best available costing software, nor that an authored reference is a human study.

## Data and literals

All inputs are invented, public, unvalidated resource-use examples. No provider,
patient record, programme data, external workbook or other upstream repository
is required. One deliberately false verification label tests that the engine
preserves caller assertions without authenticating them.

The point baseline is one third of an hour at 90/hour (30.00), two items at 3 per
two items (3.00), and one shared batch at 5.05: total **38.05**. The batch splits
2.53/2.52 between recipients a/b; with direct amounts 30.00/3.00, their totals are
**32.53/5.52**. These are accounting examples, not observed prices or screening
recipes. Omitting material yields 35.05; an aliased extra batch yields 43.10;
changing the material denominator from two to one yields 41.05. These submitted
inputs can be evaluated correctly while contradicting the authored source truth.

Point lines worth 0.005 and 0.015 round to 0.00 and 0.02. A two-day uniform interval
split into two 0.005 segments has exact total 0.01 and rounded total **0.00**.
Two 0.015 segments round to **0.04**, although their exact total is 0.03.
The accepted per-generated-segment half-even method is fixed.

The [inventory](fixtures/cases.json) fixes 24 cases and their expected outcomes:
seven valid controls, twelve contract violations, five source-truth defects.
Rejections and numerical correctness of submitted inputs are separate outcomes.
Knowledge of the authored inventory is never attributed to the native engine.

## Cache unit and failure rules

A portfolio maps independent requests to complete reports; it has no aggregate
financial total or cross-request pool. Each request includes all of its allocations,
quotes, policy and provenance. A quotation shared across scenarios must be
materialised in each affected request, and changing it invalidates each snapshot.

Cache identity includes executable SHA256, command and the full UTF-8 request
digest. Bytes are compared before reuse. Unused quotes, source declarations,
policy metadata and array order all participate. Harmless reordering causes a
conservative miss; this is measured, not hidden.

Entries store immutable complete output bytes. Updates are committed only after
every request succeeds, and absent requests are evicted. A failing portfolio
returns no partial financial result and retains the old cache. Failed requests
are not cached. The executable is checked at portfolio boundaries; concurrent
binary replacement is unsupported. There is no intra-request incremental engine.

## Measures

| Outcome | Definition |
| --- | --- |
| Numerical correctness | Exact rational and rounded line/pool/object/total agreement with the independent oracle and literal controls; zero tolerance |
| Detection | Native rejections / labelled defects, separately for contract and source-truth strata |
| False positives | Native rejections / valid controls |
| Explanation | Expected error code, nonempty message/path, empty stdout on rejection |
| Reporting coverage | Applicable identity, policy, source, context and numerical checks; not an external reporting-standard score |
| Incremental correctness | Complete report bytes, including input/output digests, equal to full recomputation |
| Work | Native calls, hits/misses, input/output bytes and retained cache payload bytes |
| Timing | Five raw paired samples, medians and full/incremental median ratio; alternating order |
| Memory | Linux parent/child RSS high-water values for the entire run; per-method peak remains null; cache payload bytes exclude interpreter overhead |
| Human effort, diagnosis/repair time, usability | Null: no analyst study |
| External accuracy, transportability, privacy utility/risk | Null: no such experiment |

Timing uses 8 and 32 requests alternating point and interval controls, each with a
distinct run ID. Scenarios are cold cache, unchanged, one rate, all rates, one
policy, one source declaration, one allocation, one unused quote, one record-order
change, one interval rate, insertion and removal.

One untimed pair precedes five measured pairs. Every warm pair starts from a fresh
seeded baseline, so later repetitions cannot become spurious hits. Seed cost is
recorded separately. Encoding, hashing, CLI startup/I/O and result-map construction
are inside latency; fixture generation and independent validation are outside.
Execution is sequential on CPU. Cold cache does not imply cold operating-system
caches. The host is uncontrolled; no statistical/general speed claim is permitted.

Exactness and expected call counts gate timing summaries. Failed checks remain
in a failed bundle. Null, equal and slower results are retained without a speed
threshold. Memory high-water values span the complete run, including metadata
probes, and are not comparative per-workload measurements.

## Reproducibility and boundaries

The proposed runner records exact Git source, dirty state, runtime source-file
digests, binary/build receipt, lockfile, protocol/harness/fixture digests, Python
and standard-library identities, OS/CPU information, raw inputs, native reports
and errors, all timing pairs and explicit null fields. Companion files have
checksums. The build receipt is locally executed evidence, not an attestation.

At this initial handoff the full bundle path and paired timings are **unexecuted**.
Earlier local observations are preserved separately and are not relabelled.
Future protocol/input changes require a new version, retaining adverse results.

Production evaluation, schemas, wrappers, root manifests, shared fixtures and CI
remain with the integrator. F2.3–4, F2.5's complete programme evidence, external
validation and publication remain open. No frontier, empirical, clinical,
human-adoption or release-readiness claim follows from these synthetic cases.
