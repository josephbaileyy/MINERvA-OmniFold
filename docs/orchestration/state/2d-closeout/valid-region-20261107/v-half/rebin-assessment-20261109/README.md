# What a rebinning of R00-R15 would cost (the valid-region lane, 2026-11-09/10, for the director and Joseph)

The director asked for this on 2026-11-09. It was made read-only, at 0 node-h, with nothing run on the cluster. Every
file:line is at main `58719d4b91924aedd8fd32397c524d8cbb8d2641`, read through `git show`. Lines marked [INF] are
inferences. No V-HALF class is given here beyond the counts already reported (valid 5, not valid 9, unresolved 2).
<!-- absence-ok: a statement of how this record was made (the lane's own scope), not a claim that a result does not exist -->

CITABLE FOR: the cost and time assessment and its sources.
NOT CITABLE FOR: any rebinning decision, any V-HALF class, any cell's validity.

**Unverified dependency.** pscratch purges files by access time (`nd-unfolding/ref_g1/ref_g1.py:132`). Every
"re-aggregates at 0 node-h" below assumes that the pscratch fine-grid products still exist. That had not been checked
when this was written. A stat-only existence check is the follow-up; its result is recorded beside this file when it
runs. **Checked 2026-11-10T04:16Z** (`purge-check/README.md`): all 8,795 listed files present, 0 missing; the oldest
access was 10.6 days earlier. The check does not guarantee that the files survive later.
<!-- absence-ok: a stated dependency, not a claim that a file is absent; the check is the follow-up -->

## Bottom line

**Merging cells within the current grid.** About 25 node-h of compute, almost all of it LL5D's cell-level gates. The
real cost is code edits plus an amendment, audit and bind cycle on five studies.

**A rebinning that leaves the fine grid.**
- About 87-92 node-h if F0b regrades only its 12 graded truths.
- About 280-400 node-h if F0b is rerun in full, including its offset control and P rows.
- Either way it hits a blocker: the 5D lateral dumps no longer exist.

**Correction.** The message sent before this record counted F0b's inputs as 1,368 experiments, for a worst case of
112-131 node-h. F0b in fact reads 8,545 products: the 1,368 experiments, 7,176 calibration products and the closure
floor. The worst case is restated in §4.

## 1. The cell definition

- **The boxes.** R00-R15 are unions of 32 "H2" boxes, two bins per axis (`nd-unfolding/s5p_stage1_inspect.py:47-48`):
  - pt [0, 0.7, 4.5], pz [1.5, 4.5, 60], E_avail [0, 0.8, 100], q3 [0, 2, 100], W [0, 1.8, 100].
  - Each fine cell is assigned by its centre, and every coarse edge must be a fine edge (`coarse_map`, :77-99).
- **The maps.**
  - `nd-unfolding/pv-ladder/readouts/h2_definition.json` maps the 32 boxes onto 16 cells (`h2_to_reporting_cell`).
    Boxes 2, 6, 10 and 14 are unreported.
  - `s1_assemble.fine_map` expands that map to the 65,856 fine cells (`nd-unfolding/s1_assemble.py:103-116`).
  - `functional_matrix` makes row c the fine-bin volume where fm == c (:119-122). So each cell is a linear functional
    U·x of the fine vector x.
- **Merges of R-cells, or any union of the 32 boxes** (including unreported ones), are a new `h2_to_reporting_cell`
  list. `coarse_map` and `functional_matrix` need no new code. What has to be re-pinned or edited:
  - `DEFINITION_SHA256`, `FINE_MAP_SHA256` and `N_CELLS` (`s1_assemble.py:43-44`, :51), and the 32-box/16-cell check
    (:110);
  - `prr_read.py:61`;
  - about 15 modules that hardcode 16, among them `fd_f0_regrade.py:67` (with its GiBUU cell list at :74),
    `prior_retention/prr_probe.py:147`, `fd_cpl_addition.py:44`, `fd_data_product.py:42` and `fd_ct_periods.py:54`;
  - V-HALF: `CELLS` (`v_half.py:35`), the length checks (:239-241, :264), C-DOMAIN's 8 GiBUU cells (:284), and C-HAND,
    which is fixed on R06 (:323).
  - The module list is the search agent's; s1_assemble, prr_read and v_half were spot-checked.
- **Unions of fine cells that are not unions of H2 boxes** need new coarse edges and a rerun of the H2 builder
  (`h2_definition.py`, code `44848eb1`). The builder reads the MC npz `07fccc1a` on pscratch.
- **Boundaries that are not fine edges** need a new fine grid, and with it new unfolds of everything.

## 2. What re-aggregates at 0 node-h

Every unfolded product keeps the fine vector (`xsec_flat`, plus `xtrue_flat` where simulated). The committed readouts
hold only 16-cell numbers.

- **The data central value `fb5cc679`.** Fine. It is on pscratch only, at
  `s5p-20260926/runs/s2/num/data/data_b-_j-.npz`, with a CFS archive copy
  (`docs/orchestration/state/2d-closeout/stageF/methods/m2-archive/inputs_sha256.tsv:32-33`). `f = U @ xs`
  (`s1_assemble.py:313`).
- **F0b.** Its inputs are 8,545 fine products, selected by its own code from committed manifests
  (`fd_f0_regrade.py:560-584`):
  - 221 graded experiments at the 12 graded truths: 40, 5 × 20, 1 and 5 × 16;
  - the closure floor;
  - 1,147 ungraded P-row experiments;
  - 7,176 calibration products. These feed only the A7 offset control (control 7) and the P rows (:738-775).

  Each is checked as a fine vector (:417-421) and integrated (:712-717).
  - The readout's bias and noise are ratios, r = X̂/X − 1, with noise cov(r)/B (:207-212). So they are recomputed per
    experiment from the fine products, not by A·N·Aᵀ. That is login arithmetic: the last regrade took 70 s
    (`FD-F0b-REPORT.md:41`).
- **FD-PRR.**
  - Route 1's 181 products are fine (`prior_retention/prr_read.py:172-174`, `prr_probe.py:633-634`). The read takes
    about 80 s on a login node (`fd/receipts-prr/read/`) once its 16-cell pins are edited.
  - Route 2 (IBU) stored only 16-cell integrals (`prr_ibu.py:14-15`). It needs a new job, measured at 0.1517 node-h
    (`fd/receipts-prr/ibu/attempt3/`).
- **The covariance blocks, exact as A·C·Aᵀ for merges.** Each is a sample covariance or an outer product of linear cell
  vectors, with weights that do not depend on x:
  - C_stat (`s1_assemble.py:316-321`);
  - the universe bands, by weighted MAT CalcCovMx (:125-130, :323-329);
  - the laterals, two-endpoint, with MINOS rescaled per pT before U (:331-341);
  - C_norm (:343) and C_seed (:344-352);
  - C_resp, the half-span d dᵀ (`build_cresp.py:108-114`);
  - C_model_abs: s_k∘X0 = X_k − X0 is linear (`pv-ladder/build_cmodel5d.py`). The merged fractional matrix is
    diag(1/Af)·A·C_abs·Aᵀ·diag(1/Af), not A·C_frac·Aᵀ.

  The C_e sum has no clipping and no PSD repair (:353, :366-368).
- **Not exact: C_PL,5D.** It is built from cellwise ratios: r = x_P/T_P, g = r/mbar − 1, C = k Σ e_P g gᵀ
  (`fd_ct_periods.py:411`, :422-427). It is rebuilt at login cost from its 34 period unfolds and 4 MC truths on
  pscratch, which are named in `fd/readout/fd_ct_5b_periods.json` (inputs_sha256.unfolds) and
  `fd/receipts-ct/5b/5b-inputs-steps.tsv`.
- **New unions of fine cells, beyond merges, need the fine vectors.**
  - Committed: C_stat b1-b20, all 175 universes, the 10 laterals, the 80 seed replicas
    (`s1/readout/s1_assembly/`) and C_resp's 8 endpoints (`phase1/mp1/s1-receipts/verify/`).
  - On pscratch only: C_stat b21-b50 (`S1-REPORT.md:222-225`), the central value, the pv-ladder model products and the
    C_PL period unfolds.

## 3. New compute

- **V-HALF's re-read:** 0 (local).
- **F0b's grading:** about 0, on a login node, once the grade matrices are rebuilt on the new cells
  (`prr_read.py:223-257` rebuilds them from committed inputs).
- **Stability (FD-STAB).**
  - Its stability statistic is on s5e's 153 functionals, which do not depend on the cells
    (`estimator_stability_analyze.py:282-298`).
  - The parts that do use M16 are `cell_sd` and the bias at 17 truths (:234-237, :299, :305). They re-aggregate from
    its fine products on a login node.
  - A full rerun was 4.8645 node-h (`fd/receipts-stab-a1r/README-full-readout.txt:9-10`).
- **LL5D** tests coverage of the 16 cells under C_T. Its gate is per-block, cell-level work.
  - G(N) = 1,333.9 + 99.23·(2(15 + N/20) + 30) s per truth, which is 10.29 h at N = 3,000
    (`LL5D-DECLARATION.md:570-574`). The cross terms add 1-1.5 h (`LL5D-AMENDMENT-A1A.md:155-168`), for 11.3-11.8 h
    per truth.
  - The calibration measured 1.18 node-h (`fd/receipts-ll5d/calib-2/README.md:9-10`).
  - [INF] A cell-level redo is about 1.2 + 2·(11.3-11.8) ≈ 24-25 node-h, against a reservation of 67 (5 + 62).
  - The full LL5D is about 62-63 expected under its 148 cap (`LL5D-DECLARATION.md:589-593`, with A1a). Its pilot and
    bulk have not run; they wait for the gates (`LL5D-BINDING-3.md:42-43`).
    <!-- absence-ok: no ll5d pilot or bulk receipt exists under fd/receipts-ll5d/ at 58719d4b (its directories are a1a, a1a1, a1b, calib-1-invalid, calib-2 and ovl); the binding gates them on the gate jobs -->
  - The 16-cell gates 61040235 and 61040163 were RUNNING at 2026-11-09T23:34Z (`fd/receipts-prr/read/`). [INF] They
    end around 04:00Z on 2026-11-10.

## 4. Totals, against 1,627 node-h (half 813.7; `fd/receipts-prr/ibu/attempt3/cluster/logs/connect-ibu-3.log.txt:12`)

**Best case** (merges or H2-box unions, same fine grid):
- About 25 node-h expected: LL5D's gates 24-25 and IBU 0.15. Everything else is login arithmetic. That is about 3 % of
  the half.
- LL5D's pilot and bulk (about 38) then run at the new cells instead of the old, not in addition, unless both sets are
  wanted.
- [INF] Wall clock: compute well under a day (about 12 h of gates in parallel, then 8 h of bulk). The calendar is set
  by the edits and re-pins in about 15 modules, plus amendment, audit and bind on S1, F0b, FD-PRR, V-HALF and LL5D:
  several days at the 2026-11-09 cadence.

**Worst case** (a new fine grid), rerunning every unfold:

| item | node-h | source |
|---|---|---|
| S1 | 6.04 | measured, `S1-REPORT.md:132-135` |
| F0b, the 12 graded truths only (222 unfolds) | 5.1-8.2 | [INF] at 0.022828 to 0.036875 node-h per unfold, `FD-PRR-DECLARATION.md:465-477` |
| F0b in full (8,545 unfolds) | 195-315 | [INF] at the same rates |
| FD-PRR | 7.58 | measured |
| FD-STAB | 4.86 | measured |
| LL5D | 62-63 | expected |
| C_PL, C_resp, C_model | a few | [INF] |

- That is about 87-92 node-h with the graded-only F0b, or about 280-400 node-h with F0b in full. These are about 11 %
  and 34-49 % of the half, before rebuilding the fine-grid inputs, which is unpriced.
- **Blocker:** the 5D lateral dumps no longer exist (`LL5D-DECLARATION.md:276`, citing `FD-1B-DECLARATION.md:99`).
  The laterals cannot be re-unfolded on a new grid; they could only be carried in relative form, as LL5D §3.8 does.
- [INF] Calendar: weeks.

## 5. What a pre-specified merging rule must declare (listed only; nothing is drafted)

- **Timing.** It is fixed, audited and bound before any merged V-HALF is computed.
- **The criterion uses no V-HALF outcome.** For example, it could use only definition-level quantities (purity,
  stability, MC n_eff), as h2_definition's own merge steps do.
- **The allowed merges:**
  - unions of R-cells only, or of H2 boxes;
  - adjacency, and along which axes;
  - whether unreported boxes may join;
  - the maximum number of rounds, a minimum cell count, and a deterministic order and tie-break.
- **What stays fixed:** the 12 truths, the 1 % floor, HALF 0.5, K = 2, the noise treatment and H1/H2's provenance.
  No truth is dropped.
- **One shot:** no iteration on the merged result.
- **A terminal outcome.** If, after the allowed merges, any cell is still not valid (or unresolved), or the minimum
  count is breached, the result is "no acceptable binning". Without that outcome, a valid-only binning is always
  reachable by merging enough.
- **The 16-cell result** is reported beside the merged one, with the declared licences.
- **Item 5** (the advisor's consequence) stays Joseph's.

## Sources the lane did not open itself

The module list in §1 and parts of §2-§3 came from three read-only search agents. The lines the bottom line rests on
were spot-checked directly at 58719d4b:
- `s1_assemble.py:43-44`, :51, :103-122 and :313-321;
- `s5p_stage1_inspect.py:47-48` and :77-99;
- `fd_ct_periods.py:405-436`;
- `fd_f0_regrade.py:207-224`, :420-470, :560-590 and :738-775;
- `v_half.py:35`;
- `FD-F0b-REPORT.md:41`;
- `LL5D-DECLARATION.md:274-284`, :543-593, and A1a :155-168;
- `calib-2/README.md:9-10`;
- `README-full-readout.txt:9-10`;
- `LL5D-BINDING-3.md:42-43`;
- `build_cresp.py:108-114`;
- `prr_ibu.py:12-16`;
- `S1-REPORT.md:132-135` and :222-225.
