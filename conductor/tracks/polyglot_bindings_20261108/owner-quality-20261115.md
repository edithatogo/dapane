# Polyglot owner quality follow-up — 15 November 2026

## Outcome and source

The bounded owner correction is `988e41158a17d6613006b9bffe59cd59a3aa9cca` (tree
`757c1ee74d575ed0e21d9f6e11b99dad72b11053`), a fast-forward from the
received integrator head `8716c423f15c6449940df902fbabfab870d38f4d`. Only the owned binding
namespace and this track change. All shared integration commits are preserved.
The [structured receipt](owner-quality-20261115.json) retains actual commands,
outputs, source identities, artifact hashes, failed observations and focused review.

The [sole-integrator intake](https://github.com/edithatogo/dapane/blob/497cd6472b1eb282ea6bd79271a7c76a881e9cec/conductor/roadmap-intake-2026-11-15.md) accepts `bindings/polyglot/`,
reconciles the blocked registry state, and supplies standalone installed/native CI.
These requests are completed; the earlier handoff is retained as history.
The PR remains draft and this track remains blocked on its unmet requirements.
Julia is outside this repair.

## Findings and fixes

| Finding reproduced on received head | Owner correction | Preserved contract |
| --- | --- | --- |
| ABI Clippy exited 101: group `all` and the explicit unsafe lint shared priority 0 | Set `all = { level = "warn", priority = -1 }` | Both unsafe denies and `-D warnings` remain; no lint is allowed or suppressed |
| Ruff 0.17.4 formatting exited 1 for two files | Format `stage_r.py` and `tests/prepare_cases.py` using the pinned tool | Parsed Python ASTs are identical before and after; fixture assertions and subprocess arguments are preserved |

The focused review used source/AST/TOML comparisons independently of test results.
It found no additional defect in this bounded diff; all 49 prepared fixture files
also match the received hosted inventory. This is a separate author
review, not an independent release or unsafe-boundary sign-off. Rust/C/R runtime
source, headers, package locks, fixtures, the original qualification shell script,
and all shared CI/registry/core objects are unchanged.

## Executed evidence

The integrator's received-head hosted run already passed 1 R Rust test, 5 ABI
Rust tests, 4 packaging tests, 24 installed R cases, host rejection/GC/two R
interpreters, and 24 native C cases plus 400 threaded calls. Its workflow failed
on the two owner quality findings above; no failed run is relabelled as passed.

On the clean published correction source above, the local run passed:

- Ruff lint and format; both standalone Rust format checks; ABI Clippy with warnings denied.
- Five ABI Rust tests, four packaging tests and locked/offline CLI/ABI release builds.
- All 24 synthetic reference/parity cases and the ordinary native C consumer, including lifecycle/bounds and 400 threaded calls.
- Conductor validation and all 12 lifecycle regressions; unchanged source after execution.

The local host was Debian 13 Linux x86_64, Rust 1.99.1 and Ruff 0.17.4;
exact compiler/Python versions are retained in the receipt. R is not installed
in this local executor; installed R acceptance is obtained through shared hosted CI.

### Sanitizer boundary

The first local C consumer was compiled with ASan/UBSan and invoked with
`ASAN_OPTIONS=detect_leaks=1:halt_on_error=1` and `UBSAN_OPTIONS=halt_on_error=1`.
It exited 1: LeakSanitizer reported that it cannot run under ptrace. That failed
observation is retained, tied to local commit
`26325a08f7d14fa24a60e486bfabbf53f16932ff`, whose tree equals the published
correction tree. It is not converted to a pass. A separately compiled ordinary
consumer passed on the published source; it establishes functional native
acceptance only. Shared sanitizer flags and gates are unchanged.

The local library hash belongs to this local build only. The canonical hosted
C-qualified library has its own hash; no binary identity is inferred from equal
source, a passing source build or a successful ordinary consumer.

### Hosted correction and final-head evidence

[Correction run 43693257570](https://github.com/edithatogo/dapane/actions/runs/43693257570)
passed all 41 binding commands, including both Clippy/format checks, 1 R Rust
test, 5 ABI tests, 4 packaging tests, clean installed R acceptance over 24 cases,
host rejection/GC/two interpreters, and C acceptance over 24 cases plus 400
threaded calls. The C consumer ran successfully with ASan/UBSan and leak
detection enabled. Its Rust library is not sanitizer-instrumented.

The downloaded artifact's archive digest, all 228 source-file hashes and all
103 retained artifact/log entries were verified. All 49 prepared case files
also match the received integrator receipt byte-for-byte. The
raw hosted qualification JSON is retained in the GitHub Actions run artifact (omitted from Git because its `.github/workflows/privacy-secrets.yml` SHA-256 entry triggers Gitleaks `generic-api-key` in commit-range scans);
the structured owner receipt retains selected command logs and artifact identity.

| Correction artifact | SHA-256 |
| --- | --- |
| C-qualified `libdapane_abi.so` (1,673,400 bytes) | `365d837305783862f1dda8078d14a531486f4931414bf2f291a314a2ef9f362e` |
| Installed `dapaneR.so` | `f7f86c1d9a9b379eb7b710d6a5277bec04d367123ddbc02db27bd46b064f274b` |
| R source package | `286f322be73c84d32a6561dbb43fe0ff34c441beae8ca0c767bcc52ab6e12358` |

Hosted artifact 14152499497 retains these bytes; its recorded retention ends
2026-12-15. The ABI library digest matches the received integrator's artifact
digest by measurement, not by an assumption that rebuilding preserves identity.
The integrator still owns acceptance of these bytes and the remaining requirements.

Shared controls and discovery passed; aggregate was queued when this document was
prepared. The final documentation head and its separately executed hosted results
will be pinned in the existing PR #26 owner handoff comment and PR #20 intake
comment. Earlier source results are not relabelled as final-head outcomes.

## Remaining integrator requirements

1. Accept the new exact-source hosted receipt and the exact native library bytes
   used by its C consumer. Preserve the artifact identity; a rebuilt or expired
   artifact needs new qualification rather than inheritance of an old checksum.
2. Retain separate unsafe-boundary review and optional-manifest advisory,
   SBOM/notices and staged legal-payload requirements. C-side ASan/UBSan does not
   instrument the Rust library.
3. Required offline security remains a gate. Coordination PR #20's separately
   retained privacy findings are not cleared by this lane's privacy result.
4. The original `qualify.sh` has not been executed as a whole. Shared CI runs its
   documented stages independently, with explicit Python quality checks.
5. Other hosts, Julia/JLL artifact resolution, Julia GC/lifetime tests and any
   release remain unqualified. Julia must use accepted C-qualified library bytes
   and remains outside this repair regardless of this workflow's result.

No shared source change is requested for the two quality corrections. The owner
hands the remaining acceptance and shared accounting back to the sole integrator.
No merge, publication, new worker or infrastructure/credential change occurred.
