#!/usr/bin/env python3
"""LE -> ME beam-evolution shape comparison (qualitative; OPEN_ITEMS item 9).

Overlays our ME FHC CC-inclusive results against the LE-beam predecessors,
SHAPE-ONLY (the fluxes differ -- LE <E_nu> ~ 3.5 GeV vs ME ~ 6 GeV -- so no
chi2 is meaningful without a flux translation, which would be prior-dependent):

  1. Filkins 2002.12496 (LE CC-inclusive d sigma/dpT and d sigma/dp||):
     ptmu/pzmu_cross_section TH1Ds from anc/data_release vs our 4D product's
     hXSec_pt / hXSec_pz projections; each curve normalized to unit integral
     over its own range.
  2. Rodrigues 1511.05944 (LE low-recoil d^2 sigma/(dE_avail dq3)): Tables
     III+IV of anc/supplemental.txt (67 bins) rebinned onto our coarse
     (E_avail, q3) grid -- their edges nest exactly in ours -- then per-q3-slice
     E_avail shapes (unit integral over E_avail in [0, 0.8] GeV) vs the
     (E_avail, q3) marginal of our 4D product. Slices with incomplete LE
     coverage (q3 < 0.2) are skipped.

  python compare_le_evolution.py   # writes products/4d/le_evolution_compare.png
"""
import argparse
import re
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import unfold_2d_omnifold_unbinned as u2d
from xsec_nd import project_marginal

EAVAIL_EDGES = [0.0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100.0]
Q3_EDGES = [0.0, 0.2, 0.4, 0.6, 0.8, 1.2, 2.0, 100.0]

# Rodrigues grids (upper edges; lower edge of the first bin = 0)
ROD_EA_HI = [0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16,
             0.20, 0.25, 0.30, 0.35, 0.40, 0.50, 0.60, 0.80]
ROD_Q3_HI = [0.2, 0.3, 0.4, 0.5, 0.6, 0.8]


def th1_np(fn, name):
    import ROOT
    f = ROOT.TFile.Open(fn)
    h = f.Get(name)
    if not h:
        raise RuntimeError(f"{name} missing in {fn}")
    n = h.GetNbinsX()
    e = np.array([h.GetXaxis().GetBinLowEdge(i + 1) for i in range(n)]
                 + [h.GetXaxis().GetBinUpEdge(n)])
    y = np.array([h.GetBinContent(i + 1) for i in range(n)])
    f.Close()
    return e, y


def parse_rodrigues(path):
    """Tables III (bin map) + IV (values) -> dict (i_ea, i_q3) -> xsec density."""
    txt = open(path).read()
    # Table III rows: '<ea_hi> | idx idx ...' with fixed 5-char columns per q3 bin
    t3 = txt.split("Table III")[1].split("Table IV")[0]
    binmap = {}
    for line in t3.splitlines():
        m = re.match(r"^\s*(0\.\d+)\s*\|(.*)$", line)
        if not m:
            continue
        ea_hi = float(m.group(1))
        i_ea = ROD_EA_HI.index(ea_hi)
        # every column starts at the first E_avail row and ends at its own
        # acceptance limit, so a row's k reported indices fill the LAST k
        # q3 columns (no fixed-width parsing needed)
        toks = m.group(2).split()
        for k, tok in enumerate(toks):
            binmap[int(tok)] = (i_ea, 6 - len(toks) + k)
    t4 = txt.split("Table IV")[1]
    vals = {}
    for line in t4.splitlines():
        m = re.match(r"^\s*(\d+)\s+([\d.eE+-]+)\s*$", line)
        if m:
            vals[int(m.group(1))] = float(m.group(2))
    grid = np.full((len(ROD_EA_HI), len(ROD_Q3_HI)), np.nan)
    for b, (i, j) in binmap.items():
        grid[i, j] = vals[b]               # 1e-38 cm^2/GeV^2 density
    return grid


