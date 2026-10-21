# Calibration of the register raters, and which prompts work best (2026-10-21)

**Asked for by Joseph** (DECISION-20261021-joseph-register-loop-2 item 5): "calibrate the raters and note which prompts
are the best".

**Done by** a calibration agent working for the director, read-only on every git tree. The director checked the
P1 and P2 tables below against the raw run outputs.

**Raters:**
- GPT-6.1-sol ("sol"), through codex-school;
- Gemini, through agy (gemini-3.8-flash-high).

Both were run through `run_x.sh`, with one retry on an empty or failed run (`tools/runjob.sh`). There were 106 runs in
the grid.

**CITABLE FOR:**
- the scores of these documents under these prompts on 2026-10-21;
- the prompt ranking;
- the calibrated target;
- the rater-copy procedure.

**NOT CITABLE FOR:**
- any physics claim;
- the quality of the anchor papers' science;
- rater behaviour on documents of other genres.

## 1. Documents

**Anchors.** Each identifier, title and journal-ref was copied from the arXiv abstract page. Each anchor is
published.

| slot | arXiv | title | journal-ref | version | words (raw / blinded) |
|---|---|---|---|---|---|
| A | 2504.06857 | Machine Learning-Assisted Unfolding for Neutrino Cross-section Measurements with the OmniFold Technique | Phys. Rev. D 112, 012008 (2025) | v2 | 9481 / 8148 |
| B | 2002.12496 | Double-Differential Inclusive Charged-Current νμ Cross Sections on Hydrocarbon in MINERvA at ⟨Eν⟩ ∼ 3.5 GeV | Phys. Rev. D 101, 112007 (2020) | v2 | 10605 / 8992 |
| C | 2205.05084 | Bias and Priors in Machine Learning Calibrations for High Energy Physics | Phys. Rev. D 106, 036011 (2022) | v2 | 11803 / 8583 |

Anchor C was chosen because its abstract reports a negative result.

**Our documents:**
- **ours-current:** the methods paper at origin/main 2f55cd53, which is register round r11, as a hold-free rater copy.
  9,844 words after blinding.
- **ours-holds:** the same paper with its holds kept.
- **ours-old:** commit 1486f754, from before the register rounds. It was rebuilt with the same script, because
  `in-r8/paper.txt` was column-interleaved layout text.

**Blinding** (`tools/blind.py`) was the same for every document. It removes:
- the title, authors, affiliations, date and journal headers;
- DOIs, arXiv stamps and page numbers;
- the acknowledgments and the reference list.

It keeps the abstract, the body, the appendices, the captions and the data-availability text. Raters saw neutral file
names.

## 2. Prompts (`prompts/`)

| id | what it asks |
|---|---|
| P0 | The register prompt of rounds r9–r11, verbatim. It gives a 1–5 rating within a six-question review and says "revised several times". |
| P0n | P0 with the revision-history framing removed. |
| **P1** | A rubric-anchored 1–5 rating of language and register only. Each level is defined, and the reply gives the rating, a one-sentence justification and three quoted passages with rewrites. |
| **P2** | A blind pairwise comparison: which of documents A and B reads more like a well-edited PRD paper, its strength (1–3) and three reasons. |
| P3 | A count of sentences a PRD copy editor would flag, quoted. The metric is the number of verified flags per 1000 words. |

## 3. Results

**P1** (runs → mean):

| document | sol | Gemini |
|---|---|---|
| anchor A | 3.5, 3.5, 3.5 → 3.50 | 3.5, 3.5, 3.5 → 3.50 |
| anchor B | 3.5, 3.5, 3.5 → 3.50 | 3, 3, 3 → 3.00 |
| anchor C | 4, 4, 4 → 4.00 | 3.5, 3.5, 4 → 3.67 |
| ours-current (r11) | 3, 3, 3 → 3.00 | 2, 2.5, 2 → 2.17 |
| ours-holds | 2.5, 2.5, 3 → 2.67 | 2, 2, 2.5 → 2.17 |
| ours-old | 2.5, 2.5, 2.5 → 2.50 | 2.5, 2.5, 2.5 → 2.50 |

**P0 and P0n on ours-current:**
- With either prompt, ours-current scored 3, 3, 3 with both models. The framing does not move our score.
- On anchor A, P0 gave sol 4, 4, 4 and Gemini 3.5 each run. P0n gave sol 3, 4, 4 and Gemini 3.5, 3.5, 3.

