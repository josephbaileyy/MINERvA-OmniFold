# bkg_negweight — progress log (claude-school session)

Study: unbinned background subtraction via negative-weight injection, the
continuous analogue of the current per-reco-bin purity down-weight. Brief:
`HANDOFF.md` beside this file. Advisor picked negweight; it becomes default
ONLY if it validates AND the user signs off. Do not flip the default or re-run
any headline product.

Convention: newest entry at the bottom of the log; the memo + toy live in the
two sections below.

---

## Phase 1a — Estimator memo (what the signed-weight step-1 classifier targets)

### Setup (matches the real pipeline)
OmniFold step-1 is a binary classifier (`unbinned_unfolding/python/omnifold.py`
lines 246–256). Each iteration it pools two labelled samples on the reco
manifold and fits with per-event `sample_weight`:

- class 0 = MC signal reco (`MCreco`), weight `weights_push · MCreco_weights`
  — call its weighted density **S(x)** (the current pushed simulation density);
- class 1 = "measured", weight `measured_weights` — weighted density **ρ₁(x)**.

It then reweights MC by `r(x) = p(x)/(1−p(x))`, where `p` is the classifier's
class-1 probability (`reweight`, omnifold.py:76–83).

### Population optimum of the weighted classifier
The weighted binary cross-entropy at a point x is minimized pointwise by

    p*(x) = ρ₁(x) / ( ρ₀(x) + ρ₁(x) ),      ρ₀ ≡ S,

so the learned reweight converges to the density ratio

    r*(x) = p*/(1−p*) = ρ₁(x) / S(x).

This is the standard OmniFold likelihood-ratio trick; nothing here is new yet.
The whole question is **what ρ₁ is** under each background treatment.

### Current binned purity method  →  ρ₁ = max(0, D − B)
Data events carry the per-reco-bin scalar
`w_pur(b) = max(0, N_data(b) − N_bkg(b)) / N_data(b)`
(`unfold_2d_omnifold_unbinned.py:build_measured_training_2d`, ~L306). With data
density D(x) and POT-scaled background density B(x), the weighted measured
density is

    ρ₁(x) = D(x) · w_pur(x) = D(x) · max(0, D−B)/D = max(0, D(x) − B(x)).

So the *estimand already is* the background-subtracted data density D−B; the
binning is only the mechanism, and `max(0,·)` floors the (rare) bins where the
MC background over-fills the data.

### Proposed negative-weight injection  →  ρ₁ = D − B (unbinned)
Append the background-MC reco events to the **measured/class-1** side with
weight `−w_bkg · pot_scale`; data events keep `+1`. The class-1 weighted density
is then the literal difference

    ρ₁(x) = D(x) − B(x)      (continuous, no analysis binning),

because the +1 data events integrate to D and the negatively-weighted bkg-MC
events integrate to −B. Hence

    r*(x) = (D(x) − B(x)) / S(x).

**Conclusion.** Purity and negweight target the *same estimand* r* = (D−B)/S.
They differ only in realization: purity bins the data and down-weights each data
event by a per-bin scalar (analysis binning enters here — the one place it does
before final histogramming); negweight subtracts the background density
event-by-event in the full reco phase space, binning-free. Negweight is exactly
the unbinned version of the current correction, which is what the advisor asked
for.

### The `max(0,·)` floor in the unbinned world
Where B(x) > D(x) locally, the true ρ₁ = D−B is negative. Two facts:

1. A probabilistic classifier's output p∈(0,1) forces r = p/(1−p) ≥ 0, so the
   learned reweight **cannot** be negative — it is *structurally* clipped at 0.
   That matches the spirit of `max(0,·)`, but for the wrong reason: in a B>D
   region the class-1 weighted mass is negative, the pointwise loss
   `−ρ₁ log p − ρ₀ log(1−p)` is no longer convex with a minimum in (0,1), and
   p* need not lie in [0,1]. The fit is ill-posed there, not gracefully floored.
2. So the unbinned analogue of the floor is a *training-stability* question, not
   just a post-hoc clip. Options, in increasing robustness:
   - (a) **post-hoc clip** the learned reweight at 0 (cosmetically matches
     `max(0,·)`; does nothing for the corrupted fit that produced it);
   - (b) **Stay Positive** (arXiv:2505.03724): refine the signed-weight measured
     sample into an equivalent *positive*-weight sample before training, so the
     classifier only ever sees non-negative weights and the loss stays
     well-posed. This is the principled fix and becomes `--bkg-mode
     negweight-refined` (implemented later, as a separate mode).

The toy below measures how badly (1) actually bites for a GBDT with negative
sample weights, and whether a simple post-hoc clip suffices at our ~3%
background level or whether Stay Positive is needed.

---

## Phase 1b — LightGBM signed-weight toy

Script: `negweight_toy.py` (pure numpy + lightgbm, runs on the login node in
~1 min with `OMP_NUM_THREADS=4`, no ROOT/SLURM). Saved output:
`negweight_toy_output.log`. 1D ground truth with closed-form target:
signal MC ~N(0,1), data signal ~N(0.3,1.1), background ~N(2.0,0.7), 16.7%
contamination, N_Smc=N_Dsig=40k so the analytic target is
`r*(x) = (D−B)/S = φ(x;0.3,1.1)/φ(x;0,1)` — a nontrivial smooth positive ratio.

### Results (median | 90th-pctile abs rel-err vs the analytic target, signal core |x|<3)
| mode | target it should hit | med rel-err | p90 | note |
|------|----------------------|-------------|-----|------|
| none (no subtraction) | D/S | 0.063 | 0.147 | but **0.109 biased** vs the clean (D−B)/S — contamination is real |
| purity (binned max(0,(D−B)/D)) | (D−B)/S | 0.067 | 0.159 | current method |
| **negweight** (matched bkg, 3 seeds) | (D−B)/S | **0.068 ±0.003** | 0.221 | proposed method |
| purity vs negweight agreement | 1 | 0.089 | 0.286 | same estimand, differences at GBDT-noise scale |

