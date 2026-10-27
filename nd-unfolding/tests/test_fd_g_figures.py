"""Controls for fd_g_figures (FD-G-FIGURES-DECLARATION.md section 6), on synthetic readouts with Stage G's, G-DIAG's,
G-FOLLOWUP's, G-SENS2's and F0b's key layout. No committed readout is drawn: the committed readouts are read only for
their digests, schemas and the K1 chain (CommittedPins). The H2 definition is the committed one (simulation-only and
pinned).

* End to end: every drawn number is read back from the figure's artists and asserted against the value at its key
  in the synthetic readouts, recomputed here from the JSON, not from the tool's model; every printed number is parsed
  from its text and asserted to its printed precision; the sidecar's digests are the files'.
* Planted defects: each control K0-K8 refuses, with nothing written, on a defective input or a defective drawing.
* Invocation: as written (-I -B, cwd outside nd-unfolding), the real pins refuse the synthetic readouts at K0."""
import copy
import json
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
sys.path.insert(1, str(Path(__file__).resolve().parent))
import fd_g_compare as G  # noqa: E402
import fd_g_figures as F  # noqa: E402
from test_fd_g_compare import DEFINITION, digest, run_isolated  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402
from matplotlib.colors import to_hex  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

REPO = ND.parent
FD = REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout"
COMMITTED = {"g_readout": FD / "fd_g_readout.json", "g_diag_readout": FD / "fd_g_diag_readout.json",
             "g_followup_readout": FD / "fd_g_followup_readout.json", "g_sens2_readout": FD / "fd_g_sens2_readout.json",
             "f0b_readout": FD / "fd_f0b_readout.json", "definition": DEFINITION}
CELLS = [f"R{c:02d}" for c in range(16)]
GIB = [f"R{c:02d}" for c in G.GIBUU_CELLS]
XB_SHA = "ab" * 32
# the fixture's own literals, not the tool's constants, so a change to the tool's is seen
REPORTED = "C_total + C_resp + V_g"
SENS_LABEL = "descriptive sensitivity of the reported \u03c7\u00b2, not an alternative result"
ALPHAS = (0.0, 0.1, 0.25, 0.5, 1.0)
S1_SHA = "cd" * 32


def modes(seed: int, n: int) -> tuple[list, list, float]:
    """G-DIAG's relative_to_f records for a random M and d: modes ranked by chi2, the top three with loadings."""
    rng = np.random.default_rng(seed)
    A = rng.normal(size=(n, n))
    M = A @ A.T * 1e-3 + np.eye(n) * 1e-4
    d = rng.normal(size=n) * 0.05
    lam, V = np.linalg.eigh(M)
    lam, V = lam[::-1], V[:, ::-1]
    V = V * np.sign(V[np.argmax(np.abs(V), axis=0), np.arange(n)])
    proj = V.T @ d
    chi2 = proj ** 2 / lam
    tot = float(chi2.sum())
    order = np.argsort(-chi2, kind="stable")
    ranked, cum = [], 0.0
    for k in order:
        cum += chi2[k] / tot
        ranked.append({"mode": int(k), "lambda": float(lam[k]), "sigma": float(np.sqrt(lam[k])),
                       "projection": float(proj[k]), "chi2": float(chi2[k]), "fraction": float(chi2[k] / tot),
                       "cumulative": cum})
    cells = CELLS if n == 16 else GIB
    top = [{"mode": m["mode"], "sigma": m["sigma"], "chi2": m["chi2"], "fraction": m["fraction"],
            "loadings": dict(zip(cells, V[:, m["mode"]].tolist()))} for m in ranked[:3]]
    return top, ranked, tot


class FigTree:
    """Six synthetic readouts, consistent with one another as the committed ones are."""

    def __init__(self, root: Path, seed: int = 0):
        self.root = root
        self.definition = DEFINITION
        rng = np.random.default_rng(seed)
        f = rng.uniform(1, 5, 16) * 1e-39
        s_ct = rng.uniform(0.04, 0.12, 16)
        s_cr = rng.uniform(0.005, 0.04, 16)
        s_tot = np.sqrt(s_ct ** 2 + s_cr ** 2)
        self.diag_modes = {}
        preds = []
        for i, spec in enumerate(G.PREDICTIONS):
            cells = CELLS if spec["cells"] == "all" else GIB
            idx = [int(c[1:]) for c in cells]
            g = f[idx] * (1 + rng.normal(0, 0.12, len(idx)))
            top, ranked, tot = modes(seed * 10 + i, len(idx))
            self.diag_modes[spec["name"]] = (top, ranked)
            preds.append({"name": spec["name"], "label": spec["label"], "sha256": spec["sha256"], "cells": cells,
                          "reported_covariance": "C_total + C_resp", "f": f[idx].tolist(), "g": g.tolist(),
                          "g_over_f_minus_1": (g / f[idx] - 1).tolist(), "sigma_total_over_f": s_tot[idx].tolist(),
                          "total": {"chi2": tot, "ndf": len(idx), "matrix": REPORTED},
                          "variant": {"covariance": "C_total", "sigma_total_over_f": s_ct[idx].tolist()}})
        names = {p["name"]: p["sha256"] for p in preds}
        self.g = {"schema": "fd-g-readout/2", "cells": CELLS, "predictions": preds,
                  "extra_block": {"name": "C_resp", "role": "adopted", "sha256": XB_SHA,
                                  "relative_sigma": s_cr.tolist()},
                  "inputs_sha256": {"s1_npz": S1_SHA, "definition": digest(self.definition), **names}}
        self.write_all()

    def ins(self, **extra) -> dict:
        return {"s1_npz": S1_SHA, "definition": digest(self.definition), "extra_block": XB_SHA,
                **{p["name"]: p["sha256"] for p in self.g["predictions"]}, **extra}

    def write(self, key: str, obj: dict) -> None:
        (self.root / f"{key}.json").write_text(json.dumps(obj, indent=1))
        self.pins[key] = digest(self.root / f"{key}.json")

    def write_all(self) -> None:
        self.pins = {"definition": digest(self.definition)}
        self.write("g_readout", self.g)
        preds = []
        for p in self.g["predictions"]:
            top, ranked = self.diag_modes[p["name"]]
            preds.append({"name": p["name"], "label": p["label"], "cells": p["cells"], "comparisons": [
                {"comparison": "reported", "matrix": REPORTED, "chi2_stage_g": p["total"]["chi2"],
                 "relative_to_f": {"top_modes": top, "modes_by_chi2": ranked}},
                {"comparison": "variant", "matrix": "C_total + V_g", "chi2_stage_g": 0.0, "relative_to_f": {}}]})
        self.dg = {"schema": "fd-g-diag-readout/1", "constants": {"top": 3}, "predictions": preds,
                   "inputs_sha256": self.ins(g_readout=self.pins["g_readout"])}
        self.write("g_diag_readout", self.dg)
        fams = {"interaction": ["interaction"], "c_e_systematic": ["interaction", "flux", "detector", "lateral"]}
        self.fu = {"schema": "fd-g-followup-readout/1", "constants": {"alphas": list(ALPHAS), "families": fams},
                   "sens": {"reported_matrix": REPORTED, "label": SENS_LABEL,
                            "records": self.records(("interaction", "c_e_systematic"), 1)},
                   "inputs_sha256": self.ins(g_readout=self.pins["g_readout"],
                                             g_diag_readout=self.pins["g_diag_readout"])}
        self.write("g_followup_readout", self.fu)
        self.s2 = {"schema": "fd-g-sens2-readout/1",
                   "constants": {"alphas": list(ALPHAS), "families": {k: [k] for k in ("flux", "detector",
                                                                                          "lateral")}},
                   "referenced": {"g_followup_readout": self.pins["g_followup_readout"],
                                  "families": copy.deepcopy(fams)},
                   "sens": {"reported_matrix": REPORTED, "label": SENS_LABEL,
                            "records": self.records(("flux", "detector", "lateral"), 2)},
                   "inputs_sha256": self.ins(g_readout=self.pins["g_readout"],
                                             g_followup_readout=self.pins["g_followup_readout"])}
        self.write("g_sens2_readout", self.s2)
        p0 = self.g["predictions"][0]
        self.b = {"schema": "fd-f0b-readout/1", "inputs_sha256": {"s1_npz": S1_SHA,
                                                                 "definition": digest(self.definition)},
                  "extra_block": {"sha256": XB_SHA, "relative_sigma": self.g["extra_block"]["relative_sigma"]},
                  "relative_sigma_plus_C_resp": {"C_total": p0["sigma_total_over_f"]}}
        self.write("f0b_readout", self.b)

    def records(self, families, seed) -> list:
        rng = np.random.default_rng(100 + seed)
        out = []
        for fam in families:
            for p in self.g["predictions"]:
                c0 = p["total"]["chi2"]
                for a in ALPHAS:
                    out.append({"family": fam, "alpha": a, "prediction": p["name"], "ndf": p["total"]["ndf"],
                                "chi2": c0 if a == 0 else c0 * (1 - a * rng.uniform(0.1, 0.6)),
                                "label": SENS_LABEL})
        rng.shuffle(out)
        return out

    def paths(self) -> dict:
        return {k: (self.root / f"{k}.json" if k != "definition" else self.definition) for k in F.INPUTS}

    def argv(self, out: Path, figures=("ratio", "modes", "sens"), form=None) -> list:
        a = []
        for k, p in self.paths().items():
            a += ["--" + k.replace("_", "-"), str(p)]
        a += ["--figures", *figures, "--out-dir", str(out)]
        return a + (["--ratio-form", form] if form else [])


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fd-fig-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(plt.close, "all")
        (self.tmp / "in").mkdir()
        self.tree = FigTree(self.tmp / "in")
        self.out = self.tmp / "out"

    def run_tool(self, figures=("ratio", "modes", "sens"), form=None, pins=None):
        a = F.build_args(self.tree.argv(self.out, figures, form))
        return F.run(a, pins=self.tree.pins if pins is None else pins)

    def refuses(self, control, clause=None, **kw):
        with self.assertRaises(SystemExit) as cm:
            self.run_tool(**kw)
        msg = str(cm.exception)
        self.assertIn(f"FAIL control {control}", msg)
        if clause:
            self.assertIn(clause, msg)
        self.assertFalse(self.out.exists() and any(self.out.iterdir()), "something was written")
        return msg

    def rewrite(self, key, fn, rechain=True):
        """Plant a defect in one readout; with rechain, the readouts made from it are re-pinned to it, so that the
        chain (K1) holds and only the planted defect can fire."""
        t = self.tree
        objs = {"g_readout": t.g, "g_diag_readout": t.dg, "g_followup_readout": t.fu, "g_sens2_readout": t.s2,
                "f0b_readout": t.b}
        fn(objs[key])
        t.write(key, objs[key])
        if not rechain:
            return
        for k in ("g_diag_readout", "g_followup_readout", "g_sens2_readout"):
            ins = objs[k]["inputs_sha256"]
            for up in ("g_readout", "g_diag_readout", "g_followup_readout"):
                if up in ins:
                    ins[up] = t.pins[up]
            if "referenced" in objs[k]:
                objs[k]["referenced"]["g_followup_readout"] = t.pins["g_followup_readout"]
            t.write(k, objs[k])


