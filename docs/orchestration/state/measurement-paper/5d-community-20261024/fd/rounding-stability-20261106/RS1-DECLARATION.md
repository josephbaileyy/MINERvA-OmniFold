# RS1 DECLARATION: the mechanism of the rounding instability, on simulated pseudo-data (2026-11-06)

**For** audit by `coverage-5b-audit` and binding by the director. **Nothing has run, and nothing runs before the
binding.**

**Written by** the rounding-instability lane, a Claude session named `director-helper-3`, under the director's
handoff `HANDOFF-20261106-lane-rounding-instability.md`, which lives outside the repository. All repository
citations are at `origin/main` `d95ed680` unless stated.

**Authority.**
- `DECISION-20261106-joseph-diagnoses-jinst-corrections.md:40-41`, item 1.3: "The rounding-instability fix. First the
  spread is measured on the sixteen reported cells. Then an ensemble-averaged estimator is declared as a variant. It
  is declared, audited and bound before it runs."
- `DECISION-20261106-joseph-plateau-next-work.md:45-46`, "What is decided" item 1: "The mechanism is found first,
  then an estimator that averages over rounding perturbations is declared as a variant." It reached main in #865,
  merge `6d0aca7f`, after this declaration's base `d95ed680`, and is cited at that merge.
- Compute: `DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md` item 2 (#640). Each campaign is
  declared, priced and bound, and one priced above half the group balance returns to Joseph first. This one is priced
  at 4.5 CPU node-h (§7).

**This is step 1 of two.** Step 2, the ensemble-averaged estimator, is a separate declaration (§11).

**CITABLE FOR:**
- the design, readings, price and code plan of the step-1 study, as declared;
- once its outcome record exists: R0's two ratios on the 16 reported cells (§6), **as a description only**. Neither
  is read as a pass or a fail.

**NOT CITABLE FOR:**
- any result or mechanism. Only RS1's outcome record can name one;
- any statement about the real data;
- any change to the reported estimator, or to `OUTCOME-20261105-fd-stab-none-pass.md`. NONE_PASS stays terminal for
  the variants it tested (B2, B3a, B3b). This study tests no candidate estimator.

## 1. The question

**The instability.**
- Configuration (e) is the five-observable joint-test estimator (`registry/ESTIMATORS.tsv:8`, `e-R-joint-test`).
- Its result is bitwise independent of its training seed, and its row order moves it by at most 1.4e-10 σ
  (`OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md:81`).
- An edge-safe perturbation of every input coordinate within ±½ float32 ulp moves its real-data functionals by
  0.78 data-σ in the median and 2.58 at most, against bounds of 0.3 and 1.0 (same line; `KNOWN_ISSUES.md` 80).
- On the GiBUU-like stability pseudo-experiment, FD-STAB's control read a mean median of 0.759 and a mean maximum of
  6.83 pseudo-data σ (`OUTCOME-20261105-fd-stab-none-pass.md:25`).

**The question RS1 answers:** through which channel does a rounding-scale perturbation of the input coordinates reach
configuration (e)'s result? RS1 tests each candidate the referees name (`HANDOFF` §1 (i)) with a test declared to
separate it from the others (§3).

**What RS1 cannot answer:**
- whether the same channel carries the spread on the real data. RS1 runs on one simulated pseudo-experiment;
- how large the spread is on data. That is R0 (§6), arithmetic on records already on main;
- whether any remedy works. That is step 2.

## 2. What the code already implies, and what it does not

These facts set up the tests. Each is a reading of source, not a measurement, and §3 tests each one.

1. **The perturbation is coordinates only.** `s5p_numerics.jittered` (`nd-unfolding/s5p_numerics.py:79-87`) jitters
   MC truth, MC reco, observed and template coordinates through `s5e_trace.jitter_coords`
   (`nd-unfolding/s5e_trace.py:351-368`). No weight is touched.
2. **A jittered product runs in float64, and the base in float32** (`s5p_numerics.py:183-187`). So FD-STAB's
   base-to-jitter comparison mixes the jitter with a change of dtype. s5e measured the float64 upcast of the same
   values "bitwise inert" (`DIAGNOSIS-20260926-s5e-oi192-estimator.md:66`), but on B0's estimator and not on this
   input. RS1 re-measures it on configuration (e) (test K3).
3. **Four LightGBM models see the coordinates:** the Stay-Positive refinement classifier
   (`2d-unfolding/unfold_2d_omnifold_unbinned.py`, `refine_stay_positive`), and OmniFold's step-1 classifier, step-2
   classifier and regressor (`nd-unfolding/omnifold_nn_core.py:223`, `:257-266`). All four run in histogram mode, with
   `bin_construct_sample_cnt` above every row count and `deterministic`, `force_row_wise` and a fixed thread count
   (`nd-unfolding/s5c_unfold.py:54-60`; the refinement through `s5n_pseudo.refine_params`,
   `nd-unfolding/s5n_pseudo.py:234-236`).
4. **In histogram mode, a coordinate reaches a fit only through binning.** Each feature's bins are built from its
   sorted distinct values and their counts (LightGBM v4.6.0, the version the FD-STAB dry run's environment printed,
   `src/io/bin.cpp:338-391`, then `FindBinWithZeroAsOneBin` and `GreedyFindBin` at `:242-298` and `:78-150`). Two values count as distinct when they differ by more
   than one double ulp (`include/LightGBM/utils/common.h:845-848`, `CheckDoubleEqualOrdered`). The fit then uses
   only each row's bin, label and weight.
   - Sources: `https://raw.githubusercontent.com/microsoft/LightGBM/v4.6.0/`; sha256 of `bin.cpp`
     `3386767e6bbc29c5…`, of `common.h` `bbf86e6c96aba08b…`.
5. **So a sub-float32 jitter applied to each row on its own breaks every tie.** The coordinates are float32 values
   upcast to float64 (`s5e_trace.py:358-359`). Rows that share a float32 value form one distinct value with a count.
   After the jitter, each row is its own distinct value with count 1, so the greedy bin boundaries can fall inside a
   former tie. **This is a hypothesis about the trigger, not a finding.**
6. **A jitter that moves every row sharing a value by the same amount, and keeps the order, preserves the bin
   partition.** It keeps every distinct value's count and their order, so `GreedyFindBin` groups the same values into
   the same bins. The boundaries move, but only between adjacent distinct values, so every training row stays in its
   bin. With deterministic training, each fit then has identical binned inputs, labels and weights. The trees should
   be identical apart from their numeric thresholds, and every prediction on a training row identical.
   - **One exception, from the code:** the regressor predicts rows it did not train on, the reco-failing MC rows
     (`omnifold_nn_core.py:259-260`). Such a row can sit exactly on a training midpoint and cross it. RS1 measures
     whether that channel matters (§3, K1) rather than assuming it away.
7. **Row order is inert** (`OUTCOME-20260926-…:81`, on data, estimator R). Reordering changes the order of histogram
   accumulation, a perturbation of relative size about 1e-16 in the gains. Its smallness argues against "near-degenerate
   gains flipped by arithmetic noise", but it was measured on data, not on this input. RS1 re-measures it (K4).

## 3. The candidates and the tests that separate them

The candidates are the six named in all four referee rounds (`HANDOFF` §1 (i)). Each has a test, a prediction and a
reading fixed here (§5 defines M, the bands and DEFINITE).

| id | candidate | the test (arms, §4) | prediction if the candidate is the mechanism |
|---|---|---|---|
| K1 | **ties broken by the jitter, entering through LightGBM's data-derived bins** (the referees' "split ties" and "histogram binning") | V: the tie-preserving, order-preserving jitter of §2 item 6, against A0, the bound protocol's jitter, at the same 10 seeds | the spread vanishes: M_V reads R (removed). Most fits should be bitwise identical to the unjittered float64 base. |
| K2 | **histogram coarseness** (`max_bin`) | B63 and B1023: the bound protocol at `max_bin` 63 and 1023 on all four models, against 255, LightGBM's default and the configuration's | finer bins reduce the spread: M_1023 ≤ 0.5 |
| K3 | **float32 against float64 inputs** | the unjittered base in float64 against the same base in float32 | the two bases differ by at least 0.3 of the jitter spread |
| K4 | **near-degenerate gains flipped by arithmetic noise** | P: the unjittered float64 base with the OmniFold rows permuted (two seeds), against the unpermuted base | the permutation moves the result by at least 0.1 of the jitter spread |
| K5 | **the refinement stage, including its clip** at 2g − 1 < 0 | S-ref: only the refinement's inputs jittered; S-omni: only the OmniFold loop's inputs jittered; S-all: both, through the same code path, as the equivalence control | if the refinement is a sufficient entry: M_ref reads C (carried) |
| K6 | **the W² clamp** (reco W = 0, 1.5 % of events; `M4-W-RECORD.md:8`) | **no separating test is possible here** (below) | — |

