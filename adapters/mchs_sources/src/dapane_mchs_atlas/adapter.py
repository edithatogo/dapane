"""Prepare explicitly selected views without importing provider runtimes or formulas."""

from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Callable
from importlib.resources import files
from typing import Any
from urllib.parse import urlsplit

from ._validation import (
    AdapterError,
    choice,
    currency,
    day,
    digest,
    equal,
    exact,
    fail,
    integer,
    object_at,
    rows,
    snapshot,
    text,
    timestamp,
)

PINS = json.loads(files(__package__).joinpath("provider_pins.json").read_text(encoding="utf-8"))
CORE_SOURCE = "id version evidence access validation content_digest locator"
SOURCE_EXTRA = "official_status rights known_from"
DECIMAL_OUTPUT = (
    "eligible_icu_hours los_icu_removed w01 w02 w03 w04 gwau "
    "private_service_deduction private_accommodation_deduction nwau total_funding"
)
CONTEXT = "stream classification_system classification_edition pricing_edition"


def _url(value: Any, path: str) -> str:
    value = text(value, path, limit=2048)
    try:
        parsed = urlsplit(value)
        valid = parsed.scheme in ("http", "https") and parsed.hostname and not parsed.username
    except ValueError:
        valid = False
    if not valid:
        fail("invalid_source_url", "Expected an HTTP(S) source URL without credentials.", path)
    return value


def _known(value: Any, cutoff: str, path: str) -> str:
    value = day(value, path)
    if value > cutoff:
        fail("not_known", "Source evidence was not available at the knowledge cutoff.", path)
    return value


def _evidence(meta: dict[str, Any], cutoff: str, path: str) -> None:
    evidence = choice(
        meta["evidence"], ("synthetic", "observed", "derived"), f"{path}/evidence", "source_status"
    )
    choice(meta["access"], ("public", "restricted", "private"), f"{path}/access", "source_status")
    choice(
        meta["validation"],
        ("unvalidated", "source_verified", "empirically_validated"),
        f"{path}/validation",
        "source_status",
    )
    official = choice(
        meta["official_status"],
        ("synthetic", "official", "not_official"),
        f"{path}/official_status",
        "source_status",
    )
    if (evidence == "synthetic") != (official == "synthetic") or (
        evidence == "synthetic" and meta["validation"] != "unvalidated"
    ):
        fail("source_status", "Synthetic evidence must remain synthetic and unvalidated.", path)
    rights = object_at(meta["rights"], "status licence evidence_ref", "", f"{path}/rights")
    choice(rights["status"], ("permitted",), f"{path}/rights/status", "source_rights")
    for field in ("licence", "evidence_ref"):
        value = text(rights[field], f"{path}/rights/{field}", limit=2048)
        if value.casefold() in ("unknown", "unspecified", "pending", "none"):
            fail("source_rights", "Explicit rights evidence is required.", f"{path}/rights/{field}")
    _known(meta["known_from"], cutoff, f"{path}/known_from")


def _source(value: Any, cutoff: str, path: str) -> dict[str, Any]:
    source = object_at(value, f"{CORE_SOURCE} {SOURCE_EXTRA}", "", path)
    _evidence(source, cutoff, path)
    for field in ("id", "version"):
        text(source[field], f"{path}/{field}")
    digest(source["content_digest"], f"{path}/content_digest", prefix=True)
    text(source["locator"], f"{path}/locator", limit=2048)
    return {key: source[key] for key in CORE_SOURCE.split()}


def _context(value: Any, path: str) -> dict[str, Any]:
    context = object_at(value, CONTEXT, "", path)
    choice(context["stream"], ("acute",), f"{path}/stream", "unsupported_stream")
    for field in CONTEXT.split():
        item = text(context[field], f"{path}/{field}")
        if item.casefold() in ("unknown", "unspecified", "pending", "none"):
            fail("unknown_context", "Explicit classification and pricing context is required.", path)
    return context


