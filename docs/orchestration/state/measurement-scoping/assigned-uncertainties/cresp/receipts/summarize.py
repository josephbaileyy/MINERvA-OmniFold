"""Summarize cresp.json: per-block min/median/max relative sigma, and internal consistency checks.
Reads only the readout JSON (relative quantities); no data-against-generator quantity."""
import json, sys
import numpy as np
j = json.load(open(sys.argv[1]))
rs = {k: np.array(v) for k, v in j["relative_sigma"].items()}
cells = j["cells"]
P = j["meta"]["primary"]
order = [f"C_resp_{s}" for s in P] + ["C_resp", "C_resp_xtalk", "C_total", "C_total_resp"]
print("| block | median | min (cell) | max (cell) |\n|---|---:|---:|---:|")
for k in order:
    v = rs[k]; med = j["median_relative_sigma"][k]
    assert abs(np.median(v) - med) < 1e-15, k
    print(f"| `{k}` | {100*med:.2f} % | {100*v.min():.2f} % ({cells[v.argmin()]}) | {100*v.max():.2f} % ({cells[v.argmax()]}) |")
# diag additivity
r_sum = np.sqrt(sum(rs[f"C_resp_{s}"]**2 for s in P))
print("max |C_resp - quad(species)| rel:", np.max(np.abs(r_sum - rs["C_resp"]) / rs["C_resp"]))
r_tot = np.sqrt(rs["C_total"]**2 + rs["C_resp"]**2)
print("max |C_total_resp - quad(C_total,C_resp)| rel:", np.max(np.abs(r_tot - rs["C_total_resp"]) / rs["C_total_resp"]))
T = np.sum(rs["C_total_resp"]**2)
for k, share in j["trace_share_of_C_total_resp"].items():
    print(f"trace share {k}: json {share:.6f} recomputed {np.sum(rs[k]**2)/T:.6f}")
print("trace shares sum:", sum(j["trace_share_of_C_total_resp"].values()))
print(f"xtalk, same normalisation (not in C_total_resp): {np.sum(rs['C_resp_xtalk']**2)/T:.6f}")
print("\nper cell:\n| cell | proton | meson | EM | other | C_resp | cross-talk | C_total | C_total_resp | ratio |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
for i, c in enumerate(cells):
    row = [rs[k][i] for k in order[:5]] + [rs["C_resp_xtalk"][i], rs["C_total"][i], rs["C_total_resp"][i]]
    print(f"| {c} | " + " | ".join(f"{100*x:.2f}" for x in row) + f" | {rs['C_total_resp'][i]/rs['C_total'][i]:.3f} |")
ratio = rs["C_total_resp"] / rs["C_total"]
print("ratio C_total_resp/C_total sigma: median %.4f min %.4f (%s) max %.4f (%s)" % (np.median(ratio), ratio.min(), cells[ratio.argmin()], ratio.max(), cells[ratio.argmax()]))
dom = [P[np.argmax([rs[f'C_resp_{s}'][i] for s in P])] for i in range(16)]
print("largest species per cell:", {s: dom.count(s) for s in P})
print("cells where C_resp > C_total/2:", [c for i, c in enumerate(cells) if rs['C_resp'][i] > rs['C_total'][i]/2])
print("xtalk/C_resp ratio: median %.3f max %.3f (%s)" % (np.median(rs['C_resp_xtalk']/rs['C_resp']), (rs['C_resp_xtalk']/rs['C_resp']).max(), cells[(rs['C_resp_xtalk']/rs['C_resp']).argmax()]))