**K5 cannot separate the clip from the refinement classifier.** Removing the clip would change the estimator, which is
out of scope. If K5 reads SUPPORTED, the record names "the refinement stage". It gives the clip's share only as a
readout: per jitter, the rows whose clip status differs from the base (§6).

**K6 is not testable by this design, and the record says so.**
- The edge-safe jitter never moves a value on a grid edge (`s5e_trace.py:364-366`), and reco W = 0 is the lower edge.
  So the clamped rows are never perturbed.
- LightGBM also bins zero by itself (`bin.cpp:242-298`, `FindBinWithZeroAsOneBin`, at `kZeroThreshold`).
- What RS1 can say is whether the W axis carries the spread (arm F_W). That is a location, not the clamp.
- The tracer counts the W = 0 rows left unmoved in every product.

**Attribution by axis.** F_k jitters only axis k (k ∈ pT, p∥, E_avail, q3, W; `nd-unfolding/s5c_coverage.py:30`) with
the bound protocol's own draws for that axis: the other axes' steps are set to zero. This arm is paired, seed by seed,
with A0. It is descriptive, and it feeds K6's location statement only.

**Amplification is read, not tested.** If K1 or K2 names the trigger, the referees' next question is why a few rows
changing bin move a functional by a statistical σ. RS1 records two readouts on A0, and neither carries a verdict:
1. the spread per OmniFold iteration, k = 1 to 5, through `s5e_trace.Recorder` (`s5e_trace.py:267-349`, imported
   unchanged);
