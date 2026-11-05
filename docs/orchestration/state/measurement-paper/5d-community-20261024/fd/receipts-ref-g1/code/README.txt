REF-G1 code receipt (REF-G1-BINDING-1.md ruling 2: the code lane writes nd-unfolding/ref_g1/ with its tests, the
mutation harness with every mutant §7 lists plus the expected survivors, and a receipt). limitations-catalog,
2026-11-05, on a detached worktree of origin/main e46551d66 (#775). Nothing ran on the cluster; no analysis input
was read.

binding-delta.txt  the receipt-binding inventory delta the config adds (158 -> 161), enumerated and power-tested.
files.sha256    sha256 of the five files the runs below used, taken before and after both runs (identical).
tests.txt       python3 -B nd-unfolding/ref_g1/test_ref_g1.py -v   ->  Ran 30 tests, OK, exit 0.
harness.txt     python3 -B nd-unfolding/ref_g1/ref_g1_mutation.py  ->  MUTATION CHECK :: PASS (26 mutations,
                2 expected survivors), exit 0. The two equivalent mutants each ran once against the whole suite and
                survived; their proofs are in ref_g1_mutation.py beside EXPECTED_SURVIVORS.

Environment: Python 3.14.6, numpy 2.4.4, scipy 1.18.1 (a scratch venv on the system interpreter with scipy added),
macOS 26.6.2 arm64; PYTHONDONTWRITEBYTECODE=1 and -B, and no __pycache__ was left under nd-unfolding/ref_g1/.

Revision 2 (the code audit, #781; the director's rulings of 2026-11-05):
- C1: a failed control (G-draw, G-pair, G-CV, G-IBU1, G-cells) stops the read: STOP.json names it, no Delta is formed,
  no reading is written, exit 1.
- C2: the read refuses bars whose recorded reader or config digest is not the running one.
- C3: each unit's done-marker carries its control verdict; only a PASS unit is skipped on a rerun, any other is
  refused (rc 6).
- null_t's weighted estimator is one function, tested equal to s1_assemble.mat_cov draw by draw.
- gibu1 runs only in IBU-1's recorded environment (interpreter and Python version from IBU-1's guard inventory,
  D_N.jsonl:1 @ ddbc43e42); IBU-1 recorded no numpy or scipy version, which the unit records and does not require.
Each change has a test and a mutant.

Recorded for step two (REF-G1-BINDING-1.md; the director's rulings of 2026-11-05):
- The rc-5 membership refusal is a defensive guard that real data cannot reach: edge-safe jitter leaves
  float32(edge) in place and every other float32 value lies at least 1/2 ulp from the edge. Its test substitutes the
  jitter to move one row across an edge and counts the substitution's calls, so a substitution that never ran fails.
- G-draw compares exactly the declaration's list (keep masks, obs_counts, MC Poisson factors, tmpl_w).
- One driver test (Units.test_a_detector_universe_through_the_bank_parsers) sets s5p_universe.SENTINEL_ROWS to the
  synthetic fixture's sentinel count; the production value 2,801 is untouched in every other test.
- The pins config.json carries beyond #775's listing (tune_v1.json 13bb1eae..., s1_assembly.npz db000707...,
  the flux-universe ROOT file 5eecae84..., the flux constraint e38ad7d2...) are the cluster lane's follow-up listing.
