# Repository map

## Observed starting point

On 8 November 2026 the GitHub repository `edithatogo/dapane` was public and empty,
with no branch commits, instructions, manifests, licence, source, tests or existing
Conductor records. Its configured default branch was `main`. No content needed
migration or deletion.

The setup adds:

| Path | Current responsibility |
| --- | --- |
| `README.md` | Entry point and honest maturity statement |
| `AGENTS.md` | Repository-specific navigation and working practices |
| `conductor/index.md` | Authoritative project-context index |
| `conductor/*.md` | Product, requirements, architecture, decisions, workflow and roadmap |
| `conductor/code_styleguides/` | Rust, Python/FFI and document conventions |
| `conductor/tracks/` | Coherent implementation/research specs, task plans and metadata |
| `conductor/archive/` | Archive policy; no archived tracks at setup |
| `scripts/validate_conductor.py` | Dependency-free structural and consistency check |
| `.github/workflows/conductor.yml` | Read-only documentation CI |

The first runtime tracks will establish the Cargo workspace, crate layout,
manifests, lockfiles, schemas, fixtures and Python package. Paths described in the
design as proposed implementation locations do not exist merely because they are
mentioned here. There are no package releases, binary artefacts or deployments.

## Source-of-truth boundaries

Dapane owns this framework's requirements, architecture and coordinated roadmap.
The original MCHS design is a source snapshot; MCHS retains its domain adapter and
calculator ownership. UOGTO owns semantics and reporting-profile mappings;
standards_check owns original reporting-source records. See
[ecosystem](ecosystem.md) for exact reviewed snapshots and readiness.

## Keeping this map current

Update this file when implementation areas or public entry points are added or
removed. Record actual build/test commands in the workflow and affected track.
Do not replace executable discovery with a speculative exhaustive file tree.
