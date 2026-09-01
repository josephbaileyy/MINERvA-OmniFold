# PREDECLARATION 2026-09-01 — quarantine cause 3, `M(ii)` estimator-seed magnitude

**Status: written before the measurement. No measurement has run and this document contains no result.**
It predeclares only cause 3's `M(ii)`, *"the magnitude of what varying seeds would have
contributed"*, for the background-aware, post-J28 scalar-5D candidate. `M(i)` is already satisfied
and is not reopened here: the two throw products carry fixed-seed null norms
`1.9706093906025077e-50` (pre-J28) and `5.8223488501140625e-50` (J28-corrected), and the candidate
stamps carry `upstream_fixed_seed_null_norm = 5.8223488501140625e-50` against tolerance `1e-12`.

## Authority and boundary

Joseph authorized this work directly on 2026-09-01:

> *"I authorize you spend the hours and drafting to investigate and fix the causes"*

That authorizes the bounded measurement specified here. It does **not** authorize adopting a
covariance, adding an estimator-seed block to a budget, changing a central value, moving a gate,
discharging cause 3 as a whole, or editing `docs/analysis-note/values.tex`. Gate 2 remains FAIL and no
scalar-5D covariance is adopted. A result from this measurement must be recorded and reviewed before
any further conclusion is taken.

## 1. Exact quantity

The primary magnitude is

\[
  m_{\rm seed} = \sqrt{\operatorname{Tr} C_{\rm seed}}
  \quad [\mathrm{cm}^2/\mathrm{nucleon}],
\]

where `C_seed` is the unbiased (`1/(N-1)`) covariance over **exactly 12** scalar-5D cross-section
vectors produced from one fixed data/MC draw while changing only the LightGBM/OmniFold estimator
seed. The population is the finite declared set, not an inferred distribution:

```
estimator seeds: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
fixed data/MC draw seed: 0
estimator: lgbm
iterations: 5
axes, in flat-C order: p_T, p_parallel, E_avail, q3, W
support: candidate-reported bins, selected by candidate CV > 0 (predicate, not a hardcoded count)
```

For vectors `x_s` on that support,

\[
  \bar{x}=\frac1{12}\sum_s x_s,\qquad
  C_{\rm seed}=\frac1{11}\sum_s(x_s-\bar{x})(x_s-\bar{x})^T.
\]

Two reductions are reported because one scalar trace cannot detect a seed contribution concentrated
in a subset of bins:

\[
 f_{\rm agg}=\frac{m_{\rm seed}}
 {4.357790406860002\times10^{-38}},\qquad
 f_{\rm med}=\operatorname{median}_{i:\,x_i^{\rm cand}>0}
 \frac{\sqrt{(C_{\rm seed})_{ii}}}{\sigma_i^{\rm cand}}.
\]

The aggregate denominator is the candidate's stamped `sqrt_tr_old`. `sigma_i^cand` is read from the
diagonal of `hCov_combined5d_total_uthrow` in the same candidate; it is not reconstructed from a
rounded note macro. The full `C_seed`, its diagonal, `m_seed`, `f_agg`, and `f_med` are all outputs.

### Inputs

The fixed scan input is named in advance as

```
nd-unfolding/bank_sweep_5d_bkgaware/cv.npz
```

with the background-aware bank directory `nd-unfolding/bank_sweep_5d_bkgaware/` as its required
companion population. It must be read with the post-J28 flux source

```
2d-unfolding/baseline_flux/flux_integral_universes_MEFHC.root
```

and compared to the candidate

```
nd-unfolding/uq_5d/readopt_20260811_footing/stamped_bkgaware_meancentered_20260812.root
```

whose committed receipt records SHA-256
`4f168e83eaeb4bc7191a4e13e219c7ff06556e5ad30b9df4fcc249e6720c7ec2`.

**Declared input-schema uncertainty:** `bank_sweep_5d_bkgaware/cv.npz` is the candidate sweep's shared
CV block, but by itself it is not a manifest of all 188 universe members and does not prove that a
fixed-draw runner has exercised the 100 PPFX flux normalizations. Before submission, the launcher
receipt must demonstrate that the fixed-draw input contains every array required by the estimator-only
runner and that its lineage reaches the same background bank and post-J28 flux treatment. If that
cannot be demonstrated without constructing a new packed input, the run is **INCONCLUSIVE BEFORE
EXECUTION** and must not substitute `of_inputs_5d.npz` or a CV-only legacy input. Creating a new packed
input would require its path, schema, source digests, and cost to be appended to a new pre-execution
record; it may not be filled in after a seed result exists.

