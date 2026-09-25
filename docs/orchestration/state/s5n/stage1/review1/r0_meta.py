import json, numpy as np, glob, sys
R="/pscratch/sd/j/josephrb/s5n-20260925/runs/"
for f in [R+"c2/c2_rep_a.npz", R+"dev/nominal_a0_s300000.npz", R+"sigma/boot_b1.npz", R+"diag/diag_prior_eavail_shape_a1_s301000.npz", R+"c7/data_negweight.npz"]:
    z=np.load(f,allow_pickle=False); m=json.loads(str(z["meta"]))
    print("==",f, z.files)
    m.pop("estimator_params",None)
    print(json.dumps(m,indent=0,default=str)[:3000])
sys.path.insert(0,"/pscratch/sd/j/josephrb/s5n-20260925/deploy/82dc1517/nd-unfolding")
import project_cov_nd as pc
for a in ["pt","pz","eavail","q3","W"]: print(a, list(pc.AXIS_EDGES[a]))
