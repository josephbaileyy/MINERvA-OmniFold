"""Comparison producers take each side's bin geometry from that side's own TH2D axes.

The paper release's ``pt_pl_cross_section`` bins pT with edges 0.075 / 0.325 / 0.475, which
``bin_mapping.txt`` prints as 0.07 / 0.33 / 0.47, our analysis grid. The producers below take the
widths and positions of PUBLISHED values (data, its covariance, the model tables) from the release
TH2D's axes, and the widths, positions and labels of OUR result from our ``hXSec2D``'s axes.

Each producer is tested on small synthetic files:
  - release on the 0.075 grid, ours on our grid: the published geometry is the release axis's;
  - ours on the 0.075 grid (regeneration): our geometry is our input's axis;
  - both on our grid: the output equals that of the producer as it was at ``BASE`` (read with
    ``git show``), and outputs that involve no published width stay unchanged when the release is
    on the 0.075 grid; functions called with their old arguments behave as at ``BASE``.
The ``BASE`` comparisons are skipped when git or ``BASE`` is unavailable, and every test is skipped
when PyROOT or matplotlib is. Locally:
  ~/cov2d-work/figenv/rootmpl3108/bin/python -m pytest 2d-unfolding/tests/test_published_axis_widths.py -q
"""
import contextlib
import csv
import importlib.util
import io
import json
import math
import subprocess
import sys
import tempfile
import unittest
import warnings
from pathlib import Path
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve()
U2D_DIR = HERE.parents[1]
UQ_DIR = U2D_DIR / "uq"
REPO = U2D_DIR.parent
ANC = U2D_DIR / "minerva_paper_anc"
for _d in (REPO, U2D_DIR, UQ_DIR):
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))
import reported_cells as rc  # noqa: E402

# main before the producers read geometry from the TH2D axes
BASE = "ab5adeebbb0e325868f58b1eeda3f3d00e31c97b"

try:
    import ROOT
    ROOT.gROOT.SetBatch(True)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.axes import Axes
    HAVE_DEPS = True
except ImportError:
    HAVE_DEPS = False

OUR_PT = np.array(rc.PT_EDGES, dtype=float)
PAPER_PT = np.array([0, 0.075, 0.15, 0.25, 0.325, 0.40, 0.475, 0.55,
                     0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50])
PT053 = PAPER_PT.copy()
PT053[7] = 0.53                         # 0.53 / 1.5 < tan 20 deg < 0.55 / 1.5: one cell enters the interior
PZ = np.array(rc.PZ_EDGES, dtype=float)
N_PT, N_PZ = rc.GRID_SHAPE
TAN20 = math.tan(math.radians(20.0))


def paper_stat_mask():
    diag = np.zeros(rc.N_CELLS)
    with open(ANC / "cov_ptpl_minerva_inclusive_6GeV_stat.txt") as f:
        r = csv.reader(f)
        next(r)
        for i, j, v in r:
            if i == j:
                diag[int(i)] = float(v)
    return (diag > 0).reshape(rc.GRID_SHAPE)


def areas(pt_edges, pz_edges=PZ):
    """[pt, pz] bin areas."""
    return np.outer(np.diff(pt_edges), np.diff(pz_edges))


def interior(pt_edges):
    """[pt, pz] strict-interior mask, pt_hi / pz_lo <= tan 20 deg."""
    return np.asarray(pt_edges)[1:, None] / PZ[None, :-1] <= TAN20


def centres(e):
    e = np.asarray(e, dtype=float)
    return 0.5 * (e[:-1] + e[1:])


def disp(e):
    """Fig. 13's display axis: cumulative sqrt bin width."""
    return np.concatenate([[0.0], np.cumsum(np.sqrt(np.diff(np.asarray(e, dtype=float))))])