def _target(context: dict[str, Any]) -> str:
    # Full digest avoids truncating/colliding compound classification identifiers.
    encoded = json.dumps(context, sort_keys=True, separators=(",", ":")).encode()
    return "mchs-acute:" + hashlib.sha256(encoded).hexdigest()


def _activity(value: Any, cutoff: str, path: str) -> dict[str, Any]:
    activity = object_at(
        value,
        "profile provider_revision method id classification_code context "
        "unit service_date source result",
        "",
        path,
    )
    choice(
        activity["profile"], ("mchs-acute-decimal-projection/0.1",), f"{path}/profile", "profile"
    )
    equal(
        activity["provider_revision"],
        PINS["mchs"]["revision"],
        f"{path}/provider_revision",
        code="provider_revision",
    )
    choice(
        activity["method"],
        ("calculate_acute_decimal", "calculate_acute_2026"),
        f"{path}/method",
        "unsupported_method",
    )
    text(activity["id"], f"{path}/id")
    text(activity["classification_code"], f"{path}/classification_code")
    _context(activity["context"], f"{path}/context")
    choice(activity["unit"], ("NWAU",), f"{path}/unit", "unsupported_unit")
    day(activity["service_date"], f"{path}/service_date")
    source = _source(activity["source"], cutoff, f"{path}/source")
    result = object_at(
        activity["result"], f"error_code separation_category {DECIMAL_OUTPUT}", "", f"{path}/result"
    )
    integer(result["error_code"], 0, 255, f"{path}/result/error_code")
    if result["error_code"] != 0:
        fail("provider_error", "MCHS reported an error; zero output is not valid activity.", path)
    integer(result["separation_category"], 1, 4, f"{path}/result/separation_category")
    for field in DECIMAL_OUTPUT.split():
        if type(result[field]) is not str:
            fail(
                "invalid_exact",
                "Decimal provider fields must be original decimal strings.",
                f"{path}/result/{field}",
            )
        exact(result[field], f"{path}/result/{field}")
    return {
        "id": activity["id"],
        "quantity": result["nwau"],
        "source": source,
        "target": _target(activity["context"]),
        "context": activity["context"],
        "unit": activity["unit"],
        "service_date": activity["service_date"],
    }


def _atlas_header(pack: dict[str, Any], cutoff: str, path: str) -> dict[str, Any]:
    choice(pack["profile"], ("atlas-exact-supplement/0.1",), f"{path}/profile", "profile")
    equal(
        pack["provider_revision"],
        PINS["atlas"]["revision"],
        f"{path}/provider_revision",
        code="provider_revision",
    )
    version = object_at(
        pack["source_version"],
        "id source_id version_label source_url format parser_status effective_from "
        "effective_to retrieved_at checksum_sha256 notes",
        "",
        f"{path}/source_version",
    )
    snap = object_at(
        pack["snapshot"],
        "id source_id source_version_id source_url retrieved_at checksum_sha256 licence_gate cache_scope",
        "local_path content_type byte_size notes",
        f"{path}/snapshot",
    )
    meta = object_at(
        pack["metadata"],
        "evidence access validation official_status known_from rights effective_to_convention",
        "",
        f"{path}/metadata",
    )
    _evidence(meta, cutoff, f"{path}/metadata")
    choice(
        meta["effective_to_convention"],
        ("exclusive",),
        f"{path}/metadata/effective_to_convention",
        "date_convention",
    )
    for record, label, fields in [
        (version, "source_version", "id source_id version_label format"),
        (snap, "snapshot", "id source_id source_version_id"),
    ]:
        for field in fields.split():
            text(record[field], f"{path}/{label}/{field}")
        _url(record["source_url"], f"{path}/{label}/source_url")
        timestamp(record["retrieved_at"], f"{path}/{label}/retrieved_at")
        digest(record["checksum_sha256"], f"{path}/{label}/checksum_sha256")
        if record.get("notes") is not None:
            text(record["notes"], f"{path}/{label}/notes", limit=4096)
    for field in ("source_id", "source_url", "retrieved_at", "checksum_sha256"):
        equal(snap[field], version[field], f"{path}/snapshot/{field}")
    equal(snap["source_version_id"], version["id"], f"{path}/snapshot/source_version_id")
    for field in ("effective_from", "effective_to"):
        day(version[field], f"{path}/source_version/{field}")
    if version["effective_from"] >= version["effective_to"]:
        fail("invalid_date", "Release applicability must be a nonempty half-open interval.", path)
    choice(
        version["parser_status"],
        ("prototype", "validated", "production"),
        f"{path}/source_version/parser_status",
        "source_status",
    )
    if version["parser_status"] == "prototype" and meta["evidence"] != "synthetic":
        fail("source_status", "Prototype parser output is admitted only for synthetic fixtures.", path)
    choice(snap["licence_gate"], ("permissive",), f"{path}/snapshot/licence_gate", "source_rights")
    choice(
        snap["cache_scope"],
        ("public_raw_cache", "public_derived_only"),
        f"{path}/snapshot/cache_scope",
        "source_rights",
    )
    if snap.get("local_path") is not None:
        fail("unsupported_snapshot", "Local paths are not admitted in this portable profile.", path)
    if snap.get("byte_size") is not None:
        integer(snap["byte_size"], 0, 2**63 - 1, f"{path}/snapshot/byte_size")
    if snap.get("content_type") is not None:
        text(snap["content_type"], f"{path}/snapshot/content_type")
    return {
        "id": version["source_id"],
        "version": version["id"],
        "evidence": meta["evidence"],
        "access": meta["access"],
        "validation": meta["validation"],
        "content_digest": "sha256:" + snap["checksum_sha256"],
        "locator": snap["source_url"],
    }


