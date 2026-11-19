"""Complete-request memoisation experiment; all valuations stay in the Rust CLI.

No Dapane formulas, input normalisation or partial-report construction belong here.
The cache is process local and bounded to the most recent successful portfolio.
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path

from .common import Failure, decode, digest, file_digest, require


class NativeRejection(Failure):
    """A native structured rejection with empty financial output."""

    def __init__(self, diagnostic: dict):
        self.diagnostic = diagnostic
        super().__init__(f"{diagnostic['code']}: {diagnostic['message']} ({diagnostic['path']})")


@dataclass(frozen=True)
class WorkItem:
    command: str
    payload: bytes

    def __post_init__(self):
        require(self.command in {"evaluate", "evaluate-intervals"}, "Unsupported CLI command")
        require(isinstance(self.payload, bytes), "Request must be immutable UTF-8 bytes")


@dataclass
class Result:
    reports: dict[str, bytes]
    native_calls: int
    hits: int
    input_bytes: int
    output_bytes: int
    cache_payload_bytes: int


class NativeCli:
    """One explicitly supplied binary; no build, network, shell or source lookup."""

    def __init__(self, executable: Path):
        self.executable = executable.resolve(strict=True)
        require(self.executable.is_file(), "CLI must be a regular file")

    def fingerprint(self) -> str:
        return file_digest(self.executable)

    def invoke(self, item: WorkItem) -> bytes:
        try:
            process = subprocess.run(
                [str(self.executable), item.command, "-"],
                input=item.payload,
                capture_output=True,
                check=False,
                timeout=60,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise Failure(f"Native invocation failed: {error}") from error
        if process.returncode:
            require(process.returncode == 1, f"Unexpected native exit {process.returncode}")
            require(process.stdout == b"", "Rejected request emitted partial financial output")
            diagnostic = decode(process.stderr)
            require(isinstance(diagnostic, dict), "Native error is not an object")
            require(set(diagnostic) == {"code", "message", "path"}, "Invalid error envelope")
            require(
                all(isinstance(value, str) and value for value in diagnostic.values()),
                "Native error fields must be nonempty strings",
            )
            raise NativeRejection(diagnostic)
        require(process.stderr == b"", "Successful invocation emitted unexpected stderr")
        report = decode(process.stdout)
        require(isinstance(report, dict), "Native report is not an object")
        financial = report if item.command == "evaluate" else report.get("report", {})
        require(isinstance(financial, dict), "Native financial report is not an object")
        require(financial.get("status") == "complete", "Missing complete native report")
        return process.stdout


def _key(identity: str, item: WorkItem) -> tuple[str, str, str]:
    return identity, item.command, digest(item.payload)


def _result(items: dict, reports: dict, calls: int, cache_bytes: int) -> Result:
    return Result(
        reports=reports,
        native_calls=calls,
        hits=len(items) - calls,
        input_bytes=sum(len(work.payload) for work in items.values()),
        output_bytes=sum(len(raw) for raw in reports.values()),
        cache_payload_bytes=cache_bytes,
    )


def full(runner: NativeCli, items: dict[str, WorkItem]) -> Result:
    """Recompute all independent requests; return nothing if any one fails."""
    identity = runner.fingerprint()
    reports = {}
    for name, work in sorted(items.items()):
        _key(identity, work)  # Identical full-input hashing in both timed paths.
        reports[name] = runner.invoke(work)
    require(identity == runner.fingerprint(), "CLI changed during full recomputation")
    return _result(items, reports, len(items), 0)


class Incremental:
    """Cache complete byte-identical requests under an exact executable identity."""

    def __init__(self, runner: NativeCli):
        self.runner = runner
        self._entries: dict[tuple[str, str, str], tuple[bytes, bytes]] = {}

    def evaluate(self, items: dict[str, WorkItem]) -> Result:
        identity = self.runner.fingerprint()
        pending = {}
        reports = {}
        calls = 0
        for name, work in sorted(items.items()):
            key = _key(identity, work)
            cached = pending.get(key, self._entries.get(key))
            if cached is None:
                raw = self.runner.invoke(work)
                calls += 1
            else:
                original, raw = cached
                require(original == work.payload, "Input digest collision; refuse cache reuse")
            pending[key] = work.payload, raw
            reports[name] = raw
        require(identity == self.runner.fingerprint(), "CLI changed during incremental evaluation")
        # Replacement is atomic and evicts entries removed from this portfolio.
        self._entries = pending
        cache_bytes = sum(len(payload) + len(raw) for payload, raw in pending.values())
        return _result(items, reports, calls, cache_bytes)
