# Rust kernel acceptance and closeout

Date: **15 November 2026** (Australia/Brisbane). Track: `rust_kernel_20261108`.
Scope: the unpublished `0.1.0` candidate, point/capacity profiles 0.1/0.2 and the
separate interval schema 0.1 / method `dapane-intervals-v0.1.0`.

The bounded kernel acceptance is **passed** on Linux x86_64. This record binds
actual local native and installed-artifact execution to source trees, records
independent review and preserves the narrower scope of each check. Synthetic
references qualify computation, not provider truth or empirical economic validity.

## Source and review identities

| Record | Identity and meaning |
| --- | --- |
| Initial integration base | `d7063cecc26abe96a3f28fca575b99b450241430` |
| Retained acceptance-test baseline | `6da9d531a30be587fbc7f4b629fbeb677934d088` |
| Implementation and first review fixes | `2d4698a33249845182ee41e2184040eb088af475` |
| Qualified corrected source | `023dc4b61452caa0e4ba886d76333f4c398c8498`, tree `3ce4e29d8eafabf6afb837bc762ac277cf13f536` |
| Equivalent local test commit | `19c460ada9e810f6aedb6f53ef5d29cfec780876`, the same tree `3ce4e29…` |
| Accepted prerequisite | PR #9, merged as `224cf91dbcf513feaa022b2cf5aa310a965472ce` |
| Qualified integrated source | `a703c93d49e782b67fe4b14588bf1fb26292bb23`, tree `006a11a59e33c42c42ee4ab815b5cdb632caf55e` |
| Equivalent local integration | `7bac5e4db2b6e239ba9fd7e52ab542f477445215`, the same tree `006a11a…` |

Native execution used the corrected working content subsequently committed as
`19c460a`; it does not claim that unmodified `2d4698a` compiled. Git tree equality
binds that execution to published `023dc4b`. The main integration changed no Rust,
Python-wrapper, Cargo, toolchain or packaging input. The installed wheels were
therefore reused for the **expanded merged Python suite**, with byte identity
checked independently. Final closeout edits contain documentation and retained
evidence, with no numerical, test, schema or packaging changes.

The [review record](review.md) retains the findings and corrections. The final
independent re-review inspected interval implementation blob
`328ee914436b6239f8f23a5b5eb054be2192a1eb` and checker blob
`9e4dfd8c2ec6b02108c0add3be5299950de153fe`, finding no remaining blocking defect.
PR #9's separate track records were preserved; this archive closes the kernel
track only. The unrelated conditional offline-security PR #5 is not part of it.

## Observed execution

| Check | Observed result |
| --- | --- |
| Rust formatting and workspace Clippy | Passed, warnings denied |
| Native tests | **62 passed**: CLI 6, interval CLI 2, capacity 9, valuation 25, interval review regressions 8, interval acceptance 12 |
| Minimal release build | Core and CLI passed with `--no-default-features` |
| Clean CLI installation | Passed; separately installed executable used for reference and interval validation |
| Original contract check | Four schemas, five fixtures, 37 schema/parser negatives, five independently checked CLI reports, 14 runtime rejections and three identity/context cases passed |
| Interval contract check | Two schemas, nine structural negatives, exact reference/lineage/digest/replay/order checks, 11 runtime rejections and **15 schema-valid tampered-report controls** passed |
| Dependency tooling regressions | **11 passed** |
| Full dependency qualification | **36** registry packages matched lock/inventory/fetched manifests; **29** packages in the native closure, including core and CLI |
| Python formatting/lint after integration | Passed, all 15 applicable Python files already formatted; retained the merged bundle-verifier target |
| Conductor structure and archival | Passed: 14 tracks, 12 requirements, 149 tasks and 493 local links; all seven focused archive-validator regressions also passed after archival |
| Pinned local secret/privacy baseline | Gitleaks 8.30.1 and Presidio 2.2.366 passed the integrated commit range with zero findings; explicit commit scope and complete selected-text coverage retained |

The 12 interval acceptance tests include a loop over 25 durations, checking exact
quantity conservation and ordering. The eight review regressions exercise encoded
byte amplification, generated-ID collisions, nested duplicate keys, component-set
ordering, shared-parent end dates, generated rational precision, cross-mode pools
and total expanded record bounds. The original five fixture digests remain unchanged.

### Retained failing baseline

The retained baseline was executed **retrospectively after implementation had
been authored**, once the local pinned toolchain and complete cache were available:

```sh
cargo test --locked --offline -p dapane-core --test intervals
```

At `6da9d531…` it exited 101 with `E0432`, unresolved import
`dapane_core::evaluate_intervals_json`, as intended for the missing API. It is an
observed failing baseline, not a claim that a local fail-first run preceded all
implementation. Earlier attempts that lacked cached dependencies are not counted
as the expected failure. The subsequent compiler-discovered borrow error in
diagnostic mapping was fixed before the passing native run.

### Installed Python artifacts

All wheels were freshly built for their own interpreter using Maturin 1.16.0,
Rust 1.99.1 and locked Cargo dependencies. Each was installed with `--no-deps` into
a separate environment. Tests ran outside the checkout, with `PYTHONPATH` unset
and `--import-mode=importlib`; Python and native imports resolved in `site-packages`.
Pytest 9.2.0, jsonschema 4.26.0, Maturin 1.16.0 and Ruff 0.17.4 were pinned.

| Interpreter | Full merged suite | Wheel SHA-256 |
| --- | --- | --- |
| CPython 3.12.14 | **133 passed**, 3.42 s | `e3f123ea0a7c3d8fe2eb12db5747876c44733e967c526c11e579cb6773627286` |
| CPython 3.13.5 | **133 passed**, 3.41 s | `4ced6a9cf7484dfc5ed60ad54b3c54b2a885d137c19e99c47010af7e165c7505` |
| CPython 3.14.10 | **133 passed**, 3.07 s | `dd87c5e0c4103393dd6c760d0006da4e18e2d4fdfd51e0322f60e45fd962c0d7` |
| CPython 3.15.1 | **133 passed**, 3.04 s | `160cba6a06dcb1295ef7e3e39ec4722ae91e255f88b243036de2b62628e8764f` |

The expanded suite includes the accepted immutable-bundle and archive-validator
regressions from PR #9. This qualifies the existing Python wrapper after the kernel
change; the new interval API itself is Rust/CLI only. The wheel filenames carry
`manylinux_2_34_x86_64`, but these local tests establish only the observed Linux
x86_64 environment, not a redistribution or wider-platform claim.

## Reproduction commands

Use the pinned Rust 1.99.1 toolchain and `requirements-dev.txt`. The local native
run used a complete existing Cargo cache and `CARGO_NET_OFFLINE=true`; isolated
build targets prevented artifacts from the retained failing baseline being reused.
`PYO3_PYTHON` selected an installed supported interpreter for workspace Clippy.

```sh
cargo fmt --all --check
cargo clippy --workspace --locked --all-targets -- -D warnings
cargo test --locked
cargo build --locked --release --no-default-features -p dapane-core -p dapane-cli
cargo install --locked --path crates/dapane-cli --root "$CLI_PREFIX"
python scripts/validate_contract.py --cli "$CLI_PREFIX/bin/dapane"
python scripts/validate_intervals.py --cli "$CLI_PREFIX/bin/dapane"
python -m unittest discover -s tests/tooling -p test_qualify_kernel.py -v
python scripts/qualify_kernel.py
python scripts/validate_conductor.py
ruff check python tests/python scripts/validate_contract.py scripts/benchmark_cli.py scripts/verify_run_bundle.py scripts/validate_intervals.py scripts/qualify_kernel.py tests/tooling
ruff format --check python tests/python scripts/validate_contract.py scripts/benchmark_cli.py scripts/verify_run_bundle.py scripts/validate_intervals.py scripts/qualify_kernel.py tests/tooling
```

For each supported interpreter, create a fresh environment, install the pinned
development requirements, build/install its wheel and test from an external
working directory. `$REPO`, `$WHEEL_DIR` and `$OUTSIDE` denote absolute task paths:

```sh
maturin build --locked --release --interpreter python --out "$WHEEL_DIR"
python -m pip install --no-deps "$WHEEL_DIR"/*.whl
cd "$OUTSIDE"
env -u PYTHONPATH python -m pytest --import-mode=importlib "$REPO/tests/python" -q
```

The compiler was `rustc 1.99.1 (58cf8f9c3 2026-10-13)`, commit
`58cf8f9c35b355199727627d07ae34a4e2846d67`; Cargo was
`1.99.1 (5f94df478 2026-08-27)`, host `x86_64-unknown-linux-gnu`, LLVM 23.1.1.
This demonstrates the declared minimum; no older compiler support is inferred.
The [dependency record](../../../docs/kernel-dependencies.md) distinguishes the
checked development dependency boundary from project-licence/publication decisions.

