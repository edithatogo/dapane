"""Deterministic synthetic reporting evidence over unchanged native run bundles."""

from __future__ import annotations

import copy
import hashlib
from urllib.parse import quote

from rdflib import RDF, Graph, URIRef

from .catalogue import COST, Catalogue
from .transport import (
    MAX_DECLARATION_BYTES,
    ReportingError,
    canonical,
    fail,
    fields,
    pointer_value,
    text,
)

CONTEXT = {
    "@version": 1.1,
    "cost": str(COST),
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "dcterms": "http://purl.org/dc/terms/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
}
BASIS_CHOICES = {
    "economic_cost": {"economic-opportunity"},
    "financial_cost": {"financial-expenditure", "accounting-cost"},
    "funding": {"funding-valuation"},
    "charge": {"tariff-valuation"},
}
FORMAT = "dapane-reporting-evidence/0.1"


def _iri(value: str) -> dict:
    return {"@id": value}


def _json(value: object) -> dict:
    return {"@value": copy.deepcopy(value), "@type": "@json"}


def _choice(value: object, choices: tuple | set, path: str) -> str:
    if not isinstance(value, str) or value not in choices:
        fail("unsupported_state", path, "unsupported explicit declaration")
    return value


def _declarations(declaration: dict, bundle: dict, catalogue: Catalogue) -> tuple:
    if len(canonical(declaration)) > MAX_DECLARATION_BYTES:
        fail("limit_exceeded", "/", "reporting declarations exceed byte limit")
    fields(
        declaration,
        {"format", "bundle_digest", "source_commits", "study", "profiles", "assertions"},
        "/",
    )
    if declaration["format"] != "dapane-reporting-declarations/0.1":
        fail("reporting_version", "/format", "unsupported reporting declaration version")
    if declaration["source_commits"] != catalogue.commits:
        fail("source_version_mismatch", "/source_commits", "declare exactly the pinned sources")
    if declaration["bundle_digest"] != bundle["bundle_digest"]:
        fail("bundle_version_mismatch", "/bundle_digest", "assertions belong to another snapshot")
    study = fields(
        declaration["study"], {"label", "method", "valuation_basis", "basis_rationale"}, "/study"
    )
    for name in study:
        text(study[name], "/study/" + name)
    if (COST[study["method"]], RDF.type, COST.CostingMethod) not in catalogue.ontology:
        fail("unknown_method", "/study/method", "method is absent from the pinned ontology")
    basis = bundle["request"]["policy"]["basis"]
    if study["valuation_basis"] not in BASIS_CHOICES[basis]:
        fail("basis_mismatch", "/study/valuation_basis", "explicit basis is incompatible with run")
    if not isinstance(declaration["profiles"], list) or not 1 <= len(declaration["profiles"]) <= 12:
        fail("invalid_profiles", "/profiles", "declare one to twelve distinct profiles")
    selected, profiles, applicable = set(), [], set()
    seen = set()
    for row in declaration["profiles"]:
        fields(row, {"id", "applicability", "rationale"}, "/profiles")
        ident = text(row["id"], "/profiles/id", limit=128)
        if ident in seen:
            fail("duplicate_profile", "/profiles/id", "profile may be declared only once")
        seen.add(ident)
        if ident not in catalogue.profiles:
            fail("unknown_profile", "/profiles/id", "profile is absent from pinned catalogue")
        profile = catalogue.profiles[ident]
        if profile["purpose"] != "reporting":
            fail("assessment_dimension", "/profiles/id", "appraisal is not reporting completeness")
        state = _choice(
            row["applicability"],
            catalogue.assertion_states["applicability"],
            "/profiles/applicability",
        )
        text(row["rationale"], "/profiles/rationale")
        if state != "not-applicable":
            selected.update(profile["requirements"])
        if state == "applicable":
            applicable.update(profile["requirements"])
        profiles.append(
            {
                **row,
                "iri": profile["iri"],
                "authority": profile["authority"],
                "mapping_review_status": profile["mapping_review_status"],
                "mapped_requirement_count": len(profile["requirements"]),
                "instruments": [
                    {
                        "instrument_id": source,
                        "instrument_version": catalogue.sources[source]["version"],
                        "category": catalogue.sources[source]["category"],
                        "source_status": catalogue.sources[source]["status"],
                        "extraction_scope": catalogue.sources[source]["verification_scope"],
                    }
                    for source in sorted(profile["sources"])
                ],
            }
        )
    if not isinstance(declaration["assertions"], list) or len(declaration["assertions"]) > 106:
        fail("invalid_assertions", "/assertions", "expected a bounded array of item declarations")
    assertions = {}
    for row in declaration["assertions"]:
        fields(
            row,
            {
                "instrument_id",
                "instrument_version",
                "item_id",
                "applicability",
                "reporting_status",
                "rationale",
                "review_status",
                "evidence",
            },
            "/assertions",
        )
        for name in ("instrument_id", "instrument_version", "item_id"):
            text(row[name], "/assertions/" + name, limit=128)
        key = (row["instrument_id"], row["item_id"])
        if key not in selected:
            fail("unknown_requirement", "/assertions", "item is not in an included profile")
        if key in assertions:
            fail("duplicate_assertion", "/assertions", "an item may be assessed only once")
        original = catalogue.requirements[key]
        if row["instrument_version"] != original["instrument_version"]:
            fail("source_version_mismatch", "/assertions", "original instrument version differs")
        state = _choice(
            row["applicability"],
            catalogue.assertion_states["applicability"],
            "/assertions/applicability",
        )
        status = _choice(
            row["reporting_status"],
            catalogue.assertion_states["assessmentStatus"],
            "/assertions/reporting_status",
        )
        _choice(row["review_status"], {"not-reviewed", "reviewed"}, "/assertions/review_status")
        if key not in applicable and state != "unresolved":
            fail("unresolved_profile", "/assertions", "resolve profile applicability before items")
        if row["rationale"] is not None:
            text(row["rationale"], "/assertions/rationale")
        if state == "not-applicable" and row["rationale"] is None:
            fail("missing_rationale", "/assertions/rationale", "not-applicable needs a rationale")
        if not isinstance(row["evidence"], list) or len(row["evidence"]) > 32:
            fail(
                "invalid_evidence", "/assertions/evidence", "expected at most 32 evidence locations"
            )
        if status in {"reported", "partial"} and not row["evidence"]:
            fail("missing_evidence", "/assertions/evidence", "reported/partial needs evidence")
        pointers = set()
        for evidence in row["evidence"]:
            fields(evidence, {"pointer", "note"}, "/assertions/evidence")
            text(evidence["note"], "/assertions/evidence/note")
            pointer_value(bundle, evidence["pointer"])
            if evidence["pointer"] in pointers:
                fail("duplicate_evidence", "/assertions/evidence", "duplicate evidence location")
            pointers.add(evidence["pointer"])
        assertions[key] = copy.deepcopy(row)
    return study, sorted(profiles, key=lambda p: p["id"]), selected, assertions


