#!/usr/bin/env python3
"""MP-2 S2 step 3 (root_6_28, LightGBM 4.6): the event-level reweighting models and gates V1-V4, under the frozen
feature contract (feature_contract_draft.json 98141c2f..., addenda 8 and 9) and the readings recorded in
docs/orchestration/state/measurement-paper/phase1/mp2/S2-IMPLEMENTATION.md (named R1..Rn in the code).

  models  trains model (k, h, f) for one generator and feature set: Tune v1 C+H rows inside the fine grid and the
          generator's E_nu support, of half h outside fold f (at most 4,000,000, drawn uniformly), against the
          generator's harmonized events outside G-fold f; 10% of each class's training rows validate (R1); class
          weights sum to half the split's rows per class; early stopping after 200 rounds on the weighted binary
          logloss. It predicts every Tune row of half h, fold f and writes the odds p/(1-p), p clipped to
          [1e-9, 1 - 1e-9]. A model file is never overwritten.
  gates   assembles the K = 5 replicas (each Tune row is predicted by exactly one model per replica), fixes the
          global constant c_k (R2), and evaluates V2, V3, V4 for every replica (R3) and V1 on replica 0 (R4).

Usage: python3 mp2_s2_fit.py models --gen G --fset primary|fallback --tasks k:h:f,... --harm DIR [DIR] --out DIR --threads T
       python3 mp2_s2_fit.py gates  --gen G --fset primary|fallback --harm DIR [DIR] --out DIR --threads T
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402

import s5p_stage1_inspect as s1  # noqa: E402

CONTRACT_SHA = "98141c2f22f4fc3f2a7f5b30a0c509d6a29a37d145a72ea802623a2a2d6630cd"
N_MCGEN = 32_849_103
ASIMOV_SEED = 520261101
K = 5
FOLD_KEY = [2026102100 + k for k in range(K)]
LGBM_SEED = [2026102110 + k for k in range(K)]
V1_SPLIT_SEED, GVG_SPLIT_SEED = 2026102140, 2026102141
TUNE_MAX = 4_000_000
SUPPORT = {"genie_cv": (0.0, 100.0), "genie_mec": (0.0, 100.0), "nuwro_ch": (0.5, 100.0), "gibuu_ch": (0.0, 20.0)}
F_PRIMARY = ["pt", "pz", "eavail", "q3", "W", "enu", "sum_p_KE", "sum_pipm_KE", "sum_em_E", "sum_n_KE", "E_other",
             "n_p", "n_pipm", "p1_KE", "p1_cos", "pipm1_KE", "pipm1_cos", "n1_KE"]
F_FALLBACK = ["pt", "pz", "eavail", "q3", "W", "enu", "sum_p_KE", "sum_pipm_KE", "sum_em_E", "sum_n_KE", "E_other"]
FSETS = {"primary": F_PRIMARY, "fallback": F_FALLBACK}
PARAMS = {"objective": "binary", "learning_rate": 0.05, "num_leaves": 63, "min_child_samples": 200, "n_estimators": 3000,
          "subsample": 0.8, "subsample_freq": 1, "colsample_bytree": 1.0, "reg_lambda": 0.0, "deterministic": True,
          "force_row_wise": True, "verbose": -1}
EARLY_STOP = 200
VAL_FRAC = 0.10
P_CLIP = 1e-9
V2_CHI2NDF, V2_PULL, V2_NMIN = 1.5, 3.0, 20
V4_ESS, V4_MAXW = 0.3, 50.0
V1_MARGIN = 0.005
# R5: V3 bins (declared before any fit); multiplicities and counts by integer, the last bin open
V3_BINS = {"v3_n_mult_KE10": np.r_[np.arange(0, 11) - 0.5, np.inf], "v3_p_mult_KE20": np.r_[np.arange(0, 11) - 0.5, np.inf],
           "v3_pi0_count": np.r_[np.arange(0, 7) - 0.5, np.inf],
           "neutron_KE_MeV": np.array([0.0, 10.0, 20.0, 50.0, 100.0, 200.0, 500.0, 1000.0, 2000.0, np.inf])}


def sha256(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def splitmix64(x: np.ndarray, key: int) -> np.ndarray:
    """half_mask's mixer (s5c_pseudo.half_mask), unreduced."""
    with np.errstate(over="ignore"):
        z = (np.asarray(x, np.uint64) ^ np.uint64(key)) + np.uint64(0x9E3779B97F4A7C15)
        z = (z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
        z = (z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
        return z ^ (z >> np.uint64(31))


def split_key_for(seed: int) -> int:
    return (seed * 0x9E3779B1 + 0x5C5C) % (2 ** 61 - 1)       # s5c_pseudo.split_key_for


def tune_half(i):
    """The contract's half h(i) = s5c_pseudo.half_mask(n, split_key_for(ASIMOV_SEED)) at the global MCgen row i."""
    return (splitmix64(i, split_key_for(ASIMOV_SEED)) & np.uint64(1)).astype(np.int8)


def tune_fold(i, k):
    return ((splitmix64(i, FOLD_KEY[k]) >> np.uint64(1)) % np.uint64(5)).astype(np.int8)


def gen_fold(j, k):
    return (splitmix64(j, FOLD_KEY[k] + 1) % np.uint64(5)).astype(np.int8)     # the JSON's G-fold, literally


def load(harm, gen, fset):
    """The harmonized events of G and the Tune C+H rows inside G's support (from the harmonize outputs)."""
    hd = next(Path(d) for d in harm if (Path(d) / f"events_{gen}.npz").exists())
    td = next(Path(d) for d in harm if (Path(d) / "tune_CH.npz").exists())
    feats = FSETS[fset]
    ev = np.load(hd / f"events_{gen}.npz")
    tz = np.load(td / "tune_CH.npz")
    lo, hi = SUPPORT[gen]
    enu = tz["enu"]
    ins = (enu >= lo) & (enu <= hi)
    T = {"X": np.column_stack([tz[f][ins] for f in feats]).astype(np.float64), "w": tz["w_truth"][ins],
         "i": tz["i"][ins].astype(np.int64), "fine": tz["fine"][ins], "n_all": int(enu.size), "in_support": ins}
    Gd = {"X": np.column_stack([ev[f] for f in feats]).astype(np.float64), "w": ev["c"], "j": ev["j"].astype(np.int64),
          "fine": ev["fine"]}
    if np.any(np.diff(T["i"]) <= 0):
        raise SystemExit("the Tune rows are not in ascending MCgen order")
    src = {"events": {"path": str(hd / f"events_{gen}.npz"), "sha256": sha256(hd / f"events_{gen}.npz")},
           "tune": {"path": str(td / "tune_CH.npz"), "sha256": sha256(td / "tune_CH.npz")}}
    return T, Gd, tz, ev, src, hd


def balanced(wa, wb):
    """Class weights: each class sums to half the split's row count (S0's rule)."""
    n = wa.size + wb.size
    return wa * (0.5 * n / wa.sum()), wb * (0.5 * n / wb.sum())


def fit_one(Xa, wa, Xb, wb, seed, threads, val_seed, n_estimators=None):
    """Label 0 = a (Tune), 1 = b (G). R1: the validation rows are 10% of EACH class, drawn with val_seed."""
    import lightgbm as lgb
    r = np.random.default_rng(val_seed)
    va, vb = r.random(wa.size) < VAL_FRAC, r.random(wb.size) < VAL_FRAC
    twa, twb = balanced(wa[~va], wb[~vb])
    vwa, vwb = balanced(wa[va], wb[vb])
    X = np.vstack([Xa[~va], Xb[~vb]])
    y = np.r_[np.zeros((~va).sum()), np.ones((~vb).sum())]
    Xv = np.vstack([Xa[va], Xb[vb]])
    yv = np.r_[np.zeros(va.sum()), np.ones(vb.sum())]
    p = dict(PARAMS, random_state=seed, n_jobs=threads)
    if n_estimators is not None:
        p["n_estimators"] = int(n_estimators)
    m = lgb.LGBMClassifier(**p)
    t0 = time.time()
    if n_estimators is None:
        m.fit(X, y, sample_weight=np.r_[twa, twb], eval_set=[(Xv, yv)], eval_sample_weight=[np.r_[vwa, vwb]],
              eval_metric="binary_logloss", callbacks=[lgb.early_stopping(EARLY_STOP, verbose=False)])
        best = int(m.best_iteration_)
        vl = float(m.best_score_["valid_0"]["binary_logloss"])
    else:
        m.fit(X, y, sample_weight=np.r_[twa, twb])
        best, vl = int(n_estimators), None
    return m, {"best_iteration": best, "valid_logloss": vl, "fit_s": round(time.time() - t0, 2),
               "n_train": [int((~va).sum()), int((~vb).sum())], "n_valid": [int(va.sum()), int(vb.sum())]}


def odds(m, X, threads):
    t0 = time.time()
    p = m.predict_proba(X, num_iteration=m.best_iteration_ if getattr(m, "best_iteration_", None) else None)[:, 1]
    p = np.clip(p, P_CLIP, 1.0 - P_CLIP)
    return p / (1.0 - p), round(time.time() - t0, 2)


def cmd_models(a):
    T, Gd, _, _, src, _ = load(a.harm, a.gen, a.fset)
    h_all = tune_half(T["i"])
    out = a.out
    out.mkdir(parents=True, exist_ok=True)
    for tk in a.tasks.split(","):
        k, h, f = (int(x) for x in tk.split(":"))
        target = out / f"model_{a.gen}_{a.fset}_k{k}h{h}f{f}.npz"
        if target.exists():
            print("exists, skipped:", target, flush=True)
            continue
        t0 = time.time()
        fo = tune_fold(T["i"], k)
        tr = np.nonzero((h_all == h) & (fo != f))[0]
        if tr.size > TUNE_MAX:
            sub_seed = 2026102120 + 100 * k + 10 * h + f
            tr = np.sort(np.random.default_rng(sub_seed).choice(tr, size=TUNE_MAX, replace=False))
        gtr = gen_fold(Gd["j"], k) != f
        m, info = fit_one(T["X"][tr], T["w"][tr], Gd["X"][gtr], Gd["w"][gtr], LGBM_SEED[k], a.threads,
                          val_seed=[LGBM_SEED[k], h, f])
        pr = np.nonzero((h_all == h) & (fo == f))[0]
        od, pred_s = odds(m, T["X"][pr], a.threads)
        ru = resource.getrusage(resource.RUSAGE_SELF)
        info.update(gen=a.gen, fset=a.fset, k=k, h=h, f=f, n_tune_pool=int(((h_all == h) & (fo != f)).sum()),
                    n_gen_train_pool=int(gtr.sum()), n_pred=int(pr.size), predict_s=pred_s, wall_s=round(time.time() - t0, 2),
                    threads=a.threads, maxrss_kb=ru.ru_maxrss, slurm_job=os.environ.get("SLURM_JOB_ID"), sources=src,
                    code_sha256=sha256(Path(__file__).resolve()))
        np.savez(target, odds=od, i=T["i"][pr], meta_json=np.asarray(json.dumps(info)))
        print("MODEL", json.dumps({k_: info[k_] for k_ in ("gen", "fset", "k", "h", "f", "best_iteration", "valid_logloss",
                                                            "fit_s", "predict_s", "n_train", "n_pred", "wall_s")}), flush=True)
    return 0


# ---------------------------------------------------------------- gates
def chi2_shape(tc, tv, tn, gc, gv, gn, nmin):
    """R6: shape closure. Both sides normalised to G's total over all bins; chi2 over bins with >= nmin raw entries on
    both sides; ndf = bins used - 1."""
    s = gc.sum() / tc.sum()
    use = (tn >= nmin) & (gn >= nmin)
    d = s * tc - gc
    var = s * s * tv + gv
    pull = np.where(var > 0, d / np.sqrt(np.where(var > 0, var, 1.0)), 0.0)
    chi2 = float(np.sum(pull[use] ** 2))
    ndf = int(use.sum()) - 1
    return {"scale": float(s), "n_bins_used": int(use.sum()), "chi2": chi2, "ndf": ndf,
            "chi2_ndf": chi2 / ndf if ndf > 0 else None, "max_abs_pull_used": float(np.max(np.abs(pull[use]))) if use.any() else None,
            "pull": pull, "use": use}


def cmd_gates(a):
    T, Gd, tz, ev, src, hd = load(a.harm, a.gen, a.fset)
    hy = json.loads((hd / f"hybrid_an_{a.gen}.json").read_text())
    rho_an = np.load(hy["rho_npz"]["path"])["rho"]
    if sha256(hy["rho_npz"]["path"]) != hy["rho_npz"]["sha256"]:
        raise SystemExit("rho_an digest differs from its record")
    prod = np.load(hd / f"harmonized_{a.gen}.npz")
    import gen5d_flux_reweight as gfr
    g5 = gfr.load_g5(gfr.DEFAULTS["gen5d_tree"])
    dV = g5.widths(*g5.AXES).reshape(-1)
    nfine = dV.size
    contract = json.loads(Path(a.contract).read_text())
    supported = contract["measurement"]["partition_J"]["supported_cells"]
    cmap, ncell = s1.coarse_map(s1.J_EDGES, supported)
    res = {"schema": "mp2-s2-gates/1", "gen": a.gen, "fset": a.fset, "argv": sys.argv, "slurm_job": os.environ.get("SLURM_JOB_ID"),
           "code_sha256": sha256(Path(__file__).resolve()), "sources": src, "hybrid_an": str(hd / f"hybrid_an_{a.gen}.json"),
           "replicas": {}}
    r_an = rho_an[T["fine"]]
    Gc_fine = prod["xsec_flat"] * dV
    Gv_fine = prod["sumw2_flat"] * dV ** 2
    Gn_fine = prod["nevt_flat"]
    W = {}
    for k in range(K):
        od = np.full(T["i"].size, np.nan)
        files = sorted(a.out.glob(f"model_{a.gen}_{a.fset}_k{k}h*f*.npz"))
        if len(files) != 10:
            raise SystemExit(f"replica {k}: {len(files)} model files, not 10")
        for fp in files:
            z = np.load(fp)
            idx = np.searchsorted(T["i"], z["i"])
            if not np.array_equal(T["i"][idx], z["i"]):
                raise SystemExit(f"{fp}: rows not in the Tune table")
            if np.any(np.isfinite(od[idx])):
                raise SystemExit(f"{fp}: a row predicted twice")
            od[idx] = z["odds"]
        if np.any(~np.isfinite(od)):
            raise SystemExit(f"replica {k}: {int((~np.isfinite(od)).sum())} rows without a prediction")
        c = float(np.sum(T["w"] * r_an) / np.sum(T["w"] * od))           # R2
        wG = c * od
        W[k] = wG
        w = T["w"] * wG
        N = int(w.size)
        ess = float(w.sum() ** 2 / np.sum(w * w))
        ess_t = float(T["w"].sum() ** 2 / np.sum(T["w"] ** 2))
        mean_w = float(np.sum(T["w"] * wG) / T["w"].sum())
        v4 = {"N_rows": N, "kish_ess": ess, "ess_over_N": ess / N, "ess_over_ess_wtruth": ess / ess_t,
              "max_wG_over_mean": float(wG.max() / mean_w), "share_rows_w_gt_50mean": float(np.mean(wG > 50 * mean_w))}
        v4["pass"] = bool(v4["ess_over_N"] >= V4_ESS and v4["max_wG_over_mean"] <= V4_MAXW)
        # V2: fine cells and J cells, shape (R6)
        tc = np.bincount(T["fine"], w, nfine)
        tv = np.bincount(T["fine"], w * w, nfine)
        tn = np.bincount(T["fine"], None, nfine).astype(float)
        fine = chi2_shape(tc, tv, tn, Gc_fine, Gv_fine, Gn_fine, V2_NMIN)
        rep = cmap >= 0
        jt = np.bincount(cmap[rep], tc[rep], ncell)
        jtv = np.bincount(cmap[rep], tv[rep], ncell)
        jg = np.bincount(cmap[rep], Gc_fine[rep], ncell)
        jgv = np.bincount(cmap[rep], Gv_fine[rep], ncell)
        s = fine["scale"]
        jpull = (s * jt - jg) / np.sqrt(s * s * jtv + jgv)
        v2 = {"fine": {k_: v_ for k_, v_ in fine.items() if k_ not in ("pull", "use")},
              "J": {"max_abs_pull": float(np.max(np.abs(jpull))), "n_beyond_3": int(np.sum(np.abs(jpull) > V2_PULL)),
                    "pulls": jpull.tolist()}}
        v2["pass"] = bool(fine["chi2_ndf"] is not None and fine["chi2_ndf"] <= V2_CHI2NDF and v2["J"]["n_beyond_3"] == 0)
        # V3 (R5, R6): held-out distributions
        v3 = {}
        for key, bins in V3_BINS.items():
            if key == "neutron_KE_MeV":
                tvv, tww = tz["nKE_val"], None
                sel_t = T["in_support"][tz["nKE_ev"]]
                pos_t = np.searchsorted(np.nonzero(T["in_support"])[0], tz["nKE_ev"][sel_t])
                tx, twt = tz["nKE_val"][sel_t], w[pos_t]
                gx, gwt = ev["nKE_val"], ev["c"][ev["nKE_ev"]]
            else:
                tx, twt = tz[key][T["in_support"]], w
                gx, gwt = ev[key], ev["c"]
            ib_t, ib_g = np.digitize(tx, bins) - 1, np.digitize(gx, bins) - 1
            nb = bins.size - 1
            r_ = chi2_shape(np.bincount(ib_t, twt, nb), np.bincount(ib_t, twt * twt, nb), np.bincount(ib_t, None, nb).astype(float),
                            np.bincount(ib_g, gwt, nb), np.bincount(ib_g, gwt * gwt, nb), np.bincount(ib_g, None, nb).astype(float), V2_NMIN)
            r_["pulls"] = r_.pop("pull").tolist()
            r_.pop("use")
            r_["pass"] = bool(r_["chi2_ndf"] is not None and r_["chi2_ndf"] <= V2_CHI2NDF and r_["max_abs_pull_used"] <= V2_PULL)
            v3[key] = r_
        v3["pass"] = all(v["pass"] for v in v3.values() if isinstance(v, dict))
        res["replicas"][str(k)] = {"c": c, "V2": v2, "V3": v3, "V4": v4}
        print("REPLICA", k, json.dumps({"c": c, "V2": v2["pass"], "V2_fine_chi2ndf": fine["chi2_ndf"],
                                        "V2_J_max_pull": v2["J"]["max_abs_pull"], "V3": {k_: (v["chi2_ndf"], v["pass"]) for k_, v in v3.items() if isinstance(v, dict)},
                                        "V4": v4}), flush=True)
    # V1 on replica 0 (R4)
    r = np.random.default_rng(V1_SPLIT_SEED)
    nt = min(TUNE_MAX, T["i"].size)
    ti = np.sort(r.choice(T["i"].size, size=nt, replace=False))
    XA, wA = T["X"][ti], (T["w"] * W[0])[ti]
    XB, wB = Gd["X"], Gd["w"]
    ta, tb = r.random(nt) < 0.5, r.random(wB.size) < 0.5
    m1, i1 = fit_one(XA[ta], wA[ta], XB[tb], wB[tb], V1_SPLIT_SEED, a.threads, val_seed=[V1_SPLIT_SEED, 1])
    from sklearn.metrics import roc_auc_score
    ea, eb = balanced(wA[~ta], wB[~tb])
    pA = m1.predict_proba(XA[~ta], num_iteration=m1.best_iteration_)[:, 1]
    pB = m1.predict_proba(XB[~tb], num_iteration=m1.best_iteration_)[:, 1]
    auc = float(roc_auc_score(np.r_[np.zeros(pA.size), np.ones(pB.size)], np.r_[pA, pB], sample_weight=np.r_[ea, eb]))
    # control: G vs G, the same protocol on G halves (R7), capacity matched
    rg = np.random.default_rng(GVG_SPLIT_SEED)
    half = rg.random(wB.size) < 0.5
    XA2, wA2, XB2, wB2 = XB[~half], wB[~half], XB[half], wB[half]
    ta2, tb2 = rg.random(wA2.size) < 0.5, rg.random(wB2.size) < 0.5
    m2, i2 = fit_one(XA2[ta2], wA2[ta2], XB2[tb2], wB2[tb2], GVG_SPLIT_SEED, a.threads, val_seed=[GVG_SPLIT_SEED, 1],
                     n_estimators=i1["best_iteration"])
    ea2, eb2 = balanced(wA2[~ta2], wB2[~tb2])
    qA, qB = m2.predict_proba(XA2[~ta2])[:, 1], m2.predict_proba(XB2[~tb2])[:, 1]
    auc_c = float(roc_auc_score(np.r_[np.zeros(qA.size), np.ones(qB.size)], np.r_[qA, qB], sample_weight=np.r_[ea2, eb2]))
    res["V1"] = {"replica": 0, "auc": auc, "auc_control_GvsG": auc_c, "margin": V1_MARGIN,
                 "fit": i1, "control_fit": i2, "pass": bool(auc <= auc_c + V1_MARGIN)}
    print("V1", json.dumps({k_: v_ for k_, v_ in res["V1"].items() if k_ not in ("fit", "control_fit")}), flush=True)
    allrep = [res["replicas"][str(k)] for k in range(K)]
    res["verdict"] = {"V1": res["V1"]["pass"], "V2_all_replicas": all(x["V2"]["pass"] for x in allrep),
                      "V3_all_replicas": all(x["V3"]["pass"] for x in allrep), "V4_all_replicas": all(x["V4"]["pass"] for x in allrep)}
    res["verdict"]["S2_pass"] = all(res["verdict"].values())
    ru = resource.getrusage(resource.RUSAGE_SELF)
    res.update(maxrss_kb=ru.ru_maxrss)
    (a.out / f"gates_{a.gen}_{a.fset}.json").write_text(json.dumps(res, indent=1, default=float) + "\n")
    np.savez(a.out / f"weights_{a.gen}_{a.fset}.npz", i=T["i"], **{f"wG_k{k}": W[k] for k in range(K)})
    print("VERDICT", a.gen, a.fset, json.dumps(res["verdict"]), flush=True)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("models", "gates"))
    ap.add_argument("--gen", required=True, choices=sorted(SUPPORT))
    ap.add_argument("--fset", required=True, choices=sorted(FSETS))
    ap.add_argument("--tasks", default="")
    ap.add_argument("--harm", nargs="+", required=True)
    ap.add_argument("--contract", default=None, help="the s5c contract (J partition), for gates")
    ap.add_argument("--fcontract", required=True, help="the frozen feature contract (sha256 asserted)")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--threads", type=int, default=64)
    a = ap.parse_args(argv)
    if sha256(a.fcontract) != CONTRACT_SHA:
        print("STOP: the feature contract's sha256 is not the frozen one", flush=True)
        return 4
    return cmd_models(a) if a.cmd == "models" else cmd_gates(a)


if __name__ == "__main__":
    raise SystemExit(main())
