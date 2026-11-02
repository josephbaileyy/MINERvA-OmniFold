"""Controls for fd_gencmp_e2.py (FD-GENCMP-AMENDMENT-E-ADDENDUM-E2.md), on synthetic inputs. No real prediction,
covariance or data value is read; the real files read are the H2 definition and the Stage-1 receipt (geometry) and the
PV ladder's committed config (its structure).

Each control is tested in the direction it acts and in the other: V (the carbon arrays, the CH combination), the
config's repointing, R1's comparison (numbers, not paths), S's arithmetic against build_cmodel5d's own, and the chi2
rows against fd_g_compare's."""
import json
import re
import sys
import unittest
from pathlib import Path

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(1, str(ND))
sys.path.insert(1, str(ND / "pv-ladder"))
import build_cmodel5d as BC  # noqa: E402
import fd_cpl_addition as A  # noqa: E402
import fd_g_compare as fg  # noqa: E402
import fd_gencmp as gc  # noqa: E402
import fd_gencmp_e2 as E2  # noqa: E402

RNG = np.random.default_rng(20261102)
N = gc.N_FINE


def step_a(n=N):
    xc, sc = RNG.uniform(1e-42, 2e-42, n), RNG.uniform(1e-90, 2e-90, n)
    xh, sh = RNG.uniform(1e-42, 2e-42, n), RNG.uniform(1e-90, 2e-90, n)
    xch, sch = gc.combine(xc, sc, xh, sh)
    return {"xsec_C12_frozen": xc, "sumw2_C12_frozen": sc, "xsec_H": xh, "sumw2_H": sh, "xsec_CH": xch,
            "sumw2_CH": sch}


class Vertices(unittest.TestCase):
    def setUp(self):
        self.sa = step_a()
        self.carbon = {"xsec_flat": self.sa["xsec_C12_frozen"].copy(), "sumw2_flat": self.sa["sumw2_C12_frozen"].copy(),
                       "edges_pt": np.arange(3.0), "nevt_flat": np.ones(N)}

    def test_the_ch_file_keeps_the_edges_and_carries_step_as_ch_arrays(self):
        out = E2.ch_arrays(self.carbon, self.sa)
        self.assertEqual(sorted(out), ["edges_pt", "sumw2_flat", "xsec_flat"])
        self.assertTrue(np.array_equal(out["xsec_flat"], self.sa["xsec_CH"]))

    def test_a_carbon_file_other_than_step_as_refuses(self):
        self.carbon["xsec_flat"][7] *= 1 + 1e-12
        with self.assertRaises(E2.Stop):
            E2.ch_arrays(self.carbon, self.sa)

    def test_a_ch_array_other_than_the_combination_refuses(self):
        self.sa["xsec_CH"] = self.sa["xsec_CH"].copy()
        self.sa["xsec_CH"][3] *= 1 + 1e-12
        with self.assertRaises(E2.Stop):
            E2.ch_arrays(self.carbon, self.sa)


