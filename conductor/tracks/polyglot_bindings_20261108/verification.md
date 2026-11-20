# Polyglot verification record — 15 November 2026

## Current owner follow-up

The [distribution review](distribution-review.md) records the completed macOS
arm64 R source package and Julia archive reinstallation.

The [current quality/acceptance handoff](owner-quality-20261115.md) and
[structured evidence](owner-quality-20261115.json) supersede the original pending
replay, namespace, registry and standalone-CI requests below. The integrator
executed installed R/native C acceptance on its exact received source; this owner
corrected the two quality findings without changing runtime semantics. Julia,
separate unsafe-boundary acceptance and optional legal/security/release obligations
remain open. Final-head results are pinned in the existing PR #26 / PR #20 owner
comments rather than assigned to an earlier source.

## Historical recovery handoff — retained

## Evidence boundary

**The published candidate is not qualified.** The ordinary execution environment
disconnected before the native C consumer could run and then reported no usable
environment. No existing remote execution device was connected. The original
checkout, native artifacts and complete on-disk logs could not be recovered in
this turn. No new execution infrastructure, credentials or worker was created.

Source was preserved through the GitHub connector from the submitted edit text.
The two lane lockfiles were reconstructed from the unchanged main lock and the
exact seven additional package records observed during the completed R build.
Checksums were reread from the official crates.io index. This is a recovery
procedure, not proof that the final files are byte-identical to the inaccessible
tested worktree. New source-bound qualification is mandatory.

The original local R checkpoint was
`efbe2a310de4ba1f223649bcd094462a05e2222f`. It was not pushed and is not a remote
acceptance SHA. R install tests preceded subsequent provenance/documentation
edits in that checkpoint. If the checkout becomes accessible, retain that history
and compare it; do not reset or discard it as part of integration.

## Inspected source and ownership

| Surface | Exact inspected revision |
| --- | --- |
| Main and unchanged core | `e34f87c9df39a2132fecee142431cdeefb732471` |
| Main tree | `c07a6b2589b9d665f619f5d977d66e513180bab4` |
| Release owner PR #17 | `a4ddde7ae7a799e37a5d594cde9c195ff057bc5e` |
| Later coordination PR #20 | `e615454c9f3f41f96e9e310f446d2440d98cf5eb` |
| rextendr registration/notice source | `d7383605ebdc766ddc46e9b73ff2b34bf6c19565` |

Live main/open PRs/branches were checked before implementation and refreshed before
submission. No competing polyglot branch or PR was present. This lane selected
`bindings/polyglot/` before observing PR #20's alternate reservations. The path
claim is part of the integrator request.

## Executed before interruption

These are observed command results from the worktree based on the pinned main,
not rerun results for the published recovery commit.

| Check | Observed result |
| --- | --- |
| Root CLI release build, locked/offline | Passed |
| R wrapper Rust unit test | 1 passed: injected pure-Rust panic returns structured internal error |
| R rustfmt and Clippy with warnings denied | Passed |
| Shared case preparation | 24 cases; independent baseline and added exact-value/interval assertions passed |
| Vendored R source staging | Passed; original core source bytes compared with staged bytes |
| R CMD build | Source package built |
| R CMD INSTALL --preclean into isolated library | Passed, including loading from temporary and final install locations |
| Installed R acceptance | 24 cases, host rejection, GC stress, two independent R interpreter processes passed |
| Packaging unit tests | 3 passed |
| ABI Rust unit tests | 5 passed |
| ABI locked/offline release build | Passed |

Retained tool-output excerpts:

```text
24 shared cases; host rejection, GC and two interpreter checks passed
test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
Ran 3 tests ... OK
test result: ok. 5 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```

The R acceptance environment was Debian 13 Linux x86_64. R reported
`R version 4.5.0 (2025-04-11)`; the selected Rust toolchain directory was
`1.99.1-x86_64-unknown-linux-gnu`. extendr-api/ffi/macros were 0.9.0.
R was extracted into an isolated temporary tool directory; no system installation
or global configuration change was made. The downloaded Debian
`r-base-core_4.5.0-3_amd64.deb` was 28,626,144 bytes, SHA256
`6c529a906d2a26cf78e6c24eaa96e0bbd061b032e6c824f9a61e5f313353b155`.
That is a tool-runtime identity, not a Dapane artifact checksum.

### Cases and what they prove

Five original fixtures check their hand-calculated projections, including newborn
total 150.00 and infant views 60.00/90.00. Added explicit examples cover
9007199254740993 without a float conversion, an exact 1/3, zero and Unicode.
Five existing capacity fixtures compare full CLI reports, including unknown
capacity/use states; no new independent capacity arithmetic is claimed.

Two interval cases check total 110.00 at a rate boundary and the accepted
per-generated-segment rule: two exact 0.005 segments round to 0.00 + 0.00, while
the exact sum remains 0.01. Eight invalid cases retain core diagnostics for
floating/null/missing quantities, unknown fields/version, 0.1 capacity fields,
duplicate JSON keys and malformed JSON.

