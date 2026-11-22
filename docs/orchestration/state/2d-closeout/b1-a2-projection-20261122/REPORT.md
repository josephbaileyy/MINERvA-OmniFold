# b1 REPORT: IBUKT A2's mean residual pattern on Δ = E_R − published, in V_pub's modes (2026-11-22)

**By** the `cov2d` session, for the director. Results go to the director first, with no note wording.

**Run:** `b1_projection.py` at `a843ae65` (DECLARATION.md rev 2, sha256 `8b5835b9…`; code `b0cf7d0d…`; the director's OK on
2026-11-22 after a confirming agy read). The run was local on this Mac with ROOT 6.40.04, numpy 1.26.4, scipy 1.17.1 and one
BLAS thread. It used 0 node-h and no connect, and exited 0. Every number below is quoted from `run/readout.json`
(sha256 `614f53d2dae8f2cf2e648a679c3a18f5d7d9dc2dd9e09aa919b71c03b3e5786f`) or `run/readout.txt` (`5ba0a8fe…`).
The full printout is `run/run.log`.

**CITABLE FOR:** the controls and readings as measured, the labels the declaration's rules give them, and the sentences
§3 licenses for those labels, quoted below.

**NOT CITABLE FOR:**
- a cause of the 2D shape difference. "Origin undetermined" stands unless Joseph decides otherwise;
- that E_R or the published result is right;
- the bias at the data's true spectrum;
- coverage, an estimator choice, or any note or paper wording.

## 1. Controls: all 8 PASS

| control | measured | bar |
|---|---|---|
| C-OPS | E_R `a5c13fc3…`, published `6c6dce72…`, A2 readout `dfae50f5…` | exact |
| C-CELLS | 205 cells; StatOnly = Total; every A2 truth's `cells` equal | exact |
| C-PUB | χ² 465.4152699540014 against 465.4152721915331, rel 4.8e-9 | max(1e-8, 10 κ₂ ε) = 3.3e-3 (κ₂ 1.47e12) |
| C-SUM | rel 1.05e-7 | 3.3e-3 |
| C-K | k = 73; S₇₃/205 = 0.66185 | 73; 0.662 ± 0.0005 |
| C-M | all six M modes within 4 significant figures in λ/λ_max and ±0.005 in \|z_Δ\| | as declared |
| C-A2 | recomputed means and guards equal the readout's, worst 0.0 | 1e-15 |
| C-LIN | worst \|a − b\| is 1.5e-5 of its bar | 1e-12 + 1e-10·\|a\| |

**N-PREC.** No M mode and no g is numerically unresolved:
- the largest per-mode driver difference on Δ is 6.5e-4 relative, over all 205 modes;
- on z_β in M at the primary truths, the largest is 2.6e-6 relative;
- across every truth, method and set, the largest |g_numpy − g_evr| is 6.6e-7.

## 2. Readings (OmniFold, β = A2 mean fractional residual ⊙ E_R; f ± h, h = A2's 5-draw guard)

### R1, primary: K₇₃, the 73 best-determined directions of the published covariance

| truth | g ± h | label |
|---|---|---|
| nominal | +0.0004 ± 0.0150 | minor |
| genie_mec | +0.1611 ± 0.0446 | unresolved across minor, partial |
| nuwro | +0.1062 ± 0.0640 | minor |

**Combined (§3): "unresolved at genie_mec."** The resolved truths, nominal and nuwro, both read minor. Their licensed sentence
(§3, minor):
> "At truth ⟨nominal / nuwro⟩, the E_R estimator's A2 mean residual pattern supplies at most a fifth of Δ's component in the 73
> best-determined directions of the published covariance, either way. This weakens this bias pattern as a main contributor in
> these directions."

At genie_mec:
> "At truth genie_mec, the five draws do not resolve the share in the 73 best-determined directions of the published covariance
> among minor, partial."

### R2: K̄, the 132 poorly determined directions of the published covariance

| truth | g ± h | label |
|---|---|---|
| nominal | +0.0049 ± 0.0226 | minor |
| genie_mec | +0.1453 ± 0.0137 | minor |
| nuwro | +0.2967 ± 0.0203 | partial |

