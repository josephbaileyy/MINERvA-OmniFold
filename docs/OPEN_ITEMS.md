# Open items — the single live list

Everything not yet done, in one place. Consolidates and **supersedes**
`docs/PREPUB_READINESS.md` and `docs/FUTURE_DIRECTIONS.md` (now tombstones;
their full text is in git history, their DONE banners in the RUN_LOGs and
`VALIDATION_LEDGER.md`). Bugs/code debt live in `KNOWN_ISSUES.md` (repo root).

Execution references (instructions, not run receipts):
[the dependency/rerun map](RESULT_DEPENDENCY_AND_RERUN_MAP.md) defines
invalidation frontiers, [the publication runbook](PUBLICATION_COMPLETION_RUNBOOK.md)
assigns the remaining packets, and
[the post-publication reorganization plan](POST_PUBLICATION_REORG_PLAN.md) gates
cleanup behind the publication-results freeze tag.

## Active remediation gate (5D GBDT closed; PET full-event gate reopened)

**Presentation deadline: 2026-07-16.** Central values, closure tests,
dimensional anchors, and the finalized 2D reproduction remain current. Old
4D/FPS unified/adopted covariances, `(E_avail,W)` covariance-dependent
generator significances, and their historical products remain unquotable. The
corrected 5D GBDT covariance is the ledger-verified replacement. The completed
PET campaign is retained as a recoil-only representation cross-check and does
not close the literal full-event PET gate below.

- Regenerate 4D/FPS joint throws with asymmetric $\pm1\sigma$ endpoint
  interpolation, one fixed estimator seed, throw-mean centering, and a separate
  mean-shift diagnostic; rebuild the matched MAT $1/N$ block comparator from
  actual minus/plus re-unfolds. Do not reuse the old jitter-subtracted adopted
  covariances.
- **PET before publication:** do not promote or extend the current recoil-only
  covariance as though it belonged to a full-event estimator. Preserve its
  completed products and replicas as cross-checks. A new nominal and UQ campaign
  begins only after the full-event representation and stress-closure gate below
  pass.
- Rerun the five-axis statistical replicas and project the full covariance as
  $M C_{5D}M^\top$ before rebuilding $(E_{\rm avail},W)$ significances.
- Quantify lateral support migration with selection-complete
  `MNV101_ACTIVE_UNIVERSE=BAND:IDX` per playlist. Five bands are genuinely
  kinematic (`BeamAngleX/Y`, `MuonResolution`, `Muon_Energy_MINERvA/MINOS`);
  MinosEfficiency and GEANT are weight-only. The unrun three-band presentation
  bound is retired with the completed talk workstream; full five-band coverage
  remains the publication gate.
- The 12-playlist background-aware dump, 169 vertical unfolds, 18 detector
  unfolds, and matched CV are complete; KNOWN_ISSUES #13 is closed with a
  sub-0.3% effect. Keep production banked sweeps fail-closed when per-universe
  background columns are missing.

### PET full-event + FPS measurement-domain gate (KNOWN_ISSUES #19)

The present PET step-1/step-2 classifiers see only the reconstructed recoil
cloud and truth-hadron cloud. Muon/scalar arrays are phase-space and extraction
metadata, not classifier features. Binning a recoil-derived event weight in
muon coordinates does not unfold the full joint distribution: at fixed recoil,
the conditional muon distribution remains the generator prior. Therefore use
**full-event** for the input representation and **extended phase space** for the
relaxed acceptance; do not use “full phase space” as a synonym for a recoil
point cloud. The publication deliverable requires both changes. A full-event
classifier trained on the standard restricted phase space does not close this
item.

Mandatory measurement-domain contract:

- source only FPS CV event loops produced with
  `MNV101_FULL_PHASE_SPACE=1`, which remove the four truth muon kinematic cuts
  while retaining the tracker fiducial definition and unchanged reconstructed
  selection;
- preserve the FPS truth denominator, newly admitted native misses, signal,
  background, data, and event alignment through every cloud dump, scalar/W
  source, train, extraction, systematic endpoint, projection, and closure;
- pass `--full-phase-space` wherever code reconstructs the truth gate. A path
  that consumes finalized inputs without that option must instead verify
  embedded FPS provenance and reject incompatible metadata;
- use the canonical extended FPS `(p_T,p_parallel)` edges, including the low-
  and high-`p_parallel` and high-`p_T` catch bins. Record and compare the exact
  arrays and reported-bin ordering; fail closed on the standard paper grid;
- use P3F products under `active_universe_5d/fps/` for selection-complete
  laterals. P3S products under `active_universe_5d/standard/` are regression
  controls only and cannot be relabeled or reused as FPS endpoints;
- report acceptance-supported and prior-dominated extrapolation regions
  separately, and repeat the FPS anchor, extension closure, coverage, and
  prior-swap/envelope controls for the new estimator.

Artifact guard: `of_inputs_pc_fps.npz` applies the standard truth gate, and
`of_inputs_pc_fps_xps.npz` lifts the angular cut but retains the standard
`p_T/p_parallel` bounds. Neither is an FPS publication input. The `xps2`
gate-and-edge convention is the semantic starting point, but its current
recoil-only tensors are not the final full-event representation.

