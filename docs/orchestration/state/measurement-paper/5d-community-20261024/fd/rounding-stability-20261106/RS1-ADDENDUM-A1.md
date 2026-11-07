# RS1 ADDENDUM A1: resuming the full run after attempt 1's teardown crash (2026-11-07)

**For** audit by `coverage-5b-audit` and binding by the director, as RS1-BINDING-2 addendum A1. **Nothing has run under
it.** It changes no part of RS1's design (`RS1-DECLARATION.md`, bound by `RS1-BINDING-1.md`), no bound module, and not
`sbatch_rs1.sh`. It adds a staging module and a resume wrapper only.

**Written by** the rounding-instability lane (`director-helper-3`) under the director's rulings of 2026-11-07 on
attempt 1 (in correspondence): INVALID (infrastructure); a resume approved in principle; a fresh root; a new wrapper
with a teardown guard; V_02 recomputed; the refactor deferred; the cap unchanged. Citations are at M =
`e306087e68fd497541d32b440848a40f7f29611e` unless stated.

**CITABLE FOR:** the resume's design, guard, price and connect plan.
**NOT CITABLE FOR:** any RS1 result; a cause of the crash beyond its log's frames.

## 1. What happened (receipt #901, `receipts/full-attempt-1/`)

Job 60972000 failed after 58:40, for 0.9778 node-h.
- **The task:** `rs1_V_02` wrote all four of its products with rc 0, then segfaulted in PyROOT during interpreter
  teardown (`CPyCppyy::op_str` from `Py_FinalizeEx`), with exit 129. `sbatch_rs1.sh` treats any non-zero exit as a
  failure (`:59-60`, `exit 255`), so xargs stopped launching.
- **What ended:** 11 full tasks (42 unfolds). 45 tasks never started.
- **RS1's charge:** 1.2400 of the 8.0 cap.

**Why ROOT is in a task at all.**
- `s5n_pseudo.refine` (`nd-unfolding/s5n_pseudo.py:263-272`) calls `load_u2d` (`:256-261`). That imports
  `2d-unfolding/unfold_2d_omnifold_unbinned.py`, which runs `import ROOT` at module level (`:24`, `SetBatch` at `:26`).
- The path uses only `refine_stay_positive` (`:412-459`) and `_make_bkg_classifier` (`:381-411`), and neither uses
  ROOT. So ROOT is loaded in every RS1, FD-STAB and ENS1 task, and this path does not need it.
- **Not established:** why one process in 21 crashed at exit. In the same path there were no crashes in RS1's 9 dry
  tasks or in FD-STAB's 137.

## 2. The resume

**2.1 A fresh root,** `/pscratch/sd/j/josephrb/rs1-a1-20261107`. Attempt 1's root stays intact as evidence.

**Why a fresh root.** The bound analysis requires `<root>/log-dry/DONE` and `<root>/log-full/DONE` at the same pin, with
no STOP or FAILED beside them (`rounding_mechanism_analyze.py:123-137`). Attempt 1's `log-full` holds FAILED.

**The connect**, from a fresh clone at M into `$NEW/deploy`, and a fresh clone at A1's M into `$NEW/a1`:
- builds `queue.tsv` and `dry.tsv` with the bound probe's own `tasks --runs $NEW/runs`. The counts must be 66 and 9,
  and the lines must equal attempt 1's except for the root path;
- runs `rs1_a1_plan.py stage --old $OLD --new $NEW`:
  - **log-dry** is copied verbatim and verified file by file;
  - **a task is done** only if it ended in attempt 1 and every product and trace sidecar it declares
    (`rs1_a1_plan.expected`) matches its line in attempt 1's `log-dry/SHA256SUMS` (a dry task) or `log-full/SHA256SUMS`
    (a full task). Its files are copied with O_NOATIME and re-hashed;
  - **every other task is todo.** Files attempt 1 left for a todo task go to `runs-attempt1/<id>/`, never to `runs/`,
    because the runner skips existing targets;
  - **expected:** 20 done tasks (9 dry and 11 full) and 46 todo tasks (178 unfolds, V_02 among them, its four products
    in `runs-attempt1/rs1_V_02/`). `plan.tsv`, `copies.sha256` and `stage.json` are written.

