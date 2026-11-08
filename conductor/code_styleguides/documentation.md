# Documentation and metadata conventions

Use plain language, meaningful headings and relative links to repository files.
Keep each requirement's `RQ-XX` identifier stable. Track IDs are stable directory
names; rename through an explicit migration rather than breaking cross-repo links.

Each track contains `index.md`, `spec.md`, `plan.md` and `metadata.json`. Keep the
registry's state, the index's `Status:` line and metadata's `status` consistent.
Use UTF-8 JSON with two-space indentation and a final newline. Dependency fields
contain local track IDs; provider dependencies belong in `external_dependencies`.

Write actionable plan items with `[ ]`, `[~]`, `[x]`, `[!]` or `[-]`. Completed
items need observable evidence. Record a clear reason for omitted or blocked
work. Keep acceptance criteria distinct from implementation activities.

Distinguish design decisions, assumptions, measured facts and future hypotheses.
Cite original standards and immutable repository snapshots for factual claims.
Do not label catalogue topic mappings as complete checklist transcriptions or
project-defined reporting profiles as externally endorsed standards.

Dates use ISO 8601 in metadata. Setup's review date is 2026-11-08, using the user's
Australia/Brisbane calendar. Do not replace historical verification dates with a
new date unless new evidence has actually been obtained.