2. the split tables of every fit, for jitters 1–3 and V's jitters 1–3, against the float64 base: the first tree
   whose structure differs, the share of identical trees, and whether the first difference is a new feature or only a
   new threshold, with both nodes' `split_gain`.

## 4. The arms and their inputs

**The input is FD-STAB's stability pseudo-experiment, unchanged** (`FD-STAB-DECLARATION.md` §3.1):
- the GiBUU-like truth `eavail_shape` at amplitude 1 with `state/s5n/eavail-ratio-gibuu-over-genie.json`;
- pseudo-seed 990000, configuration R, 5 iterations and 32 threads per lane;
- the inputs `of_inputs_5d.npz` (sha256 `07fccc1a…`) and `bkg_dump.npz` (`2addac8f…`), as FD-STAB's queue line
  names them (`fd/receipts-stab-a1r/connect/queue.tsv:2`).

**Why this input.**
- The spread there is about 7× its nominal size (`KNOWN_ISSUES.md` 80), so the ratios of §5 have resolving power.
- A0 can be checked bitwise against FD-STAB's pinned control products (§5.1).
- It is not an F0b truth (`FD-STAB-DECLARATION.md:95-103`).
- No data enter a product. The production loader reads the data file, as in FD-STAB, but the pseudo-experiment's
  measured side is built from the simulation and the background dump alone (`FD-STAB-DECLARATION.md:75-82`).

**Jitter seeds 1–10** in every jittered arm (S-all: 1–5). These are FD-STAB's first ten seeds, so A0 has a bitwise
reference.