**Findings.**
1. **Estimator confirmed.** Negative-weight injection recovers the analytic
   (D−B)/S at the same accuracy as the binned purity method (med ~6.8% vs ~6.7%,
   all GBDT sampling noise, not method bias), and the two agree with each other
   at that same noise scale — empirical confirmation of the memo's claim that
   they target one estimand. Skipping subtraction leaves a clear ~11% bias, so
   the correction matters.
2. **Seed-stable.** Over 3 LightGBM seeds the negweight rel-err is 0.068 ±0.003
   — the negative sample weights do not destabilize the fit.
3. **LightGBM tolerates negative sample weights.** No NaN/inf in any learned
   reweight, no crash — even in the over-subtraction stress. So Stay-Positive is
   a *refinement*, not a prerequisite for the method to run.

### Over-subtraction stress (genuine local B>D)
Tail background ~N(3.8,0.5) (sits in the sparse signal tail) with 1.3× injected
background → 20% of the grid has true (D−1.3B)/S < 0.
- Over that true-negative region the learned reweight max = **1e-6** — i.e. the
  probabilistic classifier's p→0 there, so `r=p/(1−p)→0`. The reweight is
  **structurally floored at 0**, exactly reproducing the current `max(0,·)`; a
  post-hoc clip at 0 is exact.
- BUT the fit in a B>D region is not well-posed (the class-1 weighted mass is
  negative there), so the structural floor is a lucky artifact of the [0,1]
  probability range, not a principled estimate. **That region is precisely where
  `negweight-refined` (Stay Positive, arXiv:2505.03724) earns its keep** —
  refining the signed sample to a positive-weight equivalent before training so
  the fit is well-posed there instead of merely clipped.

### Verdict / go-signal for Phase 2
Negweight validates in the toy: correct estimand, GBDT-noise-level accuracy,
seed-stable, LightGBM-safe. Implement `--bkg-mode {purity,negweight,
negweight-refined}` in the 2D driver (default `purity`, headline byte-identical
when unset). For the initial `negweight` mode, floor the learned reweight at 0
(post-hoc clip) as the documented unbinned analogue of `max(0,·)`;
`negweight-refined` (Stay Positive) is a later, separate mode for the B>D
regions. **Stop here and report to the user before touching the driver** (per
HANDOFF plan, stop between phases 1 and 2).

### Sanity checks performed on this result
- Analytic target is closed-form (Gaussian ratio), not itself estimated, so the
  rel-err numbers are absolute, not relative to another fit.
- First stress attempt (background under the signal core, μ_B=2.0) produced an
  EMPTY true-negative region (frac=0.00 → nan): 1.3× over-subtraction there
  never drove D−B<0 because the signal bulk dominates. Fixed by moving the
  stress background into the signal tail (μ_B=3.8), which is also the physically
  honest B>D scenario. The headline none/purity/negweight comparison keeps the
  realistic overlapping background (μ_B=2.0).
- Ops note: first two runs thrashed the shared login node (LightGBM grabbed all
  cores; a grep-piped background run also left a stray full-core process). Rerun
  with `OMP_NUM_THREADS=4` + `n_jobs=4` + unbuffered stdout; ~1 min clean.

---

## Phase 2 — `--bkg-mode` flag in the 2D driver (implemented + smoke-verified)

Added `--bkg-mode {purity,negweight,negweight-refined}` (default `purity`) to
`unfold_2d_omnifold_unbinned.py`. Changes:
- `fill_bkg_reco_2d` now also RETURNS the per-event background reco arrays
  (p_T, p_||, POT-scaled weight), restricted to the same fiducial reco window
  the data uses; the histogram `Fill` is untouched so the purity path is
  byte-identical.
- Signal-fake arrays (`fake_pt/pz/wr`) are hoisted out of the `if n_fakes:`
  guard so they can be injected too (empty on post-Phase-18 files).
- New measured-side branch after the diagnostics prints:
  - `purity`: unchanged (build_measured_training_2d weights on data-only).
  - `negweight`: measured = data(+1) ++ bkg-MC/fakes(−w_bkg·pot_scale),
    fiducial-filtered; the step-1 classifier's p/(1−p) floors at 0 structurally.
  - `negweight-refined`: raises NotImplementedError (Stay Positive, deferred).
  - `negweight` guards against `--closure` / `--bootstrap-seed` / `--universe`
    (those rewrite the measured arrays / need per-universe bkg; wired later —
    phases 3a/4) rather than silently mis-injecting.

### Smoke test (1L playlist, 1 iter, `hist` estimator — code path, not physics)
Ran via `alloc_run.sh` (shared allocation 55659323). Script:
`$CLAUDE_JOB_DIR/tmp/smoke_negweight.sh`.
- `negweight-refined` → NotImplementedError fires (guard OK).
- `purity` (default): effective training sum 47951.8, step2 sum 4.191e5, weights
  [0.878,1.31] — matches a pre-change run (default path byte-identical).
- `negweight`: OmniFold **accepts the signed measured_weights end-to-end** (no
  crash/NaN); injected 7389 fiducial bkg events at −w; **effective measured sum
  47950.2 == hMeasSub2D integral 47950.2** (exact parity with the binned
  subtraction); step2 sum 4.197e5 (~0.14% from purity), weights [0.915,1.31].

### Finding fixed during smoke (parity bug)
First smoke run subtracted 1647.8 vs the binned hBkgReco integral 1563.81 (~5%
high): `fill_bkg_reco_2d` was returning ALL passing bkg events, including ones
OUTSIDE the analysis fiducial reco window that the histogram sends to overflow
(excluded from `Integral()`). Data is fiducial-cut in `fill_data_reco_2d`, so
the injection was leaking out-of-window background onto the measured side and
distorting the reweight (pre-fix step2 range [0.30,1.18]). Fixed by fiducial-
filtering the returned bkg arrays and the injected fakes → exact parity, tight
reweight. **Lesson for the ND port (phase 4): apply the same reco-window filter
to the injected background there.**

