"""Tests of fd_cpl_addition.py (FD-CT-5B-ADDITION-DECLARATION.md) and of the three tools it parametrizes: each
check is shown both to fire on the defect it guards and to stay silent on the good case."""
from __future__ import annotations

import copy
import json
import re
import shutil
import subprocess
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
import fd_flux_boot as FB  # noqa: E402
import fd_g_compare as G  # noqa: E402
import fd_g_figures as FIG  # noqa: E402
import s1_assemble as sa  # noqa: E402
from test_fd_g_compare import digest  # noqa: E402

REPO = ND.parent
FDP = REPO / A.FD
AUDIT = FDP / "fd/readout/fd_ct_5b_audit.json"
CELLS = A.CELLS


def quiet():
    return mock.patch("sys.stdout")


def run_quiet(fn, *a, **kw):
    with quiet():
        return fn(*a, **kw)


# ------------------------------------------------------------------------------------------------ pure parts

class Npz(unittest.TestCase):
    def test_the_same_arrays_give_the_same_bytes_and_np_load_reads_them(self):
        arr = {"f": np.arange(16.0) + 1, "M": np.eye(16) * 3.5}
        b1, b2 = A.npz_bytes(arr), A.npz_bytes(copy.deepcopy(arr))
        self.assertEqual(b1, b2)
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        (tmp / "x.npz").write_bytes(b1)
        back = A.load_npz(tmp / "x.npz")
        self.assertEqual(list(back), ["f", "M"])
        self.assertTrue(all(np.array_equal(back[k], arr[k]) for k in arr))

    def test_another_process_writes_the_same_bytes(self):
        arr = {"f": np.linspace(1, 2, 16)}
        code = (f"import sys; sys.path.insert(0, {str(ND)!r}); import numpy as np, hashlib, fd_cpl_addition as A; "
                "print(hashlib.sha256(A.npz_bytes({'f': np.linspace(1, 2, 16)})).hexdigest())")
        r = subprocess.run([sys.executable, "-I", "-B", "-c", code], capture_output=True, text=True, check=True)
        import hashlib
        self.assertEqual(r.stdout.strip(), hashlib.sha256(A.npz_bytes(arr)).hexdigest())

    def test_a_different_array_gives_different_bytes(self):
        a = {"f": np.ones(16)}
        b = {"f": np.ones(16) * (1 + 1e-15)}
        self.assertNotEqual(A.npz_bytes(a), A.npz_bytes(b))


class Compare(unittest.TestCase):
    """Control R's comparison, in both directions, on a committed readout."""

    def setUp(self):
        self.old = json.loads((FDP / "fd/readout/fd_g_readout.json").read_text())

    def test_a_readout_equals_itself(self):
        self.assertEqual(A.compare_numbers(self.old, copy.deepcopy(self.old)), [])

    def test_a_changed_number_is_found_and_a_last_bit_is_not(self):
        new = copy.deepcopy(self.old)
        new["predictions"][2]["total"]["chi2"] *= 1 + 1e-9
        bad = A.compare_numbers(self.old, new)
        self.assertEqual(len(bad), 1)
        self.assertIn("/predictions/2/total/chi2", bad[0])
        new = copy.deepcopy(self.old)
        new["predictions"][2]["total"]["chi2"] *= 1 + 1e-15
        self.assertEqual(A.compare_numbers(self.old, new), [])

    def test_a_changed_structure_is_found(self):
        new = copy.deepcopy(self.old)
        new["predictions"][0]["extra"] = "a string, so that only the structure differs"
        self.assertEqual([b for b in A.compare_numbers(self.old, new)], ["structure /predictions/0"])
        new = copy.deepcopy(self.old)
        new["predictions"][0]["f"].append(1.0)
        self.assertTrue(A.compare_numbers(self.old, new))

    def test_a_bool_and_a_null_are_compared_by_type(self):
        self.assertFalse(A.same_number(True, 1))
        self.assertFalse(A.same_number(None, 0))
        self.assertTrue(A.same_number(None, None))
        self.assertFalse(A.same_number(float("nan"), float("nan")))

    def test_argv_and_code_digests_are_excluded_but_named(self):
        new = copy.deepcopy(self.old)
        new["argv"] = ["elsewhere"]
        new["code_sha256"] = {"x": "y"}
        self.assertEqual(A.compare_numbers(self.old, new), [])
        self.assertEqual(A.compare_strings(self.old, new, ("/argv", "/code_sha256")), [])
        self.assertTrue(A.compare_strings(self.old, new, ("/argv",)))

    def test_strings_are_compared_outside_the_exclusions(self):
        new = copy.deepcopy(self.old)
        new["labels"]["what"] += " "
        self.assertEqual(A.compare_numbers(self.old, new), [])
        self.assertEqual(A.compare_strings(self.old, new, ()), ["string /labels/what"])

    def test_the_figure_sidecar_exclusion_is_argv_code_and_versions_only(self):
        self.assertEqual(A.FIG_EXCLUDE, ("/argv", "/code", "/versions"))
        side = json.loads((FDP / "fd/figures/fd_g_fig_ratio.json").read_text())
        new = copy.deepcopy(side)
        new["pdf_sha256"] = "0" * 64
        self.assertEqual(A.compare_strings(side, new, A.FIG_EXCLUDE), ["string /pdf_sha256"])
        new = copy.deepcopy(side)
        new["code"]["commit"] = "x"
        new["versions"]["numpy"] = "0"
        self.assertEqual(A.compare_strings(side, new, A.FIG_EXCLUDE), [])

    def test_pairing_renames_the_blocks_key(self):
        old = {"relative_sigma_plus_C_resp": {"C_total": [1.0, 2.0]}, "x": 3}
        new = {f"relative_sigma_plus_{A.NAME}": {"C_total": [1.5, 2.5]}, "x": 4}
        self.assertEqual(list(A.paired(old, new)), [("/relative_sigma_plus_C_resp/C_total/0", 1.0, 1.5),
                                                     ("/relative_sigma_plus_C_resp/C_total/1", 2.0, 2.5),
                                                     ("/x", 3, 4)])


class Labels(unittest.TestCase):
    def test_every_context_number_is_the_committed_audit_readouts(self):
        au = json.loads(AUDIT.read_text())
        with quiet():
            A.check_labels(A.LABELS, au)
        self.assertEqual(A.context_numbers(au)["context_dr_pair"], ["GEANT_Pion#1", "meson#1", "0.853", "0.560",
                                                                    "0.617", "1.51"])
        self.assertEqual(A.context_numbers(au)["context_5a_5b"], ["-2.724%", "-2.699%", "+4.671%", "+4.806%",
                                                                  "81.6", "192.8"])

    def test_a_context_number_that_is_not_the_audits_fires_L(self):
        au = json.loads(AUDIT.read_text())
        bad = dict(A.LABELS, context_5a_5b=A.LABELS["context_5a_5b"].replace("81.6", "81.7"))
        with quiet(), mock.patch.dict(A.LABELS, bad), self.assertRaises(A.Stop) as cm:
            A.check_labels(bad, au)
        self.assertEqual(cm.exception.control, "L")

    def test_two_numbers_swapped_between_periods_fire_L(self):
        au = json.loads(AUDIT.read_text())
        t = A.LABELS["context_5a_5b"]
        bad = dict(A.LABELS, context_5a_5b=t.replace("81.6", "@").replace("192.8", "81.6").replace("@", "192.8"))
        with quiet(), mock.patch.dict(A.LABELS, bad), self.assertRaises(A.Stop) as cm:
            A.check_labels(bad, au)
        self.assertIn("out of order", str(cm.exception))

    def test_a_missing_decision_label_fires_L(self):
        au = json.loads(AUDIT.read_text())
        labels = {k: v for k, v in A.LABELS.items() if k != "decision"}
        with quiet(), self.assertRaises(A.Stop):
            A.check_labels(labels, au)

    def test_a_context_not_marked_descriptive_fires_L(self):
        au = json.loads(AUDIT.read_text())
        bad = dict(A.LABELS, context_dr_pair=A.LABELS["context_dr_pair"].replace("descriptive; ", ""))
        with quiet(), mock.patch.dict(A.LABELS, bad), self.assertRaises(A.Stop):
            A.check_labels(bad, au)


