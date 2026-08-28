import hashlib
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


import subprocess
import os
import sys

class MeasureScriptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="measure-script-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

        self.script_source = Path(__file__).parent / "measure_k0_farend_f1b_f17b.sh"
        self.script = self.root / "measure_k0_farend_f1b_f17b.sh"

        self.code_root = self.root / "code"
        self.tools_root = self.root / "tools"
        self.measurer = self.code_root / "docs" / "orchestration" / "measure_m1_m6.py"
        self.comparator = self.tools_root / "docs" / "orchestration" / "compare_m1_m6.py"
        self.expected = self.tools_root / "docs" / "orchestration" / "m1m6_expected_differences.json"
        self.preserver = self.tools_root / "docs" / "orchestration" / "preserve_f17b_record.py"

        self.measurer.parent.mkdir(parents=True)
        self.comparator.parent.mkdir(parents=True)

        self.measurer.write_text("import sys; sys.exit(0)", encoding="utf-8")
        self.measurer.chmod(0o755)

        comp_script = "import sys\n" \
                      "if '--record' in sys.argv:\n" \
                      "    idx = sys.argv.index('--record')\n" \
                      "    open(sys.argv[idx+1], 'w').write('{}')\n" \
                      "sys.exit(0)\n"
        self.comparator.write_text(comp_script, encoding="utf-8")
        self.comparator.chmod(0o755)

        real_preserver = Path(__file__).parent / "preserve_f17b_record.py"
        self.preserver.write_bytes(real_preserver.read_bytes())
        self.preserver.chmod(0o755)

        self.preserver_expected = hashlib.sha256(self.preserver.read_bytes()).hexdigest()
        PRESERVER_EXPECTED = self.preserver_expected

        script_text = self.script_source.read_text()
        script_text = script_text.replace("CANON=/pscratch/sd/j/josephrb/MINERvA-OmniFold", "CANON=${CANON}")
        script_text = script_text.replace("CODE_ROOT=/pscratch/sd/j/josephrb/k0r2/clean", "CODE_ROOT=${CODE_ROOT}")
        script_text = script_text.replace(
            'EXPECTED_PRESERVER_SHA256=ea2dea540e24c38abf8d63669f8d06989a05172b95f6b2e31afc7d79358fefd9',
            f'EXPECTED_PRESERVER_SHA256={PRESERVER_EXPECTED}'
        ) + "\nexit 0\n"
        self.script.write_text(script_text)
        self.script.chmod(0o755)

        self.expected.write_text("{}", encoding="utf-8")

        self.env = os.environ.copy()
        self.env.update({
            "MNV_TOOLS_ROOT": str(self.tools_root),
            "CODE_ROOT": str(self.code_root),
            "CANON": str(self.root / "canon"),
            "TMPDIR": str(self.root / "tmp"),
            "MNV_F17B_RECORD_PATH": str(self.root / "durable.json"),
            "PY": sys.executable,
            "MODE": "--measure"
        })
        Path(self.env["CODE_ROOT"]).mkdir(exist_ok=True)
        Path(self.env["CANON"]).mkdir(exist_ok=True)
        Path(self.env["TMPDIR"]).mkdir(exist_ok=True)
        Path(self.tools_root).mkdir(exist_ok=True)
        for p in [self.env["CODE_ROOT"], self.env["CANON"], self.tools_root]:
            subprocess.run(["git", "-C", p, "init"], check=True, capture_output=True)
            subprocess.run(["git", "-C", p, "config", "user.email", "test@test.com"], check=True, capture_output=True)
            subprocess.run(["git", "-C", p, "config", "user.name", "Test"], check=True, capture_output=True)
            subprocess.run(["git", "-C", p, "commit", "--allow-empty", "-m", "init"], check=True, capture_output=True)

    def run_script(self):
        return subprocess.run(["bash", str(self.script), "--measure"], env=self.env, capture_output=True, text=True)

    def test_s3_fires_swapping_preserver_exits_13(self):
        # Swap DURING invocation
        # We create a preserver that appends to itself while running.
        script_text = b"import sys\nopen(sys.argv[0], 'ab').write(b' changed')\nsys.exit(0)\n"
        self.preserver.write_bytes(script_text)

        # Update the expected hash so it passes the PRE check
        import hashlib
        h = hashlib.sha256(script_text).hexdigest()
        st = self.script.read_text()
        st = st.replace(f'EXPECTED_PRESERVER_SHA256={self.preserver_expected}', f'EXPECTED_PRESERVER_SHA256={h}')
        self.script.write_text(st)

        cp = self.run_script()
        self.assertEqual(cp.returncode, 13)
        self.assertIn("REFUSE: a tool changed on disk across its own invocation", cp.stdout)

    def test_s3_fires_preserver_changed_before_invocation(self):
        # Mutate preserver before script execution. The script has EXPECTED_PRESERVER_SHA256
        # matching the original real preserver.
        self.preserver.write_bytes(b"import sys\nsys.exit(0)\n")
        cp = self.run_script()
        self.assertEqual(cp.returncode, 13)
        self.assertIn("REFUSE: preserver changed on disk BEFORE invocation", cp.stdout)

    def test_s3_silent_unchanged_preserver_does_not_trip_bracket(self):
        cp = self.run_script()
        self.assertEqual(cp.returncode, 0)

    def test_s3_full_digests_trip_bracket_on_collision(self):
        # Two files with the same first 12 hex chars of SHA-256 (5c98ec1f4916)
        content_1 = b"blob 15930654\n"
        content_2 = b"blob 39102528\n"

        script_1 = b"import sys\n# " + content_1 + b"\nopen(sys.argv[0], 'wb').write(b'''import sys\\n# " + content_2 + b"\\n''')"
        self.preserver.write_bytes(script_1)

        # Update the mock script to expect script_1's hash
        h1 = hashlib.sha256(script_1).hexdigest()

        script_text = self.script.read_text()
        script_text = script_text.replace(
            f'EXPECTED_PRESERVER_SHA256={self.preserver_expected}',
            f'EXPECTED_PRESERVER_SHA256={h1}'
        )
        self.script.write_text(script_text)

        cp = self.run_script()
        self.assertEqual(cp.returncode, 13)
        self.assertIn("REFUSE: a tool changed on disk", cp.stdout)

    def test_s4_fires_measurer_failure_short_circuits_immediately(self):
        # Measurer fails
        self.measurer.write_text("import sys; sys.exit(7)")
        # Comparator asserts it is NEVER invoked!
        self.comparator.write_text("import sys; print('COMPARATOR INVOKED'); sys.exit(1)")

        cp = self.run_script()
        self.assertEqual(cp.returncode, 7)
        self.assertIn("REFUSE: measurer failed", cp.stdout)
        self.assertNotIn("COMPARATOR INVOKED", cp.stdout)
        self.assertNotIn("COMPARATOR EXIT", cp.stdout)

    def test_s4_silent_succeeding_measurer_proceeds(self):
        cp = self.run_script()
        self.assertEqual(cp.returncode, 0)
        self.assertIn("COMPARATOR EXIT", cp.stdout)


if __name__ == "__main__":
    unittest.main()
