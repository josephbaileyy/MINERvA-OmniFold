"""cov2d_readout (COV2D-ADDENDUM-A4.md): both phases end to end on a synthetic two-truth tree, and every guard in both
directions: phase N opens no toy product and records the inventory; phase S refuses, before any toy product, an absent
or other null record, another M, truth or verdict, a blocks file off its digest, and a changed inventory; section 9.9
(implemented here, not glue) refuses each wrong field and passes a correct product; the toys' code must be the null
record's (A4-1); each product names its truth, role and seed (A4-2); the identity windows at their edges.
Stubbed, as test_cov2d_blocks.Control95Main stubs them: the MAT environment, part B's arithmetic (Cells, x01,
flux_weights, partb_sums, c_model, noatime_inputs) and the null's 2,000,000 draws (n_mc=4,000 here). PyROOT is needed
(the open audit wraps TFile.Open; read_provenance's own test writes a real ROOT file).
    cd 2d-unfolding/cov2d/tests && python -B -m unittest -v test_cov2d_readout
"""
from __future__ import annotations

import collections
import functools
import hashlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import cov2d as c  # noqa: E402

try:
    import ROOT  # noqa: F401
    import cov2d_readout as rd  # noqa: E402
    import cov2d_blocks as cb  # noqa: E402
    import cov2d_null as cn  # noqa: E402
    HAVE = True
except Exception:  # pragma: no cover
    HAVE = False

N, NX, NY = 205, 14, 16
TRUTHS = ("G18", "AR23")
DRIVER = "/deploy/2d-unfolding/re2/re2_driver.py"
CODE = {"driverSha256": "d" * 64, "omnifoldHelperSha256": "h" * 64}
COMMON = "--mcfile $MC --iters 5 --use-weights --estimator lgbm --seed 42"
TAIL = "--bkg-mode negweight-refined --refine-n-estimators 400 --refine-num-leaves 31"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def rep_mask() -> np.ndarray:
    r = np.random.default_rng(1)
    rep = np.zeros(NX * NY, bool)
    keep = set(r.choice([i for i in range(NX * NY) if i != c.OUTLIER_CELL], N - 1, replace=False).tolist())
    rep[sorted(keep | {c.OUTLIER_CELL})] = True
    return rep


def args_of(label: str, truth: str) -> str:
    role, rest = label[0], label.split("_", 2)[2] if label.count("_") >= 2 else ""
    data = f"--data-file $D/data_{c.REALIZATION_SEED[truth]}.root"
    if role == "U":
        b, i = rest.rsplit("_", 1)
        return (f"--omnifile $UNI --flux-universe-file $FLUXU --verbose {COMMON} --universe {b}:{i} "
                f"--branch-select derived {TAIL} {data}")
    if role == "L":
        b, i = rest.rsplit("_", 1)
        return (f"--omnifile $ACT/runEventLoopOmniFold_5D_MEFHC_active_{b}_{i}.root {COMMON} --branch-select all {TAIL} "
                f"{data}")
    if role == "B":
        return f"--omnifile $CV {COMMON} --bootstrap-seed {int(rest)} --bootstrap-streams three {TAIL} {data}"
    if role == "T":
        return f"--omnifile $CV {COMMON} --branch-select all {TAIL} --data-file $D/data_{int(rest)}.root"
    return f"--omnifile $CV {COMMON} --branch-select all {TAIL} {data}"


def labels_of(truth: str) -> list:
    out = [f"X_{truth}"]
    out += [f"U_{truth}_{b}_{i}" for b in c.ORDER for i in range(c.BANDS[b])]
    out += [f"L_{truth}_{b}_{i}" for b in c.LATERAL_BANDS for i in (0, 1)]
    out += [f"B_{truth}_{n:03d}" for n in range(1, 301)]
    out += [f"T_{truth}_{s}" for s in c.TOY_SEEDS[truth]]
    return out


G18C = ["L_G18_BeamAngleX_0", "X_G18", "B_G18_001", "U_G18_Flux_0", "T_G18_5720000"]


