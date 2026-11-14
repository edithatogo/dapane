# First runtime verification

Review date: **8 November 2026**. Scope: the unpublished Dapane `0.1.0` candidate,
JSON contract `0.1`, method `dapane-exact-v0.1.0`. All economic values and domain
examples are synthetic. This record qualifies the bounded implementation and
installed interfaces; it does not qualify existing provider rules, real screening
programmes, external source validity or every Conductor requirement.

## Environment and dependency identity

- Rust **1.99.1**, edition 2024, `x86_64-unknown-linux-gnu`.
- Local host: Linux x86_64, glibc 2.41. The candidate is not yet qualified on other hosts.
- Exact registry dependency graph: [Cargo.lock](../Cargo.lock).
- Declared dependency licences/checksums: [dependency inventory](dependencies.json).
- Native Python build: PyO3 **0.30.1**, Maturin **1.16.0**.
- Verification tooling: Pytest **9.2.0**, jsonschema **4.26.0**, Ruff **0.17.4**.

The core/CLI build without Python, Kairos, a table engine, cloud account or ontology
reasoner. Native default workspace members are core and CLI. Python is a separate
crate and has no runtime Python-package dependencies.

## Native and public-contract checks

| Executed check | Observed result |
| --- | --- |
| `cargo fmt --all --check` | Passed |
| `cargo test --locked` | **25 core tests and 5 CLI tests passed** |
| `cargo clippy --workspace --all-targets --locked -- -D warnings` | Passed |
| `cargo build --locked --release -p dapane-cli` | Release CLI built |
| `cargo install --locked --path crates/dapane-cli --root <clean-prefix>` | Installed CLI executed the newborn file from outside the checkout: 150.00 total, 60.00/90.00 infant views |
| `python scripts/validate_contract.py --cli target/release/dapane` | Four schemas, five fixtures, 37 structural/parser negatives, 14 runtime rejection cases and three identity/context cases |

The contract check verifies actual CLI reports against independently authored
exact/rounded values, source and context lineage, source/object/pool conservation,
canonical rational output and independently computed input/output digests.
Structurally valid but semantically invalid requests must fail in Rust and emit
no partial financial report. JSON Schema alone cannot establish these properties.

The [installed CLI record](cli-verification.json) captures the executable hash
and observed result identity. Final Conductor validation passed for 13 tracks,
12 requirements and 132 tasks; a separate runtime-document link scan found no
missing local targets. Ruff checks and formatting passed for the Python package,
installed-wheel tests and new verification scripts.

Core cases include half-even ties, line-before-total rounding, explicit zero versus
missing data, half-open quote intervals, knowledge cutoffs, wrong units/kinds/bases,
loaded-component overlap, duplicate identities and allocation sources, unknown
context references, zero weights and unsupported methods. An independent
quotient/remainder oracle checks equal allocation across **102 pool amounts**.
Bounds tests exercise 10,000-per-collection and 20,000-total record limits, the
4 MiB typed/input boundary, UTF-8 byte limits and actual intermediate rational
growth beyond 4,096 bits using distinct prime denominators.

## Independent reference cases

| Synthetic input | Independently expected result |
| --- | --- |
| Workforce: 20 minutes at 90/hour | Exact `1/3` hour, value **30.00** |
| Genomics: one batch 100 plus collections 10 + 10 | **120.00**, specimen views **60.00 / 60.00** |
| Activity-only funding: 2.50 weighted units at 17/unit | **42.50**, with no physical resource rows |
| Newborn: collections 10 + 10, batch 100, one confirmation 30 | **150.00**, infant views **60.00 / 90.00** |
| Shared 0.05 pool, equal weights for a/b/c | **0.02 / 0.02 / 0.01**, zero residual |

The [fixture notes](../fixtures/README.md) explain the calculations and source
limits; [expected.json](../fixtures/expected.json) contains authored expectations.
No provider output was treated as an independent oracle. Core-specific tests also
use other explicitly synthetic rates to exercise fractional and boundary behavior.

