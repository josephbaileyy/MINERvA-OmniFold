"""C2-CORR: correlation structure and eigenvalue spectra of the C2-EFF covariances, and the paired IBU(K) - OmniFold
difference covariance per K (tier3-design, 2026-11-27; local, 0 node-h; Joseph's yes of 2026-11-27 via the director).

usage: python3 -I -B c2_corr.py FETCH_DIR --out RECORD.json [--png SPECTRA.png]

FETCH_DIR is C2-EFF's verified fetch (/Users/josephbailey/c2eff-data/c2eff-run1). The 205 published bins, the
loaders and C2-EFF's controls (C-PIN, C-FETCH, C-META, C-CELLS, C-STAT, C-AXES, C-QR, C-FINITE) are c2_eff.py's,
imported unchanged; c2_eff.compute runs first, so a failing C2-EFF control stops this driver too.

Added controls:
  C-PAIR  on the full 224-cell vectors, exactly as REF-C2C1's reader: T = delta^T C+ delta, delta = c2_central(K) -
          E_R central (001_xsec.root), C+ the rank-75 pseudo-inverse of the ddof-1 covariance of D_b = c2_replica_b(K)
          - E_R replica b ((b+1):03d); T must reproduce read-2's committed K10 and K5 T to 1e-8 relative. That ties
          the per-replica pairing and both ensembles to the bound read.
  C-ID    tr C_delta(K) = tr C_IBU(K) + tr C_OF - 2 tr C_cross(K), to 1e-10 relative, every K.
  C-PSD   every covariance used is symmetric and its smallest eigenvalue >= -1e-12 lambda_max.
  C-CORR  every correlation matrix has a unit diagonal to 1e-12.

Quantities (205 cells; ddof 1; descriptive, no verdict):
  (1) for C_IBU(K) (every K), C_OF and StatOnly: off-diagonal correlation summaries (mean |rho|, max |rho|, mean
      rho, fraction negative, mean rho of grid neighbours in pT and in p||), the eigenvalue spectrum (descending,
      absolute and as a share of the trace), top-k trace shares, the participation ratio (sum lambda)^2/sum lambda^2,
      and the cosines of the principal angles between the leading 1, 5 and 10 eigenvectors of each pair among
      C_IBU(10), C_OF and StatOnly;
  (2) per K: C_delta(K) = Cov(IBU(K) - OF) on the same draws, sqrt tr C_delta, sqrt tr C_delta / sqrt tr C_OF, the
      cross-covariance trace, per-cell correlation of IBU(K) and OF (median, min, max), and C_delta's spectrum
      summaries.
The record carries the three spectra for the figure (c2_corr_figure.py draws the note's PDF from it), and a flat
"headline" block of the values a note sentence may bind, each copied from the record's own fields.
--png draws a quick-look plot (labels only, no claim).
It prints statuses only.
"""
import argparse
import importlib.util
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("c2_eff", os.path.join(HERE, "c2_eff.py"))
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)

READOUT = E.C2 + "/read-2/readout.json"
E.PINS[READOUT] = "2b6a89282c01f39ee66c5239fd92b81b277b5388"
RANK = 75            # REF-C2C1's rule: floor(300 / 4) (config.json readings.rank_divisor 4)
PAIR_TOL = 1e-8
ID_TOL = 1e-10
PSD_TOL = 1e-12
TOPK = (1, 5, 10, 20, 50)
ANGLE_K = (1, 5, 10)


class Stop(Exception):
    pass


def pinv_rank(C: np.ndarray, r: int) -> np.ndarray:
    """REF-C2C1's rank-r pseudo-inverse (ref_c2c1_read.py pinv_rank), restated."""
    lam, V = np.linalg.eigh((C + C.T) / 2)
    top = np.argsort(lam)[::-1][:r]
    if np.any(lam[top] <= 0):
        raise Stop(f"C-PAIR: the leading {r} eigenvalues are not all positive")
    return (V[:, top] / lam[top]) @ V[:, top].T


def t_stat(delta: np.ndarray, D: np.ndarray, r: int) -> float:
    return float(delta @ pinv_rank(np.cov(D, rowvar=False, ddof=1), r) @ delta)


def readout_t(b: bytes) -> dict:
    d = json.loads(b.decode())
    try:
        return {10: float(d["K10"]["C2-R1"]["T"]), 5: float(d["K5"]["C2-R1"]["T"])}
    except (KeyError, TypeError, ValueError) as e:
        raise Stop(f"C-PIN: readout.json's T values are not readable ({e})")


