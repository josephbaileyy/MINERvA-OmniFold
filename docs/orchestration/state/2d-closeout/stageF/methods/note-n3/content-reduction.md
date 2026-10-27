# Analysis note: costed content-reduction list (for Joseph's decision)

**Prepared for** Joseph, through the director, at the director's request (n3 outline, question 4:
`docs/orchestration/state/2d-closeout/stageF/methods/note-n3/outline.md:106,113`). This is a list, not edits.
Nothing in the repository was changed.

**Text measured:** the round-3 worktree `wt-n3` at `e8c76937` ("[note] Register round n3: batches n3-B to n3-E"),
its `docs/analysis-note/*.tex` sources, and the `main_note.pdf` built from them (2026-10-26 16:46, 120 pages; no note
source is newer than the PDF). Blinded with the caveat study's own `tools/blind_note.py`, the note is **52,500
words** (the study measured 53,018 at `fe92211c`). Line numbers are those of the reflowed sources, where one line is
one paragraph.

**CITABLE FOR:** where each listed caveat prints in the round-3 sources; which records bind it; the measured size of
each proposed removal; the density estimate in §5 with its stated uncertainty.
**NOT CITABLE FOR:** any physics claim; an approval of any row (every row is Joseph's decision); a complete inventory
of caveats in the round-3 text (the inventories were coded on `fe92211c`, and caveats added since are not counted).

---

## 1. What this list can and cannot do (read first)

1. **The list does not close the R-N7 gap.** Applying every row (consolidations and drops) moves the note from
   about **7.1–8.2** distinct caveats per 1,000 words today to about **7.0–8.0**. The comparator range is 1.6–2.5 (§5).
2. **The reason is arithmetic.** The density counts distinct caveats. A consolidation keeps one home, so by
   construction it removes no distinct caveat; it only removes words, which raises the rate slightly. Only a drop
   lowers the count, and the 63 drop sites here remove about 17–29 of the 371–431 surviving distinct (kind, issue)
   pairs.
3. **The gap sits in the long tail, not in the repeats.** 253 of the 431 surviving distinct caveats are stated
   exactly once, and the density is about the same in every section (§6). To reach 2.5 at about 49,000 words the note
   could keep about 123 distinct caveats; to reach 1.6, about 79. That means removing **roughly 270–315 more**,
   about two thirds of all of them. Only removing secondary results together with their qualifiers would do that.
   That is the content decision R-N7 and R-P9 describe, and this list does not attempt it.
4. **What the list does buy:** about 3,300 words (6%); caveat statements per 1,000 words from about 17.0 to 15.1;
   restatements per caveat from 2.06 to about 1.89, at the top of the long comparators' 1.4–1.9 range. It also
   answers most of the passages sol2 quoted (§4).
5. **A decision this list puts to Joseph.** REPORT §8 notes that a collaboration-internal note may legitimately carry
   more caveats than the published long documents. Joseph may decide that 1.6–2.5 is not the target for this note,
   or that the target applies only after secondary results move out.
6. **Every DROP row needs a guardrail change.** The standing rule is "no fact leaves both documents"
   (`DECISION-20261021-joseph-register-loop-2.md` item 4; restated in `DECISION-20261025-joseph-prd-caveat-convention.md`
   item 4 and `DECISION-20261025-joseph-register-rounds-paper-rewrite.md` item 4). A drop is allowed only if Joseph
   lifts that rule for the fact, or names the internal records document (`main_records.tex`, cited as
   NoteRecords2026) as an allowed destination, as `DECISION-20261021-joseph-da-and-note-records.md` did for the record
   appendices.
7. **Two rows override director rules for round n3.** R01 and the ES/§12 parts of R17 remove executive-summary or §12
   restatements. The n3 outline kept these ("The ES and §12 restatements are summaries and stay",
   `note-n3/outline.md:48`).
8. **Already done.** Rounds n1–n3 already consolidated many body repeats: "descriptive central values" and "no
   mechanism" moved to the §7 lead (source comments at `sec_eavailw.tex:4`, `:102` and `sec_3d.tex:8`, `:139`), and
   the n3 ledger collapsed others (`note-n3/ledger.md`, rows C15, D-6, D-7, D-9). Inventory rows for those no longer
   print and are not counted here.

## 2. Method

- **Re-location.** Each of the 967 inventory rows (`caveat-study/inv/ours-note-body.tsv`, `ours-note-app.tsv`) was
  matched against the current sources, macros and comments stripped, by the longest run of consecutive words.
  - 660 rows match (≥80% of the quote);
  - 230 match partly (reworded);
  - 77 no longer print.
  - "Found" gives the low end of every count below and "found + partial" the high end.
- **Homes.** Each candidate was then searched in the current sources by its key phrases, so the homes listed include
  sites the coders never coded.
- **Bindings.** These come from `docs/orchestration/DECISION-*.md`, `docs/publication/DECISION-*.md` and
  `stageF/DRAFT-disclosures.md`, searched for "required disclosures", "must carry", "verbatim", "disclos" and
  "must".
- **Sizes.** Each proposed removal is one entry of a spec: a home, an anchor phrase, and K (keep), C (consolidate)
  or D (drop).
  - A tool takes the sentence holding each anchor, or the paragraph, or a counted clause where only a clause would go.
  - It counts that span's words.
  - It counts the coded inventory statements whose quotes fall inside the span.
  - It counts the distinct (kind, issue) pairs that lose every surviving statement.
  - Words are counted on the TeX source with macros as tokens, so they run about 5–7% below the blinded PDF count (the note's TeX sources total about 49,000 such words,
    against 52,500 blinded).
- **Quotes.** The quotes below are 6–15 words of the source with TeX markup stripped (`§` stands for a section
  reference). Each is greppable in the source by its plain words.
- **Working files.** These are scratch files, not in the repository; they reproduce every count.
  - `scratchpad/n3/cr/spec.txt`: every home and its K/C/D tag.
  - `cr/located.tsv`: the re-located inventory.
  - `cr/impact.txt`: the per-row totals.
  - `cr/tools/{locate,sent,impact,ctx,show}.py`.
  - `cr/note-raw.txt` and `cr/note-blind.txt`.
  - Rerun: `python3 -I cr/tools/impact.py cr/spec.txt cr/located.tsv`.
- **Not run:** the note's gates (`check_note_records.py`, `check_sec4_receipts.py`, the registry tests, the build).
  Any adopted row has to pass them. `docs/analysis-note/records-inventory-base.json` contains at least one dropped
  sentence ("Two provenance limits", R15).

**Key to each row.** *Homes* lists every current site: **[keep]** is the proposed single home or a qualifier that must
stay, **[C]** is removed by consolidation and replaced by a pointer, and **[D]** is removed outright. *Size* is
sites / coded statements removed / words removed.

---

## 3. The candidates

### R01. The "Principal limitations" list is printed twice — mixed (c, d) — CONSOLIDATE
- **Homes:**
  - [keep] `sec_summary.tex:46` "Principal limitations. The principal limitations, each stated in the body with the
    result";
  - [C] `sec_execsummary.tex:109` "Principal limitations: The body states each limitation with the result it
    qualifies".
  - The two paragraphs share 147 of §12's 198 words.
- **Action:** keep the §12 list, which is where R-N1 wants the principal ones restated. The executive summary points
  to it. The reverse also works.
- **Reader loses:** the one-page list on p. 2. Each item still prints in §12 or at its home. The three items only the
  ES list carries are at `sec_summary.tex:29` (purity bias), `sec_summary.tex:60` (tier 2) and `sec_intro.tex:37`
  (PET).
- **Number or claim:** no. The C₂ = 0.912 it quotes also prints at `sec_validation.tex:147`.
- **sol2:** N01 "The quoted 2D statistical block has had no coverage test"; N10b "The one five-dimensional covariance
  used in this note does not meet".
- **Size:** 1 paragraph / 10 / 265.
- **Bound:** the list itself is not bound, but its items are bound at their homes. Removing it overrides the n3 rule
  that the ES restatements stay.
<!-- absence-ok: quotes or summarizes the note's own text, before or after this round, as the round's record or as the decision list's quoted homes; not a new absence claim -->

### R02. Residual regularization bias, in no quoted uncertainty — (c) — NO REDUCTION AVAILABLE without removing claims
- **Homes:**
  - [keep] `main_note.tex:101` "residual bias, interpreted as regularization bias, that no quoted uncertainty
    includes";
  - [keep] `sec_5d.tex:77` "The Eavail and q_3 residuals, a regularization (unfolding-model) bias of the estimator,
    enter";
  - [keep] `sec_validation.tex:109` "regularization bias outside every quoted uncertainty";
  - [keep] `sec_systematics.tex:203` "the dependence on the regularization, and departures of the detector response";
  - [keep] `main_note.tex:73` "regularization bias is largest in this region";
  - [keep] `sec_execsummary.tex:57` "The high-Eavail, high-W region carries the largest regularization bias";
  - [keep] `sec_eavailw.tex:103` "and the regularization bias of Sec. 9 is largest at high Eavail";
  - [keep] `sec_summary.tex:19` "The regularization bias is largest in the high-Eavail, high-W region";
  - [C] `sec_5d.tex:61` "Their status in the quoted uncertainties is stated in §";
  - also in the R01 list.
- **Why nearly all stay:** this is the note's most restated caveat (21 coded statements). Every remaining
  restatement sits beside a printed high-Eavail, high-W excess statement. Joseph ruled for the paper that this
  statement stands only with "the largest-bias region stated" (`docs/publication/DECISION-20261006-joseph-publication-approvals.md`,
  addendum "Fig. 2 scope"). The same condition is read across to the note's matching sentences.
- **Reader loses:** nothing.
- **Number or claim:** **yes.** It qualifies the 74% residual (`sec_5d.tex:61`) and the excess statements.
- **Alternative:** convert the caveat into an assigned model-dependence uncertainty (REPORT §6, row 1). That changes
  numbers, needs its own decision, and is outside this list.
- **sol2:** none.
- **Size:** 1 / 0 / 10.

### R03. Generator comparisons are descriptive central-value comparisons with no mechanism — (d) — CONSOLIDATE
- **Homes:**
  - [keep] `sec_3d.tex:10` "The comparisons with generator predictions in this section and in Sec. 8 are"
    (descriptive, no mechanism);
  - [keep] `main_note.tex:68`, `:71`, `:77` (abstract) "comparisons locate no interaction mechanism";
  - [keep] the "(descriptive)" labels at `sec_execsummary.tex:51` and `:57`, which qualify the claims of their own
    bullets;
  - [C] `sec_3d.tex:123` "Figure X compares central values only";
  - [C] `sec_3d.tex:199` "used only for central-value comparison";
  - [C] `sec_eavailw.tex:110` "they do not locate an interaction mechanism";
  - [C] `sec_eavailw.tex:128` "These are central-value ratios; no compatibility metric is quoted, for the reason given";
  - also in the R01 list.
- **Reader loses:** per-figure reminders, already stated at the §7 lead.
- **Number or claim:** `sec_eavailw.tex:128` sits beside printed GENIE percentages (`\genieWmidLo`–`\genieWmidHi`).
  Without it a reader may look for a significance. The sentence stays true.
- **sol2:** N07 (`sec_eavailw.tex:5`, partly).
- **Size:** 4 / 4 / 33.

### R04. No 3D or 4D covariance is quoted — (c) — CONSOLIDATE, plus DROP of two hypothetical-covariance passages
- **Homes:**
  - [keep] `sec_3d.tex:10` "no 3D or 4D covariance is quoted, and no generator χ², p-value";
  - [keep] captions `sec_3d.tex:128`, `:167`, `:173` "Data … no error bars because no 3D covariance is quoted", and
    `:199` (each explains an absent error bar);
  - [C] `sec_method.tex:100` "no 3D or 4D covariance is quoted";
  - [C] `sec_systematics.tex:4` "A 3D budget built with the analogous 3D grid construction is not quoted";
  - [C] `sec_systematics.tex:300` "The 4D and extended-fiducial results have no covariance from this procedure";
  - [C] `sec_3d.tex:192` "No pulls or full-covariance χ² are reported (no corrected 4D covariance";
  - [D] `sec_3d.tex:132` "The 3D covariance, if quoted, would be the exact projection of the five-dimensional";
  - [D] `sec_3d.tex:189` "No 4D uncertainty is reported. Nor is any ratio of the unified-throw to" (the whole
    recipe paragraph).
- **Reader loses (D):**
  - that the 3D projection of the 5D covariance has been computed but is not used;
  - the recipe a corrected 4D covariance would follow.
- **Number or claim:** no. Note that "computed but not used" is a fact, so it needs the records destination.
- **sol2:** N06 "No 3D covariance is quoted (§7). The one that would"; N06 "No 4D uncertainty is reported. No 4D
  uncertainty magnitude".
- **Size:** C 4 / 4 / 61; D 2 / 5 / 119.

### R05. The one 5D covariance does not meet its specification, and its four measurements — (b, c) — CONSOLIDATE restatements only
- **Homes:**
  - [keep] `sec_5d.tex:250` "The covariance does not meet the acceptance criteria of its specification" (whole
    paragraph);
  - [keep] `sec_5d.tex:302` "Four measurements limit what the covariance supports";
  - [keep] `result_status_rows.tex:25` "One scalar-5D covariance, used although it has not met";
  - [keep] `sec_summary.tex:46` (R01);
  - [C] `sec_intro.tex:67` "The five-axis covariance used in this note and its four measured limitations";
  - [C] `app_negweight.tex:186` "That five-axis covariance does not meet the acceptance criteria of its
    specification" (about 60 of the paragraph's 119 words).
- **Reader loses:** nothing; App. C would point to §9.6.
- **Number or claim:** **yes.** It conditions every use of the covariance and its (Eavail, W) projection, including
  s_proj = 6.145% against 5% (`sec_5d.tex:306`).
- **sol2:** N08 "The covariance does not meet the acceptance criteria of its" and N08 "The specification requires the
  null bound to be fixed before". Both are kept: they are bound. Also N12 "That five-axis covariance is used although
  it does not meet" (removed), and N10b.
- **Size:** 2 / 0 / 68.
- **BOUND** by `DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md`:
  - §2: the defect is stated "in the same place as the decision";
  - §4: "Every deliverable built from this adoption carries" the four measurements, and Joseph calls them
    "measurements, not caveats".
  - The home paragraph and the four measurements cannot move.

### R06. 5D intervals miscover; the predeclared total-width criterion is not met — (c) — CONSOLIDATE
- **Homes:**
  - [keep] `main_note.tex:103` "Statistical intervals miscover at the tested truths" (abstract);
  - [keep] `sec_5d.tex:214` "No frequentist coverage is therefore claimed for any five-dimensional interval";
  - [keep] `sec_5d.tex:146` "so the total-width target cannot be met in RD1";
  - [C] `sec_5d.tex:4` "the failed five-dimensional coverage test (§)" (roadmap clause);
  - [C] `sec_5d.tex:8` "correcting a nominal closure bias does not establish coverage under other truths";
  - [C] `sec_5d.tex:135` "no reporting definition qualifies (next paragraph)";
  - also in the R01 list.
- **Reader loses:** forward references.
- **Number or claim:** yes, the abstract's "none … satisfies the predeclared 10% criterion" (`main_note.tex:104-105`).
  It is kept.
- **sol2:** none.
- **Size:** 3 / 4 / 46.

### R07. The generator tests' calibration is conditional — (c) — CONSOLIDATE (small)
- **Homes:**
  - [keep] `main_note.tex:107-108` "at a 5% family-wise error rate under the stated calibration assumptions";
  - [keep] `sec_joint.tex:106` "The decision rule therefore controls the familywise error rate of the ten decisions";
  - [keep] `sec_joint.tex:115` "The calibration is valid for the simulated null to the extent that";
  - [keep] `sec_execsummary.tex:77` and `sec_summary.tex:36` "controlled at 5% under the stated calibration
    assumptions";
  - [C] `sec_joint.tex:16` "Whether the calibration reproduces the analysis of the data is calibration fidelity";
  - [C] `result_status_rows.tex:32` "calibration adequacy remains conditional".
- **Why the ES and §12 sites stay:** each prints the FWER claim itself. The qualifier stays beside the claim wherever
  the claim prints (the director's reading in `DECISION-20261021-joseph-register-loop-2.md` item 4, and the KEEP list
  in `register-prd-study/REPORT.md` §5).
- **Reader loses:** nothing material.
- **Number or claim:** **yes,** the 5% FWER.
- **sol2:** none.
- **Size:** 2 / 6 / 18. The 6 is an overcount: the table row is one long "sentence".

### R08. No calorimetric recoil-response band in the generator tests — (c) — CONSOLIDATE
- **Homes:**
  - [keep] `main_note.tex:113` "omit an uncertainty on the calorimetric recoil response";
  - [keep] `sec_joint.tex:281` "The declared nuisance model here includes the reweights but no calorimetric response
    band" (home, `sec:joint5d-response`);
  - [keep] `sec_joint.tex:307` "The rejections are therefore conditional on the simulation's hadronic response";
  - [keep] `sec_joint.tex:139` "there is no recoil-energy-scale band in the analysis's systematic set". This is a
    condition quoted in the words of the test specification (`sec_joint.tex:5`).
  - [C] `sec_joint.tex:168` "The analysis has no band for the calorimetric recoil-energy response";
  - [C] `sec_joint.tex:354` "In particular, the hadronic response and the sub-fine-grid residual remain outside";
  - also in the R01 list.
- **Reader loses:** two pointers.
- **Number or claim:** yes, the ten rejections. The kept homes carry it.
- **Pending:** `DECISION-20261026-joseph-abstract-and-cresp-build.md` approves building C_resp, and Joseph will decide
  whether it joins the reported total. I did not verify whether C_resp reaches the joint tests' nuisance model. If it
  does, this whole row changes.
- **sol2:** none.
- **Size:** 2 / 2 / 29.

### R09. The detector-response-mismatch closure was never run; App. D describes its protocol — (c, d) — DROP App. D, CONSOLIDATE the rest
- **Homes:**
  - [keep] `sec_validation.tex:39` "None of these tests uses pseudo-data whose detector response differs from the
    unfolding";
  - [keep] `sec_validation.tex:57` "Every closure test here therefore keeps the simulated MINERvA response";
  - [keep] `sec_eavailw.tex:103` "It has not been run";
  - [C] `sec_validation.tex:61` "All retain the simulated MINERvA detector response";
  - [C] `sec_5d.tex:131` "All tests retain the simulated detector response";
  - [C] `sec_5d.tex:17` "Every study uses the analysis simulation's detector response, except the calibration";
  - [C] `sec_3d.tex:90` "it does not test response mismatch";
  - [D] `sec_eavailw.tex:103` "The response-mismatch closure of Appendix D is designed to test whether an incorrect";
  - [D] `sec_validation.tex:39` "Appendix D defines such a test, a closure that rescales only the reconstructed" and
    "No result from it is reported here";
  - [D] `sec_intro.tex:72` "Detector-response-mismatch closure (protocol implemented, not yet run)";
  - [D] `app_guide.tex:8` "a protocol implemented but not yet run (App. D)";
  - [D] `sec_validation.tex:118-119` "Response mismatch … Protocol implemented, not run" (table row);
  - [D] all of `app_response_mismatch.tex` (`:4`, `:6`, `:11`, `:13`, `:20`, `:22`, about 400 words), for example
    `:22` "This appendix records a validation protocol, not a result or an uncertainty".
- **Reader loses:**
  - the design of an unrun test (amplitude, outputs, the deferred correlated follow-up);
  - the acknowledgment at `main_note.tex:154`, which thanks Kevin McFarland for suggesting this closure, would then
    have no section to point to.
- **Number or claim:** no. The absence of the test is kept at three homes.
- **sol2:** N07 "The response-mismatch closure of Appendix D is designed to test"; N13, all six quotes ("A
  documented hadronic-response variation…", "The implementation runs only as a closure…", "It labels every output
  as a diagnostic…", "It is deferred unless…", "The reconstruction-only arm is intentionally cheap…").
- **Size:** C 4 / 3 / 42; D 13 / 15 / 488; 8 distinct pairs lost.
- **Bindings:**
  - `DECISION-20261014-joseph-2d-endpoint-and-open-items.md` item 2 deferred the closure's settings ("defer it").
  - The Fig. 2 addendum of `DECISION-20261006` requires the *absence* of the closure to be stated. It does not
    require the protocol, and the kept homes state the absence.
<!-- absence-ok: quotes or summarizes the note's own text, before or after this round, as the round's record or as the decision list's quoted homes; not a new absence claim -->

### R10. Point-cloud (PET) work is future work and supplies no result — (d) — CONSOLIDATE
- **Homes:**
  - [keep] `sec_intro.tex:37` "Point-cloud (PET) unfolding of the full event is future work, under development";
  - [keep] `app_pet_pointer.tex:5` (the pointer appendix);
  - [keep] `main_note.tex:117-118` (abstract) "this note uses no PET result";
  - [C] `sec_execsummary.tex:105` "Point-cloud (PET) studies are future work and contribute no result here";
  - [C] `sec_intro.tex:70` "Point-cloud (PET) representations (future work)" (table row);
  - [C] `sec_method.tex:44` "point-cloud representations are future work (App. F)";
  - [C] `app_guide.tex:9` "Future work. Point-cloud (PET) representations, documented separately";
  - [C] `selection_features.tex:20` "PET design-study recovery does not validate real-data background subtraction";
  - [C] `app_codebase.tex:16` "Point-cloud (PET) code under nd-unfolding/pet/ supports future work".
- **Reader loses:** reminders only.
- **Number or claim:** no.
- **sol2:** none.
- **Size:** 6 / 5 / 64.
- **Bound:** the abstract sentence is abstract text, so changing it is Joseph's own act. It is kept here.

### R11. The fine grid's convergence is not shown — (c) — CONSOLIDATE
- **Homes:**
  - [keep] `main_note.tex:114` "assume convergence of the fine grid on which the null hypotheses are defined";
  - [keep] `sec_joint.tex:148` "The fine-grid convergence check has not shown convergence" (home);
  - [keep] `sec_joint.tex:138`, which quotes the specification's condition (i);
  - [C] `sec_execsummary.tex:77` "That residual is unmeasured";
  - [C] `sec_joint.tex:16` "depends on the composition below the fine grid and on convergence of that grid";
  - [C] `sec_joint.tex:354` (shared with R08).
- **Reader loses:** nothing; the robustness-variant sentence at `sec_execsummary.tex:77` stays.
- **Number or claim:** yes, the rejections. The abstract and home are kept.
- **sol2:** none.
- **Size:** 3 / 1 / 24.
<!-- absence-ok: quotes or summarizes the note's own text, before or after this round, as the round's record or as the decision list's quoted homes; not a new absence claim -->

### R12. Extended fiducial: tier 2 is prior-dominated, and the value came from the purity battery — (c, d) — BOUND, almost no reduction
- **Homes:**
  - [keep] `sec_fps.tex:57` "Tier 2, prior-extrapolated, comprises the dead cells (∼28% of the rate)";
  - [keep] `sec_fps.tex:57` "The extended-fiducial central value was produced with the binned purity correction
    (the battery";
  - [keep] `app_negweight.tex:140` "was therefore produced with the binned purity correction, not";
  - [keep] `sec_fps.tex:26` "The quoted 2D result, with refined negative-weight subtraction, is … lower";
  - [keep] `sec_fps.tex:31` "this prior was not rebuilt after the flux repair";
  - [keep] `sec_execsummary.tex:92` "which form tier 2";
  - [keep] `sec_summary.tex:60` "separately labeled prior-dominated extrapolation contributes about 28%";
  - [C] `selection_features.tex:20` "Removing truth cuts adds extrapolation without adding selected data".
- **Reader loses:** one caption sentence.
- **Number or claim:** **yes.**
  - The tier-2 qualifier is printed beside the extended value at every site.
  - `sec_fps.tex:31` qualifies the ±1.5% prior envelope.
- **sol2:** N10a, all four (`sec_fps.tex:57`, `:31`, and two at `:26`). They are kept, because they are bound or
  qualify a number.
- **Size:** 1 / 1 / 9.
- **BOUND:**
  - `DECISION-20261026-joseph-fps-scope-r04-sensitivity-and-tex-reflow.md` §1: "Both sites print the short scope fix"
    (`sec_fps.tex:57` and `app_negweight.tex:140`).
  - `DECISION-20261024-joseph-adopt-re2-2d-refined.md` item 3: the RO-FPS wording was approved by Joseph
    (`sec_fps.tex:26`).

### R13. The 2D result is not independently validated — (c) — CONSOLIDATE
- **Homes:**
  - [keep] `main_note.tex:52-53` "That uncertainty is computed with the central value's own estimator … not been
    independently validated";
  - [keep] `sec_systematics.tex:198` "The result's intervals, bias and covariance have not been independently
    validated" (home);
  - [C] `sec_validation.tex:44` "What the remaining validation needs. The follow-up assessment distinguishes a
    proposed split-sample width check";
  - [C] `app_statmethods.tex:364` "(iii) It does not address coverage. The only 2D coverage test".
- **Reader loses:** `sec_validation.tex:44` also carries two points that `sec_systematics.tex:198` lacks:
  - a split-sample width check would give only conditional precision;
  - "a limit of the available inputs, not a general impossibility".
  - Keeping those two sentences cuts the saving to about 160 words.
- **Number or claim:** yes, the 2D covariance. The home and the abstract are kept.
- **sol2:** N01 "That uncertainty is computed with the central value's own estimator". It is kept.
- **Size:** 2 / 11 / 220.
- **BOUND:**
  - `DECISION-20261014` §2: "Full scientific closeout is NOT ACHIEVED, and the package must say so", with no
    coverage claim.
  - DRAFT-disclosures D1, adopted provisionally in `DECISION-20261018-joseph-2d-j3-j5-provisional.md` (J4 W1).
  - The home must keep D1's content.

### R14. History of the earlier 2D statistical band (failed coverage, rebuilt, rescored post hoc) — (a, b) — CONSOLIDATE, plus DROP of two post-hoc studies
- **Homes:**
  - [keep] `sec_validation.tex:135-171`, §5.2 `sec:coverage`. It includes:
    - `:135` "That band is an earlier one, not the quoted statistical block";
    - `:144` "The band fails: it undercovers in its tails";
    - `:150`;
    - `:160` "The attribution rule was fixed before the full run, but its clause";
    - `:162`;
    - `:171` "Post hoc rescoring against the rebuilt (since superseded) band".
  - [keep] `sec_validation.tex:173` "A re-test on held-out simulation would separate the two explanations; it has not
    been run".
  - [D] `sec_validation.tex:154` "The per-bin pattern below is descriptive and post hoc", with its bullets `:156`
    "Uneven in both directions" and `:157` "Where it is too narrow".
  - [D] `sec_validation.tex:173` "A post hoc diagnostic that bootstraps a single toy, under a decision rule".
  - [C] `result_status_rows.tex:14` "Earlier statistical band failed fixed-truth coverage; rebuilt band and quoted …".
  - [C] `sec_validation.tex:18` "earlier band fails. Rebuilt band awaits independent test".
  - [C] `sec_intro.tex:62` "2D fixed-truth coverage (first-built and rebuilt band)".
  - [C] `sec_method.tex:46` "the per-bin standard deviation of the earlier statistical band, which was built at
    seed 1".
  - [C] `sec_systematics.tex:53` "scored two earlier statistical bands, not this block".
  - [C] `app_statmethods.tex:467` "The fixed-truth test of § measured an earlier band against the estimator's own".
  - [C] `app_statmethods.tex:617-618` "Earlier statistical band vs. fixed truth … fails" (audit row).
  - [C] `app_statmethods.tex:634` "found the diagonal of the first-built C^stat undercovering in".
  - also in the R01 list.
- **Reader loses (D):**
  - the per-bin anatomy of the failure: 82 bins too wide, 35 with per-bin C₂ below 0.85;
  - the single-toy diagnostic that favours "toys scatter too little" over "data bootstrap too wide".
  - Both are labelled post hoc and descriptive.
- **Number or claim:** the kept section carries C₂ = 0.912 [0.907, 0.918] and the rescoring values. The two drops
  qualify no printed number outside themselves.
- **sol2:** N04 "This test asks whether the 2D statistical band quoted when"; N04 "That band is an earlier one" (both
  kept, bound); N04 "The attribution rule was fixed before the full run" (kept: a post-hoc disclosure); N04 "A post
  hoc diagnostic that bootstraps a single toy" (dropped); N01 (via R01).
- **Size:** C 9 / 13 / 136; D 4 / 5 / 195; 2 distinct pairs lost.
- **BOUND:**
  - KI-85, named in `DECISION-20261014` §2.
  - DRAFT-disclosures D2: "the history: the earlier statistical band undercovered … post-hoc rescoring is descriptive
    and partly circular; the held-out re-test is deferred". The note takes D2's sentence (J3 C4), and "keep the …
    rescoring, labelled historical" (J3 C7), both in `DECISION-20261018-joseph-2d-j3-j5-provisional.md`.
  - `DECISION-20261025-joseph-r18-history-to-note.md` item 1: the history "remains printed in the note, at
    sec:coverage".
  - The kept section and the held-out sentence cannot move.
<!-- absence-ok: quotes or summarizes the note's own text, before or after this round, as the round's record or as the decision list's quoted homes; not a new absence claim -->

### R15. Background treatment: why the 5D chain stayed on purity, and what uses which treatment — (a, e, c) — DROP the rationale and provenance, CONSOLIDATE the configuration lists
- **Homes:**
  - [keep] `main_note.tex:81-90` (abstract) "Closure tests that include backgrounds show a bias from the purity
    subtraction";
  - [keep] `sec_5d.tex:51` "It comes from the purity-based subtraction (§), enters no quoted covariance";
  - [keep] `sec_summary.tex:29` "Pseudo-experiments with backgrounds reveal a purity-subtraction bias of up to 4%";
  - [D] `app_negweight.tex:125` "The standard chain uses purity by choice, on two grounds (Ref., oi6-oi8-oi126)"
    (whole paragraph);
  - [D] `sec_method.tex:100` "they were produced before the purity bias was found and the refinement was"
    (history clause);
  - [D] `app_negweight.tex:8` "Two provenance limits apply to the production numbers: the driver revision";
  - [D] `app_negweight.tex:8` "this appendix establishes no supported production path and changes no default";
  - [C] `app_negweight.tex:8` "Every cross section and uncertainty quoted in this note uses the binned purity" (the
    configuration list, which restates Table 3 in `sec_method.tex`);
  - [C] `sec_3d.tex:81` "the figure is not redrawn for the configuration-(e) central value";
  - [C] `sec_3d.tex:206` "not redrawn for configuration (e)".
- **Reader loses (D):**
  - why the 5D central value was not switched off purity (and so still carries the 4% bias);
  - that the equivalence-study numbers' driver revision is corroborated, not pinned.
- **Number or claim:** the abstract's 4% bias and the 14-of-205 cells stay. `app_negweight.tex:125` explains the
  status of the quoted 5D central value; it does not qualify a number.
- **sol2:**
  - N02 "In five dimensions, the central value and its covariance use";
  - N12 "The standard chain uses purity by choice, on two grounds";
  - N12 "Second, switching would have required rerunning every unfold";
  - N12 "Two provenance limits travel with the production numbers";
  - all removed.
- **Size:** C 3 / 3 / 83; D 4 / 5 / 173; 3 distinct pairs lost.
- **BOUND:**
  - The abstract sentences are approved integration wording (`DECISION-20261024-joseph-approve-integration-wording-s1-compute-preserve.md`
    item 1; source comment at `main_note.tex`, W7).
  - The 2D adoption itself is `DECISION-20261024-joseph-adopt-re2-2d-refined.md`.
  - The dropped sentences are not bound, but "Two provenance limits" appears in `records-inventory-base.json`. Check
    `check_note_records.py` first.

### R16. Lost pseudo-experiments and their recovery — (b, c, e) — BOUND, minimal reduction
- **Homes:**
  - [keep] `sec_joint.tex:229` "A determinism check fixed in advance (16 of 16 completed seeds rerun bitwise";
  - [keep] `sec_joint.tex:231-235` "The scope of the recovery's checks is narrower than that of the main";
  - [keep] `sec_joint.tex:238` "The recovery is for reporting only: the primary decisions are those of the";
  - [keep] `sec_joint.tex:106` "A2 requires the lost pseudo-experiments to have been lost independently";
  - [keep] `sec_execsummary.tex:77` "The pseudo-experiments lost to time limits have been rerun, for reporting only";
  - [C] `sec_joint.tex:5` "the recovery of the lost pseudo-experiments and the later sensitivity studies" (roadmap
    clause);
  - [C] `sec_joint.tex:196` (Table caption) "the rest were lost to time limits and later recovered for reporting
    only".
- **Reader loses:** nothing.
- **Number or claim:** **yes,** the ten rejections and the 4.6 margin.
- **sol2:** N01 "The pseudo-experiments lost to time limits have been rerun" (kept); N09 "The section gives the design
  and the six conditions" (clause removed); N09 "The scope of the recovery's checks is narrower" and "the reading in
  which the recovered draws are added" (kept).
- **Size:** 2 / 1 / 20.
- **BOUND:**
  - `DECISION-20261005-s5p-recompute-extension-and-lost-seed-recovery.md` §5, "Required disclosures beside the claim":
    items 1–5 (report-only status, deterministic reruns, the 4.6 margin, the earlier stops, the scope of the checks).
  - Its "What it changes": the statement that every submitted draw was observed replaces the old qualifier. That
    makes the ES sentence part of the claim.

### R17. Process vocabulary: "fixed before", "set in advance", "predeclared", "no threshold on record" — (e, c) — DROP the vocabulary, CONSOLIDATE the threshold statement
- **Homes:**
  - [keep] `sec_3d.tex:87` "is not graded, because no acceptance threshold fixed before the test is on record";
  - [keep] the table cells `sec_validation.tex:89` and `:93` "no predeclared threshold";
  - [C] `sec_execsummary.tex:40` "No acceptance threshold fixed before either closure is on record";
  - [C] `sec_summary.tex:19` "No acceptance threshold fixed before either closure is on record";
  - [C] `result_status_rows.tex:25` "injected-bump closures have no recorded threshold";
  - [C] `sec_5d.tex:31` "no threshold set in advance";
  - [D] the phrase only, at:
    - `sec_validation.tex:97` "threshold 0.20, set in advance";
    - `sec_5d.tex:90` "whose criterion was set before it was run";
    - `sec_5d.tex:214` "set before the test was run";
    - `sec_5d.tex:77` "set before the test";
    - `sec_5d.tex:306` "set before production, on 2026-09-18";
    - `sec_summary.tex:46` "set before production";
    - `sec_joint.tex:34` "fixed before the calibration";
    - `app_statmethods_nd.tex:12` "fixed in advance";
    - `app_response_mismatch.tex:11` "fixed before the results are examined";
    - `sec_validation.tex:37` "predeclared suite";
    - `main_note.tex:105` "the predeclared 10% criterion" (abstract).
- **Kept as BOUND or required:**
  - `sec_joint.tex:115` (the joint-test pre-specification; R-P7's one exception; the budget-extension disclosure of
    `DECISION-20261004-s5p-production-budget-extension.md` §3);
  - `sec_joint.tex:229` (determinism "fixed in advance", `DECISION-20261005` §5 item 2);
  - `sec_5d.tex:250` (the null bound not fixed before production, `DECISION-20260920` §2);
  - `sec_validation.tex:160` (a post-hoc disclosure).
- **Reader loses:**
  - The threshold statement leaves the ES and §12. **This bears on a claim:** those bullets print the closure results
    (0.10 of the injected change; q₃ to 1.1%), and without the statement a reader may take them as passes.
  - The dropped vocabulary tells the reader that a criterion was not chosen after the result. That matters most in the
    abstract and at `sec_5d.tex:306` (the 5% bound of DECISION-20260920 §4, M1).
- **sol2:** N06 "This residual is not graded, because no acceptance threshold fixed" (kept at home); N10b "No
  acceptance threshold fixed before either closure is on record" (removed from ES and §12).
- **Size:** C 4 / 4 / 36; D 11 phrases / 11 / 49; 1 distinct pair lost.
- **Bound:** R-N6 (remove process vocabulary) is the study's rule, not a decision. The abstract phrase is Joseph's.

### R18. LightGBM was chosen after the comparisons; learner dependence is in no block — (b, c) — CONSOLIDATE
- **Homes:**
  - [keep] `sec_method.tex:77` "LightGBM was chosen for the central value after both comparisons with the
    publication";
  - [keep] `sec_systematics.tex:102` "No block contains the dependence on the learner";
  - [keep] `sec_execsummary.tex:28` "LightGBM was chosen over the exact-split estimator … after";
  - [C] `sec_summary.tex:13` "The central value and its uncertainty share the LightGBM estimator, which was chosen";
  - [C] `result_status_rows.tex:14` "learner chosen after the comparisons were known";
  - [C] `sec_systematics.tex:202` "the dependence on the machine-learning estimator: a per-bin median of 1.03%".
- **Reader loses:** nothing; the two homes stay.
- **Number or claim:** yes, the 1.03% (maximum 17.6%) learner difference, which stays at `sec_systematics.tex:102`.
- **sol2:** none.
- **Size:** 3 / 2 / 48.
- **BOUND:**
  - `docs/publication/DECISION-20261011-joseph-2d-central-lightgbm-seed42.md`, "Disclosures this requires" item 1
    (post hoc choice);
  - `DECISION-20261017-joseph-2d-adopt-s5-plus-playlist.md` §2 (the learner dependence "is in no block. It is
    disclosed").

### R19. Exact-split cross-check: provenance, seed and not-recomputed studies — (c, e, a) — DROP
- **Homes:**
  - [D] `sec_method.tex:77`: "Its seed was not fixed: the driver version it ran had no seed"; "The run's own log was
    not found"; "Two driver revisions regenerate it"; "It is not invariant to the estimator seed, however"; "The
    spread over seeds is unmeasured"; "The agreement of that median with the LightGBM seed-1 to seed-42 median … is a
    coincidence".
  - [D] `sec_method.tex:127` (table) "seed not fixed".
  - [D] `sec_systematics.tex:102` "One reseeded exact-split run differs from the unseeded one" and "The spread of the
    exact-split estimator over seeds is unmeasured".
  - [D] `sec_method.tex:100` "Studies in this note labeled exact-split use the exact-split central value".
  - [D] `sec_results.tex:88` "Taken with respect to the exact-split cross-check instead, the same combined
    covariance has".
  - [D] `app_statmethods.tex:284` "dividing the combined covariance by the exact-split cross-check instead gives".
  - [D] `app_statmethods.tex:379` and `:434` "(not recomputed for the LightGBM central value)".
- **Reader loses:**
  - the provenance and seed behaviour of the former central value, now a cross-check;
  - the flag that studies labelled exact-split were not redone.
- **Number or claim:** **yes, partly.** The exact-split χ²/ndf (`\chiPaperExact`, 3.66) still prints at
  `sec_execsummary.tex:28`, `sec_summary.tex:13`, `sec_results.tex:131` and `sec_3d.tex:68`, and supports the "about
  one unit" learner band (`sec_results.tex:131`).
  - Without the seed sentences, 3.66 reads as a seed-stable value. It is one seed setting; the reseeded run gives
    3.57.
  - If 3.66 stays, keep "the spread over seeds is unmeasured" (6 words), or the row changes a number's meaning.
- **sol2:** N02 "Its seed was not fixed: the driver version it ran" (both quotes); N02 "Studies in this note labeled
  exact-split use"; N05 "Taken with respect to the exact-split cross-check instead … 6.462%".
- **Size:** 14 / 9 / 204; 4 distinct pairs lost.
- **Bound at the time:** `DECISION-20261011` "Disclosures this requires" item 3 (reproducibility; XR's finding that
  the exact-split estimator is seed-dependent, 3.565 against 3.661). It was written when the exact-split value had
  just stopped being the quoted one. Whether it still binds is Joseph's reading.
<!-- absence-ok: quotes or summarizes the note's own text, before or after this round, as the round's record or as the decision list's quoted homes; not a new absence claim -->

### R20. Seed-42 provenance of the purity-subtracted 2D central value — (e, c) — DROP
- **Homes:**
  - [D] `sec_method.tex:46`: "Seed 42 was chosen on computing cost: building the statistical band at seed";
  - "The purity-subtracted seed-42 central value has no recorded run configuration";
  - "An independent rerun reproduces it to 1.4×10⁻¹¹";
  - "Both of those central values are regenerated to ≲2×10⁻¹¹ by runs with one".
- **Reader loses:**
  - why seed 42;
  - how the configuration-(a) central value, which the 5D chain and several figures still use, is shown to be
    reproducible without a recorded configuration.
- **Number or claim:** no printed number depends on it. The seed-1 to seed-42 difference (0.18% median) stays in the
  same paragraph.
- **sol2:** N02 "Seed 42 was chosen on computing cost".
- **Size:** 4 / 2 / 98; 1 distinct pair lost.
- **Bound at the time:** `DECISION-20261011` disclosures 2–3 (seed mismatch, reproducibility, written for the
  configuration-(a) value). As in R19, this is Joseph's reading.

### R21. 2D construction disclosures (G2, C_PL, July sweep KI-93, training noise X03, NormDISCC, C07′, J36, KI-94) — (c) — BOUND, one consolidation
- **Homes:**
  - [keep] `sec_systematics.tex:165` "an uncertainty assigned for an observed inconsistency between run periods whose
    cause is unknown";
  - [keep] `:170` "Because the block is built from the observed differences among the periods, it contains them";
  - [keep] `:219` "the approximation is not corrected. It was tested in two of the 187";
  - [keep] `:247` "The universe × retraining values and the band-centering numbers cannot be recomputed";
  - [keep] the July-sweep sentence near `:121`;
  - [C] `sec_systematics.tex:219` "Separately, retraining moves these two universes' shifts by a median 1.13–1.23",
    which `:247` states in full.
- **Reader loses:** nothing.
- **Number or claim:** **yes,** the 2D covariance.
- **sol2:** N03, all three current quotes ("The quoted universe block uses the July sweep", "Because the block is built
  from the observed differences", "In expectation such noise adds variance"). All kept: bound. The fourth N03 quote
  (the ten-seed 0.99% passage) no longer prints.
- **Size:** 1 / 1 / 14.
- **BOUND:**
  - `DECISION-20261014` §2 (KI 85, 88, 90–94, NormDISCC, C07′, G2, J36 and the playlist spread "disclosed"; Q5's
    declared convention).
  - `DECISION-20261015-joseph-g2-carry.md` §2.
  - `DECISION-20261015-joseph-playlist-consistency-term.md` ("unknown cause").
  - `DECISION-20261017` §3 (the double-ratio check "is passed by construction"; which period is right is unknown).
  - J4 W2 (D5's clause verbatim) and W9 (D11's two universes note only) of `DECISION-20261018-joseph-2d-j3-j5-provisional.md`.

### R22. App. A χ² material: the ours-only obstruction, the split bootstrap, the double count, the remaining refinements — (c, d) — DROP, keeping the bound scans
- **Homes:**
  - [keep] `app_statmethods.tex:474-492` "Regularization scans (earlier covariance; all cutoff-dependent)" with its
    table, and `:492`;
  - [keep] `app_statmethods.tex:503` "What is reported. The combined χ²/ndf = 0.929 is a descriptive distance";
  - [keep] `sec_results.tex:35` "with a regularization scan made for the exact-split cross-check on an earlier
    covariance";
  - [D] `app_statmethods.tex:457` "The real obstruction is statistical, not rank. Even at full rank (205) a
    defensible";
  - [D] `:467` "Data/MC split bootstrap. The data/MC split bootstrap was run on the earlier rebuilt";
  - [D] `:472` "An ours-only χ² must use our own C^ours. Its inverse remains regularizer-dependent";
  - [D] `:494` "Bootstrap/paper-stat double-count. The combined distance (§) adds C^boot to TotalCov";
  - [D] `:498` "Remaining refinements. The known band-independence exception, the Bashyal flux ↔ Muon_Energy_MINOS".
- **Reader loses:**
  - why no single ours-only χ² is quoted (it stays as one sentence at `:503`);
  - the data/MC split decomposition;
  - the explicit double-count arithmetic behind "descriptive";
  - the statement that the truncated pseudo-inverse is collaboration practice, from a private communication.
- **Number or claim:** the combined 0.929 keeps its "descriptive distance" qualifier at `:503` and
  `sec_results.tex:35`. The double-count paragraph (`:494`) gives the reason. Dropping it leaves the claim qualified
  but unexplained.
- **sol2:** N11 "We retain double-counted 0.929 as the well-defined …"; N11 "The collaboration uses the same
  truncated-spectral pseudo-inverse"; N05 "We therefore quote the per-bin pulls and the truncated result" (kept,
  bound).
- **Size:** 5 paragraphs / 14 / 521; 8 distinct pairs lost.
- **BOUND, partly:** `DECISION-20261018-joseph-2d-j3-j5-provisional.md` J3 C7 says "keep the regularization scan …
  labelled historical", and C5 says "the note keeps the descriptive χ² register". So the scans and `:503` are kept,
  and the dropped paragraphs are not bound.

### R23. "What the paper does not say" (about Ruterbories 2021) — not a caveat under the codebook — DROP, with the MAT-check sentence BOUND
- **Homes:**
  - [D] `app_statmethods.tex:229` "What the paper does not say. It gives no per-band covariance construction" (about
    60 words);
  - [keep] `app_statmethods.tex:231` "That check could not detect that the Flux band omitted those constraint weights".
- **Reader loses:** the inventory of what the published paper leaves to MAT. It is about other people's work, so the
  codebook does not count it.
- **Number or claim:** no.
- **sol2:** N11 "What the paper does not say" (dropped); N11 "That check filled the MnvH1D without MAT's per-universe
  weights" (kept).
- **Size:** 1 / 0 / 60.
- **BOUND:** `docs/publication/DECISION-20261012-joseph-adopt-2d-c04-repair.md`, "Disclosures required": "The earlier
  'MAT-conformant, byte-for-byte' check could not have caught this". This binds `:231`.

### R24. Scope disclaimers of the exact binned comparison — (d) — DROP two sentences
- **Homes:**
  - [keep] `sec_5d.tex:83` "The comparison is binned, signal-only and noise-free, at the simulation's detector
    response";
  - [D] `sec_5d.tex:83` "It does not address what unbinned or biased estimators could recover, the coverage";
  - [D] `sec_5d.tex:83` "The diagnostic establishes no impossibility, and the precision thresholds it proposes are not
    acceptance".
- **Reader loses:**
  - that the thresholds the diagnostic proposes are not acceptance criteria;
  - an explicit "no impossibility" disclaimer.
- **Number or claim:** the kept sentence carries the scope that the KEEP list requires ("binned, signal-only and
  noise-free" and the 38% population). The dropped sentences qualify no number.
- **sol2:** N08 "The comparison is binned, signal-only and noise-free" (kept part; disclaimers removed).
- **Size:** 2 / 0 / 43.

### R25. The 5D development samples are not independent validation — (c) — KEEP (listed because sol2 quotes it)
- **Homes:**
  - [keep] `sec_5d.tex:107` "Because these samples were used during development, they provide no independent
    validation here";
  - [keep] "Their assessment seeds are separate but also entered the estimator's later development".
- **Why it stays:** it is the only statement that the 5D validation is not independent. Without it the validation
  results read as independent.
- **sol2:** N08 "Because these samples were used during development".
- **Size:** 0.

### R26. 5D estimator fails the data-stability test — (c) — small DROP and CONSOLIDATE
- **Homes:**
  - [keep] `sec_5d.tex:90` "The candidate fails the data-stability test, whose criterion was set before";
  - [keep] `sec_5d.tex:90` "The baseline estimator's shifts, a median of 0.8 and at most 2.5, place";
  - [D] `sec_5d.tex:90` "The instability also explains the difference of at most 1.2% on data between the driver";
  - [C] `sec_5d.tex:192` "The study leaves the stability failure in place and does not transfer to".
- **Reader loses:** the explanation of the at-most-1.2% difference between the driver and the development pipeline on
  data.
- **Number or claim:** the 1.2% is printed only in the dropped sentence. Dropping it removes that number, so it is a
  fact that needs the records destination.
- **sol2:** N08 "The baseline estimator's shifts, 0.8 and 2.5, place this instability".
- **Size:** C 1 / 1 / 25; D 1 / 0 / 19.

### R27. GiBUU sample has no neutrinos above 20 GeV; NuWro and GiBUU are carbon, not CH — (c) — CONSOLIDATE (the 20 GeV pointer only)
- **Homes:**
  - [keep] `sec_3d.tex:116` "Its sample stops at E_ν≈20 GeV, so it is empty above p∥≈20" (home);
  - [keep] `sec_eavailw.tex:119` "it was generated only up to E_ν≈20 GeV";
  - [keep] `main_note.tex:75` (abstract);
  - [keep] `sec_joint.tex:142` (a quoted specification condition), `:168` "(v) GiBUU lacks E_ν>20 GeV", and `:26` (the
    test domain);
  - [C] `sec_eavailw.tex:5` "Section X discusses its E_ν≈20 GeV limit";
  - [C] `sec_execsummary.tex:57` "each by about its overall shortfall once GiBUU's E_ν≈20 GeV sample limit";
  - [C] `sec_summary.tex:19` "once the E_ν>20 GeV events missing from GiBUU are accounted for".
- **The carbon-versus-CH homes** (`main_note.tex:75`, `:115`; `sec_execsummary.tex:57`, `:77`; `sec_eavailw.tex:94`;
  `sec_joint.tex:331`, `:339`; `sec_summary.tex:36`) all stay.
- **Reader loses:** for the two ES and §12 clauses, the reason GiBUU's shortfall is quoted "once … accounted for".
  The phrase "each by about its overall shortfall" then reads less precisely. Keep the clause if that matters.
- **Number or claim:** yes, the generator shortfall comparison.
- **sol2:** N09 "The GiBUU re-evaluation is reported under the label 'B3 …'" (both quotes). Kept: bound.
- **Size:** 3 / 1 / 34.
- **BOUND:** `DECISION-20261020-joseph-nuwro-ch-claim.md`. The note carries the CH replays, "GiBUU's B3 label and its
  bias check", and the statement that the replays are descriptive.

### R28. Release appendix: the earlier RC1 replay — (a) — DROP candidate, Joseph's text
- **Homes:**
  - [D] `app_release.tex:42` "An earlier version of the package, RC1, was replayed from an empty directory";
  - other `app_release.tex` reproduction limits (`:4`, `:9`, `:29`, `:42`, `:50`) and the "Do not check a rank"
    guidance (`:88`): no proposal.
- **Reader loses:** that a clean-room replay of an earlier package passed.
- **Number or claim:** no.
- **sol2:** N14 "An earlier version of the package, RC1, was replayed". Also N14 "This appendix describes the local
  replay package", "The broader result package must contain every item", "A ✓ marks identities" and "Do not check a
  rank". No proposal for those, and N10b `sec_summary.tex:78` (release status) likewise.
- **Size:** 1 / 1 / 38.
- **BOUND:** release text is Joseph's (`DECISION-20261025-joseph-register-rounds-paper-rewrite.md` item 4,
  "Protected text … release text"; `DECISION-20261025-joseph-prd-caveat-convention.md`, "Not changed"). Any change to
  this appendix is his.

### R29. Finite-ensemble bias of the inverse: the superseded unified-throw example — (a) — DROP the example only
- **Homes:**
  - [D] `app_statmethods_nd.tex:16` "The superseded unified-throw 5D covariance has N=160, truncated p=100";
  - [keep] the rest of `:16` and `:19` "No generic correction is prescribed".
- **Reader loses:** a worked size (58/160 ≈ 0.36) for a superseded covariance.
- **Number or claim:** no current number.
- **sol2:** none.
- **Size:** 1 / 2 / 18.
- **BOUND:** `DECISION-20260910-joseph-b-deferred-and-finite-ensemble-disclosure.md` item 2 (finite-ensemble
  disclosure for endpoint A). The kept text carries it.

---

## 4. Every sol2 passage and where it lands

| piece | quote (first words) | current site | disposition |
|---|---|---|---|
| N01 | That uncertainty is computed with the central value's own estimator | `main_note.tex:52` | R13, kept (bound) |
| N01 | The pseudo-experiments lost to time limits have been rerun | `sec_execsummary.tex:77` | R16, kept (bound) |
| N01 | The quoted 2D statistical block has had no coverage test | `sec_execsummary.tex:109` | R01, removed with the ES list; home R14 |
| N02 | Seed 42 was chosen on computing cost | `sec_method.tex:46` | R20, DROP |
| N02 | Its seed was not fixed: the driver version (×2) | `sec_method.tex:77` | R19, DROP |
| N02 | In five dimensions, the central value and its covariance use | `sec_method.tex:100` | R15, history clause DROP |
| N02 | Studies in this note labeled exact-split | `sec_method.tex:100` | R19, DROP |
| N03 | The quoted universe block uses the July sweep | `sec_systematics.tex:121` | R21, kept (bound) |
| N03 | Because the block is built from the observed differences | `sec_systematics.tex:170` | R21, kept (bound) |
| N03 | In expectation such noise adds variance | `sec_systematics.tex:247` | R21, kept (bound) |
| N03 | For comparison, the mean of the earlier ten-seed LightGBM scan | — | no longer prints |
| N04 | This test asks whether the 2D statistical band (×2) | `sec_validation.tex:135` | R14, kept (bound) |
| N04 | The attribution rule was fixed before the full run | `sec_validation.tex:160` | R14, kept (post-hoc disclosure) |
| N04 | A post hoc diagnostic that bootstraps a single toy (×2) | `sec_validation.tex:173` | R14, DROP (re-test sentence kept) |
| N05 | We therefore quote the per-bin pulls and the truncated result | `sec_results.tex:35` | R22, kept (bound J3 C7) |
| N05 | The systematic row holds 43 bands | `sec_results.tex:123` | not a caveat (budget description); no row |
| N05 | The two maps are close because our result departs | `sec_results.tex:166` | single scope statement (d), ~25 words; DROP possible, not counted in §5 |
| N05 | Every block is computed with the LightGBM estimator … 6.462 % | `sec_results.tex:88` | R19, last sentence DROP |
| N06 | The closure's marginal scatter is far below … not graded | `sec_3d.tex:87` | R17, kept at home |
| N06 | No 3D covariance is quoted … The one that would be quoted (×2) | `sec_3d.tex:132` | R04, DROP |
| N06 | No 4D uncertainty is reported | `sec_3d.tex:189` | R04, DROP |
| N06 | The comparisons here and in §8.5 are made with unchanged figure code | — | no longer prints |
| N07 | In central values, Valencia 2p2h closes about half | `sec_eavailw.tex:5` | physics finding; R27 removes the 20 GeV pointer in it |
| N07 | The comparison with external generators depends on the generator | — | reworded; no longer prints as quoted |
| N07 | Like q3, and unlike Eavail, W changes under the lateral shifts | `sec_eavailw.tex:18` | method description, not a caveat; no row |
| N07 | The response-mismatch closure of Appendix D is designed | `sec_eavailw.tex:103` | R09, DROP ("not been run" kept) |
| N08 | The comparison is binned, signal-only and noise-free | `sec_5d.tex:83` | R24, disclaimers DROP |
| N08 | Because these samples were used during development | `sec_5d.tex:107` | R25, KEEP |
| N08 | The covariance does not meet the acceptance criteria (×2) | `sec_5d.tex:250` | R05, kept (bound) |
| N08 | The baseline estimator's shifts, 0.8 and 2.5 | `sec_5d.tex:90` | R26 |
| N09 | The section gives the design and the six conditions | `sec_joint.tex:5` | R16, roadmap clause C |
| N09 | The scope of the recovery's checks is narrower (×2) | `sec_joint.tex:231-235` | R16, kept (bound) |
| N09 | The GiBUU re-evaluation is reported under the label (×2) | `sec_joint.tex:339` | R27, kept (bound) |
| N10a | The extended-fiducial central value was produced with the binned purity | `sec_fps.tex:57` | R12, kept (bound) |
| N10a | The sample's mis-sampled flux … not rebuilt | `sec_fps.tex:31` | R12, kept (qualifies ±1.5%) |
| N10a | The quoted 2D result … no longer reproduces it; In the published sub-block | `sec_fps.tex:26` | R12, kept (bound) |
| N10b | Summary. The executive summary (p. 2) lists each result | `sec_summary.tex:4` | scope restatement (d), ~25 words; C possible under R-N5, not counted in §5 |
| N10b | No acceptance threshold fixed before either closure | `sec_execsummary.tex:40`, `sec_summary.tex:19` | R17, C |
| N10b | A local release candidate … no release has been tagged | `sec_summary.tex:78` | release text, Joseph's (R28) |
| N10b | The one five-dimensional covariance used in this note does not meet | `sec_summary.tex:46` | R01/R05, kept |
| N11 | That check filled the MnvH1D without MAT's per-universe weights | `app_statmethods.tex:231` | R23, kept (bound) |
| N11 | We retain double-counted 0.929 | `app_statmethods.tex:494` | R22, DROP |
| N11 | The collaboration uses the same truncated-spectral pseudo-inverse | `app_statmethods.tex:498` | R22, DROP |
| N11 | What the paper does not say | `app_statmethods.tex:229` | R23, DROP |
| N12 | Two provenance limits travel with the production numbers | `app_negweight.tex:8` | R15, DROP |
| N12 | The standard chain uses purity by choice (×2) | `app_negweight.tex:125` | R15, DROP |
| N12 | The choice of background treatment and the choice of covariance (×2) | `app_negweight.tex:186` | R05, C |
| N13 | all six (App. D) | `app_response_mismatch.tex:11`, `:13`, `:20` | R09, DROP |
| N14 | This appendix describes the local replay package; The broader result package; A ✓ marks; Do not check a rank | `app_release.tex:4`, `:50`, `:88` | R28, Joseph's text; no proposal |
| N14 | An earlier version of the package, RC1 | `app_release.tex:42` | R28, DROP candidate |
<!-- absence-ok: quotes or summarizes the note's own text, before or after this round, as the round's record or as the decision list's quoted homes; not a new absence claim -->

## 5. Totals and the density estimate

**Removed by the rows of §3** (from `cr/impact.txt`). "Statements" are coded inventory statements whose quotes fall
in a removed span: the first figure counts found-only rows, the second found plus partly matched rows. Words are
counted on the removed spans.

| | sites | statements | words | distinct (kind, issue) pairs removed |
|---|---|---|---|---|
| CONSOLIDATE rows | 61 | 54–77 | ~1,290 | 0 by construction (the tool reports 9–11, which are pairs a coder split by kind across homes) |
| DROP rows | 63 | 39–69 | ~2,030 | 17–29 |
| **all** | **124** | **93–146** | **~3,310 (6.3%)** | **17–29, or 26–38 counting the kind-split artifacts** |

The two single statements in §4 that are not counted here (`sec_results.tex:166`, `sec_summary.tex:4`) would add
about 50 words.

**Density, distinct caveats per 1,000 blinded words:**

| basis | now (52,500 words) | after all rows (~49,190 words) |
|---|---|---|
| inventory rows found and partly found (431 distinct) | 8.21 | 7.99 (8.17 without the artifacts) |
| inventory rows found only (371 distinct) | 7.07 | 6.99 (7.20 without the artifacts) |
| the study's figure at `fe92211c` | 8.41 | — |
| long comparators (set N) | 1.6–2.5 | 1.6–2.5 |

**Other measures, on the found-plus-partial basis:**
- statements per 1,000 words: 16.95 now, about 15.1 after;
- statements per distinct caveat: 2.06 now, about 1.89 after. The N range is 1.4–1.9 and the study's note value was
  2.17. On the found-only basis: 1.78 now, about 1.65 after.

**Method and uncertainty, plainly:**
- **The current count is not a fresh coding.** It is the 2026-10-25 inventory with the rows that no longer print
  removed. Caveats written into the text in rounds n1–n3 are not counted. So "now" is probably an undercount, and the
  true current rate may be higher.
- **The two bases bracket the matching uncertainty.**
  - A partly matched row may be a reworded caveat, which still prints.
  - It may also be a matched fragment of a deleted one.
- **Coder agreement is about ±25%** (REPORT §2.4), which turns 7.0–8.0 into roughly 5–10.
- **Removed statements are overcounted** where a removed span is a whole long sentence or table row that also holds a
  kept caveat (R07, R13). They are undercounted where a coder never coded a site (R05 shows 68 words and 0
  statements).
- **None of this changes the conclusion.** Every reading of the estimate stays at about three times the comparator
  ceiling or more.

**What reaching the range would take:** at about 49,000 words, 2.5 per 1,000 allows about 123 distinct caveats, and
1.6 allows about 79. From about 390 after this list, the note would have to lose about 270–315 more distinct
caveats. 253 of today's 431 are stated only once. So the remaining reduction cannot come from consolidation. It has
to come from removing the results that carry those caveats.

## 6. Where the distinct caveats sit (why no single block drop closes the gap)

Distinct (kind, issue) pairs whose every surviving statement is in one file, per 1,000 TeX words of that file. Removing
a whole block lowers the note's rate only where its rate is above the note's average of about 8.2.

| file | TeX words | statements | distinct only here | per 1,000 words |
|---|---|---|---|---|
| `app_response_mismatch.tex` | 411 | 10 | 7 | 17.0 |
| `app_statmethods_nd.tex` | 1,954 | 37 | 26 | 13.3 |
| `app_guide.tex` | 337 | 5 | 4 | 11.9 |
| `sec_systematics.tex` | 3,915 | 91 | 46 | 11.7 |
| `sec_validation.tex` | 2,661 | 79 | 28 | 10.5 |
| `app_negweight.tex` | 3,279 | 49 | 30 | 9.1 |
| `app_release.tex` | 1,655 | 26 | 14 | 8.5 |
| `sec_5d.tex` | 5,126 | 107 | 42 | 8.2 |
| `sec_fps.tex` | 880 | 18 | 7 | 8.0 |
| `app_statmethods.tex` | 6,653 | 99 | 51 | 7.7 |
| `sec_3d.tex` | 3,775 | 64 | 25 | 6.6 |
| `sec_joint.tex` | 5,664 | 94 | 30 | 5.3 |
| `sec_method.tex` | 2,998 | 31 | 13 | 4.3 |

**Worked example of a block drop.** Drop all of App. C, D, the N-D statistics appendix and the release appendix:
about 7,300 words and 77 distinct caveats. The note's rate goes from about 8.2 to about 7.8. The caveats are spread
evenly through the text, and that is the measured form of R-N7's finding: the excess comes from how many qualified
results the note reports, not from a few overgrown passages.

## 7. Records that bind the listed caveats (quick reference)

| record | what it binds | rows |
|---|---|---|
| `DECISION-20261014-joseph-2d-endpoint-and-open-items.md` §2 | "Full scientific closeout is NOT ACHIEVED, and the package must say so"; no coverage claim; KI 85, 88, 90–94, NormDISCC, C07′, G2, J36 and the playlist spread disclosed | R13, R14, R21 |
| `DECISION-20261015-joseph-g2-carry.md` §2 | the four contents of the G2 disclosure | R21 |
| `DECISION-20261015-joseph-playlist-consistency-term.md` | "observed run-period inconsistency of unknown cause … not … a measured systematic of a known source" | R21 |
| `DECISION-20261017-joseph-2d-adopt-s5-plus-playlist.md` §§2–3 | learner dependence "in no block … disclosed"; X02/X03 reported, not added; C_PL's check passed by construction | R18, R21 |
| `DECISION-20261018-joseph-2d-j3-j5-provisional.md` J3 C4, C5, C7; J4 W1, W2, W9 | the note takes D2's sentence; keeps the descriptive χ² register; keeps the regularization scan and rescoring "labelled historical"; D1's register; D5's clause verbatim; D11's universes in the note | R13, R14, R21, R22 |
| `stageF/DRAFT-disclosures.md` D1–D12 ("Must carry") | the content of each 2D disclosure (provisionally adopted through J3/J4) | R13, R14, R18, R21 |
| `DECISION-20261005-s5p-recompute-extension-and-lost-seed-recovery.md` §5 | "Required disclosures beside the claim", items 1–5 | R16, R17 |
| `DECISION-20261004-s5p-production-budget-extension.md` §3 | the budget extension decided while looks were visible | R17 (`sec_joint.tex:115`) |
| `DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md` §§2, 4 | the defect "in the same place as the decision"; four measurements carried by every deliverable | R05, R17 |
| `DECISION-20260910-joseph-b-deferred-and-finite-ensemble-disclosure.md` item 2 | the finite-ensemble disclosure | R29 |
| `docs/publication/DECISION-20261011-joseph-2d-central-lightgbm-seed42.md` "Disclosures this requires" 1–4 | the post hoc learner choice; seed mismatch; reproducibility | R18, R19, R20 (at the time) |
| `docs/publication/DECISION-20261012-joseph-adopt-2d-c04-repair.md` "Disclosures required" | the 6.87% omission; the flux block below the published one; that the MAT check could not have caught it | R23 |
| `docs/publication/DECISION-20261006-joseph-publication-approvals.md`, Fig. 2 addendum | the (Eavail, W) statement stands with the absent closure and the largest-bias region stated (paper; read across here) | R02, R09 |
| `DECISION-20261020-joseph-nuwro-ch-claim.md` | the note carries the CH replays, the B3 label and its bias check, and "descriptive" | R27 |
| `DECISION-20261024-joseph-adopt-re2-2d-refined.md` item 3 | Joseph-approved wording: C_model, RO-FPS, `\fpsAbove` | R12 |
| `DECISION-20261024-joseph-approve-integration-wording-s1-compute-preserve.md` item 1 | the approved integration wording (the abstract's background-treatment sentences) | R15 |
| `DECISION-20261025-joseph-r18-history-to-note.md` item 1 | the earlier-band history "remains printed in the note, at sec:coverage" | R14 |
| `DECISION-20261026-joseph-fps-scope-r04-sensitivity-and-tex-reflow.md` §1 | the short scope fix at both extended-fiducial sites | R12 |
| `DECISION-20261025-joseph-register-rounds-paper-rewrite.md` item 4; `-prd-caveat-convention.md` "Not changed" | release text, `\pubhold`, data availability and KI-85 are Joseph's | R28, R14 |
| `DECISION-20261021-joseph-register-loop-2.md` item 4 (restated 2026-10-25) | "no fact leaves both documents" | every DROP row |
