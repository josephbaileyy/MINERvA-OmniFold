"""Controls for the 1B gate-D pre-check, Part 1 (state/measurement-paper/5d-community-20261024/
FD-1B-PRECHECK-FD-DECLARATION.md), each rule in the direction it acts and in the other:

* the universe set: Flux_0..99 and the 8 detector universes; an interaction universe refuses in the job;
* the modes on the toy world: B's factors are the toys' own (``fd_1b_toys.source_factors``) bitwise; at CV every mode
  is the derivation CV experiment bitwise; B moves only the reco and background weights;
* the unfolding flux (section 2.1): mode A unfolds a Flux universe with Phi_u, B and Dnom with Phi_CV, and Dnom's truth
  carries Phi_u; ``fd_1b_inv.with_mc`` would have given A Phi_CV and Dnom Phi_u, and each test fails on that;
* HD1's premise flags are recorded for detector universes in mode A;
* rules S, F and K at their edges and with unresolved cells ignored; the attribution levels at n/2 and n/4;
* the readout end to end on a staged synthetic world: B = E reads REPRODUCED, B = E / 1.2 reads DEPARTS, the
  attribution lands on the factor the fixture sets, kappa = 1 passes and 1.2 fails; the identity; and every control
  refuses (gate D's ratio, the diagnosis's ratio, S1's blocks, a CV product, a product's flux, one code, the flux
  file); A_Phi equals A where the fixture's universes are pure normalization;
* the job's products record the flux they unfolded with, and the pilot trigger reads PASS and REPRICE at its edges.

No real data are read: every fixture is synthetic."""
from __future__ import annotations

import contextlib
import io
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
sys.path.insert(1, str(ND))
sys.path.insert(1, str(Path(__file__).resolve().parent))

import fd_1b_diag as fdg  # noqa: E402
import fd_1b_inv as inv  # noqa: E402
import fd_1b_precheck_fd as pfd  # noqa: E402
import fd_1b_score as fs  # noqa: E402
import fd_1b_toys as toys  # noqa: E402
import s1_assemble as sa  # noqa: E402
import s5c_unfold  # noqa: E402
import s5n_pseudo  # noqa: E402
from test_fd_1b import World as ToyWorld, digest, fake_unfold, toy_meta  # noqa: E402
import test_fd_1b_inv  # noqa: E402
from test_fd_1b_inv import plain_noatime  # noqa: E402

CELLS = [f"R{c:02d}" for c in range(16)]
EYE = np.eye(16)


# --------------------------------------------------------------------------------------------------- the toy world


class ToyCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="fd1b-pfd-"))
        cls.w = ToyWorld(cls.tmp)
        cls.inputs = s5c_unfold.load_inputs(cls.w.inputs)
        bz = np.load(cls.w.bkg, allow_pickle=True)
        cls.bkg = {"bkg_reco": bz["bkg_reco"], "bkg_w": bz["bkg_w"], "bkg_nd": bz["bkg_nd"]}
        z = dict(np.load(cls.w.bank / "cv.npz", allow_pickle=True))
        rng = np.random.default_rng(3)
        for k, e in zip(("td_pt", "td_pz", "td_ea", "td_q3", "td_w"), cls.inputs["edges"]):
            z[k] = rng.uniform(e[0], e[-1], 50)
        cls.bank_cv = z
        np.savez(cls.w.bank / "cv.npz", **z)
        cls.w.manifest.write_text("".join(f"{digest(p)}  {p}\n" for p in sorted(cls.w.bank.iterdir()))
                                  + f"{digest(cls.w.receipt)}  {cls.w.receipt}\n")
        cls.w.pins.write_text(json.dumps(toys.make_pins(cls.w.bank, cls.w.det, cls.w.manifest, cls.w.receipt)))
        # a per-universe flux table in the npz form flux_universe reads: CV and 100 universes on the toy pT grid
        cv = np.asarray(cls.inputs["flux"], float)
        univ = cv[:, None] * np.random.default_rng(5).uniform(0.85, 1.15, (cv.size, 100))
        cls.flux_file = cls.tmp / "flux_universes.npz"
        np.savez(cls.flux_file, hFluxCV=cv, hFluxUniv=univ)
        cls.phi = univ.T

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def setUp(self):
        self.ps = self.w.patches() + [plain_noatime()]
        for p in self.ps:
            p.start()

    def tearDown(self):
        for p in reversed(self.ps):
            p.stop()

    def modes(self, mode, tag):
        ui, ub, info = pfd.mode_inputs(mode, tag, self.inputs, self.bkg, self.w.bank, self.w.det, self.bank_cv,
                                       self.flux_file)
        exp_cv, xt_cv = inv.nominal_experiment(self.inputs, self.bkg)
        exp, xt = pfd.experiment(mode, self.inputs, self.bkg, ui, ub, exp_cv, xt_cv)
        return ui, ub, info, exp, xt, exp_cv, xt_cv


