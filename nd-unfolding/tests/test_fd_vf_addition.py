"""Tests of fd_vf_addition.py (FD-VF-ADDITION-DECLARATION.md): each control is shown to fire on the defect it guards
and to stay silent on the good case; the chain's argv, blocks and names per arm; and the order that keeps every V_F
step behind the OLD arms' controls."""
from __future__ import annotations

import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ND))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fd_cpl_addition as A  # noqa: E402
import fd_deposit_candidate as DC  # noqa: E402
import fd_vf_addition as V  # noqa: E402
from test_fd_g_compare import digest  # noqa: E402

REPO = ND.parent
FDP = REPO / V.FD


def quiet():
    return mock.patch("sys.stdout")


def inputs():
    with quiet():
        return V.block_inputs(REPO)


def built(*args):
    with quiet():
        return V.build_block(*args)


# ------------------------------------------------------------------------------------------------ the block

class Block(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="vf-block-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def run_block(self, out):
        a = V.build_args(["block", "--repo", str(REPO), "--out-dir", str(out)])
        with quiet(), mock.patch("sys.stderr"):
            return V.run(a)

    def test_the_block_is_the_pinned_bytes_and_written_as_declared(self):
        self.assertEqual(self.run_block(self.tmp / "b"), 0)
        self.assertEqual(digest(self.tmp / "b/vf_block.npz"), V.VF_BLOCK_NPZ)
        z = A.load_npz(self.tmp / "b/vf_block.npz")
        self.assertEqual(list(z), ["f", "C_e", "V_F", "dF", "C_resp_plus_dF", "C_resp_plus_C_PL5D_plus_dF",
                                   V.WITHOUT_F, V.REPORTED_F])
        self.assertTrue(np.array_equal(z["dF"], z["V_F"] - z["C_e"]))
        cpl = A.load_npz(FDP / "fd/with-cpl/block/cpl_block.npz")
        self.assertTrue(np.array_equal(z["C_resp_plus_C_PL5D_plus_dF"], cpl[A.XKEY] + z["dF"]))
        self.assertTrue(np.array_equal(z["C_resp_plus_dF"], cpl["C_resp"] + z["dF"]))
        js = json.loads((self.tmp / "b/vf_block.json").read_text())
        self.assertEqual(js["npz"]["sha256"], V.VF_BLOCK_NPZ)
        self.assertEqual(js["inputs_sha256"], V.PINS)
        self.assertEqual([b["name"] for b in js["npz"]["extra_blocks"]], ["dF", "C_resp + dF", "C_resp + C_PL5D + dF"])

    def test_the_committed_block_is_the_pinned_bytes(self):
        p = FDP / "fd/with-vf/block/vf_block.npz"
        if not p.exists():
            self.skipTest("the block is committed with the code")
        self.assertEqual(digest(p), V.VF_BLOCK_NPZ)

    def test_an_existing_output_refuses(self):
        (self.tmp / "b").mkdir()
        (self.tmp / "b/vf_block.json").write_text("{}")
        self.assertEqual(self.run_block(self.tmp / "b"), 1)

    def test_an_input_that_is_not_its_pin_refuses_v0(self):
        with mock.patch.dict(V.PINS, {"v_f_csv": "0" * 64}):
            self.assertEqual(self.run_block(self.tmp / "b"), 1)
        self.assertFalse((self.tmp / "b/vf_block.npz").exists())

    def test_a_c_e_that_is_not_the_products_refuses_v1(self):
        VF, L, Ce, dp, cpl = inputs()
        Ce2 = Ce.copy()
        Ce2[0, 0] *= 1 + 1e-15
        with self.assertRaises(V.Stop) as cm:
            built(VF, L, Ce2, dp, cpl)
        self.assertEqual(cm.exception.control, "V1")

    def test_a_cpl_block_whose_c_pl5d_is_not_the_products_refuses_v1(self):
        VF, L, Ce, dp, cpl = inputs()
        cpl = dict(cpl, C_PL5D=cpl["C_PL5D"] * 1.0000001)
        with self.assertRaises(V.Stop) as cm:
            built(VF, L, Ce, dp, cpl)
        self.assertEqual(cm.exception.control, "V1")

    def test_a_v_f_that_is_not_l_c_e_l_refuses_v2(self):
        VF, L, Ce, dp, cpl = inputs()
        with self.assertRaises(V.Stop) as cm:
            built(VF * (1 + 1e-9), L, Ce, dp, cpl)
        self.assertEqual(cm.exception.control, "V2")

    def test_an_asymmetric_l_refuses_v2(self):
        VF, L, Ce, dp, cpl = inputs()
        L2 = L.copy()
        L2[0, 1] += 1e-6
        with self.assertRaises(V.Stop) as cm:
            built(VF, L2, Ce, dp, cpl)
        self.assertEqual(cm.exception.control, "V2")

    def test_an_l_that_does_not_commute_with_c_e_refuses_v2(self):
        VF, L, Ce, dp, cpl = inputs()
        R = np.eye(16)
        R[0, 1] = R[1, 0] = 0.3                                # symmetric, but not a function of C_e
        L2 = L @ R + R @ L
        with self.assertRaises(V.Stop) as cm:
            built(L2 @ Ce @ L2.T, L2, Ce, dp, cpl)
        self.assertEqual(cm.exception.control, "V2")

    def test_a_df_that_is_not_psd_refuses_v3(self):
        VF, L, Ce, dp, cpl = inputs()
        Ls = 0.9 * np.eye(16)                                   # V_F = 0.81 C_e: dF negative definite
        with self.assertRaises(V.Stop) as cm:
            built(Ls @ Ce @ Ls.T, Ls, Ce, dp, cpl)
        self.assertEqual(cm.exception.control, "V3")

    def test_the_identity_l_gives_a_zero_df_and_the_committed_matrices(self):
        VF, L, Ce, dp, cpl = inputs()
        z = built(Ce.copy(), np.eye(16), Ce, dp, cpl)
        self.assertEqual(float(np.abs(z["dF"]).max()), 0.0)
        self.assertTrue(np.array_equal(z[V.REPORTED_F], np.array(dp["matrices"][A.REPORTED])))


# ------------------------------------------------------------------------------------------------ the product

class ProductTree:
    """The committed product, a built vf_block, and a Stage G readout made consistent with C_rep,F."""

    def __init__(self, root: Path):
        self.root = root
        a = V.build_args(["block", "--repo", str(REPO), "--out-dir", str(root / "block")])
        with quiet():
            assert V.run(a) == 0
        self.npz, self.bj = root / "block/vf_block.npz", root / "block/vf_block.json"
        self.dp = FDP / "fd/with-cpl/data-product/fd_data_product_cpl.json"
        self.g = root / "g.json"
        self.write_g()

    def write_g(self, mutate=None):
        blk = A.load_npz(self.npz)
        sig = np.sqrt(np.diag(blk[V.REPORTED_F])) / blk["f"]
        g = json.loads((FDP / "fd/with-cpl/readout/fd_g_readout.json").read_text())
        g["extra_block"] = {**g["extra_block"], "sha256": digest(self.npz), "key": V.SIDE_KEY["with"],
                            "name": V.BLOCKS[V.SIDE_KEY["with"]], "role": "adopted"}
        import fd_g_compare as G
        f = blk["f"]
        for p in g["predictions"]:
            idx = [V.CELLS.index(c) for c in p["cells"]]
            gv, Vg = np.zeros(16), np.zeros(16)
            gv[idx] = p["g"]
            Vg[idx] = (np.array(p["sigma_Vg_over_f"]) * f[idx]) ** 2
            out = G.compare(f, gv, Vg, blk[V.REPORTED_F], idx, V.REPORTED_NAME)
            for k in ("total", "shape_only"):
                p[k] = {**p[k], **{q: out[k][q] for q in ("chi2", "p", "matrix")}}
            p["sigma_total_over_f"] = sig[idx].tolist()
            p["reported_covariance"] = V.REPORTED_NAME
        if mutate:
            mutate(g)
        self.g.write_text(json.dumps(g))

    def pins(self):
        return {"data_product": digest(self.dp), "block_npz": digest(self.npz), "block_json": digest(self.bj),
                "g_readout": digest(self.g)}

    def product(self, out, pins="default", npz=None):
        a = V.build_args(["product", "--data-product", str(self.dp), "--block-npz", str(npz or self.npz),
                          "--block-json", str(self.bj), "--g-readout", str(self.g), "--out-dir", str(out)])
        with quiet(), mock.patch("sys.stderr"):
            return V.run(a, pins=self.pins() if pins == "default" else pins)


class Product(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="vf-prod-"))
        cls.t = ProductTree(cls.tmp / "t")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def tearDown(self):
        self.t.write_g()

    def test_the_product_carries_both_revised_matrices_and_reads_back(self):
        out = self.tmp / "p-ok"
        self.assertEqual(self.t.product(out), 0)
        js = json.loads((out / f"{V.PRODUCT_STEM}.json").read_text())
        self.assertEqual(list(js["matrices"]), list(V.PRODUCT_MATRICES))
        self.assertEqual(js["correlation_of"], V.REPORTED_F)
        blk = A.load_npz(self.t.npz)
        self.assertTrue(np.array_equal(np.array(js["matrices"][V.REPORTED_F]), blk[V.REPORTED_F]))
        dp = json.loads(self.t.dp.read_text())
        for k in ("C_e", "C_model_abs", "C_resp", "C_PL5D"):
            self.assertTrue(np.array_equal(np.array(js["matrices"][k]), np.array(dp["matrices"][k])), k)
        self.assertEqual(sorted(p.name for p in out.iterdir()), sorted(V.product_names()))

    def test_without_the_chains_pins_it_refuses(self):
        self.assertEqual(self.t.product(self.tmp / "p-nopins", pins=None), 1)

    def test_another_committed_product_refuses_k0(self):
        pins = {**self.t.pins(), "data_product": "0" * 64}
        self.assertEqual(self.t.product(self.tmp / "p-k0", pins=pins), 1)

    def test_a_stage_g_on_the_old_block_name_refuses_k1(self):
        self.t.write_g(lambda g: g["extra_block"].update(name=A.NAME))
        self.assertEqual(self.t.product(self.tmp / "p-k1"), 1)

    def test_a_stage_g_on_the_nopl_key_refuses_k1(self):
        self.t.write_g(lambda g: g["extra_block"].update(key=V.SIDE_KEY["nopl"]))
        self.assertEqual(self.t.product(self.tmp / "p-k1b"), 1)

    def test_a_block_whose_df_is_not_v_f_minus_c_e_refuses_k2(self):
        z = A.load_npz(self.t.npz)
        z["dF"] = z["dF"] * 1.01
        bad = self.tmp / "bad.npz"
        bad.write_bytes(A.npz_bytes(z))
        pins = {**self.t.pins(), "block_npz": digest(bad)}
        js = json.loads(self.t.bj.read_text())
        js["npz"]["sha256"] = digest(bad)
        bj2 = self.tmp / "bad.json"
        bj2.write_text(json.dumps(js))
        self.t.write_g(lambda g: g["extra_block"].update(sha256=digest(bad)))
        pins.update(g_readout=digest(self.t.g), block_json=digest(bj2))
        a = V.build_args(["product", "--data-product", str(self.t.dp), "--block-npz", str(bad), "--block-json",
                          str(bj2), "--g-readout", str(self.t.g), "--out-dir", str(self.tmp / "p-k2")])
        with quiet(), mock.patch("sys.stderr"), mock.patch.object(V, "report", wraps=V.report) as rep:
            self.assertEqual(V.run(a, pins=pins), 1)
        self.assertEqual(rep.call_args_list[-1].args[0], "K2")

    def test_a_stage_g_sigma_that_is_not_the_revised_matrix_refuses_k3(self):
        def m(g):
            g["predictions"][0]["sigma_total_over_f"][0] *= 1.001
        self.t.write_g(m)
        self.assertEqual(self.t.product(self.tmp / "p-k3"), 1)

    def test_a_stage_g_naming_the_old_covariance_refuses_k3(self):
        self.t.write_g(lambda g: g["predictions"][0].update(reported_covariance="C_total + C_resp + C_PL5D"))
        self.assertEqual(self.t.product(self.tmp / "p-k3b"), 1)

    def test_an_existing_output_refuses(self):
        out = self.tmp / "p-exists"
        out.mkdir()
        (out / f"{V.PRODUCT_STEM}_cells.csv").write_text("x")
        self.assertEqual(self.t.product(out), 1)