**Combined (§3): "truth-dependent."** All three truths are resolved and their labels differ, so no summary sentence is drawn.
Per truth:
- nominal, genie_mec (minor): "…supplies at most a fifth of Δ's component in the 132 poorly determined directions of the
  published covariance, either way. This weakens this bias pattern as a main contributor in these directions."
- nuwro (partial): "…supplies between a fifth and a half of Δ's component in the 132 poorly determined directions of the
  published covariance: a partial contributor at most."

The declaration's disclosure that R2 might read unresolved did not apply: every primary truth resolved in K̄.

### R3: Δ's six largest contributors, per mode (ρ ± h, label)

| truth | 23 | 9 | 118 | 2 | 79 | 121 |
|---|---|---|---|---|---|---|
| nominal | +0.019 ± 0.072 minor | +0.037 ± 0.092 minor | −0.007 ± 0.125 minor | −0.011 ± 0.041 minor | −0.001 ± 0.010 minor | +0.041 ± 0.102 minor |
| genie_mec | −0.066 ± 0.081 minor | +0.106 ± 0.083 minor | +0.411 ± 0.115 unresolved across partial, candidate | +0.151 ± 0.093 unresolved across minor, partial | +0.562 ± 0.065 unresolved across partial, candidate | +0.299 ± 0.151 unresolved across minor, partial |
| nuwro | −0.329 ± 0.039 opposite | +0.284 ± 0.064 partial | +0.018 ± 0.079 minor | −0.158 ± 0.047 unresolved across opposite, minor | +0.129 ± 0.060 minor | +0.681 ± 0.149 candidate |

Each label's sentence is §3's per-mode sentence. For example, nuwro mode 121 (candidate): "In mode 121, the pattern supplies
between half and one and a half times Δ's component." Nuwro mode 23 (opposite): "In mode 23, the pattern points against Δ's
component." Every sentence is in `readout.json` → `readings.R3`. They describe the share in a single mode only.

### Secondary truths (labelled, not in the combined statement)

| truth | R1 (K₇₃) | R2 (K̄) |
|---|---|---|
| bump | −0.0008 ± 0.0382 minor | −0.0590 ± 0.0255 minor |
| tilt | −0.0182 ± 0.0545 minor | +0.0042 ± 0.0278 minor |
| within_plus | +0.0392 ± 0.0382 minor | +0.1765 ± 0.0267 unresolved across minor, partial |
| within_minus | −0.0137 ± 0.0147 minor | −0.1802 ± 0.0352 unresolved across opposite, minor |

Their R3 labels are in `readout.txt`.

## 3. Printed, read by nothing

These are in `readout.txt` under "printed, read by nothing". They are listed for the director's reading of the record and carry
no label:
- **The cosine** in whitened coordinates, OmniFold at the primary truths: K₇₃ +0.004, +0.171, +0.113; K̄ +0.101, +0.143,
  +0.170 (nominal, genie_mec, nuwro).
- **q = S(β)/S(Δ)**, raw, OmniFold: K₇₃ 0.0072, 0.886, 0.893; K̄ 0.0023, 1.03, 3.05.
- **The unit-amplitude remainder S(Δ − β)/S(Δ)**, OmniFold: K₇₃ 1.006, 1.564, 1.680; K̄ 0.993, 1.741, 3.455.
- **The e ⊙ p sensitivity:** g moves by at most 0.0075 (within_plus, OmniFold, K₇₃) from the e ⊙ E_R values, over every truth, method and set.
- **IBU K=5 and K=10 and K₂₀₅:** all printed in `readout.txt`.

## 4. Limits carried to the result (declaration §5)

- Δ is treated as fixed; E_R's own noise is not propagated.
- A2's bias comes from 5 Poisson draws on one simulated bank with the nominal response. The bank's finite-simulation and
  learner-seed effects are not sampled.
- The truths are development stresses (IBUKT-DECLARATION §4), not the data's truth.
- A minor reading weakens only this pattern, at these truths, in these directions. A partial or candidate reading names a
  contributor at most. Neither is a cause.
