# PTMC DECLARATION (DRAFT r2): REF-C2C1's paired test, binned IBU against 2D OmniFold, under OOFVC's R reclassification (2026-11-27)

**Status: DRAFT r2.** It is not audited and not bound, and nothing runs from it.
- The director ruled on D1–D5 on 2026-11-27 (§8).
- r2 answers the first reads, codex-school2 and agy `gemini-4-hydrogen-high` (§8, `reads/r1/`).
- The scoping, price and calendar are in `PTMC-SCOPING.md`.

**Asked for by** Joseph, through the director (2026-11-27). **Drafted by** ibu-chi-squared-issue, read-only on
origin/main `e726cb876`.

**CITABLE FOR:** the design, the controls, the readings fixed before any number, and the licences.

**NOT CITABLE FOR:** any result, cause, physics claim or note wording. The result goes to Joseph before any note text
uses it.

## 0. The question, and what is on record

**The question.** Do binned IBU and 2D OmniFold stay statistically distinguishable, by REF-C2C1's paired test, once
the MC counting convention is OOFVC's R?

**On record (production convention).**
- `OUTCOME-20261106-ref-c2c1-read.md`, readout.json `0ee21301…`. At K = 10, C2-R1 reads **differ**:
  - T_δ = 382.8, against q̂₉₅ = 123.6 and max̂ = 138.5;
  - N = 300 Q_R replicas at rank 75, on the analysis grid.
- At K = 5 it also reads differ.

**R** is OOFVC's reclassification (`OOFVC-DECLARATION.md` §1.3). It follows the counting of MINERvA's released 2021
comparison code. The rows are r3's join output, `oofvc_rows.npz` `cbf34bd8…`, with join record `13674f6d…`. On
r3's record, R does three things:
- **544,162** νμ CC mc_background entries whose true muon is in the grid are taken out of the background;
- **536,518** of them, the ones reconstructed in a cell of the grid, are appended to the selected signal;
- **7,644**, reconstructed outside the grid, enter neither population.

Three caveats carry over from OOFVC:
- νμ CC rows whose true muon is outside the grid stay in the background, as an approximation (OOFVC ruling 3);
- parity with the publication's final production histograms is not established;
- OOFVC's IBU-only numerator variant, N, is not part of this design.

At the central value, OOFVC read r_IBU LOWER and r_ER LITTLE CHANGE. That was on Tier 1's p_T edges, 0.075 / 0.325 /
0.475 GeV/c. This declaration asks a different question, on a different grid (§2.5): the paired IBU-OmniFold
difference under R, against its own bootstrap noise.

## 1. Operands and pins (each is checked by C-IN or C-D4; refused if it differs)

