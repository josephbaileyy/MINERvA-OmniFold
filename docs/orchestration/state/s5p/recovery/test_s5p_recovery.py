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


def product(path: Path, x, meta: dict):
    np.savez_compressed(path, xsec_flat=x, xtrue_flat=x * 2, meta=json.dumps(meta))


# the real layout (s5p_nullexp.py:343-351): ``refinement`` sits at the TOP level (``**ev`` from unfold_one)
BASE_META = {"schema": "s5p-null-experiment/1", "pseudo_seed": 7, "split_key": "k",
             "nuisance_draw": {"normalization_z": 0.1},
             "code_sha256": {"a": "1"}, "input_npz_sha256": "n", "bkg_dump_sha256": "b", "config": "R", "iters": 5,
             "capacity": None, "hypothesis": {"sha256": "h"}, "alternative": None,
             "estimator_params": [{"num_threads": 32, "seed": 42}], "development": {"expectation": False},
             "detector_bands": ["d"], "model_bands": ["m"],
             "refinement": {"seconds": 1.0, "n_clipped": 3, "classifier_params": {"num_leaves": 31}},
             "experiment": {"refinement": {"seconds": 2.0}},
             "slurm_job": "111", "seconds_unfold": 10.0}
R.split_key_for = lambda seed: "k"  # the fixture's split key (the real one is s5c_pseudo.split_key_for)


