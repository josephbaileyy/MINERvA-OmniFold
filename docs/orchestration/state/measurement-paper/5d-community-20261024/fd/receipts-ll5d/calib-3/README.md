# LL5D ll5d_calib, run 3 (job 61075496): the step ended rc 0 and printed `verdict=CALIBRATED` (2026-11-10)

**By** the `cov2d` session. This is step 2 of the rerun Joseph decided (`DECISION-20261110-joseph-ll5d-rerun-16-cells.md`,
#1018), run under amendment A1a.2 (bound in #1021; M_A1a.2 = `639ef907250a2a7909b7b9ba89b2e85e70c9b767`). Step 1,
the vi preflight, passed (`../vicheck/`). The director's go named `connect-calib-3.sh` `e81b4787…` and `launch-ll5d.sh`
`b86004df…`. `calib3-vs-calib2.diff.txt` diffs the connect line by line against run 2's.

A calibration rerun was required because `read_calibration` refuses a record whose `code_sha256` differs from the
running code's (`ll5d.py` at M_A1a.2), and A1a.2 changed `ll5d.py`.

- **The step's own result:**
  - `calib rc=0` (`ll5d_calib_61075496.out.txt`);
  - `Exit status: 0` (`calibration.time`);
  - the printed line `LL5D-CALIBRATION verdict=CALIBRATED` (`calibration.out.txt`);
  - sacct reads COMPLETED, ExitCode 0:0, Elapsed 01:10:12 (`joblog.txt`, `watch.log.txt`).
- **The calibration record** is `calibration.json`, sha256
  `e9584339098c98ff9059279299329b1e84efca4f81583f4ebc71417b2fdb571b`.
- **Its companion `calibration.npz`** (13,951,349 bytes) has sha256
  `b31ddd12d050163396b4811705777fc1fa28f77757575af73c8dc5976b3c1a7c`, the same digest as run 2's.
  - It is not committed, because the repository ignores `*.npz`.
  - It stays at `/pscratch/sd/j/josephrb/ll5d-calib-3-20261110/calibration.npz`, and a copy whose sha256 matches is
    kept in the lane's working directory.
  - Both digests are what the gate-2 connects bind.
- **CANNOT AUTHORIZE:** the gate jobs. Each gate connect gets its own go on its own sha256.

## The comparison with run 2 (`cmp-vs-calib2.txt`, made by `cmp_calib.py`)

The director asked for a bitwise comparison with run 2 (`../calib-2/`), and a field-by-field comparison of the record
apart from `code_sha256` and timing. `cmp_calib.py` is committed here, and `cmp-vs-calib2.txt` is its output.

- **The npz:**
  - both files hold the same 14 keys;
  - the list of arrays that differ in dtype, shape or bytes is empty;
  - the two files' sha256 are equal (`b31ddd12…`).
- **The json** has 21 compared top-level fields, all byte-equal under `json.dumps(sort_keys=True)`:
  checks, constants, control_law, control_linearisation, draws_per_set, evaluations, fd_1b_c2_source, inputs,
  outputs_descriptive, power, ratio_mean_per_cell, rule, salt, schema, sd300_per_cell, seeds, sets, step, threads,
  truths and verdict. The script's list of differing fields is empty.
- **Set aside:** atime, code_sha256, peak_rss_kib and timing. These record the code and the run.
  - **`code_sha256` differs only in `ll5d.py`:** `2b0224c6fe52c5bb2d3fe64d461ac9edb80ebd191b0ab2f892dec605a0b56a14`
    here, against run 2's `b49f5d5f793265ef0cf569abe1912838cce9280e692f4dd61100d05c133aec1f`.
  - **`timing`:**
    - `seconds` 4199.32 here, against 4226.08 in run 2;
    - `set_seconds_measured` 4.149, against 4.214;
    - `projected_seconds` 2626.41, against 2657.71;
    - `budget_seconds` 16200 in both.
  - **`peak_rss_kib`:** 10,024,880 here, against 10,028,020.
  - **`atime.moved`** is empty in both, over 715 tracked files.

## The record's fields, as written (`calibration.json`)

This receipt reports the fields and draws no coverage conclusion.

- `schema` `ll5d-calibration/1`, `verdict` `CALIBRATED`, `sets` 10000, `draws_per_set` 3000, `truths` g18 and ar23.
  `evaluations` are g18/minus2, g18/all, ar23/minus2 and ar23/all.
- **The rule and the controls:**
  - `rule.s` is 0.9, `rule.measured_jointly` true and `rule.i_alone_exceeds` false;
  - `control_law.holds` and `control_linearisation.holds` are true, and `power.meets` is true;
  - `checks.D1.passes` is true, with `differ` empty.
- **Threads:** the four `threads` variables OMP, OPENBLAS, MKL and NUMEXPR are "1".
- **`code_sha256`:** `fd_1b_c2.py` is `522d7edd71643df61d0c5ef5a7488834e664eb36d20c3e0c0b46e10a5808f02f`, the vendored
  file A1a.2 left unchanged.

## The run

- **The launch** (`fence.txt`, `staged_sha.txt`, `launch.txt`, `launch-stdout.txt`, `removal.log.txt`):
  - the fence was clear on login02 at 2026-11-10T06:11:27Z (squeue empty, no cov2d job unended);
  - the staged connect's node sha256 matched the local file and the go, `e81b4787efcb79bee71bb2fa8acc1a60171229cdb6eab7fd01f8f44e0feb2dc5`;
  - it was launched detached at 06:11:51Z;
  - `/dev/shm/josephrb-ll5d-calib3.sh` was removed (`rm -f` rc 0, and the closing `ls` found nothing).
- **The connect** (`connect-calib-3.log.txt`):
  - `balance_node_h=1585.7 half=792.9 cap=148.0`;
  - `projection charged=23.087 held=0.000 this=5.0 total=28.087 cap=148.0`;
  - the deploy had porcelain 0 at `639ef907250a2a7909b7b9ba89b2e85e70c9b767`, with all 14 bound blobs OK;
  - the job script's sha256 was `52859995f5b250c6f4c41a53f7382e8908b2a5c95631f2a7134d1dc2587b3f26`, and this copy
    hashes to the same;
  - atime-pre: 749 files at 06:13:02Z;
  - submitted as job 61075496, with TimeLimit=05:00:00.
- **The job** (`ll5d_calib_61075496.out.txt`):
  - it ran on nid004828 from 06:23:51Z, and the closing line reads `end=2026-11-10T07:34:00Z`;
  - the deploy was clean with 14 blobs OK, and every thread variable was 1;
  - CPU 4598%, wall 1:10:01, max RSS 10,024,880 KiB in the timed process;
  - sacct's batch MaxRSS is 158,212,460K across its workers.
  - `env-job.log.txt` records the same two `setup.sh: No such file or directory` lines as the earlier LL5D jobs.
- **Cost:** 01:10:12 on one node, about 1.17 node-h.
- **Atimes:** atime-post was taken stat-only over the same declared inputs at 07:35:27Z on login37
  (`atime-post.raw.txt`). `atime-post.tsv` is byte-identical to `atime-pre.tsv` (`cmp` rc 0), so 0 of 749 files moved.
- **The fetched files:** all 10 match the node's sha256 (`node-sha256.txt`; `shasum -c` gives 10 OK).
  - The `.log`/`.out` files carry a `.txt` suffix here because the repository ignores those extensions.
  - The originals stay in `/pscratch/sd/j/josephrb/ll5d-calib-3-20261110/`.
  - A first fetch attempt copied only the connect log, because zsh did not word-split the file list. It was redone
    under bash before any check was read, and the 10-file `shasum -c` above is from the redone fetch.

## Files

`connect-calib-3.sh`, `launch-ll5d.sh`, `calib3-vs-calib2.diff.txt`, `sbatch-ll5d-calib.sh`, `bound.sha256`,
`connect-calib-3.log.txt`, `ll5d_calib_61075496.out.txt`, `env-job.log.txt`, `calibration.json`, `calibration.out.txt`,
`calibration.time`, `atime-pre.tsv`, `atime-post.tsv`, `atime-post.raw.txt`, `node-sha256.txt`, `fence.txt`,
`staged_sha.txt`, `launch.txt`, `launch-stdout.txt`, `removal.log.txt`, `watch.log.txt`, `joblog.txt`,
`cmp_calib.py`, `cmp-vs-calib2.txt`.
