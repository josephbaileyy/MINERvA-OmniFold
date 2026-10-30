"""Writes the numeric tables of FD-CT-5B-REPORT.md from the committed readouts (no number is typed by hand).

    python3 -I -B make_5b_report_tables.py <fd directory>
"""
import json
import sys
from pathlib import Path

fd = Path(sys.argv[1])
r = json.load(open(fd / "readout/fd_ct_5b_periods.json"))
c = json.load(open(fd / "readout/fd_ct_5b_control.json"))
pc = json.load(open(fd / "readout/fd_ct_5b_precheck.json"))
cells = r["cells"]
o = []

o.append("**The control and the precheck:**\n")
o.append("| record | verdict | K1 inputs bitwise | K2 unfold bitwise (max rel. diff., fine cells) | K3 cells within τ | cells over |")
o.append("|---|---|---|---|---:|---|")
k3 = c["K3_within_tolerance_of_f"]
o.append(f"| control | {c['verdict']} | {c['K1_inputs_bitwise_mp1_zero']['pass']} (failed keys "
         f"{c['K1_inputs_bitwise_mp1_zero']['failed_keys']}, npz bytes equal {c['K1_inputs_bitwise_mp1_zero']['lat_npz_bytes_equal']}) | "
         f"{c['K2_unfold_bitwise_mp1_zero']['pass']} ({c['K2_unfold_bitwise_mp1_zero']['max_rel_diff_fine_cells']}) | "
         f"{sum(k3['within_by_cell'])} of {len(cells)} | {k3['cells_over']} |")
k3p = pc["K3_within_tolerance_of_f"]
o.append(f"| precheck | {pc['verdict']} | — | — | {sum(k3p['within_by_cell'])} of {len(cells)} | {k3p['cells_over']} |")

e = r["constants"]["exposure_share"]
o.append(f"\n**Constants:** exposure shares e_PA = {e['PA']:.4f}, e_PB = {e['PB']:.4f}, e_PC = {e['PC']:.4f}; "
         f"k = V2/(1 − V2) = {r['constants']['k']:.4f}; {r['constants']['n_boot']} bootstrap replicas per period, seeds "
         + ", ".join(f"{P} {s[0]}–{s[-1]}" for P, s in r["constants"]["bootstrap_seeds"].items()) + ".\n")

o.append("**Each comparison on R00–R15** (χ²_M in the metric of M = (C_total + C_resp)/(f fᵀ); the noise columns are the "
         "bootstrap reference; the contrast is across p_∥ = 4.5 GeV/c):\n")
o.append("| comparison | integral | χ²_M | noise E[χ²_M] | noise draws, min–max | above every draw | p_∥ contrast | its noise σ | z |")
o.append("|---|---:|---:|---:|---|---|---:|---:|---:|")
for name, x in r["comparisons"].items():
    n = x.get("noise") or {}
    if n:
        d = n["draw_chi2_M"]
        cols = [f"{n['expected_chi2_M']:.3f}", f"{min(d):.3f}–{max(d):.3f}", str(n["exceeds_every_draw"]),
                f"{100 * x['pz_contrast']:+.3f}%", f"{100 * n['pz_contrast_sigma']:.3f}%", f"{n['pz_contrast_z']:+.2f}"]
    else:
        cols = ["—", "—", "—", f"{100 * x['pz_contrast']:+.3f}%", "—", "—"]
    o.append(f"| `{name}` | {100 * x['integral_shift']:+.3f}% | {x['chi2_M']:.3f} | " + " | ".join(cols) + " |")

o.append("\n**Per cell, the double ratios minus 1, with their bootstrap-noise σ** (relative; σ_M is the reported matrix's):\n")
drs = ("dr_PB/PA", "dr_PC/PA", "dr_PC/PB")
o.append("| cell | " + " | ".join(f"{d} (σ_noise)" for d in drs) + " | σ_M |")
o.append("|---|" + "---:|" * (len(drs) + 1))
for i, cell in enumerate(cells):
    o.append(f"| {cell} | " + " | ".join(
        f"{100 * r['comparisons'][d]['shift'][i]:+.3f}% ({100 * r['comparisons'][d]['noise']['sigma_rel'][i]:.3f}%)"
        for d in drs) + f" | {100 * r['sigma_rel_M'][i]:.3f}% |")

C = r["C_PL5D"]
o.append(f"\n**C_PL,5D** (rank {C['rank']}; trace share {C['trace_share']:.4f} of M + C_PL,5D; σ median "
         f"{100 * C['sigma_rel_summary']['median']:.3f}%, range {100 * C['sigma_rel_summary']['min']:.3f}–"
         f"{100 * C['sigma_rel_summary']['max']:.3f}%; σ/σ_M median {C['sigma_ratio_to_M_summary']['median']:.4f}, "
         f"range {C['sigma_ratio_to_M_summary']['min']:.4f}–{C['sigma_ratio_to_M_summary']['max']:.4f}):\n")
o.append("| cell | σ, C_PL,5D | σ/σ_M | σ, noise floor | σ / noise floor |")
o.append("|---|---:|---:|---:|---:|")
for i, cell in enumerate(cells):
    o.append(f"| {cell} | {100 * C['sigma_rel'][i]:.3f}% | {C['sigma_ratio_to_M'][i]:.4f} | "
             f"{100 * C['noise_floor_sigma_rel'][i]:.3f}% | {C['sigma_ratio_to_noise_floor'][i]:.3f} |")

G = r["g_vs_5A"]["periods"]
o.append("\n**5B's period offsets g_X against 5A's projected ones** (Δ = g_5B − g_5A; the noise σ is g_5B's own):\n")
o.append("| period | \\|Δ\\|/σ median (min–max) | Δᵀ M⁻¹ Δ |")
o.append("|---|---|---:|")
for P, x in G.items():
    s = x["abs_difference_over_noise_summary"]
    o.append(f"| {P} | {s['median']:.3f} ({s['min']:.3f}–{s['max']:.3f}) | {x['difference_chi2_M']:.3f} |")
o.append("\n| cell | " + " | ".join(f"{P} g_5B / g_5A (\\|Δ\\|/σ)" for P in G) + " |")
o.append("|---|" + "---:|" * len(G))
for i, cell in enumerate(cells):
    o.append(f"| {cell} | " + " | ".join(
        f"{100 * x['g_5b'][i]:+.3f}% / {100 * x['g_5a'][i]:+.3f}% ({x['abs_difference_over_noise'][i]:.2f})"
        for x in G.values()) + " |")
print("\n".join(o))
print("\nLABELS::" + json.dumps(r["labels"]))
