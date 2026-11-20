# Perspective, transfer boundary and missing-adapter fallback

Dated 20 November 2026. This T3.2 record documents the synthetic fiscal adapter
and the expected consumer fallback. Installed consumer verification remains in
T3.3. [Fiscal contract](../../../adapters/decision_draws/CONTRACT.md)

## Perspectives

| Perspective | What enters the selected result | What stays out |
| --- | --- | --- |
| `health_system` | The required health contract supplies QALY flows and a threshold. NMB is the threshold times discounted QALYs, less discounted direct medical cost. | Enforcement and excise/GST lines are reported and listed as excluded from the selected result. |
| `public_finance` | Net public outlay is medical plus enforcement expenditure minus government tax receipts. | Omit `health` or set it to null. QALYs and NMB are null. |
| `societal` | NMB uses the required health contract and subtracts declared medical and enforcement economic costs. Domestic excise and GST net to zero. | Excise and GST are reported as transfers outside the selected resource cost. |

Schedules retain their row perspective and the report retains the full packet
key. Equity aggregation requires compatible packets for the same scenario,
comparison, draw, replication, perspective and valuation context. Each
`subgroup_id` has its own result row.

## Excise, GST and deadweight loss

Excise and GST are `discounted_tax_transfer` lines. A positive transfer gives
a positive government receipt and an equal negative household payer flow.
Negative transfers reverse those signs. The two legs use the same timing and
discount rate and sum to zero within the domestic boundary. Each tax type
requires an explicit line, including a labelled zero when known.

Deadweight loss, illicit-market substitution and broader compliance costs
belong in a separately specified economic model. The synthetic ledger admits
medical and enforcement resource lines and domestic excise and GST transfers.

## When Dapane is not installed

When the optional adapter is unavailable, the intended fallback is the
consumer's standalone method. Report Dapane-derived results as unavailable.
T3.3 still needs to exercise that behaviour in each installed consumer.

The inspected Tobac source at `891f79e07292b7754f78d7193130623bd5f9e243`
contains related functions in `src/tobac/health.py` and evidence-packet
handling in `src/tobac/interchange.py`. The originally planned
`economics.py` and `decision.py` paths are absent. T2.3 still needs to map
the relevant interface and run the synthetic NZ/AU parity fixtures.