def c_pair(ibu_central: np.ndarray, er_central: np.ndarray, ibu: np.ndarray, of: np.ndarray, want: dict) -> dict:
    """ibu_central (K, 224), er_central (224,), ibu (N, K, 224), of (N, 224)."""
    out = {}
    for K, t_want in want.items():
        ki = E.KS.index(K)
        t = t_stat(ibu_central[ki] - er_central, ibu[:, ki, :] - of, RANK)
        rel = abs(t / t_want - 1)
        if not rel <= PAIR_TOL:
            raise Stop(f"C-PAIR: K={K} T = {t!r}, read-2 recorded {t_want!r} (rel {rel:.3g})")
        out[str(K)] = {"T": t, "recorded": t_want, "rel": rel}
    return {"pass": True, "tol": PAIR_TOL, "rank": RANK, "by_K": out}


def cov(X: np.ndarray) -> np.ndarray:
    return np.cov(X, rowvar=False, ddof=1)


def psd_check(name: str, C: np.ndarray) -> np.ndarray:
    if not np.allclose(C, C.T, rtol=0, atol=PSD_TOL * np.max(np.abs(C))):
        raise Stop(f"C-PSD: {name} is not symmetric")
    lam = np.linalg.eigvalsh((C + C.T) / 2)[::-1]
    if not lam[-1] >= -PSD_TOL * lam[0]:
        raise Stop(f"C-PSD: {name} has eigenvalue {lam[-1]!r} below -1e-12 lambda_max {lam[0]!r}")
    return lam


def corr(C: np.ndarray, name: str) -> np.ndarray:
    d = np.sqrt(np.diag(C))
    if not np.all(d > 0):
        raise Stop(f"C-CORR: {name} has a non-positive variance")
    R = C / np.outer(d, d)
    if not np.max(np.abs(np.diag(R) - 1)) <= PSD_TOL:
        raise Stop(f"C-CORR: {name}'s correlation diagonal is not 1")
    return R


def neighbours(cells: np.ndarray) -> tuple:
    """Index pairs (within the 205) of grid neighbours: same pT row, adjacent p|| ; same p|| column, adjacent pT."""
    pos = {int(c): i for i, c in enumerate(cells)}
    along_pz, along_pt = [], []
    for c, i in pos.items():
        pt, pz = divmod(c, E.NPZ)
        if pz + 1 < E.NPZ and (c + 1) in pos:
            along_pz.append((i, pos[c + 1]))
        if pt + 1 < E.NPT and (c + E.NPZ) in pos:
            along_pt.append((i, pos[c + E.NPZ]))
    return np.array(along_pz), np.array(along_pt)


def structure(C: np.ndarray, name: str, nb: tuple) -> dict:
    lam = psd_check(name, C)
    R = corr(C, name)
    off = R[~np.eye(len(R), dtype=bool)]
    pz, pt = nb
    tr = float(np.sum(lam))
    lam_pos = np.clip(lam, 0, None)
    return {
        "mean_abs_offdiag_rho": float(np.mean(np.abs(off))),
        "max_abs_offdiag_rho": float(np.max(np.abs(off))),
        "mean_offdiag_rho": float(np.mean(off)),
        "fraction_offdiag_negative": float(np.mean(off < 0)),
        "mean_rho_neighbours_along_ppar": float(np.mean(R[pz[:, 0], pz[:, 1]])),
        "mean_rho_neighbours_along_pt": float(np.mean(R[pt[:, 0], pt[:, 1]])),
        "n_neighbour_pairs": [int(len(pz)), int(len(pt))],
        "trace": tr,
        "topk_trace_share": {str(k): float(np.sum(lam_pos[:k]) / tr) for k in TOPK},
        "participation_ratio": float(np.sum(lam_pos) ** 2 / np.sum(lam_pos ** 2)),
        "eigenvalues_desc": [float(x) for x in lam],
    }


def top_vectors(C: np.ndarray, k: int) -> np.ndarray:
    lam, V = np.linalg.eigh((C + C.T) / 2)
    return V[:, np.argsort(lam)[::-1][:k]]


def principal_cosines(A: np.ndarray, B: np.ndarray) -> dict:
    return {str(k): [float(x) for x in np.linalg.svd(top_vectors(A, k).T @ top_vectors(B, k), compute_uv=False)]
            for k in ANGLE_K}


