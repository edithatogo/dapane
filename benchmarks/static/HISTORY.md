# Protocol and evidence history

## Original local registration

The protocol and 24 literal cases were committed locally at
`b9485ef60799ed0a809d9c416c8b984065c7590e` before native comparison. They used
`benchmarks/static_v1/`. Main was pinned to
`e34f87c9df39a2132fecee142431cdeefb732471`.

The first comparison rejected all twelve contract violations and accepted all
seven controls and five source-truth defects. Two expected diagnostic codes were
wrong; 22/24 expectation checks passed. This failed original expectation check
is retained as an observation, not relabelled a passing run.

| Case | Original expected code | Observed and corrected code |
| --- | --- | --- |
| unsupported-discount | invalid_json | invalid_request |
| unsupported-rounding | unsupported_rounding | invalid_request |

Unknown typed fields and enum variants fail at typed deserialisation. They do
not reach the subsequent rounding validator. No evaluator or numerical expectation
changed to obtain these results.

## Local v1.1 acceptance

The correction and implementation were committed at
`5cc42f41d1713afab9348d781a38717d515b6b75`. The local suite passed **21 tests**,
including all 24 mutation expectations, all twelve cache scenarios at eight
requests, native failure/recovery, generated-segment replay, and 200 rational
half-even ties cross-checked with Decimal. This was one Linux/Python 3.12.14
execution with a Rust 1.99.1 locked offline CLI build.

## Environment loss and publication v1.2

Before paired timing collection, the environment became unavailable. The local
commits, binary and complete raw mutation artifact could no longer be accessed.
Their identities and tool-observed summaries survive in the conversation and
[local observations](evidence/local-observations.json); the local SHAs are not
claimed to be downloadable GitHub objects. Lost raw native outputs are not
fabricated or presented as a complete result bundle.

The implementation was reconstructed from the authored tool-call source.
The integrator's subsequently published ownership map reserves
`benchmarks/static/`, so publication uses that namespace and updates synthetic
source locators. This changes input/report identity. Protocol v1.2 records the
move, reconstruction and retained diagnostic corrections.

The publication revision includes the initially unexecuted build receipt,
paired runner, verifier and two extra gate tests. A small transport type guard
was added during static review. No new local execution was possible. The **exact
published head must be rebuilt, tested, linted and measured** before qualification.
Earlier 21-test evidence does not qualify this reconstructed source or its new
paths. There is no published timing or memory result.

No production files, expected shared fixtures, registry, credentials,
infrastructure, CI or security/release gates were changed. The draft PR and
track handoff retain the unresolved acceptance steps.
