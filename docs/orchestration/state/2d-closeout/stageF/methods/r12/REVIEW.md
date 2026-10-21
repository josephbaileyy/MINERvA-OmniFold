# Adversarial review: register round r12 (methods paper rewrite)

Reviewer: independent, read-only. Nothing in either worktree was edited.

## What was compared

**Before.**
- Source: `S/wt-reg1/docs/analysis-note/paper_body.tex`. It is byte-identical to `wt-reg2` HEAD (`1a74560c`) and to the writer's `paper_body.before.tex`.
- PDF: `S/methods-final-v3/main_paper.pdf`.

**After.**
- Source: the `S/wt-reg2` working tree.
- PDFs: `S/plain-language/builds/r12/repo/docs/analysis-note/main_paper.pdf` (sha256 `4051f1a6…`) and `main_note.pdf` (`f5e54274…`). Both hashes equal the build receipt in `build_final.out`.
- The r12 build tree's `.tex` files are byte-identical to the `wt-reg2` working tree for all five changed files.

**Method.**
- All text was extracted with `pdftotext` (raw and `-layout`) into `S/rv-r12/`.
- My scripts are in `S/rv-r12-tools/`:
  - `nums.py` and `nums2.py`: number survival, with and without context;
  - `words.py`: spelled-out counts;
  - `sents.py`: sentence diff;
  - `lims.py`: inventory of limitation sentences;
  - `heads.py` and `insec.py`: a phrase must print *inside* the numbered note section, located from `main_note.aux` and the PDF headings.
- The writer's ledger and REPORT were read only as claims to test.

**Line references.** `A:n` is `wt-reg2/docs/analysis-note/paper_body.tex` line n. `B:n` is the same file in `wt-reg1`.

---

## BLOCKING

### B1. V A now asserts agreement of the central values, not only of their normalizations (strengthened claim)
- **Before (B:718–720):** "Each higher-dimensional central value is checked against the lower-dimensional result it extends. The three-, four-, and five-observable marginal normalizations agree at the approximately 1–2% level."
- **After (A:473–475):** "Each higher-dimensional central value agrees with the lower-dimensional result it extends: the three-, four-, and five-observable marginal normalizations agree at the approximately 1–2% level."
- **Why it blocks:** the evidence is agreement of the marginal normalizations only. The first clause now claims agreement of each central value with no qualification. Read alone, it covers shape as well. It also sits uneasily beside V C ("Agreement in the marginal normalizations thus coexists with substantial residual bias").
- **Fix:** "Each higher-dimensional central value is checked against the lower-dimensional result it extends: the three-, four-, and five-observable marginal normalizations agree at the approximately 1–2% level."

### B2. The five-iteration statement lost its scope. It now reads as a general fact that the paper and the note contradict
- **Before (B:426–428):** "For the joint-test estimator, five iterations were kept under a rule set before the comparison, because 10, 15, or 20 did not reduce the model dependence."
- **After (A:289–290):** "…(Sec. V); 10, 15, or 20 iterations do not reduce its model dependence, so it keeps five."
- **Why it blocks:**
  - The source, `RECORD-20260927-s5p-stage2-exit.md` §2 K and §3, says "do not reduce the model dependence **at the rule's resolution**". The operative quantity is M, the maximum over the development truths of the median |bias|/|departure|.
  - The note's §9.4 prints "D1 and W1 improve slowly".
  - The paper's own V B prints "thirty iterations reduce the Eavail residual by 26 %".
  - Removing "under a rule set before the comparison" removed the only words that scoped "model dependence" to that metric. As read, the sentence is now false for D1 and W1.
  - The paper also gives no pointer to §9.4, where the rule now prints.
