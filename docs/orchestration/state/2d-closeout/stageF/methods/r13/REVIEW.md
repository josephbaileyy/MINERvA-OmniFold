# Adversarial review: register round r13 (methods paper)

Reviewer: independent and read-only. I edited no file in any worktree and made no commit. `git -C S/wt-reg3 status --porcelain` still shows only ` M docs/analysis-note/paper_body.tex`.

**Scratch-file incident.** My first `git diff` redirect wrote by mistake to `S/rev-reg3/wd.txt`, which is a scratch file of an earlier reviewer, and overwrote it. It is not in any worktree, and the file can be regenerated. All my other work files are in `S/rev-r13/`.

**Line references.**
- `A:n` is `S/wt-reg3/docs/analysis-note/paper_body.tex` (r13).
- `B:n` is `S/wt-reg2/docs/analysis-note/paper_body.tex` (r12, which equals origin/main 38a53a53).
- Note files are named directly and live in `S/wt-reg3/docs/analysis-note/`.

## Provenance checks (all passed)
- **r12 is main.** `git -C S/wt-reg2 diff origin/main -- docs/analysis-note` is empty. The `wt-reg2` HEAD `c1ca6316` is an ancestor of origin/main.
- **r13 changes one file.** `git -C S/wt-reg3 diff origin/main --stat` lists only `paper_body.tex`: 36 hunks, one of them a source comment.
- **The builds match their sources.** For each version, all 41 `.tex` files in `plain-language/builds/{r12,r13}/repo/docs/analysis-note/` are byte-identical to the matching worktree.
- **Both build logs are clean.** Neither has an undefined reference. The two overfull boxes in r13 are the same two that r12 has.

## C. Protected text: CONFIRMED byte-identical
- **Source.** `main_paper.tex` has sha256 `d978ce7b…f111` in origin/main, in `wt-reg3` and in the r13 build tree.
- **Printed text.** I extracted the PDF text from ACKNOWLEDGMENTS to the end and normalized it (page-number lines dropped, hyphenation joined). r12 and r13 then differ only in where pdftotext places the page numbers 12 and 13 and the "DATA AVAILABILITY" heading. Every word is identical.
- **`\pubhold`.** Both `\pubhold` texts are unchanged. The diff contains no `pubhold`.

## A. Number survival (scripted)
- **Script.** `S/rev-r13/nums.py` compares every numeric token in the `pdftotext` raw text of both PDFs. r12 has 1021 tokens and r13 has 1017; both have 319 distinct values.
- **The only differences:**
  - `10`, `15` and `20` each drop by one. This is the iteration rule's "10, 15, or 20", which moved to the note; it prints at `sec_5d.tex:312`.
  - `300` drops by one. This is "a separate 300-replica ensemble". The 300 replicas still print twice, at A:402 and A:439.
- **Nothing else changed:** no number was altered, added or lost.

## A/B. Findings

### SHOULD-FIX 1. The hydrocarbon sentence is not what note §10.9 says, and "as generated" is inaccurate as read
- **Before (B:1016–1017):** "These corrected evaluations are descriptive and do not re-grade the recorded decisions of Table IV (Ref. [14], Sec. 10.9)."
- **After (A:1013–1015):** "These target-corrected evaluations are descriptive; the decisions of Table IV are those of the predictions as generated (Ref. [14], Sec. 10.9)."
- **The note (`sec_joint.tex:703–704`):** "They are descriptive: they do not re-grade the recorded decisions of Table IV, which stand."
- **Why it matters:**
  - **The guardrail is gone.** The r12 re-review (R1) required the replays to read as not re-grading the decisions. "Do not re-grade … which stand" now prints in neither r13 sentence. The new clause names which predictions the decisions belong to; it does not say that the decisions stand.
  - **It invites a re-grade.** The sentence before it says NuWro's total rejection "does not survive that correction robustly". After that, "the decisions … are those of the predictions as generated" reads as "Table IV concerns the uncorrected predictions, and for the corrected ones the verdict differs". The note refuses exactly that reading.
  - **"As generated" is false as read.** The paper says the GENIE and NuWro predictions "are reweighted exactly, event by event, to the analysis flux" (A:217–218). The note says that its replays run the generator products through "the frozen conversion, flux-repair and binning chain" (`sec_joint.tex:710–711`). So no tested prediction is literally "as generated". The phrase is right only in the narrow sense of "on the target it was generated on".
  - The ledger row R4 itself records the difference from the note ("note §10.9: 'do not re-grade …'"). It does not test whether the two say the same thing.
