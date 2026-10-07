"""Controls for s5p_missing_sensitivity (a labelled, report-only bound on the seeds production lost).

The classification:
- counts completed, interrupted, never-started and unestablished seeds per submitted batch, from the tables, the
  ledger and the task-log classification;
- does not count unsubmitted batches as missing;
- refuses when its completed counts differ from the evaluated ensemble.

The bounds shift the claim counts as stated; the corners are labelled descriptive. The all-assignment certificate
holds for a strong rejection and fails both for a borderline one and when separation fails. The looks re-apply the
frozen stopping rule with the draws missing by each look. Power bounds bracket the measured fraction. The CLI writes
a separate file and never overwrites one."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
import s5p_inference as si  # noqa: E402
import s5p_missing_sensitivity as ms  # noqa: E402


def leaf(k, b):
    return {"p": (k + 1) / (b + 1), "k": k, "B": b}


def entry(kt, ks, b):
    """A null without M1 (its family is its c-variants), as s5p_joint.test_null writes it."""
    v = {"0.0": {"total": leaf(kt, b), "shape": leaf(ks, b)}}
    e = {"variants": v, "robustness_variants": {}}
    for s in ("total", "shape"):
        e[s] = v["0.0"][s]
        e[s + "_robust"] = v["0.0"][s]
    return e


def evaluate(tests):
    claims = {f"{n}:{s}": {kk: e[s][kk] for kk in ("p", "k", "B")} for n, e in tests.items() for s in ("total", "shape")}
    d = si.holm_determined(claims, 0.05)
    return {"tests": tests, "decisions": d, "decisions_robust_kappa": d, "robust_to_the_sub_fine_residual": {t: True for t in d}}


class World:
    """Two nulls (A: batches 0, 1 submitted, 2 not; Z: batch 0), 2 tasks x 3 seeds per batch, one power set."""

    def __init__(self, root: Path):
        self.root = root
        self.tables = root / "tables"
        self.tables.mkdir()
        self.prod = root / "prod"
        self.status = root / "status"
        self.status.mkdir()
        self.ledger = root / "ledger.jsonl"
        self.tasks = []
        led = []
        self.base = {"A": 1000, "Z": 5000, "P1_a1.0": 9000}
        for lane, kind, batches in (("A", "cal", (0, 1, 2)), ("Z", "cal", (0,)), ("P1_a1.0", "pow", (0,))):
            for b in batches:
                stem = f"cal-{lane}-b{b}" if kind == "cal" else f"pow-{lane}"
                out = self.prod / lane
                out.mkdir(parents=True, exist_ok=True)
                rows = []
                for t in range(2):
                    first = self.base[lane] + 6 * b + 3 * t
                    rows.append(f"{stem}_{t}\ts5p_nullexp.py\t--pseudo-seeds\t{first}:{first + 2}\t--tag\t{lane}\t--out\t{out}")
                (self.tables / f"{stem}.tsv").write_text("# table\n" + "\n".join(rows) + "\n")
                if not (lane == "A" and b == 2):  # batch 2 of A never submitted
                    led.append({"kind": "job", "job_id": str(100 + len(led)), "token": f"2026-10-01T00:00:00Z-1-{ms.label_of(stem)}"})
        led.append({"kind": "budget", "budget_sha256": "x"})
        self.ledger.write_text("\n".join(json.dumps(r) for r in led) + "\n")

    def design(self):
        return {"alpha_family": 0.05,
                "nulls": {n: {"calibration_glob": str(self.prod / n / f"{n}_s*.npz"),
                              "calibration_n": {"min": 0, "max": 1999, "sequential_status": str(self.status / f"{n}-final.json")}}
                          for n in ("A", "Z")},
                "power": {"P1_a1.0": {"glob": str(self.prod / "P1_a1.0" / "P1_a1.0_s*.npz"), "n": 6}}}

    def product(self, lane, seed):
        (self.prod / lane / f"{lane}_s{seed}.npz").write_bytes(b"x")

    def states(self, mapping):
        self.tasks.append({"lane": "x", "seeds": {str(s): {"state": st} for s, st in mapping.items()}})
        return {"tasks": self.tasks}


def build(root: Path):
    w = World(root)
    # A: batch 0 seeds 1000..1005 all complete; batch 1 seeds 1006..1011: 1006-1008 complete, 1009 interrupted,
    # 1010 never started, 1011 unestablished (no product, no log state)
    for s in list(range(1000, 1006)) + [1006, 1007, 1008]:
        w.product("A", s)
    for s in range(5000, 5006):
        w.product("Z", s)
    for s in (9000, 9001, 9002, 9003, 9004):
        w.product("P1_a1.0", s)  # 9005 interrupted
    states = w.states({1009: "interrupted", 1010: "never started", 9005: "interrupted"})
    return w, states


class Classification(unittest.TestCase):
    def test_counts_and_unsubmitted_batch(self):
        with tempfile.TemporaryDirectory() as d:
            w, st = build(Path(d))
            c = ms.classify(ms.read_tables(w.tables), ms.submitted_labels(w.ledger), st)
            a = c[("cal", "A")]
            self.assertEqual(a["by_batch"][0], {"completed": 6})
            self.assertEqual(a["by_batch"][1], {"completed": 3, "interrupted": 1, "never started": 1, "unestablished": 1})
            self.assertEqual(a["not_submitted_batches"], [2])
            self.assertNotIn(2, a["by_batch"])
            # the unestablished seed counts pessimistically in the interrupted-only bound
            self.assertEqual(ms.missing(a), {"interrupted_or_unestablished": 2, "unestablished": 1, "all": 3})
            self.assertEqual(ms.missing(a, upto_batch=1), {"interrupted_or_unestablished": 0, "unestablished": 0, "all": 0})
            self.assertEqual(ms.missing(c[("pow", "P1_a1.0")])["all"], 1)

    def test_label_mapping(self):
        self.assertEqual(ms.label_of("cal-GENIE_2_12_10_CV-b2"), "s5p_cal_genie_2_12_10_cv_b2")
        self.assertEqual(ms.label_of("pow-P3_a1.0"), "s5p_pow_p3_a1p0")

    def test_identity_with_the_evaluator_selection(self):
        with tempfile.TemporaryDirectory() as d:
            w, st = build(Path(d))
            design = w.design()
            c = ms.classify(ms.read_tables(w.tables), ms.submitted_labels(w.ledger), st)
            res = evaluate({"A": entry(0, 0, 9), "Z": entry(0, 0, 6)})  # A has 9 completed: consistent
            ms.check_identity(res, design, c)
            with self.assertRaises(SystemExit):  # B differs from the selection
                ms.check_identity(evaluate({"A": entry(0, 0, 10), "Z": entry(0, 0, 6)}), design, c)
            # a partial file is excluded by the evaluator's selection and by the classification alike
            (w.prod / "A" / "A_s1011.partial-77.npz").write_bytes(b"x")
            ms.check_identity(res, design, c)
            # a product outside every submitted table row is in the selection but not classified: refused
            w.product("A", 1999)
            with self.assertRaises(SystemExit):
                ms.check_identity(res, design, c)


class Bounds(unittest.TestCase):
    def test_shifts(self):
        c, m = leaf(2, 100), {"interrupted_or_unestablished": 3, "all": 7}
        self.assertEqual(ms.shifted(c, "worst_interrupted", m)["k"], 5)
        self.assertEqual(ms.shifted(c, "worst_interrupted", m)["B"], 103)
        self.assertEqual((ms.shifted(c, "worst_all_missing", m)["k"], ms.shifted(c, "worst_all_missing", m)["B"]), (9, 107))
        self.assertEqual((ms.shifted(c, "best_all_missing", m)["k"], ms.shifted(c, "best_all_missing", m)["B"]), (2, 107))
        self.assertEqual(ms.shifted({"p": 1.0, "k": 0, "B": 0}, "worst_all_missing", m)["B"], 0)

    def _classes(self, mA, mZ):
        def rec(m):
            return {"by_batch": {0: {"completed": 1, "interrupted": m[0], "never started": m[1], "unestablished": 0}},
                    "seeds": {"completed": [1]}, "not_submitted_batches": []}
        return {("cal", "A"): rec(mA), ("cal", "Z"): rec(mZ)}

    def test_strong_rejection_certified_and_corners_descriptive(self):
        res = evaluate({"A": entry(0, 0, 1999), "Z": entry(900, 900, 1999)})
        self.assertEqual(res["decisions"]["A:total"]["decision"], "rejected")
        # 5 missing draws: worst (5, 2004) has CP upper ~0.006 < alpha/m = 0.0125 (four tests here)
        out = ms.decisions(res, {"alpha_family": 0.05}, self._classes((2, 3), (2, 3)))
        self.assertTrue(out["certificates"]["all"]["primary"]["certified"])
        self.assertEqual(out["certificates"]["all"]["certified_rejections"], ["A:shape", "A:total"])
        self.assertTrue(out["scenarios"]["worst_all_missing"]["survives"]["A:total"])
        self.assertEqual(out["scenarios"]["worst_all_missing"]["extremal"], "not proven (descriptive corner)")

    def test_borderline_rejection_not_certified(self):
        # k = 0 at B = 999: CP upper 0.0037 < 0.005 rejects; with 40 extra exceedances it cannot stay below
        res = evaluate({"A": entry(0, 0, 999), "Z": entry(900, 900, 1999)})
        self.assertEqual(res["decisions"]["A:total"]["decision"], "rejected")
        out = ms.decisions(res, {"alpha_family": 0.05}, self._classes((20, 20), (0, 0)))
        cert = out["certificates"]["all"]["primary"]
        self.assertFalse(cert["all_below_alpha_over_m"])
        self.assertFalse(cert["certified"])
        self.assertEqual(out["certificates"]["all"]["certified_rejections"], [])
        self.assertFalse(out["scenarios"]["worst_all_missing"]["survives"]["A:total"])

    def test_separation_failure_not_certified(self):
        # A stays below alpha/m at its worst (3, 3003), but Z (not rejected) could reach a smaller best p
        # (10, 10400) with many missing draws: R cannot be guaranteed first, so nothing is certified
        res = evaluate({"A": entry(0, 0, 3000), "Z": entry(10, 10, 400)})
        self.assertEqual(res["decisions"]["A:total"]["decision"], "rejected")
        self.assertNotEqual(res["decisions"]["Z:total"]["decision"], "rejected")
        out = ms.decisions(res, {"alpha_family": 0.05}, self._classes((3, 0), (0, 10000)))
        cert = out["certificates"]["all"]["primary"]
        self.assertTrue(cert["all_below_alpha_over_m"])
        self.assertFalse(cert["separated"])
        self.assertFalse(cert["certified"])


class Status(unittest.TestCase):
    def test_counterexample_versus_unestablished_wording(self):
        def rec(i, n):
            return {"by_batch": {0: {"completed": 1, "interrupted": i, "never started": n}}, "seeds": {"completed": [1]}, "not_submitted_batches": []}
        res = evaluate({"A": entry(0, 0, 999), "Z": entry(900, 900, 1999)})
        # 40 missing draws flip A at the worst corner: an explicit counterexample
        out = ms.decisions(res, {"alpha_family": 0.05}, {("cal", "A"): rec(20, 20), ("cal", "Z"): rec(0, 0)})
        self.assertTrue(out["per_test_status"]["A:total"].startswith("can change (counterexample: "))
        # no missing draws: certified
        out = ms.decisions(res, {"alpha_family": 0.05}, {("cal", "A"): rec(0, 0), ("cal", "Z"): rec(0, 0)})
        self.assertTrue(out["per_test_status"]["A:total"].startswith("certified"))
        self.assertEqual(out["per_test_status"]["Z:total"], "not certified: survival under all missing-outcome assignments is unestablished")
        # an incomplete output never certifies
        out = ms.decisions(res, {"alpha_family": 0.05}, {("cal", "A"): rec(0, 0), ("cal", "Z"): rec(0, 0)}, complete=False)
        self.assertFalse(out["certificates"]["all"]["primary"]["certified"])
        self.assertFalse(out["per_test_status"]["A:total"].startswith("certified"))


class Looks(unittest.TestCase):
    def _design(self, sdir):
        return {"alpha_family": 0.05, "nulls": {"A": {"calibration_n": {"min": 0, "max": 1999,
                                                                       "sequential_status": str(sdir / "A-final.json")}}}}

    def test_rule_reapplied_with_draws_missing_by_each_look(self):
        with tempfile.TemporaryDirectory() as d:
            sdir = Path(d)
            (sdir / "A-B0.json").write_text(json.dumps({"B": 0, "stop": False, "reason": "no calibration product yet"}))
            th = sorted(set(si.holm_thresholds(0.05, 2)) | {0.01, 0.05})
            dec = {s: si.sequential_decision(0, 1300, th) for s in ("total", "shape")}
            (sdir / "A-B1300.json").write_text(json.dumps({"B": 1300, "decisions": dec, "stop": True, "reason": "rule met for both tests"}))
            classes = {("cal", "A"): {"by_batch": {0: {"completed": 1300, "interrupted": 30, "never started": 10}},
                                      "seeds": {}, "not_submitted_batches": []}}
            lk = ms.looks(self._design(sdir), classes, 0.05)["A"]
            out = lk["looks"]
            self.assertTrue(lk["all_looks_mapped"])
            self.assertEqual((out[0]["batches_before_look"], out[1]["batches_before_look"]), (0, 1))
            self.assertEqual(out[1]["worst_all_missing"]["missing_by_look"]["all"], 40)
            self.assertTrue(out[1]["best_all_missing"]["rule_stops"])
            self.assertFalse(out[1]["worst_all_missing"]["rule_stops"])  # k = 40 at B = 1340: no bound below 0.005

    def test_wholly_lost_batch_makes_the_look_unresolved(self):
        # batch 1 lost every product: the look after batch 1 and the look after batch 2 would share B = 200 (one
        # status file, the later overwriting the earlier), so batch counts 1 and 2 both fit B = 200
        with tempfile.TemporaryDirectory() as d:
            sdir = Path(d)
            th = sorted(set(si.holm_thresholds(0.05, 2)) | {0.01, 0.05})
            dec = {s: si.sequential_decision(0, 200, th) for s in ("total", "shape")}
            (sdir / "A-B200.json").write_text(json.dumps({"B": 200, "decisions": dec, "stop": False, "reason": "continue"}))
            classes = {("cal", "A"): {"by_batch": {0: {"completed": 200}, 1: {"interrupted": 34, "never started": 166},
                                                   2: {"completed": 150, "interrupted": 50}},
                                      "seeds": {}, "not_submitted_batches": []}}
            lk = ms.looks(self._design(sdir), classes, 0.05)["A"]
            self.assertFalse(lk["all_looks_mapped"])
            self.assertIsNone(lk["looks"][0]["batches_before_look"])
            self.assertIn("unresolved", lk["looks"][0]["batch_mapping"])
            self.assertNotIn("worst_all_missing", lk["looks"][0])


class Power(unittest.TestCase):
    def test_bounds_bracket(self):
        res = {"power": {"levels": [0.05], "P1_a1.0": {"n": 5, "total": {"0.05": {
            "unshifted": {"power": 0.8, "n": 5}, "claim_rule": {"power": 0.6, "n": 5}, "claim_rule_determined": {"power": 0.4, "n": 5}}},
            "shape": {}}}}
        classes = {("pow", "P1_a1.0"): {"by_batch": {0: {"interrupted": 1}}, "seeds": {}, "not_submitted_batches": []}}
        b = ms.power_bounds(res, classes)["P1_a1.0"]["total"]["0.05"]["claim_rule"]
        self.assertAlmostEqual(b["lower_none_detected"], 3 / 6)
        self.assertAlmostEqual(b["upper_all_detected"], 4 / 6)


class Complete(unittest.TestCase):
    def test_complete_run_exits_0_and_certifies(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            w, st = build(root)
            w.product("A", 1011)  # the unestablished seed now has its product
            w.product("A", 1010)  # and the never-started one too: only seed 1009 (interrupted) and 9005 are missing
            st["tasks"][0]["seeds"].pop("1010")
            for n in ("A", "Z"):
                (w.status / f"{n}-final.json").write_text(json.dumps({"B": 0, "stop": True, "reason": "rule met for both tests"}))
            seed_states = root / "states.json"
            seed_states.write_text(json.dumps(st))
            dpath = root / "design.json"
            dpath.write_text(json.dumps(w.design()))
            res = evaluate({"A": entry(0, 0, 11), "Z": entry(0, 0, 6)})
            res["design_sha256"] = hashlib.sha256(dpath.read_bytes()).hexdigest()
            res["power"] = {"levels": [0.05], "P1_a1.0": {"n": 5, "total": {}, "shape": {}}}
            epath = root / "evaluate.json"
            epath.write_text(json.dumps(res))
            out = root / "sens.json"
            rc = ms.main(["--evaluate", str(epath), "--design", str(dpath), "--tables", str(w.tables), "--ledger", str(w.ledger),
                          "--seed-states", str(seed_states), "--out", str(out)])
            r = json.loads(out.read_text())
            self.assertEqual((rc, r["status"]), (0, "COMPLETE"))
            self.assertEqual(r["classification"]["cal:A"]["missing_seeds"], {"interrupted": [1009]})


class Cli(unittest.TestCase):
    def test_separate_file_design_check_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            w, st = build(root)
            seed_states = root / "states.json"
            seed_states.write_text(json.dumps(st))
            design = w.design()
            dpath = root / "design.json"
            dpath.write_text(json.dumps(design))
            res = evaluate({"A": entry(0, 0, 9), "Z": entry(0, 0, 6)})
            res["design_sha256"] = hashlib.sha256(dpath.read_bytes()).hexdigest()
            res["power"] = {"levels": [0.05], "P1_a1.0": {"n": 5, "total": {}, "shape": {}}}
            epath = root / "evaluate.json"
            epath.write_text(json.dumps(res))
            out = root / "sens.json"
            args = ["--evaluate", str(epath), "--design", str(dpath), "--tables", str(w.tables), "--ledger", str(w.ledger),
                    "--seed-states", str(seed_states), "--out", str(out)]
            before = epath.read_bytes()
            self.assertEqual(ms.main(args), 4)  # an unestablished seed and no final statuses: INCOMPLETE
            self.assertEqual(epath.read_bytes(), before)
            r = json.loads(out.read_text())
            self.assertEqual(r["status"], "INCOMPLETE")
            self.assertTrue(any("unestablished" in x for x in r["incomplete_reasons"]))
            self.assertTrue(any("no final status" in x for x in r["incomplete_reasons"]))
            for c in r["decisions"]["certificates"].values():
                self.assertFalse(c["primary"]["certified"])
            self.assertEqual(r["schema"], "s5p-missing-sensitivity/1")
            self.assertIn("LABELLED SENSITIVITY", r["label"])
            self.assertEqual(r["classification"]["cal:A"]["missing_seeds"]["unestablished"], [1011])
            with self.assertRaises(SystemExit):
                ms.main(args)
            dpath.write_text(json.dumps({**design, "alpha_family": 0.1}))
            with self.assertRaises(SystemExit):
                ms.main(args[:-1] + [str(root / "other.json")])


if __name__ == "__main__":
    unittest.main()