def _synthetic_sources(bundle: dict) -> list[dict]:
    """The first reporting candidate accepts public synthetic source declarations only."""
    result = {}

    def walk(value: object) -> None:
        if isinstance(value, dict):
            if {"id", "version", "evidence", "access", "validation"} <= set(value):
                if value["evidence"] != "synthetic" or value["access"] != "public":
                    fail(
                        "unsupported_source_scope",
                        "/source",
                        "candidate requires public synthetic inputs",
                    )
                result[canonical(value)] = value
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(bundle)
    return [result[key] for key in sorted(result)]


def export_evidence(
    history: list,
    declaration: dict,
    catalogue: Catalogue,
    *,
    expected_head_digest: str,
    as_of: str,
) -> dict:
    """Replay Rust per bundle, select history, and export bounded reporting assertions."""
    from scripts.verify_run_bundle import verify_history

    selection = verify_history(history, expected_head_digest=expected_head_digest, as_of=as_of)
    if selection["status"] != "active":
        fail("inactive_bundle", "/history", "no active snapshot at requested knowledge date")
    bundle = next(b for b in history if b["bundle_digest"] == selection["selected_digest"])
    sources = _synthetic_sources(bundle)
    study, profiles, selected, assertions = _declarations(declaration, bundle, catalogue)
    identity = hashlib.sha256(
        b"dapane:reporting:0.1\n"
        + canonical(
            {
                "bundle_digest": bundle["bundle_digest"],
                "head_digest": expected_head_digest,
                "as_of": as_of,
                "declaration": declaration,
                "source_manifest_digest": catalogue.manifest_digest,
                "mapping_digest": catalogue.mapping_digest,
                "catalogue_map_digest": catalogue.catalogue_map_digest,
            }
        )
    ).hexdigest()
    root = "urn:dapane:reporting:0.1:" + identity
    bundle_id, study_id, policy_id = root + ":bundle", root + ":study", root + ":policy"
    native_policy = bundle["report"]["policy"]
    perspective = COST[native_policy["perspective"]]
    extra_nodes = []
    if (perspective, RDF.type, COST.Perspective) not in catalogue.ontology:
        perspective = URIRef(root + ":perspective")
        extra_nodes.append(
            {
                "@id": str(perspective),
                "@type": "cost:Perspective",
                "rdfs:label": native_policy["perspective"],
            }
        )
    nodes = [
        {
            "@id": bundle_id,
            "@type": "cost:EvidenceArtifact",
            "rdf:value": _json(bundle),
            "cost:sourceDigest": bundle["bundle_digest"],
            "cost:evidenceStatus": "synthetic",
            "cost:accessStatus": "public",
            "cost:validationStatus": "native-replay-verified",
        },
        {
            "@id": study_id,
            "@type": "cost:CostingStudy",
            "rdfs:label": study["label"],
            "cost:hasPerspective": _iri(str(perspective)),
            "cost:valuationPolicy": _iri(policy_id),
            "cost:hasMethod": _iri(str(COST[study["method"]])),
        },
        {
            "@id": policy_id,
            "@type": "cost:ValuationPolicy",
            "rdf:value": _json(native_policy),
            "cost:valuationBasis": _iri(str(COST[study["valuation_basis"]])),
            "cost:hasPerspective": _iri(str(perspective)),
            "cost:currency": native_policy["currency"],
            "cost:priceYear": {"@value": str(native_policy["price_year"]), "@type": "xsd:gYear"},
            "cost:valuationRecipe": study["basis_rationale"],
        },
        *extra_nodes,
    ]
    rows, evidence_nodes = [], {}
    states = {
        app: dict.fromkeys(catalogue.assertion_states["assessmentStatus"], 0)
        for app in catalogue.assertion_states["applicability"]
    }
    for key in sorted(selected):
        source = catalogue.requirements[key]
        row = assertions.get(
            key,
            {
                "instrument_id": key[0],
                "instrument_version": source["instrument_version"],
                "item_id": key[1],
                "applicability": "unresolved",
                "reporting_status": "not-assessed",
                "rationale": None,
                "review_status": "not-reviewed",
                "evidence": [],
            },
        )
        evidence = []
        for location in row["evidence"]:
            iri = bundle_id + "#" + quote(location["pointer"], safe="/~")
            evidence.append(_iri(iri))
            evidence_nodes[iri] = {
                "@id": iri,
                "@type": "cost:EvidenceArtifact",
                "cost:sourceURL": _iri(iri),
                "cost:evidenceStatus": "synthetic",
                "cost:accessStatus": "public",
                "cost:validationStatus": "location-resolved-in-native-replayed-bundle",
            }
        assertion = {
            "@id": root + ":assertion:" + quote(key[0] + "/" + key[1], safe=""),
            "@type": "cost:ReportingAssertion",
            "cost:reportsRequirement": _iri(source["iri"]),
            "cost:assessedStudy": _iri(study_id),
            "cost:applicability": row["applicability"],
            "cost:assessmentStatus": row["reporting_status"],
            "cost:evidenceReference": evidence,
        }
        if row["rationale"] is not None:
            assertion["cost:applicabilityRationale"] = row["rationale"]
        nodes.append(assertion)
        rows.append(
            {
                **copy.deepcopy(source),
                **row,
                "review_status_authority": "caller-declared",
                "evidence_locations": [v["@id"] for v in evidence],
            }
        )
        states[row["applicability"]][row["reporting_status"]] += 1
    nodes.extend(evidence_nodes[key] for key in sorted(evidence_nodes))
    for source in sources:
        ident = root + ":source:" + hashlib.sha256(canonical(source)).hexdigest()
        node = {
            "@id": ident,
            "@type": "cost:EvidenceArtifact",
            "rdf:value": _json(source),
            "cost:versionLabel": source["version"],
            "cost:evidenceStatus": source["evidence"],
            "cost:accessStatus": source["access"],
            "cost:validationStatus": source["validation"],
        }
        if source.get("content_digest") is not None:
            node["cost:sourceDigest"] = source["content_digest"]
        nodes.append(node)
    payload = {
        "format": FORMAT,
        "qualification": "synthetic_candidate",
        "source_commits": catalogue.commits,
        "source_manifest": copy.deepcopy(catalogue.manifest),
        "source_manifest_digest": catalogue.manifest_digest,
        "contract_mapping_digest": catalogue.mapping_digest,
        "catalogue_map_digest": catalogue.catalogue_map_digest,
        "bundle_digest": bundle["bundle_digest"],
        "bundle_node": bundle_id,
        "history_head_digest": expected_head_digest,
        "as_of": as_of,
        "profiles": profiles,
        "requirements": rows,
        "coverage": {
            "requirement_count": len(rows),
            "states": states,
            "scope": "mapped original item identifiers only; no compliance score or full-checklist claim",
            "domain_only_instruments": sorted(
                {
                    i["instrument_id"]
                    for p in profiles
                    if p["applicability"] != "not-applicable"
                    for i in p["instruments"]
                    if i["extraction_scope"]["verified_mapping_count"] == 0
                }
            ),
        },
        "assessment_dimensions": {
            "reporting": "caller declarations with explicit unassessed defaults",
            "methodological_appraisal": "not-assessed",
            "computational_verification": {
                "status": "native-replay-verified",
                "engine_version": bundle["report"]["engine_version"],
                "method_version": bundle["report"]["method_version"],
                "scope": "existing bundle schema, lifecycle, digest and exact installed-Rust replay",
            },
            "empirical_validation": "not-assessed",
        },
    }
    document = {
        "@context": dict(CONTEXT),
        "@graph": [
            {
                "@id": root,
                "@type": "cost:EvidenceArtifact",
                "rdf:value": _json(payload),
                "cost:evidenceStatus": "synthetic",
                "cost:accessStatus": "public",
                "cost:validationStatus": "reporting-assertions-not-independently-reviewed",
                "dcterms:format": FORMAT,
                "dcterms:source": [
                    _iri(src["repository"] + "/tree/" + src["commit"])
                    for src in catalogue.manifest["sources"].values()
                ],
            },
            *nodes,
        ],
    }
    conforms, _ = validate_jsonld(document, catalogue)
    if not conforms:
        fail("shacl_nonconformance", "/", "evidence graph violates pinned upstream shapes")
    return document


