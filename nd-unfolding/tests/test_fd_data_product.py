"""Controls for fd_data_product (FD-DATA-PRODUCT-DECLARATION.md sections 3 and 5.2), on synthetic S1 and C_resp
products and synthetic readouts with the committed ones' key layout. No real covariance is read; the committed readouts are read
only for their digests and chain (CommittedPins), and the H2 definition is the committed one.

* End to end: every matrix, correlation, f and relative sigma in the JSON and in each CSV is parsed and asserted
  against the synthetic products, recomputed here; the labels are the declared ones; the CSVs' digests are the files'.
* Planted defects: one per check of Q0-Q6, each refusing with its own clause and nothing written.
* Invocation: as written (-I -B, cwd outside nd-unfolding), the real pins refuse the synthetic products at Q0."""
import csv
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
import fd_data_product as F  # noqa: E402
from test_fd_g_compare import DEFINITION, digest, run_isolated  # noqa: E402

REPO = ND.parent
FD = REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024"
CRESP = REPO / "docs/orchestration/state/measurement-scoping/assigned-uncertainties/cresp"
CELLS = [f"R{c:02d}" for c in range(16)]
DEF_PIN = "b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89"
STAGE1 = REPO / "docs/orchestration/state/s5p/stage1/stage1_inspect.json"
NAMES = ("C_e", "C_model_abs", "C_resp", "C_total_plus_C_resp")


def ext(C):
    if not np.all(np.isfinite(C)):
        return {"min": None, "max": None}
    e = np.linalg.eigvalsh(C)
    return {"min": float(e.min()), "max": float(e.max())}


def psd(seed, rank=16, scale=1.0):
    A = np.random.default_rng(seed).normal(size=(rank, 16))
    return A.T @ A * scale


