# COVFIX PG: the two validation truths through F1's GENIE v3 pipeline

`pg_generate.sh` is the one executable that cov2d's bound PG binary runs as a subprocess
(`state/2d-closeout/covfix-20261122/COVFIX-DECLARATION.md` §4.1–§4.2). It runs F1's bound pipeline with only the
tune names and the seeds changed, in F1b′'s single-wave layout (`FD-F1-DECLARATION-AMENDMENT-2.md` §4).

**Status: not ready to bind.**
- `pg_pins.json` (strace's path and sha256, CVMFS's dbconfig sha256) is empty until the director pins it from PG's
  probe receipt (R1). Until then `pg_generate.sh` refuses before any step.
- Slot 1's private product must also be installed by B2 (`state/2d-closeout/covfix-20261122/pg/install/`).

**Slot 1 and the checks** (`state/2d-closeout/covfix-20261122/pg/PLAN-SLOT1-PROBE.md`, approved; `RULINGS-A2.md`).
Slot 1 is G21_11a_00_000, from a sha-pinned private copy of SciSoft's G2111a00000 product under
`/pscratch/sd/j/josephrb/covfix-pg/products`. Slot 2 is G18_02a_00_000, from CVMFS. Before generation, in order:
0. Both drivers refuse if LD_PRELOAD, LD_AUDIT, BASH_ENV, ENV, PYTHONPATH, PYTHONSTARTUP, PYTHONUSERBASE, GXMLPATHS
   or GALGCONF is set. pg_generate.sh also refuses in these cases:
   - the deploy has any untracked or ignored file, or a git call fails;
   - W is not its own physical path, or W/tmp is not a real directory of the user's with mode 0700;
   - pg_pins.json lacks strace's, dbconfig's or the system tools' pins;
   - `record/root-schemas.json` has no gst schema. It stays unset until B3's replay records one and the director
     confirms it.
1. strace is opened once on fd 9. `pg_verify.py tool-check --fd 9` reads its sha256 through that inherited
   descriptor (no path is opened: `/proc/self/fd/9` is a magic link that O_NOFOLLOW refuses), and its self-test runs.
   CVMFS's revision and root hash are recorded now and at the end. If they differ, every CVMFS file the run read must
   re-hash equal to its pin (`revision-compare`), or it is a STOP. `node-record` then records the compute node's
   `/proc` mount options (hidepid) and the allocation's exclusivity. F1's argv carries the seed, so this is the
   boundary on record (C3); the seed never reaches the sbatch line, the job name, `--comment`, the batch script or
   the exported environment.
2. The private product is checked against every pinned member. Its top level must be exactly `.upsfiles` and
   `genie_xsec`; `genie_xsec` itself is a container, not a member, and `.upsfiles` holds only a read-only dbconfig.
3. Each tune's setup resolves `gevgen`, `gspl2root` and `awk`, and records `LD_LIBRARY_PATH` and `GXMLPATH`.
   - The programs are checked against the genie manifest, by bytes and by real path.
   - awk must be a root-owned system tool, by its own path and its real path.
   - No LD_LIBRARY_PATH entry may be empty or lie outside CVMFS and the system library directories.
