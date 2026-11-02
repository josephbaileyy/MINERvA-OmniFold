"""Controls for 1B's mode D and its grid check (state/measurement-paper/5d-community-20261024/FD-1B-MODED-DECLARATION.md),
each rule in the direction it acts and in the other:

* the grids: nominal is the fine grid; coarse keeps every H2 edge and nests in the fine grid; fine halves every cell;
* the grid check's B and C at the nominal grid are I2's modes bitwise, and another grid changes them;
* the D experiment: at CV and r = 1 it is the derivation's CV experiment bitwise; for a universe its pseudo-data are
  the universe's weights x r and its unfolding MC is the CV's; the data-like factor rescales each reporting cell's
  truth to f exactly; rows outside the reported grid keep weight 1;
* the jobs: Dnom's CV product is the derivation's CV product bitwise; the Ddl job refuses without its truth, with a
  wrong digest or against another nominal truth; --grid is required for B and C and refused for D; the grid check's
  universes are the declared six; an atime move exits 8;
* the pilot trigger, rule D (PASS / PARTIAL / FAIL, R00 and R05 not exempt), the matched-truth reading and the grid
  reading, each at its edges;
* the readout end to end on staged synthetic products: D equal to S1 passes, D 1.2x S1 fails, and every control
  refuses (Dnom CV, the data-like truth, the nominal grid against I2, one code, the dl digest, M); it reads with
  O_NOATIME only.

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

import fd_1b_inv as inv  # noqa: E402
import fd_1b_moded as md  # noqa: E402
import fd_1b_score as fs  # noqa: E402
import fd_1b_toys as toys  # noqa: E402
import s1_assemble as sa  # noqa: E402
import s5c_unfold  # noqa: E402
import s5n_pseudo  # noqa: E402
import s5p_stage1_inspect as s1i  # noqa: E402
from test_fd_1b import EDGES, World as ToyWorld, digest, fake_unfold  # noqa: E402
from test_fd_1b_inv import Staged, plain_noatime  # noqa: E402

TOY_FINE = dict(zip(s1i.AXES, [e.tolist() for e in EDGES]))
TOY_H2 = {"pt": [0.0, 2.0], "pz": [0.0, 1.0, 2.0], "eavail": [0.0, 1.0], "q3": [0.0, 1.0, 3.0], "W": [0.0, 3.0]}
N_FINE = int(np.prod([len(e) - 1 for e in EDGES]))
TOY_FM = np.where(np.arange(N_FINE) < N_FINE - 4, np.arange(N_FINE) % 16, -1).astype("<i4")


def toy_grid():
    return [mock.patch.object(s1i, "FINE", TOY_FINE), mock.patch.object(s1i, "H2_EDGES", TOY_H2)]


# ------------------------------------------------------------------------------------------------------------ grids


class Grids(unittest.TestCase):
    def test_nominal_is_the_fine_grid(self):
        for e, a in zip(md.grid_edges("nominal"), s1i.AXES):
            self.assertTrue(np.array_equal(e, np.asarray(s1i.FINE[a], float)))

    def test_coarse_keeps_every_h2_edge_and_nests_in_the_fine_grid(self):
        for e, a in zip(md.grid_edges("coarse"), s1i.AXES):
            fine = np.asarray(s1i.FINE[a], float)
            self.assertTrue(set(s1i.H2_EDGES[a]) <= set(e.tolist()), a)
            self.assertTrue(set(e.tolist()) <= set(fine.tolist()), a)
            self.assertEqual((e[0], e[-1]), (fine[0], fine[-1]))
        self.assertEqual([len(e) - 1 for e in md.grid_edges("coarse")], [7, 8, 4, 4, 4])

    def test_fine_halves_every_cell(self):
        for e, a in zip(md.grid_edges("fine"), s1i.AXES):
            fine = np.asarray(s1i.FINE[a], float)
            self.assertEqual(len(e) - 1, 2 * (len(fine) - 1))
            np.testing.assert_array_equal(e[::2], fine)
        self.assertEqual(int(np.prod([len(e) - 1 for e in md.grid_edges("fine")])), 65_856 * 32)

    def test_an_unknown_grid_refuses(self):
        with self.assertRaises(ValueError):
            md.grid_edges("medium")


class ToyCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="fd1b-moded-"))
        cls.w = ToyWorld(cls.tmp)
        cls.inputs = s5c_unfold.load_inputs(cls.w.inputs)
        bz = np.load(cls.w.bkg, allow_pickle=True)
        cls.bkg = {"bkg_reco": bz["bkg_reco"], "bkg_w": bz["bkg_w"], "bkg_nd": bz["bkg_nd"]}
        z = dict(np.load(cls.w.bank / "cv.npz", allow_pickle=True))
        rng = np.random.default_rng(3)
        for k, e in zip(("td_pt", "td_pz", "td_ea", "td_q3", "td_w"), cls.inputs["edges"]):
            z[k] = rng.uniform(e[0], e[-1], 50)
        cls.bank_cv = z
        # the jobs build mode A's universe MC from the bank's own cv.npz: this module's private world carries the
        # truth-denominator coordinates there too, with its manifest and pins re-made over the changed file
        np.savez(cls.w.bank / "cv.npz", **z)
        cls.w.manifest.write_text("".join(f"{digest(p)}  {p}\n" for p in sorted(cls.w.bank.iterdir()))
                                  + f"{digest(cls.w.receipt)}  {cls.w.receipt}\n")
        cls.w.pins.write_text(json.dumps(toys.make_pins(cls.w.bank, cls.w.det, cls.w.manifest, cls.w.receipt)))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def setUp(self):
        self.ps = self.w.patches() + [plain_noatime()] + toy_grid()
        for p in self.ps:
            p.start()

    def tearDown(self):
        for p in reversed(self.ps):
            p.stop()


class GridModes(ToyCase):
    def test_the_nominal_grid_is_i2s_b_and_c_bitwise(self):
        for mode in md.GRID_MODES:
            for u in ("MaRES_0", "LowQ2_1"):
                mine = md.grid_inputs(mode, u, "nominal", self.inputs, self.bkg, self.w.bank)
                ref = inv.mode_inputs(mode, u, self.inputs, self.bkg, self.w.bank, self.bank_cv)
                for k in ("w_truth", "w_reco", "denom_nd"):
                    np.testing.assert_array_equal(np.asarray(mine[0][k], float), np.asarray(ref[0][k], float), (mode, u, k))
                np.testing.assert_array_equal(mine[1]["bkg_w"], ref[1]["bkg_w"])

    def test_another_grid_changes_the_factors_and_leaves_the_rest(self):
        for mode, key in (("B", "w_reco"), ("C", "w_truth")):
            nom = md.grid_inputs(mode, "MaRES_0", "nominal", self.inputs, self.bkg, self.w.bank)[0]
            for g in ("coarse", "fine"):
                ui = md.grid_inputs(mode, "MaRES_0", g, self.inputs, self.bkg, self.w.bank)[0]
                self.assertFalse(np.array_equal(ui[key], nom[key]), (mode, g))
                for e, f in zip(ui["edges"], self.inputs["edges"]):     # the unfolding grid is untouched
                    np.testing.assert_array_equal(e, f)
            if mode == "B":
                self.assertIs(ui["w_truth"], self.inputs["w_truth"])

    def test_cv_is_the_cv_on_every_grid(self):
        for mode in md.GRID_MODES:
            for g in md.GRIDS:
                ui, ub, _ = md.grid_inputs(mode, "CV", g, self.inputs, self.bkg, self.w.bank)
                for k in ("w_truth", "w_reco", "denom_nd"):
                    self.assertIs(ui[k], self.inputs[k])

    def test_the_fine_grid_check_refuses_foreign_edges(self):
        with self.assertRaisesRegex(inv.Refusal, "FINE"):
            md.check_fine_grid(dict(self.inputs, edges=[e * 2 for e in self.inputs["edges"]]))
        md.check_fine_grid(self.inputs)


class DExperiment(ToyCase):
    def test_at_cv_and_nominal_truth_it_is_the_derivations_cv_experiment(self):
        exp_cv, x_cv = inv.nominal_experiment(self.inputs, self.bkg)
        r = s5n_pseudo.truth_weight("nominal", self.inputs, 0.0, None)
        exp, x = md.d_experiment(self.inputs, self.bkg, dict(self.inputs), dict(self.bkg), r)
        for k in exp_cv:
            if k == "edges":
                self.assertTrue(all(np.array_equal(a, b) for a, b in zip(exp[k], exp_cv[k])))
            else:
                self.assertTrue(np.array_equal(np.asarray(exp[k]), np.asarray(exp_cv[k])), k)
        np.testing.assert_array_equal(x, x_cv)

    def test_nature_is_the_universe_and_the_unfolding_mc_is_the_cv(self):
        exp_cv, x_cv = inv.nominal_experiment(self.inputs, self.bkg)
        ui, ub, _ = inv.mode_inputs("A", "MaRES_1", self.inputs, self.bkg, self.w.bank, self.bank_cv)
        r = np.random.default_rng(1).uniform(0.8, 1.2, self.inputs["MCgen"].shape[0])
        exp, x = md.d_experiment(self.inputs, self.bkg, ui, ub, r)
        for k in inv.MC_KEYS:
            np.testing.assert_array_equal(np.asarray(exp[k]), np.asarray(exp_cv[k]), k)
        reco = np.asarray(self.inputs["pass_reco"], bool)
        lam = np.concatenate([np.asarray(ui["w_reco"], float)[reco] * r[reco], np.asarray(ub["bkg_w"], float)])
        xy = np.concatenate([self.inputs["MCreco"][reco], self.bkg["bkg_reco"]])
        keep = (lam > 0) & s5n_pseudo.fid_mask(xy, self.inputs["edges"])
        np.testing.assert_allclose(np.sort(exp["obs_counts"]), np.sort(lam[keep]), rtol=1e-15)
        self.assertFalse(np.array_equal(exp["obs_counts"], exp_cv["obs_counts"]))
        half = dict(ui, w_truth=0.5 * np.asarray(ui["w_truth"], float))
        np.testing.assert_array_equal(x, s5n_pseudo.true_xsec(half, np.ones(self.inputs["MCgen"].shape[0], bool), r))
        self.assertFalse(np.array_equal(x, x_cv))

    def test_the_data_like_factor_rescales_each_cells_truth_exactly(self):
        with mock.patch.object(sa, "fine_map", lambda d: TOY_FM):
            U = sa.functional_matrix(TOY_FM)
        cell = md.row_cell(self.inputs, TOY_FM)
        r_cell = np.linspace(0.7, 1.4, 16)
        r = md.dl_weight(cell, r_cell)
        _, x_t = inv.nominal_experiment(self.inputs, self.bkg)
        _, x = md.d_experiment(self.inputs, self.bkg, dict(self.inputs), dict(self.bkg), r)
        ux = U @ np.ravel(x_t)
        np.testing.assert_allclose(U @ np.ravel(x), r_cell * ux, rtol=1e-12)
        self.assertTrue(np.all(r[cell < 0] == 1.0))
        self.assertTrue(np.any(cell < 0))
        np.testing.assert_array_equal(r[cell >= 0], r_cell[cell[cell >= 0]])

    def test_a_fine_map_of_another_size_refuses(self):
        with self.assertRaisesRegex(inv.Refusal, "fine map"):
            md.row_cell(self.inputs, TOY_FM[:-1])


class Jobs(ToyCase):
    def argv(self, mode, out, universes="CV", grid=None, dl=None, dl_sha=None, definition=None):
        a = ["unfold", "--mode", mode, "--universes", universes, "--npz", str(self.w.inputs), "--bkg", str(self.w.bkg),
             "--bank", str(self.w.bank), "--detector-dir", str(self.w.det), "--pins", str(self.w.pins),
             "--expect-pins-sha256", digest(self.w.pins), "--out", str(out), "--tag", "t"]
        a += ["--grid", grid] if grid else []
        a += ["--dl", str(dl)] if dl else []
        a += ["--expect-dl-sha256", dl_sha] if dl_sha else []
        a += ["--definition", str(definition)] if definition else []
        return a

    def refuses(self, argv, msg):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(md.main(argv), 4)
        self.assertIn(msg, err.getvalue())

    def dl_file(self, ux=None):
        _, x_t = inv.nominal_experiment(self.inputs, self.bkg)
        U = sa.functional_matrix(TOY_FM)
        p = self.tmp / f"dl-{len(list(self.tmp.glob('dl-*')))}.json"
        p.write_text(json.dumps({"schema": md.SCHEMA, "r_cell": np.linspace(0.8, 1.2, 16).tolist(),
                                 "U_xT": (U @ np.ravel(x_t) if ux is None else ux).tolist()}))
        return p

    def test_dnoms_cv_product_is_the_derivations_cv_product(self):
        out_d, out = self.tmp / "der", self.tmp / "dnom"
        with mock.patch.object(s5n_pseudo, "unfold_negweight", fake_unfold):
            self.assertEqual(toys.main(self.w.run_argv("derivation", "derivation", out_d, universes="CV")), 0)
            self.assertEqual(md.main(self.argv("Dnom", out, "CV,MaRES_0")), 0)
        a = np.load(out_d / "t_CV.npz")["xsec_flat"]
        self.assertTrue(np.array_equal(a, np.load(out / "t_Dnom_CV.npz")["xsec_flat"]))
        z = np.load(out / "t_Dnom_MaRES_0.npz")
        self.assertFalse(np.array_equal(z["xsec_flat"], a))
        meta = json.loads(str(z["meta"]))
        self.assertEqual((meta["truth"], meta["dl_sha256"], meta["grid"]), ("nominal", None, None))
        self.assertIsInstance(meta["peak_rss_kib"], int)
        self.assertGreater(meta["peak_rss_kib"], 0)

    def test_ddl_runs_with_its_truth_and_refuses_without_it_or_against_another(self):
        dl = self.dl_file()
        definition = self.tmp / "def.json"
        definition.write_text("{}")
        with mock.patch.object(s5n_pseudo, "unfold_negweight", fake_unfold), \
                mock.patch.object(sa, "fine_map", lambda d: TOY_FM):
            out = self.tmp / "ddl"
            self.assertEqual(md.main(self.argv("Ddl", out, "CV", dl=dl, dl_sha=digest(dl), definition=definition)), 0)
            z = np.load(out / "t_Ddl_CV.npz")
            meta = json.loads(str(z["meta"]))
            self.assertEqual((meta["truth"], meta["dl_sha256"]), ("data-like", digest(dl)))
            # the job applies the factors: its CV nature's truth is r_c x (U x_T)_c in every cell
            d = json.loads(dl.read_text())
            np.testing.assert_allclose(sa.functional_matrix(TOY_FM) @ z["xtrue_flat"],
                                       np.asarray(d["r_cell"]) * np.asarray(d["U_xT"]), rtol=1e-12)
            self.refuses(self.argv("Ddl", self.tmp / "x1", "CV"), "Ddl needs --dl")
            self.refuses(self.argv("Ddl", self.tmp / "x2", "CV", dl=dl, dl_sha="0" * 64, definition=definition),
                         "digest differs from the declared data-like truth")
            bad = self.dl_file(ux=np.ones(16))
            self.refuses(self.argv("Ddl", self.tmp / "x3", "CV", dl=bad, dl_sha=digest(bad), definition=definition),
                         "not the one the data-like factors were made against")

    def test_grid_is_required_for_b_and_c_and_refused_for_d(self):
        with mock.patch.object(s5n_pseudo, "unfold_negweight", fake_unfold):
            self.refuses(self.argv("B", self.tmp / "y1", "CV"), "--grid is required")
            self.refuses(self.argv("Dnom", self.tmp / "y2", "CV", grid="fine"), "--grid is required")
            self.assertEqual(md.main(self.argv("C", self.tmp / "y3", "MaRES_0", grid="coarse")), 0)
            self.assertTrue((self.tmp / "y3" / "t_C_coarse_MaRES_0.npz").exists())

    def test_the_grid_check_runs_only_its_six_universes(self):
        with mock.patch.object(s5n_pseudo, "unfold_negweight", fake_unfold):
            self.refuses(self.argv("B", self.tmp / "z1", "LowQ2_1", grid="fine"), "grid check's declared universes")
            self.refuses(self.argv("Dnom", self.tmp / "z2", "Flux_3"), "not one of the 67 interaction universes")

    def test_the_job_exits_non_zero_when_an_opened_files_atime_moves(self):
        out = self.tmp / "atime"

        def touching(exp, *a, **k):
            st = os.stat(self.w.inputs)
            os.utime(self.w.inputs, ns=(st.st_atime_ns + 10 ** 9, st.st_mtime_ns))
            return fake_unfold(exp, *a, **k)

        with mock.patch.object(s5n_pseudo, "unfold_negweight", touching):
            self.assertEqual(md.main(self.argv("Dnom", out, "CV")), 8)
        self.assertEqual(json.loads(next(out.glob("atime-*.json")).read_text())["moved"], [str(self.w.inputs)])


# ------------------------------------------------------------------------------------------- the pilot's trigger


class PilotWalls(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fd1b-moded-walls-"))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write(self, seconds=900.0, rss=20_000_000, skip=None, over=None):
        for mode, grid, u in md.PILOT:
            if (mode, grid, u) == skip:
                continue
            s, r = over[1:] if over and over[0] == (mode, grid, u) else (seconds, rss)
            np.savez_compressed(self.tmp / md.product_name("t", mode, grid, u), xsec_flat=np.zeros(3),
                                meta=json.dumps({"mode": mode, "grid": grid, "universe": u, "seconds_unfold": s,
                                                 "peak_rss_kib": r}))

    def cli(self):
        return md.main(["walls", "--unfolds", str(self.tmp), "--tag", "t", "--out", str(self.tmp / f"w{len(list(self.tmp.glob('w*')))}.json")])

    def test_inside_both_limits_passes_at_the_edges(self):
        self.write(seconds=md.UNIT_SECONDS, rss=md.RSS_LIMIT_KIB)
        self.assertEqual(md.pilot_walls(self.tmp, "t")["verdict"], "PASS")
        self.assertEqual(self.cli(), 0)

    def test_one_slow_unfold_or_one_large_rss_reprices(self):
        self.write(over=(("B", "fine", "MaRES_0"), md.UNIT_SECONDS + 0.1, 20_000_000))
        self.assertEqual(md.pilot_walls(self.tmp, "t")["verdict"], "REPRICE")
        self.assertEqual(self.cli(), 1)
        self.write(over=(("Ddl", None, "2p2h_0"), 900.0, md.RSS_LIMIT_KIB + 1))
        self.assertEqual(md.pilot_walls(self.tmp, "t")["verdict"], "REPRICE")

    def test_a_missing_pilot_product_refuses(self):
        self.write(skip=("Dnom", None, "CV"))
        with self.assertRaisesRegex(inv.Refusal, "missing"):
            md.pilot_walls(self.tmp, "t")
        self.assertEqual(self.cli(), 4)

    def test_the_declared_constants(self):
        self.assertEqual(md.UNIT_SECONDS, 1062.0)
        self.assertEqual(md.RSS_LIMIT_KIB, 44_040_192)
        self.assertEqual(len(set(md.PILOT)), 8)
        self.assertEqual(len(set(md.GRID_UNIVERSES)), 6)
        self.assertTrue(set(md.GRID_UNIVERSES) <= {f"{b}_{i}" for b in inv.INTERACTION for i in range(sa.EXPECT[b])})


# ---------------------------------------------------------------------------------------------------------- rules


class Rules(unittest.TestCase):
    def test_rule_d_reads_pass_partial_and_fail_at_its_edges(self):
        self.assertEqual(md.d_outcome(np.full(16, 1.0))["verdict"], "PASS")
        self.assertEqual(md.d_outcome(np.r_[np.full(15, 1.0), 0.9])["verdict"], "PASS")    # the edge is inside
        self.assertEqual(md.d_outcome(np.r_[np.full(15, 1.0), 1.1])["verdict"], "PASS")
        r = md.d_outcome(np.r_[np.full(8, 1.0), np.full(8, 1.3)])
        self.assertEqual((r["verdict"], r["cells_in_window"], r["next"]), ("PARTIAL", 8, "to Joseph"))
        r = md.d_outcome(np.r_[np.full(7, 1.0), np.full(9, 0.5)])
        self.assertEqual((r["verdict"], len(r["below"]), r["next"]), ("FAIL", 9, "to Joseph"))

    def test_r00_and_r05_are_not_exempt(self):
        for c in (0, 5):
            rho = np.ones(16)
            rho[c] = 1.5
            r = md.d_outcome(rho)
            self.assertEqual((r["verdict"], r["above"]), ("PARTIAL", [f"R{c:02d}"]))

    def test_the_matched_truth_reading(self):
        self.assertEqual(md.kappa_reading(np.r_[np.full(8, 1.0), np.full(8, 2.0)])["reading"], "matched")
        self.assertEqual(md.kappa_reading(np.r_[np.full(7, 1.0), np.full(9, 2.0)])["reading"], "unmatched")

    def test_the_grid_reading(self):
        flat = md.grid_reading(np.ones(16), np.ones(16))
        self.assertEqual((flat["grid_dependent"], flat["subcell_hypothesis_supported"]), (False, False))
        hyp = md.grid_reading(np.full(16, 1.3), np.full(16, 0.7))
        self.assertEqual((hyp["grid_dependent"], hyp["subcell_hypothesis_supported"]), (True, True))
        # moving with the grid the other way is grid dependence without the hypothesis
        rev = md.grid_reading(np.full(16, 0.7), np.full(16, 1.3))
        self.assertEqual((rev["grid_dependent"], rev["subcell_hypothesis_supported"]), (True, False))
        edge = md.grid_reading(np.r_[np.full(8, 1.2), np.ones(8)], np.r_[np.full(7, 0.8), np.ones(9)])
        self.assertEqual((edge["grid_dependent"], edge["subcell_hypothesis_supported"]), (True, False))


# ---------------------------------------------------------------------------------------------------------- readout


class Readout(unittest.TestCase):
    ONE = Staged.ONE

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fd1b-moded-read-"))
        self.w = Staged(self.tmp)
        self.ps = self.w.patches() + [plain_noatime()]
        for p in self.ps:
            p.start()
        self.s1 = fs.load_s1(self.w.s1)
        self.d = fs.derivation_blocks(self.w.root / "derivation", inv.DER_TAG, self.s1, self.w.constraint)
        m = sum(v for k, v in self.s1["blocks"].items() if k.startswith("band:") and sa.group_of(k) == "interaction")
        self.i2 = self.tmp / "i2.json"
        self.i2.write_text(json.dumps({"M": np.diag(m).tolist(), "A": (np.diag(m) * self.d["g"] ** 2).tolist(),
                                       "factors": {"F_truth": [1.0] * 16}}))
        self.i0 = self.tmp / "i0.json"
        self.i0.write_text(json.dumps({"g": self.d["g"].tolist()}))
        self.dl = self.tmp / "dl.json"
        self.dl.write_text(json.dumps({"schema": md.SCHEMA, "r_cell": (self.w.f / self.w.x_t).tolist()}))
        self.definition = self.tmp / "def.json"

    def tearDown(self):
        for p in reversed(self.ps):
            p.stop()
        shutil.rmtree(self.tmp)

    def write(self, scale=1.0, tamper=None):
        u_dir, i2_dir = self.tmp / "unf", self.tmp / "i2unf"
        shutil.rmtree(u_dir, ignore_errors=True)
        shutil.rmtree(i2_dir, ignore_errors=True)
        u_dir.mkdir()
        i2_dir.mkdir()
        f = self.w.f
        cv_der = np.load(self.w.root / "derivation" / f"{inv.DER_TAG}_CV.npz")["xsec_flat"]
        dl_sha = digest(self.dl)

        def save(name, x, t, **meta):
            meta = {"schema": md.SCHEMA, **self.ONE, **meta}
            np.savez_compressed(u_dir / name, xsec_flat=x, xtrue_flat=t, meta=json.dumps(meta))

        for mode in md.D_MODES:
            sha = dl_sha if mode == "Ddl" else None
            t_cv = f.copy() if mode == "Ddl" else self.w.x_t.copy()
            if tamper == "dl-truth" and mode == "Ddl":
                t_cv = f * (1 + 1e-9)
            x_cv = cv_der * (1 + 1e-15) if tamper == "dnom-cv" and mode == "Dnom" else (cv_der if mode == "Dnom" else f)
            save(md.product_name("t", mode, None, "CV"), x_cv, t_cv, mode=mode, grid=None, universe="CV", dl_sha256=sha)
            for b in inv.INTERACTION:
                for i in range(sa.EXPECT[b]):
                    xs1 = np.load(self.w.root / "uni" / f"{inv.S1_TAG}_{b}_{i}.npz")["xsec_flat"]
                    t = t_cv * (1 + 0.01 * (i + 1))
                    meta = dict(mode=mode, grid=None, universe=f"{b}_{i}", dl_sha256=sha)
                    if tamper == "one" and (mode, b, i) == ("Ddl", "MaRES", 1):
                        meta["iters"] = 6
                    if tamper == "sha" and (mode, b, i) == ("Ddl", "MaRES", 1):
                        meta["dl_sha256"] = "0" * 64
                    save(md.product_name("t", mode, None, f"{b}_{i}"), t + scale * (xs1 - f), t, **meta)
        for mode in md.GRID_MODES:
            for g in md.GRIDS:
                for k, u in enumerate(md.GRID_UNIVERSES):
                    x = cv_der * (1 + 0.01 * (k + 1) * {"coarse": 1.3, "nominal": 1.0, "fine": 0.7}[g])
                    save(md.product_name("t", mode, g, u), x, self.w.x_t, mode=mode, grid=g, universe=u, dl_sha256=None)
                    if g == "nominal":
                        ref = x * (1 + 1e-15) if tamper == "grid" and (mode, k) == ("C", 2) else x
                        np.savez_compressed(i2_dir / f"fd1b_inv_{mode}_{u}.npz", xsec_flat=ref)
        return u_dir, i2_dir

    def go(self, u_dir, i2_dir, i2=None):
        with mock.patch.object(sa, "fine_map", lambda d: None), mock.patch.object(sa, "functional_matrix", lambda fm: np.eye(16)):
            return md.readout(self.w.root, u_dir, i2_dir, i2 or self.i2, self.i0, self.dl, self.definition, "t")

    def test_d_equal_to_s1_passes_and_reads_the_grid_hypothesis(self):
        r = self.go(*self.write(scale=1.0))
        np.testing.assert_allclose(r["rho_D"], 1.0, rtol=1e-9)
        self.assertEqual(r["rule_D"]["verdict"], "PASS")
        np.testing.assert_allclose(r["kappa"], 1.0, rtol=1e-9)
        self.assertEqual(r["kappa_reading"]["reading"], "matched")
        for mode in md.GRID_MODES:
            np.testing.assert_allclose(r["grid_check"][mode]["coarse_over_nominal"], 1.3, rtol=1e-9)
            self.assertTrue(r["grid_check"][mode]["reading"]["subcell_hypothesis_supported"])
        self.assertEqual(r["dl_sha256"], digest(self.dl))

    def test_dltruth_is_f_over_the_nominal_truth_per_cell(self):
        with mock.patch.object(sa, "fine_map", lambda d: None), mock.patch.object(sa, "functional_matrix", lambda fm: np.eye(16)):
            r = md.dltruth(self.w.root, self.definition)
        np.testing.assert_allclose(r["r_cell"], self.w.f / self.w.x_t, rtol=1e-15)
        self.assertEqual(r["U_xT"], self.w.x_t.tolist())

    def test_d_larger_than_s1_fails(self):
        r = self.go(*self.write(scale=1.2))
        np.testing.assert_allclose(r["rho_D"], 1.2, rtol=1e-9)
        self.assertEqual((r["rule_D"]["verdict"], len(r["rule_D"]["above"])), ("FAIL", 16))

    def test_controls_refuse(self):
        for tamper, msg in (("dnom-cv", "derivation CV"), ("dl-truth", "is not f"), ("grid", "I2's product"),
                            ("one", "one code"), ("sha", "this data-like truth")):
            with self.assertRaisesRegex(fs.Invalid, msg, msg=tamper):
                self.go(*self.write(tamper=tamper))
        bad = self.tmp / "i2-bad.json"
        r2 = json.loads(self.i2.read_text())
        r2["M"][0] = float(np.nextafter(r2["M"][0], 1.0))
        bad.write_text(json.dumps(r2))
        with self.assertRaisesRegex(fs.Invalid, "I2's M"):
            self.go(*self.write(), i2=bad)

    def test_the_readout_reads_with_o_noatime_only(self):
        u_dir, i2_dir = self.write()
        with mock.patch.object(inv, "load_npz_plain", side_effect=AssertionError("a plain read")):
            self.go(u_dir, i2_dir)
        self.assertTrue(any(str(u_dir) in p for p in inv.OPENED))


if __name__ == "__main__":
    unittest.main()
