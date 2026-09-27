"""Controls for s5c_array.sh task selection: an array task runs its line; a non-array job (the meter omits
--array for --ntasks 1) runs line 0 only when the table has exactly one task line, and is refused otherwise;
outside Slurm it is refused. The pinned-tree refusal (exit 2 on a dirty/unpinned deploy) is reached after
task selection, so each case is observed through its message."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "s5c_array.sh"


def run(table_lines, env):
    with tempfile.TemporaryDirectory() as d:
        t = Path(d) / "t.tsv"
        t.write_text("# comment\n" + "".join(l + "\n" for l in table_lines))
        e = {k: v for k, v in os.environ.items() if not k.startswith("SLURM_")}
        e.update(env)
        return subprocess.run(["bash", str(SCRIPT), d, "0" * 40, str(t), d], env=e, capture_output=True, text=True)


class Tests(unittest.TestCase):
    def test_single_line_non_array_job_is_task_zero(self):
        r = run(["a\tx.py\t--n 1"], {"SLURM_JOB_ID": "1"})
        self.assertNotIn("not an array task", r.stderr)
        self.assertIn("refusing: deploy HEAD", r.stderr)  # it went on to the pinned-tree check

    def test_multi_line_non_array_job_is_refused(self):
        r = run(["a\tx.py", "b\tx.py"], {"SLURM_JOB_ID": "1"})
        self.assertEqual(r.returncode, 2)
        self.assertIn("not an array task and the table has 2 task lines", r.stderr)

    def test_outside_slurm_is_refused(self):
        r = run(["a\tx.py"], {})
        self.assertEqual(r.returncode, 2)
        self.assertIn("not an array task", r.stderr)

    def test_array_task_selects_its_index(self):
        r = run(["a\tx.py", "b\tx.py"], {"SLURM_JOB_ID": "1", "SLURM_ARRAY_TASK_ID": "1"})
        self.assertNotIn("not an array task", r.stderr)
        self.assertIn("refusing: deploy HEAD", r.stderr)


if __name__ == "__main__":
    unittest.main()
