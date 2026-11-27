"""C-E3 tail diagnostic for e1 (read-only, MC-only): where the [8, 15) tail of |q3'/q3 - 1| comes from with true Eν.

Declared in DECLARATION.md before it runs (the director's ruling, 2026-11-27). It is run on login02 by ce3-diag.sh,
which embeds the built copy (ce3_diag_remote.py, with PINS filled from committed records) and checks its sha256.

Inputs, each opened O_NOATIME|O_NOFOLLOW through a no-symlink descriptor walk, read once into memory, sha256-checked
against PINS, atime checked unchanged, and never written:
  - the 12 S1 dumps lat_<PL>.npz (keys MCreco, MCgen, w_reco, pass_reco, pass_truth only; never "measured");
  - flux4's 12 factor products flux-factors-<PL>.npz (key "energy" only).
Per p∥ stratum (reco p∥, as C-E3 strata it), on the rows C-E3 controls, it reports:
  (i)   C-E3's error as bound: fd_rpd_reco.energy_statistics at 2415e8d6, copied verbatim below, pooled over the 12
        playlists in order and passed through the bound weighted_quantiles. It must reproduce d2s0e1's STOP record
        (median 0.0009871258308031816, q99 0.0301471583174564 in 8:15) bit for bit, or the run fails its self-check;
  (ii)  the exact kinematics: Q² = 2Eν(Eμ − |pμ| cosθ) − mμ², q3² = Q² + (Eν − Eμ)²;
  (iii) (i) with MCgen's float32 rounding of p_T and p∥: the error at the four corners pt ± h_pt, pz ± h_pz (h half the
        float32 spacing), row by row, giving bounds on each quantile;
the weighted median, 99th and 99.9th percentiles of each, C-E1's kinematic fraction, and where the rows over the 0.03
gate sit in (p_T, p∥, Eν, q3), including how many have Eν within 1% of Eμ.
Nothing is written on the cluster: one JSON object on stdout, messages on stderr. Exit 0: report written (any reading);
9: an input or the self-check failed (report written with verdict SELF-CHECK-FAILED or INPUT-FAILED); 2: refused.
"""

import hashlib
import io
import json
import os
import stat
import sys
import time

import numpy as np

PINS = {}  # filled by build_diag.py from committed records: {"lat": {PL: [path, sha256]}, "products": {...}}
BASE = "/pscratch/sd/j/josephrb/"
PLAYLISTS = ("1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P")
M_MUON = 0.1056583755  # fd_rpd_reco.py:91 at 2415e8d6
CE1_MIN, CE3_MEDIAN, CE3_Q99 = 0.999, 0.002, 0.03  # fd_rpd_reco.py:99-101
STOP_RECORD = {"8:15": (0.0009871258308031816, 0.0301471583174564)}  # d2s0e1 run-20261127 d2-predict.STOP.json
STRATA = ((1.5, 8), (8, 15), (15, 60))
LAT_KEYS = ("MCreco", "MCgen", "w_reco", "pass_reco", "pass_truth")
assert "measured" not in LAT_KEYS  # blinding: the measured key is never read
FRACTIONS = np.array([0.5, 0.99, 0.999])
EDGES = {
    "pt": [0, 0.07, 0.15, 0.25, 0.4, 0.7, 1.0, 1.5, 4.5, 1e9],
    "pz_true": [0, 1.5, 4.5, 8, 10, 15, 20, 60, 1e9],
    "enu": [0, 2, 4, 6, 8, 10, 15, 20, 50, 1e9],
    "q3": [0, 0.1, 0.2, 0.4, 0.8, 1.2, 2.0, 100, 1e9],
}


def stop(why, rc=2):
    sys.stderr.write("STOP ce3-diag: %s\n" % why)
    sys.stderr.flush()
    sys.exit(rc)


