"""Writes the numeric tables of FD-CT-READERS-REPORT.md from the committed readouts (no number is typed by hand)."""
import json, sys
from pathlib import Path
fd = Path(sys.argv[1])
r = json.load(open(fd / "readout/fd_ct_recoil.json"))
out = []
out.append("| cell | s₋ | s₊ | d | σ/f C_resp | σ/f C_total + C_resp | \\|d\\|/σ C_resp | \\|d\\|/σ C_total + C_resp |")
out.append("|---|---:|---:|---:|---:|---:|---:|---:|")
for i, c in enumerate(r["cells"]):
    out.append(f"| {c} | {r['shift_minus'][i]:+.4f} | {r['shift_plus'][i]:+.4f} | {r['half_span'][i]:+.4f} | "
               f"{r['sigma_rel']['C_resp'][i]:.4f} | {r['sigma_rel']['C_total_resp'][i]:.4f} | "
               f"{r['abs_half_span_over_sigma']['C_resp'][i]:.3f} | {r['abs_half_span_over_sigma']['C_total_resp'][i]:.3f} |")
a = r["abs_half_span_over_sigma"]
s = r["half_span_summary_abs"]
out.append("")
out.append(f"- **\\|d\\|, median (min–max):** {s['median']:.4f} ({s['min']:.4f}–{s['max']:.4f}).")
out.append(f"- **\\|d\\|/σ for C_resp:** median {a['C_resp_summary']['median']:.3f} ({a['C_resp_summary']['min']:.3f}–{a['C_resp_summary']['max']:.3f}); "
           f"**for C_total + C_resp:** median {a['C_total_resp_summary']['median']:.3f} ({a['C_total_resp_summary']['min']:.3f}–{a['C_total_resp_summary']['max']:.3f}).")
q = r["half_span_quadratic_form"]
out.append(f"- **The half-span's quadratic form dᵀ M⁻¹ d:** {q['C_total_resp']:.3f} for M = C_total + C_resp; {q['C_total']:.3f} for M = C_total. Label: \"{q['label']}\".")
sp = r["fraction_of_half_span_in_C_resp_span"]
out.append(f"- **The fraction of d in C_resp's range:** {sp['value']:.4f}, beside rank/16 = {sp['random_direction_expectation']:.2f} (rank {sp['C_resp_rank']}). Label: \"{sp['label']}\".")
cr = r["curvature_ratio"]
out.append(f"- **The curvature ratio:** {cr['value']:.4f}. Label: \"{cr['label']}\".")
(Path(sys.argv[2]) / "t3a.md").write_text("\n".join(out) + "\n")
c = json.load(open(fd / "readout/fd_ct_chi2.json"))
P = ["5.0", "16.0", "50.0", "84.0", "95.0"]
out = []
for name, t in c["truths"].items():
    out.append(f"\n**{name}** (`{t['cal']}`): {t['n_experiments']} experiments, B_eff {t['B_eff']:.1f}.\n")
    out.append("| matrix | cells | χ² | weighted mean | weighted 5 / 16 / 50 / 84 / 95 % | unweighted mean | unweighted 5 / 16 / 50 / 84 / 95 % |")
    out.append("|---|---|---|---:|---|---:|---|")
    for mn, m in t["matrices"].items():
        for cn, x in m.items():
            for dn, lab in (("about_truth", "about the truth"), ("about_weighted_mean", "about b̃")):
                d = x[dn]; w = d["weighted"]; u = d["unweighted"]
                out.append(f"| {mn} | {cn} | {lab} | {w['mean']:.2f} | {' / '.join(f'{w['percentiles'][p]:.2f}' for p in P)} | "
                           f"{u['mean']:.2f} | {' / '.join(f'{u['percentiles'][p]:.2f}' for p in P)} |")
            ref = x["about_truth"]["reference_chi2"]
            out.append(f"| {mn} | {cn} | χ²_{ref['ndf']} | {ref['mean']:.2f} | {' / '.join(f'{ref['percentiles'][p]:.2f}' for p in P)} | | |")
            ws = x["width_ratio_summary"]
            out.append(f"| {mn} | {cn} | b̃'s own χ²; width ratio | {x['chi2_of_weighted_mean_bias']:.2f} | width ratio median {ws['median']:.3f} ({ws['min']:.3f}–{ws['max']:.3f}) | | |")
(Path(sys.argv[2]) / "t4c.md").write_text("\n".join(out) + "\n")
print("labels.chi2:", c["labels"]["what"])
print("labels.recoil:", r["labels"]["what"])