class Determinism(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.x = np.arange(10, dtype=np.float64)

    def meta(self, **kw):
        m = json.loads(json.dumps(BASE_META))
        for k, v in kw.items():
            if k == "refinement_seconds":
                m["refinement"]["seconds"] = v
                m["experiment"]["refinement"]["seconds"] = v + 1
            else:
                m[k] = v
        return m

    def test_only_volatile_fields_differ_passes(self):
        product(self.tmp / "a.npz", self.x, self.meta())
        product(self.tmp / "b.npz", self.x.copy(), self.meta(slurm_job="222", seconds_unfold=99.0, refinement_seconds=5.5))
        same, diffs, _, mb = R.products_equivalent(self.tmp / "a.npz", self.tmp / "b.npz")
        self.assertTrue(same, diffs)
        self.assertEqual(mb["slurm_job"], "222")

    def test_a_non_volatile_meta_field_fails(self):
        product(self.tmp / "a.npz", self.x, self.meta())
        product(self.tmp / "b.npz", self.x, self.meta(nuisance_draw={"normalization_z": 0.2}))
        same, diffs, _, _ = R.products_equivalent(self.tmp / "a.npz", self.tmp / "b.npz")
        self.assertFalse(same)
        self.assertIn("nuisance_draw", diffs[0])

    def test_a_top_level_refinement_non_volatile_field_fails(self):
        m = self.meta()
        m["refinement"]["n_clipped"] = 4
        product(self.tmp / "a.npz", self.x, self.meta())
        product(self.tmp / "b.npz", self.x, m)
        self.assertFalse(R.products_equivalent(self.tmp / "a.npz", self.tmp / "b.npz")[0])

    def test_estimator_params_difference_fails(self):
        product(self.tmp / "a.npz", self.x, self.meta())
        product(self.tmp / "b.npz", self.x, self.meta(estimator_params=[{"num_threads": 16, "seed": 42}]))
        self.assertFalse(R.products_equivalent(self.tmp / "a.npz", self.tmp / "b.npz")[0])

    def test_a_nested_non_volatile_field_fails(self):
        m = self.meta()
        m["experiment"]["refinement"]["n_clipped"] = 4
        product(self.tmp / "a.npz", self.x, self.meta())
        product(self.tmp / "b.npz", self.x, m)
        self.assertFalse(R.products_equivalent(self.tmp / "a.npz", self.tmp / "b.npz")[0])

    def test_one_ulp_in_an_array_fails(self):
        y = self.x.copy()
        y[3] = np.nextafter(y[3], 10.0)
        product(self.tmp / "a.npz", self.x, self.meta())
        product(self.tmp / "b.npz", y, self.meta())
        same, diffs, _, _ = R.products_equivalent(self.tmp / "a.npz", self.tmp / "b.npz")
        self.assertFalse(same)
        self.assertIn("xsec_flat", diffs[0])

    def setup_cmd(self, rerun_job="222", same_file=False):
        tdir = self.tmp / "tables"
        tdir.mkdir()
        prod = self.tmp / "prod"
        prod.mkdir()
        write_table(tdir, "cal-X-b0.tsv", [row("cal-X-b0_0", 7, 7, str(prod))])
        product(prod / "cal_X_s7.npz", self.x, self.meta())
        rerun_dir = self.tmp / "rec" / "determinism" / "cal" / "X"
        rerun_dir.mkdir(parents=True)
        if same_file:
            (rerun_dir / "cal_X_s7.npz").symlink_to(prod / "cal_X_s7.npz")
        else:
            product(rerun_dir / "cal_X_s7.npz", self.x, self.meta(slurm_job=rerun_job, seconds_unfold=3.0))
        man = self.tmp / "man.json"
        man.write_text(json.dumps({"root": str(self.tmp / "rec"), "phase": "determinism", "n_seeds": 1,
                                   "tables": {"t": {"lane": "cal-X", "seeds": [7]}}}))
        jobs = self.tmp / "jobs.txt"
        jobs.write_text("222\n333_0\n")
        return ["determinism", "--manifest", str(man), "--tables", str(tdir), "--job-ids", str(jobs)]

    def test_cmd_passes_on_a_genuine_rerun(self):
        argv = self.setup_cmd()
        self.assertEqual(R.main(argv + ["--out", str(self.tmp / "o.json")]), 0)

    def test_cmd_refuses_the_same_file(self):
        argv = self.setup_cmd(same_file=True)
        self.assertEqual(R.main(argv + ["--out", str(self.tmp / "o.json")]), 1)

    def test_cmd_refuses_a_job_outside_the_array(self):
        argv = self.setup_cmd(rerun_job="999")
        self.assertEqual(R.main(argv + ["--out", str(self.tmp / "o.json")]), 1)

    def test_cmd_refuses_the_original_job(self):
        argv = self.setup_cmd(rerun_job="111")
        (self.tmp / "jobs.txt").write_text("111\n")
        self.assertEqual(R.main(argv + ["--out", str(self.tmp / "o.json")]), 1)


class Resolve(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        prod = self.tmp / "prod" / "cal" / "X"
        prod.mkdir(parents=True)
        x = np.arange(4.0)
        for s in (100, 200):
            product(prod / f"cal_X_s{s}.npz", x, dict(BASE_META, pseudo_seed=s))
        (prod / "cal_X_s101.partial-9.npz").write_bytes(b"partial")
        self.rec = self.tmp / "rec" / "recovery" / "cal" / "X"
        self.rec.mkdir(parents=True)
        product(self.rec / "cal_X_s101.npz", x, dict(BASE_META, pseudo_seed=101, slurm_job="5"))
        self.design = self.tmp / "design.json"
        self.design.write_text(json.dumps({"nulls": {"X": {"calibration_glob": str(prod / "cal_X_s*.npz"),
                                                            "calibration_n": {"sequential_status": "/x"}}}}))
        self.man = self.tmp / "man.json"
        self.man.write_text(json.dumps({"root": str(self.tmp / "rec"), "phase": "recovery",
                                        "tables": {"t": {"lane": "cal-X", "seeds": [101]}}}))

    def resolve(self, ss, union="u", residual=None):
        p = self.tmp / f"ss-{union}.json"
        p.write_text(json.dumps(ss))
        extra = []
        if residual is not None:
            r = self.tmp / f"res-{union}.json"
            r.write_text(json.dumps(residual))
            extra = ["--residual", str(r)]
        return R.main(["resolve", "--design", str(self.design), "--manifest", str(self.man), "--seed-states", str(p),
                       "--union-root", str(self.tmp / union), "--out-design", str(self.tmp / f"d-{union}.json")] + extra)

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
        product(self.rec / "cal_X_s100.npz", np.arange(4.0), dict(BASE_META, pseudo_seed=100))
        ss = seed_states("cal-X", {100: ("completed", 0), 101: ("interrupted", 1), 200: ("completed", 0)})
        with self.assertRaises(SystemExit):
            self.resolve(ss, union="w")


class ResolveResidualAndProvenance(unittest.TestCase):
    SS = {100: ("completed", 0), 101: ("interrupted", 1), 102: ("never started", 2), 200: ("completed", 0)}
    resolve = Resolve.resolve

    def setUp(self):
        Resolve.setUp(self)
        self.man.write_text(json.dumps({"root": str(self.tmp / "rec"), "phase": "recovery",
                                        "tables": {"t": {"lane": "cal-X", "seeds": [101, 102]}}}))

    def test_a_declared_residual_seed_may_stay_missing(self):
        self.assertEqual(self.resolve(seed_states("cal-X", self.SS), union="r1", residual=[102]), 0)
        rep = json.loads((self.tmp / "d-r1.report.json").read_text())
        self.assertEqual(rep["cal-X"]["residual_missing"], 1)
        self.assertEqual(json.loads((self.tmp / "d-r1.json").read_text())["nulls"]["X"]["calibration_n"], 3)

    def test_an_undeclared_missing_seed_fires(self):
        with self.assertRaises(SystemExit):
            self.resolve(seed_states("cal-X", self.SS), union="r2")

    def test_a_completed_seed_cannot_be_declared_residual(self):
        with self.assertRaises(SystemExit):
            self.resolve(seed_states("cal-X", self.SS), union="r3", residual=[102, 200])

    def test_provenance_mismatch_fires(self):
        product(self.rec / "cal_X_s101.npz", np.arange(4.0), dict(BASE_META, pseudo_seed=101, input_npz_sha256="other"))
        with self.assertRaises(SystemExit):
            self.resolve(seed_states("cal-X", self.SS), union="r4", residual=[102])

    def test_a_wrong_split_key_fires(self):
        product(self.rec / "cal_X_s101.npz", np.arange(4.0), dict(BASE_META, pseudo_seed=101, split_key="other"))
        with self.assertRaises(SystemExit):
            self.resolve(seed_states("cal-X", self.SS), union="r6", residual=[102])

    def test_a_failed_resolve_leaves_no_final_union(self):
        product(self.rec / "cal_X_s101.npz", np.arange(4.0), dict(BASE_META, pseudo_seed=999))
        with self.assertRaises(SystemExit):
            self.resolve(seed_states("cal-X", self.SS), union="r7", residual=[102])
        self.assertFalse((self.tmp / "r7").exists())

    def test_a_wrong_pseudo_seed_fires(self):
        product(self.rec / "cal_X_s101.npz", np.arange(4.0), dict(BASE_META, pseudo_seed=999))
        with self.assertRaises(SystemExit):
            self.resolve(seed_states("cal-X", self.SS), union="r5", residual=[102])


class Retry(unittest.TestCase):
    setUp = Tables.setUp

    def test_retry_only_of_lost_seeds(self):
        f = self.tmp / "seeds.json"
        f.write_text(json.dumps([102]))
        R.main(["tables", "--phase", "retry", "--seed-states", str(self.ss), "--tables", str(self.tdir),
                "--root", "/rec", "--out-dir", str(self.tmp / "rt"), "--seeds-file", str(f)])
        rows = [ln.split("\t") for ln in (self.tmp / "rt" / "rec-retry-cal-X.tsv").read_text().splitlines()[1:]]
        self.assertEqual([R.arg(r, "--out") for r in rows], ["/rec/recovery/cal/X"])
        f.write_text(json.dumps([200]))
        with self.assertRaises(SystemExit):
            R.main(["tables", "--phase", "retry", "--seed-states", str(self.ss), "--tables", str(self.tdir),
                    "--root", "/rec", "--out-dir", str(self.tmp / "rt2"), "--seeds-file", str(f)])


if __name__ == "__main__":
    unittest.main()
