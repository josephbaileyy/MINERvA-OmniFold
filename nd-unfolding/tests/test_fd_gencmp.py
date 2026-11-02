"""Controls for fd_gencmp.py and fd_gencmp_kin.py (FD-GENCMP-DECLARATION.md), on synthetic inputs. No real prediction,
covariance or data value is read; the only real file read is the H2 definition, for its geometry.

Every control is tested in the direction it acts and in the other: it passes on a consistent fixture and refuses on a
one-entry defect (A0, A1, the CH bitwise check, C0, C3, the Q coverage label, step D's rule, the outcome rule of
step C at each boundary)."""
import hashlib
import io
import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(1, str(ND))
import fd_g_compare as fg  # noqa: E402
import fd_gencmp as G  # noqa: E402
import fd_gencmp_kin as K  # noqa: E402
import s1_assemble as sa  # noqa: E402

REPO = ND.parent
N = G.N_FINE
RNG = np.random.default_rng(20261101)


def sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def spd(n, scale):
    A = RNG.normal(size=(n, n))
    return (A @ A.T / n + np.eye(n)) * np.outer(scale, scale)


class Fixture:
    """A synthetic tree of every input steps A, C and D read, with its own pins."""

    def __init__(self, d: Path):
        self.d = d
        self.U = G.cell_matrix()
        self.p5 = RNG.uniform(1e-42, 2e-42, N)
        f = self.U @ self.p5
        Ce, Cma = spd(16, 0.05 * f), spd(16, 0.03 * f)
        Cr, Cpl = spd(16, 0.02 * f), spd(16, 0.01 * f)
        self.f = f
        np.savez(d / "block.npz", f=f, C_resp=Cr, C_PL5D=Cpl, C_total_plus_C_resp_plus_C_PL5D=Ce + Cma + Cr + Cpl,
                 P_rel=np.eye(16), C_resp_plus_C_PL5D=Cr + Cpl)
        (d / "dp.json").write_text(json.dumps({"matrices": {"C_e": Ce.tolist(), "C_model_abs": Cma.tolist()}}))
        (d / "cmodel.json").write_text(json.dumps({"x": f.tolist()}))
        self.R = {"f": f, "reported": Ce + Cma + Cr + Cpl, "nopl": Ce + Cma + Cr}
        for name in ("nuwro", "gibuu"):
            xc, sc = RNG.uniform(1e-42, 2e-42, N), RNG.uniform(1e-90, 2e-90, N)
            xh, sh = RNG.uniform(1e-42, 2e-42, N), RNG.uniform(1e-90, 2e-90, N)
            xch, sch = G.combine(xc, sc, xh, sh)
            np.savez(d / f"{name}.npz", xsec_C12_frozen=xc, sumw2_C12_frozen=sc, xsec_H=xh, sumw2_H=sh,
                     xsec_CH=xch, sumw2_CH=sch)
            np.savez(d / f"{name}_frozen.npz", xsec_flat=xc, sumw2_flat=sc)
        np.savez(d / "gibuu_alt.npz", xsec_CH=RNG.uniform(1e-42, 2e-42, N), sumw2_CH=RNG.uniform(1e-90, 2e-90, N))
        np.savez(d / "genie.npz", xsec_H1=RNG.uniform(1e-44, 2e-44, N), sumw2_H1=RNG.uniform(1e-92, 2e-92, N))
        self.write_readouts()
        self.paths = {"BLOCK": d / "block.npz", "DATA_PRODUCT": d / "dp.json", "CMODEL": d / "cmodel.json",
                      "NUWRO_NPZ": d / "nuwro.npz", "GIBUU_NPZ": d / "gibuu.npz", "GIBUU_ALT_NPZ": d / "gibuu_alt.npz",
                      "GENIE_H_NPZ": d / "genie.npz", "READOUT_REPORTED": d / "rep.json", "READOUT_NOPL": d / "nopl.json",
                      "FROZEN_NUWRO": str(d / "nuwro_frozen.npz"), "FROZEN_GIBUU": str(d / "gibuu_frozen.npz")}

    def write_readouts(self, bump=0.0, bump_shape=0.0):
        rows = {"reported": [], "without_C_PL5D": []}
        for name, cells in (("nuwro", G.ALL_CELLS), ("gibuu", G.GIBUU_CELLS)):
            z = np.load(self.d / f"{name}.npz")
            g, Vg = G.integrate(self.U, z["xsec_C12_frozen"], z["sumw2_C12_frozen"], cells)
            for key, C in (("reported", self.R["reported"]), ("without_C_PL5D", self.R["nopl"])):
                c = fg.compare(self.f, g, Vg, C, cells, key)
                rows[key].append({"name": name, "total": {"chi2": c["total"]["chi2"] * (1 + bump)},
                                  "shape_only": {"chi2": c["shape_only"]["chi2"] * (1 + bump_shape)}})
        (self.d / "rep.json").write_text(json.dumps({"predictions": rows["reported"]}))
        (self.d / "nopl.json").write_text(json.dumps({"predictions": rows["without_C_PL5D"]}))

    def pins(self):
        out = {str(p): sha(p) for p in self.d.iterdir() if p.is_file() and p.suffix in (".npz", ".json", ".root")}
        out[str(G.DEFINITION)] = sha(G.DEFINITION)
        return out

    def patches(self):
        ps = [mock.patch.object(G, k, v) for k, v in self.paths.items()]
        ps.append(mock.patch.object(G, "load_pins", lambda path=None: self.pins()))
        return ps


class WithFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.fx = Fixture(self.d)
        self.ps = self.fx.patches()
        for p in self.ps:
            p.start()

    def tearDown(self):
        for p in self.ps:
            p.stop()
        self.tmp.cleanup()

    def a1_json(self, ok=True):
        pins = self.fx.pins()
        p = self.d / "a1_out.txt"
        names = ("nuwro", "gibuu", "nuwro_frozen", "gibuu_frozen")
        p.write_text(json.dumps({"pass": ok, "inputs": {f"/elsewhere/{n}.npz": {"sha256": pins[str(self.d / f"{n}.npz")]}
                                                         for n in names}}))      # other paths: A1 matches by digest
        return p


class StepA(WithFixture):
    def test_runs_and_writes(self):
        out = self.d / "ch_out.txt"
        G.main(["ch", "--a1-json", str(self.a1_json()), "--out", str(out)])
        r = json.loads(out.read_text())
        self.assertEqual(set(r["generators"]), {"nuwro", "gibuu"})
        self.assertEqual(r["generators"]["gibuu"]["cells"], [f"R{c:02d}" for c in G.GIBUU_CELLS])
        self.assertIn("CH_alt_weight", r["generators"]["gibuu"])
        self.assertNotIn("CH_alt_weight", r["generators"]["nuwro"])
        self.assertIn("B3 (sampling closure) failed on hydrogen", r["generators"]["gibuu"]["CH"]["label"])

    def test_a0_refuses_a_committed_chi2_off_by_1e_6(self):
        self.fx.write_readouts(bump=1e-6)
        with self.assertRaises(fg.Stop) as e:
            G.main(["ch", "--a1-json", str(self.a1_json()), "--out", str(self.d / "x_out.txt")])
        self.assertIn("A0", str(e.exception))
        self.assertFalse((self.d / "x_out.txt").exists())

    def test_a1_failed_readout_refuses(self):
        with self.assertRaises(fg.Stop) as e:
            G.main(["ch", "--a1-json", str(self.a1_json(ok=False)), "--out", str(self.d / "x_out.txt")])
        self.assertIn("A1", str(e.exception))

    def test_ch_bitwise_check_refuses_a_one_cell_defect(self):
        z = dict(np.load(self.d / "nuwro.npz"))
        z["xsec_CH"] = z["xsec_CH"].copy()
        z["xsec_CH"][1234] *= 1 + 1e-15 if z["xsec_CH"][1234] * (1 + 1e-15) != z["xsec_CH"][1234] else 1 + 1e-12
        np.savez(self.d / "nuwro.npz", **z)
        self.fx.write_readouts()
        with self.assertRaises(fg.Stop) as e:
            G.main(["ch", "--a1-json", str(self.a1_json()), "--out", str(self.d / "x_out.txt")])
        self.assertIn("bitwise", str(e.exception))

    def test_refuses_overwrite(self):
        out = self.d / "ch_out.txt"
        out.write_text("{}")
        with self.assertRaises(fg.Stop):
            G.main(["ch", "--a1-json", str(self.a1_json()), "--out", str(out)])

    def test_a1_command_both_directions(self):
        out = self.d / "a1r_out.txt"
        G.main(["a1", "--nuwro-frozen", str(self.d / "nuwro_frozen.npz"), "--gibuu-frozen", str(self.d / "gibuu_frozen.npz"),
                "--out", str(out)])
        self.assertTrue(json.loads(out.read_text())["pass"])
        z = dict(np.load(self.d / "gibuu_frozen.npz"))
        z["sumw2_flat"] = z["sumw2_flat"].copy()
        z["sumw2_flat"][7] *= 2
        np.savez(self.d / "gibuu_frozen.npz", **z)
        with self.assertRaises(fg.Stop):
            G.main(["a1", "--nuwro-frozen", str(self.d / "nuwro_frozen.npz"),
                    "--gibuu-frozen", str(self.d / "gibuu_frozen.npz"), "--out", str(self.d / "a1s_out.txt")])


