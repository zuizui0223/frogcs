from __future__ import annotations
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from fetch_pinned_naamp_sources import find_file, checked_write


class TestPinnedSource(unittest.TestCase):
    def test_no_outcomes_requested(self):
        meta = {"files": [
            {"name": "Runs.csv", "downloadUri": "https://example.org/runs"},
            {"name": "Stops.csv", "downloadUri": "https://example.org/stops"},
            {"name": "Counts.csv", "downloadUri": "https://example.org/counts"},
        ]}
        self.assertEqual(find_file(meta, "Runs.csv"), "https://example.org/runs")
        with self.assertRaisesRegex(ValueError, "forbidden"):
            find_file(meta, "Counts.csv")
        with self.assertRaisesRegex(ValueError, "exactly one"):
            find_file({"files": []}, "Runs.csv")

    def test_pin_drift_aborts_before_file_write(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
                checked_write(root, "Runs.csv", b"not the official data")
            self.assertFalse((root / "Runs.csv").exists())


if __name__ == "__main__":
    unittest.main()