**P2** (both orders, one run each):
- ours-current against ours-old: current won 4 of 4.
- ours-current against the anchors:
  - with sol, ours won 5 of 8, against anchors A and B, and lost both runs against anchor C;
  - with Gemini, ours won 8 of 8.
- **Reading.** The raters' reasons show P2 rewards surface polish. For example, they cited the anchors' typos and
  colloquialisms.
- **Consequence.** P2 is usable between two versions of our own paper. It is not usable for calibrating against
  published work.

**P3:**
- It does not resolve ours-old against ours-current with either model.
- With sol, anchor A (5.56 flags per 1000 words) is indistinguishable from ours-current (5.52).
- It is noisy: the sd is 0.3–1.5 flags per 1000 words.
- Its quote lists are useful to a writer, but it is not a metric.

**Holds.** After blinding, only the deposit hold remains in the text. It lowered sol's P1 by 0.33 (two of three runs)
and Gemini's by 0.

## 4. Ranking and recommendations

- **Absolute score: P1 with sol.**
  - It has the best combination of three properties:
    - every anchor run scores above every run on our paper;
    - its run-to-run sd is 0.12;
    - it resolves our own revisions: ours-old 2.50 against ours-current 3.00, z ≈ 5.
  - Report Gemini's P1 alongside, but do not gate on it: it scored ours-old above ours-current.
- **Round-to-round decision: P2, new version against the previous one,** in both orders with both models (4 runs).
  - Adopt the new version if it wins at least 3 of 4, sol shows no order flip, and P1 with sol does not fall.
  - This rule rests on one measured version pair.
- **Runs per round:** 3 P1 runs with sol. A 0.5-point change needs 1–2 runs at the measured sd.
- **Calibrated target.** It replaces "4.5/5".
  - The published anchors' P1 mean is 3.67 with sol (3.5, 3.5, 4.0) and 3.39 with Gemini.
  - No anchor scored above 4.0 from either model on any prompt.
  - Target: **P1 with sol ≥ 3.5 on 3 of 3 runs.**
- **The "revised several times" framing** (P0 against P0n) had no measured effect on our paper.

## 5. Rater copies (`make_rater_copy.sh <worktree> <out.txt>`)

**What it builds.** The paper, twice, in scratch copies:
- the normal build;
- a build with `\pubhold` rendering nothing, after `tools/check_holds.py` proves that every hold is a sentence of its
  own.

It requires that both builds have no unresolved references and that the text contains no `??`.

**If the paper uses `\externaldocument`,** it builds `main_note` first.

**The rater text.** It is the normal build's text with the hold spans removed.
- **Why not the hold-free build's text.** Dropping a hold reflows the last page. In round r12, the reflow put half of
  the data-availability text after the first reference line, where blinding drops it.
- **The hold-free build is still checked.**
  - `tools/holddiff.py`: a word-level diff against the normal build.
  - If that diff fails only through reflow order, `tools/multiset_check.py` must find equal word multisets.

**Before blinding,** `tools/fix_da_order.py` restores the data-availability heading to reading order.

**After blinding,** the script fails if:
- the heading or the section's last sentence is missing;
- any identifying text, `HOLD` or `??` survives.

**Tests:**
- The script was tested on r11 and r12. Its r12 output is byte-identical to a hand-built copy.
- Its r11 output equals the calibration's ours-current as a word multiset.
- Each of these planted defects failed it, as it should:
  - a missing reference label;
  - a hand-typed `[HOLD: …]`;
  - a literal `??`.

**Paths.** The scripts are the as-run copies. `tools/runjob.sh` names the session's scratch directory, so adjust its
`C=` line before reuse.

## 6. Limits

- Each cell has 3 runs, and 11 of 18 P1 and P0 cells had zero variance, so the z-scores are rough.
- The raters may know the anchors from training. This was not measured.
- Anchor B's arXiv v2 PDF ends its conclusion mid-sentence.
- P0's "about 13 pages" is false for anchor A.
- The funding hold could not be measured, because blinding removes the acknowledgments.
- In rounds r8–r11 Gemini gave P0 3.5. Here it gave P0 and P0n 3.0 in all 6 runs; the cause was not tested.
