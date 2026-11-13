# E96D under amendment 1: the dry run (GATE PASS), the full run (50 of 50) and the declared readout (2026-11-12 to 2026-11-13)

**By** the valid-region lane (director-helper-2), for the director.

**Under:**
- E96D-DECLARATION.md;
- E96D-AMENDMENT-1.md, option (a): one full job at `--time=4:15:00`, a gate bound of t ≤ 962.1 s and a cap of 5.1 node-h;
- E96D-BINDING-1 addendum A1, at M_A1 `b438ab2710b2dcfd30238107187caa3628393b11`, with the module
  `nd-unfolding/ensemble_estimator_data.py` at `414f7d35`.

**The director's GOs** were for these scripts, all in `connect/`, each run from a `/dev/shm` copy whose sha256 the
login node checked first:

| script | sha256 | what it does |
|---|---|---|
| `e96d_a1_restest.sh` | `fca284bd…` | dummy reservation-window test |
| `e96d_a1_dry_submit.sh` | `0a59335b…` | submits the dry run |
| `e96d_a1_full_submit.sh` | `3a5395bc…` | submits the full run, with the reservation-window STOP (exit 11) |
| `e96d_a1_post.sh` | `386d77a8…` | polls a job and packs its receipts |
| `e96d_a1_launch.sh` | `143f7440…` | Mac-side launcher for the scripts above |
| `e96d_a1_analyze.sh` | `76e8924d…` | the readout |
| `e96d_a1_launch2.sh` | `66d52f57…` | launcher for `analyze` and `fetch-analyze` only |

The fence scripts were `cov2d_fence.sh` `16a2a5cd…` and `hpss_launch.sh` `296ea772…`, as committed at
`fd/retention-20261110/hpss-20261111/connect/`.

**The result:**
- The dry gate passed.
- The full run ended 50 of 50 tasks with rc 0.
- The declared readout (`ensemble_estimator_data.py analyze`) ran with rc 0, and every control, A-D0 to A-D3, passed
  (`connect/analyze.session.txt:20-21`).
- The readout record is `cluster/analysis/ANALYSIS.json.txt`: 8995 bytes, sha256
  `b42208efdbb78e3c7f52174bf8ee97ea0f6414489c076efb8f39fc76ffc469e2` (`connect/analyze.session.txt:24`).
- **It was committed unread.** No session printed it, and the lane did not open it. Under BINDING-1 ruling 5, the
  director reads it once from this committed record. It enters the paper or the note only by Joseph's decision.
  <!-- absence-ok: this record's own custody statement; analyze.session.txt prints only the record's name, size and sha256 (e96d_a1_analyze.sh "never prints the record") -->

## What ran (all times UTC; Slurm's times are PST and were converted by script)

- **The restest,** 2026-11-11T12:04:45Z on login37 (`connect/restest.session.txt`): RESTEST PASS (`:11-12`).
  - Its three dummy reservations bracket the window.
  - Only `dummy_in` counted, as expected.
- **The fences.** Five `hpss_launch.sh` + `cov2d_fence.sh` sessions on login27, each `FENCE CLEAR`
  (`connect/fence-A..E.session.txt`):

  | fence | time | what followed |
  |---|---|---|
  | A | 2026-11-12T14:08:50Z | |
  | B | 2026-11-12T14:19:07Z | |
  | C | 14:30:19Z | the dry submit |
  | D | 18:25:45Z | the first full attempt |
  | E | 2026-11-13T00:32:42Z | the second full attempt; 28 cov2d/t2a rows in 14 days, none unended (`fence-E:4`) |

- **The dry submit,** login12, 14:30:31 to 14:31:24Z, rc 0 (`connect/dry-submit.session.txt`).
  - The in-script fence passed. LL5D's two gate jobs, 61078463 and 61078506, were COMPLETED (`:7-9`), which meets
    amendment ruling 6.
  - iris: the m3246 balance was 1462.4 node-h. Half of it is 731.2, against the 5.1 cap (`:14`).
  - The deploy was at M_A1 with 0 porcelain lines, and 6 bound files' sha256 matched (`:21-23`).
  - The queues were `dry.tsv` `db379681…` and `full.tsv` `3aa0bc5e…` (`:28-29`).
  - Job 61171790, TimeLimit 00:30:00 as declared (`:34-36`).
