#!/usr/bin/env python3
"""MP-2 S2 step 3 (root_6_28, LightGBM 4.6): the event-level reweighting models and the gate computations, under the
frozen feature contract (feature_contract_draft.json 98141c2f..., addenda 8 and 9), the readings recorded in
docs/orchestration/state/measurement-paper/phase1/mp2/S2-IMPLEMENTATION.md and their rulings in binding addendum 13.

  models  trains model (k, h, f) for one generator and feature set: Tune v1 C+H rows inside the fine grid and the
          generator's E_nu support, of half h outside fold f (at most 4,000,000, drawn uniformly), against the
          generator's harmonized events outside G-fold f, atomic-electron targets excluded (R13); 10% of each
          class's training rows validate (R1); class weights sum to half the split's rows per class; early stopping
          after 200 rounds on the weighted binary logloss, the logloss recorded at 500..3000 trees. It predicts every
          Tune row of half h, fold f and writes the odds p/(1-p), p clipped to [1e-9, 1 - 1e-9]. Never overwrites.
  gates   assembles the K = 5 replicas (each Tune row is predicted by exactly one model per replica), fixes c_k (R2),
          and computes V4 for every replica (R3) and V1 on replica 0 (R4): the gate on fold 0, held out on both sides
          (R10), with the R7 control; the pooled V1 and, when V1 reaches 2800 trees, a 10000-tree V1, both
          descriptive. V2 and V3 statistics (R5, R5b, R6) are computed for every replica and SEALED: no V2/V3
          pass/fail is computed or printed (addendum 13: held for Joseph). R6's s is asserted equal across replicas,
          and its identity s k_T f_CH,an is reported, with g0 and R9's out-of-support shares.

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
OFIN = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz"
OFIN_SHA = "07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f"
MNVTUNE = "/pscratch/sd/j/josephrb/s5p-20260926/gen5d/mnvtune_v1_xsec5d.npz"
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
LOGLOSS_CHECKPOINTS = (500, 1000, 2000, 2500, 2800, 3000)   # addendum 13, the iteration cap
V1_CAP_REPORT, V1_DESCRIPTIVE_MAX = 2800, 10000
S_REL_TOL = 1e-12
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
    gm = ev["tgt"] != 0                     # R13 (addendum 13): GENIE atomic-electron targets never train, nor enter V1, V3
    Gd = {"X": np.column_stack([ev[f][gm] for f in feats]).astype(np.float64), "w": ev["c"][gm],
          "j": ev["j"][gm].astype(np.int64), "fine": ev["fine"][gm], "n_excluded_tgt0": int((~gm).sum()), "mask": gm}
    if np.any(np.diff(T["i"]) <= 0):
        raise SystemExit("the Tune rows are not in ascending MCgen order")
    src = {"events": {"path": str(hd / f"events_{gen}.npz"), "sha256": sha256(hd / f"events_{gen}.npz")},
           "tune": {"path": str(td / "tune_CH.npz"), "sha256": sha256(td / "tune_CH.npz")}}
    return T, Gd, tz, ev, src, hd


def balanced(wa, wb):
    """Class weights: each class sums to half the split's row count (S0's rule)."""
    n = wa.size + wb.size
    return wa * (0.5 * n / wa.sum()), wb * (0.5 * n / wb.sum())


def fit_one(Xa, wa, Xb, wb, seed, threads, val_seed, n_estimators=None, n_estimators_max=None):
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
    if n_estimators_max is not None:
        p["n_estimators"] = int(n_estimators_max)
    m = lgb.LGBMClassifier(**p)
    t0 = time.time()
    curve = {}
    if n_estimators is None:
        m.fit(X, y, sample_weight=np.r_[twa, twb], eval_set=[(Xv, yv)], eval_sample_weight=[np.r_[vwa, vwb]],
              eval_metric="binary_logloss", callbacks=[lgb.early_stopping(EARLY_STOP, verbose=False),
                                                       lgb.record_evaluation(curve)])
        best = int(m.best_iteration_)
        vl = float(m.best_score_["valid_0"]["binary_logloss"])
        ll = curve["valid_0"]["binary_logloss"]
        checkpoints = {str(t): (float(ll[t - 1]) if len(ll) >= t else None) for t in LOGLOSS_CHECKPOINTS}
        n_rec = len(ll)
    else:
        m.fit(X, y, sample_weight=np.r_[twa, twb])
        best, vl, checkpoints, n_rec = int(n_estimators), None, None, None
    return m, {"best_iteration": best, "valid_logloss": vl, "fit_s": round(time.time() - t0, 2),
               "valid_logloss_at": checkpoints, "n_iterations_recorded": n_rec, "n_estimators_max": int(p["n_estimators"]),
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
    """R6: shape closure at the hybrid's rate. Both sides scaled to G's total over all bins (s = sum G / sum T); chi2
    over the bins with >= nmin raw entries on both sides; ndf = bins used - 1. R5b: the pull population is the chi2
    bins; every excluded bin is listed with each side's share, and a bin with >= nmin on one side only is a support
    gap. Statistics only: NO pass/fail (addendum 13: the V2 and V3 verdicts are held for Joseph)."""
    from scipy.stats import chi2 as chi2d
    s = gc.sum() / tc.sum()
    use = (tn >= nmin) & (gn >= nmin)
    d = s * tc - gc
    var = s * s * tv + gv
    pull = np.where(var > 0, d / np.sqrt(np.where(var > 0, var, 1.0)), 0.0)
    chi2 = float(np.sum(pull[use] ** 2))
    ndf = int(use.sum()) - 1
    exc = np.nonzero(~use & ((tn > 0) | (gn > 0)))[0]
    gap = (tn >= nmin) ^ (gn >= nmin)
    return {"scale_s": float(s), "n_bins_used": int(use.sum()), "chi2": chi2, "ndf": ndf,
            "chi2_ndf": chi2 / ndf if ndf > 0 else None, "p_value": float(chi2d.sf(chi2, ndf)) if ndf > 0 else None,
            "max_abs_pull_used": float(np.max(np.abs(pull[use]))) if use.any() else None,
            "pulls_used": {str(int(b)): float(pull[b]) for b in np.nonzero(use)[0]} if use.sum() <= 200 else None,
            "n_excluded_bins": int(exc.size), "n_support_gap_bins": int(gap.sum()),
            "excluded_share_T": float(tc[~use].sum() / tc.sum()), "excluded_share_G": float(gc[~use].sum() / gc.sum()),
            "support_gap_share_T": float(tc[gap].sum() / tc.sum()), "support_gap_share_G": float(gc[gap].sum() / gc.sum()),
            "excluded_bins": ({str(int(b)): {"T_share": float(tc[b] / tc.sum()), "G_share": float(gc[b] / gc.sum()),
                                             "n_T": int(tn[b]), "n_G": int(gn[b]), "support_gap": bool(gap[b])} for b in exc}
                              if exc.size <= 200 else None)}


def auc_w(m, Xa, wa, Xb, wb, num_iteration):
    from sklearn.metrics import roc_auc_score
    ea, eb = balanced(wa, wb)
    pa = m.predict_proba(Xa, num_iteration=num_iteration)[:, 1]
    pb = m.predict_proba(Xb, num_iteration=num_iteration)[:, 1]
    return float(roc_auc_score(np.r_[np.zeros(pa.size), np.ones(pb.size)], np.r_[pa, pb], sample_weight=np.r_[ea, eb]))


def v1_test(XA, wA, XB, wB, seed, ctrl_seed, threads, GX, Gw, n_ctrl, n_estimators_max=None):
    """One V1: a fresh classifier (model.params) trained on 50% of the (Tune, G) sample, AUC on the other 50%; and the
    capacity-matched control on two disjoint random subsets of G's events of n_ctrl each (R7), V1's protocol, its
    n_estimators fixed to V1's best iteration."""
    r = np.random.default_rng(seed)
    ta, tb = r.random(wA.size) < 0.5, r.random(wB.size) < 0.5
    m1, i1 = fit_one(XA[ta], wA[ta], XB[tb], wB[tb], seed, threads, val_seed=[seed, 1], n_estimators_max=n_estimators_max)
    auc = auc_w(m1, XA[~ta], wA[~ta], XB[~tb], wB[~tb], m1.best_iteration_)
    rg = np.random.default_rng(ctrl_seed)
    perm = rg.permutation(Gw.size)
    if 2 * n_ctrl > Gw.size:
        raise SystemExit(f"control needs 2 x {n_ctrl} G events, G has {Gw.size}")
    ia, ib = perm[:n_ctrl], perm[n_ctrl:2 * n_ctrl]
    ta2, tb2 = rg.random(n_ctrl) < 0.5, rg.random(n_ctrl) < 0.5
    m2, i2 = fit_one(GX[ia][ta2], Gw[ia][ta2], GX[ib][tb2], Gw[ib][tb2], ctrl_seed, threads, val_seed=[ctrl_seed, 1],
                     n_estimators=i1["best_iteration"])
    auc_c = auc_w(m2, GX[ia][~ta2], Gw[ia][~ta2], GX[ib][~tb2], Gw[ib][~tb2], None)
    return {"auc": auc, "auc_control_GvsG": auc_c, "margin": V1_MARGIN, "n_tune": int(wA.size), "n_gen": int(wB.size),
            "n_control_each": int(n_ctrl), "fit": i1, "control_fit": i2, "pass": bool(auc <= auc_c + V1_MARGIN),
            "at_frozen_capacity": bool(i1["best_iteration"] >= V1_CAP_REPORT)}