class DPTree:
    """Synthetic S1 and C_resp products and the three readouts, consistent with one another as the real ones are."""

    def __init__(self, root: Path, seed: int = 0):
        self.root = root
        rng = np.random.default_rng(seed)
        self.f = rng.uniform(1, 5, 16) * 1e-39
        F2 = np.outer(self.f, self.f)
        self.Ce = (psd(seed + 1) * 2e-4 + np.eye(16) * 1e-3) * F2
        self.Cm = psd(seed + 2, rank=3) * 1e-4 * F2
        self.Cx = psd(seed + 3, rank=4) * 5e-5 * F2
        self.write()

    def sig(self, C):
        return (np.sqrt(np.diag(C)) / self.f).tolist()

    def write(self, Ct=None, Ctr=None, edit=None, cresp=None, f_npz=None):
        """The products and readouts; Ct, Ctr override the stored C_total and C_total_resp; edit(name, obj) changes a
        readout before it is written, and the readouts after it are re-pinned to it."""
        Ct = self.Ce + self.Cm if Ct is None else Ct
        Ctr = Ct + self.Cx if Ctr is None else Ctr
        edit = edit or (lambda name, obj: None)
        np.savez(self.root / "s1.npz", f=self.f if f_npz is None else f_npz, C_e=self.Ce, C_model_abs=self.Cm, C_total=Ct)
        np.savez(self.root / "cresp.npz", **(cresp or {"C_resp": self.Cx, "C_total_resp": Ctr}))
        self.pins = {"definition": DEF_PIN, "stage1": digest(STAGE1), "s1_npz": digest(self.root / "s1.npz"),
                     "cresp_npz": digest(self.root / "cresp.npz")}
        objs = {
            "s1_json": {"schema": "s1-readout/1", "assembly_sha256": self.pins["s1_npz"], "cells": CELLS,
                        "meta": {"schema": "s1-assembly/1"},
                        "relative_sigma": {"C_e": self.sig(self.Ce), "C_model": self.sig(self.Cm),
                                           "C_total": self.sig(Ct)},
                        "eigen": {"C_e": ext(self.Ce), "C_total": ext(Ct)}},
            "cresp_json": {"schema": "cresp-readout/1", "assembly_sha256": self.pins["cresp_npz"], "cells": CELLS,
                           "meta": {"inputs_sha256": {"s1_assembly": self.pins["s1_npz"], "definition": DEF_PIN}},
                           "relative_sigma": {"C_resp": self.sig(self.Cx), "C_total_resp": self.sig(Ct + self.Cx),
                                              "C_total": self.sig(Ct)},
                           "eigen": {"C_resp": ext(self.Cx), "C_total": ext(Ct), "C_total_resp": ext(Ct + self.Cx)}},
            "g_readout": {"schema": "fd-g-readout/2", "cells": CELLS,
                          "inputs_sha256": {"s1_npz": self.pins["s1_npz"], "definition": DEF_PIN},
                          "extra_block": {"sha256": self.pins["cresp_npz"], "role": "adopted"},
                          "predictions": [{"name": "genie_cv", "cells": CELLS, "f": self.f.tolist(),
                                           "sigma_total_over_f": self.sig(Ct + self.Cx)}]},
        }
        for name, obj in objs.items():
            edit(name, obj)
            (self.root / f"{name}.json").write_text(json.dumps(obj))
            self.pins[name] = digest(self.root / f"{name}.json")
        rows = ["| cell | proton | C_resp | cross-talk | C_total | C_total_resp | ratio |",
                "|---|---:|---:|---:|---:|---:|---:|"]
        for i, c in enumerate(CELLS):
            v = {k: 100 * np.sqrt(C[i, i]) / self.f[i] for k, C in (("C_resp", self.Cx), ("C_total", Ct),
                                                                    ("C_total_resp", Ct + self.Cx))}
            rows.append(f"| {c} | 0.00 | {v['C_resp']:.2f} | 0.00 | {v['C_total']:.2f} | {v['C_total_resp']:.2f} | 1.000 |")
        text = ["# a synthetic CRESP-REPORT", "", *rows]
        edit("cresp_report", text)
        (self.root / "cresp_report.md").write_text("\n".join(text) + "\n")
        self.pins["cresp_report"] = digest(self.root / "cresp_report.md")

    def argv(self, out: Path) -> list:
        paths = {"s1_npz": self.root / "s1.npz", "cresp_npz": self.root / "cresp.npz", "definition": DEFINITION,
                 "stage1": getattr(self, "stage1", STAGE1), "cresp_report": self.root / "cresp_report.md",
                 **{k: self.root / f"{k}.json" for k in ("s1_json", "cresp_json", "g_readout")}}
        a = []
        for k in F.INPUTS:
            a += ["--" + k.replace("_", "-"), str(paths[k])]
        return a + ["--out-dir", str(out)]


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fd-dp-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        (self.tmp / "in").mkdir()
        self.tree = DPTree(self.tmp / "in")
        self.out = self.tmp / "out"

    def run_tool(self, pins=None):
        return F.run(F.build_args(self.tree.argv(self.out)), pins=self.tree.pins if pins is None else pins)

    def refuses(self, control, clause, pins=None):
        shutil.rmtree(self.out, ignore_errors=True)
        with self.assertRaises(SystemExit) as cm:
            self.run_tool(pins)
        msg = str(cm.exception)
        self.assertIn(f"FAIL control {control}", msg)
        self.assertIn(clause, msg)
        self.assertFalse(self.out.exists() and any(self.out.iterdir()), "something was written")


def read_csv(p: Path) -> list:
    with open(p, newline="") as fh:
        return list(csv.reader(fh))


