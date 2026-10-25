# Binding: F0, the re-grade of existing (e) fake-data products on the 16 H2 cells (2026-10-25)

**By** the paper-tighten lane, as director.

**Under:**
- Joseph's approval, `DECISION-20261025-joseph-approve-5d-fd-f0.md` (PR #354);
- `FD-PLAN.md` (PR #352) and `FD-DIRECTOR-RULINGS.md` (PR #353).

**Binds** [`FD-F0-DECLARATION.md`](FD-F0-DECLARATION.md), merged in PR #357. Its file sha256 begins
`f60336d48c163acb`.

**MEASURES:** nothing. It authorizes the two login-node steps of the declaration's §2, at 0 node-h.

**CANNOT AUTHORIZE:**
- Stage G, F1, F1-W or any merge;
- a claim or printed wording;
- any Slurm job, GPU use, premium QOS or write to CFS.

## 1. The bound code

**The deploy pin** is `7fad6e8335003dd1466b78517478f88b80eea487`, main after PR #357.
- So `D=$B/deploy/7fad6e83`, with `B=/pscratch/sd/j/josephrb/fd-f0-20261025`.
- At this pin, the director checked that every digest in the declaration's §8 matches. The values begin:
  - `fd_f0_regrade.py` `05f9161c`;
  - `test_fd_f0_regrade.py` `ef2cacd7`;
  - `s1_assemble.py` `b157250a`;
  - `s5p_stage1_inspect.py` `26569afc`;
  - `h2_definition.json` `b6790761`;
  - `stage0_preserve.sh` `27ccc04a`;
  - `fd/F4-PRESERVE-INVENTORY.sha256` `c3c245cf`.
- The director ran `test_fd_f0_regrade`, `test_s1_assemble` and `test_s1_scripts_isolated` at the PR head `40427c14`,
  locally with `-B`: **60 tests, OK**. The pin's tree is identical to that head's: `git diff 40427c14 7fad6e83` is empty.

## 2. Rulings on the declaration's §7

All eleven items are **accepted as declared.** Four carry a reason:

1. **Item 1, control 6.** It reproduces the recorded floor, 3.2179640496732276e-05, to 10⁻¹². BUILD-REPORT's
   "at most 3.2e-5" is a rounding of that value, and an exact reproduction fails closed on any change. This corrects
   FD-PLAN §3.5 item 6, which was written from the rounded figure.
2. **Item 2, the per-experiment table holds r only.** That is consistent with ruling 6.
3. **Item 6, the 288 / 18 line stays,** labelled "read by group, never pooled", beside the group counts.
4. **Item 11, control 7's lean toward failing.** It is not corrected, because the rule is FD-PLAN's. It is reported with
   `row4_noise_trace_share`. If it fails, row 6 is descriptive, and the report says so.

**Accepted as disclosed:** before binding, the control 2 probe read only `meta` and the `.npy` headers of the real
products. It computed no cell value. Like the plan's header reads, it is a scoping read.

## 3. A ruling made in advance: the per-experiment table

**The problem.** The readout records the sha256 of `fd_f0_experiments.npz`. If `verify_receipt_artifacts.py` then
requires that file to be obtainable, the report's commit fails on it.

**The ruling, in advance, by the S1 precedent** (`S1-DIRECTOR-RULINGS.md` §1 item 5): if the check flags the table,
track it with `git add -f` in the readout's companion directory, `fd/readout/fd_f0_readout/`. The conditions:
- its sha256 equals the readout's value and the pscratch source's;
- it holds relative residuals only, and the leak guard has passed over it.

**If the check does not flag it,** the table stays on pscratch as declared.

## 4. Conditions

1. **§2.1 deploy and tests,** exactly as declared.
   - If any condition fails, it is a STOP: HEAD, porcelain 0 before and after, the §8 digests, `tests rc=0` with 60
     tests.
2. **§2.2, the HPSS copy,** after §2.1.
   - Before starting, `hpssquota` must show at least 1 GiB free.
   - Run it detached, as declared.
   - Any non-zero `rc`, including 3 (control 0) and 124, is a STOP.
3. **§2.3, the re-grade,** after §2.2 exits 0. The argv is exact.
   - Exit 0 proceeds.
   - Exit 1, 2, 3 or 124 is a STOP, reported unrepaired. Exit 3 is the leak guard.
4. **No step is rerun or repaired** without the director.
5. **Ledger** both steps in `fd/LEDGER.tsv`.
6. **The report is `FD-F0-REPORT.md`, opened as a PR to the director.** It carries:
   - the deploy log;
   - the preserve receipts and `hsi ls -l`;
   - each control's outcome;
   - the readout's group counts, with their denominators and Gaussian references;
   - the per-truth χ² and its p, and the model-only and in-sample variants as labelled;
   - control 7's result, with `row4_noise_trace_share`.

   It carries no f, no absolute cell value and no f − g. It draws no conclusion about publishability, a limitation, or
   any paper statement; those are proposed by the director to Joseph.

The steps may start once this record is on `main`.

## Not changed

- The S1 covariance, C_model,5D, R00–R15, κ = 1, the route decision, and FD-PLAN's statistics. Control 6's bound is the
  one exception, and §2 item 1 rules on it.
- Claims, KI-85 and publication are Joseph's.