- **Fix:** "…; it keeps five iterations under a rule fixed before the comparison, because 10, 15, or 20 did not reduce the rule's measure of model dependence, the largest residual ratio over the development truth changes (Ref. [14], Sec. 9.4)."
- **On the writer's open item 2, the attribution is correct.** Amendment 2 (`state/s5p/contract-amendment-2-stage2-studies.json`, `configuration_selection_rule.configuration_2`) defines configuration 2 as "R with B0 classifiers and K2 iterations". R is the contract's baseline estimator: the 400-tree, 31-leaf Stay-Positive refinement on 100/8 OmniFold classifiers, which is the paper's configuration (e). Study K is noise-free with no background, "so R and B0 coincide".
  - So the "baseline-capacity configuration" of the record *is* the joint-test estimator at its own OmniFold capacity.
  - The rule's set {10, 15, 20} is the amendment's grid cut by K_afford ≈ 20.
  - The note addition at `sec_5d.tex:306–310` is accurate. It prints in §9.4.

### B3. The 2D rebuilt band now reads as if it were the quoted statistical block (guardrail)
- **Before (B:672–680):** "…The band was then rebuilt. Rescoring the same pseudo-experiments against the rebuilt band removes the tail undercoverage … The rebuilt band has not been tested on independent pseudo-experiments, and the quoted statistical block is a different ensemble from it."
- **After (A:439–449):** "Neither this block nor the total has had a coverage test. In 100 closure pseudo-experiments at a fixed truth, an earlier version of the statistical band undercovered in its tails … Rescoring the same pseudo-experiments against the rebuilt band removes the tail undercoverage: 97.7 % … Because the simulated part of the rebuilt band reuses the resampling mechanism …, this rescoring is not an independent coverage test (Ref. [14], Sec. 5.2)."
- **Why it blocks:** the paragraph opens with the quoted block and then speaks of "an earlier version of the statistical band" and "the rebuilt band". A reader will take the rebuilt band to be the quoted block, with its tails repaired, and will take "neither … has had a coverage test" to be a technicality.
  - The note's §5.2 says otherwise: "The quoted statistical block is now a different ensemble, 300 replicas at the central value's seed (§4.2). This section's result is for the earlier band and was not re-tested."
  - That qualifier was what kept the paragraph true as read.
- **Fix:** after the rescoring sentence, add "The rebuilt band is not the quoted block, which is a separate 300-replica ensemble; neither has been tested on independent pseudo-experiments."

### B4. The 135 MeV limitation left the paper with no pointer, and the note refuses the reading the paper now invites
- **Before (B:238–241):** "…changes no true-Eavail bin by more than 1.05 %; this effect has not been compared with the full covariance."
- **After (A:177–180):** "…changes no true-Eavail bin by more than 1.05 %." There is no pointer.
- **Why it blocks:**
  - The limitation prints only in note §7.1: "The effect is measured but has not been assessed against the projection of the scalar-5D covariance in use. Its materiality is not established, and this note does not call it immaterial."
  - With the caveat gone, the two small numbers read as a demonstration of immateriality. That is precisely the reading the note refuses.
  - The writer dropped the pointer because §7.1 does not print 0.67 % and 1.05 % (open item 5). But the pointer is owed for the *limitation*, not for the numbers.
- **Fix:** "…by more than 1.05 %; this effect has not been assessed against the covariance (Ref. [14], Sec. 7.1)."

---

## SHOULD-FIX

### S1. The post-hoc label on the GENIE CV projection non-rejection is gone from the paper
- **Before:**
  - B:1375–1376: "(p = 0.48 in total, 0.63 in shape; a post hoc observation), so the information that rejects it involves the hadronic axes".
  - B:1318–1319: "…is a post hoc observation."
- **After (A:944–946):** "(p = 0.48 in total, 0.63 in shape), so the information that rejects it involves the hadronic axes". The label prints nowhere in the paper.
- **Why:**
  - The label prints in note §10.3 and §10.7. The paper reaches it only indirectly, via "(Sec. VII E)" and then "Ref. [14], Sec. 10.7".
  - Without it, the inference drawn in condition (ii) reads as a pre-specified result.
- **Fix:** restore "; a post hoc observation" inside the parenthesis. It costs four words.