def drawn(fig) -> dict:
    out = {}
    for a in fig.findobj(lambda o: o.get_gid() is not None):
        out.setdefault(a.get_gid(), []).append(a)
    return out


def numbers(text: str) -> list[float]:
    return [float(x) for x in re.findall(r"[-+]?\d+(?:\.\d+)?", text)]


# literal expectations, written out here rather than taken from the tool's constants
LEGENDS = {"genie_cv": "GENIE 2.12.10 CV, no MEC", "genie_mec": "GENIE 2.12.10 + Valencia MEC",
           "nuwro": "NuWro 21.09: $^{12}$C target; no correction to CH applied",
           "gibuu": "GiBUU 2019: $^{12}$C target; no correction to CH applied; $p_\\parallel$ < 4.5 cells only",
           "mnvtune_v1": "MINERvA Tune v1: prior (not an independent prediction)"}
STYLE = {"genie_cv": ("#2a78d6", "o"), "genie_mec": ("#eb6834", "s"), "nuwro": ("#1baf7a", "^"),
         "gibuu": ("#4a3aa7", "D"), "mnvtune_v1": ("#6b6b6b", "v")}


class EndToEnd(Base):
    """Every drawn number against the synthetic readouts' keys, recomputed here."""

    def figure(self, name, form=F.RATIO_FORMS[0], axis=F.GIBUU_AXES[0]):
        F.MF.style()
        r = {k: json.loads(Path(p).read_text()) for k, p in self.tree.paths().items()}
        model = F.MODEL[name](r, mock.Mock(ratio_form=form, gibuu_axis=axis))
        return F.draw(name, model), model

    def test_runs_and_writes_three_figures_with_sidecars(self):
        self.assertEqual(self.run_tool(), 0)
        for n in F.FIGURES:
            pdf, side = self.out / f"{F.NAMES[n]}.pdf", self.out / f"{F.NAMES[n]}.json"
            s = json.loads(side.read_text())
            self.assertEqual(s["pdf_sha256"], digest(pdf))
            self.assertEqual(s["inputs_sha256"], {k: self.tree.pins[k] for k in F.INPUTS})
            for f, p in (("fd_g_figures.py", ND / "fd_g_figures.py"), ("s1_assemble.py", ND / "s1_assemble.py"),
                         ("make_figs.py", REPO / "publication/release/figs/make_figs.py")):
                self.assertEqual(s["code"]["sha256"][f], digest(p))
            self.assertEqual(s["controls_passed"], ["K0", "K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8"])
            self.assertEqual(s["schema"], "fd-g-figure-sidecar/1")
            self.assertEqual(s["options"], {"ratio_form": "data-over-prediction", "gibuu_axis": "separate"})
            self.assertEqual(s["plotted"]["figure"], n)
            self.assertNotIn("p", json.dumps(s["plotted"]).replace('"', " ").split())
            b = pdf.read_bytes()
            self.assertTrue(b.startswith(b"%PDF"))
            self.assertNotIn(b"/Subtype /Image", b)
        self.assertFalse(list(self.out.glob("*.partial")))

    def test_ratio_data_over_prediction_against_the_keys(self):
        for axis in F.GIBUU_AXES:
            fig, _ = self.figure("ratio", axis=axis)
            D_ = drawn(fig)
            for p in self.tree.g["predictions"]:
                n = p["name"]
                idx = [int(c[1:]) for c in p["cells"]]
                f, g, s = (np.array(p[k]) for k in ("f", "g", "sigma_total_over_f"))
                (ln,) = D_[f"ratio:{n}"]
                xy = ln.get_xydata()
                np.testing.assert_array_equal(np.round(xy[:, 0]), idx)
                np.testing.assert_allclose(xy[:, 1], f / g, rtol=1e-14)
                np.testing.assert_allclose(xy[:, 1], 1 / (1 + np.array(p["g_over_f_minus_1"])), rtol=1e-12)
                (lc,) = D_[f"ratio:{n}:err"]
                seg = np.array(lc.get_segments())
                np.testing.assert_array_equal(seg[:, 0, 0], xy[:, 0])
                np.testing.assert_allclose(seg[:, 0, 1], f / g - (f / g) * s, rtol=1e-14)
                np.testing.assert_allclose(seg[:, 1, 1], f / g + (f / g) * s, rtol=1e-14)
                # the bar is C_total + C_resp: its square is the variant's plus C_resp's
                xb = np.array(self.tree.g["extra_block"]["relative_sigma"])[idx]
                np.testing.assert_allclose(((seg[:, 1, 1] - seg[:, 0, 1]) / 2 / xy[:, 1]) ** 2,
                                           np.array(p["variant"]["sigma_total_over_f"]) ** 2 + xb ** 2, rtol=1e-12)
                self.assertEqual(D_[f"ratio:{n}:legend"][0].get_text(), LEGENDS[n])
                self.assertEqual((to_hex(ln.get_color()), ln.get_marker(), ln.get_linestyle()),
                                 (*STYLE[n], "None"))
                self.assertEqual(to_hex(lc.get_colors()[0]), STYLE[n][0])
                want_axes = 1 if (n == "gibuu" and axis == "separate") else 0
                self.assertIs(ln.axes, fig.axes[want_axes])
                self.assertIs(lc.axes, fig.axes[want_axes])
            self.assertEqual(len(fig.axes), 2 if axis == "separate" else 1)
            self.assertFalse(any(g.startswith("ratio:data") for g in D_))
            leg = fig.legends[0]
            for h, t in zip(leg.legend_handles, leg.get_texts()):
                n = next(k for k, v in LEGENDS.items() if v == t.get_text())
                self.assertEqual((to_hex(h.get_color()), h.get_marker()), STYLE[n])
            plt.close(fig)

    def test_gibuu_has_nothing_above_p_parallel_4_5(self):
        for form in F.RATIO_FORMS:
            for axis in F.GIBUU_AXES:
                fig, _ = self.figure("ratio", form, axis)
                xs = []
                for gid, arts in drawn(fig).items():
                    if gid.startswith("ratio:gibuu") and not gid.endswith("legend"):
                        for a in arts:
                            self.assertTrue(isinstance(a, LineCollection) or a.get_linestyle() == "None")
                            xs += list(a.get_xydata()[:, 0]) if isinstance(a, Line2D) else [
                                s[0][0] for s in a.get_segments()]
                self.assertEqual(sorted({int(round(x)) for x in xs}), list(G.GIBUU_CELLS))
                plt.close(fig)
        fig, _ = self.figure("modes")
        self.assertFalse(any(g.startswith("modes:gibuu") for g in drawn(fig)))

    def test_ratio_prediction_over_data_against_the_keys(self):
        for axis in F.GIBUU_AXES:
            fig, _ = self.figure("ratio", "prediction-over-data", axis)
            D_ = drawn(fig)
            s = np.array(self.tree.g["predictions"][0]["sigma_total_over_f"])
            for a in range(len(fig.axes)):
                rects = D_[f"ratio:data:{a}"]
                self.assertEqual(len(rects), 16)
                for i, r in enumerate(rects):
                    self.assertIs(r.axes, fig.axes[a])
                    self.assertAlmostEqual(r.get_y(), 1 - s[i], places=14)
                    self.assertAlmostEqual(r.get_y() + r.get_height(), 1 + s[i], places=14)
                    self.assertAlmostEqual(r.get_x() + r.get_width() / 2, i, places=14)
            for p in self.tree.g["predictions"]:
                (ln,) = D_[f"ratio:{p['name']}"]
                np.testing.assert_allclose(ln.get_xydata()[:, 1], 1 + np.array(p["g_over_f_minus_1"]), rtol=1e-15)
                self.assertNotIn(f"ratio:{p['name']}:err", D_)
            plt.close(fig)

    def test_ratio_key_is_the_definition(self):
        fig, _ = self.figure("ratio")
        D_ = drawn(fig)
        defn = json.loads(DEFINITION.read_text())
        expect = {"pt": {(0.0, 0.7): "< 0.7", (0.7, 4.5): "> 0.7"}, "pz": {(1.5, 4.5): "< 4.5", (4.5, 60.0): "> 4.5"},
                  "eavail": {(0.0, 0.8): "< 0.8", (0.8, 100.0): "> 0.8", (0.0, 100.0): "all"},
                  "q3": {(0.0, 2.0): "< 2", (2.0, 100.0): "> 2", (0.0, 100.0): "all"},
                  "W": {(0.0, 1.8): "< 1.8", (1.8, 100.0): "> 1.8", (0.0, 100.0): "all"}}
        self.assertEqual(len(defn["reporting_cells"]), 16)
        for c in defn["reporting_cells"]:
            for ax in expect:
                t = D_[f"ratio:key:{ax}:R{c['id']:02d}"][0]
                self.assertEqual(t.get_text(), expect[ax][tuple(c["box"][ax])])
                self.assertIs(t.axes, fig.axes[-1])
        self.assertEqual([t.get_text() for t in fig.axes[-1].get_xticklabels()], CELLS)
        self.assertEqual(D_["ratio:keylabel:pz"][0].get_text(), "$p_\\parallel$ (GeV/$c$)")
        self.assertEqual(D_["ratio:keylabel:W"][0].get_text(), "$W$ (GeV)")

    def test_modes_against_the_keys(self):
        fig, _ = self.figure("modes")
        D_ = drawn(fig)
        for i, n in enumerate(("genie_cv", "genie_mec", "nuwro", "mnvtune_v1")):
            top, ranked = self.tree.diag_modes[n]
            for k in range(3):
                bars = D_[f"modes:{n}:{k + 1}"]
                np.testing.assert_array_equal([b.get_height() for b in bars], [top[k]["loadings"][c] for c in CELLS])
                np.testing.assert_allclose([b.get_x() + b.get_width() / 2 for b in bars], range(16), atol=1e-15)
                self.assertEqual({to_hex(b.get_facecolor()) for b in bars}, {STYLE[n][0]})
                t0, t1 = D_[f"modes:{n}:{k + 1}:text0"][0], D_[f"modes:{n}:{k + 1}:text1"][0]
                self.assertTrue(all(a.axes is fig.axes[i * 3 + k] for a in bars + [t0, t1]))
                a, b = numbers(t0.get_text().replace("$\\chi^2$", "")), numbers(t1.get_text())
                self.assertEqual(a[0], ranked[k]["mode"])
                self.assertLessEqual(abs(a[1] - 100 * ranked[k]["fraction"]), 0.05 + 1e-9)
                self.assertLessEqual(abs(b[0] - 100 * ranked[k]["sigma"]), 0.005 + 1e-9)
                z = ranked[k]["projection"] / ranked[k]["sigma"]
                self.assertLessEqual(abs(b[1] - z), 0.005 + 1e-9)
                self.assertAlmostEqual(z ** 2 / ranked[k]["chi2"], 1.0, places=12)
            lab = D_[f"modes:{n}:label"][0]
            self.assertEqual(lab.get_text(), LEGENDS[n])
            self.assertIs(lab.axes, fig.axes[i * 3])
        for k in range(3):
            self.assertEqual(D_[f"modes:header:{k + 1}"][0].get_text(), f"rank {k + 1} by $\\chi^2$")

    def test_sens_against_the_keys(self):
        fig, _ = self.figure("sens")
        D_ = drawn(fig)
        recs = self.tree.fu["sens"]["records"] + self.tree.s2["sens"]["records"]
        for a, p in enumerate(self.tree.g["predictions"]):
            for fam in ("interaction", "flux", "detector", "lateral", "c_e_systematic"):
                want = sorted((x["alpha"], x["chi2"]) for x in recs if x["family"] == fam
                              and x["prediction"] == p["name"])
                (ln,) = D_[f"sens:{p['name']}:{fam}"]
                np.testing.assert_array_equal(ln.get_xydata(), np.array(want))
                self.assertIs(ln.axes, fig.axes[a])
            self.assertEqual(D_[f"sens:{p['name']}:ndf"][0].get_text(), f"ndf {p['total']['ndf']}")
            self.assertEqual(D_[f"sens:{p['name']}:label"][0].get_text(), LEGENDS[p["name"]].replace(": ", ":\n", 1))
            self.assertIs(D_[f"sens:{p['name']}:label"][0].axes, fig.axes[a])
        self.assertEqual(D_["sens:legend:c_e_systematic"][0].get_text(),
                         "interaction + flux + detector + lateral (joint)")
        for fam in ("interaction", "flux", "detector", "lateral"):
            self.assertEqual(D_[f"sens:legend:{fam}"][0].get_text(), f"{fam} alone")
        self.assertEqual(D_["sens:note"][0].get_text(),
                         "descriptive sensitivity of the reported χ²,\nnot an alternative result")

    def test_style_is_the_articles(self):
        self.assertEqual(self.run_tool(("ratio",)), 0)
        F.MF.style()
        import matplotlib as mpl
        self.assertEqual(mpl.rcParams["font.family"], ["serif"])
        self.assertEqual(mpl.rcParams["pdf.fonttype"], 42)
        b = (self.out / "fd_g_fig_ratio.pdf").read_bytes()
        self.assertIn(b"/FontFile2", b)
        self.assertNotIn(b"/CreationDate", b)
        for n, k in (("genie_cv", "GENIE-CV"), ("genie_mec", "GENIE+MEC"), ("nuwro", "NuWro"), ("gibuu", "GiBUU")):
            self.assertEqual(STYLE[n][0], F.MF.COLORS[k])

    def test_same_bytes_in_two_processes(self):
        o1, o2 = self.tmp / "o1", self.tmp / "o2"
        for o in (o1, o2):
            res = run_isolated([str(ND / "fd_g_figures.py"), *self.tree.argv(o, ("ratio",))])
            self.assertEqual(res.returncode, 1)            # the real pins refuse the synthetic readouts ...
        for o in (o1, o2):                                 # ... so the pins are patched in a wrapper
            w = self.tmp / "w.py"
            w.write_text(f"import sys; sys.path.insert(0, {str(ND)!r}); import fd_g_figures as F; "
                         f"F.PINS.update({json.dumps(self.tree.pins)}); raise SystemExit(F.main())\n")
            res = run_isolated([str(w), *self.tree.argv(o, ("ratio", "modes"))])
            self.assertEqual(res.returncode, 0, res.stderr)
        for n in ("ratio", "modes"):
            self.assertEqual(digest(o1 / f"{F.NAMES[n]}.pdf"), digest(o2 / f"{F.NAMES[n]}.pdf"))

    def test_no_overwrite(self):
        for name in ("fd_g_fig_modes.json", "fd_g_fig_ratio.pdf", "fd_g_fig_sens.pdf"):
            with self.subTest(name=name):
                shutil.rmtree(self.out, ignore_errors=True)
                self.out.mkdir()
                (self.out / name).write_text("{}")
                with self.assertRaises(SystemExit) as cm:
                    self.run_tool()
                self.assertIn("FAIL control K0: no output exists", str(cm.exception))
                self.assertEqual(sorted(p.name for p in self.out.iterdir()), [name])
                self.assertEqual((self.out / name).read_text(), "{}")

    def test_a_later_refusal_writes_nothing(self):
        self.rewrite("g_diag_readout", lambda o: o["constants"].update(top=2))
        with self.assertRaises(SystemExit) as cm:
            self.run_tool(("ratio", "modes"))
        self.assertIn("FAIL control K4", str(cm.exception))
        self.assertFalse(self.out.exists() and any(self.out.iterdir()))

    def test_declared_layout_and_wording(self):
        """The ylabel per form, the key's axis names and units, the offsets, the line styles and the legend order,
        written out here."""
        for form, ylab in (("data-over-prediction", "data / prediction"), ("prediction-over-data", "prediction / data")):
            fig, _ = self.figure("ratio", form)
            self.assertEqual([ax.get_ylabel() for ax in fig.axes], [ylab, ylab])
            plt.close(fig)
        fig, _ = self.figure("ratio")
        D_ = drawn(fig)
        for ax, lab in (("pt", "$p_T$ (GeV/$c$)"), ("pz", "$p_\\parallel$ (GeV/$c$)"),
                        ("eavail", "$E_{\\mathrm{avail}}$ (GeV)"), ("q3", "$q_3$ (GeV/$c$)"), ("W", "$W$ (GeV)")):
            self.assertEqual(D_[f"ratio:keylabel:{ax}"][0].get_text(), lab)
        for n, off in (("genie_cv", -0.3), ("genie_mec", -0.15), ("nuwro", 0.0), ("gibuu", 0.15), ("mnvtune_v1", 0.3)):
            p = next(q for q in self.tree.g["predictions"] if q["name"] == n)
            np.testing.assert_allclose(D_[f"ratio:{n}"][0].get_xdata(), [int(c[1:]) + off for c in p["cells"]],
                                       atol=1e-15)
        self.assertEqual([t.get_text() for t in fig.legends[0].get_texts()], [LEGENDS[n] for n in (
            "genie_cv", "genie_mec", "nuwro", "gibuu", "mnvtune_v1")])
        plt.close(fig)
        fig, _ = self.figure("sens")
        D_ = drawn(fig)
        for fam, ls in (("interaction", "-"), ("flux", "-"), ("detector", "-"), ("lateral", "-"), ("c_e_systematic", "--")):
            self.assertEqual(D_[f"sens:gibuu:{fam}"][0].get_linestyle(), ls)
        leg = fig.axes[5].get_legend()
        self.assertEqual([t.get_text() for t in leg.get_texts()],
                         ["interaction alone", "flux alone", "detector alone", "lateral alone",
                          "interaction + flux + detector + lateral (joint)"])
        self.assertEqual(leg.get_title().get_text(), "family shrunk")
        self.assertEqual([fig.axes[i].get_xlabel() for i in range(5)], ["$\\alpha$"] * 5)
        for i, p in enumerate(self.tree.g["predictions"]):     # each panel's y range pads its curves by 12 %
            ys = [y for fam in ("interaction", "flux", "detector", "lateral", "c_e_systematic")
                  for y in D_[f"sens:{p['name']}:{fam}"][0].get_ydata()]
            lo, hi = min(ys), max(ys)
            np.testing.assert_allclose(fig.axes[i].get_ylim(), [lo - 0.12 * (hi - lo), hi + 0.12 * (hi - lo)])
        plt.close(fig)
        fig, _ = self.figure("modes")
        D_ = drawn(fig)
        for gid, arts in D_.items():
            if gid.endswith(":text0"):
                self.assertRegex(arts[0].get_text(), r"^mode \d+: \d+\.\d% of \$\\chi\^2\$$")
            elif gid.endswith(":text1"):
                self.assertRegex(arts[0].get_text(), r"^\$\\sigma\$ = \d+\.\d\d%, distance [+-]\d+\.\d\d\$\\sigma\$$")
        plt.close(fig)
        fig, _ = self.figure("ratio")
        D_ = drawn(fig)
        ys = [D_[f"ratio:keylabel:{ax}"][0].get_window_extent(fig.canvas.get_renderer()).y0
              for ax in ("pt", "pz", "eavail", "q3", "W")]
        self.assertEqual(ys, sorted(ys, reverse=True))      # the key's rows: p_T, p_parallel, E_avail, q3, W

    def test_sidecar_provenance(self):
        self.assertEqual(self.run_tool(("modes",)), 0)
        s = json.loads((self.out / "fd_g_fig_modes.json").read_text())
        pdf = self.out / "fd_g_fig_modes.pdf"
        self.assertEqual(s["pdf_bytes"], pdf.stat().st_size)
        want = {"fd_g_figures.py": ND / "fd_g_figures.py", "fd_g_compare.py": ND / "fd_g_compare.py",
                "s1_assemble.py": ND / "s1_assemble.py", "s5p_stage1_inspect.py": ND / "s5p_stage1_inspect.py",
                "make_figs.py": REPO / "publication/release/figs/make_figs.py"}
        self.assertEqual(s["code"]["sha256"], {k: digest(p) for k, p in want.items()})
        import subprocess
        head = subprocess.run(["git", "-C", str(ND), "rev-parse", "HEAD"], capture_output=True, text=True)
        st = subprocess.run(["git", "-C", str(REPO), "status", "--porcelain", "--", *map(str, want.values())],
                            capture_output=True, text=True)
        if head.returncode == 0:
            self.assertEqual(s["code"]["commit"], head.stdout.strip())
            self.assertEqual(s["code"]["clean"], st.stdout == "")
        else:
            self.assertIsNone(s["code"]["commit"])
        self.assertEqual(s["versions"]["matplotlib"], __import__("matplotlib").__version__)
        b = pdf.read_bytes()
        self.assertIn(b"DejaVuSerif", b)           # the article's serif type, as the run drew it


