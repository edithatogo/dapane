"""Synthetic reporting acceptance against pinned upstream products and installed Rust."""

import copy
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

from rdflib import RDF, Graph, URIRef

from adapters.reporting_profiles.catalogue import load_catalogue, verify_contract_map
from adapters.reporting_profiles.evidence import export_evidence, validate_jsonld
from adapters.reporting_profiles.transport import (
    ReportingError,
    canonical,
    parse_json,
    pointer_value,
)

ROOT = Path(__file__).resolve().parents[3]
SOURCES = Path(os.environ["DAPANE_REPORTING_SOURCES"])


def seal(bundle):
    """Independent transport digest; no valuation formula is implemented here."""
    raw = json.dumps(
        {key: value for key, value in bundle.items() if key != "bundle_digest"},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode()
    bundle["bundle_digest"] = (
        "sha256:" + hashlib.sha256(b"dapane:run-bundle:0.1\n" + raw).hexdigest()
    )
    return bundle


def fixture():
    """Read immutable synthetic native output, then require the verifier to replay it."""
    root = ROOT / "adapters/reporting_profiles/fixtures"
    bundle = json.loads((root / "synthetic-history.json").read_text())[0]
    declaration = json.loads((root / "synthetic-declarations.json").read_text())
    return bundle, declaration


def payload(output):
    return output["@graph"][0]["rdf:value"]["@value"]


class ReportingAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalogue = load_catalogue(SOURCES / "uogto", SOURCES / "standards_check")

    def setUp(self):
        self.bundle, self.declaration = fixture()

    def export(self):
        return export_evidence(
            [self.bundle],
            self.declaration,
            self.catalogue,
            expected_head_digest=self.bundle["bundle_digest"],
            as_of="2026-11-15",
        )

    def reseal(self):
        import dapane

        self.bundle["report"] = dapane.evaluate(self.bundle["request"])
        seal(self.bundle)
        self.declaration["bundle_digest"] = self.bundle["bundle_digest"]

    def test_source_counts_original_identifiers_and_contract_field_coverage(self):
        self.assertEqual(len(self.catalogue.sources), 26)
        self.assertEqual(len(self.catalogue.requirements), 106)
        self.assertIn(("agreedt_2018", "1.1"), self.catalogue.requirements)
        self.assertEqual(len(self.catalogue.profiles), 12)
        self.assertEqual(
            verify_contract_map(self.catalogue.ontology), self.catalogue.mapping_digest
        )
        mapping = json.loads((ROOT / "adapters/reporting_profiles/contract-map.json").read_text())
        self.assertEqual(
            sum(
                len(r["fields"]) for s in mapping["schemas"].values() for r in s["records"].values()
            ),
            281,
        )

    def test_native_baseline_and_positive_shacl(self):
        output = self.export()
        self.assertEqual(self.bundle["report"]["totals"]["rounded"], "150.00")
        self.assertEqual(
            sorted(
                x["total"]
                for x in self.bundle["report"]["object_totals"]
                if x["object_id"] in {"infant-a", "infant-b"}
            ),
            ["60.00", "90.00"],
        )
        p = payload(output)
        self.assertEqual(p["coverage"]["requirement_count"], 89)
        self.assertEqual(p["coverage"]["states"]["applicable"]["partial"], 1)
        self.assertEqual(p["coverage"]["states"]["unresolved"]["not-assessed"], 88)
        self.assertTrue(validate_jsonld(output, self.catalogue)[0])

    def test_missing_evidence_fails_closed(self):
        self.declaration = json.loads(
            (
                ROOT / "adapters/reporting_profiles/fixtures/reported-without-evidence.json"
            ).read_text()
        )
        with self.assertRaisesRegex(ReportingError, "missing_evidence"):
            self.export()

    def test_not_applicable_requires_rationale(self):
        self.declaration = json.loads(
            (
                ROOT / "adapters/reporting_profiles/fixtures/not-applicable-without-rationale.json"
            ).read_text()
        )
        with self.assertRaisesRegex(ReportingError, "missing_rationale"):
            self.export()

    def test_source_version_mismatch_fails_closed(self):
        self.declaration = json.loads(
            (ROOT / "adapters/reporting_profiles/fixtures/wrong-source-version.json").read_text()
        )
        with self.assertRaisesRegex(ReportingError, "source_version_mismatch"):
            self.export()

    def test_upstream_shacl_rejects_removed_evidence(self):
        output = self.export()
        assertion = next(
            n
            for n in output["@graph"]
            if n.get("@type") == "cost:ReportingAssertion"
            and n.get("cost:assessmentStatus") == "partial"
        )
        del assertion["cost:evidenceReference"]
        self.assertFalse(validate_jsonld(output, self.catalogue)[0])

    def test_upstream_shacl_rejects_invalid_not_applicable_assertion(self):
        output = self.export()
        assertion = next(n for n in output["@graph"] if n.get("@type") == "cost:ReportingAssertion")
        assertion["cost:applicability"] = "not-applicable"
        assertion.pop("cost:applicabilityRationale", None)
        self.assertFalse(validate_jsonld(output, self.catalogue)[0])

    def test_deterministic_and_lossless_native_payload(self):
        before = copy.deepcopy(self.bundle)
        output = self.export()
        self.assertEqual(output, self.export())
        node = next(n for n in output["@graph"] if n["@id"].endswith(":bundle"))
        self.assertEqual(canonical(node["rdf:value"]["@value"]), canonical(before))
        self.assertEqual(self.bundle, before)

    def test_all_reporting_and_applicability_states_remain_separate(self):
        self.declaration["assertions"] = []
        for item, (app, status) in enumerate(
            [
                ("applicable", "reported"),
                ("applicable", "partial"),
                ("applicable", "not-reported"),
                ("applicable", "not-assessed"),
                ("not-applicable", "not-assessed"),
                ("unresolved", "not-assessed"),
            ],
            1,
        ):
            self.declaration["assertions"].append(
                {
                    "instrument_id": "cheers_2022",
                    "instrument_version": "2022",
                    "item_id": str(item),
                    "applicability": app,
                    "reporting_status": status,
                    "rationale": "Synthetic scope excludes this item."
                    if app == "not-applicable"
                    else None,
                    "review_status": "not-reviewed",
                    "evidence": [{"pointer": "/report/policy", "note": "Synthetic policy."}]
                    if status in {"reported", "partial"}
                    else [],
                }
            )
        p = payload(self.export())
        states = p["coverage"]["states"]
        self.assertEqual(
            states["applicable"],
            dict.fromkeys(("reported", "partial", "not-reported", "not-assessed"), 1),
        )
        self.assertEqual(states["not-applicable"]["not-assessed"], 1)
        self.assertEqual(states["unresolved"]["not-assessed"], 84)
        self.assertEqual(p["assessment_dimensions"]["methodological_appraisal"], "not-assessed")
        self.assertEqual(p["assessment_dimensions"]["empirical_validation"], "not-assessed")
        self.assertTrue(
            all(
                r["mapping_review_status"] == "editorial_mapping_review_required"
                for r in p["requirements"]
            )
        )

    def test_domain_only_instrument_is_not_a_complete_checklist(self):
        self.declaration["profiles"] = [
            {
                "id": "budget-impact",
                "applicability": "applicable",
                "rationale": "Explicit synthetic budget-impact scope.",
            }
        ]
        self.declaration["assertions"] = []
        p = payload(self.export())
        self.assertEqual(p["coverage"]["requirement_count"], 0)
        self.assertEqual(p["coverage"]["domain_only_instruments"], ["ispor_bia_2014"])
        self.assertNotIn("score", p["coverage"])
        self.assertIs(
            p["profiles"][0]["instruments"][0]["extraction_scope"][
                "full_checklist_transcription_added"
            ],
            False,
        )

    def test_overlapping_profiles_deduplicate_original_requirements(self):
        self.declaration["profiles"].append(
            {
                "id": "general-costing",
                "applicability": "applicable",
                "rationale": "Synthetic overlap.",
            }
        )
        p = payload(self.export())
        self.assertEqual(p["coverage"]["requirement_count"], 89)
        self.assertEqual(len({(r["instrument_id"], r["item_id"]) for r in p["requirements"]}), 89)

    def test_not_applicable_profile_is_retained_without_invented_items(self):
        self.declaration["profiles"].append(
            {
                "id": "value-of-information",
                "applicability": "not-applicable",
                "rationale": "Synthetic scope performs no VOI analysis.",
            }
        )
        p = payload(self.export())
        self.assertEqual(p["coverage"]["requirement_count"], 89)
        self.assertEqual(p["profiles"][1]["applicability"], "not-applicable")

    def test_unknowns_context_publications_and_appraisals_fail_closed(self):
        for profile, code in [
            ("made-up-profile", "unknown_profile"),
            ("cheers_climate_2025", "unknown_profile"),
            ("economic-methods-appraisal", "assessment_dimension"),
        ]:
            with self.subTest(profile=profile):
                self.declaration["profiles"][0]["id"] = profile
                with self.assertRaisesRegex(ReportingError, code):
                    self.export()

    def test_unknown_requirement_wrong_version_and_unknown_states_fail(self):
        for name, value, code in [
            ("item_id", "999", "unknown_requirement"),
            ("instrument_version", "2013", "source_version_mismatch"),
            ("reporting_status", "passed", "unsupported_state"),
            ("applicability", "maybe", "unsupported_state"),
            ("review_status", "independently-verified", "unsupported_state"),
        ]:
            with self.subTest(field=name):
                old = self.declaration["assertions"][0][name]
                self.declaration["assertions"][0][name] = value
                with self.assertRaisesRegex(ReportingError, code):
                    self.export()
                self.declaration["assertions"][0][name] = old

    def test_duplicate_assertions_and_profiles_are_rejected(self):
        self.declaration["assertions"] *= 2
        with self.assertRaisesRegex(ReportingError, "duplicate_assertion"):
            self.export()
        self.declaration["assertions"] = self.declaration["assertions"][:1]
        self.declaration["profiles"] *= 2
        with self.assertRaisesRegex(ReportingError, "duplicate_profile"):
            self.export()

    def test_unknown_transport_field_is_not_ignored(self):
        self.declaration["endorsement"] = True
        with self.assertRaisesRegex(ReportingError, "invalid_fields"):
            self.export()

    def test_financial_basis_must_be_explicit_and_compatible(self):
        self.declaration["study"]["valuation_basis"] = "funding-valuation"
        with self.assertRaisesRegex(ReportingError, "basis_mismatch"):
            self.export()

    def test_source_status_declarations_are_never_promoted(self):
        output = self.export()
        originals = [n["rdf:value"]["@value"] for n in output["@graph"] if ":source:" in n["@id"]]
        self.assertTrue(originals)
        self.assertTrue(all(s["validation"] == "unvalidated" for s in originals))
        self.assertTrue(
            all(s["evidence"] == "synthetic" and s["access"] == "public" for s in originals)
        )

    def test_non_synthetic_or_private_source_scope_is_rejected(self):
        for field, value in [("evidence", "observed"), ("access", "private")]:
            with self.subTest(field=field):
                self.bundle, self.declaration = fixture()
                self.bundle["request"]["usage"][0]["source"][field] = value
                self.reseal()
                with self.assertRaisesRegex(ReportingError, "unsupported_source_scope"):
                    self.export()

    def test_unknown_or_empty_evidence_location_fails(self):
        for pointer, code in [
            ("/report/not-there", "invalid_pointer"),
            ("/report/lines/01", "invalid_pointer"),
            ("/report/~2bad", "invalid_pointer"),
            ("file:///etc/passwd", "invalid_pointer"),
            ("/reason", "empty_evidence"),
            ("/excluded_inputs", "empty_evidence"),
        ]:
            with self.subTest(pointer=pointer):
                self.declaration["assertions"][0]["evidence"][0]["pointer"] = pointer
                with self.assertRaisesRegex(ReportingError, code):
                    self.export()

    def test_rfc6901_escaping_and_explicit_zero_are_preserved(self):
        self.assertEqual(pointer_value({"a/b": {"~x": ["0.00", 0]}}, "/a~1b/~0x/0"), "0.00")
        self.assertEqual(pointer_value({"a/b": {"~x": ["0.00", 0]}}, "/a~1b/~0x/1"), 0)

    def test_native_schema_and_replay_reject_changed_reports(self):
        from scripts.verify_run_bundle import BundleError

        self.bundle["unknown"] = True
        seal(self.bundle)
        with self.assertRaisesRegex(BundleError, "invalid_bundle"):
            self.export()
        del self.bundle["unknown"]
        self.bundle["report"]["totals"]["rounded"] = "999.00"
        seal(self.bundle)
        with self.assertRaisesRegex(BundleError, "replay_mismatch"):
            self.export()

    def test_history_checkpoint_and_retraction_cannot_be_bypassed(self):
        from scripts.verify_run_bundle import BundleError

        tombstone = copy.deepcopy(self.bundle)
        tombstone.update(
            bundle_id="synthetic-retracted",
            change="retract",
            reason="Synthetic withdrawal.",
            previous_digest=self.bundle["bundle_digest"],
            request=None,
            report=None,
            observation_window=None,
            rate_releases=[],
            capital_treatments=[],
            excluded_inputs=[],
        )
        seal(tombstone)
        with self.assertRaisesRegex(BundleError, "checkpoint_mismatch"):
            export_evidence(
                [self.bundle],
                self.declaration,
                self.catalogue,
                expected_head_digest=tombstone["bundle_digest"],
                as_of="2026-11-15",
            )
        with self.assertRaisesRegex(ReportingError, "inactive_bundle"):
            export_evidence(
                [self.bundle, tombstone],
                self.declaration,
                self.catalogue,
                expected_head_digest=tombstone["bundle_digest"],
                as_of="2026-11-15",
            )

    def test_assertions_bind_to_selected_snapshot(self):
        self.declaration["bundle_digest"] = "sha256:" + "0" * 64
        with self.assertRaisesRegex(ReportingError, "bundle_version_mismatch"):
            self.export()

    def test_unknown_perspective_retains_label_without_guessing(self):
        self.bundle["request"]["policy"]["perspective"] = "synthetic-custom-view"
        self.reseal()
        output = self.export()
        node = next(n for n in output["@graph"] if n.get("@type") == "cost:Perspective")
        self.assertEqual(node["rdfs:label"], "synthetic-custom-view")

    def test_half_even_line_totals_are_preserved_without_aggregate_rerounding(self):
        for quote in self.bundle["request"]["quotes"]:
            quote["amount"] = "0.005"
        for usage in self.bundle["request"]["usage"]:
            usage["quantity"] = "1"
        self.reseal()
        self.assertEqual(self.bundle["report"]["totals"]["rounded"], "0.00")
        self.assertEqual(
            self.bundle["report"]["totals"]["exact"], {"numerator": "1", "denominator": "50"}
        )
        node = next(n for n in self.export()["@graph"] if n["@id"].endswith(":bundle"))
        self.assertEqual(node["rdf:value"]["@value"]["report"], self.bundle["report"])

    def test_jsonld_roundtrip_preserves_rdf_json_native_payload(self):
        output = self.export()
        graph = Graph().parse(data=canonical(output).decode(), format="json-ld")
        node = next(n for n in output["@graph"] if n["@id"].endswith(":bundle"))
        literal = graph.value(URIRef(node["@id"]), RDF.value)
        self.assertEqual(literal.datatype, RDF.JSON)
        self.assertEqual(canonical(json.loads(str(literal))), canonical(self.bundle))

    def test_graph_source_version_mismatch_is_not_shacl_success(self):
        output = self.export()
        payload(output)["source_commits"]["uogto"] = "0" * 40
        with self.assertRaisesRegex(ReportingError, "source_version_mismatch"):
            validate_jsonld(output, self.catalogue)

    def test_remote_or_nested_contexts_rejected_before_rdf_parsing(self):
        output = self.export()
        output["@context"] = "https://example.invalid/context.jsonld"
        with self.assertRaisesRegex(ReportingError, "remote_context"):
            validate_jsonld(output, self.catalogue)
        output = self.export()
        output["@graph"][0]["@context"] = "file:///etc/passwd"
        with self.assertRaisesRegex(ReportingError, "remote_context"):
            validate_jsonld(output, self.catalogue)

    def test_unknown_graph_terms_and_nested_redefinition_fail(self):
        output = self.export()
        output["@graph"][0]["mispelled"] = "lost by permissive JSON-LD parsers"
        with self.assertRaisesRegex(ReportingError, "unknown_term"):
            validate_jsonld(output, self.catalogue)
        del output["@graph"][0]["mispelled"]
        output["@graph"][0]["cost:evidenceReference"] = {
            "@id": "https://w3id.org/uogto/packs/costing-valuation#ResourceUse",
            "@type": "cost:ReportingAssertion",
        }
        with self.assertRaisesRegex(ReportingError, "upstream_redefinition"):
            validate_jsonld(output, self.catalogue)

    def test_loading_and_export_perform_no_network_operations(self):
        with ExitStack() as stack:
            for target in ("socket.create_connection", "urllib.request.urlopen"):
                stack.enter_context(patch(target, side_effect=AssertionError("network attempted")))
            stack.enter_context(
                patch.object(
                    socket.socket, "connect", side_effect=AssertionError("network attempted")
                )
            )
            load_catalogue(SOURCES / "uogto", SOURCES / "standards_check")
            self.export()

    def test_source_tampering_and_symlink_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "uogto"
            shutil.copytree(SOURCES / "uogto", root)
            member = root / "validation/costing-reporting-import.json"
            member.write_bytes(member.read_bytes() + b"\n")
            with self.assertRaisesRegex(ReportingError, "source_digest_mismatch"):
                load_catalogue(root, SOURCES / "standards_check")
            member.unlink()
            member.symlink_to(SOURCES / "uogto/validation/costing-reporting-import.json")
            with self.assertRaisesRegex(ReportingError, "source_path"):
                load_catalogue(root, SOURCES / "standards_check")

    def test_duplicate_keys_nonfinite_and_oversized_transport_fail(self):
        for raw, code in [
            (b'{"a":1,"a":2}', "duplicate_key"),
            (b'{"a":NaN}', "invalid_json"),
            (b'"' + b"x" * (1024 * 1024) + b'"', "limit_exceeded"),
        ]:
            with self.subTest(code=code), self.assertRaisesRegex(ReportingError, code):
                parse_json(raw)

    def test_cli_success_and_failure_have_distinct_atomic_output(self):
        with tempfile.TemporaryDirectory() as directory:
            history = Path(directory) / "history.json"
            declaration = Path(directory) / "declaration.json"
            history.write_bytes(canonical([self.bundle]))
            declaration.write_bytes(canonical(self.declaration))
            command = [
                sys.executable,
                "-m",
                "adapters.reporting_profiles",
                str(history),
                str(declaration),
                "--uogto",
                str(SOURCES / "uogto"),
                "--standards-check",
                str(SOURCES / "standards_check"),
                "--head",
                self.bundle["bundle_digest"],
                "--as-of",
                "2026-11-15",
            ]
            result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), self.export())
            self.declaration["assertions"][0]["evidence"] = []
            declaration.write_bytes(canonical(self.declaration))
            result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(result.stdout, "")
            self.assertEqual(json.loads(result.stderr)["error"]["code"], "missing_evidence")

    def test_static_native_valuation_available_without_reporting_dependencies(self):
        import dapane

        script = (
            "import sys,json; sys.path.insert(0,sys.argv[1]); import dapane; "
            "r=dapane.evaluate(json.load(open(sys.argv[2]))); "
            "assert not any(n in sys.modules for n in ['rdflib','pyshacl','adapters.reporting_profiles']); "
            "print(r['totals']['rounded'])"
        )
        result = subprocess.run(
            [
                sys.executable,
                "-I",
                "-S",
                "-c",
                script,
                str(Path(dapane.__file__).parents[1]),
                str(ROOT / "fixtures/newborn-screening.json"),
            ],
            cwd=ROOT.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "150.00")

    def test_unknown_node_class_is_rejected(self):
        output = self.export()
        output["@graph"][1]["@type"] = "cost:Typo"
        with self.assertRaisesRegex(ReportingError, "unknown_term"):
            validate_jsonld(output, self.catalogue)

    def test_nested_unknown_predicate_is_rejected(self):
        output = self.export()
        output["@graph"][0]["cost:evidenceReference"] = {
            "@id": output["@graph"][0]["@id"] + ":nested",
            "misspelled": "lost data",
        }
        with self.assertRaisesRegex(ReportingError, "unknown_term"):
            validate_jsonld(output, self.catalogue)

    def test_ontology_class_cannot_be_used_as_an_export_predicate(self):
        output = self.export()
        output["@graph"][0]["cost:ResourceUse"] = "not a property"
        with self.assertRaisesRegex(ReportingError, "unknown_term"):
            validate_jsonld(output, self.catalogue)

    def test_duplicate_node_identity_is_rejected(self):
        output = self.export()
        output["@graph"].append(copy.deepcopy(output["@graph"][1]))
        with self.assertRaisesRegex(ReportingError, "duplicate_node"):
            validate_jsonld(output, self.catalogue)

    def test_unresolved_profile_does_not_imply_item_applicability(self):
        self.declaration["profiles"][0]["applicability"] = "unresolved"
        with self.assertRaisesRegex(ReportingError, "unresolved_profile"):
            self.export()
        self.declaration["assertions"][0]["applicability"] = "unresolved"
        states = payload(self.export())["coverage"]["states"]
        self.assertEqual(states["unresolved"]["partial"], 1)
        self.assertEqual(sum(states["applicable"].values()), 0)

    def test_rational_inputs_and_exact_rounded_difference_survive(self):
        for usage in self.bundle["request"]["usage"]:
            usage["quantity"] = {"numerator": "1", "denominator": "3"}
        self.reseal()
        self.assertEqual(
            self.bundle["report"]["totals"]["exact"], {"numerator": "106", "denominator": "3"}
        )
        self.assertEqual(self.bundle["report"]["totals"]["rounded"], "35.34")
        node = next(n for n in self.export()["@graph"] if n["@id"].endswith(":bundle"))
        self.assertEqual(node["rdf:value"]["@value"], self.bundle)


if __name__ == "__main__":
    unittest.main()
