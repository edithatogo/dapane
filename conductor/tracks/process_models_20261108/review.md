# X1 lane review

Review type: author review, with no additional worker or independent-review claim.
Base: `e34f87c9df39a2132fecee142431cdeefb732471`.

## Findings and disposition

1. **Blocking: recovered source has no exact-head execution evidence.**
   The environment became unavailable before commit/push. Reconstructed source,
   tests and fixtures must be compiled, formatted and rerun (X1-IR-00). Historical
   local results are retained without attaching them to the recovered SHA.
2. **Blocking for native import: Rust4PM dependency qualification remains open.**
   Mailweft's pinned main resolves the published affected dependency graph and
   issue #4 is open. No native import surface or bypass was added.
3. **Adoption gap: root test discovery excludes the separate package.**
   Documented explicitly and assigned to the integrator as X1-IR-01. Existing
   workflow success cannot qualify it.
4. **Scope/evidence distinction corrected.**
   Historical root runtime verification does not cover the new adapter. Track
   records point to this lane's own evidence and keep X1.2/X1.3 incomplete.
5. **Local test/compiler and style findings fixed before outage.**
   A duplicate-edge test needed a separate clone to satisfy borrowing. Ruff
   import ordering and UTC alias findings were fixed. Those fixes are reflected
   in recovery, but final-head tools must check them again.

## Reviewed invariants

No source, manifest, shared schema, root CI or numerical path outside this track
and the reserved namespace is changed. The package has no dependency or raw
decoder and no monetary arithmetic. The validated result owns an immutable
snapshot; contextual edges cannot multiply use. Missing/censored quantities do
not become zero, elapsed time or a window endpoint. Unsupported correction,
transfer and non-observed selection cases fail visibly. Source digests and
observed labels are caller declarations rather than verification certificates.

Unmodelled aliases, native parser fidelity and shared source/time projection
remain explicit limits. X2/X3, releases, merge decisions and upstream remediation
remain with their existing owners.