class UniverseSet(unittest.TestCase):
    def test_the_108_universes(self):
        u = pfd.universes()
        self.assertEqual(len(u), 108)
        self.assertEqual(u[:3], ["Flux_0", "Flux_1", "Flux_2"])
        self.assertEqual(sorted(x for x in u if not x.startswith("Flux_")),
                         sorted(f"{b}_{i}" for b in sa.DETECTOR_BANDS for i in (0, 1)))
        self.assertNotIn("MaRES_0", u)
        self.assertEqual(pfd.UNFOLD_MC_KEYS, inv.MC_KEYS + ("flux",))


class Modes(ToyCase):
    def test_b_is_the_toys_own_factors_bitwise(self):
        src = np.ones(self.inputs["MCgen"].shape[0], bool)
        for tag in ("Flux_3", "MinosEfficiency_1", "GEANT_Pion_0"):
            fs_, fb, _ = pfd.toy_factors(tag, self.inputs, self.bkg, self.w.bank, self.w.det)
            ts, tb, _ = toys.source_factors(toys.single_universe(tag), self.inputs, self.bkg, self.w.bank, self.w.det,
                                            src, None)
            np.testing.assert_array_equal(fs_, ts)
            np.testing.assert_array_equal(fb, tb)

    def test_at_cv_every_mode_is_the_derivation_cv_experiment(self):
        ref = fake_unfold(inv.nominal_experiment(self.inputs, self.bkg)[0], 42, 1, 5)[0]
        for mode in pfd.MODES:
            *_, exp, xt, _, xt_cv = self.modes(mode, "CV")
            np.testing.assert_array_equal(fake_unfold(exp, 42, 1, 5)[0], ref, err_msg=mode)
            np.testing.assert_array_equal(xt, xt_cv)

    def test_b_moves_only_reco_and_background(self):
        ui, ub, *_ = self.modes("B", "Flux_3")
        for k in ("w_truth", "denom_nd", "flux"):
            np.testing.assert_array_equal(ui[k], self.inputs[k])
        self.assertFalse(np.array_equal(ui["w_reco"], self.inputs["w_reco"]))
        self.assertFalse(np.array_equal(ub["bkg_w"], self.bkg["bkg_w"]))

    def test_a_is_s1s_universe(self):
        ui, ub, *_ = self.modes("A", "Flux_7")
        w = inv.universe_weights(self.w.bank, "Flux_7", "zero")
        np.testing.assert_array_equal(ui["w_truth"], w["wt"])
        np.testing.assert_array_equal(ub["bkg_w"], w["bkgw"])
        np.testing.assert_array_equal(ui["flux"], self.phi[7])


class UnfoldingFlux(ToyCase):
    """Section 2.1: each mode's unfolding flux, and the inherited helper's behaviour each test would catch."""

    def test_mode_a_on_a_flux_universe_unfolds_with_phi_u(self):
        ui, ub, _, exp, *_ = self.modes("A", "Flux_7")
        np.testing.assert_array_equal(exp["flux"], self.phi[7])
        self.assertFalse(np.array_equal(self.phi[7], self.inputs["flux"]))
        inherited = inv.with_mc(inv.nominal_experiment(self.inputs, self.bkg)[0], ui, ub)
        np.testing.assert_array_equal(inherited["flux"], self.inputs["flux"])   # what with_mc would have done

    def test_mode_dnom_unfolds_with_phi_cv_and_its_truth_carries_phi_u(self):
        ui, ub, _, exp, xt, _, xt_cv = self.modes("Dnom", "Flux_7")
        np.testing.assert_array_equal(exp["flux"], self.inputs["flux"])
        # the truth is the universe's: x_T = denominator / (flux ...) per cell, so with Phi_u in place of Phi_CV
        e = [np.asarray(x) for x in self.inputs["edges"]]
        expand = (slice(None),) + (None,) * (len(e) - 1)
        x_u, x_c = np.asarray(xt).reshape([len(x) - 1 for x in e]), np.asarray(xt_cv).reshape([len(x) - 1 for x in e])
        ok = (x_c > 0) & (x_u > 0) & (np.asarray(ui["denom_nd"]) > 0)
        np.testing.assert_allclose((x_u * self.phi[7][expand] / ui["denom_nd"])[ok],
                                   (x_c * np.asarray(self.inputs["flux"])[expand] / self.inputs["denom_nd"])[ok], rtol=1e-12)
        self.assertFalse(np.allclose(xt, xt_cv, rtol=1e-6, atol=0))
        e_u = toys.build_full(ui, ub, np.ones(ui["MCgen"].shape[0]), np.ones(ui["w_reco"].shape[0]),
                              np.ones(ub["bkg_w"].shape[0]), None, expectation=True)[0]
        np.testing.assert_array_equal(inv.with_mc(e_u, self.inputs, self.bkg)["flux"], self.phi[7])  # the inherited bug

    def test_mode_b_and_the_detector_universes_unfold_with_phi_cv(self):
        for mode, tag in (("B", "Flux_7"), ("A", "MinosEfficiency_0"), ("Dnom", "GEANT_Neutron_1")):
            ui, _, _, exp, *_ = self.modes(mode, tag)
            np.testing.assert_array_equal(exp["flux"], self.inputs["flux"], err_msg=f"{mode} {tag}")
            np.testing.assert_array_equal(pfd.expected_flux(mode, tag, self.inputs, ui), self.inputs["flux"])

    def test_hd1s_premise_flags_are_recorded(self):
        _, _, info, *_ = self.modes("A", "MinosEfficiency_0")
        self.assertIn(info["wt_equals_cv"], (True, False))
        self.assertIn(info["denom_equals_cv"], (True, False))
        self.assertFalse(info["wt_equals_cv"])      # the toy dump's truth weights are not the CV's


