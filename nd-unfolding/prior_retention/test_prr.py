"""Tests of FD-PRR (FD-PRR-DECLARATION.md rev 2): the levels, the truths against F0's pins, the queues through the real
runner's parser, the mask, the gate and its price, staging, C-PAIR, route 2's capture and unfold, and every reading in
the direction it acts and the other.

Run: python3 -B -m unittest nd-unfolding/prior_retention/test_prr.py (no LightGBM, no ROOT, no cluster: the estimators
are deterministic stand-ins, the inputs synthetic rows on the real 5D fine grid).
"""
import contextlib
import io
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ND = HERE.parent
REPO = ND.parent
for _p in (HERE, ND, ND / "tests", ND / "pv-ladder"):
    if str(_p) not in sys.path:
        sys.path.insert(1, str(_p))
import prr_ibu as R  # noqa: E402
import prr_probe as P  # noqa: E402
import prr_read as RD  # noqa: E402
import estimator_stability_probe as esp  # noqa: E402
import fd_f0_regrade as F0  # noqa: E402
import omnifold_nn_core as onc  # noqa: E402
import s5c_unfold  # noqa: E402
import s5n_pseudo  # noqa: E402
import test_estimator_stability_probe as T  # noqa: E402  (FD-STAB's synthetic inputs and pvl ratio writer)

if not hasattr(os, "O_NOATIME"):  # macOS: REF-G1's copy reads os.O_NOATIME at each open; a 0 flag is a plain read
    os.O_NOATIME = 0


def quiet():
    return contextlib.redirect_stderr(io.StringIO())


# ============================================================================================ pins and truths
class Pins(unittest.TestCase):
    def test_every_bound_module_is_its_pinned_file(self):
        P.check_pins()
        P.check_pins(R.CODE_PINS)
        RD.check_inputs(REPO)

    def test_a_changed_module_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            rel = next(iter(P.CODE_PINS))
            (Path(d) / rel).parent.mkdir(parents=True)
            shutil.copy(REPO / rel, Path(d) / rel)
            P.check_pins({rel: P.CODE_PINS[rel]}, Path(d))
            (Path(d) / rel).write_text((Path(d) / rel).read_text() + "\n")
            with self.assertRaises(P.Refused):
                P.check_pins({rel: P.CODE_PINS[rel]}, Path(d))

    def test_a_changed_input_stops_the_reader(self):
        with tempfile.TemporaryDirectory() as d:
            rel = next(iter(RD.INPUT_PINS))
            (Path(d) / rel).parent.mkdir(parents=True)
            (Path(d) / rel).write_bytes(b"x")
            with self.assertRaises(RD.Stop):
                RD.check_inputs(Path(d), {rel: RD.INPUT_PINS[rel]})


class Truths(unittest.TestCase):
    def test_the_truths_are_table_iis_twelve_in_f0s_order(self):
        graded = [t["name"] for t in F0.TRUTHS if t["row"] in (1, 2, 3, 4)]
        self.assertEqual(list(P.TRUTHS), graded)
        self.assertEqual(len(P.TRUTHS), 12)

    def test_each_truth_is_fd_stabs_closure_row_unchanged(self):
        rows = {r[0]: r for r in esp.CLOSURES}
        for t in P.TRUTHS:
            self.assertEqual(P.closure_spec(t), rows[t])

    def test_every_committed_truth_file_carries_f0s_pin(self):
        hyp = {"nominal": "mnvtune_v1", "A7_mnvtune": "mnvtune_v1", "W1": "mnvtune_v1", "W2": "mnvtune_v1",
               "W3": "mnvtune_v1", "q3": "mnvtune_v1", "stage0c_gibuu": "mnvtune_v1", "closure_nuwro": "mnvtune_v1",
               "A7_genie_cv": "genie_cv", "A7_genie_mec": "genie_mec", "A7_nuwro": "nuwro_cv", "A7_gibuu": "gibuu_cv"}
        alt = {"W1": "W1", "W2": "W2", "W3": "W3", "stage0c_gibuu": "gibuu"}
        for t in P.TRUTHS:
            name, h, a, kind, amp = P.closure_spec(t)
            self.assertEqual(P.sha256_path(REPO / h), F0.HYP[hyp[t]], t)
            if t in alt:
                self.assertEqual(P.sha256_path(REPO / a), F0.RATIO[alt[t]], t)
        self.assertEqual(RD.expected_truth("closure_nuwro", REPO)["alt"]["sha256"], F0.RATIO["closure_nuwro"])
        self.assertEqual(RD.expected_truth("closure_nuwro", REPO)["alt"]["truth"], esp.PVL_TRUTH)

    def test_the_flagged_truths_are_table_iis_flags(self):
        ro = json.loads((REPO / RD.FD / "with-cpl/readout/fd_f0b_readout.json").read_text())
        flagged = sorted(x["name"] for x in ro["truths"] if x["name"] in P.TRUTHS
                         and (x["grade"]["p_lt_0.01"] or x["grade"]["cells_abs_z_gt_2"]))
        self.assertEqual(flagged, sorted(P.FLAGGED))

    def test_the_floor_seeds_are_no_campaigns(self):
        self.assertNotIn(991001, P.FLOOR_SEEDS)
        self.assertTrue(set(P.FLOOR_SEEDS).isdisjoint({esp.CLOSURE_SEED, esp.STABILITY_PSEUDO_SEED}))
        if shutil.which("git") and (REPO / ".git").exists():
            hits = subprocess.run(["git", "-C", str(REPO), "grep", "-l", "-E", r"(^|[^0-9.a-f])99400[1-4]([^0-9]|$)",
                                   "--", "nd-unfolding", ":!nd-unfolding/prior_retention"],
                                  capture_output=True, text=True).stdout.split()
            self.assertEqual(hits, [])


# ============================================================================================ levels, tasks, price
class Levels(unittest.TestCase):
    def test_b0_is_configuration_e(self):
        self.assertEqual({k: P.LEVELS["B0"][k] for k in ("iters", "capacity", "mc_fraction", "mask")},
                         {"iters": 5, "capacity": None, "mc_fraction": "half", "mask": None})

    def test_each_level_changes_one_factor(self):
        b0 = P.LEVELS["B0"]
        for F, lvs in P.FACTORS.items():
            for lv in lvs:
                L = P.LEVELS[lv]
                self.assertEqual(L["factor"], F)
                changed = [k for k in ("iters", "capacity", "mc_fraction", "mask") if L[k] != b0[k]]
                self.assertEqual(changed, [{"F1": "iters", "F2": "capacity", "F3": "mc_fraction", "F4": "mask"}[F]], lv)
        self.assertEqual([P.LEVELS[l]["iters"] for l in P.FACTORS["F1"]], [2, 10, 20, 50])
        self.assertEqual([P.LEVELS[l]["capacity"] for l in P.FACTORS["F2"]], [(25, 4), (400, 31), (1000, 63)])

    def test_the_masks(self):
        self.assertEqual(P.MASKS["O5"], (P.AXES, P.AXES))
        self.assertEqual(P.MASKS["O4r"], (P.AXES, ("pt", "pz", "eavail", "q3")))
        self.assertEqual(P.MASKS["O4"], (("pt", "pz", "eavail", "q3"),) * 2)
        self.assertEqual(P.MASKS["O3"][0], ("pt", "pz", "eavail"))
        self.assertEqual(P.MASKS["O2"][1], ("pt", "pz"))

    def test_the_floor_levels_belong_to_their_factors(self):
        for F, lv in P.FLOOR_LEVEL.items():
            self.assertIn(lv, P.FACTORS[F])


class Tasks(unittest.TestCase):
    def test_the_declared_task_list(self):
        t = P.all_tasks()
        self.assertEqual(len(t), len(set(t)))
        self.assertEqual(len(t), 13 * 12 + 1 + 4 * 6)
        self.assertAlmostEqual(sum(P.units(x[0]) for x in t), 551.8, places=9)
        floor = [x for x in t if x[2] != P.PRIMARY_SEED]
        self.assertEqual(sorted({x[2] for x in floor}), list(P.FLOOR_SEEDS))
        self.assertEqual(sorted({(x[0], x[1]) for x in floor}),
                         sorted({(lv, "A7_gibuu") for lv in P.FLOOR_LEVELS} | {("B0", "nominal")}))

    def test_the_dry_run_measures_every_level_and_completes_c_pair(self):
        dry = [x for x in P.all_tasks() if P.job_of(*x) == "dry"]
        self.assertEqual(sorted({x[0] for x in dry}), sorted(P.LEVELS))
        self.assertIn(("B0", "A7_gibuu", P.PRIMARY_SEED), dry)
        self.assertIn(("O5", "nominal", P.PRIMARY_SEED), dry)
        self.assertEqual(len(dry), 15)

    def test_jobs_partition_the_tasks(self):
        by = {j: [x for x in P.all_tasks() if P.job_of(*x) == j] for j in P.JOBS}
        self.assertEqual(sum(map(len, by.values())), len(P.all_tasks()))
        self.assertTrue(all(P.LEVELS[x[0]]["factor"] == "F1" for x in by["iter"]))
        self.assertTrue(all(P.LEVELS[x[0]]["factor"] == "F2" for x in by["cap"]))
        self.assertEqual(sorted(x[1] for x in by["misc"] if x[0] == "C1000"), sorted(P.CAP_TO_MISC))

    def test_the_queue_is_longest_first(self):
        a = P.staged_paths(Path("/S"), Path("/R"))
        for j in P.JOBS:
            u = [float(l.split("\t")[2]) for l in P.queue_lines(a, j)[1:]]
            self.assertEqual(u, sorted(u, reverse=True), j)

    def test_queue_columns(self):
        a = P.staged_paths(Path("/S"), Path("/R"))
        line = P.queue_lines(a, "dry")[1].split("\t")
        self.assertEqual(line[0], P.task_id(line[1], "nominal", P.PRIMARY_SEED))
        self.assertEqual(line[3], "prior_retention/prr_probe.py")
        self.assertEqual(line[4], "run")


