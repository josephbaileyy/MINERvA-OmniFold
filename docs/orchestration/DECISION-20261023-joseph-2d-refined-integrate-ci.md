# DECISION 2026-10-23 (second) — Joseph: switch the adopted 2D result to the refined estimator; integrate RE-1 now; add a CI check

**Recorded by** the paper-tighten lane, as director.

**What led to it.** RE1-REPORT-2 (PR #265; rulings PR #268) found C2 FLAG. In a nominal-truth 2D closure with
background (20 seeds), the purity arm's mean residual reaches +5.89 σ_stat in 14 of 205 cells, and the refined arm
stays within ±0.44 σ_stat. On data the switch moves the 2D result by at most 0.497 σ_total. The director put four
decisions to Joseph:
1. **The adopted 2D result:**
   - (a) switch to the refined estimator and rebuild what depends on it (recommended);
   - (b) keep purity and state the bias;
   - (c) switch the central value only (not recommended).
2. **The background-treatment revisit (OI-6):** this follows from 1.
3. **When to integrate the RE-1 numbers and figures:** after the human read (recommended), or now.
4. **Commit-time enforcement of the record checks:**
   - (a) a GitHub check on PRs (recommended);
   - (b) update the shared checkout's hooks.

Joseph's answer, verbatim:

> 1. do a 3.  integrate now, we can easily restart our reading rounds 4. a

sha256 of the text plus a final newline begins `e2274f6334a9f8b1`.

## What is decided

1. **The adopted 2D result moves to the refined estimator,** with everything that depends on it rebuilt for that
   estimator: the 2D central value, its covariance, the comparison with MINERvA's published result, and the printed 2D
   numbers.
   - **Step 1 is a plan, and runs nothing.** The re-1 lane writes `RE2-PLAN.md`: what depends on the adopted 2D
     result, the measured unit costs, the declared controls, and the charge against the 2D closeout ceiling
     (`AUTHORIZATION-20261012-2d-closeout-delegation.md` §3 item 2, `:52-58`, ≤ 700 CPU node-h in all; first
     cited as "§2", corrected 2026-10-23 after the re-1 lane found the mis-citation).
   - Runs follow the usual declaration and binding. A cost beyond the remaining ceiling goes back to Joseph.
   - Until the rebuilt result is adopted, the note and paper print the current 2D result, and say plainly that a
     closure test found a purity bias in 14 cells and that the 2D result is being moved to the refined estimator.
2. **OI-6 follows from item 1** (Joseph answered items 1, 3 and 4; the director recorded item 2 as consequential). When
   the rebuilt 2D result is adopted, the refined treatment is used in every dimension, and the note records the
   background-treatment revisit as carried out, with RE-1 as its evidence. Until then the note says the revisit is in
   progress, with C2 as its first result. The director confirms this reading with Joseph in his next report.
3. **The RE-1 numbers and figures are integrated now:** the thirteen 3D numbers and five figures of RE1-REPORT-2 §4,
   and the `sec_3d.tex:130-134` wording fix. Joseph and Ben's reading round restarts on a new reading copy, with a diff.
   The 3D numbers that compare against the 2D result change again when the 2D switch lands.
4. **A GitHub Actions check** runs the record checks on every PR: the manifest check, the hash bindings, the registry,
   the results index, and the absence-claim check against the PR's base. Joseph's shared checkout and its hooks are not
   touched.

## Not changed

- No submission, deposit or tag. Claims beyond these items stay Joseph's. MP-2 stays held.
