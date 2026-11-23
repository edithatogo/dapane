# Optional v2 report fingerprints

Use the standalone Rust crate to generate a portable fingerprint for a Dapane
point or capacity report. Callers select the profile explicitly. The function
evaluates the supplied request through Dapane's strict native parser and returns
the native output digest alongside a detached v2 fingerprint.

```rust
let fingerprint = dapane_canonical_v2::fingerprint_report(
    dapane_canonical_v2::PROFILE,
    request_json,
)?;
```

The fingerprint is SHA-256 of the bytes `dapane:report:canonical-v2\n` followed
by the UTF-8 JCS serialization of the complete native report, including both
native digests. Store the `dapane-canonical-v2` profile name with the resulting
`sha256:` value. Use the original input and output digests to verify existing
valuation receipts. The adapter rejects raw JSON numbers other than integers
in the inclusive range −9,007,199,254,740,991 to 9,007,199,254,740,991.
Decimal amounts and rational components remain exact strings. [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html#section-3.1)

The adapter uses `serde_json_canonicalizer` 0.3.2 and its `ryu-js` dependency
within its own locked graph. The root workspace, CLI and Python package
continue to use their existing v1 interfaces.

## Verification

```sh
cargo test --manifest-path adapters/canonicalization_v2/Cargo.toml --locked --offline
cargo clippy --manifest-path adapters/canonicalization_v2/Cargo.toml --locked --offline --all-targets -- -D warnings
cargo deny --manifest-path adapters/canonicalization_v2/Cargo.toml --locked --config deny.toml check -s
```

On Rust 1.99.1 and aarch64 macOS, the native CLI and a fresh CPython 3.15.1
wheel built from the same core source produced byte-identical reports for the
five original point fixtures and the known-capacity fixture. The five
historical input/output digests matched the recorded values. The native
contract suite also checked exact values, rounding, source identity and
allocation. [Historical digests](../../fixtures/genomics-capacity/v0.1-digests.json)

The fingerprint tests use independent Node.js 26.13.1 reference values. The
reference sorted object names by UTF-16 code unit, preserved array order,
serialized safe scalars with `JSON.stringify`, and hashed the selected
domain and bytes with `node:crypto`. All six fingerprints matched. Three
unit tests cover Unicode ordering, exact strings, unsafe numbers and strict
request/profile rejection. The dependency check passed with one warning for
an unused licence allowance in the isolated graph.