- **The dry job,** 61171790: COMPLETED, 14:33:42 to 14:49:26Z, 00:15:44 elapsed (`connect/post-dry.session.txt:9`).
  - Queue rc was 0, DONE holds 2 of 2 tasks at the pin, and gate rc was 0 (`:12-15`).
  - post-dry ran late, at 18:11:30Z, because the lane's session was paused 14:56 to 18:11Z by a usage limit.
- **The first full attempt** (full-1) was a STOP, login14, 18:25:55Z, rc 11 (`connect/full-1-STOP.session.txt`). See
  [The STOP](#the-stop-full-1). Nothing was submitted.
- **The second full attempt** (full-2), login38, 00:32:53 to 00:33:09Z, rc 0 (`connect/full-2.session.txt`).
  - The reservation window ran from now to 05:17:53Z (`:7`).
    - Its scan covered `:8-18`, and no StartTime fell inside it.
    - The next one, 2026-11-13T22:00:00Z (`:18`), is after the window.
  - The fence passed (`:20`).
  - The dry DONE and GATE were at the pin, with the sent queue (`:22-23`).
  - The deploy was at M_A1 with 0 porcelain lines (`:25`).
  - The balance was 1433.7 node-h; half of it is 716.9 (`:30`).
  - Job 61202343, TimeLimit 04:15:00 as declared (`:46-48`).
- **The full job,** 61202343: COMPLETED, 2026-11-13T02:14:17 to 05:19:27Z, 03:05:10 elapsed, on one node
  (`connect/post-full-2.session.txt:9`).
  - It ran on nid006517 with 8 lanes at the pin (`:11`), and queue rc was 0 (`:12`).
  - DONE holds 50 of 50 tasks, rc 0 (`:14`; `cluster/full/log-full/DONE.txt`).
  - post-full-1, at 04:30:23Z, found it RUNNING (`connect/post-full-1.session.txt:9-11`), and exited rc 10 as
    designed.
- **The readout,** login10, 06:05:22 to 06:05:31Z, rc 0, at 0 node-h (`connect/analyze.session.txt`).
  - Pre-checks (`:9-14`):
    - full DONE, 50 of 50, rc 0, at the pin;
    - the fence passed (it stops on our `^(cov2d|t2a|e96data|ll5d)` jobs, and the squeue was empty:
      `cluster/analysis/logs/squeue-before-analyze.txt.txt`, 0 bytes);
    - the deploy at M_A1 with 0 porcelain lines;
    - the module at `414f7d35`.
  - The call (`e96d_a1_analyze.sh`) mirrors the dry gate's arguments in `sbatch_e96data.sh:101-104`@b438ab27:
    - `--runs`, `--e-product` (e)'s product, `--definition h2_definition.json`, `--data-product fd_data_product.json`;
    - `--out`, without `--full-queue` or `--pin`;
    - with `python3 -B` and 1 BLAS thread.
  - The deploy still had 0 porcelain lines afterwards (`:29`).
- **The fetches,** one scp each:

  | archive | sha256 | equals the cluster-side sum at | source |
  |---|---|---|---|
  | `post-dry.tar.gz` | `2b52bd12…` | `post-dry.session.txt:74` | `connect/fetch-dry.txt` |
  | `post-full.tar.gz` | `8bd13f5c…` | `post-full-2.session.txt:116` | `connect/fetch-full.txt` |
  | `post-analyze.tar.gz` | `273dea76…` | `analyze.session.txt:30` | `connect/fetch-analyze.txt` |

  - Each archive was unpacked under `cluster/dry/`, `cluster/full/` and `cluster/analysis/`, with `.txt` appended to
    each name, as in `dry-20261111/`. No member had an absolute or `..` path, and there were no symlinks.
  - The archives' copies of the submit scripts and the queue equal the approved ones:
    `cluster/full/logs/e96d_full_submit.sh.txt` `3a5395bc…`, `e96d_dry_submit.sh.txt` `0a59335b…`, `full.tsv.txt`
    `3aa0bc5e…`.
- **The products** stay on pscratch under `/pscratch/sd/j/josephrb/e96data-a1/runs/`. They are pinned by:
  - `cluster/full/log-full/SHA256SUMS.txt`: 99 product digests, for base F64, control E, repeat k = 1 and ensemble
    k = 1–96;
  - `cluster/dry/log-dry/SHA256SUMS.txt`: the dry run's control and k = 1.

## The dry gate (`cluster/dry/log-dry/GATE.json.txt`, pass true at the pin)

| control | result |
|---|---|
| A-D0: (e)'s product is `fb5cc679` | pass (`:5-6`) |
| A-D0: U @ (e)'s xsec_flat equals the data product's f to 10⁻¹² | pass, max_rel 0.0 (`:8-11`) |
| A-D1: the control exists, equals (e)'s xsec_flat bitwise, and is the declared call | pass (`:14-21`) |
| k = 1 exists and is the declared call; the control and k = 1 ran one code | pass (`:23-33`) |
| the projection: lane_max × t + 300 s ≤ 0.9 × 15,300 s | pass (`:35-46`) |

The projection's numbers:
- lane_max is 14, and t = 923.954 s, which is k = 1's; the control's was 861.619 s.
- So the projection is 13,235.356 s, against 13,770 s.
- t is under amendment 1's bound of 962.1 s.
- The full run's actual elapsed time was 11,110 s (03:05:10).

## The STOP (full-1)

- **What happened:** the reservation-window check stopped before stat and sbatch.
  - The window ran from 18:25:55Z to 23:10:55Z (`connect/full-1-STOP.session.txt:7`).
  - A reservation starting at 2026-11-12T13:00:00 PST = 21:00:00Z fell inside it (`:11`). The script exited 11
    (`:17-18`).
- **The reservation,** from the director's read-only `scontrol`: `_CAP_SC26_Test2`, 21:00 to 23:00Z, 100 nodes of
  `regular_milan_ss11`, accounts m3739 and m5070, no flags. It was neither a maintenance nor ours.
- **The director's ruling (b):** one rerun of `3a5395bc`, unchanged, after 23:00:00Z, after the fence and a by-hand
  squeue check for ll5d, cov2d, rsn_ and rdx_ jobs. Nothing was repaired.
- **The director's added condition:** launch only after LL5D's pilot 61181899 has left squeue AND cov2d confirms its
  atime-post. cov2d confirmed at 00:32:03Z, and full-2 followed at 00:32:53Z.
- **Follow-up (the director, 2026-11-12):**
  - The A1 submit scripts' fences match only `^ll5d_gate_`: `e96d_a1_full_submit.sh:55`,
    `e96d_a1_dry_submit.sh:34,47`. So an `ll5d_pilot` job passes them.
  - The by-hand check covered that for full-2.
  - Any later E96D connect's fence must match `^ll5d`, as `e96d_a1_analyze.sh` does.

## The input atimes (stat only, for LL5D's gate receipts)

E96D's full job reads `of_inputs_5d.npz` and `bkg_dump.npz` plainly. `analyze` reads (e)'s product
`data_b-_j-.npz` plainly. Every mtime and size is unchanged across all readings.

| reading | of_inputs_5d.npz | bkg_dump.npz | data_b-_j-.npz |
|---|---|---|---|
| before the dry run, 14:30:31Z (`dry-submit:16-18`) | 2026-11-12T14:10:22Z | 2026-11-12T14:10:10Z | 2026-11-11T08:24:40Z |
| after the dry run, 18:11:30Z (`post-dry:6-8`) | 2026-11-12T14:34:02Z | 2026-11-12T14:34:02Z | 2026-11-12T14:49:26Z |
| before the full run, 00:33:00Z (`full-2:32-34`) | 14:34:02Z, unchanged | 14:34:02Z, unchanged | 14:49:26Z, unchanged |
| during the full run, 04:30:23Z (`post-full-1:6-8`) | 2026-11-13T02:14:41Z | 2026-11-13T02:14:41Z | unchanged |
| after the full run, 06:00:45Z (`post-full-2:6-8`) | 2026-11-13T05:04:16Z | 2026-11-13T05:04:16Z | unchanged |
| after analyze, 06:05:30Z (`analyze:26-28`) | unchanged | unchanged | 2026-11-13T06:05:30Z |

- The epochs are 1794492622, 1794492610, 1794385480, 1794494042, 1794494966, 1794536081, 1794546256 and 1794549930.
  They were converted by script.
- The 14:34:02Z read falls inside the dry job (14:33:42 to 14:49:26Z). The 02:14:41Z and 05:04:16Z reads fall inside
  the full job (02:14:17 to 05:19:27Z).
- These readings went to cov2d as they were taken.
- **cov2d's bracket overlapped analyze** (cov2d's account, relayed 2026-11-13). The hold the lane and the director
  asked for reached cov2d only after it had acted:
  - cov2d took its LL5D `pre` reading at 06:01:21Z;
  - its G2R envtest connect ran 06:02 to 06:06:37Z, so analyze (06:05:26 to 06:05:30Z) fell inside the bracket;
  - its `post` at 06:08:11Z read NONE-MOVED, 0 of 1146 paths.