# ------------------------------------------------------------------------------------------------ the block

def spd(rng, n=16, scale=1.0):
    X = rng.normal(0, 1, (n, n))
    return scale * (X @ X.T / n + 0.5 * np.eye(n))


class BlockTree:
    """S1's and C_resp's npz, a 5B readout with a rank-2 P, and the committed audit readout re-pointed at them."""

    def __init__(self, root: Path, seed: int = 0, P_mutate=None, per_mutate=None, audit_mutate=None,
                 cresp_mutate=None):
        self.root = root
        root.mkdir(parents=True, exist_ok=True)
        rng = np.random.default_rng(seed)
        f = rng.uniform(1, 5, 16) * 1e-39
        ff = np.outer(f, f)
        Ce, Cm, Cr = spd(rng, scale=4e-3) * ff, spd(rng, scale=1e-3) * ff, spd(rng, scale=4e-4) * ff
        Ct = Ce + Cm
        self.s1_npz, self.cresp_npz = root / "s1.npz", root / "cresp.npz"
        np.savez(self.s1_npz, f=f, C_e=Ce, C_model_abs=Cm, C_total=Ct)
        Ctr = Ct + Cr
        if cresp_mutate:
            Ctr = cresp_mutate(Ctr.copy())
        np.savez(self.cresp_npz, C_resp=Cr, C_total_resp=Ctr)
        g1, g2 = rng.normal(0, 0.03, 16), rng.normal(0, 0.02, 16)
        P = 0.6 * np.outer(g1, g1) + 0.3 * np.outer(g2, g2)
        if P_mutate:
            P = P_mutate(P)
        M = (Ct + Cr) / ff
        self.per = {"cells": CELLS, "inputs_sha256": {"s1_npz": digest(self.s1_npz), "cresp": digest(self.cresp_npz)},
                    "C_PL5D": {"C_PL5D_rel": P.tolist(), "sigma_rel": np.sqrt(np.clip(np.diag(P), 0, None)).tolist(),
                               "trace_share": float(np.trace(P) / np.trace(M + P))}}
        if per_mutate:
            per_mutate(self.per)
        self.periods = root / "periods.json"
        self.periods.write_text(json.dumps(self.per))
        au = json.loads(AUDIT.read_text())
        au["inputs_sha256"].update(readout_5b=digest(self.periods), s1_npz=digest(self.s1_npz),
                                   cresp=digest(self.cresp_npz))
        if audit_mutate:
            audit_mutate(au)
        self.audit = root / "audit.json"
        self.audit.write_text(json.dumps(au))
        self.f, self.P, self.Cr, self.Ct = f, P, Cr, Ct
        self.pins = {**A.PINS, "audit": digest(self.audit), "periods": digest(self.periods),
                     "s1_npz": digest(self.s1_npz), "cresp_npz": digest(self.cresp_npz)}

    def argv(self, out: Path) -> list:
        return ["block", "--audit-json", str(self.audit), "--periods-json", str(self.periods), "--s1-npz",
                str(self.s1_npz), "--cresp-npz", str(self.cresp_npz), "--out-dir", str(out)]

    def run(self, out: Path, pins=None) -> int:
        with quiet(), mock.patch.dict(A.PINS, pins or self.pins):
            return A.run(A.build_args(self.argv(out)))


