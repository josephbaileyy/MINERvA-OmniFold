"""LL5D amendment A1a (ll5d.py): the REQUIRED tests of LL5D-DECLARATION.md section 12 that A1a carries, the minus2
gate's m2-a to m2-g (936-C1 and the audit's lows), and the all-path equality with A2.1's gate path at 342c0ce5 (the
director's ruling on A1). Every rule is tested in the direction it acts and the other.

    python3 -B nd-unfolding/tests/test_ll5d.py
"""
from __future__ import annotations

import argparse
import builtins
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest import mock

import numpy as np

ND = Path(__file__).resolve().parents[1]
REPO = ND.parent
sys.path.insert(1, str(ND))
sys.path.insert(1, str(Path(__file__).resolve().parent))

import fd_1b_c2 as c2  # noqa: E402
import fd_1b_inv as inv  # noqa: E402
import fd_1b_mc as mc  # noqa: E402
import fd_1b_score as fs  # noqa: E402
import fd_1b_toys as toys  # noqa: E402
import ll5d  # noqa: E402
import s1_assemble as sa  # noqa: E402
import s5c_unfold  # noqa: E402
import s5p_universe  # noqa: E402
from test_fd_1b import World as ToyWorld, digest  # noqa: E402

VENDORED_MC = ND / "tests" / "data" / "fd_1b_mc_at_342c0ce5.py.txt"
VENDORED_MC_SHA256 = "062628b69976f730d9d394e64ecf6f93d9952654306471ac0119542c6b07dd67"   # 342c0ce5:nd-unfolding/fd_1b_mc.py
VENDORED_MC_BLOB = "e77fe6ba3c97dd3a5330bb004685a15f6136da8f"
RUNNER = ND / "tests" / "ll5d_a21_reference.py"
ONES = {k: "1" for k in ll5d.THREAD_VARS}


SEED_PATTERN = r"(?<![0-9A-Za-z.,])(47[5-7][0-9]{4}|4,7[5-7][0-9],[0-9]{3}|4_7[5-7][0-9]_[0-9]{3})(?![0-9A-Za-z]|,[0-9])"
_RCPT = "docs/orchestration/state/measurement-paper/5d-community-20261024/"
OWN_SEED_FILES = ("nd-unfolding/ll5d.py", "nd-unfolding/tests/test_ll5d.py", "nd-unfolding/tests/ll5d_a1a_mutation.py",
                  _RCPT + "LL5D-DECLARATION.md", _RCPT + "LL5D-AMENDMENT-A1A.md") + tuple(
    _RCPT + "fd/receipts-ll5d/a1a/" + f for f in ("tests-numpy126-seed0.txt", "tests-numpy126-seed1.txt",
                                                    "tests-numpy126-seed2.txt", "tests-numpy2-seed0.txt"))


OWN_RECEIPT_PREFIX = _RCPT + "fd/receipts-ll5d/"     # LL5D's own receipt tree (the director, 2026-11-09)


def seed_collisions(lines: list[str]) -> list[str]:
    """git grep -n -o lines (path:line:token) whose token is an integer in section 3.6's range, outside LL5D's own
    files (OWN_SEED_FILES, exact paths) and LL5D's own receipt tree (OWN_RECEIPT_PREFIX, an exact path prefix: its
    receipts name LL5D's own products, which are not collisions); a token ending in a decimal fraction is a float
    literal, not a seed."""
    bad = []
    for line in lines:
        path, _, tok = line.split(":", 2)
        if path in OWN_SEED_FILES or path.startswith(OWN_RECEIPT_PREFIX) or re.search(r"\.[0-9]$", tok):
            continue
        if 4_751_000 <= int(re.sub(r"[,_]", "", tok)) <= 4_770_999:
            bad.append(line)
    return bad


def law_control_computed(tc: unittest.TestCase, law: dict) -> None:
    """The law control was computed for every evaluation and cell (finite z, a boolean verdict). Whether it holds on
    a toy null of a few dozen sets is chance: 64 z-values at 4 SE from 20-40 sets fail about 2-5 % of worlds by the t
    distribution (PYTHONHASHSEED=17 showed it). The rule itself is fd_1b_c2.control, verbatim from 342c0ce5."""
    tc.assertIsInstance(law["holds"], bool)
    for e in ll5d.EVALUATIONS:
        z = np.asarray(law[e]["z"], float)
        tc.assertEqual(z.shape, (sa.N_CELLS,))
        tc.assertTrue(np.all(np.isfinite(z)), e)


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def plain():
    return mock.patch.object(inv, "NOATIME_FLAG", 0)


def consistent(tag: str, w: dict, cv_denom: np.ndarray, tdw_ref: np.ndarray) -> dict:
    """The fixture's weights as the real bank's behave (A2.1's test fixture rule, about tdw_ref): a detector universe's
    denom_nd is the CV's bitwise; a bank universe's tdw is tdw_ref within 2 % row by row, crc32-seeded in the tag (the
    real tdw_ref is the CV-equal per-row weight the universes vary about, section 3.4)."""
    rng = np.random.default_rng(zlib.crc32(tag.encode()))
    if "denom_nd" in w:
        w = dict(w, denom_nd=np.asarray(cv_denom, float))
    if "tdw" in w:
        w = dict(w, tdw=np.asarray(tdw_ref, float) * rng.uniform(0.98, 1.02, np.shape(w["tdw"])))
    return w


