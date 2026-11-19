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

Capability status: bounded synthetic native checks pass at the exact corrected
source recorded below. Production/provider qualification and security/release
gates remain separate; the whole track is not complete.

- [Adapter and contract](../../../adapters/decision_draws/README.md)
- [Verification and evidence limits](VERIFICATION.md)
- [Review and fixes](REVIEW.md)
- [Exact-SHA integration handoff](HANDOFF.md)

- [Owner quality repair and executed evidence](owner-quality-20261115.md)
- [D2/D3 optional provider preparation adapter](../../../adapters/decision_provider_d2/README.md)
- [D3 local preparation evidence and open gates](../../../adapters/decision_provider_d2/D3-EVIDENCE.md)

The integrator has reconciled the central registry and added standalone CI for `adapters/decision_draws/` and `adapters/decision_provider_d2/`. Later provider phases (`D2.1`–`D3.3`), installed Voiage/Innovate/Paignia execution, and production/release qualification remain open.
