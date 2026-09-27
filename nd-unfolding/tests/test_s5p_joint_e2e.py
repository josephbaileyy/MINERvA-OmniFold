"""End-to-end control of the joint-test evaluator and the sequential controller on synthetic products: build-v,
evaluate (shift variants, claim rule, Holm, power at two levels) and s5p_seqstop run through their entry points;
a null whose calibration shares the data's process gives a bulk p-value, a displaced prediction a small one, and a
declared shift raises the implied size of the unshifted test."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
import s5p_joint as sj  # noqa: E402
import s5p_seqstop as ss  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
STAGE1 = REPO / "docs/orchestration/state/s5p/stage1/stage1_inspect.json"
S5C = REPO / "docs/orchestration/state/s5c/contract.json"


def product(path, x, seed=None, lateral_z=None):
    meta = {"pseudo_seed": seed, "nuisance_draw": None if lateral_z is None else {"lateral_z": lateral_z, "normalization_z": 0.0}}
    np.savez_compressed(path, xsec_flat=x, meta=json.dumps(meta))


class E2E(unittest.TestCase):
    def test_build_v_evaluate_and_seqstop(self):
        rng = np.random.default_rng(11)
        stage1 = json.loads(STAGE1.read_text())
        supported = json.loads(S5C.read_text())["measurement"]["partition_J"]["supported_cells"]
        U, names, _ = sj.j_matrix(stage1, supported)
        n = U.shape[1]
        x0 = rng.uniform(0.5, 1.5, n) * 1e-39
        noise = lambda: x0 * (1 + 0.03 * rng.normal(size=n))  # noqa: E731
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            for sub in ("v", "cal_ok", "cal_bad", "alt", "lat"):
                (d / sub).mkdir()
            for i in range(60):
                product(d / "v" / f"v_s{i:04d}.npz", noise(), seed=1000 + i)
            for i in range(199):
                product(d / "cal_ok" / f"c_s{i:04d}.npz", noise(), seed=2000 + i)
                product(d / "cal_bad" / f"c_s{i:04d}.npz", 1.2 * noise(), seed=3000 + i)  # drawn at the displaced null's truth
            for i in range(40):
                product(d / "alt" / f"a_s{i:04d}.npz", x0 * 1.10 * (1 + 0.03 * rng.normal(size=n)), seed=4000 + i)
            product(d / "lat" / "b0.npz", x0 * 0.999)
            product(d / "lat" / "b1.npz", x0 * 1.001)
            for i in range(3):
                product(d / "lat" / f"j{i}.npz", x0 * (1 + 1e-4 * rng.normal(size=n)))
            product(d / "data.npz", noise())
            np.savez(d / "pred0.npz", xsec_flat=x0, sumw2_flat=(0.001 * x0) ** 2)
            np.savez(d / "pred1.npz", xsec_flat=x0 * 1.2, sumw2_flat=(0.001 * x0) ** 2)
            np.savez(d / "D.npz", D_J=0.02 * (U @ x0), d_pairs=np.array([0.02 * (U @ x0)] * 4))
            design = {"stage1": str(STAGE1), "s5c_contract": str(S5C), "alpha_family": 0.05,
                      "lateral_endpoints": {"B": [str(d / "lat/b0.npz"), str(d / "lat/b1.npz")]},
                      "data_jitters": [str(d / f"lat/j{i}.npz") for i in range(3)], "data_central": str(d / "data.npz"),
                      "v_ensemble_glob": str(d / "v/*.npz"), "v_ensemble_n": 60,
                      "shift_coefficients": [0.0, 0.5, 1.0],
                      "process_shift": {"MnvTune_v1": {"path": str(d / "D.npz"), "sha256": sj.sha256(d / "D.npz"), "mode": "raw"},
                                        "Displaced": {"none": "test fixture"}},
                      "nulls": {"MnvTune_v1": {"prediction": str(d / "pred0.npz"), "calibration_glob": str(d / "cal_ok/*.npz"),
                                               "calibration_n": 199, "surrogate_seed0": 10},
                                "Displaced": {"prediction": str(d / "pred1.npz"), "calibration_glob": str(d / "cal_bad/*.npz"),
                                              "calibration_n": {"max": 1999, "sequential_status": str(d / "st/Displaced-final.json")},
                                              "surrogate_seed0": 20}},
                      "power": {"P": {"glob": str(d / "alt/*.npz"), "surrogate_seed0": 30}}}
            (d / "design.json").write_text(json.dumps(design))
            self.assertEqual(sj.main(["build-v", "--design", str(d / "design.json"), "--out", str(d / "V.npz")]), 0)
            args = ["--design", str(d / "design.json"), "--v", str(d / "V.npz"), "--null", "Displaced", "--status-dir", str(d / "st")]
            self.assertEqual(ss.main(args), 0)  # 0 exceedances in 199: the 99.5% upper bound 0.026 still straddles 0.005
            look = json.loads((d / "st/Displaced-B199.json").read_text())
            self.assertEqual(look["decisions"]["total"]["k"], 0)
            self.assertFalse((d / "st/Displaced-final.json").exists())
            with self.assertRaises(SystemExit):  # the evaluator refuses an unstopped sequential calibration
                sj.main(["evaluate", "--design", str(d / "design.json"), "--v", str(d / "V.npz"), "--out", str(d / "r0.json")])
            design["nulls"]["Displaced"]["calibration_n"]["max"] = 199
            (d / "design.json").write_text(json.dumps(design))
            self.assertEqual(ss.main(args), 3)
            st = json.loads((d / "st/Displaced-final.json").read_text())
            self.assertTrue(st["stop"])
            self.assertEqual(st["reason"], "maximum reached")
            self.assertEqual(sj.main(["evaluate", "--design", str(d / "design.json"), "--v", str(d / "V.npz"),
                                      "--out", str(d / "res.json")]), 0)
            res = json.loads((d / "res.json").read_text())
        ok, bad = res["tests"]["MnvTune_v1"], res["tests"]["Displaced"]
        self.assertGreater(ok["variants"]["0.0"]["total"]["p"], 0.01)
        self.assertEqual(set(ok["variants"]), {"0.0", "0.5", "1.0"})
        self.assertEqual(ok["total"]["p"], max(v["total"]["p"] for v in ok["variants"].values()))
        self.assertGreater(ok["variants"]["1.0"]["implied_size_of_unshifted_test"]["total"]["power"], 0.05)
        self.assertEqual(bad["total"]["k"], 0)
        self.assertEqual(set(bad["variants"]), {"0.0"})  # no shift declared for it
        self.assertEqual(set(res["power"]["P"]["total"]), {"0.05", str(0.05 / 4)})  # 2 nulls x 2 tests: Holm first step alpha / 4
        self.assertGreater(res["power"]["P"]["total"]["0.05"]["unshifted"]["power"], 0.9)
        # the determinacy rule: at B = 199 no rejection is determined at alpha / 4 (upper bound for k = 0 is 0.018)
        self.assertEqual(res["decisions"]["Displaced:total"]["decision"], "undetermined")
        self.assertIn(res["decisions"]["MnvTune_v1:total"]["decision"], ("undetermined", "not rejected"))
        self.assertLessEqual(res["power"]["P"]["total"]["0.05"]["claim_rule_determined"]["power"],
                             res["power"]["P"]["total"]["0.05"]["claim_rule"]["power"])
        self.assertEqual(ok["observed_jitter_p"]["total"]["n"], 3)


if __name__ == "__main__":
    unittest.main()
