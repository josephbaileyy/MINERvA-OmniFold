# ENS1 DECLARATION: an ensemble-averaged estimator, on simulated pseudo-data (2026-11-07)

**For** audit by `coverage-5b-audit` and binding by the director. **Nothing has run, and nothing runs before the
binding.** This is step 2 of the rounding-instability lane. It is declared **before RS1's outcome is read**
(`RS1-BINDING-1.md` ruling 5). When this was written, RS1's dry run (job 60970044) had been submitted and no RS1
product had been read.

**Written by** the rounding-instability lane, a Claude session named `director-helper-3`, under the director's
handoff `HANDOFF-20261106-lane-rounding-instability.md` §2 item 2, which lives outside the repository. All repository
citations are at `origin/main` `d53b5f01` unless stated.

**Authority.**
- `DECISION-20261106-joseph-diagnoses-jinst-corrections.md:40-41`, item 1.3: "Then an ensemble-averaged estimator is
  declared as a variant. It is declared, audited and bound before it runs."
- `DECISION-20261106-joseph-plateau-next-work.md:45-46`, item 1: "then an estimator that averages over rounding
  perturbations is declared as a variant."
- Compute: `DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md` item 2 (#640). The two stages' caps
  together, 101.0 CPU node-h (§8), are below half the group balance (1,774.4 node-h remaining, iris at
  2026-11-07T17:52Z, RS1 dry-run connect log; the receipt is committed with RS1's dry run). The director bound the
  scale without returning to Joseph: N = 96, P = 10, stage 2 conditional (the director's rulings of 2026-11-07, in
  correspondence; recorded with the binding).

**CITABLE FOR:**
- the design, criteria, price and code plan of ENS1, as declared;
- once its outcome record exists: whether the ensemble estimator E₉₆ meets FD-STAB's stability bar on the declared
  input, and (only if it does) whether it is no worse in bias than configuration (e) at the 17 F0b truths.

**NOT CITABLE FOR:**
- any result before the outcome record exists;
- any statement about the real data, or any coverage statement;
- a mechanism. RS1 alone can name one. ĉ (§7.1) is a description, not a mechanism test;
- the replacement of the reported estimator. That is Joseph's decision (handoff §2 item 2);
- bias at any truth beyond the 17, or with nuisances drawn, or at the full MC sample;
- a reinterpretation of `OUTCOME-20261105-fd-stab-none-pass.md`. NONE_PASS stays terminal for B2, B3a and B3b.

## 1. The question

Configuration (e), the reported five-observable estimator, is bitwise invariant to its training seed and row order,
but its output moves under rounding-scale perturbations of its inputs. On the FD-STAB stability input the control
reads mean median 0.759 and mean maximum 6.83 statistical σ against a bar of 0.3 / 1.0
(`fd/receipts-stab-a1r/readout/readout-2/fd_stab.json:6-7`, sha256 `653356ae…`; `OUTCOME-20261105-fd-stab-none-pass.md`).

**Does the mean of N fits, each at its own fixed rounding-scale perturbation of the input, meet that bar?** If it does,
does it worsen bias? The estimator is E_N; configuration (e) is F.

## 2. The estimator E_N

**2.1 Definition.** For an input y (the coordinates MC truth, MC reco, observed, and background template):

  E_N(y) = (1/N) Σ_{k=1..N} F(y + δ_k(y)),   N = **96**,

where F is configuration (e) unchanged (the bound OmniFold classifiers and regressor and the Stay-Positive
refinement, as FD-STAB's control ran it), run in float64 coordinates, and δ_k is the **internal jitter**:

  δ_k(y) = u_k ⊙ spacing₃₂(round₃₂(y)),   u_k ~ U(−½, ½) i.i.d. per coordinate, from `default_rng(10000 + k)`,

so each step lies within **±½ of the value's float32 spacing**, the protocol's own scale
(`s5e_trace.py:362-364`: `rng.uniform(-0.5, 0.5, out.shape) * ulp`). It is applied **to y at full precision in
float64**, with δ_k = 0 wherever round₃₂(y) equals a grid edge of its axis (the
edge-safe rule of `s5e_trace.jitter_coords`, `nd-unfolding/s5e_trace.py:365-367`). The draws u_k have the shape of
each coordinate array and are drawn in a fixed order (MCgen, MCreco, measured, bkg_reco), so δ_k is a fixed function
of k and the array shape: **E_N is one deterministic estimator**, the same for every input it is given.

- **The scale is pinned by a test in both directions:** over a large fixture, every |δ_k| / spacing₃₂ is ≤ ½, and its
  maximum exceeds 0.49. A REQUIRED mutant that halves the scale (the ±¼ of this declaration's first head, audit ENS-2)
  is killed by it.
- **Internal seeds 10001–10096** are disjoint from the protocol's jitter seeds (1–51, `s5p_numerics` pairs), from
  RS1's seed 0, and from the pseudo-seeds 990000 and 991000. A test checks the disjointness.
- **The mean is of the unfolded cross section** (`xsec_flat`). s5e's 153 functionals and the 16 cells are linear in
  it (`estimator_stability_analyze.functionals`, `cell_matrix`), so the mean of the functionals is the functional of
  the mean.

**2.2 The trap this definition avoids.** `s5e_trace.jitter_coords` casts its input to float32 before stepping
(`s5e_trace.py:358`, `x32 = np.asarray(x, np.float32)`). Reusing it as the internal jitter would round the
protocol-perturbed input y = x + δ_s back to x (except at powers of two), so E_N(x_s) = E_N(x) almost bitwise, and
E_N would pass the bar while averaging nothing the test probes. Any estimator that rounds its input to float32 first
passes the same way. Two other float32 casts sit on the path and are closed the same way:
- `s5p_numerics` runs an unjittered pair in float32 (`s5p_numerics.py:183-184`). The base input therefore runs as
  jitter seed 0, RS1's float64 unjittered path (`rounding_mechanism_probe.py:60, 282-288` at `e306087e`): seed 0
  returns `jittered(inputs, bkg, None)`, the float64 copy, and the internal jitter is added to it;
- `s5p_nullexp` unfolds in float32 (`s5p_nullexp.py:342`, `unfold_one(exp, np.float32, …)`). Stage 2 rebinds
  `s5p_numerics.unfold_one` in the closure process to run in float64 (§9).

**REQUIRED tests and mutants** (the director's ruling 2):
- a test that E_N(x_s) ≠ E_N(x) on a fixture whose F is sensitive below float32 resolution, and that its inputs differ
  from E_N(x)'s at every k;
- a REQUIRED mutant that reintroduces the float32 cast (the internal jitter through `jitter_coords(y, 10000 + k)`),
  killed by that test;
- a REQUIRED mutant that leaves the closure's `unfold_one` in float32, killed by a test that the closure fits differ
  across k on a sensitive fixture;
- a REQUIRED mutant that runs the base unjittered pair `-:-` (float32) instead of seed 0.

**2.3 The grid guard.** The total move |δ_s + δ_k| is below one float32 spacing, so a value off an edge cannot reach
it. The stability loop's own check refuses any product whose fine-grid membership changes (`s5p_numerics.py:186-191`,
exit 5), and since the internal jitter is added inside the rebound `jittered`, that check covers the total
perturbation. The closure runner has no such check; the wrapper adds it, with `s5p_numerics.cell_membership`
(`:73`), before any closure fit. A refusal is a failed task, so the run is INCOMPLETE (§4.4).

**2.4 What E_N is not.** It is not a bootstrap (the data are not resampled), not a seed ensemble (F is seed-invariant),
and not an average over pseudo-experiments. It averages over the rounding-level ambiguity of the inputs only.

## 3. Inputs: simulated pseudo-data only

The data never enter a product, as in FD-STAB (`FD-STAB-DECLARATION.md` §3, `check_namespace`, `DataNeverInAProduct`).

**3.1 Stage 1, the stability input.** FD-STAB's and RS1's exactly:
- `of_inputs_5d.npz` (sha256 `07fccc1a…`) and `bkg_dump.npz` (`2addac8f…`), at the paths of FD-STAB's queue
  (`fd/receipts-stab-a1r/connect/queue.tsv:2`);
- truth `eavail_shape`, amplitude 1, `state/s5n/eavail-ratio-gibuu-over-genie.json` (sha256 `45cc3e0a…`);
- `--construction pseudo`, pseudo-seed **990000**, `--config R --iters 5 --threads 32`, estimator seed 42;
- the 21 inputs: the base x (seed 0) and the protocol jitters x_s, **s = 1–20** (s5e's `jitter_coords`, the same
  seeds as FD-STAB's control products j1–j20). Each runs through E₉₆: 21 × 96 = **2,016 unfolds**, plus
  the one unfold of F₆₄(x) for G0 (§4.2).

**3.2 Stage 2, the bias input.** FD-STAB's 18 noise-free closures at the F0b truths (`FD-STAB-DECLARATION.md` §3.2;
`estimator_stability_probe.CLOSURES`, `nd-unfolding/estimator_stability_probe.py:315-336`), unchanged:
`s5p_nullexp.py --expectation --no-nuisance --mc-fraction half` at split seed 991000, with the bank and detector
directory of FD-STAB's queue (`connect/queue.tsv:58`).
- The 17 distinct truths run through E₉₆: 17 × 96 = 1,632 unfolds.
- **The determinism control:** A7 MnvTune is the same closure as nominal. It runs at k = 1 only (1 unfold), in a task
  separate from nominal's k = 1, at the same 32 threads. Its `xsec_flat` and `xtrue_flat` must both equal nominal's
  k = 1 bitwise, or the analysis stops.
- **The comparison F** is FD-STAB's own control closures, at the same truths, split and MC fraction, pinned in
  `fd/receipts-stab-a1r/full/SHA256SUMS` (the 18 `runs/control/closure/…_s991000.npz` lines; file sha256
  `e2c35e55…`). They are copied with `dd iflag=noatime` and verified against those lines. F is not re-run.
- **The truth vectors.** Every k of one truth must give the same `xtrue_flat` bitwise, since the internal jitter
  preserves grid membership. Otherwise the analysis stops.

## 4. Stage 1: the stability criterion

**4.1 The statistic is FD-STAB's §4.3, unchanged, with E₉₆ in place of F** (the director's ruling 3):
- r_j(s) = (U E₉₆(x_s))_j / (U E₉₆(x))_j − 1 over s5e's 153 reported functionals U;
- divided by σ_rel, the committed pseudo-data bootstrap σ of configuration (e) (`state/s5e/cand/assess_receipt.json`
  `sigma_rel_pct`, sha256 `84266e30…`, pinned in `estimator_stability_analyze.py:67`);
- the disjoint pairs (1,2), (3,4), …, (19,20), **P = 10**; per pair and functional the larger |r|/σ; then the median
  and the maximum over the 153 functionals;
- the criterion reads the **mean over the 10 pairs: mean median ≤ 0.3 and mean maximum ≤ 1.0.**
- It is computed by the bound `estimator_stability_analyze.stability_stats` (`:73-90`), which reads its module
  constant `N_PAIRS` at call time (`:77-88`). The wrapper rebinds it to 10 for the call and restores it in a `finally`,
  as RS1 rebinds bound names; G0 uses the same P = 10. Tests check that the result equals a hand computation, that at
  `N_PAIRS = 25` on 51 rows it equals the bound function unchanged, and that the constant is restored after a raise.
- **Why σ is configuration (e)'s, not E₉₆'s:** the bar is a fraction of the estimator's statistical scale, and ENS1
  does not bootstrap E₉₆: the bootstrap of a 96-fit mean costs 96× a bootstrap. This is disclosed (§10).
  <!-- absence-ok: scopes what this declaration's own design computes, not a claim that a result is absent from the repository -->

**4.2 G0, the informativeness gate, on the same seeds and the same base dtype.** The control F is evaluated with
the same statistic at P = 10, with r_j(s) = (U F(x_s))_j / (U F₆₄(x))_j − 1. **F must fail the bar**, or the verdict is
UNINFORMATIVE. FD-STAB's control at P = 25 fails it by a factor of 6.8 in the maximum, so G0 is expected to hold.
- **The jitters** F(x_s), s = 1–20, are FD-STAB's committed products `stab_control_b-_j1.npz` … `_j20.npz` (float64
  coordinates, `s5p_numerics.py:186-188`), copied with `dd iflag=noatime` in ENS1's connect and verified against
  FD-STAB's `SHA256SUMS`.
- **The base F₆₄(x) is F's float64 seed-0 base, computed by ENS1** (audit ENS-1): one unfold through the bound control
  stability path with pair `-:0` and RS1's seed-0 rebinding only (no internal jitter), in stage 1's dry run. FD-STAB's
  base `stab_control_b-_j-.npz` is float32 (`s5p_numerics.py:183-184`). Against it, F's r_j would mix the dtype change
  with the jitter, which is RS1's K3 contrast, and G0 could read informative where F passes on E₉₆'s own statistic.
- **A test refuses a float32 base for G0** (meta `coords` "float32" or `jitter_seed` null), with a REQUIRED mutant
  that admits FD-STAB's float32 base.

**4.3 The expectation, stated as an expectation and not part of the bar** (the director's ruling 3). If the 96 fits
behave as independent draws of F's rounding response, the statistic scales as 1/√96: about 0.077 median and 0.70
maximum. A fraction c of a fit's rounding variance that is a function of the input, not of δ_k, is not removed by
averaging. Under exact scaling the expected maximum reaches 1.0 at c* = 1/6.83² − 1/96 = **0.0110**.

**4.4 The stage-1 verdict.**
- **INCOMPLETE:** the full run did not finish (a STOP, a failed or refused task, or Slurm's limit). Nothing is graded,
  as in FD-STAB §6: the analysis requires every shard's DONE receipt with rc 0 and no STOP or FAILED beside it.
- **STOP:** a gate failed (§4.5). Reported to the director unrepaired; nothing is graded.
- **UNINFORMATIVE:** G0 fails. Terminal. Stage 2 does not run.
- **STAB_FAIL:** E₉₆ misses either bar. **A finding, and terminal for ENS1**: stage 2 does not run, and the record
  says so. ĉ (§7.1) is reported with its declared interpretation.
- **STAB_PASS:** E₉₆ meets both bars. Stage 2 runs after the director's go.

**4.5 Gates, before any reading.**
- **E1, one estimator:** every product carries the ENS1 meta block (§9) with one code digest set, the declared input
  digests, pseudo-seed 990000, internal seed 10000 + k, and protocol seed s; the 2,016 (s, k) cells are each present
  exactly once.
- **E2, the perturbations survived:** each product records the sha256 of its four coordinate arrays after the
  internal jitter. For every k, the 21 inputs' digests are distinct; for every s, the 96 internal seeds' digests are
  distinct. This is the run-time form of the trap test (§2.2), independent of F's sensitivity.
- **E3, the control's references:** the 20 control jitters equal FD-STAB's `SHA256SUMS` lines, and F₆₄(x) carries
  the ENS1 code digests, pseudo-seed 990000, `jitter_seed` 0 and `coords` float64.
- **E4, the σ receipt** is the pinned file and its functionals are s5c's 153 (`estimator_stability_analyze.py:284-288`).

**4.6 Power (§6 has the simulation).** At N = 96 and P = 10, P(pass) if c = 0 is 0.969 in the conservative Gaussian,
ρ = 0 reading, and 0.990 in the t3, ρ = 0 reading, which matches the record's SD51 best.

## 5. Stage 2: the bias criterion, conditional on STAB_PASS

**Runs only if stage 1 reads STAB_PASS, and after the director's go.** Its acceptance is fixed here (the director's
ruling 4). If stage 1 reads anything else, stage 2 does not run and its price is not spent.
<!-- absence-ok: a conditional rule of this declaration's own design, not a claim that a result is absent from the repository -->

**5.1 The metrics** are FD-STAB's §5.1: for each truth T, b = X / X_true − 1 on the 16 reporting cells
(`s1_assemble.functional_matrix` over the pinned H2 definition), RMS_T over the cells and MAX_T = max |b|. X is
E₉₆'s closure (the mean of 96 closure fits) or F's (FD-STAB's control closure).

**5.2 "No worse", with a measured floor.** E₉₆ is no worse at T if RMS_T(E) − RMS_T(F) ≤ Δ_RMS and
MAX_T(E) − MAX_T(F) ≤ Δ_MAX, computed by the bound `estimator_stability_analyze.no_worse` (`:118-129`), with:
- **F's per-cell rounding SD** s_F from FD-STAB's control base and 51 jitters, by the bound `cell_sd` (`:93-97`).
  It must equal the committed `cell_sd.control` (`fd_stab.json:575`, rounded to 1e-8) within 1e-8, or the analysis
  stops. The 31 jitters 21–51 are copied with `dd iflag=noatime` in stage 2's connect;
- **E₉₆'s per-cell rounding SD** s_E from stage 1: `cell_sd` of the base ensemble and the 20 jittered ensembles on the
  16 cells, 21 values, **20 degrees of freedom**;
- **the 95 % upper factors per SD.** FD-STAB's 1.20 is √(50/χ²₀.₀₅,₅₀) = 1.199 for 50 degrees of freedom. s_E has 20,
  so its factor is √(20/χ²₀.₀₅,₂₀) = **1.358**. `metric_noise` is linear in s, so s_E is passed to the bound
  `no_worse` scaled by 1.358 / 1.20. The floor is then 3 · √((1.358 n_E)² + (1.20 n_F)²), each SD with its own
  factor. A test checks this identity;
- **a zero floor is INVALID**, not worse (FD-STAB §5.2).

The familywise rate of a false "worse" over 17 truths × 2 metrics is FD-STAB's: about 0.5 % with correctly estimated
SDs, at most about 4.5 % if both are underestimated by their full factors.

**5.3 The stage-2 verdict.**
- **PASS:** no worse at all 17 truths. The outcome record calls E₉₆ **a stabilised variant** (handoff §2 item 2).
  Whether it replaces the reported estimator is Joseph's decision.
- **BIAS_WORSE:** worse at one or more truths, listed. E₉₆ is not described as a stabilised variant.
- **INVALID:** a zero floor at some truth. Terminal for this analysis; to the director.
- **INCOMPLETE / STOP:** as in §4.4.
- **The GiBUU readout** (A7 GiBUU and Stage 0c GiBUU biases, per estimator) is printed and used by no criterion
  (FD-STAB §5.3).

## 6. The declared power simulation

`ensemble/power/ens_power_sim.py`, seed **20261107**, output committed as `ens_power_sim.out.txt`. It is a model,
not a measurement:
- per functional, one fit's rounding deviation is σ_j · e, log σ_j ~ N(μ, τ²) over the 153 functionals, with an
  equicorrelation ρ between functionals and a common fraction c per input;
- (μ, τ) are fitted so that one fit at P = 25 reproduces the control's 0.759 / 6.83. The SD51 median and maximum are
  printed as a check the fit does not use (the record: 0.581 / 2.515);
- the grid: tail ∈ {Gaussian, Student t₃}, ρ ∈ {0, 0.5, 0.9}, N ∈ {64, 96}, c ∈ {0, 0.002, 0.005, 0.01, 0.02, 0.05},
  P = 10; 2,000 replications (Gaussian) or 300 (t₃, 96 fits averaged explicitly).

**The readings declared** (`ens_power_sim.out.txt`):

| reading | SD51 check (med / max) | N | c = 0 | c = 0.005 | c = 0.01 | c = 0.02 |
|---|---|---|---|---|---|---|
| Gaussian, ρ = 0 (conservative: its SD51 max overshoots) | 0.556 / 3.26 | 96 | 0.969 | 0.863 | 0.617 | 0.132 |
| t₃, ρ = 0 (closest to the record's SD51) | 0.650 / 2.36 | 96 | 0.990 | 0.947 | 0.883 | 0.447 |
| Gaussian, ρ = 0, at the first-proposed N | 0.556 / 3.26 | 64 | 0.843 | 0.626 | 0.337 | 0.033 |

P(pass) is the fraction of simulated studies meeting both bars. At ρ = 0.9 the c = 0 power falls to 0.87 (both
tails). **Why the pairs do not buy power:** every pair is measured against the one base ensemble E₉₆(x), so the
pairs share its noise. FD-STAB's across-pair SE understates the study-to-study spread of the mean maximum; that is
why N, not P, was raised.

## 7. Readouts with no criterion

**7.1 ĉ, the effective-N readout.** Per functional j, in σ units relative to E₉₆(x):
- v_w,j: the variance over k of the base input's 96 single fits F(x + δ_k) (ddof 1);
- v_b,j: the variance over the 21 inputs of E₉₆ (ddof 1);
- q_j = v_b,j / v_w,j − 1/96 and ĉ_j = q_j / (1 + q_j). Under the model of §4.3, v_b = σ²(c + (1 − c)/96) and
  v_w = (1 − c)σ², so ĉ_j estimates c_j.

Reported: the median of ĉ_j over the 153 functionals, and ĉ_j for the ten functionals with the largest per-functional
mean (over pairs) of the stage-1 statistic.

**The interpretation rule, fixed now, which never moves the verdict** (the director's ruling):
- v_b from 21 values has a relative SD of about √(2/20) = 0.32, so ĉ is resolved only above about
  ε = 0.32 / 96 = **0.0033**;
- **if STAB_FAIL** and the median of the top ten ĉ_j is ≥ c* = 0.0110, the record reads "the failure is carried by a
  component that averaging over rounding perturbations does not remove";
- **if STAB_FAIL** and it is ≤ ε, the record reads "no input-dependent component is resolved; the failure is
  consistent with the declared power (§4.6, §6) or with a heavier tail than the model's";
- **otherwise** (between ε and c*, or under STAB_PASS), ĉ is printed without a reading.

**7.2 E₉₆'s numerical uncertainty** (handoff §1 (ii), "with its spread as a numerical uncertainty"): per functional
and per cell, the SD over k of the base input's 96 fits divided by √96, in σ units and as a relative value on the 16
cells.

**7.3 The control at P = 10.** F's statistic from §4.2, on F₆₄(x), printed beside E₉₆'s for the same seeds.

**7.4 E₉₆ against F at the stability truth.** b on the 16 cells for E₉₆(x) and for F₆₄(x) against the pseudo-experiment's
`xtrue_flat`. A description only: one truth, one experiment, and not an F0b truth.

## 8. Compute

**Unit.** 0.022828 CPU node-h per unfold at 8 lanes per node (`FD-1B-STAGED-DECLARATION.md:530`, measured on S1),
657 s of one lane. FD-STAB measured 522 s per control stability unfold and 466 s per control closure unfold
(`fd/receipts-stab-a1r/gate-projection/project_offline.out.txt`), so the unit is conservative. RS1's dry run measures
a float64 jittered unfold of the same estimator on the same input before ENS1 launches.

**Packing.** Each task is one input (or one truth) and 2 internal seeds, run in one process that calls the bound
runner once per seed: 1,008 stability tasks of 2 unfolds; 816 closure tasks of 2 plus the 1-unfold determinism task.
The dry runs split their tasks into one-unfold tasks. Tasks of 2 balance the lanes exactly: a stage-1 shard holds
167 or 168 tasks, 21 per lane, 42 unfolds; a stage-2 shard 135 or 136, 17 per lane, 34 unfolds. Each `run` call reloads
and re-digests the inputs, which the unit's margin covers. The queue is split round-robin into **6 one-node shards**, each an exclusive node with 8 lanes (`xargs -P 8`), as in
RS1's job script. A failed task exits 255 and its shard starts nothing further.

| stage | run | unfolds | expected node-h | wall per shard | `--time` | charge ceiling |
|---|---|---|---|---|---|---|
| 1 | dry: (s, k) ∈ {0, 1} × {1–4}, and F₆₄(x) (§4.2), 9 one-unfold tasks, one node | 9 | 0.21 | ~0.3 h | `0:45:00` | 0.75 |
| 1 | full: the other 2,008, 6 shards | 2,008 | 45.84 | 7.67 h | `9:00:00` each | 54.00 |
| **1** | | **2,017** | **46.04** | | | **cap 55.0** |
| 2 | dry: nominal at k = 1–4, W1 at k = 1–2, A7 MnvTune at k = 1, one node | 7 | 0.16 | ~0.25 h | `0:45:00` | 0.75 |
| 2 | full: the other 1,626, 6 shards | 1,626 | 37.12 | 6.21 h | `7:30:00` each | 45.00 |
| **2** | | **1,633** | **37.28** | | | **cap 46.0** |

- **The caps bind through Slurm's `--time`** on exclusive single-node jobs: each stage's ceiling (the sum of its jobs'
  limits) is below its cap. The director binds each stage's cap separately (the director's ruling).
- **The projection gate, per stage.** The full run starts only if the dry run's measured per-unfold time t gives a
  per-shard wall, the largest lane load × t plus 300 s of setup, of at most 0.9 × the shard limit: 8.1 h for stage 1
  (t ≤ 687 s at 42 unfolds per lane) and 6.75 h for stage 2 (t ≤ 705 s at 34). Otherwise it returns to the director
  for a reprice.
- **The dry runs' products carry into the full runs**, which skip them (RS1's rule).
- **No resume without the director.** A shard that stops leaves no DONE receipt; the stage is INCOMPLETE.
- **Totals:** expected 83.32 node-h, caps 101.0 node-h, below half the balance (887.2).

**Rules.** CPU only, QOS regular, `--exclusive`, `--no-requeue`. Nothing written to CFS from a job. Products go to
`/pscratch/sd/j/josephrb/ens1-20261107/`. The charge is read from `sacct` after each job ends. Every connect: a fresh
clone at the bound sha; the cov2d `squeue` check recorded; iris read; a `stat` of every input; FD-STAB's references
copied with `dd iflag=noatime`, their atime checked; `--time` in H:MM:SS with scontrol's TimeLimit checked; ssh's rc
read unpiped; the connect script's sha256 sent to the director before launch; each receipt committed as a PR.
**The COV2D fence:** the inputs are the 5D bank, the s5p background dump, the bank sweep and the detector directory,
none of them a COV2D input; the check is still run and recorded.

## 9. Code plan (written for the audit; the code follows the binding)

Bound modules are imported unchanged. If one needs a change, the lane stops and asks the director.

| file | role |
|---|---|
| `nd-unfolding/ensemble_estimator_probe.py` | `stability --k LIST --seed S -- <args>`: for each k, installs the internal jitter and calls `estimator_stability_probe.main(["--candidate", "control", "stability", "--", …, "--pairs=-:S", "--tag", "ens1_k{k:03d}"])`; `closure --k LIST --truth T -- <args>`: the same through the control closure path; `tasks`: the queue, shards and dry lists |
| `nd-unfolding/ensemble_estimator_analyze.py` | gates E1–E4, the stage-1 statistic and G0, ĉ and the readouts; stage 2's floors, `no_worse` and verdict |
| `nd-unfolding/sbatch_ens1.sh` | one node, modes `dry` and `shard <i>`; RS1's refusals (wrong or dirty deploy, an existing log, a full shard without the dry DONE at the same pin, a missing environment) |
| `nd-unfolding/tests/test_ensemble_estimator.py` | the REQUIRED tests of §2.2 and a test in each direction for every gate, reading and refusal |
| `nd-unfolding/tests/ensemble_estimator_mutation.py` | the harness, with the REQUIRED mutants of §2.2 and one per gate, criterion and refusal |

**The rebindings**, each of a name the bound code resolves at call time:
- `s5p_numerics.jittered` (stability): seed 0 returns the float64 copy `jittered(inputs, bkg, None)`; any seed then
  has δ_k added at full precision to MCgen, MCreco, measured and bkg_reco;
- `s5p_nullexp.build` (closures): δ_k is added to `ui` and `ub` before the bound `build` runs, outside its
  `ExpectationRNG` window (`s5p_nullexp.py:243`), after the wrapper's grid-membership check;
- `s5p_numerics.unfold_one` (closures only): float64 in place of the hard-coded float32;
- `s5n_pseudo.write_product`: every product's meta gains an `ens1` block (k, internal seed, protocol seed or truth,
  the four coordinate digests after δ_k, the wrapper's sha256).

**Disclosure of a reused runner input check:** the stability call runs through the bound probe's `check_namespace`
for the control stability path, which requires the declared input and pairs. The closure call runs through the bound
probe's control closure path with FD-STAB's closure arguments.

## 10. Limits and disclosures

- **σ is configuration (e)'s pseudo-data bootstrap σ, not E₉₆'s.** If averaging also lowered E₉₆'s statistical σ,
  the bar in E₉₆'s own units would be harder than stated; averaging over rounding perturbations is not expected to
  change the statistical σ, and ENS1 does not bootstrap E₉₆ to check it.
  <!-- absence-ok: scopes what this declaration's own design computes, not a claim that a result is absent from the repository -->
- **One stability input and one pseudo-experiment,** as in FD-STAB: the GiBUU-like `eavail_shape` truth at
  pseudo-seed 990000. A pass here is not a pass at other truths or on data.
- **Stage 2's floor transfers from the stability input to every closure,** as FD-STAB's does (§5.2 there): an
  assumption, stated.
- **The perturbation scale is the protocol's,** ±½ of the float32 spacing (§2.1). A different scale defines a different estimator.
  It is not chosen with knowledge of RS1's outcome, which is unread.
- **N = 96 fits cost 96× one fit.** That is a property of the estimator a referee will weigh; this study does not
  address it.
- **Stage 2 compares a float64 estimator with a float32 one.** E₉₆'s closures run in float64 coordinates (§2.2); F's,
  FD-STAB's control closures, ran in float32 (`s5p_nullexp.py:342`), as the reported estimator does. So "no worse"
  compares E₉₆ with the reported estimator as it is, dtype included; it does not isolate the effect of averaging. F's
  floor s_F is FD-STAB's, from a float32 base and float64 jitters (audit LOW).
- **The power is modelled** (§6), not measured. A heavier tail or a stronger correlation than the grid's lowers it.

## 11. Open items for the audit and the binding

All three were answered by the audit (§13). None is open.

## 12. What follows

- STAB_PASS then PASS: the outcome record and its CITABLE FOR go to the director, then to Joseph for the replacement
  decision. Any paper text is the paper lane's, through the PRD-referee read.
- Any other verdict: the outcome record states it, and no estimator change follows from ENS1.

## 13. The audit and its dispositions (`coverage-5b-audit`, #887, at `b3690707`)

| item | finding | disposition |
|---|---|---|
| ENS-1 | G0's F was on FD-STAB's float32 base, while E₉₆'s statistic uses a float64 seed-0 base: F's r_j mixed dtype with jitter (RS1's K3), so G0 could read informative where F would pass on E₉₆'s statistic | **Fixed** (§4.2): F₆₄(x), F's float64 seed-0 base, is computed in stage 1's dry run (1 unfold, 0.023 node-h; stage 1 now 2,017 unfolds, 46.04 node-h, cap unchanged) and used by G0, §7.3 and §7.4. A test refuses a float32 base, with a REQUIRED mutant |
| ENS-2 | §2.1 wrote δ = u ⊙ ½·spacing with u ~ U(−½, ½), which is ±¼ spacing, while §10 called it the protocol's ±½ | **Fixed** (§2.1): δ_k = u_k ⊙ spacing₃₂, u_k ~ U(−½, ½), the protocol's ±½ (`s5e_trace.py:362-364`), pinned by a step-range test in both directions and a REQUIRED mutant at ±¼ |
| §11.1 | rebinding `N_PAIRS` is fine (read at call time, `:77-88`); restore it in a `finally`; G0 at the same P = 10 | **Adopted** (§4.1), with a restore-after-raise test |
| §11.2 | one fit is enough for determinism if `xsec_flat` and `xtrue_flat` are compared bitwise, in separate tasks, at the same threads | **Adopted** (§3.2) |
| §11.3 | keep stage 2's dry run: the closure path is new | **Kept** (§8) |
| LOW | E₉₆'s closures are float64 against F's float32 | **Disclosed** (§10) |
