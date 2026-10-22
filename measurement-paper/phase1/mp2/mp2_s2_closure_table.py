"""Per (G, fset): every gate's per-replica range, read from gates_*.json, verdict_v2v3_*.json and the model metas."""
import glob, hashlib, json, sys
import numpy as np
D = sys.argv[1]
out = {"schema": "mp2-s2-closure-table/1", "source_dir": D, "rows": {}}
def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()
def rng(x):
    return [float(min(x)), float(max(x))]
for gen in ("genie_cv", "genie_mec", "nuwro_ch", "gibuu_ch"):
    for fs in ("primary", "fallback"):
        gp, vp = f"{D}/gates_{gen}_{fs}.json", f"{D}/verdict_v2v3_{gen}_{fs}.json"
        g, v = json.load(open(gp)), json.load(open(vp))
        R = [str(k) for k in range(5)]
        v4 = [g["replicas"][k]["V4"] for k in R]
        vr = [v["replicas"][k] for k in R]
        ms = sorted(glob.glob(f"{D}/model_{gen}_{fs}_k*h*f*.npz"))
        b = [json.loads(np.load(m)["meta_json"].item())["best_iteration"] for m in ms]
        out["rows"][f"{gen}/{fs}"] = {
            "files": {gp: sha(gp), vp: sha(vp)},
            "V1": {"auc": g["V1"]["auc"], "auc_control": g["V1"]["auc_control_GvsG"], "bar": g["V1"]["auc_control_GvsG"] + g["V1"]["margin"], "pass": g["V1"]["pass"], "fit_best_iteration": g["V1"]["fit"]["best_iteration"]},
            "V4": {"ess_over_N": rng([x["ess_over_N"] for x in v4]), "max_w_over_mean": rng([x["max_wG_over_mean"] for x in v4]),
                   "pass_per_replica": [x["pass"] for x in v4]},
            "V2_fine": {"chi2_ndf": rng([x["V2_fine"]["chi2_ndf"] for x in vr]), "ndf": sorted({x["V2_fine"]["ndf"] for x in vr}),
                        "pass_per_replica": [x["V2_fine"]["pass"] for x in vr]},
            "V2_J": {"max_abs_pull": rng([x["V2_J"]["max_abs_pull"] for x in vr]), "pass_per_replica": [x["V2_J"]["pass"] for x in vr]},
            "V3": {"min_p_d": rng([x["V3"]["min_p_d"] for x in vr]), "fail_closed": sorted({d for x in vr for d in x["V3"]["fail_closed"]}),
                   "largest_p_d_any_distribution": float(max(d["p_d"] for x in vr for d in x["V3"]["distributions"].values())),
                   "n_distributions_failing_per_replica": [int(sum(d["p_d"] <= x["V3"]["bar_min_p_d_gt"] for d in x["V3"]["distributions"].values())) for x in vr],
                   "chi2_ndf_per_distribution": {d: rng([x["V3"]["distributions"][d]["chi2_ndf"] for x in vr]) for d in vr[0]["V3"]["distributions"]},
                   "pass_per_replica": [x["V3"]["pass"] for x in vr]},
            "V2_J_argmax_cells": sorted({x["V2_J"]["argmax_cell"] for x in vr}),
            "c": rng([g["replicas"][k]["c"] for k in R]),
            "verdict": v["verdict"],
            "best_iteration": {"n_models": len(b), "min_median_max": [int(min(b)), int(np.median(b)), int(max(b))], "n_ge_2800": int(sum(x >= 2800 for x in b))},
            "R9": g.get("R9") and {k: g["R9"][k] for k in ("n_rows_out_of_support", "w_truth_share_out_of_support")},
        }
print(json.dumps(out, indent=1))
