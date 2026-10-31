"""Controls for 1B's toy mode, scorer and task tables (state/measurement-paper/5d-community-20261024/FD-1B-DECLARATION.md
section 8.4), in both directions: each rule must pass what it should pass and fail what it should fail.

* the scorer's constants are the declaration's numbers, held against the declaration's own text;
* synthetic coverage fixtures PASS at a matched scale and FAIL at x0.7 and x1.3, two-sided at the control and
  one-sided at a test arm; 4A passes a matched matrix, fails a small one and refuses one that is not positive definite;
* the 1/2-1/2 endpoint draw, the 2p2h draw and the w_u / sum w flux draw reproduce S1's block estimators, exactly by
  enumeration and in the toys' own draw records;
* the toy mode with every draw off, given F1c's own argv builder, reproduces F1c's experiment and product bitwise (the
  unfold is replaced by a deterministic recorder, the same in both runs, since LightGBM does not run here);
* the refusals: seeds, arms, pins, digests, a draw or truth that departs from the declared one, a missing toy;
* gate D reproduces S1's blocks exactly when the toys' shifts carry them, and stops when they do not;
* every submit line is account m3246, QOS regular, constraint cpu, under 12 h, through the committed packer.

No real data are read: the fixtures are a small synthetic 5D world."""
import hashlib
import json
import math
import os
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(1, str(ND))
import fd_1b_score as fs  # noqa: E402
import fd_1b_tasks as ft  # noqa: E402
import fd_1b_toys as toys  # noqa: E402
import fd_f1_tasks  # noqa: E402
import s1_assemble as sa  # noqa: E402
import s5c_pseudo  # noqa: E402
import s5e_candidate  # noqa: E402
import s5n_pseudo  # noqa: E402
import s5p_nullexp as ne  # noqa: E402
import s5p_universe  # noqa: E402

REPO = ND.parent
DECL = REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024/FD-1B-DECLARATION.md"
DECL_SHA256_PREFIX = "07d0e0b6b722c7de"   # the file the director bound (FD-1B-BINDING.md)
EDGES = [np.array([0.0, 1.0, 2.0]), np.array([0.0, 1.0, 2.0]), np.array([0.0, 0.5, 1.0]),
         np.array([0.0, 1.0, 2.0, 3.0]), np.array([0.0, 1.5, 3.0])]
SHAPE = tuple(len(e) - 1 for e in EDGES)


def digest(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def flat(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("*", ""))


# --------------------------------------------------------------------------------------------- the synthetic world


class World:
    """A small 5D world with every file a toy reads: inputs, background dump, bank, detector dump, constraint file,
    sf1-style manifest, detector receipt, pins, F1 prep ratios and sums."""

    def __init__(self, root: Path, n=3000, nb=500, seed=0):
        rng = np.random.default_rng(seed)
        self.root = root
        gen = np.column_stack([rng.uniform(0, 2, n), rng.uniform(0, 2, n), rng.uniform(0, 1, n),
                               rng.uniform(0, 3, n), rng.uniform(0, 3, n)])
        sentinel = np.arange(20)
        gen[sentinel] = -9999.0
        reco = np.clip(gen + rng.normal(0, 0.05, gen.shape), 0.001, None)
        reco[sentinel] = np.abs(rng.normal(1, 0.1, (20, 5)))
        pass_truth = np.ones(n, bool)
        pass_truth[sentinel] = False
        pass_reco = rng.uniform(size=n) < 0.85
        self.inputs = root / "inputs.npz"
        np.savez(self.inputs, MCgen=gen, MCreco=reco, measured=reco[:400] + 0.01, pass_reco=pass_reco,
                 pass_truth=pass_truth, w_truth=rng.uniform(0.5, 1.5, n), w_reco=rng.uniform(0.5, 1.5, n),
                 measured_weights=np.ones(400), denom_nd=rng.uniform(50, 80, SHAPE), flux=np.array([1e-4, 2e-4]),
                 data_pot=np.array(1e20), n_nucleons=np.array(1e30), nedges=np.array(5),
                 **{f"edges_{i}": e for i, e in enumerate(EDGES)})
        bkg_reco = np.column_stack([rng.uniform(0, 2, nb), rng.uniform(0, 2, nb), rng.uniform(0, 1, nb),
                                    rng.uniform(0, 3, nb), rng.uniform(0, 3, nb)])
        self.bkg = root / "bkg.npz"
        np.savez(self.bkg, bkg_reco=bkg_reco, bkg_w=rng.uniform(0.1, 0.4, nb), bkg_nd=np.zeros(SHAPE),
                 meta=json.dumps({"npz_sha256": digest(self.inputs)}))
        self.bank, self.det = root / "bank", root / "det"
        self.bank.mkdir()
        self.det.mkdir()
        bank_gen = gen.copy()
        bank_gen[sentinel] = np.nan
        np.savez(self.bank / "cv.npz", MCgen=bank_gen, MCreco=reco, pass_reco=pass_reco, pass_truth=pass_truth,
                 measured=reco[:400] + 0.01, bkg_cols=bkg_reco)
        z = np.load(self.inputs)
        bz = np.load(self.bkg)
        tags_bank = ([f"Flux_{i}" for i in range(100)] + [u for u in toys.s1_universes()
                                                        if u.rpartition("_")[0] not in sa.DETECTOR_BANDS
                                                        and not u.startswith("Flux_")]
                     + ["Rvp1pi_0", "Rvp1pi_1"] + [f"GEANT_{b}_{i}" for b in ("Neutron", "Pion", "Proton") for i in (0, 1)])
        for t in tags_bank:
            r = np.random.default_rng(abs(hash(("bank", t))) % (2 ** 32))
            np.save(self.bank / f"{t}_wt.npy", z["w_truth"] * r.uniform(0.9, 1.1, n))
            np.save(self.bank / f"{t}_wr.npy", z["w_reco"] * r.uniform(0.9, 1.1, n))
            np.save(self.bank / f"{t}_tdw.npy", r.uniform(0.9, 1.1, 50))
            np.save(self.bank / f"{t}_bkgw.npy", bz["bkg_w"] * r.uniform(0.9, 1.1, nb))
        for b in sa.DETECTOR_BANDS:
            for i in (0, 1):
                t = f"{b}_{i}"
                r = np.random.default_rng(abs(hash(("det", t))) % (2 ** 32))
                np.save(self.det / f"{t}_wt.npy", z["w_truth"] * r.uniform(0.9, 1.1, n))
                np.save(self.det / f"{t}_wr.npy", z["w_reco"] * r.uniform(0.9, 1.1, n))
                np.save(self.det / f"{t}_denom_nd.npy", r.uniform(50, 80, SHAPE))
                np.save(self.det / f"{t}_bkgw.npy", bz["bkg_w"] * r.uniform(0.9, 1.1, nb))
        self.receipt = root / "detector-dump.json"
        self.receipt.write_text(json.dumps({"files_sha256": {p.name: digest(p) for p in sorted(self.det.iterdir())}}))
        self.manifest = root / "inputs-sha256.txt"
        self.manifest.write_text("".join(f"{digest(p)}  {p}\n" for p in sorted(self.bank.iterdir()))
                                 + f"{digest(self.receipt)}  {self.receipt}\n")
        self.constraint = root / "constraint.txt"
        w = rng.uniform(0.5, 4.0, 100)
        self.constraint.write_text("".join(f"Flux {i} {w[i]!r}\n" for i in range(100)) + "Other 0 1.0\n")
        self.flux_w = w
        self.pins = root / "pins.json"
        self.pins.write_text(json.dumps(toys.make_pins(self.bank, self.det, self.manifest, self.receipt)))
        self.prep = root / "prep"
        for sub in ("bridged", "ratios/L-5D-PV"):
            (self.prep / sub).mkdir(parents=True)
        for k, name in enumerate(("genie_v3_g18", "genie_v3_ar23")):
            ratio = {"schema": "s5e-shape-ratio/1", "axes": [2], "edges": [EDGES[2].tolist()],
                     "shape_ratio": [1.0 + 0.1 * (k + 1), 1.0 - 0.05 * (k + 1)]}
            (self.prep / "bridged" / f"{name}.json").write_text(json.dumps(ratio))
            (self.prep / "ratios/L-5D-PV" / f"{name}.json").write_text(json.dumps({"x": k}))
        self.sums = root / "f1-prep-SHA256SUMS"
        self.sums.write_text("".join(f"{digest(p)}  ./{p.relative_to(self.prep)}\n"
                                     for p in sorted(self.prep.rglob("*.json"))))

    def patches(self):
        return [mock.patch.object(sa, "INPUT_NPZ_SHA256", digest(self.inputs)),
                mock.patch.object(sa, "BKG_SHA256", digest(self.bkg)),
                mock.patch.object(sa, "CONSTRAINT_SHA256", digest(self.constraint)),
                mock.patch.object(s5p_universe, "SENTINEL_ROWS", 20),
                mock.patch.object(toys, "F1_SUMS", self.sums),
                mock.patch.object(fd_f1_tasks, "NPZ", (str(self.inputs), digest(self.inputs))),
                mock.patch.object(fd_f1_tasks, "BKG", (str(self.bkg), digest(self.bkg)))]

    def run_argv(self, arm, mode, out, seeds=None, universes=None, no_draws=False, pins_sha=None):
        argv = ["run", "--arm", arm, "--mode", mode, "--npz", str(self.inputs), "--bkg", str(self.bkg),
                "--expect-npz-sha256", digest(self.inputs), "--expect-bkg-sha256", digest(self.bkg),
                "--bank", str(self.bank), "--detector-dir", str(self.det), "--pins", str(self.pins),
                "--expect-pins-sha256", pins_sha or digest(self.pins), "--flux-constraint", str(self.constraint),
                "--prep", str(self.prep), "--threads", "32", "--tag", "t", "--out", str(out)]
        argv += ["--seeds", seeds] if seeds else []
        argv += ["--universes", universes] if universes else []
        return argv + (["--no-draws"] if no_draws else [])


CALLS: list = []


def fake_unfold(exp, estimator_seed, threads, iters, permute_seed=None, refine_fn=None, unfold_fn=None):
    """A deterministic stand-in for the production unfold: a fixed function of every array it is given."""
    CALLS.append({"exp": exp, "args": (estimator_seed, threads, iters, permute_seed)})
    h = np.histogramdd(exp["obs"], bins=exp["edges"], weights=exp["obs_counts"])[0]
    m = np.histogramdd(exp["MCgen"], bins=exp["edges"], weights=exp["w_truth"] * (1 + 0.1 * exp["w_reco"]))[0]
    t = np.histogramdd(exp["tmpl"], bins=exp["edges"], weights=exp["tmpl_w"])[0]
    ev = {"refinement": {"classifier_params": {"n_estimators": 400, "num_leaves": 31, "random_state": estimator_seed + 3}},
          "estimator_params": [{"n_estimators": 100, "num_leaves": 8, "random_state": estimator_seed}] * 3}
    return h + 1e-3 * m - 0.5 * t, ev


class WorldCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="fd1b-test-"))
        cls.world = World(cls.tmp)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def setUp(self):
        self.saved = {k: getattr(s5n_pseudo, k) for k in ("refine_params", "code_digests", "truth_weight", "TRUTHS",
                                                          "unfold_negweight")}
        self.ps = self.world.patches() + [mock.patch.object(s5n_pseudo, "unfold_negweight", fake_unfold)]
        for p in self.ps:
            p.start()
        CALLS.clear()
        self.out = Path(tempfile.mkdtemp(dir=self.tmp))

    def tearDown(self):
        for p in reversed(self.ps):
            p.stop()
        for k, v in self.saved.items():
            setattr(s5n_pseudo, k, v)

    def loaded(self):
        inputs = s5n_pseudo.s5c_unfold.load_inputs(self.world.inputs)
        bz = np.load(self.world.bkg, allow_pickle=True)
        return inputs, {"bkg_reco": bz["bkg_reco"], "bkg_w": bz["bkg_w"], "bkg_nd": bz["bkg_nd"]}


