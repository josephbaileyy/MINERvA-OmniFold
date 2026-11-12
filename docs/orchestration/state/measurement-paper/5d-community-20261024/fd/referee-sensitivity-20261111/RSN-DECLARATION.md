# RSN declaration rev 3: referee sensitivity analyses (3.1, 3.2, 1.2; fresh F1.1, F1.2), DRAFT

**Session:** tier3-design, 2026-11-11, at the director's brief, its rev 2 request and its rulings on the audit of
rev 2. **For:** coverage-5b-audit's recheck, then the director's binding. After the maintenance, a cluster lane runs it, and each
connect's sha256s go to the director first.

**Status:** draft. The code and tests are under `nd-unfolding/rsn/`, with receipts in `rev3/` (rev 1's and rev 2's are
in `rev1/` and `rev2/`). No job has been submitted and no connect made. The work does not wait for the LL5D readout.
§10 lists what rev 2 changed, and §11 what rev 3 changes.

## 0. What this is

**The requests:**
- The recheck referee report (`secondary-results/referee-methods-recheck-20261111/gpt.txt`, #1074): major issue 3
  (:44-52) and major issue 1 (:17-19).
- The fresh referee report (`secondary-results/referee-methods-fresh-20261111/gpt.txt`): major issue 1 (:11-21),
  "the treatment of unreconstructed events needs a controlled validation".
- helper-3's designs in #977's `RESPONSE.md`:
  - rows 3.1, 3.2 and 1.2 at `d1d6f1ded` (:41, :42, :28);
  - rows F1.1 and F1.2 at `39d0ff8c` (:226-227).

**The arms:**

| arm | referee | what changes | unfolds |
|---|---|---|---|
| **G6** | 3.1: a common supported phase space | GiBUU's reweight is restricted to p∥ < 6 GeV/c | 1 |
| **SM** | 3.2: a less discontinuous ratio | the three reweights are smoothed by a local average | 3 |
| **WR** | 1.2 and F1.1: the misses regressor, physically weighted | the regressor is fitted with sample_weight = w_push · w_truth | data + 4 closures |
| **WU** | F1.1: the equal-weight references at the deformed truths | none (nominal regressor) at the A7 GiBUU hybrid and the q3 tilt | 2 closures |
| **TR** | F1.2(ii): a transfer test in simulation | a held-out regressor fit beside the loop, the loop untouched | rides on 3 steps |
| **NC** | — | none: it must equal P5 bitwise after the maintenance | 1 |

**F1.2(i) is not declared here:** the widened regressor inputs. Its inputs are not in the analysis sample, so it cannot
be priced as a cheap arm (§2.7).

**How the results enter the paper.** Each result enters only as a stated sensitivity of the construction named here,
**never as a calibrated uncertainty.** No C^V, shift or δ is added to a reported covariance, and none replaces
C_model or the estimator in a reported result. Every reading below is fixed before any run (§3), with the paper
conclusions it can and cannot change (§3.4).

## 1. Inputs

Every input is checked by its sha256 before it is read. A missing input or a different digest refuses.
- **pv-ladder `prep/` and `products/`:** exposed from 2026-12-19 (`FD-PSCRATCH-RETENTION-PROPOSAL.md:77`). Of them, HPSS
  (`retention-20261110/hpss-20261111/manifests`) holds only nuwro.json and the two frozen closures. The run must
  happen before 12-19 or after these are archived (§6, the HPSS recommendation).
- **`cpl_block.npz`:** not in those manifests.

| input | sha256 | role |
|---|---|---|
| pv-ladder `prep/ratios/L-5D-PV/` (pscratch), checked through the committed `nd-unfolding/pv-ladder/prep-SHA256SUMS` (`29ac6b7c…`) | per file: `925cbd8d…` ratios.json, `8d0e0f42…` genie_mec, `38e47eb6…` nuwro, `52438000…` gibuu, `13bb1eae…` tune_v1 | the frozen gated reweights, their ρ, labels and prior weights |
| pv-ladder `products/` (pscratch): L-5D-PV_e_{tune_v1, genie_mec, nuwro, gibuu, closure_nuwro, closure_tune_v1} | `build_cmodel5d.py` EXPECT (`dbe9a95e…`, `bdff9193…`, `caf6eee7…`, `bdf33157…`, `fff9030e…`, `eb3e2188…`) | the frozen shifts and closures |
| P5, `k1_p5_rerun.npz` (also tracked, `fd/receipts-f1/run/cluster/f1b3/prep/`) | `e36f3b25…` | the NC's target |
| `of_inputs_5d.npz`, `bkg_dump.npz` (pv-ladder `config.json`, L-5D-PV; on HPSS) | `07fccc1a…`, `2addac8f…` | the unfold's inputs, as L-5D-PV |
| `docs/orchestration/state/s5p/ratios/nullsF/null-gibuu_cv-F.json` (committed), with its `rho-gibuu_cv-F.npz` (pscratch `s5p-20260926`, on HPSS) | `0080495c…` (fd_f0_regrade HYP), `d8f52112…` | F0b's A7 GiBUU hybrid truth (§2.5) |
| `readouts/cmodel_5d.json` (committed) | `3cfdc6a5…` | S and the nominal C_model (GiBUU 0.890 of the trace, NuWro 0.095, GENIE+MEC 0.014) |
| `readouts/h2_definition.json`, `h2_definition_describe.json`, `gibuu_domain_cells.json` (committed) | `b6790761…`, `da7edae0…`, `855eeff6…` | the cells; the prep's reproduction controls |
| `fd/with-cpl/readout/fd_f1_readout.json` (committed) | `5ccc89e5…` | the 22 records' committed grades (NC-R) and the reported σ |
| `fd_f1_experiments.npz` (pscratch `fd-f1-20261027/grade/`; on HPSS) | `997c7dae…` | the per-experiment biases the noise of each mean is rebuilt from |
| `fd/receipts-f1/run/cluster/f1b3/prep/f1-prep-SHA256SUMS` (committed) | `981b188b…` | the two held-out truths' identities |
| `s1_assembly.npz` (pscratch; on HPSS), `cpl_block.npz` key `C_resp_plus_C_PL5D` (pscratch) | `db000707…`, `d9aa32fd…` | C_e, the stat block, f and C_resp + C_PL,5D |
| the NuE constraint file (`s1_assemble.CONSTRAINT_SHA256`) | `e38ad7d2…` | the row-6 and row-4 flux weights |
| `fd/receipts-1b/inv/i0/i0.json` (committed) | `9a4142d3…` | WR's and TR's rounding floor σ_J (§3.3) |

## 2. The arms

### 2.1 G6 (referee 3.1): GiBUU on a common supported phase space

**The construction.** It is GiBUU's frozen gated ratio with every fine cell whose upper p∥ edge exceeds 6 GeV/c set to
r = 1 and labelled off. `pvl_lib.normalize` then rescales the remaining assigned cells. This is
`H2-DEFINITION-ADDENDUM-GIBUU-DOMAIN.md` §3's option (ii), computed exactly as `gibuu_domain_cells.py` computes it
(k 1.2059 → 1.2012). J has an edge at 6, so every ρ and label below 6 is what `pvl_ratios.py` gives with
pz_max = 6. GENIE+MEC and NuWro keep their frozen ratios, so one unfold runs.

**Why 6 GeV/c.** Below 6 GeV/c every sample holds the cross section. GiBUU's missing E_ν > 20 GeV part is 0.98 % of
the cross section there in GENIE CV and 1.01 % in NuWro. At 6–10 GeV/c it is 4.88 % and 5.26 %
(`gibuu_enu_coverage.json`, the addendum's §1 table). G6 removes the momentum-dependent application cut at 10 and the
E_ν truncation from GiBUU's shift, and nothing else.

**What G6 does not address.** It does not address the carbon-versus-CH difference, because no CH sample of NuWro or
GiBUU is in this design.

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
R = 1 is tried first, and R = 2 only if R = 1 fails. If both fail, the prep writes no SM reweight and J2n replaces J2
(§6). The result is then reported as "no construction of this family at R ≤ 2 was less discontinuous by the declared
measure", and SM gives no reading of C_model.

### 2.3 WR (referee 1.2, fresh F1.1): the misses regressor, physically weighted

**The weight.** `omnifold_nn_core.omnifold_loop` fits its regressor with no sample weight (`:258-260` at `8f99b7ff`).
WR fits it with `sample_weight` = w_push · w_truth on its rows, the truth-passing, reco-passing MC rows in the loop's
own order. This is the population the loop is reweighting at that iteration.

**This weight supersedes rev 1's w_truth (the director's ruling, 2026-11-11).** It is the same weight as T3's MW arm
(`tier3/t3p_arms.py:15-16`; `T3-PIPELINE-TESTS-DECLARATION.md` rev 4 :235), so the repository has one definition of "the
weighted misses regressor". Two definitions in two lanes would make WR's and MW's readings incomparable at the same
truths. w_truth alone is not run. w_push is the loop's own value: the output of `omnifold_nn_core._reweight` for the loop's second
classifier, which is ones before the first iteration.
<!-- absence-ok: scoping statement about RSN's declared arms (no w_truth-only arm), not a claim that a result does not exist -->

**What stays the same.** The classifiers, their weights, the seeds and the estimator parameters do not change.
`omnifold_nn_core.py` is not edited. `rsn_unfold.py` wraps the regressor that `make_estimators` returns and reads
w_push through `_reweight`. It refuses to write unless every iteration fitted through the wrapper with exactly the
expected rows.

**The points (both sets, since packing makes them cheap; §5):**
- the data;
- the noise-free closure at the prior (F1.1's nominal closure, and rev 1's floor);
- the noise-free closure at NuWro's shape (rev 1);
- the noise-free closures at the A7 GiBUU hybrid and at the q3 tilt (F1.1's principal deformed truths, §2.5).

### 2.4 NC

`rsn_nc` is `rsn_unfold.py --regressor-weight none` on the data with the identity reweight. It must equal P5, and so
the frozen L-5D-PV_e_tune_v1, bitwise on the full grid and on the 16 cells (`build_cmodel5d.nominal_control`). It runs
alone first (J1). Without its PASS, J2 and J3 are not submitted, and the director decides any rerun of the frozen
products in the new environment. Every shift below is taken from rsn_nc.

### 2.5 WU and the deformed truths (fresh F1.1)

**The truths.** Both are F0b's two flagged truths, built by their own code:
- **the A7 GiBUU hybrid:** `s5p_truths.hypothesis_weight` with the committed `null-gibuu_cv-F.json` at amplitude 1;
- **the q3 tilt:** `s5c_pseudo.truth_weight("q3_given_eavail_w", amplitude 0.3)`.

`rsn_unfold.py --truth` replaces the identity reweight with them, for closures only.

**The closures.** They are pv-ladder's noise-free signal-only closures on the full MC (`pvl_lib.closure_inputs`), as at
the prior and at NuWro. They are not F0b's background-inclusive half-MC experiments. There is no frozen equal-weight
closure at these two truths, so WU runs the nominal regressor at both as WR's reference. T3's B0 and MW arms (after
LL5D) make the same comparison on FD-PRR's background-inclusive half-MC construction, with the same weight.

### 2.6 TR (fresh F1.2(ii)): a transfer test in simulation

**What is held out.** At every iteration, before the loop's own regressor fit, a seeded mask holds out 20 % of the
matched rows: the regressor's rows, the truth-passing, reco-passing MC events. The mask is
`numpy.random.default_rng([20261111, k]).random(n) < 0.2` for iteration k, fixed now.

**The probe.** A separate regressor of the same class and parameters is fitted on the other 80 %, with the step's own
sample weight, and predicts the held-out rows. Their known step-1 weight, the loop's own target for those rows, is
compared with the prediction:
- overall: the w_truth-weighted relative bias and RMS;
- per reporting cell: t_c = Σ w ŷ / Σ w y − 1;
- per decile of the fine truth cell's reconstruction acceptance (its w_truth share that is reconstructed).

**The points.** The data (TR_data), and the A7 GiBUU hybrid and q3 closures (WU's two steps).

**The control.** The probe is a separate object on read-only arrays, and the loop's fits, arrays and estimators are
untouched. TR_data must therefore equal rsn_nc bitwise, and the build refuses otherwise. WU's two closures carry the
same probe and have no bitwise reference of their own, so for them the guarantee is the same mechanism, shown on the
data by TR_data = rsn_nc.

### 2.7 Not declared: F1.2(i), and TR against the omitted quantities

**What F1.2(i) needs.** It widens the regressor's inputs with E_ν, the true vertex position and the leading-proton
kinetic energy. These must be per-event columns aligned to the MC rows of `of_inputs_5d.npz`.

**Why it is not declared.** The sample's writer, `nn_dump_inputs.py:89-103`, stores the five truth features (MCgen),
the five reconstructed features and the weights. It stores no other truth column and no event identity, so no column
can be joined to its rows afterwards.
Search: `nn_dump_inputs.py` np.savez_compressed keys; `pet/` and `g2_fullevent` inventories for E_nu, vertex and proton fields @ 8f99b7ff

**What would provide it.** A new dump of the event loop's trees with those branches, written in the same order as the
analysis sample and checked against it (`pass_truth`, `pass_reco` and `w_truth` byte-equal). That is a separate
production with its own declaration and price, not a cheap arm. The same input is what TR needs to bin its residual
against the omitted quantities, so TR here reads its residual against acceptance and the five features only.

## 3. Readings and outcome tables (fixed before any run)

The conclusions they bear on are P1–P8 in §3.4.

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
four held-out records still meet both criteria.

**Each arm's verdict:**
- "the fake-data conclusions survive V" if P1 is unchanged and P3 holds;
- otherwise "a fake-data conclusion changes under V", with the records named.

**What G6 can and cannot move, stated before the run.**
- **It cannot move** A7_gibuu or stage0c_gibuu. They are the only records graded without GiBUU's shift
  (fd_f0_regrade.TRUTHS: own = GiBUU), so neither grade can change (C-INV, which checks the grade, the model-only and
  the eight-cell grades, after checking bitwise that S^G6's GENIE+MEC and NuWro rows are the nominal ones).
- **Every other graded record can move.** These are the prior, W1–W3, q3, the NuWro closure, A7_mnvtune,
  A7_genie_cv, A7_genie_mec, A7_nuwro and the four held-out records. Each is graded against a matrix that includes
  GiBUU's row, which G6 changes in every region cell and which carries 0.890 of C_model's trace.
- **So L can lose q3 or gain members.** In the committed readout W3 is at p = 0.037 and A7_nuwro at p = 0.093. All five
  P1 classes are reachable under G6.

### 3.3 WR and WU: what is graded, against what and at which truths

**The references.**
- **The rounding floor:** φ_c = σ_J,c / x_c, from i0.json's data jitter spread over cmodel_5d.json's P5 integrals. It
  must reproduce the printed median 0.133 %, minimum 0.055 % and maximum 0.252 % (FD-1B-INV-I0-REPORT.md:67).
- **The reported σ_c:** from the F1 readout's C_total + C_resp + C_PL,5D.
- **The matrix M_T of each truth:** fd_f0_regrade's leave-out rule, M_T = C_e/(ff^T) + Σ_{j≠own(T)} s_j s_j^T +
  C_x/(ff^T), with own = GiBUU for the A7 GiBUU hybrid, NuWro for the NuWro closure, and none for the data, the prior
  and q3.
- **The covariance-weighted directions:** every vector v is resolved on M_T's eigen-directions. The whitened components
  a_i = e_i·v/√λ_i (largest three printed) satisfy Σ a_i² = v^T M_T^−1 v. The change is also resolved along the
  whitened equal-weight bias, the direction in which a failing truth fails.

**P6, the data.** P6 is δ_c = X_c(WR_data)/X_c(rsn_nc) − 1. Its χ² against M_data and its directions are printed.

| class | rule |
|---|---|
| W0, within the rounding floor | max_c \|δ_c\|/φ_c ≤ 2 |
| W1, above the floor and below half the reported σ | not W0, and max_c \|δ_c\|/σ_c ≤ 0.5 |
| W2, at least half the reported σ | some \|δ_c\|/σ_c > 0.5; the cells are named |

**P7, the closures.** Each bias is X/X_true − 1 on the 16 cells, weighted (WR) beside equal weights. The equal-weight
references are the frozen closure at the prior and at NuWro, and WU at the two deformed truths.
- **At the prior:** max |b^W| > 1e-4 flags "the weighted regressor breaks the prior's closure" (frozen: 3.2e-5).
- **At NuWro:** the RMS ratio RMS(b^W)/RMS(b^U) is "lower" below 0.9, "higher" above 1.1, and "comparable" otherwise.
- **At the A7 GiBUU hybrid and the q3 tilt:** both biases are graded noise-free (N = 0) against M_T. The weighting is
  **material** at T if either holds:
  - the noise-free flag differs between the two (any |z| > 2 or p < 0.01);
  - |χ²_W − χ²_U| > 0.25 χ²_U.

  Otherwise it is **immaterial**. Each closure's χ², flags, directions and the change along the equal-weight bias are
  printed.

**WR's verdict (F1.1), scoped to pvl's construction:**
- "in pvl's noise-free signal-only closures, the equal-weight regression is immaterial at the A7 GiBUU hybrid and the
  q3 tilt, and the data move within the rounding floor / below half the reported σ", if both deformed truths are
  immaterial and P6 is W0 or W1;
- otherwise "in pvl's noise-free signal-only closures, the equal-weight regression is material", naming the truths
  and, for W2, the data's cells.

**What the verdict licenses (the director's ruling on audit R2).** A "material" or "immaterial" WR is a stated
sensitivity of pvl's noise-free signal-only full-MC closure, WR against WU, graded alike.
- **It does not attribute F0b's flags** at A7_gibuu and q3. Those were made in the background-inclusive half-MC
  construction, with noise.
- **That attribution is T3's B0/MW reading:** FD-PRR's construction, at the same weight, after LL5D.
- **The estimator is not changed** here under any outcome.

### 3.4 Which paper conclusions each arm could change

| | conclusion | G6 | SM | WR, WU | TR |
|---|---|---|---|---|---|
| P1 | the fake-data bias exceeds the criteria at two truths (A7_gibuu, the q3 tilt) | yes: every record but A7_gibuu and stage0c_gibuu, so L can lose q3 or gain members (§3.2) | yes | no: a stated sensitivity in pvl's closure only; attribution is T3's MW (§3.3) | — |
| P2 | the other truths meet the criteria only with the broader terms, C_model among them | yes | yes | — | — |
| P3 | the four held-out records meet both criteria (R11 at G18 only with C_model) | yes | yes | — | — |
| P4 | C_model is dominated by the GiBUU shift (0.890) | yes | yes | — | — |
| P5 | the reported per-cell σ of the sixteen released cells | yes | yes | — | — |
| P6 | the sixteen released central values | — | — | yes | — |
| P7 | the noise-free closures at the prior, NuWro, the A7 GiBUU hybrid and the q3 tilt | — | — | yes | — |
| P8 | the misses' step-1 weights transfer from the reconstructed events at fixed truth (limitation 8) | — | — | — | yes |

**What no arm changes:**
- the 2D benchmark, whose comparison uses no C_model, and whose unfolding these arms do not refit;
- the prior-retention study;
- the rounding study;
- the 2D coverage results;
- LL5D's test, whose design and covariance are its own declaration's and are not regraded here;
- the Stage G generator χ² (S10, Tables S14–S15), which this design does not recompute.

**The paper's wording under each outcome** is a stated sensitivity, never an uncertainty added to the result. The 3.x
and F1 text that waits for these results must read correctly under every class above.

### 3.5 TR (P8): the transfer readings

TR is read at the last iteration, at each point (the data, the A7 GiBUU hybrid, the q3 tilt), on t_c. It is set
against the same φ_c and σ_c, conservatively: a held-out bias t on every miss would move a cell by at most t, since
the misses carry 15.7–68.1 % of a cell.

| class | rule |
|---|---|
| T0, transfers within twice the rounding floor | max_c \|t_c\| ≤ 2 φ_c |
| T1, within half the reported σ | not T0, and max_c \|t_c\| ≤ 0.5 σ_c |
| T2, at least half the reported σ | some \|t_c\| > 0.5 σ_c, or no held-out row in a cell; the cells are named |

The overall relative bias and RMS, and the relative bias in the lowest and highest acceptance deciles, are printed
beside the class as descriptions, with no threshold.

**What the classes bound.** t_c includes the 80 % probe's own estimation noise, and no noise reference is made. So
the classes bound the transfer bias plus that noise, and T0 (2φ, 0.1–0.5 %) may be out of reach from the noise alone.

**What TR can and cannot show.** A uniform random mask tests transfer among matched events at fixed truth. It cannot
show that misses resemble matched events in what the five features omit, which is what §2.7's input would test.

## 4. Seeds

| what | seeds and settings |
|---|---|
| every unfold | LightGBM random_state 42 for both classifiers and the regressor; the refinement classifier 45 (s5e candidate R); deterministic, force_row_wise, 32 threads, all-row binning, 5 iterations; the same as L-5D-PV |
| the data unfold | deterministic, so the training-seed block is zero |
| the closures | noise-free, so no pseudo-data draw |
| TR's mask | `default_rng([20261111, k])` at iteration k, fraction 0.2; the probe regressor takes the loop regressor's own parameters, random_state 42 among them |
| the regrade | re-reads the committed experiments at their recorded pseudo-seeds; it draws nothing |

## 5. Price

**The basis.** pv-ladder's `LEDGER.tsv` records two jobs on one exclusive node:
- **J5, 60206336:** 5 L-5D-PV unfolds in 811 s, 0.2253 node-h;
- **J1, 60202786:** 7 steps, the 5D NC among them, in 861 s, 0.2392 node-h. Its longest step took 13:45 and its
  MaxRSS was 16.5 GB or less.

The charge is per node-time, and a node holds at most 8 steps of 32 threads. `BINDING.md:15`'s "about 0.45 node-h" for
three unfolds is a projection made before any job.

**TR's added cost.** It adds one regressor fit per iteration to three steps. That is small beside the two classifier
fits, and it is inside each step's wall time.

| job | steps | projection | `--time` (1.25×) | maximum |
|---|---|---|---|---|
| J1 | rsn_nc alone | 15 min, 0.25 node-h | 0:19:00 | 0.32 |
| J2 | G6 (1), SM (3), WR data and two closures (3), TR_data (1): 8 steps | 17 min, 0.28 node-h | 0:22:00 | 0.37 |
| J2n (only instead of J2) | G6, WR (3), TR_data: 5 steps | 17 min, 0.28 node-h | 0:22:00 | 0.37 |
| J3 | WR and WU at the A7 GiBUU hybrid and the q3 tilt: 4 steps | 15 min, 0.25 node-h | 0:19:00 | 0.32 |

**Per arm,** sharing a job by step:

| arm | price |
|---|---|
| NC (J1, shared by all) | 0.25 node-h |
| G6 | 0.035 node-h |
| SM | 0.105 node-h |
| WR at the data, the prior and NuWro | 0.105 node-h |
| TR on the data | 0.035 node-h |
| F1.1 at the two deformed truths (J3: 2 WR and 2 WU, TR's two other points among them) | 0.25 node-h |

**The total.** It is projected at 0.78 node-h, with a hard maximum of 1.01 at the three time limits. **The cap is
raised to 1.25 CPU node-h,** inside the director's approval of about 2. The prep, the build, the regrade and the
readings run on a login node at 0 node-h.

**The stop rule.** The scheduler enforces the 1.25× limit. A stopped job is reported to the director and is not
resubmitted without the director's go.

## 6. Order and gates

1. **Audit and binding.** coverage-5b-audit rechecks rev 3, and the director binds the code digests of §7.
2. **Archive first, recommended.** The cluster lane archives the following to HPSS before connect 1, against their
   committed sha256s:
   - pv-ladder's `prep/` (22 MB) and `products/` (2.5 MB);
   - `cpl_block.npz`.

   Without the archive, the run must finish before 2026-12-19.
3. **Connect 1, login node.**
   - Clone at the pin.
   - Run `rsn_prep.py --ratios <pvl prep>/ratios/L-5D-PV --out <OUT>/prep`.
   - Commit its printed `rsn-prep-SHA256SUMS` and `prep.json` in a receipt PR (the new pin).
   - **NC-R gate (0 node-h, login node):** run `rsn_regrade.py --nominal-only` with cmodel_5d.json's S on the pinned
     F1 table, S1 and cpl block. It writes `<OUT>/nc_r.json` with `"verdict": "PASS"` only if all 22 records, control
     7 (its verdict, χ² and p) and the group and by-family counts reproduce the committed F1 readout. Commit it with
     the prep's receipt. **Every job refuses without it,** so a regrade mismatch is found before any node-hour.
   - Write `<OUT>/fence.txt`, after the director has announced the `rsn_` family to every fenced lane.
   - Submit J1.
4. **After J1.**
   - Run `rsn_cmodel.py nc` on a login node and commit its PASS.
   - Write `<OUT>/gates/J2.ok` (or J2n) and `J3.ok` naming the pin.
   - Submit J2 (or J2n) and J3.
5. **After J2 and J3, login node:**
   - `rsn_cmodel.py build`;
   - `rsn_regrade.py`;
   - `rsn_read.py`.
   The readouts are committed with the run's receipts.

**The launcher's refusals.** `sbatch_rsn.sh` refuses before any step if:
- the deploy is not clean at the pin;
- the job's name is not `rsn_<job>`;
- its TimeLimit exceeds the job's declared limit;
- a fenced prefix is queued or running;
- a reweight differs from its committed sha256;
- a product exists;
- `<OUT>/nc_r.json` records no NC-R PASS (every job);
- for J2, J2n or J3, the gate or the NC PASS is missing; for J2 or J2n, also the committed reweight list.

The inputs are read, not written.

## 7. Code

| file | sha256 |
|---|---|
| `nd-unfolding/rsn/rsn_prep.py` | `7b0fc567776d2016897173b1f8ab723fd99daedd34454537b36cd42bd03194be` |
| `nd-unfolding/rsn/rsn_unfold.py` | `5796bb6043a0ff646043206ef3ef623cbaf19d003875331da54a5642454e3690` |
| `nd-unfolding/rsn/rsn_cmodel.py` | `ab63292122bffbc30e5d85efc2a5ae3f96c7f917891a856c48e2d26414848a48` |
| `nd-unfolding/rsn/rsn_regrade.py` | `661608d81ccf7ca0ab08aee853f5934d4c0dab89677e82f8292239fee60b7652` |
| `nd-unfolding/rsn/rsn_read.py` | `4dd37197f6aa6c7f013b3ffea5558fd8d8fd1bc124047f761269adafce87e484` |
| `nd-unfolding/rsn/sbatch_rsn.sh` | `f889a0cf4de4a78aa7096bc01341ab6f3e6cdb41438267918519da7a527051d6` |
| `nd-unfolding/rsn/rsn_tasks.tsv` | `354bd16dd4d8b9dd5462f1daf6114e7beb467be3ab80e28b8ff212f51ea55616` |
| `nd-unfolding/rsn/test_rsn.py` | `887dbccd648e8648c03810e8d7ef335e09e5dfc7d97d4098c608db8de7bcaf29` |
| `nd-unfolding/rsn/rsn_mutation.py` | `8075fe8c9befed9184924fbab614ed81bf8c46bcfa112c7420a8c1a34d33f483` |

These files are used unchanged: `pvl_unfold.py` `59ab0e11…`, `pvl_lib.py` `f8a7d2c2…`, `omnifold_nn_core.py`
`24f87f11…`, `fd_f0_regrade.py` `0dfa722c…`, `build_cmodel5d.py` `aaa81575…`, `s5p_truths.py`, `s5c_pseudo.py`.

## 8. Tests and mutants

`test_rsn.py` is numpy-only. The estimators are stubs, and the products and records are synthetic; the committed
records the code pins are read from the checkout. To rev 1's coverage it adds:
- the regressor's weight equals w_push · w_truth at every iteration, with w_push recomputed from the loop's second
  classifier;
- the transfer diagnostic leaves the loop bitwise unchanged, with its mask, probe rows, weights and summary;
- the declared truths replace only the identity reweight in a closure, with the A7 hypothesis pinned;
- the closure references, TR_data's bitwise control and the transfer records;
- WR's matrices, eigen-components and failing-direction projection;
- the deformed-truth and transfer classes and WR's verdict;
- J3 and the per-job limits.

`rsn_mutation.py` plants 109 declared defects. Each must be killed by its named test. The receipts are in `rev3/`
(clean clone, serial, nice 19, one thread).

Rev 3 adds tests for the NC-R gate (nominal only, before J1), control 7's χ² and p, the by-family counts,
C-INV's full set and its row check, and every job's NC-R refusal: 52 tests in all.

## 9. CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the declared design, readings, outcome tables, seeds and price, before any run.
- **Not citable for:**
  - any result;
  - a calibrated uncertainty;
  - a change to C_model, to the estimator, to a grade or to a criterion;
  - attributing F0b's flags to the equal-weight regression (that is T3's MW reading);
  - the carbon-versus-CH difference;
  - F1.2(i), or TR against the omitted truth quantities (§2.7);
  - LL5D's coverage under a changed C_model;
  - the Stage G χ²;
  - any paper sentence.

## 10. Rev 2 changes (the director's request of 2026-11-11)

**New arms and readings:**
- **F1.1 (fresh major 1):** WR gains the A7 GiBUU hybrid and q3 closures, and WU their equal-weight references (§2.5).
  Rev 1's prior and NuWro closures are kept (both sets). Rev 2 adds P7's deformed-truth classes and WR's verdict,
  and the covariance-weighted directions F1.1 asks for (§3.3).
- **F1.2(ii):** TR, the transfer test, with its seed and fraction fixed (§2.6, §3.5).
- **F1.2(i):** not declared, for a missing input; what would provide it is stated (§2.7).

**Changes to rev 1:**
- **WR's weight** is now w_push · w_truth, T3's MW definition (rev 1: w_truth).
- **J2** gains TR_data (8 steps, limit 0:22:00), and **J3** is new.
- **The cap** is raised from 0.75 to 1.25 node-h (projected 0.78).
- **The HPSS recommendation** is added (§6).
- **Tests** grow from 41 to 50, and **mutants** from 70 to 101.

## 11. Rev 3 changes (the audit of rev 2 and the director's rulings, 2026-11-11)

**The two majors:**
- **R1:** under G6, every record graded with GiBUU's row can move, W3 (p = 0.037) and A7_nuwro (p = 0.093) among them,
  so L can gain members. Only A7_gibuu and stage0c_gibuu are invariant (§3.2, §3.4's P1 row).
- **R2:** WR's verdict is scoped to pvl's noise-free signal-only closure, as a stated sensitivity. Attributing F0b's
  flags stays with T3's B0/MW reading (§3.3, §3.4, §9).

**The minors:**
- **m4 (ruled):** NC-R runs on a login node before J1, at 0 node-h (`rsn_regrade.py --nominal-only`), and every job
  waits on its PASS (§6, the launcher).
- **m1:** NC-R also checks control 7's χ² and p, and each group's by-family counts.
- **m2:** C-INV checks the model-only and eight-cell grades too, after a bitwise check that S^G6's GENIE+MEC and NuWro
  rows are the nominal ones.
- **m3:** TR's classes are stated to bound the transfer bias plus the probe's estimation noise (§3.5).
- **m5:** WU's TR records rest on TR_data = rsn_nc for the mechanism (§2.6).

**The rest:**
- §2.3 states that w_push · w_truth supersedes rev 1's w_truth, and why.
- 52 tests and 109 mutants.
