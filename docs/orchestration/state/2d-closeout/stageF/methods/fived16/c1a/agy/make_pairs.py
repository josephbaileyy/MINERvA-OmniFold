"""Build the agy pairs for step (c)'s 1A sentences: BEFORE is the study's facts, generated from fd_f1_readout.json and
quoted from FD-F1-REPORT.md (nothing retyped); AFTER is each sentence as it prints (prd-read/r5/input.txt, the NEW
lines). The control copy plants one strengthening per planted pair; BEFORE excuses nothing (the b2 lesson).
usage: python3 make_pairs.py <worktree> <outdir> [input.txt [prefix]]
  pass 1: prd-read/r5/input.txt (the first drafts), pairs.txt; pass 2: prd-read/r5/applied.txt (the round-5 forms
  applied), pairs2.txt."""
import json, re, sys
W, O = sys.argv[1], sys.argv[2]
INP = sys.argv[3] if len(sys.argv) > 3 else None
PFX = sys.argv[4] if len(sys.argv) > 4 else "pairs"
FD = f"{W}/docs/orchestration/state/measurement-paper/5d-community-20261024"
M = f"{W}/docs/orchestration/state/2d-closeout/stageF/methods/fived16"
ro = json.load(open(f"{FD}/fd/readout/fd_f1_readout.json"))
rep = open(f"{FD}/FD-F1-REPORT.md").read()
new = dict(re.findall(r"^(L1|A1|A2|H1|H2) \([^)]*\)\. OLD: .*\nNEW: (.*)$", open(INP or f"{M}/prd-read/r5/input.txt").read(), re.M))
assert sorted(new) == ["A1", "A2", "H1", "H2", "L1"]
sig = ro["relative_sigma_plus_C_resp"]["C_total"]
recs = []
for t in ro["truths"]:
    if t["group"] != "held-out":
        continue
    g, s, md = t["grade"], t["sensitivity"], t["model_only"]
    i = max(range(16), key=lambda j: abs(g["z"][j]))
    bs = max(abs(b) / x for b, x in zip(t["bias"], sig))
    recs.append(f"{t['name']} ({t['estimator']}, {t['n_experiments']} experiment(s)): chi2 {g['chi2']:.3f} for 16 dof, "
                f"p {g['p']:.3f}, largest |z| {abs(g['z'][i]):.3f} in {g['cells'][i]}, cells with |z| > 2: "
                f"{len(g['cells_abs_z_gt_2'])}; max over cells of |bias|/sigma {bs:.3f}; leave-out-GENIE+MEC (descriptive) "
                f"chi2 {s['chi2']:.3f}, p {s['p']:.3f}; model-only (descriptive) chi2 {md['chi2']:.1f}, cells with "
                f"|z| > 2: {', '.join(md['cells_abs_z_gt_2']) or 'none'}")
gt = ro["triggers"]["by_group"]["held-out"]


def quote(start, end):
    i = rep.index(start); j = rep.index(end, i)
    return re.sub(r"\s+", " ", rep[i:j + len(end)]).replace("`", "").replace("**", "")


facts = ("Facts from the study's report and readout (accepted as correct): "
         f"The readout's label: \"{ro['labels']['f1']}\". The readout also says: \"{ro['labels']['not']}\". "
         "Truths: two GENIE v3.04.00 tunes, G18_10a_02_11b and AR23_20i_00_000, generated for this study (no GENIE v3 "
         "events existed before it). Each truth is a gated, k-normalised shape ratio to GENIE CV per fine cell, built "
         "exactly as the C_model vertices were (cells with too few events pooled over a coarse cell or set to r = 1), "
         "applied as a truth-level reweight of the same simulation under the nominal detector response. Per truth, 20 "
         "Poisson pseudo-experiments on half the simulation and one noise-free closure, each graded against the full "
         "C_total + C_resp (ndf 16), as non-vertex truths in their own group, held-out, never pooled with the other "
         "groups. z = b / sqrt(diag(C + N)), with N the noise of the mean (N = 0 for a closure); sigma is "
         "sqrt(diag(C_total + C_resp)). The listing rule: a cell with |z| > 2, or a truth with P(chi2_16 > chi2) < 0.01. "
         "Records: " + "; ".join(recs) + ". "
         f"Group tally: {gt['cells_abs_z_gt_2']} of {gt['cells']} cells with |z| > 2 and {gt['truths_p_lt_0.01']} of "
         f"{gt['truths']} records with p < 0.01; Gaussian reference {gt['gaussian_reference_cells']:.2f} cells and "
         f"{gt['gaussian_reference_truths']:.2f} records, context only. "
         + quote("The four records are not four independent tests.", "it is printed here only as the readout records it.") + " "
         + quote("G18_10a_02_11b's 2p2h is", "partial evidence (") + "LIMITATION-PLAN.md). "
         + quote("The two truths are not two independent tests.", "combines them as independent.") + " "
         f"Control 9 passed: the 18 earlier fake-data truths grade exactly as their committed readout records them. "
         "The study is NOT CITABLE FOR: a coverage result or any statement that the intervals' coverage or width is "
         "validated; a test of the detector response; the two truths as independent tests.")
plants = {  # one strengthening per planted pair: (pair, old, new)
    "L1": [("but it cannot test the intervals' width", "and it confirms the intervals' width"),
           ("but does not test interval widths", "and confirms interval widths")],
    "A1": [("at two held-out GENIE v3 truths", "at two held-out truths")],
    "H1": [("so the two truths are partial evidence and not independent tests", "so the two truths are two independent tests"),
           ("They provide partial evidence and are not independent tests", "They are two independent tests")],
    "H2": [("0 of 4 records with p<0.01", "1 of 4 records with p<0.01")],
}
prompt_note = ("(Q4 and Q5 are additions; Q1's second sentence reports an earlier study, which BEFORE does not cover and "
               "which is not to be judged.)")
for name, plant in ((f"{PFX}.txt", False), (f"{PFX}-control.txt", True)):
    out = []
    for n, k in enumerate(("L1", "A1", "A2", "H1", "H2"), 1):
        a = new[k]
        if plant and k in plants:
            hit = [pq for pq in plants[k] if a.count(pq[0]) == 1]
            assert len(hit) == 1, (k, plants[k])
            a = a.replace(*hit[0])
        out.append(f"Q{n}.\nBEFORE: {facts}\nAFTER: {a}\n")
    open(f"{O}/{name}", "w").write(prompt_note + "\n\n" + "\n".join(out))
print("pairs written; control plants in", ", ".join(plants))
