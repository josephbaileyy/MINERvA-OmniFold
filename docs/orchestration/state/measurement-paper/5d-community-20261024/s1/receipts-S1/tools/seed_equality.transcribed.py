import numpy as np, json, lightgbm
A="/pscratch/sd/j/josephrb/s5p-20260926/runs/s2/num/data"; S="/pscratch/sd/j/josephrb/s1-20261024/runs/seed"
def z(p): return np.load(p, allow_pickle=False)
n=eq=0; neq=[]
for b in range(1,21):
    ref=z(f"{A}/data_b{b}_j{100+b}.npz")["xsec_flat"]
    for s in (45,48,51,54):
        n+=1; e=bool(np.array_equal(ref, z(f"{S}/S1seed{s}_b{b}_j{100+b}.npz")["xsec_flat"])); eq+=e
        if not e: neq.append((b,s))
print("xsec_flat of S1seed<s>_b<b>_j<100+b> bitwise equal to set A data_b<b>_j<100+b> (seed 42):", eq, "of", n, "unequal:", neq)
keys=("random_state","subsample","subsample_freq","colsample_bytree","deterministic","bin_construct_sample_cnt","n_estimators","num_leaves")
for s in (45,48,51,54):
    m=json.loads(str(z(f"{S}/S1seed{s}_b1_j101.npz")["meta"]))
    print("seed", s, "estimator_seed", m["estimator_seed"], "B0", [{k:p.get(k) for k in keys if k in p} for p in m["estimator_params"]])
    print("seed", s, "refinement", {k:m["refinement"]["classifier_params"].get(k) for k in keys})
m42=json.loads(str(z(f"{A}/data_b1_j101.npz")["meta"])); m45=json.loads(str(z(f"{S}/S1seed45_b1_j101.npz")["meta"]))
print("code_sha256 differing between set A b1 and S1seed45 b1:", {k:(m42["code_sha256"].get(k), m45["code_sha256"].get(k)) for k in set(m42["code_sha256"])|set(m45["code_sha256"]) if m42["code_sha256"].get(k)!=m45["code_sha256"].get(k)})
print("lightgbm", lightgbm.__version__)
