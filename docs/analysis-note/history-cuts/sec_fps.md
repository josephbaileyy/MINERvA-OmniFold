# Cutdown, §12 (sec_fps.tex): cut log

**Under** Joseph's decision of 2026-11-16 (DECISION-20261116-joseph-paper-batch.md at main `99aefd3f0`, sixth answer,
item 33: "§12 (extended fiducial) is reduced to one paragraph, with its caveat"; item 34, the cutdown) and the
editor's brief: the paragraph states that the value was made with the binned purity correction, which the note has
since replaced, and that its NuWro-shaped prior was not rebuilt after the flux repair; the value stays only with that
caveat.

**The rule (2026-11-13):** history or detail stays in the note only if removing it would change a reader's
understanding of the reported object, its reproducibility, its evidential independence or its limitations.
Everything else goes to the ledger or the records document.

**Base:** `sec_fps.tex` at `8342963c16d74bc10d740e5637d602300557e53a`. Line numbers are the base's. Every removed
passage stays in the commit history at that sha and line, which is its ledger home. The provenance of the validation
battery is the records entry `fps-battery` (R1.9, `app_provenance.tex`), which is unchanged.

**The new section** is one paragraph assembled from the base's own sentences, in this order: the opening (:4), the
extrapolation sentence (:14), the value and its subtraction (:52–:58), the control (:26), the three priors (:31), the
two tiers (:62) and their status (:64). Words: 1,040 before, 376 after.

| id | base line | words cut | disposition | old text | new text | home of the content | why not NEEDED |
|---|---|---|---|---|---|---|---|
| K1 | :4 | 30 | shortened | "…, with a three-prior dependence envelope, a hidden-variable closure and a 200-pseudo-experiment containment diagnostic for the extension." and "The result consists only of central values and these validation tests, without a quoted covariance." | "…, with a three-prior dependence envelope." The second sentence is cut. | 8342963c1:sec_fps.tex:4 | They announce the tests K3 removes. That no covariance is quoted is still said, by the paragraph's last sentence ("no extended-domain covariance has been constructed"). |
| K2 | :13–:21 | about 210 | cut to ledger | §12.1 "Acceptance and the extended domain": the shares of the rate inside and outside the published cuts, the growth of the truth denominator, and Fig. fpsacc with its caption. One sentence is kept ("In regions without acceptance the unfolding extrapolates through the step-1 regressor for missed events."). | cut | 8342963c1:sec_fps.tex:13–21 | Description of a preliminary study that reports no qualified result (item 33). The kept sentence is the one that says where the value is an extrapolation. |
| K3 | :23–:49 | about 420 | cut to ledger | §12.2 "Validation tests": the list's lead; the published-region check's ratios; the closure item; the per-cell half-spreads of the three-prior envelope; the containment diagnostic; Figs. fpscmp and fpsenv with their captions. Kept: the control's definition and the two sentences saying it does not reproduce the quoted 2D result; the ±1.5% across three priors; the NuWro-shaped prior's definition and that it was not rebuilt after the flux repair. | cut | 8342963c1:sec_fps.tex:23–49; the battery's provenance: records entry `fps-battery` | As K2. Every caveat on the value is kept: the purity correction, the control, the unrepaired prior. The tests cut are passes or descriptive diagnostics of the extension, and none is a stated failure. |
| K4 | :60 | about 95 | cut to ledger | The reporting-grid paragraph (the extended grid's edges; the 185-cell anchor; how the 22.3% and 11.3% shares are counted) | cut | 8342963c1:sec_fps.tex:60 | It defines the grid of the figures and shares K2 and K3 remove. |
| K5 | :51–:58 | 3 | shortened (layout) | The subsection heading "Central value and two-tier reporting"; the displayed equation with its tag "(central value)" | The value is set inline in the sentence it belonged to, which already says "central value". | — | Layout: one paragraph has no subsection. The macro \fpsSigma is used once, as before. |
| K6 | :62 | +2 | antecedent kept | "the acceptance-supported cells (ε ≳ 2%)" | "the acceptance-supported cells (reconstruction efficiency ε ≳ 2%)" | — | ε was defined in the caption of Fig. fpsacc, which K2 removes; the two words are that caption's ("reconstruction efficiency"). |

**Dependent cuts in the same commit:** `sec_summary.tex` (row K3 of history-cuts/sec_execsummary.md) and
`app_statmethods_nd.tex` §B.3 (row K1 of history-cuts/app_statmethods_nd.md).

**Kept on purpose:** "We adopt two-tier reporting" and both tier definitions (the status table and the limitations
paragraph of the executive summary name tier 2); "Neither tier is a completed measurement"; "Tier 1 has no qualified
uncertainty"; the last sentence on the missing covariance.