# ----------------------------------------------------------------------------------------------------- constants


class Constants(unittest.TestCase):
    def test_the_declaration_is_the_bound_file(self):
        self.assertTrue(digest(DECL).startswith(DECL_SHA256_PREFIX))

    def test_windows_ses_flags_and_seeds_are_the_declarations_numbers(self):
        text = flat(DECL.read_text())
        w1, w2 = fs.WINDOWS[1], fs.WINDOWS[2]
        want = f"C1 ∈ [{w1[0]:.6f}, {w1[1]:.6f}] and C2 ∈ [{w2[0]:.6f}, {w2[1]:.6f}]"
        self.assertIn(want, text)
        self.assertEqual(want, "C1 ∈ [0.631880, 0.728668] and C2 ∈ [0.928139, 0.972193]")
        cw = fs.chi2_windows()
        self.assertIn(f"mean χ² must lie in [{cw['mean'][0]:.3f}, {cw['mean'][1]:.3f}]", text)
        self.assertIn(f"must lie in [{cw['tail'][0]:.4f}, {cw['tail'][1]:.4f}]", text)
        self.assertIn(f"26.296, χ²₁₆'s 95th percentile", text)
        self.assertAlmostEqual(fs.chi2_sf(fs.CHI2_Q95), 0.05, places=12)
        n = fs.N_TOYS["final"]
        self.assertEqual((fs.flag_threshold(n, 1), fs.flag_threshold(n, 2)), (182, 276))
        self.assertIn("ĉ_c(1) ≤ 182/300 = 0.6067 or ĉ_c(2) ≤ 276/300 = 0.9200", text)
        se = [math.sqrt(fs.NOMINAL[k] * (1 - fs.NOMINAL[k]) / n) for k in (1, 2)]
        self.assertIn(f"SE is {se[0]:.4f} (k = 1) and {se[1]:.4f} (k = 2)", text)
        self.assertIn(f"{fs.N_BOOT:,} resamples, generator seed {fs.BOOT_SEED}", text)
        self.assertEqual((fs.N_BOOT, fs.BOOT_SEED, fs.LEVEL, fs.N_TOYS),
                         (20_000, 20_261_030, {"interim": 0.995, "final": 0.95}, {"interim": 100, "final": 300}))
        self.assertIn("99.5 % at the interim look, 95 % at the final look", text)
        self.assertEqual((fs.WILSON_LEVEL, fs.FLAG_LEVEL, fs.SCALE_TOLERANCE, fs.CONTROL_SCALES),
                         (0.95, 0.995, (0.9, 1.1), (0.7, 1.3)))
        for arm, label in (("control", "control | nominal"), ("g18", "G18 | G18_10a_02_11b"), ("ar23", "AR23 | AR23")):
            lo, hi = toys.ARMS[arm][1:]
            self.assertIn(f"{lo:,}–{hi:,}", text)
            self.assertEqual(hi - lo + 1, 300)
        self.assertIn("seeds 2,600,000–2,600,015", text)

    def test_the_matrices_and_estimator_are_the_declared_ones(self):
        self.assertEqual(digest(fs.DATA_PRODUCT), fs.DATA_PRODUCT_SHA256)
        text = flat(DECL.read_text())
        self.assertIn(fs.DATA_PRODUCT_SHA256, text)
        self.assertIn(fs.S1_NPZ_SHA256[:8], text)
        self.assertEqual((toys.CONFIG, toys.ESTIMATOR_SEED, toys.ITERS), ("R", 42, 5))
        self.assertEqual(fs.vl.__file__, str(REPO / "2d-unfolding/uq/coverage_fixed_truth/score_coverage.py"))
        self.assertEqual(fs.NORM, 0.014)


# ------------------------------------------------------------------------------------------------------- the draws