class Tree:
    """A synthetic run directory, records directory and origin/main for both truths."""
    def __init__(self, d: Path):
        self.d, self.g = d, d / "guarded"
        self.run = self.g / "run"
        self.rec = d / "rec"
        self.rep = rep_mask()
        self.flat = [int(i) for i in np.flatnonzero(self.rep)]
        r = np.random.default_rng(7)
        self.vec, self.prov, self.comp_rows, self.runs_sha = {}, {}, [], {}
        self.env_text = (f"A={self.g}/shared\nSTAGE={self.g}/stage\nexport CV=$STAGE/cv.root ACT=$STAGE/laterals\n"
                         f"export UNI=$A/uni.root\nexport MC=$A/mc.root\nexport FLUXU=$A/fluxu.root\n"
                         f"O=${{COV2D_O:-{self.run}}}\n")
        (d / "env.sh").write_text(self.env_text)
        self.env = rd.job_env(self.env_text, str(self.run))
        self.data_sha = {}
        self.natures, self.x_true = {}, {}
        for t in TRUTHS:
            self.build_truth(t, r)
        self.write_runs()
        comp = "\t".join(["truth", "label", "plan_job", "job", "job_id", "sacct", "lane", "walls_rc0", "walls_other",
                          "digests", "sha256", "disk", "basis", "verdict"]) + "\n"
        comp += "".join("\t".join(row) + "\n" for row in self.comp_rows)
        (d / "completeness.tsv").write_text(comp)
        self.comp = (d / "completeness.tsv", sha(comp.encode()))
        self.ns = self.g / "ns"
        (self.ns / "out" / "ER").mkdir(parents=True)
        (self.ns / "out" / "ER" / "xsec.root").write_bytes(b"ER")
        self.vec["ER"] = self.x_R
        c08 = self.d / "c08.npz"
        A_ = r.standard_normal((N, 4))
        np.savez(c08, c08=A_ @ A_.T * 1e-4)
        self.c08 = (str(c08), sha(c08.read_bytes()))
        S = r.standard_normal((3, N)) * 0.02
        self.C_model = sum(np.outer(s, s) for s in S)
        self.C_minus = sum(np.outer(s, s) for s in S[1:])
        ratio = np.ones(N)
        ratio[:5] = 0.8
        c2 = {"efficiency": {"cells205": self.flat},
              "b": {t: {"variance_ratio": {"option_1_clipped": ratio.tolist()}} for t in TRUTHS}}
        (self.rec / "c2.json").write_text(json.dumps(c2))
        self.c2 = (self.rec / "c2.json", sha((self.rec / "c2.json").read_bytes()))
        self.pins = {}
        for k in rd.ROLLUP_PINS:
            p = self.g / "pins" / k
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(k.encode())
            self.pins[k] = (str(p), sha(k.encode()))
        (self.g / "bf").mkdir()
        import cov2d_blocks as cb_
        for pl in cb_.rollup().BR.PLAYLISTS:
            for kind in ("MC", "Data"):
                (self.g / "bf" / f"runEventLoop{kind}_{pl}.root").write_bytes(f"{kind}{pl}".encode())
        self.origin = {}

    def build_truth(self, t: str, r):
        x_R = getattr(self, "x_R", None)
        if x_R is None:
            self.x_R = x_R = r.uniform(1.0, 2.0, N)
        x_T = x_R * r.uniform(0.8, 1.2, N)
        pdir = self.run / rd.pseudo_dir(t)
        (pdir / "a").mkdir(parents=True)
        (pdir / "b").mkdir(parents=True)
        files = []
        for s in list(c.TOY_SEEDS[t]) + [c.REALIZATION_SEED[t]]:
            b = f"data {t} {s}".encode()
            files.append({"seed": s, "role": "toy" if s != c.REALIZATION_SEED[t] else "realization", "sha256": sha(b)})
            self.data_sha[(t, s)] = sha(b)
        (self.rec / "pseudo" / t).mkdir(parents=True)
        (self.rec / "pseudo" / t / "pseudo_b.json").write_text(json.dumps({"files": files}))
        natures = [{"role": "toy", "seed": s, "universes": [], "lateral_signs": [int(x) for x in r.choice([-1, 1], 5)],
                    "norm_z": float(r.standard_normal())} for s in c.TOY_SEEDS[t]]
        natures.append({"role": "realization", "seed": c.REALIZATION_SEED[t], "universes": [], "lateral_signs": [],
                        "norm_z": None})
        full = np.zeros((len(natures), NX * NY))
        full[:, self.rep] = x_T * r.uniform(0.95, 1.05, (len(natures), N))
        self.x_true[t] = full[:, self.rep]
        np.savez(pdir / "b" / "truth_xsec.npz", xsec=full.reshape(len(natures), NX, NY),
                 seeds=np.array([n["seed"] for n in natures]))
        m_all = np.abs(r.standard_normal((len(natures), NX * NY))) * 1e-3
        pa = {"natures": natures, "toys": [{"seed": n["seed"], "role": n["role"],
                                            "truth_lambda": {"sum_lambda_neg": -float(m_all[k].sum()) * 2.0}}
                                           for k, n in enumerate(natures)]}
        (pdir / "a" / "pseudo_a.json").write_text(json.dumps(pa))
        (self.rec / "pseudo" / t / "pseudo_a.json").write_text(json.dumps(pa))
        pos = np.abs(r.uniform(1, 2, (len(natures), NX * NY)))
        np.savez(pdir / "a" / "cells.npz", S=pos, m_seen=pos * 1e-3, N=pos, m_all=m_all,
                 neg_reco_background=-pos * 1e-4, S_reco=pos, seeds=np.array([n["seed"] for n in natures]))
        self.natures[t] = natures
        lo, hi = (rd.epoch_pst(x) for x in rd.JOB_WINDOW[t])
        for f in ("a/cells.npz", "a/pseudo_a.json", "b/truth_xsec.npz"):
            os.utime(pdir / f, (lo + 60, lo + 60))
        for lab in labels_of(t):
            job = f"{t}_C" if lab in G18C and t == "G18" else f"{t}_x"
            b = lab.encode()
            path = self.run / "out" / lab / "xsec.root"
            path.parent.mkdir(parents=True)
            path.write_bytes(b)
            self.comp_rows.append([t, lab, f"{t}_x", job, "1", "COMPLETED 0:0", "1", "1", "0", "1", sha(b), "match",
                                   "basis", "PASS"])
            role = lab[0]
            if role == "X":
                v = x_T
            elif role == "T":
                k = list(c.TOY_SEEDS[t]).index(int(lab.rsplit("_", 1)[1]))
                v = self.x_true[t][k] + 0.002 * r.standard_normal(N)
            else:
                v = x_T + (0.03 if role == "B" else 0.05) * r.standard_normal(N)
            self.vec[lab] = v
            self.prov[lab] = self.good_prov(lab, t)
        self.x_T = getattr(self, "x_T", {})
        self.x_T[t] = x_T

    def table_truth(self, lab: str, t: str) -> str:
        return "G18C" if t == "G18" and lab in G18C else t

    def good_prov(self, lab: str, t: str) -> dict:
        out = f"{self.run}/out/{lab}/xsec.root"
        args = args_of(lab, t)
        env = dict(self.env, D=f"{self.run}/{rd.pseudo_dir(self.table_truth(lab, t))}/b")
        argv = [DRIVER] + rd.expected_argv(args, env, out)
        role, rest = lab[0], (lab.split("_", 2)[2] if lab.count("_") >= 2 else "")
        cfg = {"out": out, "seed": 42, "universe": None, "bootstrap_seed": None,
               "omnifile": env["CV"], "data_file": f"{env['D']}/data_{c.REALIZATION_SEED[t]}.root"}
        seed = c.REALIZATION_SEED[t]
        if role == "U":
            b, i = rest.rsplit("_", 1)
            cfg.update(universe=f"{b}:{i}", omnifile=env["UNI"])
        elif role == "L":
            b, i = rest.rsplit("_", 1)
            cfg["omnifile"] = f"{env['ACT']}/runEventLoopOmniFold_5D_MEFHC_active_{b}_{i}.root"
        elif role == "B":
            cfg["bootstrap_seed"] = int(rest)
        elif role == "T":
            seed = int(rest)
            cfg["data_file"] = f"{env['D']}/data_{seed}.root"
        return {"runConfig": json.dumps(cfg), "runArgv": json.dumps(argv), **CODE,
                "dataFileSha256": self.data_sha[(t, seed)]}

    def write_runs(self):
        tabs = {"G18": [], "AR23": [], "G18C": []}
        for row in self.comp_rows:
            t, lab = row[0], row[1]
            tt = self.table_truth(lab, t)
            tabs[tt].append(f"{tt}_job\t{tt}_job.1\t{lab}\t64\tre2\t{args_of(lab, t)}\t100")
            if tt == "G18C":
                tabs["G18"].append(f"G18_job\tG18_job.1\t{lab}\t64\tre2\t{args_of(lab, t)}\t100")
        (self.run / "tables").mkdir(parents=True)
        for tt, rows in tabs.items():
            text = "job\tlane\tlabel\tcpus\tscript\targs\test_s\n" + "".join(x + "\n" for x in rows)
            (self.run / "tables" / f"runs_{tt}.tsv").write_text(text)
            self.runs_sha[tt] = sha(text.encode())


