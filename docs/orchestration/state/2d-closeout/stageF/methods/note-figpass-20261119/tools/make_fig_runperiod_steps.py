#!/usr/bin/env python3
"""The run-period graphic (the readability read's addition, approved by Joseph; the director's request of 2026-11-18).

usage: python3 -I make_fig_runperiod_steps.py [--out DIR]

Two panels, each from one committed record held to its sha256 (the script refuses other bytes):
(a) reconstruction level: the 1G-1M and 1N-1P groups' ratios R_X/R_A to 1A-1F in p_par, with the data statistical
    uncertainty, and each group's step q(8-15 GeV/c)/q(1.5-8 GeV/c) - 1, from the 2D run-period record
    runperiod_values.json (L-row G4; the record sec_systematics.tex prints as rp-pb-reco and rp-pc-reco);
(b) each playlist's own p_par step t_X across 8 GeV/c against 1A-1F, from its five-observable unfold (the playlist
    left out of the reference when it is one of 1A-1F), with sigma_X, its class (FREE, PARTIAL, CARRIES) and half the
    recombined 1G/1L/1M step, t_bar/2, from the run-period diagnosis readout fd_rpd.json, R1 (FD-RPD-DECLARATION.md
    sec. 5; the record sec_fived16.tex's run-period subsection prints as rpd-r1-*).
The classes are recomputed from the record's t, sigma, h and sigma_h by the declaration's rule (FREE if |t| <= 2 sigma;
CARRIES if h >= 2 sigma_h; else PARTIAL) and must equal the record's. After drawing, the plotted numbers are read
back from the figure's artists and must equal the records' (identity check). Nothing is written if a check fails.
Outputs: runperiod_steps.pdf (no creation date), runperiod_steps.png (preview), runperiod_steps_values.json.

FIGURE PASS COPY (cov2d, 2026-11-19): this file is note-newfigs-20261118/make_fig_runperiod_steps.py with only the
explicit font sizes raised so no word prints under 7 pt at \textwidth (legends, panel labels and group names 7.6 pt;
they were 6.6 to 7.2), the repository root one level higher (it sits in tools/), and its default output in this
record's figs-src/. The originals are immutable MANIFEST rows. Every check is unchanged. Also panel (b)'s lower y limit is lower, for the larger panel label.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[7]
sys.path.insert(0, str(REPO))
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import note_print_style as nps  # noqa: E402

RECO = ("docs/orchestration/state/2d-closeout/stageF/methods/methods-short-20261109/lrows-g/g4-runperiod/"
        "runperiod_values.json", "f63074b1")      # make_values_fived16.py READOUTS["runper"]
RPD = ("docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-rpd/run/readout/fd_rpd.json",
       "c0b06cfd")                                # make_values_fived16.py READOUTS["rpd"]
PLAYLISTS = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"]
GROUPS = (("1A–1F", PLAYLISTS[0:6]), ("1G–1M", PLAYLISTS[6:9]), ("1N–1P", PLAYLISTS[9:12]))
# panel (a): the two groups; panel (b): the three classes. Greys and marker shapes only: these are not palette
# identities (note_palette.py names generators and products, not run periods or classes), and the data are this
# work's, drawn in black and greys so no colour reads as a generator.
GROUP_STYLE = {"PB": dict(color="black", marker="o", markerfacecolor="black", linestyle="None"),
               "PC": dict(color="0.45", marker="s", markerfacecolor="white", linestyle="None")}
CLASS_STYLE = {"CARRIES": dict(color="black", marker="D", markerfacecolor="black"),
               "PARTIAL": dict(color="0.35", marker="s", markerfacecolor="0.6"),
               "FREE": dict(color="0.45", marker="o", markerfacecolor="white")}


def load(rel, pin):
    p = REPO / rel
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    if not h.startswith(pin):
        raise SystemExit(f"REFUSE: {rel} has sha256 {h}, not the pinned {pin}")
    return json.loads(p.read_text()), h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE.parent / "figs-src")
    a = ap.parse_args()
    rp, h_reco = load(*RECO)
    rpd, h_rpd = load(*RPD)
    assert rp["schema"] == "lrows-g4-runperiod/1" and rpd["schema"] == "fd-rpd-readout/1"
    e = rp["pz_edges_GeV"]
    ctr = [math.sqrt(e[i] * e[i + 1]) for i in range(len(e) - 1)]
    pan = rp["panels"]
    for k, grp in (("PB", "1G–1M"), ("PC", "1N–1P")):
        assert pan[k]["group"] == grp and pan[k]["reference"] == "1A–1F"
        assert len(pan[k]["reco_ratio"]) == len(ctr) == len(pan[k]["reco_data_stat"])
    r1 = rpd["R1"]
    assert sorted(r1["classes"]) == sorted(PLAYLISTS) and r1["outcome"] == "OTHER"
    t = [100 * r1["t"][x] for x in PLAYLISTS]
    s = [100 * r1["sigma"][x] for x in PLAYLISTS]
    cls = [r1["classes"][x] for x in PLAYLISTS]
    rule = []
    for x in PLAYLISTS:
        if abs(r1["t"][x]) <= 2 * r1["sigma"][x]:
            rule.append("FREE")
        elif r1["h"][x] >= 2 * r1["sigma_h"][x]:
            rule.append("CARRIES")
        else:
            rule.append("PARTIAL")
    assert rule == cls, f"the declaration's rule gives {rule}, the record {cls}"
    for x in PLAYLISTS:   # h_X = t_X - t_bar/2, as the declaration defines it
        assert abs(r1["h"][x] - (r1["t"][x] - r1["tbar"] / 2)) < 1e-12
    half_tbar = 100 * r1["tbar"] / 2

    nps.apply()
    fig, (axa, axb) = plt.subplots(1, 2, figsize=nps.figsize(1.0, 0.42), gridspec_kw={"width_ratios": [1.1, 1.0]})
    # (a)
    axa.axhline(1.0, color="0.6", lw=0.6, zorder=0)
    axa.axvline(8.0, color="0.6", lw=0.6, ls="--", zorder=0)
    ebs = {}
    for k, dx in (("PB", 0.985), ("PC", 1.015)):
        q = pan[k]
        lab = f"{q['group']} / 1A–1F: step {q['reco_step_pct']:+.2f}%"
        ebs[k] = axa.errorbar([c * dx for c in ctr], q["reco_ratio"], yerr=q["reco_data_stat"], capsize=1.6,
                              elinewidth=0.8, markersize=3.2, label=lab, **GROUP_STYLE[k])
    axa.set_xscale("log")
    axa.set_xlim(1.4, 64)
    axa.set_xticks([2, 5, 10, 20, 50])
    axa.set_xticklabels(["2", "5", "10", "20", "50"])
    axa.set_xlabel(r"$p_\parallel$ (GeV/$c$)")
    axa.set_ylabel(r"reconstructed ratio to 1A–1F")
    axa.set_ylim(0.94, 1.13)
    axa.legend(loc="upper left", frameon=False, fontsize=7.6)
    axa.text(0.97, 0.04, "(a) reconstruction level", transform=axa.transAxes, ha="right", va="bottom", fontsize=7.6)
    # (b)
    xb = list(range(12))
    axb.axhline(0.0, color="0.6", lw=0.6, zorder=0)
    axb.axhline(half_tbar, color="0.3", lw=0.8, ls="--", zorder=0, label=r"half the 1G–1M group's step, $\bar t/2$")
    for g, (name, members) in enumerate(GROUPS):
        i0, i1 = PLAYLISTS.index(members[0]), PLAYLISTS.index(members[-1])
        if g % 2 == 1:
            axb.axvspan(i0 - 0.5, i1 + 0.5, color="0.93", lw=0, zorder=0)
        axb.text((i0 + i1) / 2, 0.985, name, transform=axb.get_xaxis_transform(), ha="center", va="top", fontsize=7.6)
    ebb = {}
    for c in ("FREE", "PARTIAL", "CARRIES"):
        idx = [i for i in xb if cls[i] == c]
        ebb[c] = axb.errorbar([xb[i] for i in idx], [t[i] for i in idx], yerr=[s[i] for i in idx], linestyle="None",
                              capsize=1.6, elinewidth=0.8, markersize=3.4, label=c, **CLASS_STYLE[c])
    axb.set_xticks(xb)
    axb.set_xticklabels(PLAYLISTS)
    axb.set_xlim(-0.6, 11.6)
    axb.set_xlabel("playlist")
    axb.set_ylabel(r"unfolded $p_\parallel$ step $t_X$ (%)")
    lo = min(ti - si for ti, si in zip(t, s))
    hi = max(ti + si for ti, si in zip(t, s))
    axb.set_ylim(lo - 3.4, hi + 7.5)   # figure pass: room under the data for the larger panel label
    axb.legend(loc="upper left", frameon=False, fontsize=7.6, bbox_to_anchor=(0.0, 0.92))
    axb.text(0.97, 0.04, "(b) each playlist, five-observable unfold", transform=axb.transAxes, ha="right", va="bottom", fontsize=7.6)
    fig.tight_layout(pad=0.3, w_pad=1.0)

    # identity checks: the figure's artists hold the records' numbers
    for k, dx in (("PB", 0.985), ("PC", 1.015)):
        line, _, bars = ebs[k].lines
        assert list(line.get_ydata()) == pan[k]["reco_ratio"]
        assert all(abs(xv - c * dx) < 1e-12 for xv, c in zip(line.get_xdata(), ctr))
        half = [(sg[1][1] - sg[0][1]) / 2 for sg in bars[0].get_segments()]
        assert all(abs(hv - sv) <= 1e-12 * sv for hv, sv in zip(half, pan[k]["reco_data_stat"]))
    got = {}
    for c, eb in ebb.items():
        line, _, bars = eb.lines
        half = [(sg[1][1] - sg[0][1]) / 2 for sg in bars[0].get_segments()]
        for xv, yv, hv in zip(line.get_xdata(), line.get_ydata(), half):
            got[int(xv)] = (c, yv, hv)
    assert sorted(got) == xb
    for i in xb:
        c, yv, hv = got[i]
        assert c == cls[i] and yv == t[i] and abs(hv - s[i]) <= 1e-12 * s[i]

    a.out.mkdir(parents=True, exist_ok=True)
    fig.savefig(a.out / "runperiod_steps.pdf", metadata={"CreationDate": None})
    fig.savefig(a.out / "runperiod_steps.png", dpi=200)
    vals = {
        "schema": "note-newfigs-runperiod-steps/1",
        "records": {"reco": {"path": RECO[0], "bytes_digest_sha256": h_reco}, "rpd": {"path": RPD[0], "bytes_digest_sha256": h_rpd}},
        "panel_a": {"pz_edges_GeV": e, "pz_centres_GeV": ctr,
                    "groups": {k: {"group": pan[k]["group"], "reference": pan[k]["reference"],
                                   "reco_ratio": pan[k]["reco_ratio"], "reco_data_stat": pan[k]["reco_data_stat"],
                                   "reco_step_pct": pan[k]["reco_step_pct"]} for k in ("PB", "PC")}},
        "panel_b": {"playlists": PLAYLISTS, "t_pct": t, "sigma_pct": s, "class": cls, "half_tbar_pct": half_tbar},
        "checks": {"records_sha256_pinned": True, "classes_equal_declaration_rule": True, "h_equals_t_minus_half_tbar": True,
                   "plotted_points_and_bars_equal_records": True},
    }
    (a.out / "runperiod_steps_values.json").write_text(json.dumps(vals, indent=1) + "\n")
    print("wrote", a.out / "runperiod_steps.pdf", "; records", h_reco[:8], h_rpd[:8])


if __name__ == "__main__":
    main()