class Deposit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="vf-dep-"))
        cls.t = ProductTree(cls.tmp / "t")
        assert cls.t.product(cls.tmp / "dp") == 0
        cls.dp = cls.tmp / "dp" / f"{V.PRODUCT_STEM}.json"
        cls.pins = {"data_product": digest(cls.dp), "g_readout": digest(cls.t.g)}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def run_dc(self, argv, v):
        with quiet(), mock.patch("sys.stderr"):
            return DC.run(DC.build_args(argv), variant=v)

    def test_the_variant_builds_and_checks_the_reported_matrix_with_v_f(self):
        out = self.tmp / "pkg"
        v = V.deposit_variant(self.pins)
        self.assertEqual(self.run_dc(["build", "--data-product", str(self.dp), "--g-readout", str(self.t.g),
                                      "--out-dir", str(out)], v), 0)
        self.assertEqual(self.run_dc(["check", "--package", str(out), "--data-product", str(self.dp),
                                      "--g-readout", str(self.t.g)], v), 0)
        js = json.loads((out / "deposit.json").read_text())
        self.assertEqual(js["covariance_of"], V.REPORTED_F)
        self.assertEqual(js["labels"]["block"], V.LABELS["block"])
        self.assertEqual((out / "covariance.csv").read_bytes(),
                         (self.dp.parent / f"{V.PRODUCT_STEM}_{V.REPORTED_F}.csv").read_bytes())

    def test_the_cpl_variant_cannot_build_from_the_v_f_product(self):
        try:
            rc = self.run_dc(["build", "--data-product", str(self.dp), "--g-readout", str(self.t.g),
                              "--out-dir", str(self.tmp / "pkg-cpl")], A.deposit_variant(self.pins))
        except KeyError as e:                      # the V_F product has no C_total_plus_C_resp_plus_C_PL5D
            rc = str(e)
        self.assertNotEqual(rc, 0)


