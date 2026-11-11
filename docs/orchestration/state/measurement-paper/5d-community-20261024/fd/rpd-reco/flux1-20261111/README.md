# RPD-RECO flux connect 1: the READY candidate and the batch-job connect (revision 2, DRAFT for coverage-5b-audit, 2026-11-11)

**By** the limitation-resolver lane, at the director's request of 2026-11-11. **Draft only.** Nothing here has run on
Perlmutter. The connect runs only on the director's go for its exact sha256, after these four steps:
1. the audit's GO;
2. #848's merge;
3. binding 2;
4. the director's announcement of the job name `rpd_flux1` to every fenced lane.

P-RPD stays closed.
<!-- absence-ok: the document's own status (a draft that has not run), not a claim that a result does not exist -->

**Revision 2** answers the audit's NO-GO at `cb9f3e00` (F1 blocker, F2 major) and the director's rulings of 2026-11-11:
- F1: the factor products stay on pscratch;
- F2: the run is a Slurm batch job, not a login-node process;
- point 3: the fixed label;
- point 4 (a)-(c): the fences and the single protected-path exception, with cov2d's no-objection and its
  stat-receipt condition.

**20261111 is a fixed label naming this config, not the run's date.** It stays the directory's name whenever the job
runs. The receipt records the actual run times separately (`job-host.txt`, sacct's Start and End).

## The code it runs

#848's flux wrapper and producers, unchanged except for one addition this revision makes for cov2d's condition. The
addition is proposed into #848's branch as its own PR, #1072, `code/rpd-reco-stage-time-20261111` at `2d05eb7fdf7fddaae8d482130e67ad039d517c6c`:
- custody `prepare`'s `copy()` records `staging_utc_ns` (`started`, `ended`, the UTC wall time around its stat
  bracket) beside the `stat_before` and `stat_after` it already records;
- the new test `test_prepare_records_stat_bracket_and_staging_time` fails if any staged item, the MPARAMFILES exception
  included, lacks either stat (device, inode, bytes, mtime_ns, atime_ns) or the staging window.

Its receipts are in `fd/rpd-reco/stage-time-20261111/` on that branch.

The connect pins that head by sha. When the director merges it into #848, `tools/gen_flux1.py` regenerates the three
scripts at the merged head in one command, and their new shas go to the director. The files the job pins, at
`2d05eb7f`:

