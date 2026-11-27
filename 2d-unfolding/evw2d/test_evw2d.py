#!/usr/bin/env python3
"""Controls for ``evw2d.py`` (EVW2D-DECLARATION.md §4-§5): each mechanism fires on its defect and stays silent on the
clean case.

The run tests drive E_R's real driver, in-process, from a clean tree at the pinned commit (``EVW2D_DRIVER_TREE``), on a
synthetic omnifile shaped like RE-2's fixture (``re2/tests/test_re2_driver.py``) plus rows that reach every branch of
the signal loader's keep rule, with two OmniFold iterations. Their references are made by the same driver, unrecorded,
on our edges and with ``PT_EDGES`` set to the paper's, as E_R and Tier 1 were. The reference tests read the committed
Tier 1 products. Needs PyROOT, LightGBM, scikit-learn and numpy.

    EVW2D_DRIVER_TREE=/path/to/clean/clone/at/77d76cfc python3 -B -m pytest -q -p no:cacheprovider \
        2d-unfolding/evw2d/test_evw2d.py

The tests' lane root is a temporary directory beside the driver tree (removed at exit), so the binding checks see
the tree, the staging roots and the outputs inside it.
"""
from __future__ import annotations

import atexit
import contextlib
import copy
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from array import array
from pathlib import Path
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
if os.environ.get("EVW2D_MUTANT"):  # evw2d_mutation.py: the module under test is a mutated copy
    import importlib.util
    _spec = importlib.util.spec_from_file_location("evw2d", os.environ["EVW2D_MUTANT"])
    E = importlib.util.module_from_spec(_spec)
    sys.modules["evw2d"] = E
    _spec.loader.exec_module(E)
else:
    import evw2d as E  # noqa: E402

TREE = Path(os.environ.get("EVW2D_DRIVER_TREE", "")).resolve()
if not (TREE / "2d-unfolding" / "re2" / "re2_driver.py").is_file():
    raise SystemExit("set EVW2D_DRIVER_TREE to a clean tree at config.json's driver_tree.commit")
# O_NOATIME, substituted as REF-C2C1's suite does (macOS has none; O_NONBLOCK is inert on a regular file's open)
mock.patch.object(os, "O_NOATIME", os.O_NONBLOCK, create=True).start()

BASE = json.loads(E.CONFIG.read_text())
BASE["driver_tree"]["root"] = str(TREE)
R, DRIVER, OHF = E.load_runner(BASE)
PAPER_PT = [0, 0.075, 0.15, 0.25, 0.325, 0.40, 0.475, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50]
PHI = 6.2433e-4
TIER1 = REPO / "docs/orchestration/state/ibu-chi2-20261123/tier1/units"


def sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()




# ------------------------------------------------------------------------------------------- fixtures

SPECIAL = [  # (MC, MC_pz, sim, sim_pz, sim_pass, w_truth, w_reco): each reaches one branch of the keep rule
    (0.30, 4.0, 0.31, 4.1, 1, np.nan, 1.0),      # non-finite w_truth: dropped
    (0.30, 4.0, 0.31, 4.1, 1, 1.0, 1.0e4),       # w_reco at 1e4: dropped
    (0.30, 4.0, 0.31, 4.1, 1, -0.1, 1.0),        # negative w_truth: dropped
    (1.00, 2.0, 0.98, 2.1, 1, 1.0, 1.0),         # theta > 20 deg, reco passes: kept, reco only
    (0.30, 70.0, 0.31, 50.0, 1, 1.0, 1.0),       # truth p|| outside, reco passes: kept, reco only
    (0.30, 70.0, 0.31, 50.0, 0, 1.0, 1.0),       # truth outside, reco fails: dropped
    (np.nan, 4.0, 0.31, 4.1, 1, 1.0, 1.0),       # truth not finite, reco passes: kept, truth -9999
    (0.30, 4.0, 4.60, 4.1, 1, 1.0, 1.0),         # reco pT outside: kept, truth only
    (4.50, 20.0, 1.0, 19.0, 1, 1.0, 1.0),        # truth pT on the top edge: truth passes, no cell (overflow)
    (0.30, 60.0, 0.30, 59.0, 1, 1.0, 1.0),       # truth p|| on the top edge: truth passes, no cell
    (0.07, 5.0, 0.07, 5.0, 1, 1.2, 1.1),         # on our interior pT edge and a p|| edge: the upper cell
    (0.075, 5.0, 0.075, 5.0, 1, 1.3, 1.2),       # on the paper's interior pT edge
    (0.0, 1.5, 0.0, 1.5, 0, 0.9, 0.9),           # on the lower corner: truth passes
    (0.30, 4.0, 4.50, 4.1, 1, 1.0, 1.0),         # reco pT on the top edge: reco passes
    (0.30, 4.0, 0.31, 60.0, 1, 1.0, 1.0),        # reco p|| on the top edge: reco passes
    (0.40, 6.0, 0.41, 6.1, 1, 1.1, 1.0),         # two identical rows: two entries, both kept
    (0.40, 6.0, 0.41, 6.1, 1, 1.1, 1.0),
]


def write_omnifile(path: Path, *, seed: int = 11, n: int = 3000, denom_extra: bool = False) -> None:
    """RE-2's fixture shape (post-Phase-18, hasTruthOnlyMisses) with the SPECIAL rows appended to mc_signal_reco. The
    denominator holds exactly the truth-passing signal rows, permuted; ``denom_extra`` adds one more row."""
    import ROOT
    rng = np.random.default_rng(seed)
    pt = rng.uniform(0.02, 2.0, n)
    pz = rng.uniform(1.6, 18.0, n)
    pt = np.minimum(pt, 0.3 * pz)
    sp = (rng.uniform(size=n) < 0.7).astype(np.uint8)
    cols = {"MC": pt, "MC_pz": pz, "sim": np.clip(pt * rng.normal(1, 0.06, n), 0.001, 4.4),
            "sim_pz": np.clip(pz * rng.normal(1, 0.06, n), 1.51, 59.0), "sim_pass": sp,
            "w_truth": rng.uniform(0.5, 1.5, n), "w_reco": rng.uniform(0.5, 1.5, n)}
    spec = np.array(SPECIAL, dtype=float)
    for j, k in enumerate(E.SIGNAL_BRANCHES):
        add = spec[:, j].astype(np.uint8) if k == "sim_pass" else spec[:, j]
        cols[k] = np.concatenate([cols[k], add])
    # the truth-passing kept rows, by the driver's own rule
    keep = []
    for i in range(cols["MC"].size):
        wt, wr = cols["w_truth"][i], cols["w_reco"][i]
        good = np.isfinite(wt) and np.isfinite(wr) and 0 <= wt < 1e4 and 0 <= wr < 1e4
        if good and DRIVER.in_truth_phase_space(float(cols["MC"][i]), float(cols["MC_pz"][i]), 0, 4.5, 1.5, 60.0):
            keep.append(i)
    keep = np.array(keep)
    perm = rng.permutation(keep.size)
    den = {k: cols[k][keep][perm] for k in ("MC", "MC_pz", "w_truth")}
    if denom_extra:
        for k, v in (("MC", 0.2), ("MC_pz", 3.0), ("w_truth", 1.0)):
            den[k] = np.append(den[k], v)
    nb, nd = 1200, 2000
    bkg = {"sim_background": rng.uniform(0.0, 2.2, nb), "sim_background_pz": rng.uniform(1.4, 18.0, nb),
           "sim_background_pass": (rng.uniform(size=nb) < 0.9).astype(np.uint8), "w_bkg": rng.uniform(0.0, 2.0, nb)}
    data = {"measured": rng.uniform(0.02, 2.0, nd), "measured_pz": rng.uniform(1.6, 18.0, nd),
            "measured_pass": np.ones(nd, np.uint8)}
    f = ROOT.TFile.Open(str(path), "RECREATE")
    for name, c in (("mc_signal_reco", cols), ("mc_background", bkg), ("data", data), ("mc_truth_denom", den)):
        t = ROOT.TTree(name, name)
        bufs = {}
        for k, v in c.items():
            code, leaf = ("B", "b") if v.dtype == np.uint8 else ("d", "D")
            bufs[k] = array(code, [0])
            t.Branch(k, bufs[k], f"{k}/{leaf}")
        for i in range(next(iter(c.values())).size):
            for k, v in c.items():
                bufs[k][0] = v[i].item()
            t.Fill()
        t.Write()
    ROOT.TParameter("double")("dataPOTUsed", 1.0e20).Write()
    ROOT.TParameter("double")("mcPOTUsed", 4.0e20).Write()
    ROOT.TParameter("int")("hasTruthOnlyMisses", 1).Write()
    f.Close()


def write_flux(path: Path, values=None) -> None:
    import ROOT
    g = ROOT.TFile.Open(str(path), "RECREATE")
    h = ROOT.TH1D("pTmu_reweightedflux_integrated", "", 14, np.array(PAPER_PT, float))
    vals = values if values is not None else [np.nextafter(PHI, 1.0) if i % 3 == 0 else PHI for i in range(14)]
    for i, v in enumerate(vals):
        h.SetBinContent(i + 1, v)
    h.Write()
    g.Close()


# the tests' lane root holds the driver tree, this checkout and LANE, where every test writes; its parent stands in for
# the scratch prefix
LANE_ROOT = Path(os.path.commonpath([str(TREE), str(REPO)]))
LANE = Path(tempfile.mkdtemp(prefix="evw2d-test-", dir=LANE_ROOT))
mock.patch.object(E, "SCRATCH_PREFIX", str(LANE_ROOT.parent)).start()


def _remove_lane():
    for d, _, _ in os.walk(LANE):  # staging roots are read-only (0555); open them before removing
        os.chmod(d, 0o755)
    shutil.rmtree(LANE, True)


atexit.register(_remove_lane)


def driver_hxsec(cfg: dict, out: Path, pt_edges=None) -> np.ndarray:
    """The driver unrecorded (REF-C2C1's runner), on our edges or with PT_EDGES replaced, as E_R and Tier 1 ran."""
    edges = list(pt_edges) if pt_edges is not None else list(DRIVER.PT_EDGES)
    with mock.patch.object(DRIVER, "PT_EDGES", edges):
        R.run_driver(DRIVER, OHF, E.resolve_argv(cfg), out / "xsec.root", staging=E.staging_root(cfg))
    return E.own_hist(R, out / "xsec.root", "hXSec2D", edges, DRIVER.PZ_EDGES)


def bound(cfg: dict, lane: Path) -> dict:
    """cfg with the binding filled for the tests: the declaration's digest and the lane root."""
    cfg = copy.deepcopy(cfg)
    cfg["declaration_sha256"] = sha(REPO / cfg["declaration"])
    cfg["lane_root"] = str(lane)
    return cfg


@contextlib.contextmanager
def as_main(cfg: dict, env: dict | None = None, host: str = "nid001234"):
    """main() on ``cfg``: written to a config file whose digest is passed, the reviewed values set to the fixture's,
    the driver tree's modules unloaded first (main() refuses preloaded ones), an allocation in the environment."""
    p = Path(tempfile.mkdtemp(dir=LANE)) / "config.json"
    p.write_text(json.dumps(cfg))
    fresh = {k: v for k, v in sys.modules.items() if k not in E.PRELOAD_FORBIDDEN}
    reviewed = dict(ER_ARGV=cfg["argv"], ER_CPUS=cfg["cpus"], ER_THREAD_ENV=cfg["thread_env"],
                    INPUT_SHA256={k: cfg["inputs"][f"{k}_sha256"] for k in ("CV", "MC")},
                    REFERENCES_SHA256=cfg["references"]["sha256"])
    alloc = {"SLURM_JOB_ID": "77", "SLURM_STEP_ID": "0", "SLURM_JOB_NUM_NODES": "1"} if env is None else env
    with contextlib.ExitStack() as st:
        st.enter_context(mock.patch.object(E, "CONFIG", p))
        st.enter_context(mock.patch.dict(sys.modules, fresh, clear=True))
        for k, v in reviewed.items():
            st.enter_context(mock.patch.object(E, k, v))
        st.enter_context(mock.patch.dict(os.environ, alloc))
        st.enter_context(mock.patch.object(E.socket, "gethostname", lambda: host))
        yield (lambda *argv: E.main(["--config-sha256", sha(p), *argv]))