- **The overlap is harmless.** cov2d says analyze's file, `s5p-20260926/runs/s2/num/data/data_b-_j-.npz`, is not
  among LL5D's 1146 atime paths, which are also the envtest's bracket. The list's only `data_b-_j-` entry is
  `fd-1b-inv-20261101/i0/in/jitter-data/data_b-_j-.npz`.
- of_inputs_5d and bkg_dump read 1794546256 in both cov2d readings.
- The envtest STOPped on a suite failure, without submitting a job. That is cov2d's own report to the director.

## A concurrent job: rpd_flux1 (limitation-resolver)

- Job 61206960 ran 01:56:02 to 02:00:15Z, while 61202343 was still PENDING.
- Its staged originals are
  `fd/rpd-reco/flux1-20261111/run-61206960/staged-originals.txt`@97e19095eab8c7b44a985cb3a79c248e7adf8a70 (PR #1126):
  54 lines, digest `cf9f9b9d681b4fd6b26c603d174ea07bdea370748be547bd43eb92810294864a`.
- The lane re-ran `grep -nE 's5p-20260926|of_inputs_5d|bkg_dump|data_b-'` on it: rc 1, no lines.
- None of E96D's three inputs is among them.

## Known, as in the dry run

`cluster/full/log-full/env.log.txt:1-2` carries two "setup.sh: No such file or directory" lines:
- `deploy/unbinned_unfolding/build/setup.sh`;
- `deploy/MINERvA101/opt/bin/setup.sh`.

The same two lines are in `cluster/dry/log-dry/env.log.txt:1-2`, and the dry gate passed with them. Both are ROOT/MAT
setups, which the lightgbm tasks do not use. The environment line reads lightgbm 4.6.0, numpy 1.26.4 and python
3.11.14 (`:3`).

## CITABLE FOR / NOT CITABLE FOR

**CITABLE FOR:**
- the custody of E96D A1:
  - each connect's script sha;
  - the gate's controls and projection;
  - the full run's completion, 50 of 50, rc 0, at M_A1;
  - the product digests;
- the readout's own status: rc 0, with no control failed;
- the record's path and sha256;
- the atime readings and their attribution;
- the reservation STOP, and the ruling under which full-2 ran.

**NOT CITABLE FOR:**
- any E₉₆ or F₆₄ value or statement about the data. Those are in `cluster/analysis/ANALYSIS.json.txt`, which is
  unread here. The director reads it once, and it enters the paper or note only by Joseph's decision.
- any adoption of E₉₆, coverage, uncertainty, or change to (e), C_e or any record;
- a cause of the per-unfold times;
- whether any job other than rpd_flux1 read E96D's inputs. The atime readings bound only the moves.

Nothing is submitted, deposited or tagged.
