# Rust conventions

- Use typed records and explicit enums for units, valuation bases, evidence
  status and errors; avoid unqualified floating-point `cost` fields.
- Keep pure numerical/domain-neutral code independent of Python, R, Julia,
  HTTP, database, simulator, table-engine and ontology-reasoner crates.
- Prefer established exact decimal/rational and date implementations after
  qualifying precision, range, denominator and serialization requirements.
- Make overflow, missing input, unsupported precision, invalid dates and unit
  mismatch explicit `Result` errors. Do not panic across a public FFI boundary.
- Separate unrounded quantities/results from policy-governed rounded values.
- Avoid hidden global state, implicit current dates, source updates and RNGs.
- Document invariants and ownership, especially for allocation and FFI. Add
  unsafe code only with a bounded justification and lifetime/ownership tests.
- Keep optional integrations behind crate/feature boundaries. No implicit GPU
  or native process-plugin runtime in the default scalar path.
- Use rustfmt and appropriate Clippy checks when the Cargo workspace exists.
  Verify independent reference cases and meaningful negative/property cases.
