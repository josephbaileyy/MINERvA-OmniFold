# COV2D addendum A4, phase S for AR23: the score record (2026-11-07)

**By** the `cov2d` session. This ran under COV2D-BINDING-2 addendum A4, and under addendum A5's ruling 5 ("AR23's phase S
may run now at M = `ac25b665`"), with the director's go for `connect-s-AR23.sh`. The go carried one condition, met
before launch: #889 (A5) was merged on origin/main.

**M = `ac25b66533788ceb18b1d4e5add259c53b216669`.** `--null-digest` was
`80274e52c23365e5c6f84fad977576e54507bf186e1d04a8da8d596a75b0ac76` (`../null_AR23.json`, on main by #888).

- **MEASURES:** AR23's phase S (`COV2D-ADDENDUM-A4.md` §4): the grade of the 300 toys, §9.9 on the toys, and §6's
  readouts, in `../score_AR23.json`.
- **CANNOT AUTHORIZE:** any outcome sentence.
  - The COV2D outcome record is the director's. It is written after G18's phase S at A5's M, covering both tunes under
    COV2D-DECLARATION.md §12-§13.
  - This README states the record's fields and draws no reading from them.

**Result: `COV2D-SCORE AR23 UNDER-COVERS`, rc 0** (`PHASE-S AR23 UNDER-COVERS rc=0`).

## The record

`../score_AR23.json`: sha256 `fe5263e904f65892ce26b75fb279441230713c38675c2a3615c59d561c4f5ce1`, 101,696 bytes, the same
as the node's (MATCH in `launch-sAR23.out.txt`).

**Its fields, as recorded:**
- `truth` AR23; `M` as above; `null_digest` as above; `ref` origin/main; `verdict` UNDER-COVERS; `stop` [];
  `controls_failed` []; `pins_checked` true.
- **§9.9 on the 300 toys:** `problems` []. The `code` is the same driverSha256 (`938c53c5…`) and omnifoldHelperSha256
  (`e9623412…`) as both null records.
- **Atime:** 304 checked, `atime_moved` [].
- **The open audit:** 316 guarded opens, 314 distinct, all 316 with the O_NOATIME bit; `refused` []; 1,259 opens in all.
- **`truth_lambda_inequality`:** holds in 300 of 300; `decisive` false (A4 §7). Its operands' digests are recorded.
- **`grade`:**
  - `verdict` UNDER-COVERS; `ndf` 204;
  - `joint_count` 0 and `k_joint` 190, so `joint_flag` is true;
  - `flagged_cells` [29, 56]:
    - counts 164 and 148, against `k_cell` 174 each;
    - `s_c` 1.165 and 1.316;
    - `attribution` R29 and R56 are each `driven_by` "bias", with `pull_mean` −0.851 and 1.039 and `pull_sd` 0.636 and
      0.709;
  - `chi2_mean_over_ndf` 16.55 (se 0.17);
  - `weakened_share` 0.263; `outlier_cell` 216 has count 247 against `k_cell` 173 and is not flagged;
  - `size`: joint 0.0175, per-truth union bound 0.0348.
- **`cross_term`:** max/σ 0.0516, median/σ 0.0022, p90/σ 0.0111.
- **`readouts`:** `spread_alone`, `bias`, `predicted_offset`, `leave_out_mec`, `realization_check`,
  `clipping_residual`, in the record.
- **The Cholesky check:** at ndf 204, grade's Cholesky cross-check does not run (`fd_1b_mc.py:663`; addendum A5).

**The results index.** `tools/registry/results_index.py` classes this record `included` (24 rows; its keys tokenize to
bias, pull_mean and pull_sd). This commit carries the regenerated `RESULTS-INDEX.tsv`, `RESULTS-POPULATION.tsv` and
`docs/analysis-note/records_results_index.tex`, whose row reads status "unreviewed". It is committed on the director's
option (a) of 2026-11-07.

## The connect

- **The script:** `connect-s-AR23.sh`, sha256 `c71883a09433504839f144f96bb62d42a3c05a17257467c3fa4cebff2d0e1fe0`. The
  director had it before launch.
  - It differs from G18's (`../../G18/phase-s-1-invalid/connect-s-G18.sh`) in lines 16-17 only (T, D); see
    `connect-s-G18-to-AR23.diff.txt`.
  - The launcher is `2c9a5de8…`, as receipted in `../../G18/phase-s-1-invalid/launch-s5-s.diff.txt`.
- **The condition (`wait-889-sAR23.sh`, `wait-889.log.txt`):** the script polled every 60 s. At 18:22:33Z it found #889
  MERGED as `fe6b25e7…`, that commit an ancestor of freshly fetched origin/main, and COV2D-BINDING-2.md there naming
  addendum A5. Only then did it run the launcher.
- **The fence (`fence.txt`):** clear at 2026-11-07T18:22:40Z on login02, with squeue empty and no unended cov2d job in
  sacct.
- **Staging (`staged_sha.txt`):** DIGEST_MATCH. Launched at 18:22:58Z (`launch.txt`).
- **The run (`connect-s-AR23.log.txt`, `score_AR23.log.txt`):**
  - **Deploy:** a fresh clone at M in `/dev/shm`, porcelain 0, `READOUT-SHA OK`, `origin/main=fe6b25e7…`, and
    `NULL-ON-MAIN OK 80274e52…`.
  - **MAT:** pinned (`{"mat_setup_scripts": 6, "mismatches": 0}`), with the MnvH1D preflight.
  - **Interpreter:** Python 3.11.14, numpy 1.26.4, ROOT 6.28/12.
  - **Time:** elapsed 0:13.70, max RSS 0.40 GB, exit status 0.
  - **After:** porcelain 0, HEAD = M, blobs unchanged. The clone and `tmp` (with the toy copies) were removed, rc 0.
- **Removal (`removal.log.txt`):** the launcher listed `out/` (`out_list.txt`: `score_AR23.json`), hashed and fetched the
  five files (5 MATCH), then removed the staged script and the directory, each with rc 0.
- **Not shown:** the 27 ROOT rootmap warnings, which are in `score_AR23.log.txt`.
- **0 node-h:** a login node, no job.

## Files

- `../score_AR23.json`;
- `connect-s-AR23.sh`, `connect-s-G18-to-AR23.diff.txt`, `wait-889-sAR23.sh`, `wait-889.log.txt`,
  `launch-sAR23.out.txt`;
- `fence.txt`, `staged_sha.txt`, `launch.txt`, `out_list.txt`, `removal.log.txt`;
- `connect-s-AR23.log.txt`, `score_AR23.log.txt`, `blobs.before.txt`, `blobs.after.txt`.