class Price(unittest.TestCase):
    def test_each_limit_passes_the_gate_at_the_conservative_unit(self):
        for j, v in P.price().items():
            self.assertGreaterEqual(v["limit_h"], v["least_limit_h"], j)

    def test_the_cap_is_the_sum_of_the_limits_and_each_is_under_12_h(self):
        self.assertAlmostEqual(sum(P.JOB_LIMIT_H.values()), P.CAP_NODE_H, places=12)
        self.assertTrue(all(h <= 12 for h in P.JOB_LIMIT_H.values()))
        self.assertEqual(set(P.JOB_LIMIT_H), set(P.JOBS) | {"ibu"})

    def test_the_expected_cost(self):
        self.assertAlmostEqual(551.8 * 0.022828, 12.5965, places=3)

    def test_limit_prints_h_mm_ss(self):
        with contextlib.redirect_stdout(io.StringIO()) as o:
            P.main(["limit", "dry"])
        self.assertEqual(o.getvalue().strip(), "5:15:00")
        with contextlib.redirect_stdout(io.StringIO()) as o:
            P.main(["limit", "ibu"])
        self.assertEqual(o.getvalue().strip(), "0:30:00")

    def test_pack_is_list_scheduling_with_its_tail(self):
        self.assertEqual(P.pack([10, 10, 10], lanes=2), 20)
        self.assertEqual(P.pack([5, 1, 1, 1, 1, 1], lanes=2), 5)
        self.assertEqual(P.pack([1, 1], lanes=2, busy=[4]), 4)
        self.assertEqual(P.pack([], lanes=8), 0.0)


# ============================================================================================ the gate
class Gate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        r = Path(self.tmp.name)
        self.q, self.log = r / "q.tsv", r / "log"
        self.log.mkdir()
        lines = ["# q"] + [f"prr_K50_W{i}_s991000\tK50\t10.0\tx\trun" for i in range(3)] + \
                [f"prr_B0_W{i}_s991000\tB0\t1.0\tx\trun" for i in range(3)]
        self.q.write_text("\n".join(lines) + "\n")

    def tearDown(self):
        self.tmp.cleanup()

    def end(self, tid, start, end):
        (self.log / f"{tid}.start").write_text(f"{start}\n")
        (self.log / f"{tid}.end").write_text(f"{end}\n")

    def test_the_dry_gate_admits_within_the_limit(self):
        self.assertEqual(P.gate("prr_B0_W0_s991000", self.q, self.log, 0.0, 5.25, "dry", now=0.0), 0)
        self.assertTrue((self.log / "prr_B0_W0_s991000.start").exists())

    def test_a_projection_over_0_9_of_the_limit_stops(self):
        self.assertEqual(P.gate("prr_B0_W0_s991000", self.q, self.log, 0.0, 1.0, "dry", now=0.0), 3)
        self.assertIn("0.9", json.loads((self.log / "STOP").read_text())["reason"])
        self.assertEqual(P.gate("prr_B0_W1_s991000", self.q, self.log, 0.0, 99.0, "dry", now=0.0), 3)

    def test_a_full_job_refuses_an_unmeasured_level(self):
        self.end("prr_B0_W9_s991000", 0.0, 600.0)
        self.assertEqual(P.gate("prr_B0_W0_s991000", self.q, self.log, 0.0, 99.0, "full", now=0.0), 3)
        self.assertIn("K50", json.loads((self.log / "STOP").read_text())["reason"])

    def test_a_full_job_runs_on_measured_rates(self):
        self.end("prr_B0_W9_s991000", 0.0, 600.0)
        self.end("prr_K50_W9_s991000", 0.0, 1000.0)
        self.assertEqual(P.gate("prr_B0_W0_s991000", self.q, self.log, 0.0, 99.0, "full", now=0.0), 0)
        p = P.project(0.0, 0.0, P.read_queue(self.q), P.read_log(self.log))
        self.assertEqual(p["rates_s"], {"B0": 600.0, "K50": 1000.0})
        self.assertAlmostEqual(p["projected_h"], 1000.0 / 3600)

    def test_measured_rates_move_the_projection_both_ways(self):
        self.end("prr_B0_W9_s991000", 0.0, 6000.0)
        self.end("prr_K50_W9_s991000", 0.0, 60000.0)
        p = P.project(0.0, 0.0, P.read_queue(self.q), P.read_log(self.log))
        self.assertAlmostEqual(p["projected_h"], 60000.0 / 3600)
        self.assertEqual(P.gate("prr_B0_W0_s991000", self.q, self.log, 0.0, 18.0, "full", now=0.0), 3)

    def test_an_ended_task_is_skipped_and_an_unknown_one_stops(self):
        self.end("prr_B0_W0_s991000", 0.0, 1.0)
        self.assertEqual(P.gate("prr_B0_W0_s991000", self.q, self.log, 0.0, 99.0, "dry", now=0.0), 4)
        self.assertEqual(P.gate("prr_B0_X_s991000", self.q, self.log, 0.0, 99.0, "dry", now=0.0), 3)

    def test_the_0_9_rule_is_exact(self):
        self.q.write_text("# q\nprr_B0_W0_s991000\tB0\t1.0\tx\trun\n")
        h = P.UNIT_S / 3600
        self.assertEqual(P.gate("prr_B0_W0_s991000", self.q, self.log, 0.0, h / 0.95, "dry", now=0.0), 3)
        (self.log / "STOP").unlink()
        self.assertEqual(P.gate("prr_B0_W0_s991000", self.q, self.log, 0.0, h / 0.85, "dry", now=0.0), 0)

    def test_the_tail_is_projected(self):
        lines = ["# q"] + [f"prr_K50_W{i}_s991000\tK50\t10.0\tx\trun" for i in range(9)]
        self.q.write_text("\n".join(lines) + "\n")
        p = P.project(0.0, 0.0, P.read_queue(self.q), {})
        self.assertAlmostEqual(p["projected_h"], 2 * 10 * P.UNIT_S / 3600)  # nine on eight lanes: one lane runs two


# ============================================================================================ the runner's parser
def synthetic_stage(d: Path):
    inp = T.fine_inputs()
    stage = d / "stage"
    (stage / "bank").mkdir(parents=True)
    T.write_npz(stage / "of_inputs_5d.npz", inp)
    rng = np.random.default_rng(5)
    np.savez(stage / "bkg_dump.npz", bkg_reco=inp["MCreco"][rng.integers(0, 6000, 800)], bkg_w=rng.uniform(0.1, 1, 800),
             bkg_nd=np.zeros(1), meta=json.dumps({"npz_sha256": "x"}))
    np.savez(stage / "bank" / "cv.npz", MCgen=inp["MCgen"])
    ratio_dir = stage / "pvl" / "prep" / "ratios" / "L-5D-PV"
    ratio_dir.mkdir(parents=True)
    ratio = T.write_pvl_ratio(ratio_dir)
    if ratio.name != "nuwro.json":
        ratio.rename(ratio_dir / "nuwro.json")
    a = P.staged_paths(stage, d / "runs")
    a.expect_npz_sha256, a.expect_bkg_sha256 = P.sha256_path(a.npz), P.sha256_path(a.bkg)
    return a, inp


