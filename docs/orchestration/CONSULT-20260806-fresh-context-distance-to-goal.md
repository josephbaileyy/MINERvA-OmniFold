I read the consult transcript, CLAUDE.md, the D2 block of `docs/OPEN_ITEMS.md`, the J28/niter-3 plan, and `KNOWN_ISSUES.md`, then verified the load-bearing claims against code and artifacts. Nothing written, staged, committed, or submitted.

**Your draft is directionally right but wrong in the same direction the last two framings were wrong: it flatters the code.** The headline "the code is ready and verified; the physics is not" does not survive. I found a defect in the one step that actually produces the deliverable, and it is exactly the species of `KNOWN_ISSUES` trap #10.

---

# (0) The thing your draft is missing, and it outranks items 1–7

**`extract_fullevent_fps.py` divides the cross section by an efficiency it must not divide by. As written, Step 4b will produce a result ×2.36 too high on the integral and ×398 too high in the lowest p∥ bin.**

The chain, all verified this turn:

| step | evidence |
|---|---|
| The extractor's completeness is *reco efficiency* | `extract_fullevent_fps.py:390-404` — `comp = Σw(pass_truth&pass_reco)/Σw(pass_truth)`, docstring "Verbatim `PETxsec5D._comp`" |
| It goes in the **denominator** | `xsec_nd.py:79` — `denom = completeness * flux * n_nucleons * data_pot * vol` |
| `counts` is over **all** fiducial truth, so it is already efficiency-corrected | `extract_fullevent_fps.py:431-434` histograms `(w_truth*push)[pass_truth]`; `push` comes from `reweight_full_inventory` over all 49,152,885 rows. OmniFold step 2 assigns ν_k to truth-only-miss rows (`omnifold.py:218-220`) — that is what step 2 is *for* |
| On this exact grid the correct completeness is **identically 1** | I opened `nd-unfolding/active_universe_5d/fps/unfolds/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_BeamAngleX_{0,1}.root`: `globalCompleteness = 1.0000000000000002`, `hCompletenessND_flat` = 285 bins, **266 nonzero, min = median = max = 1.000000**. 266 is exactly the populated-cell count I get from the G2 dump |
| …and the validated driver *asserts* it | `unfold_nd_omnifold_unbinned.py:993-999` defines completeness as `of_in/mc_truth_denom` — a **coverage** correction, not an efficiency — and `:747-752` requires `n_sig_truth == n_td` **exactly** when native misses are present. The G2 dump has them: 58.1% of its rows are `pass_truth & !pass_reco` |
| `PETxsec5D` only ever survived this because of the anchor | `pet_systematics_5d.py:127-141` — `comp_rescale = ref/comp_pc_cv` overrides its own ε with the GBDT completeness, "makes the CV match the milestone" (median 1.215/1.258, `ND_OMNIFOLD_RUN_LOG.md:976`, `PET_UQ_PRODUCTION_STATUS.md:462`) |
| The FPS port deliberately carries **no** anchor | `extract_fullevent_fps.py:459-461`: `completeness_anchor: "NONE — … no such anchor exists for this domain and inventing one would rescale the answer"` |
| No test has power over it | `tests/test_fullevent_extract.py:351-376` recomputes the same formula with the same helper and asserts bit-equality — a self-agreement test. `:331-342` *pins the wrong semantics as intended behavior* |

**The runbook's claim "no such anchor exists for this domain" is false.** It exists, in this repo, on this exact 285-cell grid, and it is the constant 1.

Two notes on robustness. First, the defect is the same either way: either `counts` should be masked to `pass_truth & pass_reco` and the division is right, or `counts` is right and the division must go. Second, the practical failure mode is not silent corruption — a 2.36× discrepancy against the FPS GBDT product will be obvious. The danger is that someone "fixes" it by inventing an anchor, which the runbook warns against in the same breath.

**Consequence for ordering: Step 4 (train) is safe to run now; Step 4b (extract) must not run until this is settled.** Fixing it touches a hash-pinned test file, so it is a gate event — much cheaper now than after a commissioning run.

---

# (1) Item-by-item

**Item 1 — powered closure criterion.** Substance agreed. But the proposed replacement, `recovery / ideal_recovery(a_b,k) ≥ θ`, **is the inert-tolerance defect in a new dress**: the denominator auto-lowers the bar exactly where `a_b` is small. At `a_b = 0.0025` the ideal at k=3 is 0.0075, so any estimator — including a null one — passes there. Deeper: **no closure criterion can have power in the low-a region at all.** A closure injects a truth reweight and asks if it is recovered; at a=0.0025 the structural answer is "no, by 98.5%" for every estimator. The redesign needs two criteria, not one: the ratio criterion on a predeclared high-`a_b` subdomain where it has power, and a **prior-sensitivity** criterion on the rest — which is not a closure test, and which is the same object item (d) owes anyway.

