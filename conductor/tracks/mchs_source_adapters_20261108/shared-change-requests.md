# Shared-change requests for the sole integrator

No shared files are edited by this lane.

## S1 — Central lifecycle reconciliation

The owned track records M1/M2 source work as `in_progress`, with exact-head
verification blocked. Update only its existing row in `conductor/tracks.md`
from `[ ] / new` to `[~] / in_progress`, preserving surrounding owner work:

Keep the existing track-link and requirement cells. Change that row's marker
from `[ ]` to `[~]` and its status cell from `new` to `in_progress`.

The unchanged Conductor validator must then pass on the integrated exact head.
This row change does not complete M2, M3 or the whole track.

## S2 — Explicit optional package qualification

Owned root: `adapters/mchs_sources/`. Import namespace: `dapane_mchs_atlas`.
It is a separate pure-Python transport package with no mandatory runtime
dependencies. Default native execution uses the exact installed Dapane wheel.
The setuptools build requirement is pinned to 84.2.1.

Add explicit checks through the existing shared CI/qualification mechanism:

1. Run Ruff check/format and all 34 lane tests against a qualified CLI.
2. Build/install the adapter wheel in a clean consumer with the same candidate
   Dapane native wheel; run the suite outside the checkout, then the default-native
   installed smoke test.
3. Retain exact adapter/native source and wheel/CLI identities. Include packaged
   `provider_pins.json` and verify source imports are not shadowing installation.
4. Run existing shared/native/interval/installed gates on the integration head.
   The lane does not add a core dependency, modify root packaging or touch CI.
5. Keep existing offline-security and publication gates. A queued run is not a pass.

The tests fail when the CLI is absent. New directories are not implicitly covered
by existing CI. Do not mark this capability qualified on unrelated workflow
success.

## S3 — Economic interpretation and future provider interfaces

Review the explicit outer-profile mapping: tariff uses native `charge`; funding
uses native `funding`; resource costs are a separate core 0.1 request; payments
are exact observation/model records without native valuation or aggregation.
This needs no new shared basis or schema field. Rich classification, rights and
provider metadata remain in the separate versioned envelope.

For later M3, coordinate upstream-owned exact exports:

- MCHS: serialize the existing acute Decimal result before any float boundary,
  with explicit classification/pricing/source context and no inferred NEP.
- Atlas: retain original exact source values and bind them to source snapshots;
  its currently normalized float amount cannot supply that precision.
- Preserve provider APIs, source restrictions and rollback pins; do not widen the
  candidate to official rates or installed providers without their evidence.

Publication/package legal payloads remain the release owner's work. No dependency
or runtime qualification is inferred from the selected project licence.
