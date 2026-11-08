# Synthetic fixture calculations

Every value, person, event and rate in this directory is synthetic. These
fixtures are small independent arithmetic references, not clinical evidence,
official fee schedules, observed workloads or provider-output parity tests.
The schema and executable acceptance tests determine which cases currently run.
Version `0.1` distinguishes `resource_use` from `activity_measure` on both use
and quote targets; valuation bases are `economic_cost`, `financial_cost`,
`funding` and `charge`. Numeric inputs are decimal strings or string-valued
numerator/denominator pairs, never JSON floating-point numbers. See the runtime
contract for the complete DTO and supported rounding/allocation policy.
Provider mappings and their immutable source revisions are recorded in
[`docs/provider-boundaries.md`](../docs/provider-boundaries.md).

Do not obtain the expected result by calling the implementation being tested.
Retain the hand calculation below and compare both the Rust and installed Python
surfaces against the same inputs and expectations.

## Fractional workforce duration

One synthetic worker contributes 20 minutes. An invented quote is AUD 90 per
hour. The exposure is exactly `20 / 60 = 1/3` hour, so its exact value is
`(1/3) × 90 = AUD 30`.

This tests a nonterminating decimal exposure. Storing `0.333333` hours would
change the quantity. Keep the conversion and multiplication rational until the
declared display/settlement step. A companion invented AUD 100/hour quote yields
exactly `100/3` AUD; the rounded amount requires a named rounding policy and must
not replace the exact value.

These examples do not determine annual paid hours, productive time, award
eligibility, overtime or whether a workforce rate already includes on-costs.
Those facts belong to the provider/plugin and rate release.

## Shared genomics batch

One synthetic assay batch costs AUD 100 and serves two specimens. Each specimen
also has an invented collection cost of AUD 10. The source ledger contains one
batch quantity of one, valued once at AUD 100, and two distinct collection uses
valued at AUD 10 each. Its total is `100 + 10 + 10 = AUD 120`.

With an explicit equal batch allocation, each specimen's view receives
`100 × 1/2 = AUD 50` from the batch plus its own AUD 10 collection cost. The
result is AUD 60 per specimen and `60 + 60 = AUD 120` in total.

The two batch allocation values sum to AUD 100. Adding the batch source line to
its allocation views would count the batch twice. Linking the
batch to two specimen objects does not create two batch uses. Unused capacity,
failed assays, controls and repeat samples require additional explicit inputs;
this tiny example assumes none of them.

## Activity-only funding

An invented activity measure is 2.50 units with an invented funding quote of
AUD 17.00 per activity unit:

`2.50 × 17.00 = AUD 42.50`.

No resource-use records are needed. The result belongs to the funding view and
does not imply a resource cost of AUD 42.50. The units and rates are synthetic;
they are not an official NWAU example, an NEP value or a qualification of the
MCHS classification/calculation engine. This case fails if a funding quote is
silently applied to a resource target or funding and economic cost are merged.

## Newborn screening: two infants and one shared batch

The demonstration programme has infants A and B, one specimen each, one shared
batch and one confirmation activity for infant B. All activities, durations and
prices below are invented for arithmetic verification.

| Source use | Quantity and invented rate | Source value | Allocation to A | Allocation to B |
| --- | --- | ---: | ---: | ---: |
| Collection for A | 5 minutes × AUD 2/minute | 10 | 10 | 0 |
| Collection for B | 5 minutes × AUD 2/minute | 10 | 0 | 10 |
| Shared batch | 1 batch × AUD 100/batch | 100 | 50 | 50 |
| Confirmation for B | 15 minutes × AUD 2/minute | 30 | 0 | 30 |
| **Total** | | **150** | **60** | **90** |

The programme has four distinct source uses. Its cost is
`10 + 10 + 100 + 30 = AUD 150`. Infant views satisfy
`60 + 90 = AUD 150`. The shared batch is counted once despite its links to both
infants/specimens. Confirmation belongs to infant B's pathway and remains a
distinct use; it is not another initial screen.

The fixture exercises event IDs, process/activity context and object links
without requiring a simulation engine. It is not a clinical screening model and
does not assert detection rates, prevalence, programme throughput, health
outcomes or cost effectiveness. An observed programme, static recipe or future
Kairos simulation can produce the same neutral use shape with different,
explicitly labelled provenance.

## Sub-cent allocation and conservation

The `dapane-exact-v0.1.0` method rounds each source line half-even at the policy
scale, then allocates each rounded pool by largest remainder. An invented AUD
0.05 pool split equally among objects `a`, `b`, `c` has exact shares of `1/60`
AUD. At scale two, flooring each ideal share gives AUD 0.01 each, with two cents
left to assign. The equal fractional remainders are resolved by ascending object
ID, giving `a = 0.02`, `b = 0.02`, `c = 0.01`. The total remains AUD 0.05 and the
residual is zero. The fixture deliberately supplies weights in `c, a, b` order
to distinguish the declared tie rule from input-order dependence.

Use exact values as the primary oracle and rounded values as a separate,
policy-specific oracle. The exact allocation share is a share of the rounded
pool; `pool_exact` separately retains the pre-rounding source value. This profile
does not expose a partial-allocation/residual policy.

Required negative cases include conflicting/duplicate source-use IDs, wrong
denominator units, incompatible target kinds, unknown object references,
overlapping included components and invalid/overallocated shares. A reference
result must preserve the use-to-quote and allocation-to-source lineage so a
correct total cannot conceal an incorrect explanation.

No test in this directory qualifies a live provider by itself. Real provider
adapters additionally need immutable provider fixtures, supported installation
evidence and a demonstrable execution through the provider's public interface.

## Files and executable checks

| Request | Independent reference |
| --- | --- |
| `workforce.json` | AUD 30.00 from exact `1/3` hour at AUD 90/hour; unattributed source value. |
| `genomics.json` | AUD 120.00; specimen views AUD 60.00 each; batch context object has zero direct value. |
| `activity-funding.json` | AUD 42.50 funding from activity only, with no resource records. |
| `newborn-screening.json` | AUD 150.00; infant A AUD 60.00 and infant B AUD 90.00; specimen/batch/confirmation context objects retain zero additional value. |
| `subcent-allocation.json` | AUD 0.05 split AUD 0.02, 0.02 and 0.01 by object ID. |

`expected.json` stores these independently specified exact and rounded values,
including source lines, object balances and allocation shares. It was not
generated from the Rust engine. Every request declares synthetic, public,
unvalidated provenance and invented AUD prices with economic price year 2026.

Run `python scripts/validate_contract.py` for schema/fixture checks. Add
`--cli target/release/dapane` to execute the compiled CLI and verify the expected
values, lineage, conservation, digest identities and semantic rejection cases.
See [`schemas/README.md`](../schemas/README.md) for the boundary between schema
and runtime validation.