def base_module(rel, name, d):
    """The file at BASE, written to directory d and imported as module `name`; None when git or
    BASE is unavailable."""
    try:
        src = subprocess.run(["git", "-C", str(REPO), "show", f"{BASE}:{rel}"],
                             capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    path = Path(d) / f"{name}.py"
    path.write_bytes(src)
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def new_module(rel, name):
    spec = importlib.util.spec_from_file_location(name, U2D_DIR / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def run_main(module, argv, **attrs):
    """module.main() under argv with module attributes overridden; returns (value, stdout)."""
    saved = {k: getattr(module, k) for k in attrs}
    old_argv = sys.argv
    out = io.StringIO()
    try:
        for k, v in attrs.items():
            setattr(module, k, v)
        sys.argv = [module.__name__] + [str(a) for a in argv]
        with contextlib.redirect_stdout(out), warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            rv = module.main()
    finally:
        sys.argv = old_argv
        for k, v in saved.items():
            setattr(module, k, v)
    return rv, out.getvalue()


@contextlib.contextmanager
def spy(method):
    """Record (label, x or edges) of every Axes.<method> call."""
    orig = getattr(Axes, method)
    calls = []

    def wrapper(self, *a, **k):
        x = a[0] if method == "step" else (a[1] if len(a) > 1 else k.get("edges"))
        calls.append((k.get("label"), np.asarray(x, dtype=float)))
        return orig(self, *a, **k)

    with mock.patch.object(Axes, method, wrapper):
        yield calls


def hist_dump(path):
    """{name: (pt edges, pz edges, contents)} of every TH2D, and values of TMatrix/TParameter."""
    f = ROOT.TFile.Open(str(path))
    out = {}
    for key in f.GetListOfKeys():
        o = key.ReadObj()
        if o.InheritsFrom("TH2"):
            pt, pz = rc.th2d_edges(o)
            c = np.array([[o.GetBinContent(i, j) for j in range(1, o.GetNbinsY() + 1)]
                          for i in range(1, o.GetNbinsX() + 1)])
            out[key.GetName()] = (pt, pz, c)
        elif o.InheritsFrom("TMatrixTBase<double>"):
            out[key.GetName()] = np.array([[o(i, j) for j in range(o.GetNcols())]
                                           for i in range(o.GetNrows())])
        elif o.InheritsFrom("TParameter<double>") or o.InheritsFrom("TParameter<int>"):
            out[key.GetName()] = o.GetVal()
    f.Close()
    return out


@unittest.skipUnless(HAVE_DEPS, "PyROOT or matplotlib unavailable")
class Fixture(unittest.TestCase):
    """Synthetic paper releases and our results on several pT grids.

    Releases: anc07 (our grid), anc075 (the release's grid), anc053 (0.53 for 0.55).
    Ours: ours07, ours075, ours053, ours_off (0.60 for 0.55), ours_badpz (7.5 for 7.0).
    """

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        d = cls.dir = Path(cls.tmp.name)
        rng = np.random.default_rng(11)
        cls.rep = paper_stat_mask()
        cls.cells = rc.reported_indices(cls.rep)
        cls.paper = np.where(cls.rep, 1e-39 * rng.lognormal(0.0, 0.7, rc.GRID_SHAPE), 0.0)
        cls.ours = np.where(cls.rep, cls.paper * (1 + 0.03 * rng.standard_normal(rc.GRID_SHAPE)), 0.0)
        cls.model = np.where(cls.rep, cls.paper * (1 + 0.1 * rng.standard_normal(rc.GRID_SHAPE)), 0.0)
        sig = 0.05 * cls.paper.ravel()
        corr = 0.3 * np.outer(sig, sig) * np.outer(cls.rep.ravel(), cls.rep.ravel())
        cls.cov = np.diag(sig ** 2) + corr * (1 - np.eye(rc.N_CELLS))
        for tag, pt in (("anc075", PAPER_PT), ("anc07", OUR_PT), ("anc053", PT053)):
            (d / tag).mkdir()
            cls.write_paper(d / tag / "cov_ptpl_minerva_inclusive_6GeV.root", pt)
        off = OUR_PT.copy()
        off[7] = 0.60
        badpz = PZ.copy()
        badpz[9] = 7.5
        for name, pt, pz in (("ours07", OUR_PT, PZ), ("ours075", PAPER_PT, PZ), ("ours053", PT053, PZ),
                             ("ours_off", off, PZ), ("ours_badpz", OUR_PT, badpz)):
            cls.write_ours(d / f"{name}.root", pt, cls.ours, pz)
        with open(d / "model.txt", "w") as f:
            f.write("P||bin,Ptbin,model_cross_section\n")
            for ipt in range(N_PT):
                for ipz in range(N_PZ):
                    f.write(f"{ipz + 1},{ipt + 1},{cls.model[ipt, ipz]:.6e}\n")

    @classmethod
    def tearDownClass(cls):
        plt.close("all")
        cls.tmp.cleanup()

    @classmethod
    def write_paper(cls, path, pt_edges, transpose=False):
        """The release layout: TH2D x = p_parallel, y = pT (x = pT with transpose), and four
        224 x 224 TMatrixD."""
        f = ROOT.TFile.Open(str(path), "RECREATE")
        pt_edges = np.asarray(pt_edges, dtype=float)
        if transpose:
            h = ROOT.TH2D("pt_pl_cross_section", "", N_PT, pt_edges, N_PZ, PZ)
        else:
            h = ROOT.TH2D("pt_pl_cross_section", "", N_PZ, PZ, N_PT, pt_edges)
        for ipt in range(N_PT):
            for ipz in range(N_PZ):
                ix, iy = (ipt + 1, ipz + 1) if transpose else (ipz + 1, ipt + 1)
                h.SetBinContent(ix, iy, float(cls.paper[ipt, ipz]))
        h.Write()
        for name, scale in (("TotalCovariance", 1.0), ("StatOnlyCovariance", 0.4),
                            ("FluxCovariance", 0.3), ("MuonEnergyScaleCovariance", 0.2)):
            m = ROOT.TMatrixD(rc.N_CELLS, rc.N_CELLS)
            for i in cls.cells:
                for j in cls.cells:
                    m[int(i)][int(j)] = float(scale * cls.cov[i, j])
            m.Write(name)
        f.Close()

    @staticmethod
    def write_ours(path, pt_edges, a, pz_edges=PZ):
        f = ROOT.TFile.Open(str(path), "RECREATE")
        h = ROOT.TH2D("hXSec2D", "", N_PT, np.asarray(pt_edges, dtype=float),
                      N_PZ, np.asarray(pz_edges, dtype=float))
        for ix in range(N_PT):
            for iy in range(N_PZ):
                h.SetBinContent(ix + 1, iy + 1, float(a[ix, iy]))
        h.Write()
        f.Close()

    def base(self, rel, name):
        m = base_module(rel, name, self.dir)
        if m is None:
            self.skipTest(f"git show {BASE[:12]}:{rel} unavailable")
        return m

    def anc(self, tag):
        return self.dir / tag / "cov_ptpl_minerva_inclusive_6GeV.root"


class Th2dEdgesTest(Fixture):
    def test_both_orientations_read_exactly(self):
        for args, pt in (((N_PT, PAPER_PT, N_PZ, PZ), PAPER_PT), ((N_PZ, PZ, N_PT, PAPER_PT), PAPER_PT),
                         ((N_PT, OUR_PT, N_PZ, PZ), OUR_PT)):
            h = ROOT.TH2D("h", "", *args)
            got_pt, got_pz = rc.th2d_edges(h)
            np.testing.assert_array_equal(got_pt, pt)
            np.testing.assert_array_equal(got_pz, PZ)

    def test_other_shapes_are_refused(self):
        for nx, ny in ((14, 14), (14, 15), (16, 16), (15, 14)):
            with self.subTest(shape=(nx, ny)), self.assertRaises(rc.CellIdentityError):
                rc.th2d_edges(ROOT.TH2D(f"h{nx}{ny}", "", nx, 0, 1, ny, 0, 1))


class CompareToModelsTest(Fixture):
    def argv(self, prefix, ours="ours07"):
        return ["--ours", self.dir / f"{ours}.root", "--model", f"Tune:{self.dir / 'model.txt'}",
                "--out-prefix", self.dir / prefix]

    def projections(self, tag, ours):
        """main() with project() and Axes.step recorded: [(who, axis, pt edges, y)], [(label, x)]."""
        ctm = new_module("compare_to_models.py", f"ctm_{tag}_{ours}")
        calls = []
        orig = ctm.project

        def project(vec_red, mask, axis, *edges):
            r = orig(vec_red, mask, axis, *edges)
            calls.append((vec_red, axis, edges, r[1]))
            return r

        with spy("step") as steps:
            run_main(ctm, self.argv(f"p_{tag}_{ours}", ours), ANC_DIR=str(self.dir / tag), project=project)
        mask = self.rep.ravel()
        out = []
        for vec_red, axis, (pt, pz), y in calls:
            who = ("ours" if np.array_equal(vec_red, self.ours.ravel()[mask]) else
                   "data" if np.array_equal(vec_red, self.paper.ravel()[mask]) else "model")
            out.append((who, axis, pt, y))
        return out, steps

    def check(self, tag, ours, ours_pt, paper_pt):
        calls, steps = self.projections(tag, ours)
        self.assertEqual({c[0] for c in calls}, {"ours", "data", "model"})
        for who, axis, pt, y in calls:
            np.testing.assert_array_equal(pt, ours_pt if who == "ours" else paper_pt)
            ref = {"ours": self.ours, "data": self.paper}.get(who)
            if ref is not None and axis == "pz":
                want = (np.where(self.rep, ref, 0.0) * np.diff(pt)[:, None]).sum(axis=0)
                np.testing.assert_allclose(y, want, rtol=1e-12)
        # positions: the pT projection panel is drawn first, one step per curve
        pt_steps = steps[:3]
        labels = {lab: x for lab, x in pt_steps}
        np.testing.assert_array_equal(labels["This work (OmniFold)"], centres(ours_pt))
        np.testing.assert_array_equal(labels["Published (PRD 104, 092007)"], centres(paper_pt))
        np.testing.assert_array_equal(labels["Tune"], centres(paper_pt))

    def test_published_geometry_from_release_axis(self):
        self.check("anc075", "ours07", OUR_PT, PAPER_PT)

    def test_our_geometry_from_our_axis(self):
        self.check("anc07", "ours075", PAPER_PT, OUR_PT)

    def test_unchanged_where_no_published_width(self):
        old = self.base("2d-unfolding/compare_to_models.py", "ctm_base")
        new = new_module("compare_to_models.py", "ctm_new2")
        for tag, same_proj in (("anc07", True), ("anc075", False)):
            with self.subTest(paper=tag):
                run_main(old, self.argv(f"old_{tag}"), ANC_DIR=str(self.dir / tag))
                run_main(new, self.argv(f"new_{tag}"), ANC_DIR=str(self.dir / tag))
                for suffix in ("_report.txt", "_ratio_maps.png", "_projections.png"):
                    a = (self.dir / f"old_{tag}{suffix}").read_bytes()
                    b = (self.dir / f"new_{tag}{suffix}").read_bytes()
                    if suffix == "_projections.png" and not same_proj:
                        self.assertNotEqual(a, b, "the published projections ignore the release axis")
                    else:
                        self.assertEqual(a, b, suffix)

    def test_project_old_arguments(self):
        old = self.base("2d-unfolding/compare_to_models.py", "ctm_base2")
        new = new_module("compare_to_models.py", "ctm_new3")
        mask = self.rep.ravel()
        for axis in ("pt", "pz"):
            e_old, y_old = old.project(self.ours.ravel()[mask], mask, axis)
            e_new, y_new = new.project(self.ours.ravel()[mask], mask, axis)
            np.testing.assert_array_equal(e_old, e_new)
            np.testing.assert_array_equal(y_old, y_new)


def shape_chi2_ref(x_o, x_p, a_o, a_p, C, mask):
    """Unit-area shape chi^2 written out: s = x / sum(x a), J = (1 - s_p a_p^T) / tot_p, and the
    chi^2 taken in the (n-1)-dimensional range of J C J^T (orthogonal to a_p, its null vector)
    through an explicit orthonormal basis, so no pseudo-inverse threshold is involved."""
    use = mask & (np.diag(C) > 0)
    tot_o, tot_p = float((x_o * a_o)[use].sum()), float((x_p * a_p)[use].sum())
    s_o, s_p = x_o[use] / tot_o, x_p[use] / tot_p
    J = (np.eye(int(use.sum())) - np.outer(s_p, a_p[use])) / tot_p
    Cs = J @ C[np.ix_(use, use)] @ J.T
    q, _ = np.linalg.qr(np.column_stack([a_p[use], np.eye(int(use.sum()))[:, :-1]]))
    Q = q[:, 1:]                                         # orthonormal complement of a_p
    y = Q.T @ (s_o - s_p)
    return float(y @ np.linalg.solve(Q.T @ Cs @ Q, y))


class NormalizeShapeTest(Fixture):
    def run_new(self, tag, out, ours="ours07"):
        m = new_module("normalize_xsec_shape.py", f"nx_{out}")
        return run_main(m, ["--ours", self.dir / f"{ours}.root", "--out", self.dir / out],
                        ANC_DIR=str(self.dir / tag))

    def check(self, tag, ours, ours_pt, paper_pt, out):
        self.run_new(tag, out, ours)
        h = hist_dump(self.dir / out)
        rep, intr = self.rep.ravel(), (interior(paper_pt) & self.rep).ravel()
        a_o, a_p = areas(ours_pt).ravel(), areas(paper_pt).ravel()
        for name, pt, ref, a, mask in (("hXSecPaper2D_shape_205", paper_pt, self.paper, a_p, rep),
                                       ("hXSecPaper2D_shape_185", paper_pt, self.paper, a_p, intr),
                                       ("hXSec2D_shape_205", ours_pt, self.ours, a_o, rep),
                                       ("hXSec2D_shape_185", ours_pt, self.ours, a_o, intr)):
            got_pt, got_pz, s = h[name]
            np.testing.assert_array_equal(got_pt, pt, err_msg=name)
            np.testing.assert_array_equal(got_pz, PZ, err_msg=name)
            x = ref.ravel()
            want = np.where(mask, x / (x * a)[mask].sum(), 0.0)
            np.testing.assert_allclose(s.ravel(), want, rtol=1e-12, err_msg=name)
            self.assertAlmostEqual(float((s.ravel() * a)[mask].sum()), 1.0, places=12)
        xo, xp = self.ours.ravel(), self.paper.ravel()
        for key, C, mask in (("chi2_shape_205_total", self.cov, rep), ("chi2_shape_205_stat", 0.4 * self.cov, rep),
                             ("chi2_shape_185_total", self.cov, intr)):
            # pinv keeps a near-null eigenvalue the explicit basis excludes: agreement to ~1e-5
            self.assertAlmostEqual(h[key] / shape_chi2_ref(xo, xp, a_o, a_p, C, mask), 1.0, places=4, msg=key)

    def test_published_geometry_from_release_axis(self):
        self.check("anc075", "ours07", OUR_PT, PAPER_PT, "nx075.root")

    def test_our_geometry_from_our_axis(self):
        self.check("anc07", "ours075", PAPER_PT, OUR_PT, "nx_regen.root")

    def test_unchanged_where_no_published_width(self):
        old = self.base("2d-unfolding/normalize_xsec_shape.py", "nx_base")
        for tag in ("anc07", "anc075"):
            with self.subTest(paper=tag):
                _, so = run_main(old, ["--ours", self.dir / "ours07.root", "--out", self.dir / f"nxo_{tag}.root"],
                                 ANC_DIR=str(self.dir / tag))
                _, sn = self.run_new(tag, f"nxn_{tag}.root")
                a, b = hist_dump(self.dir / f"nxo_{tag}.root"), hist_dump(self.dir / f"nxn_{tag}.root")
                self.assertEqual(sorted(a), sorted(b))
                for k in a:
                    if tag == "anc075" and not k.startswith("hXSec2D_shape"):
                        continue        # paper shapes, the shape covariances and chi^2 use the paper's areas
                    va, vb = a[k], b[k]
                    for x, y in zip(va if isinstance(va, tuple) else (va,),
                                    vb if isinstance(vb, tuple) else (vb,)):
                        np.testing.assert_array_equal(x, y, err_msg=k)
                if tag == "anc07":
                    self.assertEqual(so.replace(f"nxo_{tag}", "X"), sn.replace(f"nxn_{tag}", "X"))

    def test_old_arguments(self):
        old = self.base("2d-unfolding/normalize_xsec_shape.py", "nx_base2")
        new = new_module("normalize_xsec_shape.py", "nx_new2")
        np.testing.assert_array_equal(old.bin_widths(), new.bin_widths())
        np.testing.assert_array_equal(old.interior_mask(), new.interior_mask())
        s = self.ours.ravel()
        ho, hn = old.shape_to_th2d("a", "", s), new.shape_to_th2d("b", "", s)
        for x, y in zip(rc.th2d_edges(ho), rc.th2d_edges(hn)):
            np.testing.assert_array_equal(x, y)

    def test_transposed_release_is_refused(self):
        p = self.dir / "transposed" / "cov_ptpl_minerva_inclusive_6GeV.root"
        p.parent.mkdir(exist_ok=True)
        self.write_paper(p, PAPER_PT, transpose=True)
        for rel, name in (("normalize_xsec_shape.py", "nx_t"), ("compare_to_paper_interior.py", "ci_t")):
            m = new_module(rel, name)
            f = ROOT.TFile.Open(str(p))
            with self.subTest(module=rel), self.assertRaises(ValueError):
                m.fill_paper(f.Get("pt_pl_cross_section"))
            f.Close()

    NOTE = "[NOTE] cross-grid shape chi2: our cell areas differ from the release axis's; not a note number"

    def test_cross_grid_note_and_closure(self):
        """One NOTE line exactly when the two sides' areas differ; every closure integral prints 1."""
        for tag, ours, cross in (("anc075", "ours07", True), ("anc07", "ours075", True),
                                 ("anc075", "ours075", False), ("anc07", "ours07", False)):
            with self.subTest(release=tag, ours=ours):
                _, out = self.run_new(tag, f"nx_note_{tag}_{ours}.root", ours)
                lines = out.splitlines()
                self.assertEqual(lines.count(self.NOTE), 1 if cross else 0)
                self.assertEqual(sum("cross-grid" in line for line in lines), 1 if cross else 0)
                closure = [line for line in lines if "closure: shape integral on" in line]
                self.assertEqual([line.split(" on ")[1].split(" =")[0] for line in closure],
                                 ["205 ours", "205 paper", "185 ours", "185 paper"])
                for line in closure:
                    self.assertTrue(line.endswith("= 1.0000000000"), line)


@unittest.skipUnless(HAVE_DEPS, "PyROOT or matplotlib unavailable")
class WellConditionedShapeChi2Test(unittest.TestCase):
    """shape_chi2's cross-grid projection equals the exact pseudo-inverse chi^2 on a small,
    well-conditioned case: C full rank, C_shape = J C J^T of rank n - 1 with null vector w."""

    def test_projected_chi2_is_the_exact_pseudo_inverse(self):
        nx = new_module("normalize_xsec_shape.py", "nx_wellcond")
        rng = np.random.default_rng(3)
        n = 7
        A = rng.standard_normal((n, n))
        Q0, _ = np.linalg.qr(A)
        C = Q0 @ np.diag(np.linspace(1.0, 4.0, n)) @ Q0.T          # full rank, condition number 4
        w = rng.uniform(0.5, 1.5, n)                                  # paper areas
        w_ours = w * rng.uniform(0.8, 1.2, n)                         # different areas
        x_p = rng.uniform(1.0, 2.0, n)
        x_o = x_p * rng.uniform(0.95, 1.05, n)
        mask = np.ones(n, dtype=bool)
        with contextlib.redirect_stdout(io.StringIO()):
            chi2, ndf, s_o, s_p, C_shape, idx = nx.shape_chi2(x_o, x_p, w, C, mask, "t", w_ours)
        self.assertEqual(ndf, n - 1)
        np.testing.assert_allclose(C_shape @ w, 0.0, atol=1e-12)    # w spans C_shape's null space
        ev = np.linalg.eigvalsh(C_shape)
        self.assertGreater(ev[1] / ev[-1], 1e-3)                      # well conditioned on its range
        # exact pseudo-inverse: invert C_shape on an orthonormal basis of the complement of w
        q, _ = np.linalg.qr(np.column_stack([w, np.eye(n)[:, :-1]]))
        B = q[:, 1:]
        np.testing.assert_allclose(B.T @ w, 0.0, atol=1e-12)
        y = B.T @ (s_o - s_p)
        ref = float(y @ np.linalg.solve(B.T @ C_shape @ B, y))
        self.assertLessEqual(abs(chi2 / ref - 1.0), 1e-10)
        self.assertGreater(abs(float((s_o - s_p) @ w)), 1e-5)         # the projection had work to do


class InteriorTest(Fixture):
    def argv(self, out, ours="ours07"):
        return ["--ours", self.dir / f"{ours}.root", "--out", self.dir / out]

    def scan(self, stdout):
        """The p|| scan table: [(p|| cut, N, chi2)]."""
        rows = []
        for line in stdout.splitlines():
            if line.startswith("  p||>="):
                tok = line[len("  p||>="):].split()
                rows.append((float(tok[0]), int(tok[1]), float(tok[2])))
        return rows

    def test_mask_and_scan_read_release_axis(self):
        """A release axis that moves one cell across tan(20 deg) moves it in the mask and the scan."""
        m = new_module("compare_to_paper_interior.py", "ci_new")
        _, s075 = run_main(m, self.argv("i075.png"), ANC_DIR=str(self.dir / "anc075"))
        _, s053 = run_main(m, self.argv("i053.png"), ANC_DIR=str(self.dir / "anc053"))
        n = [int(line.split(":")[1].split("/")[0]) for s in (s075, s053) for line in s.splitlines()
             if "bins in strict interior" in line]
        self.assertEqual(n[1], n[0] + 1)
        np.testing.assert_array_equal(np.flatnonzero(m.interior_mask(PT053, PZ) != m.interior_mask(PAPER_PT, PZ)),
                                      [6 * N_PZ])
        diff = (self.ours - self.paper).ravel()
        for stdout, pt in ((s075, PAPER_PT), (s053, PT053)):
            rows = self.scan(stdout)
            self.assertEqual(len(rows), 6)
            for k, (cut, n_got, chi2_got) in enumerate(rows):
                sel = interior(pt) & self.rep
                sel[:, :k] = False
                sel = sel.ravel()
                d = diff[sel]
                chi2 = float(d @ np.linalg.pinv(self.cov[np.ix_(sel, sel)]) @ d)
                self.assertEqual(cut, PZ[k])
                self.assertEqual(n_got, int(sel.sum()))
                self.assertAlmostEqual(chi2_got, chi2, places=1)
        self.assertEqual(self.scan(s053)[0][1], self.scan(s075)[0][1] + int(self.rep[6, 0]))

    def test_no_cell_changes_membership_on_the_release_axis(self):
        m = new_module("compare_to_paper_interior.py", "ci_new2")
        np.testing.assert_array_equal(m.interior_mask(PAPER_PT, PZ), m.interior_mask())

    def test_our_axis_is_not_used(self):
        """Our result enters only through its contents: ours on the release grid prints the same."""
        m = new_module("compare_to_paper_interior.py", "ci_new4")
        _, a = run_main(m, self.argv("ia.png", "ours07"), ANC_DIR=str(self.dir / "anc075"))
        _, b = run_main(m, self.argv("ib.png", "ours075"), ANC_DIR=str(self.dir / "anc075"))
        self.assertEqual(a.replace("ours07.root", "X").replace("ia.png", "Y"),
                         b.replace("ours075.root", "X").replace("ib.png", "Y"))

    def test_output_unchanged(self):
        old = self.base("2d-unfolding/compare_to_paper_interior.py", "ci_base")
        new = new_module("compare_to_paper_interior.py", "ci_new3")
        for tag in ("anc07", "anc075"):
            with self.subTest(paper=tag):
                _, so = run_main(old, self.argv(f"io_{tag}.png"), ANC_DIR=str(self.dir / tag))
                _, sn = run_main(new, self.argv(f"in_{tag}.png"), ANC_DIR=str(self.dir / tag))
                self.assertEqual(so.replace(f"io_{tag}", "X"), sn.replace(f"in_{tag}", "X"))
                self.assertEqual((self.dir / f"io_{tag}.png").read_bytes(),
                                 (self.dir / f"in_{tag}.png").read_bytes())


class StripRatioTest(Fixture):
    NEW_KEY = "area_max_reldev_vs_paper_axis"

    def run_receipt(self, module, tag, ours, out):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            rv, _ = run_main(module, ["--anc-dir", self.dir / tag,
                                      "--ours", f"x={self.dir / ours}.root:hXSec2D", "--out", self.dir / out])
        return rv, err.getvalue()

    def receipt(self, tag, ours, out):
        m = new_module("strip_ratio_receipt.py", f"sr_{out}")
        rv, err = self.run_receipt(m, tag, ours, out)
        self.assertEqual(rv, 0, err)
        return m, json.loads((self.dir / out).read_text())

    def check_strips(self, rows, mask, ours_pt, paper_pt):
        for j, row in enumerate(rows):
            sel = mask[:, j]
            if not sel.any():
                self.assertIsNone(row)
                continue
            self.assertEqual((row["pz_lo"], row["pz_hi"]), (PZ[j], PZ[j + 1]))
            self.assertAlmostEqual(row["S_paper"] / float((self.paper * areas(paper_pt))[:, j][sel].sum()), 1, 12)
            self.assertAlmostEqual(row["S_ours"] / float((self.ours * areas(ours_pt))[:, j][sel].sum()), 1, 12)

    def check_contrast(self, con, ours, mask, ours_pt, paper_pt):
        lo = mask & (PZ[None, :-1] >= 1.5) & (PZ[None, 1:] <= 2.5)
        hi = mask & (PZ[None, :-1] >= 20.0) & (PZ[None, 1:] <= 60.0)
        a_o, a_p = areas(ours_pt), areas(paper_pt)
        Rl = (ours * a_o)[lo].sum() / (self.paper * a_p)[lo].sum()
        Rh = (ours * a_o)[hi].sum() / (self.paper * a_p)[hi].sum()
        g = (-Rl * np.where(lo, a_p, 0) / (self.paper * a_p)[lo].sum()
             + Rh * np.where(hi, a_p, 0) / (self.paper * a_p)[hi].sum()).ravel()
        self.assertAlmostEqual(con["R_low"] / Rl, 1, 12)
        self.assertAlmostEqual(con["R_high"] / Rh, 1, 12)
        self.assertAlmostEqual(con["sigma_diff_paper_total"] / math.sqrt(g @ self.cov @ g), 1, 10)

    def check(self, tag, ours, ours_pt, paper_pt, out):
        m, r = self.receipt(tag, ours, out)
        res = r["results"]["x"]
        intr = interior(paper_pt) & self.rep
        self.assertEqual(r["n_interior"], int(intr.sum()))
        self.check_strips(res["reported_205"]["strips"], self.rep, ours_pt, paper_pt)
        self.check_strips(res["interior_185"]["strips"], intr, ours_pt, paper_pt)
        self.check_contrast(res["reported_205"]["contrast"], self.ours, self.rep, ours_pt, paper_pt)
        self.check_contrast(res["interior_185"]["contrast"], self.ours, intr, ours_pt, paper_pt)
        fac = m.historical_factor(PZ)[None, :]
        pc = res["power_control_historical_gradient_injected"]["interior_185"]
        self.check_contrast(pc["contrast"], self.ours * fac, intr, ours_pt, paper_pt)
        return r

    def test_release_axis(self):
        r = self.check("anc075", "ours07", OUR_PT, PAPER_PT, "s075.json")
        # |0.07 / 0.075 - 1| and |0.08 / 0.075 - 1| in the first two pT bins
        self.assertAlmostEqual(r["inputs"]["x"][self.NEW_KEY], 1 / 15, places=12)
        # the recorded field keeps its meaning: release axis against bin_mapping.txt's printed edges
        self.assertAlmostEqual(r["paper_th2d_axis_area_max_reldev_vs_authoritative"], 0.075 / 0.07 - 1, places=12)

    def test_our_input_on_release_grid(self):
        r = self.check("anc075", "ours075", PAPER_PT, PAPER_PT, "s_regen.json")
        self.assertNotIn(self.NEW_KEY, r["inputs"]["x"])

    def test_edge_moving_release(self):
        r = self.check("anc053", "ours07", OUR_PT, PT053, "s053.json")
        _, r075 = self.receipt("anc075", "ours07", "s075b.json")
        self.assertEqual(r["n_interior"], r075["n_interior"] + int(self.rep[6, 0]))

    def test_grid_guard(self):
        m = new_module("strip_ratio_receipt.py", "sr_guard")
        for tag, ours, ok in (("anc075", "ours07", True), ("anc075", "ours075", True), ("anc053", "ours07", True),
                              ("anc07", "ours07", True), ("anc07", "ours075", False), ("anc075", "ours053", False),
                              ("anc075", "ours_off", False), ("anc075", "ours_badpz", False)):
            with self.subTest(release=tag, ours=ours):
                rv, err = self.run_receipt(m, tag, ours, f"g_{tag}_{ours}.json")
                if ok:
                    self.assertEqual(rv, 0, err)
                else:
                    self.assertEqual(rv, 3)
                    self.assertIn("bin edges differ from the paper grid", err)

    def test_non_positive_area_is_refused(self):
        m = new_module("strip_ratio_receipt.py", "sr_area")

        class Axis:
            def __init__(self, w):
                self.w = w

            def GetBinWidth(self, i):
                return self.w[i - 1]

        class Hist:
            def GetName(self):
                return "stub"

            def GetNbinsX(self):
                return N_PT

            def GetNbinsY(self):
                return N_PZ

            def GetXaxis(self):
                return Axis(np.r_[0.0, np.diff(OUR_PT)[1:]])

            def GetYaxis(self):
                return Axis(np.diff(PZ))

        with self.assertRaisesRegex(ValueError, "non-positive bin area"):
            m.positive_areas(Hist())

    def test_json_equal_to_base_on_our_grid(self):
        old = self.base("2d-unfolding/strip_ratio_receipt.py", "sr_base")
        new = new_module("strip_ratio_receipt.py", "sr_new3")
        self.assertEqual(self.run_receipt(old, "anc07", "ours07", "so.json")[0], 0)
        self.assertEqual(self.run_receipt(new, "anc07", "ours07", "sn.json")[0], 0)
        a = json.loads((self.dir / "so.json").read_text())
        b = json.loads((self.dir / "sn.json").read_text())
        self.assertNotIn(self.NEW_KEY, b["inputs"]["x"])
        self.assertEqual(a, b)

    def test_old_arguments(self):
        old = self.base("2d-unfolding/strip_ratio_receipt.py", "sr_base2")
        new = new_module("strip_ratio_receipt.py", "sr_new4")
        np.testing.assert_array_equal(old.interior_mask(), new.interior_mask())
        np.testing.assert_array_equal(old.historical_factor(), new.historical_factor())
        ipt, ipz = old.strip_index()
        area = np.diff(OUR_PT)[ipt] * np.diff(PZ)[ipz]
        args = (self.ours.ravel(), self.paper.ravel(), area, self.cov, self.rep.ravel())
        self.assertEqual(old.measure(*args), new.measure(*args))


class Fig67Test(Fixture):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        d = cls.dir
        n = len(cls.cells)
        rng = np.random.default_rng(5)
        flat = cls.ours.ravel()[cls.cells]
        cls.total = np.zeros((n, n))
        for name, hname, s in (("uni.root", "hCov_universe_Flux", 0.04), ("boot.root", "hCov2D_reported", 0.02)):
            f = ROOT.TFile.Open(str(d / name), "RECREATE")
            g = s * flat[:, None] * rng.standard_normal((n, 3))
            c = g @ g.T + np.diag((0.01 * flat) ** 2)
            cls.total += c
            h = ROOT.TH2D(hname, "", n, 0, n, n, 0, n)
            for i in range(n):
                for j in range(n):
                    h.SetBinContent(i + 1, j + 1, float(c[i, j]))
            h.Write()
            rc.identity_hist(cls.cells).Write()
            f.Close()
        # ML seed covariances for --include-ml auto: one above the 0.002 draw threshold, one below
        cls.ml = {}
        for name, s in (("ml_big.root", 0.03), ("ml_small.root", 1e-5)):
            c = np.diag((s * flat) ** 2)
            cls.ml[name] = c
            f = ROOT.TFile.Open(str(d / name), "RECREATE")
            h = ROOT.TH2D("hCov2D_reported", "", n, 0, n, n, 0, n)
            for i in range(n):
                h.SetBinContent(i + 1, i + 1, float(c[i, i]))
            h.Write()
            rc.identity_hist(cls.cells).Write()
            f.Close()

    def argv(self, tag, prefix, ours="ours07", ml=("never", "")):
        d = self.dir
        return ["--xsec-root", d / f"{ours}.root", "--universe-root", d / "uni.root",
                "--bootstrap-root", d / "boot.root", "--include-ml", ml[0], "--ml-root", ml[1],
                "--paper-root", self.anc(tag), "--out-prefix", d / prefix, "--projections-json", d / f"{prefix}.json"]

    def test_ml_auto_found_and_drawn(self):
        """--include-ml auto with an ML file above the threshold: drawn, on our input's axis."""
        m = new_module("uq/plot_uncertainty_fig6_7_style.py", "f67_ml_big")
        with spy("stairs") as stairs:
            run_main(m, self.argv("anc07", "f_ml_big", "ours075", ("auto", self.dir / "ml_big.root")))
        got = json.loads((self.dir / "f_ml_big.json").read_text())
        C_ml = self.ml["ml_big.root"]
        for axis in ("pt", "pz"):
            np.testing.assert_allclose(got[axis]["ML"], self.frac(self.ours, PAPER_PT, C_ml, axis), rtol=1e-10)
            np.testing.assert_allclose(got[axis]["Total"], self.frac(self.ours, PAPER_PT, self.total + C_ml, axis),
                                       rtol=1e-10)
        drawn = {lab: e for lab, e in stairs if len(e) == N_PT + 1}
        np.testing.assert_array_equal(drawn["ML"], PAPER_PT)
        summary = (self.dir / "f_ml_big_summary.txt").read_text()
        self.assertIn(f"ml_root: {self.dir / 'ml_big.root'}", summary)

    def test_ml_auto_below_threshold_is_not_drawn(self):
        m = new_module("uq/plot_uncertainty_fig6_7_style.py", "f67_ml_small")
        run_main(m, self.argv("anc07", "f_ml_small", "ours075", ("auto", self.dir / "ml_small.root")))
        got = json.loads((self.dir / "f_ml_small.json").read_text())
        C_ml = self.ml["ml_small.root"]
        for axis in ("pt", "pz"):
            self.assertNotIn("ML", got[axis])
            np.testing.assert_allclose(got[axis]["Total"], self.frac(self.ours, PAPER_PT, self.total + C_ml, axis),
                                       rtol=1e-10)
        self.assertIn("ML (not drawn)", (self.dir / "f_ml_small_summary.txt").read_text())

    def test_ml_auto_missing_file_is_skipped(self):
        m = new_module("uq/plot_uncertainty_fig6_7_style.py", "f67_ml_missing")
        run_main(m, self.argv("anc075", "f_ml_missing", "ours07", ("auto", self.dir / "no_such_ml.root")))
        run_main(m, self.argv("anc075", "f_ml_never", "ours07"))
        self.assertEqual(json.loads((self.dir / "f_ml_missing.json").read_text()),
                         json.loads((self.dir / "f_ml_never.json").read_text()))
        self.assertIn("ml_root: (not used)", (self.dir / "f_ml_missing_summary.txt").read_text())

    def test_ml_auto_unchanged_on_our_grid(self):
        old = self.base("2d-unfolding/uq/plot_uncertainty_fig6_7_style.py", "f67_ml_base")
        new = new_module("uq/plot_uncertainty_fig6_7_style.py", "f67_ml_new")
        ml = ("auto", self.dir / "ml_big.root")
        run_main(old, self.argv("anc07", "fmo", "ours07", ml))
        run_main(new, self.argv("anc07", "fmn", "ours07", ml))
        self.assertEqual((self.dir / "fmo.json").read_bytes(), (self.dir / "fmn.json").read_bytes())
        for suffix in ("_pt.png", "_pz.png"):
            self.assertEqual((self.dir / f"fmo{suffix}").read_bytes(), (self.dir / f"fmn{suffix}").read_bytes())
        self.assertEqual((self.dir / "fmo_summary.txt").read_text().replace("fmo", "X"),
                         (self.dir / "fmn_summary.txt").read_text().replace("fmn", "X"))

    def frac(self, x, pt, C, axis):
        w = np.diff(PZ)[None, :] if axis == "pt" else np.diff(pt)[:, None]
        P = np.zeros((N_PT if axis == "pt" else N_PZ, len(self.cells)))
        for k, gid in enumerate(self.cells):
            ipt, ipz = divmod(int(gid), N_PZ)
            P[ipt if axis == "pt" else ipz, k] = w[0, ipz] if axis == "pt" else w[ipt, 0]
        central = (np.where(self.rep, x, 0.0) * w).sum(axis=1 if axis == "pt" else 0)
        return np.sqrt(np.diag(P @ C @ P.T)) / np.abs(central)

    def check(self, tag, ours, ours_pt, paper_pt, prefix):
        m = new_module("uq/plot_uncertainty_fig6_7_style.py", f"f67_{prefix}")
        with spy("stairs") as stairs:
            run_main(m, self.argv(tag, prefix, ours))
        got = json.loads((self.dir / f"{prefix}.json").read_text())
        C = self.cov[np.ix_(self.cells, self.cells)]
        for axis in ("pt", "pz"):
            np.testing.assert_allclose(got[axis]["Published total"], self.frac(self.paper, paper_pt, C, axis),
                                       rtol=1e-10, err_msg=axis)
            np.testing.assert_allclose(got[axis]["Total"], self.frac(self.ours, ours_pt, self.total, axis),
                                       rtol=1e-10, err_msg=axis)
        drawn = {lab: e for lab, e in stairs if len(e) == N_PT + 1}     # the pT panel
        np.testing.assert_array_equal(drawn["Total"], ours_pt)
        np.testing.assert_array_equal(drawn["Published total"], paper_pt)

    def test_published_geometry_from_release_axis(self):
        self.check("anc075", "ours07", OUR_PT, PAPER_PT, "f075")

    def test_our_geometry_from_our_axis(self):
        self.check("anc07", "ours075", PAPER_PT, OUR_PT, "f_regen")

    def test_unchanged_where_no_published_width(self):
        old = self.base("2d-unfolding/uq/plot_uncertainty_fig6_7_style.py", "f67_base")
        new = new_module("uq/plot_uncertainty_fig6_7_style.py", "f67_new2")
        for tag in ("anc07", "anc075"):
            with self.subTest(paper=tag):
                run_main(old, self.argv(tag, f"fo_{tag}"))
                run_main(new, self.argv(tag, f"fn_{tag}"))
                a = json.loads((self.dir / f"fo_{tag}.json").read_text())
                b = json.loads((self.dir / f"fn_{tag}.json").read_text())
                if tag == "anc07":
                    self.assertEqual(a, b)
                    for suffix in ("_pt.png", "_pz.png"):
                        self.assertEqual((self.dir / f"fo_{tag}{suffix}").read_bytes(),
                                         (self.dir / f"fn_{tag}{suffix}").read_bytes())
                    so = (self.dir / f"fo_{tag}_summary.txt").read_text().replace(f"fo_{tag}", "X")
                    sn = (self.dir / f"fn_{tag}_summary.txt").read_text().replace(f"fn_{tag}", "X")
                    self.assertEqual(so, sn)
                else:
                    # dsigma/dpT sums over p_parallel only, so only the p_parallel projection of the
                    # published total takes the pT widths
                    for axis in a:
                        for label in a[axis]:
                            if label != "Published total" or axis == "pt":
                                self.assertEqual(a[axis][label], b[axis][label], f"{axis} {label}")
                    self.assertNotEqual(a["pz"]["Published total"], b["pz"]["Published total"])

    def test_old_arguments(self):
        old = self.base("2d-unfolding/uq/plot_uncertainty_fig6_7_style.py", "f67_base2")
        new = new_module("uq/plot_uncertainty_fig6_7_style.py", "f67_new3")
        xo, xn = old.load_xsec(str(self.dir / "ours07.root")), new.load_xsec(str(self.dir / "ours07.root"))
        self.assertEqual(len(xn), 2)
        for a, b in zip(xo, xn):
            np.testing.assert_array_equal(a, b)
        po = old.load_paper_total(str(self.anc("anc075")), xo[1])
        pn = new.load_paper_total(str(self.anc("anc075")), xo[1])
        self.assertEqual(len(pn), 2)
        for a, b in zip(po, pn):
            np.testing.assert_array_equal(a, b)
        for axis in ("pt", "pz"):
            np.testing.assert_array_equal(old.projection_matrix(axis, xo[1]), new.projection_matrix(axis, xo[1]))
            np.testing.assert_array_equal(old.central_projection(xo[0], xo[1], axis),
                                          new.central_projection(xo[0], xo[1], axis))

    def test_bad_release_shape_is_refused(self):
        p = self.dir / "bad14" / "cov_ptpl_minerva_inclusive_6GeV.root"
        p.parent.mkdir(exist_ok=True)
        f = ROOT.TFile.Open(str(p), "RECREATE")
        ROOT.TH2D("pt_pl_cross_section", "", N_PT, 0, 1, N_PT, 0, 1).Write()
        ROOT.TMatrixD(rc.N_CELLS, rc.N_CELLS).Write("TotalCovariance")
        f.Close()
        m = new_module("uq/plot_uncertainty_fig6_7_style.py", "f67_bad")
        with self.assertRaises(SystemExit) as cm:
            m.load_paper_total(str(p), self.rep)
        self.assertIn("expected 14 x 16", str(cm.exception))


class Fig13Test(Fixture):
    def infile(self, ours):
        """Our file with what load_result reads; the truth-flux steps are stubbed in stub()."""
        path = self.dir / f"f13_{ours}.root"
        if not path.exists():
            f = ROOT.TFile.Open(str(self.dir / f"{ours}.root"))
            h = f.Get("hXSec2D")
            g = ROOT.TFile.Open(str(path), "RECREATE")
            for name in ("hXSec2D", "hOFTruthDenom2D", "hEff2D"):
                h.Clone(name).Write()
            ROOT.TParameter("double")("dataPOT", 1.0).Write()
            ROOT.TParameter("double")("nNucleons", 1.0).Write()
            g.Close()
            f.Close()
        return path

    @staticmethod
    def stub(m):
        return dict(load_flux_bins_for_truth=lambda *a: (None, "stub"),
                    compute_truth_xsec_2d=lambda h_truth, *a: h_truth.Clone("truth"))

    def main(self, m, tag, ours, out, *extra):
        plt.close("all")
        run_main(m, ["--infile", self.infile(ours), "--paper", self.anc(tag), "--out", self.dir / out, *extra],
                 **self.stub(m))
        fig = plt.gcf()
        return fig.axes

    @staticmethod
    def title(ax):
        return next(t.get_text() for t in ax.texts if "<" in t.get_text())

    @staticmethod
    def points(ax):
        """{label: x} of the errorbar points."""
        return {c.get_label(): np.asarray(c.lines[0].get_xdata()) for c in ax.containers}

    @staticmethod
    def xbars(ax):
        """{label: [(x_lo, x_hi)]} of the errorbar x-error segments (the first bar collection)."""
        return {c.get_label(): np.array([[s[0][0], s[1][0]] for s in c.lines[2][0].get_segments()])
                for c in ax.containers}

    def test_published_xerr_on_release_axis(self):
        """The published x-errors span the release bins mapped onto our display axis; ours span ours."""
        m = new_module("plot_2d_threeway_fig13.py", "f13_xerr")
        for tag, ours, ours_pt, paper_pt in (("anc075", "ours053", PT053, PAPER_PT),
                                             ("anc07", "ours075", PAPER_PT, OUR_PT)):
            with self.subTest(release=tag, ours=ours):
                axes = self.main(m, tag, ours, f"f13_xerr_{ours}.png")
                d_ours = disp(ours_pt)
                p_disp = np.interp(paper_pt, ours_pt, d_ours)
                for ax in axes[16:]:                                  # p_parallel slices, along pT
                    bars = self.xbars(ax)
                    np.testing.assert_allclose(bars["Published (PRD 104, 092007)"],
                                               np.column_stack([p_disp[:-1], p_disp[1:]]), rtol=0, atol=1e-12)
                    np.testing.assert_allclose(bars["This work (OmniFold)"],
                                               np.column_stack([d_ours[:-1], d_ours[1:]]), rtol=0, atol=1e-12)
                half = 0.5 * np.diff(p_disp)
                self.assertFalse(np.allclose(half, 0.5 * np.diff(d_ours)))   # the two differ on these grids

    def test_main_geometry(self):
        """Ours on an off-grid axis (0.53): titles, ticks and our points follow it; the published
        points sit at the release axis (0.075 grid) mapped onto that display axis."""
        m = new_module("plot_2d_threeway_fig13.py", "f13_main")
        axes = self.main(m, "anc075", "ours053", "f13_main.png")
        pt_axes, pz_axes = axes[:N_PT], axes[16:]
        self.assertEqual(len(pz_axes), N_PZ)
        self.assertEqual(self.title(pt_axes[6]), "0.475 < p_T < 0.53")
        self.assertEqual(self.title(pt_axes[7]), "0.53 < p_T < 0.70")
        self.assertEqual(self.title(pz_axes[9]), "7.00 < p_|| < 8.00")
        d_ours = disp(PT053)
        np.testing.assert_allclose(pz_axes[0].get_xticks(), np.interp([0.4, 1.0, 1.5, 2.5, 4.5], PT053, d_ours))
        self.assertEqual(pz_axes[0].get_xlim(), (0.0, d_ours[-1]))
        pts = self.points(pz_axes[3])
        np.testing.assert_allclose(pts["This work (OmniFold)"], centres(d_ours))
        np.testing.assert_allclose(pts["Published (PRD 104, 092007)"], centres(np.interp(PAPER_PT, PT053, d_ours)))
        d_pz = disp(PZ)
        np.testing.assert_allclose(pt_axes[0].get_xticks(), np.interp([4, 10, 20, 40, 60], PZ, d_pz))

    def test_main_pt_only(self):
        m = new_module("plot_2d_threeway_fig13.py", "f13_ptonly")
        axes = self.main(m, "anc075", "ours053", "f13_ptonly.png", "--pt-only")
        self.assertEqual(self.title(axes[6]), "0.475 < p_T < 0.53")
        self.assertEqual(self.title(axes[13]), "2.50 < p_T < 4.50")
        d_pz = disp(PZ)
        np.testing.assert_allclose(axes[0].get_xticks(), np.interp([4, 10, 20, 40, 60], PZ, d_pz))
        pts = self.points(axes[2])
        np.testing.assert_allclose(pts["This work (OmniFold)"], centres(d_pz))
        np.testing.assert_allclose(pts["Published (PRD 104, 092007)"], centres(d_pz))

    def test_main_our_input_on_release_grid(self):
        m = new_module("plot_2d_threeway_fig13.py", "f13_regen")
        axes = self.main(m, "anc07", "ours075", "f13_regen.png")
        self.assertEqual([self.title(a) for a in axes[:N_PT]][:7],
                         ["0.00 < p_T < 0.075", "0.075 < p_T < 0.15", "0.15 < p_T < 0.25", "0.25 < p_T < 0.325",
                          "0.325 < p_T < 0.40", "0.40 < p_T < 0.475", "0.475 < p_T < 0.55"])
        d_ours = disp(PAPER_PT)
        pz_axes = axes[16:]
        self.assertEqual(pz_axes[0].get_xlim(), (0.0, d_ours[-1]))
        pts = self.points(pz_axes[3])
        np.testing.assert_allclose(pts["This work (OmniFold)"], centres(d_ours))
        np.testing.assert_allclose(pts["Published (PRD 104, 092007)"], centres(np.interp(OUR_PT, PAPER_PT, d_ours)))

    def test_main_unchanged_on_our_grid(self):
        old = self.base("2d-unfolding/plot_2d_threeway_fig13.py", "f13_base")
        new = new_module("plot_2d_threeway_fig13.py", "f13_new")
        for extra in ((), ("--pt-only",)):
            with self.subTest(extra=extra):
                titles = []
                for m, out in ((old, "f13_old.png"), (new, "f13_new.png")):
                    axes = self.main(m, "anc07", "ours07", out, *extra)
                    titles.append([self.title(a) for a in axes if any("<" in t.get_text() for t in a.texts)])
                self.assertEqual(len(titles[1]), N_PT if extra else N_PT + N_PZ)
                self.assertEqual(titles[0], titles[1])
                self.assertEqual((self.dir / "f13_old.png").read_bytes(), (self.dir / "f13_new.png").read_bytes())

    def test_edge_label(self):
        m = new_module("plot_2d_threeway_fig13.py", "f13_label")
        for x, want in ((0.07, "0.07"), (0.075, "0.075"), (0.325, "0.325"), (0.475, "0.475"), (1.5, "1.50"),
                        (0.0, "0.00"), (60.0, "60.00")):
            self.assertEqual(m.edge_label(x), want)
        for x in np.r_[OUR_PT, PZ]:
            self.assertEqual(m.edge_label(float(x)), f"{x:.2f}")

    def test_old_arguments(self):
        old = self.base("2d-unfolding/plot_2d_threeway_fig13.py", "f13_base2")
        new = new_module("plot_2d_threeway_fig13.py", "f13_new2")
        path = str(self.infile("ours07"))
        for k, v in self.stub(old).items():
            setattr(old, k, v)
        for k, v in self.stub(new).items():
            setattr(new, k, v)
        ro, rn = old.load_result(path), new.load_result(path)
        self.assertEqual(len(rn), 4)
        for a, b in zip(ro, rn):
            np.testing.assert_array_equal(a, b)
        po, pn = old.paper_arrays(str(self.anc("anc075"))), new.paper_arrays(str(self.anc("anc075")))
        self.assertEqual(len(pn), 3)
        for a, b in zip(po, pn):
            np.testing.assert_array_equal(a, b)
        for m, out in ((old, "f13_draw_old.png"), (new, "f13_draw_new.png")):
            fig = plt.figure(figsize=(10.4, 13.2))
            outer = fig.add_gridspec(2, 1)
            err = 0.05 * self.paper
            m.plot_pt_slices(fig, outer[0], self.paper, err, self.rep, self.ours, err, self.model)
            m.plot_pz_slices(fig, outer[1], self.paper, err, self.rep, self.ours, err, self.model)
            fig.savefig(self.dir / out, dpi=60)
            plt.close(fig)
        self.assertEqual((self.dir / "f13_draw_old.png").read_bytes(), (self.dir / "f13_draw_new.png").read_bytes())

    def test_transposed_release_is_refused(self):
        p = self.dir / "transposed13" / "cov_ptpl_minerva_inclusive_6GeV.root"
        p.parent.mkdir(exist_ok=True)
        self.write_paper(p, PAPER_PT, transpose=True)
        m = new_module("plot_2d_threeway_fig13.py", "f13_t")
        with self.assertRaises(RuntimeError):
            m.paper_arrays(str(p))


# main before plot_2d_cross_section.py drew on its inputs' own axes
BASE_XS = "359ee648e6528689a77ff380cdf06313dff907d1"


def base_module_at(sha, rel, name, d):
    """The file at commit sha, written to directory d and imported as module `name`; None when git
    or sha is unavailable."""
    try:
        src = subprocess.run(["git", "-C", str(REPO), "show", f"{sha}:{rel}"],
                             capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    path = Path(d) / f"{name}.py"
    path.write_bytes(src)
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def th1_dump(h):
    n = h.GetNbinsX()
    return (np.array([h.GetXaxis().GetBinLowEdge(i) for i in range(1, n + 2)]),
            np.array([h.GetBinContent(i) for i in range(1, n + 1)]),
            np.array([h.GetBinError(i) for i in range(1, n + 1)]))


@unittest.skipUnless(HAVE_DEPS, "PyROOT or matplotlib unavailable")
class CrossSectionPlotEdges(unittest.TestCase):
    """plot_2d_cross_section.py (and plot_2d_paper_comparison.py, which imports its slices) on its
    input's own axes: on our grid every value, string and output equals BASE_XS's; on the release's
    grid the labels, projection widths and efficiency map follow the 0.075 / 0.325 / 0.475 axis."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls.tmp.name)
        rng = np.random.default_rng(23)
        cls.cont = rng.lognormal(0.0, 0.5, rc.GRID_SHAPE)
        cls.err = 0.05 * cls.cont
        cls.eff = rng.uniform(0.2, 0.95, rc.GRID_SHAPE)
        cls.truth = 1e4 * cls.cont * (1 + 0.1 * rng.standard_normal(rc.GRID_SHAPE))
        cls.flux = 1e-4 * (2 + np.arange(N_PT))
        for tag, pt in (("g07", OUR_PT), ("g075", PAPER_PT)):
            cls.write_input(cls.dir / f"{tag}.root", pt)
        for name, kw in (("eff", "hEff2D"), ("flux", "hFlux_pt"), ("truth", "hOFTruthDenom2D"), ("xpt", "hXSec_pt")):
            cls.write_input(cls.dir / f"mixed_{name}.root", PAPER_PT, other={kw: OUR_PT})
        pz = PZ.copy()
        pz[9] = 7.5
        cls.write_input(cls.dir / "mixed_xpz.root", PAPER_PT, other={"hXSec_pz": pz})
        cls.write_input(cls.dir / "mixed_truthpz.root", PAPER_PT, other={"hOFTruthDenom2D": (PAPER_PT, pz)})
        cls.write_input(cls.dir / "noflux075.root", PAPER_PT, skip=("hFlux_pt",))
        cls.write_input(cls.dir / "notruthdenom075.root", PAPER_PT, skip=("hOFTruthDenom2D",))
        for tag, pt in (("mc07", OUR_PT), ("mc075", PAPER_PT)):
            f = ROOT.TFile.Open(str(cls.dir / f"{tag}.root"), "RECREATE")
            h = ROOT.TH1D("pTmu_reweightedflux_integrated", "", N_PT, np.asarray(pt, dtype=float))
            for i in range(N_PT):
                h.SetBinContent(i + 1, float(cls.flux[i]))
            h.Write()
            f.Close()

    @classmethod
    def tearDownClass(cls):
        plt.close("all")
        cls.tmp.cleanup()

    @classmethod
    def th2(cls, name, pt, vals, errs=None):
        pt, pz = pt if isinstance(pt, tuple) else (pt, PZ)
        h = ROOT.TH2D(name, "", N_PT, np.asarray(pt, dtype=float), N_PZ, np.asarray(pz, dtype=float))
        h.Sumw2()
        for ix in range(N_PT):
            for iy in range(N_PZ):
                h.SetBinContent(ix + 1, iy + 1, float(vals[ix, iy]))
                if errs is not None:
                    h.SetBinError(ix + 1, iy + 1, float(errs[ix, iy]))
        h.SetDirectory(0)
        return h

    POT, NUC = 1.06e21, 3.2e30

    @classmethod
    def write_input(cls, path, pt, other=None, skip=()):
        """The fields main() reads, as unfold_2d_omnifold_unbinned.py writes them; `other` puts the
        named histograms on other edges (pT, or p_par for hXSec_pz), `skip` leaves them out."""
        o = other or {}
        f = ROOT.TFile.Open(str(path), "RECREATE")
        cls.th2("hXSec2D", pt, 1e-39 * cls.cont, 1e-39 * cls.err).Write()
        for name, vals in (("hOFTruthDenom2D", cls.truth), ("hTruth2D", cls.truth), ("hEff2D", cls.eff)):
            if name not in skip:
                cls.th2(name, o.get(name, pt), vals).Write()
        for name, edges, n in (("hXSec_pt", o.get("hXSec_pt", pt), N_PT), ("hXSec_pz", o.get("hXSec_pz", PZ), N_PZ),
                               ("hFlux_pt", o.get("hFlux_pt", pt), N_PT)):
            if name in skip:
                continue
            h = ROOT.TH1D(name, "", n, np.asarray(edges, dtype=float))
            for i in range(n):
                h.SetBinContent(i + 1, float(1e-38 * (1 + i)) if name != "hFlux_pt" else float(cls.flux[i]))
                h.SetBinError(i + 1, float(1e-40 * (1 + i)))
            h.Write()
        ROOT.TParameter("double")("dataPOT", cls.POT).Write()
        ROOT.TParameter("double")("nNucleons", cls.NUC).Write()
        ROOT.TParameter("int")("nIterations", 5).Write()
        f.Close()

    def expected_truth_xsec(self, pt):
        """compute_truth_xsec_2d's definition, written out: u / (flux_i N POT dpT dp_par) in cm^2."""
        return self.truth / (self.flux[:, None] * self.NUC * self.POT * np.outer(np.diff(pt), np.diff(PZ))) * 1e4

    def new(self, tag):
        return new_module("plot_2d_cross_section.py", f"xs_new_{tag}")

    def modules(self, tag):
        old = base_module_at(BASE_XS, "2d-unfolding/plot_2d_cross_section.py", f"xs_old_{tag}", self.dir)
        if old is None:
            self.skipTest(f"git show {BASE_XS[:12]} unavailable")
        return old, new_module("plot_2d_cross_section.py", f"xs_new_{tag}")

    def test_edge_label(self):
        for x, want in ((0.07, "0.07"), (0.075, "0.075"), (1.5, "1.50"), (0.0, "0.00"), (0.325, "0.325"),
                        (0.475, "0.475"), (4.5, "4.50"), (0.33, "0.33")):
            self.assertEqual(rc.edge_label(x), want)
        self.assertEqual(rc.edge_label(1 / 3), "0.333333333")
        f13 = new_module("plot_2d_threeway_fig13.py", "f13_lab")
        self.assertIs(f13.edge_label, rc.edge_label)

    def test_slice_labels(self):
        old, new = self.modules("lab")
        for tag in ("07", "075"):
            h = self.th2(f"hlab{tag}", OUR_PT if tag == "07" else PAPER_PT, self.cont, self.err)
            for axis in ("pt", "pz"):
                so, sn = old.th2_to_slices(h, axis), new.th2_to_slices(h, axis)
                for (lo_, ho), (ln, hn) in zip(so, sn):
                    np.testing.assert_array_equal(th1_dump(ho)[1], th1_dump(hn)[1])
                    np.testing.assert_array_equal(th1_dump(ho)[2], th1_dump(hn)[2])
                if tag == "07" or axis == "pz":
                    self.assertEqual([x[0] for x in so], [x[0] for x in sn])
            if tag == "075":
                got = [x[0] for x in new.th2_to_slices(h, "pt")]
                self.assertEqual(got[0], "0.00 < p_T < 0.075")
                self.assertEqual(got[3], "0.25 < p_T < 0.325")
                self.assertEqual(got[5], "0.40 < p_T < 0.475")
                self.assertEqual(got[6], "0.475 < p_T < 0.55")
                self.assertEqual([x[0] for x in old.th2_to_slices(h, "pt")][0], "0.00 < p_T < 0.07")

    def test_truth_projections(self):
        old, new = self.modules("proj")
        import unfold_2d_omnifold_unbinned as uu
        h07 = self.th2("hp07", OUR_PT, self.cont, self.err)
        for a, b in zip(new.truth_projections(h07), (uu.project_xsec_1d(h07, ax, old.PT_EDGES, old.PZ_EDGES)
                                                      for ax in ("pt", "pz"))):
            for x, y in zip(th1_dump(a), th1_dump(b)):
                np.testing.assert_array_equal(x, y)
        h075 = self.th2("hp075", PAPER_PT, self.cont, self.err)
        hpt, hpz = new.truth_projections(h075)
        e, v, _ = th1_dump(hpt)
        np.testing.assert_array_equal(e, PAPER_PT)
        np.testing.assert_allclose(v, self.cont @ np.diff(PZ), rtol=1e-12)
        e, v, _ = th1_dump(hpz)
        np.testing.assert_array_equal(e, PZ)
        np.testing.assert_allclose(v, np.diff(PAPER_PT) @ self.cont, rtol=1e-12)
        self.assertFalse(np.allclose(v, np.diff(OUR_PT) @ self.cont, rtol=1e-6))

    def test_efficiency_mesh(self):
        new = self.new("eff")
        for pt in (OUR_PT, PAPER_PT):
            pz_e, pt_e, arr = new.efficiency_mesh(self.th2("heff", pt, self.eff))
            np.testing.assert_array_equal(pt_e, pt)
            np.testing.assert_array_equal(pz_e, PZ)
            np.testing.assert_array_equal(arr, self.eff)

    def th2_grid(self, name, pt, pz, vals):
        h = ROOT.TH2D(name, "", N_PT, np.asarray(pt, dtype=float), N_PZ, np.asarray(pz, dtype=float))
        for ix in range(N_PT):
            for iy in range(N_PZ):
                h.SetBinContent(ix + 1, iy + 1, float(vals[ix, iy]))
        h.SetDirectory(0)
        return h

    def test_helpers_follow_the_p_parallel_axis_too(self):
        new = self.new("pz")
        pz = PZ.copy()
        pz[9] = 7.5
        h = self.th2_grid("hbadpz", PAPER_PT, pz, self.cont)
        hpt, hpz = new.truth_projections(h)
        np.testing.assert_allclose(th1_dump(hpt)[1], self.cont @ np.diff(pz), rtol=1e-12)
        np.testing.assert_array_equal(th1_dump(hpz)[0], pz)
        pz_e, pt_e, _ = new.efficiency_mesh(h)
        np.testing.assert_array_equal(pz_e, pz)
        np.testing.assert_array_equal(pt_e, PAPER_PT)
        self.assertEqual(new.th2_to_slices(h, "pz")[9][0], "7.5 < p_|| < 8.0")

    def test_transposed_or_mixed_inputs_are_refused(self):
        new = self.new("refuse")
        t = ROOT.TH2D("htr", "", N_PZ, PZ, N_PT, PAPER_PT)
        t.SetDirectory(0)
        for fn in (new.truth_projections, new.efficiency_mesh):
            with self.assertRaises(ValueError):
                fn(t)
        with self.assertRaises(ValueError):
            new.th2_to_slices(t, "pt")
        for bad in ("eff", "flux", "truth", "truthpz", "xpt", "xpz"):
            with self.assertRaises(RuntimeError, msg=bad):
                self.run_xs(new, self.dir / f"mixed_{bad}.root", str(self.dir / f"m_{bad}"), False)
        pc = new_module("plot_2d_paper_comparison.py", "pc_refuse")
        for bad in ("eff", "flux", "truth", "truthpz"):
            with self.assertRaises(RuntimeError, msg=bad):
                run_main(pc, ["--infile", self.dir / f"mixed_{bad}.root", "--prefix", self.dir / f"pc_{bad}"])

    def test_fallback_flux_must_be_on_the_truth_edges(self):
        new = self.new("fallback")
        pc = new_module("plot_2d_paper_comparison.py", "pc_fallback")
        inp = self.dir / "noflux075.root"
        with self.assertRaises(RuntimeError):
            self.run_xs(new, inp, str(self.dir / "fb07"), False, ["--mcfile", self.dir / "mc07.root"])
        with self.assertRaises(RuntimeError):
            run_main(pc, ["--infile", inp, "--prefix", self.dir / "pcfb07", "--mcfile", self.dir / "mc07.root"])
        out = self.run_xs(new, inp, str(self.dir / "fb075"), False, ["--mcfile", self.dir / "mc075.root"])
        self.assertIn("mc075.root:pTmu_reweightedflux_integrated", out)
        run_main(pc, ["--infile", inp, "--prefix", self.dir / "pcfb075", "--mcfile", self.dir / "mc075.root"])

    def test_truth_fallback_to_hTruth2D(self):
        new = self.new("tfb")
        out = self.run_xs(new, self.dir / "notruthdenom075.root", str(self.dir / "tfb"), False)
        self.assertIn("hOFTruthDenom2D not found", out)

    def run_xs(self, module, infile, prefix, style, extra=()):
        argv = ["--infile", infile, "--prefix", prefix] + (["--style", "restyle-2026-10", "--print-font"] if style else []) + list(extra)
        _, out = run_main(module, argv)
        return out

    def test_main_on_our_grid_equals_base(self):
        old, new = self.modules("main")
        for style in (False, True):
            outs = {}
            for tag, m in (("old", old), ("new", new)):
                prefix = str(self.dir / f"m{int(style)}_{tag}")
                outs[tag] = self.run_xs(m, self.dir / "g07.root", prefix, style).replace(prefix, "P")
            self.assertEqual(outs["old"], outs["new"])
            for stem in ("pt_slices", "pz_slices", "proj_pt", "proj_pz", "eff_heatmap"):
                a = (self.dir / f"m{int(style)}_old_{stem}.png").read_bytes()
                b = (self.dir / f"m{int(style)}_new_{stem}.png").read_bytes()
                self.assertEqual(a, b, f"{stem} style={style}")

    def test_main_on_paper_grid(self):
        new = self.new("main075")
        want = self.expected_truth_xsec(PAPER_PT)
        for style in (False, True):
            proj, grids, meshes = [], [], []

            def rec_proj(h_xsec, h_truth, **k):
                proj.append((th1_dump(h_xsec), th1_dump(h_truth)))
                return orig_proj(h_xsec, h_truth, **k)

            def rec_grid(xs, ts, *a, **k):
                grids.append(([x[0] for x in xs], [t[0] for t in ts], [th1_dump(t[1]) for t in ts]))
                return orig_grid(xs, ts, *a, **k)

            def rec_mesh(ax, *a, **k):
                meshes.append(tuple(np.asarray(x, dtype=float) for x in a[:3]))
                return orig_mesh(ax, *a, **k)

            orig_proj, orig_grid, orig_mesh = new.plot_1d_projection, new.plot_panel_grid, Axes.pcolormesh
            with mock.patch.object(new, "plot_1d_projection", rec_proj), \
                    mock.patch.object(new, "plot_panel_grid", rec_grid), mock.patch.object(Axes, "pcolormesh", rec_mesh):
                self.run_xs(new, self.dir / "g075.root", str(self.dir / f"p075_{int(style)}"), style)
            (xpt, tpt), (xpz, tpz) = proj
            np.testing.assert_array_equal(xpt[0], PAPER_PT)
            np.testing.assert_array_equal(tpt[0], PAPER_PT)
            np.testing.assert_allclose(tpt[1], want @ np.diff(PZ), rtol=1e-12)
            np.testing.assert_array_equal(tpz[0], PZ)
            np.testing.assert_allclose(tpz[1], np.diff(PAPER_PT) @ want, rtol=1e-12)
            (lx, lt, tslices), (pzx, pzt, pzslices) = grids
            np.testing.assert_array_equal(xpz[0], PZ)
            self.assertEqual(pzx, pzt)
            self.assertEqual(pzx[0], "1.5 < p_|| < 2.0")
            for k, d in enumerate(pzslices):
                np.testing.assert_array_equal(d[0], PAPER_PT)
                np.testing.assert_allclose(d[1], want[:, k], rtol=1e-12)
            self.assertEqual(lx, lt)
            self.assertEqual(lx[6], "0.475 < p_T < 0.55")
            self.assertEqual(lx[0], "0.00 < p_T < 0.075")
            for k, d in enumerate(tslices):
                np.testing.assert_allclose(d[1], want[k], rtol=1e-12)
            pz_e, pt_e, arr = meshes[0]
            np.testing.assert_array_equal(pz_e, PZ)
            np.testing.assert_array_equal(pt_e, PAPER_PT)
            np.testing.assert_array_equal(arr, self.eff)

    def test_paper_comparison_main(self):
        old = base_module_at(BASE_XS, "2d-unfolding/plot_2d_paper_comparison.py", "pc_old", self.dir)
        if old is None:
            self.skipTest(f"git show {BASE_XS[:12]} unavailable")
        new = new_module("plot_2d_paper_comparison.py", "pc_new")
        for style in (False, True):
            st = ["--style", "restyle-2026-10", "--print-font"] if style else []
            outs = {}
            for tag, m in (("old", old), ("new", new)):
                prefix = str(self.dir / f"pc{int(style)}_{tag}")
                outs[tag] = run_main(m, ["--infile", self.dir / "g07.root", "--prefix", prefix] + st)[1].replace(prefix, "P")
            self.assertEqual(outs["old"], outs["new"])
            for stem in ("pt_slices", "pz_slices"):
                self.assertEqual((self.dir / f"pc{int(style)}_old_{stem}.png").read_bytes(),
                                 (self.dir / f"pc{int(style)}_new_{stem}.png").read_bytes(), f"{stem} style={style}")

    def test_paper_comparison_on_the_release_grid(self):
        new = new_module("plot_2d_paper_comparison.py", "pc_075")
        for style in (False, True):
            st = ["--style", "restyle-2026-10", "--print-font"] if style else []
            texts, stairs = [], []
            ot, ox, os_ = Axes.set_title, Axes.text, Axes.stairs
            with mock.patch.object(Axes, "set_title", lambda ax, t, *a, **k: (texts.append(t), ot(ax, t, *a, **k))[1]), \
                    mock.patch.object(Axes, "text", lambda ax, x, y, t, *a, **k: (texts.append(t), ox(ax, x, y, t, *a, **k))[1]), \
                    mock.patch.object(Axes, "stairs", lambda ax, v, e=None, *a, **k: (stairs.append(np.asarray(e, dtype=float)), os_(ax, v, e, *a, **k))[1]):
                run_main(new, ["--infile", self.dir / "g075.root", "--prefix", self.dir / f"pc075_{int(style)}"] + st)
            want = "$0.475 < p_T < 0.55$" if style else "0.475 < p_T < 0.55"
            self.assertTrue(any(want in str(t) for t in texts), style)
            self.assertFalse(any("0.47 < p_T" in str(t) for t in texts), style)
            self.assertTrue(any(len(e) == N_PT + 1 and np.array_equal(e, PAPER_PT) for e in stairs), style)

    def test_paper_comparison_slices_use_the_label(self):
        pc = new_module("plot_2d_paper_comparison.py", "pc_lab")
        h = self.th2("hpc", PAPER_PT, self.cont, self.err)
        self.assertEqual(pc.th2_to_slices(h, "pt")[6][0], "0.475 < p_T < 0.55")


if __name__ == "__main__":
    unittest.main()