class Controls(Base):
    """Each control refuses a planted defect, with nothing written."""

    def setUp(self):
        super().setUp()
        self.out.mkdir()

    def refuses(self, control, clause=None, **kw):
        shutil.rmtree(self.out, ignore_errors=True)
        self.out.mkdir()
        try:
            with self.assertRaises(SystemExit) as cm:
                self.run_tool(**kw)
            msg = str(cm.exception)
            self.assertIn(f"FAIL control {control}", msg)
            if clause:
                self.assertIn(clause, msg)
            self.assertEqual(list(self.out.iterdir()), [], "something was written")
        finally:
            shutil.rmtree(self.out, ignore_errors=True)
            self.out.mkdir()

    def test_k0_pin_and_schema(self):
        self.refuses("K0", "g_sens2_readout sha256", pins={**self.tree.pins, "g_sens2_readout": "0" * 64})
        self.rewrite("f0b_readout", lambda o: o.update(schema="fd-f0b-readout/2"))
        self.refuses("K0", "f0b_readout schema")

    def test_k1_each_clause(self):
        cases = [
            ("g_diag_readout", lambda o: o["inputs_sha256"].update(g_readout="0" * 64), "this Stage G readout"),
            ("g_followup_readout", lambda o: o["inputs_sha256"].update(g_diag_readout="0" * 64),
             "this G-DIAG readout"),
            ("g_sens2_readout", lambda o: o["referenced"].update(g_followup_readout="0" * 64),
             "references, this G-FOLLOWUP"),
            ("f0b_readout", lambda o: o["inputs_sha256"].update(definition="0" * 64), "this definition"),
            ("f0b_readout", lambda o: o["inputs_sha256"].update(s1_npz="0" * 64), "S1 product"),
            ("f0b_readout", lambda o: o["extra_block"].update(sha256="0" * 64), "same C_resp"),
            ("g_readout", lambda o: o["extra_block"].update(role="sensitivity"), "C_resp is adopted"),
            ("g_readout", lambda o: o["predictions"].reverse(), "five predictions in order"),
            ("g_sens2_readout", lambda o: o["inputs_sha256"].update(nuwro="0" * 64), "same five predictions"),
            ("g_sens2_readout", lambda o: o["inputs_sha256"].update(g_readout="0" * 64), "this Stage G readout"),
            ("g_followup_readout", lambda o: o["inputs_sha256"].update(g_readout="0" * 64), "this Stage G readout"),
            ("g_sens2_readout", lambda o: o["inputs_sha256"].update(g_followup_readout="0" * 64),
             "G-SENS2 ran on, and references"),
            ("g_diag_readout", lambda o: o["inputs_sha256"].update(definition="0" * 64), "this definition"),
            ("g_sens2_readout", lambda o: o["inputs_sha256"].update(definition="0" * 64), "this definition"),
            ("g_readout", lambda o: o["inputs_sha256"].update(definition="0" * 64), "this definition"),
            ("g_diag_readout", lambda o: o["inputs_sha256"].update(s1_npz="0" * 64), "S1 product"),
            ("g_followup_readout", lambda o: o["inputs_sha256"].update(extra_block="0" * 64), "same C_resp"),
            ("g_readout", lambda o: o["extra_block"].update(name="C_x"), "C_resp is adopted"),
            ("g_readout", lambda o: o["predictions"][2].update(label="NuWro 21.09"), "with their labels"),
            ("g_readout", lambda o: o["predictions"][0].update(sha256="0" * 64), "with their labels"),
            ("g_diag_readout", lambda o: o["inputs_sha256"].update(gibuu="0" * 64), "same five predictions"),
            ("g_diag_readout", lambda o: o["predictions"].reverse(), "G-DIAG holds the five predictions in order"),
        ]
        for key, fn, clause in cases:
            with self.subTest(clause=clause):
                self.tree = FigTree(self.tmp / "in")
                chain_field = any(w in clause for w in ("this Stage G readout", "this G-DIAG readout", "references"))
                self.rewrite(key, fn, rechain=not chain_field)
                self.refuses("K1", clause)

    def test_k2_the_error_bar_is_c_total_plus_c_resp(self):
        def with_vg(o):                       # a bar that also carries V_g: sigma^2 is no longer the two blocks'
            for p in o["predictions"]:
                p["sigma_total_over_f"] = [s * 1.01 for s in p["sigma_total_over_f"]]
        self.rewrite("g_readout", with_vg)
        self.refuses("K2", "sigma^2 = sigma(C_total)^2 + sigma(C_resp)^2", figures=("ratio",))

    def test_k2_f0b_and_the_data(self):
        self.rewrite("f0b_readout", lambda o: o["relative_sigma_plus_C_resp"]["C_total"].__setitem__(3, 0.5))
        self.refuses("K2", "F0b's", figures=("ratio",))
        self.tree = FigTree(self.tmp / "in")
        self.rewrite("g_readout", lambda o: o["predictions"][2]["f"].__setitem__(5, 1e-39))
        self.refuses("K2", "nuwro: f is the same data", figures=("ratio",))
        self.tree = FigTree(self.tmp / "in")
        self.rewrite("g_readout", lambda o: o["predictions"][1]["g_over_f_minus_1"].__setitem__(0, 0.0))
        self.refuses("K2", "genie_mec: g/f - 1", figures=("ratio",))

    def test_k3_gibuu_cells(self):
        def high(o):
            p = o["predictions"][3]
            p["cells"] = p["cells"][:7] + ["R04"]
        self.rewrite("g_readout", high)
        self.refuses("K3", "GiBUU's cells", figures=("ratio",))

    def test_k3_a_gibuu_point_drawn_above_4_5(self):
        orig = F.ratio_model

        def planted(r, form, axis=F.GIBUU_AXES[0]):
            m = orig(r, form, axis)
            for it in m["items"]:
                if it["gid"] == "ratio:gibuu":
                    it["x"][-1] = 4 + F.OFFSET["gibuu"]
            return m
        with mock.patch.object(F, "ratio_model", planted):
            self.refuses("K3", "ratio:gibuu is on GiBUU's eight cells only", figures=("ratio",))

    def test_k3_gibuu_joined_by_a_line(self):
        orig = F.ratio_model

        def planted(r, form, axis=F.GIBUU_AXES[0]):
            m = orig(r, form, axis)
            F.by_gid(m)["ratio:gibuu"]["style"]["ls"] = "-"
            return m
        with mock.patch.object(F, "ratio_model", planted):
            self.refuses("K3", "as points", figures=("ratio",))

    def test_k4_modes(self):
        def swap(o):
            rt = o["predictions"][0]["comparisons"][0]["relative_to_f"]
            rt["top_modes"][0], rt["top_modes"][1] = rt["top_modes"][1], rt["top_modes"][0]
        self.rewrite("g_diag_readout", swap)
        self.refuses("K4", "genie_cv rank 1", figures=("modes",))
        self.tree = FigTree(self.tmp / "in")
        self.rewrite("g_diag_readout", lambda o: o["predictions"][2]["comparisons"][0]["relative_to_f"][
            "modes_by_chi2"][1].update(projection=0.123))
        self.refuses("K4", "nuwro rank 2: (projection/sigma)^2", figures=("modes",))
        self.tree = FigTree(self.tmp / "in")
        self.rewrite("g_diag_readout", lambda o: o["predictions"][4]["comparisons"][0].update(matrix="C_total + V_g"))
        self.refuses("K4", "mnvtune_v1: one reported comparison", figures=("modes",))

    def test_k5_sens(self):
        self.rewrite("g_sens2_readout", lambda o: o["sens"]["records"].pop(0))
        self.refuses("K5", "one record per alpha", figures=("sens",))
        self.tree = FigTree(self.tmp / "in")

        def shifted(o):
            for x in o["sens"]["records"]:
                if x["alpha"] == 0 and x["prediction"] == "gibuu" and x["family"] == "interaction":
                    x["chi2"] *= 1 + 1e-8
        self.rewrite("g_followup_readout", shifted)
        self.refuses("K5", "gibuu interaction: alpha = 0", figures=("sens",))

    def plant_definition(self, fn):
        """A copy of the definition with fn applied, pinned, and every readout re-made on it."""
        defn = json.loads(DEFINITION.read_text())
        fn(defn)
        path = self.tmp / "definition.json"
        path.write_text(json.dumps(defn))
        self.tree.definition = path
        self.tree.g["inputs_sha256"]["definition"] = digest(path)
        self.tree.write_all()

    def test_k2_k3_each_clause(self):
        def pred(i, **kw):
            return lambda o: o["predictions"][i].update(**kw)

        def neg(o):
            p = o["predictions"][1]
            p["g"][0] = -p["g"][0]
            p["g_over_f_minus_1"][0] = p["g"][0] / p["f"][0] - 1
        cases = [
            ("g_readout", lambda o: o["predictions"][3]["sigma_total_over_f"].__setitem__(0, 0.5),
             "K2", "gibuu: sigma_total_over_f is the same"),
            ("g_readout", pred(0, reported_covariance="C_total"), "K2", "genie_cv: the reported covariance"),
            ("g_readout", neg, "K2", "genie_mec: f and g are positive"),
            ("g_readout", lambda o: o["predictions"][0]["variant"].update(covariance="C_total + C_resp"),
             "K2", "the error bar is C_total + C_resp"),
            ("f0b_readout", lambda o: o["extra_block"]["relative_sigma"].__setitem__(2, 0.9), "K2", "F0b's"),
            ("g_readout", lambda o: o["predictions"][1].update(cells=CELLS[:15] + ["R00"]), "K3",
             "every other prediction is on all sixteen cells"),
        ]
        for key, fn, control, clause in cases:
            with self.subTest(clause=clause):
                self.tree = FigTree(self.tmp / "in")
                self.rewrite(key, fn)
                self.refuses(control, clause, figures=("ratio",))

    def test_k3_the_definition(self):
        self.plant_definition(lambda d: d["reporting_cells"].pop())
        self.refuses("K3", "the definition reports exactly R00-R15", figures=("ratio",))
        self.tree = FigTree(self.tmp / "in")
        self.plant_definition(lambda d: d["reporting_cells"][1]["box"].update(pt=[0.7, 4.5]))
        self.refuses("K3", "cells R00-R03 share their p_T and p_parallel box", figures=("ratio",))

    def test_k4_each_clause(self):
        def rt(i, o):
            return o["predictions"][i]["comparisons"][0]["relative_to_f"]

        def descending(o):
            r = rt(1, o)
            for key in ("top_modes", "modes_by_chi2"):
                r[key][0], r[key][1] = r[key][1], r[key][0]

        def short(o):
            rt(2, o)["top_modes"][0]["loadings"].pop("R07")

        def scaled(o):
            t = rt(0, o)["top_modes"][2]
            t["loadings"] = {c: 1.01 * v for c, v in t["loadings"].items()}

        def flipped(o):
            t = rt(4, o)["top_modes"][1]
            t["loadings"] = {c: -v for c, v in t["loadings"].items()}

        def twice(o):
            o["predictions"][0]["comparisons"].append(copy.deepcopy(o["predictions"][0]["comparisons"][0]))
        cases = [
            (lambda o: o["constants"].update(top=2), "G-DIAG recorded its top 3 modes"),
            (twice, "genie_cv: one reported comparison"),
            (lambda o: o["predictions"][1]["comparisons"][0].update(chi2_stage_g=1.0), "genie_mec: one reported"),
            (descending, "genie_mec rank 2: the modes are in descending chi2"),
            (short, "nuwro rank 1: top_modes[0] is modes_by_chi2[0]"),
            (scaled, "genie_cv rank 3: unit loadings"),
            (flipped, "mnvtune_v1 rank 2: unit loadings, signed"),
        ]
        for fn, clause in cases:
            with self.subTest(clause=clause):
                self.tree = FigTree(self.tmp / "in")
                self.rewrite("g_diag_readout", fn)
                self.refuses("K4", clause, figures=("modes",))

    def test_k5_each_clause(self):
        def recs(fn):
            return lambda o: [fn(x) for x in o["sens"]["records"] if x["prediction"] == "nuwro" and x["alpha"] == 0.5]
        cases = [
            ("g_followup_readout", lambda o: o["sens"].update(reported_matrix="C_total + V_g"),
             "g_followup_readout: the reported matrix and label"),
            ("g_sens2_readout", lambda o: o["sens"].update(label="a sensitivity"),
             "g_sens2_readout: the reported matrix and label"),
            ("g_sens2_readout", lambda o: o["constants"].update(alphas=[0.0, 0.1, 0.25, 0.5]),
             "g_sens2_readout: the reported matrix and label"),
            ("g_sens2_readout", lambda o: o["referenced"]["families"].update(interaction=["flux"]),
             "G-SENS2's referenced families are G-FOLLOWUP's"),
            ("g_sens2_readout", recs(lambda x: x.update(ndf=15)), "nuwro flux: alpha = 0 is Stage G's"),
            ("g_followup_readout", recs(lambda x: x.update(label="x")), "nuwro interaction: alpha = 0 is Stage G's"),
            ("g_followup_readout", recs(lambda x: x.update(chi2=None)), "nuwro interaction: alpha = 0 is Stage G's"),
        ]
        for key, fn, clause in cases:
            with self.subTest(clause=clause):
                self.tree = FigTree(self.tmp / "in")
                self.rewrite(key, fn)
                self.refuses("K5", clause, figures=("sens",))

    def test_k6_each_drawn_kind(self):
        def seg_drop(fig, m):
            (lc,) = self.art(fig, "ratio:nuwro:err")
            lc.set_segments(lc.get_segments()[:-1])

        def seg_x(fig, m):
            (lc,) = self.art(fig, "ratio:nuwro:err")
            s = [np.array(x) for x in lc.get_segments()]
            s[1][:, 0] += 0.01
            lc.set_segments(s)

        def line_x(fig, m):
            (ln,) = self.art(fig, "ratio:gibuu")
            ln.set_xdata(ln.get_xdata() + 0.01)

        def bar_x(fig, m):
            self.art(fig, "modes:genie_cv:1")[3].set_x(5.0)

        def bar_drop(fig, m):
            self.art(fig, "modes:genie_cv:1")[3].remove()

        def last_bar_drop(fig, m):
            self.art(fig, "modes:genie_cv:1")[-1].remove()

        def text(fig, m):
            self.art(fig, "ratio:key:q3:R09")[0].set_text("< 2")

        def ref(fig, m):
            self.art(fig, "ratio:ref:0")[0].set_ydata([1.1, 1.1])

        def extra(fig, m):
            fig.axes[0].plot([1.0], [1.0], gid="ratio:extra")

        def moved(fig, m):
            fig.axes[1].set_position([0.11, 0.31, 0.87, 0.17])

        def ticks(fig, m):
            fig.axes[-1].set_xticks(range(16), ["x"] * 16)

        def ylabel(fig, m):
            fig.axes[0].set_ylabel("ratio")

        def stray(fig, m):
            fig.axes[0].tick_params(labelbottom=True)
        cases = [(seg_drop, "ratio:nuwro:err is drawn"), (seg_x, "ratio:nuwro:err is drawn"),
                 (line_x, "ratio:gibuu is drawn"), (text, "ratio:key:q3:R09 is drawn"), (ref, "ratio:ref:0 is drawn"),
                 (extra, "the drawn gids are the model's"), (moved, "the axes are the model's"),
                 (ticks, "the tick labels are the model's"), (ylabel, "ratio:ylabel:0 is the model's"),
                 (stray, "only the model's axes show x tick labels")]
        for fn, clause in cases:
            with self.subTest(clause=clause), self.painted(fn):
                self.refuses("K6", clause, figures=("ratio",))
        for fn, clause in ((bar_x, "modes:genie_cv:1 is drawn"), (bar_drop, "modes:genie_cv:1 is drawn"),
                           (last_bar_drop, "modes:genie_cv:1 is drawn")):
            with self.subTest(clause=clause), self.painted(fn):
                self.refuses("K6", clause, figures=("modes",))

    def test_k6_the_band_and_the_page(self):
        def band(fig, m):
            self.art(fig, "ratio:data:0")[4].set_height(0.0)
        with self.painted(band):
            self.refuses("K6", "ratio:data:0 is drawn", figures=("ratio",), form="prediction-over-data")
        orig = F.ratio_model

        def narrow(r, form, axis=F.GIBUU_AXES[0]):
            m = orig(r, form, axis)
            m["axes"][0]["xlim"] = [-0.6, 14.0]
            return m
        with mock.patch.object(F, "ratio_model", narrow):
            self.refuses("K6", "nothing clipped", figures=("ratio",))

        def band_clipped(r, form, axis=F.GIBUU_AXES[0]):
            m = orig(r, form, axis)
            ys = [q[1] for q in F.by_gid(m)["ratio:data:0"]["rects"]]
            m["axes"][0]["ylim"][0] = min(ys) + 1e-3
            for it in m["items"]:
                if it["axes"] == 0 and it["kind"] == "line":
                    it["y"] = [max(y, min(ys) + 2e-3) for y in it["y"]]
            return m
        with mock.patch.object(F, "ratio_model", band_clipped):
            self.refuses("K6", "clipped: ['ratio:data:0']", figures=("ratio",), form="prediction-over-data")

        def off_page(r, form, axis=F.GIBUU_AXES[0]):
            m = orig(r, form, axis)
            F.by_gid(m)["ratio:keylabel:W"]["at"]["x"] = -0.3
            return m
        with mock.patch.object(F, "ratio_model", off_page):
            self.refuses("K6", "every text lies on the page", figures=("ratio",))

    def test_rel_and_check_pdf(self):
        self.assertEqual(F.rel([1.0, 2.0], [1.0, 2.0]), 0.0)
        self.assertEqual(F.rel([1.0, 2.0], [1.0]), float("inf"))
        self.assertEqual(F.rel([1.0, float("nan")], [1.0, 1.0]), float("inf"))
        self.assertAlmostEqual(F.rel([1.0, 2.0], [1.0, 2.2]), 0.2 / 2.2)
        good = b"%PDF-1.4 /FontFile2 x"
        F.check_pdf("t", good, good)
        for bad, clause in ((b"%PDF-1.4 x", "TrueType"), (b"%PDF-1.4 /FontFile2 /Type3", "TrueType"),
                            (b"%PDF-1.4 /FontFile2 /Subtype /Image", "raster"), (b"PDF /FontFile2", "TrueType")):
            with self.subTest(bad=bad), self.assertRaises(SystemExit) as cm:
                F.check_pdf("t", bad, bad)
            self.assertIn("K8", str(cm.exception))
        with self.assertRaises(SystemExit) as cm:
            F.check_pdf("t", good, good + b" ")
        self.assertIn("same bytes", str(cm.exception))

    def test_tolerances(self):
        """K6's 1e-12 and the readouts' 1e-10, each at a defect between them and a looser tolerance."""
        def plant(fig, m):
            (ln,) = self.art(fig, "ratio:genie_mec")
            y = ln.get_ydata().copy()
            y[0] *= 1 + 1e-9
            ln.set_ydata(y)
        with self.painted(plant):
            self.refuses("K6", "ratio:genie_mec is drawn", figures=("ratio",))

        def shifted(o):
            for x in o["sens"]["records"]:
                if x["alpha"] == 0 and x["prediction"] == "nuwro" and x["family"] == "flux":
                    x["chi2"] *= 1 + 3e-10
        self.rewrite("g_sens2_readout", shifted)
        self.refuses("K5", "nuwro flux: alpha = 0", figures=("sens",))

    def test_k7_each_clause(self):
        with mock.patch.dict(F.QUALIFIERS, {"genie_cv": ("a qualifier not in its label",)}):
            self.refuses("K7", "ratio:genie_cv:legend", figures=("ratio",))
        with mock.patch.dict(F.QUALIFIERS, {"nuwro": ("C13 target; no correction to CH applied",)}):
            self.refuses("K7", "ratio:nuwro:legend", figures=("ratio",))
        with mock.patch.dict(F.QUALIFIERS, {"nuwro": ()}):
            self.refuses("K7", "ratio:nuwro:legend", figures=("ratio",))
        P = {n: {"name": n, "label": "X; Y"} for n in F.ORDER}
        with mock.patch.dict(F.SHORT, {n: "X" for n in F.ORDER}), mock.patch.dict(F.QUALIFIERS, {}, clear=True):
            with self.assertRaises(SystemExit) as cm:
                F.check_labels({"figure": "ratio", "items": []}, {"g_readout": {"predictions": list(P.values())}})
        self.assertIn("the five names differ", str(cm.exception))

    def test_k8_a_type3_font(self):
        orig = F.MF.style

        def type3():
            orig()
            plt.rcParams["pdf.fonttype"] = 3
        with mock.patch.object(F.MF, "style", type3):
            self.refuses("K8", "TrueType", figures=("ratio",))

    def painted(self, after):
        """A paint that draws the model, then plants a defect in the drawn figure."""
        orig = F.paint

        def planted(model):
            fig = orig(model)
            after(fig, model)
            return fig
        return mock.patch.object(F, "paint", planted)

    def art(self, fig, gid):
        return [a for a in fig.findobj(lambda o: o.get_gid() == gid)]

    def test_k6_a_point_drawn_off_the_model(self):
        def plant(fig, model):
            (ln,) = self.art(fig, "ratio:nuwro")
            y = ln.get_ydata().copy()
            y[2] *= 1.001
            ln.set_ydata(y)
        with self.painted(plant):
            self.refuses("K6", "ratio:nuwro is drawn as the model holds it", figures=("ratio",))

    def test_k6_an_error_bar_and_a_loading(self):
        def plant(fig, model):
            (lc,) = self.art(fig, "ratio:genie_cv:err")
            s = [np.array(x) for x in lc.get_segments()]
            s[0][1, 1] += 1e-3
            lc.set_segments(s)
        with self.painted(plant):
            self.refuses("K6", "ratio:genie_cv:err", figures=("ratio",))
        with self.painted(lambda fig, m: self.art(fig, "modes:nuwro:2")[5].set_height(0.0)):
            self.refuses("K6", "modes:nuwro:2 is drawn", figures=("modes",))

    def test_k6_a_missing_and_an_unmodelled_artist(self):
        with self.painted(lambda fig, m: self.art(fig, "sens:gibuu:flux")[0].remove()):
            self.refuses("K6", "the drawn gids are the model's", figures=("sens",))
        with self.painted(lambda fig, m: fig.axes[0].plot([4.15, 5.15], [1.0, 1.0], "D")):   # GiBUU-like, no gid
            self.refuses("K6", "every artist with ink is a model item", figures=("ratio",))
        # review C's three: an axes title, an axis label the model does not hold, a figure-level line
        for plant in (lambda fig, m: fig.axes[0].set_title("a title"),
                      lambda fig, m: fig.axes[0].set_xlabel("cell"),
                      lambda fig, m: fig.add_artist(Line2D([0.1, 0.9], [0.5, 0.5], gid=None))):
            with self.subTest(plant=plant), self.painted(plant):
                self.refuses("K6", "every artist with ink is a model item", figures=("ratio",))

    def test_k6_style_and_axes(self):
        with self.painted(lambda fig, m: self.art(fig, "ratio:gibuu")[0].set_linestyle("-")):
            self.refuses("K6", "ratio:gibuu is drawn as the model holds it", figures=("ratio",))
        with self.painted(lambda fig, m: self.art(fig, "ratio:nuwro")[0].set_color("#000000")):
            self.refuses("K6", "ratio:nuwro is drawn", figures=("ratio",))

        def move(fig, m):                        # GENIE CV's row label drawn on NuWro's row
            (t,) = self.art(fig, "modes:genie_cv:label")
            t.remove()
            fig.axes[6].text(0.0, 1.0, t.get_text(), transform=fig.axes[6].transAxes, gid=t.get_gid())
        with self.painted(move):
            self.refuses("K6", "modes:genie_cv:label is drawn", figures=("modes",))

    def test_k6_legend_handles_reversed(self):
        def reverse(fig, m):
            leg = fig.legends[0]
            texts = [(t.get_text(), t.get_gid()) for t in leg.get_texts()]
            hs = list(reversed([a for a in fig.axes[0].lines + fig.axes[1].lines if a.get_gid() and
                                F.by_gid(m)[a.get_gid()]["kind"] == "line"]))
            leg.remove()
            new = fig.legend(hs, [t for t, _ in texts], loc="upper center", ncol=2, frameon=False)
            for t, (_, gid) in zip(new.get_texts(), texts):
                t.set_gid(gid)
        with self.painted(reverse):
            self.refuses("K6", "shows its own series' handle", figures=("ratio",))

    def test_k6_a_model_label_on_the_wrong_row(self):
        orig = F.modes_model

        def planted(r):
            m = orig(r)
            I = F.by_gid(m)
            I["modes:genie_cv:label"]["axes"], I["modes:nuwro:label"]["axes"] = (I["modes:nuwro:label"]["axes"],
                                                                                I["modes:genie_cv:label"]["axes"])
            return m
        with mock.patch.object(F, "modes_model", planted):
            self.refuses("K6", "modes:genie_cv:label sits in its own data's panel", figures=("modes",))

    def test_k6_clipped(self):
        orig = F.padded
        with mock.patch.object(F, "padded", lambda v: [orig(v)[0], 1.0]):
            self.refuses("K6", "nothing clipped", figures=("ratio",))

    def test_k6_text_over_text_and_over_bars(self):
        orig = F.ratio_model

        def planted(r, form, axis=F.GIBUU_AXES[0]):
            m = orig(r, form, axis)
            F.by_gid(m)["ratio:key:q3:R03"]["at"]["dy"] = F.by_gid(m)["ratio:key:eavail:R03"]["at"]["dy"]
            return m
        with mock.patch.object(F, "ratio_model", planted):
            self.refuses("K6", "no two texts overlap", figures=("ratio",))
        with mock.patch.object(F, "MODES_YLIM", (-1.05, 1.05)):
            self.refuses("K6", "no text covers a drawn point, bar end or bar", figures=("modes",))

    def test_k7_labels(self):
        with mock.patch.dict(F.QUALIFIERS, {"gibuu": (G.C12_LABEL,)}):
            self.refuses("K7", "ratio:gibuu:legend", figures=("ratio",))
        with mock.patch.dict(F.QUALIFIERS, {"mnvtune_v1": ("an independent prediction",)}):
            self.refuses("K7", "mnvtune_v1", figures=("modes",))
        with mock.patch.dict(F.SHORT, {"genie_cv": F.SHORT["genie_mec"], "genie_mec": F.SHORT["genie_cv"]}):
            self.refuses("K7", "genie_cv", figures=("ratio",))
        with mock.patch.dict(F.SHORT, {"nuwro": "NuWro 21"}):
            self.refuses("K7", "ratio:nuwro:legend names nuwro as Stage G's label does", figures=("ratio",))
        orig = F.sens_model

        def note(r):
            m = orig(r)
            F.by_gid(m)["sens:note"]["text"] = "the sensitivity"
            return m
        with mock.patch.object(F, "sens_model", note):
            self.refuses("K7", "the sensitivity note", figures=("sens",))

    def test_k8_raster_and_bytes(self):
        def raster(fig, m):
            im = fig.axes[0].imshow(np.zeros((2, 2)), extent=(0, 1, 0, 1))
            im.set_gid("modes:raster")
        with self.painted(raster), mock.patch.object(F, "readback", lambda fig, model: None):
            self.refuses("K8", "no raster image", figures=("modes",))
        calls = [0]
        orig_r = F.render

        def drifting(fig):
            calls[0] += 1
            fig.text(0, 0, str(calls[0]))
            return orig_r(fig)
        with mock.patch.object(F, "render", drifting):
            self.refuses("K8", "same bytes", figures=("ratio",))


