# Review report for Optional Power Platform delivery

## Summary

The local synthetic handoff passed on 20 November 2026 after the review fixes in [ad6edcd](https://github.com/edithatogo/dapane/commit/ad6edcdbe10090a28773ace58199adf0f3fc9bf9). The owner deferred live SharePoint work. The [specification](spec.md) retains the deployment checks for any later pilot.

## Verification checks

- [x] Plan compliance for file export, CLI execution, installed-wheel replay, immutable history and a versioned SharePoint setup contract.
- [x] Style compliance with Ruff lint and format checks for the exchange scripts.
- [x] Regression coverage for the command-line round trip, revision keys, list columns, direct links, partial archives and invalid dates. Existing retry, replacement and tamper cases were retained.
- [x] Eleven exchange tests passed against the release CLI and newly built wheel on CPython 3.15.1, macOS arm64. The wheel was installed before running the tests from outside the checkout.
- [x] Conductor validation and all 12 lifecycle regression tests passed after the in-place archive.

## Findings and fixes

- **List presentation.** The earlier JSON summary contained arrays and a relative filename. It also lacked the built-in Title value. The opt-in SharePoint summary emits scalar fields, a direct bundle link and counts for exclusions and incomplete capacity pools. It carries currency, price year, basis and perspective. Incomplete totals remain blank.
- **Revision identity.** Two CareOps requests can share a native bundle digest. The unique key now uses the project, scenario and input revision. The original input bytes have their own digest. A repeated byte-identical export keeps the same paths and file identities.
- **Import failure handling.** An incomplete archive and a missing recording date now fail before a summary is written. The importer checks the expected three files, receipt and installed-wheel replay against the original export.

## Recorded execution

Commands run from the repository except for pytest, which was launched from a temporary directory with absolute paths to the worktree interpreter, test file and release CLI.

```sh
cargo build --locked --release -p dapane-cli
.venv/bin/maturin build --locked --release --interpreter .venv/bin/python
DAPANE_CLI=/absolute/candidate/dapane /absolute/worktree/.venv/bin/python \
  -m pytest -q /absolute/worktree/power_platform/test_manual_exchange.py
.venv/bin/ruff check power_platform
.venv/bin/ruff format --check power_platform
.venv/bin/python scripts/validate_conductor.py
.venv/bin/python -m unittest discover -s tests -p test_conductor_validation.py -q
```

The documented example produced AUD 150.00 in price year 2026 and `completed`. The separate exclusion and capacity-gap cases produced `incomplete` with a blank total. The file-transfer test used independent local copies of the export and result files.

| Checked artifact | SHA-256 |
| --- | --- |
| Release CLI | `6c1d3f0faaf0b0d951eabc76afbd2e856b389fce21c1501eae80cfd09a3a4a3f` |
| Installed CPython 3.15 wheel | `c40b987a393c98baf5cefec8d88737117a10f4db186983d0256cf93f1306294e` |
| Example input export | `f730e43cdcd1f57cf4e7f6fda5bc5b7735125ecfc3da7ccc0616238567c08c9f` |
| Example bundle file | `b33d9951bc2d7541ce27431c97cc7127d1bd0748ebf3fde3c035a6c5eb78bee3` |