@unittest.skipUnless(HAVE, "needs PyROOT (the open audit wraps TFile.Open)")
class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        cls.tree = Tree(Path(cls.td.name).resolve())

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def setUp(self):
        T = self.tree
        self.out = Path(tempfile.mkdtemp(dir=T.d))
        (self.out / "tmp").mkdir()
        tree = T

        class FakeCells:
            def __init__(self, er):
                self.rep, self.x = tree.rep, tree.x_R

            def vec(self, path):
                return tree.vec[Path(path).read_bytes().decode()]
        ro = cb.rollup()
        self.opened_products = []
        patches = [
            (cb, "AUDIT", None), (cb.OpenAudit.__init__, "__defaults__", ((str(T.g),),)),
            (cb, "pinned_mat_environment", lambda: {"stub": "MAT"}),
            (cb, "c_model", lambda: (T.C_model, T.C_minus, {"cells": T.flat})),
            (cb, "C08_R_FILE", T.c08), (ro, "BF", str(T.g / "bf")),
            (ro, "NS_R", str(T.ns)), (ro, "partb_sums", lambda: {"ER/xsec.root": sha(b"ER")}),
            (ro, "Cells", FakeCells), (ro, "flux_weights", lambda: (np.linspace(0.5, 1.5, 100), np.ones(3))),
            (ro, "x01", lambda cells, paths, phi, tag: np.stack([tree.vec[Path(p).read_bytes().decode()] for p in paths])),
            (ro, "CHECKS", collections.OrderedDict()),
            (rd, "COMPLETENESS", T.comp), (rd, "C2_RECORD", T.c2), (rd, "REC", T.rec), (rd, "RUNS_SHA", T.runs_sha),
            (rd, "ENV_FILE", T.d / "env.sh"),
            (rd, "PSEUDO_A_SHA", {t: sha((T.rec / "pseudo" / t / "pseudo_a.json").read_bytes()) for t in TRUTHS}),
            (rd, "G18_CELLS", {"size": (T.run / "pseudo/G18/a/cells.npz").stat().st_size,
                               "minute": rd.datetime.fromtimestamp(rd.epoch_pst(rd.JOB_WINDOW["G18"][0]) + 60,
                                                                   rd.PST).strftime("%Y-%m-%dT%H:%M")}),
            (rd, "read_provenance", lambda p: tree.prov[Path(p).read_bytes().decode()]),
            (rd, "git_show", lambda ref_path: tree.origin.get(ref_path.split(":", 1)[1])),
            (cn, "null_at_T", functools.partial(cn.null_at_T, n_mc=4_000)),
            (c, "deploy_head", lambda root: "M0"),
        ]
        if not getattr(os, "O_NOATIME", 0):      # macOS: no O_NOATIME, so reads move atime; the atime test covers it
            patches.append((rd.Run, "watch", lambda self_, path: None))
        p = mock.patch.object(os, "O_NOATIME", getattr(os, "O_NOATIME", 0), create=True)   # macOS has none
        p.start()
        self.addCleanup(p.stop)
        for target, attr, value in patches:
            p = mock.patch.object(target, attr, value)
            p.start()
            self.addCleanup(p.stop)
        p = mock.patch.dict(ro.PIN, T.pins)
        p.start()
        self.addCleanup(p.stop)
        p = mock.patch.dict(os.environ, {"TMPDIR": str(self.out / "tmp")})
        p.start()
        self.addCleanup(p.stop)
        self.addCleanup(lambda: cb.AUDIT is not None and cb.AUDIT.uninstall())

    def null(self, t="G18"):
        """One phase N; noatime_inputs repoints the rollup's globals at its private copies (one truth per process in a
        real run), so each call here starts from the fixture's own."""
        ro = cb.rollup()
        with mock.patch.object(ro, "BF", str(self.tree.g / "bf")), mock.patch.dict(ro.PIN, self.tree.pins):
            return rd.phase_null(t, self.out, str(self.tree.run))

    def commit(self, t="G18", rec_bytes=None, npz_bytes=None):
        nb = rec_bytes if rec_bytes is not None else (self.out / f"null_{t}.json").read_bytes()
        zb = npz_bytes if npz_bytes is not None else (self.out / f"blocks_{t}.npz").read_bytes()
        self.tree.origin[f"{rd.READOUT_REL}/{t}/null_{t}.json"] = nb
        self.tree.origin[f"{rd.READOUT_REL}/{t}/blocks_{t}.npz"] = zb
        self.addCleanup(self.tree.origin.clear)
        return sha(nb)


