# HANDOFF — unbinned background subtraction via negative-weight injection (personal → claude-school)
Written 2026-07-07 by the personal-account session. Point claude-school here.
Log progress to `bkg_negweight_state.md` in this directory (same convention as
`nd-unfolding/HANDOFF_fps_step3/fps_pipeline_state.md`). claude-school has a SEPARATE memory dir —
everything needed is in this file plus the repo docs it cites.

## THE ASK (advisor \bpn, relayed 2026-07-07, verbatim)
> "I think the negative weight method for background subtraction would be ideal. It would basically
> be the unbinned version of what you do now. If you are worried about negative weights, there is
> https://arxiv.org/abs/2505.03724. Maybe worth a quick comparison between what you have now and
> that in an appendix? If the unbinned approach works, let's make that the default?"

This answers the pending question in the analysis note §3.1 (`docs/analysis-note/sec_method.tex`,
the `\jrb` reply asking negative-weight vs purity-classifier vs T2K labels). The advisor picked
negative weights. The reference is Nachman & Noll, "Stay Positive: Neural Refinement of Sample
Weights" (arXiv:2505.03724) — a NN phase-space-dependent scaling + resampling protocol that turns a
signed-weight sample into an equivalent positive-weight one. Fetch and read it before implementing.

## WHAT WE DO NOW (the thing being replaced)
Per-reco-bin purity down-weight on the data side of OmniFold step 1:
`w_pur(b) = max(0, N_data(b) − N_bkg(b)) / N_data(b)` — binned on the analysis grid, ~3% overall,
the ONE place analysis binning enters before final histogramming (note §3.1 says exactly this).
Code:
- 2D: `2d-unfolding/unfold_2d_omnifold_unbinned.py` — `fill_bkg_reco_2d` (~line 248),
  `build_measured_training_2d` (~line 279; its docstring already discusses negative weights).
- ND: `nd-unfolding/unfold_nd_omnifold_unbinned.py` — `collect_bkg_nd` (~line 379),
  `build_measured_training_nd` (~line 459).
- Systematics wiring: per-universe bkg weight branches `w_bkg_<band>_<idx>` and lateral-universe
  bkg kinematic swaps (KNOWN_ISSUES #13 fix) flow through `collect_bkg_nd` — the new method must
  preserve this (universe-varied background must still vary the subtraction).
- Background events live in the omnifiles' `mc_background` tree: reco kinematics
  `sim_background(_pz/_eavail/_q3/_W)`, `sim_background_pass`, weight `w_bkg`, POT-scaled.

## THE PROPOSED METHOD (unbinned negative-weight injection)
Replace the binned purity weight by appending the background-MC reco events to the DATA side of the
step-1 training with weight `−w_bkg × pot_scale` (data events keep +1). The step-1 classifier
data-vs-simreco with signed weights then estimates the likelihood ratio against the
background-subtracted data density (D−B)/S — i.e. exactly the current correction, but continuous in
the full reco phase space instead of per-bin. Work out and document the estimator statement
carefully (what the weighted-BCE/logloss optimum converges to with signed weights) before coding.

Known risks to resolve, in order:
1. **LightGBM with negative sample weights** — it accepts them, but gradient/hessian contributions
   flip sign; verify on a toy (known D, B, S densities; check the learned reweight converges to
   (D−B)/S) before trusting it on data. If unstable → risk 2.
2. **Stay Positive fallback (2505.03724)** — refine the signed-weight measured sample into an
   equivalent positive-weight sample (their scaling + resampling protocol), then train as usual.
   Implement as a separate mode so the two variants can be compared.
3. **Locally negative effective density** (B>D in some reco region) — the current binned method
   floors at zero (`max(0,·)`); decide + document the unbinned analogue (clip the learned reweight
   at 0, or let Stay Positive handle it).

## PLAN (phases; STOP + report to user between 3 and 4)
1. **Design memo** (goes in bkg_negweight_state.md): estimator math; toy LightGBM signed-weight
   check (pure numpy/lightgbm toy, no ROOT needed).
2. **Implement in the 2D driver** behind a flag `--bkg-mode {purity,negweight,negweight-refined}`,
   default `purity` (headline path byte-identical when flag unset). 2D is the cheap validated
   sandbox (frozen benchmark total \sigma = 3.073e-38 cm^2/nucleon).
3. **Validate in 2D**: (a) closure with pseudo-data = sim reco + injected bkg (recovered/truth per
   bin, both modes); (b) real-data unfold negweight-vs-purity per-bin ratio map + totals (expect
   differences at or below the ~3% purity-correction scale, concentrated where bkg concentrates);
   (c) seed stability (a few reruns). Report the comparison table to the user.
4. **Port to the ND driver** (same flag; preserve the universe-varied bkg wiring) and run a 5D CV
   comparison. The real payoff is FPS, where the background treatment is larger (former kinematic
   fakes) — coordinate with the user before any FPS-scale rerun.
5. **Appendix draft** for the analysis note (`docs/analysis-note/`, new `app_negweight.tex` or a
   §3.1-adjacent appendix): method statement, the toy/closure evidence, the 2D data comparison,
   and the Stay Positive citation. Also rewrite the §3.1 `\jrb` reply to say the advisor chose the
   negative-weight route and point to the appendix. Reader-voice rules apply (no status language).
6. **Default switch is the USER's call** after seeing the comparison — do NOT flip the default or
   re-run headline products unilaterally.

## OPS CONSTRAINTS (school-session specifics — all proven the hard way, see fps_pipeline_state.md)
- Before ANY sbatch/salloc/alloc_run.sh that sources setup_salloc_env.sh:
  `export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28` (school's sandboxed $HOME
  breaks the default conda-prefix resolution for both sbatch AND interactive).
- 2D unfolds run in minutes-to-tens-of-minutes on a shared-QoS node or interactive allocation; no
  GPU needed anywhere in this study (GBDT only).
- Never scancel jobs another session started; personal memory dir is READ-ONLY for school;
- Commit ONLY when the user asks (straight to main, remote is `github`, Co-Authored-By trailer).
- Data files: 2D omnifile + data live where `2d-unfolding/unfold_2d_omnifold_unbinned.py`'s
  defaults point (check its argparse); do not regenerate event loops for this study.

## REFERENCES
- arXiv:2505.03724 — Stay Positive (the advisor's suggested robustness method).
- arXiv:2507.09582 — Practical Guide to unbinned unfolding: recommends negative-weight subtraction
  for nontrivial backgrounds, records no analysis that has used it (we'd be first).
- ATLAS Z+jets (2024) + Andreassen et al. — identify negative weights as the natural in-method
  subtraction; see LITERATURE_NOTES.md §background-subtraction and note §3.1 for the full survey.
- `nd-unfolding/bkg_channel_split.py` — recent per-channel background decomposition (useful for
  the appendix's "where the background lives" figure, if wanted).