class Fixture(unittest.TestCase):
    """A2.1's toy world (test_fd_1b.World), with the bank's six GEANT tdw set to one tdw_ref and listed in their own
    manifest, the npz's denom_nd hist(tdw_ref), and every universe's weights made consistent."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="ll5d-"))
        cls.w = ToyWorld(cls.tmp)
        cls.inputs = s5c_unfold.load_inputs(cls.w.inputs)
        bz = np.load(cls.w.bkg, allow_pickle=True)
        cls.bkg = {"bkg_reco": bz["bkg_reco"], "bkg_w": bz["bkg_w"], "bkg_nd": bz["bkg_nd"]}
        z = dict(np.load(cls.w.bank / "cv.npz", allow_pickle=True))
        rng = np.random.default_rng(3)
        for k, e in zip(("td_pt", "td_pz", "td_ea", "td_q3", "td_w"), cls.inputs["edges"]):
            z[k] = rng.uniform(e[0], e[-1], 50)
        cls.bank_cv = z
        cls.flux = np.random.default_rng(4).uniform(0.9, 1.1, (100, 2)) * np.asarray(cls.inputs["flux"], float)
        cls.tdw_ref = np.random.default_rng(5).uniform(0.95, 1.05, 50)
        cls.inputs["denom_nd"] = s5p_universe.denominator(cls.bank_cv, cls.tdw_ref, cls.inputs["edges"])
        for tag in ll5d.GEANT_BANK_TAGS:
            np.save(cls.w.bank / f"{tag}_tdw.npy", cls.tdw_ref)
        cls.ref_sha = digest(cls.w.bank / f"{ll5d.TDW_REF_TAG}_tdw.npy")
        cls.manifest = cls.tmp / "ll5d-manifest.txt"
        cls.write_manifest()
        with plain():
            cls.weights = {t: consistent(t, inv.universe_weights(mc.universe_dir(t, cls.w.bank, cls.w.det), t, "zero"),
                                         cls.inputs["denom_nd"], cls.tdw_ref) for t in toys.s1_universes()}
        cls.groups = toys.interaction_groups(cls.w.bank)
        n = cls.inputs["w_truth"].shape[0]
        cls.r = {t: np.random.default_rng(len(t) + 7).uniform(0.8, 1.2, n) for t in ll5d.TRUTHS}
        n_bins = int(np.prod([np.asarray(e).size - 1 for e in cls.inputs["edges"]]))
        cells = ll5d.flat_cells(np.asarray(cls.inputs["MCgen"], float), cls.inputs["edges"])
        live = np.unique(cells[(cells >= 0) & np.asarray(cls.inputs["pass_truth"], bool)])
        fm = np.full(n_bins, -1)
        fm[live] = np.arange(live.size) % sa.N_CELLS
        cls.fm = fm
        cls.U = np.vstack([np.where(fm == c, 1.0 + 0.1 * c, 0.0) for c in range(sa.N_CELLS)])
        cls.flux_p = np.random.default_rng(6).uniform(0.5, 1.5, 100)
        cls.flux_p /= cls.flux_p.sum()
        cls.s1 = {"U": cls.U.astype(np.float32), "f": np.linspace(1.0, 2.0, sa.N_CELLS)}
        cls.reported = np.diag((0.05 * cls.s1["f"]) ** 2)
        cls.pins = json.loads(cls.w.pins.read_text())

    @classmethod
    def write_manifest(cls):
        cls.manifest.write_text("".join(f"{digest(cls.w.bank / f'{t}_tdw.npy')}  {cls.w.bank / f'{t}_tdw.npy'}\n"
                                        for t in ll5d.GEANT_BANK_TAGS))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def setUp(self):
        self.ps = self.w.patches() + [plain(), mock.patch.object(ll5d, "TDW_REF_SHA256", self.ref_sha),
                                      mock.patch.dict(os.environ, ONES),
                                      mock.patch.object(fs, "reported_matrix", lambda s1: self.reported)]
        for p in self.ps:
            p.start()

    def tearDown(self):
        for p in reversed(self.ps):
            p.stop()

    def world(self) -> dict:
        return {"inputs": self.inputs, "bkg": self.bkg, "bank_cv": self.bank_cv, "flux": self.flux,
                "groups": self.groups, "pins": self.pins, "npz_sha": "n", "bkg_sha": "b", "tdw_ref": self.tdw_ref,
                "tdw_cv": self.tdw_ref}

    def load(self, tag):
        return self.weights[tag], self.weights[tag]

    def prepared(self, rows=True, truths=ll5d.TRUTHS):
        return ll5d.prepare(self.world(), self.load, {t: self.r[t] for t in truths}, self.flux_p, self.U, rows=rows)

    def draws(self, truth="g18", n=6):
        return [mc.draw_universes(toys.draw_for_seed(int(s), self.flux_p, self.groups))
                for s in list(ll5d.TOY_SEEDS[truth])[:n]]

    def args(self, **kw):
        base = dict(npz=self.w.inputs, bkg=self.w.bkg, bank=self.w.bank, detector_dir=self.w.det, pins=self.w.pins,
                    flux_constraint=self.w.constraint, flux_table=None, definition=self.tmp / "definition.json",
                    prep=self.tmp, manifest=self.manifest, expect_pins_sha256=digest(self.w.pins),
                    expect_flux_table_sha256=None, expect_manifest_sha256=digest(self.manifest),
                    time_limit_seconds=1e7)
        base.update(kw)
        return argparse.Namespace(**base)

    def job_patches(self):
        def via(reader, path):
            if reader is toys.flux_probabilities:
                return self.flux_p
            if reader is fs.load_s1:
                return self.s1
            raise AssertionError(f"unexpected read {path}")
        return [mock.patch.object(mc, "_load_world", lambda a: self.world()),
                mock.patch.object(ll5d, "verified_weights", lambda world, a, tag: self.load(tag)),
                mock.patch.object(mc, "truth_ratio", lambda t, p: (None, None)),
                mock.patch.object(mc, "truth_weight", lambda t, inputs, ratio, push: self.r[t]),
                mock.patch.object(mc, "via_noatime", via), mock.patch.object(sa, "fine_map", lambda p: self.fm),
                mock.patch.object(sa, "functional_matrix", lambda fm: self.U),
                mock.patch.object(fs, "reported_matrix", lambda s1: self.reported)]


# ------------------------------------------------------------------------------------------------- provenance


class Provenance(unittest.TestCase):
    def test_fd_1b_c2_is_342c0ce5s_bytes(self):
        data = Path(c2.__file__).read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), ll5d.FD_1B_C2_SOURCE["sha256"])
        self.assertEqual(git_blob(data), ll5d.FD_1B_C2_SOURCE["blob"])
        self.assertEqual(ll5d.FD_1B_C2_SOURCE["branch"], "decl/1b-staged-a2-1-20261103")

    def test_the_vendored_fd_1b_mc_is_342c0ce5s_bytes(self):
        data = VENDORED_MC.read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), VENDORED_MC_SHA256)
        self.assertEqual(git_blob(data), VENDORED_MC_BLOB)

    def test_the_drivers_are_not_called(self):
        src = Path(ll5d.__file__).read_text()
        for name in ("c2.prepare(", "c2.fine_sums(", "c2.c2_inputs(", "c2.calibrate_main(", "c2.c2check_main(",
                     "c2.layout_1b() if", "source_factors"):
            self.assertNotIn(name, src)


# ---------------------------------------------------------------------------------------------- m2-a, m2-b


class Layouts(unittest.TestCase):
    def test_m2a_minus2_is_s1s_layout_less_exactly_two_bands(self):
        self.assertEqual(ll5d.REMOVED, ("GEANT_Neutron", "GEANT_Proton"))
        order, bands, tags = c2.layout_1b()
        o2, b2, t2 = ll5d.layout_minus2()
        self.assertEqual(set(order) - set(o2), {"GEANT_Neutron", "GEANT_Proton"})
        self.assertEqual(set(order) - set(o2), set(ll5d.REMOVED))
        self.assertEqual(list(o2), [b for b in order if b not in ll5d.REMOVED])
        self.assertEqual(b2, {b: n for b, n in bands.items() if b not in ll5d.REMOVED})
        self.assertEqual(t2, [t for t in tags if t.rpartition("_")[0] not in ll5d.REMOVED])
        self.assertEqual(len(tags) - len(t2), 4)
        self.assertIn("GEANT_Pion", b2)
        self.assertIn("MinosEfficiency", b2)
        self.assertEqual(ll5d.layout("all"), c2.layout_1b())
        with self.assertRaises(ll5d.Refusal):
            ll5d.layout("half")

    def test_drop2_keeps_the_order_and_every_other_universe(self):
        d = ["Flux_3", "MaRES_1", "MinosEfficiency_0", "GEANT_Neutron_1", "GEANT_Pion_0", "GEANT_Proton_0"]
        self.assertEqual(ll5d.drop2(d), ["Flux_3", "MaRES_1", "MinosEfficiency_0", "GEANT_Pion_0"])


class Selection(Fixture):
    def test_m2b_selection_accepts_drop2_and_refuses_a_kept_band(self):
        draws = self.draws(n=8)
        _, _, tags = ll5d.layout("all")
        col = {u: i for i, u in enumerate(tags)}
        S_all = ll5d.selection(draws, "all", col)
        S_m2 = ll5d.selection(draws, "minus2", col)
        removed = [col[t] for t in tags if t.rpartition("_")[0] in ll5d.REMOVED]
        self.assertTrue(np.all(S_m2[:, removed] == 0))
        keep = [i for i in range(len(tags)) if i not in removed]
        np.testing.assert_array_equal(S_m2[:, keep], S_all[:, keep])
        self.assertTrue(np.all(S_all[:, removed].sum(axis=1) == 2))
        v = ll5d.restrict(self.prepared(rows=False), "minus2")
        S_c = ll5d.selection(draws, "minus2", v["col"])
        np.testing.assert_array_equal(S_c, S_all[:, v["rows_of_all"]])
        _, b2, _ = ll5d.layout_minus2()
        for kept in ("GEANT_Neutron", "GEANT_Proton"):
            bad = [[t for t in d if t.rpartition("_")[0] not in ll5d.REMOVED or t.startswith(kept)] for d in draws]
            with self.assertRaises(c2.Refusal):
                c2.selection(bad, col, b2)


# ------------------------------------------------------------------------------- composition, m2-c, the clip


class Composition(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(17)
        self.nu, self.rows = 9, 400
        self.Vi = rng.integers(-50, 200, (self.nu, self.rows)).astype(float)
        self.refi = rng.integers(1, 150, self.rows).astype(float)
        self.Vf = rng.normal(1.0, 0.4, (self.nu, self.rows))
        self.reff = rng.normal(1.0, 0.1, self.rows)
        self.cols_all = [0, 2, 3, 5, 7, 8]
        self.gn, self.gp = 5, 7                       # the two removed bands' universes in this draw

    def test_k1_is_the_universe_bitwise(self):
        acc, peak = ll5d.compose_rows(self.Vf, self.reff, [4])
        prod = ll5d.product_rows(self.Vf, self.reff, [4], acc)
        np.testing.assert_array_equal(acc, self.Vf[4])
        np.testing.assert_array_equal(prod, self.Vf[4])
        np.testing.assert_array_equal(peak, np.abs(self.Vf[4]))
        self.assertFalse(np.shares_memory(acc, self.Vf))

    def test_first_order_in_draw_order(self):
        before = self.Vf.copy()
        acc, peak = ll5d.compose_rows(self.Vf, self.reff, self.cols_all)
        np.testing.assert_array_equal(self.Vf, before)          # the universes are read, never written
        want = self.Vf[0].copy()
        for c in self.cols_all[1:]:
            want += self.Vf[c] - self.reff
        np.testing.assert_array_equal(acc, want)
        np.testing.assert_array_equal(peak, np.max(np.abs(self.Vf[self.cols_all]), axis=0))

    def test_m2c_minus2_is_all_less_the_two_terms_before_the_clip(self):
        m2 = [c for c in self.cols_all if c not in (self.gn, self.gp)]
        a_all, _ = ll5d.compose_rows(self.Vi, self.refi, self.cols_all)
        a_m2, _ = ll5d.compose_rows(self.Vi, self.refi, m2)
        np.testing.assert_array_equal(a_m2, a_all - (self.Vi[self.gn] - self.refi) - (self.Vi[self.gp] - self.refi))
        f_all, _ = ll5d.compose_rows(self.Vf, self.reff, self.cols_all)
        f_m2, _ = ll5d.compose_rows(self.Vf, self.reff, m2)
        np.testing.assert_allclose(f_m2, f_all - (self.Vf[self.gn] - self.reff) - (self.Vf[self.gp] - self.reff),
                                   rtol=1e-12, atol=1e-12)

    def test_m2c_the_fine_sum_composites_too(self):
        rng = np.random.default_rng(3)
        H = {q: rng.integers(-20, 90, (self.nu, 30)).astype(float) for q in ("A", "B", "D")}
        cv = {q: rng.integers(1, 60, 30).astype(float) for q in ("A", "B", "D")}
        S_all = np.zeros((1, self.nu))
        S_all[0, self.cols_all] = 1.0
        S_m2 = S_all.copy()
        S_m2[0, [self.gn, self.gp]] = 0.0
        c_all, c_m2 = c2.composite_sums(S_all, H, cv), c2.composite_sums(S_m2, H, cv)
        for q in ("A", "B", "D"):
            np.testing.assert_array_equal(c_m2[q][0], c_all[q][0] - (H[q][self.gn] - cv[q]) - (H[q][self.gp] - cv[q]))

    def test_m2c_each_reading_is_clipped_on_its_own_composite(self):
        """A row where the all composite clips and the minus2 one does not, and one where the reverse holds: each
        reading's clipped value is max(its own composite, 0), never derived from the other after its clip."""
        V = np.array([[1.0, 1.0], [1.0, 1.0], [-5.0, 4.0], [1.0, 1.0]])
        ref = np.array([1.0, 1.0])
        cols_all, cols_m2 = [0, 1, 2, 3], [0, 1, 3]       # universe 2 is a removed band's
        a_all, _ = ll5d.compose_rows(V, ref, cols_all)
        a_m2, _ = ll5d.compose_rows(V, ref, cols_m2)
        np.testing.assert_array_equal(a_all, [-5.0, 4.0])
        np.testing.assert_array_equal(a_m2, [1.0, 1.0])
        geo = {"gen": np.array([0, 1]), "td": np.array([0, 1]), "shape": (2,)}
        const = {"n_nucleons": 1.0, "data_pot": 1.0, "edges": [np.array([0.0, 1.0, 2.0])]}
        r = np.ones(2)
        for comp_q, want_b in ((a_all, [0.0, 4.0]), (a_m2, [1.0, 1.0])):
            nt = ll5d.nature_truth({"wt": comp_q, "tdw": np.array([1.0, 1.0])}, r, geo, np.ones(2), const)
            np.testing.assert_array_equal(nt["B"], want_b)
        wrong = np.maximum(a_all, 0.0) - (V[2] - ref)                # the all composite's clip less the term
        self.assertFalse(np.array_equal(np.maximum(a_m2, 0.0), wrong))

    def test_the_product_composite_is_crossterms_rule(self):
        V = np.array([[2.0, 3.0, 1.0], [4.0, 6.0, 5.0], [0.5, 1.5, 2.0]])
        ref = np.array([2.0, 0.0, 1.0])
        acc, _ = ll5d.compose_rows(V, ref, [0, 1, 2])
        prod = ll5d.product_rows(V, ref, [0, 1, 2], acc)
        np.testing.assert_allclose(prod, [2.0 * (4.0 / 2.0) * (0.5 / 2.0), acc[1], 1.0 * 5.0 * 2.0], rtol=1e-15)


class Clip(unittest.TestCase):
    def geo(self, n=60, nf=8, seed=2):
        rng = np.random.default_rng(seed)
        return {"gen": rng.integers(-1, nf, n), "td": rng.integers(-1, nf, n), "shape": (nf,)}, rng

    def test_each_tree_is_clipped_on_its_own_composite_and_nowhere_else(self):
        geo, rng = self.geo()
        wt, tdw = rng.normal(0.2, 1.0, 60), rng.normal(0.2, 1.0, 60)
        r = rng.uniform(0.8, 1.2, 60)
        const = {"n_nucleons": 1.0, "data_pot": 1.0, "edges": [np.linspace(0, 8, 9)]}
        nt = ll5d.nature_truth({"wt": wt, "tdw": tdw}, r, geo, np.ones(8), const)
        np.testing.assert_array_equal(nt["B"], ll5d._bins(geo["gen"], np.maximum(wt, 0.0), 8))
        np.testing.assert_array_equal(nt["A"], ll5d._bins(geo["gen"], np.maximum(wt, 0.0) * r, 8))
        np.testing.assert_array_equal(nt["D"], ll5d._bins(geo["td"], np.maximum(tdw, 0.0), 8))
        np.testing.assert_array_equal(nt["m_wt"], ll5d._bins(geo["gen"], np.maximum(-wt, 0.0), 8))
        np.testing.assert_array_equal(nt["m_tdw"], ll5d._bins(geo["td"], np.maximum(-tdw, 0.0), 8))
        cross = ll5d._bins(geo["td"], np.where(wt < 0, 0.0, tdw), 8)        # a tree clipped on the other's sign
        self.assertFalse(np.array_equal(nt["D"], cross))

    def test_the_denominator_is_never_negative_under_adversarial_composites(self):
        for seed in range(20):
            geo, rng = self.geo(seed=seed)
            comp = {"wt": rng.normal(-1.0, 3.0, 60), "tdw": rng.normal(-1.0, 3.0, 60)}
            const = {"n_nucleons": 1.0, "data_pot": 1.0, "edges": [np.linspace(0, 8, 9)]}
            nt = ll5d.nature_truth(comp, np.ones(60), geo, np.ones(8), const)
            for k in ("A", "B", "D", "x"):
                self.assertTrue(np.all(nt[k] >= 0), k)
            self.assertTrue(np.all(np.isfinite(nt["x"])))

    def test_the_bins_are_histogramdds(self):
        rng = np.random.default_rng(9)
        edges = [np.array([0.0, 1.0, 2.0]), np.array([0.0, 0.5, 1.0, 2.0])]
        coords = np.column_stack([rng.uniform(-0.2, 2.2, 500), rng.uniform(-0.1, 2.1, 500)])
        coords[:5, 0] = 2.0                           # histogramdd's closed last edge
        w = rng.integers(1, 9, 500).astype(float)
        h, _ = np.histogramdd(coords, bins=edges, weights=w)
        np.testing.assert_array_equal(ll5d._bins(ll5d.flat_cells(coords, edges), w, h.size), h.ravel())


