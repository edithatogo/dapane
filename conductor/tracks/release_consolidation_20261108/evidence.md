# Execution and review evidence

Implementation date: **15 November 2026** (Australia/Brisbane).

The sections through the initial closure boundary preserve earlier observations.
The [current handoff receipt](../../../docs/release-handoff-2026-11-15.md) records
the completed provider/setup merges, incorporated archives, fresh live baseline,
notice implementation and remaining security/publication blockers.

## GitHub prerelease selection (21 November 2026)

The owner selected GitHub Releases under `edithatogo/dapane` for the
`v0.1.0` prerelease and deferred publication to PyPI and crates.io.
GitHub returned the authenticated login `edithatogo` and admin permission
on the repository. The releases and matching tag lookups returned empty lists.

The first selected candidate was `d02095d9bf7e89c6fc00805c4bc484a3ead3e33b`.
The successful hosted release run contains five verified provenance subjects.
Local `verify-matrix` accepted the downloaded Linux x86_64 CPython 3.15.1 target
for this source. The candidate passed 215 installed tests and ten independent
reference cases. [Release artifacts](https://github.com/edithatogo/dapane/actions/runs/44748104482)

The central job was queued at decision readback. The later executed scan failed.
Targeted OpenGrep diagnosis found two console sinks in the manual exchange CLI.
The source fix required a fresh candidate.
[Original scan](https://github.com/edithatogo/dapane/actions/runs/44748104889)

## Verified GitHub prerelease and in-place archive

- PR #67 moved the manual exchange's request-derived digests and SharePoint
  upload plan to explicit local files. The console reports fixed statuses and
  error summaries. All 12 manual exchange tests passed, including byte-identical
  retries and rejection without echoing raw diagnostics. The pinned OpenGrep
  analyzer covered all 121 tracked sources with zero findings on `fcfe244`.
  [Reviewed source change](https://github.com/edithatogo/dapane/pull/67)
- The published candidate is `5a24196c6e3b8905613dcf5100c239018c919b7a`
  (tree `b90e90da7fe07bbad0b6daa12ef783d40de043a9`). The Linux x86_64 CLI and
  CPython 3.15.1 wheel passed the two clean builds, 215 installed tests,
  10 independent references and exact-artifact provider replay. The dependency
  advisory and licence checks and the aggregate candidate matrix passed.
  The CLI, wheel, source archive, evidence and reproducibility receipt verified
  against the trusted GitHub-hosted `main` attestation.
  [Release assurance](https://github.com/edithatogo/dapane/actions/runs/44841721904)
- The same commit passed the central offline-security workflow. Job
  `136651486647` passed the isolated preconditions and the four layers in a
  network-disabled container, completing at `2026-11-21T00:21:22Z`. The
  one-job runner deregistered after completion.
  [Executed exact-source scan](https://github.com/edithatogo/dapane/actions/runs/44841722219)
- GitHub published the prerelease at `2026-11-21T00:36:28Z` after the scan passed.
  The tag resolved to the checked commit. All ten uploaded assets were
  downloaded from the public URLs, and their byte sizes and SHA-256 digests
  matched the staged files and GitHub's asset metadata.
  [Public prerelease](https://github.com/edithatogo/dapane/releases/tag/v0.1.0)

The [track metadata](metadata.json) retains the source and asset identities,
native readback and earlier candidate evidence. The original specification,
plan and dependency links remain at the authoritative track path.

## Publication control review — 20 November 2026

The manifest and generated candidate receipts now carry the requirement for
central offline-security evidence on the exact source. Matrix verification
rejects a receipt with missing or altered publication blockers. The 67 release
control tests passed, including regressions for an omitted gate, an unsupported
pass claim and a receipt that drops the blocker. The publication command
returned exit 2 and continued to report the unresolved registry identity.

The hosted release verification for main `c3b499e` passed on attempt 2 after
the transparency log returned a transient 404 in the signing step. The archived
CPython 3.15.1 package passed 215 installed tests and ten independent reference
cases. Local matrix verification passed for the downloaded artifact, and
`gh attestation verify` checked all five signed subjects against the exact main
revision and workflow. [Release run and artifacts](https://github.com/edithatogo/dapane/actions/runs/44737207139).

At review start, the central scan for main `c3b499e` had no runner assigned
and zero executed steps. The repository runner list returned zero registered
runners. Release assurance remains blocked on an executed scan for the release
source and verification of the intended registry identity.
[Offline security run](https://github.com/edithatogo/dapane/actions/runs/44737207951).

## Reconciliation and scope

The branch began at Dapane main
[d7063cecc26abe96a3f28fca575b99b450241430](https://github.com/edithatogo/dapane/commit/d7063cecc26abe96a3f28fca575b99b450241430).
The existing core-contracts PR 9, contribution-guide PR 10 and conditional offline
security PR 5 were inspected as separate owners. Core/kernel/Python tracks were
not silently declared complete or folded into release work. The offline security
draft retains its own runner/integration prerequisites.

The release work owns its new capability manifest, evidence script/tests,
release workflow, dependency policy and release documentation. It preserves the
existing numerical kernel, consumer APIs, toolchain/lockfile, runtime/privacy
workflows and other tracks.

## Initial findings and remediation

An independent Conductor acceptance review identified the mandatory licensing,
registry and real-consumer gaps. The later owner instruction resolves project licensing as Apache-2.0; registry and real-consumer gaps remain open. The current
documentation validator's acceptance of an archived state would not prove those
criteria; no premature archive is recorded.

The implementation adds exact-source/artifact binding, installed wheel payload
identity, both wire-profile references, explicit matrix completeness and clean
build comparison. Negative tests address altered binaries/receipts, stale source
or reference hashes, unsupported targets/ABI, duplicate/missing matrix members,
wheel substitution and loss of unknown capacity.

Source inspection also corrected the CLI version check to accommodate the
existing version output's contract suffix. Wheel verification checks installed
payload bytes, not merely a matching package version, and retains an explicit
native-layout/ABI scope. Independent review also identified a saved-report source
substitution gap and a same-directory comparison loophole. The remediation binds
both profiles' canonical input digests, quote/usage/capacity source snapshots and
report engine versions to the checked input, and requires distinct build directories.
Adversarial cases rehash a substituted quote snapshot and still require rejection.

## Verification status

The execution workspace was initially unavailable. After recovery, the candidate
assurance checks were executed on CPython **3.12.14**:

| Check | Actual result |
| --- | --- |
| Standard-library adversarial release tests | **31 passed** |
| Ruff 0.17.4 lint and formatting | Passed |
| Candidate manifest validation | Passed |
| Publication negative gate | Expected exit **2**; publication remains false |
| Conductor consistency | Passed: 14 tracks, 12 requirements, 145 tasks, 434 local links |
| Workflow YAML, 11 shell run blocks and embedded Python syntax | Passed |
| Rust 1.99.1 formatting and workspace Clippy with warnings denied | Passed |
| Locked offline native tests | **40 passed: 6 CLI, 9 capacity, 25 evaluator** |
| Minimal-feature release CLI and CPython 3.12.14 wheel | Built successfully |

The exact Rust 1.99.1 toolchain and all 36 checksum-matching registry crates were
available in existing caches. No compiler downgrade, dependency change or
network substitute was needed for the native build. Native verification began
at source commit 3c80b594e149fd81c27ac79bf9f6d36529b0e8d5; the subsequent review
fixes affect only release tooling/tests and documentation, not native source,
fixtures, package manifests or lockfile.

The independent reviewer closed all five findings: input/source provenance,
saved engine version, distinct build directories, interpreter-to-wheel pairing
and dependency versions against Cargo.lock. The reviewer independently ran the
two final consistency regressions and checked the diff. The full installed-reference
and repeatability work subsequently passed for all four interpreter targets at
published source 354df1, as recorded below.

## Completed local artifact qualification

The complete result is in [the dated qualification record](../../../docs/release-verification-2026-11-15.md).
At exact published source **354df1fd47fabcf8f2f571ac51566ad03d9cd3e4**, CPython
3.12.14, 3.13.5, 3.14.10 and 3.15.2 each passed two clean byte-identical builds,
clean installed collection/verification, 74 installed tests and contract checks.
All four same-source receipts passed aggregate matrix verification. Each receipt
contains ten independent synthetic reference reports and minimal-dependency evidence.

At that same source, all cargo-deny policy domains passed against recorded RustSec
revision 4ef2df8e806a65e2f1ecc14f56f51249062b23d6. Python build-tool auditing found
no known vulnerabilities in 36 resolved packages. Three CycloneDX 1.6 SBOMs were
generated without changing Cargo.lock. Bounded CLI performance was measured.
The separate SBOM-generator build warning and local-host limits are retained in
the dated record. Complete artifacts, receipts, logs and checksums were retained.

At the tested source, hosted Conductor, Privacy and Runtime workflows subsequently
passed. Release assurance remained queued; its Ubuntu artifact matrix and trusted-main
attestation are not inferred from local results. Exact run links are in the dated record.
This later documentation update records the tested source honestly; it does not
claim the earlier artifacts were built from this documentation commit.

Configured checks:

- Candidate-policy validation and adversarial standard-library unit tests.
- Ruff lint/format and Conductor consistency.
- Existing native, schema, installed-wheel and privacy/security checks.
- Two fresh builds and exact CLI/wheel byte comparison on Linux x86_64.
- Independent installed references and full Python tests for CPython 3.12–3.15.
- Default core/CLI dependency closure and zero Python runtime dependencies.
- Dated advisory/licence/source outcomes and per-crate CycloneDX SBOMs.
- The existing bounded 10/1,000/5,000-row CLI performance measurement.
- Complete same-source matrix verification; main-only attestation route.

The results above identify the executed checks. Hosted Release assurance execution
and trusted-main attestations still need their own outcomes. Failed-run artifacts
record failures and do not qualify a candidate.

## Subsequent integration and licensing

The owner selected Apache-2.0. The [integration record](../../../docs/release-integration-2026-11-15.md)
records consistent package metadata/licence payloads, the archived-track incorporation
audit, integration with main c70edf65, and the concrete hosted rustup bootstrap fix.
The current integration changes native scope and package contents; historical 354df1
receipts remain retained without being relabelled as fresh results. The 36 current
release-control tests and source/static checks passed. Full hosted qualification of
the integrated source remains required.

## Closure boundary at the initial audit

Public package publication remains disabled. Apache-2.0 is selected for Dapane
project material. Registry ownership, real workforce/genomics migration and external
repository archival are not established. The consolidation review selected no external archive and copied no
restricted provider assets.

The user requested review, fixes and archival. Review/fixes can be performed on
the candidate assurance implementation now. The original track's archival must
wait for its outstanding mandatory release acceptance evidence.

## Authorised owner handoff received

The later handoff was checked against live main e34f87c9 and release head d37575ec.
All four prerequisite tracks are archived and incorporated. The existing provider
verification and lock retain qualified workforce/genomics revisions and bounded
historical compatibility; the earlier real-consumer blocker is resolved within
that scope. Hosted Release assurance, provider consumers, Runtime, Conductor,
Privacy and CodeQL passed at d37575ec. Those exact run links and the observed
133 installed tests per target are in the current receipt.

Release changes add full authenticated dependency and Rust standard-library
notices, preserve Apache-2.0 project licensing, correct Python aggregate licence
metadata, and call the existing provider verifier using the exact release CLI
and wheel. The 64 local release-control tests and Ruff pass; notice generation
has an independent review. New artifact bytes and workflow coupling require
fresh hosted execution at the new source. The central offline security runs are
queued without an assigned runner and have no scanner outcome. Their gate is
preserved. Channel/account choices remain with the owner; publication is disabled.
No external repository archive or legacy machinery removal is implied.

## Hosted qualification of the notice and provider increment

At exact published source **5f03f28e3aa5a98c45c0853ce7498c86b181d66a**, all ordinary
hosted checks passed. The [source-bound receipt](../../../docs/release-qualification-5f03f28.json)
retains the four wheel/CLI identities, raw benchmark, full advisory outcome,
three SBOM hashes and the exact provider artifact download. All five downloaded
archives and their 100 member checksums were independently inspected. Actual
wheel and sdist metadata and all three legal payloads matched the intended policy.

Each interpreter passed 133 installed tests and ten independent references, plus
the installed interval rejection/tamper controls and two byte-identical clean
builds. The release provider job passed using those exact CPython 3.15 artifacts
in the existing workforce/genomics environments. Runtime separately passed 62
native and eleven tooling tests, plus its four installed suites. Release
aggregation, standalone providers, Conductor, Privacy and CodeQL passed. The
central offline jobs remain queued; trusted-main attestation was correctly skipped
on the PR. These results establish the recorded candidate scope while publication
and final security qualification remain blocked.

## Post-merge main qualification and signed attestation (0658d94 — 19 November 2026)

Following PR #17 (`f9e8fd7`) and PR #22 (`0658d94`) merges to `main`, source
`0658d94ad772023a0185a000b5254f9c2f4a63a9` (tree
`48c3ae972ed48e5e1e6e47862e99381323191fa7`) completed its `main` workflow runs.
The [post-merge qualification record](../../../docs/release-qualification-2026-11-19.md)
and [artifact receipt](../../../docs/release-qualification-0658d94.json) retain
the verified run IDs, artifact hashes, checksums, benchmark measurements and
offline attestation check:

- **Passed ordinary `main` workflows:** Release assurance (`43769725207`,
  including `manifest` 64 control tests, 4 candidate builds, `supply-chain`,
  `provider-candidate` on artifact `14184700967` with workforce 3.15.2 /
  genomics 3.15.1 / 196 native-boundary tests, `matrix` and trusted-main
  `attest` job `132994080532`), Runtime (`43769725112`: 62 native tests, 11
  tooling tests, 196 installed tests per CPython 3.12–3.15), Installed provider
  consumers (`43769725145`), Conductor validation (`43769725080`: 14 tracks, 12
  requirements, 155 tasks, 629 local links, 12 regression tests), Privacy and
  secrets (`43769725087`: 0 Gitleaks findings, Presidio 25/25 files clean),
  Standalone roadmap lanes (`43769725139`: newborn qualified) and CodeQL
  (`43769724700` / `44010763585`).
- **Downloaded artifact & matrix verification on clean `0658d94`:** All six
  archives from run `43769725207` matched their GitHub API SHA-256 digests; all
  100 `CHECKSUMS.sha256` entries (`20 + 20 + 20 + 25 + 15`) passed; and
  `python3 scripts/release_assurance.py verify-matrix` passed across all four
  CPython targets (`3.12.16`, `3.13.18`, `3.14.10`, `3.15.2`).
- **Signed trusted-main provenance verification:** `candidate-provenance`
  (`14184669447`, `attestation.json` 12,920 bytes, SHA-256
  `42e9a2d39c18233d5245af5728372d5554bb929a5dc333926c2ed4dd812e3d4a`) holds 14
  distinct SHA-256 subjects under `https://slsa.dev/provenance/v1` (Rekor log
  index `3912525884`, repository attestation `67905453`). All 20 candidate
  subject files across all four interpreter directories passed
  `gh attestation verify --bundle` (`gh 2.105.0`, `--source-ref refs/heads/main`,
  `--source-digest 0658d94ad772023a0185a000b5254f9c2f4a63a9`,
  `--deny-self-hosted-runners`).
- **Remaining blockers (`L1.2` and `L4.2`):** Publication stays disabled pending
  owner channel and registry-account choices (`L1.2`), and `Offline AI security`
  run `43769725442` (job `132982710619`) timed out in queue after 24 hours and
  was cancelled (`2026-11-16T22:31:07Z`) with `runner_id: 0` and 0 steps
  executed (`L4.2`). Track status remains `blocked` with `archive_performed: false`.
