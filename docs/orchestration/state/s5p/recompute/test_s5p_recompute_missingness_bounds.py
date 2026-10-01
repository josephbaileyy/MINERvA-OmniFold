"""Controls for the report-side missing-experiment bounds (s5p_recompute_missingness_bounds): the certificate's
soundness by exhaustive enumeration, fail-closed handling, the not-submitted exclusion, coherence, power
denominators, and an end-to-end run on the recompute's toy world."""
import itertools
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
sys.path.insert(1, str(REPO / "nd-unfolding"))
sys.path.insert(1, str(REPO / "nd-unfolding" / "tests"))
sys.path.insert(1, str(HERE))
import s5p_recompute as R  # noqa: E402
import s5p_recompute_missingness_bounds as M  # noqa: E402
from s5p_recompute_toy import Toy  # noqa: E402


def certificate(entries, L, alpha, form="holds"):
    """The module's certificate on a bare family (entries with test, k, B, p; L per test)."""
    prim = R.holm_determined(entries, alpha)
    rej = [e["test"] for e, d in zip(entries, prim) if d["decision"] == "rejected"]
    per = {e["test"]: M.bound(e["k"], e["B"], L[i]) for i, e in enumerate(entries)}
    return M.certify([e["test"] for e in entries], per, rej, alpha).get(form), rej


class CertificateSoundness(unittest.TestCase):
    def test_certified_rejections_hold_under_every_assignment(self):
        """Exhaustive: whenever a certificate form holds, every assignment of the missing experiments (each test's
        count raised by 0..L at size B + L) leaves every primary rejection rejected."""
        r = np.random.default_rng(20260930)
        certified = {"holds": 0, "simple_alpha_over_m": 0}
        only_step_aware = 0
        for _ in range(500):
            m = 4
            B = [int(r.choice([150, 200, 400, 800, 1600])) + int(r.integers(0, 50)) for _ in range(m)]
            k = [int(r.choice([0, 0, 0, 1, 2, 5, 40, 300])) for _ in range(m)]
            L = [int(r.integers(0, 4)) for _ in range(m)]
            ents = [{"test": f"t{i}", "k": k[i], "B": B[i], "p": (k[i] + 1) / (B[i] + 1)} for i in range(m)]
            ok_step, rej = certificate(ents, L, 0.05)
            ok_simple, _ = certificate(ents, L, 0.05, "simple_alpha_over_m")
            if ok_simple:
                self.assertTrue(ok_step)  # the simple form implies the step-aware one
            only_step_aware += bool(ok_step and not ok_simple)
            for form, ok in (("holds", ok_step), ("simple_alpha_over_m", ok_simple)):
                if not ok:
                    continue
                certified[form] += 1
                for d in itertools.product(*[range(x + 1) for x in L]):
                    e2 = [{"test": e["test"], "k": e["k"] + d[i], "B": e["B"] + L[i],
                           "p": (e["k"] + d[i] + 1) / (e["B"] + L[i] + 1)} for i, e in enumerate(ents)]
                    dec = {x["test"]: x["decision"] for x in R.holm_determined(e2, 0.05)}
                    for t_ in rej:
                        self.assertEqual(dec[t_], "rejected", (form, k, B, L, d))
        self.assertGreater(certified["simple_alpha_over_m"], 20)  # each form exercised, not vacuously true
        self.assertGreater(only_step_aware, 5)  # the step-aware form certifies cases the simple one cannot

    def test_without_missing_experiments_the_step_aware_form_is_exact(self):
        """L = 0: every primary rejection (distinct p) is certified by the step-aware form."""
        r = np.random.default_rng(7)
        for _ in range(300):
            B = [int(r.choice([200, 800, 1999])) for _ in range(4)]
            k = [int(r.choice([0, 1, 3, 50])) for _ in range(4)]
            ents = [{"test": f"t{i}", "k": k[i], "B": B[i], "p": (k[i] + 1) / (B[i] + 1)} for i in range(4)]
            if len({e["p"] for e in ents}) < 4:
                continue
            ok, rej = certificate(ents, [0] * 4, 0.05)
            if rej:
                self.assertTrue(ok, (k, B))


