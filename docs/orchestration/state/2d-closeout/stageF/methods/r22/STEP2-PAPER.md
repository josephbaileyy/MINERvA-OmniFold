# r22 Step 2, the paper round: plan

**Under** [STEP2-PLAN.md](STEP2-PLAN.md): the method of §3, the paper adoption rule of §4 and the stopping rule of §5,
all fixed before any score. The director cleared the round on 2026-10-30, after #539: G1b's in-scope gaps; the
pinned A1 and A4 pairs, which go through the director to Joseph before adoption; and the B4 re-pin of
`registry/ALIASES.tsv:38` and ATTRIBUTION (§7, ruling 4). This file adds only what the paper round needs beyond
STEP2-PLAN.md. It is committed before any text is written and before any NEW score.

## 1. The gap list

`tools/step2p_gaps.py` writes `step2p/gaps.tsv` and `step2p/held.tsv`.

- **Ids.** G1 and G1b number their paper gaps alike, so the ids are prefixed `G1:` and `G1b:`. G1's paper-s-06 (the
  abstract's χ² sentence) and G1b's paper-s-06 (the C_resp sentence) are different gaps.
- **In scope: 34 gaps.**
  - G1's 13 paper gaps from `step2/gaps-ws.tsv`. Eleven are WORDING or STRUCTURE under both classifications. The other
    two are the #524 Joseph pairs: G1:paper-s-09, the Data availability sentence (A1), and G1:paper-s-06, the
    abstract's χ² sentence (A4).
  - G1b's 21 gaps that both classifications call WORDING or STRUCTURE (G1B-RULES.md §5).
  - Several gaps of the two runs name the same passage. They are kept as separate rows. The writer treats them
    together.
- **Held: 23 sentences.** These are the out-of-scope paper gaps of either run whose quote is located: PROTECTED under
  either classification, or not carried by #524. 3 UNVERIFIED gaps are skipped.
  - Each held quote must still print in NEW's paper, as STEP2-PLAN.md §3 step 2 requires.
  - The check is EXACT after normalization (`tools/check_held.py`). The note round's gapped `locate()` is not used:
    this round's self-test showed that it accepts a quote with one word changed.
  - Applied after the fact to the adopted note, the exact check gives the same result as the gapped one. Of the 67
    out-of-scope quotes, all print exactly apart from the known B09-g-09 renumbering. B10-g-02 matches only gapped at
    the base, where a table float splits the sentence, and matches exactly in the adopted note.
