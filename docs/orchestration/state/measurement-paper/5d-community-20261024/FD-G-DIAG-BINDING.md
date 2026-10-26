# Binding: G-DIAG, the descriptive breakdown of Stage G's χ² (2026-10-26)

**By** the paper-tighten lane, as director.

**Under:**
- Joseph's approval of Stage G, `DECISION-20261025-joseph-f0-limitation-stage-g-and-paper-scope.md` (PR #364), item 2,
  which covers this read of the data against the generators;
- `FD-F0b-AND-G-BINDING.md` (PR #376), and Stage G as reported, `FD-G-REPORT.md` (PR #378).

**Binds** [`FD-G-DIAG-DECLARATION.md`](FD-G-DIAG-DECLARATION.md) with its amendment 1, merged in PR #379. Its file
sha256 begins `8cf8f16048e4f45b`.

**What led to it.** Under the reported covariance, every prediction's χ² is large, but no single cell pull exceeds
4.4 in magnitude. The prior, MnvTune v1, has the largest χ². The director asked for a breakdown showing which
directions in the cells carry the χ² and which covariance blocks set them, before anyone reads it.

**MEASURES:** nothing. It authorizes the declaration's two login-node steps, §2.1 and §2.2, at 0 node-h.

**CANNOT AUTHORIZE:**
- a new statistic, or an alternative to Stage G's reported χ²;
- a claim, a reading or printed wording, which are Joseph's;
- splitting S1's groups or C_resp's species, which is a follow-up the director decides;
- any Slurm job, GPU use, premium QOS or write to CFS.

## 1. The bound code

**The deploy pin** is `d02ce2f21818963fca5836e4dc4462dd81ad6175`, main after PR #379.
- `B=/pscratch/sd/j/josephrb/fd-g-diag-20261026` and `D=$B/deploy/d02ce2f2`.

**At this pin, the director checked** that the §8 digests match. They begin:
- `fd_g_diag.py` `7c161280`, `test_fd_g_diag.py` `870564f5`;
- `fd_g_compare.py` `0a3c09cd`, `test_fd_g_compare.py` `b4d0ff26`, unchanged;
- the input readout `fd/readout/fd_g_readout.json` `75a9ddee`, Stage G's.

**The director ran the declared test modules** at the PR head `91001a35`, locally with `-B`:
`test_fd_g_diag test_fd_g_compare test_s1_assemble test_s1_scripts_isolated`, **Ran 90 tests, OK**.

## 2. Rulings on the declaration's §7

As relayed on 2026-10-26 and recorded in the declaration's amendment 1:
1. **Relative-to-f units are the reading.** Absolute units are reported in full and labelled "the same χ² decomposed
   in absolute units (different modes)". The reasons:
   - the cells differ in rate, so absolute modes are dominated by the highest-rate cells;
   - the uncertainty model is built in relative terms;
   - a mode's relative σ compares directly with the per-cell σ.
2. **Shape-only is not decomposed.** The report states total − shape-only for each prediction.
3. **S1's seven groups** are the blocks, with their members listed.
4. **C_resp is one block,** as adopted.
5. **The removal records carry χ², ndf and the condition number, and no p.** A p on a matrix that is not a reported
   uncertainty would be read as an alternative result. A test asserts the key set.
6. **The ridge** is 10⁻¹⁰ × the mean diagonal, in each unit.
7. **`methods_disagree` is the numerical-artefact signal.** `ridge_sensitive` means sensitivity to conditioning. The
   report does not call a ridge-sensitive χ² an artefact.
8. **The matrix decomposed is M = C + V_g,** Stage G's comparison matrix.

## 3. Conditions

1. **§2.1, deploy and tests,** exactly as declared, with `<pin>` = `d02ce2f2…`.
   - `$B` must not exist before `mkdir`.
   - It must show HEAD equal to the pin, porcelain 0 before and after, the §8 digests, and `tests rc=0` with
     "Ran 90 tests". Anything else is a STOP.
2. **§2.2, the breakdown,** after §2.1. The argv is exact, with Stage G's five extra-block arguments and role `adopted`.
   - Exit 0 proceeds. Exit 1, 2 or 124 is a STOP, reported unrepaired.
   - D5 and D7 are part of the run: Stage G's reported χ² must be reproduced, and every breakdown's own χ² must equal
     it to 10⁻¹⁰.
3. **No step is rerun or repaired** without the director.
4. **The report is `FD-G-DIAG-REPORT.md`, opened as a PR to the director.** It follows rulings 1, 2 and 7. For each
   prediction, it carries:
   - the mode counts at 50/90/99 %;
   - the top three modes, with their relative σ and block shares;
   - the removals table;
   - the stability flags.

   It gives numbers only. The results index is regenerated in-branch under the standing ruling of 2026-10-26, if the
   readout enters the population.
5. **Ledger:** rows in `fd/LEDGER.tsv` for both steps.
6. **Pre-binding receipts:** the login37 test logs may be committed as receipts of the tests only, and the scratch
   clone removed.

The steps may start once this record is on `main`.

## Not changed

- Stage G's readout and report; the S1 covariance, C_model,5D, C_resp, R00–R15 and κ = 1.
- `fd-g-diag-20261026` joins the pscratch directories whose retention is raised before 2026-11-20.
- Claims, KI-85 and publication are Joseph's. Nothing is submitted, deposited or tagged.