**Item 2 — `nominal_pet_training_allowed: false`. This is not a gate.** It is a hardcoded literal in the payload (`validate_pet_nominal_gate4.py:1117`): the validator emits `False` unconditionally, PASS or FAIL, and no code path sets it True. And `sbatch_pet_fullevent_nominal.sh` **never reads it** — its real preconditions are the Gate-2 target sha/size (`:101-102`), the Gate-3 manifest verdict (`train_fullevent_nominal.py:164-165`), and `assert_publication_config` (`:159`), all currently satisfied. "The nominal has never been trained" is right. "`nominal_pet_training_allowed: false` is blocking it" is wrong. It is Joseph's decision, exactly as the docstring at `:6` says.

**Item 3 — Step 4b.** Correct, and now much stronger: see §0. The `pass_truth` mask fix landed in `2b2e5f1` today; the completeness defect is in the same function's caller and did not.

**Item 4 — Step 7. Drop it; it is not on the path.** `RESTORE-2026-08-03.md:28-32` gives the spine as `0a→0→0b→1→2→6→3→2b→4→4b`, and says in as many words "(5, 7, 7b are independent)". Step 7 is the real-data arm of the **event-feature ranking** (B-3 evidence), not of the measurement. There is no separate real-data step for the cross section — the nominal already trains against the data-derived Gate-2 target (`bkg_mode=negweight-refined`). Listing it as blocking overstates the distance.

**Item 5 — niter=3 budget.** Agreed, plan is good. One thing it does not say: **there is no statistical-covariance capability for this lane at all.** `extract_fullevent_fps.py:148,165` refuses `bootstrap_seed != -1`; `sbatch_pet_bootstrap_replica.sh` / `extract_bootstrap_replica.py` are the recoil/5D path. C_stat for full-event FPS is an unwritten launcher plus ~20×(8 h train + push), not a queued run. That is very likely the largest remaining GPU cost in the campaign and nothing tracks it.

**Item 6 — J28.** Agreed; the plan's §2 establishes it is schedulable now.

**Item 7 — you are not over-weighting it. You are under-quantifying it.** Verified independently from the G2 dump (`w_truth`-weighted, and cross-checked unweighted):

| p∥ (GeV) | % of fiducial truth | acceptance `a_b` | **(1−a_b)³** | (1−a_b)¹⁰⁰ |
|---|---|---|---|---|
| 0.00–0.75 | 10.32% | 0.00251 | **0.9925** | 0.778 |
| 0.75–1.50 | 10.80% | 0.00722 | **0.9785** | 0.485 |
| **< 1.50 total** | **21.12%** | — | **0.9854** | — |
| whole declared domain | 100% | 0.4235 | **0.3905** | — |

The decision-relevant number is not the acceptance, it is the closed-form prior weight. Since ν_k = (1−(1−a)^k)·t + (1−a)^k·1, the fraction of the answer that is **still the prior, with no data correction at all**, is (1−a_b)^k. So at k=3:

- In the fifth of phase space the FPS extension exists to add, **98.5% of the answer is GENIE.**
- Across the whole declared domain, **39% of the answer is GENIE** in the *ideal-classifier limit*.
- Even k=100 leaves 78% / 48% in the two lowest bins. No k fixes it. (Independently reproduces the predecessor's saturation conclusion from a different direction.)

And it is worse than an uncertainty problem, because of what those bins *are*: `fullevent_fps_dataloader.py:72-75` sets `_PAPER_PPAR_MIN = 1.5` and comments "FPS adds `[0,0.75,1.5]` low catch bins — the FPS grid must **not** be the paper grid," and the reported mask is `h_prior > 0` (`train_fullevent_nominal.py:101`). **The novel content of this measurement relative to the published 2D result is precisely its least-measured region, and the estimator's resolution there is ~1.5%.** That is the sentence to put in front of Joseph.

One number to re-verify before it is quoted anywhere: the predecessor's `a_b = 0.012` for p∥ 0.75–1.5. I get 0.00722 weighted and 0.00706 unweighted — a 1.7× disagreement. Global values agree (0.418539 unweighted vs the Gate-2 receipt's 0.4185618), so it is bin-local, probably a binning or subsample difference. Conclusions unchanged either way.

**What your draft over-claims:** "the code is ready and verified." Correct it to: *the gates are green on everything except the last mile; the last mile has never run and has a wrong-quantity bug; and the estimator's structural resolution over a fifth of the declared domain is ~1.5%.*

---

# (2) Does the powered closure have to pass before the nominal can be trained?