# ------------------------------------------------------------------------------------ the builders, m2-d, m2-g


class Builders(Fixture):
    def test_detector_rows_carry_tdw_ref_and_enter_with_zero_departure(self):
        P = self.prepared()
        for i, t in enumerate(P["tags"]):
            if t.rpartition("_")[0] in sa.DETECTOR_BANDS:
                np.testing.assert_array_equal(P["rows"]["tdw"][i], self.tdw_ref)
                np.testing.assert_array_equal(P["D_full"][i], P["d_ref"])
        cols = [P["col"][t] for t in self.draws(n=1)[0]]
        bank = [c for c in cols if P["tags"][c].rpartition("_")[0] not in sa.DETECTOR_BANDS]
        a_all, _ = ll5d.compose_rows(P["rows"]["tdw"], self.tdw_ref, cols)
        a_bank, _ = ll5d.compose_rows(P["rows"]["tdw"], self.tdw_ref, bank)
        np.testing.assert_array_equal(a_all, a_bank)

    def test_the_cv_denominator_is_hist_tdw_ref(self):
        P = self.prepared()
        np.testing.assert_array_equal(P["d_ref"], np.ravel(s5p_universe.denominator(self.bank_cv, self.tdw_ref,
                                                                                    self.inputs["edges"])))
        np.testing.assert_array_equal(P["D_cv_full"], P["d_ref"])

    def test_m2d_the_minus2_reference_is_all_less_the_two_bands_variances(self):
        P = self.prepared(rows=False)
        order, bands, tags = ll5d.layout("all")
        for t in ll5d.TRUTHS:
            X = P["single_x"][t]
            k, terms = 0, {}
            for b in order:
                n = bands[b]
                Xb = X[k:k + n]
                p = (self.flux_p / self.flux_p.sum()) if b == sa.FLUX else np.full(n, 1.0 / n)
                terms[b] = p @ (Xb - p @ Xb) ** 2
                k += n
            want = P["ref_x"][f"{t}/all"] - terms["GEANT_Neutron"] - terms["GEANT_Proton"]
            np.testing.assert_allclose(P["ref_x"][f"{t}/minus2"], want, rtol=1e-12)
            self.assertFalse(np.allclose(P["ref_x"][f"{t}/minus2"], P["ref_x"][f"{t}/all"], rtol=1e-12, atol=0))

    def test_m2g_restrict_copies_no_row_array_and_the_zero_columns_are_the_selected_form(self):
        P = self.prepared()
        ids = {k: id(v) for k, v in P["rows"].items()}
        v = ll5d.restrict(P, "minus2")
        self.assertEqual({k: id(x) for k, x in P["rows"].items()}, ids)
        self.assertFalse({"rows", "V", "wt", "wr", "bkgw", "tdw"} & set(v))
        s1 = self.s1
        rel, geo, V, cv = ll5d.c2_inputs(P, s1, self.fm)
        draws = self.draws(n=6)
        S_pad = ll5d.selection(draws, "minus2", P["col"])
        S_cmp = ll5d.selection(draws, "minus2", v["col"])
        idx = v["rows_of_all"]
        V_sel = {k: V[k][idx] for k in ("wt", "wr", "bkgw", "tdw", "D")}
        t = "g18"
        phi = c2.draw_flux(S_pad, P["flux_cols"], P["phi"])
        np.testing.assert_array_equal(phi, c2.draw_flux(S_cmp, v["flux_cols"], P["phi"]))
        q_pad = c2.c2_truth(V, cv, S_pad, self.r[t], geo, phi, P["const"])
        q_cmp = c2.c2_truth(V_sel, cv, S_cmp, self.r[t], geo, phi, P["const"])
        for k in q_pad:
            np.testing.assert_allclose(q_pad[k], q_cmp[k], rtol=1e-12, atol=0, err_msg=k)


# ------------------------------------------------------------------------------- the calibration, m2-e, the rule


class Calibration(Fixture):
    def state(self, n=300):
        P = self.prepared(rows=False)
        views = {rd: ll5d.restrict(P, rd) for rd in ll5d.READINGS}
        ll5d._worker_init({"views": views, "cv": P["cv"], "U": P["U"], "ref_x": P["ref_x"],
                           "ref_count": P["ref_count"], "phi": P["phi"], "const": P["const"], "flux_p": self.flux_p,
                           "groups": self.groups, "n": n})
        return P, views

    def test_m2e_each_minus2_replicate_is_the_all_replicates_draws_less_two(self):
        P, views = self.state()
        seen = []
        real = c2.set_ratios

        def spy(S, *a):
            seen.append(S.copy())
            return real(S, *a)
        with mock.patch.object(c2, "set_ratios", spy):
            t, s, out = ll5d.one_set(("g18", 3))
        draws = ll5d.calibration_draws("g18", 3, self.flux_p, self.groups, 300)
        S_m2, S_m2_300, S_all, S_all_300 = seen
        np.testing.assert_array_equal(S_m2, ll5d.selection(draws, "minus2", views["minus2"]["col"]))
        np.testing.assert_array_equal(S_all, ll5d.selection(draws, "all", views["all"]["col"]))
        np.testing.assert_array_equal(S_m2_300, S_m2[:300])
        np.testing.assert_array_equal(S_all[:, views["minus2"]["rows_of_all"]], S_m2)
        self.assertEqual(set(out), set(ll5d.READINGS))
        for rx, rl, r3 in out.values():
            self.assertEqual(rx.shape, (sa.N_CELLS,))
            self.assertTrue(np.all(np.isfinite(rl)))

    def test_the_calibration_streams_are_disjoint_and_fixed(self):
        a = ll5d.calibration_draws("g18", 0, self.flux_p, self.groups, 30)
        self.assertEqual(a, ll5d.calibration_draws("g18", 0, self.flux_p, self.groups, 30))
        self.assertNotEqual(a, ll5d.calibration_draws("g18", 1, self.flux_p, self.groups, 30))
        self.assertNotEqual(a, ll5d.calibration_draws("ar23", 0, self.flux_p, self.groups, 30))
        two_word = [mc.draw_universes(toys.draw(np.random.default_rng([ll5d.CAL_SEED["g18"], 0]), self.flux_p,
                                                self.groups))]
        self.assertNotEqual(a[:1], two_word)


class Rule(unittest.TestCase):
    def null(self, sets=4000, sd=0.03, seed=1):
        rng = np.random.default_rng(seed)
        return {e: rng.normal(1.0, sd, (sets, sa.N_CELLS)) for e in ll5d.EVALUATIONS}

    def test_the_rule_is_over_exactly_the_four_paired_evaluations(self):
        R = self.null(sets=200)
        with self.assertRaises(ll5d.Refusal):
            ll5d.threshold_rule({e: R[e] for e in ll5d.EVALUATIONS[:3]})
        bad = dict(R)
        bad["ar23/all"] = R["ar23/all"][:100]
        with self.assertRaises(ll5d.Refusal):
            ll5d.threshold_rule(bad)

    def test_the_union_is_measured_jointly_per_replicate(self):
        R = self.null(sets=4000)
        rule = ll5d.threshold_rule(R)
        self.assertTrue(rule["measured_jointly"])
        self.assertIsNotNone(rule["s"])
        st = {e: c2.null_stats(R[e]) for e in ll5d.EVALUATIONS}
        for g in rule["grid"]:
            stops = [c2.stops_at(st[e], g["s"], st[e]["sd_ml"], st[e]["sd_c"]) for e in ll5d.EVALUATIONS]
            self.assertAlmostEqual(g["union"], float(np.mean(np.any(stops, axis=0))), places=15)
        k = [g["s"] for g in rule["grid"]].index(rule["s"])
        self.assertLessEqual(rule["grid"][k]["union"], c2.UNION_LIMIT)
        if k:
            self.assertGreater(rule["grid"][k - 1]["union"], c2.UNION_LIMIT)
        thr = rule["thresholds"]["ar23/minus2"]
        self.assertAlmostEqual(thr["ii_mean_log"], rule["s"] * c2.SD_MULT_LOGMEAN * st["ar23/minus2"]["sd_ml"])
        self.assertEqual(thr["iii_alpha_multiple"], rule["s"] * c2.SD_MULT_CELL)

    def test_paired_evaluations_cost_less_budget_than_independent_ones(self):
        R = self.null(sets=4000)
        same = {e: R["g18/minus2"] for e in ll5d.EVALUATIONS}       # fully paired: the union is one evaluation's
        s_same, s_ind = ll5d.threshold_rule(same)["s"], ll5d.threshold_rule(R)["s"]
        self.assertLess(s_same, s_ind)
        one = ll5d.threshold_rule(same)
        for g in one["grid"]:
            self.assertAlmostEqual(g["union"], g["per_evaluation"]["g18/minus2"], places=15)

    def test_i_alone_over_the_budget_is_flagged(self):
        R = self.null(sets=2000, sd=0.13)
        self.assertTrue(ll5d.threshold_rule(R)["i_alone_exceeds"])
        self.assertFalse(ll5d.threshold_rule(self.null(sets=2000))["i_alone_exceeds"])

    def test_power_and_the_verdict_run_on_evaluation_keys(self):
        R = self.null(sets=3000)
        rule = ll5d.threshold_rule(R)
        power = c2.power_at(R, rule)
        self.assertEqual(set(power) - {"meets"}, set(ll5d.EVALUATIONS))
        law = c2.control(R)
        self.assertIn(c2.calibration_verdict_n(law, c2.linearisation(R), rule, power),
                      ("CALIBRATED", "POWER_SHORT_TO_DIRECTOR", "CONTROL_FAILED"))


# --------------------------------------------------------------------------------------- D1-D3, N1, T <= 0


