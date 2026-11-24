import numpy as np
SC = "/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/8f21a498-e586-4293-aaeb-c5560401abaa/scratchpad"
z = np.load(SC + "/priortest/in/signed_data.npz"); M, T, yr = z["response"], z["prior"], z["refined_y"]
v = np.load(SC + "/priortest/vectors.npz"); F, ur10, pub, mask = v["F"], v["ur10"], v["pub"], v["mask"]
R = np.divide(M, T[None, :], out=np.zeros_like(M), where=T[None, :] > 0)
fo = R @ np.where(mask, pub / np.where(F > 0, F, 1), ur10)
r = np.where(fo > 0, 100 * (yr / np.where(fo > 0, fo, 1) - 1), np.nan).reshape(14, 16)
e = np.where(yr > 0, 100 / np.sqrt(np.abs(yr)), np.nan).reshape(14, 16)
PZ = [1.5,2,2.5,3,3.5,4,4.5,5,6,7,8,9,10,15,20,40,60]; PT=[0,0.07,0.15,0.25,0.33,0.40,0.47,0.55,0.70,0.85,1.00,1.25,1.50,2.50,4.50]
for i in (0, 1):
    print(f"reco pT {PT[i]}-{PT[i+1]}: " + " ".join(f"{PZ[j]}:{r[i,j]:+.1f}" for j in range(16) if not np.isnan(r[i,j])))
    print(f"   data-stat %:        " + " ".join(f"{e[i,j]:.1f}" for j in range(16) if not np.isnan(r[i,j])))
for j in (13, 14, 15):
    print(f"reco p|| {PZ[j]}-{PZ[j+1]}: " + " ".join(f"{PT[i]}:{r[i,j]:+.1f}" for i in range(14) if not np.isnan(r[i,j])))
