# Newborn synthetic N1–N2 handoff

Review date: 2026-11-15. Scope: synthetic prepared recipes and tests only.
Integration owner: Dapane — Release assurance and consolidation,
chat `6af8e445-ffd4-83ec-8e51-ff6b596f11b1`.

## Immutable implementation identity

| Record | Identity |
| --- | --- |
| Pinned main | `e34f87c9df39a2132fecee142431cdeefb732471` |
| N1 published commit | `08de58177ba98d66a3da7e05eee430e0ec4cdb19` |
| N2 published implementation | `41a6f204ab0215f3f28393b413ebf3c327a5282a` |
| N2 complete tree | `a1b553b6c2a54ce06a6e022b863c903d902cf3e0` |
| Equivalent local implementation commit | `e67556658ca0e8f08e031f9778947127f5e25fa8` |
| Branch | `feat/newborn-synthetic-n1-n2-20261115` |

The GitHub tree was compared with the local committed tree before updating the
branch; they are identical. GitHub commits were created through the existing
authenticated connection because shell Git push had no credentials. No credential
or infrastructure was changed. This documentation-only follow-up records the
implementation identity; its own submission SHA belongs in the PR description.

The first temporary checkout was lost when the execution environment restarted.
Its unpublished local N1 SHA `429d3320c4199042882c111546a3aba5c356d817` is historical,
not the submitted implementation. Recovered files were re-tested. Prior runs are
not substituted for the source-bound results below.

## Delivered and retained scope

N1.1–N1.3 and N2.1–N2.3 are complete for the explicitly authorised synthetic scope.
The [recipe guide](../../../fixtures/newborn-synthetic/README.md) documents thirteen
prepared requests, invented source inputs and independent expected values:

- Distinct infant, episode, collection attempt, specimen, card, assay, batch,
  result, recall, confirmation and follow-up identities; two assays per specimen.
- Disjoint salary/oncost composition and once-only transport, QC, setup, controls,
  assay materials and programme overhead.
- Inadequate specimen and repeat collection; failed assay with successful repeat;
  unresolved failure; reflex testing; partial batches; additional panels.
- Declared family-time inclusion and five population/window-specific denominators.
  Repeats do not increase distinct infants; zero-denominator references are null.
- Explicit below/at/above capacity scenarios; missing use and unknown availability
  retain null shares and unallocated cost under contract 0.2.

The original fixture and shared expectations are unchanged. The baseline remains
150 total and 60/90 infant views, including its historical input/output digests.
Point half-even rounding and accepted half-even rounding per generated interval
segment are preserved. Native financial arithmetic remains entirely in Rust.

The richer recipe is a versioned fixture profile producing ordinary requests.
Denominator ratios are independent test references, not a new native reporting API.
There is no real provider execution, programme pack, clinical assumption, empirical
validation or qualified reporting adapter. N3.1–N3.3 remain open and the track stays
`in_progress`; no registry lifecycle change is requested.

## Executed evidence

The [machine-readable receipt](verification.json) binds the exact implementation,
fixture/test SHA256 values, environment and all thirteen native input/output digests.
It also retains the full stdin snapshot for the interval rounding control.

| Executed check | Result |
| --- | --- |
| Dedicated installed-wheel newborn checks | 63 passed |
| Complete installed Python suite, outside checkout | 196 passed on CPython 3.12.14 |
| All thirteen prepared requests through installed CLI | Complete reports equal installed-wheel reports, including digests |
| Existing point contract validator | Five reference reports; 37 structural/parser negatives, 14 native rejections, three identity/context cases |
| Existing interval validator | Nine schema negatives, eleven native rejections and fifteen tampered-report controls passed |
| Separate newborn interval tie control | Two exact 0.005 segments round to 0.00 + 0.00; exact total 0.01; scalar replay identical |
| Conductor validator | Passed for 14 tracks, 12 requirements and 153 tasks |
| Conductor lifecycle regressions | 12 passed |
| Ruff 0.17.4 lint/format and whitespace check | Passed |

Commands, with `REPO` and `CLI` set to the relevant checkout and installed binary:

```sh
cd /tmp
python -m pytest -p no:cacheprovider --import-mode=importlib "$REPO/tests/python" -q
cd "$REPO"
python scripts/validate_contract.py --cli "$CLI"
python scripts/validate_intervals.py --cli "$CLI"
python scripts/validate_conductor.py
python -m unittest discover -s tests -p test_conductor_validation.py -q
ruff check tests/python/test_newborn_synthetic.py
ruff format --check tests/python/test_newborn_synthetic.py
git diff --check
```