class Inputs(WithFixture):
    def test_pin_mismatch_refuses(self):
        inp = G.Inputs({**self.fx.pins(), str(self.d / "block.npz"): "0" * 64})
        with self.assertRaises(fg.Stop):
            inp.bytes(self.d / "block.npz")

    def test_unpinned_refuses(self):
        p = self.d / "other.npz"
        np.savez(p, a=np.zeros(1))
        with self.assertRaises(fg.Stop):
            G.Inputs({}).bytes(p)

    def test_result_controls_refuse_a_defect(self):
        z = dict(np.load(self.d / "block.npz"))
        z["C_total_plus_C_resp_plus_C_PL5D"] = z["C_total_plus_C_resp_plus_C_PL5D"].copy()
        z["C_total_plus_C_resp_plus_C_PL5D"][3, 3] *= 1.001
        np.savez(self.d / "block.npz", **z)
        with self.assertRaises(fg.Stop):
            G.result(G.Inputs())


class Rules(unittest.TestCase):
    def test_outcome_rule_each_side_of_each_boundary(self):
        s16, slow = 1.0, 0.6
        lo, hi = 2 * abs(s16 - slow), 2 * np.sqrt(s16 ** 2 + slow ** 2)
        self.assertEqual(G.rule(0.99 * lo, s16, slow)["outcome"], "agree")
        self.assertEqual(G.rule(1.01 * lo, s16, slow)["outcome"], "agree below a correlation")
        self.assertEqual(G.rule(-0.99 * hi, s16, slow)["outcome"], "agree below a correlation")
        self.assertEqual(G.rule(1.01 * hi, s16, slow)["outcome"], "differ")
        d = 0.5 * (lo + hi)
        r = G.rule(d, s16, slow)["rho_star"]
        self.assertTrue(0 < r < 1)
        self.assertAlmostEqual(d, 2 * np.sqrt(s16 ** 2 + slow ** 2 - 2 * r * s16 * slow), places=12)

    def test_3d_rule_is_descriptive_both_ways(self):
        self.assertEqual(G.rule(1.9, 1.0, None)["outcome"], "agree at the sigma_16 scale (descriptive)")
        self.assertEqual(G.rule(-2.1, 1.0, None)["outcome"], "differ at the sigma_16 scale (descriptive)")

    def test_native_rule_both_directions(self):
        g = np.ones(16)
        V = np.full(16, 0.01)
        self.assertTrue(G.native_rule(g, V, g + 0.05, V, G.ALL_CELLS)["agree"])
        self.assertFalse(G.native_rule(g, V, g + 0.21, V, G.ALL_CELLS)["agree"])         # sum z^2 = 35.3
        one = g.copy()
        one[3] += 0.6                                                                     # one |z| > 3.5
        self.assertFalse(G.native_rule(g, V, one, V, G.ALL_CELLS)["agree"])

    def test_combine_is_mp3b_order_bitwise(self):
        x, y = RNG.uniform(size=1000), RNG.uniform(size=1000)
        got, _ = G.combine(x, x, y, y)
        self.assertTrue(np.array_equal(got, (12.0 / 13.0) * x + (1.0 / 13.0) * y))

    def test_chi2_pair_refuses_nonpositive(self):
        R = {"f": np.ones(16), "reported": np.eye(16), "nopl": np.eye(16)}
        g = np.ones(16)
        g[5] = 0
        with self.assertRaises(fg.Stop):
            G.chi2_pair(R, g, np.zeros(16), G.ALL_CELLS)


