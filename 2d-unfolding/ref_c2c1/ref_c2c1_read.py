#!/usr/bin/env python3
"""REF-C2C1 reader: the reported cells, then the controls and the readings C2-R1, C2-R2, C1-R1, C1-R2 (frozen;
REF-C2C1-DECLARATION.md §1.0-§2.4, REF-C2C1-BINDING-1.md).

  cells --out DIR/cells.root
        The 205 reported cells, materialised from the bound precision ROOT by the receipt's rule ("positive diagonal of
        StatOnlyCovariance on the paper's 224-bin global grid") and written as reported_cells.IDENTITY_HIST. The file
        is committed with its sha256 before the run; ``read`` takes that sha256.
  read  --run DIR --cells DIR/cells.root --cells-sha256 SHA --out DIR/readout.json
        The controls first (C-IN, C-CELLS, C-PUB, C-REF, C-CV, C-SET, and the c2 units' C-SIM and C-ROO). If any fails,
        STOP.json names it, no difference is formed and no reading is written (exit 1). Otherwise the readings, at
        K = 10 (primary) and K = 5 (second fixed K, the same rules), every other K printed.

Every distance is ``compare_to_paper_fullcov.chi2_with_cov`` against the published TotalCovariance, ndf = its
positive-diagonal bin count (``:102-109``); the flattening is that module's ``flatten_ours`` and ``flatten_th2d``.

MEASURES: the declared readings on the declared products. CANNOT AUTHORIZE: a reported 2D estimator, a cause of the
2D difference, equality with the publication's intermediate stages, or any claim (§1.5, §2.4, §5).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "uq"))
import ref_c2c1 as C  # noqa: E402


class Refused(RuntimeError):
    """A precondition of the reading failed: nothing is written."""


def compare():
    import compare_to_paper_fullcov as cp  # noqa: E402  (imports ROOT; the comparison the 2.270 came from)
    return cp


def th2(path: Path, name: str = "hXSec2D") -> np.ndarray:
    import ROOT
    f = ROOT.TFile.Open(str(path))
    if not f or f.IsZombie() or not f.Get(name):
        raise Refused(f"{path} has no {name}")
    v = compare().flatten_ours(f.Get(name))
    f.Close()
    return v


def named(path: Path, name: str) -> str:
    import ROOT
    f = ROOT.TFile.Open(str(path))
    obj = f.Get(name)
    v = obj.GetTitle() if obj else None
    f.Close()
    return v


class Staged:
    """Every pscratch file the read opens (E_R's central and replicas, the publication), copied once through O_NOATIME
    into DIR, its sha256 taken in the same pass; the read opens only the copies (the director's ruling on #787's R1).
    DIR must not exist: a re-run reads into a new directory."""

    def __init__(self, root: Path):
        self.root, self.sha, self.copies = root, {}, {}

    def __call__(self, src) -> Path:
        src = str(src)
        if src not in self.copies:
            if not self.copies:
                try:
                    self.root.mkdir(parents=True)
                except FileExistsError:
                    raise Refused(f"{self.root} exists: the read stages its inputs into a new directory") from None
            dest = self.root / f"{len(self.copies):03d}_{Path(src).name}"
            self.sha[src] = C.copy_noatime(Path(src), dest)
            self.copies[src] = dest
        return self.copies[src]


class Publication:
    """The bound precision reference: the published cross section on the 224-cell grid, its TotalCovariance and the
    StatOnlyCovariance that defines the reported cells."""

    def __init__(self, cfg: dict, staged: Staged):
        import ROOT
        pub = cfg["publication"]
        p = staged(pub["path"])
        if staged.sha[pub["path"]] != pub["sha256"]:
            raise Refused("the publication's precision ROOT digest differs from config.json")
        cp = compare()
        f = ROOT.TFile.Open(str(p))
        self.x = cp.flatten_th2d(f.Get(pub["histogram"]))
        self.cov = cp.tmatrix_to_numpy(f.Get(pub["covariance"]))
        self.stat = cp.tmatrix_to_numpy(f.Get(pub["mask_covariance"]))
        f.Close()
        import reported_cells as rc
        self.cells = rc.reported_indices((np.diag(self.stat) > 0).reshape(rc.GRID_SHAPE))

    def distance(self, x: np.ndarray) -> tuple[float, int]:
        """chi2/ndf against the published result under its TotalCovariance (compare_to_paper_fullcov.py:99-112)."""
        chi2, ndf, _ = compare().chi2_with_cov(np.asarray(x, float) - self.x, self.cov, "", report=False)
        return chi2 / ndf, ndf


# ------------------------------------------------------------------------------------------- the null and T


def pinv_rank(Cm: np.ndarray, r: int) -> np.ndarray:
    lam, V = np.linalg.eigh((Cm + Cm.T) / 2)
    top = np.argsort(lam)[::-1][:r]
    if np.any(lam[top] <= 0):
        raise Refused(f"the leading {r} eigenvalues are not all positive")
    return (V[:, top] / lam[top]) @ V[:, top].T


def rank_for(n: int, cfg: dict) -> int:
    """The declared rank rule: the leading floor(N / 4) eigenmodes of the N-replica covariance."""
    return n // int(cfg["readings"]["rank_divisor"])


def t_and_null(delta: np.ndarray, D: np.ndarray, r: int) -> dict:
    """T = delta^T C+ delta, C+ the rank-r pseudo-inverse of the replicas' ddof-1 covariance; its null by
    leave-one-out: for each replica, T of (D_i - mean of the rest) under the rest's rank-r pseudo-inverse."""
    T = float(delta @ pinv_rank(np.cov(D, rowvar=False, ddof=1), r) @ delta)
    null = []
    for i in range(D.shape[0]):
        rest = np.delete(D, i, axis=0)
        d = D[i] - rest.mean(axis=0)
        null.append(float(d @ pinv_rank(np.cov(rest, rowvar=False, ddof=1), r) @ d))
    null = np.array(null)
    n = D.shape[0]
    return {"T": T, "rank": r, "n_replicas": n, "q95": float(np.quantile(null, 0.95)), "max": float(null.max()),
            "hartlap": (n - r - 2) / (n - 1)}


def classify_t(t: dict, words: tuple[str, str, str]) -> str:
    return words[0] if t["T"] <= t["q95"] else (words[1] if t["T"] <= t["max"] else words[2])


def classify_rho(lo: float, hi: float, c2r1: str, cfg: dict) -> str:
    """C2-R2 (the director's ruling on #767): a class is read only if the replicas' central 90 % interval of rho
    lies inside it."""
    a, b = cfg["readings"]["rho_input_side"]
    alg = cfg["readings"]["rho_algorithm_side"]
    if a <= lo and hi <= b:
        return "input side"
    if hi <= alg and c2r1 == "differ":
        return "algorithm side"
    if lo > b:
        return "IBU farther: no attribution"
    return "unresolved"


# ------------------------------------------------------------------------------------------- products


def c2_xsec(run: Path, unit: str, K: int) -> np.ndarray:
    z = np.load(run / f"{unit}.npz", allow_pickle=False)
    ks = [int(k) for k in z["ks"]]
    return np.asarray(z["xsec"][ks.index(K)], float)


def meta(run: Path, unit: str) -> dict:
    return json.loads(str(np.load(run / f"{unit}.npz", allow_pickle=False)["meta"]))


def done_pass(run: Path, unit: str) -> bool:
    p = run / f"{unit}.done"
    return p.exists() and json.loads(p.read_text()).get("verdict") == "PASS"


def lgbm(run: Path, unit: str) -> list[dict]:
    return json.loads(str(np.load(run / f"{unit}.npz", allow_pickle=False)["lgbm_params"]))


def c_set(er: list[dict], c1: list[dict], keys: list[str]) -> dict:
    """C-SET: in each construction (the OmniFold estimators and the refinement), the only difference from E_R's
    parameters is the four deterministic keys."""
    if len(er) != len(c1) or not er:
        return {"pass": False, "why": f"{len(er)} E_R constructions against {len(c1)} c1"}
    rows = []
    for a, b in zip(er, c1):
        diff = sorted(k for k in set(a["params"]) | set(b["params"]) if a["params"].get(k) != b["params"].get(k))
        rows.append({"kind": a["kind"], "differ": diff})
    return {"pass": all(r["differ"] == sorted(keys) for r in rows), "constructions": rows}


def rel(a: np.ndarray, b: np.ndarray) -> float:
    nz = b != 0
    if np.any(a[~nz] != 0):
        return float("inf")
    return float(np.max(np.abs(a[nz] / b[nz] - 1))) if nz.any() else 0.0


# ------------------------------------------------------------------------------------------- read


def write_cells(cfg: dict, out: Path, protected=C.PROTECTED) -> dict:
    import ROOT
    import reported_cells as rc
    out.parent.mkdir(parents=True, exist_ok=True)
    with C.read_guards(protected, (out.parent, C.REPO)):
        pub = Publication(cfg, Staged(out.parent / f"{out.stem}-inputs"))
    f = ROOT.TFile.Open(str(out), "RECREATE")
    rc.identity_hist(pub.cells).Write()
    ROOT.TNamed("rule", "positive diagonal of StatOnlyCovariance on the paper's 224-bin global grid").Write()
    ROOT.TNamed("source_sha256", cfg["publication"]["sha256"]).Write()
    f.Close()
    return {"cells": len(pub.cells), "sha256": C.sha256(out)}


def read(cfg: dict, run: Path, cells: Path, cells_sha: str, out: Path, protected=C.PROTECTED) -> dict:
    """The read, under read_guards: the run's own products, the cells file and the repository are read in place; every
    other file (E_R's, the publication) only as a staged O_NOATIME copy beside the readout."""
    with C.read_guards(protected, (run, out.parent, cells, C.REPO), (out.parent,)):
        return guarded_read(cfg, run, cells, cells_sha, out)


def guarded_read(cfg: dict, run: Path, cells: Path, cells_sha: str, out: Path) -> dict:
    import reported_cells as rc
    if C.sha256(cells) != cells_sha:
        raise Refused("the cells file is not the committed one (sha256 differs)")
    rd = cfg["readings"]
    controls = {}
    staged = Staged(out.parent / "inputs")
    pub = Publication(cfg, staged)
    import ROOT
    f = ROOT.TFile.Open(str(cells))
    bound, _ = rc.read_cells(f)
    f.Close()
    try:
        rc.require_same_cells(np.asarray(bound), np.asarray(pub.cells), "committed cells", "the receipt's rule")
        _, _, mask = compare().chi2_with_cov(np.zeros(pub.x.size), pub.cov, "", report=False)
        rc.require_same_cells(np.asarray(bound), rc.reported_indices(mask.reshape(rc.GRID_SHAPE)), "committed cells",
                              "TotalCovariance's mask")
        controls["C-CELLS"] = {"pass": True, "cells": int(len(bound))}
    except (rc.CellIdentityError, TypeError, ValueError) as e:
        controls["C-CELLS"] = {"pass": False, "why": str(e)[:300]}
    e_r = Path(cfg["e_r"]["central"])
    want_in = {k: cfg["inputs"][f"{k}_sha256"] for k in ("CV", "MC")}
    unit_in = {u: meta(run, u).get("inputs_sha256") for u in ("er", "c2_central", "c1_central")}
    e_r_copy = staged(e_r)
    controls["C-IN"] = {"pass": bool(staged.sha[str(e_r)] == cfg["e_r"]["central_sha256"]
                                     and all(v == want_in for v in unit_in.values())),
                        "units_inputs_ok": {u: v == want_in for u, v in unit_in.items()}}
    c_pub = cfg["publication"]["c_pub"]
    src = c_pub["source"]  # C-PUB's reference holds only for the inputs it was computed on
    if (staged.sha[str(e_r)], staged.sha[cfg["publication"]["path"]]) != (src["e_r_sha256"], src["covariance_sha256"]):
        raise Refused("C-PUB's reference chi2 was computed on another E_R or covariance (config.json c_pub.source)")
    x_er = th2(e_r_copy)
    d_er, ndf = pub.distance(x_er)
    controls["C-PUB"] = {"chi2": d_er * ndf, "ndf": ndf,
                         "pass": bool(ndf == c_pub["ndf"] and abs(d_er * ndf / c_pub["chi2"] - 1) <= c_pub["rtol"])}
    x_er_run = th2(run / "er.root")
    controls["C-CV"] = {"max_rel": rel(x_er_run, x_er), "pass": bool(rel(x_er_run, x_er) <= rd["e_r_rtol"])}
    ref_e, ref_r, ref_c2 = (json.loads(named(p, "re2Refinement") or "{}")
                           for p in (e_r_copy, run / "er.root", run / "c2_central.root"))
    det = all(ref_r.get(k) == ref_e.get(k) == ref_c2.get(k) for k in ("params", "signed_sum"))
    fit = all(abs(r.get(k, np.inf) / ref_e.get(k, np.nan) - 1) <= rd["e_r_rtol"] for r in (ref_r, ref_c2)
              for k in ("refined_sum", "clipped_fraction") if ref_e.get(k))
    w_sum = meta(run, "c2_central").get("measured_weights_sum", np.nan)
    y_c2 = np.asarray(np.load(run / "c2_central.npz", allow_pickle=False)["y"], float)
    y_er = np.asarray(np.load(run / "er.npz", allow_pickle=False)["y"], float)
    d_bin = rel(y_c2, y_er)
    controls["C-REF"] = {"a_deterministic_exact": bool(det), "b_fitted_1e-8": bool(fit),
                         "c_e_r_reproduced": controls["C-CV"]["pass"],
                         "d_measured_weights_vs_refined_sum": abs(w_sum / ref_e.get("refined_sum", np.nan) - 1),
                         "d_measured_histogram_vs_e_r_per_bin": d_bin,
                         "pass": bool(det and fit and controls["C-CV"]["pass"] and d_bin <= rd["e_r_rtol"]
                                      and abs(w_sum / ref_e.get("refined_sum", np.nan) - 1) <= rd["e_r_rtol"])}
    want_cpus = int(cfg["e_r"]["cpus"])
    unit_cpus = {u: meta(run, u).get("cpus") for u in ("er", "c2_central", "c1_central")}
    unit_threads = {u: meta(run, u).get("thread_env") for u in ("er", "c2_central", "c1_central")}
    controls["C-CPUS"] = {"pass": all(v == want_cpus for v in unit_cpus.values())
                          and all(v == cfg["e_r"]["thread_env"] for v in unit_threads.values()),
                          "units": unit_cpus, "threads": unit_threads, "e_r": want_cpus}
    controls["C-SET"] = c_set(lgbm(run, "er"), lgbm(run, "c1_central"), cfg["c1"]["deterministic_keys"])
    c2m = meta(run, "c2_central").get("controls", {})
    for name in ("C-SIM", "C-ROO"):
        controls[name] = c2m.get(name, {"pass": False, "why": "missing from c2_central"})
    first, last = C.replica_set(cfg)
    c1r = cfg["c1"]["replicas"]
    units = (["er", "c2_central", "c1_central"] + [f"c2_replica_b{b}" for b in range(first, last + 1)]
             + [f"c1_replica_b{b}" for b in range(c1r["first"], c1r["last"] + 1)])
    not_done = [u for u in units if not done_pass(run, u)]
    controls["done"] = {"pass": not not_done, "not_pass": not_done[:20], "n_not_pass": len(not_done)}
    failed = [k for k, c in controls.items() if not c["pass"]]
    if failed:
        stop = {"schema": "ref-c2c1-stop/1", "stopped": True, "stopped_by": failed, "controls": controls,
                "staged_sha256": staged.sha,
                "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        (out.parent / "STOP.json").write_text(json.dumps(stop, indent=1, default=float) + "\n")
        return stop
    # the differences are formed only here, after every control passed
    rec = {"schema": "ref-c2c1-readout/1", "controls": controls, "D_E_R": d_er, "ndf": ndf}
    e_reps = {b: th2(staged(cfg["e_r"]["replica"].format(b=b))) for b in range(first, last + 1)}
    for K in (cfg["c2"]["iterations"]["primary"], cfg["c2"]["iterations"]["second"]):
        x_ibu = c2_xsec(run, "c2_central", K)
        D = np.array([c2_xsec(run, f"c2_replica_b{b}", K) - e_reps[b] for b in range(first, last + 1)])
        t = t_and_null(x_ibu - x_er, D, rank_for(D.shape[0], cfg))
        r1 = classify_t(t, ("agree", "marginal", "differ"))
        rho_r = np.array([pub.distance(c2_xsec(run, f"c2_replica_b{b}", K))[0] / pub.distance(e_reps[b])[0]
                          for b in range(first, last + 1)])
        q = (1 - rd["rho_interval"]) / 2
        lo, hi = float(np.quantile(rho_r, q)), float(np.quantile(rho_r, 1 - q))
        d_ibu = pub.distance(x_ibu)[0]
        rec[f"K{K}"] = {"C2-R1": {**t, "reading": r1}, "D_IBU": d_ibu, "rho": d_ibu / d_er,
                        "rho_interval": [lo, hi], "C2-R2": classify_rho(lo, hi, r1, cfg)}
    rec["primary_K"] = cfg["c2"]["iterations"]["primary"]
    rec["D_IBU_every_K"] = {int(K): pub.distance(c2_xsec(run, "c2_central", int(K)))[0]
                            for K in cfg["c2"]["iterations"]["scan"]}
    x_c1 = th2(run / "c1_central.root")
    D1 = np.array([th2(run / f"c1_replica_b{b}.root") - th2(staged(cfg["e_r"]["replica"].format(b=b)))
                   for b in range(c1r["first"], c1r["last"] + 1)])
    t1 = t_and_null(x_c1 - x_er, D1, rank_for(D1.shape[0], cfg))
    rec["C1-R1"] = {**t1, "reading": classify_t(t1, ("equivalent", "marginal", "setting-dependent"))}
    rec["C1-R2"] = {"D_e": pub.distance(x_c1)[0], "D_E_R": d_er}
    rec["does_not_license"] = ("c2 and c1 compare estimators on this analysis's inputs; agreement between methods does "
                               "not show that the upstream ingredients or intermediate stages equal MINERvA's, and a "
                               "difference does not show that either method is correct (REF-C2C1 §1.5, §5)")
    rec["staged_sha256"] = staged.sha
    rec["written_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    out.write_text(json.dumps(rec, indent=1, default=float) + "\n")
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("cells")
    c.add_argument("--out", type=Path, required=True)
    r = sub.add_parser("read")
    r.add_argument("--run", type=Path, required=True)
    r.add_argument("--cells", type=Path, required=True)
    r.add_argument("--cells-sha256", required=True)
    r.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    cfg = json.loads(C.CONFIG.read_text())
    try:
        C.check_code(cfg)
        if a.cmd == "cells":
            print(json.dumps(write_cells(cfg, a.out)))
            return 0
        rec = read(cfg, a.run, a.cells, a.cells_sha256, a.out)
    except (Refused, C.GateFailure) as e:
        print(f"refusing: {e}", file=sys.stderr)
        return 4
    if rec.get("stopped"):
        print(f"STOP: failed controls {rec['stopped_by']}; no reading was formed", file=sys.stderr)
        return 1
    k = rec[f"K{rec['primary_K']}"]
    print(json.dumps({"C2-R1": k["C2-R1"]["reading"], "C2-R2": k["C2-R2"], "C1-R1": rec["C1-R1"]["reading"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
