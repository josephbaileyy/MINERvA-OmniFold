"""Writes the numeric tables of FD-CT-3B-REPORT.md from the committed readout (no number is typed by hand)."""
import json, sys
from pathlib import Path
r = json.load(open(Path(sys.argv[1]) / "readout/fd_ct_mismatch.json"))
o = []
f = r["closure_floor_summary_abs"]
o.append(f"**The closure floor** b_zero (zero-on-zero bias against the truth), |b_zero| median {f['median']:.3e}, "
         f"range {f['min']:.3e}–{f['max']:.3e}.\n")
o.append("**Each shifted closure, Δ = b − b_zero:**\n")
o.append("| variant | \\|Δ\\|/σ median (min–max) | Δᵀ M⁻¹ Δ |")
o.append("|---|---|---:|")
for v, x in r["variants"].items():
    s = x["abs_delta_over_sigma_total_resp_summary"]
    o.append(f"| `{v}` | {s['median']:.4f} ({s['min']:.4f}–{s['max']:.4f}) | {x['quadratic_form_total_resp']:.4f} |")
o.append("\n**Per species and W2b: the closure half-span h beside −d** (d the data half-span):\n")
o.append("| species | cos(h, −d) | ‖h‖/‖d‖ | hᵀ M⁻¹ h | residual (h + d)ᵀ M⁻¹ (h + d) | max \\|h + d\\|/σ |")
o.append("|---|---:|---:|---:|---:|---:|")
rows = list(r["species"].items()) + [("w2b ±4 %", r["w2b_recoil_4pct"])]
for sname, x in rows:
    o.append(f"| {sname} | {x['cosine_closure_vs_minus_data']:.4f} | {x['norm_ratio_closure_over_data']:.4f} | "
             f"{x['closure_half_span_quadratic_form']:.4f} | {x['residual_quadratic_form']:.4f} | "
             f"{max(x['residual_over_sigma_total_resp']):.4f} |")
o.append("\n**Per cell, h and −d by species** (relative values; h relative to the closures' truth, d to f, W2b's d to its "
         "own δ = 0 chain):\n")
names = [s for s, _ in rows]
o.append("| cell | " + " | ".join(f"{n} h / −d" for n in names) + " |")
o.append("|---|" + "---|" * len(names))
for i, c in enumerate(r["cells"]):
    o.append(f"| {c} | " + " | ".join(f"{x['closure_half_span'][i]:+.4f} / {-x['data_half_span'][i]:+.4f}" for _, x in rows) + " |")
a = r["closure_analogue_of_C_resp"]
o.append("\n**The closure analogue of C_resp** (Σ over the four primary species of h hᵀ; beside C_resp, not a component):\n")
o.append("| cell | σ, closure analogue | σ/f, C_resp | ratio |")
o.append("|---|---:|---:|---:|")
for i, c in enumerate(r["cells"]):
    o.append(f"| {c} | {a['sigma_rel'][i]:.5f} | {r['sigma_rel']['C_resp'][i]:.5f} | {a['ratio_to_sigma_C_resp'][i]:.4f} |")
print("\n".join(o))
print("\nLABELS::" + json.dumps(r["labels"]))
