# COV2D staging from a DTN: $CV and the 10 active laterals. **STAGE PASS** (2026-11-04)

**By** the `cov2d` session, under `COV2D-BINDING-1.md` ruling 1 ("control (2a) on a login node and staging from a DTN,
next") and `COV2D-DECLARATION.md` §8 ("Lateral I/O") and §7. **MEASURES:** the staged copies' bytes against two
agreeing digest records. **CANNOT AUTHORIZE:** a job.

## What the pilot and the bulk re-check (the director's rule, 2026-11-04)

`/pscratch/sd/j/josephrb/cov2d-inputs-20261104/stage/inputs.stat`, 11 rows, mode 0440, sha256
**`3614ebadf9cb1b95340b80129e6e743e780a7979cf6392d9d64d7b56ffa02adf`** (copied here as `inputs.stat.txt`).
- **The rule:** the pilot and the bulk re-hash each staged copy against this record before reading it. A mismatch or a
  purge stops the run, with no silent re-stage.
- **The dates:** pscratch purges, so the bulk's latest submission date, 2026-12-01, stays as declared. §4.4's fallback
  (laterals carried) applies if staging is not usable by then.

## The connect

- **Script:** `connect-stage.sh`, sha256 `99fb8a66470c5c97d43807de9c6f9d3613d09ed59964cb268b088b6cde6a6e53`, approved
  before it ran.
  - Placed as `/pscratch/sd/j/josephrb/cov2d-stage-20261104.sh`, which had the same digest on dtn01.
  - It embeds the stager `cov2d_stage.py` (`8c21b24d…`) verbatim.
- **Where and when:** dtn01.nersc.gov, 2026-11-04T04:18:58Z to 04:27:56Z, 0 node-h, no job.
- **The route:** part B's (`re2/run/launch/re2b_dtn_hash.sh`), with (c)'s §7 rule added. Every source is read through
  O_NOATIME, and its atime is checked unchanged.

## What it found (`connect-stage.log.txt`)

- **The quota,** read with `lfs quota -u josephrb /pscratch`. `myquota`, which the declaration names, is not installed
  on the DTNs; `lfs` reads the same Lustre quota.
  - Before: 18,357,269,556 KiB of 21,474,836,480 (85.48 %).
  - Staging: 527,922,961 KiB, projected to 87.94 %, under the 90 % gate.
  - After: 87.94 %, and 87.95 % on a re-read at 04:29:25Z (`removal.log.txt`).
- **Before any copy:**
  - the CFS `SHA256SUMS` beside the laterals, read through O_NOATIME, hashed to its pinned
    `73775251f377a35b86c5d9433d1db63d65267525b9261f773064a1e9d17764f6` (part B's LAT_SUMS_SHA);
  - all 10 laterals' rows agreed with part B's committed DTN record (`re2/run/partb_readout/preflight/inputs.stat`);
  - so two independent records agree. `$CV`'s digest is CV_SHA, `43f8cc16…`.
- **The 11 copies, all PASS** (four workers, nice 19). For each copy:
  - its size equals the source's;
  - its sha256, re-read through O_NOATIME, equals the declared digest;
  - its stat agreed before and after the hash;
  - it was renamed from `.partial` only after these checks, and sealed 0440.

| file | bytes | sha256 |
|---|---:|---|
| `runEventLoopOmniFold_MEFHC.root` ($CV) | 2,144,008,221 | `43f8cc16…` |
| `laterals/…_BeamAngleX_0.root` | 53,845,911,012 | `38b9fc30…` |
| `laterals/…_BeamAngleX_1.root` | 53,844,600,453 | `0e0491a6…` |
| `laterals/…_BeamAngleY_0.root` | 53,845,291,390 | `058746fd…` |
| `laterals/…_BeamAngleY_1.root` | 53,845,371,537 | `3bca6a45…` |
| `laterals/…_MuonResolution_0.root` | 53,845,199,952 | `839ab9c5…` |
| `laterals/…_MuonResolution_1.root` | 53,845,210,317 | `33308006…` |
| `laterals/…_Muon_Energy_MINERvA_0.root` | 53,845,254,183 | `533037d2…` |
| `laterals/…_Muon_Energy_MINERvA_1.root` | 53,845,155,381 | `90a1d7b7…` |
| `laterals/…_Muon_Energy_MINOS_0.root` | 53,841,190,691 | `f105f681…` |
| `laterals/…_Muon_Energy_MINOS_1.root` | 53,845,919,075 | `f2e67fd6…` |

The full digests, sizes, mtimes, inodes and paths are in `inputs.stat.txt`. In all, 540.5 GB; `du -sh` prints 504G
(GiB).

- **No source's atime moved.** All 11 `src_atime_ns` values are equal before and after their copies, so the staging moved
  no CFS atime. `$CV`'s stays 1792770770214610703, the same value as in both (2a) runs.
- **Leftovers:** no `.partial` remains, and no stager process (`node_listing.txt`).

## Tests before the sha went to the director

All of them ran in a Linux container (python:3.11-slim), because macOS lacks O_NOATIME (`tests_container.txt`).
- **`test_stage_unit.py`, the stager, 7 of 7:**
  - a pass with records, 0440 copies and no `.partial` left;
  - a wrong digest gives rc 4, the file stays `.partial`, and no record is written;
  - an existing destination or record is refused;
  - a malformed manifest is refused;
  - a source whose atime moves FAILs;
  - a source whose size differs FAILs;
  - a spy shows every source read uses O_NOATIME.
- **`test_stage_glue.sh`, the whole connect** on fake CFS and pscratch trees, with `lfs` and `hostname` stubbed and the
  pins swapped for the fakes' digests:
  - everything agreeing → STAGE PASS, 11 rows, 0440;
  - quota projected just over 90 % → STOP;
  - quota projected at 89.99 % → PASS;
  - `SHA256SUMS` not the pinned file → STOP;
  - one lateral disagreeing with part B → STOP;
  - an existing target → STOP.
- **Metadata pre-checks on dtn01** (stat, `which` and `lfs quota` only):
  - python3 3.9.25 has O_NOATIME;
  - all 11 sources and `SHA256SUMS` are owned by josephrb, so O_NOATIME is permitted;
  - the target was absent.

## Removals and what stays

- **Removed** (`removal.log.txt`, 04:29:25Z): `/pscratch/sd/j/josephrb/cov2d-stage-20261104.sh` (`99fb8a66…`, checked
  first), rc 0, absent after.
- **Stays**, as part B's did: `/pscratch/sd/j/josephrb/cov2d-inputs-20261104/` (the 11 copies) and its `stage/`
  directory, which holds `inputs.stat`, `connect-stage.log`, `manifest.tsv`, `SHA256SUMS.copy` and the stager.
  - These are this lane's own new pscratch files, as §7 says. Each is exposed 8 weeks after its last read.

## Files

| file | what |
|---|---|
| `connect-stage.sh`, `cov2d_stage.py` | the connect as run; the stager embedded in it |
| `test_stage_unit.py`, `test_stage_glue.sh`, `tests_container.txt` | the tests and their container output |
| `connect-stage.log.txt` | the run's log |
| `inputs.stat.txt` | the record, the re-hash reference (sha256 `3614ebad…` as on pscratch) |
| `manifest.tsv`, `SHA256SUMS.copy.txt` | the copy manifest; the CFS SHA256SUMS as read |
| `node_listing.txt`, `removal.log.txt` | the stage directory's listing and digests; the removal |
