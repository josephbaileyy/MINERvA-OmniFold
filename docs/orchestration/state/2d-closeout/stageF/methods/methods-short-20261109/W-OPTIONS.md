# The short methods paper: wording options for the director's W-items (2026-11-09)

**Recorded by** `director-helper-3`, for the director's independent read and decision under Joseph's away delegation
(`DECISION-20261109-joseph-away-wording-delegation.md`).

**What this covers:** W-1 to W-8, W-11 to W-18, W-20, W-22 and W-23. W-9, W-10, W-19 and W-21 are banked for Joseph
and are not here.

**The text quoted** is the draft at this file's commit, on PR #977, by section. It is not quoted by line, because
lines move.

**For each item:**
- **"Current"** is what the draft prints now.
- The options are in recommendation order, **with mine first**.
- **"Rests on"** gives the records at file:line.

**The paths and sources:**
- Paths under `state/` are relative to `docs/orchestration/`.
- "the consult" is `state/2d-closeout/stageF/methods/secondary-results/consult-astra-publishable-path-20261109/answer.txt`.
- "R6" is `state/2d-closeout/stageF/methods/secondary-results/referee-methods-round6-20261109/` on #982. Its four
  reports are cited as S1, S2, G1 and G2:
  - S1: `sonnet-jinst-short-r6-1.txt`
  - S2: `sonnet-jinst-short-r6-2.txt`
  - G1: `gemini-jinst-short-r6-1.txt`
  - G2: `gemini-jinst-short-r6-2.txt`
