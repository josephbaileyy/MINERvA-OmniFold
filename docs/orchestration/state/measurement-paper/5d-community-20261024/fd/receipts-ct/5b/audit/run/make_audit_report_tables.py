"""Print FD-CT-5B-AUDIT-REPORT.md's tables from the committed readout, so that no number is transcribed by hand.

Usage: python3 -I -B make_audit_report_tables.py <fd_ct_5b_audit.json> <fd_ct_5b_periods.json>
"""
import hashlib
import json
import sys

A_PATH, B5_PATH = sys.argv[1], sys.argv[2]
A = json.load(open(A_PATH))
B5 = json.load(open(B5_PATH))
PER = ("PA", "PB", "PC")
GROUPS = ("flux", "detector", "lateral", "C_resp", "DR", "interaction", "normalization", "C_model", "all")


def pct(x):
    return f"{100 * x:+.3f}%"


def f3(x):
    return f"{x:.3f}"


def f4(x):
    return f"{x:.4f}"


print(f"readout sha256 {hashlib.sha256(open(A_PATH, 'rb').read()).hexdigest()}")
print(f"5B readout sha256 {hashlib.sha256(open(B5_PATH, 'rb').read()).hexdigest()}")
print(f"controls_passed {A['controls_passed']}; assertions_passed {A['assertions_passed']}")
sc = A["stop_condition"]
print("\nstop_condition (verbatim):\n")
print("```json\n" + json.dumps(sc, indent=1) + "\n```")

i1 = A["item1_overlap"]
idf = i1["identification"]
print("\n## T1 OV per group (on P, and on P's pattern part)\n")
print("| group | OV(P) | b_1, b_2 along P's modes | OV(pattern) | b_1, b_2 along the pattern's modes |")
print("|---|---:|---|---:|---|")
for g in GROUPS:
    o, p = i1["OV"][g], i1["OV_pattern"][g]
    print(f"| {g} | {f3(o['OV'])} | {o['b'][0]:.3e}, {o['b'][1]:.3e} | {f3(max(p['OV'], 0.0))} "
          f"| {p['b'][0]:.3e}, {p['b'][1]:.3e} |")
o, p = i1["OV"]["all"], i1["OV_pattern"]["all"]
print(f"\nP's λ: {o['lambda'][0]:.3e}, {o['lambda'][1]:.3e}; the pattern part's λ: {p['lambda'][0]:.3e}, "
      f"{p['lambda'][1]:.3e}")
print(f"normalization's OV(pattern) as written: {i1['OV_pattern']['normalization']['OV']:.3e} (a numerical zero)")

print("\n## T2 identification: the best three per group by min(E_PB, E_PC), then named rows\n")
q = idf["residual_q95_chi2_14"]
print(f"N_cand {idf['n_candidates']}; uniform, excluded: {idf['uniform_excluded']}; fired_by {idf['fired_by']}; "
      f"χ²_res(1): " + ", ".join(f"{X} {idf['candidates'][0][X]['chi2_res_intercept']:.1f}" for X in PER)
      + f"; χ²₁₄ 95% {q:.3f}")
print("\n| group | candidate | E_PB (a_PB) | E_PC (a_PC) | E_PA (a_PA) | χ²_res PB, PC | fires O |")
print("|---|---|---|---|---|---|---|")


def row(g, c):
    e = {X: f"{f3(c[X]['E'])} ({c[X]['a'][0]:+.2f})" for X in PER}
    print(f"| {g} | `{c['candidate']}` | {e['PB']} | {e['PC']} | {e['PA']} | "
          f"{c['PB']['chi2_res']:.1f}, {c['PC']['chi2_res']:.1f} | {c['fires_O']} |")


for g, L in idf["best_per_group"].items():
    for c in L:
        row(g, c)
byname = {c["candidate"]: c for c in idf["candidates"]}
print("| (named: E ≥ 0.5 in PB or PC) | | | | | | |")
for c in idf["candidates"]:
    if (c["PB"]["E"] >= 0.5 or c["PC"]["E"] >= 0.5) and not any(
            c["candidate"] == b["candidate"] for L in idf["best_per_group"].values() for b in L):
        row(c["group"], c)
top = max(idf["candidates"], key=lambda c: min(c["PB"]["E"], c["PC"]["E"]))
print(f"\nlargest min(E_PB, E_PC) over all candidates: {f3(min(top['PB']['E'], top['PC']['E']))} "
      f"(`{top['candidate']}`)")
bp = idf["best_pair_in_DR"]
print(f"\nbest pair in DR (no stop role): {bp['candidates']}, score {f3(bp['score'])}; "
      + "; ".join(f"{X} E {f3(bp[X]['E'])}, a ({bp[X]['a'][0]:+.2f}, {bp[X]['a'][1]:+.2f}), "
                  f"χ²_res {bp[X]['chi2_res']:.1f}" for X in PER))
le = idf["look_elsewhere"]
print(f"\nlook-elsewhere: Beta tail {le['beta_tail']:.4f}; if PB and PC identical {le['if_PB_PC_patterns_identical']:.4f}; "
      f"if independent {le['if_independent']:.2e}")
nv = i1["noise_vs_stat"]
s = nv["floor_over_stat_sigma_summary"]
print(f"\nfloor σ / C_stat σ: median {f3(s['median'])}, range {f3(s['min'])}–{f3(s['max'])}; expected √(2k) "
      f"{f3(nv['expected_under_poisson_sqrt_2k'])}; tr(floor)/tr(P) {f4(nv['floor_trace_share_of_P'])}")

i2 = A["item2_stability"]
cells = A["cells"]
print("\n## T3 stability\n")
print(f"s_med {i2['s_med']:.4f} (threshold {i2['threshold_N']}); replica median σ: "
      + ", ".join(f"{100 * x:.3f}%" for x in i2["replica_median_sigma"]))