def _quote(
    value: Any, pack: dict[str, Any], source: dict[str, Any], path: str
) -> dict[str, Any]:
    record = object_at(value, "id item exact application", "", path)
    text(record["id"], f"{path}/id")
    item = object_at(
        record["item"],
        "source_id jurisdiction domain code_system item_code item_label currency "
        "payment_unit effective_from effective_to provenance",
        "item_description payment_amount patient_amount restriction_text setting "
        "professional_component facility_component",
        f"{path}/item",
    )
    if item.get("payment_amount") is not None:
        fail(
            "lossy_atlas_amount",
            "Normalized Atlas money is float-based; supply an exact supplement "
            "and a metadata record with null payment_amount.",
            f"{path}/item/payment_amount",
        )
    if item.get("patient_amount") is not None or item.get("restriction_text") is not None:
        fail(
            "unsupported_item",
            "Patient components and conditional restrictions need another profile.",
            path,
        )
    for field in (
        "source_id", "jurisdiction", "domain", "code_system", "item_code", "item_label", "payment_unit"
    ):
        text(item[field], f"{path}/item/{field}")
    for field in ("item_description", "setting"):
        if item.get(field) is not None:
            text(item[field], f"{path}/item/{field}", limit=4096)
    for field in ("professional_component", "facility_component"):
        if item.get(field) is not None and type(item[field]) is not bool:
            fail("invalid_type", "Component flags must be boolean or null.", f"{path}/item/{field}")
    currency(item["currency"], f"{path}/item/currency")
    version = pack["source_version"]
    equal(item["source_id"], version["source_id"], f"{path}/item/source_id")
    for field in ("effective_from", "effective_to"):
        day(item[field], f"{path}/item/{field}")
    if not (
        version["effective_from"] <= item["effective_from"] < item["effective_to"]
        <= version["effective_to"]
    ):
        fail("stale_quote", "Item dates must fit the declared source release interval.", path)
    provenance = object_at(
        item["provenance"],
        "source_id source_url retrieved_at effective_date source_version licence_class",
        "transformation_notes",
        f"{path}/item/provenance",
    )
    for key, expected in {
        "source_id": version["source_id"],
        "source_url": version["source_url"],
        "retrieved_at": version["retrieved_at"],
        "source_version": version["version_label"],
        "effective_date": item["effective_from"],
    }.items():
        equal(provenance[key], expected, f"{path}/item/provenance/{key}")
    choice(
        provenance["licence_class"],
        ("permissive",),
        f"{path}/item/provenance/licence_class",
        "source_rights",
    )
    if provenance.get("transformation_notes") is not None:
        text(
            provenance["transformation_notes"],
            f"{path}/item/provenance/transformation_notes",
            limit=4096,
        )
    supplement = object_at(
        record["exact"], "amount per_quantity source_field source_locator snapshot_sha256",
        "", f"{path}/exact",
    )
    exact(supplement["amount"], f"{path}/exact/amount")
    exact(supplement["per_quantity"], f"{path}/exact/per_quantity", positive=True)
    text(supplement["source_field"], f"{path}/exact/source_field")
    text(supplement["source_locator"], f"{path}/exact/source_locator", limit=2048)
    digest(supplement["snapshot_sha256"], f"{path}/exact/snapshot_sha256")
    equal(
        supplement["snapshot_sha256"], pack["snapshot"]["checksum_sha256"],
        f"{path}/exact/snapshot_sha256",
    )
    application = object_at(
        record["application"], "view context unit price_year components", "", f"{path}/application"
    )
    view = choice(
        application["view"], ("funding", "tariff"), f"{path}/application/view", "unsupported_view"
    )
    context = _context(application["context"], f"{path}/application/context")
    equal(
        application["unit"], item["payment_unit"], f"{path}/application/unit",
        code="incompatible_quote",
    )
    integer(application["price_year"], 1, 9999, f"{path}/application/price_year")
    components = rows(application["components"], f"{path}/application/components", nonempty=True)
    for index, component in enumerate(components):
        text(component, f"{path}/application/components/{index}")
    if len(set(components)) != len(components):
        fail("duplicate_id", "Quote components must be unique.", f"{path}/application/components")
    quote = {
        "id": record["id"],
        "kind": "activity_measure",
        "target": _target(context),
        "unit": application["unit"],
        "amount": supplement["amount"],
        "per_quantity": supplement["per_quantity"],
        "currency": item["currency"],
        "price_year": application["price_year"],
        "basis": "funding" if view == "funding" else "charge",
        "components": components,
        "valid_from": item["effective_from"],
        "valid_to": item["effective_to"],
        "known_from": pack["metadata"]["known_from"],
        "source": source,
    }
    return {"quote": quote, "view": view, "context": context}