class PhaseN(Base):
    def test_null_passes_at_both_truths_and_opens_no_toy(self):
        for t in TRUTHS:
            rec = self.null(t)
            self.assertEqual((rec["verdict"], rec["stop"], rec["controls_failed"]), ("PASS", [], []), t)
            self.assertEqual(rec["toy_paths_opened"], 0)
            self.assertEqual(rec["products_read"], 1 + 175 + 10 + 300)
            self.assertEqual(rec["code"], CODE)
            self.assertEqual(len(rec["inventory"]["toys"]), 300)
            self.assertEqual(rec["M"], "M0")
            self.assertEqual(rec["blocks_npz_sha256"], sha((self.out / f"blocks_{t}.npz").read_bytes()))
            self.assertLessEqual(rec["null"]["match_rel"], 1e-12)
            ro = cb.rollup()       # the real noatime_inputs: every pinned rollup input and 2 x playlists flux/POT copies
            self.assertEqual({k: rec["inputs"][k] for k in rd.ROLLUP_PINS}, {k: v[1] for k, v in self.tree.pins.items()})
            self.assertEqual(len([k for k in rec["inputs"] if k.startswith(str(self.tree.g / "bf"))]),
                             2 * len(ro.BR.PLAYLISTS))

    def peek(self, how):
        T = self.tree
        orig = cb.rollup().x01

        def peeking(cells, paths, phi, tag):
            toy = T.run / "out" / "T_G18_5720000" / "xsec.root"
            if how == "plain":
                open(toy, "rb").close()
            else:
                cb.read_noatime(toy)         # a sanctioned O_NOATIME read: only phase N's own log check can catch it
            return orig(cells, paths, phi, tag)
        return mock.patch.object(cb.rollup(), "x01", peeking)

    def test_a_plain_toy_open_in_phase_n_is_refused_by_the_audit(self):
        with self.peek("plain"), self.assertRaises(c.Refusal):
            self.null("G18")
        self.assertTrue([p for _, p, _ in cb.AUDIT.log if "/out/T_G18_" in p])

    def test_a_noatime_toy_read_in_phase_n_stops(self):           # A4-3: the rule is "phase N opens no toy path"
        with self.peek("noatime"):
            rec = self.null("G18")
        self.assertEqual(rec["verdict"], "STOP")
        self.assertEqual(rec["toy_paths_opened"], 1)
        self.assertTrue(any("opened 1 toy paths" in x for x in rec["stop"]))

    def test_a_product_off_its_digest_refuses(self):
        p = self.tree.run / "out" / "B_AR23_007" / "xsec.root"
        old = p.read_bytes()
        p.write_bytes(b"tampered")
        self.addCleanup(p.write_bytes, old)
        with self.assertRaisesRegex(c.Refusal, "B_AR23_007"):
            self.null("AR23")

    def test_completeness_off_its_pin_refuses(self):
        with mock.patch.object(rd, "COMPLETENESS", (self.tree.comp[0], "0" * 64)):
            with self.assertRaises(c.Refusal):
                self.null("G18")

    def test_an_inventory_file_outside_its_job_window_stops(self):
        p = self.tree.run / "pseudo/AR23-a2/b/truth_xsec.npz"
        st = p.stat()
        hi = rd.epoch_pst(rd.JOB_WINDOW["AR23"][1])
        os.utime(p, (hi + 5, hi + 5))
        self.addCleanup(os.utime, p, ns=(st.st_atime_ns, st.st_mtime_ns))
        rec = self.null("AR23")
        self.assertEqual(rec["verdict"], "STOP")
        self.assertTrue(any("truth_xsec_npz: mtime" in x for x in rec["identity"]["problems"]))

    def test_non_toy_code_differs_is_invalid(self):
        lab = "U_G18_Flux_3"
        good = self.tree.prov[lab]
        self.tree.prov[lab] = dict(good, driverSha256="e" * 64)
        self.addCleanup(self.tree.prov.__setitem__, lab, good)
        rec = self.null("G18")
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertTrue(any("driverSha256" in x for x in rec["section_9_9"]["problems"]))