def toy_record(tmp):
    t = Toy(tmp / "w")
    base = t.truth["MnvTune_v1"]
    t.set_data(base * np.repeat(np.linspace(0.7, 1.3, 4), base.size // 4))
    t.calibration("MnvTune_v1", 800)
    t.calibration("GiBUU_2019", 200)
    t.status("MnvTune_v1", 800, True, "maximum reached")
    t.status("GiBUU_2019", 200, True, "maximum reached")
    t.power("P1_a1.0", 20, "MnvTune_v1", np.repeat(np.linspace(0.7, 1.3, 4), base.size // 4))
    pw = {"P1_a1.0": {"glob": str(t.root / "pow/P1_a1.0/pow_P1_a1.0_s*.npz"), "surrogate_seed0": 1951000,
                      "n": 24, "null": "MnvTune_v1"}}
    return R.jsonable(R.evaluate(t.design(power=pw), t.v_path, t.contract, log=lambda *a: None))


def disposition(counts_by_null, power=None):
    nulls = {}
    for k, c in counts_by_null.items():
        lost = sum(v for x, v in c.items() if x in ("submitted_interrupted", "submitted_never_started",
                                                    "submitted_task_no_log", "submitted_failed_rc"))
        nulls[k] = {"counts": c, "lost_work": lost, "recompute_missing_seeds_equal": True,
                    "not_submitted": c.get("not_submitted_no_admission", 0)}
    return {"nulls": nulls, "power": power or {}}


class EndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = Path(tempfile.mkdtemp(prefix="s5p_missbounds_"))
        cls.rec = toy_record(cls.dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir, ignore_errors=True)

    def test_complete_run_certifies_and_bounds(self):
        d = disposition({"MnvTune_v1": {"submitted_interrupted": 2, "submitted_never_started": 3},
                         "GiBUU_2019": {}},
                        {"P1_a1.0": {"counts": {"submitted_interrupted": 1}, "lost_work": 1}})
        out = M.evaluate_bounds(self.rec, d)
        self.assertEqual(out["status"], "complete", out["incomplete"])
        self.assertIn("MnvTune_v1:total", out["primary_rejections"])
        a, b = out["populations"]["a_interrupted"], out["populations"]["b_all_lost"]
        self.assertEqual(out["losses"]["MnvTune_v1"]["L"], {"a_interrupted": 2, "b_all_lost": 5})
        w = b["per_test"]["MnvTune_v1:total"]["worst"]
        k0 = self.rec["nulls"]["MnvTune_v1"]["tests"]["total"]["k"]
        self.assertEqual((w["k"], w["B"]), (k0 + 5, 805))
        self.assertTrue(a["certificate"]["holds"])
        self.assertFalse(a["certificate"]["simple_alpha_over_m"])  # GiBUU rejections sit at steps 2-3
        # (b) L = 5 at MnvTune: its worst p 6/806 rises above GiBUU's 1/201, GiBUU moves to step 0, where its upper
        # end 0.018 straddles 0.0125 and the family stops undetermined. Not certified, and a run shows the change.
        self.assertFalse(b["certificate"]["holds"])
        self.assertEqual(b["runs_not_proven_extremal"]["all_worst"]["GiBUU_2019:total"], "undetermined")
        self.assertIn("all_worst:MnvTune_v1:total", b["decisions_changed_in_runs"])
        self.assertEqual(out["holm_level"], 0.95)
        p = out["power"]["P1_a1.0"]
        self.assertEqual((p["n_present"], p["L"]), (20, 1))
        c = p["shape"]["0.05"]["rank_unshifted"]["count"]
        self.assertEqual(p["shape"]["0.05"]["rank_unshifted"]["bounds"], [c / 21, (c + 1) / 21])

    def test_unknown_losses_fail_closed(self):
        d = disposition({"MnvTune_v1": {"submitted_task_no_log_unverified": 6}, "GiBUU_2019": {}})
        out = M.evaluate_bounds(self.rec, d)
        self.assertEqual(out["status"], "INCOMPLETE")
        self.assertEqual(out["losses"]["MnvTune_v1"]["L"], {"a_interrupted": 6, "b_all_lost": 6})
        self.assertTrue(any("not-established" in x for x in out["incomplete"]))

    def test_not_submitted_is_excluded(self):
        d = disposition({"MnvTune_v1": {"not_submitted_no_admission": 200}, "GiBUU_2019": {}})
        out = M.evaluate_bounds(self.rec, d)
        self.assertEqual(out["losses"]["MnvTune_v1"]["L"], {"a_interrupted": 0, "b_all_lost": 0})
        self.assertEqual(out["losses"]["MnvTune_v1"]["not_submitted"], 200)
        self.assertEqual(out["status"], "complete")

    def test_large_loss_breaks_the_certificate(self):
        d = disposition({"MnvTune_v1": {"submitted_never_started": 40}, "GiBUU_2019": {}})
        out = M.evaluate_bounds(self.rec, d)
        self.assertTrue(out["populations"]["a_interrupted"]["certificate"]["holds"])  # never-started not in (a)
        self.assertFalse(out["populations"]["b_all_lost"]["certificate"]["holds"])
        self.assertIn("NOT certified", out["populations"]["b_all_lost"]["verdict"])

    def test_incoherent_claim_and_non_terminal_are_incomplete(self):
        import copy
        rec = copy.deepcopy(self.rec)
        rec["nulls"]["MnvTune_v1"]["tests"]["total"]["k"] += 1
        rec["nulls"]["GiBUU_2019"]["calibration"]["final_status_present"] = False
        out = M.evaluate_bounds(rec, disposition({"MnvTune_v1": {}, "GiBUU_2019": {}}))
        joined = "\n".join(out["incomplete"])
        self.assertIn("claim k", joined)
        self.assertIn("no final status", joined)
        d = disposition({"MnvTune_v1": {}, "GiBUU_2019": {}})
        d["nulls"]["MnvTune_v1"]["recompute_missing_seeds_equal"] = False
        self.assertIn("differ", "\n".join(M.evaluate_bounds(self.rec, d)["incomplete"]))


if __name__ == "__main__":
    unittest.main()
