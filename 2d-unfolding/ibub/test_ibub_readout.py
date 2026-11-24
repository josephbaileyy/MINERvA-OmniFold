#!/usr/bin/env python3
"""Tests for ``ibub_readout.py`` (IBUB-DECLARATION.md sections 4-6). Each mechanism fires on its defect and stays
silent on the clean case.

The pure statistics are checked on cases whose answer is known:
- the test matrix's cells and area-weighted bands;
- z*;
- the bootstrap counts;
- the paired difference, which cancels the truth;
- DIFFER on a planted offset, and NOT RESOLVED APART on equal methods.

C-OF runs COV2D's own errors, bias and spread_alone on a synthetic ensemble. It must pass on the committed values, and
fail on a perturbed surrogate and on two swapped truth rows. The means alone would pass the swap (the agy read's
finding 1), and the test shows that too.

The whole readout runs end to end through the real ``cov2d_readout.Run``, with its open audit guarding the fixture's
"pscratch". The patches are the ones ``test_cov2d_readout.Base`` uses: the MAT environment, part B's sums and Cells,
deploy_head and read_provenance. On top of the clean run, each of these must not read PASS: an incomplete unit set, a
unit whose data file is another toy's, a K = 10 row off its hXSec2D, a non-finite K = 5 cell, a broken C-OF, and --out
under a guarded tree.

Needs PyROOT (the audit wraps TFile.Open), numpy and scipy.
    cd 2d-unfolding/ibub && python -B -m unittest -v test_ibub_readout
"""
from __future__ import annotations

import copy
import hashlib
import io
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
import ibub_readout as ir  # noqa: E402
import ibub_unit as iu  # noqa: E402
c, cb, rd, cr, cs = ir.c, ir.cb, ir.rd, ir.cr, ir.cs
REAL_CONFIG = iu.load_config     # captured before any patch

T = "G18"
SEEDS = list(c.TOY_SEEDS[T])
REAL = c.REALIZATION_SEED[T]
KS = [1, 2, 3, 4, 5, 10, 15, 20]
JOB = "61000001"
DEPLOY = "M0"     # c.deploy_head is patched to return it, as test_cov2d_readout patches it


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def rep_mask() -> np.ndarray:
    """The real reported cells (224 -> 205), so every band has a cell."""
    return iu.reported_cells(REAL_CONFIG())


