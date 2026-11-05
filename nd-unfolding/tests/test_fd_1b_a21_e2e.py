"""A2.1's jobs end to end on a toy world written consistently to disk (the director's mock audit): the calibration
and c2check through fd_1b_c2.prepare, with the production loaders unmocked (fd_1b_mc._load_world with its digest and
pin checks, verified_weights, _single, truth_ratio on the toy F1 prep, truth_weight with s5e_deform's install,
fs.load_s1 on a staged assembly, fs.reported_matrix on the committed data product).

Stand-ins, each named: World.patches() re-pins the toy files' digests (constants, as every 1B job test does); the S1
assembly's digest is re-pinned the same way; and the H2 fine map and functional matrix are replaced by a toy map,
because the committed definition is built on the real 65,856-cell grid and cannot map the toy's 48 cells."""
import argparse
import json
import os
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
import fd_1b_inv as inv  # noqa: E402
import fd_1b_mc as mc  # noqa: E402
import fd_1b_score as fs  # noqa: E402
import fd_1b_toys as toys  # noqa: E402
import s1_assemble as sa  # noqa: E402
import s5p_universe  # noqa: E402
from test_fd_1b import EDGES, SHAPE, World, digest  # noqa: E402
import fd_1b_noatime_guard as guard  # noqa: E402

# A test-scoped guard: the production decision (guard.refuses) over a mutable root list, so a test can run 1B's real
# entry paths under it and then switch it off (a production hook is permanent for its process). The stand-in bit is
# os.O_NOFOLLOW, which fd_1b_inv.open_noatime is given here in place of O_NOATIME (macOS has none).
_GUARD_ROOTS: list = []
_REFUSED: list = []
_HOOKED: list = []


def _guard_hook(event, args):
    if event == "open" and _GUARD_ROOTS:
        flags = args[2] if len(args) > 2 and args[2] is not None else 0
        if guard.refuses(args[0], flags, tuple(_GUARD_ROOTS), os.O_NOFOLLOW):
            _REFUSED.append(os.fsdecode(args[0]))
            raise PermissionError(f"(test guard) a plain open of a declared input refused: {os.fsdecode(args[0])}")
from test_fd_1b_mc import pinned, plain_noatime  # noqa: E402

N_TD = 50