class Config(unittest.TestCase):
    def test_every_pscratch_path_is_repointed_and_the_vertices_replaced(self):
        cfg = json.loads(E2.CONFIG.read_text())
        run = Path("/r/run")
        out = E2.config_ch(cfg, run, {"nuwro": (Path("/r/run/vertices/nuwro_ch.npz"), "a" * 64),
                                       "gibuu": (Path("/r/run/vertices/gibuu_ch.npz"), "b" * 64)})
        paths = []

        def walk(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    if k == "path":
                        paths.append(v)
                    else:
                        walk(v)
        walk(out)
        self.assertFalse([p for p in paths if p.startswith(str(E2.SCRATCH))])
        self.assertEqual(out["vertices"]["nuwro"]["sha256"], "a" * 64)
        self.assertEqual(out["vertices"]["gibuu"]["pz_max"], cfg["vertices"]["gibuu"]["pz_max"])
        self.assertEqual(out["vertices"]["genie_mec"]["sha256"], cfg["vertices"]["genie_mec"]["sha256"])
        self.assertEqual(out["reference"]["sha256"], cfg["reference"]["sha256"])
        self.assertIn("CH = C12 + free proton", out["vertices"]["nuwro"]["label"])


class R1(unittest.TestCase):
    def test_the_comparison_ignores_the_paths_and_sees_every_number(self):
        old = {"r": [1.0, 1.1], "k": 0.98, "source": {"path": "/a", "sha256": "x"}, "reference": {"path": "/b"}}
        new = dict(old, source={"path": "/c", "sha256": "x"}, reference={"path": "/d"})
        self.assertEqual(A.compare_numbers(old, new, ("/source", "/reference")), [])
        self.assertTrue(A.compare_numbers(old, dict(new, r=[1.0, 1.1 + 1e-9]), ("/source", "/reference")))


class Factor(unittest.TestCase):
    def test_s_is_build_cmodel5ds_own_arithmetic(self):
        rmap, n, *_ = BC.load_definition(BC._HERE / "readouts" / "h2_definition.json",
                                         E2._REPO / "docs/orchestration/state/s5p/stage1/stage1_inspect.json", BC.EXPECT)
        xs = {k: RNG.uniform(1e-42, 2e-42, N) for k in ("tune_v1",) + BC.VERTICES}
        prod = {f"L-5D-PV_e_{k}": {"x": v} for k, v in xs.items()}
        self.assertTrue(np.array_equal(E2.factor(xs, rmap, n), BC.factor(prod, rmap, n)))

    def test_model_abs(self):
        f, S = RNG.uniform(1, 2, 16), RNG.normal(size=(3, 16))
        self.assertTrue(np.allclose(E2.model_abs(f, S), np.diag(f) @ (S.T @ S) @ np.diag(f)))


class Chi2(unittest.TestCase):
    def test_the_rows_are_fd_g_compares_chi2_on_the_readouts_g_and_vg(self):
        f = RNG.uniform(1, 2, 16)
        M = RNG.normal(size=(16, 16))
        C_rest = M @ M.T / 16 + np.eye(16)
        S = 0.05 * RNG.normal(size=(3, 16))
        g, sv = f * RNG.uniform(0.9, 1.1, 16), RNG.uniform(0.01, 0.02, 16)
        cells = list(range(16))
        readout = {"predictions": [{"name": "nuwro", "cells": [f"R{c:02d}" for c in cells], "g": g.tolist(),
                                    "sigma_Vg_over_f": sv.tolist()},
                                   {"name": "mnvtune_v1", "cells": [], "g": [], "sigma_Vg_over_f": []}]}
        rows = E2.chi2_rows(readout, f, C_rest, S)
        want = fg.compare(f, g, (sv * f) ** 2, C_rest + E2.model_abs(f, S), cells, "x")
        self.assertEqual(set(rows), {"nuwro"})
        self.assertAlmostEqual(rows["nuwro"]["total"], want["total"]["chi2"], places=10)
        self.assertAlmostEqual(rows["nuwro"]["shape_only"], want["shape_only"]["chi2"], places=10)

    def test_a_larger_model_block_lowers_the_chi2(self):
        f = np.ones(16)
        g = f * 1.05
        readout = {"predictions": [{"name": "gibuu", "cells": [f"R{c:02d}" for c in range(16)], "g": g.tolist(),
                                    "sigma_Vg_over_f": [0.01] * 16}]}
        small = E2.chi2_rows(readout, f, np.eye(16) * 1e-3, np.full((1, 16), 0.01))["gibuu"]["total"]
        big = E2.chi2_rows(readout, f, np.eye(16) * 1e-3, np.full((1, 16), 0.05))["gibuu"]["total"]
        self.assertLess(big, small)


class Pins(unittest.TestCase):
    def test_the_committed_pins_are_the_committed_bytes(self):
        self.assertEqual(E2.sha256(E2.CMODEL5), E2.CMODEL5_SHA256)
        self.assertEqual(E2.sha256(E2.DP), E2.DP_SHA256)
        self.assertEqual(E2.sha256(E2.BLOCK), E2.BLOCK_SHA256)
        for arm, h in E2.E1_SHA256.items():
            self.assertEqual(E2.sha256(E2.E1 / arm / "readout" / "fd_g_readout.json"), h)
        for name, npz in E2.CH_VERTICES.items():                          # S1: step A's products, pinned
            self.assertEqual(E2.sha256(npz), E2.STEP_A_SHA256[name])

    def test_the_gate_refuses_a_missing_receipt_and_passes_a_present_one(self):
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "R1.ok"
            with self.assertRaises(E2.Stop):
                E2.gate(p, "R1")
            p.write_text("R1 passed\n")
            E2.gate(p, "R1")

    def test_the_corner_is_the_four_predictions_without_the_prior(self):
        self.assertEqual(E2.CORNER, ("genie_cv", "genie_mec", "nuwro", "gibuu"))

    def test_the_inputs_file_pins_what_the_steps_stage(self):
        pins = {Path(p).relative_to(E2.SCRATCH).as_posix() for p in gc.load_pins(E2.INPUTS)}
        cfg = json.loads(E2.CONFIG.read_text())
        want = {Path(cfg["rungs"][E2.RUNG][k]["path"]).relative_to(E2.SCRATCH).as_posix() for k in ("npz", "bkg")}
        want |= {f"{E2.PREP}/{n}.json" for n in E2.RATIO_FILES}
        want |= {f"{E2.PRODUCTS}/L-5D-PV_e_{v}.npz" for v in ("tune_v1",) + BC.VERTICES}
        self.assertTrue(want <= pins, sorted(want - pins))


JOB = E2.FD / "fd/gencmp-e2/receipts/x_e2_unfold.sh"


class NoiseFloor(unittest.TestCase):
    """The director's E2 ruling: the seed-43 carbon pair, its check_meta at seed 43, and the reading fixed in advance."""

    def test_the_job_launches_exactly_the_declared_unfolds_with_their_seeds(self):
        txt = JOB.read_text()
        tasks = dict(m.groups()[:2] for m in re.finditer(r'"(\w+):(\d+):([^"]+)"', txt))
        self.assertEqual(set(tasks), set(E2.UNFOLDS))
        self.assertEqual({k for k, v in tasks.items() if v == str(E2.NOISE_SEED)}, set(E2.NOISE.values()))
        self.assertEqual({k for k, v in tasks.items() if v == "42"}, set(E2.UNFOLDS) - set(E2.NOISE.values()))
        self.assertIn(f"NT={len(E2.UNFOLDS)};", txt)
        self.assertIn("--estimator-seed \"$SEED\"", txt)
        self.assertIn("#SBATCH -t 00:25:00", txt)

    def test_the_noise_pair_uses_the_committed_prep_ratios(self):
        txt = JOB.read_text()
        for v, k in E2.NOISE.items():
            self.assertIn(f'"{k}:{E2.NOISE_SEED}:$P/{v}.json"', txt)
        self.assertIn('P="$R/inputs/pv-ladder-20261024/prep/ratios/L-5D-PV"', txt)

    def meta(self, PA, vertex, seed):
        cfg = json.loads(E2.CONFIG.read_text())["rungs"][E2.RUNG]
        task = PA.tasks(E2.PVL / "tasks.tsv")[f"L-5D-PV_e_{vertex}"]
        axes = PA.L.RUNGS[task["rung"]][0]
        m = {"rung": task["rung"], "arm": "e", "closure": False, "input_npz_sha256": cfg["npz"]["sha256"],
             "bkg_dump_sha256": cfg["bkg"]["sha256"], "ratio_sha256": "r" * 64, "features": list(axes),
             "estimator_seed": seed, "iters": 5, "threads": 32,
             "refinement": {"ran": True, "classifier_params": dict(PA.REFINE, random_state=seed + 3)},
             "completeness_guard": {"r_spread_in_cell": 0.0, "completeness": 0.0},
             "code_sha256": {"a.py": "x"}, "estimator_params": [{"random_state": seed, "num_threads": 32}]}
        return task, cfg, {"vertices": {vertex: {"ratio_sha256": "r" * 64}}}, m

    def test_check_meta_at_seed_43_accepts_a_seed_43_product_and_refuses_a_seed_42_one(self):
        import pvl_analyze as PA
        task, cfg, ratios, m43 = self.meta(PA, "gibuu", 43)
        _, _, _, m42 = self.meta(PA, "gibuu", 42)
        with E2.declared_seed(PA, 43):
            PA.check_meta("x43", m43, task, ratios, cfg, None)
            with self.assertRaises(SystemExit):
                PA.check_meta("x42", m42, task, ratios, cfg, None)
            with self.assertRaises(SystemExit):     # the refinement at seed 42's random_state
                PA.check_meta("x", dict(m43, refinement={"ran": True, "classifier_params": dict(PA.REFINE, random_state=45)}),
                              task, ratios, cfg, None)
        PA.check_meta("x42", m42, task, ratios, cfg, None)
        with self.assertRaises(SystemExit):
            PA.check_meta("x43", m43, task, ratios, cfg, None)

    def test_declared_seed_restores_the_module_even_on_a_refusal(self):
        import pvl_analyze as PA
        before = (dict(PA.DECLARED), dict(PA.REFINE))
        with self.assertRaises(RuntimeError):
            with E2.declared_seed(PA, 43):
                self.assertEqual((PA.DECLARED["estimator_seed"], PA.REFINE["random_state"]), (43, 46))
                raise RuntimeError
        self.assertEqual((PA.DECLARED, PA.REFINE), before)

    def test_estimator_parameters_compare_but_for_random_state(self):
        a = [{"random_state": 42, "n": 1}, {"random_state": 42, "n": 2}]
        b = [{"random_state": 43, "n": 1}, {"random_state": 43, "n": 2}]
        self.assertEqual(E2.params_but_seed(b, 43), E2.params_but_seed(a, 42))
        self.assertNotEqual(E2.params_but_seed([dict(b[0], n=9), b[1]], 43), E2.params_but_seed(a, 42))
        with self.assertRaises(SystemExit):
            E2.params_but_seed([b[0], dict(b[1], random_state=42)], 43)

    def test_the_reading_is_fixed_by_twice_the_noise_floor(self):
        self.assertTrue(E2.reading(1.0, 0.5)["within_seed_variation"])
        self.assertFalse(E2.reading(1.0 + 1e-12, 0.5)["within_seed_variation"])
        self.assertFalse(E2.reading(0.1, 0.0)["within_seed_variation"])
        r = E2.reading(0.4, 0.3)
        self.assertTrue(r["sentence"].endswith("against a seed-to-seed change of 0.30; within the estimator's seed "
                                               "variation"))
        self.assertNotIn("within", E2.reading(3.0, 0.3)["sentence"])


if __name__ == "__main__":
    unittest.main()
