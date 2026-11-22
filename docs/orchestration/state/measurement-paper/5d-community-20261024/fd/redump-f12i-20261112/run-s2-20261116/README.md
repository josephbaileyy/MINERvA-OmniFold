# RDX gs2 and s2: the gate file, and the eleven playlist submits (receipt)

**By** session tier3-design, under the director's go of 2026-11-16 for gs2 and then s2 (`../RDX-BINDING-1.md`, addenda
J1 and J3). One run each. Both steps used the launcher and connect from M_RDXC
`11e36cf1a5643ef6db2d480f3d345364d3247592`, which were taken by `git show` and checked by `shasum -a 256` before each
connect. Their digests were `602c728a7b4326f2…` and `eae946894be8ce02…`, J3's digests. The pin was M_RDXS `ad0535c4`.

`*.session.txt` is the launcher's stdout byte for byte: ssh's rc line, the session, then the launcher's rc line.
`*.session.err.txt` is the ssh session's stderr, NERSC's login banner.

## gs2: login27, 2026-11-16T19:57:38Z, rc 0

- **The checks:**
  - the node's `/dev/shm` copy was `eae946894be8ce02…` (`gs2.session.txt:2, 4`);
  - the 15 purge-exposed MP-1 inputs were PRESENT, by stat only (5-101);
  - `squeue --me` was empty (102-103).
- **What it wrote:** `out/gates/s2.ok`, with the lines `pin=ad0535c4a62ac0a20711a4a00f2266ddaf926d7c` and
  `utc=2026-11-16T19:57:38Z` (104-105). gs2 STOPs if the gate file is already there (`rdx_connect.sh:98`), and it
  exited rc 0, so this run created it.
- **Exit codes:** launcher, ssh and script all rc 0 (1, 106-108).
- **Charge:** none (no job).

## The holds, before s2

- **cov2d acked before the s2 connect:**
  - no cov2d cluster window was open or planned in the next ~8 h;
  - no connect or submit was pending;
  - no cov2d atime watch was running.

  Their fences refuse every `rdx_` job other than `rdx_s1_1A` (ruling ii), so a cov2d connect will refuse while these
  jobs are up. cov2d said they will ask for this lane's end message before any new cluster work.
- **FYIs** on the `rdx_s2_<PL>` family and its window went to director-helper-2 and limitation-resolver.

## s2: login27, 19:58:15–19:59:23Z, rc 0

**What passed before the first submit:**
- the `/dev/shm` copy was `eae946894be8ce02…` (`s2.session.txt:2, 4`);
- the 15 inputs were PRESENT (5-101);
- `squeue --me` was empty (102-103);
- the policy check was CLEAR, with no hits (104-131). s2's reads are the playlist manifests and
  `minerva_large_files`.

The connect's own requirements, which STOP on failure and ran before the policy check, also passed:
- `gates/ll5d_atime_post.txt` is non-empty;
- `checks/align_1A.json`, `truthx_rows_1A.json` and `walk_probe.json` each record PASS. c1 wrote them on 2026-11-16
  (`../run-c1-20261116/`);
- `gates/s2.ok` names the pin.

**Each playlist,** in order. The connect ran:
1. the launcher's smoke: its AnaTuples were checked by size and mtime against the manifest, with 0 differing;
2. the fence;
3. `rdx_cap.py` on a fresh sacct snapshot and `submissions.log`;
4. sbatch.

Every cap gate passed. The totals match the projection sent to the director before the go (1.0870 at the 11th):

| job | id | limit | AnaTuples | cap total (node-h) | lines |
|---|---|---|---|---|---|
| rdx_s2_1B | 61423404 | 1:00:00 | 58 | 0.1095 | 132-137 |
| rdx_s2_1C | 61423406 | 1:15:00 | 123 | 0.1584 | 138-143 |
| rdx_s2_1D | 61423408 | 3:30:00 | 344 | 0.2952 | 144-149 |
| rdx_s2_1E | 61423410 | 2:45:00 | 270 | 0.4028 | 150-155 |
| rdx_s2_1F | 61423414 | 3:45:00 | 331 | 0.5494 | 156-161 |
| rdx_s2_1G | 61423417 | 3:15:00 | 294 | 0.6765 | 162-167 |
| rdx_s2_1L | 61423421 | 1:00:00 | 21 | 0.7156 | 168-173 |
| rdx_s2_1M | 61423451 | 4:45:00 | 300 | 0.9013 | 174-179 |
| rdx_s2_1N | 61423454 | 2:45:00 | 169 | 1.0088 | 180-185 |
| rdx_s2_1O | 61423456 | 1:00:00 | 42 | 1.0479 | 186-191 |
| rdx_s2_1P | 61423459 | 1:00:00 | 61 | 1.0870 | 192-197 |