- **Fix:** "These target-corrected evaluations are descriptive and do not re-grade the decisions of Table IV, which concern each prediction on the target it was generated for and stand (Ref. [14], Sec. 10.9)." A shorter option is to restore the r12 clause.

### SHOULD-FIX 2. The five-iteration move sends the reader to the unscoped wording that r12 B2 rejected; the rule's measure is now in neither document
- **Before (B:291–294):** "It keeps five iterations under a rule fixed before the comparison, because 10, 15, or 20 did not reduce the rule's measure of model dependence, the largest residual proxy over the development truth changes (Ref. [14], Sec. 9.4)."
- **After (A:292–293):** "…; the rule that set its five iterations is given in Ref. [14], Sec. 9.4."
- **The pointer's target (`sec_5d.tex:311–313`):** "a rule fixed before the comparison would have replaced its five iterations by 10, 15, or 20 only if they reduced the model dependence; none did, so five were kept."
- **Why it matters:**
  - **The paper sentence itself is fine.** It is not false, and it no longer states the outcome.
  - **But the writer's claim is wrong.** The writer says that "the r12 B2 scoping issue cannot recur" (triage #10, ledger M18). It recurs at the place the paper now points to. The note says "reduced the model dependence" with no scope.
  - **Contradiction 1, inside §9.4.** The same section prints "D1 and W1 improve slowly" (`sec_5d.tex:296`).
  - **Contradiction 2, across documents.** The paper's own Sec. V B prints "thirty iterations reduce the Eavail residual by 26 %" (A:511–512). This is the pair of contradictions B2 identified.
  - **The definition left both documents.** The definition of the operand, "the rule's measure … the largest residual proxy over the development truth changes", is the r12 B2 fix. It now prints in neither document at the iteration rule.
  - **The ledger probe does not cover it.** The M18 probe matches "lowers the largest residual proxy over the development truths". That is the *capacity* sentence (`sec_5d.tex:305–308`), not the iteration rule. A reader cannot tell from the note that the iteration rule used the same measure.
  - **Severity.** Under rule 3 ("no fact leaves both documents"), the author could reasonably class this as BLOCKING. I rate it SHOULD-FIX because the capacity sentence two lines earlier lets a careful reader infer the measure.
- **Fix (a one-phrase note edit, which is in scope under DECISION item 2):** `sec_5d.tex:312–313`, "only if they reduced the rule's measure of model dependence, the largest residual proxy over the development truths; none did".
  - Alternatively, restore "under a rule fixed before the comparison, because 10, 15, or 20 did not reduce the rule's measure of model dependence" in the paper.

### SHOULD-FIX 3. Sec. IV B: the reordering keeps the populations distinct, but the second scoring now reads as designed rather than post hoc
- **Before (B:445–456):** "Neither this block nor the total has had a coverage test. In 100 closure pseudo-experiments at a fixed truth, an earlier version of the statistical band undercovered … Rescoring the same pseudo-experiments against the rebuilt band removes the tail undercoverage … The rebuilt band is not the quoted block, which is a separate 300-replica ensemble; neither has been tested on independent pseudo-experiments."
- **After (A:443–454):** "The coverage of this block, and of the total, has not been tested. Two earlier versions of the statistical band, distinct from the quoted block, were scored on 100 closure pseudo-experiments at a fixed truth (Ref. [14], Sec. 5.2). The first undercovered in its tails: … Rescoring the same pseudo-experiments against the rebuilt band removes the tail undercoverage: … This rescoring is not an independent coverage test, because the simulated part of the rebuilt band reuses the resampling mechanism of those pseudo-experiments."
- **Identities and populations: correct.**
  - The quoted block, the two earlier bands and the rescoring stay distinct.
  - "Distinct from the quoted block" now comes before the history, which is better than r12 for B3.
  - The note supports all of it (`sec_validation.tex:276–278`): the first band; the rebuilt band; the quoted block "a different ensemble …; this section's result is for the earlier band and was not re-tested".
- **Post hoc status: weakened.**
  - "Two earlier versions … were scored on 100 … pseudo-experiments" presents both scorings as one designed study.
  - The note says that the first scoring had criteria "fixed in advance" (`sec_validation.tex:219`, `:247`). It says the second is "evaluated post hoc … and partly circular" (`sec_validation.tex:284–285`).
  - r12 at least showed the order: the band failed, was rebuilt, and was rescored. r13 never says that the second version is the rebuilt band, or that it was built after the failure.
  - Only the pointer to §5.2 remains. The paper gives the circularity reason and not the post hoc one.