class Geometry(unittest.TestCase):
    def test_quadrants_match_the_definition(self):
        defn = json.loads(G.DEFINITION.read_text())
        q = G.quadrant_cells(defn)
        for k, Q in G.QUADRANTS.items():
            self.assertEqual(q[k]["cells"], Q["cells"])
            self.assertEqual(q[k]["unreported"], Q["unreported"])
            self.assertEqual(len(q[k]["boxes"]), 8)

    def test_enumeration_finds_regions_when_they_exist(self):
        self.assertTrue(G.enumerate_eavail_regions({"h2_to_reporting_cell": list(range(32))}))

    def test_enumeration_on_the_definition(self):
        defn = json.loads(G.DEFINITION.read_text())
        self.assertEqual(G.enumerate_eavail_regions(defn), [])


def write_root(path, hists):
    import uproot
    with uproot.recreate(path) as f:
        for k, v in hists.items():
            f[k] = v


class StepC(WithFixture):
    def setUp(self):
        super().setUp()
        e_pt = np.asarray(sa.s1.FINE["pt"], float)
        e_pz = np.asarray(sa.s1.FINE["pz"], float)
        e_ea = np.asarray(sa.s1.FINE["eavail"], float)
        cv = RNG.uniform(0.5, 1.5, (14, 16))
        cv[13, :6] = 0.0
        cv[12, :5] = 0.0
        cv[11, :8] = 0.0                                   # 19 empty bins: 205 cells remain
        w2 = np.outer(np.diff(e_pt), np.diff(e_pz))
        cv *= G.VL173_2D_INTEGRAL / (cv * w2).sum()
        self.cv, self.w2 = cv, w2
        cells = np.flatnonzero(cv.ravel() > 0)
        self.assertEqual(cells.size, 205)
        x = cv.ravel()[cells]
        np.savez(self.d / "q.npz", total_plus_C_PL=np.diag((0.06 * x) ** 2), area=w2.ravel()[cells], cells_x_EU=x)
        np.savez(self.d / "pl.npz", cells=cells)
        write_root(self.d / "cv2.root", {"hXSec2D": (cv, e_pt, e_pz)})
        cv3 = RNG.uniform(0.5, 1.5, (14, 16, 7))
        cv3 *= G.TOTAL_3D / (cv3 * np.einsum("i,j,k->ijk", np.diff(e_pt), np.diff(e_pz), np.diff(e_ea))).sum()
        self.cv3, self.edges = cv3, (e_pt, e_pz, e_ea)
        write_root(self.d / "cv3.root", {"hXSec3D": (cv3, e_pt, e_pz, e_ea)})
        idx = np.sort(RNG.choice(14 * 16 * 7, 1431, replace=False)).astype(float)
        ax = np.arange(1432, dtype=float)
        write_root(self.d / "proj.root", {"hCov_proj_pt_pz_eavail": (np.diag(np.full(1431, 1e-82)), ax, ax),
                                          "hRowIndex": (idx, ax)})
        np.savez(self.d / "p5.npz", xsec_flat=self.fx.p5, shape=np.array([14, 16, 7, 7, 6]))
        np.savez(self.d / "tune.npz", xsec_flat=RNG.uniform(1e-42, 2e-42, N))

    def args(self, out):
        return ["overlap", "--p5", str(self.d / "p5.npz"), "--mnvtune", str(self.d / "tune.npz"),
                "--cv2d", str(self.d / "cv2.root"), "--q2d", str(self.d / "q.npz"), "--playlist", str(self.d / "pl.npz"),
                "--cv3d", str(self.d / "cv3.root"), "--proj3d", str(self.d / "proj.root"), "--out", str(out)]

    def test_runs_with_every_quadrant_formed(self):
        out = self.d / "ov_out.txt"
        G.main(self.args(out))
        r = json.loads(out.read_text())
        self.assertEqual(set(r["quadrants"]), {"QA", "QB", "QC", "QD"})
        for q in ("QA", "QB", "QC", "QD"):
            self.assertIn(r["quadrants"][q]["2D"]["outcome"], ("agree", "agree below a correlation", "differ"))
            self.assertIn("descriptive", r["quadrants"][q]["3D"]["outcome"])
            self.assertIn("no outcome is read", r["quadrants"][q]["3D"]["descriptive_PROJ3D"]["label"])
        self.assertEqual(r["quadrants"]["QC"]["unreported_share_P5"], 0.0)
        self.assertGreater(r["quadrants"]["QA"]["unreported_share_P5"], 0.0)
        self.assertEqual(r["eavail_regions_formable"], [])

    def test_quadrant_not_covered_by_q_gets_central_only(self):
        pl = np.load(self.d / "pl.npz")["cells"]
        keep = pl != pl[-1]                               # drop the last cell, in QD (high pT, high p_par)
        q = dict(np.load(self.d / "q.npz"))
        np.savez(self.d / "pl.npz", cells=pl[keep])
        np.savez(self.d / "q.npz", total_plus_C_PL=q["total_plus_C_PL"][np.ix_(keep, keep)], area=q["area"][keep],
                 cells_x_EU=q["cells_x_EU"][keep])
        cv = self.cv.copy()
        e_pt, e_pz = np.asarray(sa.s1.FINE["pt"], float), np.asarray(sa.s1.FINE["pz"], float)
        cv *= (G.VL173_2D_INTEGRAL / (cv.ravel()[pl[keep]] * self.w2.ravel()[pl[keep]]).sum())
        write_root(self.d / "cv2.root", {"hXSec2D": (cv, e_pt, e_pz)})
        out = self.d / "ov2_out.txt"
        G.main(self.args(out))
        r = json.loads(out.read_text())
        self.assertEqual(r["quadrants"]["QD"]["2D"]["label"], "Q does not cover this quadrant; no 2D comparison is formed")
        self.assertNotIn("d_pct", r["quadrants"]["QD"]["2D"])
        self.assertNotIn("outcome", r["quadrants"]["QD"]["2D"])
        self.assertIn("outcome", r["quadrants"]["QA"]["2D"])

    def test_c3_refuses_a_wrong_2d_total(self):
        e_pt, e_pz = np.asarray(sa.s1.FINE["pt"], float), np.asarray(sa.s1.FINE["pz"], float)
        write_root(self.d / "cv2.root", {"hXSec2D": (self.cv * 1.001, e_pt, e_pz)})
        with self.assertRaises(fg.Stop) as e:
            G.main(self.args(self.d / "x_out.txt"))
        self.assertIn("C3", str(e.exception))

    def test_c0_refuses_a_p5_that_does_not_give_f(self):
        p5 = self.fx.p5.copy()
        p5[np.flatnonzero(self.fx.U[0])[0]] *= 1.01
        np.savez(self.d / "p5.npz", xsec_flat=p5, shape=np.array([14, 16, 7, 7, 6]))
        with self.assertRaises(fg.Stop) as e:
            G.main(self.args(self.d / "x_out.txt"))
        self.assertIn("C0", str(e.exception))