def rebin_rodrigues(grid):
    """Density grid (16 ea x 6 q3) -> our coarse 4 ea x 4 q3 (0-0.8 in both).

    Width-weighted average of densities (edges nest exactly). Returns the
    coarse density grid and a completeness mask (True = all source cells
    reported)."""
    ea_e = np.array([0.0] + ROD_EA_HI)
    q3_e = np.array([0.0] + ROD_Q3_HI)
    my_ea = np.array(EAVAIL_EDGES[:5])     # 0,0.1,0.2,0.4,0.8
    my_q3 = np.array(Q3_EDGES[:5])         # 0,0.2,0.4,0.6,0.8
    out = np.zeros((4, 4))
    cov = np.ones((4, 4), bool)
    for I in range(4):
        ii = np.where((ea_e[:-1] >= my_ea[I] - 1e-9) & (ea_e[1:] <= my_ea[I + 1] + 1e-9))[0]
        for J in range(4):
            jj = np.where((q3_e[:-1] >= my_q3[J] - 1e-9) & (q3_e[1:] <= my_q3[J + 1] + 1e-9))[0]
            tot, area = 0.0, 0.0
            for i in ii:
                for j in jj:
                    w = (ea_e[i + 1] - ea_e[i]) * (q3_e[j + 1] - q3_e[j])
                    v = grid[i, j]
                    if np.isnan(v):
                        cov[I, J] = False
                        continue
                    tot += v * w
                    area += w
            full = (my_ea[I + 1] - my_ea[I]) * (my_q3[J + 1] - my_q3[J])
            if area < full - 1e-9:
                cov[I, J] = False
            out[I, J] = tot / full if full > 0 else 0.0   # missing cells enter as 0
    return out, cov


