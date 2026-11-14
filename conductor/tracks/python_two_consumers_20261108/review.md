# Conductor review: Python delivery with two consumers

Review date: **15 November 2026**.

Status: **bounded static review passed after remediation; final genomics recheck passed; runtime qualification and final workforce resource-fix recheck pending**.

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
| Workforce provider | [PR #305](https://github.com/edithatogo/microcosting_healthworkforce/pull/305); initial `ea8eb6821335b12d318d2ea2cd40e44ee87d689d`, remediation rechecked at **`eddde5b2a88997e08319f42cf898f0c35a5c7958`** |
| Genomics provider | [PR #173](https://github.com/edithatogo/microcosting_genomics/pull/173); initial `ec5f15a07f6a28b017c3c9d272869a70796b1fce`, semantic remediation through `c4a6406c9e4ce3f32ddb139c150229599a06c443`, final bounded recheck at **`90eb19dbc0868ecd1102d2d64a32fa98d0aab6ee`**, tree `67a4b379bd6a3783964d4f978b3d99bae2a101b8` |

The provider baselines were workforce
`ba86fdf6843d070d257f799e061ea14d18fba387` and genomics
`de09042469fce2f48b1227283a9e2daa08fc7c79`. The final genomics formatting/type
changes have been reconciled with the reviewed semantics. Workforce's subsequent
package-resource compatibility fix still requires its final bounded recheck.
The coordinator must pin actual qualified commit identities. A pass on an earlier
revision does not qualify a later one.

## Findings and remediation

| Severity | Finding | Reviewed resolution |
| --- | --- | --- |
| Medium | Genomics compared the source Decimal spelling directly with its fixed-point quotation projection, rejecting valid unchanged values such as `1E+2` versus `100`. | The consumer now checks the producer's finite, bounded exact Decimal projection. Regression cases cover modest positive/negative exponents, altered amounts and unsupported values. This is transport conversion, not valuation. |
| Medium | Genomics scope membership accepted strings in place of employer/classification arrays, permitting substring matches in a rehashed malformed artifact. | Actual nonempty arrays of nonblank strings are required before exact membership. Both malformed scope fields have regression cases. |
| Medium | Workforce formatted compact extreme Decimal inputs before applying the artifact byte limit, allowing excessive expansion. | Decimal digits/scale and rational components are bounded before string conversion, including explicit quantity transport. Cases cover huge exponents, precision/scale limits and supported exact values. |
| Medium | The initial coordinator exercised the new historical Rust replay but did not qualify the real installed legacy genomic cell-read route. | The reviewed runner constructs the installed `SheetManager` and `CalculationEngine`, invokes the preserved adapter, requires nonmissing AB22/AB23/AB24 values and compares them with separately extracted raw XML caches. Execution remains a runtime gate. |
| Medium | The provider owner reported that the restored workforce suite found a residual `importlib.resources.files("src")` anchor after the canonical namespace move. | The proposed repair uses the canonical resource anchor and aliases the legacy package root as well as its modules. Final published-fix review and resource/identity verification are pending; the earlier static review does not close this runtime finding. |
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
new canonical artifact digest. Installed compatibility tests remain required.

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

## Final assessment and remaining gates

No substantive unresolved correctness finding remains in the final reviewed
genomics semantics or coordinator runner blob. Workforce's subsequently found
package-resource compatibility finding remains pending as stated above.
The runner now closes the ownership,
legacy-entry-point, artifact-identity and controlled-rounding review findings.
Its workflow separates the pinned workforce Python 3.15.2 and genomics Python
3.15.1 environments, uses isolated installed imports and compares both consumers
with the same Rust implementation.

**Runtime qualification is pending in this review record.** No CI or installed
test pass is asserted here. The coordinator must record actual final-revision
provider checks, installed-consumer execution, selected historical-route results
and required Dapane checks. Recheck the final workforce package-resource fix for
semantic drift and update the immutable lock accordingly. Complete and archive
the track only after those results are recorded; preserve this review and the
earlier evidence. No source workbook output is copied into this record.
