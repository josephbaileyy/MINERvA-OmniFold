# OUTCOME 2026-09-25 — Tier-S coverage of candidate F2: FAIL (futility), independently reproduced

**CITABLE FOR:** the predeclared Tier-S coverage verdict of the scalar-5D campaign's candidate F2
(deterministic LightGBM OmniFold) under contract amendment 4 (bias-corrected statistical intervals on the
153 reported functionals): **FAIL by the amendment-3 futility rule** at the first 400 declared validation
seeds of every grid point. It also covers the per-point failure pattern, the independent recomputation,
and what the verdict rests on. **NOT CITABLE FOR:** coverage of any other construction (the uncorrected
reported `f_hat ± σ` intervals were not tested and are predicted by D1 to undercover worse); any statement
about the adopted trunk `3d7465f6…` beyond the purity-background bias already recorded in
[`OUTCOME-20260925-s5c-purity-background-bias-at-high-W.md`](OUTCOME-20260925-s5c-purity-background-bias-at-high-W.md);
the q3-conditional point as evidence about the estimator (§3).

Campaign: [`CAMPAIGN-s5c-20260924-index.md`](CAMPAIGN-s5c-20260924-index.md). Rule and construction:
[`state/s5c/contract.json`](state/s5c/contract.json) (frozen `c29dde25`), amendment 3's futility rule,
[`state/s5c/contract-amendment-4-f2-revision-2.json`](state/s5c/contract-amendment-4-f2-revision-2.json)
(frozen `95d0e87c`). Review dispositions before the look:
[`state/s5c/review-3-disposition.json`](state/s5c/review-3-disposition.json).

## 1. The look

`nd-unfolding/s5c_futility_watch.sh` (deploy `12d94181`) ran the frozen evaluator unattended at
**2026-09-25T17:40:55Z**. It had waited until all 1,200 declared seeds existed (400 per grid point:
nominal 200000–200399, `eavail_tilt` a=0.2 204000–204399, `q3_given_eavail_w` a=0.3 208000–208399). It then
applied `--interim 400 --bias-correction`, wrote the stop file, and cancelled the three running validation
allocations (58868867, 58870274, 58872289). No further validation experiment ran.

Receipt: [`state/s5c/tier_s/interim_400.json`](state/s5c/tier_s/interim_400.json), sha256 `aa574c17…`,
identical to the cluster copy; watcher log and stop record alongside.

| grid point | futile at 68% (UCB < 0.66) | futile at 95% (UCB < 0.94) | min coverage 68% / 95% | median coverage 68% / 95% |
|---|---|---|---|---|
| nominal | 0 | **2** (EW36, J161) | 0.570 (EW36) / 0.850 (EW36) | 0.710 / 0.960 |
| `eavail_tilt` a=0.2 | **51** | **42** | 0.060 (J224) / 0.288 (EW17) | 0.665 / 0.950 |
| `q3_given_eavail_w` a=0.3 | 153 | 152 | 0.000 / 0.000 | 0.000 / 0.000 |

Per-comparison level 0.05/459. The median half-width over σ is 1.03–1.04 at every point, so the
correction's standard error barely widens the intervals.

## 2. What the verdict rests on

- **The verdict does not depend on the q3 point.** Nominal alone is futile at 95% (EW36, J161), and the tilt
  point alone at 51 (68%) and 42 (95%) functionals. At 0.05/306, with the q3 point dropped, the counts are
  nominal 1/2 and tilt 51/42 (review round 4).
- **Nominal**, where the correction was estimated: EW36 keeps a −0.44% residual after correction (σ/f 0.63%),
  and its pulls spread 1.16× wider than σ. This was predicted by review round 3 (M2): the Tier-S σ comes from
  a bootstrap that does not redraw background. The nominal 68% UCB clears its threshold by only 0.0003.
- **E_avail tilt**: the nominal-truth correction does not transfer (EW17 is still +1.05%, 2.6σ, after
  correction). The highest-W cells cover 0.07–0.13 at 68%. This was predicted by review round 3 (H2) from
  development experiment `p3_tilt20_s2`.
- F2 has used both development revisions the plan permits (plan §6). A validation failure may not be used
  to tune and re-test on the same sample (plan §7).

## 3. The q3-conditional point: a construction defect, not estimator evidence

Review round 4 found that 2,801 pass_truth rows of the input sample carry −9999 sentinel gen values
(q3: 1,327; W: 1,474; 1,755 of them pass reco). `truth_weight` included them in each (E_avail, W) cell's
q3 mean, variance and re-centring, while `np.histogramdd` drops them from `x_true`. In the lowest-E_avail
row the per-cell q3 spread went from 0.24–5.06 to 45.8–3,793, all but removing the deformation there, and
the in-grid (E_avail, W) marginal of the truth was not preserved (EW5 1.128, EW36 0.981; every other cell
0.995–1.003).

Amendment 4's statement that for the M1 (E_avail, W) functionals this point's truth equals nominal
therefore holds for the intended construction, not for the implemented one. The data flow itself is
verified: an independent rebuild of r, the half-B mask and `x_true` reproduces the products exactly;
Poisson rate sums match; an ideal unfold matches truth to within 1% per cell; the total closes to 1.0002.

The q3 point's total failure (unfolded/truth 0.84–1.36 on the EW cells) tracks a reco-level (E_avail, W)
distortion: higher-q3 events reconstruct at lower W, giving a pseudo-data/MC ratio of 0.83–1.23 per reco
cell, correlated at 0.93 with the unfolded/nominal pattern. That is consistent with the estimator placing a
reco (E_avail, W) distortion in truth (E_avail, W) rather than in q3. It is **not proven** without further
unfolds, and it is recorded as a lead, not a result.

**Repaired** after the verdict: `truth_weight` now takes its statistics over in-grid rows only and leaves
out-of-grid rows at r = 1 (`nd-unfolding/s5c_pseudo.py`), with a regression test that is red on the
defective code. The repair affects future experiments only. None of this campaign's products changes, and
the verdict (§2) does not use this point.

(The campaign's own first diagnosis of this point, a q3-dependent completeness, was wrong; review round 4
measured completeness ≈ 1.)

## 4. Independent reproduction

Review round 4 (isolated worktree at `83b16c16`, read-only) recomputed the verdict with its own
functional, σ and Clopper–Pearson code, without importing the evaluator. Every hit count, UCB and σ is
identical to the receipt. Its metadata checks passed for all 1,200 products and 200 bootstrap replicas:
truth, amplitude, seed, split key, config, input and background digests, code digests, no duplicates, and
every product written before the look.

## 5. Consequences

- **No measurement uncertainty checkpoint qualifies** under the plan. The Tier-S gate is failed for F2's
  bias-corrected intervals, and the uncorrected reported construction was not validated.
- The reported F2 construction (`C_Z` under F2) was held before completion and not assembled
  (review-3-disposition.json, resource decision); no F2 product is adopted.
- **Three independent causes** each defeat Tier S, and none is estimator-seed behaviour, so no remaining
  estimator family can meet the requirement:
  1. the purity background method's closure bias, which is estimator-independent (D1);
  2. a statistical σ that omits background sampling;
  3. non-transfer of a nominal-truth correction under truth departures.
- Spend: validation used 15.35 CPU + 6.0 GPU node-h. The campaign total is 20.09 CPU + 9.79 GPU node-h
  (39.2 A100-h) of the 500 / 500 envelope
  ([`state/s5c/tier_s/meter-measure-20260925T1749Z.json`](state/s5c/tier_s/meter-measure-20260925T1749Z.json)).