class Tree:
    """A synthetic tune: COV2D's records and products, and IBU units, under a guarded root g."""

    def __init__(self, d: Path, *, tune: str = "G18", ibu_offset_cell: int | None = None, offset: float = 0.0,
                 flagged: int = 1):
        self.d, self.T = d, tune
        self.SEEDS, self.REAL = list(c.TOY_SEEDS[tune]), c.REALIZATION_SEED[tune]
        self.pdir = rd.pseudo_dir(tune) + "/b"
        self.flagged = flagged
        self.g = d / "g"                    # the guarded tree ("pscratch")
        self.run = self.g / "cov2d-run"
        self.units = self.g / "ibub" / "units"
        self.rec = d / "rec"                # the repository's receipts (read through read_pinned)
        for p in (self.run / "out", self.run / self.pdir, self.units, self.rec / "pseudo" / self.T, d / "ns/out/ER"):
            p.mkdir(parents=True, exist_ok=True)
        rng = np.random.default_rng(11)
        self.rep = rep_mask()
        self.flat = np.flatnonzero(self.rep)
        n = self.flat.size
        self.area = rng.uniform(0.5, 2.0, n)
        base = rng.uniform(1.0, 3.0, n)
        self.sigma = 0.05 * base
        A = rng.normal(size=(n, n)) * 0.002
        self.C_T = np.diag(self.sigma ** 2) + A @ A.T
        self.C_model = np.diag((0.02 * base) ** 2)
        self.x_true = base + rng.normal(0, 0.01, (len(self.SEEDS), n))
        self.x_of = self.x_true + 0.01 * base + rng.normal(0, 0.03, (len(self.SEEDS), n))
        self.x_ibu = self.x_of + rng.normal(0, 0.003, (len(self.SEEDS), n))    # IBU tracks OF toy by toy, as on shared toys
        if ibu_offset_cell is not None:
            self.x_ibu[:, ibu_offset_cell] += offset
        self.vec = {}
        # E_R (the cells' source)
        (d / "ns/out/ER/xsec.root").write_bytes(b"ER")
        # the natures and the truth file
        natures = [{"seed": s, "role": "toy", "lateral_signs": [int(x) for x in rng.choice([-1, 1], 5)],
                    "norm_z": float(rng.normal())} for s in self.SEEDS]
        natures.append({"seed": self.REAL, "role": "realization", "lateral_signs": [1] * 5, "norm_z": 0.0})
        self.natures = natures
        pa = json.dumps({"natures": natures}).encode()
        (self.rec / "pseudo" / self.T / "pseudo_a.json").write_bytes(pa)
        self.pa_sha = sha(pa)
        full = np.zeros((len(natures), 224))
        full[: len(self.SEEDS), self.rep] = self.x_true
        full[-1, self.rep] = base
        buf = io.BytesIO()
        np.savez(buf, xsec=full.reshape(len(natures), 14, 16), seeds=np.array([nn["seed"] for nn in natures]))
        (self.run / self.pdir / "truth_xsec.npz").write_bytes(buf.getvalue())
        self.truth_sha = sha(buf.getvalue())
        # the blocks record
        self.minos_x = np.stack([base * 1.01, base * 0.99])
        blocks = {"rep": self.rep, "C_T": self.C_T, "C_model_abs": self.C_model, "minos_x": self.minos_x}
        for b in c.LATERAL_BANDS:
            blocks["band__" + b] = np.stack([base * (1 + 0.005), base * (1 - 0.005)])
        buf = io.BytesIO()
        np.savez(buf, **blocks)
        self.blocks_path = d / "blocks.npz"
        self.blocks_path.write_bytes(buf.getvalue())
        self.blocks = blocks
        # the OmniFold toy products and the completeness table
        rows = ["label\ttruth\tverdict\tsha256"]
        for k, s in enumerate(self.SEEDS):
            key = f"OF-{s}".encode()
            p = self.run / "out" / f"T_{self.T}_{s}"
            p.mkdir(exist_ok=True)
            (p / "xsec.root").write_bytes(key)
            self.vec[key.decode()] = self.x_of[k]
            rows.append(f"T_{self.T}_{s}\t{self.T}\tPASS\t{sha(key)}")
        for lab in self.other_labels():
            rows.append(f"{lab}\t{self.T}\tPASS\t{'0' * 64}")
        comp = ("\n".join(rows) + "\n").encode()
        self.comp_path = d / "completeness.tsv"
        self.comp_path.write_bytes(comp)
        self.comp = (self.comp_path, sha(comp))
        # the score record: COV2D's own functions on these errors
        self.score_path = d / "score.json"
        self.write_score()
        # pseudo_b (the toys' data digests) and C2's record
        self.data_sha = {s: sha(f"data-{s}".encode()) for s in self.SEEDS}
        pb = {"verdict": "PASS", "files": [{"seed": s, "role": "toy", "sha256": self.data_sha[s],
                                            "path": f"{self.run}/{self.pdir}/data_{s}.root"} for s in self.SEEDS]}
        pb["files"].append({"seed": self.REAL, "role": "realization", "sha256": "r" * 64,
                            "path": f"{self.run}/{self.pdir}/data_{self.REAL}.root"})
        pbb = json.dumps(pb).encode()
        self.pb_path = d / "pseudo_b.json"
        self.pb_path.write_bytes(pbb)
        self.pb_sha = sha(pbb)
        c2 = json.dumps({"b": {self.T: {"variance_ratio": {"option_1_clipped": [1.0] * (n - 2) + [0.8, 0.85]}}},
                         "efficiency": {"cells205": [int(x) for x in self.flat]}}).encode()
        self.c2_path = d / "c2.json"
        self.c2_path.write_bytes(c2)
        self.c2 = (self.c2_path, sha(c2))
        self.prov = {}
        for k, s in enumerate(self.SEEDS):
            self.write_unit(k, s)
        self.write_barrier()

    def write_barrier(self, done=None, **change):
        """The two reference markers, the barrier receipt with their digests, and the job's IBUB-DONE binding the
        receipt's sha256 (as refcheck, complete and the job write them)."""
        units = {}
        for u in iu.REFERENCE_UNITS:
            m = {"unit": u, "verdict": "PASS", "job": JOB, "deploy_head": DEPLOY, "sha256": sha(u.encode()),
                 "root_sha256": sha(u.encode() + b"r")}
            (self.units / f"{u}.done").write_text(json.dumps(m))
            units[u] = {"pass": True, "srun_rc": 0, "npz_sha256": m["sha256"], "root_sha256": m["root_sha256"]}
        rec = {"verdict": "PASS", "job": JOB, "deploy_head": DEPLOY, "runner_sha256": iu.rc.sha256(Path(iu.__file__)),
               "units": units}
        rec.update(change)
        raw = json.dumps(rec).encode()
        (self.units / "refcheck.json").write_bytes(raw)
        d = {"job": JOB, "M": DEPLOY, "stage": "toys", "rc": 0,
             "completion": {"verdict": "PASS", "barrier_sha256": sha(raw)}}
        d.update(done or {})
        (self.units.parent / "IBUB-DONE").write_text(json.dumps(d))

    def other_labels(self):
        labs = [f"X_{self.T}"] + [f"U_{self.T}_{b}_{i}" for b in c.ORDER for i in range(c.BANDS[b])]
        labs += [f"L_{self.T}_{b}_{i}" for b in c.LATERAL_BANDS for i in (0, 1)]
        return labs + [f"B_{self.T}_{n:03d}" for n in range(1, 301)]

    def errors_post(self, x_true=None):
        bands = {b: self.blocks["band__" + b] for b in c.LATERAL_BANDS}
        deltas = cs.lateral_deltas(bands, self.minos_x)
        return cs.errors(self.x_of, self.x_true if x_true is None else x_true, self.natures, deltas, self.C_T)[0]

    def write_score(self, x_true=None, tweak=0.0):
        E = self.errors_post(x_true)
        sigma = np.sqrt(np.diag(self.C_T))
        sa = cr.spread_alone(E, self.C_T, self.C_model)
        bias = list(np.asarray(cr.bias(E, sigma)) + tweak)
        rec = {"readouts": {"bias": bias, "spread_alone": sa}, "grade": {"flagged_cells": [int(x) for x in self.flat[3:3 + self.flagged]]}}
        raw = json.dumps(rec).encode()
        self.score_path.write_bytes(raw)
        self.score_sha = sha(raw)

    def write_unit(self, k, s, *, data_sha=None, k10_tweak=0.0, k5_nan=False, verdict="PASS"):
        name = f"toy_{self.T}_{s}"
        full = np.zeros((len(KS), 224))
        for i, K in enumerate(KS):
            full[i, self.rep] = self.x_ibu[k]
        full[KS.index(10), self.rep] *= (1 + k10_tweak)
        if k5_nan:
            full[KS.index(5), self.rep][0] = np.nan
            full[KS.index(5), int(self.flat[0])] = np.nan
        ds = self.data_sha[s] if data_sha is None else data_sha
        meta = {"kind": "toy", "tune": self.T, "seed": s, "data_sha256": ds,
                "controls": {k: {"pass": True} for k in iu.CONTROLS["toy"]}, "slurm_job": JOB, "deploy_head": DEPLOY,
                "runner_sha256": iu.rc.sha256(Path(iu.__file__)), "config_sha256": iu.rc.sha256(iu.CONFIG)}
        buf = io.BytesIO()
        np.savez(buf, ks=np.array(KS), xsec=full, meta=json.dumps(meta))
        (self.units / f"{name}.npz").write_bytes(buf.getvalue())
        key = f"IBU-{s}".encode()
        (self.units / f"{name}.root").write_bytes(key)
        self.vec[key.decode()] = self.x_ibu[k]
        self.prov[key.decode()] = {"dataFileSha256": ds}
        (self.units / f"{name}.done").write_text(json.dumps({
            "unit": name, "kind": "toy", "tune": self.T, "seed": s, "job": JOB, "deploy_head": DEPLOY, "verdict": verdict,
            "sha256": sha(buf.getvalue()), "root_sha256": sha(key), "data_sha256": ds}))

    def reorder_truth(self):
        """truth_xsec.npz with two rows' seeds exchanged (its rows no longer follow the natures)."""
        p = self.run / self.pdir / "truth_xsec.npz"
        z = dict(np.load(p))
        z["seeds"] = z["seeds"].copy()
        z["seeds"][[0, 1]] = z["seeds"][[1, 0]]
        buf = io.BytesIO()
        np.savez(buf, **z)
        p.write_bytes(buf.getvalue())
        self.truth_sha = sha(buf.getvalue())

    def reorder_natures(self):
        """pseudo_a.json (and the truth rows with it) with two toys exchanged: the toys are out of the declared order."""
        nat = list(self.natures)
        nat[0], nat[1] = nat[1], nat[0]
        raw = json.dumps({"natures": nat}).encode()
        (self.rec / "pseudo" / self.T / "pseudo_a.json").write_bytes(raw)
        self.pa_sha = sha(raw)
        p = self.run / self.pdir / "truth_xsec.npz"
        z = dict(np.load(p))
        z["seeds"] = np.array([n["seed"] for n in nat])
        buf = io.BytesIO()
        np.savez(buf, **z)
        p.write_bytes(buf.getvalue())
        self.truth_sha = sha(buf.getvalue())

    def config(self) -> dict:
        cfg = REAL_CONFIG()
        cfg["cov2d_records"][self.T].update(blocks=str(self.blocks_path), blocks_sha256=sha(self.blocks_path.read_bytes()),
                                       score=str(self.score_path), score_sha256=self.score_sha,
                                       truth_xsec_sha256=self.truth_sha)
        cfg["cells"].update(blocks=str(self.blocks_path), blocks_sha256=sha(self.blocks_path.read_bytes()))
        cfg["toys"][self.T].update(dir=f"{self.run}/{self.pdir}", pseudo_b=str(self.pb_path), pseudo_b_sha256=self.pb_sha)
        cfg["readout"]["bootstrap_B"] = 2000
        cfg["readout"]["write_root"] = str(self.d)          # the declared readout root, for the test
        return cfg


