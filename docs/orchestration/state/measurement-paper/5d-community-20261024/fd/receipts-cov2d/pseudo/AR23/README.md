# COV2D A2, stage 2: the AR23 pseudo-data rerun PASSes (job 60889690; step A PASS, step B PASS)

**By** the `cov2d` session, 2026-11-06. This is the second stage of A2's fixed conditional sequence (COV2D-BINDING-2.md,
"Binding 2, addendum A2", revision 2: **M = `a60547692df5f963e428cdfe4661fc51ab785b7b`**). It proceeded on stage 1's
PASS record (`../../a2/cluster_tests/CLUSTER-TESTS.md`, #822). The first AR23 attempt, STOP #2, is in
`../AR23-attempt1/`.

**MEASURES:** AR23's 301 pseudo-data files and truths at M, with sections 9.4 and 9.11; A2's staged copies, their
settle readings and both guards' recorded values; the deletion of the copies. **CANNOT AUTHORIZE** anything beyond
stage 3, the eight universe jobs, which proceed on this record once it is on main.

**Verdict: PASS.** No guard fired and no input was off its pin. The STOP count stays at two.

`pseudo_b.json` is the record `cov2d_jobs.order` reads from origin/main (`PSEUDO_RECORD`), byte for byte the job's file
(sha256 `d50ef13a…`, the node's digest in `remote_sha256.txt`). It carries `"M": "a6054769…"` and
`"pins_checked": true`. With `cov2d_jobs.py` at M, and the G18 and pilot records as committed on main (admitted by
`PRIOR_RECORDS`), `order(u, …, M)` returns `[]` for each of the eight universe jobs `G18_Ua`–`AR23_Ud`. Without this
record it returns the AR23 pseudo-data blocker. Bulk jobs are still refused until all eight universe jobs are
submitted.

## The submission (06:10:11Z)

- **The connect** (`connect-ar23-rerun.sh`, sha256 `a00743912829570f66a814949f997afd85602104d8e2807b918df7f2cdb8c215`;
  log `connect-ar23b.log.txt`, `1ada97ea…`): login02. DIGEST_MATCH, launched 06:09:52Z.
- **The deploy:** `/pscratch/sd/j/josephrb/cov2d-deploy-a6054769`, head = M, porcelain 0, `--ignored` 0, before and
  after the submission.
- **origin/main** `822fe16d`. The connect hashed the records the order reads there: G18's `pseudo_b.json`
  `230f6918…` and the pilot readout `b59ffa2d…` (both equal to their `PRIOR_RECORDS` digests), and stage 1's
  `CLUSTER-TESTS.md` `88d56927…`.
- **order:** `{"job": "pseudo", "truth": "AR23", "blocked_by": []}`.
- **gate:** `{"spent": 4.3608, "held": 0.0, "want": "pseudo_AR23", "want_node_h": 4.0, "total": 8.3608, "cap": 165.8,
  "pass": true, "staged_bytes": 173261737169, "quota_problem": null}`. The quota check at submission (A2 §3,
  option (c)) passed.
- **scontrol:** Account m3246, TimeLimit 04:00:00 (`PSEUDO_LIMITS["AR23"]`), one node, partition regular_milan_ss11,
  QOS=regular_1 (accepted by the director for G18).

## The job

| | |
|---|---|
| sacct | `60889690 cov2d-pseudo_AR23 COMPLETED 0:0`, Elapsed 02:31:44 (9,104 s), 1 node: **2.53 node-h** of the 4.0 reserved |
| start, end | 2026-11-06 06:19:09Z, 08:50:53Z (sacct prints node-local time, UTC−8); node nid006885 |
| `$UNI` | `UNI-STAT PASS` before step A |
| step A (omnifold_py310) | `COV2D-PSEUDO-A AR23 PASS natures=301 stops=0`, 4,561.5 s |
| step B (root_6_28 + pinned MAT) | `{"mat_setup_scripts": 6, "mismatches": 0}`, then `COV2D-PSEUDO-B AR23 PASS files=301 stops=0`, 4,487.3 s |
| deletion | `deleted staged copies; kept 0 whose stat differed` |

The job log (`cov2d-pseudo_AR23-60889690.out.txt`) also has ROOT's rootmap warnings about the RooUnfold classes, as
for G18. `mat-60889690.json`, the job's `mat_environment` record, is identical to G18's.

With this job, the gate's spent total is 6.89 node-h of the 165.8 cap.

**Step A** (`pseudo_a.json`):
- verdict PASS, stop [], 301 natures (300 toys and the realization, seed 5,731,000), `pins_checked` true;
- **staging:** four copies in `a/stage`, each sha256 equal to its pin: `$UNI` `220c479e…` (171,117,087,867 bytes),
  `$CV` `43f8cc16…`, the flux constraint `e38ad7d2…`, AR23's ratio file `eab33d6d…`. No `off_pin` entry;
- **the shared sources during staging:** each source's atime before and after its copy is recorded and equal
  (`src_atime_moved` false for all four; `shared_atime_moved` []);
- **settle:** two consecutive readings of the copies' atimes, equal (`settle_atime_ns`);
- **the guard:** `atime_ns` holds both values for each copy, and before = after for all four; `atime_moved` [];
- the director's R1 counts all zero; 36 non-finite reco weights zeroed and counted (`wr` 36, `wt` 0, `bkgw` 0), as
  for G18 and AR23's first attempt;
- r_T from 0.6098 to 2.5682; POT data 1.0574e21, MC 4.9782e21.

**Step B** (`pseudo_b.json`):
- verdict PASS, stop [], **`"M": "a60547692df5f963e428cdfe4661fc51ab785b7b"`**, `pins_checked` true;
- **staging:** three copies in `b/stage` at their pins: E_R `a5c13fc3…`, the MC file `d40aea69…`, the flux-universe
  file `5eecae84…`. Sources unmoved (`shared_atime_moved` []); no `off_pin` entry;
- **settle and guard:** two equal settle readings; before = after for all three copies; `atime_moved` [];
- **section 9.4:** 205 cells; truth code vs reference 2.61e-16 (the bar is 1e-12), denominator vs reference 2.61e-16,
  hTruth2D = hOFInputTruth2D, and the flux, data POT and nucleon count all equal;
- **section 9.11:** passes for all 301 files (301 distinct seeds). The realization, seed 5,731,000: 3,647,810 rows,
  as expected; reco cells equal; no row outside the passing rows; z = 0.981.

**One observation, not a test.** Step A recorded the shared flux constraint's atime as 1793891894 (2026-11-05
15:18:14Z) before and after its copy. That is the value limitation-resolver's stat saw after STOP #2, and the time of
REF-G1's second read, as in `../AR23-attempt1/README.md`. It is consistent with that record's inferred explanation and
does not test it.

## The staged copies' deletion

`deletions.tsv` (RE-2's B9 form) has seven rows: the four copies of step A and the three of step B. Each row's size,
mtime and inode equal what staging recorded (`stat_match` yes), and each names step B's PASS record as its condition.
After the job, `a/stage`, `b/stage` and the job's TMPDIR `$O/tmp/60889690` are empty (`end_state.txt`).

## After the job

- **The deploy:** head = M; `git status --porcelain` 0, `--porcelain --ignored` 0. Nothing was cleaned.
- **Left in place on pscratch:** `$O/pseudo/AR23-a2/a` (step A's products), `$O/pseudo/AR23-a2/b` (the 301 data
  files, the truths and `pseudo_b.json`), and the first attempt's `$O/pseudo/AR23/a`, unchanged.
- **The connect's files:** `/dev/shm/josephrb-cov2d-ar23b.{log,sh}` removed at 06:11:16Z, rc 0 each, and `/dev/shm`
  left empty (`removal.log.txt`). At 08:56:45Z it held no entry of the user's.

## Files

- `pseudo_b.json`, `pseudo_a.json`: the job's records, verbatim.
- `cov2d-pseudo_AR23-60889690.out.txt`: the job's log. Its `.txt` suffix was added because `*.out` is gitignored; the
  bytes are unchanged.
- `mat-60889690.json`: the job's MAT environment record.
- `deletions.tsv`: the staged copies' deletion ledger, verbatim.
- `connect-ar23-rerun.sh`, `connect-ar23b.log.txt`: the connect and its log.
- `end_state.txt`: sacct, the stage and TMPDIR listings, the deploy's porcelain, `$O/pseudo` and `/dev/shm`, fetched at
  08:56:45Z.
- `remote_sha256.txt`: the records', the ledger's and the log's digests, taken on the node. Each equals its file here.
- `removal.log.txt`: the connect's `/dev/shm` removals.