| arm | what changes | products | unfolds |
|---|---|---|---:|
| **A0** | nothing: the bound protocol, traced | base in float32; base in float64 (unjittered); jitters 1–10 | 12 |
| **V** | the jitter is keyed on the value, not the row (below) | jitters 1–10 | 10 |
| **F_k**, 5 axes | only axis k is jittered, with the protocol's draws | 5 × jitters 1–10 | 50 |
| **S-ref** | only the refinement sees jittered coordinates; the OmniFold loop gets the unjittered float64 ones | jitters 1–10 | 10 |
| **S-omni** | the refinement runs on the unjittered float64 coordinates; the loop gets jittered ones | jitters 1–10 | 10 |
| **S-all** | both jittered, applied after the experiment is built, as S-ref and S-omni are | jitters 1–5 | 5 |
| **B63**, **B1023** | `max_bin` 63 or 1023 on all four LightGBM models | float64 base; jitters 1–10, each | 22 |
| **P** | the float64 base with the OmniFold input rows permuted (`s5c_unfold.permute`, `nd-unfolding/s5c_unfold.py:106-116`) | seeds 1 and 2 | 2 |
| **total** | | | **121** |

**The value-keyed jitter (V).**
- Each value moves by `u × ½ × ulp↓(x)`, where ulp↓ is the float32 spacing toward zero, `|x| − nextafter(|x|, 0)`,
  and u is in [−1, 1).
- u is a keyed hash (splitmix64) of the seed, the axis and the value's float32 bit pattern. Every row in every array
  that shares a float32 value on an axis moves identically.
- Values on a grid edge are not moved, as in the protocol.
- **Why ulp↓, and not the protocol's ulp:** at a power of two, the spacing above is twice the spacing below. A ±½-ulp
  step could then reorder two adjacent float32 values. With ulp↓ the order is strictly preserved (§8 tests it). The
  two scales differ only at powers of two.

**S-ref, S-omni and S-all.**
- These arms jitter the built experiment's arrays (MC truth and reco, observed, template), not the inputs before the
  experiment is built.
- **S-all is the equivalence control:** jittering after the build should reproduce the protocol's spread in
  distribution. The unfolding MC (half A) and the pseudo-data source (half B) are disjoint rows, so each value is still
  perturbed independently.
- If S-all does not read C against A0 (DEFINITE), S-ref and S-omni are UNINFORMATIVE and K5 is not read.
- **Grid membership** is checked after every post-build jitter, with the same `s5e_trace.flat_index` as
  `s5p_numerics.cell_membership` (`s5p_numerics.py:73-76`). A product whose membership changed is refused.

## 5. The statistics and the readings

**Functionals.** Two sets, each read on its own:
- the 153 s5e reported functionals (`s5c_coverage.reported_functionals`), FD-STAB's set;
- the 16 reported cells R00–R15, by S1's integration rule (`s1_assemble.functional_matrix`,
  `nd-unfolding/s1_assemble.py:119-122`) over the pinned H2 definition (`h2_definition.json`, sha256
  `b6790761…`).

**The spread of an arm.**
- For functional j and arm a: s_{a,j} is the SD, with ddof = 1, of F_{a,j,s} / mean_s(F_{a,j}) − 1 over the arm's
  jitter seeds s. It is taken around the arm's own mean, so no base enters (FD-STAB audit R3,
  `FD-STAB-DECLARATION.md:440`).
- ρ_{a,j} = s_{a,j} / s_{A0,j}, and M_a = median_j ρ_{a,j}.
- A functional with s_{A0,j} = 0 is excluded and counted. If more than 10 % of a set is excluded, that set reads
  INVALID.

**Its interval.**
- 2,000 bootstrap resamples of the seeds, at bootstrap seed 20261106.
- Paired arms (V, F_k, B63, B1023) resample their seeds jointly with A0's; S-ref, S-omni and S-all resample
  independently of it.
- The interval is the 5th to 95th percentile of M_a.

**Bands:**
- **R, removed:** M ≤ 0.10;
- **P, partial:** 0.10 < M < 0.70;
- **C, carried:** M ≥ 0.70.

A reading is **DEFINITE** only when its 90 % interval lies inside one band. Otherwise it is INCONCLUSIVE.

