"""C2-EFF: IBU K=10 against OmniFold (E_R) on the same 300 bootstrap draws, and against MINERvA's StatOnlyCovariance
(tier3-design, 2026-11-27; local, 0 node-h; run only after c2_fetch.sh printed FETCH OK).

usage: python3 -I -B c2_eff.py FETCH_DIR --out RECORD.json

Cell set: the 205 published bins (positive diagonal of StatOnlyCovariance on the paper's 224-cell grid, C-order
(pt, p||), GlobalID = 16 (ptbin-1) + (p||bin-1)), the set the recorded 0.4067 ratio uses (RE-2 values_table rows
statonly-trace-a, stat-vs-statonly-b). Every ensemble is mapped onto exactly these 205 cells.

Quantities (each covariance ddof 1 about its own replica mean, on the 205 cells):
  s_IBU(K) = sqrt(tr C_IBU(K)), the c2 replicas c2_replica_b1..b300 at each K;
  s_OF     = sqrt(tr C_OF), read-2's staged E_R copies 002..301_xsec.root (b -> (b+1):03d), hXSec2D;
  s_STAT   = sqrt(tr StatOnly) on the 205 cells, from the committed release text file;
  r_a(K) = s_IBU(K)/s_OF (the estimator ratio on the same draws), r_b(K) = s_IBU(K)/s_STAT, r_of = s_OF/s_STAT;
  paired delete-one jackknife SEs of r_a and r_b; per-cell median sigma ratios. K = 10 is primary; the rest are printed.

Controls (any failure writes a STOP record, rc 3): C-PIN, C-FETCH, C-META, C-CELLS, C-STAT (s_STAT reproduces the
recorded 4.63859769901624e-40 to 1e-6), C-AXES, C-QR (r_of reproduces the recorded 0.4066643573220531 to 1e-6, so the
OmniFold replicas are Q_R's statistical replicas on the same cells), C-FINITE.

It prints statuses only; the numbers are in the record, read by the director first.
"""
import argparse
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile

import numpy as np

REPO = os.environ.get("C2_EFF_REPO") or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                                      *[".."] * 7))
N_REP = 300
KS = [1, 2, 3, 4, 5, 10, 15, 20]
PRIMARY = 10
TOL = 1e-6
NPT, NPZ = 14, 16
PT_EDGES = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50])
PZ_EDGES = np.array([1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0])
C2 = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ref-c2c1/step2"
PINS = {  # path at origin/main -> git blob id (git rev-parse origin/main:<path>)
    "2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV_stat.txt":
        "e3b368cd9fd2cca2bc6af83f1a34cf7f8e3f2343",
    C2 + "/cells/cells.root": "4f5ac5cbcc3bbfa590af5d18d8713bb3dbd011fb",
    "docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partc_r2/partc-r2/values_table.tsv":
        "49b397410c55c2351552ee8637c073409cf78f43",
}
STAT_TXT, CELLS_ROOT, VALUES = list(PINS)
CONFIG_COMMIT = "77d76cfc"  # the units' config (read-2 README: "config_sha256 names 77d76cfc's config.json")


class Stop(Exception):
    pass


def git_bytes(path: str) -> bytes:
    blob = subprocess.run(["git", "-C", REPO, "rev-parse", f"origin/main:{path}"], capture_output=True, text=True)
    if blob.returncode != 0 or blob.stdout.strip() != PINS[path]:
        raise Stop(f"C-PIN: origin/main:{path} is not blob {PINS[path]} ({blob.stdout.strip() or blob.stderr.strip()})")
    r = subprocess.run(["git", "-C", REPO, "cat-file", "blob", PINS[path]], capture_output=True)
    if r.returncode != 0:
        raise Stop(f"C-PIN: cannot read blob {PINS[path]}")
    return r.stdout


def config_sha() -> str:
    r = subprocess.run(["git", "-C", REPO, "show", f"{CONFIG_COMMIT}:2d-unfolding/ref_c2c1/config.json"],
                       capture_output=True)
    if r.returncode != 0:
        raise Stop(f"C-PIN: {CONFIG_COMMIT}:2d-unfolding/ref_c2c1/config.json is not readable")
    return hashlib.sha256(r.stdout).hexdigest()


def recorded_values(tsv: bytes) -> tuple:
    rows = {ln.split("\t")[0]: ln.split("\t") for ln in tsv.decode().splitlines() if ln.strip()}
    try:
        trace = float(rows["statonly-trace-a"][10])
        ratio = float(rows["stat-vs-statonly-b"][10])
    except (KeyError, IndexError, ValueError) as e:
        raise Stop(f"C-PIN: values_table rows not readable ({e})")
    return trace, ratio


