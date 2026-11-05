# COV2D amendment, rolling audit part 1: the null (e4071821) and the scorer (6ae6b48d)

**Auditor:** the `coverage-5b-audit` session, 2026-11-04, read-only. Its report, received by SendMessage, is copied
verbatim below. The answers and fixes are in `ANSWERS.md` (this directory).

---

COV2D audit part 1 (cov2d_null.py at e4071821 and cov2d_score.py at 6ae6b48d): your six questions hold. I verified Q1 on the real blocks path, not the fixture. There are two low-medium input guards and two test gaps.

How I checked:
- A fresh detached worktree, with the 12 tests passing.
- 23 mutants of my own, each against both suites, with the unmutated pair passing first: 19 KILLED, 2 survivors equivalent, 2 real gaps.
- Afterwards there were 0 .pyc and a clean status.

**Your questions**

**Q1. Each law's covariance is its band's block: yes, on the real code.**
- The algebra:
  - build_repair.wcov (:127–132) centres at the w-weighted mean. So it is Σ p_u (x_u − μ_p)(x_u − μ_p)ᵀ with p = w/Σw, which is Discrete.centred's covariance.
  - With uniform p, 2p2h is ⅓ and each pair band is ¼ΔΔᵀ = two_point(Δ).
  - universe_block replaces MINOS by minos_x on both sides.
- Your null test's C_T comes from its own retyped wcov in Discrete's form (`d = X - p @ X`), so it agrees by construction.
- So I drove the REAL cov2d_blocks.assemble → re2c_rollup.universe_block → build_repair.wcov into the real null_at_T, with ROOT stubbed for the import only. I used five regimes:
  - physical scale (1e-39), with cells spanning decades;
  - lognormal Flux weights, σ 2;
  - a 30% common offset on every universe;
  - spreads of 1e-3;
  - unit scale.
- check_matched came out at 5e-17 to 4e-16 in every regime, with each law against universe_block's own block at ≤ 8e-16 own-scale, and §9.8 PSD passing.
- Worth adding as a test in your PyROOT env.

**Q2. The Gaussian is exactly C_stat + C_norm + C08 + C_model_abs.** assemble's C_T is C_univ + C_lat + C_norm + C_stat + C08 + C_model_abs, with no C_PL_R (cov2d_blocks.py:144). check_matched enforces the sum, and my mutant dropping C08 was killed.

**Q3. The order and algebra are right** (RUN).
- surrogate = (x̂ + Σ s_b Δ_b/2)(1 + 0.014 z) exactly.
- The cross term equals A − B, the lateral-first result minus the normalization-first one, to 2.6e-16.
- The sign convention is immaterial to the law: s = ±1 equiprobable, two_point symmetric.
- All 5 order, sign and cross mutants were killed.

**Q4. score adds nothing to a verdict except INVALID.**
- "A flagged weakened cell labelled" was killed.
- INVALID keeps verdict_graded, as declared, and both INVALID mutants were killed.
- 1B's grade has no 16-cell constant: its divisor is len(p_use) and its n is E.shape[0] (fd_1b_mc.py:657–678).

**Findings, most severe first**

**S1 (low-medium; RUN): score grades any toy count.**
- score and errors never compare E.shape[0] with len(TOY_SEEDS[truth]).
- grade re-derives its thresholds at n = E.shape[0], whereas null_at_T records them at 300.
- Run: 299 and 150 toys were graded with no refusal (k_cell[0] 171 → 170 → 78).
- §5.2's rule is Bin(300, …), and 1B refuses a non-declared seed set before grading (fd_1b_mc.toy_paths).
- What would close it: refuse unless exactly the declared 300.

**S2 (low; RUN): the outlier cell is skipped silently.** If cov2d.OUTLIER_CELL ∉ cells, score drops "outlier_cell" without a refusal (run: cells 0–204). §5.2 requires its reading "whatever it is". The same applies to readouts :116 (part 2, R6).

**S3 (low; RUN): two test gaps.** These mutants survive:
- "outlier read at the wrong position" (i = 0): no test checks the outlier's values;
- "weakened share over the unflagged cells": no test asserts weakened_share.

**S4 (low; reading): errors() takes sigma from the caller** for the cross term, with no shape check and no tie to √diag C_T.

**S5 (note): equivalent survivors.**
- null_at_T's n_toys default is G18's count, used for both truths. Both are 300, so the mutant is equivalent.
- The 205-divisor guard can't fire given the 205×205 check, unless fd_1b_null changes. It's fine as a tripwire.

Next: part 4 (the pilot), checked against part 3's J1.
