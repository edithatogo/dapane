"""Inspect only committed synthetic fixtures; this is not a runtime importer.

Standard-library XML/JSON reads establish fixture content and independent
expectations. They do not qualify Rust4PM, validate complete native standards,
or feed decoded events to the production contract validator.
"""

from __future__ import annotations

import hashlib
import json
import unittest
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
NS = {"xes": "http://www.xes-standard.org/"}


def unique_members(pairs):
    """Avoid last-write-wins while inspecting negative fixtures."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON member")
        result[key] = value
    return result


def fixture_json(name):
    return json.loads(
        (FIXTURES / name).read_text(encoding="utf-8"),
        object_pairs_hook=unique_members,
    )


def instant(value):
    """Independent comparison of fixed whole-second fixture timestamps."""
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("fixture timestamp has no offset")
    return parsed.astimezone(UTC)


def xes_events(name):
    """Inspect fixture attributes, retaining repeated event records."""
    root = ET.parse(FIXTURES / name).getroot()
    return [
        unique_members(
            [(child.attrib["key"], child.attrib["value"]) for child in event]
        )
        for event in root.findall("xes:trace/xes:event", NS)
    ]


def canonical_ocel_fixture(value):
    """Compare known fixture sets, including full attribute history."""
    if isinstance(value, dict):
        return {
            key: canonical_ocel_fixture(item) for key, item in sorted(value.items())
        }
    if isinstance(value, list):
        return sorted(
            (canonical_ocel_fixture(item) for item in value),
            key=lambda item: json.dumps(item, sort_keys=True),
        )
    return value


class SyntheticFixtureTests(unittest.TestCase):
    def setUp(self):
        self.expected = fixture_json("expected.json")

    def test_all_source_bytes_are_bound_to_explicit_unexecuted_cases(self):
        self.assertEqual(self.expected["fixture_status"], "synthetic")
        listed = {case["file"] for case in self.expected["cases"]}
        actual = {path.name for path in FIXTURES.iterdir()} - {"expected.json"}
        self.assertEqual(listed, actual)
        self.assertEqual(len(listed), 13)
        for case in self.expected["cases"]:
            with self.subTest(file=case["file"]):
                self.assertFalse(case["raw_decoder_executed"])
                digest = hashlib.sha256(
                    (FIXTURES / case["file"]).read_bytes()
                ).hexdigest()
                self.assertEqual(digest, case["sha256"])

    def test_three_hand_stated_uses_are_not_multiplied_by_related_objects(self):
        uses = self.expected["expected_uses"]
        self.assertEqual(len(uses), 3)
        self.assertEqual(
            {u["id"] for u in uses},
            {"collection-a", "collection-b", "batch-use"},
        )
        by_unit = {}
        for use in uses:
            quantity = use["quantity"]
            by_unit.setdefault(use["unit"], Fraction())
            by_unit[use["unit"]] += Fraction(
                int(quantity["numerator"]), int(quantity["denominator"])
            )
        self.assertEqual(by_unit, {"kit": Fraction(2), "hour": Fraction(1, 2)})
        batch = next(u for u in uses if u["id"] == "batch-use")
        self.assertEqual(len(batch["object_ids"]), 7)
        self.assertEqual(batch["event_ids"], ["run-start", "run-complete"])
        self.assertNotIn("quote_id", batch)

    def test_ocel_object_types_and_many_to_many_graph_match_manual_expectation(self):
        raw = fixture_json("many-to-many.ocel.json")
        self.assertEqual(
            {(o["id"], o["type"]) for o in raw["objects"]},
            {(o["id"], o["kind"]) for o in self.expected["objects"]},
        )
        actual = {
            (obj["id"], rel["objectId"], rel["qualifier"])
            for obj in raw["objects"]
            for rel in obj["relationships"]
        }
        expected = {
            (rel["from"], rel["to"], rel["qualifier"])
            for rel in self.expected["object_relations"]
        }
        self.assertEqual(actual, expected)
        self.assertEqual(len(actual), 8)
        for specimen in ["specimen-a", "specimen-b"]:
            self.assertTrue(
                {
                    (specimen, assay, "tested-by")
                    for assay in ["assay-a", "assay-b"]
                } <= actual
            )
        for event in raw["events"]:
            if event["id"] in ["run-start", "run-complete"]:
                self.assertEqual(len(event["relationships"]), 6)

    def test_ocel_retains_five_native_attribute_types_and_timed_history(self):
        raw = fixture_json("many-to-many.ocel.json")
        definition = next(
            t for t in raw["eventTypes"] if t["name"] == "run-complete"
        )
        self.assertEqual(
            {a["type"] for a in definition["attributes"]},
            {"integer", "float", "boolean", "string", "time"},
        )
        event = next(e for e in raw["events"] if e["id"] == "run-complete")
        values = {a["name"]: a["value"] for a in event["attributes"]}
        self.assertIs(type(values["sample-count"]), int)
        self.assertIs(type(values["accepted"]), bool)
        self.assertIs(type(values["control-ratio"]), float)
        self.assertEqual(values["sample-count"], 2)
        self.assertEqual(values["control-ratio"], 0.5)
        self.assertEqual(values["label"], "synthetic-run")
        self.assertEqual(
            instant(values["calibrated-at"]), instant("2026-01-01T00:00:00Z")
        )
        batch = next(o for o in raw["objects"] if o["id"] == "batch-1")
        self.assertEqual(
            [(a["time"], a["value"]) for a in batch["attributes"]],
            [
                ("2026-01-01T00:00:00Z", "queued"),
                ("2026-01-01T00:02:00Z", "running"),
                ("2026-01-01T00:32:00Z", "finished"),
            ],
        )

    def test_reordered_ocel_preserves_full_fixture_not_just_costing_projection(self):
        original = fixture_json("many-to-many.ocel.json")
        reordered = fixture_json("reordered.ocel.json")
        self.assertNotEqual(original, reordered)
        self.assertEqual(
            canonical_ocel_fixture(original), canonical_ocel_fixture(reordered)
        )

    def test_explicit_event_instants_match_independent_epoch_values(self):
        raw = fixture_json("many-to-many.ocel.json")
        epoch = datetime(1970, 1, 1, tzinfo=UTC)
        for event in raw["events"]:
            delta = instant(event["time"]) - epoch
            self.assertEqual(
                delta.days * 86400 + delta.seconds,
                self.expected["event_instants"][event["id"]],
            )

    def test_equivalent_offsets_are_different_bytes_with_same_event_instants(self):
        raw = fixture_json("many-to-many.ocel.json")
        offset = fixture_json("offset-equivalent.ocel.json")
        self.assertNotEqual(raw, offset)
        self.assertEqual(
            {e["id"]: instant(e["time"]) for e in raw["events"]},
            {e["id"]: instant(e["time"]) for e in offset["events"]},
        )
        first = xes_events("observed.xes")
        second = xes_events("offset-equivalent.xes")
        self.assertNotEqual(first, second)
        self.assertEqual(
            {e["identity:id"]: instant(e["time:timestamp"]) for e in first},
            {e["identity:id"]: instant(e["time:timestamp"]) for e in second},
        )

    def test_duplicate_id_cases_are_exact_duplicates_not_different_resource_use(self):
        raw = fixture_json("duplicate-id.ocel.json")
        self.assertEqual(
            Counter(e["id"] for e in raw["events"])["collect-a"], 2
        )
        self.assertEqual(raw["events"][0], raw["events"][-1])
        xes = xes_events("duplicate-id.xes")
        first = self.expected["xes_event_identity_map"]["collect-a"]
        self.assertEqual(Counter(e["identity:id"] for e in xes)[first], 2)
        self.assertEqual(xes[0], xes[-1])

    def test_duplicate_json_member_is_visible_to_the_independent_reader(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON member"):
            fixture_json("duplicate-member.ocel.json")

    def test_missing_timestamps_are_present_as_negative_cases(self):
        raw = fixture_json("missing-time.ocel.json")
        self.assertEqual(sum("time" not in e for e in raw["events"]), 1)
        self.assertEqual(
            sum("time:timestamp" not in e for e in xes_events("missing-time.xes")),
            1,
        )

    def test_right_censoring_has_no_invented_completion_or_quantity(self):
        raw = fixture_json("right-censored.ocel.json")
        self.assertEqual(
            {e["id"] for e in raw["events"]},
            {"collect-a", "collect-b", "run-start"},
        )
        expected = self.expected["right_censored_expectation"]
        self.assertIsNone(expected["end_event_id"])
        self.assertIsNone(expected["quantity"])
        self.assertEqual(expected["costing_readiness"], "CensoredUse")
        self.assertEqual(len(xes_events("right-censored.xes")), 3)
        batch = next(o for o in raw["objects"] if o["id"] == "batch-1")
        self.assertNotIn("finished", [a["value"] for a in batch["attributes"]])

    def test_xes_ids_and_explicit_lifecycle_anchors_survive_reordering(self):
        original = xes_events("observed.xes")
        reordered = xes_events("reordered.xes")
        self.assertNotEqual(original, reordered)
        self.assertEqual(
            {e["identity:id"]: e for e in original},
            {e["identity:id"]: e for e in reordered},
        )
        identity = self.expected["xes_event_identity_map"]
        self.assertEqual(
            {e["identity:id"] for e in original}, set(identity.values())
        )
        by_id = {e["identity:id"]: e for e in original}
        self.assertEqual(
            by_id[identity["run-start"]]["lifecycle:transition"], "start"
        )
        self.assertEqual(
            by_id[identity["run-complete"]]["lifecycle:transition"], "complete"
        )
        self.assertEqual(by_id[identity["run-start"]]["concept:name"], "run")
        self.assertEqual(by_id[identity["run-complete"]]["concept:name"], "run")


if __name__ == "__main__":
    unittest.main()
