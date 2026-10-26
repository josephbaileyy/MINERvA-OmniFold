# DECLARATION F0b: F0's re-grade against C_total_resp, and the HPSS copy of cresp.npz (2026-10-26)

**By** the measurement session, for the director to bind.

**Under:**
- Joseph's adoption of C_resp,
  [`DECISION-20261026-joseph-adopt-cresp.md`](../../../DECISION-20261026-joseph-adopt-cresp.md) items 3 and 4
  (PR #374, main `c7d00acd`);
- the director's instruction of 2026-10-26, relayed to this session: F0b is an F0 addendum, and the HPSS copy of
  `cresp.npz` goes first;
- F0 as declared and bound, [`FD-F0-DECLARATION.md`](FD-F0-DECLARATION.md), and as run,
  [`FD-F0-REPORT.md`](FD-F0-REPORT.md).

**Declares:**
- the `--extra-block` option of `nd-unfolding/fd_f0_regrade.py`, and its tests in
  `nd-unfolding/tests/test_fd_f0_regrade.py` (class `ExtraBlockF0b`, plus one `CommittedPins` test);
- the one-line inventory `fd/CRESP-PRESERVE-INVENTORY.sha256`;
- the exact argv of the HPSS copy and of the re-grade, their order, and the readout.

**MEASURES:** nothing. Neither the copy nor the re-grade has run.
<!-- absence-ok: a scoping statement about this session's own work: the option is new in this commit, and the only cluster reads were cresp.npz's sha256 and its .npy headers (login37, 2026-10-26T08:08Z) -->

**CANNOT AUTHORIZE:**
- running anything: the director binds first;
- Stage G, which runs only after F0b's report is merged ([`FD-G-DECLARATION.md`](FD-G-DECLARATION.md) amendment 1);
- any reading of the data against a generator: F0b is fake data only;
- a claim, printed wording or a publishability conclusion, which are Joseph's.

**CITABLE FOR:** what F0b will compute, from which inputs, in which order, and what makes it stop.

**NOT CITABLE FOR:** any result.

## 0. Summary

- **What changes from F0:** the grade matrix. F0 graded each truth against C^(T) = C_e/(f fᵀ) + Σ_{j ≠ own(T)} s_j s_jᵀ.
  F0b grades it against C^(T) + C_resp/(f fᵀ).
  - The leave-out still acts on C_model only. C_resp is never left out.
  - The in-sample, sensitivity and eight-cell matrices also carry C_resp, since each is C^(T) with a different
    leave-out or on fewer cells (§7, item 1).
  - **The model-only matrix is F0's,** C_stat/(f fᵀ) + Σ_{j ≠ own} s_j s_jᵀ. It carries no C_e, so no C_resp.
- **What does not change:** the 8,545 products and their digests; the estimators and the noise of each mean; controls
  0–8; the triggers (|z| > 2 per cell, P(χ²₁₆ > χ²) < 0.01 per truth); the groups and denominators; the leak guard;
  P_FLOOR. Without `--extra-block` the tool is F0's, and a test shows its readout has F0's keys exactly.
- **Control 7 is reported again.** It grades O_MnvTune − O_GENIE CV against their noise alone, with no covariance
  block, so C_resp cannot enter it. **The expected result is F0's, χ²₁₆ 245.74, FAIL**, and row 6 stays descriptive.
  The report says so and quotes the number.
- **The HPSS copy:** `cresp.npz` (12,952 B) is not byte-reproducible (`CRESP-REPORT.md`, "Retention"), so it is copied
  first. The copy uses the committed Stage 0 preserve script, unchanged, over a one-line inventory, and is checked by
  hashverify and a retrieval.
- **Cost:** 0 node-h. Two login-node steps, no Slurm job. pscratch gets about 1 GB for the deploy and under 10 MB
  for the outputs. HPSS gets about 20 kB. Nothing goes to CFS.
- **The order:**
  1. deploy, with the tests in the deploy (§2.1);
  2. the HPSS copy (§2.2);
  3. the re-grade (§2.3);
  4. the report, merged before Stage G runs.
- **Stop rule:** any refusal, any non-zero exit, or any step past 1.25 × its projected wall is reported unrepaired.

## 1. Inputs

All of F0's inputs, unchanged and checked as F0 checks them (`FD-F0-DECLARATION.md` §1), plus one:

| input | where | checked against |
|---|---|---|
| C_resp, key `C_resp`, 16 × 16 `<f8`, absolute units | `$P/cresp-20261026/out/cresp.npz` | `4d8b579732b79cbbb8e6c9a4f6335c4bda4eae6dd4194241a0d8cd6e7ea8a20a`, passed on the command line (control 1), as `CRESP-REPORT.md` records it |

**What the file is** (sha256 and `.npy` headers on login37, 2026-10-26T08:08Z; no values read):
- the sha256 is the report's;
- the members are `C_resp`, `C_total_resp`, the five species blocks `C_resp_{proton,meson,em,other,xtalk}` (each
  16 × 16 `<f8`) and `meta`;
- `build_cresp.py` writes `C_resp` as the sum of the four primary species, in the units of S1's C_total
  (`build_cresp.py:187-196`, at `c7d00acd`). Cross-talk is not in it.

## 2. Exact commands

**Definitions:**
- `P=/pscratch/sd/j/josephrb`.
- `B=$P/fd-f0b-20261026`. It does not exist yet (login37, 2026-10-26T08:08Z).
  <!-- absence-ok: `ls -d /pscratch/sd/j/josephrb/fd-f0b-20261026` on login37 at 2026-10-26T08:08Z printed 'No such file or directory' -->
- `D=$B/deploy/<pin8>`: a clean clone of the binding commit, which the binding names.
- `T=$D/docs/orchestration/state/measurement-paper/5d-community-20261024`.
- `PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B"`, as for F0.
- `XB="--extra-block $P/cresp-20261026/out/cresp.npz --extra-block-sha256 4d8b579732b79cbbb8e6c9a4f6335c4bda4eae6dd4194241a0d8cd6e7ea8a20a --extra-block-key C_resp --extra-block-name C_resp"`.

### 2.1 Deploy and tests (login node)

F0's §2.1, with `$B` as above and `FD-F0b-DECLARATION.md` and `fd/CRESP-PRESERVE-INVENTORY.sha256` added to the
`sha256sum` list:

```bash
mkdir -p $B/logs $B/tmp
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold $D && git -C $D checkout --quiet --detach <pin>
{ date -u +%FT%TZ; hostname; git -C $D rev-parse HEAD
  echo "porcelain_ignored_lines $(git -C $D status --porcelain --ignored | wc -l)"
  cd $D && sha256sum nd-unfolding/fd_f0_regrade.py nd-unfolding/tests/test_fd_f0_regrade.py nd-unfolding/s1_assemble.py \
    nd-unfolding/s5p_stage1_inspect.py nd-unfolding/pv-ladder/readouts/h2_definition.json \
    docs/orchestration/state/measurement-paper/5d-design-20261023/stage0/stage0_preserve.sh \
    docs/orchestration/state/measurement-paper/5d-community-20261024/fd/CRESP-PRESERVE-INVENTORY.sha256 \
    docs/orchestration/state/measurement-paper/5d-community-20261024/FD-F0b-DECLARATION.md; } > $B/logs/deploy.log 2>&1
cd $D/nd-unfolding/tests && TMPDIR=$B/tmp env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -B -m unittest \
  test_fd_f0_regrade test_s1_assemble test_s1_scripts_isolated > $B/logs/deploy-tests.log 2>&1; echo "tests rc=$?" >> $B/logs/deploy.log
echo "porcelain_ignored_lines_after_tests $(git -C $D status --porcelain --ignored | wc -l)" >> $B/logs/deploy.log
```

**It must show:**
- HEAD equal to the pin;
- 0 porcelain lines before and after the tests;
- the §8 digests;
- `tests rc=0` with "Ran 69 tests … OK" (47 F0/F0b + 22 S1, locally on 2026-10-26).

Anything else is a STOP.

### 2.2 The HPSS copy of `cresp.npz` (login node, after §2.1)

This is the committed Stage 0 preserve script, unchanged, over the one-line inventory. Its first step,
`sha256sum --quiet -c` of the inventory, checks the npz against `4d8b5797…` before anything is copied.

```bash
cd $B && setsid nohup bash -c "timeout 375 bash $D/docs/orchestration/state/measurement-paper/5d-design-20261023/stage0/stage0_preserve.sh \
  $T/fd/CRESP-PRESERVE-INVENTORY.sha256 $B/preserve /home/j/josephrb/mnv-5d-cresp-20261026; echo rc=\$?" \
  > $B/logs/preserve.out 2>&1 < /dev/null &
# PASS = the last line "rc=0" in $B/logs/preserve.out and "[P] ... PASS: HPSS copy verified ..." in $B/preserve/preserve.log
```

- **The inventory:** `fd/CRESP-PRESERVE-INVENTORY.sha256`, one line, `4d8b5797…a8a20a  /pscratch/sd/j/josephrb/cresp-20261026/out/cresp.npz`.
  A test (`test_the_committed_cresp_preserve_inventory_is_the_cresp_report`) checks that the path and digest are the
  ones `CRESP-REPORT.md` records.
- **What the script does:** as for F0 (`FD-F0-DECLARATION.md` §2.2): one uncompressed tar of that path; `hsi put`,
  `hashcreate`, `hashverify`; a retrieval by `hsi get`, compared to the tar by sha256; removal of the retrieved copy
  only. It never modifies or deletes the inventoried file.
- **Exit codes** (`stage0_preserve.sh`): 0 is PASS; 3: the npz no longer matches its digest; 4: tar; 5: put; 6:
  hashcreate or hashverify; 7: get; 8: the retrieved copy differs; 124: past 375 s. Any non-zero exit is a STOP.
- **Projected wall:** 5 minutes. F0's copy of 14.9 MB took 5 s (`fd/LEDGER.tsv`). The timeout is 375 s, 1.25 × that.
- **Space:** HPSS has 89.2 GiB free (`hpssquota`, 422.79 of 512.00 GiB used, login37, 2026-10-26T08:08Z). The copy
  needs about 20 kB.
- **The HPSS directory** `/home/j/josephrb/mnv-5d-cresp-20261026` does not exist yet (`hsi ls -d` returned
  HPSS_ENOENT, login37, 2026-10-26T08:08Z).
  <!-- absence-ok: `hsi -q "ls -d /home/j/josephrb/mnv-5d-cresp-20261026"` on login37 at 2026-10-26T08:08Z printed 'No such file or directory [-2: HPSS_ENOENT]' -->
- **Names:** the script calls its tar `stage0-inputs.tar` and its inventory copy `INVENTORY.sha256`. The HPSS
  directory's name identifies this copy, as for F0 and S1. The report states the mismatch.
- **After PASS:** delete `$B/preserve/stage0-inputs.tar`. Keep `stage0-inputs.tar.sha256`, `paths.list` and
  `preserve.log`. `cresp.npz` is not touched.

### 2.3 The re-grade (login node, after §2.2 exits 0)

F0's §2.3 argv, with `$XB` inserted before the outputs, the outputs renamed, and the timeout 375 s instead of 1,125 s (below):

```bash
cd $B && TMPDIR=$B/tmp timeout 375 $PY $D/nd-unfolding/fd_f0_regrade.py \
  --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --s1-npz $P/s1-20261024/s1_assembly.npz --s1-json $T/s1/readout/s1_assembly.json \
  --cmodel-npz $P/cmodel5d-20261024/out/cmodel_5d.npz --cmodel-json $D/nd-unfolding/pv-ladder/readouts/cmodel_5d.json \
  --flux-constraint $P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt \
  --d16-dir $D/docs/orchestration/state/s5p/stage3/f4 --f4-root $P/s5p-20260926/runs/s3r/f4 \
  --stage0-inventory $D/docs/orchestration/state/measurement-paper/5d-design-20261023/stage0/INVENTORY.sha256 \
  --s5e-assess $P/s5e-20260925/runs/cand/assess \
  --stage0c-sums $D/docs/orchestration/state/measurement-paper/5d-design-20261023/stage0/receipts-A/products.sha256 \
  --stage0c-root $P/5d-stage0-20261023 --pvl-products $P/pv-ladder-20261024/products \
  --s5p-sums $D/docs/orchestration/state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt --s5p-root $P/s5p-20260926 \
  $XB \
  --out-json $B/fd_f0b_readout.json --out-npz $B/fd_f0b_experiments.npz \
  > $B/logs/f0b.out 2> $B/logs/f0b.err; echo "rc=$?" >> $B/logs/f0b.out
```

- **Projected wall:** 5 minutes. F0 took 44 s on login37 (`fd/LEDGER.tsv`), and F0b adds one 13 kB read and a 16 × 16
  addition. The timeout is 375 s, 1.25 × that, so exit 124 is a STOP.
- **Exit codes:** F0's: 0 (every control passed, or control 7 failed as declared, and the readout was written); 1 (a
  control refused, or an unexpected error, with numbers redacted; nothing written); 2 (argparse, including a partial
  set of the four `--extra-block` options); 3 (the leak guard refused; nothing more written).