- **How the two lists meet.** Where an in-scope gap's quote is a held sentence (`held_overlap` in `gaps.tsv`), the
  held sentence wins. That gap may act only on other passages its PROBLEM describes, its "pattern". If it has none,
  it is skipped and reported. This follows STEP2-PLAN.md §6 answer 4: a gap that either classification calls
  PROTECTED stays out.
  - The sentences this holds: the seed-42 sentence (G1:paper-g-04), the Scope sentence (G1:paper-g-07,
    G1b:paper-s-08), the five-iterations sentence (G1:paper-s-03, G1b:paper-s-10), the envelope target (G1b:paper-g-11),
    the flux reason (G1b:paper-g-12), the Fig. 3 covariance (G1b:paper-s-04), the run-period block (G1b:paper-s-17),
    the coverage claim (G1b:paper-s-19) and the note pointer (G1:paper-g-01).
  - The FROZEN sentence (G1:paper-s-02's quote) is held in any case. G1:paper-s-02 consolidates the other repeated
    coverage statements around it.
  - **Exception.** G1b:paper-s-05 is the Data availability sentence of the A1 pair. It is exempt only when Joseph's
    pinned pair is applied (`--pair-applied G1:paper-s-09`).

## 2. The base

- **The rule** (STEP2-PLAN.md §2) is triggered, because the paper's text changed since `d84124c5`. At `f47b1b4a`
  (origin/main, after #539) the blinded rater copy differs from Step 1's in one line, "Table 12. Table 10 there"
  becoming "Table 13. Table 11 there". These are the note's table numbers, read through xr-hyper; the note round's B06
  added a table. The title page's date also differs, but the blinded copy drops it.
- **The base is therefore `f47b1b4a`.** Its rater copy is `step2p/base/manuscript.txt`, made by `make_rater_copy.sh`.
  It is re-scored with sol2 P1 ×3 before any text is written: 3, 3, 3 (`step2p/base/P1__base-paper-f47b1b4a__sol2__r*.txt`),
  the same as Step 1's 3, 3, 3. The target is 3.667.
- **Every held quote and every in-scope quote** was carried to the new base by quote. All locate, because the
  changed line is in no quote.

## 3. Method

As STEP2-PLAN.md §3, for one document.

1. **One writer** edits `paper_body.tex` only, under [step2p/WRITER-BRIEF.md](step2p/WRITER-BRIEF.md). The two pairs
   go to `step2p/pairs.md` as before/after text and are not applied. main_paper.tex is not edited.
2. **The fact ledger** is `step2p/ledger.md`, checked by `step2p/check_paper.py` (self-test: 16 planted defects caught,
   2 silent controls). The checker requires:
   - every probe holds;
   - every changed base sentence is named in a row;
   - every label survives;
   - every other note-directory source is byte-identical, and main_paper.tex differs from its base only by pinned pairs;
   - each of the eight GATE phrases prints once, and the FROZEN sentence prints once;
   - there is no new number;
   - the registered alias "the joint-test estimator" still prints.

   A #522 move needs an `N:` probe showing that the note prints the fact. The paper keeps its one pointer to its
   limitations in the note, the held G1b:paper-s-20 sentence.
3. **A two-direction review** by an independent read-only agent.
4. **agy agreement** on every changed passage, with a planted control.
5. **The B4 re-pin** (§7 ruling 4). If line 52 changes, the rows that cite paper_body.tex are re-cited with
   `check_registry.py --cite`: ALIASES 38 (line 52, digest `402b2cee1998669e`), ALIASES 47 (line 64, `308c2724c0758c07`)
   and ATTRIBUTION 17 (line 52, `402b2cee1998669e`). The alias text "the joint-test estimator, a deterministic
   LightGBM" stays registered. `records_estimators.tex` is regenerated. The re-pin record, in the round's report and
   commit, names every old and new line and digest.
6. **The build and all gates:** `build_all.sh` (SEC4 receipts, `make_values_fived16.py --check`, the FIVED16 blocks),
   `check_held.py`, `reflow_tex.py --check`, and the record-checks.yml steps with BASE=origin/main.

## 4. Adoption and measurement

- **The paper rule of STEP2-PLAN.md §4, unchanged.** NEW is adopted if all three hold:
  - NEW beats the base in at least 3 of 4 blind P2 runs (sol2 and gemini, both orders), with
    `rater-calibration/prompts/P2.prompt.txt` unchanged and the blinded rater copies as Documents A and B, as r21;
  - sol2 does not flip between orders;
  - on 3 sol2 P1 runs (`prompts/P1.prompt.txt`, as the base's), NEW's mean and its lowest run are each at least the base's (3.0 and 3).

  If any of the three fails, the paper keeps its base text.
- **The pairs.** They are judged inside the text that would be adopted. If Joseph approves them before the runs, they
  are applied first. If he has not, the runs judge the paper without them, and any later application gets its own
  check. If the paper is not adopted, neither pair is.
- **Score and stopping rule:** STEP2-PLAN.md §5. P1's resolution at 3 is reported.

## 5. Rule change, 2026-10-30 (after #549 and #550): held for facts, and one judgement with the pairs

Recorded before any text of this pass is written and before any of its runs.

**What led to it.** All three P1 runs on the adopted paper quoted the same passages: the five-iterations sentence, the
limitations pointer with "is stated only here", and the Data availability package sentence. sol2's own rewrites of the
first two kept every fact and qualifier. The first two were frozen only by this round's byte-exact held rule (§1),
which was the director's answer 4 of STEP2-PLAN.md §6, not a Joseph ruling. The director changed it on 2026-10-30.

**The rule.** A sentence quoted by an out-of-scope gap is held for its FACTS, not its bytes. It may be reworded only
when all of these hold:
- (a) the out-of-scope gap's own change is not made: no fact, qualifier or KEEP item is dropped, and nothing is
  softened;
- (b) every fact and qualifier in it carries a probe. Where the note prints it, the probe is an `N:` probe of the note
  source and a `P::` probe of its new paper wording. Where only the paper prints it (C18, the four low-stability cells),
  it is a `P::` probe, and the fact may not leave the paper. Its sentence may still be reworded (the director,
  2026-10-30);
- (c) agy reads the old and new sentence as SAME, with a planted control.

Byte-exact holding stays for:
- Joseph's own text: Data availability beyond his approved A1 pair, the abstracts and title (A4, A5), and the claims
  (A7);
- the FROZEN sentence;
- the B4 gate-bound phrases (`check_paper.py` GATE, and the registry-pinned lines, which are re-pinned with a record if
  their line changes).

**The KEEP list** (Joseph, `DECISION-20261028-joseph-protections-remade-and-r21.md` item 6) stays. It is read, as in
`DECISION-20261029-joseph-limitations-may-leave-paper.md` item 2, as the qualifier staying with its claim, not as its
bytes. The director confirmed this reading on 2026-10-30, citing Joseph's own wording in
`DECISION-20261023-joseph-5d-a-and-register-round.md:35-36`: "The KEEP list stands: qualifiers whose removal makes a
sentence false even under the stated scope stay where they are."
`check_paper.py` now enforces it. Every r21 KEEP row (`r21/ledger.md`) whose probes print in the base paper must
either still print verbatim or be named by its F-id in a ledger row, with a `P::` probe of its new wording and an agy
SAME read.
- The adopted paper (#549) already reworded five of the 64: F025, F145, F149, F246 and F305. None is dropped, and each
  gets its row now.
- F109, the five-iterations KEEP item ("because 10, 15, or 20 iterations did not reduce its model dependence…"), must
  print in substance if its sentence is reworded.

**Which sentences this pass may reword.** These are the held sentences that an in-scope gap acts on (`held_overlap`
in `gaps.tsv`). `tools/check_held.py --fact-held` exempts these from the exact check (the A7 three only with `--a7-released`), and the ledger and agy
checks above take its place:

| held id | sentence | in-scope gaps that act on it |
|---|---|---|
| G1b:paper-g-01 | the note pointer ("The companion analysis note … cited below by section") | G1:paper-g-01 |
| G1b:paper-g-06 | the seed-42 sentence | G1:paper-g-04 |
| G1b:paper-g-03 | the Scope sentence ("one OmniFold implementation on one data set …") | G1:paper-g-07, G1b:paper-s-08 |
| G1:paper-g-02, G1b:paper-g-08 | the five-iterations sentence (F109 KEEP) | G1:paper-s-03, G1b:paper-s-10 |
| G1:paper-g-06 | the envelope target ("none of the reporting definitions … meets this target") | G1b:paper-g-11 |
| G1:paper-g-10 | the flux reason ("for a reason the released inputs do not let us determine") | G1b:paper-g-12 |
| G1b:paper-g-13 | the Fig. 3 covariance ("an earlier purity-subtracted … covariance that fails …") | G1b:paper-s-04 |
| G1b:paper-g-18 | the run-period block ("its size is not validated and its own consistency check cannot fail") | G1b:paper-s-17 |
| G1b:paper-g-20 | the coverage claim ("We make no coverage claim …") | G1b:paper-s-19 |
| G1b:paper-s-20 | the limitations pointer | G1:paper-s-10, G1b:paper-s-15 (R-1's two gaps) |
<!-- absence-ok: the table quotes printed paper sentences by name; not a claim that something has not been run -->

- **A7: three stay exact (the director, 2026-10-30).** The out-of-scope gaps on three of these sentences are tagged A7
  (claims) by a classifier: G1:paper-g-10 (the flux reason), G1b:paper-g-13 (the Fig. 3 covariance) and G1b:paper-g-20
  (the coverage claim). The director ruled that they scope the result's claims, so rewording them is claim-wording
  work, which is Joseph's under A7. None is what P1 quotes.
  - They stay byte-exact (`check_held.py` A7_PENDING, never passed `--a7-released` in this pass).
  - Their gaps G1b:paper-g-12, G1b:paper-s-04 and G1b:paper-s-19 are skipped under A7.
  - If a later P1 quotes one of them, it goes to the director as a pinned pair for Joseph.
  - Eight held ids remain held for facts.
- **The limitations pointer.** The metatext "The low stability of four of the sixteen cells is stated only here." is
  dropped. The low-stability fact (C18) stays in the paper's Limitations, with its `P::` probe. The pointer to the
  note's limitations stays (Joseph, #522 item 2).
- **The gaps now included.** The nine skipped in the first pass because their held quote left no other passage
  (G1:paper-g-01, -g-04; G1b:paper-g-11, -g-12, -s-04, -s-08, -s-10, -s-17, -s-19), R-1's two, and the remainder of
  G1:paper-s-03.
- **Still byte-exact.** The other held sentences (G1:paper-g-08, G1:paper-s-08, G1b:paper-g-07, -g-09, -g-14, -g-19,
  -s-02, -s-13, the FROZEN pair G1:paper-g-03 and G1b:paper-g-02, and the abstract G1b:paper-s-07) are acted on by no
  in-scope gap, and stay exact. G1b:paper-s-05 is exempt only through the applied A1 pair.
- **R-6** was accepted by the director as a cut to the note: the note prints the fallback role (`sec_5d.tex`), and
  ledger P-10 probes it.

**One judgement.** Joseph approved both pairs exactly as pinned (`DECISION-20261030-joseph-paper-pairs.md`), and they
are applied through `PAIRS` / `PAIR_PINS`.
- **NEW** is the paper with both pairs and this pass's fact-held rewrites.
- **The base** is the adopted paper as merged (#549, `e33a1ab0`), whose rater copy is `step2p/new/manuscript.txt`
  (sol2 P1 3, 3, 3).
- **The rule** is §4's, unchanged:
  - NEW wins at least 3 of 4 blind P2 runs;
  - sol2 does not flip;
  - NEW's sol2 P1 ×3 mean is at least 3.0, and its lowest run at least 3.
- **If the rule fails,** neither the pairs nor the rewrites are adopted, and the paper stays as merged.
- **Outputs** go to `step2p/pass2/`.

### The text judged (fixed 2026-10-30, before the runs)

The writer's pass ([step2p/pass2/WRITER-BRIEF.md](step2p/pass2/WRITER-BRIEF.md)) went through the two-direction review
and agy ([step2p/pass2/agy1/](step2p/pass2/agy1/)). Under rule (c), only the changes that agy and the review read as
SAME were kept.

**Kept:**
- **The note pointer.** It is reordered: "…note [14], cited below by section, gives …". agy read it SAME twice.
- **The seed-42 sentence.** It now reads "uses LightGBM [23] at seed 42, with …", so the seed stays attached to
  LightGBM (review R2-4). agy read it SAME twice. Line 50 is re-pinned: ALIASES 38 and ATTRIBUTION 17 move from
  `52bd6f35a5367d1e` to `07a348c82f88db98`.
- **The limitations opener.** It now reads "Apart from the low stability of four of the sixteen cells (below), the
  limitations of these results are stated with the results they qualify, …". The exception stays because dropping
  "is stated only here" alone made the opener false (review R2-1).
  - agy ([step2p/pass2/agy2/](step2p/pass2/agy2/)) gave this pair two verdicts. On the real file: "DIFFERS: AFTER drops
    the explicit exclusivity statement 'is stated only here' … replacing it with the locational pointer '(below)'". In
    the control run, on the same text: "SAME".
  - **The director's ruling (2026-10-30): accepted as written.** The clause keeps the exception true, and "(below)"
    carries the location. agy's DIFFERS concerns the metatext that the director ordered dropped.

**Reverted to the merged text** (their gaps skipped):
- **The Scope sentence.** agy read it DIFFERS: "apply to" is stronger, and "one … one" is lost (review R2-5).
- **The five-iterations sentence.** Defining the residual proxy adds a fact and a new quantity, the 1 % threshold.
  The no-new-fact rule holds (the director).
- **The envelope target.** agy read both wordings DIFFERS.
- **The run-period block.** "A consistency check that reuses those differences" broadens "its own" (review R2-2,
  agy).

**agy2's control** caught 3 of 3. A chunk with fewer than three negations is now topped up with identity fillers
(`make_agy_pairs.py`), and all 3 fillers read SAME in the real file.
