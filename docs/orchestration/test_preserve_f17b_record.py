import json
from pathlib import Path
import tempfile
import unittest

import preserve_f17b_record


class PreserveF17BRecordTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="f17b-preserve-test.")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "scratch" / "record.json"
        self.destination = self.root / "durable" / "record.json"
        self.source.parent.mkdir()

    def test_valid_json_is_published_byte_for_byte(self):
        self.source.write_text(json.dumps({"verdict": "expected", "rows": [1, 2]}))
        receipt = preserve_f17b_record.preserve(self.source, self.destination)
        self.assertEqual(self.destination.read_bytes(), self.source.read_bytes())
        self.assertEqual(receipt["path"], str(self.destination))
        self.assertEqual(receipt["bytes"], len(self.source.read_bytes()))
        self.assertEqual(len(receipt["sha256"]), 64)

    def test_existing_destination_is_never_overwritten(self):
        self.source.write_text('{"new": true}')
        self.destination.parent.mkdir()
        self.destination.write_text('{"old": true}')
        with self.assertRaises(FileExistsError):
            preserve_f17b_record.preserve(self.source, self.destination)
        self.assertEqual(self.destination.read_text(), '{"old": true}')
        self.assertEqual(list(self.destination.parent.glob(".*.tmp-*")), [])

    def test_invalid_json_is_not_published(self):
        self.source.write_text("not-json")
        with self.assertRaises(json.JSONDecodeError):
            preserve_f17b_record.preserve(self.source, self.destination)
        self.assertFalse(self.destination.exists())


if __name__ == "__main__":
    unittest.main()