class Check(Base):
    """fd_g_figures_check.py, the independent re-derivation, on the tool's output and on planted defects."""

    def check(self, out: Path):
        argv = []
        for k, p in self.tree.paths().items():
            argv += ["--" + k.replace("_", "-"), str(p)]
        return run_isolated([str(ND / "fd_g_figures_check.py"), *argv, "--figures-dir", str(out)])

    def test_passes_on_the_tools_output(self):
        for i, (form, axis) in enumerate([(f, a) for f in F.RATIO_FORMS for a in F.GIBUU_AXES]):
            out = self.tmp / f"o{i}"
            F.run(F.build_args(self.tree.argv(out, ("ratio", "modes", "sens") if i == 0 else ("ratio",))
                               + ["--ratio-form", form, "--gibuu-axis", axis]), pins=self.tree.pins)
            res = self.check(out)
            self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
            self.assertIn(f"0 failed, {3 if i == 0 else 1} sidecars", res.stdout)

    def tamper(self, fig, fn):
        """A copy of the tool's output with one sidecar changed by fn."""
        if not (self.tmp / "clean").exists():
            self.assertEqual(F.run(F.build_args(self.tree.argv(self.tmp / "clean")), pins=self.tree.pins), 0)
        shutil.rmtree(self.out, ignore_errors=True)
        shutil.copytree(self.tmp / "clean", self.out)
        side = self.out / f"{F.NAMES[fig]}.json"
        s = json.loads(side.read_text())
        fn(s)
        side.write_text(json.dumps(s))
        return self.check(self.out)

    def test_refuses_planted_defects(self):
        def item(s, gid):
            return next(it for it in s["plotted"]["items"] if it["gid"] == gid)
        cases = [
            ("ratio", lambda s: item(s, "ratio:nuwro")["y"].__setitem__(3, item(s, "ratio:nuwro")["y"][3] * 1.0001),
             "ratio:nuwro is f/g"),
            ("ratio", lambda s: item(s, "ratio:gibuu:err")["hi"].__setitem__(0, 9.0), "ratio:gibuu:err"),
            ("ratio", lambda s: item(s, "ratio:key:W:R05").update(text="all"), "ratio:key:W:R05 is the definition"),
            ("ratio", lambda s: item(s, "ratio:mnvtune_v1:legend").update(text="MINERvA Tune v1"),
             "ratio:mnvtune_v1:legend names it"),
            ("modes", lambda s: item(s, "modes:nuwro:2")["heights"].reverse(), "modes:nuwro:2 bars"),
            ("modes", lambda s: item(s, "modes:genie_mec:3:text1").update(text="$\\sigma$ = 9.99%, distance +0.00$\\sigma$"),
             "modes:genie_mec:3 prints"),
            ("modes", lambda s: item(s, "modes:genie_cv:label").update(axes=3), "modes:genie_cv:label names it as Stage G's label does, over its own rank-1 panel"),
            ("sens", lambda s: item(s, "sens:gibuu:lateral")["y"].reverse(), "sens:gibuu:lateral is the records"),
            ("sens", lambda s: item(s, "sens:nuwro:ndf").update(text="ndf 15"), "sens:nuwro:ndf is Stage G's"),
            ("sens", lambda s: s["plotted"]["items"].append({"gid": "sens:extra", "kind": "text", "text": "1.0"}),
             "sens: every plotted item is checked"),
            ("ratio", lambda s: s.update(pdf_sha256="0" * 64), "ratio: the PDF's sha256"),
            # review C: a name cut at a delimiter, a rank swap, GiBUU on the wrong axes, options that differ
            ("ratio", lambda s: item(s, "ratio:genie_cv:legend").update(text="GENIE 2.12.10 CV"),
             "ratio:genie_cv:legend is the declared name"),
            ("modes", lambda s: [item(s, f"modes:nuwro:{k}{t}").update(axes=7 + (k == 2) * 1 - (k == 3) * 1)
                                 for k in (2, 3) for t in ("", ":text0", ":text1")], "modes:nuwro:2 is in row nuwro"),
            ("ratio", lambda s: item(s, "ratio:gibuu").update(axes=0), "ratio:gibuu is on its declared axes"),
            ("ratio", lambda s: s["options"].update(ratio_form="prediction-over-data"),
             "ratio: the model's form and GiBUU axis are the run's options"),
            ("modes", lambda s: s["inputs_sha256"].update(g_readout="0" * 64), "modes: the inputs' sha256"),
        ]
        for fig, fn, clause in cases:
            with self.subTest(clause=clause):
                res = self.tamper(fig, fn)
                self.assertEqual(res.returncode, 1, res.stdout)
                self.assertIn(f"FAIL {clause}", res.stdout)


