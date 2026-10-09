# Session 5 (gbdt) — 5D GBDT successor: a discriminating next design

**CITABLE FOR:** the saved-output reductions in `results.json` (each traced to a committed operand),
the ranking of the three explanations with their evidence, the proposed diagnostic D-ID and its
preregistration-ready design (§6), two conditional intervention specifications (§7), the cost and
feasibility arithmetic (§9), and the route table (§10).
**NOT CITABLE FOR:** a measured cross section, an uncertainty, a coverage result, a ratified gate,
compute authority, an adopted estimator or any regrading of s5c/s5n/s5e/s5p. The 10% width, 5%
allowance and 0.63/0.92 coverage figures used below are **proposals, not gates**. The publication-ready
measurement objective is **not** achieved by this lane.

| field | content |
|---|---|
| `Lane` | Session 5, gbdt |
| `Decision` | What new evidence could distinguish repairable estimator bias from weakly constrained truth directions, and is one small successor development experiment justified? |
| `Branch` / `Base` / `Head` | `prep/next-gbdt-20261009` / `5ac9706a21e8a5ac8863a65fd7623d8ab8d22269` (the common merged baseline; it supersedes `901f0088`/`8eafd357` by the dispatch override; `origin/main` was equal to it at 2026-10-09T19:59Z) / the commit that adds this file; the frozen reviewed commit is named in `Review` |
| `Owned files` | `docs/orchestration/state/next-preparation-20261009/gbdt/REPORT.md`, `reduce_saved_outputs.py`, `results.json`, `comparator.py`, `test_comparator.py` (all in that directory; nothing else written) |
| `Pinned inputs` | §2 table (sha256 prefixes; full digests in `results.json` `integrity`) |
| `Resources` | §12: elapsed and CPU measured; scratch < 5 MiB; tracked ≈ 0.12 MiB; **cluster 0, GPU 0, training 0** (one read-only `ls` on a login node, §2) |
| `Review` | §11 |
| `Model / effort` | Owner: Claude Opus 5.5 (`claude-opus-5-5`), the identity this session reports; effort not observable. Reviewer: §11 |
| `Disposition` | §13: **D1 PASS** (D-ID designed and ready for a resource decision); **D2 FAIL** for the old ~70-node-hour panel as the next step; **D3 FAIL against the proposed targets** for the present estimator and the frozen-procedure validation route; overall objective **unmet** |
| `Next action` | §14: Joseph's resource decision on D-ID (≤ 6.25 local CPU core-hours admitted, 1.44 GiB read-only copy of one existing file, 0 GPU, 0 training), plus the endpoint-scope question in §10.3 |

## 0. Setup (campaign-review choice)

One owner (this session) and one fresh read-only reviewer on a frozen commit in an isolated worktree,
one initial review and one focused re-review after a single repair batch, per the dispatch. The decision
is the one above. Terminal outcomes: PASS / FAIL / INCONCLUSIVE per decision, with a demonstrated no-go
counted as completion. Budget: Goal 5's caps (6 h elapsed, 2 local CPU core-hours, 2 GiB scratch, zero
cluster/GPU/training), with the last quarter held for verification and delivery. No other agents, no peer
messages. This follows the review's bounded-artifact pattern
([`CAMPAIGN-REVIEW-20260929.md`](../../../CAMPAIGN-REVIEW-20260929.md) §6) and claims no model advantage.

## 1. What this lane did and did not do

- **Did:** read-only verification of the synthesis operands, eight new saved-output reductions,
  synthetic tests of a reference comparator, design and cost arithmetic, one `ls` of the named cluster
  inputs, and this report.
- **Did not:** fit, train, unfold, toy, resample, run oracle substitutions or hyperparameter trials,
  submit jobs, use a GPU, copy event data, edit any record outside `Q/gbdt/`, or reopen a terminal
  campaign. Every existing output used is development evidence.

## 2. Inputs, pinned and verified

| input | identity | check performed here |
|---|---|---|
| `nd-unfolding/gbdt_model_dependence/inputs/operands.npz` | `61c32477…` | equals `inventory.json` `operands_sha256` (enforced in code) |
| `…/inputs/inventory.json` | `e3f3289b…` | used for ratio identities (below) |
| `…/definition.json`, `README.md`, `PROPOSAL.md` | `7022958b…`, `46a0ed82…`, `7c4cd9f5…` | read |
| `state/s5e/cand/assess_receipt.json` | `84266e30…` | ensemble means and SDs agree with it to ≤ 1.2e-15 on all 151 shared functionals, six truths |
| `state/s5e/diag/diag_receipt.json` | `f0880725…` | source of the per-iteration fold χ² series (§3, E6–E7) |
| `PROPOSAL-20261005-scalar-measurement-successor.md` | `03956ead…` | read, including §0 reconciliation |
| `OUTCOME-20260926-s5e…`, `DIAGNOSIS-20260926-s5e…` | `c0d15cae…`, `6d7b2bb3…` | read |
| corrected ratios `state/s5p/ratios/altR/p1r-…`, `p2r-…`, `p3r-…` | `9240e4b3…`, `6a36c9bc…`, `b3108969…` | numerator/denominator digests (`475a2871…` NuWro, `cfa42210…` GENIE CV, `c179855d…` GENIE MEC) appear in the committed flux-fix receipts `gen5d-fluxfix-2.json`/`-3.json`; `change_against` names the historical W3 (`3455daf3…`) and W2 (`80e16f95…`) ratios. P1r has 101 of 1,568 cells at the [0.25, 4] clip; P3r none; P2r 3 of 294 |
| goals copy | `81496789…` | equals the digest recorded in `DISPATCH.md` |

