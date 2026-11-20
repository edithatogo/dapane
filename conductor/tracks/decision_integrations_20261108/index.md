# Uncertainty and decision-library integration

Track: `decision_integrations_20261108`

Status: in_progress

Connect correctly paired cost outputs to Voiage, Innovate and Paignia while retaining their existing ownership of decision methods, adoption mechanisms and strategic models.

- [Specification](spec.md)
- [Implementation plan](plan.md)
- [Metadata](metadata.json)
- [Track registry](../../tracks.md)
- [Roadmap](../../roadmap.md)

Requirements: RQ-11, RQ-02, RQ-03.

The D2/D3 adapter suite passed 78 synthetic contract tests. Native replays
reproduced the Innovate capacity and Paignia payoff examples, and the standalone
Dapane CLI reproduced the newborn-screening total. On 20 November the installed
Voiage 3.1.0 wheel returned the staff-time EVPI of 10 per assay. Paignia
`44bebdae9ca53a113681041e8fe5dcc16f57b918` selected action B at utility 20.
Innovate main `fd7e259bb9a685d620f80907c6815d4837da3e53` does not expose the adoption operation, so its price-feedback case stays blocked. See the
[19 November verification](VERIFICATION.md#decision-provider-evidence-review--19-november-2026)
and the [20 November execution](VERIFICATION.md#installed-voiage-execution--20-november-2026).

- [Adapter and contract](../../../adapters/decision_draws/README.md)
- [Verification and evidence limits](VERIFICATION.md)
- [Review and fixes](REVIEW.md)
- [Exact-SHA integration handoff](HANDOFF.md)

- [Owner quality repair and executed evidence](owner-quality-20261115.md)
- [D2/D3 optional provider preparation adapter](../../../adapters/decision_provider_d2/README.md)
- [18 November D3 preparation dossier](../../../adapters/decision_provider_d2/D3-EVIDENCE.md)

The integrator has reconciled the central registry and added standalone CI for
`adapters/decision_draws/` and `adapters/decision_provider_d2/`. Production,
security and release qualification remain open.
