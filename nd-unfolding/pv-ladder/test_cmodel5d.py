"""Tests for build_cmodel5d on a synthetic product tree (numpy only): `python3 -m unittest test_cmodel5d -v` here.

No test reads an unfold product: the six L-5D-PV products and P5 are written by the fixture into a temporary directory,
with metas that pass the ladder's provenance check. The committed definition, Stage-1 receipt, config, tasks and
prep-SHA256SUMS are read as they are (none is a data product). Every guard has a case where it fires and one where it
stays silent."""
import argparse
import copy
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import numpy as np

import build_cmodel5d as B
import pvl_lib as L

HERE = Path(__file__).resolve().parent
NFINE = int(np.prod([len(L.FINE[a]) - 1 for a in L.AXES5]))


def sha(p):
    return L.sha256_path(p)


class Tree:
    """A synthetic tree: the prior x0, vertex unfolds x0 (1 + e_k) on each fine cell, a NuWro closure whose bias per
    base H2 cell is b_c, and the NuWro data shift set to `shift_of(b)`."""

    def __init__(self, root, b_scale=0.03, shift_of=lambda b: -b, seed=5):
        self.root = Path(root)
        (self.root / "products").mkdir(parents=True)
        rng = np.random.default_rng(seed)
        rmap, n, _, base_map, _ = B.load_definition(HERE / "readouts" / "h2_definition.json",
                                                    B._ROOT / "docs/orchestration/state/s5p/stage1/stage1_inspect.json",
                                                    B.EXPECT)
        self.rmap, self.n, self.base_map = rmap, n, base_map
        x0 = rng.uniform(0.5, 1.5, NFINE)
        b27 = b_scale * np.where(np.arange(27) % 2 == 0, 1.0, -1.0) * rng.uniform(0.6, 1.4, 27)
        b = np.where(base_map >= 0, b27[np.maximum(base_map, 0)], 0.0)
        cfg, T, ratios = B.provenance_refs(HERE / "config.json", HERE / "tasks.tsv", HERE / "prep-SHA256SUMS")
        self.expect = copy.deepcopy(B.EXPECT)
        xs = {"L-5D-PV_e_tune_v1": x0, "L-5D-PV_e_genie_mec": x0 * (1 + rng.normal(0, 0.03, NFINE)),
              "L-5D-PV_e_nuwro": x0 * (1 + shift_of(b)), "L-5D-PV_e_gibuu": x0 * (1 + rng.normal(0, 0.1, NFINE))}
        for name, x in xs.items():
            self.write(name, x, None, cfg, T, ratios)
        self.write("L-5D-PV_e_closure_nuwro", x0 * (1 + b), x0, cfg, T, ratios)
        self.write("L-5D-PV_e_closure_tune_v1", x0 * (1 + 1e-6), x0, cfg, T, ratios)
        self.p5 = self.root / "p5.npz"
        np.savez(self.p5, xsec_flat=x0)
        self.expect["p5"] = sha(self.p5)
        self.cfg, self.T, self.ratios = cfg, T, ratios

    def meta(self, name, cfg, T, ratios):
        t = T[name]
        data = t["mode"] == "data"
        return {"rung": "L-5D-PV", "arm": "e", "closure": not data, "input_npz_sha256": cfg["npz"]["sha256"],
                "bkg_dump_sha256": cfg["bkg"]["sha256"], "ratio_sha256": ratios["vertices"][t["vertex"]]["ratio_sha256"],
                "features": list(L.AXES5), "estimator_seed": 42, "iters": 5, "threads": 32,
                "refinement": ({"ran": True, "classifier_params": dict(B.A.REFINE)} if data else {"ran": False}),
                "completeness_guard": ({"r_spread_in_cell": 0.0, "completeness": 0.0} if data else None),
                "code_sha256": {"synthetic": "1"}, "estimator_params": [{"synthetic": 1}]}

    def write(self, name, x, xtrue, cfg, T, ratios, meta=None):
        p = self.root / "products" / f"{name}.npz"
        arrays = {"xsec_flat": np.asarray(x, float), "shape": np.array([NFINE])}
        if xtrue is not None:
            arrays["xtrue_flat"] = np.asarray(xtrue, float)
        np.savez(p, **arrays, meta=json.dumps(meta or self.meta(name, cfg, T, ratios)))
        self.expect["products"][name] = sha(p)

    def args(self, out="out.json", npz=None):
        return argparse.Namespace(products=self.root / "products", p5=self.p5,
                                  definition=HERE / "readouts" / "h2_definition.json",
                                  stage1=B._ROOT / "docs/orchestration/state/s5p/stage1/stage1_inspect.json",
                                  config=HERE / "config.json", tasks=HERE / "tasks.tsv", prep_sums=HERE / "prep-SHA256SUMS",
                                  out_json=self.root / out, out_npz=(self.root / npz) if npz else None)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.t = Tree(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def fires(self, msg, expect=None, args=None):
        with self.assertRaises(SystemExit) as cm:
            B.build(args or self.t.args(), expect or self.t.expect)
        self.assertIn(msg, str(cm.exception))
        self.assertFalse((self.t.root / "out.json").exists(), "a refused build wrote its output")


class Build(Base):
    def test_silent_end_to_end(self):
        out = B.build(self.t.args(npz="c.npz"), self.t.expect)
        S = np.asarray(out["S"])
        self.assertEqual(S.shape, (3, 16))
        z = np.load(self.t.root / "c.npz")
        np.testing.assert_allclose(z["C_model"], S.T @ S, rtol=1e-12, atol=0)
        np.testing.assert_array_equal(z["C_abs"], z["C_model"] * np.outer(z["x"], z["x"]))
        self.assertEqual(B.B2.matrix_sha256(z["C_model"]), out["matrix_sha256"]["C_model"])
        self.assertAlmostEqual(sum(out["trace_share_by_vertex"].values()), 1.0, places=12)
        self.assertTrue(out["nominal_control"]["a_full_grid_bitwise"])
        self.assertEqual(set(out["labels"]), {"component", "coverage", "gibuu", "step_adjacent", "positive_control"})
        self.assertEqual(out["rank"], 3)

    def test_x_is_p5_on_the_reporting_cells(self):
        out = B.build(self.t.args(), self.t.expect)
        p5 = np.load(self.t.p5)["xsec_flat"]
        np.testing.assert_array_equal(np.asarray(out["x"]), B.integrals(p5, self.t.rmap, self.t.n))

    def test_refuses_to_overwrite(self):
        (self.t.root / "out.json").write_text("{}")
        with self.assertRaises(SystemExit) as cm:
            B.build(self.t.args(), self.t.expect)
        self.assertIn("refusing to overwrite", str(cm.exception))
        self.assertEqual((self.t.root / "out.json").read_text(), "{}")


class Digests(Base):
    def test_definition_digest(self):
        e = copy.deepcopy(self.t.expect)
        e["definition"] = "0" * 64
        self.fires("not the approved definition", e)

    def test_fine_map_digest(self):
        e = copy.deepcopy(self.t.expect)
        e["fine_map"] = "0" * 64
        self.fires("fine map", e)

    def test_tampered_definition_with_its_own_sha(self):
        """A definition edited consistently (its file digest updated) still fails on the fine map."""
        D = json.loads((HERE / "readouts" / "h2_definition.json").read_text())
        D["h2_to_reporting_cell"][0], D["h2_to_reporting_cell"][1] = D["h2_to_reporting_cell"][1], 3
        p = self.t.root / "def.json"
        p.write_text(json.dumps(D))
        e = copy.deepcopy(self.t.expect)
        e["definition"] = sha(p)
        a = self.t.args()
        a.definition = p
        self.fires("fine map", e, a)

    def test_stage1_digest(self):
        e = copy.deepcopy(self.t.expect)
        e["stage1"] = "0" * 64
        self.fires("Stage-1 receipt", e)

    def test_product_digest(self):
        e = copy.deepcopy(self.t.expect)
        e["products"]["L-5D-PV_e_gibuu"] = "0" * 64
        self.fires("L-5D-PV_e_gibuu.npz: sha256", e)

    def test_p5_digest(self):
        e = copy.deepcopy(self.t.expect)
        e["p5"] = "0" * 64
        self.fires("P5", e)

    def test_silent_on_the_declared_digests(self):
        self.assertTrue(B.build(self.t.args(), self.t.expect)["nominal_control"]["b_cells_bitwise"])


class Provenance(Base):
    def test_wrong_rung_fires(self):
        m = self.t.meta("L-5D-PV_e_nuwro", self.t.cfg, self.t.T, self.t.ratios)
        m["rung"] = "L-4D"
        z = np.load(self.t.root / "products" / "L-5D-PV_e_nuwro.npz")
        self.t.write("L-5D-PV_e_nuwro", z["xsec_flat"], None, self.t.cfg, self.t.T, self.t.ratios, meta=m)
        self.fires("rung")

    def test_wrong_ratio_fires(self):
        m = self.t.meta("L-5D-PV_e_gibuu", self.t.cfg, self.t.T, self.t.ratios)
        m["ratio_sha256"] = self.t.ratios["vertices"]["nuwro"]["ratio_sha256"]
        z = np.load(self.t.root / "products" / "L-5D-PV_e_gibuu.npz")
        self.t.write("L-5D-PV_e_gibuu", z["xsec_flat"], None, self.t.cfg, self.t.T, self.t.ratios, meta=m)
        self.fires("ratio_sha256")

    def test_different_code_fires(self):
        m = self.t.meta("L-5D-PV_e_gibuu", self.t.cfg, self.t.T, self.t.ratios)
        m["code_sha256"] = {"synthetic": "2"}
        z = np.load(self.t.root / "products" / "L-5D-PV_e_gibuu.npz")
        self.t.write("L-5D-PV_e_gibuu", z["xsec_flat"], None, self.t.cfg, self.t.T, self.t.ratios, meta=m)
        self.fires("code_sha256")

    def test_silent_on_declared_provenance(self):
        cfg, T, ratios = self.t.cfg, self.t.T, self.t.ratios
        self.assertEqual(len(B.load_products(self.t.root / "products", self.t.expect, cfg, T, ratios)), 6)


class NominalControl(Base):
    def test_one_fine_cell_differs_fires(self):
        p5 = np.load(self.t.p5)["xsec_flat"].copy()
        p5[12345] *= 1 + 1e-12
        np.savez(self.t.p5, xsec_flat=p5)
        self.t.expect["p5"] = sha(self.t.p5)
        self.fires("'a_full_grid_bitwise': False")

    def test_integration_routes_disagree_fires(self):
        orig = B.integrals_s5p
        B.integrals_s5p = lambda x, cmap, n: orig(x, cmap, n) * (1 + 1e-15)
        try:
            self.fires("'c_integration_routes_bitwise': False")
        finally:
            B.integrals_s5p = orig

    def test_silent_when_bitwise(self):
        x0 = np.load(self.t.p5)["xsec_flat"]
        rec, _ = B.nominal_control(x0, x0.copy(), self.t.rmap, self.t.n)
        self.assertTrue(all(rec[k] for k in ("a_full_grid_bitwise", "b_cells_bitwise", "c_integration_routes_bitwise")))

    def test_empty_nominal_cell_fires(self):
        with self.assertRaises(ValueError):
            B.P.rel_shift(np.ones(3), np.array([1.0, 0.0, 1.0]))


class Factor(unittest.TestCase):
    def setUp(self):
        self.S = np.random.default_rng(2).normal(0, 0.05, (3, 16))

    def test_perturbed_matrix_fires(self):
        C = B.B2.cmodel(self.S)
        C[3, 4] *= 1 + 1e-9
        with self.assertRaises(SystemExit) as cm:
            B.check_factor(self.S, C)
        self.assertIn("not S^T S", str(cm.exception))

    def test_silent_on_s_transpose_s(self):
        np.testing.assert_array_equal(B.check_factor(self.S, B.B2.cmodel(self.S)), np.abs(self.S).max(axis=0))


class PositiveControl(unittest.TestCase):
    def run_tree(self, **kw):
        tmp = tempfile.mkdtemp()
        try:
            t = Tree(tmp, **kw)
            return B.build(t.args(), t.expect)["positive_control"]
        finally:
            shutil.rmtree(tmp)

    def test_pass_on_27_and_16_labelled_not_powered(self):
        pc = self.run_tree()
        self.assertEqual(pc["graded"], "base27")
        self.assertEqual(pc["verdict"], "PASS")
        self.assertEqual(pc["base27"]["n_cells"], 27)
        self.assertTrue(pc["reporting16"]["label"].startswith("not powered"))
        self.assertLess(pc["base27"]["closure_floor_max_abs"], 1e-5)

    def test_fail_labels_not_evidence(self):
        pc = self.run_tree(shift_of=lambda b: np.abs(b))
        self.assertEqual(pc["verdict"], "FAIL")
        self.assertIn("not evidence", pc["label"])
        self.assertTrue(pc["reporting16"]["label"].startswith("not powered"))

    def test_not_powered_labels_not_evidence(self):
        pc = self.run_tree(b_scale=0.005)
        self.assertEqual(pc["verdict"], "NOT_POWERED")
        self.assertIn("not evidence", pc["label"])


if __name__ == "__main__":
    unittest.main()