class RealParser(unittest.TestCase):
    """Every queue line, through prr_probe.run into s5p_nullexp's own argparse, stopped once the namespace and column
    checks pass. Any SystemExit fails."""

    class Parsed(Exception):
        pass

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.a, _ = synthetic_stage(Path(self.tmp.name))
        self.real = P.check_namespace
        self.seen = []

        def stop(ns, level, truth):
            why = self.real(ns, level, truth)
            if why is None:
                P.check_columns(Path(ns.npz))
                self.seen.append((level, truth))
                raise self.Parsed()
            return why
        P.check_namespace = stop
        self.cwd = os.getcwd()
        os.chdir(REPO)

    def tearDown(self):
        P.check_namespace = self.real
        os.chdir(self.cwd)
        self.tmp.cleanup()

    def parse(self, cols):
        with quiet() as err:
            try:
                P.main(cols[4:])
            except SystemExit as e:
                self.fail(f"{cols[0]}: SystemExit {e.code}: {err.getvalue()[-300:]}")

    def test_every_queue_line_parses_and_passes_under_the_real_runner(self):
        n = 0
        for j in P.JOBS:
            for line in P.queue_lines(self.a, j)[1:]:
                cols = line.split("\t")
                with self.subTest(task=cols[0]), self.assertRaises(self.Parsed):
                    self.parse(cols)
                n += 1
        self.assertEqual(n, len(P.all_tasks()))
        self.assertEqual(len(self.seen), n)

    def refused(self, edit):
        line = P.queue_lines(self.a, "dry")[1]
        cols = line.split("\t")
        cols = edit(cols)
        with quiet():
            try:
                return P.main(cols[4:])
            except SystemExit as e:
                return e.code

    def test_the_refusals_fire_on_the_runners_parse(self):
        def setopt(name, value):
            def f(cols):
                cols = list(cols)
                cols[cols.index(name) + 1] = value
                return cols
            return f
        self.assertEqual(self.refused(setopt("--iters", "6")), 2)
        self.assertEqual(self.refused(setopt("--capacity", "400,31")), 2)
        self.assertEqual(self.refused(setopt("--mc-fraction", "quarter")), 2)
        self.assertEqual(self.refused(setopt("--pseudo-seeds", "991001:991001")), 2)
        self.assertEqual(self.refused(setopt("--pseudo-seeds", "994001:994001")), 2)  # C1000 is not a floor level
        self.assertEqual(self.refused(setopt("--threads", "16")), 2)
        self.assertEqual(self.refused(setopt("--hypothesis", P.closure_spec("A7_gibuu")[1])), 2)
        self.assertEqual(self.refused(lambda c: [x for x in c if x != "--expectation"]), 2)
        self.assertEqual(self.refused(lambda c: c + ["--iters", "5"]), 2)  # repeated
        self.assertEqual(self.refused(lambda c: [("--iter" if x == "--iters" else x) for x in c]), 2)  # abbreviated

    def test_the_refusal_is_on_the_parsed_namespace(self):
        ns = types.SimpleNamespace(config="R", expectation=True, no_nuisance=True, iters=5, capacity=None,
                                   mc_fraction="half", pseudo_seeds="994002:994002", estimator_seed=42, threads=32,
                                   hypothesis=P.closure_spec("A7_gibuu")[1], alternative=None, alternative_amplitude=1.0)
        self.assertIsNone(self.real(ns, "B0", "A7_gibuu"))
        self.assertIsNotNone(self.real(ns, "K10", "A7_gibuu"))
        self.assertIsNotNone(self.real(ns, "B0", "W1"))


class Columns(unittest.TestCase):
    def test_the_input_columns_are_checked_not_assumed(self):
        with tempfile.TemporaryDirectory() as d:
            inp = T.fine_inputs(n=300)
            T.write_npz(Path(d) / "ok.npz", inp)
            self.assertEqual(P.check_columns(Path(d) / "ok.npz"), P.AXES)
            arrays = dict(np.load(Path(d) / "ok.npz", allow_pickle=True))
            arrays["axes"] = np.array(["eavail", "W", "q3"], dtype=object)
            np.savez(Path(d) / "swapped.npz", **arrays)
            with self.assertRaises(P.Refused):
                P.check_columns(Path(d) / "swapped.npz")
            arrays = dict(np.load(Path(d) / "ok.npz", allow_pickle=True))
            arrays["edges_2"] = arrays["edges_2"] * 1.01
            np.savez(Path(d) / "edges.npz", **arrays)
            with self.assertRaises(P.Refused):
                P.check_columns(Path(d) / "edges.npz")


# ============================================================================================ the mask and the install
class Linear:
    """A deterministic smooth stand-in with LightGBM's surface (fit, predict_proba, predict, get/set_params)."""

    def __init__(self, **params):
        self.params = dict(params)

    def get_params(self, deep=True):
        return dict(self.params)

    def set_params(self, **params):
        self.params.update(params)
        return self

    def fit(self, X, y, sample_weight=None):
        X = np.asarray(X, float)
        self.coef = np.linalg.lstsq(np.c_[X, np.ones(len(X))], np.asarray(y, float), rcond=None)[0]
        return self

    def _z(self, X):
        return np.c_[np.asarray(X, float), np.ones(len(X))] @ self.coef

    def predict_proba(self, X):
        p = 1 / (1 + np.exp(-np.clip(self._z(X), -5, 5)))
        return np.column_stack([1 - p, p])

    def predict(self, X):
        return 1.0 + 0.1 * np.tanh(self._z(X))


class Mask(unittest.TestCase):
    def setUp(self):
        self.saved = (onc.make_estimators, onc.omnifold_loop)
        onc.make_estimators = lambda kind, nvars, seed=None: (Linear(), Linear(), Linear())
        self.inp = T.fine_inputs(n=1500, seed=2)
        self.inp["pass_truth"] = np.ones(1500, bool)

    def tearDown(self):
        onc.make_estimators, onc.omnifold_loop = self.saved

    def unfold(self, mask):
        rec = {}
        with P.column_mask(mask, rec):
            xs, _ = s5c_unfold.unfold(self.inp, "production", 42, 1, 2)
        return xs, rec

    def test_the_five_column_mask_is_a_bitwise_pass_through(self):
        a, _ = self.unfold(None)
        b, rec = self.unfold("O5")
        self.assertTrue(np.array_equal(a, b))
        self.assertEqual(rec["calls"], 1)

    def test_each_mask_hands_the_loop_its_columns_and_the_histogram_all_five(self):
        seen = []
        real = onc.omnifold_loop

        def spy(MCgen, MCreco, measured, *a, **k):
            seen.append((MCgen.shape[1], MCreco.shape[1], measured.shape[1], np.array(MCgen[:3]), np.array(MCreco[:3])))
            return real(MCgen, MCreco, measured, *a, **k)
        onc.omnifold_loop = spy
        for mask, (ng, nr) in {"O4r": (5, 4), "O4": (4, 4), "O3": (3, 3), "O2": (2, 2)}.items():
            xs, rec = self.unfold(mask)
            g, r, m, gen3, reco3 = seen[-1]
            self.assertEqual((g, r, m), (ng, nr, nr), mask)
            gi, ri = P.column_indices(P.MASKS[mask][0]), P.column_indices(P.MASKS[mask][1])
            self.assertTrue(np.array_equal(gen3, self.inp["MCgen"][:3][:, gi]))
            self.assertTrue(np.array_equal(reco3, self.inp["MCreco"][:3][:, ri]))
            self.assertEqual(xs.shape, tuple(len(e) - 1 for e in self.inp["edges"]))
            self.assertEqual(rec["calls"], 1)

    def test_a_dropped_column_changes_the_result(self):
        a, _ = self.unfold(None)
        b, _ = self.unfold("O2")
        self.assertFalse(np.array_equal(a, b))

    def test_the_loop_is_restored_and_a_wrong_shape_refused(self):
        before = onc.omnifold_loop
        with self.assertRaises(KeyError):
            with P.column_mask("O2", {}):
                raise KeyError("x")
        self.assertIs(onc.omnifold_loop, before)
        with P.column_mask("O2", {}):
            with self.assertRaises(P.Refused):
                onc.omnifold_loop(np.zeros((3, 4)), np.zeros((3, 5)), np.zeros((3, 5)))


class Install(unittest.TestCase):
    def setUp(self):
        self.saved = s5n_pseudo.write_product
        self.written = []
        s5n_pseudo.write_product = lambda out, arrays, meta: self.written.append(meta) or 0

    def tearDown(self):
        s5n_pseudo.write_product = self.saved

    def test_every_product_carries_its_level(self):
        with P.install("C400", "q3", guard=False):
            s5n_pseudo.write_product(Path("x.npz"), {}, {"iters": 5, "capacity": (400, 31),
                                                         "development": {"mc_fraction": "half"}})
        pr = self.written[-1]["prior_retention"]
        self.assertEqual((pr["level"], pr["truth"], pr["factor"]), ("C400", "q3", "F2"))
        self.assertEqual(pr["declared"]["capacity"], [400, 31])
        self.assertEqual(pr["recorded"]["capacity"], [400, 31])
        self.assertEqual(pr["code_sha256"], P.sha256_path(Path(P.__file__).resolve()))

    def test_no_product_without_the_check_or_with_a_missed_mask(self):
        with P.install("B0", "q3", guard=True):
            with self.assertRaises(RuntimeError):
                s5n_pseudo.write_product(Path("x.npz"), {}, {})
        with P.install("O2", "q3", guard=False):
            with self.assertRaises(RuntimeError):
                s5n_pseudo.write_product(Path("x.npz"), {}, {})
        self.assertEqual(self.written, [])

    def test_names_are_restored_after_an_error(self):
        before = (s5n_pseudo.write_product, onc.omnifold_loop)
        with self.assertRaises(KeyError):
            with P.install("O3", "W1"):
                raise KeyError("x")
        self.assertEqual(before, (s5n_pseudo.write_product, onc.omnifold_loop))


