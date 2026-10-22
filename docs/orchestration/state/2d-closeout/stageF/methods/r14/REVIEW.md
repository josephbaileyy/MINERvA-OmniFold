# Adversarial review: register round r14 (methods paper)

I reviewed this independently and read-only. I edited no file in any worktree and made no commit. `git -C S/wt-reg4 status --short` still shows only ` M docs/analysis-note/paper_body.tex`. My scratch files are in `S/rev-reg4/`.

**One incidental write to disclose.** While testing whether r14 merges onto the new main, I ran `git stash create` and `git merge-tree --write-tree`. Both wrote unreferenced objects into the shared object store. Neither changed a ref, the index, the stash list or the worktree.

**Line references.**
- `A:n` is `S/wt-reg4/docs/analysis-note/paper_body.tex` (r14).
- `B:n` is the same file at 58fe8a61 (r13).
- Note files live in `S/wt-reg4/docs/analysis-note/`.

## Provenance
- **The builds match their sources.**
  - `builds/r14/.../paper_body.tex` is byte-identical to the wt-reg4 file.
  - `builds/r13/.../paper_body.tex` is byte-identical to 58fe8a61.
  - Apart from `paper_body.tex`, the two build trees differ only by a `__pycache__`.
- **The build logs are clean.** Neither paper log has an undefined reference, and both have the same 2 overfull boxes. `build_r14.out` reports SEC4-RECEIPTS PASS 15/15, and the ledger checker run read-only gives "rows 341, probes 489, failures 0".
- **The note is unchanged.** The extracted text of the r13 and r14 note PDFs is identical.
- **origin/main moved during this review (see SHOULD-FIX 2).**
  - It was 58fe8a61 when I started and is now 4a3f3b27: PR #212, merged 17:02 PDT, which adopts the shorter Data availability paragraph and edits `app_release.tex`.
  - PR #212 does not touch `paper_body.tex`, so r14 applies to it without conflict.
  - The r14 PDF, however, pairs the r14 body with the *old* Data availability paragraph.

## D. Protected text: CONFIRMED against the stated base; see SHOULD-FIX 2 for the current main
- **Source.** `main_paper.tex` has sha256 `d978ce7b…f111` in 58fe8a61, in wt-reg4 and in the r14 build tree. The diff contains no `pubhold`.
- **Printed text.** In both PDFs I compared every word from the DATA AVAILABILITY heading to the end. The only differences are:
  - where pdftotext places the heading;
  - one hyphenation break ("in-stead").
- **Against the current origin/main (4a3f3b27)** the file is no longer identical, because main changed it. r14 did not edit it.

## A. Lost facts
- **The numbers, by script.** `S/rev-reg4/numcmp.py` compares the numeric-token multisets of the two `pdftotext -layout` texts.
  - The raw counts are 1013 tokens (318 distinct values) in r13 and 1011 (316) in r14.
  - The only differences are `224` (1→0) and `53` (1→0). Nothing else was lost, altered or added.
  - In the source, the only macros that changed count are `\jtLostCal` and `\jtLostPow` (1→0).
- **Move 1: the lost-pseudo-experiment counts → note §10.6.** They print in the note PDF: "Scheduler time limits interrupted or prevented 224 of the submitted calibration pseudo-experiments (111 interrupted, 113 never started) and 53 power pseudo-experiments" (`sec_joint.tex:513–515`). The paper points to them at A:913 (`\nsec{sec:joint5d-lost}`, printed "Sec. 10.6").
- **Move 2: the binned-diagnostic exclusions → note §9.3.** All three print at `sec_5d.tex:197–201`:
  - "does not bound what unbinned or biased estimators could recover";
  - "it does not address the coverage failure";
  - "[does not] validate any interval".
  - The pointer is A:746–747, "(scope and exclusions: Ref. [14], Sec. 9.3)", and it resolves to "9.3 Why the estimator does not follow a generator-sized change".