4. reduce, gspl2root, a one-event coverage run per tune, every gevgen and every gntpc run under strace (open, stat,
   access, readlink, chdir, the execve and execveat, rename, link, symlink and unlink families). Their traces are
   checked; `pg_verify.py`'s docstring lists the rules, and every refusal names a reason code. In outline:
   - each role starts with its own program (awk, gspl2root, gevgen, gntpc), and every exec is resolved and bound to
     the manifest or a pinned system tool;
   - nothing is written, renamed, linked or unlinked outside W (/dev/null aside). An open that creates a file without
     truncating it counts as an output only at the role's expected path, after the same process found it absent or
     unlinked it (ROOT's RECREATE);
   - each tune's XML is found by GENIE's own search: the order is rebuilt from the trace's access probes, and the
     first path that exists is the one read;
   - the pinned spline is read, and the coverage run reads its pinned messenger;
   - nothing else under a genie_xsec data directory is read, and a read that cannot be resolved is a STOP;
   - every ROOT and GENIE library comes from CVMFS and is hashed; other shared libraries come from CVMFS or a system
     library directory;
   - `..` paths are resolved on the node by their full real path.
5. The reduce keeps every spline for each (probe, target) pair of F1's argv, compared by tune, key, knot count and
   knot values, with duplicates refused (`reduce-check`). The coverage run uses the public seed, F1's argv
   (`argv-check`: its block sets only N, the seed and the messenger) and a messenger with only GEVGDriver at DEBUG.
   GENIE builds every spline at initialisation, so one event covers them all. Before any sealed seed is used, the
   log must show that GENIE found every spline of every pair in the pinned file (`coverage-log`). Its outputs are
   then deleted, and its log's hash is kept.
The generation runs in its own process group (setsid). On any exit, every background step's tree is stopped and
reaped, and processes in that group or with a cwd under W are checked for survivors; this shell's own parent chain
is spared. Survivors are drained (30 s after SIGKILL) before publication and before seed-named files are renamed; a
failed rename is a STOP that names no path. Every check's pass is recorded in PRODUCTS.json. `pg_lib.py publish`
then:
- lists the outgoing set from an explicit allowlist. Any other file outside W/tmp, seed-bearing ones aside, is a STOP;
- scans every outgoing file for the seeds in decimal, hex and int64 (both byte orders), with each ROOT object
  inflated (ZLIB, LZMA, ZSTD, LZ4; any other codec is a STOP). int32 matches are counted against their chance
  expectation and recorded, never a STOP;
- checks each gst's trees, branches and streamer info against B3's schema;
- writes `out/leak_scan.json` and the public `out/PG-PUBLISH-SHA256SUMS`, and scans both.
A STOP after publication withdraws both files. The required inventory (`pg_lib.py inventory`) is checked last.

**B3 (`pg_replay.sh`)** runs these checks for slot 1 on a login node, then:
- slot 1's coverage run, and one 100-event public-seed gevgen and gntpc;
- slot 2's traced reduce at its real CVMFS path, its completeness and its coverage run;
- the four real-shape checks (`shape-check`) and three host checks (`host-check`), which must pass there before slot 2
  is generated.
A trap deletes the public-seed event and status files on every exit. Every unlink is tried even when reading the
file fails, and any file left is a failure. `deleted.json` keeps each file's hash and size, each ROOT file's decoded
scan and the gst's schema, which `replay.json` (`covfix-pg-replay-run/3`) carries with each trace's execs and both
CVMFS revisions. agy's and codex-school's reads, and their dispositions, are in
`state/2d-closeout/covfix-20261122/pg/AGY-READ-A2.md`; round 4's are in `pg/delta-read-r4/`.

## Contract

```
cd W && TMPDIR=W/tmp pg_generate.sh --workdir W --seeds W/seeds.json < /dev/null
```

- **The parent** gives it cwd W, `TMPDIR=W/tmp` (existing), stdin `/dev/null`, captured stdout and stderr, and a
  scrubbed environment. It runs on one exclusive CPU node. The parent verifies this file's sha256.
- **seeds.json:** `{"tunes": [{"u": 0, "name": "G21_11a_00_000", "task_seeds": [7 ints]}, {"u": 1, "name":
  "G18_02a_00_000", "task_seeds": [7 ints]}]}`. `pg_lib.load_seeds` checks §4.2's rule as far as the
  file allows, since the base is not in it. u0's first seed must be in [1e9, 2e9). Seeds must be consecutive within a
  tune, and u1's first must be u0's + 10,000. Every seed must be below 2³¹ − 1. A refusal names the rule, never the value.
- **Exit:** 0 on success, 1 on a failed step (a STOP), 2 on a refusal before any step (bad arguments, cwd, TMPDIR, an
  existing `W/out`, `W/run` or `W/PRODUCTS.json`, or a deploy that is not `PG_DEPLOY_PIN` or has a modified tracked
  file).
- **Its own stdout and stderr** carry only step names with pass/STOP, task and file counts, timestamps and the host
  name. They carry no seed, no path under W and no physics number. Every sub-step's output goes to `W/out/logs/` or
  `W/out/work/u<u>/t<k>/task.log`.

## Environment it needs

| variable | why |
|---|---|
| `PATH` | at least `/usr/bin:/bin`: bash, git, awk, xargs, `/usr/bin/time`, timeout, sha256sum, find, sort, cmp, hostname |
| `HOME` | `setup_salloc_env.sh` activates `$HOME/.conda/envs/root_6_28`. `setup_genie_v3.sh` reads the compat-lib shim at `$HOME/.genie_compatlibs` |
| `TMPDIR` | must be `W/tmp`. It is re-exported after every environment activation, because `setup_salloc_env.sh` sets `TMPDIR=$SCRATCH/tmp` |
| `PG_DEPLOY_PIN` | the full commit sha the deploy must be at. The executable refuses without it |
| `SCRATCH` (optional) | read by `setup_salloc_env.sh` only for the TMPDIR and CODEX_HOME it sets. TMPDIR is then overridden |
| `GENIE_COMPAT` (optional) | overrides the shim directory, as in F1 |
| `ROOT628_PREFIX`, `ROOT628_CONDA` (optional) | override the analysis environment's location, as `setup_salloc_env.sh` allows |

It needs no network, no passphrase and no GNUPGHOME: encryption is the parent's. It runs without `SLURM_*`
variables, but `node-record` reads `SLURM_JOB_ID` and `SLURM_CPUS_ON_NODE`. The parent's env_keep must pass both, or
`node_check.json` records `slurm_job` and `all_cpus_allocated` false.

## What it writes (all under W)

- `W/run/`: `queue.txt` (tune, seed and work directory per task; seed-bearing) and the deploy status snapshots.
- `W/out/splines/`: the reduced splines. `W/out/`: the flux file and its JSON, the spline-check JSONs, the gspl2root
  graphs and their logs.
- `W/out/work/u<u>/t<k>/`: each task's gst, `input-flux.root`, `gevgen.log`, `gntpc.log`, `task.log`, `task.time` and
  `gevgen.status`. gevgen names that file `genie-mcjob-<seed>.status`, and it is renamed so that no file name carries a
  seed.
- `W/out/gst/`, `W/out/gen5d/`: the merged gst and the gen5d npz with its meta JSON (f_MEC, the sampling test, the
  counts).
- `W/out/prep/`: `config-pg.json`, `ratios/L-5D-PV/<truth>.json`, `bridged/<truth>.json` and `f1-prep-SHA256SUMS`.
- `W/PRODUCTS.json`: per u, the tune, the truth name and the relative paths of the bridged ratio (what PV applies,
  §3.4), the pvl ratio and the prediction.
- `W/out/PG-SHA256SUMS`: the plaintext sha256 of every product. **It is seed-bearing and must stay inside the seal.**
- `W/out/PG-PUBLISH-SHA256SUMS` and `W/out/leak_scan.json`: the allowlisted, published files' sums and the scan's
  counts. Both are public and both are scanned.
- `W/out/revision_compare.json` and `W/out/node_check.json`: the CVMFS revision compare and the node record.

Nothing is written into the deploy. Python runs with `-B` and `PYTHONDONTWRITEBYTECODE=1`, and the deploy's full
`git status --ignored` is compared before the run, after the environment-using setup steps, and at the end. Any
difference is a STOP.

## Differences from F1, all mechanical

- **No pilot and no budget gate.** PG's price comes from F1b′'s measured timings (director, 2026-11-23). The per-task
  timeout is F1b′'s 5,115 s (`budget3.json`), and the node's wall limit is the parent's.
- **Work directories** are `u<u>/t<k>`, not `s<seed>`, and the status file is renamed (above).
- **The truths** go through `fd_f1_prep.py --truth-set pg`, with the names `genie_v3_g21` and `genie_v3_g18_02a`. `--truth-set f1`, the default, is F1's, unchanged.
- **The PG spline pins** are in `gen5d_v3.PG_SPLINE_PINS`, apart from F1's bound `SPLINE_PINS`. They are SciSoft's
  digests from PG's offline record, and the node's bytes must equal them.
- `setup_genie_v3.sh` and `run_gevgen_v3.sh` gain the two PG qualifier cases. `setup_genie_v3.sh`'s
  `GENIE_XSEC_TUNE` check is unchanged: it requires the product to set the tune asked for.
- **Slot 1 only:** `setup_genie_v3.sh` prepends the private products directory to `PRODUCTS`, and
  `run_gevgen_v3.sh reduce` reads that copy's `gxspl-NUsmall.xml`.
- **The trace prefix:** `run_gevgen_v3.sh` runs awk, gspl2root, gevgen and gntpc under strace (execve traced) only
  when both `PG_STRACE_FD` (a descriptor above 2) and `PG_TRACE_DIR` are given. It never inherits `PG_TRACE`. With
  neither, F1's commands run byte-identically. Its `coverage` mode runs the same `gevgen_cmd` for one event at the
  public seed 123456789 with the pinned messenger. Its bytes bf49c3ec… had the director's GO for the PG path only.
  Round 4 extends its trace set, so its new sha goes to the director before it runs; it runs on NERSC only under a
  slot binding the director issues.

## Tests

`python3 -B -m pytest -q nd-unfolding/tests/test_covfix_pg.py` runs `pg_lib.py` and the PG additions on synthetic
inputs. It also runs `pg_generate.sh` end to end against a throwaway git deploy whose GENIE, ROOT and prep steps are
stubs that record their arguments. F1's own `test_fd_f1.py` passes unchanged.
