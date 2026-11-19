# Kernel dependency qualification

The native kernel retains the tested Rust **1.99.1** baseline, edition 2024 and
locked dependency versions. This is the supported minimum demonstrated by the
existing native CI, not a claim that older compilers fail. The
[qualification script](../scripts/qualify_kernel.py) checks this declared boundary
against source records and, in full mode, the active compiler and fetched Cargo
metadata. It adds no dependencies and does not update the lockfile.

## Reproducible checks

```sh
python3 scripts/qualify_kernel.py --inventory-only
python3 -m unittest discover -s tests/tooling -p test_qualify_kernel.py -v
python3 scripts/qualify_kernel.py
```

The first command needs Python 3.11 or later and the checkout. It checks matching
toolchain/MSRV declarations, the disabled registry-publication gate in each
workspace package, the two native default members, and exact package identities,
checksums, licence declarations and declared Rust minima in
[Cargo.lock](../Cargo.lock) and the [inventory](dependencies.json). A passing
static check does not establish that package sources were fetched or compiled.

The tooling tests exercise inventory tampering, manifest drift, a wrapper build
dependency entering the native closure, clock features, publication settings and
default-member changes. Their metadata is explicitly synthetic: they test the
guard's rejection paths and do not qualify actual fetched packages.

Full mode additionally verifies `rustc --version --verbose`, `cargo --version`
and `cargo metadata --locked --format-version 1`. The active compiler must match
the exact pin; Cargo must belong to the same stable major/minor release series,
with its actual patch version recorded. It compares fetched manifest licence/MSRV
declarations with the inventory, traverses the core/CLI normal and build
dependencies, and requires every resolved package to belong to the reviewed
native package set. This positive list rejects new wrappers, table engines,
network clients, simulators and accelerators even if their names are unfamiliar.
The traversal includes target-dependent dependencies conservatively and excludes
development-only edges. The `time` dependency must resolve with the
`parsing` feature alone. Python remains a separate workspace member.

The script emits a JSON observation with its scope, compiler/host identity when
checked, package counts and the resolved native closure. It does not compile code.
The existing formatting, Clippy, native tests, clean CLI installation and installed
wheel matrix remain separate necessary evidence. Run their existing commands on
the same revision before treating the full kernel increment as verified.

## Licence boundary

The inventory contains explicit MIT/Apache-2.0 alternatives, an Unlicense/MIT
alternative, MIT, the combined Unicode-3.0 declaration, and the Apache-2.0
declaration with LLVM exception. The script accepts only these exact reviewed
expressions and rejects missing or changed declarations; it does not parse or
silently approve new SPDX expressions. Their source notices, applicable attribution
and redistribution obligations must be retained when preparing a distribution.
The Unicode licence and LLVM exception must not be dropped by reducing a compound
expression to a generic permissive label. These are dependency declarations, not
a licence chosen for Dapane.

`target-lexicon` has no declared Rust minimum in the current inventory. The script
preserves that unknown explicitly; the actual pinned-toolchain build provides
compatibility evidence for the exercised target. It does not infer an older MSRV.

The owner selected Apache-2.0 for project material in ADR-014. Source-data rights,
distribution notices and registry publication remain with the
[release track](../conductor/tracks/release_consolidation_20261108/index.md).
Every workspace package retains `publish = false`; current qualification reports
derive `project_licence` from the workspace manifest and retain
`release_qualified: false`. Historical archived observations retain the licence
state at their checked source. Kernel dependency qualification does not establish
registry rights, economic, clinical or source-data validity.
