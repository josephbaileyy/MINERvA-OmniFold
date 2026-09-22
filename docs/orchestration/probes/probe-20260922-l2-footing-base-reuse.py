"""Is the PROBE's footing_ok=False a property of the L2 product, or an artifact of REUSING
the base Member object across two cross_member_validity calls?

l2_stage6_measure.sh loads `base` ONCE and calls measure() twice. If anything in
cross_member_validity mutates a member in place, the SECOND call sees a different base.
"""
import z_grade as G

M0 = "/pscratch/sd/j/josephrb/z2m-products/member_k000000"
M1 = "/pscratch/sd/j/josephrb/z2m-products/member_k001200"
L2 = "/pscratch/sd/j/josephrb/z2m-products/member_k001200_L2laterals"


def load(d):
    return G.Member(f"{d}/z-cv.npz", f"{d}/z-receipt-cv.json", "cv")


def foot(m):
    return m.footing()


print("=== A. REUSED base, control then probe (exactly what stage 6 does) ===")
base = load(M0)
f_before = foot(base)
v1, _ = G.cross_member_validity([base, load(M1)], [0, 1200])
f_mid = foot(base)
v2, _ = G.cross_member_validity([base, load(L2)], [0, 1200])
f_after = foot(base)
print("   control footing_ok:", bool(v1.footing_ok))
print("   probe   footing_ok:", bool(v2.footing_ok))
print("   base footing stable across calls? before==mid:", f_before == f_mid,
      " mid==after:", f_mid == f_after)
if f_before != f_mid:
    print("   BASE MUTATED between calls:", {k: (f_before[k], f_mid[k]) for k in f_before if f_before[k] != f_mid[k]})

print()
print("=== B. FRESH base for each call ===")
v1b, _ = G.cross_member_validity([load(M0), load(M1)], [0, 1200])
print("   control footing_ok:", bool(v1b.footing_ok))
v2b, _ = G.cross_member_validity([load(M0), load(L2)], [0, 1200])
print("   probe   footing_ok:", bool(v2b.footing_ok))
allb = {f: bool(getattr(v2b, f)) for f in v2b.__dataclass_fields__}
print("   probe all fields (fresh base):")
for k, val in allb.items():
    print("     ", "PASS" if val else "*** FAIL ***", k)
print("   probe all_true (fresh base):", all(allb.values()))

print()
print("=== C. probe ONLY, nothing run before it ===")
v3, _ = G.cross_member_validity([load(M0), load(L2)], [0, 1200])
print("   probe footing_ok:", bool(v3.footing_ok))