class EndToEnd(Base):
    def test_every_number_against_the_products(self):
        self.assertEqual(self.run_tool(), 0)
        t = self.tree
        Ct = t.Ce + t.Cm
        M = Ct + t.Cx
        want = {"C_e": t.Ce, "C_model_abs": t.Cm, "C_resp": t.Cx, "C_total_plus_C_resp": M}
        np.testing.assert_allclose(M, t.Ce + t.Cm + t.Cx, rtol=0, atol=1e-12 * np.abs(np.diag(M)).max())
        d = np.sqrt(np.diag(M))
        rho = M / np.outer(d, d)
        js = json.loads((self.out / "fd_data_product.json").read_text())
        for name, C in want.items():
            rows = read_csv(self.out / f"fd_data_product_{name}.csv")
            self.assertEqual(rows[0], ["cell", *CELLS])
            self.assertEqual([r[0] for r in rows[1:]], CELLS)
            np.testing.assert_array_equal(np.array([[float(x) for x in r[1:]] for r in rows[1:]]), C)
            np.testing.assert_array_equal(np.array(js["matrices"][name]), C)
            np.testing.assert_array_equal(js["relative_sigma"][name], np.sqrt(np.diag(C)) / t.f)
        rows = read_csv(self.out / "fd_data_product_corr_C_total_plus_C_resp.csv")
        np.testing.assert_array_equal(np.array([[float(x) for x in r[1:]] for r in rows[1:]]), rho)
        np.testing.assert_array_equal(np.array(js["correlation"]), rho)
        self.assertEqual(js["correlation_of"], "C_total_plus_C_resp")
        np.testing.assert_array_equal(js["f"], t.f)
        cells = read_csv(self.out / "fd_data_product_cells.csv")
        self.assertEqual(cells[0], ["cell", "pt_lo", "pt_hi", "pz_lo", "pz_hi", "eavail_lo", "eavail_hi", "q3_lo",
                                    "q3_hi", "W_lo", "W_hi", "f", "rel_sigma_C_e", "rel_sigma_C_model_abs",
                                    "rel_sigma_C_resp", "rel_sigma_C_total_plus_C_resp"])
        defn = json.loads(DEFINITION.read_text())
        for i, (row, c) in enumerate(zip(cells[1:], defn["reporting_cells"])):
            self.assertEqual(row[0], f"R{c['id']:02d}")
            self.assertEqual([float(x) for x in row[1:11]], [v for ax in ("pt", "pz", "eavail", "q3", "W")
                                                              for v in c["box"][ax]])
            self.assertEqual(float(row[11]), t.f[i])
            for j, name in enumerate(NAMES):
                self.assertEqual(float(row[12 + j]), np.sqrt(want[name][i, i]) / t.f[i])
            self.assertEqual(js["cells"][i]["box"], c["box"])
        for n, h in js["files_sha256"].items():
            self.assertEqual(digest(self.out / n), h)
        self.assertEqual(sorted(p.name for p in self.out.iterdir()), sorted([*js["files_sha256"], "fd_data_product.json"]))
        self.assertEqual(js["inputs_sha256"], {k: t.pins[k] for k in F.INPUTS})
        self.assertEqual(js["code_sha256"]["fd_data_product.py"], digest(ND / "fd_data_product.py"))
        self.assertEqual(js["labels"]["what"], "data product: the 5D result's reported covariance")
        self.assertEqual(js["labels"]["not_citable_for"], "coverage")
        self.assertIn("FD-F0b-REPORT.md", js["labels"]["limitation"])
        self.assertTrue((FD / "FD-F0b-REPORT.md").exists())
        self.assertEqual(js["controls_passed"], ["Q0", "Q1", "Q2", "Q3", "Q4", "Q5", "Q6"])
        # the note's 27 supported H2 cells and the 16 reporting cells (the director's question of 2026-10-27)
        st1 = json.loads(STAGE1.read_text())["mc"]["H2"]
        self.assertEqual((st1["n_cells"], st1["n_reported"]), (32, 27))
        self.assertEqual([i for i, x in enumerate(st1["reported"]) if not x], [2, 6, 10, 14, 17])
        self.assertEqual(js["h2"]["unsupported_stage1"], [2, 6, 10, 14, 17])
        self.assertEqual(js["h2"]["unreported_boxes"], [[2], [6], [10], [14]])
        self.assertEqual(js["h2"]["absorbed"], {"17": "R09"})
        self.assertEqual(js["h2"]["in_cells"], [b for b in range(32) if b not in (2, 6, 10, 14)])
        self.assertEqual(js["h2"]["h2_to_reporting_cell"], defn["h2_to_reporting_cell"])
        self.assertEqual(js["labels"]["cells"], (
            "R00-R15 are the definition's 16 reporting cells: the 32 H2 boxes (s5p_stage1_inspect.H2_EDGES) after its "
            "purity merges (steps, tau 0.1). Stage 1 (state/s5p/stage1/stage1_inspect.json mc.H2) supports 27 of the "
            "32 boxes before merging (the note's 27 supported H2 cells); its unsupported boxes are 2, 6, 10, 14, 17. "
            "28 boxes enter the 16 cells; the definition's unreported boxes are 2, 6, 10, 14; box 17, unsupported "
            "alone, enters R09 (17, 19, 21, 23) by the merges"))
        self.assertFalse(list(self.out.glob("*.partial")))

    def test_no_overwrite(self):
        for name in ("fd_data_product.json", "fd_data_product_C_resp.csv", "fd_data_product_cells.csv"):
            with self.subTest(name=name):
                shutil.rmtree(self.out, ignore_errors=True)
                self.out.mkdir()
                (self.out / name).write_text("x")
                with self.assertRaises(SystemExit) as cm:
                    self.run_tool()
                self.assertIn("FAIL control Q0: no output exists", str(cm.exception))
                self.assertEqual([p.name for p in self.out.iterdir()], [name])


