# COV2D: the G18 pseudo-data job PASSes (job 60848251; step A PASS, step B PASS)

**By** the `cov2d` session, 2026-11-05. Binding 2 ruling 2.1, with the director's GO for `connect-g18-pseudo.sh`
(sha256 `db6f62c1d7b713ad1840d4ba1dfdb0ac9a0f19e525c2c173d3eca41f4e823186`). **MEASURES:** G18's 301 pseudo-data files
and truths, with sections 9.4, 9.6 and 9.11, at M. **CANNOT AUTHORIZE:** the pilot. Its connect sha goes to the
director first.

`pseudo_b.json` is the record `cov2d_jobs.order` reads from origin/main (`PSEUDO_RECORD`), byte for byte the job's file
(sha256 `230f6918…`, the digest taken on the node in `remote_sha256.txt`). With `cov2d_jobs.py` at M, `order("pilot",
"pilot", {this record}, set(), M)` returns `[]`. AR23's pseudo-data job is still refused until the pilot readout's PASS.

## The submission (10:30:34Z)

- **The connect** (`connect-g18-pseudo.sh`, log `connect-g18.log.txt`): login02. DIGEST_MATCH, launched 10:29:33Z.
- **The deploy:** a fresh clone of GitHub at **M = `cb31611ca8b96ed2d1eeb809fda7236e56645863`**, at
  `/pscratch/sd/j/josephrb/cov2d-deploy-cb31611c`. head = M, porcelain 0. The six bound job files' blobs equal the
  amendment's §9.
- **sacct, as the gate read it:** none of the user's jobs since 2026-11-04 is a cov2d-* job.
- **The bound submit script** (`cov2d_submit.sh`): binding 2's M line on origin/main; the tables written once; then
  the order and the gate:
  - order: `{"job": "pseudo", "truth": "G18", "blocked_by": []}`;
  - gate: `{"spent": 0.0, "held": 0.0, "want": "pseudo_G18", "want_node_h": 3.0, "total": 3.0, "cap": 165.8, "pass": true}`.
- **submissions.log:** `2026-11-05T10:30:34Z M=cb31611c… job=pseudo_G18 id=60848251 limit=03:00:00`
  (`submit_state.txt`, with the gate's sacct rows and the tables listing).
- **scontrol:** Account m3246, TimeLimit 03:00:00, one node, partition regular_milan_ss11, **QOS=regular_1**.

**The QOS flag** (the director's ruling, 2026-11-05). Perlmutter maps `--qos=regular` to an internal sub-QOS, here
`regular_1`. The job's own check, `grep -q "QOS=regular"` in `cov2d_pseudo.sbatch` (and `cov2d_job.sbatch`), is a
substring match, so it passes. It would also pass any QOS whose name begins "regular". The director accepted
`regular_1` and left the check unchanged. An exact match, `QOS=regular(_[0-9]+)?`, goes into the next amendment, if
there is one.

## The job

| | |
|---|---|
| sacct | `60848251 cov2d-pseudo_G18 COMPLETED 0:0`, Elapsed 02:24:34 (8,674 s), 1 node: **2.41 node-h** of the 3.0 reserved; MaxRSS (batch) 207,659,228 K |
| start, end | 2026-11-05 10:42:18Z, 13:06:52Z (sacct prints node-local time, UTC−8); node nid005476 |
| `$UNI` | `UNI-STAT PASS` before step A |
| step A (omnifold_py310) | `COV2D-PSEUDO-A G18 PASS natures=301 stops=0`, 4,174.8 s |
| step B (root_6_28 + pinned MAT) | `{"mat_setup_scripts": 6, "mismatches": 0}`, then `COV2D-PSEUDO-B G18 PASS files=301 stops=0`, 4,446.2 s |

The job log (`cov2d-pseudo_G18-60848251.out.txt`) also has ROOT's rootmap warnings, which say the RooUnfold classes in
libUnfoldUtilsDict.so are already in libRooUnfold.so. `mat-60848251.json` is the job's `mat_environment` record.

**Step A** (`pseudo_a.json`):
- verdict PASS, stop [], 301 natures (300 toys and the realization), pins checked, atime moved on nothing;
- the director's R1 counts all zero: a weight ≥ 1e4, a non-finite weight, a row in the box but outside the phase
  space;
- 36 non-finite reco weights zeroed, and counted (`nonfinite_zeroed`: `wr` 36, `wt` 0, `bkgw` 0);
- r_T from 0.6496 to 2.5754; POT data 1.0574e21, MC 4.9782e21.

**Step B** (`pseudo_b.json`):
- verdict PASS, stop [], **`"M": "cb31611ca8b96ed2d1eeb809fda7236e56645863"`**, pins checked, atime moved on nothing;
- **inputs at their pins:** E_R `a5c13fc3…`, the MC file `d40aea69…`, the flux-universe file `5eecae84…`;
- **section 9.4:** 205 cells; truth code vs reference 2.61e-16 (the bar is 1e-12), denominator vs reference
  2.61e-16, hTruth2D = hOFInputTruth2D, and the flux, data POT and nucleon count all equal;
- **section 9.11:** passes for all 301 files.
  - The realization is seed 5,721,000: 3,642,438 rows, as expected; reco cells equal; no row outside the passing
    rows; z = 0.680.

## The deploy after the job

`git status --porcelain`: 0. `git status --porcelain --ignored`: **0**. The job wrote no bytecode or other file into
the deploy, which is still a clean checkout at M (`end_state.txt`). Nothing was cleaned.

## Files

- `pseudo_b.json`, `pseudo_a.json`: the job's records, verbatim.
- `cov2d-pseudo_G18-60848251.out.txt`: the job's log. Its `.txt` suffix was added because `*.out` is gitignored; the
  bytes are unchanged.
- `mat-60848251.json`: the job's MAT environment record.
- `connect-g18-pseudo.sh`, `connect-g18.log.txt`: the connect and its log.
- `submit_state.txt`: `$O` after the submission (the gate's sacct rows, gate and order JSON, submissions.log, and the
  tables).
- `end_state.txt`: sacct, the deploy's porcelain and the listing of `$O` after the job.
- `remote_sha256.txt`: the records' digests, taken on the node. Each equals its file here.
- `removal.log.txt`: `/dev/shm/josephrb-cov2d-g18.{log,sh}` removed (rc 0 each), and `/dev/shm` left empty.