### S2. The coverage verdict was narrowed from "the tested truths" to the rate change
- **Before:**
  - B:794: "An end-to-end coverage test … failed the acceptance criterion set before the test (Fig. 4)."
  - B:828–829: "These intervals therefore miscover at the tested truths, and no frequentist coverage is claimed…"
- **After:**
  - A:520–523: "Statistical intervals from configuration (c), corrected for the estimator's closure bias at nominal truth, miscover when the true signal rate is lowered by about 10 % (Fig. 4)."
  - Later: "No frequentist coverage is therefore claimed…"
- **Why:**
  - Note §9.5 says: "It failed its predeclared futility criterion at the nominal truth and under a 10% reduction of the signal rate."
  - Fig. 4's caption still says two integrals lie below 0.94 at nominal truth.
  - The text now implies the failure occurs only under the rate change. That is better than the evidence.
- **Fix:** "…miscover at the tested truths, most strongly when the true signal rate is lowered by about 10 % (Fig. 4)", or restore "failed the acceptance criterion".

### S3. Condition (iv): D is called an upper bound, but it was measured on the mean only
- **Before (B:1416–1419):** "…at most about 0.07 null standard deviations but not always consistent with zero, enters as the upper-bound shift described above. That shift was measured for the mean only, in a process without noise or nuisance draws."
- **After (A:966–968):** "…at most about 0.07 null standard deviations, enters as the upper-bound shift D."
- **Why:**
  - The facts print in §10.4, to which the heading points.
  - But "upper-bound shift" without "measured for the mean only" reads as a bound on the shift of the whole null distribution.
- **Fix:** append "; it was measured for the mean only, without noise or nuisance draws".

### S4. The GiBUU energy-non-conservation caveat left the paper, and it bears on a tested prediction
- **Before (B:1466–1469):** "GiBUU's deep-inelastic events on hydrogen do not conserve energy, for a cause not identified, which may lower their available energy in that replay and possibly affects its carbon prediction as well."
- **After:** removed.
- **Why:**
  - It prints in §10.9, and the paper's pointer is correct.
  - But it qualifies both "Correcting both predictions … moves both toward the data", for the GiBUU replay, and the GiBUU 2019 prediction that Table IV actually tests.
- **Fix:** keep one clause: "the GiBUU replay, and possibly its carbon prediction, is affected by deep-inelastic events on hydrogen that do not conserve energy".

### S5. Missing pointers: each moved fact prints in the note, but the paper does not point to it
The rule says the paper must point to where a moved fact prints. I checked each target inside the section's own PDF page range.

| Paper site | Moved fact | Prints in |
|---|---|---|
| V A (A:476–479) | the 3D and 4D closures had no threshold set in advance | §5.1 table: "no predeclared threshold" for both; §9.1 table |
| IV A (A:358–365) | the exact-split seed spread is unmeasured; the LightGBM central value replaced the exact-split one on 2026-10-11 | §3.2 |
| III (A:282–285) | the central values were produced before the purity bias was found and were not regenerated | §3.2 |
| V B (A:501–503) | the 74 % cell's cross-section share was not recorded | §9.2 (the new addition) |
| III (A:289–290) | the iteration rule | §9.4 (see B2) |

**Fix:** add "(Ref. [14], Sec. N)" at each site.

### S6. Table III shows "—" where the source has values
- **After (A:737–738):** at 200 iterations, NuWro/GENIE in (pT, p∥, Eavail) and q3 at fixed (Eavail, W) print "—".
- **Source:** D-ID `REPORT.md` §9.3 gives K = 200 medians for them: W3 4.4 % and q3 6.6 %. Note §9.3 omits them.
- **Why:** a dash reads as "not computed". The table's other entries all match note §9.3 and the D-ID report:
  - trees: 9.5, 5.4, 5.6, 4.3;
  - exact binned at K = 5: 8.3, 5.4, 4.9, 5.3;
  - at 10⁵ iterations: 0.8, 2.8, 8.9, 6.7;
  - at 200 iterations: 3.3, 3.3.
