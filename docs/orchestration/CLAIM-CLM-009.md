# CLM-009 claim detail

## Original claim cell

Sieve reduction (user conjecture, v2 after prior-art correction): for bins with D̄≥B̄, negweight OmniFold step-1 restricted to per-reco-bin-constant classifiers yields r(b)=(D̄−B̄)/S̄ — bin-identical to the purity method; composed with binned-OmniFold=IBU it equals subtract-then-IBU. The max(0,·) floor does NOT emerge from raw signed BCE (objective unbounded below for D̄<B̄; no minimizer) — it is a prescription (clip/regularization/positivized loss); the same unboundedness is the root of unbinned negweight instability (→ Stay-Positive).

## Status history

VERIFIED-NUMERIC (sieve toy V6 all-PASS: closed-form 2e-14; LightGBM 0.38%; purity==negweight 0.38% in positive bins; negative bins driven to ~0 under regularization while signed loss decreases unboundedly; unbinned-vs-sieve within-bin RMSE 18.8x better; note: signed Hessians destabilize naive LightGBM tree growth)

## Evidence artifact

note App. B.2 (commit 89ecc79, Overleaf c02ec6e) + orchestration_runs/negweight_reduction/{NEGWEIGHT_PURITY_REDUCTION.md,codex_priorart.out,toy/}

## Data/config hash

—

## Commit

—

## Slurm job(s)

—

## Independent verifier

codex-school V5 (12 sources, citation-verified); orchestrator hand-check of the W1<0 divergence

## Residual history

novelty: only the explicit binwise corollary + purity identification; MUST cite arXiv:2105.04448 (closest prior art), also 2409.08183, 2505.03724 §III.E; v1 floor claim was the orchestrator's own overclaim, caught by the verification layer
