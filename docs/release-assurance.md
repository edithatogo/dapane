# Candidate release assurance

This implements the executable part of
[release_consolidation_20261108](../conductor/tracks/release_consolidation_20261108/index.md).
The [capability manifest](../release/capabilities.json) describes a candidate to
check. It does not declare a released package or turn a proposed platform into a
supported one. Each run must produce fresh evidence for the exact clean source
commit and artifacts.

The [dated local qualification](release-verification-2026-11-15.md) records the
completed installed matrix, dual-build identities, SBOM/advisory outcomes and
measured limits at its exact source. The later
[handoff and hosted qualification record](release-handoff-2026-11-15.md) records
the incorporated owners' work and successful ordinary hosted checks at `5f03f28`,
with a [source-bound artifact receipt](release-qualification-5f03f28.json).
Central offline security remains unexecuted. Each subsequent source revision
still needs its own complete qualification.

## Scope and first-release prerequisites

The initial candidate includes the Rust core, JSON CLI, thin native Python
interface, five original synthetic examples and five explicit genomics capacity
examples. Contract 0.1 retains full-pool allocation; contract 0.2 preserves
unknown use/capacity and unallocated value. The package remains version 0.1.0.
Methods are paired explicitly with their wire versions. The integrated candidate
also preserves run-bundle profile 0.1 and the Rust/CLI interval envelope 0.1,
`dapane-intervals-v0.1.0`. The interval method rounds each generated segment;
there is no Python interval API. Installed bundle tests and independent installed
CLI interval checks cover those accepted additions.

A first public release requires the contracts, kernel and Python/two-consumer
tracks. All three are now archived on main with their bounded acceptance evidence;
the setup archive is also incorporated. The
[selected provider qualification](python-provider-verification.md) covers the
QLD HP3.1 base-salary quotation and manual DNA-extraction labour, with retained
legacy entry points and bounded historical replay. It does not qualify whole
assays, all workbook behaviour or other providers. These prerequisites remain
mandatory in the manifest. Optional MCHS/source adapters, reporting, newborn
programme qualification, Power Platform, R/Julia, process execution, decision
integrations and frontier research do not block this bounded first release.

The owner selected Apache-2.0 for Dapane project material on 15 November 2026.
The canonical LICENSE, NOTICE and THIRD_PARTY_NOTICES.txt are checked in source,
installed wheels and candidate CLI bundles. The dependency and standard-library
texts retain their source identities; the optional Python aggregate licence
expression is omitted as explained in [release controls](release-controls.md).
External provider assets remain excluded. Registry/channel choices and final
source qualification remain open. Workspace Cargo
publication stays disabled; this workflow has no registry publisher, release-tag
action or repository archive operation.
The publication check intentionally returns exit code 2 with those blockers:

~~~sh
python scripts/release_assurance.py validate
python scripts/release_assurance.py validate --publication
~~~

## Exact target matrix

The workflow requests these environments; a target becomes evidenced only when
its native installation, parity checks and receipt have succeeded on the same
source revision.

| Runner | OS and architecture | Interpreter | ABI |
| --- | --- | --- | --- |
| ubuntu-24.04 | Linux x86_64 | CPython 3.12 | Interpreter-specific |
| ubuntu-24.04 | Linux x86_64 | CPython 3.13 | Interpreter-specific |
| ubuntu-24.04 | Linux x86_64 | CPython 3.14 | Interpreter-specific |
| ubuntu-24.04 | Linux x86_64 | CPython 3.15 | Interpreter-specific |

Receipts record the actual Python patch version, libc, operating-system identity,
Rust/Cargo versions, source commit/tree and input hashes. Wheel tags alone do not
qualify other Linux distributions, manylinux redistribution, ARM, Windows,
macOS, PyPy, free-threaded Python or ABI3.

## What is checked

The [release workflow](../.github/workflows/release-assurance.yml) builds the CLI
and wheel twice with separate clean Cargo target directories. It compares the
actual bytes and names after fixing the source epoch and normalising build
paths. This establishes repeatability on the recorded runner. It does not
establish bit-for-bit reproducibility across different hosts or compilers.