- **Fix:** add 4.4 and 6.6 to note §9.3 and to the table, or caption the dash "not quoted in Ref. [14]".

### S7. Section VI: the populations behind "15 of the 144" and "(121)" are not stated
- **After (A:700–703):** "The tree approximation dominates only 15 of the 144 residuals analysed; most of them (121) lie in quantities that the binned response constrains weakly…"
- **Source:** note §9.3 says "Of the 144 eligible residuals, pooled over the deformations, 15 are dominated by the tree approximation, 2 of them in identified quantities, a share of 0.014. Most of the 144 (121)…". D-ID §9.2 and §9.3 say 144 = 376 − 232, and §11 says "approximation-dominated for 15 of 144 eligible J functionals".
- **What is right:**
  - "15" and "121" are described as the source describes them.
  - The 144 and the 121 are one population.
  - Table III's medians are over the same 109 cells.
- **Two defects:**
  1. The reader sees "109 joint cells", then "144 residuals", and is not told that 144 counts cell-and-truth-change pairs. It is pooled over five truth changes, including W2, which is not in the table, and it is the 38 % quoted two sentences later.
  2. "most of them (121)" has an ambiguous antecedent, since "them" could be the 15.
- **Fix:** "…dominates only 15 of the 144 cell-and-truth-change residuals with a resolution-stable diagnosis (pooled over five truth changes); most of the 144 (121) lie in quantities…". The A share of 0.014 can stay in the note.

### S8. The neutron-mass W check reads as if it was done for every prediction
- **After (A:215–218):** "…which changes their coarse-cell predictions by at most about one Monte Carlo standard error in each cell where this was evaluated".
- **Before:** "(GENIE CV and NuWro without their 50–100 GeV samples; not at cell level for GENIE + MEC; not evaluable for GiBUU)".
- **Why:** the sentence is true, and the scope prints in §8.1, which is pointed to. But "their" covers GiBUU, for which the check was impossible.
- **Fix:** add "(not evaluable for GiBUU)".

### S9. Carry-forward: xr-hyper and the version of the cited note
- `main_paper.tex:22–28`. The 38 printed section numbers come from `main_note.aux`.
- An arXiv or PRD source without that file prints "??".
- Ref. [14] points to the note's repository `tree/main`, so the numbers can drift silently when the note changes.
- **Fix:** hard-code the numbers in the submission source, or ship the aux file, and pin [14] to a tag.
- I checked all 36 `\nsec`/`\napp` targets, plus "Secs. 8.1 and 8.2" and "Secs. 7.7 and 7.8". Every one resolves to the correct section, including the 10.5 paragraphs (κ scan and power), which sit inside "10.5 Decisions".

---

## NIT

- **N1.** Condition (ii) dropped "which has been checked only for the symmetry of its endpoints" (B:1365). It prints in §10.4, and the heading points there. "Linear surrogate" is supported by §10.4.
- **N2.** Condition (i) dropped that the design-review rate is undocumented (B:1351–1353). It prints in §10.4: "a design-review value whose calculation is not recorded".
- **N3.** A:678 "Three results indicate that…" replaces "point to". It is marginally firmer. Consider "suggest that".
- **N4.** Table III typography:
  - it is 11.4 pt overfull (`main_paper.log:632`, A:729–741);
  - the "200" column sits flush against "exact binned", so rows read "8.3 3.3".
  - **Fix:** use `@{}lrr@{\qquad}rr@{}` or similar spacing.
- **N5.** The Table III caption says "noise-free, signal-only", but the pooled counts include W2, whose boosted-tree comparator is background-inclusive. Note §9.3 discloses this, and the outcome is unchanged without W2. Add "(W2's comparator includes background; the counts are unchanged without it)".
- **N6.** The scope paragraph dropped "two predictions are for carbon, the data for CH (Sec. II)" and "we quote no covariance-based generator significance for them". Both still print elsewhere in the paper (Sec. II and V D).
- **N7.** V E's first sentence dropped "within the study's rules and computing budget". The statement stays true for "tested" definitions, and the paragraph ends with a pointer to §9.4.
- **N8. Pre-existing, not introduced by r12.**
  - Note §9.2 says the GiBUU/GENIE ratio "is not a measured GiBUU–GENIE difference" (mis-sampled flux, §7.6).
  - Paper V B calls it a change "as large as the difference between generators".
  - Worth a separate check.