### Outputs and required keys

The numerical artifact is fixed as

```
nd-unfolding/uq_5d/cause3_mii_20260901/cause3_mii_estimator_seed_magnitude.root
```

and the tracked receipt as

```
docs/orchestration/state/RECEIPT-20260901-cause3-mii-estimator-seed-magnitude.json
```

The ROOT must contain these exact keys:

| key | class | content |
|---|---|---|
| `hCov_cause3_mii_seed_reported` | `TH2D` | unbiased 12-member `C_seed` on candidate support |
| `hSigma_cause3_mii_seed_reported` | `TH1D` | `sqrt(diag(C_seed))` |
| `hMean_cause3_mii_seed_reported` | `TH1D` | 12-member mean vector |
| `hCandidateSigma_reported` | `TH1D` | candidate `sigma_i^cand` used in `f_med` |
| `sqrt_trace_seed` | `TParameter<double>` | `m_seed`, in `cm2/nucleon` |
| `candidate_sqrt_trace` | `TParameter<double>` | exact denominator `4.357790406860002e-38` |
| `f_agg` | `TParameter<double>` | aggregate ratio |
| `f_med` | `TParameter<double>` | candidate-support median ratio |
| `n_seeds` | `TParameter<int>` | `12` |
| `fixed_data_seed` | `TParameter<int>` | `0` |
| `n_iterations` | `TParameter<int>` | `5` |
| `ndim` | `TParameter<int>` | `5` |
| `reported_nbins` | `TParameter<int>` | measured support cardinality; predicate remains authoritative |
| `estimator` | `TNamed` | `lgbm` |
| `estimator_seed_set` | `TNamed` | literal comma-separated `1,...,12` |
| `axes` | `TNamed` | `p_T,p_parallel,E_avail,q3,W` |
| `centering` | `TNamed` | `ensemble-mean, unbiased-1/(N-1)` |
| `input_path` / `input_sha256` | `TNamed` | exact fixed input identity |
| `candidate_path` / `candidate_sha256` | `TNamed` | exact candidate identity |
| `background_bank_path` / `background_bank_manifest_sha256` | `TNamed` | background footing identity |
| `flux_source_path` / `flux_source_sha256` | `TNamed` | post-J28 flux footing identity |
| `code_commit` | `TNamed` | executed clean-tree commit |

The JSON receipt must repeat those scalars and identities; list all 12 member paths, SHA-256 digests,
read-back estimator seeds, exit codes, and elapsed seconds; record the candidate's source stamps; and
carry `adopts_nothing: true`, `moves_no_gate: true`, and `values_tex_untouched: true`. A ROOT existing
without this receipt is not a completed measurement.

## 2. Footing match, made falsifiable

The run is on the candidate's footing only if **all** checks below agree. Similar names, dates, or a
post-J28 code checkout do not substitute for them.

1. The candidate path and SHA-256 equal the values above, and its own keys read back:
   `centering_convention = mean-centered`,
   `combined_source = uq_universe_5d_covariance_combined_bkgaware.root`,
   `uthrow_source = unified_throw_cov_5d_fluxfix_20260806_full160.root`,
   `sqrt_tr_old = 4.357790406860002e-38`,
   `upstream_fixed_seed_null_norm = 5.8223488501140625e-50`, and
   `upstream_n_throws = 160`.
2. The full footing receipt names the same `combined_source` and inventories 169 vertical universes,
   18 lateral universes, and one CV. Within it, the background-bank manifest covers the 169 vertical
   members and the direct-driver manifest covers the 18 lateral members plus CV; each shows
   per-universe background treatment rather than a fallback to CV-frozen background weights.
3. The flux inventory contains exactly 100 contiguous PPFX universes `0..99`; Flux members use their
   own integrated flux through `flux_universe_bins`, not the CV integral. The flux ROOT digest and the
   executing source digest are recorded.
