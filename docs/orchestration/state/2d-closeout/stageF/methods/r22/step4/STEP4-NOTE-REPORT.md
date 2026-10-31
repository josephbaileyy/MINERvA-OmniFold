# r22 Step 4, the note's truth round: report, part 1 (T1, T2, T4, T5; 2026-10-31)

**Under** [STEP4-PLAN.md](../STEP4-PLAN.md), committed before any text, which the director accepted on 2026-10-31.
- **What this round is:** truth fixes and a decided table format. They are adopted per change on truth checks. No
  rater runs are made, and the round does not count toward the stopping rule.
- **Not in this part:** T3, R and T6. They wait for RESTYLE AMENDMENT 1's bound rerun and Joseph's second look, and
  follow in their own PR (the director, 2026-10-31).
- Nothing is submitted, deposited or tagged.

## The changes

| id | file | change | source |
|---|---|---|---|
| T1 | `sec_results.tex`, `fig:model` | Tune v1 "(orange)" → "(blue)" | the producer draws Tune v1 as `#4C72B0`, and the pinned PDF strokes no orange (`fig-restyle-20261031/CAPTION-FIXES.md`). "Blue" is also the amendment palette's name for `#4C72B0`, so T1 stands after the install |
| T2 | `sec_eavailw.tex`, `fig:eavailWband` | the caption names the two projections. The corner claim is attributed to `sec:eavailw-band`, where its ratios print. "Band" is replaced, and "unchanged" becomes "essentially unchanged" | `overlay_eavailW_band.py` draws two 1D projections with no band; the section prints the corner ratios and "essentially unchanged ($1.142\to1.139$)" |
| T4 | `sec_eavailw.tex` | "the leading-hadron angle" → "the polar angle of the summed momentum of all final-state particles other than muons and neutrinos" | `CVUniverse.h:267-268` and `GetHadronAngleTrue()`, which sums every final-state particle but muons and neutrinos (photons included; review) |
| T5 | `sec_fived16.tex`, `tab:fived16-gen` | Option B (#581): "All 16 cells" and "8-cell subset" blocks; χ² and ndf in separate columns, with the "without $C_{\mathrm{resp}}$" χ² and its ndf; the caption names the ndf columns | the values macros, unchanged |

**Two deviations from the plan's text, both in T5:**
- The plan said the note keeps its own caption.
- The "without $C_{\mathrm{resp}}$" χ² now has its own ndf column, so as not to drop its printed ndf. That made "the last column" untrue.
- So the caption now reads "the shape-only $\chi^2$ and its ndf beside it; the last two columns give …, and its ndf". The ledger records this as T5-b.

## The checks (STEP4-PLAN.md §3)

1. **Ledger** (`step4/check_ledger.py`): 7 rows, 22 probes, 5 changed base sentences, 0 failures; self-test PASS.
   - Each corrected fact has a home:
     - `L:` for the code facts (`technote_style.py`; `CVUniverse.h`; `runEventLoopOmniFold.cpp`; `overlay_eavailW_band.py`);
     - `N:` for the section's own numbers.
   - `X:` probes confirm the wrong wording is gone.
2. **Two-direction review** ([review.md](review.md)): 3 findings, all fixed:
   - T4's "hadronic" said more than the code computes;
   - T5's group header "shape-only" read like a covariance choice;
   - T5's caption missed the shape-only ndf.
   Nothing was lost, weakened or added.
3. **agy's targeted read** ([agy-read.md](agy-read.md)). On the final text (`agy2/`), every difference agy lists is its
   pair's declared correction. The identity filler reads NONE, and the control catches 3 of 3 planted changes.
4. **Table 16's number probe** (`tools/check_table_macros.py`): 31 numbers, each its macro, in the rendered table;
   self-test PASS. Its plants are a typed number in the source and a changed value inside the table's block.
5. **Build, pieces and held:**
   - the pieces were cut from a build of `527a2a7e` ([PIECES-PROOF.txt](PIECES-PROOF.txt)):
     - B05, B07 and B09 change by this round's edits;
     - B08 holds the same words in another order;
     - the rest are byte-identical;
   - held check: 29/29 exact;
   - local CI: in the PR.

## Outcome

T1, T2, T4 and T5 are adopted. The note's register score stays at 3.278, as measured on Step 3's adopted text; this
round makes no rater runs.