- **Fix (this is safe under the SEC4 gate, which binds only "removes the tail undercoverage: …% fall within two … and …% within one" and "against …% nominal"):**
  - "…The first, whose test was specified in advance, undercovered in its tails: …"
  - "Rescoring the same pseudo-experiments post hoc against the second, rebuilt band removes the tail undercoverage: …"
- **Out of scope; it was the same in r12.** The note says the rebuilt band's C1 = 0.781 and C2 = 0.977 are "both above their nominal windows", so the rebuilt band is too wide. The paper's "removes the tail undercoverage" is true, but it lets the numbers alone show the overcoverage.

### NIT 1. 135 MeV: "a shift that has not been assessed against the covariance" (A:181–184)
- **Before (B:179–181):** "…by more than 1.05 %; its materiality has not been established, because it has not been assessed against the covariance (Ref. [14], Sec. 7.1)."
- **After:** "…by more than 1.05 %, a shift that has not been assessed against the covariance (Ref. [14], Sec. 7.1)."
- **Question asked: does it now read as immaterial?** No more than the wording the r12 review B4 accepted ("this effect has not been assessed against the covariance"). The limitation and the pointer are both present, and no sentence is false.
- **What "its materiality has not been established" did:** it was the only explicit refusal of the "two small numbers, so immaterial" reading. It prints at `sec_3d.tex:88–89`: "Its materiality is not established, and this note does not call it immaterial".
- **Optional fix:** "…, an effect whose materiality is not established because it has not been assessed against the covariance". This adds four words.

### NIT 2. The §3.2 pointer now reads as a citation for the bias (A:284–286)
- **After:** "…with the purity-based subtraction, whose bias in simulation is given in Sec. V A (Ref. [14], Sec. 3.2)."
- **The problem:** the moved fact ("they were not regenerated", `sec_method.tex:200–203`) does print in §3.2. But the pointer now attaches to "whose bias … is given in Sec. V A", which already has its own reference.
- **Fix:** "The two- to five-observable central values use configuration (a), the central-value estimator (provenance: Ref. [14], Sec. 3.2), with the purity-based subtraction, whose bias in simulation is given in Sec. V A."

### NIT 3. Sec. VII C: "the error control above permits this" (A:909–911)
- **Before (B:913–915):** "…which the result above covers, since it holds for any stopping rule".
- **The problem:** "permits" is normative. The note (`sec_joint.tex`, §10.3) says that the bound "holds whatever rule determined when sampling stopped, including the budget extensions".
- **Fix:** "the error control above is unaffected by this, because it holds for any stopping rule".
- **Facts:** all are kept: the design fixed first, the reviewers' prior sight of the residuals, a bounded extension with p values visible, and the pointer.

### NIT 4. A split detached "with the joint-test estimator" from the 27-cell clause (A:663–670)
- **The problem:** in r12, the semicolon kept "With the joint-test estimator" governing both clauses. In r13, "For a coarser, non-nested partition … into 27 cells the envelope alone does not exceed it, …" is a sentence of its own.
- **Fix:** "For a coarser, non-nested partition … into 27 cells, the same estimator's envelope alone does not exceed it, …".

### NIT 5. "Three questions are distinct." introduces a statement (A:833–834)
- **The problem:** the first of the three sentences that follow, "The hybrid null is defined exactly on the finite grid and needs no convergence", is an assertion, not a question.
- **Fix:** "Three properties are distinct."

### NIT 6. Sec. I scope sentence (A:106–110)
- **After:** "The three- to five-observable results are central values, …; their intervals have no validated coverage, so the paper does not deliver a validated five-observable cross-section measurement."
- **Issue 1:** "results" now names both the central values and "the paper's main results" (the validation studies, A:72–73).
- **Issue 2:** "so" gives missing coverage as the only reason. Note §9.4 also prints that no reporting definition qualified and that "no five-dimensional measurement with total uncertainties was constructed".
- **Fix:** "The three- to five-observable outputs are central values …; their intervals have no validated coverage, and the paper does not deliver …".

### NIT 7. The source comment cites a file that does not exist (A:15–16)
- **The problem:** the comment reads "(scratchpad wt-reg3-work: triage.md, ledger.md, REPORT.md)", but there is no `REPORT.md` in `wt-reg3-work`. Triage #30 also cites "REPORT, unsure item 1".
- **Why it matters:** comments ship in an arXiv source.
- **Fix:** cite the committed ledger path, as the r12 ledger header does, or drop the scratchpad reference.

### NIT 8. C25 collapse: the rebuilt band's untested status is now only implied (A:452–454)
- **The problem:** "This rescoring is not an independent coverage test" does not say that the rescoring is the band's *only* test. The r12 text said so: "neither has been tested on independent pseudo-experiments".
- **Severity:** acceptable. The quoted block's status is explicit at A:443–444, and the rebuilt band is not quoted.

