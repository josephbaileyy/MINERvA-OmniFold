# Review of note register batch b3 (§9, App. B, App. C)

Reviewer: independent, read-only. Base: origin/main `b603f9cf` (build `rec3`, sources confirmed byte-equal to HEAD).
After: uncommitted edits in `S/wt-note-b3` (build `note-b3`, sources confirmed byte-equal to the worktree).
Nothing was edited in any worktree. Scratch outputs are in `S/wt-note-b3-work/rv/`.

## Pre-submission item for the author (not a writer defect)

**The background-treatment obligation is real, and it is open.** App. C.6 (`app_negweight.tex:285-287`) now prints:
"The choice carries an obligation to revisit the background treatment before submission, and that obligation has
not been met."

- **Where it comes from.** Joseph decided on 2026-08-07 that the standard 5D chain is quoted on purity and
  revisited before submission (`docs/orchestration/RUNBOOK-20260807-gbdt-closeout.md` §2 item 1, :55-57, tracked
  as G-0 at :205-213 and in §7 item 1 at :436-437). He confirmed it on 2026-08-15:
  `DECISION-20260815-joseph-oi6-oi8-oi126.md` :9-24, "keep purity, but make sure this distinction and reasoning is
  obvious in the note".
- **What would close it.** Either re-affirm purity, or run the full 5D 187-universe comparison of both treatments
  at 5 iterations with `lgbm` (RUNBOOK §2.1 :93-97; `docs/OPEN_ITEMS.md` OI-6).
- **Status.** On origin/main (`8f2df745`) OI-6 still reads "the REVISIT OBLIGATION SURVIVES AS THE OPEN HALF".
  A search of the DECISION files from September and October 2026 found no ruling that meets it.
- **The old text said the same.** It read "nothing in this subsection meets that obligation", under the heading
  "Background treatment chosen, its obligation not yet met; …". The base note also printed "The obligation … therefore
  remains open" (`app_negweight.tex:392`, unchanged). So the new sentence is accurate and claims no more than before.
- **What to do.** The posted note now tells arXiv readers about an unmet pre-submission duty. Before posting, the author
  should either meet the obligation (the cheapest route is a recorded re-affirmation of purity) or decide how the note
  should state the limitation. C.7 already prints the limitation itself: there is no full 5D 187-universe comparison.

## Findings

### F1. BLOCKING (a new false-as-read statement; qualifier removed). §9.4, `sec_5d.tex:299-300`
- **Before (:294-295):** "Figure … shows the available traces, without extension beyond the committed iteration ranges."
- **After:** "Figure … shows the traces over the iteration ranges that were run; none is extrapolated."
- **Why it is false.** More iterations than the plotted ones were run:
  - `RECORD-20260927-s5p-stage2-exit.md:29` gives the GiBUU, q3 and W1 traces "from checkpoints, k ≤ 40/30/40 at the
    receipt and still running".
  - App. B.2, in both versions, says "later entries are excluded" (`app_statmethods_nd.tex:129-130`).
  - So the plotted ranges are the ones that were recorded and used, not the ones that were run. "Committed" was the
    qualifier that kept the old sentence true.
- **Fix:** "Figure … shows the traces over the recorded iteration ranges (later checkpoint entries are excluded,
  App. B.2); none is extrapolated."

### F2. BLOCKING (a minor lost clause). App. C.8, `app_negweight.tex:421`
- **Before:** "Neither fact follows from or is needed by this appendix."
- **After:** "neither fact follows from this appendix or depends on it."
- **What was lost.** "Depends on it" restates "follows from" (the facts do not rest on the appendix). The other half of
  the claim, that the appendix does not need either fact, is gone.
- **Fix:** "neither fact follows from this appendix, and the appendix needs neither."

### F3. SHOULD-FIX (scope incomplete; check 3). App. C, `app_negweight.tex:17-20`
- **Before:** "Every result in this note uses the binned purity weight of §…" This was false as read.
- **After:** "Every cross section and uncertainty quoted in this note uses the binned purity weight …; the joint-test
  estimator of the generator tests (§10) uses refined negative-weight subtraction."
- **What checks out.**
  - `sec_method.tex:160-174` confirms that configuration (2), the joint-test estimator, uses "the unbinned
    negative-weight background treatment" with a 400/31 refinement.
  - `sec_joint.tex:96-100` confirms it in §10.
  - The glossary term "refined negative-weight subtraction" (GLOSSARY B2) is the right one.
  - Read as the note's term of art, "quoted" means the measured results, and then the sentence is true. §9.4 says
    that no five-dimensional measurement with total uncertainties was constructed.
