#!/usr/bin/env python3
"""The sixteen-cell generator residuals: per cell, (g_i - f_i)/f_i for each prediction of the note's main comparison
table (tab:fived16-gen), with grey bars at +-sqrt(C_rep,ii)/f_i (Joseph's request for the journal-voice rewrite's
generator comparison, relayed by the director on 2026-11-20).

usage: python3 -I make_fig_fived16_genresidual.py [--out DIR]

Inputs, each held to the sha256 prefix that make_values_fived16.py READOUTS pins for the reported arm (the script
refuses any other bytes):
  dp    fd/with-cpl/data-product/fd_data_product_cpl.json                     f and C_rep = C_total + C_resp + C_PL,5D
  g     fd/gencmp-e/rerun1/chain/chdefs/with/readout/fd_g_readout.json       GENIE CV, GENIE + MEC, MINERvA Tune v1
  gdefs fd/gencmp/readout/defs.json                                           NuWro and GiBUU on carbon, analysis
                                                                              definitions (GiBUU on its 8 cells)
These are the predictions and arm of tab:fived16-gen: make_values_fived16.py takes that table's GENIE and Tune rows
from "g" and its NuWro and GiBUU (carbon) rows from gdefs' carbon analysis definitions, against the reported matrix.
Checks before drawing (any failure writes nothing):
  - every readout's f equals the data product's f, cell by cell, and its cells are R00-R15 (GiBUU: its 8 cells);
  - the record's relative sigma of C_rep equals sqrt(diag)/f;
  - each readout's own g/f - 1 equals (g - f)/f computed here;
  - against the note's printed values (docs/analysis-note/values_fived16.tex, regenerated and --checked by the build):
    the GENIE CV, GENIE + MEC and Tune per-cell (g - f)/f of tab:fived16-pulls (g-<p>-gf-R<nn>, one decimal, %), and
    the NuWro and GiBUU carbon total chi2 of tab:fived16-gen (g-<p>-carbon-total-chi2) from the same gdefs records;
  - GiBUU's cells are exactly those below p_par = h2-mid-pz.
After drawing, the plotted marker heights and bar half-heights are read back from the figure's artists and asserted
equal to the computed values (identity check). Outputs (to --out, default ../figs-src, not committed):
fived16_genresidual.pdf (no creation date, so reruns are byte-identical), .png (preview), and
fived16_genresidual_values.json (every plotted number, the inputs' paths and sha256, the checks).
Descriptive only: the bars are the reported covariance's diagonal; the chi2 of tab:fived16-gen also includes V_g and the
correlations, which no bar shows.
V_F COPY (note-vffigs-20261126, 2026-11-26): note-genresid-20261120's producer with only its inputs changed to the
C_e^infl (V_F) records (V_F option C, readings #1368), each at the pin make_values_fived16.py READOUTS gives it in #1378:
INPUTS (dp: the V_F data product; g: the V_F with-arm Stage G readout; gdefs: the V_F gdefs recompute), COV_KEY (the
reported matrix C_total + C_resp + C_PL,5D + DeltaC_e), and the labels the records must carry (the data product's schema,
the readouts' reported-covariance and chi2-matrix names). It checks against the note's own values_fived16.tex, as the
original does; this branch is cut from #1378's head, whose file prints the V_F values. The drawing, every other check
and every output are unchanged.
"""
import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[7]
sys.path.insert(0, str(REPO))
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402
import note_palette as pal  # noqa: E402
import note_print_style as nps  # noqa: E402

