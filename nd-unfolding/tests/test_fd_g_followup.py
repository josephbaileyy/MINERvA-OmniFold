"""Controls for fd_g_followup (FD-G-FOLLOWUP-DECLARATION.md section 6), on synthetic matrices, on G-DIAG's synthetic
Stage G tree and on the committed records. No real prediction, covariance or data value is read; the H2 definition is
the committed one (it is simulation-only and pinned).

* Shrink: the diagonal is kept bit for bit, the off-diagonal is (1 - alpha) times, the literal D^1/2 [...] D^1/2
  form agrees, alpha = 0 is the identity and alpha = 1 the diagonal, and positive semidefiniteness is kept.
* Definition: R04's face neighbours and every listed cell's reporting neighbours agree with the boxes' geometry.
* Planted defects: for each item of G-R04 (0-5) and of G-SENS, a defective version of the tool's own function is
  patched in and a control or the item's validator, silent on the correct output, reports it.
* End to end: Stage G and G-DIAG are run on the synthetic tree, then G-FOLLOWUP as invoked (-I -B, cwd outside
  nd-unfolding); every number is recomputed by hand. Each control F0, R1-R4 and S0-S2 refuses with nothing written."""
import json
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
import fd_g_compare as G  # noqa: E402
import fd_g_diag as D  # noqa: E402
import fd_g_followup as F  # noqa: E402
import s1_assemble as sa  # noqa: E402
from test_fd_g_compare import DEFINITION, digest, run_isolated  # noqa: E402
from test_fd_g_diag import DiagTree  # noqa: E402

REPO = ND.parent
FD = REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024"
DEFN = json.loads(DEFINITION.read_text())


def psd(n=16, rank=None, seed=0, scale=1.0):
    A = np.random.default_rng(seed).normal(size=(rank or n, n))
    return (A.T @ A) * scale


def faces(a: dict, b: dict) -> list[str]:
    """The axes along which boxes a and b touch, when they overlap with positive length on every other axis."""
    touch = [ax for ax in a if a[ax][1] == b[ax][0] or b[ax][1] == a[ax][0]]
    over = [ax for ax in a if min(a[ax][1], b[ax][1]) > max(a[ax][0], b[ax][0])]
    return touch if len(touch) == 1 and len(over) == len(a) - 1 else []