def _policy(value: Any, view: str, path: str) -> dict[str, Any]:
    policy = object_at(value, "id version currency price_year perspective basis rounding", "", path)
    for field in ("id", "version", "perspective"):
        text(policy[field], f"{path}/{field}")
    currency(policy["currency"], f"{path}/currency")
    integer(policy["price_year"], 1, 9999, f"{path}/price_year")
    equal(
        policy["basis"], "funding" if view == "funding" else "charge", f"{path}/basis",
        code="view_basis",
    )
    rounding = object_at(policy["rounding"], "scale mode", "", f"{path}/rounding")
    integer(rounding["scale"], 0, 12, f"{path}/rounding/scale")
    choice(rounding["mode"], ("half_even",), f"{path}/rounding/mode", "unsupported_rounding")
    return policy


def _request(
    view: dict[str, Any],
    activities: dict[str, Any],
    quotes: dict[str, Any],
    run_id: str,
    cutoff: str,
    path: str,
) -> dict[str, Any]:
    view = object_at(view, "name policy selections", "", path)
    name = choice(view["name"], ("funding", "tariff"), f"{path}/name", "unsupported_view")
    policy = _policy(view["policy"], name, f"{path}/policy")
    use_rows = []
    used_activities: set[str] = set()
    selected_quotes: dict[str, Any] = {}
    for index, selection in enumerate(
        rows(view["selections"], f"{path}/selections", nonempty=True)
    ):
        spath = f"{path}/selections/{index}"
        selection = object_at(selection, "line_id activity_id quote_id", "", spath)
        for field in ("line_id", "activity_id", "quote_id"):
            text(selection[field], f"{spath}/{field}")
        if selection["activity_id"] not in activities:
            fail("missing_activity", "Selected activity does not exist.", f"{spath}/activity_id")
        if selection["quote_id"] not in quotes:
            fail(
                "missing_quote", "An explicit applicable quotation is required.", f"{spath}/quote_id"
            )
        activity = activities[selection["activity_id"]]
        prepared_quote = quotes[selection["quote_id"]]
        quote = prepared_quote["quote"]
        for actual, expected in [
            (prepared_quote["view"], name),
            (prepared_quote["context"], activity["context"]),
            (quote["unit"], activity["unit"]),
            (quote["currency"], policy["currency"]),
            (quote["price_year"], policy["price_year"]),
        ]:
            equal(actual, expected, spath, code="incompatible_quote")
        if not quote["valid_from"] <= activity["service_date"] < quote["valid_to"]:
            fail("stale_quote", "Quote does not apply on the activity service date.", spath)
        use_rows.append({
            "id": selection["line_id"],
            "use_id": activity["id"],
            "kind": "activity_measure",
            "target": activity["target"],
            "unit": activity["unit"],
            "quantity": activity["quantity"],
            "service_date": activity["service_date"],
            "quote_id": quote["id"],
            "source": activity["source"],
        })
        used_activities.add(activity["id"])
        selected_quotes[quote["id"]] = quote
    if used_activities != set(activities):
        fail(
            "unpriced_activity",
            "Every activity requires an explicit selection in each requested view.",
            path,
        )
    return {
        "schema_version": "0.1",
        "run_id": text(f"{run_id}:{name}", f"{path}/run_id"),
        "knowledge_cutoff": cutoff,
        "policy": policy,
        "quotes": [selected_quotes[key] for key in sorted(selected_quotes)],
        "usage": sorted(use_rows, key=lambda row: row["id"]),
    }


