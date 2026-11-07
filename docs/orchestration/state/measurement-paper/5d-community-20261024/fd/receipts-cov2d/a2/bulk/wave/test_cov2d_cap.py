"""The companion test of cov2d_cap.py (the director's ruling, point 4): on a stub where sacct omits the last submitted
id, the recompute refuses when the true total is over the cap and stays silent when it is not.

    python3 -B -m unittest test_cov2d_cap -v
"""
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

import cov2d_cap as cc

M = "a60547692df5f963e428cdfe4661fc51ab785b7b"
OLD = "cb31611ca8b96ed2d1eeb809fda7236e56645863"
ENDED = ["60848251|cov2d-pseudo_G18|COMPLETED|8674|1|180",
         "60857636|cov2d-pilot|COMPLETED|2702|1|101",
         "60860645|cov2d-pseudo_AR23|FAILED|4323|1|180",
         "60889690|cov2d-pseudo_AR23|COMPLETED|9104|1|240"]          # stage 3's sacct rows: 6.8897 node-h spent
SPENT = (8674 + 2702 + 4323 + 9104) / 3600


def sub(id_, job, limit, m=M):
    return "2026-11-06T09:08:10Z M=%s job=%s id=%s limit=%s" % (m, job, id_, limit)


class Recompute(unittest.TestCase):
    def test_fires_on_the_unlisted_id_when_the_true_total_is_over(self):
        # listed: spent 6.89 + 17 pending at 08:54:00 (151.3) = 158.19; the last submitted id is not in sacct yet
        pend = ["%d|cov2d-X%d|PENDING|0|1|534" % (700 + i, i) for i in range(17)]
        subs = [sub(700 + i, "X%d" % i, "08:54:00") for i in range(17)] + [sub(799, "G18_Ta", "07:38:00")]
        rec = cc.recompute(ENDED + pend, subs, M, "03:20:00")
        self.assertEqual(rec["unlisted_ids"], ["799"])
        self.assertAlmostEqual(rec["total"], SPENT + 17 * 8.9 + 458 / 60 + 200 / 60)
        self.assertGreater(rec["total"], cc.CAP)
        self.assertFalse(rec["pass"])
        # the control: without the unlisted line the same sacct passes, so the refusal came from the unlisted term
        self.assertTrue(cc.recompute(ENDED + pend, subs[:-1], M, "03:20:00")["pass"])

    def test_silent_with_an_unlisted_id_when_the_true_total_is_under(self):
        subs = [sub(800, "G18_Ua", "08:54:00")]
        rec = cc.recompute(ENDED, subs, M, "08:06:00")
        self.assertEqual(rec["unlisted_ids"], ["800"])
        self.assertAlmostEqual(rec["total"], SPENT + 8.9 + 8.1)
        self.assertTrue(rec["pass"])

    def test_replays_stage_3_at_AR23_Uc(self):
        # the gate saw held 35.6 (four G18 universe jobs) and total 51.39; six were submitted at M before AR23_Uc
        u = ["G18_Ua", "G18_Ub", "G18_Uc", "G18_Ud", "AR23_Ua", "AR23_Ub"]
        ids = ["60895562", "60895566", "60895578", "60895585", "60895594", "60895595"]
        sacct = ENDED + ["%s|cov2d-%s|PENDING|0|1|534" % (i, j) for i, j in zip(ids[:4], u[:4])]
        subs = [sub("60857636", "pilot", "01:41:00", OLD), sub("60860645", "pseudo_AR23", "03:00:00", OLD),
                sub("60889690", "pseudo_AR23", "04:00:00")] + [sub(i, j, "08:54:00") for i, j in zip(ids, u)]
        rec = cc.recompute(sacct, subs, M, "08:54:00")
        self.assertEqual(rec["unlisted_ids"], ["60895594", "60895595"])
        self.assertAlmostEqual(rec["held"], 6 * 8.9)
        self.assertAlmostEqual(rec["total"], 69.18972222222222)

    def test_at_the_cap_passes_and_just_over_refuses(self):
        rows = ["1|cov2d-A|COMPLETED|%d|1|600" % int((cc.CAP - 1) * 3600)]
        self.assertTrue(cc.recompute(rows, [], M, "01:00:00")["pass"])
        self.assertFalse(cc.recompute(rows, [], M, "01:00:01")["pass"])

    def test_rows_it_must_ignore_or_count(self):
        rows = ["5|fd_c2c1r|PENDING|0|1|150",                         # another lane's job: not priced
                "6|cov2d-A|CANCELLED by 123|3600|1|600",             # ended: its elapsed
                "7|cov2d-B|COMPLETING|100|1|60",                     # not known terminal: its limit
                "8|cov2d-C|RUNNING|100|2|60"]                        # nodes multiply
        subs = [sub(9, "D", "01:00:00", OLD), sub(7, "B", "01:00:00")]   # another M's id; a listed id is not re-added
        rec = cc.recompute(rows, subs, M, "00:00:00")
        self.assertEqual(rec["unlisted_ids"], [])
        self.assertAlmostEqual(rec["spent"], 1.0)
        self.assertAlmostEqual(rec["held"], 1.0 + 2.0)

    def test_unusable_input_refuses(self):
        with self.assertRaises(cc.Unusable):
            cc.recompute(["1|cov2d-A|PENDING|0|1|UNLIMITED"], [], M, "01:00:00")
        with self.assertRaises(cc.Unusable):
            cc.recompute(["1|cov2d-A|PENDING|0|1"], [], M, "01:00:00")
        with self.assertRaises(cc.Unusable):
            cc.recompute([], ["2026 M=%s job=A" % M], M, "01:00:00")


class Cli(unittest.TestCase):
    def run_cli(self, sacct, subs, limit):
        with tempfile.TemporaryDirectory() as d:
            ps, pl = os.path.join(d, "s.psv"), os.path.join(d, "submissions.log")
            with open(ps, "w") as f:
                f.write("\n".join(sacct) + "\n")
            with open(pl, "w") as f:
                f.write("\n".join(subs) + "\n")
            out = io.StringIO()
            with redirect_stdout(out):
                rc = cc.main(["--sacct", ps, "--submissions", pl, "--M", M, "--limit", limit])
            return rc, json.loads(out.getvalue())

    def test_exit_codes(self):
        pend = ["%d|cov2d-X%d|PENDING|0|1|534" % (700 + i, i) for i in range(17)]
        subs = [sub(700 + i, "X%d" % i, "08:54:00") for i in range(17)]
        self.assertEqual(self.run_cli(ENDED + pend, subs, "03:20:00")[0], 0)
        rc, rec = self.run_cli(ENDED + pend, subs + [sub(799, "T", "07:38:00")], "03:20:00")
        self.assertEqual((rc, rec["pass"], rec["unlisted_ids"]), (3, False, ["799"]))
        self.assertEqual(self.run_cli(["1|cov2d-A|PENDING|0|1|UNLIMITED"], [], "01:00:00")[0], 2)


if __name__ == "__main__":
    unittest.main()
