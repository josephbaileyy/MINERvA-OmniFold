#!/usr/bin/env python3
"""The q0 study's readings (PLAN.md section 3, committed at aae34aab before computing), on the extract's npz.

    q0_analyze.py --npz FILE --out DIR     (DIR must not exist; writes results.json and results.txt)

The npz's sha256 must equal the connect record's (q0_extract.json, RECORDS.SHA256SUMS). Descriptive only: it licenses no
note wording, and the variable choice stays Joseph's and Ben's.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

NPZ_SHA = "91d013793fae94a363bc3e515fa600474c0d9218e412cd0766b42535c7f152b5"   # connect/run/records/RECORDS.SHA256SUMS
PT_C = [0.0, 0.25, 0.47, 0.70, 1.00, 1.50, 4.50]       # PLAN 3: subsets of re2_driver.py:44-48
PZ_C = [1.5, 3.0, 4.5, 6.0, 9.0, 20.0, 60.0]
MERGE_MIN = 50_000
EAV_BINS = [0.0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100.0]  # eavail_step0.py:41-47 row 3
SPLIT_SEED, SUB_SEED, N_FIT, N_SCORE = 20261124, 20261125, 2_000_000, 2_000_000
HGB = dict(loss="squared_error", learning_rate=0.1, max_iter=300, max_leaf_nodes=63, min_samples_leaf=200,
           l2_regularization=0.0, max_bins=255, early_stopping=False, random_state=20261124)
THREADS = 4
CELL_MIN_SCORE = 2000


# ---------------------------------------------------------------------------------------------- weighted helpers
def wquantile(x: np.ndarray, w: np.ndarray, qs) -> list[float]:
    """Weighted quantiles: the weighted CDF at cumulative-weight midpoints, linear interpolation (PLAN 3)."""
    o = np.argsort(x, kind="stable")
    x, w = x[o], w[o]
    c = np.cumsum(w)
    mid = (c - 0.5 * w) / c[-1]
    return [float(np.interp(q, mid, x)) for q in qs]


def wpearson(x, y, w) -> float:
    w = w / w.sum()
    mx, my = np.sum(w * x), np.sum(w * y)
    cov = np.sum(w * (x - mx) * (y - my))
    return float(cov / np.sqrt(np.sum(w * (x - mx) ** 2) * np.sum(w * (y - my) ** 2)))


def wrank(x, w) -> np.ndarray:
    """Weighted mid-ranks: the cumulative weight below each value plus half its tie group's weight."""
    o = np.argsort(x, kind="stable")
    xs, ws = x[o], w[o]
    uniq, start = np.unique(xs, return_index=True)
    gw = np.add.reduceat(ws, start)
    below = np.concatenate([[0.0], np.cumsum(gw)[:-1]])
    r_group = below + 0.5 * gw
    r = np.empty_like(x, dtype=np.float64)
    r[o] = np.repeat(r_group, np.diff(np.append(start, xs.size)))
    return r


def wspearman(x, y, w) -> float:
    return wpearson(wrank(x, w), wrank(y, w), w)


