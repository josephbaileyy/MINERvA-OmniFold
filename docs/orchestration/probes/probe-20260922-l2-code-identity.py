import json, numpy as np
P = {"m0":    "/pscratch/sd/j/josephrb/z2m-products/member_k000000",
     "m1200": "/pscratch/sd/j/josephrb/z2m-products/member_k001200",
     "L2":    "/pscratch/sd/j/josephrb/z2m-products/member_k001200_L2laterals"}
R = {}
for k, d in P.items():
    z = np.load(f"{d}/z-cv.npz", allow_pickle=False)
    m = json.loads(str(z["metadata_json"]))
    ci = m.get("code_identity") or {}
    cl = json.dumps(ci.get("import_closure_digests"), sort_keys=True)
    R[k] = (ci.get("revision"), cl)
    print(f"{k:6s} revision={ci.get('revision')}  closure_len={len(cl)}")
print()
print("revisions all equal (m0 vs m1200) :", R["m0"][0] == R["m1200"][0])
print("revisions all equal (m0 vs L2)    :", R["m0"][0] == R["L2"][0])
print("closures  equal (m0 vs m1200)     :", R["m0"][1] == R["m1200"][1])
print("closures  equal (m0 vs L2)        :", R["m0"][1] == R["L2"][1])
print()
print("=> code_agrees(m0,m1200) =", bool(R["m0"][0]) and R["m0"][0] == R["m1200"][0] and R["m0"][1] == R["m1200"][1])
print("=> code_agrees(m0,L2)    =", bool(R["m0"][0]) and R["m0"][0] == R["L2"][0] and R["m0"][1] == R["L2"][1])
