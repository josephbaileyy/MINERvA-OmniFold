#!/usr/bin/env python3
"""Versioned generator for the PET point-cloud INPUT figures used in the
analysis note (sec_validation) and the July-16 talk. Resolves KNOWN_ISSUES #18
(these were ad-hoc products with no script, absent from make_figures.sh).

Source of truth: the truth-cloud-coverage-FIXED inputs
``of_inputs_pc_fullcloud.npz`` (2026-06-28 fix, commit 8cc54e9). The pre-fix
``of_inputs_pc.npz`` left the truth cloud EMPTY on truth-only-miss rows (~27% of
events), which produced a spurious cardinality-0 spike and dragged the truth
mean down to ~3.3; do NOT plot from it (KNOWN_ISSUES #18).

Writes (to --outdir, default products/pet):
  pet_event_displays.{png,pdf}          example reco-cluster & truth-hadron clouds
  pet_cardinality_real.{png,pdf}        per-event cardinality, truth real FS hadrons only
  pet_cardinality_withremnant.{png,pdf} same, truth incl. GENIE nuclear-remnant pseudo-codes
  pet_truncation_retention.{png,pdf}    energy retained vs truncation cap (num_part argument)

Reco points are recoil CALORIMETER CLUSTERS: each carries (energy, detector
position) -- there is no per-cluster momentum (the muon, which is tracked and
does have a reco momentum, is removed from the cloud). Truth points are GENIE
final-state hadrons with full momentum.

Light (note) is the default; run with TECHNOTE_DARK=1 for the deck -- technote_style
gates the theme (same filenames, dark ground) and STRIPS titles, so per-panel
text uses ax.text and all description lives in the LaTeX caption.

  python pet/plot_event_displays.py [--npz of_inputs_pc_fullcloud.npz] [--outdir products/pet]
"""
import argparse
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
for _a in (os.path.dirname(_HERE), os.path.dirname(os.path.dirname(_HERE))):
    if os.path.exists(os.path.join(_a, "technote_style.py")):
        sys.path.insert(0, _a)
        break

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import technote_style  # noqa: E402,F401  (title-strip + .pdf twin + TECHNOTE_DARK gating)
import matplotlib.pyplot as plt  # noqa: E402

# PDG -> (label, colour) for the truth cloud (mid-tone hues; TECHNOTE_DARK
# remaps hardcoded colours at savefig time).
PDG = {2212: ("p", "#4C72B0"), 2112: ("n", "#8C8C8C"), 211: (r"$\pi^+$", "#DD8452"),
       -211: (r"$\pi^-$", "#C44E52"), 111: (r"$\pi^0$", "#55A868"),
       22: (r"$\gamma$", "#CCB974"), 321: (r"$K^+$", "#64B5CD"), -321: (r"$K^-$", "#937860")}
_PSEUDO = 1_000_000_000  # |pdg| >= this are GENIE nuclear-remnant / bookkeeping pseudo-codes


def _card(cloud):
    """points per event = slots with non-zero energy (feature 0)."""
    return (cloud[:, :, 0] != 0).sum(axis=1)


def _card_real(cloud):
    """truth points per event counting only physical FS hadrons (drop pseudo-codes)."""
    return ((cloud[:, :, 0] != 0) & (np.abs(cloud[:, :, 4]) < _PSEUDO)).sum(axis=1)


def _wfrac(c, w, P):
    h = np.array([w[c == k].sum() for k in range(P + 1)])
    return h / h.sum()


