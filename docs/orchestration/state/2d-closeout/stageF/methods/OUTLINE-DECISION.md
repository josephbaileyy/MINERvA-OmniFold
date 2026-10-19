# Methods paper: the outline (director's choice after the X4 framing round)

**Owner:** the paper-tighten lane, as director (Stage F), 2026-10-19, under
[`../METHODS-FRAMING.md`](../METHODS-FRAMING.md) §3 step 1. The inputs are
[`x4/gpt-6.1-sol-framing.md`](x4/gpt-6.1-sol-framing.md) and
[`x4/gemini-3.8-flash-framing.md`](x4/gemini-3.8-flash-framing.md).

**CITABLE FOR:** the structure the rewrite follows, and why.
**NOT CITABLE FOR:**
- final wording or claims (claims are Joseph's; the title and abstract are provisional until the Ben review);
- any result not already in a record.

## 1. What was taken from each model

- **GPT-6.1-sol's outline is the base.**
  - It keeps observed outputs, demonstrated properties and interpretive assumptions apart.
  - It makes the bias and coverage results the paper's centre, with figures.
  - It handles each of the referee's twelve comments, and separates framing from analysis (comments 4–6 need
    analysis; that is M2 and SF-1).
- **Gemini's proposals:**
  - **Used:** the calibration flowchart, and the "disclosure as absolution" warning (state the scope once, then write
    with conditional precision).
  - **Rejected:** "the first application of unbinned machine-learning deconvolution to neutrino-nucleus scattering
    data". It is unsupported, and was rejected in passes 1 and 2 too.
  - **Not adopted:** "strong and exceptionally timely". GPT-6.1-sol's assessment ("plausible but presently
    incomplete") is the one the director accepts.

## 2. Structure

| § | title (working) | main point | figures and tables |
|---|---|---|---|
| I | Introduction and scope | The paper evaluates an implementation of multidimensional unfolding and of conditional inference. It does not deliver a validated five-observable measurement. Test calibration and interval coverage are different requirements | a claims-and-evidence table (no new result); the scope statement, once |
| II | Data, observables and domains | Fixed selection; five simultaneous observables whose reconstructed inputs overlap (W is fixed by pT, p∥, q3 at reconstruction); definitions in the article (M4) | an observable-definition table; a generator table (target, energy coverage, flux treatment, test domain) |
| III | Estimators and validation design | Each result belongs to a named estimator configuration | an estimator matrix; a validation-design table (truth change, backgrounds, response, domain, criterion) |
| IV | Two-dimensional benchmark | Normalization within 1.1%; 95.6% of bins within 10%; the covariance-weighted value 2.65 is a descriptive distance; learner dependence; the post hoc central-value choice stated once | Fig. 1, with the exact-split alternative shown |
| V | Bias and coverage in five dimensions | Selected checks pass alongside substantial regularization bias and failed coverage. This is the paper's centre | **new:** background-treatment residuals; deformation recovery; coverage per quantity (M3) |
| VI | What the uncertainty studies establish | The ensembles quantify specified variations, not validated total intervals; an envelope over five tested deformations, against the chosen target | covariance-component table; run-period double ratio; reporting-definition table |
| VII | Central values as illustrations | Estimator outputs for qualitative comparison, with no physical localization | Fig. 2; Fig. 3 only if it serves §VIII |
| VIII | Conditional hypothesis tests | Full-chain calibration tests specified ensembles with a biased estimator: the hypotheses, the generative model, the statistic, the calibration and its familywise bound (M2), validation (SF-1), results, sensitivity | a generative-model table; a calibration flowchart; Table I; Fig. 4 with its shift defined; the refinement comparison |
| IX | Discussion, conclusions, reproducibility | What worked, what failed, what is untested; why unfold before testing (M5); the release | — |

## 3. Rules for the rewrite (in addition to pass 2's)

- **The scope statement** starts from GPT-6.1-sol's Part 3 draft, corrected by the M2 audit:
  - the null is a family below the fine grid, with Tune v1's composition varied by the drawn universes and the
    fine-cell integrals fixed;
  - the size is nuisance-averaged;
  - the familywise bound is "at most 0.9α" under stated assumptions
    ([`M2-FWER-RECORD.md`](M2-FWER-RECORD.md)).

  Caveats that GPT's Part 3 table marks "retain at the claim" stay at the claim.
- **Every number keeps its estimator.**
- **The abstract** (about 150 words) states the conditional rejections only with their conditions, and only if
  SF-1 does not fail. If SF-1 fails for a test, Joseph decides the claim (M8).
- **The descriptive physics interpretations** that the referee flagged (the low-recoil mechanism, the 52% gap
  filling, "separates the remaining discrepancy", the GiBUU tail substitution) are shortened or removed, and each
  change goes to the M8 list.
- **"Model dependence"** is renamed "an envelope over the five tested truth deformations" unless a broader bound is
  shown.