Define three explicit event-feature schemas rather than manufacturing
counterparts that do not exist:

- `event_reco` and `event_data` use the same observable schema: a distinguished
  reconstructed muon with full direction and momentum
  (`p_x,p_y,p_z` or `p_T,p_parallel,phi`), energy and charge/type, plus MINOS
  range/curvature and match-quality context only where its identical data/MC
  definition is validated;
- `event_truth` uses a distinct truth schema with the truth-muon four-vector and
  truth event quantities. Never create truth MINOS/range/match counterparts or
  fill detector-only features with sentinels;
- the recoil set with energy and unambiguous geometry: view ID plus position and
  `z`, preferably coordinates relative to the interaction vertex, with timing
  and cluster/prong/type information when available;
- truth-particle four-vectors plus a categorical PDG/type encoding (the PDG is
  already dumped but the current loader discards it);
- reconstructed vertex quantities may enter `event_reco/event_data`; truth
  vertices may enter `event_truth`. A step-1 MC or data classifier must never
  receive the MC truth vertex. Include explicit summaries for information
  outside the retained cloud, including constituent count,
  discarded/unclustered energy and detector-region energy totals, or use a
  validated variable-length scheme that removes the fixed top-12 loss;
- masks/type embeddings that distinguish muon, recoil constituents, padding,
  detector views, and any residual-summary token.

Do not feed generator interaction mode, generator-only process labels, or other
unobservable truth labels into the publication classifier. Incoming-neutrino
energy and similar truth-only latents require a separate prior-dependence case;
they are not part of the default full-event claim. Run/playlist may be used only
as validated detector-period conditioning, never as an unchecked data/MC label
shortcut.

Implementation gate, in order:

1. Prove the source ROOT has the FPS configuration and reproduce the committed,
   matched-CV FPS-versus-standard denominator/miss census within its declared
   tolerance. Verify the extended edges/order, unchanged reco selection, and
   event alignment before training.
2. Repair and test independently paired `(point_cloud, event_features)` inputs
   for `event_reco`, `event_data`, and `event_truth` through PET, DataLoader,
   both `MultiFold.cache()` steps, reweight-all inference, bootstrap
   persistence, and extraction. Permit different step-1/step-2 feature counts
   and normalization contracts. The current `num_evt` branch is not functional
   end-to-end, and fixing `net.py` alone is insufficient.
3. Define the neighborhood metric explicitly. The vendored local PET assumes
   its first two token coordinates are an angular/geometric pair, while the
   current tensors begin with energy and one position/momentum component. Use
   validated view-aware detector geometry at reco and direction/angle geometry
   at truth, rather than letting raw column order define nearest neighbors.
4. Prove row alignment and reco/data schema parity; document every input, mask,
   normalization, truncation, and unavailable counterpart. Add an explicit
   leakage test proving that step 1 contains no truth-only feature.
5. Add an omitted-variable stress closure that changes muon kinematics at fixed
   recoil. It must expose the recoil-only estimator and close with the full-event
   estimator. Also retain ordinary closure, central normalization,
   lower-dimensional marginal gates, and full-event-versus-recoil comparisons
   in the FPS extension and dead-cell tiers. Passing this stress closure alone
   does not satisfy the FPS controls.
6. Freeze the full-event FPS feature and measurement contracts before
   production, then rerun the PET nominal, GPU floor, coherent statistical
   ensemble, PET-specific ML ensemble, vertical/retraining response,
   P3F-based selection-complete laterals, covariance assembly, projections and
   comparisons. Recompute the FPS prior envelope: additional features may
   change extrapolation behavior but cannot create detector information in
   zero-efficiency cells. No current recoil-PET covariance component is
   automatically transferable to the new estimator.

### Potential next step after the full-event FPS gate: broaden reconstructed acceptance

Do not enlarge the truth denominator beyond the declared FPS fiducial domain
merely because a more expressive estimator is available. After P5A/P5B, use
the response/efficiency map, prior envelope, stress and ordinary closure, and
coverage results to define the strongest data-supported reporting boundary.
Promote stable cells to the primary acceptance-supported measurement and keep
near-zero-efficiency cells in a separately labeled, model-dependent
extrapolation tier.

If important regions remain unconstrained, study a genuinely broader
**reconstructed** selection rather than another truth-only expansion. Candidate
categories include MINERvA-contained or otherwise non-MINOS-matched muons and
additional angular/low-momentum acceptance. Such a campaign requires its own
reconstruction categories, charge-sign/background treatment, efficiency and
migration model, detector systematics, closure/coverage tests, and publication
decision gate. Retain a tracker interaction fiducial volume so the target
nucleon normalization and cross-section definition remain reproducible. The
objective is maximum observed information and supported phase space, not the
largest nominal truth-space volume.

## Blocked on external input

