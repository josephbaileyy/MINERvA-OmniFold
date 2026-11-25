"""Tests of fd_vf_addition.py (FD-VF-ADDITION-DECLARATION.md): each control is shown to fire on the defect it guards
and to stay silent on the good case; the chain's argv, blocks and names per arm; and the order that keeps every V_F
step behind the OLD arms' controls."""
from __future__ import annotations

import copy
import json
import os
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
        self.assertEqual(list(z), ["f", "C_e", "C_e_infl", "DeltaC_e", "C_resp_plus_DeltaC_e", "C_resp_plus_C_PL5D_plus_DeltaC_e",
                                   V.WITHOUT_F, V.REPORTED_F])
        self.assertTrue(np.array_equal(z["DeltaC_e"], z["C_e_infl"] - z["C_e"]))
        cpl = A.load_npz(FDP / "fd/with-cpl/block/cpl_block.npz")
        self.assertTrue(np.array_equal(z["C_resp_plus_C_PL5D_plus_DeltaC_e"], cpl[A.XKEY] + z["DeltaC_e"]))
        self.assertTrue(np.array_equal(z["C_resp_plus_DeltaC_e"], cpl["C_resp"] + z["DeltaC_e"]))
        js = json.loads((self.tmp / "b/vf_block.json").read_text())
        self.assertEqual(js["npz"]["sha256"], V.VF_BLOCK_NPZ)
        self.assertEqual(js["inputs_sha256"], V.PINS)
        self.assertEqual([b["name"] for b in js["npz"]["extra_blocks"]], ["DeltaC_e", "C_resp + DeltaC_e", "C_resp + C_PL5D + DeltaC_e"])

    def test_the_committed_block_is_the_pinned_bytes(self):
        p = FDP / "fd/with-vf/block/vf_block.npz"
        if not p.exists():
            self.skipTest("the block is committed with the code")
        self.assertEqual(digest(p), V.VF_BLOCK_NPZ)

    @unittest.skipIf(os.environ.get("VF_MUTANT_RUN") == "1", "provenance, not behaviour: any edit of the module fails it")
    def test_the_committed_block_readout_is_what_this_code_writes(self):
        p = FDP / "fd/with-vf/block/vf_block.json"
        if not p.exists():
            self.skipTest("the block is committed with the code")
        self.assertEqual(self.run_block(self.tmp / "b"), 0)
        self.assertEqual((self.tmp / "b/vf_block.json").read_bytes(), p.read_bytes(),
                         "vf_block.json names another fd_vf_addition.py: rebuild it with this code")

    def test_a_member_stored_big_endian_refuses_v4(self):
        import io as _io
        import zipfile as _zf

        def big(arrays):                                  # the same values, with "f" stored as >f8
            buf = _io.BytesIO()
            with _zf.ZipFile(buf, "w", _zf.ZIP_STORED) as z:
                for k, v in arrays.items():
                    b = _io.BytesIO()
                    np.lib.format.write_array(b, np.asarray(v, dtype=">f8" if k == "f" else "<f8"), allow_pickle=False)
                    zi = _zf.ZipInfo(f"{k}.npy", date_time=(1980, 1, 1, 0, 0, 0))   # fixed: both writes agree
                    zi.compress_type = _zf.ZIP_STORED
                    z.writestr(zi, b.getvalue())
            return buf.getvalue()
        with mock.patch.object(A, "npz_bytes", big), mock.patch.object(V, "report", wraps=V.report) as rep:
            self.assertEqual(self.run_block(self.tmp / "b"), 1)
        last = rep.call_args_list[-1].args
        self.assertEqual(last[:2], ("V4", "the npz reads back key by key, bit for bit (dtype, shape and bytes)"))
        self.assertFalse(last[2])

    def test_an_existing_output_refuses(self):
        (self.tmp / "b").mkdir()
        (self.tmp / "b/vf_block.json").write_text("{}")
        self.assertEqual(self.run_block(self.tmp / "b"), 1)

    def test_an_input_that_is_not_its_pin_refuses_v0(self):
        with mock.patch.dict(V.PINS, {"v_f_csv": "0" * 64}):
            self.assertEqual(self.run_block(self.tmp / "b"), 1)
        self.assertFalse((self.tmp / "b/vf_block.npz").exists())

    def record_repo(self, mutate):
        """A repository copy of the five inputs, with blocks5d.json mutated and its pin moved to the new bytes."""
        r = self.tmp / "repo"
        for k, rel in V.SOURCES.items():
            (r / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(REPO / rel, r / rel)
        js = json.loads((r / V.SOURCES["blocks5d_json"]).read_text())
        mutate(js)
        (r / V.SOURCES["blocks5d_json"]).write_text(json.dumps(js))
        return r, digest(r / V.SOURCES["blocks5d_json"])

    def last_check(self, fn):
        with quiet(), mock.patch.object(V, "report", wraps=V.report) as rep, self.assertRaises(V.Stop):
            fn()
        return rep.call_args_list[-1].args[1]

    def test_a_record_naming_another_v_f_refuses_v0(self):
        r, h = self.record_repo(lambda js: js["matrices_sha256"].update({"V_F.csv": "0" * 64}))
        with mock.patch.dict(V.PINS, {"blocks5d_json": h}):
            self.assertEqual(self.last_check(lambda: V.block_inputs(r)), "the B5D record names this V_F")

    def test_a_record_whose_v_f_is_not_the_csvs_refuses_v0(self):
        def m(js):
            js["fluctuation"]["V_F"][0][0] *= 1 + 1e-15
        r, h = self.record_repo(m)
        with mock.patch.dict(V.PINS, {"blocks5d_json": h}):
            self.assertEqual(self.last_check(lambda: V.block_inputs(r)), "the record's V_F is the CSV's, bit for bit")

    def test_an_asymmetric_l_with_a_consistent_v_f_refuses_on_symmetry(self):
        VF, L, Ce, dp, cpl = inputs()
        L2 = L.copy()
        L2[0, 1] += 1e-3
        self.assertEqual(self.last_check(lambda: V.build_block(L2 @ Ce @ L2.T, L2, Ce, dp, cpl)), "L is symmetric")

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
        self.assertEqual(float(np.abs(z["DeltaC_e"]).max()), 0.0)
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
        g["argv"] = ["fd_g_compare.py", "--extra-block", str(self.npz), "--extra-block-sha256", digest(self.npz),
                     "--extra-block-key", V.SIDE_KEY["with"], "--extra-block-name", V.BLOCKS[V.SIDE_KEY["with"]],
                     "--extra-block-role", "adopted"]
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

    def test_another_committed_product_with_its_own_digest_refuses_k0(self):
        other = self.tmp / "dp-other.json"
        other.write_bytes(self.t.dp.read_bytes() + b"\n")
        a = V.build_args(["product", "--data-product", str(other), "--block-npz", str(self.t.npz), "--block-json",
                          str(self.t.bj), "--g-readout", str(self.t.g), "--out-dir", str(self.tmp / "p-k0b")])
        with quiet(), mock.patch("sys.stderr"), mock.patch.object(V, "report", wraps=V.report) as rep:
            self.assertEqual(V.run(a, pins={**self.t.pins(), "data_product": digest(other)}), 1)
        self.assertEqual(rep.call_args_list[-1].args[1], "the committed data product's pin is the declared one")

    def test_a_block_readout_on_other_inputs_refuses_k1(self):
        js = json.loads(self.t.bj.read_text())
        js["inputs_sha256"]["v_f_csv"] = "0" * 64
        bj2 = self.tmp / "bj-other.json"
        bj2.write_text(json.dumps(js))
        a = V.build_args(["product", "--data-product", str(self.t.dp), "--block-npz", str(self.t.npz), "--block-json",
                          str(bj2), "--g-readout", str(self.t.g), "--out-dir", str(self.tmp / "p-k1c")])
        with quiet(), mock.patch("sys.stderr"), mock.patch.object(V, "report", wraps=V.report) as rep:
            self.assertEqual(V.run(a, pins={**self.t.pins(), "block_json": digest(bj2)}), 1)
        self.assertEqual(rep.call_args_list[-1].args[1], "the block readout names this npz and the pinned inputs")

    def test_a_block_whose_v_f_is_not_df_plus_c_e_refuses_on_df(self):
        z = A.load_npz(self.t.npz)
        z["C_e_infl"] = z["C_e_infl"] * 1.01
        bad = self.tmp / "bad-vf.npz"
        bad.write_bytes(A.npz_bytes(z))
        js = json.loads(self.t.bj.read_text())
        js["npz"]["sha256"] = digest(bad)
        bj2 = self.tmp / "bad-vf.json"
        bj2.write_text(json.dumps(js))
        self.t.write_g(lambda g: g["extra_block"].update(sha256=digest(bad)))
        a = V.build_args(["product", "--data-product", str(self.t.dp), "--block-npz", str(bad), "--block-json",
                          str(bj2), "--g-readout", str(self.t.g), "--out-dir", str(self.tmp / "p-k2b")])
        pins = {**self.t.pins(), "block_npz": digest(bad), "block_json": digest(bj2), "g_readout": digest(self.t.g)}
        with quiet(), mock.patch("sys.stderr"), mock.patch.object(V, "report", wraps=V.report) as rep:
            self.assertEqual(V.run(a, pins=pins), 1)
        self.assertEqual(rep.call_args_list[-1].args[1], "DeltaC_e is the block's C_e_infl - C_e, bit for bit")

    def test_a_stage_g_on_the_old_block_name_refuses_k1(self):
        self.t.write_g(lambda g: g["extra_block"].update(name=A.NAME))
        self.assertEqual(self.t.product(self.tmp / "p-k1"), 1)

    def test_a_stage_g_on_the_nopl_key_refuses_k1(self):
        self.t.write_g(lambda g: g["extra_block"].update(key=V.SIDE_KEY["nopl"]))
        self.assertEqual(self.t.product(self.tmp / "p-k1b"), 1)

    def test_a_block_whose_df_is_not_v_f_minus_c_e_refuses_k2(self):
        z = A.load_npz(self.t.npz)
        z["DeltaC_e"] = z["DeltaC_e"] * 1.01
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

    def test_a_stage_g_with_a_shortened_cell_list_refuses_k3(self):
        def m(g):
            g["predictions"][0]["cells"] = g["predictions"][0]["cells"][:-1]
            g["predictions"][0]["sigma_total_over_f"] = g["predictions"][0]["sigma_total_over_f"][:-1]
        self.t.write_g(m)
        with mock.patch.object(V, "report", wraps=V.report) as rep:
            self.assertEqual(self.t.product(self.tmp / "p-k3c"), 1)
        self.assertEqual(rep.call_args_list[-1].args[:2],
                         ("K3", "Stage G's predictions are its declared five, in order, on their declared cells"))

    def test_a_stage_g_naming_the_old_covariance_refuses_k3(self):
        self.t.write_g(lambda g: g["predictions"][0].update(reported_covariance="C_total + C_resp + C_PL5D"))
        self.assertEqual(self.t.product(self.tmp / "p-k3b"), 1)

    def test_a_file_changed_on_disk_after_writing_refuses_k6(self):
        real = A.write_atomic

        def corrupting(path, data):
            real(path, data.replace(b"R07", b"R7 ") if path.name.endswith("_cells.csv") else data)
        with mock.patch.object(A, "write_atomic", corrupting), mock.patch.object(V, "report", wraps=V.report) as rep:
            self.assertEqual(self.t.product(self.tmp / "p-k6"), 1)
        self.assertEqual(rep.call_args_list[-1].args[0], "K6")
        self.assertFalse((self.tmp / "p-k6").exists(), "a refused product installs no output")

    def test_a_json_whose_bytes_changed_on_disk_refuses_k6(self):
        real = A.write_atomic

        def spaced(path, data):
            real(path, data + b" " if path.name == f"{V.PRODUCT_STEM}.json" else data)
        with mock.patch.object(A, "write_atomic", spaced), mock.patch.object(V, "report", wraps=V.report) as rep:
            self.assertEqual(self.t.product(self.tmp / "p-k6j"), 1)
        self.assertEqual(rep.call_args_list[-1].args[:2], ("K6", f"{V.PRODUCT_STEM}.json: the file on disk is the bytes written"))

    def cells_text_changed(self, out, change):
        real = V.product_files

        def files(p, dp):
            f = real(p, dp)
            n = f"{V.PRODUCT_STEM}_cells.csv"
            f[n] = change(f[n])
            return f
        with mock.patch.object(V, "product_files", files), mock.patch.object(V, "report", wraps=V.report) as rep:
            self.assertEqual(self.t.product(self.tmp / out), 1)
        return rep.call_args_list[-1].args[:2]

    def test_a_cells_csv_whose_f_is_not_the_products_refuses_k6_on_readback(self):
        def bump(text):
            rows = text.splitlines()
            head = rows[0].split(",")
            r1 = rows[1].split(",")
            r1[head.index("f")] = repr(float(r1[head.index("f")]) * 1.0000001)
            return "\n".join([rows[0], ",".join(r1), *rows[2:]]) + "\n"
        self.assertEqual(self.cells_text_changed("p-k6f", bump),
                         ("K6", "the cells CSV lists R00-R15 with f and every relative sigma, bit for bit"))

    def test_a_cells_csv_whose_box_edges_are_not_the_products_refuses_k6_on_readback(self):
        def edge(text):
            rows = text.splitlines()
            r1 = rows[1].split(",")
            r1[1] = repr(float(r1[1]) + 0.001)
            return "\n".join([rows[0], ",".join(r1), *rows[2:]]) + "\n"
        self.assertEqual(self.cells_text_changed("p-k6e", edge),
                         ("K6", "the cells CSV's box edges are the committed product's cells, bit for bit"))

    def test_a_box_edge_of_minus_zero_refuses_k6_on_readback(self):
        def mzero(text):
            rows = text.splitlines()
            r1 = rows[1].split(",")
            assert r1[1] == "0.0", r1[1]
            r1[1] = "-0.0"
            return "\n".join([rows[0], ",".join(r1), *rows[2:]]) + "\n"
        self.assertEqual(self.cells_text_changed("p-k6z", mzero),
                         ("K6", "the cells CSV's box edges are the committed product's cells, bit for bit"))

    def test_cells_whose_box_edges_are_not_the_products_refuse_k6(self):
        real = A.write_atomic

        def edges(path, data):
            real(path, data.replace(b"R00,0.0,", b"R00,0.001,", 1) if path.name.endswith("_cells.csv") else data)
        with mock.patch.object(A, "write_atomic", edges), mock.patch.object(V, "report", wraps=V.report) as rep:
            self.assertEqual(self.t.product(self.tmp / "p-k6b"), 1)
        self.assertEqual(rep.call_args_list[-1].args[0], "K6")

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

def fake_f(names, listed, z=None, m="M"):
    return {"truths": [{"name": n, "graded": True, "grade_matrix": m, "grade": {
        "chi2": 10.0 + i, "p": 0.5, "cells": V.CELLS, "cells_abs_z_gt_2": (z or {}).get(n, [])}}
        for i, n in enumerate(names)],
        "triggers": {"listed": [{"truth": x} for x in listed]}}


class Table(unittest.TestCase):
    def test_renaming_maps_each_v_f_key_to_the_old_spelling(self):
        self.assertEqual(V.rename_vf("relative_sigma_plus_C_resp + C_PL5D + DeltaC_e"), "relative_sigma_plus_C_resp + C_PL5D")
        self.assertEqual(V.rename_vf("relative_sigma_plus_C_resp + DeltaC_e"), "relative_sigma_plus_C_resp")
        self.assertEqual(V.rename_vf("C_total"), "C_total")

    def test_curated_names_newly_listed_and_cleared_truths(self):
        o = fake_f(["a", "b", "c"], ["a", "b"])
        n = fake_f(["a", "b", "c"], ["a"], m="M + DeltaC_e")
        with quiet():
            c = V.curated({"S with/f0b": o}, {"S with/f0b": n})
        self.assertEqual(c["listings"]["S with/f0b"]["cleared"], ["b"])
        self.assertEqual(c["listings"]["S with/f0b"]["newly_listed"], [])

    def test_truths_in_another_order_refuse_t(self):
        with quiet(), self.assertRaises(V.Stop) as cm:
            V.curated({"S with/f0b": fake_f(["a", "b"], [])}, {"S with/f0b": fake_f(["b", "a"], [], m="M + DeltaC_e")})
        self.assertEqual(cm.exception.control, "T")

    def test_same_bits_tells_minus_zero_and_dtype_apart(self):
        self.assertTrue(V.same_bits(np.array([0.0, 1.0]), np.array([0.0, 1.0])))
        self.assertFalse(V.same_bits(np.array([0.0]), np.array([-0.0])))
        self.assertFalse(V.same_bits(np.array([1.0]), np.array([1.0], dtype=np.float32)))

    def test_named_records_are_checked_in_every_readout_family_before_pairing(self):
        rel = V.OLD_E["with"]["g_diag"][0]
        o = json.loads((REPO / rel).read_text())
        n = copy.deepcopy(o)
        with quiet():
            V.identities(o, n, "E with/g_diag")
        n["predictions"] = n["predictions"][::-1]
        with quiet(), self.assertRaises(V.Stop) as cm:
            V.identities(o, n, "E with/g_diag")
        self.assertEqual(cm.exception.control, "T")
        o = {"modes": [{"name": "C_total + C_resp + C_PL5D + V_g", "x": 1}]}
        n = {"modes": [{"name": "C_total + C_resp + C_PL5D + DeltaC_e + V_g", "x": 2}]}
        with quiet():
            V.identities(o, n, "x")

    def test_f0s_sigma_pairs_its_base_with_the_revised_one_on_the_same_cells(self):
        o, n = fake_f(["a"], []), fake_f(["a"], [], m="M + DeltaC_e")
        o["cells"] = n["cells"] = V.CELLS
        o["relative_sigma"] = {"C_total": [1.0] * 16}
        with quiet(), self.assertRaises(V.Stop):
            V.curated({"F0": o}, {"F0": n})
        n["relative_sigma_plus_DeltaC_e"] = {"C_total": [1.1] * 16}
        with quiet():
            c = V.curated({"F0": o}, {"F0": n})
        self.assertEqual(c["f0_sigma"], {"cells": V.CELLS, "old": {"C_total": [1.0] * 16}, "vf": {"C_total": [1.1] * 16}})
        n["cells"] = V.CELLS[::-1]                                   # the same truths on reversed cells
        with quiet(), self.assertRaises(V.Stop):
            V.curated({"F0": o}, {"F0": n})
        n["cells"] = V.CELLS
        n["relative_sigma_plus_DeltaC_e"] = {"C_total": [1.1] * 15}  # a shortened vector
        with quiet(), self.assertRaises(V.Stop):
            V.curated({"F0": o}, {"F0": n})

    def test_curated_checks_identities_in_a_family_it_has_no_rows_for(self):
        rel = V.OLD_E["with"]["g_diag"][0]
        o = json.loads((REPO / rel).read_text())
        n = copy.deepcopy(o)
        n["predictions"] = n["predictions"][::-1]
        with quiet(), self.assertRaises(V.Stop) as cm:
            V.curated({"E with/g_diag": o}, {"E with/g_diag": n})
        self.assertEqual(cm.exception.control, "T")

    def test_each_side_names_its_matrix(self):
        o = fake_f(["a"], [])
        n = copy.deepcopy(o)
        n["truths"][0]["grade_matrix"] = "M + DeltaC_e"
        with quiet():
            V.curated({"S with/f0b": o}, {"S with/f0b": n})
        n["truths"][0]["grade_matrix"] = "M"
        with quiet(), self.assertRaises(V.Stop):
            V.curated({"S with/f0b": o}, {"S with/f0b": n})

    def test_stage_g_matrices_carry_df_before_v_g_and_the_order_is_checked(self):
        def g(names, m):
            return {"predictions": [{"name": x, "cells": V.CELLS, "total": {"chi2": 1.0, "p": 0.5, "ndf": 16, "matrix": m + " + V_g"},
                                     "shape_only": {"chi2": 1.0, "p": 0.5, "ndf": 15,
                                                    "matrix": m + " + V_g + 100 f f^T (free normalization)"}}
                                    for x in names]}
        o, n = g(["a", "b"], "C_total + C_resp + C_PL5D"), g(["a", "b"], "C_total + C_resp + C_PL5D + DeltaC_e")
        with quiet():
            c = V.curated({"S with/g": o}, {"S with/g": n})
        self.assertEqual(len(c["stage_g"]["S with/g"]), 4)
        with quiet(), self.assertRaises(V.Stop):
            V.curated({"S with/g": o}, {"S with/g": g(["a", "b"], "C_total + C_resp + C_PL5D")})
        with quiet(), self.assertRaises(V.Stop):
            V.curated({"S with/g": o}, {"S with/g": g(["b", "a"], "C_total + C_resp + C_PL5D + DeltaC_e")})
        n2 = g(["a", "b"], "C_total + C_resp + C_PL5D + DeltaC_e")
        n2["predictions"][0]["shape_only"]["ndf"] = 16                # a revised shape-only grade on 16 dof
        with quiet(), self.assertRaises(V.Stop):
            V.curated({"S with/g": o}, {"S with/g": n2})

    def test_the_table_refuses_without_the_chains_pins(self):
        tmp = Path(tempfile.mkdtemp(prefix="vf-tab-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        (tmp / "pairs.json").write_text(json.dumps([["F0", str(tmp / "o"), "0" * 64, str(tmp / "n"), "0" * 64]]))
        a = V.build_args(["table", "--pairs", str(tmp / "pairs.json"), "--out-dir", str(tmp / "t")])
        with quiet(), mock.patch("sys.stderr") as err:
            self.assertEqual(V.run(a, pins=None), 1)
        self.assertIn("table runs in the chain only", "".join(str(c) for c in err.mock_calls))

    def test_the_table_is_written_from_pinned_pairs(self):
        tmp = Path(tempfile.mkdtemp(prefix="vf-tab-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        po, pn = tmp / "o.json", tmp / "n.json"
        po.write_text(json.dumps(fake_f(["a", "b"], ["a", "b"])))
        pn.write_text(json.dumps(fake_f(["a", "b"], ["a"], m="M + DeltaC_e")))
        o, n = fake_f(["a", "b"], ["a", "b"]), fake_f(["a", "b"], ["a"], m="M + DeltaC_e")
        o["cells"] = n["cells"] = V.CELLS
        o["relative_sigma"], n["relative_sigma_plus_DeltaC_e"] = {"C_total": [1.0] * 16}, {"C_total": [1.1] * 16}
        po.write_text(json.dumps(o))
        pn.write_text(json.dumps(n))
        (tmp / "pairs.json").write_text(json.dumps([["F0", str(po), digest(po), str(pn), digest(pn)]]))
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
        rec = {"step": name, "arm": arm, "tool": tool, "argv": argv, "pins": pins, "variant": variant or None,
               "outputs": {str(q): digest(Path(q)) for q in outputs}}
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
                "vf-with": (str(self.vf["npz"]), self.vf["sha"], "C_resp_plus_C_PL5D_plus_DeltaC_e", "C_resp + C_PL5D + DeltaC_e"),
                "vf-nopl": (str(self.vf["npz"]), self.vf["sha"], "C_resp_plus_DeltaC_e", "C_resp + DeltaC_e")}
        for arm, (f, sha, key, name) in want.items():
            xb = V.arm_flags(self.pS, arm, self.vf)
            self.assertEqual((flag(xb, "--extra-block"), flag(xb, "--extra-block-sha256"), flag(xb, "--extra-block-key"),
                              flag(xb, "--extra-block-name"), flag(xb, "--extra-block-role")),
                             (f, sha, key, name, "adopted"), arm)
            self.assertNotIn("--extra-block-role", V.arm_flags(self.pS, arm, self.vf, role=False))

    def test_f0_takes_no_block_in_the_old_arm_and_df_in_the_v_f_arm(self):
        c = self.chain(self.pS)
        with mock.patch.object(V, "check_c", lambda *x, **k: None):
            V.run_f0(c, "old-f0", self.vf)
            V.run_f0(c, "vf-f0", self.vf)
        old, new = c.steps[0]["argv"], c.steps[1]["argv"]
        self.assertNotIn("--extra-block", old)
        self.assertEqual(old, [*self.pS.f0(), "--out-json", flag(old, "--out-json"), "--out-npz", flag(old, "--out-npz")])
        self.assertEqual((flag(new, "--extra-block-key"), flag(new, "--extra-block-name")), ("DeltaC_e", "DeltaC_e"))
        self.assertNotIn("--extra-block-role", new)

    def test_f0s_c_e_infl_arm_is_checked_with_its_block_and_the_old_arm_is_not(self):
        seen = []
        c = self.chain(self.pS)
        with mock.patch.object(V, "check_c", lambda c, label, path, sha, key, up, role, **k: seen.append((label, key, k))):
            V.run_f0(c, "old-f0", self.vf)
            V.run_f0(c, "vf-f0", self.vf)
        self.assertEqual(seen, [("vf-f0 f0", "DeltaC_e", {"tool": "fd_f0_regrade"})])

    def test_f1_reads_the_committed_f0b_in_an_old_arm_and_its_own_in_a_v_f_arm(self):
        c = self.chain(self.pS)
        committed = (REPO / V.OLD_S["with"]["f0b"][0], V.OLD_S["with"]["f0b"][1])
        V.run_s(c, "old-with", self.vf, committed)
        f1 = [s for s in c.steps if s["step"] == "f1"][0]["argv"]
        self.assertEqual((flag(f1, "--f0b-readout"), flag(f1, "--f0b-readout-sha256")), (str(committed[0]), committed[1]))
        c2 = self.chain(self.pS)
        with mock.patch.object(V, "check_c", lambda *x, **k: None):
            out = V.run_s(c2, "vf-with", self.vf, None)
        f1 = [s for s in c2.steps if s["step"] == "f1"][0]["argv"]
        self.assertEqual((flag(f1, "--f0b-readout"), flag(f1, "--f0b-readout-sha256")),
                         (str(out["f0b"]), digest(out["f0b"])))
        self.assertEqual([s["step"] for s in c2.steps], ["f0b", "f1", "g"])

    def test_the_chdefs_set_pins_committed_upstreams_in_old_arms_and_written_ones_in_v_f_arms(self):
        f0b = (self.tmp / "f0b.json", "cd" * 32)
        for arm, name in (("old-with", A.NAME), ("old-nopl", None), ("vf-with", "C_resp + C_PL5D + DeltaC_e"),
                          ("vf-nopl", None)):
            c = Recorder(self.pE, self.BA / "chain.json", [], self.tmp / "preds.json")
            with mock.patch.object(V, "check_c", lambda *x, **k: None):
                res = V.run_e(c, arm, self.vf, f0b)
            side = arm.split("-")[1]
            steps = [*V.E_STEPS, *(["figures", "figures_check"] if side == "with" else [])]
            self.assertEqual([s["step"] for s in c.steps], steps, arm)
            diag, fup = c.steps[1], c.steps[2]
            if arm.startswith("old"):
                self.assertEqual(diag["pins"]["g_readout"], V.OLD_E[side]["g"][1], arm)
                self.assertEqual(flag(diag["argv"], "--g-readout"), str(REPO / V.OLD_E[side]["g"][0]), arm)
                self.assertEqual(fup["pins"]["g_diag_readout"], V.OLD_E[side]["g_diag"][1], arm)
            else:
                self.assertEqual(diag["pins"]["g_readout"], res["H"]["g"], arm)
                self.assertEqual(flag(diag["argv"], "--g-readout"), str(res["out"]["g"]), arm)
            self.assertEqual(diag["pins"]["s5p_sums"], V.CHDEFS_SUMS, arm)
            if side == "with":
                fig = c.steps[5]
                self.assertEqual(flag(fig["argv"], "--reported-block-name"), name, arm)
                self.assertEqual(fig["argv"].count("--reported-block-name"), 1, arm)
                self.assertEqual(flag(fig["argv"], "--prediction-set"), "gencmp-chdefs", arm)
                self.assertEqual((flag(fig["argv"], "--f0b-readout"), fig["pins"]["f0b_readout"]), (str(f0b[0]), f0b[1]),
                                 arm)
                self.assertEqual(c.steps[6]["pins"], {}, arm)

    def test_a_v_f_step_is_checked_as_soon_as_it_returns(self):
        seen = []

        def check_c(c, label, *a, **k):
            seen.append((label, [s["step"] for s in c.steps][-1]))
        c = Recorder(self.pE, self.BA / "chain.json", [], self.tmp / "preds.json")
        with mock.patch.object(V, "check_c", check_c):
            V.run_e(c, "vf-nopl", self.vf, (self.tmp / "f0b.json", "cd" * 32))
        self.assertEqual(seen, [(f"E vf-nopl {k}", k) for k in V.E_STEPS])


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

    def test_r_fires_on_an_infinity_in_place_of_a_finite_number_and_on_a_non_finite_constant(self):
        rel, pin = V.OLD_S["with"]["g"]
        g = json.loads((REPO / rel).read_text())
        g["predictions"][0]["total"]["chi2"] = float("inf")
        new = self.tmp / "g.json"
        new.write_text(json.dumps(g))                          # json writes Infinity
        with quiet(), self.assertRaises(V.Stop) as cm:
            V.check_r(self.c, "g", REPO, rel, pin, new, strings=False)
        self.assertEqual(cm.exception.control, "R")
        old = json.loads((REPO / rel).read_text())
        new_ = copy.deepcopy(old)
        new_["predictions"][0]["total"]["chi2"] = float("inf")
        self.assertTrue(V.finite_mismatch(old, new_))
        self.assertTrue(V.finite_mismatch(new_, old))
        self.assertEqual(V.finite_mismatch(old, copy.deepcopy(old)), [])

    def test_strict_decoding_refuses_every_non_finite_constant(self):
        for c in (b'{"x": Infinity}', b'{"x": -Infinity}', b'{"x": NaN}'):
            with self.assertRaises(V.Stop):
                V.load_strict(c)
        self.assertEqual(V.load_strict(b'{"x": 1.5}'), {"x": 1.5})

    def test_r_fires_on_an_overflowed_exponent_that_decodes_to_infinity(self):
        rel, pin = V.OLD_S["with"]["g"]
        old = (REPO / rel).read_text()
        chi2 = json.loads(old)["predictions"][0]["total"]["chi2"]
        new = self.tmp / "g.json"
        new.write_text(old.replace(repr(chi2), "1e999", 1))       # no Infinity constant: only finiteness can see it
        self.assertNotEqual(new.read_text(), old)
        with quiet(), self.assertRaises(V.Stop) as cm:
            V.check_r(self.c, "g", REPO, rel, pin, new, strings=False)
        self.assertEqual(cm.exception.control, "R")

    def test_r_figures_fires_on_a_committed_figure_that_is_not_e_a2s_receipt_bytes(self):
        fig = self.tmp / "fig"
        shutil.copytree(REPO / V.OLD_E_FIG, fig)
        sums = self.tmp / "sums"
        sums.write_text("".join(f"{'0' * 64}  {q.name}\n" for q in sorted(fig.iterdir())))
        with mock.patch.object(V, "OLD_E_FIG_SUMS", str(sums)), quiet(), self.assertRaises(V.Stop) as cm:
            V.check_r_figures(self.c, "E", REPO, fig)
        self.assertIn("E-A2's receipt bytes", cm.exception.args[0])

    def test_the_renderer_must_be_e_a2s(self):
        with quiet():
            have = {"python": sys.version.split()[0], "numpy": np.__version__}
            want = json.loads((REPO / V.OLD_E_FIG / "fd_g_fig_modes.json").read_text())["versions"]
            if all(have.get(k) == v for k, v in want.items() if k != "matplotlib"):
                self.skipTest("this interpreter is E-A2's")
            with self.assertRaises(V.Stop) as cm:
                V.check_renderer(self.c, REPO)
        self.assertEqual(cm.exception.control, "C")

    def test_c_requires_each_producers_structured_fields_and_its_argv_role(self):
        p = self.tmp / "g.json"
        base = ["t.py", "--extra-block-sha256", "ab" * 32, "--extra-block-key", "DeltaC_e", "--extra-block-name",
                "DeltaC_e"]
        g = {"argv": [*base, "--extra-block-role", "adopted"],
             "extra_block": {"sha256": "ab" * 32, "key": "DeltaC_e", "name": "DeltaC_e", "role": "adopted"}}
        for drop in (None, "role", "key", "name"):
            r = copy.deepcopy(g)
            if drop:
                del r["extra_block"][drop]
            p.write_text(json.dumps(r))
            if drop is None:
                with quiet():
                    V.check_c(self.c, "x", p, "ab" * 32, "DeltaC_e", {}, True, tool="fd_g_compare")
            else:
                with quiet(), self.assertRaises(V.Stop, msg=drop):
                    V.check_c(self.c, "x", p, "ab" * 32, "DeltaC_e", {}, True, tool="fd_g_compare")
        p.write_text(json.dumps({**g, "argv": base}))                # a Stage G whose argv has no role
        with quiet(), self.assertRaises(V.Stop):
            V.check_c(self.c, "x", p, "ab" * 32, "DeltaC_e", {}, True, tool="fd_g_compare")
        f = {"argv": [*base, "--extra-block-role", "adopted"], "extra_block": {"sha256": "ab" * 32, "key": "DeltaC_e",
                                                                              "name": "DeltaC_e"}}
        p.write_text(json.dumps(f))                                  # an F tool whose argv has a role
        with quiet(), self.assertRaises(V.Stop):
            V.check_c(self.c, "x", p, "ab" * 32, "DeltaC_e", {}, False, tool="fd_f0_regrade")
        p.write_text(json.dumps({"argv": base, "inputs_sha256": {}}))  # a downstream tool without inputs' block digest
        with quiet(), self.assertRaises(V.Stop):
            V.check_c(self.c, "x", p, "ab" * 32, "DeltaC_e", {}, False, tool="fd_g_diag")

    def test_the_experiment_table_must_be_the_readouts_and_the_declared_one(self):
        r, npz = self.tmp / "r.json", self.tmp / "t.npz"
        npz.write_bytes(b"table")
        r.write_text(json.dumps({"table_sha256": digest(npz)}))
        with quiet():
            V.check_table(self.c, "x", r, npz, digest(npz))
        with quiet(), self.assertRaises(V.Stop):
            V.check_table(self.c, "x", r, npz, "0" * 64)
        r.write_text(json.dumps({"table_sha256": "0" * 64}))
        with quiet(), self.assertRaises(V.Stop):
            V.check_table(self.c, "x", r, npz, digest(npz))

    def test_r_fires_on_a_committed_file_that_is_not_its_pin(self):
        rel, _ = V.OLD_S["with"]["g"]
        with quiet(), self.assertRaises(V.Stop):
            V.check_r(self.c, "g", REPO, rel, "0" * 64, REPO / rel, strings=False)

    def test_s_and_c_hold_on_a_consistent_readout_and_fire_otherwise(self):
        t = ProductTree(self.tmp / "t")
        blk = A.load_npz(t.npz)
        with quiet():
            V.check_s(self.c, "x", t.g, None, blk, "with")
            V.check_c(self.c, "x", t.g, digest(t.npz), V.SIDE_KEY["with"], {}, True, tool="fd_g_compare")
        with quiet(), self.assertRaises(V.Stop) as cm:
            V.check_s(self.c, "x", t.g, None, blk, "nopl")        # the nopl matrix's sigma is smaller
        self.assertEqual(cm.exception.control, "S")
        with quiet(), self.assertRaises(V.Stop) as cm:
            V.check_c(self.c, "x", t.g, "0" * 64, V.SIDE_KEY["with"], {}, True, tool="fd_g_compare")
        self.assertEqual(cm.exception.control, "C")
        with quiet(), self.assertRaises(V.Stop) as cm:            # the readout records the reported key, not nopl's
            V.check_c(self.c, "x", t.g, digest(t.npz), V.SIDE_KEY["nopl"], {}, True, tool="fd_g_compare")
        with quiet(), self.assertRaises(V.Stop) as cm:            # a Stage G records a role; an F tool records none
            V.check_c(self.c, "x", t.g, digest(t.npz), V.SIDE_KEY["with"], {}, False, tool="fd_g_compare")
        self.assertEqual(cm.exception.control, "C")

    def test_s_fires_on_an_f0b_whose_sigma_is_not_the_revised_matrix(self):
        t = ProductTree(self.tmp / "t2")
        blk = A.load_npz(t.npz)
        sig = (np.sqrt(np.diag(blk[V.REPORTED_F])) / blk["f"]).tolist()
        f0b = self.tmp / "f0b.json"
        f0b.write_text(json.dumps({"relative_sigma_plus_C_resp + C_PL5D + DeltaC_e": {"C_total": sig}}))
        with quiet():
            V.check_s(self.c, "x", t.g, f0b, blk, "with")
        f0b.write_text(json.dumps({"relative_sigma_plus_C_resp + C_PL5D + DeltaC_e": {"C_total": [x * 1.001 for x in sig]}}))
        with quiet(), self.assertRaises(V.Stop) as cm:
            V.check_s(self.c, "x", t.g, f0b, blk, "with")
        self.assertEqual(cm.exception.control, "S")

    def test_s_fires_on_a_stage_g_without_its_five_predictions(self):
        t = ProductTree(self.tmp / "t3")
        blk = A.load_npz(t.npz)
        t.write_g(lambda g: g.update(predictions=[]))
        with quiet(), self.assertRaises(V.Stop) as cm:
            V.check_s(self.c, "x", t.g, None, blk, "with")
        self.assertEqual(cm.exception.control, "S")

    def test_r_figures_holds_on_the_committed_figures_and_fires_on_a_changed_pdf(self):
        fig = self.tmp / "fig"
        shutil.copytree(REPO / V.OLD_E_FIG, fig)
        js = json.loads((fig / "fd_g_fig_ratio.json").read_text())
        js["argv"] = ["moved"]
        (fig / "fd_g_fig_ratio.json").write_text(json.dumps(js))
        with quiet():
            V.check_r_figures(self.c, "E", REPO, fig)
        (fig / "fd_g_fig_modes.pdf").write_bytes((fig / "fd_g_fig_modes.pdf").read_bytes() + b"\n")
        with quiet(), self.assertRaises(V.Stop) as cm:
            V.check_r_figures(self.c, "E", REPO, fig)
        self.assertEqual(cm.exception.control, "R")

    def test_c_fires_on_an_upstream_digest_that_is_not_the_written_one(self):
        p = self.tmp / "r.json"
        argv = ["t.py", "--extra-block-sha256", "ab" * 32, "--extra-block-key", "DeltaC_e", "--extra-block-name", "DeltaC_e"]
        r = {"argv": argv, "inputs_sha256": {"extra_block": "ab" * 32, "g_readout": "11" * 32},
             "referenced": {"g_readout": "11" * 32}}
        p.write_text(json.dumps(r))
        with quiet():
            V.check_c(self.c, "x", p, "ab" * 32, "DeltaC_e", {"g_readout": "11" * 32}, False)
        with quiet(), self.assertRaises(V.Stop):
            V.check_c(self.c, "x", p, "ab" * 32, "DeltaC_e", {"g_readout": "22" * 32}, False)
        p.write_text(json.dumps({**r, "referenced": {"g_readout": "33" * 32}}))      # a duplicate reference differs
        with quiet(), self.assertRaises(V.Stop):
            V.check_c(self.c, "x", p, "ab" * 32, "DeltaC_e", {"g_readout": "11" * 32}, False)
        p.write_text(json.dumps({**r, "argv": [*argv, "--extra-block-sha256", "cd" * 32]}))  # argv names two digests
        with quiet(), self.assertRaises(V.Stop):
            V.check_c(self.c, "x", p, "ab" * 32, "DeltaC_e", {"g_readout": "11" * 32}, False)
        p.write_text(json.dumps({**r, "inputs_sha256": {"g_readout": "11" * 32}}))  # no digest field for the block
        with quiet(), self.assertRaises(V.Stop):
            V.check_c(self.c, "x", p, "ab" * 32, "DeltaC_e", {"g_readout": "11" * 32}, False)
        p.write_text(json.dumps({**r, "extra_block": {"sha256": None}}))            # a null second digest
        with quiet(), self.assertRaises(V.Stop):
            V.check_c(self.c, "x", p, "ab" * 32, "DeltaC_e", {"g_readout": "11" * 32}, False)
        p.write_text(json.dumps({**r, "referenced": {}}))                           # a required duplicate missing
        with quiet():
            V.check_c(self.c, "x", p, "ab" * 32, "DeltaC_e", {"g_readout": "11" * 32}, False)
        with quiet(), self.assertRaises(V.Stop):
            V.check_c(self.c, "x", p, "ab" * 32, "DeltaC_e", {"g_readout": "11" * 32}, False, required=("g_readout",))
        g = {**r, "argv": [*argv, "--extra-block-role", "adopted"], "extra_block": {"sha256": "ab" * 32, "role": "variant"}}
        p.write_text(json.dumps(g))                                                 # a recorded role that is not argv's
        with quiet(), self.assertRaises(V.Stop):
            V.check_c(self.c, "x", p, "ab" * 32, "DeltaC_e", {"g_readout": "11" * 32}, True)
        g["extra_block"]["role"] = "adopted"
        p.write_text(json.dumps(g))
        with quiet():
            V.check_c(self.c, "x", p, "ab" * 32, "DeltaC_e", {"g_readout": "11" * 32}, True)


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
        for rel, _ in [V.OLD_F0, (V.CHDEFS_SPEC, None),
                       *[v for s in (V.OLD_S, V.OLD_E) for arm in s.values() for v in arm.values()]]:
            (self.D / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(REPO / rel, self.D / rel)
        (self.tmp / "E/pred").mkdir(parents=True)
        (self.tmp / "E/pred/SHA256SUMS").write_text("staged\n")
        self.calls = []
        self.fail_pd = False

    def old_pd(self, *a, **k):
        self.calls.append(("old_product_deposit", "old-with"))
        if self.fail_pd:
            raise V.Stop("R", "R deposit deposit.json")

    def recorder_run(self, chain, name, arm, tool, argv, outputs, timeout, pins=None, variant=""):
        self.calls.append((name, arm))
        for q in outputs:
            Path(q).parent.mkdir(parents=True, exist_ok=True)
            src = self.tmp / "blk" / Path(q).name
            Path(q).write_bytes(src.read_bytes() if src.exists() else b"{}")
        return {}

    def run_chain(self, fail_label, check_r=None, sums=None):
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
                   mock.patch.object(V, "run_f0", lambda c, arm, vf: (self.calls.append(("f0", arm)),
                                                                      (self.tmp, self.tmp))[1]),
                   mock.patch.object(V, "run_s", lambda c, arm, vf, f: (self.calls.append(("S", arm)),
                                                                        {k: self.tmp for k in
                                                                         (*V.S_STEPS, "f0b_npz", "f1_npz")})[1]),
                   mock.patch.object(V, "check_table", lambda *x, **k: None),
                   mock.patch.object(V, "check_renderer", lambda *x, **k: None),
                   mock.patch.dict(os.environ, {}),
                   mock.patch.object(V, "CHDEFS_SUMS", sums or digest(self.tmp / "E/pred/SHA256SUMS")),
                   mock.patch.object(V, "run_e", lambda c, arm, vf, f: (self.calls.append(("E", arm)),
                                                                        {"out": {k: self.tmp for k in V.E_STEPS},
                                                                         "H": {}, "fig": self.tmp})[1]),
                   mock.patch("fd_gencmp_e.load_chdefs", lambda p: json.loads((REPO / V.CHDEFS_SPEC).read_text())),
                   mock.patch.object(V, "old_product_deposit", self.old_pd),
                   mock.patch.object(V, "vf_arms", lambda *x, **k: self.calls.append(("vf_arms", "vf-all")))]
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

    def test_every_old_control_passing_reaches_the_v_f_part_last(self):
        self.calls = []
        self.assertEqual(self.run_chain(None), 0)
        order = [c[0] for c in self.calls if c[0] in ("f0", "S", "E", "old_product_deposit", "vf_arms")]
        self.assertEqual(order, ["f0", "S", "E", "S", "E", "old_product_deposit", "vf_arms"])

    def test_a_failed_product_or_deposit_control_stops_before_the_v_f_part(self):
        self.calls = []
        self.fail_pd = True
        self.assertEqual(self.run_chain(None), 1)
        self.assertNotIn(("vf_arms", "vf-all"), self.calls)
        self.assertIn(("old_product_deposit", "old-with"), self.calls)

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

    def test_a_staged_manifest_that_is_not_the_recorded_one_refuses_before_any_step(self):
        self.calls = []
        self.assertEqual(self.run_chain(None, sums="0" * 64), 1)
        self.assertEqual([c for c in self.calls if c[0] in ("f0", "S", "E")], [])

    def test_matplotlib_and_temporary_files_stay_under_the_run_directory(self):
        self.calls = []
        self.assertEqual(self.run_chain(None), 0)
        self.assertEqual(os.environ["MPLCONFIGDIR"], str((self.tmp / "BA" / "mpl").resolve()))
        self.assertEqual(os.environ["TMPDIR"], str((self.tmp / "BA" / "tmp").resolve()))

    def test_a_predictions_specification_that_is_not_the_committed_one_refuses_before_any_step(self):
        spec = json.loads((REPO / V.CHDEFS_SPEC).read_text())
        spec[0]["sha256"] = "0" * 64
        self.calls = []
        with mock.patch("fd_gencmp_e.load_chdefs", lambda p: spec):
            a = V.build_args(["chain", "--run-dir", str(self.tmp / "BA"), "--run-e", str(self.tmp / "E"),
                              "--scratch", str(self.tmp / "P")])
            self.run_chain(None)        # starts the patches (this run passes); then the second run with the bad spec
        shutil.rmtree(self.tmp / "BA")
        self.calls = []
        with mock.patch("fd_gencmp_e.load_chdefs", lambda p: spec), quiet(), mock.patch("sys.stderr"):
            self.assertEqual(V.run(a), 1)
        self.assertEqual([c for c in self.calls if c[0] in ("f0", "S", "E")], [])

    def test_an_existing_logs_directory_refuses(self):
        (self.tmp / "BA" / "logs").mkdir(parents=True)
        self.assertEqual(self.run_chain(None), 1)
        self.assertEqual(self.calls, [])

    def test_an_existing_run_directory_refuses(self):
        (self.tmp / "BA" / "S").mkdir(parents=True)
        self.assertEqual(self.run_chain(None), 1)
        self.assertEqual(self.calls, [])


FAKE = """import argparse, json, sys
def build_args(argv):
    ap = argparse.ArgumentParser(); ap.add_argument("--out"); return ap.parse_args(argv)
def run(a, pins=None, predictions=None, variant=None):
    open(a.out, "w").write(json.dumps({"pins": pins, "predictions": predictions, "argv": sys.argv}))
    return 0
def main():
    a = build_args(sys.argv[1:]); open(a.out, "w").write(json.dumps({"cli": True, "argv": sys.argv})); return 0
if __name__ == "__main__":
    sys.exit(main())
"""


class Runner(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="vf-run-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        (self.tmp / "D/nd-unfolding").mkdir(parents=True)
        for n in ("fake_tool.py", f"{V.CLI_ONLY}.py"):
            (self.tmp / "D/nd-unfolding" / n).write_text(FAKE)
        self.BA = self.tmp / "BA"
        for d in ("logs", "pins"):
            (self.BA / d).mkdir(parents=True)
        self.preds = self.tmp / "preds.json"
        self.preds.write_text(json.dumps([{"name": "x"}]))
        self.c = V.Chain(A.Paths(self.tmp / "D", self.tmp / "P", self.BA), self.BA / "chain.json", [], self.preds)

    def test_pins_and_the_prediction_set_reach_the_tool_in_process(self):
        out = self.BA / "o.json"
        with quiet():
            self.c.run("s", "E-vf-with", "fake_tool", ["--out", str(out)], [out], 30, pins={"g_readout": "ab" * 32})
        got = json.loads(out.read_text())
        self.assertEqual(got["pins"], {"g_readout": "ab" * 32})
        self.assertEqual(got["predictions"], [{"name": "x"}])

    def test_the_figures_check_runs_as_its_cli_even_with_pins(self):
        out = self.BA / "o.json"
        with quiet():
            self.c.run("figures_check", "E-vf-with", V.CLI_ONLY, ["--out", str(out)], [out], 30, pins={})
        self.assertTrue(json.loads(out.read_text())["cli"])

    def test_a_nonzero_exit_or_a_missing_output_stops(self):
        with quiet(), self.assertRaises(V.Stop):
            self.c.run("s", "x", "fake_tool", ["--out", str(self.BA / "o.json")], [self.BA / "missing.json"], 30)


class VfArms(unittest.TestCase):
    def test_the_v_f_part_runs_f0_both_sides_the_product_the_deposit_and_the_table_in_order(self):
        tmp = Path(tempfile.mkdtemp(prefix="vf-arms2-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        BA = tmp / "BA"
        for d in ("logs", "pins"):
            (BA / d).mkdir(parents=True)
        cS = Recorder(A.Paths(REPO, tmp / "P", BA), BA / "chain.json", [])
        cE = Recorder(A.Paths(REPO, tmp / "P", BA), BA / "chain.json", cS.steps)
        seen = []

        def made(c, name):
            q = tmp / f"{name}.json"
            q.write_text(json.dumps({"name": name}))
            c.steps.append({"step": name, "outputs": {str(q): digest(q)}})
            return q

        def f0(c, arm, vf):
            seen.append(("f0", arm))
            return made(c, f"{arm}-f0"), made(c, f"{arm}-f0npz")

        def s_(c, arm, vf, f):
            seen.append(("S", arm, f))
            return {k: made(c, f"{arm}-{k}") for k in (*V.S_STEPS, "f0b_npz", "f1_npz")}

        def e_(c, arm, vf, f):
            seen.append(("E", arm, f[0].name))
            out = {k: made(c, f"E-{arm}-{k}") for k in V.E_STEPS}
            return {"out": out, "H": {k: digest(v) for k, v in out.items()}, "fig": None}
        tables = {"f0": "t0", **{f"{s}/{k}": "t" for s in ("with", "nopl") for k in ("f0b", "f1")}}
        with mock.patch.object(V, "run_f0", f0), mock.patch.object(V, "run_s", s_), mock.patch.object(V, "run_e", e_), \
             mock.patch.object(V, "check_table", lambda *x, **k: None), mock.patch.object(V, "check_s", lambda *x, **k: None):
            V.vf_arms(cS, cE, REPO, BA, {"npz": tmp / "vf_block.npz", "sha": "ab" * 32, "json_sha": "cd" * 32}, {}, tables)
        self.assertEqual(seen, [("f0", "vf-f0"), ("S", "vf-with", None), ("E", "vf-with", "vf-with-f0b.json"),
                                ("S", "vf-nopl", None), ("E", "vf-nopl", "vf-nopl-f0b.json")])
        run = [s for s in cS.steps if "tool" in s]
        self.assertEqual([s["step"] for s in run], ["data_product", "deposit_build", "deposit_check", "table"])
        self.assertEqual([s["variant"] for s in run[1:3]], ["with-vf", "with-vf"])
        self.assertEqual(run[0]["pins"]["block_json"], "cd" * 32)
        pairs = json.loads((BA / "pins/table-pairs.json").read_text())
        self.assertEqual(len(pairs), 1 + 2 * (len(V.S_STEPS) + len(V.E_STEPS)))
        self.assertEqual(pairs[0][1:3], [str(REPO / V.OLD_F0[0]), V.OLD_F0[1]])
        self.assertEqual(pairs[0][4], digest(tmp / "vf-f0-f0.json"))
        self.assertEqual(run[3]["pins"][pairs[1][1]], V.OLD_S["with"]["f0b"][1])


class OldProductDeposit(unittest.TestCase):
    """The OLD product and deposit, run for real by their own tools on the committed inputs (all committed)."""

    def test_the_committed_with_block_product_and_deposit_are_reproduced_and_checked_as_recorded(self):
        tmp = Path(tempfile.mkdtemp(prefix="vf-oldpd-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        BA = tmp / "BA"
        for d in ("logs", "pins"):
            (BA / d).mkdir(parents=True)
        c = V.Chain(A.Paths(REPO, tmp / "P", BA), BA / "chain.json", [])
        with quiet():
            V.old_product_deposit(c, REPO, c.p, BA)
        self.assertEqual([s["step"] for s in c.steps if "tool" in s], ["data_product", "deposit_build", "deposit_check"])
        self.assertTrue(all(s["ok"] for s in c.steps if s.get("check")))
        self.assertEqual(sum(1 for s in c.steps if s.get("check") and "5B receipt" in s["step"]), 5)


class OldDepositReceipt(unittest.TestCase):
    def test_a_committed_deposit_file_that_is_not_the_5b_receipts_refuses(self):
        self.assertEqual(sorted(V.deposit_receipt_sums(REPO)), sorted((*DC.FILES, DC.REFERENCE)))
        tmp = Path(tempfile.mkdtemp(prefix="vf-dep5b-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        BA = tmp / "BA"
        for d in ("logs", "pins"):
            (BA / d).mkdir(parents=True)
        c = V.Chain(A.Paths(REPO, tmp / "P", BA), BA / "chain.json", [])
        wrong = {n: "0" * 64 for n in (*DC.FILES, DC.REFERENCE)}
        with mock.patch.object(V, "deposit_receipt_sums", lambda D: wrong), quiet(), self.assertRaises(V.Stop) as cm:
            V.old_product_deposit(c, REPO, c.p, BA)
        self.assertIn("5B receipt", cm.exception.args[0])


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