class StepCRefusals(StepC):
    def refuses(self, control):
        with self.assertRaises(fg.Stop) as e:
            G.main(self.args(self.d / "x_out.txt"))
        self.assertIn(control, str(e.exception))
        self.assertFalse((self.d / "x_out.txt").exists())

    def test_c1_refuses_a_2d_grid_without_the_quadrant_edge(self):
        e_pt, e_pz = self.edges[0].copy(), self.edges[1]
        e_pt[np.isclose(e_pt, 0.7)] = 0.71
        write_root(self.d / "cv2.root", {"hXSec2D": (self.cv, e_pt, e_pz)})
        self.refuses("C1")

    def test_c1_refuses_a_3d_grid_without_the_quadrant_edge(self):
        e_pt, e_pz, e_ea = self.edges
        e_pz2 = e_pz.copy()
        e_pz2[np.isclose(e_pz2, 4.5)] = 4.6
        write_root(self.d / "cv3.root", {"hXSec3D": (self.cv3, e_pt, e_pz2, e_ea)})
        self.refuses("C1")

    def test_area_check_refuses(self):
        q = dict(np.load(self.d / "q.npz"))
        q["area"] = q["area"].copy()
        q["area"][17] *= 1.01
        np.savez(self.d / "q.npz", **q)
        self.refuses("area")

    def test_units_check_refuses(self):
        q = dict(np.load(self.d / "q.npz"))
        q["total_plus_C_PL"] = q["total_plus_C_PL"] * 1e6
        np.savez(self.d / "q.npz", **q)
        self.refuses("units")

    def test_quadrant_definition_check_refuses(self):
        bad = {**G.QUADRANTS, "QA": {**G.QUADRANTS["QA"], "unreported": [2]}}
        with mock.patch.object(G, "QUADRANTS", bad):
            self.refuses("declared ones")

    def test_proj3d_index_check_refuses_a_duplicate(self):
        idx = np.sort(RNG.choice(14 * 16 * 7, 1431, replace=False)).astype(float)
        idx[5] = idx[4]
        ax = np.arange(1432, dtype=float)
        write_root(self.d / "proj.root", {"hCov_proj_pt_pz_eavail": (np.diag(np.full(1431, 1e-82)), ax, ax),
                                          "hRowIndex": (idx, ax)})
        self.refuses("PROJ3D")

    def test_c3_refuses_a_wrong_3d_total(self):
        e_pt, e_pz, e_ea = self.edges
        write_root(self.d / "cv3.root", {"hXSec3D": (self.cv3 * 1.001, e_pt, e_pz, e_ea)})
        self.refuses("3D integral")

    def test_an_eavail_region_stops_for_an_amendment(self):
        with mock.patch.object(G, "enumerate_eavail_regions", lambda defn: [{"cells": [0]}]):
            self.refuses("amendment")

    def test_without_c_pl_is_printed_only(self):
        out = self.d / "ov3_out.txt"
        G.main(self.args(out))
        r = json.loads(out.read_text())["quadrants"]["QC"]["2D"]
        self.assertIn("printed only", r["printed_only_without_C_PL5D"]["label"])
        self.assertIn("reported matrix", r["primary"])