def validate_jsonld(document: dict, catalogue: Catalogue) -> tuple[bool, str]:
    """Check graph conformance only; never certify evidence truth or native replay.

    Source pins and inline context are checked before RDF parsing. The verified
    ontology/catalogue/shapes use no OWL imports, rules, inference, remote contexts,
    SPARQL endpoints or JavaScript. Embedded rdf:JSON is opaque evidence data.
    """
    from pyshacl import validate

    fields(document, {"@context", "@graph"}, "/jsonld")
    if document["@context"] != CONTEXT:
        fail("remote_context", "/@context", "only the fixed inline prefix context is supported")
    nodes = document["@graph"]
    if not isinstance(nodes, list) or not 1 <= len(nodes) <= 10000:
        fail("invalid_graph", "/@graph", "expected a bounded local evidence graph")
    try:
        payload = nodes[0]["rdf:value"]["@value"]
        matches = (
            payload["format"] == FORMAT
            and payload["source_commits"] == catalogue.commits
            and payload["source_manifest_digest"] == catalogue.manifest_digest
            and payload["contract_mapping_digest"] == catalogue.mapping_digest
            and payload["catalogue_map_digest"] == catalogue.catalogue_map_digest
            and canonical(payload["source_manifest"]) == canonical(catalogue.manifest)
        )
    except (KeyError, TypeError, IndexError) as exc:
        raise ReportingError(
            "invalid_graph", "/@graph", "missing source-bound export payload"
        ) from exc
    if not matches:
        fail("source_version_mismatch", "/@graph", "export does not use pinned source snapshot")

    def local(value: object) -> None:
        if isinstance(value, dict):
            if value.get("@type") == "@json":
                fields(value, {"@type", "@value"}, "/json-literal")
                return
            if "@context" in value:
                fail("remote_context", "/@graph", "nested contexts are unsupported")
            for child in value.values():
                local(child)
        elif isinstance(value, list):
            for child in value:
                local(child)

    local(nodes)
    for node in nodes:
        if (
            not isinstance(node, dict)
            or not isinstance(node.get("@id"), str)
            or not node["@id"].startswith("urn:dapane:reporting:0.1:")
        ):
            fail("upstream_redefinition", "/@graph", "export nodes need local instance identities")
        for predicate in node:
            if predicate in {
                "@id",
                "@type",
                "rdf:value",
                "rdfs:label",
                "dcterms:format",
                "dcterms:source",
            }:
                continue
            if not predicate.startswith("cost:") or not any(
                catalogue.ontology.triples((COST[predicate.removeprefix("cost:")], None, None))
            ):
                fail("unknown_term", "/@graph", "unknown export predicate would lose meaning")
    raw = canonical(document)
    if len(raw) > 32 * 1024 * 1024:
        fail("limit_exceeded", "/@graph", "export exceeds byte limit")
    graph = Graph().parse(data=raw.decode("utf-8"), format="json-ld")
    if any(
        not str(subject).startswith("urn:dapane:reporting:0.1:") for subject in graph.subjects()
    ):
        fail(
            "upstream_redefinition", "/@graph", "nested nodes may not redefine upstream identities"
        )
    graph += catalogue.ontology
    graph += catalogue.graph
    conforms, _, report = validate(
        graph,
        shacl_graph=catalogue.shapes,
        inference="none",
        advanced=False,
        do_owl_imports=False,
        js=False,
        allow_infos=False,
        allow_warnings=False,
    )
    return bool(conforms), str(report)