**A base-difference statistic** for K3 and K4: D = median_j |F_{x,j} / F_{ref,j} − 1| / s_{A0,j}.
- K3: x is the float64 base, ref the float32 base.
- K4: x is each permuted base, ref the float64 base. D_P is the larger of the two seeds' values.

### 5.1 Gates, before any reading

- **G1, bitwise reproduction.** A0's float32 base and jitters 1–10 must equal FD-STAB's control products
  `runs/control/stability/stab_control_b-_j-.npz` and `…_j1.npz` to `…_j10.npz` in `xsec_flat`, bitwise. Those
  products are pinned in `fd/receipts-stab-a1r/full/SHA256SUMS` (sha256 `e2c35e55…`, lines 229, 239, 250, 261, 272,
  275-280).
  - The comparison is of arrays, not file digests, because product metadata carries timings.
  - A0 runs with the same thread count and lane layout as FD-STAB: 32 threads, 8 lanes. A bitwise check across jobs
    needs the same thread environment.
  - **If G1 fails, nothing is read.** The run is reported to the director as NOT REPRODUCED.
- **G2, informativeness.** A0 must show a nonzero spread. If more than 10 % of the 153 functionals have
  s_{A0,j} = 0, the study reads UNINFORMATIVE.
- **G3, the tracer is a pass-through.** The traced A0 products must equal the untraced ones bitwise; G1 checks this
  directly. `s5e_trace.traced_unfold` also checks its own rebuild bitwise (`s5e_trace.py:243-264`).

### 5.2 The readings

Each candidate is read on both functional sets. A candidate is SUPPORTED, or NOT SUPPORTED, only if both sets give
the same DEFINITE reading. Otherwise it is INCONCLUSIVE.

| id | SUPPORTED | PARTIAL | NOT SUPPORTED | otherwise |
|---|---|---|---|---|
| K1 | M_V reads R | M_V reads P: tie-breaking is one channel among others | M_V reads C | INCONCLUSIVE |
| K2 | M_1023 ≤ 0.5 and its interval's upper end ≤ 0.7 | — | the interval's lower end ≥ 0.7 | INCONCLUSIVE |
| K3 | D ≥ 0.3 | 0 < D < 0.3: present, below the jitter scale | the two bases are bitwise equal | — |
| K4 | D_P ≥ 0.10 | — | D_P ≤ 0.01 | INCONCLUSIVE |
| K5 | M_ref reads C: the refinement is a sufficient entry | M_ref reads P | M_ref reads R | UNINFORMATIVE if S-all fails |
| K6 | — | — | — | NOT TESTABLE (§3) |

**What each outcome licenses.**
- **K1 SUPPORTED.** The record may say: "on this pseudo-experiment, the perturbation reaches the estimator by breaking
  ties among equal float32 values, which changes LightGBM's histogram bins; a perturbation that keeps the ties removes
  the spread."
  - It may not say that the data's spread has this cause.
  - It may not say that ties are a defect of the inputs. Equal float32 values are what float32 storage of these
    kinematics produces.
- **K2 SUPPORTED.** Finer binning reduces the spread on this input. That is not a remedy; step 2 is where a remedy
  is declared.
- **K3 or K4 SUPPORTED.** The channel exists at the stated size. **K3 or K4 NOT SUPPORTED** re-confirms the s5e
  measurements on this input and estimator.
- **K5.** S-ref and S-omni both reading C means either stage alone is a sufficient entry. Neither is then "the"
  mechanism.
- **The outcome record** names every SUPPORTED candidate, or states that none is supported. That is the stopping
  criterion for step 1.
- **No outcome changes** the estimator, NONE_PASS, or any wording on main.

### 5.3 Predictions, stated before anything runs

This lane's own expectation, from §2. It is not a criterion, and it is printed so that the outcome can be compared
with it:
- K1 SUPPORTED. V should be bitwise equal to the float64 base for most fits, with any residual coming through the
  regressor's untrained rows;
- K3 NOT SUPPORTED (bitwise equal);
- K4 NOT SUPPORTED;
- K2 and K5: no expectation.

## 6. Readouts with no criterion

