# External benchmark protocol

Registered before the full retrieval on 20 November 2026. Initial readback used
two records to confirm endpoint and exact-text field availability. The selected
public CMS Medicare FFS inpatient geography/service publication is 2024, dataset
2941ab09-8cee-49d8-9703-f3c5b854e388. The eligible classification is DRG 470. It
has one annual definition and non-identifying geographic aggregates. Keep the
national row separate and analyse the 50 states and DC. Retain source hashes.
Record all absent geographies and blank or invalid amount or discharge fields.
A missing public cell remains unknown. Retain the publisher's coverage limits.

The quantity is discharges and the rate is the mean Medicare payment per
discharge. Reconstruct local implied Medicare payments and transport the
published national rate to each state's discharges. Independently reproduce
both via exact rational arithmetic with half-even cent rounding. Compare
valuation, population, weighted absolute differences and relative errors.
The reconstruction uses already-rounded published means and the national rate
includes the analysed states. This is an aggregate funding/transferability
check without independent cost-account verification or patient-level claims.
Record the source mapping effort and available dimensions without inferring
human effort, causal or economic-cost claims.

## Executed results

The 51 published state/DC rows contain 64,419 discharges. Each row has a usable
count and mean. No state in the selected frame is absent. The independent
Fraction oracle and native CLI matched to the cent on all 102 valued lines.
The state-specific reconstruction totals USD 922,586,578.00. Applying the
national mean to the same state counts totals USD 922,586,577.98. The USD 0.02
gap reflects published precision and rounding. The sum of absolute state
differences is USD 149,616,649.66, or 16.2171% of the state-rate reconstruction.
The pooled rate is higher for 35 states and lower for 16. The national match
does not transfer to state-level use.

The source mapping needed a documented group, one population definition,
state codes, discharge count and one mean payment field. The first pass
incorrectly rejected a published seven-decimal mean under a six-decimal
validator. The review changed that bound to the native 36-decimal limit and
reran the same selection. The result holds without imputing a value or changing
the eligible geography frame. The available aggregate fields cannot establish
physical resource use, individual payments, costing accuracy, case mix within
the group or independent transport to a new site. The record measures the
mapping and coverage steps. It contains no human effort study.

## Reproduce

Download the public aggregate API response to a private working directory,
preserve its hash and run the locked release CLI through the repo-local Python
3.15.1 environment. The [receipt](evidence/external/cms-funding-v1.json) retains
the input, executable and report digests and the aggregate comparison. The
source rows stay with CMS. Independent oracle totals and the rerun were
identical on the recorded host.

    .venv/bin/python benchmarks/static/cms_funding_transport.py \
      --source /absolute/cms-2024-drg470.json --cli /absolute/dapane \
      --out /absolute/cms-funding-result.json

- [U.S. government catalogue and 2024 data endpoint](https://catalog.data.gov/dataset/medicare-inpatient-hospitals-by-geography-and-service-d713e)
- [CMS geography and service data dictionary](https://data.cms.gov/resources/medicare-inpatient-hospitals-by-geography-and-service-data-dictionary-0)
- [CMS methodology and coverage](https://data.cms.gov/resources/medicare-inpatient-hospitals-methodology)
