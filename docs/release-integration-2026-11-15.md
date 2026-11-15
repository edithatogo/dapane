# Release integration and Apache-2.0 adoption — 15 November 2026

## Decision and source boundary

The project owner instructed this integration to use Apache 2.0. The canonical
[Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0.txt) is
retained in [LICENSE](../LICENSE), SHA256
`cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`.
[NOTICE](../NOTICE) retains project attribution. Rust workspace/crate manifests,
Python packaging and citation metadata declare `Apache-2.0`.

Ordinary licence and notice copies accompany each nested Rust crate. Python
packaging declares both files through PEP 639. Release checks reject inconsistent
metadata, changed crate copies, incomplete wheel notices and substituted licence
payloads. The source-package check inspects Cargo package file lists and the
Python source distribution. Workspace crates now participate in dependency licence
checks; unpublished status no longer exempts them.

This resolves Dapane's project-licence decision. Dependencies and separately
obtained provider assets retain their own licences and attribution obligations.
No external provider source asset is included. Accepted SPDX expressions do not
by themselves establish that every third-party binary distribution notice is present.
Registry publication remains disabled.

## Incorporated archived tracks

The audit inspected main
[`c70edf65a119d9ffda410cd4e5325e1f37e9332a`](https://github.com/edithatogo/dapane/commit/c70edf65a119d9ffda410cd4e5325e1f37e9332a)
and merged that accepted history into the existing release branch. Its archive
catalogue, registry, track indices and metadata agree on exactly two archives:

| Track | Implementation integration | Archive integration | Source verification |
| --- | --- | --- | --- |
| Core contracts | [PR #9](https://github.com/edithatogo/dapane/pull/9), `224cf91dbcf513feaa022b2cf5aa310a965472ce` | [PR #18](https://github.com/edithatogo/dapane/pull/18), `c70edf65a119d9ffda410cd4e5325e1f37e9332a` | Implementation is an ancestor of main; bundle schema, verifier, reference cases and substantive tests match the merged implementation. All nine archive-closeout files match the inspected main. |
| Rust kernel | [PR #16](https://github.com/edithatogo/dapane/pull/16), `172d0ef39291a936a35c6e221eb467701ccefbba` | Included in PR #16 | Implementation is an ancestor of main. 51 of 53 integrated files match byte for byte; the shared registry and archive catalogue alone changed afterwards. Native code, schemas, tests and evidence are retained. |

Both archives retain their original acceptance evidence. The optional Arrow/Parquet
kernel task remains expressly deferred; no optional integration is promoted by
this release work. The historical evidence's licence observations remain tied to
their original source, before the present Apache-2.0 decision.

The accepted interval API is the separate Rust/CLI envelope `0.1`, method
`dapane-intervals-v0.1.0`, with half-even rounding per generated segment. The
superseded [PR #15](https://github.com/edithatogo/dapane/pull/15) is closed and
unmerged; its once-per-parent alternative is not silently integrated. Python's
public point/capacity API is unchanged. Run-bundle profile 0.1 and its independent
repository verifier are preserved.

At the audit, setup was **completed** on main. Its archive and additional lifecycle
checks remained in open [PR #14](https://github.com/edithatogo/dapane/pull/14), head
`0649a044b2e9eac051a77c139ed3b5d618130ac0`. Those changes must not be described as
incorporated until that PR passes its applicable checks and merges. The provider
track in [PR #13](https://github.com/edithatogo/dapane/pull/13) remains separately
owned and in progress.

## Qualification and actual CI correction

The [earlier local qualification](release-verification-2026-11-15.md) belongs to
source `354df1fd47fabcf8f2f571ac51566ad03d9cd3e4`. Current main adds native interval
and bundle work, and licensing changes package contents. The earlier wheel hashes
and 74-test results are not qualifications of this integrated source.

At release head `74986ec23b4f97732dc10c62857421f1e5503134`, hosted Conductor,
Privacy, Runtime and CodeQL passed. Release assurance's 3.14 build failed before
compilation while rustup tried to add repository-required components after a
minimal install: a `cargo-fmt` conflict. The corrected release workflow explicitly
installs `rustfmt` and `clippy` with pinned Rust 1.99.1, matching the established
Runtime workflow. The compiler, dependency lock and acceptance gates are preserved.

The integrated candidate additionally runs the independent interval verifier
against the installed CLI and retains its log. Installed Python tests include the
accepted bundle/reference regressions. The manifest limits each additional profile
to its actual interfaces.

Before publishing this integration commit, the 36 release-control tests, manifest
validation, static kernel inventory and Conductor consistency check passed locally.
The available local Rust executable was no longer present; no new native build or
installed artifact result is inferred. Fresh hosted execution must qualify this
source, including licence payloads, all four interpreters and the complete current
suites. Independent integration review identified and fixed a null-state filtering
case: an unknown registry/provider status must remain a publication blocker. A
regression covers all three unresolved fields. Trusted-main attestation runs only after successful qualification on main.

## Remaining publication decisions and work

The owner still needs to select the first publication channels and the registry
accounts/organisations that will control the package names. Candidate package names
are `dapane` for Python and `dapane-core`/`dapane-cli`/`dapane-python` for Rust;
configuration does not reserve a registry name or establish publishing authority.

Real workforce/genomics qualification and historical migration/recovery evidence
remain with the existing Python-consumer track. Complete distributed dependency
notices and exact-source hosted results remain implementation/qualification work.
They are not additional licence-choice questions. External provider assets remain
excluded unless separately selected and qualified.

The release track retains **blocked** status until its mandatory acceptance evidence
is complete. Its requested archival is already authorised. No external repository
archive, legacy API removal or public registry publication is part of this integration.
