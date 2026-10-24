# R10 report review (2026-10-24)

**By** an independent read-only reviewer: a fresh Claude subagent of the validation lane, given the declaration, the
bindings, the code, the raw outputs and the draft report, and not the lane's conclusions. It recomputed the report's figures
from `outputs/r10_results.json` and the receipts with `python3 -I`. It did not recompute the cluster file size, or
the EW, H2 and T1 readouts beyond the p90 and n_inf check. **Caveat:** the reviewer is the same model family as the
author. Its first-pass review is summarized below, condensed but faithful (the reviewer confirmed this); the
lane's disposition of each finding follows it, and the re-check of the corrected report is at the end.

## First pass: ACCEPT-WITH-CORRECTIONS

The verdict (INCOMPLETE), the 11 states, the global-null outcome and almost every number reproduce. One finding is
MAJOR (a declared readout is missing, and an inference reads too much into leg B); the rest are MINOR or NIT. **No code
defect.**

1. **MAJOR — nominal split-half floor and the declared nominal E_ν < 20 GeV readout missing.** DECLARATION §6
   requires the GiBUU **and nominal** restricted residuals as ratios to f = 1. The nominal split residual, which is
   split-half noise alone, grows with binning (f1 0.00442; f2 0.00598; C1–C4@f2 0.00666–0.00738; f4 0.02658, twin
   0.02570). It is above W2's cut of 0.00594 in f2, f4 and C1–C4@f2. At f4, W2 0.02666 against nominal 0.02658 (ratio
   1.00), so "W2 2.99 × at f4" is the noise floor. The §3 sentence "does not cut the departure residual … anywhere"
   presents leg B's failure as a property of the added information. *Correction:* add the nominal column and a floor
   bullet, and rescope.
2. **MINOR — "2–9%" margin over the twin.** `width_median_x_over_twin` runs 0.9093–0.9984, so the margin is 0.2–9.1%.
3. **MINOR — "moves no residual toward leg B's cut" is false as worded.** C2@f1 goes 0.996 → 0.981 and C2xC3@f1
   0.978 → 0.964. Say "brings no residual near".
4. **MINOR — the same-role readouts at K ≥ 10 cut by more than a third, configurations and twins alike** (f4 K = 20:
   0.244/0.256/0.363/0.523; twin 0.259/0.275/0.361/0.551). The split role is never cut at any K (closest C4@f1 GiBUU
   K = 20, 0.669). Say so.
5. **MINOR — "111 identities duplicated … all in run00111353".** `duplicate_keys_within_file_all` =
   `sum(ks[1:] == ks[:-1])` counts surplus entries, which equals identities only if each repeats exactly twice. The
   single-file attribution comes from the first run's diagnosis, not this receipt, and "no other playlist" is measured
   over the files read. Resolved-by-vertex = 1 and unresolved = 0 are correct as stated.
6. **MINOR — the guard's own verdict line** (`EMPTY-REPOSITORY-ORIGIN-SET … SAW NOTHING`, "THIS INTERPRETER ONLY")
   should be quoted, with its explanation.
7. **MINOR — "same pass and values as at `b4b1136c`"** cannot be checked: only the `289a1ff7` controls JSON is
   committed.
8. **NIT —** the two reasons for INCOMPLETE are separately sufficient, not independent.
9. **NIT —** attributing the global-null failure to the declared mechanism needs an inference tag; the miss is
   2.6 × the band.
10. **NIT —** "mostly grow" should be "all grow" (12 of 12); "leg B decided every PASS in advance" reads better as
    "leg B alone excludes a PASS".
11. **NIT —** "+∞ (an acceptance hole)": `width_stats` also counts NaN as +∞ (f1 split T2: 47 inf and 4 NaN over 185).
12. **NIT —** the file size of `r10_extra.npz` was from notes, not a receipt; `y-worktree-state.txt` did not show the
    detached state; `review-report.md` must exist and the report be re-checked.

