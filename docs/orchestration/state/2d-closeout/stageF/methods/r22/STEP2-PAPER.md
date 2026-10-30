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