A clean consumer installs the wheel without runtime dependency resolution. The
CLI executes outside the source checkout. The receipt collector verifies every
wheel payload against RECORD and compares the installed Python/native bytes
with the supplied wheel; another installation with the same version cannot
substitute silently. Both imports must resolve to that installation outside the
checkout. Rust performs all valuation.

All ten independently specified synthetic fixtures run through both interfaces.
The receipt includes the complete reports, expected-input hashes and output
digests. It compares totals, source lines, object shares, pools and explicit
unknown capacity states with the authored reference cases. The existing full
installed-wheel tests additionally exercise schemas, errors and numerical
invariants. The default native dependency closure is inspected separately from
the workspace, which legitimately also contains the PyO3 wrapper.

After all candidate builds pass, the release workflow calls the existing provider
workflow with the same run's CPython 3.15 CLI and wheel. It verifies the candidate
receipt before checking out the immutable providers, then uses their existing
verifier in separate locked Python 3.15.2 and 3.15.1 environments. The aggregate
matrix depends on this job as well as the build and supply-chain jobs. Standalone
provider checks remain available on pull requests and pushes to main.

The [supply-chain controls](release-controls.md) record dependency licences,
advisory outcomes, the advisory database revision, CycloneDX SBOMs and the
trusted-main provenance route. Those records supplement functional checks;
a self-authored JSON receipt is not a signed attestation or evidence of source
rights. A green candidate job does not resolve the publication prerequisites.

## Reproduce and inspect receipts

Build artifacts into separate directories, each containing the CLI named
dapane and one interpreter-specific wheel. Copy LICENSE, NOTICE and
THIRD_PARTY_NOTICES.txt into the collected candidate directory. Install one wheel into a clean
virtual environment. Run collection using that environment's interpreter from
outside the repository:

~~~sh
python /absolute/dapane/scripts/release_assurance.py compare \
  --first /absolute/build-one --second /absolute/build-two \
  --output /absolute/artifacts/reproducibility.json

/absolute/consumer/bin/python /absolute/dapane/scripts/release_assurance.py collect \
  --cli /absolute/artifacts/dapane \
  --wheel /absolute/artifacts/dapane-0.1.0-cp315-cp315-linux_x86_64.whl \
  --output /absolute/artifacts/evidence.json

python /absolute/dapane/scripts/release_assurance.py verify \
  --evidence /absolute/artifacts/evidence.json \
  --artifact-dir /absolute/artifacts

python /absolute/dapane/scripts/release_assurance.py verify-matrix \
  --directory /absolute/downloaded-candidate-artifacts
~~~

Use the wheel's actual filename; the example does not promise a particular
redistribution tag. Keep the original receipts and artifacts together. Commands
refuse to replace existing evidence files. Verification rejects changed
artifact bytes, another source commit, dirty tracked inputs, changed reference
or lock hashes, incomplete reference results and missing/duplicate matrix
targets. Verify against the source revision named in the receipt; later
documentation commits also have different identities.

Evidence verification checks consistency relative to the trusted source and
record. It cannot detect an adversary who replaces both artifacts and unsigned
records with a new coherent fabrication. Use the authenticated workflow run
and, for the trusted-main route, the signed attestations described in the
controls guide. Retain the original run identity and artifact digest.

## Numerical, scale and performance limits

The implemented contracts remain authoritative for the 4 MiB input boundary,
record limits, exact rational bounds, supported rounding and explicit economic
meanings. This release work does not change them or add acceleration.

Only the CPython 3.15 candidate job runs the bounded existing CLI benchmark:
10, 1,000 and 5,000 usage rows, valuation and allocation, three repeats. Its raw
record includes wall and child CPU times, output identity and peak child RSS
across the measurement. This is a Linux single-runner observation, not
per-workload memory, a real-provider workload or a comparative speedup claim.
Other interpreter jobs run installed functional checks without inheriting a
new performance claim.

## Migration and consolidation

Use the [migration and recovery procedure](release-migration.md) before changing
a consumer. The [consolidation inventory](release-consolidation.md) selects no
repository for archival or code removal. The original release track remains
open until its remaining registry/channel decisions and exact-source qualification,
including the centrally managed security execution, are complete;
a successful documentation validator does not justify premature archival.