class Jobs(ToyCase):
    def argv(self, mode, universes, out):
        return ["unfold", "--mode", mode, "--universes", universes, "--npz", str(self.w.inputs), "--bkg", str(self.w.bkg),
                "--bank", str(self.w.bank), "--detector-dir", str(self.w.det), "--flux-file", str(self.flux_file),
                "--pins", str(self.w.pins), "--expect-pins-sha256", digest(self.w.pins), "--threads", "1",
                "--out", str(out)]

    def run_job(self, mode, universes, out):
        with mock.patch.object(s5n_pseudo, "unfold_negweight", fake_unfold), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return pfd.main(self.argv(mode, universes, out))

    def test_products_record_the_flux_they_unfolded_with(self):
        out = self.tmp / "unf-a"
        self.assertEqual(self.run_job("A", "CV,Flux_7,MinosEfficiency_0", out), 0)
        for u, phi in (("CV", self.inputs["flux"]), ("Flux_7", self.phi[7]), ("MinosEfficiency_0", self.inputs["flux"])):
            z = np.load(out / f"{pfd.TAG}_A_{u}.npz", allow_pickle=False)
            m = json.loads(str(z["meta"]))
            np.testing.assert_array_equal(z["unfolding_flux"], phi)
            self.assertEqual(m["unfolding_flux_sha256"], pfd.array_sha256(phi))
            self.assertEqual(m["cv_flux_sha256"], pfd.array_sha256(self.inputs["flux"]))
            self.assertEqual(m["flux_file_sha256"], digest(self.flux_file))

    def test_the_job_refuses_a_product_unfolded_with_another_modes_flux(self):
        out = self.tmp / "unf-inherited"
        with mock.patch.object(pfd, "with_mc", inv.with_mc):      # section 2.1's inherited helper
            self.assertEqual(self.run_job("A", "Flux_7", out), 4)
        self.assertFalse((out / f"{pfd.TAG}_A_Flux_7.npz").exists())

    def test_a_moved_atime_exits_8(self):
        out = self.tmp / "unf-atime"

        def touching(exp, *a, **k):
            st = os.stat(self.w.inputs)
            os.utime(self.w.inputs, ns=(st.st_atime_ns + 10 ** 9, st.st_mtime_ns))
            return fake_unfold(exp, *a, **k)

        with mock.patch.object(s5n_pseudo, "unfold_negweight", touching), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(pfd.main(self.argv("B", "CV", out)), 8)
        self.assertEqual(json.loads(next(out.glob("atime-*.json")).read_text())["moved"], [str(self.w.inputs)])

    def test_an_interaction_universe_refuses(self):
        self.assertEqual(self.run_job("B", "MaRES_0", self.tmp / "unf-r"), 4)
        self.assertFalse((self.tmp / "unf-r" / f"{pfd.TAG}_B_MaRES_0.npz").exists())


