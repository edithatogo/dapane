# Conductor: assess canonical JSON dependency without changing hashes

## Verified current state
- Workspace dependencies already include `serde` derive and `serde_json`; `crates/dapane-core/src/json.rs` uses a typed `serde::de::Visitor` to reject duplicate object keys and `serde_json` for conversion.
- `write_canonical` recursively sorts JSON object keys and serializes scalars with `serde_json`; `digest` hashes the resulting bytes with a domain prefix. A separate `encoded_size` writer enforces the 4 MiB typed-request limit.
- `serde_json_canonicalizer` is available elsewhere in this ecosystem, but **not proven byte-compatible with Dapane's historical canonical form** (UTF-16/JCS key ordering and ECMAScript numeric representation can differ). This is a candidate for a constrained comparison, not a drop-in replacement.

## Required decision
Freeze present canonicalization as `dapane-canonical-v1` until golden hashes and independent references establish equivalence. A new algorithm must use explicit version negotiation and separate domain tags, preserve v1 verification of old receipts, and avoid silently changing user-visible hashes. Keep duplicate-key rejection, typed validation, byte limits, explicit rounding and source/provenance invariants. Do not introduce a dependency if it only reproduces already-tested code at higher operational cost.

## Ownership
Only a proposal to the existing sole Dapane integration owner. No edits to arithmetic, provider/consumer contracts, shared manifests/locks, CI or releases. No assertions of runtime acceptance from planning.