class Denominator(Fixture):
    def tearDown(self):
        super().tearDown()
        for tag in ll5d.GEANT_BANK_TAGS:
            np.save(self.w.bank / f"{tag}_tdw.npy", self.tdw_ref)
        self.write_manifest()

    def a(self):
        return self.args(expect_manifest_sha256=digest(self.manifest))

    def test_d1_passes_on_six_equal_arrays(self):
        ref, d1 = ll5d.load_tdw_ref(self.a())
        np.testing.assert_array_equal(ref, self.tdw_ref)
        self.assertTrue(d1["passes"])
        self.assertEqual(d1["tags"], list(ll5d.GEANT_BANK_TAGS))

    def test_d1_fires_on_one_ulp(self):
        x = self.tdw_ref.copy()
        x[17] = np.nextafter(x[17], np.inf)
        np.save(self.w.bank / "GEANT_Proton_1_tdw.npy", x)
        self.write_manifest()
        _, d1 = ll5d.load_tdw_ref(self.a())
        self.assertFalse(d1["passes"])
        self.assertEqual(d1["differ"], ["GEANT_Proton_1"])

    def test_tdw_ref_must_be_the_recorded_file(self):
        x = self.tdw_ref.copy()
        x[0] = np.nextafter(x[0], np.inf)
        np.save(self.w.bank / f"{ll5d.TDW_REF_TAG}_tdw.npy", x)
        with self.assertRaisesRegex(ll5d.Refusal, "not the recorded file"):
            ll5d.load_tdw_ref(self.a())
        self.write_manifest()
        with self.assertRaisesRegex(ll5d.Refusal, "not the declared tdw_ref"):
            ll5d.load_tdw_ref(self.a())

    def controls(self, denom=None, det=None):
        world = self.world()
        if denom is not None:
            world = dict(world, inputs=dict(self.inputs, denom_nd=denom))

        def load(tag):
            w = self.weights[tag]
            if det is not None and tag == det[0]:
                w = dict(w, denom_nd=det[1])
            return w, w
        return ll5d.denominator_controls(world, self.tdw_ref, {"passes": True}, load)

    def test_d2_and_d3_pass_on_the_fixture(self):
        c = self.controls()
        self.assertTrue(c["D2"]["passes"] and c["D3"]["passes"] and c["passes"])
        self.assertEqual(len(c["D3"]["universes"]), 8)

    def test_d2_at_its_cell_edge(self):
        """hist(tdw_ref) is the npz's denom_nd here; one npz cell moved so that dn / ref - 1 is f there, with the
        total kept by the largest cell (whose own deviation stays far below f)."""
        d = np.asarray(self.inputs["denom_nd"], float).ravel()
        pos = np.flatnonzero(d > 0)
        i, j = pos[np.argmin(d[pos])], pos[np.argmax(d[pos])]
        for f, ok in ((0.999e-3, True), (1.001e-3, False)):
            ref = d.copy()
            ref[i] = d[i] / (1.0 + f)
            ref[j] = d[j] + (d[i] - ref[i])
            c = self.controls(denom=ref.reshape(np.shape(self.inputs["denom_nd"])))
            self.assertAlmostEqual(c["D2"]["max_cell_rel_dev"], f, places=12)
            self.assertLess(c["D2"]["total_rel_dev"], 1e-12)
            self.assertEqual(c["D2"]["passes"], ok, f)

    def test_d2_at_its_total_edge(self):
        d = np.asarray(self.inputs["denom_nd"], float)
        for t, ok in ((0.9e-9, True), (1.1e-9, False)):
            c = self.controls(denom=d * (1.0 + t))
            self.assertEqual(c["D2"]["passes"], ok, t)
            self.assertLess(c["D2"]["max_cell_rel_dev"], 1e-8)

    def test_d2_fires_on_a_one_ulp_support_change(self):
        """The npz cell at the smallest positive float where hist(tdw_ref) is 0 (a support change of one ULP)."""
        d = np.asarray(self.inputs["denom_nd"], float).copy()
        z = np.flatnonzero(d.ravel() == 0)
        self.assertGreater(z.size, 0)
        d.flat[z[0]] = np.nextafter(0.0, 1.0)
        c = self.controls(denom=d)
        self.assertFalse(c["D2"]["same_support"])
        self.assertFalse(c["D2"]["passes"])

    def test_d2_fails_on_the_support_alone(self):
        """A denominator row reweighted to 1e-6, alone in its fine cell, and the npz's cell there 0 with that mass on its
        largest cell: the total and every cell where the npz is > 0 stay within their tolerances, so only the support
        can fail D2."""
        td = ll5d.td_cells(self.bank_cv, self.inputs["edges"])
        counts = np.bincount(td[td >= 0], minlength=self.U.shape[1])
        i = int(np.flatnonzero((td >= 0) & (counts[np.maximum(td, 0)] == 1))[0])
        ref_w = self.tdw_ref.copy()
        ref_w[i] = 1e-6
        dn = np.ravel(s5p_universe.denominator(self.bank_cv, ref_w, self.inputs["edges"]))
        npz = dn.copy()
        j = int(np.argmax(npz))
        npz[j] += npz[td[i]]
        npz[td[i]] = 0.0
        world = dict(self.world(), inputs=dict(self.inputs, denom_nd=npz.reshape(np.shape(self.inputs["denom_nd"]))))
        c = ll5d.denominator_controls(world, ref_w, {"passes": True}, self.load)
        self.assertFalse(c["D2"]["same_support"])
        self.assertLess(c["D2"]["max_cell_rel_dev"], ll5d.DENOM_CELL_TOL)
        self.assertLess(c["D2"]["total_rel_dev"], ll5d.DENOM_TOTAL_TOL)
        self.assertFalse(c["D2"]["passes"])

    def test_d3_fires_on_one_ulp(self):
        d = np.asarray(self.inputs["denom_nd"], float).copy()
        k = np.flatnonzero(d.ravel() > 0)[3]
        d.flat[k] = np.nextafter(d.flat[k], np.inf)
        c = self.controls(det=("GEANT_Pion_1", d))
        self.assertEqual(c["D3"]["differ"], ["GEANT_Pion_1"])
        self.assertFalse(c["passes"])


class N1(unittest.TestCase):
    def test_the_bound_is_strict(self):
        r = ll5d.n1_ratio(np.array([10.0, np.nextafter(10.0, np.inf), 0.0, 1.0]), np.array([1.0, 1.0, 0.0, 0.0]))
        self.assertEqual(r[0], 10.0)
        self.assertFalse(r[0] > ll5d.N1_BOUND)
        self.assertTrue(r[1] > ll5d.N1_BOUND)
        self.assertEqual(r[2], 1.0)
        self.assertEqual(r[3], np.inf)
        self.assertEqual(ll5d.N1_BOUND, 10.0)


