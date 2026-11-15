# Release qualification handoff — 15 November 2026

Follow-up: ordinary hosted qualification has now passed at exact source
**5f03f28e3aa5a98c45c0853ce7498c86b181d66a**, including the new notice bytes and
the existing provider verifier consuming the release artifacts. Its
[artifact receipt](release-qualification-5f03f28.json) retains exact identities
and outcomes. Central offline security is still queued and publication remains
disabled. The earlier baseline below is retained with its original source.

## Receipt and exact source boundary

Received the owner's authorised consolidation handoff, including the provider
owner's **15 November 2026, 01:42 UTC** completion report and the setup owner's
durable review. Continued the existing release branch and
[PR #17](https://github.com/edithatogo/dapane/pull/17). No new implementation owner,
external chat, provider implementation or numerical method was introduced.

Fresh live inspection found main
[`e34f87c9df39a2132fecee142431cdeefb732471`](https://github.com/edithatogo/dapane/commit/e34f87c9df39a2132fecee142431cdeefb732471),
tree `c07a6b2589b9d665f619f5d977d66e513180bab4`, and PR #17 head
[`d37575ec5662393f3831db5f827d63df00bfc37d`](https://github.com/edithatogo/dapane/commit/d37575ec5662393f3831db5f827d63df00bfc37d),
tree `170684cdb4480473e8e6fa0b729984a966c00899`. The release branch already
incorporates this main history. The workspace fast-forwarded to that head without
discarding the coordinator's merges. This record distinguishes that tested
baseline from the subsequent notice and release-provider workflow changes.

## Incorporated owners and archives

| Owner/track | Merged integration | Durable record consumed |
| --- | --- | --- |
| Setup | [Dapane PR #14](https://github.com/edithatogo/dapane/pull/14), `c229a16d07b75bc67989368b502c898ea7a946c4` | [Archived setup review](../conductor/tracks/conductor_setup_20261108/review.md), qualified source `0649a044b2e9eac051a77c139ed3b5d618130ac0` |
| Core contracts | [PR #9](https://github.com/edithatogo/dapane/pull/9), `224cf91dbcf513feaa022b2cf5aa310a965472ce`; archive [PR #18](https://github.com/edithatogo/dapane/pull/18), `c70edf65a119d9ffda410cd4e5325e1f37e9332a` | [Core acceptance and verification](../conductor/tracks/core_contracts_20261108/verification.md) |
| Rust kernel | [PR #16](https://github.com/edithatogo/dapane/pull/16), `172d0ef39291a936a35c6e221eb467701ccefbba` | [Kernel verification](../conductor/tracks/rust_kernel_20261108/verification.md), retained independent review and archive evidence |
| Python and two consumers | [Dapane PR #13](https://github.com/edithatogo/dapane/pull/13), `1a9012fff2904cb8719cb275d3020d0162f90455` | [Provider verification](python-provider-verification.md), [provider lock](provider-consumers.lock.json), [archived review](../conductor/tracks/python_two_consumers_20261108/review.md) |
| Workforce provider | [Workforce PR #305](https://github.com/edithatogo/microcosting_healthworkforce/pull/305), `8fa5882e2fda6cdba9ae93c46542c5b0b874c260` | Qualified source `c351a7c6420a356c4c13d2da3010bc7e7d0341f9` retained in the provider lock |
| Genomics provider | [Genomics PR #173](https://github.com/edithatogo/microcosting_genomics/pull/173), `b218f1464abb334fb60b3851af837325a238fa1a` | Qualified source `be2451f34a389f90e618cf37a5e8e1fcbb148dea` retained in the provider lock |

The four Dapane prerequisite tracks are archived in place, with their registry,
indices, metadata, implementation and evidence incorporated. The provider
repositories' receiving trees equal the qualified source trees: workforce
`5e28ad116994bb16ee2eacfddcb2d9bc2319eb0b`, genomics
`3417657a247d18d97c479cf3e799744a42cc81fb`. Pins remain on those qualified
revisions; a same-tree merge commit does not require rebuilding the genomics
development version, which embeds its source revision.

Accepted interval semantics remain the separate Rust/CLI envelope `0.1`, method
`dapane-intervals-v0.1.0`, with **half-even rounding per generated segment**.
[PR #15](https://github.com/edithatogo/dapane/pull/15) remains closed/unmerged and
its alternative preserved; [issue #19](https://github.com/edithatogo/dapane/issues/19)
records the resolution. Python's point/capacity API and run-bundle profile 0.1
are unchanged. Optional tracks retain their own acceptance criteria.

The provider scope is the selected QLD HP3.1 base-salary quotation release
`qld-health-hp3p1-reference-20261115` and manual DNA-extraction labour: 30 + 5
minutes per physical attempt, one to six specimens and explicit failures/retries.
Canonical/legacy entry points and the bounded historical calculator path remain
available. Separate locked Python 3.15.2 and 3.15.1 environments are required.
No whole-assay/workbook, empirical, clinical, co-installability or other-platform
claim follows. Original source HTML/workbooks are not redistributed in Dapane.

## Verified hosted baseline at d37575ec

| Workflow | Exact-source run | Observed result |
| --- | --- | --- |
| Release assurance | [43664411107](https://github.com/edithatogo/dapane/actions/runs/43664411107) | Passed all four candidates, supply-chain and matrix jobs; PR attestation skipped by design |
| Installed provider consumers | [43664411050](https://github.com/edithatogo/dapane/actions/runs/43664411050) | Passed; checkout `0dfbe37d3bf92c7bbf3fb717d28fedb443e8abdc` has the same tree as d37575ec |
| Runtime | [43664411087](https://github.com/edithatogo/dapane/actions/runs/43664411087) | Passed |
| Conductor validation | [43664411096](https://github.com/edithatogo/dapane/actions/runs/43664411096) | Passed |
| Privacy and secrets | [43664411082](https://github.com/edithatogo/dapane/actions/runs/43664411082) | Passed |
| CodeQL | [43664409923](https://github.com/edithatogo/dapane/actions/runs/43664409923) | Passed; aggregate check also passed |

Release job logs identify exact source `d37575ec` and CPython **3.12.16, 3.13.18,
3.14.10 and 3.15.2** on the declared Linux runner. Each passed **133 installed
tests**, ten scalar/capacity reference cases and two byte-identical clean builds.
Independent installed interval checks passed nine schema rejections, eleven
runtime rejections and fifteen tampered-report controls per target. The 3.15
benchmark and source-package legal inventory passed. Cargo-deny reported zero
errors/warnings across advisories, bans, licences and sources; pip-audit reported
no known vulnerabilities. Three dependency SBOMs and the build receipts were
retained by the run.

The standalone provider job built its own artifacts. Equal source trees establish
the same implementation, but do not establish identical wheel bytes. The new
release job therefore calls that existing verifier using the **same run's exact
CPython 3.15 CLI/wheel**, verifies the release receipt first, and makes aggregate
matrix success depend on the provider result. It retains the two provider pins
and environments. Manual workflow dispatch is absent, preserving the provider
owner's restriction against a manual branch path into default-branch caches.

## Distribution notice completion

[THIRD_PARTY_NOTICES.txt](../THIRD_PARTY_NOTICES.txt) and its
[machine-readable provenance](../release/distribution-notices.json) were generated
from all **36 checksum-verified Cargo.lock registry archives**. The generator
retains **74 upstream legal files**, four Rust supplemental files and **30 unique
full text payloads**, with every package/file attribution preserved when texts
are shared. Coverage includes licence alternatives, Unicode terms, the
target-lexicon LLVM exception and nested PyO3 runtime material. It deliberately
covers the whole locked graph, including build and target-specific packages,
without asserting exact linker inclusion.

The complete **84,098,960-byte** official Rust 1.99.1 compiler archive was streamed
and its SHA256 matched to the versioned official channel manifest before retaining
only its legal files. The [supplement record](../release/toolchain-notices.json)
gives the URLs, archive member names and individual digests. Archive SHA256:
`2ff05ff9c08a90861e7f6e4065b40a8b87463b4576186fd613871c3e37f2091f`.
Source revision: `58cf8f9c35b355199727627d07ae34a4e2846d67`.
The retained `COPYRIGHT-library.html` is the official full standard-library
inventory, not just the compiler's top-level MIT/Apache texts. This is not a
claim of complete compiler or operating-system library distribution coverage.

Generated notice SHA256:
`531a87c73c797f15dec96e8f4aed96288d8f386cd8fa11d6ff00769b68ddbc95`.
Generated provenance JSON SHA256:
`e16ee57d7590c80114a3fac8f1892fd104fb624d991c138ea7403f49bfa38e15`.
CI regenerates and compares the inventory from authenticated archives. Tests
reject corrupt/missing archives, substituted identities, unsafe archive members,
missing licence terms, tampered toolchain material and stale outputs.

LICENSE, NOTICE and the generated notice file accompany all nested crates,
candidate CLI bundles, wheels and the Python sdist. Release checks compare their
actual bytes. Dapane's project licence remains **Apache-2.0**. Python's optional
aggregate distribution expression is omitted under the
[documented PyPA metadata boundary](release-controls.md); no compound licence
is guessed from the conservative inventory.

## Hosted qualification at 5f03f28

The follow-up inspection at **04:26 UTC** verified source
[`5f03f28e3aa5a98c45c0853ce7498c86b181d66a`](https://github.com/edithatogo/dapane/commit/5f03f28e3aa5a98c45c0853ce7498c86b181d66a),
tree `191a295ee823297a3f517e7f584cf6023cbe4d40`. All ordinary hosted checks passed:

| Workflow | Run | Result |
| --- | --- | --- |
| Release assurance | [43676274010](https://github.com/edithatogo/dapane/actions/runs/43676274010) | All four candidates, supply-chain, exact-artifact providers and aggregate matrix passed |
| Runtime | [43676274053](https://github.com/edithatogo/dapane/actions/runs/43676274053) | 62 native tests, eleven tooling tests, four installed suites passed |
| Standalone providers | [43676274020](https://github.com/edithatogo/dapane/actions/runs/43676274020) | Passed |
| Conductor | [43676274022](https://github.com/edithatogo/dapane/actions/runs/43676274022) | Passed |
| Privacy and secrets | [43676274024](https://github.com/edithatogo/dapane/actions/runs/43676274024) | Passed |
| CodeQL | [43676271782](https://github.com/edithatogo/dapane/actions/runs/43676271782) | Actions, Python and Rust analyses and aggregate check passed |

Each of CPython **3.12.16, 3.13.18, 3.14.10 and 3.15.2** passed 133 installed tests,
ten independent scalar/capacity references, the installed interval rejection and
tamper controls, and two byte-identical clean builds. The runner was Linux x86_64,
glibc 2.39, Rust 1.99.1. The wheels' `manylinux_2_34_x86_64` tags do not extend
qualification beyond the executed Ubuntu runner. Receipts retain the 29-package
minimal native closure and zero Python runtime dependencies.

| Interpreter | Wheel SHA256 |
| --- | --- |
| 3.12.16 | `a2902e5d23422962523654a1c5d2015837a8e6ba509792bc833dbdf23ecc8201` |
| 3.13.18 | `aff83cc061a22c112f0b4f45970409a2ccb37e2b4aacfc83454a8f608b8fdaf7` |
| 3.14.10 | `1fa1ed1671d67331d396c3f8e430a8802f737a18e21928ea5d603d3c77dada4a` |
| 3.15.2 | `d4a1adbf74710dfcebb1ab1ac887901ae7fa489b7ecd6a4e8c02df0cfc206369` |

All four CLI payloads have SHA256
`2d3f3c5b54399a3613d4b6d97e8538cadc3074192fdd076f261118d1a67b03a2`.
Five downloaded artifact ZIPs matched their recorded archive digests, and all
100 recorded member checksums passed. Direct wheel/sdist inspection confirmed
Metadata 2.4, absence of both optional aggregate licence fields, three declared
legal files and exact legal bytes matching the CLI companions and archived source.
The source distribution and all three Cargo package inventories contain the legal
files. Full filenames, sizes, hashes and raw observations are in the JSON receipt.

The [release provider job](https://github.com/edithatogo/dapane/actions/runs/43676274010/job/132697595562)
downloaded candidate artifact **14145643783**, archive SHA256
`f52fcbccb909ee971ffde41c85b3ede54b903d01b430cd5fd332bd7013ea31f7`.
It verified the receipt before provider checkout, then passed workforce on Python
3.15.2 and genomics on 3.15.1 using the same CLI/wheel bytes, plus 133 native-boundary
tests. The aggregate matrix waited for this result. Runtime's merge checkout
`556fc6867a29ae1bf9acb6767dfd141844f3cc7c` has exactly the tested source tree.

Cargo-deny passed all four policy domains with zero errors/warnings against
RustSec revision `4ef2df8e806a65e2f1ecc14f56f51249062b23d6`; the Python audit
reported no known vulnerabilities in 36 resolved packages. Three CycloneDX SBOMs
were inspected and their hashes retained. This is a dated dependency observation.

The synthetic CLI benchmark ran three repeats at each scale. Median wall times
include process startup and JSON input/output:

| Usage rows | Valuation, seconds | Allocation, seconds |
| --- | --- | --- |
| 10 | 0.001442 | 0.001639 |
| 1,000 | 0.036719 | 0.049538 |
| 5,000 | 0.203711 | 0.317516 |

Peak child RSS across the complete run was **86,384 KiB**. This is not per-workload
memory or a cross-host/provider performance claim. The raw timings, CPU measures,
input/output sizes and output digests remain in the JSON receipt. Artifact storage
has 30-day retention; the receipt preserves identities and results, not the binary
bytes. Retain artifacts beyond that window before publication or any consolidation
that depends on recovery.

## Review, remaining execution and owner choices

Local verification of this increment passed **64 release-control tests**, Ruff
lint/format, notice regeneration and focused workflow syntax checks. The earlier
five release findings and integration null-state fix remain covered. Independent
notice-generator and integration reviews found no material defect. The integration
review independently checked pinned Maturin 1.16.0 metadata behaviour and the
exact-artifact provider dependency. Conductor consistency passed with 14 tracks,
12 requirements, 155 tasks and 557 local links; two workflows, 23 Bash blocks
and three embedded Python blocks parsed. The local Rust executable is
unavailable, so no fresh native artifact result is inferred from these controls.
At initial publication the changed notices, packaging and reusable-provider path
required new hosted results. The completed 5f03f28 run above supplies those results.
PR #17 retains subsequent exact-head status; the
older [local qualification](release-verification-2026-11-15.md) and
[initial integration record](release-integration-2026-11-15.md) remain historical.

At the initial baseline, the centrally managed offline security runs
[43664411263](https://github.com/edithatogo/dapane/actions/runs/43664411263) and
[43664409752](https://github.com/edithatogo/dapane/actions/runs/43664409752) are
**queued and unexecuted** at inspection. Their jobs request
`self-hosted`, `linux`, `x64`, `ai-security-offline`; runner ID is zero and no
runner is assigned. No scanner outcome exists. The caller still pins reusable
workflow `36362fa872e4ce747266a6e795fcefa3dd343f67`; its central documented profile
requires pre-provisioned infrastructure. No gate was disabled or waiver inferred
from branch metadata, and no runner was provisioned. Runner execution remains an
external blocker before treating PR #17 as fully qualified. On 5f03f28 the current
[PR run 43676274294](https://github.com/edithatogo/dapane/actions/runs/43676274294)
and [push run 43676270592](https://github.com/edithatogo/dapane/actions/runs/43676270592)
also remain queued with no execution result. Successful ordinary checks do not
replace that result. PR attestation was correctly skipped because the event is
ineligible; trusted-main provenance still follows successful main qualification.

Publication remains disabled: the owner still needs to choose the first channels
and controlling accounts/organisations. Candidate names do not reserve names or
prove registry authority. Apache project licensing and the selected provider
qualification are resolved; no further licence choice is requested. Successful
trusted-main attestation follows eligible main-branch qualification. No package
publication, release tag, legacy API removal or external repository archive was
performed. The release track's archival is already authorised and remains held
until its mandatory acceptance evidence is complete.
