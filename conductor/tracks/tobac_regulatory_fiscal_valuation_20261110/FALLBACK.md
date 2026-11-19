# Perspective, transfer boundary and missing-adapter fallback

Dated 2026-11-20. This is the T3.2 record for the synthetic fiscal adapter. It
does not show that `tobac` or `voiage` imported a table.

## Perspectives

| Perspective | What enters the selected result | What stays out |
| --- | --- | --- |
| `health_system` | Discounted `health_system_direct_cost` lines, then health NMB when a health contract is present | Enforcement resource lines and excise/GST transfers. They are reported and listed as excluded. |
| `public_finance` | Medical plus enforcement resource cost, minus government receipts | Health NMB. `health` must be null. The result is net public outlay. |
| `societal` | Medical plus enforcement resource cost. Domestic excise and GST cancel inside the boundary. | Adding a transfer to societal resource cost. The adapter rejects an unlabelled addition. |

A schedule row may name its own perspective. That tag does not replace the
packet key. Equity aggregation refuses to mix scenario, strategy, draw,
replication or perspective, and it keeps each `subgroup_id` on its own row.

## Excise, GST and deadweight loss

Excise and GST are `discounted_tax_transfer` lines. A positive amount is a
government receipt and an equal household payer outflow. Their sum inside the
domestic boundary is zero. The adapter does not calculate excess burden,
deadweight loss, illicit-market substitution or a compliance-cost wedge. Those
effects need an explicit resource line from `tobac`. Omitting a known-zero
excise or GST line is not a zero.

## When Dapane is not installed

`tobac` keeps its own valuation code. At `891f79e07292b7754f78d7193130623bd5f9e243`
that code is not in `src/tobac/economics.py` or `src/tobac/decision.py`. The
related functions are in `src/tobac/health.py`, and `src/tobac/interchange.py`
handles evidence packets. Absence of this adapter must not be filled with zeros
or with a copied formula. `voiage` likewise keeps its own value-of-perspective
and credal calculations until a later installed-consumer check joins the
six-key table.