def utc(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def read_pinned(path, want):
    """O_NOATIME|O_NOFOLLOW read through a no-symlink descriptor walk; sha256 and atime checked."""
    if not path.startswith(BASE) or ".." in path.split("/"):
        stop("%s is not under %s" % (path, BASE))
    st0 = os.lstat(path)
    if stat.S_ISLNK(st0.st_mode) or not stat.S_ISREG(st0.st_mode):
        stop("%s is not a regular file" % path, 9)
    parts = path[len(BASE):].split("/")
    d = os.open(BASE.rstrip("/"), os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for comp in parts[:-1]:
            nd = os.open(comp, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=d)
            os.close(d)
            d = nd
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOATIME | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=d)
    finally:
        os.close(d)
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_ino != st0.st_ino:
            stop("%s changed between lstat and open" % path, 9)
        chunks, h = [], hashlib.sha256()
        while True:
            b = os.read(fd, 1 << 24)
            if not b:
                break
            chunks.append(b)
            h.update(b)
    finally:
        os.close(fd)
    st1 = os.lstat(path)
    data = b"".join(chunks)
    row = {"path": path, "sha256": h.hexdigest(), "bytes": len(data), "atime_unchanged": st1.st_atime == st0.st_atime}
    row["ok"] = row["sha256"] == want and row["atime_unchanged"] and len(data) == st0.st_size
    return data, row


# ---- copied verbatim from fd_rpd_reco.py at 2415e8d6 (weighted_quantiles :874-886; energy_statistics' error and
#      strata selection :936-961). test_ce3_diag.py checks these equal the bound functions on fixtures. ----
def weighted_quantiles(values, weights, fractions):
    order = np.argsort(values, kind="stable")
    cumulative = np.cumsum(weights[order])
    if not (len(cumulative) and cumulative[-1] > 0):
        raise ValueError("empty weighted distribution")
    indices = np.searchsorted(cumulative, fractions * cumulative[-1], side="left")
    return np.asarray(values[order[np.minimum(indices, len(order) - 1)]], dtype=float)


def bound_error(truth, energy):
    pt, pz = truth[:, 0], truth[:, 1]
    muon = np.sqrt(pt * pt + pz * pz + M_MUON * M_MUON)
    theta = np.arctan2(truth[:, 0], truth[:, 1])
    with np.errstate(invalid="ignore", divide="ignore"):
        q3 = np.sqrt(4 * energy * muon * np.sin(theta / 2) ** 2 + (energy - muon) ** 2)
        error = np.abs(q3 / truth[:, 3] - 1)
    return error, muon, theta


def strata_masks(reco_pz, weights, energy, muon):
    out = {}
    for low, high in STRATA:
        selected = (reco_pz >= low) & ((reco_pz <= high) if high == 60 else (reco_pz < high)) & (weights > 0)
        valid = np.isfinite(energy) & (energy >= muon)
        out["%s:%s" % (low, high)] = (selected, selected & valid)
    return out
# ---- end of the verbatim copy ----


def exact_error(truth, energy, muon, theta):
    pt, pz = truth[:, 0], truth[:, 1]
    p = np.sqrt(pt * pt + pz * pz)
    with np.errstate(invalid="ignore", divide="ignore"):
        q2 = 2 * energy * (muon - p * np.cos(theta)) - M_MUON * M_MUON
        q3 = np.sqrt(q2 + (energy - muon) ** 2)
        error = np.abs(q3 / truth[:, 3] - 1)
    return error, q2


def corner_errors(truth32, energy):
    """(i)'s error at the four float32-rounding corners of (p_T, p∥); returns the row-wise min and max."""
    pt32, pz32 = truth32[:, 0], truth32[:, 1]
    hpt = np.spacing(pt32).astype(np.float64) / 2
    hpz = np.spacing(pz32).astype(np.float64) / 2
    base = truth32.astype(np.float64)
    lo = hi = None
    for spt in (-1, 1):
        for spz in (-1, 1):
            t = base.copy()
            t[:, 0] = base[:, 0] + spt * hpt
            t[:, 1] = base[:, 1] + spz * hpz
            e, _, _ = bound_error(t, energy)
            lo = e if lo is None else np.fmin(lo, e)
            hi = e if hi is None else np.fmax(hi, e)
    return lo, hi


def wq(values, weights):
    finite = np.isfinite(values)
    if not finite.any() or weights[finite].sum() <= 0:
        return [None, None, None]
    return [float(v) for v in weighted_quantiles(values[finite], weights[finite], FRACTIONS)]


def share(values, weights, edges):
    idx = np.clip(np.searchsorted(np.asarray(edges, dtype=float), values, side="right") - 1, 0, len(edges) - 2)
    tot = float(weights.sum())
    return [round(float(weights[idx == i].sum()) / tot, 6) if tot > 0 else None for i in range(len(edges) - 1)]


def main():
    if not hasattr(os, "O_NOATIME"):
        stop("this platform has no O_NOATIME")
    if set(PINS) != {"lat", "products"} or sorted(PINS["lat"]) != sorted(PLAYLISTS):
        stop("PINS not filled (run build_diag.py)")
    started = time.time()
    report = {"schema": "rpd-reco-ce3-diag/1", "started": utc(started), "host": os.uname()[1],
              "python": sys.version.split()[0], "numpy": np.__version__, "inputs": [], "strata": {}}
    pooled = {k: {n: [] for n in ("e1", "e2", "lo", "hi", "w", "pt", "pzt", "pzr", "enu", "emu", "q3", "theta", "q2")}
              for k in ("%s:%s" % s for s in STRATA)}
    totals = {k: [0.0, 0.0] for k in pooled}
    input_ok = True
    for pl in PLAYLISTS:
        lat_b, lat_row = read_pinned(*PINS["lat"][pl])
        prod_b, prod_row = read_pinned(*PINS["products"][pl])
        report["inputs"] += [lat_row, prod_row]
        if not (lat_row["ok"] and prod_row["ok"]):
            input_ok = False
            continue
        with np.load(io.BytesIO(lat_b), allow_pickle=False) as z:
            arrays = {k: np.asarray(z[k]) for k in LAT_KEYS}  # only these keys are ever decompressed
        with np.load(io.BytesIO(prod_b), allow_pickle=False) as z:
            energy = np.asarray(z["energy"], dtype=float)
        del lat_b, prod_b
        mcgen32 = arrays["MCgen"]
        if mcgen32.dtype != np.float32:
            input_ok = False
            report["inputs"].append({"playlist": pl, "problem": "MCgen is %s, not float32" % mcgen32.dtype})
            continue
        values = np.asarray(arrays["MCreco"], dtype=float)
        truth = np.asarray(mcgen32, dtype=float)
        reco = np.asarray(arrays["pass_reco"], dtype=bool)
        weights = np.asarray(arrays["w_reco"], dtype=float) * reco
        if energy.shape != (len(truth),):
            input_ok = False
            report["inputs"].append({"playlist": pl, "problem": "energy rows differ"})
            continue
        energy = energy * 1.0  # scale 1.0, as d2-predict calls it
        e1, muon, theta = bound_error(truth, energy)
        e2, q2 = exact_error(truth, energy, muon, theta)
        lo, hi = corner_errors(mcgen32, energy)
        for k, (selected, controlled) in strata_masks(values[:, 1], weights, energy, muon).items():
            totals[k][0] += float(weights[selected].sum())
            totals[k][1] += float(weights[controlled].sum())
            c = controlled
            for n, a in (("e1", e1), ("e2", e2), ("lo", lo), ("hi", hi), ("w", weights), ("pt", truth[:, 0]),
                         ("pzt", truth[:, 1]), ("pzr", values[:, 1]), ("enu", energy), ("emu", muon),
                         ("q3", truth[:, 3]), ("theta", theta), ("q2", q2)):
                pooled[k][n].append(a[c])
        del arrays, values, truth, weights, energy, e1, e2, lo, hi, q2
    if not input_ok:
        report["verdict"] = "INPUT-FAILED"
        sys.stdout.write(json.dumps(report, indent=1, sort_keys=True) + "\n")
        sys.exit(9)
    self_ok = True
    passes_ii = True
    for k, cols in pooled.items():
        a = {n: np.concatenate(v) for n, v in cols.items()}
        w = a["w"]
        median1, q991 = (float(x) for x in weighted_quantiles(a["e1"], w, np.array([0.5, 0.99])))
        row = {
            "C-E1_fraction": totals[k][1] / totals[k][0] if totals[k][0] > 0 else None,
            "rows": int(len(w)),
            "i_bound": {"median_q99_q999": wq(a["e1"], w), "nonfinite": int((~np.isfinite(a["e1"])).sum())},
            "ii_exact": {"median_q99_q999": wq(a["e2"], w), "nonfinite": int((~np.isfinite(a["e2"])).sum()),
                         "negative_Q2_rows": int((a["q2"] < 0).sum())},
            "iii_float32": {"rowwise_min_median_q99_q999": wq(a["lo"], w),
                            "rowwise_max_median_q99_q999": wq(a["hi"], w),
                            "max_abs_shift": float(np.nanmax(np.maximum(a["hi"] - a["e1"], a["e1"] - a["lo"])))},
        }
        row["i_bound"]["gates"] = median1 <= CE3_MEDIAN and q991 <= CE3_Q99
        m2, q2v = row["ii_exact"]["median_q99_q999"][:2]
        row["ii_exact"]["gates"] = m2 is not None and m2 <= CE3_MEDIAN and q2v <= CE3_Q99 \
            and row["ii_exact"]["nonfinite"] == 0
        passes_ii = passes_ii and row["ii_exact"]["gates"]
        if k in STOP_RECORD:
            row["self_check"] = {"stop_record": list(STOP_RECORD[k]), "recomputed": [median1, q991],
                                 "bit_equal": (median1, q991) == STOP_RECORD[k]}
            self_ok = self_ok and row["self_check"]["bit_equal"]
        if k == "1.5:8":
            self_ok = self_ok and row["i_bound"]["gates"] and row["C-E1_fraction"] >= CE1_MIN
        tail = a["e1"] > CE3_Q99
        tw = w[tail]
        near = np.abs(a["enu"] / a["emu"] - 1) <= 0.01
        row["tail_over_gate"] = {
            "rows": int(tail.sum()),
            "weight_fraction": float(tw.sum() / w.sum()) if w.sum() > 0 else None,
            "enu_within_1pct_of_emu": {"rows": int((tail & near).sum()),
                                       "weight_fraction_of_tail": float(w[tail & near].sum() / tw.sum()) if tw.sum() > 0 else None},
            "quantiles_05_50_95": {n: ([float(x) for x in weighted_quantiles(a[n][tail], tw, np.array([0.05, 0.5, 0.95]))]
                                       if tail.any() and tw.sum() > 0 else None)
                                   for n in ("pt", "pzt", "pzr", "enu", "emu", "q3", "theta", "q2", "e2")},
            "weight_share_by_bin": {n: {"edges": EDGES[n], "share": share(a[{"pt": "pt", "pz_true": "pzt", "enu": "enu",
                                                                              "q3": "q3"}[n]][tail], tw, EDGES[n])}
                                    for n in EDGES} if tail.any() else None,
        }
        row["stratum_enu_within_1pct_of_emu_weight_fraction"] = float(w[near].sum() / w.sum()) if w.sum() > 0 else None
        report["strata"][k] = row
    if not self_ok:
        report["verdict"] = "SELF-CHECK-FAILED"
        sys.stdout.write(json.dumps(report, indent=1, sort_keys=True) + "\n")
        sys.exit(9)
    report["verdict"] = "R-A (ii) passes every stratum" if passes_ii else "R-B (ii) does not pass every stratum"
    report["seconds"] = round(time.time() - started, 1)
    sys.stdout.write(json.dumps(report, indent=1, sort_keys=True) + "\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