class MoreRefusals(WithFixture):
    def test_r_refuses_f_not_cmodel_x(self):
        cm = json.loads((self.d / "cmodel.json").read_text())
        cm["x"][4] *= 1 + 1e-9
        (self.d / "cmodel.json").write_text(json.dumps(cm))
        with self.assertRaises(fg.Stop) as e:
            G.result(G.Inputs())
        self.assertIn("cmodel", str(e.exception))

    def test_a2_refuses_negative_vg(self):
        R = {"f": np.ones(16), "reported": np.eye(16), "nopl": np.eye(16)}
        Vg = np.zeros(16)
        Vg[2] = -1e-9
        with self.assertRaises(fg.Stop) as e:
            G.chi2_pair(R, np.ones(16), Vg, G.ALL_CELLS)
        self.assertIn("A2", str(e.exception))

    def test_a0_refuses_a_shape_only_chi2_off_by_1e_6(self):
        self.fx.write_readouts(bump_shape=1e-6)
        with self.assertRaises(fg.Stop) as e:
            G.main(["ch", "--a1-json", str(self.a1_json()), "--out", str(self.d / "x_out.txt")])
        self.assertIn("shape_only", str(e.exception))

    def test_a1_readout_missing_a_frozen_digest_refuses(self):
        p = self.a1_json()
        r = json.loads(p.read_text())
        r["inputs"].pop("/elsewhere/gibuu_frozen.npz")
        p.write_text(json.dumps(r))
        with self.assertRaises(fg.Stop) as e:
            G.main(["ch", "--a1-json", str(p), "--out", str(self.d / "x_out.txt")])
        self.assertIn("A1", str(e.exception))


