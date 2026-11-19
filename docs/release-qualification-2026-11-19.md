# Post-merge `main` release qualification and signed attestation — 19 November 2026

This record binds the merged default-branch baseline
[`0658d94ad772023a0185a000b5254f9c2f4a63a9`](https://github.com/edithatogo/dapane/commit/0658d94ad772023a0185a000b5254f9c2f4a63a9)
(tree `48c3ae972ed48e5e1e6e47862e99381323191fa7`, after PR #17 `f9e8fd7` and
PR #22 `0658d94` merged to `main`) to its executed GitHub Actions results,
downloaded candidate artifacts, local `verify-matrix` check and offline
Sigstore attestation verification. Machine-readable identities and measurements
are retained in
[release-qualification-0658d94.json](release-qualification-0658d94.json).

The earlier PR #17 records
([release-handoff-2026-11-15.md](release-handoff-2026-11-15.md) and
[release-qualification-5f03f28.json](release-qualification-5f03f28.json)) remain
preserved as historical observations of source `5f03f28`. Adding these
documentation receipts does not relabel candidate artifacts as built from the
documentation commit.

## Observed `main` workflows at `0658d94`

| Workflow | Run | Outcome |
| --- | --- | --- |
| Release assurance | [43769725207](https://github.com/edithatogo/dapane/actions/runs/43769725207) | **Passed**: manifest (`132982715205`, 64 control tests), 4 candidate builds, supply-chain (`132985930716`), provider-candidate (`132988843013`), matrix (`132991086540`) and trusted-main `attest` (`132994080532`) |
| Runtime | [43769725112](https://github.com/edithatogo/dapane/actions/runs/43769725112) | **Passed**: 62 native tests, 11 tooling tests, 196 installed Python tests per target (3.12–3.15) |
| Installed provider consumers | [43769725145](https://github.com/edithatogo/dapane/actions/runs/43769725145) | **Passed**: workforce (Python 3.15.2), genomics (Python 3.15.1) and 196 native-boundary tests |
| Conductor validation | [43769725080](https://github.com/edithatogo/dapane/actions/runs/43769725080) | **Passed**: 14 tracks, 12 requirements, 155 tasks, 629 local links and 12 regression tests |
| Privacy and secrets | [43769725087](https://github.com/edithatogo/dapane/actions/runs/43769725087) | **Passed**: 0 Gitleaks findings; Presidio 25/25 selected files scanned, 0 blocking and 0 advisory findings |
| Standalone roadmap lanes | [43769725139](https://github.com/edithatogo/dapane/actions/runs/43769725139) | **Passed**: newborn synthetic lane qualified (`newborn-tests: passed`) |
| CodeQL | [43769724700](https://github.com/edithatogo/dapane/actions/runs/43769724700) / [44010763585](https://github.com/edithatogo/dapane/actions/runs/44010763585) | **Passed**: Actions, Python and Rust analyses |
| Offline AI security | [43769725442](https://github.com/edithatogo/dapane/actions/runs/43769725442) | **Cancelled (unexecuted)**: job `132982710619` queued `2026-11-15T22:31:07Z` and auto-cancelled `2026-11-16T22:31:07Z` after 24h timeout (`runner_id: 0`, 0 steps executed) |

## Verified artifact matrix and checksums

All six artifacts from Release assurance run `43769725207` were downloaded on a
clean checkout of `0658d94ad772023a0185a000b5254f9c2f4a63a9`, verified against
their GitHub Actions API SHA-256 digests, unpacked outside the repository,
checked across all 100 entries in `CHECKSUMS.sha256` (`20 + 20 + 20 + 25 + 15`),
and verified with `python3 scripts/release_assurance.py verify-matrix`
(`Verified 4 installed interpreter targets`, exit 0).

Each CPython target ran on Linux `x86_64` with `glibc 2.39`, Rust `1.99.1`,
and `Cargo 1.99.1` (`ubuntu-24.04` Azure/AWS runner kernels recorded per receipt),
passing two byte-identical clean builds, **196 installed tests** (up from 133
at `5f03f28` following PR #22's 63 newborn tests), 10 independent
scalar/capacity references, 9 interval schema rejections, 11 interval runtime
rejections and 15 tampered-report controls:

| CPython | Artifact ID | Archive SHA-256 | Wheel bytes | Wheel SHA-256 |
| --- | ---: | --- | ---: | --- |
| 3.12.16 | `14183709100` | `b5422a590ceeb29ae1d3ec8e9da62a67bae653f32a5fdece3f2bee77a7f60414` | 722,188 | `e68d2b6f0d6b9c15ce4acb17a52f1d34c27eb2bf031d7f1982473e7e0d508179` |
| 3.13.18 | `14184845444` | `28125e08802adbf3e4cc1321c7ab596a21c5f2ab1e7a732993435ce4ffb8080b` | 722,507 | `25c35146b2648bce04ae869896ae34b704e09f12f06e7f1855127a685e69e1c8` |
| 3.14.10 | `14184169481` | `ec8bbc4e87ae1f78892e946a4de6414445e2252718ec322b269f480d444d49ca` | 722,650 | `20a2f6fc4849608af586aec0c3326d08693ad46642d503909f603fcdfa982fd0` |
| 3.15.2 | `14184700967` | `39d333b8988f996cd4baa03a38e9721c78d1d4b8ed2031100d865105e21617d8` | 722,753 | `3a340622b86505765e8ff93b993b321b0f89778ad05e9a0e0d92393ff5971371` |

Common candidate payloads across the matrix:

- **CLI binary (`dapane`):** 1,446,888 bytes, identical across all four targets,
  SHA-256 `2d3f3c5b54399a3613d4b6d97e8538cadc3074192fdd076f261118d1a67b03a2`.
- **Source archive (`source.tar.gz`):** 1,137,262 bytes, identical across all
  four targets, SHA-256 `9997199b41bff82d588974f980b5ede31a7a58839a6f23143932d4681b8d0826`.
- **Python sdist (`dapane-0.1.0.tar.gz`):** SHA-256
  `9087e2fe0572b5ffc90beb1c6b743bc9583af13077aafecb0370c4d5f8ec810b`; Metadata
  2.4; optional `License-Expression` and `License` omitted; `License-File`
  lists `LICENSE`, `NOTICE` and `THIRD_PARTY_NOTICES.txt` with payloads matching
  the repository root across CLI companions, wheels (`requires_dist: []`),
  sdist and Cargo crate inventories (`dapane-core` 18 files, `dapane-cli` 10
  files, `dapane-python` 8 files).
- **Minimal native closure:** 29 packages, zero Python runtime dependencies.

## Exact-artifact provider check, supply-chain and benchmark

- **Exact-artifact provider job (`132988843013`):** downloaded
  `candidate-python-3.15` (`14184700967`), verified archive digest
  `39d333b8988f996cd4baa03a38e9721c78d1d4b8ed2031100d865105e21617d8`, and passed
  `workforce` (`3.15.2`), `genomics` (`3.15.1`) and 196 native-boundary tests.
- **Supply-chain artifact (`14184079965`):** archive SHA-256
  `2013777a368b3604fc2762ae5716e9c6efafa4771145b1ede5f2234c6f824c21`, 15 members
  verified. `cargo-deny 0.20.2` passed all four domains (`0` errors, `0`
  warnings, `38` licence helps) against RustSec advisory-db
  `02e2517f457a359fc6d3440ea4560c8ea188fee8` (`2026-11-15T22:53:27Z`);
  `pip-audit` checked 36 Python build/assurance packages with 0 known
  vulnerabilities; three CycloneDX 1.6 SBOMs were produced (`dapane-core` 26
  components, `dapane-cli` 27, `dapane-python` 36).
- **Bounded CPython 3.15 CLI benchmark (3 repeats per scale, including startup
  and JSON I/O):**

| Usage rows | Valuation median (s) | Allocation median (s) |
| ---: | ---: | ---: |
| 10 | 0.001046 | 0.001422 |
| 1,000 | 0.020460 | 0.029945 |
| 5,000 | 0.152769 | 0.247505 |

Peak child RSS across the benchmark run was **86,428 KiB**. This single-runner
synthetic measurement is not per-workload memory, an empirical workload, or a
cross-host performance claim. Actions artifacts expire after 30 days; preserve
candidate and provenance artifacts beyond that window before any release or
recovery-dependent decision.

## Trusted-main signed provenance

Job `attest` (`132994080532`) signed candidate artifacts on the eligible push to
`refs/heads/main`, producing artifact `candidate-provenance` (`14184669447`,
archive SHA-256 `8ddd20a090a6c5b03bb5e234bccfa9d14a8e6f95023423dcbf97085b52209810`)
containing `attestation.json` (12,920 bytes, SHA-256
`42e9a2d39c18233d5245af5728372d5554bb929a5dc333926c2ed4dd812e3d4a`, predicate
`https://slsa.dev/provenance/v1`, Rekor log index `3912525884`, repository
attestation `67905453`).

The bundle contains **14 distinct SHA-256 subjects** covering all **20 candidate
subject files** (`dapane`, `*.whl`, `source.tar.gz`, `evidence.json` and
`reproducibility.json` across all four interpreter directories, where `dapane`
and `source.tar.gz` share one digest each across targets). Using `gh 2.105.0`,
all 20 files passed offline verification against `attestation.json`:

```sh
gh attestation verify <subject-file> \
  --bundle <path-to>/attestation.json \
  --repo edithatogo/dapane \
  --signer-workflow edithatogo/dapane/.github/workflows/release-assurance.yml \
  --source-ref refs/heads/main \
  --source-digest 0658d94ad772023a0185a000b5254f9c2f4a63a9 \
  --deny-self-hosted-runners
```

## Remaining blockers keeping `release_consolidation_20261108` blocked

1. **`L1.2` (`[!]`):** Package publication remains disabled (`publication.enabled: false`, `registry_identity: "unverified"`, Cargo `publish = false`). First-release channels and controlling registry accounts/organisations remain open owner decisions.
2. **`L4.2` (`[!]`):** Centrally managed `Offline AI security` run [`43769725442`](https://github.com/edithatogo/dapane/actions/runs/43769725442) (job `132982710619`) was auto-cancelled after 24 hours in queue with `runner_id: 0` and 0 steps executed on required runner labels `self-hosted`, `linux`, `x64`, `ai-security-offline`. No gate is waived; `release_consolidation_20261108` remains `blocked` and unarchived (`archive_performed: false`).
