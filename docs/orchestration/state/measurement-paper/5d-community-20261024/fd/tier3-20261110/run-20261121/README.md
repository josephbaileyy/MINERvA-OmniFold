# T3: the three jobs and the read (receipt; tier3-design, 2026-11-21)

These ran under T3-BINDING-1 with addendum V1, `T3-CONNECT-PLAN.md`, and the director's standing go of 2026-11-21,
which relays Joseph's authorization. The deploy was M_V1 = 8bb4e3b0e1028d960e39de0c202569a08a1218a0, with
`$OUT = /pscratch/sd/j/josephrb/t3p-20261121`. The read is declaration section 7's one reader run. It used
`t3p_read.py` (f4c221dd…, the bound bytes) in a fresh clone at M_V1, and it printed `{"verdict": "COMPLETE"}`, rc 0.

**No reading is quoted in this receipt.** The readings are in `cluster/read/readout.json` and `cluster/read/readout.txt`:
TR-1, TR-2, the trajectory, location and composite classes, and the per-cell table. By declaration section 7 they go to
the director, who reads them and reports to Joseph before any paper text.

- **readout.json** sha256 b0362c387ec3d8fd48616abe5dcf589407fd007b62214d6297b47418d1a9ecce, 749,936 bytes.
- **readout.txt** sha256 17e37fa1536b3c37102afddeb384b3bf2f819fa09f918fcfd7557f21c3b0b171, 2,526 bytes.

CITABLE FOR:
- that the three T3 jobs ran as bound and completed, with C-PAIR and C-X passed;
- that the read ran once, as bound, and completed;
- the outputs' sha256 and bytes;
- the connects' checks and the charge.

NOT CITABLE FOR: any reading, class or wording, until the director's read and report to Joseph.

## The jobs (sacct, in `cluster/logs/connect-read.log.txt`)

| job | id | start (PST) | end (PST) | ElapsedRaw | nodes | node-h | DONE | C-PAIR / C-X (`log-*/pair.json`) |
|---|---|---|---|---|---|---|---|---|
| t3p_dry | 61726250 | 02:42:16 | 03:51:54 | 4,178 s | 1 | 1.161 | 6 of 6, rc 0 | pass (4 / 6) |
| t3p_q3 | 61728686 | 04:35:17 | 05:48:39 | 4,402 s | 1 | 1.223 | 6 of 6, rc 0 | pass (4 / 6) |
| t3p_floor | 61731751 | 06:12:44 | 09:40:31 | 12,467 s | 1 | 3.463 | 24 of 24, rc 0 | pass (8 / 24) |
| **total** | | | | 21,047 s | | **5.846** (cap 10.0) | | |

Every job ended COMPLETED, exit 0:0. Each `--time` came from `t3p_probe.py limit`: 2:15:00, 2:00:00 and 5:45:00.

## The submit connects (`connect/t3p_submit.sh`, `connect/t3p_launch.sh`; logs in `cluster/logs/`, lane side in `lane/`)

- **dry** (connect rev 1, 745074a9).
  - The connect passed:
    - the fence;
    - iris;
    - the clone at M_V1 and the bound digests;
    - `test_t3p.py`, 69 OK (`cluster/logs/tests.log.txt`);
    - the pins (`cluster/logs/pins.tsv`);
    - the queues (6 / 6 / 24);
    - `fence.txt`.
  - Then it submitted 61726250 (TimeLimit 02:15:00 by scontrol) and ended rc 8: its own limit call had written ignored
    `__pycache__/` directories into the deploy (`cluster/logs/connect-dry.log.txt`). The job stayed queued and was
    reported, not cancelled.
  - The director ruled rc 8 not a refusal, and connect rev 2 (50e86da3) tolerates ignored `__pycache__/` only.
- **q3** (rev 2, 50e86da3): submitted 61728686, rc 0.
- **floor**:
  - Attempt 1 (rev 2) bailed at the connect's t3p_ fence while q3 was PENDING (`lane/floor-attempt1-session.out.txt`,
    `BAIL fence (sacct) not clear`, rc 9). It wrote nothing.
  - The director ruled a resubmission once q3 was terminal, at the same connect with no changed byte and fresh acks.
  - Attempt 2 submitted 61731751, rc 0.
