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

> **Starting a fresh session? Read the latest handoff first:**
> [`orchestration/HANDOFF-20260806-2246Z.md`](orchestration/HANDOFF-20260806-2246Z.md) — jobs in
> flight, what was settled 2026-08-06 (D2 powered closure FAILED; `niter` stays at 3; J28 re-roll
> exact but 122/160), the decisions that are Joseph's, and what to do first.
> **Handoffs must be indexed here.** The previous one
> (`nd-unfolding/pet/HANDOFF-20260805-2300Z.md`) was referenced by nothing in the repo, which is the
> same orphaning failure that left nine findings unread until 2026-08-06. Add a line, replace the one
> above, and keep only the current handoff linked.

## Active remediation gate (5D GBDT closed; PET full-event gate reopened)

**Presentation deadline 2026-07-16 --- PASSED; the talk workstream is closed.** This section is now framed by the 2026-08-03 Perlmutter restore, not the talk. Central values, closure tests,
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
   and normalization contracts. **Updated 2026-08-01:** the `num_evt` branch is
   no longer the blocker — `dfef335` landed the 13-feature reco schema with
   `n_evt_reco`/`n_evt_truth` carried separately, so the two legs may now differ
   in width, and `pet/extract_fullevent_fps.py` supplies the missing
   reweight-all + extraction path. **Decision recorded 2026-08-04:** Step 1 uses
   `w_reco`, Step 2/truth yields use `w_truth`; the nominal must consume the
   hash-bound precomputed Gate-2 target; and closure gets an MC-only TF path.
   Implement the dual-leg loader/engine boundary, mandatory target consumer,
   row/hash/provenance gates, and MC-only construction as one receipt-bound
   patch set, then re-issue Gate 2 and Gate 4. Canonical requirements:
   `docs/orchestration/DECISION-20260804-B4-STEP3-RECEIPTS.md`.
   **STATUS 2026-08-05: D1/D2/D3 implemented; GATE 2 RE-ISSUED AND PASSED** (job
   56344268). What remains, in order:
   (a) **run the D2 powered recovery closure** --- `pet/closure_powered_truth_reweight.py`
       exists and its Gate-4 component re-derives every metric from the dump. The 08-04 GPU
       smoke (job 56347531) exercised the whole path and **returned FAIL, exit 3** --- not a
       crash: it ran the complete protocol and wrote a verdict. That FAIL was an artifact of
       the smoke's 20,000-row half-size, and it is now PROVABLE rather than inferred: the
       submission-side gate scores `floor/gap = 0.4040` at 20k (acceptance budget 0.50x the
       sampling floor --- unpassable however well the estimator performed) against
       `floor/gap = 0.0459` at the predeclared 2M. The smoke's report and artifact were
       deleted, which is why this had to be reconstructed; `--json` is mandatory on the gate
       now so a FAIL can never again leave no evidence.
       The predeclared run (clipped-exponential truth-pT tilt at amplitude 0.35, clip
       |z|<=3, disjoint deterministic 2M/2M at split seed 7, nominal policy incl. batch 512,
       accept at gap>=0.15, floor/gap<=0.10, residual/gap<=0.20) has NOT completed. Sized at
       12.84 GiB peak host memory. The two training-independent criteria are already measured
       and pass with margin (gap 0.2343 = 1.56x, floor/gap 0.0459 = 2.2x), so the only open
       number is `residual <= 0.0469` (recovery >= 0.80). Until it passes, `powered_closure`
       is red BY DESIGN and Gate-4 cannot PASS.
       **Job 56355818 was CANCELLED 2026-08-06 at 00:57Z, 5:18 into its 12 h run**, on the
       user's instruction and for a mechanical reason: it was executing `niter=2`, and the
       seed policy moved to `niter=3` in the same window. Its report would have recorded
       `niter: 2` and been rejected by `powered:nominal_configuration`
       (`validate_pet_nominal_gate4.py:790-795`) and `freeze:seed_policy` (`:937`). **It must
       be RE-RUN at niter=3**, which is now the only thing standing between Gate-4 and a
       runtime verdict. Cancelling cost ~5 min of GPU because it was caught minutes after
       dispatch rather than hours; see
       [`FINDING-20260806-campaign-pin-inverted-on-insignificant-variance.md`](orchestration/FINDING-20260806-campaign-pin-inverted-on-insignificant-variance.md).

       **RE-RUN COMPLETED AND IT FAILED. Job 56381674, 2026-08-06, `niter=3` confirmed in
       `configuration`, elapsed 01:58:19, rc=3, `verdict=FAIL`.** The two training-independent
       criteria passed exactly as predicted (`gap = 0.234270` >= 0.15; `floor/gap = 0.045876`
       <= 0.10, preflight cross-check AGREE). **The open number missed, and not marginally:
       `residual = 0.106159` against the `<= 0.0469` budget, `residual/gap = 0.4531` against
       `<= 0.20`, so recovery is `0.5469` against the predeclared `>= 0.80`.** Evidence:
       `pet/powered_closure/{POWERED_CLOSURE_REPORT,POWERED_PREFLIGHT}.slurm-56381674.json`,
       `DONE.slurm-56381674.txt`, artifact `...ARTIFACT.slurm-56381674.npz`
       (report sha256 `d5a01f3f4ffd…`). **Do not touch the thresholds** --- diagnose.

       **First-pass diagnosis from the report's own per-bin arrays (285 bins = 15 pT x 19
       pparallel, `BIN_ORDER` pt-major).** The failure is **not** a normalization bug and
       **not** localized pathology:
       - Normalization closes *exactly*: `sum(h_prior) = sum(h_target) = sum(h_unfolded) = 1.0`
         and `sum(h_unfolded - h_target) = 0.000000`. This is consistent with the B1 rate
         closure passing at `k=3` and means the two closures are not in contradiction --- they
         measure different things.
       - The unfold moves in the right direction but **not far enough, globally**:
         `L1(unfolded - prior) / L1(target - prior) = 0.6549`, per-bin median recovery `0.8233`,
         with 128 of 262 bins under 0.8 and **29 bins moving the wrong way** (recovery < 0).
       - The residual is **broadly distributed**, not a few bad cells: the top 10 bins carry
         26.5% of the L1 residual, top 20 carry 44.8%, top 50 carry 75.1%.
       - ~~**The miss is asymmetric in the TILT DIRECTION**~~ --- **REFUTED 2026-08-06 15:10Z. The
         cited bins were CONFOUNDED with `p_parallel`, and the first reading ("worst cells cluster at
         the `i_pparallel = 0` edge") was closer to right than the correction that replaced it.**
         Decoded (`cell = i_pt * 19 + i_pp`, verified against the report's own edges): the four
         "down-tilted" bins 38/57/76/95 are **all four at `i_pp = 0`**, i.e. `p_parallel` 0.0--0.75
         GeV where `a_b = 0.003`; the three "up-tilted" bins 242/243/244 are at `i_pp = 14/15/16`,
         `p_parallel` 10--40 GeV where `a_b ~ 0.64-0.71`. The 0.17--0.24 vs 0.72--0.91 contrast is
         **the `p_parallel` acceptance gradient read off at two different `p_parallel` values**, not a
         measurement of tilt direction at all.
         Marginalizing over all 19 `p_parallel` cells --- the only way to isolate a pT-only tilt ---
         **there is no down-tilt deficit, and the sign is if anything OPPOSITE**: down-tilted pT bins
         0--6 recover 0.65--0.75 against an ideal of 0.61--0.65 (slightly *exceeding* it), while the
         up-tilted extremes fall short (pT 12: 0.575 vs ideal 0.737; pT 13: 0.712 vs 0.854). The
         pT-8 outlier is the tilt pivot (ratio 0.977), a ratio of two near-zero numbers.

       **So the over-regularization framing is dead, and so are BOTH of its hypotheses.**
       (i) more iterations: `k=3 -> 4` buys 0.023, saturating by `k=8` --- no `k` fixes this.
       (ii) `epochs=8` optimization-limited: **measured false.** The six surviving training histories
       in `powered_closure/weights.slurm-56381674/` show step-2 train loss moving **3.2e-5** across 8
       epochs in iteration 2 and 3.0e-5 in iteration 3, with iteration 2's `val_loss` getting
       *worse* (0.829560 -> 0.829612, best at epoch 1). That is a fit with no remaining gradient
       signal, not one starved of steps. Where information exists the fit already matches the
       pointwise ideal.

       **Why the wrong hypothesis was attractive --- a real telemetry bug, now the lead item in
       `KNOWN_ISSUES`:** `omnifold.py:303` logs `hist.history['val_loss'][0]` under the label
       **"Last val loss"**. It prints **epoch 1**, not the last epoch. Anyone judging convergence from
       the log is reading the first epoch, which is plausibly how "optimization-limited" got proposed
       without the history pickles ever being opened. Related: `ModelCheckpoint(save_best_only=True)`
       (`omnifold.py:272-275`) writes best-val weights while `reweight` uses the **last-epoch
       in-memory** model, so on-disk checkpoints are **not** bit-identical to what a run used.

       **What is actually unexplained** is per-bin **scatter**, rms 0.212 about the ideal curve. It
       costs 0.084 of the aggregate through the absolute value: overshoot bins (`r > 1`) contribute
       9.3% of `residual/gap`, and `E_w[r] = 0.631` against an aggregate of 0.547 --- the signed mean
       hides it. That is a **variance** question, so it needs a **seed ensemble**, not a longer run.
       **CORRECTED --- this session first wrote "no niter=2 comparison exists, so the failure cannot
       be attributed to the niter switch either way." That was too weak.** The concurrent session
       supplied the structural argument: with acceptance `a = n_step1_a/n_truth_a = 837494/1999920 =
       0.418764` (the report's own `samples` block), `RunStep2` pins the other 58.1% of truth rows to
       exactly 1, so B1's bound gives a **ceiling on recovery** of `1-(1-a)^k` --- reproduced
       independently here: `k=1` 0.41876, **`k=2` 0.66216**, `k=3` 0.80364, `k=4` 0.88587. So
       **`56355818` at `niter=2` could never have passed a 0.80 bar; it was doomed by construction**,
       and the 2->3 switch was not merely better for B1 but *necessary for this criterion to be
       satisfiable at all*. **Caveat, theirs and important:** `1-(1-a)^k` is B1's bound for the
       fold-forward **RATE** ratio, applied here by analogy to a **spectral L1**. Same mechanism, and
       the numbers line up, but the transfer is **NOT proven** --- verify before quoting. Measured
       0.546853 is 68% of the k=3 ceiling, sitting between the k=1 and k=2 ceilings.

       **RETRACTED 2026-08-06 15:10Z --- the two paragraphs that stood here were WRONG, and wrong in
       the direction that flattered the result.** A fresh-context claude-school session (READ-ONLY,
       `/pscratch/sd/j/josephrb/q_fresh.claude.txt`) derived the bound properly and measured what the
       analogy had only assumed. Both of my/our errors are recorded rather than quietly patched:

       1. **`1-(1-a)^k` is not a CEILING, it is an EQUALITY in the ideal-classifier limit.** From
          `omnifold.py:198-200,218-220`: `nu_k(x) = a(x) C_k t(x) + (1-a(x)) nu_{k-1}(x)`, so for
          x-independent `a`, `nu_k - t = (1-a)^k (1-t)` pointwise and the spectral L1 follows
          exactly. So the transfer to L1 **does** hold --- but framing it as a ceiling let 0.547 read
          as "68% of the way to a structural limit" when the ideal limit *predicts* 0.804 and the
          estimator **missed it by 0.257**. The correct reading makes the result look **worse**, not
          partially excused.
       2. **The number was wrong, because `a(x)` is wildly non-constant.** Measured per-bin from the
          dump: `a_b` runs **0.003 to 0.81**, driven by the **MINOS match threshold** --- at
          `p_parallel < 0.75 GeV` the muon never reaches MINOS. **35 bins with `a_b < 1%` carry 23.2%
          of the injected displacement mass.** Under heterogeneity the aggregate is
          `1 - E_w[(1-a_b)^k]`, and by Jensen the global-`a` form is only an upper bound. Exact
          per-bin recursion: `k=1` 0.426, `k=2` 0.572, **`k=3` 0.635**, `k=4` 0.657, `k=8` 0.686.
          Model confirmed rather than fitted: over the 121 bins carrying the top 90% of displacement
          mass, measured vs predicted per-bin recovery gives **Pearson 0.862 / Spearman 0.879**, and
          the displacement-weighted signed means agree to 0.3% (0.63129 vs 0.63296).

       **Consequence (i) SURVIVES and strengthens:** `niter=2`'s ideal is **0.572**, not 0.66216 ---
       further below the 0.80 bar. `56355818` could not have passed. Keep that conclusion.

       **Consequence (ii) is RETRACTED AND REVERSED.** The bar does **not** sit 0.36 pp *under* a
       0.80364 ceiling. It sits **16.5 pp ABOVE the achievable 0.6347.** Reaching 0.80 on this domain
       needs `k` of order **100** (0.780 at k=50, 0.815 at k=100). The bar was not tight --- it was
       **unreachable at any practical k**. Same species as the inert-tolerance defect, **opposite
       sign**. Still not a proposal to lower it; see (e) for what replaces it.

       Note `residual/gap` and `recovery` are **one criterion stated twice**, not two independent
       failures: `recovery == 1 - residual/gap` holds exactly (verified bit-for-bit).

       **And the "more iterations" reading is dead.** `k=3 -> 4` buys **0.023** and the curve saturates
       by `k=8`. **No `k` fixes this.** The k=4 B1 arms (`56400517`, `56400519`) are therefore **not
       load-bearing** --- they still close (e)'s scalar question, so let them run, but they will not
       rescue the differential test.
   (a2) ~~**run Step 3, the ordinary P5A closure, with `--json`**~~ --- **DONE 2026-08-05,
       PASS**, job 56358150. `marginal_l1 = 0.006594` (<= 0.10, 15x margin),
       `|median(push)-1| = 0.0858` (<= 0.15), `bkg_mode = mc-only`, not a synthetic fixture,
       `refinement_invoked = False`. Receipt
       `nd-unfolding/products/pet/fullevent_fps/closure_fullevent_fps.json`, sha256
       `6c9520c7f42ecae89c0f7eb4b68cd14d5dc55518ba42a8c31fe6ee56f8e284c4`, **now committed and
       hash-bound** --- it had been an untracked, cluster-only file, so earlier statements that
       item 4 was "done" were true about the digest and false about the repository. Verified by
       execution that the gate can consume it: `check_closure_provenance` returns True, 11/11,
       and still does with the policy at `niter=3` (it does not reference `niter`, and Step 3
       legitimately runs at its own `--niter 2 --epochs 6`).
       Not blocked by the ROOT/TF interpreter split: D2 made `closure_fullevent_fps.py` default
       to `--bkg-mode mc-only`, which needs TF alone (`closure_fullevent_fps.py:14-16`).
   (a3) ~~**item 3, the measured `fold_forward_ratio_dev_max`**~~ --- **RESOLVED 2026-08-06,
       and NOT as a new number.** The tolerance stays at **0.05**; the **seed policy** moved
       `niter` 2 -> 3, which lowers the structural floor `(1-a)^k (R-1)/R` from 3.7318% to
       2.1698%. Measured on 48 seeds per arm (identical seeds 7-54, N=240,000, epochs 8, at
       R=1.1240802949941018 / a=0.4185618199216587): `niter=2` gave **6/48** exceedances of
       0.05, `niter=3` gave **0/48** (Fisher exact p ~ 0.026). Status string moved
       `PROVISIONAL_PENDING_CLOSURE_MEASUREMENT` -> `MEASURED_20260806_B1_48SEEDS_NITER3`. The
       four B1 receipts are committed as evidence. **No tolerance was raised.**
   (b) ~~**re-issue the Gate-4 launch-code gate (Step 2b)**~~ --- **DONE 2026-08-06** as
       `state/p3f-pet-gate4-launch-code-gate-20260806.json`, with all four owed items in ONE
       commit and `20260801b` retired under the D3 at-issue convention. 10 binding moves;
       verifier goes **10 mismatches -> 0** and both `test_hash_bindings.py` guards go green.
   (c) then, and only then, Step 4 --- now gated only on the powered closure re-run at
       `niter=3` (a1).
   (d) **NEW 2026-08-06, opened by the niter 2 -> 3 switch itself: the uncertainty budget must be
       RECOMPUTED at niter=3.** Any covariance component derived at `niter=2` is now inconsistent
       with the central value the campaign will publish, because `niter` changes the estimator, not
       a threshold. This is a consequence of `2b2e5f1` that the re-issue did **not** record and that
       nothing else in the repo stated --- surfaced by an out-of-band audit, not by me.
       It **couples directly to the pending flux covariance sizing** (see the J28 item), so the two
       should be planned together rather than sequentially: recomputing the budget at `niter=2` and
       then again at `niter=3` is double work against a moving target.
       Consequence for sequencing: **resolve `test_uq_remediation.py`'s J28 fixture AFTER this**, not
       before --- deciding fixture-stale vs guard-over-strict now risks doing it twice.
       **The joint plan is written up at
       [`PLAN-20260806-niter3-budget-and-J28-reroll.md`](orchestration/PLAN-20260806-niter3-budget-and-J28-reroll.md)**
       (2026-08-06), including predeclared decision rules. Note what it establishes at §2: the J28
       re-roll is **no longer blocked on the Perlmutter restore** the ledger still cites as its
       blocker --- the ~~365~~ **542** throw/block slabs (the original count missed every block slab;
       BEN-032), the three banks and `rescale_flux_universes.py` are all present, so the pass is
       schedulable now. Scratch is purgeable and those slabs are the largest schedule risk, which is
       why the plan's Step 0 is protecting them.
       **STEPS 0-2 ARE DONE (2026-08-06).** Step 0: 548 files / 8.1 GiB protected off-scratch with a
       digest+readability manifest (`nd-unfolding/products/slab_manifest_20260806.json`). Step 1: the
       exact re-roll, job `56417324` --- the Flux block was **understated ~4.2x**, `sqrt_tr_blocksum`
       **+10.19%**, `sqrt_tr_unified` **-0.72%**; the old "+3-4% upward" first-order estimate is
       superseded and was **not** confirmed, and the `g` direction is **convention-dependent**
       (mean-centered -2.55%, CV-centered +0.62%), so **adoption is blocked on the F7 decision**
       (`CORRECTED_UQ_PRODUCTION_STATUS.md:66`). Step 2:
       [`STEP2-20260806-niter3-budget-classification.md`](orchestration/STEP2-20260806-niter3-budget-classification.md)
       --- **this item's own framing is wrong for the PET lane**: there is no full-event PET covariance
       to *recompute*, so it is a BUILD (which item 6 already required), and the 5D GBDT lane transfers
       on a positive closed-input argument.
       **BOTH escalated decisions are now resolved (2026-08-06).** (i) **F7 was never open** --- its
       criterion was predeclared at `CORRECTED_UQ_PRODUCTION_STATUS.md:73-78` and the data answers it:
       `||mean_shift||` is **4.69x** the sampling floor `sqrt_tr/sqrt(160)` (37.1% of `sqrt_tr` vs a 7.9%
       floor), so mean-centered-only is disqualified and the CV-centered variant is required. **It is
       also already satisfied in the note**, which quotes `\gbdtFiveAdoptTrace` 5.81e-38 (mean-centered)
       **and** `\gbdtFiveCVTrace` 6.24e-38 (CV-centered) **and** `\gbdtFiveMeanShift` 1.65e-38 separately
       --- exactly "report the shift either way, do not silently drop". (ii) **The full-event PET budget
       is WANTED for publication** --- Joseph, mail 20:29Z: *"Ideally, the [full] event PET uncertainty
       budget is ready for the publication."* So the **>=100 GPU-h** build (the "170-250" figure is
       unverified) is planned work, not discretionary; and since the PET vertical block consumes
       `bank_uthrow_5d`, the J28 re-roll must be **adopted** before that budget is assembled on it.
   (g) **NEW 2026-08-06 --- nine throw slabs of the adopted 5D ensemble are LOST, so the corrected
       covariance is a 76.2% subsample.** The adopted `uq_5d/unified_throw_cov_5d.root` records
       `n_throws = 160` (read from the ROOT) and `sqrt_tr_unified = 4.4607819710748654e-38`, but
       `uq_5d/uthrow_slabs_5d_sb/` now holds only slabs **0-30**; slabs **31-39 (~38 throws) are gone**
       from purgeable scratch. The J28 re-roll therefore ran on **122** throws, and its "before" sits
       **-2.62%** below the adopted `sqrt_tr_unified`. The before/after *relative* changes are controlled
       (same slabs both sides) and stand, but the corrected **absolute** numbers are **not** drop-in
       replacements for the adopted covariance. **To replace it exactly, slabs 31-39 must be re-thrown**
       --- otherwise the replacement is a 122-throw product and must be labelled as one. Note Step 0's
       protection could only ever cover the survivors, so it does not mitigate this. See BEN-033 for the
       generalisable trap (read ensemble size from the product, not the launcher).
   (f) **NEW 2026-08-06 --- J28 has a SIXTH site that the fix never touched:
       `nd-unfolding/eavailW_covariance.py`.** Not among `081ae4a`'s twelve files, not scoped by
       `AUDIT-FINDINGS-20260731.md`. It loads `flux_bins` once from the CV histogram (`:104`) and passes
       it to `extract_cross_section_nd` on every call (`:232`) with no per-universe override, while
       running all 100 PPFX universes through `_y_band` (`:259`, `:274-276`) into `C_flux` --- so
       `C_flux` is **understated** exactly as the five known sites were. Mechanism confirmed; **code
       read, not run**, so no magnitude is quoted. Nothing published is wrong today (`values.tex:53-54`
       records the (E_avail,W) significances as removed; `sec_eavailw.tex:136-138` declines compatibility
       "without the corrected projected covariance") --- but that corrected covariance is a stated
       deliverable and could not be built from this script as it stood. Detail in `KNOWN_ISSUES.md`.
       **CODE FIXED 2026-08-06 (no number produced)** --- `xsec_ew`/`_y_band` take a `flux` override and
       the flux loop resolves a per-universe table through the `flux_universe` helper 081ae4a already
       shipped; fail-closed (no silent CV fallback; the old behaviour needs an explicit
       `--allow-cv-flux-universes`), guarded by
       `tests/test_flux_universe_fix.py::EavailWFluxBlockIsPerUniverse`, whose three guards are proved to
       fire against the reconstructed pre-fix source. This is the same footing 081ae4a had for the first
       five sites: code fixed and mutation-tested, **numbers not re-rolled**. The script is bound by no
       receipt, so no gate re-issue was needed. **What remains:** rebuild the `(E_avail,W)` covariance
       with the fix, as part of the `M C_5D M^T` projection this file already requires --- that needs the
       cluster.
   (e) **The niter=3 choice still owes a REGULARIZATION justification --- but a narrower one than
       this item claimed when it was opened.** `niter` is a regularization parameter: more iterations
       = less regularization = more variance, less bias. As opened, this item read everything in
       `2b2e5f1` and in
       [`FINDING-20260806-campaign-pin-inverted-on-insignificant-variance.md`](orchestration/FINDING-20260806-campaign-pin-inverted-on-insignificant-variance.md)
       as arguing the choice from **gate behaviour** --- realized exceedance 0/48 vs 6/48, window width
       to the parameter-free ceiling, false-reject rate --- which establishes the choice is *sound*,
       not that it is *right*. A B1 closure passing is not a bias-variance argument.

       **Reassessed 2026-08-06: both halves of a bias--variance argument were already receipted in
       `state/p3f-pet-gate4-launch-code-gate-20260806.json`; they had simply never been assembled into
       one.** From `seed_policy_change.measurement`, at the measured operating point
       (`R = 1.1240802949941018`, `a = 0.4185618199216587`, `N = 240000`, `epochs = 8`, seeds 7--54 in
       both arms): at `k=2` the closed-form bias is `0.037318` against a measured mean deviation of
       `0.038008` with `sd = 0.008153`; at `k=3` the closed form is `0.021698` against a measured mean
       of `0.021876` with `sd = 0.008444`. So the **bias falls by a factor 1.72 and tracks the
       `B1-NORMALIZATION-FIX-DESIGN.md:329` closed form `(1-a)^k (R-1)/R` to under 0.1 pp in both
       arms**, while the **variance is flat** (sd ratio 1.036). Bias down at fixed variance *is* the
       regularization statement; the 6/48 vs 0/48 exceedance is its observable consequence, not an
       independent argument.

       Two further points the original wording missed. The fold-forward deviation compares the
       unfold's pushed reco-level normalization against the measured data/MC ratio `R` --- a
       **reco-space, data-computable** quantity of the folding-back / bottom-line family --- so it does
       **not** fall to the objection the note itself raises against Huang *et al.*'s truth-level
       chi-square criterion (`docs/analysis-note/sec_method.tex:89-98`). And the scan is an MC closure
       with an injected rate defect, not a fit to data, so it is not the tuning-on-result loop that
       `sec_method.tex:155-167` disclaims.

       **What is still genuinely owed:**
       1. **The argument is bias--variance on ONE SCALAR** --- the reco-level rate closure --- not on
          the differential cross section. The publication-grade version needs the per-bin closure
          residual and the per-bin unfolded spread as functions of `k`. The per-bin half comes free:
          `pet/closure_powered_truth_reweight.py:302-303` already persists `h_prior`, `h_target`,
          `h_unfolded` and `h_untilted` as full per-bin arrays, so job **56381674** --- the a1 re-run,
          confirmed 2026-08-06 to be running at `niter=3` because the driver reads
          `NOMINAL_SEED_POLICY` (`closure_powered_truth_reweight.py:265`,
          `train_fullevent_nominal.py:51`) --- yields it on completion with **no code change and no
          Gate-4 re-issue**. **RESOLVED 2026-08-06, and the answer is bad:** 56381674 completed
          `verdict=FAIL` with recovery 0.5469 against a predeclared 0.80, and its per-bin arrays show
          globally-short, normalization-exact, broadly-distributed under-recovery (`L1` ratio 0.6549,
          29 bins moving the wrong way). Full diagnosis under item 2(a) above. **The scalar-scope
          caveat on CLM-010 was load-bearing: the differential test does NOT inherit the scalar
          result.** If the cause is too-few iterations for shape, this argues `k > 3`, which is the
          opposite of a stopping-point argument. Do not edit that driver to add per-bin output ---
          the data is already there,
          and `sbatch_powered_closure.sh` pins the driver's digest in `EXPECTED_DRIVER_SHA` and fails
          closed, so an edit would silently break the next submission until that constant is updated
          too. (The driver itself is *not* among the 22 live hash pins in the receipt --- the pinned
          closure scripts are `closure_b1_rate_injection.py`, `closure_fullevent_fps.py` and
          `stress_closure_muon.py` --- so the constraint here is the launcher's own pin, not the gate's.)
       2. **Nothing measured bounds `k` from above.** `(1-a)^k -> 0`, so the same argument gives
          `0.012617` at `k=4` and keeps improving; with variance flat over 2->3 it argues `k >= 3`, not
          `k = 3`. Job **56397442** (`pet/sbatch_b1_niter4_scan48.sh`, 48 seeds, same operating point
          read back out of the k=3 arm's own receipt entry) measures the k=4 point. **If its spread is
          also flat, the record must say plainly that the stopping point is set by cost and by the
          literature default of 3 --- not chosen by this measurement.** Writing it the other way round
          would be the same overclaim BEN-025 exists to prevent.
       3. **A note edit is queued but not yet owed.** `sec_pet.tex:24,47` describes the *recoil-only*
          PET cross-check, which genuinely ran at two iterations --- that text is correct and must not
          be "fixed". What will be needed once the full-event lane enters the note is one sentence
          reconciling scalar production at `n=5` (`sec_method.tex:147`) with the full-event lane at
          `n=3`, because a referee will ask; `LITERATURE_NOTES.md:65` (OmniFold default 3, <=5 typical)
          is the citation for the latter. `sec_fps.tex` carries no iteration count today, so there is
          nothing to correct in the note yet.

       Launching the nominal (which pins whatever `niter` the contract carries) should still wait on
       item 1; `nominal_pet_training_allowed: false` is doing its job. The switch was made on Joseph's
       explicit instruction and is defensible.
   The end-to-end nominal is still unproven: nothing has yet trained on this target.
3. Define the neighborhood metric explicitly. The vendored local PET assumes
   its first two token coordinates are an angular/geometric pair, while the
   current tensors begin with energy and one position/momentum component. Use
   validated view-aware detector geometry at reco and direction/angle geometry
   at truth, rather than letting raw column order define nearest neighbors.
4. Prove row alignment and reco/data schema parity; document every input, mask,
   normalization, truncation, and unavailable counterpart. Add an explicit
   leakage test proving that step 1 contains no truth-only feature.
5. ~~Add an omitted-variable stress closure that changes muon kinematics at
   fixed recoil. It must expose the recoil-only estimator and close with the
   full-event estimator.~~ **DONE 2026-08-01** — `pet/stress_closure_muon.py`,
   Delta slurm 20758087, commit `0e19f66`. Recoil-only sits at the prior
   (0.5811 vs 0.5820, blind if above 0.5x prior — 2.0x margin); full-event
   closes to 0.0428, 7.4% of the recoil-only residual (recovers if below 0.5 —
   6.8x margin). Evidence in
   `docs/orchestration/runs/b6-stress-closure-muon/`. Note the earlier PASS at
   `df7397e` (07-30) was against the pre-`--json` script; this one is against
   the hash the live Gate-4 receipt binds and is machine-readable, which
   Gate-4's now-required `--stress-report` needs.
   **The rest of this item is still open:** the present identity closure is now
   classified as an MC self-consistency smoke, not evidence for the
   `negweight-refined` target. Add and run a nontrivial injected truth-reweight
   recovery closure at the nominal estimator configuration, enforce central
   normalization and lower-dimensional marginal gates, and retain
   full-event-versus-recoil comparisons in the FPS extension and dead-cell
   tiers. Passing either the stress closure or the MC smoke alone does not
   satisfy the FPS controls. See decision D2 in the canonical record above.
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
   **ASKED AND PARTIALLY ANSWERED 2026-08-02** (in person at the presentation;
   verbal, no citable thread — see the ANSWERS section of
   `docs/COLLABORATOR_QUESTIONS.md`):
   - **FrInel_pi — CLOSED.** Still current practice, but the reason is a
     *degeneracy*: a set of dials overlap / are circularly dependent and any one
     of them must be commented out. So the choice of `FrInel_pi` is conventional,
     not a statement that the knob is individually suspect — which is what the
     MAT source comment reads like. Cite the practice and the degeneracy, not
     the comment's implication.
   - **Ours-only truncated-spectral chi^2 — CLOSED.** The collaboration uses the
     same truncated-spectral pseudo-inverse. Confirmed as practice, not as a
     citation; a reference is a separate ask if the note needs one.
   - **First 3D+ unfolded covariance — PREMISE CORRECTED; endorsement still
     owed.** Clarified 2026-08-02: MINERvA does have a 3D unfolding publication,
     already found and cited, and nothing beyond that. The question's premise
     ("no prior MINERvA 3D+ unfolding result") was therefore wrong, but the
     note never made that claim — it says prior multi-differential results were
     *binned* and the distinction here is the unbinned, simultaneously-unfolded
     formulation plus the full 3D+ covariance. No note edit needed. **What is
     still owed is the endorsement itself**: no view was given on publishing the
     1431-bin covariance or its rank-deficient GoF, which is what App. A item 5
     actually gates.

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