All 24 full result/error JSON payloads are compared between installed R and the
Rust CLI. These are regression parity oracles; they are distinct from the
independent numerical projection assertions. R-specific cases reject NA, NULL,
empty/multiple strings, numeric/logical/list/factor/raw inputs, invalid UTF-8 and
oversized input. GC stress retains results after original inputs are released;
two PSOCK processes exercise separate R main threads. No foreign-thread R API
support is claimed.

The ABI unit tests cover the common panic guard, retained storage reclamation,
non-reused/stale handles, count/byte saturation, and identifier exhaustion. They
do not replace an actual C consumer or Julia lifetime/artifact tests.

## Not executed or not retained

- Native C acceptance and its sanitizer run: the execution request failed before
  a usable process could be created. The authored consumer includes null, length,
  version, UTF-8, short-buffer sentinel, stale/free, count-limit and 400 threaded
  calls, but none are claimed passed.
- ABI Clippy/rustfmt: no result was obtained from that interrupted command.
- The final recovered source, new source-recursion guard/regression and the new
  all-in-one qualification script have not been run.
- Julia implementation, installed Julia package, GC preservation and artifact/JLL
  resolution remain pending. A runtime download was started but no completion
  result was received; it establishes no host qualification.
- No Dapane source-tarball/shared-library digests were retained before interruption.
  Do not derive or invent them from a successful build message.
- No new dependency advisory, licence aggregate, release, offline-security or
  other-platform result is supplied by this lane.
- Final Conductor validation needs the integrator's registry reconciliation. The
  branch changes track status to blocked while main's row remains new; the
  consistency requirement is preserved, not waived.

## Review and recovery changes

The local packaging tests verified workspace-inheritance resolution, shared
dependency pin preservation and refusal to overwrite existing output. Review
then found that a new staging directory inside the source tree could recurse.
Recovery adds a resolved-path rejection and a fourth test; both require execution.

The handle documentation now says unknown/stale identifiers fail, and explicitly
limits identity to one loaded library instance. Handles from different instances
can have the same integer, so no foreign-library identity guarantee is asserted.
Whitespace was normalized during recovery; the optional Python packaging test's
unused import was removed. ABI unsafe operations retain explicit caller
preconditions and safety comments; the core's unsafe prohibition is unchanged.

Reconstruction made the earlier local checks insufficient for final-source
acceptance. B2.3/B3.2 therefore remain blocked, and the PR remains draft.
The next concrete execution is:

```sh
bash bindings/polyglot/qualify.sh /absolute/new-qualification
```

Retain its exact source SHA, tool versions, log, exported symbols and artifact
checksums. Fix real failures without suppressing tests or changing shared
numerics. Only after the C consumer passes may the same lane implement Julia.

## Hosted documentation check after publication

At documentation head `5eb2e0408ace4586d2f7441b5c1bec5faeabe10d`,
[Conductor run 43681333801](https://github.com/edithatogo/dapane/actions/runs/43681333801)
failed with three reported errors: the expected registry/status mismatch and two
relative links inside the proposed registry diff in `handoff.md`. The checker
also inspects fenced text. The latter two were lane-owned documentation defects;
the handoff now gives a column-by-column row edit without those context-dependent
links. This correction does not change binding source or waive the remaining
registry mismatch. Its own exact-head hosted outcome is recorded in the PR.

## macOS host and ABI review

On 20 November 2026 the Dapane integration reviewer examined the Rust ABI and C header at Dapane `593013d7dc2f44a91ff4ee63f60feed3436e347c` (ABI tree `3fcc47cf1e58cd6dc4df859cfeff262886c05370`). The implementation was received from the earlier bindings lane at `9904252`. This is a separate source review of ABI v1 for callers that satisfy the documented pointer and library-lifetime contract.

The review followed all five exported functions. The version query touches no caller memory. Evaluation checks the operation and length bound before borrowing input, keeps the borrow within the call and publishes the integer handle only after successful insertion. Both success and kernel errors use the same owned result lifecycle. Length and copy initialize the return count and hold the registry lock through access. A short buffer receives the required length without a partial copy. Free removes the entry under that lock. Checked, monotonic identifiers and bounded total retained bytes prevent reuse and wraparound. Each path that can panic is guarded, and the build requires unwinding support. Callers must provide valid, disjoint, exclusively writable outputs. The header and Rust safety comments now state this for concurrent callers.

Warnings-denied Clippy and all five ABI tests passed. The macOS arm64 C consumer, compiled with AddressSanitizer and UBSan, passed 24 parity cases, lifecycle checks and 400 concurrent native calls. Sanitizers instrumented the C caller. The release dynamic library SHA-256 was `230792ee8c18098252cf60550b686385e124b9343d393c492b5bdb9d46d4bd40`.

The separately installed Homebrew R 4.6.2 met the package requirement. The staged locked source built and installed into an empty R library. The 24 shared cases, host rejection, garbage collection and two separate R interpreters passed. Source package SHA-256 was `a83579d18244cab088f25b2b6a2c21528c44040a3f8830d60348c1d372398299`. The system-default R 4.3.0 remains outside the package's supported range.