- **What is incomplete.** The same estimator also produces the development numbers of §§9.2-9.4:
  - GLOSSARY A2 says R "has the joint-test estimator's configuration".
  - The paper says "With the joint-test estimator, the envelope alone exceeds it", citing §9.4 (`paper_body.tex:667-673`).
  - Those numbers include the bounded unfolding-model component (median 12.0/9.6/13.4%), the bootstrap SD of 0.368%
    and the development intervals.
  - Naming §10 alone suggests that everything outside §10 is purity.
- **Fix:** "…; the joint-test estimator, used for the generator tests (§10) and for the development studies of
  §§9.2-9.4, uses refined negative-weight subtraction."

### F4. NIT (population of the new numbers; check 1 / Q2). §9.4, `sec_5d.tex:319-325`
- **Numbers:** these are exactly the record's and the receipt's.
  - `state/s5p/stage2/stage2_receipt.json` `study_K.b0.M.H2` gives k=5 0.31433, k=10 0.38398, k=15 0.40166 and
    k=20 0.39763. So "at least 0.384 at 10, 15 or 20" is exact, with k=15 taken from the receipt; the record's table
    (:80-86) omits k=15, and §3 (:114-116) gives the minimum, 0.384.
  - On J, k=5 0.626 is below k=10/15/20 (0.635/0.631/0.650), so "on the J or the H2 cells … None did" is exact.
- **Scope:** exact.
  - M is the maximum over the development alternatives (gibuu = D1, q3, w1, w3) of the T2 proxy (:76-78).
  - W3 sets it and does not converge, while GiBUU and W1 improve slowly (:88-93). That supports "a maximum …, so
    the slow gains for D1 and W1 do not lower it".
  - The sentence now matches the paper's own wording (`paper_body.tex:292-295`, pointer §9.4).
  - "Only if" states a necessary condition, so it is safe even though the rule also has the ≤ 0.25 clause.
- **Population.** M is computed on the noise-free baseline-capacity (B0) traces of Fig. `gbdt-recovery`, not on
  background-inclusive runs of the joint-test estimator. The sentence opens "For the joint-test estimator", so a reader
  may take 0.314 to be that estimator's own value.
- **Suggested wording:** "(on H2, over the noise-free traces of Fig. …, it is 0.314 …)".

### F5. NIT. App. C.6, `app_negweight.tex:277`
The bold "**This is a recorded choice, not a silent default**" is now plain "Purity is a deliberate choice for this
chain, not a silent default". The substance is intact. Joseph's ruling asked that "this distinction and reasoning is
obvious in the note", so the author may want the emphasis back. That is a judgement call, not a lost fact.

### F6. NIT. App. B.4, `app_statmethods_nd.tex:155`
"with no new validation result here" became "no validation result for them is reported here", which drops "new". The
appendix's B.5 is a derivation, not a validation, so the stronger negative is true. Restoring "new" would be the
literal-preserving choice.

### F7. NIT. App. B.1, `app_statmethods_nd.tex:56-57` and heading :37
- "The treatment is to be decided … once declaration (v) has recorded the quantities the treatment needs" became
  "must be chosen … from the quantities that declaration (v) records".
- The heading "why it does not yet mandate a correction" became "why no correction is prescribed".
- The "not yet / once" timing is softened, but the meaning survives. No action is needed.

### F8. NIT (scope). The orchestrator counted 13 paper pointers; there are 10
`paper_body.tex` and `main_paper.tex` carry 10 `\nsec`/`\napp` pointers into this batch's labels, and the printed
paper shows the same 10:
- §9.2 ×1;
- §9.3 ×2;
- §9.4 ×2;
- §9.5 ×2;
- §9.6 ×1;
- App. C ×1;
- App. B.5 ×1.

If 13 was meant to include other labels, I did not find them.

## The directed checks

1. **§9.4 five-iteration rule.** Exact in scope and numbers, for the same population as the record (F4 suggests a
   wording to name it). The writer's source comment (`sec_5d.tex:316-318`) cites the correct record lines.
   **Q2: keep the parenthesis**, preferably with F4's population phrase.
2. **App. C obligation.** It is accurate and was already printed (see the section at the top). Created 2026-08-07
   (RUNBOOK §2) and confirmed 2026-08-15 (DECISION-20260815, OI-6). Still unmet on origin/main.
