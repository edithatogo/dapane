# Release assurance controls

Status: implemented candidate workflow; execution results belong to the exact
checked commit and its retained artifacts. Configuring these checks does not
qualify a public package release, a real provider migration or a repository
archive. Dapane project material is Apache-2.0; registry identities remain unresolved.

The [capability manifest](../release/capabilities.json) selects the first bounded
candidate. The [release track](../conductor/tracks/release_consolidation_20261108/index.md)
retains the wider acceptance criteria and outstanding prerequisites.

## Source and artifact identity

[Release assurance](../.github/workflows/release-assurance.yml) checks out the
explicit pull-request head or push commit. Candidate reports therefore identify
the tested source revision, rather than depending on GitHub's implicit
pull-request merge checkout. Existing Runtime, Conductor and privacy checks
remain separate.

Each Linux x86_64 job:

1. Installs the existing Rust 1.99.1 toolchain and pinned Python build tools.
2. Builds the CLI and interpreter-specific wheel twice into fresh target
   directories, with a fixed source commit timestamp, remapped build paths and
   incremental compilation disabled.
3. Compares artifact names and complete SHA256 digests. A mismatch fails the job.
4. Installs those exact bytes into a new consumer location, installs the wheel
   with `--no-deps --no-index`, then records native module ownership and checks
   the supplied wheel against its installed files.
5. Exercises independent synthetic references through the installed CLI and
   Python package from outside the checkout. The existing installed-wheel suite
   supplies additional negative and capacity-profile coverage.
6. Retains the source archive, source commit/tree, Cargo lockfile, toolchain,
   build package versions, artifact digests, replay results and comparison report.

The CPython matrix is **3.15.1 on ubuntu-24.04 x86_64**.
Actual patch versions and host details are captured by each receipt. A successful
receipt for one interpreter does not qualify another. The aggregation job requires
a receipt for every declared target on the same checked source and rejects missing or duplicate
targets. Wheel tags alone do not establish manylinux, other Linux distributions,
Windows, macOS, ARM, ABI3, PyPy or free-threaded support.

The comparison establishes repeatability within one recorded runner environment.
The Ubuntu runner image and interpreter patch releases are not immutable build
images; byte identity across machines or future runner revisions is not asserted.
A future public release needs a retained build environment or separately
qualified reproducibility evidence. Preserve the exact archived artifacts and
source inputs for recovery, as described in [compatibility](compatibility.md).

GitHub artifact downloads may normalize executable modes. Install a downloaded
CLI with `install -m 755 dapane /absolute/prefix/bin/dapane` after validating its
SHA256 digest; do not treat mode changes as changed binary contents.

## Dependency and source controls

[deny.toml](../deny.toml) applies to the Linux runtime dependency graph. The job
runs cargo-deny **0.20.2** against the locked workspace and records its complete
diagnostics, exit status and the actual RustSec advisory-database commit. The
policy rejects known advisories, yanked crates, duplicate crate versions,
unqualified registry/Git sources and licences outside the explicit allowlist.
It has no advisory ignore entries.

Dapane project material is Apache-2.0 by the owner's explicit decision. Workspace
packages and their third-party dependencies all undergo licence checking; there is
no private-workspace exemption. Each nested crate carries ordinary copies of
LICENSE, NOTICE and THIRD_PARTY_NOTICES.txt. Wheel payloads and CLI bundle companions
must match those root files. The 3.15 candidate also checks Cargo package file lists
and the actual Python source distribution, including its legal metadata and bytes.
Keeping `publish = false` does not exempt a
package from licence checking or claim verified registry ownership.

[The notice generator](../scripts/distribution_notices.py) reads all 36 locked
registry archives after checking each archive against Cargo.lock. It collects
the upstream licence, copyright, attribution and exception files, including nested
runtime material. It reads the authenticated archives directly. The generated
[inventory](../release/distribution-notices.json) retains each package, source
checksum, legal-file identity and shared-text reference. The
[Rust supplement](../release/toolchain-notices.json) records the official 1.99.1
compiler-archive checksum and its complete standard-library copyright inventory.
The acquisition and coverage limits are in the [handoff record](release-handoff-2026-11-15.md).

