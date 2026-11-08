# Setup verification

Scope: initialise the Conductor project records in the empty Dapane repository.
Review date: 8 November 2026, Australia/Brisbane.

## Local checks

- `python3 scripts/validate_conductor.py` passed: 13 tracks, 12 requirements,
  132 actionable tasks and 328 local file-link targets.
- `python3 -m py_compile scripts/validate_conductor.py` passed.
- `git diff --cached --check` passed for the reviewed setup files.
- An isolated temporary-fixture CLI check rejected all 11 invalid cases below
  with a non-zero result and a diagnostic, without an uncaught traceback.
- A valid local Markdown link with a quoted title was accepted.

| Rejected fixture | Expected protection |
| --- | --- |
| Missing required context | Incomplete setup cannot pass |
| Broken local link | Missing file targets are reported |
| Unknown local dependency | Provider text cannot masquerade as a local prerequisite |
| Dependency cycle | The local execution graph must remain acyclic |
| Unknown requirement ID | Tracks reference canonical requirement identifiers |
| Unowned canonical requirement | Every requirement has a track owner |
| Registry/metadata status mismatch | Project status records agree |
| Completed track with unfinished tasks | Completion cannot conceal pending work |
| Non-string metadata status | Invalid metadata produces a diagnostic |
| Markdown source resolving outside the repository | External source contents are not read |
| Track directory resolving outside the repository | External track contents are not traversed |

The temporary checks exercised the actual `--root` CLI against copied fixtures;
they did not modify the deliverable repository. Additional focused checks covered
valid in-repository source symlinks, Markdown title forms and invalid root paths.

## Review resolutions

Independent review identified and resolved two planning issues: newborn recipe
work no longer waits for an optional reporting adapter, and optional Arrow/Parquet
IO no longer blocks the scalar kernel/CLI/Python milestone. Validator review also
resolved outside-root source reads, title parsing and malformed-status handling.

## Publication

The reviewed setup is ready for initial publication to the empty repository.
Remote commit identity and hosted CI outcome will be recorded after publication;
the setup track remains in progress until that handoff is verified.

## Limits

The validator checks local file targets, metadata, traceability and the dependency
graph; it does not fetch external URLs or prove scientific claims. No costing
runtime, installed language package, clinical model, Power App or process execution
is implemented or qualified by this setup. All runtime and research tracks remain
new/planned.
