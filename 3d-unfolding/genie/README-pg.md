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
   - `record/root-schemas.json` lacks the `gst` (gntpc's) or `gst_merged` (hadd's) schema. Both stay unset until
     B3's replay records them and the director confirms them;
   - the core limit cannot be set to 0. Every process of the job then writes no core, under W or anywhere (Q2).
1. strace is opened once on fd 9. `pg_verify.py tool-check --fd 9` reads its sha256 through that inherited
   descriptor (no path is opened: `/proc/self/fd/9` is a magic link that O_NOFOLLOW refuses), and its self-test runs.
   CVMFS's revision and root hash are recorded now and at the end. If they differ, every CVMFS file the run read must
   re-hash equal to its pin (`revision-compare`), or it is a STOP. `node-record` then records the compute node's
   `/proc` mount options (hidepid) and the allocation's exclusivity. F1's argv carries the seed, so this is the
   boundary on record (C3); the seed never reaches the sbatch line, the job name, `--comment`, the batch script or
   the exported environment. Every pinned CVMFS file (the genie manifest's 3,673 files and 58 links, and each CVMFS
   tune's spline and README) is hashed before anything is traced and again after the last trace check (`pin-hash`,
   Q1). Each must equal its pin both times, and both hash sets are kept.
2. The private product is checked against every pinned member. Its top level must be exactly `.upsfiles` and
   `genie_xsec`; `genie_xsec` itself is a container, not a member, and `.upsfiles` holds only a read-only dbconfig.
3. Each tune's setup resolves `gevgen`, `gspl2root` and `awk`, and records `LD_LIBRARY_PATH` and `GXMLPATH`.
   - The programs are checked against the genie manifest, by bytes and by real path.
   - awk must be a root-owned system tool, by its own path and its real path.
   - No LD_LIBRARY_PATH entry may be empty or lie outside CVMFS and the system library directories.
4. reduce, gspl2root, a one-event coverage run per tune, every gevgen and every gntpc run under strace (open, stat,
   access, readlink, chdir, the execve and execveat, rename, link, symlink, unlink, mkdir, mknod and truncate
   families). Their traces are
   checked; `pg_verify.py`'s docstring lists the rules, and every refusal names a reason code. In outline:
   - each role starts with its own program (awk, gspl2root, gevgen, gntpc), and every exec is resolved and bound to
     the manifest or a pinned system tool. Since round 9, ROOT 6.22's interpreter under a GENIE program may also run
     its pinned family (`pg_pins.json` `interpreter_tools`: sh as bash, ls, sed, ldd, both loaders, CVMFS gcc v9_3_0's
     g++ and cc1plus), only as a child process, only in the ROOT programs' roles, and only with the command lines B3
     run 3 showed; ldd's 32-bit loader probe alone may exit 1;
   - nothing is written, truncated, renamed, created or unlinked outside W (/dev/null aside), and no link is made
     anywhere. An open that creates a file without truncating it counts as an output only at the role's expected
     path, after the same process last found it absent or unlinked it (ROOT's RECREATE); a later open is a read;
   - gntpc reads exactly the GHEP its own task's gevgen created, and writes its gst;
   - each tune's XML is found by GENIE's own search (XmlParserUtils, AlgConfigPool): every searched read follows a
     walk of GENIE's list from its head, all but the last absent, with the tune and CMC directories only once the
     tune is configured, and AlgConfigPool's re-probe of the path found. The file read must be the first that exists
     on that list. An explicit path must have been tried in every directory first;
   - the pinned spline is read, and the coverage run reads its pinned messenger;
   - nothing else under a genie_xsec data directory is read, and a read that cannot be resolved is a STOP;
   - every ROOT and GENIE library comes from CVMFS and is hashed; other shared libraries come from CVMFS or a system
     library directory;
   - `..` paths are resolved on the node by their full real path.
5. The reduce keeps every spline for each (probe, target) pair of F1's argv, parsed as XML the way GENIE reads it
   (a commented-out spline is not one), compared by tune, key, the knots counted against nknots and their values,
   with duplicates refused (`reduce-check`). The coverage run uses the public seed, F1's argv (`argv-check`: its
   block sets only N, the seed and the messenger, and the genie block only F1's positional inputs and the laconic
   messenger) and a messenger with only GEVGDriver and XSecSplLst at DEBUG.
   In flux mode gevgen builds each driver's sum spline in Configure, before any event (GMCJDriver.cxx:399-447), so one
   event covers the bootstrap. Before any sealed seed is used, `coverage-log` reads its log as D3′(ii) was adopted
   (pg/DESIGN-D3PRIME-II.md §3, Joseph 2026-11-27). For each pair of F1's argv it requires:
   - one driver, whose UseSplines lookups, all found, are its required inventory, each a full key of the reduced
     spline in its tune;
   - one sum spline of N knot blocks, N from the driver's own record, each looking up and evaluating exactly that
     inventory from its spline;
   - none of GENIE's missing-spline messages.
   The coverage mode writes gevgen's stderr to its own file, gevgen.err. GENIE's one log appender writes to cout
   (Messenger.cxx:62), so every record is in gevgen.log, and an unbuffered ROOT warning cannot land inside a buffered
   record. The stderr file is hashed and its lines counted, never parsed.
   On a pass the run's outputs are deleted and the log's hash is kept. On a STOP (§4) the public-seed event, status,
   GHEP and flux files are deleted, and only the log's recognized records are kept (`coverage-keep`, with the raw
   log's hash and size). The replay runner's `--keep-coverage-records` keeps them on a pass too, for validation;
   production has no such flag.
