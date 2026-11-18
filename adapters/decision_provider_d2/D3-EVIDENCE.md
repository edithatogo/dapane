# D3 — Bounded additional-evidence and native-provider qualification dossier

**Track:** `conductor/tracks/decision_integrations_20261108`, leaves D3.1–D3.3.
**Implementation location:** `adapters/decision_provider_d2/`, a proposed new
namespace whose admission is reserved to the existing Dapane sole integrator.
**Status:** locally executed synthetic preparation and negative controls; **no
installed D2/D3 provider-consumer acceptance and no scientific study acceptance**.

The upstream D1/T1 candidate remains independently owned in draft PR #23. The
optional D2 candidate is stacked on its exact head in PR #29. This dossier does
not amend D1/T1, the generic Rust valuation kernel, shared schemas, locked pins,
root CI or existing release/security controls.

## D3.1 — Selected evidence question and numerical reference

**Question:** Would resolving uncertainty about laboratory personnel time per
assay alter the choice between the present process and a proposed replacement?
The proposed study type is prospective time-and-motion measurement. This
example deliberately assumes *perfect information*; it does not infer what an
actual measurement protocol would reveal.

| Quantity, AUD 2026 per assay | Short-time draw | Long-time draw |
| --- | ---: | ---: |
| Current process: already-valued economic cost | 80 | 80 |
| Changed process: already-valued economic cost | 60 | 120 |
| Net benefit, current | -80 | -80 |
| Net benefit, change | -60 | -120 |

Both parameter draws have assumed probability 1/2 and unchanged clinical
outcomes. These **invented** costs are an independent illustrative mathematical
reference, **not** observations from the genomic microcosting workbook or
measurements at a laboratory. Their present/candidate component decompositions
are not independently modelled. A research workflow would first replace them
with **Dapane-evaluated real cost-model outputs**, drawing on the separately
owned genomic-assay and workforce sources, with explicit scenario/draw/replicate
identity and assay, currency, denominator and price-vintage mapping.

Analytical reference, derived independently of Voiage:

- Under current information, mean net benefit of *current* is -80 and *change*
  is (-60 - 120)/2 = -90; optimal current-information net benefit is **-80**.
- With perfect information, the selected strategy is *change* in the short-time
  state (-60) and *current* in the long-time state (-80); expected perfect
  information value before the information premium is **-70**.
- **EVPI = -70 - (-80) = AUD 10 per assay**, conditional on the invented
  distributions and economic perspective. This is a **maximum theoretical
  information value**, not a forecast of savings or the value of a feasible
  study. EVSI is **not calculated**.

An actual measurement study would require a pre-specified sampling/likelihood
model for staff time (including between-batch versus within-batch variation,
hands-on versus elapsed time, different staff classifications and failed/repeat
attempts), prior uncertainty and dependence across strategies, capacity effects,
research costs, candidate implementation costs and the value of the decision
over the relevant population/time horizon. These are **not** inferred from the
workbook, D1's generic draw IDs, an archived PSA, or the numerical reference.

The implementation in `study.py` prepares a complete six-key
scenario/strategy/draw/replication/perspective/subgroup envelope from the
**existing D2 `dapane-d2-voiage/0.1` contract** and validates its
domain-separated digest, native cost/outcome pairing, exact values, unit,
economic basis and price year. It accepts **equal-weight draws only**. It
carries the independent reference and never evaluates EVPI locally.