1. **Collaborator confirmations** (technote App. A): whether the historical
   FrInel_pi exclusion is still endorsed; precedent for the ours-only
   truncated-spectral χ²; collaboration endorsement for publishing the
   first MINERvA 3D+ unfolded covariance and its rank-deficient GoF treatment
   (there is no prior MINERvA 3D+ unfolding precedent). The historical code
   fact is sourced: public MAT-MINERvA
   `GenieSystematics.cxx` comments out the knob in both standard-registry
   builders ([vector lines 36–38](https://github.com/MinervaExpt/MAT-MINERvA/blob/c20ad220e95f55b4ef2e9426c56dd2a3800f7533/universes/GenieSystematics.cxx#L36-L38);
   [map lines 90–92](https://github.com/MinervaExpt/MAT-MINERvA/blob/c20ad220e95f55b4ef2e9426c56dd2a3800f7533/universes/GenieSystematics.cxx#L90-L92)),
   unchanged since the 2021-07-07 initial public
   [commit](https://github.com/MinervaExpt/MAT-MINERvA/commit/69e841ef53e336090dee7db25b70b8562bae76dc).
   **Ready-to-send draft: `docs/COLLABORATOR_QUESTIONS.md` (2026-06-12)** —
   needs only the user to send it.

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

## Active campaign — PET capstone (kickoff 2026-06-19)

11. **5D unified-throw adoption decision** — DONE 2026-07-01/02. The 5D
    GBDT jitter-matched unified-throw study (dump 55286192, block/run
    55286273/55286275, combine 55286276, all COMPLETED) gave a
    jitter-corrected trace ratio **1.539** (far milder than 4D's 2.01, near
    FPS's 1.295), with a non-uniform per-bin picture (median per-bin sigma
    ratio 0.830, inflation concentrated in a minority of high-variance
    bins). Adopted (same conservative per-bin max() transfer as 4D/FPS):
    `nd-unfolding/uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined_uthrow.root`,
    adopted median 13.69%/bin (up from block-sum 13.33-13.43%). Scripts
    `unified_throw_cov_5d.py` / `adopt_unified_5d.py` (both untracked,
    pending commit).
12. **PET FPS capstone remaining steps** — Step 2 of the PET capstone
    (raw-data FPS unfold beyond the published phase space). Cloud-fixed
    FPS point-cloud re-dump chain (evloop 55288326, hadd 55288356, npz
    55288408) is DONE 2026-06-29/30. **Full-stats PET FPS train (job
    55288409, horovod, train=40,000,000, ranks=4, niter=5, epochs=8) is
    RUNNING** (started 2026-07-01 after a ~2-day queue wait). Remaining,
    in order: (a) train drains; (b) mandatory 3-prior envelope — MnvTune
    and bare-GENIE priors exist from the 2D/5D pilots, the 5D NuWro leg
    (`build_fps_prior_nuwro_5d.py`) is drafted but has not been run; (c)
    Tier-2 retraining-response analysis at 8-10M events (the full-stats
    29 A100-hr/train cost was previously judged too expensive to repeat
    per-universe, so this is a convergence-curve check, not a full
    per-universe retrain); (d) per-event-weight covariance so any
    observable inherits the band.
13. **Understand the PET 5D unified/block ratio (5.711)** — PET's own
    unified-throw check (frozen 2M-train reweighter,
    `pet_5d_covariance_combined_unified_wlat_summary.json`) gives a
    trace-ratio inflation of **5.711x**, much larger than the GBDT-side 5D
    ratio (1.539, item 11) or the qualitative 4D picture. Flagged, NOT
    adopted into any published PET uncertainty. A same-day comparison using
    this un-vetted ratio anyway
    (`products/pet/unified5d/pet_vs_gbdt_uncertainty_5d_summary.json`,
    PET 16.7% vs GBDT 13.7%, ratio 1.346) should be treated as exploratory
    until this is understood — is it a frozen-reweighter artifact, a
    genuinely larger PET nonlinearity, or a bank/binning mismatch?
14. **Note-update items (pending)** — none of the following are yet
    reflected in the analysis note: the full-stats PET numbers (once
    item 12 drains); the 5D GBDT uncertainty statement (now
    Models/2p2h-dominant rather than Flux-dominant, and the unified-throw-
    adopted 13.69%/bin rather than the block-sum 13.43%/bin, per item 11);
    the PET 5D verdict (WORSE vs GBDT, indicative/2M-train-anchored, per
    item 13's caveat).

## Methodology stance (for the eventual response-to-referees)

- Covariance is block-summed (C_syst+C_stat+C_ML); the unified-throw study
  tests the linearity assumption directly and, in 4D, found it broken
  (block-sum underestimates ~2×) — the published 4D systematic adopts the
  unified-throw magnitude.
- Central value: single-run CV; ensemble-mean CV agrees at 0.28%.
- The corrected 4D/5D ML band isolates train/test-split response at fixed
  estimator seed 42. Pure estimator-seed sensitivity is not added separately;
  disclose this deliberate scope with any replacement budget.
- GoF reported both binned (truncated-spectral χ²) and unbinned (C2ST).
