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

    def __init__(self, lost=(5, 10), extreme_recovered=()):
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
                                         "calibration_n": {"max": 12, "min": 4,
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
        # the frozen evaluation: the real test_null on the frozen products, Holm with determinacy
        fe = {"tests": {}, "power": {"levels": [0.05, 0.005]}}
        claims = {}
        model = FakeModel(self.design, None)
        for key in ("X", "Y"):
            files = sj.product_files(self.design["nulls"][key]["calibration_glob"])
            e = sj.test_null(model, self.design, key, np.eye(2), NAMES, np.array([0, 0]), files, [0.0, 0.5, 1.0])
            e.pop("_nulls")
            fe["tests"][key] = e
            for s in ("total", "shape"):
                claims[f"{key}:{s}"] = {k: e[s][k] for k in ("p", "k", "B")}
        fe["decisions"] = si.holm_determined(claims, 0.05)
        self.fe = fe
        (t / "fe.json").write_text(json.dumps(fe))

    def write_design(self):
        self.design_path = self.tmp / "design.json"
        self.design_path.write_text(json.dumps(self.design))


class FrozenS(unittest.TestCase):
    def run_fs(self, w, man="man.json", out="fs.json"):
        return R.main(["frozen-s", "--design", str(w.design_path), "--evaluate", str(w.tmp / "fe.json"),
                       "--v", str(w.tmp / "V.npz"), "--manifest", str(w.tmp / man), "--tables", str(w.tables),
                       "--out", str(w.tmp / out)])

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