class PhaseS(Base):
    def setUp(self):
        super().setUp()
        self.nrec = self.null("G18")
        cb.AUDIT = None

    def score(self, digest=None, t="G18"):
        return rd.main(["score", "--truth", t, "--null-digest", digest or self.commit(t), "--out", str(self.out),
                        "--run-dir", str(self.tree.run)])

    def refused(self):
        return json.loads((self.out / "score_G18.refused.json").read_text())["refused"]

    def test_score_completes_after_the_gate(self):
        self.assertEqual(self.score(), 0)
        rec = json.loads((self.out / "score_G18.json").read_text())
        self.assertIn(rec["verdict"], ("COVERS", "UNDER-COVERS"))
        self.assertEqual(rec["section_9_9"]["problems"], [])
        self.assertEqual(set(rec["readouts"]), {"spread_alone", "bias", "predicted_offset", "leave_out_mec",
                                                "realization_check", "clipping_residual"})
        self.assertEqual(rec["truth_lambda_inequality"]["holds_in"], 300)
        self.assertEqual(len(rec["grade"]["weakened_pass"]) + sum(1 for x in rec["grade"]["flagged_cells"]
                                                                   if x in self.tree.flat[:5]), 5)

    def assert_refused_before_toys(self, digest, pattern):
        self.assertEqual(self.score(digest), 2)
        self.assertRegex(self.refused(), pattern)
        self.assertFalse([p for _, p, _ in cb.AUDIT.log if "/out/T_G18_" in p])     # no toy product opened
        self.assertFalse((self.out / "score_G18.json").exists())

    def test_absent_record_refuses(self):
        self.tree.origin.clear()
        self.assert_refused_before_toys("0" * 64, "holds no null_G18.json")

    def test_wrong_digest_refuses(self):
        self.commit()
        self.assert_refused_before_toys("1" * 64, "not 1111")

    def edited(self, **kv):
        rec = json.loads((self.out / "null_G18.json").read_text())
        rec.update(kv)
        return self.commit(rec_bytes=json.dumps(rec).encode())

    def test_another_m_refuses(self):
        self.assert_refused_before_toys(self.edited(M="M1"), "not this deploy's HEAD")

    def test_another_truth_refuses(self):
        self.assert_refused_before_toys(self.edited(truth="AR23"), "AR23's, not G18's")

    def test_a_stop_verdict_refuses(self):
        self.assert_refused_before_toys(self.edited(verdict="STOP"), "verdict is STOP")

    def test_blocks_off_the_record_refuses(self):
        d = self.commit(npz_bytes=b"not the blocks")
        self.assert_refused_before_toys(d, "blocks npz")

    def test_a_changed_inventory_file_refuses(self):
        p = self.tree.run / "pseudo/G18/a/cells.npz"
        old, st = p.read_bytes(), p.stat()
        p.write_bytes(old + b"x")
        os.utime(p, ns=(st.st_atime_ns, st.st_mtime_ns))
        self.addCleanup(lambda: (p.write_bytes(old), os.utime(p, ns=(st.st_atime_ns, st.st_mtime_ns))))
        self.assert_refused_before_toys(self.commit(), "inventory: cells_npz")

    def test_a_changed_toy_stat_refuses(self):
        p = self.tree.run / "out/T_G18_5720011/xsec.root"
        st = p.stat()
        os.utime(p, ns=(st.st_atime_ns, st.st_mtime_ns + 10**9))
        self.addCleanup(os.utime, p, ns=(st.st_atime_ns, st.st_mtime_ns))
        self.assert_refused_before_toys(self.commit(), "T_G18_5720011's stat")

    def toy_field(self, lab, **kv):
        good = self.tree.prov[lab]
        cfg = json.loads(good["runConfig"])
        if "cfg" in kv:
            cfg.update(kv.pop("cfg"))
        self.tree.prov[lab] = dict(good, runConfig=json.dumps(cfg), **kv)
        self.addCleanup(self.tree.prov.__setitem__, lab, good)

    def assert_invalid(self, word):
        self.assertEqual(self.score(), 3)
        rec = json.loads((self.out / "score_G18.json").read_text())
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertNotIn("grade", rec)                    # refused before any toy error is used
        self.assertTrue(any(word in x for x in rec["section_9_9"]["problems"]), rec["section_9_9"]["problems"])

    def test_a_toy_with_another_driver_is_invalid(self):          # A4-1
        self.toy_field("T_G18_5720100", driverSha256="e" * 64)
        self.assert_invalid("driverSha256")

    def test_a_toy_with_another_helper_is_invalid(self):          # A4-1
        self.toy_field("T_G18_5720100", omnifoldHelperSha256="e" * 64)
        self.assert_invalid("omnifoldHelperSha256")

    def test_a_toy_with_another_data_file_digest_is_invalid(self):
        self.toy_field("T_G18_5720200", dataFileSha256="0" * 64)
        self.assert_invalid("dataFileSha256")

    def test_a_toy_with_another_argv_is_invalid(self):
        good = json.loads(self.tree.prov["T_G18_5720201"]["runArgv"])
        self.toy_field("T_G18_5720201", runArgv=json.dumps(good + ["--extra"]))
        self.assert_invalid("runArgv")

    def test_a_toy_with_another_seed_is_invalid(self):
        self.toy_field("T_G18_5720202", cfg={"seed": 7})
        self.assert_invalid("seed 7")

    def test_a_toy_naming_another_truth_is_invalid(self):          # A4-2
        self.toy_field("T_G18_5720203", cfg={"out": f"{self.tree.run}/out/T_AR23_5730203/xsec.root"})
        self.assert_invalid("T_G18_5720203: runConfig out")

    def test_a_toy_naming_another_toys_data_is_invalid(self):      # A4-2: its seed is not its label's
        self.toy_field("T_G18_5720204", cfg={"data_file": f"{self.tree.run}/pseudo/G18/b/data_5720205.root"})
        self.assert_invalid("not its toy's")

    def test_truth_rows_out_of_natures_order_refuse(self):
        p = self.tree.run / "pseudo/G18/b/truth_xsec.npz"
        old, st = p.read_bytes(), p.stat()
        z = np.load(io.BytesIO(old))
        seeds = np.array(z["seeds"])
        seeds[[0, 1]] = seeds[[1, 0]]
        np.savez(p, xsec=z["xsec"], seeds=seeds)
        os.utime(p, ns=(st.st_atime_ns, st.st_mtime_ns))
        self.addCleanup(lambda: (p.write_bytes(old), os.utime(p, ns=(st.st_atime_ns, st.st_mtime_ns))))
        self.null("G18")        # a fresh null record over the changed file, so the gate passes
        cb.AUDIT = None
        self.assertEqual(self.score(), 2)
        self.assertRegex(self.refused(), "not pseudo_a's natures in order")

    def test_toy_seeds_not_declared_refuse(self):
        pa = self.tree.rec / "pseudo/G18/pseudo_a.json"
        rec = json.loads(pa.read_text())
        rec["natures"][0]["seed"] = 1
        with mock.patch.object(rd, "PSEUDO_A_SHA", {"G18": sha(json.dumps(rec).encode()), "AR23": ""}):
            old = pa.read_text()
            pa.write_text(json.dumps(rec))
            self.addCleanup(pa.write_text, old)
            self.assertEqual(self.score(), 2)
        self.assertRegex(self.refused(), "not the declared seeds")


