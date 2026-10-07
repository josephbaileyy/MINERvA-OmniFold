# Final independent review of the PRD article and release (PLAN §7), 2026-10-06

**CITABLE FOR:** the review's target, its verdicts, every finding and the owner's resolution. This is the publication
lane's checked restatement, not a verbatim transcript.
**NOT CITABLE FOR:** any physics result, or coauthor or journal approval.

| | |
|---|---|
| reviewer | a fresh read-only Opus 5.5 subagent in a detached worktree (`MINERvA-OmniFold-final-review`), left clean. It stalled once on a long command and was resumed with its context intact. |
| cycle 1 target | `a87e2888` (article, claim table) plus the RC2 tarball `4146a4e7…` |
| cycle 1 verdict | **NOT READY**: 3 blocking, 10 should-fix, 9 notes. The inference itself was confirmed: all 27 sampled numbers trace to their sources, Table I matches the record row for row, RC2 gives VERIFY PASS, and the open-data terms match. |

## Cycle 1 findings and resolutions (repairs at `f81120be`; RC3 at `5ed1afba`)

| id | finding | resolution |
|---|---|---|
| B1 | The 3D–5D central values were attributed to scikit-learn | **Confirmed.** `ND_OMNIFOLD_STATUS.md:152-153` lists `_lgbm` products, and `run_p4_unfold_std.sh:209` passes `--estimator lgbm`. The article now lists four estimator identities, and the Fig. 2/3 captions name the 5D LightGBM production estimator. |
| B2 | The localization misdescribed Fig. 2 | **Confirmed** from the released arrays. Restated: cell-integrated, 67% of the difference is at E_avail ≥ 0.8 and 83% of that at W ≥ 1.8, with 22% in the widest catch cell; in ratio, 12–31% there and 23–31% at W < 1.1 GeV for every E_avail. The text says no response-mismatch closure was run and names the region of largest bias. **Removed from the abstract.** R10(b) remains a scope decision for Joseph. |
| B3 | Fig. 4 had no release producer | `plot_joint_null_distributions.py` is now in the release; `verify_rc.py` regenerates Fig. 4 (RC3 PASS) |
| S1 | "report-only" missing from the abstract and conclusions | Added to both |
| S2 | D3 disclosures 3–5 incomplete | Added: the next margin, 49.8 (GENIE CV shape); the four early-stop nulls at B = 1200; reading (a) described as a same-rules consistency replay, not an independent recomputation |
| S3 | Table I's B could be read as including recovered draws | B is now defined as "completed at the frozen stop, of 1400 submitted per null (1800 for NuWro)" |
| S4 | W2 conclusion overstated | Scoped: a data-side, single-scale variation applied after calibration, with the null's response unmeasured; "not removed by this data-side variation" |
| S5 | W1 "rejects" | Now "gives p < 0.05 for every test in at least one projection" |
| S6 | The 2D band story was inconsistent | "as first built" in the abstract, introduction and conclusions; the rebuilt band is called not re-tested; rescoring C1 = 78.1% above its window; cause untested |
| S7 | Data-informed disclosure missing | Added: reviewer residuals seen before the freeze; p-values exposed in the status files; the production-budget extension decided while they were visible (DECISION-20261004); no statistic, variant, threshold or stopping rule changed |
| S8 | Bibliography errors | Corrected entries from INSPIRE in `publication.bib`: Huang PRD 112, 012008; MINERvA PRL 129, 021803; MINERvA PRD 114, 072001; Canelli EPJC 86, 106. "Published" became "on data", because NOvA is a preprint. `technote.bib` was not edited. |
| S9 | W2 evidence was on branches only | W2 branch merged (`a5adb086`). W2B status is DONE/AGREE (`aa0ac8ff`). |
| S10 | Fig. 3 could not show the ratios | Redrawn from the released arrays with ratio panels and units (`paper_eavailW_generators_ratio.pdf`) |
| N1 | Missing nuisances | Added the 1.4% normalization, the rounding noise from 20 re-unfolds, the finite-sample residual, and E_ν > 100 GeV (negligible) |
| N2 | Incomplete power sets | Stated (172–199 of 200 retained) |
| N3 | "within its budget" | Now "with any configuration its rules allowed, a scientific rather than a computational limitation" |
| N4 | 32.8 M events | Now "the simulation contains 32.8 million true signal events" |
| N5 | Table I overfull | `\scriptsize`; a residual 0.7 pt is accepted |
| N6 | Fig. 1 legend underscores | Not changed: the Fig. 1 figure is note-owned. Recorded for the note owners. |
| N7 | README runtime | Now 2–11 min |
| N8 | Claim table L2/L3 | Updated to VL170/VL172 |
| N9 | "independently disfavours" | Now "also disfavours" (same data; independent of the recoil response only) |

## Cycle 2

[Recorded after the focused re-check.]