The installed Linux CPython 3.12 wheel is the retained qualified kernel artifact,
SHA256 `e3f123ea0a7c3d8fe2eb12db5747876c44733e967c526c11e579cb6773627286`.
The CLI SHA256 is `ee16254d1443d202e9a8b9f12be24c93fdd1f87830eebd14521334498de56573`.
Installed native and Python bytes were compared to that wheel. Full `crates/`,
`python/`, Cargo manifests/lock, toolchain and Python packaging files were compared
between pinned main and qualified kernel source `a703c93d49e782b67fe4b14588bf1fb26292bb23`:
they are identical. These are executed fixture/interface checks using existing
qualified binaries; no fresh Rust build is claimed for this lane's local session.

The PR's hosted builds, other Python/platform qualification, automated review and
offline security are separate evidence. At receipt creation those final-submission
checks had not executed. Read their current exact-head status before integration;
queued, skipped or absent checks are not passes.

To repeat CLI/wheel parity and the stored interval control:

```python
import json
import os
from pathlib import Path
import subprocess
import dapane

root, cli = Path(os.environ["REPO"]), os.environ["CLI"]
fixtures = root / "fixtures/newborn-synthetic"
cases = json.loads((fixtures / "scenarios.json").read_text())["cases"]
for name in cases:
    path = fixtures / f"{name}.json"
    result = subprocess.run([cli, "evaluate", str(path)], capture_output=True,
                            text=True, check=True)
    assert not result.stderr
    assert json.loads(result.stdout) == dapane.evaluate(json.loads(path.read_text()))
receipt = json.loads((root / "conductor/tracks/newborn_screening_20261108/verification.json").read_text())
control = receipt["interval_rounding_control"]
result = subprocess.run([cli, "evaluate-intervals", "-"],
                        input=json.dumps(control["stdin_snapshot"]),
                        capture_output=True, text=True, check=True)
assert not result.stderr
report = json.loads(result.stdout)
assert report["report"] == dapane.evaluate(report["expanded_request"])
assert len(report["segments"]) == 2
assert [line["rounded"] for line in report["report"]["lines"]] == ["0.00", "0.00"]
assert report["report"]["totals"]["exact"] == {"numerator": "1", "denominator": "100"}
assert report["report"]["totals"]["rounded"] == "0.00"
```

## Review findings and fixes

Author review found and fixed two verification issues before submission:

1. The first check froze the entire shared expected-output file, which would impede
   unrelated integrator changes. It now freezes only the historical newborn entry.
2. Valid-screen metadata needed to prove a selected result belongs to its infant.
   Tests now follow result → assay → specimen → infant and the episode relation.

All references remain independent fixed values. Eleven negative cases exercise
duplicate uses/components/pools, direct-plus-pooled attribution, missing quotations,
unknown fields, over-capacity/zero-capacity, missing quantities, unsupported units
and prohibited capacity downgrade. This is author review and executed evidence;
it is not mislabelled as an independent third-party review.

## Integrator requests and path ownership

Changed paths are limited to this track, `fixtures/newborn-synthetic/` and the new
`tests/python/test_newborn_synthetic.py`. Shared code, schemas, root docs, Cargo,
locks, workflows and `fixtures/expected.json` are unchanged.

**Required central coordination:** ownership PR #20 initially reserves
`adapters/newborn_screening/`. Dylan's explicit lane instruction authorises the
fixture namespace and dedicated tests used here. Reconcile the central map to
these actual paths, retaining this implementation. No rename or competing adapter
is needed. This lane has not edited the integrator-owned map.

**No shared runtime/API/schema/dependency change is required.** The existing Runtime
workflow already discovers the dedicated file within `tests/python` for all four
installed-wheel jobs. The new CLI catalogue was executed locally; promoting it
into the common CLI qualification script is an optional integrator follow-up,
without copying these references into the shared expectations file.

Keep existing release, numerical, privacy and offline-security gates. The sole
integrator reviews the final PR head and receiving tree before any integration.
No merge, release, tag, registry publication, new worker, external-repository edit,
credential change or infrastructure action was performed. Publication stays disabled.

Rollback is a scoped revert of the lane commits, retaining the original baseline
and its accepted contracts. No shared migration or irreversible data change exists.