@unittest.skipUnless(HAVE, "needs PyROOT")
class CholeskyTolPure(unittest.TestCase):
    """Addendum A5's tolerance, max(1e-9, 10 kappa_2(C_T) eps), from C_T alone."""
    def test_the_formula(self):
        eps = np.finfo(np.float64).eps
        Q, _ = np.linalg.qr(np.random.default_rng(3).normal(size=(6, 6)))
        lam = np.array([1.0, 0.5, 1e-3, 1e-6, 1e-9, 1.5e-12])
        t = rd.cholesky_tol((Q * lam) @ Q.T)
        self.assertAlmostEqual(t["kappa2"] / (1 / 1.5e-12), 1, places=3)
        self.assertEqual(t["eps"], eps)
        self.assertEqual(t["tol"], 10 * t["kappa2"] * eps)
        self.assertGreater(t["tol"], 1e-4)
        self.assertEqual(t["rule"], "max(1e-9, 10 kappa_2(C_T) eps)")

    def test_the_floor_is_1b_s_1e_9(self):
        t = rd.cholesky_tol(np.eye(5))
        self.assertEqual(t["kappa2"], 1.0)
        self.assertEqual(t["tol"], 1e-9)


class CholeskyA5(Base):
    """Addendum A5 in phase S: each grade's tolerance (C_T's, and C_T-'s for the leave-out-MEC readout) from its matrix
    before any toy is read, passed to 1B's grade and recorded; a refusal from either grade writes score_<T>.invalid.json
    through Run.finish and prints a distinct INVALID line naming the grade, exit 3."""
    def setUp(self):
        super().setUp()
        self.nrec = self.null("G18")
        cb.AUDIT = None

    def score(self, digest=None, t="G18"):
        return rd.main(["score", "--truth", t, "--null-digest", digest or self.commit(t), "--out", str(self.out),
                        "--run-dir", str(self.tree.run)])

    def committed(self, key):
        return np.load(self.out / "blocks_G18.npz")[key]

    def test_kappa_1e12_in_both_C_T_and_C_T_minus_grades_under_a5(self):
        """Both matrices full rank at kappa ~ 1e12 (the null record re-pinned to the new blocks): each grade's correct
        Cholesky differs from the non-null chi2 by more than 1B's 1e-9 and passes A5's tolerance."""
        z = dict(np.load(self.out / "blocks_G18.npz"))
        for key, seed in (("C_T", 21), ("C_T_minus", 22)):
            Q, _ = np.linalg.qr(np.random.default_rng(seed).normal(size=(205, 205)))
            top = np.linalg.eigvalsh(z[key])[-1]
            C = (Q * (top * np.logspace(0, np.log10(1.5e-12), 205))) @ Q.T
            z[key] = (C + C.T) / 2
        buf = io.BytesIO()
        np.savez(buf, **z)
        zb = buf.getvalue()
        rec = json.loads((self.out / "null_G18.json").read_text())
        rec["blocks_npz_sha256"] = sha(zb)
        self.assertEqual(self.score(self.commit("G18", json.dumps(rec).encode(), zb)), 0)
        out = json.loads((self.out / "score_G18.json").read_text())
        for field in ("cholesky_check", "cholesky_check_minus"):
            chk = out[field]
            self.assertGreater(chk["kappa2"], 1e11, field)
            self.assertEqual(chk["compared"]["ndf"], 205, field)
            self.assertGreater(chk["compared"]["max_rel_diff"], 1e-9, field)    # 1B's default would refuse
            self.assertLessEqual(chk["compared"]["max_rel_diff"], chk["tol"], field)

    def test_each_tolerance_is_recorded_from_its_matrix_before_any_toy_and_passed_to_its_grade(self):
        import fd_1b_mc as mc
        real_tol, real_grade, seen, calls = rd.cholesky_tol, mc.grade, [], []

        def tol(C):
            seen.append([p for _, p, _ in cb.AUDIT.log if "/out/T_G18_" in p])
            return real_tol(C)

        def grade(E, C, null, **kw):
            calls.append((C, kw))
            return real_grade(E, C, null, **kw)
        with mock.patch.object(rd, "cholesky_tol", tol), mock.patch.object(mc, "grade", grade):
            self.assertEqual(self.score(), 0)
        rec = json.loads((self.out / "score_G18.json").read_text())
        self.assertEqual(seen, [[], []])                                   # both computed before any toy was opened
        for key, field, i in (("C_T", "cholesky_check", 0), ("C_T_minus", "cholesky_check_minus", 1)):
            want = real_tol(self.committed(key))
            self.assertEqual({k: rec[field][k] for k in want}, want, key)
            np.testing.assert_array_equal(calls[i][0], self.committed(key))
            self.assertEqual(calls[i][1]["chol_tol"], want["tol"], key)
            self.assertEqual(rec[field]["compared"]["tol"], want["tol"], key)
        self.assertEqual(len(calls), 2)
        self.assertEqual(rec["cholesky_check"]["compared"]["ndf"], rec["grade"]["ndf"])
        self.assertEqual(rec["cholesky_check_minus"]["compared"]["ndf"], rec["readouts"]["leave_out_mec"]["grade"]["ndf"])

    def refuse_at(self, key):
        import contextlib
        import fd_1b_mc as mc
        real_grade, target = mc.grade, self.committed(key)

        def grade(E, C, null, **kw):
            if np.array_equal(C, target):
                e = mc.Refusal("the non-null chi2 and the Cholesky chi2 differ")
                e.compared = {"ndf": 205, "max_rel_diff": 0.5, "tol": kw["chol_tol"]}
                raise e
            return real_grade(E, C, null, **kw)
        buf = io.StringIO()
        with mock.patch.object(mc, "grade", grade), contextlib.redirect_stdout(buf):
            self.assertEqual(self.score(), 3)
        self.assertIn(f"COV2D-SCORE G18 INVALID (grade refused, {key}: the non-null chi2 and the Cholesky chi2 differ)",
                      buf.getvalue())
        self.assertFalse((self.out / "score_G18.json").exists())
        rec = json.loads((self.out / "score_G18.invalid.json").read_text())
        self.assertEqual(rec["verdict"], "INVALID")
        self.assertEqual(rec["grade_refusal"]["grade"], key)
        self.assertEqual(rec["grade_refusal"]["text"], "the non-null chi2 and the Cholesky chi2 differ")
        self.assertEqual(rec["grade_refusal"]["compared"]["max_rel_diff"], 0.5)
        field = "cholesky_check" if key == "C_T" else "cholesky_check_minus"
        self.assertEqual(rec[field]["compared"]["max_rel_diff"], 0.5)
        self.assertIn(f"grade refused ({key}): the non-null chi2 and the Cholesky chi2 differ", rec["controls_failed"])
        self.assertNotIn("grade", rec)
        self.assertNotIn("readouts", rec)
        for k in ("atime_checked", "atime_moved", "open_audit", "modules"):    # Run.finish ran
            self.assertIn(k, rec)
        self.assertEqual(cb.AUDIT._undo, [])                                       # the open audit is uninstalled

    def raise_in_the_grade(self, exc):
        import fd_1b_mc as mc

        def grade(E, C, null, **kw):
            raise exc
        return mock.patch.object(mc, "grade", grade)

    def test_a_cov2d_refusal_inside_the_try_stays_a_refusal_not_a_grade_refusal(self):     # auditor A5-C1 (V12)
        with self.raise_in_the_grade(c.Refusal("another refusal, not 1B's grade")):
            self.assertEqual(self.score(), 2)
        refused = json.loads((self.out / "score_G18.refused.json").read_text())["refused"]
        self.assertEqual(refused, "another refusal, not 1B's grade")
        self.assertFalse((self.out / "score_G18.invalid.json").exists())
        self.assertFalse((self.out / "score_G18.json").exists())

    def test_any_other_failure_inside_the_try_propagates_unrecorded(self):                  # auditor A5-C1 (V11)
        with self.raise_in_the_grade(ZeroDivisionError("not a refusal")):
            with self.assertRaises(ZeroDivisionError):
                self.score()
        self.assertFalse((self.out / "score_G18.invalid.json").exists())
        self.assertFalse((self.out / "score_G18.json").exists())

    def test_a_refusal_of_the_C_T_grade_writes_the_invalid_record_and_finishes_run(self):
        self.refuse_at("C_T")

    def test_a_refusal_of_the_C_T_minus_grade_writes_the_invalid_record_and_finishes_run(self):
        self.refuse_at("C_T_minus")


