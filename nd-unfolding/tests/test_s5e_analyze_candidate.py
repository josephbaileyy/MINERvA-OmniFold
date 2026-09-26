"""End-to-end control for the s5e candidate receipt on synthetic products (no LightGBM or ROOT).

The receipt reads its thresholds from the frozen amendment; on synthetic experiments with known noise it
must pass the C3 criterion when the candidate is unbiased and fail it when a bias is planted, and the
assessment stage must build every criterion (A1-A5) and a verdict."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ND = Path(__file__).resolve().parents[1]
REPO = ND.parent
sys.path.insert(1, str(ND))
import s5c_coverage as sc  # noqa: E402
import s5e_analyze_candidate as ac  # noqa: E402

AMEND = REPO / "docs/orchestration/state/s5e/contract-amendment-3-candidate-R-and-assessment.json"
S5C = REPO / "docs/orchestration/state/s5c/contract.json"
ADOPTED = REPO / "docs/orchestration/state/s5c/d1/bias_vs_adopted.json"


class Synthetic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        U, _ = sc.reported_functionals(json.loads(S5C.read_text()))
        cls.ew = np.argmax(U[:42], axis=0)  # the (E_avail,W) cell of each 5D cell
        cls.xt = np.ones(U.shape[1])

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="s5e-cand-"))
        self.rng = np.random.default_rng(0)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def product(self, path: Path, bias=0.0, sd=0.002, truth=True):
        path.parent.mkdir(parents=True, exist_ok=True)
        eps = self.rng.normal(0, sd, 42)[self.ew] + bias
        arrays = {"xsec_flat": self.xt * (1 + eps)}
        if truth:
            arrays["xtrue_flat"] = self.xt
        np.savez_compressed(path, **arrays, meta=json.dumps({}))

    def tree(self, k1_bias=0.0, assessment=False):
        d = self.tmp / "ns/runs/cand/dev"
        for b in range(1, 101):
            self.product(d / "sigma" / f"boot_b{b}.npz", truth=False)
        for i in range(20):  # the frozen K1 size (the C3 threshold assumes n >= 20)
            self.product(d / "k1_R" / f"nominal_a0_s{700000 + i}.npz", bias=k1_bias)
            self.product(d / "k1_B0" / f"nominal_a0_s{700000 + i}.npz", bias=0.004)
        for i in range(8):
            self.product(d / "k2" / f"eavail_shape_a1_s{701000 + i}.npz", bias=0.05)
            self.product(d / "k3" / f"q3_given_eavail_w_a0.3_s{702000 + i}.npz", bias=0.02)
        for nm in ("k4_base", "k4_seed43", "k4_perm1", "k4_perm2"):
            self.product(d / "k4" / f"{nm}.npz", sd=0.0)
        s5n = self.tmp / "s5n"
        for i in range(8):
            self.product(s5n / "dev" / f"eavail_shape_a1_s{301000 + i}.npz", bias=0.05)
            self.product(s5n / "dev" / f"q3_given_eavail_w_a0.3_s{302000 + i}.npz", bias=0.02)
        for b in range(1, 201):
            self.product(s5n / "sigma" / f"boot_b{b}.npz", truth=False)
        if assessment:
            A = self.tmp / "ns/runs/cand/assess"
            for key, bias in (("nominal", 0.0), ("eavail_gibuu", 0.05), ("q3", 0.02), ("W1", 0.01), ("W2", 0.001), ("W3", 0.02)):
                for i in range(8):
                    self.product(A / key / f"x_s{i}.npz", bias=bias)
            for nm in ("a3_base", "a3_seed43", "a3_perm1", "a3_perm2"):
                self.product(A / "a3" / f"{nm}.npz", sd=0.0)
            for nm in ("data_R", "data_R_upcast", "data_R_jitteredge1", "data_R_jitteredge2"):
                self.product(A / "data" / f"{nm}.npz", sd=0.0, truth=False)
            for b in range(1, 51):
                self.product(A / "data" / "boot" / f"boot_b{b}.npz", truth=False)
            self.product(self.tmp / "ns/runs/diag/drv/data_b0.npz", sd=0.0, bias=0.001, truth=False)
        return s5n

    def run_stage(self, stage, s5n):
        out = self.tmp / f"{stage}.json"
        ac.main(["--amendment", str(AMEND), "--s5c-contract", str(S5C), "--adopted-sigma", str(ADOPTED),
                 "--ns", str(self.tmp / "ns"), "--s5n-runs", str(s5n), "--stage", stage, "--out", str(out)])
        return json.loads(out.read_text())

    def test_unbiased_candidate_passes_c3_and_planted_bias_fails(self):
        s5n = self.tree(k1_bias=0.0)
        r = self.run_stage("development", s5n)
        self.assertTrue(r["K1"]["criterion"]["pass"])
        self.assertFalse(r["K1"]["B0_criterion"]["pass"])  # the planted 0.4% B0 bias is caught
        self.assertTrue(r["K4"]["pass"])
        self.assertTrue(r["K2_K3"]["K2"]["pass_not_worse"])
        shutil.rmtree(self.tmp / "ns")
        s5n = self.tree(k1_bias=0.004)
        r = self.run_stage("development", s5n)
        self.assertFalse(r["K1"]["criterion"]["pass"])
        self.assertFalse(r["development_exit"])

    def test_assessment_builds_every_criterion_and_a_verdict(self):
        s5n = self.tree(assessment=True)
        r = self.run_stage("assessment", s5n)
        for k in ("A1", "A2", "A3", "A4", "A5"):
            self.assertIn(k, r)
        self.assertTrue(r["data_upcast_equals_data_R"])
        self.assertIn(r["verdict"], ("A_PASS_DEVELOPMENT_SCALE", "A_FAIL"))
        self.assertIn("EW0", r["A4"]["cells_model_dependence_within_adopted_sigma"])  # W1-W3 <= 2% < adopted sigma of EW0 (3.0%)
        import s5e_next_design as nd
        out = self.tmp / "design.json"
        nd.main(["--assessment", str(self.tmp / "assessment.json"), "--adopted-sigma", str(ADOPTED),
                 "--cost-pseudo", "0.0115", "--cost-data", "0.025", "--out", str(out)])
        d = json.loads(out.read_text())
        g = d["A_statistical_scope_coverage"]["all_42_EW_cells"]["68_nominal_only"]
        self.assertEqual(g["m"], 42)
        self.assertGreater(g["n_for_80pct_assurance_exactly_nominal"], 1000)  # exact nominal coverage needs thousands
        self.assertGreater(d["B_model_dependence"]["cost_cpu_node_h"], 0)


if __name__ == "__main__":
    unittest.main()