class Draws(unittest.TestCase):
    groups = fs.declared_groups()

    def test_flux_probability_reproduces_s1s_weighted_block_exactly(self):
        rng = np.random.default_rng(3)
        X = rng.normal(size=(100, 16))
        w = rng.uniform(0.5, 4.0, 100)
        p = w / w.sum()
        mu = p @ X
        exact = ((X - mu).T * p) @ (X - mu)
        np.testing.assert_allclose(exact, sa.mat_cov(X, w), rtol=1e-12, atol=1e-14)
        uniform = sa.mat_cov(X)
        self.assertGreater(np.abs(exact - uniform).max(), 1e-3)  # the weighting matters

    def test_endpoint_and_2p2h_draws_reproduce_the_pair_estimator_exactly(self):
        rng = np.random.default_rng(4)
        pair = rng.normal(size=(2, 16))
        d = pair[1] - pair[0]
        half = 0.5 * sum(np.outer(x - pair.mean(0), x - pair.mean(0)) for x in pair)
        np.testing.assert_allclose(half, sa.mat_cov(pair), rtol=1e-12)
        np.testing.assert_allclose(half, 0.25 * np.outer(d, d), rtol=1e-12)
        three = rng.normal(size=(3, 16))
        np.testing.assert_allclose(sum(np.outer(x - three.mean(0), x - three.mean(0)) for x in three) / 3,
                                   sa.mat_cov(three), rtol=1e-12)

    def test_the_toys_draw_records_have_the_declared_frequencies(self):
        rng = np.random.default_rng(5)
        w = rng.uniform(0.5, 4.0, 100)
        p = w / w.sum()
        n = 6000
        D = [toys.draw_for_seed(2_610_000 + s, p, self.groups) for s in range(n)]
        cnt = np.bincount([d["flux"] for d in D], minlength=100)
        z = (cnt - n * p) / np.sqrt(n * p * (1 - p))
        self.assertLess(np.abs(z).max(), 4.5)
        self.assertLess(abs(np.mean(z ** 2) - 1), 0.35)
        for b in ("MaRES", "LowQ2"):
            self.assertLess(abs(np.mean([d["model"][b] == f"{b}_1" for d in D]) - 0.5), 4 * 0.5 / math.sqrt(n))
        for i in range(3):
            self.assertLess(abs(np.mean([d["model"]["2p2h"] == f"2p2h_{i}" for d in D]) - 1 / 3), 4 * 0.47 / math.sqrt(n))
        for b in toys.DETECTOR_DRAW_ORDER:
            self.assertLess(abs(np.mean([d["detector"][b] for d in D]) - 0.5), 4 * 0.5 / math.sqrt(n))
        for b in toys.LATERAL_DRAW_ORDER:
            s = np.array([d["lateral_s"][b] for d in D])
            self.assertTrue(set(s) == {-1, 1})
            self.assertLess(abs(s.mean()), 4 / math.sqrt(n))
        zn = np.array([d["normalization_z"] for d in D])
        self.assertLess(abs(zn.mean()), 4 / math.sqrt(n))
        self.assertLess(abs(zn.var() - 1), 0.1)
        self.assertNotIn("Rvp1pi", D[0]["model"])
        self.assertEqual(sorted(D[0]["model"]), sorted(toys.INTERACTION_BANDS))

    def test_independent_band_draws_add_to_the_sum_of_s1s_blocks(self):
        rng = np.random.default_rng(6)
        w = rng.uniform(0.5, 4.0, 100)
        p = w / w.sum()
        shifts = {"flux": rng.normal(size=(100, 16))}
        for b in toys.INTERACTION_BANDS:
            shifts[b] = rng.normal(size=(sa.EXPECT[b], 16)) * 0.5
        for b in toys.DETECTOR_DRAW_ORDER:
            shifts[b] = rng.normal(size=(2, 16)) * 0.5
        blocks = sa.mat_cov(shifts["flux"], w) + sum(sa.mat_cov(shifts[b]) for b in shifts if b != "flux")
        n = 6000
        Y = []
        for s in range(n):
            d = toys.draw_for_seed(2_620_000 + s, p, self.groups)
            y = shifts["flux"][d["flux"]].copy()
            for b, u in d["model"].items():
                y += shifts[b][int(u.rpartition("_")[2])]
            for b, i in d["detector"].items():
                y += shifts[b][i]
            Y.append(y)
        emp = np.cov(np.array(Y), rowvar=False)
        self.assertLess(np.abs(np.diag(emp) / np.diag(blocks) - 1).max(), 0.1)

    def test_the_draw_is_fixed_by_the_seed(self):
        p = np.full(100, 0.01)
        self.assertEqual(toys.draw_for_seed(7, p, self.groups), toys.draw_for_seed(7, p, self.groups))
        self.assertNotEqual(toys.draw_for_seed(7, p, self.groups), toys.draw_for_seed(8, p, self.groups))

    def test_single_universe_draws_name_one_universe(self):
        self.assertEqual(toys.single_universe("CV"), {"flux": None, "model": {}, "detector": {}})
        self.assertEqual(toys.single_universe("Flux_7")["flux"], 7)
        self.assertEqual(toys.single_universe("MaRES_1")["model"], {"MaRES": "MaRES_1"})
        self.assertEqual(toys.single_universe("GEANT_Pion_0")["detector"], {"GEANT_Pion": 0})
        for bad in ("Rvp1pi_0", "Flux_100", "MaRES_2"):
            with self.assertRaises(toys.Refusal):
                toys.single_universe(bad)
        self.assertEqual(len(toys.s1_universes()), 175)


# --------------------------------------------------------------------------------------- the universe set and pins


class Universes(WorldCase):
    def test_interaction_groups_drop_rvp1pi_and_are_s1s_set(self):
        g = toys.interaction_groups(self.world.bank)
        self.assertNotIn("Rvp1pi", g)
        self.assertEqual(sorted(g), sorted(toys.INTERACTION_BANDS))
        self.assertEqual(len(g), 33)
        self.assertEqual(g, fs.declared_groups())  # the scorer re-derives draws from the same groups
        bad = self.out / "bank"
        shutil.copytree(self.world.bank, bad)
        for p in bad.glob("MaRES_1_*"):
            p.unlink()
        with self.assertRaises(toys.Refusal):
            toys.interaction_groups(bad)

    def test_the_flux_probabilities_are_the_constraint_weights_over_their_sum(self):
        p = toys.flux_probabilities(self.world.constraint)
        np.testing.assert_allclose(p, self.world.flux_w / self.world.flux_w.sum(), rtol=1e-15)
        self.assertGreater(p.max() / p.min(), 2.0)  # not uniform

    def test_flux_ids_must_be_0_to_99(self):
        self.assertEqual(toys.flux_ids(self.world.bank), list(range(100)))
        bad = self.out / "bank"
        shutil.copytree(self.world.bank, bad)
        (bad / "Flux_42_wr.npy").unlink()
        with self.assertRaises(toys.Refusal):
            toys.flux_ids(bad)

    def test_pins_pass_the_recorded_files_and_refuse_a_wrong_or_changed_one(self):
        pins = json.loads(self.world.pins.read_text())
        toys.check_pins(pins, self.world.bank, self.world.det)
        self.assertEqual(len(pins["files"]), 1 + 4 * 175)
        bad = self.out / "m.txt"
        lines = self.world.manifest.read_text().splitlines()
        lines[3] = "0" * 64 + lines[3][64:]
        bad.write_text("\n".join(lines) + "\n")
        with self.assertRaises(toys.Refusal):
            toys.make_pins(self.world.bank, self.world.det, bad, self.world.receipt)
        p = Path(next(iter(pins["files"])))
        st = p.stat()
        try:
            os.utime(p, ns=(st.st_atime_ns, st.st_mtime_ns + 1_000_000_000))
            with self.assertRaises(toys.Refusal):
                toys.check_pins(pins, self.world.bank, self.world.det)
        finally:
            os.utime(p, ns=(st.st_atime_ns, st.st_mtime_ns))
        short = dict(pins, files=dict(list(pins["files"].items())[1:]))
        with self.assertRaises(toys.Refusal):
            toys.check_pins(short, self.world.bank, self.world.det)

    def test_the_truth_ratio_must_carry_the_committed_digest(self):
        ratio, sha = toys.truth_ratio("genie_v3_g18", self.world.prep)
        self.assertEqual(ratio["schema"], "s5e-shape-ratio/1")
        self.assertEqual(toys.truth_ratio("nominal", None), (None, None))
        other = self.out / "prep"
        shutil.copytree(self.world.prep, other)
        (other / "bridged/genie_v3_g18.json").write_text(json.dumps(dict(ratio, shape_ratio=[1.3, 0.9])))
        with self.assertRaises(toys.Refusal):
            toys.truth_ratio("genie_v3_g18", other)
        with self.assertRaises(toys.Refusal):
            toys.truth_ratio("genie_v3_ar23", None)


# ------------------------------------------------------------------------------------------------- source factors


class Factors(WorldCase):
    def full_draw(self):
        p = toys.flux_probabilities(self.world.constraint)
        return toys.draw_for_seed(2_610_003, p, toys.interaction_groups(self.world.bank))

    def test_factors_are_s5p_nullexps_for_a_full_draw(self):
        inputs, bkg = self.loaded()
        d = self.full_draw()
        src = np.random.default_rng(1).uniform(size=inputs["w_reco"].size) < 0.5
        fs1, fb1, _ = toys.source_factors(d, inputs, bkg, self.world.bank, self.world.det, src, None)
        fs2, fb2 = ne.source_factors(dict(d), inputs, bkg, self.world.bank, self.world.det, src, None)
        np.testing.assert_array_equal(fs1, fs2)
        np.testing.assert_array_equal(fb1, fb2)

    def test_the_interaction_factor_keeps_the_source_truth_in_every_fine_cell(self):
        inputs, bkg = self.loaded()
        d = {"flux": None, "model": {"MaRES": "MaRES_1"}, "detector": {}}
        src = np.ones(inputs["w_reco"].size, bool)
        fsig, _, _ = toys.source_factors(d, inputs, bkg, self.world.bank, self.world.det, src, None)
        k = np.load(self.world.bank / "MaRES_1_wr.npy") / inputs["w_reco"]
        self.assertGreater(np.abs(fsig / k - 1).max(), 1e-3)  # g_f acts: not the bare reco ratio

    def test_a_detector_band_comes_from_the_dump_only(self):
        inputs, bkg = self.loaded()
        det = self.out / "det"
        shutil.copytree(self.world.det, det)
        for p in det.glob("GEANT_Pion_1_*"):
            p.unlink()
        d = {"flux": None, "model": {}, "detector": {"GEANT_Pion": 1}}
        self.assertTrue((self.world.bank / "GEANT_Pion_1_wr.npy").exists())  # the bank's copy is not a fallback
        with self.assertRaises(toys.Refusal):
            toys.source_factors(d, inputs, bkg, self.world.bank, det, np.ones(inputs["w_reco"].size, bool), None)


