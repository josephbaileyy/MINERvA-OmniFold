# Phase F — AUSSIE Scalar Benchmark (2026-09-22)

## 1. Objective and Scope

This document evaluates the AUSSIE (Adversary-free Unfolding SanS Iteration or Emulation) algorithm [arXiv:2602.24282] on a bounded, low-dimensional scalar representation of the MINERvA E_avail unfolding task. The goal is to determine if AUSSIE resolves the observed slow convergence, structural bias, and iteration limits that plague traditional OmniFold and IBU when applied to this dataset, thereby justifying a full evaluation with the PET backbone.

All evaluations here are simulation-only (Phase B1 data), bounded to the `muon_eavail` (reco-side) and `truth4` (truth-side) scalar inputs. The test executes on the exact historical halves and endpoint criteria used in Phase B.

## 2. Implementation and Mapping to the Paper

The AUSSIE algorithm is non-iterative and proceeds in two steps, which we map directly to the paper's methodology:

1.  **Step 1 — Classifier $R_\theta(x)$:** We train an MLP classifier (equivalent to OmniFold Step 1) on the observable phase space `muon_eavail` to distinguish pseudo-data from the prior simulation, optimizing the Binary Cross-Entropy (BCE) loss. The output logit serves as $\log R_\theta(x)$, where $R_\theta(x) \approx p_{\text{data}}(x) / p_{\text{sim}}(x)$ (Eq. 11 of the paper).
2.  **Step 2 — Unfolder $R_\phi(z)$:** We train a second MLP on the truth phase space `truth4` to match the detector-level density ratio $R_\theta(x)$. As the problem is higher dimensional than the toy cases, we employ the AutoDiff variant (Eq. 18 / Eq. 20 of the paper). The unfolder is updated by minimizing the $L_1$ norm of the gradients of the MLC (Maximum Likelihood Classifier) regression loss $\mathcal{L}_{\text{MLC}}$ with respect to the frozen classifier's parameters $\theta$.

**Deviation for Detector Inefficiency (Misses):**
The AUSSIE paper does not explicitly detail the treatment of events that pass generation but fail reconstruction (efficiency misses). In the MLC objective, $x$ is required to compute $\mathcal{L}_{\text{MLC}}$, meaning gradients can only be computed over paired $(x, z)$ events (those passing both reco and truth). B1's OmniFold implementations handle misses via the `carry_misses` strategy, where the target `pull` weight is left as 1 for misses, and the step 2 network regresses this value directly. To ensure a strictly fair and comparable evaluation against B1, we introduce a regression term for the misses:
$$ \mathcal{L}_{\text{miss}} = \mathbb{E}_{z \sim p_{\text{miss}}} [(R_\phi(z) - 1)^2 \cdot w_{\text{truth}}] $$
This penalizes deviations from $R_\phi(z) = 1$ for unobservable events, aligning the AUSSIE unfolder exactly with the `carry_misses` assumption used in the OmniFold baseline.

## 3. Results and Comparisons

The benchmark is run across 3 random seeds (evaluating model variance) on the static Phase B1 halves. AUSSIE ran for 50 epochs in both steps, achieving convergence in ~8 seconds per seed (16 GB Mac, 10 cores).

### Overall and Regional Recovery

| Estimator | Aggregate | Low Acceptance | Moderate | Good |
| :--- | :--- | :--- | :--- | :--- |
| **Binned IBU (k=3)** | 0.472 | 0.011 | 0.577 | 0.866 |
| **Binned IBU (best, k=15)** | 0.683 | 0.040 (k=20) | 0.724 (k=20) | 0.791 (k=20) |
| **OmniFold HGB (k=3)** | 0.412 | 0.041 | 0.472 | 0.733 |
| **OmniFold HGB (best, k=20)** | 0.524 | 0.136 | 0.663 | 0.812 |
| **AUSSIE (seed 1)** | 0.783 | 0.641 | 0.877 | 0.889 |
| **AUSSIE (seed 2)** | 0.834 | 0.754 | 0.901 | 0.907 |
| **AUSSIE (seed 3)** | 0.757 | 0.668 | 0.860 | 0.877 |
| **AUSSIE (mean ± sd)** | **0.791 ± 0.039** | **0.688 ± 0.059** | **0.879 ± 0.021** | **0.891 ± 0.015** |

*(Note: Baseline numbers taken directly from B1 `SCALAR_REFERENCES-20260922.md`.)*

### Signed Per-Bin Residuals

Residuals (Unfolded − Target, normalized) across the 7 `E_avail` bins. 
Injected signal: `[-.016, -.014, -.025, -.036, -.032, -.015, +.138]`

| Method | Bins `[0, .1, .2, .4, .8, 1.5, 3, 100]` GeV |
| :--- | :--- |
| IBU (k=3) | `+.006 +.005 +.010 +.017 +.020 +.016 -.073` |
| OmniFold HGB (k=3) | `+.012 +.010 +.018 +.030 +.031 +.018 -.119` |
| **AUSSIE (seed 1)** | `+.002 +.001 +.002 +.005 +.008 +.012 -.030` |

### Runtimes

*   **OmniFold (20 iterations)**: Generally dominates time due to sequential dependency.
*   **AUSSIE**: Highly efficient. Step 1 and Step 2 run exactly once. Recorded runtimes: 8.0s, 9.7s, 7.0s per complete run.

## 4. Verdict

**VERDICT: SUPPORTS advancing to AUSSIE evaluation with the PET backbone.**

**Evidence:**
1.  **Dramatically improved recovery:** AUSSIE surpasses not only OmniFold at matched iterations (0.791 vs 0.412) but also outperforms the best converged result of OmniFold (0.524) and Binned IBU (0.683).
2.  **Breakthrough in low-acceptance regions:** OmniFold and IBU struggle immensely in the low-acceptance region (recovery 0.136 and 0.040, respectively). AUSSIE elevates recovery in this problematic region to **~0.688**, proving that the limitation is fundamentally algorithmic (iteration/optimization bounds), not informational.
3.  **Tail bin correction:** The persistent structural undershoot in the highly displaced top `E_avail` bin (-0.119 for OmniFold, -0.073 for IBU) is reduced to just -0.030 by AUSSIE.
4.  **No sequential bottleneck:** AUSSIE is inherently parallelizable over epochs/batches and avoids the iterative degradation, eliminating the ambiguity in choosing a stopping threshold $k$.

The bounded scalar evidence strongly indicates that AUSSIE's single-pass direct objective extracts the necessary transfer function far more effectively than iterative expectation-maximization. Scaling this to the PET backbone is the recommended next step.