## Independent references and acceptance mapping

| Acceptance | Evidence and result |
| --- | --- |
| Exact quantities, quotations and invalid combinations | `1/3 × 90 + 2/3 × 120 = 110`; malformed dates, coverage gaps/overlaps, incompatible units/views, stale or missing selected quotes and unsupported precision fail with structured errors |
| Conserving allocation and duplicate-charge protection | Full-pool allocation conserves 110; capacity example allocates 33 and retains 77 unallocated; original parent/source/component validation precedes generated identities |
| Exact CLI transport, source pinning and completeness | Parent/quote/context snapshots retained; generated tuple identities independently checked; missing capacity remains unknown; expanded request replays the complete scalar report |
| Direct activity valuation | `2.50 × 17 = 42.50` without creating resource-use records |
| Deterministic reproduction | Repeated/order-permuted requests give identical reports; both envelope hashes are independently reconstructed; original scalar digests remain unchanged |
| Independent minimal native execution | Default core/CLI members; minimal release build and clean CLI install; native closure excludes Python, table, network, simulator and GPU packages |

The rounding counterexample is deliberate: `0.005 + 0.005 = 0.01` exactly, but
per-segment half-even rounding gives `0.00 + 0.00 = 0.00`. Exact quantity/value
conservation does not promise invariance under arbitrary additional segmentation.
Each result retains the method identity and original segment-determining inputs.

## Bounded performance observation

The [retained measurement](evidence/benchmark.json) used the independently installed
release CLI and three repetitions of 5,000-row synthetic valuation and allocation:

```sh
python scripts/benchmark_cli.py --cli "$CLI_PREFIX/bin/dapane" --counts 5000 --repeats 3 --output benchmark.json
```

| Workload | Median wall time | Recorded child CPU times |
| --- | --- | --- |
| 5,000-row valuation | 0.254592 s | 0.211981, 0.260503, 0.253008 s |
| 5,000-recipient allocation | 0.308880 s | 0.377906, 0.300423, 0.263586 s |

The run checked the exact total of 150,000 and allocation conservation. Maximum
child RSS across the complete run was 85,052 KiB, not per-workload memory.
Wall times include process startup and JSON IO. Environment: Linux 6.18.57,
x86_64, glibc 2.41, Python 3.12.14. These are bounded observations, not interval
throughput, concurrency, provider, acceleration or cross-machine comparisons.

## Evidence retention, CI and scope

The [evidence manifest](evidence/manifest.json) binds raw retained test logs,
artifact hashes and the benchmark. The [review](review.md) records independent
findings and their disposition. Existing Runtime, Conductor and Privacy/secrets
workflows remain configured without weakened gates. At this closeout's observation,
hosted jobs for integrated head `a703c93…` were queued: Runtime
[43653291385](https://github.com/edithatogo/dapane/actions/runs/43653291385),
Conductor [43653291335](https://github.com/edithatogo/dapane/actions/runs/43653291335)
and Privacy/secrets
[43653291336](https://github.com/edithatogo/dapane/actions/runs/43653291336).
Those queued jobs are **not** recorded as passing. The acceptance evidence above
is actual local execution of the pinned native and four-interpreter installed
matrix, including the accepted prerequisite. Current hosted status is visible in
[PR #16](https://github.com/edithatogo/dapane/pull/16).

The interval method supports only explicitly declared uniform calendar-day exposure
and selected quotes. It bounds the original and expanded request to 4 MiB, generated
plus point rows to 10,000, expanded top-level records to 20,000 and replayable exact
number precision. Source/context cloning occurs only after encoded-size reservation.
It does not infer timestamps, timezones, working calendars, utilisation, source
eligibility or an economic capital formula.

Optional Arrow/Parquet remains explicitly deferred under K3.2 because the selected
first consumers use exact JSON. Project-licence selection, distribution notices,
source-data rights and registry publication remain in release consolidation;
`publish = false` is retained. Real providers, other platforms, R/Julia, process
execution and empirical validation retain their own tracks.

For recovery, retain the exact envelope, scalar report, source commit, lockfile,
toolchain and artifact identity. Re-evaluate the retained expanded request with
the matching scalar method and compare the complete report and recorded digest.
Existing point callers continue using `evaluate` and their original schemas;
the original five fixture-digest regression is the compatibility evidence.
The archive retains this track's specification, plan, review, evidence, stable
dependency ID and links in place; it does not archive any repository or other track.
