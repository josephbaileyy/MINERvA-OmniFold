# The rebin assessment's pscratch dependency, checked by stat (the valid-region lane, 2026-11-10)

`../README.md` states one unverified dependency: that the pscratch fine-grid products a merge-only rebin would
re-aggregate still exist. pscratch purges by access time (`nd-unfolding/ref_g1/ref_g1.py:132` @ 58719d4b). This is the
check, run on the director's go for `purge_check.sh` at sha256
9503563ff189373f9c9543e60b6be0aa6a033cb607cdaeee4e0916ca83edcb9e.

CITABLE FOR: that each of the 8,795 listed files existed on pscratch at 2026-11-10T04:16-04:17Z, with the sizes and
access-time ages below.
NOT CITABLE FOR: any file's contents or digest (nothing was read); that a file will still exist later; any rebinning
decision, any V-HALF class, any cell's validity.

## What ran

- **The session.** One foreground ssh session on login37, from 2026-11-10T04:16:05Z to 04:17:55Z, with ssh rc 0 read
  unpiped (`purge-session.txt`).
  - The script was staged in /dev/shm and checked at its sha256. It removed that copy at exit.
  - The first attempt, earlier on 2026-11-10 (after 03:19Z), got ssh rc 255 with no output. The NERSC certificate had expired at
    2026-11-10T00:11Z, so nothing was staged. Joseph renewed the certificate, valid to 2026-11-11T04:15Z.
- **The method.** Stat only. Each listed path is passed to `stat -c "%s %X"` (size and access time) once, through awk.
  - stat reads no file's contents and does not move the access time.
  - No directory was listed and nothing was written on the cluster. The report went to stdout.
- **The list.** 8,795 explicit paths, embedded in the script. `make_lists.py` built them from committed records only, in
  a clean clone at 58719d4b with no cluster contact:
  - **central** (1): s5p-20260926 `runs/s2/num/data/data_b-_j-.npz`, the data central value fb5cc679.
  - **cstat** (30): `data_b21..50_j121..150`, the C_stat replicas that are not committed (`S1-REPORT.md:222-225`).
  - **f0b_graded** (221), **f0b_floor** (1), **f0b_pow** (1,147) and **f0b_cal** (7,176): F0b's inputs by its own
    selection (`fd_f0_regrade.py:560-584`, `TRUTHS`, `f4_inputs`, and `listed_set`'s manifest side without its glob).
    They are drawn from the roots in `fd_f0b_readout.json`'s argv and the committed manifests it names. The per-truth
    counts equal the readout's `n_experiments`.
  - **prr** (181): FD-PRR's route-1 products (`fd/receipts-prr/misc/cluster/log-misc/SHA256SUMS`).
  - **cpl** (38): C_PL,5D's 34 period unfolds (`fd/readout/fd_ct_5b_periods.json` inputs_sha256.unfolds) and 4 MC truths
    (`fd/receipts-ct/5b/5b-inputs-steps.tsv`).

## The result (`purge-session.txt`)

| group | listed | found | missing | bytes found | oldest access (days) | newest access (days) |
|---|---:|---:|---:|---:|---:|---:|
| central | 1 | 1 | 0 | 95,564 | 4.5 | 4.5 |
| cstat | 30 | 30 | 0 | 2,821,266 | 4.5 | 4.5 |
| f0b_graded | 221 | 221 | 0 | 40,677,480 | 9.3 | 4.5 |
| f0b_floor | 1 | 1 | 0 | 188,532 | 4.5 | 4.5 |
| f0b_pow | 1,147 | 1,147 | 0 | 212,457,483 | 9.3 | 9.3 |
| f0b_cal | 7,176 | 7,176 | 0 | 1,328,190,614 | 9.3 | 9.3 |
| prr | 181 | 181 | 0 | 33,324,255 | 0.2 | 0.2 |
| cpl | 38 | 38 | 0 | 3,898,100 | 10.6 | 10.3 |

- **All present.** All 8,795 files were present, 0 missing, about 1.62 GB in all. awk rc 0, and the check exited 0.
- **The oldest access** was 10.6 days earlier, on C_PL,5D's period files. FD-PRR's products were last read 0.2 days
  before, by the PRR read.
- **What this shows.** The merge-only route's pscratch inputs existed at the check. Its cost, and its 0 node-h
  re-aggregation, rest on files that were all present that day.
- **What it does not show.** It does not guarantee they survive. The purge is by access time, and the stat did not
  reset any clock. Its window is NERSC's policy, which this record does not quote. [INF] A rebin that waits should
  check again before it relies on these files, or copy them first.