class Case:
    """One staged fixture (omnifile, flux), its config and its two driver-made references."""

    def __init__(self, *, denom_extra=False, flux=None):
        self.td = Path(tempfile.mkdtemp(dir=LANE))
        self.stage = self.td / "stage"
        self.stage.mkdir()
        write_omnifile(self.stage / "omni.root", denom_extra=denom_extra)
        write_flux(self.stage / "flux.root", flux)
        cfg = copy.deepcopy(BASE)
        cfg["inputs"]["staging"].update(root=str(self.stage), CV="omni.root", MC="flux.root")
        cfg["inputs"]["CV_sha256"] = sha(self.stage / "omni.root")
        cfg["inputs"]["MC_sha256"] = sha(self.stage / "flux.root")
        cfg["argv"] = [("2" if x == "5" else x) for x in cfg["argv"]]
        cfg["cpus"] = R.cpu_count()
        cfg["thread_env"] = {k: os.environ.get(k) for k in cfg["thread_env"]}
        er = driver_hxsec(cfg, self._fresh("ref_er"))
        pa = driver_hxsec(cfg, self._fresh("ref_paper"), PAPER_PT)
        refs = self.td / "references.npz"
        np.savez(refs, er=er, er_pt_edges=np.array(DRIVER.PT_EDGES, float), er_pz_edges=np.array(DRIVER.PZ_EDGES, float),
                 paper=pa, paper_pt_edges=np.array(PAPER_PT, float), paper_pz_edges=np.array(DRIVER.PZ_EDGES, float),
                 meta=np.array("{}"))
        cfg["references"] = {"path": str(refs), "sha256": sha(refs)}
        self.cfg = bound(cfg, LANE_ROOT)
        self.cfg_sha = hashlib.sha256(json.dumps(self.cfg, sort_keys=True).encode()).hexdigest()
        os.chmod(self.stage, 0o555)  # as stage() leaves it
        self.verified = E.check_staged(self.cfg, R)
        self.n = 0

    def _fresh(self, name):
        d = self.td / name
        d.mkdir()
        return d

    def out(self):
        self.n += 1
        return self.td / f"out{self.n}"

    def run(self, cfg=None, out=None, tree_sha=None):
        out = out or self.out()
        rc = E.run(cfg or self.cfg, out, R, DRIVER, OHF, tree_sha or dict(BASE["driver_tree"]["code_sha256"]),
                   self.verified, config_sha256=self.cfg_sha, started=time.time())
        rec = json.loads((out / "run.json").read_text()) if (out / "run.json").exists() else None
        return rc, out, rec

    def done(self, out):
        return json.loads((out / "evw2d.done").read_text())


_CASES = {}


def case(name="clean", **kw) -> Case:
    if name not in _CASES:
        _CASES[name] = Case(**kw)
    return _CASES[name]


def tampered_write(change):
    """A write_npz that applies ``change(arrays, meta)`` to weights.npz before writing it."""
    real = E.write_npz

    def write(path, arrays, meta):
        if path.name == "weights.npz":
            arrays, meta = change({k: np.array(v, copy=True) for k, v in arrays.items()}, copy.deepcopy(meta))
        return real(path, arrays, meta)
    return mock.patch.object(E, "write_npz", write)


# ------------------------------------------------------------------------------------------- tests


