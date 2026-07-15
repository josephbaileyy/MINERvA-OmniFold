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
Optional alternative displays (exploratory; off by default, not in the note build):
  --energy-angle  -> pet_event_displays_energy_angle.{png,pdf}  (E vs polar angle, both levels)
  --render-3d     -> pet_event_displays_3d.{png,pdf}            (truth cones from the vertex
                     opening onto the reco-cluster plane)

Reco points are recoil CALORIMETER CLUSTERS: each carries (energy, detector
position) -- there is no per-cluster momentum (the muon, which is tracked and
does have a reco momentum, is removed from the cloud). Truth points are GENIE
final-state hadrons with full momentum. The reco cloud has NO stored vertex, so
the angle/3D views place the reco geometry w.r.t. a nominal per-event vertex
(upstream of the clusters) -- illustrative; a faithful version needs the
reconstructed vertex added to the dump.

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
from mpl_toolkits.mplot3d import Axes3D  # noqa: E402,F401  (registers 3d projection)

# PDG -> (label, colour) for the truth cloud (mid-tone hues; TECHNOTE_DARK
# remaps hardcoded colours at savefig time).
PDG = {2212: ("p", "#4C72B0"), 2112: ("n", "#8C8C8C"), 211: (r"$\pi^+$", "#DD8452"),
       -211: (r"$\pi^-$", "#C44E52"), 111: (r"$\pi^0$", "#55A868"),
       22: (r"$\gamma$", "#CCB974"), 321: (r"$K^+$", "#64B5CD"), -321: (r"$K^-$", "#937860")}
_PSEUDO = 1_000_000_000  # |pdg| >= this are GENIE nuclear-remnant / bookkeeping pseudo-codes


def _card(cloud):
    return (cloud[:, :, 0] != 0).sum(axis=1)


def _card_real(cloud):
    return ((cloud[:, :, 0] != 0) & (np.abs(cloud[:, :, 4]) < _PSEUDO)).sum(axis=1)


def _wfrac(c, w, P):
    h = np.array([w[c == k].sum() for k in range(P + 1)])
    return h / h.sum()


def _pdg_label(code):
    return (("nucl./pseudo", "0.7") if abs(int(code)) >= _PSEUDO
            else PDG.get(int(code), (str(int(code)), "0.5")))


def _headroom(ax, frac=0.40, log=False):
    """Reserve an empty band at the top of the axes for text/legend so they do
    not sit on top of data markers."""
    y0, y1 = ax.get_ylim()
    if log:
        import math
        ax.set_ylim(y0, y0 * (y1 / y0) ** (1.0 / (1.0 - frac)))
    else:
        ax.set_ylim(y0, y0 + (y1 - y0) / (1.0 - frac))


def _pick_events(z, pg, pr, ptru, prec, n):
    rec_sc = z["reco_scalars"]
    both = np.where(ptru & prec)[0]
    cr_cnt = _card(pr)[both]
    ea = rec_sc[both, 2]
    keep = both[(cr_cnt >= 5) & (cr_cnt <= 12) & (ea > 0.05) & (ea < 3.0)
                & (_card_real(pg)[both] >= 2)]
    order = keep[np.argsort(rec_sc[keep, 2])]
    return order[np.linspace(0, len(order) - 1, n).astype(int)]


