# Open items — the single live list

Everything not yet done, in one place. Consolidates and **supersedes**
`docs/PREPUB_READINESS.md` and `docs/FUTURE_DIRECTIONS.md` (now tombstones;
their full text is in git history, their DONE banners in the RUN_LOGs and
`VALIDATION_LEDGER.md`). Bugs/code debt live in `KNOWN_ISSUES.md` (repo root).

## Blocked on external input

1. **Collaborator confirmations** (technote App. A): FrInel_pi exclusion still
   current MAT guidance; precedent for the ours-only truncated-spectral χ²;
   precedent for publishing a 3D+ systematic covariance. **Ready-to-send
   draft: `docs/COLLABORATOR_QUESTIONS.md` (2026-06-12)** — needs only the
   user to send it.

## Deferred analysis refinements

2. **Ascencio fine-binned comparison** — the maximal-common-grid full-cov
   cross-check is DONE 2026-06-10 (χ²/ndf = 1.68/2, p = 0.43, consistent;
   `nd-unfolding/compare_ascencio_fullcov.py`, data from the public arXiv
   tarball). Stage 1 DONE 2026-06-12 (job 54351853 +
   `compare_ascencio_fine.py`): all 44 cells, ours/theirs median 1.077,
   5/44 cells beyond 2σ of their errors — agreement at the super-grid level;
   numbers in the ledger. Stage 2 (187-universe sweep on the fine binning,
   needed before any fine-grid full-cov χ² can be quoted) is a separate
   compute decision once the FPS arrays drain.
3. **PET per-lateral re-inference** — DONE 2026-06-10 (job 54284039):
   PET-native lateral band via the event-aligned 5D join, no C++ re-dump,
   no GPU. Native median 1.74% vs transferred 4.03% (total budget 22.5% vs
   23.0%) — the published GBDT transfer validated as the conservative side;
   `KNOWN_ISSUES.md` #3 RESOLVED. Residual (deferred indefinitely): full
   per-universe PET re-TRAINING would capture the retraining response the
   frozen-push scheme misses; bounded between 1.74% and 4.03% by these two
   estimates.
4. **W-resolved laterals / dedicated W systematic campaign** — DONE
   2026-06-13 (interactive job 54391533). The 18 detector universes (6
   muon/beam laterals with shifted pt/pz/q3/W + 3 GEANT weight bands) +
   matched CV were re-inferred on the 5D axes and `eavailW_covariance.py
   --lateral-sweep-*` rebuilt the (E_avail,W) covariance with the W-resolved
   block. The W-resolved lateral (median 2.36%/bin) is LARGER than the
   transferred approximation (1.80%) and was adopted; corner significances
   GENIE 9.0→8.9, +MEC 9.2→9.2, NuWro 10.5→15.6, GiBUU 18.2→22.4σ — the
   deficit deepens for the worst-fitting generators. `KNOWN_ISSUES.md` #4
   CLOSED; technote table + exec summary + open-questions updated;
   `products/5d/eavailW_covariance_wlat.root`.
5. **True multi-band (lateral) event-loop unified throw** — the weight-composed
   unified throw covers reweight bands only; a C++ event-loop multi-band throw
   would additionally capture lateral (kinematic-shift) cross-terms.
6. **NEUT as fifth generator** — still gated (re-checked 2026-06-12: no
   public source release exists; github `neut-devel/neut` is 404 — NEUT is
   distributed via T2K's internal git on request to the maintainers, so the
   path is an access request to Hayato et al., citing the NEUT EPJ ST paper
   2106.15809).
7. **Coverage 200-toy regeneration** — DONE 2026-06-11 (arrays
   54273493/54273495): `uq/coverage_toys.py` reproduces every documented
   number exactly (mean 68.71%, PASS); `KNOWN_ISSUES.md` #2 RESOLVED,
   ledger flag lifted.
8. **Driver no-weights normalization fix** — DONE 2026-06-10. Fix applied
   and verified (job 54271042: battery + envelope reproduce without the
   1/pot_scale correction); `KNOWN_ISSUES.md` #1 RESOLVED, ledger entry
   added.
9. **LE-beam evolution comparisons** — DONE 2026-06-11 (qualitative, shapes
   only): `nd-unfolding/compare_le_evolution.py` overlays Filkins 2002.12496
   (CC-incl dσ/dpT, dσ/dp∥; data from the arXiv tarball, now in
   `nd-unfolding/reference_le/`) and Rodrigues 1511.05944 ((E_avail,q3)
   Tables III+IV rebinned onto our coarse grid — edges nest exactly; strict
   LE-coverage masking) against the ME 4D-product marginals →
   `products/4d/le_evolution_compare.png`; numbers in the ledger. Residual
   (unchanged): a quantitative LE↔ME translation needs per-event true Eν
   dumped (one event-loop branch, piggyback on a future re-run) and is
   prior-dependent.

## Active campaign — full phase space (FPS)

10. **FPS UQ stage** (decision memo `nd-unfolding/FPS_PILOT.md`, GO with
    two-tier reporting; CV chain + MEFHC battery + 3-prior envelope DONE
    2026-06-10, anchor gate PASS). **Everything staged/in flight
    2026-06-11** (job IDs in `nd-unfolding/.fps_uq_chain_jobs.txt`,
    narrative in the RUN_LOG): 187-universe sweep → block-sum cov;
    bootstrap + split-seedscan → combines → full budget → unified-throw
    adoption (block-sum vs unified-throw decision, as in 4D); **mandatory**
    unified throw via the validated 2D FPS bank (#12 miss-row pinning);
    extension-region validation launched (hidden-variable E_avail closure +
    200 coverage toys, region split via
    `nd-unfolding/fps_extension_validation.py`). Remaining: report verdicts
    when the chain drains.

## Methodology stance (for the eventual response-to-referees)

- Covariance is block-summed (C_syst+C_stat+C_ML); the unified-throw study
  tests the linearity assumption directly and, in 4D, found it broken
  (block-sum underestimates ~2×) — the published 4D systematic adopts the
  unified-throw magnitude.
- Central value: single-run CV; ensemble-mean CV agrees at 0.28%.
- ML band includes the train/test split, not just the estimator seed.
- GoF reported both binned (truncated-spectral χ²) and unbinned (C2ST).
