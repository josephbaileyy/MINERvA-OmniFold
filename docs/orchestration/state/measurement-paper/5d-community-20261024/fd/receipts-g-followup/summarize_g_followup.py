"""FD-G-FOLLOWUP-REPORT.md: the report's tables, printed from the committed readout alone (no other input).
Usage: python3 -I -B summarize_g_followup.py fd/readout/fd_g_followup_readout.json"""
import json
import sys

r = json.load(open(sys.argv[1]))
R = r["r04"]
CELLS = r["constants"]["cells"]
OTHERS = CELLS[1:]


def pct(x, d=2):
    return "—" if x is None else f"{100 * x:.{d}f}"


def num(x, d=3):
    return "null" if x is None else f"{x:+.{d}f}"


print("## provenance: G-DIAG reported, relative-to-f top modes")
print("| prediction | mode | sigma % | fraction % | R04 rank | " + " | ".join(CELLS) + " |")
print("|---" * (5 + len(CELLS)) + "|")
for n, tops in R["provenance_g_diag_top_modes"].items():
    for t in tops:
        print(f"| {n} | {t['mode']} | {pct(t['sigma'])} | {pct(t['fraction'], 1)} | {t['rank_of_R04_by_abs_loading']} | "
              + " | ".join(f"{t['loadings'][c]:+.2f}" for c in CELLS) + " |")

print("\n## item 1: the definition")
print("| cell | H2 boxes | p_T | p_par | E_avail | q3 | W | fine bins | neighbours (axis) |")
print("|---|---|---|---|---|---|---|---|---|")
for c in CELLS:
    d = R["item1_definition"][c]
    b = d["box"]
    print(f"| {c} | {', '.join(map(str, d['h2_boxes']))} | " + " | ".join(f"{b[a][0]:g}–{b[a][1]:g}" for a in
                                                                       ("pt", "pz", "eavail", "q3", "W"))
          + f" | {d['n_fine_bins']} | " + ", ".join(f"{n['neighbour']} ({n['axis']})" for n in d["neighbours"]) + " |")

print("\n## item 2: relative sigma, %")
it2 = R["item2_relative_sigma"]
blocks = list(it2[CELLS[0]])
print("| block | " + " | ".join(CELLS) + " | median of 16 |")
print("|---" * (len(CELLS) + 2) + "|")
for k in blocks:
    print(f"| {k} | " + " | ".join(pct(it2[c][k]) for c in CELLS) + f" | {pct(it2['median_over_16'][k])} |")

print("\n## item 3: correlation with R04")
it3 = R["item3_correlation_with_R04"]
print("| matrix | rank | " + " | ".join(OTHERS) + " |")
print("|---" * (len(OTHERS) + 2) + "|")
for k, v in it3["under"].items():
    print(f"| {k} | {it3['rank'][k]} | " + " | ".join(num(v[c]) for c in OTHERS) + " |")
for n, v in it3["under_prediction"].items():
    print(f"| {v['matrix']} ({n}) | — | " + " | ".join(num(v[c]) for c in OTHERS) + " |")

print("\n## item 4: Stage G's reported comparison, per prediction and cell")
for n, p in R["item4_stage_g"].items():
    print(f"\n### {n} ({p['matrix']})")
    print("| cell | g/f − 1 % | pull | sigma_total/f % | sigma_Vg/f % | MC events |")
    print("|---|---|---|---|---|---|")
    for c in CELLS:
        v = p["cells"][c]
        if not v["compared"]:
            print(f"| {c} | not compared | | | | |")
        else:
            print(f"| {c} | {100 * v['g_over_f_minus_1']:+.2f} | {v['pull']:+.2f} | {pct(v['sigma_total_over_f'])} | "
                  f"{pct(v['sigma_Vg_over_f'])} | {v['n_mc_events']:.0f} |")

print("\n## item 5: the search")
i5 = R["item5_search"]
print("pattern:", i5["pattern"], i5["flags"], "on", i5["matched_on"])
print("string members not JSON:", i5["string_members_not_json"])
print("| product | keys searched | matches |")
print("|---|---|---|")
for k, n in i5["keys_searched"].items():
    print(f"| {k} | {n} | {len(i5['matches'][k])} |")
for k, v in i5["matches"].items():
    if v:
        print(f"- {k}: " + "; ".join(v))
print("- manifest (file names, not opened):", i5["s5p_manifest_paths_matching"]["paths"])
dv = i5["definition_values"]
print(f"\ndefinition simulation_only = {dv['simulation_only']}")
print("| field | " + " | ".join(CELLS) + " | median of 16 |")
print("|---" * (len(CELLS) + 2) + "|")
for f in dv["fields"]:
    fmt = (lambda x: f"{x:.3f}") if f in ("purity", "stability") else (lambda x: f"{x:,.0f}")
    print(f"| {f} | " + " | ".join(fmt(dv["cells"][c][f]) for c in CELLS) + f" | {fmt(dv['median_over_16'][f])} |")

print("\n## G-SENS")
print("label:", r["sens"]["label"])
print("unchanged:", r["sens"]["unchanged"])
recs = r["sens"]["records"]
for fam in r["constants"]["families"]:
    for n in dict.fromkeys(x["prediction"] for x in recs):
        rows = [x for x in recs if x["family"] == fam and x["prediction"] == n]
        print(f"\n### {fam} ({rows[0]['family_role']}), {n}, ndf {rows[0]['ndf']}")
        print("| α | χ² | condition | λ_min | modes 50/90/99 % | top mode σ % | its fraction % | leading cells |")
        print("|---|---|---|---|---|---|---|---|")
        for x in rows:
            t, m = x["top_mode"], x["modes_needed"]
            print(f"| {x['alpha']:g} | {x['chi2']:.2f} | {x['condition']:.3g} | {x['lambda_min']:.3g} | "
                  f"{m['50%']}/{m['90%']}/{m['99%']} | {pct(t['sigma'])} | {pct(t['fraction'], 1)} | "
                  + ", ".join(f"{y['cell']} {y['loading']:+.2f}" for y in t["leading_cells"]) + " |")
flags = [(x["family"], x["alpha"], x["prediction"]) for x in recs if x["stability"]["unstable"]]
print("\nunstable records:", flags or "none")
print("largest methods spread:", max(max(x["stability"]["rel_mode_sum_vs_cholesky"], x["stability"]["rel_lstsq_vs_cholesky"])
                                    for x in recs))
print("largest ridge change:", max(x["stability"]["rel_ridge_vs_cholesky"] for x in recs))
print("smallest shrunk-group lambda_min:", min(v for x in recs for v in x["shrunk_group_lambda_min"].values()))
print("smallest lambda_min of M:", min(x["lambda_min"] for x in recs))
print("worst |chi2(alpha 0) - Stage G| relative:", max(abs(x["chi2"] - x["chi2_stage_g"]) / x["chi2_stage_g"]
                                                       for x in recs if x["alpha"] == 0))
print("non_finite_written_as_null:", r["non_finite_written_as_null"])