The generation runs in its own session (setsid). GNU timeout gives each task a process group of its own, but the
session survives that and any reparenting. On any exit, every background step's tree is stopped and reaped, then
`pg_verify.py drain` KILLs every survivor in that session, again at each poll, until none is left or 30 s (monotonic)
have passed. A process outside the session with a cwd under W, other than this shell's parent chain, is a STOP and
is not killed: it may be the parent's. A process list that cannot be read is a STOP. The drain runs before
publication and before seed-named files are renamed, and each guard logs a count-only line when it fires
(`state/2d-closeout/covfix-20261122/pg/REHEARSAL-CHECKLIST.md`). A failed rename is a STOP that names no path. Every check's pass is recorded in PRODUCTS.json. `pg_lib.py publish`
then:
- lists the outgoing set from an explicit allowlist. Any other file outside W/tmp, seed-bearing ones aside, is a STOP;
- scans every outgoing file's path and bytes, apart, for the seeds in decimal, hex and int64 (both byte orders):
  - each ROOT file's keys and free gaps must cover fBEGIN to fEND exactly, with nothing after it;
  - every ROOT object is inflated (ZLIB, LZMA, ZSTD, LZ4), each block exactly one complete stream, and so is any
    old block a free gap still holds. Any other codec is a STOP;
  - gzip files and every zip (npz) member are inflated. Any other compressed container is a STOP;
- treats int32 matches as a STOP in every ROOT object but a TBasket's payload. In baskets and raw bytes they are
  counted against their chance expectation and recorded;
- checks each gst's keys and streamer info against B3's schema of its kind: gntpc's for the task gsts, hadd's for
  `out/gst/*_ALL.gst.root`;
- writes `out/leak_scan.json` and `out/PG-PUBLISH-SHA256SUMS`, and scans both. Both stay in W and are sealed with it
  (at PG nothing leaves W but ciphertext; the publish set leaves only at PV's decrypt step).
The deploy's last snapshot is taken before the publish set is listed, so it is published and scanned. After
publication the deploy is compared once more, without writing a file. A STOP after publication withdraws both files. The required inventory (`pg_lib.py inventory`) is checked last.

**B3 (`pg_replay.sh`)** runs these checks for slot 1 on a login node, then:
- slot 1's coverage run, one 100-event public-seed gevgen and gntpc (bound to that gevgen's GHEP), and hadd of
  that gst under pg_generate's own output name, so both schemas come from the real writers;
- slot 2's traced reduce at its real CVMFS path, its completeness and its coverage run;
- the four real-shape checks (`shape-check`) and three host checks (`host-check`), which must pass there before slot 2
  is generated.