def stat_matrix(txt: bytes) -> np.ndarray:
    C = np.zeros((NPT * NPZ, NPT * NPZ))
    seen = 0
    for ln in txt.decode().splitlines()[1:]:
        i, j, v = ln.split(",")
        C[int(i), int(j)] = float(v)
        seen += 1
    if seen != (NPT * NPZ) ** 2:
        raise Stop(f"C-CELLS: the stat file has {seen} entries, not {(NPT * NPZ) ** 2}")
    return C


def th2_values(path: str, name: str) -> np.ndarray:
    import uproot
    with uproot.open(path) as f:
        h = f[name]
        ex, ey = h.axis(0).edges(), h.axis(1).edges()
        if len(ex) != NPT + 1 or len(ey) != NPZ + 1 or not (np.allclose(ex, PT_EDGES, rtol=0, atol=1e-9)
                                                           and np.allclose(ey, PZ_EDGES, rtol=0, atol=1e-9)):
            raise Stop(f"C-AXES: {os.path.basename(path)}:{name} is not the (pt 14, p|| 16) grid")
        v = np.asarray(h.values(flow=False), float)
    if v.shape != (NPT, NPZ):
        raise Stop(f"C-AXES: {os.path.basename(path)}:{name} has shape {v.shape}")
    return v.ravel(order="C")  # GlobalID = 16 (ptbin-1) + (p||bin-1), compare_to_paper_fullcov.flatten_ours


def cells_from_root(b: bytes) -> np.ndarray:
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "cells.root")
        with open(p, "wb") as f:
            f.write(b)
        a = th2_values(p, "hReportedCells")
    if not np.all((a == 0) | (a == 1)):
        raise Stop("C-CELLS: hReportedCells holds values other than 0 and 1")
    return np.flatnonzero(a == 1)


def sha_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_fetch(fetch: str) -> None:
    sums = os.path.join(fetch, "SHA256SUMS")
    with open(sums) as f:
        rows = [ln.split() for ln in f if ln.strip()]
    if len(rows) != 2 * (N_REP + 1) + N_REP + 1:
        raise Stop(f"C-FETCH: SHA256SUMS has {len(rows)} rows, not 903")
    for digest, rel in rows:
        if sha_file(os.path.join(fetch, rel)) != digest:
            raise Stop(f"C-FETCH: {rel} differs from SHA256SUMS")


def load_ibu(fetch: str, cfg_sha: str) -> np.ndarray:
    X = np.empty((N_REP, len(KS), NPT * NPZ))
    for b in range(1, N_REP + 1):
        name = f"c2_replica_b{b}"
        z = np.load(os.path.join(fetch, "files", "units", name + ".npz"), allow_pickle=False)
        meta = json.loads(str(z["meta"]))
        if meta.get("unit") != name or meta.get("bootstrap_seed") != b or meta.get("config_sha256") != cfg_sha:
            raise Stop(f"C-META: {name}'s meta names unit {meta.get('unit')}, seed {meta.get('bootstrap_seed')}, "
                       f"config {meta.get('config_sha256')}")
        if not meta.get("controls") or not all(c.get("pass") is True for c in meta["controls"].values()):
            raise Stop(f"C-META: {name}'s own controls are not all PASS")
        if [int(k) for k in z["ks"]] != KS:
            raise Stop(f"C-META: {name}'s ks are not {KS}")
        X[b - 1] = np.asarray(z["xsec"], float)
    return X


def load_of(fetch: str) -> np.ndarray:
    return np.array([th2_values(os.path.join(fetch, "files", "inputs", f"{b + 1:03d}_xsec.root"), "hXSec2D")
                     for b in range(1, N_REP + 1)])


def sqrt_tr_cov(X: np.ndarray) -> float:
    """sqrt of the trace of the ddof-1 sample covariance of the rows of X."""
    return float(np.sqrt(np.sum(np.var(X, axis=0, ddof=1))))


def jackknife_se(f, n: int) -> float:
    vals = np.array([f(np.delete(np.arange(n), i)) for i in range(n)])
    return float(np.sqrt((n - 1) / n * np.sum((vals - vals.mean()) ** 2)))


