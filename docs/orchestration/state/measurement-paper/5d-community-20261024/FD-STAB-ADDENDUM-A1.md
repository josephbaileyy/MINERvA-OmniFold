# FD-STAB ADDENDUM A1: the NuWro pv-ladder closure's truth (2026-11-04)

**Amends** [`FD-STAB-DECLARATION.md`](FD-STAB-DECLARATION.md), bound at step one by
[`FD-STAB-BINDING-1.md`](FD-STAB-BINDING-1.md) at M = `dd47f98e`. **For** the audit (coverage-5b-audit) and the
director's binding. The dry run waits for it. Written by limitations-catalog at the director's request, under the
director's rulings of 2026-11-04 (quoted in §6).

## 0. The defect

limitation-resolver's DTN pins check (`pins-check.json` `031e6d55…`, a final STOP) found that every byte matched its
pin, but the §11.1 schema check failed:

- `prep/ratios/L-5D-PV/nuwro.json` (`38e47eb6…`) is schema `pvl-ratio/1`.
- That schema was not in `SCHEMA_TRUTH` (`estimator_stability_probe.py:303` at `dd47f98e`).
- So `closure_truth_kind` (`:356`) would have refused every candidate's `closure_nuwro` task with exit 2 in the full
  run.
- None of the eight dry-run tasks read the file, so the dry run would not have shown it.

**How the suite missed it.** The tests stood the file in with `{"schema": "s5e-shape-ratio/1"}`
(`tests/test_estimator_stability_probe.py:266` at `dd47f98e`). The fixture agreed with the code, not with the file.

## 1. The mapping: `pvl-ratio/1` is read as truth `pvl_ratio`

- `SCHEMA_TRUTH["pvl-ratio/1"] = "pvl_ratio"` (`PVL_TRUTH`).
- `pvl_truth()` adds `pvl_ratio` to `s5n_pseudo.truth_weight` for one closure invocation, the way `s5p_truths` and
  `s5e_deform` add theirs. Every other name passes through, and the name is restored on exit.
- `pvl_ratio_weight` is **`pvl_lib.row_weight`, imported unchanged**, the function that made F0b row 3's truth weight
  (`pvl_unfold.py --closure`). It refuses:
  - an amplitude other than 1 (the pv-ladder has none);
  - a ratio whose axes are not L-5D-PV's;
  - a grid that is not the pv-ladder's 5D fine grid, its five axes in pvl's order with pvl's fine edges. `pvl_unfold`
    requires the same of the npz.
- **The MnvTune null hypothesis is exactly 1 on every row.** `null-mnvtune_v1-J` has `rho = 1.0` in all 243 cells and
  `preserve_total` false. So the probe's per-row weight, hypothesis × alternative, is pvl's r bitwise
  (`PvlTruth.test_the_mnvtune_hypothesis_is_exactly_one_so_the_product_is_pvls`).

**Why not the F1 bridge** (`fd_f1_prep.bridge` to `s5e-shape-ratio/1`):
- F1 bridged only its pseudo-experiments (row 7). Its closures (row 8) ran `pvl_unfold.py` on the `pvl-ratio/1` file
  itself.
- `ratio_nd` (`s5e_deform.ratio_weight`) rescales the in-grid `w_truth` total by one constant, over every in-grid row,
  truth-failing rows included. pvl's r is k-normalised over its assigned cells only.
- So a bridged truth is F0b's times a constant ≠ 1 (`PvlTruth.test_the_f1_bridge_is_not_the_same_truth`).

