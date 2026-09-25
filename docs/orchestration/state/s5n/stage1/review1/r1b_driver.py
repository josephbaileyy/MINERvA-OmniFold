import json, sys, os, numpy as np
DEP = "/pscratch/sd/j/josephrb/s5n-20260925/deploy/82dc1517"
sys.path.insert(0, DEP + "/nd-unfolding")
import s5c_coverage as sc, s5c_assemble
R = "/pscratch/sd/j/josephrb/s5n-20260925/runs/"
U, names = sc.reported_functionals(json.load(open(DEP + "/docs/orchestration/state/s5c/contract.json")))
fp = U @ np.load(R + "c7/data_purity.npz")["xsec_flat"]; fn = U @ np.load(R + "c7/data_negweight.npz")["xsec_flat"]
drv = U @ s5c_assemble.read_flat(R + "c7/xsec_5d_driver_negweight_F2.root")
det = U @ s5c_assemble.read_flat("/pscratch/sd/j/josephrb/s5c-20260924/runs/construction/det/5d_det_cv.root")
o = {"driver_negw_vs_npz_negw_max_rel_pct": 100*float(np.max(np.abs(drv/fn-1))), "argmax": names[int(np.argmax(np.abs(drv/fn-1)))],
     "driver_negw_vs_npz_negw_median_rel_pct": 100*float(np.median(np.abs(drv/fn-1))),
     "s5c_det_cv(purity,driver,bkgaware omnifile)_vs_npz_purity_max_rel_pct": 100*float(np.max(np.abs(det/fp-1))),
     "driver_negw_minus_det_cv_rel: max|.-npz diff| pp": 100*float(np.max(np.abs((drv-det)/det-(fn-fp)/fp))),
     "driver_path_method_sensitivity_highW_pct": {n: round(100*float((drv[i]-det[i])/det[i]),3) for i,n in enumerate(names) if n in ("EW5","EW11","EW17","EW23","EW29","EW35","EW41","total_integrated")}}
print(json.dumps(o, indent=1)); json.dump(o, open(os.path.dirname(os.path.abspath(__file__))+"/r1b_driver.json","w"), indent=1)
