# Execution and review evidence

Implementation date: **15 November 2026** (Australia/Brisbane).

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
registry and real-consumer gaps. The candidate work keeps them open. The current
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

The execution workspace became unavailable before code-level local execution.
No native build, Python test or lint result is claimed from that environment.
The implementation is being checked on hosted GitHub Actions against its exact
branch head; this record will be updated with the resulting run and outcomes.

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

Configuring these commands is not execution evidence. Failed-run artifacts, if
retained, record failures and do not qualify a candidate.

## Closure boundary

Public package publication remains disabled. No registry identity, Dapane project
licence, real workforce/genomics migration or external repository archival is
asserted. The consolidation review selected no external archive and copied no
restricted provider assets.

The user requested review, fixes and archival. Review/fixes can be performed on
the candidate assurance implementation now. The original track's archival must
wait for its outstanding mandatory release acceptance evidence.
