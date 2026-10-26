"""Controls for fd_g_compare (FD-G-DECLARATION.md section 5), on a synthetic tree of every input Stage G reads and on
the committed records. No real prediction, covariance or data value is read.

* The tool runs as declared, ``env -u PYTHONPATH <python> -I -B``, from a cwd outside nd-unfolding: the real script to
  its first control, and the module end to end on the synthetic tree.
* The total and shape-only chi2, the pulls and V_g are recomputed here by hand; the chi2 survival function is checked
  against scipy for every ndf it is used at.
* GiBUU: compared on the eight p_parallel < 4.5 cells only, and no GiBUU value on the other eight cells appears in any
  output, by this test's own scan of quantities it builds from the fixture.
* Each of controls G0-G4 refuses on a one-entry defect, with nothing written."""
import copy
import re
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(1, str(ND))
import fd_g_compare as G  # noqa: E402
import s1_assemble as sa  # noqa: E402

REPO = ND.parent
DEFINITION = ND / "pv-ladder/readouts/h2_definition.json"
STATE = REPO / "docs/orchestration/state"
N = G.N_FINE
HIGH = [c for c in range(16) if c not in G.GIBUU_CELLS]

try:
    from scipy.stats import chi2 as _chi2
except ImportError:  # pragma: no cover
    _chi2 = None