A trap deletes the public-seed event and status files on every exit. Every unlink is tried even when reading the
file fails, and any file left is a failure. Each file's entry is written before it is unlinked, and an unreadable
earlier record is noted, not trusted. `deleted.json` keeps each file's hash and size, each ROOT file's decoded scan
(its name's hit apart from its bytes') and both gsts' schemas. `replay.json` (`covfix-pg-replay-run/4`, 24 checks
including both pin hashes) carries them with each trace's execs and both CVMFS revisions. The node runner forwards
the whole record, KILLs what is left of the driver's session, and removes and reports any event file left on every
exit. agy's and codex-school's reads, and their dispositions, are in
`state/2d-closeout/covfix-20261122/pg/AGY-READ-A2.md`; round 4's are in `pg/delta-read-r4/`, round 5's in
`pg/delta-read-r5/`.

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

pg_generate's environment is exactly the gen-spec's `env_keep` names (their values inherited from the site), its
`env_set` literals (pinned with the gen-spec's sha256, and a run is refused if the inherited value differs), and
`TMPDIR`, which covfix_pg sets to `W/tmp` and neither list names (cov2d, rev 12 §4.2, 17c00b1b). The split below is
this lane's proposal for the gen-spec; its author decides.

| variable | gen-spec | why |
|---|---|---|
| `PG_DEPLOY_PIN` | env_set (first) | the full commit sha the deploy must be at. The executable refuses without it |
| `PATH` | env_set: `/usr/bin:/bin` | bash, git, awk, xargs, `/usr/bin/time`, timeout, sha256sum, find, sort, cmp, hostname |
| `HOME` | env_keep | `setup_salloc_env.sh` activates `$HOME/.conda/envs/root_6_28`. `setup_genie_v3.sh` reads the compat-lib shim at `$HOME/.genie_compatlibs` |
| `SLURM_JOB_ID`, `SLURM_CPUS_ON_NODE` | env_keep | read by `node-record` only. Without them, `node_check.json` records `slurm_job` and `all_cpus_allocated` false |
| `SCRATCH` | neither | not needed: `setup_salloc_env.sh` reads it only for the TMPDIR it sets (then overridden with `W/tmp`) and a CODEX_HOME nothing here reads, and it has no `set -u`. The driver tests run without it. Left out, pg_generate cannot learn a path outside W that cov2d's spill scan (which covers `$SCRATCH/tmp`) would miss |
| `GENIE_COMPAT` (optional) | env_set, if used | overrides the shim directory, as in F1. Since round 8 the shim is allowed only as pinned in `pg_pins.json` `compat_libs` (its real directory, and libssl.so.10, libcrypto.so.10 and libxxhash.so.0 at their real targets and shas): exe-check refuses any other directory, trace-check any other library outside the roots, and pin-hash hashes the three at the start and the end. **libxxhash.so.0's target is the analysis conda env's `root_6_28/lib/libxxhash.so.0.8.2` on the home filesystem, with no revision tracking**: a change by `conda` is caught only by those two hashes, which fail closed. The libssl and libcrypto targets are on minerva.opensciencegrid.org, whose revision is recorded at the start and the end like larsoft's |
| `ROOT628_PREFIX`, `ROOT628_CONDA` (optional) | env_set, if used | override the analysis environment's location, as `setup_salloc_env.sh` allows |
| `TMPDIR` | neither | must be `W/tmp`. It is re-exported after every environment activation, because `setup_salloc_env.sh` sets `TMPDIR=$SCRATCH/tmp` |

It needs no network, no passphrase and no GNUPGHOME: encryption is the parent's.

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
  counts. Both are scanned. At PG they are sealed with the rest of W, `out/` included: nothing leaves W but
  ciphertext, and the publish set leaves only at PV's decrypt step (the director's ruling 4, 2026-11-25).
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
  Rounds 4 and 5 extend its trace set, so its new sha goes to the director before it runs; it runs on NERSC only under a
  slot binding the director issues.

## Tests

`python3 -B -m pytest -q nd-unfolding/tests/test_covfix_pg.py` runs `pg_lib.py` and the PG additions on synthetic
inputs. It also runs `pg_generate.sh` end to end against a throwaway git deploy whose GENIE, ROOT and prep steps are
stubs that record their arguments. F1's own `test_fd_f1.py` passes unchanged.
