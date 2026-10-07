# Recovery interpretation framework for Joseph's D3 disposition (fixed before the outcome)

**CITABLE FOR:** how the publication lane will map each possible outcome of the report-only lost-seed resolution
(`PROCEDURE-20261005-s5p-lost-seed-recovery.md` §5–§6) to article wording and to a proposed D3 disposition. The map
was written **before any recovered outcome was visible**.
**NOT CITABLE FOR:** any outcome, any revision of a primary decision, or Joseph's disposition itself.

**Written:** 2026-10-06. At that time `origin/main` was at `4e7c20bb`: recovery Phase A determinism PASS (16/16),
Phase B parts 1–2 complete (184/184), part 3 (job 59404940) running. No resolution, no frozen-S computation and no
stopping re-application had been reported. This lane had seen no recovered statistic.

## 1. What the resolution measures (from the procedure, not re-specified here)

For each of the 10 tests the procedure reports:
- k and B for the frozen evaluation;
- **(a)** the union with S recomputed, and **(b)** the recovered draws under the frozen S;
- the recovered draws at or above the observed statistic;
- the decisions under (a) and (b);
- the earliest complete-batch stopping decisions (§5.4);
- any residual corners.

The recompute lane cross-checks T for the recovered products (§6). Under §5.5, **"can change" is resolved by
observation only if all three of these hold, with no residual missing draw, or with residual corners that change
nothing:**
- (a) leaves every decision unchanged;
- (b) leaves every decision unchanged;
- the decisions at the earliest complete-batch stops are unchanged.

## 2. Outcome classes and the article wording proposed for each

The frozen primary decisions (Table I of the article) are reported as frozen in every class. The resolution is
always labelled report-only.

| class | condition (procedure §5.5 and §6) | proposed article wording, at `paper_body.tex` §"Lost pseudo-experiments" | proposed D3 disposition for Joseph |
|---|---|---|---|
| **R1: resolved, all hold** | (a), (b) and the earliest stops leave all 10 decisions unchanged; no residual missing draw, or residual corners change nothing; the cross-check AGREEs | "Rerunning every lost pseudo-experiment, as a report-only resolution fixed before the rerun, leaves all ten decisions unchanged, both with the recovered experiments added to the calibration and against the frozen calibration, and at the earliest stopping point of the sequential rule. *N_ge* of the *M* recovered experiments reached the observed statistic." (counts per test in the supplement) | "The lost-seed sensitivity is resolved by observation for all ten tests. The decisions may be stated without the 'can change' qualifier, provided the resolution and its report-only status are stated beside them." |
| **R2: resolved for some tests** | the §5.5 criteria hold for some tests and fail for others | The surviving tests are stated as in R1. Each other test is stated as "rejected in the frozen evaluation; the report-only resolution does not support this rejection (it changes under (a), under (b), or at the earliest stop)". | "Only the tests resolved by observation carry the headline. The others are reported as frozen decisions that the resolution does not support." The headline is narrowed accordingly. |
| **R3: no test resolved** | every test fails a §5.5 criterion | "In the frozen evaluation all ten are rejected, but the report-only resolution of the lost pseudo-experiments does not support these rejections." | **Scientific hold on the joint-test headline.** The article (route B) proceeds with the joint tests as a method demonstration with this negative resolution, or drops the section. Joseph chooses which. |
| **R4: incomplete** | residual missing draws remain and their corners change a decision, or the resolution is incomplete | Corners are stated as in the existing sensitivity, and the affected tests are treated as R2/R3. | As R2 or R3 for the affected tests. No re-recovery beyond the procedure without a new authorization. |
| **X: cross-check disagreement** | the recompute lane's §6 cross-check disagrees on any recovered T | No resolution wording is used. | **Hold** until the recompute lane's disagreement route closes. A disagreement is never settled by changing a reading to match. |

## 3. Interpretation rules this lane will apply (fixed now)

1. **A resolution that holds does not upgrade the primary analysis.** It removes the "can change" qualifier for the
   resolved tests only. It does not alter the stopping history, the B values or the frozen p-values.
2. **Counts are reported, not only verdicts.** For every test, the number of recovered experiments reaching the
   observed statistic is reported, even when the decision is unchanged.
3. **No test is singled out after the fact.** NuWro shape (k = 1) is the test closest to its threshold. It gets the
   same treatment as the others. If it alone fails, that is class R2, stated as such, and it is not explained away.
4. **Power** stays context only (amendment 7). The recovered power draws change only the power table.
5. The interpretation depends on the cross-check (§6). Without its AGREE, class X applies.

## 4. What will be brought to Joseph

When D2 lands (the resolution report plus the cross-check), this lane will bring:
- the class;
- the per-test table;
- the wording from §2;
- the proposed disposition as one sentence for approval;
- any deviation from this framework, each with its reason.