class Receipt(Fixture):
    def run_receipt(self, V_edit=None, r=None, truth="g18", n=8, clock=None, phi=None):
        P = self.prepared(truths=[truth])
        rel, geo, V, cv = ll5d.c2_inputs(P, self.s1, self.fm)
        if V_edit:
            V = V_edit(dict(V), P, geo)
        draws = self.draws(truth, n)
        inputs = self.inputs
        const_full = {"n_nucleons": float(inputs["n_nucleons"]), "data_pot": float(inputs["data_pot"]),
                      "edges": inputs["edges"]}
        flux_map = {f"Flux_{i}": i for i in range(100)}
        rc, fine, seal = ll5d.receipt(V, cv, draws, P["col"], self.r[truth] if r is None else r,
                                P["phi"] if phi is None else phi, geo, self.U, P["d_ref"], const_full, flux_map,
                                list(ll5d.TOY_SEEDS[truth]), rel, clock)
        return rc, fine, P, geo, V, cv, draws, const_full, seal

    def test_a_clean_receipt_passes_and_records(self):
        rc, fine, P, geo, V, cv, draws, const_full, seal = self.run_receipt()
        self.assertEqual(rc["verdict"], "PASS")
        self.assertEqual(rc["natures_evaluated"], 2 * len(draws))
        self.assertEqual([p["reading"] for p in rc["per_nature"]], ["minus2"] * len(draws) + ["all"] * len(draws))
        for reading in ll5d.READINGS:
            self.assertEqual(rc["crossterm"][reading]["draws"], len(draws))
        self.assertEqual(fine["wt"].shape, (self.U.shape[1],))

    def test_each_reading_composes_its_own_draw_and_the_truth_takes_phi_u(self):
        rc, fine, P, geo, V, cv, draws, const_full, seal = self.run_receipt(n=3)
        refs = {"wt": cv["wt"], "wr": cv["wr"], "bkgw": cv["bkgw"], "tdw": cv["tdw"]}
        for row in rc["per_nature"]:
            tags = draws[row["draw"]] if row["reading"] == "all" else ll5d.drop2(draws[row["draw"]])
            cols = [P["col"][t] for t in tags]
            comp = {q: ll5d.compose_rows(V[q], refs[q], cols)[0] for q in ("wt", "tdw")}
            u = int(tags[0].rpartition("_")[2])
            nt = ll5d.nature_truth(comp, self.r["g18"], geo, P["phi"][u], const_full)
            T16 = seal[f"U_T_clipped_{row['reading']}"][row["draw"]]
            np.testing.assert_allclose(T16, self.U @ nt["x"], rtol=1e-12, atol=0)   # BLAS vs compose's order
            other = ll5d.nature_truth(comp, self.r["g18"], geo, np.asarray(self.inputs["flux"], float), const_full)
            self.assertFalse(np.allclose(T16, self.U @ other["x"], rtol=1e-6, atol=0))

    def test_the_clip_prep_products_equal_a_direct_computation(self):
        """REQUIRED (the director's ruling on the clipcheck inputs): per reading, the per-row sums of max(-lambda, 0)
        (signal on the reco-passing rows, background) and each draw's U T_D clipped and unclipped equal a direct
        computation: compose's order per draw, and the truths through s5n_pseudo.true_xsec (histogramdd and the
        extraction, an independent path) on the nature's arrays, clipped or not. Not bitwise: BLAS composites and two
        binnings, so 1e-10 relative."""
        rc, fine, P, geo, V, cv, draws, const_full, seal = self.run_receipt(n=5)
        import s5n_pseudo
        reco = geo["reco"] >= 0
        r = self.r["g18"]
        for rd in ll5d.READINGS:
            sig, bkg = np.zeros(V["wr"].shape[1]), np.zeros(V["bkgw"].shape[1])
            self.assertEqual(int(seal[f"draws_{rd}"]), len(draws))
            for d, tags in enumerate(ll5d.reading_draws(draws, rd)):
                cols = [P["col"][x] for x in tags]
                comp = {q: ll5d.compose_rows(V[q], np.asarray(cv[q], float), cols)[0] for q in ("wt", "wr", "bkgw", "tdw")}
                lam = comp["wr"] * r
                sig[reco] += np.maximum(-lam[reco], 0.0)
                bkg += np.maximum(-comp["bkgw"], 0.0)
                u = int(tags[0].rpartition("_")[2])
                for key, clip in (("U_T_clipped", True), ("U_T_unclipped", False)):
                    wt = np.maximum(comp["wt"], 0.0) if clip else comp["wt"]
                    tdw = np.maximum(comp["tdw"], 0.0) if clip else comp["tdw"]
                    ui = dict(self.inputs, w_truth=0.5 * wt, flux=P["phi"][u],
                              denom_nd=s5p_universe.denominator(self.bank_cv, tdw, self.inputs["edges"]))
                    x = s5n_pseudo.true_xsec(ui, np.ones(wt.size, bool), r)
                    np.testing.assert_allclose(seal[f"{key}_{rd}"][d], self.U @ np.ravel(x), rtol=1e-10, atol=0,
                                               err_msg=f"{key} {rd} {d}")
            np.testing.assert_allclose(seal[f"signal_negative_lambda_sum_{rd}"], sig, rtol=1e-10, atol=0)
            np.testing.assert_allclose(seal[f"background_negative_lambda_sum_{rd}"], bkg, rtol=1e-10, atol=0)
            self.assertGreater(float(seal[f"signal_negative_lambda_sum_{rd}"].sum()) +
                               float(seal[f"background_negative_lambda_sum_{rd}"].sum()) + 1.0, 0.0)
        self.assertNotIn("T16", json.dumps(rc))

    def test_t_le_0_stops_and_halts_at_the_first(self):
        """Every row of reporting cell c at 0.95 x the CV in every universe: each reading's composite there is
        -0.8 x CV (minus2, 36 universes) or -0.9 x CV (all, 38), within N1's bound, so the clip empties the cell and T
        <= 0 alone fires; with one row at the CV in every universe (its composite the CV's), T > 0 and it passes."""
        c = 5
        cells = np.where(np.asarray(self.inputs["pass_truth"], bool),
                         ll5d.flat_cells(np.asarray(self.inputs["MCgen"], float), self.inputs["edges"]), -1)
        rows_c = np.flatnonzero(np.isin(cells, np.flatnonzero(self.fm == c)))
        cv_wt = np.asarray(self.inputs["w_truth"], float)

        def kill(V, P, geo):
            V["wt"] = V["wt"].copy()
            V["wt"][:, rows_c] = 0.95 * cv_wt[rows_c]
            return V
        rc, *_, seal = self.run_receipt(V_edit=kill)
        self.assertEqual(rc["verdict"], "STOP")
        self.assertEqual(rc["natures_evaluated"], 1)
        self.assertEqual(rc["stop"]["reading"], "minus2")
        self.assertEqual(rc["stop"]["reasons"], [f"T <= 0: reporting cells [{c}]"])
        self.assertEqual(seal["U_T_clipped_minus2"][0][c], 0.0)
        self.assertEqual(rc["per_nature"][0]["n1"]["wt"]["rows_above"], 0)

        def nearly(V, P, geo):
            V = kill(V, P, geo)
            live = [i for i in rows_c if P["d_ref"][geo["gen"][i]] > 0]
            V["wt"][:, live[0]] = cv_wt[live[0]]
            return V
        rc, *_, seal = self.run_receipt(V_edit=nearly)
        self.assertEqual(rc["verdict"], "PASS")
        self.assertTrue(all(np.all(seal[f"U_T_clipped_{rd}"][:, c] > 0) for rd in ll5d.READINGS))

    def test_t_le_0_takes_composes_clip_sign_on_near_zero_rows(self):
        """Every row of reporting cell c with every Flux universe's wt 0 and every other universe's equal to the CV's,
        the CV's set to 0.1: compose's order gives exactly 0 + sum (0.1 - 0.1) = 0, while the BLAS composite sums
        0.1 thirty-odd times and subtracts (k - 1) 0.1, which rounds away from 0. Without the recompute a row would keep
        a rounding-sized positive weight and T in cell c would be > 0; with it, every row clips and T <= 0 fires."""
        c = 5
        cells = np.where(np.asarray(self.inputs["pass_truth"], bool),
                         ll5d.flat_cells(np.asarray(self.inputs["MCgen"], float), self.inputs["edges"]), -1)
        rows_c = np.flatnonzero(np.isin(cells, np.flatnonzero(self.fm == c)))
        P = self.prepared(truths=["g18"])
        rel, geo, V, cv = ll5d.c2_inputs(P, self.s1, self.fm)
        cv = dict(cv, wt=np.asarray(cv["wt"], float).copy())
        cv["wt"][rows_c] = 0.1
        V = dict(V, wt=V["wt"].copy())
        V["wt"][:, rows_c] = 0.1
        flux = [P["col"][f"Flux_{i}"] for i in range(100)]
        V["wt"][np.ix_(flux, rows_c)] = 0.0
        draws = self.draws("g18", 4)
        S = ll5d.selection(draws, "minus2", P["col"])
        blas = S @ V["wt"][:, rows_c] - (S.sum(axis=1, keepdims=True) - 1.0) * cv["wt"][rows_c][None]
        self.assertTrue(np.any(blas[0] > 0), "precondition: the BLAS composite rounds above 0 on some row")
        for d in range(len(draws)):
            exact = ll5d.compose_rows(V["wt"], cv["wt"], [P["col"][x] for x in ll5d.drop2(draws[d])], rows_c)[0]
            np.testing.assert_array_equal(exact, 0.0)
        inputs = self.inputs
        const_full = {"n_nucleons": float(inputs["n_nucleons"]), "data_pot": float(inputs["data_pot"]),
                      "edges": inputs["edges"]}
        rc, _, _ = ll5d.receipt(V, cv, draws, P["col"], self.r["g18"], P["phi"], geo, self.U, P["d_ref"], const_full,
                             {f"Flux_{i}": i for i in range(100)}, list(ll5d.TOY_SEEDS["g18"]), rel)
        self.assertEqual(rc["verdict"], "STOP")
        self.assertEqual(rc["stop"]["reasons"], [f"T <= 0: reporting cells [{c}]"])
        self.assertGreater(rc["exact"]["zero_recomputed"]["wt"], 0)

    def test_n1_at_exactly_the_bound_does_not_stop(self):
        """A w_reco row with the CV's weight 0, 1.0 in ten of draw 0's universes and 0 in every other: draw 0's composite
        there is 1 + ... + 1 = 10 exactly against a peak of 1, so N1's statistic is exactly 10, which is not above the
        bound; the receipt passes and records 10."""
        P = self.prepared(truths=["g18"])
        rel, geo, V, cv = ll5d.c2_inputs(P, self.s1, self.fm)
        draws = self.draws("g18", 3)
        row = 11
        cols = [P["col"][x] for x in ll5d.drop2(draws[0])][:10]
        V = dict(V, wr=V["wr"].copy())
        V["wr"][:, row] = 0.0
        V["wr"][cols, row] = 1.0
        cv = dict(cv, wr=np.asarray(cv["wr"], float).copy())
        cv["wr"][row] = 0.0
        inputs = self.inputs
        const_full = {"n_nucleons": float(inputs["n_nucleons"]), "data_pot": float(inputs["data_pot"]),
                      "edges": inputs["edges"]}
        rc, _, _ = ll5d.receipt(V, cv, draws, P["col"], self.r["g18"], P["phi"], geo, self.U, P["d_ref"], const_full,
                             {f"Flux_{i}": i for i in range(100)}, list(ll5d.TOY_SEEDS["g18"]), rel)
        self.assertEqual(rc["verdict"], "PASS")
        self.assertEqual(rc["per_nature"][0]["n1"]["wr"]["max_past_screen"], 10.0)
        self.assertEqual(rc["per_nature"][0]["n1"]["wr"]["rows_above"], 0)

    def test_n1_stops(self):
        def spike(V, P, geo):
            V["wr"] = V["wr"].copy()
            cv_row = np.asarray(self.inputs["w_reco"], float)
            draw = self.draws("g18", 1)[0]
            cols = [P["col"][t] for t in ll5d.drop2(draw)]
            V["wr"][cols, 7] = cv_row[7] - 50.0 * abs(cv_row[7])   # every departure piles up past 10x the peak
            V["wr"][cols[0], 7] = -1.0
            return V
        rc, *_ = self.run_receipt(V_edit=spike)
        self.assertEqual(rc["verdict"], "STOP")
        self.assertTrue(any(s.startswith("N1: wr") for s in rc["stop"]["reasons"]))

    def test_the_receipt_projection_reprices(self):
        calls = []

        def clock(done, total):
            calls.append((done, total))
            if done == 3:
                raise ll5d.Reprice("line")
        with self.assertRaises(ll5d.Reprice):
            self.run_receipt(clock=clock)
        self.assertEqual(calls[-1], (3, 16))


class CrossTerms(unittest.TestCase):
    """REQUIRED (the director's condition 2 on option (B)): the streamed per-draw product composite equals 342c0ce5's
    fd_1b_mc.crossterm. Not bitwise: crossterm forms the product as a_CV exp(sum log|rho|) times its sign parity, and
    product_rows by repeated multiplication, so the two agree to rounding, about k x eps relative; held at 1e-12."""

    @classmethod
    def setUpClass(cls):
        from importlib.machinery import SourceFileLoader
        cls.ref = SourceFileLoader("fd_1b_mc_at_342c0ce5", str(VENDORED_MC)).load_module()

    def test_the_streamed_product_equals_a21s_crossterm(self):
        rng = np.random.default_rng(23)
        nu, n, nb = 12, 300, 10
        V = rng.uniform(0.5, 1.5, (nu, n))
        V[3, :20] = 0.0                                  # a zero universe weight floors the product
        V[5, 20:40] *= -1.0                              # negative ratios: the sign parity
        cv = rng.uniform(0.5, 1.5, n)
        cv[40:55] = 0.0                                  # a_CV = 0: the first-order sum there
        flat = rng.integers(-1, nb, n)
        U = np.vstack([np.where(np.arange(nb) % 4 == c, 1.0 + c, 0.0) for c in range(4)])
        dcols = [np.array([0, 3, 5, 7]), np.array([1, 4, 6, 8, 10]), np.array([2, 5, 9, 11]), np.array([0, 1, 2])]
        Hp, Ha, H0 = self.ref.crossterm(V, cv, dcols, flat, nb, U)
        for d, cs in enumerate(dcols):
            a = ll5d.compose_rows(V, cv, list(cs))[0]
            p = ll5d.product_rows(V, cv, list(cs), a)
            np.testing.assert_allclose(U @ ll5d._bins(flat, p, nb), Hp[d], rtol=1e-12, atol=0, err_msg=f"product {d}")
            np.testing.assert_allclose(U @ ll5d._bins(flat, a, nb), Ha[d], rtol=1e-12, atol=0, err_msg=f"additive {d}")
        np.testing.assert_array_equal(U @ ll5d._bins(flat, cv, nb), H0)

    def test_the_streamed_product_holds_no_array_the_size_of_v(self):
        V = np.random.default_rng(2).uniform(0.5, 1.5, (40, 1000))
        cv = np.ones(1000)
        seen = []

        class Spy(np.ndarray):
            def __getitem__(self, k):
                out = np.ndarray.__getitem__(self, k)
                seen.append(np.shape(out))
                return out
        ll5d.product_rows(V.view(Spy), cv, [0, 5, 9], ll5d.compose_rows(V, cv, [0, 5, 9])[0])
        self.assertTrue(seen and all(sh == (1000,) for sh in seen), seen)


class SourceFactors(Fixture):
    def test_m2f_the_product_composition_is_off_the_nature_path(self):
        def boom(*a, **k):
            raise AssertionError("fd_1b_toys.source_factors was called")
        with mock.patch.object(toys, "source_factors", boom):
            rc, *_ = Receipt.run_receipt(self)
            self.assertEqual(rc["verdict"], "PASS")
            Calibration.state(self)
            ll5d.one_set(("ar23", 0))


# --------------------------------------------------------------------------------------------------- seeds


