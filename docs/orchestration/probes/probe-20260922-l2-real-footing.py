"""Call the REAL Member.footing() on all three products. My earlier check reimplemented it
and got equality; cross_member_validity disagrees, so the reimplementation is the suspect."""
import json
import z_grade as G
P = {"m0":    "/pscratch/sd/j/josephrb/z2m-products/member_k000000",
     "m1200": "/pscratch/sd/j/josephrb/z2m-products/member_k001200",
     "L2":    "/pscratch/sd/j/josephrb/z2m-products/member_k001200_L2laterals"}
F = {}
for k, d in P.items():
    m = G.Member(f"{d}/z-cv.npz", f"{d}/z-receipt-cv.json", "cv")
    F[k] = m.footing()
    print(k, json.dumps(F[k], sort_keys=True))
print()
print("m0 == m1200 :", F["m0"] == F["m1200"])
print("m0 == L2    :", F["m0"] == F["L2"])
for key in sorted(F["m0"]):
    same = F["m0"][key] == F["L2"][key]
    print(f"  {key:18s} equal={same}")
    if not same:
        print(f"      m0 = {F['m0'][key]}")
        print(f"      L2 = {F['L2'][key]}")
