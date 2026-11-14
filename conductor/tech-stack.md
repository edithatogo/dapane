# Technology stack and dependency policy

## Historical setup

The repository was empty: no code, manifests, lockfiles, licence, release or CI
was present. The initial setup added Markdown/JSON project context, a Python
standard-library documentation validator and a GitHub Actions job for that validator.
The subsequent first runtime is described below; setup validation alone did not
qualify it.

The documentation job uses `python3` on `ubuntu-24.04`; that interpreter is tooling
for repository checks, not the future Python package's support declaration.
`actions/checkout` is pinned to the observed v7 commit
`3d3c42e5aac5ba805825da76410c181273ba90b1`, with read-only permissions and persisted
credentials disabled. The tag was inspected through the
[GitHub API](https://api.github.com/repos/actions/checkout/git/ref/tags/v7) on
8 November 2026. The immutable pin is authoritative for this workflow.

## Implemented first candidate

The Cargo workspace has `dapane-core`, `dapane-cli` and `dapane-python`; default
members are only core and CLI. `rust-toolchain.toml` pins stable Rust **1.99.1**,
the workspace declares that tested minimum and uses edition 2024. `Cargo.lock`
pins the exact graph. This baseline makes no promise about older compilers.

| Direct dependency | Locked version | Responsibility |
| --- | --- | --- |
| serde / serde_json | 1.0.229 / 1.0.154 | Typed strict transport and canonical report construction |
| num-rational / num-bigint / num-traits | 0.4.2 / 0.4.8 / 0.2.19 | Bounded exact rational arithmetic |
| chrono | 0.4.45, default features disabled, `std` only | Strict calendar dates without clock/timezone lookup |
| sha2 | 0.11.1 | Input and report digests |
| PyO3 | 0.30.1, separate wrapper crate | Native Python boundary |

`num-bigint` stays on the line required by the selected `num-rational` release;
using an incompatible newer major would duplicate numeric types. The core has
no simulation, table, Python, web or ontology dependency. Arrow/Parquet is deferred
because the first five reference consumers use exact JSON directly.

Maturin 1.16.0 builds interpreter-specific wheels. Development requirements pin
Maturin, Pytest 9.2.0, jsonschema 4.26.0 and Ruff 0.17.4. The Python package itself
has no runtime Python-package dependencies. Its declared CPython range is
3.12–3.15, with actual interpreter/platform checks recorded in
[runtime verification](../docs/runtime-verification.md); no ABI3 or other-platform
support follows from the range alone.

The [dependency inventory](../docs/dependencies.json) records the 36 locked
registry packages and their declared licences/checksums. This is a source
inventory, not a completed project-licence or source-data rights decision.
Packages use `publish = false` while the project licence is unresolved.

Runtime CI uses the pinned checkout action above and setup-python v6 at
`ece7cb06caefa5fff74198d8649806c4678c61a1`, inspected through its
[tag reference](https://api.github.com/repos/actions/setup-python/git/ref/tags/v6)
on 8 November 2026. It runs native, schema and four-interpreter installed-wheel
checks with read-only repository permissions.

## Broader implementation direction

| Layer | Direction | Boundary |
| --- | --- | --- |
| Core | Rust; Cargo workspace | Domain-neutral records, exact arithmetic, valuation and allocation |
| Core support | Qualified serde/serde_json, error, time, decimal/rational and hashing crates | Use established implementations; select exact versions with fixtures and MSRV evidence |
| Python | PyO3 + maturin; uv for Python tooling | Thin installed extension and optional batch convenience layer |
| Table interfaces | Polars with Arrow/Parquet interchange | Optional IO/adapter crates; no pandas/xarray compatibility implementation in the new core |
| R | extendr, with rextendr packaging if suitable | Direct call to the shared Rust core; no C ABI prerequisite |
| Julia | Versioned C ABI; native artifacts/JLL packaging | No Python or R runtime dependency |
| Local interface | CLI, JSON manifests, optional Arrow/Parquet files | Same engine and versioned run contract |
| Power Platform | Standard SharePoint/file route first | Authorised worker, custom connector/API and WASM/PCF separately optional |
| Semantics | UOGTO and standards_check versioned products | Optional mappings/validation, no mandatory reasoner in the hot path |
| Process models | rust4pm candidate; XES, OCEL, PNML and bounded BPMN adapters | Model execution remains with a qualified engine such as Kairos |

Versions and support are not copied from another repository. The native/Python
choices above are implemented; R/Julia and optional adapters remain outputs of the
[core contracts](tracks/core_contracts_20261108/index.md),
[Python consumers](tracks/python_two_consumers_20261108/index.md) and
[polyglot bindings](tracks/polyglot_bindings_20261108/index.md) tracks.

## Alignment policy

Align schemas, error behaviour, numerical semantics and provider contracts across
the portfolio. Reuse provider packages rather than source-copying their rules.
Keep exact dependency constraints in manifests/locks once they exist, accompanied
by a tested compatibility matrix. A native extension's ABI range does not widen
the enclosing Python distribution's supported interpreter range.

Current stable dependencies are the supported baseline. Preview toolchains and
new releases can be exercised in isolated, non-promoted canary jobs. Do not
silently widen sibling repositories' runtime pins or claim that declared support
has been tested. Record vendored patches, source rights and transitive licences.

## Numeric and performance choices

Preserve decimal source values and rational exposure without silent float
coercion. Choose bounds for precision, magnitude, denominator and serialization;
define overflow/error and rounding behaviour before benchmarking implementations.
Arrow decimal encodings and rational pairs must preserve the agreed contract.

Begin with deterministic CPU execution. Add Rayon, SIMD, GPU, distributed or
incremental paths only for measured workloads and independently checked results.
Do not inherit MCHS's acceleration defaults. Qualify chunk-boundary invariance,
parallel reduction, cancellation and peak memory for each supported path.

## Tooling as implementation begins

Use Cargo formatting/lint/test checks for Rust and Ruff plus appropriate type and
test tooling for Python wrappers. Test installed wheels and native packages, not
only imports from a source checkout. Lock build/release environments and record
source identity, licences, dependency inventory and release provenance using
existing portfolio practices. Do not introduce empty success badges or jobs for
unimplemented packages.

The first release must have a documented project licence. The setup does not
choose one by inference from neighbouring repositories. Dependency and data
licences need separate treatment; PM4Py is an optional AGPL/commercial comparison
adapter, not an assumed permissive runtime dependency.

## Primary implementation references

- [PyO3](https://pyo3.rs/main/) and [maturin](https://www.maturin.rs/).
- [extendr](https://extendr.rs/) and [Julia C interface](https://docs.julialang.org/en/v1/manual/calling-c-and-fortran-code/).
- [Arrow C data interface](https://arrow.apache.org/docs/format/CDataInterface.html).
- [Rust process_mining](https://docs.rs/process_mining/latest/process_mining/) and [OMG BPMN](https://www.omg.org/spec/BPMN/2.0.2/).
- [Power Apps licence designation](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/license-designation) and [PCF overview](https://learn.microsoft.com/en-us/power-apps/developer/component-framework/overview).

These references support the design direction. Recheck version-specific support
when selecting and qualifying an implementation; they are not frozen dependency
pins or evidence that Dapane has implemented those capabilities.
