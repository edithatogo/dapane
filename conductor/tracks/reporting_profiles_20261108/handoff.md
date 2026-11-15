# Reporting E1–E2 exact-SHA handoff

Recipient: the existing sole integrator, **Dapane — Release assurance and consolidation**, chat `6af8e445-ffd4-83ec-8e51-ff6b596f11b1`, [Dapane PR #17](https://github.com/edithatogo/dapane/pull/17).

## Proposed source and ownership

| Identity | Exact value |
| --- | --- |
| Base main | `e34f87c9df39a2132fecee142431cdeefb732471` |
| Base tree | `c07a6b2589b9d665f619f5d977d66e513180bab4` |
| Tested implementation | `8f7c5dcbe14287759d62fd41d0804a92b734b75f` |
| Tested tree | `7bbc79089737c462460ba3029a901e60f86ff68d` |
| Published branch | `feat/reporting-jsonld-shacl-e1-e2` |
| First durable checkpoint | `fe337a04236d595fb44a00aba6355fa85e642bc4` |
| Coordination record | [PR #20](https://github.com/edithatogo/dapane/pull/20), head `e615454c9f3f41f96e9e310f446d2440d98cf5eb` |

The final PR description names the handoff commit and its tree separately. This file cannot contain the SHA of the commit that contains itself. Its implementation SHA is immutable, and [execution.json](evidence/execution.json) records every tested adapter blob. The handoff commit changes only this track's records.

Only `adapters/reporting_profiles/` and `conductor/tracks/reporting_profiles_20261108/` are owned by this lane. There is no new shared adapter parent file. Live main, open PRs and track ownership were inspected before work and again before submission; no competing reporting owner was found. Other active lanes were left untouched.

E1.1–E1.3 and E2.1–E2.3 are complete within the bounded synthetic repository-local candidate. The whole track remains `in_progress`; E3 is pending. This is not a merge, release or capability-promotion request.

## Delivered behavior

- Pin and verify seven UOGTO/standards_check files, catalogue counts, original instrument/version/item identities and extraction qualifications.
- Account for all 281 native property occurrences through reference rules or explicit unmapped reasons.
- Read unchanged verified run-bundle history; replay native Rust, preserve its exact JSON, digest, lifecycle and selected snapshot; emit a separate versioned JSON-LD document.
- Require explicit costing method, compatible valuation basis and profile applicability. Preserve partial, not-reported, not-assessed, unresolved and justified not-applicable states.
- Require precise evidence locations for reported/partial assertions, retain caller review separately from upstream mapping review, expose domain-only extraction gaps and avoid a compliance score.
- Validate against actual pinned upstream SHACL; reject malformed declarations, tampered pins, invalid contexts/terms and redefinitions without emitting partial financial stdout.

There are no copied/redefined upstream semantic definitions or numerical formulas. Existing per-generated-segment half-even and fail-closed native contracts remain unchanged.

## Exact source and native pins

- UOGTO `7e9075b8fd77543fc8853fab20319415cb86597d`: [PR #128](https://github.com/edithatogo/UOGTO/pull/128), open/unmerged.
- standards_check `d1f1137edfa5375e0225ca2216903ce5583a44f0`: the matching import snapshot; [catalogue PR #65](https://github.com/edithatogo/standards_check/pull/65) is merged. Both selected files match observed main `d592bb3fa7972f421a1a68ec28e1938fd3d52136`.
- Native release-owner artifact source `a4ddde7ae7a799e37a5d594cde9c195ff057bc5e`, run `43677159295`, artifact `14145769688`.
- CPython 3.12 wheel SHA-256 `17421cb91cd68fde202eaadc361a4f7d5395efb12042d539cf1f82da2033e46c`.
- CLI SHA-256 `2d3f3c5b54399a3613d4b6d97e8538cadc3074192fdd076f261118d1a67b03a2`.

The [source lock](../../../adapters/reporting_profiles/sources.lock.json), [native artifact receipt](evidence/native-artifact.json) and [verification record](verification.md) retain the full identities and qualifications.

## REP-IR-01 — Required registry reconciliation

**Status: open; blocks Conductor validation and integration.**

Owned shared path: `conductor/tracks.md`. Select the existing row whose link target is `./tracks/reporting_profiles_20261108/index.md`. Change only these two cells; retain its title, link and `RQ-07, RQ-01` requirements:

| Cell | Current | Requested |
| --- | --- | --- |
| Marker | `[ ]` | `[~]` |
| Status | `new` | `in_progress` |

Reason: this lane has executed E1/E2 and correctly updates its own plan, index and metadata. Leaving the registry unchanged produces exactly one Conductor error. The lane has not edited or bypassed the shared row. Apply the change in an integrator-owned commit, then run `python scripts/validate_conductor.py` and the existing lifecycle tests against the resulting head. E3 stays pending; do not mark the track completed or archived.

## REP-IR-02 — Required explicit optional reporting CI

**Status: open; hosted reporting execution has not occurred.**

Owned shared paths: the integrator's choice of `.github/workflows/` and installed-artifact qualification. Existing root test discovery does not include `adapters/reporting_profiles/tests/`.

Proposed job contract:

1. Check out the exact integrated candidate head and record its tree. Obtain an exact native wheel/CLI from the same source-qualified run or another explicitly reviewed compatible artifact. Verify the artifact receipt and hashes; do not resolve the unpublished Dapane name from a public registry.
2. Use a separate CPython 3.12 environment. Install the wheel with `--no-deps`, then install `adapters/reporting_profiles/requirements.lock` with `--require-hashes --only-binary=:all:`. Pin any lint tool separately; local evidence used Ruff 0.17.4.
3. Materialize read-only local UOGTO and standards_check snapshots at the exact commits in the source lock. The test loader independently verifies seven file hashes, bytes and Git blob IDs. No workflow-supplied floating branch may replace those pins.
4. Run the explicit reporting suite below, the retained interval validator with the selected CLI, and the existing Conductor gates. Preserve stdout/stderr, package versions, source/tree IDs, wheel/CLI hashes and actual exit codes.
5. Require negative declarations to fail with no output and actual upstream SHACL graph mutations to be nonconformant. Keep network access disabled during source loading/export where the host supports it; the suite also installs a socket/URL tripwire.
6. Qualify any additional platform separately. Keep RDF dependencies outside ordinary native/Python imports and the minimal Rust graph.

```sh
DAPANE_REPORTING_SOURCES=/path/to/exact-snapshots \
  python -m unittest discover -s adapters/reporting_profiles/tests -v
python scripts/validate_intervals.py --cli /path/to/exact/dapane
ruff check adapters/reporting_profiles
ruff format --check adapters/reporting_profiles
python scripts/validate_conductor.py
python -m unittest discover -s tests -p test_conductor_validation.py -v
```

Compatibility: no shared numeric/schema change is required for the repository-local candidate. Optional dependency advisory/licence policy and any capability/installed-package promotion remain the integrator's decision. Preserve all existing numerical, privacy, security, installed-artifact and release gates.

## REP-IR-03 — Future shared schema/API requests

**Status: deferred; not required to use this repository-local candidate.**

- The adapter imports the existing repository bundle verifier. Packaging it as an SDK extra requires an integrator-owned supported verifier API and packaging decision; this PR does not copy or move the shared verifier.
- The closed reporting declaration/export formats are separately versioned. Registering a reporting JSON Schema in shared `schemas/` requires an integrator proposal with a unique schema ID and positive/negative fixtures. Strict native bundle 0.1 is unchanged.
- Native interval envelopes are not run-bundle 0.1. Their inclusion requires an explicitly versioned bundle/replay interface from the integrator. Do not coerce intervals to scalar records or reround an aggregate.
- New semantic terms, full item extraction or independently reviewed mappings belong to UOGTO/standards_check owners. Lossy decimal allocation or single-object RDF projections remain unmapped in this candidate; the existing native JSON preserves those records.

## Acceptance and remaining work

Executed at the published implementation: 41 reporting tests, existing native interval validation, Ruff lint/format, 12 lifecycle tests and dependency consistency all pass. The final track validation retains the single registry failure. See [verification](verification.md), [review/fixes](review.md) and [raw logs](evidence/execution.json).

No hosted reporting run, final integrated-head qualification, broader platform qualification, new native build, independent scientific review, E3 curation or empirical validation is claimed. The UOGTO pack remains a qualified unmerged pin. SHACL success is graph conformance only.

The final PR stays draft/pending for the sole integrator's shared changes and exact resulting-head review. No merge/automerge, release/package publication, extra worker, upstream write, credential or infrastructure change is authorised by this handoff.