Run `cargo fetch --locked`, then
`python scripts/distribution_notices.py --check` to reject stale or substituted
notices. Use `--write` only when deliberately regenerating reviewed inputs, then
copy the resulting root notice file into each workspace crate. The conservative
inventory includes build/procedural-macro/target-specific packages; it is not a
claim that every listed dependency is linked into every artifact. Full upstream
licence alternatives and exceptions are retained without selecting a new project
licence or asserting complete operating-system/compiler distribution coverage.

Python's optional `License-Expression` describes the containing distribution.
The [PyPA core metadata specification](https://packaging.python.org/en/latest/specifications/core-metadata/#license-expression)
and [pyproject specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/#license)
distinguish it from project licensing. This candidate omits the optional expression
and the legacy `License` field instead of inferring an aggregate expression from
the conservative notice inventory. The project remains Apache-2.0 in LICENSE,
NOTICE, Cargo, citation metadata and the capability manifest. `license-files`
declares all three legal files. `license` is not dynamic: the pinned
[Maturin 1.16.0 metadata implementation](https://github.com/PyO3/maturin/blob/v1.16.0/src/metadata.rs)
clears an undeclared, non-dynamic field rather than inheriting Cargo's project
licence. Wheel and sdist checks enforce the actual emitted metadata. Any future
aggregate expression requires an artifact-specific review of bundled contents.

The Python distribution declares no runtime dependencies. Separately, pip-audit
**2.10.1** audits the resolved build and assurance requirements with strict
dependency collection. Its JSON response records the resolved packages and
reported findings. That response is a dated observation of the advisory service,
not an immutable copy of the service's entire database. Candidate build-package
and assurance-tool inventories are retained separately from runtime dependencies.

Cargo metadata and `cargo tree` retain package licences, dependency identities,
features and duplicate-version evidence. cargo-cyclonedx **0.5.10** generates a
CycloneDX **1.6** SBOM for each workspace crate and the declared Linux target.
The SBOM generation runs offline after locked dependency resolution, followed
by a check that Cargo.lock is unchanged. These SBOMs include Rust dependencies;
they do not assert coverage of every operating-system library or the complete
compiler supply chain.

All runtime fixtures remain synthetic. Passing dependency checks cannot establish
rights to redistribute a provider's quotations, workbooks, research data or
other embedded sources. Those source decisions remain separately recorded
release prerequisites.

## Performance and minimal installation

The CLI builds with `--no-default-features`, and the enabled core/CLI dependency
tree is retained. Installed Python evidence is collected before test tooling is
added to the clean environment. This distinguishes the zero-runtime-dependency
consumer from the development environment.

The CPython 3.15 job runs the existing synthetic valuation and allocation
benchmark at **10, 1,000 and 5,000** usage rows, three times each. Reports contain
wall/CPU measurements, input/output sizes and independently checked totals.
The Linux `ru_maxrss` measurement is peak child RSS across the whole benchmark;
it is not per-workload memory. Single-runner measurements establish no general
speedup, cross-machine performance, concurrency, real-provider or empirical
economic validity.

## Permissions, provenance and retention

PR, candidate, matrix and supply-chain jobs use read-only repository permissions,
disabled persisted checkout credentials and immutable action references. The
existing privacy/secret workflow is unchanged. No self-hosted runner or secret
is required by this workflow.

A separate job attests candidate bytes only after the complete matrix, exact-artifact
provider check and supply-chain jobs pass on a **push to this repository's main branch**. It downloads
the successful jobs' artifacts and generates signed build provenance using
`actions/attest` with explicit subject paths. Only that job receives
`id-token: write` and `attestations: write`; it has no package or contents write
permission. Storage records and registry pushes are disabled. PRs do not receive
these attestation permissions. Release/provider workflows accept pull requests
and pushes to main; their reusable call cannot restore a manual branch-trigger
path into provider execution or its default-branch caches.

The separate, centrally managed [offline security caller](../.github/workflows/offline-ai-security.yml)
retains its existing pinned reusable workflow and policy. Main requires a
`self-hosted`, `linux`, `x64` runner with the `ai-security-offline` label.
Pull requests select the dedicated `ai-security-offline-dapane-pr-<number>`
label. The capability manifest and candidate receipts identify the requirement
for executed scan evidence on the exact release source. The hosted release
workflow verifies that the requirement appears in each receipt.

A signed build statement binds bytes to a build. It is not a statement that the
provider has migrated, an economic method has been validated or
a package published. Verify a downloaded subject offline with the GitHub CLI using the
`candidate-provenance` bundle (`attestation.json`), expected repository,
workflow and source revision, and compare it to its receipt.
Set `DAPANE_EXPECTED_SOURCE_SHA` to the reviewed main-branch commit first:

```sh
gh attestation verify /absolute/path/to/artifact \
  --bundle /absolute/path/to/attestation.json \
  --repo edithatogo/dapane \
  --signer-workflow edithatogo/dapane/.github/workflows/release-assurance.yml \
  --source-ref refs/heads/main \
  --source-digest "${DAPANE_EXPECTED_SOURCE_SHA:?set the reviewed source commit}" \
  --deny-self-hosted-runners
```

The workflow retains candidate, supply-chain and signed-provenance artifacts for
**30 days**, including diagnostic artifacts from unsuccessful runs. A failed run's
uploaded files are evidence of the failure; they are not a qualified candidate.
Before a release or a recovery-dependent consolidation decision, preserve the
qualified artifacts beyond that temporary retention window.

The workflow has no registry-publication job. Publication still requires the
manifest's explicit licence, identity, source-rights, provider and capability
gates. Optional integrations do not become mandatory first-release dependencies.

## Portfolio alignment and primary references

The applicable portfolio baseline was inspected at
[repository-standards e195af3](https://github.com/edithatogo/repository-standards/tree/e195af3b0f46db74e797c5bf2e177b7882085186),
including its
[supply-chain workflow](https://github.com/edithatogo/repository-standards/blob/e195af3b0f46db74e797c5bf2e177b7882085186/.github/workflows/supply-chain-evidence.yml)
and
[Rust dependency selection standard](https://github.com/edithatogo/repository-standards/blob/e195af3b0f46db74e797c5bf2e177b7882085186/docs/rust-dependency-selection-standard.md).
Dapane applies those artifact, SBOM, checksum, provenance, scoped-permission and
dependency-evidence controls to its actual installed artifacts. It retains its
existing toolchain and numerical dependency choices.

Pins and interfaces were checked against these primary sources on 15 November 2026:

- [cargo-deny 0.20.2 release](https://github.com/EmbarkStudios/cargo-deny/releases/tag/0.20.2),
  [configuration](https://github.com/EmbarkStudios/cargo-deny/blob/0.20.2/deny.template.toml)
  and [advisory options](https://github.com/EmbarkStudios/cargo-deny/blob/0.20.2/docs/src/checks/advisories/cfg.md).
- [cargo-cyclonedx 0.5.10 release](https://github.com/CycloneDX/cyclonedx-rust-cargo/releases/tag/cargo-cyclonedx-0.5.10)
  and [version-specific CLI](https://github.com/CycloneDX/cyclonedx-rust-cargo/blob/cargo-cyclonedx-0.5.10/cargo-cyclonedx/src/cli.rs).
- [pip-audit 2.10.1](https://github.com/pypa/pip-audit/blob/v2.10.1/README.md).
- [upload-artifact v7.0.2](https://github.com/actions/upload-artifact/tree/cf430e030ddbb5b0abf93d22962f4752f3646cd9)
  and [download-artifact v8.0.2](https://github.com/actions/download-artifact/tree/9000827ccba6bdab643e8b6fd33ac0654aef8333).
- [actions/attest v4.2.2](https://github.com/actions/attest/blob/1e69f48acb82d1966a394da916b4c1698aa569d6/README.md)
  and the [GitHub CLI verification options](https://cli.github.com/manual/gh_attestation_verify).