def paired(ibu: np.ndarray, of: np.ndarray) -> dict:
    """ibu (N, K, 205), of (N, 205) on the 205 cells."""
    C_of = cov(of)
    out = {}
    for ki, K in enumerate(E.KS):
        I = ibu[:, ki, :]
        C_i = cov(I)
        Dl = I - of
        C_d = cov(Dl)
        X = np.cov(np.hstack([I, of]), rowvar=False, ddof=1)
        n = I.shape[1]
        cross = X[:n, n:]
        lhs, rhs = np.trace(C_d), np.trace(C_i) + np.trace(C_of) - 2 * np.trace(cross)
        rel = abs(lhs / rhs - 1)
        if not rel <= ID_TOL:
            raise Stop(f"C-ID: K={K} tr C_delta {lhs!r} vs {rhs!r} (rel {rel:.3g})")
        lam = psd_check(f"C_delta(K={K})", C_d)
        lam_pos = np.clip(lam, 0, None)
        rho_c = np.diag(cross) / np.sqrt(np.diag(C_i) * np.diag(C_of))
        out[str(K)] = {
            "sqrt_tr_delta": float(np.sqrt(lhs)),
            "sqrt_tr_delta_over_sqrt_tr_of": float(np.sqrt(lhs / np.trace(C_of))),
            "tr_cross": float(np.trace(cross)),
            "c_id_rel": float(rel),
            "per_cell_corr_ibu_of": {"median": float(np.median(rho_c)), "min": float(np.min(rho_c)),
                                     "max": float(np.max(rho_c))},
            "delta_topk_trace_share": {str(k): float(np.sum(lam_pos[:k]) / np.sum(lam_pos)) for k in TOPK},
            "delta_participation_ratio": float(np.sum(lam_pos) ** 2 / np.sum(lam_pos ** 2)),
        }
    return out


def headline(base: dict, struct: dict, angles: dict, pd: dict) -> dict:
    """Flat keys a note sentence may bind (the director's request of 2026-11-27); each is copied from the record's own
    computed values, nothing new is computed here. IBU = C_IBU at K = 10, OF = C_OF, published = StatOnly."""
    k10 = base["per_K"]["10"]
    trio = (("ibu_k10", "C_IBU_K10"), ("of", "C_OF"), ("published", "StatOnly"))
    h = {"r_a_k10_ibu_over_of": k10["r_a_ibu_over_of"], "r_a_k10_jackknife_se": k10["r_a_jackknife_se"],
         "r_b_k10_ibu_over_published": k10["r_b_ibu_over_statonly"], "r_b_k10_jackknife_se": k10["r_b_jackknife_se"],
         "r_of_over_published": base["r_of_over_statonly"]}
    for short, key in trio:
        s = struct[key]
        h[f"participation_ratio_{short}"] = s["participation_ratio"]
        h[f"neighbour_rho_ppar_{short}"] = s["mean_rho_neighbours_along_ppar"]
        h[f"neighbour_rho_pt_{short}"] = s["mean_rho_neighbours_along_pt"]
        h[f"mean_abs_offdiag_rho_{short}"] = s["mean_abs_offdiag_rho"]
    h["leading_vector_cosine_ibu_k10_published"] = angles["C_IBU_K10|StatOnly"]["1"][0]
    h["leading_vector_cosine_of_published"] = angles["C_OF|StatOnly"]["1"][0]
    h["leading_vector_cosine_ibu_k10_of"] = angles["C_IBU_K10|C_OF"]["1"][0]
    h["paired_delta_k10_sqrt_tr_over_of"] = pd["10"]["sqrt_tr_delta_over_sqrt_tr_of"]
    h["paired_per_cell_corr_k10_median"] = pd["10"]["per_cell_corr_ibu_of"]["median"]
    return h


