# DECLARATION LL5D: the like-for-like 5D coverage test at G18 and AR23, read without and with GEANT_Neutron and GEANT_Proton (2026-11-08)

**By** the `cov2d` session, for `coverage-5b-audit` to audit and the director to bind. Nothing runs before both.

**Under:**
- [`DECISION-20261108-joseph-5d-coverage-and-parallel-studies.md`](../../../DECISION-20261108-joseph-5d-coverage-and-parallel-studies.md)
  (#934, merge `52334c34`), item 1, at `:31-36`:
  - the test is declared now, under the 2026-11-06 override of rule (iii);
  - it is read with and without GEANT_Neutron and GEANT_Proton, with **the reading without them primary**;
  - it is declared, priced, audited and bound before anything runs;
  - a campaign above half the group balance goes back to Joseph first;
  - branch `decl/1b-staged-a2-1-20261103` stays as it is.
- [`DECISION-20261106-joseph-plateau-next-work.md`](../../../DECISION-20261106-joseph-plateau-next-work.md), item 2,
  at `:49-52`. This is Joseph's override of 1B's rule (iii) (`DECISION-20261102-joseph-1b-redesign.md:78`), for "a
  declared coverage test built like-for-like".
- The director's brief of 2026-11-08, and the director's rulings on this draft (2026-11-08, by message), listed in §14.

**After:**
- Part 0, [`FD-1B-PRECHECK-ATTRIBUTION.md`](FD-1B-PRECHECK-ATTRIBUTION.md).
- Part 1, [`OUTCOME-20261108-1b-precheck-part1.md`](../../../OUTCOME-20261108-1b-precheck-part1.md) (#933), with its record
  `fd/receipts-1b/precheck-fd/p4/records/p4/readout.json` (sha256 `8e05ca9b…`, re-hashed for this draft).
- [`OUTCOME-20261106-1b-stage1-receipt-stop.md`](../../../OUTCOME-20261106-1b-stage1-receipt-stop.md): the §2b STOP.
- COV2D's design, [`COV2D-DECLARATION.md`](COV2D-DECLARATION.md): 300 pseudo-experiments per held-out tune, with the
  covariance rebuilt at each tune.
- 1B's staged design and its amendments, read from the campaign branch at `342c0ce5` without touching it.

Citations are at main `52334c34` unless another sha is given. "Part 1 `[path]`" is a key path in Part 1's
`readout.json`.

**MEASURES:** nothing.
- No job has run, and no connect has been made for this declaration.
- The drafter has not read the 1B receipt, its breakdown, or any of its inputs for this design. §3.4's denominator rule
  rests on design records only, all dated before the stage-1 stop (the director's ruling D).
- The drafter has computed no κ, F factor, composite or clipped mass.

**CANNOT AUTHORIZE:**
- any job before the director's binding 1 (this declaration) and binding 2 (amendment A1's code, §12);
- any change to the reported covariance, an interval, the estimator, a claim, or the paper or note text;
- a study of the truth dependence (item (c), excluded);
- any diagnosis or repair of GEANT_Neutron or GEANT_Proton. limitation-resolver diagnoses them under its own
  declaration, which cannot change this test's primary reading (decision item 2).

**CITABLE FOR:**
- the design, the readings and the rules here, all fixed before any draw;
- the per-group like-for-like construction and its grounds in Part 0 and Part 1 (§2);
- the denominator rule and its design grounds (§3.4);
- the mapping of Joseph's earlier 1B rules onto this test (§8).

**NOT CITABLE FOR:**
- **any coverage statement, in either direction,** about the 5D intervals, the reported covariance, or the procedure;
- that the like-for-like construction holds at G18 or AR23. Rule K was read at the nominal truth only (Part 1;
  limitation-resolver's answer Q5);
- the cause of the GEANT_Neutron or GEANT_Proton departure, or any repair of it;
- the truth dependence (item (c)), or which truth the intervals should use;
- the coverage of any ENS1 estimator (the director's ruling 5);
- a coverage rate, the lateral block, C_resp, C_PL,5D, or the response model;
- any wording for the paper or the note.

**The job-name family is `ll5d_*`** (§9): `ll5d_calib`, `ll5d_gate_G18`, `ll5d_gate_AR23`, `ll5d_pilot` and
`ll5d_bulk_01` to `ll5d_bulk_10`. The family is new. The director tells every fenced lane before any go.

**PENDING-JOSEPH:**
- **The analogue of rule (iii) for this test** (§8, row R3). Until Joseph rules, the default is fail-closed: any
  STOP or INVALID goes to the director and to Joseph unrepaired, and nothing relaunches.

## 1. What is tested, and what is fixed

- **The test.** At each of two GENIE v3 tunes held out of the analysis, natures are drawn about the tune's truth under
  the systematic model. Each nature's pseudo-dataset is unfolded once by the reported procedure with the nominal
  simulation. The procedure's covariance, rebuilt at that truth by `s1_assemble.py`'s procedure, is graded against the
  errors. This is COV2D's design on S1's 5D bank, with every group built like-for-like (§2).
- **The estimator** is configuration (e), the reported procedure (`OUTCOME-20261105-fd-stab-none-pass.md`: "1B stage 1
  launches on configuration (e) as planned"). The test does not wait for ENS1.
  - If Joseph adopts an ENS1 estimator, this test is re-pinned by an amendment, priced then, which must not reuse
    configuration (e)'s bulk products (the director's ruling 5).
- **Not under revision:** the reported covariance (S1's blocks, C_model, C_resp, C_PL,5D), the estimator and every
  reported number. No outcome inflates, replaces or re-weights a block.
- **Grading is per tune and per reading.** With two truths there is no coverage rate.
- **Two readings, both fixed now** (decision item 1):
  - **Primary, `minus2`:** natures that never draw GEANT_Neutron or GEANT_Proton, graded against C_T without those
    two bands' blocks;
  - **Beside it, `all`:** natures drawing every band, graded against the full C_T.
- **The two readings are paired.** They share toy seeds, draw streams and Poisson streams (§3.6), so they are
  correlated. **Neither reading is a test of the other** (the director's ruling 2).

## 2. Like-for-like, group by group

**What "like-for-like" means here.** Part 0 and Part 1 locate gate D's mismatch in comparisons of unlike objects. They
do not locate it in the toys failing to realize what they draw.
- **The rule-S harness check** reproduces in all three drawn groups (Part 1 CITABLE FOR, `OUTCOME-20261108-1b-precheck-part1.md:51-53`).
- **The departures** sit in the factors that compare different objects:
  - F_side = √(B/A): the toys' factors on the simulation side against S1's whole universe at the same truth;
  - F_truth = √(A/M): S1's whole universe at the nominal truth against S1 at the data.
- **The construction that removes both comparisons** is mode D's object, which rule K gates:
  - the nature is the whole universe, with no factor applied to a CV nature;
  - the error is taken against that nature's own truth;
  - the reference block is S1's mechanism rebuilt at the same truth as the nature, not M at the data.
  - Rule K, κ = √(Dnom / A_unc), checks exactly this object at the nominal truth
    (`FD-1B-PRECHECK-FD-DECLARATION.md` §2 table and §4.4; `FD-1B-MODED-DECLARATION.md:45-62`).

| group | what Part 0 / Part 1 found | the like-for-like construction here | its check at the nominal truth |
|---|---|---|---|
| **interaction** (33 bands, 67 universes) | the departure is B against A (I2's "F_prior", renamed F_side), dominant in 14 of 15 cells; F_truth under in 15 of 16 (Part 0 `:66`, `:177-180`) | nature = the universe's full arrays (truth weights, reco weights, denominator, background), not the truth-preserving factor g_f (mode D, `FD-1B-MODED-DECLARATION.md:47-57`) | rule K **PASS**, κ 0.9757–1.0570 in 16 of 16 cells (Part 0 `:68`, `:149-175`; `FD-1B-STAGED-STAGE0-REPORT.md:12`) |
| **flux** (1 band, 100 weighted universes) | **F_side the account**, in 7 of 9 attributed cells (Part 1 `[groups/flux/rule_F/level/F_side]` = "account"; outcome `:36`) | nature = the universe's full arrays **and its flux Φ_u** in the truth. Unfolding uses Φ_CV (Part 1 §2.1, `FD-1B-PRECHECK-FD-DECLARATION.md:83-93`) | rule K **PASS**, 16 of 16 resolved (`[groups/flux/rule_K/verdict]`; κ 0.9838–1.0016 in `[groups/flux/factors/kappa]`) |
| **detector** (4 bands, 8 universes) | **F_truth the account**, in R03, R05 and R06 (`[groups/detector/rule_F/level/F_truth]` = "account"; outcome `:37`) | nature = the dump's full arrays (wt, wr, bkgw; denominator = the CV's, §3.4), graded against the block **rebuilt at the nature's truth** (§4), never against M at the data | rule K **PASS** for the group (`[groups/detector/rule_K/verdict]`; κ 0.9898–1.0183), and for GEANT_Pion and MinosEfficiency |
| **GEANT_Neutron, GEANT_Proton** | rule S DEPARTS and rule K **FAIL**, in 6 and 4 cells (`[bands/GEANT_Neutron/rule_K/cells_outside]` = R00 R02 R08 R09 R10 R11; `[bands/GEANT_Proton/rule_K/cells_outside]` = R01 R05 R07 R08; outcome `:41-42`) | **excluded from the primary reading** on both sides; drawn in the `all` reading | none: rule K fails, so this is why the primary excludes them |

**What rule K licenses, and what it does not.**
- Part 1 licenses "full-universe pseudo-data reproduce S1's universe block for band b at the nominal truth" (outcome
  `:54-55`).
- It licenses nothing at G18 or AR23. Rule K is read at r = 1, where unf = ofin, so a detector universe's truth
  weights cancel out of its truth. At r ≠ 1 they do not (limitation-resolver's answer Q2, my reading of
  `s5n_pseudo.py:170-186`).
- No cross-band or composition term was measured: Part 1 drew each band alone (limitation-resolver's answer Q4).
- So this test does not assume κ ≈ 1 at the tunes. A departure there enters the test's own errors, and the report
  cannot separate it from a covariance failure (§13).

**Not drawn, and so not like-for-like by construction:**
- the lateral block, carried at each truth (§3.8);
- the normalization surrogate;
- C_model, C_resp and C_PL,5D.

The laterals and the normalization carry 29.0 % of the original toys' covariance trace (`gate-d.json:6`; Part 0 `:194-195`).

## 3. The design

### 3.1 The truths

| truth | definition | pin |
|---|---|---|
| **G18** | G18_10a_02_11b: F1's gated, k-normalised bridged ratio, applied by `s5n_pseudo.truth_weight("ratio_nd", …, 1.0, ratio)`, as `fd_1b_toys.truth_ratio` and `truth_model` apply it | the committed `f1-prep-SHA256SUMS` digest, checked by `fd_1b_toys.truth_ratio` |
| **AR23** | AR23_20i_00_000, the same | the same |

- **No plug-in truth** (the director's ruling 1). `FD-1B-STAGED-BINDING-3.md:52` @ `342c0ce5` defers it to Joseph's
  publication-scope decision (OI-205). Adding it later needs its own amendment and price.
- **r_T > 0 on every row** is a control (§10). Clipping before or after applying r_T is then the same.
- **"Held out" is not "independent".** G18's Valencia 2p2h shares the GENIE + MEC shift's family, and AR23 shares G18's
  Nieves quasielastic model (1B's staged declaration §3). §7 reports the leave-out-MEC variant.

### 3.2 The natures: every drawn group

One toy is one nature. It is drawn by `fd_1b_toys.draw_for_seed(seed, flux_p, groups)`, unchanged, then unfolded once.

| group | the nature drawn | its block in C_T |
|---|---|---|
| **flux** | one of the 100 universes, with probability w_u / Σw (`s1_assemble.flux_weights`) | the constraint-weighted `mat_cov` |
| **interaction** | each of the 33 bands at one of its universes: a pair band at either endpoint with probability ½, 2p2h at one of 3 | `mat_cov` per band, unweighted |
| **detector** | each of the 4 bands at either universe with probability ½, from the detector dump (wt, wr, bkgw; denominator §3.4) | `mat_cov` per band |
| **lateral** | the surrogate: x̂ += Σ_b s_b Δ_b(T)/2, s_b = ±1, with Δ_b(T) carried (§3.8) | ¼ Δ_b(T) Δ_b(T)ᵀ, X01 for Muon_Energy_MINOS |
| **normalization** | x̂ × (1 + 0.014 z), z ~ N(0, 1) | (0.014 x̂_T)(0.014 x̂_T)ᵀ |
| **statistical** | Poisson pseudo-data at data size at λ⁺ on every reco-passing signal row and every background row, plus set A's MC and template Poisson(1) streams at the toy's seed (`fd_1b_toys.mc_template_streams`) | set A's bootstrap at one realization of T (§4) |
| **seed** | not drawn: estimator seed 42 for every unfold | not rebuilt; checked (§4) |

**Loading.** Every drawn universe's arrays are loaded exactly as S1's universe unfolds and κ load them:
- `s5p_universe.weights(bank, tag, nonfinite="zero")`, or the detector dump for the detector bands;
- then `s5p_universe.universe_inputs`. Non-finite weights are zeroed, and negative weights are kept until §3.4's
  clip.

**The `minus2` reading draws the same way.** The draw is made with every band, and then GEANT_Neutron's and
GEANT_Proton's universes are dropped from the composition. So both readings consume identical random streams, and
every other band takes the same universe in both.

### 3.3 Composition: first order, per row

For a draw D = (u₁, …, u_k) in `draw_for_seed`'s order (the flux universe first, then the interaction bands sorted,
then the detector bands), each per-row array a composes as

  a_D = a_{u₁} + Σ_{j≥2} (a_{u_j} − a_ref), accumulated in draw order,

for a ∈ {wt, wr, bkgw, tdw}.
- **For wt, wr and bkgw,** a_ref is the CV's array. These are `DECISION-20261102-joseph-1b-redesign.md` item 1's rule
  and amendment 2's.
- **For tdw,** a_ref is the per-row reference of §3.4.
- **For k = 1,** a_D = a_{u₁} bitwise.
- **The flux in the truth** is the one flux universe's Φ_u (`s5p_universe.py:115-122`). The unfolding MC's flux is
  Φ_CV (§3.5).

### 3.4 The denominator: composed per row, clipped per row, then histogrammed (task item 2; the director's ruling D)

**The rule.**
1. **Compose per row.** tdw_D = tdw_{u₁} + Σ_{j≥2} (tdw_{u_j} − tdw_ref), over the truth-denominator rows.
   - tdw_ref is the bank's GEANT tdw, which S1's own denominator control already uses as the CV-equal per-row truth
     weight (`s1_controls.py:14`, `:131-132`).
   - A detector universe carries a `denom_nd` histogram, not per-row tdw (`s5p_universe.py:83-86`). It enters with
     zero departure. This requires its `denom_nd` to equal the CV's bitwise, which Part 1 recorded for all 8 detector
     universes (`[descriptive/detector_dump_equals_cv/<u>/denom_equals_cv]` = true). The control re-checks it and
     refuses otherwise (§10).
2. **Clip per row.** tdw_D⁺ = max(tdw_D, 0), and wt_D⁺ = max(wt_D, 0) on the truth-passing rows. Each tree is clipped
   on its own composite, row by row.
3. **Histogram.** The nature's denominator is `s5p_universe.denominator(bank_cv, tdw_D⁺, edges)`, the function
   `universe_inputs` uses for a single bank universe.

**So every fine-cell denominator is ≥ 0 by construction.** It is a sum of non-negative terms. It is 0 only where
every row in that fine cell clips, or where the cell is empty.

**The truth** is the procedure's own `s5n_pseudo.true_xsec`, on the nature's clipped arrays, with r_T and Φ_u:
- unf = hist(wt_D⁺ · r_T), ofin = hist(wt_D⁺);
- completeness = ofin / dn_D⁺ where dn_D⁺ > 0;
- the extraction's own mask sets T = 0 in a fine cell whose completeness denominator is not > 0
  (`xsec_nd.py:79-82`). That is the convention every CV and universe product already uses for an empty cell.

**The grounds.** All are design records dated before the stage-1 stop of 2026-11-06. None reads the 1B receipt or its
inputs.
- **Joseph's clip rule for both coverage tests** (`DECISION-20261103-joseph-coverage-clip-rule.md`, items 1–2, and
  the director's clarification at `:84-94`): "each tree is clipped on its own composite, row by row", and the graded
  truth is max(composite truth weight, 0). The denominator rows are the 5D truth's own tree: at r = 1 the truth is
  T = dn / (Φ·N·POT·vol) (limitation-resolver's answer Q2). So the rule applies to them row by row.
- **Why 1B composed the denominator per cell instead.** Amendment 1 §4.2(i) @ `342c0ce5` (`FD-1B-STAGED-AMENDMENT-1.md:195-200`)
  gives the reason that `cv.npz` holds no CV per-row tdw, so a per-row ratio could not be formed. That was the only
  reason given. S1's control shows that a CV-equal per-row tdw exists in the bank (above). So the reason no longer
  binds.
- **The clip-rule machinery already composes tdw per row.** A2.1's c2check works row by row on 32,849,103 tdw rows
  (`FD-1B-STAGED-ADDENDUM-A2-1.md` §8c @ `342c0ce5`), against its own per-row CV array (`cvdenom-run`). Amendment A1
  either uses tdw_ref throughout, or shows that array equal to tdw_ref bitwise (§12).
- **COV2D's bound truth is the same rule in 2D.** The graded truth is the clipped composite truth weight per
  `mc_truth_denom` row, with the CV completeness ≡ 1 (`COV2D-DECLARATION.md:154-169`).

**Fail-closed, at the receipt (§5.1), before any unfold.** A reporting cell whose truth U·T_D is ≤ 0 or non-finite
in any declared draw of either reading is a **STOP**. By construction it can fire only if every row of that
reporting cell clips.

**Recorded, not gated, per toy and per declared draw:**
- the fine cells with dn_D⁺ = 0 < dn_CV, and those with ofin_D⁺ = 0 < ofin_CV;
- the clipped tdw mass and the clipped wt mass, per truth cell and U-mapped to the 16 reporting cells.

### 3.5 The pseudo-data and the unfold

- **The Poisson mean** on a reco-passing signal row is λ = wr_D × r_T, and on a background row λ = bkgw_D.
  λ⁺ = max(λ, 0) row by row (Joseph's clip rule, item 1).
- **The experiment** is `fd_1b_toys.build_full`'s, with these arrays and its Poisson stream. The unfolding MC is the
  nominal simulation, with its weights, denominator, template and flux Φ_CV, by `fd_1b_precheck_fd.with_mc`
  (`UNFOLD_MC_KEYS` = `fd_1b_inv.MC_KEYS` + flux, `fd_1b_precheck_fd.py:68`, `:140`), exactly as Dnom does (`:149-152`).
- **The unfold** is S1's estimator, `toys.CONFIG`, `toys.ITERS` and estimator seed 42.
- **The error** is e = U x̂ − U T_D on the 16 reporting cells, after the lateral and normalization surrogates.

### 3.6 Seeds

| what | G18 | AR23 |
|---|---|---|
| toys (both readings, shared) | 4,751,000–4,751,299 | 4,761,000–4,761,299 |
| the gate sample (§5.2), whose first 300 are the toys' draws (11-04 item 1) | 4,751,000 to 4,751,000 + N − 1 | 4,761,000 to 4,761,000 + N − 1 |
| the realization d̃_T for the stat block (§4) | 4,770,100 | 4,770,200 |
| the grading null, `minus2` / `all` | 4,770,310 / 4,770,320 | 4,770,410 / 4,770,420 |
| the gate calibration's null replicates | from 4,770,500 | from 4,770,600 |

- **N ≤ 9,000**, so the two gate samples cannot overlap. The amendment fixes N by 11-04 item 3's power requirement.
- **Draw, Poisson and salt streams** are `fd_1b_toys`' (`default_rng([seed, DRAW_SALT])`, and the Poisson stream at
  `[seed, PSEUDO_SALT]`).
- **No collision.** A search of every tracked `.py`, `.sh`, `.tsv`, `.json`, `.md` and `.txt` file for an integer
  token in 4,751,000–4,770,999 found none. The only hits were float literals in data records.
  - Search: `git grep -I -n -P '(?<![0-9A-Za-z.,])(47[5-7][0-9]{4}|4,7[5-7][0-9],[0-9]{3})(?![0-9A-Za-z]|,[0-9])' -- '*.py' '*.sh' '*.tsv' '*.json' '*.md' '*.txt'` @ `1ad13b76`, filtered to 4,751,000–4,770,999: 11 hits, all float literals (`sum_lambda`, `pz`, `px`, `sum_of_squares`).
  - The amendment's code repeats the check at its own sha.

### 3.7 Not drawn

- **C_model:** a fixed-truth draw cannot produce it. It is what should cover each tune's departure.
- **C_resp:** the nominal-response scope.
- **C_PL,5D:** it is built from the data's run-period groups.

### 3.8 The lateral block, carried

The 5D lateral dumps no longer exist (`FD-1B-DECLARATION.md:99`). So:
- at T, S1's lateral blocks are transferred in relative form, Δ_b(T) = Δ_b ∘ (x̂_T / f), and C_lat,b(T) = ¼ Δ_b(T) Δ_b(T)ᵀ;
- the surrogate draws the same Δ_b(T);
- the lateral block is carried at each truth, not tested. Its share of S1's C_total trace is 0.1406
  (`FD-1B-DECLARATION.md:99`).

## 4. The covariance rebuilt at each truth

**The reported procedure** is `s1_assemble.py` (blob `b157250a…`, last changed at `fe5d79c6`):
- C_e = C_stat + Σ_b C_b + C_lat + C_norm + C_seed (`:320-353`);
- C_total = C_e + C_model_abs.

**At truth T, the data are replaced by d_T,** T's pseudo-data at their means (nominal response, every Poisson draw
at its mean). Each block is rebuilt as S1 built it from the data.

| block at T | how | unfolds per truth |
|---|---|---:|
| central x̂_T | d_T unfolded with the nominal MC | 1 |
| flux | d_T with each Flux universe's MC and Φ_u (`universe_inputs`), constraint-weighted `mat_cov` | 100 |
| interaction | d_T with each interaction universe's MC, `mat_cov` per band. This is I2's mode A at T | 67 |
| detector | d_T with each of the 8 detector universes' MC, `mat_cov` per band | 8 |
| stat | set A's procedure on one Poisson realization d̃_T (§3.6): replicas b = 1–50 by `s5n_pseudo.bootstrap_replica`, the refinement refit per replica, sample covariance with ddof 1 | 50 |
| seed | not rebuilt. One check per truth: x̂_T at estimator seed 45 equals seed 42 bitwise, or INVALID | 1 |
| normalization | (0.014 x̂_T)(0.014 x̂_T)ᵀ | 0 |
| C_model_abs | diag(x̂_T) C_model,5D diag(x̂_T), with the pinned fractional C_model,5D (`s1_assemble.py:355-360`) | 0 |
| lateral | carried (§3.8) | 0 |

That is **227 unfolds per truth.** Both readings share them.

**The graded matrices:**
- `all`: C_T = C_e(T) + C_model_abs(T);
- `minus2`: C_T⁽⁻²⁾, the same sum with `band:GEANT_Neutron` and `band:GEANT_Proton` left out.

**Why the removal is exact.**
- Each band's block is its own `mat_cov` over that band's universes (`s1_assemble.py:329` @ `52334c34`, blob
  `b157250a…`).
- C_e is their plain sum (`:353`), with no cross-band term.
- So C_T⁽⁻²⁾ is built as a rebuild with those two bands excluded. The control requires it to equal
  C_T − C_GEANT_Neutron − C_GEANT_Proton to 10⁻¹² of max |C_T| elementwise. It cannot be bitwise, because the sum's
  order differs (the director's ruling 2).

**What a result carries over to, and what it does not.**
- Both readings leave C_resp and C_PL,5D out, since neither is drawn. Both are positive semi-definite. So a cell that
  covers under C_T also covers under C_T + C_resp(T) + C_PL,5D(T), the procedure's full covariance at T.
- The χ² region carries over only if both matrices have ndf = 16.
- **Nothing here relates C_T to the matrix made at the data.**
- An under-coverage under C_T is not shown to persist under the full covariance at T.
- d_T at its means is the procedure's expected block at T. A block rebuilt per toy is not priced, and the report
  says so.

## 5. Before the bulk: the receipt, the clipping gate and clipcheck

### 5.1 The receipt (inside the gate jobs, §9)

This is run exactly in float64, in compose's order, over every declared draw of both readings at both truths: 2 × 2
× 300 natures. The director's §2d (ii) on 1B is carried.

**STOP if either fires:**
- **N1:** any per-row composite above 10 × the largest single-universe magnitude on that row (amendment 2's bound,
  carried);
- **T ≤ 0:** any reporting cell's U·T_D ≤ 0 or non-finite (§3.4).

**Recorded:** §3.4's counts and masses, N1's maxima, and the clipped fractions |Σλ⁻| / Σλ for signal and background.

**The denominator controls, REQUIRED** (the director's ruling D):
- **(D1)** the 8 GEANT tdw arrays are bitwise equal to each other, so tdw_ref is well defined;
- **(D2)** hist(tdw_ref) on the bank's coordinates matches the CV `denom_nd` with the same support, total within
  10⁻⁹, and every cell within 10⁻³ (S1's tolerances, `s1_controls.py:14-18`);
- **(D3)** each detector dump's `denom_nd` equals the CV's bitwise.

A failed control is INVALID, reported unrepaired.

**Why it is not on a login node.** The per-row composites need about 270 GiB: A2.1's c2check probe peaked at 269 GiB
over the same 175 × 32,849,103 tdw rows (`FD-1B-STAGED-ADDENDUM-A2-1.md` §8c). So the receipt runs at the start of
each gate job, before the gate's blocks, at no extra item. This corrects my message to the director, which said
"0-node-h".

### 5.2 The clipping gate (Joseph's 11-03 clip rule and gates, with 11-04's large sample)

**C2's fixed reading** (`fd/receipts-cov2d/clip/c2_reading.txt`, sha256 `b5b4fc4b…`) is applied unchanged as a hard
stop. Its variance part is replaced by Joseph's 16-cell gate. Its R_c rules and row-match bound are unchanged
(`DECISION-20261103-joseph-1b-variance-gate.md` item 3).

**The 16-cell variance gate, per evaluation.** The clipped-composition variance ratios r_c (C2's definition) are
evaluated on the gate sample of N draws from the same code, configuration and clip rule as the 300 declared draws.
The gate passes if all hold:
- (i) at most 2 of 16 cells have |r_c − 1| > 0.20;
- (ii) |mean log r_c| ≤ t_ii;
- (iii) max |r_c − 1| ≤ t_iii;
- t_ii and t_iii are recalibrated by null simulation at N, before any 5D draw is examined, on the correlated null
  including the reference variance's noise (11-04 item 2).

**The population: the director's mapping of Joseph's 11-03 and 11-04 rules onto this population**, which Joseph may
override (the director's ruling 3):
- **four evaluations:** {G18, AR23} × {`minus2`, `all`};
- the joint noise-only false-stop budget is **1 % over the four**;
- materiality per evaluation: at least 80 % power against a uniform 8 % variance deflation. If N cannot reach it at
  N ≤ 9,000, that is a REPRICE to the director;
- (i) keeps ±0.20 with k = 2, unless the null at N shows that (i) alone exceeds the budget. In that case it goes to
  Joseph (11-04 item 2).

**First, the large-N unclipped null** (11-04 item 4). At N, under the unclipped first-order law, the per-cell mean
ratio is 1 within its measured SE: the law control at z = 4, and the linearisation tolerance 0.02. If it fails,
nothing proceeds, and it goes to the director.

**The backstop** (11-04 item 5). On the 300 declared draws, (iii) at 4.3 SD per cell by rule (α), and (i) at k = 2,
as a loose check. A config hash shared by the gate sample and the toys is logged.

**A failed gate, at either reading or either tune, means nothing launches,** and the test returns to Joseph (11-03
variance gate, item 3).

### 5.3 clipcheck: the clipping offset up front (the 11-02 redesign's addition (ii), per row)

- **The clipmean,** per truth and per reading: one unfold of d_T plus the mean over the 300 declared draws of each
  row's |λ⁻|. That is the response to the clipped data mass around d_T.
- **The truth side,** at no unfold: τ_c is the mean over the 300 draws of U·(T_D(clipped) − T_D(unclipped tdw and wt,
  with T kept only where the unclipped denominator is > 0)), over σ_c.
- **The offset:** o_c = U(x̂_clipmean − x̂_T)_c / σ_c − τ_c. Its sign is the error's, e = x̂ − T.
- **σ_c's proxy before the bulk** is S1's reported σ at the data (`fd_1b_score.reported_matrix`), as amendment 2 §5b
  used it. The final readout recomputes o_c with C_T.
- **The rule, fixed now.** If any cell at any (truth, reading) has |o_c| ≥ δ* = 0.667, the verdict is `TO_JOSEPH`,
  and the case goes to Joseph before any bulk. Otherwise the verdict is `PROCEED`.
  - δ* is the offset that lowers a unit Gaussian's ±1σ content by §6's per-cell resolution, 0.10
    (amendment 2 §5).

## 6. Grading, fixed before any number is read

**One implementation:** `nd-unfolding/fd_1b_null.py`, imported unchanged, on the 16 reporting cells, per (truth,
reading).

**The statistics,** as 1B's staged §5.1:
- p̂_c against the draw-matched null p_c(T);
- χ² on C_T's non-null subspace (eigenvalues above 10⁻¹² of the largest);
- q̂ against q(T);
- pulls;
- the bias-versus-width attribution of every flagged cell (`fd_1b_null.attribute`);
- mean χ²/ndf;
- s_c.

**The Cholesky reading rule** (COV2D-BINDING-2's A5 M line, ruling 3, carried to 16 cells). For every grade with ndf
= 16, the score record must show a finite κ₂, a finite tol and a finite max_rel_diff ≤ tol. Otherwise that (truth,
reading) is INVALID and goes to the director unrepaired.

**The null.** `fd_1b_null.null_contents` runs at each (truth, reading) after its blocks exist and before any toy error
is read.
- **The laws:** the drawn bands' centred discrete laws at T, from that reading's bands only, plus one Gaussian for
  stat, normalization and C_model_abs(T).
- **The match:** `check_matched` at 10⁻¹² against that reading's C_T.
- **The size of the simulation:** 2,000,000 error vectors at §3.6's seeds.

| reading | condition |
|---|---|
| **cell c under-covers** | #{\|e_tc\| ≤ σ_c} ≤ k_c(T), the largest k with P(Bin(300, p_c(T)) ≤ k) < 0.025/16 |
| **joint under-coverage** | #{χ²_t in region} ≤ k_J(T), the largest k with P(Bin(300, q(T)) ≤ k) < 0.025 |
| **COVERS at (T, reading)** | no cell under-covers, and no joint under-coverage |
| **UNDER-COVERS at (T, reading)** | otherwise; each cell is named, with whether the joint fraction is under too |
| **INVALID at (T, reading)** | any §10 control fails for it, or the Cholesky reading rule fails. Reported unrepaired |

- **The rule is one-sided.** Over-coverage is reported, but it is not a failure.
- **The weakened pass:** a pass in a cell whose clipped variance ratio is below 0.9 counts as weakened (the director's
  ruling recorded in the 11-03 clip rule, item 4).
- **The flagged cell and the clipping offset:** a flagged cell with |o_c| ≥ 0.667 under C_T is read "the flag may be
  the clipping artefact". That reading cannot un-flag a cell.
- **Size,** per (truth, reading): at most 0.05 by the union bound (0.025 over the cells, 0.025 joint). Over the two
  tunes within one reading, at most 0.10.
  - The two readings are correlated by construction, so no size across readings is stated, and none is needed: the
    primary reading is `minus2`.
- **Resolution,** for orientation from 1B's staged `arith.out`: about 0.10 in content per cell and 0.08 jointly.

## 7. Descriptive readouts, no verdict

Each is produced per (truth, reading):
- the spread alone, against C_e(T) without C_model;
- the toys' mean error against σ_c (the bias);
- the predicted offset of the un-centred draws, −Σ_b Σ_u p_u (U x̂_u(T) − U x̂_T), at no unfold;
- the leave-out-MEC variant C_T⁻, with 1B staged §5.4's reading, which changes no verdict;
- the clipping record: o_c in every cell, the clipped fractions, and the clipped mass per reco cell and per truth cell
  for every toy. The latter is the 11-02 addition (ii) in per-row form (the director's ruling D);
- the cross terms (the 11-02 addition (i)): each cell's reco-weighted histogram under product against additive
  composition, over the declared draws, in σ_c. It is computed in the gate jobs;
- the realization check and the truth's clipped-mass record (§3.4);
- **between the readings,** per cell, p̂_c(`all`) − p̂_c(`minus2`) and the two pull means. These describe; neither
  reading tests the other.

## 8. Earlier rules on 1B, mapped onto this test (task item 3)

| | rule | source | here |
|---|---|---|---|
| R1 | first-order composition, in draw order, k = 1 bitwise | `DECISION-20261102-joseph-1b-redesign.md` item 1 | **carries**, with the denominator per row (§3.3–§3.4, the director's ruling D) |
| R2a | addition (i): cross terms, descriptive | same, item 2 (i) | **carries** (§7) |
| R2b | addition (ii): clipped mass per reco and truth cell per toy, the offset from one mean unfold per truth, and its reading fixed before any number | same, item 2 (ii) | **carries**, per row, per reading, with the truth side added (§5.3, §6) |
| R3 | a second STOP ends stage 1 unless Joseph rules otherwise | same, item 2 (iii), `:78` | **overridden by Joseph for 1B** (2026-11-06 item 2). **Whether this test carries its own STOP limit is PENDING-JOSEPH.** Until then: fail-closed, any STOP or INVALID to the director and Joseph unrepaired, and nothing relaunches |
| R4 | negative counts: option (a), λ⁺ in the pseudo-data only | same, item 3 | **superseded** by the 11-03 clip rule (R7) |
| R5 | the wording: one neutral methods sentence, no "does not test" clause, the required facts as description, clipping, the ±1σ draws, shared universes and cross terms to the note; the paper lane drafts, a PRD-referee read follows, and Joseph reads | same, item 4 | **carries**. **New and Joseph's:** how, or whether, the paper describes the two readings and the exclusion of two bands, and the note's text on the denominator clip (§13) |
| R6 | the director's §2d (ii), an exact float64 pass; §2b, a non-positive denominator fails closed | same, item 5 | §2d (ii) **carries** (§5.1). §2b is **replaced by construction** (§3.4), and a non-positive *reporting-cell* truth STOPs (§5.1), as the director accepted |
| R7 | consistent clipping, each tree on its own composite, row by row; 1B gated on C2's fixed reading as a hard stop; the weakened-pass reading | `DECISION-20261103-joseph-coverage-clip-rule.md` items 1–4 and clarification | **carries**, and is the ground of §3.4. The gate is §5.2 |
| R8 | the 16-cell variance gate (i)–(iii), calibration first, 1 % over three truths | `DECISION-20261103-joseph-1b-variance-gate.md` | **carries**, on 16 cells. The 1 % is over four evaluations: **the director's mapping, which Joseph may override** (§5.2) |
| R9 | the large-sample gate: N ≈ 3,000, 1 %, 80 % power at an 8 % deflation, the unclipped null first, the backstop, and the plug-in calibrated after B4 | `DECISION-20261104-joseph-1b-large-sample-gate.md` items 1–7 | items 1–5 and 7 **carry**, per evaluation. Item 6 (the plug-in) **does not apply**: no plug-in truth (the director's ruling 1) |
| R10 | stage 1 waits for the B4 stabilisation probe | 11-03 clip rule, item 3 | **discharged**: NONE_PASS, configuration (e) (`OUTCOME-20261105-fd-stab-none-pass.md`) |
| R11 | a campaign above half the group balance goes to Joseph first | plateau decision item 2; DECISION-20261108 item 1 | **carries** (§9) |

**Flagged for Joseph, through the director:**
- R3, the STOP limit;
- R5, the wording of the two readings;
- R8, whether the director's population mapping stands.

## 9. Price, caps and the projection gate (task item 4)

**The measured costs:**

| path | measured | source |
|---|---|---|
| a change on the MC side (rebuilt blocks) | max 849.6 s, median 725.1 s per unfold | I2 (`FD-1B-INV-I2-REPORT.md:81`) |
| a change on the pseudo-data side (toys) | max 801.4 s plus 16.0 s load | `FD-1B-STAGE2-REPORT.md` §2 |
| node-h per unfold at 8 lanes | 0.022828 | `S1-REPORT.md` §3 |
| c2check at N = 3,000, one truth, one law | 1,314.2 s one-off + 165 × 62.59 s blocks = 3.23 h; peak 269 GiB | A2.1 §8c, job 60859504 |
| the calibration at N, two truths | 0.721 node-h | A2.1 §8b, job 60783756 |

**The unit** is 1,062 s per unfold (1.25 × 849.6 s), as in mode D and 1B staged.

**The resources:** 8 lanes per node, CPU only, `-A m3246 -q regular -C cpu --exclusive --no-requeue`. Every job runs
under 12 h, and nothing goes on CFS.

**Items:**
- per truth: 227 rebuilt blocks, 600 toys (300 per reading) and 2 clipmeans = 829;
- both truths: 1,658;
- plus the 4 procedure controls (§10): **1,662**.

| step | job name(s) | nodes | `--time` | reserved node-h | expected node-h |
|---|---|---:|---|---:|---:|
| calibration at N, 4 evaluations | `ll5d_calib` | 1 | `03:00:00` | 3.0 | about 1.5 |
| receipt + gate + cross terms, per truth (both readings) | `ll5d_gate_G18`, `ll5d_gate_AR23` | 1 each | `08:00:00` | 16.0 | about 12.2 |
| pilot: 4 controls, x̂_T × 2, clipmean × 4, G18 toy 4,751,000 in both readings, AR23 stat replica b = 1 (13 items) | `ll5d_pilot` | 1 | `01:00:00` | 1.0 | about 0.4 |
| bulk: the other 1,649 items, at most 22 per lane at the unit (23,364 s, 81 %) | `ll5d_bulk_01` … `ll5d_bulk_10` | 10 × 1 | `08:00:00` | 80.0 | about 37.6 |
| **cap** | | | | **100.0** | **about 52** |

- **The expected cost** is S1's measured 0.022828 node-h per unfold for the unfolds, and the A2.1 measurements for
  the gate. The gate is 1,314 s plus 2 × 165 × 62.6 s, about 6.1 h per truth. It does not count any saving from
  sharing blocks between the readings.
- **This is above the "about 38 expected, about 80 cap" I sent the director.** That figure left out the gate jobs and
  the calibration (19.0 node-h of cap). I flag it here.

**The caps bind through `--time`.**
- Every connect prints `scontrol show job`'s TimeLimit after submission, and cancels on any mismatch with the table.
- `--time` is written H:MM:SS in full, never as a bare H:MM.
- A job that times out is INVALID, goes to the director unrepaired, and is rerun only on the director's go.

**The projection gate,** before every submission:
- charged so far, from sacct over every `ll5d_*` job: ElapsedRaw × NNodes;
- plus the full `--time` × nodes of every `ll5d_*` job that has been submitted but is not yet ended in sacct. This
  guards against sacct lagging its own sbatch;
- plus this job's `--time` × nodes;
- must be ≤ 100.0 node-h. Otherwise nothing is submitted, and it goes to the director.

**The in-job cost guards:**
- each gate job projects its total from prepare and its first two blocks, and exits before the blocks if the
  projection exceeds 7:30:00. That is a REPRICE to the director, not a STOP;
- after the pilot, every unfold's wall must be ≤ 1,062 s and its peak RSS within S1's per-lane limit, or REPRICE (an
  amendment).

**The balance.** `iris` is read at the first connect. If 100.0 is above half the remaining balance, it goes to Joseph
before any submission (R11). The last balance on record is about 2,035 node-h (A2.1 §8b, 2026-11-04), so half is
about 1,017.

**Storage:** an HPSS copy at each step's end, with `hpssquota` read first.

**The fences.**
- `cov2d_fence.sh` runs before every connect.
- Staging waits until no `cov2d-*` job is queued or running, because the flux constraint
  `sorted_NuEConstraint_FHC_RHC_IMD.txt` is a COV2D input (as Part 1 §6 ruled).
- The new family `ll5d_*` must reach every fenced lane before any go. The director sends it.

## 10. Controls

Any failure reads INVALID and is reported unrepaired.

**The procedure controls (in the pilot).** Each re-runs a block's path on the real data and must reproduce S1's
product bitwise:
- set-A replica b = 1;
- interaction universe MaRES_0;
- flux universe Flux_0;
- detector universe GEANT_Pion_0.

**Per truth:**
- the truth pin;
- r_T > 0 on every row;
- the seed check (x̂_T at seed 45 equals seed 42);
- d_T consistency: the toy path with no draws and every Poisson at its mean builds d_T's arrays bitwise.

**The nature:**
- **k = 1:** §3.3's rule gives `universe_inputs`' arrays bitwise for MaRES_0 and Flux_0 (all four arrays, the
  denominator through §3.4), and for GEANT_Pion_0 (wt, wr, bkgw);
- its experiment at r = 1 equals `fd_1b_moded.d_experiment`'s bitwise, which is κ's nature;
- D1–D3 (§5.1).

**The two readings:**
- **The paired draw:** for every seed, the `minus2` draw equals the `all` draw with GEANT_Neutron's and
  GEANT_Proton's universes removed, and every other band's universe is the same;
- **The block removal:** C_T⁽⁻²⁾ equals C_T minus the two blocks to 10⁻¹² of max |C_T| (§4);
- **The null:** `check_matched` at 10⁻¹² per (truth, reading).

**The grade:**
- C_T is symmetric and positive semi-definite at 10⁻¹² relative, and its ndf is recorded;
- the Cholesky reading rule holds (§6).

**Provenance:**
- one code and one input set across every product of a truth;
- every product names its truth, reading, role, universe and seed;
- the toys' seeds are exactly §3.6's: none missing and none extra.

**Reads:**
- every input not made by this lane is read with `O_NOATIME`. EPERM is raised, never retried;
- each job writes an atime sidecar and exits with 8 set on any move. A move is a deviation, reported unprompted and
  never restored.

## 11. Order, connects and routing

The director gets each connect's sha256 and gives a go before it. Each connect's receipt is a PR. The audit gets
each readout before the next submission.

1. **Binding 1** (this declaration), then **amendment A1** (§12) and **binding 2**.
2. **Connect 1:**
   - the fence;
   - `iris`, `hpssquota` and `squeue`;
   - the stat of every source, which is a STOP to the director, with nothing staged, if a source is missing;
   - a fresh deploy at binding 2's merge.
3. **`ll5d_calib`.** Its readout gives the thresholds, N and the power, and they are committed before any 5D draw is
   examined.
4. **`ll5d_gate_G18` and `ll5d_gate_AR23`,** each running the receipt, the gate and the cross terms. Readout:
   - PASS, STOP or INVALID;
   - the gate per evaluation;
   - D1–D3.
5. **`ll5d_pilot`,** then its walls and **clipcheck**. A `TO_JOSEPH` verdict goes to Joseph before any bulk.
6. **The bulk** is submitted only after all of these:
   - the gate PASS at all four evaluations;
   - the pilot's walls PASS and every control passing;
   - clipcheck `PROCEED`;
   - the projection gate;
   - the audit's written acknowledgement.
7. **Per (truth, reading):** the null, then the readout, then the score record, **committed as a receipt PR whatever
   its verdict**. The lane drafts no outcome sentence. The outcome record is the director's.

## 12. Code, to come as amendment A1 (binding 2)

**A new module, `nd-unfolding/ll5d.py`.**
- **It imports unchanged:** `fd_1b_toys`, `fd_1b_inv`, `fd_1b_moded`, `fd_1b_null`, `s5p_universe`, `s5n_pseudo`,
  `xsec_nd` and `s1_assemble`'s block functions.
- **C2's and A2.1's gate code** is imported from where it lands on main, or copied verbatim from `342c0ce5` with an
  equality test on a shared fixture. Either way it is pinned to a main sha, never to the campaign branch.
- **Its subcommands:** `calib`, `gate` (receipt, gate and cross terms), `unfold`, `walls`, `clipcheck`, `null` and
  `readout`.

**The REQUIRED tests, each with a mutant that a test must kill:**
- per-row first-order composition, and the k = 1 reduction;
- the tdw reference;
- each tree clipped on its own composite, and nowhere else;
- the denominator ≥ 0 under adversarial composites;
- D1, D2 and D3: each fires on a one-ULP change, and D2 at its 10⁻⁹ total and 10⁻³ cell edges (the director's
  ruling D);
- the T ≤ 0 STOP and N1 at their edges;
- the paired draw, and the `minus2` removal on both sides, including the block-removal tolerance;
- Φ_u in the truth, and Φ_CV in the unfolding (Part 1 §2.1's inherited `with_mc` defect killed);
- the gate's thresholds and the four-evaluation budget;
- clipcheck's δ* and its σ proxy;
- the Cholesky reading rule's three failure modes;
- the seed ranges;
- O_NOATIME over the call graph, and an atime move exiting 8.

**The mutation receipt** is committed with its digests. The suite passes at three PYTHONHASHSEEDs.

## 13. What the result can and cannot license; the paper and the note

**MEASURES, when run:** per (truth, reading), §6's statistics and reading, and §7's readouts.

**CANNOT SUPPORT, whatever the outcome:**
- a coverage rate, or coverage at truths unlike these two;
- that the reported intervals cover nature;
- anything about the lateral block, C_resp, C_PL,5D or the response model;
- **that the toys realize S1's block at the tunes.** Rule K is read at the nominal truth only, so a departure from
  like-for-like at T is inside the errors and is not separated;
- anything about GEANT_Neutron or GEANT_Proton beyond the `all` reading's own statistics;
- the coverage of any ENS1 estimator;
- item (c).

**A pass under C_T** carries over to the procedure's full covariance at T, not to the reported covariance made at the
data's point (§4).

**The paper and the note.** This declaration fixes no text.
- The paper lane drafts when a result lands, under R5. The text goes through a PRD-referee read, and Joseph reads it
  before merge.
- New items, which are Joseph's: whether and how the paper names the two readings and the excluded bands, and the
  note's text on the per-row denominator clip.
- The note, in every outcome, states:
  - §6's resolution and size;
  - the overlaps (§3.1);
  - that the d_T-at-means block stands in for a per-toy block;
  - that the laterals are carried.

## 14. For the director

**The director's rulings on this draft (2026-11-08, by message), written in as rulings:**
- **D:** the denominator, per row, ACCEPTED. Addition (ii) is kept per row. D1–D3 are REQUIRED with mutants. The
  T ≤ 0 STOP is accepted.
- **1:** G18 and AR23 only.
- **2:** paired ensembles, with an exact removal that is tested.
- **3:** the 1 % budget over four evaluations, as the director's mapping, which Joseph may override.
- **4:** the analogue of rule (iii) is PENDING-JOSEPH, with the fail-closed default.
- **5:** configuration (e), with no wait for ENS1.

**Two changes from what I sent you, both above:**
- **The receipt runs in the gate jobs, not on a login node** (§5.1). The per-row composites need about 270 GiB.
- **The cap is 100.0 node-h, and about 52 expected,** not about 80 and 38. The gate jobs and the calibration were
  missing from my message. The total is still below half the last recorded balance.

**An option I have not included.** κ at each tune: Dnom against A at T, which would measure like-for-like at the
truths themselves. It costs 175 extra unfolds per truth, about 8 node-h expected. It is not requested, and the
report states the limit (§13).

Nothing is submitted, deposited or tagged.
