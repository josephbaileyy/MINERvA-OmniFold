# The third two-referee read, 2026-11-05

**Asked for by** the director (2026-11-05), as the readiness measure Joseph tracks, on the paper after the referee
presentation round (#765, merged at main `c6784fa89`).

**The same procedure as 2026-11-04** (`../referee-rerun-20261104/`):
- **The prompt:** `referee-prompt.txt`, byte-identical to 11-04's and 11-01's (sha256 `a24a34a1…`).
- **Two blind referees:**
  - Sonnet as a read-only subagent (`sonnet-referee-task.txt`). Its task is 11-04's, with only the file paths and the
    word count changed. Its transcript shows four tool calls, each a Read of one of its two files.
  - Gemini via agy, with `gemini-3.8-flash-high` and `--sandbox`, run from an empty working directory. It wrote nothing
    there.
- **The manuscript:** the blinded rater copy (`manuscript.blind.txt`), from `rater-calibration/make_rater_copy.sh`'s
  `.blind.txt`, run on a clean worktree at main `c6784fa89`. It has 9,271 words, against 7,676 on 11-04. The growth is
  the presentation round's Appendix A and the disclosures it added.

**Verdicts:**

| referee | 2026-11-04 | 2026-11-05 |
|---|---|---|
| Sonnet | major revision; not publishable in PRD as a measurement with the current set of limitations; reframe as a methods study if they cannot be resolved | major revision; "does not support its title claim, a cross-section measurement with a quoted covariance"; if not resolved, "reframed as a methods and validation study" |
| Gemini | major revision, with mandatory re-scoping to a methodology paper or rejection as a cross-section measurement | major revision, "cannot be accepted as a physics cross-section measurement unless the fundamental validation failures and numerical instabilities are resolved, or the paper is fundamentally rescaled and reframed as a methodological case study" |

**The disqualifying set, against 11-04:**
- **Sonnet, the same four items:** coverage and the stopped test; the prior dependence at generator-sized truths; the
  rounding instability; the run-period step.
  - The low-stability cells move out of the disqualifying combination into a major issue of their own, with R10 and
    R15 called acceptable "if flagged in the table, as the paper does with a dagger".
  - The rounding item now names the zero training-seed block as conflicting with the instability. That is B0's
    reconciliation (DECISION-20261102-joseph-bias-and-stabilisation-routes.md item 5).
- **Gemini, the same three items:** the fake-data bias, the aborted coverage test, and the floating-point instability.
  The 2D shape difference, the run-period block, C_model's circularity, the generator samples and the low-stability
  cells stay among its major issues.

**What the presentation round changed in the reports:**
- Sonnet no longer raises:
  - the "No hyperparameter search … / learner chosen after" inconsistency, which item 1 addressed;
  - the requests for a per-block table, the correlation matrix, the systematic list and the flux integral, which
    item 2 addressed. It now asks for a heat map of Table V.
- Sonnet now reads the 2D comparison as descriptive and the choices as disclosed. Its major issue 5 quotes "The learner
  and the background treatment were both chosen after the comparison was visible", and it asks that the comparison not
  be called an "end-to-end test".
- **New requests:**
  - *Sonnet:* a held-out truth set and the criteria's multiplicity (major issue 8); detector-response mock data beyond
    a scale (major issue 9); the 3^5 typesetting; the origin of the 1.40 % normalization and of the 1.17 factor.
  - *Gemini:* Table II as densities or with the cell volumes; the 16 × 16 matrix's condition number.

**CITABLE FOR:** the two referees' reports on the paper at `c6784fa89`.

**NOT CITABLE FOR:** any physics claim, or a decision.
