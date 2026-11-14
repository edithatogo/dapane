# Compatibility, identity and rollback

The implementation remains an unpublished `0.1.0` package candidate. Its original
wire contract `0.1` / method `dapane-exact-v0.1.0` remains supported unchanged.
The explicit [capacity profile](contract-v0.2.md) adds wire `0.2` / method
`dapane-exact-v0.2.0`. Package and contract versions are independent. These
identities have different responsibilities; a package version alone does not
identify a price release or an economic method.

| Identity | Meaning | Change rule |
| --- | --- | --- |
| Engine/package version | Code and packaging implementation | Pin the source revision and `Cargo.lock` for a reproducible source build. Published binaries will need their own artifact identity. |
| `schema_version` | Accepted fields, types and meanings | Accepts `0.1` and `0.2` explicitly. Capacity records are rejected in `0.1`. Unknown fields and versions fail; there is no implicit conversion. |
| `method_version` | Numerical and rounding semantics | Changed financial semantics require a new method identity and reference cases; retain prior expected results and explain differences. |
| Policy ID/version | Caller-selected perspective and valuation assumptions | Never silently substitute another policy. Contract 0.1 supports only its explicit fields and named rounding method. |
| Source ID/version/digest | Supplied source snapshot | Corrections create a new source version and a new run. A supplied digest is preserved; the core does not retrieve external content to verify it. |
| Model ID/version | Producer process model context | Preserve independently of valuation, so price-only revaluation need not change the process model. |

The input digest preserves supplied decimal spellings and canonicalizes collection
order. The output digest covers the complete report except its own digest field.
Neither digest proves the truth of input data or replaces a signed release record.
The exact algorithm and normalization are in the [contract](contract-v0.1.md).
The [capacity contract](contract-v0.2.md) defines its separate remainder and
unknown-state semantics. The five original fixture input/output digests remain
unchanged. Typed Rust `Request` literals need the new empty
`capacity_allocations` vector; pre-1.0 source compatibility is not asserted for
struct construction. JSON/CLI/Python full-pool inputs remain compatible.

## Namespaces and extensions

Use stable provider-owned identifiers when exchanging data, for example
`workforce:staff_time` or `newborn:collection`; the example prefix is a naming
convention, not a globally registered vocabulary. Units and components compare
exactly. Adapters must map their vocabulary deliberately; similarly named units
are not automatically equivalent. The bundled synthetic fixtures use identifiers
scoped to their own request.

There is no arbitrary `extensions` bag or dynamic native plugin ABI in 0.1.
Do not hide unsupported intervals, retractions, source eligibility, uncertainty
draws, capital treatments or clinical assumptions inside an unrelated string.
A provider may retain a source artifact through a pinned locator/digest, but a
calculation needing unsupported semantics must fail or be explicitly transformed
under a separately qualified adapter contract.

Typed packages and versioned data adapters are the intended plugin mechanism.
Workforce owns employment/rate rules; genomics owns recipes and batch assumptions;
MCHS owns classified activity and funding rules. Their package pins and public
APIs are not widened by Dapane's Python support range. See the
[source mappings](provider-boundaries.md).

## Installed interfaces

The native crate and CLI do not require Python. The Python distribution has no
runtime Python-package dependencies and calls the same Rust kernel. Native wheels
are interpreter-specific; no ABI3, PyPy, free-threaded Python, macOS, Windows,
ARM or manylinux redistribution support is claimed by the initial Linux tests.
The [verification record](runtime-verification.md) identifies actual platforms.

R, Julia and a stable C ABI remain planned. No user is expected to install Python
to use a future direct R/Rust binding or Julia native artifact. Arrow/Parquet,
process import, Kairos and operational service adapters remain optional.

## Migration and recovery

There is no earlier released Dapane runtime to preserve, and no existing provider
entry point is replaced by this change. Consumers can continue using their
provider while an adapter is qualified. Keep historical workbooks, official
reference inputs and independently calculated expected results in their owning
repositories with their access restrictions intact.

For a candidate evaluation, preserve the exact input JSON, report, engine source
revision, lockfile, toolchain and Python wheel identity. To roll back an experiment,
restore that candidate artifact and inputs and verify its recorded output digest.
Do not force a historical run through a corrected method while retaining the old
method label. A later migration must retain an explicit old-version path until
affected consumers have qualified the new result.

No repository should be archived based on these synthetic tests. Real provider
integration, compatibility/rollback evidence and review of unique assets remain
release/consolidation work. A project licence and registry identity are also
unresolved release prerequisites; the workspace packages set `publish = false`.