**No — and the campaign is not blocked on redefining a criterion.** Four reasons:

1. No mechanical interlock exists (§Item 2 above).
2. The redesign changes the *criterion*, not the estimator. A nominal trained at the frozen seed policy stays valid under any redesign that does not move `seed_policy`.
3. Even if the redesign shrinks the reported domain, that moves FROZEN's mask → Gate-4 re-issue → **but not a retrain**: the mask is applied at histogramming, from per-event weights (`train_fullevent_nominal.py:94-101`; the extraction re-histograms from the full push array).
4. Cost asymmetry: 8 h × 1 GPU against a criterion redesign that needs an ensemble first.

Say it plainly to Joseph: *training the nominal is unblocked today; what is blocked is quoting the result.* Train it, mark the product non-quotable in the same commit, and put the completeness gate in front of 4b instead.

---

# (3) Realistic ordering, step count, GPU-hours

| lane | steps | GPU-h | notes |
|---|---|---|---|
| **A. free, today** | A1 settle + fix the completeness defect (gate event); A2 checkpoint k-scan (§below); A3 commit the acceptance map + the (1−a_b)^k table as a tracked product | ~0.2 | A3 is now load-bearing for three separate items |
| **B. central value, parallel with everything** | B1 Step 4 nominal (8 h wall, incl. matched floor repeat); B2 Step 4b — **only after A1** | 8–16 + 4–8 | product non-quotable |
| **C. power evidence** | C1 8-seed ensemble at k=3 → noise floor → θ (+8 at k=4 discharges (e)#1); C2 second injection **with p∥ dependence** — the test that has the power you want; C3 Gate-4 re-issue, two-criterion design | 16–32 + 2 | C1 needs an `--estimator-seed` override → `EXPECTED_DRIVER_SHA` bump in the launcher, not a gate re-issue |
| **D. uncertainty** | D1 the PLAN's Step 0→5 (protect slabs, J28 re-roll, niter classification, rebuild, fixture, quarantine lift) — 5 sub-steps, mostly CPU; D2 prior/model band for the low-a region (`fps_prior_envelope.py` + `--prior-reweight` exist on the GBDT path; **no PET analogue**); D3 **C_stat — capability does not exist** | ~10 + 16 + **160–240** | D3 is the long pole |

**≈14–16 distinct campaign steps. ≈60–90 GPU-h for the central value and its power evidence; ≈170–250 more if a full-event statistical bootstrap is required.** Wall-clock is queue-dominated — 56355818 waited 21.5 h — so I would not convert these to dates.

**Honest answer to Joseph's question:** the central value is a handful of steps and under 100 GPU-hours away. The uncertainty is further than the item list suggests, because one component (C_stat for this lane) has no implementation, and one component (the model/prior band over 21% of the phase space) is not estimable by any method currently in the repo. And in that 21%, "uncertainty" is the wrong word: the result there is 98.5% prior, so what is owed is a prior-variation band that will dominate, not a covariance.

---

# (4) Step 1: agree it should run — but not as designed, and not first

**Agree on value, disagree on protocol, disagree on priority.** A1 goes first because it is free and it is about the deliverable. Then run the k-scan; it is minutes and the k-dependence is otherwise unmeasured.

**The stated caveat is now measured, and it is worse than "k=3 will not reproduce exactly."** I read all six history pickles: `argmin(val_loss)` = **4, 4, 6, 0, 5, 4 — never the last epoch (7), in any of the six.** And `patience = early_stop = 10` (`omnifold.py:58,128`) with `EPOCHS = 8`, no caller overriding it (`closure_powered_truth_reweight.py:265`, `train_fullevent_nominal.py:391`), so `EarlyStopping(restore_best_weights=True)` (`:266-268`) can never fire inside 8 epochs — Keras restores only inside the stop branch. So the in-memory model `reweight` used **is** the last epoch, and every on-disk checkpoint **is** a different epoch.

**Therefore "calibrate on k=3 first" is not available**: the one comparison you would calibrate on carries the same unknown offset you are trying to remove. What survives is a reframing — the three step-2 checkpoints are *homogeneous* best-val models from one trajectory, so the **k-differences** are a fair test even if the level is offset, and the k=3 value **measures** the offset rather than absorbing it.

Also: `closure_powered_truth_reweight.py` **persists no inference contract** — the artifact holds only `dump_rows_a/b`, `weights_push`, `mc_indices` (`:287`). Architecture comes from `meta` (`:261-263`) and the input normalization is derived inside `build_fullevent_loaders` at run time. Re-deriving it is safe here *only because* `dump_rows_b` is saved, so you can reproduce the same population — the J02 warning is about deriving it over a *different* population (49.2M instead of 2M). But it means **there is no stored normalization to assert against, so the k=3 spectrum reproduction is the only falsification handle. Skip it and the exercise is unfalsifiable.** (Worth a `KNOWN_ISSUES` row: the nominal driver stores its norms, the closure driver does not.)

### How, concretely

1. **Rows:** `dump_rows_b` (2,000,000 int64) from `POWERED_CLOSURE_ARTIFACT.slurm-56381674.npz`.
2. **Inputs:** stream `part_gen` and `truth_scalars` for those rows from `G2_FPS_MEFHC_P12.npz` using `extract_fullevent_fps._RowStream`. Do **not** slice `d["part_gen"][lo:hi]` — deflate re-decompresses from the start; `tests/test_fullevent_extract.py:228-237` exists for that trap. `part_gen` is 11.8 GB decompressed.
3. **Model:** rebuild the step-2 (truth-leg) PET with `num_evt = meta["n_evt_truth"]`, `num_part = P`, `num_transformer = 2` exactly as `:263`; derive the truth-leg normalization from `dump_rows_b` via the same `build_fullevent_loaders` call at split seed 7 — do not hand-roll it. Load `OmniFold_fe_powered_iter{0,1,2}_step2.weights.h5`.
4. **Reweight:** use the engine's own `MultiFold.reweight` on a minimal instance (same pattern as `extract_fullevent_fps._engine_reweighter`) so the logit cap is one implementation. Then mirror `RunStep2` exactly: `push = np.ones(2_000_000); push[pass_truth_b] = reweight(...)[pass_truth_b]` — **ones, not empty** (`omnifold.py:218-220`; this is the bug `2b2e5f1` fixed).
5. **Histogram:** `np.histogram2d(pt, ppar, bins=[fe.CANONICAL_PT_EDGES, fe.CANONICAL_PPARALLEL_EDGES], weights=(w_truth*push))` on `pass_truth` rows, normalize to unit sum — the convention at `closure_powered_truth_reweight.py:302-303`.
6. **Metrics:** take `h_prior`, `h_target`, `h_untilted` verbatim from `POWERED_CLOSURE_REPORT.slurm-56381674.json`, and **import** `validate_pet_nominal_gate4.check_powered_closure`'s arithmetic (`:733-901`) rather than re-implementing gap/floor/residual. `recovery = 1 − residual/gap`.

### Predeclared refutation — fix these before you look

Model: `r_b(k) = 1 − (1−a_b)^k` pointwise; aggregate `recovery = 1 − E_w[|1 − r_b(k)|]`.

- **R1 (method, checked first).** If `|r₃^ckpt − 0.546853| > 0.02`, the checkpoints are not the run's estimator: the k-scan is uninformative, **no claim either way**, stop. A large δ is not evidence for or against the model, and must not be reinterpreted as either.
- **R2 (the actual test).** With `|δ| ≤ 0.02`, REFUTED if `|Δ_meas(1→2) − 0.146| > 0.03` **or** `|Δ_meas(2→3) − 0.063| > 0.03`. (0.03 ≈ half the smaller predicted increment; fixed now.)
- **R3 (sign, δ-independent).** REFUTED if recovery is not monotone in k, or if `Δ(2→3) > Δ(1→2)`. The recursion forces both.
- **R4 (per-bin).** REFUTED if, over the 121 bins carrying the top 90% of displacement mass, `Spearman(r_b(k=1), a_b) < 0.5`, or `∂r_b/∂k < 0` in more than 10% of them.
- **R5 (structural — and note it is already failing).** The model says the 32 cells with `a_b < 0.005` can recover at most 0.005 at k=1 and 0.015 at k=3. The predecessor's own table measures **0.208 / 0.202 there at k=3 against an ideal of 0.008 / 0.034 — over-recovery by ~25×.**

**So the honest predeclaration, which is what I would hold you to, is this:** the acceptance model is already *confirmed as a description of the aggregate* and *refuted as a description of the low-a bins*, before the k-scan runs. It gets the aggregate right (0.63129 vs 0.63296) because low-a over-recovery cancels high-a under-recovery. "The acceptance model is confirmed" must therefore never be stated globally — it holds where `a_b` is large and is violated by 25× where `a_b` is small, in the direction of the estimator manufacturing information in cells the detector cannot see.

**The k-scan's single most informative output is whether that 25× over-recovery is flat in k or grows with k.** If it grows, it is iteration-driven and k is the lever. **If it is flat, it is architectural pooling across p∥ — and then the low-p∥ FPS bins are not a measurement, and no criterion, no extra k, and no covariance will make them one.** That is the result you cannot rationalise afterwards, and it is the one that decides what "a cross section for the full phase space" is allowed to mean.