---

## Direction A: residue

**Numbers.**
- Before-paper prose and tables hold 709 numeric tokens with 229 distinct values. I also checked spelled-out counts.
- Checked in context, at least three neighbouring words within ±150 characters, all but the following survive in the after paper.
- **Moved, and verified in the note:**
  - "50–100 GeV" → §8.1;
  - "0.8902 α < 0.9 α" → §10.3 and App. B.5;
  - "8.3 % against 9.5 %" → now Table III.
- **Dropped as redundant:** "(separate from the one in use)". "Further covariances" carries it.
- **Not lost:** Table IV (formerly III) is identical. All ten CI strings diff equal, and B, k, p and the thresholds match.
- **Changed values:** none.
- **New numbers:** 144, 121 and the Table III entries. All trace to note §9.3 and D-ID §9.3. The one gap is S6.

**Limitations.**
- `lims.py` found 109 limitation-bearing sentences in the before paper. I read the whole before paper and traced each limitation or disclosure that was removed or reworded: about 38 distinct items.
- I opened every target in the after-note PDF text, inside the section range. All print where the ledger says, except:
  - 135 MeV (B4): it prints in §7.1, but nothing points there;
  - the five items in S5: they print, but are not pointed to.
- Statements removed because they *strengthened* the paper are acceptable and were not flagged: "selected before the joint-test design was fixed", "fixed in advance", "specified in advance", "criterion fixed before it ran".

**Guardrail cases where removal changes how a remaining sentence reads:** B2, B3 and B4 (false or misleading as read), and S1–S4 and S8 (stronger as read). The writer's list of 15 kept qualifiers is accurate; I confirmed every one prints.

## Direction B: additions

- **The four note additions.**
  - All four print in the intended sections: §8.2, §9.2, §9.4 and §10.7.
  - All four match their sources:
    - the degeneracy sentence is the old paper sentence verbatim;
    - the 74 % cell is EW index 29, which is Eavail 0.8–1.5 and W ≥ 3, as stated;
    - the iteration rule matches amendment 2, as discussed under B2;
    - "powers not compared" is the old paper clause.
- **Protected text.**
  - `main_paper.tex` changed only in the preamble (xr-hyper) and in one abstract word, "adopted" → "specified".
  - The source from `\begin{acknowledgments}` to the bibliography hashes identically in both trees (`73129e5f…`).
  - The printed text from ACKNOWLEDGMENTS to the references hashes identically in both PDFs (`45395b27…`).
  - Both `\pubhold` texts are unchanged.
  - **Byte-identical: confirmed.**

## Register: surviving development-history or bookkeeping passages (exact quotes)

Most are required disclosures. Consider recasting them as design facts rather than chronology.

1. Fig. 3: "Panel (a) uses the random seeds of the studies that developed the estimator; panel (b) uses seeds generated to assess it, which were later also used in its development."
2. Fig. 4: "its reweighting was incorrectly constructed, and the test's verdict does not depend on it."
3. IV B: "an earlier version of the statistical band undercovered in its tails" … "Rescoring the same pseudo-experiments against the rebuilt band removes the tail undercoverage".
4. VII C: "The test design was fixed before any observed statistic was computed, but after its reviewers had seen descriptive per-cell residuals of the data, and a bounded extension of the calibration's computing budget was decided while observed p values were visible".
5. VII C: "Computing time limits interrupted or prevented 224 calibration and 53 power pseudo-experiments; all were rerun afterwards".
6. VII C: "An independent recomputation of every p value and decision, with separately written code, agrees with the original evaluation."
7. Table IV: "B: null pseudo-experiments completed at the stopping point, of 1400 submitted per null (1800 for NuWro)".
8. VI: "On the same 109 joint cells and the truth changes of the estimator's development studies".
9. VII E: "these replays do not change the decisions of Table IV". "Replays" is internal jargon.
10. Table I: "coverage of an earlier band: failed" and "learner chosen after the comparison".

