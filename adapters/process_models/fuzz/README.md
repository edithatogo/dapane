# Bounded parser fuzzing

## Scope and invariants

XML result determinism, bounded depth/node/attribute counts; JSON compact reparse equality; PNML result determinism, positive arc weights and existing bipartite endpoints; BPMN core/extended profiles and both config parsers are exercised.

The target includes the same assertion helper as the native `fuzz_regressions`
integration test. Two native tests replay the corpus and deterministic truncation,
bit-flip and suffix mutations, so ordinary CI executes these invariants even
without libFuzzer. The libFuzzer workspace is independent of the production
workspace and adds no production dependency or feature.

All committed seeds are synthetic: authored here or copied from existing repository
fixtures. The minimal PDF, where present, is generated from simple locally authored
objects. Never add real messages, patient data, downloaded papers, credentials,
private logs or attachments. Only synthetic campaigns may upload crash/corpus
artifacts; review any newly minimized regression before committing it.

## Run and reproduce

```bash
cargo +1.99.1 test --manifest-path adapters/process_models/Cargo.toml --locked --offline --test fuzz_regressions
rustup toolchain install nightly-2026-11-19 --profile minimal
cargo +nightly-2026-11-19 install cargo-fuzz --version 0.13.2 --locked
bash adapters/process_models/fuzz/run.sh 30
# Longer bounded local campaign (1..3600 seconds accepted):
bash adapters/process_models/fuzz/run.sh 600
```

The runner fetches using the committed fuzz `Cargo.lock` with `--locked`, builds
offline, and refuses a changed lockfile. This is explicit because cargo-fuzz
0.13.2 itself has no `--locked` flag. Nightly and cargo-fuzz are pinned;
libfuzzer-sys is exactly 0.4.13. The runner uses AddressSanitizer, debug assertions,
a fixed starting seed, a 5-second per-input timeout, 1 GiB RSS and 512 MiB
allocation limits, and an external campaign watchdog. Maximum input size is
262,145 bytes. These harness limits do not claim a production resource
sandbox or complete parser coverage. Runs can end early on any invariant,
sanitizer, allocation or timeout failure; that is a failing result, not a pass.

Crashes go to `adapters/process_models/fuzz/artifacts/parse_models/`. Tool versions, commit, lock hash,
budget, compiler output and full campaign statistics are under
`adapters/process_models/fuzz/target/evidence/`. New coverage inputs stay in
`adapters/process_models/fuzz/target/corpus/parse_models/`; checked-in seeds are unchanged.

Replay a saved artifact from the same commit and fuzz lockfile:

```bash
cd adapters/process_models/fuzz
cargo +nightly-2026-11-19 fuzz run parse_models artifacts/parse_models/ARTIFACT -- -runs=1 -timeout=5 -rss_limit_mb=1024 -malloc_limit_mb=512
cargo +nightly-2026-11-19 fuzz tmin parse_models artifacts/parse_models/ARTIFACT
```

Minimize locally with the same resource limits and promote only a reviewed,
synthetic reproducer to the native regression corpus. A finite campaign with no
finding is evidence of that execution, not proof of parser safety.

## CI and admission

The existing process-model adapter workflow already runs the new native tests.
The shared `.github/` workflows, root manifests/locks and central Conductor
registry are reserved to the sole integrator by `AGENTS.md`; this change leaves
those surfaces to that owner. Proposed integration: run this script for 30 seconds
on adapter PRs and 600 seconds weekly with contents:read, no checkout credentials,
a 30-minute job timeout and 14-day synthetic crash/evidence artifacts. Scheduled
coverage-guided execution remains an explicit integrator-owned gate; merely adding
this executable harness does not establish that schedule.
