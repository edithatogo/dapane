# Kernel toolchain and dependency qualification

This record covers K1.1 of the [Rust kernel track](../conductor/tracks/rust_kernel_20261108/index.md).
It qualifies the pinned compiler declarations, dependency metadata and scalar
dependency boundary of the **unpublished candidate**. Numerical acceptance,
installed-artifact behaviour and economic/source validity remain separate evidence.

## Reproducible check

Use the pinned Rust toolchain from [rust-toolchain.toml](../rust-toolchain.toml).
Fetch the already locked sources once, then perform the check offline:

```sh
cargo fetch --locked
python3 scripts/qualify_kernel.py
python3 -m unittest discover -s tests/tooling -p 'test_qualify_kernel.py' -v
```

The [checker](../scripts/qualify_kernel.py) uses Python's standard library and
`cargo metadata --locked --offline --no-default-features --format-version 1`.
It does not fetch sources, update the lockfile or execute a provider. Missing
Cargo/cache/compiler prerequisites fail the default check. An explicitly selected
`--static-only` mode reports the compiler, fetched metadata and resolved graph as
**not checked**; CI does not use that mode.

The check enforces these existing boundaries:

- Rust **1.99.1** is the exact qualified pin and declared workspace minimum; each
  member inherits that minimum. The running compiler must report the same release.
- Every registry package's name, version, source and checksum matches
  [Cargo.lock](../Cargo.lock) and the [recorded inventory](dependencies.json).
- Fetched package declarations match the recorded licence expressions and Rust
  minimums. Cargo's equivalent `1.60` / `1.60.0` spellings compare equally; a missing
  declaration remains missing.
- Traversing normal and build dependencies from core and CLI reaches only the
  existing scalar dependency set. Wrapper, table, IO, simulation, GPU and network
  dependencies require an explicit boundary review before they can enter that set.
- Chrono disables default features in the manifest and resolves only `alloc` and
  `std`; clock/timezone features are rejected.
- Default workspace members remain core and CLI. All workspace packages retain
  disabled publication and inherit the workspace lint policy. The core also
  retains its source-level `forbid(unsafe_code)`.

The metadata traversal includes target-conditional normal/build edges, making
the boundary check conservative across the recorded graph. A dependency graph
check does not substitute for compiling and testing a target.

## Observed local results

On **15 November 2026**, the following commands passed in the implementation
checkout, using the unchanged lockfile and inventory. These local observations
precede final publication; the reconstructed files require hosted qualification
on the final implementation commit.

| Check | Observed result |
| --- | --- |
| `python3 scripts/qualify_kernel.py --static-only` | 36 locked registry identities/checksums matched; publication remained disabled |
| `python3 scripts/qualify_kernel.py` | Full offline fetched-metadata and native dependency checks passed |
| `python3 -m unittest discover -s tests/tooling -p 'test_qualify_kernel.py' -v` | 19 tests passed |
| `ruff check scripts/qualify_kernel.py tests/tooling/test_qualify_kernel.py` | Passed with the existing pinned Ruff 0.17.4 |

The observed compiler was `rustc 1.99.1 (58cf8f9c3 2026-10-13)`, host
`x86_64-unknown-linux-gnu`. The normal/build native closure contained **27** registry
packages; the full workspace inventory contained **36**. Chrono resolved
`["alloc", "std"]`. `target-lexicon` remained the only dependency with no declared
Rust minimum. The highest recorded dependency minimum was **1.88**; this does not
establish support for Dapane on that older compiler.

The tooling tests exercise changed checksums and identities, duplicate JSON and
inventory entries, missing licence declarations, altered Unicode obligations,
invented Rust minimums, wrapper dependencies introduced through normal/build edges,
enabled Chrono clock features, missing resolved graphs and enabled publication.
Their synthetic metadata tests qualify the checker; the separate default command
above exercised actual fetched Cargo metadata.

The new [kernel workflow](../.github/workflows/kernel.yml) additionally runs the
minimal core/CLI build and tests offline, the interval reference validator and the
existing bounded CPU benchmark. Its hosted outcome is pending until a run on the
published implementation head is inspected. It preserves the existing native and
installed-wheel workflow and does not establish additional platform support.

## Licence and release boundary

The inventory records declared expressions exactly. In particular,
`unicode-ident` retains `(MIT OR Apache-2.0) AND Unicode-3.0`; the wrapper-only
`target-lexicon` retains `Apache-2.0 WITH LLVM-exception`. The checker compares these
declarations and does not reduce them to a blanket approval or select a licence.
Cargo documents the different meanings of
[`AND`, `OR` and `WITH`](https://doc.rust-lang.org/cargo/reference/manifest.html#the-license-and-license-file-fields).

The project licence remains **unresolved**. Publication remains disabled in every
Cargo package. Existing [release task L1.2](../conductor/tracks/release_consolidation_20261108/plan.md)
owns project/package licensing, registry identities and source redistribution;
L1.3 owns release dependency/advisory checks and provenance. Those tasks are not
completed by this technical qualification. Distribution notices, source rights,
legal compatibility and public release readiness have not been established here.

This is the existing ownership boundary in [the decisions record](../conductor/decisions.md).
Kernel implementation completion must not be represented as a package release or
as resolution of those remaining decisions.
