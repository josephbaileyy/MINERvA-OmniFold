"""Tests of bsel_select.py (B-SEL-DECLARATION.md rev 1): the rule in each direction and on each operand, the controls'
STOPs, and an end-to-end main() on a synthetic repo. Run: python3 -B -m unittest nd-unfolding/bsel/test_bsel.py"""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bsel_select as B  # noqa: E402

N = 16


def gens(scale=0.1):
    """Generators whose pairwise S_g is known: Tune v1 = 1; genie_cv = 1, genie_mec = 1 + a, nuwro = 1 - a gives
    S_g = sqrt((a^2 + a^2 + 4a^2)/3) = a sqrt(2)."""
    one = np.ones(N)
    return {"mnvtune_v1": one.tolist(), "genie_cv": one.tolist(), "genie_mec": (one + scale).tolist(),
            "nuwro": (one - scale).tolist(), "gibuu": (one + 3 * scale).tolist()}


def inputs(beta_val=0.0, se_val=0.0):
    beta = {t: np.full(N, beta_val) for t in B.TRUTHS}
    se = {t: np.full(N, se_val) for t in B.TRUTHS}
    split = {t: np.tile(beta[t], (16, 1)) for t in B.A7}
    return beta, se, split


class Rule(unittest.TestCase):
    def test_sg_formula(self):
        S = B.sg(gens(0.1), B.PANEL)
        self.assertTrue(np.allclose(S, 0.1 * np.sqrt(2)))
        Sp = B.sg(gens(0.1), B.PANEL_PLUS, B.GIBUU_CELLS)
        self.assertEqual(int(np.sum(~np.isnan(Sp))), 8)
        self.assertTrue(np.all(np.isnan(Sp[[4, 5, 6, 7, 12, 13, 14, 15]])))

    def test_the_bound_is_inclusive_and_both_terms_count(self):
        S = 0.1 * np.sqrt(2)
        beta, se, split = inputs(0.0, 0.0)
        beta["q3"] = np.full(N, S - B.Z * 0.01)
        se["q3"] = np.full(N, 0.01)
        r = B.select(beta, se, split, gens(0.1))
        self.assertEqual(r["n_measured"], 16)  # exactly at the bound: measured (<=)
        se["q3"] = np.full(N, 0.0101)
        self.assertEqual(B.select(beta, se, split, gens(0.1))["n_measured"], 0)  # the SE term pushes it over
        se["q3"] = np.full(N, 0.01)
        beta["q3"] = -np.full(N, S - B.Z * 0.01 + 1e-6)
        self.assertEqual(B.select(beta, se, split, gens(0.1))["n_measured"], 0)  # |beta|: the sign does not help

    def test_the_worst_truth_decides(self):
        beta, se, split = inputs(0.01, 0.0)
        beta["F1_genie_v3_ar23"] = np.full(N, 0.5)
        r = B.select(beta, se, split, gens(0.1))
        self.assertEqual(r["n_measured"], 0)
        self.assertEqual(r["cells"][0]["worst_truth"], "F1_genie_v3_ar23")

    def test_a_split_flip_makes_a_cell_exploratory(self):
        beta, se, split = inputs(0.05, 0.0)  # S_g = 0.1414: measured at the means
        split["A7_gibuu"][7, 3] = 0.2  # one split of one A7 truth crosses in cell R03
        r = B.select(beta, se, split, gens(0.1))
        self.assertTrue(r["cells"][3]["measured_at_means"])
        self.assertTrue(r["cells"][3]["flips"])
        self.assertEqual(r["cells"][3]["label"], "exploratory")
        self.assertEqual(r["n_measured"], 15)

    def test_a_flip_into_measured_also_counts(self):
        beta, se, split = inputs(0.05, 0.0)
        beta["A7_nuwro"] = np.full(N, 0.3)
        split["A7_nuwro"] = np.tile(beta["A7_nuwro"], (16, 1))
        split["A7_nuwro"][2, 5] = 0.01  # replacing the worst truth with this split would make R05 measured
        r = B.select(beta, se, split, gens(0.1))
        self.assertFalse(r["cells"][5]["measured_at_means"])
        self.assertTrue(r["cells"][5]["flips"])

    def test_discrimination_flag_boundary(self):
        S = 0.1 * np.sqrt(2)
        beta, se, split = inputs(0.0, 0.0)
        beta["W1"] = np.full(N, 0.5 * S)
        r = B.select(beta, se, split, gens(0.1))
        self.assertEqual(r["n_discriminating"], 16)
        beta["W1"] = np.full(N, 0.5 * S * (1 + 1e-9))
        r = B.select(beta, se, split, gens(0.1))
        self.assertEqual((r["n_measured"], r["n_discriminating"]), (16, 0))

    def test_the_declared_constants_are_literal(self):
        self.assertEqual((B.Z, B.KAPPA, B.KAPPA_DISC), (1.96, 1.0, 0.5))

    def test_exactly_at_the_bound_is_measured(self):
        S = B.sg(gens(0.1), B.PANEL)
        beta, se, split = inputs(0.0, 0.0)
        beta["W2"] = S.copy()  # U = |beta| = S_g exactly, SE 0
        r = B.select(beta, se, split, gens(0.1))
        self.assertEqual(r["n_measured"], 16)
        self.assertTrue(all(c["measured_at_means"] for c in r["cells"]))

    def test_a_guard_of_1_96_se(self):
        S = 0.1 * np.sqrt(2)
        beta, se, split = inputs(0.0, 0.0)
        se["W2"] = np.full(N, S / 1.96 * (1 + 1e-6))  # over the bound at z = 1.96, under it at z = 1.645
        self.assertEqual(B.select(beta, se, split, gens(0.1))["n_measured"], 0)

    def test_a_flipping_cell_is_never_discriminating(self):
        beta, se, split = inputs(0.01, 0.0)  # well under 0.5 S_g: discriminating at the means
        split["A7_genie_cv"][0, 2] = 0.5
        r = B.select(beta, se, split, gens(0.1))
        self.assertTrue(r["cells"][2]["flips"])
        self.assertFalse(r["cells"][2]["discriminating"])
        self.assertEqual(r["n_discriminating"], 15)

    def test_the_split_bound_carries_the_se(self):
        S = 0.1 * np.sqrt(2)
        beta, se, split = inputs(0.0, 0.0)
        se["A7_gibuu"] = np.full(N, 0.05)  # at the means U = 0.098 < S_g
        split["A7_gibuu"][4, 6] = S - 0.05  # |split| alone is under S_g; with + 1.96 SE it crosses
        r = B.select(beta, se, split, gens(0.1))
        self.assertTrue(r["cells"][6]["flips"])

    def test_a_split_exactly_at_the_bound_does_not_flip(self):
        S = B.sg(gens(0.1), B.PANEL)
        beta, se, split = inputs(0.0, 0.0)
        split["A7_gibuu"][0] = S.copy()  # U at that split = S_g exactly: still measured under <=, so no flip
        r = B.select(beta, se, split, gens(0.1))
        self.assertFalse(any(c["flips"] for c in r["cells"]))
        self.assertEqual(r["n_measured"], 16)

    def test_zero_sg_stops(self):
        g = gens(0.0)
        beta, se, split = inputs()
        with self.assertRaises(B.Stop):
            B.select(beta, se, split, g)

    def test_assemble_units_and_the_closure_split_term(self):
        b = {t: np.full(N, 0.02) for t in B.TRUTHS}
        sig = {t: np.full(N, 0.001) for t in B.TRUTHS}
        sig["closure_nuwro"] = np.zeros(N)
        R = {t: np.full(N, 1.5) for t in B.TRUTHS}
        rng = np.random.default_rng(0)
        split_r = {t: 0.02 + rng.normal(0, 0.004, (16, N)) for t in B.A7}
        beta, se, split_beta, extra = B.assemble(b, sig, R, split_r)
        self.assertTrue(np.allclose(beta["q3"], 0.03))
        self.assertTrue(np.allclose(se["q3"], 0.0015))
        s2 = np.mean([np.var(split_r[t] * 1.5, axis=0, ddof=1) for t in B.A7], axis=0)
        self.assertTrue(np.allclose(se["closure_nuwro"], np.sqrt(s2)))
        self.assertTrue(np.allclose(split_beta["A7_gibuu"], split_r["A7_gibuu"] * 1.5))
        self.assertFalse(np.allclose(se["W1"], np.sqrt((0.0015) ** 2 + s2)))  # no split term added elsewhere

    def test_leak_check(self):
        B.leak_check({"a": [0.01, 0.2]}, [np.array([3e-39])])
        with self.assertRaises(B.Stop):
            B.leak_check({"a": [3e-39]}, [])
        with self.assertRaises(B.Stop):
            B.leak_check({"a": [0.25]}, [np.array([0.25])])