**The analysis now checks the kind.** It exempted the schema-named closure from its truth-kind check
(`estimator_stability_analyze.py:214` at `dd47f98e`, `kind != "SCHEMA"`). It now requires `pvl_ratio` there and refuses
any other kind (`EndToEnd` tamper `pvl_kind`, the F1 bridge's `ratio_nd`).

## 2. The truth control: the same truth definition as F0b row 3

**What "the same closure" means.** The probe's truths are half B ×2 by declaration (§3.2: "These are not F0b's
products … one MC split"); `s5n_pseudo.true_xsec` sums the split's B half. F0b row 3's `xtrue` is the full MC
(`pvl_lib.closure_inputs`). The two truth histograms differ at MC-statistics level, for all 17 truths alike. So
"the same closure" means the same truth DEFINITION, and that is what C1 and C2 test, exactly.

**The command.** `estimator_stability_probe.py truth-control --queue <OUT>/dry.tsv --f0b-product P --scratch DIR --out
JSON` (`truth_control`). It runs the queue's own `stab_control_closure_closure_nuwro` line through `main`: `install`,
the namespace check, `pvl_truth`, then s5p_nullexp. Only `--out` is moved, to an empty scratch directory. The run is
stopped where the experiment hands its per-row truth weight to `s5n_pseudo.true_xsec`, before any unfold and before
anything is written. Then:

| check | what | kind |
|---|---|---|
| **C1** | the captured per-row weight equals `pvl_lib.row_weight` on the pinned `nuwro.json`, bitwise on every MC row; the axis names are read from the npz, as `pvl_unfold` reads them | gate |
| **C2** | that weight, put through F0b row 3's own truth (`pvl_lib.closure_inputs`: the full MC, the nominal completeness), reproduces the pinned F0b product's `xtrue_flat` within **1e-12 relative per cell**, with the same zero cells | gate |
| C3 | the probe's own truth (half B ×2) against that `xtrue_flat`: the maximum and median relative difference | descriptive |

**The pins are F0's own:**
- `fd_f0_regrade.RATIO["closure_nuwro"]` (`38e47eb6…`) for the ratio;
- `fd_f0_regrade.PINS["closure"]` (`fff9030e…`, `L-5D-PV_e_closure_nuwro.npz`) for the product.

A file that differs from its pin is refused (exit 2), and so is a non-empty scratch directory.

**Ruling 6.** The record carries relative differences, counts and digests only, never an absolute cell value.

**In the job.** `sbatch_fd_stab.sh dry` takes the pinned F0b product as a sixth argument and refuses without it. It
runs the control before T0, so the control's time is charged to the dry run (`sacct`) and is not projected by the
gate. A pass (exit 0) lets the queue start. Any other exit writes `log-dry/STOP` ("truth control rc=…") and ends the
job before any task. Then there is no `DONE`, and the full run refuses. **C1 or C2 failing stops the run and comes to
the director.**

**Where the product is.** The cluster lane passes the path of F0b's product, from the products directory F0b read
(`fd_f0_regrade --pvl-products`). The digest check makes the path's correctness checkable.

## 3. The dry run: nine tasks, and its time limit

**The task.** `DRY_TASKS` gains `stab_control_closure_closure_nuwro` (`TRUTH_CONTROL_TASK`), the one task that reads
the cluster-held ratio. The real-input path now runs before the full run. The task's product and timing carry into
the full run, whose gate skips it, as for the other eight.

**The time limit stays `--time=0:45`.** The audit's simulator, unchanged, was run with the dry run's task list as
coded ("nine") and as bound ("eight"): `fd/stab/gatesim/a1_dry_tasks.py`, output `a1_dry_tasks.txt`, noise-free, with
120 s of setup per job.

| α | B2 | dry (eight) | dry (nine) | outcome, eight → nine | total spent, eight → nine |
|---|---|---|---|---|---|
| 0.8 | 1.0× | 0.18 | 0.33 | COMPLETE → COMPLETE | 6.42 → 6.57 |
| 1.0 | 1.0× | 0.22 | 0.40 | COMPLETE → COMPLETE | 6.46 → 6.64 |
| 1.0 | 1.7× | 0.34 | 0.40 | COMPLETE → COMPLETE | 7.81 → 7.83 |
| 1.1 | 1.0× | 0.23 | 0.44 | COMPLETE → COMPLETE | 6.48 → 6.68 |
| 1.0 | 2.0× | 0.40 | 0.40 | STOP@5 → STOP@5 | 0.43 → 0.43 |
| 1.3 | 2.0× | 0.51 | 0.51 | STOP@5 → STOP@5 | 0.54 → 0.54 |

- **The longest dry run is 0.51 node-h (31 min)** in every cell of the table, at α = 1.3. That is already the
  eight-task worst case, since B2's first task at 2× runs for two waves.
- **The control adds the part of one closure task before its unfold:** loading the npz (33–35 s, the `seconds_load` of four
  `pvl_unfold.py` products on `of_inputs_5d.npz` `07fccc1a…`, in `fd/gencmp-e2/receipts/sweep-a1/e2a1_probe.out.json`), the bank alignment, the truth weights and one full-MC histogram. That is estimated at
  1–3 min; the job's `sacct` start and the `[stab] … start=` line bracket it.
- **About 34 min against 45: a margin of at least 11 min.**
- In all 20 cells of `a1_dry_tasks.txt` the outcome is the same with eight or nine tasks. The ninth task moves one
  closure's charge from the full run into the dry run. It adds up to 0.20 node-h to a completing run, through a
  second wave on one lane while seven lanes are idle. The worst completing total is 7.83, within the 8.0 cap.
- **One effect on the basis.** The second-wave task runs while the other lanes are idle, so it may time faster than
  under full load. It is one of the control's closure timings (with `nominal` and `A7_mnvtune`), so the gate's
  closure rate for the control may read slightly fast: the α < 1 direction of §7. Slurm's `--time` remains the hard
  limit.

## 4. Tests and mutants

**114 tests** (94 before):

- `PvlTruth`, 7 tests, on a `pvl-ratio/1` file written by **`pvl_ratios.write_ratio`, the production writer**, on the
  real 65,856-cell L-5D-PV grid:
  - the file names the pvl truth;
  - the weight is `row_weight` bitwise;
  - the bridge is not the same truth;
  - the MnvTune hypothesis is exactly 1;
  - the refusals (amplitude, edges, axis order, the ratio's axes, schema) and silence on the declared file;
  - the name is restored.
- `TruthControl`, 10 tests, on a synthetic closure, through the real probe and s5p_nullexp. Only the bank's alignment
  check is stubbed, because it needs the full bank and reads nothing the truth uses:
  - it passes and writes nothing;
  - a one-row change to the weight (2⁻⁴⁰ relative) fails C1 alone, with C2 passing below its tolerance;
  - the F1-bridge weight fails C1 and C2. It also fails C2 alone: with `pvl_lib.row_weight` itself returning the
    bridge weight, C1 compares the bridge with itself and passes, and C2 fails by the same relative difference;
  - a product off by 1e-10 fails C2, and one off by 1e-13 passes;
  - a changed zero cell fails C2;
  - an unpinned ratio, an unpinned product and a used scratch are refused;
  - the default pins are F0's;
  - the record carries no absolute value;
  - every numeric leaf of the record is on a key whitelist (counts, relative differences and the tolerance), and
    one planted absolute cell, at the top level, in C2, in C3 or as a list, is refused;
  - the command exits 0, 1 or 2 by its verdict.
- `JobScript`, 3 tests:
  - a failed control (exit 1) stops the dry run before any task, with a STOP, no `DONE`, and the full run refused;
  - a refused control (exit 2) stops it too;
  - the dry run refuses without the F0b product.
  `test_dry_then_full` also checks that the control ran on this run's queue and product.
- **Changed:**
  - `RealParsers` writes the real-format file instead of the stand-in;
  - `EndToEnd` writes kind `pvl_ratio` and gains the tamper `pvl_kind`;
  - `Tasks` expects nine dry tasks, the ninth being `TRUTH_CONTROL_TASK`.

**92 mutations** (69 before), each of which must be killed by its named test. The 23 new mutants:

| area | mutants |
|---|---|
| the mapping | maps the schema to `ratio_nd`; rescales the total; takes any amplitude; takes any grid; the closure runs without `pvl_truth`; the name is not restored |
| the control | C1 not gated; C1 compares the weight with itself; C2's tolerance at 1e-9; C2's zero cells unchecked; C2 against the half-B truth; the verdict ignores C2; the pins unchecked; the product pin is not F0's; a used scratch admitted; the exit ignores the verdict; C2 reads the recomputed pvl weight instead of the probe's; the record leaks one absolute cell |
| the dry run | `closure_nuwro` not in it; the job ignores the control's exit; the job runs without the F0b product |
| the analysis | the schema-named closure's kind exempt again; the schema-named closure wants `ratio_nd` |

The F1-bridge and whitelist tests and their two mutants close the two test gaps, N1 and N2, from
coverage-5b-audit's audit of 337fd783 (PR #750, comment 6637775427). The probe, sbatch and analysis are
unchanged from that head.

## 5. What A1 amends in the declaration

| declaration | was | now |
|---|---|---|
| §3.2, the closure NuWro row | "truth kind from its `schema`" | schema `pvl-ratio/1`, read as truth `pvl_ratio` = `pvl_lib.row_weight` (§1) |
| §3.2, the analysis's checks | an alternative's kind is checked, except for the schema-named closure | checked for every closure; `pvl_ratio` for the schema-named one |
| §7 | the gate skips the dry run's eight tasks | nine; the dry run runs the truth control before T0 |
| §8 | 94 tests, 69 mutations; `sbatch_fd_stab.sh dry <deploy> <pin> <OUT> 8.0` | 114 tests, 92 mutations; `sbatch_fd_stab.sh dry <deploy> <pin> <OUT> 8.0 <F0b closure product>` |
| §11.1 | the dry run confirms the ratio's schema names a declared truth kind | measured: `pvl-ratio/1`; resolved here, and checked by C1 and C2 |
| §11.2 | eight one-unfold tasks | the truth control, then nine one-unfold tasks; `--time=0:45` kept (§3) |

**Unchanged:**
- the candidates, the 18 truths and their files and pins;
- the stability and bias criteria, the verdict and its terminal branches;
- the cap of 8.0 CPU node-h, the gate, and the receipts.

**What the full run would have done without A1.** It would have stopped at its first `closure_nuwro` task: a failed
task stops the queue (§7). It would not have produced a wrong number.

## 6. The director's rulings (2026-11-04), as received

1. The mapping is accepted: `SCHEMA_TRUTH["pvl-ratio/1"]` → `pvl_lib.row_weight`, imported unchanged, refusing an
   off-grid input or an amplitude ≠ 1. The bridge's constant rescaling over in-grid rows is decisive against it.
2. The control is ruled as in §2: C1 and C2 are gates, and C3 is descriptive. C1 or C2 failing stops the run and
   comes to the director. This does not change what the probe measures, so it is not Joseph's.
3. The analysis change is approved: kind `pvl_ratio` for the schema-named closure, tested in both directions, with a
   mutant.
4. Nine tasks on 8 lanes: show that the dry run fits `--time=0:45` with margin, or raise the dry run's limit and say so
   here (§3).

## 7. Commands

    python3 -I nd-unfolding/estimator_stability_probe.py tasks --out <OUT>/queue.tsv --dry-out <OUT>/dry.tsv \
        --npz <npz> --bkg <bkg> --bank <bank> --detector-dir <det> --expect-npz-sha256 <h> --expect-bkg-sha256 <h> \
        --closure-ratio-dir <dir holding prep/ratios/L-5D-PV/nuwro.json> --runs <OUT>/runs
    sbatch --time=0:45 nd-unfolding/sbatch_fd_stab.sh dry <deploy> <pin> <OUT> 8.0 <F0b L-5D-PV_e_closure_nuwro.npz>
    sbatch --time=<8.0 minus the dry run's charge> nd-unfolding/sbatch_fd_stab.sh full <deploy> <pin> <OUT> <8.0 minus that charge>
    python3 -B nd-unfolding/tests/estimator_stability_mutation.py      # 92 mutations, all killed

**Who runs it:** the cluster lane the binding names (limitation-resolver), from a fresh clone at the commit that binds
A1. This session does not contact the cluster.

MEASURES: nothing; it declares a change. CANNOT AUTHORIZE: a run before the director binds A1.