**Historical operands reproduce from raw arrays with independent code** (`results.json`
`headline_reproduction`): W3 noise-free J median |residual| 5.573% at K = 5 and 6.573% at K = 200
(max 32.904% → 44.770%, H2 3.421% → 3.680%); W3 assessment EW29 bias +23.665%, SD 0.558%; EW7 −6.812%,
0.299%; nominal EW41 15/40 hits at fixed σ. Each matches the synthesis README.

**Ratio identity, from inventory metadata.** The same file feeds the K = 5 assessment ensemble, the
noise-free trace and the data prior: W3 = `3455daf3…` = prior d4; W2 = `80e16f95…` = d3; GiBUU
E_avail = `45cc3e0a…` = d1; W1 = `2a208df9…` = d2. These pairings make E2 and E5 below well defined.
**These are historical ratios** (pre flux repair); the corrected P1r–P3r were used in s5p power runs,
so they are development truths too.

**Cluster inputs present (read-only `ls`, login05, 2026-10-09T20:15:45Z).** The event file
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz` is present at
1,548,438,020 B (mtime 2026-06-27), with `s5c-20260924/runs/p2/bkg_dump.npz` (16,017,201 B),
`s5e-20260925/runs/diag/{asimov,bkg,drv,rep,trace}` and `s5p-20260926/runs/s2/conv/k_*.npz`. **Not
re-hashed** here. The consumers' records name it `07fccc1a…`, which is an admission check for D-ID, not a
fact established by this listing. `/pscratch` is purgeable.

## 3. Saved-output findings

All from `results.json` (`reduce_saved_outputs.py`, NumPy/SciPy only, no repository import, one
thread). "Departures" are the five development truths GiBUU E_avail, q3 (a = 0.3), W1, W2 and W3.

**E1. The error is bias, not repeat variance.** At K = 5 (candidate R, 20 experiments per truth), the
median |bias| over J cells is 9.36% (GiBUU), 4.47% (q3), 5.99% (W1), 0.56% (W2) and 5.40% (W3). The
median repeat SD is 0.26–0.43%. The median bias share of MSE is 0.99–0.998 in J for the four strong
departures (0.79 for W2), and 81–99% of J cells have |t| > 3.6. Nominal has no significant bias (max
|bias| 0.098%, no |t| > 3.6).

**E2. The bias is deterministic: one noise-free run measures it.** The B0 noise-free (asimov_same)
K = 5 residual and the R K = 5 ensemble mean agree for every departure and map. Pearson ≥ 0.998, slope
0.990–1.009, median |difference| 0.06–0.21 pp, against median biases of 1–11%. The residual
differences are 1.0–2.9 ensemble SE (median), consistent with the estimators differing only in
refinement and background. **Consequence:** the bias question does not need repeat ensembles. A
discriminating diagnostic can be noise-free.

**E3. The residual is misallocation, not shrinkage toward the prior.** For cells with |departure| > 1%,
take ρ = (f̂ − f_nom)/(f_true − f_nom) at K = 5. Pure shrinkage would give ρ ∈ [0, 1]. In J, ρ < 0 (the
estimate moves *against* the cell's own departure) in 32% (GiBUU), 37% (W1), 28% (W3) and 11% (q3) of
cells. ρ > 1 in 5–33%. At the largest available K these fractions are 25%, 30%, 29% and 11%. More
iterations do not repair the sign errors. Example: GiBUU EW29 has a −30.3% departure and a +74%
residual, above the +43% that staying at the prior would give. The reco departure is reproduced by
moving weight between truth cells.

**E4. Iterations do not converge the residual (finite scans).** For W3, the J median goes 5.57% → 6.27%
→ 6.57% at K = 5/40/200, and 66% of J cells are worse at 200 than at 5. GiBUU improves slowly
(J 9.47% → 4.90%, K = 5 → 40; max 51.3% → 39.1%), as does W1 (5.41% → 4.09%). q3 worsens in EW
(4.99% → 6.42%, K = 5 → 30). No infinite-K or algorithm-wide claim is made.

**E5. On real data, a prior swap reproduces most of the closure residual.** Linearize the estimator.
The closure residual of truth T with the nominal prior is r_T = −(I − A)(T − N). The data shift when the
prior is changed to T is s_T = (I − A)(T − N), so r_T = −s_T (identity tested on a synthetic linear
estimator in `test_comparator.py`). Measured, using the R ensemble mean against the data prior of the
same ratio file:

| truth (prior) | J: R² of r explained by −s / slope / Pearson | EW | H2 |
|---|---|---|---|
| GiBUU (d1) | 0.753 / 0.731 / 0.947 | 0.815 / 0.891 / 0.936 | 0.858 / 0.771 / 0.967 |
| W1 (d2) | 0.769 / 0.718 / 0.962 | 0.836 / 0.887 / 0.946 | 0.578 / 0.661 / 0.881 |
| W3 (d4) | 0.690 / 0.724 / 0.916 | 0.715 / 0.750 / 0.926 | 0.513 / 0.817 / 0.742 |
| W2 (d3) | 0.191 / 0.558 / 0.726 | 0.871 / 0.895 / 0.936 | −0.818 / 0.394 / 0.775 |

For the three strong departures, 69–84% of the J/EW residual sum of squares is a deterministic function
of the prior–truth difference that persists on real data. The slope below 1 means the data shift
underestimates the closure residual by 11–28%. The relation is a sensitivity, **not a bound**. W2's
residual is small and noisy relative to it.

**E6. Fold misfit: the two departures behave differently** (s5e D4/D5 noise-free χ² of the unfolded
fold against the truth fold, 5D reco binning of 10,499 cells, analysis exposure):

| run | λ_5D at K = 5 / 15 / 30 | monotone? | median EW residual first → last |
|---|---|---|---|
| B0, E_avail | 367.7 / 237.8 / 163.7 | yes, every recorded step, EW and 5D | 14.27% → 8.05% |
| capacity 400/31, E_avail | 218.4 / 123.8 (K ≤ 15) | yes | 15.01% → 10.29% |
| B0, q3 | 1260.3 / 1031.0 / 987.0 (982.2 at 20, 999.3 at 25) | **no**: plateau (λ30/λ15 = 0.957), the 5D series rises at 25, EW rises at 8 of 29 steps | 3.28% → **6.56%** (grows) |
| capacity 400/31, q3 | 331.2 / 174.4 (K ≤ 15) | yes (λ15/λ8 = 0.74, still falling) | 2.89% → 3.14% |
| missed events at w = 1, q3 | 2340.8 / 1256.1 / 1209.3 | plateau | 2.74% → 5.60% |

These are asimov_same constructions, so an exact solution, the truth itself, exists. Exact EM keeps
reducing a visible misfit. **For q3, B0 has a fixed point the data reject** (λ_5D ≈ 985, an omnibus
excess of ≈ 6σ). Capacity removes the stall and halves the median residual (6.16% → 3.14% at K = 15).
This identifies **classifier approximation as a material contributor for q3**. **For E_avail, capacity
halves the visible misfit (237.8 → 123.8 at K = 15) while the truth residual does not improve
(9.16% → 10.29%).** Fitting the visible directions better does not move the truth error, which is the
signature of **weakly constrained directions** for E_avail.

**E7. Visibility of the residual.** At K = 5 the E_avail residual keeps 88% of the departure's truth rms
amplitude over J, but only 6.3% of its reco amplitude (√(λ_5D/S_dep)): it is about 14× less visible per
unit truth amplitude than the departure. For q3 the ratios are 44% truth and 11.7% reco (about 3.8×).
At K = 30 the E_avail residual's omnibus excess over 10,499 cells is 1.1σ, so a goodness-of-fit test on
data would not see it. A directed test along its own direction gives √164 ≈ 12.8σ, so a
likelihood-based estimator can in principle remove the visible part. How much of the truth residual
that would remove is **not identifiable from saved outputs**: it needs the response (§6).

**E8. Against the proposed targets, the present estimator fails on existing evidence.** Take the
allowance B_c as the maximum over the five departures of |K = 5 ensemble bias|. Its median is 14.7% (J),
19.0% (EW) and 9.8% (H2). Only 19% of J cells (30% of H2) are ≤ 5%. Leaving out the single most
damaging departure still leaves medians of 10.0% (J) and 5.8% (H2). Because B enters the half-width
additively, the proposed ≤ 10% median total half-width already fails at J and EW, and is marginal at H2
before any systematic is added. The departures are historical amplitudes (a = 1; q3 a = 0.3), not the
plausible size of the data's departure from the model. This is a failure against **proposed** targets
and a finite development set, not a ratified FAIL.

**Capacity at K = 10 (noise-free, three truths)** moves the J median 5.55% → 4.41% (W3), 9.22% → 8.67%
(GiBUU) and 4.10% → 3.52% (q3); H2 for W3 moves 3.68% → 1.01%. The approximation component is real and
truth dependent.

## 4. Three explanations, ranked, with a discriminating observation for each

| rank | explanation | saved evidence for / against | discriminating observation (in D-ID) | if the observation is positive | if negative |
|---|---|---|---|---|---|
| 1 | **Weak identifiability of the reporting functionals** (truth directions with near-null response at analysis exposure, plus within-cell ambiguity) | For: E6 E_avail (misfit falls, truth error does not), E7 (14× lower visibility), E3 (sign errors persist), E4. Against: λ > 0 at K = 30, so part of the residual is visible | Per-functional Cramér–Rao width σ_c of the binned exact-response problem at the analysis exposure (truth grids T1/T2), and the share of the GBDT residual in Fisher modes whose own χ² contribution is < 1 | Functional c is **weakly identified** (σ_c > 10%): no estimator meets the proposed target there without prior information. Change the functional (§7, I2) or carry a large declared allowance | σ_c ≤ 2.5% and the residual is mostly visible: the data determine c, so the GBDT bias is an estimator defect (rank 2 or 3), in principle repairable |
| 2 | **Classifier ratio approximation / iteration error** | For: E6 q3 (stall, non-monotone, removed by capacity), capacity on W3 H2. Against: E_avail is insensitive to capacity | Binned exact-response IBU from the same prior and pseudo-data, compared with the saved GBDT trajectory at matched K (1…30, and 200 for W3) | **approximation-dominated** (|r_IBU| ≤ 0.5 |r_GBDT|): the GBDT does not execute the iteration it approximates. Specify I1 | **iteration-faithful** (|r_IBU − r_GBDT| ≤ 0.3 |r_GBDT|): the GBDT does what exact IBU would. The residual is iterative regularization, and its removability is decided by rank 1 |
| 3 | **Propagation / acceptance / background bookkeeping** | Against: signal-only reproduces the departure failure, the MC split and driver path are excluded, step 2 reproduces step-1 truth sums to 0.11% (s5e). Partial: the missed-event treatment changes q3 by 13–15% | Exact-efficiency binned IBU against GBDT, split by the missed-event fraction of each truth cell; and a same-response vs split-half response comparison | The GBDT excess over exact IBU concentrates where the missed fraction is large: bookkeeping (missed-event extrapolation) is implicated, and the regressor needs its own design | No concentration: bookkeeping is not material at the tested departures |

A finite unsuccessful search cannot prove identifiability. A binned Fisher width bounds what *this
binning* of the data can see. Unbinned data can carry more information, so σ_c is conservative in the
reco direction. Coarse truth cells hide within-cell freedom, so it is optimistic in the truth direction.
D-ID therefore reports two truth resolutions and states which way each approximation errs.

## 5. Why not the old panel, and why not more toys

The ~70-node-hour panel (`PROPOSAL.md`) estimates a bias–variance–MSE relation across R5/R20/capacity
with 160 repeats per truth. E1 and E2 remove its rationale as the *next* step. Variance is 0.2–0.4%
against biases of 5–15%, so the MSE is bias to within 1%. The bias is measured by a single noise-free
run to about 0.2 pp. The panel's own capacity and K contrasts are available noise-free at roughly 1/160
of the repeat cost, and E6 already shows that their effect depends on the departure. A variance axis
cannot change any decision while the bias is 20–50 times larger. **Disposition D2: FAIL as the next
step** (the existing evidence rejects its premise). It could only become relevant after a repair brings
the bias near the statistical scale.

## 6. Proposed diagnostic D-ID (preregistration-ready; not run)

**Purpose.** Separate, per reporting functional and per departure, (a) the part of the GBDT residual an
exact-response iteration would also leave (iterative regularization), (b) the part the exact response
removes (GBDT approximation or bookkeeping), and (c) the intrinsic data-determined precision of the
functional at the analysis exposure (identifiability).

**What it is not.** It does not run a classifier fit, ensemble, toy, oracle-substituted OmniFold or a
deployable estimator. The binned exact-response iteration is a diagnostic oracle. It cannot be quoted
as a measurement, and nothing in it validates an interval.

**Inputs (all existing; identities as admission checks).**

| role | object | identity / admission check |
|---|---|---|
| events | `of_inputs_5d.npz`, keys read by `s5c_unfold.load_inputs` (`510d749a…`): `MCgen`, `MCreco`, `pass_reco`, `pass_truth`, `w_truth`, `w_reco`, edges | sha256 must equal `07fccc1a…` (stage-1/inventory record); otherwise stop |
| departure weights | GiBUU `45cc3e0a…`, W1 `2a208df9…`, W2 `80e16f95…`, W3 `3455daf3…`, q3 (s5e amplitude 0.3 construction), corrected P1r/P2r/P3r (§2) | each digest equal to the record. Weights built by the committed `s5e_deform` path (sha pinned at admission), never re-derived by hand |
| GBDT comparators | s5p `runs/s2/conv/k_b0_{nominal,w3}.npz`, `k_cap10_*.npz`, the partial `k_b0_{gibuu,w1,q3}` prefixes (as the synthesis truncated them), and s5e `runs/diag/{asimov,trace}` products (`fn_push` per iteration, final `xsec_flat`, `reco5d_push_it*`) | digests equal to `inventory.json` and to the diag receipt's inputs. Partial files are truncated to the synthesis's included iterations |
| reco binning | the s5e tracer's 5D reco cells (10,499) | **admission check:** the comparator's S_dep must reproduce the receipt's 92,363.63 (GiBUU) and 92,244.78 (q3) within 0.1%, and the GBDT fold λ_5D within 2% at K = 5, 15, 30 |
| reporting maps | `definition.json` EW/J/H2 maps and reported masks (39/109/27) | unchanged |

**Sample roles and event identity.** (i) *Same-sample oracle:* response and pseudo-data from all MC
rows. This is exact for asimov_same, so any residual is the iteration's or the identifiability's.
(ii) *Split-half:* response from the unfolding half and pseudo-data from the other half by the
existing split key. Disjointness is checked by row index, and both halves' row counts and weight sums
are recorded. Rows are MC events within one file. **No independent data population is involved or
claimed.** The data file is not read. Row index is the identity, and `(run, subrun, gate)` is not an
event key. If the split key cannot be reproduced bitwise from the record, run (i) only and label (ii)
missing.

**Construction (fixed in advance).** Truth grids: T1 = J cells (243, of which 109 are supported); T2 =
each J edge split at the fine edge nearest its midpoint (≤ 7,776 cells, empty cells dropped and
listed). T3 = the fine grid (65,856) is used **only** for the IBU trajectory (sparse), never for dense
algebra. Response `R[reco, truth]` = reco-passing weight / truth-passing weight per truth cell, built
twice: with nominal weights and with each departure's weights. The difference is the within-cell
(binning) bias, reported as its own number. Background: signal-only (s5e showed signal-only reproduces
the departure failure). The background-inclusive variant is out of scope and is recorded as such.

**Computations.** For each departure × grid × response variant:

1. IBU from the nominal prior, K = 1…30 (and 200 for W3), reported on the 175 functionals.
2. IBU run to convergence (relative truth change < 1e-10, or 10⁵ iterations, whichever comes first);
   non-convergence is recorded, never truncated silently.
3. Fisher `F = Rᵀ diag(1/y) R` at T1 and T2. Per-functional CR width with explicit null-space
   detection (`comparator.cr_width`).
4. The invisible share of the GBDT final-K residual aggregated to T1/T2 (`comparator.invisible_share`;
   a mode is invisible when its own noise-free χ² contribution is < 1).
5. Labels from `comparator.classify`.

Reference implementations are in `comparator.py`, tested on synthetic fixtures (§11).

**Metrics.** Per functional: r_GBDT(K), r_IBU(K), r_IBU(∞), relative σ_c, invisible share, and the
binning bias. Per map: medians, 90th percentiles, maxima and full per-cell tables. No cell selection.

**Predeclared decision rules** (thresholds frozen in `comparator.py`; the primary is T2 with the
split-half response at K = 5):

- *iteration*: approximation-dominated if |r_IBU| ≤ 0.5|r_GBDT|; iteration-faithful if
  |r_IBU − r_GBDT| ≤ 0.3|r_GBDT|; otherwise mixed;
- *identifiability*: identified-at-target if σ_c ≤ 2.5%; weakly identified if σ_c > 10%; otherwise
  intermediate;
- *branch outcome* (per map, over the five historical departures and P1r–P3r): **branch C** if ≥ 50% of
  functionals with |r_GBDT| > 2% are weakly identified; **branch A** if ≥ 50% are
  approximation-dominated and identified-at-target; **mixed** otherwise. Label shares are always
  reported with their per-departure breakdown;
- a functional whose label changes between T1 and T2, or between the response variants, is reported
  as **resolution-sensitive** and counts toward neither branch.

**Numerical tolerances.** The noise-free nominal must return r_IBU ≤ 1e-8 at every K (implementation
control). The same-sample oracle with the departure-weighted response must converge to its own binned
truth within 1e-6 relative on identified functionals (exactness control). If either fails, the run is
INCONCLUSIVE and is not tuned.

**Missing-result rules.** A departure whose weight file fails its digest is excluded and listed; it is
never replaced. A failed admission check stops everything after it. The grid T2 is dropped only if its
Fisher matrix exceeds 6 GiB, and that is recorded. No result is dropped for its value.

**Stopping.** One pass at the frozen settings; no extension, re-thresholding or re-gridding after
results. Stop at the cap below.

**Interpretation of both outcomes.**

- **Branch C:** the J-grid joint functionals are weakly identified at the analysis exposure. The
  present endpoint (J-cell joint 5D at ≤ 10% width) is out of reach for *any* estimator using these data
  and this response without prior information. This is a quantified no-go for that endpoint, and the
  route moves to I2, an endpoint change that needs Joseph's scope decision.
- **Branch A:** the functionals are identified and the GBDT leaves avoidable error. I1 becomes the
  justified next experiment.
- **Mixed:** I1 and I2 apply to their own labelled functional sets. If both sets are small, record
  INCONCLUSIVE with the shares.
- **Any outcome** is simulation-only and conditional on the fixed detector response, the signal-only
  model and the departure family.

**Price (forecast, not measured).** Data movement: one read-only copy of the 1.44 GiB event file, or
the 14 needed float32 columns (≈ 1.06 GiB), into a dated scratch; deleted after the run. Compute:
binning passes over 20.4 M rows; dense eigendecomposition at ≤ 7,776 (≈ 0.48 GiB per matrix); sparse
IBU at T3. Planning 1–4 CPU core-hours, plus 1 hour of independent recomputation of the label shares
from the per-cell table, giving 5 / 0.8 = **6.25 local CPU core-hours admitted**, ≤ 2 GiB scratch,
≤ 8 GiB RAM, two threads, 0 GPU, 0 training, 0 Slurm. Running instead on a login node is a cluster-use
decision for Joseph and is not priced as node-hours. Development, review and verification of the full
driver: ≈ 1 owner-day and one fresh review, not included above.

## 7. Two conditional interventions (specified, not executed)

**I1 — capacity-raised OmniFold estimators, noise-free first** (justified only under branch A). It is
tied to E6 (the q3 stall that capacity removes) and to the capacity effect at K = 10. Setting: the s5e
D5 capacity probe (400 trees / 31 leaves on the three OmniFold estimators). The R refinement (400/31)
and all other settings are unchanged. No other setting is scanned. Truths: the five historical
departures plus P1r/P2r/P3r, all development. Run asimov_same to K = 30. Primary metric: the share of
branch-A functionals whose |r| falls to ≤ 0.5 of B0's at equal K, and ≤ 1.5 times r_IBU. Secondary: the
λ_5D series is monotone. Price: 8 truths × 30 iterations × 489.5 s (the cap10 trace median, 4,895.386 s
per 10 iterations) = 117,489 s = 4.08 node-hours at 8 tasks per node; ×1.25 packing = 5.10, plus 1.0
verification = 6.10, /0.8 = **7.62 CPU node-hours admitted**, 0 GPU. This is a forecast from
heterogeneous timings. Stop rule: if after K = 30 fewer than half of the branch-A functionals meet the
primary metric, I1 FAILS and is not extended. Only a pass justifies a separately admitted, much more
expensive confirmation on an untouched departure (§10).

**I2 — change the reporting functionals to identified ones, with a strict-bounds benchmark** (justified
under branch C). It is tied to E7/E8 and to D-ID's per-functional σ_c. Select, from MC alone and before
any data result is inspected, the functional set whose σ_c ≤ 2.5% at T2: wide combinations of J cells,
H2, or response-derived combinations, frozen with a digest. Evaluate the existing saved GBDT products on
it as a local reduction, which needs the fine-grid `xsec_flat` of existing products (about 70 MB).
Construct One-at-a-time Strict Bounds intervals on it as a **methodological benchmark** (§8). This is a
**different publication endpoint** from the joint J-cell measurement and needs Joseph's scope
decision. Price: selection and evaluation 2–10 CPU core-hours. The strict-bounds solver is an
**unpriced dependency**: no second-order-cone solver (e.g. `cvxpy`) exists in the present environment,
and installing one is an environment decision.

## 8. Fine-bin confidence sets (arXiv:2111.01091), mapped to this problem

Read from the paper's text (sha256 `b8588756…` of the fetched PDF, 2026-10-09): Stanley, Patil and
Kuusela, *Uncertainty quantification for wide-bin unfolding: one-at-a-time strict bounds and
prior-optimized confidence intervals*, DOI 10.1088/1748-0221/17/10/P10013.

| paper's assumption | here | change needed |
|---|---|---|
| y ∼ Poisson(Kλ), used through the Gaussian approximation y = Kλ + ε, ε ∼ N(0, diag(Kλ)), with Kλ treated as known in their simulations (§2.1.1) | 10,499 reco cells; low-count cells exist | whiten with an estimated variance; check the Gaussian approximation in sparse cells or merge them |
| K from an MC ansatz with "Monte Carlo noise … negligible", fine true bins to limit ansatz dependence (eq. 2.10) | 20.4 M MC rows over ≤ 65,856 fine cells: MC noise per fine cell is **not** negligible | propagate the response's MC uncertainty (for example, replicate the bounds over response bootstraps, or enlarge the constraint set); unaddressed by the paper |
| constraints Aλ ≤ b (non-negativity; monotone/convex options) | non-negativity holds; shape constraints are physics choices | any constraint beyond non-negativity is a model assumption to be declared |
| OSB: min/max hᵀλ s.t. ‖y − Kλ‖² ≤ z²₁₋α/₂ + s², Aλ ≤ b; coverage proved (Tenorio et al.) when h is in the row space of K; **empirical only** in rank-deficient cases; one-at-a-time | the 5D problem is rank-deficient at T2/T3; there are 175 functionals | use as a benchmark, not a validated procedure. Simultaneous claims need the SSB variant or multiplicity control, which is wider |
| PO intervals: provable frequentist coverage for fixed dual parameters, with the prior used only to optimize expected length | same | the same response-uncertainty gap applies |
| no background in the paper's main examples; 1D examples with m = 40 smeared and n = 10/40/80 true bins | signal plus a refined negative-weight background | add the background with its own uncertainty to the forward model; scale the computation (m ≈ 10⁴, n ≈ 10³–10⁵) |

**Conclusion.** Strict bounds answer exactly the identifiability question here, because the interval
width is the data-consistent range of the functional. That makes them the natural I2 benchmark.
Response MC noise, backgrounds and 5D scale are unaddressed, and the coverage is empirical in our
rank-deficient regime. **They are not a validated rescue of the GBDT.**

## 9. Full validation budget and feasibility

Per-experiment intervals must be reconstructed by the frozen procedure, as Goal 5 requires. Sizing
(`results.json` `design`, exact Clopper–Pearson): pass if every functional's one-sided lower bound at
familywise 0.05 (Bonferroni over functionals × cases × two levels) is ≥ 0.63 (I68) and ≥ 0.92 (I95),
with ≥ 0.80 union-bound assurance at exactly nominal coverage. The bounds are proposals. Sizes: H2
(27 functionals), 4 cases: **3,562** experiments per case; J (109), 4 cases: **4,404**; all 175
reported: **4,698**. One case only: 2,726 / 3,565 / 3,845. A brute-force test checks the search's
minimality on a small case.

Cost at the measured 293.973 s per K = 5 pseudo unfold (32 threads; 423 receipts), 8 tasks per node,
×1.25 packing, admitted = subtotal / 0.8 (J sizing, 4 cases):

| unfolds per experiment (procedure) | subtotal node-h | admitted node-h |
|---|---:|---:|
| 1 (central only, no interval) | 225 | 281 |
| 31 (central + 30 bootstrap) | 6,968 | 8,710 |
| 101 (central + 100 bootstrap, the s5e R recipe) | 22,701 | 28,377 |
| 288 (+ 187 refit flux/detector/interaction universes) | 64,733 | 80,916 |

These exclude sample construction, identity work, the I1/I2 confirmation, retries and review. Speed
sensitivity for the 288-unfold recipe (Amdahl, accelerated fraction f unknown and labelled; no Session-4
result had been pushed when this was written): f = 0.8, s = 10 gives 22,656 admitted; f = 0.95,
s = 100 gives 4,815. Earlier pools for comparison: the s5p CPU pool was 341 node-hours, and s5e used
10.4.

**Feasibility conclusion.** Validating a GBDT bootstrap-plus-universe total interval in 5D by frozen
per-experiment reconstruction costs 10²–10³ times any pool this project has used, even under optimistic
speedups. Even the statistical-only interval with 30 replicas is ≈ 8,700 node-hours. **This is a
quantified no-go for that validation route under the present method** (D3). It does not prove every
alternative infeasible. A procedure whose per-experiment interval costs seconds (a binned or linearized
propagation, strict bounds) changes the count by about 300×, but it is a **different interval
algorithm** that needs its own design and validation, including the response-uncertainty gap of §8.

## 10. Route from D-ID to publication review

"Now" means answerable from current inputs; "P" means it needs new production; "M" means it needs a
changed method.

| stage | evidence available | missing populations / identities / variations | admission criteria (proposed) | price | stop | gate class |
|---|---|---|---|---|---|---|
| S0 D-ID | E1–E8; named inputs present (2026-10-09 `ls`) | none for the diagnostic itself; the event-file digest is to be re-measured | §6 admission checks | ≤ 6.25 CPU core-h, 1.44 GiB read | §6 | Now (after authorization) |
| S1 point-estimator confirmation | development truths only: historical GiBUU/W1–W3/q3; corrected P1r–P3r (already inspected in s5p) | **an untouched physical departure**: interaction-knob / FSI / MnvTune-component reweights or response variations. The loader reads no such weights; whether the file carries any is unobserved (one key listing) | a frozen I1 or I2 estimator; bias on the untouched departure within the frozen allowance; no sign reversal on identified functionals | I1 noise-free 7.6 node-h; untouched-departure inputs **unpriced** (event-loop production if weights are absent) | stop if no untouched departure exists: **NO UNTOUCHED VALIDATION DOMAIN** | P (inputs), M (if I2) |
| S2 matched total-UQ construction | R's 100-replica data bootstrap (refits everything) and the numerical floor (s5e A3); the adopted `C_EW` covers a different estimator | per-universe 5D inputs (flux/detector/interaction) for the same estimator; background-template statistics; a joint nuisance law | same estimator, domain and centering for every block; the allowance B from S1 enters once | data construction 288 × 648.0 s ≈ 6.5 node-h subtotal ×1.25/0.8 ≈ 10.1 node-h after inputs exist; inputs **unpriced** | stop if universes cannot be produced for this estimator | P |
| S3 calibration / coverage | none qualifying (fixed-σ coverage is historical) | independent pseudo-data populations at production size, per experiment, with each experiment's own interval | §9 sizing on the frozen functional set | §9: 281 to 80,916 node-h under the present method | **no-go under the present method** (§9) unless a cheap per-experiment interval is first validated | M |
| S4 supported reproduction | the synthesis reproduction path and the receipts | a pinned guarded producer for the new estimator (Session 2's harness pattern) | bitwise rerun of the central; provenance of the executed module | small, unpriced until S1 fixes the estimator | — | P |
| S5 publication review | — | Joseph's endpoint decision; the claims map | independent review of claims against evidence | review only | — | decision |

**10.1 Answerable now:** E1–E8, the D-ID design, the infeasibility of frozen-procedure validation
under the present method, and the failure of the present estimator against the proposed targets.
**10.2 New production:** untouched departures and response variations, per-universe 5D inputs,
identity-carrying independent populations. **Changed method:** any affordable S3, and I2.

**10.3 Relation to the 2D pairing problem and to scope.** This route **does not address** the 2D
pairing problem (exact-GBT central against LightGBM uncertainty blocks, transfer unmeasured;
`closeout/REPORT.md` §11). That remains under Joseph's interim keep-and-disclose decision and its own
lanes. The 5D route aims at a **different publication endpoint**, the joint `(pT, p_parallel, E_avail,
q3, W)` measurement. Its I2 branch would change the endpoint again, from J cells to identified
functionals. Both need Joseph's separate scope decision. **Any success along S0–S1 is a
simulation-only, conditional success** (fixed response, signal-only, development departures) and must
be labelled that way.

## 11. Verification and review

- **Independent numerical checks.** The ensemble statistics are re-derived from raw arrays and match
  the s5e receipt to ≤ 1.2e-15. All README headline numbers reproduce (§2). The reducer imports no
  repository module and checks the operand digest.
- **Synthetic controls (`test_comparator.py`, 8 tests, pass).** Positive and negative controls:
  - exact IBU misfit is monotone and falls by > 10³; an approximate (over-smoothing) step stalls at
    > 100× the exact misfit (the E6 discriminant fires on the defect and stays silent on the exact
    case);
  - a duplicated response column makes the difference functional non-identifiable (σ = ∞) while the
    sum stays finite, and the clean response is finite everywhere;
  - the invisible share is 1 for a weak mode and 0 for a strong mode;
  - classification labels fire in both directions;
  - the linear prior-pull identity r = −s holds exactly;
  - a non-diagonal kernel produces ρ < 0 and a diagonal one does not;
  - the Clopper–Pearson sizing is minimal, by brute force.
- **Consequential arithmetic recomputed by hand.** I1: 8 × 30 × 489.5386 = 117,489 s; /28,800 = 4.080;
  ×1.25 = 5.099; +1 = 6.099; /0.8 = 7.62. §9: 293.973/28,800 × 1.25 = 0.012759 node-h per unfold;
  × 4 × 4,404 × 288 = 64,733; /0.8 = 80,916. A normal-approximation check of N for J/4 cases,
  (z₁₋₅.₇ₑ₋₅ + z₁₋₂.₃ₑ₋₄)² p(1−p)/0.0527² ≈ (3.86 + 3.50)² × 0.2166 / 0.002777 ≈ 4,225, agrees with
  the exact 4,404.
- **Fresh reviewer:** recorded below after the review.

## 12. Commands and resources

```bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
python3 -I docs/orchestration/state/next-preparation-20261009/gbdt/reduce_saved_outputs.py \
    --out docs/orchestration/state/next-preparation-20261009/gbdt/results.json   # 31.6 s, 98 MiB RSS
