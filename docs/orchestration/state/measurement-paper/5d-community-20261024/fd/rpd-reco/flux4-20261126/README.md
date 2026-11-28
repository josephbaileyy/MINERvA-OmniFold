# RPD-RECO true-Eν flux rerun at 2415e8d6 (rpd_flux4): config and scripts (2026-11-26)

**By** limitation-resolver, for the director's binding. Nothing in this directory has run. The connect runs only on
the director's GO for its exact sha256, with a three-lane ack file (cov2d, tier3-design, minerva-lib).

## Why a fourth flux run

RPD-RECO amendment 1 (#1300, merged 2507f2d9) moves the flux factors to true Eν, read from RDX's truthx sidecar, with
C-JOIN part 1 in flux-extract. Its code is #1308 (merged at 2415e8d6). The chain from flux3 reruns in order: flux4, then
P0 (dry, then run), then d2-predict and step0, then the c0 harness, then c0. The flux3, P0 and d2s0 records stay as
history. flux4 is the first step that reads the sidecar.

The director accepted the four design defaults on 2026-11-26; this package implements them.

## What changes from flux3

[`tools/gen_flux4.py`](tools/gen_flux4.py) produces every file here from flux3's committed package by counted
replacements, and refuses any other change. It loads flux3's generator (sha256-pinned) for its block constants.

1. **The clone** moves from 6896e787 to S = `2415e8d66d1a9160e724d426eaeb54d458d4b4f7`, in the connect's `S` and in the
   job's HEAD check. Every one of flux3's 14 pins is re-read at S through `git show`. Only the four files #1308
   changed move; any other change refuses:
   - `nd-unfolding/fd_rpd_reco.py` 7302cc1d → `12f68102…`;
   - `nd-unfolding/fd_rpd_reco_custody.py` 634670b3 → `6428dead…`;
   - `nd-unfolding/tests/test_fd_rpd_reco.py` e1b92ef0 → `eee5ae4c…`;
   - `nd-unfolding/tests/fd_rpd_reco_mutation.py` f2612369 → `8dfdeaf1…`.

   These are the shas the agy read of #1308 reviewed (GO; `enu-true-code-20261124/reads/`).
2. **The config** (`production-config.ready.json`, `f53a86f6…`) is flux3's `d797183b` with these leaves only:
   - `flux_extract/path` and `flux_custody/path` move to `/pscratch/sd/j/josephrb/rpd-reco-flux4-20261126/run/`;
   - a new `true_energy` block, in the schema #1308 reads (`fd_rpd_reco.py` `Inputs.__init__`, `true_energies`,
     `omnifile_spot_check`; custody `prepare`'s TRUE_ENERGY_PIN):
     - `path` is the sidecar, `/pscratch/sd/j/josephrb/rdx-20261112b/out/dumps/truthx_RDX_ALL.npz`, and `sha256` is
       `641ba34c5ebde6d1881c705b862fab144a6fbb8a58ef3d84e59f1c8ba030a79e`. The sidecar probe of 2026-11-26 read this
       digest by O_NOATIME (`sidecar-probe-20261126/run-20261126/`).
     - `npz_sha256` is lat_zero's `6ca02c3d8b09dfd168b5184c03d433a7bd65749f5f6fc4cefecdbed7b6ce052f`.
     - `omnifiles` holds the 12 RDX omnifiles `rdx-20261112b/out/evloop/runEventLoopOmniFold_RDX_<PL>.root` with c2's
       sha256s (`run-c2-20261117/c2.session.txt:1150-1161`), read at S.

   The generator asserts the leaf diff is exactly that set. The bound `flux_selection` and every other leaf are
   unchanged.
3. **The fetch drops flux3's byte identity** with the previous run's products (step 2b). The factors now change by
   design: they are evaluated at true Eν and carry the new `energy` column. In its place, step 2b checks flux4's own
   true-energy join record in `run/flux-extract.json`:
   - status PASS;
   - the source's sha256 is the pinned sidecar, and its `npz_sha256` is lat_zero;
   - the spot rows and block rows name the 12 playlists, each spot list has at least the two ends, and its fields
     are of equal length;
   - each `run/flux-factors-<PL>.npz` has an `energy` column, 1-D float64 of its block's length, finite and positive.

   A miss exits 15 after the records are sent. That is a STOP to the director, not a reading. C-JOIN part 2 (the
   bitwise omnifile spot check) stays in P0, as placed.
4. **Fences and acks:**
   - The connect's step-2 sacct fence also watches geanttw* jobs: `tolower($2) ~ /^(cov2d|t2a|rpd|geanttw)/`. A live
     geanttw_ job refuses the connect, which puts the director's sequencing in code.
   - The launcher's connect takes one ack file of three lines, `ACK-UTC <YYYY-MM-DDTHH:MM:SSZ> <lane>`. The lanes are
     cov2d (the protected paths), tier3-design (the sidecar's owner) and minerva-lib (geanttw's lane), in that order,
     each at most 6 h old and at most 5 min ahead, followed by the ack texts. flux3's byte-exact guard is unchanged:
     one copy into the session, then validated, refusing a NUL byte, removed on any refusal, with the clock read
     checked.
5. **The overlap fence** (`tools/fence_overlap.py`) lists the sidecar among the originals custody `prepare` stages:
   `prepare` at S stages `true_energy.path` (the TRUE_ENERGY_PIN block). On this config with S as the clone:
   `FENCE staged originals 58` (flux3's 57 plus the sidecar), `FENCE OVERLAP: CLEAR (allowed 1, stops 0)`
   (`tests/fence_overlap_real_config.out.txt`).
6. **The sidecar, stat only, in the connect** (amendment 1 §8: "the flux4 and P0 connects stat each one first"): a new
   step 5b runs `stat -c '%F|%s'` on the sidecar, without following a link and without opening it. It must be a
   `regular file` of 2,364,943,114 bytes, the probe's size, or the connect STOPs (exit 3) before the job is written.
7. **Names:** the job is `rpd_flux4` and the root `/pscratch/sd/j/josephrb/rpd-reco-flux4-20261126`. Shared QOS, 4 CPUs,
   16G and `--time 01:00:00` are as for flux3.

The normalized diffs against flux3's scripts, with roots, names and blobs folded, show only these changes.

## The NuE constraint file (the director's question, 2026-11-26)

**flux-extract does open `sorted_NuEConstraint_FHC_RHC_IMD.txt`, as a staged copy.** The read is declared and logged on
flux3's terms, which flux4 keeps unchanged.
- **Where it is set:** `fd_rpd_reco.py:1921-1928` (at S) constructs
  `root.PlotUtils.FluxReweighter(14, True, "minervame"+group, gen2thin, g4numiv6, 100)`. The second argument, `True`,
  applies the NuE constraint. It runs inside `staged_mat_prefixes(prefixes)` (`:1919`), so MAT's MPARAMFILES points at
  the staged copy.
- **What is staged:** `fd_rpd_reco_custody.py:561` lists `("MPARAMFILES", "FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt")`
  among the fifteen static MAT dependencies custody `prepare` stages.
- **The declaration** (`rpd_flux4_connect.sh`, step 5 in its header): the one allowed exception to cov2d's 36 protected
  paths. Custody prepare stages it once, in one stat-bracketed staging with two O_NOATIME reads (`noatime_digest`, then
  `stage_copy`). Its `stat_before` and `stat_after` (device, inode, bytes, mtime_ns, atime_ns) are compared by
  STAGE_SOURCE_STAT and recorded with the UTC staging window. The job's `outer` stat-only log brackets the whole job in
  `exception-stat-outer.txt`, and the fetch's protected read publishes `protected-read.json`. That is condition (c)'s
  atime and mtime log. cov2d's no-objection is its line in the three-lane ack file.
- **flux3's evidence** (`flux3-20261123/run-61861637/records/`):
  - `flux-extract.strace` shows the MAT process opening only the staged copy, `…/run/mat-data/MPARAMFILES/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt`;
  - `protected-read.json` names the original and its resolved path; both copies hash to `e38ad7d2…`;
  - `exception-stat-outer.txt` shows before and after equal (mtime_ns 1630424966000000000, atime_ns 1794862761000000000).

## The price (measured; `price/`)

- **The baseline:** flux3, the same job shape, charged **0.0058 node-h** (531 s at AllocCPUS 10 of 256).
- **flux4's added work**, measured on a synthetic sidecar of the real schema and row count (32,846,302 rows,
  2.36 GB), against `fd_rpd_reco.py` at S:
  - custody-style staging (read and sha256, copy, read and sha256): 17.0 s on this Mac's SSD;
  - `true_energies` itself (C-JOIN part 1): 16.2 s, status PASS, with a **peak RSS of 1.37 GiB**.
- **The budget on Perlmutter**, allowing 4 × the staging time for pscratch: about 632 s, rounded up to 700 s, which is
  **about 0.0076 node-h**. The ceiling at the 1 h time limit is 0.039 node-h. The 1.37 GiB peak fits in the 16G
  limit, inside which flux3 ran.

## Purge exposure

The sidecar's purge exposure begins 2027-01-12T17:45:29Z, and the omnifiles' 2027-01-12T05:08Z (the probe). lat_zero's
begins 2026-12-25T08:53:42Z; flux4 compares only its digest, as recorded in the sidecar's meta, and does not read it.
The e1 chain through P0 is planned to finish well before 2026-12-20, the director's target. A purged sidecar STOPs
flux4 at the connect's step 5b, before anything is submitted. Custody `prepare`'s digest check also refuses a changed
one in the job.

## Checks on these bytes

- `gen_flux4.py`: rc 0.
- **The overlap fence** on this config at S: 58 staged originals, CLEAR.
- [`tests/test_sacct_fence.sh`](tests/test_sacct_fence.sh), cut from `rpd_flux4_connect.sh`: **27 checks pass, 18/18
  mutants killed**. It adds three geanttw cases (RUNNING, an uppercase PENDING before midnight, two COMPLETED) and a
  `family-drops-geanttw` mutant.
- [`tests/test_launch.sh`](tests/test_launch.sh), stubs and dummies only: **27 checks pass, 16/16 mutants killed**.
  - The three-lane ack: fresh; each lane stale or in the future; out of order; two lines only; padded; trailing words;
    an uppercase lane; an impossible time; seconds 60; no text; whitespace text; a NUL byte; no final newline; a failed
    clock read.
  - Also the cert, fence mode and tamper cases.
- [`tests/test_fetch_finish.sh`](tests/test_fetch_finish.sh): **11 checks pass, 5/5 mutants killed** (flux3's, renamed).
- [`tests/test_true_energy.sh`](tests/test_true_energy.sh), step 2b cut from the fetch and run on fixtures: **18 checks
  pass, 14/14 mutants killed**.
  - Each failure: status; either digest; a playlist missing from the spots or the blocks; a short or single spot
    list; NaN; infinite; negative; one row short; float32; 2-D of the block's length; no energy column; no record; a
    missing product.
  - A static check that a failed record exits 15 before the success exit.
- [`tests/test_sidecar_stat.sh`](tests/test_sidecar_stat.sh), step 5b cut from the connect against a stub GNU stat:
  **8 checks pass, 4/4 mutants killed**. The cases: a regular file of the probe's size; one byte short; a symlink; a
  symlink whose size field equals the probe's; a directory; stat failing; stat printing a matching line but failing. A static check confirms it never reads the
  sidecar and never follows a link.
- **The squeue grep:** the connect, the fetch and the launcher contain no `squeue`. The generator asserts it.

The test outputs are in `tests/*.out.txt`.

## Reads

| read | report | sha256 | verdict |
|---|---|---|---|
| agy (gemini-4-hydrogen-high), the package | `reads/agy/report.txt` | `150dc3570463e4a0adb5f66a07038113f99cb5f475199271cba11643f2adc06c` | GO |

All five of its findings are NON-BLOCKING, and all were taken:
- the connect's header comments now name geanttw* and step 5b;
- the launch test's header describes the three-lane file;
- `test_sidecar_stat.sh`'s size and type mutants now die on the cases they target (one byte short; a symlink whose size
  field equals the probe's, a case added), not on the valid case;
- `test_true_energy.sh`'s missing-energy mutant now substitutes a plausible column instead of crashing;
- `price/price.txt` notes the staging pass count and that its numbers are transcribed.

Every suite was rerun on the final bytes.

## Files and shas

| file | sha256 |
|---|---|
| `production-config.ready.json` | `f53a86f6dec50965d1d45cb77bcfc904228ebd96ffa18eb9f87babeb53d1ba1d` |
| `rpd_flux4_connect.sh` | `8989815086ec0ed771d333b109d3ef627e85dbfebe9d76d7b51f6336fe637215` |
| `rpd_flux4_fetch.sh` | `4da3ee5eb10ca6465aa5649b362ca61f8107ffdf29807a316af647820417b585` |
| `rpd_flux4_launch.sh` | `70c64e0cc155e72dfd5f99d10d26c658c358fea608b58bd874f558af54916936` |
| `tools/fence_overlap.py` | `1371a21a867739b6250175fe5fd7667f6175d055d115b5079d66f9b9070fc512` |
| `tools/gen_flux4.py` | `73d02cd0e364c85c9ce75bea214a8f93df62b155179c206847ce8b6903ba0d4a` |