The data-availability text ("prepared locally but not yet deposited") is protected and was not assessed.

## New errors in the after PDF
- No "??" and no undefined references.
- Table III is overfull and its columns are cramped (N4).
- Equation (1) is 11 pt overfull; this predates r12.
- Otherwise clean.

## Writer's open items
1. Agree that the history can stay, but fix B3.
2. The attribution is correct; see B2.
3. Fine to keep. It is a register issue only (item 4 in the register list).
4. "15 of 144" is correct, but the population needs stating (S7).
5. Disagree: the pointer is owed for the limitation (B4).
6. Out of scope (protected).
7. Not checked against the 2026-10-20 decision.

---

## Verdict: ADOPT-AFTER-FIXES

The four BLOCKING fixes add a total of about 70 words. With B1–B4 and S1–S5 applied, the rewrite meets the rules.

**Checked:**
- 709 numeric tokens (229 distinct values), plus spelled-out counts;
- 109 limitation sentences, about 38 of them moved or reworded, each traced into the note PDF section;
- 119 of 296 after-paper sentences that are not verbatim, each compared with its source;
- 38 note pointers;
- the 4 note additions against their sources;
- Table III's 14 values against note §9.3 and D-ID §9.2, §9.3 and §11;
- protected text, by hash.

**Not checked:**
- the 333-row ledger, row by row;
- the rest of the 136-page note, the primer and the PET note;
- numbers printed inside figures;
- the physics of unchanged claims;
- the build scripts and `check_sec4_receipts.py`;
- whether the abstract matches the 2026-10-20 NuWro decision;
- GPT's original register complaint.

---

## Re-review (round 2, after the writer's fixes)

**Build checked.**
- `S/plain-language/builds/r12/repo/docs/analysis-note/`: `main_paper.pdf` sha256 `a7a692f7…` and `main_note.pdf` `12faf53b…`.
- The build's `.tex` files are byte-identical to the `wt-reg2` working tree for all five changed files.
- `main_paper.log`: no undefined references and no "??".
- The Table III overfull box is gone. The only remaining overfull boxes are the old ones: eq. (1) at 11 pt and 0.7 pt at lines 1034–1052.

**Method.** I diffed the first-round and revised PDF texts sentence by sentence: 54 sentences differ. I checked each changed sentence against its source in the note PDF, the D-ID report and the s5p records.

### 1. Do the fixes resolve the findings?