# ---------------------------------------------------------------------------
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
    """Canonical two-panel display: reco clusters in detector position space
    beside truth hadrons in momentum space. Per-panel text and legend live in a
    reserved top band (headroom) so they never overlap data markers."""
    rec_sc, tru_sc = z["reco_scalars"], z["truth_scalars"]
    picks = _pick_events(z, pg, pr, ptru, prec, n_events)

    fig, axs = plt.subplots(n_events, 2, figsize=(11, 3.7 * n_events))
    for row, ev in enumerate(picks):
        # LEFT: reco recoil clusters in DETECTOR POSITION space (no per-cluster momentum)
        rc = pr[ev]
        m = rc[:, 0] != 0
        E, pos, zz = rc[m, 0], rc[m, 1], rc[m, 2]
        A = axs[row, 0]
        s = 40 + 220 * (E / E.max() if E.max() > 0 else E)
        sc = A.scatter(zz, pos, s=s, c=E, cmap=technote_style.SEQ_CMAP,
                       edgecolor="k", lw=0.4, alpha=0.9)
        fig.colorbar(sc, ax=A, fraction=0.046, label="cluster energy [MeV]")
        A.set_xlabel("cluster $z$ (detector position) [mm]")
        A.set_ylabel("cluster transverse position [mm]")
        _headroom(A, 0.30)
        rs = rec_sc[ev]
        A.text(0.03, 0.97, f"reco recoil clusters: {m.sum()}\n"
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
            lab, col = _pdg_label(pdg[j])
            st = 40 + 220 * (Et[j] / Et.max() if Et.max() > 0 else 0)
            B.scatter(pz[j], pT[j], s=st, color=col, edgecolor="k", lw=0.4, alpha=0.9,
                      label=lab if lab not in seen else None)
            seen.add(lab)
        B.set_xlabel(r"$p_z$ (momentum) [MeV]")
        B.set_ylabel(r"$p_T$ (momentum) [MeV]")
        # reserve a top band, then put counts (upper-left) and species legend
        # (upper-right) inside it -- clear of the markers below
        B.margins(0.12)
        _headroom(B, 0.42)
        ts = tru_sc[ev]
        B.text(0.03, 0.97, f"truth FS hadrons: {mt.sum()}\n"
               f"$E_{{avail}}$={ts[2]:.2f}, $q_3$={ts[3]:.2f} GeV",
               transform=B.transAxes, va="top", ha="left", fontsize=9)
        B.legend(frameon=False, fontsize=8, loc="upper right", ncol=2,
                 columnspacing=0.8, handletextpad=0.3, borderaxespad=0.4)
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, "pet_event_displays.png"), dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"[disp] wrote pet_event_displays (events {list(map(int, picks))})")


def make_displays_energy_angle(z, pg, pr, ptru, prec, outdir, n_events=4, with_muon=False):
    """Alternative: both levels on ONE axis per event -- energy vs polar angle.
    Reco cluster angle is taken w.r.t. a nominal per-event vertex (see header).
    With --with-muon, the muon is added from the stored muon (pT,pz) scalars
    (truth_scalars/reco_scalars cols 0-1 = GetMuonPT[True]/GetMuonPz[True]) with a
    distinct marker -- the log-E vs angle view absorbs the GeV muon scale cleanly."""
    rec_sc, tru_sc = z["reco_scalars"], z["truth_scalars"]
    picks = _pick_events(z, pg, pr, ptru, prec, n_events)

    def _muon(sc_row):  # (pt,pz) GeV -> (theta_deg, E_MeV); E ~ |p| for a GeV muon
        pt, pz = float(sc_row[0]), float(sc_row[1])
        p = np.hypot(pt, pz)
        return np.degrees(np.arctan2(pt, pz)), np.sqrt(p * p + 0.10566 ** 2) * 1000.0
    ncol = 2
    nrow = int(np.ceil(n_events / ncol))
    fig, axs = plt.subplots(nrow, ncol, figsize=(6.0 * ncol, 4.4 * nrow))
    axs = np.atleast_1d(axs).ravel()
    for ax, ev in zip(axs, picks):
        rc = pr[ev]
        m = rc[:, 0] != 0
        Er, pos, zz = rc[m, 0], rc[m, 1], rc[m, 2]
        z0 = zz.min() - 100.0                                   # nominal vertex (upstream)
        th_r = np.degrees(np.arctan2(np.abs(pos), np.maximum(zz - z0, 1.0)))
        ax.scatter(th_r, Er, s=26, color="0.55", edgecolor="none", alpha=0.75,
                   label="reco clusters (nominal-vtx angle)")
        tc = pg[ev]
        mt = tc[:, 0] != 0
        Et, px, py, pz, pdg = (tc[mt, 0], tc[mt, 1], tc[mt, 2], tc[mt, 3], tc[mt, 4].astype(int))
        th_t = np.degrees(np.arctan2(np.hypot(px, py), pz))
        seen = set()
        for j in range(mt.sum()):
            lab, col = _pdg_label(pdg[j])
            ax.scatter(th_t[j], Et[j], s=180, color=col, edgecolor="k", lw=0.8, marker="*",
                       zorder=5, label=(f"truth {lab}" if lab not in seen else None))
            seen.add(lab)
        if with_muon:  # the muon: a real reconstructed track with a momentum vector
            th_mt, e_mt = _muon(tru_sc[ev])
            ax.scatter(th_mt, e_mt, s=360, marker=(6, 1, 0), color="#20232f",
                       edgecolor="gold", lw=1.3, zorder=6, label=r"$\mu$ (truth)")
            th_mr, e_mr = _muon(rec_sc[ev])
            ax.scatter(th_mr, e_mr, s=150, marker="X", color="#20232f",
                       edgecolor="w", lw=0.8, zorder=6, label=r"$\mu$ (reco)")
        rs = rec_sc[ev]
        ax.set_yscale("log")
        ax.set_xlabel(r"polar angle $\theta$ [deg]")
        ax.set_ylabel("energy [MeV]")
        _headroom(ax, 0.45, log=True)
        ax.text(0.03, 0.97, f"$E_{{avail}}$={rs[2]:.2f}, $q_3$={rs[3]:.2f} GeV\n"
                f"{m.sum()} clusters, {mt.sum()} hadrons",
                transform=ax.transAxes, va="top", ha="left", fontsize=9)
        ax.legend(frameon=False, fontsize=8, loc="upper right")
    for ax in axs[len(picks):]:
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, "pet_event_displays_energy_angle.png"),
                dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"[eang] wrote pet_event_displays_energy_angle (events {list(map(int, picks))})")


