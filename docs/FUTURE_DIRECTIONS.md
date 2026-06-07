# Future directions — MINERvA OmniFold toward the full-phase-space cross section

**Created 2026-06-06.** The end goal is a *full unfolding of the cross section over the full
phase space*. The binned/scalar track (2D → 3D → 4D `d⁴σ/(dp_T dp_∥ dE_avail dq3)`, all with
combined syst+stat+ML covariance budgets) is essentially complete, and the **PET point-cloud
absolute-cross-section method milestone** is the current active workstream (see
`nd-unfolding/ND_OMNIFOLD_STATUS.md`; design `HIGHER_DIM_OMNIFOLD_DESIGN.md`). This file
records the directions chosen *not* to do now, with enough detail to pick up cold.

The user's 2026-06-06 decision: pursue the PET → real absolute measurement at **method-
milestone** scope first (full-stats absolute measurement validated by closure + GBDT
cross-check), and **record** the directions below as future work.

---

## 0. Deferred — publication-grade completion of the PET milestone (full systematics)

The active milestone delivers a full-statistics, absolutely-normalized PET point-cloud cross
section validated by closure and an absolute GBDT cross-check, but **without** its own
systematic/stat/ML covariance. The publication-grade completion is to drive the
**engine-agnostic UQ harness** through the PET engine exactly as the GBDT path does:

- **Systematics:** per-universe re-unfold over the 187-universe sweep (the same
  `universes_full_list.txt`), feeding each universe's reco/truth clouds through the trained
  PET reweighter, then `analyze_universes_nd.py` (bin-count- and engine-agnostic) for the
  block-sum covariance + 1.4% norm band.
- **Stat:** `bootstrap_nd.py` analogue on the point-cloud npz (Poisson-weight the PET inputs).
- **ML:** ensemble of PET trainings (the `n_ensemble`/NTRIAL convention, already validated on
  the GBDT split-seedscan) → the ML band + ensemble-mean CV.
- Combine via `combine_cov_nd.py` → the 4D PET combined budget, the analogue of the GBDT
  `uq_universe_4d_covariance_combined.root`.

Cost: PET is GPU-heavier than LightGBM, so 187 universe re-unfolds is the expensive part —
amortize with the read-once bank pattern (see memory `nd_unfold_io_bound_bank`) and PET
**inference** reuse (train once per universe class, reweight cheaply). This is the natural
"make the point-cloud result publishable" step.

---

## B. New physics axis — the high-E_avail DIS-tail excess (open question 6)

> **STATUS 2026-06-06 — IMPLEMENTED (W), pending the re-run.** Chosen observable = **W**
> (hadronic invariant mass; DIS = high W). Truth `GetTrueExperimentersW()` already existed;
> added `RecoW()` + wired W fully into `runEventLoopOmniFold.cpp` (mirrors q3, incl. lateral
> shifted-W) + registered axis `W` in the nd driver (`--axes eavail,q3,W`). An investigation
> of the alternatives found W is the only candidate with a clean RECO estimator (the tuples
> carry only calorimetric clusters — no per-particle id/momentum), so proton multiplicity +
> hadronic angle are dumped as TRUTH diagnostics (`MC_nproton/MC_npip/MC_hadangle`) in the
> SAME re-run for excess investigation, but cannot be OmniFold axes until a reco estimator is
> built. Built + smoke-tested (see `nd-unfolding/ND_OMNIFOLD_RUN_LOG.md`, Workstream F).
> The only remaining (expensive) step is the 12-playlist event-loop re-run + 5D unfold + cov.



The one genuinely open *physics* item (`docs/technote/sec_openquestions.tex:76`): enabling
Valencia 2p2h resolves the low-recoil excess but leaves a separate **+2.2σ data excess in the
E_avail [1.50, 3.00) GeV bin**, where 2p2h does not contribute and the sub-percent pion-FSI
dials cannot reach — a deep-inelastic / high-W tail modelling question.

Direction: add a **physically-motivated 5th scalar axis** that localizes this excess —
candidates (pick by physics, not blindly): hadronic invariant mass **W**, **proton/hadron
multiplicity**, or a **hadronic-system angle**. The unfolding machinery is ready: the
axis-list driver `unfold_nd_omnifold_unbinned.py` (`EXTRA_AXES` registry) already takes an
arbitrary axis list, and `xsec_nd.py` is dimension-agnostic. The cost is the usual one per
*new observable*: a `CVUniverse.h` accessor (mirror `NewEavail()` L184 / `GetEAvailableTrue()`
L194) + a 12-playlist event-loop re-run to dump the new truth/reco branch, then the same
covariance pipeline. Keep the new axis binning coarse (the 4D covariance is already mostly
null space). Anchor with the marginal-recovers-4D Jacobian identity + injected-shape closure,
exactly as q3 was validated.

---

## C. Rigorous unified-throw systematics (block-sum vs unified covariance)

The block-sum (uncorrelated-band) covariance construction is **consistent** but not cleanly
*confirmed*. The cheap single-throw superposition probe was jitter-limited (cross-terms at the
OmniFold run-to-run floor → leans block-sum-valid), and the ratio-product "unified throw"
proxy was found **artifact-prone** (multiplying single-band reweight ratios compounds low-w_cv
tail events → a spurious 25× inflation; `ND_OMNIFOLD_RUN_LOG.md`, 2026-06-04).

The methodologically sound object is a **true multi-band universe** campaign: the event loop
applies *all* systematic shifts together per universe (one genuinely jointly-shifted sample
per throw), re-unfold each, and build the covariance directly. Jitter averages down as
1/√T over many throws. This is a pre-publication methodology item (memory
`prepub_methodology_items` #1), independent of dimensionality/engine — it can run on the
existing 3D/4D result. It is the definitive settlement of the block-sum assumption.

---

_See also: `LITERATURE_NOTES.md` §C (recorded pre-pub items), `HIGHER_DIM_OMNIFOLD_DESIGN.md`
§5 (cost/risk: only publish binned projections along axes with a physics question)._
