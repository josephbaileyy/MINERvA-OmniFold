#!/usr/bin/env python3
"""Draw the vector-native PET event-representation schematic used as Fig. 17.

The detector layout is redrawn from the public MINERvA/Fermilab ``How it
works`` side elevation and the MINERvA detector paper (arXiv:1305.5199).  No
event data are used: this figure explains why a single scintillator cluster has
one view coordinate, how X/U/V association produces a 3D track, and how a
full-event PET upgrade could combine a distinguished muon feature with the
present variable-length recoil sets.

Outputs ``pet_event_representation_schematic.{pdf,png}`` in --outdir.
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle
import numpy as np


BLUE = "#3973B9"
RED = "#C94B46"
ORANGE = "#E28E3E"
GREEN = "#4E9A6A"
PURPLE = "#8064A2"
INK = "#20242B"
MUTED = "#68717D"
PALE = "#F5F7FA"


def arrow(ax, xy0, xy1, color=INK, lw=1.6, ms=13, zorder=5):
    ax.add_patch(FancyArrowPatch(xy0, xy1, arrowstyle="-|>", mutation_scale=ms,
                                lw=lw, color=color, zorder=zorder))


def detector_panel(ax):
    ax.set_xlim(-0.3, 10.8)
    ax.set_ylim(-0.55, 4.0)
    ax.axis("off")
    ax.text(-0.2, 3.80, "(a) Where the two event representations come from",
            fontsize=13, va="top", weight="bold")

    # Upstream elements and the central detector.  This is deliberately a clean
    # redraw rather than an embedded low-resolution web raster.
    ax.add_patch(Rectangle((0.05, 0.55), 0.20, 2.45, fc="#D79A8B", ec=INK, lw=0.8))
    ax.text(0.15, 1.78, "steel\nshield", rotation=90, ha="center", va="center", fontsize=7)
    ax.add_patch(Rectangle((0.45, 0.70), 0.20, 2.15, fc="#FFFFFF", ec=INK, lw=0.8))
    ax.text(0.55, 1.78, "veto", rotation=90, ha="center", va="center", fontsize=7)
    ax.add_patch(Circle((0.95, 1.78), 0.43, fc="#72A9A4", ec=INK, lw=0.9))
    ax.text(0.95, 1.78, "liquid\nHe", ha="center", va="center", fontsize=7)

    ax.add_patch(Rectangle((1.45, 0.48), 6.00, 2.62, fc="#EFF1F4", ec=INK, lw=1.0))
    ax.add_patch(Rectangle((1.45, 0.48), 6.00, 0.30, fc="#DCE3ED", ec=INK, lw=0.6))
    ax.add_patch(Rectangle((1.45, 2.80), 6.00, 0.30, fc="#DCE3ED", ec=INK, lw=0.6))
    ax.add_patch(Rectangle((1.65, 0.78), 0.82, 2.02, fc="#D8E8F2", ec=INK, lw=0.6))
    ax.add_patch(Rectangle((2.47, 0.78), 2.95, 2.02, fc="#FAFAF8", ec=INK, lw=0.6))
    ax.add_patch(Rectangle((5.42, 0.78), 0.88, 2.02, fc="#F7E9AE", ec=INK, lw=0.6))
    ax.add_patch(Rectangle((6.30, 0.78), 1.15, 2.02, fc="#DCE3ED", ec=INK, lw=0.6))
    ax.text(2.06, 1.79, "nuclear\ntargets", ha="center", va="center", fontsize=8)
    ax.text(3.94, 1.79, "active tracker", ha="center", va="center", fontsize=10,
            weight="bold")
    ax.text(5.86, 1.79, "ECAL", ha="center", va="center", fontsize=8, rotation=90)
    ax.text(6.88, 1.79, "HCAL", ha="center", va="center", fontsize=8, rotation=90)

    ax.add_patch(Rectangle((8.35, 0.35), 1.42, 3.05, fc="#F8F8F8", ec=INK, lw=1.0))
    ax.text(9.06, 1.88, "MINOS\nmuon spectrometer", rotation=90,
            ha="center", va="center", fontsize=9)

    arrow(ax, (-0.20, 1.78), (2.75, 1.78), color=PURPLE, lw=1.7)
    ax.text(1.05, 2.18, r"$\nu_\mu$ beam", color=PURPLE, fontsize=9)

    # A neutrino vertex, a long MINOS-matched muon, and short recoil activity.
    v = (3.70, 1.78)
    ax.scatter(*v, s=34, c=INK, zorder=7)
    ax.plot([v[0], 9.30], [v[1], 2.63], color=BLUE, lw=2.4, zorder=6)
    arrow(ax, (8.75, 2.55), (9.35, 2.64), color=BLUE, lw=2.2, ms=12)
    ax.plot([v[0], 4.50], [v[1], 1.20], color=RED, lw=2.1, zorder=6)
    for dx, dy, c in [(0.20, -0.10, ORANGE), (0.43, -0.29, RED),
                      (0.62, -0.43, ORANGE), (0.78, -0.56, RED)]:
        ax.scatter(v[0] + dx, v[1] + dy, s=42, c=c, ec="white", lw=0.5, zorder=7)

    ax.annotate("reconstructed muon track\n→ direction in MINERvA,\n"
                "momentum/charge from MINOS",
                xy=(7.60, 2.38), xytext=(5.75, 3.62), fontsize=8.5, color=BLUE,
                ha="center", va="top",
                arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.1))
    ax.annotate("hadronic recoil\n→ strip energy deposits",
                xy=(4.28, 1.35), xytext=(4.95, 0.10), fontsize=8.5, color=RED,
                ha="center", va="bottom",
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.1))
    ax.text(5.55, -0.42, "beam direction $z$", fontsize=8.5, color=MUTED)
    arrow(ax, (6.85, -0.30), (7.45, -0.30), color=MUTED, lw=1.0, ms=9)


def draw_plane(ax, center, theta_deg, label, color):
    """Draw one strip plane and highlight the one-dimensional cluster band."""
    cx, cy = center
    w, h = 0.25, 0.25
    box = Rectangle((cx - w / 2, cy - h / 2), w, h, fc="#FBFBFC", ec=INK, lw=0.8)
    ax.add_patch(box)
    th = np.deg2rad(theta_deg)
    d = np.array([np.cos(th), np.sin(th)])
    n = np.array([-np.sin(th), np.cos(th)])
    for off in np.linspace(-0.15, 0.15, 9):
        p = np.array([cx, cy]) + off * n
        line, = ax.plot([p[0] - 0.23*d[0], p[0] + 0.23*d[0]],
                        [p[1] - 0.23*d[1], p[1] + 0.23*d[1]],
                        color="#ADB5BF", lw=0.65, zorder=2)
        line.set_clip_path(box)
    # Highlight a strip band: the measured coordinate is normal to the strip;
    # position along the strip remains undetermined in this one plane.
    p = np.array([cx, cy]) + 0.025 * n
    hi, = ax.plot([p[0] - 0.23*d[0], p[0] + 0.23*d[0]],
                  [p[1] - 0.23*d[1], p[1] + 0.23*d[1]],
                  color=color, lw=5.0, alpha=0.72, solid_capstyle="butt", zorder=3)
    hi.set_clip_path(box)
    ax.text(cx, cy + 0.155, label, ha="center", va="bottom", fontsize=9, weight="bold")


def views_panel(ax):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.00, 0.98, "(b) Why one cluster has one transverse coordinate",
            fontsize=13, va="top", weight="bold")
    ax.text(0.01, 0.88, "A cluster is formed from adjacent hits in one scintillator plane.",
            fontsize=9, color=MUTED)

    draw_plane(ax, (0.16, 0.62), 90, "X view", BLUE)
    draw_plane(ax, (0.49, 0.62), 30, "U view", ORANGE)
    draw_plane(ax, (0.82, 0.62), -30, "V view", GREEN)
    ax.text(0.16, 0.42, r"measures $x$", ha="center", fontsize=8.5, color=BLUE)
    ax.text(0.49, 0.42, r"measures $u$", ha="center", fontsize=8.5, color=ORANGE)
    ax.text(0.82, 0.42, r"measures $v$", ha="center", fontsize=8.5, color=GREEN)

    ax.text(0.02, 0.31, r"one cluster: $E_{\rm dep}+z+$ one X/U/V projection",
            fontsize=9.5, weight="bold")
    arrow(ax, (0.41, 0.27), (0.59, 0.27), color=INK, lw=1.3, ms=10)
    ax.text(0.50, 0.235, "associate compatible activity\nacross planes and views",
            ha="center", va="top", fontsize=7.8, color=MUTED)

    # A compact matched-view glyph: the three constraints cross at a fitted
    # point/trajectory only after pattern recognition.
    cx, cy = 0.82, 0.22
    ax.add_patch(Circle((cx, cy), 0.11, fc="#FBFBFC", ec=INK, lw=0.8))
    for th, col in [(90, BLUE), (30, ORANGE), (-30, GREEN)]:
        d = np.array([np.cos(np.deg2rad(th)), np.sin(np.deg2rad(th))])
        ax.plot([cx - 0.10*d[0], cx + 0.10*d[0]],
                [cy - 0.10*d[1], cy + 0.10*d[1]], color=col, lw=3.0, alpha=0.72)
    ax.scatter(cx, cy, s=28, c=INK, zorder=6)
    ax.text(0.82, 0.075, "matched views\n→ 3D track", ha="center", fontsize=8.3)
    ax.text(0.02, 0.015, "Unmatched shower clusters stay view-specific:\n"
            "no particle direction or four-vector.", fontsize=7.9, color=RED,
            va="bottom")


def card(ax, xy, wh, title, edge):
    x, y = xy
    w, h = wh
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.018",
                       fc=PALE, ec=edge, lw=1.4)
    ax.add_patch(p)
    ax.text(x + 0.018, y + h - 0.045, title, fontsize=11, weight="bold", color=edge,
            va="top")
    return x, y, w, h


def representation_panel(ax):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.00, 0.98, "(c) Current recoil tensors and the proposed full-event upgrade",
            fontsize=13, va="top", weight="bold")

    xr, yr, wr, hr = card(ax, (0.02, 0.17), (0.38, 0.68), "Reconstructed event", BLUE)
    xt, yt, wt, ht = card(ax, (0.60, 0.17), (0.38, 0.68), "Truth event", RED)

    # Reco: the cloud is current; the dashed muon block is the proposed upgrade.
    ax.add_patch(FancyBboxPatch((xr + 0.032, yr + 0.425), 0.315, 0.145,
                                boxstyle="round,pad=0.008,rounding_size=0.012",
                                fc="white", ec=BLUE, lw=1.0, ls="--"))
    ax.scatter(xr + 0.055, yr + 0.50, s=150, marker="D", c=BLUE, ec=INK, lw=0.7)
    ax.text(xr + 0.095, yr + 0.53, r"proposed muon feature", fontsize=9.5, weight="bold")
    ax.text(xr + 0.095, yr + 0.46, r"$(p_T^\mu,p_\parallel^\mu)_{\rm reco}$",
            fontsize=10, color=BLUE)
    for i, (dx, dy, sz, col) in enumerate([
            (0.055, 0.27, 55, "#F1C84B"), (0.105, 0.23, 90, "#70A1D7"),
            (0.155, 0.29, 42, "#DB7B68"), (0.205, 0.22, 70, "#78B28B"),
            (0.255, 0.28, 48, "#9B82BF")]):
        ax.scatter(xr + dx, yr + dy, s=sz, c=col, ec=INK, lw=0.45)
    ax.text(xr + 0.055, yr + 0.35, "current PET: variable-length recoil set", fontsize=9.5,
            weight="bold")
    ax.text(xr + 0.055, yr + 0.095,
            r"cluster token: $[E_{\rm dep},\,\mathrm{pos}_{\rm view},\,z]$" "\n"
            r"$\mathrm{pos}_{\rm view}$ is one X/U/V projection",
            fontsize=8.8, color=INK)

    # PET box and directional arrows.
    ax.add_patch(FancyBboxPatch((0.455, 0.36), 0.09, 0.28,
                                boxstyle="round,pad=0.012,rounding_size=0.02",
                                fc="#FFF3CE", ec="#B98812", lw=1.5))
    ax.text(0.50, 0.50, "PET\nOmniFold", ha="center", va="center", fontsize=10,
            weight="bold", color="#725300")
    arrow(ax, (0.405, 0.50), (0.452, 0.50), color=INK, lw=1.5, ms=11)
    arrow(ax, (0.548, 0.50), (0.595, 0.50), color=INK, lw=1.5, ms=11)

    # Truth: likewise, the muon is available but is not in the current tensor.
    ax.add_patch(FancyBboxPatch((xt + 0.032, yt + 0.425), 0.315, 0.145,
                                boxstyle="round,pad=0.008,rounding_size=0.012",
                                fc="white", ec=BLUE, lw=1.0, ls="--"))
    ax.scatter(xt + 0.055, yt + 0.50, s=180, marker="*", c=BLUE, ec=INK, lw=0.7)
    ax.text(xt + 0.095, yt + 0.53, r"proposed muon feature", fontsize=9.5, weight="bold")
    ax.text(xt + 0.095, yt + 0.46, r"$(p_T^\mu,p_\parallel^\mu)_{\rm truth}$",
            fontsize=10, color=BLUE)
    truth_pts = [(0.055, 0.27, 95, BLUE, "o"), (0.115, 0.22, 70, ORANGE, "o"),
                 (0.175, 0.30, 80, GREEN, "o"), (0.235, 0.23, 55, RED, "o")]
    for dx, dy, sz, col, mk in truth_pts:
        ax.scatter(xt + dx, yt + dy, s=sz, c=col, marker=mk, ec=INK, lw=0.5)
    ax.text(xt + 0.055, yt + 0.35, "current PET: variable-length hadron set", fontsize=9.5,
            weight="bold")
    ax.text(xt + 0.055, yt + 0.095,
            r"hadron token: $[E,\,p_x,\,p_y,\,p_z]$" "\n"
            r"PDG is stored in the dump, but omitted by the loader",
            fontsize=8.8, color=INK)

    ax.text(0.50, 0.055,
            "Full-event upgrade = current recoil set + distinguished muon feature",
            ha="center", va="center", fontsize=11, color=INK, weight="bold")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outdir", default="products/pet")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    plt.rcParams.update({"font.size": 10, "axes.linewidth": 0.8,
                         "mathtext.fontset": "dejavusans"})
    fig = plt.figure(figsize=(13.2, 8.2), facecolor="white")
    detector_panel(fig.add_axes([0.035, 0.52, 0.57, 0.44]))
    views_panel(fig.add_axes([0.625, 0.52, 0.345, 0.44]))
    representation_panel(fig.add_axes([0.045, 0.03, 0.91, 0.45]))

    stem = os.path.join(args.outdir, "pet_event_representation_schematic")
    fig.savefig(stem + ".pdf", bbox_inches="tight")
    fig.savefig(stem + ".png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {stem}.{{pdf,png}}")


if __name__ == "__main__":
    main()
