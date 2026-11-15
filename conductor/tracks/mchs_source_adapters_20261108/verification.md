# M1/M2 verification record — 15 November 2026

## Current qualification state

**Recovered implementation `44b33969ed8254964dc95d3dbc74732d62bc8529`: not executed.** The execution environment became
unavailable during verification. No usable local execution environment remained.
Source and tests were recovered from this session's authored edits and published
through the authorised GitHub connection. Recovery is not byte-for-byte proof
that the final files equal the earlier executed working tree.

The candidate contains 34 distinct test methods and a separate installed-native
smoke test. Full replay, syntax/lint/format and installed-package verification
remain mandatory. M1.3 and M2 acceptance markers are left open accordingly.

## Executed before the outage

| Check | Observed result | Exact limit |
| --- | --- | --- |
| Live repository/ownership inspection | Main `e34f87c9df39a2132fecee142431cdeefb732471`; initially only PR #17. Subsequently read the integrator's PR #20 at `e615454c9f3f41f96e9e310f446d2440d98cf5eb`. | No competing MCHS adapter owner found. Final paths use #20's `adapters/mchs_sources/` reservation. |
| Upstream contract inspection | MCHS `125933c7770e9a6bed9b62e354a6380d3dac3d47`; Atlas `a93516ed416118bc51c1db2b71ab540fa4d0fe52`; pinned code/blob records retained. | Read-only inspection; no upstream runtime or official data qualification. |
| Initial test baseline | Import failed before the adapter module existed. | A missing-module baseline, not proof of an economic defect. |
| First source suite | **24 tests passed**, including five native-CLI tests, with exit code 0. | Uncommitted earlier working version. Its exact file hashes were not captured before the outage; this does not qualify the final recovered head. |
| Native synthetic outcomes | Funding 42.50; tariff 50.00; resource cost 15.00; separate supplied payment 40.00. Activity-only funding generated no resource-use lines. | Synthetic transport/valuation, not MCHS equation or Atlas parser execution. |
| Native rejection/rounding controls | Missing rates, unknown rights/status, edition/date/unit incompatibility, float inputs, duplicate identities and zero/error distinction; half-even 0.005 → 0.00 and 0.015 → 0.02; native component duplication rejected. | Earlier 24-test version only. The separate interval API was not requalified in this lane. |
| Intermediate Ruff | Ruff 0.17.4 check passed; format applied to two files, two unchanged. | Subsequent fixes, test changes and recovery have not been linted/formatted. |
| Native artifact verification | Downloaded the integrator's exact candidate archive, matched ZIP and CLI digests, verified all 25 listed member checksums. | Reused native artifact, not a lane rebuild. |
| Source comparison | Rust core/CLI/Python source, Cargo.lock and toolchain unchanged between pinned main and candidate engine source; root Cargo change was the selected Apache-2.0 licence field. | Packaging/legal-file differences remain the integrator's work. |

Actual first successful test invocation, from the earlier temporary checkout:

```sh
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=adapters/mchs_atlas/src \
DAPANE_TEST_CLI=/tmp/dapane-mchs-native-3ba95fceed09/dapane \
python3 -m unittest discover -s adapters/mchs_atlas/tests -v
```

Observed terminal result: `Ran 24 tests in 0.034s`, `OK`, exit code 0.
The earlier unpushed local directory was `adapters/mchs_atlas/`. After the
integrator's reservation became visible, the recovered candidate adopted
`adapters/mchs_sources/`; its import namespace remains `dapane_mchs_atlas`.

Runtime: CPython **3.12.14**, Linux x86_64. Rust was not available on PATH.
The CLI was executed successfully from the verified existing artifact.

## Native artifact identities

- Integrator source commit: `a4ddde7ae7a799e37a5d594cde9c195ff057bc5e`.
- Source tree: `740c1f379e69db746a5d56ec7212e7676924b473`.
- [Release-assurance run 43677159295](https://github.com/edithatogo/dapane/actions/runs/43677159295).
- [Artifact 14146911264](https://github.com/edithatogo/dapane/actions/runs/43677159295/artifacts/14146911264).
- ZIP bytes: **2,475,629**.
- ZIP SHA256: `c00e72422063557250436a76a9bbfe16e42208d5543cdec0f5ac02f6d60c58d7`.
- CLI SHA256: `2d3f3c5b54399a3613d4b6d97e8538cadc3074192fdd076f261118d1a67b03a2`.
- Artifact rustc receipt: **1.99.1**, host `x86_64-unknown-linux-gnu`.
- Archive `source-commit.txt`, `source-tree.txt` and `evidence.json` agreed.
- All **25** member checksums in `CHECKSUMS.sha256` matched extracted bytes.

These identities establish which native candidate was used, not execution of
the recovered adapter source or approval to release that candidate.

## Source review fixes requiring replay

[Review](review.md) records the added resource-rights matching, future-payment
rejection, nonduplicating test inheritance, fictional fixture licence metadata,
and no-resource collection-type check. They remain unexecuted on this head.

## Pending exact-head commands

From a restored or existing authorised runtime with the qualified native CLI:

```sh
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=adapters/mchs_sources/src \
DAPANE_TEST_CLI=/absolute/path/to/qualified/dapane \
python3 -m unittest discover -s adapters/mchs_sources/tests -v

ruff check adapters/mchs_sources/src adapters/mchs_sources/tests
ruff format --check adapters/mchs_sources/src adapters/mchs_sources/tests
python3 scripts/validate_conductor.py
```

Use the package's pinned build dependency to build a wheel, install it with the
exact qualified Dapane native wheel, and run the same suite with `python -I`
from outside the checkout. Also execute:

```sh
python -I /absolute/repo/adapters/mchs_sources/tests/installed_smoke.py \
  --fixture /absolute/repo/adapters/mchs_sources/fixtures/parallel-views.json
```

The native test harness fails if its CLI is absent. No conditional success or
silent skip is introduced.

The current registry still says `new`. The lane's own track says
`in_progress`; this deliberate shared-change request prevents final Conductor
acceptance until the integrator updates its row. Do not waive or modify the
validator. Root CI also needs an explicit lane invocation; unrelated green jobs
do not establish that these 34 tests ran.

Live-provider installed consumers, official rate releases, cross-platform claims,
new package release assurance and M3 migration remain unexecuted.

## Publication integrity checks

All 22 authored files were read back from GitHub at implementation commit
`44b33969ed8254964dc95d3dbc74732d62bc8529` and matched the submitted text.
The implementation tree is `8d3e0c62fc0e630bc7bf9dba79a773824bef0935`.
JSON documents parsed, all changed paths were within the two owned roots, and
candidate Markdown links resolved against the pinned base plus authored files.
These read-only publication checks do not execute Python, run Ruff, verify an
installed wheel, or satisfy the Conductor lifecycle gate.