- At submit, each job was PENDING in QOS shared.
- **Exit codes:** launcher, ssh and script all rc 0 (1, 198-200).
- The cap total holds every job at its ceiling: 0.0704 spent (s1) plus 1.0166 held.

## The jobs' outcomes: all eleven COMPLETED 0:0

**The watch.** `s2-jobs/watch_s2.sh` (sha256 `734ba3fc…`) ran on this laptop. Every 10 min it read
`sacct -X -n -P -j <the eleven ids> -o JobID,JobName,State,ExitCode,Elapsed,ElapsedRaw,Start,End` over ssh to saul.
It never used squeue. It stopped when all eleven rows were in a terminal state.
- `s2-jobs/watch.log.txt` holds every read: 31 reads from 19:59:56Z on 2026-11-16 to 01:02:42Z on 2026-11-17.
- One read failed, ssh rc 255 with no rows, at 20:30:47Z (line 37). The next read, 10 min later, was whole.
- The first job started at 12:09:23 local, on its first RUNNING row (line 14).

**The final read** is `s2-jobs/sacct.psv`, a copy of `watch.log.txt:352-362`. Start and End are Perlmutter local time,
PST (UTC−8). The charge is ElapsedRaw × 0.0391 node-h per hour, `rdx_cap.py`'s shared rate.

| job | id | state | elapsed | of limit | start → end (PST) | charge (node-h) |
|---|---|---|---|---|---|---|
| rdx_s2_1B | 61423404 | COMPLETED 0:0 | 00:25:37 (1537 s) | 43% | 12:09:23 → 12:35:00 | 0.0167 |
| rdx_s2_1C | 61423406 | COMPLETED 0:0 | 01:05:06 (3906 s) | 87% | 12:12:08 → 13:17:14 | 0.0424 |
| rdx_s2_1D | 61423408 | COMPLETED 0:0 | 02:33:47 (9227 s) | 73% | 12:18:04 → 14:51:51 | 0.1002 |
| rdx_s2_1E | 61423410 | COMPLETED 0:0 | 02:10:27 (7827 s) | 79% | 12:20:56 → 14:31:23 | 0.0850 |
| rdx_s2_1F | 61423414 | COMPLETED 0:0 | 02:57:23 (10643 s) | 79% | 12:30:16 → 15:27:39 | 0.1156 |
| rdx_s2_1G | 61423417 | COMPLETED 0:0 | 02:32:12 (9132 s) | 78% | 12:33:03 → 15:05:15 | 0.0992 |
| rdx_s2_1L | 61423421 | COMPLETED 0:0 | 00:12:01 (721 s) | 20% | 12:34:01 → 12:46:02 | 0.0078 |
| rdx_s2_1M | 61423451 | COMPLETED 0:0 | 04:05:32 (14732 s) | 86% | 12:49:04 → 16:54:36 | 0.1600 |
| rdx_s2_1N | 61423454 | COMPLETED 0:0 | 02:03:17 (7397 s) | 75% | 12:49:05 → 14:52:22 | 0.0803 |
| rdx_s2_1O | 61423456 | COMPLETED 0:0 | 00:32:42 (1962 s) | 54% | 12:58:56 → 13:31:38 | 0.0213 |
| rdx_s2_1P | 61423459 | COMPLETED 0:0 | 00:48:54 (2934 s) | 82% | 12:58:56 → 13:47:50 | 0.0319 |

- **s2's charge:** 0.7605 node-h.
- **RDX's total spent:** 0.8309 of the 2.5 cap (s1 0.0704 + s2 0.7605), which leaves 1.6691.
- **Unchecked so far:** the job logs and the outputs. Their checks belong to c2, which takes its own go: the per-playlist
  O_NOATIME copy, C-ALIGN-PL and C-TRUTHX, and `out/loops.sha256` only if every one passes.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:**
  - gs2's gate file;
  - s2's pre-submit checks, its eleven job ids and limits, and each cap gate's totals;
  - the launcher and connect shas that ran;
  - the eleven jobs' sacct states and their charge.
- **Not citable for:** the jobs' logs or output files (c2 reads them), any C-ALIGN-PL or C-TRUTHX verdict (c2's,
  under its own go), or any RDX reading.