- "the decision" is `DECISION-20261109-joseph-methods-baseline-and-plan.md` at `943d5f97` (#976).
- "the editor" is journal-editor's read of `e3b99c82b`, items as in `QUEUE-editor-1.md`.

---

## W-1. The title

- **Current:** "Five-observable unbinned unfolding of MINERvA open data with OmniFold: a methods and validation
  study".
- **Options:**
  1. **(Recommended)** "Five-observable unbinned unfolding of MINERvA open data with OmniFold: what is recovered,
     what is retained from the prior, and what is stable".
     - It names the three findings.
     - It drops "validation", which the director's round-6 item 4 rules out of the title. S1 also asks the title to
       follow the paper's own "not a blind validation" (S1 `:40`, `:97`).
  2. "Five-observable unbinned unfolding of MINERvA open data with OmniFold: a methods study of prior retention,
     numerical stability and uncertainty calibration". This is longer and closer to S2's summary (S2 `:121`).
  3. Keep the current title. Against it: item 4, and S1 `:40`.
- **Rests on:**
  - the decision's item 2, "a short methods-and-validation paper", which names the paper type and not the title;
  - S1 `:40`, `:111` ("what would become disqualifying is claiming a validation");
  - the intro's first scope sentence, "a methods and validation study", which follows this choice (W-1 covers both).

## W-2. The abstract's finding sentences

- **Current:** the method; "Three findings follow."; the benchmark sentence; the prior-retention sentence, plus the
  pending clause (now its own sentence, per the editor's C1); the stability sentence with the ensemble; the calibration
  sentence (see W-11), plus the pending like-for-like clause, also its own sentence; and the illustration sentence.
- **Options:**
  1. **(Recommended)** Keep the structure with fewer numbers.
     - Keep 1 %, 2.6 and the ensemble's "1 of 17".
     - Drop "over many eigenmodes of the published covariance" and the criteria in parentheses, which §3.3 gives.

     S1's minor 1 (`:115`) and S2's minor 1 (`:105`) call the abstract overloaded with numbers.
  2. Add the size of the rounding effect on the reported cells: a median 0.133 % of the cross section. S1 asks for
     this (`:63`: "Add the 16-cell result and the ratio to the total uncertainty"). It adds one clause.
  3. Keep the abstract as it is.
- **Rests on:** S1 `:63`, `:115`; S2 `:105`; the editor's C2 (one clause for the like-for-like test).

## W-3. V-HALF beside, or instead of, the two earlier validity rules

- **Current:** §5.4 gives a one-sentence summary of V-ATLAS and V-PRIOR (14 of 16 cells each, 12 under both, pointing to
  S11), then V-HALF's definition and its pending counts.
- **Options:**
  1. **(Recommended)** Beside, as drafted. The summary keeps finished content in the paper if V-HALF is late (the
     editor's A5), and the full rules stay in S11.
  2. V-HALF alone in the paper, with V-ATLAS and V-PRIOR only in S11.
  3. All three rules in the Supplement, with one sentence in the paper. S2 classes the rules as "(c), detail for the
     note" (S2 `:92`).
- **Rests on:**
  - `DECISION-20261109-joseph-bias-half-rule.md:31-35`, `:49`;
  - `OUTCOME-20261107-valid-region.md:43-45`, `:129`;
  - S2 `:92`.

## W-4. Naming the ensemble's bias–variance study as the basis for the adoption question

- **Current:** not named. §6.1 says the ensemble "is not adopted" and that it "is a tested mitigation of the
  instability, not a replacement".
- **Weighed, as the director asked:** three of the four reads ask exactly for a bias–variance or explicit adoption
  rule:
  - S1 `:66`: "Either adopt the ensemble … or explain why a single-truth criterion governs";
  - S2 `:45`: "State the bias differences quantitatively and justify the rule, or revise it";
  - G2 `:59-63`, which offers adopting it as option 1.

  G1 asks too (`:51-52`). The consult recommends exactly that study (the consult `:25`, `:58`), and the decision
  schedules it (item 4, `:59-66`).
- **Options:**
  1. **(Recommended)** One sentence in §6.1, after "not adopted": "Whether a small bias increase is an acceptable
     price for the stability gain is a bias–variance question, which a separate study, specified in advance at truths
     reserved from this one, is to address; this paper's conclusions do not depend on it." This states the basis the
     reads ask for. It claims no result, and it keeps the decision's rule that "nothing about it enters this paper".
  2. The same sentence in §7's next-steps paragraph instead of §6.1, which keeps §6.1 to results.
  3. Not named. Against it: the reads say the rejection looks arbitrary without a stated basis.
- **Rests on:** the decision's item 4 (`:59-66`): "the initial methods paper neither waits on it nor changes because
  of it". Option 1 states its existence and basis only. Also `OUTCOME-20261109-ens1-stab-pass-bias-worse.md:53-71`, the
  CITABLE FOR and NOT CITABLE FOR, which allow no ranking beyond the verdict.

## W-5. The localization next step, and whether a list of what is not claimed is printed

- **Current:** §7's paragraph "These results bound what the study shows. …". It gives the three exclusions as prose,
  and calls the localization test "the natural next step".
- **Options:**
  1. **(Recommended)** Keep the prose, which is the editor's A6.
  2. A short printed list, "This study does not establish: …". Against it: the editor says it reads as internal and
     plants the strong claims.
  3. Drop the "next step" sentence, keeping only "not established".
- **Rests on:** the decision's item 6 (`:73-78`): "until then it is a stated next step"; the consult `:15-17`;
  `OUTCOME-20261107-valid-region.md` (no localization conclusion; the consult `:17` cites `:23,36,98-124`).

## W-6. "Illustration only" in the abstract

- **Current:** "The five-observable output on data is therefore given only as an illustration." §7 now says
  "illustration" too; the editor's B13 replaced "demonstration".
- **Options:**
  1. **(Recommended)** Keep it. Three reads accept the illustrative framing explicitly (S1 `:111`, G1 `:114`, G2 `:137`), and
     S1 asks for "illustrative output" consistently (`:126`).
  2. Drop it from the abstract and keep it in §1 and §7.
- **Rests on:** round 5's abstract; R6 README, "What the reads agree on".

## W-7. The per-learner χ² values in §4.1

- **Current:** "with purity-based subtraction, their χ²/ndf values were 3.66 (scikit-learn exact-split), 2.65
  (LightGBM) and 2.70 (scikit-learn histogram, a mean over ten seeds), so the distance depends on the estimator".
- **Options:**
  1. **(Recommended)** Keep the values in the paper. G1's issue 4 (`:47`) asks for exactly this in the main text,
     "not only in the Supplement". The editor's B2 says the selection effect can't be sized without them.
  2. Move them to S4, which already carries them, and keep only the clause "the distance depends on the estimator".
- **Rests on:** `values.tex:48`, `:81` (`\chiPaperExact`, `\chiPaperPurity`); r5:156; G1 `:47`.

## W-8. "Declared" inside the approved B0 and RS1 sentences

- **Current:** the printed paper has no "declared" (check_round's GONE list). The B0 sentences and RS1's licensed
  clauses are verbatim. Their remaining process words are "below a tenth of any total uncertainty" and "rounding-level
  perturbation". G2 calls the register an audit log (`:143`), and S2 says pre-registration language "loses force"
  (`:114`).
- **Options:**
  1. **(Recommended)** Keep the approved sentences verbatim. They are Joseph's (B0) or licensed (RS1); changing them
     needs Joseph.
  2. Ask Joseph for a register pass on the B0 sentences only, with the same claims.
- **Rests on:** `DECISION-20261106-joseph-b0-reconciliation-sentence.md`; `OUTCOME-20261108-rs1-rounding-mechanism.md:54`ff,
  `:126`.

## W-11. The abstract's calibration sentence

<!-- absence-ok: this section quotes draft wording options for the director's decision; it states no finding that a result does not exist -->

- **Current:** "The uncertainties are not calibrated: the two-dimensional covariance under-covers at two held-out
  generator tunes."
- **Options:**
  1. **(Recommended, the editor's wording)** "The calibration of the uncertainties is not established: the
     two-dimensional covariance under-covers at two held-out generator tunes, and no five-observable coverage test has
     run to a result." The current text goes beyond COV2D's NOT CITABLE FOR. Two reads say the same: S1 `:53` ("must
     be restricted to 2D"), S2 `:59`.
  <!-- absence-ok: quoted draft wording for the director's decision; the record it rests on is cited in this item -->
  2. "The two-dimensional covariance under-covers at two held-out generator tunes; the five-observable intervals have
     not been tested for coverage." This drops the generalization altogether.
  <!-- absence-ok: quoted draft wording for the director's decision; the record it rests on is cited in this item -->
  3. Keep the current text. Against it: COV2D's licence, and §1 and Limitation 1 of this paper.
- **Rests on:** `OUTCOME-20261108-cov2d-both-tunes-under-cover.md:97-106` (CITABLE FOR), `:108-110` (NOT CITABLE FOR:
  "Coverage of the reported intervals at the data's point"; "A coverage rate"). The like-for-like variant clause stays
  under every option.

## W-12. "Tracks the same bias" (§7, second paragraph)

- **Current:** "The second is the shift of the data result when the simulation's prior is reweighted to generator-sized
  changes of the truth, which tracks the same bias (ref. [14], section 9.4). The note's calibrated tests of the
  predictions show the same bias toward the prior (ref. [14], section 11.5)."
- **Options:**
  1. **(Recommended)** "…, which is consistent with the same bias (ref. [14], section 9.4); the note's calibrated tests
     of the predictions are consistent with it too (ref. [14], section 11.5)." The paper presents neither result, so
     the weaker verb is what a reader can check (the editor's A3).
  2. Drop both sentences, and keep the first finding, the residual of section 5.1, as the paper's evidence.
  3. Keep the current text.
- **Rests on:** r5:319, whose sources are at `bc8673186`; the note's `sec_5d.tex` `sec:gbdt-model-dependence` and
  `sec_joint.tex` `sec:joint5d-results`. Their CITABLE FOR should be re-read for the exact verb before deciding.

## W-13. "Run-period consistency" among what the method does not provide (§7, first paragraph)

- **Current:** "It does not yet provide validated interval coverage, numerical stability, recovery of every
  generator-sized truth change tested within the reported uncertainty, or run-period consistency".
- **Options:**
  1. **(Recommended, the editor's A4)** End the list at "…within the reported uncertainty", then add: "and the data
     show a run-period inconsistency, present before unfolding, of unknown cause". The step is in the reconstructed
     data (§4.2; Table 1, "In data").
  2. Keep it in the list, adding "(a property of the data, section 4.2)".
- **Rests on:** `state/2d-closeout/period-unfold-20261014/REPORT.md:3`, `:63-64` (r5:196's comment); §4.2.

## W-14. "Applying the thresholds of the usage recommendations of ref. [5]" (§5.4)

- **Current:** "one applying the thresholds of the usage recommendations of ref. [5]".
- **Options:**
  1. **(Recommended)** "one implementing three of the per-cell thresholds of the usage recommendations of ref. [5], whose
     fourth recommendation, a test of correlation assumptions on pseudo-data, is not met here". This uses the record's
     own count: A1–A3 are applied, and guide item 5 is not met.
  2. "one based on the usage recommendations of ref. [5]", with the detail left to S11.
- **Rests on:** `OUTCOME-20261107-valid-region.md:35`, `:43-45`, `:56` ("Guide item 5 is not met"); r5:274.
  **Check before printing "fourth":** the record numbers it "item 5", so the count of recommendations should be read
  from the guide itself.

## W-15. The residual compared with a covariance that failed acceptance (§5.1, and Fig. 3(b)'s band)

- **Current:** "… lies within the quoted total uncertainty in about half of those cells. Those uncertainties come from
  an earlier purity-subtracted five-observable covariance that fails its specified acceptance criteria." Fig. 3(b)
  draws that covariance's band.
- **Options:**
  1. **(Recommended)** Drop the comparison sentence and the band, and keep the residual's size, 16–31 %. Both Sonnet
     reads object: S1 `:30` ("not evidence about the reported result"), S2 `:40`. A comparison with a covariance that
     failed acceptance carries no information about the reported one.
     - `check_sec4_receipts.py` anchors "about half of those cells", so the check's VERBAL row must be retired with
       it.
     - Fig. 3(b) needs a redraw without the band. That is a figure-code change.
  2. Keep both, with a reason added: "shown for scale only; that covariance is not the reported one".
  3. Keep the current text.
- **Rests on:** r5:218 and its comment (VL154: 20 of 42); `nsec{sec:eavailw-adopted}`; S1 `:30`; S2 `:40`.

## W-16. "Bitwise independent of its training seed" in the abstract

- **Current:** "The estimator is reproducible, bitwise independent of its training seed, but not numerically stable".
- **Options:**
  1. **(Recommended)** "…, bitwise independent of its training seed in the unfolds we ran, …" restores §6.1's own
     qualifier (the editor's A7).
  2. Also add why: "a consequence of training on the full sample without subsampling". S1 says it "is not a robustness
     virtue" (`:64`).
- **Rests on:** r5:230 ("in the unfolds we ran"); S1 `:64`, `:118`.

## W-17. "Multidifferential neutrino measurements on data reach three dimensions"

- **Current:** the last sentence of the intro's first paragraph, just before "This paper is a … study … in five
  observables".
- **Options:**
  1. **(Recommended)** Move it earlier in the context paragraph, after the IBU sentence, so that it does not sit next to
     the scope sentence (the editor's A8).
  2. Drop it.
  3. Keep it where it is.
- **Rests on:** r5:13; the outline decision's rejection of "first application" framing (the editor's A8).

## W-18. Limitation 3 (the note's calibrated tests), and the estimator's name

- **Current:**
  - Limitation 3: "The note's calibrated tests reject hybrid nulls … not physical exclusions, and show no evidence of
    additional discrimination beyond matched coarse projections."
  - The name "joint-test estimator", "named for the note's calibrated joint tests".
- **Options, Limitation 3:**
  1. **(Recommended)** Move it to S7, with §7's 11.5 sentence (see W-12). Two reads call the joint-test machinery
     "(c), for the note": S1 `:105` and S2 `:89`.
  2. Keep it, with two sentences describing the joint tests.
- **Options, the name:**
  1. **(Recommended)** "the five-observable estimator", parallel to "the two-observable estimator". S1 asks for a
     rename (`:121`), and so does the editor's A9.
     - The registry carries ALIASES rows 38 and 47 for "joint-test estimator", and the printed-label check needs the
       new name as an alias.
     - limitation-resolver says the package doesn't use the term, so only paper quotes move.
  2. "the baseline estimator".
  3. Keep the name.
- **Rests on:**
  - `docs/orchestration/registry/ALIASES.tsv` rows 38 and 47;
  - `tools/registry/check_registry.py` (the printed-label rule);
  - S1 `:105`, `:121`; S2 `:89`.

## W-20. One timing statement, and the first coverage test's gate in one sentence

- **Current:**
  - §3.3 says "Every criterion was fixed before the results it grades were seen", and about ten more "specified" or
    "fixed in advance" phrases follow in §§4–6.
  - §6.2 gives the gate in three sentences.
- **Options:**
  1. **(Recommended)** Keep §3.3's statement and remove the repeats in §§4–6, except two: the explicit exception in §4.1
     (the background treatment, adopted after the comparison was known), and the run-period block "added after these
     differences were seen" (§3.2). Cut the gate to one sentence pointing to S9.
     - The director has to confirm, test by test, that every result §§4–6 reports had its criterion fixed first. The
       candidates are Table 2's criteria, the stability requirement, COV2D's grading, the like-for-like grading, the
       IBU nulls and the period benchmark.
     - S2 `:114` and G2 `:143` say the repeated language loses force. G1 and G2 want the gate history in the note
       (G1 `:77`, G2 `:93`).
  2. Keep the repeats, and cut only the gate.
  3. Keep both.
- **Rests on:**
  - r5:247 and FD-DIRECTOR-RULINGS.md §2 (Table 2's criteria);
  - `FD-STAB-DECLARATION.md` §5 (the stability requirement);
  - the COV2D declaration;
  - `LL5D-DECLARATION.md` §6;
  - the REF-G1 and REF-C2C1 outcomes (r5:180-182's comments);
  - `OUTCOME-20261107-per-period-2d-benchmark.md`.

## W-22. What the joint unbinned approach offers (motivation only)

<!-- absence-ok: this section quotes draft wording options for the director's decision; it states no finding that a result does not exist -->

- **Current, a draft in §1 after the redundancy sentence:** "Unfolding them jointly keeps their correlations event by
  event, so that projections and cells in any of the observables can be formed afterwards from one result and one
  covariance, and the hadronic observables are corrected together with the muon kinematics rather than through a
  separate binned response for each choice; this study does not test whether that gain is realized."
- **Options:**
  1. **(Recommended, as drafted)** It gives the motivation, says nothing is claimed, and answers S1's issue 7 and S2's
     issue 7 ("the five-observable physics case is not made", `:80-84`, `:61-65`) with a motivation, not a result.
  2. Shorter: "Unfolding the observables jointly lets any projection or cell definition be formed afterwards from one
     result with one covariance; whether that offers a practical gain over binned unfolding is not tested here."
  <!-- absence-ok: quoted draft wording for the director's decision; the record it rests on is cited in this item -->
  3. Motivation plus the test that would show the gain, as next-step text in §7. This is S1 `:84`'s candidate tests:
     bias against IBU at the same truths, and the information content of W and q₃ by dropping an observable.
- **Rests on:** the intro's OmniFold paragraph (r5:13); S4 `sec:method-algo` ("Histogramming this ensemble in any
  binning chosen afterwards gives the unfolded spectrum"). S1 `:84` itself allows "the paper should say it does not
  show an advantage".

## W-23. C_e named in §3.2

- **Current:** §3.2 lists the six groups inside C_total ("the statistical, flux, interaction, detector, lateral and
  normalization uncertainties of the joint-test estimator and C_model") without naming their sum. S5 defines C_e.
- **Options:**
  1. **(Recommended)** Name it: "…the statistical, flux, interaction, detector, lateral and normalization uncertainties
     of the joint-test estimator, whose sum is $C_{\mathrm{e}}$, and $C_{\mathrm{model}}$". This aligns the paper, S5
     and the result package, whose glossary quotes S5. limitation-resolver would then quote the paper.
  2. Leave the paper as it is. The package already quotes S5's definition.
- **Rests on:** `supplemental_body.tex`, S5 ("$C_{\mathrm{e}}$ sums the statistical bootstrap of configuration (e)
  …"); limitation-resolver's reply of 2026-11-09 (#981 at `0b6fb4df`).

---

## Reader items that are not W-items yet, for the director

- **The χ²/205 divisor.** Both Sonnet reads object to it. S1 `:42` asks for χ² per direction kept (136/73 = 1.86 and
  285/139 = 2.05). S2 `:26` asks for "ndf equal to the modes kept". The director's ruling of 2026-11-09 fixed the
  current form, so this is the director's to reopen. Any per-direction value would be a new derived number and would
  need a ledger row.
- **C_PL,5D as the primary covariance.** Both Gemini reads ask for the fake-data tests and generator comparisons to be
  primary *without* C_PL,5D (G1 `:34`, G2 `:71`). This changes what is reported, so it is not a wording item.
- **The W collinearity test.** G1 issue 6 (`:57`) and G2 issue 1 (`:32`) ask for a 4D unfolding without W. This is new
  compute, so it is not a wording item.
- **Repeating the mechanism study on more pseudo-experiments, and the refinement-only tie test.** S1 `:67` and S2
  `:44` ask for these. This is new compute.