## Installed Python matrix

The corrected core was rebuilt and installed for all four interpreters.
Each interpreter-specific wheel is installed into its own clean virtual environment.
Tests execute from `/tmp` using `--import-mode=importlib`, resolve the native module
inside the installed distribution and do not import the source package.

| CPython | Final installed-wheel result |
| --- | --- |
| 3.12.14 | 54 tests passed |
| 3.13.15 | 54 tests passed |
| 3.14.9 | 54 tests passed |
| 3.15.1 | 54 tests passed |

The [artifact record](wheel-verification.json) contains wheel filenames, sizes and SHA256 digests.
All four artifacts were installed with no runtime dependency downloads.

Tests cover the five consumers, exact `Decimal`/`Fraction` transport, binary-float
and non-finite rejection, duplicate JSON keys, errors, malformed/cyclic host inputs,
allocation conservation, context, deterministic concurrent calls and the review
regression below. All valuation enters the shared Rust implementation.

Wheel tags are build metadata. Testing on this host does not establish every
manylinux distribution, stable ABI, PyPy, free-threaded Python, other operating
systems or ARM support. The existing workforce/genomics packages were not installed
as migrated consumers; their provider pins and namespace/source issues stay open.

## Independent review and resolved defects

Review covered the complete evaluator, validation, numeric and canonical-JSON
modules, CLI and the documented contract. Two concrete defects were reproduced
and corrected before final candidate publication:

1. **Equivalent context was rejected.** Two disjoint salary/oncost lines shared
   one use and event, but one inherited process/activity while the other stated
   the identical IDs. Comparing resolved context now accepts them and returns
   **33.00** for `1/3 × (90 + 9)`. Conflicting context remains rejected. The
   regression failed against the prior native implementation and installed wheel.
2. **A non-UTF-8 Unix filename could panic the CLI.** OS-native argument handling
   now preserves such file paths and returns structured invalid-command errors.
   The CLI regression verifies a valid request at a non-UTF-8 filename.

No additional concrete accounting, conservation, digest or source-certification
defects were identified in this bounded review. This is not a claim of exhaustive
verification or empirical validation.

## Bounded performance observation

The [raw measurement](benchmarks/2026-11-08-linux-x86_64.json) records three runs
per workload, including CLI startup and JSON input/output. Each row is exact
`(1/3) × 90 = 30`; the allocation workload pools all rows and gives one equal
share to each of the same number of recipients. Every run checks totals, object
shares, zero residual and repeatable output identity.

| Usage rows | Valuation median wall time | Valuation plus allocation median |
| ---: | ---: | ---: |
| 10 | 1.67 ms | 1.81 ms |
| 1,000 | 31.18 ms | 41.31 ms |
| 5,000 | 225.54 ms | 309.88 ms |

Peak child RSS across the entire measurement was **84,812 KiB**; it is not a
per-workload memory figure. This is a single-host synthetic baseline, with no
concurrent execution, external provider, distributed/GPU or comparative speedup
claim. The 5,000-recipient workload emits about 4.6 MB of JSON. Larger-scale
streaming/table IO requires its own exactness, resource and performance evidence.

Reproduce using `python scripts/benchmark_cli.py --cli target/release/dapane`.

## Remaining qualification

The runtime supports already quantified, nonnegative point-date usage. It does
not execute event logs, Petri nets, BPMN or Kairos, derive occupancy intervals,
apply retractions, convert units implicitly, calculate FX/escalation/discounting/
capital/tax, or implement stochastic decision models. Component inclusion labels
detect repeated charges; a loaded aggregate quote is not automatically decomposed.

Source evidence/access/validation are preserved caller declarations. An output
digest proves identity of encoded input/result, not correctness of a source claim.
Real programme and provider evidence, reporting/ontology adapters, deployment,
licence selection, registry publication and archive decisions remain open in
[Conductor](../conductor/tracks.md). No full runtime track is marked complete solely
on these synthetic and installed-artifact checks.