class RebuildReaders(WithFixture):
    """defs and native end to end on a synthetic rebuild directory."""

    def rebuild(self, status_override=None, ch_defect=False):
        rd = self.d / "rb"
        rd.mkdir()
        status = {}

        def put(sample, x, v, variants):
            for var in variants:
                np.savez(rd / f"{sample}_{var}.npz", xsec_flat=x * (1 + 1e-3 * (var != "gen")), sumw2_flat=v,
                         nevt_flat=np.ones(N))
        allv = ["gen", "wonly", "axisonly"] + [f"ana_s{s}" for s in K.SEEDS]
        for name in ("genie_cv", "genie_mec"):
            put(name, RNG.uniform(1e-42, 2e-42, N), RNG.uniform(1e-90, 2e-90, N), allv)
            status[name] = {"B0": True, "B2": "pass", "complete": True}
        for gen in ("nuwro", "gibuu"):
            z = np.load(self.d / f"{gen}.npz")
            xc = z["xsec_C12_frozen"] * (1 + 1e-6) if (ch_defect and gen == "nuwro") else z["xsec_C12_frozen"]
            put(f"{gen}_C12", xc, z["sumw2_C12_frozen"], allv + (["ana_mn"] if gen == "gibuu" else []))
            put(f"{gen}_H", z["xsec_H"], z["sumw2_H"], allv)
            status[f"{gen}_C12"] = status[f"{gen}_H"] = {"B0": True, "B2": "pass", "complete": True}
        nw = np.load(self.d / "nuwro.npz")
        put("nuwro_CHnative", nw["xsec_CH"], nw["sumw2_CH"], allv)
        status["nuwro_CHnative"] = {"B0": True, "B2": "n/a", "complete": True}
        status.update(status_override or {})
        for s_, st in (status_override or {}).items():
            if not st.get("complete"):
                for f in rd.glob(f"{s_}_ana_s*.npz"):
                    f.unlink()                          # a B2 stop writes no analysis products
        (rd / "rebuild.json").write_text(json.dumps({"status": status}))
        return rd

    def test_defs_reads_complete_samples_and_skips_a_b2_stop(self):
        rd = self.rebuild({"genie_mec": {"B0": True, "B2": "stop", "complete": False}})
        out = self.d / "defs_out.txt"
        G.main(["defs", "--rebuild-dir", str(rd), "--out", str(out)])
        r = json.loads(out.read_text())
        self.assertEqual(r["not_read"], ["genie_mec"])
        self.assertNotIn("CH", r["generators"]["genie_mec"])
        self.assertIn("CH", r["generators"]["nuwro"])
        self.assertIn("ana_mn_delta_over_sigma", r["generators"]["gibuu"]["CH"])
        self.assertEqual(len(r["generators"]["gibuu"]["CH"]["cells"]), 8)

    def test_defs_refuses_a_rebuilt_ch_that_is_not_step_a(self):
        rd = self.rebuild(ch_defect=True)
        with self.assertRaises(fg.Stop) as e:
            G.main(["defs", "--rebuild-dir", str(rd), "--out", str(self.d / "x_out.txt")])
        self.assertIn("B0", str(e.exception))

    def test_native_runs_both_routes(self):
        rd = self.rebuild()
        out = self.d / "nat_out.txt"
        G.main(["native", "--rebuild-dir", str(rd), "--out", str(out)])
        r = json.loads(out.read_text())
        self.assertTrue(r["agree"])                      # the native sample is step A's CH here
        self.assertIn("rule", r["analysis_definitions"])
        self.assertIn("step A's combination", r["paper_uses"])

    def test_native_refuses_an_incomplete_native_sample(self):
        rd = self.rebuild({"nuwro_CHnative": {"B0": False, "B2": "n/a", "complete": False}})
        with self.assertRaises(fg.Stop) as e:
            G.main(["native", "--rebuild-dir", str(rd), "--out", str(self.d / "x_out.txt")])
        self.assertIn("nuwro_CHnative", str(e.exception))


class NoAtimeRefusals(unittest.TestCase):
    def test_pscratch_refused_without_o_noatime(self):
        saved = getattr(os, "O_NOATIME", None)
        try:
            if saved is not None:
                del os.O_NOATIME
            with self.assertRaises(fg.Stop):
                G.read_noatime(Path("/pscratch/sd/x/never-opened.npz"))
        finally:
            if saved is not None:
                os.O_NOATIME = saved

    def test_a_moved_atime_is_detected(self):
        with tempfile.NamedTemporaryFile(delete=False) as fh:
            fh.write(b"abc")
        from types import SimpleNamespace
        for step, want in ((0, True), (1, False)):
            calls = []

            def fake(path, *a, **k):
                calls.append(1)
                return SimpleNamespace(st_atime_ns=1_000 + step * (len(calls) - 1))
            with mock.patch.object(G.os, "stat", fake):
                _, ok = G.read_noatime(Path(fh.name))
            self.assertEqual(ok, want)
        os.unlink(fh.name)

