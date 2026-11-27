# PTMC DECLARATION (DRAFT): REF-C2C1's paired test, binned IBU against 2D OmniFold, under MINERvA's counting convention (2026-11-27)

**Status: DRAFT.** It is not audited and not bound, and nothing runs from it. The scoping, price and calendar are in
`PTMC-SCOPING.md`.

**Asked for by** Joseph, through the director (2026-11-27). **Drafted by** ibu-chi-squared-issue, read-only on
origin/main `e726cb876`.

**CITABLE FOR:** the design, the controls, the readings fixed before any number, and the licences.

**NOT CITABLE FOR:** any result, cause, physics claim or note wording. The result goes to Joseph before any note text
uses it.

## 0. The question, and what is on record

**The question.** Do binned IBU and 2D OmniFold stay statistically distinguishable once the counting convention
matches MINERvA's?

**On record (production convention).**
- `OUTCOME-20261106-ref-c2c1-read.md`, readout.json `0ee21301…`. At K = 10, C2-R1 reads **differ**:
  - T_δ = 382.8, against q̂₉₅ = 123.6 and max̂ = 138.5;
  - N = 300 Q_R replicas at rank 75, on the analysis grid.
- At K = 5 it also reads differ.

**MINERvA's convention** is OOFVC's R (`OOFVC-DECLARATION.md` §1.3). The νμ CC mc_background entries whose true muon
is in the grid are moved to the selected signal, as MINERvA's 2021 code counts them. The production driver sends
them to the background (runEventLoopOmniFold.cpp:1453-1456).
- The rows are r3's join output, `oofvc_rows.npz`, sha256 `cbf34bd8…`, with join record `13674f6d…`.
- At the central value, OOFVC read r_IBU LOWER and r_ER LITTLE CHANGE (on the paper's p_T edges). This declaration
  asks a different question: the paired difference between the two methods under R, against its own bootstrap noise.

## 1. Operands, bound by digest (refused if any differs)

| operand | identity |
|---|---|
| CV omnifile, flux file | `43f8cc16…`, `d40aea69…` (REF-C2C1 `config.json`), staged by an O_NOATIME DTN copy |
| moved rows | `oofvc_rows.npz` `cbf34bd8cad0f4978dc1aea22713eb5057bf521118dc7ce8d10b93b30defcb03` (r3), staged by an O_NOATIME copy |
| driver | M's `re2_driver.py` `938c53c5…` (E_R's grid), plus `oofvc_driver.diff`, plus §2.2's bootstrap hunk. Its digest is pinned at the tool commit. **Tier 1's edge patch is not applied** |
| REF-C2C1 code | `ref_c2c1.py` `285dd138…` and `ref_c2c1_read.py` `0412401b…`, imported unchanged |
| E_R, off-convention | `hXSec2D` of `a5c13fc3…`; D_E_R = 2.270318400934308 (readout.json) |
| IBU, off-convention | readout.json's `D_IBU_every_K` |
| baseline products (D4) | `ref-c2c1-20261106/units/c2_replica_b{1..200}.npz` and `read-2/inputs/{001..200}_xsec.root` (Q_R S1_001..200). Each is hashed at the read; the units' `.done` sha256 must match |
| publication | `6c6dce72…`; it enters only through the descriptive D values |

## 2. The design (frozen)

### 2.1 The paired unit

One in-process run of E_R's driver: E_R's argv (`config.json` `e_r.argv`), plus `--signal-convention minerva
--oofvc-rows <staged>`, plus `--bootstrap-seed b --bootstrap-streams three` for a replica. E_R's 64 CPUs and thread
environment apply.
- **OmniFold.** The driver's own `omnifold` call is observed, not replaced. The driver's hXSec2D is the E_R-side
  product.
- **IBU.** In the same call, before OmniFold runs, IBU is solved on the identical inputs:
  - REF-C2C1's `binned_problem` on the arguments OmniFold receives (MC truth and reco, masks, w_truth, w_reco, and the
    refined w̃);
  - `roounfold_bayes` at K ∈ {1, 2, 3, 4, 5, 10, 15, 20};
  - `xsec_at_every_k` through the driver's own recorded extraction.
