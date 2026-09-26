# s5e diagnosis — independent review, round 1 (operand level)

**Reviewer.** An independent agent, read-only, in the isolated worktree `MINERvA-OmniFold-s5e-review1`
(detached at `0998742b`), using its own code; it did not call `s5e_analyze_diag.py`.
**Scope.** No Slurm submission. Nothing was written outside `/pscratch/sd/j/josephrb/s5e-20260925/review1/`
and the session scratch. The review worktree's `git status --porcelain` was empty afterwards.
**Artifacts.** Scripts and outputs are copied beside this file in `review1/`; the `.out` files are
stored as `.out.txt` because `.gitignore` drops `*.out`.

## Verdicts, as returned

| # | item | verdict | reviewer's numbers (abridged) |
|---|---|---|---|
| 1 | instrumentation and D0 | CONFIRMED | `trace_checks` = iterations in all 83 traced products; D0 28/28 bitwise (xsec and xtrue); data_b0 = c7 bitwise; the tracer core is unchanged between the production deploy (`ceb5b8af`) and the repair deploy (`e1516836`; the diff only adds code) |
| 2 | D1 | CONFIRMED | E_avail driver 10.498/73.783% vs npz 10.852/73.507%, difference 1.781 pp (EW17), correlation 0.99976; q3 4.953/37.628 vs 5.002/37.770%; the injection wrapper is equivalent (npz completeness 0.9996–1.0004; xtrue ratio 1.000000); the row-alignment check is trivially true by construction, and the real parity comes from the repaired `input_parity` |
| 3 | D2 and repairs | CONFIRMED (one LOW) | seeds and upcast bitwise inert; zeros confirmed (plus MC reco E_avail 2,104 and data E_avail 82); edge-safe probe on data 1.225/0.179% and 0.983/0.188%; driver–npz 1.286/0.189% before the mask and 1.042/0.277% after; parity after removing 2,801 rows exact up to 7.6e-6 (389.26 events); statistical σ ≈ 0.208% |
| 4 | D3–D5 numbers | CONFIRMED | every table value reproduced |
| 4 | observability verdict | PARTLY | F2 |
| 5 | D7 | CONFIRMED; naming justified | B0 − signal-only 11.24 / 57 / 1.461%; refinement-capacity 4.05 / 1 (J58 +0.038 ± 0.009%); expectation template 15.32 / 61; closure 6.94 (41) / 2.78 (0) / 2.98 (0); only `refine_override` differs between the variant's products and B0's |

## Findings and dispositions

| finding | severity | reviewer | disposition |
|---|---|---|---|
| F1 | HIGH | §7 labels as EXCLUDED factors that moved the metric by ≥ 10%. Iterations on E_avail: median −25.8%, max −18.4% (k 5 → 30), still falling ≈ 0.10 pp per iteration, about k ≈ 35 to reach the 30% screen. Missed-event unity on q3: median −14.1/−12.9/−14.7% at k = 5/15/30. Early stopping on q3: −34% (k = 1 vs 5) | **ACCEPTED.** §7 rewritten. Iteration count (E_avail), missed-event treatment (q3) and stopping (q3) are recorded as factors with measured partial effects below the predeclared 30% screen, not as excluded. The candidate decision (amendment 3) now states them and why they do not justify a candidate. |
| F2 | MEDIUM | "directions the reco data barely constrain" and §8's "therefore an unfolding-model dependence" go beyond the evidence. The remaining imprint is a noncentrality of λ_EW 144 → 68 (≈ 12σ → 8σ) and λ_5D 368 → 164 for E_avail. In D3 signal-only the unfolded fold fits worse than truth (χ² 160 vs 53 at k = 5), so a slow-convergence component is present. The q3 verdict fired at a state (capacity k = 1) with λ_EW 1109, though it also holds at capacity k = 15 | **ACCEPTED.** §§4, 6–8 rewritten. The residual's reco imprint is small relative to the departure's own signal but statistically strong at the analysis exposure. Convergence is slow and incomplete within 30 iterations, and observability is not established as the sole cause. The departure residual is carried as a measured, estimator-dependent model dependence (what these data and this estimator leave), not as an identified property of the detector alone. The q3 verdict is annotated. |
| F3 | LOW/MEDIUM | D7 wording: "removes" (J58 still t = 4.05); "> 90%" (median 93%, minimum 82%); the direct refinement-capacity − B0 comparison (max \|t\| 12.46, 61 functionals) not reported; reco residual 4.13/0.52% → 1.68/0.07%; variance cost (per-seed closure SD ratio 1.12 median, 1.055 EW); the propagation sentence rests on Spearman −0.32 (p = 0.036) | **ACCEPTED.** §5 rewritten with all of these. |
| F4 | LOW | D2 per-functional reading: mask moves 45 functionals above the probe, 12 of them shrinking the difference; driver–npz exceeds the probe in 57 of 153. On the noise-free path the moves are symmetric (34 shrink, 32 grow), so they are noise and "no factor named" stands. "The mask accounts for the largest path difference" is cherry-picked | **ACCEPTED.** §3 rewritten: the mask is not named on either path. |
| F5 | LOW | "≥ 99.2%" holds only in the EW projection; the 5D q3 explained fraction is 0.986–0.989 | **ACCEPTED**, stated with its basis. |
| F6 | LOW | missed-event figures are the signal-only k = 1 run; background-inclusive 1.43/5.75%, k = 5 0.09/0.45%, q3 k = 1 4.8/9.2% | **ACCEPTED**, reported. |
| F7 | LOW | 87 npz products (83 traced + 4 driver) | **ACCEPTED.** |

**Not recomputed by the reviewer:** the D6 R² values (LightGBM training). The W = 0 fractions were
confirmed (1.14% MC, 1.18% data).
