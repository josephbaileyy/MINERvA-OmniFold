"""Controls for fd_gencmp_e.py, for the --prediction-set option of fd_g_figures.py and fd_g_figures_check.py, and for
step C-R's refined arm of fd_gencmp.py overlap (FD-GENCMP-AMENDMENT-E-DECLARATION.md), on synthetic inputs. No real
prediction, covariance or data value is read; the real files read are the H2 definition (geometry), the committed
with-block extra block (its digest only) and the committed defs.json (its structure only).

Every control is tested in the direction it acts and in the other: it passes on a consistent fixture and refuses on a
one-entry defect (stage's pin, E0's g and chi2, the chdefs set's file digests, R0's comparison, XC, the figure set
guard, C-R's arm key and C3)."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(1, str(ND))
sys.path.insert(1, str(ND / "tests"))
import fd_cpl_addition as A  # noqa: E402
import fd_g_compare as fg  # noqa: E402
import fd_g_diag as D  # noqa: E402
import fd_g_figures as FG  # noqa: E402
import fd_g_figures_check as FC  # noqa: E402
import fd_gencmp as gc  # noqa: E402
import fd_gencmp_e as E  # noqa: E402
import fd_gencmp_kin as kin  # noqa: E402
import test_fd_gencmp as TG  # noqa: E402  (StepC's synthetic 2D/3D fixture)

REPO = ND.parent
N = gc.N_FINE
RNG = np.random.default_rng(20261102)


def sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def spd(n, scale):
    M = RNG.normal(size=(n, n))
    return (M @ M.T / n + np.eye(n)) * np.outer(scale, scale)


class Sets(unittest.TestCase):
    """The chdefs set's names, cells and labels, and the figure tool's and the checker's legends for it."""

    def test_names_cells_and_order_are_stage_gs(self):
        self.assertEqual([s["name"] for s in E.CHDEFS], [p["name"] for p in fg.PREDICTIONS[:4]])
        self.assertEqual([s["cells"] for s in E.CHDEFS], [p["cells"] for p in fg.PREDICTIONS[:4]])
        self.assertEqual(E.TUNE["name"], "mnvtune_v1")

    def test_every_label_carries_its_legend_qualifiers(self):
        quals, required = FG.PREDICTION_SETS["gencmp-chdefs"]
        for s in E.CHDEFS:
            short = FG.SHORT[s["name"]]
            self.assertTrue(s["label"].startswith(short) and s["label"][len(short)] == ";", s["name"])
            for q in quals[s["name"]]:
                self.assertIn(q, s["label"])
            for r in required:                    # K7: a required string in the label must be drawn
                if r in s["label"]:
                    self.assertIn(r, quals[s["name"]])
        self.assertIn(gc.LABELS["gibuu_CH"], E.CHDEFS[3]["label"])
        self.assertIn(gc.LABELS["nuwro_CH"], E.CHDEFS[2]["label"])

    def test_figure_legend_equals_the_checkers_declared_name_in_both_sets(self):
        try:
            for pset in FG.PREDICTION_SETS:
                FG.use_prediction_set(pset)
                names, _ = FC.PREDICTION_SETS[pset]
                for n in FG.ORDER:
                    self.assertEqual(FG.legend_text(n), names[n], (pset, n))
        finally:
            FG.use_prediction_set(FG.DEFAULT_SET)

    def test_default_set_is_todays(self):
        self.assertIs(FG.PREDICTION_SETS["stage-g"][0], FG.QUALIFIERS)
        self.assertIn(fg.C12_LABEL, FG.PREDICTION_SETS["stage-g"][1])
        self.assertIs(FC.PREDICTION_SETS["stage-g"][0], FC.NAMES)
        self.assertEqual(FG.prediction_set_option(SimpleNamespace(prediction_set="stage-g")), {})
        self.assertEqual(FG.prediction_set_option(SimpleNamespace()), {})
        self.assertEqual(FG.prediction_set_option(SimpleNamespace(prediction_set="gencmp-chdefs")),
                         {"prediction_set": "gencmp-chdefs"})

    def test_figures_refuse_the_chdefs_set_without_its_predictions(self):
        a = SimpleNamespace(prediction_set="gencmp-chdefs", figures=["sens"], out_dir=Path("/nonexistent"))
        with self.assertRaises(fg.Stop) as e:
            FG.run(a)
        self.assertIn("K0", str(e.exception))

    def test_check_chain_compares_against_the_passed_set(self):
        preds = [dict(p) for p in fg.PREDICTIONS]
        g = {"predictions": [{"name": p["name"], "label": p["label"], "sha256": p["sha256"]} for p in preds]}
        # the K1 label check alone, through the same expression check_chain uses
        same = lambda ps: all(p["label"] == s["label"] and p["sha256"] == s["sha256"]  # noqa: E731
                              for p, s in zip(g["predictions"], ps))
        self.assertTrue(same(fg.PREDICTIONS))
        preds[2]["label"] = "something else"
        self.assertFalse(same(preds))