def matched_world(root: Path) -> dict:
    """consistent_world with the denominator rows the truth-passing in-grid signal rows themselves (coordinates as
    float32, as the bank stores them, and the npz's MCgen made float32-exact so row_hash keys agree; tdw_CV their
    w_truth), so C2's row match (vi) is bounded, and a push file for the plug-in: a world on which c2check can PASS,
    for the H3 round trip."""
    x = consistent_world(root)
    w = x["w"]
    z = dict(np.load(w.inputs, allow_pickle=True))
    gen = np.asarray(z["MCgen"], np.float64).astype(np.float32).astype(np.float64)
    z["MCgen"] = gen
    cells = mc.flat_cells(gen, EDGES)
    sel = np.asarray(z["pass_truth"], bool) & (cells >= 0)
    cv = dict(np.load(w.bank / "cv.npz", allow_pickle=True))
    bank_gen = gen.copy()
    bank_gen[~np.isfinite(np.asarray(cv["MCgen"], float)).all(axis=1)] = np.nan
    cv["MCgen"] = bank_gen
    for k, j in zip(("td_pt", "td_pz", "td_ea", "td_q3", "td_w"), range(5)):
        cv[k] = gen[sel, j].astype(np.float32)
    np.savez(w.bank / "cv.npz", **cv)
    tdw_cv = np.asarray(z["w_truth"], float)[sel]
    np.save(x["tdw"], tdw_cv)
    z["denom_nd"] = s5p_universe.denominator(cv, tdw_cv, EDGES)
    np.savez(w.inputs, **z)
    b = dict(np.load(w.bkg, allow_pickle=True))
    b["meta"] = json.dumps({"npz_sha256": digest(w.inputs)})
    np.savez(w.bkg, **b)
    for p in sorted(w.bank.glob("*_tdw.npy")):
        r = np.random.default_rng(zlib.crc32(p.name.encode()))
        np.save(p, tdw_cv * r.uniform(0.98, 1.02, tdw_cv.size))
    for p in sorted(w.det.glob("*_denom_nd.npy")):
        np.save(p, z["denom_nd"])
    w.receipt.write_text(json.dumps({"files_sha256": {p.name: digest(p) for p in sorted(w.det.iterdir())}}))
    w.manifest.write_text("".join(f"{digest(p)}  {p}\n" for p in sorted(w.bank.iterdir()))
                          + f"{digest(w.receipt)}  {w.receipt}\n")
    w.pins.write_text(json.dumps(toys.make_pins(w.bank, w.det, w.manifest, w.receipt)))
    push = root / "push.npz"
    np.savez(push, push=np.random.default_rng(9).uniform(0.9, 1.1, int(np.asarray(z["pass_truth"], bool).sum())))
    return dict(x, push=push)


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
    truths = ("g18", "ar23")

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="fd1b-a21-e2e-"))
        cls.x = cls.world(cls.tmp)
        cls.cal = cls.tmp / "cal" / "cal.json"
        with cls.patched():
            cls.cal_rec = c2.calibrate_main(cls.args(sets=40, workers=2, budget_seconds=1e6, out=cls.cal,
                                                     draws=300))      # speed: the rule and power are N-free

    @classmethod
    def world(cls, root):
        return consistent_world(root)

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
                    prep=w.prep, push=cls.x.get("push"),
                    expect_push_sha256=digest(cls.x["push"]) if cls.x.get("push") else None, cv_tdw=cls.x["tdw"],
                    expect_cv_tdw_sha256=digest(cls.x["tdw"]), truths=list(cls.truths))
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
        self.assertIn(rec["verdict"], ("CALIBRATED", "CONTROL_FAILED", "LINEARISATION_TO_DIRECTOR", "I_ALONE_TO_DIRECTOR", "NO_THRESHOLD_TO_DIRECTOR", "POWER_SHORT_TO_DIRECTOR"))
        self.assertEqual(len(rec["rule"]["grid"]), len(c2.S_GRID))

    def calibrated(self):
        """The calibration's own record with its verdict set to CALIBRATED and its power met (a named fixture step: 40
        sets of the toy cannot reach the declared 10,000, and their power is not the real one), its ratio file
        unchanged."""
        rec = dict(self.cal_rec, verdict="CALIBRATED", power=dict(self.cal_rec.get("power") or {}, meets=True))
        p = self.tmp / "cal" / "cal-calibrated.json"
        p.write_text(json.dumps(rec))
        shutil.copy(self.cal.with_suffix(".npz"), p.with_suffix(".npz"))
        return p

    def cal300(self):
        """The backstop's 300-draw calibration (schema /1): a named fixture holding the toy calibration's own per-cell
        SDs, which it measured at 300 draws per set (draws=300), and job 60771025's fd_1b_c2 digest, so c2check's
        check of the code behind those SDs (cal300_code_check) runs on this tree's own files."""
        from test_fd_1b_c2 import CAL300_REF_SHA256
        p = self.tmp / "cal" / "cal300.json"
        p.write_text(json.dumps({"schema": "fd-1b-c2-calibration/1", "code_sha256": {"fd_1b_c2.py": CAL300_REF_SHA256},
                                 "outputs": {t: {"a": {"sd_per_cell": self.cal_rec["rule"]["thresholds"][t]["sd_per_cell"]}}
                                             for t in self.truths}}))
        return p

    def c2args(self, cal, **kw):
        c3 = self.cal300()
        return self.args(calibration=cal, expect_calibration_sha256=digest(cal),
                         expect_calibration_npz_sha256=digest(cal.with_suffix(".npz")), staged=self.x["staged"],
                         calibration_300=c3, expect_calibration_300_sha256=digest(c3),
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
        self.assertEqual(g["gate_sample"]["n"], c2.GATE_N)
        self.assertTrue(g["gate_sample"]["first_300_bitwise"])
        self.assertEqual(set(g["backstop"]), {"g18", "ar23"})
        self.assertEqual(len(g["config_hash"]), 64)
        self.assertEqual(g["calibration"]["verdict"], "CALIBRATED")
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

    def test_c2check_refuses_a_calibration_from_other_code(self):
        """The director's ruling (A), 2026-11-05: c2check refuses a calibration whose code_sha256 is not its own
        gate_code_digests (fd_1b_c2 and fd_1b_mc each changed, or none recorded), and on its own code's record goes on
        to the next check (here a wrong 300-draw digest, which it reaches only past this one)."""
        cal = self.calibrated()
        rec = json.loads(cal.read_text())
        self.assertEqual(rec["code_sha256"], c2.gate_code_digests())             # the fixture's own run, this code
        for i, code in enumerate((dict(rec["code_sha256"], **{"fd_1b_c2.py": "0" * 64}),
                                  dict(rec["code_sha256"], **{"fd_1b_mc.py": "0" * 64}), None)):
            other = self.tmp / "cal" / f"cal-other-{i}.json"
            other.write_text(json.dumps(dict(rec, code_sha256=code)))
            shutil.copy(cal.with_suffix(".npz"), other.with_suffix(".npz"))
            with self.patched(), self.assertRaisesRegex(c2.Refusal, "computed by other code"):
                c2.c2check_main(self.c2args(other))
        a = self.c2args(cal)
        a.expect_calibration_300_sha256 = "0" * 64
        with self.patched(), self.assertRaisesRegex(c2.Refusal, "300-draw calibration's digest differs"):
            c2.c2check_main(a)
        a = self.c2args(cal)                                          # and a 300-draw record at other code
        c3 = json.loads(a.calibration_300.read_text())
        c3["code_sha256"] = {"fd_1b_c2.py": "0" * 64}
        a.calibration_300.write_text(json.dumps(c3))
        a.expect_calibration_300_sha256 = digest(a.calibration_300)
        with self.patched(), self.assertRaisesRegex(c2.Refusal, "not the record its pins describe"):
            c2.c2check_main(a)

    def test_one_set_is_02e71a0bs_at_300_draws(self):
        """The director's named exemption (2026-11-05): the current _one_set, which passes n=st["n"] to
        calibration_draws, is 02e71a0b's _one_set (tests/data/fd_1b_c2_at_02e71a0b.py.txt, job 60771025's code) when
        st["n"] = 300. Both, on this world's prepared state, give bitwise-equal ratios for two sets of each truth; at 299
        they differ, so the test sees the argument."""
        from test_fd_1b_c2 import CAL300_REF_SHA256, reference_module
        old = reference_module("02e71a0b", CAL300_REF_SHA256)
        with self.patched():
            P = c2.prepare(self.args())
            state = {k: P[k] for k in ("H", "cv", "U", "ref_x", "ref_count", "flux_cols", "phi", "const", "flux_p",
                                       "col", "bands")}
            state["groups"] = P["world"]["groups"]
            jobs = [(t, s) for t in self.truths for s in (0, 7)]
            saved = dict(c2._STATE)
            try:
                old._worker_init(dict(state))
                want = [old._one_set(j) for j in jobs]
                for n, same in ((300, True), (299, False)):
                    c2._STATE.clear()
                    c2._worker_init(dict(state, n=n))
                    got = [c2._one_set(j) for j in jobs]
                    eq = [g[:2] == w[:2] and np.array_equal(g[2], w[2]) and np.array_equal(g[3], w[3])
                          for g, w in zip(got, want)]
                    self.assertEqual(eq, [same] * len(jobs), n)
            finally:
                c2._STATE.clear()
                c2._STATE.update(saved)

    def test_c2check_refuses_a_sample_whose_first_300_are_not_the_declared(self):
        cal = self.calibrated()
        real = c2.gate_seeds
        with self.patched(), mock.patch.object(c2, "gate_seeds", lambda t: real(t)[1:] + [real(t)[-1] + 1]), \
                self.assertRaisesRegex(c2.Refusal, "first 300 differ"):
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

    def gate_file(self, name: str, pins: Path) -> Path:
        """A gate record bound to this world's inputs with the given pins, as c2check writes one for G18."""
        gate = self.tmp / name
        with self.patched():
            ins = {"npz_sha256": sa.INPUT_NPZ_SHA256, "bkg_sha256": sa.BKG_SHA256, "pins_sha256": digest(pins),
                   "flux_table_sha256": digest(self.x["table"]), "cv_tdw_sha256": digest(self.x["tdw"]),
                   "push_sha256": None}
            code = c2.gate_code_digests()
            gate.write_text(json.dumps({
                "schema": c2.SCHEMA_GATE, **mc.CLIP_GATE, "reads": {"g18": "option (1)"}, "truths": ["g18"],
                "declared_seeds": {"g18": [mc.TOY_SEEDS["g18"][0], mc.TOY_SEEDS["g18"][-1]]},
                "code_sha256": code, "calibration_sha256": "c" * 64, "inputs": ins,
                "calibration": {"verdict": "CALIBRATED", "sha256": "c" * 64, "s": 1.0, "union": 0.009,
                                "three_truths_measured": True, "power_meets": True, "code_sha256": code},
                "backstop": {"g18": {"passes": True}}, "config_hash": c2.config_hash(code, ins, "nature"),
                "gate_sample": {"n": c2.GATE_N, "first_300_bitwise": True}}))
        return gate

    def toy_argv(self, bank: Path, pins: Path) -> list[str]:
        w = self.x["w"]
        return ["unfold", "--truth", "g18", "--role", "toy", "--items", str(mc.TOY_SEEDS["g18"][0]),
                "--npz", str(w.inputs), "--bkg", str(w.bkg), "--bank", str(bank), "--detector-dir", str(w.det),
                "--pins", str(pins), "--flux-constraint", str(w.constraint), "--expect-pins-sha256", digest(pins),
                "--prep", str(w.prep), "--threads", "1", "--estimator", "R",
                "--flux-table", str(self.x["table"]), "--expect-flux-table-sha256", digest(self.x["table"]),
                "--cv-tdw", str(self.x["tdw"]), "--expect-cv-tdw-sha256", digest(self.x["tdw"])]

    def test_a_negative_composite_denominator_row_end_to_end(self):
        """The director's request before binding 3: a composite denominator row driven negative (two drawn bank
        universes' tdw lowered on one row, every universe's tdw still >= 0, the CV's untouched) is clipped by the
        'nature' rule end to end through run_unfold: the record, the product's per-cell array the readout's (a)
        aggregates, and the toy truth, each against the row's own contribution computed from the files."""
        w = self.x["w"]
        fake = lambda exp, threads, seed=42, unfold_fn=None: (np.zeros(SHAPE), {})  # noqa: E731

        def toy(rule, bank, pins, out, gate=None):
            argv = self.toy_argv(bank, pins) + ["--clip-rule", rule, "--out", str(out)]
            if gate is not None:
                argv += ["--clip-gate", str(gate), "--expect-clip-gate-sha256", digest(gate)]
            with self.patched(), mock.patch.object(mc, "_unfold", fake), \
                    pinned(self.tmp, digest(gate) if gate else None):
                self.assertEqual(mc.main(argv), 0, rule)
            z = np.load(out / mc.product_name("fd1b_mc", "g18", "toy", str(mc.TOY_SEEDS["g18"][0])), allow_pickle=True)
            return json.loads(str(z["meta"])), {k: np.asarray(z[k], float) for k in z.files if k != "meta"}
        # the truth clip does not read the denominator, so the cells it touches are found first, on the world's own
        # bank, and the lowered row's cell is chosen outside them: measured, so no one world's layout is assumed
        _, base = toy("nature", w.bank, w.pins, self.tmp / "toy-neg-base", self.gate_file("gate-base.json", w.pins))
        touched = set(np.flatnonzero(base["clip_truth_nature_flat"] > 0).tolist())
        bank = self.tmp / "bank-neg"
        shutil.copytree(w.bank, bank)
        cvz = dict(np.load(bank / "cv.npz", allow_pickle=True))
        cells = mc.td_cells(cvz, EDGES)
        occ = np.bincount(cells[cells >= 0], minlength=int(np.prod(SHAPE)))
        free = [c for c in np.argsort(-occ, kind="stable").tolist() if occ[c] >= 3 and c not in touched]
        self.assertTrue(free, (touched, occ.tolist()))                         # a cell the truth clip leaves alone
        cell = free[0]                                                          # with other rows to keep it > 0
        row = int(np.flatnonzero(cells == cell)[0])
        with self.patched():
            d = toys.draw_for_seed(int(mc.TOY_SEEDS["g18"][0]), toys.flux_probabilities(w.constraint),
                                   toys.interaction_groups(bank))
        tags = mc.draw_universes(d)
        lowered = [t for t in tags if (bank / f"{t}_tdw.npy").exists() and not t.startswith("Flux")][:2]
        for t in lowered:
            v = np.load(bank / f"{t}_tdw.npy")
            v[row] = 0.2
            np.save(bank / f"{t}_tdw.npy", v)
        manifest, pins = self.tmp / "manifest-neg.txt", self.tmp / "pins-neg.json"
        manifest.write_text("".join(f"{digest(p)}  {p}\n" for p in sorted(bank.iterdir())) + f"{digest(w.receipt)}  {w.receipt}\n")
        pins.write_text(json.dumps(toys.make_pins(bank, w.det, manifest, w.receipt)))
        tdw_cv = np.load(self.x["tdw"])

        def own(t):                            # a detector universe (its denom_nd in the detector dir) brings the CV's
            return tdw_cv if (w.det / f"{t}_denom_nd.npy").exists() else np.load(bank / f"{t}_tdw.npy")
        rows = sum(own(t) for t in tags) - (len(tags) - 1) * tdw_cv              # every composite denominator row
        comp = rows[row]
        self.assertLess(comp, 0)                                               # the fixture reaches the regime
        self.assertTrue(np.all(np.delete(rows, row) > 0))                       # and only this row is negative
        self.assertTrue(all(np.all(own(t) >= 0) for t in tags))                # while no universe's tdw is
        d_cell = rows[cells == cell].sum()                                     # the composite cell, positive (2b)
        self.assertGreater(d_cell, 0)
        md, ad = toy("data", bank, pins, self.tmp / "toy-neg-data")
        mn, an = toy("nature", bank, pins, self.tmp / "toy-neg-nature", self.gate_file("gate-neg.json", pins))
        rec = mn["clip"]["denominator"]
        self.assertEqual(rec["rows_negative"], 1)
        self.assertAlmostEqual(rec["sum_negative"], comp, places=12)            # the record: the row's own value
        want = np.zeros(int(np.prod(SHAPE)))
        want[cell] = -comp
        np.testing.assert_allclose(an["clip_denom_flat"], want, rtol=1e-12, atol=1e-15)   # its cell only
        np.testing.assert_allclose(self.x["U"] @ an["clip_denom_flat"], -comp * self.x["U"][:, cell], rtol=1e-12,
                                   atol=1e-15)                                 # what the readout's (a) aggregates
        self.assertNotIn("clip_denom_flat", ad)
        self.assertNotIn("denominator", md["clip"])
        np.testing.assert_array_equal(an["clip_truth_nature_flat"], base["clip_truth_nature_flat"])   # unmoved by tdw
        differ = set(np.flatnonzero(an["xtrue_flat"] != ad["xtrue_flat"]).tolist())
        self.assertIn(cell, differ)
        self.assertLessEqual(differ, touched | {cell})                         # nothing else moves the truth
        self.assertAlmostEqual(an["xtrue_flat"][cell] / ad["xtrue_flat"][cell], (d_cell - comp) / d_cell, places=10)

    def test_a_toy_item_under_nature_end_to_end(self):
        """run_unfold, through mc.main, for a declared G18 toy under each rule: --cv-tdw loaded and checked,
        the composite on one binning (e2), clip_draw's nature (truth and denominator rows), the toy truth, and
        check_clip_gate. One named stand-in: the estimator (_unfold, the bound negweight-refined OmniFold, which A2.1 does
        not change, whose output no A2.1 check reads, and which needs ROOT)."""
        w = self.x["w"]
        gate = self.tmp / "gate-file.json"                    # bound to this run's inputs, as c2check writes it
        with self.patched():
            ins = {"npz_sha256": sa.INPUT_NPZ_SHA256, "bkg_sha256": sa.BKG_SHA256, "pins_sha256": digest(w.pins),
                   "flux_table_sha256": digest(self.x["table"]), "cv_tdw_sha256": digest(self.x["tdw"]),
                   "push_sha256": None}
            code = c2.gate_code_digests()
            gate.write_text(json.dumps({
                "schema": c2.SCHEMA_GATE, **mc.CLIP_GATE, "reads": {"g18": "option (1)"}, "truths": ["g18"],
                "declared_seeds": {"g18": [mc.TOY_SEEDS["g18"][0], mc.TOY_SEEDS["g18"][-1]]},
                "code_sha256": code, "calibration_sha256": "c" * 64, "inputs": ins,
                "calibration": {"verdict": "CALIBRATED", "sha256": "c" * 64, "s": 1.0, "union": 0.009,
                                "three_truths_measured": True, "power_meets": True, "code_sha256": code},
                "backstop": {"g18": {"passes": True}}, "config_hash": c2.config_hash(code, ins, "nature"),
                "gate_sample": {"n": c2.GATE_N, "first_300_bitwise": True}}))
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
            with self.patched(), mock.patch.object(mc, "_unfold", fake), \
                    pinned(self.tmp, digest(gate)):
                self.assertEqual(mc.main(argv), 0, rule)
            z = np.load(out / mc.product_name("fd1b_mc", "g18", "toy", str(mc.TOY_SEEDS["g18"][0])), allow_pickle=True)
            metas[rule] = (json.loads(str(z["meta"])), np.asarray(z["xtrue_flat"], float),
                           {k: np.asarray(z[k], float) for k in mc.NATURE_CLIP_ARRAYS if k in z.files})
        mn, xn, an = metas["nature"]
        md, xd, ad = metas["data"]
        self.assertEqual((sorted(an), ad), (sorted(mc.NATURE_CLIP_ARRAYS), {}))   # the readout's (a), nature only
        self.assertTrue(all(np.all(v >= 0) for v in an.values()))
        np.testing.assert_allclose(an["clip_denom_flat"].sum(), -mn["clip"]["denominator"]["sum_negative"], rtol=1e-12)
        self.assertLessEqual(an["clip_truth_nature_flat"].sum(), -mn["clip"]["truth"]["sum_negative"] * (1 + 1e-12))
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

    def test_the_cv_tdw_is_checked_at_load(self):
        """_load_world, unmocked: the CV per-row tdw must be finite and >= 0 (the writer's 0 <= w gate) and one per
        denominator row; each failure refuses, and the good file loads."""
        with self.patched():
            self.assertEqual(mc._load_world(self.args())["tdw_cv"].shape, (N_TD,))
        for bad in (np.r_[np.ones(N_TD - 1), -1e-9], np.r_[np.ones(N_TD - 1), np.nan], np.ones(N_TD - 1)):
            p = self.tmp / "bad-tdw.npy"
            np.save(p, bad)
            with self.patched(), self.assertRaises(mc.Refusal):
                mc._load_world(self.args(cv_tdw=p, expect_cv_tdw_sha256=digest(p)))



class RoundTrip(E2E):
    """The director's H3: c2check's own written record, on a world where it can PASS (matched_world, all three
    truths), goes to check_clip_gate by its digest: it is admitted; each re-verified field (H2) perturbed, and
    declared by its own digest, is refused. Only this class's test runs here (the parent's run on their own world)."""
    truths = ("g18", "ar23", "plugin")

    @classmethod
    def world(cls, root):
        return matched_world(root)

    def gate_argv(self, gate):
        w = self.x["w"]
        return ["unfold", "--truth", "g18", "--role", "toy", "--items", str(mc.TOY_SEEDS["g18"][0]),
                "--npz", str(w.inputs), "--bkg", str(w.bkg), "--bank", str(w.bank), "--detector-dir", str(w.det),
                "--pins", str(w.pins), "--flux-constraint", str(w.constraint), "--expect-pins-sha256", digest(w.pins),
                "--prep", str(w.prep), "--threads", "1", "--estimator", "R", "--clip-rule", "nature",
                "--flux-table", str(self.x["table"]), "--expect-flux-table-sha256", digest(self.x["table"]),
                "--cv-tdw", str(self.x["tdw"]), "--expect-cv-tdw-sha256", digest(self.x["tdw"]),
                "--clip-gate", str(gate), "--expect-clip-gate-sha256", digest(gate),
                "--out", str(self.tmp / f"rt-{gate.stem}")]

    def bulk(self, gate):
        fake = lambda exp, threads, seed=42, unfold_fn=None: (np.zeros(SHAPE), {})  # noqa: E731
        with self.patched(), mock.patch.object(mc, "_unfold", fake), \
                pinned(self.tmp, digest(gate)):
            return mc.main(self.gate_argv(gate))

    def test_the_1b_entries_read_every_declared_input_through_o_noatime(self):
        """The director's ruling of 2026-11-05, exercised rather than walked: the calibration, c2check, the probe and a
        bulk unfold, run on this world under the guard's own decision over the world's input roots (the npz,
        background, bank, detector dump, pins, flux constraint, flux table, prep, S1 staged and CV tdw), open none of
        them plainly. A plain read would refuse here as it would under fd_1b_noatime_guard on the cluster."""
        w = self.x["w"]
        roots = [w.inputs, w.bkg, w.bank, w.det, w.pins, w.constraint, w.prep, self.x["table"], self.x["staged"],
                 self.x["tdw"]]
        if not _HOOKED:
            sys.addaudithook(_guard_hook)
            _HOOKED.append(True)
        cal = self.calibrated()
        a = self.c2args(cal)
        a.out = self.tmp / "gate" / "gate-guarded.json"
        out = self.tmp / "probe" / "probe-guarded.json"
        argv = ["c2probe", "--npz", str(w.inputs), "--bkg", str(w.bkg), "--bank", str(w.bank), "--detector-dir", str(w.det),
                "--pins", str(w.pins), "--expect-pins-sha256", digest(w.pins), "--flux-constraint", str(w.constraint),
                "--flux-table", str(self.x["table"]), "--expect-flux-table-sha256", digest(self.x["table"]),
                "--definition", str(self.tmp / "definition.json"), "--staged", str(self.x["staged"]),
                "--cv-tdw", str(self.x["tdw"]), "--expect-cv-tdw-sha256", digest(self.x["tdw"]), "--prep", str(w.prep),
                "--truths", "g18", "--blocks", "2", "--out", str(out)]
        cal_args = self.args(sets=4, workers=2, budget_seconds=1e6, out=self.tmp / "cal" / "cal-guarded.json", draws=300)
        _REFUSED.clear()                                      # every argument digest above is the test's, made unguarded
        with self.patched(), mock.patch.object(inv, "NOATIME_FLAG", os.O_NOFOLLOW):
            _GUARD_ROOTS[:] = [os.path.realpath(r) for r in roots]
            try:
                c2.calibrate_main(cal_args)
                g = c2.c2check_main(a)
                self.assertEqual(c2.main(argv), 0)
            finally:
                _GUARD_ROOTS.clear()
        self.assertEqual(_REFUSED, [])
        self.assertEqual(g["verdict"], "PASS")
        _REFUSED.clear()
        fake = lambda exp, threads, seed=42, unfold_fn=None: (np.zeros(SHAPE), {})  # noqa: E731   (as bulk())
        bulk_argv = self.gate_argv(a.out)                     # its digests are the test's reads, made before the guard
        with self.patched(), mock.patch.object(inv, "NOATIME_FLAG", os.O_NOFOLLOW), mock.patch.object(mc, "_unfold", fake), \
                pinned(self.tmp, digest(a.out)):
            _GUARD_ROOTS[:] = [os.path.realpath(r) for r in roots]
            try:
                self.assertEqual(mc.main(bulk_argv), 0)                     # a bulk unfold on c2check's record
            finally:
                _GUARD_ROOTS.clear()
        self.assertEqual(_REFUSED, [])
        with self.patched(), mock.patch.object(inv, "NOATIME_FLAG", 0):      # the guard sees a plain read: it fires
            _GUARD_ROOTS[:] = [os.path.realpath(r) for r in roots]
            try:
                with self.assertRaises(PermissionError):
                    inv.open_noatime(w.pins).read()
            finally:
                _GUARD_ROOTS.clear()
        self.assertEqual(_REFUSED, [os.fsdecode(w.pins)])

    def test_c2checks_record_round_trip(self):
        cal = self.calibrated()
        with self.patched():
            g = c2.c2check_main(self.c2args(cal))
        self.assertEqual(g["verdict"], "PASS", g["reads"])
        self.assertTrue(g["calibration"]["three_truths_measured"])
        gate = self.tmp / "gate" / "gate.json"
        self.assertEqual(self.bulk(gate), 0)                                   # c2check's own record: admitted
        for k, v in (("calibration", dict(g["calibration"], verdict="TO_JOSEPH")),
                     ("calibration", dict(g["calibration"], sha256="d" * 64)),
                     ("calibration", dict(g["calibration"], three_truths_measured=False)),
                     ("calibration", dict(g["calibration"], union=0.0101)),
                     ("calibration", dict(g["calibration"], power_meets=False)),
                     ("backstop", dict(g["backstop"], g18=dict(g["backstop"]["g18"], passes=False))),
                     ("config_hash", "0" * 64), ("verdict", "STOP"), ("reading", "option (3)")):
            bad = self.tmp / "gate" / f"bad-{k}-{len(list((self.tmp / 'gate').glob('bad-*')))}.json"
            bad.write_text(json.dumps(dict(g, **{k: v})))
            self.assertEqual(self.bulk(bad), 4, (k, v))

    def test_a_failed_backstop_stops_c2check(self):
        """P6: with every reading option (1), as this world gives, a backstop failure alone makes the verdict STOP
        (the final receipt's survivor "c2check: PASS without the backstop"). The 300-draw calibration's per-cell SDs
        are made a thousandth of the fixture's, so (iii) by (alpha) at 4.3 SD_c fails on the declared draws."""
        cal = self.calibrated()
        with self.patched():
            ok = c2.c2check_main(self.c2args(cal))
        self.assertEqual((ok["verdict"], all(b["passes"] for b in ok["backstop"].values())), ("PASS", True))
        tiny = self.tmp / "cal" / "cal300-tiny.json"
        from test_fd_1b_c2 import CAL300_REF_SHA256
        tiny.write_text(json.dumps({"schema": "fd-1b-c2-calibration/1", "code_sha256": {"fd_1b_c2.py": CAL300_REF_SHA256},
                                    "outputs": {
            t: {"a": {"sd_per_cell": (np.asarray(self.cal_rec["rule"]["thresholds"][t]["sd_per_cell"]) * 1e-3).tolist()}}
            for t in self.truths}}))
        a = self.c2args(cal)
        a.calibration_300, a.expect_calibration_300_sha256 = tiny, digest(tiny)
        a.out = self.tmp / "gate" / "gate-backstop.json"
        with self.patched():
            g = c2.c2check_main(a)
        self.assertTrue(all(v == "option (1)" for v in g["reads"].values()))
        self.assertFalse(any(b["passes"] for b in g["backstop"].values()))
        self.assertEqual(g["verdict"], "STOP")

    def test_each_truth_is_read_at_its_own_calibrated_thresholds(self):
        """c2check reads the clipped ratio with gate_n at each truth's OWN calibrated thresholds (the final receipt's
        survivors "the clipped ratio read at #724's fixed gate" and "another truth's thresholds"). With AR23's (ii)
        threshold alone set to 0, AR23 alone must stop reading option (1): neither #724's fixed 0.07 nor G18's
        thresholds would stop it."""
        cal = self.calibrated()
        rec = json.loads(cal.read_text())
        rec["rule"]["thresholds"]["ar23"] = dict(rec["rule"]["thresholds"]["ar23"], ii_mean_log=0.0)
        tight = self.tmp / "cal" / "cal-ar23-tight.json"
        tight.write_text(json.dumps(rec))
        shutil.copy(cal.with_suffix(".npz"), tight.with_suffix(".npz"))
        a = self.c2args(tight)
        a.out = self.tmp / "gate" / "gate-ar23-tight.json"
        with self.patched():
            g = c2.c2check_main(a)
        self.assertFalse(g["reading_detail"]["ar23"]["gate_n"]["ii"])
        self.assertTrue(c2.c2_gate(g["record"]["b"]["ar23"]["variance_ratio"][c2.CLIPPED]))   # #724's gate passes it
        self.assertTrue(c2.gate_n(g["record"]["b"]["ar23"]["variance_ratio"][c2.CLIPPED],
                                  rec["rule"]["thresholds"]["g18"])["passes"])               # and G18's thresholds
        self.assertNotEqual(g["reads"]["ar23"], "option (1)")
        self.assertEqual((g["reads"]["g18"], g["reads"]["plugin"]), ("option (1)", "option (1)"))
        self.assertEqual(g["verdict"], "STOP")

    def test_c2_truth_is_bitwise_f19adbdas_end_to_end(self):
        """The director's ruling (a): c2check with the hoisted c2_truth writes the same gate record as with f19adbda's
        c2_truth (every field but seconds and atime), building the multiplicative terms once for the job (two arrays, not
        two per c2_truth call); and on c2check's own c2_truth arguments, with non-positive universe and CV weights
        injected so every floor branch is reached, the two agree bitwise in every quantity, the terms given or not."""
        from test_fd_1b_c2 import reference_c2
        ref = reference_c2()
        cal = self.calibrated()
        calls = []

        def spy(*args, **kw):
            calls.append(args)
            kw.pop("terms")                                             # f19adbda builds its own
            return ref.c2_truth(*args, **kw)
        a_new = self.c2args(cal)
        a_new.out = self.tmp / "gate" / "gate-new.json"
        a_ref = self.c2args(cal)
        a_ref.out = self.tmp / "gate" / "gate-ref.json"
        with self.patched():
            with mock.patch.object(c2, "multiplicative_terms", wraps=c2.multiplicative_terms) as mt:
                g_new = c2.c2check_main(a_new)
            self.assertEqual(mt.call_count, 2)                          # wt and tdw, once for the job
            with mock.patch.object(c2, "c2_truth", spy):
                g_ref = c2.c2check_main(a_ref)
        drop = lambda g: {k: v for k, v in json.loads(json.dumps(g)).items() if k not in ("seconds", "atime")}  # noqa: E731
        self.assertEqual(drop(g_new), drop(g_ref))
        self.assertEqual(len(calls), 2 * len(self.truths))           # the 300 and the N per truth
        V, cv, S, r, geo, phi, const = calls[1]                     # the first truth's gate sample
        rng = np.random.default_rng(41)
        V2 = {k: np.array(v, copy=True) for k, v in V.items()}
        cv2 = {k: np.array(v, copy=True) for k, v in cv.items()}
        for q in ("wt", "tdw"):
            u, w = V2[q].shape
            V2[q][rng.random((u, w)) < 0.02] = 0.0
            V2[q][rng.random((u, w)) < 0.02] *= -0.5
            cv2[q][rng.random(w) < 0.03] = 0.0
            cv2[q][rng.random(w) < 0.03] *= -0.5
            T = c2.multiplicative_terms(V2[q], cv2[q])
            self.assertGreater(T["zu"].size, 0, q)
            self.assertGreater(int((~T["pos"]).sum()), 0, q)
            self.assertTrue(np.any(S[:, T["zu"]] > 0), q)            # some drawn universe floors a row
        foreign = (c2.c2_terms({q: np.array(v, copy=True) for q, v in V.items()}, cv),   # another V, equal values
                   c2.c2_terms(V, {q: np.array(v, copy=True) for q, v in cv.items()}),   # another cv
                   {q: c2.multiplicative_terms(V[q], cv[q]) for q in ("wt", "tdw")},      # no source recorded
                   {"wt": c2.c2_terms(V, cv)["wt"]})                                    # one array's only
        for bad in foreign:
            with self.assertRaisesRegex(c2.Refusal, "not built from this V and cv"):
                c2.c2_truth(V, cv, S, r, geo, phi, const, terms=bad)
        for args in ((V, cv, S, r, geo, phi, const), (V2, cv2, S, r, geo, phi, const)):
            want = ref.c2_truth(*args)
            for got in (c2.c2_truth(*args), c2.c2_truth(*args, terms=c2.c2_terms(args[0], args[1]))):
                self.assertEqual(sorted(got), sorted(want))
                for k in want:
                    self.assertTrue(np.array_equal(got[k], want[k], equal_nan=True), k)

    def test_the_merge_of_per_truth_records_is_the_all_truth_record(self):
        """The director's ruling (a), one truth per job: c2check run once per truth and merged (c2check-merge, through
        the CLI with each part's digest) equals c2check run over all three truths on every field but seconds, atime and
        merged_from; the merged record is admitted by the bulk's gate as the single run's is."""
        cal = self.calibrated()
        a_all = self.c2args(cal)
        a_all.out = self.tmp / "gate" / "gate-all.json"
        with self.patched():
            g_all = c2.c2check_main(a_all)
        parts = []
        for t in self.truths:
            a = self.c2args(cal)
            a.truths, a.out = [t], self.tmp / "gate" / f"gate-part-{t}.json"
            with self.patched():
                c2.c2check_main(a)
            parts.append(a.out)
        merged = self.tmp / "gate" / "gate-merged.json"
        argv = ["c2check-merge", "--out", str(merged)]
        for p in reversed(parts):                                   # any part order
            argv += ["--part", str(p), "--expect-part-sha256", digest(p)]
        self.assertEqual(c2.main(argv), 0)
        g_m = json.loads(merged.read_text())
        drop = lambda g: {k: v for k, v in json.loads(json.dumps(g)).items()  # noqa: E731
                          if k not in ("seconds", "atime", "merged_from")}
        self.assertEqual(drop(g_m), drop(g_all))
        self.assertEqual(g_all["threads"], {k: os.environ.get(k) for k in c2.THREAD_VARS})   # recorded as set
        self.assertEqual(g_m["verdict"], "PASS")
        self.assertEqual([m["truths"] for m in g_m["merged_from"]], [[t] for t in reversed(self.truths)])
        self.assertEqual(self.bulk(merged), 0)                       # the merged record admits, as the single does
        with self.assertRaisesRegex(c2.Refusal, "digest is not the one given"):
            c2.main(["c2check-merge", "--out", str(self.tmp / "gate" / "x.json"), "--part", str(parts[0]),
                     "--expect-part-sha256", "0" * 64, "--part", str(parts[1]), "--expect-part-sha256", digest(parts[1])])
        recs = [json.loads(p.read_text()) for p in parts]
        with self.assertRaisesRegex(c2.Refusal, "in two per-truth records"):
            c2.c2check_merge([recs[0], recs[0]])
        with self.assertRaisesRegex(c2.Refusal, "at least two"):
            c2.c2check_merge([recs[0]])
        for k, v in (("config_hash", "0" * 64), ("threads", {"OMP_NUM_THREADS": "7"}), ("calibration_sha256", "d" * 64),
                     ("code_sha256", {"x.py": "0"})):
            with self.assertRaisesRegex(c2.Refusal, f"differ in {k}"):
                c2.c2check_merge([recs[0], dict(recs[1], **{k: v}), recs[2]])
        with self.assertRaisesRegex(c2.Refusal, r"differ in C2's \(vi\)"):
            c2.c2check_merge([recs[0], dict(recs[1], record=dict(recs[1]["record"], vi={})), recs[2]])
        two = json.loads(cal.read_text())                           # a calibration without the plug-in
        two["truths"] = [t for t in two["truths"] if t != "plugin"]
        cal2 = self.tmp / "cal" / "cal-two.json"
        cal2.write_text(json.dumps(two))
        shutil.copy(cal.with_suffix(".npz"), cal2.with_suffix(".npz"))
        a = self.c2args(cal2)
        a.truths, a.out = ["plugin"], self.tmp / "gate" / "gate-plugin-uncal.json"
        with self.patched(), self.assertRaisesRegex(c2.Refusal, "not among the calibration's"):
            c2.c2check_main(a)
        stop = dict(recs[1], reads={self.truths[1]: "option (2)"})
        self.assertEqual(c2.c2check_merge([recs[0], stop, recs[2]])["verdict"], "STOP")   # one truth's reading stops it
        bad = dict(recs[2], backstop={self.truths[2]: dict(recs[2]["backstop"][self.truths[2]], passes=False)})
        self.assertEqual(c2.c2check_merge([recs[0], recs[1], bad])["verdict"], "STOP")    # and one backstop

    def test_the_timing_probe(self):
        """c2probe (the director's ruling (a), item 3, and ruling (A)) through the CLI: c2check's one-off steps each timed
        through c2check's own functions (prepare, c2_inputs, c2_terms once, c2_vi, c2_draws for the 300 and the GATE_N
        gate sample), then --blocks blocks of the gate sample through c2_truth; its projection is the one-off steps +
        (300 + GATE_N)/DRAW_BLOCK blocks at the mean block time (the first block, which pays one-off costs, set aside);
        |Z| per array as c2_terms builds it; it refuses two truths and an existing output."""
        w = self.x["w"]
        out = self.tmp / "probe" / "probe.json"
        argv = ["c2probe", "--npz", str(w.inputs), "--bkg", str(w.bkg), "--bank", str(w.bank), "--detector-dir", str(w.det),
                "--pins", str(w.pins), "--expect-pins-sha256", digest(w.pins), "--flux-constraint", str(w.constraint),
                "--flux-table", str(self.x["table"]), "--expect-flux-table-sha256", digest(self.x["table"]),
                "--definition", str(self.tmp / "definition.json"), "--staged", str(self.x["staged"]),
                "--cv-tdw", str(self.x["tdw"]), "--expect-cv-tdw-sha256", digest(self.x["tdw"]), "--prep", str(w.prep),
                "--truths", "g18", "--blocks", "3", "--out", str(out)]
        built, drawn, vi = [], [], []
        real_terms, real_draws, real_vi = c2.c2_terms, c2.c2_draws, c2.c2_vi

        def spy_terms(V, cv):
            built.append(real_terms(V, cv))
            return built[-1]

        def spy_draws(P, seed_list):
            drawn.append(list(seed_list))
            return real_draws(P, seed_list)

        def spy_vi(*args):
            vi.append(real_vi(*args))
            return vi[-1]
        with self.patched():
            with mock.patch.object(c2, "multiplicative_terms", wraps=c2.multiplicative_terms) as mt, \
                    mock.patch.object(c2, "c2_terms", spy_terms), mock.patch.object(c2, "c2_draws", spy_draws), \
                    mock.patch.object(c2, "c2_vi", spy_vi):
                self.assertEqual(c2.main(argv), 0)
            self.assertEqual(mt.call_count, 2)                          # wt and tdw, once, not per block
            self.assertEqual(len(built), 1)
            self.assertEqual(drawn, [list(mc.TOY_SEEDS["g18"]), list(c2.gate_seeds("g18")[:c2.GATE_N])])  # as c2check
            self.assertEqual(len(vi), 1)
            self.assertIsNotNone(vi[0]["largest_cell_unmatched_share"])
            rec = json.loads(out.read_text())
            self.assertEqual(rec["schema"], "fd-1b-c2-probe/2")
            self.assertEqual(set(rec["once_seconds"]), {"prepare", "inputs", "terms", "vi", "draws_300", "draws_gate"})
            self.assertTrue(all(v >= 0 for v in rec["once_seconds"].values()))
            self.assertEqual(rec["z_pairs"], {q: int(built[0][q]["zu"].size) for q in ("wt", "tdw")})
            self.assertGreater(rec["peak_rss_kib"], 0)
            self.assertEqual((rec["truth"], rec["blocks"], len(rec["block_seconds"])), ("g18", 3, 3))
            self.assertEqual(rec["blocks_per_truth"], (len(mc.TOY_SEEDS["g18"]) + c2.GATE_N) // c2.DRAW_BLOCK)
            self.assertAlmostEqual(rec["block_seconds_used"], float(np.mean(rec["block_seconds"][1:])), places=12)
            self.assertAlmostEqual(rec["projected_seconds_per_truth"], sum(rec["once_seconds"].values())
                                   + rec["blocks_per_truth"] * rec["block_seconds_used"], places=6)
            self.assertEqual(rec["code_sha256"], c2.gate_code_digests())
            self.assertEqual(set(rec["rows"]), {"wt", "wr", "bkgw", "tdw", "D"})
            with self.assertRaisesRegex(c2.Refusal, "refusing to overwrite"):   # it will not overwrite
                c2.main(argv)
            with self.assertRaises(SystemExit):                             # one truth only
                c2.main(argv[:-5] + ["--truths", "g18", "ar23", "--blocks", "3", "--out", str(out) + "2"])
            with self.assertRaisesRegex(c2.Refusal, "times one truth"):     # and the function's own guard
                c2.c2probe_main(argparse.Namespace(truths=["g18", "ar23"], blocks=3))

    # the parent's tests run on their own world; here only the round trip
    test_the_calibration_runs_the_production_chain = test_c2check_end_to_end = None
    test_c2check_refuses_an_uncalibrated_or_foreign_calibration = None
    test_c2check_refuses_a_calibration_from_other_code = None
    test_one_set_is_02e71a0bs_at_300_draws = None
    test_c2check_refuses_a_sample_whose_first_300_are_not_the_declared = None
    test_the_binning_script_end_to_end = test_the_receipt_end_to_end = None
    test_a_toy_item_under_nature_end_to_end = test_the_cv_tdw_is_checked_at_load = None
    test_a_negative_composite_denominator_row_end_to_end = None


if __name__ == "__main__":
    unittest.main()