def digest(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class Tree:
    """Every Stage G input, built from known cell values: each prediction's fine values are constant within a cell,
    so its cell integral, its V_g and its event count are known exactly."""

    def __init__(self, root: Path, seed=0, scale=1e-39):
        rng = np.random.default_rng(seed)
        self.root = root
        self.fm = sa.fine_map(DEFINITION)
        self.U = sa.functional_matrix(self.fm)
        self.vol = sa.s1.fine_volume()
        self.f = rng.uniform(4, 6, 16) * scale
        ff = np.outer(self.f, self.f)
        A = rng.normal(size=(40, 16))
        Ce_rel = 0.05 ** 2 * (np.cov(A, rowvar=False) / 4 + np.eye(16) * 0.5)
        S = rng.normal(0, 0.02, (3, 16))
        self.Ce, self.Cma = Ce_rel * ff, (S.T @ S) * ff
        self.Ct = self.Ce + self.Cma
        self.preds = {}
        for p in G.PREDICTIONS:
            gc = self.f * (1 + rng.normal(0, 0.08, 16))           # cell integrals
            relvar = rng.uniform(1e-5, 4e-4, 16)                    # V_g / g^2 per cell
            self.preds[p["name"]] = {"g": gc, "relvar": relvar, "meta": {p["meta"][0]: p["meta"][1]}}
        self.out = None

    def fine(self, name):
        """xsec, sumw2, nevt on the fine grid with the cell values above (outside the cells: arbitrary, positive)."""
        d = self.preds[name]
        cell = np.clip(self.fm, 0, None)
        ncell = np.bincount(self.fm[self.fm >= 0], minlength=16)
        volc = self.U.sum(axis=1)
        inside = self.fm >= 0
        x = np.where(inside, (d["g"] / volc)[cell], 3.3e-41)
        # sum_f sumw2_f vol_f^2 = relvar g^2 with sumw2_f = a_c / vol_f^2 spread evenly over the cell's fine cells
        s2 = np.where(inside, (d["relvar"] * d["g"] ** 2 / ncell)[cell] / self.vol ** 2, 1e-90)
        nev = np.where(inside, 7.0, 1.0)
        return x, s2, nev

    def write(self, mutate=None):
        if self.root.exists():
            shutil.rmtree(self.root)
        R, P = self.root, self.root / "s5p"
        R.mkdir(parents=True)
        for p in G.PREDICTIONS:
            path = P / p["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            x, s2, nev = self.fine(p["name"])
            arrs = {"xsec_flat": x, "sumw2_flat": s2, "nevt_flat": nev,
                    **{f"edges_{a}": np.asarray(sa.s1.FINE[a], float) for a in sa.s1.AXES},
                    "meta_json": json.dumps(self.preds[p["name"]]["meta"])}
            if mutate:
                arrs = mutate(p["name"], arrs) or arrs
            np.savez_compressed(path, **arrs)
        self.sums = R / "SHA256SUMS.txt"
        self.sums.write_text("".join(f"{digest(P / p['path'])}  {p['path']}\n" for p in G.PREDICTIONS)
                             + f"{'0' * 64}  runs/other.npz\n")
        s1n = R / "s1_assembly.npz"
        np.savez_compressed(s1n, f=self.f, U=self.U.astype(np.float32), C_e=self.Ce, C_model_abs=self.Cma,
                            C_total=self.Ct, meta=json.dumps({"blocks": []}))
        s1j = R / "s1_assembly.json"
        s1j.write_text(json.dumps({"assembly_sha256": digest(s1n),
                                   "relative_sigma": {"C_total": (np.sqrt(np.diag(self.Ct)) / self.f).tolist()}}))
        cmj = R / "cmodel_5d.json"
        cmj.write_text(json.dumps({"x": self.f.tolist()}))
        self.pins = {"s1_npz": digest(s1n), "s1_json": digest(s1j), "cmodel_json": digest(cmj),
                     "s5p_sums": digest(self.sums)}
        self.predictions = tuple(dict(p, sha256=digest(P / p["path"])) for p in G.PREDICTIONS)
        self.out = R / "out"
        self.out.mkdir()
        self.argv = ["--definition", str(DEFINITION), "--s1-npz", str(s1n), "--s1-json", str(s1j),
                     "--cmodel-json", str(cmj), "--s5p-sums", str(self.sums), "--s5p-root", str(P),
                     "--out-json", str(self.out / "readout.json")]
        return self

    def config(self):
        return {"nd": str(ND), "pins": self.pins, "predictions": self.predictions, "argv": self.argv}


WRAPPER = r"""
import json, sys
cfg = json.load(open(sys.argv[1]))
sys.path.insert(0, cfg["nd"])
import fd_g_compare as m
m.PINS = cfg["pins"]
m.PREDICTIONS = tuple(dict(p, meta=tuple(p["meta"])) for p in cfg["predictions"])
sys.argv = ["fd_g_compare.py"] + cfg["argv"]
raise SystemExit(m.main(cfg["argv"]))
"""


def run_isolated(args):
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    with tempfile.TemporaryDirectory(prefix="fd-g-cwd-") as cwd:
        return subprocess.run([sys.executable, "-I", "-B", *args], cwd=cwd, env=env, capture_output=True, text=True,
                              timeout=600)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fd-g-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def run_module(self, tree):
        cfg, w = self.tmp / "cfg.json", self.tmp / "wrapper.py"
        cfg.write_text(json.dumps(tree.config()))
        w.write_text(WRAPPER)
        return run_isolated([str(w), str(cfg)])

    def assertStops(self, tree, control):
        with self.assertRaises(SystemExit) as cm:
            G.run(G.build_args(tree.argv), tree.pins, tree.predictions)
        self.assertIn(f"FAIL control {control}:", str(cm.exception.code))
        self.assertEqual(list(tree.out.iterdir()), [], "a refused run wrote something")


class Statistics(unittest.TestCase):
    def test_chi2_survival_is_exact_for_every_ndf_used(self):
        if _chi2 is None:
            self.skipTest("scipy not available")
        for ndf in (1, 2, 3, 7, 8, 15, 16):
            for x in (0.0, 0.3, 2.0, 7.0, 14.07, 15.0, 25.0, 30.6, 60.0, 300.0):
                want = float(_chi2.sf(x, ndf))
                self.assertAlmostEqual(G.chi2_sf(x, ndf), want, delta=1e-300 + 1e-10 * want, msg=(ndf, x))
        with self.assertRaises(ValueError):
            G.chi2_sf(1.0, 0)

    def test_compare_by_hand(self):
        rng = np.random.default_rng(3)
        f = rng.uniform(1, 2, 16)
        Ct = np.cov(rng.normal(size=(60, 16)), rowvar=False) * 0.01
        g = f * (1 + rng.normal(0, 0.05, 16))
        Vg = rng.uniform(1e-5, 1e-4, 16)
        for cells in (list(range(16)), list(G.GIBUU_CELLS)):
            r = G.compare(f, g, Vg, Ct, cells, "C")
            i = np.asarray(cells)
            d, M = (f - g)[i], Ct[np.ix_(i, i)] + np.diag(Vg[i])
            self.assertAlmostEqual(r["total"]["chi2"], float(d @ np.linalg.solve(M, d)), places=9)
            Ms = M + 100 * np.outer(f[i], f[i])
            self.assertAlmostEqual(r["shape_only"]["chi2"], float(d @ np.linalg.solve(Ms, d)), places=9)
            self.assertEqual((r["total"]["ndf"], r["shape_only"]["ndf"]), (len(i), len(i) - 1))
            self.assertEqual((r["total"]["matrix_rank"], r["shape_only"]["matrix_rank"]), (len(i), len(i)))
            self.assertEqual(r["total"]["matrix"], "C + V_g")
            np.testing.assert_allclose(r["pulls"], d / np.sqrt(np.diag(M)), rtol=1e-12)
            self.assertLessEqual(r["shape_only"]["chi2"], r["total"]["chi2"])

    def test_rank_counts_eigenvalues_above_the_relative_threshold(self):
        rng = np.random.default_rng(5)
        A = rng.normal(size=(16, 5))
        self.assertEqual(G.rank(A @ A.T), 5)
        self.assertEqual(G.rank(A @ A.T + np.eye(16)), 16)

    def test_shape_only_removes_a_pure_normalization(self):
        rng = np.random.default_rng(4)
        f = rng.uniform(1, 2, 16)
        Ct = np.cov(rng.normal(size=(60, 16)), rowvar=False) * 0.01
        r = G.compare(f, 1.2 * f, np.zeros(16), Ct, list(range(16)), "C")
        a = float(f @ np.linalg.solve(Ct, f))
        self.assertGreater(r["total"]["chi2"], 10)
        self.assertAlmostEqual(r["shape_only"]["chi2"], 0.04 * a / (1 + 100 * a), places=9)   # ~ 0.04/100
        self.assertLess(r["shape_only"]["chi2"], 1e-3)


class EndToEnd(Base):
    def test_run_as_invoked_and_recomputed_by_hand(self):
        tree = Tree(self.tmp / "t").write()
        r = self.run_module(tree)
        self.assertEqual(r.returncode, 0, r.stderr[-3000:])
        self.assertNotIn("ModuleNotFoundError", r.stderr)
        for c in ("G0", "G1", "G2", "G3", "G4"):
            self.assertIn(f"PASS control {c} ", r.stdout)
        out = json.loads((tree.out / "readout.json").read_text())
        self.assertEqual(out["schema"], "fd-g-readout/2")
        self.assertIsNone(out["extra_block"])
        self.assertEqual([p["name"] for p in out["predictions"]], [p["name"] for p in G.PREDICTIONS])
        for p in out["predictions"]:
            d = tree.preds[p["name"]]
            cells = list(G.GIBUU_CELLS) if p["name"] == "gibuu" else list(range(16))
            i = np.asarray(cells)
            g = d["g"][i]
            Vg = d["relvar"][i] * g ** 2
            M = tree.Ct[np.ix_(i, i)] + np.diag(Vg)
            dd = tree.f[i] - g
            self.assertEqual(p["cells"], [f"R{c:02d}" for c in cells])
            np.testing.assert_allclose(p["g"], g, rtol=1e-12)
            np.testing.assert_allclose(np.asarray(p["sigma_Vg_over_f"]) ** 2, Vg / tree.f[i] ** 2, rtol=1e-9)
            self.assertAlmostEqual(p["total"]["chi2"], float(dd @ np.linalg.solve(M, dd)), delta=1e-8 * p["total"]["chi2"])
            Ms = M + 100 * np.outer(tree.f[i], tree.f[i])
            self.assertAlmostEqual(p["shape_only"]["chi2"], float(dd @ np.linalg.solve(Ms, dd)),
                                   delta=1e-8 * p["shape_only"]["chi2"])
            n = len(cells)
            self.assertEqual((p["total"]["ndf"], p["shape_only"]["ndf"]), (n, n - 1))
            self.assertEqual(p["total"]["matrix"], "C_total + V_g")
            self.assertEqual(p["reported_covariance"], "C_total")
            self.assertNotIn("variant", p)                                # no extra block, no variant
            self.assertIn("100 f f^T", p["shape_only"]["matrix"])
            self.assertEqual((p["total"]["matrix_size"], p["total"]["matrix_rank"]), ([n, n], n))
            self.assertEqual((p["shape_only"]["matrix_size"], p["shape_only"]["matrix_rank"]), ([n, n], n))
            np.testing.assert_allclose(p["pulls"], dd / np.sqrt(np.diag(M)), rtol=1e-9)
            np.testing.assert_allclose(p["sigma_total_over_f"], np.sqrt(np.diag(tree.Ct)[i]) / tree.f[i], rtol=1e-12)
            for key in ("total", "shape_only"):
                want = float(_chi2.sf(p[key]["chi2"], p[key]["ndf"])) if _chi2 is not None else None
                self.assertEqual(p[key]["p"], G.chi2_sf(p[key]["chi2"], p[key]["ndf"]))
                if want is not None:
                    self.assertAlmostEqual(p[key]["p"], want, delta=1e-300 + 1e-9 * want)
            self.assertNotIn("cells_abs_pull_gt_2", p)                 # no trigger is declared for Stage G
            self.assertEqual(p["shape_only"]["mode"], G.SHAPE_MODE_NOTE)   # the ruled mode note, beside each shape-only chi2
            self.assertIn("2.4 % (16 cells) and 7 % (8 cells)", p["shape_only"]["mode"])
            if p["name"] in ("nuwro", "gibuu"):
                self.assertIn("C12 target; no correction to CH applied", p["label"])
            if p["name"] == "mnvtune_v1":
                self.assertIn("prior (not an independent prediction)", p["label"])
            self.assertEqual(p["n_mc_events_in_cells"], [7.0 * int(np.sum(tree.fm == c)) for c in cells])
            self.assertIn(f"rank {n}]", r.stdout)
        self.assertEqual(r.stdout.count("(free normalization), 16x16, rank 16; mode along f"), 4)
        self.assertEqual(r.stdout.count("(free normalization), 8x8, rank 8; mode along f"), 1)
        self.assertEqual(sorted(p.name for p in tree.out.iterdir()), ["readout.json"])

    def test_no_gibuu_value_above_p_parallel_4p5_is_shown(self):
        self.gibuu_scan(None)

    def test_no_gibuu_value_above_p_parallel_4p5_is_shown_with_an_adopted_block(self):
        self.gibuu_scan("adopted")

    def gibuu_scan(self, role):
        tree = Tree(self.tmp / "t", seed=2, scale=1.0).write()
        mats = [tree.Ct]
        if role is not None:
            Cx = ExtraBlock.resp(tree)
            _, extra = ExtraBlock.block(tree, Cx, role=role)
            tree.argv[-2:-2] = extra
            mats.append(tree.Ct + Cx)
        r = self.run_module(tree)
        self.assertEqual(r.returncode, 0, r.stderr[-3000:])
        gib = tree.preds["gibuu"]
        f = tree.f
        forbidden = []
        for C in mats:
            for c in HIGH:        # the test's own construction of every GiBUU quantity on the high-p_parallel cells
                g = gib["g"][c]
                Vg = gib["relvar"][c] * g ** 2
                forbidden += [g, f[c] - g, g / f[c] - 1, np.sqrt(Vg) / f[c], (f[c] - g) / np.sqrt(C[c, c] + Vg)]
            g16 = gib["g"]                     # and the 16-cell GiBUU chi2s and p, which must not exist
            M16 = C + np.diag(gib["relvar"] * g16 ** 2)
            d16 = f - g16
            for M in (M16, M16 + 100 * np.outer(f, f)):
                x2 = float(d16 @ np.linalg.solve(M, d16))
                forbidden += [x2, G.chi2_sf(x2, 16), G.chi2_sf(x2, 15)]
        forbidden = np.abs(np.array([v for v in forbidden if v != 0]))
        text = (tree.out / "readout.json").read_text() + r.stdout + r.stderr
        import re
        nums = np.abs(np.array([float(t) for t in re.findall(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?", text)]))
        hits = [v for v in nums if v != 0 and np.any(np.abs(forbidden - v) <= 1e-10 * forbidden)]
        self.assertEqual(hits, [])
        out = json.loads((tree.out / "readout.json").read_text())
        rec = next(p for p in out["predictions"] if p["name"] == "gibuu")
        self.assertEqual(rec["cells"], ["R00", "R01", "R02", "R03", "R08", "R09", "R10", "R11"])
        self.assertEqual((rec["total"]["ndf"], rec["shape_only"]["ndf"]), (8, 7))
        for k in ("pulls", "f", "g", "f_minus_g", "g_over_f_minus_1", "sigma_total_over_f", "sigma_Vg_over_f",
                  "n_mc_events_in_cells"):
            self.assertEqual(len(rec[k]), 8, k)
        def ndfs(o):
            if isinstance(o, dict):
                return ([o["ndf"]] if "ndf" in o else []) + [x for v in o.values() for x in ndfs(v)]
            return [x for v in o for x in ndfs(v)] if isinstance(o, list) else []
        self.assertEqual(sorted(set(ndfs(rec))), [7, 8])                      # no 16-cell GiBUU statistic of any kind
        self.assertEqual("variant" in rec, role is not None)
        # stdout: every number is one the readout carries, as printed, or a fixed constant of the control lines
        allowed = {"4.5", "1e-12", "100"}
        for p in out["predictions"]:
            allowed |= {str(p["n_cells"])}
            for k, s in [(k, p[k]) for k in ("total", "shape_only")] + [
                    (k, p["variant"][k]) for k in ("total", "shape_only") if "variant" in p]:
                allowed |= {f"{s['chi2']:.2f}", str(s["ndf"]), f"{s['p']:.3g}", str(s["matrix_rank"]),
                            *(str(n) for n in s["matrix_size"])}
        allowed |= {str(n) for n in range(0, 17)}
        for line in r.stdout.splitlines():
            if line.startswith("{"):
                continue                                                       # the wrote line: a path and a digest
            for tok in re.findall(r"(?<![A-Za-z_])[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?", line):
                self.assertIn(tok.lstrip("+"), allowed, line)
        # negative control: the scan has power - the same quantities on the eight LOW cells are found
        low = [abs(gib["g"][c] / f[c] - 1) for c in G.GIBUU_CELLS]
        self.assertTrue(all(np.any(np.abs(nums - v) <= 1e-10 * v) for v in low))

    def test_refuses_to_overwrite(self):
        tree = Tree(self.tmp / "t").write()
        (tree.out / "readout.json").write_text("{}")
        with self.assertRaises(SystemExit):
            G.run(G.build_args(tree.argv), tree.pins, tree.predictions)


class ExtraBlock(Base):
    """A declared extra block, pinned by digest, in each of its two roles (amendment 1): adopted, where the reported
    comparison includes it and the one without it is the variant; sensitivity, the other way round."""

    @staticmethod
    def block(tree, C, key="C_resp", name="c_resp", role="adopted"):
        p = tree.root / f"{name}.npz"
        np.savez(p, **{key: C})
        return p, ["--extra-block", str(p), "--extra-block-sha256", digest(p), "--extra-block-key", key,
                   "--extra-block-name", "C_resp", "--extra-block-role", role]

    @staticmethod
    def resp(tree, seed=9):
        v = np.random.default_rng(seed).normal(0, 0.03, (5, 16)) * tree.f
        return v.T @ v

    def by_hand(self, tree, name, C):
        """Both chi2, the pulls and sigma/f of one prediction against C + V_g, recomputed here."""
        d = tree.preds[name]
        i = np.asarray(list(G.GIBUU_CELLS) if name == "gibuu" else list(range(16)))
        g = d["g"][i]
        M = C[np.ix_(i, i)] + np.diag(d["relvar"][i] * g ** 2)
        dd = tree.f[i] - g
        Ms = M + 100 * np.outer(tree.f[i], tree.f[i])
        return (float(dd @ np.linalg.solve(M, dd)), float(dd @ np.linalg.solve(Ms, dd)), dd / np.sqrt(np.diag(M)),
                np.sqrt(np.diag(C)[i]) / tree.f[i], len(i))

    def assertPrinted(self, line, rec):
        """A stdout line carries this record's own values, as formatted."""
        t, s = rec["total"], rec["shape_only"]
        self.assertIn(f"total chi2 {t['chi2']:.2f}/{t['ndf']} p {t['p']:.3g} ", line)
        self.assertIn(f"shape-only chi2 {s['chi2']:.2f}/{s['ndf']} p {s['p']:.3g} ", line)

    def assertComparison(self, rec, want, matrix):
        x2, x2s, z, sig, n = want
        self.assertAlmostEqual(rec["total"]["chi2"], x2, delta=1e-8 * x2)
        self.assertAlmostEqual(rec["shape_only"]["chi2"], x2s, delta=1e-8 * x2s)
        self.assertEqual(rec["total"]["matrix"], f"{matrix} + V_g")
        self.assertTrue(rec["shape_only"]["matrix"].startswith(f"{matrix} + V_g + 100 f f^T"))
        self.assertEqual((rec["total"]["ndf"], rec["shape_only"]["ndf"], rec["total"]["matrix_rank"]), (n, n - 1, n))
        for k in ("total", "shape_only"):
            self.assertEqual(rec[k]["p"], G.chi2_sf(rec[k]["chi2"], rec[k]["ndf"]))
        np.testing.assert_allclose(rec["pulls"], z, rtol=1e-9)
        np.testing.assert_allclose(rec["sigma_total_over_f"], sig, rtol=1e-12)

    def run_role(self, role, sub):
        tree = Tree(self.tmp / sub).write()
        Cx = self.resp(tree)
        _, extra = self.block(tree, Cx, role=role)
        tree.argv[-2:-2] = extra
        r = self.run_module(tree)
        self.assertEqual(r.returncode, 0, r.stderr[-3000:])
        return tree, Cx, r, json.loads((tree.out / "readout.json").read_text())

    def test_adopted_reports_the_block_and_labels_the_other_without_it(self):
        tree, Cx, r, out = self.run_role("adopted", "a")
        self.assertEqual((out["extra_block"]["name"], out["extra_block"]["role"]), ("C_resp", "adopted"))
        self.assertTrue(out["extra_block"]["label"].startswith("adopted into the reported comparison"))
        np.testing.assert_allclose(out["extra_block"]["relative_sigma"], np.sqrt(np.diag(Cx)) / tree.f, rtol=1e-12)
        self.assertEqual(out["labels"]["reported"], "each prediction's top-level comparison is against C_total + C_resp + "
                         "V_g; its variant record is against C_total + V_g, without C_resp: the variant without the "
                         "declared block")
        self.assertTrue(out["labels"]["covariance"].startswith(G.COVARIANCE_LABEL))
        self.assertTrue(out["labels"]["covariance"].endswith(
            "; C_resp is added to C_total in the reported comparison (labels.reported)"))
        for p in out["predictions"]:
            self.assertEqual(p["reported_covariance"], "C_total + C_resp")
            self.assertComparison(p, self.by_hand(tree, p["name"], tree.Ct + Cx), "C_total + C_resp")
            v = p["variant"]
            self.assertEqual(v["covariance"], "C_total")
            self.assertTrue(v["label"].startswith("without C_resp"))
            self.assertComparison(v, self.by_hand(tree, p["name"], tree.Ct), "C_total")
            self.assertLessEqual(p["total"]["chi2"], v["total"]["chi2"] + 1e-9)   # a PSD addition cannot raise chi2
        lines = [ln for ln in r.stdout.splitlines() if ln.startswith("[G]")]
        self.assertEqual(len(lines), 10)
        for p, rep_line, var_line in zip(out["predictions"], lines[::2], lines[1::2]):
            self.assertPrinted(rep_line, p)
            self.assertPrinted(var_line, p["variant"])
            self.assertIn(", reported: total chi2", rep_line)
            self.assertIn("[C_total + C_resp + V_g, ", rep_line)
            self.assertTrue(var_line.startswith("[G]   variant without C_resp: total chi2"), var_line)
            self.assertIn("[C_total + V_g, ", var_line)

    def test_sensitivity_reports_c_total_and_labels_the_block_a_variant(self):
        tree, Cx, r, out = self.run_role("sensitivity", "s")
        self.assertEqual(out["extra_block"]["role"], "sensitivity")
        self.assertTrue(out["extra_block"]["label"].startswith("a declared sensitivity variant"))
        self.assertEqual(out["labels"]["reported"], "each prediction's top-level comparison is against C_total + V_g; "
                         "its variant record is against C_total + C_resp + V_g, with C_resp: a declared sensitivity "
                         "variant")
        self.assertTrue(out["labels"]["covariance"].endswith("; C_resp is added to C_total in the variant (labels.reported)"))
        for p in out["predictions"]:
            self.assertEqual(p["reported_covariance"], "C_total")
            self.assertComparison(p, self.by_hand(tree, p["name"], tree.Ct), "C_total")
            self.assertEqual(p["variant"]["covariance"], "C_total + C_resp")
            self.assertTrue(p["variant"]["label"].startswith("with C_resp: a declared sensitivity variant"))
            self.assertComparison(p["variant"], self.by_hand(tree, p["name"], tree.Ct + Cx), "C_total + C_resp")
        lines = [ln for ln in r.stdout.splitlines() if ln.startswith("[G]")]
        self.assertEqual(len(lines), 10)
        for p, rep_line, var_line in zip(out["predictions"], lines[::2], lines[1::2]):
            self.assertPrinted(rep_line, p)
            self.assertPrinted(var_line, p["variant"])
        self.assertTrue(all("[C_total + V_g, " in ln for ln in lines[::2]))
        self.assertTrue(all(ln.startswith("[G]   variant with C_resp: total chi2") for ln in lines[1::2]))

    def test_the_two_roles_swap_the_same_two_comparisons(self):
        _, _, _, a = self.run_role("adopted", "a")
        _, _, _, s = self.run_role("sensitivity", "s")
        keys = ("total", "shape_only", "pulls", "sigma_total_over_f")
        for pa, ps in zip(a["predictions"], s["predictions"]):
            self.assertEqual({k: pa[k] for k in keys}, {k: ps["variant"][k] for k in keys}, pa["name"])
            self.assertEqual({k: ps[k] for k in keys}, {k: pa["variant"][k] for k in keys}, pa["name"])
            for k in ("f", "g", "f_minus_g", "g_over_f_minus_1", "sigma_Vg_over_f", "n_mc_events_in_cells"):
                self.assertEqual(pa[k], ps[k])

    def test_without_the_option_there_is_no_variant(self):
        tree = Tree(self.tmp / "t").write()
        self.assertEqual(G.run(G.build_args(tree.argv), tree.pins, tree.predictions), 0)
        out = json.loads((tree.out / "readout.json").read_text())
        self.assertIsNone(out["extra_block"])
        self.assertTrue(all("variant" not in p and p["reported_covariance"] == "C_total" for p in out["predictions"]))
        self.assertEqual(out["labels"]["reported"], "each prediction's top-level comparison is against C_total + V_g")
        self.assertEqual(out["labels"]["covariance"], G.COVARIANCE_LABEL)

    def test_refusals(self):
        tree = Tree(self.tmp / "t").write()
        Cx = self.resp(tree)
        _, extra = self.block(tree, Cx)
        bad_sha = list(extra)
        bad_sha[3] = "a" * 64
        cases = {"G0": (bad_sha, "extra block")}
        notpsd = Cx.copy()
        notpsd[0, 0] = -abs(Cx[0, 0])
        anti = np.triu(np.full((16, 16), 1e-3 * Cx.max()), 1)
        asym_psd = Cx + anti - anti.T                          # asymmetric, and PSD once symmetrized: only the
        self.assertGreaterEqual(np.linalg.eigvalsh((asym_psd + asym_psd.T) / 2 / np.outer(tree.f, tree.f)).min(),
                                -1e-12)                        # symmetry check can refuse it
        for k, (what, C, check) in enumerate((("asymmetric", asym_psd, "is symmetric"),
                                              ("not PSD", notpsd, "is positive semidefinite"),
                                              ("shape", Cx[:15, :15], "is a finite 16 x 16 matrix"))):
            for role in G.ROLES:
                _, e = self.block(tree, C, name=f"case{k}-{role}", role=role)
                cases[f"G2 {what} {role}"] = (e, f"C_resp {check}")
        _, e = self.block(tree, Cx, key="other", name="case-key")
        e[e.index("--extra-block-key") + 1] = "C_resp"
        cases["G2 key"] = (e, "no key 'C_resp'")
        for what, (e, check) in cases.items():
            argv = tree.argv[:-2] + e + tree.argv[-2:]
            with self.assertRaises(SystemExit, msg=what) as cm:
                G.run(G.build_args(argv), tree.pins, tree.predictions)
            self.assertIn(f"FAIL control {what.split()[0]}:", str(cm.exception.code), what)
            self.assertIn(check, str(cm.exception.code), what)                 # the check that refused, by name
            self.assertEqual(list(tree.out.iterdir()), [], what)

    def test_the_five_options_go_together_and_the_role_is_one_of_two(self):
        tree = Tree(self.tmp / "t").write()
        _, extra = self.block(tree, self.resp(tree))
        partial = {f"all but {extra[i]}": extra[:i] + extra[i + 2:] for i in range(0, 10, 2)}   # each one left out
        partial.update({"role alone": extra[8:], "block alone": extra[:2], "an unknown role": extra[:9] + ["primary"]})
        self.assertEqual(len(partial), 8)
        for what, e in partial.items():
            with self.assertRaises(SystemExit, msg=what) as cm, mock.patch("sys.stderr"):
                G.build_args(tree.argv + e)
            self.assertEqual(cm.exception.code, 2, what)
        for role in G.ROLES:
            self.assertEqual(G.build_args(tree.argv + extra[:9] + [role]).extra_block_role, role)


class Controls(Base):
    def test_g0_digests(self):
        for key in ("s1_npz", "s1_json", "cmodel_json", "s5p_sums"):
            tree = Tree(self.tmp / f"t-{key}").write()
            tree.pins[key] = "f" * 64
            self.assertStops(tree, "G0")
        tree = Tree(self.tmp / "t-pred").write()
        tree.predictions = tuple(dict(p, sha256="e" * 64) if p["name"] == "nuwro" else p for p in tree.predictions)
        self.assertStops(tree, "G0")
        tree = Tree(self.tmp / "t-sums").write()     # the file matches its pin but the manifest line does not
        tree.sums.write_text(tree.sums.read_text().replace(tree.predictions[1]["sha256"], "d" * 64))
        tree.pins["s5p_sums"] = digest(tree.sums)
        self.assertStops(tree, "G0")
        tree = Tree(self.tmp / "t-def").write()
        d = json.loads(DEFINITION.read_text())
        d["h2_to_reporting_cell"][0], d["h2_to_reporting_cell"][1] = d["h2_to_reporting_cell"][1], d["h2_to_reporting_cell"][0]
        bad = self.tmp / "h2.json"
        bad.write_text(json.dumps(d))
        tree.argv[tree.argv.index("--definition") + 1] = str(bad)
        self.assertStops(tree, "G0")

    def test_g1_structure(self):
        cases = {
            "missing sumw2": lambda n, a: {k: v for k, v in a.items() if k != "sumw2_flat"},
            "short xsec": lambda n, a: dict(a, xsec_flat=a["xsec_flat"][:-1]),
            "edges": lambda n, a: dict(a, edges_pz=np.asarray(a["edges_pz"]) * 1.01),
            "negative sumw2": lambda n, a: dict(a, sumw2_flat=np.where(np.arange(N) == 5, -1.0, a["sumw2_flat"])),
            "nan": lambda n, a: dict(a, xsec_flat=np.where(np.arange(N) == 9, np.nan, a["xsec_flat"])),
            "meta": lambda n, a: dict(a, meta_json=json.dumps({"generator": "nuwro_cv"})),
        }
        for what, fn in cases.items():
            tree = Tree(self.tmp / f"t-{what.replace(' ', '_')}")
            tree.write(mutate=lambda n, a, fn=fn: fn(n, a) if n == "genie_mec" else None)
            self.assertStops(tree, "G1")

    def test_g2_s1(self):
        for what in ("f", "C_total", "sigma"):
            tree = Tree(self.tmp / f"t-{what}").write()
            s1n = Path(tree.argv[tree.argv.index("--s1-npz") + 1])
            s1j = Path(tree.argv[tree.argv.index("--s1-json") + 1])
            cmj = Path(tree.argv[tree.argv.index("--cmodel-json") + 1])
            if what == "f":
                cmj.write_text(json.dumps({"x": (tree.f * (1 + 1e-9)).tolist()}))
            if what == "C_total":
                with np.load(s1n) as z:
                    d = {k: z[k] for k in z.files}
                d["C_total"] = d["C_total"] * (1 + 1e-9)
                np.savez_compressed(s1n, **d)
            j = json.loads(s1j.read_text())
            j["assembly_sha256"] = digest(s1n)
            if what == "sigma":
                j["relative_sigma"]["C_total"][4] *= 1 + 1e-9
            s1j.write_text(json.dumps(j))
            tree.pins.update(s1_npz=digest(s1n), s1_json=digest(s1j), cmodel_json=digest(cmj))
            self.assertStops(tree, "G2")

    def test_g0_s1_readout_names_the_npz(self):
        tree = Tree(self.tmp / "t").write()
        s1j = Path(tree.argv[tree.argv.index("--s1-json") + 1])
        j = json.loads(s1j.read_text())
        j["assembly_sha256"] = "c" * 64
        s1j.write_text(json.dumps(j))
        tree.pins["s1_json"] = digest(s1j)
        self.assertStops(tree, "G0")

    def test_g2_one_entry_defects(self):
        for what in ("C_e entry", "U entry", "not PD"):
            tree = Tree(self.tmp / f"t-{what.replace(' ', '_')}").write()
            s1n = Path(tree.argv[tree.argv.index("--s1-npz") + 1])
            s1j = Path(tree.argv[tree.argv.index("--s1-json") + 1])
            with np.load(s1n) as z:
                d = {k: z[k].copy() for k in z.files}
            if what == "C_e entry":
                d["C_e"][2, 3] *= 1.01
                d["C_e"][3, 2] *= 1.01
            if what == "U entry":
                j0 = np.flatnonzero(d["U"][5])[0]
                d["U"][5, j0] *= 2
            if what == "not PD":
                Ct = d["C_total"]
                Ct[0, 1] = Ct[1, 0] = 2 * np.sqrt(Ct[0, 0] * Ct[1, 1])     # |corr| = 2: diagonal and sigma unchanged
                d["C_model_abs"] = Ct - d["C_e"]
            np.savez_compressed(s1n, **d)
            j = json.loads(s1j.read_text())
            j["assembly_sha256"] = digest(s1n)
            s1j.write_text(json.dumps(j))
            tree.pins.update(s1_npz=digest(s1n), s1_json=digest(s1j))
            self.assertStops(tree, "G2")

    def test_g3_gibuu_cells(self):
        tree = Tree(self.tmp / "t").write()
        with mock.patch.object(G, "GIBUU_CELLS", (0, 1, 2, 3, 8, 9, 10, 12)):
            self.assertStops(tree, "G3")

    def test_g4_positive_integrals(self):
        tree = Tree(self.tmp / "t")
        tree.preds["mnvtune_v1"]["g"][6] = -abs(tree.preds["mnvtune_v1"]["g"][6])
        tree.write()
        self.assertStops(tree, "G4")

    def test_g4_a_high_gibuu_cell_is_never_integrated(self):
        tree = Tree(self.tmp / "t")
        tree.preds["gibuu"]["g"][13] = -1.0     # a non-positive GiBUU value above p_parallel 4.5 must not matter
        tree.write()
        seen = []
        real = G.compare

        def spy(f, g, Vg, Ct, cells, name):
            seen.append((list(cells), np.array(g), np.array(Vg)))
            return real(f, g, Vg, Ct, cells, name)
        with mock.patch.object(G, "compare", spy):
            self.assertEqual(G.run(G.build_args(tree.argv), tree.pins, tree.predictions), 0)
        gib = [s for s in seen if s[0] == list(G.GIBUU_CELLS)]
        self.assertEqual(len(gib), 1)
        self.assertTrue(np.all(gib[0][1][HIGH] == 0) and np.all(gib[0][2][HIGH] == 0))   # never formed above 4.5
        self.assertTrue(all(s[0] == list(range(16)) for s in seen if s is not gib[0]))


class Invocation(Base):
    def test_help_and_argparse_under_isolation(self):
        r = run_isolated([str(ND / "fd_g_compare.py"), "--help"])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("usage:", r.stdout)
        r = run_isolated([str(ND / "fd_g_compare.py")])
        self.assertNotIn("ModuleNotFoundError", r.stderr)
        self.assertEqual(r.returncode, 2, r.stderr)

    def test_the_real_script_reaches_g0_and_refuses_synthetic_records(self):
        tree = Tree(self.tmp / "t").write()
        r = run_isolated([str(ND / "fd_g_compare.py"), *tree.argv])
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("FAIL control G0:", r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertEqual(list(tree.out.iterdir()), [])


class CommittedPins(unittest.TestCase):
    def test_prediction_digests_are_the_archive_manifest_and_the_pv2d_config(self):
        sums = sa.load_manifest(STATE / "s5p/archive/SHA256SUMS-s5p-archive-20261006.txt")
        for p in G.PREDICTIONS:
            self.assertEqual(sums.get(p["path"]), p["sha256"], p["name"])
        cfg = json.loads((REPO / "2d-unfolding/pv2d/config.json").read_text())
        self.assertEqual(cfg["reference"]["sha256"], G.PREDICTIONS[0]["sha256"])
        for name, v in (("genie_mec", "genie_mec"), ("nuwro", "nuwro"), ("gibuu", "gibuu")):
            self.assertEqual(cfg["vertices"][v]["sha256"], next(p for p in G.PREDICTIONS if p["name"] == name)["sha256"])
        self.assertEqual(cfg["cross_check"]["sha256"], G.PREDICTIONS[4]["sha256"])

    def test_record_pins(self):
        fd = STATE / "measurement-paper/5d-community-20261024"
        self.assertEqual(digest(fd / "s1/readout/s1_assembly.json"), G.PINS["s1_json"])
        self.assertEqual(json.loads((fd / "s1/readout/s1_assembly.json").read_text())["assembly_sha256"], G.PINS["s1_npz"])
        self.assertEqual(digest(ND / "pv-ladder/readouts/cmodel_5d.json"), G.PINS["cmodel_json"])
        self.assertEqual(digest(STATE / "s5p/archive/SHA256SUMS-s5p-archive-20261006.txt"), G.PINS["s5p_sums"])

    def test_gibuu_cells_and_counts(self):
        d = json.loads(DEFINITION.read_text())
        self.assertEqual(sorted(c["id"] for c in d["reporting_cells"] if c["box"]["pz"][1] <= 4.5), list(G.GIBUU_CELLS))
        self.assertEqual([p["cells"] for p in G.PREDICTIONS], ["all", "all", "all", "gibuu", "all"])


if __name__ == "__main__":
    unittest.main()