4. The candidate-support predicate is read from the candidate CV and is identical as a set for every
   seed output; the axes, edge arrays, flatten order, POT, nucleon count, and five-iteration setting
   agree exactly.
5. Only the estimator seed changes. The fixed data/MC draw seed remains `0`; no bootstrap, split,
   throw, detector-universe, or flux-universe identity is allowed to vary between the 12 members.

**This is the falsifier for the footing claim:** any disagreement above, including a missing flux
inventory or a fallback to `of_inputs_5d.npz`, makes the measurement `INCONCLUSIVE / WRONG FOOTING`.
No magnitude may then be quoted as cause 3's `M(ii)`.

## 3. Acceptance threshold, fixed before the result

`M(ii)` is **MET** only if both conditions hold:

```
f_agg <= 0.0415
f_med <= 0.0274
```

Equivalently, the aggregate leg requires

```
m_seed <= 1.808483018846901e-39 cm2/nucleon
```

against the fixed candidate denominator. There is no single absolute `m_seed` that can replace the
`f_med` condition: the same trace can be diffuse or concentrated, so the per-bin leg is independently
binding.

### Non-tuning justification

The boundary is derived from the precision already used to print the two affected quantities, not
from a seed result. Adding an omitted independent contribution `S` to a reported uncertainty `U`
changes it in quadrature, `U' = sqrt(U^2 + S^2)`. Requiring that change to remain below half of the
last printed unit gives

\[
  S/U \leq \sqrt{2\delta+\delta^2},
\]

where `delta` is that half-unit divided by the printed value. The three-significant-figure aggregate
quantity gives `4.15%`; the four-significant-figure median quantity gives `2.74%`. The thresholds were
therefore fixed by publication precision before `m_seed` exists. They are deliberately not placed
near an expected answer: a threshold chosen to make the eventual number pass is not a criterion.
If the printed precision changes before execution, these numerical thresholds are void and must be
redeclared before the run; changing only the central printed value does not invite tuning.

### Why the F7 sampling-floor rule does not apply

F7 compares an ensemble **mean shift** with the finite-`N` sampling floor
`sqrt(Tr C)/sqrt(N)`. Its `F7_FLOOR_MULTIPLE = 2.0` separates a shift consistent with finite-sample
mean fluctuation from one well above that floor. `M(ii)` instead measures the covariance generated by
changing estimator seeds. Under a true zero seed response the outputs can be identical and the
covariance is zero; `sqrt(Tr C_candidate)/sqrt(12)` is not a noise floor for `C_seed` and would import
systematic covariance into an estimator-noise test. The F7 factor `2.0` therefore has no principled
role in this acceptance decision. The publication-precision rule above tests the actual question:
whether the omitted contribution can move a reported value at its declared precision.

## 4. Exhaustive outcome branches

The branches are evaluated in this order; a validity failure dominates every numerical branch.

1. **INCONCLUSIVE / WRONG FOOTING.** Any check in section 2 fails, the declared packed input does not
   contain the runner's required arrays, a required source/digest is absent, or the 100-universe
   post-J28 flux treatment cannot be tied to the scan input. Stop before or after the failed check and
   report no `M(ii)` magnitude.
2. **INCONCLUSIVE / VACUOUS SEED VARIATION.** Read-back seed set is not exactly `1..12`, the fixed-draw
   identity changes, any member is missing/non-finite, or any two per-seed output digests collide.
   A zero spread in this branch is not a favourable result; it is evidence that the knob may not have
   reached the estimator. This is the execution falsifier.
3. **MET.** All validity checks pass and both `f_agg <= 0.0415` and `f_med <= 0.0274`. This grades only
   cause 3's `M(ii)` for this candidate and authorizes nothing downstream.
4. **NOT MET — AGGREGATE (unfavourable).** Valid measurement, `f_agg > 0.0415` and
   `f_med <= 0.0274`. The omitted contribution can move the aggregate at its printed precision.
5. **NOT MET — PER-BIN (unfavourable).** Valid measurement, `f_agg <= 0.0415` and
   `f_med > 0.0274`. Aggregation hides a contribution that can move the median per-bin quantity.
6. **NOT MET — BOTH (unfavourable).** Valid measurement and both thresholds are exceeded.

