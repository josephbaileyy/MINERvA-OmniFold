"""Controls for s5p_recovery.py. Each guard is tested in the direction it acts: it fires on a bad input and stays
silent on a good one."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import s5p_recovery as R  # noqa: E402


def row(name, first, last, out, tag="cal_X"):
    return [name, "s5p_nullexp.py", "--npz", "/a.npz", "--threads", "32", "--pseudo-seeds", f"{first}:{last}",
            "--tag", tag, "--out", out]


def write_table(d: Path, name: str, rows):
    (d / name).write_text("# header\n" + "\n".join("\t".join(r) for r in rows) + "\n")


def seed_states(lane, states):
    """states: {seed: (state, position)} in one task."""
    return {"tasks": [{"lane": lane, "seeds": {str(s): {"state": st, "position": p} for s, (st, p) in states.items()}}]}


class Tables(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.tdir = self.tmp / "tables"
        self.tdir.mkdir()
        write_table(self.tdir, "cal-X-b0.tsv", [row("cal-X-b0_0", 100, 102, "/prod/cal/X")])
        write_table(self.tdir, "cal-X-b1.tsv", [row("cal-X-b1_0", 200, 202, "/prod/cal/X")])
        ss = seed_states("cal-X", {100: ("completed", 0), 101: ("interrupted", 1), 102: ("never started", 2),
                                   200: ("completed", 0), 201: ("completed", 1), 202: ("completed", 2)})
        self.ss = self.tmp / "ss.json"
        self.ss.write_text(json.dumps(ss))

    def run_tables(self, phase, out="o"):
        return R.main(["tables", "--phase", phase, "--seed-states", str(self.ss), "--tables", str(self.tdir),
                       "--root", "/rec", "--out-dir", str(self.tmp / out)])

    def test_recovery_reruns_exactly_the_lost_seeds_with_frozen_args(self):
        self.assertEqual(self.run_tables("recovery"), 0)
        m = json.loads((self.tmp / "o" / "rec-recovery-manifest.json").read_text())
        self.assertEqual(m["n_seeds"], 2)
        rows = [ln.split("\t") for ln in (self.tmp / "o" / "rec-recovery-cal-X.tsv").read_text().splitlines()[1:]]
        self.assertEqual([R.arg(r, "--pseudo-seeds") for r in rows], ["101:101", "102:102"])
        frozen = row("cal-X-b0_0", 100, 102, "/prod/cal/X")
        for r in rows:
            self.assertEqual(R.arg(r, "--out"), "/rec/recovery/cal/X")
            # every other position is byte-identical to the frozen row
            diff = [i for i, (x, y) in enumerate(zip(r, frozen)) if x != y]
            self.assertEqual(diff, [0, frozen.index("--pseudo-seeds") + 1, frozen.index("--out") + 1])

    def test_parts_cover_every_row_once(self):
        R.main(["tables", "--phase", "recovery", "--seed-states", str(self.ss), "--tables", str(self.tdir),
                "--root", "/rec", "--out-dir", str(self.tmp / "p"), "--parts", "2"])
        m = json.loads((self.tmp / "p" / "rec-recovery-manifest.json").read_text())
        names = [ln.split("\t")[0] for i in (1, 2)
                 for ln in (self.tmp / "p" / f"rec-recovery-part{i}.tsv").read_text().splitlines()[1:]]
        self.assertEqual(sorted(names), ["cal-X-b0_0-s101-rec", "cal-X-b0_0-s102-rec"])
        self.assertEqual([x["ntasks"] for x in m["submission_parts"]], [1, 1])

    def test_determinism_picks_first_and_latest_position(self):
        self.assertEqual(self.run_tables("determinism"), 0)
        m = json.loads((self.tmp / "o" / "rec-determinism-manifest.json").read_text())
        self.assertEqual([s for t in m["tables"].values() for s in t["seeds"]], [100, 202])

    def test_seed_in_two_rows_fires(self):
        write_table(self.tdir, "cal-X-b2.tsv", [row("cal-X-b2_0", 202, 203, "/prod/cal/X")])
        with self.assertRaises(SystemExit):
            self.run_tables("recovery")

    def test_recovery_dir_equal_to_production_fires(self):
        write_table(self.tdir, "cal-X-b0.tsv", [row("cal-X-b0_0", 100, 102, "/rec/recovery/cal/X")])
        with self.assertRaises(SystemExit):
            self.run_tables("recovery", out="y")

    def test_no_overwrite(self):
        self.assertEqual(self.run_tables("recovery"), 0)
        with self.assertRaises(SystemExit):
            self.run_tables("recovery")


class Determinism(unittest.TestCase):
    def test_bitwise(self):
        tmp = Path(tempfile.mkdtemp())
        x = np.arange(10, dtype=np.float64)
        np.savez(tmp / "a.npz", xsec_flat=x, meta=np.array("m"))
        np.savez(tmp / "b.npz", xsec_flat=x.copy(), meta=np.array("m"))
        y = x.copy()
        y[3] = np.nextafter(y[3], 10.0)  # one ulp
        np.savez(tmp / "c.npz", xsec_flat=y, meta=np.array("m"))
        self.assertEqual(R.npz_identical(tmp / "a.npz", tmp / "b.npz"), (True, []))
        same, diffs = R.npz_identical(tmp / "a.npz", tmp / "c.npz")
        self.assertFalse(same)
        self.assertIn("xsec_flat", diffs[0])
        np.savez(tmp / "d.npz", xsec_flat=x)
        self.assertFalse(R.npz_identical(tmp / "a.npz", tmp / "d.npz")[0])


class Resolve(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        prod = self.tmp / "prod" / "cal" / "X"
        prod.mkdir(parents=True)
        for s in (100, 200):
            (prod / f"cal_X_s{s}.npz").write_bytes(b"p")
        (prod / "cal_X_s101.partial-9.npz").write_bytes(b"partial")
        self.rec = self.tmp / "rec" / "recovery" / "cal" / "X"
        self.rec.mkdir(parents=True)
        (self.rec / "cal_X_s101.npz").write_bytes(b"r")
        self.design = self.tmp / "design.json"
        self.design.write_text(json.dumps({"nulls": {"X": {"calibration_glob": str(prod / "cal_X_s*.npz"),
                                                            "calibration_n": {"sequential_status": "/x"}}}}))
        self.man = self.tmp / "man.json"
        self.man.write_text(json.dumps({"root": str(self.tmp / "rec"), "phase": "recovery",
                                        "tables": {"t": {"lane": "cal-X", "seeds": [101]}}}))

    def resolve(self, ss, union="u"):
        p = self.tmp / f"ss-{union}.json"
        p.write_text(json.dumps(ss))
        return R.main(["resolve", "--design", str(self.design), "--manifest", str(self.man), "--seed-states", str(p),
                       "--union-root", str(self.tmp / union), "--out-design", str(self.tmp / f"d-{union}.json")])

    def test_union_equals_submitted(self):
        ss = seed_states("cal-X", {100: ("completed", 0), 101: ("interrupted", 1), 200: ("completed", 0)})
        self.assertEqual(self.resolve(ss), 0)
        d = json.loads((self.tmp / "d-u.json").read_text())
        self.assertEqual(d["nulls"]["X"]["calibration_n"], 3)
        self.assertEqual(sorted(p.name for p in (self.tmp / "u" / "cal" / "X").iterdir()),
                         ["cal_X_s100.npz", "cal_X_s101.npz", "cal_X_s200.npz"])  # the partial is excluded
        self.assertIn("_report_only", d)

    def test_a_still_missing_seed_fires(self):
        ss = seed_states("cal-X", {100: ("completed", 0), 101: ("interrupted", 1), 102: ("never started", 2),
                                   200: ("completed", 0)})
        with self.assertRaises(SystemExit):
            self.resolve(ss, union="v")

    def test_a_seed_both_frozen_and_recovered_fires(self):
        (self.rec / "cal_X_s100.npz").write_bytes(b"dup")
        ss = seed_states("cal-X", {100: ("completed", 0), 101: ("interrupted", 1), 200: ("completed", 0)})
        with self.assertRaises(SystemExit):
            self.resolve(ss, union="w")


if __name__ == "__main__":
    unittest.main()
