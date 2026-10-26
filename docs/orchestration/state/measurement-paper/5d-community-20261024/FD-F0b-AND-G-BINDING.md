# Binding: the HPSS copy of cresp.npz, the F0b re-grade, and Stage G with C_resp adopted (2026-10-26)

**By** the paper-tighten lane, as director.

**Under:**
- Joseph's adoption of C_resp, `DECISION-20261026-joseph-adopt-cresp.md` (PR #374), items 2–4;
- Joseph's approval of Stage G, `DECISION-20261025-joseph-f0-limitation-stage-g-and-paper-scope.md` (PR #364), item 2;
- F0 as bound and reported: `FD-F0-BINDING.md` (PR #358) and `FD-F0-REPORT.md` (PR #362).

**Binds,** both merged in PR #375:
- [`FD-F0b-DECLARATION.md`](FD-F0b-DECLARATION.md), file sha256 beginning `f2727f38631427fe`, for its §2.2 (the HPSS
  copy) and §2.3 (the re-grade);
- [`FD-G-DECLARATION.md`](FD-G-DECLARATION.md) as amended (amendment 1, §12), file sha256 beginning
  `e5445e254e9d18db`, for its §2.2 with the §2.3 arguments and the role `adopted`.

**MEASURES:** nothing. It authorizes four login-node steps at 0 node-h, in the order of §4.

**CANNOT AUTHORIZE:**
- F1, F1-W, any cell merge, or any change to C_e, C_model, C_resp or κ;
- a claim, a reading of any result, or printed wording, which are Joseph's;
- any Slurm job, GPU use, premium QOS or write to CFS.

## 1. The bound code

**The deploy pin** is `c4396756ec843248b00e788a20f2760b43bdc55f`, main after PR #375. Both steps deploy from it:
- F0b: `B=/pscratch/sd/j/josephrb/fd-f0b-20261026`, `D=$B/deploy/c4396756`;
- Stage G: `B=/pscratch/sd/j/josephrb/fd-g-20261025`, as declared, `D=$B/deploy/c4396756`.

**At this pin, the director checked** that every digest in both declarations' §8 matches. The values begin:
- `fd_f0_regrade.py` `37427d9d`, `test_fd_f0_regrade.py` `2e64e35a`;
- `fd_g_compare.py` `0a3c09cd`, `test_fd_g_compare.py` `b4d0ff26`;
- `s1_assemble.py` `b157250a`, `s5p_stage1_inspect.py` `26569afc`, `h2_definition.json` `b6790761`;
- `stage0_preserve.sh` `27ccc04a`;
- `fd/CRESP-PRESERVE-INVENTORY.sha256` `4d2068b6`. Its one line names `cresp.npz` at `4d8b5797…a8a20a`, the digest
  `cresp/CRESP-REPORT.md` records.

**The director ran the declared test modules** at the PR head `885ad0eb`, locally with `-B`:
- `test_fd_f0_regrade test_s1_assemble test_s1_scripts_isolated`: **Ran 69 tests, OK**;
- `test_fd_g_compare test_s1_assemble test_s1_scripts_isolated`: **Ran 49 tests, OK**. The `FAIL control …` lines
  in its output are the planted refusals that the tests require.
- The worktree's porcelain was 0 after both runs, apart from the test scratch directory.
- The pin's tree for these files is the head's: the digests above were read at `origin/main` after the merge.

## 2. Rulings on FD-F0b §7

1. **Item 1 is accepted.** The in-sample, sensitivity and eight-cell matrices carry C_resp.
   - **The reason.** Each is C^(T) with a different leave-out or on fewer cells. Since Joseph's adoption, C_resp is
     part of the reported uncertainty, so a matrix that carries C_e without it would stand for no reported total.
   - The model-only matrix stays F0's, because it carries no C_e.
2. **Item 2 is accepted.** The tool does not check that `cresp.npz` was built on S1's assembly `db000707…`.
   `CRESP-REPORT.md` records that the JSON's `meta.inputs_sha256` names that assembly, and this binding pins the npz by
   its digest, `4d8b5797…`. G0 and control 1 refuse any other file.
3. **Item 3 is made a condition.** Control 7's χ²₁₆ and every model-only grade must equal F0's committed readout
   (`fd/readout/fd_f0_readout.json`) to a relative 10⁻¹².
   - The option must not touch them, so a difference is a defect, not a result.
   - If either differs, F0b's report says so unrepaired, and Stage G does not run until the director rules.
   - Control 7 failing again, as expected, is not a STOP. It gates row 6 only, as in F0.
4. **Item 4, the report's table, is accepted.** Each column is headed by its matrix, with F0's denominators and
   Gaussian references. Any truth whose listing changes between F0 and F0b is named.

## 3. Rulings on FD-G

1. **The extra block is C_resp in the role `adopted`.** Stage G's argv is §2.2's, with these five arguments inserted
   before `--out-json`, exactly:

   ```bash
     --extra-block /pscratch/sd/j/josephrb/cresp-20261026/out/cresp.npz \
     --extra-block-sha256 4d8b579732b79cbbb8e6c9a4f6335c4bda4eae6dd4194241a0d8cd6e7ea8a20a \
     --extra-block-key C_resp --extra-block-name C_resp --extra-block-role adopted
   ```

   - **Construction record:** `C-RESP-SPEC.md` (PR #365), as built and reported in `cresp/CRESP-REPORT.md` (PR #372).
   - **Units:** the key holds `build_cresp.py`'s summed block, a 16 × 16 covariance on R00–R15 in S1's absolute units,
     the same as C_total. The declaration read its header as (16, 16) `<f8`.
2. **G's §7 rulings, as relayed on 2026-10-25 and printed in its §7, stand.**
3. **The run without an extra block is not authorized.** The variant record under `adopted` gives the comparison
   against C_total + V_g beside the reported one, so a second run would duplicate it.

## 4. Conditions and order

1. **The F0b deploy and tests** (FD-F0b §2.1), exactly as declared, with `<pin>` = `c4396756…`.
   - `$B` must not exist before `mkdir`. If it exists, STOP.
   - It must show HEAD equal to the pin, porcelain 0 before and after, the §8 digests, and `tests rc=0` with
     "Ran 69 tests". Anything else is a STOP.
2. **The HPSS copy** (FD-F0b §2.2), after step 1.
   - Before starting, `hpssquota` must show at least 1 GiB free, and `hsi ls -d /home/j/josephrb/mnv-5d-cresp-20261026`
     must still return HPSS_ENOENT.
   - Run it detached, as declared. Any non-zero `rc`, including 3 and 124, is a STOP.
   - After PASS, delete only `$B/preserve/stage0-inputs.tar`, as declared.
3. **The F0b re-grade** (FD-F0b §2.3), after step 2 exits 0. The argv is exact.
   - Exit 0 proceeds. Exit 1, 2, 3, 4 or 124 is a STOP, reported unrepaired.
4. **F0b's report** is `FD-F0b-REPORT.md`, opened as a PR to the director. It carries:
   - the deploy log, the preserve receipts and `hsi ls -l`;
   - each control's outcome and the §2 item 3 equality check;
   - the §7 item 4 table;
   - the per-truth χ² and p under C^(T) + C_resp, beside F0's, with the in-sample, sensitivity, model-only and
     eight-cell variants as labelled.

   It carries no f, no absolute cell value and no f − g, and it draws no conclusion.
5. **Stage G** (FD-G §2.1 and §2.2 with §3 item 1 above) runs only after F0b's report is merged on `main`.
   - The deploy is FD-G §2.1 at this pin, and must show "Ran 49 tests". `$B` must not exist before it is made.
   - Exit 0 proceeds. Any other exit is a STOP.
   - F0b's grades do not gate Stage G. Joseph accepted the fake-data limitation and approved G (PR #364). Only a STOP
     in steps 1–4, or a failure of §2 item 3, holds it.
6. **Stage G's report** is `FD-G-REPORT.md`, opened as a PR to the director.
   - It carries the deploy log and the readout `fd-g-readout/2`, with every χ² beside its matrix's name, size and rank.
     The reported comparison (C_total + C_resp + V_g) and the variant without C_resp are both quoted, each labelled.
   - It draws no reading. The interpretation is Joseph's.
7. **No step is rerun or repaired** without the director.
8. **Ledger:** each step in `fd/LEDGER.tsv`, with host, start, end, rc and wall.
9. **Pre-binding receipts.** The login37 test logs in `$P/fd-cresp-testcheck-20261026/` may be committed as
   pre-binding receipts, with Stage G's earlier ones, and the test clones then removed. They are receipts of the
   tests only, not of any run.

The steps may start once this record is on `main`.

## Not changed

- The S1 covariance, C_model,5D, C_resp, R00–R15, κ = 1, the route decision, FD-PLAN's statistics and triggers, and
  F0's readout and report.
- **Retention.** `fd-f0b-20261026` and `fd-g-20261025` join the pscratch directories whose retention is raised before
  the 2026-11-20 purge window. Their readouts go to git in the reports, and `cresp.npz` goes to HPSS in step 2.
- Claims, KI-85 and publication are Joseph's. Nothing is submitted, deposited or tagged.