class Stage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.scratch = self.d / "scratch"
        (self.scratch / "x/y").mkdir(parents=True)
        (self.scratch / "x/y/a.npz").write_bytes(b"alpha")
        (self.scratch / "b.txt").write_bytes(b"beta")
        self.pins = {str(self.scratch / "x/y/a.npz"): hashlib.sha256(b"alpha").hexdigest(),
                     str(self.scratch / "b.txt"): hashlib.sha256(b"beta").hexdigest(),
                     str(REPO / "README.md"): "0" * 64}           # outside the scratch root: not staged

    def tearDown(self):
        self.tmp.cleanup()

    def test_copies_under_the_scratch_layout_and_records(self):
        a = SimpleNamespace(scratch=self.scratch, run_dir=self.d / "run")
        self.assertEqual(E.cmd_stage(a, self.pins), 0)
        self.assertEqual((self.d / "run/inputs/x/y/a.npz").read_bytes(), b"alpha")
        rec = json.loads((self.d / "run/inputs/STAGE.json").read_text())
        self.assertEqual(set(rec["copied"]), {"x/y/a.npz", "b.txt"})

    def test_refuses_a_pin_mismatch(self):
        self.pins[str(self.scratch / "b.txt")] = hashlib.sha256(b"betA").hexdigest()
        with self.assertRaises(E.Stop) as e:
            E.cmd_stage(SimpleNamespace(scratch=self.scratch, run_dir=self.d / "run"), self.pins)
        self.assertIn("control S", str(e.exception))

    def test_refuses_overwrite(self):
        a = SimpleNamespace(scratch=self.scratch, run_dir=self.d / "run")
        E.cmd_stage(a, self.pins)
        with self.assertRaises(E.Stop):
            E.cmd_stage(a, self.pins)

    def test_the_inputs_file_pins_every_scratch_input_the_chain_reads(self):
        rel = set(E.scratch_pins(gc.load_pins(E.INPUTS)))
        want = {"s1-20261024/s1_assembly.npz", "cresp-20261026/out/cresp.npz",
                "MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt",
                f"{E.REBUILD}/rebuild.json",
                *(f"s5p-20260926/{p['path']}" for p in fg.PREDICTIONS),
                *(f"{E.REBUILD}/{s}_ana_s{seed}.npz" for spec in E.CHDEFS for s in spec["src"] for seed in kin.SEEDS)}
        self.assertTrue(want <= rel, sorted(want - rel))
        pins = gc.load_pins(E.INPUTS)
        self.assertEqual(pins[str(E.SCRATCH / "s1-20261024/s1_assembly.npz")], A.PINS["s1_npz"])
        self.assertEqual(pins[str(E.SCRATCH / "cresp-20261026/out/cresp.npz")], A.PINS["cresp_npz"])
        for p in fg.PREDICTIONS:
            self.assertEqual(pins[str(E.SCRATCH / "s5p-20260926" / p["path"])], p["sha256"])
        defs = json.loads(E.DEFS.read_text())
        self.assertEqual(pins[str(E.SCRATCH / E.REBUILD / "rebuild.json")], defs["rebuild_json_sha256"])


