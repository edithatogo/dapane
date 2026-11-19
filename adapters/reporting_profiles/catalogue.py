"""Read pinned upstream products without fetching, copying or redefining semantics."""

from __future__ import annotations

import hashlib
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from rdflib import RDF, Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection

from .transport import MAX_SOURCE_BYTES, ReportingError, fail, parse_json

ADAPTER = Path(__file__).resolve().parent
ROOT = ADAPTER.parents[1]
COST = Namespace("https://w3id.org/uogto/packs/costing-valuation#")
SH = Namespace("http://www.w3.org/ns/shacl#")
CONTEXT_CATEGORIES = {"development_protocol", "evidence_review", "study_protocol"}
APPRAISAL_CATEGORIES = {"appraisal_instrument", "model_appraisal_guidance"}


@dataclass(frozen=True)
class Catalogue:
    """Content-qualified external snapshots and their original identity joins."""

    manifest: dict
    manifest_digest: str
    mapping_digest: str
    catalogue_map_digest: str
    ontology: Graph
    shapes: Graph
    graph: Graph
    sources: dict
    requirements: dict
    profiles: dict
    assertion_states: dict

    @property
    def commits(self) -> dict[str, str]:
        return {key: value["commit"] for key, value in self.manifest["sources"].items()}


def _source_bytes(root: Path, relative: str, expected: dict) -> bytes:
    path = root / relative
    try:
        for part in [path, *path.parents]:
            if part == root.parent:
                break
            if part.is_symlink():
                fail("source_path", relative, "snapshot members must not be symbolic links")
        if not path.is_file():
            fail("source_unavailable", relative, "pinned source file is unavailable")
        with path.open("rb") as stream:
            raw = stream.read(MAX_SOURCE_BYTES + 1)
    except OSError as exc:
        raise ReportingError("source_unavailable", relative, "cannot read pinned source") from exc
    if len(raw) > MAX_SOURCE_BYTES:
        fail("limit_exceeded", relative, "source file exceeds byte limit")
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if (len(raw), hashlib.sha256(raw).hexdigest(), blob) != (
        expected["bytes"],
        expected["sha256"],
        expected["git_blob"],
    ):
        fail("source_digest_mismatch", relative, "source differs from pinned Git object")
    return raw


def _graph(raw: bytes) -> Graph:
    # Explicit local bytes and format; RDFLib does not follow owl:imports.
    return Graph().parse(data=raw.decode("utf-8"), format="turtle")


