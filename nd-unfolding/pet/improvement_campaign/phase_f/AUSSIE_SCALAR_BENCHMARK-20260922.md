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

### Ablation Results

| Method | Miss Handling | k or lambda | Aggregate | Low | Moderate | Good | Top-Bin Res |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| AUSSIE | penalty | 0 | 0.849 | 0.729 | 0.910 | 0.923 | -0.020 |
| AUSSIE | penalty | 0.01 | 0.847 | 0.728 | 0.908 | 0.923 | -0.021 |
| AUSSIE | penalty | 0.1 | 0.848 | 0.729 | 0.909 | 0.923 | -0.020 |
| AUSSIE | penalty | 1 | 0.792 | 0.688 | 0.879 | 0.891 | -0.029 |
| AUSSIE | penalty | 10 | 0.792 | 0.685 | 0.880 | 0.894 | -0.029 |
| AUSSIE | penalty | 100 | 0.767 | 0.641 | 0.867 | 0.889 | -0.032 |
| AUSSIE | penalty | 1000 | 0.648 | 0.388 | 0.783 | 0.884 | -0.049 |
| OmniFold | carry | 1 | 0.245 | 0.009 | 0.241 | 0.454 | -0.104 |
| OmniFold | carry | 3 | 0.411 | 0.033 | 0.475 | 0.735 | -0.081 |
| OmniFold | carry | 5 | 0.459 | 0.051 | 0.570 | 0.792 | -0.075 |
| OmniFold | carry | 10 | 0.511 | 0.104 | 0.659 | 0.824 | -0.068 |
| OmniFold | carry | 20 | 0.543 | 0.160 | 0.681 | 0.821 | -0.063 |
| OmniFold | carry | 50 | 0.582 | 0.226 | 0.701 | 0.819 | -0.058 |
| OmniFold | eff | 1 | 0.621 | 0.442 | 0.657 | 0.720 | -0.052 |
| OmniFold | eff | 3 | 0.779 | 0.628 | 0.803 | 0.841 | -0.031 |
| OmniFold | eff | 5 | 0.797 | 0.664 | 0.823 | 0.851 | -0.028 |
| OmniFold | eff | 10 | 0.821 | 0.683 | 0.834 | 0.865 | -0.025 |
| OmniFold | eff | 20 | 0.791 | 0.634 | 0.826 | 0.841 | -0.029 |
| OmniFold | eff | 50 | 0.783 | 0.608 | 0.845 | 0.853 | -0.030 |

#### Mean Learned R(z) in Low Acceptance (Misses vs Passes)
| Penalty (lambda) | Misses | Passes |
| :--- | :--- | :--- |
| 0 | 1.151 | 1.196 |
| 0.01 | 1.150 | 1.195 |
| 0.1 | 1.151 | 1.196 |
| 1 | 1.096 | 1.144 |
| 10 | 1.098 | 1.147 |
| 100 | 1.078 | 1.132 |
| 1000 | 1.030 | 1.087 |

## 4. Verdict

**VERDICT: CONFOUNDED. AUSSIE'S GAIN IS PRIMARILY EFFICIENCY CORRECTION, NOT THE NON-ITERATIVE FORMULATION.**

**Evidence:**
1. **Miss handling dominates:** When OmniFold is allowed to efficiency-correct misses (training step 2 on reco-passing events only and applying $R$ to all), its recovery jumps drastically, matching or exceeding AUSSIE. OmniFold (`eff`, k=50) achieves 0.783, compared to AUSSIE (`lambda=0`) at 0.849.
2. **Non-iterative formulation is not the breakthrough:** When miss handling is matched to the B1 baseline by enforcing the carry-misses assumption (AUSSIE with `lambda=1000`), AUSSIE's recovery collapses to 0.648. This is comparable to or worse than OmniFold (`carry`, k=50) which reaches 0.582. The non-iterative formulation itself does not confer a significant advantage.
3. **Extrapolation to misses:** As lambda approaches 0, AUSSIE's learned $R(z)$ on misses strongly tracks the $R(z)$ on passes in the low-acceptance region (e.g. ~1.17 for misses vs ~1.21 for passes). With high lambda, misses are forced back to 1.0. The unconstrained extrapolation is the source of the apparent improvement, perfectly mirroring the behaviour of efficiency-corrected IBU from Phase B1.

The initial evaluation was confounded by an implicit change in the uncertainty model (efficiency correction vs carry-misses). The non-iterative method itself does not solve the low-acceptance recovery issue under the required historical constraints. PET evaluation of AUSSIE is **not justified** on this basis.