# assess canonical JSON dependency without changing hashes

[Specification](spec.md) · [Plan](plan.md) · [Metadata](metadata.json)

Potential replacement is custom canonical JSON writer, not Serde itself; Serde is already used.

Status: completed

The [optional v2 crate](../../../adapters/canonicalization_v2/README.md) is locally
qualified for detached fingerprints. Historical receipts use the retained v1 writer.
