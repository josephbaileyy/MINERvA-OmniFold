# Independent statistical-design review — dispositions (commit `8d9aaf8d`)

**Reviewer:** an independent read-only Claude specialist (not involved in the design), detached worktree
`MINERvA-OmniFold-pfd-review-stat` at `8d9aaf8d`; afterwards `git status --porcelain` (also `--ignored`) was
empty. No final-bank data opened. Synthetic probes and Gaussian simulations in the reviewer's scratch only.
**This file is the orchestrator's restatement and disposition.** Every finding was checked against the code.
Analysis tests at review: 59/59.

| # | sev | finding (restated) | verified | disposition |
|---|---|---|---|---|
| 1 | BLOCK | C4's 2.5 × empirical-sd width limit nearly equals a calibrated B = 6 interval's expected width (t₅ c₄ = 2.45) and is a one-look point rule: correctly calibrated procedures fail it about half the time. | yes (arithmetic) | **Fixed** (Amendment 2c.2): limit relative to the calibrated expected half-width, 1.25 × t c₄ √(1+1/B) × RMS error; implemented and tested. |
| 2 | MAJOR | The interval omits √(1+1/B) for the member mean → nominal 95 % ≈ 0.937, 68 % ≈ 0.646; low C1 power at 68 %. | yes | **Fixed** (2c.1); calibration test rebuilt on the bootstrap model (delta ~ σ, members ~ σ) → nominal coverage reproduced; pull scale updated. |
| 3 | MAJOR | §6.6 implementation deviated: 6.5 skipped when the cheaper design led; UNRESOLVED before 6.6.2; order when the costlier design is materially better and the cheaper passes 6.5 ambiguous. | yes (reproduced) | **Fixed** (2c.3): per-pair order (i) 6.5 → cheaper, (ii) costlier materially better, (iii) cheaper materially better, (iv) equivalent → tie-break; ruling on the ambiguity from the goal text (comparable + ≥ 2× cheaper → smaller); tests for each branch; an old test that expected the large model to win on a missed saving threshold was wrong against the brief and is corrected. |
| 4 | MAJOR | Look 2 possible without the look-1 file; ranking verdicts not carried; SELECTED while a candidate pending. | yes | **Fixed** (2c.4): look 2 refused without `previous`; decisive ranking carried; CONTINUE while pending. |
| 5 | MAJOR | B1's Clopper–Pearson treats (case, draw) units as independent although the 21 cases share each draw; anti-conservative; a cluster-robust 10 % bound is unattainable with 8 draws. | yes | **Accepted as a labelled limitation** (2c.5): B1 remains the protocol's rule, labelled independence-based, with a replicate-cluster companion reported; the report states that the design cannot support a cluster-robust 10 % bound at n_S = 8. |
| 6 | MAJOR | Sizing: no D3 in the pilot; E4/E5 fixed at 8; n_F driven by a noisy pilot mean; pilot design must match the chosen large design; m declared. | yes | **Fixed** (2c.6): size at min(pilot mean, 0); joint power reported; D3 pilot rows added; E4/E5 sized by the rule; re-pilot if the large slot is not L128S1 K = 5. |
| 7 | MAJOR | Bank-conditional estimand; the bank's offset does not shrink with n (≈ half the −0.02 margin for paired E0); 0.773 is a variance factor. | yes | **Fixed in scope** (2c.7): estimand stated as bank-conditional; bank-effect bound reported beside §6.5; factor clarified. |
| 8 | MAJOR | Two-phase freeze: the Amendment 3 heading would unlock all scoring at once; m could change with a third finalist; no retry policy. | yes | **Fixed** (2c.9–10): explicit UNBLIND amendment after a completeness manifest; retry policy (identical config/draw/seed only). m is set by Amendment 3 with the decision set. |
| 9 | MINOR | Point rules (B2, C2, U2a, U2c) without error control near thresholds. | yes | **Fixed (reporting)**: intervals reported; B2 flags "statistically unresolved". |
| 10 | MINOR | N2 uses pilot seed runs. | — | **Ruled** (2c.11): N2 characterizes estimator stochasticity; DEV seed runs are appropriate. |
| 11 | MINOR | The 3F floor is for 7-bin histograms; 28-bin floors are ~2× larger. | yes | **Fixed** (2c.8): 3F × max(1, √(nbins/7)); test added. |

**Sound per the reviewer** (not re-litigated): all-parts-must-pass eligibility needs no within-rule correction;
ranking among eligible candidates with m = 2 keeps family-wise error ≤ α; α/2 per look is valid for any look-2
trigger; event pairing enforced by row digests; t-bounds valid given the banks; exact Clopper–Pearson; coverage
target excludes pseudodata bootstrap weights; distinct-member checks; the cluster bootstrap for pooling bins; the
0.99 over-coverage cap; the top-bin width limit has ample room on DEV.

**Not assessable by the reviewer:** the actual pilot numbers, the pseudodata/prior/seed variance split, bootstrap
validity for this ML estimator, bias size relative to σ (DEV top-bin residuals for H2S1 at k = 5 hint at ≈ 1σ bias,
a threat to C1/C2 as an outcome, not a design flaw).

Tests after the fixes: analysis 62/62.
