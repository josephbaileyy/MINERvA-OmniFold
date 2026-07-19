import json
import os
import pathlib
import subprocess
import tempfile
import unittest


HERE = pathlib.Path(__file__).resolve().parent
WATCHER = HERE / "watch_slurm_array_resume.sh"


class WatcherTests(unittest.TestCase):
    def write_executable(self, path: pathlib.Path, body: str) -> None:
        path.write_text(body)
        path.chmod(0o700)

    def test_preflight_and_complete_wake_are_one_shot(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = pathlib.Path(raw)
            state = tmp / "state"
            state.mkdir()
            status = tmp / "status"
            codex = tmp / "codex"
            args_file = tmp / "codex.args"
            self.write_executable(
                status,
                "#!/bin/sh\nprintf '%s\\n' '{\"schema_version\":1,\"job_id\":\"42\",\"overall\":\"COMPLETE\",\"observer_errors\":[],\"unknown_tasks\":[],\"counts\":{\"COMPLETED\":2},\"tasks\":{}}'\n",
            )
            self.write_executable(
                codex,
                f"#!/bin/sh\nprintf '%s\\n' \"$@\" > {args_file}\nexit 0\n",
            )
            env = os.environ | {
                "WAKE_REPO": str(HERE.parent.parent),
                "WAKE_STATE_DIR": str(state),
                "WAKE_JOB_ID": "42",
                "WAKE_TASK_SPEC": "1-2",
                "WAKE_RUN_ID": "test-array",
                "WAKE_STATUS_BIN": str(status),
                "WAKE_POLL_SECONDS": "1",
                "CODEX_BIN": str(codex),
            }
            preflight = subprocess.run([WATCHER, "--preflight-only"], env=env, text=True, capture_output=True)
            self.assertEqual(preflight.returncode, 0, preflight.stderr)
            first = subprocess.run([WATCHER], env=env, text=True, capture_output=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            event = json.loads((state / "test-array-wakeup.json").read_text())
            self.assertEqual(event["event"], "slurm-array-complete")
            args = args_file.read_text()
            self.assertIn("exec\nresume\n--disable\ngoals", args)
            self.assertIn("--dangerously-bypass-approvals-and-sandbox", args)
            self.assertTrue((state / "test-array-resume.invoked").is_file())
            self.assertTrue((state / "test-array-resume.done").is_file())
            second = subprocess.run([WATCHER], env=env, text=True, capture_output=True)
            self.assertEqual(second.returncode, 126)
            self.assertIn("refuse to reuse occupied marker", second.stderr)


if __name__ == "__main__":
    unittest.main()