### Checked and found sound (no finding)
- **The four moves.** Each moved clause prints in the note section the paper cites, inside that section:
  - §7.1 at `sec_3d.tex:88–89`;
  - §3.1 at `sec_method.tex:43–44`, verbatim;
  - §3.2 at `sec_method.tex:200–203`;
  - §9.4 at `sec_5d.tex:311–314`, but see SHOULD-FIX 2.
  - The paper points to each one.
- **Guardrail on the moves.** Only the §9.4 target creates a false-as-read problem (SHOULD-FIX 2). Removing the effective-sample-size clause and "not recomputed" leaves no r13 sentence false or stronger. Sec. VIII still says that the central values "use the purity-based subtraction, with its bias of up to 4 %" (A:1082–1084).
- **The two collapses.**
  - **L2** (A:719–720): the Sec. VI sentence keeps "attributed" and "same origin … not established". The inference and correction clauses still print in Sec. V C (A:538–543).
  - **C25:** see NIT 8.
- **The flagged word swaps.**
  - "survives the nominal-truth bias correction" (A:538–539) is equivalent to note §9.5: "a residual bias that the nominal-truth bias correction does not remove".
  - "The covariance omits …" (A:463) is equivalent to "No block includes …", because the covariance is the block sum.
  - "The omission matters" (A:948) has a clear antecedent: "It has no band for the calorimetric hadronic-energy response" (A:940).
- **Other rewrites I checked.** None has a defect:
  - "The comparisons … use this covariance …; the calibration of the joint tests … does not use it" is supported by `sec_joint.tex:12–13`, "which they do not use".
  - "Under the specified envelope prescription, none …" keeps its scope.
  - In condition (iv), "measured for the mean only" stays beside D (r12 S3).
  - The GiBUU clause stays (r12 S4).
  - "A post hoc observation" stays (r12 S1).
  - The lost-pseudo-experiment sentence is consistent with §10.6 ("The lost seeds were therefore rerun").
  - "Fifth change" in the Table III caption matches "pooled over five truth changes" (A:733).
- **The seven sentence splits.** I found no qualifier detached in the seven splits the writer listed:
  - Sec. II, the external-prediction sentence ("They" = the predictions);
  - Sec. VII B, the three-way distinction (see NIT 5 for the wording);
  - Sec. VII B, the source-half sentence;
  - Sec. VII D (i);
  - Sec. VII D (iv);
  - Sec. VI, the D-ID scope sentence;
  - Sec. VIII, the last sentence.
  - The unlisted split in V D is NIT 4.
  - In the V C split, "The rate change itself is recovered …" now stands alone, but the "inferred … rather than measured directly" qualifier follows in the next sentence and matches note §9.5. It is acceptable.
- **The writer's ledger checker.** Run read-only, it reports "ledger rows 341, probes 470, failures 0". This matches the writer's claim. It does not catch SHOULD-FIX 1 or 2, because those probes test wording, not equivalence.

## D. Data availability proposal (`DA-proposal.md`; not applied)
- **Transcription.** The "current text" block equals `main_paper.tex`'s Data availability section with comments removed; I checked this with diff.
  - The `\pubhold` text in the draft is byte-identical.
  - `\napp` is defined at A:24, before `\input{paper_body}` ends.
  - `app:release` prints as App. H, and `app:release-scope` as H.1, per `main_note.aux`.
- **Destinations: all 23 rows are correct.** I opened `app_release.tex` and confirmed each "yes" quote at H and H.1 (release status at lines 10–31, scope at lines 33–55, identities at line ~57).
  - Rows 8 (numpy, scipy, matplotlib) and 16 (the Sec. VII A numbers) stay in the paper, as stated.
  - Row 17 is correctly flagged as needing an addition to H.
- **D-1 (SHOULD-FIX, draft).** "Apart from the multiplier scan, the other quoted numbers, and the event-level processing, require …" parses as a three-item list governed by "Apart from", which leaves the verb without a subject. Read that way, it exempts the other quoted numbers. Fix: "The other quoted numbers, except the multiplier scan, and the event-level processing require …".
- **D-2 (SHOULD-FIX, draft; the proposed note addition for row 17).** The wording is supported, with a caveat.
  - **Support.** `docs/publication/release/RC7-README.md:75–78` and `:105–106` say "fresh virtual environment, empty directory" and "`verify_rc.py` … exit 0 and 'VERIFY: PASS' if every replay and figure check agrees".
  - **Caveat 1.** This is RC7's own README, not an independent replay record. H.1's independent empty-directory replay was of "an earlier version" (RC1). The addition must not be worded as, or placed beside, the independent replay.
  - **Caveat 2.** The same README is stale on Fig. 1. It says that `make_figs.py` "reproduces the article's figure files byte for byte", including `paper_fig1_validation.pdf`. This was superseded when the 2D central value became LightGBM. Cite the README for the empty-directory run only.
