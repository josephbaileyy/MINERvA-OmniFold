# S2R: the job and the fetch (receipt; tier3-design, 2026-11-24)

**Verdict: FAIL**, under `../S2R-DECLARATION.md` §3 as bound by S2R-BINDING-1 (#1307, merge
`6174986ebb554371de51b3525cc7b691b4051d8d`). The director accepted it on 2026-11-24.

**Consequence**, per the director's ruling under binding ruling 6 and the time box: the current estimator, E_R / B0,
is **frozen** for the (b) design. Nothing reruns S2R.

## The rule and the six numbers (k = 5; bar 0.05; `fetch-records/read/readout.txt`)

| truth | ρ_B0(5) | ρ_S2R(5) | Δ | bar: ρ_S2R(5) ≤ ρ_B0(5) − 0.05 | clears |
|---|---|---|---|---|---|
| A7_gibuu | 0.125000768884699 | 0.11729003297639137 | −0.00771 | ≤ 0.0750 | False |
| q3 | 0.17852905299277708 | 0.16118656821394617 | −0.01734 | ≤ 0.1285 | False |

- The nominal truth is not flagged under S2R (`nominal flagged False`).
- The S2R trajectory to k = 20 and the flags at the two truths are printed in `readout.txt`. They are descriptive only:
  they support no claim and no change to the bar (the director's ruling).
- This receipt draws no cause.

## The reproduction control, passed before any reading was used (`fetch-records/log/pair.json`)

- **C-PAIR:** B0's k = 5 unfold is bitwise equal to FD-PRR's B0 product at nominal, A7_gibuu and q3, with 0 cells
  differing. It ran at FD-PRR's 32 threads and seed 42.
- **C-X:** 6 of 6 bitwise.
- **C-ONE:** S2R and B0 agree at k = 1 to 2.2e-16.
- **C-ARM** (readout evidence): 20 relative fits in each S2R task, a max round trip of 5.6e-16, and 0 rows saturated.
- **C-CT:** pass.

## The submit connect (`session-submit/`, `fetch-records/logs/connect-submit.log.txt`)

- **On the director's GO,** with the launcher, submit and fetch connects taken by `git show 6174986eb:…`, shasum
  f8cd325d, fa3fbaf7 and b5c9f5bc.
- **Acks** (each UTC time from the peer's `date -u`): cov2d 19:12:18Z (naming the three FD-PRR inputs),
  director-helper-3 19:12:33Z (IBUB 61924744), limitation-resolver 19:12:38Z.
  - The window ended at 19:27:18Z: the oldest ack + 900 s, computed with date (`lane/submit-wend.txt`).
  - limitation-resolver was told right before the connect, and all three got END messages after it.
- **login38, 19:13:18Z to 19:15:52Z.** The /dev/shm copy was checked at fa3fbaf7 on the node; ssh rc 0, script rc 0,
  done 0. On the node:
  - the fence (sacct) was clear;
  - iris gave m3246 a balance of 608.7 node-h (half 304.4 ≥ the 1.0 cap);
  - the clone at M = `4017c0825444c4e88742801653bf088075c197ed` was clean, and the 8 bound digests and the declaration
    (16c7f5fb…) were OK;
  - test_s2r.py ran 58 OK;
  - the pins check passed for all 8 inputs: each was read once through dd iflag=noatime, its sha256 OK, and its stat
    unmoved (`logs/pins.tsv`);
  - lightgbm was 4.6.0, and the limit 1:00:00;
  - the Slurm option variables left numbered 0; sbatch rc 0;
  - scontrol showed TimeLimit 01:00:00 and no array fields.

## The job (sacct, `lane/watch-s2r.log.txt`)

- **sacct:** `61935360|s2r_run|COMPLETED|0:0|2026-11-24T11:42:33|2026-11-24T12:13:51|1878|nid005671` (times PST).
- **The charge:** 1 node × 1,878 s = **0.522 CPU node-h**, against the 1.0 cap. It goes on its own CPU line.
- **The job log** (`logs/s2r_run_61935360.out.txt`): the queue ran 19:43:11Z to 20:13:43Z, 6 lanes, rc 0, then "done".
  `log/DONE` reads `{"tasks": 6, "ended": 6, "rc": 0, "job": "61935360"}`.
- **Task wall** (`log/tasks/*.time`):

  | task | wall | budget |
  |---|---|---|
  | B0 nominal | 474 s | 700 s |
  | B0 A7_gibuu | 574 s | 700 s |
  | B0 q3 | 625 s | 700 s |
  | S2R nominal | 1,585 s | 2,100 s |
  | S2R A7_gibuu | 1,572 s | 2,100 s |
  | S2R q3 | 1,831 s | 2,100 s |

  The largest max RSS was 14,413,496 kB (13.7 GiB), S2R q3.
- **The watch** was sacct only, every 10 minutes from login38, with no squeue.

## The fetch connect (`session-fetch/`)

- **Acks:** cov2d 21:11:27Z, limitation-resolver 21:11:30Z, director-helper-3 21:11:44Z. The window ended at 21:26:27Z
  (`lane/fetch-wend.txt`). limitation-resolver was told before the connect, and ENDs were sent after it.
- **login38, 21:12:02Z to 21:12:31Z.** ssh rc 0, script rc 0, done 0.
  - `fetch-records.tar` sha256 `bff9f7c1ccf806df1ba5ead55f2a71f278d3bafcd98c4ab32843c4081cc50c23`, 266,240 B, equals
    the node log's. It is not committed; its contents are extracted under `session-fetch/records/fetch-records/`.
  - RECORDS.SHA256SUMS checks under `shasum --strict`: 53 lines for 53 files (`records-check.txt`).
- **The products** (`runs/*.npz`) stay on pscratch, with their sha256 in `log/SHA256SUMS`. The root
  `/pscratch/sd/j/josephrb/s2r-20261124` is static; removing it is Joseph's call.

## Readout digests

- `read/readout.json` sha256 `b829c3ec5e4313f7be9e08d6cf17679c2ce291271c2baefdb3e6bb41b32878ad`.
- `read/readout.txt` sha256 `432d2fdf3db5c3f708bc3a2ceafc8e8fae28740c3a55bb56d04a81d281d611df`.

## The regenerated index files

`RESULTS-INDEX.tsv`, `RESULTS-POPULATION.tsv` and `docs/analysis-note/records_results_index.tex` are as
`tools/registry/results_index.py --write` generated them. readout.json joins the results population with one metric
row, `controls/C-CT/closure_nuwro_z_abs` = 0. That is FD-PRR's C-CT control (the grade matrices reproduce F0b's
`closure_nuwro` grade), not an S2R reading. The row is a generated listing marked UNATTRIBUTED, on the same path as
T3's and FD-PRR's readouts (the director's ruling of 2026-11-09, option (a)).

## Renames

27 record names that git ignores (`.log`, `.out`, `.err`) carry ".txt" here, listed in `RENAMES.tsv` with each file's
sha256. Their contents are unchanged. `fetch-records/RECORDS.SHA256SUMS` lists the original names.

**CITABLE FOR:** that S2R ran as bound and FAILED the declared rule at both truths; the six numbers above; the
controls; the charge. **NOT CITABLE FOR:** any cause, any estimator change, any note wording.
