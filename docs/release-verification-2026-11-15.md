# Local release qualification — 15 November 2026

The subsequent [integration and licensing record](release-integration-2026-11-15.md)
records Apache-2.0 adoption and accepted kernel/contracts integration. The results
below remain observations of the original, earlier source.
The [later handoff record](release-handoff-2026-11-15.md) supplies the merged-owner
receipt and hosted baseline; it does not relabel the local results below.

## Checked source and scope

The complete local artifact qualification used source
[354df1fd47fabcf8f2f571ac51566ad03d9cd3e4](https://github.com/edithatogo/dapane/commit/354df1fd47fabcf8f2f571ac51566ad03d9cd3e4),
tree `9e103806053ec18e4eaf588268be79c4995ddb34`.
The environment was Linux 6.18.57, x86_64, glibc 2.41, Rust/Cargo 1.99.1 and
Maturin 1.16.0. These results are local observations. The configured hosted
Ubuntu Release assurance workflow and trusted-main attestation still require their
own outcomes.

The subsequent Conductor/evidence documentation commit records these historical
results; it does not relabel them as execution on a later source commit. No kernel,
Python runtime, manifest, lockfile, fixture or test implementation is changed by
that recording step.

## Installed matrix and artifact identities

Each interpreter used two distinct, initially empty Cargo build directories.
Both actual CLI/wheel outputs were retained and compared byte for byte. A clean
consumer installed the exact wheel without resolving runtime dependencies, then
ran the release collector/verifier, installed Python tests and CLI contract checks
from outside the checkout. Aggregate matrix verification passed for all four
same-source receipts.

| CPython | Installed tests | Independent references | Two clean builds | Wheel SHA256 |
| --- | --- | --- | --- | --- |
| 3.12.14 | 74 passed | 10 passed | Byte-identical | `0f24277a758a991d212b2cdb46eb5be7c85aa62b335ada36312db71166171505` |
| 3.13.5 | 74 passed | 10 passed | Byte-identical | `2b418bd6f643cff3f0f84ca5e66aa3b97f67b7980beb650cf055a282539bdd96` |
| 3.14.10 | 74 passed | 10 passed | Byte-identical | `be340fd11f0e38a5d5d6e7c25aa491658bd38d67bb463956b8a4fbaf06762249` |
| 3.15.2 | 74 passed | 10 passed | Byte-identical | `06e5668c2115fdd69180185b174fe075dfb8e10c129b50a33f59819e4ea94ce7` |

All CLI builds produced the same SHA256:
`cd8eca067cb37406dfe8fbce094ccb7175e8a34d25a0afb1a535ade44455ead8`.
The wheels are tagged for their respective CPython interpreter and
`manylinux_2_34_x86_64`; those tags do not establish additional distribution,
ABI or platform support.

Every receipt recorded zero Python runtime dependencies and the 29-package
minimal core/CLI dependency closure. Both contract 0.1 and 0.2 source identities,
methods and independent synthetic values were verified. Unknown capacity was
retained as unknown. Every receipt has `publication_ready: false`.

The 31 release assurance regression tests, Ruff lint/format, manifest validation,
expected negative publication gate, Conductor validation and workflow syntax
checks also passed. Earlier native formatting, Clippy and 40 behavioural tests
(6 CLI, 9 capacity, 25 evaluator) passed at
[3c80b594](https://github.com/edithatogo/dapane/commit/3c80b594e149fd81c27ac79bf9f6d36529b0e8d5).
A scoped Git comparison confirmed no crate, Python runtime, Cargo manifest/lockfile,
pyproject or installed-test changes between that commit and the qualified source.

## Hosted workflow observations

The following hosted results were observed for the tested source `354df1` after
local qualification. These observations are tied to that source and those runs;
a subsequent documentation commit receives its own checks.

| Workflow | Exact run | Observed outcome |
| --- | --- | --- |
| Conductor validation | [43652925908](https://github.com/edithatogo/dapane/actions/runs/43652925908) | Success |
| Privacy and secrets | [43652925968](https://github.com/edithatogo/dapane/actions/runs/43652925968) | Success |
| Runtime | [43652925937](https://github.com/edithatogo/dapane/actions/runs/43652925937) | Success |
| Release assurance | [43652925904](https://github.com/edithatogo/dapane/actions/runs/43652925904) | Queued |

The hosted Release assurance artifact matrix and signed trusted-main provenance
remain unverified. Local results do not substitute for those outcomes.

## Dependency and SBOM outcomes

The controls were executed in an isolated worktree at the same published source.
Cargo.lock remained unchanged and the source was clean afterwards.

| Control | Observed outcome |
| --- | --- |
| Locked Cargo metadata | 39 workspace and registry packages recorded |
| Duplicate crate check | No duplicate crates |
| cargo-deny 0.20.2 | Advisories, bans, licences and sources passed with zero errors/warnings |
| RustSec database | `4ef2df8e806a65e2f1ecc14f56f51249062b23d6` |
| pip-audit 2.10.1, build/assurance requirements | 36 packages; no known vulnerabilities reported |
| cargo-cyclonedx 0.5.10 | Three CycloneDX 1.6 JSON SBOMs generated |

| SBOM | Components | SHA256 |
| --- | ---: | --- |
| dapane-core | 26 | `4208cc16656f1f7852d79497659aedf5c2b94cb883d0f42654988878259013a3` |
| dapane-cli | 27 | `87924a056456dbf7fda82a8dfad766b0398daf9a9e9adba1ff51411988cb92a6` |
| dapane-python | 36 | `272714b353d0d9a564a6412d85d344c0e4a12da5811d8750b7bbea4f79e27ba7` |

Dapane's project licence remains unresolved; the dependency licence result excludes
only its unpublished workspace packages from licence clearance. The upstream
locked installation of cargo-cyclonedx 0.5.10 emitted a warning for yanked
`xml-rs 0.8.19` in that tool's own build graph. That observed limitation is retained;
Dapane's checked runtime graph had no corresponding policy finding. No compiler
or complete assurance-tool build graph certification is implied.

## Bounded performance observation

The existing synthetic benchmark ran at 10, 1,000 and 5,000 usage rows, with three
repeats for valuation and valuation plus allocation. The CPython 3.15.2 measurement
of the installed CLI recorded:

| Usage rows | Valuation median | Valuation plus allocation median |
| ---: | ---: | ---: |
| 10 | 1.46 ms | 2.50 ms |
| 1,000 | 23.78 ms | 31.27 ms |
| 5,000 | 180.10 ms | 243.21 ms |

Peak child RSS across this measurement was **85,044 KiB**. It is not a per-workload
memory measurement. The additional 3.12 run and raw timings are retained with the
receipts. This shared-host synthetic observation establishes no general speedup,
real-provider performance, economic-method validation or other-platform support.

## Review and remaining acceptance

Independent review closed five concrete findings, with regressions: saved source
provenance, saved engine identity, same-directory build comparison, interpreter/
wheel pairing and locked dependency versions. No further concrete implementation
blocker was identified within that review scope.

The full source-bound receipts, both independent artifact sets, JUnit results,
command logs, raw benchmark records, SBOMs and checksums have been retained as a
candidate verification bundle. Source code remains in the pinned Git repository.
Unsigned local receipts are consistency evidence; signed trusted-main provenance
and hosted workflow results remain separate.

The [original release track](../conductor/tracks/release_consolidation_20261108/index.md)
remains blocked on project licensing/registry identity, applicable redistribution
conditions, real workforce/genomics consumer qualification and outstanding hosted
checks. Optional integration tracks do not gate the first release. No external
repository archive, legacy API removal or public package publication was performed.