def _resource(value: Any, evidence: Any, run_id: str, cutoff: str) -> dict[str, Any]:
    """Preserve the caller's separate core request; native evaluation validates it."""
    if type(value) is not dict or type(value.get("policy")) is not dict:
        fail(
            "resource_view", "Resource costs require an existing core request and policy.",
            "/resource_cost",
        )
    choice(value.get("schema_version"), ("0.1",), "/resource_cost/schema_version", "resource_view")
    choice(
        value["policy"].get("basis"), ("economic_cost", "financial_cost"),
        "/resource_cost/policy/basis", "resource_view",
    )
    declared: dict[tuple[str, str], dict[str, Any]] = {}
    for index, record in enumerate(rows(evidence, "/resource_sources", nonempty=True)):
        source = _source(record, cutoff, f"/resource_sources/{index}")
        key = (source["id"], source["version"])
        if key in declared:
            fail(
                "duplicate_id", "Resource source declarations must be unique.",
                f"/resource_sources/{index}",
            )
        declared[key] = source
    used: set[tuple[str, str]] = set()
    for collection in ("usage", "quotes"):
        for index, row in enumerate(
            rows(value.get(collection), f"/resource_cost/{collection}", nonempty=True)
        ):
            if type(row) is not dict or row.get("kind") != "resource_use":
                fail(
                    "resource_view",
                    "Resource costs cannot contain weighted activity quotations or usage.",
                    f"/resource_cost/{collection}/{index}",
                )
            path = f"/resource_cost/{collection}/{index}/source"
            source = object_at(row.get("source"), CORE_SOURCE, "", path)
            text(source["id"], f"{path}/id")
            text(source["version"], f"{path}/version")
            key = (source["id"], source["version"])
            if key not in declared:
                fail(
                    "source_rights",
                    "Every resource source requires its explicit rights/status declaration.",
                    path,
                )
            equal(source, declared[key], path)
            used.add(key)
    if used != set(declared):
        fail(
            "source_mismatch", "Resource source declarations must match the request's sources.",
            "/resource_sources",
        )
    equal(
        value.get("run_id"), f"{run_id}:resource_cost", "/resource_cost/run_id", code="resource_view"
    )
    equal(
        value.get("knowledge_cutoff"), cutoff, "/resource_cost/knowledge_cutoff", code="resource_view"
    )
    return value