The existing Voiage-native entry point is
`voiage._runtime.compute_evpi`, which dispatches to
`voiage._core.compute_evpi` in Rust. See the upstream
[method source](https://github.com/edithatogo/voiage/blob/main/voiage/_runtime.py)
and [native code](https://github.com/edithatogo/voiage/blob/main/rust/crates/voiage-numerics/src/evpi.rs).
No Dapane implementation of an EVPI/EVPPI/EVSI estimator is introduced.

## D3.2 — Method and evidence-maturity limits

| Area | Evidence state | Permitted interpretation |
| --- | --- | --- |
| Dapane D1 native paired costs | Candidate in PR #23, not accepted by this D3 work | Test input identities and cost-model execution separately |
| D2 Voiage six-key interchange | Standalone Python contract candidate | Preparation of already-valued net benefit; not clinical valuation |
| Voiage native EVPI method | Rust method exists upstream, selected wheel and native execution **not run for this example** | Only a *separately observed* result with pinned artifacts and independent expectation can close this question |
| Voiage simulation-outcome `O01–O08` | [Pending upstream](https://github.com/edithatogo/voiage/blob/main/conductor/tracks/simulation_outcome_boundary_20261107/index.md) | Do not label Dapane's mapping as an accepted upstream generic adapter |
| Innovate adoption and capacity feedback | Externally supplied D2 trajectory only | No fitted forecast, native Innovate execution, real population or observed capacity |
| Paignia finite-game input | Native static profile exists, D2 emits construction blueprint only | No native Paignia validation, game application or solver result |
| Measurement evidence | Invented two-draw analytic reference | No empirical time distribution, scientific posterior, sampling likelihood, EVSI or research cost |
| Alternative perspectives | Explicitly separate resource-cost, hospital cash, public outlay, tariff/funding, transfer and societal viewpoints | Never relabel the same values as a different perspective; independently revalue the source model |

**Uncertainty:** `draw_id` denotes a shared epistemic-parameter vector; it must
not be swapped with a stochastic replication, reweighted from row position, or
treated as a patient. `replication_id`, `perspective`, `subgroup_id` and
strategy keys must survive end to end. Correlated model inputs have to be
provided by the external source; a shared name or RNG seed is not evidence of
valid pairing. Parameter uncertainty and patient heterogeneity are separate.

**Costs and decision welfare:** economic opportunity cost, public expenditure,
cash savings, tariffs/funding and domestic excise/GST transfers are different
constructs. Their unit, price basis, perspective, inclusion and source-rights
limitations must remain explicit. Cost differences do not automatically become
clinical effects or strategic utility; Paignia payoff mapping is owned by the
application, Voiage owns VOI numerics.

**Population impact:** the 10 AUD per-assay reference has *no* declared patient
population, observation window, adoption forecast or discounting. Multiplication
by volumes without model provenance would be an unsupported population EVPI
claim. Measurement benefits must be offset by its real cost and may be less than
EVPI; no positive ENBS is asserted.

## D3.3 — Executable installed-native paths and rollback

`study.py` includes `run_static_without_providers`: it invokes an **explicit
absolute, sha256-pinned native Dapane CLI** using the already-supported
`dapane evaluate -` protocol in an environment with no Python provider search
path. It does not import or invoke Voiage, Innovate, Paignia or a Dapane
alternative numerical implementation. Nonzero exit, timeout, invalid output,
unexpected method or binary digest fail closed. **Only a fake-CLI synthetic
subprocess test is locally executed so far**; a real pinned binary must be run
and its output independently checked by the receiving owner.

To reproduce local synthetic/negative tests (Python 3.12–3.15 standard library):

```sh
cd adapters/decision_provider_d2
python -m unittest discover -s tests -v
python -m compileall -q bridge.py study.py native_voiage.py tests
```

To run **real** Voiage *after* qualifying and installing the selected artifact
in a **separate interpreter environment**:

```sh
# Do not invent or guess the values below: retrieve them from an accepted
# source-to-wheel receipt. Voiage is separately installed in this environment.
python native_voiage.py \
  --prepared /absolute/path/to/prepared-d3.json \
  --wheel /absolute/path/to/accepted-voiage.whl \
  --wheel-digest sha256:<independently-verified-wheel-sha256> \
  --revision <exact-reviewed-provider-commit> \
  --output /new/evidence/location/voiage-native-evpi.json
```

The runner checks the wheel bytes, archive members, imported module origin and
every installed Voiage package member before calling its *native* EVPI. It
cannot derive/attest an accepted commit-to-wheel binding by itself: retain and
independently check the provider build receipt, native-extension hash, real
execution log and host/environment provenance. A genuine native result should
then be checked using `verify_native_evpi_receipt` against the independently
derived 10 AUD reference for **the identical four already-valued cells**. A
matched receipt is still `verified_declaration_not_installed_acceptance`
until its execution and selected source/artifact identity are independently
adjudicated.

Run an **installed actual Dapane CLI** separately through
`run_static_without_providers` with an exact, previously selected executable
SHA and the unchanged native point contract. Retain binary SHA, request bytes,
native JSON report, output digest, source revision and comparison to independent
expected totals. Disable all optional decision providers. The default static
valuation must remain operational, without auto-selection or any runtime
dependency on those providers. A failed optional integration must not overwrite
or silently reinterpret an earlier static report.

### Exact acceptance blockers

1. **D1/PR23** needs received and accepted native cost-model evaluation evidence
   against its actual source, not a reconstructed JSON-shaped fixture.
2. The Dapane **sole integrator** must approve the new adapter namespace and
   add explicit D2+D3 hosted/installed coverage; root workflow, dependency pins
   and Conductor registry remain under their existing owner.
3. Execute and independently inspect the pinned Voiage-native consumer and
   numerical oracle. A preparer- or user-declared checksum alone is not proof
   of real execution. Voiage's pending generic outcome track remains separate.
4. Execute a reviewed Innovate native scenario and a Paignia native
   `GameSpecification::validate_for_profile` consumer against their accepted
   exact revisions/artifacts; declare unsupported components distinctly.
5. Run real static Dapane CLI with all optional decision providers unavailable
   and independently check a native report; preserve rollback evidence.
6. Maintain required privacy/security/offline and scientific/release gates.
   Do not mark D2.1–D2.4 or D3.1–D3.3 `[x]` based on local synthetic tests.

### Read-only source-status snapshot

At the **18 November 2026** inspection, Dapane main was
`0658d94ad772023a0185a000b5254f9c2f4a63a9`, D1 PR #23 was still
`d994e638685c4c48d22d5f474d03fe9261efa546`, and D2 PR #29 was
`b796be5633ee828601787f1937e77d743ac6062e` before this D3 child.
Voiage's generic outcome `O01–O08` tasks were still marked pending and
Paignia's current consumer manifest contained **no real application receipts**.
These are dated observations, not claims about later merge or release states.

**Delivery disposition:** bounded D3.1 evidence-design logic and D3.2 full
methodology/limitations are implemented. D3.1's *actual* Voiage numerical use
and D3.3's actual three-provider installed execution are **not completed**.
No external research study, clinical dataset, journal submission, cohort source,
real patient information, software release, merge or public registration occurred.