class Seeds(unittest.TestCase):
    def test_the_declared_seeds(self):
        self.assertEqual(ll5d.TOY_SEEDS["g18"], range(4_751_000, 4_751_300))
        self.assertEqual(ll5d.TOY_SEEDS["ar23"], range(4_761_000, 4_761_300))
        self.assertEqual(ll5d.STAT_SEED, {"g18": 4_770_100, "ar23": 4_770_200})
        self.assertEqual(ll5d.NULL_SEED, {"g18/minus2": 4_770_310, "g18/all": 4_770_320, "ar23/minus2": 4_770_410,
                                          "ar23/all": 4_770_420})
        self.assertEqual(ll5d.CAL_SEED, {"g18": 4_770_500, "ar23": 4_770_600})
        self.assertEqual((ll5d.GATE_N, ll5d.GATE_N_MAX), (3_000, 9_000))

    def test_the_gate_sample_extends_the_toys_and_cannot_overlap(self):
        for t in ll5d.TRUTHS:
            self.assertEqual(ll5d.gate_seeds(t, 3000)[:300], list(ll5d.TOY_SEEDS[t]))
        self.assertLess(ll5d.gate_seeds("g18", ll5d.GATE_N_MAX)[-1], ll5d.TOY_SEEDS["ar23"][0])
        self.assertLess(ll5d.gate_seeds("ar23", ll5d.GATE_N_MAX)[-1], ll5d.STAT_SEED["g18"])
        for n, ok in ((300, True), (9000, True), (3000, True), (280, False), (3010, False), (9020, False)):
            if ok:
                ll5d.check_n(n)
            else:
                with self.assertRaises(ll5d.Refusal):
                    ll5d.check_n(n)

    def test_no_other_tracked_file_uses_the_seed_range(self):
        """Section 3.6's collision check, repeated at this sha: integer tokens in section 3.6's seed range, in tracked
        .py/.sh/.tsv/.json/.md/.txt files, appear only in LL5D's own files, named exactly (OWN_SEED_FILES), or as float
        literals. (The range is not written in this docstring, which a verbose test log prints.)"""
        if not (REPO / ".git").exists():
            self.skipTest("not a git checkout")
        out = subprocess.run(["git", "grep", "-I", "-n", "-o", "-P", SEED_PATTERN + r"(\.[0-9])?", "--", "*.py", "*.sh",
                              "*.tsv", "*.json", "*.md", "*.txt"], cwd=REPO, capture_output=True, text=True)
        self.assertIn(out.returncode, (0, 1), out.stderr)
        self.assertEqual(seed_collisions(out.stdout.splitlines()), [])

    def test_the_seed_check_still_catches_a_real_collision(self):
        """The exclusion is by exact path: a hit in any other file is a collision, in each of the three spellings, and
        so is a hit in a file whose path merely contains an own file's name; a float literal is not."""
        own = OWN_SEED_FILES[0]
        lines = [f"{own}:3:4751000", "nd-unfolding/other.py:7:4751000", "docs/x.md:2:4,760,500",
                 "nd-unfolding/y.py:9:4_770_999", f"copy/{own}:1:4751001", "data/z.json:4:4755555.5",
                 "nd-unfolding/w.py:1:4771000"]
        self.assertEqual(seed_collisions(lines), lines[1:5])
        ours = OWN_RECEIPT_PREFIX + "pilot/unfold.log.txt:12:4751000"
        other_campaign = _RCPT + "fd/receipts-1b/staged/x.txt:3:4751000"
        look_alike = _RCPT + "fd/receipts-ll5d-copy/x.txt:4:4751000"
        nested = "elsewhere/" + OWN_RECEIPT_PREFIX + "x.txt:5:4751000"
        self.assertEqual(seed_collisions([ours, other_campaign, look_alike, nested]), [other_campaign, look_alike, nested])
        self.assertTrue(OWN_RECEIPT_PREFIX.endswith("/fd/receipts-ll5d/"))
        self.assertTrue(re.fullmatch(SEED_PATTERN, "4751000") and re.fullmatch(SEED_PATTERN, "4,751,000"))


# ---------------------------------------------------------------------------------------------- O_NOATIME


class NoAtime(Fixture):
    FLAG = 1 << 29

    def setUp(self):
        super().setUp()
        self.flagged, self.plain_opens = [], []
        real_os_open = os.open

        def os_open(path, flags, *a, **k):
            if flags & self.FLAG:
                self.flagged.append(os.fspath(path))
            return real_os_open(path, flags & ~self.FLAG, *a, **k)

        def recording(real):
            def opener(file, *a, **k):
                if isinstance(file, (str, os.PathLike)):
                    self.plain_opens.append(os.fspath(file))
                return real(file, *a, **k)
            return opener
        self.ps2 = [mock.patch.object(inv, "NOATIME_FLAG", self.FLAG), mock.patch.object(inv.os, "open", os_open),
                    mock.patch.object(builtins, "open", recording(builtins.open)),
                    mock.patch.object(io, "open", recording(io.open))]
        for p in self.ps2:
            p.start()

    def tearDown(self):
        for p in reversed(self.ps2):
            p.stop()
        super().tearDown()

    def test_tdw_ref_the_manifest_and_the_universes_are_read_with_o_noatime_only(self):
        a = self.args()
        self.plain_opens.clear()
        ll5d.load_tdw_ref(a)
        world = self.world()
        for tag in ("MaRES_0", "Flux_3", "GEANT_Pion_1"):
            ll5d.verified_weights(world, a, tag)
        paths = [str(self.manifest)] + [str(self.w.bank / f"{t}_tdw.npy") for t in ll5d.GEANT_BANK_TAGS]
        paths += [str(mc.universe_dir(t, self.w.bank, self.w.det) / f"{t}_{k}.npy") for t in ("MaRES_0", "Flux_3")
                  for k in ("wt", "wr", "tdw", "bkgw")]
        paths += [str(self.w.det / f"GEANT_Pion_1_{k}.npy") for k in ("wt", "wr", "denom_nd", "bkgw")]
        for p in paths:
            self.assertIn(p, self.flagged, p)
            self.assertNotIn(p, self.plain_opens, p)

    def test_the_calibration_record_is_read_with_o_noatime_only(self):
        cal = self.tmp / "na-cal.json"
        thr = {e: {"ii_mean_log": 1.0, "iii_alpha_multiple": 1.0} for e in ll5d.EVALUATIONS}
        cal.write_text(json.dumps({"schema": ll5d.SCHEMA_CAL, "verdict": "CALIBRATED", "rule": {"s": 1.0,
                                   "thresholds": thr}, "sd300_per_cell": {e: [1.0] for e in ll5d.EVALUATIONS},
                                   "code_sha256": ll5d.code_digests(), "draws_per_set": 300}))
        np.savez(cal.with_suffix(".npz"), single_x_g18=np.ones((2, 2)))
        a = argparse.Namespace(calibration=cal, expect_calibration_sha256=digest(cal),
                               expect_calibration_npz_sha256=digest(cal.with_suffix(".npz")))
        self.plain_opens.clear()
        ll5d.read_calibration(a, np.ones((2, 2)), "g18")
        for p in (str(cal), str(cal.with_suffix(".npz"))):
            self.assertIn(p, self.flagged)
            self.assertNotIn(p, self.plain_opens)


class ExitCodes(unittest.TestCase):
    def run_main(self, rec=None, exc=None, cmd="calib"):
        tmp = Path(tempfile.mkdtemp(prefix="ll5d-rc-"))
        self.addCleanup(shutil.rmtree, tmp)
        argv = [cmd] + [x for k in ("npz", "bkg", "bank", "detector-dir", "pins", "flux-constraint", "flux-table",
                                    "definition", "prep", "manifest") for x in (f"--{k}", str(tmp / k))]
        argv += ["--out", str(tmp / "out.json"), "--expect-pins-sha256", "p", "--expect-flux-table-sha256", "f",
                 "--expect-manifest-sha256", "m", "--time-limit-seconds", "100"]
        argv += ["--workers", "1", "--budget-seconds", "1"] if cmd == "calib" else [
            "--truth", "g18", "--staged", str(tmp), "--calibration", str(tmp / "c.json"),
            "--expect-calibration-sha256", "c", "--expect-calibration-npz-sha256", "n"]
        fn = "calib_main" if cmd == "calib" else "gate_main"

        def body(a):
            if exc:
                raise exc
            return rec
        with mock.patch.object(ll5d, fn, body), mock.patch.object(inv, "atime_check",
                                                                  lambda: {"moved": (rec or {}).get("_moved", [])}):
            return ll5d.main(argv), tmp

    def test_an_atime_move_sets_8(self):
        rc, _ = self.run_main({"verdict": "CALIBRATED", "atime": {"moved": ["/x"]}})
        self.assertEqual(rc, 8)
        rc, _ = self.run_main({"verdict": "STOP", "atime": {"moved": ["/x"]}}, cmd="gate")
        self.assertEqual(rc, 3 | 8)
        rc, _ = self.run_main({"verdict": "PASS", "atime": {"moved": []}}, cmd="gate")
        self.assertEqual(rc, 0)

    def test_refusals_are_invalid_and_reprices_are_reprices(self):
        rc, tmp = self.run_main(exc=ll5d.Refusal("bad input"))
        self.assertEqual(rc, 5)
        self.assertEqual(json.loads((tmp / "out.invalid.json").read_text())["verdict"], "INVALID")
        rc, tmp = self.run_main(exc=ll5d.Reprice("slow"), cmd="gate")
        self.assertEqual(rc, 4)
        rc, _ = self.run_main({"verdict": "POWER_SHORT_TO_DIRECTOR", "atime": {"moved": []}})
        self.assertEqual(rc, 3)

    def test_one_blas_thread_is_required(self):
        with mock.patch.dict(os.environ, ONES):
            ll5d.require_threads()
        with mock.patch.dict(os.environ, dict(ONES, OPENBLAS_NUM_THREADS="8")):
            with self.assertRaisesRegex(ll5d.Refusal, "OPENBLAS_NUM_THREADS"):
                ll5d.require_threads()


# --------------------------------------------------------------------------------------------- end to end


