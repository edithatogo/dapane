# MCHS owner quality repair — 15 November 2026

## Source and scope

The received PR #25 head was `8281042676c1d9cafab69e9c57cdfd064a9a5adf`,
tree `8a324bed7aec3051a24f81138137477c3cd574ab`. Its two shared integration
commits are retained. The sole integrator remains Dapane — Release assurance and
consolidation, chat `6af8e445-ffd4-83ec-8e51-ff6b596f11b1`.

The correction commit is
[`5bf28b093edda7c092ce48d76fedc4d592de9ba5`](https://github.com/edithatogo/dapane/commit/5bf28b093edda7c092ce48d76fedc4d592de9ba5),
tree `0f27cc40904f2d82af9e7e46c722f2748a826d4b`. It changes exactly four owned files:

- `adapters/mchs_sources/README.md`
- `adapters/mchs_sources/src/dapane_mchs_atlas/adapter.py`
- `adapters/mchs_sources/tests/installed_smoke.py`
- `adapters/mchs_sources/tests/test_adapters.py`

This handoff is a documentation-only successor. The final published head and
its subsequent checks must be read from the
[head-specific PR receipt](https://github.com/edithatogo/dapane/pull/25).
A source commit, working-copy check and later hosted run remain distinct evidence.

## Received qualification and preserved failures

The integrator's
[unaltered qualification receipt](https://github.com/edithatogo/dapane/blob/497cd6472b1eb282ea6bd79271a7c76a881e9cec/conductor/roadmap-evidence-2026-11-15/attempt-2/pr25/qualification.json)
and [selected logs](https://github.com/edithatogo/dapane/blob/497cd6472b1eb282ea6bd79271a7c76a881e9cec/conductor/roadmap-evidence-2026-11-15/attempt-2/pr25/execution.json)
identify [run 43686535494](https://github.com/edithatogo/dapane/actions/runs/43686535494)
on the received head above.

That run passed 34 tests against the installed adapter, default-native smoke,
both wheel builds/installations and identity checks. Its overall qualification
failed on Ruff I001 and four formatting findings. Both failures were reproduced
locally with Ruff 0.17.4 before correction. The original 24-test working-copy
history in [verification.md](verification.md), recovered-source
[receipt.json](receipt.json), and original implementation [review.md](review.md)
remain unchanged; none is relabelled as current-source success.

## Correction and local checks

Ruff 0.17.4 applied the I001 fix to the installed smoke imports and formatted the
owned namespace. The root lint policy, dependency pins and all gates are unchanged.

The following checks passed on the corrected bytes before publication:

```sh
ruff check --no-cache adapters/mchs_sources
ruff format --check --no-cache adapters/mchs_sources
git diff --check
```

The full lint selection passed; formatting reported six files already formatted.
The fix command selected I001 only for the mutation, then the unchanged full
repository lint policy was used for verification. The
[structured review](owner-quality-20261115.json) records before/after identities.

Capacity was checked before work. The workspace overlay had approximately
5 MiB free, while /tmp had approximately 979 MiB free. A new, small temporary
checkout preserved existing work. No local Rust build was attempted. Fresh native
and wheel qualification uses the integrator's existing hosted workflow.

## Review and independence limits

A separate diff review found no changes to algorithms, diagnostics, values,
assertions, synthetic fixture bytes, provider pins or native arithmetic.
Independent Python syntax-tree comparisons found:

- Identical trees for `adapter.py` and `test_adapters.py`.
- An identical `installed_smoke.py` tree after normalizing only the two named
  top-level imports, `dapane` and `dapane_mchs_atlas`.
- One removed space before a comment in the README Python example.

The adapter does not import the native evaluator at package import time; its
default native evaluation is loaded when called. The smoke import reorder must
also pass the installed-native test on the new source.

These are author review plus independent mechanical checks, not a second
human/agent review or scientific validation. No additional worker was created.
Any required independent acceptance remains with the existing integrator;
it must not be inferred from formatting or from the historical test pass.

## Current acceptance and integration disposition

At the time this file was authored, fresh hosted qualification of the corrected
head had not executed. The PR receipt records the later exact-head outcomes,
commands, source/artifact identities and remaining gates. A passing lane receipt
does not establish provider qualification or waive repository checks.

The integrator's [intake decisions](https://github.com/edithatogo/dapane/blob/497cd6472b1eb282ea6bd79271a7c76a881e9cec/conductor/roadmap-intake-2026-11-15.md)
are acknowledged:

- S1 registry reconciliation and S2 explicit installed/native CI have been
  supplied and are preserved.
- S3 tariff-to-charge interpretation is accepted only for the separate synthetic
  outer profile. Funding, resource cost and exact payment observations/models
  remain distinct.
- M3 requires provider-owned exact values: MCHS Decimal serialized before float
  conversion and original Atlas exact values with classification, source revision
  and rights context. No inferred NEP rate or duplicate parser is introduced.

M1.3/M2 acceptance remains with the integrator; the track stays in_progress.
M3 remains outside this repair. Synthetic-only boundaries, fail-closed rejection,
and per-generated-segment half-even semantics are unchanged.

Offline security was queued on the received head and is not passed evidence.
[PR20's separate privacy findings](https://github.com/edithatogo/dapane/blob/497cd6472b1eb282ea6bd79271a7c76a881e9cec/conductor/roadmap-evidence-2026-11-15/privacy-review.md)
remain enforced independently of lane passes. No shared CI, registry, root
manifest, core, schema, upstream repository or other lane is changed by this
repair. No merge, release, scanner exception, infrastructure or credential change
is authorized or performed.
