"""F0b report tables (FD-F0b-AND-G-BINDING.md section 2 items 3-4): reads only F0's committed readout and F0b's readout."""
import json, sys
import numpy as np

f0, f0b = (json.load(open(p)) for p in sys.argv[1:3])
REL = 1e-12
def rel_eq(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return a.shape == b.shape and bool(np.all(np.abs(a - b) <= REL * np.maximum(np.abs(a), np.abs(b))))

print("## item 3: equality with F0's committed readout, to a relative 1e-12")
c0, c1 = f0["controls"]["offset_control_7"], f0b["controls"]["offset_control_7"]
print(f"control 7 chi2: F0 {c0['chi2']!r}  F0b {c1['chi2']!r}  equal {rel_eq(c0['chi2'], c1['chi2'])}  "
      f"pass F0 {c0['pass']} F0b {c1['pass']}  p_below_floor F0 {c0['p_below_floor']} F0b {c1['p_below_floor']}")
print(f"control 7 record identical: {c0 == c1};  controls identical: {f0['controls'] == f0b['controls']}")
A, B = {t["name"]: t for t in f0["truths"]}, {t["name"]: t for t in f0b["truths"]}
assert list(A) == list(B)
bad = []
for n in A:
    m0, m1 = A[n]["model_only"], B[n]["model_only"]
    ok = rel_eq(m0["chi2"], m1["chi2"]) and rel_eq(m0["z"], m1["z"]) and rel_eq(m0["p"], m1["p"]) and m0["cells"] == m1["cells"]
    if not ok:
        bad.append(n)
print(f"model-only grades equal (chi2, z, p) for {len(A) - len(bad)} of {len(A)} truths; unequal: {bad}")
print(f"model-only records identical: {sum(A[n]['model_only'] == B[n]['model_only'] for n in A)} of {len(A)}")
for k in ("bias", "noise_sigma", "B_eff", "graded"):
    print(f"{k} identical for all truths: {all(A[n][k] == B[n][k] for n in A)}")
print(f"table_sha256: F0 {f0['table_sha256']}  F0b {f0b['table_sha256']}")

print("\n## item 4: trigger counts by group")
print("| group | F0: cells |z|>2, C^(T) | F0b: cells |z|>2, C^(T) + C_resp | Gaussian ref | F0: truths p<0.01, C^(T) | F0b: truths p<0.01, C^(T) + C_resp | ref |")
print("|---|---:|---:|---:|---:|---:|---:|")
for g in sorted(f0["triggers"]["by_group"]):
    a, b = f0["triggers"]["by_group"][g], f0b["triggers"]["by_group"][g]
    assert (a["cells"], a["truths"]) == (b["cells"], b["truths"])
    print(f"| {g} | {a['cells_abs_z_gt_2']} of {a['cells']} | {b['cells_abs_z_gt_2']} of {b['cells']} | {a['gaussian_reference_cells']:.2f} | "
          f"{a['truths_p_lt_0.01']} of {a['truths']} | {b['truths_p_lt_0.01']} of {b['truths']} | {a['gaussian_reference_truths']:.2f} |")
a, b = f0["triggers"]["all_graded"], f0b["triggers"]["all_graded"]
print(f"| all graded (read by group) | {a['cells_abs_z_gt_2']} of {a['cells']} | {b['cells_abs_z_gt_2']} of {b['cells']} | {a['gaussian_reference_cells']:.2f} | "
      f"{a['truths_p_lt_0.01']} of {a['truths']} | {b['truths_p_lt_0.01']} of {b['truths']} | {a['gaussian_reference_truths']:.2f} |")
print("\nby family (vertex-family):")
for fam in f0["triggers"]["by_group"]["vertex-family"]["by_family"]:
    a = f0["triggers"]["by_group"]["vertex-family"]["by_family"][fam]
    b = f0b["triggers"]["by_group"]["vertex-family"]["by_family"][fam]
    print(f"  {fam}: truths {a['truths']}; cells |z|>2 F0 {a['cells_abs_z_gt_2']} F0b {b['cells_abs_z_gt_2']}; p<0.01 F0 {a['truths_p_lt_0.01']} F0b {b['truths_p_lt_0.01']}")

print("\n## listed truths")
L0 = {x["truth"]: x for x in f0["triggers"]["listed"]}
L1 = {x["truth"]: x for x in f0b["triggers"]["listed"]}
print("| truth | F0 (C^(T)): cells |z|>2; p<0.01 | F0b (C^(T) + C_resp): cells |z|>2; p<0.01 |")
print("|---|---|---|")
for n in A:
    if n in L0 or n in L1:
        f = lambda x: "not listed" if x is None else f"{', '.join(x['cells']) or 'none'}; {x['p_lt_0.01']}"
        print(f"| {n} | {f(L0.get(n))} | {f(L1.get(n))} |")
changed = [n for n in A if (n in L0) != (n in L1) or (n in L0 and L0[n] != L1[n])]
print(f"listing changed between F0 and F0b: {changed}")
print(f"  of which listed in F0 only: {[n for n in A if n in L0 and n not in L1]}; in F0b only: {[n for n in A if n in L1 and n not in L0]}")

print("\n## per truth: chi2 / p (ndf 16; eight-cell ndf 8)")
def cp(g):
    if g is None:
        return "-"
    p = "<1e-30" if g["p_below_floor"] else f"{g['p']:.3g}"
    return f"{g['chi2']:.2f} / {p}"
print("| truth | row | group | graded | grade F0 | grade F0b | in-sample F0 | in-sample F0b | sensitivity F0 | sensitivity F0b | model-only (both) | 8-cell F0 | 8-cell F0b |")
print("|---|---:|---|---|---|---|---|---|---|---|---|---|---|")
for n in A:
    a, b = A[n], B[n]
    print(f"| {n} | {a['row']} | {a['group']} | {a['graded']} | {cp(a['grade'])} | {cp(b['grade'])} | {cp(a.get('in_sample'))} | {cp(b.get('in_sample'))} | "
          f"{cp(a.get('sensitivity'))} | {cp(b.get('sensitivity'))} | {cp(a['model_only'])} | {cp(a.get('p_parallel_lt_4p5'))} | {cp(b.get('p_parallel_lt_4p5'))} |")
print("\nmatrix names (F0b): " + "; ".join(sorted({t["grade_matrix"] for t in f0b["truths"]})))
print("sensitivity matrices (F0b): " + "; ".join(f"{t['name']}: {t['sensitivity']['matrix']}" for t in f0b["truths"] if "sensitivity" in t))
s0, s1 = f0["relative_sigma_summary_percent"], f0b["relative_sigma_plus_C_resp_summary_percent"]
print("\n## per-cell relative sigma summary, % (median, min, max)")
for k in s0:
    print(f"{k}: F0 {s0[k]}  F0b (+ C_resp) {s1[k]}")
xs = np.asarray(f0b["extra_block"]["relative_sigma"])
print(f"C_resp alone: median {100*np.median(xs):.2f} min {100*xs.min():.2f} max {100*xs.max():.2f}")
print(f"F0b extra_block: name {f0b['extra_block']['name']} key {f0b['extra_block']['key']} sha256 {f0b['extra_block']['sha256']}")
print(f"schema {f0b['schema']}; code fd_f0_regrade.py {f0b['code_sha256']['fd_f0_regrade.py']}")
