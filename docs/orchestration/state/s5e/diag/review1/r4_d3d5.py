"""D3 (traced pseudo), D4 (noise-free B0), D5 (capacity, missed-unity) recomputed independently."""
import numpy as np
from scipy import stats
from common import *
T = {"nominal": 300000, "eavail": 301000, "q3": 302000}
print("===== D3 traced pseudo (4 seeds), seed-mean residual; chi2 with measured-side variance")
for t, b in ([] if __import__("os").environ.get("SKIPD3") else T.items()):
    for bk in ("bkg", "sig"):
        P = [L(f"{RUNS}/trace/trace_{t}_{bk}_s{b + i}.npz") for i in range(4)]
        K = P[0]["fn_push"].shape[0]
        for k in (1, 5, 10, 20):
            i = k - 1
            mp = np.mean([R(p["fn_push"][i], p["fn_true"]) for p in P], 0)
            mA = np.mean([R(p["fn_push"][i], p["fn_true_A"]) for p in P], 0)
            ml = np.mean([R(p["fn_pull"][i], p["fn_true"]) for p in P], 0)
            v = [ewproj(p["reco5d_Dvar"]) for p in P]
            cD_push = np.mean([chi2(p["reco_ew_D"], p["reco_ew_push"][i], vv)[0] for p, vv in zip(P, v)])
            cD_pull = np.mean([chi2(p["reco_ew_D"], p["reco_ew_pull"][i], vv)[0] for p, vv in zip(P, v)])
            cD_true = np.mean([chi2(p["reco_ew_D"], p["reco_ew_true"], vv)[0] for p, vv in zip(P, v)])
            cpush_true = np.mean([chi2(p["reco_ew_push"][i], p["reco_ew_true"], vv)[0] for p, vv in zip(P, v)])
            s2 = np.mean([(p["truth_ew_pass_wpush"][i] + p["truth_ew_fail_wpush"][i]) / (p["truth_ew_pass_wpull"][i] + p["truth_ew_fail_wpull"][i]) - 1 for p in P], 0)
            print(f"{t}_{bk} k={k}: push {ew(mp)} vsA {ew(mA)} pull {ew(ml)} | chi2EW D-push {cD_push:.0f} D-pull {cD_pull:.0f} D-true {cD_true:.0f} push-true {cpush_true:.0f} | step2 med {100*np.median(np.abs(s2)):.3f}% max {100*np.abs(s2).max():.3f}%")
            if bk == "bkg" and t != "nominal" and k in (1, 5):
                # missed-event: fill vs reco-passing new_w per truth EW cell; r identical?
                g = []; rr = []; s1 = []
                for p in P:
                    nf = p["truth_ew_fail_wnew"][i] / p["truth_ew_fail_w"][i]; npass = p["truth_ew_pass_wnew"][i] / p["truth_ew_pass_w"][i]
                    rf = p["truth_ew_fail_wr"][i] / p["truth_ew_fail_w"][i]; rp = p["truth_ew_pass_wr"][i] / p["truth_ew_pass_w"][i]
                    g.append(nf - npass); rr.append(rf - rp); s1.append(npass - rp)
                g, rr, s1 = (np.mean(x, 0) for x in (g, rr, s1))
                print(f"     missed k={k}: |fill - pass new_w| med {100*np.median(np.abs(g)):.2f}% max {100*np.abs(g).max():.2f}%; |r_fail - r_pass| max {np.abs(rr).max():.2e}; |pass new_w - r| med {100*np.median(np.abs(s1)):.1f}% max {100*np.abs(s1).max():.1f}%")
        # 5D chi2 at k=5 (snapshot)
        c5 = np.mean([chi2(p["reco5d_D"], p["reco5d_push_it5"], p["reco5d_Dvar"])[0] for p in P]); t5 = np.mean([chi2(p["reco5d_D"], p["reco5d_true"], p["reco5d_Dvar"])[0] for p in P]); n5 = chi2(P[0]["reco5d_D"], P[0]["reco5d_true"], P[0]["reco5d_Dvar"])[1]
        print(f"   {t}_{bk} 5D chi2 (k=5): D-push {c5:.0f} D-true {t5:.0f} over {n5} cells")