# ---------------------------------------------------------------------------------------------- the experiments


class Experiments(WorldCase):
    def test_the_expectation_is_the_mean_and_the_truth_is_all_of_the_mc(self):
        inputs, bkg = self.loaded()
        n = inputs["w_reco"].size
        r = np.random.default_rng(2).uniform(0.8, 1.2, n)
        fsig = np.random.default_rng(3).uniform(0.9, 1.1, n)
        fb = np.random.default_rng(4).uniform(0.9, 1.1, bkg["bkg_w"].size)
        exp, xt, info = toys.build_full(inputs, bkg, r, fsig, fb, None, expectation=True)
        reco = inputs["pass_reco"]
        lam = np.concatenate([(inputs["w_reco"] * r * fsig)[reco], bkg["bkg_w"] * fb])
        obs = np.concatenate([inputs["MCreco"][reco], bkg["bkg_reco"]])
        keep = s5n_pseudo.fid_mask(obs, EDGES) & (lam > 0)
        np.testing.assert_array_equal(exp["obs_counts"], lam[keep])
        data = s5n_pseudo.build_data(inputs, bkg)
        for k in ("MCgen", "MCreco", "w_truth", "w_reco", "tmpl", "tmpl_w"):
            np.testing.assert_array_equal(exp[k], data[k])
        from xsec_nd import extract_cross_section_nd
        sel = inputs["pass_truth"]
        unf = np.histogramdd(inputs["MCgen"][sel], bins=EDGES, weights=(inputs["w_truth"] * r)[sel])[0]
        ofin = np.histogramdd(inputs["MCgen"][sel], bins=EDGES, weights=inputs["w_truth"][sel])[0]
        want, _ = extract_cross_section_nd(unf, ofin / inputs["denom_nd"], inputs["flux"], float(inputs["data_pot"]),
                                           float(inputs["n_nucleons"]), EDGES)
        np.testing.assert_allclose(xt, want, rtol=1e-13)
        self.assertTrue(info["expectation"])

    def test_the_truth_does_not_move_with_the_draw(self):
        inputs, bkg = self.loaded()
        n, nb = inputs["w_reco"].size, bkg["bkg_w"].size
        r = np.ones(n)
        _, x0, _ = toys.build_full(inputs, bkg, r, np.ones(n), np.ones(nb), 11, False)
        _, x1, _ = toys.build_full(inputs, bkg, r, np.random.default_rng(1).uniform(0.5, 1.5, n), np.ones(nb) * 2, 11, False)
        np.testing.assert_array_equal(x0, x1)

    def test_the_streams_are_set_as_and_leave_the_observed_counts(self):
        inputs, bkg = self.loaded()
        n, nb = inputs["w_reco"].size, bkg["bkg_w"].size
        exp, _, _ = toys.build_full(inputs, bkg, np.ones(n), np.ones(n), np.ones(nb), 21, False)
        rep = toys.mc_template_streams(exp, 2_610_000)
        ref = s5n_pseudo.bootstrap_replica(exp, 2_610_000)
        for k in ("w_truth", "w_reco", "tmpl_w"):
            np.testing.assert_array_equal(rep[k], ref[k])
        np.testing.assert_array_equal(rep["obs_counts"], exp["obs_counts"])
        self.assertFalse(np.array_equal(ref["obs_counts"], exp["obs_counts"]))
        self.assertFalse(np.array_equal(rep["w_truth"], exp["w_truth"]))

    def test_half_mode_applies_the_draw_to_the_source_halves_only(self):
        inputs, bkg = self.loaded()
        seen = {}
        orig = s5n_pseudo.build_pseudo

        def spy(ui, ub, *a, **k):
            seen["ui"], seen["ub"] = ui, ub
            return orig(ui, ub, *a, **k)

        d = {"flux": 5, "model": {}, "detector": {"GEANT_Pion": 1}}
        with mock.patch.object(s5n_pseudo, "build_pseudo", spy):
            toys.experiment("half", d, 2_600_001, inputs, bkg, "nominal", None, self.world.bank, self.world.det, None)
        split = s5c_pseudo.split_key_for(2_600_001)
        is_b = s5c_pseudo.half_mask(inputs["w_reco"].size, split)
        is_c = s5c_pseudo.half_mask(bkg["bkg_w"].size, s5n_pseudo.bkg_split_key(split))
        np.testing.assert_array_equal(seen["ui"]["w_reco"][~is_b], inputs["w_reco"][~is_b])
        np.testing.assert_array_equal(seen["ub"]["bkg_w"][~is_c], bkg["bkg_w"][~is_c])
        self.assertFalse(np.array_equal(seen["ui"]["w_reco"][is_b], inputs["w_reco"][is_b]))


# ------------------------------------------------------------------------------------------- F1c's line, bitwise


class F1cReproduction(WorldCase):
    def test_every_draw_off_reproduces_f1cs_experiment_and_product(self):
        runs = self.out / "f1c"
        rows = fd_f1_tasks.steps(self.world.sums, str(self.world.prep), str(runs))
        row = next(r for r in rows if r[1] == "f1_pe_genie_v3_g18_s806000")
        self.assertEqual(row[2], "s5e_candidate.py")
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("SLURM_CPUS_PER_TASK", None)
            self.assertEqual(s5e_candidate.main(row[3:]), 0)
            theirs_calls = list(CALLS)
            CALLS.clear()
            self.assertEqual(toys.main(self.world.run_argv("repro-g18", "half", self.out / "ours", seeds="806000:806000",
                                                           no_draws=True)), 0)
        ours, theirs = CALLS[0], theirs_calls[0]
        self.assertEqual(ours["args"], theirs["args"])
        self.assertEqual(ours["args"][:3], (42, 32, 5))
        self.assertEqual(sorted(ours["exp"]), sorted(theirs["exp"]))
        for k, v in theirs["exp"].items():
            if k == "edges":
                continue
            np.testing.assert_array_equal(np.asarray(ours["exp"][k]), np.asarray(v), err_msg=k)
        a = np.load(self.out / "ours" / "t_s806000.npz")
        b = np.load(runs / "pe/genie_v3_g18/ratio_nd_a1_s806000.npz")
        self.assertTrue(np.array_equal(a["xsec_flat"], b["xsec_flat"]) and a["xsec_flat"].dtype == b["xsec_flat"].dtype)
        np.testing.assert_array_equal(a["xtrue_flat"], b["xtrue_flat"])
        sums = self.out / "f1c-sums"
        sums.write_text(f"{digest(runs / 'pe/genie_v3_g18/ratio_nd_a1_s806000.npz')}  ./pe/genie_v3_g18/ratio_nd_a1_s806000.npz\n")
        argv = ["repro", "--pair", f"{self.out / 'ours/t_s806000.npz'}={runs / 'pe/genie_v3_g18/ratio_nd_a1_s806000.npz'}",
                "--f1c-sums", str(sums), "--f1c-runs", str(runs), "--out", str(self.out / "repro.json")]
        with mock.patch("sys.stdout"):
            self.assertEqual(fs.main(argv), 0)
        self.assertEqual(json.loads((self.out / "repro.json").read_text())["verdict"], "PASS")
        theirs_other = runs / "pe/genie_v3_g18/ratio_nd_a1_s806001.npz"
        sums.write_text(sums.read_text() + f"{digest(theirs_other)}  ./pe/genie_v3_g18/ratio_nd_a1_s806001.npz\n")
        argv2 = ["repro", "--pair", f"{self.out / 'ours/t_s806000.npz'}={theirs_other}", "--f1c-sums", str(sums),
                 "--f1c-runs", str(runs), "--out", str(self.out / "repro2.json")]
        with mock.patch("sys.stdout"):
            self.assertEqual(fs.main(argv2), 1)
        self.assertEqual(json.loads((self.out / "repro2.json").read_text())["verdict"], "FAIL")


# ------------------------------------------------------------------------------------------------- the toy runs


