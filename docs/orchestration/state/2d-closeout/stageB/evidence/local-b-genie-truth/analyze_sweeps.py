"""Analyze sweeps.npz/json (read_sweeps.py) for KI-92 and KI-93. numpy only."""
import json, re, sys
from collections import defaultdict
import numpy as np

base = sys.argv[1]
A = np.load(base + ".npz")
M = json.load(open(base + ".json"))
IN = ["hDataReco2D", "hBkgReco2D", "hMeasSub2D", "hMeasTrain2D", "hTruth2D", "hEffNum", "hEffDen",
      "hOFInputTruth2D", "hOFTruthDenom2D", "hFlux_pt"]
OUT = ["hUnfold2D", "hOFCompleteness2D", "hXSec2D"]
ref = A["ref/E_U|hXSec2D"][1:-1, 1:-1]
rep = ref.ravel() > 0
assert rep.sum() == 205


def get(tag, h):
    k = f"{tag}|{h}"
    return A[k] if k in A.files else None


def eq(a, b):
    return None if a is None or b is None else bool(np.array_equal(a, b))


def vec(tag):
    return get(tag, "hXSec2D")[1:-1, 1:-1].ravel()[rep]


def maxrel(a, b):
    if a is None or b is None:
        return None
    m = b != 0
    return float(np.max(np.abs(a[m] - b[m]) / np.abs(b[m]))) if m.any() else float(np.max(np.abs(a)))


res = {}
cvtag = {"pn": "pn/CV", "nw": "nw/CV", "may": "may/CV"}
res["cv_identity"] = {s: {"sha256": M[t]["sha256"], "realpath": M[t]["realpath"],
                          "max_rel_vs_E_U": maxrel(vec(t), vec("ref/E_U")),
                          "inputs_bitwise_equal_E_U": {h: eq(get(t, h), get("ref/E_U", h)) for h in IN}}
                      for s, t in cvtag.items()}
res["E_U_sha256"] = M["ref/E_U"]["sha256"]

for s in ("pn", "nw", "may"):
    cv = cvtag[s]
    tags = sorted(t for t in M if t.startswith(s + "/") and t != cv)
    bands = defaultdict(dict)
    rows = {}
    for t in tags:
        band, idx = re.match(r".*/(.+)_(\d+)$", t).groups()
        bands[band][int(idx)] = t
        r = {"params_equal_cv": {k: M[t]["params"].get(k) == M[cv]["params"].get(k) for k in M[cv]["params"]},
             "fluxSource": M[t]["named"].get("fluxSource"),
             "inputs_equal_cv": {h: eq(get(t, h), get(cv, h)) for h in IN},
             "inputs_maxrel_cv": {h: maxrel(get(t, h), get(cv, h)) for h in IN},
             "xsec_maxrel_cv": maxrel(vec(t), vec(cv)),
             "keys_equal_cv": M[t]["keys"] == M[cv]["keys"], "mtime": M[t]["mtime"],
             "sha256": M[t]["sha256"], "realpath": M[t]["realpath"]}
        rows[t] = r
    res[s + "_rows"] = rows
    # no-op universes: every input bitwise equal to CV
    noop = [t for t, r in rows.items() if all(v is True for v in r["inputs_equal_cv"].values())]
    res[s + "_noop"] = {t: rows[t]["xsec_maxrel_cv"] for t in noop}
    # truth-side inputs equal to CV (expected for laterals)
    res[s + "_truth_equal_cv"] = sorted(t for t, r in rows.items()
                                        if r["inputs_equal_cv"]["hTruth2D"] is True and r["inputs_equal_cv"]["hEffDen"] is True)
    res[s + "_data_equal_cv_all"] = {str(v): sum(1 for r in rows.values() if r["inputs_equal_cv"]["hDataReco2D"] is v) for v in (True, False, None)}
    res[s + "_params_nonflux_all_equal"] = all(all(r["params_equal_cv"].values()) for t, r in rows.items()
                                               if "/Flux_" not in t)
    # Rvn1pi vs Rvp1pi
    rv = {}
    for i in (0, 1):
        a, b = bands["Rvn1pi"][i], bands["Rvp1pi"][i]
        rv[str(i)] = {"inputs_bitwise_equal": {h: eq(get(a, h), get(b, h)) for h in IN},
                      "xsec_maxrel": maxrel(vec(a), vec(b)),
                      "xsec_bitwise": bool(np.array_equal(vec(a), vec(b)))}
    res[s + "_Rvn1pi_vs_Rvp1pi"] = rv
    # band covariances, MAT mean-centred 1/N (analyze_universes.py:256-259)
    c0 = vec(cv)
    cov = {}
    for band, d in bands.items():
        D = np.stack([vec(d[i]) - c0 for i in sorted(d)])
        Z = D - D.mean(axis=0, keepdims=True)
        cov[band] = Z.T @ Z / D.shape[0]
    tot = sum(cov.values())
    sig = np.sqrt(np.diag(tot))
    once = tot - cov["Rvp1pi"]
    s1 = np.sqrt(np.diag(once))
    rv_rel = np.sqrt(np.diag(cov["Rvn1pi"])) / c0
    res[s + "_cov"] = {
        "n_bands": len(cov), "n_universes": len(tags),
        "bands": {b: len(d) for b, d in sorted(bands.items())},
        "sqrt_trace_total": float(np.sqrt(np.trace(tot))),
        "Rvn1pi_rel_sigma_median": float(np.median(rv_rel)), "Rvn1pi_rel_sigma_max": float(rv_rel.max()),
        "Rvn1pi_vs_Rvp1pi_bandcov_maxabsdiff_over_max": float(np.max(np.abs(cov["Rvn1pi"] - cov["Rvp1pi"])) / np.max(np.abs(cov["Rvn1pi"]))),
        "count_once_sigma_ratio_median": float(np.median(s1 / sig)), "count_once_sigma_ratio_min": float(np.min(s1 / sig)),
        "count_once_frac_trace_change": float(np.trace(cov["Rvp1pi"]) / np.trace(tot)),
        "count_once_rel_frobenius": float(np.linalg.norm(cov["Rvp1pi"]) / np.linalg.norm(tot)),
        "total_rel_sigma_median": float(np.median(sig / c0)),
    }
    np.save(base + f"_{s}_totcov.npy", tot)
json.dump(res, open(base + "_analysis.json", "w"), indent=1, sort_keys=True)
