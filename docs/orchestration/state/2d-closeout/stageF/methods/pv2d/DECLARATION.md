# Declaration: PV-2D, the 2D prior-variation (model-dependence) test (2026-10-23)

**By** the session "2d test", under [`ASSIGNMENT.md`](ASSIGNMENT.md) (the director's PR #282, `main` `177bf84b`) and
[`../../lanes/COMMON-RULES.md`](../../lanes/COMMON-RULES.md). **Written** 2026-10-23, before any PV-2D job was submitted
and before any unfold with a reweighted prior was run. **Status:** awaiting the director's binding. A job started
before binding is held and not used.

**CITABLE FOR:** what will be run, on which inputs, with which reweights, the controls and their numeric pass rules,
the readouts, and the compute cap, fixed before any result. Also the vertex reweights themselves (§3), which are
projections of fixed predictions, not unfolding outputs.

**NOT CITABLE FOR:** any result, any uncertainty component or any claim change.

## 1. The question and the estimator

How much does the real-data 2D (p_T, p_∥) result move when the MC truth prior is reweighted from Tune v1 to another
generator's shape? The readout is descriptive; there is no pass/fail for the measurement. The controls carry the
pass rules (§5).

**The estimator is E_U's**, configuration (a): LightGBM, 100 trees, 8 leaves, learning rate 0.1, `--seed 42`, purity
background subtraction, five iterations, 128 threads. Its source is
`docs/publication/DECISION-20261011-joseph-2d-central-lightgbm-seed42.md:18-22`. E_U itself is
`2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root`, sha256 `4f5a1b6d44b9e721…`, re-measured on Perlmutter on
2026-10-23. Its launcher is `2d-unfolding/sbatch_unfold_2d_MEFHC_5iter_universes_full_CV.sh`. The refined estimator
(RE-2) is not run here; §8 offers it as an option. <!-- absence-ok: scope of this declaration (what PV-2D runs), not a claim about other lanes' work -->

## 2. The design

**The reweight follows s5p amendment 3** (`state/s5p/contract-amendment-3-stage2-supplement.json`). The data are
unfolded with w_truth and w_reco of every truth-passing MC signal row multiplied by r(truth). The response per event,
the background, the flux and the data are unchanged. Signal fakes (rows failing the truth selection) keep their
weights; they are background by the paper's convention, and none exist on this post-Phase-18 omnifile.

**The denominator defect is repaired by construction.** s5p's first study-P run reweighted the MC weights but not
the truth denominator, so each product was divided by its cells' mean reweight (`RECORD-20260927-s5p-stage2-exit.md`
§1; `state/s5p/campaign-state.json` incident; repair `nd-unfolding/s5p_universe.py` `prior_inputs`). Here r is
constant on each truth cell, and the truth-denominator rows' w_truth are multiplied by the same r. The completeness
c is then the nominal one to rounding, which is equivalent to s5p's `denom × ofin_r/ofin`. This is enforced twice
in the producer, fail-closed (`pv2d_lib.completeness_guard`, max |c_varied/c_nominal − 1| ≤ 1e-9): once on the
numpy completeness and once on the product's own `hOFCompleteness2D`. A synthetic control
(`test_pv2d.DenominatorGuard.test_defective_form_fires`) shows the guard refusing the defective form, and the
repaired form passes it silently.

**r on the 2D truth binning.** The cells are the paper's 14 × 16 (p_T, p_∥) cells. A row's cell follows ROOT's
`TH2D::Fill` convention: low edge inclusive, high edge exclusive, and a value on the last edge goes to overflow.
- **Under- and overflow.** A row whose truth lies outside the grid on either axis keeps r = 1. On this omnifile
  there are none among the signal's truth-passing rows: E_U's `hTruth2D` under- and overflow bins are all zero,
  re-measured 2026-10-23.
- **Unreported cells.** The 19 cells that are not reported (E_U `hXSec2D` = 0) keep r = 1, as do the reported
  cells the gate leaves unassigned (§3).
- **Composition below the 2D binning stays Tune v1's.** Within a cell, the distribution in (E_avail, q3, W) and in
  everything else is the MC's own.