| operand | identity |
|---|---|
| CV omnifile, flux file | `43f8cc16…`, `d40aea69…` (REF-C2C1 `config.json`), staged by an O_NOATIME DTN copy |
| moved rows; join record | `oofvc_rows.npz` `cbf34bd8cad0f4978dc1aea22713eb5057bf521118dc7ce8d10b93b30defcb03` (r3), staged by an O_NOATIME copy; join record `13674f6d…` (r3's `score.json`, `inputs.join_sha256`) |
| driver | M's (`77d76cfc`) `re2_driver.py` `938c53c5…`, plus `oofvc_driver.diff` `6e836e05…`, plus §2.2's hunk. The result is pinned at the tool commit. **Tier 1's edge patch is not applied** |
| code imported unchanged | `ref_c2c1.py` `285dd138…`, `ref_c2c1_read.py` `0412401b…`, `oofvc_lib.py` `a3df5569…`; at M, `omnifold.py` `e9623412…` and `compare_to_paper_fullcov.py` `1dd5ff52…` (REF-C2C1's pin at M and M') |
| new code | the paired runner, the scorer and PTMC's config, pinned at the tool commit |
| RooUnfold | `libRooUnfold.so` `0b34e1e3…` (REF-C2C1 config) |
| publication | `6c6dce72…`, used only for C-CELLS, C-PUB and the descriptive D values |

**The baseline products (D4).** They are checked by C-D4 (§3.2). The disposition in §3.3 applies; C-IN does not.

| product | binding |
|---|---|
| REF-C2C1's IBU central | `units/c2_central.npz`, whose sha256 must equal the committed `units-centrals/c2_central.done` (`929d0e78…`) |
| REF-C2C1's IBU replicas | `units/c2_replica_b{b}.npz`, b = 1..200; each sha256 must equal its committed `.done` (`receipts-ref-c2c1/step2/units-replicas/**/c2_replica_b{b}.done`) |
| E_R central | `read-2/inputs/001_xsec.root`, sha256 `a5c13fc3…` |
| Q_R replicas | `read-2/inputs/{(b+1):03d}_xsec.root` for b = 1..200, i.e. `002`..`201`. Each sha256 must equal readout.json's `staged_sha256` for source `…/partb/out/S1_{b:03d}/xsec.root`, and its own recorded bootstrap seed must be b. The reader staged the publication as 000, then E_R as 001, then S1_001.. (`ref_c2c1_read.py:81, 233, 249, 303`) |

Every baseline product is read through O_NOATIME and staged, by REF-C2C1's `Staged` class, unchanged.

## 2. The design (frozen)

### 2.1 The paired unit

One in-process run of E_R's driver:
- E_R's argv (`config.json` `e_r.argv`), plus `--signal-convention minerva --oofvc-rows <staged>` on an R unit, plus
  `--bootstrap-seed b --bootstrap-streams three` on a replica;
- 64 CPUs, with `OMP_NUM_THREADS=64`, `MKL_NUM_THREADS=1` and `OPENBLAS_NUM_THREADS=1`;
- `--unit-factors` is refused.

**The two methods:**
- **OmniFold.** The driver's own `omnifold` call is observed, not replaced. The unit's `hXSec2D` is OmniFold's. **No
  IBU control reads it.**
- **IBU.** Inside that call, before OmniFold runs, IBU is solved on the identical inputs:
  - REF-C2C1's `binned_problem` on the arguments OmniFold receives (MC truth and reco, masks, w_truth, w_reco, and the
    refined w̃);
  - `roounfold_bayes` (the bound library, never the numpy unfolder) at K ∈ {1, 2, 3, 4, 5, 10, 15, 20};
  - `xsec_at_every_k` through the driver's own recorded extraction call.

**Products.** `<unit>.root` (the driver's) and `<unit>.npz`, which holds:
- the IBU cross section and unfolded vector per K;
- the binned problem (M, T, y);
- the digests of the arrays the OmniFold call received;
- the draw record and completeness record of §2.2;
- argv, the environment and the pins.

A done-marker records the verdict and both products' sha256.

**The pairing is tighter than REF-C2C1's, and that is better (the director's ruling D3).**
- REF-C2C1 ran its IBU replicas and E_R's Q_R replicas as separate driver runs. Each refitted the refinement on the
  same resampled input with the same `random_state`, and LightGBM is not deterministic at 64 threads. So the two
  sides' w̃ agreed only to the fit's reproducibility.
- Here both methods consume one w̃, so δ carries no refit-to-refit noise. It also costs one driver run per replica
  instead of two, which keeps the price under the cap.
- **The asymmetry with B is measured, not assumed (C-PROTO, §3.2).**
  - B's products were made the separate way.
  - Five production-convention paired replicas, at seeds 1..5, are compared bin by bin with B's own products for the
    same seeds.
  - §5 uses "all else held fixed" only under C-PROTO's bound.

### 2.2 The bootstrap under R (the driver hunk)

- **The refusal is lifted for one case.** The present diff refuses `--bootstrap-seed` with `minerva`. That refusal is
  lifted only for `--bootstrap-streams three` on the negweight-refined path, with `--use-weights` and without
  `--unit-factors`. Closure, universe and `--data-file` stay refused.
- **Data factors:** unchanged, Poisson(1) from `default_rng(b)` over the data rows. The data are not reclassified.
- **Original signal rows:** Poisson(1) from `default_rng(b + 10,000,000)`, over exactly the off-convention signal rows,
  in their order. The appended rows are not in that draw.
- **A moved row keeps its own draw (D2).**
  - `append_oofvc_rows` returns the mc_background entry of each row it appends, in append order. These go to the end
    of the signal arrays, and no later step reorders them; between the loader and the bootstrap block the arrays are
    only read.
  - An appended row's factor is b_bkg[entry]: the background stream's Poisson(1) factor, from
    `default_rng(b + 20,000,000)` over every mc_background entry.
  - A listed entry is skipped by the background fill before its fill row is recorded (`oofvc_driver.diff`), so it
    never reaches `re2_injected_entries`. Its factor is used once, on the signal side.
  - The 7,644 rows reconstructed outside the grid are skipped and not appended. They carry no factor in the active
    estimator.
  - The reco and truth weights of an appended row ride its factor together, as for every MC row.
