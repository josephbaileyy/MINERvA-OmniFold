#!/usr/bin/env python3
"""Offline genuine-vs-fake background channel split.

KNOWN_ISSUES #13 companion / Ruterbories (arXiv:2106.16210) 0.2% cross-check.

Reads the per-event truth channel labels that the C++ event loop's BkgTreeReco
path writes on the mc_background tree (bkg_nuPDG, bkg_current, bkg_inttype,
bkg_vtx_{x,y,z}) and classifies each SELECTED background event to reproduce the
Ruterbories NARROW background definition (wrong flavour + wrong sign + NC) and
contrast it with our BROAD definition (NARROW + out-of-fiducial-vertex).

The signal channel + fiducial test mirror CCInclusiveSignal.h EXACTLY
(truth::IsNeutrino / IsCC / ZRange / Apothem):

  numu-CC signal channel : GetTruthNuPDG() == 14  AND  GetCurrent() == 1
  fiducial vertex        : 5980 <= z <= 8422  (ZRange 'Tracker')  AND  the
                           hexagonal Apothem(850) cut, which in the framework is
                             |y| < fSlope*|x| + 2*apothem/sqrt(3)   AND  |x| < apothem
                           with fSlope = -1/sqrt(3), apothem = 850 (mm).

Categories (mutually exclusive; every selected bkg event lands in exactly one):
  wrong_sign       pdg == -14                                  (numubar)
  wrong_flavour    |pdg| in {12, 16}                           (nue / nutau, either sign)
  nc               pdg == 14 AND current != 1                  (numu neutral current)
  out_of_fiducial  pdg == 14 AND current == 1 AND vertex outside the fiducial
  fake             pdg == 14 AND current == 1 AND vertex inside the fiducial
                   (an out-of-PHASE-SPACE signal event -- NOT genuine background;
                    present because Phase 18's fill keeps  if(isSignal && inPS) continue;)

  NARROW genuine = wrong_sign + wrong_flavour + nc     (Ruterbories-comparable, ~0.2%)
  BROAD  genuine = NARROW + out_of_fiducial            (our definition -> the ~0.35%)

Rates are POT-scaled bkg-weight sums expressed as a fraction of the data event
count (data weight = 1). Compare NARROW to Ruterbories' 8655 events (0.2%) and
BROAD to the archived playlist-1A 0.35%.

REQUIRES an omnifile produced by the event loop AFTER the 2026-07-04 C++ change
(the bkg_* label branches; staged, not yet re-run). Fails loudly if the labels
are absent so a pre-change file is never silently misread.

  python3 bkg_channel_split.py --omnifile <MEFHC omnifile> [--json out.json]
"""
import argparse
import json
import math
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
if f"{_REPO}/2d-unfolding" not in sys.path:
    sys.path.insert(0, f"{_REPO}/2d-unfolding")

# Fiducial constants -- must match runEventLoopOmniFold.cpp / CCInclusiveSignal.h.
MINZ, MAXZ, APOTHEM = 5980.0, 8422.0, 850.0
_SLOPE = -1.0 / math.sqrt(3.0)


def in_fiducial(x, y, z):
    """Vectorized ZRange('Tracker') + Apothem(850) on the truth vertex (mm),
    a bit-for-bit port of truth::ZRange::checkConstraint and
    truth::Apothem::checkConstraint in CCInclusiveSignal.h."""
    zr = (z >= MINZ) & (z <= MAXZ)
    apo = (np.abs(y) < _SLOPE * np.abs(x) + 2.0 * APOTHEM / math.sqrt(3.0)) \
        & (np.abs(x) < APOTHEM)
    return zr & apo


def _read_bkg(t):
    """Per-event read of the selected mc_background labels into numpy arrays.
    Returns (pdg, current, inttype, x, y, z, w) for events with
    sim_background_pass != 0 and a finite, in-range w_bkg (matches
    und.collect_bkg_nd's weight guard)."""
    from array import array
    need = ["bkg_nuPDG", "bkg_current", "bkg_inttype",
            "bkg_vtx_x", "bkg_vtx_y", "bkg_vtx_z", "w_bkg", "sim_background_pass"]
    for b in need:
        if not t.GetBranch(b):
            raise RuntimeError(
                f"[FAIL] '{b}' missing from mc_background -- this omnifile predates "
                "the 2026-07-04 BkgTreeReco channel-label change. Re-run the event "
                "loop (the labels are dumped unconditionally, no env var needed).")
    a_pdg = array("i", [0]); a_cur = array("i", [0]); a_int = array("i", [0])
    a_x = array("d", [0.0]); a_y = array("d", [0.0]); a_z = array("d", [0.0])
    a_w = array("d", [0.0]); a_pass = array("B", [0])
    t.SetBranchAddress("bkg_nuPDG", a_pdg); t.SetBranchAddress("bkg_current", a_cur)
    t.SetBranchAddress("bkg_inttype", a_int)
    t.SetBranchAddress("bkg_vtx_x", a_x); t.SetBranchAddress("bkg_vtx_y", a_y)
    t.SetBranchAddress("bkg_vtx_z", a_z)
    t.SetBranchAddress("w_bkg", a_w); t.SetBranchAddress("sim_background_pass", a_pass)
    pdg, cur, itp, xs, ys, zs, ws = [], [], [], [], [], [], []
    n = t.GetEntries()
    for i in range(n):
        t.GetEntry(i)
        if a_pass[0] == 0:
            continue
        w = float(a_w[0])
        if not (math.isfinite(w) and 0 <= w < 1e6):
            continue
        pdg.append(int(a_pdg[0])); cur.append(int(a_cur[0])); itp.append(int(a_int[0]))
        xs.append(float(a_x[0])); ys.append(float(a_y[0])); zs.append(float(a_z[0]))
        ws.append(w)
    return (np.asarray(pdg), np.asarray(cur), np.asarray(itp),
            np.asarray(xs), np.asarray(ys), np.asarray(zs), np.asarray(ws))


