# r22 Step 1 — the gap diagnosis: prompts, control and rules, fixed before any gap run

**Under** [DECISION-20261029-joseph-register-rounds-reopen.md](../../../../../DECISION-20261029-joseph-register-rounds-reopen.md)
item 2, Step 1. **Recorded by** the paper rewrite lane. **Approved by** the director (2026-10-29), as written, with two
additions (§6). This file is committed before the first gap run, so every rule here predates the gap outputs.

Step 1 is a diagnosis only. It changes no text in the paper or the note.

## 1. Base and targets

- Base: main `d84124c5`.
  - Paper: the blinded rater copy from `make_rater_copy.sh`, sha256 `a945a490…`, 7,465 words. It is byte-identical
    to r21 NEW (`r21/measure/new/r21new.blind.txt`).
  - Note: `main_note.pdf` built at `d84124c5`, sha256 `33847dc3…`, cut into 15 blinded pieces by `tools/split_base.py`
    (55,967 words). The pieces follow the 2026-10-22 whole-note grouping, with Sec. 10 (sixteen-cell) as its own piece.
- Targets: the anchors re-scored with the current P1 and P1N prompts, sol2 ×3 each. Those scores were measured before
  this file was written; the report gives them with the base scores.
- Prompts P1 (`rater-calibration/prompts/P1.prompt.txt`, sha256 `4bbbf272…`) and P1N (`P1N.prompt.txt`, `46f5ded8…`)
  are unchanged since the calibration.

## 2. The gap prompts

- `prompts/G1.prompt.txt` (paper, sha256 `5538d961…`) and `prompts/G1N.prompt.txt` (note pieces, `c6459e84…`).
- The header and the 1–5 scale lines are P1's, byte-identical. G1N's genre sentences are P1N's, verbatim.
  `tools/make_gap_inputs.py` asserts both.
- The question, in both: what would have to change for the text to rate 4 on this scale, at the register of the
  references, with exact quotes. Each answer gives CURRENT RATING, at most 12 GAPS (QUOTE, SCOPE, PROBLEM, CHANGE,
  SHARE, with the shares summing to 100), and one ENOUGH sentence.
- Inputs:
  - G1: `reference-1..3.txt` = the blinded paper anchors A, B and C; `manuscript.txt` = the paper.
  - G1N: `reference-1..4.txt` = note anchor pieces AT1, AT2, AP1 and AP2; `chapter.txt` = one base piece.
- No anchor score and no word about protections reaches a rater.
- `gap/INPUTS.SHA256SUMS` pins all 28 input files. `make_gap_inputs.py` rebuilds them byte for byte.

## 3. The planted control

- Three planted sentences (`tools/plants.py`), each on its own line, after the first line ending in a period at or past
  25%, 50% and 75% of the text:
  1. bookkeeping: "This paragraph was rewritten in round r17 after review ticket OI-131, and the earlier wording is
     kept in the project records."
  2. process, colloquial: "We then went back and reran the whole chain a second time, just to be safe, and nothing
     changed."
  3. jargon: "The z2m lane's tier-S gate stayed green on every rerun of the FIVED16 package."
- Control copies: `paper-ctl/manuscript.txt` (sha256 `971b77f1…`, 7,519 words) and `B09-ctl/chapter.txt`
  (`e0a79b9c…`). B09 is the piece of median word count, chosen by that rule.
- `make_gap_inputs.py` asserts that each plant occurs exactly once in its control copy, never in a real input, and that
  the control copy minus its three plant lines equals the real input.
- **Pass rule:** a control run passes when the rater quotes at least 2 of the 3 plants. A plant counts as quoted when a
  located QUOTE lies within it (`tools/parse_gaps.py`). If a rater's control fails, its real runs are still reported,
  marked "control failed, low power", and the director is told before any classification.

## 4. Runs