- **R0, the spread on the 16 reported cells in units of σ_stat.** This answers referee request (iii), and decision
  item 1.3's "first the spread is measured on the sixteen reported cells".
  - It is arithmetic on two records on main, at 0 node-h, done locally:
    - per cell, I0's measured data floor σ_J/f (`fd/receipts-1b/inv/i0/i0.json`, `sigma_J_data`, sha256
      `9a4142d3…`; described at `FD-1B-INV-I0-REPORT.md:66-68`);
    - over S1's statistical σ (`s1/readout/s1_assembly.json`, `relative_sigma`, stat group, sha256 `81e5ef3f…`;
      tabulated at `S1-REPORT.md:253-271`).
  - **Disclosed:** both medians are already printed on main (0.133 % and 0.24 %), so R0 is not blind. S1's stat σ is
    a refit-per-replica data bootstrap, which already carries the rounding spread (`KNOWN_ISSUES.md` 80: about 37 %
    of its variance). So σ_J/σ_stat is a share of a variance that contains it, not a ratio of independent terms.
  - **Two numbers per cell, with their median and range over the 16 cells** (the director's ruling on #867):
    1. **R0a**, the ratio as defined: σ_J,c / σ_S1,c;
    2. **R0b**, the ratio against the rounding-removed stat σ: σ_J,c / √(σ_S1,c² − σ_J,c²).
       - It is well defined in cell c only if σ_S1,c > σ_J,c.
       - Where it is not, the record says so for that cell, gives no value, and computes no median unless all 16 are
         defined.
       - R0b assumes the two variances add, which `KNOWN_ISSUES.md` 80's absorption measurement supports in aggregate
         (replica variance above the rounding variance for every functional) but does not establish per cell. The
         record states that assumption.
  - **Neither number is read as a pass or a fail.** No bar applies to them.
  - **Units.** σ_J/f and S1's `relative_sigma` are both relative. The code reads each file's own unit, refuses if
    either is not stated or not derivable from the file, and prints the unit it used.
  - R0 is the only reading on data-derived numbers, and it reads committed results, not data.
- **Absolute spreads** of every arm in pseudo-data σ: FD-STAB's σ (`state/s5e/cand/assess_receipt.json`
  `sigma_rel_pct`, sha256 `84266e30…`) and FD-STAB's 25-pair statistic, for A0 only. These are for comparison with
  FD-STAB; neither enters §5.2.
- **The per-iteration spread** on A0 (§3), as the ratio s(k)/s(1), k = 1–5, as a median over functionals.
- **The split-table diffs** (§3).
- **Ties in the inputs, per axis and per fit set:** the share of rows whose float32 value is shared with another row.
  It is computed on the built experiment's arrays, which are simulation, inside the job.
- **The clip:** per jitter, the rows whose 2g − 1 < 0 status differs from the base's. The clipped rows' indices are
  stored, about 10³ rows (on data, 1,313; `DIAGNOSIS-20260926-…:80`).
- **The unmoved W = 0 rows**, counted per product.

## 7. Compute

**Unit and price.**
- The unit is FD-STAB's: 657 s of one lane, 0.022828 CPU node-h at 8 lanes per node (`FD-STAB-DECLARATION.md:241-242`).
- Measured on FD-STAB's control, the per-unfold time was about 408 s in four-unfold tasks (task 01: 1,632.2 s,
  `fd/receipts-stab-a1r/full/records/stab_control_stability_01.{start,end}`). The unit is conservative.
- Allowances: +10 % for the tracer and model dumps on every unfold, and 2× for `max_bin` 1023.

| | unfolds | unit-equivalents | CPU node-h |
|---|---:|---:|---:|
| all arms but B1023 | 110 | 121.0 | 2.76 |
| B1023 | 11 | 24.2 | 0.55 |
| **full run, expected** | **121** | **145.2** | **3.31** |

**Cap: 4.5 CPU node-h, dry run and full run together.** It binds three ways:
1. **Slurm's limit, on one node.** The dry run is submitted with `--time=0:45:00` and the full run with
   `--time=3:45:00`. On one exclusive node the charge cannot exceed `--time`. Both are written H:MM:SS:
   `--time=0:45` means 45 seconds, the error that invalidated FD-STAB's first dry run.
