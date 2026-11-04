"""A2.1's jobs end to end on a toy world written consistently to disk (the director's mock audit): the calibration
and c2check through fd_1b_c2.prepare, with the production loaders unmocked (fd_1b_mc._load_world with its digest and
pin checks, verified_weights, _single, truth_ratio on the toy F1 prep, truth_weight with s5e_deform's install,
fs.load_s1 on a staged assembly, fs.reported_matrix on the committed data product).

Stand-ins, each named: World.patches() re-pins the toy files' digests (constants, as every 1B job test does); the S1
assembly's digest is re-pinned the same way; and the H2 fine map and functional matrix are replaced by a toy map,
because the committed definition is built on the real 65,856-cell grid and cannot map the toy's 48 cells."""
import argparse
import json
import shutil
import sys
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest import mock

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fd_1b_c2 as c2  # noqa: E402
import fd_1b_mc as mc  # noqa: E402
import fd_1b_score as fs  # noqa: E402
import fd_1b_toys as toys  # noqa: E402
import s1_assemble as sa  # noqa: E402
import s5p_universe  # noqa: E402
from test_fd_1b import EDGES, SHAPE, World, digest  # noqa: E402
from test_fd_1b_mc import plain_noatime  # noqa: E402

N_TD = 50


def consistent_world(root: Path) -> dict:
    """World, then made to agree with the real files' measured facts on disk: cv.npz carries the denominator rows'
    coordinates; the npz's denom_nd is those rows' histogram at the CV weight (1 per row, written as the (d1) read's
    weights file); each bank universe's tdw is the CV's within 2 % (crc32-seeded, not hash()); each detector
    universe's denom_nd is the CV's bitwise (check D); a staged flux table and an S1 assembly; pins regenerated."""
    w = World(root)
    rng = np.random.default_rng(5)
    cv = dict(np.load(w.bank / "cv.npz", allow_pickle=True))
    for k, e in zip(("td_pt", "td_pz", "td_ea", "td_q3", "td_w"), EDGES):
        cv[k] = rng.uniform(e[0], e[-1], N_TD).astype(np.float32)
    np.savez(w.bank / "cv.npz", **cv)
    tdw_cv = np.ones(N_TD)
    np.save(root / "cvdenom.npy", tdw_cv)
    denom = s5p_universe.denominator(cv, tdw_cv, EDGES)
    z = dict(np.load(w.inputs, allow_pickle=True))
    z["denom_nd"] = denom
    np.savez(w.inputs, **z)
    b = dict(np.load(w.bkg, allow_pickle=True))
    b["meta"] = json.dumps({"npz_sha256": digest(w.inputs)})
    np.savez(w.bkg, **b)
    for p in sorted(w.bank.glob("*_tdw.npy")):
        r = np.random.default_rng(zlib.crc32(p.name.encode()))
        np.save(p, r.uniform(0.98, 1.02, N_TD))
    for p in sorted(w.det.glob("*_denom_nd.npy")):
        np.save(p, denom)
    w.receipt.write_text(json.dumps({"files_sha256": {p.name: digest(p) for p in sorted(w.det.iterdir())}}))
    w.manifest.write_text("".join(f"{digest(p)}  {p}\n" for p in sorted(w.bank.iterdir()))
                          + f"{digest(w.receipt)}  {w.receipt}\n")
    w.pins.write_text(json.dumps(toys.make_pins(w.bank, w.det, w.manifest, w.receipt)))
    flux_cv = np.asarray(z["flux"], float)
    table = root / "flux_table.npz"
    np.savez(table, hFluxCV=flux_cv, hFluxUniv=flux_cv[None, :] * rng.uniform(0.95, 1.05, (100, flux_cv.size)))
    n = int(np.prod(SHAPE))
    fm = np.arange(n) % sa.N_CELLS
    U = np.vstack([np.where(fm == c, 1.0 + 0.25 * c, 0.0) for c in range(sa.N_CELLS)])
    f_dp = np.asarray(json.loads(fs.DATA_PRODUCT.read_text())["f"], float)
    blocks = sorted(["stat", "normalization", "seed"] + [f"band:{b}" for b in sa.EXPECT] +
                    [f"lat:{b}" for b in sa.LATERAL_BANDS])
    staged = root / "staged" / "s1"
    staged.mkdir(parents=True)
    np.savez(staged / "s1_assembly.npz", f=f_dp, U=U.astype(np.float32), C_e=np.eye(sa.N_CELLS),
             meta=json.dumps({"blocks": blocks}),
             **{"C_" + k.replace(":", "_"): np.eye(sa.N_CELLS) * 1e-3 for k in blocks})
    return {"w": w, "table": table, "fm": fm, "U": U, "staged": root / "staged", "tdw": root / "cvdenom.npy",
            "s1": staged / "s1_assembly.npz"}