def make_cardinality(z, P, pg, pr, mc, ptru, prec, wt, wr, wm, outdir):
    c_all, c_real, w_t = _card(pg)[ptru], _card_real(pg)[ptru], wt[ptru]
    c_r, w_r = _card(pr)[prec], wr[prec]
    c_m, w_m = _card(mc), wm
    fr, fm = _wfrac(c_r, w_r, P), _wfrac(c_m, w_m, P)
    x = np.arange(P + 1)

    def one(c_t, tlabel, outname):
        ft = _wfrac(c_t, w_t, P)
        fig, ax = plt.subplots(figsize=(8.2, 5.2))
        ax.step(x, ft, where="mid", lw=2.0, color="#4C72B0",
                label=f"{tlabel} (mean {np.average(c_t, weights=w_t):.2f})")
        ax.step(x, fr, where="mid", lw=2.0, color="#55A868",
                label=f"reco clusters, MC (mean {np.average(c_r, weights=w_r):.2f})")
        ax.errorbar(x, fm, fmt="o", ms=5, color="k",
                    label=f"reco clusters, data (mean {np.average(c_m, weights=w_m):.2f})")
        ax.axvline(P, color="0.6", ls=(0, (2, 2)), lw=1.0)
        ax.annotate(f"truncation cap = {P}", xy=(P, ax.get_ylim()[1] * 0.6),
                    xytext=(-6, 0), textcoords="offset points", ha="right",
                    rotation=90, va="center", fontsize=10, color="0.4")
        ax.set_xlabel("point-cloud cardinality (points per event)")
        ax.set_ylabel("fraction of events (POT-weighted)")
        ax.set_yscale("log")
        ax.set_xlim(-0.5, P + 0.5)
        ax.set_xticks(x)
        ax.legend(frameon=False, fontsize=11)
        fig.tight_layout()
        fig.savefig(os.path.join(outdir, outname), dpi=140, bbox_inches="tight")
        plt.close(fig)
        print(f"[card] {outname}: mean={np.average(c_t, weights=w_t):.3f} "
              f"f0={ft[0]:.4f} f1={ft[1]:.4f} f2={ft[2]:.4f} cap={ft[P]:.4f}")

    one(c_real, "truth FS hadrons (real only)", "pet_cardinality_real.png")
    one(c_all, "truth FS hadrons (incl. nuclear remnants)", "pet_cardinality_withremnant.png")


def make_retention(pg, pr, ptru, prec, P, outdir, sub=3_000_000):
    def retention(cloud, mask):
        idx = np.where(mask)[0][:sub]
        E = -np.sort(-cloud[idx][:, :, 0].astype(np.float64), axis=1)
        cs = np.cumsum(E, axis=1)
        tot = np.where(cs[:, -1:] > 0, cs[:, -1:], np.nan)
        return np.nanmean(cs / tot, axis=0), np.nanmean(E / tot, axis=0)

    ct, mt_ = retention(pg, ptru)
    cr, mr_ = retention(pr, prec)
    sat_t = (_card(pg)[ptru] >= P).sum() / ptru.sum()
    xx = np.arange(1, P + 1)
    fig, ax = plt.subplots(figsize=(7.6, 5.2))
    ax.plot(xx, 100 * ct, "o-", color="#4C72B0", lw=2, label="truth FS hadrons")
    ax.plot(xx, 100 * cr, "s-", color="#55A868", lw=2, label="reco clusters")
    ax.axvline(P, color="0.6", ls=(0, (2, 2)), lw=1)
    ax.annotate(f"12th slot: {100 * mt_[-1]:.2f}%", xy=(P, 100 * ct[-1]),
                xytext=(-95, -16), textcoords="offset points", fontsize=9, color="0.35")
    ax.annotate(f"12th slot: {100 * mr_[-1]:.2f}%", xy=(P, 100 * cr[-1]),
                xytext=(-95, 4), textcoords="offset points", fontsize=9, color="0.35")
    ax.set_xlabel("truncation cap $P$ (highest-energy constituents kept)")
    ax.set_ylabel("mean cumulative energy retained\n(% of the kept top-12 energy)")
    ax.set_xticks(xx)
    ax.set_ylim(20, 103)
    ax.legend(frameon=False)
    ax.text(0.02, 0.02, r"memory $\propto P$; attention $\propto P^{2}$",
            transform=ax.transAxes, fontsize=8, color="0.45")
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, "pet_truncation_retention.png"), dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"[ret] truth 12th slot {100 * mt_[-1]:.2f}%  reco {100 * mr_[-1]:.2f}%  "
          f"truth saturation(>=12) {100 * sat_t:.2f}%")