- **F0's outputs are not touched:** `$B` is new, and the tool refuses to overwrite.
- **What is committed** (the report's PR):
  - `$B/fd_f0b_readout.json`, as `fd/readout/fd_f0b_readout.json`;
  - `logs/{deploy.log,deploy-tests.log,preserve.out,f0b.out,f0b.err}`, `preserve/preserve.log`,
    `preserve/stage0-inputs.tar.sha256` and `preserve/paths.list`, under `fd/receipts-f0b/`;
  - two ledger rows in `fd/LEDGER.tsv`.
  The table `fd_f0b_experiments.npz` stays on pscratch; its sha256 is in the readout.

## 3. Controls

F0's controls 0–8, unchanged in order and in what they refuse (`FD-F0-DECLARATION.md` §3), with the extra block
added to two of them:

| control | added with `--extra-block` | test |
|---|---|---|
| **1** | the npz's file sha256 equals `--extra-block-sha256`; the PASS line counts 9 records instead of 8 | `ExtraBlockF0b.test_refusals` ("1 digest"); `test_stdout_with_and_without` |
| **4** | the key exists; the block is a finite 16 × 16 matrix, symmetric to 10⁻¹², and positive semidefinite (relative, to 10⁻¹²); C^(T) + C_resp/(f fᵀ) for the full C_total is positive definite | `ExtraBlockF0b.test_refusals`: missing key, asymmetric, not PSD, wrong shape, non-finite |

**Control 7 is unchanged in code:** it calls `grade(D, N_O,a + N_O,b, 0)`, with a zero covariance (`fd_f0_regrade.py`,
the offset-control loop). A test shows its readout record is identical with and without the block.

## 4. Statistics

F0's (`FD-F0-DECLARATION.md` §4), with C_x = C_resp/(f fᵀ), f S1's:

| matrix | F0 | F0b |
|---|---|---|
| grade | C_e,rel + Σ_{j ≠ own} s_j s_jᵀ | the same + C_x |
| in-sample (vertex-family truths) | C_e,rel + Σ_j s_j s_jᵀ | the same + C_x |
| sensitivity (GENIE CV, q3) | C_e,rel + Σ_{j ≠ sens} s_j s_jᵀ | the same + C_x |
| eight cells (GiBUU family) | the grade matrix on R00–R03, R08–R11 | the same + C_x on those cells |
| model-only | C_stat,rel + Σ_{j ≠ own} s_j s_jᵀ | **unchanged** |
| control 7 | the noise alone | **unchanged** |

Pulls z = b/√diag(C + N) and χ² = bᵀ(C + N)⁻¹b, ndf 16 (8 on the eight cells), as in F0. A PSD addition can only
lower every |z| and every χ², and a test checks both.

## 5. The readout

**Without `--extra-block`:** `fd-f0-readout/1`, F0's, key for key. A test compares its key sets (top level, labels,
controls and every truth record) and its matrix names with the committed F0 readout `fd/readout/fd_f0_readout.json`.

