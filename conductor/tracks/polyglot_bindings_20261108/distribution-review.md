# R and Julia distribution review

Reviewed and executed on 20 November 2026 on macOS 27.2.1 arm64. The selected
handoff includes a vendored R source archive and a Julia package archive with
recorded SHA-256 digests. The release track retains registry and publication
decisions.

## Findings and fixes

- The earlier Julia check assembled its package from the working tree. The
  installer now exercises the actual archive, verifies its six regular members,
  and loads the package and bundled library from a fresh environment. It also
  retains the staged-library check used by the standalone host workflow.
- The archive builder verifies the thin arm64 Mach-O library header before
  creating the package. It writes a complete tar in a temporary directory before
  installing it at the requested path. An executable renamed as the library
  failed validation, and a repeated request for an existing path preserved its
  original bytes. Two archives built from the same bytes were identical.
- The install documentation now identifies the tested runtime versions and
  provides the package build, installation and readback commands.

## Artifact verification

| Artifact | SHA-256 |
| --- | --- |
| `dapaneR_0.1.0.tar.gz` | `a83579d18244cab088f25b2b6a2c21528c44040a3f8830d60348c1d372398299` |
| `dapaneR.so` from the fresh install | `932a1e5b321b8df5c1f6f0e33388698c429fb949db6f79265c1b8e92cf5d7643` |
| `dapane-julia-macos-arm64.tar` | `1f61ab3f4e1f6d9491fbff7d7ca142a8102e23bbd3d4430d7161ac960977128c` |
| `libdapane_abi.dylib` shipped in the Julia archive | `230792ee8c18098252cf60550b686385e124b9343d393c492b5bdb9d46d4bd40` |

- `R CMD INSTALL --preclean` built the vendored source archive into an empty
  library under R 4.6.2. `Rscript --vanilla bindings/polyglot/tests/installed.R`
  passed 24 shared cases, host rejection, GC stress and two R interpreters.
  The archive embeds source and lock hashes from `593013d`. Those R and core
  input paths are byte-identical to the reviewed source.
- The archive builder ran under CPython 3.15.1. The Julia 1.13.4
  `test/installed.jl --archive` run with `JULIA_PKG_OFFLINE=true` passed four
  installed artifact assertions and 44 assertions across the same 24 cases.
  The installed package located its library without an explicit path. The
  extracted library and all three legal files matched the input bytes.
- The same dylib passed the
  [instrumented C checks and ownership review](verification.md#macos-host-and-abi-review).
  The C header and Rust safety comments document exclusive caller-owned output
  and immutable input for the duration of each call.

The [reproduction instructions](../../../bindings/polyglot/README.md) cover the
qualified local packages. BinaryBuilder/JLL, public registry distribution and
additional native targets were outside this selection.