- **The background stream** is unchanged over the rows that remain in the background.
- **Completeness under R is resampled consistently.** This answers agy's blocker 2 and codex's finding 6.
  - In production (Phase-17 inputs, `hasTruthOnlyMisses`), the input truth equals the canonical denominator event for
    event. Resampling both sides gives c* = c_CV, so a replica takes c_CV (KNOWN_ISSUES 84; `re2_driver.py:2432-2448`
    at M).
  - Under R that argument fails: the appended rows enter the input truth but not the denominator.
  - So on an R replica, the hunk sets, per truth cell j:

    c*_j = (T*_orig,j + T*_moved,j) / D*_j,  with  D*_j = D_CV,j · T*_orig,j / T_orig,CV,j

    Here T is the summed w_truth of the truth-passing signal rows (original, or appended), * marks resampled weights and
    CV the un-resampled ones. D*_j is the denominator resampled with the same factors as the original rows that equal
    it event for event.
  - With nothing moved, this reduces exactly to c*_j = c_CV,j, KNOWN_ISSUES 84's value. The production path is
    untouched; the hunk acts only under `minerva`.
  - **Cells are handled as follows:**
    - T_orig,CV,j = 0 keeps the CV completeness, which is the extraction's existing zero-denominator behaviour, and is
      counted.
    - T_orig,CV,j > 0 with T*_orig,j = 0 in a replica is a **STOP** for that unit. It is counted, and the unit fails.
- **The draw and completeness record** per unit:
  - the data, original-row, appended-row and injected-row factor vectors' sums and sha256;
  - the appended entry list's sha256;
  - c* per cell;
  - the counts of the two special cell cases.

### 2.3 Units

| unit | convention | seed | role |
|---|---|---|---|
| `p_off_c` | production | — | C-BASE |
| `p_off_b{1..5}` | production | 1..5 | C-PROTO, C-REPOFF |
| `p_R_c` | R | — | δ_R; C-MOVE, C-FIX, C-SIM, C-ROO |
| `p_R_b{1..200}` | R | 1..200 | C_δ and the null |

That is 207 units.

### 2.4 The statistic

This is REF-C2C1 §1.4's statistic, by its reader's own `t_and_null`, `rank_for` and `classify_t`, after the gates of
C-SHAPE (§3.1):
- **The vectors:** the full 224-cell vector at K = 10, in GlobalID = (p_T bin − 1)·16 + (p∥ bin − 1) order. K = 5 is
  computed identically and is not primary. The 205 reported cells enter only C-CELLS, C-PUB and the descriptive D.
- **R:**
  - δ_R = x_IBU,R − x_E_R,R on `p_R_c`;
  - D_b = x_IBU − x_E_R on `p_R_b`, for b = 1..200;
  - T = δᵀ C⁺ δ, with C⁺ the rank-50 pseudo-inverse of the ddof-1 covariance of the D_b (r = ⌊200/4⌋);
  - the null is leave-one-out, with q̂₉₅ its 95th percentile and max̂ its maximum.
- **B:** the same statistic on REF-C2C1's products at seeds 1..200, by the same functions:
  - δ_off = `c2_central` − E_R (`001_xsec.root`);
  - D_b,off = `c2_replica_b{b}` − Q_R S1_b.