**With it:** `fd-f0b-readout/1`. That is F0's readout, with:
- `labels.what` ending "plus C_resp (F0b)", and `labels.grade_matrix` stating §4's table in words;
- `extra_block`: name, file, sha256, key, per-cell relative σ √diag(C_x), and a "declared before this run" label;
- `relative_sigma_plus_C_resp{C_e, C_total, minus_genie_mec, minus_nuwro, minus_gibuu}` and its
  `_summary_percent`, beside F0's `relative_sigma`, which is unchanged;
- each truth's `grade_matrix` and `sensitivity.matrix` ending " + C_resp".

**stdout** gains one first line, `[F0] F0b: every grade matrix carries C_resp; the model-only matrix is F0's`.
Every output still passes the leak guard first. A test runs the test's own leak scan on a run with the block, and a
planted leak with the block is still refused (exit 3, nothing written).

## 6. Code and tests

- **Changed:** `nd-unfolding/fd_f0_regrade.py` (the option, controls 1 and 4, the grades, the readout and one stdout
  line) and `nd-unfolding/tests/test_fd_f0_regrade.py`.
- **Unchanged:** `s1_assemble.py`, `s5p_stage1_inspect.py` and `stage0_preserve.sh`.

| test | what it shows |
|---|---|
| `ExtraBlockF0b` (8) | <ul><li>**by hand,** on one tree run with and without the block: every grade, in-sample, sensitivity and eight-cell z against C + C_x; the trigger counts by group from those z; the denominators are F0's; every `relative_sigma_plus_C_resp` entry and its summary; `labels.what` and `labels.grade_matrix` in full; and bias, noise, B_eff, estimator, model-only and all of `controls` (control 7 included) are identical to F0's;</li><li>the χ² and p of six truths against C + C_x + N, with N rebuilt from the products; model-only against F0's matrix;</li><li>a zero block reproduces every F0 grade exactly; a PSD block lowers every χ² and every |z|;</li><li>without the option, the readout is F0's key for key against the committed F0 readout;</li><li>stdout with and without, under `-I -B` from a cwd outside nd-unfolding, with the test's own leak scan;</li><li>a planted leak with the block exits 3, nothing written;</li><li>refusals at control 1 (digest) and control 4 (key; an asymmetric block whose symmetrized form is PSD; not PSD; shape; non-finite), each asserting the check that refused by name, nothing written;</li><li>the four options go together: each left out alone, and the name alone, exit 2</li></ul> |
| `CommittedPins.test_the_committed_cresp_preserve_inventory_is_the_cresp_report` | the one-line inventory's path and digest are the ones `CRESP-REPORT.md` records |

