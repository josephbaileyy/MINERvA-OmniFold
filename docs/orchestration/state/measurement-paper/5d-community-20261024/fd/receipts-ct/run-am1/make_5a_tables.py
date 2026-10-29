"""Writes the numeric tables of FD-CT-READERS-5A-REPORT.md from the committed 5A readout (no number is typed by hand)."""
import json, sys
from pathlib import Path
r = json.load(open(Path(sys.argv[1]) / "readout/fd_ct_period.json"))
out = []
for vn, v in r["variants"].items():
    pr = vn == "prior"
    out.append(f"\n**Weighting: {vn}** ({r['constants']['weights'][vn]}). Rank of C_PL,16: {v['rank']}. Trace share of C_PL,16 "
               f"in C_total + C_resp + C_PL,16: {v['trace_share']:.5f}. Extrapolated cells (u_R > {r['constants']['extrapolated_above']}): "
               f"{v['extrapolated_cells'] or 'none'}. 2D cells with negative weight, per cell: {v['negative_weight_2d_cells']}.\n")
    hdr = "| cell | σ/f C_PL,16 | σ/f S_ref,16 | σ/f C_total + C_resp | ratio C_PL,16 / (C_total + C_resp) |" + (" u_R |" if pr else "")
    out.append(hdr)
    out.append("|---|---:|---:|---:|---:|" + ("---:|" if pr else ""))
    for i, c in enumerate(r["cells"]):
        row = (f"| {c} | {v['sigma_rel']['C_PL16'][i]:.5f} | {v['sigma_rel']['S_ref16'][i]:.5f} | "
               f"{v['sigma_rel']['C_total_resp'][i]:.5f} | {v['sigma_ratio_to_C_total_resp'][i]:.4f} |")
        if pr:
            row += f" {v['weight_outside_2d_support'][i]:.5f} |"
        out.append(row)
    s, q = v["sigma_rel_summary"], v["sigma_ratio_summary"]
    out.append("")
    out.append(f"- σ/f of C_PL,16: median {s['C_PL16']['median']:.5f} ({s['C_PL16']['min']:.5f}–{s['C_PL16']['max']:.5f}); "
               f"of S_ref,16: median {s['S_ref16']['median']:.5f} ({s['S_ref16']['min']:.5f}–{s['S_ref16']['max']:.5f}).")
    out.append(f"- The ratio to C_total + C_resp: median {q['median']:.4f} ({q['min']:.4f}–{q['max']:.4f}).")
e = r["constants"]["e"]
out.append(f"\n**Constants:** e = {e['PA']:.4f}, {e['PB']:.4f}, {e['PC']:.4f} (PA, PB, PC); k = V2/(1 − V2) = {r['constants']['k']:.4f}.")
print("\n".join(out))
print("\nLABEL::" + r["labels"]["what"])