- **Products.** `<unit>.root` (the driver's) and `<unit>.npz`: the IBU cross section per K, the binned problem's
  digests, and the draw record of §2.2.

### 2.2 The bootstrap under R (the driver hunk)

- **The refusal is lifted for one case.** The present diff refuses `--bootstrap-seed` with `minerva`. That refusal is
  lifted only for `--bootstrap-streams three` on the negweight-refined path. Closure, universe and `--data-file` stay
  refused.
- **Data factors:** unchanged, Poisson(1) over the data rows (the data are not reclassified).
- **Signal-MC factors:** Poisson(1) from the signal sub-RNG (seed + 10,000,000), over exactly the off-convention
  signal rows, in their order. The appended rows are not in that draw.
- **A moved row keeps its own draw (D2).** An appended row's factor is b_bkg[entry]: the background stream's Poisson(1)
  factor for its mc_background entry (seed + 20,000,000, drawn over every entry). A moved row is skipped by the
  background fill, so that factor is used only once, on the signal side.
  - The reco and truth weights ride that factor together, as for every MC row.
- **The background stream** is unchanged over the rows that remain in the background.
- **Completeness:** the un-resampled w_truth, as now (KNOWN_ISSUES 84).
- **The draw record** per unit:
  - the data factor sum;
  - the MC factor sum over the original rows;
  - the factor sum over the appended rows;
  - the background-stream sum over the injected rows.

### 2.3 Units

| unit | convention | seed | role |
|---|---|---|---|
| `p_off_c` | production | — | C-BASE |
| `p_off_b1` | production | 1 | C-REPOFF |
| `p_R_c` | R | — | δ_R and the controls |
| `p_R_b{1..200}` | R | 1..200 | C_δ and the null |

### 2.4 The statistic

This is REF-C2C1 §1.4's statistic, by its reader's own functions, on the full 224-cell vector at K = 10 (K = 5 is
reported identically):
- δ_R = x_IBU,R − x_E_R,R on `p_R_c`;
- D_b = x_IBU − x_E_R on `p_R_b`, for b = 1..200;
- T = δᵀ C⁺ δ, with C⁺ the rank-r pseudo-inverse of the ddof-1 covariance of the D_b. The rank is r = ⌊N/4⌋ = 50
  (`rank_for`);
- the null is leave-one-out (`t_and_null`), with q̂₉₅ its 95th percentile and max̂ its maximum.

**Calibration** (coverage-5b-audit, #767 Q1, at p = 224, N = 200 and rank 50, which is this case):
- the rate for "differ" is 0.003, against 1/(N + 1) = 0.005;
- so max̂ is about a 0.5 % bar.

The null is exact agreement: "differ" says a difference is detectable at this noise, not that it is large.

**The baseline, B** (D4), is the same statistic on the production convention, at the same seeds, N and rank:
- δ_off = REF-C2C1's `c2_central` − E_R (`a5c13fc3`);
- D_b,off = `c2_replica_b{b}` − Q_R S1_b, for b = 1..200.

## 3. Controls (each must pass, or nothing is read and it goes to the director)

- **C-IN:** every digest in §1.
- **C-GRID:**
  - the driver's PT_EDGES and PZ_EDGES equal REF-C2C1's (E_R's) grid;
  - their outer extents equal OOFVC's paper-edge grid, so the rows' in-grid set is unchanged.
- **C-PINS:** every unit records the driver, runner, ref_c2c1 and oofvc_lib digests, the rows file and the inputs, and
  each equals the bound value.
- **C-BASE:** `p_off_c` reproduces E_R's hXSec2D to ≤ 1e-8 relative in every bin (RE-2's rule). Its IBU gives
  readout.json's D_IBU at every K to ≤ 1e-8 relative. This ties the paired seam to REF-C2C1's c2 and to E_R.
- **C-REPOFF:** `p_off_b1` reproduces Q_R S1_001's hXSec2D, and REF-C2C1's `c2_replica_b1` cross section at K = 10
  and K = 5, each to ≤ 1e-8 relative. This ties the replica path.
  - If the D4 products are absent, C-REPOFF is "not available". It is not a failure, and B is then not formed.
- **C-MOVE:** under R, the append counts equal r3's join record:
  - 536,518 appended, 7,644 outside, 0 dropped;
  - per reco cell, the background removed (off minus R) equals the moved rows' filled weight to 1e-12 of that
    cell's production background, OOFVC's C-MOVE rule (`OOFVC-DECLARATION.md:309-313`), with `p_off_c` as the off side.
- **C-PAIR:** in every unit, IBU's measured histogram is the bin sum of the very w̃ array the OmniFold call received.
  The two w̃ digests are recorded and must be equal, bit for bit.
- **C-DRAW-R:**
  - in `p_R_b1`, the data and original-row MC factor sums equal `p_off_b1`'s exactly;
  - in every R replica, the appended rows' factor vector equals b_bkg at their entries (sum and digest recorded;
    unit-tested on the fixture).
- **C-SIM, C-ROO, C-FILL:** REF-C2C1's, on `p_R_c`, at 1e-9.
- **C-DONE and C-CPUS:**
  - all 204 units PASS;
  - each ran with 64 CPUs and E_R's thread environment.

## 4. Readings, fixed before any number

**PTMC-R1** (primary, K = 10; K = 5 reported identically and not primary). This is REF-C2C1's C2-R1 rule on R:

| T_R | reading |
|---|---|
| T_R ≤ q̂₉₅ | **agree** |
| q̂₉₅ < T_R ≤ max̂ | **marginal** |
| T_R > max̂ | **differ** |

**PTMC-B:** the same rule on B. It is formed only if C-REPOFF passed.

**Printed beside the readings, read by nothing:**
- T / q̂₉₅ for R and for B;
- the Hartlap factor;
- D_IBU and D_E_R under R at every K on the analysis grid;
- the per-replica ρ interval;
- per-bin δ_R in units of √C_bb.

## 5. Statements and licences

| PTMC-R1 | PTMC-B | statement |
|---|---|---|
| differ | differ, or not formed | **"Under MINERvA's counting convention, binned IBU and 2D OmniFold stay distinguishable: the paired test reads differ"**, adding "as it does under the production convention at the same draws" when B is differ |
| marginal or agree | differ | **"Under MINERvA's convention the paired test reads ⟨marginal / agree⟩, where on the same draws, N and rank under the production convention it reads differ"** |
| marginal or agree | not formed | "Under MINERvA's convention the paired test reads ⟨marginal / agree⟩ at N = 200." It is **not** compared with the original's differ at N = 300, because N and rank differ |
| any | marginal or agree | the R reading as measured. No statement about a change of reading, because the matched baseline does not reproduce the original's differ |

**Licenses:** the statement in its row, with T, q̂₉₅ and max̂.

**Does not license:**
- that the methods are equivalent or equal (the null is exact agreement);
- that the convention is the cause of the IBU-OmniFold difference, beyond "the reading changes with the convention,
  all else held fixed";
- which method is right;
- any statement that our inputs or intermediate stages equal MINERvA's (REF-C2C1 §1.5's last row);
- any change to E_R, Q_R or the note's adopted results.

## 6. Admissibility

- No R product becomes a reported result.
- No follow-up run is made because of these outcomes unless a new declaration binds it.
