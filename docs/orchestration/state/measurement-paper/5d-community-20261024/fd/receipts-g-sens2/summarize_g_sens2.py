"""FD-G-SENS2-REPORT.md: the report's tables, printed from the committed G-SENS2 readout and, for the two families
G-SENS2 references (binding ruling 6), the committed G-FOLLOWUP readout. No other input.
Usage: python3 -I -B summarize_g_sens2.py fd/readout/fd_g_sens2_readout.json fd/readout/fd_g_followup_readout.json"""
import hashlib
import json
import sys

r = json.load(open(sys.argv[1]))
fu_bytes = open(sys.argv[2], "rb").read()
fu = json.loads(fu_bytes)
assert hashlib.sha256(fu_bytes).hexdigest() == r["referenced"]["g_followup_readout"], "not the referenced readout"
recs, furecs = r["sens"]["records"], fu["sens"]["records"]
preds = list(dict.fromkeys(x["prediction"] for x in recs))
alphas = r["constants"]["alphas"]


def pct(x, d=2):
    return f"{100 * x:.{d}f}"


print("## identity (H0)")
print("| family | α | prediction | χ², G-FOLLOWUP readout | χ², recomputed | relative difference |")
print("|---|---|---|---|---|---|")
for x in r["identity"]:
    print(f"| {x['family']} | {x['alpha']:g} | {x['prediction']} | {x['chi2_g_followup_readout']:.6f} | "
          f"{x['chi2_recomputed']:.6f} | {x['relative_difference']:.1e} |")

print("\n## χ² by family and α, the five families side by side")
fams = [("interaction", furecs, "G-FOLLOWUP cd82517a"), ("c_e_systematic", furecs, "G-FOLLOWUP cd82517a"),
        ("flux", recs, "G-SENS2"), ("detector", recs, "G-SENS2"), ("lateral", recs, "G-SENS2")]
for n in preds:
    rows = {f: {x["alpha"]: x for x in src if x["family"] == f and x["prediction"] == n} for f, src, _ in fams}
    ndf = rows["flux"][0.0]["ndf"]
    print(f"\n### {n}, ndf {ndf}")
    print("| α | " + " | ".join(f"{f} ({w})" for f, _, w in fams) + " |")
    print("|---" * (len(fams) + 1) + "|")
    for a in alphas:
        print(f"| {a:g} | " + " | ".join(f"{rows[f][a]['chi2']:.2f}" for f, _, _ in fams) + " |")

for fam in r["constants"]["families"]:
    for n in preds:
        rows = [x for x in recs if x["family"] == fam and x["prediction"] == n]
        print(f"\n### {fam} ({rows[0]['family_role']}), {n}, ndf {rows[0]['ndf']}")
        print("| α | χ² | condition | λ_min | modes 50/90/99 % | top mode σ % | its fraction % | leading cells | "
              "group λ_min |")
        print("|---|---|---|---|---|---|---|---|---|")
        for x in rows:
            t, m = x["top_mode"], x["modes_needed"]
            print(f"| {x['alpha']:g} | {x['chi2']:.2f} | {x['condition']:.3g} | {x['lambda_min']:.3g} | "
                  f"{m['50%']}/{m['90%']}/{m['99%']} | {pct(t['sigma'])} | {pct(t['fraction'], 1)} | "
                  + ", ".join(f"{y['cell']} {y['loading']:+.2f}" for y in t["leading_cells"])
                  + f" | {x['shrunk_group_lambda_min'][fam]:.2g} |")

print("\n## flux: top-mode block shares")
sh = r["flux_top_mode_shares"]["predictions"]
blocks = list(next(iter(sh.values()))["0"]["block_shares"])
for n, by in sh.items():
    fol = by["alpha_0_mode_at_0.1"]
    print(f"\n### {n}")
    print(f"- α = 0 top mode {by['0']['mode']}, σ {pct(by['0']['sigma'])} %, carries {pct(by['0']['fraction'], 1)} % "
          f"(χ² {by['0']['chi2']:.2f}), flux_ratio {by['0']['flux_ratio']:.3f}, dominant {by['0']['dominant']}")
    print(f"- α = 0.1 top mode {by['0.1']['mode']}, σ {pct(by['0.1']['sigma'])} %, carries "
          f"{pct(by['0.1']['fraction'], 1)} % (χ² {by['0.1']['chi2']:.2f}), flux_ratio {by['0.1']['flux_ratio']:.3f}, "
          f"dominant {by['0.1']['dominant']}")
    print(f"- α = 0 mode followed into α = 0.1: χ² along it {fol['chi2_along']:.2f}, flux_ratio "
          f"{fol['flux_ratio']:.3f}, dominant {fol['dominant']}; overlap |v0·v0.1| {by['overlap_abs']:.3f}")
    print("\n| block | α = 0 own mode | α = 0.1 own mode | α = 0 mode at α = 0.1 |")
    print("|---|---|---|---|")
    for b in blocks:
        print(f"| {b} | {by['0']['block_shares'][b]:.3f} | {by['0.1']['block_shares'][b]:.3f} | "
              f"{fol['block_shares'][b]:.3f} |")

flags = [(x["family"], x["alpha"], x["prediction"]) for x in recs if x["stability"]["unstable"]]
print("\nunstable records:", flags or "none")
print("largest rel difference of mode-sum or lstsq from Cholesky:",
      max(max(x["stability"]["rel_mode_sum_vs_cholesky"], x["stability"]["rel_lstsq_vs_cholesky"]) for x in recs))
print("largest ridge change:", max(x["stability"]["rel_ridge_vs_cholesky"] for x in recs))
neg = sorted({(x["family"], x["alpha"], x["shrunk_group_lambda_min"][x["family"]]) for x in recs
              if x["shrunk_group_lambda_min"][x["family"]] <= 0})
print("non-positive shrunk-group lambda_min (family, alpha, value):", neg)
print("smallest lambda_min of M:", min(x["lambda_min"] for x in recs))
print("worst S0 relative:", max(abs(x["chi2"] - x["chi2_stage_g"]) / x["chi2_stage_g"] for x in recs if x["alpha"] == 0))
print("non_finite_written_as_null:", r["non_finite_written_as_null"])