@unittest.skipUnless(HAVE, "needs PyROOT")
class Pure(unittest.TestCase):
    """The section 9.9 compares and the identity windows on their own."""
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.tree = Tree(Path(self.td.name).resolve())

    def check(self, lab, prov, t="G18", code=None):
        T = self.tree
        tt = T.table_truth(lab, t)
        row = (tt, "j", args_of(lab, t))
        seed = int(lab.rsplit("_", 1)[1]) if lab[0] == "T" else c.REALIZATION_SEED[t]
        return rd.section_9_9(lab, prov, t, row, T.env, str(T.run), T.data_sha[(t, seed)], code)

    def test_every_correct_product_passes(self):
        for lab in ["X_G18", "U_G18_Flux_0", "U_G18_2p2h_1", "L_G18_Muon_Energy_MINOS_1", "B_G18_300", "T_G18_5720299",
                    "X_AR23", "B_AR23_001"]:
            t = lab.split("_")[1]
            self.assertEqual(self.check(lab, self.tree.prov[lab], t, CODE), [], lab)

    def bad(self, lab, cfg=None, **kv):
        p = dict(self.tree.prov[lab], **kv)
        if cfg:
            c_ = json.loads(p["runConfig"])
            c_.update(cfg)
            p["runConfig"] = json.dumps(c_)
        return self.check(lab, p, code=CODE)

    def test_each_wrong_field_refuses(self):
        self.assertTrue(self.bad("U_G18_Flux_0", driverSha256="x"))
        self.assertTrue(self.bad("U_G18_Flux_0", omnifoldHelperSha256="x"))
        self.assertTrue(self.bad("U_G18_Flux_0", dataFileSha256="x"))
        self.assertTrue(self.bad("U_G18_Flux_0", runArgv=json.dumps([DRIVER, "--omnifile", "x"])))
        self.assertTrue(self.bad("U_G18_Flux_0", cfg={"seed": 43}))
        self.assertTrue(self.bad("U_G18_Flux_0", cfg={"universe": "Flux:1"}))
        self.assertTrue(self.bad("B_G18_002", cfg={"bootstrap_seed": 3}))
        self.assertTrue(self.bad("L_G18_BeamAngleY_0", cfg={"omnifile": "/x/active_BeamAngleY_1.root"}))
        self.assertTrue(self.bad("X_G18", cfg={"universe": "Flux:0"}))
        self.assertTrue(self.bad("X_G18", cfg={"data_file": "/x/data_5720000.root"}))

    def test_another_role_refuses(self):
        p = dict(self.tree.prov["X_G18"])
        c_ = json.loads(p["runConfig"])
        c_["out"] = f"{self.tree.run}/out/B_G18_001/xsec.root"
        p["runConfig"] = json.dumps(c_)
        self.assertTrue(any("runConfig out" in x for x in self.check("X_G18", p, code=CODE)))

    def test_plan_refuses_an_undeclared_toy_set(self):
        comp = {lab: {} for lab in labels_of("G18")}
        rd.plan("G18", comp)
        comp.pop("T_G18_5720007")
        comp["T_G18_5729999"] = {}
        with self.assertRaisesRegex(c.Refusal, "declared seeds"):
            rd.plan("G18", comp)

    def test_one_code(self):
        self.assertEqual(rd.one_code({"a": CODE, "b": CODE}), (CODE, []))
        self.assertIsNone(rd.one_code({"a": CODE, "b": dict(CODE, driverSha256="e")})[0])

    def inv(self, t, dt, size=None):
        lo, hi = (rd.epoch_pst(x) for x in rd.JOB_WINDOW[t])
        base = lo if dt <= 0 else hi
        mt = int((base + dt) * 1e9) if dt else int(lo * 1e9)
        rec = {"size": size or 1, "mtime_ns": mt, "inode": 1, "sha256": rd.PSEUDO_A_SHA[t]}
        return {"cells_npz": dict(rec), "pseudo_a_json": dict(rec), "truth_xsec_npz": dict(rec)}

    def test_window_edges(self):
        for t in TRUTHS:
            lo, hi = (rd.epoch_pst(x) for x in rd.JOB_WINDOW[t])
            for at, ok in ((lo - 1, False), (lo + 1, True), (hi - 1, True), (hi + 1, False)):
                rec = {"size": rd.G18_CELLS["size"], "mtime_ns": int(at * 1e9), "inode": 1, "sha256": rd.PSEUDO_A_SHA[t]}
                inv = {k: dict(rec) for k in ("cells_npz", "pseudo_a_json", "truth_xsec_npz")}
                probs = [x for x in rd.identity(t, inv) if "outside" in x]
                self.assertEqual(not probs, ok, (t, at - lo, hi - at))

    def test_pst_is_utc_minus_8(self):
        self.assertEqual(rd.epoch_pst("2026-11-05T02:42:18"), 1793875338.0)

    def test_g18_cells_size_and_minute(self):
        m = rd.datetime.fromisoformat(rd.G18_CELLS["minute"] + ":30").replace(tzinfo=rd.PST).timestamp()
        rec = {"size": rd.G18_CELLS["size"], "mtime_ns": int(m * 1e9), "inode": 1, "sha256": rd.PSEUDO_A_SHA["G18"]}
        inv = {k: dict(rec) for k in ("cells_npz", "pseudo_a_json", "truth_xsec_npz")}
        self.assertEqual(rd.identity("G18", inv), [])
        inv["cells_npz"] = dict(rec, size=rec["size"] + 1)
        self.assertTrue(rd.identity("G18", inv))
        inv["cells_npz"] = dict(rec, mtime_ns=rec["mtime_ns"] + 60 * 10**9)
        self.assertTrue(rd.identity("G18", inv))

    def test_job_env_and_argv(self):
        e = self.tree.env
        self.assertEqual(e["UNI"], f"{self.tree.g}/shared/uni.root")
        self.assertEqual(e["O"], str(self.tree.run))
        argv = rd.expected_argv("--omnifile $CV --data-file $D/data_1.root", dict(e, D="/d"), "/o")
        self.assertEqual(argv, ["--omnifile", f"{self.tree.g}/stage/cv.root", "--data-file", "/d/data_1.root", "--out", "/o"])


