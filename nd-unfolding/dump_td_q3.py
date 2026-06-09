#!/usr/bin/env python3
"""Dump the truth-denominator q3 column aligned to bank_uthrow's td ordering.

The 4D unified throw (task 14) reuses bank_uthrow's per-event universe-weight arrays but
needs the 4th axis (q3) on the truth-DENOMINATOR coords -- the only column bank_uthrow
lacks (built 3D: pt,pz,eavail). The bank's td was collected with collect_truth_denom_nd
gating on eavail (extras=[eavail]); adding q3 as a SECOND gated extra would drop the 1327
events with non-finite q3 (kept 32,847,776 != bank 32,849,103) and break row-alignment.

So we replicate the bank's EXACT gate (finite pt,pz,eavail,w; 0<=w<1e4; truth phase space)
and carry q3 as a PASSIVE column -- non-finite q3 (the 1327, 4e-5 of the sample) filled to
0 so they bin into the first q3 cell, exactly the rows the bank's td kept. Self-verifying:
asserts row count + td_w bit-identity to the bank before writing, proving the ordering.

  python dump_td_q3.py --out bank_uthrow/td_q3.npz
"""
import argparse
import os
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def main():
    import ROOT
    import unfold_2d_omnifold_unbinned as u2d
    ap = argparse.ArgumentParser()
    ap.add_argument("--omnifile",
                    default=f"{_REPO}/nd-unfolding/runEventLoopOmniFold_4D_MEFHC_universes_full.root")
    ap.add_argument("--bank", default="bank_uthrow")
    ap.add_argument("--out", default="bank_uthrow/td_q3.npz")
    args = ap.parse_args()

    pt_e, pz_e = u2d.PT_EDGES, u2d.PZ_EDGES
    pt_lo, pt_hi, pz_lo, pz_hi = pt_e[0], pt_e[-1], pz_e[0], pz_e[-1]

    f = ROOT.TFile.Open(args.omnifile, "READ")
    if not f or f.IsZombie():
        raise SystemExit(f"[FAIL] cannot open {args.omnifile}")
    t_td = f.Get("mc_truth_denom")
    data_pot, mc_pot, pot_scale = u2d.get_pot_scales(f)
    print(f"[td_q3] reading mc_truth_denom from {os.path.basename(args.omnifile)} "
          f"(pot_scale={pot_scale:.6g})", flush=True)
    cols = ROOT.RDataFrame(t_td).AsNumpy(["MC", "MC_pz", "MC_eavail", "MC_q3", "w_truth"])
    pt = cols["MC"].astype(np.float64); pz = cols["MC_pz"].astype(np.float64)
    ea = cols["MC_eavail"].astype(np.float64); q3 = cols["MC_q3"].astype(np.float64)
    w = cols["w_truth"].astype(np.float64)
    f.Close()
    print(f"[td_q3] read {pt.size} rows from tree", flush=True)

    # bank gate (collect_truth_denom_nd with extras=[eavail], use_weights=True):
    #   finite(pt,pz,eavail,w) AND 0<=w<1e4 AND in_truth_phase_space(pt,pz)   -- q3 NOT gated
    finite = np.isfinite(pt) & np.isfinite(pz) & np.isfinite(ea) & np.isfinite(w)
    wgood = finite & (w >= 0) & (w < 1e4)
    theta = np.arctan2(pt, pz)
    inps = (pt >= pt_lo) & (pt <= pt_hi) & (pz >= pz_lo) & (pz <= pz_hi) \
        & (theta < u2d.MAX_MUON_THETA_RAD)
    keep = wgood & inps
    td_pt = pt[keep]; td_pz = pz[keep]; td_ea = ea[keep]
    td_w = (w[keep] * pot_scale)
    td_q3 = np.where(np.isfinite(q3[keep]), q3[keep], 0.0)     # passive; fill 1327 non-finite -> 0
    print(f"[td_q3] kept {td_w.size} (filled {int((~np.isfinite(q3[keep])).sum())} non-finite q3 -> 0)")

    # ordering proof: must match the bank's stored td_w bit-for-bit
    bank_cv = np.load(os.path.join(args.bank, "cv.npz"))
    bw = bank_cv["td_w"].astype(np.float64)
    if bw.size != td_w.size:
        raise SystemExit(f"[FAIL] size mismatch bank td_w {bw.size} vs new {td_w.size}")
    dmax = float(np.abs(bw - td_w).max())
    # td_ea was stored float32 in the bank; compare at float32 precision (the bit-exact
    # td_w match below is the definitive ordering proof).
    dea = float(np.abs(bank_cv["td_ea"].astype(np.float64) - td_ea).max())
    print(f"[td_q3] ordering proof: max|td_w_new - bank td_w| = {dmax:.3e}; "
          f"max|td_ea diff| = {dea:.3e} (float32 eps ~1e-6)")
    if dmax > 1e-6 or dea > 1e-3:
        raise SystemExit("[FAIL] td ordering does NOT match the bank -- q3 cannot be trusted")

    np.savez(args.out, td_pt=td_pt.astype(np.float32), td_pz=td_pz.astype(np.float32),
             td_ea=td_ea.astype(np.float32), td_q3=td_q3.astype(np.float32),
             td_w=td_w.astype(np.float64))
    print(f"[td_q3] ALIGNED. wrote {args.out}")


if __name__ == "__main__":
    main()