- **D-3 (decision flag, not a defect).** The draft moves "The package carries the exact-split two-dimensional curve; Fig. 1 … regenerated separately" to H.
  - An earlier ruling, recorded in a `main_paper.tex` comment (plain-language pass 2, theme B, P6), says "the package's limitation stays here".
  - DECISION-20261021 (second) item 4 plausibly supersedes it. Joseph should know that adopting the draft reverses P6.
  - No sentence in the draft becomes false without it. The draft does not claim that the package reproduces Fig. 1.
- **Nothing stronger than the evidence.**
  - "Candidate", "not yet deposited" and "Apart from the multiplier scan" all stay.
  - "It recomputes …" matches H's "reproduces …".
  - The word counts are close to the writer's: I count about 247 words before and 135 after, with my own macro stripping.

## E. Register: surviving development history or bookkeeping (at most 8)
1. A:443–447: "Two earlier versions of the statistical band, distinct from the quoted block, were scored on 100 closure pseudo-experiments … The first undercovered in its tails". This is a history of superseded bands, and the SEC4 gate binds its numbers.
2. A:907–911: "The test design was fixed before any observed statistic was computed, although its reviewers had already seen descriptive per-cell residuals of the data. The calibration's computing budget was later extended by a bounded amount with observed p values visible". This disclosure is required.
3. A:911–914: "The pseudo-experiments that computing time limits interrupted or prevented (224 for calibration, 53 for power) were rerun; …".
4. A:366–368: "This learner was chosen after both comparisons were known, so the benchmark is a reproduction rather than an independent validation." This is a Table I guardrail.
5. A:583 (Fig. 3 caption): "panel (b) uses separate assessment seeds, which also entered its later development."
6. A:628–630: "…does not meet the validation criteria of its specification (Ref. [14], Sec. 9.6)." This is internal-record framing.
7. A:292–293: "the rule that set its five iterations is given in Ref. [14], Sec. 9.4." This is a bare bookkeeping pointer.
8. A:128–130: "from an earlier production of the MINERvA open-data release … (see Data availability)."

## Verdict: **ADOPT-AFTER-FIXES**
- **No BLOCKING finding.** Numbers, protected text and the four moves all check out.
- **Before adoption:**
  - Fix SHOULD-FIX 1 (the hydrocarbon clause: restore "do not re-grade … stand" and drop "as generated").
  - Fix SHOULD-FIX 2 (scope the note's §9.4 iteration-rule sentence, or restore the measure in the paper).
  - Fix SHOULD-FIX 3 (two words, "post hoc", and identify the second band).
- The NITs are optional.
- The DA proposal is fit for Joseph's decision once D-1 and D-2 are fixed.

## Counts
- **Hunks.** I read 36 diff hunks, all of them; 35 change printed text.
- **Numbers.** I compared 1021 and 1017 numeric tokens (319 distinct values in each). There are 4 differences, all explained.
- **Note targets.** I opened 11 note sections at the cited labels: §3.1, §3.2, §4.6, §5.2, §7.1, §9.4, §9.5, §10 intro, §10.3, §10.6, §10.9, and App. H/H.1.
- **Changed sentences.** I tested about 45 changed or removed printed sentences against r12 and the note, including the 4 moves, 2 collapses and 7 splits.
- **Triage and ledger.** I read all 47 triage rows and all 55 ledger lines that mention r13; I tested 14 of them in depth against the sources.
- **DA rows.** I checked 23 DA destination rows against `app_release.tex`.
- **Protected text.** I made 3 protected-text identity checks: source sha, printed tail and `\pubhold`.

## Not checked
- I did not check sentences unchanged between r12 and r13 against primary evidence, other than the out-of-scope note in SHOULD-FIX 3.
- I did not check the note's own sentences beyond the pointer targets and their immediate context. The r13 note PDF differs from r12 only in trailing bytes, the note sources being identical.
- I did not compare the primer or the PET note.
- I did not re-run the build or the SEC4 gate. I read the gate's patterns only to confirm that the proposed fix leaves them intact.
- I did not open primary records (RECORD-20260927, the rescore JSON or the RC7 replay receipts) beyond the RC7 README.
- I did not rate the register with any model.
