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

## The short abstract and the introduction (the director, relaying Joseph 2026-11-16; items 22-25 to follow)

**The abstract** is the codex referee's 198-word form (absref/out.txt §3), approved by Joseph. A script checked the
rendered text word for word. The read added two changes, which Joseph approved:
- "binned unfolding at five iterations overshoots";
- "remove neither bias flag".

The abstract is now 199 words.
- **Keying:** vhalf-outcome, prr-pr3-any, prr-abs, ll5d-campaign, ll5d-alljoint and ll5d-route.
- **Retired:** LL5D_ABS_FORM.
- **Re-declared:** the listed-truth sentences. The abstract's is a count, "at two truths" (n = 2); the introduction's is
  a count plus n.

**The read (independent, read-only) of the abstract and the introduction:**
- **The abstract, sentence by sentence:** PASS, except one defect: IBU overshoots only at five iterations. The
  readout's IBU ρ is +0.23 and +0.36 at one iteration and +0.07 and +0.10 at two, and turns negative from three.
  Fixed as Joseph approved.
- **(a)** "Coverage tests omit some reported uncertainty terms" is true for the 2D test: COV2D-DECLARATION.md:214,
  "C_PL_R ... not in the graded matrix", and :221. The body's 2D-test sentence now says the run-period block "was
  neither drawn nor included in the graded covariance".
- **(b)** The bias-half sentence states a measured inequality and needs no "descriptive". Two body gaps go to
  journal-editor's F5 pass, on the director's ruling:
  - Table 1's caption defines "Descriptive" for the second 5D test only;
  - Supplement :1247 calls the bias-half rule "graded".
- **"Remove neither":** checked against readout.json. Every FD-PRR OmniFold level, B0 included, has grade.flagged true
  at both A7_gibuu and q3, and prr_levels_values asserts it. IBU at five iterations, the comparison method, unflags q3.
- **The introduction's additions** were fixed as the read proposed:
  - "at five iterations";
  - the screen sentence placed before IBU, so that "also" refers correctly;
  - "the five-observable test that gave a result", because the introduction never names a first test.

**The style gate:**
- **The abstract** is re-based: wps 11 against the base's 16.4 and the references' 17.3-22.8. Lower is the gate's
  direction.
- **The body:** check_style counted case-arm keys as words and hid sentence ends behind them. 220ddf41f fixes that,
  with a self-test and a mutant; the director approved it. The body is now 20.0 against 20.1.

**The read of items 22-25's three texts** (independent, read-only):
- **"At the two flagged truths, binned unfolding at five iterations overshoots ...": PASS.** IBU K5 ρ is −0.116 at
  A7_gibuu and −0.130 at q3 (s991000). A7_gibuu is negative on all five splits. sec:prr defines ρ < 0 as passing the
  truth along the prior-to-truth direction.
- **"Tested settings change prior retention but remove neither bias flag": the facts PASS; minor scope note, not
  applied.** Every OmniFold level stays flagged at both truths, and ρ moves past the threshold for K2 at q3 and for C25
  and O2 at both truths. But S8.2 says "For IBU the study varies the iterations", and IBU at K5 unflags q3, so a reader
  could count IBU as a tested setting. The read proposes "Tested settings of the five-observable estimator change
  prior retention but remove neither bias flag" (203 words), for Joseph via the director.
- **app_release.tex:9: minor note, not applied.** "Extended" reads as additions only, but B′ replaces RC7's text panel.
  The read proposes "... extended to draw this analysis's band and, in place of RC7's text panel, the distribution of
  standardized bin differences", for the director. RL-25's row already says "in place of the text panel".
