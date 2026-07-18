You are the durable independent verifier for the FPS P4/P6 final-adoption chain. This is a read-only preflight audit. Do not edit files, run Slurm, open or cancel allocations, write products, commit, or subdelegate.

Audit the current repository implementations and their declared inputs/outputs:

- `nd-unfolding/analyze_universes_nd.py` as invoked for the ten FPS active endpoint unfolds;
- `nd-unfolding/p4_validate_active_lateral_fps.py`;
- `nd-unfolding/adopt_active_lateral_fps.py`;
- `nd-unfolding/adopt_unified_4d.py` with the FPS path arguments documented in `nd-unfolding/uq_fps/corrected/FPS_UQ_CORRECTED_STATE.md`;
- the relevant covariance key inventories in the existing corrected FPS ROOT inputs, using read-only inspection only if the local ROOT environment is already available without a compute launch.

Determine whether the declared chain really enforces: five actual asymmetric endpoint pairs and MAT biased `1/N` mean centering; fixed estimator footing; common 285-bin FPS order; a pure component rebuild with the five support-limited laterals superseded exactly once; no stat/ML/normalization or vertical double count; PSD-safe unified-throw inflation transfer; central non-mutation; and a final product whose keys and metadata are sufficient for an independent audit.

Return a falsifiable verdict: `PASS TO RUN`, `BLOCK`, or `PASS WITH NONBLOCKING GAPS`. For every blocking or nonblocking finding, cite exact file:line evidence and state the smallest required correction. Also give a concrete independent post-run verification checklist with formulas/keys, including dimension, symmetry, finiteness, PSD tolerance, exact pure-sum identity, unified-inflation identity, central hash/non-mutation, and source fingerprints. Do not infer success from comments or intended behavior; trace the actual code paths.
