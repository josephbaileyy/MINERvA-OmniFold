"""Controls for s5p_requeue: the resumed queue begins at the running batch's wait line, keeps every later line
except the throttle value, and refuses an ambiguous or missing resume label."""
import sys
import unittest
from pathlib import Path

sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
import s5p_requeue as rq  # noqa: E402

Q = Path(__file__).resolve().parents[2] / "docs/orchestration/state/s5p/prod/queues/cal-MnvTune_v1.q"


class Tests(unittest.TestCase):
    def test_resume_from_the_running_batch_changes_only_the_throttle(self):
        lines = Q.read_text().splitlines()
        out = rq.requeue(lines, "s5p_cal_mnvtune_v1_b0", 3, "note")
        i = [k for k, ln in enumerate(lines) if "-n s5p-s5p_cal_mnvtune_v1_b0 " in ln and ln.startswith("until")][0]
        self.assertEqual(len(out) - 1, len(lines) - i)
        for a, b in zip(lines[i:], out[1:]):
            self.assertEqual(a.replace("--throttle 2 ", "--throttle 3 "), b)
        self.assertFalse(any("s5p_cal_mnvtune_v1_b0 --measures" in ln for ln in out))  # batch 0 is never resubmitted
        self.assertTrue(any("--label s5p_cal_mnvtune_v1_b1 " in ln for ln in out))

    def test_missing_label_is_refused(self):
        with self.assertRaises(SystemExit):
            rq.requeue(Q.read_text().splitlines(), "s5p_cal_nope_b0", 3, "n")


if __name__ == "__main__":
    unittest.main()