- **Acks.** Every connect followed acks from cov2d, limitation-resolver and director-helper-3. Each ack's UTC time came
  from `date`, and the window end was the oldest ack plus 900 s (`lane/*-wend.txt`).
- **Watches.** The job states came from sacct, never squeue (`lane/watch-*.log.txt`).

## The read connect (`connect/t3p_read_connect.sh` rev 1, 9c4b604c; `connect/t3p_read_launch.sh` rev 1, 9d6bf0f1)

The plan's row c5 had no script. Two scripts were written for it. Their checks before the go are in
`connect/read-checks/` and come in three parts:
- a guarded read on test_t3p's planted fixture;
- eight Debian stand-in variants;
- Grok's read for the director, which gave FIX at rev 0, and its recheck of rev 1, which gave GO.

The director gave the go at 5de22199.

- **The session.** login38, 18:48:07–18:49:35Z, after acks at 18:47:48Z (cov2d) and 18:47:49Z (director-helper-3,
  limitation-resolver), with the window ending at 19:02:48Z. Results:
  - ssh rc 0 and script rc 0;
  - the `/dev/shm` copy was checked at its sha256 on the node;
  - the done file is `0` (`cluster/logs/connect-read.done`).
- **Preconditions and checks** (`cluster/logs/connect-read.log.txt`):
  - the sacct fence was clear;
  - the three jobs were COMPLETED, with DONE 6, 6 and 24;
  - `deploy-read` was at HEAD M_V1 with 0 porcelain `--ignored` lines before and after;
  - the six bound T3 files were OK;
  - the declaration (f96ed6f2…) and addendum V1 (3998708a…) were at their pins;
  - the SHA256SUMS of dry, q3 and floor had 6, 12 and 36 well-formed lines and held under `--strict`;
  - `runs/` held 36 products.
- **The read.** M_V1's `t3p_read.main` ran unchanged under root_6_28's python 3.11.14 with these settings:
  - `-I -B`, nice 19, ionice idle, every thread cap at 1, PYTHONHASHSEED=0;
  - inside `ref_g1.read_guards(ref_g1.PROTECTED, ($D, $OUT), root=False)`;
  - its stdout went to /dev/null, so the log holds only the verdict line.
- **The records.** 224 files went through `dd iflag=noatime` into `$OUT/fetch-read/`, each copy equal to its source.
  `RECORDS.SHA256SUMS` lists them. One tar was made, `fetch-read.tar`, sha256 2bdeb9f6…, 2,314,240 bytes.
- **The fetch.** The tar, the connect's log and the done file were streamed with `dd iflag=noatime`.
  - The tar's sha256 equals the log's.
  - It was extracted here as `cluster/`, and `RECORDS.SHA256SUMS` checks (rc 0, `lane/read-records-check.txt`).
- **Not fetched.** The products themselves (`runs/*.npz`) stay on pscratch. Their sha256 are in
  `cluster/log-floor/SHA256SUMS`.

## The regenerated index files

The index files are `RESULTS-INDEX.tsv`, `RESULTS-POPULATION.tsv` and `docs/analysis-note/records_results_index.tex`
(`records_estimators.tex` is unchanged).
- readout.json joins the results population with one metric row, `controls/C-CT/closure_nuwro_z_abs`. That is FD-PRR's
  C-CT control (the grade matrices reproduce F0b's noise-free `closure_nuwro` grade), not a T3 reading.
- The PR carries the files as `tools/registry/results_index.py --write` generated them. The row is a generated listing
  marked UNATTRIBUTED, the same path as FD-PRR's readout (the director's ruling of 2026-11-09, option (a)).

## Renames

65 record names that git ignores (`.log`, `.out`, `.err`) carry ".txt" here (`RENAMES.tsv`, with each file's sha256).
Their contents are unchanged. `cluster/RECORDS.SHA256SUMS` lists the original names.

<!-- absence-ok: a scoping statement of what this receipt quotes, under declaration section 7 -->