def find_p(obj, path=""):
    """Every key named exactly p, anywhere."""
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "p":
                out.append(f"{path}.p")
            out.extend(find_p(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.extend(find_p(v, f"{path}[{i}]"))
    return out


# validators: each returns a list of problems; silent on the correct output, loud on a planted defect

def check_neighbours(item1):
    bad = []
    boxes = {f"R{c['id']:02d}": c["box"] for c in DEFN["reporting_cells"]}
    for c, r in item1.items():
        want = {(o, faces(boxes[c], boxes[o])[0]) for o in boxes if o != c and faces(boxes[c], boxes[o])}
        got = {(n["neighbour"], n["axis"]) for n in r["neighbours"] if n["neighbour"].startswith("R")}
        if got != want:
            bad.append(f"{c}: reporting neighbours {sorted(got)} != geometry {sorted(want)}")
    return bad


def check_counts(item1, fm):
    return [f"{c}: {r['n_fine_bins']} fine bins" for c, r in item1.items()
            if r["n_fine_bins"] != int(np.bincount(fm[fm >= 0], minlength=16)[int(c[1:])])]


def check_medians(item2, rel_by_hand):
    return [k for k, v in rel_by_hand.items() if not np.isclose(item2["median_over_16"][k], np.median(v), rtol=1e-12)]


def check_item4(item4, g):
    bad = []
    for name, p in item4.items():
        rec = g[name]
        for c, v in p["cells"].items():
            if c not in rec["cells"]:
                if v["compared"] or set(v) != {"compared", "why"}:
                    bad.append(f"{name} {c}: a value where Stage G formed none")
                continue
            k = rec["cells"].index(c)
            for key, src in (("g_over_f_minus_1", "g_over_f_minus_1"), ("pull", "pulls"),
                             ("sigma_total_over_f", "sigma_total_over_f"), ("sigma_Vg_over_f", "sigma_Vg_over_f"),
                             ("n_mc_events", "n_mc_events_in_cells")):
                if v.get(key) != rec[src][k]:
                    bad.append(f"{name} {c}: {key}")
    return bad


def check_search(matches, want):
    return [f"{name}: missing {w}" for name, ws in want.items() for w in ws if w not in matches.get(name, [])]


def check_provenance(prov, gd):
    bad = []
    gdp = {p["name"]: p for p in gd["predictions"]}
    for name, tops in prov.items():
        ref = gdp[name]["comparisons"][0]["relative_to_f"]["top_modes"]
        for t, r in zip(tops, ref):
            if t["mode"] != r["mode"] or any(t["loadings"][c] != r["loadings"][c] for c in F.CELLS):
                bad.append(f"{name} mode {t['mode']}: not the reported comparison's")
    return bad


class FollowupTree(DiagTree):
    """G-DIAG's synthetic tree, with S1's readout carrying every group's relative sigma and median (as s1_assemble
    writes it), and G-DIAG run on it: its readout is the one G-FOLLOWUP pins. The seed block is exactly zero, as in
    the committed S1 readout (relative sigma 0 on every cell)."""

    def __init__(self, root, seed=0, scale=1e-39):
        super().__init__(root, seed=seed, scale=scale)
        self.blocks["seed"] = np.zeros((16, 16))
        self.Ce = sum(self.blocks[k] for k in sorted(self.blocks))
        self.Ct = self.Ce + self.Cma

    def write(self, mutate=None, role="adopted", g_mutate=None, s1_mutate=None):
        super().write(mutate, role=role, g_mutate=g_mutate)
        R = self.root
        groups = {}
        for k, v in self.blocks.items():
            groups[sa.group_of(k)] = groups.get(sa.group_of(k), 0) + v
        rel = {g: (np.sqrt(np.diag(C)) / self.f).tolist() for g, C in
               {**groups, "C_e": self.Ce, "C_model": self.Cma, "C_total": self.Ct}.items()}
        s1j = {"assembly_sha256": self.pins["s1_npz"], "relative_sigma": rel,
               "median_relative_sigma": {g: float(np.median(v)) for g, v in rel.items()}}
        if s1_mutate:
            s1_mutate(s1j)
        p = R / "s1_assembly.json"
        p.write_text(json.dumps(s1j))
        self.pins["s1_json"] = digest(p)
        self.dpins["s1_json"] = digest(p)
        self.gd_readout = R / "fd_g_diag_readout.json"
        dargv = [x if x != str(self.out / "diag.json") else str(self.gd_readout) for x in self.dargv]
        with mock.patch("sys.stdout"):
            D.run(D.build_args(dargv), self.dpins, self.predictions)
        self.fpins = {**self.dpins, "g_diag_readout": digest(self.gd_readout)}
        self.fargv = self.dargv[:-2] + ["--g-diag-readout", str(self.gd_readout), "--out-json",
                                        str(self.out / "followup.json")]
        return self

    def config(self):
        return {"nd": str(ND), "pins": self.fpins, "predictions": self.predictions, "argv": self.fargv}


WRAPPER = r"""
import json, sys
cfg = json.load(open(sys.argv[1]))
sys.path.insert(0, cfg["nd"])
import fd_g_compare as g
import fd_g_followup as m
m.PINS = m.SENS2_PINS = cfg["pins"]
g.PREDICTIONS = tuple(dict(p, meta=tuple(p["meta"])) for p in cfg["predictions"])
sys.argv = ["fd_g_followup.py"] + cfg["argv"]
raise SystemExit(m.main(cfg["argv"]))
"""


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fd-gf-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def run_module(self, tree):
        cfg, w = self.tmp / "cfg.json", self.tmp / "wrapper.py"
        cfg.write_text(json.dumps(tree.config()))
        w.write_text(WRAPPER)
        return run_isolated([str(w), str(cfg)])

    def run_inproc(self, tree):
        with mock.patch("sys.stdout"):
            self.assertEqual(F.run(F.build_args(tree.fargv), tree.fpins, tree.predictions), 0)
        return json.loads((tree.out / "followup.json").read_text())

    def assertStops(self, tree, control, why=""):
        with self.assertRaises(SystemExit) as cm, mock.patch("sys.stdout"):
            F.run(F.build_args(tree.fargv), tree.fpins, tree.predictions)
        self.assertIn(f"FAIL control {control}:", str(cm.exception.code))
        self.assertIn(why, str(cm.exception.code))
        self.assertFalse((tree.out / "followup.json").exists(), "a refused run wrote its readout")


# ------------------------------------------------------------------------------------------------ shrink


class Shrink(unittest.TestCase):
    def test_the_diagonal_is_kept_bit_for_bit(self):
        for seed, scale in ((0, 1.0), (1, 1e-80), (2, 3.7e-41)):
            C = psd(seed=seed, scale=scale)
            for a in (*F.ALPHAS, 0.3, 0.77, 1 / 3):
                self.assertTrue(np.array_equal(np.diag(F.shrink(C, a)), np.diag(C)), (seed, a))

    def test_off_diagonal_and_the_literal_form(self):
        C = psd(rank=5, seed=3, scale=1e-80)
        d = np.sqrt(np.diag(C))
        rho = C / np.outer(d, d)
        off = ~np.eye(16, dtype=bool)
        for a in F.ALPHAS:
            S = F.shrink(C, a)
            np.testing.assert_allclose(S[off], (1 - a) * C[off], rtol=0, atol=0)
            literal = np.outer(d, d) * ((1 - a) * rho + a * np.eye(16))
            np.testing.assert_allclose(S, literal, rtol=1e-14, atol=0)

    def test_alpha_0_is_the_identity_and_alpha_1_the_diagonal(self):
        C = psd(seed=4)
        self.assertTrue(np.array_equal(F.shrink(C, 0.0), C))
        self.assertTrue(np.array_equal(F.shrink(C, 1.0), np.diag(np.diag(C))))
        self.assertIsNot(F.shrink(C, 0.0), C)

    def test_positive_semidefinite_is_kept(self):
        for rank in (1, 3, 16):
            C = psd(rank=rank, seed=rank)
            for a in F.ALPHAS:
                ev = np.linalg.eigvalsh(F.shrink(C, a))
                self.assertGreaterEqual(ev.min(), -1e-12 * ev.max(), (rank, a))

    def test_only_the_family_is_shrunk(self):
        B = {"stat": psd(seed=5), "interaction": psd(seed=6), "flux": psd(seed=7)}
        out = F.shrunk_blocks(B, ("interaction",), 0.5)
        self.assertIs(out["stat"], B["stat"])
        self.assertIs(out["flux"], B["flux"])
        self.assertTrue(np.array_equal(out["interaction"], F.shrink(B["interaction"], 0.5)))

    def test_the_declared_constants(self):
        self.assertEqual(F.CELLS, ("R04", "R00", "R01", "R07", "R08", "R09", "R10", "R14"))
        self.assertEqual(F.ALPHAS, (0.0, 0.1, 0.25, 0.5, 1.0))
        self.assertEqual(F.FAMILIES, {"interaction": ("interaction",), "c_e_systematic": (
            "interaction", "flux", "detector", "lateral")})
        self.assertEqual(set(D.GROUPS) - set(F.FAMILIES["c_e_systematic"]), {"stat", "seed", "normalization"})
        self.assertEqual(F.LEAD, 3)
        self.assertEqual(F.SENS_LABEL, "descriptive sensitivity of the reported χ², not an alternative result")
        self.assertEqual(F.FAMILY_ROLE, {"interaction": "primary", "c_e_systematic": "second"})

    def test_the_search_matches_whole_words_only(self):
        for k in ("data_b0_j100.npz", "expected_reco_signal", "mc_neff_truth", "nevt_flat", "n_mc_events_in_cells",
                  "union_purity", "Reco_Efficiency", "eff", "Data_Counts"):
            self.assertTrue(F.SEARCH.search(k), k)
        for k in ("recovery", "records", "coeff", "metadata", "eventually", "C_resp"):
            self.assertFalse(F.SEARCH.search(k), k)

    def test_each_searched_word_alone(self):
        words = ["data", "reco", "eff", "efficiency", "count", "counts", "nevt", "n_ev", "event", "events", "purity",
                 "stability", "truth", "signal", "accept", "acceptance"]
        self.assertEqual(F.SEARCH.pattern.count("|") + 1, len(words))
        for w in words:
            self.assertEqual(F.search({"x": [("zz", f"q_{w}_q")]}), {"x": [f"zz / q_{w}_q"]}, w)

    def test_key_paths_and_the_leaf_rule(self):
        self.assertEqual(F.key_paths([{"a": 1}, {"eff": 2}]), [("[]", "a"), ("[]", "eff")])
        self.assertEqual(F.key_paths([{"a": 1}, {"a": 2}]), [("[]", "a")])
        self.assertEqual(F.search({"x": [("data", "x"), ("y", "data")]}), {"x": ["y / data"]})
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        np.savez(tmp / "a.npz", C=np.eye(2), meta=json.dumps({"n_data": 1}), raw=np.bytes_(b'{"reco": 2}'),
                 note="not json")
        un = []
        self.assertEqual(F.npz_key_paths(tmp / "a.npz", un),
                         [("C",), ("meta",), ("meta", "n_data"), ("raw",), ("raw", "reco"), ("note",)])
        self.assertEqual(un, ["a.npz:note"])
        self.assertEqual(F.search({"a": F.npz_key_paths(tmp / "a.npz", [])}), {"a": ["meta / n_data", "raw / reco"]})

    def test_worst_rel_counts_equal_zeros_as_agreement(self):
        self.assertEqual(F.worst_rel([0.0, 1.0], [0.0, 1.0]), 0.0)
        self.assertEqual(F.worst_rel([0.0], [1e-300]), 1.0)
        self.assertAlmostEqual(F.worst_rel([1.0, 2.0], [1.0, 2.0 * (1 + 1e-9)]), 1e-9, delta=1e-15)
        self.assertEqual(F.worst_rel([np.nan], [np.nan]), float("inf"))
        self.assertEqual(F.worst_rel([1.0], [1.0, 1.0]), float("inf"))


# ------------------------------------------------------------------------------------------------ the definition


class Definition(unittest.TestCase):
    def test_r04s_neighbours_by_hand(self):
        got = {(n["neighbour"], n["axis"]) for n in F.neighbours(4, DEFN)}
        self.assertEqual(got, {("R00", "pz"), ("R12", "pt"), ("R06", "eavail"), ("R07", "eavail"), ("R05", "q3"),
                               ("unreported H2 box 10", "q3")})

    def test_every_listed_cells_reporting_neighbours_match_the_geometry(self):
        fm = sa.fine_map(DEFINITION)
        item1 = {c: F.definition_record(int(c[1:]), DEFN, fm) for c in F.CELLS}
        self.assertEqual(check_neighbours(item1), [])
        self.assertEqual(check_counts(item1, fm), [])

    def test_h2_boxes_rebuild_every_cells_box(self):
        for c in DEFN["reporting_cells"]:
            self.assertEqual(F.bounding_box([F.h2_box(b, sa.s1.H2_EDGES) for b in c["h2_cells"]]), c["box"])
        self.assertEqual(F.h2_box(10, sa.s1.H2_EDGES), {"pt": [0.0, 0.7], "pz": [4.5, 60.0], "eavail": [0.0, 0.8],
                                                        "q3": [2.0, 100.0], "W": [0.0, 1.8]})

    def test_the_definitions_search_fields(self):
        v = F.definition_values(DEFN)
        self.assertEqual(v["fields"], ["purity", "stability", "expected_reco_signal", "truth_selected",
                                       "mc_neff_truth"])
        self.assertIs(v["simulation_only"], True)
        self.assertEqual(v["cells"]["R04"]["purity"], DEFN["reporting_cells"][4]["purity"])
        for k in v["fields"]:
            self.assertEqual(v["median_over_16"][k], float(np.median([c[k] for c in DEFN["reporting_cells"]])))


# ------------------------------------------------------------------------------------------------ planted defects


class PlantedDefects(Base):
    """One or more per item. Each defect is patched into the tool's own function; the item's control or validator
    is silent on the correct output (EndToEnd) and reports the defect here."""

    def test_item_0_the_variant_comparisons_modes(self):
        tree = FollowupTree(self.tmp / "t").write()
        out = self.run_inproc(tree)
        gd = json.loads(tree.gd_readout.read_text())
        self.assertEqual(check_provenance(out["r04"]["provenance_g_diag_top_modes"], gd), [])
        (tree.out / "followup.json").unlink()
        for p in gd["predictions"]:
            p["comparisons"].reverse()
        bad = {p["name"]: p for p in gd["predictions"]}
        prov = {n: [{"mode": t["mode"], "loadings": t["loadings"]} for t in
                    bad[n]["comparisons"][0]["relative_to_f"]["top_modes"]] for n in out["r04"][
                        "provenance_g_diag_top_modes"]}
        self.assertTrue(check_provenance(prov, json.loads(tree.gd_readout.read_text())))

    def test_item_1_neighbours_across_two_axes(self):
        real = F.neighbours

        def two_axes(cell, defn):
            m = defn["h2_to_reporting_cell"]
            out = []
            for b in defn["reporting_cells"][cell]["h2_cells"]:
                for k in range(5):
                    for j in range(k + 1, 5):
                        nb = b ^ (1 << (4 - k)) ^ (1 << (4 - j))
                        if m[nb] >= 0 and m[nb] != cell:
                            out.append({"neighbour": f"R{m[nb]:02d}", "axis": sa.s1.AXES[k], "h2_pairs": []})
            return out + real(cell, defn)
        fm = sa.fine_map(DEFINITION)
        with mock.patch.object(F, "neighbours", two_axes):
            item1 = {c: F.definition_record(int(c[1:]), DEFN, fm) for c in F.CELLS}
        self.assertTrue(check_neighbours(item1))

    def test_item_1_fine_bins_counted_over_the_whole_grid(self):
        fm = sa.fine_map(DEFINITION)
        with mock.patch.object(F, "definition_record",
                               lambda c, d, fm: {"n_fine_bins": int(np.sum(fm >= c)), "neighbours": []}):
            item1 = {c: F.definition_record(int(c[1:]), DEFN, fm) for c in F.CELLS}
        self.assertTrue(check_counts(item1, fm))

    def test_item_1_the_h2_bit_order_reversed(self):
        tree = FollowupTree(self.tmp / "t").write()
        real = F.h2_box
        rev = lambda b, edges: real(int(f"{b:05b}"[::-1], 2), edges)  # noqa: E731
        with mock.patch.object(F, "h2_box", rev):
            self.assertStops(tree, "R1", "bounding box")

    def test_item_2_variance_not_sigma(self):
        tree = FollowupTree(self.tmp / "t").write()
        real = F.relative_sigma
        with mock.patch.object(F, "relative_sigma", lambda *a: {k: v ** 2 for k, v in real(*a).items()}):
            self.assertStops(tree, "R2", "S1's committed one")

    def test_item_2_not_divided_by_f(self):
        tree = FollowupTree(self.tmp / "t").write()
        real = F.relative_sigma

        def undivided(f, *a):
            out = real(f, *a)
            out["interaction"] = out["interaction"] * f
            return out
        with mock.patch.object(F, "relative_sigma", undivided):
            self.assertStops(tree, "R2", "S1's committed one")

    def test_item_2_median_over_the_listed_cells(self):
        rel = {"x": np.random.default_rng(1).uniform(0.01, 0.1, 16)}
        item2 = {"median_over_16": {"x": float(np.median(rel["x"][[int(c[1:]) for c in F.CELLS]]))}}
        self.assertTrue(check_medians(item2, rel))
        self.assertEqual(check_medians({"median_over_16": {"x": float(np.median(rel["x"]))}}, rel), [])

    def test_item_3_correlation_without_the_square_root(self):
        tree = FollowupTree(self.tmp / "t").write()
        with mock.patch.object(F, "correlation", lambda B, i, j: float(B[i, j] / (B[i, i] * B[j, j]))), \
                np.errstate(invalid="ignore"):
            self.assertStops(tree, "R3", "within [-1, 1]")

    def test_item_3_the_reported_covariance_without_c_resp(self):
        tree = FollowupTree(self.tmp / "t").write()
        real = F.correlation_matrices

        def no_x(groups, S, Cx, Ct, f, xn):
            m = real(groups, S, Cx, Ct, f, xn)
            m[f"C_total + {xn}"] = Ct
            return m
        with mock.patch.object(F, "correlation_matrices", no_x):
            self.assertStops(tree, "R3", "the blocks rebuild")

    def test_item_4_the_variants_pulls(self):
        tree = FollowupTree(self.tmp / "t").write()
        out = self.run_inproc(tree)
        g = {p["name"]: p for p in json.loads(tree.g_readout.read_text())["predictions"]}
        self.assertEqual(check_item4(out["r04"]["item4_stage_g"], g), [])
        real = F.prediction_cells

        def variant(rec):
            out = real(rec)
            for c, v in out.items():
                if v["compared"]:
                    v["pull"] = rec["variant"]["pulls"][rec["cells"].index(c)]
            return out
        bad = {n: {"cells": variant(g[n])} for n in g}
        self.assertTrue(check_item4(bad, g))

    def test_item_4_a_gibuu_value_formed_on_r04(self):
        tree = FollowupTree(self.tmp / "t").write()
        g = {p["name"]: p for p in json.loads(tree.g_readout.read_text())["predictions"]}
        real = F.prediction_cells

        def formed(rec):
            out = real(rec)
            for c, v in out.items():
                if not v["compared"]:
                    out[c] = {"compared": True, "pull": rec["pulls"][0], "g_over_f_minus_1": 0.0,
                              "sigma_Vg_over_f": 0.0, "n_mc_events": 0}
            return out
        bad = {n: {"cells": formed(g[n])} for n in g}
        self.assertIn("gibuu R04: a value where Stage G formed none", check_item4(bad, g))

    def test_item_4_a_readout_whose_pulls_do_not_follow_from_its_sigmas(self):
        def g_mutate(r):
            r["predictions"][0]["sigma_Vg_over_f"][3] *= 1.5     # D5 does not read sigma_Vg_over_f
        tree = FollowupTree(self.tmp / "t").write(g_mutate=g_mutate)
        self.assertStops(tree, "R4", "every reported pull")

    def test_item_5_a_case_sensitive_search(self):
        keys = {"x": [("C_resp",), ("Data_Counts",), ("meta", "Reco_Efficiency")]}
        want = {"x": ["Data_Counts", "meta / Reco_Efficiency"]}
        self.assertEqual(check_search(F.search(keys), want), [])
        with mock.patch.object(F, "SEARCH", __import__("re").compile(F.SEARCH.pattern)):
            self.assertTrue(check_search(F.search(keys), want))

    def test_item_5_a_dotted_key_is_one_key(self):
        keys = F.key_paths({"inputs_sha256": {"data_b0_j100.npz": "x", "lat_a.npz": "y"}})
        self.assertEqual(F.search({"s": keys}), {"s": ["inputs_sha256 / data_b0_j100.npz"]})

    def test_sens_the_diagonal_scaled_too(self):
        tree = FollowupTree(self.tmp / "t").write()
        with mock.patch.object(F, "shrink", lambda C, a: (1.0 - a) * C + a * 0.5 * np.diag(np.diag(C))):
            self.assertStops(tree, "S2", "diagonal")

    def test_sens_the_wrong_group_shrunk(self):
        tree = FollowupTree(self.tmp / "t").write()
        real = F.shrunk_blocks
        with mock.patch.object(F, "shrunk_blocks", lambda B, fam, a: real(B, tuple(
                "flux" if g == "interaction" else g for g in fam), a)):
            self.assertStops(tree, "S2", "(1 - alpha) times")

    def test_sens_a_group_outside_the_family_shrunk_too(self):
        tree = FollowupTree(self.tmp / "t").write()
        real = F.shrunk_blocks
        with mock.patch.object(F, "shrunk_blocks", lambda B, fam, a: real(B, (*fam, "stat"), a)):
            self.assertStops(tree, "S2", "outside the family")

    def test_sens_c_resp_dropped(self):
        tree = FollowupTree(self.tmp / "t").write()
        real = F.sens_record
        with mock.patch.object(F, "sens_record", lambda d, B, c: real(d, {k: v for k, v in B.items() if k != "C_resp"},
                                                                      c)):
            self.assertStops(tree, "S0", "alpha = 0 reproduces")

    def test_sens_an_indefinite_shrunk_matrix(self):
        tree = FollowupTree(self.tmp / "t").write()
        real = F.shrink
        with mock.patch.object(F, "shrink", lambda C, a: real(C, a) if a == 0 else -40.0 * C):
            self.assertStops(tree, "S1", "positive definite")

    def test_sens_the_modes_in_absolute_units(self):
        tree = FollowupTree(self.tmp / "t").write()
        out = self.run_inproc(tree)
        r = next(x for x in out["sens"]["records"] if x["prediction"] == "genie_cv" and x["alpha"] == 0.5
                 and x["family"] == "interaction")
        cells, d, B = self.by_hand(tree, "genie_cv", "interaction", 0.5)
        lam = np.linalg.eigvalsh(sum(B.values()))
        self.assertTrue(np.isclose(r["top_mode"]["sigma"] ** 2, lam, rtol=1e-9).any())
        fi = tree.f[np.asarray(cells)]
        lam_abs = np.linalg.eigvalsh(sum(B.values()) * np.outer(fi, fi))
        self.assertFalse(np.isclose(r["top_mode"]["sigma"] ** 2, lam_abs, rtol=1e-6).any())

    def test_sens_a_p_value(self):
        tree = FollowupTree(self.tmp / "t").write()
        out = self.run_inproc(tree)
        self.assertEqual(find_p(out), [])
        real = F.sens_record
        with mock.patch.object(F, "sens_record", lambda *a: {**real(*a), "p": 0.5}):
            (tree.out / "followup.json").unlink()
            out = self.run_inproc(tree)
        self.assertTrue(find_p(out["sens"]))

    def normalization_seen(self, tree):
        """Run the tool, capturing every block set it sums; return the second family's normalization blocks, per
        prediction and alpha, beside that prediction's unshrunk one built by hand."""
        calls, real = [], F.sens_record

        def spy(d, B, cells):
            calls.append((cells, B))
            return real(d, B, cells)
        with mock.patch.object(F, "sens_record", spy):
            self.run_inproc(tree)
        (tree.out / "followup.json").unlink()
        n = len(F.ALPHAS)
        fam2 = calls[len(tree.predictions) * n:]                  # FAMILIES order: interaction, then c_e_systematic
        out = []
        for k, spec in enumerate(tree.predictions):
            _, _, ref = self.by_hand(tree, spec["name"], "interaction", 0.0)
            out.append((spec["name"], ref["normalization"], [B["normalization"] for _, B in fam2[k * n:(k + 1) * n]]))
        return out

    def test_sens_normalization_is_bit_identical_in_every_second_family_matrix(self):
        tree = FollowupTree(self.tmp / "t").write()
        seen = self.normalization_seen(tree)
        self.assertEqual(len(seen), 5)
        for name, ref, blocks in seen:
            self.assertEqual(len(blocks), len(F.ALPHAS))
            for a, B in zip(F.ALPHAS, blocks):
                self.assertTrue(np.array_equal(B, blocks[0]), (name, a))
                np.testing.assert_allclose(B, ref, rtol=1e-12, atol=0)
                self.assertGreater(np.abs(B - np.diag(np.diag(B))).max(), 0)  # still fully correlated off-diagonal

    def test_sens_normalization_put_back_in_the_second_family(self):
        tree = FollowupTree(self.tmp / "t").write()
        fam = {**F.FAMILIES, "c_e_systematic": (*F.FAMILIES["c_e_systematic"], "normalization")}
        with mock.patch.object(F, "FAMILIES", fam):
            seen = self.normalization_seen(tree)
        self.assertTrue(any(not np.array_equal(B, blocks[0]) for _, _, blocks in seen for B in blocks))

    @staticmethod
    def by_hand(tree, name, fam, alpha):
        """The relative-to-f blocks of one prediction's reported M with the family shrunk, built from the tree."""
        cells = list(G.GIBUU_CELLS) if name == "gibuu" else list(range(16))
        i = np.asarray(cells)
        fi = tree.f[i]
        ff = np.outer(fi, fi)
        p = tree.preds[name]
        gc = p["g"][i]
        groups = {}
        for k, v in tree.blocks.items():
            groups[sa.group_of(k)] = groups.get(sa.group_of(k), 0) + v[np.ix_(i, i)] / ff
        B = {}
        for g, C in groups.items():
            if g in F.FAMILIES[fam]:
                C = (1 - alpha) * C + alpha * np.diag(np.diag(C))
            B[g] = C
        B["C_model"] = tree.Cmf[np.ix_(i, i)]
        B["C_resp"] = tree.Cx[np.ix_(i, i)] / ff
        B["V_g"] = np.diag(p["relvar"][i] * gc ** 2 / fi ** 2)
        return cells, (tree.f[i] - gc) / fi, B


# ------------------------------------------------------------------------------------------------ end to end


class EndToEnd(Base):
    def test_run_as_invoked_every_number_by_hand(self):
        tree = FollowupTree(self.tmp / "t").write()
        r = self.run_module(tree)
        self.assertEqual(r.returncode, 0, r.stderr[-3000:])
        for c in ("D0", "D1", "D2", "D3", "D4", "D5", "F0", "R1", "R2", "R3", "R4", "S0", "S1", "S2"):
            self.assertIn(f"PASS control {c} ", r.stdout)
        out = json.loads((tree.out / "followup.json").read_text())
        g = {p["name"]: p for p in json.loads(tree.g_readout.read_text())["predictions"]}
        gd = json.loads(tree.gd_readout.read_text())
        self.assertEqual(out["schema"], "fd-g-followup-readout/1")
        self.assertEqual(out["non_finite_written_as_null"], 0)
        self.assertEqual(find_p(out), [])
        r04 = out["r04"]
        # item 0
        self.assertEqual(check_provenance(r04["provenance_g_diag_top_modes"], gd), [])
        self.assertEqual(sorted(r04["provenance_g_diag_top_modes"]), ["genie_cv", "genie_mec", "mnvtune_v1", "nuwro"])
        # item 1
        fm = sa.fine_map(DEFINITION)
        self.assertEqual(check_neighbours(r04["item1_definition"]), [])
        self.assertEqual(check_counts(r04["item1_definition"], fm), [])
        for c, rec in r04["item1_definition"].items():
            cell = DEFN["reporting_cells"][int(c[1:])]
            self.assertEqual((rec["id"], rec["box"], rec["h2_boxes"]), (cell["id"], cell["box"], cell["h2_cells"]))
            self.assertEqual(rec["neighbours"], sorted(rec["neighbours"], key=lambda n: (n["neighbour"], n["axis"])))
            for n in rec["neighbours"]:
                for b, nb in n["h2_pairs"]:
                    self.assertIn(b, cell["h2_cells"])
                    self.assertNotIn(nb, cell["h2_cells"])
                    self.assertEqual(bin(b ^ nb).count("1"), 1)
        for name, tops in r04["provenance_g_diag_top_modes"].items():
            for t in tops:
                L = t["loadings"]
                ref = next(m for m in next(p for p in gd["predictions"] if p["name"] == name)["comparisons"][0][
                    "relative_to_f"]["top_modes"] if m["mode"] == t["mode"])["loadings"]
                self.assertEqual(t["rank_of_R04_by_abs_loading"],
                                 1 + sum(abs(v) > abs(ref["R04"]) for v in ref.values()))
                self.assertEqual(L, {c: ref[c] for c in F.CELLS})
        # item 2, by hand
        f = tree.f
        groups = {}
        for k, v in tree.blocks.items():
            groups[sa.group_of(k)] = groups.get(sa.group_of(k), 0) + v
        hand = {gname: np.sqrt(np.diag(C)) / f for gname, C in groups.items()}
        hand.update({f"C_model:{v}": np.abs(tree.S[j]) for j, v in enumerate(D.VERTICES)})
        hand.update({"C_resp": np.sqrt(np.diag(tree.Cx)) / f, "C_total": np.sqrt(np.diag(tree.Ct)) / f,
                     "C_total + C_resp": np.sqrt(np.diag(tree.Ct + tree.Cx)) / f,
                     "C_e": np.sqrt(np.diag(tree.Ce)) / f, "C_model": np.sqrt(np.diag(tree.Cmf))})
        it2 = r04["item2_relative_sigma"]
        self.assertEqual(set(it2), {*F.CELLS, "median_over_16"})
        for c in F.CELLS:
            self.assertEqual(set(it2[c]), set(hand))
            for k, v in hand.items():
                self.assertAlmostEqual(it2[c][k], v[int(c[1:])], delta=1e-12 * v[int(c[1:])])
        self.assertEqual(check_medians(it2, hand), [])
        # item 3, by hand
        it3 = r04["item3_correlation_with_R04"]

        def rho(B, j):
            return None if B[4, 4] * B[j, j] == 0 else B[4, j] / np.sqrt(B[4, 4] * B[j, j])
        ff = np.outer(f, f)
        mats = {"C_total + C_resp": tree.Ct + tree.Cx, "C_resp": tree.Cx, "C_total": tree.Ct,
                **{f"C_model:{v}": np.outer(tree.S[j], tree.S[j]) for j, v in enumerate(D.VERTICES)},
                **groups, "C_e": tree.Ce, "C_model": tree.Cmf * ff}
        self.assertEqual(set(it3["under"]), set(mats))
        for k, B in mats.items():
            for c in F.CELLS[1:]:
                want = rho(B, int(c[1:]))
                if want is None:
                    self.assertIsNone(it3["under"][k][c], (k, c))
                else:
                    self.assertAlmostEqual(it3["under"][k][c], want, delta=1e-12, msg=(k, c))
        self.assertEqual({c: it3["under"]["seed"][c] for c in F.CELLS[1:]}, dict.fromkeys(F.CELLS[1:]))
        self.assertEqual(it2["R04"]["seed"], 0.0)
        self.assertEqual({k: it3["rank"][k] for k in ("C_model:genie_mec", "C_model:nuwro", "C_model:gibuu",
                                                     "normalization", "seed", "C_total + C_resp")},
                         {"C_model:genie_mec": 1, "C_model:nuwro": 1, "C_model:gibuu": 1, "normalization": 1, "seed": 0,
                          "C_total + C_resp": 16})
        self.assertEqual(sorted(it3["under_prediction"]), ["genie_cv", "genie_mec", "mnvtune_v1", "nuwro"])
        for n, v in it3["under_prediction"].items():
            p = tree.preds[n]
            Mn = tree.Ct + tree.Cx + np.diag(p["relvar"] * p["g"] ** 2)
            self.assertEqual(v["matrix"], "C_total + C_resp + V_g")
            for c in F.CELLS[1:]:
                self.assertAlmostEqual(v[c], rho(Mn, int(c[1:])), delta=1e-12)
        # item 4
        it4 = r04["item4_stage_g"]
        self.assertEqual(check_item4(it4, g), [])
        self.assertEqual({c for c, v in it4["gibuu"]["cells"].items() if not v["compared"]}, {"R04", "R07", "R14"})
        for n in it4:
            self.assertEqual(it4[n]["matrix"], "C_total + C_resp + V_g")
            self.assertEqual(it4[n]["cells"]["R08"]["n_mc_events"], 7.0 * np.sum(fm == 8))
        # item 5
        it5 = r04["item5_search"]
        self.assertIn("reporting_cells / [] / expected_reco_signal", it5["matches"]["definition"])
        self.assertIn("predictions / [] / n_mc_events_in_cells", it5["matches"]["g_readout"])
        self.assertIn("nevt_flat", it5["matches"]["prediction:genie_cv"])
        self.assertEqual(it5["matches"]["extra_block"], [])
        self.assertEqual(it5["s5p_manifest_paths_matching"]["paths"], [])
        self.assertEqual(it5["definition_values"]["cells"]["R04"], {
            k: DEFN["reporting_cells"][4][k] for k in it5["definition_values"]["fields"]})
        # G-SENS, by hand
        recs = out["sens"]["records"]
        self.assertEqual(len(recs), 2 * 5 * 5)
        self.assertEqual(out["sens"]["unchanged"], ["stat", "seed", "normalization", "C_model:genie_mec",
                                                    "C_model:nuwro", "C_model:gibuu", "C_resp", "V_g"])
        for x in recs:
            cells, d, B = PlantedDefects.by_hand(tree, x["prediction"], x["family"], x["alpha"])
            M = sum(B.values())
            want = float(d @ np.linalg.solve(M, d))
            self.assertAlmostEqual(x["chi2"], want, delta=1e-9 * want)
            self.assertEqual(x["ndf"], len(cells))
            self.assertEqual(x["chi2_stage_g"], g[x["prediction"]]["total"]["chi2"])
            if x["alpha"] == 0:
                self.assertAlmostEqual(x["chi2"], x["chi2_stage_g"], delta=1e-10 * x["chi2_stage_g"])
            ev = np.sort(np.linalg.eigvalsh(M))[::-1]
            self.assertAlmostEqual(x["condition"], ev[0] / ev[-1], delta=1e-8 * ev[0] / ev[-1])
            self.assertAlmostEqual(x["lambda_min"], ev[-1], delta=1e-9 * ev[-1])
            w, V = np.linalg.eigh(M)
            c = (V.T @ d) ** 2 / w
            k = int(np.argmax(c))
            self.assertAlmostEqual(x["top_mode"]["sigma"], np.sqrt(w[k]), delta=1e-9 * np.sqrt(w[k]))
            self.assertAlmostEqual(x["top_mode"]["fraction"], c[k] / c.sum(), delta=1e-9)
            self.assertEqual(x["top_mode"]["mode"], len(cells) - 1 - k)          # eigh ascending, the tool descending
            self.assertAlmostEqual(x["top_mode"]["chi2"], c[k], delta=1e-9 * c[k])
            v = V[:, k] * np.sign(V[np.argmax(np.abs(V[:, k])), k])
            np.testing.assert_allclose(list(x["top_mode"]["loadings"].values()), v, atol=1e-9)
            self.assertEqual(list(x["top_mode"]["loadings"]), [f"R{j:02d}" for j in cells])
            self.assertEqual(x["cells"], [f"R{j:02d}" for j in cells])
            lead = [cells[j] for j in np.argsort(-np.abs(v))[:3]]
            self.assertEqual([y["cell"] for y in x["top_mode"]["leading_cells"]], [f"R{j:02d}" for j in lead])
            frac = np.cumsum(np.sort(c)[::-1]) / c.sum()
            self.assertEqual(x["modes_needed"], {f"{int(round(100 * q))}%": int(np.argmax(frac >= q - 1e-12) + 1)
                                                 for q in D.FRACTIONS})
            self.assertEqual(x["label"], F.SENS_LABEL)
            self.assertEqual(x["family_role"], F.FAMILY_ROLE[x["family"]])
            self.assertEqual(set(x["shrunk_group_lambda_min"]), set(F.FAMILIES[x["family"]]))
            for gname, lm in x["shrunk_group_lambda_min"].items():
                self.assertAlmostEqual(lm, np.linalg.eigvalsh(B[gname]).min(), delta=1e-9 * np.abs(B[gname]).max())
            self.assertFalse(x["stability"]["unstable"])
        # the shrinkage moves the chi2: alpha = 1 on the interaction group differs from alpha = 0
        a1 = next(x for x in recs if x["family"] == "interaction" and x["alpha"] == 1.0 and x["prediction"] == "nuwro")
        self.assertGreater(abs(a1["chi2"] - a1["chi2_at_alpha_0"]), 1e-6 * a1["chi2_at_alpha_0"])
        self.assertEqual(out["controls_passed"], ["D0", "D1", "D2", "D3", "D4", "D5", "F0", "R1", "R2", "R3", "R4",
                                                  "S0", "S1", "S2"])
        self.assertEqual(out["labels"], F.LABELS)
        self.assertIn("no p-value", out["labels"]["sens"])
        self.assertEqual(set(out["inputs_sha256"]), {*F.PINS, "definition", "extra_block",
                                                     *(p["name"] for p in tree.predictions)})
        lines = r.stdout.splitlines()
        r04l = [ln for ln in lines if ln.startswith("[G-R04]")]
        self.assertEqual(len(r04l), len(F.CELLS))
        for c, ln in zip(F.CELLS, r04l):
            self.assertTrue(ln.startswith(f"[G-R04] {c}: {r04['item1_definition'][c]['n_fine_bins']} fine bins"))
            if c != "R04":
                self.assertTrue(ln.endswith(f"rho(R04, {c}) {it3['under']['C_total + C_resp'][c]:+.3f}"), ln)
        for x in recs:                                         # each line read against its record, not summary_line
            ln = next(ln for ln in lines if ln.startswith(f"[G-SENS] {x['family']:14s} alpha {x['alpha']:<4g} "
                                                          f"{x['prediction']:10s}:"))
            self.assertIn(f"chi2 {x['chi2']:.2f}/{x['ndf']} (alpha 0: {x['chi2_at_alpha_0']:.2f})", ln)
            self.assertTrue(ln.endswith(", ".join(f"{y['cell']} {y['loading']:+.2f}"
                                                  for y in x["top_mode"]["leading_cells"])), ln)
        self.assertTrue(lines[-1].startswith('{"wrote": '))
        self.assertIn(f"[G-SENS] every line below: {F.SENS_LABEL}", lines)
        sl = [ln for ln in lines if ln.startswith("[G-SENS]") and "every line below" not in ln]
        self.assertEqual(sl, [F.summary_line(x["family"], x["alpha"], x["prediction"], x, x["chi2_at_alpha_0"])
                              for x in recs])
        self.assertEqual(sorted(p.name for p in tree.out.iterdir()), ["followup.json"])

    def test_the_sensitivity_role_reports_the_matrix_without_c_resp(self):
        tree = FollowupTree(self.tmp / "t").write(role="sensitivity")
        out = self.run_inproc(tree)
        g = {p["name"]: p for p in json.loads(tree.g_readout.read_text())["predictions"]}
        self.assertEqual(out["sens"]["reported_matrix"], "C_total + V_g")
        self.assertEqual(out["sens"]["unchanged"], ["stat", "seed", "normalization", "C_model:genie_mec",
                                                    "C_model:nuwro", "C_model:gibuu", "V_g"])
        for x in out["sens"]["records"]:
            if x["alpha"] == 0:
                self.assertAlmostEqual(x["chi2"], g[x["prediction"]]["total"]["chi2"],
                                       delta=1e-10 * x["chi2"])
        self.assertEqual(out["r04"]["item3_correlation_with_R04"]["under_prediction"]["nuwro"]["matrix"],
                         "C_total + V_g")
        self.assertEqual(check_item4(out["r04"]["item4_stage_g"], g), [])

    def test_a_non_finite_number_is_written_as_null_and_counted(self):
        tree = FollowupTree(self.tmp / "t").write()
        real = F.sens_record
        with mock.patch.object(F, "sens_record", lambda *a: {**real(*a), "condition": float("inf")}):
            out = self.run_inproc(tree)
        self.assertEqual(out["non_finite_written_as_null"], 50)
        self.assertIsNone(out["sens"]["records"][0]["condition"])

    def test_refuses_to_overwrite(self):
        tree = FollowupTree(self.tmp / "t").write()
        (tree.out / "followup.json").write_text("{}")
        with self.assertRaises(SystemExit):
            F.run(F.build_args(tree.fargv), tree.fpins, tree.predictions)


# ------------------------------------------------------------------------------------------------ controls


class Controls(Base):
    def test_d0_runs_first(self):
        tree = FollowupTree(self.tmp / "t").write()
        tree.fpins["g_readout"] = "0" * 64
        self.assertStops(tree, "D0", "g_readout")

    def test_f0_the_g_diag_readout_pin(self):
        tree = FollowupTree(self.tmp / "t").write()
        tree.fpins["g_diag_readout"] = "0" * 64
        self.assertStops(tree, "F0", "g_diag_readout")

    def test_f0_each_sub_check(self):
        for change, why in ((lambda r: r.update(schema="fd-g-diag-readout/0"), "schema"),
                            (lambda r: r["inputs_sha256"].update(g_readout="0" * 64), "Stage G readout"),
                            (lambda r: r["inputs_sha256"].update(extra_block="0" * 64), "extra block"),
                            (lambda r: r["predictions"].pop(), "the same predictions"),
                            (lambda r: r["predictions"][0]["comparisons"].reverse(), "comparison's matrix")):
            with self.subTest(why=why):
                tree = FollowupTree(self.tmp / "t").write()
                r = json.loads(tree.gd_readout.read_text())
                change(r)
                tree.gd_readout.write_text(json.dumps(r))
                tree.fpins["g_diag_readout"] = digest(tree.gd_readout)
                self.assertStops(tree, "F0", why)

    def test_r1_u_disagrees_with_the_fine_map(self):
        tree = FollowupTree(self.tmp / "t").write()
        real = D.load

        def bad(*a):
            x = real(*a)
            x.U = x.U.copy()
            x.U[4, np.nonzero(x.U[4])[0][0]] = 0
            return x
        with mock.patch.object(D, "load", bad):
            self.assertStops(tree, "R1", "U's nonzero")

    def test_r1_a_cell_not_reported(self):
        tree = FollowupTree(self.tmp / "t").write()
        real = D.load

        def bad(*a):
            x = real(*a)
            x.defn["reporting_cells"][1]["reported"] = False
            return x
        with mock.patch.object(D, "load", bad):
            self.assertStops(tree, "R1", "reported")

    def test_r1_a_fine_bin_mapped_outside_the_cells(self):
        tree = FollowupTree(self.tmp / "t").write()
        real = D.load

        def bad(*a):
            x = real(*a)
            x.fm = x.fm.copy()
            x.fm[np.nonzero(x.fm < 0)[0][0]] = 16
            return x
        with mock.patch.object(D, "load", bad):
            self.assertStops(tree, "R1", "cover the fine grid")

    def test_r2_item_2s_median_is_a_mean(self):
        tree = FollowupTree(self.tmp / "t").write()
        with mock.patch.object(F.np, "median", np.mean):
            self.assertStops(tree, "R2", "item 2's median")

    def test_r2_a_group_off_by_1e_9_or_a_median_missing(self):
        tree = FollowupTree(self.tmp / "t").write(s1_mutate=lambda j: j["relative_sigma"]["lateral"].__setitem__(
            4, j["relative_sigma"]["lateral"][4] * (1 + 1e-9)))
        self.assertStops(tree, "R2", "S1's committed one")
        tree = FollowupTree(self.tmp / "t").write(s1_mutate=lambda j: j["median_relative_sigma"].pop("seed"))
        self.assertStops(tree, "R2", "missing ['seed']")
        tree = FollowupTree(self.tmp / "t").write(s1_mutate=lambda j: j["relative_sigma"]["stat"].__setitem__(
            0, j["relative_sigma"]["stat"][0] * (1 + 1e-13)))
        with mock.patch("sys.stdout"):
            self.assertEqual(F.run(F.build_args(tree.fargv), tree.fpins, tree.predictions), 0)

    def test_r2_a_median_or_stage_gs_sigma_total_off_by_1e_9(self):
        tree = FollowupTree(self.tmp / "t").write(s1_mutate=lambda j: j["median_relative_sigma"].__setitem__(
            "flux", j["median_relative_sigma"]["flux"] * (1 + 1e-9)))
        self.assertStops(tree, "R2", "item 2's median")

        def g_mutate(r):
            r["predictions"][1]["sigma_total_over_f"][5] *= 1 + 1e-9         # D5 does not read sigma_total_over_f
        tree = FollowupTree(self.tmp / "t").write(g_mutate=g_mutate)
        self.assertStops(tree, "R2", "sigma_total_over_f")

    def test_r4_and_s0_tolerances(self):
        def g_mutate(r):
            r["predictions"][2]["sigma_Vg_over_f"][7] *= 1 + 1e-7
        tree = FollowupTree(self.tmp / "t").write(g_mutate=g_mutate)
        self.assertStops(tree, "R4", "every reported pull")
        tree = FollowupTree(self.tmp / "t").write()
        real = F.sens_record
        for eps, stops in ((1e-8, True), (1e-12, False)):
            def nudged(*a, eps=eps):
                r = real(*a)
                return {**r, "chi2": r["chi2"] * (1 + eps)}
            with mock.patch.object(F, "sens_record", nudged):
                if stops:
                    self.assertStops(tree, "S0", "alpha = 0 reproduces")
                else:
                    self.run_inproc(tree)

    def test_r2_vertices_do_not_sum_to_c_model(self):
        tree = FollowupTree(self.tmp / "t").write()
        real = F.relative_sigma

        def bad(*a):
            out = real(*a)
            out["C_model:nuwro"] = out["C_model:nuwro"] * 1.01
            return out
        with mock.patch.object(F, "relative_sigma", bad):
            self.assertStops(tree, "R2", "vertices' variances")

    def test_r2_not_stage_gs_sigma_total(self):
        tree = FollowupTree(self.tmp / "t").write()
        real = F.relative_sigma

        def bad(*a):
            out = real(*a)
            out["C_total + C_resp"] = out["C_total"]
            return out
        with mock.patch.object(F, "relative_sigma", bad):
            self.assertStops(tree, "R2", "sigma_total_over_f")


class Invocation(Base):
    def test_help_and_argparse_under_isolation(self):
        r = run_isolated([str(ND / "fd_g_followup.py"), "--help"])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("--g-diag-readout", r.stdout)
        tree = FollowupTree(self.tmp / "t").write()
        i = tree.fargv.index("--g-diag-readout")
        r = run_isolated([str(ND / "fd_g_followup.py"), *tree.fargv[:i], *tree.fargv[i + 2:]])
        self.assertEqual(r.returncode, 2, r.stderr)

    def test_the_real_script_reaches_d0_and_refuses_synthetic_records(self):
        tree = FollowupTree(self.tmp / "t").write()
        r = run_isolated([str(ND / "fd_g_followup.py"), *tree.fargv])
        self.assertEqual(r.returncode, 1, r.stderr[-2000:])
        self.assertIn("FAIL control D0:", r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertFalse((tree.out / "followup.json").exists())


class CommittedPins(unittest.TestCase):
    def test_the_g_diag_readout_pin_and_what_it_ran_on(self):
        p = FD / "fd/readout/fd_g_diag_readout.json"
        self.assertEqual(digest(p), F.PINS["g_diag_readout"])
        r = json.loads(p.read_text())
        self.assertEqual(r["schema"], "fd-g-diag-readout/1")
        self.assertEqual(r["inputs_sha256"]["g_readout"], D.PINS["g_readout"])
        self.assertEqual(r["inputs_sha256"]["extra_block"],
                         "4d8b579732b79cbbb8e6c9a4f6335c4bda4eae6dd4194241a0d8cd6e7ea8a20a")
        self.assertEqual({k: F.PINS[k] for k in D.PINS}, D.PINS)

    def test_r04_leads_the_top_modes_its_cells_load_in(self):
        """The cells are the director's: R04 is the largest-|loading| cell of a reported relative-to-f top mode of
        every 16-cell prediction, and each listed cell loads at |v| >= 0.25 in at least one of those modes."""
        r = json.loads((FD / "fd/readout/fd_g_diag_readout.json").read_text())
        led = {}
        for p in r["predictions"]:
            if p["name"] == "gibuu":
                continue
            tops = [t for t in p["comparisons"][0]["relative_to_f"]["top_modes"]
                    if max(t["loadings"], key=lambda c: abs(t["loadings"][c])) == "R04"]
            self.assertTrue(tops, p["name"])
            led[p["name"]] = tops
        for c in F.CELLS[1:]:
            self.assertTrue(any(abs(t["loadings"][c]) >= 0.25 for ts in led.values() for t in ts), c)

    def test_s1s_readout_carries_what_r2_checks(self):
        j = json.loads((FD / "s1/readout/s1_assembly.json").read_text())
        for k in (*D.GROUPS, "C_e", "C_model", "C_total"):
            self.assertEqual(len(j["relative_sigma"][k]), 16)
            self.assertIn(k, j["median_relative_sigma"])


# ------------------------------------------------------------------------------------------------ G-SENS2


class Sens2Tree(FollowupTree):
    """FollowupTree with G-FOLLOWUP run on it: its readout is the one G-SENS2 pins and references."""

    def write(self, mutate=None, role="adopted", g_mutate=None, s1_mutate=None, fu_mutate=None):
        super().write(mutate, role=role, g_mutate=g_mutate, s1_mutate=s1_mutate)
        self.fu_readout = self.root / "fd_g_followup_readout.json"
        argv = self.fargv[:-1] + [str(self.fu_readout)]
        with mock.patch("sys.stdout"):
            F.run(F.build_args(argv), self.fpins, self.predictions)
        if fu_mutate:
            r = json.loads(self.fu_readout.read_text())
            fu_mutate(r)
            self.fu_readout.write_text(json.dumps(r))
        self.spins = {**self.fpins, "g_followup_readout": digest(self.fu_readout)}
        i = self.fargv.index("--g-diag-readout")
        self.sargv = self.fargv[:i] + self.fargv[i + 2:-2] + [
            "--part", "sens2", "--g-followup-readout", str(self.fu_readout), "--out-json", str(self.out / "sens2.json")]
        return self

    def config(self):
        return {"nd": str(ND), "pins": self.spins, "predictions": self.predictions, "argv": self.sargv}


class Sens2Base(Base):
    def run_s2(self, tree):
        with mock.patch("sys.stdout"):
            self.assertEqual(F.run(F.build_args(tree.sargv), tree.spins, tree.predictions), 0)
        return json.loads((tree.out / "sens2.json").read_text())

    def assertStops2(self, tree, control, why=""):
        with self.assertRaises(SystemExit) as cm, mock.patch("sys.stdout"):
            F.run(F.build_args(tree.sargv), tree.spins, tree.predictions)
        self.assertIn(f"FAIL control {control}:", str(cm.exception.code))
        self.assertIn(why, str(cm.exception.code))
        self.assertFalse((tree.out / "sens2.json").exists(), "a refused run wrote its readout")


def by_hand2(tree, name, groups, alpha):
    """As PlantedDefects.by_hand, for any tuple of groups shrunk."""
    cells = list(G.GIBUU_CELLS) if name == "gibuu" else list(range(16))
    i = np.asarray(cells)
    fi = tree.f[i]
    ff = np.outer(fi, fi)
    p = tree.preds[name]
    gc = p["g"][i]
    grp = {}
    for k, v in tree.blocks.items():
        grp[sa.group_of(k)] = grp.get(sa.group_of(k), 0) + v[np.ix_(i, i)] / ff
    B = {g: ((1 - alpha) * C + alpha * np.diag(np.diag(C)) if g in groups else C) for g, C in grp.items()}
    for j, v in enumerate(D.VERTICES):
        B[f"C_model:{v}"] = np.outer(tree.S[j][i], tree.S[j][i])
    B["C_resp"] = tree.Cx[np.ix_(i, i)] / ff
    B["V_g"] = np.diag(p["relvar"][i] * gc ** 2 / fi ** 2)
    return cells, (tree.f[i] - gc) / fi, B


def check_shares(out, tree):
    """The flux family's top-mode shares at alpha 0 and 0.1, the followed alpha-0 mode and the overlap, by hand."""
    bad = []
    for name, by in out["flux_top_mode_shares"]["predictions"].items():
        vs = {}
        F = None
        for al in ("0", "0.1"):
            t = by[al]
            cells, d, B = by_hand2(tree, name, ("flux",), float(al))
            F = by_hand2(tree, name, (), 0.0)[2]["flux"]
            M = sum(B.values())
            w, V = np.linalg.eigh(M)
            c = (V.T @ d) ** 2 / w
            k = int(np.argmax(c))
            v = V[:, k] * np.sign(V[np.argmax(np.abs(V[:, k])), k])
            vs[al] = v
            for b, Bb in B.items():
                if not np.isclose(t["block_shares"][b], float(v @ Bb @ v / w[k]), rtol=1e-8, atol=1e-12):
                    bad.append(f"{name} alpha {al} {b}")
            if t["mode"] != len(cells) - 1 - k or not np.isclose(t["sigma"], np.sqrt(w[k]), rtol=1e-9):
                bad.append(f"{name} alpha {al}: mode or sigma")
            if not np.isclose(t["flux_ratio"], float(v @ F @ v / (v @ np.diag(np.diag(F)) @ v)), rtol=1e-9):
                bad.append(f"{name} alpha {al}: flux_ratio")
            want = {b: float(v @ Bb @ v / w[k]) for b, Bb in B.items()}
            if (t["dominant"] != max(want, key=want.get) or not np.isclose(t["chi2"], c[k], rtol=1e-9)
                    or not np.isclose(t["fraction"], c[k] / c.sum(), rtol=1e-9)
                    or not np.isclose(t["share_sum"], sum(want.values()), rtol=1e-9)):
                bad.append(f"{name} alpha {al}: dominant, chi2, fraction or share_sum")
        cells, d, B = by_hand2(tree, name, ("flux",), 0.1)
        v = vs["0"]
        q = float(v @ sum(B.values()) @ v)
        fol = by["alpha_0_mode_at_0.1"]
        fw = {b: float(v @ Bb @ v / q) for b, Bb in B.items()}
        if (not np.isclose(fol["variance_along"], q, rtol=1e-9) or fol["dominant"] != max(fw, key=fw.get)
                or not np.isclose(fol["flux_ratio"], float(v @ F @ v / (v @ np.diag(np.diag(F)) @ v)), rtol=1e-9)):
            bad.append(f"{name}: the followed mode's variance, dominant block or flux_ratio")
        if not np.isclose(fol["chi2_along"], float((v @ d) ** 2 / q), rtol=1e-9) or any(
                not np.isclose(fol["block_shares"][b], float(v @ Bb @ v / q), rtol=1e-8, atol=1e-12) for b, Bb in B.items()):
            bad.append(f"{name}: the followed mode")
        if not np.isclose(by["overlap_abs"], abs(float(vs["0"] @ vs["0.1"])), rtol=1e-9, atol=1e-12):
            bad.append(f"{name}: overlap")
    return bad


class Sens2(Sens2Base):
    def test_the_declared_constants(self):
        self.assertEqual(F.SENS2_FAMILIES, {"flux": ("flux",), "detector": ("detector",), "lateral": ("lateral",)})
        self.assertEqual(F.SENS2_ROLE, "single group")
        self.assertEqual(F.IDENTITY, (("interaction", 1.0, "nuwro"), ("c_e_systematic", 0.25, "gibuu")))
        self.assertEqual(F.SHARES, ("flux", (0.0, 0.1)))
        self.assertNotIn("g_followup_readout", F.PINS)
        self.assertEqual({k: v for k, v in F.SENS2_PINS.items() if k != "g_followup_readout"}, D.PINS)
        self.assertEqual(F.SENS2_PINS["g_followup_readout"],
                         "cd82517afdfb1dc8383580c8a4c57e82d9b87864e75d28528cb35c4455f6e379")
        self.assertFalse(set(F.SENS2_FAMILIES) & set(F.FAMILIES))

    def test_run_as_invoked_every_number_by_hand(self):
        tree = Sens2Tree(self.tmp / "t").write()
        r = self.run_module(tree)
        self.assertEqual(r.returncode, 0, r.stderr[-3000:])
        for c in ("D0", "D1", "D2", "D3", "D4", "D5", "H0", "H1", "S0", "S1", "S2", "H2"):
            self.assertIn(f"PASS control {c} ", r.stdout)
        for c in ("F0", "R1", "R2", "R3", "R4"):
            self.assertNotIn(f"control {c} ", r.stdout)
        out = json.loads((tree.out / "sens2.json").read_text())
        g = {p["name"]: p for p in json.loads(tree.g_readout.read_text())["predictions"]}
        fu = json.loads(tree.fu_readout.read_text())
        self.assertEqual(out["schema"], "fd-g-sens2-readout/1")
        self.assertEqual(out["controls_passed"], ["D0", "D1", "D2", "D3", "D4", "D5", "H0", "H1", "S0", "S1", "S2", "H2"])
        self.assertEqual(out["non_finite_written_as_null"], 0)
        self.assertEqual(find_p(out), [])
        self.assertEqual(out["referenced"]["g_followup_readout"], digest(tree.fu_readout))
        # H0's identity: the two records, equal to the G-FOLLOWUP readout's
        self.assertEqual([(x["family"], x["alpha"], x["prediction"]) for x in out["identity"]], list(F.IDENTITY))
        for x in out["identity"]:
            ref = next(r for r in fu["sens"]["records"] if (r["family"], r["alpha"], r["prediction"]) ==
                       (x["family"], x["alpha"], x["prediction"]))
            self.assertEqual(x["chi2_g_followup_readout"], ref["chi2"])
            self.assertLessEqual(x["relative_difference"], 1e-12)
        # no interaction or joint record is recomputed
        self.assertEqual({x["family"] for x in out["sens"]["records"]}, {"flux", "detector", "lateral"})
        recs = out["sens"]["records"]
        self.assertEqual(len(recs), 3 * 5 * 5)
        for fam, un in out["sens"]["unchanged"].items():
            self.assertNotIn(fam, un)
            self.assertIn("normalization", un)
            self.assertEqual(len(un), 7 + 3 + 1 + 1 - 1)
        for x in recs:
            cells, d, B = by_hand2(tree, x["prediction"], F.SENS2_FAMILIES[x["family"]], x["alpha"])
            M = sum(B.values())
            want = float(d @ np.linalg.solve(M, d))
            self.assertAlmostEqual(x["chi2"], want, delta=1e-9 * want)
            self.assertEqual(x["ndf"], len(cells))
            self.assertEqual(x["family_role"], "single group")
            self.assertEqual(x["label"], F.SENS_LABEL)
            self.assertEqual(set(x["shrunk_group_lambda_min"]), {x["family"]})
            if x["alpha"] == 0:
                self.assertAlmostEqual(x["chi2"], g[x["prediction"]]["total"]["chi2"], delta=1e-10 * x["chi2"])
            ev = np.sort(np.linalg.eigvalsh(M))[::-1]
            self.assertAlmostEqual(x["condition"], ev[0] / ev[-1], delta=1e-8 * ev[0] / ev[-1])
            w, V = np.linalg.eigh(M)
            c = (V.T @ d) ** 2 / w
            k = int(np.argmax(c))
            self.assertEqual(x["top_mode"]["mode"], len(cells) - 1 - k)
            self.assertAlmostEqual(x["top_mode"]["sigma"], np.sqrt(w[k]), delta=1e-9 * np.sqrt(w[k]))
            frac = np.cumsum(np.sort(c)[::-1]) / c.sum()
            self.assertEqual(x["modes_needed"], {f"{int(round(100 * q))}%": int(np.argmax(frac >= q - 1e-12) + 1)
                                                 for q in D.FRACTIONS})
            self.assertFalse(x["stability"]["unstable"])
        for x in recs:
            a0 = next(y for y in recs if (y["family"], y["prediction"], y["alpha"]) == (x["family"], x["prediction"], 0.0))
            self.assertEqual(x["chi2_at_alpha_0"], a0["chi2"])
        self.assertEqual(out["referenced"]["families"], {k: list(v) for k, v in F.FAMILIES.items()})
        self.assertEqual(out["constants"]["families"], {"flux": ["flux"], "detector": ["detector"], "lateral": ["lateral"]})
        self.assertEqual(out["constants"]["identity"], [["interaction", 1.0, "nuwro"], ["c_e_systematic", 0.25, "gibuu"]])
        self.assertEqual(out["sens"]["reported_matrix"], "C_total + C_resp + V_g")
        self.assertIn("not recomputed", out["labels"]["referenced"])
        self.assertEqual(out["labels"]["sens"], F.LABELS["sens"])
        # alpha = 1 on each family moves the chi2
        for fam in F.SENS2_FAMILIES:
            a1 = next(x for x in recs if x["family"] == fam and x["alpha"] == 1.0 and x["prediction"] == "genie_cv")
            self.assertGreater(abs(a1["chi2"] - a1["chi2_at_alpha_0"]), 1e-9 * a1["chi2_at_alpha_0"])
        # the addition
        sh = out["flux_top_mode_shares"]
        self.assertEqual((sh["family"], sh["alphas"]), ("flux", [0.0, 0.1]))
        self.assertEqual(sorted(sh["predictions"]), sorted(p["name"] for p in tree.predictions))
        self.assertEqual(check_shares(out, tree), [])
        lines = r.stdout.splitlines()
        self.assertIn(f"[G-SENS2] every line below: {F.SENS_LABEL}", lines)
        for x in recs:
            ln = next(ln for ln in lines if ln.startswith(f"[G-SENS] {x['family']:14s} alpha {x['alpha']:<4g} "
                                                          f"{x['prediction']:10s}:"))
            self.assertIn(f"chi2 {x['chi2']:.2f}/{x['ndf']}", ln)
        self.assertEqual(len([ln for ln in lines if ln.startswith("[G-SENS2] flux alpha ")]), 10)
        self.assertEqual(len([ln for ln in lines if ln.startswith("[G-SENS2] flux alpha-0 mode at 0.1")]), 5)
        for name, by in sh["predictions"].items():
            self.assertEqual(set(by), {"0", "0.1", "alpha_0_mode_at_0.1", "overlap_abs"})
            self.assertEqual(by["0"]["mode"], next(r for r in recs if r["family"] == "flux" and r["alpha"] == 0
                                                   and r["prediction"] == name)["top_mode"]["mode"])
        self.assertEqual(sorted(p.name for p in tree.out.iterdir()), ["sens2.json"])

    def test_normalization_and_every_other_block_bit_identical(self):
        tree = Sens2Tree(self.tmp / "t").write()
        calls, real = [], F.sens_record

        def spy(d, B, cells):
            calls.append(B)
            return real(d, B, cells)
        with mock.patch.object(F, "sens_record", spy):
            self.run_s2(tree)
        fam_calls = calls[len(F.IDENTITY):]                      # H0's two come first, then the families in order
        n = len(F.ALPHAS) * len(tree.predictions)
        self.assertEqual(len(fam_calls), 3 * n)
        for k, fam in enumerate(F.SENS2_FAMILIES):
            block = fam_calls[k * n:(k + 1) * n]
            for p in range(len(tree.predictions)):
                ref = block[p * len(F.ALPHAS)]                    # alpha = 0
                for B in block[p * len(F.ALPHAS):(p + 1) * len(F.ALPHAS)]:
                    for b in B:
                        if b != fam:
                            self.assertTrue(np.array_equal(B[b], ref[b]), (fam, b))
                    self.assertTrue(np.array_equal(np.diag(B[fam]), np.diag(ref[fam])))

    def test_refuses_to_overwrite(self):
        tree = Sens2Tree(self.tmp / "t").write()
        (tree.out / "sens2.json").write_text("{}")
        with self.assertRaises(SystemExit), mock.patch("sys.stdout"):
            F.run(F.build_args(tree.sargv), tree.spins, tree.predictions)


def _top_least(d, blocks, cells, Fl):
    """A defective top_mode_shares: the mode with the LEAST chi2."""
    M = sum(blocks.values())
    lam, V = D.eigen(M)
    _, c = D.mode_chi2(lam, V, d)
    t = int(np.argmin(c))
    v = V[:, t]
    sh = D.block_shares(v, lam[t], blocks)
    return {"mode": t, "sigma": float(np.sqrt(lam[t])), "chi2": float(c[t]), "fraction": float(c[t] / c.sum()),
            "loadings": dict(zip(cells, v.tolist())), "block_shares": sh, "share_sum": float(sum(sh.values())),
            "dominant": max(sh, key=sh.get), "flux_ratio": F.flux_ratio(v, Fl)}, v


class Sens2PlantedDefects(Sens2Base):
    """One per new item; each defect is patched into the tool and its control (or validator) reports it."""

    def test_flux_family_names_detector(self):
        tree = Sens2Tree(self.tmp / "t").write()
        with mock.patch.object(F, "SENS2_FAMILIES", {**F.SENS2_FAMILIES, "flux": ("detector",)}):
            self.assertStops2(tree, "H1", "exactly its own group")

    def test_detector_family_scales_the_diagonal(self):
        tree = Sens2Tree(self.tmp / "t").write()
        real = F.shrunk_blocks
        with mock.patch.object(F, "shrunk_blocks", lambda B, fam, a: {k: ((1 - a) * v if k in fam else v) for k, v in
                                                                      B.items()} if fam == ("detector",) else
                               real(B, fam, a)):
            self.assertStops2(tree, "S2", "diagonal")

    def test_lateral_family_shrinks_normalization_too(self):
        tree = Sens2Tree(self.tmp / "t").write()
        with mock.patch.object(F, "SENS2_FAMILIES", {**F.SENS2_FAMILIES, "lateral": ("lateral", "normalization")}):
            self.assertStops2(tree, "H1", "exactly its own group")
        real = F.shrunk_blocks
        with mock.patch.object(F, "shrunk_blocks", lambda B, fam, a: real(B, (*fam, "normalization"), a)
                               if fam == ("lateral",) else real(B, fam, a)):
            self.assertStops2(tree, "S2", "every block outside the family is unchanged")

    def test_identity_recomputed_with_the_wrong_family(self):
        tree = Sens2Tree(self.tmp / "t").write()
        real, n = F.shrunk_blocks, [0]

        def wrong_in_h0(B, fam, a):
            n[0] += 1
            return real(B, ("flux",) if n[0] <= len(F.IDENTITY) else fam, a)
        with mock.patch.object(F, "shrunk_blocks", wrong_in_h0):
            self.assertStops2(tree, "H0", "two G-FOLLOWUP chi2 values")

    def test_identity_against_a_tampered_readout(self):
        def fu_mutate(r):
            rec = next(x for x in r["sens"]["records"] if (x["family"], x["alpha"], x["prediction"]) == F.IDENTITY[0])
            rec["chi2"] *= 1 + 1e-8
        tree = Sens2Tree(self.tmp / "t").write(fu_mutate=fu_mutate)
        self.assertStops2(tree, "H0", "two G-FOLLOWUP chi2 values")

    def test_shares_not_divided_by_lambda(self):
        tree = Sens2Tree(self.tmp / "t").write()
        with mock.patch.object(D, "block_shares", lambda v, lam, B: {k: float(v @ b @ v) for k, b in B.items()}):
            self.assertStops2(tree, "H2", "sum to 1")

    def test_shares_of_the_mode_with_the_least_chi2(self):
        tree = Sens2Tree(self.tmp / "t").write()
        with mock.patch.object(F, "top_mode_shares", _top_least):
            self.assertStops2(tree, "H2", "the one its record carries")

    def test_shares_from_the_unshrunk_blocks(self):
        tree = Sens2Tree(self.tmp / "t").write()
        out = self.run_s2(tree)
        self.assertEqual(check_shares(out, tree), [])
        (tree.out / "sens2.json").unlink()
        real, n = F.shrunk_blocks, [0]
        before = len(F.IDENTITY) + 3 * len(F.ALPHAS) * len(tree.predictions)

        def unshrunk_in_the_shares(B, fam, a):
            n[0] += 1
            return real(B, fam, 0.0 if n[0] > before else a)
        with mock.patch.object(F, "shrunk_blocks", unshrunk_in_the_shares):
            self.assertStops2(tree, "H2", "the one its record carries")


class Sens2Controls(Sens2Base):
    def test_h0_the_pin(self):
        tree = Sens2Tree(self.tmp / "t").write()
        tree.spins["g_followup_readout"] = "0" * 64
        self.assertStops2(tree, "H0", "g_followup_readout")

    def test_h0_each_sub_check(self):
        for change, why in ((lambda r: r.update(schema="fd-g-followup-readout/0"), "differs in schema"),
                            (lambda r: r["inputs_sha256"].update(g_readout="0" * 64), "differs in Stage G readout"),
                            (lambda r: r["inputs_sha256"].update(extra_block="0" * 64), "differs in extra block"),
                            (lambda r: r["constants"]["families"].pop("interaction"), "differs in its families"),
                            (lambda r: r["constants"].update(alphas=[0.0, 1.0]), "differs in its alphas"),
                            (lambda r: r["sens"].update(reported_matrix="C_total + V_g"),
                             "differs in its reported matrix"),
                            (lambda r: r["inputs_sha256"].update(s1_npz="0" * 64), "differs in its shared input pins"),
                            (lambda r: r["inputs_sha256"].update(nuwro="0" * 64), "differs in its predictions"),
                            (lambda r: next(x for x in r["sens"]["records"] if (x["family"], x["alpha"],
                                            x["prediction"]) == F.IDENTITY[1]).update(chi2=None), "with a chi2"),
                            (lambda r: r["sens"].update(records=[]), "differs in its predictions")):
            with self.subTest(why=why):
                tree = Sens2Tree(self.tmp / "t").write(fu_mutate=change)
                self.assertStops2(tree, "H0", why)

    def test_s0_runs_on_the_new_families(self):
        tree = Sens2Tree(self.tmp / "t").write()
        real, calls = F.sens_record, [0]

        def drop_after_identity(d, B, c):
            calls[0] += 1
            return real(d, B if calls[0] <= len(F.IDENTITY) else {k: v for k, v in B.items() if k != "C_resp"}, c)
        with mock.patch.object(F, "sens_record", drop_after_identity):
            self.assertStops2(tree, "S0", "alpha = 0 reproduces")

    def test_s1_an_indefinite_shrunk_matrix(self):
        tree = Sens2Tree(self.tmp / "t").write()
        real = F.shrunk_blocks
        with mock.patch.object(F, "shrunk_blocks", lambda B, fam, a: {k: (-60.0 * v if k in fam else v) for k, v in
                                                                      B.items()} if fam == ("flux",) and a > 0 else
                               real(B, fam, a)):
            self.assertStops2(tree, "S1", "positive definite")


class Sens2Coverage(Sens2Base):
    """Review B's survivors, each killed by the test named for it."""

    def test_the_default_pins_are_sens2s(self):
        tree = Sens2Tree(self.tmp / "t").write()
        with mock.patch.object(F, "SENS2_PINS", tree.spins), mock.patch("sys.stdout"):
            self.assertEqual(F.run(F.build_args(tree.sargv), None, tree.predictions), 0)

    def test_identity_fields_below_the_tolerance(self):
        def fu_mutate(r):
            rec = next(x for x in r["sens"]["records"] if (x["family"], x["alpha"], x["prediction"]) == F.IDENTITY[0])
            rec["chi2"] *= 1 + 1e-13
        tree = Sens2Tree(self.tmp / "t").write(fu_mutate=fu_mutate)
        out = self.run_s2(tree)
        fu = json.loads(tree.fu_readout.read_text())
        ref = next(x for x in fu["sens"]["records"] if (x["family"], x["alpha"], x["prediction"]) == F.IDENTITY[0])
        i0 = out["identity"][0]
        self.assertEqual(i0["chi2_g_followup_readout"], ref["chi2"])
        self.assertNotEqual(i0["chi2_recomputed"], ref["chi2"])
        self.assertAlmostEqual(i0["relative_difference"], abs(i0["chi2_recomputed"] - ref["chi2"]) / ref["chi2"],
                               delta=1e-18)
        self.assertGreater(i0["relative_difference"], 1e-14)

    def test_h0_refuses_a_recomputed_chi2_that_is_none(self):
        tree = Sens2Tree(self.tmp / "t").write()
        real, n = F.sens_record, [0]

        def none_in_h0(d, B, c):
            n[0] += 1
            return {**real(d, B, c), "chi2": None} if n[0] <= len(F.IDENTITY) else real(d, B, c)
        with mock.patch.object(F, "sens_record", none_in_h0):
            self.assertStops2(tree, "H0", "two G-FOLLOWUP chi2 values")

    def test_s2_one_ulp_on_a_diagonal_an_off_diagonal_and_an_extra_block(self):
        tree = Sens2Tree(self.tmp / "t").write()
        real = F.shrunk_blocks

        def ulp(B, fam, a):
            out = real(B, fam, a)
            if fam == ("flux",) and a > 0:
                C = out["flux"].copy()
                C[3, 3] = np.nextafter(C[3, 3], np.inf)
                out["flux"] = C
            return out

        def off(B, fam, a):
            out = real(B, fam, a)
            if fam == ("detector",) and a > 0:
                C = out["detector"].copy()
                C[0, 1] *= 1 + 1e-9
                C[1, 0] *= 1 + 1e-9
                out["detector"] = C
            return out

        def extra(B, fam, a):
            out = real(B, fam, a)
            if fam == ("lateral",) and a > 0:
                out = {**out, "extra": 1e-6 * np.eye(len(next(iter(out.values()))))}
            return out
        for patch, why in ((ulp, "diagonal"), (off, "(1 - alpha) times"), (extra, "diagonal")):
            with self.subTest(why=why), mock.patch.object(F, "shrunk_blocks", patch):
                self.assertStops2(tree, "S2", why)

    def test_h2_tolerance_followed_shares_and_a_flipped_loading(self):
        tree = Sens2Tree(self.tmp / "t").write()
        real_f, real_t = F.followed_mode, F.top_mode_shares

        def fol_bad(v, d, B, Fl):
            r = real_f(v, d, B, Fl)
            return {**r, "share_sum": r["share_sum"] * (1 + 1e-6)}

        def flip(d, B, c, Fl):
            r, v = real_t(d, B, c, Fl)
            k = c[0]
            return {**r, "loadings": {**r["loadings"], k: -r["loadings"][k]}}, v

        def shares_bad(d, B, c, Fl):
            r, v = real_t(d, B, c, Fl)
            return {**r, "share_sum": r["share_sum"] * (1 + 1e-6)}, v
        for name, patch, why in (("followed_mode", fol_bad, "sum to 1"), ("top_mode_shares", flip, "carries"),
                                 ("top_mode_shares", shares_bad, "sum to 1")):
            with self.subTest(why=why), mock.patch.object(F, name, patch):
                self.assertStops2(tree, "H2", why)

    def test_h1_refuses_a_family_named_for_a_forbidden_group(self):
        tree = Sens2Tree(self.tmp / "t").write()
        for fam in ({"normalization": ("normalization",)}, {"stat": ("stat",)}, {"interaction": ("interaction",)}):
            with self.subTest(fam=fam), mock.patch.object(F, "SENS2_FAMILIES", {**F.SENS2_FAMILIES, **fam}):
                self.assertStops2(tree, "H1", "exactly its own group")

    def test_the_sensitivity_role_leaves_c_resp_out_of_unchanged(self):
        tree = Sens2Tree(self.tmp / "t").write(role="sensitivity")
        out = self.run_s2(tree)
        self.assertEqual(out["sens"]["reported_matrix"], "C_total + V_g")
        for un in out["sens"]["unchanged"].values():
            self.assertNotIn("C_resp", un)
            self.assertIn("normalization", un)


class Sens2Invocation(Sens2Base):
    def test_part_sens2_needs_the_followup_readout_and_followup_needs_g_diag(self):
        tree = Sens2Tree(self.tmp / "t").write()
        i = tree.sargv.index("--g-followup-readout")
        r = run_isolated([str(ND / "fd_g_followup.py"), *tree.sargv[:i], *tree.sargv[i + 2:]])
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("--part sens2 requires --g-followup-readout", r.stderr)
        j = tree.fargv.index("--g-diag-readout")
        r = run_isolated([str(ND / "fd_g_followup.py"), *tree.fargv[:j], *tree.fargv[j + 2:]])
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("--part followup requires --g-diag-readout", r.stderr)
        r = run_isolated([str(ND / "fd_g_followup.py"), *tree.sargv, "--g-diag-readout", "x.json"])
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("--part sens2 does not read --g-diag-readout", r.stderr)

    def test_the_real_script_reaches_d0_and_refuses_synthetic_records(self):
        tree = Sens2Tree(self.tmp / "t").write()
        r = run_isolated([str(ND / "fd_g_followup.py"), *tree.sargv])
        self.assertEqual(r.returncode, 1, r.stderr[-2000:])
        self.assertIn("FAIL control D0:", r.stderr)
        self.assertNotIn("Traceback", r.stderr)


class Sens2CommittedPins(unittest.TestCase):
    def test_the_g_followup_readout_pin_and_the_identity_records(self):
        p = FD / "fd/readout/fd_g_followup_readout.json"
        self.assertEqual(digest(p), F.SENS2_PINS["g_followup_readout"])
        r = json.loads(p.read_text())
        self.assertEqual(r["constants"]["families"], {k: list(v) for k, v in F.FAMILIES.items()})
        keys = {(x["family"], x["alpha"], x["prediction"]) for x in r["sens"]["records"]}
        self.assertTrue(set(F.IDENTITY) <= keys)
        self.assertEqual({k: r["inputs_sha256"][k] for k in D.PINS}, D.PINS)


if __name__ == "__main__":
    unittest.main()
