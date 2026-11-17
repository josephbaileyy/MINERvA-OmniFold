# PRD-referee read of the D_IBU paragraph (2026-11-11; an independent general-purpose subagent, no tools)

# Referee report: the IBU-distance paragraph in Section 4

I worked only from the facts in your prompt and used no tools. One exception: the covariance condition number of about 1e12 appears only in your Question 3, not in the recorded facts. The paper should cite it only if a record supports it.

## 1. "The difference arises mainly in the unfolding step"

**What the facts show.** The inputs and grid are held fixed. On them, a binned IBU at the published iteration count (K=10) lands at chi2/ndf = 1.03 from the published result. The OmniFold result on the same inputs lands at 2.27. The paired test (T = 382.8 against a null maximum of 138.5) is the only calibrated statement here, and it says the two unfoldings differ beyond their paired noise. The five-observable estimator reproduces the 2D result (2.36), so the effect is shared by the OmniFold estimators on these inputs, not peculiar to the 2D fit. Changing only the unfolding method therefore brings the result much closer to the published shape. That localization is a real finding.

**What the facts do not show:**
- **Equal inputs.** The IBU shares this analysis's inputs, so it cannot separate input differences from method differences. Several inputs were never compared with the publication: the event files and the earlier-processing run period, flux, nucleon count, out-of-phase-space treatment and detector response. Those differences could still contribute, and they could enter OmniFold and IBU differently. An input effect that only becomes visible through OmniFold's regularization is not excluded.
- **That chi2/ndf near 1 means reproduction.** The IBU and the published result share almost all their data events. An exact reproduction would sit near chi2 = 0, not 1. A value of 1.03 means the differences are about the size of the full published uncertainties. Under an ill-conditioned covariance, a few poorly determined directions can also dominate the value. It is a descriptive distance, not a measure of agreement.
- **A clean split between "unfolding step" and inputs.** Chi2 is not additive, and no decomposition was done, so "mainly" is a quantitative claim nobody measured.
- **An OmniFold-specific defect.** The IBU distance itself swings from 3.95 (K=1) through 0.83 (K=5) to 2.16 (K=20). Regularization strength alone moves it by more than the OmniFold-to-IBU gap. That fits a regularization difference as well as anything specific to OmniFold. The record offers no mechanism, so the paper should not hint at one.
- **Blindness.** The IBU uses this analysis's background treatment, which is one of the two choices made with the comparison in view.

**More precise wording:** drop the causal "arises" and the unquantified "mainly". For example: "with the inputs held fixed, changing only the unfolding method brings the result much closer to the published shape; differences between these inputs and the publication's are not excluded as a contributor."

## 2. Presenting K=10 and K=5

- **K=10 first is correct.** It is the declared primary and the published count, which protects against cherry-picking.
- **K=5 beside it is a problem as written.** K=5 is also the minimum of the scan, so quoting it alone looks like selecting the best value. The phrase "the iteration count of this paper's estimators" also implies that five OmniFold iterations and five IBU iterations are comparable regularization, which nothing establishes.
- **The K-dependence should be stated.** Values are 0.83–1.59 for K=2–15, 2.16 at K=20 and 3.95 at K=1. The scan is informative: for K=2–15 the IBU stays well below 2.27, so the comparative claim is robust. It also shows the distance is strongly sensitive to regularization.
- **Recommendation:** quote K=10, give the range, and either drop the K=5 pairing or caveat it.

## 3. Scope of the final sentence

"Mechanism not established" is right. "Descriptive" is right but incomplete. It is missing four points:
- The IBU shares this analysis's inputs, so input differences from the publication cannot be excluded as a contributor.
- The IBU and the published result share data, so chi2/ndf near 1 under the published covariance is not evidence of reproduction. An ill-conditioned covariance makes the value more fragile still.
- The calibrated statement is the paired test (IBU differs from OmniFold on the same inputs). The paragraph should point to it so readers know which number carries inferential weight.
- The cross-covariance caveat applies to the IBU-vs-published distance as well, not only to OmniFold-vs-published.

## 4. Sentences now in tension

- **(e) contradicts the paragraph.** "Where the shape difference arises is not resolved" says the opposite of "the difference arises mainly in the unfolding step." Suggested row: "T = 382.8, above the null's maximum of 138.5; IBU on the same inputs lies closer to the published result (chi2/ndf 1.03 at K=10); the mechanism is not resolved."
- **(b), (c) and (f) are in tension because they say "source".** A source is partly what the paragraph now localizes. Change "source" to "mechanism" and add the localization:
  - (b): "...a correlated shape difference that accompanies the unfolding method on fixed inputs and whose mechanism has not been identified."
  - (c): "The mechanism of the shape difference has not been identified; a binned unfolding of the same inputs lies closer to the published shape."
  - (f): "...a shape difference in two dimensions, much reduced when only the unfolding method is changed, whose mechanism is unidentified; it does not validate the five-observable distribution."
- **(a) is still true but under-describes.** "Reason" reads as mechanism. Suggested: "...within about 1%, but differs in shape; a binned unfolding of the same inputs lies closer to the published shape, and the mechanism of the difference is not established."
- **(d) is consistent.** It accurately describes the OmniFold benchmark and needs no change. An optional pointer to the IBU comparison would help.

## 5. Recommended wording and verdict

"On this analysis's own inputs and grid, a binned IBU lies at chi2/ndf = 1.03 from the published result under its covariance at ten iterations, the published count and this comparison's primary setting (0.83–1.59 for two to fifteen iterations, 2.16 at twenty and 3.95 at one), against 2.27 for the two-dimensional OmniFold result; the paired test above shows the two unfoldings differ beyond their paired noise. With the inputs held fixed, changing only the unfolding method therefore brings the result much closer to the published shape, although differences between these inputs and the publication's (Table X) are not excluded as a contributor. The mechanism is not established. Because the IBU and the published result share data, the cross-covariance is unavailable and the published covariance is ill-conditioned, these chi2 values are descriptive, and a value near one does not by itself indicate reproduction."

If the condition number is not on record, cut "and the published covariance is ill-conditioned".

**Verdict: ACCEPT WITH CHANGES.** The localization is supported in comparative form. The required changes are: remove "arises mainly", show the K-scan instead of the K=5 pairing, add the shared-inputs and shared-data caveats, and reconcile (e) (a direct contradiction) and the "source" wording in (b), (c) and (f).
