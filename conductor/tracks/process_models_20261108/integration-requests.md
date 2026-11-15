# X1 requests to the sole integrator

Owner: Dapane — Release assurance and consolidation, chat
`6af8e445-ffd4-83ec-8e51-ff6b596f11b1`.

This lane owns this track and `adapters/observed_events/`, the namespace reserved
by [coordination PR #20](https://github.com/edithatogo/dapane/pull/20).
The local pre-outage candidate used `adapters/observed-import-contracts/`;
no work under that path was published. Recovery adopts the reserved path.
Shared core/CLI/Python, schemas, root manifests/lock/CI, registry and root docs
remain untouched.

| ID | Concrete request | Reason and gate |
| --- | --- | --- |
| X1-IR-00 | Repeat the package checks, formatting, fixture auditor and Conductor checks on the exact recovered head before acceptance. | The local environment failed before commit/push. Source/test/fixture recovery is not byte-verified against that lost checkout; historical local results do not qualify the recovered commit. |
| X1-IR-01 | Add explicit package `--manifest-path adapters/observed_events/Cargo.toml` and fixture-audit commands to CI. If instead adopting it into the root workspace, remove its nested `[workspace]` and regenerate root lock in the same reviewed change. | Root cargo commands do not discover the package. It has no external dependencies. Keep required checks and offline security gates. |
| X1-IR-02 | Consume the existing Mailweft owner's qualified Rust4PM/quick-xml revision and exact-head provenance, licence, advisory and native-OS evidence. Separately qualify Dapane's raw XES/XML and OCEL JSON input paths. | Mailweft issue #4 is open. Email/JSON qualification would not automatically establish XML import safety. No parallel remediation or advisory ignores. |
| X1-IR-03 | Connect the qualified native parser under the proposed mapping while retaining the full native model/source. Run actual raw fixtures and complete schema/round-trip tests. | Preserve typed attributes/history, E2O/O2O qualifiers, native IDs and source timestamps. Reject duplicate members/identities, unknown meaningful constructs and malformed data atomically. Bound bytes/decompression and disable external entity/schema resolution. |
| X1-IR-04 | Decide a separately versioned import/assertion manifest and shared pre-valuation projection. Specify timestamp/service-date policy, source mapping revision and paired-event lineage. | Core Event has a date and ordinary Usage has one event context. Do not truncate richer source data, place new semantics in unrelated strings, or silently change strict schemas. Occupancy is not uniform-calendar-day exposure. |
| X1-IR-05 | After qualification, supply explicit source refs, quote selection and allocation to the unchanged exact core. Keep missing/censored/transfer cases blocked absent a separately qualified policy. | No monetary arithmetic exists here. Preserve per-generated-segment half-even rounding and use identities under price-only revaluation; context does not infer quantities or allocation. |
| X1-IR-06 | Reconcile registry/root evidence pointers during integration. | Track remains in_progress, matching the untouched registry. X1.1 specifies a bounded contract; X1.2 is blocked and X1.3 remains partial. X2 and X3 stay pending. |

The required native acceptance includes exact/conflicting duplicate IDs,
duplicate JSON members, reordering, offset/missing-time handling, all censoring
states, incomplete quantities, many-to-many graphs and native attribute/history
fidelity. Synthetic prepared cases are inputs, not evidence that parser gates pass.

No merge, publication, additional worker, upstream write, credential or
infrastructure change is part of this handoff.