| Finding | New text (paper_body.tex) | Verdict |
|---|---|---|
| B1 | A:477 "Each higher-dimensional central value is checked against the lower-dimensional result it extends: …" | Resolved. |
| B2 | A:292–295 "It keeps five iterations under a rule fixed before the comparison, because 10, 15, or 20 did not reduce the rule's measure of model dependence, the largest residual proxy over the development truth changes (Ref. [14], Sec. 9.4)." | Resolved. See below. |
| B3 | A:455–456 "The rebuilt band is not the quoted block, which is a separate 300-replica ensemble; neither has been tested on independent pseudo-experiments." | Resolved. See below. |
| B4 | A:180–182 "…; its materiality has not been established, because it has not been assessed against the covariance (Ref. [14], Sec. 7.1)." | Resolved. Matches §7.1: "has not been assessed against the projection of the scalar-5D covariance in use. Its materiality is not established". |
| S1 | A:953–954 "(…; a post hoc observation)" | Resolved. |
| S2 | A:525–527 "miscover at the tested truths, most strongly when the true signal rate is lowered by about 10 %" | Resolved. Consistent with §9.5, which records a failure at nominal truth and under the rate change. |
| S3 | A:976–977 "…; it was measured for the mean only, without noise or nuisance draws." | Resolved. Matches §10.4. |
| S4 | A:1011–1013 "The GiBUU correction, and possibly its carbon prediction, is affected by deep-inelastic events on hydrogen that do not conserve energy." | Resolved. Matches §10.9: the events "do not conserve energy"; "It may also affect GiBUU's carbon prediction". |
| S5 | Pointers at A:182 (§7.1), A:286 and A:364 (§3.2), A:483 (§5.1), A:508 (§9.2), A:295 (§9.4) | Resolved. Each target prints the fact: §3.2 "were not regenerated" and the exact-split history; §5.1 table "no predeclared threshold"; §9.2 the 74 % cell and its unrecorded share. |
| S6 | Table III A:739–748: 200 iterations, W3 4.4 and q3 6.6; note `sec_5d.tex:185–186` | Resolved. D-ID `REPORT.md` §9.3, "Longer exact iteration" table: W3 K = 200 4.4 %, q3 K = 200 6.6 %. The note prints them in §9.3. |
| S7 | A:705–710 "Of the 144 cell-and-truth-change residuals above 2 % whose diagnosis is stable under the truth resolution, pooled over five truth changes, the tree approximation dominates only 15; most of the 144 (121) lie in quantities that the binned response constrains weakly…" | Resolved. See below. |
| S8 | A:219 "(it cannot be evaluated for GiBUU)" | Resolved. Matches §8.1. |
| N3 | A:684 "Three results point to…" | Reverted to the original wording. |
| N4, N5 | Table III spacing; W2 comparator clause in the caption | Resolved. Matches §9.3: "whose boosted-tree comparator includes background and without which the outcome is unchanged". |
| S9 | xr-hyper and version pinning of the cited note | Not addressed. A carry-forward for the submission source, not a defect in this build. |

**B2 in detail.** "The largest residual proxy over the development truth changes" is the rule's M.
- Amendment 2, `configuration_selection_rule.M_of_k`, defines M as "the maximum over the four development alternatives … of the noise-free median … of |bias| / |departure|".
- The note's §9.4 uses the same phrase: "the largest residual proxy over the development truths".
- The rule belongs to the joint-test estimator: configuration 2 is "R with B0 classifiers".
- "Did not reduce" is in the past tense and scoped to that measure, so it no longer conflicts with "D1 and W1 improve slowly" (§9.4) or with V B's 26 %.

**B3 in detail.** §5.2 says: "The quoted statistical block is now a different ensemble, 300 replicas at the central value's seed (§4.2)."
- "Neither has been tested on independent pseudo-experiments" is true.
- For the quoted block it is weaker than the full fact; §4.2 says it "has had no coverage test at all". But the paragraph's opening sentence already says "Neither this block nor the total has had a coverage test", so nothing is lost.

**S7 in detail.** The sentence matches D-ID §9.2, §9.3 and §11:
- 376 J functionals have |r| > 2 %;
- 232 of them are resolution-sensitive and excluded, which leaves 144 eligible, pooled over GiBUU, W1, W3, q3 and W2;
- 15 of the 144 are approximation-dominated;
- 121 of the 144 are C-counted.

The 144 is now visibly a different population from the 109 cells, and the antecedent of "most of the 144" is unambiguous.

No new loss, strengthened claim or changed number was introduced by the B or S fixes.

### 2. The register recasts

