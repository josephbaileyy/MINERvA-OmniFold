"""Build the REPORT tables from the JSON outputs (no ROOT). Usage: python3 -I summarize.py <outputs dir> > summary_tables.md"""
import json
import sys

o = sys.argv[1]
mb = json.load(open(f"{o}/mix_bias.json"))
ed = json.load(open(f"{o}/eff_decomp.json"))
it = json.load(open(f"{o}/intensity.json"))
fx = json.load(open(f"{o}/fluxcheck.json"))
PLS = list(mb["factors"])

print("## T1. Per-playlist factors (May per-playlist CV event-loop outputs; 10x10 grid of yields.py)\n")
print("| PL | data POT share | MC POT share | POT_d/POT_mc | data/1e19 | bkg/1e19 (MC) | (D-B)/1e19 | truth/1e19 (MC) "
      "| eff S/T | R | rel. (D-B) | rel. eff | rel. truth | rel. R |")
print("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
for p in PLS:
    f, w = mb["factors"][p], mb["_mix_weights"][p]
    r = f["rel_to_1A1D_mean"]
    print(f"| {p} | {w['data_share']:.4f} | {w['mc_share']:.4f} | {w['potd_over_potmc']:.4f} | {f['data_per_1e19']:,.0f} | "
          f"{f['bkg_per_1e19_mc']:,.0f} | {f['dsub_per_1e19']:,.0f} | {f['truth_per_1e19_mc']:,.0f} | {f['eff_S_over_T']:.4f} | "
          f"{f['R']:.4f} | {r['dsub_per_1e19']:.4f} | {r['eff_S_over_T']:.4f} | {r['truth_per_1e19_mc']:.4f} | {r['R']:.4f} |")
print("\n'rel.' = ratio to the mean of 1A-1D. R = rel.(D-B) / (rel.eff x rel.truth) exactly.\n")

print("## T2. MC efficiency steps (w_truth-weighted unless stated) and unweighted miss classes\n")
print("| PL | reco-selection eff | in-grid given pass | w_reco/w_truth | S/T | truth-only misses / rows | "
      "in-tree failing / rows | flux integral (m^-2/POT) |")
print("|---|---:|---:|---:|---:|---:|---:|---:|")
for p in PLS:
    e = ed[p]
    tom = e["nTruthOnlyMisses_param"] / e["n_rows"]
    fail = (e["n_miss_rows"] - e["nTruthOnlyMisses_param"]) / e["n_rows"]
    print(f"| {p} | {e['f_present']:.4f} | {e['f_grid_pass']:.4f} | {e['wreco_over_wtruth']:.4f} | {e['eff']:.4f} | "
          f"{tom:.4f} | {fail:.4f} | {fx[p]['flux_sum_m2_per_pot']:.7f} |")

print("\n## T3. AnaTuple sample: intensity and reco-level rates (3 Data files, 1 MC file per playlist; fiducial reco vertex)\n")
print("| PL | numi_pot Data / MC (1e12) | batch POT Data / MC | fid. per 1e17 POT Data / MC | ratio | "
      "match&tdead&nu fraction Data / MC | ratio | chain per 1e17 POT ratio | MINOS CV weight (MC, matched) |")
print("|---|---|---|---|---:|---|---:|---:|---:|")
for p in PLS:
    D, M = it[p]["Data"], it[p]["MC"]
    print(f"| {p} | {D['numi_pot_mean']:.1f} / {M['numi_pot_mean']:.1f} | {D['batch_pot_mean']:.2f} / {M['batch_pot_mean']:.2f} | "
          f"{D['fiducial_per_1e17_pot']:.0f} / {M['fiducial_per_1e17_pot']:.0f} | {it[p]['fiducial_per_1e17_pot_data_over_mc']:.4f} | "
          f"{D['match_tdead_nu_frac']:.4f} / {M['match_tdead_nu_frac']:.4f} | {it[p]['match_tdead_nu_frac_data_over_mc']:.4f} | "
          f"{it[p]['chain_per_1e17_pot_data_over_mc']:.4f} | {M['minos_corr_mean_on_matched']:.4f} |")
print("\nn_fiducial (Data, MC): " + ", ".join(f"{p} {it[p]['Data']['n_fiducial']}/{it[p]['MC']['n_fiducial']}" for p in PLS))

print("\n## T4. Mix bias, pooled (production) over per-playlist (dw), efficiency-corrected binned rate\n")
for n in ("bbb", "ibu"):
    b = mb[n]
    print(f"- {n}: total {b['total_bias'] * 100:+.3f}% (MC-stat sd {b['total_bias_mcstat'] * 100:.3f}%, {mb['_toys']} toys); "
          f"bins with D>=50: {b['bins_used_D_ge_50']}, min/max {b['bin_bias_min_max_D_ge_50'][0] * 100:+.2f}% / "
          f"{b['bin_bias_min_max_D_ge_50'][1] * 100:+.2f}%")
    print("  - p_T marginal (%): " + ", ".join(f"{x * 100:+.2f}" for x in b["pt_marginal_bias"]))
    print("  - p_|| marginal (%): " + ", ".join(f"{x * 100:+.2f}" for x in b["pz_marginal_bias"]))
print(f"- efficiency part only (bbb): {mb['bbb_eff_only']['total_bias'] * 100:+.3f}%; background part only: "
      f"{mb['bbb_bkg_only']['total_bias'] * 100:+.4f}%")
print(f"- integrated efficiency, pooled {mb['eff_total_pooled']:.5f} vs per-playlist {mb['eff_total_dw']:.5f}; "
      f"background, pooled {mb['bkg_total_pooled']:.1f} vs per-playlist {mb['bkg_total_dw']:.1f} events; "
      f"global POT_d/POT_mc {mb['global_potd_over_potmc']:.6f}")