36 runs, one each, through `register-method/tools/run_x.sh` by `tools/gapjob.sh` (one retry on failure or empty output):

| Inputs | Prompt | Models | Runs |
|---|---|---|---|
| `paper`, `paper-ctl` | G1 | sol2, gemini | 4 |
| `B01`–`B15`, `B09-ctl` | G1N | sol2, gemini | 32 |

sol2 is gpt-6.1-sol through codex-school2. gemini is agy, `gemini-3.8-flash-high`.

## 5. Classification (c) and counting (d)

**Location.** Each QUOTE is located in its rated text by the calibration's rule (`key()` and `locate()` from
`rater-calibration/tools/analyze.py`, exact or gapped). An unlocated quote is UNVERIFIED: it is listed and not
classified. Plant gaps and control runs are not classified or counted.

**Classes.**

1. **PROTECTED** if the rater's CHANGE would do any of these:
   - reword text whose wording is Joseph's: protections inventory (`protections-inventory-20261028/REPORT.md`) A1, Data
     Availability; A4, the abstracts; A5, the title;
   - change what a claim states (A7);
   - reword a gate-bound phrase (B4; the r21 fact ledger's GATE rows) or the FROZEN sentence;
   - drop or weaken a KEEP or guardrail qualifier (B1, B3);
   - remove an HONESTY-required fact from the document, or move it to the note where the result it bounds stays
     (inventory §4: C1, C5, C7, C8, C11, C12, C17, C20).

   Each PROTECTED record names the inventory item or ledger row, with the exact sentence.
2. **STRUCTURE** if it is not PROTECTED and the change moves, cuts, merges or splits passages or sections, converts
   prose to a list or table, or sends text to the note, an appendix or the records.
3. **WORDING** otherwise: a rewrite in place that keeps every fact and qualifier.

- A mixed change takes the highest class: PROTECTED > STRUCTURE > WORDING.
- A gap these rules cannot place is UNRESOLVED. It is listed with its quote and counted in no class.
- A fresh read-only agent classifies every gap independently from these rules alone. The report lists every
  disagreement.

**Counting.**

- Per run, a class's share is the sum of that class's SHARE values, the raters' own numbers. If a run's shares do not
  sum to 100, they are rescaled to 100 and the raw sum is reported.
- Shares are reported per document × rater. For the note, the share is the mean over the 15 pieces, equal weight, as
  P1N's mean is a piece mean. Gap counts per class are reported too. No other weighting, and no inference beyond the
  quotes.
- PROTECTED gaps go to Joseph as choices, quoting the exact sentences. They are never reworded around.

## 6. The director's two additions

1. Each rater's ENOUGH line is recorded verbatim in the report. If either rater says the listed changes would not
   reach 4, that sentence goes to Joseph beside the class shares.
2. The report gives P1N's low resolution in the 3 band beside the base result, as a limit on what the stopping rule can
   see.

## 7. Stopping rule (from the decision, item 2)

Stop when P1's mean on each document reaches the anchors' re-measured mean, or after three rounds with no movement in
P1, whichever comes first.

## Files

- `prompts/G1.prompt.txt`, `prompts/G1N.prompt.txt`.
- `tools/split_base.py`: cuts the note into the 15 base pieces.
- `tools/extract_piece.py`: cuts the note anchor pieces from their arXiv PDFs. It is restored verbatim from the
  calibration session's transcript, because the calibration's copy was swept with its scratch directory.
- `tools/plants.py`, `tools/make_gap_inputs.py`, `tools/parse_gaps.py`, `tools/gapjob.sh`, and `tools/runjob.sh` (the
  P1/P1N score runs).
- `gap/INPUTS.SHA256SUMS`.
- Used from the repository, unchanged: `rater-calibration/tools/blind.py` (sha256 `a7f098d6…`),
  `register-method/tools/run_x.sh` (`f226f7c3…`), `rater-calibration/tools/analyze.py` (`8e993d7b…`).