| Recast (line) | Before → after | Fact changed? |
|---|---|---|
| Table I (A:87) | "coverage of an earlier band: failed" → "an earlier band failed coverage" | No. |
| Fig. 3 (A:585–587) | "…seeds of the studies that developed the estimator; … seeds generated to assess it, which were later also used in its development" → "…seeds of the estimator's development studies; … separate assessment seeds, which also entered its later development" | No. |
| Fig. 4 (A:609–610) | "was incorrectly constructed" → "does not implement the intended change" | No. Equivalent. |
| VI (A:701) | "the truth changes of the estimator's development studies" → "the fixed truth changes used to develop the estimator" | No. §9.3 says "the fixed historical truth deformations". |
| VII C (A:905–909) | "…but after its reviewers had seen…" → "…; its reviewers had seen descriptive per-cell residuals of the data…" | No, but the timing is now only implicit. See R4. |
| VII C (A:911) | "all were rerun afterwards, and none reaches" → "rerun, none of them reaches" | No. The grammar is awkward. See R3. |
| VII C (A:913) | "An independent recomputation of every p value and decision, with separately written code, agrees with the original evaluation." → "Independently written code reproduces every p value and decision." | Not stronger than the before paper. See below. |
| VII E (A:1013–1014) | "These replays do not change the decisions of Table IV" → "These corrected evaluations do not change the decisions of Table IV" | **Yes, in effect.** See R1. |

**The independent recomputation.**
- The source is note §10.3 and the provenance appendix: "An independent recomputation of every p value and decision from the stored products, with separately written code, agrees with the production evaluation on all 1379 compared rows; it verifies the calculation, not the adequacy of the calibration" (verdict AGREE, 1379 of 1379).
- "Reproduces every p value and decision" is supported, given 1379 of 1379 rows.
- The new sentence says no more than the before paper did. Neither states the operand, "from the stored products".
- A reader could take "reproduces" to mean an independent rerun of the calibration chain. The caveat in (v)/(vi) ("The independent recomputation verifies the calculation, not whether the chain reproduces the data analysis") limits that reading.
- NIT: add the operand (R2).

### 3. Protected text

**Byte-identical: confirmed.**
- **Source:** `\begin{acknowledgments}` through `\bibliography`, sha256 `73129e5f…` in both `wt-reg1` and `wt-reg2`. The `main_paper.tex` diff is still only the xr-hyper preamble and "adopted" → "specified"; `paper_body.tex` contains no `\pubhold`.
- **Print:** the raw-text hash changed (`45395b27…` → `15563b4d…`) only because the DATA AVAILABILITY heading and the page break moved. With headings, page numbers and line-break hyphens stripped, both PDFs give `7cc936a9…`, identical word for word.

### Remaining fixes

- **R1 (SHOULD-FIX; a fact as read).**
  - **Text (A:1013–1014):** "These corrected evaluations do not change the decisions of Table IV". It follows directly after "NuWro's total-test rejection does not survive that correction robustly".
  - **Problem:** "corrected evaluations" presents the CH replays as the authoritative evaluation that confirmed the decisions. Note §10.9 says the opposite: "They are descriptive: they do not re-grade the recorded decisions of Table 12, which stand". At its frozen Holm position, NuWro's total test "would then lie 1.11 null standard deviations below its boundary, and so be undetermined".
  - **Fix:** "These descriptive replays do not re-grade the recorded decisions of Table IV (Ref. [14], Sec. 10.9)."
- **R2 (NIT).** A:913: "Independently written code, applied to the stored outputs, reproduces every p value and decision."
- **R3 (NIT).** A:911: "rerun, none of them reaches" → "when rerun, none of them reaches".
- **R4 (NIT).** A:906: "its reviewers had seen descriptive per-cell residuals of the data" → "…before it was fixed". This matches §10.3: "before it was frozen".
- **R5 (NIT).** Table III now floats to p. 9, inside Sec. VII, although it is first cited in Sec. VI on p. 7. Move the float earlier in the source, or use `[tbp]` placement.
- **Carry-forward (from S9).** Before submission, ship `main_note.aux` or hard-code the numbers, and pin Ref. [14] to a tagged note version.

### Verdict: ADOPT after R1

R1 is a one-sentence wording fix. R2–R5 are optional polish.

**Checked this round:**
- all 54 changed sentences;
- the 14 B and S fixes, plus N3, N4 and N5;
- 7 register recasts;
- the two Table III values, against D-ID §9.3;
- the B2 wording, against amendment 2 and the stage-2 exit record;
- all printed note pointers: 0 undefined;
- the protected text, in source and in print.

**Not re-checked:** the ledger update, and parts of the note outside the sections cited above.