def make_displays(z, pg, pr, ptru, prec, outdir, n_events=4):
    rec_sc, tru_sc = z["reco_scalars"], z["truth_scalars"]
    both = np.where(ptru & prec)[0]
    cr_cnt = _card(pr)[both]
    ea = rec_sc[both, 2]
    keep = both[(cr_cnt >= 5) & (cr_cnt <= 12) & (ea > 0.05) & (ea < 3.0)
                & (_card_real(pg)[both] >= 2)]
    order = keep[np.argsort(rec_sc[keep, 2])]
    picks = order[np.linspace(0, len(order) - 1, n_events).astype(int)]

    fig, axs = plt.subplots(n_events, 2, figsize=(11, 3.7 * n_events))
    for row, ev in enumerate(picks):
        # LEFT: reco recoil clusters in DETECTOR POSITION space (no per-cluster momentum)
        rc = pr[ev]
        m = rc[:, 0] != 0
        E, pos, zz = rc[m, 0], rc[m, 1], rc[m, 2]
        A = axs[row, 0]
        s = 40 + 260 * (E / E.max() if E.max() > 0 else E)
        sc = A.scatter(zz, pos, s=s, c=E, cmap=technote_style.SEQ_CMAP,
                       edgecolor="k", lw=0.4, alpha=0.9)
        fig.colorbar(sc, ax=A, fraction=0.046, label="cluster energy [MeV]")
        A.set_xlabel("cluster $z$ (detector position) [mm]")
        A.set_ylabel("cluster transverse position [mm]")
        rs = rec_sc[ev]
        A.text(0.03, 0.96, f"reco recoil clusters: {m.sum()}\n"
               f"$E_{{avail}}$={rs[2]:.2f}, $q_3$={rs[3]:.2f} GeV",
               transform=A.transAxes, va="top", ha="left", fontsize=9)
        # RIGHT: truth FS hadrons in MOMENTUM space, coloured by species
        tc = pg[ev]
        mt = tc[:, 0] != 0
        Et, px, py, pz, pdg = (tc[mt, 0], tc[mt, 1], tc[mt, 2], tc[mt, 3],
                               tc[mt, 4].astype(int))
        pT = np.hypot(px, py)
        B = axs[row, 1]
        seen = set()
        for j in range(mt.sum()):
            code = int(pdg[j])
            lab, col = (("nucl./pseudo", "0.7") if abs(code) >= _PSEUDO
                        else PDG.get(code, (str(code), "0.5")))
            st = 40 + 260 * (Et[j] / Et.max() if Et.max() > 0 else 0)
            B.scatter(pz[j], pT[j], s=st, color=col, edgecolor="k", lw=0.4, alpha=0.9,
                      label=lab if lab not in seen else None)
            seen.add(lab)
        ts = tru_sc[ev]
        B.set_xlabel(r"$p_z$ (momentum) [MeV]")
        B.set_ylabel(r"$p_T$ (momentum) [MeV]")
        B.text(0.03, 0.96, f"truth FS hadrons: {mt.sum()}\n"
               f"$E_{{avail}}$={ts[2]:.2f}, $q_3$={ts[3]:.2f} GeV",
               transform=B.transAxes, va="top", ha="left", fontsize=9)
        B.legend(frameon=False, fontsize=8, loc="upper right", ncol=2)
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, "pet_event_displays.png"), dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"[disp] wrote pet_event_displays (events {list(map(int, picks))})")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--npz", default="of_inputs_pc_fullcloud.npz",
                    help="coverage-FIXED point-cloud inputs (NOT the pre-06-28 of_inputs_pc.npz)")
    ap.add_argument("--outdir", default="products/pet")
    ap.add_argument("--no-displays", action="store_true")
    ap.add_argument("--no-cardinality", action="store_true")
    ap.add_argument("--no-retention", action="store_true")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    if "of_inputs_pc.npz" in os.path.basename(args.npz):
        print("[WARN] --npz points at the pre-06-28 (stale) file; the truth cardinality "
              "will show a spurious k=0 spike. Use of_inputs_pc_fullcloud.npz (KNOWN_ISSUES #18).")

    z = np.load(args.npz, allow_pickle=True)
    P = int(z["num_part"])
    pg, pr, mc = z["part_gen"], z["part_reco"], z["measured_pc"]
    ptru, prec = z["pass_truth"], z["pass_reco"]
    wt, wr, wm = z["w_truth"], z["w_reco"], z["measured_weights"]
    print(f"[load] {args.npz}: N={len(pg)} num_part={P} "
          f"pass_truth={ptru.sum()} pass_reco={prec.sum()}")

    if not args.no_cardinality:
        make_cardinality(z, P, pg, pr, mc, ptru, prec, wt, wr, wm, args.outdir)
    if not args.no_retention:
        make_retention(pg, pr, ptru, prec, P, args.outdir)
    if not args.no_displays:
        make_displays(z, pg, pr, ptru, prec, args.outdir)
    print("[plot_event_displays] DONE")


if __name__ == "__main__":
    main()