class Invocation(Base):
    def test_real_pins_refuse_synthetic_readouts(self):
        res = run_isolated([str(ND / "fd_g_figures.py"), *self.tree.argv(self.out)])
        self.assertEqual(res.returncode, 1)
        self.assertIn("FAIL control K0 g_readout sha256 is the pin", res.stdout + res.stderr)
        self.assertNotIn("Traceback", res.stderr)
        self.assertFalse(self.out.exists() and any(self.out.iterdir()))

    def test_argparse(self):
        for bad in (["--figures"], ["--figures", "ratio", "ratio"], ["--figures", "table"],
                    ["--figures", "ratio", "--ratio-form", "ratio"]):
            with self.subTest(bad=bad):
                argv = self.tree.argv(self.out)
                argv = argv[:argv.index("--figures")] + bad + ["--out-dir", str(self.out)]
                res = run_isolated([str(ND / "fd_g_figures.py"), *argv])
                self.assertEqual(res.returncode, 2, res.stderr)


class CommittedPins(unittest.TestCase):
    """The committed readouts: digests, schemas and the K1 chain only. Nothing is drawn from them."""

    def test_pins_schemas_and_chain(self):
        for k, p in COMMITTED.items():
            self.assertEqual(digest(p), F.PINS[k], k)
        r = {k: json.loads(p.read_text()) for k, p in COMMITTED.items()}
        for k in F.INPUTS:
            self.assertEqual(r[k]["schema"], F.SCHEMAS[k])
        F.check_chain(r, F.PINS)
        self.assertEqual(r["g_diag_readout"]["constants"]["top"], F.TOP)
        self.assertEqual(r["g_followup_readout"]["constants"]["alphas"], list(ALPHAS))
        self.assertEqual(F.ALPHAS, ALPHAS)
        self.assertEqual((F.REPORTED, F.SENS_LABEL), (REPORTED, SENS_LABEL))
        for k in ("g_followup_readout", "g_sens2_readout"):
            self.assertEqual((r[k]["sens"]["reported_matrix"], r[k]["sens"]["label"]), (REPORTED, SENS_LABEL))
        self.assertEqual(sorted(r["g_followup_readout"]["constants"]["families"]) +
                         sorted(r["g_sens2_readout"]["constants"]["families"]),
                         sorted(f for k, f in F.FAMILIES if k == "g_followup_readout") +
                         sorted(f for k, f in F.FAMILIES if k == "g_sens2_readout"))


if __name__ == "__main__":
    unittest.main()