**The vertices are generator shape ratios to GENIE 2.12 CV, applied to the Tune v1 prior: the s5p convention.**
s5p's D1–D4 were GiBUU/GENIE, NuWro/GENIE, GENIE MEC/CV and NuWro/GENIE. For vertex k,
- ρ_k = g_k / g_GENIE-CV per cell, where g is the flux-repaired 5D prediction integrated over (E_avail, q3, W) by
  `gen5d_to_rootpreds.integrate`, times the cell area;
- r_k = ρ_k × κ_k on the assigned cells and 1 elsewhere. κ_k fixes E_U's prior truth weight (`hTruth2D`) summed over
  the assigned cells, so each vertex is a pure shape departure (`s5n_pseudo.eavail_ratio_weight`'s convention).

Tune v1 is the prior itself, so its r is exactly 1. That run is the nominal control and the zero of every shift.
Untuned GENIE CV is the reference, so it is not a separate vertex.

**Why not the literal "reweight the prior to the vertex", r = g_k / prior?** I built it first, from the same inputs
and before any unfold. It gave r from 0.06 to 3.06, driven by two things the standalone generators share and the
analysis MC does not:
- generator MC noise: cells at 30–100% statistical error;
- standalone-generation artifacts: no E_ν > 100 GeV, so the 40–60 GeV/c row sits at 0.26–0.34 of Tune v1 for
  GENIE+MEC at low p_T, and high-p_∥ undersampling (`README-gen5d-fluxfix.md`, limitations; `KNOWN_ISSUES.md` 83).

The GENIE-CV reference cancels the artifacts to first order (KNOWN_ISSUES 83: *"NuWro/GENIE and GENIE-MEC/GENIE
ratios cancel the defect to first order"*), and the gate below controls the noise. That build is superseded and
was not used. Its files remain on scratch at `pv2d-20261023/ratios-build/ratios-superseded-ungated/`.

**The statistical gate** (`pv2d_lib.gated_shape_ratio`, `stat_max` = 0.05). The ratio's relative error is the
quadrature sum of both predictions' errors, each from its `sumw2` (Σ sumw2 × volume², the gen5d convention).
- **fine:** a cell keeps its own ρ if that error is ≤ 5%;
- **coarse:** otherwise it takes the pooled ρ over the unassigned region cells of its s5p coarse
  (p_T, p_∥) cell (p_T edges 0, 0.55, 0.85, 4.5; p_∥ edges 1.5, 3.5, 6, 60; `state/s5p/ratios/nulls*`), if the
  pooled error is ≤ 5%;
- **noisy:** otherwise r = 1.

**GiBUU is defined on p_∥ < 10 GeV/c only** (KNOWN_ISSUES 82). The GiBUU sample has no E_ν > 20 GeV, and above about
10 GeV/c its deficit is that cut (`README-gen5d-fluxfix.md`, check 5), which the E_ν < 100 GeV GENIE reference does
not share. At p_∥ ≥ 10 GeV/c, GiBUU's r = 1.

**The flux caveat (KNOWN_ISSUES 83)** is carried: the GENIE and NuWro predictions are the per-event flux-reweighted
repairs with 50–100 GeV supplements, not regenerations; E_ν > 100 GeV is absent from all of them. GiBUU is
reweighted to the analysis flux (σ × 0.9966) and keeps its 20 GeV cut.

## 3. The vertex reweights (built 2026-10-23, before any unfold)

`2d-unfolding/pv2d/make_ratios.py` ran at `01d815b9` on a Perlmutter login node in `root_6_28`, through
`nd-unfolding/mnv_guarded_run.py`. The inventory shows every module loaded from the deploy itself. Its output is
committed in `2d-unfolding/pv2d/ratios/`, and every file's sha256 equals its `projections.json` entry
(`projections.json` lists the inputs, per-cell g, variance, ρ, labels and errors).

| vertex | source (flux-repaired 5D) | source sha256 | ratio file sha256 | cells on the 205: fine / coarse / noisy / off | median \|r − 1\| | p90 | range of r |
|---|---|---|---|---|---:|---:|---|
| Tune v1 (nominal) | the prior (r ≡ 1) | — | `906a60aa37e91ae6…` | — | 0 | 0 | 1 |
| GENIE+MEC | `gen5d_fluxfix/genie_mec_xsec5d_full.npz` | `c179855df6e42a5b…` | `cfaaf4d663a392ce…` | 107 / 96 / 2 / 0 | 0.032 | 0.078 | 0.914–1.159 |
| NuWro | `gen5d_fluxfix/nuwro_cv_xsec5d_full.npz` | `475a2871304db23e…` | `785180dd9dba80a0…` | 108 / 95 / 2 / 0 | 0.063 | 0.264 | 0.886–2.127 |
| GiBUU | `gen5d_fluxfix/gibuu_cv_xsec5d_fluxfix.npz` | `48917692ee129590…` | `b62c224ac4321f38…` | 45 / 100 / 4 / 56 | 0.025 | 0.082 | 0.873–1.172 |
| reference: GENIE 2.12 CV | `gen5d_fluxfix/genie_cv_xsec5d_full.npz` | `cfa42210dfe9cadc…` | — | — | — | — | — |

- The source paths are under `/pscratch/sd/j/josephrb/s5p-20260926/`. Their sha256 values equal the committed
  receipt `state/s5p/gen5d/gen5d-fluxfix-2.json`.
- The positive-control fallbacks `{vertex}_sq` (ρ², renormalized the same way) are in the same directory:
  NuWro's is `a8f03852b3d604a3…`.
- The unassigned "noisy" cells are the θ = 20° boundary corner cells (for example p_T 0.70–0.85, p_∥ 1.5–2.0).
- The gate assigns 99.96% of the prior's truth weight on the reported cells for GENIE+MEC and NuWro (the rest is
  the two noisy corner cells), and 90.9% for GiBUU (its p_∥ ≥ 10 GeV/c cells are off by definition).
- The median fine-cell ratio error is 2.1% (GENIE+MEC), 1.9% (NuWro) and 3.4% (GiBUU). This residual noise enters
  the shifts and is not separated from them (§10).
- NuWro's largest values (r ≈ 2.1 at p_T < 0.15, p_∥ < 2.5 GeV/c) are fine cells at ≤ 5% error. They are the NuWro
  model's own forward-angle shape, not noise.
- **Cross-check.** The 5D analysis MC truth (`gen5d/mnvtune_v1_xsec5d.npz` `bf7bd278…`, from `of_inputs_5d.npz`),
  projected the same way, has the shape of E_U's 2D prior to a median 1.0e-4 over the 205 cells. The maximum is
  0.32, in one low-weight cell (p_T < 0.07, p_∥ 20–40 GeV/c). So the 2D and 5D studies' priors are the same MC.

## 4. Code and inputs

**Code** is under `2d-unfolding/pv2d/` (new). Existing producers are copied, not edited. The run pin is the commit
the binding names; the one proposed here is `3631ea3f` (branch `pv2d/declaration-20261023`; the ratios were built at `01d815b9`, and no
later commit changed `make_ratios.py` or `pv2d_lib.py`). Its pv2d files must carry these digests (first 16 hex;
`sha256sum` on the committed bytes):

| file | sha256 | role |
|---|---|---|
| `unfold_2d_pv2d.py` | `9759def97c70b7ae` | the producer: a copy of `2d-unfolding/unfold_2d_omnifold_unbinned.py` (`74a4ed69c3fa9c4a`). Every change is marked "PV-2D" (`diff` shows 122 changed lines): `--prior-ratio`, `--closure-ratio`, the two completeness guards, provenance fields, and the OmniFold helper imported from the deploy rather than the hardcoded cluster root (OI-136). Without the two flags its path is the original's. |
| `pv2d_lib.py` | `03aedc97c0941bcc` | reweight, guards, ratio construction, readouts (numpy only) |
| `make_ratios.py` | `c9483f3c957c1f35` | §3 |
| `pv2d_analyze.py` | `70f2740643f7d0b6` | §5 controls and §6 readouts; `--nc-only` decides the pilot |
| `test_pv2d.py` | `5e8666ed928db264` | 30 synthetic controls, each guard tested in the direction it acts (all pass locally and on Perlmutter at `3631ea3f`) |
| `config.json`, `tasks.tsv`, `sbatch_pv2d.sh` | `59a8bdce24c132e2`, `ec33c8dfa8823137`, `dd6c86754d69413d` | pins, the task table, the launcher. `config.json` gained the flux file's sha256 and the omnifile's size and mtime after the ratio build; neither enters `make_ratios.py` |

**Unchanged code the runs use:**
- `unbinned_unfolding/python/omnifold.py` `e96234124a31edd7`: byte-identical to the deployed cluster checkout's;
- `nd-unfolding/mnv_guarded_run.py` `30162f57771c9d5a`;
- `3d-unfolding/genie/gen5d_to_rootpreds.py` `bd7d0d7f82b73cf3`: the same bytes the gen5d flux-fix build ran.

**Inputs** (`config.json`; the readout checks each one and records it):
- the omnifile `2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root`, E_U's input, read in place in the
  deployed checkout's directory. It is 171,117,087,867 bytes, mtime 2026-07-08 08:08:15 PDT, and is identified by
  size and mtime, not hashed; NC is its numerical identity check;
- the flux file `2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root` `d40aea69235cdc98…`;
- E_U (above);
- the adopted Q on the 205 cells: CFS `2d-closeout-stageF-rebuild-20261018/outA/cov2d_Q_205.npz` `771e49a5…`,
  read only (`stageF/rebuild/REPORT.md`);
- the published release `2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root` `6c6dce72…`, as
  `state/uqpaper-median-20261006/paper_median.py` reads it.

**Deploy.** A clean clone at the pin under `$PSCRATCH/pv2d-20261023/deploy/repo`. `sbatch_pv2d.sh` refuses to run
unless HEAD equals the pin and no tracked file is modified, and it never overwrites a product. Each unfold runs
through `mnv_guarded_run.py --expect-root <deploy>`. The launcher also refuses untracked files in the two import
directories (`2d-unfolding/pv2d/`, `unbinned_unfolding/python/`).

**Environment.** The deploy's `setup_salloc_env.sh` activates `root_6_28`: Python 3.11.14, ROOT 6.28/12, LightGBM
4.6.0, scikit-learn 1.8.0, measured on a login node from the clean clone on 2026-10-23. Two of its `source` lines
point to gitignored build trees a clean clone lacks: the RooUnfold build and MINERvA101/PlotUtils. The producer
imports neither: it bypasses RooUnfold and reads the flux from a ROOT file. Sourcing the shared checkout's copies
instead would put that tree on `PYTHONPATH`, the OI-136 hazard. NC is the numerical check that nothing E_U used is
missing.

## 5. Runs and controls (pass rules fixed now)

| task | mode | r | role |
|---|---|---|---|
| `data_tune_v1` | data, `--prior-ratio` | 1 | **NC**, and the pilot |
| `data_genie_mec`, `data_nuwro`, `data_gibuu` | data, `--prior-ratio` | the vertex | the readout |
| `closure_tune_v1` | `--closure --closure-ratio` | 1 | PC closure floor |
| `closure_nuwro` | `--closure --closure-ratio` | NuWro | PC closure bias |
| `data_nuwro_sq`, `closure_nuwro_sq` | as above | NuWro ρ² | PC fallback, only if PC is NOT_POWERED |

**Integrity (each run; a failure makes that run not a result, and `pv2d_analyze.py` refuses):**
- the product's recorded ratio sha256 equals the declared file's;
- its `driverSha256` and `omnifoldHelperSha256` equal the deploy's `unfold_2d_pv2d.py` and `omnifold.py`, and its
  helper file is the deploy's;
- its `runConfig` equals the declared settings: 5 iterations, `--use-weights`, purity, seed 42, lgbm, cpu, branch
  selection "all", no universe or bootstrap, the declared omnifile and flux file, and closure only on a closure task;
- on a data run, each of these equals r per cell to 1e-9 against `data_tune_v1`, so all three weights moved:
  - `hTruth2D` (w_truth);
  - `hEffNum` (w_reco, truth- and reco-passing rows);
  - `hOFTruthDenom2D` (the denominator);
- also on a data run, `hOFCompleteness2D` equals the nominal one to 1e-9, and both completeness guards are recorded
  and ≤ 1e-9;
- on a closure run, `hTruthRew2D / hTruth2D` = r per cell to 1e-9.

**NC, the nominal control.** `data_tune_v1` against E_U on the 205 reported cells. **PASS iff max |x/x_EU − 1| <
1e-5** (s5p got below 1e-5 relative); bitwise equality is reported. `data_tune_v1` runs first, alone. **No other
job is submitted unless NC passes.** On FAIL I stop and report to the director; no vertex result is produced.

**PC, the positive control** (`pv2d_lib.positive_control`):
- **Vertex.** NuWro, fixed by the rule "largest median |r − 1| over the 205 reported cells", applied to the §3 files
  before any unfold (NuWro 0.063, GENIE+MEC 0.032, GiBUU 0.025).
- **Quantities.**
  - shift = x(data, NuWro prior) / x(data, Tune v1 prior) − 1;
  - bias = x(closure at NuWro truth, Tune v1 prior) / x_true(NuWro) − 1, from `hXSec2D` and `hTruthRewXSec2D`;
  - both relative, per reported cell.
- **Theory.** By the linear-response relation (s5p amendment 3), shift ≈ −bias.
- **Rule.** Take the cells with |bias| > 1%.
  - **NOT_POWERED** if there are fewer than 20 such cells.
  - Otherwise, **PASS iff** the Pearson correlation of shift with −bias is ≥ 0.7 **and** the least-squares slope
    (through the origin) is in [0.67, 1.5]. Otherwise **FAIL**.
- **NOT_POWERED → the fallback.** Run `data_nuwro_sq` and `closure_nuwro_sq` once and apply the same rule to them
  (ρ² doubles the departure in log). If the fallback is also NOT_POWERED or FAIL, PC is not passed. The readout
  reads the fallback only when the primary is NOT_POWERED, and then the fallback decides.
- **A FAIL or an unpassed PC** means the test has not shown that it can see a bias. h is then reported as a
  measured number labelled "positive control not passed", and is **not** evidence about model dependence, per the
  assignment's "a null result without a positive control does not count".
- **Reported beside the rule:**
  - the closure floor (`closure_tune_v1` against its own truth: median, p90, max);
  - the 2D analogue of amendment 6's measurement: the fraction of the |bias| > 1% cells where |shift| ≥ |bias|.
    In 5D it held in 52–78% of cells.

## 6. Readouts (descriptive; no pass/fail)

For each vertex (GENIE+MEC, NuWro, GiBUU), on the 205 reported cells, the relative shift against `data_tune_v1`:
- the median, 90th percentile and maximum of |shift| (with the maximum's cell);
- the signed median;
- the integrated (area-weighted) total's shift.

**The envelope** is h = max over the three vertices of |shift| per cell, with its median, p90, max and the
dominant vertex's cell count.

**Comparisons of h:**
- with the adopted σ_tot: Q = S5 + C_PL, per cell √diag(Q)/E_U (median 6.45%; `values.tex:140`,
  `DECISION-20261017-joseph-2d-adopt-s5-plus-playlist.md:45`). Reported: the medians of h and σ, the quantiles of
  h/σ, and the fractions of cells with h > σ and h > σ/2;
- with the published per-bin total uncertainties (√diag TotalCovariance / x_paper, median 6.85%), the same way;
- with the scalars 6.45% (primary) and 6.87% (the superseded VL172 value; secondary reference only).

The amendment-6 caveat is carried in the readout file and the report: **h is evidence about model dependence at
these vertices, not a per-cell bias bound** (`state/s5p/contract-amendment-6-review1-repairs.json`,
`LOW_items.bound_wording`).

## 7. Compute

**Grant.** ≤ 20 CPU node-h under the 2D closeout delegation (`AUTHORIZATION-20261012-2d-closeout-delegation.md`
§3). Account m3246, QOS regular (each job > 30 min, so not debug), never premium; one exclusive CPU node per task.

**Sizing from a measured pilot.**
- **The pilot.** `data_tune_v1` is projected at 60 min: the July record of the same unfold configuration on the same
  omnifile, job 55677845 (the July CV, `uq/purity_newomni/`; 43.1 min, 18:05:49–18:48:56 UTC; log
  `2d-unfolding/unfold_MEFHC_uni_full_CV_55677845.out`), × 1.4 for today's slowdown (`state/gpu-timing-20261023/REPORT.md`). Its limit is 1:15
  (1.25×).
- **The other data runs** are projected at the pilot's measured elapsed time.
- **The closure runs** are projected at 1.6× the pilot's elapsed time: step 1 trains on about 40 M rows (20 M
  pseudo-data plus 20 M MC reco) against about 24 M on data.
- **Limits** are 1.25× each projection, rounded up to the minute. I stop and report any job beyond 1.25× its
  projection, as the limit enforces.

**The cap.** Projected total: 1 + 3 + 2 × 1.6 = 7.2 pilot-units (about 7 node-h at 60 min), plus 2.6 if the fallback
runs. **Hard cap: 12 charged CPU node-h**, the sum of the limits, recomputed from the pilot. I check with the director
before submitting anything that would take the worst case above 12, and never go above 20.

**Ledger.** `LEDGER.tsv` in this directory, one row per job: job id, QOS, state, elapsed, charge (elapsed × billing/256,
one CPU node = 256), task and log path.

**Storage.** Everything goes to `$PSCRATCH/pv2d-20261023/` (products about 60 kB each, logs, inventories); nothing
goes to CFS. Every product's path and sha256 go in `receipts/`.

## 8. Options for the binding (not run unless the director admits them)

1. **The refined arm.** The same three vertices plus nominal under RE-2's refined estimator: configuration (a) with
   `--bkg-mode negweight-refined` and the 400/31 refinement classifier, `random_state` 45
   (`2d-unfolding/re1/re1_2d.py:70-75`). It costs four unfolds, about 5 node-h. It would need the 400/31 override in
   the copy (a further PV-2D change) and its own nominal control against the RE-1 C2 refined central product. It is
   not cheap enough to include by default.
2. **The literal reference** (r = g_k / Tune v1 prior, §2), gated the same way, as a sensitivity on the convention:
   three more unfolds (about 3 node-h). I recommend against it. Its departures are dominated by the shared
   standalone-generation artifacts described in §2.

## 9. Pre-run review

An independent read-only reviewer (a fresh subagent given the code, the assignment and the s5p design, not my
conclusions) reviewed `8315aa1d`. It found no blocker. It recomputed every ratio file from `projections.json`
bitwise, and it confirmed the cell convention, the closure reference, the helper path, the readout's sign and
indexing, and that the producer diff is clean.

It found two major gaps in what the readout verifies:
- no check that the products share one driver, helper and run configuration;
- no check that w_reco and the denominator moved, only w_truth. It showed this with a mutation that removed the
  w_reco multiply and passed all 24 tests.

It also found minor items:
- the readout did not enforce NC or the fallback rule, or label h;
- the launcher did not refuse untracked files and had a replace race;
- the flux file was not pinned;
- some argmax fields were list positions, not cell ids;
- a cosmetic title;
- a wording error (100% for 99.96%).

All are repaired at `3631ea3f` (commit message lists them), and the w_reco mutation now fails a test. Two items are
left as stated, not changed:
- the omnifile is identified by size and mtime, not hashed;
- the ratio error assumes independent samples (conservative if GENIE+MEC shares events with GENIE CV).

## 10. Not done, limitations and deviations from the assignment

- **Deviation (needs binding):** the vertices are generator/GENIE-CV shape ratios on the Tune v1 prior (the s5p
  convention), not "the prior reweighted to the vertex". Tune v1 is the nominal and contributes zero shift. Reason
  in §2.
- **Deviation (needs binding):** the statistical gate and the coarse pooling (§2–3); GiBUU on p_∥ < 10 GeV/c only.
- **Residual generator noise** (median 2–3% per fine cell, ≤ 5% by construction) enters each shift and is not
  separated from it. The OmniFold response to high-frequency structure in the prior is largest where resolution is
  poorest, so h may include a noise term of up to about that size in those cells. No noise-only run is declared.
- **The positive control is at one vertex** (NuWro). The linear-response relation is not tested at GENIE+MEC or
  GiBUU. <!-- absence-ok: scope of this declaration's positive control -->
- **No coverage statement.** Only E_U's configuration is tested, at one seed (42).
- **h is a sensitivity** over three vertices, not a hull bound and not a covariance. The 2D-versus-5D comparison is
  the director's.