def analyse(ibu224, of224, stat224, cells, rec_trace, rec_ratio, ibu_central, er_central, want_t) -> dict:
    base = E.compute(ibu224, of224, stat224, cells, rec_trace, rec_ratio)   # C2-EFF's controls, unchanged
    pair = c_pair(ibu_central, er_central, ibu224, of224, want_t)
    I = ibu224[:, :, cells]
    O = of224[:, cells]
    S = stat224[np.ix_(cells, cells)]
    nb = neighbours(cells)
    mats = {f"C_IBU_K{K}": cov(I[:, ki, :]) for ki, K in enumerate(E.KS)}
    mats["C_OF"] = cov(O)
    mats["StatOnly"] = S
    struct = {k: structure(v, k, nb) for k, v in mats.items()}
    trio = {"C_IBU_K10": mats["C_IBU_K10"], "C_OF": mats["C_OF"], "StatOnly": S}
    angles = {f"{a}|{b}": principal_cosines(trio[a], trio[b])
              for a, b in (("C_IBU_K10", "C_OF"), ("C_IBU_K10", "StatOnly"), ("C_OF", "StatOnly"))}
    pd = paired(I, O)
    head = headline(base, struct, angles, pd)
    return {"headline": head, "c2_eff_controls": base["controls"], "c2_eff_ratios_K10": base["per_K"]["10"],
            "controls": {"C-PAIR": pair, "C-ID": {"pass": True, "tol": ID_TOL},
                         "C-PSD": {"pass": True, "tol": PSD_TOL}, "C-CORR": {"pass": True}},
            "structure": struct, "principal_cosines": angles, "paired_difference": pd,
            "figure_spectra": {k: struct[k]["eigenvalues_desc"] for k in trio}}


def run(fetch: str) -> dict:
    rec = {"schema": "c2-corr/1", "fetch_dir": os.path.abspath(fetch), "pins": E.PINS, "cells": 205,
           "what": "descriptive: correlation structure, spectra and paired differences of bootstrap covariances",
           "caveats": [
               "the draws resample data, signal MC and background MC together; StatOnly's contents are not "
               "established (item 3a)",
               "IBU is REF-C2C1's binned IBU on E_R's inputs, not MINERvA's analysis code",
               "300-replica sample covariances: their small eigenvalues carry sampling noise of their own"]}
    try:
        stat = E.stat_matrix(E.git_bytes(E.STAT_TXT))
        cells = E.cells_from_root(E.git_bytes(E.CELLS_ROOT))
        rec_trace, rec_ratio = E.recorded_values(E.git_bytes(E.VALUES))
        want_t = readout_t(E.git_bytes(READOUT))
        E.check_fetch(fetch)
        ibu = E.load_ibu(fetch, E.config_sha())
        of = E.load_of(fetch)
        z = np.load(os.path.join(fetch, "files", "units", "c2_central.npz"), allow_pickle=False)
        if [int(k) for k in z["ks"]] != E.KS:
            raise Stop("C-META: c2_central's ks")
        ibu_c = np.asarray(z["xsec"], float)
        er_c = E.th2_values(os.path.join(fetch, "files", "inputs", "001_xsec.root"), "hXSec2D")
        rec.update(analyse(ibu, of, stat, cells, rec_trace, rec_ratio, ibu_c, er_c, want_t))
        rec["status"] = "OK"
    except (Stop, E.Stop, OSError, ValueError, KeyError) as e:
        rec["status"] = "STOP"
        rec["stop"] = f"{type(e).__name__}: {e}"
    return rec


def plot(rec: dict, png: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.4, 4.2), dpi=150)
    style = {"C_IBU_K10": ("#1f5fa8", "-", "IBU, 10 iterations (same draws)"),
             "C_OF": ("#c0392b", "-", "OmniFold (quoted statistical block)"),
             "StatOnly": ("#555555", "--", "MINERvA StatOnlyCovariance")}
    for k, (c, ls, lab) in style.items():
        lam = np.array(rec["figure_spectra"][k])
        ax.semilogy(np.arange(1, len(lam) + 1), np.clip(lam, 1e-300, None), color=c, ls=ls, lw=1.6, label=lab)
    ax.set_xlabel("eigenvalue rank (205 published bins)")
    ax.set_ylabel(r"eigenvalue  [(cm$^2$/(GeV/$c$)$^2$)$^2$]")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(alpha=0.25, lw=0.5)
    fig.tight_layout()
    fig.savefig(png)
    plt.close(fig)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("fetch")
    ap.add_argument("--out", required=True)
    ap.add_argument("--png")
    a = ap.parse_args(argv)
    for p in filter(None, (a.out, a.png)):
        if os.path.lexists(p):
            print(f"refusing: {p} exists")
            return 2
    rec = run(a.fetch)
    with open(a.out, "x") as f:
        json.dump(rec, f, indent=1, allow_nan=False)
        f.write("\n")
    if rec["status"] == "OK" and a.png:
        plot(rec, a.png)
    print(f"C2-CORR {rec['status']}" + (f": {rec['stop']}" if rec["status"] != "OK" else ""))
    return 0 if rec["status"] == "OK" else 3


if __name__ == "__main__":
    sys.exit(main())
