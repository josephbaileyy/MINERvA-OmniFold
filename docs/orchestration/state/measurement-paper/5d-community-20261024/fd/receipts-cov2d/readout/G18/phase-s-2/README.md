# COV2D addendum A5: phase S for G18 at M_A5, the score record (2026-11-08)

**By** the `cov2d` session. This ran under COV2D-BINDING-2's "Addendum A5, the M line" (#911), ruling 2 (ruling 5 as
amended). The director's go named `connect-s-G18.sh` `3cd40164…`, D = `6bd5259d…`, `launch-s5.sh` `314fa64d…` and
`go.sh` `e55e174b…`, after #914 merged at `1102091d`.

**M_A5 = `b1d56e4f08e62983784e34b2278f38a09a68eca0`.** `--null-digest` was
`6bd5259d61b062af7b3a8b09af78fc544e3eba48e35a062a28fdcd923b90f6e0` (`../null_G18.json`, phase N's rerun, `../phase-n-2/`).

- **MEASURES:** G18's phase S (`COV2D-ADDENDUM-A4.md` §4) in `../score_G18.json`. That is:
  - the grade of the 300 toys;
  - §9.9 on the toys;
  - §6's readouts;
  - the A5 Cholesky cross-check of both grades.
- **CANNOT AUTHORIZE:** any outcome sentence.
  - The COV2D outcome record for both tunes is the director's, under COV2D-DECLARATION.md §12–§13.
  - This README states the record's fields and draws no reading from them.
- **Supersedes, at G18:** run 1 (`../phase-s-1-invalid/`, at M `ac25b665`). That run crashed on 1B's Cholesky
  refusal and wrote no score record.

**Result:**
- **`COV2D-SCORE G18 UNDER-COVERS`, rc 0.**
- **`A5-READING-RULE PASS`.**
- **`PHASE-S G18 UNDER-COVERS rc=0`.**

## The A5 reading rule (the M line's ruling 3), as printed (`connect-s-G18.log.txt`)

```
A5-READING score_G18.json C_T ndf=205 kappa2=949600599690.9141 tol=0.002108536899949418 cmp_tol=0.002108536899949418 max_rel_diff=2.037160451440201e-08 OK (finite, max_rel_diff <= tol, the grade used the recorded tol)
A5-READING score_G18.json C_T_minus ndf=205 kappa2=955403078851.6176 tol=0.0021214209918776596 cmp_tol=0.0021214209918776596 max_rel_diff=7.32927432078867e-08 OK (finite, max_rel_diff <= tol, the grade used the recorded tol)
A5-READING-RULE PASS
```

| grade | record key | ndf | κ₂ | tol | tol used by the grade | max_rel_diff |
|---|---|---:|---:|---:|---:|---:|
| C_T | `cholesky_check` | 205 | 9.496e11 | 2.1085e-3 | 2.1085e-3 | 2.04e-8 |
| C_T⁻ (leave-out-MEC) | `cholesky_check_minus` | 205 | 9.554e11 | 2.1214e-3 | 2.1214e-3 | 7.33e-8 |

- Both entries carry `eps` 2.220446049250313e-16.
- Both `rule` strings read `"max(1e-9, 10 kappa_2(C_T) eps)"`, the C_T⁻ entry's included. Its κ₂ is C_T⁻'s own, which
  differs from C_T's. The string is the same constant for both entries. This is recorded for the follow-up list.

## The record

`../score_G18.json`: sha256 `849766942b3ecd9e6e72fd5db9d1a59815796b3f917875f8d0122b0c639088ec`, 101,840 bytes, the
same as the node's (MATCH in `launch-sG18.out.txt`).

**Its fields, as recorded:**
- **Identity:**
  - `truth` G18; `M` M_A5; `null_digest` as above; `ref` origin/main;
  - `verdict` UNDER-COVERS; `stop` []; `controls_failed` []; `pins_checked` true;
  - `host` login02; `root` 6.28/12.
- **§9.9 on the 300 toys:** `problems` [], `products` 300. The `code` is the same driverSha256 (`938c53c5…`) and
  omnifoldHelperSha256 (`e9623412…`) as the null record.
- **Atime:** 304 checked, `atime_moved` [].
- **The open audit:** 317 guarded opens, 315 distinct, all 317 with the O_NOATIME bit; `refused` []; 1,260 opens in all.
- **`truth_lambda_inequality`:** holds in 300 of 300; `decisive` false. Its operands' digests are recorded.
- **`grade`:**
  - `verdict` UNDER-COVERS; `ndf` 205.
  - `joint_count` 0 and `k_joint` 192, so `joint_flag` is true.
  - `flagged_cells` [29]: count 148 against `k_cell` 175; `s_c` 1.347.
    - `attribution` R29 is `driven_by` "bias", with `pull_mean` −0.964 (se 0.038), `pull_sd` 0.666 (se 0.027) and
      `centred_count` 261 against `k_flag` 175.
  - `chi2_mean_over_ndf` 24.17 (se 0.37).
  - `weakened_share` 0.0488, with `weakened_pass` at 10 cells.
  - `outlier_cell` 216: count 261 against `k_cell` 173, not flagged.
  - `over_covers` true at 67 cells.
  - `size`: joint 0.0192; cells union bound 0.0171; per-truth union bound 0.0363.
- **`cross_term`:** max/σ 0.0635, median/σ 0.0022, p90/σ 0.0120.
- **`readouts`:** `spread_alone`, `bias`, `predicted_offset`, `leave_out_mec`, `realization_check` and
  `clipping_residual`, as written in the record.

**The results index.** `score_G18.json` is a JSON under `state/` with metric-named keys, as `score_AR23.json` was. This
commit carries the regenerated `RESULTS-INDEX.tsv`, `RESULTS-POPULATION.tsv` and
`docs/analysis-note/records_results_index.tex` from `tools/registry/results_index.py --write`, on the director's option
(a) for AR23's record of 2026-11-07.

## The connect

- **The script:** `connect-s-G18.sh`, sha256 `3cd401648abb6aa72b80ace1680d89124ebe6fca320c63d18259ab67f66a041d`.
  - It is the phase-S template at M_A5 (`make-connect-s5.py` writes it from run 1's template) with T = G18 and D set.
  - Its diff from run 1's `../phase-s-1-invalid/connect-s-G18.sh` (`207c797c…`) is `connect-s-G18-1-to-2.diff.txt`.
    It changes:
    - M = M_A5, D, and READOUT_SHA = `0c3ad137…`;
    - a verdict pattern for `INVALID (grade refused, …)`;
    - the A5 reading-rule block, which runs after the driver on whichever score record was written.
- **The connect's own tests:**
  - `a5-reading-test.txt` and `a5-reading-variants.py`: the rule's body on 8 synthetic records. It passes the good
    record and an ndf-204 one, and fails each of these:
    - NaN;
    - inf;
    - max_rel_diff > tol;
    - no compared values;
    - a None max_rel_diff;
    - a grade that used a different tol.
  - `a5-reading-wrapper-test.txt`: the shell block end to end, in 4 cases. These cover the PHASE-S override and the
    NOT-CHECKED branch.
  - `verdict-case-test.txt`: the verdict mapping, in 8 cases.
- **The launch:**
  - `go.sh` printed `LAUNCHER-SHA OK 314fa64d…` and `CONNECT-SHA OK 3cd40164…` (`launch-sG18.out.txt`).
  - The local run directory of run 1 was renamed `run-sG18-1` before launch.
- **The fence (`fence.txt`):** clear at 2026-11-08T03:34:48Z on login02. squeue was empty, and no cov2d job was
  unended in sacct.
- **Staging (`staged_sha.txt`):** DIGEST_MATCH. Launched at 03:35:06Z (`launch.txt`).
- **The run (`connect-s-G18.log.txt`, `score_G18.log.txt`):**
  - **Deploy:** a fresh clone at M_A5, porcelain 0, `READOUT-SHA OK 0c3ad137…`, `origin/main=1102091d…`, and
    `NULL-ON-MAIN OK 6bd5259d…`.
  - **MAT:** pinned (`{"mat_setup_scripts": 6, "mismatches": 0}`), with the MnvH1D preflight.
  - **Interpreter:** Python 3.11.14, numpy 1.26.4, ROOT 6.28/12, nice 19, taskset -c 8-11, threads 1.
  - **Time:** elapsed 0:14.49, max RSS 0.40 GB, exit status 0.
  - **After:** porcelain 0, HEAD = M_A5, blobs unchanged. The clone and `tmp` were removed, rc 0.
- **Removal (`removal.log.txt`):**
  - The launcher listed `out/` (`out_list.txt`: `score_G18.json`).
  - It hashed and fetched five files (5 MATCH).
  - It then removed the staged script, the files and the directory: 8 removals, each rc 0. The closing `/dev/shm`
    listing was empty.
- **The ROOT rootmap warnings** (27 lines) are in `score_G18.log.txt`.
- **0 node-h:** a login node, no job.

## Files

- `../score_G18.json`;
- `connect-s-G18.sh`, `connect-s-G18-1-to-2.diff.txt`, `make-connect-s5.py`, `launch-sG18.out.txt`;
- `fence.txt`, `staged_sha.txt`, `launch.txt`, `out_list.txt`, `removal.log.txt`;
- `connect-s-G18.log.txt`, `score_G18.log.txt`, `blobs.before.txt`, `blobs.after.txt`;
- `a5-reading-test.txt`, `a5-reading-variants.py`, `a5-reading-wrapper-test.txt`, `verdict-case-test.txt`.