2. **The dry run's projection.** The dry run runs 8 one-unfold tasks on 8 lanes:
   - A0's float32 base;
   - A0's float64 base;
   - A0 jitter 1;
   - V jitter 1;
   - B1023's base;
   - B63's base;
   - S-ref jitter 1;
   - P seed 1.

   It checks G1 on the float32 base and jitter 1. The full run starts only if the projected full wall, from the dry
   run's per-kind times packed on 8 lanes, is at most the smaller of 3.75 h and 0.9 × (4.5 − the dry run's `sacct` charge). FD-STAB's 9-task dry run charged 992 s, about 0.28 node-h (`fd/receipts-stab-a1r/sacct-60827080.txt`), so the expected 3.31 h fits with about 12 % to spare. Otherwise it
   returns to the director for a reprice. The dry run's products carry into the full run, which skips them.
3. **No resume without the director.** A stopped or time-limited run leaves no DONE receipt and is not graded; it is
   reported as INCOMPLETE. The job refuses to re-run a mode whose log exists (FD-STAB's rule).

**Rules.**
- CPU only, QOS regular, `--exclusive`, `--no-requeue`.
- Nothing is written to CFS from a job. Products go to `/pscratch/sd/j/josephrb/rs1-20261106/`.
- The charge is read from `sacct` after the job ends, not before the next `sbatch`, because `sacct` lags.
- **The authority bound:** 4.5 is far below half the group balance (2,069.4 node-h remaining, last recorded
  `FD-1B-INV-I0-REPORT.md:61`). The cluster lane reads `iris` before launch.
- **Reads:**
  - the job reads its inputs through the production loaders, as FD-STAB's did;
  - every audit or inspection read uses O_NOATIME;
  - FD-STAB's control products are read for G1 with `dd iflag=noatime` copies.
- **The COV2D fence:** the inputs are the 5D bank and the s5p background dump, not E_R products or the flux
  constraint. The fence script still runs, and `squeue` is checked for `cov2d-*` jobs before every connect.
- **Retention:** FD-STAB's products were written 2026-11-04/05, and the 5D bank was read by FD-STAB on 2026-11-04,
  inside the pscratch window. The dry run's first step is a `stat` of every input and of the G1 references.

**Who runs it.** This lane, after the audit and the director's binding, from a clean deploy at the bound sha (the
director's ruling on #867).
- The dry run goes first.
- Before each connect, the lane sends the director the connect script's sha256.
- `squeue` is checked for `cov2d-*` jobs before any connect, and the check is recorded in the receipts.
- ssh's return code is read unpiped.
- Receipts are committed as PRs.
- If the NERSC certificate has expired, the lane tells the director; Joseph renews it.

## 8. Code plan (written after this declaration is audited, before binding step two)

**No bound module is edited.** One new wrapper module, `nd-unfolding/rounding_mechanism_probe.py`, and one job script.
- **Every arm runs through `estimator_stability_probe.py --candidate control stability`, unchanged** (FD-STAB's
  control path: `s5p_numerics.main` with `Recorded` pass-through estimators). G1 proves that path reproduces FD-STAB.
- The wrapper installs one arm-specific rebinding, for one invocation, before calling it.
- **Each rebinding:**

| arm | rebinding (resolved at call time by the bound code) |
|---|---|
| F_k | `s5e_trace.jitter_coords` → the same draws, with the other axes' steps zeroed |
| V | `s5e_trace.jitter_coords` → the value-keyed jitter |
| S-ref, S-omni, S-all | `s5p_numerics.unfold_one` → jitter the built experiment's arrays for the refinement, the loop, or both, then check grid membership |
| B63, B1023 | `s5c_unfold.config_params` → add `max_bin`, which the refinement also reads (`s5n_pseudo.py:234-236`); `s5c_unfold.unfold` already verifies every built estimator's parameters (`s5c_unfold.py:129-134`) |
| P | `s5c_unfold.unfold` → `s5c_unfold.permute` first |
| A0 trace | `omnifold_nn_core.make_estimators` → a recorder of each fit's model dump; `s5e_trace.traced_unfold` for the per-iteration functionals |

- **Order of installation matters,** because `estimator_stability_probe.install` captures `s5c_unfold.config_params` when it
  runs (`estimator_stability_probe.py:267-268`). A test shows the composed parameters reach every estimator.

**The job script** is `nd-unfolding/sbatch_rs1.sh`, modelled on `sbatch_fd_stab.sh`:
- the same deploy-pin check, log refusal, environment check, `SHA256SUMS` on every outcome and DONE receipt;
- no adaptive gate, since the cap binds by `--time` on one node (§7).

**The analysis** is `rounding_mechanism_analyze.py`:
- it reads only a run with a DONE receipt;
- it evaluates G1–G3, then §5.2;
- it writes one readout JSON.

**Tests, local, with stand-in estimators, as FD-STAB's.** Each is tested in the direction it acts and in the other:
- **V:** order and ties preserved on every float32 binade boundary, including both sides of every power of two
  in [2⁻¹⁰, 2¹⁰]; equal values move identically across arrays; edge values unmoved;
- **V, a counterfactual:** the protocol's row-keyed jitter does reorder or break ties in the same fixture;
- **F_k:** the masked draws equal the protocol's on axis k, bitwise;
- **the composed config parameters** reach all four models;
- **post-build jitter:** refused when membership changes;
- **G1:** refuses on a one-ulp difference; passes on a metadata-only difference;
- **the readings:** every band boundary and INCONCLUSIVE case, in both directions;
- **K3:** NOT SUPPORTED only on bitwise equality;
- **INVALID and UNINFORMATIVE** branches;
- **the analysis** refuses a run with no DONE receipt;
- **every queue line** runs through the real runners' parsers (FD-STAB's `RealParsers` lesson);
- **a mutation harness:** one planted defect per guard and per reading, each killed by a named test.

