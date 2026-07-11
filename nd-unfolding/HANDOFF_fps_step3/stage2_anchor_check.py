#!/usr/bin/env python3
"""Stage-2 anchor check: does xps2 (full phase space + extended grid), restricted to
the standard pt/pz sub-region AND to bins fully interior to theta_mu<20deg, reproduce
the standard-PS PET headline (Stage-1 benchmark: integral ratio 1.0047, median|r-1| 1.03%)?

xps2 grid (15,19,7,7,6): pt indices 0-13 == standard's 14 pt bins, pt index 14 is the
new [4.5,30] catch column. pz indices 2-17 == standard's 16 pz bins, pz indices 0-1 are
the new [0,0.75)/[0.75,1.5) catch rows, pz index 18 is the new [60,120] catch row.

A pt/pz bin is "interior" to theta<20deg if its max-theta corner (pt_hi, pz_lo) has
atan2(pt_hi,pz_lo) < theta_max -- i.e. the WHOLE bin lies below the cut, so lifting the
theta gate (xps2's --full-phase-space) cannot have added or removed any truth events
in that bin relative to the theta-gated standard-PS dump.
"""
import math

import numpy as np

PT_EDGES = [0, 0.07, 0.15, 0.25, 0.33, 0.4, 0.47, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5, 2.5, 4.5]
PZ_EDGES = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0]
THETA_MAX = math.radians(20.0)

std = np.load("products/pet/fps_envelope_5d/fps_gbdt_prior_xsec_5d.npz")
xps2 = np.load("products/pet/fps_envelope_5d_xps2/fps_gbdt_prior_xsec_5d.npz")

std_shape = (14, 16, 7, 7, 6)
xps2_shape = (15, 19, 7, 7, 6)

x_pet_std = std["x_pet"].reshape(std_shape, order="C")
rep_std = std["rep"].reshape(std_shape, order="C")
x_pet_xps2_full = xps2["x_pet"].reshape(xps2_shape, order="C")
rep_xps2_full = xps2["rep"].reshape(xps2_shape, order="C")

# restrict xps2 to the standard pt/pz sub-region (pt 0:14, pz 2:18)
x_pet_xps2 = x_pet_xps2_full[0:14, 2:18, :, :, :]
rep_xps2 = rep_xps2_full[0:14, 2:18, :, :, :]

# interior-to-theta<20deg mask on the 14x16 pt/pz grid
interior_pt_pz = np.zeros((14, 16), bool)
for i in range(14):
    pt_hi = PT_EDGES[i + 1]
    for j in range(16):
        pz_lo = PZ_EDGES[j]
        interior_pt_pz[i, j] = math.atan2(pt_hi, pz_lo) < THETA_MAX
n_interior_pt_pz = interior_pt_pz.sum()
interior_5d = np.broadcast_to(interior_pt_pz[:, :, None, None, None], std_shape)
print(f"[anchor] interior pt/pz positions: {n_interior_pt_pz}/{14*16} "
      f"-> interior 5D bins: {interior_5d.sum()}")

both_rep = rep_std & rep_xps2 & interior_5d
print(f"[anchor] bins with BOTH populated (rep_std & rep_xps2) & interior: {both_rep.sum()}")

a = x_pet_std[both_rep]
b = x_pet_xps2[both_rep]
ratio = b / a
integral_ratio = b.sum() / a.sum()
median_abs_dev = np.median(np.abs(ratio - 1.0))
p90_abs_dev = np.percentile(np.abs(ratio - 1.0), 90)

print(f"[anchor] n_bins_compared = {both_rep.sum()}")
print(f"[anchor] integral ratio (xps2/std) = {integral_ratio:.4f}")
print(f"[anchor] median |r-1| = {100*median_abs_dev:.2f}%")
print(f"[anchor] p90 |r-1|    = {100*p90_abs_dev:.2f}%")
print(f"[anchor] max |r-1|    = {100*np.max(np.abs(ratio-1.0)):.2f}%")
print(f"[anchor] Stage-1 benchmark: integral ratio 1.0047, median|r-1| 1.03%")

# also report without the interior restriction (all pt/pz-restricted bins, any theta)
both_rep_noninterior = rep_std & rep_xps2
a2 = x_pet_std[both_rep_noninterior]; b2 = x_pet_xps2[both_rep_noninterior]
print(f"\n[anchor, no theta-interior cut] n_bins={both_rep_noninterior.sum()} "
      f"integral ratio={b2.sum()/a2.sum():.4f} median|r-1|={100*np.median(np.abs(b2/a2-1.0)):.2f}%")
