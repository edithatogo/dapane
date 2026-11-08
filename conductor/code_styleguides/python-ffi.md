# Python and native-interface conventions

Python provides typed input construction, orchestration and convenient result
access around the shared Rust engine. Keep formulas in Rust and use Polars/Arrow
at optional table boundaries. Avoid implicit float conversion of decimal strings
or numerator/denominator values.

Use Ruff for Python lint/format once configured. Keep imports lightweight and
optional adapters isolated. Map native failures to stable public error types.
Test installed distributions in clean consumers; importing local source does not
verify wheel contents, ABI compatibility or native-library resolution.

R may call Rust directly through extendr; it need not depend on the C ABI. Julia
uses a separately qualified versioned C ABI. Wrappers must respect their host's
GC, lifetime, threading and missing-value rules.

The C ABI uses opaque handles or clearly owned buffers, explicit sizes and errors,
version negotiation, panic containment and matching allocation/free operations.
Rust internal layouts are not a public ABI. Zero-copy is a qualified optimisation,
not a requirement that overrides ownership or exact numeric semantics.

Use the same independent fixtures across Rust, Python, R, Julia and any later
WASM surface, with explicit tolerances only where the numerical method permits.
