# Independent static synthetic benchmarks

This is the bounded F1/F2.1–2 implementation for
[the existing benchmark track](../../conductor/tracks/frontier_benchmarks_20261108/index.md).

**Initial published state: draft, exact-head execution blocked.** An earlier local
counterpart passed 21 tests, including the 24 mutation cases and complete-report
comparisons for 12 update scenarios. The execution environment then became
unavailable. The published source was reconstructed from the authored code and
moved to the integrator's reserved `benchmarks/static/` namespace. Those earlier
tests do **not** qualify this exact published revision. The build-receipt, timing
runner, offline bundle verifier and two additional gate tests are unexecuted.

See [protocol](PROTOCOL.md), [comparators](COMPARATORS.md),
[protocol history and corrections](HISTORY.md), and
[retained local observations](evidence/local-observations.json).

## What this implements

- Twenty-four invented point/interval cases: seven controls, twelve contract
  defects and five defects requiring source truth that the evaluator lacks.
- A separate Fraction-based arithmetic oracle plus authored literal expectations.
- Experimental caching of **complete independent requests**. Every changed request
  still goes through the unchanged Rust CLI. Complete reports, including digests,
  must match full recomputation byte for byte.
- Transactional cache updates, executable and full-input identity, failed-request
  rejection, eviction, immutable output bytes and conservative invalidation.
- A fixed paired-measurement protocol with fresh seeding per pair and honest null,
  equal or slower observations. No performance result is currently available.
- A result-bundle writer/verifier that retains raw inputs/reports, source/binary
  identities, raw timing pairs, measured boundaries and explicit unmeasured fields.

This is test tooling, not a Dapane production API. It adds no runtime dependency
and changes no evaluator, schema, installed wrapper, manifest, lockfile or CI.

## Reproduce after restoring execution

From a clean checkout of the exact PR head, with Rust 1.99.1 and Python 3.12+
available, use a writable directory outside the checkout for evidence. The
existing locked Cargo dependency cache must be populated; the build stays offline.

```sh
python3 -m benchmarks.static.build \
  --target-dir /tmp/dapane-static-target \
  --receipt /tmp/dapane-static-build.json

DAPANE_BENCH_CLI=/tmp/dapane-static-target/release/dapane \
  python3 -m unittest discover -s benchmarks/static/tests -v

ruff check benchmarks/static
ruff format --check benchmarks/static

python3 -m benchmarks.static.run \
  --cli /tmp/dapane-static-target/release/dapane \
  --build-receipt /tmp/dapane-static-build.json \
  --output /tmp/dapane-static-result

python3 -m benchmarks.static.verify /tmp/dapane-static-result
```

Use unused receipt/output paths: existing evidence is never overwritten.
The native tests require `DAPANE_BENCH_CLI`; an unavailable executable is a
failure, not a skipped acceptance suite. The runner requires a clean source tree,
checks the pinned runtime files against the protocol baseline and binds the
receipt to the exact executable. Changed runtime sources need a reviewed protocol
revision rather than relabelling older evidence.

A normal run writes `results.json`, `inputs.json`, `reports.json` and
`checksums.json`. A failed experiment retains its observations with a failed
status and no timing summary for the failing comparison. A checksum verifies
identity, not authorship or the accuracy of a source assertion.

The [handoff](../../conductor/tracks/frontier_benchmarks_20261108/HANDOFF.md)
requests the integrator-owned registry/CI changes. The existing workflows do not
automatically execute this namespace. No gate is waived and no frontier,
empirical, clinical, cross-platform or release-readiness claim is made.