def _payments(values: Any, activities: dict[str, Any], cutoff: str) -> list[dict[str, Any]]:
    result = []
    identifiers: set[str] = set()
    observations: set[tuple[str, str, str]] = set()
    for index, value in enumerate(rows(values, "/payments")):
        path = f"/payments/{index}"
        payment = object_at(
            value, "id record_kind amount currency date scope_ref observation_ref model source",
            "", path,
        )
        identity = text(payment["id"], f"{path}/id")
        if identity in identifiers:
            fail("duplicate_id", "Payment identifiers must be unique.", f"{path}/id")
        identifiers.add(identity)
        kind = choice(
            payment["record_kind"], ("observation", "model"), f"{path}/record_kind", "payment_evidence"
        )
        exact(payment["amount"], f"{path}/amount")
        currency(payment["currency"], f"{path}/currency")
        day(payment["date"], f"{path}/date")
        text(payment["scope_ref"], f"{path}/scope_ref")
        if payment["scope_ref"] not in activities:
            fail(
                "payment_evidence", "Payment scope must identify a supplied activity.",
                f"{path}/scope_ref",
            )
        source = _source(payment["source"], cutoff, f"{path}/source")
        if kind == "observation":
            if payment["observation_ref"] is None or payment["model"] is not None:
                fail(
                    "payment_evidence", "An observation requires its reference and no model.", path
                )
            text(payment["observation_ref"], f"{path}/observation_ref")
            choice(
                source["evidence"], ("observed", "synthetic"),
                f"{path}/source/evidence", "payment_evidence",
            )
            if payment["date"] > cutoff:
                fail(
                    "payment_evidence",
                    "An observation cannot occur after the run's knowledge cutoff.",
                    f"{path}/date",
                )
            key = (source["id"], source["version"], payment["observation_ref"])
            if key in observations:
                fail(
                    "duplicate_id", "The same payment observation cannot be imported twice.", path
                )
            observations.add(key)
        else:
            if payment["observation_ref"] is not None or type(payment["model"]) is not dict:
                fail(
                    "payment_evidence",
                    "A modelled payment requires a named model and no observation reference.",
                    path,
                )
            model = object_at(payment["model"], "id version", "", f"{path}/model")
            for field in ("id", "version"):
                text(model[field], f"{path}/model/{field}")
            choice(
                source["evidence"], ("derived", "synthetic"),
                f"{path}/source/evidence", "payment_evidence",
            )
        result.append(payment)
    return sorted(result, key=lambda row: row["id"])


