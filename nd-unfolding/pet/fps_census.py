#!/usr/bin/env python3
"""FPS denominator / native-miss census + acceptance (Tier-1/Tier-2) map (P5A).

Reads ONLY the light arrays from an FPS point-cloud npz (pass_reco, pass_truth, w_truth,
truth_scalars, measured_*, edges) and the big-cloud SHAPES via the zip headers (no
materialization). Verifies event alignment, asserts the canonical extended FPS edges,
and reports the acceptance-supported (Tier-1, eff>=thr) vs prior-dominated (Tier-2, dead)
weighted-rate split on the (pT, p_parallel) truth grid. This is a P5A domain-integrity
validation, NOT a publication coverage/covariance claim (those are P5B)."""
import argparse
import sys
import zipfile

import numpy as np
import numpy.lib.format as npf

_ND = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding"
if _ND + "/pet" not in sys.path:
    sys.path.insert(0, _ND + "/pet")
import fullevent_fps_dataloader as fe  # noqa: E402


def _shape(z, key):
    with z.open(key + ".npy") as fh:
        ver = npf.read_magic(fh); shape, _, dt = npf._read_array_header(fh, ver)
    return shape, dt


def _load(z, key):
    with z.open(key + ".npy") as fh:
        return npf.read_array(fh, allow_pickle=False)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--eff-thr", type=float, default=0.02, help="Tier-1 efficiency threshold")
    ap.add_argument("--no-fps-guard", action="store_true")
    a = ap.parse_args()

    z = zipfile.ZipFile(a.inputs)
    have = {n[:-4] for n in z.namelist() if n.endswith(".npy")}
    # shapes for alignment (no materialization of the big clouds)
    shp = {k: _shape(z, k)[0] for k in ("part_reco", "part_gen", "measured_pc") if k in have}
    print(f"[census] {a.inputs}")
    for k, s in shp.items():
        print(f"[census]   {k}: {s}")

    edges_pt = _load(z, "edges_0"); edges_pz = _load(z, "edges_1")
    if not a.no_fps_guard:
        fe.assert_extended_fps_edges(edges_pt, edges_pz)
        print("[census] extended-FPS edge assertion: PASS")

    pr = _load(z, "pass_reco").astype(bool)
    pt = _load(z, "pass_truth").astype(bool)
    wt = _load(z, "w_truth").astype(np.float64)
    ts = _load(z, "truth_scalars").astype(np.float64)   # (N,4): pt,pz,eavail,q3
    mw = _load(z, "measured_weights").astype(np.float64)

    # alignment gates
    N = pr.shape[0]
    assert pt.shape[0] == N == wt.shape[0] == ts.shape[0], "[FAIL] MC-side row misalignment"
    assert shp["part_reco"][0] == N and shp["part_gen"][0] == N, "[FAIL] cloud rows != MC rows"
    assert shp["measured_pc"][0] == mw.shape[0], "[FAIL] data cloud rows != measured_weights"
    print(f"[census] alignment: MC rows={N}, data rows={mw.shape[0]} — PASS")

    # denominator / miss / signal / fake census (truth-authoritative gate)
    sig = pr & pt                     # reconstructed signal
    miss = pt & ~pr                   # native misses (FPS grows these)
    fake = pr & ~pt                   # fakes
    denom = pt                        # truth denominator
    wsig, wmiss, wden = wt[sig].sum(), wt[miss].sum(), wt[denom].sum()
    print(f"[census] truth denom (pass_truth): n={int(denom.sum())} sumw={wden:.4e}")
    print(f"[census] signal (reco&truth):      n={int(sig.sum())} sumw={wsig:.4e} "
          f"({100*wsig/wden:.1f}% of denom)")
    print(f"[census] native misses (truth&!reco): n={int(miss.sum())} sumw={wmiss:.4e} "
          f"({100*wmiss/wden:.1f}% of denom)  <- FPS-admitted")
    print(f"[census] fakes (reco&!truth):      n={int(fake.sum())}")
    print(f"[census] overall efficiency = sumw(sig)/sumw(denom) = {wsig/wden:.4f}")

    # acceptance map on the (pT,p||) truth grid -> Tier-1 (eff>=thr) vs Tier-2 (dead) rate
    ptv, pzv = ts[:, 0], ts[:, 1]
    ipt = np.clip(np.digitize(ptv, edges_pt) - 1, 0, len(edges_pt) - 2)
    ipz = np.clip(np.digitize(pzv, edges_pz) - 1, 0, len(edges_pz) - 2)
    ncell = (len(edges_pt) - 1) * (len(edges_pz) - 1)
    cell = ipt * (len(edges_pz) - 1) + ipz
    wden_cell = np.bincount(cell[denom], wt[denom], minlength=ncell)
    wsig_cell = np.bincount(cell[sig], wt[sig], minlength=ncell)
    eff_cell = np.divide(wsig_cell, wden_cell, out=np.zeros_like(wden_cell),
                         where=wden_cell > 0)
    tier1 = eff_cell >= a.eff_thr
    w_tier1 = wden_cell[tier1].sum(); w_tier2 = wden_cell[~tier1 & (wden_cell > 0)].sum()
    tot = wden_cell.sum()
    print(f"[census] reported cells populated: {int((wden_cell>0).sum())}/{ncell}")
    print(f"[census] Tier-1 acceptance-supported (eff>={a.eff_thr:g}): "
          f"{100*w_tier1/tot:.1f}% of truth rate")
    print(f"[census] Tier-2 prior-dominated dead cells:                "
          f"{100*w_tier2/tot:.1f}% of truth rate  <- carry prior band, NOT measured")
    print("[census] DONE (domain integrity ok; NOT a publication coverage claim)")


if __name__ == "__main__":
    main()