class Controls(Base):
    def edited(self, target, fn):
        self.tree.write(edit=lambda name, obj: fn(obj) if name == target else None)

    def test_q0(self):
        for k in F.INPUTS:
            with self.subTest(pin=k):
                self.refuses("Q0", f"{k} sha256 is the pin", pins={**self.tree.pins, k: "0" * 64})
        cases = [("s1_json", lambda o: o.update(schema="s1-assembly/1"), "s1_json schema"),
                 ("s1_json", lambda o: o["meta"].update(schema="s1-assembly/2"), "of schema s1-assembly/1"),
                 ("cresp_json", lambda o: o.update(schema="cresp-readout/2"), "cresp_json schema"),
                 ("g_readout", lambda o: o.update(schema="fd-g-readout/1"), "g_readout schema"),
                 ("s1_json", lambda o: o.update(assembly_sha256="0" * 64), "S1's readout names this S1 assembly"),
                 ("cresp_json", lambda o: o.update(assembly_sha256="0" * 64), "C_resp's readout names this C_resp"),
                 ("cresp_json", lambda o: o["meta"]["inputs_sha256"].update(s1_assembly="0" * 64),
                  "C_resp's readout names this C_resp, built on this S1"),
                 ("cresp_json", lambda o: o["meta"]["inputs_sha256"].update(definition="0" * 64), "and definition"),
                 ("g_readout", lambda o: o["inputs_sha256"].update(s1_npz="0" * 64), "Stage G ran on this S1"),
                 ("g_readout", lambda o: o["inputs_sha256"].update(definition="0" * 64), "Stage G ran on this S1"),
                 ("g_readout", lambda o: o["extra_block"].update(sha256="0" * 64), "Stage G ran on this S1"),
                 ("g_readout", lambda o: o["extra_block"].update(role="sensitivity"), "C_resp, adopted")]
        for target, fn, clause in cases:
            with self.subTest(clause=clause):
                self.tree = DPTree(self.tmp / "in")
                self.edited(target, fn)
                self.refuses("Q0", clause)

    def test_q1(self):
        self.tree.write(f_npz=self.tree.f[:15])
        self.refuses("Q1", "f is 16 cells")
        self.tree = DPTree(self.tmp / "in")
        t = self.tree
        t.f = t.f.copy()
        t.f[3] = -t.f[3]
        t.write()
        self.refuses("Q1", "f is positive")
        self.tree = DPTree(self.tmp / "in")
        t = self.tree
        t.write(cresp={"C_resp": t.Cx[:15, :15], "C_total_resp": t.Ce + t.Cm + t.Cx})
        self.refuses("Q1", "every matrix 16 x 16")
        self.tree = DPTree(self.tmp / "in")
        self.tree.Cm = self.tree.Cm.copy()
        self.tree.Cm[2, 2] = np.nan
        self.tree.write()
        self.refuses("Q1", "finite")
        self.tree = DPTree(self.tmp / "in")
        self.edited("cresp_json", lambda o: o.update(cells=CELLS[::-1]))
        self.refuses("Q1", "the definition reports R00-R15")
        for box in (17, 3):                  # 17: an unsupported box absorbed by R09; 3: a supported one
            with self.subTest(box=box):
                self.tree = DPTree(self.tmp / "in")
                st1 = json.loads(STAGE1.read_text())
                st1["mc"]["H2"]["reported"][box] = not st1["mc"]["H2"]["reported"][box]
                self.tree.stage1 = self.tmp / "stage1.json"
                self.tree.stage1.write_text(json.dumps(st1))
                self.tree.pins["stage1"] = digest(self.tree.stage1)
                # the definition names the committed receipt, so Q0 refuses the edited one first ...
                self.refuses("Q0", "the definition was checked against this Stage-1 receipt")
                with mock.patch.dict(F.PINS, {}):    # ... and with that clause passed, Q1 refuses it
                    orig = F.report
                    with mock.patch.object(F, "report", lambda c, n, ok, why="differs": orig(
                            c, n, True if n.startswith("the definition was checked") else ok, why)):
                        self.refuses("Q1", "the H2 boxes")

    def test_q2_the_sum_of_its_parts(self):
        t = self.tree
        Ct = t.Ce + t.Cm
        bad = Ct.copy()
        bad[4, 4] *= 1 + 1e-9
        t.write(Ct=bad, Ctr=bad + t.Cx)
        # keep every relative sigma the readouts hold equal to the planted C_total's, so Q2 alone fires
        self.refuses("Q2", "C_total + C_resp is the sum of its parts")
        self.tree = DPTree(self.tmp / "in")
        t = self.tree
        Ctr = t.Ce + t.Cm + t.Cx
        Ctr[0, 1] = Ctr[1, 0] = Ctr[0, 1] * (1 + 1e-6)
        t.write(Ctr=Ctr)
        self.refuses("Q2", "is cresp.npz's C_total_resp")

    def test_q3_each_committed_sigma(self):
        def off(key, sub):
            def fn(o):
                v = o["relative_sigma"][sub] if key != "g_readout" else o["predictions"][0][sub]
                v[5] *= 1 + 1e-9
            return key, fn
        cases = [(off("s1_json", "C_e"), "C_e's relative sigma is s1_json's C_e"),
                 (off("s1_json", "C_model"), "C_model_abs's relative sigma is s1_json's C_model"),
                 (off("cresp_json", "C_resp"), "C_resp's relative sigma is cresp_json's C_resp"),
                 (off("cresp_json", "C_total_resp"), "C_total_plus_C_resp's relative sigma is cresp_json's"),
                 (off("g_readout", "sigma_total_over_f"), "C_total_plus_C_resp's relative sigma is g_readout's"),
                 (off("s1_json", "C_total"), "C_total's relative sigma is S1's and C_resp's"),
                 (off("cresp_json", "C_total"), "C_total's relative sigma is S1's and C_resp's"),
                 (off("g_readout", "f"), "f is Stage G's"),
                 (("s1_json", lambda o: o["eigen"]["C_e"].update(max=o["eigen"]["C_e"]["max"] * (1 + 1e-7))),
                  "the spectra's extremes"),
                 (("cresp_json", lambda o: o["eigen"]["C_total_resp"].update(min=o["eigen"]["C_total_resp"]["min"] * 1.01)),
                  "the spectra's extremes"),
                 (("cresp_report", lambda rows: rows.pop(7)), "CRESP-REPORT.md's table")]
        for (key, fn), clause in cases:
            with self.subTest(clause=clause, key=key):
                self.tree = DPTree(self.tmp / "in")
                self.edited(key, fn)
                self.refuses("Q3", clause)
        self.tree = DPTree(self.tmp / "in")      # one value of the table off by 0.02 (its last digit is 0.01)

        def bump(rows):
            i = next(j for j, r in enumerate(rows) if r.startswith("| R04 |"))
            cols = rows[i].split("|")
            cols[3] = f" {float(cols[3]) + 0.02:.2f} "
            rows[i] = "|".join(cols)
        self.edited("cresp_report", bump)
        self.refuses("Q3", "CRESP-REPORT.md's table, to its 2 dp")

    def test_q4(self):
        t = self.tree
        t.Ce = t.Ce.copy()
        t.Ce[0, 1] += 1e-6 * t.Ce[0, 0]
        t.write()
        self.refuses("Q4", "C_e is symmetric")
        self.tree = DPTree(self.tmp / "in")
        t = self.tree
        M = t.Ce + t.Cm + t.Cx
        t.Cx = t.Cx.copy()
        t.Cx[0, 1] = t.Cx[1, 0] = 3 * np.sqrt(M[0, 0] * M[1, 1])
        t.write()
        self.refuses("Q4", "C_total + C_resp is positive definite")
        for name in ("Cm", "Cx"):
            with self.subTest(asymmetric=name):
                self.tree = DPTree(self.tmp / "in")
                A = getattr(self.tree, name).copy()
                A[0, 1] += 1e-6 * A[0, 0]
                setattr(self.tree, name, A)
                self.tree.write()
                self.refuses("Q4", {"Cm": "C_model_abs", "Cx": "C_resp"}[name] + " is symmetric")
        for name in ("Cm", "Cx"):
            with self.subTest(name=name):
                self.tree = DPTree(self.tmp / "in")
                t = self.tree
                A = getattr(t, name).copy()
                A[2, 3] = A[3, 2] = 3 * np.sqrt(A[2, 2] * A[3, 3])
                setattr(t, name, A)
                t.write()
                self.refuses("Q4", {"Cm": "C_model_abs", "Cx": "C_resp"}[name] + " is positive semidefinite")

    def test_q5_and_q6(self):
        t = self.tree
        Ct = t.Ce + t.Cm
        with mock.patch.object(F, "correlation", lambda M: M / np.outer(np.sqrt(np.diag(Ct)), np.sqrt(np.diag(Ct)))):
            self.refuses("Q5", "the correlation is C_total + C_resp's")       # of the wrong matrix
        with mock.patch.object(F, "correlation", lambda M: M / M[0, 0]):
            self.refuses("Q5", "the correlation is C_total + C_resp's")
        orig = F.matrix_csv
        with mock.patch.object(F, "matrix_csv", lambda C: orig(np.round(C / C.max(), 6) * C.max())):
            self.refuses("Q6", "the CSV and the JSON read back bit for bit")
        orig_c = F.cells_csv

        def rounded(p):
            q = dict(p)
            q["f"] = np.float32(p["f"]).astype(float)
            return orig_c(q)
        with mock.patch.object(F, "cells_csv", rounded):
            self.refuses("Q6", "the cells CSV reads back f")