# ------------------------------------------------------------------------------------------------ the table

def fake_f(names, listed, z=None):
    return {"truths": [{"name": n, "graded": True, "grade_matrix": "M", "grade": {
        "chi2": 10.0 + i, "p": 0.5, "cells_abs_z_gt_2": (z or {}).get(n, [])}} for i, n in enumerate(names)],
        "triggers": {"listed": [{"truth": x} for x in listed]}}


class Table(unittest.TestCase):
    def test_renaming_maps_each_v_f_key_to_the_old_spelling(self):
        self.assertEqual(V.rename_vf("relative_sigma_plus_C_resp + C_PL5D + dF"), "relative_sigma_plus_C_resp + C_PL5D")
        self.assertEqual(V.rename_vf("relative_sigma_plus_C_resp + dF"), "relative_sigma_plus_C_resp")
        self.assertEqual(V.rename_vf("C_total"), "C_total")

    def test_pairing_follows_renamed_keys(self):
        old = {"relative_sigma_plus_C_resp + C_PL5D": {"C_total": [1.0, 2.0]}, "x": 3}
        new = {"relative_sigma_plus_C_resp + C_PL5D + dF": {"C_total": [1.5, 2.5]}, "x": 4}
        got = list(V.paired(old, new))
        self.assertIn(("/relative_sigma_plus_C_resp + C_PL5D/C_total/0", 1.0, 1.5), got)
        self.assertIn(("/x", 3, 4), got)

    def test_curated_names_newly_listed_and_cleared_truths(self):
        o = fake_f(["a", "b", "c"], ["a", "b"])
        n = fake_f(["a", "b", "c"], ["a"])
        with quiet():
            c = V.curated({"F0": o}, {"F0": n})
        self.assertEqual(c["listings"]["F0"]["cleared"], ["b"])
        self.assertEqual(c["listings"]["F0"]["newly_listed"], [])

    def test_truths_in_another_order_refuse_t(self):
        with quiet(), self.assertRaises(V.Stop) as cm:
            V.curated({"F0": fake_f(["a", "b"], [])}, {"F0": fake_f(["b", "a"], [])})
        self.assertEqual(cm.exception.control, "T")

    def test_the_table_refuses_without_the_chains_pins(self):
        tmp = Path(tempfile.mkdtemp(prefix="vf-tab-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        (tmp / "pairs.json").write_text("[]")
        a = V.build_args(["table", "--pairs", str(tmp / "pairs.json"), "--out-dir", str(tmp / "t")])
        with quiet(), mock.patch("sys.stderr"):
            self.assertEqual(V.run(a, pins=None), 1)

    def test_the_table_is_written_from_pinned_pairs(self):
        tmp = Path(tempfile.mkdtemp(prefix="vf-tab-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        po, pn = tmp / "o.json", tmp / "n.json"
        po.write_text(json.dumps(fake_f(["a", "b"], ["a", "b"])))
        pn.write_text(json.dumps(fake_f(["a", "b"], ["a"])))
        (tmp / "pairs.json").write_text(json.dumps([["F0", str(po), str(pn)]]))
        a = V.build_args(["table", "--pairs", str(tmp / "pairs.json"), "--out-dir", str(tmp / "t")])
        with quiet():
            self.assertEqual(V.run(a, pins={str(po): digest(po), str(pn): digest(pn)}), 0)
        js = json.loads((tmp / "t/fd_vf_table.json").read_text())
        self.assertEqual(js["curated"]["listings"]["F0"]["cleared"], ["b"])
        with quiet(), mock.patch("sys.stderr"):
            a2 = V.build_args(["table", "--pairs", str(tmp / "pairs.json"), "--out-dir", str(tmp / "t2")])
            self.assertEqual(V.run(a2, pins={str(po): "0" * 64, str(pn): digest(pn)}), 1)


# ------------------------------------------------------------------------------------------------ the chain

class Recorder(V.Chain):
    """A Chain whose steps are recorded, with each declared output written as a small file, not run."""

    def run(self, name, arm, tool, argv, outputs, timeout, pins=None, variant=""):
        for q in outputs:
            Path(q).parent.mkdir(parents=True, exist_ok=True)
            Path(q).write_text(json.dumps({"step": name, "arm": arm}))
        rec = {"step": name, "arm": arm, "tool": tool, "argv": argv, "pins": pins, "variant": variant or None}
        self.steps.append(rec)
        return rec

    def save(self):
        pass


def flag(argv, f):
    return argv[argv.index(f) + 1] if f in argv else None


class Arms(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="vf-arms-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.BA = self.tmp / "BA"
        for d in ("logs", "pins"):
            (self.BA / d).mkdir(parents=True)
        self.vf = {"npz": self.tmp / "vf_block.npz", "sha": "ab" * 32}
        self.pS = A.Paths(REPO, self.tmp / "P", self.BA)
        import fd_gencmp_e as E
        run_e = self.tmp / "RUN_E"
        (run_e / "pred").mkdir(parents=True)
        (run_e / "pred/SHA256SUMS").write_text("x\n")
        self.pE = E.Paths(REPO, self.BA, run_e, "chdefs")

    def chain(self, p):
        return Recorder(p, self.BA / "chain.json", [])

    def test_each_arms_block_key_name_and_file(self):
        want = {"old-with": (str(self.pS.T / "fd/with-cpl/block/cpl_block.npz"), V.PINS["cpl_block_npz"], A.XKEY, A.NAME),
                "old-nopl": (str(self.pS.cresp), A.PINS["cresp_npz"], "C_resp", "C_resp"),
                "vf-with": (str(self.vf["npz"]), self.vf["sha"], "C_resp_plus_C_PL5D_plus_dF", "C_resp + C_PL5D + dF"),
                "vf-nopl": (str(self.vf["npz"]), self.vf["sha"], "C_resp_plus_dF", "C_resp + dF")}
        for arm, (f, sha, key, name) in want.items():
            xb = V.arm_flags(self.pS, arm, self.vf)
            self.assertEqual((flag(xb, "--extra-block"), flag(xb, "--extra-block-sha256"), flag(xb, "--extra-block-key"),
                              flag(xb, "--extra-block-name"), flag(xb, "--extra-block-role")),
                             (f, sha, key, name, "adopted"), arm)
            self.assertNotIn("--extra-block-role", V.arm_flags(self.pS, arm, self.vf, role=False))

    def test_f0_takes_no_block_in_the_old_arm_and_df_in_the_v_f_arm(self):
        c = self.chain(self.pS)
        V.run_f0(c, "old-f0", self.vf)
        V.run_f0(c, "vf-f0", self.vf)
        old, new = c.steps[0]["argv"], c.steps[1]["argv"]
        self.assertNotIn("--extra-block", old)
        self.assertEqual(old, [*self.pS.f0(), "--out-json", flag(old, "--out-json"), "--out-npz", flag(old, "--out-npz")])
        self.assertEqual((flag(new, "--extra-block-key"), flag(new, "--extra-block-name")), ("dF", "dF"))
        self.assertNotIn("--extra-block-role", new)

    def test_f1_reads_the_committed_f0b_in_an_old_arm_and_its_own_in_a_v_f_arm(self):
        c = self.chain(self.pS)
        committed = (REPO / V.OLD_S["with"]["f0b"][0], V.OLD_S["with"]["f0b"][1])
        V.run_s(c, "old-with", self.vf, committed)
        f1 = [s for s in c.steps if s["step"] == "f1"][0]["argv"]
        self.assertEqual((flag(f1, "--f0b-readout"), flag(f1, "--f0b-readout-sha256")), (str(committed[0]), committed[1]))
        c2 = self.chain(self.pS)
        out = V.run_s(c2, "vf-with", self.vf, None)
        f1 = [s for s in c2.steps if s["step"] == "f1"][0]["argv"]
        self.assertEqual((flag(f1, "--f0b-readout"), flag(f1, "--f0b-readout-sha256")),
                         (str(out["f0b"]), digest(out["f0b"])))
        self.assertEqual([s["step"] for s in c2.steps], ["f0b", "f1", "g"])

    def test_the_chdefs_set_chains_its_pins_and_draws_each_arms_name(self):
        f0b = (self.tmp / "f0b.json", "cd" * 32)
        for arm, name in (("old-with", A.NAME), ("old-nopl", None), ("vf-with", "C_resp + C_PL5D + dF"),
                          ("vf-nopl", "C_resp + dF")):
            c = Recorder(self.pE, self.BA / "chain.json", [], self.tmp / "preds.json")
            res = V.run_e(c, arm, self.vf, f0b)
            self.assertEqual([s["step"] for s in c.steps], [*V.E_STEPS, "figures", "figures_check"], arm)
            diag = c.steps[1]
            self.assertEqual(diag["pins"]["g_readout"], res["H"]["g"], arm)
            self.assertEqual(diag["pins"]["s5p_sums"], digest(self.pE.s5p_sums), arm)
            fig = c.steps[5]
            self.assertEqual(flag(fig["argv"], "--reported-block-name"), name, arm)
            self.assertEqual(fig["argv"].count("--reported-block-name"), 1 if name else 0, arm)
            self.assertEqual(flag(fig["argv"], "--prediction-set"), "gencmp-chdefs", arm)
            self.assertEqual((flag(fig["argv"], "--f0b-readout"), fig["pins"]["f0b_readout"]), (str(f0b[0]), f0b[1]), arm)


class Checks(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="vf-chk-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.BA = self.tmp / "BA"
        for d in ("logs", "pins"):
            (self.BA / d).mkdir(parents=True)
        self.c = V.Chain(A.Paths(REPO, self.tmp / "P", self.BA), self.BA / "chain.json", [])

    def test_r_holds_on_the_committed_readout_but_argv_and_block_file_and_fires_on_a_number(self):
        rel, pin = V.OLD_S["with"]["g"]
        g = json.loads((REPO / rel).read_text())
        g["argv"] = ["moved"]
        g["extra_block"]["file"] = "/elsewhere/cpl_block.npz"
        new = self.tmp / "g.json"
        new.write_text(json.dumps(g))
        with quiet():
            V.check_r(self.c, "g", REPO, rel, pin, new, strings=True)
        g["predictions"][0]["total"]["chi2"] *= 1 + 1e-9
        new.write_text(json.dumps(g))
        with quiet(), self.assertRaises(V.Stop) as cm:
            V.check_r(self.c, "g", REPO, rel, pin, new, strings=False)
        self.assertEqual(cm.exception.control, "R")

    def test_r_with_strings_fires_on_a_changed_label_and_without_them_does_not(self):
        rel, pin = V.OLD_S["with"]["g"]
        g = json.loads((REPO / rel).read_text())
        g["labels"] = {**g.get("labels", {}), "what": "something else"}
        new = self.tmp / "g.json"
        new.write_text(json.dumps(g))
        with quiet():
            V.check_r(self.c, "g", REPO, rel, pin, new, strings=False)
        with quiet(), self.assertRaises(V.Stop):
            V.check_r(self.c, "g", REPO, rel, pin, new, strings=True)

    def test_r_fires_on_a_committed_file_that_is_not_its_pin(self):
        rel, _ = V.OLD_S["with"]["g"]
        with quiet(), self.assertRaises(V.Stop):
            V.check_r(self.c, "g", REPO, rel, "0" * 64, REPO / rel, strings=False)

    def test_s_and_c_hold_on_a_consistent_readout_and_fire_otherwise(self):
        t = ProductTree(self.tmp / "t")
        blk = A.load_npz(t.npz)
        with quiet():
            V.check_s(self.c, "x", t.g, None, blk, "with")
            V.check_c(self.c, "x", t.g, digest(t.npz), {})
        with quiet(), self.assertRaises(V.Stop) as cm:
            V.check_s(self.c, "x", t.g, None, blk, "nopl")        # the nopl matrix's sigma is smaller
        self.assertEqual(cm.exception.control, "S")
        with quiet(), self.assertRaises(V.Stop) as cm:
            V.check_c(self.c, "x", t.g, "0" * 64, {})
        self.assertEqual(cm.exception.control, "C")

    def test_c_fires_on_an_upstream_digest_that_is_not_the_written_one(self):
        p = self.tmp / "r.json"
        p.write_text(json.dumps({"extra_block": {"sha256": "ab" * 32}, "inputs_sha256": {"g_readout": "11" * 32}}))
        with quiet():
            V.check_c(self.c, "x", p, "ab" * 32, {"g_readout": "11" * 32})
        with quiet(), self.assertRaises(V.Stop):
            V.check_c(self.c, "x", p, "ab" * 32, {"g_readout": "22" * 32})


class Order(unittest.TestCase):
    """No V_F step runs unless every OLD-arm control has passed."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="vf-order-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.D = self.tmp / "D"
        b = self.D / V.FD / "fd/with-vf/block"
        b.mkdir(parents=True)
        a = V.build_args(["block", "--repo", str(REPO), "--out-dir", str(self.tmp / "blk")])
        with quiet():
            assert V.run(a) == 0
        for n in ("vf_block.npz", "vf_block.json"):
            shutil.copy(self.tmp / "blk" / n, b / n)
        for rel, _ in [V.OLD_F0, *[v for s in (V.OLD_S, V.OLD_E) for arm in s.values() for v in arm.values()]]:
            (self.D / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(REPO / rel, self.D / rel)
        self.calls = []

    def recorder_run(self, chain, name, arm, tool, argv, outputs, timeout, pins=None, variant=""):
        self.calls.append((name, arm))
        for q in outputs:
            Path(q).parent.mkdir(parents=True, exist_ok=True)
            src = self.tmp / "blk" / Path(q).name
            Path(q).write_bytes(src.read_bytes() if src.exists() else b"{}")
        return {}

    def run_chain(self, fail_label, check_r=None):
        def default_check_r(c, label, *a, **k):
            self.calls.append(("R", label))
            if label == fail_label:
                raise V.Stop("R", label)

        check_r = check_r or default_check_r

        a = V.build_args(["chain", "--run-dir", str(self.tmp / "BA"), "--run-e", str(self.tmp / "E"),
                          "--scratch", str(self.tmp / "P")])
        patches = [mock.patch.object(V, "DEPLOY", self.D),
                   mock.patch.object(V.Chain, "run", lambda c, *x, **k: self.recorder_run(c, *x, **k)),
                   mock.patch.object(V, "check_r", check_r),
                   mock.patch.object(V, "check_r_figures", lambda *x, **k: None),
                   mock.patch.object(V, "run_f0", lambda c, arm, vf: (self.calls.append(("f0", arm)), self.tmp)[1]),
                   mock.patch.object(V, "run_s", lambda c, arm, vf, f: (self.calls.append(("S", arm)),
                                                                        {k: self.tmp for k in V.S_STEPS})[1]),
                   mock.patch.object(V, "run_e", lambda c, arm, vf, f: (self.calls.append(("E", arm)),
                                                                        {"out": {k: self.tmp for k in V.E_STEPS},
                                                                         "H": {}, "fig": self.tmp})[1]),
                   mock.patch("fd_gencmp_e.load_chdefs", lambda p: [])]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        with quiet(), mock.patch("sys.stderr"):
            return V.run(a)

    def test_a_failed_old_control_stops_before_any_v_f_step(self):
        for label in ("F0", "S old-with g", "E old-nopl flux_boot"):
            self.calls = []
            shutil.rmtree(self.tmp / "BA", ignore_errors=True)
            self.assertEqual(self.run_chain(label), 1, label)
            self.assertFalse([c for c in self.calls if str(c[1]).startswith("vf-")], (label, self.calls))
            self.assertIn(("R", label), self.calls)

    def test_the_old_arms_run_in_order_before_the_first_v_f_step(self):
        self.calls = []
        with mock.patch.object(V.Chain, "check", lambda c, name, ok, detail: self.calls.append(("check", name))):
            self.run_chain("E old-nopl g_sens2")
        arms = [c[1] for c in self.calls if c[0] in ("f0", "S", "E")]
        self.assertEqual(arms, ["old-f0", "old-with", "old-with", "old-nopl", "old-nopl"])

    def test_the_chdefs_old_with_arm_compares_strings_and_the_nopl_arm_does_not(self):
        seen = {}

        def check_r(c, label, *a, strings=False):
            seen[label] = strings
            if label == "E old-nopl flux_boot":
                raise V.Stop("R", label)

        self.assertEqual(self.run_chain(None, check_r), 1)
        self.assertTrue(seen["E old-with g"])
        self.assertFalse(seen["E old-nopl g"])
        self.assertFalse(seen["S old-with g"])
        self.assertFalse(seen["F0"])

    def test_a_committed_block_that_is_not_the_pinned_bytes_refuses_before_any_step(self):
        p = self.D / V.FD / "fd/with-vf/block/vf_block.npz"
        p.write_bytes(p.read_bytes() + b"x")
        self.calls = []
        self.assertEqual(self.run_chain(None), 1)
        self.assertEqual(self.calls, [])

    def test_an_existing_run_directory_refuses(self):
        (self.tmp / "BA" / "S").mkdir(parents=True)
        self.assertEqual(self.run_chain(None), 1)
        self.assertEqual(self.calls, [])


class Boot(unittest.TestCase):
    def test_the_bootstrap_gives_each_variant_its_module(self):
        self.assertIn('variant in ("with-cpl", "with-vf")', V.BOOT)
        self.assertIn('(A if variant == "with-cpl" else V).deposit_variant(pins)', V.BOOT)
        self.assertIn('kw["predictions"] = json.load(open(preds_file))', V.BOOT)

    def test_the_v_f_variant_reaches_the_tool_through_the_bootstrap(self):
        tmp = Path(tempfile.mkdtemp(prefix="vf-boot-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        t = ProductTree(tmp / "t")
        assert t.product(tmp / "dp") == 0
        dp = tmp / "dp" / f"{V.PRODUCT_STEM}.json"
        BA = tmp / "BA"
        for d in ("logs", "pins"):
            (BA / d).mkdir(parents=True)
        c = V.Chain(A.Paths(REPO, tmp / "P", BA), BA / "chain.json", [])
        pins = {"data_product": digest(dp), "g_readout": digest(t.g)}
        pkg = BA / "pkg"
        with quiet():
            c.run("deposit_build", "vf-with", "fd_deposit_candidate",
                  ["build", "--data-product", str(dp), "--g-readout", str(t.g), "--out-dir", str(pkg)],
                  [pkg / "deposit.json"], 120, pins=pins, variant="with-vf")
        self.assertEqual(json.loads((pkg / "deposit.json").read_text())["covariance_of"], V.REPORTED_F)
        self.assertEqual(json.loads((BA / "chain.json").read_text())["steps"][0]["variant"], "with-vf")


if __name__ == "__main__":
    unittest.main()