def prepare(bundle: dict[str, Any]) -> dict[str, Any]:
    """Build separate core requests plus source snapshots; no monetary arithmetic.

    Preparation checks adapter applicability and evidence. The returned status is
    prepared; only native evaluation can produce complete valuation reports.
    Exact source strings must precede any upstream float conversion. This function
    does not assert source truth, legal permission, or provider equation validity.
    """
    original = snapshot(bundle)
    data = object_at(
        original, "profile run_id knowledge_cutoff activities quote_packs views",
        "resource_cost resource_sources payments", "",
    )
    choice(data["profile"], ("dapane-mchs-atlas/0.1",), "/profile", "profile")
    run_id = text(data["run_id"], "/run_id", limit=110)
    cutoff = day(data["knowledge_cutoff"], "/knowledge_cutoff")
    activities: dict[str, Any] = {}
    for index, value in enumerate(rows(data["activities"], "/activities", nonempty=True)):
        activity = _activity(value, cutoff, f"/activities/{index}")
        if activity["id"] in activities:
            fail("duplicate_id", "Activity identifiers must be unique.", f"/activities/{index}/id")
        activities[activity["id"]] = activity
    quotes: dict[str, Any] = {}
    release_snapshots: dict[tuple[str, str], dict[str, Any]] = {}
    for index, value in enumerate(rows(data["quote_packs"], "/quote_packs", nonempty=True)):
        path = f"/quote_packs/{index}"
        pack = object_at(
            value, "profile provider_revision source_version snapshot metadata quotes", "", path
        )
        source = _atlas_header(pack, cutoff, path)
        release_key = (source["id"], source["version"])
        release_metadata = {
            key: pack[key] for key in ("source_version", "snapshot", "metadata")
        }
        if release_key in release_snapshots:
            equal(release_metadata, release_snapshots[release_key], path)
        release_snapshots[release_key] = release_metadata
        for qindex, value in enumerate(rows(pack["quotes"], f"{path}/quotes", nonempty=True)):
            qpath = f"{path}/quotes/{qindex}"
            quote = _quote(value, pack, source, qpath)
            identity = quote["quote"]["id"]
            if identity in quotes:
                fail(
                    "duplicate_id", "Quotation identifiers must be unique across packs.",
                    f"{qpath}/id",
                )
            quotes[identity] = quote
    requests: dict[str, Any] = {}
    for index, value in enumerate(rows(data["views"], "/views", nonempty=True)):
        path = f"/views/{index}"
        request = _request(value, activities, quotes, run_id, cutoff, path)
        name = value["name"]
        if name in requests:
            fail("duplicate_id", "Each valuation view can occur once.", f"{path}/name")
        requests[name] = request
    if data.get("resource_cost") is not None:
        if "resource_sources" not in data:
            fail(
                "source_rights", "Resource costs require explicit source rights/status evidence.",
                "/resource_sources",
            )
        requests["resource_cost"] = _resource(
            data["resource_cost"], data["resource_sources"], run_id, cutoff
        )
    elif "resource_sources" in data and rows(data["resource_sources"], "/resource_sources"):
        fail(
            "source_mismatch", "Resource source evidence requires its resource-cost request.",
            "/resource_sources",
        )
    payments = _payments(data.get("payments", []), activities, cutoff)
    encoded = json.dumps(
        original, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return {
        "profile": "dapane-mchs-atlas-prepared/0.1",
        "status": "prepared",
        "requests": requests,
        "payments": payments,
        "provenance": original,
        "adapter_input_digest": "sha256:"
        + hashlib.sha256(b"dapane:mchs-atlas:0.1\n" + encoded).hexdigest(),
    }


def evaluate(
    bundle: dict[str, Any],
    *,
    evaluator: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Evaluate each explicit view using the installed Rust binding or a trusted bridge.

    A custom evaluator must call the same qualified Dapane native core (for
    example, its CLI). No formulas or payment aggregation live in this package.
    Any failure raises; partial reports are never returned as complete.
    """
    prepared = prepare(bundle)
    if evaluator is None:
        try:
            from dapane import evaluate as evaluator
        except ImportError as error:
            raise AdapterError(
                "native_unavailable",
                "Install a qualified Dapane wheel or supply its native CLI bridge.",
            ) from error
    reports = {}
    for name, request in sorted(prepared["requests"].items()):
        try:
            report = evaluator(copy.deepcopy(request))
        except ValueError as error:
            if isinstance(error, AdapterError):
                raise
            if all(
                isinstance(getattr(error, key, None), str) for key in ("code", "message", "path")
            ):
                raise AdapterError(
                    error.code, error.message, f"/requests/{name}{error.path}"
                ) from error
            raise
        if (
            type(report) is not dict
            or report.get("status") != "complete"
            or report.get("policy") != request["policy"]
        ):
            fail(
                "invalid_native_report",
                "Native evaluator returned an incomplete or incompatible report.",
                f"/requests/{name}",
            )
        reports[name] = report
    if prepared["payments"]:
        reports["payment"] = {
            "records": prepared["payments"], "aggregation": "not_performed"
        }
    return {
        "profile": "dapane-mchs-atlas-result/0.1",
        "status": "complete",
        "views": reports,
        "provenance": prepared["provenance"],
        "adapter_input_digest": prepared["adapter_input_digest"],
    }