class Invocation(Base):
    def test_real_pins_refuse_synthetic_products(self):
        res = run_isolated([str(ND / "fd_data_product.py"), *self.tree.argv(self.out)])
        self.assertEqual(res.returncode, 1)
        self.assertIn("FAIL control Q0 s1_npz sha256 is the pin", res.stdout + res.stderr)
        self.assertNotIn("Traceback", res.stderr)
        self.assertFalse(self.out.exists())

    def test_argparse(self):
        argv = self.tree.argv(self.out)
        i = argv.index("--cresp-npz")
        res = run_isolated([str(ND / "fd_data_product.py"), *(argv[:i] + argv[i + 2:])])
        self.assertEqual(res.returncode, 2)


class CommittedPins(unittest.TestCase):
    """The committed readouts' digests and their chain to the two pinned products. No product is opened."""

    def test_pins_and_chain(self):
        paths = {"s1_json": FD / "s1/readout/s1_assembly.json", "cresp_json": CRESP / "cresp.json",
                 "g_readout": FD / "fd/readout/fd_g_readout.json", "definition": DEFINITION, "stage1": STAGE1,
                 "cresp_report": CRESP / "CRESP-REPORT.md"}
        for k, p in paths.items():
            self.assertEqual(digest(p), F.PINS[k], k)
        s1, cr, g = (json.loads(paths[k].read_text()) for k in ("s1_json", "cresp_json", "g_readout"))
        for k, want in F.SCHEMAS.items():
            self.assertEqual(json.loads(paths[k].read_text())["schema"], want, k)
        self.assertEqual(s1["meta"]["schema"], "s1-assembly/1")
        for k in ("C_e", "C_total"):
            self.assertEqual(sorted(s1["eigen"][k]), ["max", "min", "rank_rel_1e-12"])
        for k in ("C_resp", "C_total", "C_total_resp"):
            self.assertIn("max", cr["eigen"][k])
        # the report's per-cell table is cresp.json's relative sigma, to its 2 dp (the check Q3 makes at run time)
        table = F.report_table(paths["cresp_report"].read_text())
        self.assertEqual(table["cells"], CELLS)
        for c in F.REPORT_COLUMNS:
            self.assertLessEqual(np.abs(100 * np.array(cr["relative_sigma"][c]) - np.array(table[c])).max(), 0.005 + 1e-9)
        self.assertEqual(s1["assembly_sha256"], F.PINS["s1_npz"])
        self.assertEqual(cr["assembly_sha256"], F.PINS["cresp_npz"])
        self.assertEqual(cr["meta"]["inputs_sha256"]["s1_assembly"], F.PINS["s1_npz"])
        self.assertEqual(g["extra_block"]["sha256"], F.PINS["cresp_npz"])
        self.assertEqual(g["inputs_sha256"]["s1_npz"], F.PINS["s1_npz"])
        for k in ("C_e", "C_model", "C_total"):
            self.assertIn(k, s1["relative_sigma"])
        for k in ("C_resp", "C_total_resp", "C_total"):
            self.assertIn(k, cr["relative_sigma"])
        self.assertEqual(g["predictions"][0]["name"], "genie_cv")
        self.assertEqual(len(g["predictions"][0]["cells"]), 16)


if __name__ == "__main__":
    unittest.main()
