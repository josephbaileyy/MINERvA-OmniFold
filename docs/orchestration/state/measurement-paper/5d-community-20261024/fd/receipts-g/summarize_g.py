"""FD-G report tables (FD-F0b-AND-G-BINDING.md section 4 item 6): reads only fd_g_readout.json."""
import json, sys
import numpy as np

r = json.load(open(sys.argv[1]))
P = r["predictions"]
def pf(p):
    return f"{p:.3g}"
print(f"schema {r['schema']}; controls {r['controls_passed']}; extra_block {r['extra_block']['name']} role {r['extra_block']['role']} sha256 {r['extra_block']['sha256']}")
print(f"labels.reported: {r['labels']['reported']}\n")
print("## chi2 by prediction")
print("| prediction | cells | comparison | statistic | chi2 | ndf | p | matrix | size | rank |")
print("|---|---:|---|---|---:|---:|---:|---|---|---:|")
for p in P:
    for tag, rec in (("reported", p), ("variant without C_resp", p["variant"])):
        for k, name in (("total", "total"), ("shape_only", "shape-only")):
            s = rec[k]
            print(f"| {p['name']} | {p['n_cells']} | {tag} | {name} | {s['chi2']:.2f} | {s['ndf']} | {pf(s['p'])} | {s['matrix']} | "
                  f"{s['matrix_size'][0]}x{s['matrix_size'][1]} | {s['matrix_rank']} |")
print("\n## cells per prediction")
for p in P:
    print(f"{p['name']}: {', '.join(p['cells'])}")
cells = r["cells"]
print("\n## per-cell pulls (f - g)/sqrt(M_cc): reported (C_total + C_resp + V_g) / variant (C_total + V_g)")
print("| cell | " + " | ".join(p["name"] for p in P) + " |")
print("|---|" + "---:|" * len(P))
for c in cells:
    row = []
    for p in P:
        if c in p["cells"]:
            i = p["cells"].index(c)
            row.append(f"{p['pulls'][i]:+.2f} / {p['variant']['pulls'][i]:+.2f}")
        else:
            row.append("–")
    print(f"| {c} | " + " | ".join(row) + " |")
print("\n## per-cell g/f - 1, in %")
print("| cell | " + " | ".join(p["name"] for p in P) + " |")
print("|---|" + "---:|" * len(P))
for c in cells:
    row = [f"{100*p['g_over_f_minus_1'][p['cells'].index(c)]:+.1f}" if c in p["cells"] else "–" for p in P]
    print(f"| {c} | " + " | ".join(row) + " |")
print("\n## per-cell sigma/f, in %: covariance (reported, with C_resp) / (variant, C_total) ; V_g per prediction")
gc = P[0]
print("| cell | sqrt(C_total+C_resp)/f | sqrt(C_total)/f | " + " | ".join(f"sqrt(V_g)/f {p['name']}" for p in P) + " |")
print("|---|---:|---:|" + "---:|" * len(P))
for c in cells:
    i = gc["cells"].index(c)
    row = [f"{100*p['sigma_Vg_over_f'][p['cells'].index(c)]:.2f}" if c in p["cells"] else "–" for p in P]
    print(f"| {c} | {100*gc['sigma_total_over_f'][i]:.2f} | {100*gc['variant']['sigma_total_over_f'][i]:.2f} | " + " | ".join(row) + " |")
# consistency: sigma_total_over_f identical across predictions on shared cells; C_resp sigma in quadrature
for p in P:
    for c in p["cells"]:
        i, j = p["cells"].index(c), gc["cells"].index(c)
        assert abs(p["sigma_total_over_f"][i] - gc["sigma_total_over_f"][j]) <= 1e-12 * gc["sigma_total_over_f"][j]
xs = np.asarray(r["extra_block"]["relative_sigma"]); a = np.asarray(gc["sigma_total_over_f"]); b = np.asarray(gc["variant"]["sigma_total_over_f"])
print(f"\nmax |(C_total+C_resp) sigma^2 - C_total sigma^2 - C_resp sigma^2| / ... : {np.max(np.abs(a**2 - b**2 - xs**2) / a**2):.2e}")
print(f"sigma summaries %: C_total+C_resp median {100*np.median(a):.2f} min {100*a.min():.2f} max {100*a.max():.2f}; C_total median {100*np.median(b):.2f} min {100*b.min():.2f} max {100*b.max():.2f}")
print("\n## MC events in cells")
for p in P:
    n = np.asarray(p["n_mc_events_in_cells"])
    print(f"{p['name']}: min {n.min():.0f} median {np.median(n):.0f} max {n.max():.0f}")
print("\n## labels")
for p in P:
    print(f"{p['name']}: {p['label']}")
for k in ("covariance", "shape_only", "gibuu", "not"):
    print(f"labels.{k}: {r['labels'][k]}")