class CallGraph(ToyCase):
    """Every input the unfold path opens goes through open_noatime, in all three modes, Flux and detector universes
    included. The flux file is the staged copy the job is given (declaration section 6): its digest is read with
    O_NOATIME, and flux_universe then reads that copy plainly, as ROOT does in production."""
    SENTINEL = test_fd_1b_inv.CallGraph.SENTINEL
    instrument = test_fd_1b_inv.CallGraph.instrument

    def test_the_unfold_path_opens_every_input_with_o_noatime(self):
        out = self.tmp / "cg"
        pins_sha = digest(self.w.pins)
        for p in reversed(self.ps):
            p.stop()
        rec, ps = self.instrument()
        for p in self.w.patches() + ps:
            p.start()
        try:
            with mock.patch.object(s5n_pseudo, "unfold_negweight", fake_unfold), \
                    contextlib.redirect_stdout(io.StringIO()):
                for mode, us in (("A", "CV,Flux_2,GEANT_Pion_1"), ("B", "Flux_5,MinosEfficiency_0"), ("Dnom", "Flux_9")):
                    argv = ["unfold", "--mode", mode, "--universes", us, "--npz", str(self.w.inputs), "--bkg",
                            str(self.w.bkg), "--bank", str(self.w.bank), "--detector-dir", str(self.w.det),
                            "--flux-file", str(self.flux_file), "--pins", str(self.w.pins), "--expect-pins-sha256",
                            pins_sha, "--threads", "1", "--out", str(out)]
                    self.assertEqual(pfd.main(argv), 0)
        finally:
            mock.patch.stopall()
            for p in self.ps:
                p.start()
        ins = {str(p) for p in [self.w.inputs, self.w.bkg, self.w.pins, *self.w.bank.iterdir(), *self.w.det.iterdir()]}
        opened = {p for p, _ in rec["os"] if p in ins}
        for must in (self.w.inputs, self.w.bkg, self.w.pins, self.w.bank / "cv.npz", self.w.bank / "Flux_2_tdw.npy",
                     self.w.bank / "Flux_5_wr.npy", self.w.det / "GEANT_Pion_1_denom_nd.npy",
                     self.w.det / "MinosEfficiency_0_bkgw.npy"):
            self.assertIn(str(must), opened)
        self.assertEqual([p for p in rec["plain"] if p in ins], [])
        self.assertEqual([p for p, flag in rec["os"] if p in ins and not flag], [])
        # the staged flux copy is read plainly (its digest and flux_universe) and is not an atime-tracked source
        self.assertNotIn(str(self.flux_file), {p for p, flag in rec["os"] if flag})
        self.assertEqual(json.loads(next(out.glob("atime-A-*.json")).read_text())["moved"], [])