**Locally** (2026-10-26: Python 3.12.2, numpy 1.26.4, scipy 1.15.2), `python3 -B -m unittest test_fd_f0_regrade
test_s1_assemble test_s1_scripts_isolated` ran 69 tests, OK (47 F0/F0b + 22 S1). F0's 38 tests pass unchanged. The
cluster run is reported in the PR.

## 7. For the director

1. **The in-sample, sensitivity and eight-cell matrices also carry C_resp.** The instruction names the grade matrix
   and the model-only one. Each of the other three is C^(T) with a different leave-out, or on fewer cells, so I added
   C_resp to them too, to keep them comparable with the grade beside them. If they should stay F0's, it is a one-line
   change per matrix.
2. **What the tool checks of the block:** digest, key, shape, finiteness, symmetry, PSD, and that C_total + C_resp is
   positive definite. The last is a backstop that no test can reach, since C_total is checked positive definite
   and C_resp PSD (review B). It does not check that the block was built on S1's assembly `db000707…`. `CRESP-REPORT.md`
   records that `meta.inputs_sha256` names it, and the binding's digest pins that file.
3. **Expected unchanged:** control 7 (FAIL, χ²₁₆ 245.74) and every model-only grade. The report quotes both as
   measured, beside F0's.
4. **The report's table:** for each group, F0's and F0b's cells with |z| > 2 and truths with p < 0.01, each column
   headed by its matrix (C^(T), and C^(T) + C_resp), with the same denominators and Gaussian references. Then the
   listed truths of each. Numbers only, no reading.