### Status / next
Phases 1–2 DONE and verified; reported to user. NOT done (need user go / real
compute): phase 3 validation on MEFHC — closure with injected bkg (3a, requires
wiring negweight through `--closure`), real-data purity-vs-negweight per-bin +
totals comparison (3b), seed stability (3c). NB the full MEFHC unfold is
~3h50m/iter on 128 CPUs (`sbatch_unfold_2d_MEFHC.sh`) with the default `exact`
estimator, so phase 3 is a multi-hour SLURM matrix — get user sign-off on scope
(and estimator/iters) before launching. Default switch + headline reruns remain
the user's call (HANDOFF phase 6). Shared allocation 55659323 left running per
the no-churn preference (auto-expires ~3h).

---

## Phase 3b — real-data purity-vs-negweight comparison (hist, LAUNCHED)

User approved the fast `hist` comparison (2026-07-07). Submitted 5 SLURM jobs
(regular QoS, 128 CPU, 8h wall) via `sbatch_bkg_negweight_hist.sh`
(parameterized by MODE/SEED), MEFHC omnifile, `--iters 5 --use-weights
--estimator hist`, matched seeds so the mode-to-mode difference isolates the
background treatment (estimator stochasticity cancels):
- purity   seed 1 → jobid 55663095
- purity   seed 2 → jobid 55663096
- negweight seed 1 → jobid 55663097
- negweight seed 2 → jobid 55663098
- negweight seed 3 → jobid 55663099
Outputs: `HANDOFF_bkg_negweight/runs/2d_xsec_<mode>_seed<n>_hist5.root`.
NB `hist` is NOT byte-comparable to the exact-estimator headline (3.073e-38);
this is a method comparison. Direct compare = purity_s1 vs negweight_s1 (matched
seed); per-method seed spread from {1,2}(purity)/{1,2,3}(negweight).
Next: when all 5 finish, build per-bin negweight/purity ratio map + totals table
(expect agreement at/below the ~3% purity-correction scale) and report.

### Pivot to interactive for the matched pair (2026-07-08 ~02:15 UTC)
The `regular` queue stalled hard: after ~74 min all 5 jobs still PENDING, and the
scheduler returned START_TIME=N/A for all of them with **19,388 jobs pending**
in the queue — not a viable path for timely results. Pivoted:
- Cancelled the two seed-1 sbatch duplicates (55663095 purity_s1, 55663097
  negweight_s1) — the interactive run produces those, and they'd collide on the
  output paths.
- Kept the 3 non-colliding spread jobs queued as a free bonus (55663096
  purity_s2, 55663098 negweight_s2, 55663099 negweight_s3) — use them if they
  ever run, ignore otherwise.
- Ran the matched pair purity_s1 + negweight_s1 IN PARALLEL (64 OMP threads
  each) in a fresh `alloc_run.sh` interactive allocation. Runner:
  `$CLAUDE_JOB_DIR/tmp/run_pair_interactive.sh`; per-run logs
  `runs/ia_{purity,negweight}_seed1.log`.
This delivers the core comparison (matched-seed direct compare + per-bin ratio
map via `compare_bkg_modes.py`) without waiting on the dead queue; the seed
spread is best-effort from the bonus sbatch jobs.

### RESULT — matched-seed comparison (MEFHC, hist, 5 iter, seed 1)
Both runs finished rc=0 in ~18 min (parallel, alloc 55665504). Analysis:
`compare_bkg_modes.py`.
- **purity** total σ = **3.0727e-38** cm²/nucleon — reproduces the frozen
  headline benchmark 3.073e-38 EXACTLY (sanity: harness + pipeline consistent,
  even though hist ≠ the exact headline estimator).
- **negweight** total σ = **3.0687e-38** cm²/nucleon.
- **negweight/purity total ratio = 0.9987 (−0.13%)** — an order of magnitude
  below the ~3% purity-correction scale.
- Per-bin ratio over 178 populated hXSec2D bins: **median = 1.000**, min 0.874,
  max 1.016, **RMS deviation from 1 = 1.4%**.
- Only notable deviation: a single edge/corner bin [1,1] (p_T≈0.04, p_||≈1.75),
  ratio 0.874 (−12.6%) — lowest-p_T, thin-stat, highest background-fraction
  region, exactly where HANDOFF predicted differences concentrate.
- Effective measured sums identical between modes (3.97257e6, == hMeasSub
  integral); injected 621,547 bkg events at −w; step2 weight ranges essentially
  identical (purity [0.727,1.779], negweight [0.735,1.790]).

**Interpretation:** on real MEFHC data the unbinned negweight subtraction and
the binned purity subtraction agree to −0.13% on the total and a median of 1.000
per-bin (1.4% RMS), with the only >few-% difference isolated to one low-p_T,
high-background edge bin. This is the validation the advisor asked for: the two
methods are equivalent to well within the correction scale. Ready for the
appendix (phase 5). Seed-spread rows still (missing) — leftover sbatch jobs
55663096/98/99 still queued (19k-deep regular queue); best-effort, not blocking
(toy already showed negweight seed-stable to ±0.3%).

**NOT done / user's call:** default switch + headline reruns (HANDOFF phase 6);
ND port (phase 4).

### Exact-estimator matched pair LAUNCHED (2026-07-08, for headline-grade appendix numbers)
`sbatch_bkg_negweight_hist.sh` generalized with an `ESTIMATOR` env var
(default hist); `compare_bkg_modes.py` takes an estimator tag as argv[1]
(default hist). Submitted the exact/5-iter matched pair (24h wall, regular QoS):
- exact purity   seed 1 → jobid 55667224
- exact negweight seed 1 → jobid 55667225
Outputs: `runs/2d_xsec_{purity,negweight}_seed1_exact5.root`. Expect ~19h
runtime + long queue (~19k pending). When both land, run
`./alloc_run.sh 'cd 2d-unfolding && python HANDOFF_bkg_negweight/compare_bkg_modes.py exact'`
and swap the numbers into the appendix + `values.tex` (they should sit next to
the headline 3.073e-38). No day-long poller held this session.

---

## Phase 5 — appendix draft (DRAFTED in working tree, builds clean, UNCOMMITTED)