def _draw_cone(ax, direction, height, color, half_angle_deg=7.0, n=28, alpha=0.28):
    """Translucent cone with apex at the origin, axis along `direction`."""
    d = np.asarray(direction, float)
    nrm = np.linalg.norm(d)
    if nrm == 0 or height <= 0:
        return
    d = d / nrm
    a = np.array([1.0, 0, 0]) if abs(d[0]) < 0.9 else np.array([0, 1.0, 0])
    u = np.cross(d, a); u /= np.linalg.norm(u)
    v = np.cross(d, u)
    t = np.linspace(0, height, 2)
    phi = np.linspace(0, 2 * np.pi, n)
    T, PH = np.meshgrid(t, phi)
    r = T * np.tan(np.radians(half_angle_deg))
    X = T * d[0] + r * (np.cos(PH) * u[0] + np.sin(PH) * v[0])
    Y = T * d[1] + r * (np.cos(PH) * u[1] + np.sin(PH) * v[1])
    Z = T * d[2] + r * (np.cos(PH) * u[2] + np.sin(PH) * v[2])
    ax.plot_surface(X, Y, Z, color=color, alpha=alpha, linewidth=0, shade=True)


def make_displays_3d(z, pg, pr, ptru, prec, outdir, n_events=2):
    """Alternative: 3D-like display. Truth FS hadrons are cones opening from the
    (nominal) vertex along their momentum direction; reco clusters sit on the
    y=0 detector plane at their true relative positions. Axes: beam z, transverse
    x (=reco 'pos'/truth px), transverse y (truth py; reco has no 2nd transverse
    coord, so clusters lie on y=0)."""
    rec_sc = z["reco_scalars"]
    picks = _pick_events(z, pg, pr, ptru, prec, max(n_events, 2))[-n_events:]
    fig = plt.figure(figsize=(7.2 * n_events, 6.4))
    for i, ev in enumerate(picks):
        ax = fig.add_subplot(1, n_events, i + 1, projection="3d")
        rc = pr[ev]
        m = rc[:, 0] != 0
        Er, pos, zz = rc[m, 0], rc[m, 1], rc[m, 2]
        z0 = zz.min() - 100.0
        zr = zz - z0                                             # cluster beam-z rel. vertex
        rmax = max(np.sqrt(zr ** 2 + pos ** 2).max(), 1.0)
        # reco clusters on the y=0 plane
        s = 30 + 200 * (Er / Er.max() if Er.max() > 0 else Er)
        sc = ax.scatter(zr, pos, np.zeros_like(zr), s=s, c=Er, cmap=technote_style.SEQ_CMAP,
                        edgecolor="k", lw=0.3, depthshade=False)
        # truth hadron cones from the vertex (direction = momentum), length ~ energy
        tc = pg[ev]
        mt = tc[:, 0] != 0
        Et, px, py, pz, pdg = (tc[mt, 0], tc[mt, 1], tc[mt, 2], tc[mt, 3], tc[mt, 4].astype(int))
        Emax = Et.max() if Et.max() > 0 else 1.0
        seen = {}
        for j in range(mt.sum()):
            lab, col = _pdg_label(pdg[j])
            h = rmax * (0.35 + 0.65 * Et[j] / Emax)
            _draw_cone(ax, (pz[j], px[j], py[j]), h, col)
            seen.setdefault(lab, col)
        # proxy legend for species + clusters
        from matplotlib.lines import Line2D
        handles = [Line2D([0], [0], marker="^", ls="", color=c, mec="k", ms=9, label=f"truth {l}")
                   for l, c in seen.items()]
        handles.append(Line2D([0], [0], marker="o", ls="", color="0.5", mec="k", ms=7,
                              label="reco clusters (y=0 plane)"))
        rs = rec_sc[ev]
        ax.legend(handles=handles, frameon=False, fontsize=8, loc="upper left",
                  bbox_to_anchor=(0.0, 1.02))
        ax.set_xlabel("beam $z$ [mm]")
        ax.set_ylabel("transverse $x$ [mm]")
        ax.set_zlabel("transverse $y$ [mm]")
        ax.text2D(0.98, 0.02, f"$E_{{avail}}$={rs[2]:.2f}, $q_3$={rs[3]:.2f} GeV\n"
                  f"{m.sum()} clusters, {mt.sum()} hadrons",
                  transform=ax.transAxes, va="bottom", ha="right", fontsize=9)
        ax.view_init(elev=18, azim=-72)
    fig.colorbar(sc, ax=fig.axes, fraction=0.02, pad=0.02, label="cluster energy [MeV]")
    fig.savefig(os.path.join(outdir, "pet_event_displays_3d.png"), dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"[3d] wrote pet_event_displays_3d (events {list(map(int, picks))})")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--npz", default="of_inputs_pc_fullcloud.npz",
                    help="coverage-FIXED point-cloud inputs (NOT the pre-06-28 of_inputs_pc.npz)")
    ap.add_argument("--outdir", default="products/pet")
    ap.add_argument("--no-displays", action="store_true")
    ap.add_argument("--n-events", type=int, default=4,
                    help="rows in the canonical display (talk uses 2 for a 16:9 slide)")
    ap.add_argument("--no-cardinality", action="store_true")
    ap.add_argument("--no-retention", action="store_true")
    ap.add_argument("--energy-angle", action="store_true", help="also write the E-vs-angle display")
    ap.add_argument("--render-3d", action="store_true", help="also write the 3D cone/plane display")
    ap.add_argument("--with-muon", action="store_true",
                    help="add the muon (from stored muon pT/pz scalars) to the E-vs-angle display")
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
        make_displays(z, pg, pr, ptru, prec, args.outdir, n_events=args.n_events)
    if args.energy_angle:
        make_displays_energy_angle(z, pg, pr, ptru, prec, args.outdir, with_muon=args.with_muon)
    if args.render_3d:
        make_displays_3d(z, pg, pr, ptru, prec, args.outdir)
    print("[plot_event_displays] DONE")


if __name__ == "__main__":
    main()