class ToyRuns(WorldCase):
    def test_a_control_toy_records_the_declared_estimator_draw_and_streams(self):
        with mock.patch("sys.stdout"):
            self.assertEqual(toys.main(self.world.run_argv("control", "toy", self.out, seeds="2610000:2610001")), 0)
        p = toys.flux_probabilities(self.world.constraint)
        g = toys.interaction_groups(self.world.bank)
        for s in (2_610_000, 2_610_001):
            m = sa.check_meta(self.out / f"t_s{s}.npz", toys.SCHEMA,
                              expect={"arm": "control", "mode": "toy", "pseudo_seed": s, "truth": "nominal"})
            self.assertEqual(m["draw"], json.loads(json.dumps(toys.draw_for_seed(s, p, g))))
            self.assertEqual(m["experiment"]["stream_replica"], s)
            self.assertFalse(m["experiment"]["expectation"])
        e0, e1 = CALLS[0]["exp"], CALLS[1]["exp"]
        inputs, _ = self.loaded()
        self.assertEqual(e0["MCgen"].shape[0], inputs["MCgen"].shape[0])  # all of the MC unfolds
        self.assertFalse(np.array_equal(e0["w_truth"], inputs["w_truth"]))  # with set A's MC stream
        x0, x1 = (np.load(self.out / f"t_s{s}.npz")["xtrue_flat"] for s in (2_610_000, 2_610_001))
        np.testing.assert_array_equal(x0, x1)
        X, xt, draws = fs.load_toys(self.out, "t", "control", [2_610_000, 2_610_001], np.eye(x0.size), p)
        np.testing.assert_array_equal(xt, x0)  # the toy mode's own products pass the scorer's read-back

    def test_runs_refuse_what_the_declaration_does_not_allow(self):
        w = self.world
        bad = [w.run_argv("control", "toy", self.out, seeds="2610299:2610300"),
               w.run_argv("control", "toy", self.out, seeds="2609999:2610000"),
               w.run_argv("control", "toy", self.out, seeds="2610000:2610000", no_draws=True),
               w.run_argv("repro-g18", "half", self.out, seeds="806000:806000"),
               w.run_argv("control", "half", self.out, seeds="2610000:2610000"),
               w.run_argv("derivation", "derivation", self.out, seeds="1:1"),
               w.run_argv("control", "toy", self.out, seeds="2610000:2610000", pins_sha="0" * 64)]
        with mock.patch("sys.stderr"):
            for argv in bad:
                self.assertEqual(toys.main(argv), 4, argv)
            wrong = w.run_argv("control", "toy", self.out, seeds="2610000:2610000")
            wrong[wrong.index("--expect-npz-sha256") + 1] = "f" * 64
            self.assertEqual(toys.main(wrong), 4)
        self.assertEqual(list(self.out.glob("*.npz")), [])

    def test_a_derivation_run_is_noise_free_with_one_universe(self):
        with mock.patch("sys.stdout"):
            self.assertEqual(toys.main(self.world.run_argv("derivation", "derivation", self.out,
                                                           universes="CV,Flux_3,MaRES_1,GEANT_Pion_0")), 0)
        for tag in ("CV", "Flux_3", "MaRES_1", "GEANT_Pion_0"):
            m = sa.check_meta(self.out / f"t_{tag}.npz", toys.SCHEMA, expect={"arm": "derivation", "universe": tag})
            self.assertEqual(m["draw"], json.loads(json.dumps(toys.single_universe(tag))))
            self.assertTrue(m["experiment"]["expectation"])
        cv = CALLS[0]["exp"]
        inputs, _ = self.loaded()
        np.testing.assert_array_equal(cv["w_truth"], inputs["w_truth"])  # no stream


# ------------------------------------------------------------------------------------------------------ the scorer


def synthetic(seed=0, rho=0.2):
    """A 16-cell world: truth x_t, data f != x_t, and a drawn matrix M_d on f with weak correlations."""
    rng = np.random.default_rng(seed)
    x_t = rng.uniform(1.0, 3.0, 16)
    f = x_t * rng.uniform(0.9, 1.2, 16)
    sd = 0.1 * f
    C = rho ** np.abs(np.subtract.outer(np.arange(16), np.arange(16)))
    return x_t, f, C * np.outer(sd, sd)


def gaussian_toys(x_t, f, M_d, scatter, n=300, seed=1, bias=None):
    Mt = fs.transfer(M_d, f, x_t)
    L = np.linalg.cholesky(Mt)
    z = np.random.default_rng(seed).normal(size=(n, 16))
    return x_t + (bias if bias is not None else 0) + scatter * z @ L.T