def compute(ibu: np.ndarray, of: np.ndarray, stat: np.ndarray, cells: np.ndarray, rec_trace: float,
            rec_ratio: float) -> dict:
    """ibu (N, K, 224), of (N, 224), stat (224, 224); cells: the 205 indices."""
    for nm, a in (("ibu", ibu), ("of", of), ("stat", stat)):
        if not np.all(np.isfinite(a)):
            raise Stop(f"C-FINITE: {nm} has non-finite values")
    pos = np.flatnonzero(np.diag(stat) > 0)
    if not np.array_equal(pos, np.sort(cells)) or len(cells) != 205:
        raise Stop(f"C-CELLS: StatOnly's positive diagonal ({len(pos)} cells) is not the committed 205-cell set")
    S = stat[np.ix_(cells, cells)]
    s_stat = float(np.sqrt(np.trace(S)))
    c_stat = abs(s_stat / rec_trace - 1)
    if not c_stat <= TOL:
        raise Stop(f"C-STAT: sqrt tr StatOnly = {s_stat!r}, recorded {rec_trace!r} (rel {c_stat:.3g})")
    O = of[:, cells]
    s_of = sqrt_tr_cov(O)
    c_qr = abs((s_of / s_stat) / rec_ratio - 1)
    if not c_qr <= TOL:
        raise Stop(f"C-QR: s_OF/s_STAT = {s_of / s_stat!r}, recorded {rec_ratio!r} (rel {c_qr:.3g})")
    n = O.shape[0]
    sd_of = np.std(O, axis=0, ddof=1)
    sd_stat = np.sqrt(np.diag(S))
    per_k = {}
    for ki, K in enumerate(KS):
        I = ibu[:, ki, :][:, cells]
        s_ibu = sqrt_tr_cov(I)
        sd_ibu = np.std(I, axis=0, ddof=1)
        per_k[str(K)] = {
            "sqrt_tr_ibu": s_ibu,
            "r_a_ibu_over_of": s_ibu / s_of,
            "r_a_jackknife_se": jackknife_se(lambda idx: sqrt_tr_cov(I[idx]) / sqrt_tr_cov(O[idx]), n),
            "r_b_ibu_over_statonly": s_ibu / s_stat,
            "r_b_jackknife_se": jackknife_se(lambda idx: sqrt_tr_cov(I[idx]) / s_stat, n),
            "median_sigma_ratio_ibu_over_of": float(np.median(sd_ibu / sd_of)),
            "median_sigma_ratio_ibu_over_statonly": float(np.median(sd_ibu / sd_stat)),
        }
    return {"cells": 205, "n_replicas": n, "sqrt_tr_statonly": s_stat, "sqrt_tr_of": s_of,
            "r_of_over_statonly": s_of / s_stat, "median_sigma_ratio_of_over_statonly": float(np.median(sd_of / sd_stat)),
            "controls": {"C-STAT": {"rel": c_stat, "tol": TOL, "pass": True},
                         "C-QR": {"rel": c_qr, "tol": TOL, "pass": True},
                         "C-CELLS": {"pass": True}, "C-FINITE": {"pass": True}},
            "primary_K": PRIMARY, "per_K": per_k}


def run(fetch: str) -> dict:
    rec = {"schema": "c2-eff/1", "fetch_dir": os.path.abspath(fetch), "pins": PINS, "config_commit": CONFIG_COMMIT,
           "what": "descriptive: bootstrap widths on the same draws (data Poisson, signal MC, background), 205 cells",
           "caveats": [
               "the draws resample data, signal MC and background MC together; MINERvA's StatOnly contents are not "
               "established (item 3a), so r_b compares unlike source sets as far as is known",
               "IBU K=10 here is REF-C2C1's binned IBU on E_R's inputs, not MINERvA's analysis code",
               "pairing for the jackknife is b -> read-2 inputs (b+1):03d, as read-2's staging records"]}
    try:
        stat = stat_matrix(git_bytes(STAT_TXT))
        cells = cells_from_root(git_bytes(CELLS_ROOT))
        rec_trace, rec_ratio = recorded_values(git_bytes(VALUES))
        cfg = config_sha()
        check_fetch(fetch)
        ibu = load_ibu(fetch, cfg)
        of = load_of(fetch)
        rec.update(compute(ibu, of, stat, cells, rec_trace, rec_ratio))
        rec["controls"].update({"C-PIN": {"pass": True}, "C-FETCH": {"pass": True}, "C-META": {"pass": True},
                                "C-AXES": {"pass": True}})
        rec["status"] = "OK"
    except (Stop, OSError, ValueError, KeyError) as e:
        rec["status"] = "STOP"
        rec["stop"] = f"{type(e).__name__}: {e}"
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("fetch")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if os.path.lexists(a.out):
        print(f"refusing: {a.out} exists")
        return 2
    rec = run(a.fetch)
    with open(a.out, "x") as f:
        json.dump(rec, f, indent=1, allow_nan=False)
        f.write("\n")
    print(f"C2-EFF {rec['status']}" + (f": {rec['stop']}" if rec["status"] != "OK" else ""))
    return 0 if rec["status"] == "OK" else 3


if __name__ == "__main__":
    sys.exit(main())
