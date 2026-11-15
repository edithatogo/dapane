"""Additional acceptance for the initially unexecuted result-bundle path."""

import unittest

from benchmarks.static.cache import WorkItem
from benchmarks.static.common import canonical
from benchmarks.static.run import Archive, comparison


class EchoRunner:
    """Returns transport echoes rather than financial reports to trigger the oracle gate."""

    def fingerprint(self):
        return "unqualified-echo"

    def invoke(self, item):
        return canonical({"echo": item.payload.decode("utf-8")})


class BundleGateTests(unittest.TestCase):
    def test_failed_independent_check_cannot_produce_timing_summary(self):
        result = comparison(
            EchoRunner(), 2, "cold",
            {"warmup_pairs": 0, "measured_pairs": 1},
            Archive(),
        )
        self.assertFalse(result["passed"])
        self.assertIsNone(result["summary"])
        self.assertIn("failure", result["pairs"][0])
        self.assertIn("report_refs", result["pairs"][0]["full"])

    def test_archive_identity_includes_command_and_keeps_exact_transport_bytes(self):
        archive = Archive()
        items = {
            "point": WorkItem("evaluate", b'{"value":"1"}'),
            "interval": WorkItem("evaluate-intervals", b'{"value":"1"}'),
            "spelling": WorkItem("evaluate", b'{ "value": "1" }'),
        }
        refs = archive.inputs_for(items)
        self.assertEqual(len(set(refs.values())), 3)
        self.assertEqual(archive.inputs[refs["spelling"]]["payload_utf8"], '{ "value": "1" }')


if __name__ == "__main__":
    unittest.main()