class Patched(unittest.TestCase):
    """The real Run and its open audit, patched as test_cov2d_readout.Base patches them."""

    def patch(self, tree: Tree, cfg: dict | None = None):
        tr = tree

        class FakeCells:
            def __init__(self, er):
                self.rep, self.area = tr.rep, tr.area

            def vec(self, path):
                return tr.vec[Path(path).read_bytes().decode()]
        ro = cb.rollup()
        patches = [
            (cb, "AUDIT", None), (cb.OpenAudit.__init__, "__defaults__", ((str(tr.g),),)), (cb, "GUARDED", (str(tr.g),)),
            (cb, "pinned_mat_environment", lambda: {"stub": "MAT"}),
            (ro, "NS_R", str(tr.d / "ns")), (ro, "partb_sums", lambda: {"ER/xsec.root": sha(b"ER")}), (ro, "Cells", FakeCells),
            (rd, "COMPLETENESS", tr.comp), (rd, "C2_RECORD", tr.c2), (rd, "REC", tr.rec),
            (rd, "PSEUDO_A_SHA", {tr.T: tr.pa_sha}),
            (rd, "read_provenance", lambda p: tr.prov[Path(p).read_bytes().decode()]),
            (c, "deploy_head", lambda root: "M0"),
            (iu, "load_config", lambda path=None: cfg or tr.config()),
            (rd.Run, "watch", lambda self_, path: None),      # macOS has no O_NOATIME, so reads move atime
            (os, "O_NOATIME", getattr(os, "O_NOATIME", 0)),
        ]
        for target, attr, value in patches:
            p = mock.patch.object(target, attr, value, create=True)
            p.start()
            self.addCleanup(p.stop)
        tmp = Path(tempfile.mkdtemp(dir=tr.d))
        p = mock.patch.dict(os.environ, {"TMPDIR": str(tmp)})
        p.start()
        self.addCleanup(p.stop)
        self.addCleanup(lambda: cb.AUDIT is not None and cb.AUDIT.uninstall())

    def go(self, tree: Tree, name="out"):
        return ir.readout(tree.T, tree.units, tree.d / name, str(tree.run), JOB)


# ------------------------------------------------------------------------------------------- pure