3. **Re-scoped purity claim.** True for the measured results and for §10. Incomplete for §§9.2-9.4 (F3).
4. **Removed material.**
   - **The "A scoped response-information diagnostic" paragraph (§9.5).** It carried no fact beyond a pointer to §9.3.
     §9.3 still prints every element of it: 376/232/144 (38%), 121, the uninformative muon projection, the
     binned/signal-only/noise-free/fixed-response/development-truth scope, the out-of-scope list and the records
     pointer (`response-diagnostic`). No paper pointer to §9.5 concerns it: both are about interval construction and
     the miscoverage diagnosis, and both still print. No label was removed.
   - **The three "(Ref., superseded values)" pointers (C.1, C.6, C.7).** The records print each one:
     - `app_history.tex:288-300`, "From App. C, the extended-fiducial footing …", carries the withdrawn σ_ext
       implication and the withdrawn "agree by construction";
     - `app_history.tex:302-305`, "From App. C.1, the continuous estimand".
   - The current facts all still print: σ_ext was not produced with negative-weight injection; it is not a theorem;
     the two do not share the continuous estimand.
   - **No fact lost.** One caution: 41 other "superseded values" pointers remain in other chapters, so these three now
     differ from the note-wide convention. RECORDS-MOVE and RECORDS-PIN pass.
5. **The 10 paper pointers.** Each pointed-to fact still prints in its subsection:
   - App. C: the targets differ within a bin;
   - §9.4: the 10/15/20 rule, now worded as in the paper;
   - §9.2: 74% in 0.8≤E_avail<1.5, W≥3 GeV, with or without background;
   - §9.5 ×2: the interval construction, and the Gaussian-fit inference with its source not established;
   - §9.6: "does not meet the acceptance criteria of its specification";
   - §9.4: the envelope medians and the 1.4% normalization;
   - §9.3 ×2: the pooled W2 "unchanged without it", 38%, the out-of-scope list and the regularization conclusion;
   - App. B.5: unchanged.

   The paper's pdftotext is byte-identical to `rec3`. The 184 label numbers are identical (my own aux comparison
   against `rec3`, with page numbers stripped).
6. **The §9.6 null-bound rewrite.** Intact.
   - "does not meet the acceptance criteria"; "the bound was not fixed before this covariance was produced, so the
     requirement cannot be met for it". This matches DECISION-20260920 §2: "SPEC §6.4 requires the null bound fixed
     before production, and production has happened".
   - The metadata is "not passing and … not to be used", matching `scientific_acceptance: NON-PASSING` and
     `adoptable: false` (DECISION-20260920 :24-26).
   - The exception "covers only this file and its projection, not any other covariance built to the same
     specification, including the two companion covariances". This matches §3 "covers 3d7465f6… and nothing else —
     explicitly including 361090f9… and 7e4636a3…".
   - The following block-sum sentence (records-move L12) is byte-identical.