class Coverage(unittest.TestCase):
    def test_the_control_passes_matched_scatter_and_fails_both_ways(self):
        x_t, f, M = synthetic()
        r = fs.score_control(gaussian_toys(x_t, f, M, 1.0), x_t, f, M, "final")
        self.assertEqual(r["verdict"], "PASS")
        self.assertTrue(r["positive_control"]["passes"])
        self.assertEqual(r["scaled"]["0.7"]["verdict"], "FAIL-undercoverage")
        self.assertEqual(r["scaled"]["1.3"]["verdict"], "FAIL-overcoverage")
        self.assertEqual(fs.score_control(gaussian_toys(x_t, f, M, 1.4), x_t, f, M, "final")["verdict"],
                         "FAIL-undercoverage")
        self.assertEqual(fs.score_control(gaussian_toys(x_t, f, M, 0.7), x_t, f, M, "final")["verdict"],
                         "FAIL-overcoverage")

    def test_a_pass_is_void_when_the_positive_control_fails(self):
        x_t, f, M = synthetic()
        with mock.patch.object(fs.vl, "positive_control", return_value={"passes": False}):
            r = fs.score_control(gaussian_toys(x_t, f, M, 1.0), x_t, f, M, "final")
        self.assertEqual(r["verdict"], "INCONCLUSIVE")

    def test_the_interim_look_stops_only_on_a_fail(self):
        x_t, f, M = synthetic()
        self.assertEqual(fs.score_control(gaussian_toys(x_t, f, M, 1.0, n=100), x_t, f, M, "interim")["verdict"], "CONTINUE")
        r = fs.score_control(gaussian_toys(x_t, f, M, 1.6, n=100), x_t, f, M, "interim")
        self.assertEqual(r["verdict"], "FAIL-undercoverage")
        self.assertEqual(r["base"]["level"], 0.995)

    def test_a_test_arm_is_one_sided(self):
        x_t, f, M = synthetic()
        r = fs.score_test_arm(gaussian_toys(x_t, f, M, 1.0), x_t, f, M, M, "final")
        self.assertEqual(r["verdict"], "PASS")
        self.assertIn("no undercoverage detected at the study's sensitivity", r["meaning"])
        self.assertEqual(fs.score_test_arm(gaussian_toys(x_t, f, M, 1.4), x_t, f, M, M, "final")["verdict"], "FAIL")
        wide = fs.score_test_arm(gaussian_toys(x_t, f, M, 1.0), x_t, f, 4 * M, M, "final")
        self.assertEqual((wide["one_sided"], wide["one_sided_0.7"], wide["verdict"]), ("PASS", "PASS", "INCONCLUSIVE"))
        self.assertEqual(fs.one_sided({"C1": [0.60, 0.69], "C2": [0.95, 0.96]}), "PASS")
        self.assertEqual(fs.one_sided({"C1": [0.60, 0.68], "C2": [0.95, 0.96]}), "FAIL")
        self.assertEqual(fs.one_sided({"C1": [0.70, 0.75], "C2": [0.90, 0.954]}), "FAIL")

    def test_a_test_arms_interim_look_stops_only_on_a_fail(self):
        x_t, f, M = synthetic()
        self.assertEqual(fs.score_test_arm(gaussian_toys(x_t, f, M, 1.0, n=100), x_t, f, M, M, "interim")["verdict"],
                         "CONTINUE")
        self.assertEqual(fs.score_test_arm(gaussian_toys(x_t, f, M, 1.6, n=100), x_t, f, M, M, "interim")["verdict"],
                         "FAIL")

    def test_a_flagged_cell_is_reported_on_a_pass(self):
        x_t, f, M = synthetic()
        X = gaussian_toys(x_t, f, M, 1.0)
        X[:, 5] = x_t[5] + (X[:, 5] - x_t[5]) * 1.8
        r = fs.score_test_arm(X, x_t, f, M, M, "final")
        self.assertIn("R05", r["flagged_cells"]["c1"])
        self.assertEqual(len(r["per_cell"]["c1_wilson95"]), 16)

    def test_wilson_flags_at_the_declared_counts(self):
        n = 300
        self.assertLess(fs.wilson(182, n, fs.FLAG_LEVEL)[1], fs.NOMINAL[1])
        self.assertGreaterEqual(fs.wilson(183, n, fs.FLAG_LEVEL)[1], fs.NOMINAL[1])
        self.assertLess(fs.wilson(276, n, fs.FLAG_LEVEL)[1], fs.NOMINAL[2])
        self.assertGreaterEqual(fs.wilson(277, n, fs.FLAG_LEVEL)[1], fs.NOMINAL[2])
        x_t = np.ones(16)
        X = np.ones((n, 16))
        X[:118, 0] = 2.5  # 182 of 300 inside |z| <= 1 in cell 0
        pc = fs.per_cell(X, x_t, np.ones(16))
        self.assertEqual(pc["c1"][0], 182 / 300)
        self.assertTrue(pc["c1_flag_measured_undercoverage"][0])
        self.assertAlmostEqual(pc["c1_se"][0], math.sqrt(182 / 300 * 118 / 300 / 300))

    def test_4a_passes_a_matched_matrix_fails_a_small_one_and_refuses_a_singular_one(self):
        x_t, f, M = synthetic()
        a = fs.four_a(gaussian_toys(x_t, f, M, 1.0), x_t, f, M, M, "control")
        self.assertEqual((a["gates"], a["graded"]["verdict"]), ("nothing", "PASS"))
        self.assertEqual(fs.four_a(gaussian_toys(x_t, f, M, 1.3), x_t, f, M, M, "control")["graded"]["verdict"],
                         "FAIL-undercoverage")
        self.assertEqual(fs.four_a(gaussian_toys(x_t, f, M, 0.8), x_t, f, M, M, "control")["graded"]["verdict"],
                         "FAIL-overcoverage")
        v = np.ones(16)
        with self.assertRaises(fs.Invalid):
            fs.chi2_values(np.zeros((3, 16)), np.zeros(16), np.outer(v, v))

    def test_4a_at_a_test_arm_grades_about_the_toy_mean(self):
        x_t, f, M = synthetic()
        bias = np.zeros(16)
        bias[3] = 3 * math.sqrt(fs.transfer(M, f, x_t)[3, 3])
        X = gaussian_toys(x_t, f, M, 1.0, bias=bias)
        a = fs.four_a(X, x_t, f, M, 2 * M, "g18")
        self.assertIsNone(a["mean_subtracted_no_verdict"]["verdict"])  # binding ruling 4: graded at the control only
        self.assertEqual(a["mean_subtracted_no_verdict"]["classification"], {"mean": "inside", "tail": "inside"})
        self.assertGreater(a["about_truth_no_verdict"]["M_d"]["mean"], 20)
        Mt = fs.transfer(M, f, x_t)
        c = X - X.mean(axis=0)
        want = np.einsum("ij,jk,ik->i", c, np.linalg.inv(Mt), c) * 300 / 299
        self.assertAlmostEqual(a["mean_subtracted_no_verdict"]["mean"], float(want.mean()), places=9)
        v = np.ones(16)
        self.assertIn("refused", fs.four_a(X, x_t, f, np.outer(v, v), M, "control"))

    def test_the_surrogates_are_carried_to_the_truth(self):
        x_t, f, _ = synthetic()
        rng = np.random.default_rng(9)
        deltas = {b: rng.normal(size=16) * 0.05 * f for b in sa.LATERAL_BANDS}
        combos = []
        for bits in range(32):
            s = {b: (1 if (bits >> i) & 1 else -1) for i, b in enumerate(sa.LATERAL_BANDS)}
            combos.append({"lateral_s": s, "normalization_z": 0.0})
        Y = fs.surrogate(np.tile(x_t, (32, 1)), combos, deltas, f, x_t) - x_t
        want = sum(fs.transfer(0.25 * np.outer(d, d), f, x_t) for d in deltas.values())
        np.testing.assert_allclose(Y.T @ Y / 32, want, rtol=1e-10, atol=1e-14)
        one = fs.surrogate(x_t[None, :], [{"lateral_s": {b: 1 for b in sa.LATERAL_BANDS}, "normalization_z": 2.0}],
                           {b: np.zeros(16) for b in sa.LATERAL_BANDS}, f, x_t)
        np.testing.assert_allclose(one[0], x_t * 1.028)

    def test_the_drawn_matrix_leaves_out_the_seed_block(self):
        b = {"stat": np.eye(2), "seed": 5 * np.eye(2), "band:Flux": 2 * np.eye(2), "normalization": np.eye(2)}
        np.testing.assert_array_equal(fs.drawn_matrix({"blocks": b}), 4 * np.eye(2))


# ----------------------------------------------------------------------------------------- toy products, read back


def toy_meta(arm, seed, draw, mode="toy", **extra):
    m = {"schema": toys.SCHEMA, "arm": arm, "mode": mode, "pseudo_seed": seed, "no_draws": False, "draw": draw,
         "config": "R", "capacity": None, "iters": 5, "estimator_seed": 42,
         "estimator_params": [{"n_estimators": 100, "num_leaves": 8, "random_state": 42}] * 3,
         "refinement": {"classifier_params": {"n_estimators": 400, "num_leaves": 31, "random_state": 45}},
         "input_npz_sha256": sa.INPUT_NPZ_SHA256, "bkg_dump_sha256": sa.BKG_SHA256,
         "truth": toys.ARMS[arm][0], "truth_ratio_sha256": toys.committed_ratio_sha256(toys.ARMS[arm][0]),
         "numpy_version": np.__version__, "code_sha256": {"fd_1b_toys.py": "c" * 64}}
    m.update(extra)
    return m


def write_toys(d: Path, arm, seeds, X, x_t, flux_p, tamper=None, meta_extra=None):
    d.mkdir(parents=True, exist_ok=True)
    g = fs.declared_groups()
    for k, s in enumerate(seeds):
        draw = json.loads(json.dumps(toys.draw_for_seed(s, flux_p, g)))
        xt = x_t
        if tamper == ("draw", k):
            draw["flux"] = (draw["flux"] + 1) % 100
        if tamper == ("truth", k):
            xt = x_t * (1 + 1e-12)
        if tamper == ("inf-truth", None):  # every toy the same infinite truth: inf == inf, so only the finite check
            xt = x_t.copy()                # can refuse it (a NaN never equals itself and trips the agreement check)
            xt[3] = np.inf
        extra = meta_extra if tamper == ("meta", k) else {}
        np.savez_compressed(d / f"t_s{s}.npz", xsec_flat=X[k], xtrue_flat=xt, meta=json.dumps(toy_meta(arm, s, draw, **extra)))


