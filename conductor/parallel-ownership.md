# Parallel roadmap ownership and integration

Owner instruction recorded **15 November 2026**. This is the coordinating record
for Dylan's seven existing Pro ChatGPT workstreams. The existing Dapane integration
and release owner remains the **sole integrator**. This record creates no worker,
chat, implementation track, package release or capability claim.

## Pinned live baseline

The initial live inspection was **15 November 2026, 14:53 AEST (04:53 UTC)**.

| Surface | Observed identity and state |
| --- | --- |
| Repository | `edithatogo/dapane` |
| Main | [`e34f87c9df39a2132fecee142431cdeefb732471`](https://github.com/edithatogo/dapane/commit/e34f87c9df39a2132fecee142431cdeefb732471) |
| Main tree | `c07a6b2589b9d665f619f5d977d66e513180bab4` |
| Release owner | Existing [PR #17](https://github.com/edithatogo/dapane/pull/17), head `a4ddde7ae7a799e37a5d594cde9c195ff057bc5e`, tree `740c1f379e69db746a5d56ec7212e7676924b473`; open and unmerged |
| Lane PRs | None published at this initial inspection; PR #17 was the sole open PR. This is a dated observation, not a claim about subsequent submissions. |
| Archived prerequisites | Setup, core contracts, Rust kernel and Python/two consumers are incorporated on main. Their accepted implementations and historical records remain preserved. |

Main's ordinary Runtime, provider, Conductor, Privacy and CodeQL checks passed.
Its [offline security run](https://github.com/edithatogo/dapane/actions/runs/43664377890)
remained queued. PR #17 retains its exact-head qualification and unresolved gates
in its description and
[release handoff receipt](https://github.com/edithatogo/dapane/blob/a4ddde7ae7a799e37a5d594cde9c195ff057bc5e/docs/release-handoff-2026-11-15.md).
PR #17 is not a released package or a merged prerequisite for the optional lanes.
The reviewed shared numerical interfaces are identical on the pinned main and
release heads; release packaging and assurance changes remain with their owner.

Workers must refresh main, open PRs, review threads and published path claims
before editing or submitting. Record their actual base and tested heads. Never
overwrite a newer owner claim or assume this snapshot remains current.

The subsequent [seven-PR intake](roadmap-intake-2026-11-15.md) records the
published lane heads, their existing handoffs, accepted namespace reconciliation,
integrator-owned registry/CI changes and actual execution limits. The original
baseline above remains historical evidence; it is not the latest PR inventory.

## Exclusive ownership

Each row represents one existing worker, identified by its bounded lane rather
than an invented person or chat ID. The joint decision/fiscal lane owns two
existing track directories. **Seven workers therefore cover eight tracks.**

Each worker owns its listed `conductor/tracks/<id>/` directory and new files under
the reserved roots below. Those roots are reservations, not scaffolding or evidence
that a package already exists. Keep lane-specific source, tests, fixtures,
contracts, dependency proposals and evidence together there.

| Lane | Existing track and authorised slice | Reserved new-file roots |
| --- | --- | --- |
| Newborn synthetic | [newborn_screening_20261108](tracks/newborn_screening_20261108/index.md): N1.1–N1.3 and N2.1–N2.3. Preserve the already qualified N2.1 example. | Published PR #22 claim: `fixtures/newborn-synthetic/` and the single new `tests/python/test_newborn_synthetic.py` file. |
| MCHS and atlas | [mchs_source_adapters_20261108](tracks/mchs_source_adapters_20261108/index.md): M1.1–M1.3 and M2.1–M2.3. | `adapters/mchs_sources/` |
| Reporting JSON-LD/SHACL | [reporting_profiles_20261108](tracks/reporting_profiles_20261108/index.md): E1.1–E1.3 and E2.1–E2.3. | `adapters/reporting_profiles/` |
| Observed XES/OCEL imports | [process_models_20261108](tracks/process_models_20261108/index.md): X1.1–X1.3 only. | `adapters/observed_events/` |
| Polyglot | [polyglot_bindings_20261108](tracks/polyglot_bindings_20261108/index.md): B1.1–B1.2, then R B2.1–B2.3; the same owner retains the subsequent ABI/Julia branch. | Published PR #26 claim: `bindings/polyglot/`; this does not assign the parent `bindings/` directory. |
| Paired draws and Tobac fiscal | [decision_integrations_20261108](tracks/decision_integrations_20261108/index.md): D1.1–D1.3; [tobac_regulatory_fiscal_valuation_20261110](tracks/tobac_regulatory_fiscal_valuation_20261110/index.md): T1.1–T1.3. | Both published modules are under `adapters/decision_draws/`. |
| Independent synthetic static benchmarks | [frontier_benchmarks_20261108](tracks/frontier_benchmarks_20261108/index.md): F1.1–F1.3 and F2.1–F2.2. | `benchmarks/static/` |

The existing polyglot plan places **C ABI and Julia in B3.1–B3.4**, not B2.
Preserve those identifiers and Dylan's sequence: prepare the shared boundary,
qualify R, then address the separately qualified ABI/Julia branch with the same
owner. A minimal C consumer must qualify the ABI before Julia uses it. R does
not depend on C ABI, Julia or Python. No B3 or publication task becomes complete
by finishing B1–B2.

If an existing lane has already published a different dedicated namespace,
retain that work and send its exact path claim to the integrator for reconciliation.
Do not create a competing implementation or rename another owner's files. New
shared parent files, such as a common adapter index, remain integrator-owned.

The accepted published claims above replace the unused provisional newborn and
separate R/C ABI/Julia roots. The joint D1/T1 owner needs no duplicate fiscal
implementation under the unused `adapters/tobac_fiscal/` reservation. Owners
retain their published dedicated files when making subsequent fixes.

The **integrator exclusively owns**:

- `crates/dapane-core/`, `crates/dapane-cli/`, `crates/dapane-python/`, and
  `python/dapane/`, including their public APIs and existing tests.
- Shared `schemas/`, existing common fixtures/reference outputs, shared scripts,
  installed-artifact qualification and release capability/evidence machinery.
- Root Cargo manifests/lockfile/toolchain, Python packaging and shared dependency
  files, licence/notices, lint/dependency policy and all `.github/` CI/security.
- The Conductor registry, project context/root documentation, this ownership
  map, release/consolidation track and integration/merge decisions.

Files present at the pinned baseline outside a worker's own track remain
read-only to that worker, as do subsequent integrator-owned shared files.
New files outside its reserved roots require an integrator path decision. An
adapter-local schema can be proposed inside its own root; promotion into shared
`schemas/` requires a shared-change request. The bundle verifier recursively
registers shared schemas, so merely adding a conflicting schema there can affect
existing qualification.

The integrator will review and consume lane PRs, apply justified shared changes,
and reconcile central records. It will not implement or duplicate the seven
owners' scopes. External repositories retain their existing domain, ontology,
reporting, simulation and decision-method owners.

## Shared interfaces held stable

The implemented [point contract 0.1](../docs/contract-v0.1.md) and
[capacity contract 0.2](../docs/contract-v0.2.md) use the Rust
`evaluate_json` / `evaluate` entry points. CLI `evaluate` and Python
`dapane.evaluate_json` / `dapane.evaluate` call that same numerical implementation.
Exact numbers cross JSON as decimal strings or numerator/denominator string pairs;
structured diagnostics retain `code`, `message` and `path`.

The [interval envelope 0.1](../docs/interval-contract-v0.1.md), method
`dapane-intervals-v0.1.0`, remains a separate Rust/CLI surface with declared
uniform calendar-day exposure and **half-even rounding per generated segment**.
It does not infer irregular observed exposure or timezone-aware durations. Python
has no interval entry point. [PR #15](https://github.com/edithatogo/dapane/pull/15)
remains a preserved, closed alternative; the accepted resolution is in
[issue #19](https://github.com/edithatogo/dapane/issues/19).

Native requests/reports and [run-bundle 0.1](../docs/run-bundle-v0.1.md) reject
unknown fields. The implemented bundle qualification remains `synthetic_candidate`.
Planned concepts in the design document are not fields in these implemented
schemas. A lane must use a separately versioned record linked to unchanged native
input/output or bundle digests, or request a deliberate shared contract version.
It must not place new semantics in unrelated strings and claim native validation.

Production valuation/allocation remains in Rust. Independent test oracles must
derive expected results separately; they are qualification evidence, not another
production pricing implementation. Preserve source snapshots, native method IDs,
unknown values, unallocated amounts and historical digests. A changed quotation
changes the full native request identity even when physical-use identities stay
the same.

## Review of proposed integration interfaces

These are reviewed directions for the owners' bounded proposals, not acceptance
of implementations that have not yet been submitted.

| Lane | Compatible initial boundary | Required distinction or shared-change request |
| --- | --- | --- |
| Newborn N1–N2 | Construct synthetic versioned recipes producing ordinary 0.1 requests, or explicit 0.2 capacity requests, and consume native reports. Preserve infant/specimen/assay/batch relationships. | Keep denominator/window definitions, stage rules and perspective assumptions in a lane record. Preserve the existing 150 total and 60/90 views. Repeat/failure/partial-batch cases must not duplicate batch expense or distinct infants. Capacity thresholds require explicit inputs; no clinical defaults or real-programme claim. |
| MCHS M1–M2 | Emit `activity_measure` usage and matching quotations; use separate native policies/runs for cost and funding. Bind a mapping manifest to exact provider/classification/source revisions. | Classification edition is not price year. Preserve source rights separately from access labels. Native bases are economic cost, financial cost, funding and charge; tariff-to-charge meaning requires an explicit proposal, and observed payment is not silently treated as funding. Never manufacture resource usage from activity weights or turn missing rates into zero. |
| Reporting E1–E2 | Read unchanged reports or verified bundles and emit a separate versioned JSON-LD/evidence document with pinned UOGTO and standards_check identities and precise evidence locations. | Reporting coverage/applicability states are not native `complete` or source-validation states. Keep missing, partial, unassessed and justified not-applicable distinct. Do not insert JSON-LD into strict bundle 0.1 or copy upstream ontology/instrument ownership. Shared schema registration and any installed verifier API require integrator changes. |
| Observed X1 | Preserve an immutable imported event/object ledger and import manifest; produce native usage only under an explicit qualified quantity mapping. Apply quotations separately. | Native events hold dates, not full timestamps. Retain original timestamp/timezone/precision, lifecycle, censoring and corrections without loss. Native source evidence permits only synthetic/observed/derived. Preserve assumed/simulated distinctions externally. Object relationships do not infer duration, consumption or allocation. X1 adds no process simulator, PNML/BPMN execution or Kairos execution integration. |
| Polyglot | Thin R calls can use existing Rust JSON/typed APIs with exact values and diagnostics. Later C ABI and Julia expose the same selected operations. | Request workspace/package placement, dependencies, installed-host CI and capability registration. ABI proposals must define versions, lengths, ownership/free symmetry, errors and panic containment. Preserve the core/workspace unsafe restrictions; any required foreign-pointer boundary needs a separately reviewed wrapper design. No unexecuted host is qualified by Python or CLI parity alone. |
| Decisions D1 and fiscal T1 | D1 associates explicit indexed draws with unchanged requests and reports through a separate typed envelope. The same owner proposes one shared scenario/strategy/draw/replication/perspective/subgroup vocabulary for both tracks. | Reject missing/duplicate/mispaired draws. Outcomes have a separately identified model contract. Core has no tax-transfer, discounting, NMB or signed-flow method. T1 contracts and exact independent cases may proceed, while production numerical changes need an explicit method/profile request, sign/timing/rounding rules and a precision convention for subannual discounting. Later external decision providers remain D2/D3 and T2/T3 work. |
| Static benchmarks F1/F2.1–2 | Use synthetic cases, independent oracles and full recomputation through the unchanged evaluator; keep experiment inputs/results source-bound. | Distinguish mutations the contract rejects from plausible omissions/aliases/denominators that require independent evidence or cannot be detected from supplied data. F2.2 has no existing incremental engine: define the experimental cache unit and invalidation rule, prove equality to full recomputation including allocation dependencies, then measure it. Shared engine changes require a request; no speedup or frontier claim follows from the protocol alone. |

M1.1, E1.1 and X1.2 owners must inspect and pin their actual upstream dependencies
and rights. Historical ecosystem pins are starting references, not fresh evidence
of current releases. Optional dependencies must remain outside the default core
and ordinary Python import. Do not resolve the unpublished Dapane candidate by
name from a public registry; identify the exact built or retained artifact used.

## Shared-change requests and PR intake

Use the lane's existing PR body or a file in its own track for a shared-change
request. This is an implementation handoff to the integrator, not another user
approval form. Include:

1. Lane/task IDs, exact base and proposed head, reserved paths and relevant
   upstream source/artifact identities.
2. The requested shared paths/API/schema/dependency/CI changes and why the current
   interface cannot support the bounded case. Include a proposed diff or contract
   description without editing reserved shared files.
3. Compatibility, exact numeric/source semantics and optional-installation impact,
   plus the smallest independent positive and negative acceptance cases.
4. Commands actually executed, runtime/platform/tool versions, results and retained
   evidence. Label proposed, unavailable, failed, queued and skipped checks accurately.

The integrator handles PRs sequentially against live main. It checks ownership and
scope first, resolves shared requests in an integrator-owned commit, reviews the
exact resulting head, and requires applicable checks before integration. A new
base or changed head requires new source-bound qualification. Verify the receiving
tree and preserve the previous qualified source/evidence after integration.

A new lane test directory is not automatically exercised by existing CI. The
owner must provide its executed commands; the integrator adds appropriate hosted
or installed-artifact coverage through the shared CI request before claiming that
capability is qualified. Existing test discovery or a green documentation job is
not evidence that the new adapter ran. Do not weaken a gate to accommodate an
unavailable runtime or a queued security runner.

Track owners maintain their own index, plan, metadata and evidence. If their PR
changes a track's lifecycle status, request the matching central registry update;
the integrator applies it before final Conductor validation. Keep a PR pending
while that coordination is unresolved rather than editing another owner's file
or waiving consistency checks. Task-level progress does not require falsely
completing a whole track. Root docs and capability promotion follow actual evidence.

## Explicitly retained boundaries

- **Publication stays disabled.** Dylan's channel/account choices remain open.
  Apache-2.0 is the selected project licence; the release owner retains project
  and dependency notice work. No lane may publish packages, tags or public releases.
- **Power Platform was deferred from these seven lanes.** No tenant, worker, premium connector, app or
  deployment activation is part of these seven lanes.
- Preserve existing offline security, privacy, numerical, installed-artifact and
  release gates. Queued/unexecuted results are not passes; the integrator does not
  provision infrastructure or infer a waiver from branch settings.
- The four archived prerequisite tracks and their historical evidence stay intact.
  No historical fixture, expected value, method or source identity is rewritten
  to accommodate a new lane. No external repository archive or legacy removal is
  authorised by this ownership assignment.
- Real newborn programme qualification, M3 migration, reporting E3, process X2/X3,
  decision D2/D3, fiscal T2/T3, benchmark F2.3/F2.4 and external-validation F3 are
  separate acceptance scopes. Preserve negative/null research results even in the
  authorised static subset. No clinical, empirical or broader platform claim is
  inferred from synthetic examples.

The [registry](tracks.md) retains each track's actual lifecycle state. This map
records responsibility and review boundaries; it does not silently advance those
states or make optional lanes prerequisites for the bounded first release.

## Main integration reconciliation — 19 November 2026

Following sequential `--no-ff` integration onto `main`, this ownership record incorporates:

- PR #21 (`observed_events` X1 lane) plus X2 bounded PNML/BPMN adapters (`adapters/process_models/`) and workflow integration.
- PR #23 (`adapters/decision_draws/` for D1.1–D1.3 and T1.1–T1.3), PR #24 (`benchmarks/static/` for F1/F2.1–F2.2), PR #25 (`adapters/mchs_sources/` for M1–M2), PR #27 (`adapters/reporting_profiles/` for E1–E2), and PR #26 (`bindings/polyglot/` for B1–B2, with raw CI receipt removed from Git to preserve Gitleaks history cleanliness and the polyglot track retained as `blocked` pending ABI/Julia B3 and installed-host gates).
- PR #29 (retargeted to `main` after mechanical Ruff lint/formatting alignment), admitting `adapters/decision_provider_d2/` as the bounded optional D2/D3 preparation namespace under [decision_integrations_20261108](tracks/decision_integrations_20261108/index.md) with standalone CI in `.github/workflows/decision-provider-d2.yml`, while leaving `D2.1`–`D3.3` and installed provider acceptance open.
- PR #30 registering [serde_canonicalization_qualification_20261118](tracks/serde_canonicalization_qualification_20261118/index.md) (`new`), PR #28 (StepSecurity `harden-runner`), and PR #31 (pinned `actions/setup-python@v7.1.0`).

## Implementation and integration handoff, 20 November 2026

The integration chat `01a1f635-4bc2-7b60-87f9-e6d3111f4cb3` works in the managed checkout `~/.codex/worktrees/dapane-track-integration/dapane`. It owns the integration branches, shared CI, the release manifest and this registry reconciliation. The existing source-lane assignments above remain with their recorded worktrees.

The integrated source covers the fiscal executable and policy comparisons, installed decision providers, manual CareOps file exchange, native benchmark reruns and binding-host review. The linked [track plans](tracks.md) identify the exact delivered scope and the external acceptance that remains. This checkout operates on synthetic fixtures and local packages. Native CareOps operations, external provider contracts and registry accounts remain with their respective owners. The next release operation is to verify the integrated source and its hosted checks.

The same integration checkout owns the Power Platform source closeout in `power_platform/` and `conductor/tracks/power_platform_20261108/`, including the registry and archive entry. The owner deferred all live Power Platform work. The source handoff uses synthetic files and the existing SharePoint design.

On 21 November 2026 the same integration chat recorded the release channel
decision from the isolated CLI clone at
`/Volumes/PortableSSD/dapane-prerelease-20261121.x5LbfG/dapane` after the managed
checkout's Git volume filled. This work owned the release track records and the
`edithatogo/dapane` prerelease, initially selecting `d02095d`.

The same checkout merged the exchange fix in PR #67 and qualified `5a24196`.
The one-job runner completed the central scan and deregistered. GitHub served
the verified `v0.1.0` prerelease and all ten assets. The release track is archived
in place. [Terminal evidence](tracks/release_consolidation_20261108/evidence.md#verified-github-prerelease-and-in-place-archive)

On 24 November 2026 the same integration chat owns the Dapane hosted
offline-security migration from the isolated CLI checkout listed above.
The scope is the pinned scanner, Dapane workflow and release instructions.
The next operation is GitHub Actions qualification of the migration before
landing PR #73 and scanning the resulting `main` commit.

On 24 November 2026, integration chat `01a1f635-4bc2-7b60-87f9-e6d3111f4cb3`
uses the same isolated CLI checkout on `codex/dapane-optional-followups`.
It owns the L3.3/L3.4 release evidence, F3.2 CMS benchmark and opt-in
canonicalization experiment. The repository reads cover predecessor metadata,
release assets and pinned consumer receipts. The next operation is the public
aggregate benchmark replay from the registered protocol.
