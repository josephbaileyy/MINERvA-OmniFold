"""End-to-end controls for ``frozen-s`` and ``stopping``: the REAL ``s5p_joint.test_null``, ``s5p_seqstop.main`` and
``s5p_inference`` on a synthetic two-cell world; only the heavy loaders (stage-1 J matrix, the prediction, the
model's additive terms, the ensemble reader and the shift files) are replaced. Status files are written by the real
controller, one look per batch, so ``stopping`` must reproduce every one of them."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[4] / "nd-unfolding"))
import s5p_inference as si  # noqa: E402
import s5p_joint as sj  # noqa: E402
import s5p_robust_labels  # noqa: E402
import s5p_seqstop  # noqa: E402
import s5p_recovery as R  # noqa: E402

NAMES = ["a", "b"]
MU = np.array([1.0, 1.0])
OBS = np.array([1.6, 0.9])  # differs from MU in total and in shape


class FakeModel:
    def __init__(self, design, U):
        self.f_data = OBS.copy()
        self.jitters = OBS[None, :] + np.array([[0.0, 0.0], [1e-6, 0.0]])
        self.U = None

    def symmetry(self, design):
        return {}


def fake_ensemble(model, files):
    F = np.array([np.load(p)["f"] for p in files]) if files else np.zeros((0, 2))
    seeds = np.array([R.seed_of(Path(p)) for p in files], dtype=np.int64)
    return F, seeds


def fake_load_shift(spec, n):
    if spec is None:
        return None, None
    if "kappa" in json.dumps(spec) or spec.get("path", "").endswith("m1.npz"):
        return np.array([0.05, -0.05]), None
    return np.array([0.1, 0.1]), np.array([[0.2, 0.1], [0.3, 0.2], [0.25, 0.15]])


def patch():
    sj.j_matrix = lambda stage1, supported: (None, NAMES, np.array([0, 0]))
    sj.Model = FakeModel
    sj.check_v = lambda design, v: None
    sj.prediction = lambda path, U: (MU.copy(), np.full(2, 0.01))
    sj.ensemble = fake_ensemble
    sj.load_shift = fake_load_shift


class World:
    """Two nulls (X with an M1 declaration, Y without), 3 batches of 4 seeds each; some seeds lost."""

    def __init__(self, lost=(5, 10), extreme_recovered=(), max_b=12, power=True):
        patch()
        self.tmp = Path(tempfile.mkdtemp())
        t = self.tmp
        (t / "stage1.json").write_text("{}")
        (t / "contract.json").write_text(json.dumps({"measurement": {"partition_J": {"supported_cells": []}}}))
        np.savez(t / "V.npz", V=np.eye(2))
        self.tables = t / "tables"
        self.tables.mkdir()
        self.status = t / "status"
        rng = np.random.default_rng(1)
        self.design = {"stage1": str(t / "stage1.json"), "s5c_contract": str(t / "contract.json"),
                       "alpha_family": 0.05, "shift_coefficients": [0.0, 0.5, 1.0], "nulls": {}, "power": {},
                       "process_shift": {}, "m1_shift": {}}
        cls_tasks = []
        bases = (("X", 100), ("Y", 200))
        for key, base in bases:
            prod = t / "prod" / key
            prod.mkdir(parents=True)
            self.design["nulls"][key] = {"prediction": "p", "domain": None,
                                         "calibration_glob": str(prod / f"cal_{key}_s*.npz"), "surrogate_seed0": 7,
                                         "calibration_n": {"max": max_b, "min": 4,
                                                           "sequential_status": str(self.status / f"{key}-final.json")}}
            self.design["process_shift"][key] = {"mode": "bias_aligned_upper", "path": "d.npz"}
            self.design["m1_shift"][key] = ({"path": "m1.npz", "sha256": "x", "kappa": 2, "kappa_robust": 3}
                                            if key == "X" else {"none": "test"})
        self.write_design()
        for key, _ in bases:  # the controller's B = 0 look
            s5p_seqstop.main(["--design", str(self.design_path), "--v", str(t / "V.npz"), "--null", key,
                              "--status-dir", str(self.status)])
        for b in range(3):
            for key, base in bases:
                prod = t / "prod" / key
                first = base + 4 * b
                R_row = ["cal-%s-b%d_0" % (key, b), "s5p_nullexp.py", "--pseudo-seeds", f"{first}:{first + 3}",
                         "--tag", f"cal_{key}", "--out", str(prod)]
                (self.tables / f"cal-{key}-b{b}.tsv").write_text("# t\n" + "\t".join(R_row) + "\n")
                seeds = {}
                for i, s in enumerate(range(first, first + 4)):
                    lost_here = (s - base) in lost
                    seeds[str(s)] = {"state": "interrupted" if lost_here else "completed", "position": i}
                    f = MU + rng.normal(size=2) * 0.3
                    if not lost_here:
                        np.savez(prod / f"cal_{key}_s{s}.npz", f=f)
                    else:  # what the recovery would produce
                        rec = t / "rec" / "recovery" / "cal" / key
                        rec.mkdir(parents=True, exist_ok=True)
                        np.savez(rec / f"cal_{key}_s{s}.npz", f=(OBS * 4.0) if (s - base) in extreme_recovered else f)
                cls_tasks.append({"lane": f"cal-{key}", "seeds": seeds})
                if not (self.status / f"{key}-final.json").exists():  # the real controller's look after batch b
                    s5p_seqstop.main(["--design", str(self.design_path), "--v", str(t / "V.npz"), "--null", key,
                                      "--status-dir", str(self.status)])
        self.seed_states = {"tasks": cls_tasks}
        man = {"root": str(t / "rec"), "phase": "recovery", "tables": {}}
        for key, base in (("X", 100), ("Y", 200)):
            man["tables"][key] = {"lane": f"cal-{key}", "seeds": [base + x for x in lost]}
        (t / "man.json").write_text(json.dumps(man))
        (t / "empty-man.json").write_text(json.dumps(dict(man, tables={k: dict(v, seeds=[]) for k, v in man["tables"].items()})))
        # power: one lane at null Y with 24 alternative products and 3 lost (recovered) ones
        if power:
            pdir = t / "prod" / "pow" / "P"
            pdir.mkdir(parents=True)
            self.design["power"]["P"] = {"glob": str(pdir / "pow_P_s*.npz"), "surrogate_seed0": 9, "n": 27, "null": "Y"}
            prow = ["pow-P_0", "s5p_nullexp.py", "--pseudo-seeds", "900:926", "--tag", "pow_P", "--out", str(pdir)]
            (self.tables / "pow-P.tsv").write_text("# t\n" + "\t".join(prow) + "\n")
            pseeds = {}
            for i, s in enumerate(range(900, 927)):
                lost_here = s in (903, 910, 920)
                pseeds[str(s)] = {"state": "never started" if lost_here else "completed", "position": i}
                f = MU * 1.4 + rng.normal(size=2) * 0.3
                d = (t / "rec" / "recovery" / "pow" / "P") if lost_here else pdir
                d.mkdir(parents=True, exist_ok=True)
                np.savez(d / f"pow_P_s{s}.npz", f=f)
            cls_tasks.append({"lane": "pow-P", "seeds": pseeds})
        self.seed_states = {"tasks": cls_tasks}
        man = {"root": str(t / "rec"), "phase": "recovery", "tables": {}}
        for key, base in (("X", 100), ("Y", 200)):
            man["tables"][key] = {"lane": f"cal-{key}", "seeds": [base + x for x in lost]}
        if power:
            man["tables"]["P"] = {"lane": "pow-P", "seeds": [903, 910, 920]}
        (t / "man.json").write_text(json.dumps(man))
        (t / "empty-man.json").write_text(json.dumps(dict(man, tables={k: dict(v, seeds=[]) for k, v in man["tables"].items()})))
        self.write_design()
        # the frozen evaluation by the REAL s5p_joint.main (fixed counts = the frozen products), and the real labels
        ev_design = json.loads(json.dumps(self.design))
        for key in ev_design["nulls"]:
            ev_design["nulls"][key]["calibration_n"] = len(sj.product_files(ev_design["nulls"][key]["calibration_glob"]))
        (t / "ev-design.json").write_text(json.dumps(ev_design))
        assert sj.main(["evaluate", "--design", str(t / "ev-design.json"), "--v", str(t / "V.npz"),
                        "--out", str(t / "fe.json")]) == 0
        assert s5p_robust_labels.main(["--evaluate", str(t / "fe.json"), "--design", str(t / "ev-design.json"),
                                       "--out", str(t / "rl.json")]) == 0
        self.fe = json.loads((t / "fe.json").read_text())

    def write_design(self):
        self.design_path = self.tmp / "design.json"
        self.design_path.write_text(json.dumps(self.design))


class FrozenS(unittest.TestCase):
    def run_fs(self, w, man="man.json", out="fs.json"):
        return R.main(["frozen-s", "--design", str(w.design_path), "--evaluate", str(w.tmp / "fe.json"),
                       "--v", str(w.tmp / "V.npz"), "--manifest", str(w.tmp / man), "--tables", str(w.tables),
                       "--robust-labels", str(w.tmp / "rl.json"), "--out", str(w.tmp / out)])

    def test_empty_recovery_reproduces_the_primary_decisions(self):
        w = World()
        self.assertEqual(self.run_fs(w, man="empty-man.json"), 0)
        o = json.loads((w.tmp / "fs.json").read_text())
        self.assertEqual({k: v["decision"] for k, v in o["decisions_complete_set"].items()},
                         {k: v["decision"] for k, v in w.fe["decisions"].items()})

    def test_recovered_extreme_draws_are_counted_per_variant(self):
        w = World(extreme_recovered=(5,))
        self.assertEqual(self.run_fs(w), 0)
        o = json.loads((w.tmp / "fs.json").read_text())
        for key in ("X", "Y"):
            for name, v in o["tests"][key]["per_variant"].items():
                for s in ("total", "shape"):
                    self.assertEqual(v[s]["M_recovered"], 2)
                    self.assertGreaterEqual(v[s]["k_recovered"], 1)  # the 4 x OBS draw exceeds in every variant
            c = o["tests"][key]["complete_set"]["total"]["claim"]
            self.assertEqual(c["B"], w.fe["tests"][key]["total"]["B"] + 2)

    def test_empty_recovery_self_validates_labels_and_power(self):
        w = World()
        self.assertEqual(self.run_fs(w, man="empty-man.json"), 0)
        o = json.loads((w.tmp / "fs.json").read_text())
        self.assertIn("labels", o["self_validation"])
        self.assertEqual(o["power"]["P"]["frozen"]["n"], 24)

    def test_recovered_power_draws_enter_the_complete_set(self):
        w = World()
        self.assertEqual(self.run_fs(w), 0)
        o = json.loads((w.tmp / "fs.json").read_text())
        self.assertEqual(o["power"]["P"]["complete_set"]["n"], 27)
        self.assertEqual(o["power"]["P"]["M_recovered"], 3)

    def test_a_tampered_power_determined_value_fires(self):
        w = World()
        fe = json.loads((w.tmp / "fe.json").read_text())
        cr = fe["power"]["P"]["total"]["0.05"]["claim_rule_determined"]
        cr["power"] = float(cr["power"]) + 1e-9 if "power" in cr else cr
        (w.tmp / "fe.json").write_text(json.dumps(fe))
        with self.assertRaises(SystemExit):
            self.run_fs(w, man="empty-man.json")

    def test_a_tampered_label_fires(self):
        w = World()
        rl = json.loads((w.tmp / "rl.json").read_text())
        k = next(iter(rl["labels"]))
        rl["labels"][k] = "not robust" if rl["labels"][k] != "not robust" else "robust to the sub-fine residual"
        (w.tmp / "rl.json").write_text(json.dumps(rl))
        with self.assertRaises(SystemExit):
            self.run_fs(w, man="empty-man.json")

    def test_a_missing_recovered_product_fires(self):
        w = World()
        next((w.tmp / "rec" / "recovery" / "cal" / "X").glob("*.npz")).unlink()
        with self.assertRaises(SystemExit):
            self.run_fs(w)

    def test_a_tampered_frozen_value_fires(self):
        w = World()
        fe = json.loads((w.tmp / "fe.json").read_text())
        fe["tests"]["X"]["variants"]["0.5"]["null_T_total_sd"] += 1e-12
        (w.tmp / "fe.json").write_text(json.dumps(fe))
        with self.assertRaises(SystemExit):
            self.run_fs(w, man="empty-man.json")

    def test_a_wrong_variant_list_fires(self):
        w = World()
        fe = json.loads((w.tmp / "fe.json").read_text())
        fe["tests"]["Y"]["variants"]["m1+2"] = fe["tests"]["Y"]["variants"]["0.0"]
        (w.tmp / "fe.json").write_text(json.dumps(fe))
        with self.assertRaises(SystemExit):
            self.run_fs(w, man="empty-man.json")


class Stopping(unittest.TestCase):
    def run_st(self, w, out="st.json"):
        return R.main(["stopping", "--design", str(w.design_path), "--frozen-design", str(w.design_path),
                       "--v", str(w.tmp / "V.npz"), "--tables", str(w.tables), "--status-dir", str(w.status),
                       "--out", str(w.tmp / out)])

    def test_frozen_design_reproduces_every_real_controller_look(self):
        w = World()
        self.assertEqual(self.run_st(w), 0)
        o = json.loads((w.tmp / "st.json").read_text())
        looks = [r for v in o["nulls"].values() for r in v["looks"]]
        self.assertTrue(looks)
        self.assertTrue(all(r["reproduces_frozen_look"] for r in looks), looks)

    def test_a_stopping_controller_is_reproduced_and_decided_at_the_stop(self):
        w = World(max_b=7)  # the real controller stops at the maximum after batch 1
        self.assertTrue((w.status / "X-final.json").exists())
        self.assertEqual(self.run_st(w, out="st3.json"), 0)
        o = json.loads((w.tmp / "st3.json").read_text())
        looks = [r for v in o["nulls"].values() for r in v["looks"]]
        self.assertTrue(all(r["reproduces_frozen_look"] for r in looks), looks)
        self.assertTrue(any(r["stop_complete"] for r in looks))
        self.assertIsInstance(o["decisions_at_complete_batch_stop"], dict)
        self.assertEqual(len(o["decisions_at_complete_batch_stop_kappa3_replace"]), 4)

    def test_a_wrong_minimum_is_detected(self):
        w = World()
        d = json.loads(w.design_path.read_text())
        d["nulls"]["X"]["calibration_n"]["min"] = 5
        alt = w.tmp / "alt-design.json"
        alt.write_text(json.dumps(d))
        R.main(["stopping", "--design", str(w.design_path), "--frozen-design", str(alt), "--v", str(w.tmp / "V.npz"),
                "--tables", str(w.tables), "--status-dir", str(w.status), "--out", str(w.tmp / "st2.json")])
        o = json.loads((w.tmp / "st2.json").read_text())
        self.assertFalse(all(r["reproduces_frozen_look"] for r in o["nulls"]["X"]["looks"]))


if __name__ == "__main__":
    unittest.main()