class Kinematics(unittest.TestCase):
    def test_masses_are_gen_to_xsec5d_s(self):
        src = (REPO / "3d-unfolding/genie/gen_to_xsec5d.py").read_text()
        m = re.search(r"CVU_M_N, CVU_M_P = ([0-9.]+), ([0-9.]+)", src)
        self.assertEqual((float(m.group(1)), float(m.group(2))), (K.CVU_M_N, K.CVU_M_P))
        self.assertIn("CVU_M_NUCLEON = (1.5 * CVU_M_N + CVU_M_P) / 2.5", src)
        self.assertIn("M_NUCLEON = 0.939565", (REPO / "3d-unfolding/genie/gen_to_xsec_eavailW.py").read_text())

    def test_struck_mass(self):
        self.assertTrue(np.array_equal(K.struck_mass(np.array([2112, 2212, 0, 2000000200])),
                                       [K.CVU_M_N, K.CVU_M_P, K.CVU_M_NUCLEON, K.CVU_M_NUCLEON]))

    def test_w_analysis_formula_and_nan(self):
        enu, emu, th, m = 5.0, 3.0, 0.2, K.CVU_M_P
        want = np.sqrt(m * m + 2 * m * (enu - emu) - 4 * enu * emu * np.sin(th / 2) ** 2)
        self.assertAlmostEqual(float(K.w_analysis(enu, emu, np.cos(th), m)), want, places=12)
        self.assertTrue(np.isnan(K.w_analysis(5.0, 5.0, np.cos(0.5), m)))

    def test_beam_frame_identity_and_norm(self):
        px, py, pz = RNG.normal(size=100), RNG.normal(size=100), RNG.uniform(1, 5, 100)
        pt, qz, _ = K.beam_frame(px, py, pz, K.unit_z(100))
        self.assertTrue(np.array_equal(pt, np.hypot(px, py)) and np.array_equal(qz, pz))
        n = np.column_stack([1e-3 * RNG.normal(size=100), 1e-3 * RNG.normal(size=100), np.ones(100)])
        n /= np.linalg.norm(n, axis=1)[:, None]
        pt2, qz2, _ = K.beam_frame(px, py, pz, n)
        self.assertTrue(np.allclose(pt2 ** 2 + qz2 ** 2, px ** 2 + py ** 2 + pz ** 2, rtol=1e-12))
        self.assertFalse(np.array_equal(pt2, pt))

    def test_draws_depend_on_tag_and_seed_only(self):
        a = K.draws(K.SEEDS[0], "nuwro_C12:main", 50)
        b = K.draws(K.SEEDS[0], "nuwro_C12:main", 50)
        c = K.draws(K.SEEDS[0], "nuwro_H:main", 50)
        d = K.draws(K.SEEDS[1], "nuwro_C12:main", 50)
        self.assertTrue(np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1]))
        self.assertFalse(np.array_equal(a[0], c[0]))
        self.assertFalse(np.array_equal(a[0], d[0]))
        self.assertTrue(np.all((a[1] >= 0) & (a[1] < 2 * np.pi)))

    def test_lepton_from_pt_pz(self):
        pt, pz, phi = RNG.uniform(0, 2, 20), RNG.uniform(1, 9, 20), RNG.uniform(0, 6.28, 20)
        x, y, z = K.lepton_from_pt_pz(pt, pz, phi)
        self.assertTrue(np.allclose(np.hypot(x, y), pt, rtol=1e-14) and np.array_equal(z, pz))


class NoAtime(unittest.TestCase):
    def test_read_noatime_returns_the_bytes(self):
        with tempfile.NamedTemporaryFile(delete=False) as fh:
            fh.write(b"abc")
        try:
            data, _ = G.read_noatime(Path(fh.name))
            self.assertEqual(data, b"abc")
        finally:
            os.unlink(fh.name)

    @unittest.skipUnless(hasattr(os, "O_NOATIME"), "O_NOATIME exists on Linux (Perlmutter) only")
    def test_atime_is_unchanged_on_linux(self):
        with tempfile.NamedTemporaryFile(delete=False) as fh:
            fh.write(b"abc")
        try:
            os.utime(fh.name, (1_000_000_000, 1_000_000_000))
            _, ok = G.read_noatime(Path(fh.name))
            self.assertTrue(ok)
        finally:
            os.unlink(fh.name)


if __name__ == "__main__":
    unittest.main()
