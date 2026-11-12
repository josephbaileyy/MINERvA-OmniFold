#!/usr/bin/env python3
"""L-row G4 (referee6 major 8): the run-period inconsistency before and after unfolding, drawn from committed
products only; never runs an unfold. 0 node-h (the director, 2026-11-12).

    python3 -I make_runperiod_figure.py      (run from any directory)

Writes, beside this script: runperiod.pdf, runperiod.png and runperiod_values.json (every plotted number and every
check). The inputs are pinned by sha256 in inputs.json, and any other digest refuses.

What is drawn: two panels, period group P_B = 1G-1M and P_C = 1N-1P, each against ONE reference, P_A = 1A-1F (the
per-period unfolding's own groups, periods.py:9-12 of period-unfold-20261014), as a function of p_parallel on the
16-bin analysis grid, summed over p_T:
- reconstructed: R_X = (D_X - B_X) / S_X, every playlist's simulated signal S and background B scaled to its own
  data POT before summing (the playlist-spread proxy, ref_shape.py; per-playlist yields from proxy_hists.py's
  work_proxy.npz, POTs from proxy_hists_meta.json), plotted as R_X / R_A, with the data statistical uncertainty;
- unfolded: the per-period unfolding's double ratio (data over each period's own simulated truth) of the integrated
  p_parallel yields, analysis.json [comparisons/dr_X/PA/marginal_ratio_minus_1/pz], for RE-2's refined background,
  the reported two-dimensional configuration, with the bootstrap noise sigma of the p_parallel marginal
  [comparisons/dr_X/PA/noise/sigma_pz_marginal_pct] (ten paired draws; the noise of the cell-projected marginal,
  used as the band of this ratio).
The step printed in each panel is q(8-15 GeV/c) / q(1.5-8 GeV/c) - 1 of the integrated yields, the definition the
paper uses (analyze_periods.py:152-168; ref_shape's 6.10 %).

Checks (each an assert; the script writes nothing if one fails):
- the reconstructed code reproduces the committed reconstruction-level reference, 1G-1M against 1A-1E on the proxy
  grid: ref_shape.json [1G-1M_vs_1A-1E/by_pz] to its printed 5 decimals, and the step 6.10 % to 0.01;
- the reconstructed 1G-1M / 1A-1E ratio on the analysis grid gives the same step as on the proxy grid (to 1e-9; the
  two grids share the step's edges 1.5, 8 and 15 GeV/c);
- the unfolded steps read here are the committed RE-2 regeneration's (values_table.tsv:162: 0.06888084964241115)
  and the purity run's (0.06942682814976497);
- every unfolded marginal has 16 bins, the analysis grid of work_proxy.npz.
The changed reference is stated in runperiod_values.json: the committed reconstruction-level number the paper
quotes (+6.10 %) is against 1A-1E; this figure uses 1A-1F for both levels, so its reconstructed step differs."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[8]
PINS = json.loads((HERE / "inputs.json").read_text())
PERIODS = {"PA": ["1A", "1B", "1C", "1D", "1E", "1F"], "PB": ["1G", "1L", "1M"], "PC": ["1N", "1O", "1P"]}
LABEL = {"PA": "1A–1F", "PB": "1G–1M", "PC": "1N–1P"}
REF_1AE = ["1A", "1B", "1C", "1D", "1E"]
STEP_LO, STEP_HI = (1.5, 8.0), (8.0, 15.0)
PZ_ANA = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0]
STEP_REFINED, STEP_PURITY = 0.06888084964241115, 0.06942682814976497


def load(key: str, override: Path | None = None) -> bytes:
    p = override if override is not None else ROOT / PINS[key]["path"]
    b = p.read_bytes()
    got = hashlib.sha256(b).hexdigest()
    assert got == PINS[key]["digest"], f"{key}: sha256 {got} is not the pinned {PINS[key]['digest']}"
    return b


def reco(z, meta, grid):
    k = {p: meta[p]["pot_data"] / meta[p]["pot_mc"] for p in meta}

    def ys(group):
        D = sum(z[f"{p}__{grid}__D"] for p in group).sum(0)
        S = sum(k[p] * z[f"{p}__{grid}__S"] for p in group).sum(0)
        B = sum(k[p] * z[f"{p}__{grid}__B"] for p in group).sum(0)
        return D, S, B

    edges = np.asarray(z[f"edges__{grid}__pz"], float)

    def ratio(num, den):
        Dn, Sn, Bn = ys(num)
        Dd, Sd, Bd = ys(den)
        a, b = (Dn - Bn) / Sn, (Dd - Bd) / Sd
        q = a / b
        eq = q * np.sqrt((np.sqrt(Dn) / Sn / a) ** 2 + (np.sqrt(Dd) / Sd / b) ** 2)
        lo = (edges[:-1] >= STEP_LO[0]) & (edges[1:] <= STEP_LO[1])
        hi = (edges[:-1] >= STEP_HI[0]) & (edges[1:] <= STEP_HI[1])
        qr = lambda s: ((Dn[s].sum() - Bn[s].sum()) / Sn[s].sum()) / ((Dd[s].sum() - Bd[s].sum()) / Sd[s].sum())  # noqa: E731
        return q, eq, qr(hi) / qr(lo) - 1.0

    return edges, ratio


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work-proxy", type=Path, default=None,
                    help="work_proxy.npz, if not at its pinned path (inputs/, a copy of #977's receipt member)")
    a = ap.parse_args(argv)
    import io
    z = np.load(io.BytesIO(load("work_proxy", a.work_proxy)), allow_pickle=False)
    meta = json.loads(load("proxy_meta"))
    ref = json.loads(load("reco_reference"))
    unf = {"refined": json.loads(load("unfolded_refined")), "purity": json.loads(load("unfolded_purity"))}

    # the reconstructed code against the committed reference (1G-1M vs 1A-1E, proxy grid)
    _, rp = reco(z, meta, "proxy")
    q, _, st = rp(PERIODS["PB"], REF_1AE)
    want = np.array(ref["1G-1M_vs_1A-1E"]["by_pz"])
    assert np.max(np.abs(np.round(q, 5) - want)) == 0.0, "the reconstructed ratio does not reproduce ref_shape.json"
    assert abs(100 * st - 6.10) < 0.01, f"the reconstructed step {100 * st:.3f} % is not the committed 6.10 %"
    edges, ra = reco(z, meta, "ana")
    assert edges.tolist() == PZ_ANA, "work_proxy's analysis p_parallel grid is not the 16-bin grid"
    _, _, st_ana = ra(PERIODS["PB"], REF_1AE)
    assert abs(st_ana - st) < 1e-9, "the two grids disagree on the step"
    # the unfolded values
    for name, want_step in (("refined", STEP_REFINED), ("purity", STEP_PURITY)):
        assert unf[name]["comparisons"]["dr_PB/PA"]["step"]["value"] == want_step, f"{name}: dr_PB/PA step"
        for X in ("PB", "PC"):
            m = unf[name]["comparisons"][f"dr_{X}/PA"]
            assert len(m["marginal_ratio_minus_1"]["pz"]) == 16 and len(m["noise"]["sigma_pz_marginal_pct"]) == 16

    out = {"schema": "lrows-g4-runperiod/1", "pz_edges_GeV": PZ_ANA, "reference": "PA = 1A-1F, at both levels",
           "changed_reference_note": "the paper's reconstruction-level step (+6.10 %) is 1G-1M against 1A-1E "
                                     "(ref_shape.json); here both levels use 1A-1F, the unfolding's reference",
           "checks": {"reco_reproduces_ref_shape_by_pz": True, "reco_step_1G1M_vs_1A1E_pct": 100 * st,
                      "unfolded_steps_are_committed": True},
           "inputs": PINS, "panels": {}}
    plt.rcParams.update({"font.family": "serif", "mathtext.fontset": "cm", "font.size": 8.5,
                         "axes.linewidth": .6, "pdf.fonttype": 42})
    fig, axes = plt.subplots(1, 2, figsize=(508 / 72, 3.2), sharey=True, layout="constrained")
    ctr = np.sqrt(np.array(PZ_ANA[:-1]) * np.array(PZ_ANA[1:]))
    lo_e, hi_e = ctr - np.array(PZ_ANA[:-1]), np.array(PZ_ANA[1:]) - ctr
    for ax, X in zip(axes, ("PB", "PC")):
        qr, eqr, sr = ra(PERIODS[X], PERIODS["PA"])
        m = unf["refined"]["comparisons"][f"dr_{X}/PA"]
        qu = 1 + np.array(m["marginal_ratio_minus_1"]["pz"])
        eu = np.array(m["noise"]["sigma_pz_marginal_pct"]) / 100
        su, nu = m["step"]["value"], m["step"]["noise_sigma"]
        pu = unf["purity"]["comparisons"][f"dr_{X}/PA"]["step"]
        ax.axhline(1, color="0.6", lw=.6)
        ax.axvline(8, color="0.6", lw=.6, ls=":")
        ax.errorbar(ctr * 0.97, qr, xerr=[lo_e * 0.97, hi_e * 0.97], yerr=eqr, fmt="o", ms=3, lw=.8, color="#1f4e8c",
                    label="reconstructed: (data − bkg) / signal simulation")
        ax.errorbar(ctr * 1.03, qu, yerr=eu, fmt="s", ms=3, lw=.8, color="#b2182b", mfc="white",
                    label="unfolded: data / simulated truth")
        ax.set_xscale("log")
        ax.set_xlim(1.4, 64)
        ax.set_xticks([2, 3, 5, 8, 15, 30, 60])
        ax.set_xticklabels(["2", "3", "5", "8", "15", "30", "60"])
        ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        ax.set_xlabel(r"$p_\parallel$ (GeV/$c$)")
        ax.set_title(f"{LABEL[X]} relative to {LABEL['PA']}", fontsize=8.6)
        ax.text(0.97, 0.05, f"step at 8 GeV/$c$\nreconstructed {100 * sr:+.2f} %\nunfolded {100 * su:+.2f} ± {100 * nu:.2f} %",
                transform=ax.transAxes, fontsize=7.6, ha="right", va="bottom")
        out["panels"][X] = {"group": LABEL[X], "reference": LABEL["PA"],
                            "reco_ratio": qr.tolist(), "reco_data_stat": eqr.tolist(), "reco_step_pct": 100 * sr,
                            "unfolded_ratio": qu.tolist(), "unfolded_noise_sigma": eu.tolist(),
                            "unfolded_step_pct": 100 * su, "unfolded_step_noise_pct": 100 * nu,
                            "unfolded_purity_step_pct": 100 * pu["value"], "unfolded_purity_step_noise_pct": 100 * pu["noise_sigma"]}
    axes[0].set_ylabel("double ratio")
    h, lab = axes[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="outside lower center", ncol=2, fontsize=7.8, frameon=False)
    fig.savefig(HERE / "runperiod.pdf", metadata={"CreationDate": None, "ModDate": None})
    fig.savefig(HERE / "runperiod.png", dpi=180)
    (HERE / "runperiod_values.json").write_text(json.dumps(out, indent=1) + "\n")
    for X, v in out["panels"].items():
        print(f"{v['group']} / {v['reference']}: reco step {v['reco_step_pct']:+.3f} %, unfolded {v['unfolded_step_pct']:+.3f} "
              f"± {v['unfolded_step_noise_pct']:.3f} % (purity {v['unfolded_purity_step_pct']:+.3f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