**Not testable locally:** LightGBM itself. §2 item 6's invariance under V is a property of LightGBM. The dry run's V
jitter 1 is its first test on the real code, and the record reports it as measured.

## 9. Limits and disclosures

- **One pseudo-experiment realization**, and 10 jitters per arm (S-all: 5). The intervals cover the jitter draws,
  not the realization.
- **The GiBUU-like input** is the development truth of the paper's Fig. 3 and lies within 2 % in shape of Stage 0c
  GiBUU (`FD-STAB-DECLARATION.md:100-103`). RS1 adopts nothing, so the selection-contamination rule (ii) is not
  engaged. Step 2 must weigh it if it uses this input.
- **V tests one counterfactual.** It shows whether breaking ties is necessary for the spread. It does not show that
  real-world rounding differences, such as driver against npz (`KNOWN_ISSUES.md` 79), act only by breaking ties. Those
  can also merge or split float32 values.
- **K2 varies `max_bin` on all four models together.** It does not separate the refinement's binning from the loop's.
- **R0 is not blind** (§6).
- **The LightGBM source facts** are read at tag v4.6.0. The cluster's build is assumed to match it; the dry run's
  environment log prints the version.

## 10. Open items for the audit and the binding

1. **Settled by the director:**
   - #865 is merged and is cited at `6d0aca7f`;
   - R0 is in scope, with the two ratios of §6;
   - this lane runs the jobs (§7).
2. **The bands** (0.10, 0.70) and the K2/K3/K4 thresholds are this lane's choice, made before any number. The audit
   may tighten them.
3. **Ten jitters per arm.** Doubling them would add about 2.8 node-h, still under half the group balance by far.
   The audit may ask for it.

## 11. What follows: step 2, declared separately

Step 2 is the ensemble-averaged estimator: the mean over N perturbed fits, with its spread as a numerical uncertainty.
- It is declared after RS1 is bound, and before RS1's outcome is read.
- Its acceptance is the same 0.3 / 1.0 bars (`HANDOFF` §2 item 2).
- If K1 reads SUPPORTED, step 2's perturbation can be chosen with knowledge of the channel. The order of declaration
  is set so that its acceptance is fixed first.
- Whether a passing variant replaces the reported estimator is Joseph's decision.