class Materialize(unittest.TestCase):
    """A synthetic rebuild directory, its defs.json made by fd_gencmp's own functions, and MnvTune v1's file."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.run = self.d / "run"
        self.rb = self.run / "inputs" / E.REBUILD
        self.rb.mkdir(parents=True)
        (self.rb / "rebuild.json").write_text(json.dumps({"status": {}}))
        for spec in E.CHDEFS:
            for s in spec["src"]:
                for seed in kin.SEEDS:
                    np.savez(self.rb / f"{s}_ana_s{seed}.npz", xsec_flat=RNG.uniform(1e-42, 2e-42, N),
                             sumw2_flat=RNG.uniform(1e-90, 2e-90, N), nevt_flat=RNG.integers(0, 9, N).astype(float))
        self.U = gc.cell_matrix()
        f = self.U @ RNG.uniform(1e-42, 2e-42, N)
        C = spd(16, 0.05 * f)
        self.R = {"f": f, "reported": C + spd(16, 0.01 * f), "nopl": C}
        self.write_defs()
        tune = self.run / "inputs" / "s5p-20260926" / E.TUNE["path"]
        tune.parent.mkdir(parents=True)
        np.savez(tune, xsec_flat=np.ones(N))
        self.tune_patch = mock.patch.object(E, "TUNE", {**E.TUNE, "sha256": sha(tune)})
        self.tune_patch.start()

    def tearDown(self):
        self.tune_patch.stop()
        self.tmp.cleanup()

    def write_defs(self, bump=0.0):
        gens = {}
        for spec in E.CHDEFS:
            cells = gc.ALL_CELLS if spec["cells"] == "all" else gc.GIBUU_CELLS
            x, v, _ = E.corner(self.rb, spec["src"])
            g, Vg = gc.integrate(self.U, x, v, cells)
            c = gc.chi2_pair(self.R, g, Vg, cells)
            c["reported"]["total"]["chi2"] *= 1 + bump
            gens[spec["name"]] = {"CH": {"analysis_definitions": {"chi2": c, "g": g[cells].tolist()}}}
        self.defs = self.d / "defs.json"
        self.defs.write_text(json.dumps({"rebuild_json_sha256": sha(self.rb / "rebuild.json"), "generators": gens},
                                        default=float))

    def materialize(self):
        a = SimpleNamespace(run_dir=self.run, defs=self.defs)
        return E.cmd_materialize(a, R=self.R, defs_sha256=sha(self.defs))

    def test_writes_five_predictions_stage_g_accepts(self):
        self.assertEqual(self.materialize(), 0)
        pred = self.run / "pred"
        specs = E.load_chdefs(pred)
        sums = gc.sa.load_manifest(pred / "SHA256SUMS")
        for s in specs[:4]:
            self.assertEqual(sums[s["path"]], s["sha256"])
            self.assertEqual(fg.prediction_problems(pred / s["path"], s), [])
        self.assertEqual(specs[4]["path"], E.TUNE["path"])

    def test_corner_is_defs_combination_bitwise(self):
        x, v, n = E.corner(self.rb, ("nuwro_C12", "nuwro_H"))
        xc, vc, _ = gc.seed_mean(self.rb, "nuwro_C12", kin.SEEDS)
        xh, vh, _ = gc.seed_mean(self.rb, "nuwro_H", kin.SEEDS)
        xx, vv = gc.combine(xc, vc, xh, vh)
        self.assertTrue(np.array_equal(x, xx) and np.array_equal(v, vv))
        self.assertEqual(n.shape, (N,))

    def test_e0_refuses_a_one_entry_defect_in_a_rebuilt_product(self):
        p = self.rb / f"gibuu_H_ana_s{kin.SEEDS[2]}.npz"
        z = dict(np.load(p))
        row = self.U[gc.GIBUU_CELLS[0]]
        fine = int(np.argmax(row))                       # the cell's largest fine volume, so the defect reaches g
        z["xsec_flat"][fine] *= 1 + 1e-6
        np.savez(p, **z)
        with self.assertRaises(E.Stop) as e:
            self.materialize()
        self.assertIn("E0", str(e.exception))

    def test_e0_refuses_a_chi2_off_by_1e_9(self):
        self.write_defs(bump=1e-9)
        with self.assertRaises(E.Stop) as e:
            self.materialize()
        self.assertIn("E0", str(e.exception))

    def test_refuses_another_rebuild_directory(self):
        (self.rb / "rebuild.json").write_text(json.dumps({"status": {"x": 1}}))
        with self.assertRaises(E.Stop):
            self.materialize()

    def test_refuses_an_unpinned_defs(self):
        with self.assertRaises(E.Stop):
            E.cmd_materialize(SimpleNamespace(run_dir=self.run, defs=self.defs), R=self.R, defs_sha256="0" * 64)

    def test_load_chdefs_refuses_a_changed_file(self):
        self.materialize()
        p = self.run / "pred" / "gencmp_e/genie_mec_ch_ana.npz"
        p.write_bytes(p.read_bytes() + b"\0")
        with self.assertRaises(E.Stop) as e:
            E.load_chdefs(self.run / "pred")
        self.assertIn("control P", str(e.exception))

    def test_refuses_overwrite(self):
        self.materialize()
        with self.assertRaises(E.Stop):
            self.materialize()


class Chain(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.c = A.Chain(SimpleNamespace(BA=self.d), self.d / "chain.json")

    def tearDown(self):
        self.tmp.cleanup()

    def test_step_pins_replace_only_the_upstream_and_the_manifest(self):
        H = {"g": "a" * 64, "g_diag": "b" * 64, "g_followup": "c" * 64}
        p = E.step_pins("g_diag", H, {"s5p_sums": "d" * 64})
        self.assertEqual(p["g_readout"], "a" * 64)
        self.assertEqual(p["s5p_sums"], "d" * 64)
        self.assertEqual({k: v for k, v in p.items() if k not in ("g_readout", "s5p_sums")},
                         {k: v for k, v in D.PINS.items() if k not in ("g_readout", "s5p_sums")})
        p = E.step_pins("g_sens2", H, {})
        self.assertEqual((p["g_readout"], p["g_followup_readout"]), ("a" * 64, "c" * 64))
        self.assertEqual(E.step_pins("g", H, {}), fg.PINS)

    def test_arm_blocks_are_the_committed_arms(self):
        p = SimpleNamespace(cresp=Path("/x/cresp.npz"), block=REPO / E.FD / "fd/with-cpl/block/cpl_block.npz")
        xb, name = E.arm_block(p, "nopl")
        self.assertEqual((name, xb[3], xb[5]), ("C_resp", A.PINS["cresp_npz"], "C_resp"))
        xb, name = E.arm_block(p, "with")
        self.assertEqual((name, xb[3], xb[5], xb[7]), (A.NAME, E.BLOCK_SHA256, A.XKEY, A.NAME))
        self.assertEqual(sha(p.block), E.BLOCK_SHA256)

    def test_the_committed_pins_are_the_committed_bytes(self):
        for arm in E.ARMS:
            for k, (rel, pin) in E.COMMITTED[arm].items():
                self.assertEqual(sha(REPO / rel), pin, (arm, k))

    def test_r0_comparison_ignores_argv_and_block_path_only(self):
        old = {"argv": ["a"], "extra_block": {"path": "/p/a", "sha256": "x"}, "v": [1.0, 2.0], "label": "L"}
        new = {"argv": ["b"], "extra_block": {"path": "/q/b", "sha256": "x"}, "v": [1.0, 2.0], "label": "L"}
        self.assertEqual(A.compare_numbers(old, new, E.R0_EXCLUDE) + A.compare_strings(old, new, E.R0_EXCLUDE), [])
        for k, v in (("v", [1.0, 2.0 * (1 + 1e-9)]), ("label", "M")):
            bad = {**new, k: v}
            self.assertTrue(A.compare_numbers(old, bad, E.R0_EXCLUDE) + A.compare_strings(old, bad, E.R0_EXCLUDE))
        bad = {**new, "extra_block": {"path": "/q/b", "sha256": "y"}}
        self.assertTrue(A.compare_strings(old, bad, E.R0_EXCLUDE))

    def xc_fixture(self, bump=0.0):
        gens, preds = {}, []
        for spec in E.CHDEFS:
            g = RNG.uniform(1, 2, 3).tolist()
            chi2 = {k: {"total": {"chi2": float(RNG.uniform(10, 20))}, "shape_only": {"chi2": float(RNG.uniform(5, 9))}}
                    for k in ("reported", "without_C_PL5D")}
            gens[spec["name"]] = {"CH": {"analysis_definitions": {"g": g, "chi2": chi2}}}
            preds.append({"name": spec["name"], "g": g, "total": {"chi2": chi2["reported"]["total"]["chi2"] * (1 + bump)},
                          "shape_only": {"chi2": chi2["reported"]["shape_only"]["chi2"]}})
        preds.append({"name": "mnvtune_v1", "g": [9.0], "total": {"chi2": 1.0}, "shape_only": {"chi2": 1.0}})
        out = self.d / "g.json"
        out.write_text(json.dumps({"predictions": preds}))
        return {"out": {"g": out}}, {"generators": gens}

    def test_xc_passes_when_stage_g_is_defs(self):
        res, defs = self.xc_fixture()
        E.check_xc(self.c, "with", res, defs)

    def test_xc_refuses_a_chi2_off_by_1e_9(self):
        res, defs = self.xc_fixture(bump=1e-9)
        with self.assertRaises(A.Stop) as e:
            E.check_xc(self.c, "with", res, defs)
        self.assertIn("XC", str(e.exception))

    def test_xc_reads_the_matrix_of_its_arm(self):
        res, defs = self.xc_fixture()
        with self.assertRaises(A.Stop):                  # the nopl arm is compared with defs' without_C_PL5D chi2
            E.check_xc(self.c, "nopl", res, defs)

    def test_chain_steps_run_only_with_explicit_pins(self):
        c = E.Chain(SimpleNamespace(BA=self.d, nd=ND), self.d / "c.json", None)
        with self.assertRaises(E.Stop):
            c.run("g", "old-nopl", "fd_g_compare", [], [], 1, pins=None)


class StepCR(TG.StepC):
    """fd_gencmp.py overlap --arm refined on StepC's synthetic 2D/3D fixture, rescaled to E_R's recorded integral.
    StepC's own tests run in test_fd_gencmp.py; they are not collected again here (set to None below)."""

    def setUp(self):
        super().setUp()
        prior = self.d / "overlap_c_out.txt"             # step C's readout on the purity fixture, the C-R3D reference
        gc.main(self.args(prior))
        self.prior = prior
        self.p3 = [mock.patch.object(gc, "OVERLAP_C", prior), mock.patch.object(gc, "OVERLAP_C_SHA256", sha(prior))]
        for p in self.p3:
            p.start()
        self.cv_r = self.cv * (gc.ER_2D_INTEGRAL / gc.VL173_2D_INTEGRAL)
        e_pt, e_pz = np.asarray(gc.sa.s1.FINE["pt"], float), np.asarray(gc.sa.s1.FINE["pz"], float)
        TG.write_root(self.d / "cv2.root", {"hXSec2D": (self.cv_r, e_pt, e_pz)})
        self.write_q(arm=True)

    def tearDown(self):
        for p in self.p3:
            p.stop()
        super().tearDown()

    def test_cr3d_refuses_a_3d_row_other_than_step_cs(self):
        r = json.loads(self.prior.read_text())
        r["quadrants"]["QB"]["3D"]["S"] *= 1 + 1e-9
        self.prior.write_text(json.dumps(r))
        with mock.patch.object(gc, "OVERLAP_C_SHA256", sha(self.prior)):
            with self.assertRaises(fg.Stop) as e:
                gc.main([*self.args(self.d / "x_out.txt"), "--arm", "refined"])
        self.assertIn("C-R3D", str(e.exception))

    def test_cr3d_refuses_an_unpinned_step_c_readout(self):
        with mock.patch.object(gc, "OVERLAP_C_SHA256", "0" * 64):
            with self.assertRaises(fg.Stop) as e:
                gc.main([*self.args(self.d / "x_out.txt"), "--arm", "refined"])
        self.assertIn("C-R3D", str(e.exception))

    def write_q(self, arm: bool):
        cells = np.flatnonzero(self.cv_r.ravel() > 0)
        x = self.cv_r.ravel()[cells]
        np.savez(self.d / "q.npz", total_plus_C_PL=np.diag((0.06 * x) ** 2), area=self.w2.ravel()[cells], cells_x_EU=x,
                 **({"arm": np.array("refined")} if arm else {}))

    def test_refined_arm_runs_and_labels_its_result(self):
        out = self.d / "cr_out.txt"
        gc.main([*self.args(out), "--arm", "refined"])
        r = json.loads(out.read_text())
        self.assertEqual((r["arm_2d"], r["result_2d"], r["step"]), ("refined", "E_R with Q_R", "C-R (Q26)"))
        self.assertEqual(set(r["quadrants"]), {"QA", "QB", "QC", "QD"})

    def test_refined_arm_refuses_a_q_without_its_arm_key(self):
        self.write_q(arm=False)
        with self.assertRaises(fg.Stop):
            gc.main([*self.args(self.d / "x_out.txt"), "--arm", "refined"])

    def test_c3_refined_refuses_the_purity_integral(self):
        e_pt, e_pz = np.asarray(gc.sa.s1.FINE["pt"], float), np.asarray(gc.sa.s1.FINE["pz"], float)
        TG.write_root(self.d / "cv2.root", {"hXSec2D": (self.cv, e_pt, e_pz)})
        with self.assertRaises(fg.Stop) as e:
            gc.main([*self.args(self.d / "x_out.txt"), "--arm", "refined"])
        self.assertIn("C3", str(e.exception))

    def test_c3_purity_refuses_the_refined_integral(self):
        with self.assertRaises(fg.Stop) as e:
            gc.main(self.args(self.d / "x_out.txt"))
        self.assertIn("C3", str(e.exception))

    def test_two_inputs_files_that_disagree_refuse(self):
        pins = self.fx.pins()
        other = dict(pins)
        k = next(iter(other))
        other[k] = "0" * 64
        with mock.patch.object(gc, "load_pins", lambda path=None: other if str(path).endswith("b") else pins):
            with self.assertRaises(fg.Stop) as e:
                gc.main([*self.args(self.d / "x_out.txt"), "--arm", "refined", "--inputs", "a", "--inputs", "b"])
        self.assertIn("pinned twice", str(e.exception))


for _name in [n for n in vars(TG.StepC) if n.startswith("test_")]:
    setattr(StepCR, _name, None)


if __name__ == "__main__":
    unittest.main()