| file | sha256 |
|---|---|
| `nd-unfolding/fd_rpd_reco.py` | `7302cc1df71758cfae6bdcfba031d37cc78902beaf454b29e12f3e053d44f141` |
| `nd-unfolding/fd_rpd_reco_custody.py` | `867822e3cbf7063088717565d2be4e68ae3625cb24ce468255d98ba8fd59bdb5` |
| `nd-unfolding/fd_rpd_inputs.py` | `6e4ed0f1d7f55b7bfe2f26752eeb28bb9cbe33325a9d91cc7c06d9494a0b0a70` |
| `nd-unfolding/fd_rpd_reco_flux_connect.sh` | `32db52355a4811bd4bf5f8b8cc0b5c397c7b403a0996048bcafd8c8c665cc76e` |
| `nd-unfolding/tests/fd_rpd_reco_mat_check.py` | `06360100038f0203b0d994f71c171b12cd955697edf32d1d744c4ce271ceb26d` |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rpd-reco/timing-20261106/flux-gen2thin-pdg-14-minervame1M_rearrangedUniverses.root` | `d9704aa45c016b044284d9e3cfc8c6d5c07cda0835a445866d5f792c8ac82840` |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rpd-reco/INPUTS.sha256` | `7638f94f56ad0471769445cffe68ff538c9b68158f48415e7c3cafa7ee95a295` |
| `nd-unfolding/pv-ladder/readouts/h2_definition.json` | `b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89` |
| `docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/flux-pot-provenance-20261104/energy-spectrum-candidates.tsv` | `e60609e756e35fbc9846ae5983c1d848999bc17c7504e3ca876c22c9bcc0e88f` |
| `MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h` | `900d7368d6184d503399bd99c0fd30085212df0327b8be374182495b85a3677d` |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rpd-reco/code-audit-fix-20261106/MAT-DATA-DEPENDENCIES.json` | `b056487e592e7704c2a98c14243b26f44c82821382837a263b75c169859cce0b` |

## 1. The READY candidate (unchanged from revision 1)

[`production-config.ready.json`](production-config.ready.json), sha256
`cde8d02904b0257d82745b03fd61c1aef1a50270f14f36ad7f38c8b3f235f50b`. The audit found it right.

Its changes from the audited proposal are exactly three:
- `configuration_status` is `READY`;
- `${RUN_DATE}` → `20261111` in `flux_extract.path`;
- the same in `flux_custody.path`.

[`tests/check_candidate.py`](tests/check_candidate.py) checks it against `a4c3e556`'s code:
[`tests/CANDIDATE-CHECK.txt`](tests/CANDIDATE-CHECK.txt). The config does not pin code, so the code PR leaves it
unchanged.
<!-- absence-ok: the config's own fields (it binds data and MAT files by path, not code), not a claim about a result -->

Fields left for runtime by design:
- `flux_selection.*.retention` stays `AWAITING_RUNTIME_STAT_AND_STAGED_RETENTION_RECORD`;
- the `premise` booleans stay null.

The flux stage carries retention as a string (`fd_rpd_reco.py:1150`) and reads `premise` only at P0 (`:2137`). P0
needs its own READY config with both measured.

## 2. Where each step runs

| where | step |
|---|---|
| login node, [`rpd_flux1_connect.sh`](rpd_flux1_connect.sh) | 1. refuses unless `/pscratch/sd/j/josephrb/rpd-reco-flux-20261111` is absent |
| | 2. **fence (a):** a queued or running job of ours named `cov2d*`, `t2a*` or `rpd*` refuses. LL5D and E96D jobs pass. The launcher's `fence` mode runs the committed `cov2d_fence.sh` (`16a2a5cd…`) first |
| | 3. fresh clone at `2d05eb7f` into `<root>/clone`, with HEAD, porcelain and the 11 pins checked |
| | 4. the READY config, written from the script into `<root>/`, sha256-checked |
| | 5. **fences (b) and (c):** [`tools/fence_overlap.py`](tools/fence_overlap.py), described below |
| | 6. the job script, written from the script; `sbatch`; then scontrol's `JobName=rpd_flux1`, `TimeLimit=03:00:00`, `QOS=shared` and `Account=m3246` are checked, and the job is cancelled on any difference |
| compute node, job `rpd_flux1` | 1. copies the clone to `/dev/shm/limres-rpd-flux1/repo`, the path the config binds, and rechecks HEAD, porcelain and the 11 pins |
| | 2. copies the config there, sha256-checked |
| | 3. the strace probe |
| | 4. an outer `stat` of the exception file (no open) before and after the wrapper, in `exception-stat-outer.txt` |
| | 5. #848's `fd_rpd_reco_flux_connect.sh` unchanged, writing `connect.log`. Its steps: `check-mat-setup`; the MAT setup; the real-MnvH1D check; custody `prepare` (staging, its COV2D fence, NATIVE_SELECTION, the 15-file MAT inventory, the exception's read); the missing-dependency check; `flux-extract` under strace; `trace-check` |
| | 6. removes its `/dev/shm` directory, then writes `job.rc` and `job-host.txt` (jobid, host, start and end UTC) |
| login node, [`rpd_flux1_fetch.sh`](rpd_flux1_fetch.sh) | reports and sends the records (section 4) |

The login steps read no input, load no MAT or ROOT and run no producer. The clone and the overlap fence are file
metadata and git only.

**The job.** It runs in the shared QOS with 4 CPUs, `--mem=16G` and `--time=03:00:00`, on `-C cpu` under account
m3246. Its output goes to `job.out` and `job.err` under the root. Nothing is written to CFS, and nothing is written
outside the root and the job's `/dev/shm`.
- **Wall basis.** Prologue 5's data-free wrapper ran in 29 s (`../prologue5-20261108/connect5.out`, 23:43:21Z to
  23:43:50Z). That covers the MAT setup, ROOT's start and the traced worker, with no input staged.
  - This run adds the staging of 1.58 GB: the 24 dumps, each read once by `stage_copy` and its copy read once by
    `digest`.
  - It adds two more ROOT starts.
  - It adds `flux-extract`. No measurement of flux-extract exists. Search: git grep -il flux-extract @ 68be035e (origin/main; only the five prologue policy-config.json files, which name it; no flux-extract.json and no timing record). Its own guard bounds it: `DEFAULT_WALL_SECONDS` is
    7,200 (`fd_rpd_reco.py:59`), checked after each playlist (`:1932`, WALL_CLOCK), so it can overrun by at most one
    playlist.
  - So 03:00:00 is the 2 h guard, one playlist's overrun, and staging and setup with margin.
  - A run past 7,200 s inside the extract STOPs at WALL_CLOCK, and that STOP is the result.
- **Memory basis.** The largest playlist is 1M, at 5,916,895 MC rows. In `flux-extract`, the five-column `MCgen`
  (237 MB), the energy arrays (about 0.3 GB) and `mat_flux_swap`'s 3×N and 2×N float64 work arrays (about 0.25 GB) come
  to about 1.3 GB. ROOT and MAT add about 1 GB, so the estimated peak is about 2.5 GB. 16G is about 6× that.
- **Price.** At most 3 h × 1/32 node ≈ **0.094 node-h**. 1/32 is the larger of 4 of 256 CPU threads and 16 of 512 GB.
  If the shared QOS were charged as a whole node, the bound is 3 node-h. sacct's Elapsed sets the charge.

## 3. The protected-path exception (rulings (b) and (c); cov2d's no-objection and condition)

`tools/fence_overlap.py` (`baa7630936db399abf57aa6edf9af1ffc053a3ee80c3730981a806fd8598a202`) runs on the login node before `sbatch`, under MAT_PYTHON with the clone's
own modules. It STOPs (exit 3) in two cases:
- either write root (`/pscratch/sd/j/josephrb/rpd-reco-flux-20261111`, `/dev/shm/limres-rpd-flux1`) overlaps any of
  cov2d's 30 protected paths, in either direction;
- any original `prepare` stages overlaps one.

The 57 staged originals are:
- the six bound files and `flux_source`;
- the 24 pins;
- the three C-N files;
- the closed 15-file MAT set, under prologue 5's recorded prefixes;
- the nine MAT setup and library files `fd_rpd_inputs` pins.

There is one exception, named by full path:
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt`.
It is allowed only when both the read and the protected entry are exactly that path. A protected directory that holds
it still STOPs.

