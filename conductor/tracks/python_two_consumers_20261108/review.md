# Conductor review: Python delivery with two consumers

Review date: **15 November 2026**.

Status: **review complete and implementation qualification passed on `d4d6500e`
(tested merge `cf9a7ad`); track archived in place**. [PR 13](https://github.com/edithatogo/dapane/pull/13)
records the subsequent archive-commit checks and merge.

This record reviews the [specification](spec.md), [plan](plan.md), provider-owned
adapters and coordinating installed-consumer checks. It does not certify source
redistribution rights, employment eligibility, economic assumptions, a complete
assay model or whole-workbook correctness. The coordinating
[qualification record](../../../docs/python-provider-verification.md) owns final
runtime results and platform evidence.

## Reviewed identities

| Surface | Reviewed identity and scope |
| --- | --- |
| Dapane baseline | `d7063cecc26abe96a3f28fca575b99b450241430`; contract, Rust validation, Python transport and existing consumer tests |
| Initial coordinator | [PR #13](https://github.com/edithatogo/dapane/pull/13), `a1d4f9f135b09d9bb2d190540082773d86ef8056`; runner, workflow, lock and track records |
| Final coordinator runner | `scripts/verify_provider_consumers.py`, Git blob **`e1933bf3eb6427747707a77d0378171b2e3f8a60`**; actual local file and diff reviewed before commit |
| Workforce provider | [PR #305](https://github.com/edithatogo/microcosting_healthworkforce/pull/305); initial `ea8eb6821335b12d318d2ea2cd40e44ee87d689d`, numeric remediation at `eddde5b2a88997e08319f42cf898f0c35a5c7958`, final resource/identity recheck at **`c351a7c6420a356c4c13d2da3010bc7e7d0341f9`**, tree `5e28ad116994bb16ee2eacfddcb2d9bc2319eb0b` |
| Genomics production semantic review | [PR #173](https://github.com/edithatogo/microcosting_genomics/pull/173); initial `ec5f15a07f6a28b017c3c9d272869a70796b1fce`, semantic remediation through `c4a6406c9e4ce3f32ddb139c150229599a06c443`, final bounded recheck at **`90eb19dbc0868ecd1102d2d64a32fa98d0aab6ee`**, tree `67a4b379bd6a3783964d4f978b3d99bae2a101b8` |
| Genomics final tests-only revision | `be2451f34a389f90e618cf37a5e8e1fcbb148dea`, tree `3417657a247d18d97c479cf3e799744a42cc81fb`; production source unchanged from `90eb19d`, with independently reviewed workbook/delegation tests and passed final hosted gates |

The provider baselines were workforce
`ba86fdf6843d070d257f799e061ea14d18fba387` and genomics
`de09042469fce2f48b1227283a9e2daa08fc7c79`. Final provider formatting/type changes
and the workforce package-resource compatibility fix have been reconciled with
the reviewed semantics. The final immutable coordinator pins are `c351a7c` and `be2451f`; the latter
adds the separately reviewed coverage tests below to the production semantics
reviewed at `90eb19d`. Earlier identities remain dated checkpoints. A pass on an
earlier revision does not qualify a later one.

## Findings and remediation

| Severity | Finding | Reviewed resolution |
| --- | --- | --- |
| High | Hosted CodeQL identified default-branch cache poisoning capability through manual dispatch of the provider qualification workflow, even with read-only repository permissions. | Commit `d4d6500e144944824a4988b0a85ea800832b15c0` removes the optional `workflow_dispatch` trigger while preserving automatic pull-request and push-to-main qualification. Independent query review confirmed the trigger boundary; the subsequent CodeQL aggregate gate passed. No alert suppression, dependency change or acceptance-step removal was used. |
| Medium | Genomics compared the source Decimal spelling directly with its fixed-point quotation projection, rejecting valid unchanged values such as `1E+2` versus `100`. | The consumer now checks the producer's finite, bounded exact Decimal projection. Regression cases cover modest positive/negative exponents, altered amounts and unsupported values. This is transport conversion, not valuation. |
| Medium | Genomics scope membership accepted strings in place of employer/classification arrays, permitting substring matches in a rehashed malformed artifact. | Actual nonempty arrays of nonblank strings are required before exact membership. Both malformed scope fields have regression cases. |
| Medium | Workforce formatted compact extreme Decimal inputs before applying the artifact byte limit, allowing excessive expansion. | Decimal digits/scale and rational components are bounded before string conversion, including explicit quantity transport. Cases cover huge exponents, precision/scale limits and supported exact values. |
| Medium | The initial coordinator exercised the new historical Rust replay but did not qualify the real installed legacy genomic cell-read route. | The reviewed runner constructs the installed `SheetManager` and `CalculationEngine`, invokes the preserved adapter, requires nonmissing AB22/AB23/AB24 values and compares them with separately extracted raw XML caches. The integration coordinator executed this installed route successfully. |
| Medium | The provider owner reported that the restored workforce suite found a residual `importlib.resources.files("src")` anchor after the canonical namespace move. | Final commit `c351a7c` uses the canonical resource anchor and aliases the legacy package root after registering its submodule finder. Independent installed checks passed for both import orders, package/module identity, resource byte equality and bundled-profile loading. |
| Low | An earlier CI summary treated successful CodeQL analysis execution as a passed aggregate security gate. | Commit-level checks were independently refreshed. The qualification record now retains the failed aggregate checks on both `bc96cc1` and `c1333839`, separately from their passing functional jobs, and requires a successful post-fix aggregate check. |
| Low | Initial ownership assertions examined a request that the adapter evaluation helper rebuilt rather than consumed. | Snapshots now surround the direct `dapane.evaluate(request)` call. Actual workforce quantity and genomics batch inputs are checked after provider construction/evaluation. |
| Low | Malformed source Decimal strings could escape the adapter's `ValueError` convention. | `InvalidOperation` is translated into `ValueError`; a malformed-string regression was added. |

The final semantic recheck also confirmed strict source-registry version admission
(`int` value `1`, excluding booleans) and runtime rejection of missing or unknown
manual-extraction option keys after the TypedDict refactor.

The final genomics diff from `c4a6406` to `90eb19d` preserves those runtime checks
while narrowing validated types. Its batch helper retains insertion order and
the same specimen, failure and retry rules. Malformed/incomplete current-report
shapes now fail before the comparison opens the source workbook; six negative
cases exercise that boundary. This structural guard does not authenticate an
arbitrary caller-supplied report or requalify its numerical result. The docs
explicitly exclude the existing PSA/VOI demonstrations from this selected
manual-extraction qualification. No new substantive finding arose in that diff.

The workforce namespace shim retains canonical module/class identity for the
current flat package structure, preserves historical imports and pickle names,
and retains the canonical module location for `python -m` execution. Its legacy
pricing function and legacy release-digest algorithm remain separate from the
new canonical artifact digest. The final root alias gives both package names the
same canonical specification and resource location without duplicating module
instances. Its installed resource/identity checks passed in fresh isolated
processes for each import order.

## Independent numerical and identity checks

Independent integer/rational calculations established these expectations without
calling either provider or the Dapane implementation:

| Synthetic exposure or comparison | Exact expected total | Rounded expectation |
| --- | --- | --- |
| Twenty minutes at 46.0658 AUD/hour | `230329/15000` | `15.36` |
| One physical 30-minute labwork plus 5-minute administration batch | `1612303/60000` | `26.87` |
| Failed attempt followed by a complete retry | `1612303/30000` | `53.74` |
| Six separate specimen pairs of 5 minutes plus 5/6 minute, at the same current quotation | `1612303/60000` | `26.88`, with `4.48` per specimen |

The last row isolates source-line granularity from a change in historical rate
or component coverage. It is an expected one-cent difference under the declared
rounding method, not a formula repair. The runner constructs both controls for
Rust evaluation and checks complete native CLI parity. Three specimens across
two separately allocated attempts receive `17.92`, `17.92`, `17.90`; pooling both
attempts before rounding would be a different method.

The stored workforce fixture's canonical compact, sorted, UTF-8 JSON hashes were
independently recomputed in JavaScript. The hash implementation was checked
against the standard empty-string and `abc` SHA-256 vectors. Both stored digests
matched:

- Release snapshot: `160c58975b20e708fb6b46d33782391230fa97e0c033ea2341545ad1255c516c`.
- Artifact excluding its own digest field: `9cd5e8bb48b29186b7fd4ea911f914c0e0dbf4f3fc188a1f6728cbe65947ec60`.

This verifies committed fixture content and canonical identity. It does not
substitute for Pydantic regeneration or installed Python execution. The reviewed
runner additionally requires the regenerated artifact digest to match the
independent coordinator lock before handoff.

## Earlier local installed qualification

The integration coordinator executed both stages from `/tmp` using `python -I`
and noneditable installed provider wheels. This dated checkpoint used provider revisions `c351a7c` and `90eb19d`, before
the later tests-only coverage addition and kernel integration. Both stages used
the same Dapane 0.1.0 wheel:

`dapane-0.1.0-cp315-cp315-manylinux_2_34_x86_64.whl`

SHA-256: `f0b916236e7ad5ea36c905878d8d2c67cf5f38601a85e2be1ca3307d009c4c79`.

The reviewer independently recomputed that wheel hash and checked the actual
Python 3.15.2 and 3.15.1 interpreter versions. The coordinator's successful local
execution covers:

| Installed stage | Passed acceptance scope |
| --- | --- |
| Workforce, Python 3.15.2 | Export against the independent artifact pin; canonical/legacy identity; exact exposure and legacy pricing; complete native CLI parity |
| Genomics, Python 3.15.1 | No workforce import; six specimen occupancies; failed/repeated attempt pools; same-rate rounding control; complete native CLI parity; selected historical replay; actual legacy engine reads and raw-cache comparison |

For the final workforce resource fix, the reviewer separately ran two fresh
isolated Python 3.15.2 processes from `/tmp`, one for each import order. Both
verified root package identity, submodule/model identity, equal bundled-resource
bytes and successful `load_candidate_profile()` loading. These are local
installed-artifact results; they do not assert a hosted CI pass or additional
platform support.

## Final assessment and gate closure

No substantive unresolved correctness finding remains in the final reviewed
provider semantics or coordinator runner blob. The resource compatibility finding
is closed by the final fix, bounded recheck and installed verification.
The runner closes the ownership,
legacy-entry-point, artifact-identity and controlled-rounding review findings.
Its workflow separates the pinned workforce Python 3.15.2 and genomics Python
3.15.1 environments, uses isolated installed imports and compares both consumers
with the same Rust implementation.

**Implementation qualification passed on `d4d6500e`, tested as merge `cf9a7ad`.**
The qualification record retains exact provider/coordinator revisions and check
receipts. The
closeout reconciles the receiving branch and preserves the final immutable
provider pins. The track is completed and archived in place with this review
and its earlier evidence. No source workbook output is copied into this record.

## Integration reconciliation

The coordinator subsequently reconciled completed Rust-kernel main
`172d0ef39291a936a35c6e221eb467701ccefbba`. Its native and Python artifacts
were rebuilt, and both isolated installed provider stages plus all 133
Python tests passed again. The coordinator runner remains the reviewed
blob `e1933bf3eb6427747707a77d0378171b2e3f8a60`; provider revisions remain
`c351a7c6420a356c4c13d2da3010bc7e7d0341f9` and
`90eb19dbc0868ecd1102d2d64a32fa98d0aab6ee`. The qualification record
retains both the earlier hosted checkpoint and these integrated artifact
identities. No new provider or numerical-method change was introduced
while reconciling the documentation.

## Coverage-gate remediation

Codecov reported 80.48% patch coverage on the first final genomics revision,
below the unchanged 90% target. The tests-only fix
`be2451f34a389f90e618cf37a5e8e1fcbb148dea` changes only
`tests/test_dapane_adapter.py` and `tests/test_dapane_workbook.py`.
The independent reviewer inspected both actual test files and found no issue.

The synthetic workbook uses hand-authored values, formulas and raw cache strings.
Its digest override is confined to the fixture. The tests verify source-byte
preservation, exact historical exposures of 5 and 5/6 minutes, unchanged/rate-only/
component-only comparison cases, structural source rejection, lazy delegation,
request/result identity and propagation of the same import/native exception.
The evaluator double tests transport and classification; it does not duplicate
valuation or claim scientific validation.

The owner executed 69 focused tests and the full suite (1,318 passed, four
existing skips) on Python 3.15.1. Coverage of the three new production modules is
319/328 statements (about 97.26%). Ruff and strict typing passed. Production code,
source data, dependency constraints and coverage thresholds are unchanged.
The final CI, privacy and Codecov patch checks passed on the new pin. Patch
coverage is 97.25% against the unchanged 90% target. The coordinator's
installed-provider and runtime checks passed on `c1333839f2faadaaecd8c7356d0a520557a477ed`.
Both provider changes are merged in their owning repositories; the qualification
record links their check receipts and merge identities. Receiving main's setup, core-contract and Rust-kernel archives, stricter lifecycle
validator and regression checks are retained in the closeout.
No further correctness finding remains within this selected scope.

## Archive-document review

An independent review of the six closeout records—track index, specification,
plan, metadata, registry and archive index—found no substantive issue. Original
acceptance criteria, dependencies and dated evidence links are retained. The
setup, core-contract and Rust-kernel archive records and all other track statuses
are preserved. Completion remains limited to the selected installed provider scope.

## Hosted workflow-security finding

The aggregate CodeQL checks on `bc96cc1` and `c1333839` reported a high-severity
`actions/cache-poisoning/poisonable-step` finding in the new qualification
workflow. Successful analysis execution does not establish a passed security
gate; the earlier summary was corrected above. The actual annotation identified
both provider checkout refs and the manual-dispatch event. A separate review of the CodeQL query confirmed that
turning off setup-uv's cache alone would not remove the job's cache capability.
Removing the unnecessary manual trigger is the bounded fix. Ordinary PR and
push-to-main qualification remain; all numerical/provider source and pinned
revisions are unchanged. The qualification record retains the failed check and
links the successful post-fix runs on `d4d6500`.
