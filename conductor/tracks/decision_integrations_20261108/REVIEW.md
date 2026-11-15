# Bounded self-review and fixes

This is the implementing agent's self-review, not an independent review by a
second worker. User instructions prohibited creating more workers. Native
re-execution of the recovered source remains blocked; see [verification](VERIFICATION.md).

## Findings resolved in the local implementation and carried into recovery

| Finding | Consequence | Resolution / evidence boundary |
| --- | --- | --- |
| D1 could not rely on deserializing maps directly | Duplicate keys could disappear before validation | Recursive unique-key JSON reader covers maps, arrays and embedded native requests; rejection test present |
| Replacing defaults before validation could hide an invalid native template | A model could appear admissible only after substitution | Evaluate the original template first through the unchanged native JSON method |
| Re-serializing typed core inputs could drop the presence of a prohibited empty 0.1 capacity field | Adapter could weaken a native schema boundary | Keep raw native request shape and use public JSON entry points; negative regression present |
| Joining on only draw/strategy labels would lose scenario, replication or subgroup identity | Mispaired comparisons and silent pooling | Require the complete six-key Cartesian panel and bind the full draw-set digest |
| A broad fiscal cost label did not distinguish opportunity cost from budgetary expenditure | Economic cost could silently become public net outlay | Require `resource_basis`; public finance requires `public_expenditure`, societal requires `economic_cost`; line bases must match |
| Missing fiscal categories were implicitly zero | Incomplete evidence could appear to be a complete result | Require explicit medical, enforcement, excise and GST categories; known zero is a labelled zero flow |
| Aggregate rounding would change accepted interval behavior | Two half-cent generated segments could become a rounded cent | Return unchanged native reports and test exact 1/100 against rounded 0.00 |
| A fiscal method label could imply an upstream qualification | Unqualified provider use | Keep a local synthetic reference method, no provider import/dispatch, and require integrator review before production promotion |

The last two fiscal semantic fixes (basis and category completeness) are covered
by two additional tests; the historical local T1 suite increased from 17 to 19
passing tests. The recovered tree carries those fixes, but those earlier passes
are not exact-tree qualification.

## Recovered-source inspection

Manual review traced input limits/duplicate handling, typed unknown-field
rejection, exact rational bounds, stable-ID binding targets, template-before-draw
evaluation, key completeness, native report retention, transfer sign conventions,
matching payer/recipient timing, fiscal basis compatibility and exact rate-per-step
discounting. Code comments were clarified to describe an unqualified synthetic
reference rather than claim method qualification.

The fixture quantities and expected values were checked by independent
JavaScript BigInt rational arithmetic and the draw-set digest was recomputed.
A static path check admits only this adapter namespace and the two assigned
track directories. Root Cargo files, shared crates, schemas, CI, registry and
upstream repositories were not edited.

## Open findings / integration gates

1. Reconstructed source has not been compiled, linted, formatted or tested at its
   published SHA. Recovery errors and formatting differences remain possible.
2. The nested workspace's lockfile was reconstructed from the root dependency
   graph. Package identities/checksums match, but `cargo --locked` has not
   accepted the recovered lock.
3. Root CI does not execute this adapter. The integrator must add explicit
   manifest-path checks without weakening existing gates.
4. The two central registry state rows need the integrator's coordinated change;
   owned records truthfully show work started.
5. T1's exact signed arithmetic is a reference candidate. Any production method
   registration or bridge to rounded/native cost outputs requires an explicit
   integrator decision on signs, timing, basis, precision and rounding.
6. T1 checks the syntax of a declared draw digest, not a producer/consumer match.
   Cohort/equity/provider integration and D1-to-T1 verification remain T2/T3.
7. Upstream planned oracle paths do not exist at the inspected Tobac SHA. Future
   parity work must reconcile the actual `health.py` contract and source
   qualification separately, without assuming the old paths or method names.

All seven findings remain visible in the [handoff](HANDOFF.md). No shared-file
edit, gate waiver, source-adjudication duplication, merge or release was used to
close them.