**The bars are prespecified empirical thresholds.**
- A simulation in coverage-5b-audit (#767 Q1), quoted in REF-C2C1 §1.4, used p = 224, replicas centred on δ_data and
  a truncated pseudo-inverse at ⌊N/4⌋. At N = 200 it found a "differ" rate of 0.003, against 1/(N + 1) ≈ 0.005.
- That simulation is not a validation of the R pipeline. No calibrated R false-positive rate is claimed.
- The reference null is exact agreement, so "differ" says a difference is detectable at this noise in the retained
  modes, not that it is large.
- The statistic is blind to any component of δ lying wholly in the discarded subspace.

### 2.5 The grid

M's driver grid, which is E_R's and REF-C2C1's:
- p_T edges 0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50 GeV/c;
- p∥ edges 1.5 … 60 GeV/c, 14 × 16 cells.

This is not Tier 1's grid, whose interior p_T edges are 0.075, 0.325 and 0.475. r3's rows file is reused: its only
grid test, "true muon in a cell of the grid", depends on the outer extents (p_T 0–4.5, p∥ 1.5–60 GeV/c), and the two
grids share them (C-GRID).

## 3. Controls

### 3.1 The R controls (each must pass, or nothing is read and it goes to the director)

- **C-IN:** every §1 pin, checked on the bytes that are used (the staged copies, the deploy tree, the scorer's own
  files).
- **C-GRID:**
  - the driver's PT_EDGES and PZ_EDGES equal REF-C2C1's at M exactly;
  - both axes' outer edges equal Tier 1's grid;
  - every unit's output axes equal E_R's `hXSec2D` axes (`a5c13fc3…`).
- **C-UNITS:** an exact inventory of the 207 units, with no missing, extra or duplicate seed. For each unit:
  - the npz and root sha256 equal its done-marker's;
  - the verdict is PASS;
  - argv equals §2.1's for its row, with the convention flags present on R units and absent on production units, and
    `--bootstrap-seed` equal to its b;
  - the K list is exactly the scan;
  - the unfolder is RooUnfold at the bound library;
  - the CPU count is 64 and the thread environment is §2.1's literals.
- **C-PINS:** every unit records the driver, runner, ref_c2c1, oofvc_lib, omnifold, RooUnfold, rows, join-record and
  input digests, each equal to §1's.
- **C-MOVE** (OOFVC's rule, `OOFVC-DECLARATION.md:309-314`, on M's grid, comparing `p_R_c` with `p_off_c`):
  - per reco cell, the background removed equals the moved rows reconstructed in the grid that the background loader
    had filled (0 ≤ w < 1e6, POT-scaled). This is recomputed independently from the rows file;
  - the tolerance is 1e-12 of the cell's production background. A cell whose production background is zero needs an
    exact zero residual;
  - the signal arrays grow by exactly 536,518, with 7,644 outside, `dropped_appended_weight` = 0 and
    `dropped_outside_weight` = 0 (r3's counts);
  - the skipped and appended entry sets are disjoint and cover the rows file;
  - any non-finite value refuses.
- **C-FIX** (OOFVC's list): `hOFTruthDenom2D`, `hDataReco2D`, `hFlux_pt`, dataPOT, mcPOT, potScale, both flux integrals
  and nNucleons are equal bit for bit, with bin errors and overflow, between `p_R_c` and `p_off_c`.
- **C-FILL-IBU:** in every unit and at every K, IBU's event-level route equals the direct route to ≤ 1e-9 relative,
  with exact zeros where the reference is zero.
  - The event-level route is `ref_c2c1.filled` (the factors u/T per truth-passing event times w_truth), then the
    recorded extraction.
  - The direct route is `xsec_at_every_k`.
  - The unit's own `hXSec2D` is never compared, because it is OmniFold's.
- **C-PAIR:** in every unit, inside the observed call:
  - the w̃, coordinates and masks passed to the real OmniFold are the very arrays IBU binned (sha256 recorded on both
    sides, equal);
  - y is rebuilt independently, with `np.histogram2d` on those coordinates and w̃ over the driver's edges, and equals
    IBU's stored y to 1e-12 relative per cell.
- **C-DRAW-R**, row level, in every replica unit. The runner regenerates, from b, the data, original-signal and
  background factor vectors with the driver's offsets.
  - It checks, row by row and exactly, that the weights reaching the OmniFold call equal the CV weights times the
    expected factors:
    - data rows: the data draw;
    - original signal rows: the signal draw;
    - appended rows: b_bkg at the recorded entries, in order;
    - injected rows: b_bkg at `re2_injected_entries`.
  - It checks that the appended entry list equals the rows file's in-grid list in append order.
  - In the scorer, for every b in 1..200, `p_R_b`'s data-factor and original-row MC-factor sums equal Q_R S1_b's
    recorded `p1Streams` sums exactly (when C-D4 has the file).
- **C-COMP:** in every R replica:
  - c* is recomputed independently from the rows and the factors and equals the unit's to 1e-12 relative per cell;
  - the two special-cell counts are recorded, and the STOP case (§2.2) has count zero.
  - In every production replica, c* equals c_CV exactly.
- **C-SIM, C-ROO** (REF-C2C1's, at 1e-9): C-SIM covers every reported cell, on `p_R_c` and `p_off_c`; C-ROO runs on
  every unit with the bound library.
- **C-BASE:** `p_off_c` reproduces:
  - E_R's `hXSec2D` (`a5c13fc3…`) per bin to ≤ 1e-8 relative, with exact zeros (RE-2's rule; C-CV measured
    9.2×10⁻¹² for a refit);
  - REF-C2C1's `c2_central.npz` cross section at every K, per bin, to ≤ 1e-8 relative, with exact zeros.

  The descriptive D_E_R and D_IBU are compared with readout.json to ≤ 1e-6 relative, OOFVC's tolerance for distances.
  If `c2_central.npz` fails C-D4, C-BASE's IBU vector half falls back to those distances. That fallback is recorded.
- **C-CELLS, C-PUB** (REF-C2C1's): the 205 cells from the bound precision ROOT, and χ² = 465.41527219152636 over 205
  for E_R, to 1e-8.
- **C-SHAPE**, the scorer's gates before any classification. For each arm (R, and B if formed) and each K in {10, 5}:
  - δ is a finite 224-vector and D a finite 200 × 224 matrix, rows in seed order 1..200;
  - the full covariance and every one of the 200 leave-one-out covariances have at least 50 strictly positive
    eigenvalues above the pseudo-inverse's own cut;
  - T, q̂₉₅ and max̂ are finite.

  Any failure refuses. A non-finite T is never classified.
- **C-DONE and C-CPUS:** all of the above held for every unit used.

### 3.2 The baseline controls (C-D4, C-PROTO, C-REPOFF)

- **C-D4:**
  - every §1 baseline product is present as a regular file;
  - each sha256 equals its independent binding (the committed `.done` markers; readout.json's `staged_sha256`);
  - each Q_R copy's recorded bootstrap seed is b;
  - each REF npz's meta records unit `c2_replica_b{b}` and K list equal to the scan;
  - exactly one pair per seed.
- **C-REPOFF:** `p_off_b1` reproduces Q_R S1_001's `hXSec2D`, and `c2_replica_b1`'s cross section at K = 10 and 5, per
  bin to ≤ 1e-8 relative, with exact zeros. Its refinement record matches S1_001's: `signed_sum` exactly;
  `refined_sum` and `clipped_fraction` to ≤ 1e-8.
- **C-PROTO:** for b = 1..5:
  - ε_b = max over cells with C_bb,B > 0 of |D_b,paired − D_b,B| / √(C_bb,B), with C_B the B covariance. A cell
    with C_bb,B = 0 needs |D_b,paired − D_b,B| = 0 exactly, or C-PROTO fails;
  - ε = max_b ε_b;
  - C-PROTO passes when ε ≤ 1e-3: the protocol difference is then under a thousandth of the B noise in every cell.
  - ε is printed either way.

### 3.3 The baseline's disposition, fixed before any T

Each of these is recorded with its reason before any T is formed.
- **B is formed** when C-D4, C-REPOFF and C-PROTO all pass.
- **B is "not formed: unavailable"** when C-D4 finds a product absent and nothing present mismatches. The R reading
  stands alone (§5).
- **STOP to the director, with nothing read**, when any present product fails its digest, seed or meta check, or when
  C-REPOFF fails.
- **B is "formed, protocol-qualified"** when C-PROTO fails while C-D4 and C-REPOFF pass. Both triples are reported
  with their protocols, and §5's "all else held fixed" is not used.

## 4. Readings, fixed before any number

**PTMC-R1** (primary, K = 10). This is REF-C2C1's C2-R1 rule on R:

| T_R | reading |
|---|---|
| T_R ≤ q̂₉₅ | **agree** |
| q̂₉₅ < T_R ≤ max̂ | **marginal** |
| T_R > max̂ | **differ** |

**PTMC-B:** the same rule on B, when B is formed.

**K = 5** is reported in the same form. Only K = 10 enters §5.

**Printed beside the readings, read by nothing:**
- T / q̂₉₅ per arm (shown as "undefined" if q̂₉₅ = 0);
- the Hartlap factor (N − r − 2)/(N − 1) = 148/199 ≈ 0.7437;
- D_IBU at every K and D_E_R under R, on the analysis grid;
- the per-replica ρ_b = D_IBU,b / D_E_R,b at K = 10 and 5, and its central 90 % interval (a replica with
  D_E_R,b = 0 is shown as undefined and excluded from the interval, and counted);
- per-cell δ_R / √C_bb, with zero-variance cells shown as undefined;
- ε from C-PROTO.

## 5. Statements and licences

Every statement concerns **statistical detectability in the retained rank-50 modes, at K = 10, under R.**

| PTMC-R1 | B | statement |
|---|---|---|
| differ | formed, differ | **"Under OOFVC's R reclassification, binned IBU and 2D OmniFold stay distinguishable by the paired test: it reads differ under R, as it does under the production convention on the same draws, N and rank."** |
| marginal or agree | formed, differ | **"Under R, the paired test reads ⟨marginal / agree⟩, where on the same draws, N and rank under the production convention it reads differ."** |
| any | formed, marginal or agree | The R reading as measured, with both triples. No statement about a change of reading: the matched baseline does not reproduce the original's differ |
| any | not formed (unavailable) | "Under R, the paired test reads ⟨reading⟩ at N = 200." It is **not** compared with the original's differ at N = 300 or rank 75 |
| any | formed, protocol-qualified | Both triples, each with its protocol (one shared refinement against separate refits), and ε. No "held fixed" wording |

**"All else held fixed"** may be added to the first two rows only when B is formed, i.e. when C-PROTO passed. It
carries the qualifier: "up to the refit reproducibility C-PROTO measured (ε ≤ 1e-3)". A change of reading is an
observed crossing of each arm's own bar. It is not a test that the IBU-OmniFold discrepancy itself changed, since each
arm has its own covariance, retained modes and bars.

**Licenses:** the statement in its row, with T, q̂₉₅ and max̂ for each arm read.

**Does not license:**
- that the methods are equivalent or equal (the null is exact agreement);
- that the convention is the cause of the IBU-OmniFold difference;
- which method is right;
- any statement that this analysis's inputs, intermediate stages or R equal MINERvA's production histograms (REF-C2C1
  §1.5's last row; OOFVC's parity caveat);
- anything from K = 5 or from §4's printed quantities;
- any change to E_R, Q_R or the note's adopted results.

## 6. Admissibility

- No R product becomes a reported result.
- No follow-up run is made because of these outcomes unless a new declaration binds it.

## 7. Cost and the STOP rule

- **The cost of a replica** is measured from the pilot job's sacct record. A lane's wall time for `p_R_b1`, divided by
  the four lanes per node, is the estimated node-h of one R replica.
- **STOP:** if the pilot's charged node-h, plus 199 × that estimate, exceeds 11.5, the replicas do not launch.
- **The hard cap is 12.5 node-h for the whole campaign,** pilot and retries included. A retry reruns only a unit that
  failed, within the cap.

## 8. Rulings and records

**The director's rulings, 2026-11-27, on the scoping's D1–D5:**
- D1: seeds 1..200;
- D2: a moved row keeps its own background-stream factor;
- D3: the paired unit, with the tighter pairing stated as better (§2.1);
- D4: the matched N = 200 baseline, whose stat connect gets its own GO;
- D5: M's driver grid, with C-GRID, and C-MOVE against r3's counts.

The STOP rule stands (§7).

**The calendar.** This goes in note v1 only if its receipt merges, with full reads, before the note's last sync.
Otherwise it is v2. No step is shortened for the date.

**D4's stat connect** ran on 2026-11-27 at 10:08:52Z on login04, on the director's GO and with cov2d's ack
(`receipts/stat-d4/`).
- It found 604 of 604 expected files: `c2_central` and `c2_replica_b1..200` (.npz and .done), the publication copy,
  and `001..201_xsec.root`.
- The oldest file atime is 2026-11-06T07:31Z, so the purge window is about 2027-01-01.

**Reads, round 1, on the DRAFT at `8040eedba`** (`reads/r1/`, verbatim). Both were run with the same prompt.
- codex-school2, `gpt-6.2-sol` at high effort: 5 blockers, 8 major, 3 minor.
- agy `gemini-4-hydrogen-high`: 4 blockers, 3 major, 1 minor.

Grok is unfunded. Each finding's disposition is in `reads/r1/DISPOSITION.md`.

**Changes in r2 that touch a ruling:**
- C-PROTO adds four production replicas, seeds 2..5, beside D4's `p_off_b1`, at about 0.2 node-h. This prices the
  shared-against-separate refinement asymmetry that both reads raised.
- The resampled completeness under R (§2.2) changes the D2 hunk's scope: it now covers completeness as well as the
  factors.

Both go to the director with r2.