print("replica trace share of M + P^(k): " + ", ".join(f4(x) for x in i2["replica_trace_share"]))
jk = i2["jackknife"]
print("noise E[χ²_M], all ten (jackknife SE): " + "; ".join(
    f"{k} {jk['expected_chi2_M'][k]:.3f} ({jk['expected_chi2_M_se'][k]:.3f})" for k in jk["expected_chi2_M"]))
for h, v in i2["split_half"].items():
    print(f"split half {h}: " + "; ".join(f"{k} {x:.3f}" for k, x in v["expected_chi2_M"].items()))
print(f"noise-dominated cells {i2['noise_dominated_cells']}; debiased rank {i2['debiased']['rank']}")
tp = i2["three_periods"]
print(f"ν_eff {tp['nu_eff']:.4f}; 68% interval on σ_true/σ̂ [{tp['sigma_ratio_68'][0]:.4f}, {tp['sigma_ratio_68'][1]:.4f}]")
print("\n| cell | replica σ, mean (SD) | √diag(mean P^(k)) / σ(P) − 1 | σ(floor)/σ(P) | σ(P)/σ(floor), jackknife SE "
      "| debiased σ / σ(P) | σ(floor)/σ(C_stat) |")
print("|---|---|---:|---:|---:|---:|---:|")
for j, c in enumerate(cells):
    print(f"| {c} | {100 * i2['replica_sigma_mean'][j]:.3f}% ({100 * i2['replica_sigma_sd'][j]:.3f}%) | "
          f"{i2['mean_block_sigma_over_P_sigma_minus_1'][j]:+.3f} | {f3(i2['floor_sigma_over_P_sigma'][j])} | "
          f"{f3(jk['sigma_over_floor_se'][j])} | {f4(i2['debiased']['sigma_over_P_sigma'][j])} | "
          f"{f3(nv['floor_over_stat_sigma'][j])} |")

i3 = A["item3_5a_vs_5b"]
print("\n## T4 5A against 5B\n")
print(f"uniform share: 5B {f4(i3['uniform_share']['5B'])}, 5A {f4(i3['uniform_share']['5A'])}; trace: 5B "
      f"{i3['trace']['5B']:.4e}, 5A {i3['trace']['5A']:.4e}; trace with the uniform part removed: 5B "
      f"{i3['trace_uniform_removed']['5B']:.4e}, 5A {i3['trace_uniform_removed']['5A']:.4e}")
print("\n| period | mean offset 5B | mean offset 5A | pattern correlation | \\|Δ\\|/σ_comb median (min–max) "
      "| Σ (Δ/σ_comb)² over 16 cells |")
print("|---|---:|---:|---:|---|---:|")
for X in PER:
    p = i3["periods"][X]
    s = p["abs_difference_over_combined_noise_summary"]
    print(f"| {X} | {pct(p['mean_offset']['5B'])} | {pct(p['mean_offset']['5A'])} | {f3(p['pattern_correlation'])} | "
          f"{f3(s['median'])} ({f3(s['min'])}–{f3(s['max'])}) | {p['difference_chi2_combined_diagonal']:.1f} |")
print("\nE_avail contrast (POST HOC), Δ = g_5B − g_5A, low minus high E_avail, ± its combined-noise σ:\n")
print("| period | p_∥ low half: low {R00, R08} − high {R02, R03, R10, R11} | p_∥ high half: low {R04, R12} − high "
      "{R06, R07, R15} |")
print("|---|---|---|")
for X in PER:
    e = i3["periods"][X]["ea_contrast"]
    print(f"| {X} | " + " | ".join(
        f"{pct(e[h]['low_minus_high'])} ± {100 * e[h]['sigma']:.3f}% ({e[h]['low_minus_high'] / e[h]['sigma']:+.2f}σ)"
        for h in ("pz_lo", "pz_hi")) + " |")
pl = i3["planes"]
print(f"\nprincipal angles span(P_5A) vs span(P_5B): {pl['principal_angles_deg'][0]:.2f}°, "
      f"{pl['principal_angles_deg'][1]:.2f}°")
print("share of g_5A,X outside 5B's plane: " + ", ".join(f"{X} {f3(pl['g5a_outside_5B_plane'][X])}" for X in PER))
print("share of g_5B,X outside 5A's plane: " + ", ".join(f"{X} {f3(pl['g5b_outside_5A_plane'][X])}" for X in PER))
print("\nper cell |Δ|/σ_comb:\n")
print("| cell | " + " | ".join(PER) + " |")
print("|---|---:|---:|---:|")
for j, c in enumerate(cells):
    print(f"| {c} | " + " | ".join(f3(i3["periods"][X]["abs_difference_over_combined_noise"][j]) for X in PER) + " |")

i4 = A["item4_rank_two"]
print("\n## T5 rank two\n")
print(f"rank {i4['rank']}; whitened eigenvalues λ̃ {i4['whitened_eigenvalues'][0]:.4f}, "
      f"{i4['whitened_eigenvalues'][1]:.4f}; largest χ² fall fraction {f4(i4['largest_chi2_fall_fraction'])}")
print("reference bound: " + "; ".join(
    f"{X} {f4(v['value'])} (first order {f4(v['first_order_bound'])})" for X, v in i4["reference_bound"].items()))
print(f"plane retention median {f4(i4['plane_retention_median'])} (threshold {i4['threshold_R']}); R_k: "
      + ", ".join(f4(x) for x in i4["plane_retention"]))
print("principal angles span(P) vs span(P^(k)), degrees: "
      + "; ".join(f"{a:.1f}, {b:.1f}" for a, b in i4["replica_principal_angles_deg"]))
