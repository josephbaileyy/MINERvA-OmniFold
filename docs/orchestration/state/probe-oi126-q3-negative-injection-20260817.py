"""How much negative weight is there to clip, and is it LOCALISED?

Jensen's gap is bounded by how often and how hard the projection bites. If the negative
injection is diffuse, the refinement is near-linear everywhere and (c) has no localisation
mechanism -- it cannot produce a band-confined displacement with a sign flip.

WHERE THE NEGATIVES ARE. The refined targets are all non-negative (min 0.0 measured), so the
negatives live in the RAW measured leg before refinement:

    measured leg = 4,116,128 DATA rows (positive) + 564,591 BACKGROUND rows (injected NEGATIVE)
                 = 4,680,719 = the target length, exactly.

Stay-Positive clips where the signed sum in a cell goes negative, i.e. WHERE BACKGROUND
OUTWEIGHS DATA. That ratio, per cell, is the localisation question.

A STRUCTURAL CAVEAT, STATED RATHER THAN BINNED OVER:
The 63 tail cells are TRUTH-space (the xsec grid). The measured leg is RECO-space, and DATA
ROWS HAVE NO TRUTH COORDINATE AT ALL. So "negatives in the 63 truth cells" is not a defined
quantity. What is defined, and is reported here, is the RECO-space band on the SAME edges:
p_par bins 10-15 = 6-20 GeV. That is informative about localisation without pretending to be
the truth-cell set.
"""
import json

import numpy as np

R = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
NPZ = f"{R}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz"
PT = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.4, 0.47, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5, 2.5, 4.5,
               30.0], float)
PP = np.array([0.0, 0.75, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0,
               20.0, 40.0, 60.0, 120.0], float)
NPT, NPP = 15, 19
NC = NPT * NPP

z = np.load(NPZ, allow_pickle=False)
ds = np.asarray(z["measured_scalars"], np.float64)
bs = np.asarray(z["bkg_reco_scalars"], np.float64)
wb = np.asarray(z["w_bkg"], np.float64)
z.close()
print(f"data rows {ds.shape[0]}   bkg rows {bs.shape[0]}   sum -> {ds.shape[0] + bs.shape[0]}")
print(f"w_bkg: min {wb.min():.4e}  max {wb.max():.4e}  mean {wb.mean():.4e}  sum {wb.sum():.6e}")
print(f"w_bkg sign: {'all positive (subtracted downstream)' if (wb >= 0).all() else 'MIXED/NEGATIVE as stored'}")


def cells(pt, pp):
    i = np.clip(np.digitize(pt, PT) - 1, 0, NPT - 1)
    j = np.clip(np.digitize(pp, PP) - 1, 0, NPP - 1)
    return i * NPP + j


cd = cells(ds[:, 0], ds[:, 1])
cb = cells(bs[:, 0], bs[:, 1])
data_n = np.bincount(cd, minlength=NC).astype(float)          # data rows are unit weight
bkg_m = np.bincount(cb, weights=wb, minlength=NC)
bkg_n = np.bincount(cb, minlength=NC).astype(float)

tot_neg_rows = bs.shape[0] / (ds.shape[0] + bs.shape[0])
tot_neg_mass = wb.sum() / (data_n.sum() + wb.sum())
print(f"\nGLOBAL  negative ROWS  {tot_neg_rows:.4%}   negative MASS {tot_neg_mass:.4%}")

live = data_n + bkg_m > 0
frac = np.zeros(NC)
frac[live] = bkg_m[live] / (data_n[live] + bkg_m[live])
clipped = (bkg_m > data_n) & live       # cells where the signed sum would go negative


def report(sel, label):
    s = sel & live
    n = int(s.sum())
    if not n:
        print(f"  {label:26s} no live cells")
        return
    print(f"  {label:26s} cells {n:3d}  median bkg-share {np.median(frac[s]):.3%}  "
          f"max {frac[s].max():.3%}  cells where bkg>data: {int((clipped & s).sum())}")


col = np.arange(NC) % NPP
print("\nBACKGROUND SHARE OF THE MEASURED LEG, per reco cell:")
report(np.ones(NC, bool), "ALL live")
report((col >= 10) & (col <= 15), "reco band 6-20 GeV")
report(col <= 9, "reco p|| < 6 GeV")
report(col >= 16, "reco p|| > 20 GeV")

print(f"\nCELLS WHERE THE PROJECTION CAN BITE (bkg mass > data count): "
      f"{int(clipped.sum())} of {int(live.sum())} live")
print(f"  of those, in the reco 6-20 band: {int((clipped & (col >= 10) & (col <= 15)).sum())}")

out = {"what": "negative-injection extent and localisation, reco space",
       "data_rows": int(ds.shape[0]), "bkg_rows": int(bs.shape[0]),
       "global_negative_row_fraction": float(tot_neg_rows),
       "global_negative_mass_fraction": float(tot_neg_mass),
       "w_bkg_sum": float(wb.sum()), "w_bkg_all_positive_as_stored": bool((wb >= 0).all()),
       "live_cells": int(live.sum()),
       "cells_where_bkg_exceeds_data": int(clipped.sum()),
       "cells_where_bkg_exceeds_data_in_reco_band_10_15": int(
           (clipped & (col >= 10) & (col <= 15)).sum()),
       "median_bkg_share_all": float(np.median(frac[live])),
       "median_bkg_share_band_10_15": float(np.median(frac[live & (col >= 10) & (col <= 15)])),
       "median_bkg_share_below_6": float(np.median(frac[live & (col <= 9)])),
       "median_bkg_share_above_20": float(np.median(frac[live & (col >= 16)])),
       "CAVEAT": ("RECO space. The 63 tail cells are TRUTH space and data rows carry no truth "
                  "coordinate, so a truth-cell negative fraction is not a defined quantity."),
       "per_cell_bkg_share": [float(x) for x in frac]}
print("\n<<<RECEIPT_JSON>>>")
print(json.dumps(out, indent=1, sort_keys=True))
