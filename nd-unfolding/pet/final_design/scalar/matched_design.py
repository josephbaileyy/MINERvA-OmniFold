"""DECLARED design of the scalar AUSSIE-vs-OmniFold matched comparison (committed before any
tuning or evaluation number was computed).

Tuning opportunity (identical for the two learned methods): a 4-point grid each, evaluated on the
F0 development selection only (pool F replicate 0, `dev` tilt), truth inputs `truth4`, both miss
rules separately, with 2 tuning seeds (11, 12) that are NOT evaluation seeds. Criterion: the mean
over the tuning seeds of the historical seven-bin E_avail recovery R against F0's pseudodata truth
-- OmniFold at the declared iteration count k = 3, AUSSIE (non-iterative) at its output. Ties go to
the first grid point (the predecessor's configuration). The winner per (method, miss rule) is
frozen in `frozen_config.json` and used, unchanged, for every case, both truth-input sets and all
evaluation seeds (1, 2, 3).

Matched pairs (same reco inputs, same truth inputs, same selections, same engine normalization):
  AUSSIE lambda = 0     <->  OmniFold efficiency-corrected
  AUSSIE lambda = 1000  <->  OmniFold carry-misses
OmniFold operating points: k = 3 (PRIMARY, declared; the reference candidate's iteration count),
k = 10 and k_F0 (the k in 1..10 maximizing the frozen configuration's mean R on F0; secondary).

Decision rule (PROTOCOL-20260925 section 5): AUSSIE advances to a PET-backbone evaluation only if
it beats matched scalar OmniFold on robustness OR stability, evaluated per matched pair on the
whole library (16 (selection, case) units x 3 seeds), truth4 inputs primary:
  robustness win  = (fewer moves-away (unit, seed) cells AND worst-case per-case mean R not lower)
                    OR (higher worst-case per-case mean R AND no more moves-away cells);
  stability win   = lower median (over units) across-seed SD of R AND lower max across-seed SD.
Per-case mean R = mean over the case's replicates (T0, T1 or F0, F1) and seeds; worst case = min
over the 8 cases. "Moves away" = residual L1 > injected L1 on the E_avail endpoint (R < 0).
Development evidence only; simulation only.
"""
from __future__ import annotations

TUNE_SELECTION = ("F0", "dev")
TUNE_SEEDS = (11, 12)
EVAL_SEEDS = (1, 2, 3)
TUNE_TRUTH_SET = "truth4"
TRUTH_SETS = ("truth4", "truth4_species")
PRIMARY_K = 3
OMNIFOLD_ITERATIONS = 10
IBU_ITERATIONS = 10

HGB_BASE = dict(learning_rate=0.1, max_iter=400, max_leaf_nodes=31, min_samples_leaf=200)
HGB_GRID = {
    "h1": dict(HGB_BASE),                                                    # predecessor
    "h2": dict(learning_rate=0.1, max_iter=400, max_leaf_nodes=63, min_samples_leaf=1000),
    "h3": dict(learning_rate=0.05, max_iter=800, max_leaf_nodes=31, min_samples_leaf=200),
    "h4": dict(learning_rate=0.05, max_iter=800, max_leaf_nodes=63, min_samples_leaf=1000),
}
AUSSIE_GRID = {
    "a1": dict(lr=1e-3, epochs=50),                                          # predecessor
    "a2": dict(lr=1e-3, epochs=20),
    "a3": dict(lr=3e-4, epochs=50),
    "a4": dict(lr=3e-4, epochs=20),
}