# ---------------------------------------------------------------------------------------------- the coarse grid
def coarse_cells(pt, pz, eligible) -> tuple[np.ndarray, dict]:
    """Cell id per row (-1 outside the grid) after PLAN 3's merge rule on unweighted eligible counts."""
    ip = np.searchsorted(PT_C, pt, side="right") - 1
    iz = np.searchsorted(PZ_C, pz, side="right") - 1
    ip = np.where(pt == PT_C[-1], len(PT_C) - 2, ip)
    iz = np.where(pz == PZ_C[-1], len(PZ_C) - 2, iz)
    inside = (ip >= 0) & (ip < len(PT_C) - 1) & (iz >= 0) & (iz < len(PZ_C) - 1)
    npt = len(PT_C) - 1
    raw = np.where(inside, iz * npt + ip, -1)
    label = {c: c for c in range(npt * (len(PZ_C) - 1))}            # cell -> representative
    counts = np.bincount(raw[eligible & inside], minlength=len(label))

    def rep(c):
        while label[c] != c:
            c = label[c]
        return c
    changed = True
    while changed:
        changed = False
        groups = {}
        for c in label:
            groups.setdefault(rep(c), []).append(c)
        for r, members in sorted(groups.items()):
            n = int(sum(counts[m] for m in members))
            if n >= MERGE_MIN:
                continue
            iz_r, ip_min = r // npt, min(m % npt for m in members)
            row = sorted({rep(iz_r * npt + j) for j in range(npt)} - {r})
            lower = [g for g in row if max(m % npt for m in groups[g]) < ip_min]
            upper = [g for g in row if min(m % npt for m in groups[g]) > ip_min]
            target = max(lower, key=lambda g: max(m % npt for m in groups[g])) if lower else \
                (min(upper, key=lambda g: min(m % npt for m in groups[g])) if upper else None)
            if target is None:
                continue                     # a p|| row with one group left stays below the minimum (reported)
            label[r] = target
            changed = True
            break
    rep_of = np.array([rep(c) for c in range(len(label))], dtype=np.int64)
    cell = np.where(raw >= 0, rep_of[np.clip(raw, 0, None)], -1)
    names = {}
    for c in sorted({rep(c) for c in label}):
        members = sorted(m for m in label if rep(m) == c)
        pts = sorted({m % npt for m in members})
        names[int(c)] = {"pz": [PZ_C[c // npt], PZ_C[c // npt + 1]], "pt": [PT_C[pts[0]], PT_C[pts[-1] + 1]],
                         "members": [int(m) for m in members], "n_eligible": int(sum(counts[m] for m in members))}
    return cell, names


# ---------------------------------------------------------------------------------------------- the readings
def readings(z: dict, n_fit: int = N_FIT, n_score: int = N_SCORE, hgb: dict | None = None) -> dict:
    from sklearn.ensemble import HistGradientBoostingRegressor
    hgb = dict(HGB if hgb is None else hgb)
    out = {}
    pt, pz, ea, q0, w = (np.asarray(z[k], np.float64) for k in ("pt", "pz", "eavail", "q0", "w_reco"))
    st = np.asarray(z["q0_status"])
    n = pt.size
    out["n_rows"] = int(n)
    # reading 4
    out["R4"] = {"frac_q0_le_0_unweighted": float(np.mean(q0 <= 0)),
                 "frac_q0_le_0_weighted": float(w[q0 <= 0].sum() / w.sum()),
                 **{f"frac_status_{k}_unweighted": float(np.mean(st == k)) for k in (1, 2)},
                 **{f"frac_status_{k}_weighted": float(w[st == k].sum() / w.sum()) for k in (1, 2)}}
    base = (st == 0) & np.isfinite(q0) & np.isfinite(ea) & np.isfinite(w) & (w > 0)
    out["excluded_R1_R2"] = {"n": int((~base).sum()), "weight_frac": float(w[~base & np.isfinite(w)].sum() / w[np.isfinite(w)].sum())}
    cell, names = coarse_cells(pt, pz, base)
    out["cells"] = {str(k): v for k, v in names.items()}
    out["cells"]["-1"] = {"outside": True, "n_eligible": int((base & (cell < 0)).sum())}
    # reading 1
    groups = {"overall": base, **{str(c): base & (cell == c) for c in list(names) + [-1]}}
    out["R1"] = {g: ({"n": int(m.sum()), "pearson": wpearson(q0[m], ea[m], w[m]), "spearman": wspearman(q0[m], ea[m], w[m])}
                     if m.sum() > 2 else {"n": int(m.sum())}) for g, m in groups.items()}
    # reading 2
    out["R2"] = []
    for lo, hi in zip(EAV_BINS[:-1], EAV_BINS[1:]):
        m = base & (ea >= lo) & ((ea < hi) if hi != EAV_BINS[-1] else (ea <= hi))
        row = {"eavail_GeV": [lo, hi], "n": int(m.sum()), "weight": float(w[m].sum())}
        if m.sum():
            row["q0_q16_q50_q84_GeV"] = wquantile(q0[m], w[m], (0.16, 0.50, 0.84))
        out["R2"].append(row)
    # reading 3
    out["R3"] = {}
    for tname in ("q3_true", "W_true"):
        y = np.asarray(z[tname], np.float64)
        elig = base & np.isfinite(y) & np.isfinite(pt) & np.isfinite(pz)
        idx = np.flatnonzero(elig)
        perm = np.random.default_rng(SPLIT_SEED).permutation(idx.size)
        half = idx.size // 2
        h1, h2 = idx[perm[:half]], idx[perm[half:]]
        rs = np.random.default_rng(SUB_SEED)
        fit = np.sort(rs.choice(h1, size=min(n_fit, h1.size), replace=False))
        sco = np.sort(rs.choice(h2, size=min(n_score, h2.size), replace=False))
        feats = {"A": np.column_stack([pt, pz, ea]), "B": np.column_stack([pt, pz, ea, q0])}
        res = {"n_eligible": int(idx.size), "n_excluded_nonfinite_target": int((base & ~np.isfinite(y)).sum()),
               "n_fit": int(fit.size), "n_score": int(sco.size)}
        resid = {}
        for k, X in feats.items():
            m = HistGradientBoostingRegressor(**hgb)
            m.fit(X[fit], y[fit], sample_weight=w[fit])
            resid[k] = y[sco] - m.predict(X[sco])

        def widths(r, ww):
            q16, q84 = wquantile(r, ww, (0.16, 0.84))
            return {"half68": 0.5 * (q84 - q16), "rms": float(np.sqrt(np.sum(ww * r * r) / ww.sum()))}
        per = {}
        for g in ["overall"] + [str(c) for c in list(names) + [-1]]:
            sel = np.ones(sco.size, bool) if g == "overall" else (cell[sco] == int(g))
            if sel.sum() < CELL_MIN_SCORE:
                per[g] = {"n_score": int(sel.sum())}
                continue
            a, b = widths(resid["A"][sel], w[sco][sel]), widths(resid["B"][sel], w[sco][sel])
            per[g] = {"n_score": int(sel.sum()), "A": a, "B": b,
                      "ratio_B_over_A": {"half68": b["half68"] / a["half68"], "rms": b["rms"] / a["rms"]}}
        res["by_group"] = per
        out["R3"][tname] = res
    return out


def render(r: dict) -> str:
    L = ["q0 study readings (descriptive; PLAN.md at aae34aab). Units GeV.", ""]
    L.append(f"R4  rows {r['n_rows']}: q0<=0 {r['R4']['frac_q0_le_0_unweighted']:.3g} (w {r['R4']['frac_q0_le_0_weighted']:.3g}); "
             f"status1 {r['R4']['frac_status_1_unweighted']:.3g}; status2 {r['R4']['frac_status_2_unweighted']:.3g}")
    o = r["R1"]["overall"]
    L.append(f"R1  overall corr(q0, E_avail): Pearson {o['pearson']:.4f}, Spearman {o['spearman']:.4f} (n {o['n']})")
    for g, v in r["R1"].items():
        if g != "overall" and "pearson" in v:
            c = r["cells"][g]
            tag = "outside" if g == "-1" else f"pT {c['pt']} pz {c['pz']}"
            L.append(f"     {tag}: Pearson {v['pearson']:.4f} Spearman {v['spearman']:.4f} (n {v['n']})")
    L.append("R2  q0 quantiles (16/50/84) by reco E_avail bin:")
    for row in r["R2"]:
        qs = row.get("q0_q16_q50_q84_GeV")
        L.append(f"     E_avail {row['eavail_GeV']}: n {row['n']}" + (f"  {qs[0]:.4f} / {qs[1]:.4f} / {qs[2]:.4f}" if qs else ""))
    for t, res in r["R3"].items():
        o = res["by_group"]["overall"]
        L.append(f"R3  {t}: A (pT,p||,E_avail) half68 {o['A']['half68']:.4f} rms {o['A']['rms']:.4f}; "
                 f"B (+q0) half68 {o['B']['half68']:.4f} rms {o['B']['rms']:.4f}; ratio B/A half68 "
                 f"{o['ratio_B_over_A']['half68']:.3f} rms {o['ratio_B_over_A']['rms']:.3f}")
        for g, v in res["by_group"].items():
            if g == "overall" or "A" not in v:
                continue
            c = r["cells"][g]
            tag = "outside" if g == "-1" else f"pT {c['pt']} pz {c['pz']}"
            L.append(f"     {tag}: ratio half68 {v['ratio_B_over_A']['half68']:.3f} rms {v['ratio_B_over_A']['rms']:.3f} (n {v['n_score']})")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--npz", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        print(f"REFUSED: {a.out} exists", file=sys.stderr)
        return 9
    got = hashlib.sha256(a.npz.read_bytes()).hexdigest()
    if got != NPZ_SHA:
        print(f"REFUSED: {a.npz} is {got}, not {NPZ_SHA}", file=sys.stderr)
        return 9
    if os.environ.get("OMP_NUM_THREADS") != str(THREADS):
        print(f"REFUSED: OMP_NUM_THREADS must be {THREADS} (matched threads, PLAN 3)", file=sys.stderr)
        return 9
    t0 = time.time()
    z = dict(np.load(a.npz))
    r = readings(z)
    import sklearn
    r["meta"] = {"npz_sha256": got, "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                 "numpy": np.__version__, "sklearn": sklearn.__version__, "threads": THREADS, "hgb": HGB,
                 "seconds": time.time() - t0}
    a.out.mkdir(parents=True)
    (a.out / "results.json").write_text(json.dumps(r, indent=1) + "\n")
    (a.out / "results.txt").write_text(render(r))
    print(json.dumps({"written": str(a.out), "seconds": round(time.time() - t0, 1)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
