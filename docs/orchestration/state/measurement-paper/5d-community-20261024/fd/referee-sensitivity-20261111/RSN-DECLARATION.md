# RSN declaration: three referee sensitivity analyses (3.1, 3.2, 1.2), DRAFT

**Session:** tier3-design, 2026-11-11, at the director's brief. **For:** coverage-5b-audit's audit, then the director's
binding. After the maintenance, a cluster lane runs it, and each connect's sha256s go to the director first.

**Status:** draft. The code and tests are under `nd-unfolding/rsn/`, with receipts in `rev1/`. No job has been
submitted and no connect made. The work does not wait for the LL5D readout.

## 0. What this is

**The request.** The recheck referee report asks for three analyses: `secondary-results/referee-methods-recheck-20261111/gpt.txt`
(#1074), major issue 3 (:44-52) and major issue 1 (:17-19). helper-3 designed them in #977's `RESPONSE.md` at
`d1d6f1ded`: rows 3.1 (:41), 3.2 (:42) and 1.2's optional A (:28). The director's rulings (:142-158) approve them in
principle at about 0.75 node-h, with this chain.

**The arms.**

| arm | referee | what changes | unfolds |
|---|---|---|---|
| **G6** | 3.1: a common supported phase space | GiBUU's reweight is restricted to p∥ < 6 GeV/c | 1 |
| **SM** | 3.2: a less discontinuous ratio | the three reweights are smoothed by a local average | 3 |
| **WR** | 1.2: the unmatched-event regressor | the regressor is fitted with the simulation's event weights | 1 data + 2 closures |
| **NC** | — | none: it must equal P5 bitwise after the maintenance | 1 |

**How the results enter the paper.** Each result enters only as a stated sensitivity of the construction named here,
**never as a calibrated uncertainty.** No C^V, shift or δ is added to a reported covariance, and none replaces
C_model in a reported result. Every reading below is fixed before any run (§3), with the paper conclusions it can
and cannot change (§3.4).

## 1. Inputs

Every input is checked by its sha256 before it is read. A missing input or a different digest refuses, so a purged
pscratch copy stops the arm. The pv-ladder `prep/` and `products/` copies are exposed from 2026-12-19
(`FD-PSCRATCH-RETENTION-PROPOSAL.md:77`).

| input | sha256 | role |
|---|---|---|
| pv-ladder `prep/ratios/L-5D-PV/` (pscratch), checked through the committed `nd-unfolding/pv-ladder/prep-SHA256SUMS` (`29ac6b7c…`) | per file: `925cbd8d…` ratios.json, `8d0e0f42…` genie_mec, `38e47eb6…` nuwro, `52438000…` gibuu, `13bb1eae…` tune_v1 | the frozen gated reweights, their ρ, labels and prior weights |
| pv-ladder `products/` (pscratch): L-5D-PV_e_{tune_v1, genie_mec, nuwro, gibuu, closure_nuwro, closure_tune_v1} | `build_cmodel5d.py` EXPECT (`dbe9a95e…`, `bdff9193…`, `caf6eee7…`, `bdf33157…`, `fff9030e…`, `eb3e2188…`) | the frozen shifts and closures |
| P5, `k1_p5_rerun.npz` | `e36f3b25…` | the NC's target |
| `of_inputs_5d.npz`, `bkg_dump.npz` (pv-ladder `config.json`, L-5D-PV) | `07fccc1a…`, `2addac8f…` | the unfold's inputs, as L-5D-PV |
| `readouts/cmodel_5d.json` (committed) | `3cfdc6a5…` | S and the nominal C_model (GiBUU 0.890 of the trace, NuWro 0.095, GENIE+MEC 0.014) |
| `readouts/h2_definition_describe.json`, `readouts/gibuu_domain_cells.json` (committed) | `da7edae0…`, `855eeff6…` | the prep's reproduction controls |
| `fd/with-cpl/readout/fd_f1_readout.json` (committed) | `5ccc89e5…` | the 22 records' committed grades (NC-R) and the reported σ |
| `fd_f1_experiments.npz` (pscratch `fd-f1-20261027/grade/`; HPSS manifest `retention-20261110/hpss-20261111`) | `997c7dae…` | the per-experiment biases the noise of each mean is rebuilt from |
| `fd/receipts-f1/run/cluster/f1b3/prep/f1-prep-SHA256SUMS` (committed) | `981b188b…` | the two held-out truths' identities |
| `s1_assembly.npz` (pscratch), `cpl_block.npz` key `C_resp_plus_C_PL5D` (pscratch) | `db000707…`, `d9aa32fd…` | C_e, the stat block, f and C_resp + C_PL,5D |
| the NuE constraint file (`s1_assemble.CONSTRAINT_SHA256`) | `e38ad7d2…` | the row-6 and row-4 flux weights |
| `fd/receipts-1b/inv/i0/i0.json` (committed) | `9a4142d3…` | WR's rounding floor σ_J (§3.3) |

## 2. The arms

### 2.1 G6 (referee 3.1): GiBUU on a common supported phase space

**The construction.** It is GiBUU's frozen gated ratio with every fine cell whose upper p∥ edge exceeds 6 GeV/c set to
r = 1 and labelled off. `pvl_lib.normalize` then rescales the remaining assigned cells. This is
`H2-DEFINITION-ADDENDUM-GIBUU-DOMAIN.md` §3's option (ii), computed exactly as `gibuu_domain_cells.py` computes it
(k 1.2059 → 1.2012). J has an edge at 6, so every ρ and label below 6 is what `pvl_ratios.py` gives with
pz_max = 6. GENIE+MEC and NuWro keep their frozen ratios, so one unfold runs.

**Why 6 GeV/c.** Below 6 GeV/c every sample holds the cross section. GiBUU's missing E_ν > 20 GeV part is 0.98 % of
the cross section there in GENIE CV and 1.01 % in NuWro. At 6–10 GeV/c it is 4.88 % and 5.26 %
(`gibuu_enu_coverage.json`, the addendum's §1 table). The paper's joint tests already use p∥ < 6. G6 removes the
momentum-dependent application cut at 10 and the E_ν truncation from GiBUU's shift, and nothing else.

**What G6 does not address.** It does not address the carbon-versus-CH difference, because no CH sample of NuWro or
GiBUU is in this design (the referee: a validated free-proton sample "is not a prerequisite").

### 2.2 SM (referee 3.2): a less discontinuous ratio construction

**The construction.** For each of the three vertices, SM takes the prior-weighted moving average of the frozen
reweight r over each region cell's radius-R neighbourhood: the region cells within R fine bins on every axis.
`normalize` then rescales the region cells with prior weight. Off cells keep r = 1. The total prior weight in the
region is unchanged, as in the frozen construction. GiBUU keeps its p∥ < 10 domain, so SM changes one thing:
discontinuity.

**The manipulation check, fixed now.** The step share is computed per reporting cell: the prior's truth weight in fine
cells that have an axis neighbour whose r differs by more than 0.1 (`pvl_lib.STEP`), whatever the labels, taken as a
union over the three vertices. SM is less discontinuous only if two conditions hold:
- its median share over R00–R15 is at most half the frozen construction's;
- its share is at most the frozen share in at least 12 of the 16 cells.

The frozen gate-or-cut share is 0.765–1.000 (`h2_definition_describe.json`); the prep reproduces it as a control.
R = 1 is tried first, and R = 2 only if R = 1 fails. If both fail, the prep writes no SM reweight and SM does not
run: J2n replaces J2 (§6). The result is then reported as "no construction of this family at R ≤ 2 was less
discontinuous by the declared measure", and SM gives no reading of C_model.

### 2.3 WR (referee 1.2): the unmatched-event regressor with event weights

**The change.** `omnifold_nn_core.omnifold_loop` fits its regressor with no sample weight (`:258-260` at `8f99b7ff`):
`reg.fit(MCgen[pass_reco], new_w[pass_reco])`. WR fits it with `sample_weight` = w_truth of those rows, which is
`MCgen_weights[pass_reco]` in the loop's own order. It is the weight under which step 2 sums the pull weights at
truth level, so the fit estimates the w_truth-weighted mean of the step-1 weight at fixed truth.

**Why w_push is not in the weight.** w_push depends on the truth features alone, so including it would change only the
fit's emphasis, not the conditional mean it estimates.

**What stays the same.** The classifiers, their weights, the seeds and the estimator parameters do not change.
`omnifold_nn_core.py` is not edited. `rsn_unfold.py` wraps the regressor that `make_estimators` returns, one level
inside `s5c_unfold.estimator_config`, and refuses to write unless every iteration fitted through the wrapper with
exactly the expected rows.

**The three WR runs:**
- the data;
- the noise-free closure at the prior (the floor);
- the noise-free closure at NuWro's shape (L-5D-PV's positive-control truth).

### 2.4 NC

`rsn_nc` is `rsn_unfold.py --regressor-weight none` on the data with the identity reweight. It must equal P5, and so
the frozen L-5D-PV_e_tune_v1, bitwise on the full grid and on the 16 cells (`build_cmodel5d.nominal_control`). It runs
alone first (J1). Without its PASS, J2 is not submitted, and the director decides any rerun of the frozen products in
the new environment. Every shift below is taken from rsn_nc.

## 3. Readings and outcome tables (fixed before any run)

The conclusions they bear on are P1–P7 in §3.4.

### 3.1 C^V for V ∈ {G6, SM}: what is graded and against what

**The rows of each arm's shifts:**
- **G6:** S^G6 = (s_GENIE+MEC, s_NuWro, s′_GiBUU), with the first two rows cmodel_5d.json's own.
- **SM:** S^SM = (s′_k), one row per vertex.

C^V = S^V^T S^V. A rebuild of the frozen S must equal cmodel_5d.json's S bitwise (NC-S).

**P4: q, the ratio of model σ.** q_c = √diag(C^V)_c / √diag(C_model)_c on R00–R15. It is classed as follows:

| class | rule |
|---|---|
| C_model smaller | median q < 0.8 |
| C_model larger | median q > 1.25 |
| C_model similar | median q in [0.8, 1.25] and every q_c in [0.5, 2] |
| C_model reshaped | otherwise |

GiBUU's trace share and tr(C^V)/tr(C_model) are printed beside the class, against 0.890.

**P5: the reported σ.** The per-cell ratio of √diag(C_e + C^V + C_resp + C_PL,5D) to the reported σ is printed as a
median, a minimum and a maximum. It is descriptive.

### 3.2 The fake-data regrade under C^V

**What is graded.** It grades the 22 records of the committed F1 readout:
- F0b's 18 truths: the prior, W1–W3, the q3 tilt, the Stage-0c GiBUU shape, the NuWro closure, the five A7 truths,
  and the six row-6 power alternatives, which stay ungraded because control 7 failed;
- the two held-out GENIE v3 tunes, each as 20 pseudo-experiments and one closure.

**Against what.** Each bias is the committed one, and the noise is rebuilt from the committed table. Each is graded
against fd_f0_regrade's own matrices with S → S^V: C^(T) = C_e/(ff^T) + Σ_{j≠own(T)} s_j^V s_j^V^T + C_x/(ff^T),
together with the in-sample, sensitivity, eight-cell and model-only matrices. The triggers are unchanged: a cell with
|z| > 2, or a truth with p < 0.01, counted by group.

**The controls:**
- **NC-R:** under cmodel_5d.json's S, every record reproduces the committed readout, field for field.
- **C-INV:** G6 changes GiBUU's row only, so every record graded without GiBUU's shift must grade bitwise as nominal.

**The nominal results being tested:**
- **listed:** {q3: p < 0.01; A7_gibuu: R02 and R06, p < 0.01};
- **prior:** 0 of 32 cells and 0 of 2 truths;
- **vertex-family:** 2 of 128 cells and 1 of 8 truths;
- **non-vertex:** 0 of 32 cells and 1 of 2 truths;
- **held-out:** 0 of 64 cells and 0 of 4 truths.

**P1, the listed set L^V:**

| class | rule |
|---|---|
| unchanged | L^V = L |
| fewer flagged | L^V ⊂ L |
| more flagged | L^V ⊃ L |
| different flagged | otherwise |

**P2 and P3.** P2 is each group's counts beside the nominal's, with every record's χ² under both. P3 asks whether the
four held-out records still meet both criteria (0 cells with |z| > 2, 0 truths with p < 0.01).

**Each arm's verdict:**
- "the fake-data conclusions survive V" if P1 is unchanged and P3 holds;
- otherwise "a fake-data conclusion changes under V", with the records named.

**What G6 cannot move, stated before the run.** A7_gibuu and stage0c_gibuu are graded without GiBUU's shift, so G6
cannot change either grade; C-INV enforces this. G6 can move only records graded with GiBUU's shift: q3, the prior
truths, the GENIE CV hybrid, the NuWro and GENIE+MEC family, and the held-out records. SM can move every record.

### 3.3 WR: what is graded, against what and at which truths

**P6, the data.** P6 is δ_c = X_c(WR_data)/X_c(rsn_nc) − 1 on R00–R15, graded against two references:
- the rounding floor φ_c = σ_J,c / x_c, from i0.json's data jitter spread over cmodel_5d.json's P5 integrals. It
  must reproduce the printed median 0.133 %, minimum 0.055 % and maximum 0.252 % (FD-1B-INV-I0-REPORT.md:67).
- the reported σ_c, from the F1 readout's C_total + C_resp + C_PL,5D.

| class | rule |
|---|---|
| W0, within the rounding floor | max_c \|δ_c\|/φ_c ≤ 2 |
| W1, above the floor and below half the reported σ | not W0, and max_c \|δ_c\|/σ_c ≤ 0.5 |
| W2, at least half the reported σ | some \|δ_c\|/σ_c > 0.5; the cells are named |

**P7, the two closures.** The truths are the prior (Tune v1) and NuWro's shape. Each bias is X/X_true − 1 on the 16
cells, beside the frozen unweighted closure at the same truth.
- **NuWro closure:** the RMS ratio RMS(b^W)/RMS(b) is "lower" below 0.9, "higher" above 1.1, and "comparable"
  otherwise; the largest |b^W − b| is printed.
- **Floor:** max |b^W| > 1e-4 flags "the weighted regressor breaks the prior's closure" (frozen: 3.2e-5).

WR re-grades no fake-data truth beyond these two closures.

### 3.4 Which paper conclusions each arm could change

| | conclusion | G6 | SM | WR |
|---|---|---|---|---|
| P1 | the fake-data bias exceeds the criteria at two truths (A7_gibuu, the q3 tilt) | q3 only | yes | — |
| P2 | the other truths meet the criteria only with the broader terms, C_model among them | yes | yes | — |
| P3 | the four held-out records meet both criteria (R11 at G18 only with C_model) | yes | yes | — |
| P4 | C_model is dominated by the GiBUU shift (0.890) | yes | yes | — |
| P5 | the reported per-cell σ of the sixteen released cells | yes | yes | — |
| P6 | the sixteen released central values | — | — | yes |
| P7 | the noise-free closures at the prior and at NuWro | — | — | yes |

**What no arm changes:**
- the 2D benchmark, whose comparison uses no C_model;
- the prior-retention study;
- the rounding study;
- the 2D coverage results;
- LL5D's test, whose design and covariance are its own declaration's and are not regraded here;
- the Stage G generator χ² (S10, Tables S14–S15), which this design does not recompute.

**The paper's wording under each outcome** is a stated sensitivity: "Under [G6/SM], [class]; the fake-data conclusions
[survive / change for X]". It is never an uncertainty added to the result. The 3.x text that waits for these results
must read correctly under every class above (RESPONSE.md, the director's rulings).

## 4. Seeds

| what | seeds and settings |
|---|---|
| every unfold | LightGBM random_state 42 for both classifiers and the regressor; the refinement classifier 45 (s5e candidate R); deterministic, force_row_wise, 32 threads, all-row binning, 5 iterations; the same as L-5D-PV |
| the data unfold | deterministic, so the training-seed block is zero |
| the closures | noise-free, so no pseudo-data draw |
| the regrade | re-reads the committed experiments at their recorded pseudo-seeds (rows 1–2, the A7 f4 seeds 970000–970015, the cal and pow sets, F1's 806000–806019 and 807000–807019); it draws nothing |

## 5. Price

**The basis.** pv-ladder's `LEDGER.tsv` records two jobs on one exclusive node:
- **J5, 60206336:** 5 L-5D-PV unfolds (3 data, 2 closures) in 811 s, 0.2253 node-h;
- **J1, 60202786:** 7 steps, the 5D NC among them, in 861 s, 0.2392 node-h. Its longest step took 13:45 and its
  MaxRSS was 16.5 GB or less.

The charge is per node-time, so concurrent 5D steps share one job's price.

**The director's figure.** It reads `BINDING.md:15`, a projection made before any job: "about 0.45 node-h" for three
5D unfolds, 0.15 each. That basis prices the arms at 3.1 0.15, 3.2 0.45 and 1.2 0.15 (data only).

| job | steps | projection | `--time` (1.25×) | maximum |
|---|---|---|---|---|
| J1 | rsn_nc alone | 15 min, 0.25 node-h | 0:19:00 | 0.32 |
| J2 | G6 (1), SM (3), WR (3): 7 steps | 15 min, 0.25 node-h | 0:19:00 | 0.32 |
| J2n (only instead of J2) | G6, WR: 4 steps | 15 min, 0.25 node-h | 0:19:00 | 0.32 |

**Per arm,** with J2 shared by step:

| arm | price |
|---|---|
| G6 | 0.04 node-h |
| SM | 0.11 node-h |
| WR | 0.11 node-h |
| NC (J1, shared by all) | 0.25 node-h |

Each arm alone would be one 15-minute job, 0.25 node-h.

**The total.** It is projected at 0.50 node-h, with a hard maximum of 0.63 at the two time limits. The cap is the
director's 0.75 CPU node-h. The prep, the build, the regrade and the readings run on a login node at 0 node-h.

**The stop rule.** The scheduler enforces the 1.25× limit. A stopped job is reported to the director and is not
resubmitted without the director's go.

## 6. Order and gates

1. **Audit and binding.** coverage-5b-audit audits this draft, and the director binds the code digests of §7.
2. **Connect 1, login node.**
   - Clone at the pin.
   - Run `rsn_prep.py --ratios <pvl prep>/ratios/L-5D-PV --out <OUT>/prep`.
   - Commit its printed `rsn-prep-SHA256SUMS` and `prep.json` in a receipt PR (the new pin).
   - Write `<OUT>/fence.txt`, after the director has announced the `rsn_` family to every fenced lane.
   - Submit J1.
3. **After J1.**
   - Run `rsn_cmodel.py nc` on a login node and commit its PASS.
   - Write `<OUT>/gates/J2.ok` (or J2n) naming the pin.
   - Submit J2, or J2n if the prep built no SM.
4. **After J2, login node:**
   - `rsn_cmodel.py build`;
   - `rsn_regrade.py`;
   - `rsn_read.py`.
   The readouts are committed with the run's receipts.

**The launcher's refusals.** `sbatch_rsn.sh` refuses before any step if:
- the deploy is not clean at the pin;
- the job's name is not `rsn_<job>`;
- its TimeLimit exceeds 0:19:00;
- a fenced prefix is queued or running;
- a reweight differs from its committed sha256;
- a product exists;
- for J2 or J2n, the gate, the NC PASS or the committed reweight list is missing.

The inputs are read, not written, and the fence check covers any lane that writes them.

## 7. Code

| file | sha256 |
|---|---|
| `nd-unfolding/rsn/rsn_prep.py` | `7b0fc567776d2016897173b1f8ab723fd99daedd34454537b36cd42bd03194be` |
| `nd-unfolding/rsn/rsn_unfold.py` | `ab9aea66420c2bdeb05eab69a592846e369d68bf9681196010ea0d2043a3593c` |
| `nd-unfolding/rsn/rsn_cmodel.py` | `ffbb440c6d2212c92a40854dba4d404ed494376ac8a074f8ffff661ce893c8b7` |
| `nd-unfolding/rsn/rsn_regrade.py` | `7dc8039bdf7c4ab396cb3a7e730b6382124e6bf695cf580654e341d703ac40d9` |
| `nd-unfolding/rsn/rsn_read.py` | `1c25f0bbb26203817f37e794c85f851ab502efebd0e08e19279019874c68f83e` |
| `nd-unfolding/rsn/sbatch_rsn.sh` | `745ebc9b53920f4ab2528b5cd95912265da00f0c0a082074c8af12bde72c302b` |
| `nd-unfolding/rsn/rsn_tasks.tsv` | `19cb58cd66f52705d56efaffa365a75af9fe64d001affe814ddfb33dff9cf5d7` |
| `nd-unfolding/rsn/test_rsn.py` | `6116277057c37361b2ef240e0b8e0a5b9ad338b3f164dfc527be4d4cd6231ebf` |
| `nd-unfolding/rsn/rsn_mutation.py` | `14a9a710c88d0e56e8c949f420a5f525e92bba1f163c7e9e38ce29e37ebe52ab` |

These files are used unchanged: `pvl_unfold.py` `59ab0e11…`, `pvl_lib.py` `f8a7d2c2…`, `omnifold_nn_core.py`
`24f87f11…`, `fd_f0_regrade.py` `0dfa722c…`, `build_cmodel5d.py` `aaa81575…`.

## 8. Tests and mutants

`test_rsn.py` is numpy-only. The estimators are stubs, and the products and records are synthetic; the committed
records the code pins are read from the checkout. It covers:
- the box sum against a brute force;
- the smoothing's weighted mean and normalization;
- G6's cut and rescaling;
- the step share;
- the manipulation check's boundaries and the radius ladder;
- each prep control's refusal;
- the weighted regressor's rows, weights and fit count, and every refusal and patch restore;
- the arms' rows and the WR biases;
- the NC, NC-S and meta refusals;
- the regrade's estimates and matrices against fd_f0_regrade's own functions;
- NC-R refusing on each differing field, and C-INV;
- every outcome table's boundaries;
- the launcher's refusals and its seven declared steps, in smoke mode.

`rsn_mutation.py` plants 70 declared defects. Each must be killed by its named test. The receipts are in `rev1/`
(clean clone, serial, nice 19, one thread).

## 9. CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the declared design, readings, outcome tables, seeds and price, before any run.
- **Not citable for:**
  - any result;
  - a calibrated uncertainty;
  - a change to C_model, to a grade or to a criterion;
  - the carbon-versus-CH difference;
  - LL5D's coverage under a changed C_model;
  - the Stage G χ²;
  - any paper sentence.