FD = "docs/orchestration/state/measurement-paper/5d-community-20261024"
INPUTS = {
    "dp": (f"{FD}/fd/with-vf/data-product/fd_data_product_vf.json", "1a37b082"),
    "g": (f"{FD}/fd/with-vf/readout/vf-with-E/fd_g_readout.json", "7034a08e"),
    "gdefs": (f"{FD}/fd/with-vf/p2/gdefs.vf.json", "6c202b08b5d9ed0b"),
}
VALUES = "docs/analysis-note/values_fived16.tex"
COV_KEY = "C_total_plus_C_resp_plus_C_PL5D_plus_DeltaC_e"
# (readout name, values key, palette identity, marker, source)
SERIES = (
    ("genie_cv", "gcv", "genie_cv", "v", "g"),
    ("genie_mec", "gmec", "genie_mec", "P", "g"),
    ("nuwro", "nuwro", "nuwro", "^", "gdefs"),
    ("gibuu", "gibuu", "gibuu", "D", "gdefs"),
    ("mnvtune_v1", "tune", "tune_v1", "s", "g"),
)
CELLS = [f"R{i:02d}" for i in range(16)]


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def tex_values(path):
    """The \\fvval keys of values_fived16.tex as strings, TeX spaces (~) as spaces."""
    v = {}
    for m in re.finditer(r"\\@namedef\{fv@([^}]+)\}\{([^}]*)\}", path.read_text(encoding="utf-8")):
        v[m.group(1)] = m.group(2).replace("~", " ")
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE.parent / "figs-src")
    a = ap.parse_args()
    d, digests = {}, {}
    for k, (rel, pin) in INPUTS.items():
        p = REPO / rel
        digests[k] = sha256(p)
        if not digests[k].startswith(pin):
            raise SystemExit(f"REFUSE: {rel} has sha256 {digests[k]}, not the pinned {pin}")
        d[k] = json.loads(p.read_text())
    vtex = REPO / VALUES
    vdigest = sha256(vtex)
    tv = tex_values(vtex)

    dp = d["dp"]
    assert dp["schema"] == "fd-data-product-vf/1"
    assert [c["cell"] for c in dp["cells"]] == CELLS
    f = dp["f"]
    C = dp["matrices"][COV_KEY]
    rel_sig = [math.sqrt(C[i][i]) / f[i] for i in range(16)]
    assert all(abs(rel_sig[i] - dp["relative_sigma"][COV_KEY][i]) < 1e-12 for i in range(16)), "relative sigma"
    assert d["g"]["schema"] == "fd-g-readout/2" and d["gdefs"]["schema"] == "fd-gencmp-defs/1"
    gpred = {p["name"]: p for p in d["g"]["predictions"]}
    assert all(p["reported_covariance"] == "C_total + C_resp + C_PL5D + DeltaC_e" for p in gpred.values())
    mid_pz = float(tv["h2-mid-pz"])
    low = [c["cell"] for c in dp["cells"] if c["box"]["pz"][1] <= mid_pz]
    assert len(low) == 8, low

    series = []
    for name, key, ident, marker, src in SERIES:
        if src == "g":
            rec = gpred[name]
            g, cells, own = rec["g"], rec["cells"], rec["g_over_f_minus_1"]
            fr = rec["f"]
        else:
            ad = d["gdefs"]["generators"][name]["carbon"]["analysis_definitions"]
            rec = ad["chi2"]["reported"]
            g, cells, own, fr = rec["g"], rec["cells"], rec["g_over_f_minus_1"], rec["f"]
            assert g == ad["g"], f"{name}: the carbon chi2 record's g is not the analysis-definition g"
            printed = tv[f"g-{key}-carbon-total-chi2"]
            assert f"{rec['total']['chi2']:.2f}" == printed, f"{name}: chi2 {rec['total']['chi2']} vs printed {printed}"
            assert rec["total"]["matrix"] == "C_total + C_resp + C_PL5D + DeltaC_e + V_g"
        assert cells == (low if name == "gibuu" else CELLS), f"{name}: cells {cells}"
        idx = [CELLS.index(c) for c in cells]
        assert all(fr[j] == f[i] for j, i in enumerate(idx)), f"{name}: f differs from the data product's"
        r = [(g[j] - f[i]) / f[i] for j, i in enumerate(idx)]
        assert all(abs(r[j] - own[j]) < 1e-12 for j in range(len(idx))), f"{name}: the readout's own g/f - 1 differs"
        if src == "g":
            for j, i in enumerate(idx):
                pk = f"g-{key}-gf-{CELLS[i]}"
                assert f"{100 * r[j]:.1f}" == tv[pk], f"{pk}: {100 * r[j]:.3f} vs printed {tv[pk]}"
        lab = tv[f"gs-label-{key}"] + (" (carbon)" if name in ("nuwro", "gibuu") else "")
        series.append({"name": name, "label": lab, "ident": ident, "marker": marker, "idx": idx,
                       "residual_pct": [100 * x for x in r], "source": src})

    # ---- draw
    nps.apply()
    fig, ax = plt.subplots(figsize=nps.figsize(1.0, 0.46))
    x = list(range(16))
    half_w = 0.42
    bars = []
    for i in x:
        s = 100 * rel_sig[i]
        rect = Rectangle((i - half_w, -s), 2 * half_w, 2 * s, facecolor="0.86", edgecolor="none", zorder=1)
        ax.add_patch(rect)
        bars.append(rect)
    ax.axhline(0, color="0.25", lw=0.7, zorder=2)
    offs = [-0.28, -0.14, 0.0, 0.14, 0.28]
    arts = []
    for s, dx in zip(series, offs):
        xs = [i + dx for i in s["idx"]]
        kw = pal.style(s["ident"], linestyle="None")
        kw["marker"] = s["marker"]
        kw["markerfacecolor"] = kw["markeredgecolor"] = kw["color"]
        (ln,) = ax.plot(xs, s["residual_pct"], markersize=3.8, zorder=3, label=s["label"], **kw)
        arts.append(ln)
    for q in (1, 2, 3):
        ax.axvline(4 * q - 0.5, color="0.35", lw=0.7, ls=(0, (1.5, 1.5)), zorder=2)
    for q in range(4):
        box = dp["cells"][4 * q]["box"]
        assert all(dp["cells"][4 * q + k]["box"]["pt"] == box["pt"] and dp["cells"][4 * q + k]["box"]["pz"] == box["pz"]
                   for k in range(4)), f"quadrant {q}"
        (pt0, pt1), (pz0, pz1) = box["pt"], box["pz"]
        ax.text(4 * q + 1.5, 0.975, rf"$p_T$ {pt0:g}–{pt1:g}, $p_\parallel$ {pz0:g}–{pz1:g}" + "\n(GeV/$c$)",
                transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=7.4)
    lo = min(min(s["residual_pct"]) for s in series)
    hi = max(max(s["residual_pct"]) for s in series)
    smax = max(100 * v for v in rel_sig)
    ax.set_ylim(min(lo, -smax) - 6, max(hi, smax) + 22)
    ax.set_xlim(-0.6, 15.6)
    ax.set_xticks(x)
    ax.set_xticklabels(CELLS, fontsize=7.6)
    ax.tick_params(axis="x", length=0, pad=2)
    ax.set_xlabel("Reporting cell")
    ax.set_ylabel(r"$(g_i - f_i)/f_i$ (%)")
    handles = arts + [Patch(facecolor="0.86", edgecolor="none", label=r"Reported uncertainty, $\pm\sqrt{C_{ii}}/f_i$")]
    ax.legend(handles=handles, ncol=3, fontsize=7.2, loc="lower center", bbox_to_anchor=(0.5, 1.0), frameon=False,
              handletextpad=0.3, columnspacing=1.0, borderaxespad=0.2)
    fig.tight_layout(pad=0.3)

    # ---- identity check: the figure holds the computed numbers
    for s, ln, dx in zip(series, arts, offs):
        assert list(ln.get_ydata()) == s["residual_pct"], f"{s['name']}: plotted heights differ"
        assert list(ln.get_xdata()) == [i + dx for i in s["idx"]], f"{s['name']}: plotted cells differ"
    for i, rect in enumerate(bars):
        h = 100 * rel_sig[i]
        assert abs(rect.get_y() + h) <= 1e-12 * h and abs(rect.get_height() - 2 * h) <= 1e-12 * h, f"bar {i}"
    assert all(t.get_fontsize() >= 7.0 for t in fig.findobj(matplotlib.text.Text) if t.get_text()), "a font under 7 pt"

    a.out.mkdir(parents=True, exist_ok=True)
    fig.savefig(a.out / "fived16_genresidual.pdf", metadata={"CreationDate": None})
    fig.savefig(a.out / "fived16_genresidual.png", dpi=200)
    vals = {
        "schema": "note-genresid-fived16/1",
        "inputs": {k: {"path": INPUTS[k][0], "bytes_digest_sha256": digests[k]} for k in INPUTS},
        "printed_values_file": {"path": VALUES, "bytes_digest_sha256": vdigest},
        "covariance": COV_KEY,
        "quantity": "(g_i - f_i)/f_i in percent; bar half-height 100 sqrt(C_rep,ii)/f_i",
        "relative_sigma_reported_pct": dict(zip(CELLS, [100 * v for v in rel_sig])),
        "series": [{"name": s["name"], "label": s["label"], "source": INPUTS[s["source"]][0],
                    "residual_pct": dict(zip([CELLS[i] for i in s["idx"]], s["residual_pct"]))} for s in series],
        "checks": {"inputs_sha256_pinned": True, "f_equal_across_readouts": True, "relative_sigma_equals_record": True,
                   "readout_g_over_f_minus_1_equal": True, "printed_gf_equal_gcv_gmec_tune": True,
                   "printed_carbon_chi2_equal_nuwro_gibuu": True, "gibuu_cells_below_mid_pz": True,
                   "plotted_heights_equal": True, "plotted_bars_equal": True, "fonts_at_least_7pt": True},
    }
    (a.out / "fived16_genresidual_values.json").write_text(json.dumps(vals, indent=1) + "\n")
    print("wrote", a.out / "fived16_genresidual.pdf", "; inputs", {k: v[:8] for k, v in digests.items()})


if __name__ == "__main__":
    main()