Boundary equality is MET because the conditions are written `<=`; non-finite values are branch 1 or
2, never comparisons that happen to return false. The named scientific falsifier is a valid,
footing-matched result above either threshold. The named instrumentation falsifier is a seed/digest
collision or any seed stamp inconsistent with the declared set.

## 5. What this measurement cannot settle

- It cannot reopen or improve `M(i)`; that null is already measured.
- It cannot discharge cause 3 as a whole, close any other quarantine cause, change CAND/QUOTED
  counts, adopt a covariance, move Gate 1 or Gate 2, or touch `values.tex`.
- It does not add `C_seed` to the uncertainty budget. A magnitude measurement and budget adoption are
  different decisions.
- It measures estimator variation at one fixed data/MC draw. It does not measure seed-by-draw
  interaction, coverage, a new central estimator, or the behaviour of seeds outside `1..12`.
- It does not by itself resolve whether the candidate's two historical estimator-seed baselines
  (sweep-side `42`, throw-side `1000`) must be varied jointly in a full composite-member scan. The
  fixed-draw scan is the quantity `CRITERIA` identified through the 12-seed AI1 precedent; treating it
  as a substitute for a full two-baseline composite scan would require a separate ruling.
- It cannot turn the July `\gbdtAiEstTrace` result into candidate evidence. That value remains an
  auxiliary robustness check on `of_inputs_5d.npz`, with no flux universes and no bkgaware sweep.

## 6. Cost and scheduler request, re-derived in task-hours

The estimate is derived from the recorded execution shape, not from a Slurm time limit. The original
packed run used 12 local estimator fits at `CONC=6`: two waves. The recorded tail measured about
20 minutes per wave, and the combine completed about 3 minutes after all 12 members existed. Therefore

```
GPU allocation:  2 waves * 20 min = 40 min = 0.667 GPU task-h
CPU combine:                              3 min = 0.050 CPU task-h
conservative declared cost envelope: <= 1.0 GPU task-h + 0.1 CPU task-h
```

The scheduler shape is one GPU task on the `gpu` partition with shared QoS, one A100, 32 CPUs,
`--time=01:30:00`, running 12 local fits at `CONC=6`, followed by one CPU combine task with
`--time=00:10:00`. Thus the scheduler task count is **2** (one GPU producer task, one CPU combine
task), while the scientific replica count is **12**. The requested walltime ceilings would be
`1.5 GPU task-h + 0.167 CPU task-h`; they are ceilings, not the cost estimate.

Numerically this fits beneath Joseph's ratified **arm 1 bootstrap ceiling of 20 GPU task-hours** and
**arm 7 combine ceiling of 5 CPU task-hours**. Those ceilings are denominated in task-hours — sums of
`ElapsedRaw` over tasks — by `DECISION-20260901-joseph-delegated-ceiling-unit-is-task-hours.md`.
They belong to the forward-rehearsal table and are used here only as conservative per-arm envelopes;
they do not themselves authorize this new arm. The direct 2026-09-01 authorization on the face of
this document is the authority.

**Cost uncertainty that must survive into the receipt:** the measured 20-minute waves were on
`of_inputs_5d.npz`, not on a demonstrated candidate-footing packed input. The estimate is transferable
only if the preflight establishes an equivalently packed runner input. If candidate-footing preparation
or direct ROOT reads add a scheduler task or change the per-fit execution shape, this cost derivation is
void and the run must return for a new pre-execution cost declaration. The `01:30:00` request must never
be multiplied by 12; twelve local fits share one allocation in two waves.

## 6b. PREFLIGHT RESULT 2026-09-01 — the footing EXISTS and §6's cost derivation is VOID by its own terms

Run before submission, as §7 requires. **Both halves of §6's stated uncertainty resolved, one
favourably and one not.**

**FAVOURABLE — the candidate footing is available, and it is not a packed input at all.** The bkgaware
arm does not read `of_inputs_5d.npz`; it reads ROOT directly.
`sbatch_unfold_5d_detector_bkgaware_gpu.sh:278-279` sets
`OMNIFILE = runEventLoopOmniFold_5D_MEFHC_universes_full_bkgaware.root` and
`FLUX_MC = 2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root`, and passes them as `--omnifile` /
`--mcfile` at `:294` and `:308`. **The `OMNIFILE` exists on the cluster at 171,117,093,365 bytes.** So
§2's falsifier — *"a fallback to `of_inputs_5d.npz`"* — is avoided, and there is no packed-input schema
to design.