# ============================================================================================ staging and C-PAIR
class Stage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.r = Path(self.tmp.name)
        (self.r / "a.bin").write_bytes(b"alpha")
        self.man = [{"role": "a", "src": str(self.r / "a.bin"), "sha256": P.sha256_path(self.r / "a.bin"), "name": "x/a.bin"}]

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_staged_copy_carries_its_pin_and_stat_records(self):
        rec = P.stage(self.man, self.r / "s")
        self.assertEqual((self.r / "s" / "x" / "a.bin").read_bytes(), b"alpha")
        f = rec["files"][0]
        self.assertEqual(f["stat_before"], f["stat_after"])
        self.assertEqual(rec["dest"], str(self.r / "s"))
        P.verify_stage(rec)
        (self.r / "s" / "x" / "a.bin").write_bytes(b"beta")
        with self.assertRaises(P.Refused):
            P.verify_stage(rec)

    def test_a_wrong_pin_or_a_used_destination_is_refused(self):
        with self.assertRaises(P.Refused):
            P.stage([{**self.man[0], "sha256": "0" * 64}], self.r / "s1")
        (self.r / "s2").mkdir()
        with self.assertRaises(P.Refused):
            P.stage(self.man, self.r / "s2")

    def test_a_moved_atime_is_refused(self):
        real = P.stat_record
        calls = []

        def moved(path):
            rec = real(path)
            calls.append(1)
            return {**rec, "atime_ns": rec["atime_ns"] + (len(calls) % 2 == 0)}
        P.stat_record = moved
        try:
            with self.assertRaises(P.Refused):
                P.stage(self.man, self.r / "s3")
        finally:
            P.stat_record = real

    def test_the_manifest_names_every_shared_read(self):
        roles = {e["role"] for e in P.SOURCES}
        self.assertEqual(roles, {"of_inputs_5d", "bkg_dump", "bank_cv", "closure_ratio_nuwro",
                                 "fd_stab_control_nominal", "fd_stab_control_A7_gibuu"})
        a = P.staged_paths(Path("/S"), Path("/R"))
        self.assertEqual(a.closure_ratio_dir / "prep/ratios/L-5D-PV/nuwro.json",
                         Path("/S") / next(e["name"] for e in P.SOURCES if e["role"] == "closure_ratio_nuwro"))
        self.assertEqual(a.npz.name, "of_inputs_5d.npz")