class Jobs(Fixture):
    """calib_main then gate_main over the toy world, at N = 300 and 40 replicate sets (the rules are N-free)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cal = cls.tmp / "cal" / "cal.json"

    def calibrate(self):
        if self.cal.exists():
            return json.loads(self.cal.read_text())
        a = self.args(out=self.cal, draws=300, sets=40, workers=2, budget_seconds=1e6)
        ps = self.job_patches()
        for p in ps:
            p.start()
        try:
            return ll5d.calib_main(a)
        finally:
            for p in reversed(ps):
                p.stop()

    def gate(self, truth="g18", out=None, cal_rec=None, **kw):
        self.calibrate()
        cal = self.cal
        if cal_rec is not None:
            cal = self.tmp / "cal" / f"edited-{len(list((self.tmp / 'cal').iterdir()))}.json"
            cal.write_text(json.dumps(cal_rec))
            shutil.copy(self.cal.with_suffix(".npz"), cal.with_suffix(".npz"))
        out = out or self.tmp / f"gate-{truth}-{len(list(self.tmp.iterdir()))}.json"
        a = self.args(out=out, truth=truth, staged=self.tmp, calibration=cal, expect_calibration_sha256=digest(cal),
                      expect_calibration_npz_sha256=digest(cal.with_suffix(".npz")), **kw)
        ps = self.job_patches()
        for p in ps:
            p.start()
        try:
            return ll5d.gate_main(a)
        finally:
            for p in reversed(ps):
                p.stop()

    def test_a_calibration_over_the_toy_world(self):
        rec = self.calibrate()
        self.assertEqual(rec["schema"], ll5d.SCHEMA_CAL)
        self.assertEqual(rec["evaluations"], list(ll5d.EVALUATIONS))
        self.assertEqual(rec["draws_per_set"], 300)
        self.assertEqual(set(rec["sd300_per_cell"]), set(ll5d.EVALUATIONS))
        law_control_computed(self, rec["control_law"])
        self.assertTrue(rec["checks"]["D1"]["passes"])
        self.assertEqual(rec["code_sha256"], ll5d.code_digests())
        self.assertEqual(rec["fd_1b_c2_source"], ll5d.FD_1B_C2_SOURCE)
        z = np.load(self.cal.with_suffix(".npz"))
        self.assertEqual(z["ratio_g18_minus2"].shape, (40, sa.N_CELLS))
        np.testing.assert_array_equal(z["ratio300_ar23_all"], z["ratio_ar23_all"])   # N = 300: the same draws

    def calibrated(self, ii=10.0, iii=100.0):
        """The toy calibration (40 sets cannot reach the 1 % budget) with thresholds and backstop SDs written in, so
        the gate's reading path runs; the rule itself is tested in Rule."""
        rec = json.loads(json.dumps(self.calibrate()))
        rec["verdict"] = "CALIBRATED"
        rec["rule"]["s"] = 1.0
        for e in ll5d.EVALUATIONS:
            rec["rule"]["thresholds"][e].update(ii_mean_log=ii, iii_alpha_multiple=iii)
        return rec

    def test_a_gate_over_the_toy_world(self):
        g = self.gate(cal_rec=self.calibrated())
        self.assertIn(g["verdict"], ("PASS", "STOP"))
        self.assertEqual(g["receipt"]["verdict"], "PASS")
        self.assertEqual(set(g["reads"]), {"g18/minus2", "g18/all"})
        self.assertEqual(set(g["backstop"]), {"g18/minus2", "g18/all"})
        self.assertTrue(g["gate_sample"]["first_300_bitwise"])
        self.assertTrue(g["controls"]["denominator"]["passes"])
        self.assertIn("minus2", g["receipt"]["crossterm"])
        self.assertGreater(g["peak_rss_kib"], 0)
        self.assertIn("gate_projection", g)
        ok = all(v == "option (1)" for v in g["reads"].values()) and all(b["passes"] for b in g["backstop"].values())
        self.assertEqual(g["verdict"], "PASS" if ok else "STOP")

    def test_the_gate_refuses_an_uncalibrated_or_foreign_calibration(self):
        rec = self.calibrated()
        with self.assertRaisesRegex(ll5d.Refusal, "not CALIBRATED"):
            self.gate(cal_rec=dict(rec, verdict="POWER_SHORT_TO_DIRECTOR"))
        with self.assertRaisesRegex(ll5d.Refusal, "other code"):
            self.gate(cal_rec=dict(rec, code_sha256={"ll5d.py": "x"}))
        no_s = json.loads(json.dumps(rec))
        no_s["rule"]["s"] = None
        with self.assertRaisesRegex(ll5d.Refusal, "no threshold"):
            self.gate(cal_rec=no_s)
        one = json.loads(json.dumps(rec))
        one["sd300_per_cell"].pop("ar23/minus2")
        with self.assertRaisesRegex(ll5d.Refusal, "no threshold"):
            self.gate(cal_rec=one)

    def test_each_evaluation_reads_its_own_thresholds(self):
        rec = self.calibrated()
        for e in ll5d.EVALUATIONS:
            if e.endswith("/minus2"):
                rec["rule"]["thresholds"][e].update(ii_mean_log=0.0, iii_alpha_multiple=0.0)
        g = self.gate(cal_rec=rec)
        self.assertNotEqual(g["reads"]["g18/minus2"], "option (1)")
        self.assertEqual(g["reading_detail"]["g18/all"]["gate_n"]["passes"], True)
        self.assertEqual(g["reading_detail"]["g18/minus2"]["gate_n"]["passes"], False)

    def test_a_gate_sample_whose_first_300_differ_is_refused(self):
        """11-04 item 1's bit-for-bit check: the gate sample's first 300 must be the declared draws' C2 quantities."""
        real, calls = c2.c2_truth, []

        def shifted(V, cv, S, *a, **k):
            q = real(V, cv, S, *a, **k)
            calls.append(S.shape[0])
            if len(calls) == 3:                             # the first reading's gate sample (head, tail, sample)
                q = dict(q, N=q["N"].copy())
                q["N"][0, 0] = np.nextafter(q["N"][0, 0], np.inf)
            return q
        with mock.patch.object(c2, "c2_truth", shifted), \
                self.assertRaisesRegex(ll5d.Refusal, "first 300 differ from the declared draws in N"):
            self.gate(cal_rec=self.calibrated())

    def test_the_clip_prep_is_sealed_and_moves_no_verdict(self):
        """The gate record holds only the sealed file's path, size, sha256 and keys; the verdict, the readings and the
        backstop are the same with the clip-prep products removed (the director's condition 3)."""
        g = self.gate(cal_rec=self.calibrated())
        cp = g["clip_prep"]
        self.assertEqual(set(cp), {"path", "bytes", "sha256", "keys", "sealed"})
        f = self.tmp / cp["path"]
        self.assertEqual(hashlib.sha256(f.read_bytes()).hexdigest(), cp["sha256"])
        self.assertEqual(f.stat().st_size, cp["bytes"])

        def keys(x):
            if isinstance(x, dict):
                for k, v in x.items():
                    yield k
                    yield from keys(v)
            elif isinstance(x, list):
                for v in x:
                    yield from keys(v)
        rest = {k: v for k, v in g.items() if k != "clip_prep"}
        self.assertFalse([k for k in keys(rest) if k.startswith(("signal_negative", "background_negative", "U_T_"))])
        real = ll5d.receipt

        def unsealed(*a, **k):
            rc, fine, _ = real(*a, **k)
            return rc, fine, {}
        with mock.patch.object(ll5d, "receipt", unsealed):
            h = self.gate(cal_rec=self.calibrated())
        self.assertIsNone(h["clip_prep"])
        for k in ("verdict", "reads", "backstop", "reading_detail"):
            self.assertEqual(json.dumps(g[k], sort_keys=True), json.dumps(h[k], sort_keys=True), k)

    def test_a_failing_gate_reading_is_a_stop(self):
        g = self.gate(cal_rec=self.calibrated(ii=0.0, iii=0.0))
        self.assertEqual(g["verdict"], "STOP")
        self.assertTrue(all(v != "option (1)" for v in g["reads"].values()))

    def test_a_failed_control_is_invalid_before_anything_is_read(self):
        rec = self.calibrated()
        with mock.patch.object(ll5d, "truths_r", lambda w, p, t: ({x: self.r[x] for x in t},
                                                                  {x: {"passes": False} for x in t})):
            g = self.gate(cal_rec=rec)
        self.assertEqual(g["verdict"], "INVALID")
        self.assertNotIn("receipt", g)

    def test_the_receipt_reprices_past_its_line(self):
        with self.assertRaisesRegex(ll5d.Reprice, "the receipt alone projects"):
            self.gate(cal_rec=self.calibrated(), time_limit_seconds=1e-3)

    def test_the_gate_reprices_past_its_line(self):
        with mock.patch.object(ll5d, "RECEIPT_PROBE", 10 ** 9), \
                self.assertRaisesRegex(ll5d.Reprice, "the gate projects"):
            self.gate(cal_rec=self.calibrated(), time_limit_seconds=1e-3)


# ------------------------------------------------------------------- the real chain (amendment A1a.1)


def pristine_s5n():
    """s5n_pseudo's own definitions, loaded afresh from its source: the state of a fresh process, before any
    s5e_candidate.install. Patched over the shared module, it makes a test independent of what earlier tests installed."""
    from importlib.machinery import SourceFileLoader
    pr = SourceFileLoader("s5n_pseudo_pristine", str(ND / "s5n_pseudo.py")).load_module()
    import s5n_pseudo
    return mock.patch.multiple(s5n_pseudo, truth_weight=pr.truth_weight, TRUTHS=pr.TRUTHS,
                               refine_params=pr.refine_params, code_digests=pr.code_digests)


