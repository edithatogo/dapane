# Run the first Dapane kernel

The working interface is the [version 0.1 contract](contract-v0.1.md). Inputs are
exact decimal strings or rational pairs; quotes, units, source versions, economic
basis, dates and rounding are explicit. The examples contain synthetic data.

## Native CLI

Install the pinned Rust toolchain using rustup, then build from the checkout:

```sh
cargo build --locked --release -p dapane-cli
target/release/dapane evaluate fixtures/newborn-screening.json
target/release/dapane evaluate fixtures/workforce.json
cat fixtures/activity-funding.json | target/release/dapane evaluate -
```

The newborn example returns a 150.00 source total and conserving infant views of
60.00 and 90.00. The workforce example uses exactly one third of an hour at 90 per
hour. The activity example values 2.50 units at 17 per unit as funding of 42.50;
it contains no physical resource-use inference.

`dapane evaluate` prints a complete JSON report to stdout, or a structured error
to stderr with a nonzero exit status. It has no network or implicit current-date
selection. Save stdout only after checking the exit code. For operational file
exchange, write to a temporary result and rename it only after success; the CLI
does not itself implement job claiming or atomic publication.

To install the CLI independently of this checkout:

```sh
cargo install --locked --path crates/dapane-cli --root /absolute/install/location
/absolute/install/location/bin/dapane --version
```

## Python extension

Build a native wheel for a selected CPython interpreter and install it into a
separate virtual environment. This is a local source build; no PyPI release is
assumed.

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/maturin build --locked --release --interpreter .venv/bin/python --out dist
.venv/bin/python -m pip install --no-deps --no-index --find-links dist dapane==0.1.0
```

```python
import json
from pathlib import Path
from dapane import DapaneError, evaluate, evaluate_json

request_text = Path("fixtures/newborn-screening.json").read_text()
report = evaluate(json.loads(request_text))
assert report["totals"]["rounded"] == "150.00"

# Exact canonical JSON also remains available without a dict round trip.
report_json = evaluate_json(request_text)

try:
    evaluate({"schema_version": "unsupported"})
except DapaneError as error:
    print(error.code, error.path, error.message)
```

The dict interface also transports standard-library `Decimal` and `Fraction`
exactly. It rejects binary floats and non-finite values. All valuation and
allocation still execute in Rust; Python performs transport and error mapping.
The native extension is built for each interpreter rather than claiming a stable
ABI. Actual tested versions and platforms are recorded in
[runtime verification](runtime-verification.md).

## Verification

```sh
cargo fmt --all --check
cargo clippy --locked --all-targets -- -D warnings
cargo test --locked
python scripts/validate_contract.py --cli target/release/dapane
python scripts/validate_conductor.py
```

Run Python tests from outside the repository after installing the wheel:

```sh
cd /tmp
/absolute/venv/bin/python -m pytest --import-mode=importlib /absolute/dapane/tests/python -q
```

The schema check needs `jsonschema`, pinned in the development requirements.
Schema validation handles structural constraints; Rust additionally checks
references, date applicability, component overlap, conservation and numeric
bounds. Neither check verifies the caller's source declarations against external
data or demonstrates real programme validity.

## Current scope

Supported: dated nonnegative quantities, exact quotation application, disjoint
component pricing, half-even line rounding, deterministic full-pool allocation,
event/process/object context, preserved source declarations and replay digests.

The native/CLI [interval profile](interval-contract-v0.1.md) additionally supports
caller-declared uniform calendar-day exposure and pinned rate-boundary splitting:

```sh
target/release/dapane evaluate-intervals fixtures/intervals/rate-boundary.json
python scripts/validate_intervals.py --cli target/release/dapane
python scripts/qualify_kernel.py
```

The synthetic interval fixture gives `1/3 × 90 + 2/3 × 120 = 110`. Its dates do
not imply a working calendar or observed utilisation. The interval method uses
per-segment half-even rounding and keeps the original parent and expanded request
for audit/replay. The [kernel evidence](../conductor/tracks/rust_kernel_20261108/verification.md)
records the exact qualified source and artifacts. Python continues to expose
the existing scalar entry points.

The [selected provider composition](python-provider-verification.md) qualifies
a source-selected QLD base-pay quotation and one manual DNA extraction labour
stage. The [installed-consumer workflow](../.github/workflows/provider-consumers.yml)
builds the pinned provider revisions and exercises them in their separate
Python 3.15.2 and 3.15.1 environments. The provider-owned migration guides
describe their APIs and preserved historical paths.

## Local CI/CD hooks, selective routing, and profiling

Local Git hooks live in [`.githooks/`](../.githooks/pre-commit) (activate with
`git config core.hooksPath .githooks`, and mirrored in
[`.pre-commit-config.yaml`](../.pre-commit-config.yaml)):

- **`pre-commit`** runs Gitleaks, staged JSON hygiene, Ruff lint/format, selective Rust
  `fmt`/`clippy` for touched crates only, Conductor validation, release-manifest
  checks, and fast affected unit tests, printing a compact wall-clock profile.
  Set `DAPANE_PRECOMMIT_ACT=1` to also run affected workflows in `act`.
- **`pre-push`** runs Gitleaks across the pushed commit range and invokes
  [`scripts/run_local_ci.py`](../scripts/run_local_ci.py) on affected scopes.

Run local CI manually on any diff or the full suite:

```sh
python3 scripts/run_local_ci.py --dry-run
python3 scripts/run_local_ci.py --runner auto --profile
python3 scripts/run_local_ci.py --all --runner native --profile
```

With `--runner auto` and [`.actrc`](../.actrc), affected GitHub Actions workflows
run via `act` when a Docker daemon (e.g. `colima start`) is reachable, and otherwise
fall back cleanly to profiled native parity execution (using `cargo-nextest` when
installed). [`scripts/ci_select.py`](../scripts/ci_select.py) drives both local hooks
and PR workflow filtering, while [`scripts/ci_profile.py`](../scripts/ci_profile.py)
records step wall/CPU/RSS metrics and publishes `$GITHUB_STEP_SUMMARY` tables in CI.

Separate capabilities remain on the roadmap: broader source packs and domain
recipes, richer interval exposure, financial corrections, richer economic
methods, reporting/ontology exports, R/Julia, Power Apps, process import/execution
and uncertainty/decision integrations. Unknown fields are rejected; adding a
policy name does not silently activate an unimplemented method.
