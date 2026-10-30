# r22 Step 1 — the gap diagnosis: report (2026-10-29)

**Under** [DECISION-20261029-joseph-register-rounds-reopen.md](../../../../../DECISION-20261029-joseph-register-rounds-reopen.md)
item 2, Step 1, by the rules fixed in [RULES.md](RULES.md) before any gap run (commit `6c9f3d29`). The rules were
then amended by the director's rulings and by Joseph's #521 and #522 (§4).
**Recorded by** the paper rewrite lane. **No text change:** this round edits neither the paper nor the note.

**CITABLE FOR:**
- the targets the stopping rule uses, re-measured: the paper anchors' P1 mean and the note anchors' P1N mean;
- the base at main `d84124c5`: P1 on the paper, P1N on the note's 15 pieces;
- what sol2 and gemini name as separating each document from a 4, with the raters' quotes and their own SHARE numbers;
- each named gap's class (PROTECTED, STRUCTURE, WORDING) under the committed rules as amended, by two independent
  classifications, in three states (committed, after #521, after #522), with every disagreement listed;
- the PROTECTED gaps as Joseph's choices, quoting the exact sentences ([PROTECTED-CHOICES.md](PROTECTED-CHOICES.md)).

**NOT CITABLE FOR:**
- any rewrite, or a prediction that a rewrite would move P1. The raters' SHARE values are their estimates, not
  measurements;
- the paper's quote-level detail without its low-power mark: the paper's planted control failed for both raters (§3);
- gemini on note pieces B06 and B08: both runs failed both attempts (§2);
- any physics claim, or the truth of any rater's proposed change.

---

## 1. Targets and base (part a)

All runs: P1 (`rater-calibration/prompts/P1.prompt.txt`, sha256 `4bbbf272…`) or P1N (`P1N.prompt.txt`, `46f5ded8…`),
unchanged since the calibration; sol2 (gpt-6.1-sol through codex-school2) ×3. All 69 runs logged `gpt-6.1-sol`, and
none needed a retry (`measure/status.tsv`).

| | runs | mean |
|---|---|---|
| Paper anchors (P1): A 3.5, 3.5, 3.5; B 3.5, 3.5, 3.5; C 4, 4, 4 | 9 | **3.667** |
| Note anchors (P1N): AT1 4, 4, 4; AT2 4, 4, 4; AP1 4, 4, 4; AP2 3.5, 3.5, 3.5 | 12 | **3.875** |
| Paper base, `d84124c5` (P1): 3, 3, 3 | 3 | **3.00** |
| Note base, `d84124c5` (P1N), mean over 15 pieces | 45 | **3.122** |

- Both anchor means equal the calibration's (`rater-calibration/REPORT.md`, `NOTE-BASELINE.md`).
- The anchor texts were rebuilt from the calibration's recorded commands, because its scratch copies had been swept.
  Each rebuilt copy matches the recorded word count exactly (paper A 8,148, B 8,992, C 8,583; note AT1 5,822, AT2
  4,214, AP1 8,062, AP2 9,886) and its source PDF digest (T2K `360f1f4e…`, PDSP `4e3a981f…`). Their digests are in
  `measure/ANCHORS.SHA256SUMS`. The texts of published papers are not committed, as in the calibration.
- The paper base is the rater copy from `make_rater_copy.sh`, sha256 `a945a490…`, 7,465 words. It is byte-identical to
  r21 NEW (`r21/measure/new/r21new.blind.txt`).
- The note base is `main_note.pdf` at `d84124c5` (sha256 `33847dc3…`), cut by `tools/split_base.py` into the 15 pieces
  in `base/pieces/` (55,967 words). The split fails if an author, affiliation, e-mail, repository owner or hold
  survives. It fired once, on a placeholder clause that pdftotext wraps across a line, and that is fixed.
- Note piece means: B05 (Sec. 6) and B07 (Sec. 8) 3.5, 3.5, 3.5; B01 3.5, 3, 3.5; B04 3.5, 3.5, 3; B11 3, 3, 3.5. The
  other ten pieces are 3, 3, 3.

**The limit on what the stopping rule can see** (director's addition 2):
- **P1N barely resolves the 3 band.** 34 of the 45 base runs are exactly 3.0. The director was earlier told 35; the
  re-count from the run files gives 34. Only two pieces score 3.5 in all three runs.
- **The paper is the same.** Every P1 sol2 run since r11 has given 3 (the decision record, "What led to it"), and so does this base.
- **So a round can improve the text without moving P1.** The stopping rule's "three rounds with no P1 movement" can be
  reached that way.

## 2. The gap runs (part b)

36 runs, as committed (RULES.md §4): G1 on `paper` and `paper-ctl`, G1N on `B01`–`B15` and `B09-ctl`, each × sol2 and
gemini, through `register-method/tools/run_x.sh` (unchanged) by `tools/gapjob.sh` (one retry).

- **34 runs count.** Every one has a CURRENT RATING, 7 to 12 gaps and an ENOUGH line, and every run's SHAREs sum to
  100.
- **gemini on B06 and B08 failed both attempts.**
  - Attempt 1 printed a complete answer and never exited; I killed it after 36–39 min (status `killed-noexit`).
  - Attempt 2 did the same and hit the 15-min timeout (rc=124).
  - By the attempt rule (rc 0), both runs fail. Their four outputs are kept in `gap/runs-noexit/` and are used
    nowhere.
  - The note × gemini figures below are over the other 13 pieces (director's ruling 1).
- **The hangs were gemini's alone.**
  - 7 of the 23 gemini attempts hung after writing a complete answer.
  - 5 of the 18 gemini runs hung on their first attempt: B03, B06, B08, B11 and B12. B03, B11 and B12 then succeeded
    on attempt 2.
  - No sol2 attempt hung.
  - The director was earlier told "7 of 18 gemini runs"; the count is of attempts.
- **The timeout was added after the rules commit, in two steps.** Neither changes a prompt, input or rule.
  - `94e57cb4`: each attempt runs in its own process group, killed after 900 s.
  - `114ca3d4`: on a timeout the function waits for the watcher's KILL. In the first version, one agy process
    survived the timeout, because the function killed its own watcher before the KILL step and agy ignores TERM. I
    killed that process by hand.
  - `tools/test_with_timeout.sh` tests the function both ways: hangs return 124 with no survivor, and fast exits keep
    their status. Its agy-shaped fixture passed on both versions, because the race never occurred in it. **The fix
    rests on its construction, not on a reproduced failure.**

**CURRENT RATING from the gap prompts.** G1 and G1N carry P1's and P1N's scale, so these are a calibration fact. They
are reported beside the anchors' P1 and P1N scores, and no inference is drawn (director's ruling 4).

| | sol2 | gemini |
|---|---|---|
| paper, paper-ctl | 3, 3 | 2, 2 |
| note pieces, B09-ctl | 3 on every piece except B07 (3.5); B09-ctl 3 | 2 on every valid piece and B09-ctl |
| anchors, P1/P1N (§1) | paper 3.67, note 3.875 | not run |

**ENOUGH** (director's addition 1). All 34 counted runs, and both controls of each rater, answer Yes. No rater says
that its listed changes would fall short of 4, so no ENOUGH sentence goes to Joseph as a reservation. Every line is
quoted verbatim in [ENOUGH.txt](gap/ENOUGH.txt). Two examples:
- sol2, paper: "Yes; applied consistently throughout, these language changes would bring the manuscript to 4 without
  requiring different scientific findings, additional studies or removal of substantive limitations."
- gemini, paper: "Yes, implementing these changes in full would remove the pervasive internal-note
  characteristics—including private citations, record-keeping logs, defensive disclaimers, and local jargon—bringing
  the manuscript into the typical register of a published PRD paper."

## 3. The planted controls

The pass rule (RULES.md §3) is that the rater quotes at least 2 of the 3 plants.

| control | sol2 | gemini |
|---|---|---|
| B09-ctl (note) | 3 of 3, **PASS** | 3 of 3, **PASS** |
| paper-ctl | 1 of 3, **FAIL** | 1 of 3, **FAIL** |

- **The verdict stands as committed** (director's ruling). The controls were not rerun, and the pass rule was not
  amended.
- **What the paper failure means.** The paper's two real runs are reported as **control failed, low power**. A quoted
  gap in them can stand for several passages, and the raters assigned their SHAREs to such grouped gaps.
- **The note is unaffected.** Its controls pass, and each plant was its own gap with SCOPE "this passage".
- **Descriptive evidence only, not an amended verdict.**
  - On the paper, both raters quoted plant 1 as one "pattern" gap (sol2: "about 4 passages like it"; gemini: "about 3").
  - sol2's CHANGE for that gap reads, verbatim: "Delete the revision-ticket sentence, the z2m/tier-S/FIVED16 sentence,
    the “just to be safe” rerun sentence, and the announcement that a limitation is stated “only here,” retaining any
    necessary methodological information in direct scientific prose."
  - Beside the three plants, it names r21's truth-fix sentence, "The low stability of four of the sixteen cells is
    stated only here." (paper-s-10 below).
  - gemini's CHANGE names no plant individually: "Delete all internal issue-tracking tickets, continuous-integration
    build notes, and informal logbook remarks from the text and figure captions."
- **Next, G1b.** To recover the paper's resolution, the director has ruled a new, pre-declared paper diagnosis, G1b,
  after this report.
  - It changes only the format: SCOPE "this passage" only, one gap per passage, and up to 20 gaps.
  - It uses the same plants at new positions, chosen by the same rule, and the same pass rule, committed before it runs.
  - It is a new round, not a retry, and it has not been run.
  <!-- absence-ok: states that a planned diagnosis is still to come; not a claim that a result is absent -->

## 4. Classification (part c)

- **Location.** Each QUOTE is located by the calibration's `analyze.py` rule. Two are UNVERIFIED and not classified:
  paper-g-05 and B12-g-02.
- **Two classifications.** I classified every gap from [CLASSIFY-BRIEF.md](CLASSIFY-BRIEF.md). A fresh read-only
  agent classified every gap from the same brief, without seeing my classification ("lane" and "independent" below).
- **Corrections to my first pass,** made from the rated text before the final count:
  - paper-s-06 is in the paper's abstract, so it is A4;
  - B12-g-09's seed list also prints in the note's Sec. 4.3, so it is STRUCTURE.

**Three states, each applied to both classifications:**
1. **Committed:** RULES.md §5, as amended by the director's rulings on this round.
   - **Records** (ruling 2): a cut of records from the note is STRUCTURE only where the repository's records document
     keeps the fact, and each such gap names that home. Without a home, it is PROTECTED (B2).
     - The note's "Ref. [37], R1.n" is the n-th entry of `app_provenance.tex`'s description lists: R1.3 flux-repair
       :94, R1.14 response-diagnostic :112, R1.16 july-sweep :114.
     - Where the entry lacks the specific number, the cut is PROTECTED. Examples: B03-g-03, the 0.27 ratio to the
       ten-seed block; B13-g-01, N = 160, 0.363, 2.76.
   - **Implementation detail** (ruling 3): my brief's first reading, which made these cuts STRUCTURE, was not adopted,
     since it narrowed B2 after the outputs existed. Cuts of implementation detail that would leave both documents form
     the sub-class PROTECTED-B2-DETAIL.
2. **After #521** ([DECISION-20261029-joseph-relax-b2-internal-ledger.md](../../../../../DECISION-20261029-joseph-relax-b2-internal-ledger.md)).
   - A sub-class gap that names a ledger record keeping the fact (a file:line at `d84124c5`, opened and checked) is
     STRUCTURE (cut). Without one, it stays PROTECTED.
   - Limitations, disclosures, qualifiers, and reported numbers and findings still need a published home.
3. **After #522** ([DECISION-20261029-joseph-limitations-may-leave-paper.md](../../../../../DECISION-20261029-joseph-limitations-may-leave-paper.md)).
   - A limitation or disclosure may leave the paper when the note keeps it. Such a move or cut is STRUCTURE, with a
     pointer and a probe in the round that makes it.
   - B1, B3, A1, A4, A5, A7, B4 and the FROZEN phrase are unchanged. #522 concerns only the paper, so no note row
     changes.
   - **One reading flagged for the director.** Item 1 lists the §I coverage sentence among the placements that may
     leave the paper, while item 2 keeps "the FROZEN … phrases" unchanged. Both classifications read it as: the
     sentence may move to, or be consolidated with, the note's copies, but not be reworded or replaced. Under that
     reading paper-g-03 (replace it) stays PROTECTED, and paper-s-02 (consolidate) is STRUCTURE in both.
   - Rows #522 moved:
     - lane: paper-s-10 (the low-stability item moves to its result, so the preceding sentence stays true);
     - independent: paper-g-06 (the note keeps the missed target, B08 Sec. 9.4) and paper-s-02.
   - The lane keeps paper-g-06 PROTECTED (B1). Its change, as a pattern, also removes C20's "fails its specified
     acceptance criteria" where Fig. 3's band uses that covariance.

**Agreement on the 285 classified gaps:** 248 (87.0 %) committed; 247 (86.7 %) after #521; 248 (87.0 %) after #522.
- Every disagreement is in `gap/compare-<state>.txt` and `gap/disagreements-<state>.tsv`, with both reasons.
- After #522, 18 of the 37 disagreements are PROTECTED against STRUCTURE: whether a cut fact still prints elsewhere in
  the same document, or whether a records entry holds the exact number.
- The ones that touch Joseph's text or a judgement the rules do not settle, after #522:

| gap | lane | independent | the point |
|---|---|---|---|
| paper-g-06 | PROTECTED (B1, C20) | STRUCTURE (note B08) | does the pattern also strip C20 from Fig. 3's band? |
| paper-s-08 | UNRESOLVED (C13, F277) | WORDING | rewording "does not cover", which the paper-protections ledger (F277) probes verbatim |
| B14-g-02 | UNRESOLVED | PROTECTED (B2) | deleting the credit to Kevin McFarland for a suggestion |
| B12-g-04 | PROTECTED (B2, no single home) | STRUCTURE (a home per label) | the note's table of repository labels |
| B01-g-02 | PROTECTED (C9) | STRUCTURE | the Executive summary's lost-draw sentence; is Sec. 11.6's copy enough? |

## 5. Counts (part d)

- **Counting rule.** Per run, a class's share is the sum of its gaps' SHAREs; no run needed rescaling. For the note,
  the share is the mean over pieces, with equal weight.
- **Pieces counted.** sol2 is given over all 15 pieces and over the 13 that gemini has.
- **Reading the tables.** Shares are percent of the distance to 4, by the raters' own numbers. P is PROTECTED, D is
  PROTECTED-B2-DETAIL, S is STRUCTURE and W is WORDING. UNRESOLVED and UNVERIFIED make up the rest of each 100.

**Lane classification:**

| document × rater | committed: P / D / S / W | after #521: P / S / W | after #522: P / S / W |
|---|---|---|---|
| paper × sol2 (low power) | 13.0 / 0 / 40.0 / 42.0 | 13.0 / 40.0 / 42.0 | **10.0 / 43.0 / 42.0** |
| paper × gemini (low power) | 50.0 / 0 / 40.0 / 0 | 50.0 / 40.0 / 0 | **50.0 / 40.0 / 0** |
| note × sol2, 15 pieces | 1.9 / 1.8 / 48.6 / 47.7 | 1.9 / 50.4 / 47.7 | **1.9 / 50.4 / 47.7** |
| note × sol2, same 13 | 1.2 / 2.1 / 47.5 / 49.2 | 1.2 / 49.5 / 49.2 | **1.2 / 49.5 / 49.2** |
| note × gemini, 13 pieces | 50.5 / 6.8 / 8.8 / 31.6 | 52.3 / 13.8 / 31.6 | **52.3 / 13.8 / 31.6** |

- The rest of each 100: paper × sol2 5.0 UNRESOLVED; paper × gemini 10.0 UNVERIFIED; note × gemini 1.2 UNRESOLVED
  and 1.2 UNVERIFIED.
- P + D (committed): note × sol2 3.7 (15 pieces) and 3.3 (13); note × gemini 57.2.

**Independent classification:**

| document × rater | committed: P / D / S / W | after #521: P / S / W | after #522: P / S / W |
|---|---|---|---|
| paper × sol2 (low power) | 30.0 / 0 / 23.0 / 47.0 | 30.0 / 23.0 / 47.0 | **10.0 / 43.0 / 47.0** |
| paper × gemini (low power) | 50.0 / 0 / 40.0 / 0 | 50.0 / 40.0 / 0 | **40.0 / 50.0 / 0** |
| note × sol2, 15 pieces | 8.6 / 1.8 / 41.5 / 48.1 | 8.6 / 43.3 / 48.1 | **8.6 / 43.3 / 48.1** |
| note × sol2, same 13 | 9.0 / 2.1 / 40.5 / 48.5 | 9.0 / 42.5 / 48.5 | **9.0 / 42.5 / 48.5** |
| note × gemini, 13 pieces | 46.1 / 9.5 / 17.5 / 25.8 | 47.0 / 26.1 / 25.8 | **47.0 / 26.1 / 25.8** |

- The rest of each 100: paper × gemini 10.0 UNVERIFIED; note × gemini 1.2 UNVERIFIED.
- P + D (committed): note × sol2 10.4 (15 pieces) and 11.1 (13); note × gemini 55.6.

**Gap counts (285 gaps):**

| state | lane: P / D / S / W / unresolved / unverified | independent: P / D / S / W / unverified |
|---|---|---|
| committed | 73 / 10 / 68 / 130 / 2 / 2 | 71 / 13 / 73 / 126 / 2 |
| after #521 | 75 / 0 / 76 / 130 / 2 / 2 | 72 / 0 / 85 / 126 / 2 |
| after #522 | 74 / 0 / 77 / 130 / 2 / 2 | 70 / 0 / 87 / 126 / 2 |

**What the counts say, from the raters' own reasons:**
- **sol2:** about half its share is WORDING, and almost all of the rest is STRUCTURE. After #522 its PROTECTED share is
  10 % on the paper and 1–9 % on the note, depending on the classifier. Its CHANGE sentences mostly say "retaining" or
  "preserving" the qualifications, and every sol2 ENOUGH line says the changes would reach 4 without removing
  substantive limitations.
- **gemini:** 40–52 % of its share is PROTECTED, in both documents and under both classifications. Its CHANGE sentences
  mostly delete or "neutrally" reframe limitations, disclosures and qualifiers in the note, which B2's published-home
  condition and the guardrail keep. On the paper they reword the abstract, the FROZEN sentence and the KEEP rule.
- **No inference.** After #522, a round that targets only WORDING and STRUCTURE gaps covers this much of each rater's
  named distance to 4, depending on the classifier:
  - sol2: 85–90 % on the paper and 91–98 % on the note;
  - gemini: 40–50 % on the paper and 45–52 % on the note.

  How far P1 would move is not measured here.
  <!-- absence-ok: scopes this report; not a claim that a result is absent -->

## 6. Choices for Joseph (PROTECTED gaps)

[PROTECTED-CHOICES.md](PROTECTED-CHOICES.md) lists every gap that either classification calls PROTECTED after #522: 84
gaps, 60 of them called PROTECTED by both. Each gives:
- the exact sentence the rater quoted;
- the rater's change;
- its SHARE;
- both classifications' reasons.

They are grouped by the protection that keeps them. None has been reworded around, and each is a choice: keep the text,
or allow the change.

#522 item 3 applies to most of them: a rater asks for a limitation, disclosure, qualifier or number to leave the note
too, the B2 and C-item rows of the note. Those go to Joseph as named choices, and the file quotes each sentence with the
rater's reason.

| protection | gaps | what the raters would change |
|---|---|---|
| B2 (a fact leaving both documents; after #521, facts other than ledgered detail) | 35 | delete limitations, provenance limits, findings and numbers that print nowhere else |
| B1 (truth guardrail) | 19 | drop or "neutrally" reframe qualifiers such as "they are context only", "must not be quoted", "not yet run"; or assert a public release, or seed stability |
| C2 (KI-85 and the earlier band's history) | 6 | excise "has not been run", "not registered in advance" and the earlier band's history |
| A4 (the abstracts) | 5 | reword or restructure the paper's and the note's abstracts |
| C1, C9 (endpoint not established; the joint tests' lost draws and budget) | 4 each | replace "has not been established" with agreement statements; remove the lost-draw and budget disclosures |
| A7 (claims) | 3 (more as secondary items) | assert what the note does not state: a bounded systematic uncertainty, target-corrected tests as an evaluated systematic, a changed deferral condition |
| C8 | 2 | drop "chosen after both comparisons were known" |
| A1, B3, C4, C5, C7, FROZEN | 1 each | the Data Availability text; the five-iteration rule; NormDISCC "unconfirmed"; the run-period cause; the flux reason; replacing "Interval coverage has not been validated." |
<!-- absence-ok: the table quotes printed limitation wording that raters would change; not a claim that a result is absent -->

**The B2-detail question, now answered by #521.**
- The director had put it to Joseph as one choice: whether B2 applies to pure implementation detail. Under the
  committed rules the sub-class held 10 gaps in the lane's classification and 13 in the independent one's.
- Three representative sentences, verbatim from the note:
  - B02-g-04, "Reconstructed events require … a muon track with θµ < 20◦ matched to a MINOS track with a passing fit
    (isMinosMatchTrack==1 && minos_trk_is_ok==1), …". Ledger home: `2d-unfolding/2D_OMNIFOLD_REFERENCE.md:464-479`.
  - B12-g-03, "The comparison calls np.linalg.pinv at its default, NumPy's documented cutoff τ = rcond · σmax with
    rcond = 10−15 ; this is not the n σmax εmachine convention of np.linalg.lstsq and MATLAB." Ledger home:
    `app_history.tex:145`.
  - B15-g-03, "Driver (Python): per-analysis orchestration in 2d-unfolding/unfold_2d_omnifold_unbinned.py and its N
    -dimensional generalization nd-unfolding/unfold_nd_omnifold_unbinned.py." Ledger home:
    `2d-unfolding/2D_OMNIFOLD_REFERENCE.md:119`, `README.md:89`.
- 8 of the lane's 10 have a ledger home.
- In the lane's search, B07-g-03 (the event-loop truth-hadronic diagnostics) and B12-g-04 (the label table) have none,
  and stay PROTECTED. The independent classification found a home for B12-g-04 and 12 of its 13 overall.
- In later rounds each such cut carries a probe that its ledger record holds the fact (#521).

## 7. Stopping rule

From the decision, item 2: stop when P1's mean on each document reaches the anchors' re-measured mean, or after three
rounds with no P1 movement.
- The targets are 3.667 for the paper and 3.875 for the note. The base is 3.00 and 3.122.
- Neither document has reached its target, and no round has run.
- §1 gives P1N's resolution limit on what this rule can see.

## Files

All paths are relative to this directory.
- `RULES.md`: fixed before the gap runs.
- `CLASSIFY-BRIEF.md`: the brief both classifiers used, with the records and B2 clarifications (§4).
- `REPORT.md` and `PROTECTED-CHOICES.md` (generated from the after-#522 files).
- `prompts/G1.prompt.txt` and `prompts/G1N.prompt.txt`.
- `tools/`: `split_base.py`, `extract_piece.py`, `plants.py`, `make_gap_inputs.py`, `parse_gaps.py`, `gap_table.py`,
  `count_classes.py`, `compare_classes.py`, `protected_choices.py`, `show_gaps.py`, `ctx.py`, `gapjob.sh` (with
  `test_with_timeout.sh`) and `runjob.sh`.
- `measure/`: the 69 P1/P1N outputs, `status.tsv`, `ANCHORS.SHA256SUMS`.
- `base/pieces/`: the 15 blinded note pieces and `pieces.json`.
- `gap/`:
  - `INPUTS.SHA256SUMS`;
  - `runs/` (the 34 counted outputs and `status.tsv`) and `runs-noexit/` (the 7 hung attempts, unused);
  - `gaps.json` and `gaps.tsv` (285 gaps);
  - `class-{lane,indep}-{before521,after521,after522}.tsv`, where `before521` is the committed state;
  - `class-lane-initial.tsv`: my classification before the director's rulings 2 and 3, over the 303 rows of
    `gaps-303.tsv` (the table before the B06 and B08 gemini runs left). The independent classifier's initial file was
    edited in place; its counts are in its first report: PROTECTED 69, STRUCTURE 97, WORDING 135, UNVERIFIED 2;
  - `compare-<state>.txt`, `disagreements-<state>.tsv`, `count-<classifier>-<state>.json` and `ENOUGH.txt`.
- `SHA256SUMS` covers every file listed here.
