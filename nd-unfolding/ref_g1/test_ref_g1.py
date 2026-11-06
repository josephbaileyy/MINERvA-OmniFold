#!/usr/bin/env python3
"""Controls for ``ref_g1.py`` and ``ref_g1_read.py`` (REF-G1-DECLARATION.md §3.3, §4, §7): each mechanism fires on
its defect and stays silent on the clean case.

The driver tests use the real 5D grid, IBU-1's real J partition, the real H2 definition and fine map, and IBU-1's
synthetic events (``ibu1/test_ibu1.py``), through the real parsers: ``s5c_unfold.load_inputs`` on an of_inputs-format
npz, ``s5p_universe.weights`` on bank-format files, ``pvl_ratios.write_ratio`` for the ratios. The reader tests use
hand-made products whose cell integrals are set exactly, so every reading can be checked by hand. Nothing here reads
an analysis input."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "ibu1"))
import ref_g1 as G  # noqa: E402
import ref_g1_read as R  # noqa: E402
from test_ibu1 import synthetic_bkg, synthetic_inputs  # noqa: E402  (IBU-1's own fixture, not retyped)

# O_NOATIME, substituted explicitly (A1 §2.2: the code refuses a plain read where the platform has no O_NOATIME, as
# macOS has none). O_NONBLOCK is inert on a regular file's open, so a guarded open reads as a plain one here; the
# substitution is the same on every platform.
NOATIME_SUB = mock.patch.object(os, "O_NOATIME", os.O_NONBLOCK, create=True)
NOATIME_SUB.start()

CFG = json.loads(G.CONFIG.read_text())
LIB = G.Lib(CFG)
CONTRACT = json.loads((G.REPO / LIB.ibu1_cfg["contract"]["path"]).read_text())
INPUTS, BKG = synthetic_inputs(), synthetic_bkg()
RUN = G.Run(LIB, CFG, INPUTS, BKG, CONTRACT, chunk=7_000)
U = RUN.gw.U
KS = CFG["iterations"]["reported"]
import pvl_ratios  # noqa: E402  (pv-ladder is on sys.path after ref_g1's import)
import s5c_unfold  # noqa: E402


def unit_ratio(d: Path, name: str, r: np.ndarray | None = None) -> str:
    n = int(np.prod([len(LIB.pvl.FINE[a]) - 1 for a in LIB.pvl.AXES5]))
    _, sha = pvl_ratios.write_ratio(d, name, f"{name} (test)", LIB.pvl.AXES5, np.ones(n) if r is None else r,
                                    {"k": 1.0, "stat_max": 0.05})
    return sha


def cfg_with(**over) -> dict:
    c = copy.deepcopy(CFG)
    for path, v in over.items():
        node = c
        keys = path.split("__")
        for k in keys[:-1]:
            node = node[k]
        node[keys[-1]] = v
    return c


# ============================================================================== driver


class World(unittest.TestCase):
    def test_the_g1_world_is_ibu1s_with_the_h2_cells_and_s1s_rows(self):
        cmap, n = LIB.s1.coarse_map(LIB.s1.H2_EDGES)
        np.testing.assert_array_equal(RUN.gw.coarse_of, cmap)
        self.assertEqual(RUN.gw.n_coarse, n)
        np.testing.assert_array_equal(U, LIB.s1a.functional_matrix(LIB.s1a.fine_map(G.REPO / CFG["definition"]["path"])))
        self.assertEqual(RUN.gw.names, [f"R{c:02d}" for c in range(16)])
        # the rows are the J world's: only the coarse map and the functional rows differ
        self.assertIs(RUN.gw.tflat, RUN.jw.tflat)
        self.assertIs(RUN.gw.pairs, RUN.jw.pairs)
        self.assertEqual(len(RUN.jw.names), 153)

    def test_the_noise_free_closure_is_a_fixed_point_at_every_k(self):
        exp, x_true = LIB.pvl.closure_inputs(INPUTS, np.ones(RUN.n))
        F, _ = G.unfold_experiment(RUN.gw, G.full_half(RUN.n, INPUTS["w_truth"], INPUTS["w_reco"]), exp, KS)
        X = RUN.gw.functionals(x_true)
        nz = X != 0
        self.assertGreater(int(nz.sum()), 8)
        for row in F["F_fold"]:
            np.testing.assert_allclose(row[nz], X[nz], rtol=1e-12, atol=0)
            self.assertTrue(np.all(row[~nz] == 0))

    def test_gibu1_is_ibu1s_data_unit_bitwise(self):
        """G-IBU1's mechanism: this driver on IBU-1's J world returns what ibu1.run_data writes."""
        tmp = Path(tempfile.mkdtemp())
        try:
            G.ibu1.run_data(RUN.jw, LIB.ibu1_cfg, BKG, {"name": "D_N", "arm": "N"}, tmp)
            ref, _ = R.load(tmp / "D_N.npz")
            got, _ = RUN.gibu1()
            for k in ("ks", "F_fold", "F_sub"):
                np.testing.assert_array_equal(got[k], ref[k])
        finally:
            shutil.rmtree(tmp)


class Replicas(unittest.TestCase):
    def test_the_replica_is_es_construction_and_g_draw_is_silent(self):
        off = CFG["replicas"]["jitter_offset"]
        rep = G.replica_experiment(LIB, INPUTS, BKG, RUN.base_cells, 7, off)
        ji, jb = LIB.num.jittered(INPUTS, BKG, off + 7)
        ref = LIB.s5n.bootstrap_replica(LIB.s5n.build_data(ji, jb), 7)
        for k in ("obs_counts", "w_truth", "w_reco", "tmpl_w"):  # G-draw's list (REF-G1 §3.3)
            np.testing.assert_array_equal(rep[k], ref[k])
        half = lambda e: G.full_half(RUN.n, e["w_truth"], e["w_reco"])  # noqa: E731
        got, _ = G.unfold_experiment(RUN.gw, half(rep), rep, KS)
        want, _ = G.unfold_experiment(RUN.gw, half(ref), ref, KS)
        for k in ("F_fold", "F_sub"):  # what IBU returns is (e)'s construction's
            np.testing.assert_array_equal(got[k], want[k])
        self.assertTrue(G.g_draw(LIB, INPUTS, BKG, 7, off, rep)["pass"])
        _, meta = RUN.replica(7)
        self.assertEqual((meta["bootstrap_seed"], meta["jitter_seed"]), (7, off + 7))
        self.assertTrue(meta["g_draw"]["pass"])

    def test_g_draw_fires_on_a_replica_that_is_not_es(self):
        off = CFG["replicas"]["jitter_offset"]
        rep = G.replica_experiment(LIB, INPUTS, BKG, RUN.base_cells, 7, off)
        for key in ("obs_counts", "w_truth", "tmpl_w"):
            bad = dict(rep)
            bad[key] = np.array(rep[key], float)
            bad[key][3] += 1.0
            with self.subTest(key=key):
                self.assertFalse(G.g_draw(LIB, INPUTS, BKG, 7, off, bad)["pass"])
        other = G.replica_experiment(LIB, INPUTS, BKG, RUN.base_cells, 8, off)  # a neighbouring seed
        self.assertFalse(G.g_draw(LIB, INPUTS, BKG, 7, off, other)["pass"])

    def test_a_jitter_that_moves_membership_is_refused_before_any_replica(self):
        """The refusal (e)'s loop applies (s5p_numerics.py:188-191). Edge-safe jitter cannot move a row across an
        edge (it leaves float32(edge) in place, and every other float32 value is at least 1/2 ulp away), so the
        crossing is injected by substituting the jitter, the only way to reach the guard."""
        real = LIB.num.jittered
        edge = INPUTS["edges"][0][3]
        calls = []

        def crossing(inputs, bkg, seed):
            calls.append(seed)  # the director's condition: the test proves the substitution ran
            ji, jb = real(inputs, bkg, seed)
            ji = dict(ji)
            ji["MCreco"] = np.array(ji["MCreco"], copy=True)
            row = int(np.flatnonzero(RUN.base_cells["MCreco"] >= 0)[0])
            ji["MCreco"][row, 0] = np.nextafter(edge, -np.inf) if ji["MCreco"][row, 0] >= edge else edge
            return ji, jb

        with mock.patch.object(LIB.num, "jittered", crossing):
            ji, jb = LIB.num.jittered(INPUTS, BKG, 101)
            moved = {k: int((v != RUN.base_cells[k]).sum()) for k, v in LIB.num.cell_membership(ji, jb["bkg_reco"]).items()}
            self.assertTrue(any(moved.values()))  # (e)'s loop would refuse here, rc 5
            self.assertEqual(len(calls), 1)
            with self.assertRaises(G.MembershipMoved):
                G.replica_experiment(LIB, INPUTS, BKG, RUN.base_cells, 1, 100)
            self.assertEqual(len(calls), 2)  # the substitution reached the builder
            tmp = Path(tempfile.mkdtemp())
            try:
                self.assertEqual(G.run_unit(RUN, ("replica", 1), tmp), G.RC_MOVED)
                self.assertEqual(list(tmp.iterdir()), [])
                self.assertEqual(len(calls), 3)
            finally:
                shutil.rmtree(tmp)


class Units(unittest.TestCase):
    def test_gibu1_runs_only_in_ibu1s_environment(self):
        """The interpreter and Python version, and (A1 §1) IBU-1's thread environment and CPU count."""
        env = G.environment()
        here = {**CFG["gibu1_environment"], "interpreter": env["interpreter"], "python_version": env["python_version"],
                "thread_env": env["thread_env"], "cpus": env["cpus"]}
        cases = (({}, 0), ({"python_version": env["python_version"] + " (another build)"}, G.RC_GATE),
                 ({"thread_env": {**env["thread_env"], "OMP_NUM_THREADS": "32"}}, G.RC_GATE),
                 ({"thread_env": {**env["thread_env"], "MKL_NUM_THREADS": "32"}}, G.RC_GATE),
                 ({"cpus": env["cpus"] + 1}, G.RC_GATE))
        for over, rc in cases:
            tmp = Path(tempfile.mkdtemp())
            try:
                run = copy.copy(RUN)
                run.cfg = cfg_with(gibu1_environment={**here, **over})
                with self.subTest(over=over, rc=rc):
                    self.assertEqual(G.run_unit(run, ("gibu1",), tmp), rc)
                    self.assertEqual((tmp / "gibu1.npz").exists(), rc == 0)
                    if rc == 0:
                        _, meta = R.load(tmp / "gibu1.npz")
                        self.assertEqual(meta["environment"], env)
            finally:
                shutil.rmtree(tmp)
        self.assertEqual(CFG["gibu1_environment"]["python_version"][:7], "3.11.14")
        self.assertEqual(CFG["gibu1_environment"]["thread_env"],  # sbatch_ibu1.sh:25 @ 7ea30e3d
                         {"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"})
        self.assertEqual(CFG["gibu1_environment"]["cpus"], 2)  # sacct 60130813.0, cpu=2

    def test_a_unit_that_failed_g_draw_is_never_done(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            failed = {"checks": {"keep_observed": False}, "pass": False}
            with mock.patch.object(G, "g_draw", lambda *a, **k: failed):
                self.assertEqual(G.run_unit(RUN, ("replica", 4), tmp), G.RC_DRAW)
            self.assertEqual(json.loads((tmp / "replica_b4.done").read_text())["verdict"], "FAIL")
            before = G.sha256(tmp / "replica_b4.npz")
            self.assertEqual(G.run_unit(RUN, ("replica", 4), tmp), G.RC_DRAW)  # refused, not skipped with rc 0
            self.assertEqual(G.sha256(tmp / "replica_b4.npz"), before)
            self.assertEqual(G.run_unit(RUN, ("replica", 5), tmp), 0)
            self.assertEqual(json.loads((tmp / "replica_b5.done").read_text())["verdict"], "PASS")
            self.assertEqual(G.run_unit(RUN, ("replica", 5), tmp), 0)  # a PASS unit is skipped
        finally:
            shutil.rmtree(tmp)

    def test_the_cv_universe_is_the_central_bitwise(self):
        a, _ = RUN.central()
        b, meta = RUN.universe("CV", "-")
        for k in ("ks", "F_fold", "F_sub"):
            np.testing.assert_array_equal(a[k], b[k])
        self.assertEqual(meta["weight_sha256"], {})

    def test_a_detector_universe_through_the_bank_parsers(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            bank, det = tmp / "bank", tmp / "det"
            bank.mkdir()
            det.mkdir()
            gen = np.asarray(INPUTS["MCgen"], float).copy()
            gen[np.any(gen < -9000, axis=1)] = np.nan
            np.savez(bank / "cv.npz", MCgen=gen, MCreco=INPUTS["MCreco"], pass_reco=INPUTS["pass_reco"],
                     pass_truth=INPUTS["pass_truth"], measured=INPUTS["measured"], bkg_cols=BKG["bkg_reco"])
            rng = np.random.default_rng(4)
            w = {"wt": INPUTS["w_truth"] * rng.uniform(0.9, 1.1, RUN.n), "denom_nd": INPUTS["denom_nd"] * 1.02,
                 "bkgw": BKG["bkg_w"] * 1.05}
            w["wr"] = w["wt"] * INPUTS["w_reco"] / INPUTS["w_truth"]
            for k, v in w.items():
                np.save(det / f"GEANT_Pion_0_{k}.npy", v)
            cfg = cfg_with(inputs__bank=str(bank), inputs__detector_dir=str(det))
            run = copy.copy(RUN)
            run.cfg, run._bank_cv = cfg, None
            n_sent = int(np.any(np.asarray(INPUTS["MCgen"]) < -9000, axis=1).sum())
            run.staged = G.Staged(tmp / "stage")
            with mock.patch.object(LIB.uni, "SENTINEL_ROWS", n_sent), \
                    G.read_guards((bank, det), (G.REPO, tmp / "stage"), root=False):  # A1: the bank is read only as copies
                arrays, meta = run.universe("GEANT_Pion", "0")
            self.assertEqual(set(meta["weight_sha256"]), {"wt", "wr", "denom_nd", "bkgw"})
            self.assertEqual(meta["weight_sha256"], {k: G.sha256(det / f"GEANT_Pion_0_{k}.npy") for k in w})
            self.assertEqual(set(run.staged.sha), {p for _, p in G.unit_reads(LIB, cfg, [("universe", "GEANT_Pion", "0")])
                                                   if p not in (cfg["inputs"]["of_inputs_5d"], cfg["inputs"]["bkg_dump"])})
            self.assertEqual(list((tmp / "stage" / "GEANT_Pion_0").iterdir()), [])  # the unit's weight copies removed
            c, _ = RUN.central()
            self.assertFalse(np.array_equal(arrays["F_fold"], c["F_fold"]))
        finally:
            shutil.rmtree(tmp)

    def test_vertex_and_closure_read_the_pinned_ratio(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            sha = unit_ratio(tmp, "genie_mec")
            sha_n = unit_ratio(tmp, "nuwro")
            cfg = cfg_with(ratios__dir=str(tmp), ratios__sha256={"genie_mec": sha, "nuwro": sha_n})
            run = copy.copy(RUN)
            run.cfg, run.staged = cfg, G.Staged(tmp / "stage")
            with G.read_guards((tmp,), (G.REPO, tmp / "stage"), root=False):  # A1: the ratio is read only as its copy
                a, meta = run.vertex("genie_mec")  # r = 1: the prior is unchanged, so the vertex is the central
            c, _ = RUN.central()
            for k in ("F_fold", "F_sub"):
                np.testing.assert_array_equal(a[k], c[k])
            self.assertEqual(meta["ratio_sha256"], sha)
            cl, _ = run.closure("nuwro")
            nz = cl["X_true"] != 0
            np.testing.assert_allclose(cl["F_fold"][:, nz], np.broadcast_to(cl["X_true"][nz], cl["F_fold"][:, nz].shape),
                                       rtol=1e-12)
            run.cfg = cfg_with(ratios__dir=str(tmp), ratios__sha256={"genie_mec": "0" * 64})
            with self.assertRaises(G.GateFailure):
                run.vertex("genie_mec")
        finally:
            shutil.rmtree(tmp)

    def test_the_real_format_inputs_load_to_the_same_central(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            keys = ("MCgen", "MCreco", "measured", "pass_reco", "pass_truth", "w_truth", "w_reco", "measured_weights",
                    "denom_nd", "flux", "data_pot", "n_nucleons", "nedges")
            np.savez(tmp / "in.npz", **{k: INPUTS[k] for k in keys},
                     **{f"edges_{i}": e for i, e in enumerate(INPUTS["edges"])})
            loaded = s5c_unfold.load_inputs(tmp / "in.npz")
            run = G.Run(LIB, CFG, loaded, BKG, CONTRACT, chunk=7_000)
            a, _ = run.central()
            b, _ = RUN.central()
            for k in ("F_fold", "F_sub"):
                np.testing.assert_array_equal(a[k], b[k])
        finally:
            shutil.rmtree(tmp)

    def test_units_outside_the_declaration_are_refused(self):
        self.assertEqual(G.parse_units(CFG, ["replicas:1-3"]), [("replica", 1), ("replica", 2), ("replica", 3)])
        self.assertEqual(len(G.parse_units(CFG, ["universes:all"])), 175)
        for bad in ("replica:0", "replica:51", "replicas:40-60", "universe:Flux:100", "vertex:tune_v1", "closure:W1",
                    "central:x", "nominal"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                G.parse_units(CFG, [bad])


# ============================================================================== reader


E_META = {"config": "R", "capacity": None, "iters": 5, "estimator_seed": 42,
          "estimator_params": [{"n_estimators": 100, "num_leaves": 8, "random_state": 42}] * 3,
          "refinement": {"classifier_params": {"n_estimators": 400, "num_leaves": 31, "random_state": 45}}}


def xsec_for(cells: np.ndarray) -> np.ndarray:
    """A fine-grid cross section whose R00-R15 integrals are ``cells``: one fine cell per reporting cell."""
    x = np.zeros(U.shape[1])
    for c in range(16):
        f = int(np.flatnonzero(U[c] > 0)[0])
        x[f] = cells[c] / U[c, f]
    return x


class Fixture:
    """A run directory of IBU units and the (e) products they pair with, written in the producers' formats."""

    BANDS = {"Flux": 100, "MaRES": 2, "LowQ2": 2, "GEANT_Pion": 2}

    def __init__(self, shift: float = 0.0, flux_scale: float = 1e-3, seed: int = 0, draws: int = 20_000):
        rng = np.random.default_rng(seed)
        self.tmp = Path(tempfile.mkdtemp())
        self.run, e = self.tmp / "run", self.tmp / "e"
        self.run.mkdir()
        e.mkdir()
        self.v0 = 1e-39 * np.linspace(1, 3, 16)
        self.wflux = rng.uniform(0.5, 1.5, 100)
        lis = {g: [] for g in ("e_central", "e_replicas", "e_universes", "e_ladder_unfolds", "e_f0b_closures")}
        sig = 0.01 * self.v0

        def e_write(path, cells, meta, group, extra=None):
            np.savez(path, xsec_flat=xsec_for(cells), meta=json.dumps({**E_META, **meta}), **(extra or {}))
            lis[group].append({"path": str(path), "pin": G.sha256(path)})

        def ibu_write(name, cells, meta=None, extra=None):
            F = np.tile(cells, (len(KS), 1))
            G.ibu1.write(self.run / f"{name}.npz", {"ks": np.array(KS), "F_fold": F, "F_sub": F * 1.001, **(extra or {})},
                         meta or {})

        inp = {"input_npz_sha256": LIB.s1a.INPUT_NPZ_SHA256, "bkg_dump_sha256": LIB.s1a.BKG_SHA256}
        e_write(e / "central.npz", self.v0, {"schema": "s5p-numerics/1", "bootstrap_seed": None, **inp}, "e_central")
        self.x_ibu = self.v0 * (1 + shift)
        ibu_write("central", self.x_ibu)
        ibu_write("universe_CV", self.x_ibu)
        for b in range(1, 51):
            eb = self.v0 + sig * rng.standard_normal(16)
            e_write(e / f"data_b{b}_j{100 + b}.npz", eb, {"schema": "s5p-numerics/1", "bootstrap_seed": b,
                                                          "jitter_seed": 100 + b, "coords": "float64", **inp}, "e_replicas")
            ibu_write(f"replica_b{b}", eb + sig * rng.standard_normal(16),
                      {"bootstrap_seed": b, "jitter_seed": 100 + b, "g_draw": {"pass": True}})
        for band, n in self.BANDS.items():
            for i in range(n):
                det = band in LIB.s1a.DETECTOR_BANDS
                ws = {k: f"{band}{i}{k}" for k in ("wt", "wr", "bkgw", "denom_nd" if det else "tdw")}
                um = {"schema": "s5p-universe/1", "universe": f"{band}:{i}", "bank_weight_sha256": ws, "bank": "B",
                      "alignment": {"sentinel_rows": 2801}, **inp}
                if band == "Flux":
                    um.update(flux_universe_file="f.root", universe_info={"flux_ratio_mean": 1.0})
                scale = flux_scale if band == "Flux" else 1e-3
                eu = self.v0 * (1 + scale * rng.standard_normal(16))
                e_write(e / f"S1_{band}_{i}.npz", eu, um, "e_universes")
                ibu_write(f"universe_{band}_{i}", eu + 0.2 * scale * self.v0 * rng.standard_normal(16),
                          {"universe": f"{band}:{i}", "weight_sha256": ws})
        for v in CFG["vertices"]:
            cells = self.v0 * (1 + 0.02 * rng.standard_normal(16))
            e_write(e / f"L-5D-PV_e_{v}.npz", cells, {}, "e_ladder_unfolds")
            ibu_write(f"vertex_{v}", cells * (1 + 0.001 * rng.standard_normal(16)))
        for name, product in CFG["closures"].items():
            truth = self.v0 * 1.1
            e_write(e / f"{product}.npz", truth * (1 + 0.004 * np.sign(rng.standard_normal(16))), {}, "e_f0b_closures",
                    {"xtrue_flat": xsec_for(truth)})
            ibu_write(f"closure_{name}", truth * (1 + 0.002 * np.sign(rng.standard_normal(16))), extra={"X_true": truth})
        gib = {"ks": np.array(KS), "F_fold": np.ones((len(KS), 153)), "F_sub": np.ones((len(KS), 153)) * 2}
        rerun = self.tmp / "rerun"  # A1 §1: the gibu1 re-run writes into its own directory
        rerun.mkdir()
        self.gibu1 = rerun / "gibu1.npz"
        G.ibu1.write(self.gibu1, gib, {})
        G.ibu1.write(self.tmp / "D_N.npz", gib, {"schema": "ibu1-data/1"})
        np.savez(self.tmp / "s1_assembly.npz", f=U @ xsec_for(self.v0))
        listing = self.tmp / "listing.json"
        listing.write_text(json.dumps({"files": lis}))
        self.cfg = cfg_with(
            listing__path=str(listing),
            e_products={"central": str(e / "central.npz"), "replica": str(e / "data_b{b}_j{j}.npz"),
                        "universe": str(e / "S1_{tag}.npz"), "ladder": str(e / "L-5D-PV_e_{name}.npz"),
                        "closure": str(e / "{product}.npz"), "s1_assembly": str(self.tmp / "s1_assembly.npz"),
                        "s1_assembly_sha256": G.sha256(self.tmp / "s1_assembly.npz")},
            gibu1_reference={"path": str(self.tmp / "D_N.npz"), "sha256": G.sha256(self.tmp / "D_N.npz")})
        self.gibu1_pin = {"path": str(self.gibu1), "sha256": G.sha256(self.gibu1)}  # the read's arguments (A1 §1)
        self.cfg["readings"]["bars"].update(draws=draws, batch=2000)
        self.out = self.tmp / "out"
        # the declared inputs a run on the cluster finds on pscratch: read only as staged O_NOATIME copies
        self.protected = (e, self.tmp / "D_N.npz", self.tmp / "s1_assembly.npz")
        self.n_staged = 0

    def staged(self) -> G.Staged:
        self.n_staged += 1
        return G.Staged(self.out / f"inputs-{self.n_staged}")

    def bars(self):
        with G.read_guards(self.protected, (G.REPO, self.run, self.out), root=False):
            return R.bars(LIB, self.cfg, self.run, self.out / "bars.json", U, self.wflux, self.staged())

    def read(self, sha=None):
        p = self.out / "bars.json"
        with G.read_guards(self.protected, (G.REPO, self.run, self.out), root=False):
            return R.read(LIB, self.cfg, self.run, p, sha or G.sha256(p), self.out / "readout.json", U, self.wflux,
                          self.staged(), self.gibu1_pin)

    def close(self):
        shutil.rmtree(self.tmp)


class Readings(unittest.TestCase):
    def test_the_bars_are_ts_simulated_null_not_chi2(self):
        """Stat-dominated: T's null is Hotelling's, (49*16/34) F(16, 34), whose 0.95 point is about 45, far above
        chi2_16's 26.30; the self-check holds."""
        fx = Fixture(flux_scale=1e-6)
        try:
            rec = fx.bars()
            self.assertTrue(rec["self_check"]["pass"])
            law = R.hotelling_quantiles([0.95, 0.997], 50, 16)
            self.assertGreater(rec["bars"][0], 35.0)
            self.assertLess(abs(rec["bars"][0] / law[0] - 1), 0.08)
            self.assertGreater(rec["bars"][1], rec["bars"][0])
        finally:
            fx.close()

    def test_the_flux_block_is_resampled(self):
        fx = Fixture(flux_scale=0.05, draws=40_000)
        try:
            rec = fx.bars()
            p = R.Paired(LIB, fx.cfg, fx.run, U, fx.staged())
            dR, _ = p.replica_deltas()
            dU, _ = p.universe_deltas()
            cs = np.cov(dR, rowvar=False, ddof=1)
            cf, cx = R.universe_blocks(LIB, dU, fx.wflux)
            b = fx.cfg["readings"]["bars"]
            fixed = R.null_t(cs, cf, fx.wflux, cx, 50, b["draws"], b["seed"], b["batch"], 0.014, resample_flux=False)
            self.assertGreater(rec["bars"][1], 1.03 * float(np.quantile(fixed, 0.997)))
        finally:
            fx.close()

    def test_the_bars_never_read_the_central_difference(self):
        fx = Fixture(flux_scale=1e-3)
        try:
            a = fx.bars()
            (fx.out / "bars.json").unlink()
            arrays, meta = R.load(fx.run / "central.npz")
            (fx.run / "central.npz").unlink()
            G.ibu1.write(fx.run / "central.npz", {**arrays, "F_fold": arrays["F_fold"] * 1.5}, meta)
            b = fx.bars()
            self.assertEqual(a["bars"], b["bars"])
            self.assertEqual(a["sensitivity_stat_only_null"], b["sensitivity_stat_only_null"])
        finally:
            fx.close()

    def test_a_failed_self_check_writes_no_bars(self):
        fx = Fixture()
        try:
            real = R.hotelling_quantiles
            with mock.patch.object(R, "hotelling_quantiles", lambda qs, n, p: [1.3 * v for v in real(qs, n, p)]):
                with self.assertRaises(R.Refused):
                    fx.bars()
            self.assertFalse((fx.out / "bars.json").exists())
        finally:
            fx.close()

    def test_the_order_guard_and_the_bars_identity(self):
        fx = Fixture()
        try:
            fx.bars()
            rec = fx.read()
            self.assertTrue(rec["controls_pass"], rec["controls"])
            with self.assertRaises(R.Refused):  # the readout exists: no new bars beside it
                fx.bars()
            with self.assertRaises(R.Refused):
                fx.read(sha="0" * 64)
            arrays, meta = R.load(fx.run / "replica_b3.npz")
            (fx.run / "replica_b3.npz").unlink()
            G.ibu1.write(fx.run / "replica_b3.npz", {**arrays, "F_fold": arrays["F_fold"] * 1.01}, meta)
            with self.assertRaises(R.Refused):  # the bars came from other products
                fx.read()
        finally:
            fx.close()

    def test_bars_from_another_reader_or_config_are_refused(self):
        fx = Fixture()
        try:
            fx.bars()
            p = fx.out / "bars.json"
            good = json.loads(p.read_text())
            for key in ("reader_sha256", "config_sha256"):
                with self.subTest(key=key):
                    p.write_text(json.dumps({**good, key: "0" * 64}))
                    with self.assertRaises(R.Refused):
                        fx.read(sha=G.sha256(p))
                    self.assertFalse((fx.out / "readout.json").exists())
            p.write_text(json.dumps(good))
            self.assertIn("R1", fx.read(sha=G.sha256(p)))  # silent on a match
        finally:
            fx.close()

    def test_the_batch_weighted_covariance_is_s1s_mat_cov(self):
        rng = np.random.default_rng(9)
        Y = rng.standard_normal((5, 100, 16))
        w = rng.uniform(0.5, 1.5, 100)
        got = R.weighted_cov_batch(Y, w)
        for m in range(5):
            np.testing.assert_allclose(got[m], LIB.s1a.mat_cov(Y[m], w), rtol=1e-12, atol=1e-15)

    def test_r1_reads_agree_on_no_difference_and_differ_on_a_large_one(self):
        for shift, want in ((0.0, "agree"), (0.2, "differ")):
            fx = Fixture(shift=shift)
            try:
                fx.bars()
                rec = fx.read()
                with self.subTest(shift=shift):
                    self.assertEqual(rec["R1"]["reading"], want)
                    self.assertTrue(rec["controls_pass"], rec["controls"])
                    beside = rec["printed_beside_R1"]
                    self.assertAlmostEqual(beside["chi2_bars"][0], 26.2962, places=3)
                    np.testing.assert_allclose(beside["hartlap"]["F_bars"], [29.39, 46.09], rtol=2e-3)
                    self.assertEqual(len(beside["pulls"]), 16)
                    self.assertIn("leans toward 'agree'", beside["stated_direction"])
            finally:
                fx.close()

    def test_r1_is_not_formed_on_a_singular_covariance(self):
        C = np.eye(16)
        C[0, 0] = 0.0
        self.assertFalse(R.formed(C, 1e10)["pass"])
        C[0, 0] = 1e-11
        self.assertFalse(R.formed(C, 1e10)["pass"])
        self.assertTrue(R.formed(np.eye(16), 1e10)["pass"])

    def test_the_reading_words_at_their_bars(self):
        self.assertEqual(R.classify_r1(10.0, 10.0, 20.0), "agree")
        self.assertEqual(R.classify_r1(10.0 + 1e-9, 10.0, 20.0), "marginal")
        self.assertEqual(R.classify_r1(20.0, 10.0, 20.0), "marginal")
        self.assertEqual(R.classify_r1(20.0 + 1e-9, 10.0, 20.0), "differ")
        self.assertEqual(R.classify_r2(0.5, (0.5, 2.0)), "within")
        self.assertEqual(R.classify_r2(2.0, (0.5, 2.0)), "within")
        self.assertEqual(R.classify_r2(0.4999, (0.5, 2.0)), "IBU better")
        self.assertEqual(R.classify_r2(2.0001, (0.5, 2.0)), "IBU worse")

    def test_r2_and_r3_on_hand_set_products(self):
        fx = Fixture()
        try:
            fx.bars()
            rec = fx.read()
            for name in CFG["closures"]:
                r2 = rec["R2"][name]
                self.assertAlmostEqual(r2["median_abs_residual_ibu"], 0.002, places=12)
                self.assertAlmostEqual(r2["median_abs_residual_e"], 0.004, places=12)
                self.assertEqual(r2["reading"], "within")
                self.assertLess(r2["truths_agree_rel"], 1e-13)
            self.assertEqual(len(rec["R3"]["sigma_ibu_over_e"]), 16)
            self.assertGreater(rec["R3"]["median"], 0)
        finally:
            fx.close()


class Controls(unittest.TestCase):
    def tamper(self, fx, name, key, factor):
        arrays, meta = R.load(fx.run / f"{name}.npz") if not name.startswith("/") else R.load(Path(name))
        path = fx.run / f"{name}.npz" if not name.startswith("/") else Path(name)
        path.unlink()
        G.ibu1.write(path, {**arrays, key: arrays[key] * factor}, meta)

    def control(self, fx, name):
        fx.bars()
        rec = fx.read()
        if not rec["controls"][name]["pass"]:  # §3.3: a failed control stops the run, with no reading written
            self.assertTrue(rec.get("stopped"))
            self.assertIn(name, rec["stopped_by"])
            self.assertFalse((fx.out / "readout.json").exists())
            self.assertTrue((fx.out / "STOP.json").exists())
        return rec["controls"][name]

    def test_a_failed_control_stops_the_run_with_no_readings(self):
        fx = Fixture()
        try:
            arrays, meta = R.load(fx.run / "replica_b2.npz")
            (fx.run / "replica_b2.npz").unlink()
            G.ibu1.write(fx.run / "replica_b2.npz", arrays, {**meta, "g_draw": {"pass": False}})
            fx.bars()
            rec = fx.read()
            self.assertEqual(rec["stopped_by"], ["G-draw"])
            self.assertNotIn("R1", rec)
            self.assertFalse((fx.out / "readout.json").exists())
            stop = json.loads((fx.out / "STOP.json").read_text())
            self.assertEqual(stop["stopped_by"], ["G-draw"])
            argv = ["read", "--run", str(fx.run), "--bars", str(fx.out / "bars.json"), "--bars-sha256",
                    G.sha256(fx.out / "bars.json"), "--out", str(fx.out / "readout.json")]
            with mock.patch.object(R, "command", lambda *a, **k: rec), mock.patch.object(G, "Lib", lambda cfg: LIB):
                self.assertEqual(R.main(argv), 1)
        finally:
            fx.close()

    def test_g_cv_fires_on_either_variant(self):
        for key in ("F_fold", "F_sub"):
            fx = Fixture()
            try:
                self.tamper(fx, "universe_CV", key, 1 + 1e-15 * 8)
                with self.subTest(key=key):
                    self.assertFalse(self.control(fx, "G-CV")["pass"])
            finally:
                fx.close()

    def test_g_ibu1_fires_on_either_variant_and_on_the_pin(self):
        for key in ("F_fold", "F_sub"):
            fx = Fixture()
            try:
                self.tamper(fx, str(fx.gibu1), key, 1.0000001)
                fx.gibu1_pin["sha256"] = G.sha256(fx.gibu1)  # re-pinned: the arrays decide
                with self.subTest(key=key):
                    c = self.control(fx, "G-IBU1")
                    self.assertFalse(c["pass"])
                    self.assertFalse(c["arrays"][key])
            finally:
                fx.close()
        for pin in ("gibu1_reference", "gibu1_product"):
            fx = Fixture()
            try:
                (fx.cfg["gibu1_reference"] if pin == "gibu1_reference" else fx.gibu1_pin)["sha256"] = "0" * 64
                with self.subTest(pin=pin):
                    self.assertFalse(self.control(fx, "G-IBU1")["pass"])
            finally:
                fx.close()

    def test_g_cells_holds_at_its_tolerance(self):
        for rel, ok in ((1e-10, False), (1e-14, True)):
            fx = Fixture()
            try:
                p = Path(fx.cfg["e_products"]["s1_assembly"])
                f = np.load(p)["f"] * (1 + rel)
                np.savez(p, f=f)
                fx.cfg["e_products"]["s1_assembly_sha256"] = G.sha256(p)
                with self.subTest(rel=rel):
                    self.assertEqual(self.control(fx, "G-cells")["pass"], ok)
            finally:
                fx.close()

    def test_g_pair_fires_on_a_pin_a_swapped_replica_and_a_universe_from_other_weights(self):
        fx = Fixture()
        try:
            e = Path(fx.cfg["e_products"]["central"]).parent
            a, b = e / "data_b4_j104.npz", e / "data_b5_j105.npz"
            tmp = e / "swap.npz"
            a.rename(tmp)
            b.rename(a)
            tmp.rename(b)
            self.assertFalse(self.control(fx, "G-pair")["pass"])
        finally:
            fx.close()
        fx = Fixture()
        try:
            listing = json.loads(Path(fx.cfg["listing"]["path"]).read_text())
            listing["files"]["e_ladder_unfolds"][0]["pin"] = "0" * 64
            Path(fx.cfg["listing"]["path"]).write_text(json.dumps(listing))
            self.assertFalse(self.control(fx, "G-pair")["pass"])
        finally:
            fx.close()
        fx = Fixture()
        try:
            arrays, meta = R.load(fx.run / "universe_MaRES_1.npz")
            (fx.run / "universe_MaRES_1.npz").unlink()
            G.ibu1.write(fx.run / "universe_MaRES_1.npz", arrays, {**meta, "weight_sha256": {"wt": "x"}})
            self.assertFalse(self.control(fx, "G-pair")["pass"])
        finally:
            fx.close()

    def test_g_draw_fires_on_one_failed_replica(self):
        fx = Fixture()
        try:
            arrays, meta = R.load(fx.run / "replica_b9.npz")
            (fx.run / "replica_b9.npz").unlink()
            G.ibu1.write(fx.run / "replica_b9.npz", arrays, {**meta, "g_draw": {"pass": False}})
            self.assertFalse(self.control(fx, "G-draw")["pass"])
        finally:
            fx.close()


class Reads(unittest.TestCase):
    """A1 §2: O_NOATIME or a refusal; declared inputs read only as staged copies; the audit hook and the TFile guard
    fire on a plain read and stay silent on the allowed ones."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_o_noatime_absent_is_refused(self):
        f = self.tmp / "a.bin"
        f.write_bytes(b"x")
        with mock.patch.object(os, "O_NOATIME", 0, create=True):
            del os.O_NOATIME  # the platform has none
            with self.assertRaises(G.GateFailure):
                G.copy_noatime(f, self.tmp / "copy.bin")
        self.assertFalse((self.tmp / "copy.bin").exists())
        self.assertEqual(G.copy_noatime(f, self.tmp / "copy.bin"), G.sha256(f))

    def test_the_audit_guard_fires_on_a_plain_read_and_is_silent_otherwise(self):
        prot, ok = self.tmp / "protected", self.tmp / "allowed"
        prot.mkdir()
        ok.mkdir()
        for d in (prot, ok, self.tmp):
            np.save(d / "a.npy", np.arange(3))
        with G.read_guards((prot,), (ok,), root=False):
            for plain in (lambda: np.load(prot / "a.npy"), lambda: np.load(prot / "a.npy", mmap_mode="r"),
                          lambda: open(prot / "a.npy", "rb").close(), lambda: G.sha256(prot / "a.npy"),
                          lambda: (prot / "a.npy").read_bytes()):
                with self.assertRaises(G.GateFailure):
                    plain()
            st = G.Staged(ok / "stage")
            np.testing.assert_array_equal(np.load(st(prot / "a.npy")), np.arange(3))  # through O_NOATIME, then the copy
            (prot / "new.txt").write_text("written")  # a write is not a read
            np.load(ok / "a.npy")
            np.load(self.tmp / "a.npy")
        np.load(prot / "a.npy")  # inactive outside the block

    def test_the_tfile_guard_refuses_root_reads_outside_the_roots(self):
        """ROOT is not in this suite's environment; a stand-in module carries TFile.Open, so the guard's own logic runs."""
        opened = []
        fake = type(sys)("ROOT")
        fake.TFile = type("TFile", (), {"Open": staticmethod(lambda path, mode="READ": opened.append((path, mode)))})
        run, other = self.tmp / "run", self.tmp / "other"
        run.mkdir()
        other.mkdir()
        with mock.patch.dict(sys.modules, {"ROOT": fake}):
            with G.read_guards((), (run,), root=True):
                with self.assertRaises(G.GateFailure):
                    fake.TFile.Open(str(other / "f.root"))
                for mode in ("UPDATE", "READ_WITHOUT_GLOBALREGISTRATION", "RECREATE"):  # any mode, outside
                    with self.assertRaises(G.GateFailure):
                        fake.TFile.Open(str(other / "f.root"), mode)
                fake.TFile.Open(str(run / "f.root"))
            fake.TFile.Open(str(other / "f.root"))
        self.assertEqual([p for p, _ in opened], [str(run / "f.root"), str(other / "f.root")])

    def test_a_block_without_the_tfile_guard_refuses_a_root_import(self):
        """Without ``root`` the guard does not import ROOT, and the block fails if anything does (L2 on #806); the
        gibu1 unit's set needs no ROOT, a Flux universe's does."""
        fake = type(sys)("ROOT")
        with self.assertRaises(G.GateFailure):
            with mock.patch.dict(sys.modules):
                with G.read_guards((), (self.tmp,), root=False):
                    sys.modules["ROOT"] = fake  # as `import ROOT` inside the block would
        with mock.patch.dict(sys.modules):
            with G.read_guards((), (self.tmp,), root=False):
                pass  # silent when nothing imports ROOT
        self.assertNotIn("ROOT", sys.modules)
        self.assertFalse(G.needs_root([("gibu1",), ("central",), ("universe", "MaRES", "0")]))
        self.assertTrue(G.needs_root([("universe", "Flux", "3")]))
        self.assertIs(G.environment()["root_loaded"], False)

    def test_a_staging_directory_is_new(self):
        G.Staged(self.tmp / "s")
        with self.assertRaises(G.GateFailure):
            G.Staged(self.tmp / "s")

    def test_the_reader_stages_its_declared_set_and_the_digest_is_unchanged(self):
        fx = Fixture()
        try:
            st = G.Staged(fx.out / "inputs-x")
            paired = R.Paired(LIB, fx.cfg, fx.run, U, st)
            old = hashlib.sha256()  # Paired.digest as bound at M: every file hashed in place
            for b in paired.bs:
                for p in (fx.run / f"replica_b{b}.npz", paired.replica_paths[b]):
                    old.update(G.sha256(p).encode())
            for t in paired.tags:
                b, i = t.split(":")
                for p in (fx.run / f"universe_{b}_{i}.npz", paired.universe_paths[t]):
                    old.update(G.sha256(p).encode())
            self.assertEqual(paired.digest(), old.hexdigest())
            fx.bars()
            rec = fx.read()
            self.assertTrue(rec["controls_pass"], rec["controls"])
            declared = {p for role, p in R.reader_reads(fx.cfg, fx.gibu1_pin["path"]) if role != "flux_constraint"}
            self.assertEqual(set(rec["staged_sha256"]), declared)  # every declared file, and only those
            self.assertEqual(rec["staged_sha256"], {p: G.sha256(Path(p)) for p in declared})
        finally:
            fx.close()

    def test_the_units_load_the_staged_inputs(self):
        """run_units hands ibu1.load_inputs (which checks the pins and loads) the O_NOATIME copies, never the
        originals; under the guard a plain read of an original would raise."""
        src = self.tmp / "src"
        src.mkdir()
        (src / "in.npz").write_bytes(b"npz bytes")
        (src / "bkg.npz").write_bytes(b"bkg bytes")
        cfg = cfg_with(inputs__of_inputs_5d=str(src / "in.npz"), inputs__bkg_dump=str(src / "bkg.npz"))
        got = []

        def load_inputs(prod, icfg, npz, bkg):
            got.append((Path(npz), Path(bkg), npz.read_bytes(), bkg.read_bytes()))
            return INPUTS, BKG
        st = G.Staged(self.tmp / "stage")
        with mock.patch.object(G.ibu1, "load_inputs", load_inputs), \
                G.read_guards((src,), (G.REPO, self.tmp / "out", self.tmp / "stage"), root=False):
            self.assertEqual(G.run_units(cfg, [("central",)], self.tmp / "out", st), 0)
        (npz, bkg, nb, bb), = got
        self.assertTrue(G.under(npz, st.root.resolve()) and G.under(bkg, st.root.resolve()))
        self.assertEqual((nb, bb), (b"npz bytes", b"bkg bytes"))
        self.assertEqual(set(st.sha), {p for _, p in G.unit_reads(LIB, cfg, [("central",)])})
        self.assertTrue((self.tmp / "out" / "central.npz").exists())

    def test_the_constraint_is_read_as_a_copy(self):
        fx = Fixture()
        try:
            c = fx.tmp / "constraint.txt"
            c.write_text("".join(f"Flux {i} {float(w)!r}\n" for i, w in enumerate(fx.wflux)) + "Other 0 1.0\n")
            fx.cfg["inputs"]["flux_constraint"] = str(c)
            a = type("A", (), {"cmd": "bars", "run": fx.run, "out": fx.out / "bars.json"})
            with mock.patch.object(LIB.s1a, "CONSTRAINT_SHA256", G.sha256(c)), \
                    G.read_guards((*fx.protected, c), (G.REPO, fx.run, fx.out), root=False):
                rec = R.command(LIB, fx.cfg, a, G.Staged(fx.out / "inputs-cmd"))
            self.assertIn(str(c), rec["staged_sha256"])
            self.assertEqual(rec["flux_universes"], 100)
        finally:
            fx.close()

    def test_the_read_refuses_until_the_gibu1_product_is_given(self):
        fx = Fixture()
        try:
            a = type("A", (), {"cmd": "read", "run": fx.run, "bars": fx.out / "bars.json", "bars_sha256": "x",
                               "out": fx.out / "readout.json", "gibu1_product": None, "gibu1_sha256": None})
            with mock.patch.object(LIB.s1a, "flux_weights", lambda path: fx.wflux), \
                    mock.patch.dict(fx.cfg["inputs"], {"flux_constraint": str(fx.tmp / "s1_assembly.npz")}):
                with self.assertRaises(R.Refused):
                    R.command(LIB, fx.cfg, a, G.Staged(fx.out / "inputs-cmd"))
            self.assertNotIn("gibu1_product", dict(R.reader_reads(fx.cfg)))
            self.assertNotIn("gibu1_product", CFG)  # A1 §1, option (a): the pin is not in config.json
        finally:
            fx.close()

    def test_bars_then_the_pin_merge_then_the_read(self):
        """B1 on #806: the bars record config.json's digest, so nothing between the bars and the read may change it.
        The gibu1 re-run's pin is committed beside bars.json and given to the read, and the read forms a reading; a
        changed config.json between the two is refused."""
        fx = Fixture()
        try:
            cfg_copy = fx.tmp / "config.json"
            cfg_copy.write_bytes(G.CONFIG.read_bytes())
            with mock.patch.object(G, "CONFIG", cfg_copy):
                fx.bars()
                pins = fx.out / "gibu1-pin.json"  # the merge: bars.json and the pin, config.json untouched
                pins.write_text(json.dumps(fx.gibu1_pin))
                fx.gibu1_pin = json.loads(pins.read_text())
                rec = fx.read()
                self.assertIn("R1", rec)
                self.assertEqual(rec["gibu1_product"], fx.gibu1_pin)
                (fx.out / "readout.json").unlink()
                cfg_copy.write_text(json.dumps({**json.loads(cfg_copy.read_text()), "gibu1_product": fx.gibu1_pin}))
                with self.assertRaises(R.Refused):  # option (b)'s defect: the pin merged into config.json
                    fx.read()
        finally:
            fx.close()

def tearDownModule():
    NOATIME_SUB.stop()


if __name__ == "__main__":
    unittest.main()