def shape(y, widths):
    s = float((y * widths).sum())
    return y / s if s > 0 else y


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import ROOT
    ROOT.gErrorIgnoreLevel = ROOT.kError

    ap = argparse.ArgumentParser()
    ap.add_argument("--prod4d", default="products/4d/xsec_4d_MEFHC_5iter_lgbm.root")
    ap.add_argument("--filkins-dir", default="reference_le/filkins/anc/data_release")
    ap.add_argument("--rodrigues", default="reference_le/rodrigues/anc/supplemental.txt")
    ap.add_argument("--out-png", default="products/4d/le_evolution_compare.png")
    args = ap.parse_args()

    # ---- ours (ME) ----
    e_pt, me_pt = th1_np(args.prod4d, "hXSec_pt")
    e_pz, me_pz = th1_np(args.prod4d, "hXSec_pz")
    _, flat = th1_np(args.prod4d, "hXSecND_flat")
    edges4 = [list(u2d.PT_EDGES), list(u2d.PZ_EDGES), EAVAIL_EDGES, Q3_EDGES]
    x4 = flat.reshape([len(e) - 1 for e in edges4], order="C")
    me_eaq3 = project_marginal(x4, edges4, drop_axes=[0, 1])   # (7 ea, 7 q3) density

    # ---- Filkins (LE) ----
    le_pt_e, le_pt = th1_np(f"{args.filkins_dir}/cov_fullUncertainty_ptmu_CCInclusive.root",
                            "ptmu_cross_section")
    le_pz_e, le_pz = th1_np(f"{args.filkins_dir}/cov_fullUncertainty_pzmu_CCInclusive.root",
                            "pzmu_cross_section")

    # ---- Rodrigues (LE) ----
    rod, rod_cov = rebin_rodrigues(parse_rodrigues(args.rodrigues))

    fig = plt.figure(figsize=(15, 8))
    gs = fig.add_gridspec(2, 3, hspace=0.34, wspace=0.28)

    # row 1: Filkins muon-kinematics shapes
    for k, (le_e, le_y, e_me, y_me, lab, ttl, logx) in enumerate([
            (le_pt_e, le_pt, e_pt, me_pt, r"$p_T^\mu$ (GeV/c)",
             r"CC-inclusive $d\sigma/dp_T$ shape", False),
            (le_pz_e, le_pz, e_pz, me_pz, r"$p_\parallel^\mu$ (GeV/c)",
             r"CC-inclusive $d\sigma/dp_\parallel$ shape", True)]):
        ax = fig.add_subplot(gs[0, k])
        ax.stairs(shape(le_y, np.diff(le_e)), le_e, color="tab:blue", lw=2,
                  label=r"LE (Filkins, $\langle E_\nu\rangle\!\sim$3.5 GeV)")
        ax.stairs(shape(y_me, np.diff(e_me)), e_me, color="tab:red", lw=2,
                  label=r"ME (this work, $\langle E_\nu\rangle\!\sim$6 GeV)")
        ax.set_xlabel(lab)
        ax.set_ylabel("shape (unit integral)")
        if logx:
            ax.set_xscale("log")
        ax.legend(fontsize=8)
        ax.set_title(ttl)
    axt = fig.add_subplot(gs[0, 2])
    axt.axis("off")
    axt.text(0.0, 0.5,
             "SHAPE-ONLY comparison\n"
             "(fluxes differ; no $\\chi^2$ without a\n"
             "prior-dependent LE$\\to$ME translation)\n\n"
             "Filkins: LE CC-incl 2D, arXiv:2002.12496\n"
             "Rodrigues: LE low-recoil, arXiv:1511.05944\n"
             "Ours: 4D product marginals\n\n"
             "Rodrigues rebinned onto our coarse\n"
             "$(E_{avail},q_3)$ grid (edges nest exactly);\n"
             "$q_3<0.2$ skipped (incomplete LE coverage)",
             fontsize=9, va="center")

    # row 2: Rodrigues (E_avail, q3) per-q3-slice shapes (complete slices only)
    my_ea = np.array(EAVAIL_EDGES[:5])
    wid_ea = np.diff(my_ea)
    # q3 0.2-0.4 is skipped: after strict-completeness rebinning the LE data
    # cover only the single 0-0.1 GeV bin there (shape comparison trivial)
    for k, J in enumerate([2, 3]):         # q3 0.4-0.6, 0.6-0.8
        ax = fig.add_subplot(gs[1, k])
        # normalize both shapes over the LE-covered E_avail bins only, and
        # plot only that range (e.g. q3 0.2-0.4 has no LE data above 0.4 GeV)
        m = rod_cov[:, J]
        nlast = int(np.max(np.nonzero(m)) + 1)
        ea_cov = my_ea[:nlast + 1]
        w_cov = wid_ea[:nlast]
        ax.stairs(shape(rod[:nlast, J], w_cov), ea_cov, color="tab:blue", lw=2,
                  label="LE (Rodrigues)")
        ax.stairs(shape(me_eaq3[:nlast, J], w_cov), ea_cov, color="tab:red", lw=2,
                  label="ME (this work)")
        ax.set_xlabel(r"$E_{avail}$ (GeV)")
        ax.set_ylabel(f"shape (unit integral, 0-{ea_cov[-1]:g} GeV)")
        extra = "" if m[:nlast].all() and nlast == 4 else "  (LE-covered range)"
        ax.set_title(rf"$q_3 \in [{Q3_EDGES[J]}, {Q3_EDGES[J+1]})$ GeV{extra}")
        ax.legend(fontsize=8)

    # context map: our ME (E_avail, q3) density with the LE coverage boundary
    ax = fig.add_subplot(gs[1, 2])
    my_q3 = np.array(Q3_EDGES[:5])
    pc = ax.pcolormesh(my_q3, my_ea, me_eaq3[:4, :4], cmap="viridis")
    fig.colorbar(pc, ax=ax, label=r"ME $d^2\sigma/(dE_{avail}\,dq_3)$")
    for I in range(4):
        for J in range(4):
            if not rod_cov[I, J]:
                ax.add_patch(plt.Rectangle((my_q3[J], my_ea[I]),
                                           my_q3[J + 1] - my_q3[J],
                                           my_ea[I + 1] - my_ea[I],
                                           fill=False, hatch="///",
                                           edgecolor="white", lw=0.5))
    ax.set_xlabel(r"$q_3$ (GeV)")
    ax.set_ylabel(r"$E_{avail}$ (GeV)")
    ax.set_title("ME map; hatched = no complete LE coverage")

    fig.suptitle("LE -> ME beam evolution: shape comparison (qualitative)", fontsize=13)
    fig.savefig(args.out_png, dpi=140, bbox_inches="tight")
    print(f"[wrote] {args.out_png}")

    # numeric summary for the run log
    print("\n[Filkins pT]  LE/ME shape ratio per bin (common range):")
    # interpolate ME shape onto LE bin centres for a crude ratio
    for nm, (le_e, le_y, e_me, y_me) in [("pT", (le_pt_e, le_pt, e_pt, me_pt)),
                                         ("pz", (le_pz_e, le_pz, e_pz, me_pz))]:
        sl = shape(le_y, np.diff(le_e))
        sm = shape(y_me, np.diff(e_me))
        ctr = 0.5 * (le_e[:-1] + le_e[1:])
        idx = np.clip(np.digitize(ctr, e_me) - 1, 0, len(sm) - 1)
        ok = (ctr >= e_me[0]) & (ctr <= e_me[-1]) & (sm[idx] > 0)
        r = sl[ok] / sm[idx][ok]
        print(f"  [{nm}] LE bins in ME range: {ok.sum()}/{len(ctr)}  "
              f"shape ratio LE/ME median={np.median(r):.3f}  "
              f"range [{r.min():.2f}, {r.max():.2f}]")
    for J in (1, 2, 3):
        m = rod_cov[:, J]
        nlast = int(np.max(np.nonzero(m)) + 1)
        w_cov = wid_ea[:nlast]
        sl = shape(rod[:nlast, J], w_cov)
        sm = shape(me_eaq3[:nlast, J], w_cov)
        ok = sm > 0
        print(f"  [eavail | q3 {Q3_EDGES[J]}-{Q3_EDGES[J+1]}, LE-covered 0-"
              f"{my_ea[nlast]:g}] shape ratio LE/ME per bin: "
              + ", ".join(f"{a/b:.2f}" for a, b in zip(sl[ok], sm[ok])))


if __name__ == "__main__":
    main()