@unittest.skipUnless(HAVE, "needs PyROOT")
class Provenance(unittest.TestCase):
    def test_reads_only_tnamed_records_of_a_real_root_file(self):
        import ROOT
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "x.root")
            f = ROOT.TFile(p, "RECREATE")
            ROOT.TNamed("driverSha256", "abc").Write()
            ROOT.TNamed("runArgv", '["a"]').Write()
            h = ROOT.TH1D("hXSec", "hXSec", 2, 0, 1)
            h.Write()
            ROOT.TParameter("double")("dataPOTUsed", 1.0).Write()
            f.Close()
            self.assertEqual(rd.read_provenance(p), {"driverSha256": "abc", "runArgv": '["a"]'})


@unittest.skipUnless(HAVE, "needs PyROOT")
class Atime(Base):
    """The atime STOP in both directions, on any platform: an input's atime moved between watch and finish, or not."""
    def test_atime_moved_stops_and_unmoved_does_not(self):
        with tempfile.TemporaryDirectory(dir=self.tree.d) as td:
            for move, want in ((True, ["atime moved on 1 inputs"]), (False, [])):
                p = Path(td) / f"in{move}"
                p.write_bytes(b"x")
                with mock.patch.object(rd.Run, "watch", lambda self_, path: self_.atimes.setdefault(str(path), os.stat(path).st_atime_ns)):
                    run = rd.Run("G18", str(self.tree.run), Path(tempfile.mkdtemp(dir=td)))
                    run.watch(p)
                    if move:
                        st = os.stat(p)
                        os.utime(p, ns=(st.st_atime_ns + 10**9, st.st_mtime_ns))
                    rec = run.finish(Path(td), f"r{move}.json")
                self.assertEqual([x for x in rec["stop"] if x.startswith("atime")], want)


if __name__ == "__main__":
    unittest.main()
