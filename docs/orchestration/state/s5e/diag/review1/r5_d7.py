"""D7 paired background-inclusive minus signal-only over 12 seeds; closure vs truth; mechanism checks."""
import numpy as np
from scipy import stats
from common import *
S = list(range(300000, 300012))
def get(kind, s):
    if kind in ("b0", "sig") and s < 300004:
        p = L(f"{RUNS}/trace/trace_nominal_{'bkg' if kind == 'b0' else 'sig'}_s{s}.npz"); x = p["xsec_it5_flat"]
    else:
        p = L(f"{RUNS}/bkg/bkg_{kind}_s{s}.npz"); x = p["xsec_flat"]
    return U @ x, U @ p["xtrue_flat"], p["reco5d_D"], p["meta"], p["xtrue_flat"]
D = {k: [get(k, s) for s in S] for k in ("b0", "sig", "refcap", "exptmpl")}
# consistency: same truth and same pseudo seed/split for all variants of a seed
for i, s in enumerate(S):
    xt = [D[k][i][4] for k in D]
    same = all(np.array_equal(xt[0], x) for x in xt[1:])
    ms = [(D[k][i][3]["pseudo_seed"], D[k][i][3]["split_key"], D[k][i][3]["no_background"], D[k][i][3]["refine_override"], D[k][i][3]["expectation_template"], D[k][i][3]["estimator_seed"]) for k in D]
    if not same or len({m[0] for m in ms}) != 1 or len({m[1] for m in ms}) != 1:
        print("MISMATCH", s, same, ms)
print("variant metas seed 300005:", [(k, D[k][5][3]["no_background"], D[k][5][3]["refine_override"], D[k][5][3]["expectation_template"]) for k in D])
ti = NAMES.index("total_integrated")
def tstat(d):
    d = np.asarray(d); m = d.mean(0); se = d.std(0, ddof=1) / np.sqrt(d.shape[0]); return m, se, m / se
for k in ("b0", "refcap", "exptmpl"):
    d = [(f - fs) / t for (f, t, *_), (fs, *_r) in zip(D[k], D["sig"])]
    m, se, t = tstat(d)
    w = np.argsort(-np.abs(t))[:5]
    print(f"paired {k}-sig: max|t| {np.abs(t).max():.2f} n|t|>3.6 {(np.abs(t) > 3.6).sum()} n|t|>3 {(np.abs(t) > 3).sum()} max|mean| {100*np.abs(m).max():.3f}% total {100*m[ti]:+.3f}% | "
          + " ".join(f"{NAMES[i]}:{100*m[i]:+.3f}±{100*se[i]:.3f}(t={t[i]:.1f})" for i in w))
    for nm in ("J80", "J161", "EW40", "J58"):
        if nm in NAMES:
            j = NAMES.index(nm); print(f"    {nm}: mean {100*m[j]:+.3f}% se {100*se[j]:.3f}% t {t[j]:.2f}")
    print(f"    median SE {100*np.median(se):.4f}%  median |mean| {100*np.median(np.abs(m)):.4f}%")
    if k == "b0": mb, seb, tb = m, se, t
    else:
        idx = np.argsort(-np.abs(tb))[:12]
        red = 1 - np.abs(m[idx]) / np.abs(mb[idx])
        print(f"    on B0's 12 worst cells: |mean| reduction min {red.min():.3f} median {np.median(red):.3f}; SE ratio variant/B0 median {np.median(se[idx]/seb[idx]):.2f}")
        print(f"    SE ratio variant/B0 over all 153: median {np.median(se/seb):.3f}")
# variant minus B0 directly (paired on everything)
for k in ("refcap", "exptmpl"):
    d = [(f - fb) / t for (f, t, *_), (fb, *_r) in zip(D[k], D["b0"])]
    m, se, t = tstat(d); print(f"{k} - b0 direct: max|t| {np.abs(t).max():.2f} n|t|>3.6 {(np.abs(t)>3.6).sum()} max|mean| {100*np.abs(m).max():.3f}% total {100*m[ti]:+.3f}%")
print("closure vs truth:")
for k in ("b0", "refcap", "exptmpl", "sig"):
    r = [R(f, t) for f, t, *_ in D[k]]; m, se, t = tstat(r)
    sd = np.asarray(r).std(0, ddof=1)
    print(f"  {k}: max|t| {np.abs(t).max():.2f} n|t|>3.6 {(np.abs(t)>3.6).sum()} max|mean| {100*np.abs(m).max():.3f}% total {100*m[ti]:+.3f}% median per-seed SD {100*np.median(sd):.3f}% (EW median SD {100*np.median(sd[:42]):.3f}%)")
    if k == "b0": sdb = sd
    else: print(f"     per-seed SD ratio to B0: median {np.median(sd/sdb):.3f}, EW median {np.median(sd[:42]/sdb[:42]):.3f}")
# reco-level subtraction residual map (EW), B0 and refcap, vs truth-level paired difference
for k in ("b0", "refcap", "exptmpl"):
    dr = np.mean([ewproj(Dk) / ewproj(Ds) - 1 for (_, _, Dk, *_a), (_, _, Ds, *_b) in zip(D[k], D["sig"])], 0)
    dt = np.mean([((f - fs) / t)[:42] for (f, t, *_), (fs, *_r) in zip(D[k], D["sig"])], 0)
    sp = stats.spearmanr(dr, dt)
    print(f"reco EW subtraction residual {k}: max|.| {100*np.abs(dr).max():.2f}% median|.| {100*np.median(np.abs(dr)):.2f}%  spearman vs truth paired {sp.correlation:+.3f} (p={sp.pvalue:.3f})")
    # per-seed scatter of the reco residual
    per = np.array([ewproj(Dk) / ewproj(Ds) - 1 for (_, _, Dk, *_a), (_, _, Ds, *_b) in zip(D[k], D["sig"])])
    print(f"    reco residual SE median {100*np.median(per.std(0, ddof=1)/np.sqrt(12)):.2f}%  n cells |mean/SE|>3: {(np.abs(per.mean(0)/(per.std(0,ddof=1)/np.sqrt(12)))>3).sum()}")
# refinement evidence comparisons
for k in ("b0", "refcap", "exptmpl"):
    ev = [D[k][i][3]["refinement"] for i in range(12)]
    print(k, "refined/signed mean %.6f  clipped frac mean %.5f g_min median %.4f n_eff_refined/n_eff_signed median %.4f" % (
        np.mean([e["refined_over_signed"] for e in ev]), np.mean([e["clipped_fraction"] for e in ev]), np.median([e["g_min"] for e in ev]),
        np.median([e["n_eff_refined"] / e["n_eff_signed_abs"] for e in ev])))