class PilotWalls(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fd1b-pfd-walls-"))
        self.ps = [plain_noatime()]
        for p in self.ps:
            p.start()

    def tearDown(self):
        for p in reversed(self.ps):
            p.stop()
        shutil.rmtree(self.tmp)

    def write(self, s=100.0, rss=1000, skip=None):
        for mode, u in pfd.PILOT:
            if (mode, u) == skip:
                continue
            np.savez(self.tmp / f"{pfd.TAG}_{mode}_{u}.npz", xsec_flat=np.zeros(2),
                     meta=json.dumps({"mode": mode, "universe": u, "seconds_unfold": s, "peak_rss_kib": rss}))

    def test_at_the_limits_passes_and_beyond_reprices(self):
        self.write(pfd.UNIT_SECONDS, pfd.RSS_LIMIT_KIB)
        self.assertEqual(pfd.pilot_walls(self.tmp)["verdict"], "PASS")
        self.write(pfd.UNIT_SECONDS + 0.001, 10)
        self.assertEqual(pfd.pilot_walls(self.tmp)["verdict"], "REPRICE")
        self.write(10.0, pfd.RSS_LIMIT_KIB + 1)
        self.assertEqual(pfd.pilot_walls(self.tmp)["verdict"], "REPRICE")

    def test_a_missing_pilot_product_refuses(self):
        self.write(skip=("Dnom", "Flux_0"))
        with self.assertRaises(inv.Refusal):
            pfd.pilot_walls(self.tmp)

    def test_the_declared_pilot(self):
        self.assertEqual(len(pfd.PILOT), 8)
        self.assertEqual({m for m, _ in pfd.PILOT}, set(pfd.MODES))
        self.assertEqual(pfd.UNIT_SECONDS, 1370.0)


# ------------------------------------------------------------------------------------------------------- the rules


class Rules(unittest.TestCase):
    def test_rule_s_at_its_edges(self):
        res = np.ones(16, bool)
        f = np.ones(16)
        f[0], f[1] = 0.9, 1.1
        self.assertEqual(pfd.rule_s(f, res)["verdict"], "REPRODUCED")
        f[2] = 1.1000001
        r = pfd.rule_s(f, res)
        self.assertEqual((r["verdict"], r["cells_outside"]), ("DEPARTS", ["R02"]))
        res[2] = False
        self.assertEqual(pfd.rule_s(f, res)["verdict"], "REPRODUCED")

    def test_rule_k_at_its_edges(self):
        res = np.ones(16, bool)
        k = np.ones(16)
        k[5] = 0.8999999
        r = pfd.rule_k(k, res)
        self.assertEqual((r["verdict"], r["cells_outside"]), ("FAIL", ["R05"]))
        k[5] = 0.9
        self.assertEqual(pfd.rule_k(k, res)["verdict"], "PASS")
        k[6], res[6] = 0.5, False
        self.assertEqual(pfd.rule_k(k, res)["verdict"], "PASS")     # an unresolved cell is not read

    def test_attribution_takes_the_dominant_same_side_factor_carrying_half(self):
        F = {"total": np.array([1.5]), "F_src": np.array([1.0]), "F_side": np.array([1.4]), "F_truth": np.array([1.5 / 1.4])}
        self.assertEqual(pfd.attribute(F, 0)["factor"], "F_side")
        F = {"total": np.array([1.5]), "F_src": np.array([1.2]), "F_side": np.array([1.2]), "F_truth": np.array([1.5 / 1.44])}
        self.assertIsNone(pfd.attribute(F, 0)["factor"])    # 1.2 carries under half of ln 1.5
        F = {"total": np.array([0.7]), "F_src": np.array([1.05]), "F_side": np.array([1.0]), "F_truth": np.array([0.7 / 1.05])}
        self.assertEqual(pfd.attribute(F, 0)["factor"], "F_truth")

    def test_levels_at_n_over_2_and_n_over_4(self):
        def attr(*ks):
            return {f"R{i:02d}": {"factor": k} for i, k in enumerate(ks)}
        lv = pfd.level(attr("F_side", "F_side", "F_side", "F_truth"))
        self.assertEqual((lv["level"]["F_side"], lv["level"]["F_truth"], lv["level"]["F_src"]),
                         ("account", "refuted", "refuted"))
        lv = pfd.level(attr("F_side", "F_side", "F_truth", "F_truth"))
        self.assertEqual(lv["level"]["F_side"], "partial")     # exactly n/2 is not more than half
        lv = pfd.level(attr("F_side", "F_side", "F_side", "F_truth", "F_truth", None, None, None))
        self.assertEqual((lv["level"]["F_side"], lv["level"]["F_truth"]), ("partial", "refuted"))
        self.assertEqual(pfd.level({})["level"]["F_src"], "nothing to attribute")


# ------------------------------------------------------------------------------------------------- the readout


class Staged:
    """A staged readout world on 16 cells (U = I, g = f / x_T): toy derivation products for every S1 universe, S1
    universe unfolds whose band-b shifts are ``m[b]`` x the carried toy shifts (so rho_b = 1 / m[b]), the assembly
    built from them, gate D's and the diagnosis's committed readouts from the same arrays, I0's floors, and mode
    products whose blocks set F_src = src[b], F_side = side[b] and kappa = kap[b]. Flux universes in mode A carry
    Phi_u = Phi_CV / (1 + shift) per cell when ``pure_norm``, so A is pure normalization."""

    def __init__(self, tmp: Path, m=None, src=None, side=None, kap=None, sigma=1e-7, pure_norm=False):
        m, src, side, kap = (dict(x or {}) for x in (m, src, side, kap))
        rng = np.random.default_rng(11)
        self.tmp, self.root, self.unf = tmp, tmp / "staged", tmp / "unf"
        for sub in ("derivation", "uni", "s1"):
            (self.root / sub).mkdir(parents=True)
        self.unf.mkdir()
        self.f = rng.uniform(1.0, 3.0, 16)
        self.x_t = self.f / 1.2
        x_cv = self.x_t * rng.uniform(0.98, 1.02, 16)
        self.g = g = self.f / self.x_t
        w = rng.uniform(0.5, 4.0, 100)
        self.constraint = self.root / "flux_constraint.txt"
        self.constraint.write_text("".join(f"Flux {i} {w[i]!r}\n" for i in range(100)))
        xD, xS = {"CV": x_cv}, {"CV": self.f.copy()}
        for b in sorted(sa.EXPECT):
            for i in range(sa.EXPECT[b]):
                u = f"{b}_{i}"
                xD[u] = x_cv * (1 + rng.normal(0, 0.03, 16))
                xS[u] = self.f + m.get(b, 1.0) * g * (xD[u] - x_cv)
        for u, v in xD.items():
            mt = toy_meta("derivation", None, json.loads(json.dumps(toys.single_universe(u))), mode="derivation", universe=u)
            np.savez_compressed(self.root / "derivation" / f"{inv.DER_TAG}_{u}.npz", xsec_flat=v, xtrue_flat=self.x_t,
                                meta=json.dumps(mt))
        for u, v in xS.items():
            np.savez_compressed(self.root / "uni" / f"{inv.S1_TAG}_{u}.npz", xsec_flat=v)
        blocks = {"stat": np.diag((0.005 * self.f) ** 2), "normalization": np.outer(0.014 * self.f, 0.014 * self.f),
                  "seed": np.zeros((16, 16))}
        for b in sa.LATERAL_BANDS:
            blocks[f"lat:{b}"] = np.diag((0.01 * self.f) ** 2)
        for b in sorted(sa.EXPECT):
            X = np.array([xS[f"{b}_{i}"] for i in range(sa.EXPECT[b])])
            blocks[f"band:{b}"] = sa.mat_cov(X, w if b == sa.FLUX else None)
        self.s1 = self.root / "s1" / "s1_assembly.npz"
        np.savez_compressed(self.s1, f=self.f, U=np.eye(16, dtype=np.float32), C_e=sum(blocks.values()),
                            **{"C_" + k.replace(":", "_"): v for k, v in blocks.items()},
                            meta=json.dumps({"blocks": sorted(blocks)}))
        self.flux_sha = "f" * 64
        (self.root / "staged.json").write_text(json.dumps({"staged": [{"role": "flux-file", "sha256": self.flux_sha}],
                                                            "missing": []}))
        self.xD, self.x_cv, self.w, self.rng = xD, x_cv, w, np.random.default_rng(13)
        self.sigma = sigma
        self.cv_flux = np.linspace(1.0, 2.0, 16)
        self.edges = [np.linspace(0.0, 1.0, 17).tolist()]
        self.write_modes(src, side, kap, pure_norm)

    def meta(self, mode, u, flux):
        return {"schema": pfd.SCHEMA, "mode": mode, "universe": u, "config": "R", "iters": 5, "estimator_seed": 42,
                "code_sha256": {"x": "c" * 64}, "input_npz_sha256": "i" * 64, "bkg_dump_sha256": "b" * 64,
                "pins_sha256": "p" * 64, "flux_file_sha256": self.flux_sha, "edges": self.edges,
                "unfolding_flux_sha256": pfd.array_sha256(flux), "cv_flux_sha256": pfd.array_sha256(self.cv_flux),
                "mode_info": {"wt_equals_cv": True, "denom_equals_cv": True}}

    def save(self, mode, u, x, xt, flux, meta=None):
        np.savez(self.unf / f"{pfd.TAG}_{mode}_{u}.npz", xsec_flat=x, xtrue_flat=xt, unfolding_flux=flux,
                 cv_flux=self.cv_flux, meta=json.dumps(meta or self.meta(mode, u, flux)))

    def write_modes(self, src, side, kap, pure_norm):
        for mode in pfd.MODES:
            self.save(mode, "CV", self.x_cv, self.x_t, self.cv_flux)
        for b in pfd.BANDS:
            for i in range(sa.EXPECT[b]):
                u = f"{b}_{i}"
                dB = (self.xD[u] - self.x_cv) / src.get(b, 1.0)
                dA = dB / side.get(b, 1.0)
                self.save("B", u, self.x_cv + dB, self.x_t, self.cv_flux)
                if b == sa.FLUX and pure_norm:
                    # Phi_u with x_cv (Phi_CV / Phi_u - 1) = dA exactly: a pure normalization universe
                    phi = self.cv_flux * self.x_cv / (self.x_cv + dA)
                else:
                    phi = self.cv_flux * (1.1 if b == sa.FLUX else 1.0)
                self.save("A", u, self.x_cv + dA, self.x_t, phi)
                t_u = self.x_t * (1 + self.rng.normal(0, 0.05, 16))      # the universe's own truth
                self.save("Dnom", u, t_u + kap.get(b, 1.0) * dA, t_u, self.cv_flux)

    def committed(self):
        s1 = fs.load_s1(self.s1)
        d = fs.derivation_blocks(self.root / "derivation", inv.DER_TAG, s1, self.constraint)
        per_group = {}
        for grp, bs in pfd.GROUPS.items():
            e = sum(d["carried"][f"band:{b}"] for b in bs)
            mm = sum(s1["blocks"][f"band:{b}"] for b in bs)
            per_group[grp] = np.sqrt(np.diag(e) / np.diag(mm)).tolist()
        self.gate_d = self.tmp / "gate-d.json"
        self.gate_d.write_text(json.dumps({"per_group_sigma_ratio": per_group}))
        self.diag = self.tmp / "diag.json"
        self.diag.write_text(json.dumps({"per_band": {b: {"sigma_ratio": fdg.ratio(np.diag(d["carried"][f"band:{b}"]),
                                                                                    np.diag(s1["blocks"][f"band:{b}"]))}
                                                      for b in pfd.BANDS}}))
        self.i0 = self.tmp / "i0.json"
        self.i0.write_text(json.dumps({"floor": {"kind": "measured", "upper_factor": {"data": 1.878, "nom": 1.878}},
                                       "sigma_J_data": (self.sigma * self.f).tolist(),
                                       "sigma_J_nom_carried": (self.sigma * self.f).tolist()}))

    def base_patches(self):
        return [mock.patch.object(fs, "S1_NPZ_SHA256", digest(self.s1)),
                mock.patch.object(sa, "CONSTRAINT_SHA256", digest(self.constraint)), plain_noatime()]

    @contextlib.contextmanager
    def patched(self, gate=True):
        ps = self.base_patches()
        for p in ps:
            p.start()
        try:
            if not hasattr(self, "gate_d"):
                self.committed()
            if gate:
                with mock.patch.object(fdg, "GATE_D_SHA256", digest(self.gate_d)):
                    yield
            else:
                yield
        finally:
            for p in reversed(ps):
                p.stop()

    def run(self):
        with self.patched():
            return pfd.readout(self.root, self.unf, self.gate_d, self.diag, self.i0)


class Readout(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fd1b-pfd-ro-"))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_matching_toys_reproduce_and_kappa_passes(self):
        r = Staged(self.tmp).run()
        for grp in ("flux", "detector"):
            g = r["groups"][grp]
            self.assertEqual(g["rule_S"]["verdict"], "REPRODUCED")
            self.assertEqual(g["rule_K"]["verdict"], "PASS")
            np.testing.assert_allclose(g["factors"]["F_src"], 1.0, rtol=1e-12)
            self.assertEqual(g["rule_F"]["n_cells"], 0)

    def test_toys_off_by_twenty_percent_depart(self):
        r = Staged(self.tmp, src={sa.FLUX: 1.2}).run()
        self.assertEqual(r["bands"][sa.FLUX]["rule_S"]["verdict"], "DEPARTS")
        self.assertEqual(len(r["bands"][sa.FLUX]["rule_S"]["cells_outside"]), 16)
        np.testing.assert_allclose(r["groups"]["flux"]["factors"]["F_src"], 1.2, rtol=1e-12)
        self.assertEqual(r["groups"]["detector"]["rule_S"]["verdict"], "REPRODUCED")

    def test_the_attribution_lands_on_the_factor_the_fixture_sets(self):
        # rho_flux = 1/m = 1.5, all of it in F_side; rho_det = 1/m = 0.7, all of it in F_truth
        b = sa.DETECTOR_BANDS
        r = Staged(self.tmp, m={sa.FLUX: 1 / 1.5, **{x: 1 / 0.7 for x in b}}, side={sa.FLUX: 1.5}).run()
        fl, de = r["groups"]["flux"], r["groups"]["detector"]
        np.testing.assert_allclose(fl["factors"]["F_side"], 1.5, rtol=1e-12)
        self.assertEqual((fl["rule_F"]["n_cells"], fl["rule_F"]["level"]["F_side"]), (16, "account"))
        self.assertEqual(fl["rule_F"]["level"]["F_truth"], "refuted")
        self.assertEqual((de["rule_F"]["n_cells"], de["rule_F"]["level"]["F_truth"]), (16, "account"))

    def test_kappa_off_by_twenty_percent_fails(self):
        r = Staged(self.tmp, kap={"MinosEfficiency": 1.2}).run()
        self.assertEqual(r["bands"]["MinosEfficiency"]["rule_K"]["verdict"], "FAIL")
        self.assertEqual(r["bands"][sa.FLUX]["rule_K"]["verdict"], "PASS")

    def test_noise_cells_are_not_read(self):
        r = Staged(self.tmp, src={sa.FLUX: 1.2}, kap={sa.FLUX: 1.2}, sigma=1.0).run()   # every block under its floor
        self.assertEqual(r["bands"][sa.FLUX]["rule_S"], {"verdict": "REPRODUCED", "cells_outside": [],
                                                          "values_outside": [], "n_resolved": 0})
        self.assertEqual((r["bands"][sa.FLUX]["rule_K"]["verdict"], r["bands"][sa.FLUX]["rule_K"]["n_resolved"]),
                         ("PASS", 0))

    def test_kappas_floor_is_uncarried(self):
        # a floor set per cell so that A_unc sits above the uncarried floor (0.8 x A_unc) and below the carried one
        # (0.8 g^2 x A_unc, g = 1.2): the band's kappa cells are resolved only with the uncarried floor
        st = Staged(self.tmp)
        X = np.array([st.x_cv + (st.xD[f"MinosEfficiency_{i}"] - st.x_cv) for i in (0, 1)])
        a_unc = np.diag(sa.mat_cov(X))
        c = pfd.RESOLVE_K * inv.noise_factor("MinosEfficiency", st.w) * 1.878
        s_n = np.sqrt(0.8 * a_unc * st.g ** 2 / c)
        with st.patched(gate=False):
            st.committed()
        z = json.loads(st.i0.read_text())
        z["sigma_J_nom_carried"] = s_n.tolist()
        st.i0.write_text(json.dumps(z))
        r = st.run()
        self.assertEqual(r["bands"]["MinosEfficiency"]["rule_K"]["n_resolved"], 16)

    def test_a_phi_equals_a_for_pure_normalization_universes(self):
        r = Staged(self.tmp, pure_norm=True).run()
        np.testing.assert_allclose(r["descriptive"]["sqrt_A_phi_over_A_flux"], 1.0, rtol=1e-9)

    def test_controls_refuse(self):
        def broken(fn, why):
            st = Staged(self.tmp / f"c{len(list(self.tmp.iterdir()))}")
            with st.patched():
                fn(st)
            with st.patched(), self.assertRaisesRegex(fs.Invalid, why):
                pfd.readout(st.root, st.unf, st.gate_d, st.diag, st.i0)

        def gate_ratio(st):
            z = json.loads(st.gate_d.read_text())
            z["per_group_sigma_ratio"]["flux"][0] = float(np.nextafter(z["per_group_sigma_ratio"]["flux"][0], 9.0))
            st.gate_d.write_text(json.dumps(z))

        def diag_ratio(st):
            z = json.loads(st.diag.read_text())
            z["per_band"]["GEANT_Pion"]["sigma_ratio"][3] *= 1.0000001
            st.diag.write_text(json.dumps(z))

        def s1_block(st):
            p = st.root / "uni" / f"{inv.S1_TAG}_GEANT_Proton_0.npz"
            np.savez_compressed(p, xsec_flat=sa.xs(p) * 1.0000001)

        def cv_product(st):
            st.save("Dnom", "CV", st.x_cv * (1 + 1e-12), st.x_t, st.cv_flux)

        def wrong_flux_in_a(st):
            st.save("A", "Flux_4", st.x_cv, st.x_t, st.cv_flux)        # a Flux universe unfolded with Phi_CV

        def wrong_flux_in_dnom(st):
            phi = st.cv_flux * 1.1
            st.save("Dnom", "Flux_4", st.x_t, st.x_t, phi)              # Dnom unfolded with Phi_u

        def flux_array_mismatch(st):
            st.save("B", "Flux_4", st.x_cv, st.x_t, st.cv_flux * 1.1, meta=st.meta("B", "Flux_4", st.cv_flux))

        def one_code(st):
            mt = st.meta("B", "GEANT_Pion_1", st.cv_flux)
            mt["pins_sha256"] = "q" * 64
            st.save("B", "GEANT_Pion_1", st.x_cv, st.x_t, st.cv_flux, meta=mt)

        def flux_file(st):
            (st.root / "staged.json").write_text(json.dumps({"staged": [{"role": "flux-file", "sha256": "e" * 64}],
                                                              "missing": []}))

        for fn, why in ((gate_ratio, "flux ratio does not reproduce gate D"),
                        (diag_ratio, "GEANT_Pion: the per-band ratio does not reproduce the diagnosis"),
                        (s1_block, "band GEANT_Proton: the staged S1 unfolds do not reproduce"),
                        (cv_product, "mode Dnom at CV does not reproduce"),
                        (wrong_flux_in_a, "A_Flux_4.npz: its unfolding flux is not mode A's"),
                        (wrong_flux_in_dnom, "Dnom_Flux_4.npz: its unfolding flux is not mode Dnom's"),
                        (flux_array_mismatch, "B_Flux_4.npz: its flux array is not the one"),
                        (one_code, "pins_sha256 takes 2 values"),
                        (flux_file, "flux file is not the staged one")):
            with self.subTest(fn.__name__):
                broken(fn, why)

    def test_gate_d_must_be_the_committed_readout(self):
        st = Staged(self.tmp)
        with st.patched(gate=False), self.assertRaises(fs.Invalid):
            pfd.readout(st.root, st.unf, st.gate_d, st.diag, st.i0)


if __name__ == "__main__":
    unittest.main()