class RealChain(unittest.TestCase):
    """Amendment A1a.1 (the director's ruling on ll5d_calib run 1): the entry points over real files, with nothing in
    the fd_1b_mc / s5n_pseudo / s5c_pseudo chain mocked. A2.1's toy world, rewritten so its files agree as the real
    bank's do (the bank's td_* rows in cv.npz, every bank tdw about tdw_ref within 2 %, the six bank GEANT tdw equal
    to tdw_ref, the npz's and every detector universe's denom_nd hist(tdw_ref)), then re-pinned (detector receipt,
    sf1-style manifest, pins) and given a staged flux table. Outside the chain only: the H2 definition's map and S1's
    functional (s1_assemble, the toy grid), S1's assembly and reported matrix (fd_1b_score, gate only), the input
    digests and F1 sums (the world's own patches), O_NOATIME off (macOS), and the thread variables."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="ll5d-real-"))
        w = cls.w = ToyWorld(cls.tmp)
        w.constraint.write_text("".join(f"Flux {i} {float(w.flux_w[i])!r}\n" for i in range(100)) + "Other 0 1.0\n")
        rng = np.random.default_rng(9)                 # the constraint in plain floats: numpy 2's repr is np.float64(...)
        z = dict(np.load(w.bank / "cv.npz", allow_pickle=False))
        edges = [np.asarray(np.load(w.inputs)[f"edges_{i}"], float) for i in range(5)]
        for k, e in zip(("td_pt", "td_pz", "td_ea", "td_q3", "td_w"), edges):
            z[k] = rng.uniform(e[0], e[-1], 50)
        np.savez(w.bank / "cv.npz", **z)
        cls.tdw_ref = rng.uniform(0.95, 1.05, 50)
        for p in sorted(w.bank.glob("*_tdw.npy")):
            tag = p.name[:-len("_tdw.npy")]
            v = cls.tdw_ref if tag in ll5d.GEANT_BANK_TAGS else \
                cls.tdw_ref * np.random.default_rng(zlib.crc32(tag.encode())).uniform(0.98, 1.02, 50)
            np.save(p, v)
        dn = s5p_universe.denominator(z, cls.tdw_ref, edges)
        zi = dict(np.load(w.inputs, allow_pickle=False))
        zi["denom_nd"] = dn
        np.savez(w.inputs, **zi)
        zb = dict(np.load(w.bkg, allow_pickle=True))
        zb["meta"] = json.dumps({"npz_sha256": digest(w.inputs)})
        np.savez(w.bkg, **zb)
        for p in sorted(w.det.glob("*_denom_nd.npy")):
            np.save(p, dn)
        w.receipt.write_text(json.dumps({"files_sha256": {p.name: digest(p) for p in sorted(w.det.iterdir())}}))
        w.manifest.write_text("".join(f"{digest(p)}  {p}\n" for p in sorted(w.bank.iterdir()))
                              + f"{digest(w.receipt)}  {w.receipt}\n")
        w.pins.write_text(json.dumps(toys.make_pins(w.bank, w.det, w.manifest, w.receipt)))
        flux = np.asarray(zi["flux"], float)
        cls.flux_table = cls.tmp / "flux_universes.npz"
        np.savez(cls.flux_table, hFluxCV=flux, hFluxUniv=flux[None] * rng.uniform(0.9, 1.1, (100, flux.size)))
        n_bins = int(np.prod([e.size - 1 for e in edges]))
        cells = ll5d.flat_cells(np.asarray(zi["MCgen"], float), edges)
        live = np.unique(cells[(cells >= 0) & np.asarray(zi["pass_truth"], bool)])
        fm = np.full(n_bins, -1)
        fm[live] = np.arange(live.size) % sa.N_CELLS
        cls.fm = fm
        cls.U = np.vstack([np.where(fm == c, 1.0 + 0.1 * c, 0.0) for c in range(sa.N_CELLS)])
        f = np.linspace(1.0, 2.0, sa.N_CELLS)
        cls.s1 = {"U": cls.U.astype(np.float32), "f": f}
        cls.reported = np.diag((0.05 * f) ** 2)
        cls.cal = cls.tmp / "cal" / "calibration.json"
        cls.gate_out = cls.tmp / "gate" / "gate-g18.json"
        (cls.tmp / "s1").mkdir()
        (cls.tmp / "s1" / "s1_assembly.npz").write_bytes(b"S1's assembly stands in: fd_1b_score.load_s1 is patched")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def setUp(self):
        self.ps = self.w.patches() + [plain(), mock.patch.dict(os.environ, ONES),
                                      mock.patch.object(ll5d, "TDW_REF_SHA256", digest(self.w.bank / "GEANT_Neutron_0_tdw.npy")),
                                      mock.patch.object(sa, "fine_map", lambda p: self.fm),
                                      mock.patch.object(sa, "functional_matrix", lambda fm: self.U),
                                      mock.patch.object(fs, "load_s1", lambda p: self.s1),
                                      mock.patch.object(fs, "reported_matrix", lambda s1: self.reported),
                                      pristine_s5n()]
        for p in self.ps:
            p.start()

    def tearDown(self):
        for p in reversed(self.ps):
            p.stop()

    def args(self, **kw):
        w = self.w
        base = dict(npz=w.inputs, bkg=w.bkg, bank=w.bank, detector_dir=w.det, pins=w.pins, expect_pins_sha256=digest(w.pins),
                    flux_constraint=w.constraint, flux_table=self.flux_table,
                    expect_flux_table_sha256=digest(self.flux_table), definition=self.tmp / "definition.json",
                    prep=w.prep, manifest=w.manifest, expect_manifest_sha256=digest(w.manifest), time_limit_seconds=1e7)
        base.update(kw)
        return argparse.Namespace(**base)

    def calibrate(self):
        if not self.cal.exists():
            ll5d.calib_main(self.args(out=self.cal, draws=300, sets=20, workers=2, budget_seconds=1e7))
        rec = json.loads(self.cal.read_text())
        return rec

    def gate(self):
        if self.gate_out.exists():
            return json.loads(self.gate_out.read_text())
        rec = json.loads(json.dumps(self.calibrate()))
        rec["verdict"] = "CALIBRATED"
        rec["rule"]["s"] = 1.0
        for e in ll5d.EVALUATIONS:
            rec["rule"]["thresholds"][e].update(ii_mean_log=10.0, iii_alpha_multiple=100.0)
        cal = self.tmp / "cal" / "calibrated.json"
        cal.write_text(json.dumps(rec))
        shutil.copy(self.cal.with_suffix(".npz"), cal.with_suffix(".npz"))
        with pristine_s5n():                           # the gate installs on its own, whatever the calibration did
            return ll5d.gate_main(self.args(out=self.gate_out, truth="g18", staged=self.tmp, calibration=cal,
                                            expect_calibration_sha256=digest(cal),
                                            expect_calibration_npz_sha256=digest(cal.with_suffix(".npz"))))

    def test_truths_r_runs_the_real_truth_weight_after_the_install(self):
        """REQUIRED (A1a.1): truths_r over the world's real F1 prep ratios with fd_1b_mc.truth_weight unmocked. In a
        fresh process's state it raises ValueError("ratio_nd"), ll5d_calib run 1's crash; after install_config it
        returns r_T, finite and positive here, and different for the two truths."""
        world = mc._load_world(self.args())
        with self.assertRaisesRegex(ValueError, "ratio_nd"):
            ll5d.truths_r(world, self.w.prep, ["g18"])
        ll5d.install_config()
        r, ctl = ll5d.truths_r(world, self.w.prep, list(ll5d.TRUTHS))
        self.assertTrue(all(c["passes"] for c in ctl.values()))
        self.assertFalse(np.array_equal(r["g18"], r["ar23"]))
        self.assertFalse(np.all(r["g18"] == 1.0))

    def test_calib_main_runs_the_real_chain(self):
        """The calibration's entry point over real files, nothing in the chain mocked: it installs the candidate
        itself, loads the world, reads tdw_ref with D1, the truths, every universe, and writes its record."""
        rec = self.calibrate()
        self.assertEqual(rec["schema"], ll5d.SCHEMA_CAL)
        self.assertTrue(rec["checks"]["D1"]["passes"])
        self.assertTrue(all(v["passes"] for v in rec["checks"]["r_positive"].values()))
        law_control_computed(self, rec["control_law"])
        self.assertEqual(rec["atime"]["moved"], [])

    def test_gate_main_runs_the_real_chain(self):
        """The gate's entry point over real files, nothing in the chain mocked: the controls, the receipt over the
        declared draws in both readings, the sealed clip-prep file, the gate."""
        g = self.gate()
        self.assertTrue(g["controls"]["denominator"]["passes"], g["controls"])
        self.assertTrue(g["controls"]["r_positive"]["passes"])
        self.assertEqual(g["receipt"]["verdict"], "PASS", g["receipt"].get("stop"))
        self.assertIn(g["verdict"], ("PASS", "STOP"))
        self.assertTrue((self.gate_out.parent / g["clip_prep"]["path"]).exists())


# --------------------------------------------------------------------------------- the all-path equality


class A21Equality(Fixture):
    """REQUIRED (the director's ruling on A1): on the all path, ll5d's builders and the gate's c2_truth/c2_block equal
    A2.1's own path at 342c0ce5 bitwise, run in a subprocess with the vendored fd_1b_mc, --cv-tdw set to tdw_ref."""

    def reference(self, draws: dict) -> dict:
        d = Path(tempfile.mkdtemp(prefix="ll5d-a21-"))
        self.addCleanup(shutil.rmtree, d)
        vendor = d / "vendor"
        vendor.mkdir()
        shutil.copy(VENDORED_MC, vendor / "fd_1b_mc.py")
        fx = {"meta": np.array(json.dumps({"n_edges": len(self.inputs["edges"]), "truths": list(ll5d.TRUTHS),
                                           "groups": self.groups})),
              "flux": self.flux, "tdw_ref": self.tdw_ref, "fm": self.fm, "U": self.U, "flux_p": self.flux_p,
              "s1_U": self.s1["U"], "s1_f": self.s1["f"], "reported": self.reported}
        for k, v in self.inputs.items():
            if k != "edges":
                fx[f"in::{k}"] = np.asarray(v)
        for i, e in enumerate(self.inputs["edges"]):
            fx[f"edge::{i}"] = np.asarray(e)
        for k, v in self.bkg.items():
            fx[f"bkg::{k}"] = np.asarray(v)
        for k, v in self.bank_cv.items():
            fx[f"cv::{k}"] = np.asarray(v)
        for t, w in self.weights.items():
            for k, v in w.items():
                fx[f"w::{t}::{k}"] = np.asarray(v)
        for t in ll5d.TRUTHS:
            fx[f"r::{t}"] = self.r[t]
        np.savez(d / "fixture.npz", **fx)
        (d / "draws.json").write_text(json.dumps(draws))
        env = dict(os.environ, PYTHONHASHSEED="0", **ONES)
        p = subprocess.run([sys.executable, "-B", str(RUNNER), str(vendor), str(d / "fixture.npz"),
                            str(d / "draws.json"), str(d / "out.npz")], capture_output=True, text=True, env=env)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("A21-REFERENCE OK", p.stdout)
        z = np.load(d / "out.npz", allow_pickle=False)
        return {k: z[k] for k in z.files}

    def test_the_all_path_equals_a21s_bitwise(self):
        draws = {t: self.draws(t, 6) for t in ll5d.TRUTHS}
        ref = self.reference(draws)
        P = self.prepared()
        rel, geo, V, cv = ll5d.c2_inputs(P, self.s1, self.fm)
        mine = {"rel": rel, "keep": P["keep"], "D_full": P["D_full"], "D_cv_full": P["D_cv_full"], "phi": P["phi"]}
        mine.update({f"H::{k}": v for k, v in P["H"].items()})
        mine.update({f"cv::{k}": v for k, v in P["cv"].items()})
        mine.update({f"V::{k}": V[k] for k in ("wt", "wr", "bkgw", "tdw")})
        mine.update({f"cvrow::{k}": cv[k] for k in ("wt", "wr", "bkgw", "tdw")})
        mine.update({f"geo::{k}": geo[k] for k in ("gen", "reco", "bkg", "td")})
        blocks = {}
        for t in ll5d.TRUTHS:
            mine[f"single_x::{t}"] = P["single_x"][t]
            mine[f"ref_x::{t}"] = P["ref_x"][f"{t}/all"]
            mine[f"ref_count::{t}"] = P["ref_count"][f"{t}/all"]
            S = ll5d.selection(draws[t], "all", P["col"])
            q = c2.c2_truth(V, cv, S, self.r[t], geo, c2.draw_flux(S, P["flux_cols"], P["phi"]), P["const"])
            mine.update({f"q::{t}::{k}": v for k, v in q.items()})
            blocks[t] = c2.c2_block(q, P["ref_x"][f"{t}/all"], rel)
        vi = c2.c2_vi(P, cv, self.fm, geo)
        self.assertEqual(set(mine), set(ref) - {"json"})
        for k in mine:
            np.testing.assert_array_equal(mine[k], ref[k], err_msg=k)
        self.assertEqual(json.loads(str(ref["json"])), json.loads(json.dumps({"blocks": blocks, "vi": vi},
                                                                             sort_keys=True)))


# ------------------------------------------------------------------------------------------------- the merge


class Merge(unittest.TestCase):
    def part(self, t, verdict="PASS", **kw):
        p = {"truth": t, "verdict": verdict, "record": {"vi": {"a": 1}}, "reads": {f"{t}/minus2": "option (1)"},
             "backstop": {f"{t}/minus2": {"passes": True}}, "receipt": {"verdict": "PASS"}}
        p.update({k: "same" for k in ll5d.MERGE_SAME})
        p.update(kw)
        return p

    def test_pass_needs_both(self):
        self.assertEqual(ll5d.gate_merge([self.part("g18"), self.part("ar23")])["verdict"], "PASS")
        self.assertEqual(ll5d.gate_merge([self.part("g18"), self.part("ar23", "STOP")])["verdict"], "STOP")
        self.assertEqual(ll5d.gate_merge([self.part("g18", "INVALID"), self.part("ar23", "STOP")])["verdict"],
                         "INVALID")

    def test_refusals(self):
        with self.assertRaises(ll5d.Refusal):
            ll5d.gate_merge([self.part("g18"), self.part("g18")])
        with self.assertRaises(ll5d.Refusal):
            ll5d.gate_merge([self.part("g18"), self.part("ar23", code_sha256="other")])
        with self.assertRaises(ll5d.Refusal):
            ll5d.gate_merge([self.part("g18"), self.part("ar23", record={"vi": {"a": 2}})])


if __name__ == "__main__":
    unittest.main()
