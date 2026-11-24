#!/bin/bash
# ibuchi login-node smoke: the new binary on 1A, first 2 MC + first 8 data files, MNV101_DUMP_MUONQ=1. Writes ROOT/work/smoke.
set -eo pipefail
ROOT=/pscratch/sd/j/josephrb/ibuchi-evloop-20261123; REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
[ ! -e $ROOT/work/smoke ] || { echo "REFUSED: smoke dir exists"; exit 2; }
mkdir -p $ROOT/work/smoke && cd $ROOT/work/smoke
head -n 2 $ROOT/manifests/1A_MC.txt > smoke_MC.txt; head -n 8 $ROOT/manifests/1A_Data.txt > smoke_Data.txt
set +u; source $REPO/setup_salloc_env.sh
export MNV101_DUMP_MUONQ=1
/usr/bin/time -v $ROOT/opt/bin/runEventLoopOmniFold smoke_Data.txt smoke_MC.txt > evl.log 2> evl.err
python3 - <<'PY'
import json, numpy as np, ROOT
F = "runEventLoopOmniFold.root"; f = ROOT.TFile.Open(F)
out = {t: int(f.Get(t).GetEntries()) for t in ("mc_truth_denom", "mc_signal_reco", "mc_background", "data")}
MU = ["mu_p_total","mu_p_minos","mu_trk_p","mu_trk_p_range","mu_trk_p_curv","mu_used_range","mu_used_curv","mu_trk_quality","mu_trk_qp","mu_trk_eqp_qp","mu_mad_p","mu_thetaX","mu_thetaY","mu_theta"]
for t, x, z, p in (("mc_signal_reco","sim","sim_pz","sim_pass"), ("mc_background","sim_background","sim_background_pz","sim_background_pass"), ("data","measured","measured_pz","measured_pass")):
    names = [b.GetName() for b in f.Get(t).GetListOfBranches()]
    out[t + "_missing_mu"] = [m for m in MU if m not in names]
    a = ROOT.RDataFrame(t, F).AsNumpy([x, z, p] + MU)
    sel = (a[p] != 0) & (a["mu_p_total"] > 0)
    out[t + "_reco_rows"] = int(sel.sum())
    out[t + "_nonsentinel_frac"] = {m: float(np.mean(a[m][sel] != -9999)) for m in MU}
    pt = a["mu_p_total"][sel] / 1000 * np.sin(a["mu_theta"][sel]); pz = a["mu_p_total"][sel] / 1000 * np.cos(a["mu_theta"][sel])
    out[t + "_C_KIN"] = float(max(np.max(np.abs(pt - a[x][sel])), np.max(np.abs(pz - a[z][sel]))))
    th = np.arctan(np.sqrt(np.tan(a["mu_thetaX"][sel])**2 + np.tan(a["mu_thetaY"][sel])**2))
    out[t + "_C_ANG"] = float(np.max(np.abs(th - a["mu_theta"][sel])))
    if t == "mc_signal_reco":
        miss = a[p] == 0; out["sig_miss_rows"] = int(miss.sum()); out["sig_miss_all_sentinel"] = bool(all(np.all(a[m][miss] == -9999) for m in MU))
    out[t + "_used_curv_frac"] = float(np.mean(a["mu_used_curv"][sel] == 1)); out[t + "_quality1_frac"] = float(np.mean(a["mu_trk_quality"][sel] == 1))
print(json.dumps(out, indent=1))
PY
grep -E 'Elapsed|Maximum resident' evl.err; sha256sum runEventLoopOmniFold.root
