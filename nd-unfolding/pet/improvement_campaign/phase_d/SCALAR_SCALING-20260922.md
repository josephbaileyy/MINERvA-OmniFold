# Does more data help? Scalar development-stage scaling (2026-09-22)

**Development evidence on the DEV halves, not the confirmatory Phase D.** Protocol §6 runs Phase D on fresh,
identity-disjoint draws from pool S with a common untouched evaluation population; this study runs on the historical
halves, which development is allowed to use and confirmatory work is not. Its purpose is to tell the PET campaign
which scaling axes are worth buying GPU time for.

Inputs: the B1 populations (`populations.npz`, sha256 `b2b55791a255…`), B1's scoring (the historical seven-bin
`E_avail` recovery, regions, `scm.score_push`), B1's `HGBRatio` scalar OmniFold and the Phase F AUSSIE
implementation. Reco inputs `muon + reco E_avail`, truth inputs `truth4`. 222 runs, 3 draws × 4 sizes × 6
estimators plus the effort sweep, run locally (5 workers), `results/scalar_scaling.json`.

**Three caveats that limit what these numbers mean.**
1. The subsets are drawn from one pair of halves, so different "draws" **overlap**; they measure draw-to-draw
   variation within one population, not independent event draws. Protocol §6 forbids presenting such subsets as
   independent, which is why the confirmatory study uses pool S.
2. Subsampling the **prior** also shrinks the population the score is computed on, so the evaluation target moves
   with the sample. The oracle anchor below is measured per subset for exactly this reason.
3. Fewer events at fixed hyper-parameters also means fewer optimizer updates/trees; the effort sweep separates
   these two.

## The finite-sample ceiling (oracle anchor)

The exact injected tilt applied to the prior subset — the best any estimator could score on that evaluation
sample — is `0.969 ± 0.007` at 75k, `0.974` at 150k, `0.984` at 300k and `0.984` at 600k. Recovery below is raw;
divide by these to normalize.

## 1. Prior-MC size (pseudodata fixed at full size), aggregate recovery, mean ± sd over 3 draws

| estimator | 75k | 150k | 300k | 600k |
|---|---:|---:|---:|---:|
| OmniFold, carry-misses, k = 3 | 0.337 ± 0.007 | 0.369 ± 0.018 | 0.411 ± 0.004 | 0.416 ± 0.007 |
| OmniFold, carry-misses, k = 20 | 0.447 ± 0.005 | 0.524 ± 0.058 | 0.582 ± 0.021 | 0.548 ± 0.009 |
| OmniFold, efficiency-corrected, k = 3 | 0.749 ± 0.035 | 0.748 ± 0.027 | 0.827 ± 0.017 | 0.793 ± 0.020 |
| OmniFold, efficiency-corrected, k = 20 | 0.794 ± 0.106 | 0.791 ± 0.041 | 0.862 ± 0.033 | 0.813 ± 0.035 |
| AUSSIE, λ = 0 | 0.816 ± 0.020 | 0.820 ± 0.066 | 0.880 ± 0.035 | 0.849 ± 0.027 |
| AUSSIE, λ = 1000 (misses pinned) | 0.679 ± 0.164 | 0.641 ± 0.068 | 0.663 ± 0.022 | 0.648 ± 0.025 |

## 2. Pseudodata size (prior fixed at full size), aggregate recovery

| estimator | 75k | 150k | 300k |
|---|---:|---:|---:|
| OmniFold, carry-misses, k = 20 | 0.541 ± 0.037 | 0.540 ± 0.024 | 0.551 ± 0.014 |
| OmniFold, efficiency-corrected, k = 20 | 0.827 ± 0.014 | 0.783 ± 0.039 | 0.815 ± 0.050 |
| AUSSIE, λ = 0 | 0.818 ± 0.041 | 0.847 ± 0.010 | 0.852 ± 0.042 |

## 3. What this says

- **The prior-MC axis is the one that pays, and only in the historical (carry-misses) mode.** Going 75k → 600k
  lifts carry-misses recovery by `+0.079` at k = 3 and `+0.101` at k = 20 — real against a draw spread of 0.005–0.06,
  and still rising at 300k. Whether it continues past 600k is **not measured here**; that is the confirmatory
  Phase D question on pool S.
- **Pseudodata statistics are not the limitation in this range.** Over 75k → 300k no estimator moves by more than
  its draw spread. In other words the fitted detector-level ratio is not pseudodata-starved at these sizes.
- **Miss handling dominates every statistical axis.** At every size, switching from carry-misses to efficiency
  correction is worth roughly `+0.3` — larger than any size effect measured here, and consistent with the Phase F
  ablation and with arXiv:2504.06857's reason for correcting efficiency after unfolding.
- **The efficiency-corrected and AUSSIE curves are flat in the prior size**, which is what one expects when the
  estimator is limited by its extrapolation assumption rather than by statistics.
- **None of this is a PET result.** It says where PET's GPU time should go: more prior MC and more iterations in
  the historical miss mode, and a direct test of the miss-handling mode itself.

## 4. Effort at fixed event counts

The effort sweep (GBDT `max_iter` 10/25/50/100 with early stopping off, AUSSIE epochs 10/25/50/100, at 75k and
600k) is in `results/scalar_scaling.json` under `exp = "vary_effort"`; it separates "more events" from "more
training". Runtimes per run are recorded there (6 s to 103 s per run at these sizes).