class Pure(unittest.TestCase):
    def test_test_matrix_has_the_cells_then_31_area_weighted_bands(self):
        rep = rep_mask()
        flat = np.flatnonzero(rep)
        area = np.arange(1, 206, dtype=float)
        W, labels = ir.test_matrix(flat, area)
        self.assertEqual(W.shape, (205, 236))
        np.testing.assert_array_equal(W[:, :205], np.eye(205))
        self.assertEqual(labels[205], "pt:0")
        self.assertEqual(labels[219], "pz:0")
        self.assertEqual(labels[-1], "total")
        np.testing.assert_array_equal(W[:, -1], area)
        for i in range(14):                  # p_T band i holds exactly the cells with flat // 16 == i, by their area
            col = W[:, 205 + i]
            np.testing.assert_array_equal(col, np.where(flat // 16 == i, area, 0))
        for j in range(16):
            np.testing.assert_array_equal(W[:, 219 + j], np.where(flat % 16 == j, area, 0))
        self.assertEqual([int((W[:, 205 + i] > 0).sum()) for i in range(14)],
                         [16] * 9 + [15, 14, 13, 11, 8])      # the declaration's per-band counts (section 4)
        with self.assertRaises(c.Refusal):
            ir.test_matrix(flat[flat // 16 != 13], area[flat // 16 != 13])   # an empty band is refused

    def test_z_star_is_the_declared_bonferroni_value(self):
        self.assertAlmostEqual(ir.z_star(0.05, 236), 3.7044, places=4)
        self.assertGreater(ir.z_star(0.05, 236), ir.z_star(0.05, 205))

    def test_bootstrap_counts_are_resamples_and_seeded(self):
        a = ir.bootstrap_counts(300, 50, [5_760_000, 0])
        self.assertEqual(a.shape, (50, 300))
        np.testing.assert_array_equal(a.sum(axis=1), 300)
        np.testing.assert_array_equal(a, ir.bootstrap_counts(300, 50, [5_760_000, 0]))
        self.assertFalse(np.array_equal(a, ir.bootstrap_counts(300, 50, [5_760_000, 1])))   # the tune index matters

    def test_ratio_never_hides_a_zero_denominator(self):
        np.testing.assert_array_equal(ir.ratio([1.0, 0.0, -2.0, 4.0], [0.0, 0.0, 0.0, 2.0]), [np.inf, 0.0, -np.inf, 2.0])

    def synthetic(self, offset=0.0, cell=7, n=300, p=205, seed=4):
        rng = np.random.default_rng(seed)
        flat = np.flatnonzero(rep_mask())
        W, labels = ir.test_matrix(flat, np.ones(p))
        x_true = 1 + rng.normal(0, 0.05, (n, p))
        shared = rng.normal(0, 0.03, (n, p))
        E_of = shared + 0.01
        E_ibu = shared + rng.normal(0, 0.002, (n, p)) + 0.01
        E_ibu[:, cell] += offset
        C_T = np.eye(p) * 0.03 ** 2
        counts = ir.bootstrap_counts(n, 2000, [1, 0])
        return E_of, E_ibu, x_true, W, labels, C_T, counts

    def test_equal_methods_are_not_resolved_apart_and_never_differ(self):
        E_of, E_ibu, x_true, W, labels, C_T, counts = self.synthetic()
        s = ir.statistics(E_of, E_ibu, x_true, W, labels, C_T, counts, 0.05, 205)
        self.assertEqual(s["reading"], "NOT RESOLVED APART")
        self.assertEqual(s["differ_at"], [])
        self.assertEqual(len(s["difference"]["resolution_rel_pct"]), 236)
        self.assertTrue(all(np.isfinite(s["difference"]["resolution_rel_pct"])))
        # each method's own bias is printed with its own SE (the director's ruling 3): 0.01 at SE ~0.0017 is resolved
        # almost everywhere, for both methods
        self.assertGreater(len(s["summary"]["OF"]["bias_resolved"]), 220)
        self.assertGreater(len(s["summary"]["IBU"]["bias_resolved"]), 220)
        # the summaries: a 0.01 bias on truths near 1 is about 1 %, and the two methods' biases are interleaved
        for k in ("OF", "IBU"):
            self.assertTrue(0.8 < s["summary"][k]["rms_rel_pct"] < 1.3, s["summary"][k])
            self.assertTrue(0.7 < s["summary"][k]["median_abs_rel_pct"] < 1.3, s["summary"][k])
        self.assertTrue(40 < s["summary"]["cells_ibu_smaller_abs_bias"] < 165, s["summary"])
        un = np.asarray(s["difference"]["unpaired_ratio"])
        self.assertEqual(un.shape, (236,))
        self.assertLess(float(np.median(un)), 1.0)        # equal methods: well inside the unpaired noise
        self.assertEqual(len(s["method"]["IBU"]["se_boot"]), 236)

    def test_a_planted_offset_differs_at_its_cell_and_its_bands(self):
        E_of, E_ibu, x_true, W, labels, C_T, counts = self.synthetic(offset=0.01, cell=7)
        s = ir.statistics(E_of, E_ibu, x_true, W, labels, C_T, counts, 0.05, 205)
        self.assertEqual(s["reading"], "DIFFER")
        named = {x["test"] for x in s["differ_at"]}
        g = int(np.flatnonzero(rep_mask())[7])
        self.assertIn(f"cell:{g}", named)
        self.assertTrue(named <= {f"cell:{g}", f"pt:{g // 16}", f"pz:{g % 16}", "total"})
        self.assertEqual([x["sign"] for x in s["differ_at"] if x["test"] == f"cell:{g}"], ["IBU above OF"])

    def test_the_difference_does_not_see_the_truth(self):
        """Paired: shifting each toy's truth by any vector moves both methods' errors and leaves the difference."""
        E_of, E_ibu, x_true, W, labels, C_T, counts = self.synthetic(offset=0.004)
        shift = np.random.default_rng(9).normal(0, 0.2, E_of.shape)
        a = ir.statistics(E_of, E_ibu, x_true, W, labels, C_T, counts, 0.05, 205)
        b = ir.statistics(E_of - shift, E_ibu - shift, x_true + shift, W, labels, C_T, counts, 0.05, 205)
        np.testing.assert_allclose(a["difference"]["mean"], b["difference"]["mean"], atol=1e-12)
        np.testing.assert_allclose(a["difference"]["se_boot"], b["difference"]["se_boot"], atol=1e-12)
        self.assertNotEqual(a["method"]["OF"]["mean"], b["method"]["OF"]["mean"])

    def test_the_paired_se_is_far_below_the_unpaired_one_on_shared_toys(self):
        E_of, E_ibu, x_true, W, labels, C_T, counts = self.synthetic()
        s = ir.statistics(E_of, E_ibu, x_true, W, labels, C_T, counts, 0.05, 205)
        d_se = np.asarray(s["difference"]["se_boot"])[:205]
        un = np.sqrt(np.asarray(s["method"]["OF"]["se_boot"]) ** 2 + np.asarray(s["method"]["IBU"]["se_boot"]) ** 2)[:205]
        self.assertLess(np.median(d_se / un), 0.2)
        r = s["bootstrap_over_analytic_se"]
        self.assertTrue(0.85 < r["median"] < 1.15, r)

    def test_hotelling_is_descriptive_and_computed(self):
        E_of, E_ibu, x_true, W, labels, C_T, counts = self.synthetic()
        h = ir.statistics(E_of, E_ibu, x_true, W, labels, C_T, counts, 0.05, 205)["hotelling"]
        self.assertEqual(h["df"], [205, 95])
        self.assertEqual(h["read_by"], "nothing")
        self.assertGreater(h["T2"], 0)

    def test_c_of_passes_on_cov2ds_own_values_and_fails_a_perturbed_surrogate_and_a_mispairing(self):
        tr = Tree(Path(tempfile.mkdtemp()).resolve())
        self.addCleanup(shutil.rmtree, tr.d)
        sc = json.loads(tr.score_path.read_text())["readouts"]
        self.assertTrue(ir.c_of(tr.errors_post(), tr.C_T, tr.C_model, sc)["pass"])
        bad = copy.deepcopy(tr.natures)                  # one toy's norm_z off by 1e-6
        bad[5]["norm_z"] += 1e-6
        bands = {b: tr.blocks["band__" + b] for b in c.LATERAL_BANDS}
        E_bad = cs.errors(tr.x_of, tr.x_true, bad, cs.lateral_deltas(bands, tr.minos_x), tr.C_T)[0]
        self.assertFalse(ir.c_of(E_bad, tr.C_T, tr.C_model, sc)["pass"])
        swapped = tr.x_true.copy()                       # two toys' truths exchanged
        swapped[[0, 1]] = swapped[[1, 0]]
        got = ir.c_of(tr.errors_post(swapped), tr.C_T, tr.C_model, sc)
        self.assertFalse(got["pass"])
        self.assertTrue(got["bias"]["pass"] and got["pull_mean"]["pass"])   # the means alone are blind to it
        self.assertFalse(got["pull_sd"]["pass"])


# ------------------------------------------------------------------------------------------- end to end


class EndToEnd(Patched):
    def setUp(self):
        self.td = Path(tempfile.mkdtemp()).resolve()    # resolved, as the audit compares realpaths
        self.addCleanup(shutil.rmtree, self.td)

    def test_clean_run_reads_not_resolved_apart_with_every_control_passed(self):
        tr = Tree(self.td)
        self.patch(tr)
        rec = self.go(tr)
        self.assertEqual(rec["verdict"], "PASS", rec.get("controls_failed"))
        self.assertTrue(rec["C-OF"]["pass"])
        self.assertEqual(rec["C-COMPLETE"]["missing"], [])
        self.assertEqual(rec["reading"], {"K10": "NOT RESOLVED APART", "K5": "NOT RESOLVED APART"})
        self.assertEqual(rec["readings"]["K10"]["tests"], 236)
        self.assertEqual(set(rec["descriptive"]["cov2d_flagged_cells"]), {str(int(tr.flat[3]))})
        self.assertEqual(rec["descriptive"]["weakened_cells"], [int(tr.flat[-2]), int(tr.flat[-1])])
        z = np.load(tr.d / "out" / f"ibub_{T}_errors.npz")
        np.testing.assert_allclose(z["E_of"], tr.x_of - tr.x_true)        # before the surrogates (section 2)
        np.testing.assert_allclose(z["E_ibu10"], tr.x_ibu - tr.x_true)
        self.assertTrue((tr.d / "out" / f"ibub_{T}.json").exists())
        self.assertEqual(rec["open_audit"]["refused"], [])
        self.assertGreater(rec["open_audit"]["guarded_opens_total"], 600)

    def test_a_planted_ibu_offset_differs(self):
        tr = Tree(self.td, ibu_offset_cell=10, offset=0.05)
        self.patch(tr)
        rec = self.go(tr)
        self.assertEqual(rec["verdict"], "PASS")
        self.assertEqual(rec["reading"]["K10"], "DIFFER")
        self.assertIn(f"cell:{int(tr.flat[10])}", {x["test"] for x in rec["readings"]["K10"]["differ_at"]})

    def test_a_missing_unit_reads_incomplete_with_no_reading(self):
        tr = Tree(self.td)
        (tr.units / f"toy_{T}_{SEEDS[17]}.done").unlink()
        self.patch(tr)
        rec = self.go(tr)
        self.assertEqual(rec["verdict"], "INCOMPLETE")
        self.assertEqual(rec["C-COMPLETE"]["missing"], [SEEDS[17]])
        self.assertNotIn("reading", rec)

    def test_a_unit_on_another_toys_data_is_invalid(self):
        tr = Tree(self.td)
        tr.write_unit(3, SEEDS[3], data_sha=tr.data_sha[SEEDS[4]])
        self.patch(tr)
        rec = self.go(tr)
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertTrue(any(str(SEEDS[3]) in p for p in rec["C-DATA"]["problems"]))
        self.assertNotIn("reading", rec)

    def test_a_product_recording_another_toys_data_is_invalid(self):
        tr = Tree(self.td)
        tr.prov[f"IBU-{SEEDS[7]}"] = {"dataFileSha256": tr.data_sha[SEEDS[8]]}     # marker and meta are right
        self.patch(tr)
        rec = self.go(tr)
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertTrue(any("dataFileSha256" in p for p in rec["C-DATA"]["problems"]))

    def test_a_k10_row_off_its_hxsec2d_is_invalid(self):
        tr = Tree(self.td)
        tr.write_unit(8, SEEDS[8], k10_tweak=1e-7)
        self.patch(tr)
        rec = self.go(tr)
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertFalse(rec["C-K10"]["pass"])

    def test_a_nonfinite_k5_cell_is_invalid(self):
        tr = Tree(self.td)
        tr.write_unit(2, SEEDS[2], k5_nan=True)
        self.patch(tr)
        rec = self.go(tr)
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertEqual(rec["C-CELLS"]["nonfinite"], {"K10": 0, "K5": 1})

    def test_a_broken_c_of_is_invalid(self):
        tr = Tree(self.td)
        tr.write_score(tweak=1e-9)
        self.patch(tr)
        rec = self.go(tr)
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertFalse(rec["C-OF"]["bias"]["pass"])

    def test_a_truth_file_off_its_pin_is_a_recorded_refusal_with_no_reading(self):
        tr = Tree(self.td)
        cfg = tr.config()
        cfg["cov2d_records"][T]["truth_xsec_sha256"] = "0" * 64
        self.patch(tr, cfg)
        rec = self.go(tr)                                     # the codex read, blocker 7: a record, never a bare raise
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertIn("sha256", rec["refused"])
        self.assertNotIn("readings", json.loads((tr.d / "out" / f"ibub_{T}.json").read_text()))

    def test_a_missing_truth_file_is_a_recorded_refusal(self):
        tr = Tree(self.td)
        (tr.run / tr.pdir / "truth_xsec.npz").unlink()
        self.patch(tr)
        rec = self.go(tr)                                     # the codex read r2, item 6: a record, never a bare raise
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertIn("truth_xsec.npz", rec["refused"])
        self.assertTrue((tr.d / "out" / f"ibub_{T}.json").exists())

    def test_out_or_tmp_outside_the_declared_readout_root_is_refused(self):
        """The codex read r2, item 3: e.g. /dev/shm/limres-rpd-flux1, which is outside the declared root."""
        tr = Tree(self.td)
        cfg = tr.config()
        cfg["readout"]["write_root"] = str(tr.d / "root")
        (tr.d / "root").mkdir()
        self.patch(tr, cfg)
        with self.assertRaises(c.Refusal):
            ir.readout(T, tr.units, tr.d / "elsewhere-out", str(tr.run), JOB)
        self.assertFalse((tr.d / "elsewhere-out").exists())
        with mock.patch.dict(os.environ, {"TMPDIR": str(tr.d)}), self.assertRaises(c.Refusal):
            ir.readout(T, tr.units, tr.d / "root" / "out", str(tr.run), JOB)
        (tr.d / "root" / "existing").mkdir()
        (tr.d / "root" / "tmp").mkdir()
        with mock.patch.dict(os.environ, {"TMPDIR": str(tr.d / "root" / "tmp")}), self.assertRaises(c.Refusal) as cm:
            ir.readout(T, tr.units, tr.d / "root" / "existing", str(tr.run), JOB)   # an existing out is never written
        self.assertIn("exists", str(cm.exception))

    def test_the_result_appears_at_once_and_names_its_npz(self):
        """The codex read r2, item 5: a staging directory becomes out by one rename; a failure before it leaves no
        out; a PASS record names its npz's digest."""
        tr = Tree(self.td)
        self.patch(tr)
        with mock.patch.object(np, "savez_compressed", side_effect=OSError("disk full")), self.assertRaises(OSError):
            self.go(tr)
        self.assertFalse((tr.d / "out").exists())
        tr2 = Tree(Path(tempfile.mkdtemp()).resolve())
        self.addCleanup(shutil.rmtree, tr2.d, True)
        self.patch(tr2)
        rec = self.go(tr2)
        self.assertEqual(rec["verdict"], "PASS")
        on_disk = json.loads((tr2.d / "out" / f"ibub_{T}.json").read_text())
        self.assertEqual(on_disk["errors_npz_sha256"], iu.rc.sha256(tr2.d / "out" / on_disk["errors_npz"]))
        self.assertIn("readings", on_disk)
        self.assertEqual([p.name for p in tr2.d.glob(".out.staging-*")], [])

    def test_c_cells_counts_each_artifact_on_its_own(self):
        """The codex read r2, item 4: a non-finite ROOT row counts even when its npz fails its digest, and a
        non-finite K = 10 npz row fails C-K10 without being counted twice."""
        tr = Tree(self.td)
        k = 50
        tr.x_ibu[k, 3] = np.nan                               # its ROOT row (hXSec2D) holds a NaN
        tr.write_unit(k, SEEDS[k])
        (tr.units / f"toy_{T}_{SEEDS[k]}.npz").write_bytes(b"corrupt")    # and its npz is off its digest
        self.patch(tr)
        rec = self.go(tr)
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertEqual(rec["C-CELLS"]["nonfinite"], {"K10": 1, "K5": 0})
        td = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, td, True)
        tr = Tree(td)
        tr.write_unit(51, SEEDS[51], k10_tweak=np.nan)        # only the npz's K = 10 row is non-finite
        self.patch(tr)
        rec = self.go(tr)
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertFalse(rec["C-K10"]["pass"])
        self.assertEqual(rec["C-CELLS"]["nonfinite"], {"K10": 0, "K5": 0})

    def test_out_under_a_guarded_tree_is_refused(self):
        tr = Tree(self.td)
        self.patch(tr)
        with self.assertRaises(c.Refusal):
            ir.readout(T, tr.units, tr.g / "out", str(tr.run), JOB)
        self.assertFalse((tr.g / "out").exists())

    def test_a_unit_that_failed_or_names_another_toy_or_scan_does_not_read_pass(self):
        tr = Tree(self.td)
        name = lambda k: tr.units / f"toy_{T}_{SEEDS[k]}"      # noqa: E731
        m = json.loads(name(1).with_suffix(".done").read_text())
        name(1).with_suffix(".done").write_text(json.dumps(dict(m, verdict="FAIL")))
        self.patch(tr)
        rec = self.go(tr, "o1")
        self.assertEqual(rec["verdict"], "INCOMPLETE")       # the codex read r2, item 6: a FAIL alone is an absence
        self.assertEqual(rec["C-COMPLETE"]["missing"], [SEEDS[1]])
        self.assertEqual(rec["C-DATA"]["problems"], [])

    def rewrite_meta(self, tr, k, **change):
        """Rewrite toy k's npz with a changed meta or scan, and its marker's digest to match."""
        name = tr.units / f"toy_{T}_{SEEDS[k]}"
        z = dict(np.load(name.with_suffix(".npz")))
        meta = json.loads(str(z["meta"]))
        meta.update(change.pop("meta", {}))
        z.update(change)
        z["meta"] = json.dumps(meta)
        buf = io.BytesIO()
        np.savez(buf, **z)
        name.with_suffix(".npz").write_bytes(buf.getvalue())
        m = json.loads(name.with_suffix(".done").read_text())
        name.with_suffix(".done").write_text(json.dumps(dict(m, sha256=sha(buf.getvalue()))))

    def test_a_unit_naming_another_seed_is_invalid(self):
        tr = Tree(self.td)
        self.rewrite_meta(tr, 4, meta={"seed": SEEDS[5]})
        self.patch(tr)
        rec = self.go(tr)
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertTrue(any("meta names" in p for p in rec["C-DATA"]["problems"]))

    def test_a_unit_with_a_failed_control_is_invalid(self):
        tr = Tree(self.td)
        self.rewrite_meta(tr, 6, meta={"controls": {"C-FILL": {"pass": False}}})
        self.patch(tr)
        rec = self.go(tr)
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertTrue(any("a unit control failed" in p for p in rec["C-DATA"]["problems"]))

    def test_a_unit_with_another_scan_is_incomplete(self):
        tr = Tree(self.td)
        self.rewrite_meta(tr, 9, ks=np.array([1, 2, 3, 4, 5, 10, 15, 25]))
        self.patch(tr)
        rec = self.go(tr)
        self.assertEqual(rec["verdict"], "INVALID")             # agy read 1 finding 3: recorded, not a crash
        self.assertEqual(rec["C-COMPLETE"]["missing"], [SEEDS[9]])
        self.assertTrue(any("K scan" in p for p in rec["C-DATA"]["problems"]))

    def test_c_truth_refuses_each_misorder(self):
        """Three refusals before any reading: the truth rows against the natures, the natures' toys against the
        declared seeds, and the OmniFold labels against the declared seeds."""
        cases = {
            "truth rows": lambda tr: tr.reorder_truth(),
            "natures": lambda tr: tr.reorder_natures(),
        }
        for tag, defect in cases.items():
            td = Path(tempfile.mkdtemp()).resolve()
            self.addCleanup(shutil.rmtree, td, True)
            tr = Tree(td)
            defect(tr)
            with self.subTest(defect=tag):
                self.patch(tr)
                rec = self.go(tr)
                self.assertEqual(rec["verdict"], "INVALID")
                self.assertTrue(any(x.startswith("C-TRUTH") for x in rec["controls_failed"]), rec["controls_failed"])
                self.assertTrue((tr.d / "out" / f"ibub_{T}.json").exists())
        td = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, td, True)
        tr = Tree(td)
        self.patch(tr)
        real_plan = rd.plan

        def reversed_toys(truth, comp):
            p = real_plan(truth, comp)
            return dict(p, toy=p["toy"][::-1])
        with mock.patch.object(rd, "plan", reversed_toys):
            rec = self.go(tr, "o2")
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertIn("C-TRUTH: the OmniFold labels are not the declared seeds in order", rec["controls_failed"])

    def test_cells_other_than_the_configs_are_refused(self):
        tr = Tree(self.td)
        rep = tr.rep.copy()
        rep[int(np.flatnonzero(~rep)[0])] = True
        self.patch(tr)
        with mock.patch.object(iu, "reported_cells", lambda cfg: rep):
            rec = self.go(tr)
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertTrue(any("cells differ" in x for x in rec["controls_failed"]))

    def test_a_test_count_other_than_the_declared_is_refused(self):
        tr = Tree(self.td)
        cfg = tr.config()
        cfg["readout"]["tests"] = 235
        self.patch(tr, cfg)
        rec = self.go(tr)
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertNotIn("readings", rec)

    def test_main_prints_the_verdict_and_exits_by_it(self):
        tr = Tree(self.td)
        self.patch(tr)
        self.assertEqual(ir.main(["--truth", T, "--units", str(tr.units), "--out", str(tr.d / "m"),
                                  "--run-dir", str(tr.run), "--job", JOB]), 0)
        (tr.units / f"toy_{T}_{SEEDS[0]}.done").unlink()
        self.assertEqual(ir.main(["--truth", T, "--units", str(tr.units), "--out", str(tr.d / "m2"),
                                  "--run-dir", str(tr.run), "--job", JOB]), 3)

    def test_a_unit_from_another_job_runner_or_config_is_invalid(self):
        for k, v in (("slurm_job", "61000002"), ("runner_sha256", "0" * 64), ("config_sha256", "1" * 64)):
            td = Path(tempfile.mkdtemp()).resolve()
            self.addCleanup(shutil.rmtree, td, True)
            tr = Tree(td)
            self.rewrite_meta(tr, 12, meta={k: v})
            with self.subTest(field=k):
                self.patch(tr)
                rec = self.go(tr)
                self.assertEqual(rec["verdict"], "INVALID")
                self.assertTrue(any(k in p for p in rec["C-DATA"]["problems"]), rec["C-DATA"])

    def test_a_unit_lacking_a_declared_control_is_invalid(self):
        tr = Tree(self.td)
        self.rewrite_meta(tr, 13, meta={"controls": {k: {"pass": True} for k in sorted(iu.CONTROLS["toy"])[1:]}})
        self.patch(tr)
        rec = self.go(tr)
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertTrue(any("not the declared" in p for p in rec["C-DATA"]["problems"]))

    def test_a_unit_whose_products_are_off_its_marker_is_incomplete_not_a_crash(self):
        tr = Tree(self.td)
        (tr.units / f"toy_{T}_{SEEDS[14]}.npz").write_bytes(b"corrupt")
        (tr.units / f"toy_{T}_{SEEDS[15]}.root").unlink()
        self.patch(tr)
        rec = self.go(tr)
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertEqual(rec["C-COMPLETE"]["missing"], [SEEDS[14], SEEDS[15]])
        probs = rec["C-DATA"]["problems"]
        self.assertTrue(any(str(SEEDS[14]) in p and "npz" in p for p in probs), probs)
        self.assertTrue(any(str(SEEDS[15]) in p and "ROOT product" in p for p in probs), probs)

    def test_ar23_runs_end_to_end_at_its_own_paths_seed_and_cells(self):
        tr = Tree(self.td, tune="AR23", flagged=2)
        self.patch(tr)
        rec = self.go(tr)
        self.assertEqual(rec["verdict"], "PASS", rec.get("controls_failed"))
        self.assertEqual(rec["truth"], "AR23")
        self.assertEqual(rec["bootstrap"], {"B": 2000, "seed": [5_760_000, 1]})
        self.assertEqual(set(rec["descriptive"]["cov2d_flagged_cells"]), {str(int(x)) for x in tr.flat[3:5]})
        self.assertTrue(str(tr.run / "pseudo/AR23-a2/b") in tr.config()["toys"]["AR23"]["dir"])
        self.assertEqual(rec["C-CELLS"]["negative"], {"K10": 0, "K5": 0})

    def test_a_truncated_or_misnamed_marker_is_missing_not_a_crash(self):
        tr = Tree(self.td)
        (tr.units / f"toy_{T}_{SEEDS[20]}.done").write_text("")                  # empty
        (tr.units / f"toy_{T}_{SEEDS[21]}.done").write_text('{"unit": "toy_G18')   # truncated
        m = json.loads((tr.units / f"toy_{T}_{SEEDS[23]}.done").read_text())
        (tr.units / f"toy_{T}_{SEEDS[22]}.done").write_text(json.dumps(m))        # toy 23's marker in toy 22's place
        self.patch(tr)
        rec = self.go(tr)
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertEqual(rec["C-COMPLETE"]["missing"], [SEEDS[20], SEEDS[21], SEEDS[22]])
        self.assertEqual(sum("not readable JSON" in p for p in rec["C-DATA"]["problems"]), 2)
        self.assertTrue(any("done-marker names" in p for p in rec["C-DATA"]["problems"]))

    def test_a_marker_naming_another_toys_data_is_invalid(self):
        tr = Tree(self.td)
        f = tr.units / f"toy_{T}_{SEEDS[24]}.done"
        f.write_text(json.dumps(dict(json.loads(f.read_text()), data_sha256=tr.data_sha[SEEDS[25]])))  # meta is right
        self.patch(tr)
        rec = self.go(tr)
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertTrue(any("is not toy" in p for p in rec["C-DATA"]["problems"]))

    def test_a_unit_naming_another_tune_or_kind_is_invalid(self):
        for field, value in (("tune", "AR23"), ("kind", "central_df")):
            td = Path(tempfile.mkdtemp()).resolve()
            self.addCleanup(shutil.rmtree, td, True)
            tr = Tree(td)
            self.rewrite_meta(tr, 26, meta={field: value})
            with self.subTest(field=field):
                self.patch(tr)
                rec = self.go(tr)
                self.assertEqual(rec["verdict"], "INVALID")
                self.assertTrue(any("meta names" in p for p in rec["C-DATA"]["problems"]))

    def test_an_npz_whose_meta_is_not_json_is_missing(self):
        tr = Tree(self.td)
        self.rewrite_meta(tr, 27)
        name = tr.units / f"toy_{T}_{SEEDS[27]}"
        z = dict(np.load(name.with_suffix(".npz")))
        z["meta"] = "{not json"
        buf = io.BytesIO()
        np.savez(buf, **z)
        name.with_suffix(".npz").write_bytes(buf.getvalue())
        m = json.loads(name.with_suffix(".done").read_text())
        name.with_suffix(".done").write_text(json.dumps(dict(m, sha256=sha(buf.getvalue()))))
        self.patch(tr)
        rec = self.go(tr)
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertTrue(any("not readable" in p for p in rec["C-DATA"]["problems"]))

    def test_the_barrier_receipt_must_be_the_bound_jobs_pass(self):
        failed_ref = {u: {"pass": u != "central_df", "srun_rc": 0} for u in iu.REFERENCE_UNITS}
        cases = [({}, {"verdict": "STOP"}), ({}, {"job": "61000002"}), ({}, {"deploy_head": "M1"}),
                 ({}, {"runner_sha256": "0" * 64}), ({}, {"units": failed_ref}),           # r2 item 2: the references
                 ({"rc": 1}, {}), ({"stage": "refs"}, {}), ({"job": "61000002"}, {}), ({"M": "M1"}, {}),
                 ({"completion": {"verdict": "PASS", "barrier_sha256": "0" * 64}}, {}),  # IBUB-DONE binds another barrier
                 ({"completion": {"verdict": "FAIL"}}, {}), None, "no reference marker", "a reference marker from another job"]
        for case in cases:
            td = Path(tempfile.mkdtemp()).resolve()
            self.addCleanup(shutil.rmtree, td, True)
            tr = Tree(td)
            if case is None:
                (tr.units / "refcheck.json").unlink()
            elif case == "no reference marker":
                (tr.units / "central_df.done").unlink()
            elif case == "a reference marker from another job":       # agy read 5: the marker's own binding
                m = json.loads((tr.units / "central.done").read_text())
                (tr.units / "central.done").write_text(json.dumps(dict(m, job="61000002")))
            else:
                tr.write_barrier(done=case[0], **case[1])
            change = case
            with self.subTest(change=change):
                self.patch(tr)
                rec = self.go(tr)
                self.assertEqual(rec["verdict"], "INVALID")
                self.assertFalse(rec["C-BARRIER"]["pass"])
                self.assertNotIn("readings", rec)

    def test_a_marker_from_another_job_or_deploy_is_invalid(self):
        for field, value in (("job", "61000002"), ("deploy_head", "M1")):
            td = Path(tempfile.mkdtemp()).resolve()
            self.addCleanup(shutil.rmtree, td, True)
            tr = Tree(td)
            f = tr.units / f"toy_{T}_{SEEDS[30]}.done"
            f.write_text(json.dumps(dict(json.loads(f.read_text()), **{field: value})))
            with self.subTest(field=field):
                self.patch(tr)
                rec = self.go(tr)
                self.assertEqual(rec["verdict"], "INVALID")
                self.assertTrue(any("marker's job/deploy" in p for p in rec["C-DATA"]["problems"]))

    def test_a_meta_from_another_deploy_is_invalid(self):
        tr = Tree(self.td)
        self.rewrite_meta(tr, 31, meta={"deploy_head": "M1"})
        self.patch(tr)
        rec = self.go(tr)
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertTrue(any("deploy_head" in p for p in rec["C-DATA"]["problems"]))

    def test_an_undeclared_extra_marker_is_invalid(self):
        tr = Tree(self.td)
        (tr.units / f"toy_{T}_9999999.done").write_text("{}")
        self.patch(tr)
        rec = self.go(tr)
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertTrue(any("undeclared unit" in p for p in rec["C-DATA"]["problems"]))

    def test_a_nonfinite_cell_in_a_failed_unit_still_fires_c_cells(self):
        tr = Tree(self.td)
        tr.write_unit(40, SEEDS[40], k5_nan=True, verdict="FAIL")
        self.patch(tr)
        rec = self.go(tr)
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertEqual(rec["C-CELLS"]["nonfinite"]["K5"], 1)
        self.assertFalse(rec["C-CELLS"]["pass"])
        self.assertIn("C-CELLS", rec["controls_failed"])

    def test_a_stop_at_finish_publishes_no_reading_and_no_errors(self):
        tr = Tree(self.td)
        self.patch(tr)
        real = rd.Run.finish

        def stopping(self_, out, name):
            self_.rec["stop"].append("a simulated atime move")
            return real(self_, out, name)
        with mock.patch.object(rd.Run, "finish", stopping):
            rec = self.go(tr)
        self.assertEqual(rec["verdict"], "STOP")
        on_disk = json.loads((tr.d / "out" / f"ibub_{T}.json").read_text())
        self.assertNotIn("readings", on_disk)
        self.assertNotIn("reading", on_disk)
        self.assertFalse((tr.d / "out" / f"ibub_{T}_errors.npz").exists())

    def test_the_truth_file_joins_the_atime_ledger(self):
        tr = Tree(self.td)
        self.patch(tr)
        seen = []
        with mock.patch.object(rd.Run, "watch", lambda self_, path: seen.append(str(path))):
            rec = self.go(tr)
        self.assertEqual(rec["verdict"], "PASS")
        self.assertIn(str(tr.run / tr.pdir / "truth_xsec.npz"), seen)

    def test_an_unexpected_error_uninstalls_the_audit_and_raises(self):
        tr = Tree(self.td)
        self.patch(tr)
        with mock.patch.object(cs, "errors", side_effect=RuntimeError("boom")), self.assertRaises(RuntimeError):
            self.go(tr)
        self.assertTrue(cb.AUDIT is None or cb.AUDIT._undo == [])          # the audit's patches are gone

    def test_a_temporary_root_under_a_guarded_tree_is_refused(self):
        tr = Tree(self.td)
        self.patch(tr)
        (tr.g / "tmp").mkdir()
        with mock.patch.dict(os.environ, {"TMPDIR": str(tr.g / "tmp")}), self.assertRaises(c.Refusal):
            self.go(tr)


class HotellingSingular(unittest.TestCase):
    def test_a_singular_covariance_is_recorded_not_raised(self):
        D = np.random.default_rng(1).normal(size=(50, 4))
        D[:, 3] = D[:, 2]                          # two identical columns: S is exactly singular
        h = ir.hotelling(D)
        self.assertGreater(h["cond_S"], 1e12)                  # printed beside it, as declared; no cutoff applies
        self.assertEqual(h["read_by"], "nothing")
        self.assertNotIn("why", h) if h["T2"] is not None else self.assertIn("singular", h["why"])
        with mock.patch.object(np.linalg, "solve", side_effect=np.linalg.LinAlgError("Singular matrix")):
            h = ir.hotelling(np.random.default_rng(2).normal(size=(50, 4)))
        self.assertIsNone(h["T2"])
        self.assertIn("singular", h["why"])


class AsScripts(unittest.TestCase):
    def test_both_modules_run_as_scripts(self):
        import subprocess
        for f in ("ibub_unit.py", "ibub_readout.py"):
            r = subprocess.run([sys.executable, "-B", str(HERE / f), "--help"], capture_output=True, text=True)
            with self.subTest(script=f):
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertIn("usage:", r.stdout)


if __name__ == "__main__":
    unittest.main()
