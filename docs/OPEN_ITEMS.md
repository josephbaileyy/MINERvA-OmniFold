# Open items — the single live list

Everything not yet done, in one place. Consolidates and **supersedes**
`docs/PREPUB_READINESS.md` and `docs/FUTURE_DIRECTIONS.md` (now tombstones;
their full text is in git history, their DONE banners in the RUN_LOGs and
`VALIDATION_LEDGER.md`). Bugs/code debt live in `KNOWN_ISSUES.md` (repo root).

## Blocked on external input

1. **Ascencio bin-identical overlay** — machinery complete
   (`nd-unfolding/compare_ascencio_q3.py --ascencio-2d`); needs the
   arXiv:2110.13372 data release (HepData/member-gated).
2. **Collaborator confirmations** (technote App. A): FrInel_pi exclusion still
   current MAT guidance; precedent for the ours-only truncated-spectral χ²;
   precedent for publishing a 3D+ systematic covariance.

## Deferred analysis refinements

3. **PET per-lateral re-inference** — replace the frozen-cloud transferred
   lateral band by re-running PET inference on shifted reconstructed clouds
   per lateral universe. Design: drive the engine-agnostic UQ harness
   (`analyze_universes_nd.py`, `bootstrap_nd.py`, NTRIAL ensemble) through the
   PET engine; amortize with the read-once bank + train-once/reweight-cheap.
4. **W-resolved laterals / dedicated W systematic campaign** — the binary
   already dumps shifted-W lateral universes, so the bank exists; replaces the
   transferred 4D laterals in the (E_avail,W) covariance.
5. **True multi-band (lateral) event-loop unified throw** — the weight-composed
   unified throw covers reweight bands only; a C++ event-loop multi-band throw
   would additionally capture lateral (kinematic-shift) cross-terms.
6. **NEUT as fifth generator** — no accessible build at time of writing.
7. **Coverage 200-toy regeneration** — optional; numbers documented, toy ROOTs
   not on disk (`KNOWN_ISSUES.md` #2).
8. **Driver no-weights normalization fix** — `KNOWN_ISSUES.md` #1.

## Active campaign — full phase space (FPS)

9. **FPS campaign** (decision memo `nd-unfolding/FPS_PILOT.md`, GO with
   two-tier reporting): 12-playlist CV chain + MEFHC honesty battery +
   3-prior envelope in flight (jobs 54244119/54244120/54244178); UQ stage
   (`sbatch_evloop_array_5d_fps_universes_full.sh`, ~190 GB merged) gated on
   the MEFHC-scale anchor. In FPS the unified throw is **mandatory** (the
   migration-heavy corner that broke the 4D block sum ×2 is inside the
   measurement). New validation needed: hidden-variable closure + coverage in
   the extension regions.

## Methodology stance (for the eventual response-to-referees)

- Covariance is block-summed (C_syst+C_stat+C_ML); the unified-throw study
  tests the linearity assumption directly and, in 4D, found it broken
  (block-sum underestimates ~2×) — the published 4D systematic adopts the
  unified-throw magnitude.
- Central value: single-run CV; ensemble-mean CV agrees at 0.28%.
- ML band includes the train/test split, not just the estimator seed.
- GoF reported both binned (truncated-spectral χ²) and unbinned (C2ST).