def verify_contract_map(ontology: Graph) -> str:
    """Account for every property in the exact native schema snapshot."""
    raw = (ADAPTER / "contract-map.json").read_bytes()
    mapping = parse_json(raw, limit=MAX_SOURCE_BYTES)
    if mapping["format"] != "dapane-uogto-contract-map/0.1":
        fail("mapping_version", "/contract-map", "unsupported mapping version")
    for rule in mapping["rules"].values():
        for term in rule["terms"]:
            if not any(ontology.triples((COST[term], None, None))):
                fail("unknown_term", "/contract-map", "mapping references absent upstream term")
    for relative, expected in mapping["schemas"].items():
        data = (ROOT / relative).read_bytes()
        if hashlib.sha256(data).hexdigest() != expected["sha256"]:
            fail(
                "contract_version_mismatch",
                relative,
                "native schema changed; mapping review needed",
            )
        found = {}

        def walk(value: object, location: str = "") -> None:
            if isinstance(value, dict):
                if "properties" in value:
                    found[location or "/"] = set(value["properties"])
                for key, child in value.items():
                    walk(child, location + "/" + key)
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    walk(child, location + "/" + str(index))

        walk(parse_json(data, limit=MAX_SOURCE_BYTES))
        records = expected["records"]
        if set(found) != set(records):
            fail("mapping_incomplete", relative, "unaccounted native record")
        for location, names in found.items():
            record = records[location]
            if names != set(record["fields"]):
                fail("mapping_incomplete", relative + location, "unaccounted native field")
            for rule in record["fields"].values():
                if rule not in mapping["rules"]:
                    fail("mapping_incomplete", relative, "unresolved field mapping rule")
            for term in record["terms"]:
                if (COST[term], RDF.type, None) not in ontology:
                    fail("unknown_term", relative, "record refers to absent upstream term")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def load_catalogue(uogto: Path, standards_check: Path) -> Catalogue:
    """Verify exact local source bytes, counts, identities and extraction qualifications."""
    raw_manifest = (ADAPTER / "sources.lock.json").read_bytes()
    manifest = parse_json(raw_manifest)
    identity_raw = (ADAPTER / "catalogue-map.json").read_bytes()
    identities = parse_json(identity_raw)
    sources = {}
    for name, root in {"uogto": uogto, "standards_check": standards_check}.items():
        sources[name] = {
            relative: _source_bytes(root, relative, expected)
            for relative, expected in manifest["sources"][name]["files"].items()
        }
    external = sources["uogto"]
    ontology = _graph(external["ontologies/applied/costing-valuation.ttl"])
    graph = _graph(external["ontologies/reporting/costing-profiles.ttl"])
    shapes = _graph(external["shapes/costing-valuation.shacl.ttl"])
    receipt = parse_json(external["validation/costing-reporting-import.json"])
    registry = parse_json(
        sources["standards_check"]["reconciliations/costing/costing-standards-registry.json"]
    )
    mappings = parse_json(
        sources["standards_check"]["reconciliations/costing/costing-item-mappings.json"]
    )
    if receipt["source_commit"] != manifest["sources"]["standards_check"]["commit"]:
        fail("source_version_mismatch", "/sources", "UOGTO import uses another catalogue commit")
    for short, relative in {
        "registry": "reconciliations/costing/costing-standards-registry.json",
        "mappings": "reconciliations/costing/costing-item-mappings.json",
    }.items():
        if (
            receipt["input_sha256"][short]
            != hashlib.sha256(sources["standards_check"][relative]).hexdigest()
        ):
            fail("source_digest_mismatch", relative, "UOGTO import receipt does not match source")
    counts = {
        "source_records": len(registry["instruments"]),
        "instrument_versions": len(set(graph.subjects(RDF.type, COST.InstrumentVersion))),
        "context_publications": len(set(graph.subjects(RDF.type, COST.EvidenceArtifact))),
        "domains": len(set(graph.subjects(RDF.type, COST.ReportingDomain))),
        "requirements": len(set(graph.subjects(RDF.type, COST.ReportingRequirement))),
        "requirement_mappings": len(set(graph.subjects(RDF.type, COST.RequirementMapping))),
        "profiles": len(set(graph.subjects(RDF.type, COST.ReportingProfile))),
    }
    if counts != manifest["expected_counts"] or any(receipt[k] != v for k, v in counts.items()):
        fail("source_count_mismatch", "/sources", "upstream manifest and actual counts differ")
    source_rows = {row["id"]: row for row in registry["instruments"]}
    if len(source_rows) != counts["source_records"] or set(source_rows) != set(
        identities["sources"]
    ):
        fail("catalogue_identity", "/sources", "source identity map is incomplete")
    for key, row in source_rows.items():
        node = URIRef(identities["sources"][key])
        kind = (
            COST.EvidenceArtifact
            if row["category"] in CONTEXT_CATEGORIES
            else COST.InstrumentVersion
        )
        if (node, RDF.type, kind) not in graph or (
            graph.value(node, COST.versionLabel) != Literal(row["version"])
            or (node, COST.sourceURL, URIRef(row["primary_url"])) not in graph
        ):
            fail("catalogue_identity", key, "source version or category does not match upstream")
    requirements = {}
    for row in mappings["mappings"]:
        key = (row["instrument_id"], row["item_id"])
        source = source_rows[key[0]]
        if key in requirements or source["category"] in CONTEXT_CATEGORIES:
            fail("catalogue_identity", "/requirements", "duplicate item or contextual publication")
        if row["item_identifier_verified"] is not True or source["item_level_verified"] is not True:
            fail("unverified_identifier", "/requirements", "item extraction is not qualified")
        node = URIRef(identities["requirements"][key[0]][key[1]])
        version = URIRef(identities["sources"][key[0]])
        if (node, RDF.type, COST.ReportingRequirement) not in graph or (
            graph.value(node, COST.itemIdentifier) != Literal(key[1])
            or graph.value(node, COST.belongsToVersion) != version
        ):
            fail("catalogue_identity", "/requirements", "original item/version identity differs")
        requirements[key] = {
            "instrument_id": key[0],
            "instrument_version": source["version"],
            "item_id": key[1],
            "iri": str(node),
            "version_iri": str(version),
            "source_url": row["source_url"],
            "source_locator": row["source_locator"],
            "checked_on": row["checked_on"],
            "item_identifier_verified": row["item_identifier_verified"],
            "extraction_scope": source["verification_scope"],
            "mapping_status": mappings["mapping_status"],
            "mapping_review_status": receipt["mapping_review_status"],
        }
    if len(requirements) != counts["requirements"] or sum(
        len(rows) for rows in identities["requirements"].values()
    ) != len(requirements):
        fail("catalogue_identity", "/requirements", "requirement identity map is incomplete")
    per_source = Counter(key[0] for key in requirements)
    if dict(per_source) != receipt["requirement_counts_by_source"]:
        fail("source_count_mismatch", "/requirements", "per-instrument counts differ")
    for key, row in source_rows.items():
        scope = row["verification_scope"]
        if (
            scope["verified_mapping_count"] != per_source[key]
            or scope["full_checklist_transcription_added"] is not False
        ):
            fail("source_count_mismatch", key, "extraction scope/count does not match catalogue")
    by_iri = {row["iri"]: key for key, row in requirements.items()}
    sources_by_iri = {iri: key for key, iri in identities["sources"].items()}
    profiles = {}
    for key, iri in identities["profiles"].items():
        node = URIRef(iri)
        if (node, RDF.type, COST.ReportingProfile) not in graph:
            fail("catalogue_identity", key, "profile not present in pinned snapshot")
        selected = {
            sources_by_iri[str(v)] for v in graph.objects(node, COST.includesInstrumentVersion)
        }
        if any(source_rows[s]["category"] in CONTEXT_CATEGORIES for s in selected):
            fail("context_publication", key, "protocol/review cannot be an operational instrument")
        profiles[key] = {
            "iri": iri,
            "requirements": {by_iri[str(r)] for r in graph.objects(node, COST.includesRequirement)},
            "sources": selected,
            "authority": str(graph.value(node, COST.authority)),
            "mapping_review_status": str(graph.value(node, COST.validationStatus)),
            "purpose": "appraisal"
            if any(source_rows[s]["category"] in APPRAISAL_CATEGORIES for s in selected)
            else "reporting",
        }
    if len(profiles) != counts["profiles"]:
        fail("catalogue_identity", "/profiles", "profile identity map is incomplete")
    states = {}
    for prop in shapes.objects(COST.ReportingAssertionShape, SH.property):
        name = shapes.value(prop, SH.path)
        if name in {COST.applicability, COST.assessmentStatus}:
            states[str(name).split("#")[-1]] = tuple(
                str(v) for v in Collection(shapes, shapes.value(prop, SH["in"]))
            )
    return Catalogue(
        manifest,
        "sha256:" + hashlib.sha256(raw_manifest).hexdigest(),
        verify_contract_map(ontology),
        "sha256:" + hashlib.sha256(identity_raw).hexdigest(),
        ontology,
        shapes,
        graph,
        source_rows,
        requirements,
        profiles,
        states,
    )