Overlap is equality or containment. It is tested on paths as written and after `realpath`, which reads symlinks and
never file contents.

**How custody stages the exception at `2d05eb7f`: one stat-bracketed staging, with two O_NOATIME reads.**
- `copy(source, None)` takes `source_stat` (device, inode, bytes, mtime_ns, atime_ns; no open).
- It reads the file through `noatime_digest`, then through `stage_copy`, both read-only under O_NOATIME.
- It takes `source_stat` again. STAGE_SOURCE_STAT STOPs the run unless the two stats are equal.
- `stage_copy` checks the copy's sha256 against the measured one, and the native lookup copy under `run/mat-data` is
  staged from that copy with the same check.
- It records `stat_before`, `stat_after` and `staging_utc_ns` in the private prestage record.

The traced `flux-extract` opens only the staged copies. `trace-check` refuses any open under a protected root.

**The receipt carries the stat lines (cov2d's condition, binding).** The private record is never sent. The fetch's
[`tools/protected_read.py`](tools/protected_read.py) (`309f59d46a4f200d924c98cd6beeece9a8c9a2b92cd493fb2e84f6b5693aa7f9`) therefore writes `protected-read.json`, which
is sent, with these contents:
- the exception's original, as listed and resolved;
- the sha256 prepare measured;
- the sha256 of both staged copies, recomputed from the copies (the original is not read again);
- `stat_before` and `stat_after` with all five fields;
- `staging_utc_ns` and its ISO form;
- every staged original that overlaps a protected path.

It FAILs if any field is missing or malformed, if the stats differ, if a copy's sha256 differs, or if any other staged
original overlaps a protected path. A FAIL is sent as the finding, and the fetch exits 11.

`exception-stat-outer.txt` adds a stat of the same file before and after the whole wrapper, for LL5D's atime
attribution.

## 4. The fetch

`rpd_flux1_fetch.sh` (`58079f4824de9c0aaecdbc2cb54617bd4153f1210edc3ca0354e72fc0ebb7445`), on any login node.
- **When the job counts as finished.** It is finished when `job.rc` exists, or when sacct gives the jobid a terminal
  state. A job killed at its limit or out of memory writes no `job.rc`.
- **Until then** it prints `job.id`, `job-host.txt`, sacct's and squeue's rows, writes nothing and exits 10.
- **Once finished, it prints:**
  - sacct's row (State, ExitCode, Elapsed, Start, End, NodeList, MaxRSS, AllocCPUS, ReqMem, Timelimit);
  - a listing of the root, without the clone;
  - for each `run/flux-factors-<PL>.npz`, its size and sha256, compared with the sha256 `flux-extract.json` records.
    **The factor products are never sent (F1).**
- **The send list:**
  - the root's records: `job.id`, `job-host.txt`, `job.rc`, `job.out`, `job.err`, `rpd_flux1_job.sh`, `connect.log`,
    `strace-probe.txt`, `fence-overlap.txt`, `exception-stat-outer.txt`, `protected-read.json`;
  - the regular files directly in `run/` except the factor products;
  - those in `run/real-mnv-check/`.
- **Never sent:** `run/original-inputs`, `run/mat-data`, `run/prepare-check`, `run/tmp`, `clone`, `tools` and
  `.rpd-private`. A send list over 64 MiB refuses.
- **The checks.** It then runs prologue 5's C3 (`tools/c3_check.py`, `aed41794b72d8b8de6580d75e0fc4467cad3bc73c5b11dfac44075783b461192`) and the redaction check
  (`tools/check_redaction.py`, `992be729…`, byte-identical, VIEW NONE) as in revision 1. Point 2, sending with no
  private record, is accepted (director, from the audit's reading).

**Left in place on pscratch** for deletion after the receipt merges, by a separate connect under a ledger row:
- the root: the factor products, the staged copies, the clone and the private record.

The job removes its own `/dev/shm` directory.

## 5. Files and shas

| file | sha256 |
|---|---|
| [`rpd_flux1_connect.sh`](rpd_flux1_connect.sh) | `f5bc999483bc2c2151b96361c526fc4dad98c8986eda569c9fb37710b48908d0` |
| [`rpd_flux1_fetch.sh`](rpd_flux1_fetch.sh) | `58079f4824de9c0aaecdbc2cb54617bd4153f1210edc3ca0354e72fc0ebb7445` |
| [`rpd_flux1_launch.sh`](rpd_flux1_launch.sh) | `9f6daccb60524b915a22767c117a56b367d112f1b3e5b35c2a4cab2c50f73c27` |
| `rpd_flux1_job.sh`, as the connect writes it (a literal heredoc) | `bc2327b1d38c09bca30491df95111676d82300cda7d3aa7cbcdc4ee4228605c6` |
| [`tools/fence_overlap.py`](tools/fence_overlap.py) | `baa7630936db399abf57aa6edf9af1ffc053a3ee80c3730981a806fd8598a202` |
| [`tools/protected_read.py`](tools/protected_read.py) | `309f59d46a4f200d924c98cd6beeece9a8c9a2b92cd493fb2e84f6b5693aa7f9` |
| [`tools/c3_check.py`](tools/c3_check.py) | `aed41794b72d8b8de6580d75e0fc4467cad3bc73c5b11dfac44075783b461192` |
| [`tools/check_redaction.py`](tools/check_redaction.py) | `992be729a3604cf8bae7ea04dfab93aeae9e259b647d3a4d598fd287b2736316` |

[`tools/gen_flux1.py`](tools/gen_flux1.py) generates the three scripts from the templates in `tools/`:
`python3 -I tools/gen_flux1.py . <S> <repo>`. It reads the 11 pins from git at S, embeds the config and the three
node-side tools in base64, and asserts the config's and the redaction check's sha256s. Every other file's sha256 is in
`SHA256SUMS`.

## 6. Tested locally (macOS), on these bytes

- **The fetch,** in [`tests/FETCH-TESTS.txt`](tests/FETCH-TESTS.txt) from [`tests/test_fetch.sh`](tests/test_fetch.sh).
  It runs ten fixtures, built with `a4c3e556`'s own `write_private_prepare`. The fixture's exception path is
  substituted into a tools copy for the test.

  | fixture | rc | what happened |
  |---|---|---|
  | unfinished (sacct RUNNING) | 10 | nothing written |
  | timeout (no `job.rc`, sacct TIMEOUT) | 0 | sent |
  | full: 12 factor products totalling 600 MiB, recorded in `flux-extract.json` | 0 | 12 shas equal; 21 files sent and no product; protected read PASS |
  | leak | 7 | refused |
  | orphan | 7 | refused |
  | no private record | 0 | sent |
  | the string `fingerprints` | 7 | refused |
  | a 70 MiB non-product file | 7 | refused |
  | the exception without `staging_utc_ns` | 11 | protected read FAIL, sent |
  | another staged original under a protected path | 11 | protected read FAIL, sent |

- **The fence,** in [`tests/FENCE-TESTS.txt`](tests/FENCE-TESTS.txt) from [`tests/test_fence.sh`](tests/test_fence.sh).
  It runs seven cases on the READY config and variants of its protected list:

  | case | result |
  |---|---|
  | the READY config | CLEAR, the exception allowed once |
  | the dump root protected | STOP, 24 |
  | a protected parent of the write root | STOP |
  | the exception's directory protected | STOP |
  | the clone protected | STOP |
  | a C-N file protected | STOP |
  | the exception unlisted | CLEAR, nothing allowed |

- **End to end,** in [`tests/E2E.txt`](tests/E2E.txt) from [`tests/test_e2e.sh`](tests/test_e2e.sh), with the detail in
  [`tests/E2E-CONNECT.txt`](tests/E2E-CONNECT.txt), [`tests/E2E-JOB.txt`](tests/E2E-JOB.txt) and
  [`tests/E2E-FETCH.txt`](tests/E2E-FETCH.txt) (the job script's sha256 there is the test copy's).
  - The connect ran with a local repository as the clone URL, at `2d05eb7f`. Its 11 pins matched, the config
    matched, and the fence was CLEAR at 57 originals.
  - The `sbatch` shim ran the job script locally. The job copied the clone, rechecked the pins, ran the strace probe
    and ran #848's real wrapper, which refused at `check-mat-setup` (no MAT here). It wrote `job.rc` rc=7 and removed
    its `/dev/shm` directory.
  - The fetch then sent the records.
  - Three refusals: an `rpd` job queued gave rc 3; a TimeLimit other than 03:00:00 gave scancel and rc 6; a second
    connect on the same root gave rc 9.
- **Shims and substitutions.**
  - Shims in `tests/shim/` stand in for `hostname`, `squeue`, `sbatch`, `scontrol`, `scancel`, `sacct` and strace.
  - Three more stand in for GNU forms macOS lacks: `find -printf`, `stat -c %s` and `base64 -w`.
  - The test copies substitute only the literal roots, MAT_PYTHON, the clone URL, `/usr/bin/strace` and `/bin/true`.

**What these tests do not reach.** None of them covers:
- MAT, ROOT, strace or Slurm on Perlmutter;
- the wrapper past `check-mat-setup`;
- the launcher's ssh hops.

The launcher's lines are `rpd_mnv_check2_launch.sh`'s, which ran on 2026-11-11 (#1062).
<!-- absence-ok: the scope of the local tests, stated so no reader takes them for an on-node run -->

Nothing is submitted, deposited or tagged.
<!-- absence-ok: the document's own status line -->
