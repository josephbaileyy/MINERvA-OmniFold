"""FD-G-DIAG report tables (FD-G-DIAG-BINDING.md section 3 item 4): reads only fd_g_diag_readout.json and the
committed Stage G readout fd_g_readout.json (for total - shape-only)."""
import json, sys

r = json.load(open(sys.argv[1]))
g = {p["name"]: p for p in json.load(open(sys.argv[2]))["predictions"]}
ORDER = ["stat", "interaction", "flux", "detector", "lateral", "normalization", "seed",
         "C_model:genie_mec", "C_model:nuwro", "C_model:gibuu", "C_resp", "V_g"]
SHORT = {"interaction": "int", "flux": "flux", "detector": "det", "lateral": "lat", "normalization": "norm",
         "seed": "seed", "stat": "stat", "C_model:genie_mec": "vMEC", "C_model:nuwro": "vNuWro",
         "C_model:gibuu": "vGiBUU", "C_resp": "C_resp", "V_g": "V_g"}
print(f"schema {r['schema']}; controls {r['controls_passed']}; non-finite written as null: {r['non_finite_written_as_null']}")
print(f"constants {r['constants']}")
print("blocks per group:", {k: len(v) for k, v in r["blocks"]["s1_blocks_per_group"].items()})

print("\n## overview (relative to f)")
print("| prediction | comparison | matrix | chi2/ndf | total - shape-only | cond | rank | modes 50/90/99 % | top mode: % of chi2, sigma, dominant | ridge_sensitive | methods_disagree |")
print("|---|---|---|---|---:|---:|---:|---|---|---|---|")
for p in r["predictions"]:
    for c in p["comparisons"]:
        b = c["relative_to_f"]
        gg = g[p["name"]] if c["comparison"] == "reported" else g[p["name"]]["variant"]
        t = b["top_modes"][0]
        m = b["modes_needed"]
        print(f"| {p['name']} | {c['comparison']} | {c['matrix']} | {b['chi2']:.2f}/{b['ndf']} | "
              f"{gg['total']['chi2'] - gg['shape_only']['chi2']:.2f} | {b['eigen']['condition']:.3g} | {b['eigen']['rank']} | "
              f"{m['50%']}/{m['90%']}/{m['99%']} | {100*t['fraction']:.1f} %, {100*t['sigma']:.2f} %, {t['dominant']} | "
              f"{b['stability']['ridge_sensitive']} | {b['stability']['methods_disagree']} |")

print("\n## stability (relative to f / absolute)")
print("| prediction | comparison | rel ridge change | rel mode-sum vs Cholesky | rel lstsq vs Cholesky | unstable |")
print("|---|---|---|---|---|---|")
for p in r["predictions"]:
    for c in p["comparisons"]:
        cells = []
        for u in ("relative_to_f", "absolute"):
            s = c[u]["stability"]
            cells.append(s)
        f = lambda k: " / ".join(f"{s[k]:.1e}" for s in cells)
        print(f"| {p['name']} | {c['comparison']} | {f('rel_ridge_vs_cholesky')} | {f('rel_mode_sum_vs_cholesky')} | "
              f"{f('rel_lstsq_vs_cholesky')} | {' / '.join(str(s['unstable']) for s in cells)} |")

for p in r["predictions"]:
    for c in p["comparisons"]:
        b = c["relative_to_f"]
        print(f"\n## {p['name']}, {c['comparison']} ({c['matrix']}), relative to f: top three modes")
        hdr = [k for k in ORDER if k in b["top_modes"][0]["block_shares"]]
        print("| mode | % of chi2 | sigma (rel) | dominant | " + " | ".join(SHORT[k] for k in hdr) + " |")
        print("|---:|---:|---:|---|" + "---:|" * len(hdr))
        for t in b["top_modes"]:
            print(f"| {t['mode']} | {100*t['fraction']:.1f} | {100*t['sigma']:.2f} % | {t['dominant']} | "
                  + " | ".join(f"{t['block_shares'][k]:.3f}" for k in hdr) + " |")
        print("loadings (cells with |v| >= 0.25):")
        for t in b["top_modes"]:
            big = {k: v for k, v in t["loadings"].items() if abs(v) >= 0.25}
            print(f"  mode {t['mode']}: " + ", ".join(f"{k} {v:+.2f}" for k, v in big.items()))
        print("removals:")
        print("| removed | chi2/ndf | condition | positive definite | ill-conditioned |")
        print("|---|---:|---:|---|---|")
        for x in b["removed"]:
            x2 = "–" if x["chi2"] is None else f"{x['chi2']:.2f}"
            print(f"| {x['removed']} | {x2}/{x['ndf']} | {x['condition']:.3g} | {x['positive_definite']} | {x['ill_conditioned']} |")
        a = c["absolute"]
        m = a["modes_needed"]
        print(f"the same chi2 decomposed in absolute units (different modes): chi2 {a['chi2']:.2f}; modes 50/90/99 % "
              f"{m['50%']}/{m['90%']}/{m['99%']}; cond {a['eigen']['condition']:.3g}; top modes: "
              + "; ".join(f"mode {t['mode']} {100*t['fraction']:.1f} % dominant {t['dominant']} ({t['block_shares'][t['dominant']]:.2f})"
                          for t in a["top_modes"]))
