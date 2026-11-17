# PILOT-FB DECLARATION, rev 1: fixed bin edges against the rounding instability, on RS1's pseudo-experiment (2026-11-17)

**For** the re-read by the two independent auditors (Codex and Grok) and the director's go. **Nothing has run, and
nothing runs before the go.** DESIGN ONLY: the code (§8) is written after this is audited.

**Written by** session tier3-design, at the director's brief of 2026-11-17. Rev 0 (`260123d1`) was read by both
auditors, and both read FAIL as written, with fixable design blockers. Rev 1 answers every finding. §11 gives each
finding's disposition. All repository citations are at `13f742e3` (origin/main `be193461` merged) unless stated.
LightGBM citations are at tag v4.6.0:
- `src/io/bin.cpp`, sha256 `3386767e…`;
- `include/LightGBM/bin.h`, `3cb03538…`;
- `src/io/dataset.cpp`, `809a8d9e…`;
- `src/io/dataset_loader.cpp`, `783d5118…`;
- `python-package/lightgbm/basic.py`, `b8ccce47…`.

**Authority.**
- `DECISION-20261117b-joseph-note-plan.md` (#1212), item 3: "**PILOT-FB is approved**, from (b): the pilot and the
  fixed bin edges", with Joseph's words "yes I meant the pilot and the bin edge fixing". It runs after its audit and
  the director's go, within its declared cap of 0.9 CPU node-h. No outcome changes any note or paper wording.
- Compute: `DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md` item 2. Each campaign is declared,
  priced and bound.

**CITABLE FOR:** the design, readings, price and code plan of the pilot, as declared.

**NOT CITABLE FOR:**
- any result. Only PILOT-FB's outcome record can state one;
- any statement about the real data;
- any change to the reported estimator, to `OUTCOME-20261105-fd-stab-none-pass.md`, to RS1's or ENS1's records, or to
  any note or paper wording. **No outcome changes any wording.** The outcome goes to Joseph and Ben, through the
  director, as an option.

## 1. The question

RS1 found (`OUTCOME-20261108-rs1-rounding-mechanism.md`, K1 SUPPORTED) that on this pseudo-experiment, "the
perturbation reaches the estimator by breaking ties among equal float32 values, which changes LightGBM's histogram
bins; a perturbation that keeps the ties removes the spread". V, its tie-preserving jitter, left a spread ratio of
about 10⁻⁶. V changes the perturbation, not the estimator.

**The remedy tested here changes the estimator:** every LightGBM model gets fixed bin edges, computed once from the
unperturbed inputs, placed so that no perturbation of the protocol's size can move a row across one.

**Two questions:**
1. Does the rounding spread fall, against the same jitters that give configuration (e) its spread? "Removed" means
   S1's band R: at most 10 % of (e)'s spread (§5).
2. How much does the result depend on which of three tested binning policies is used? This is a sample, not a bound
   (§9).

**What it cannot answer:**
- whether the remedy keeps (e)'s bias at the F0b truths, or its coverage. Each is a later step, declared separately;
- anything about the real data.

## 2. What the code implies (readings of source; each is tested in §5 or §8)

1. **The four model roles, and the rows each sees.** The loop first selects the truth-passing rows: `MCreco`,
   `MCgen` and `pass_reco` become their `[pass_truth]` subsets (`omnifold_nn_core.py:210-211`). Then:

   | role | fit matrix | rows it scores |
   |---|---|---|
   | **clf1** | `MCreco[pass_reco]` ∪ `measured[meas_pass_reco]` (`:251`) | `MCreco[pass_reco]` (`:257`) |
   | **reg** | `MCgen[pass_reco]` (`:259`) | `MCgen[~pass_reco]` (`:260`) |
   | **clf2** | `MCgen` ∪ `MCgen` (`:263`) | `MCgen` (`:266`) |
   | **ref** | `obs[ok_o]` ∪ `tmpl[ok_t]` (`s5n_pseudo.py:226`) | the same rows (`unfold_2d_omnifold_unbinned.py:447`) |

   The features are the five axes, in one column order, in every role.
2. **A role's bins depend only on its fit matrix and its Dataset parameters.** LightGBM builds a feature's bins from
   the matrix's distinct values and their counts (`bin.cpp:338-391`). Labels and weights do not enter. With
   `bin_construct_sample_cnt` above every row count (`s5c_unfold.py:57`), there is no sampling, so the mapper is a
   deterministic function of the matrix and the parameters. Each role's fit matrix is the same in every iteration of
   one unfold, since only labels and weights change. So **within one unfold, a role's mapper is the same at every
   iteration.**
3. **Forced bins do not fix the bins by themselves** (`FindBinWithPredefinedBin`, `bin.cpp:157-235`):
   - it first places `−kZeroThreshold` if any value is ≤ −`kZeroThreshold`, and `+kZeroThreshold` if any value is
     > `kZeroThreshold` (`:183-197`; `kZeroThreshold` = 1e-35). It then appends +∞. Call the number of zero bounds
     placed z;
   - it inserts the forced bounds in file order, skips any with |b| ≤ 1e-35, and stops after `max_bin` − z − 1 of them;
     the rest are silently dropped (`:199-211`);
   - it **fills every remaining bin greedily from the data** (`:213-232`). Those greedy bounds lie between distinct
     data values.
4. **How a value is binned:** the first bin whose upper bound is ≥ the value (`bin.h:631`, `value <= bin_upper_bound_[m]`).
5. **The forced-bins file** (`dataset_loader.cpp:1493-1527`):
   - it is keyed by integer feature index, `"feature"`, with `"bin_upper_bound"`;
   - a file that cannot be opened is **ignored with only a warning**;
   - only adjacent duplicates are removed.
6. **The protocol's jitter** (`s5e_trace.py:358-368`) returns `x32.astype(float64) + u · spacing(|x32|)`. Here spacing
   is evaluated on the float32 absolute value and cast to float64, and u is uniform in [−½, ½). Values on an
   analysis-grid edge are not moved.
7. **Sentinels.** The pseudo-experiment path does not drop the −9999 truth sentinels: `drop_sentinel_rows`
   (`s5e_trace.py:371-376`) is refused for the pseudo construction (`:499`). So −9999 values can sit inside
   `MCgen[pass_truth]`, and therefore inside reg's and clf2's matrices. The remedy changes no input, so here they are
   values like any other. §3's rules apply to them unchanged.
8. **The jitter path has not changed since RS1's bound code:**
   `git diff --stat e306087e 13f742e3 -- nd-unfolding/{s5e_trace,s5p_numerics,s5n_pseudo,s5c_unfold,omnifold_nn_core,estimator_stability_probe,rounding_mechanism_probe,rounding_mechanism_analyze}.py 2d-unfolding/unfold_2d_omnifold_unbinned.py`
   is empty. So a seed draws the same jitter here as in RS1's A0. J (§5.1) checks this on every jittered array.

## 3. The remedy: edges per role and feature

**Inputs to the edges.** These are the unjittered float32 base's matrices (§2 item 1), built in the job's prep step
through the bound path. For each role r and feature f:
- F is the fit column;
- U is the fit column together with the scored column.

**The policy, frozen. G0 refuses unless every part holds for every role and feature:**
1. **Finite:** every value of U is finite. So no missing-value bin arises, with LightGBM's `use_missing` and
   `zero_as_missing` at their defaults.
2. **The zero band:** no value v of U has 5×10⁻³⁶ < |v| < 2×10⁻³⁵. A jitter of at most ½ spacing then cannot carry a
   value across ±`kZeroThreshold`, so z is the same for the base and every jitter.
3. **The edge count:** z_{r,f} = [any F ≤ −1e-35] + [any F > 1e-35], from the fit column, as LightGBM computes it. Then
   n_{r,f} = `max_bin` − z_{r,f} − 1.
4. **Each value's envelope:** for each distinct value u of U, s(u) = float64(numpy.spacing(float32(|u|))), and the
   envelope is [u − ½ s(u), u + ½ s(u)].
   - The envelope is closed, so it is conservative for the half-open u.
   - The grid-edge exemption is not used, which is also conservative.
   - For a negative u, |u| is used, as the jitter does.
5. **Admissible gaps:** between consecutive distinct values u_k < u_{k+1} of U, the gap is admissible iff
   u_k + ½ s(u_k) < u_{k+1} − ½ s(u_{k+1}).
   - Its edge e_k is the float64 midpoint of those two numbers.
   - The edge must lie strictly between them, have |e_k| > 2×10⁻³⁵, and survive its JSON text exactly
     (`float(repr(e)) == e`).
   - There is no other rule. A power of two is handled by s(u): its gap below is empty when the values are adjacent.
6. **Placement:**
   - The fit column's N rows are sorted. B_k is the number of rows of F ≤ u_k.
   - Edge i = 1…n aims at the row count t_i = q_i · N:
     - E1 and E3: q_i = i/(n+1);
     - E2: q_i = (i + ½)/(n+1).
   - In ascending i, take the admissible gap k that minimizes |B_k − t_i|, with ties going to the lower k.
   - If that k is not above the previous edge's gap, take the next admissible gap above the previous one.
   - If none is left, G0 refuses: **INFEASIBLE**. There is no backtracking, no padding, no smaller count and no
     fallback to LightGBM's own bins.
7. **Files:** one native LightGBM forced-bins JSON per (set, role): `[{"feature": f, "bin_upper_bound": [e…]}]`, f = 0…4
   in the role's column order. That is 3 sets × 4 roles = 12 files. They are written by the prep step before any fit,
   and their sha256 are recorded in `edges/INDEX.json`.

| set | `max_bin` | placement |
|---|---|---|
| **E1** (primary) | 255 | q_i = i/(n+1) |
| **E2** | 255 | q_i = (i + ½)/(n+1): the same resolution, edges offset by half a step |
| **E3** | 127 | q_i = i/(n+1): **half the resolution**. E3 changes model capacity as well as edges (§5, S3-res) |

**Why per role:** z and the mapper belong to each fit matrix, not to a pool (audits B2 and 1). U includes the scored
rows, so a scored row cannot cross an edge either.

**Why forced bins, and not a pre-quantization:** a pre-quantization leaves rows near a grid midpoint that still flip
(rev 0 §3). The director kept forced bins, with E3 at `max_bin` 127.

## 4. The arms and their inputs

**The input is RS1's pseudo-experiment, unchanged** (RS1 §4):
- FD-STAB's GiBUU-like stability truth, pseudo-seed 990000;
- configuration (e), estimator R, with 5 iterations and 32 threads per lane;
- inputs `of_inputs_5d.npz` (`07fccc1a…`) and `bkg_dump.npz` (`2addac8f…`), through the production loaders;
- the protocol's jitter seeds 1–20.

| arm | what runs | unfolds |
|---|---|---:|
| **A0** (baseline, reused) | RS1's A0, float32 base and jitters 1–20, pinned in RS1's `receipts/full-a1/read/runs-SHA256SUMS` (`runs/A0/rs1_A0_b-_j-.npz` `fd9f4b35…`, `…_j1.npz` `80c2a710…`, …). They are read by O_NOATIME copy | 0 |
| **A0R** (G1; the unforced control) | RS1's A0 float32 base, rerun unchanged. **It is exempt from J, G2 and G3**: it has no forced bins | 1 |
| **E1** | float32 base; jitters 1–20 | 21 |
| **E2**, **E3** | float32 base each | 2 |
| **total** | | **24** |

- **A fresh root:** the job refuses if `/pscratch/sd/j/josephrb/pfb-20261117/` exists. Every expected product (arm,
  seed) must be written by this job. The bound runner skips an existing target on existence alone
  (`s5p_numerics.py:179-181`), so a stale product cannot enter.
- **E2 and E3 are run at their bases only.** Their removal of the spread is not measured.
<!-- absence-ok: scope of this design; it states which arms the pilot runs, not that a result does not exist -->

## 5. The statistics and the readings

**Functionals:** the 153 s5e reported functionals (`s5c_coverage.reported_functionals`).
**σ_j:** FD-STAB's committed pseudo-data σ, `state/s5e/cand/assess_receipt.json` `sigma_rel_pct` (sha256 `84266e30…`),
divided by 100, so that it is a fraction (`FD-STAB-DECLARATION.md:146-156`).

**S1, the removal ratio:** RS1's `rounding_mechanism_analyze.spread_ratio`, imported unchanged (bound at `e306087e`,
unchanged since, §2 item 8). This fixes the details:
- s_{a,j} is the SD, with ddof = 1, of F/mean − 1 over seeds 1–20;
- M is the median over functionals with s_{A0,j} > 0;
- the interval is 2,000 paired resamples, with each resample's zero-spread functionals dropped, and the 5th to 95th
  `nanpercentile`;
