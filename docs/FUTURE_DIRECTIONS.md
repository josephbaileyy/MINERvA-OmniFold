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

> **2026-06-09 — four follow-on extensions: ALL 4 DONE.** See
> `nd-unfolding/ND_OMNIFOLD_RUN_LOG.md` "Four-extension campaign RESULTS" for the full detail.
> (14) **Rigorous 4D unified throw — DONE & ADOPTED.** 160-throw covariance on the real
> (pt,pz,eavail,q3) binning: jitter-corrected unified/block sqrt-trace = **2.01** (block-sum
> underestimates the vertical systematic ~2×), concentrated in the high-pT/lowest-Eavail corner
> (top 1% of bins = 78% of the trace excess). Adopted via PSD-safe fractional-inflation transfer
> onto the sweep's vertical block (`adopt_unified_4d.py` → `uq_universe_4d_covariance_combined_uthrow.root`,
> published cov sqrt-trace ×1.84, median 13.5→14.9%/bin). (15) **PET lateral band — DONE**
> (`pet_lateral_correction.py`, engine-independent fractional transfer; PET 4D total 22.4→23.02%) —
> closes the one PET-budget zero. (16) **GiBUU 4th band generator — DONE** (80-run regen +
> `gibuu_to_xsec_eavailW.py`, σ=2.22e-38 = most deficient); the dσ/dEavail generator significance
> now spans all 4 generators on the adopted cov: data misses each at >21σ overall / >15σ in the
> DIS tail. (13/B) **(E_avail,W) covariance + W-resolved significance — DONE.**
> The 12 5D `_universes_full` omnifiles merged (133 GB); `eavailW_covariance.py` ran the
> frozen-reweighter block-sum (one CV unfold + 13 knob + 100 flux universes re-binned, no
> re-inference) + stat + transferred lateral → `products/5d/eavailW_covariance.root`, median
> 14.8%/bin. CV validated to 0.1% vs the frozen 5D product — the self-validation gate caught a
> reco-pass completeness double-count (OmniFold step2 already corrects efficiency in truth space; the
> driver's completeness numerator is the FULL truth-pass set, `unfold_nd_omnifold_unbinned.py:642`),
> which had inflated the data ~2×; fixed before trusting any number. Full 42-bin (E_avail,W) χ²/ndf:
> GENIE-CV 412.7/42 (16.7σ), +MEC 390.5/42 (16.1σ), NuWro 1148.4/42 (31.2σ), GiBUU 1930.2/42 (>37σ).
> High-W DIS corner (E_avail≥0.4 & W≥1.8 GeV, 12 bins): 9.0/9.2/10.5/**18.2σ** (GiBUU most deficient)
> — the excess is a genuine high-W DIS-region feature.
> Residual deferrals: full per-lateral PET re-inference; a true multi-band (lateral) event-loop
> unified throw; W-resolved (not transferred) laterals.

---

## 0. ~~Deferred~~ DONE 2026-06-08 — publication-grade PET 4D combined covariance

> **STATUS 2026-06-08 — DONE.** `pet_systematics.py` delivers the PET 4D combined
> covariance (`products/pet/pet_4d_covariance_combined.root`, 4796 reported bins) via the
> documented frozen-reweighter path: the trained full-stats PET push weights are held fixed
> and re-binned per reweight universe (no per-universe re-inference, since reweight universes
> share clouds), with the per-event universe ratios taken from `bank_uthrow` (verified
> bit-identical gen ordering to `of_inputs_pc.npz`) and the CV completeness anchored to the
> validated GBDT product. Budget (median per-bin): **C_syst 18.3%** (block-sum over 12 GENIE
> knobs + 100 flux universes, flux-dominated), **C_stat 4.2%** (Poisson bootstrap), **C_ML
> 3.3%** (CV-vs-hi-iter training spread), **C_total 22.4%** — the same syst>stat>ML hierarchy
> as the GBDT 4D budget. The lateral (kinematic-shift) universes remain the one approximation
> (frozen reco clouds); a full re-inference per lateral universe is the residual refinement.

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

> **STATUS 2026-06-07 — DONE (W axis built, unfolded, and excess localized).** Chosen
> observable = **W** (hadronic invariant mass; DIS = high W). Truth `GetTrueExperimentersW()`
> already existed; added `RecoW()` + wired W fully into `runEventLoopOmniFold.cpp` (mirrors q3,
> incl. lateral shifted-W) + registered axis `W` in the nd driver (`--axes eavail,q3,W`). An
> investigation of the alternatives found W is the only candidate with a clean RECO estimator
> (the tuples carry only calorimetric clusters — no per-particle id/momentum), so proton
> multiplicity + hadronic angle are dumped as TRUTH diagnostics (`MC_nproton/MC_npip/
> MC_hadangle`) in the SAME re-run for excess investigation, but cannot be OmniFold axes until
> a reco estimator is built. The 12-playlist re-run + 5D unfold is **complete and validated**:
> `xsec_5d_MEFHC_5iter_lgbm.root`, W-marginal recovers the frozen 4D anchor to **5D/4D=1.0011**,
> injected-W closure 1.0000±0.0062.
>
> **Result (open question 6 is DIS-like).** `excess_eavail_W.py` compared the unfolded
> $(E_{avail},W)$ cross section to the GENIE CV (the OmniFold prior): the +2.2σ high-E_avail
> excess is **predominantly high-W**. High-E_avail (≥0.8) carries **67.2%** of the positive
> excess, of which **83.2% sits at W≥1.8 GeV**; the deep-DIS corner (E_avail>3, W>3) alone is
> **21.9%**. Plus a thin low-W (QE-like) excess and a small Δ-region deficit. See
> `nd-unfolding/ND_OMNIFOLD_RUN_LOG.md` (2026-06-07) and `docs/technote/sec_openquestions.tex`
> item 6.
>
> **Generator band — DONE 2026-06-08 (the excess is generator- AND tune-robust).** Regenerated
> GENIE-CV (2M), GENIE+Valencia-MEC (1.5M) and NuWro (2M, native Enu threaded through
> `nuwro_to_flat.C` for an experimenter's-W branch) events; the new `gen_to_xsec_eavailW.py` /
> `nuwro_to_xsec_eavailW.py` bin each onto the data's `(E_avail,W)` axis with spline/per-event
> normalisation, and `overlay_eavailW_band.py` overlays vs the unfolded data
> (`3d-unfolding/genie/eavailW_band.{png,root}`). **All three** generators underpredict the
> high-E_avail×high-W corner by 54–58% (data/gen = 1.54, 1.58, 1.56); enabling Valencia 2p2h
> does NOT close it (slightly worsens it — 2p2h is low-W), and NuWro misses it by the same
> margin. At W∈[2.2,3.0) all three sit 23–25% below the data. **(Update 2026-06-09: GiBUU is now
> the 4th band generator** — its `FinalEvents.dat` muon-ID 902 + col-15 Enu make experimenter's W
> computable; σ=2.22e-38, the most deficient.)
> **Significance — DONE (2026-06-09):** the full `(E_avail,W)` covariance
> (`eavailW_covariance.py` → `products/5d/eavailW_covariance.root`, median 14.8%/bin, CV validated to
> 0.1%) attaches χ²/Nσ to the band. Over the full 42-bin plane the four generators miss the data at
> 16.7/16.1/31.2/>37σ (GENIE-CV/+MEC/NuWro/GiBUU); in the high-W DIS corner (E_avail≥0.4 & W≥1.8 GeV,
> 12 bins) at 9.0/9.2/10.5/18.2σ — the excess is W-localised in the DIS region. A dedicated W
> systematic campaign (per-universe shifted-W laterals, not the transferred 4D laterals used here) is
> deferred (the binary already dumps the shifted-W lateral universes, so the bank exists when needed).



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

## C. ~~Rigorous unified-throw systematics~~ DONE 2026-06-08 — block-sum UNDERESTIMATES

> **STATUS 2026-06-08 — DONE (`unified_throw_cov.py`).** Built and ran the rigorous many-throw
> unified covariance, settling the block-sum assumption. Instead of a C++ event-loop re-run, the
> per-event universe ratios already in `bank_uthrow` are composed at the **event-weight** level
> (`w_cv·∏_b ρ_b^{g_b}`, g_b~N(0,1) over the 12 reweight knobs + one sampled flux universe) and
> each throw is **re-unfolded** by OmniFold — the correct construction a true multi-band universe
> would produce (for the reweight bands), avoiding the binned-ratio-product artifact. 75 throws
> vs a parallel block-sum (12 knobs + 12 flux units). **Result: sqrt-trace unified/block = 1.40,
> per-bin σ median 1.16.** A jitter null (2nd CV unfold) puts the OmniFold floor ~10× below the
> cross-term, so the corrected ratio is still 1.40 — real, not jitter. **The block-sum
> UNDERESTIMATES the systematic covariance by ~16% per bin (robust median) to ~40% in sqrt-trace**:
> the iterative unfolding adds a significant positive nonlinear cross-band term the block-sum
> drops. (The cheap single-throw probe missed this — it was pairwise and jitter-limited.) Robust
> statement = the 16% median; the 40% trace is partly Gaussian-tail compounding in a few
> high-variance bins. Artifacts: `nd-unfolding/uq_4d/unified_throw_cov.root`. **Remaining:** fold
> the cross-term into the published budget (or adopt the unified throw as the systematic cov),
> and a C++ true-multi-band event-loop run would additionally capture the **lateral**
> (kinematic-shift) bands this weight-composition cannot.

The block-sum (uncorrelated-band) covariance construction was **consistent** but not cleanly
*confirmed*. The cheap single-throw superposition probe was jitter-limited (cross-terms at the
OmniFold run-to-run floor → leaned block-sum-valid), and the ratio-product "unified throw"
proxy was found **artifact-prone** (multiplying single-band reweight ratios compounds low-w_cv
tail events → a spurious 25× inflation; `ND_OMNIFOLD_RUN_LOG.md`, 2026-06-04). The
event-weight-composition + re-unfold above is the methodologically sound object and is now done.

---

_See also: `LITERATURE_NOTES.md` §C (recorded pre-pub items), `HIGHER_DIM_OMNIFOLD_DESIGN.md`
§5 (cost/risk: only publish binned projections along axes with a physics question)._