class E2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="fd1b-a21-e2e-"))
        cls.x = consistent_world(cls.tmp)
        cls.cal = cls.tmp / "cal" / "cal.json"
        with cls.patched():
            cls.cal_rec = c2.calibrate_main(cls.args(sets=40, workers=2, budget_seconds=1e6, out=cls.cal))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    @classmethod
    def patched(cls):
        """The named stand-ins only (the module docstring)."""
        from contextlib import ExitStack
        stack = ExitStack()
        for p in cls.x["w"].patches() + [plain_noatime(), mock.patch.object(fs, "S1_NPZ_SHA256", digest(cls.x["s1"])),
                                         mock.patch.object(sa, "fine_map", lambda d: cls.x["fm"]),
                                         mock.patch.object(sa, "functional_matrix", lambda fm: cls.x["U"])]:
            stack.enter_context(p)
        return stack

    @classmethod
    def args(cls, **kw):
        w = cls.x["w"]
        base = dict(npz=w.inputs, bkg=w.bkg, bank=w.bank, detector_dir=w.det, pins=w.pins,
                    expect_pins_sha256=digest(w.pins), flux_constraint=w.constraint, flux_table=cls.x["table"],
                    expect_flux_table_sha256=digest(cls.x["table"]), definition=cls.tmp / "definition.json",
                    prep=w.prep, push=None, expect_push_sha256=None, cv_tdw=cls.x["tdw"],
                    expect_cv_tdw_sha256=digest(cls.x["tdw"]), truths=["g18", "ar23"])
        base.update(kw)
        return argparse.Namespace(**base)

    def test_the_calibration_runs_the_production_chain(self):
        rec = self.cal_rec
        self.assertEqual(rec["schema"], c2.SCHEMA_CAL)
        self.assertEqual(rec["checks"]["detector_denominator_differs_from_cv"], [])
        self.assertEqual(rec["checks"]["r_negative"]["g18"]["rows"], 0)
        self.assertEqual(rec["atime"]["moved"], [])
        self.assertEqual(rec["inputs"]["cv_tdw_sha256"], digest(self.x["tdw"]))
        z = np.load(self.cal.with_suffix(".npz"))
        self.assertEqual(z["ratio_g18"].shape, (40, sa.N_CELLS))
        self.assertFalse(np.array_equal(z["single_x_g18"], z["single_x_ar23"]))     # the toy F1 ratios, unmocked
        self.assertTrue(rec["control_law"]["holds"])
        self.assertIn(rec["verdict"], ("CALIBRATED", "TO_JOSEPH", "LINEARISATION_TO_DIRECTOR"))

    def calibrated(self):
        """The calibration's own record with its verdict set to CALIBRATED (a named fixture step: 40 sets cannot
        reach the declared 10,000), its ratio file unchanged."""
        rec = dict(self.cal_rec, verdict="CALIBRATED")
        p = self.tmp / "cal" / "cal-calibrated.json"
        p.write_text(json.dumps(rec))
        shutil.copy(self.cal.with_suffix(".npz"), p.with_suffix(".npz"))
        return p

    def c2args(self, cal, **kw):
        return self.args(calibration=cal, expect_calibration_sha256=digest(cal),
                         expect_calibration_npz_sha256=digest(cal.with_suffix(".npz")), staged=self.x["staged"],
                         out=self.tmp / "gate" / "gate.json", **kw)

    def test_c2check_end_to_end(self):
        cal = self.calibrated()
        with self.patched():
            g = c2.c2check_main(self.c2args(cal))
        self.assertEqual(g["schema"], c2.SCHEMA_GATE)
        self.assertEqual(g["step"], "c2-clip-gate")
        self.assertIn(g["verdict"], ("PASS", "STOP"))
        self.assertEqual(set(g["reads"]), {"g18", "ar23"})
        self.assertEqual(g["declared_seeds"]["g18"], [mc.TOY_SEEDS["g18"][0], mc.TOY_SEEDS["g18"][-1]])
        self.assertEqual(g["calibration_sha256"], digest(cal))
        self.assertEqual(g["inputs"]["cv_tdw_sha256"], digest(self.x["tdw"]))
        for t in ("g18", "ar23"):
            b = g["record"]["b"][t]
            self.assertEqual(len(b["variance_ratio"][c2.CLIPPED]), sa.N_CELLS)
            self.assertIn("passes", b["gate_724"])
        self.assertIsNotNone(g["record"]["vi"]["largest_cell_unmatched_share"])
        self.assertEqual(g["atime"]["moved"], [])
        self.assertEqual(g["verdict"] == "PASS", all(v == "option (1)" for v in g["reads"].values()))

    def test_c2check_refuses_an_uncalibrated_or_foreign_calibration(self):
        with self.patched(), self.assertRaisesRegex(c2.Refusal, "not CALIBRATED"):
            c2.c2check_main(self.c2args(self.cal))
        cal = self.calibrated()
        z = dict(np.load(cal.with_suffix(".npz")))
        z["single_x_g18"] = z["single_x_g18"] * 1.001
        np.savez(cal.with_suffix(".npz"), **z)
        with self.patched(), self.assertRaisesRegex(c2.Refusal, "not the calibration's"):
            c2.c2check_main(self.c2args(cal))

    def test_the_binning_script_end_to_end(self):
        """fd_1b_binning.main with truth_ratio, truth_weight, load_inputs, the seek reads and the declared draws
        unmocked (the binning rerun's ValueError("ratio_nd") came through a mocked truth_weight)."""
        import fd_1b_binning as fb
        cells = mc.td_cells(np.load(self.x["w"].bank / "cv.npz"), EDGES)
        k = int(np.flatnonzero(cells >= 0)[0])
        u = np.array(np.unravel_index(cells[k], SHAPE))
        u[1] = 1 - u[1]
        rec = {"verdict": "PASS", "checks": {"B_tolerance": {"passes": True, "rows": [
            [k, int(cells[k]), int(np.ravel_multi_index(tuple(u), SHAPE)), 1.0]]}}}
        cvd = self.tmp / "cvdenom.json"
        cvd.write_text(json.dumps(rec))
        out = self.tmp / "binning.json"
        w = self.x["w"]
        argv = ["--npz", str(w.inputs), "--bank", str(w.bank), "--detector-dir", str(w.det), "--pins", str(w.pins),
                "--flux-constraint", str(w.constraint), "--definition", "d", "--staged", str(self.x["staged"]),
                "--prep", str(w.prep), "--cvdenom", str(cvd), "--out", str(out),
                "--expect-pins-sha256", digest(w.pins), "--expect-cvdenom-sha256", digest(cvd)]
        with self.patched():
            self.assertEqual(fb.main(argv), 0)
        b = json.loads(out.read_text())
        self.assertEqual(b["moved_rows"], 1)
        self.assertEqual(b["item4"]["g18"]["draws"], len(mc.TOY_SEEDS["g18"]))
        self.assertNotEqual(b["nominal_basis_f32_minus_f64_sigma"]["g18"], b["nominal_basis_f32_minus_f64_sigma"]["ar23"])
        self.assertEqual(b["atime"]["moved"], [])

    def test_the_receipt_end_to_end(self):
        """fd_1b_mc.receipt unmocked except the named stand-ins: its U check against the staged S1 (float32, as
        s1_assemble writes it; the amendment-2 receipt test gave a float64 U and could not see the defect), (e2)'s
        d_CV, the 900 declared draws, N1 and section 2b on the real loaders."""
        with self.patched():
            rec = mc.receipt(self.args(staged=self.x["staged"]))
        self.assertEqual(rec["step"], "receipt")
        self.assertIn(rec["verdict"], ("PASS", "STOP"))
        self.assertEqual(sum(v["sample_rows"] > 0 for v in rec["validation"].values()), 3)
        self.assertEqual(rec["atime"]["moved"], [])
        with self.patched(), self.assertRaisesRegex(mc.InvalidReceipt, "--cv-tdw"):
            mc.receipt(self.args(staged=self.x["staged"], cv_tdw=None))
        U32 = np.load(self.x["s1"])["U"]
        self.assertEqual(U32.dtype, np.float32)

    def test_a_toy_item_under_nature_end_to_end(self):
        """run_unfold, through mc.main, for a declared G18 toy under each rule: --cv-tdw loaded and checked,
        the composite on one binning (e2), clip_draw's nature (truth and denominator rows), the toy truth, and
        check_clip_gate. One named stand-in: the estimator (_unfold, the bound negweight-refined OmniFold, which A2.1 does
        not change, whose output no A2.1 check reads, and which needs ROOT)."""
        w = self.x["w"]
        gate = self.tmp / "gate-file.json"                    # bound to this run's inputs, as c2check writes it
        with self.patched():
            gate.write_text(json.dumps({
                "schema": c2.SCHEMA_GATE, **mc.CLIP_GATE, "reads": {"g18": "option (1)"},
                "declared_seeds": {"g18": [mc.TOY_SEEDS["g18"][0], mc.TOY_SEEDS["g18"][-1]]},
                "code_sha256": c2.gate_code_digests(), "calibration_sha256": "c" * 64,
                "inputs": {"npz_sha256": sa.INPUT_NPZ_SHA256, "bkg_sha256": sa.BKG_SHA256, "pins_sha256": digest(w.pins),
                           "flux_table_sha256": digest(self.x["table"]), "cv_tdw_sha256": digest(self.x["tdw"])}}))
        common = ["unfold", "--truth", "g18", "--role", "toy", "--items", str(mc.TOY_SEEDS["g18"][0]),
                  "--npz", str(w.inputs), "--bkg", str(w.bkg), "--bank", str(w.bank), "--detector-dir", str(w.det),
                  "--pins", str(w.pins), "--flux-constraint", str(w.constraint), "--expect-pins-sha256", digest(w.pins),
                  "--prep", str(w.prep), "--threads", "1", "--estimator", "R",
                  "--flux-table", str(self.x["table"]), "--expect-flux-table-sha256", digest(self.x["table"]),
                  "--cv-tdw", str(self.x["tdw"]), "--expect-cv-tdw-sha256", digest(self.x["tdw"])]
        fake = lambda exp, threads, seed=42, unfold_fn=None: (np.zeros(SHAPE), {})  # noqa: E731
        metas = {}
        for rule in ("data", "nature"):
            out = self.tmp / f"toy-{rule}"
            argv = common + ["--clip-rule", rule, "--out", str(out)]
            if rule == "nature":
                argv += ["--clip-gate", str(gate), "--expect-clip-gate-sha256", digest(gate)]
            with self.patched(), mock.patch.object(mc, "_unfold", fake):
                self.assertEqual(mc.main(argv), 0, rule)
            z = np.load(out / mc.product_name("fd1b_mc", "g18", "toy", str(mc.TOY_SEEDS["g18"][0])), allow_pickle=True)
            metas[rule] = (json.loads(str(z["meta"])), np.asarray(z["xtrue_flat"], float))
        mn, xn = metas["nature"]
        md, xd = metas["data"]
        self.assertEqual((md["clip_rule"], mn["clip_rule"]), ("data", "nature"))
        self.assertIn("denominator", mn["clip"])
        self.assertIn("truth", mn["clip"])
        self.assertNotIn("denominator", md["clip"])
        self.assertEqual((md["clip"]["rule"], mn["clip"]["rule"]), ("data", "nature"))
        self.assertTrue(np.all(np.isfinite(xn)) and np.all(np.isfinite(xd)))
        with self.patched(), mock.patch.object(mc, "_unfold", fake):            # nature without --cv-tdw refuses
            argv = [x for x in common if x not in (str(self.x["tdw"]), digest(self.x["tdw"]), "--cv-tdw",
                                                    "--expect-cv-tdw-sha256")]
            self.assertNotEqual(mc.main(argv + ["--clip-rule", "nature", "--out", str(self.tmp / "toy-x"),
                                                "--clip-gate", str(gate), "--expect-clip-gate-sha256", digest(gate)]), 0)


if __name__ == "__main__":
    unittest.main()