- **Does any remaining sentence become false or stronger without the moved text?**
  - **Sec. VI.** Mostly no. The paragraph opens "A diagnostic in simulation bears on the first of these results", and the sentence before it (A:719–721) keeps "whether that bias has the same origin is not established" for the miscoverage. That covers the coverage exclusion. No paper sentence claims anything about unbinned recovery or interval validity.
  - **Sec. VII C.** One phrase is stronger; it comes from the C23 rewording, not from the move (SHOULD-FIX 1).
- **The FWER/A2 reasoning without the counts.** It still reads correctly.
  - The counts never entered the FWER argument. The bound is stated "Under them [A1, A2] … whatever rule determines when sampling stops" (A:891–897).
  - Note App. B.5 (`app_statmethods_nd.tex`, "Crossing event") lists "lost draws, and the budget extensions" inside the stopping-rule invariance.
  - "Every pseudo-experiment … was rerun, and none reaches the observed statistic" is a universal statement over a population whose size the paper no longer gives. It is not false.
  - The Table IV caption ("of 1400 submitted per null (1800 for NuWro)") still tells a reader that draws were lost.
  - There is one pre-existing gap; see NIT 6.
- **Every changed sentence.** For each of the 26 entries in `changes.md` (24 diff hunks, none of them in comments), I located every fact in r14 or at the cited note section. The two moves above are the only facts that left the paper.
  - The other 24 entries are restatements.
  - "Tests no other form or size" is now "tests a single form and size".
  - "No single band more than 15%" is now "each band at most 15%".
  - "Cannot vary with it" is now carried by "built at a fixed seed".
  - "Its source has not been identified" is now "of unidentified source".
  - "Source not established" is now "of unestablished source".

## B. Findings

### SHOULD-FIX 1. C23: "no decision depends on the lost outcomes" reads stronger than note §10.6
- **Before (B:915–918):** "The pseudo-experiments that computing time limits interrupted or prevented (224 for calibration, 53 for power) were rerun; none reaches the observed statistic in any test or shifted null, so no assignment of the lost outcomes changes any decision (Ref. [14], Sec. 10.6)."
- **After (A:910–913):** "Every pseudo-experiment that computing time limits interrupted or prevented was rerun, and none reaches the observed statistic in any test or shifted null, so no decision depends on the lost outcomes (Ref. [14], Sec. 10.6)."
- **Why the two phrasings are not equivalent.** The ledger (H29) calls them equivalent. They are not.
  - To a statistician, "depends on" names a functional dependence: the decisions would be the same whatever the lost outcomes had been.
  - Note §10.6 (`sec_joint.tex:516–520`) says the opposite: "A sensitivity computed before the lost outcomes were known showed that every decision could change under a realizable assignment of them: had every interrupted draw exceeded the observed statistic, no test would have been rejected."
  - What the evidence supports is narrower. The draws were recovered, "every submitted draw has now been observed" (`:527–528`), and the recovered values change no decision.
  - Note §10.3 (`sec_joint.tex:239–241`) adds that A2 requires the draws "to have been lost independently of their outcomes, which has not been shown".
  - So the r14 phrase overstates how settled the loss is.
- **The writer's justification has also lapsed.** C23 keeps the rerun clause because Data availability says "the recovery of the lost pseudo-experiments". The new Data availability on main (4a3f3b27) no longer has that phrase. Keeping the clause is still right, because it is the disclosure itself.
- **Fix:** "…, and none reaches the observed statistic in any test or shifted null, so including the recovered outcomes changes no decision (Ref. [14], Sec. 10.6)." Restoring r13's "no assignment of the lost outcomes changes any decision" would also do.