print("===== D4/D5 noise-free, Poisson variance = F_true (analysis exposure)")
def series(p, label, ks):
    vt5 = p["reco5d_true"]; vtew = ewproj(vt5)
    Sew = chi2(p["reco_ew_prior"], p["reco_ew_true"], vtew)[0]; S5 = chi2(p["reco5d_prior"], p["reco5d_true"], vt5)
    print(f"-- {label}: S_dep EW {Sew:.0f}, 5D {S5[0]:.0f} over {S5[1]} cells;  reco_ew_D==reco_ew_true? {np.allclose(p['reco_ew_D'], p['reco_ew_true'], rtol=1e-10)}")
    rows = {}
    for k in ks:
        if k > p["fn_push"].shape[0]: continue
        i = k - 1; r = R(p["fn_push"][i], p["fn_true"])
        c = chi2(p["reco_ew_push"][i], p["reco_ew_true"], vtew)[0]
        s5 = ""
        if f"reco5d_push_it{k}" in p:
            c5 = chi2(p[f"reco5d_push_it{k}"], p["reco5d_true"], vt5)[0]; s5 = f" 5D chi2 {c5:.0f} EF5D {(1 - c5 / S5[0]) if S5[0] > 0 else float('nan'):.4f} p5D={stats.chi2.sf(c5, S5[1]):.1e}"
        rows[k] = (np.median(np.abs(r[:42])), c)
        print(f"   k={k:2d}: {ew(r)}  EW chi2 {c:.0f} EF_EW {(1 - c / Sew) if Sew > 0 else float('nan'):.4f} p(EW,42)={stats.chi2.sf(c, 42):.1e}{s5}")
    return rows
res = {}
for t in ("nominal", "eavail", "q3"):
    res[("b0", t)] = series(L(f"{RUNS}/asimov/asimov_b0_{t}.npz"), f"B0 {t}", list(range(1, 31)))
for t in ("eavail", "q3"):
    res[("cap", t)] = series(L(f"{RUNS}/asimov/asimov_cap_{t}.npz"), f"capacity {t}", list(range(1, 16)))
    res[("uni", t)] = series(L(f"{RUNS}/asimov/asimov_unity_{t}.npz"), f"missed-unity {t}", [1, 5, 10, 15, 20, 30])
print("===== rule-relevant relative changes of the median |EW residual|")
for t in ("eavail", "q3"):
    b = res[("b0", t)]
    med = {k: v[0] for k, v in b.items()}; kb = min(med, key=med.get)
    print(f"{t}: B0 k5 {100*med[5]:.2f}% best k {kb} {100*med[kb]:.2f}% drop {1 - med[kb]/med[5]:.3f}; k30 {100*med[30]:.2f}% drop k5->30 {1 - med[30]/med[5]:.3f}; chi2 k5 {b[5][1]:.0f} k30 {b[30][1]:.0f}")
    print("    B0 median by k:", " ".join(f"{k}:{100*med[k]:.2f}" for k in range(1, 31)))
    c = res[("cap", t)]
    for k in (1, 5, 10, 15):
        print(f"    capacity k={k}: {100*c[k][0]:.2f}% vs B0 {100*med[k]:.2f}% rel {1 - c[k][0]/med[k]:+.3f}; chi2 {c[k][1]:.0f} vs {b[k][1]:.0f}")
    u = res[("uni", t)]
    for k in (5, 15, 30):
        print(f"    unity k={k}: {100*u[k][0]:.2f}% vs B0 {100*med[k]:.2f}% rel {1 - u[k][0]/med[k]:+.3f}; chi2 {u[k][1]:.0f} vs {b[k][1]:.0f}")