def cmd_gates(a):
    T, Gd, tz, ev, src, hd = load(a.harm, a.gen, a.fset)
    hy = json.loads((hd / f"hybrid_an_{a.gen}.json").read_text())
    if sha256(hy["rho_npz"]["path"]) != hy["rho_npz"]["sha256"]:
        raise SystemExit("rho_an digest differs from its record")
    rho_an = np.load(hy["rho_npz"]["path"])["rho"]
    prod = np.load(hd / f"harmonized_{a.gen}.npz")
    import gen5d_flux_reweight as gfr
    g5 = gfr.load_g5(gfr.DEFAULTS["gen5d_tree"])
    dV = g5.widths(*g5.AXES).reshape(-1)
    nfine = dV.size
    contract = json.loads(Path(a.contract).read_text())
    supported = contract["measurement"]["partition_J"]["supported_cells"]
    cmap, ncell = s1.coarse_map(s1.J_EDGES, supported)
    rep = cmap >= 0
    res = {"schema": "mp2-s2-gates/2", "gen": a.gen, "fset": a.fset, "argv": sys.argv, "slurm_job": os.environ.get("SLURM_JOB_ID"),
           "code_sha256": sha256(Path(__file__).resolve()), "sources": src, "hybrid_an": str(hd / f"hybrid_an_{a.gen}.json"),
           "rulings": "binding addendum 13 (R0-R13; V2 and V3 verdicts held for Joseph)", "replicas": {},
           "n_gen_excluded_tgt0_R13": Gd["n_excluded_tgt0"]}
    r_an = rho_an[T["fine"]]
    Gc_fine, Gv_fine, Gn_fine = prod["xsec_flat"] * dV, prod["sumw2_flat"] * dV ** 2, prod["nevt_flat"]
    sealed = {"schema": "mp2-s2-gates-v2v3-sealed/1", "gen": a.gen, "fset": a.fset,
              "rule": "addendum 13: statistics only; no V2/V3 pass/fail is computed; not read by anyone until Joseph rules "
                      "on the thresholds or keeps the frozen ones", "replicas": {}}
    W, svals = {}, []
    tn_fine = np.bincount(T["fine"], None, nfine).astype(float)
    gmask = Gd["mask"]
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
        tc, tv = np.bincount(T["fine"], w, nfine), np.bincount(T["fine"], w * w, nfine)
        fine = chi2_shape(tc, tv, tn_fine, Gc_fine, Gv_fine, Gn_fine, V2_NMIN)
        svals.append(fine["scale_s"])
        jt, jtv = np.bincount(cmap[rep], tc[rep], ncell), np.bincount(cmap[rep], tv[rep], ncell)
        jg, jgv = np.bincount(cmap[rep], Gc_fine[rep], ncell), np.bincount(cmap[rep], Gv_fine[rep], ncell)
        sj_ = fine["scale_s"]
        jpull = (sj_ * jt - jg) / np.sqrt(sj_ * sj_ * jtv + jgv)
        v3 = {}
        for key, bins in V3_BINS.items():
            if key == "neutron_KE_MeV":
                sel_t = T["in_support"][tz["nKE_ev"]]
                pos_t = np.searchsorted(np.nonzero(T["in_support"])[0], tz["nKE_ev"][sel_t])
                tx, twt = tz["nKE_val"][sel_t], w[pos_t]
                gn_ok = gmask[ev["nKE_ev"]]
                gx, gwt = ev["nKE_val"][gn_ok], ev["c"][ev["nKE_ev"][gn_ok]]
            else:
                tx, twt = tz[key][T["in_support"]], w
                gx, gwt = ev[key][gmask], ev["c"][gmask]
            ib_t, ib_g = np.digitize(tx, bins) - 1, np.digitize(gx, bins) - 1
            nb = bins.size - 1
            v3[key] = chi2_shape(np.bincount(ib_t, twt, nb), np.bincount(ib_t, twt * twt, nb), np.bincount(ib_t, None, nb).astype(float),
                                 np.bincount(ib_g, gwt, nb), np.bincount(ib_g, gwt * gwt, nb), np.bincount(ib_g, None, nb).astype(float), V2_NMIN)
        sealed["replicas"][str(k)] = {"V2": {"fine": fine, "J": {"pulls": jpull.tolist(), "max_abs_pull": float(np.max(np.abs(jpull))),
                                                                 "n_beyond_3": int(np.sum(np.abs(jpull) > V2_PULL))}},
                                      "V3": v3}
        res["replicas"][str(k)] = {"c": c, "V4": v4}
        print("REPLICA", k, json.dumps({"c": c, "V4": v4}), flush=True)          # V2/V3 never printed (addendum 13)
    # R6: s is classifier-independent; asserted equal across replicas
    sv = np.asarray(svals)
    s_rel = float(np.max(np.abs(sv - sv[0])) / abs(sv[0]))
    if s_rel > S_REL_TOL:
        raise SystemExit(f"R6: s differs across replicas by {s_rel:.3e} relative")
    oz = np.load(OFIN, allow_pickle=True)
    if sha256(OFIN) != OFIN_SHA:
        raise SystemExit("of_inputs_5d digest differs")
    fi_all = s1.fine_index(np.asarray(oz["MCgen"], float))
    wt_all = np.asarray(oz["w_truth"], float)
    ing = (fi_all >= 0) & np.isfinite(wt_all)
    den = np.load(MNVTUNE, allow_pickle=True)
    Dd = np.asarray(den["xsec_flat"], float) * dV
    k_T = float(wt_all[ing].sum() / Dd.sum())
    A_all = float(np.sum(wt_all[ing] * rho_an[fi_all[ing]]))
    sigT = float(np.sum(T["w"] * r_an))
    f_ch = sigT / A_all
    lhs = float(sv[0] * k_T * f_ch)
    rhoD = float(np.sum(rho_an * Dd))
    g_only = (tn_fine < V2_NMIN) & (Gc_fine > 0)
    res["R6"] = {"s": float(sv[0]), "s_max_rel_spread_over_replicas": s_rel, "sum_G": float(Gc_fine.sum()), "sum_T": sigT,
                 "k_T": k_T, "f_CH_an": f_ch, "identity_s_kT_fCH": lhs,
                 "identity_predicted_sumG_over_sum_rhoD": float(Gc_fine.sum() / rhoD),
                 "identity_net_ratio": lhs / float(Gc_fine.sum() / rhoD),
                 "g0_G_only_fine_cell_share": float(Gc_fine[g_only].sum() / Gc_fine.sum()),
                 "g0_per_J_cell": np.bincount(cmap[rep & g_only], Gc_fine[rep & g_only], ncell).tolist()}
    # R9: out-of-support Tune C+H rows and their w_truth share per J cell
    tfine = tz["fine"]
    tj = np.where(cmap[tfine] >= 0, cmap[tfine], -1)
    oos = ~T["in_support"]
    okj = tj >= 0
    wall = np.bincount(tj[okj], tz["w_truth"][okj], ncell)
    woos = np.bincount(tj[okj & oos], tz["w_truth"][okj & oos], ncell)
    res["R9"] = {"n_rows_out_of_support": int(oos.sum()), "w_truth_share_out_of_support": float(tz["w_truth"][oos].sum() / tz["w_truth"].sum()),
                 "share_per_J_cell": (woos / np.where(wall > 0, wall, 1.0)).tolist()}
    # V1 gate (R10): replica 0's Tune rows of fold 0 (both halves, <= 4M) against G's events of G-fold 0; control (R7)
    f0 = tune_fold(T["i"], 0) == 0
    rows0 = np.nonzero(f0)[0]
    r = np.random.default_rng(V1_SPLIT_SEED)
    if rows0.size > TUNE_MAX:
        rows0 = np.sort(r.choice(rows0, size=TUNE_MAX, replace=False))
    g0 = gen_fold(Gd["j"], 0) == 0
    XA, wA = T["X"][rows0], (T["w"] * W[0])[rows0]
    v1 = v1_test(XA, wA, Gd["X"][g0], Gd["w"][g0], V1_SPLIT_SEED, GVG_SPLIT_SEED, a.threads, Gd["X"], Gd["w"], int(g0.sum()))
    v1["sample"] = "R10: replica 0, Tune fold 0 (both halves) vs G-fold 0; held out on both sides"
    res["V1"] = v1
    print("V1", json.dumps({k_: v_ for k_, v_ in v1.items() if k_ not in ("fit", "control_fit")}), flush=True)
    if v1["at_frozen_capacity"]:
        d10 = v1_test(XA, wA, Gd["X"][g0], Gd["w"][g0], V1_SPLIT_SEED, GVG_SPLIT_SEED, a.threads, Gd["X"], Gd["w"], int(g0.sum()),
                      n_estimators_max=V1_DESCRIPTIVE_MAX)
        d10["status"] = "DESCRIPTIVE (addendum 13): V1 at 10000 trees, the same early stopping, beside the frozen-capacity gate"
        res["V1_10000_descriptive"] = d10
        print("V1_10000_descriptive", json.dumps({k_: v_ for k_, v_ in d10.items() if k_ not in ("fit", "control_fit")}), flush=True)
    # the session's pooled V1, DESCRIPTIVE beside the gate (R10)
    rp = np.random.default_rng(V1_SPLIT_SEED + 1)
    ti = np.sort(rp.choice(T["i"].size, size=min(TUNE_MAX, T["i"].size), replace=False))
    dp = v1_test(T["X"][ti], (T["w"] * W[0])[ti], Gd["X"], Gd["w"], V1_SPLIT_SEED + 1, GVG_SPLIT_SEED + 1, a.threads,
                 Gd["X"], Gd["w"], Gd["w"].size // 2)
    dp["status"] = "DESCRIPTIVE (addendum 13 R10): pooled Tune rows vs all G events; G side not held out"
    res["V1_pooled_descriptive"] = dp
    print("V1_pooled_descriptive", json.dumps({k_: v_ for k_, v_ in dp.items() if k_ not in ("fit", "control_fit")}), flush=True)
    sp = a.out / f"sealed_v2v3_{a.gen}_{a.fset}.json"
    if sp.exists():
        raise SystemExit(f"refusing to overwrite {sp}")
    sp.write_text(json.dumps(sealed, indent=1, default=float) + "\n")
    os.chmod(sp, 0o400)
    res["V2_V3"] = {"status": "HELD for Joseph (addendum 13): statistics computed and sealed, no pass/fail computed",
                    "sealed_file": str(sp), "sealed_sha256": sha256(sp)}
    res["verdict"] = {"V1": v1["pass"], "V1_at_frozen_capacity": v1["at_frozen_capacity"],
                      "V4_all_replicas": all(res["replicas"][str(k)]["V4"]["pass"] for k in range(K)),
                      "V2_V3": "held for Joseph", "S2": "not determined until the V2/V3 verdicts are released"}
    ru = resource.getrusage(resource.RUSAGE_SELF)
    res.update(maxrss_kb=ru.ru_maxrss)
    gp = a.out / f"gates_{a.gen}_{a.fset}.json"
    if gp.exists():
        raise SystemExit(f"refusing to overwrite {gp}")
    gp.write_text(json.dumps(res, indent=1, default=float) + "\n")
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