7. **Q3, "Removing D1 leaves the remaining ratios uncorrected".** The writer's reading is correct.
   - KNOWN_ISSUES row 83: the GENIE CV, GENIE+MEC and NuWro predictions all used the mis-sampled flux. So D1
     (GiBUU/GENIE) and W1-W3 (NuWro/GENIE, GENIE MEC/CV, NuWro/GENIE) were all built from uncorrected inputs.
   - The sentence warns that excluding D1, as the prior-sensitivity paragraph does ("excluding D1 gives 11.2%, 4.3%,
     9.9%"), does not leave corrected comparisons.
   - "Excluding D1 does not make the others corrected generator comparisons" preserves this. It could be made
     clearer: "W1-W3 were built from the same uncorrected predictions, so excluding D1 does not make them corrected
     generator comparisons."

## Protected text (direction C)
- App. B.5 (`sec:joint5d-fwer`, "moved verbatim" from the article) is untouched: the last diff hunk ends at
  `app_statmethods_nd.tex:172`.
- The two spans the writer kept verbatim are byte-identical (scripted check):
  - §9.6's block-sum sentence (L12);
  - App. C's provenance-limit sentences after "changes no default" (L15), 515 bytes.
- No source comment in the three files marks other text as protected.
- The edits inside the `CLAIM-ADDITION D-ID` block (§9.3) keep every element listed in its source comment.

## Mechanics (direction D)
- **Build.** `build_all rc=0` (`build_final.out`). The build log shows:
  - containment `RESULT :: PASS`, with 0/69 struck literals in the note, paper and primer;
  - `BODY-POINTERS :: PASS`;
  - `SEC4-RECEIPTS :: PASS (15/15)`;
  - `RECORDS-PIN :: SKIP` in the scratch copy.
- **Records checks, rerun by me.**
  - `RECORDS-MOVE :: PASS` (probe, rc 0).
  - `RECORDS-PIN :: PASS` on the worktree (rc 0).
- **Logs and PDF text.** 0 undefined references in each of the five logs, and 0 `??` in each pdftotext (the writer's
  run).
- **`swallowed_text.py`.** "flagged 0" (rerun by me).
- **Ledger checker.** It passes (rc 0, 160 rows, 297 probes) and `--self-test` passes. My own planted probe
  (`N:app_negweight.tex::Every result in this note uses the binned purity weight`) failed it (rc 1), as it should.
- **Writer's label script.** `run_checks.sh` strips the base and the new aux files with different `sed` pipelines, so
  its "label numbers identical" line is not a symmetric comparison. My symmetric comparison also finds them identical.

## Numbers before and after (direction A)
I compared every number in the printed chapter text (pdftotext -layout, §9, App. B, App. C), base against after.

| chapter | numbers lost | explanation |
|---|---|---|
| §9 | "07" | 2026-07 became "July 2026" |
| §9 | "9.3" | the removed pointer paragraph |
| §9 | "5" | from "Items one, two and four" and the "(Ref. [38]" line splits |
| App. B | "97", "5"×2 | page number and layout |
| App. C | "38"×3 | the three removed "Ref. [38]" pointers |
| App. C | "07" | 2026-07 became "July 2026" |

Every number gained is a new specific: 0.314, 0.384, 10, 15, 20, the pointer "§§9.1-9.3", and the repeated 144.
All of them were verified.

Word counts (pdftotext, figures included):
- §9: 5711 → 5855;
- App. B: 2154 → 2177;
- App. C: 3209 → 3251.

## Register (direction E)
The worst-rated passages are fixed:
- the §9.3 stacked non-claims;
- "must be read and checked … never inferred";
- the "rank 36" instruction;
- "reduction package … prefixes … committed ranges";
- the C.6 version-gap chain;
- the C.8 heading.

Surviving bookkeeping or meta-text (quoted exactly; at most 8):
1. "The file and the projection are identified by their SHA-256 checksums (Ref. [38], identities already fixed)." (§9.6)
2. "A file's variant is identified by its metadata, not by its path" (§9.6)
3. "the projected source's central-value array and the figure's are the same bytes, and their numerical agreement is
   only a corroborating check." (§9.6)
4. "The central value of that battery, 4.502 × 10−38 cm2/nucleon, is recorded in the validation ledger with its passed
   published-region check against the control." (C.6)
5. "the value is written into the record of every endpoint unfold as it is produced" (C.6)
6. "The analyst cross-checked the reductions numerically; no new independent scientific review of the synthesis is
   claimed." (B.2)
7. "ten endpoint unfolds whose distinct checksums are listed in the record of the covariance used in this note" (C.8)
8. "The choice carries an obligation to revisit the background treatment before submission, and that obligation has
   not been met." (C.6): a to-do, not a property of the result; see the section at the top.

## Verdict: ADOPT-AFTER-FIXES
F1 and F2 are one-clause fixes, and F3 is a one-clause scope extension. Nothing else blocks.

**Counted.**
- 3 files diffed word by word;
- about 75 changed sentences checked against the old text;
- 9 source records opened: the RECORD, the stage-2 receipt, the RUNBOOK, DECISION-20260815, DECISION-20260920,
  OPEN_ITEMS OI-6, KNOWN_ISSUES rows 75 and 83, the OUTCOME s5e candidate record, and the GLOSSARY;
- 10 paper pointers;
- 3 removed records pointers and 1 removed paragraph;
- 2 verbatim spans, plus B.5;
- every number in 3 printed chapters;
- 6 mechanical gates rerun or inspected.

**Not checked.**
- The rows of the 160-row ledger one by one: only the checker and its self-test.
- The figures' internal text (not editable).
- Equations, which were not changed.
- The paper or primer for consistency beyond the 10 pointers.
- Whether any of the 41 other "superseded values" pointers should go too (other batches).
- The rated complaint files in `S/xmodel/note-cal/`.