**UNFAVOURABLE — and it is the branch §6 wrote itself a rule for.** §6's cost derivation assumed the
packed shape: *"12 local estimator fits at `CONC=6`: two waves… about 20 minutes per wave"*, giving
`0.667` GPU task-h. **Reading the 171 GB ROOT directly is a different per-fit execution shape.**
Measured on the arm that performs exactly this operation on exactly this footing — `det5dBKG`, job
`57753244`, one bkgaware unfold per task:

```
n = 19    mean 43.5 min    min 41.9    max 45.5    total 13.76 task-h
```

A tight distribution, so it transfers reliably. **Twelve replicas at 43.5 min is ≈ 8.7 GPU task-hours,
about 13× the declared `0.667`**, and the scheduler shape becomes a 12-task array plus a combine —
**13 scheduler tasks, not 2.**

§6's own rule fires: *"If candidate-footing preparation or direct ROOT reads add a scheduler task or
change the per-fit execution shape, this cost derivation is void and the run must return for a new
pre-execution cost declaration."* **Both triggers are met. THE RUN WAS NOT LAUNCHED.**

**What is unaffected.** §1's quantity, §2's footing checks, §3's threshold and its non-tuning
justification, §4's branches and §5's limits all stand — none of them depends on the execution shape.
`8.7` GPU task-hours is still **inside** the ratified arm-1 envelope of 20 GPU task-hours, so this is a
mis-declaration to correct, not an affordability problem. **A corrected pre-execution cost declaration
is required before the first estimator fit, and Joseph authorized the launch against `0.667`, not
against `8.7`.**

## 6c. CORRECTED PRE-EXECUTION COST DECLARATION 2026-09-01 — authorized by Joseph against THIS number

§6b voided §6's derivation. This replaces it, and Joseph authorized the relaunch **against the figure
below**, having been shown the 13× correction first:

> *"relaunch it"* — Joseph, 2026-09-01, after being told the real cost is ≈`8.7` GPU task-hours and
> 13 scheduler tasks rather than the `0.667` and 2 he had originally approved.

| | |
|---|---|
| scientific replicas | **12** (estimator seeds `1..12`, CV unfold, no data draw) |
| scheduler tasks | **13** — a 12-task GPU array plus one CPU combine |
| per-replica basis | `det5dBKG` job `57753244`, the same operation on the same footing: mean **43.5 min**, min `41.9`, max `45.5`, n=19 |
| **expected GPU cost** | **≈ 8.7 GPU task-hours** |
| expected CPU combine | ≈ `0.08` CPU task-hours |
| walltime request | `--time=01:30:00` per GPU task — **2× the observed max**, matching `det5dBKG`'s shape |
| worst-case ceiling | `12 × 1.5 = 18` GPU task-hours if every task ran to its limit |

**The ceiling is stated as well as the estimate, because the ceiling is what a breach would be measured
against.** `18` sits inside the ratified arm-1 envelope of **20 GPU task-hours**, but with only 10%
headroom — so **if any task is resubmitted after a failure, this declaration is void again** and the
arithmetic must be redone before the retry, not after.

**Why the data-draw seed needs no flag on this footing.** §1 fixes the data/MC draw seed at `0`. The
old packed scan achieved that with `bootstrap_nd.py --fixed-data-seed 0`, because a bootstrap replica
draws. **A CV unfold does not draw at all** — `sbatch_unfold_5d_detector_bkgaware_gpu.sh:290-295` runs
the CV arm with no draw parameter — so "one fixed data/MC draw" holds by construction here, and §2's
check 5 (*"only the estimator seed changes"*) is satisfied by passing only `--seed`. **This is a
footing difference, not a relaxation**, and it is recorded so no reader treats the missing flag as an
omission.

## 7. Terminal instruction

This file predeclares; it does not launch. No result belongs in this file. Any outcome goes only into
the separately named ROOT and receipt, with this predeclaration's committed digest recorded before the
first estimator fit starts. If the input-footing or cost uncertainties above are not resolved before
submission, the only permitted branch is **INCONCLUSIVE BEFORE EXECUTION**.