class Pair(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        r = Path(self.tmp.name)
        self.runs = r / "runs"
        x = np.linspace(1, 2, 50).astype(np.float64)
        self.files = []
        pins = {}
        for t in ("nominal", "A7_gibuu"):
            p = P.product_path(self.runs, "B0", t, P.PRIMARY_SEED)
            p.parent.mkdir(parents=True)
            np.savez(p, xsec_flat=x * (2 if t == "A7_gibuu" else 1))
            ref = r / f"ref_{t}.npz"
            shutil.copy(p, ref)
            pins[t] = P.sha256_path(ref)
            self.files.append({"role": f"fd_stab_control_{t}", "copy": str(ref), "sha256": pins[t]})
        p = P.product_path(self.runs, "O5", "nominal", P.PRIMARY_SEED)
        p.parent.mkdir(parents=True)
        np.savez(p, xsec_flat=x)
        self.saved, P.FD_STAB_CONTROL = P.FD_STAB_CONTROL, pins

    def tearDown(self):
        P.FD_STAB_CONTROL = self.saved
        self.tmp.cleanup()

    def test_bitwise_pairs_pass(self):
        self.assertTrue(P.pair({"files": self.files}, self.runs)["pass"])

    def test_one_ulp_fails_c_pair(self):
        p = P.product_path(self.runs, "B0", "A7_gibuu", P.PRIMARY_SEED)
        x = np.load(p)["xsec_flat"]
        x[7] = np.nextafter(x[7], 10)
        np.savez(p, xsec_flat=x)
        res = P.pair({"files": self.files}, self.runs)
        self.assertFalse(res["pass"])
        self.assertEqual(res["C-PAIR"]["A7_gibuu"]["cells_differing"], 1)

    def test_a_mask_that_moves_b0_fails_c_mask(self):
        p = P.product_path(self.runs, "O5", "nominal", P.PRIMARY_SEED)
        np.savez(p, xsec_flat=np.load(p)["xsec_flat"].astype(np.float32))
        self.assertFalse(P.pair({"files": self.files}, self.runs)["C-MASK"]["nominal"]["pass"])

    def test_an_unpinned_reference_fails(self):
        Path(self.files[0]["copy"]).write_bytes(b"x")
        self.assertFalse(P.pair({"files": self.files}, self.runs)["pass"])


# ============================================================================================ route 2
class Route2Capture(unittest.TestCase):
    """B0's line through the real runner, stopped where build returns: the experiment is the runner's own."""

    def setUp(self):
        import s5p_universe
        self.tmp = tempfile.TemporaryDirectory()
        self.a, self.inp = synthetic_stage(Path(self.tmp.name))
        self.scratch = Path(self.tmp.name) / "scratch"
        self.align, s5p_universe.check_alignment = s5p_universe.check_alignment, lambda *a, **k: {}
        self.cwd = os.getcwd()
        os.chdir(REPO)

    def tearDown(self):
        import s5p_universe
        s5p_universe.check_alignment = self.align
        os.chdir(self.cwd)
        self.tmp.cleanup()

    def line(self, truth, seed=P.PRIMARY_SEED, level="B0"):
        return P.runner_argv(self.a, level, truth, seed)

    def test_the_capture_is_the_runners_experiment_and_writes_nothing(self):
        import s5c_pseudo
        import s5p_nullexp
        cache = {}
        with quiet():
            seen = R.capture("W1", self.line("W1"), cache, self.scratch)
        self.assertEqual(seen["split"], s5c_pseudo.split_key_for(P.PRIMARY_SEED))
        self.assertTrue(seen["expectation"])
        self.assertEqual(seen["exp"]["MCgen"].shape[0], int((~s5c_pseudo.half_mask(6000, seen["split"])).sum()))
        self.assertEqual(seen["r"].shape, (6000,))
        self.assertFalse((self.a.runs).exists())
        self.assertEqual(list(self.scratch.iterdir()), [])
        (self.scratch / "x").write_text("x")
        with quiet(), self.assertRaises(P.Refused):
            R.capture("W1", self.line("W1"), cache, self.scratch)
        (self.scratch / "x").unlink()
        before = (s5p_nullexp.build, s5n_pseudo.true_xsec, s5n_pseudo.truth_weight)
        with quiet():
            again = R.capture("W1", self.line("W1"), cache, self.scratch)
        self.assertTrue(np.array_equal(again["x_true"], seen["x_true"]))
        self.assertEqual(before, (s5p_nullexp.build, s5n_pseudo.true_xsec, s5n_pseudo.truth_weight))

    def test_a_truths_reweight_reaches_the_capture(self):
        with quiet():
            nom = R.capture("nominal", self.line("nominal"), {}, self.scratch)
            nuw = R.capture("closure_nuwro", self.line("closure_nuwro"), {}, self.scratch)
        self.assertTrue(np.all(nom["r"] == 1.0))
        self.assertFalse(np.allclose(nuw["r"], 1.0))
        self.assertFalse(np.allclose(nuw["x_true"], nom["x_true"], rtol=1e-6, atol=0))

    def test_a_line_that_is_not_b0s_is_refused(self):
        with quiet(), self.assertRaises(SystemExit):
            R.capture("nominal", self.line("nominal", level="K10"), {}, self.scratch)

    def test_the_queues_carry_every_route2_line(self):
        out = Path(self.tmp.name) / "q"
        with contextlib.redirect_stdout(io.StringIO()):
            P.main(["tasks", "--out", str(out), "--stage-dir", str(self.a.npz.parent), "--runs", str(self.a.runs)])
        lines = R.b0_lines(out)
        self.assertEqual(sorted(lines), sorted(R.experiments()))
        a = P.staged_paths(self.a.npz.parent, self.a.runs)
        self.assertEqual(lines[("A7_gibuu", 994003)], P.runner_argv(a, "B0", "A7_gibuu", 994003))
        self.assertEqual(len(R.experiments()), 12 + 2 * len(P.FLOOR_SEEDS))


class Route2Unfold(unittest.TestCase):
    """The captured experiment through REF-G1's own Lib, worlds and unfold_experiment, on synthetic rows on the real
    5D grid with the real H2 cells and S1 rows."""

    @classmethod
    def setUpClass(cls):
        import ibu1
        import ref_g1
        import s5c_pseudo
        import s5p_universe
        cls.tmp = tempfile.TemporaryDirectory()
        d = Path(cls.tmp.name)
        cls.a, _ = synthetic_stage(d)
        z = dict(np.load(cls.a.npz, allow_pickle=True))
        z["pass_truth"] = np.ones_like(z["pass_truth"])  # IBU-1's World refuses a reco row outside every truth cell
        z["MCgen"][40:60], z["MCreco"][40:60] = z["MCgen"][100:120], z["MCreco"][100:120]
        np.savez(cls.a.npz, **z)
        cls.a.expect_npz_sha256 = P.sha256_path(cls.a.npz)
        cls.align, s5p_universe.check_alignment = s5p_universe.check_alignment, lambda *x, **k: {}
        cls.cwd = os.getcwd()
        os.chdir(REPO)
        cfg = json.loads(ref_g1.CONFIG.read_text())
        cls.lib = ref_g1.Lib(cfg)
        contract = json.loads((REPO / cls.lib.ibu1_cfg["contract"]["path"]).read_text())
        cls.inputs = cls.lib.prod.s5c_pseudo.s5c_unfold.load_inputs(cls.a.npz)
        _, cls.gw = ref_g1.worlds(cls.lib, cfg, cls.inputs, contract)
        with quiet():
            cls.seen = R.capture("W1", P.runner_argv(cls.a, "B0", "W1", P.PRIMARY_SEED),
                                 {str(cls.a.npz.resolve()): cls.inputs}, d / "scratch")
        is_b = s5c_pseudo.half_mask(cls.inputs["MCgen"].shape[0], cls.seen["split"])
        cls.half = ibu1.half_from_experiment(cls.gw, cls.seen["exp"], is_b)
        cls.sink = []
        with R.capture_ibu(cls.lib.prod.did, cls.sink):
            cls.res = R.route2(cls.gw, cls.half, cls.seen["exp"], cls.seen["x_true"])

    @classmethod
    def tearDownClass(cls):
        import s5p_universe
        s5p_universe.check_alignment = cls.align
        os.chdir(cls.cwd)
        cls.tmp.cleanup()

    def test_every_k_on_the_sixteen_cells(self):
        self.assertEqual(self.res["arrays"]["F_fold"].shape, (len(R.KS), 16))
        self.assertEqual(self.res["arrays"]["ks"].tolist(), list(R.KS))
        self.assertTrue(np.all(np.isfinite(self.res["arrays"]["F_fold"])))

    def test_k5_is_ref_g1s_unfold_bitwise(self):
        import ref_g1
        arrays, _ = ref_g1.unfold_experiment(self.gw, self.half, self.seen["exp"], [5])
        self.assertTrue(np.array_equal(arrays["F_fold"][0], self.res["arrays"]["F_fold"][R.KS.index(5)]))

    def test_the_response_is_half_a(self):
        import s5c_pseudo
        is_b = s5c_pseudo.half_mask(self.inputs["MCgen"].shape[0], self.seen["split"])
        self.assertTrue(np.array_equal(self.half.rows, np.flatnonzero(~is_b)))
        self.assertTrue(np.array_equal(self.half.w_truth, 2.0 * self.inputs["w_truth"][~is_b]))

    def test_the_truth_is_es_cell_truth(self):
        import estimator_stability_analyze as an
        M16 = an.cell_matrix(str(REPO / "nd-unfolding/pv-ladder/readouts/h2_definition.json"))
        x = M16 @ np.asarray(self.seen["x_true"], float).ravel(order="C")
        ok = x != 0
        self.assertLess(float(np.max(np.abs(self.res["arrays"]["X_true"][ok] / x[ok] - 1))), 1e-12)

    def test_r_id_reads_the_fold_problem(self):
        rid = R.r_id(self.lib.prod.did, self.gw.U, self.sink)
        self.assertEqual(len(rid["sigma_rel"]), 16)
        ibu_calls = [x for x in self.sink if "R" in x]
        self.assertEqual(len(ibu_calls), 2)  # fold, then sub
        self.assertGreater(float(ibu_calls[0]["b"].sum()), float(ibu_calls[1]["b"].sum()))  # fold carries the template
        self.assertIn("read by nothing", rid["label"])
        self.assertEqual(rid, R.r_id(self.lib.prod.did, self.gw.U, self.sink[:2]))  # the fold unfold's, not sub's

    def test_c_ibu_passes_on_the_committed_value_and_fails_off_it(self):
        ratio = self.a.closure_ratio_dir / "prep/ratios/L-5D-PV/nuwro.json"
        with tempfile.TemporaryDirectory() as d:
            ro = Path(d) / "ro.json"

            def run(value):
                ro.write_text(json.dumps({"R2": {"nuwro": {"median_abs_residual_ibu": value}}}))
                cib = {**R.CIBU, "readout": "ro.json", "readout_sha256": P.sha256_path(ro)}
                return R.c_ibu(self.lib, self.gw, self.inputs, ratio, P.sha256_path(ratio), repo=Path(d), cibu=cib)
            got = run(1.0)["got"]
            self.assertTrue(run(got)["pass"])
            self.assertFalse(run(got * (1 + 1e-9))["pass"])
            with self.assertRaises(P.Refused):
                R.c_ibu(self.lib, self.gw, self.inputs, ratio, "0" * 64, repo=Path(d),
                        cibu={**R.CIBU, "readout": "ro.json", "readout_sha256": P.sha256_path(ro)})


class Route2Run(unittest.TestCase):
    def test_unpinned_inputs_are_refused_before_any_unfold(self):
        with tempfile.TemporaryDirectory() as d:
            a, _ = synthetic_stage(Path(d))
            with contextlib.redirect_stdout(io.StringIO()):
                P.main(["tasks", "--out", str(Path(d) / "queues"), "--stage-dir", str(a.npz.parent), "--runs", str(a.runs)])
            files = [{"role": e["role"], "copy": str(a.npz.parent / e["name"]), "sha256": P.sha256_path(a.npz.parent / e["name"])}
                     for e in P.SOURCES if (a.npz.parent / e["name"]).exists()]
            (Path(d) / "stage.json").write_text(json.dumps({"dest": str(a.npz.parent), "files": files}))
            cwd = os.getcwd()
            os.chdir(REPO)
            try:
                with quiet() as err:
                    rc = R.main(["run", "--queue-dir", str(Path(d) / "queues"), "--stage", str(Path(d) / "stage.json"),
                                 "--out", str(Path(d) / "route2")])
            finally:
                os.chdir(cwd)
            self.assertEqual(rc, 2)
            self.assertIn("digest", err.getvalue())
            self.assertFalse((Path(d) / "route2" / "route2.npz").exists())


class Route2Helpers(unittest.TestCase):
    def test_fine_to_cell_refuses_an_overlap(self):
        U = np.array([[1.0, 0, 2.0, 0], [0, 3.0, 0, 0]])
        self.assertEqual(R.fine_to_cell(U).tolist(), [0, 1, 0, -1])
        with self.assertRaises(P.Refused):
            R.fine_to_cell(np.array([[1.0, 1.0], [1.0, 0.0]]))

    def test_r_sup(self):
        world = types.SimpleNamespace(tflat=np.array([0, 1, 2, 3, -1, 0]))
        half = types.SimpleNamespace(rows=np.array([0, 1, 2, 5]), w_truth=np.array([2.0, 2.0, 2.0, 6.0]))
        r = np.array([1.0, 0.5, 1.0, 1.0, 1.0, 1.0])
        cell = np.array([0, 1, 0, 2])
        out = R.r_sup(world, half, r, cell)
        self.assertEqual(out["sum_w"][:3], [10.0, 1.0, 0.0])
        self.assertAlmostEqual(out["kish"][0], 100.0 / (4 + 4 + 36))
        self.assertAlmostEqual(out["max_share"][0], 0.6)
        self.assertEqual(out["rows"][:3], [3, 1, 0])

    def test_c_ibu_compares_to_the_committed_value(self):
        self.assertEqual(R.CIBU["readout_sha256"], P.sha256_path(REPO / R.CIBU["readout"]))
        v = json.loads((REPO / R.CIBU["readout"]).read_text())
        for k in R.CIBU["key"]:
            v = v[k]
        self.assertAlmostEqual(v, 0.03322119601639817, places=17)


# ============================================================================================ the readings
class Rho(unittest.TestCase):
    def setUp(self):
        self.p = np.full(16, 10.0)
        self.x = self.p * (1 + np.linspace(-0.2, 0.2, 16))

    def test_the_prior_retains_one_and_the_truth_zero(self):
        self.assertAlmostEqual(RD.rho(self.p, self.x, self.p)[0], 1.0)
        self.assertAlmostEqual(RD.rho(self.x, self.x, self.p)[0], 0.0)
        self.assertAlmostEqual(RD.rho(self.x - 0.3 * (self.x - self.p), self.x, self.p)[0], 0.3)

    def test_bias_orthogonal_to_the_departure_does_not_enter(self):
        d = (self.x - self.p) / self.p
        o = np.ones(16)
        o -= (o @ d) / (d @ d) * d
        self.assertAlmostEqual(RD.rho(self.x + 0.5 * o * self.p, self.x, self.p)[0], 0.0)

    def test_undefined_below_two_cells(self):
        x = self.p.copy()
        x[3] *= 1.5
        self.assertEqual(RD.rho(x, x, self.p), (None, 1))
        x[4] *= 1.005  # below the 0.01 threshold
        self.assertEqual(RD.rho(x, x, self.p)[1], 1)

    def test_t_quantile(self):
        from scipy import stats
        self.assertAlmostEqual(RD.T_Q, float(stats.t.ppf(1 - 0.01 / 12 / 2, 4)), places=12)


class Classes(unittest.TestCase):
    def test_factor_class_both_directions(self):
        self.assertEqual(RD.factor_class(0.5, [0.4, 0.49], 0.05), "reduces")
        self.assertEqual(RD.factor_class(0.5, [0.56, 0.5], 0.05), "increases")
        self.assertEqual(RD.factor_class(0.5, [0.4, 0.6], 0.05), "both")
        self.assertEqual(RD.factor_class(0.5, [0.46, 0.54], 0.05), "no effect")
        self.assertEqual(RD.factor_class(None, [0.4], 0.05), "undefined")
        self.assertEqual(RD.factor_class(0.5, [0.45], 0.05), "reduces")  # at the bar

    def test_bar(self):
        self.assertEqual(RD.bar(0.001), 0.05)
        self.assertAlmostEqual(RD.bar(0.01), RD.T_Q * 0.01)

    def test_ibu_classes(self):
        self.assertEqual(RD.ibu_class(-0.2, 0.05), "IBU retains less")
        self.assertEqual(RD.ibu_class(0.2, 0.05), "IBU retains more")
        self.assertEqual(RD.ibu_class(0.01, 0.05), "same")
        self.assertEqual(RD.ibu_k_class(0.5, 0.4), "falls")
        self.assertEqual(RD.ibu_k_class(0.5, 0.6), "rises")
        self.assertEqual(RD.ibu_k_class(0.5, 0.47), "flat")

    def test_labels(self):
        base = {"F1": "no effect", "F2": "no effect", "F3": "no effect", "F4": "no effect"}
        self.assertEqual(RD.labels_for({**base, "F1": "reduces"}, "same", "falls"),
                         ["consistent with finite-iteration regularization"])
        self.assertEqual(RD.labels_for(base, "same", "flat"), ["consistent with an information limit at these settings"])
        self.assertNotIn("consistent with an information limit at these settings",
                         RD.labels_for({**base, "F2": "reduces"}, "same", "flat"))
        self.assertNotIn("consistent with an information limit at these settings",
                         RD.labels_for({**base, "F1": "both"}, "same", "flat"))
        self.assertIn("consistent with an implementation-specific share", RD.labels_for(base, "IBU retains less", "falls"))
        self.assertIn("consistent with an implementation-specific share", RD.labels_for({**base, "F2": "reduces"}, "same", "falls"))
        self.assertIn("sensitive to the observable set", RD.labels_for({**base, "F4": "both"}, "same", "flat"))
        self.assertIn("sensitive to training statistics", RD.labels_for({**base, "F3": "increases"}, "same", "flat"))
        self.assertEqual(RD.labels_for({**base, "F1": "reduces"}, "same", "flat"), ["unattributed"])

    def test_clears(self):
        b0 = {t: t in P.FLAGGED for t in P.TRUTHS}
        lv = {t: False for t in P.TRUTHS}
        self.assertEqual(RD.clears(lv, b0), {"reading": "clears at these truths", "without_new_flags": True, "new_flags": []})
        lv["W3"] = True
        self.assertFalse(RD.clears(lv, b0)["without_new_flags"])
        lv["q3"] = True
        self.assertEqual(RD.clears(lv, b0)["reading"], "does not clear at these truths")

    def test_floor_needs_five_defined_splits(self):
        self.assertAlmostEqual(RD.floor_sd([0, 0.01, -0.01, 0.02, 0.0]), float(np.std([0, 0.01, -0.01, 0.02, 0.0], ddof=1)))
        with self.assertRaises(RD.Stop):
            RD.floor_sd([0, 0.01, 0.0, 0.0])
        with self.assertRaises(RD.Stop):
            RD.floor_sd([0, 0.01, None, 0.0, 0.0])

    def test_spearman(self):
        self.assertAlmostEqual(RD.spearman([1, 2, 3], [10, 20, 30]), 1.0)
        self.assertAlmostEqual(RD.spearman([1, 2, 3], [3, 2, 1]), -1.0)
        self.assertIsNone(RD.spearman([1, 1, 1], [1, 2, 3]))


class GradeMatrices(unittest.TestCase):
    def test_c_ct_reproduces_f0b(self):
        mats, f, ct = RD.grade_matrices(REPO)
        self.assertTrue(ct["pass"])
        self.assertEqual(set(mats), set(P.TRUTHS))
        self.assertLess(ct["closure_nuwro_chi2_rel"], 1e-12)

    def test_a_moved_vertex_fails_c_ct(self):
        with tempfile.TemporaryDirectory() as d:
            for rel in RD.INPUT_PINS:
                (Path(d) / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(REPO / rel, Path(d) / rel)
            p = Path(d) / "nd-unfolding/pv-ladder/readouts/cmodel_5d.json"
            cj = json.loads(p.read_text())
            cj["S"][2][6] *= 1.001
            p.write_text(json.dumps(cj))
            with self.assertRaises(RD.Stop):
                RD.grade_matrices(Path(d))

    def test_table_ii_flags_by_p_and_by_z(self):
        C = np.eye(16) * 0.01 ** 2
        self.assertFalse(RD.table_ii(np.full(16, 0.001), C)["flagged"])
        one = np.zeros(16)
        one[3] = 0.025  # z = 2.5 in one cell, chi2 6.25: flagged by z alone
        g = RD.table_ii(one, C)
        self.assertTrue(g["flagged"] and g["p"] > 0.01)
        g = RD.table_ii(np.full(16, 0.018), C)  # every z 1.8, chi2 51.8: flagged by p alone
        self.assertTrue(g["flagged"] and not g["cells_abs_z_gt_2"])

    def test_the_own_vertex_is_f0s(self):
        mats, _, _ = RD.grade_matrices(REPO)
        dp = json.loads((REPO / RD.FD / "with-cpl/data-product/fd_data_product_cpl.json").read_text())
        self.assertFalse(np.allclose(mats["A7_gibuu"], mats["nominal"]))
        self.assertTrue(np.array_equal(mats["nominal"], mats["A7_genie_cv"]))
        self.assertTrue(np.array_equal(mats["W1"], mats["W3"]))
        self.assertEqual(len(dp["f"]), 16)


# ============================================================================================ end to end (the reader)
class EndToEnd(unittest.TestCase):
    """read() on a synthetic run over a 40-cell grid: planted retentions give the declared classes, every product check
    and every completeness rule refuses, and the readout carries no absolute value."""

    G = 40

    def setUp(self):
        import estimator_stability_analyze as an
        self.an = an
        self.saved = an.cell_matrix
        self.M = np.vstack([np.where(np.arange(self.G) % 16 == c, 1.0, 0.0) for c in range(16)])
        an.cell_matrix = lambda h2: self.M
        self.tmp = tempfile.TemporaryDirectory()
        self.run = Path(self.tmp.name) / "out"
        self.rho = {}  # (level, truth, seed) -> planted rho
        self.ibu_rho = {}

    def tearDown(self):
        self.an.cell_matrix = self.saved
        self.tmp.cleanup()

    def truth_x(self, t, s):
        rng = np.random.default_rng(abs(hash((t, s))) % 2**32)
        base = 3e-39 * (1.0 + np.arange(self.G) / self.G)  # a cross section's scale, as the real cells
        if t in (P.PRIOR, "A7_mnvtune"):
            return base * (1 + 0.02 * (s % 5))  # the prior moves with the split, so P must be read at its own
        return base * (1 + rng.uniform(-0.3, 0.3, self.G))

    def meta(self, lv, t, s, **tamper):
        L = P.LEVELS[lv]
        want = RD.expected_truth(t, REPO)
        cap = None if L["capacity"] is None else list(L["capacity"])
        m = {"iters": L["iters"], "capacity": cap, "development": {"expectation": True, "mc_fraction": L["mc_fraction"]},
             "nuisance_draw": None, "pseudo_seed": s, "split_key": __import__("s5c_pseudo").split_key_for(s),
             "hypothesis": {"sha256": want["hyp"]}, "alternative": want["alt"],
             "code_sha256": {"s5p_nullexp.py": P.CODE_PINS["nd-unfolding/s5p_nullexp.py"],
                             "unfold_2d_omnifold_unbinned.py": P.CODE_PINS["2d-unfolding/unfold_2d_omnifold_unbinned.py"],
                             "s5n_pseudo.py": P.CODE_PINS["nd-unfolding/s5n_pseudo.py"]},
             "prior_retention": {"schema": P.SCHEMA, "level": lv, "truth": t, "factor": L["factor"],
                                 "declared": {"iters": L["iters"], "capacity": cap, "mc_fraction": L["mc_fraction"],
                                              "mask": L["mask"]},
                                 "recorded": {"iters": L["iters"], "capacity": cap, "mc_fraction": L["mc_fraction"]},
                                 "mask": {"calls": 0 if L["mask"] is None else 1,
                                          "gen_columns": None if L["mask"] is None else list(P.MASKS[L["mask"]][0]),
                                          "reco_columns": None if L["mask"] is None else list(P.MASKS[L["mask"]][1])},
                                 "input_columns": list(P.AXES), "code_sha256": "x"}}
        for k, v in tamper.items():
            m[k] = v
        return m

    def build(self, plant=None, ibu_plant=None, tamper=None):
        plant, ibu_plant = plant or {}, ibu_plant or {}
        for lv, t, s in P.all_tasks():
            xt = self.truth_x(t, s)
            p = self.truth_x(P.PRIOR, s)
            rho = plant.get((lv, t, s), plant.get((lv, t), 0.3))
            xh = xt - rho * (xt - p)  # retains exactly rho of the departure
            m = self.meta(lv, t, s)
            if tamper and tamper[0] == (lv, t, s):
                tamper[1](m)
            path = P.product_path(self.run / "runs", lv, t, s)
            path.parent.mkdir(parents=True, exist_ok=True)
            np.savez(path, xsec_flat=xh, xtrue_flat=xt, meta=json.dumps(m))
        arrays, exps = {}, {}
        for t, s in R.experiments():
            xt, p = self.M @ self.truth_x(t, s), self.M @ self.truth_x(P.PRIOR, s)
            F = []
            for k in R.KS:
                rho = ibu_plant.get((k, t, s), ibu_plant.get((k, t), 0.3))
                F.append(xt - rho * (xt - p))
            arrays[f"{t}_s{s}__F_fold"], arrays[f"{t}_s{s}__X_true"] = np.array(F), xt
            exps[f"{t}_s{s}"] = {"truth": t, "seed": s}
        (self.run / "route2").mkdir(parents=True)
        np.savez(self.run / "route2" / "route2.npz", **arrays)
        (self.run / "route2" / "route2.json").write_text(json.dumps(
            {"ks": list(R.KS), "C-IBU": {"pass": True}, "experiments": exps, "R-ID": {"sigma_rel": [0.1] * 16},
             "R-SUP": {t: {"kish": list(range(16, 0, -1))} for t in P.TRUTHS}}))
        q = self.run / "queues"
        q.mkdir()
        a = P.staged_paths(Path("/S"), self.run / "runs")
        for j in P.JOBS:
            (q / f"{j}.tsv").write_text("\n".join(P.queue_lines(a, j)) + "\n")
            (self.run / f"log-{j}").mkdir()
            n = len(P.queue_lines(a, j)) - 1
            (self.run / f"log-{j}" / "DONE").write_text(json.dumps({"mode": j, "tasks": n, "ended": n, "rc": 0}))
        (self.run / "log-ibu").mkdir()
        (self.run / "log-ibu" / "DONE").write_text(json.dumps({"mode": "ibu", "rc": 0}))
        (self.run / "log-dry" / "pair.json").write_text(json.dumps(
            {"pass": True, "C-PAIR": {t: {"pass": True} for t in P.FD_STAB_CONTROL}, "C-MASK": {"nominal": {"pass": True}}}))

    def read(self):
        return RD.read(self.run, REPO)

    def floor_plant(self, delta_sd=0.004):
        """A small spread of each floor level's rho around B0's across the five splits."""
        out = {}
        for i, s in enumerate((P.PRIMARY_SEED, *P.FLOOR_SEEDS)):
            for lv in P.FLOOR_LEVELS:
                out[(lv, P.FLOOR_TRUTH, s)] = 0.3 + (0 if lv == "B0" else delta_sd * (i - 2))
        return out

    def test_planted_classes(self):
        plant = self.floor_plant()
        plant.update({("K50", "A7_gibuu"): 0.1, ("C1000", "A7_gibuu"): 0.40, ("O2", "q3"): 0.5, ("O3", "q3"): 0.1})
        ibu = {(5, "A7_gibuu"): 0.15, (200, "A7_gibuu"): 0.05, (5, "q3"): 0.3, (200, "q3"): 0.31}
        self.build(plant, ibu)
        out, rc = self.read()
        self.assertEqual(rc, 0)
        rd = out["readings"]
        self.assertEqual(rd["PR-1"]["A7_gibuu"]["F1"], "reduces")
        self.assertEqual(rd["PR-1"]["A7_gibuu"]["F2"], "increases")
        self.assertEqual(rd["PR-1"]["A7_gibuu"]["F3"], "no effect")
        self.assertEqual(rd["PR-1"]["q3"]["F4"], "both")
        self.assertEqual(rd["PR-2a"]["A7_gibuu"], "IBU retains less")
        self.assertEqual(rd["PR-2b"]["A7_gibuu"], "falls")
        self.assertEqual(rd["PR-2a"]["q3"], "same")
        self.assertEqual(rd["PR-2b"]["q3"], "flat")
        self.assertIn("consistent with finite-iteration regularization", rd["labels"]["A7_gibuu"])
        self.assertIn("sensitive to the observable set", rd["labels"]["q3"])
        sd = float(np.std(0.004 * (np.arange(5) - 2), ddof=1))
        self.assertAlmostEqual(rd["floor"]["s_F"]["F1"], sd, places=12)
        self.assertAlmostEqual(rd["floor"]["bars"]["F1"], max(0.05, RD.T_Q * sd), places=12)
        self.assertEqual(rd["floor"]["bars"]["IBU"], 0.05)  # IBU's planted difference does not vary: the floor binds
        self.assertAlmostEqual(out["table"][f"B0/A7_gibuu/s{P.PRIMARY_SEED}"]["rho"], 0.3)
        self.assertIsNone(out["table"][f"B0/nominal/s{P.PRIMARY_SEED}"]["rho"])
        self.assertAlmostEqual(out["table"]["B0/A7_gibuu/s994002"]["rho"], 0.3)
        self.assertAlmostEqual(out["ibu"]["K5/A7_gibuu/s994003"]["rho"], 0.15)
        self.assertEqual(rd["PR-3_label"], RD.LABELS["pr3"])

    def test_a_large_floor_raises_the_bar_and_silences_a_change(self):
        plant = self.floor_plant(delta_sd=0.05)
        plant[("K50", "A7_gibuu")] = 0.1
        self.build(plant)
        rd = self.read()[0]["readings"]
        self.assertGreater(rd["floor"]["bars"]["F1"], 0.2)
        self.assertEqual(rd["PR-1"]["A7_gibuu"]["F1"], "no effect")

    def test_incomplete_runs_read_nothing(self):
        self.build(self.floor_plant())
        (self.run / "log-cap" / "STOP").write_text("x")
        out, rc = self.read()
        self.assertEqual((out["verdict"], rc), ("INCOMPLETE", RD.INCOMPLETE_RC))
        (self.run / "log-cap" / "STOP").unlink()
        d = json.loads((self.run / "log-misc" / "DONE").read_text())
        (self.run / "log-misc" / "DONE").write_text(json.dumps({**d, "ended": d["ended"] - 1}))
        self.assertEqual(self.read()[0]["verdict"], "INCOMPLETE")
        (self.run / "log-misc" / "DONE").write_text(json.dumps(d))
        (self.run / "log-ibu" / "DONE").unlink()
        self.assertEqual(self.read()[0]["verdict"], "INCOMPLETE")

    def tampered(self, key, fn):
        self.build(self.floor_plant(), tamper=(key, fn))
        with self.assertRaises(RD.Stop):
            self.read()

    def test_the_product_checks_refuse(self):
        k = ("C400", "W2", P.PRIMARY_SEED)
        self.tampered(k, lambda m: m.update(capacity=[100, 8]))

    def test_c_cap_on_the_recorded_iters(self):
        self.tampered(("K10", "W1", P.PRIMARY_SEED), lambda m: m.update(iters=5))

    def test_a_missed_mask_refuses(self):
        self.tampered(("O4", "q3", P.PRIMARY_SEED), lambda m: m["prior_retention"]["mask"].update(calls=0))

    def test_a_split_off_its_seed_refuses(self):
        self.tampered(("MCq", "W3", P.PRIMARY_SEED), lambda m: m.update(split_key=12345))

    def test_a_wrong_truth_file_refuses(self):
        self.tampered(("B0", "W1", P.PRIMARY_SEED), lambda m: m.update(hypothesis={"sha256": "0" * 64}))
        self.tmp.cleanup()
        self.tmp = tempfile.TemporaryDirectory()
        self.run = Path(self.tmp.name) / "out"
        self.tampered(("B0", "q3", P.PRIMARY_SEED), lambda m: m["alternative"].update(amplitude=0.4))

    def test_columns_and_runner_digest_refuse(self):
        self.tampered(("O2", "W1", P.PRIMARY_SEED), lambda m: m["prior_retention"].update(input_columns=list(P.AXES[::-1])))

    def test_a_product_made_by_other_code_refuses(self):
        self.tampered(("C25", "q3", P.PRIMARY_SEED), lambda m: m["code_sha256"].update({"s5n_pseudo.py": "0" * 64}))

    def test_a_noisy_product_refuses(self):
        self.tampered(("K2", "W1", P.PRIMARY_SEED), lambda m: m.update(nuisance_draw={"flux": 3}))

    def test_c_pair_and_c_ibu_records_gate(self):
        self.build(self.floor_plant())
        (self.run / "log-dry" / "pair.json").write_text(json.dumps({"pass": False}))
        with self.assertRaises(RD.Stop):
            self.read()
        self.tmp.cleanup()
        self.tmp = tempfile.TemporaryDirectory()
        self.run = Path(self.tmp.name) / "out"
        self.build(self.floor_plant())
        rec = json.loads((self.run / "route2" / "route2.json").read_text())
        (self.run / "route2" / "route2.json").write_text(json.dumps({**rec, "C-IBU": {"pass": False}}))
        with self.assertRaises(RD.Stop):
            self.read()

    def test_c_ibu_truths_must_be_es(self):
        self.build(self.floor_plant())
        z = dict(np.load(self.run / "route2" / "route2.npz"))
        z[f"q3_s{P.PRIMARY_SEED}__X_true"] = z[f"q3_s{P.PRIMARY_SEED}__X_true"] * (1 + 1e-9)
        np.savez(self.run / "route2" / "route2.npz", **z)
        with self.assertRaises(RD.Stop):
            self.read()

    def test_c_mask_on_the_products(self):
        self.build(self.floor_plant())
        p = P.product_path(self.run / "runs", "O5", "nominal", P.PRIMARY_SEED)
        z = dict(np.load(p))
        z["xsec_flat"] = z["xsec_flat"] * (1 + 1e-15) + 1e-15
        np.savez(p, **z)
        with self.assertRaises(RD.Stop):
            self.read()

    def test_the_readout_carries_no_absolute_value(self):
        self.build(self.floor_plant())
        out, rc = self.read()
        mats, f, _ = RD.grade_matrices(REPO)
        guard = F0.LeakGuard(f, [])
        self.assertEqual(guard.count(out), 0)
        out["planted"] = float(f[3])
        self.assertGreater(guard.count(out), 0)

    def test_the_main_writes_a_stop_and_no_readout(self):
        self.build(self.floor_plant(), tamper=(("C25", "W1", P.PRIMARY_SEED), lambda m: m.update(pseudo_seed=1)))
        o = Path(self.tmp.name) / "read"
        with quiet():
            rc = RD.main(["--run", str(self.run), "--repo", str(REPO), "--out", str(o)])
        self.assertEqual(rc, RD.STOP_RC)
        self.assertTrue((o / "STOP").exists())
        self.assertFalse((o / "readout.json").exists())


# ============================================================================================ the job script
class JobScript(unittest.TestCase):
    """sbatch_prr.sh run locally on a stand-in deploy: the real gate and limit, runners that only record their argv."""

    def setUp(self):
        if not shutil.which("git") or not shutil.which("bash"):
            self.skipTest("needs git and bash")
        self.tmp = tempfile.TemporaryDirectory()
        r = Path(self.tmp.name)
        self.D, self.OUT = r / "deploy", r / "out"
        pr = self.D / "nd-unfolding" / "prior_retention"
        pr.mkdir(parents=True)
        (pr / "prr_probe.py").write_text(
            "import sys, os, json, time, pathlib, hashlib\n"
            f"sys.path.insert(0, {str(HERE)!r}); sys.path.insert(1, {str(ND)!r})\n"
            "import prr_probe as p\n"
            "cmd = sys.argv[1]\n"
            "if cmd in ('gate', 'limit'):\n"
            "    sys.exit(p.main(sys.argv[1:]))\n"
            "if cmd == 'stage':\n"
            "    o = pathlib.Path(sys.argv[sys.argv.index('--out') + 1]); d = pathlib.Path(sys.argv[sys.argv.index('--dest') + 1])\n"
            "    d.mkdir(); o.write_text(json.dumps({'dest': str(d), 'files': []}))\n"
            "    sys.exit(int(os.environ.get('PRR_STAGE_RC', '0')))\n"
            "if cmd == 'verify-stage':\n"
            "    sys.exit(int(os.environ.get('PRR_VERIFY_RC', '0')))\n"
            "if cmd == 'pair':\n"
            "    pathlib.Path(sys.argv[sys.argv.index('--out') + 1]).write_text('{}')\n"
            "    sys.exit(int(os.environ.get('PRR_PAIR_RC', '0')))\n"
            "line = ' '.join(sys.argv)\n"
            "if os.environ.get('PRR_FAIL_TASK') and os.environ['PRR_FAIL_TASK'] in line: sys.exit(1)\n"
            "time.sleep(0.05)\n"
            "out = pathlib.Path(sys.argv[sys.argv.index('--out') + 1]); out.mkdir(parents=True, exist_ok=True)\n"
            "(out / (hashlib.sha256(line.encode()).hexdigest()[:12] + '.npz')).write_text(line)\n"
            "print('RAN', line)\n")
        (pr / "prr_ibu.py").write_text(
            "import sys, pathlib, os\n"
            "o = pathlib.Path(sys.argv[sys.argv.index('--out') + 1]); o.mkdir()\n"
            "(o / 'route2.npz').write_text('x'); (o / 'route2.json').write_text('{}')\n"
            "sys.exit(int(os.environ.get('PRR_IBU_RC', '0')))\n")
        (self.D / "setup_salloc_env.sh").write_text(f"export PYTHONPATH={str(r / 'mods')!r}\n")
        (r / "mods").mkdir()
        for m in ("lightgbm", "scipy"):
            (r / "mods" / f"{m}.py").write_text("")
        (r / "bin").mkdir()
        (r / "bin" / "fake_time").write_text('#!/bin/bash\nshift 3\nexec "$@"\n')
        (r / "bin" / "sha256sum").write_text('#!/bin/bash\nexec shasum -a 256 "$@"\n')
        (r / "bin" / "squeue").write_text('#!/bin/bash\nprintf "%s" "$PRR_FAKE_SQUEUE"\nexit "${PRR_FAKE_SQUEUE_RC:-0}"\n')
        for b in ("fake_time", "sha256sum", "squeue"):
            (r / "bin" / b).chmod(0o755)
        g = ["git", "-C", str(self.D), "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run(["git", "init", "-q", str(self.D)], check=True)
        subprocess.run(g + ["add", "-A"], check=True)
        subprocess.run(g + ["commit", "-q", "-m", "x"], check=True)
        self.pin = subprocess.run(["git", "-C", str(self.D), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        self.OUT.mkdir()
        (self.OUT / "manifest.json").write_text("[]")
        a = P.staged_paths(self.OUT / "stage", self.OUT / "runs")
        (self.OUT / "queues").mkdir()
        for j in P.JOBS:
            (self.OUT / "queues" / f"{j}.tsv").write_text("\n".join(P.queue_lines(a, j)) + "\n")
        env = {k: v for k, v in os.environ.items() if not k.startswith("SLURM_")}
        self.env = {**env, "PRR_SMOKE": "1", "PRR_TIME_BIN": str(r / "bin" / "fake_time"),
                    "PATH": f"{r / 'bin'}:{os.environ['PATH']}"}

    def tearDown(self):
        self.tmp.cleanup()

    def job(self, mode, pin=None, **env):
        script = os.environ.get("PRR_SBATCH", str(HERE / "sbatch_prr.sh"))  # the mutation harness's copy
        return subprocess.run(["bash", script, mode, str(self.D), pin or self.pin, str(self.OUT)],
                              capture_output=True, text=True, env={**self.env, **env}, timeout=900)

    def test_dry_then_a_full_job_then_ibu(self):
        p = self.job("dry")
        self.assertEqual(p.returncode, 0, p.stderr)
        L = self.OUT / "log-dry"
        dry = [l.split("\t")[0] for l in (self.OUT / "queues" / "dry.tsv").read_text().splitlines()[1:]]
        self.assertEqual(sorted(x.stem for x in L.glob("*.end")), sorted(dry))
        self.assertTrue((L / "DONE").exists() and (L / "pair.json").exists())
        self.assertIn("RAN", (L / "tasks" / f"{dry[0]}.log").read_text())
        p = self.job("cap")
        self.assertEqual(p.returncode, 0, p.stderr)
        n = len((self.OUT / "queues" / "cap.tsv").read_text().splitlines()) - 1
        self.assertEqual(json.loads((self.OUT / "log-cap" / "DONE").read_text())["ended"], n)
        self.assertEqual(self.job("ibu").returncode, 0)
        self.assertTrue((self.OUT / "log-ibu" / "DONE").exists())

    def test_a_failed_pair_stops_the_dry_run_and_every_full_job(self):
        p = self.job("dry", PRR_PAIR_RC="1")
        self.assertEqual(p.returncode, 1)
        self.assertTrue((self.OUT / "log-dry" / "STOP").exists())
        self.assertFalse((self.OUT / "log-dry" / "DONE").exists())
        for m in ("iter", "cap", "misc", "ibu"):
            self.assertEqual(self.job(m).returncode, 2, m)

    def test_an_ens1_job_queued_or_running_refuses_the_dry_run(self):
        for q in ("ens1_stage2|RUNNING\n", "x|RUNNING\nens1_post|PENDING\n"):
            p = self.job("dry", PRR_FAKE_SQUEUE=q)
            self.assertEqual(p.returncode, 2, q)
            self.assertIn("ens1_", p.stderr)
            self.assertFalse((self.OUT / "stage.json").exists())
        self.assertEqual(self.job("dry", PRR_FAKE_SQUEUE_RC="1").returncode, 2)  # squeue cannot answer: refuse
        self.assertFalse((self.OUT / "log-dry").exists())
        self.assertEqual(self.job("dry", PRR_FAKE_SQUEUE="prr_other|RUNNING\nxens1_a|RUNNING\n").returncode, 0)

    def test_a_refused_staging_stops_before_any_task(self):
        p = self.job("dry", PRR_STAGE_RC="2")
        self.assertEqual(p.returncode, 1)
        self.assertEqual(list((self.OUT / "log-dry").glob("*.start")), [])

    def test_a_limit_above_the_declared_is_refused(self):
        p = self.job("dry", PRR_TIMELIMIT="5:16:00")
        self.assertEqual(p.returncode, 2)
        self.assertFalse((self.OUT / "log-dry").exists())
        self.assertEqual(self.job("dry", PRR_TIMELIMIT="1-00:00:00").returncode, 2)
        self.assertEqual(self.job("dry", PRR_TIMELIMIT="4:00:00").returncode, 0)

    def test_outside_slurm_without_the_smoke_flag_it_refuses(self):
        env = {k: v for k, v in self.env.items() if k != "PRR_SMOKE"}
        p = subprocess.run(["bash", os.environ.get("PRR_SBATCH", str(HERE / "sbatch_prr.sh")), "dry", str(self.D),
                            self.pin, str(self.OUT)], capture_output=True, text=True, env=env, timeout=60)
        self.assertEqual(p.returncode, 2)

    def test_a_failed_task_leaves_no_done(self):
        p = self.job("dry", PRR_FAIL_TASK="prr_K2_nominal")
        self.assertEqual(p.returncode, 1)
        self.assertTrue((self.OUT / "log-dry" / "FAILED").exists())
        self.assertFalse((self.OUT / "log-dry" / "DONE").exists())

    def test_a_wrong_pin_or_a_rerun_is_refused(self):
        self.assertEqual(self.job("dry", pin="0" * 40).returncode, 2)
        self.assertEqual(self.job("dry").returncode, 0)
        self.assertEqual(self.job("dry").returncode, 2)

    def test_a_full_job_refuses_a_changed_stage(self):
        self.assertEqual(self.job("dry").returncode, 0)
        p = self.job("misc", PRR_VERIFY_RC="2")
        self.assertEqual(p.returncode, 1)
        self.assertTrue((self.OUT / "log-misc" / "STOP").exists())


if __name__ == "__main__":
    unittest.main()
