# Joseph's batch of 2026-11-16: the meaning reads of A5, B, F1 and F2

Decision: DECISION-20261116-joseph-paper-batch.md (PR #1181), items 2 (A5), 4 (B), 8 (F1) and 9 (F2). The director's
go and his approval of F2's text and sites (2026-11-16) are relayed messages. Each reader was an independent
general-purpose subagent, read-only.

## F2: the covariance-noise qualification (paper §6, the "conditional tests" paragraph; Supplement S8.3)

**Read 1, on the draft: REVISE.** All four fixes were adopted before the text went to the director:
- "Inflate the spread" became "make χ² and each |e_c|/σ_c larger than this null allows". Estimation noise biases χ²
  upward, because the small sample eigenvalues come out low.
- "Weakly constrained eigenmodes" became "smallest-eigenvalue directions". The old phrase can be read as the
  large-variance directions.
- "Replicas and universes" became "finite ensembles", the limitations item's phrase. The pseudo-data may share C_T's
  universes.
- Site S moved to after the test-size sentence, so that "this constructed null" follows the null's definition.
- "The verdicts stand" alone implies that they would survive a correction. Joseph's item 9 requires it, so it became
  "stand as graded under this null".

**The director's checks:**
- Each paragraph carries an absence waiver, `method scope: no Hartlap-type or other covariance-noise correction is
  applied`.
- grep of the paper, the Supplement and the LL5D and coverage records, 2026-11-16: "Hartlap" occurs only in S7's IBU
  comparison (REF-G1) and in two August search scripts for an unrelated study.
- Site S's $e^{\top}C_T^{+}e$ is S8.3's own notation (supplemental :1044).

## A5, B and F1: PASS, with two follow-on fixes adopted

- **A5:** the sentence prints only under ll5d-alljoint = all, in both status arms, after the sentence stating the joint
  flags. "Untested" holds:
  - LL5D-DECLARATION.md:322: "An under-coverage under C_T is not shown to persist under the full covariance at T";
  - the readout has no full-covariance regrade;
  - the only C_resp + C_PL,5D computation is D2's block-share bound, not a coverage test.
  <!-- absence-ok: reports the read's check of A5's scoping sentence against LL5D-DECLARATION.md:322 -->
- **B:** checked against readout.json at split 991000, with Δρ measured from B0.
  - **Increases beyond 0.05:** K2 at q3 (+0.0565; GiBUU +0.0434); C25 at both (+0.230, +0.321); O2 at both (+0.338,
    +0.214). No other level crosses, and the largest fall is −0.0307.
  - **New flags:** K2 3, C25 3, O2 6 (PR-3 new_flags), of 12 − 2 = 10 other graded truths.
  - **Noise-free:** the declaration says so at :24 and :32.
  - **W levels:** max |Δρ| over O4r, O4 and O3 is 0.0271, so "less than 0.03" holds.
  - **Fixed:** the existing next sentence, "In each case some tested level raised ρ ...", would have read as if about
    the W levels. It is replaced by "No tested level of any setting lowered ρ by as much as the threshold."
    make_values' tier1_values asserts that no level of any factor falls by the bar.
- **F1:** the 1A claim holds: q2-opendata-20261014 REPORT :27-29, and data-survey-20261022 SURVEY.md :35, where the
  other playlists match file for file by size. "The 2,374 input files" lost its owner when "its" was dropped, so it
  now reads "This analysis's 2,374 input files".
- **Not applied, for Joseph via the director:**
  - "match the current release in file size" would expose that the match is by name and size (SURVEY :272);
  - "production" in the Data availability text against "processing" in §2 and S1;
  - O4 also newly flags A7_nuwro;
  - §5.3 does not cite tab:prr-levels, which alone defines "all three learners".

## Item 14 (A1-A4, the referee's option (b)): the table entry, S row 10, the caption, §6.3 and §7

**The texts** are the decision's and answer.txt's, verbatim. Only these were substituted:
- the keyed values (tunes, cell names, and A1a.2's "float64 and float32" and "float32");
- \ssec{S8.5}{supp:study-ll5d} for "(Supplement, §S8.5)";
- section~\ref{sec:ll5d} for "(§6.2)".

The read was by an independent general-purpose subagent, read-only, on the rendered texts.

**Verdict: REVISE, one sentence that the decision does not fix; the fix is adopted.** "For the second five-observable
coverage test the finding gives one entry for each tune and variant" now contradicted the entry's "With the bands: the
same flags at each tune". It became "The finding of the second five-observable coverage test gives its flags at each
tune in each variant, the primary variant ... first".

**The facts it checked:**
- Both gates STOPped: G18 is job 61040163 and AR23 is job 61040235. Every signal and truth row was unmatched, a share
  of 1.0 in all 16 cells. The cause was w_truth stored as float64 against tdw stored as float32 (A1A2 "Under:").
- The fix rounds the key columns to float32 on both sides (A1A2 §1-2).
- The STOP fell at the gate stage, with the variance gates, gate_n, the backstop and D1-D3 visible.
- The repair changed no rule, threshold, bound or cell.
- The flags, from readout-g18.json and readout-ar23.json: G18 joint only (joint counts 12 and 14); AR23 joint and R07
  (counts 1 and 4), against a threshold of 195. ll5d-sameflags is "same".
- Every reading has 4 to 6 over-covering cells.
- **The §6.3 pointer:** S8.5's repaired case prints the route record and "Its readings are therefore descriptive."

**Notes, not applied (for Joseph via the director):**
- The decided texts mix "STOP" (table, caption, §6.3, §7, limitation 5) with "stop" (the abstract's former referee
  form, and the Supplement).
- The first "STOP" a reader meets is in the Table 1 caption.
- §6.3's per-variant sentence states the same flags twice.

**The abstract:** it is left as at 11aa69d8b, on the director's instruction of 2026-11-16, because Joseph has not
approved it and a referee is reading the whole abstract. Two measurements are kept for that ruling:
- the referee form rendered at 249 words;
- the style gate needs both its semicolon and its colon split, which gives a words-per-sentence of 18.5 against the
  base's 18.5.

## Item 15 (Fig. 1 version B'): the caption

**The read** was by an independent general-purpose subagent, on the rendered caption, the PDF (ef466621) and make_figs
9a575b36's fig1(). **Verdict: PASS.**
- Every caption statement is drawn: the r_i map on equal-size cells with unreported cells grey; the colour bar titled
  r_i at ±3, with no r_i clipped; and hist(pull[m]) of the 205 values with no reference curve, labelled
  "205 bins / mean 0.060 / SD 0.535".
- r_i is defined once, at bottom left.
- **The two medians** are both over the 205 reported bins:
  - ours is q2d-sigma-med, data_g2r.json readings.sigma.median_pct[1] = 6.463025, equal to route A's uqmedian.tex;
  - the published one is 100 median(sqrt(diag cov_total)/paper_v) over mask_reported = 6.8525, which is uqPaper, 6.85.
- **Adopted (optional):** the band sentence had "the four-block covariance of section~\ref{sec:cov16}, without
  C_model", which can be read as the sixteen-cell C_rep minus one term. It now reads "the two-dimensional covariance of
  section~\ref{sec:cov16}, the sum of four blocks without C_model".