class ReadBack(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fd1b-rb-"))
        self.p = np.full(100, 0.01)
        self.x_t, self.f, self.M = synthetic()
        self.seeds = list(range(2_610_000, 2_610_100))
        self.X = gaussian_toys(self.x_t, self.f, self.M, 1.0, n=100)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_valid_toys_read_back(self):
        write_toys(self.tmp, "control", self.seeds, self.X, self.x_t, self.p)
        X, xt, draws = fs.load_toys(self.tmp, "t", "control", self.seeds, np.eye(16), self.p)
        np.testing.assert_array_equal(X, self.X)
        np.testing.assert_array_equal(xt, self.x_t)

    def test_a_departing_draw_a_departing_truth_or_a_wrong_arm_is_invalid(self):
        for tamper in (("draw", 7), ("truth", 50)):
            d = self.tmp / str(tamper)
            write_toys(d, "control", self.seeds, self.X, self.x_t, self.p, tamper)
            with self.assertRaises(fs.Invalid):
                fs.load_toys(d, "t", "control", self.seeds, np.eye(16), self.p)
        d = self.tmp / "arm"
        write_toys(d, "g18", self.seeds, self.X, self.x_t, self.p)
        with self.assertRaises(fs.Invalid):
            fs.load_toys(d, "t", "control", self.seeds, np.eye(16), self.p)

    def test_a_wrong_truth_name_or_digest_differing_code_or_an_infinite_truth_is_invalid(self):
        cases = [(("meta", 10), {"truth": "genie_v3_g18"}), (("meta", 11), {"truth_ratio_sha256": "e" * 64}),
                 (("meta", 12), {"code_sha256": {"fd_1b_toys.py": "d" * 64}}), (("inf-truth", None), None)]
        for k, (tamper, extra) in enumerate(cases):
            d = self.tmp / f"c{k}"
            write_toys(d, "control", self.seeds, self.X, self.x_t, self.p, tamper, extra)
            with self.assertRaises(fs.Invalid, msg=str(tamper)):
                fs.load_toys(d, "t", "control", self.seeds, np.eye(16), self.p)

    def test_a_scorer_under_another_numpy_refuses_rather_than_grading(self):
        write_toys(self.tmp, "control", self.seeds, self.X, self.x_t, self.p)
        with mock.patch.object(fs.np, "__version__", "0.0.0"), self.assertRaisesRegex(SystemExit, "numpy"):
            fs.load_toys(self.tmp, "t", "control", self.seeds, np.eye(16), self.p)

    def test_a_4a_refusal_leaves_the_coverage_verdict_standing(self):
        seeds = list(range(2_610_000, 2_610_300))
        X = gaussian_toys(self.x_t, self.f, self.M, 1.0)
        write_toys(self.tmp / "toys", "control", seeds, X, self.x_t, self.p)
        sd = np.sqrt(np.diag(self.M))
        singular = np.outer(sd, sd)  # the same diagonal, rank 1: coverage reads it, 4A cannot invert it
        s1 = {"f": self.f, "U": np.eye(16), "blocks": {"stat": self.M, "seed": np.zeros((16, 16))}, "C_e": self.M}
        out = self.tmp / "final.json"
        argv = ["score", "--arm", "control", "--look", "final", "--toys", str(self.tmp / "toys"), "--tag", "t",
                "--s1-npz", "x", "--flux-constraint", "x", "--lateral-dir", "x", "--definition", "x", "--inputs-npz", "x",
                "--x01", "x", "--manifest", "x", "--out", str(out)]
        deltas = {b: np.zeros(16) for b in sa.LATERAL_BANDS}
        with mock.patch.object(fs, "_common_inputs", return_value=(s1, singular, self.M, deltas, self.p)), \
                mock.patch("sys.stdout"):
            rc = fs.main(argv)
        r = json.loads(out.read_text())
        self.assertIn("not positive definite", r["4A"]["refused"])
        self.assertEqual(r["verdict"], r["coverage"]["verdict"])
        self.assertNotEqual(r["verdict"], "INVALID")
        self.assertEqual(rc, 0 if r["verdict"] == "PASS" else 1)

    def test_a_missing_toy_is_insufficient_and_a_partial_is_invalid(self):
        write_toys(self.tmp, "control", self.seeds, self.X, self.x_t, self.p)
        (self.tmp / "t_s2610042.npz").unlink()
        with self.assertRaises(fs.Insufficient):
            fs.load_toys(self.tmp, "t", "control", self.seeds, np.eye(16), self.p)
        (self.tmp / "t_s2610042.npz.partial-1.npz").write_bytes(b"")
        with self.assertRaises(fs.Invalid):
            fs.load_toys(self.tmp, "t", "control", self.seeds, np.eye(16), self.p)

    def test_the_score_readout_names_the_matrix_and_prints_no_cross_section(self):
        write_toys(self.tmp / "toys", "control", self.seeds, self.X, self.x_t, self.p)
        blocks = {"stat": self.M * 0.5, "lat:BeamAngleX": self.M * 0.2, "normalization": self.M * 0.3,
                  "seed": np.zeros((16, 16))}
        s1 = {"f": self.f, "U": np.eye(16), "blocks": blocks, "C_e": self.M}
        deltas = {b: np.zeros(16) for b in sa.LATERAL_BANDS}
        out = self.tmp / "readout.json"
        argv = ["score", "--arm", "control", "--look", "interim", "--toys", str(self.tmp / "toys"), "--tag", "t",
                "--s1-npz", "x", "--flux-constraint", "x", "--lateral-dir", "x", "--definition", "x", "--inputs-npz", "x",
                "--x01", "x", "--manifest", "x", "--out", str(out)]
        with mock.patch.object(fs, "_common_inputs", return_value=(s1, self.M, self.M, deltas, self.p)), \
                mock.patch("sys.stdout"):
            self.assertEqual(fs.main(argv), 0)
            with mock.patch("sys.stderr"):
                self.assertEqual(fs.main(argv), 4)  # never over an existing readout
        r = json.loads(out.read_text())
        self.assertEqual((r["label"], r["verdict"], r["matrix_tested"]), ("RESULT", "CONTINUE", fs.MATRIX_TESTED))
        self.assertIn("no run-period block", r["matrix_tested"])
        self.assertIn("50.0% of C_e's trace", r["surrogates"])
        text = out.read_text()
        for v in np.concatenate([self.f, self.x_t, self.X[0]]):
            self.assertNotIn(repr(float(v)), text)


# ------------------------------------------------------------------------------------------------------- gate D


class GateD(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fd1b-gd-"))
        rng = np.random.default_rng(12)
        self.f = rng.uniform(1.0, 3.0, 16)
        self.x_cv = self.f * rng.uniform(0.85, 0.95, 16)
        self.x_t = self.x_cv * rng.uniform(0.95, 1.05, 16)  # the noise-free unfold is not the truth
        self.w = rng.uniform(0.5, 4.0, 100)
        self.constraint = self.tmp / "c.txt"
        self.constraint.write_text("".join(f"Flux {i} {self.w[i]!r}\n" for i in range(100)))
        self.x = {"CV": self.x_cv}
        for b in sorted(sa.EXPECT):
            for i in range(sa.EXPECT[b]):
                self.x[f"{b}_{i}"] = self.x_cv * (1 + rng.normal(0, 0.03, 16))
        d = self.tmp / "der"
        d.mkdir()
        for tag, v in self.x.items():
            m = toy_meta("derivation", None, json.loads(json.dumps(toys.single_universe(tag))), mode="derivation",
                         universe=tag)
            np.savez_compressed(d / f"t_{tag}.npz", xsec_flat=v, xtrue_flat=self.x_t, meta=json.dumps(m))
        self.der = d

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def s1_npz(self, interaction_scale=1.0):
        g = self.f / self.x_t  # the control's carry: sigma_c^T = sqrt(M_cc) / f_c x_T,c
        blocks = {"stat": np.diag((0.01 * self.f) ** 2), "normalization": np.outer(0.014 * self.f, 0.014 * self.f),
                  "seed": np.diag((0.001 * self.f) ** 2)}
        for b in sa.LATERAL_BANDS:
            blocks[f"lat:{b}"] = np.diag((0.02 * self.f) ** 2)
        for b in sorted(sa.EXPECT):
            X = np.array([self.x[f"{b}_{i}"] for i in range(sa.EXPECT[b])])
            C = sa.mat_cov(X, self.w if b == sa.FLUX else None) * np.outer(g, g)
            blocks[f"band:{b}"] = C * (interaction_scale if sa.group_of(f"band:{b}") == "interaction" else 1.0)
        p = self.tmp / f"s1_{interaction_scale}.npz"
        np.savez_compressed(p, f=self.f, U=np.eye(16, dtype=np.float32), C_e=sum(blocks.values()),
                            **{"C_" + k.replace(":", "_"): v for k, v in blocks.items()},
                            meta=json.dumps({"blocks": sorted(blocks)}))
        return p

    def run_gate(self, s1, name):
        out = self.tmp / f"{name}.json"
        argv = ["gate-d", "--derivation", str(self.der), "--tag", "t", "--s1-npz", str(s1),
                "--flux-constraint", str(self.constraint), "--out", str(out)]
        with mock.patch.object(fs, "S1_NPZ_SHA256", digest(s1)), \
                mock.patch.object(sa, "CONSTRAINT_SHA256", digest(self.constraint)), mock.patch("sys.stdout"):
            rc = fs.main(argv)
        return rc, json.loads(out.read_text())

    def test_toys_that_carry_s1s_blocks_pass_exactly(self):
        rc, r = self.run_gate(self.s1_npz(), "pass")
        self.assertEqual((rc, r["verdict"], r["label"]), (0, "PASS", "DERIVATION"))
        np.testing.assert_allclose(r["rho"], 1.0, rtol=1e-9)
        for grp in ("flux", "interaction", "detector"):
            np.testing.assert_allclose(r["per_group_sigma_ratio"][grp], 1.0, rtol=1e-9)

    def test_a_prior_part_s1_holds_and_the_toys_lack_is_a_stop(self):
        rc, r = self.run_gate(self.s1_npz(interaction_scale=4.0), "fail")
        self.assertEqual((rc, r["verdict"]), (1, "FAIL"))
        self.assertIn("STOP before any coverage toy", r["stop"])
        self.assertLess(min(r["rho"]), 0.9)

    def test_a_missing_or_wrong_derivation_product_stops(self):
        s1 = self.s1_npz()
        (self.der / "t_MaRES_1.npz").unlink()
        rc, r = self.run_gate(s1, "missing")
        self.assertEqual((rc, r["verdict"]), (1, "INSUFFICIENT"))
        m = toy_meta("derivation", None, json.loads(json.dumps(toys.single_universe("MaRES_0"))), mode="derivation",
                     universe="MaRES_1")
        np.savez_compressed(self.der / "t_MaRES_1.npz", xsec_flat=self.x_cv, xtrue_flat=self.x_t, meta=json.dumps(m))
        rc, r = self.run_gate(s1, "wrong")
        self.assertEqual((rc, r["verdict"]), (1, "INVALID"))
        m = toy_meta("derivation", None, json.loads(json.dumps(toys.single_universe("MaRES_1"))), mode="derivation",
                     universe="MaRES_1")
        np.savez_compressed(self.der / "t_MaRES_1.npz", xsec_flat=self.x_cv, xtrue_flat=self.x_cv, meta=json.dumps(m))
        rc, r = self.run_gate(s1, "truth")
        self.assertEqual((rc, r["verdict"]), (1, "INVALID"))


# ------------------------------------------------------------------------------------------------- the task tables


DEP = ft.P + "/fd-1b-20261030/deploy/abcdef12"


class Tasks(unittest.TestCase):
    def test_a_deploy_off_pscratch_is_refused(self):
        for bad in ("/global/cfs/cdirs/m3246/deploy", "/D", "/pscratch/sd/j/josephrbX/deploy"):
            with self.assertRaises(SystemExit):
                ft.submit_lines("2b", bad, "abc")
            with tempfile.TemporaryDirectory() as d, self.assertRaises(SystemExit):
                ft.main(["tables", "--job", "2b", "--deploy", bad, "--pins-sha256", "a" * 64, "--out-dir", d])

    def test_the_jobs_are_the_declarations_table(self):
        text = flat(DECL.read_text())
        want = {"2a": (202, 3, 9, "3.0 h", "9.00"), "2b": (100, 2, 7, "2.5 h", "5.00"), "2c": (200, 3, 9, "3.0 h", "9.00"),
                "3i": (200, 3, 9, "3.0 h", "9.00"), "3f": (400, 5, 10, "3.5 h", "17.50")}
        for job, (n, nodes, most, limit, cap) in want.items():
            spec = ft.JOBS[job]
            self.assertEqual((len(ft.expand(job)), spec["nodes"], spec["most_per_lane"]), (n, nodes, most))
            self.assertEqual(f"{ft.hours(spec['limit']):.1f} h", limit)
            self.assertEqual(f"{ft.cap(job):.2f}", cap)
            self.assertIn(f"| {job} | {n} | {nodes} | {most} |", text)
            self.assertIn(f"| {limit} | {cap} |", text)
            self.assertEqual(max(len(c) for c in ft.chunks(ft.expand(job), nodes * 8)), most)
        self.assertEqual(sum(ft.cap(j) for j in ft.JOBS), 49.5)
        self.assertEqual({s: sum(ft.cap(j) for j in ft.JOBS if j.startswith(s)) for s in "23"}, {"2": 23.0, "3": 26.5})

    def test_every_declared_toy_and_universe_runs_exactly_once(self):
        got: dict = {}
        for job in ft.JOBS:
            for arm, mode, x in ft.expand(job):
                got.setdefault((arm, mode), []).append(x)
        for arm in ("control", "g18", "ar23"):
            lo, hi = toys.ARMS[arm][1:]
            self.assertEqual(got[(arm, "toy")], list(range(lo, hi + 1)))
        self.assertEqual(got[("pilot", "toy")], list(range(2_600_000, 2_600_016)))
        self.assertEqual(got[("pilot", "half")], list(range(2_600_000, 2_600_008)))
        self.assertEqual(got[("derivation", "derivation")], ["CV"] + toys.s1_universes())
        self.assertEqual((got[("repro-g18", "half")], got[("repro-ar23", "half")]), ([806_000], [807_000]))

    def test_every_step_parses_as_a_declared_toy_run(self):
        seen = []
        with mock.patch.object(toys, "run", side_effect=lambda a, **k: seen.append(a) or 0):
            for job in ft.JOBS:
                for row in ft.steps(job, "a" * 64):
                    self.assertEqual(row[2], "fd_1b_toys.py")
                    self.assertEqual(toys.main(row[3:]), 0)
        for a in seen:
            self.assertIn(a.mode, toys.MODES[a.arm])
            if a.seeds:
                toys.parse_seeds(a.seeds, a.arm)
            self.assertEqual((a.threads, a.expect_pins_sha256), (32, "a" * 64))
            self.assertEqual(a.prep is not None, toys.TRUTHS[toys.ARMS[a.arm][0]] is not None)
            self.assertEqual(a.no_draws, a.arm.startswith("repro"))

    def test_submit_lines_are_regular_cpu_under_12_h_through_the_committed_packer(self):
        packer = (REPO / ft.PACKER_REL).read_text()
        self.assertIn("#SBATCH --exclusive", packer)
        self.assertIn("#SBATCH --no-requeue", packer)
        self.assertIn("#SBATCH --nodes=1", packer)
        for job in ft.JOBS:
            lines = ft.submit_lines(job, DEP, "abc")
            self.assertEqual(len(lines), ft.JOBS[job]["nodes"])
            for n, line in enumerate(lines):
                t = line.split()
                opt = dict(zip(t[1:9:2], t[2:10:2]))
                self.assertEqual(opt, {"-A": "m3246", "-q": "regular", "-C": "cpu", "-t": ft.JOBS[job]["limit"]})
                self.assertLess(ft.hours(opt["-t"]), 12)
                self.assertEqual(t[13], DEP + "/" + ft.PACKER_REL)
                self.assertEqual(t[-5:], ["32", "56G", str(8 * n), str(8 * n + 7), "inherit"])
                self.assertNotIn("premium", line)
                self.assertFalse([x for x in t if x.startswith(("--gpu", "--gres", "-G"))], line)

    def test_a_limit_of_12_h_or_more_is_refused_by_itself(self):
        # one node, with the declared cap and the stage ceiling moved to match, so only the 12 h rule can refuse
        for limit, h in (("12:00:00", 12.0), ("13:00:00", 13.0)):
            with mock.patch.dict(ft.JOBS, {"2b": dict(ft.JOBS["2b"], nodes=1, limit=limit)}), \
                    mock.patch.dict(ft.DECLARED_CAPS, {"2b": h}), mock.patch.dict(ft.STAGE_CEILINGS, {"2": 100.0}), \
                    self.assertRaisesRegex(SystemExit, "not under 12"):
                ft.submit_lines("2b", DEP, "abc")
        with mock.patch.dict(ft.JOBS, {"2b": dict(ft.JOBS["2b"], nodes=1, limit="11:59:00")}), \
                mock.patch.dict(ft.DECLARED_CAPS, {"2b": 11 + 59 / 60}), mock.patch.dict(ft.STAGE_CEILINGS, {"2": 100.0}):
            self.assertEqual(len(ft.submit_lines("2b", DEP, "abc")), 1)

    def test_a_cap_off_the_declared_one_or_over_the_stage_ceiling_is_refused(self):
        # 2 nodes x 2.0 h = 4.0 != 5.0, and stage 2 stays under 23.0: only the cap rule can refuse
        with mock.patch.dict(ft.JOBS, {"2b": dict(ft.JOBS["2b"], limit="02:00:00")}), \
                self.assertRaisesRegex(SystemExit, "declared"):
            ft.submit_lines("2b", DEP, "abc")
        # 3 nodes x 2.5 h = 7.5 declared, but stage 2 is then 25.5 > 23.0: only the ceiling can refuse
        with mock.patch.dict(ft.JOBS, {"2b": dict(ft.JOBS["2b"], nodes=3)}), mock.patch.dict(ft.DECLARED_CAPS, {"2b": 7.5}), \
                self.assertRaisesRegex(SystemExit, "ceiling"):
            ft.submit_lines("2b", DEP, "abc")
        with mock.patch.dict(ft.JOBS, {"2b": dict(ft.JOBS["2b"], most_per_lane=6)}), self.assertRaises(SystemExit):
            ft.steps("2b", "a" * 64)

    def test_tables_write_once(self):
        with tempfile.TemporaryDirectory() as d:
            with mock.patch("sys.stdout"):
                self.assertEqual(ft.main(["tables", "--job", "2b", "--deploy", DEP, "--pins-sha256", "a" * 64,
                                          "--out-dir", d]), 0)
            lanes = (Path(d) / "tasks-fd1b-2b.tsv").read_text().splitlines()
            self.assertEqual(len([x for x in lanes if not x.startswith("#")]), 16)
            with self.assertRaises(SystemExit):
                ft.main(["tables", "--job", "2b", "--deploy", DEP, "--pins-sha256", "a" * 64, "--out-dir", d])


if __name__ == "__main__":
    unittest.main()
