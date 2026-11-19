# Optional R and C ABI candidates

This namespace belongs to `polyglot_bindings_20261108`. R calls the existing
Rust kernel directly. The proposed C ABI calls the same functions. Numerical
validation, exact arithmetic, method identities, digests and per-generated-segment
half-even rounding stay in `dapane-core`. No Python/provider runtime is required.
All cases are synthetic.

**Current status:** the integrator replayed installed Linux R and native C
acceptance and added standalone CI. The owner corrected ABI lint precedence and
Python formatting without changing runtime source or fixture assertions. See the
[current source-bound evidence](../../conductor/tracks/polyglot_bindings_20261108/owner-quality-20261115.md).
Total ABI acceptance, optional legal/security/release requirements and other hosts
remain open. A local Julia caller is in `julia/`. It is not an installed package
or a JLL artifact.

## R direct Rust boundary

`r/` contains an extendr 0.9.0 package:

| Entry point | Existing kernel operation |
| --- | --- |
| `evaluate_json()` | Point/capacity request profiles 0.1/0.2 |
| `evaluate_intervals_json()` | Interval envelope 0.1 |

Inputs and outputs are UTF-8 JSON character strings. Decimal strings and rational
pairs remain exact: R neither decodes/re-encodes the request nor calculates costs.
Missing values, numeric vectors, lists, factors, bytes-encoded strings and vectors
of strings fail. Kernel errors become `dapane_error` conditions retaining
`code`, `message`, `path` and exact `diagnostic_json`; there is no partial result.

R API access is synchronous on the interpreter's main thread. No R handle or
borrowed string survives a call. Parallel callers use separate R processes.
The installed test stresses garbage collection and two independent interpreters;
it does not attempt forbidden calls to R from foreign worker threads.

The registration pattern is adapted from rextendr at
`d7383605ebdc766ddc46e9b73ff2b34bf6c19565`, with the MIT notice retained in
`r/inst/REXTENDR-LICENSE.txt`. rextendr 0.5.0 is the documented development
convention, not a runtime dependency; its scaffolding command was not executed.
The small Makevars is limited to the intended Linux linker set.

## Self-contained R source package

With R 4.5.0, Rust 1.99.1, a C compiler and Python 3.11+ available, use a new
staging directory outside the checkout:

```sh
cargo fetch --locked --manifest-path bindings/polyglot/r/src/rust/Cargo.toml
python3 bindings/polyglot/stage_r.py --output /absolute/new-stage/dapaneR
cd /absolute/artifacts
R CMD build --no-build-vignettes --no-manual /absolute/new-stage/dapaneR
R CMD INSTALL --preclean --library=/absolute/isolated-r-library dapaneR_0.1.0.tar.gz
```

Staging copies the existing core source bytes, resolves workspace manifest
inheritance only in that generated copy, compares source hashes and vendors the
locked Cargo graph. Installation then builds offline. The installed package
retains source/lock provenance; the original core and root workspace are untouched.
Local source packages are acceptance inputs, not published registry artifacts.
Full notices and release rights remain the integrator's qualification work.

## C ABI proposal

`abi/include/dapane.h` is the complete v1 contract. The boundary exposes five
functions: ABI version, evaluation, result length, result copy and result free.
ABI major 1 is independent of schema, engine and method versions.

Evaluation borrows input synchronously and returns a nonzero opaque handle on
success or a structured core error. The caller queries the result length, copies
complete UTF-8 JSON into its own buffer and frees the handle through Rust.
No Rust pointer, object layout or allocator-owned buffer is returned to the host.
Short copies leave the output untouched and report the required length. Result
handles are immutable, bounded to 64 handles/64 MiB, and never reused during one
loaded library's lifetime. Unknown/stale/double-free handles return an error.

Calls use a mutex for result ownership; computation still occurs in the pure
kernel. Copies and frees serialize so a concurrent free cannot invalidate a copy.
A handle belongs to one loaded library instance; numeric equality across separate
instances does not establish identity. Callers must keep that library loaded.
A caller-owned nonzero output handle is rejected without overwriting it.

Every fallible exported operation catches Rust unwinding. Builds using
`panic=abort` fail at compile time. Valid pointer ranges, alignment, disjoint
outputs and host synchronization remain C caller obligations. A null/alignment
check cannot prove arbitrary pointer validity. OOM, signals and process aborts
are not converted into diagnostics.

The C consumer tests all 24 prepared reports/errors, null/UTF-8/size/version
failures, too-small sentinel buffers, stale/double-free handles, request lifetime,
handle saturation/recovery and 400 calls across four native threads. The integrator
executed those cases with the five Rust unit tests; the owner reran ordinary
native acceptance on the correction source. Exact host/library identities and
the local sanitizer limitation are recorded in the linked evidence. These bounded
results do not establish total ABI or other-host acceptance.

## One reproduction command

The new helper is an unexecuted handoff command; it refuses a dirty source tree
or an output directory inside the checkout and stops at any failed gate:

```sh
bash bindings/polyglot/qualify.sh /absolute/new-qualification
```

It records the Git SHA and tool versions, checks both standalone Rust workspaces,
stages/installs R into a fresh library, runs host cases, builds the C library,
runs the C consumer with AddressSanitizer/UndefinedBehaviorSanitizer on the C
consumer, and writes artifact hashes. The Rust library itself is not sanitizer
instrumented by that command. No queued/missing check becomes a pass.

Independent numerical projections come from the existing hand-calculated
fixtures and explicit large-integer/rational/interval examples. Complete JSON
reports captured from the CLI are regression parity oracles. The five capacity
cases currently use complete CLI parity; this does not create independent
capacity reference calculations.

## Julia caller

`julia/` calls the C ABI through `Libdl`. It copies the request and the result
into Julia memory, preserves the request across the foreign call, and frees the
Rust handle before returning. Amounts are not decoded or recalculated. The
library path must be the target-native `dapane-abi` filename. On this machine
that is `libdapane_abi.dylib`.

Build the release library, then run the package tests with a CLI built from the
same checkout:

```sh
cargo build --offline --locked --release -p dapane-cli
cargo build --offline --locked --release --manifest-path bindings/polyglot/abi/Cargo.toml
julia --project=bindings/polyglot/julia -e 'using Pkg; Pkg.test()'
```

The 20 November run passed 20 tests on Julia 1.13.4: workforce and interval
bytes matched the CLI, a foreign-platform library name was rejected, and the
copied result survived input overwrite plus `GC.gc()`. This does not install a
packaged library or select BinaryBuilder/JLL.

## Shared changes and rollback

This lane changes only `bindings/polyglot/` and its own track. Each optional
Rust crate has a standalone workspace/lockfile. No root Cargo/CI, existing crate,
schema, provider manifest or root document changes are needed to inspect the
candidate. The integrator has accepted the path, synchronized the blocked registry
and added installed-host/native CI. Optional dependency/advisory, notice and
staged legal-payload accounting remain integrator requirements.

Preserve ABI major 1 only after qualification. An incompatible ownership or wire
change needs a new major/symbol prefix; numerical changes need their own core
method/contract decision. Until release qualification exists, rollback consists
of retaining the existing Rust/CLI/Python surfaces and omitting this namespace.
Only the exact Linux x86_64 combinations and artifacts in the evidence are tested.
Julia must consume accepted C-qualified library bytes; rebuilding the same source
does not establish binary identity or transfer acceptance to another host.