class EndToEnd(unittest.TestCase):
    """main() on a synthetic repo: committed readouts, FD-PRR's d, generators, an identity cell matrix, and six fetched
    files; the module's pins are re-pointed to the fixture's digests for the test only."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.repo, self.fetched = d / "repo", d / "fetched"
        self.fetched.mkdir()
        rng = np.random.default_rng(3)
        self.ncell_fine = N  # an identity "cell matrix": X = x
        tabs, f0b, f1 = {}, [], []
        for t in B.TRUTHS:
            if t == "closure_nuwro":
                continue
            n = 16 if t in B.A7 else 20
            r = 0.01 + rng.normal(0, 0.002, (n, N))
            rec = {"name": t, "bias": r.mean(0).tolist(),
                   "noise_sigma": np.sqrt(np.diag(np.cov(r, rowvar=False, ddof=1)) / n).tolist()}
            (f1 if t in B.F1_TRUTHS else f0b).append(rec)
            tabs[t] = r
        xt_v1 = 1e-39 * (1 + np.arange(N))
        xt_nu = xt_v1 * 1.1
        xh_nu = xt_nu * 1.004
        f0b.append({"name": "closure_nuwro", "bias": (xh_nu / xt_nu - 1).tolist(), "noise_sigma": [0.0] * N})
        np.savez(self.fetched / "fd_f0b_experiments.npz",
                 **{f"r_{t}": tabs[t] for t in B.F0B_TRUTHS if t != "closure_nuwro"},
                 **{f"seed_{t}": np.arange(970000, 970016) for t in B.A7})
        np.savez(self.fetched / "fd_f1_experiments.npz", **{f"r_{t}": tabs[t] for t in B.F1_TRUTHS})
        np.savez(self.fetched / B.TUNE_V1_CLOSURE, xtrue_flat=xt_v1, xsec_flat=xt_v1)
        np.savez(self.fetched / B.CLOSURE_OF["closure_nuwro"], xtrue_flat=xt_nu, xsec_flat=xh_nu)
        np.savez(self.fetched / B.CLOSURE_OF["F1_genie_v3_g18"], xtrue_flat=xt_v1 * 0.9, xsec_flat=xt_v1 * 0.9)
        np.savez(self.fetched / B.CLOSURE_OF["F1_genie_v3_ar23"], xtrue_flat=xt_v1 * 1.2, xsec_flat=xt_v1 * 1.2)
        prr = {"table": {f"B0/{t}/s991000": {"d": ([0.0] * N if t in B.PRIOR_TRUTHS else (0.05 * np.ones(N)).tolist())}
                         for t in B.F0B_TRUTHS if t != "closure_nuwro"}}
        files = {f"{B.FD}/with-cpl/readout/fd_f0b_readout.json": {"truths": f0b},
                 f"{B.FD}/readout/fd_f1_readout.json": {"truths": f1},
                 f"{B.FD}/receipts-prr/read/cluster/readout.json": prr,
                 f"{B.FD}/gencmp-e/rerun1/chain/chdefs/with/readout/fd_g_readout.json":
                     {"predictions": [{"name": k, "g": (np.asarray(v) * 2e-39)[list(B.GIBUU_CELLS) if k == "gibuu" else slice(None)].tolist(),
                                       "cells": [f"R{c:02d}" for c in (B.GIBUU_CELLS if k == "gibuu" else range(N))]}
                                      for k, v in gens(0.1).items()]},
                 "nd-unfolding/pv-ladder/readouts/h2_definition.json": {"identity": True}}
        for rel, obj in files.items():
            p = self.repo / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(obj))
        (self.repo / "nd-unfolding/estimator_stability_analyze.py").write_text(
            "import numpy as np\ndef cell_matrix(path):\n    return np.eye(16)\n")
        self.saved = (dict(B.COMMITTED), dict(B.FETCHED))
        B.COMMITTED.clear()
        B.COMMITTED.update({rel: B.sha256_path(self.repo / rel) for rel in files})
        B.FETCHED.clear()
        B.FETCHED.update({p.name: B.sha256_path(p) for p in self.fetched.iterdir()})
        sys.modules.pop("estimator_stability_analyze", None)

    def tearDown(self):
        B.COMMITTED.clear()
        B.COMMITTED.update(self.saved[0])
        B.FETCHED.clear()
        B.FETCHED.update(self.saved[1])
        sys.modules.pop("estimator_stability_analyze", None)
        self.tmp.cleanup()

    def run_main(self, out="out"):
        o, e = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(o), contextlib.redirect_stderr(e):
            rc = B.main(["--repo", str(self.repo), "--fetched", str(self.fetched), "--out", str(Path(self.tmp.name) / out)])
        return rc, o.getvalue(), e.getvalue()

    def test_end_to_end_writes_the_record(self):
        rc, out, err = self.run_main()
        self.assertEqual(rc, 0, err)
        self.assertEqual(json.loads(out)["verdict"], "COMPLETE")
        rec = json.loads((Path(self.tmp.name) / "out" / "selection.json").read_text())
        self.assertEqual(len(rec["cells"]), 16)
        self.assertTrue(np.allclose(rec["R"]["F1_genie_v3_g18"], 0.9))
        self.assertTrue(np.allclose(rec["R"]["closure_nuwro"], 1.1))
        self.assertTrue(np.allclose(rec["R"]["q3"], 1.05))
        self.assertEqual(rec["R"]["nominal"], [1.0] * 16)
        self.assertNotIn("e-39", json.dumps(rec))

    def test_a_wrong_pin_stops(self):
        B.FETCHED["fd_f1_experiments.npz"] = "0" * 64
        rc, _, err = self.run_main()
        self.assertEqual(rc, 5)
        self.assertIn("C-PIN", err)

    def test_a_table_that_does_not_reproduce_the_readout_stops(self):
        with np.load(self.fetched / "fd_f0b_experiments.npz") as z:
            arr = {k: np.asarray(z[k]) for k in z.files}
        arr["r_W2"] = arr["r_W2"] * (1 + 1e-9)
        np.savez(self.fetched / "fd_f0b_experiments.npz", **arr)
        B.FETCHED["fd_f0b_experiments.npz"] = B.sha256_path(self.fetched / "fd_f0b_experiments.npz")
        rc, _, err = self.run_main()
        self.assertEqual(rc, 5)
        self.assertIn("C-TAB", err)

    def test_wrong_row4_seeds_stop(self):
        with np.load(self.fetched / "fd_f0b_experiments.npz") as z:
            arr = {k: np.asarray(z[k]) for k in z.files}
        arr["seed_A7_nuwro"] = np.arange(970001, 970017)
        np.savez(self.fetched / "fd_f0b_experiments.npz", **arr)
        B.FETCHED["fd_f0b_experiments.npz"] = B.sha256_path(self.fetched / "fd_f0b_experiments.npz")
        rc, _, err = self.run_main()
        self.assertIn("C-SPLIT", err)

    def test_a_nonzero_d_at_the_prior_stops(self):
        p = self.repo / f"{B.FD}/receipts-prr/read/cluster/readout.json"
        obj = json.loads(p.read_text())
        obj["table"]["B0/A7_mnvtune/s991000"]["d"][0] = 1e-12
        p.write_text(json.dumps(obj))
        B.COMMITTED[f"{B.FD}/receipts-prr/read/cluster/readout.json"] = B.sha256_path(p)
        rc, _, err = self.run_main()
        self.assertIn("C-R", err)

    def _rewrite_json(self, rel, fn):
        p = self.repo / rel
        obj = json.loads(p.read_text())
        fn(obj)
        p.write_text(json.dumps(obj))
        B.COMMITTED[rel] = B.sha256_path(p)

    def _rewrite_npz(self, name, fn):
        p = self.fetched / name
        with np.load(p) as z:
            arr = {k: np.asarray(z[k]) for k in z.files}
        fn(arr)
        np.savez(p, **arr)
        B.FETCHED[name] = B.sha256_path(p)

    def expect(self, control):
        rc, _, err = self.run_main()
        self.assertEqual(rc, 5, err)
        self.assertIn(control, err)

    def test_a_wrong_committed_pin_stops(self):
        B.COMMITTED[f"{B.FD}/readout/fd_f1_readout.json"] = "1" * 64
        self.expect("C-PIN")

    def test_generator_shape_stops(self):
        G = f"{B.FD}/gencmp-e/rerun1/chain/chdefs/with/readout/fd_g_readout.json"
        self._rewrite_json(G, lambda o: o["predictions"][0].update(cells=["R00"]))
        self.expect("C-SG")

    def test_gibuu_on_other_cells_stops(self):
        G = f"{B.FD}/gencmp-e/rerun1/chain/chdefs/with/readout/fd_g_readout.json"
        self._rewrite_json(G, lambda o: [p.update(cells=[f"R{c:02d}" for c in range(8)]) for p in o["predictions"] if p["name"] == "gibuu"])
        self.expect("C-SG")

    def test_a_missing_truth_stops(self):
        self._rewrite_json(f"{B.FD}/readout/fd_f1_readout.json", lambda o: o["truths"].pop())
        self.expect("C-TAB")

    def test_a_nonpositive_closure_stops(self):
        self._rewrite_npz(B.TUNE_V1_CLOSURE, lambda a: a["xtrue_flat"].__setitem__(3, 0.0))
        self.expect("C-R")
        self.tearDown(); self.setUp()
        self._rewrite_npz(B.CLOSURE_OF["F1_genie_v3_ar23"], lambda a: a["xtrue_flat"].__setitem__(5, -1e-40))
        self.expect("C-R")

    def test_a_missing_prr_truth_stops(self):
        self._rewrite_json(f"{B.FD}/receipts-prr/read/cluster/readout.json", lambda o: o["table"].pop("B0/W2/s991000"))
        self.expect("C-R")

    def test_a_negative_r_stops(self):
        self._rewrite_json(f"{B.FD}/receipts-prr/read/cluster/readout.json",
                           lambda o: o["table"]["B0/q3/s991000"].update(d=[-1.5] * 16))
        self.expect("C-R")

    def test_closure_nuwro_mismatch_stops(self):
        self._rewrite_npz(B.CLOSURE_OF["closure_nuwro"], lambda a: a["xsec_flat"].__setitem__(0, a["xsec_flat"][0] * 1.01))
        self.expect("C-TAB")

    def test_a_missing_or_misshapen_table_set_stops(self):
        self._rewrite_npz("fd_f0b_experiments.npz", lambda a: a.pop("r_q3"))
        self.expect("C-TAB")
        self.tearDown(); self.setUp()
        self._rewrite_npz("fd_f1_experiments.npz", lambda a: a.__setitem__("r_F1_genie_v3_g18", a["r_F1_genie_v3_g18"][:, :8]))
        self.expect("C-TAB")

    def test_a_table_whose_noise_differs_stops(self):
        def widen(a):
            r = a["r_W1"]
            a["r_W1"] = r.mean(0) + 1.5 * (r - r.mean(0))  # the mean is kept exactly, the spread is not
        self._rewrite_npz("fd_f0b_experiments.npz", widen)
        self.expect("C-TAB")

    def test_an_existing_output_refuses(self):
        (Path(self.tmp.name) / "out").mkdir()
        rc, _, err = self.run_main()
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