python3 -m pytest -q -p no:cacheprovider docs/orchestration/state/next-preparation-20261009/gbdt/test_comparator.py
```

Environment: macOS, Python 3 with NumPy 1.26.4, SciPy 1.15.2. Elapsed so far: from 12:59:45 PDT; the
final figure is in §13. Local CPU: reductions ≈ 0.02 core-hours (two runs, 21.2 s and 29.5 s user),
tests < 0.01; the total with the review is in §13. Scratch: < 5 MiB (the paper PDF 4 MiB, logs), removed
at delivery. Tracked: the five files (≈ 116 KiB). Cluster: one `ls` (no job, no compute). GPU and
training: 0.

## 13. Disposition

| decision | verdict | reason |
|---|---|---|
| D1: what evidence discriminates repairable bias from weak identifiability, and is one small experiment justified? | **PASS** (pending §11 review) | D-ID has a defensible purpose (E6/E7 show the split is departure dependent and unresolved from saved outputs). Its inputs exist, observed 2026-10-09. The design, rules, tolerances, stopping and price are complete, with tested reference reductions. It needs no training and ≤ 6.25 CPU core-hours |
| D2: run the old ~70-node-hour bias–variance panel next? | **FAIL** | E1/E2: variance is 1/20–1/50 of bias, and noise-free runs measure the bias. The panel measures the axis that cannot change a decision |
| D3: can the present estimator plus frozen-procedure validation reach the endpoint at useful precision? | **FAIL against proposed targets** | E8: allowance median 14.7% (J) against a proposed 5%. §9: validation 8,710–80,916 admitted node-hours. These targets are not ratified; a changed method is not excluded |
| overall publication-ready objective | **not achieved** | this lane designs a diagnostic |

## 14. Next action

**Decision for Joseph:** authorize D-ID as specified in §6. That means a ≤ 1.44 GiB read-only copy of
`of_inputs_5d.npz` (or a 14-column extract) and the digested departure/comparator products, ≤ 6.25
local CPU core-hours, 0 GPU, 0 training, 0 Slurm, one owner and one fresh reviewer. Its outcome (branch
A, branch C or mixed) selects between I1 (7.62 node-hours, noise-free) and I2 (an endpoint change that
needs his scope decision). **Separately**, any S1 confirmation needs an untouched departure that does
not exist in current inputs (§10). No S3 is affordable under the present method (§9).

**Integration request (for the dispatch/catalog owner; not done here).** `generate_manifest.py` will
need rows for the four non-`REPORT.md` files in `Q/gbdt/`. Their class is this owner's choice; the
lane suggests `MACHINE open` like `REPORT.md`. The lane did not edit `MANIFEST-overrides.tsv`,
`MANIFEST.tsv` or `CATALOG.md`. If the manifest-freshness check reports these paths as missing, that is
this integration requirement, not a regression.