### SHOULD-FIX 2. Rebase onto 4a3f3b27 and rebuild before adopting or rescoring
- **The problem.** The r14 PDF is built on 58fe8a61. Main now carries a different Data availability paragraph (PR #212). It removes "the recovery of the lost pseudo-experiments" and rewrites the release sentences.
- **The consequence.** Any rater copy or protected-text check made from the r14 build describes a combination that will never exist on main.
- **What I verified.**
  - PR #212 touches `main_paper.tex`, `app_release.tex` and orchestration files only, not `paper_body.tex`.
  - The new paragraph still prints "This analysis used an earlier production of that release", so C3 (dropping "(see Data availability)") remains sound.
  - The new paragraph still names "the multiplier scan", which A:1015–1018 keeps.
- **Fix:**
  1. Apply only the `paper_body.tex` diff onto 4a3f3b27.
  2. Rebuild.
  3. Re-run the protected-text sha check against 4a3f3b27's `main_paper.tex`.
  4. Re-run the number script.

### NIT 1. C15: "could move the total in either direction" now attaches to the bands rather than to their seed sensitivity
- **Before (B:640–643):** "five bands built at a fixed seed, which carry 26.0% of √Tr C, cannot vary with it, so their seed sensitivity, which could move the total in either direction, is also unmeasured."
- **After (A:637–640):** "The spread over seed pairs is unmeasured, as is the seed sensitivity of five bands built at a fixed seed, which carry 26.0% of √Tr C and could move the total in either direction."
- **The problem.** The coordinated relative clause makes the *bands* the subject of "could move". A band, by being included, can only add to the total. The note (`sec_5d.tex:698–699`) says: "Allowing them to vary could move the total either way".
- **Fix:** "…, as is the seed sensitivity of five bands built at a fixed seed, which carry 26.0% of √Tr C; letting them vary could move the total in either direction."

### NIT 2. C17: "For these residuals" has an unclear antecedent
- **After (A:743–746):** "…the long runs do not converge, so this rests on their last iterates. For these residuals and within this comparison, the residual is consistent with the regularization…"
- **On scope: it carries.** The scope now opens the paragraph:
  - binned, noise-free and signal-only;
  - response fixed at the simulation's;
  - the same 109 cells and development truth changes;
  - the 38% stable subset, stated in the 144 sentence.
  - "Within this comparison" carries all of this to the conclusion. This is better than r13, where "covers only the residuals whose diagnosis is stable" wrongly seemed to restrict the all-cell medians too.
- **The problem.** The sentence just before is about the long runs for the GiBUU-to-GENIE change. "These residuals" can therefore be read as those, rather than the 144 resolution-stable residuals. In addition, "For these residuals …, the residual" mixes plural and singular.
- **Fix:** "For the 144 resolution-stable residuals and within this comparison, the residual is consistent with …".

### NIT 3. C9: "it removes the tail undercoverage" has two possible antecedents
- **After (A:452–457):** "…so a post hoc rescoring of them against it is not an independent coverage test; it removes the tail undercoverage: 97.7% …"
- **The problem.** The nearest "it" is the rebuilt band ("against it"). With that reading, the band itself is said to remove the undercoverage, a property established only by the non-independent rescoring.
- **What is right.**
  - "Specified in advance" and "post hoc" are both present, so r13 SHOULD-FIX 3 holds.
  - Both bands are "distinct from the quoted block".
  - The SEC4 phrases pass.
  - "Rebuilt after that test" is supported by `sec_validation.tex:276`.
- **Fix:** "…is not an independent coverage test; that rescoring removes the tail undercoverage: …".

### NIT 4. C14: a 20-word concession separates "is used" from "in the comparisons"
- **After (A:628–633):** "The covariance …, with its 42-cell (Eavail,W) projection, is used, although it does not meet the validation criteria of its specification (Ref. [14], Sec. 9.6), in the comparisons of Sec. V B, as the only five-observable covariance they use; …"
- **The content is right.** Note §9.6 (`sec_5d.tex:553`) has "It is used although it …", and `sec_joint.tex:13` has "which they do not use".
- **The problem is the register.** The sentence is harder to parse than r13's.
- **Fix:** "The comparisons of Sec. V B use only one five-observable covariance, that of the central value with its 42-cell (Eavail,W) projection, although it does not meet the validation criteria of its specification (Ref. [14], Sec. 9.6); the calibration of the joint tests (Sec. VII) does not use it."

### NIT 5. C21: the FWER statement now carries the budget bookkeeping inside the theorem
- **After (A:893–899):** "Under them, the probability of meeting the criterion at any number of pseudo-experiments up to 1999 is below the threshold, whatever rule determines when sampling stops, including the bounded extension of the calibration's computing budget that was decided with observed p values visible, so the decision rule controls the familywise error rate of the ten decisions at 5% (Ref. [14], App. B.5)."
- **The content is right.**
  - The note (`sec_joint.tex:233–235`) says "whatever rule determines when sampling stops, including the budget extensions".
  - App. B.5 says "including stops decided with results visible, … and the budget extensions".
  - DECISION-20261004-s5p-production-budget-extension.md confirms that the extension was CPU budget only, with no change to the stopping rule or to the 1999 cap.
  - The disclosure (an extension decided with p values visible) is kept in full.
- **The problem.** The sentence is about 75 words long. It turns the paper's central guarantee into a sentence that reads partly as a record.
- **Fix (optional):** close the FWER sentence at "whatever rule determines when sampling stops", then add: "This includes the bounded extension of the calibration's computing budget, decided with observed p values visible."

### NIT 6 (pre-existing; not introduced by r14). The paper never says that A2's loss-independence requirement is unverified
- **The text.**
  - r13 and r14 both define A2 only as "the pseudo-experiments' exceedances are independent given the data" (A:893–894).
  - The note prints at §10.3 (`sec_joint.tex:239–241`): "A2 requires the lost pseudo-experiments to have been lost independently of their outcomes, which has not been shown".
  - The ledger records this as H28, MOVE.
- **Why it passes the rule.** The FWER sentence points to App. B.5, which prints the requirement but not "has not been shown". The §10.3 pointer now sits on the design sentence. The FWER claim is conditional ("Under them"), so it is not false as read, and the move rule is satisfied.
- **Why it still matters.** Combined with SHOULD-FIX 1, a reader can come away believing the lost-draw question is fully closed.
- **Fix (optional, one clause):** "(A2, which also requires the lost pseudo-experiments to have been lost independently of their outcomes; Ref. [14], Sec. 10.3)".

### Checked and sound
- **C2.** The new wording, "The rejections, made with a detector model that has no calorimetric recoil-response uncertainty, are statements about these hypotheses rather than physical exclusions of the generators, and provide no measurement uncertainty" (A:116–119), is sound.
  - "These hypotheses" has a clear antecedent: the "simulated hybrid hypotheses" of A:111.
  - "Made with" states a condition, not a cause.
  - It is not stronger than r13. The abstract still prints "They are not physical exclusions".
  - Tying the recoil-response gap to the rejections matches Sec. VII D(ii) (A:937–941).
- **C22, the design sentence.** "The test design was fixed after its reviewers had seen descriptive per-cell residuals of the data, and before any observed statistic was computed (Ref. [14], Sec. 10.3)" (A:908–910) keeps both facts in time order.
  - It still discloses that the reviewers saw residuals before the design was fixed.
  - The budget extension "decided with observed p values visible" stays in the paper (A:896–898), in the FWER sentence.
  - Both match §10.3's "Two data-informed elements are disclosed".
- **C1, C3–C8, C10–C13, C16, C18–C20, C24–C26.** In each, I found every fact in r14, with no strengthening:
  - C1: "We evaluate this implementation as a case study" (A:59) keeps the case-study framing.
  - C3: "earlier production" stays, and Data availability prints it in both the old and the new paragraph.
  - C12 matches note §9.5 (`sec_5d.tex:517–528`: "inferred, not measured"; "not established").
  - C24 keeps "against the original null distributions".
  - C26 keeps "bounds neither the actual residual nor the convergence".

## C. What earlier reviews required (8 of 8 hold)
1. **Hydrocarbon replays.** "These target-corrected evaluations are descriptive and do not re-grade the decisions of Table IV, which concern each prediction on the target it was generated for and stand" (A:1012–1015). This is unchanged.
2. **The five-iteration rule is scoped, with its measure.** "keeps five iterations under a rule fixed before the comparison, because 10, 15, or 20 did not reduce the rule's measure of model dependence, the largest residual proxy over the development truth changes" (A:292–295).
3. **The rebuilt-band rescoring and the 300-replica block.**
   - The rescoring is "post hoc" and "not an independent coverage test" (A:454–455).
   - The quoted block is "a bootstrap of 300 replicas" (A:441), and both bands are "distinct from the quoted block" (A:448 and A:452–453).
4. **The 135 MeV materiality.** "an effect whose materiality is not established because it has not been assessed against the covariance" (A:183–184).
5. **Higher-dimensional central values.** "Each higher-dimensional central value is checked against the lower-dimensional result it extends" (A:481).
6. **The coverage failure also at nominal truth.** The text has "miscover at the tested truths, most strongly when …" (A:529), and the Fig. 4 caption says "At nominal truth (not drawn) … two lie below the 0.94 threshold" (A:603–604).
7. **Condition (iv).** "measured for the mean only, without noise or nuisance draws" (A:974).
8. **GENIE CV.** "a post hoc observation" (A:950–951).

## E. Register: passages that still read as history or bookkeeping (8)
1. A:446–457: the history of two superseded statistical bands. The SEC4 gate binds its numbers.
2. A:893–899: the FWER sentence now holds the budget-extension record (NIT 5).
3. A:908–913: the design chronology and the rerun of lost pseudo-experiments (SHOULD-FIX 1 applies here).
4. A:366–369: "was chosen after both comparisons were known". This is a guardrail.
5. A:586–587 (Fig. 3 caption): "a separate set of assessment seeds, also used in its later development".
6. A:628–633: "is used, although it does not meet the validation criteria of its specification". This is internal-record framing (NIT 4).
7. A:292–293: "keeps five iterations under a rule fixed before the comparison". This is required by an earlier review, but it reads as process.
8. A:90 (Table I): "an earlier band failed coverage". This is history inside a results summary table.

## Verdict: **ADOPT-AFTER-FIXES**
- **No BLOCKING finding.** The numbers, the two moves and their pointers, all 8 earlier requirements and the protected text (against 58fe8a61) check out.
- **Before adoption:**
  - SHOULD-FIX 1: one phrase in A:912–913.
  - SHOULD-FIX 2: rebase onto 4a3f3b27 and rebuild before any rescoring or protected-text sign-off.
- The NITs are optional. NIT 1 and NIT 2 are each a few words and are worth taking.

## Counts
- **Hunks.** I read 24 of 24 diff hunks, all of which change printed text.
- **Changed sentences.** I tested 26 of 26 `changes.md` entries against r13, r14 and the note.
- **Numbers.** I compared 1013 and 1011 numeric tokens, with 2 differences, both accounted for by the moves. I also compared macros, with 2 differences.
- **Note targets.** I opened 8 note locations: §5.2, §9.3, §9.5, §9.6 (its covariance status and seed-list items), §10.3, §10.6, App. B.5, and the budget-extension DECISION record.
- **Earlier requirements.** I checked 8 of 8.
- **Protected text.** I made 3 checks: the source sha against base, the printed tail word diff, and `pubhold` in the diff. I also made 1 check against the current main, which differs because main moved.
- **Ledger.** The ledger checker gave 341 rows, 489 probes and 0 failures. I read H22, H27, H28, H29, H33, H36, H38, L6, L9, L10, S9 and S11 against their sentences.

## Not checked
- I did not check unchanged r14 sentences against primary evidence.
- I did not check the note beyond the cited sections and their neighbourhoods.
- I did not compare the primer or the PET note.
- I did not rebuild r14 on 4a3f3b27, and did not run the SEC4 gate myself. I read its PASS from `build_r14.out`.
- I did not open primary records (RECORD-20261006 lost-seed resolution, D-ID REPORT) beyond the budget DECISION.
- I did not rate the register with any model, and did not compare r14 against the rater-copy build.
