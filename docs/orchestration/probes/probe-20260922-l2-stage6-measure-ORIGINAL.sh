#!/bin/bash
# L2 stage 6: MEASURE s_proj with the five lateral bands released. THIS DOES NOT GRADE.
#
# ⚠ THE DISTINCTION IS THE WHOLE POINT AND IT IS NOT PEDANTRY. The predeclaration's outcome map
# says this probe "does not regrade M(i), which is UNRESOLVED on 4c for a permanent
# predeclaration failure", does not regrade cause 3, and does not license a significance. So
# `z_grade.grade()` is NOT called: it returns a branch verdict, and minting one here would
# manufacture exactly the disposition the predeclaration forbids.
#
# What IS called is z_grade's OWN statistic path -- `m1_functionals` then `member_statistics`,
# the same functions the graded two-member campaign ran, so `s_proj` comes out of the same code
# and the same predeclared functional set rather than a re-implementation. `cross_member_validity`
# runs too, because a statistic over two members that are not comparable is not a measurement.
#
# ⚠ AND THE OUTCOME MAP IS FIXED: > 5% CONFIRMS L1's FAIL with the five varying; < 5% LICENSES
# NOTHING, because one seed pair cannot show that a MAXIMUM over the declared set is below a
# bound. This script prints the number and that reading; it does not choose a verdict.
set -o pipefail
export HOME=/global/homes/j/josephrb
WT=/pscratch/sd/j/josephrb/MINERvA-OmniFold-l2-20260921
M0=/pscratch/sd/j/josephrb/z2m-products/member_k000000
M1=/pscratch/sd/j/josephrb/z2m-products/member_k001200
L2=/pscratch/sd/j/josephrb/z2m-products/member_k001200_L2laterals
source "$WT/setup_salloc_env.sh" >/dev/null 2>&1
cd "$WT/nd-unfolding"

python3 - "$M0" "$M1" "$L2" <<'PYEOF'
import json, sys
import numpy as np
import z_grade as G

m0_dir, m1_dir, l2_dir = sys.argv[1], sys.argv[2], sys.argv[3]

def load(d):
    return G.MemberProduct(f"{d}/z-cv.npz", f"{d}/z-receipt-cv.json", "cv")

base = load(m0_dir)
print(f"[s] baseline member offset={base.offset} cov_digest={base.cov_digest()[:16]}")

def measure(label, other_dir):
    other = load(other_dir)
    members = [base, other]
    val, ev = G.cross_member_validity(members, [0, 1200])
    U, ufo = G.m1_functionals(base.mask)
    stats, detail = G.member_statistics(members, U)
    ok = all(bool(getattr(val, f)) for f in val.__dataclass_fields__) if hasattr(val, "__dataclass_fields__") else None
    print(f"\n=== {label} ===")
    print(f"  member offset      : {other.offset}")
    print(f"  cov_digest         : {other.cov_digest()[:16]}")
    print(f"  functionals        : {np.atleast_2d(U).shape[0]}")
    print(f"  validity all-true  : {ok}")
    print(f"  s_agg              : {stats['s_agg']:.6%}")
    print(f"  s_med              : {stats['s_med']:.6%}")
    print(f"  s_proj             : {stats['s_proj']:.6%}   <-- the statistic L1 turns on")
    return stats, val, ev

# CONTROL FIRST, AND IT IS NOT OPTIONAL. Re-measuring the ALREADY-GRADED pair reproduces the
# recorded s_proj = 6.145388143592225% if and only if this script is driving the same code over
# the same operands. A control that agrees makes the second number interpretable; without it a
# difference could be my harness rather than the laterals.
pinned, _, _ = measure("CONTROL: the graded pair, laterals PINNED at seed 42", m1_dir)
RECORDED = 0.06145388143592225
d = abs(pinned["s_proj"] - RECORDED)
print(f"\n  control vs GRADE-20260920 receipt: recorded {RECORDED:.15f}")
print(f"                                     measured {pinned['s_proj']:.15f}   |diff| {d:.3e}")
if d > 1e-12:
    print("  ⚠⚠ CONTROL FAILED: this harness does not reproduce the graded statistic.")
    print("     The released-lateral number below is NOT interpretable and must not be quoted.")
else:
    print("  ✅ control reproduces the graded s_proj -- the harness is the graded code path")

released, val2, ev2 = measure("PROBE: the same pair with the five laterals RELEASED at seed 1242", l2_dir)

print("\n================ L2 RESULT, against the FIXED outcome map ================")
sp = released["s_proj"]
print(f"  s_proj with the five released : {sp:.6%}")
print(f"  s_proj with them pinned       : {pinned['s_proj']:.6%}  (the graded value)")
print(f"  bound                         : 5%")
if sp > 0.05:
    print("  READING: > 5% -- L1's FAIL is CONFIRMED with the five varying. The direction of")
    print("           L2 becomes known. This is STRONG because s_proj is a MAXIMUM and more")
    print("           pairs can only raise it.")
    print("  DOES NOT: regrade M(i) (UNRESOLVED on 4c, permanent), regrade cause 3, license a")
    print("           significance, or move the adopted digest 3d7465f6.")
else:
    print("  READING: < 5% -- THIS LICENSES NOTHING. One seed pair cannot establish that the")
    print("           MAXIMUM over the declared functional set is below the bound. It is NOT a")
    print("           PASS, NOT a clearance, and NOT grounds to revisit the adoption.")
json.dump({"pinned": pinned, "released": released, "control_abs_diff": d},
          open(f"{l2_dir}/l2-statistics.json", "w"), indent=2, sort_keys=True)
print(f"\n  written: {l2_dir}/l2-statistics.json")
PYEOF