## 8. Pinned bytes

Their sha256 at this declaration's commit:

| file | sha256 |
|---|---|
| `nd-unfolding/fd_f0_regrade.py` | `37427d9d9c544cc79ec1c9071c946126dd267d9f5549a1430cf8a8c77607c21e` (F0's was `05f9161c…`) |
| `nd-unfolding/tests/test_fd_f0_regrade.py` | `2e64e35a1748095fc7a610b67c50f20958490ea49e9ab0d1a66c4ddd9c170705` (F0's was `ef2cacd7…`) |
| `nd-unfolding/s1_assemble.py` | `b157250af21a2ef74e4164db6009a40ac596e225f33ac655475798ef49f613f7` (unchanged) |
| `nd-unfolding/s5p_stage1_inspect.py` | `26569afc0da46f21167e0908014712cd800c1e14ac63a4b245a0b493c76d3d71` (unchanged) |
| `nd-unfolding/pv-ladder/readouts/h2_definition.json` | `b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89` (unchanged) |
| `…/5d-design-20261023/stage0/stage0_preserve.sh` | `27ccc04a8c14d640efe1657b3d04b657f61a682db381c105daee82f901ea5d68` (unchanged) |
| `…/5d-community-20261024/fd/CRESP-PRESERVE-INVENTORY.sha256` | `4d2068b6438e7239befff9f350c3e41e15a8a96e5d3ae6f3e2365a1090128540` |
| `cresp.npz` (input, on pscratch) | `4d8b579732b79cbbb8e6c9a4f6335c4bda4eae6dd4194241a0d8cd6e7ea8a20a` |

## 9. Ledger, storage and stops

- **Ledger:** two rows in `fd/LEDGER.tsv`, for §2.2 and §2.3, with host, start, end, rc and wall. No Slurm job, so 0
  node-h.
- **Storage:** `$B` holds the deploy clone (about 1 GB), the logs, the readout and the table (under 10 MB). HPSS gets
  the tar, its `.sha256` and the inventory (about 20 kB) at `/home/j/josephrb/mnv-5d-cresp-20261026`. Nothing goes to
  CFS. `$P/fd-f0-20261025` (F0's) is not touched.
- **Stops:** any STOP in §2 or §3 is reported to the director unrepaired. Nothing is rerun without the director.

## 10. Not changed

- F0's readout, report and receipts; the S1 covariance; C_model,5D; C_resp; R00–R15; κ = 1; the route decision.
- No GPU and no premium QOS.
- Claims, printed wording and publication are Joseph's. The report gives numbers only.

## 11. Review dispositions

Two independent read-only reviews ran on the uncommitted change, together with FD-G's amendment 1 (A: against the
instruction, the decision record and the committed records; B: a code attack with 53 single mutations in a mirror).
Neither found wrong behaviour in either tool. Both choices of §7, item 1, and `--extra-block-name` were judged
defensible by A.

| # | finding | disposition |
|---|---|---|
| B-M1 | leaving out `--extra-block` itself, or `--extra-block-key` alone, was never tested (both survived) | each of the four options is now left out alone, plus the name alone |
| B-M2, A-m3 | each control-4 refusal was shown only by some check firing: removing the symmetry or PSD check survived | each refusal asserts the check by name; a new asymmetric block whose symmetrized form is PSD can be refused by the symmetry check alone |
| B-m4 | `labels.what` and `labels.grade_matrix` were never asserted | asserted in full |
| B-m5 | `relative_sigma_plus_C_resp.C_e` and the `_summary_percent` table were untested | both recomputed by hand |
| B-m6 | the C_total + C_resp positive-definite check cannot be reached by a test | kept as a backstop; §7, item 2 |
| B-m10 | the guard refuses an absolute C_resp only through its 1e-30 floor | true in physical units, where C_resp's entries are of order 1e-80; noted here |
| A-m4 | §2.3's lead omitted the timeout change, and §2.2 lumped the exit codes | both corrected |
<!-- absence-ok: these rows restate review B's mutation findings on the uncommitted test suites of 2026-10-26 (each named mutation passed every test there); they describe that suite's coverage, now closed, not the absence of a result -->

**After the fixes,** each of B's F0b survivors is caught by the test written for it, against a clean baseline in a
mirror, except the positive-definite check (B-m6).
