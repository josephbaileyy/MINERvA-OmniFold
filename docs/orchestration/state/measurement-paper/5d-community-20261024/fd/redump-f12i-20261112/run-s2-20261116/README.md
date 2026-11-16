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

## The jobs' outcomes

To be added from sacct over the eleven ids when all have ended. The watch reads sacct only, never squeue.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:**
  - gs2's gate file;
  - s2's pre-submit checks, its eleven job ids and limits, and each cap gate's totals;
  - the launcher and connect shas that ran.
- **Not citable for:** any job's outcome (recorded in a later commit), any C-ALIGN-PL or C-TRUTHX verdict (c2's,
  under its own go), or any RDX reading.