- the reading is R ≤ 0.10 < P < 0.70 ≤ C, DEFINITE only when the interval lies inside one band, else INCONCLUSIVE.
  It is INVALID if more than 10 % of functionals are excluded.

The pilot passes `numpy.random.default_rng(20261117)`. Power is RS1's: at 20 paired seeds a true M = 0 reads R DEFINITE
in every trial (`RS1-DECLARATION.md:230-238`).

**S2, the stability statistic, like for like with RS1's A0 readout** (`FD-STAB-DECLARATION.md:158-165`):
- r_j = F_j / F_{E1 base,j} − 1;
- on each of the 10 disjoint pairs (1, 2) … (19, 20), per functional, the larger |r_j|/σ_j of the two;
- the median and maximum over the 153, then the mean over the pairs, with the standard error reported, not gated.

RS1's A0 read 0.760 and 6.78 (`rs1_read.json` `readouts.A0_pair_statistic_10_pairs`). S2 PASSES iff the mean median
is ≤ 0.3 and the mean maximum is ≤ 1.0 (s5e's A3 bars, `FD-STAB-DECLARATION.md:33-34`). Equality passes.

**S3, the dependence on the tested binning policies:** over the three float32 bases, for a pair (a, b),
d_{ab,j} = |F_{a,j}/F_{b,j} − 1|/σ_j.
- **S3-place:** the pair (E1, E2). Same resolution, different placement.
- **S3-res:** the pairs (E1, E3) and (E2, E3). Resolution and placement both change.
- **S3:** per functional, the maximum over all three pairs; then the median and maximum over the 153.

**POLICY-STABLE** iff S3's median is ≤ 0.3 and its maximum is ≤ 1.0, else POLICY-SENSITIVE. The bars were set for
jitter pairs, and S3 is not like for like with S2. So the label means only "within those numbers across the three
tested policies". S3-place and S3-res are always reported beside it.

**INVALID** (deterministic, before any reading):
- a non-finite functional in any product;
- a zero mean in S1;
- a zero denominator in S2 or S3 (F_{E1 base,j} or F_{b,j} = 0);
- a σ_j that is non-finite or ≤ 0;
- S1's own INVALID (more than 10 % excluded).

### 5.1 Gates, each with one time and one named outcome

| gate | when | what must hold | outcome if it fails |
|---|---|---|---|
| **G4**, the inputs | in the connect, before the submit; re-verified by the analysis (one gate, two checks) | every reused A0 product, the σ receipt, both inputs and the deploy's pinned files equal their pins | INPUTS CHANGED: nothing is submitted, or nothing is read |
| **G0**, the policy and edges | in the job's prep step, **before any fit** | §3 rules 1–6 for every role and feature, and the 12 files written and hashed | INFEASIBLE: the job exits before round 1, with each role and feature's admissible-gap count and the first rule that failed. This is a result about this input, not a reading of the remedy |
| **G1**, reproduction | after round 1 | A0R's `xsec_flat` equals RS1's pinned `rs1_A0_b-_j-.npz` bitwise, compared as arrays, at 32 threads and 8 lanes | NOT REPRODUCED |
| **J**, the jitter was applied | every E1 jitter unfold; round 1 gates rounds 2–3 | the coordinate arrays each role received equal `s5e_trace.jitter_coords(base32, seed, edges)` bitwise, and differ from the base in at least one entry per role and feature. Every base unfold's arrays equal the float32 upcast | JITTER NOT APPLIED |
| **G2**, the bins hold | every remedy unfold (E1's base and 20 jitters, E2's and E3's bases), every role and feature | each fit and scored row's intended bin index, under §2 item 4's rule on the role's full intended bound list (zero bounds, the edges, +∞), equals the E-set base's index | PREMISE FAILED |
| **G3**, the mapper is the intended one | every remedy unfold and role, at iteration 1 (§2 item 2 makes later iterations identical) | see below | PREMISE FAILED |
| **identity** | every remedy fit | each estimator's recorded parameters name the arm, role, `max_bin` and edge-file sha256 that role should have, for all four roles, the refinement included. `s5c_unfold.unfold`'s own check (`:129-134`) covers only `config_params`' keys and is not this witness | PREMISE FAILED |

**G3, in full.**
- **How the mapper is read.** The wrapper captures each role's fit matrix and the estimator's own Dataset parameters
  at the fit. It builds a LightGBM Dataset from exactly those, constructs it, and dumps it with
  `Dataset._dump_text` (`basic.py:3546-3562`, `LGBM_DatasetDumpText`). `Dataset::DumpTextFile`
  (`dataset.cpp:1188-1238`) prints each feature's forced bounds and every row's bin index per feature.
- **G3 requires all four of these:**
  - (a) the dump lists forced bounds for all five features, matching the file at the dump's printed precision. That
    catches an unopened file (§2 item 5);
  - (b) all five features are used;
  - (c) `feature_num_bin(f)` = n_{r,f} + z_{r,f} + 1;
  - (d) every row's dumped bin index equals its intended index.
- **Why (c) and (d) suffice.** A greedy bound lies between distinct data values (§2 item 3), so an added bound splits
  a populated bin and changes some row's index, which (d) sees. A dropped forced bound changes the count, which (c)
  sees.
- **Why a rebuilt Dataset reads the fit's mapper.** It is a deterministic function of the same matrix and parameters,
  with no sampling (§2 item 2).
- **Scored rows.** At prediction, LightGBM compares raw values with split thresholds that are these bin upper
  bounds. So the scored rows' invariance is G2's, and G3 ties G2's bounds to LightGBM's.

**Timing.** G1, J, G2 and G3 on round 1 decide whether rounds 2–3 run. J, G2 and G3 are recorded for every later unfold
too, and the analysis refuses to read if any of them failed anywhere. On any gate failure, S1–S3 are still computed
where the products allow, and printed labelled NOT READ, so the size of a failure is kept.

### 5.2 The outcome: exactly one, by precedence

First the gates and the time limit, in this order: INPUTS CHANGED, INFEASIBLE, INCOMPLETE (stopped or time-limited),
NOT REPRODUCED, JITTER NOT APPLIED, PREMISE FAILED, INVALID. The first that applies is the outcome. Otherwise the three
readings are formed: S1 ∈ {REMOVED (R), REDUCED (P), NOT REMOVED (C), INCONCLUSIVE}, S2 ∈ {STAB_PASS, STAB_FAIL} and
S3 ∈ {POLICY-STABLE, POLICY-SENSITIVE}. The first matching row is the outcome. The rows partition all 16 combinations:

| # | condition | outcome | the record may say |
|---|---|---|---|
| 1 | S1 NOT REMOVED | **NOT A REMEDY** | "Fixed edges, as declared, do not remove the rounding spread on this pseudo-experiment." |
| 2 | S2 STAB_FAIL | **NOT AN OPTION AS DECLARED** | "Under fixed edges, the result still moves beyond the stability bars under the protocol's jitters (S2 = …)." S1's reading is stated beside it |
| 3 | S1 INCONCLUSIVE | **NO OPTION STATEMENT** | the numbers only |
| 4 | REMOVED, POLICY-STABLE | **OPTION A** | "On this pseudo-experiment, fixing every LightGBM model's bin edges once, from the unperturbed inputs, reduces the rounding spread to at most 10 % of (e)'s (S1 band R). Across the three tested binning policies the result moves by at most S3's maximum in pseudo-data σ (placement alone: S3-place)." |
| 5 | REMOVED, POLICY-SENSITIVE | **OPTION B** | row 4's first sentence, then: "The result depends on the tested binning policy by S3's median and maximum in pseudo-data σ, beyond those numbers (placement alone: S3-place; resolution: S3-res)." |
| 6 | REDUCED, POLICY-STABLE | **OPTION C** | as row 4, with "reduces the rounding spread to between 10 % and 70 % of (e)'s (S1 band P)" |
| 7 | REDUCED, POLICY-SENSITIVE | **OPTION D** | as row 5, with row 6's first sentence |

- **Every option statement** carries §9's limits and the next steps it would need: bias at the F0b truths, coverage,
  and a data run, each declared separately.
- **It may not say** that the remedy works on the data, keeps (e)'s bias, should replace (e), or is "edge-stable" in
  general.
- **Every outcome**, the gate outcomes included, reports all statistics that could be computed.

### 5.3 Predictions, stated before anything runs

These are this lane's expectations, not criteria:
- G0 feasible, though nobody has counted the admissible gaps yet;
- REMOVED, with M_E1 near 0, and most or all of E1's jitters bitwise equal to E1's base in `xsec_flat`. If G3 holds,
  the regressor's scored rows cannot cross either, which closes the channel that left V's 10⁻⁶ residual;
- STAB_PASS;
- S3: no expectation.

## 6. Readouts, with no criterion

- **The remedy's shift from (e):** each E-set base against A0's float32 base, as the median and maximum over the 153
  of |F_E / F_A0 − 1|/σ. On one pseudo-experiment this is a shift, not a bias (§1).
- **E1's jitters bitwise equal to its base:** how many of the 20.
- **The 16 cells:** M_E1 and S3 on R00–R15, by S1's integration rule (RS1 §5).
- **Per role and feature:** z, n, the admissible-gap count, and the realized E1–E2 edge differences (quantile
  collisions can make them coincide).
- **The time per unfold** of each arm, and the gate overhead.

## 7. Compute

**Unit:** FD-STAB's, 657 s per unfold on one of 8 lanes, which is 0.022828 CPU node-h (`RS1-DECLARATION.md:356-358`).
The allowance is +15 % for the gates. G3's dataset dump is unmeasured, which is why rev 0's 10 % is raised.
<!-- absence-ok: a cost projection for a gate not yet built, not a claim that a result does not exist -->

| | unfolds | rounds of 8 lanes | wall at unit +15 % | node-h |
|---|---:|---:|---:|---:|
| round 1: A0R; E1, E2, E3 bases; E1 jitters 1–4 | 8 | 1 | 756 s | 0.210 |
| rounds 2–3: E1 jitters 5–20 | 16 | 2 | 1,511 s | 0.420 |
| **expected** | **24** | **3** | **2,267 s** | **0.630** |

**Cap: 0.9 CPU node-h.**
- One exclusive node, `--time=0:50:00` (H:MM:SS; 3,000 s = 0.833 node-h), `--no-requeue`, QOS regular, CPU only. The
  charge cannot exceed `--time`.
- **After round 1** the job continues only if 3 × the round-1 wall is ≤ 2,900 s. Otherwise it stops INCOMPLETE,
  having spent about 0.2–0.3 node-h, rather than running into the limit. A round-1 gate failure is expected to cost
  about one round. That is an expectation, not a ceiling: a stalled round-1 fit can use the whole allocation.
- No dry run. The charge is read from `sacct` after the job ends. No resume without the director.
- **Reads and fences:**
  - The job reads `of_inputs_5d.npz` and `bkg_dump.npz` plainly through the production loaders, as RS1 did. They are on
    other lanes' atime lists (E96D, `fd/referee-sensitivity-20261111/connect-post/README.md:21`). The director confirms
    with cov2d, at the fence notice, that no live watch names them.
  - RS1's A0 products and the σ receipt are read by O_NOATIME copy.
  - The job family is `pfb_`. cov2d and every fenced lane are told and ack before any connect. The connect's fence
    refuses if any `cov2d`, `t2a`, `ll5d`, `e96data`, `rpd_`, `rsn_`, `rdx_`, `ibukt-` or `pfb_` job is queued or
    running.
  - Status is read with `sacct`, never `squeue` alone. Every connect script's sha256 goes to the director before it
    runs. Receipts are committed as PRs.

## 8. Code plan (written after this declaration is audited)

**No bound module is edited.**
- **The wrapper:** one new module, `nd-unfolding/fb_pilot_probe.py`, runs every arm through RS1's
  `rounding_mechanism_probe.py run --arm A0` path. For an FB arm it rebinds:
  - `omnifold_nn_core.make_estimators`, so clf1, reg and clf2 each get their own role's file and `max_bin`;
  - `s5n_pseudo.refine_params`, so the refinement gets its file.

  It records each role's parameters (the identity gate), captures each role's fit matrix, scored rows and received
  coordinates (for J, G2 and G3), and runs G3's dump at iteration 1 into `/dev/shm`, deleting the dump after the check.
- **The prep step** builds the unjittered base matrices, applies §3, and writes `edges/`.
- **The job script** is `sbatch_pfb.sh`, on RS1's pattern: deploy pin, fresh root, log refusal, environment check,
  `SHA256SUMS`, DONE receipt, G0 before round 1, the round-1 gate and the wall projection.
- **The analysis** is `fb_pilot_analyze.py`: §5's statistics, the gates and §5.2's precedence.

**Tests, local, with LightGBM 4.6.0**, each in the direction it acts and in the other:
- **Admissibility:**
  - the jitter at u = −½ and at u → ½, on positive and negative values, at a positive and a negative power of two
    and its float32 neighbors, at signed zeros, and at the float32 value nearest `kZeroThreshold` and its neighbors;
  - signed spacing in place of |x| is caught (Grok's −8 pair; Codex's −1.5 pair);
  - an edge that does not survive its JSON text is refused.
- **Placement:** one pool gives one edge set. Ties, collisions, the next-gap walk, and INFEASIBLE when gaps run out.
- **z per role:** a pool with negatives and a fit column without them gives different z, and the per-role rule uses
  the fit column's.
- **G3:**
  - one fewer edge makes LightGBM fill a bin greedily, and (d) catches it;
  - one extra edge is dropped, and (c) or (d) catches it;
  - an unopenable file is caught by (a);
  - a correct file passes;
  - an unforced fit (A0R-like) fails G3 but is exempt by arm.
- **The remedy on a toy:** with forced edges, fits are bitwise identical on fit and scored rows under the jitter.
  Without them they differ.
- **J:** an unapplied jitter, or the wrong seed, is caught.
- **The outcome:** every one of the 16 combinations, each gate outcome, every INVALID branch and every boundary
  equality reaches exactly one row.
- **A mutation harness:** one planted defect per guard, per rule and per row, each killed by a named test.

## 9. Limits and disclosures

- **One pseudo-experiment and 20 jitters.** The intervals cover the jitters, not the realization.
- **The remedy's removal is measured for E1 only.** E2 and E3 are bases.
- **Three tested policies are a sample, not a bound,** on the dependence on binning. E3 also changes resolution and
  capacity, so S3-res is not a placement effect.
- **Admissibility is against this protocol's jitter only.** A real rounding difference larger than ½ spacing, such as
  driver against npz (`KNOWN_ISSUES.md` 79), could cross an edge.
- **On data, the edges would come from the data's own unperturbed inputs.** Their stability across data versions is
  untested here.
- **The remedy changes the estimator.** Bias, coverage and the data result are untested here (§1).
<!-- absence-ok: limits of this design's scope; they name what the pilot does not measure, not missing results elsewhere -->

## 10. Open items for the re-read and the director

1. **The live atime watches** on the two inputs: the director asks cov2d at the fence notice (§7).
2. **G3's dataset dump:** its cost is unmeasured. The +15 % allowance and the round-1 wall projection bound the risk.
<!-- absence-ok: a cost projection for a gate not yet built, not a claim that a result does not exist -->

## 11. Rev 1: the audits' findings and their dispositions

The reports are `~/codex-reports/pilot-fb-audit/codex/audit-codex.md` and `~/codex-reports/pilot-fb-audit/grok/audit-grok.md`,
both of rev 0 at `260123d1`. Both read FAIL as written, with fixable blockers.

| finding | disposition |
|---|---|
| Codex 1, Grok B2: G3 checks a count; z comes from a pool, not each fit; A0R would fail G3 | **Fixed.** Edges, z and n are per role and feature from the fit column (§3). G3 now reads the training mapper through the dataset dump: forced bounds present, count, and every row's bin index against the intended one, for all four roles at iteration 1, with §2 item 2's justification for later iterations. A0R is exempt by arm (§4, §5.1) |
| Codex 2, Grok B1: signed spacing; zero boundaries; the policy for sentinels, zeros and negatives | **Fixed.** The half-width is ½ spacing(\|u\|) in float32, cast to float64, exactly as the jitter computes it (§3 rule 4). The zero band (rule 2), finiteness (rule 1), the sentinels (§2 item 7: kept, values like any other) and the JSON round-trip are all frozen. Tests cover both counterexamples |
| Codex 3, Grok B3: the outcome table is not a partition | **Fixed.** Gate outcomes come first, then seven rows by precedence that partition the 16 combinations (§5.2). An INVALID path is added (§5). Each sentence says which band occurred |
| Codex 4, Grok B4, M1, M4: gate timing, G4's place, a jitter not applied, stops that lose the effect size, G0 with no outcome | **Fixed.** Each gate has one time and one named outcome (§5.1). J is added. G2, J and G3 cover every remedy unfold. Statistics are printed NOT READ on a failure. INFEASIBLE is G0's outcome |
| Codex 4: identity contract, stale products, the parameter check's reach | **Fixed.** The identity gate covers all four roles. The jitter path is shown unchanged since RS1's bound code (§2 item 8), and J re-derives every jitter. There is a fresh root, and every product is validated (§4) |
| Codex 5, Grok H1: E3 mixes resolution with placement; "edge-stable" overclaims | **Fixed.** S3-place and S3-res are reported separately. The label is POLICY-STABLE, meaning "within those numbers across the three tested policies", and the sentences say so (§5, §5.2, §9) |
| Grok H2: the edge sets are not a function of the pools | **Fixed.** The count fractions, the distance, the ties, the walk and the refusal are frozen (§3 rule 6) |
| Grok H3: G2 sees only four seeds and a local index | **Fixed.** G2 covers every remedy unfold, with the full intended bound list. G3 ties it to LightGBM's mapper |
| Grok M2: the power-of-two refusal contradicts the interval rule | **Fixed.** The extra rule is dropped. s(u) handles powers of two (§3 rule 5) |
| Grok M3: `s5c_unfold`'s check does not see the refinement or forced bins | **Fixed.** That check is no longer cited as the witness. The identity gate is (§5.1) |
| Codex 6: round 1 is not a hard third | **Fixed.** It is stated as an expectation, and a round-1 wall projection stops a run that would not fit (§7) |
| Grok L1: zeros and the threshold | **Covered** by §3 rule 2 and the tests |
| Grok L2: too few distinct values | **Covered:** INFEASIBLE, a named outcome. The prediction says the gaps are uncounted (§5.3) |
| Grok L3, rev 0 §10 item 1: authority | **Fixed:** `DECISION-20261117b-joseph-note-plan.md` item 3 (#1212) |
| Grok L4: division by zero | **Fixed:** INVALID (§5) |
| Grok B2 aside: LightGBM matches feature names | **Not so in v4.6.0:** the file is keyed by integer index (`dataset_loader.cpp:1508`). The unopenable-file case it points to is real, and G3 (a) catches it |