class Block(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="cpl-block-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def refuses(self, tree: BlockTree, control: str, pins=None):
        out = self.tmp / "out"
        with mock.patch("sys.stderr") as err:
            rc = tree.run(out, pins)
        self.assertEqual(rc, 1)
        msg = "".join(str(c.args[0]) for c in err.write.call_args_list)
        self.assertIn(f"[STOP] {control}:", msg)
        self.assertFalse((out / "cpl_block.npz").exists() or (out / "cpl_block.json").exists(), "it wrote")
        return msg

    def test_the_block_is_written_as_declared_and_reproduced(self):
        t = BlockTree(self.tmp / "t")
        self.assertEqual(t.run(self.tmp / "o1"), 0)
        self.assertEqual(t.run(self.tmp / "o2"), 0)
        z = A.load_npz(self.tmp / "o1/cpl_block.npz")
        ff = np.outer(t.f, t.f)
        self.assertEqual(list(z), ["f", "P_rel", "C_PL5D", "C_resp", A.XKEY, A.REPORTED])
        np.testing.assert_array_equal(z["P_rel"], t.P)
        np.testing.assert_array_equal(z["C_PL5D"], ff * t.P)
        np.testing.assert_array_equal(z[A.XKEY], t.Cr + ff * t.P)
        np.testing.assert_allclose(z[A.REPORTED], t.Ct + t.Cr + ff * t.P, rtol=1e-13)
        self.assertEqual(digest(self.tmp / "o1/cpl_block.npz"), digest(self.tmp / "o2/cpl_block.npz"))
        js = json.loads((self.tmp / "o1/cpl_block.json").read_text())
        self.assertEqual(js["npz"]["sha256"], digest(self.tmp / "o1/cpl_block.npz"))
        self.assertEqual(js["rank"], 2)
        self.assertEqual(js["controls_passed"], ["A", "L", "B0", "B1", "B2", "B3"])
        self.assertEqual({k: js["labels"][k] for k in ("block", "decision")},
                         {k: A.LABELS[k] for k in ("block", "decision")})

    def test_a_stop_that_fired_refuses(self):
        self.refuses(BlockTree(self.tmp / "t", audit_mutate=lambda au: au["stop_condition"].update(stop=True)), "A")

    def test_an_audit_on_another_5b_readout_refuses(self):
        self.refuses(BlockTree(self.tmp / "t", audit_mutate=lambda au: au["inputs_sha256"].update(
            readout_5b="0" * 64)), "A")

    def test_a_stop_condition_with_a_clause_named_refuses(self):
        self.refuses(BlockTree(self.tmp / "t", audit_mutate=lambda au: au["stop_condition"].update(which=["O"])), "A")

    def test_a_5b_readout_on_another_s1_refuses(self):
        self.refuses(BlockTree(self.tmp / "t", per_mutate=lambda per: per["inputs_sha256"].update(s1_npz="3" * 64)),
                     "A")

    def test_a_cresp_whose_total_is_not_its_parts_refuses_b2(self):
        def m(C):
            C[3, 3] *= 1 + 1e-9
            return C
        msg = self.refuses(BlockTree(self.tmp / "t", cresp_mutate=m), "B2")
        self.assertIn("cresp.npz's C_total_resp + C_PL5D", msg)

    def test_a_pin_that_is_not_the_files_refuses(self):
        t = BlockTree(self.tmp / "t")
        self.refuses(t, "B0", pins={**t.pins, "cresp_npz": "1" * 64})

    def test_a_rank_three_block_refuses(self):
        rng = np.random.default_rng(9)
        g3 = rng.normal(0, 0.01, 16)
        self.refuses(BlockTree(self.tmp / "t", P_mutate=lambda P: P + np.outer(g3, g3)), "B1")

    def test_a_sigma_that_is_not_the_5b_readouts_refuses(self):
        def m(per):
            per["C_PL5D"]["sigma_rel"][3] *= 1 + 1e-9
        self.refuses(BlockTree(self.tmp / "t", per_mutate=m), "B1")

    def test_a_trace_share_that_is_not_the_5b_readouts_refuses(self):
        def m(per):
            per["C_PL5D"]["trace_share"] *= 1 + 1e-6
        self.refuses(BlockTree(self.tmp / "t", per_mutate=m), "B1")

    def test_an_asymmetric_block_refuses(self):
        # antisymmetric, so (P + P^T)/2 is still rank 2 and only the symmetry check can see it
        def m(P):
            P = P.copy()
            d = 1e-6 * np.abs(P).max()
            P[0, 1] += d
            P[1, 0] -= d
            return P
        msg = self.refuses(BlockTree(self.tmp / "t", P_mutate=m), "B1")
        self.assertIn("P is symmetric", msg)

    def test_an_existing_output_refuses(self):
        t = BlockTree(self.tmp / "t")
        (self.tmp / "out").mkdir()
        (self.tmp / "out/cpl_block.json").write_text("{}")
        with mock.patch("sys.stderr"):
            self.assertEqual(t.run(self.tmp / "out"), 1)
        self.assertEqual((self.tmp / "out/cpl_block.json").read_text(), "{}")


# ------------------------------------------------------------------------------------------------ the product

class ProductTree(BlockTree):
    """BlockTree, its block, a committed-like data product (the committed one's cells and boxes) and a Stage G
    readout on the block, with every prediction's chi2 by Stage G's compare()."""

    def __init__(self, root: Path, seed: int = 0, g_mutate=None, dp_mutate=None):
        super().__init__(root, seed)
        self.blk = root / "block"
        assert self.run(self.blk) == 0
        z = A.load_npz(self.blk / "cpl_block.npz")
        dpc = json.loads((FDP / "fd/data-product/fd_data_product.json").read_text())
        with np.load(self.s1_npz) as s1:
            Ce, Cm = s1["C_e"], s1["C_model_abs"]
        M = self.Ct + self.Cr
        dp = {"controls_passed": ["Q0", "Q1", "Q2", "Q3", "Q4", "Q5", "Q6"], "labels": dpc["labels"],
              "inputs_sha256": {"s1_npz": self.pins["s1_npz"], "cresp_npz": self.pins["cresp_npz"]},
              "cells": dpc["cells"], "h2": dpc["h2"], "f": self.f.tolist(),
              "matrices": {"C_e": Ce.tolist(), "C_model_abs": Cm.tolist(), "C_resp": self.Cr.tolist(),
                           A.WITHOUT: M.tolist()},
              "relative_sigma": {A.WITHOUT: (np.sqrt(np.diag(M)) / self.f).tolist()}}
        if dp_mutate:
            dp_mutate(dp)
        self.dp = root / "dp.json"
        self.dp.write_text(json.dumps(dp))
        rep = z[A.REPORTED]
        sig = np.sqrt(np.diag(rep)) / self.f
        rng = np.random.default_rng(seed + 50)
        preds = []
        for spec in G.PREDICTIONS:
            idx = list(range(16)) if spec["cells"] == "all" else list(G.GIBUU_CELLS)
            g = np.zeros(16)
            g[idx] = self.f[idx] * (1 + rng.normal(0, 0.1, len(idx)))
            sv = rng.uniform(0.001, 0.01, len(idx))
            Vg = np.zeros(16)
            Vg[idx] = (sv * self.f[idx]) ** 2
            cmp = G.compare(self.f, g, Vg, rep, idx, f"C_total + {A.NAME}")
            preds.append({"name": spec["name"], "file": spec["path"], "sha256": spec["sha256"], "label": spec["label"],
                          "cells": [CELLS[i] for i in idx], "reported_covariance": f"C_total + {A.NAME}",
                          "f": self.f[idx].tolist(), "g": g[idx].tolist(), "sigma_Vg_over_f": sv.tolist(),
                          "sigma_total_over_f": sig[idx].tolist(),
                          **{k: {"chi2": cmp[k]["chi2"], "ndf": cmp[k]["ndf"], "p": 0.5, "matrix": cmp[k]["matrix"]}
                             for k in ("total", "shape_only")}})
        gr = {"schema": "fd-g-readout/2", "cells": CELLS, "predictions": preds,
              "extra_block": {"name": A.NAME, "key": A.XKEY, "role": "adopted",
                              "sha256": digest(self.blk / "cpl_block.npz")},
              "inputs_sha256": {"s1_npz": self.pins["s1_npz"]}}
        if g_mutate:
            g_mutate(gr)
        self.g = root / "g.json"
        self.g.write_text(json.dumps(gr))
        self.ppins = {"data_product": digest(self.dp), "block_npz": digest(self.blk / "cpl_block.npz"),
                      "block_json": digest(self.blk / "cpl_block.json"), "g_readout": digest(self.g),
                      "audit_json": self.pins["audit"]}

    def pargv(self, out: Path) -> list:
        return ["product", "--data-product", str(self.dp), "--block-npz", str(self.blk / "cpl_block.npz"),
                "--block-json", str(self.blk / "cpl_block.json"), "--g-readout", str(self.g), "--audit-json",
                str(self.audit), "--out-dir", str(out)]

    def product(self, out: Path, pins=None):
        with quiet(), mock.patch.dict(A.PINS, {**self.pins, "data_product": self.ppins["data_product"]}):
            return A.run(A.build_args(self.pargv(out)), pins=self.ppins if pins is None else pins)


class Product(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="cpl-prod-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def refuses(self, tree, control, pins=None):
        out = self.tmp / "out"
        with mock.patch("sys.stderr") as err:
            rc = tree.product(out, pins)
        self.assertEqual(rc, 1)
        self.assertIn(f"[STOP] {control}:", "".join(str(c.args[0]) for c in err.write.call_args_list))
        self.assertFalse(out.exists() and any(out.iterdir()), "it wrote")

    def test_the_product_is_written_beside_the_without_matrix_and_reads_back(self):
        t = ProductTree(self.tmp / "t")
        self.assertEqual(t.product(self.tmp / "out"), 0)
        js = json.loads((self.tmp / "out" / f"{A.PRODUCT_STEM}.json").read_text())
        self.assertEqual(list(js["matrices"]), list(A.PRODUCT_MATRICES))
        z = A.load_npz(t.blk / "cpl_block.npz")
        np.testing.assert_array_equal(np.array(js["matrices"][A.REPORTED]), z[A.REPORTED])
        np.testing.assert_array_equal(np.array(js["matrices"][A.WITHOUT]), t.Ct + t.Cr)
        self.assertEqual(js["correlation_of"], A.REPORTED)
        for k in ("block", "decision", "context_dr_pair", "context_5a_5b"):
            self.assertEqual(js["labels"][k], A.LABELS[k])
        self.assertEqual(sorted(js["files_sha256"]), sorted(p.name for p in (self.tmp / "out").glob("*.csv")))

    def test_without_the_chains_pins_it_refuses(self):
        t = ProductTree(self.tmp / "t")
        with mock.patch("sys.stderr"):
            self.assertEqual(run_quiet(A.run, A.build_args(t.pargv(self.tmp / "out"))), 1)

    def test_a_stage_g_sigma_that_is_not_the_revised_matrix_refuses(self):
        def m(gr):
            gr["predictions"][1]["sigma_total_over_f"][4] *= 1 + 1e-9
        self.refuses(ProductTree(self.tmp / "t", g_mutate=m), "K3")

    def test_a_stage_g_on_another_block_name_refuses(self):
        self.refuses(ProductTree(self.tmp / "t", g_mutate=lambda gr: gr["extra_block"].update(name="C_resp")), "K1")

    def test_a_data_product_whose_c_resp_is_not_the_blocks_refuses(self):
        def m(dp):
            dp["matrices"]["C_resp"][0][0] *= 1 + 1e-12
        self.refuses(ProductTree(self.tmp / "t", dp_mutate=m), "K2")

    def test_an_existing_output_refuses(self):
        t = ProductTree(self.tmp / "t")
        (self.tmp / "out").mkdir()
        (self.tmp / "out" / f"{A.PRODUCT_STEM}.json").write_text("{}")
        with mock.patch("sys.stderr") as err:
            self.assertEqual(t.product(self.tmp / "out"), 1)
        self.assertIn("[STOP] K0:", "".join(str(c.args[0]) for c in err.write.call_args_list))
        self.assertEqual((self.tmp / "out" / f"{A.PRODUCT_STEM}.json").read_text(), "{}")

    def test_a_block_of_rank_three_refuses_k4(self):
        t = ProductTree(self.tmp / "t")
        z = A.load_npz(t.blk / "cpl_block.npz")
        g3 = np.random.default_rng(4).normal(0, 0.01, 16) * t.f
        z["C_PL5D"] = z["C_PL5D"] + np.outer(g3, g3)
        z[A.REPORTED] = z[A.REPORTED] + np.outer(g3, g3)
        (t.blk / "cpl_block.npz").write_bytes(A.npz_bytes(z))
        bj = json.loads((t.blk / "cpl_block.json").read_text())
        bj["npz"]["sha256"] = digest(t.blk / "cpl_block.npz")
        (t.blk / "cpl_block.json").write_text(json.dumps(bj))
        g = json.loads(t.g.read_text())
        g["extra_block"]["sha256"] = digest(t.blk / "cpl_block.npz")
        sig = np.sqrt(np.diag(z[A.REPORTED])) / t.f
        for p in g["predictions"]:
            p["sigma_total_over_f"] = sig[[CELLS.index(c) for c in p["cells"]]].tolist()
        t.g.write_text(json.dumps(g))
        t.ppins.update(block_npz=digest(t.blk / "cpl_block.npz"), block_json=digest(t.blk / "cpl_block.json"),
                       g_readout=digest(t.g))
        with mock.patch("sys.stderr") as err:
            self.assertEqual(t.product(self.tmp / "out"), 1)
        self.assertIn("[STOP] K4: C_PL5D is positive semidefinite and of rank 2",
                      "".join(str(c.args[0]) for c in err.write.call_args_list))

    def test_a_without_sigma_that_is_not_the_committed_products_refuses_k5(self):
        def m(dp):
            dp["relative_sigma"][A.WITHOUT][7] *= 1 + 1e-9
        self.refuses(ProductTree(self.tmp / "t", dp_mutate=m), "K5")

    def test_a_csv_that_does_not_read_back_refuses_k6(self):
        t = ProductTree(self.tmp / "t")
        orig = A.F.read_matrix_csv

        def off(text):
            M = orig(text)
            M[0, 0] *= 1 + 1e-15
            return M
        with mock.patch.object(A.F, "read_matrix_csv", off):
            self.refuses(t, "K6")

    def test_a_data_product_whose_matrix_is_not_its_parts_plus_the_block_refuses(self):
        def m(dp):
            dp["matrices"][A.WITHOUT][2][2] *= 1 + 1e-9
        self.refuses(ProductTree(self.tmp / "t", dp_mutate=m), "K2")


# ------------------------------------------------------------------------------------------------ the deposit candidate

class Deposit(unittest.TestCase):
    """The deposit candidate's variant: it carries the revised matrix, and the default refuses it."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="cpl-dep-"))
        cls.t = ProductTree(cls.tmp / "t")
        assert cls.t.product(cls.tmp / "dp") == 0
        cls.dp = cls.tmp / "dp" / f"{A.PRODUCT_STEM}.json"
        cls.pins = {"data_product": digest(cls.dp), "g_readout": digest(cls.t.g)}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def build(self, out, v):
        a = DC.build_args(["build", "--data-product", str(self.dp), "--g-readout", str(self.t.g), "--out-dir", str(out)])
        with quiet(), mock.patch("sys.stderr"):
            return DC.run(a, variant=v)

    def check(self, pkg, v):
        a = DC.build_args(["check", "--package", str(pkg), "--data-product", str(self.dp), "--g-readout",
                           str(self.t.g)])
        with quiet(), mock.patch("sys.stderr"):
            return DC.run(a, variant=v)

    def test_the_variant_builds_and_checks_the_revised_matrix(self):
        out = self.tmp / "pkg-v"
        v = A.deposit_variant(self.pins)
        self.assertEqual(self.build(out, v), 0)
        self.assertEqual(self.check(out, v), 0)
        js = json.loads((out / "deposit.json").read_text())
        self.assertEqual(js["covariance_of"], A.REPORTED)
        self.assertEqual(js["labels"]["decision"], A.LABELS["decision"])
        self.assertEqual((out / "covariance.csv").read_bytes(),
                         (self.dp.parent / f"{A.PRODUCT_STEM}_{A.REPORTED}.csv").read_bytes())
        self.assertEqual(js["source"], {"data_product": f"fd/with-cpl/data-product/{A.PRODUCT_STEM}.json",
                                        "sha256": self.pins["data_product"]})

    def test_the_default_variant_refuses_the_revised_product_at_its_pins(self):
        self.assertEqual(self.build(self.tmp / "pkg-d", None), 1)
        self.assertFalse((self.tmp / "pkg-d").exists())

    def test_the_variant_with_another_stage_g_pin_refuses(self):
        v = A.deposit_variant({**self.pins, "g_readout": "2" * 64})
        self.assertEqual(self.build(self.tmp / "pkg-g", v), 1)

    def test_the_variant_package_fails_the_default_check_at_its_pins(self):
        out = self.tmp / "pkg-x"
        self.assertEqual(self.build(out, A.deposit_variant(self.pins)), 0)
        self.assertEqual(self.check(out, None), 1)

    def test_the_default_check_with_the_variants_pins_refuses_the_package_content(self):
        out = self.tmp / "pkg-c"
        self.assertEqual(self.build(out, A.deposit_variant(self.pins)), 0)
        a = DC.build_args(["check", "--package", str(out), "--data-product", str(self.dp), "--g-readout",
                           str(self.t.g)])
        with quiet(), mock.patch("sys.stderr") as err:
            self.assertEqual(DC.run(a, pins=self.pins), 1)          # past P0: the default key's matrix is not it
        self.assertIn("P2", "".join(str(c.args[0]) for c in err.write.call_args_list))

    def test_a_package_edited_after_the_build_fails_the_variants_check(self):
        out = self.tmp / "pkg-e"
        v = A.deposit_variant(self.pins)
        self.assertEqual(self.build(out, v), 0)
        js = json.loads((out / "deposit.json").read_text())
        js["labels"]["decision"] = "edited"
        (out / "deposit.json").write_text(json.dumps(js, indent=1) + "\n")
        self.assertEqual(self.check(out, v), 1)

    def test_the_default_variant_is_todays_constants(self):
        self.assertEqual((DC.DEFAULT.key, DC.DEFAULT.name), ("C_total_plus_C_resp", "C_total + C_resp"))
        self.assertIs(DC.DEFAULT.labels, DC.LABELS)
        self.assertIs(DC.DEFAULT.pins, DC.PINS)


# ------------------------------------------------------------------------------------------------ the table

class Table(unittest.TestCase):
    """cmd_table on the committed readouts, with a with side written as the tools write it for the combined block."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="cpl-table-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.paths, self.pins = {}, {}
        for k in A.READOUTS:
            text = (REPO / A.COMMITTED[k][0]).read_text()
            text = text.replace("C_total + C_resp", f"C_total + {A.NAME}").replace(
                "relative_sigma_plus_C_resp", f"relative_sigma_plus_{A.NAME}")
            self.write(k, json.loads(text))
        dp = json.loads((REPO / A.COMMITTED["data_product"][0]).read_text())
        w = np.array(dp["relative_sigma"][A.WITHOUT])
        self.write("data_product", {"relative_sigma": {A.WITHOUT: w.tolist(), A.BLOCK: (0.3 * w).tolist(),
                                                       A.REPORTED: (np.sqrt(1.09) * w).tolist()}})

    def write(self, k, obj):
        q = self.tmp / f"{k}_with.json"
        q.write_text(json.dumps(obj))
        self.paths[k], self.pins[f"{k}_with"] = q, digest(q)

    def table(self):
        argv = ["table"]
        for k in (*A.READOUTS, "data_product"):
            argv += [f"--{k.replace('_', '-')}-without", str(REPO / A.COMMITTED[k][0]),
                     f"--{k.replace('_', '-')}-with", str(self.paths[k])]
        argv += ["--audit-json", str(AUDIT), "--out-dir", str(self.tmp / "out")]
        pins = {**self.pins, **{f"{k}_without": A.COMMITTED[k][1] for k in (*A.READOUTS, "data_product")}}
        with quiet(), mock.patch("sys.stderr") as err:
            rc = A.run(A.build_args(argv), pins=pins)
        return rc, "".join(str(c.args[0]) for c in err.write.call_args_list)

    def test_the_table_is_written_from_the_committed_readouts(self):
        rc, err = self.table()
        self.assertEqual(rc, 0, err)
        js = json.loads((self.tmp / "out/fd_cpl_table.json").read_text())
        self.assertEqual(js["unpaired_without_leaves"], {k: [] for k in A.READOUTS})
        self.assertEqual(len(js["curated"]["stage_g"]), 10)
        kinds = {r["kind"]: r for r in js["curated"]["stage_g"] if r["prediction"] == "genie_cv"}
        self.assertEqual(kinds["shape_only"]["with"]["matrix"],
                         f"C_total + {A.NAME} + V_g + 100 f f^T (free normalization)")
        np.testing.assert_allclose(js["curated"]["sigma_over_f"]["ratio"], np.sqrt(1.09) * np.ones(16), rtol=1e-12)
        self.assertTrue((self.tmp / "out/fd_cpl_table.md").read_text().startswith("# The 5B block's addition"))

    def test_a_with_side_that_kept_the_old_shape_only_name_refuses(self):
        g = json.loads(self.paths["g"].read_text())
        g["predictions"][0]["shape_only"]["matrix"] = "C_total + C_resp + V_g + 100 f f^T (free normalization)"
        self.write("g", g)
        rc, err = self.table()
        self.assertEqual(rc, 1)
        self.assertIn("[STOP] T: Stage G genie_cv shape_only", err)
        self.assertFalse((self.tmp / "out").exists())

    def test_a_with_side_in_another_order_refuses(self):
        g = json.loads(self.paths["g"].read_text())
        g["predictions"][0], g["predictions"][1] = g["predictions"][1], g["predictions"][0]
        self.write("g", g)
        rc, err = self.table()
        self.assertEqual(rc, 1)
        self.assertIn("same order", err)

    def test_a_without_side_that_is_not_the_committed_readout_refuses(self):
        self.pins["g_with"] = digest(self.paths["g"])
        argv_pins = dict(self.pins)
        with mock.patch.dict(A.COMMITTED, {"g": (A.COMMITTED["g"][0], "4" * 64)}):
            rc, err = self.table()
        self.assertEqual(rc, 1)
        self.assertIn("[STOP] T", err)


# ------------------------------------------------------------------------------------------------ the figures

from test_fd_g_figures import FigTree  # noqa: E402


def rename_tree(t: FigTree, name: str) -> None:
    """The FigTree's readouts as Stage G and its successors write them for an adopted block named ``name``."""
    t.g["extra_block"]["name"] = name
    for p in t.g["predictions"]:
        p["reported_covariance"] = f"C_total + {name}"
        p["total"]["matrix"] = FIG.reported(name)
    t.write("g_readout", t.g)
    for p in t.dg["predictions"]:
        p["comparisons"][0]["matrix"] = FIG.reported(name)
    t.dg["inputs_sha256"]["g_readout"] = t.pins["g_readout"]
    t.write("g_diag_readout", t.dg)
    t.fu["sens"]["reported_matrix"] = FIG.reported(name)
    t.fu["inputs_sha256"].update(g_readout=t.pins["g_readout"], g_diag_readout=t.pins["g_diag_readout"])
    t.write("g_followup_readout", t.fu)
    t.s2["sens"]["reported_matrix"] = FIG.reported(name)
    t.s2["inputs_sha256"].update(g_readout=t.pins["g_readout"], g_followup_readout=t.pins["g_followup_readout"])
    t.s2["referenced"]["g_followup_readout"] = t.pins["g_followup_readout"]
    t.write("g_sens2_readout", t.s2)
    t.b[f"relative_sigma_plus_{name}"] = t.b.pop("relative_sigma_plus_C_resp")
    t.write("f0b_readout", t.b)


class Figures(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="cpl-fig-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        (self.tmp / "in").mkdir()
        self.tree = FigTree(self.tmp / "in")

    def run_fig(self, name=None, figures=("ratio", "modes", "sens")):
        argv = self.tree.argv(self.tmp / "out", figures) + (["--reported-block-name", name] if name else [])
        with quiet():
            return FIG.run(FIG.build_args(argv), pins=self.tree.pins)

    def test_the_renamed_block_draws_with_its_name(self):
        rename_tree(self.tree, A.NAME)
        self.assertEqual(self.run_fig(A.NAME), 0)
        side = json.loads((self.tmp / "out/fd_g_fig_ratio.json").read_text())
        self.assertEqual(side["options"]["reported_block_name"], A.NAME)

    def test_the_default_name_refuses_the_renamed_tree(self):
        rename_tree(self.tree, A.NAME)
        with self.assertRaises(SystemExit) as cm:
            self.run_fig()
        self.assertIn("FAIL control K1", str(cm.exception))

    def test_the_new_name_refuses_the_default_tree(self):
        with self.assertRaises(SystemExit) as cm:
            self.run_fig(A.NAME)
        self.assertIn("FAIL control K1", str(cm.exception))

    def test_the_default_names_c_resp_and_records_no_new_option(self):
        self.assertEqual(self.run_fig(), 0)
        side = json.loads((self.tmp / "out/fd_g_fig_ratio.json").read_text())
        self.assertEqual(side["options"], {"ratio_form": "data-over-prediction", "gibuu_axis": "separate"})
        self.assertEqual(FIG.REPORTED, "C_total + C_resp + V_g")

    def test_a_renamed_tree_whose_f0b_key_is_the_old_one_refuses_k2(self):
        rename_tree(self.tree, A.NAME)
        self.tree.b["relative_sigma_plus_C_resp"] = self.tree.b.pop(f"relative_sigma_plus_{A.NAME}")
        self.tree.write("f0b_readout", self.tree.b)
        with self.assertRaises(SystemExit) as cm:
            self.run_fig(A.NAME, figures=("ratio",))
        self.assertIn(f"FAIL control K2: F0b records relative_sigma_plus_{A.NAME}", str(cm.exception))

    def test_a_renamed_tree_with_one_old_matrix_name_refuses_k5(self):
        rename_tree(self.tree, A.NAME)
        self.tree.s2["sens"]["reported_matrix"] = "C_total + C_resp + V_g"
        self.tree.write("g_sens2_readout", self.tree.s2)
        with self.assertRaises(SystemExit) as cm:
            self.run_fig(A.NAME, figures=("sens",))
        self.assertIn("FAIL control K5", str(cm.exception))


# ------------------------------------------------------------------------------------------------ the flux bootstrap

from test_fd_flux_boot import BootTree  # noqa: E402


class FluxBoot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="cpl-fb-"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def renamed(self, tree, name):
        """Stage G rerun on the same tree with the extra block named ``name``; the bootstrap's argv and pins follow."""
        extra = list(tree.extra)
        extra[extra.index("--extra-block-name") + 1] = name
        g = tree.root / "fd_g_readout_renamed.json"
        gargv = tree.argv[:-2] + extra + ["--out-json", str(g)]
        with quiet(), mock.patch.object(sys, "argv", ["fd_g_compare.py"] + gargv):
            # S1's readout as BootTree rewrote it (its meta), which the bootstrap's own pins already name
            G.run(G.build_args(gargv), {**tree.pins, "s1_json": tree.bpins["s1_json"]}, tree.predictions)
        argv = list(tree.bargv)
        argv[argv.index("--g-readout") + 1] = str(g)
        argv[argv.index("--extra-block-name") + 1] = name
        return argv, {**tree.bpins, "g_readout": digest(g)}

    def boot(self, tree, argv, pins):
        out = Path(argv[argv.index("--out-json") + 1])
        if out.exists():
            out.unlink()
        with quiet(), mock.patch.object(sa, "CONSTRAINT_SHA256", pins["constraint"]), \
                mock.patch.object(sys, "argv", ["fd_flux_boot.py"] + argv):
            FB.run(FB.build_args(argv), pins, tree.predictions)
        return json.loads(out.read_text())

    def test_the_default_labels_are_the_committed_readouts(self):
        committed = json.loads((FDP / "fd/readout/fd_flux_boot_readout.json").read_text())
        self.assertEqual(FB.labels("C_total + C_resp")["units"], committed["labels"]["units"])
        self.assertEqual(FB.LABELS["units"], committed["labels"]["units"])
        self.assertEqual(list(FB.labels("x")), list(committed["labels"]))

    def test_the_labels_name_the_runs_matrix_in_both_directions(self):
        tree = BootTree(self.tmp / "t").write()
        out = self.boot(tree, tree.bargv, tree.bpins)
        self.assertEqual(out["labels"], FB.LABELS)
        argv, pins = self.renamed(tree, A.NAME)
        out2 = self.boot(tree, argv, pins)
        self.assertIn(f"on C_total + {A.NAME} + (C - C_0) + V_g", out2["labels"]["units"])
        self.assertNotIn("C_total + C_resp + (C - C_0)", out2["labels"]["units"])
        self.assertEqual({k: v for k, v in out2["labels"].items() if k != "units"},
                         {k: v for k, v in FB.LABELS.items() if k != "units"})
        self.assertEqual(out2["constants"]["reported_matrix"], f"C_total + {A.NAME} + V_g")
        self.assertEqual(A.compare_numbers(out, out2), [])          # the same block's numbers, under another name

    def test_a_name_that_is_not_stage_gs_refuses(self):
        tree = BootTree(self.tmp / "t2").write()
        argv = list(tree.bargv)
        argv[argv.index("--extra-block-name") + 1] = A.NAME
        with self.assertRaises(SystemExit) as cm:
            self.boot(tree, argv, tree.bpins)
        self.assertIn("FAIL control D5", str(cm.exception.code))


# ------------------------------------------------------------------------------------------------ the chain

FAKE = '''import argparse, json, sys
from pathlib import Path
def build_args(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--rc", type=int, default=0)
    ap.add_argument("--no-write", action="store_true")
    return ap.parse_args(argv)
def run(a, pins=None):
    if not a.no_write:
        a.out.write_text(json.dumps({"argv": sys.argv, "pins": pins}))
    return a.rc
def main(argv=None):
    return run(build_args(argv))
if __name__ == "__main__":
    raise SystemExit(main())
'''


class ChainRunner(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="cpl-chain-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        (self.tmp / "D/nd-unfolding").mkdir(parents=True)
        (self.tmp / "D/nd-unfolding/fake_tool.py").write_text(FAKE)
        self.BA = self.tmp / "BA"
        for d in ("logs", "pins"):
            (self.BA / d).mkdir(parents=True)
        self.c = A.Chain(A.Paths(self.tmp / "D", self.tmp / "P", self.BA), self.BA / "chain.json")

    def test_pins_reach_the_tool_in_process_and_argv_is_the_tools(self):
        out = self.BA / "o.json"
        with quiet():
            rec = self.c.run("s", "with", "fake_tool", ["--out", str(out)], [out], 30, pins={"g_readout": "ab" * 32})
        got = json.loads(out.read_text())
        self.assertEqual(got["pins"], {"g_readout": "ab" * 32})
        self.assertEqual(got["argv"][0], str(self.tmp / "D/nd-unfolding/fake_tool.py"))
        self.assertEqual(got["argv"][1:], ["--out", str(out)])
        self.assertEqual(rec["outputs"], {str(out): digest(out)})
        self.assertEqual(json.loads((self.BA / "pins/with-s.json").read_text()), {"g_readout": "ab" * 32})
        self.assertEqual(json.loads((self.BA / "chain.json").read_text())["steps"][0]["pins"], {"g_readout": "ab" * 32})

    def test_without_pins_the_tool_runs_as_its_cli(self):
        out = self.BA / "o.json"
        with quiet():
            self.c.run("s", "without", "fake_tool", ["--out", str(out)], [out], 30)
        self.assertIsNone(json.loads(out.read_text())["pins"])

    def test_a_nonzero_exit_stops_the_chain(self):
        out = self.BA / "o.json"
        with quiet(), self.assertRaises(A.Stop) as cm:
            self.c.run("s", "with", "fake_tool", ["--out", str(out), "--rc", "3"], [out], 30, pins={})
        self.assertEqual(cm.exception.control, "C")
        self.assertEqual(json.loads((self.BA / "chain.json").read_text())["steps"][0]["rc"], 3)

    def test_a_missing_output_stops_the_chain(self):
        out = self.BA / "o.json"
        with quiet(), self.assertRaises(A.Stop):
            self.c.run("s", "with", "fake_tool", ["--out", str(out), "--no-write"], [out], 30)

    def test_a_failed_check_stops_and_is_recorded(self):
        with quiet(), self.assertRaises(A.Stop):
            self.c.check("R x: something", False, ["number /a"])
        self.assertEqual(json.loads((self.BA / "chain.json").read_text())["steps"][-1]["ok"], False)

    def test_the_deposit_variant_reaches_the_tool_through_the_bootstrap(self):
        t = ProductTree(self.tmp / "pt")
        self.assertEqual(t.product(self.tmp / "dp"), 0)
        dp = self.tmp / "dp" / f"{A.PRODUCT_STEM}.json"
        c = A.Chain(A.Paths(REPO, self.tmp / "P", self.BA), self.BA / "chain.json")
        pins = {"data_product": digest(dp), "g_readout": digest(t.g)}
        pkg = self.BA / "pkg"
        with quiet():
            c.run("deposit_build", "with", "fd_deposit_candidate", ["build", "--data-product", str(dp), "--g-readout",
                                                                    str(t.g), "--out-dir", str(pkg)],
                  [pkg / "deposit.json"], 60, pins=pins, variant="with-cpl")
            c.run("deposit_check", "with", "fd_deposit_candidate", ["check", "--package", str(pkg), "--data-product",
                                                                    str(dp), "--g-readout", str(t.g)],
                  [pkg / "deposit.json"], 60, pins=pins, variant="with-cpl")
        self.assertEqual(json.loads((pkg / "deposit.json").read_text())["covariance_of"], A.REPORTED)
        with quiet(), self.assertRaises(A.Stop):        # the same build without the variant: the default refuses it
            c.run("deposit_build2", "with", "fd_deposit_candidate", ["build", "--data-product", str(dp),
                                                                     "--g-readout", str(t.g), "--out-dir",
                                                                     str(self.BA / "pkg2")],
                  [self.BA / "pkg2/deposit.json"], 60)


def flags(argv) -> list:
    return sorted(x for x in argv if isinstance(x, str) and x.startswith("--"))


def script_flags(rel: str, tool: str) -> list:
    """The flags of the bound run's invocation of ``tool`` in a committed step script, its $XB/$F1 lines included."""
    text = (FDP / rel).read_text()
    var = dict(re.findall(r'^(XB|F1)="(.*?)"$', text, re.M | re.S))
    m = re.search(rf"{re.escape(tool)}\.py(.*?)(?:>|$)", text, re.S)
    body = m.group(1).replace("$XB", var.get("XB", "")).replace("$F1", var.get("F1", ""))
    return sorted(t for t in body.split() if t.startswith("--"))


class StepArgv(unittest.TestCase):
    """Each chain step's flags are its last bound run's (declaration section 3), in both arms."""

    SCRIPTS = {"f0b": ("fd/receipts-f0b/step3.sh", "fd_f0_regrade"), "f1": ("fd/receipts-f1/run/s12.sh", "fd_f0_regrade"),
               "g": ("fd/receipts-g/g2.sh", "fd_g_compare"), "g_diag": ("fd/receipts-g-diag/d2.sh", "fd_g_diag"),
               "g_followup": ("fd/receipts-g-followup/f2.sh", "fd_g_followup"),
               "g_sens2": ("fd/receipts-g-sens2/s2.sh", "fd_g_followup"),
               "flux_boot": ("fd/receipts-flux-boot/run/amended/logs/s2-body.sh", "fd_flux_boot"),
               "figures": ("fd/receipts-g-figures/run/s3.sh", "fd_g_figures"),
               "figures_check": ("fd/receipts-g-figures/run/s4.sh", "fd_g_figures_check")}

    def setUp(self):
        self.p = A.Paths(REPO, Path("/P"), Path("/BA"))
        self.up = {k: Path(f"/up/{k}") for k in ("f0b", "g", "g_diag", "g_followup", "g_sens2", "data_product",
                                                  "block_npz", "block_json")}
        self.up["f0b_sha256"] = "0" * 64

    def argv(self, step, arm):
        xb = A.extra(Path("/x.npz"), "1" * 64, "k", "n")
        xb0 = A.extra(Path("/x.npz"), "1" * 64, "k", "n", role=False)
        return A.step_argv(self.p, step, xb, xb0, self.up, Path("/out/x.json"), arm)

    def test_every_steps_flags_are_its_bound_runs(self):
        for step, (rel, tool) in self.SCRIPTS.items():
            want = script_flags(rel, tool)
            self.assertEqual(flags(self.argv(step, "without")), want, step)
            extra = ["--reported-block-name"] if step == "figures" else []
            self.assertEqual(flags(self.argv(step, "with")), sorted(want + extra), step)

    def test_the_without_data_product_is_the_bound_tools_argv(self):
        self.assertEqual(flags(self.argv("data_product", "without")),
                         script_flags("fd/receipts-g-figures/run/s2.sh", "fd_data_product"))

    def test_a_flag_dropped_from_a_step_would_be_seen(self):
        want = script_flags("fd/receipts-g/g2.sh", "fd_g_compare")
        got = [x for x in self.argv("g", "without") if x != "--s1-json"]
        self.assertNotEqual(flags(got), want)

    def test_the_without_arm_uses_cresp_and_the_with_arm_the_block(self):
        self.assertEqual(A.extra(self.p.cresp, A.PINS["cresp_npz"], "C_resp", "C_resp")[3::2],
                         [A.PINS["cresp_npz"], "C_resp", "C_resp", "adopted"])
        self.assertEqual(self.p.cresp, Path("/P/cresp-20261026/out/cresp.npz"))
        self.assertEqual((A.NAME, A.XKEY), ("C_resp + C_PL5D", "C_resp_plus_C_PL5D"))


class DryWithout(unittest.TestCase):
    """The without arm with each tool replaced by a copy of its committed output: control R passes on the committed
    files, and fires on one planted difference in each kind of product."""

    SOURCES = {"data_product": "fd/data-product", "deposit_build": "fd/deposit-candidate", "figures": "fd/figures"}

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="cpl-dry-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        for d in ("logs", "pins"):
            (self.tmp / d).mkdir()
        self.c = A.Chain(A.Paths(REPO, Path("/P"), self.tmp), self.tmp / "chain.json")

    def dry(self, plant=None):
        def fake(name, arm, tool, argv, outputs, timeout, pins=None, variant=""):
            if name in self.SOURCES:
                out = Path(argv[argv.index("--out-dir") + 1])
                shutil.copytree(FDP / self.SOURCES[name], out, ignore=shutil.ignore_patterns("README.md"))
            else:
                key = next(k for k in A.READOUTS if A.COMMITTED[k][0].endswith(Path(outputs[0]).name))
                shutil.copyfile(REPO / A.COMMITTED[key][0], outputs[0])
            if plant:
                plant(name, outputs)
            self.c.steps.append({"step": name, "rc": 0})
            return {}
        with quiet(), mock.patch.object(self.c, "run", fake):
            return A.without_arm(self.c)

    def test_the_committed_files_pass_every_r_check(self):
        self.dry()
        checks = [s for s in self.c.steps if s.get("check")]
        self.assertEqual(len(checks), 7 + 2 + 5 + 3)
        self.assertTrue(all(s["ok"] for s in checks))

    def planted(self, step, fn):
        def plant(name, outputs):
            if name == step:
                fn(outputs)
        with self.assertRaises(A.Stop) as cm:
            self.dry(plant)
        self.assertEqual(cm.exception.control, "R")
        return str(cm.exception)

    def test_a_changed_number_in_a_readout_fires(self):
        def fn(outputs):
            js = json.loads(Path(outputs[0]).read_text())
            js["predictions"][0]["total"]["chi2"] += 1e-6
            Path(outputs[0]).write_text(json.dumps(js))
        self.assertIn("R g", self.planted("g", fn))

    def test_a_changed_byte_in_a_data_product_csv_fires(self):
        def fn(outputs):
            q = Path(outputs[0]).parent / "fd_data_product_C_resp.csv"
            q.write_text(q.read_text().replace("e-", "E-", 1))
        self.assertIn("CSV", self.planted("data_product", fn))

    def test_a_changed_deposit_label_fires_and_a_changed_code_digest_does_not(self):
        def code(outputs):
            q = Path(outputs[0]).parent / "deposit.json"
            js = json.loads(q.read_text())
            js["code_sha256"]["fd_deposit_candidate.py"] = "0" * 64
            q.write_text(json.dumps(js, indent=1) + "\n")
        self.dry(lambda name, outputs: code(outputs) if name == "deposit_build" else None)

        def label(outputs):
            q = Path(outputs[0]).parent / "deposit.json"
            js = json.loads(q.read_text())
            js["labels"]["status"] += "."
            q.write_text(json.dumps(js, indent=1) + "\n")
        shutil.rmtree(self.tmp / "without")
        self.c.steps.clear()
        self.assertIn("deposit deposit.json", self.planted("deposit_build", label))

    def test_a_changed_pdf_fires(self):
        def fn(outputs):
            q = Path(outputs[0])
            q.write_bytes(q.read_bytes() + b"\n")
        self.assertIn("R figure fd_g_fig_ratio", self.planted("figures", fn))


class DryWith(unittest.TestCase):
    """The with arm with each tool replaced by a fake that records the pins it was given and writes them into its
    readout's inputs_sha256, as the tools do: controls C and S pass only when each step's pins are the sha256 of the
    files the steps before it wrote."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="cpl-dryw-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        for d in ("logs", "pins"):
            (self.tmp / d).mkdir()
        self.tree = BlockTree(self.tmp / "t")
        self.c = A.Chain(A.Paths(REPO, Path("/P"), self.tmp), self.tmp / "chain.json")
        self.calls = {}

    def fake(self, name, arm, tool, argv, outputs, timeout, pins=None, variant=""):
        self.calls[name] = {"argv": argv, "pins": pins, "variant": variant}
        val = (lambda f: argv[argv.index(f) + 1] if f in argv else None)
        if name == "block":
            assert self.tree.run(Path(val("--out-dir"))) == 0
        elif name in A.READOUTS:
            npz = Path(val("--extra-block"))
            z = A.load_npz(npz)
            rep = np.sqrt(np.diag(z[A.REPORTED])) / z["f"]
            r = {"extra_block": {"sha256": val("--extra-block-sha256")}, "inputs_sha256": dict(pins or {})}
            if name == "g":
                r["predictions"] = [{"cells": CELLS, "sigma_total_over_f": rep.tolist()}]
            if name == "f0b":
                r[f"relative_sigma_plus_{val('--extra-block-name')}"] = {"C_total": rep.tolist()}
            Path(outputs[0]).write_text(json.dumps(r))
        else:
            for q in outputs:
                Path(q).parent.mkdir(parents=True, exist_ok=True)
                Path(q).write_text(json.dumps({"step": name, "pins": pins}))
        self.c.steps.append({"step": name})
        return {}

    def dry(self):
        with quiet(), mock.patch.object(self.c, "run", self.fake):
            return A.with_arm(self.c, lambda mod, attr: {"default": "d" * 64})

    def test_each_steps_pins_are_the_files_the_steps_before_wrote(self):
        H = self.dry()
        W = self.tmp / "with/readout"
        sha = {k: digest(W / Path(A.COMMITTED[k][0]).name) for k in A.READOUTS}
        self.assertEqual({k: H[k] for k in A.READOUTS}, sha)
        self.assertIsNone(self.calls["f0b"]["pins"])
        self.assertIsNone(self.calls["g"]["pins"])
        self.assertEqual(self.calls["f1"]["argv"][self.calls["f1"]["argv"].index("--f0b-readout-sha256") + 1],
                         sha["f0b"])
        self.assertEqual(self.calls["g_diag"]["pins"], {"default": "d" * 64, "g_readout": sha["g"]})
        self.assertEqual(self.calls["g_followup"]["pins"], {"default": "d" * 64, "g_readout": sha["g"],
                                                            "g_diag_readout": sha["g_diag"]})
        self.assertEqual(self.calls["g_sens2"]["pins"], {"default": "d" * 64, "g_readout": sha["g"],
                                                         "g_followup_readout": sha["g_followup"]})
        self.assertEqual(self.calls["flux_boot"]["pins"], {"default": "d" * 64, "g_readout": sha["g"]})
        dp = self.tmp / "with/data-product" / f"{A.PRODUCT_STEM}.json"
        self.assertEqual(self.calls["deposit_build"]["pins"], {"data_product": digest(dp), "g_readout": sha["g"]})
        self.assertEqual(self.calls["deposit_build"]["variant"], "with-cpl")
        self.assertEqual(self.calls["deposit_check"]["variant"], "with-cpl")
        self.assertEqual({k: v for k, v in self.calls["figures"]["pins"].items() if k != "default"},
                         {"g_readout": sha["g"], "g_diag_readout": sha["g_diag"], "g_followup_readout": sha["g_followup"],
                          "g_sens2_readout": sha["g_sens2"], "f0b_readout": sha["f0b"]})
        self.assertIn("--reported-block-name", self.calls["figures"]["argv"])
        tp = self.calls["table"]["pins"]
        self.assertEqual({k: tp[f"{k}_with"] for k in A.READOUTS}, sha)
        self.assertEqual({k: tp[f"{k}_without"] for k in (*A.READOUTS, "data_product")},
                         {k: A.COMMITTED[k][1] for k in (*A.READOUTS, "data_product")})
        self.assertTrue(all(s.get("ok", True) for s in self.c.steps))
        npz = self.tmp / "with/block/cpl_block.npz"
        for k in A.READOUTS:
            argv = self.calls[k]["argv"]
            self.assertEqual(argv[argv.index("--extra-block") + 1], str(npz), k)
            self.assertEqual(argv[argv.index("--extra-block-name") + 1], A.NAME, k)

    def test_a_step_that_reads_a_stale_upstream_fails_control_c(self):
        orig = self.fake

        def stale(name, arm, tool, argv, outputs, timeout, pins=None, variant=""):
            if name == "g_sens2":
                pins = {**pins, "g_followup_readout": "e" * 64}
            return orig(name, arm, tool, argv, outputs, timeout, pins, variant)
        self.fake = stale
        with self.assertRaises(A.Stop) as cm:
            self.dry()
        self.assertEqual(cm.exception.control, "C")
        self.assertIn("g_sens2", str(cm.exception))

    def test_a_readout_on_another_block_fails_control_c(self):
        orig = self.fake

        def other(name, arm, tool, argv, outputs, timeout, pins=None, variant=""):
            out = orig(name, arm, tool, argv, outputs, timeout, pins, variant)
            if name == "g_diag":
                js = json.loads(Path(outputs[0]).read_text())
                js["extra_block"]["sha256"] = A.PINS["cresp_npz"]
                Path(outputs[0]).write_text(json.dumps(js))
            return out
        self.fake = other
        with self.assertRaises(A.Stop) as cm:
            self.dry()
        self.assertIn("g_diag", str(cm.exception))

    def test_a_stage_g_sigma_that_is_not_the_revised_matrix_fails_control_s(self):
        orig = self.fake

        def off(name, arm, tool, argv, outputs, timeout, pins=None, variant=""):
            out = orig(name, arm, tool, argv, outputs, timeout, pins, variant)
            if name == "g":
                js = json.loads(Path(outputs[0]).read_text())
                js["predictions"][0]["sigma_total_over_f"][5] *= 1 + 1e-9
                Path(outputs[0]).write_text(json.dumps(js))
            return out
        self.fake = off
        with self.assertRaises(A.Stop) as cm:
            self.dry()
        self.assertEqual(cm.exception.control, "S")


class Committed(unittest.TestCase):
    def test_the_pins_are_the_committed_files(self):
        for k, (rel, pin) in A.COMMITTED.items():
            self.assertEqual(digest(REPO / rel), pin, k)
        self.assertEqual(digest(AUDIT), A.PINS["audit"])
        self.assertEqual(digest(FDP / "fd/readout/fd_ct_5b_periods.json"), A.PINS["periods"])

    def test_the_committed_audit_did_not_stop(self):
        au = json.loads(AUDIT.read_text())
        self.assertIs(au["stop_condition"]["stop"], False)
        self.assertEqual(au["inputs_sha256"]["readout_5b"], A.PINS["periods"])

    def test_the_table_reads_every_curated_field_from_the_committed_readouts(self):
        old = {k: json.loads((REPO / A.COMMITTED[k][0]).read_text()) for k in A.READOUTS}
        dp = json.loads((REPO / A.COMMITTED["data_product"][0]).read_text())
        dpw = {"relative_sigma": {A.WITHOUT: dp["relative_sigma"][A.WITHOUT], A.BLOCK: [0.0] * 16,
                                  A.REPORTED: dp["relative_sigma"][A.WITHOUT]}}
        c = A.curated(old, old, dp, dpw)
        self.assertEqual(len(c["stage_g"]), 10)
        self.assertEqual(len(c["truths"]["f0b"]), sum(t["graded"] for t in old["f0b"]["truths"]))
        self.assertEqual(c["sigma_over_f"]["ratio"], [1.0] * 16)
        self.assertTrue(A.table_md(c, {"g": 1}).startswith("# The 5B block's addition"))
        self.assertEqual(len(list(A.paired(old["g"], old["g"]))), len(list(A.numeric_leaves(old["g"]))))


if __name__ == "__main__":
    unittest.main()
