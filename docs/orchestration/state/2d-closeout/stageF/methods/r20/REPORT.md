# Round r20, the paper's fourth and last: NOT ADOPTED (2026-10-28)

**Governed by:**
- `DECISION-20261025-joseph-register-rounds-paper-rewrite.md` (round 4 of 4);
- the director's authorization and the approved `outline.md` (with its conditions).

**What it was:** six passages that P1 quoted after r19 (R1–R6), reworded with no structural change. The edits are in
`apply_r20.py` and `apply_r20_fixes.py`.
- Commits: `5ea7a81c`, then `7ec31a5d` after the review (ADOPT-AFTER-FIXES, no BLOCKING) and agy (both controls
  caught).
- The ledger is `ledger.md`. It was checked at `7ec31a5d` (6 rows, 0 failures) and does not hold at the reverted head.

## Measurement

| | revision | blinded copy sha256 | words |
|---|---|---|---|
| OLD | r19 as measured, `a1702535` | `76c6bfa374bffdba…` | 7,404 |
| NEW | `7ec31a5d` | `2ef2b30927034263…` | 7,395 |

| model | order | winner | strength |
|---|---|---|---|
| sol2 | A = OLD, B = NEW | B (NEW) | 1 |
| sol2 | A = NEW, B = OLD | A (NEW) | 1 |
| gemini | A = OLD, B = NEW | A (OLD) | 2 |
| gemini | A = NEW, B = OLD | B (OLD) | 2 |

**NEW wins 2 of 4.** Neither model flipped with the order, so the split is sol2 for NEW and gemini for OLD.
- The adoption rule asks for at least 3 of 4, so r20 is **not adopted**.
- The stop rule's first condition also holds: the pairwise no longer prefers the new version in both models.

**P1 sol2, run 1:** 3. Runs 2 and 3 were not spent, because the version they would score is not kept.

**Gemini's reasons are concrete, and they point at r20's own wording:**
- "Ten, 15 or 20" mixes spelled-out words and numerals;
- the serial comma was dropped;
- "so it keeps five" reads as colloquial;
- "far upward" reads as an intensifier;
- the Limitations lead nests a parenthetical inside a semicolon.

sol2 preferred r20's result-first binned-diagnostic sentence and "The bias at a truth is listed".

## What follows

- **The paper's text returns to r19's,** `5841adce` (r19 as measured, plus agy-b4's Q2 fix), in one commit, so r20
  stays in history. The r19 ledger is restored to its `5841adce` form and passes (204 rows, 0 failures).
- **Kept from r20:** `r19/check_ledger.py`'s duplicate-id plant, which now uses the ledger's own first row id.
- **The paper's register rounds are closed** (director, 2026-10-28).
- **The final P1, for the paper's text as kept** (r19's, measured on `a1702535`): sol2 **3, 3, 3**. The published PRD
  anchors' mean under the same calibrated prompt is **3.67** (`rater-calibration/REPORT.md`). The paper's text stays
  below the anchors on this prompt.
- **For Joseph in (d):** the passages P1 keeps quoting are listed in `../r19/REPORT.md`. Gemini's specific points
  above are wording he may want to judge by reading.
<!-- absence-ok: records the round's measured outcome and what was not run; not a new absence claim -->