class PinnedBytes(unittest.TestCase):
    def test_tree_files_equal_their_pins_and_the_commit(self):
        got = E.check_tree(BASE)
        self.assertEqual(got, BASE["driver_tree"]["code_sha256"])
        for rel, want in BASE["driver_tree"]["code_sha256"].items():
            blob = subprocess.run(["git", "-C", str(REPO), "show", f"{BASE['driver_tree']['commit']}:{rel}"],
                                  capture_output=True, check=True).stdout
            self.assertEqual(hashlib.sha256(blob).hexdigest(), want, rel)

    def test_pins_are_ref_c2c1s_and_tier1s(self):
        ref = json.loads(subprocess.run(["git", "-C", str(REPO), "show",
                                         f"{BASE['driver_tree']['commit']}:2d-unfolding/ref_c2c1/config.json"],
                                        capture_output=True, check=True, text=True).stdout)
        pins = BASE["driver_tree"]["code_sha256"]
        for rel in ("2d-unfolding/re2/re2_driver.py", "unbinned_unfolding/python/omnifold.py"):
            self.assertEqual(pins[rel], ref["code_sha256"][rel])
        self.assertEqual(BASE["argv"], ref["e_r"]["argv"])
        self.assertEqual((BASE["cpus"], BASE["thread_env"]), (ref["e_r"]["cpus"], ref["e_r"]["thread_env"]))
        self.assertEqual({k: BASE["inputs"][k] for k in ("CV_source", "CV_sha256", "MC_source", "MC_sha256")},
                         {k: ref["inputs"][k] for k in ("CV_source", "CV_sha256", "MC_source", "MC_sha256")})

    def copy_tree(self):
        td = Path(tempfile.mkdtemp(dir=LANE))
        for rel in BASE["driver_tree"]["code_sha256"]:
            (td / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(TREE / rel, td / rel)
        cfg = copy.deepcopy(BASE)
        cfg["driver_tree"]["root"] = str(td)
        return td, cfg

    def test_a_changed_byte_refuses(self):
        td, cfg = self.copy_tree()
        E.check_tree(cfg)
        with open(td / "2d-unfolding/ref_c2c1/config.json", "ab") as fh:
            fh.write(b" ")
        with self.assertRaises(E.GateFailure):
            E.check_tree(cfg)

    def test_a_pin_reached_through_a_link_refuses(self):
        td, cfg = self.copy_tree()
        rel = "2d-unfolding/re2/re2_driver.py"
        elsewhere = Path(tempfile.mkdtemp(dir=LANE)) / "re2_driver.py"
        shutil.move(td / rel, elsewhere)  # the same bytes, outside the tree
        os.symlink(elsewhere, td / rel)
        with self.assertRaisesRegex(E.GateFailure, "not a plain file"):
            E.check_tree(cfg)

    def test_a_bytecode_cache_refuses(self):
        td, cfg = self.copy_tree()
        (td / "2d-unfolding/re2/__pycache__").mkdir()
        with self.assertRaises(E.GateFailure):
            E.check_tree(cfg)

    def test_unbound_tree_refuses(self):
        cfg = copy.deepcopy(BASE)
        cfg["driver_tree"]["root"] = None
        with self.assertRaises(E.GateFailure):
            E.check_tree(cfg)

    def test_a_full_run_leaves_the_tree_unchanged(self):
        before = {rel: sha(TREE / rel) for rel in BASE["driver_tree"]["code_sha256"]}
        rc, _, rec = case().run()
        self.assertEqual(rc, 0)
        self.assertEqual({rel: sha(TREE / rel) for rel in before}, before)
        self.assertEqual(before, BASE["driver_tree"]["code_sha256"])
        self.assertTrue(rec["controls"]["C-PINS"]["pass"])
        self.assertEqual(rec["controls"]["C-PINS"]["after_run"], before)

    def test_c_pins_fails_when_the_pre_run_digests_differ(self):
        rc, _, rec = case().run(tree_sha={k: "0" * 64 for k in BASE["driver_tree"]["code_sha256"]})
        self.assertEqual(rc, E.RC_CONTROL)
        self.assertFalse(rec["controls"]["C-PINS"]["pass"])

    def test_driver_and_helper_come_from_the_tree(self):
        self.assertEqual(Path(DRIVER.__file__).resolve(), TREE / "2d-unfolding/re2/re2_driver.py")
        self.assertEqual(Path(R.__file__).resolve(), TREE / "2d-unfolding/ref_c2c1/ref_c2c1.py")
        self.assertEqual(Path(sys.modules["omnifold"].__file__).resolve(),
                         TREE / "unbinned_unfolding/python/omnifold.py")


class Binding(unittest.TestCase):
    def cfg(self):
        c = bound(BASE, LANE_ROOT)
        c["inputs"]["staging"]["root"] = str(LANE / "stage")
        return c

    def check(self, c, out=None):
        E.check_binding(c, "a" * 64, "a" * 64, out)

    def test_a_complete_binding_passes(self):
        self.check(self.cfg(), LANE / "new_out")
        self.check(self.cfg())

    def test_each_gap_refuses(self):
        cases = []

        def add(msg, change=None, out=None):
            c = self.cfg()
            if change:
                change(c)
            cases.append((c, out, msg))
        add("not the bound", lambda c: c.update(declaration_sha256="0" * 64))
        add("declaration_sha256 is bound", lambda c: c.update(declaration_sha256=None))
        add("lane root is bound", lambda c: c.update(lane_root=None))
        add("strictly under", lambda c: c.update(lane_root=tempfile.mkdtemp()))
        add("strictly under", lambda c: c.update(lane_root=str(E.SCRATCH_PREFIX)))
        add("the driver tree", lambda c: c["driver_tree"].update(root=tempfile.mkdtemp()))
        add("the driver tree", lambda c: c["driver_tree"].update(root=str(LANE_ROOT)))
        add("the staging root", lambda c: c["inputs"]["staging"].update(root=tempfile.mkdtemp()))
        add("the staging root", lambda c: c["inputs"]["staging"].update(root=str(LANE_ROOT)))
        for name in ("../omni.root", "/abs/flux.root", ".", "..", ""):
            add("plain file name", lambda c, n=name: c["inputs"]["staging"].update(CV=n))
        add("argv", lambda c: c.update(argv=c["argv"][:-1] + ["63"]))
        add("exact_rtol", lambda c: c.update(exact_rtol=1e-7))
        add("cpus", lambda c: c.update(cpus=32))
        add("thread_env", lambda c: c.update(thread_env=dict(c["thread_env"], OMP_NUM_THREADS="32")))
        add("inputs", lambda c: c["inputs"].update(CV_sha256="0" * 64))
        add("references", lambda c: c["references"].update(sha256="0" * 64))
        add("paper_pt_edges", lambda c: c.update(paper_pt_edges=list(DRIVER.PT_EDGES)))
        add("four required files", lambda c: c["driver_tree"].update(code_sha256={}))
        add("is not inside", out=Path(tempfile.mkdtemp()) / "out")   # --out outside the lane
        add("is not inside", out=LANE_ROOT)                          # --out is the lane root
        for i, (c, out, msg) in enumerate(cases):
            with self.assertRaisesRegex(E.GateFailure, msg, msg=str(i)):
                self.check(c, out)

    def test_this_checkout_must_be_inside_the_lane(self):
        c = self.cfg()
        elsewhere = Path(tempfile.mkdtemp())  # outside the lane, holding the same declaration
        (elsewhere / c["declaration"]).parent.mkdir(parents=True)
        shutil.copy(REPO / c["declaration"], elsewhere / c["declaration"])
        with mock.patch.object(E, "REPO", elsewhere):
            with self.assertRaisesRegex(E.GateFailure, "this checkout"):
                self.check(c)

    def test_the_command_line_digest_must_be_config_jsons(self):
        c = self.cfg()
        p = Path(tempfile.mkdtemp(dir=LANE)) / "config.json"
        p.write_text(json.dumps(c))
        with mock.patch.object(E, "CONFIG", p):
            got, digest = E.load_config()  # parsed from the bytes it hashed
        self.assertEqual((got, digest), (c, sha(p)))
        with self.assertRaisesRegex(E.GateFailure, "config.json has sha256"):
            E.check_binding(c, digest, "0" * 64)

    def test_allocation(self):
        good = {"SLURM_JOB_ID": "123", "SLURM_STEP_ID": "0", "SLURM_JOB_NUM_NODES": "1"}
        base = {k: v for k, v in os.environ.items() if not k.startswith("SLURM_")}
        with mock.patch.dict(os.environ, {**base, **good}, clear=True), \
                mock.patch.object(E.socket, "gethostname", lambda: "nid004567"):
            self.assertEqual(E.check_allocation()["host"], "nid004567")
        bad = [({**good, "SLURM_JOB_NUM_NODES": "2"}, "nid1"), ({k: v for k, v in good.items() if k != "SLURM_JOB_ID"}, "nid1"),
               ({k: v for k, v in good.items() if k != "SLURM_STEP_ID"}, "nid1"), (good, "login31"), ({}, "nid1"),
               ({**good, "SLURM_STEP_ID": "batch"}, "nid1"), ({**good, "SLURM_STEP_ID": "extern"}, "nid1"),
               ({**good, "SLURM_JOB_ID": "x"}, "nid1"),
               ({**good, "SLURM_STEP_ID": str(0xFFFFFFFB)}, "nid1")]  # a reserved id, numeric
        for env, host in bad:
            with mock.patch.dict(os.environ, {**base, **env}, clear=True), \
                    mock.patch.object(E.socket, "gethostname", lambda h=host: h):
                with self.assertRaises(E.GateFailure, msg=str((env, host))):
                    E.check_allocation()

    def test_interpreter(self):
        fresh = {k: v for k, v in sys.modules.items() if k not in E.PRELOAD_FORBIDDEN}
        with mock.patch.dict(sys.modules, fresh, clear=True):
            E.check_interpreter()
            with mock.patch.object(sys, "dont_write_bytecode", False):
                with self.assertRaisesRegex(E.GateFailure, "python -B"):
                    E.check_interpreter()
            with mock.patch.object(sys, "pycache_prefix", "/tmp/elsewhere", create=True):
                with self.assertRaisesRegex(E.GateFailure, "pycache_prefix"):
                    E.check_interpreter()
        with self.assertRaisesRegex(E.GateFailure, "loaded before"):
            E.check_interpreter()  # the suite itself loaded the driver tree's modules

    def test_checkout(self):
        self.assertEqual(E.check_checkout(BASE), BASE["driver_tree"]["commit"])
        c = copy.deepcopy(BASE)
        c["driver_tree"]["commit"] = "0" * 40
        with self.assertRaisesRegex(E.GateFailure, "HEAD"):
            E.check_checkout(c)
        g = Path(tempfile.mkdtemp(dir=LANE))
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                   GIT_COMMITTER_EMAIL="t@t")
        for cmd in (["init", "-q"], ["commit", "-q", "--allow-empty", "-m", "x"]):
            subprocess.run(["git", "-C", str(g), *cmd], check=True, env=env, capture_output=True)
        head = subprocess.run(["git", "-C", str(g), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        c["driver_tree"].update(root=str(g), commit=head)
        self.assertEqual(E.check_checkout(c), head)
        (g / "sub").mkdir()
        with self.assertRaisesRegex(E.GateFailure, "top level"):
            E.check_checkout(dict(c, driver_tree=dict(c["driver_tree"], root=str(g / "sub"))))
        g2 = Path(tempfile.mkdtemp(dir=LANE))  # another checkout, dirty, on another commit
        for cmd in (["init", "-q"], ["commit", "-q", "--allow-empty", "-m", "y"]):
            subprocess.run(["git", "-C", str(g2), *cmd], check=True, env=env, capture_output=True)
        (g2 / "stray.txt").write_text("x")
        with mock.patch.dict(os.environ, {"GIT_DIR": str(g / ".git"), "GIT_WORK_TREE": str(g)}):
            with self.assertRaises(E.GateFailure):  # judged on g2 itself, not on the clean g the variables name
                E.check_checkout(dict(c, driver_tree=dict(c["driver_tree"], root=str(g2))))
        (g / "stray.pyc").write_bytes(b"x")
        with self.assertRaisesRegex(E.GateFailure, "not clean"):
            E.check_checkout(c)

    def test_git_runs_with_no_inherited_git_variable(self):
        planted = {"GIT_DIR": "/nonexistent/.git", "GIT_WORK_TREE": "/nonexistent", "GIT_INDEX_FILE": "/nonexistent/i",
                   "GIT_CEILING_DIRECTORIES": "/", "GIT_OPTIONAL_LOCKS": "1"}
        with mock.patch.dict(os.environ, planted):
            env = E.git_env()
        self.assertEqual({k: v for k, v in env.items() if k.startswith("GIT_")}, {"GIT_OPTIONAL_LOCKS": "0"})


class Recorders(unittest.TestCase):
    def test_returns_the_identical_object_unmodified(self):
        out = (np.arange(5.0), np.ones(3))
        rec = E.Recorder()
        f = rec.wrap("f", lambda x, y=None: out)
        arg = np.arange(4.0)
        before = (E.digest(out), E.digest(arg))
        got = f(arg, y=np.zeros(2))
        self.assertIs(got, out)
        self.assertIs(got[1], out[1])
        self.assertEqual((E.digest(got), E.digest(arg)), before)
        self.assertTrue(rec.verify(["f"])["pass"])

    def test_in_the_run_each_caller_receives_the_real_object(self):
        """Spies on both sides of each recorder in the real run: inner, between the recorder and the real function;
        outer, between the recorder and its caller (the driver, or REF-C2C1's observer for the OmniFold call). The
        object each caller received is the object the real call made, and its content did not move."""
        made, received = {}, {}

        def spy(store, name, f):
            def s(*a, **k):
                o = f(*a, **k)
                store.setdefault(name, []).append({"out": o, "digest": E.digest(o), "args": a, "kwargs": k})
                return o
            return s

        def targets(driver, ohf):
            return {"omnifold": ohf, "collect_truth_denom_arrays": driver, "get_pot_scales": driver}
        real_patches, real_run_driver = E.recorder_patches, R.run_driver

        def inner(rec, driver, ohf):  # wrap the real functions before the recorders take them
            with contextlib.ExitStack() as st:
                for n, t in targets(driver, ohf).items():
                    f = spy(made, n, getattr(t, n))
                    st.enter_context(mock.patch.object(t, n, staticmethod(f) if t is ohf else f))
                return real_patches(rec, driver, ohf)

        def outer(driver, ohf, *a, **k):  # the recorders are installed: wrap them on the caller's side
            with contextlib.ExitStack() as st:
                for n, t in targets(driver, ohf).items():
                    f = spy(received, n, getattr(t, n))
                    st.enter_context(mock.patch.object(t, n, staticmethod(f) if t is ohf else f))
                return real_run_driver(driver, ohf, *a, **k)
        with mock.patch.object(E, "recorder_patches", inner), mock.patch.object(R, "run_driver", outer):
            rc, _, rec = case().run()
        self.assertEqual(rc, 0)
        self.assertEqual(set(made), set(E.SEAMS))
        self.assertEqual(set(received), set(E.SEAMS))
        for n in E.SEAMS:
            self.assertEqual((len(made[n]), len(received[n])), (1, 1), n)  # one real call, one caller call
            m, r = made[n][0], received[n][0]
            self.assertIs(r["out"], m["out"], n)
            self.assertEqual(r["digest"], m["digest"], n)
            self.assertEqual(E.digest(m["out"]), m["digest"], n)
            self.assertEqual(len(r["args"]), len(m["args"]), n)  # the arguments reach the real call as themselves
            for x, y in zip(r["args"], m["args"]):
                self.assertIs(x, y, n)
            self.assertEqual(set(r["kwargs"]), set(m["kwargs"]), n)
            for key in r["kwargs"]:
                self.assertIs(r["kwargs"][key], m["kwargs"][key], (n, key))
        self.assertTrue(rec["controls"]["C-REC"]["pass"])

    def test_a_missing_seam_refuses(self):
        real = E.recorder_patches
        with mock.patch.object(E, "recorder_patches", lambda rec, d, o: real(rec, d, o)[:2]):
            with self.assertRaises(E.GateFailure):
                case().run()

    def test_a_later_change_to_the_output_fails(self):
        out = [np.arange(5.0)]
        rec = E.Recorder()
        rec.wrap("f", lambda: out)()
        out[0][2] = 99.0
        v = rec.verify(["f"])
        self.assertFalse(v["pass"])
        self.assertFalse(v["calls"]["f"]["out_unchanged"])

    def test_a_call_that_changes_its_arguments_fails(self):
        def bad(a):
            a[0] = -1.0
            return 1.0
        rec = E.Recorder()
        rec.wrap("f", bad)(np.arange(3.0))
        v = rec.verify(["f"])
        self.assertFalse(v["pass"])
        self.assertFalse(v["calls"]["f"]["args_unchanged"])

    def test_a_missing_call_fails(self):
        self.assertFalse(E.Recorder().verify(["f"])["pass"])
        with self.assertRaises(E.GateFailure):
            E.Recorder().require(["f"])

    def test_a_second_call_refuses(self):
        rec = E.Recorder()
        f = rec.wrap("f", lambda: 1)
        f()
        with self.assertRaises(E.GateFailure):
            f()

    def test_digest_sees_dtype_shape_and_float_bits(self):
        a = np.arange(4.0)
        self.assertNotEqual(E.digest(a), E.digest(a.astype(np.float32)))
        self.assertNotEqual(E.digest(a), E.digest(a.reshape(2, 2)))
        self.assertNotEqual(E.digest(0.0), E.digest(-0.0))
        self.assertNotEqual(E.digest({"a": 1}), E.digest({"a": 2}))
        self.assertNotEqual(E.digest((1, 2)), E.digest([1, 2]))


class Key(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        c = case()
        cls.path = c.stage / "omni.root"
        import ROOT
        f = ROOT.TFile.Open(str(cls.path))
        cls.sig = DRIVER.collect_signal_arrays_2d(f.Get("mc_signal_reco"), 0, 4.5, 1.5, 60.0, 0.25, use_weights=True)
        f.Close()
        cls.cols = E.read_signal_tree(cls.path)
        cls.indep = E.keep_rule(cls.cols, DRIVER, 0.25, (0, 4.5, 1.5, 60.0))

    def call(self, sig):
        return {"args": (np.column_stack([sig["truth_pt"], sig["truth_pz"]]),
                         np.column_stack([sig["reco_pt"], sig["reco_pz"]]), None, sig["pass_reco"], sig["pass_truth"]),
                "kwargs": {"MCgen_weights": sig["w_truth"], "MCreco_weights": sig["w_reco"]}}

    def test_keep_rule_equals_the_loader_bitwise(self):
        for k in ("truth_pt", "truth_pz", "reco_pt", "reco_pz", "pass_reco", "pass_truth", "w_truth", "w_reco"):
            self.assertTrue(E.same_bits(self.indep[k], self.sig[k]), k)
        self.assertTrue(E.c_key(self.indep, self.call(self.sig))["pass"])

    def test_the_key_sequence_is_exact(self):
        """The kept entry numbers equal a scalar re-statement of the loader over the raw rows, one by one: the special
        rows, the two identical rows and the sentinel rows each at their own entry."""
        c = self.cols
        want = []
        for i in range(c["MC"].size):
            wt, wr = float(c["w_truth"][i]), float(c["w_reco"][i])
            if not (np.isfinite(wt) and np.isfinite(wr) and 0 <= wt < 1e4 and 0 <= wr < 1e4):
                continue
            tru = DRIVER.in_truth_phase_space(float(c["MC"][i]), float(c["MC_pz"][i]), 0, 4.5, 1.5, 60.0)
            rp, rz = float(c["sim"][i]), float(c["sim_pz"][i])
            rec = np.isfinite(rp) and np.isfinite(rz) and 0 <= rp <= 4.5 and 1.5 <= rz <= 60.0
            if tru or (c["sim_pass"][i] != 0 and rec):
                want.append(i)
        self.assertEqual(self.indep["entry"].tolist(), want)
        n = 3000
        self.assertIn(n + 15, want)
        self.assertIn(n + 16, want)
        self.assertTrue(np.array_equal(c["entry"], np.arange(c["MC"].size)))

    def test_special_rows_reach_their_branches(self):
        n = 3000
        e = self.indep["entry"]
        dropped = {n + 0, n + 1, n + 2, n + 5}
        self.assertFalse(dropped & set(e.tolist()))
        pos = {int(x): i for i, x in enumerate(e)}
        self.assertFalse(self.indep["pass_truth"][pos[n + 3]])   # theta > 20 deg
        self.assertFalse(self.indep["pass_truth"][pos[n + 4]])   # truth p|| outside
        self.assertEqual(self.indep["truth_pt"][pos[n + 6]], -9999.0)
        self.assertFalse(self.indep["pass_reco"][pos[n + 7]])
        for j in (8, 9, 10, 11, 12, 15, 16):
            self.assertTrue(self.indep["pass_truth"][pos[n + j]], j)
        for j in (13, 14):
            self.assertTrue(self.indep["pass_reco"][pos[n + j]], j)
        self.assertEqual(e.size, self.sig["truth_pt"].size)

    def test_entries_strictly_increase(self):
        e = self.indep["entry"]
        self.assertTrue(np.all(np.diff(e) > 0))
        self.assertEqual(np.unique(e).size, e.size)

    def test_each_mismatch_fails(self):
        for k in ("truth_pt", "truth_pz", "reco_pt", "reco_pz", "pass_reco", "pass_truth", "w_truth", "w_reco"):
            sig = {kk: np.array(v, copy=True) for kk, v in self.sig.items()}
            i = int(np.flatnonzero(sig["pass_truth"] & sig["pass_reco"])[0])
            sig[k][i] = (not sig[k][i]) if sig[k].dtype == bool else np.nextafter(sig[k][i], np.inf)
            r = E.c_key(self.indep, self.call(sig))
            self.assertFalse(r["pass"], k)
            self.assertFalse(r["equal"][k], k)

    def test_negative_zero_is_not_zero(self):
        self.assertFalse(E.same_bits(np.array([0.0]), np.array([-0.0])))

    def test_unordered_or_oversized_entries_fail(self):
        call = self.call(self.sig)
        bad = dict(self.indep, entry=self.indep["entry"][::-1].copy())
        self.assertFalse(E.c_key(bad, call)["strictly_increasing"])
        self.assertFalse(E.c_key(bad, call)["pass"])
        big = dict(self.indep, entry=self.indep["entry"] + 2 ** 32)
        self.assertFalse(E.c_key(big, call)["fits_uint32"])
        self.assertFalse(E.c_key(big, call)["pass"])

    def test_a_shorter_independent_read_fails(self):
        short = {k: v[1:] for k, v in self.indep.items()}
        self.assertFalse(E.c_key(short, self.call(self.sig))["pass"])

    def write_tree(self, kinds):
        import ROOT
        p = Path(tempfile.mkdtemp(dir=LANE)) / "t.root"
        f = ROOT.TFile.Open(str(p), "RECREATE")
        t = ROOT.TTree("mc_signal_reco", "")
        bufs = {}
        for k in E.SIGNAL_BRANCHES:
            code, leaf = kinds.get(k, ("B", "b") if k == "sim_pass" else ("d", "D"))
            bufs[k] = array(code, [0])
            t.Branch(k, bufs[k], f"{k}/{leaf}")
        t.Fill()
        t.Write()
        f.Close()
        return p

    def test_branch_types_are_required(self):
        E.read_signal_tree(self.write_tree({}))
        for kinds in ({"MC": ("f", "F")}, {"w_reco": ("f", "F")}, {"sim_pass": ("i", "I")}):
            with self.assertRaises(E.GateFailure, msg=str(kinds)):
                E.read_signal_tree(self.write_tree(kinds))

    def test_implicit_mt_refuses(self):
        import ROOT
        ROOT.ROOT.EnableImplicitMT(2)
        try:
            with self.assertRaises(E.GateFailure):
                E.read_signal_tree(self.path)
        finally:
            ROOT.ROOT.DisableImplicitMT()
        self.assertFalse(ROOT.ROOT.IsImplicitMTEnabled())


class Controls(unittest.TestCase):
    def test_flux_within_one_ulp_passes_and_two_ulps_fail(self):
        f = [PHI] * 14
        self.assertTrue(E.c_flux(f)["pass"])
        f[5] = np.nextafter(PHI, 1.0)
        self.assertTrue(E.c_flux(f)["pass"])
        f[6] = np.nextafter(f[5], 1.0)
        self.assertFalse(E.c_flux(f)["pass"])
        self.assertFalse(E.c_flux([1e-3 * i for i in range(1, 15)])["pass"])
        self.assertFalse(E.c_flux([PHI] * 13)["pass"])
        self.assertFalse(E.c_flux([0.0] * 14)["pass"])
        big = np.finfo(np.float64).max
        self.assertFalse(E.c_flux([big] * 13 + [1.0])["pass"])  # np.spacing(max float) is infinite
        self.assertFalse(E.c_flux([[PHI] * 7] * 2)["pass"])     # shape (2, 7)

    def test_the_real_flux_agrees_to_the_ulp(self):
        """The 14 values E_R's run divided by (Tier 1's committed er.root, hFlux_pt, both grids): the scalar note."""
        import ROOT
        for d in ("old", "e"):
            f = ROOT.TFile.Open(str(TIER1 / d / "er.root"))
            h = f.Get("hFlux_pt")
            v = [h.GetBinContent(i) for i in range(1, h.GetNbinsX() + 1)]
            f.Close()
            r = E.c_flux(v)
            self.assertTrue(r["pass"], (d, r))
            self.assertAlmostEqual(v[0], PHI, delta=1e-8)

    def test_complete_equal_multisets_pass(self):
        rng = np.random.default_rng(1)
        t = {"truth_pt": rng.uniform(size=50), "truth_pz": rng.uniform(size=50), "w_prior": rng.uniform(size=50)}
        p = rng.permutation(50)
        d = {"truth_pt": t["truth_pt"][p], "truth_pz": t["truth_pz"][p], "w_truth": t["w_prior"][p]}
        self.assertTrue(E.c_complete(t, d)["pass"])
        d2 = dict(d, w_truth=d["w_truth"].copy())
        d2["w_truth"][3] = np.nextafter(d2["w_truth"][3], 2.0)
        self.assertFalse(E.c_complete(t, d2)["pass"])
        d3 = {k: v[1:] for k, v in d.items()}
        self.assertFalse(E.c_complete(t, d3)["pass"])
        d4 = dict(d, truth_pt=d["truth_pz"], truth_pz=d["truth_pt"])  # columns swapped
        self.assertFalse(E.c_complete(t, d4)["pass"])

    def test_complete_sorts_by_bit_pattern(self):
        """Signed zeros in either order are the same multiset; a 2-row weight-1 set is not a 1-row weight-2 set."""
        t = {"truth_pt": np.array([0.0, -0.0, 0.3]), "truth_pz": np.array([2.0, 2.0, 3.0]),
             "w_prior": np.array([1.0, 1.0, 2.0])}
        d = {"truth_pt": np.array([-0.0, 0.3, 0.0]), "truth_pz": np.array([2.0, 3.0, 2.0]),
             "w_truth": np.array([1.0, 2.0, 1.0])}
        self.assertTrue(E.c_complete(t, d)["pass"])
        d1 = {"truth_pt": np.array([0.0, 0.3]), "truth_pz": np.array([2.0, 3.0]), "w_truth": np.array([2.0, 2.0])}
        self.assertFalse(E.c_complete(t, d1)["pass"])

    _maps = [0]

    def driver_map(self, num, den):
        """The driver's completeness: hOFInputTruth and hOFTruthDenom filled row by row, then Divide."""
        self._maps[0] += 1
        hn = DRIVER.make_th2d(f"cm_n{self._maps[0]}", "", DRIVER.PT_EDGES, DRIVER.PZ_EDGES)
        hd = DRIVER.make_th2d(f"cm_d{self._maps[0]}", "", DRIVER.PT_EDGES, DRIVER.PZ_EDGES)
        for h, rows, w in ((hn, num, "w_prior"), (hd, den, "w_truth")):
            for a, b, x in zip(rows["truth_pt"], rows["truth_pz"], rows[w]):
                h.Fill(a, b, x)
        hc = hn.Clone(f"cm_c{self._maps[0]}")
        hc.Divide(hd)
        return hc, hn, hd

    def cmap_rows(self, extra_num=(), extra_den=()):
        """One unit-weight row at the centre of every cell but (3, 3), plus rows added to cell (2, 2), as (num, den)."""
        pe, ze = np.array(DRIVER.PT_EDGES), np.array(DRIVER.PZ_EDGES)
        cells = [(ix, iy) for ix in range(14) for iy in range(16) if (ix, iy) != (2, 2)]
        base = [((pe[ix] + pe[ix + 1]) / 2, (ze[iy] + ze[iy + 1]) / 2, 1.0) for ix, iy in cells]
        c22 = ((pe[1] + pe[2]) / 2, (ze[1] + ze[2]) / 2)
        out = []
        for extra, w in ((extra_num, "w_prior"), (extra_den, "w_truth")):
            rows = base + [(*c22, x) for x in extra]
            out.append({"truth_pt": np.array([r[0] for r in rows]), "truth_pz": np.array([r[1] for r in rows]),
                        w: np.array([r[2] for r in rows])})
        return out

    def test_cmap(self):
        pe, ze = DRIVER.PT_EDGES, DRIVER.PZ_EDGES
        num, den = self.cmap_rows((1.0,), (1.0,))
        maps = self.driver_map(num, den)
        r = E.c_cmap(R, maps, pe, ze, num, den)
        self.assertEqual((r["kind"], r["pass"], r["max_dev"]), ("pass", True, 0.0))
        self.assertEqual(r["refill"], {"numerator": True, "denominator": True, "map": True})
        # equal multisets summed in two orders: a real fill-order miss, refilled exactly
        num, den = self.cmap_rows((1.0, 1e6, 1.3, -1e6), (1.0, 1e6, -1e6, 1.3))
        r = E.c_cmap(R, self.driver_map(num, den), pe, ze, num, den)
        self.assertTrue(E.CMAP_ATOL < r["max_dev"] <= E.CMAP_ROUNDING, r["max_dev"])
        self.assertEqual((r["kind"], r["pass"]), ("rounding", False))
        self.assertTrue(all(r["refill"].values()))
        hc, hn, hd = self.driver_map(num, den)
        hc.SetBinContent(0, 0.5)  # the same genuine miss, with a corrupted ratio in a flow bin: a STOP
        r = E.c_cmap(R, (hc, hn, hd), pe, ze, num, den)
        self.assertEqual((r["kind"], r["refill"]["map"]), ("stop", False))
        big_n, big_d = self.cmap_rows((1.0, 1e9, 1.3, -1e9), (1.0, 1e9, -1e9, 1.3))  # a fill-order miss above 1e-9
        r = E.c_cmap(R, self.driver_map(big_n, big_d), pe, ze, big_n, big_d)
        self.assertTrue(r["max_dev"] > E.CMAP_ROUNDING and all(r["refill"].values()), r)
        self.assertEqual(r["kind"], "stop")
        # the same miss with rows the driver did not fill: a STOP
        num2 = dict(num, w_prior=num["w_prior"] * (1 + 1e-15))
        r = E.c_cmap(R, self.driver_map(num, den), pe, ze, num2, den)
        self.assertEqual((r["kind"], r["refill"]["numerator"]), ("stop", False))
        den2 = dict(den, w_truth=den["w_truth"][::-1].copy())
        r = E.c_cmap(R, self.driver_map(num, den), pe, ze, num, den2)
        self.assertEqual((r["kind"], r["refill"]["denominator"]), ("stop", False))
        # a map error of rounding size on an exact map: a STOP (it is not the driver's summation)
        num, den = self.cmap_rows((1.0,), (1.0,))
        hc, hn, hd = self.driver_map(num, den)
        hc.SetBinContent(2, 2, 1.0 + 1.2e-12)
        r = E.c_cmap(R, (hc, hn, hd), pe, ze, num, den)
        self.assertTrue(E.CMAP_ATOL < r["max_dev"] <= E.CMAP_ROUNDING)
        self.assertEqual((r["kind"], r["refill"]["map"]), ("stop", False))
        hc.SetBinContent(2, 2, 1.0 + 1e-8)  # beyond rounding: a STOP
        self.assertEqual(E.c_cmap(R, (hc, hn, hd), pe, ze, num, den)["kind"], "stop")
        hc.SetBinContent(2, 2, 1.0)
        self.assertEqual((hd.GetBinContent(3, 3), hc.GetBinContent(3, 3)), (0.0, 0.0))  # the fixture's empty cell
        hc.SetBinContent(3, 3, 0.5)  # a zero-denominator cell must be 0, even with every positive cell exact: a STOP
        r = E.c_cmap(R, (hc, hn, hd), pe, ze, num, den)
        self.assertEqual((r["max_dev"], r["zero_cells_zero"], r["kind"]), (0.0, False, "stop"))

    def test_same_bits_needs_the_dtype(self):
        self.assertTrue(E.same_bits(np.array([1.5]), np.array([1.5])))
        self.assertFalse(E.same_bits(np.array([1.5], np.float32), np.array([1.5])))
        self.assertFalse(E.same_bits(np.array([0.0]), np.array([-0.0])))

    def test_exact_gate(self):
        ref = np.array([1.0, 2.0, 0.0])
        self.assertTrue(E.exact(ref * (1 + 0.9e-8) * np.array([1, 1, 0]), ref, 1e-8)["pass"])
        self.assertFalse(E.exact(ref * (1 + 2e-8), ref, 1e-8)["pass"])
        self.assertFalse(E.exact(np.array([1.0, 2.0, 1e-30]), ref, 1e-8)["pass"])
        self.assertFalse(E.exact(np.zeros(3), np.zeros(3), 1e-8)["pass"])
        self.assertFalse(E.exact(np.ones(2), ref, 1e-8)["pass"])

    def test_xsec_equals_the_drivers_extraction(self):
        """The fill and the formula against the driver's own TH2D fill and extract_cross_section_2d (unit
        completeness), bit for bit, with values on edges, outside the grid and a zero-flux pT bin."""
        rng = np.random.default_rng(5)
        n = 4000
        pt = np.concatenate([rng.uniform(0, 4.6, n), np.array(PAPER_PT, float), np.array(DRIVER.PT_EDGES, float)])
        pz = np.concatenate([rng.uniform(1.4, 61, n), rng.choice(np.array(DRIVER.PZ_EDGES, float), 30)])
        w = rng.uniform(0.1, 2.0, pt.size)
        flux = np.full(14, PHI)
        flux[3] = 0.0
        for edges in (DRIVER.PT_EDGES, PAPER_PT):
            hu = DRIVER.make_th2d("tu", "", edges, DRIVER.PZ_EDGES)
            for a, b, c in zip(pt, pz, w):
                hu.Fill(float(a), float(b), float(c))
            hc = DRIVER.make_th2d("tc", "", edges, DRIVER.PZ_EDGES)
            for ix in range(1, 15):
                for iy in range(1, 17):
                    hc.SetBinContent(ix, iy, 1.0)
            ref = R.th2_vector(DRIVER.extract_cross_section_2d(hu, hc, flux, 1.0e20, 3.2e30, edges, DRIVER.PZ_EDGES),
                               14, 16)
            mine = E.xsec_from_weights(pt, pz, w, edges, DRIVER.PZ_EDGES, flux, 1.0e20, 3.2e30, R.bin_index)
            self.assertTrue(E.same_bits(mine, ref), edges)
            self.assertTrue(np.all(ref[3 * 16:4 * 16] == 0))
            self.assertGreater(int((ref != 0).sum()), 150)
            allbins = np.array([hu.GetBinContent(b) for b in range(16 * 18)])
            self.assertTrue(E.same_bits(E.fill_root_bins(pt, pz, w, edges, DRIVER.PZ_EDGES), allbins))

    def test_event_level_completeness_equals_the_drivers(self):
        rng = np.random.default_rng(6)
        pt, pz, w = rng.uniform(0, 4.4, 3000), rng.uniform(1.5, 59, 3000), rng.uniform(0.2, 2, 3000)
        wp = rng.uniform(0.2, 2, 3000)
        den = {"truth_pt": np.append(pt, [3.0, 2.0]), "truth_pz": np.append(pz, [30.0, 50.0]),  # populated cells
               "w_truth": np.append(wp, [1.0, 1.5])}
        sig = {"truth_pt": pt, "truth_pz": pz, "pass_truth": np.ones(3000, bool), "w_truth": wp}
        hc, _, _ = DRIVER.compute_omnifold_completeness_2d(sig, DRIVER.PT_EDGES, DRIVER.PZ_EDGES, den)
        hu = DRIVER.make_th2d("tu2", "", DRIVER.PT_EDGES, DRIVER.PZ_EDGES)
        for a, b, c in zip(pt, pz, w):
            hu.Fill(float(a), float(b), float(c))
        flux = np.full(14, PHI)
        ref = R.th2_vector(DRIVER.extract_cross_section_2d(hu, hc, flux, 1e20, 3.2e30, DRIVER.PT_EDGES,
                                                           DRIVER.PZ_EDGES), 14, 16)
        mine = E.xsec_from_weights(pt, pz, w, DRIVER.PT_EDGES, DRIVER.PZ_EDGES, flux, 1e20, 3.2e30, R.bin_index,
                                   denom=den, w_input=wp)
        np.testing.assert_allclose(mine, ref, rtol=1e-15, atol=0)
        unit = E.xsec_from_weights(pt, pz, w, DRIVER.PT_EDGES, DRIVER.PZ_EDGES, flux, 1e20, 3.2e30, R.bin_index)
        self.assertFalse(E.exact(unit, ref, 1e-6)["pass"])

    def test_flux_count_must_match_the_bins(self):
        with self.assertRaises(E.GateFailure):
            E.xsec_from_weights(np.ones(1), np.ones(1) * 2, np.ones(1), DRIVER.PT_EDGES, DRIVER.PZ_EDGES,
                                np.ones(13), 1e20, 3e30, R.bin_index)


class Run(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = case()
        cls.rc, cls.out, cls.rec = cls.c.run()

    def test_clean_run_passes_every_control(self):
        self.assertEqual(self.rc, 0, json.dumps(self.rec["controls"], default=str)[:2000])
        self.assertEqual(self.rec["controls_verdict"], "PASS")
        self.assertEqual(self.c.done(self.out)["verdict"], "PASS")
        self.assertEqual(self.rec["findings"], [])
        self.assertEqual(self.rec["controls"]["C-CMAP"]["kind"], "pass")
        for k in ("C-KEY", "C-FLUX", "C-COMPLETE", "C-CMAP", "C-FILE", "C-FLOW", "C-SELF", "C-EXACT-ER",
                  "C-EXACT-PAPER", "C-REC", "C-PINS", "C-STAGE"):
            self.assertTrue(self.rec["controls"][k]["pass"], k)
        self.assertTrue(self.rec["controls"]["C-SELF"]["file_equals_driver"])  # the file is the driver's own hXSec2D
        self.assertEqual(set(self.rec["controls"]["C-REC"]["calls"]), set(E.SEAMS))
        self.assertFalse((self.out / "denominator.npz").exists())
        self.assertGreater(self.rec["controls"]["C-FLOW"]["hUnfold2D"]["flow_sum"], 0)  # top-edge rows are flow
        self.assertEqual(set(self.rec["phases_seconds"]), {"preflight", "driver", "key", "write", "controls",
                                                           "final_verify"})
        self.assertEqual(self.rec["controls"]["C-CMAP"]["refill"],
                         {"numerator": True, "denominator": True, "map": True})  # the refill is the driver's fill
        self.assertIn("acceptance", self.c.done(self.out)["phases_seconds"])
        self.assertEqual(set(self.rec["custody"]["files"]), {"weights.npz", "constants.json", "xsec.root"})
        self.assertGreater(self.rec["peak_rss_kb"], 0)

    def test_done_marker_is_last_and_covers_the_manifest(self):
        done = json.loads((self.out / "evw2d.done").read_text())
        self.assertEqual(done["verdict"], "PASS")
        self.assertTrue(done["acceptance"]["pass"])
        self.assertEqual(done["SHA256SUMS"], sha(self.out / "SHA256SUMS"))
        self.assertTrue(E.accepted(self.out)["pass"])
        names = {p.name for p in self.out.iterdir()}
        self.assertEqual(names, {"weights.npz", "constants.json", "xsec.root", "run.json", "SHA256SUMS", "evw2d.done"})
        self.assertGreaterEqual((self.out / "evw2d.done").stat().st_mtime_ns, (self.out / "SHA256SUMS").stat().st_mtime_ns)

    def test_the_file_is_the_driver_fill(self):
        z = E.read_npz(self.out / "weights.npz", E.WEIGHT_COLUMNS)[0]
        self.assertEqual(z["entry"].dtype, np.uint32)
        for k in E.WEIGHT_COLUMNS[1:]:
            self.assertEqual(z[k].dtype, np.float64, k)
        for name, col in (("hUnfold2D", "w_unfolded"), ("hTruth2D", "w_prior")):
            ref = E.own_hist(R, self.out / "xsec.root", name, DRIVER.PT_EDGES, DRIVER.PZ_EDGES, flow=True)
            mine = E.fill_root_bins(z["truth_pt"], z["truth_pz"], z[col], DRIVER.PT_EDGES, DRIVER.PZ_EDGES)
            self.assertTrue(E.same_bits(mine, ref), name)

    def test_rows_are_the_truth_passing_rows(self):
        z = E.read_npz(self.out / "weights.npz", E.WEIGHT_COLUMNS)[0]
        import ROOT
        f = ROOT.TFile.Open(str(self.c.stage / "omni.root"))
        sig = DRIVER.collect_signal_arrays_2d(f.Get("mc_signal_reco"), 0, 4.5, 1.5, 60.0, 0.25, use_weights=True)
        f.Close()
        self.assertEqual(z["entry"].size, int(sig["pass_truth"].sum()))
        cols = E.read_signal_tree(self.c.stage / "omni.root")
        self.assertTrue(E.same_bits(cols["MC"][z["entry"]], z["truth_pt"]))
        self.assertTrue(E.same_bits(cols["MC_pz"][z["entry"]], z["truth_pz"]))
        self.assertTrue(E.same_bits(cols["w_truth"][z["entry"]] * 0.25, z["w_prior"]))
        self.assertTrue(np.all(np.diff(z["entry"].astype(np.int64)) > 0))

    def test_meta_and_manifest(self):
        meta = E.read_npz(self.out / "weights.npz", E.WEIGHT_COLUMNS)[1]
        self.assertEqual(meta["schema"], E.SCHEMA)
        self.assertEqual(meta["key"]["omnifile_sha256"], self.c.cfg["inputs"]["CV_sha256"])
        self.assertEqual(meta["key"]["tree"], "mc_signal_reco")
        k = meta["constants"]
        self.assertEqual(len(k["flux_bins_m2_per_POT"]), 14)
        self.assertEqual(k["phi_m2_per_POT"], k["flux_bins_m2_per_POT"][0])
        self.assertIn("sum of the 14 copies", k["flux_note"])
        self.assertEqual((k["data_pot"], k["mc_pot"], k["pot_scale"]), (1.0e20, 4.0e20, 0.25))
        self.assertEqual(k["n_nucleons"], DRIVER.TRACKER_FIDUCIAL_N_NUCLEONS)
        self.assertIn("(pT, p||) only", k["validity"])
        self.assertEqual(k["validated_grids"]["paper"], [float(x) for x in PAPER_PT])
        self.assertEqual(meta["declaration_sha256"], self.c.cfg["declaration_sha256"])
        self.assertEqual(json.loads((self.out / "constants.json").read_text()), meta)
        sums = dict(reversed(line.split("  ")) for line in (self.out / "SHA256SUMS").read_text().splitlines())
        self.assertEqual(set(sums), {"weights.npz", "constants.json", "xsec.root", "run.json"})
        for name, d in sums.items():
            self.assertEqual(sha(self.out / name), d, name)

    def tampered_run(self, change):
        with tampered_write(change):
            rc, _, rec = self.c.run()
        self.assertEqual(rc, E.RC_CONTROL)
        return rec["controls"]

    def test_a_scaled_column_fails_the_exactness_tests(self):
        def scale(a, m):
            a["w_unfolded"] = a["w_unfolded"] * (1 + 3e-8)
            return a, m
        c = self.tampered_run(scale)
        for k in ("C-SELF", "C-EXACT-ER", "C-EXACT-PAPER", "C-FILE", "C-FLOW"):
            self.assertFalse(c[k]["pass"], k)
        self.assertTrue(c["C-KEY"]["pass"])

    def test_a_shifted_key_fails_c_file(self):
        def shift(a, m):
            a["entry"][5] = a["entry"][5] + 1 if a["entry"][5] + 1 != a["entry"][6] else a["entry"][5] - 1
            return a, m
        c = self.tampered_run(shift)
        self.assertFalse(c["C-FILE"]["pass"])
        self.assertFalse(c["C-FILE"]["entries"])
        for k in ("C-SELF", "C-EXACT-ER", "C-EXACT-PAPER", "C-FLOW"):  # the key changes no cell sum
            self.assertTrue(c[k]["pass"], k)

    def test_swapped_weights_in_one_cell_fail_c_file(self):
        """Two rows in the same cell on both grids exchange their unfolded weights: no cell sum moves."""
        def swap(a, m):
            g = (R.bin_index(a["truth_pt"], PAPER_PT) * 100 + R.bin_index(a["truth_pt"], DRIVER.PT_EDGES)) * 100 + \
                R.bin_index(a["truth_pz"], DRIVER.PZ_EDGES)
            ok = (R.bin_index(a["truth_pt"], DRIVER.PT_EDGES) >= 0) & (R.bin_index(a["truth_pz"], DRIVER.PZ_EDGES) >= 0)
            vals, counts = np.unique(g[ok], return_counts=True)
            cell = vals[np.argmax(counts)]
            i, j = np.flatnonzero(ok & (g == cell))[:2]
            a["w_unfolded"][[i, j]] = a["w_unfolded"][[j, i]]
            return a, m
        c = self.tampered_run(swap)
        self.assertFalse(c["C-FILE"]["w_unfolded"])
        for k in ("C-SELF", "C-EXACT-ER", "C-EXACT-PAPER"):
            self.assertTrue(c[k]["pass"], k)

    def test_a_changed_flow_row_fails_c_file_and_c_flow(self):
        def flow(a, m):
            i = int(np.flatnonzero(a["truth_pt"] == 4.5)[0])
            a["w_unfolded"][i] *= 2.0
            return a, m
        c = self.tampered_run(flow)
        self.assertFalse(c["C-FILE"]["pass"])
        self.assertFalse(c["C-FLOW"]["pass"])
        for k in ("C-SELF", "C-EXACT-ER", "C-EXACT-PAPER"):
            self.assertTrue(c[k]["pass"], k)

    def test_a_changed_truth_value_fails_c_file(self):
        def nudge(a, m):
            i = int(np.flatnonzero((a["truth_pt"] > 0.8) & (a["truth_pt"] < 0.84))[0])  # inside a cell on both grids
            a["truth_pt"][i] = np.nextafter(a["truth_pt"][i], 1.0)
            return a, m
        c = self.tampered_run(nudge)
        self.assertFalse(c["C-FILE"]["truth_pt"])
        self.assertFalse(c["C-FILE"]["pass"])
        for k in ("C-SELF", "C-EXACT-ER", "C-EXACT-PAPER", "C-FLOW"):
            self.assertTrue(c[k]["pass"], k)

    def test_a_wrong_dtype_fails_c_file(self):
        def widen(a, m):
            a["entry"] = a["entry"].astype(np.int64)
            return a, m
        c = self.tampered_run(widen)
        self.assertFalse(c["C-FILE"]["dtypes"])
        self.assertFalse(c["C-FILE"]["pass"])

    def test_a_changed_prior_on_a_flow_row_fails_c_flow(self):
        def prior(a, m):
            i = int(np.flatnonzero(a["truth_pz"] == 60.0)[0])
            a["w_prior"][i] *= 2.0
            return a, m
        c = self.tampered_run(prior)
        self.assertFalse(c["C-FLOW"]["hTruth2D"]["pass"])
        self.assertTrue(c["C-FLOW"]["hUnfold2D"]["pass"])

    def test_wrong_saved_constants_fail(self):
        def pot(a, m):
            m["constants"]["data_pot"] *= 1.001
            return a, m
        c = self.tampered_run(pot)
        self.assertFalse(c["C-FILE"]["meta"])
        for k in ("C-SELF", "C-EXACT-ER", "C-EXACT-PAPER"):  # rebuilt from the saved constants
            self.assertFalse(c[k]["pass"], k)

    def test_a_wrong_reference_fails_its_exactness_test(self):
        for key, ctl in (("er", "C-EXACT-ER"), ("paper", "C-EXACT-PAPER")):
            cfg = copy.deepcopy(self.c.cfg)
            with np.load(cfg["references"]["path"]) as z:
                refs = {k: z[k] for k in z.files}
            refs[key] = refs[key] * (1 + 2e-8)
            p = self.c.td / f"refs_{key}.npz"
            np.savez(p, **refs)
            cfg["references"] = {"path": str(p), "sha256": sha(p)}
            rc, _, rec = self.c.run(cfg)
            self.assertEqual(rc, E.RC_CONTROL, key)
            self.assertFalse(rec["controls"][ctl]["pass"], key)
            self.assertTrue(rec["controls"]["C-SELF"]["pass"], key)

    def test_reference_grids_are_enforced(self):
        for key, value in (("er_pt_edges", PAPER_PT), ("paper_pt_edges", DRIVER.PT_EDGES),
                           ("paper_pz_edges", list(DRIVER.PZ_EDGES[:-1]) + [61.0]), ("er_pz_edges", PAPER_PT + [5.0, 6.0])):
            cfg = copy.deepcopy(self.c.cfg)
            with np.load(cfg["references"]["path"]) as z:
                refs = {k: z[k] for k in z.files}
            refs[key] = np.array(value, float)
            p = self.c.td / f"refs_grid_{key}.npz"
            np.savez(p, **refs)
            cfg["references"] = {"path": str(p), "sha256": sha(p)}
            with self.assertRaises(E.GateFailure, msg=key):
                E.load_references(cfg, DRIVER)

    def test_refusals(self):
        out = self.c.out()
        out.mkdir()
        with self.assertRaises(E.GateFailure):
            E.run(self.c.cfg, out, R, DRIVER, OHF, {}, {}, config_sha256="0" * 64, started=0.0)  # the out dir exists
        cfg = copy.deepcopy(self.c.cfg)
        cfg["cpus"] = cfg["cpus"] + 1
        with self.assertRaises(E.GateFailure):
            E.run(cfg, self.c.out(), R, DRIVER, OHF, {}, {}, config_sha256="0" * 64, started=0.0)
        cfg = copy.deepcopy(self.c.cfg)
        cfg["thread_env"] = dict(cfg["thread_env"], OMP_NUM_THREADS="999")
        with self.assertRaises(E.GateFailure):
            E.run(cfg, self.c.out(), R, DRIVER, OHF, {}, {}, config_sha256="0" * 64, started=0.0)
        cfg = copy.deepcopy(self.c.cfg)
        cfg["references"]["sha256"] = "0" * 64
        with self.assertRaises(E.GateFailure):
            E.run(cfg, self.c.out(), R, DRIVER, OHF, {}, {}, config_sha256="0" * 64, started=0.0)

    def test_a_failed_key_fails_the_run_cleanly(self):
        real = E.keep_rule
        for change in (lambda d: d.update(w_reco=d["w_reco"] * (1 + 1e-12)),       # same rows, one value off
                       lambda d: d.update({k: v[1:] for k, v in d.items()})):     # one row short
            def off(cols, driver, pot_scale, bounds, change=change):
                d = real(cols, driver, pot_scale, bounds)
                change(d)
                return d
            with mock.patch.object(E, "keep_rule", off):
                rc, out, rec = self.c.run()
            self.assertEqual(rc, E.RC_CONTROL)
            self.assertFalse(rec["controls"]["C-KEY"]["pass"])
            self.assertEqual(rec["controls_verdict"], "FAIL")
            self.assertEqual(self.c.done(out)["verdict"], "FAIL")
            self.assertFalse((out / "weights.npz").exists())

    def test_a_failed_acceptance_fails_the_run(self):
        with mock.patch.object(E, "acceptance", lambda out, files: {"pass": False}):
            rc, out, rec = self.c.run()
        self.assertEqual(rc, E.RC_CONTROL)
        self.assertEqual(rec["controls_verdict"], "PASS")
        self.assertEqual(self.c.done(out)["verdict"], "FAIL")
        self.assertFalse(E.accepted(out)["pass"])

    def test_acceptance_needs_the_exact_product_set(self):
        rc, out, rec = self.c.run()
        files = rec["files_sha256"] | {"run.json": sha(out / "run.json")}
        b = ("evw2d.done",)
        self.assertTrue(E.acceptance(out, files, b)["pass"])
        self.assertFalse(E.acceptance(out, files)["present"])  # the marker is beside the products, not one of them
        self.assertFalse(E.acceptance(out, {k: v for k, v in files.items() if k != "constants.json"}, b)["pass"])
        (out / "stray.txt").write_text("x")
        self.assertFalse(E.acceptance(out, files, b)["present"])
        (out / "stray.txt").unlink()
        self.assertFalse(E.acceptance(out, dict(files, **{"run.json": "0" * 64}), b)["pass"])
        sums = (out / "SHA256SUMS").read_text()  # a manifest missing one line, every file intact
        (out / "SHA256SUMS").write_text("".join(x + "\n" for x in sums.splitlines() if "constants.json" not in x))
        r = E.acceptance(out, files, b)
        self.assertEqual((r["manifest"], r["names"], r["present"], r["rehash"]), (False, True, True, True))
        (out / "SHA256SUMS").write_text(sums)

    def test_the_done_marker_is_published_whole_or_not_at_all(self):
        d = Path(tempfile.mkdtemp(dir=LANE))
        with mock.patch.object(E.os, "replace", side_effect=OSError("crash")):
            with self.assertRaises(OSError):
                E.publish_done(d, {"verdict": "PASS"})
        self.assertFalse((d / "evw2d.done").exists())
        (d / ".evw2d.done.tmp").unlink()
        E.publish_done(d, {"verdict": "PASS"})
        self.assertEqual(json.loads((d / "evw2d.done").read_text()), {"verdict": "PASS"})
        self.assertEqual([p.name for p in d.iterdir()], ["evw2d.done"])

    def test_a_rounding_miss_in_the_map_takes_the_fallback_and_is_recorded(self):
        miss = {"max_dev": 3.0e-11, "cells_positive": 200, "zero_cells_zero": True, "kind": "rounding", "pass": False}
        with mock.patch.object(E, "c_cmap", lambda *a: dict(miss)):
            rc, out, rec = self.c.run()
        self.assertEqual(rc, 0, json.dumps(rec["controls"], default=str)[:1500])
        self.assertEqual(rec["findings"], ["C-CMAP"])
        self.assertEqual(rec["finding_sizes"], {"C-CMAP": 3.0e-11})
        self.assertEqual(self.c.done(out)["finding_sizes"], {"C-CMAP": 3.0e-11})
        self.assertTrue((out / "denominator.npz").exists())
        for k in ("C-CMAP-EVENT", "C-FILE", "C-SELF", "C-EXACT-ER", "C-EXACT-PAPER"):
            self.assertTrue(rec["controls"][k]["pass"], k)

    def test_any_other_map_failure_stops(self):
        stop = {"max_dev": 1e-6, "cells_positive": 200, "zero_cells_zero": True, "kind": "stop", "pass": False}
        with mock.patch.object(E, "c_cmap", lambda *a: dict(stop)):
            rc, out, rec = self.c.run()
        self.assertEqual(rc, E.RC_CONTROL)
        self.assertEqual(rec["findings"], [])
        self.assertFalse((out / "denominator.npz").exists())
        self.assertEqual(self.c.done(out)["verdict"], "FAIL")

    def test_a_replaced_staged_input_fails_c_stage(self):
        c = Case()
        real = R.run_driver

        def swap_after(*a, **k):
            cap = real(*a, **k)
            os.chmod(c.stage, 0o755)
            shutil.copy(c.stage / "omni.root", c.stage / "omni.new")
            os.replace(c.stage / "omni.new", c.stage / "omni.root")
            os.chmod(c.stage, 0o555)
            return cap
        with mock.patch.object(R, "run_driver", swap_after):
            rc, out, rec = c.run()
        self.assertEqual(rc, E.RC_CONTROL)
        self.assertFalse(rec["controls"]["C-STAGE"]["CV"]["same_file"])
        self.assertTrue(rec["controls"]["C-EXACT-ER"]["pass"])

    def test_a_cache_written_during_the_run_fails_c_pins(self):
        real = R.run_driver
        made = TREE / "2d-unfolding/re2/__pycache__"

        def cache_after(*a, **k):
            cap = real(*a, **k)
            made.mkdir()
            return cap
        try:
            with mock.patch.object(R, "run_driver", cache_after):
                rc, out, rec = self.c.run()
        finally:
            shutil.rmtree(made, ignore_errors=True)
        self.assertEqual(rc, E.RC_CONTROL)
        self.assertEqual(rec["controls"]["C-PINS"]["caches_after_run"], ["2d-unfolding/re2"])
        self.assertFalse(rec["controls"]["C-PINS"]["pass"])

    def test_a_tampered_constants_json_fails_c_file(self):
        real = E.write_constants

        def tamper(path, meta):
            meta = copy.deepcopy(meta)
            meta["constants"]["n_nucleons"] *= 2
            real(path, meta)
        with mock.patch.object(E, "write_constants", tamper):
            rc, _, rec = self.c.run()
        self.assertEqual(rc, E.RC_CONTROL)
        self.assertFalse(rec["controls"]["C-FILE"]["constants_json"])
        self.assertTrue(rec["controls"]["C-FILE"]["meta"])

    def test_products_changed_after_their_checks_fail_acceptance(self):
        import ROOT
        real = E.c_flow

        def change_after(back, R_, out, pte, pze):
            res = real(back, R_, out, pte, pze)
            (out / "constants.json").write_text((out / "constants.json").read_text().replace("\n", "\n ", 1))
            f = ROOT.TFile.Open(str(out / "xsec.root"), "UPDATE")
            ROOT.TNamed("evw2d_test", "x").Write()
            f.Close()
            return res
        with mock.patch.object(E, "c_flow", change_after):
            rc, out, rec = self.c.run()
        self.assertEqual(rc, E.RC_CONTROL)
        self.assertEqual(rec["controls_verdict"], "PASS")  # every control judged the bytes as they were
        self.assertNotEqual(rec["files_sha256"]["constants.json"], sha(out / "constants.json"))
        self.assertNotEqual(rec["files_sha256"]["xsec.root"], sha(out / "xsec.root"))
        done = self.c.done(out)
        self.assertEqual((done["verdict"], done["acceptance"]["rehash"]), ("FAIL", False))

    def test_a_replaced_driver_output_fails_acceptance(self):
        import ROOT
        real = E.keep_rule

        def replace_then_keep(*a, **k):  # during the independent read, a changed xsec.root takes the driver's place
            out = Path(self.c.td) / f"out{self.c.n}"
            f = ROOT.TFile.Open(str(out / "xsec.root"), "UPDATE")
            ROOT.TNamed("evw2d_stale", "x").Write()
            f.Close()
            return real(*a, **k)
        with mock.patch.object(E, "keep_rule", replace_then_keep):
            rc, out, rec = self.c.run()
        self.assertEqual(rc, E.RC_CONTROL)
        self.assertNotEqual(rec["files_sha256"]["xsec.root"], sha(out / "xsec.root"))  # the driver's own digest
        self.assertEqual(self.c.done(out)["acceptance"]["rehash"], False)

    def test_a_driver_output_replaced_before_it_returns_fails_c_self(self):
        import ROOT
        real = R.run_driver

        def stale_copy(*a, **k):  # a changed xsec.root lands before the driver returns: hashed as if the driver's
            cap = real(*a, **k)
            f = ROOT.TFile.Open(str(a[3]), "UPDATE")
            h = f.Get("hXSec2D")
            b = next(b for b in range(h.GetNcells()) if h.GetBinContent(b) != 0)
            h.SetBinContent(b, h.GetBinContent(b) * (1 + 1e-12))  # well within C-SELF's tolerance
            h.Write("", ROOT.TObject.kOverwrite)
            f.Close()
            return cap
        with mock.patch.object(R, "run_driver", stale_copy):
            rc, out, rec = self.c.run()
        self.assertEqual(rc, E.RC_CONTROL)
        self.assertFalse(rec["controls"]["C-SELF"]["file_equals_driver"])
        self.assertLessEqual(rec["controls"]["C-SELF"]["max_rel"], E.EXACT_RTOL)  # the tolerance alone would pass
        self.assertTrue(rec["controls"]["C-EXACT-ER"]["pass"])

    def test_the_exactness_tests_use_the_saved_grids(self):
        real = E.write_npz

        def tamper(path, arrays, meta):
            if path.name == "weights.npz":
                meta = copy.deepcopy(meta)
                meta["constants"]["analysis_pt_edges"][1] = 0.075  # the paper's edge, saved as ours
            return real(path, arrays, meta)
        with mock.patch.object(E, "write_npz", tamper):
            rc, _, rec = self.c.run()
        self.assertEqual(rc, E.RC_CONTROL)
        self.assertFalse(rec["controls"]["C-FILE"]["meta"])
        self.assertFalse(rec["controls"]["C-EXACT-ER"]["pass"])  # judged on the grid the file carries

    def test_a_name_swapped_and_restored_cannot_feed_the_independent_read(self):
        c = Case()
        sub = c.td / "substitute.root"
        write_omnifile(sub, seed=12)
        real_run, real_keep = R.run_driver, E.keep_rule

        def swapped(*a, **k):  # the driver reads another file under the name
            os.chmod(c.stage, 0o755)
            os.rename(c.stage / "omni.root", c.td / "omni.verified")
            shutil.copy(sub, c.stage / "omni.root")
            os.chmod(c.stage, 0o555)
            return real_run(*a, **k)

        def restored(*a, **k):  # the verified file is back under its name before anything checks it
            os.chmod(c.stage, 0o755)
            os.replace(c.td / "omni.verified", c.stage / "omni.root")
            os.chmod(c.stage, 0o555)
            return real_keep(*a, **k)
        with mock.patch.object(R, "run_driver", swapped), mock.patch.object(E, "keep_rule", restored):
            rc, out, rec = c.run()
        self.assertEqual(rc, E.RC_CONTROL)
        self.assertFalse(rec["controls"]["C-KEY"]["pass"])  # the independent read saw the verified file
        self.assertEqual(E.identity(c.stage / "omni.root"), c.verified["CV"]["identity"])

    def test_a_mutated_recording_fails_the_run(self):
        real = E.Recorder.verify

        def mutate(self_, names):
            self_.calls["omnifold"]["out"][1][0] += 1.0
            return real(self_, names)
        with mock.patch.object(E.Recorder, "verify", mutate):
            rc, _, rec = self.c.run()
        self.assertEqual(rc, E.RC_CONTROL)
        self.assertFalse(rec["controls"]["C-REC"]["pass"])

    def test_unequal_flux_fails_the_run(self):
        c = case("ramp", flux=[1e-3 * i for i in range(1, 15)])
        rc, out, rec = c.run()
        self.assertEqual(rc, E.RC_CONTROL)
        self.assertFalse(rec["controls"]["C-FLUX"]["pass"])
        for k in ("C-SELF", "C-EXACT-ER", "C-EXACT-PAPER"):  # the exactness tests apply the 14 values by index
            self.assertTrue(rec["controls"][k]["pass"], k)
        k = json.loads((out / "constants.json").read_text())["constants"]
        self.assertNotIn("phi_m2_per_POT", k)
        self.assertIn("no scalar", k["flux_note"])


class Fallback(unittest.TestCase):
    """C-COMPLETE fails: the declared fallback (the denominator table, event-level completeness) and a finding."""

    @classmethod
    def setUpClass(cls):
        cls.c = case("extra", denom_extra=True)
        cls.rc, cls.out, cls.rec = cls.c.run()

    def test_fallback_is_taken_and_reported(self):
        self.assertEqual(self.rc, 0, json.dumps(self.rec["controls"], default=str)[:2000])
        self.assertEqual(self.rec["findings"], ["C-COMPLETE"])
        self.assertFalse(self.rec["controls"]["C-COMPLETE"]["pass"])
        self.assertNotIn("C-CMAP", self.rec["controls"])
        self.assertTrue((self.out / "denominator.npz").exists())
        for k in ("C-SELF", "C-EXACT-ER", "C-EXACT-PAPER", "C-KEY", "C-REC", "C-FLUX", "C-FILE", "C-FLOW", "C-PINS"):
            self.assertTrue(self.rec["controls"][k]["pass"], k)
        meta = json.loads((self.out / "constants.json").read_text())
        self.assertIn("event-level", meta["constants"]["completeness"])
        self.assertIn("denominator.npz", (self.out / "SHA256SUMS").read_text())
        self.assertEqual(json.loads((self.out / "evw2d.done").read_text())["findings"], ["C-COMPLETE"])

    def test_the_finding_is_printed(self):
        import io
        from contextlib import redirect_stderr
        buf = io.StringIO()
        with redirect_stderr(buf):
            self.c.run()
        self.assertIn("FINDING: C-COMPLETE", buf.getvalue())

    def test_a_tampered_denominator_fails_c_file(self):
        real = E.write_npz

        def tamper(path, arrays, meta):
            if path.name == "denominator.npz":
                arrays = {k: np.array(v, copy=True) for k, v in arrays.items()}
                i = int(np.flatnonzero(arrays["truth_pt"] == 4.5)[0])  # an overflow row: no cell moves
                arrays["w_truth"][i] *= 3.0
            return real(path, arrays, meta)
        with mock.patch.object(E, "write_npz", tamper):
            rc, _, rec = self.c.run()
        self.assertEqual(rc, E.RC_CONTROL)
        self.assertFalse(rec["controls"]["C-FILE"]["denominator"])
        for k in ("C-SELF", "C-EXACT-ER", "C-EXACT-PAPER"):
            self.assertTrue(rec["controls"][k]["pass"], k)

    def test_a_wrong_denominator_meta_fails_c_file(self):
        real = E.write_npz

        def tamper(path, arrays, meta):
            if path.name == "denominator.npz":
                meta = dict(meta, table="something else")
            return real(path, arrays, meta)
        with mock.patch.object(E, "write_npz", tamper):
            rc, _, rec = self.c.run()
        self.assertEqual(rc, E.RC_CONTROL)
        self.assertFalse(rec["controls"]["C-FILE"]["denominator_meta"])
        self.assertTrue(rec["controls"]["C-FILE"]["denominator"])

    def test_the_exactness_tests_use_the_saved_completeness_selector(self):
        real = E.write_npz

        def tamper(path, arrays, meta):
            if path.name == "weights.npz":
                meta = copy.deepcopy(meta)
                meta["constants"]["completeness"] = "1 on every cell"  # the fallback no longer declared in the file
            return real(path, arrays, meta)
        with mock.patch.object(E, "write_npz", tamper):
            rc, _, rec = self.c.run()
        self.assertEqual(rc, E.RC_CONTROL)
        self.assertFalse(rec["controls"]["C-FILE"]["fallback_declared"])
        self.assertFalse(rec["controls"]["C-EXACT-ER"]["pass"])  # c = 1 from the file's selector misses the extra row

    def test_accepted_needs_the_fallback_with_findings(self):
        self.assertTrue(E.accepted(self.out)["pass"])
        d = Path(tempfile.mkdtemp(dir=LANE)) / "copy"
        shutil.copytree(self.out, d)
        for f in d.iterdir():
            f.chmod(0o644)
        (d / "denominator.npz").unlink()  # the fallback and its manifest line removed, the marker re-pointed
        sums = "".join(x + "\n" for x in (d / "SHA256SUMS").read_text().splitlines() if "denominator.npz" not in x)
        (d / "SHA256SUMS").write_text(sums)
        done = json.loads((d / "evw2d.done").read_text())
        done["SHA256SUMS"] = sha(d / "SHA256SUMS")
        (d / "evw2d.done").write_text(json.dumps(done))
        r = E.accepted(d)
        self.assertTrue(r["acceptance"]["pass"])
        self.assertEqual((r["fallback_matches_findings"], r["pass"]), (False, False))

    def test_the_rebuilt_map_equals_the_drivers(self):
        self.assertTrue(self.rec["controls"]["C-CMAP-EVENT"]["pass"])

    def test_unit_completeness_would_not_reproduce(self):
        z, meta = E.read_npz(self.out / "weights.npz", E.WEIGHT_COLUMNS)
        with np.load(self.c.cfg["references"]["path"]) as r:
            ref = r["er"]
        k = meta["constants"]
        unit = E.xsec_from_weights(z["truth_pt"], z["truth_pz"], z["w_unfolded"], DRIVER.PT_EDGES, DRIVER.PZ_EDGES,
                                   k["flux_bins_m2_per_POT"], k["data_pot"], k["n_nucleons"], R.bin_index)
        self.assertFalse(E.exact(unit, ref, 1e-8)["pass"])


class Refusals(unittest.TestCase):
    def test_step2_length_must_match_the_truth_rows(self):
        call = {"args": (np.zeros((3, 2)), None, None, None, np.array([True, True, False])),
                "kwargs": {"MCgen_weights": np.ones(3)}, "out": (np.ones(1), np.ones(3))}
        with self.assertRaises(E.GateFailure):
            E.weight_table({"entry": np.arange(3)}, call)

    def test_read_npz_refuses_other_columns(self):
        p = Path(tempfile.mkdtemp(dir=LANE)) / "w.npz"
        E.write_npz(p, {k: np.zeros(2) for k in E.WEIGHT_COLUMNS[:-1]}, {})
        with self.assertRaises(E.GateFailure):
            E.read_npz(p, E.WEIGHT_COLUMNS)
        with self.assertRaises(FileExistsError):
            E.write_npz(p, {}, {})

    def test_a_staged_path_outside_the_root_refuses(self):
        cfg = copy.deepcopy(BASE)
        cfg["inputs"]["staging"].update(root=str(LANE / "stage_x"), CV="../escape.root", MC="b.root")
        with self.assertRaises(E.GateFailure):
            E.check_staged(cfg, R)

    def main_cfg(self):
        td = Path(tempfile.mkdtemp(dir=LANE))
        (td / "a.root").write_bytes(b"a")
        (td / "b.root").write_bytes(b"b")
        cfg = bound(BASE, LANE_ROOT)
        cfg["inputs"].update(CV_source=str(td / "a.root"), CV_sha256=sha(td / "a.root"),
                             MC_source=str(td / "b.root"), MC_sha256=sha(td / "b.root"))
        cfg["inputs"]["staging"].update(root=str(td / "stage"), CV="a.root", MC="b.root")
        return td, cfg

    def listing(self, d):
        return sorted(x.name for x in d.iterdir())

    def test_main_stages_once_through_partial_names(self):
        td, cfg = self.main_cfg()
        with as_main(cfg) as m:
            self.assertEqual(m("stage"), 0)
            self.assertEqual(m("stage"), E.RC_GATE)  # the copies exist
        self.assertEqual((td / "stage" / "a.root").read_bytes(), b"a")
        self.assertFalse(os.access(td / "stage" / "a.root", os.W_OK))
        self.assertEqual(os.stat(td / "stage").st_mode & 0o777, 0o555)
        self.assertEqual(self.listing(td / "stage"), ["a.root", "b.root"])

    def test_a_failed_stage_leaves_no_file(self):
        td, cfg = self.main_cfg()
        cfg["inputs"]["MC_sha256"] = "0" * 64
        with as_main(cfg) as m:
            self.assertEqual(m("stage"), E.RC_GATE)
        self.assertEqual(self.listing(td / "stage"), ["a.root"])  # no b.root, no partial

    def test_a_partial_another_invocation_created_stays(self):
        td, cfg = self.main_cfg()
        real, made = R.copy_noatime, []

        def other_first(src, dest):  # another invocation takes the partial name first
            dest.write_bytes(b"theirs")
            made.append(dest)
            return real(src, dest)
        with mock.patch.object(R, "copy_noatime", other_first):
            with self.assertRaisesRegex(E.GateFailure, "another invocation"):
                E.stage(cfg, R)
        self.assertEqual(made[0].read_bytes(), b"theirs")
        self.assertIn(socket.gethostname(), made[0].name)

    def test_a_stale_partial_or_link_refuses_and_stays(self):
        td, cfg = self.main_cfg()
        (td / "stage").mkdir()
        (td / "stage" / "b.root.partial.1").write_bytes(b"x")
        with as_main(cfg) as m:
            self.assertEqual(m("stage"), E.RC_GATE)
        self.assertEqual((td / "stage" / "b.root.partial.1").read_bytes(), b"x")
        self.assertFalse((td / "stage" / "b.root").exists())
        (td / "stage" / "b.root.partial.1").unlink()
        (td / "stage" / "a.root").unlink()
        os.symlink(td / "nowhere", td / "stage" / "a.root")
        with self.assertRaises(E.GateFailure):
            E.stage(cfg, R)

    def test_main_refuses_a_driver_tree_off_the_pinned_commit(self):
        td, cfg = self.main_cfg()
        cfg["driver_tree"]["commit"] = "0" * 40
        with as_main(cfg) as m:
            self.assertEqual(m("stage"), E.RC_GATE)
        self.assertFalse((td / "stage").exists())  # refused before staging

    def test_main_refuses_without_a_binding(self):
        td, cfg = self.main_cfg()
        cfg["declaration_sha256"] = None
        with as_main(cfg) as m:
            self.assertEqual(m("stage"), E.RC_GATE)
        self.assertFalse((td / "stage").exists())  # nothing was created

    def test_main_needs_python_b(self):
        """Refused before any import: a loader reached with bytecode on would write a cache into the pinned tree."""
        td, cfg = self.main_cfg()

        def never(*a, **k):
            raise AssertionError("main() reached the import without python -B")
        with as_main(cfg) as m, mock.patch.object(sys, "dont_write_bytecode", False), \
                mock.patch.object(E, "load_runner", never), mock.patch.object(E, "check_tree", never):
            self.assertEqual(m("stage"), E.RC_GATE)
        self.assertFalse((td / "stage").exists())

    def test_main_catches_the_runners_own_refusal(self):
        td, cfg = self.main_cfg()
        with as_main(cfg) as m:
            self.assertEqual(m("stage"), 0)

        def refuse(*a, **k):  # the class of the ref_c2c1 module main() itself loaded
            raise sys.modules["ref_c2c1"].GateFailure("the runner refused")
        with as_main(cfg) as m, mock.patch.object(E, "check_staged", refuse):
            self.assertEqual(m("run", "--out", str(LANE / "never_out")), E.RC_GATE)
        self.assertFalse((LANE / "never_out").exists())

    def test_main_run_needs_the_allocation(self):
        import io
        from contextlib import redirect_stderr
        td, cfg = self.main_cfg()
        with as_main(cfg) as m:
            self.assertEqual(m("stage"), 0)

        def never(*a, **k):
            raise AssertionError("main() ran without an allocation")
        buf = io.StringIO()
        no_slurm = {k: v for k, v in os.environ.items() if not k.startswith("SLURM_")}
        with as_main(cfg, env={}) as m, mock.patch.dict(os.environ, no_slurm, clear=True), \
                mock.patch.object(E, "check_staged", never), redirect_stderr(buf):
            self.assertEqual(m("run", "--out", str(LANE / "never_out2")), E.RC_GATE)
        self.assertIn("srun step", buf.getvalue())
        self.assertFalse((LANE / "never_out2").exists())

    def test_main_refuses_preloaded_modules(self):
        td, cfg = self.main_cfg()
        with as_main(cfg) as m, mock.patch.dict(sys.modules, {"omnifold": mock.Mock()}):
            self.assertEqual(m("stage"), E.RC_GATE)
        self.assertFalse((td / "stage").exists())


class Staging(unittest.TestCase):
    def test_stage_copies_checks_and_refuses(self):
        td = Path(tempfile.mkdtemp(dir=LANE))
        src = td / "src"
        src.mkdir()
        (src / "a.root").write_bytes(b"omnifile")
        (src / "b.root").write_bytes(b"flux")
        cfg = copy.deepcopy(BASE)
        cfg["inputs"].update(CV_source=str(src / "a.root"), CV_sha256=sha(src / "a.root"),
                             MC_source=str(src / "b.root"), MC_sha256=sha(src / "b.root"))
        cfg["inputs"]["staging"].update(root=str(td / "stage"), CV="a.root", MC="b.root")
        got = E.stage(cfg, R)
        self.assertEqual(got["CV"]["sha256"], sha(src / "a.root"))
        self.assertEqual((td / "stage" / "b.root").read_bytes(), b"flux")
        v = E.check_staged(cfg, R)
        self.assertEqual({k: x["sha256"] for k, x in v.items()}, {"CV": sha(src / "a.root"), "MC": sha(src / "b.root")})
        self.assertTrue(E.c_stage(cfg, R, v)["pass"])
        with self.assertRaises(E.GateFailure):
            E.stage(cfg, R)  # the copies exist
        cfg2 = copy.deepcopy(cfg)
        cfg2["inputs"]["MC_sha256"] = "0" * 64
        with self.assertRaises(E.GateFailure):
            E.check_staged(cfg2, R)
        cfg3 = copy.deepcopy(cfg)
        cfg3["inputs"]["staging"]["root"] = str(td / "stage3")
        cfg3["inputs"]["CV_sha256"] = "0" * 64
        with self.assertRaises(E.GateFailure):
            E.stage(cfg3, R)
        self.assertEqual(list((td / "stage3").iterdir()), [])

    def test_c_stage_sees_a_replaced_name_and_a_writable_root(self):
        td = Path(tempfile.mkdtemp(dir=LANE))
        (td / "a.root").write_bytes(b"omnifile")
        (td / "b.root").write_bytes(b"flux")
        cfg = copy.deepcopy(BASE)
        cfg["inputs"].update(CV_source=str(td / "a.root"), CV_sha256=sha(td / "a.root"),
                             MC_source=str(td / "b.root"), MC_sha256=sha(td / "b.root"))
        cfg["inputs"]["staging"].update(root=str(td / "stage"), CV="a.root", MC="b.root")
        E.stage(cfg, R)
        v = E.check_staged(cfg, R)
        os.chmod(td / "stage", 0o755)
        self.assertFalse(E.c_stage(cfg, R, v)["root_read_only"])
        shutil.copy(td / "stage" / "a.root", td / "stage" / "a.new")
        os.replace(td / "stage" / "a.new", td / "stage" / "a.root")  # same bytes, a new file under the name
        os.chmod(td / "stage", 0o555)
        r = E.c_stage(cfg, R, v)
        self.assertFalse(r["CV"]["same_file"])
        self.assertTrue(r["CV"]["sha256_again"])
        self.assertFalse(r["pass"])

    def test_a_file_replaced_at_open_refuses(self):
        td = Path(tempfile.mkdtemp(dir=LANE))
        (td / "a.root").write_bytes(b"omnifile")
        (td / "b.root").write_bytes(b"flux")
        (td / "other").write_bytes(b"omnifile")
        cfg = copy.deepcopy(BASE)
        cfg["inputs"].update(CV_source=str(td / "a.root"), CV_sha256=sha(td / "a.root"),
                             MC_source=str(td / "b.root"), MC_sha256=sha(td / "b.root"))
        cfg["inputs"]["staging"].update(root=str(td / "stage"), CV="a.root", MC="b.root")
        E.stage(cfg, R)
        real = R.open_noatime
        with mock.patch.object(R, "open_noatime", lambda path: real(td / "other")):  # same bytes, another file
            with self.assertRaisesRegex(E.GateFailure, "replaced while it was opened"):
                E.check_staged(cfg, R)

    def test_a_staged_name_that_is_a_link_refuses(self):
        td = Path(tempfile.mkdtemp(dir=LANE))
        (td / "a.root").write_bytes(b"omnifile")
        (td / "b.root").write_bytes(b"flux")
        cfg = copy.deepcopy(BASE)
        cfg["inputs"].update(CV_source=str(td / "a.root"), CV_sha256=sha(td / "a.root"),
                             MC_source=str(td / "b.root"), MC_sha256=sha(td / "b.root"))
        cfg["inputs"]["staging"].update(root=str(td / "stage"), CV="a.root", MC="b.root")
        E.stage(cfg, R)
        os.chmod(td / "stage", 0o755)
        os.rename(td / "stage" / "a.root", td / "stage" / "a.real")
        os.symlink(td / "stage" / "a.real", td / "stage" / "a.root")  # in the root, the pinned bytes, but a link
        with self.assertRaisesRegex(E.GateFailure, "not a plain file"):
            E.check_staged(cfg, R)

    def test_unbound_staging_refuses(self):
        cfg = copy.deepcopy(BASE)   # the shipped config.json is bound from the binding commit on: unbind it here
        cfg["inputs"]["staging"]["root"] = None
        with self.assertRaises(E.GateFailure):
            E.staged(cfg)

    def test_main_runs_end_to_end_and_cleans_up(self):
        c = Case()  # its own fixture: cleanup deletes its staged copies
        out = c.td / "main_out"
        import io
        from contextlib import redirect_stderr
        with as_main(c.cfg) as m:  # each command in-process, with the driver tree's modules loaded afresh
            self.assertEqual(m("run", "--out", str(out)), 0)
        rec = json.loads((out / "run.json").read_text())
        self.assertEqual(rec["driver_tree"]["code_sha256"], BASE["driver_tree"]["code_sha256"])
        self.assertEqual(rec["inputs_sha256"], {"CV": c.cfg["inputs"]["CV_sha256"], "MC": c.cfg["inputs"]["MC_sha256"]})
        self.assertEqual(rec["slurm_job"], "77")
        self.assertIn("preflight", rec["phases_seconds"])
        self.assertEqual(len(rec["config_sha256"]), 64)
        buf = io.StringIO()
        with as_main(c.cfg) as m, redirect_stderr(buf):
            self.assertEqual(m("run", "--out", str(out)), E.RC_GATE)
        self.assertIn("exists", buf.getvalue())
        self.assertTrue(E.accepted(out)["pass"])
        real_identity = E.identity
        with as_main(c.cfg) as m, mock.patch.object(E, "identity", lambda p: dict(real_identity(p), dev=-7)):
            self.assertEqual(m("cleanup", "--out", str(out)), 0)  # another node numbers the filesystem differently
        self.assertFalse((c.stage / "omni.root").exists())
        self.assertFalse((c.stage / "flux.root").exists())
        rows = (LANE_ROOT / "deletions.tsv").read_text().splitlines()
        self.assertTrue(any(str(c.stage / "omni.root") in r and c.cfg["inputs"]["CV_sha256"] in r for r in rows))
        self.assertEqual(os.stat(c.stage).st_mode & 0o777, 0o555)

    def test_cleanup_checks_the_binding_the_files_and_the_ledger_first(self):
        c = Case()  # its own fixture: its staged copies are touched
        rc, out, _ = c.run()
        self.assertEqual(rc, 0)
        files = (c.stage / "omni.root", c.stage / "flux.root")
        with self.assertRaisesRegex(E.GateFailure, "bound to config"):
            E.cleanup(c.cfg, out, R, "0" * 64)
        lane = Path(tempfile.mkdtemp(dir=LANE))
        target = Path(tempfile.mkdtemp(dir=LANE)) / "pinned.txt"
        target.write_text("pinned")
        os.symlink(target, lane / "deletions.tsv")
        with self.assertRaises(OSError):  # the ledger is never written through a link
            E.cleanup(dict(c.cfg, lane_root=str(lane)), out, R, c.cfg_sha)
        self.assertEqual(target.read_text(), "pinned")
        lane2 = Path(tempfile.mkdtemp(dir=LANE))
        os.link(target, lane2 / "deletions.tsv")  # a hard link: O_NOFOLLOW alone would append to the target
        with self.assertRaisesRegex(E.GateFailure, "singly linked"):
            E.cleanup(dict(c.cfg, lane_root=str(lane2)), out, R, c.cfg_sha)
        self.assertEqual(target.read_text(), "pinned")
        self.assertTrue(all(f.exists() for f in files))
        os.chmod(c.stage, 0o755)
        os.rename(files[0], c.stage / "omni.real")
        os.symlink(c.stage / "omni.real", files[0])  # a link to the very file the run verified
        with self.assertRaisesRegex(E.GateFailure, "not the file the accepted run verified"):
            E.cleanup(c.cfg, out, R, c.cfg_sha)
        files[0].unlink()
        os.rename(c.stage / "omni.real", files[0])
        shutil.copy(files[0], c.stage / "omni.new")
        os.replace(c.stage / "omni.new", files[0])  # the same bytes, another file
        os.chmod(c.stage, 0o555)
        with self.assertRaisesRegex(E.GateFailure, "not the file the accepted run verified"):
            E.cleanup(c.cfg, out, R, c.cfg_sha)
        self.assertTrue(all(f.exists() for f in files))

    def test_cleanup_refuses_an_unaccepted_product(self):
        c = case()
        rc, out, _ = c.run()
        self.assertEqual(rc, 0)
        (out / "run.json").chmod(0o644)
        with open(out / "run.json", "a") as fh:
            fh.write(" ")
        self.assertFalse(E.accepted(out)["pass"])
        with self.assertRaises(E.GateFailure):
            E.cleanup(c.cfg, out, R, c.cfg_sha)
        self.assertTrue((c.stage / "omni.root").exists())


class References(unittest.TestCase):
    """The committed references.npz against the committed Tier 1 products."""

    @classmethod
    def setUpClass(cls):
        cls.refs = E.load_references(BASE, DRIVER)

    def hx(self, d):
        import ROOT
        f = ROOT.TFile.Open(str(TIER1 / d / "er.root"))
        h = f.Get("hXSec2D")
        v = R.th2_vector(h, 14, 16)
        pt = [h.GetXaxis().GetBinLowEdge(i) for i in range(1, 16)]
        pz = [h.GetYaxis().GetBinLowEdge(i) for i in range(1, 18)]
        f.Close()
        return v, pt, pz

    def test_paper_reference_is_tier1s_e_bitwise(self):
        v, pt, pz = self.hx("e")
        self.assertTrue(E.same_bits(self.refs["paper"], v))
        self.assertEqual(self.refs["paper_pt_edges"].tolist(), pt)
        self.assertEqual(self.refs["paper_pz_edges"].tolist(), pz)
        self.assertEqual(pt, [float(x) for x in BASE["paper_pt_edges"]])
        self.assertEqual(pz, [float(x) for x in DRIVER.PZ_EDGES])

    def test_er_reference_agrees_with_tier1s_old_reproduction(self):
        v, pt, pz = self.hx("old")
        self.assertTrue(E.exact(v, self.refs["er"], 1e-8)["pass"])
        self.assertEqual(self.refs["er_pt_edges"].tolist(), pt)
        self.assertEqual(self.refs["er_pz_edges"].tolist(), pz)
        self.assertEqual(pt, [float(x) for x in DRIVER.PT_EDGES])

    def test_meta_names_e_rs_digest(self):
        meta = json.loads(str(self.refs["meta"]))
        self.assertEqual(meta["er"]["sha256"], "a5c13fc38d64242bc9ee459fac87568a2f97fddf7a3ac97cc6f91eb4c2a31cef")
        self.assertEqual(meta["paper"]["sha256"], sha(TIER1 / "e" / "er.root"))

    def test_a_reference_with_a_missing_key_or_wrong_dtype_refuses(self):
        with np.load(REPO / BASE["references"]["path"]) as z:
            refs = {k: z[k] for k in z.files}
        for change in (lambda r: r.pop("paper"), lambda r: r.update(er=r["er"].astype(np.float32)),
                       lambda r: r.update(er_pt_edges=r["er_pt_edges"].astype(np.float32))):
            r = dict(refs)
            change(r)
            p = Path(tempfile.mkdtemp(dir=LANE)) / "r.npz"
            np.savez(p, **r)
            cfg = copy.deepcopy(BASE)
            cfg["references"] = {"path": str(p), "sha256": sha(p)}
            with self.assertRaises(E.GateFailure):
                E.load_references(cfg, DRIVER)

    def test_the_builder_refuses_nersc_storage(self):
        import importlib.util as iu
        spec = iu.spec_from_file_location("make_references", HERE / "make_references.py")
        mr = iu.module_from_spec(spec)
        spec.loader.exec_module(mr)
        out = Path(tempfile.mkdtemp(dir=LANE)) / "r.npz"
        for p in ("/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb/out/ER/xsec.root", "/global/cfs/x.root"):
            self.assertEqual(mr.main([p, str(out)]), 2)
        with mock.patch.object(mr, "REPO", Path("/global/cfs/cdirs/repo")):  # the paper's source on NERSC storage
            self.assertEqual(mr.main([str(out.parent / "er.root"), str(out)]), 2)
        with self.assertRaises(SystemExit):
            mr.hxsec(Path("/pscratch/x.root"), "0" * 64)
        self.assertFalse(out.exists())

    def test_the_references_judged_are_the_bytes_hashed(self):
        p = Path(tempfile.mkdtemp(dir=LANE)) / "references.npz"
        shutil.copy(REPO / BASE["references"]["path"], p)
        cfg = copy.deepcopy(BASE)
        cfg["references"] = {"path": str(p), "sha256": sha(p)}
        with np.load(p) as z:
            orig = {k: z[k] for k in z.files}
        real = np.load

        def replace_then_load(f, *a, **k):  # a lasting replacement lands just after the bytes are read
            if p.exists() and sha(p) == cfg["references"]["sha256"]:
                tmp = p.with_name("r.tmp.npz")
                np.savez(tmp, **dict(orig, er=orig["er"] * 2))
                os.replace(tmp, p)
            return real(f, *a, **k)
        with mock.patch.object(E.np, "load", replace_then_load):
            refs = E.load_references(cfg, DRIVER)
        self.assertTrue(np.array_equal(refs["er"], orig["er"]))

    def test_a_tampered_reference_refuses(self):
        cfg = copy.deepcopy(BASE)
        cfg["references"] = dict(cfg["references"], sha256="0" * 64)
        with self.assertRaises(E.GateFailure):
            E.load_references(cfg, DRIVER)


if __name__ == "__main__":
    unittest.main()
