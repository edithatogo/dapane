# Implementation and admission plan

- [ ] Check live integration ownership and overlapping PRs; freeze current `canonical` fixtures and domain-separated digest bytes at exact main SHA.
- [ ] Evaluate `serde_json_canonicalizer` against the existing `write_canonical` on Unicode UTF-16 vs UTF-8 ordering, nested objects, `-0`, powers of ten, exponent formatting, floats, integer bounds, escaping and duplicate-key rejection; use independent RFC 8785 fixtures.
- [ ] Compare conformance, performance, transitive dependencies, MSRV, advisories, and API safety; record **no-go** if evidence does not support replacement.
- [ ] For a go result, propose versioned v2 behind an optional adapter, keep v1 byte-for-byte, test cross-language Python CLI contract parity, historical hash validation and source/rounding invariants; do not change core logic through this lane.
- [ ] Run exact-head locked Rust build/test/clippy, available independent references and central offline-security gate; integrator reviews and owns merge.