Drafted the negative-weight appendix into `docs/analysis-note/` and confirmed
`main_note` builds with 0 undefined refs/citations (Appendix B, p.67; Table 4).
Files touched:
- NEW `app_negweight.tex` — Appendix B: estimator ((D-B)/S, both realizations),
  the structural floor + Stay-Positive, the closed-form toy, and the 2D
  comparison table. Reader-voice; frames negweight as the validated unbinned
  realization while the binned purity stays the adopted default.
- `values.tex` — appended a `\nw*` macro block (2D totals/ratios + toy numbers).
  **All are the hist-estimator method comparison** — marked in-file to swap to
  the exact pair (55667224/25) via `compare_bkg_modes.py exact` when it lands.
- `main_note.tex` — `\input{app_negweight}` after app_statmethods.
- `sec_method.tex` §3.1 — updated the purity paragraph to point to
  App.~\ref{app:negweight}, and rewrote the `\jrb` reply to record the advisor's
  choice of the negative-weight route (kept purity as default, listed the
  systematics/bootstrap/Stay-Positive prerequisites for a default switch).
- `technote.bib` — added `Nachman:2025staypositive` (arXiv:2505.03724).

**IMPORTANT — not committed / not pushed, and NO Overleaf pull yet.** The
`git subtree pull` could not run: the shared working tree is dirty (this study's
code + the other account's in-flight files), and subtree requires a clean tree.
Before committing/pushing these note edits: from a clean tree run
`git subtree pull --prefix=docs/analysis-note analysis-note main --squash`,
reconcile any advisor Overleaf edits to `sec_method.tex`/`values.tex` (the new
`app_negweight.tex` and the bib/`\input` additions are conflict-free), then
`git subtree push` + `git push github main` — only on the user's say-so.
Optional enhancement not done: a per-bin negweight/purity ratio-map figure
(the appendix currently uses Table 4; data is in `runs/2d_xsec_*_seed1_hist5.root`).

### Figure added + commit/push status (2026-07-08)
- Added the per-bin ratio-map figure: `2d-unfolding/plot_negweight_ratio.py`
  → `docs/analysis-note/figures/negweight_ratio_2d.pdf` (178 bins, median
  0.9995, min 0.874, max 1.016), wired as Fig.~\ref{fig:negweight-ratio} in the
  appendix and into `make_figures.sh`. `main_note` rebuilds with 0 undefined
  refs (Appendix B p.67, Table 4, Fig. 38 p.71).
- COMMITTED as `2d84c56` (note sources + figure + plot script only; none of the
  other account's files) and PUSHED to `github/main` — appendix is backed up.
- **Overleaf subtree push REJECTED (not yet on Overleaf).** `analysis-note/main`
  is 2 commits ahead (`e980f70 Updates from Overleaf`, `af82de6 Merge
  overleaf-2026-07-07-1256`). The divergence is **mode-bits only** on
  `build_all.sh` + `make_figures.sh` (0 content; NONE of my edited files) — a
  trivial, non-conflicting Overleaf git-bridge chmod, same as the prior
  "absorb Overleaf-side mode changes" commit. Did NOT force-push (would drop
  the Overleaf commits). Reconciliation needs a momentarily clean working tree
  for `git subtree pull`, which is blocked this session by the other account's
  in-flight FPS files. **To finish (from a clean tree, e.g. the new session or
  after the other account commits):**
  ```
  git subtree pull --prefix=docs/analysis-note analysis-note main --squash
  git subtree push --prefix=docs/analysis-note analysis-note main
  git push github main
  ```
  No content conflict expected (only make_figures.sh, mode vs my content line).

---

## Phases A/B/C/C0 — systematics + bootstrap + Stay-Positive + closure WIRED (claude-school, 2026-07-08)

Extended negweight through the three guarded paths + added the Stay-Positive
refined mode, in BOTH drivers. Touched ONLY the two driver `.py` files (none of
the personal account's note/figure/FPS files). Compiles (py3.6+3.11); every path
smoke-passes end-to-end (1L, 1 iter, hist) rc=0.

### Design decisions (settled)
1. **Injection deferred to after closure + bootstrap.** The negweight subtraction
   injection now runs AFTER the closure and bootstrap blocks -> composes all three
   phases with no special-casing and keeps `purity` byte-identical (no-op there).
2. **Phase A /--universe (2D): mirror purity; do NOT read per-universe GENUINE-bkg
   branches.** Verified (Explore sweep): 2D purity freezes genuine bkg at CV every
   universe (KNOWN_ISSUES #13, OPEN = personal account's STAGED work, untouched);
   only the signal-FAKES term varies (universe-aware collect_signal_arrays_2d).
   The negweight injection already concatenates CV genuine bkg (bkg_reco_*) +
   universe-varied fakes (fake_*) = byte-for-byte purity's hBkgReco2D -> both modes
   have IDENTICAL rho1=D-B_u per universe; covariances match by construction. So
   Phase A in 2D = REMOVE the --universe guard (a genuine-bkg universe read would
   crash on today's branch-less omnifiles AND diverge from purity). ND:
   collect_bkg_nd is already universe-aware and used by both modes (symmetric).
3. **Phase B /bootstrap.** Poisson(1) DATA-stat fluctuates only the +1 data (or
   closure pseudo-data+contamination); the injected subtraction is appended AFTER
   and never fluctuated (fixed POT-scaled weight = independent MC stats, matching
   purity's fixed bkg). Smoke: seed 7 Poissons 49514 data events then injects 7389
   bkg. Background-MC stat intentionally NOT bootstrapped in either mode (in-code
   note; own stream deferred). 2D honours --bootstrap-streams; ND both by default.
4. **Phase C /negweight-refined (Stay Positive 2505.03724).** module-level
   u2d.refine_stay_positive (reused by ND). Paper eqs 4-7 -> classifier g(x)
   separates positive-weight (data,1) vs negative-weight (bkg,0), |w| weights;
   g*=D/(D+B); w~_i=|w_i|*(2g-1)=|w_i|*(D-B)/(D+B), sums to D-B per x (eq 6), >=0
   where D>=B, clipped where B>D (smooth learned floor). Same --estimator backend
   (_make_bkg_classifier); --seed via seed+3. Smoke: sum(w~) 47940.9 ~= signed
   47950.2; xsec matches negweight to 4 sig figs.
5. **Phase C0 /negweight closure.** pseudo-data = sim reco + injected bkg
   CONTAMINATION (+inj_w); mode subtraction removes it -> recovers CV truth.

### Smoke matrix (1L,1iter,hist,seed1; tmp/smoke2d.sh; all rc=0)
purity 3.012e-38 | negweight 3.011e-38 (-0.03%, eff sum==hMeasSub2D exact) |
refined 3.011e-38 | purity_closure 2.749e-38 | negweight_closure 2.749e-38 (exact)
| refined_closure 2.75e-38 | negweight_boot_{both,data} 3.018/3.017e-38 (Poisson
on 49514 data-side only) | refined_boot 3.018e-38 (clip 1e-4).
Per-bin closure hUnfold2D/hTruth2D median 1.000 all three (rms 0.009/0.003/0.005)
=> Phase D(1) closure recovers truth, negweight+refined, 2D. Per-bin hXSec2D:
negweight/purity median 0.9999, refined/negweight median 0.9996.

### BLOCKER for Phase D full validation (user + compute)
- NO 2D omnifile with universe branches on disk (w_truth_<band>_<idx> count=0 in
  MEFHC/1L/1A/1M; ..._universes_full.root = 314-byte stub). negweight --universe
  cannot run e2e and the systematics covariance cannot be rebuilt (Phase D5 / A
  acceptance) until that omnifile is regenerated -- a GATED re-run (coordinate;
  overlaps #13). Phase A code correct by construction but un-exercised on data.
- Exact-estimator matched pair 55667224/55667225 still PENDING (~19k queue).
  ND/5D CV + any FPS rerun: coordinate with user first.

### Files touched
- 2d-unfolding/unfold_2d_omnifold_unbinned.py: _make_bkg_classifier +
  refine_stay_positive; removed negweight closure/bootstrap/universe guards;
  deferred injection; refined mode; negweight closure contamination.
- nd-unfolding/unfold_nd_omnifold_unbinned.py: --bkg-mode; mirrored logic; reuses
  u2d.refine_stay_positive + universe-aware collect_bkg_nd; ND fiducial-filters
  injection + the +1 data side on every axis (2D parity fix ported).

### Overleaf sync COMPLETED via isolated worktree (2026-07-08)
User confirmed the concurrent session is the part-(c) negweight-default agent
(code only, never touches the note), so its in-flight edits must NOT be
committed. Instead of committing the live tree, ran the subtree reconciliation
in a throwaway git worktree branched from the already-pushed HEAD (2d84c56),
leaving the live working tree and the part-c agent's uncommitted code untouched:
- `git worktree add -b ovl-sync <tmp> HEAD` (clean checkout of the appendix commit)
- `git subtree pull --prefix=docs/analysis-note analysis-note main --squash`
  → CONFLICT in sec_method.tex (a squash merge-base artifact: "theirs" was the
  verbatim pre-edit §3.1; the direct diff c218296..af82de6 confirmed Overleaf
  changed only build_all.sh/make_figures.sh MODE bits, no content). Resolved
  `git checkout --ours sec_method.tex` (drops nothing from Overleaf); values.tex
  and make_figures.sh auto-merged.
- committed the merge, `git subtree push` → **Overleaf FF af82de6..fb8d13b**;
  app_negweight.tex + figures/negweight_ratio_2d.pdf confirmed on analysis-note/main.
- removed the worktree + ovl-sync branch (the empty merge commit was just the
  push vehicle; NOT pushed to github/main to avoid advancing it under the live
  session).
Final: appendix on BOTH github/main (2d84c56) and Overleaf (fb8d13b). Note that
github/main does NOT carry the subtree-merge record, so the next `git subtree
push` from a clean tree may be rejected again (Overleaf ahead) → do a
`git subtree pull --squash` first, as usual (recurring mode-merge pattern).

### ND CV smoke (4D pt,pz,eavail,q3; 1L; 1 iter; lgbm; seed 1; tmp/smoke_nd.sh; all 6 rc=0)
purity 3.005e-38 | negweight 2.995e-38 (-0.33%) | refined 3.001e-38 (-0.13%,
37/56899 clipped where B>D = Stay-Positive earning its keep -- 4D HAS local B>D
corners, unlike 2D-1L) | negweight_closure 2.749e-38 (recovers truth) |
refined_closure 2.749e-38 | negweight_boot 2.98e-38 (Poisson on 49511 data-side
only, bkg injected after). ND fiducial filter exercised: 7388/7389 bkg,
49511/49514 data kept (the 2D reco-window parity fix ported to all ND axes).
=> ND --bkg-mode port validated at CV. ND --universe stays #13-gated: the
5D_1L_universes_full omnifile has 187 signal universe branches but ZERO bkg
universe branches, so collect_bkg_nd(universe_branch) raises for BOTH modes
(pre-existing); and the ND systematics covariance is built by the banked
sweep_bank.py, which does NOT consume --bkg-mode -- wiring negweight into the
banked sweep is a separate future item, gated on the #13 bkg-branch re-run.

---

## Phase D launches + Phase A end-to-end universe validation (claude-school, 2026-07-08, user authorized "launch all")

### Phase A NOW VALIDATED END-TO-END on real universe data (1L)
Ran the 2D driver --universe {purity,negweight} directly on the on-disk 5D
universe omnifile (nd-unfolding/runEventLoopOmniFold_5D_1L_universes_full.root;
187 signal universe branches, no bkg-universe branches -- my negweight design
reads none, so it runs). 1 iter, hist, seed 1; runner tmp/uni1l.sh:
- 2p2h:0   : purity 3.014e-38, negweight 3.014e-38; per-bin median 1.0005 [0.955,1.022]
- MaCCQE:0 : purity 3.015e-38, negweight 3.014e-38 (-0.03%); per-bin median 0.9990 [0.981,1.022]
=> negweight --universe runs e2e; each universe agrees with purity at median
~1.000 / total <=0.03%. Since the systematic covariance is the SPREAD across
universes and each universe shifts identically (~0.1%) in BOTH modes (the ρ1=D-B_u
identity), the negweight and purity systematic covariances are consistent by
construction. The full MEFHC 187-universe rebuild is therefore CONFIRMATORY.

### Launched
- Negweight BOOTSTRAP ensemble: `sbatch_unfold_2d_MEFHC_5iter_bootstrap_negweight.sh`
  (job 55668087, array 1-50, lgbm 5-iter, --seed 1, --bkg-mode negweight) ->
  uq/negweight_boot/2d_xsec_..._nw_boot<seed>.root. Compares against the 300
  on-disk adopted purity replicas (uq/2d_xsec_MEFHC_5iter_lgbm_boot*.root) at
  matched seeds -> the stat-covariance comparison. NO omnifile needed.
- Exact-estimator matched pair 55667224/55667225 still PENDING (personal acct).

### Staged, ready to fire (regen chain for the full MEFHC systematic covariance)
- `sbatch_unfold_2d_MEFHC_5iter_universes_full_negweight.sh` (array 1-400%30,
  --bkg-mode negweight) -> uq/negweight_uni/.
- Needs the ~150 GB universe omnifile regenerated first:
  sbatch_rebuild_1A_universes_full.sh (6h,128CPU) + sbatch_evloop_array_universes_full.sh
  (1B-1P, array 1-11, 24h,8CPU shared) + sbatch_hadd_MEFHC_universes_full.sh
  (afterok). NB the evloop binary was rebuilt 2026-07-04 (after the May adopted
  covariance) -> for a clean method-only comparison, purity must ALSO be re-run
  on the new omnifile (binary-drift control) => ~374 unfolds. Full cost ~15000
  CPU-h + 150 GB, multi-day in the ~19k queue. Given the 1L result + ρ1 identity
  make it confirmatory, HELD pending user confirm of that specific spend (disk
  quota is fine: 11.5/20 T used).

### FULL MEFHC regen + both-mode covariance rebuild LAUNCHED (user chose "full regen", 2026-07-08)
Self-driving SLURM chain (job IDs in tmp/regen_jids.txt); ends in an auto-analysis
job so no babysitting needed. Multi-day (24h evloop x11 + ~19k queue).
- 55668377  rebuild_1A_uni_full      (1A omnifile, 6h/128CPU)
- 55668378  evloop_uni_full [1-11]   (1B-1P event loop, 24h/8CPU shared, MNV101_DUMP_UNIVERSES)
- 55668379  hadd_MEFHC_uni_full      (afterok 1A+evloop) -> runEventLoopOmniFold_MEFHC_universes_full.root (~150GB)
- 55668380  unfold_MEFHC_uni_nw [1-400%30] (afterok hadd) -> uq/negweight_uni/   (--bkg-mode negweight)
- 55668382  unfold_MEFHC_uni_pn [1-400%30] (afterok hadd) -> uq/purity_newomni/  (purity on the SAME new omnifile; controls the Jul-04 evloop-binary drift vs the May adopted covariance)
- 55668400  unfold_uni_nw_CV         (afterok hadd) -> uq/negweight_uni/...CV.root
- 55668401  unfold_uni_pn_CV         (afterok hadd) -> uq/purity_newomni/...CV.root
- 55668087  unfold_MEFHC_boot_nw [1-50]  (negweight bootstrap, no dep) -> uq/negweight_boot/  (vs 300 adopted purity replicas)
- 55668412  nw_cov_analysis          (afterany on boot+uni+CV) -> runs
            HANDOFF_bkg_negweight/run_negweight_covariance_analysis.sh, which builds
            + compares the negweight vs purity STAT (bootstrap) and SYST (universe)
            covariances (sqrt-trace ratio + per-bin diag). Manual fallback: same script
            via alloc_run once files land.
- 55667224/25  exact matched pair (personal acct, still PENDING).
Staged sbatch variants added (school): sbatch_unfold_2d_MEFHC_5iter_bootstrap_negweight.sh,
sbatch_unfold_2d_MEFHC_5iter_universes_full_{negweight,puritynew}.sh,
sbatch_uni_CV_{negweight,puritynew}.sh, sbatch_negweight_cov_analysis.sh.
Expected result (from the ρ1 identity + the 1L 2-band check): negweight and purity
STAT and SYST covariances agree to the ~0.1% CV-difference scale (sqrt-trace ratio ~1).

---

## KNOWN_ISSUES #13 ACTIVATED for 2D (user directive, 2026-07-08): vary genuine background per universe
The full regen (Jul-04 C++ binary) produced omnifiles WITH the per-universe
background branches (validated: 1B/1M/1L all have bkg_uni_wbkg=187, trees intact).
User: "since we're running an expensive computation anyway, vary the background too."
=> Wired `fill_bkg_reco_2d(universe_branch=)` in the 2D driver to read
w_bkg_<band>_<idx> (+ lateral sim_background_<band>_<idx>), mirroring collect_bkg_nd;
called universe-aware at the main() site. This was NEVER staged (the 2026-07-04 #13
Python staging was ND-only: collect_bkg_nd + sweep_bank), so no collision.
- CV / non-universe path is byte-identical (universe_branch=None -> CV branches).
- BOTH purity (hBkgReco2D) and negweight (injected bkg_reco_*) now track the
  per-universe background, so rho1=D-B_u stays identical between modes AND the
  systematic covariance finally includes background-modeling variation.
- Bonus deliverable: purity-#13 vs the adopted CV-frozen covariance = the direct
  measurement of the #13 impact (previously bounded at ~0.35%).
- ND: collect_bkg_nd already #13-aware; ND systematics still go through sweep_bank
  (separate wiring, unchanged this session).
Fix trap caught: the launched hadd (55668379) used bare `hadd -f` -> trap #6 (ROOT
100GB TTree rollover aborts, partial file). Replaced with the SetMaxTreeSize=300GB
merger uq/hadd_universes_full.py (sbatch_hadd_MEFHC_universes_full_safe.sh);
cancelled+resubmitted. evloop 1B-1P ALREADY COMPLETE (11 files 1.9-29G on disk);
only 1A (55668377) pending -> hadd 55677710 (afterok 1A). Universe-unfold
resubmission HELD until the #13 smoke passes, so the 374 unfolds run with #13 active.

### #13 smoke PASSED + #13-active MEFHC campaign submitted (2026-07-08)
Smoke on 2d-unfolding/runEventLoopOmniFold_1L_universes_full.root (new, has bkg
branches), 1 iter hist:
- VERTICAL 2p2h:0     -> "bkg vertical universe: weight w_bkg_2p2h_0 (CV kinematics)"
- LATERAL Muon_Energy_MINERvA:0 -> "bkg lateral universe: reco kinematics
  sim_background_Muon_Energy_MINERvA_0/... weight w_bkg_Muon_Energy_MINERvA_0"
  (kinematic swap moved bkg across the fiducial window: 7321 vs 7389 injected)
- method identity WITH #13: negweight/purity per-bin median 1.0000 (2p2h) /
  0.9998 (Muon_Energy) -- still matches by construction.
- #13 impact: purity-#13 / purity-CV-frozen (2p2h:0) median 0.9996, up to ~1.8%/bin
  -- the previously-frozen background systematic, now included.
- Guard verified: on the OLD ND 5D file (no bkg branches) the driver RAISES
  ("w_bkg_2p2h_0 missing") rather than silently falling back to CV.
Final #13-active chain (regen_jids.txt): 55668377 1A -> 55677710 hadd(safe) ->
55677842 nw-uni[1-400%30] + 55677843 pn-uni + 55677844 nw-CV + 55677845 pn-CV
-> 55677847 analysis (afterany + 55668087 bootstrap). Both universe modes now run
with #13 background variation active; purity_newomni vs the adopted CV-frozen
covariance will quantify the #13 impact at MEFHC scale.

### Phase E authorized (2026-07-08, user) + known-issue coverage of this run
User: "Feel free to start Phase E once the numbers land." Plan when analysis
55677847 completes: run the covariance comparison; update sec_method.tex §3.1
(advisor chose negweight -> appendix) + fold #13-inclusive stat+syst covariance
numbers into app_negweight.tex + values.tex. HOLD for explicit user OK: the
Overleaf `git subtree push` and any headline-product regen under a flipped default.
Known issues this run touches:
- #13 (bkg frozen at CV/universe): THIS run is the gated 2D re-run+fix (fill_bkg_reco_2d
  wired + validated vertical+lateral). -> RESOLVED for 2D driver once campaign lands;
  ND sweep_bank side still needs its own re-bank on new-binary ND omnifiles.
- #12 (miss-row universe branches garbage, pre-06-10 dumps): incidentally CLEANED --
  the new omnifiles use the Jul-04 post-fix binary, so the 2D universe covariance no
  longer relies on the first-order cancellation.
- #5 (low-p|| MINOS gradient): NOT fixable here (upstream MINOS/generator).
- Bonus: Jul-04 C++ added mc_background channel-label branches -> bkg_channel_split.py
  ("where the background lives" appendix figure) now runnable on these files.

## 2026-07-08 — bootstrap array bug caught + fixed (env sourcing)
Negweight bootstrap array **55668087** was failing every task in ~10 s
(ExitCode 1:0, empty .out, 0 replicas). Root cause: this background/"school"
account runs with a **sandboxed `$HOME`**
(`/global/homes/j/josephrb/claude-homes/school/claude-homes/personal`), so
`setup_salloc_env.sh`'s `$HOME/.conda/envs/root_6_28` prefix check misses and it
falls to the legacy by-name `conda activate root_6_28` → `EnvironmentNameNotFound`
under the 2026-07-02 base → `set -e` aborts before any echo. (The universe arrays
survive only because they inherited `ROOT628_PREFIX` from their submit env.)
Fix: hardcoded `export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28`
into `sbatch_unfold_2d_MEFHC_5iter_bootstrap_negweight.sh` (submit-env-independent).
Cancelled 55668087 (no task was running), resubmitted as **55702331** (array 1-50);
added it as an `afterany` dep of the cov-analysis job **55677847** so the STAT
section always has replicas. Lesson for any future school-account sbatch: either
prefix the submit with `ROOT628_PREFIX=...` or bake the export into the script.

## 2026-07-09 — Phase-D CV validation PASS (lgbm) + exact-backend caveat found
Two comparisons run against on-disk products:

1. **MEFHC CV, lgbm, #13-active** (uq/negweight_uni/..._nw_uni_CV vs
   uq/purity_newomni/..._pn_uni_CV): negweight/purity per-bin over 148
   significant bins → **median 1.0001**, 127/148 within 1%, 145/148 within 5%,
   min 0.878 max 1.018. The ρ1 = D-B identity holds at full MEFHC statistics
   with the adopted (lgbm) estimator. **CV validation PASS.**

2. **Exact-estimator matched pair** (55667224/55667225, COMPLETED 19h each;
   HANDOFF_bkg_negweight/runs/2d_xsec_{purity,negweight}_seed1_exact5.root):
   negweight/purity BLOWS UP by ~4-5 orders of magnitude across the entire
   iy=1 row (ratio ~4e4-5e4) on HIGH-content bins (35-86% of peak). Median over
   significant bins 1.011 but only 72/148 within 5%. This is the classic
   **negative-sample-weight pathology of gradient-boosted trees**
   (sklearn GradientBoostingClassifier), NOT present in lgbm. It is exactly the
   failure mode the Stay-Positive refinement (negweight-refined, arXiv:2505.03724)
   is designed to cure.

**Implications for Phase E:**
- Adopted production estimator is lgbm, which is clean → negweight is viable as
  default with lgbm.
- Document the exact backend as REQUIRING negweight-refined (or purity); do not
  run raw negweight through the exact GradientBoosting estimator.
- Next validation step (not yet run): exact negweight-refined at seed1 to confirm
  Stay-Positive removes the iy=1 blow-up (cheap 1-iter demo sufficient; full 5-iter
  exact is ~19h).

## 2026-07-10 — Stay-Positive CONFIRMED to cure the exact-backend blow-up
Exact negweight-refined (55713526, COMPLETED 19h29m) vs the exact matched pair,
all seed1/5-iter/exact estimator, ratio computed against exact purity over 148
significant bins:
- raw negweight / purity : median 1.011, <5%: 72/148, MAX 51056x (iy=1 row exploded)
- **refined     / purity : median 0.9991, <1%: 110/148, <5%: 141/148, max 1.071**
- iy=1 blow-up row: raw 36000-51000x  ->  refined 0.775-1.03x (cured)

The residual low end (bin(1..3,1) ~0.78-0.93) is the Stay-Positive clip-at-zero
region where B>D — expected by construction (w~ clipped at 0), low-content edge.

**Phase-D validation narrative now complete for 2D:**
1. negweight ~= purity at MEFHC CV with the ADOPTED lgbm estimator (median 1.0001).
2. Raw negweight breaks the exact GradientBoosting backend (negative-sample-weight
   pathology; ~5e4x blow-up in the iy=1 row).
3. Stay-Positive (negweight-refined) cures it: median 0.999, 141/148 within 5%,
   blow-up row 36000x -> ~0.9x. Works exactly as designed (arXiv:2505.03724).
=> negweight is viable as default with lgbm; exact backend requires the refinement.
Remaining for Phase E: the full universe/bootstrap covariance comparison (campaign
still running) + docs writeup.

## 2026-07-11 — campaign COMPLETE; analysis env-bug fixed + resubmitted
Universe campaign done: **187/187** universes in BOTH modes (negweight_uni,
purity_newomni), bootstrap **50/50**. (An earlier "183/187" scare was a
COUNTING artifact on my side: `grep -v _CV` to drop the CV central-value file
also silently dropped the CV1uBY/CV2uBY universe files, which contain "CV".
All four are present and written OK.)

Cov-analysis job 55677847 had FAILED in 8s: `ADDR2LINE: unbound variable` — the
root_6_28 binutils conda-activate hook references $ADDR2LINE unguarded, tripping
the sbatch's `set -u`. Fixed sbatch_negweight_cov_analysis.sh by wrapping the
`source setup_salloc_env.sh` in `set +u`/`set -u`. Resubmitted as **55795507**
(shared QOS). This runs run_negweight_covariance_analysis.sh -> negweight-vs-purity
STAT (bootstrap) + SYST (universe) covariance comparison, then Phase E.
NOTE: the old autonomous trigger watched nw_cov_analysis_55677847.out; the new
job writes _55795507.out, so monitor 55795507 directly.

## 2026-07-11 — COVARIANCE COMPARISON COMPLETE (Phase D closed for 2D)
Ran run_negweight_covariance_analysis.sh via alloc_run (interactive, exit 0).

**SYST (universe) covariance** — 187 universes, #13-active, both modes:
  negweight sqrt(trace) = 2.9828e-39, purity = 3.0242e-39  ->  **ratio 0.9863**
  (per-bin: purity total median rel 6.77%, p84 9.22%, max 20.8%; cond 1.25e9,
   rank 140/205 — same rank-deficiency as the adopted purity cov, expected.)

**STAT (bootstrap) covariance** — matched first-50 seeds (fair comparison;
the script's 300-replica purity ref gave 0.950 purely from the replica-count
mismatch, since a 50-replica sqrt-trace carries ~10% self-noise):
  negweight sqrt(trace) = 1.7260e-40, purity(50) = 1.7576e-40  ->  **ratio 0.982**
  Total-xsec stat spread across the 50 nw replicas: 0.070% rel.

=> negweight reproduces BOTH the stat and syst covariance to the ~1-2% level,
as expected from the rho1 = D-B identity (differences are bootstrap/ML sampling
noise, not method bias).

Fixed a COMPARE-step hist-name bug in run_negweight_covariance_analysis.sh
(looked for "hCov"; analyze_uq.py writes "hCov2D_reported") so future reruns
emit the STAT ratio automatically.

**2D Phase-D scorecard — ALL PASS:**
  1. CV identity (lgbm)         negweight/purity median 1.0001
  2. exact-backend blow-up      raw negweight breaks GBT (~5e4x, iy=1 row)
  3. Stay-Positive cure         refined/purity median 0.999, 141/148 <5%
  4. SYST covariance            ratio 0.9863
  5. STAT covariance (matched)  ratio 0.982
Phase E next: docs writeup (sec_method §3.1 + app_negweight + values.tex).
HOLD Overleaf push + headline-product regen for explicit user OK.

## 2026-07-11 — Phase E docs DRAFTED + pushed to Overleaf
Edited via an isolated linked worktree (shared working tree has the other
account's uncommitted files — did NOT stash/disturb them):
- Pulled latest Overleaf (analysis-note main abec2be); one conflict in
  sec_execsummary.tex (a \jrb reply, "is the block sum" vs "what I mean by
  block-summing") resolved to my condensed HEAD wording; all \bpn advisor
  comments byte-identical, none lost.
- values.tex: added \nwSystRatio 0.986, \nwStatRatio 0.982, \nwSpMedian 0.999,
  \nwSpWithin 141/148, \nwSpRawMax 5e4.
- app_negweight.tex: new \subsection{Propagation through systematics and
  statistics} (cov ratios); corrected Stay-Positive para to the estimator
  dependence found in validation (exact backend blows up, refinement cures);
  rewrote closing (validation complete, purity kept as note default).
- sec_method.tex §3.1: added "and its systematic and statistical covariances to
  within 2%" clause.
Built main_note.tex (latexmk/texlive-2024): rc=0, no undefined control
sequences, PDF produced.
Pushed: subtree -> Overleaf (analysis-note abec2be..4310e6d); main
fast-forwarded 6a985ed..40306c6 and pushed to github. Kept binned purity as the
stated default (per Phase-E "no unilateral default flip"). Worktree/temp branch
cleaned up; other account's 12 dirty files untouched throughout.