**2.2 The wrapper, `sbatch_rs1_a1.sh`:** `<deploy at M> <M> <root> <a1 tools> <A1's M>`.
- **Two clones.** The tasks run from the deploy at M, the bound RS1 code at the dry run's pin. So RS1-C1's one-code rule
  and the analysis's dry = full pin rule both hold. The plan module comes from the A1 clone. Both clones must be clean
  at their pins. sbatch runs a copy of the script, so neither path is derived from the script's own location.
- **Refusals before anything is written:**
  - an existing `log-full`;
  - no dry DONE at M;
  - a plan whose task count differs from the queue's;
  - any staged file that no longer verifies (`rs1_a1_plan.py verify`);
  - a missing lightgbm or scipy.
- **Only the todo tasks run,** on 8 lanes.
- **The teardown guard** (the director's ruling):
  - a task exits 1, never 255, so xargs keeps launching;
  - **a teardown crash** is a non-zero exit after every file the task declares exists. The wrapper records
    `<id>.teardown` with the exit code, moves those files to `runs-teardown/<id>/`, and recomputes the task once. The
    re-run's files are used, and a bitwise comparison of `xsec_flat` and `xtrue_flat` is recorded;
  - **a failure before every file exists** is a failure, `<id>.failed`;
  - **a second crash** is a failure.
- **DONE** is written only if every queue task is staged and verified, or ended. It carries `mode` full, the pin, A1's
  pin, the counts, and the teardown list. Otherwise FAILED is written, listing the failed tasks.

**2.3 V_02 (the director's ruling 4).** V_02 is recomputed. Its four new products are compared bitwise with attempt 1's
in `runs-attempt1/rs1_V_02/`, as a free determinism check, and the result is recorded in the receipt. The re-run's
products are the ones used. A difference is reported, and no tie-break is applied.

## 3. Compute

**The work:** 46 tasks, 178 unfolds.

**The projection:** the dry run's per-arm walls from #891, packed in queue order on 8 lanes with 120 s of setup, give
**3.43 h**. The limit is the smaller of 0.9 × 4.5 h and 0.9 × (8.0 − 1.24), which is 4.05 h, so the resume fits.

**The submission:** `--time=4:30:00` on one exclusive node. The charge ceiling is 4.5 node-h against the 6.76 remaining
of RS1's 8.0 cap.

**Every connect:** the cov2d `squeue` check recorded, iris, ssh's rc read unpiped, the sha256 sent to the director
first, scontrol's TimeLimit checked, and the receipt committed as a PR.

## 4. Code and tests

| file | role |
|---|---|
| `nd-unfolding/rs1_a1_plan.py` | `stage`, `verify`, `expect` |
| `nd-unfolding/sbatch_rs1_a1.sh` | the resume wrapper with the guard |
| `nd-unfolding/tests/test_rs1_a1.py` | 17 tests: staging in each direction, the plan, the guard's three REQUIRED directions, the refusals, and the bound analysis accepting the fresh root's receipts |
| `nd-unfolding/tests/rs1_a1_mutation.py` | the harness: REQUIRED mutants for the guard (a teardown read as a failure, a pre-write failure read as a teardown, a second crash accepted, xargs aborting, crashed files kept), and one per staging rule and refusal |

**ENS1 carries the same guard** in `sbatch_ens1.sh` (#899), with its own REQUIRED mutants (the director's ruling 5).

## 5. Open items

1. **The refactor (deferred, the director's ruling 3).** The right fix is to move `refine_stay_positive` and
   `_make_bkg_classifier` out of the ROOT-importing driver, or to load them without importing ROOT. That touches code
   FD-STAB, RS1 and ENS1 are bound to, so it is a follow-up item with its own binding, not part of this resume.
2. **Should the crash recur in the resume,** the guard recomputes the task once. Recurrent crashes would be reported
   with their tasks and exit codes, unrepaired.