**Verified correct by the reviewer:**
- the global-null recomputation;
- all 11 states and every leg, twin and beat field;
- the §2 table (11 × 12 ratios, margins to 1e-12);
- the thresholds and closest approaches;
- all 30 global-null values;
- the §3 ranges except finding 2;
- all 52 restricted-GiBUU values;
- the sixth-axis table;
- K0–K2 and the admission checks;
- the twins' cell counts;
- the extraction receipt, including 25 input hashes and 12 playlists;
- the compute arithmetic and Y's resources;
- `shasum -c` on every file;
- the code hashes;
- the binding's required statements.

`verdict()`, `leg_a`, `leg_b`, `global_null`, `permuted_within` and `join_rows` match DECLARATION §1, §4.3 and the
amendment. The three code files are unchanged from `289a1ff7`.

## Disposition (the lane)

| # | done |
|---|---|
| 1 | §3 rescoped, with a new bullet on the split-half floor (values recomputed by the lane and equal to the reviewer's). The §4 restricted table gains the nominal value and its ratio for every configuration. |
| 2 | "0.2–9%". |
| 3 | "brings no residual near leg B's cut of 0.667". |
| 4 | §4 states the same-role cuts at K ≥ 10, the exceptions in both directions (lane recomputation: C4@f2 K = 20 and C4@f1 K = 200 cut while their twins are not; C2xC3@f1's twin cut at K = 200 while it is not), and that no split-role figure is cut at any K. |
| 5 | Reworded as surplus entries, scoped to the files read, with the single-file attribution cited to the diagnosis. The same rewording is carried into LEDGER-NOTES (both sites). |
| 6 | The guard line is quoted, with its scope and the reason. |
| 7 | `receipts/controls-only-b4b1136c.json` committed. The lane checked that its `controls` and `admission` blocks equal those of the `289a1ff7` run. |
| 8–11 | Applied as worded. |
| 12 | `receipts/r10_extra.sha256.txt` now records size and sha256 for both copies. `y-worktree-state.txt` records the branch as detached, with 0 modified and 0 untracked files. This file exists, and the corrected report was re-checked (below). |

## Re-check of the corrected report

**ACCEPT-WITH-CORRECTIONS.** All 12 first-pass findings were corrected, and every new number recomputes: the nominal
floor; the 26 nominal restricted values and ratios; the same-role K >= 10 cuts and the complete exception list; and
the closest split-role cut at any K, C4@f1 GiBUU K = 20 at 0.6693, the minimum over every K, departure,
configuration, twin and null3. `shasum -c` passes on all 13 files. Remaining findings, none affecting the verdict or
any state, and the lane's disposition:

| # | finding | done |
|---|---|---|
| R1 | MINOR: "the residual is dominated by split-half noise" and "says nothing about" overstate. Only W2 at f4 equals the floor; at f2 and C1–C4@f2 W2 is 1.56–1.90 × it; GiBUU, W1 and W3 are well above it; at f2 the floor clears W2's cut by 0.7% | heading and close reworded as suggested, with the 1.56–1.90 × range, the GiBUU, W1 and W3 values at f4, and the 0.7% margin (lane recomputed) |
| R2 | MINOR: `y-worktree-state.txt` was rewritten after the review; the pre-Y check it cites is in no committed file | the file now gives all three records with times: the pre-Y check (stated as transcript-only), the original post-Y record verbatim, and the 04:04 re-measurement |
| R3 | MINOR: "127 s" does not match the committed `b4b1136c` receipt's 126.17 s | report and LEDGER-NOTES give 126 s from the receipt; LEDGER-NOTES notes 127 s by the shell's timer |
| R4 | NIT: "most f = 2 pairs at K = 200" should be all five, in both X and twin | applied |
| R5 | NIT: "reads the same in X0 and the first X" rests on uncommitted logs | cited to LEDGER-NOTES, with the logs on pscratch |
| R6 | NIT: CITABLE FOR names only GiBUU for the restricted readout; "split-role figure" should be "split-role residual" | applied |
| R7 | NIT: "reproduced" should be "summarized"; "recomputed every figure" is too broad; add the same-model-family caveat | applied |