def classify(pdg, current, x, y, z):
    """Return a dict category -> boolean mask (mutually exclusive, exhaustive
    over the selected sample). See module docstring for the definitions."""
    is_numu = pdg == 14
    is_cc = current == 1
    fid = in_fiducial(x, y, z)
    wrong_sign = pdg == -14
    wrong_flavour = np.isin(np.abs(pdg), [12, 16])
    nc = is_numu & ~is_cc
    numu_cc = is_numu & is_cc
    out_fid = numu_cc & ~fid
    fake = numu_cc & fid
    return {
        "wrong_sign": wrong_sign,
        "wrong_flavour": wrong_flavour,
        "nc": nc,
        "out_of_fiducial": out_fid,
        "fake": fake,
    }


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--omnifile",
                    default=f"{_REPO}/2d-unfolding/baseline_flux/runEventLoopOmniFold_MEFHC.root",
                    help="omnifile with the bkg_* channel labels (post-2026-07-04)")
    ap.add_argument("--json", default=None, help="write the summary to this path")
    args = ap.parse_args()

    import ROOT
    import unfold_2d_omnifold_unbinned as u2d

    f = ROOT.TFile.Open(args.omnifile)
    if not f or f.IsZombie():
        raise RuntimeError(f"cannot open {args.omnifile}")
    data_pot, mc_pot, pot_scale = u2d.get_pot_scales(f)
    t_bkg, t_data = f.Get("mc_background"), f.Get("data")
    n_data = int(t_data.GetEntries())   # data weight == 1

    pdg, cur, itp, xs, ys, zs, ws = _read_bkg(t_bkg)
    f.Close()

    cats = classify(pdg, cur, xs, ys, zs)
    # Sanity: categories partition the selected sample exactly once each.
    cover = np.zeros(ws.shape[0], int)
    for m in cats.values():
        cover += m.astype(int)
    assert np.all(cover == 1), (
        f"category partition broken: {np.bincount(cover)} (expected all==1)")

    def rate(mask):
        wsum = float(ws[mask].sum()) * pot_scale
        return wsum, (wsum / n_data if n_data else float("nan"))

    per_cat = {k: rate(m) for k, m in cats.items()}
    narrow_mask = cats["wrong_sign"] | cats["wrong_flavour"] | cats["nc"]
    broad_mask = narrow_mask | cats["out_of_fiducial"]
    total_bkg_w = float(ws.sum()) * pot_scale
    narrow_w, narrow_frac = rate(narrow_mask)
    broad_w, broad_frac = rate(broad_mask)
    fake_w, fake_frac = per_cat["fake"]

    print(f"omnifile        : {args.omnifile}")
    print(f"data POT        : {data_pot:.4e}   mc POT: {mc_pot:.4e}   scale: {pot_scale:.4f}")
    print(f"data entries    : {n_data}")
    print(f"selected bkg    : {ws.shape[0]} rows, {total_bkg_w:.1f} POT-scaled "
          f"({total_bkg_w / n_data * 100:.3f}% of data)")
    print("-" * 64)
    print(f"{'category':<16}{'POT-scaled':>14}{'% of data':>12}")
    for k in ("wrong_sign", "wrong_flavour", "nc", "out_of_fiducial", "fake"):
        w, fr = per_cat[k]
        print(f"{k:<16}{w:>14.1f}{fr * 100:>11.3f}%")
    print("-" * 64)
    print(f"NARROW genuine  {narrow_w:>14.1f}{narrow_frac * 100:>11.3f}%   "
          f"(Ruterbories def; compare 8655 / 0.2%)")
    print(f"BROAD  genuine  {broad_w:>14.1f}{broad_frac * 100:>11.3f}%   "
          f"(our def; compare playlist-1A 0.35%)")
    print(f"fakes (out-of-PS signal) {fake_w:.1f}  ({fake_frac * 100:.3f}%) "
          f"-- NOT genuine background")

    summary = {
        "omnifile": args.omnifile,
        "data_pot": data_pot, "mc_pot": mc_pot, "pot_scale": pot_scale,
        "n_data": n_data, "n_selected_bkg": int(ws.shape[0]),
        "total_bkg_pot_scaled": total_bkg_w,
        "per_category_pot_scaled": {k: per_cat[k][0] for k in per_cat},
        "per_category_frac_of_data": {k: per_cat[k][1] for k in per_cat},
        "narrow_genuine_pot_scaled": narrow_w, "narrow_genuine_frac": narrow_frac,
        "broad_genuine_pot_scaled": broad_w, "broad_genuine_frac": broad_frac,
        "ruterbories_ref_events": 8655, "ruterbories_ref_frac": 0.002,
    }
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(summary, fh, indent=2)
        print(f"[json] wrote {args.json}")


if __name__ == "__main__":
    main()
