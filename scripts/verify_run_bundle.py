#!/usr/bin/env python3
"""Verify candidate run bundles by replaying valuation in the installed Rust wheel."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from datetime import date
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError
from referencing import Registry, Resource
from referencing.exceptions import CannotDetermineSpecification, Unresolvable

ROOT = Path(__file__).resolve().parents[1]
MAX_BUNDLE_BYTES = 16 * 1024 * 1024
MAX_HISTORY_BYTES = 64 * 1024 * 1024
MAX_REVISIONS = 100


class BundleError(ValueError):
    """A bounded contract failure; never contains partial financial totals."""

    def __init__(self, code: str, path: str, message: str):
        self.code, self.path, self.message = code, path, message
        super().__init__(f"{code} at {path}: {message}")


def fail(code: str, path: str, message: str) -> None:
    raise BundleError(code, path, message)


def canonical(value: object) -> bytes:
    """Encode transport only. Preserve array order, exact strings and JSON types."""
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeError, RecursionError) as exc:
        raise BundleError("invalid_json", "/", "expected bounded JSON values") from exc


def bundle_digest(bundle: dict) -> str:
    payload = {key: value for key, value in bundle.items() if key != "bundle_digest"}
    digest = hashlib.sha256(b"dapane:run-bundle:0.1\n" + canonical(payload)).hexdigest()
    return "sha256:" + digest


def _pairs(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            fail("duplicate_key", "/", "duplicate JSON object key")
        result[key] = value
    return result


def _constant(_: str) -> None:
    fail("invalid_json", "/", "non-finite JSON constants are unsupported")


def read_history(path: Path) -> list:
    """Read only this explicitly supplied file; no manifest URLs or file references."""
    try:
        with path.open("rb") as stream:
            raw = stream.read(MAX_HISTORY_BYTES + 1)
        if len(raw) > MAX_HISTORY_BYTES:
            fail("limit_exceeded", "/", "history exceeds byte limit")
        result = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_constant)
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        if isinstance(exc, BundleError):
            raise
        raise BundleError("invalid_json", "/", "cannot read bounded UTF-8 JSON history") from exc
    if not isinstance(result, list):
        fail("invalid_history", "/", "history must be an ordered array")
    return result


@lru_cache(maxsize=1)
def _validator() -> Draft202012Validator:
    registry = Registry()
    target = None
    try:
        for path in sorted((ROOT / "schemas").rglob("*.schema.json")):
            document = json.loads(path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(document)
            registry = registry.with_resource(document["$id"], Resource.from_contents(document))
            if path == ROOT / "schemas/bundles/0.1.schema.json":
                target = document
    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        RecursionError,
        SchemaError,
        CannotDetermineSpecification,
    ) as exc:
        raise BundleError("schema_unavailable", "/", "invalid local schema set") from exc
    if target is None:
        fail("schema_unavailable", "/", "run-bundle schema is missing")
    # No retrieval function: unregistered references cannot fetch a URL.
    return Draft202012Validator(target, registry=registry, format_checker=FormatChecker())


def _date(value: str, path: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value) is None:
        fail("invalid_date", path, "expected YYYY-MM-DD")
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise BundleError("invalid_date", path, "invalid calendar date") from exc
    return value


def _identity(value: str, path: str) -> None:
    """Match native token byte/whitespace/control rules for new annotation IDs."""
    if (
        not value
        or value != value.strip()
        or len(value.encode("utf-8")) > 128
        or any(ord(char) < 32 or 127 <= ord(char) <= 159 for char in value)
    ):
        fail("invalid_identity", path, "expected a trimmed control-free token of at most 128 bytes")


def _identities(bundle: dict) -> None:
    for field in ("bundle_id", "series_id"):
        _identity(bundle[field], f"/{field}")
    for release in bundle["rate_releases"]:
        for field in ("source_id", "version"):
            _identity(release[field], f"/rate_releases/{field}")
        for ident in release["quote_ids"]:
            _identity(ident, "/rate_releases/quote_ids")
    for treatment in bundle["capital_treatments"]:
        _identity(treatment["asset_id"], "/capital_treatments/asset_id")
        for ident in treatment["source_line_ids"]:
            _identity(ident, "/capital_treatments/source_line_ids")
    for item in bundle["excluded_inputs"]:
        _identity(item["id"], "/excluded_inputs/id")


def _releases(bundle: dict) -> None:
    quotes = {quote["id"]: quote for quote in bundle["request"]["quotes"]}
    covered, releases = set(), set()
    for release in bundle["rate_releases"]:
        identity = (release["source_id"], release["version"])
        if identity in releases:
            fail("duplicate_release", "/rate_releases", "release identities must be unique")
        releases.add(identity)
        if not release["published_on"] <= release["retrieved_on"] <= bundle["recorded_on"]:
            fail("invalid_release_dates", "/rate_releases", "invalid publication/retrieval order")
        for ident in release["quote_ids"]:
            if ident not in quotes or ident in covered:
                fail("invalid_release", "/rate_releases", "quote requires exactly one release")
            quote = quotes[ident]
            if (quote["source"]["id"], quote["source"]["version"]) != identity:
                fail("invalid_release", "/rate_releases", "quote source differs from release")
            if not release["published_on"] <= quote["known_from"] <= release["retrieved_on"]:
                fail("invalid_release_dates", "/rate_releases", "invalid quote knowledge date")
            covered.add(ident)
    if covered != set(quotes):
        fail("missing_release", "/rate_releases", "all supplied quotes need a release snapshot")


def _release_history(bundle: dict, releases: dict, quotes: dict, digests: dict) -> None:
    """Remember immutable release facts, including facts absent from later subsets."""
    if bundle["request"] is None:
        return
    for release in bundle["rate_releases"]:
        identity = (release["source_id"], release["version"])
        published = release["published_on"]
        if identity in releases and releases[identity] != published:
            fail("release_conflict", "/rate_releases", "publication changed without a new version")
        releases[identity] = published
    for quote in bundle["request"]["quotes"]:
        source = quote["source"]
        identity = (source["id"], source["version"])
        digest = source.get("content_digest")
        if digest is not None:
            if identity in digests and digests[identity] != digest:
                fail("release_conflict", "/rate_releases", "conflicting source digests")
            digests[identity] = digest
        quote_identity = (*identity, quote["id"])
        snapshot = canonical(quote)
        if quote_identity in quotes and quotes[quote_identity] != snapshot:
            fail("release_conflict", "/rate_releases", "quote changed without a new source version")
        quotes[quote_identity] = snapshot


def _scope(bundle: dict) -> None:
    request = bundle["request"]
    window = bundle["observation_window"]
    if window["from"] >= window["to"]:
        fail("invalid_window", "/observation_window", "window must be nonempty and half-open")
    if request["knowledge_cutoff"] > bundle["recorded_on"]:
        fail("future_knowledge", "/recorded_on", "knowledge cutoff exceeds recording date")
    lines = {line["id"]: line for line in request["usage"]}
    occupied = set(lines) | {line["use_id"] for line in lines.values()}
    for line in lines.values():
        if not window["from"] <= line["service_date"] < window["to"]:
            fail("invalid_window", "/observation_window", "service date outside declared window")
    excluded = set()
    for item in bundle["excluded_inputs"]:
        if item["id"] in occupied or item["id"] in excluded:
            fail("invalid_exclusion", "/excluded_inputs", "excluded identity is repeated or valued")
        excluded.add(item["id"])
    assets, claimed = set(), set()
    for treatment in bundle["capital_treatments"]:
        if treatment["asset_id"] in assets:
            fail("mixed_capital", "/capital_treatments", "one treatment per asset and view")
        assets.add(treatment["asset_id"])
        basis = (
            "economic_cost"
            if treatment["treatment"] == "prepared_economic_charge"
            else "financial_cost"
        )
        if request["policy"]["basis"] != basis:
            fail("capital_basis", "/capital_treatments", "treatment and valuation basis disagree")
        for ident in treatment["source_line_ids"]:
            if ident not in lines or ident in claimed:
                fail("invalid_capital_line", "/capital_treatments", "line must exist and map once")
            if lines[ident]["kind"] != "resource_use":
                fail("capital_kind", "/capital_treatments", "capital requires resource-use lines")
            claimed.add(ident)


def verify_bundle(bundle: dict) -> str:
    """Check one snapshot; predecessor existence requires verify_history."""
    if not isinstance(bundle, dict):
        fail("invalid_bundle", "/", "bundle must be an object")
    if len(canonical(bundle)) > MAX_BUNDLE_BYTES:
        fail("limit_exceeded", "/", "bundle exceeds byte limit")
    try:
        error = next(_validator().iter_errors(bundle), None)
    except (Unresolvable, RecursionError) as exc:
        raise BundleError("schema_unavailable", "/", "unresolvable local schema reference") from exc
    if error is not None:
        path = "/" + "/".join(str(part) for part in error.absolute_path)
        fail("invalid_bundle", path, "bundle does not match the supported schema")
    _identities(bundle)
    if bundle_digest(bundle) != bundle["bundle_digest"]:
        fail("digest_mismatch", "/bundle_digest", "manifest bytes differ from supplied digest")
    if bundle["change"] == "retract":
        return bundle["bundle_digest"]
    _releases(bundle)
    _release_history(bundle, {}, {}, {})
    _scope(bundle)
    try:
        import dapane
    except ImportError as exc:
        raise BundleError("runtime_unavailable", "/report", "install the matching wheel") from exc
    try:
        replay = dapane.evaluate(copy.deepcopy(bundle["request"]))
    except dapane.DapaneError as exc:
        raise BundleError("native_rejection", "/request", "Rust rejected request") from exc
    # Canonical bytes, not Python equality: 2026 and 2026.0 must not compare equal.
    if canonical(replay) != canonical(bundle["report"]):
        fail("replay_mismatch", "/report", "stored report does not match native replay")
    return bundle["bundle_digest"]


def verify_history(records: list, *, expected_head_digest: str, as_of: str) -> dict:
    """Verify a complete ordered chain against a caller-supplied head checkpoint."""
    _date(as_of, "/as_of")
    if not isinstance(records, list) or not 1 <= len(records) <= MAX_REVISIONS:
        fail("invalid_history", "/", "history requires 1 to 100 ordered revisions")
    if len(canonical(records)) > MAX_HISTORY_BYTES:
        fail("limit_exceeded", "/", "history exceeds byte limit")
    previous, selected, identities = None, None, set()
    releases, quotes, digests = {}, {}, {}
    for position, bundle in enumerate(records):
        verify_bundle(bundle)
        if bundle["bundle_id"] in identities:
            fail("duplicate_identity", f"/{position}", "bundle IDs must be unique in a series")
        identities.add(bundle["bundle_id"])
        if previous is None:
            if bundle["change"] != "create":
                fail("missing_origin", f"/{position}", "history must begin with create")
        else:
            if bundle["change"] == "create" or previous["change"] == "retract":
                fail("invalid_transition", f"/{position}", "create/retraction lifecycle violated")
            if bundle["series_id"] != previous["series_id"]:
                fail("series_mismatch", f"/{position}", "revisions must remain in one series")
            if bundle["previous_digest"] != previous["bundle_digest"]:
                fail("broken_chain", f"/{position}", "predecessor digest does not match")
            if bundle["recorded_on"] < previous["recorded_on"]:
                fail("backdated_revision", f"/{position}", "recording dates must be nondecreasing")
        _release_history(bundle, releases, quotes, digests)
        previous = bundle
        if bundle["recorded_on"] <= as_of:
            selected = bundle
    if previous["bundle_digest"] != expected_head_digest:
        fail("checkpoint_mismatch", "/head", "history is not complete to the supplied checkpoint")
    if selected is None:
        status = "not_yet_known"
    elif selected["change"] == "retract":
        status = "retracted"
    else:
        status = "active"
    return {
        "status": status,
        "head_digest": expected_head_digest,
        "selected_digest": None if selected is None else selected["bundle_digest"],
        "report": None if selected is None else copy.deepcopy(selected["report"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("history", type=Path, help="ordered JSON array of immutable bundles")
    parser.add_argument("--head", required=True, help="independently retained head digest")
    parser.add_argument("--as-of", required=True, help="knowledge date, YYYY-MM-DD")
    args = parser.parse_args()
    try:
        result = verify_history(
            read_history(args.history), expected_head_digest=args.head, as_of=args.as_of
        )
    except BundleError as exc:
        error = {"code": exc.code, "path": exc.path, "message": exc.message}
        print(json.dumps({"error": error}), file=sys.stderr)
        return 2
    print(canonical(result).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
