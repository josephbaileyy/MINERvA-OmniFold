# RPD-RECO P0 for e1 at 2415e8d6 (p0e1): config and scripts (2026-11-26)

**By** limitation-resolver, for the director's binding. Nothing in this directory has run. The connect runs only on
the director's GO for its exact sha256. It needs a three-lane ack file (cov2d, tier3-design, minerva-lib), and ibu-chi
is asked by message first.

P0 is still **login-only at 0 node-h, with no job and no job-name family** (FD-RPD-RECO-DECLARATION section 5;
BINDING-1 ruling 3). Everything about how it runs (the connect's steps, the detached runner, the supervisor, the single
deadline, the RSS cap and the fetch) is p0-20261123's, as bound under `FD-RPD-RECO-BINDING-2-ADDENDUM-3.md` and
described in [`../p0-20261123/README.md`](../p0-20261123/README.md). This README covers only what changes.

## Why P0 again

RPD-RECO amendment 1 (#1300) reruns the chain flux4 → P0 (dry, then run) → d2-predict + step0 → the c0 harness → c0,
each step bound separately.
- **flux4** ran as job 62051670 and was accepted (receipts PR #1403, `../flux4-20261126/run-62051670/`).
- The bound P0 package reads flux3's records at the old S, `6896e787`, with reco `7302cc1d` and custody `634670b3`. It
  cannot run e1.
- **C-JOIN part 2** is already in the bound code at S. `omnifile_spot_check` (`fd_rpd_reco.py:2307-2414`) is called
  in `p0` (`:2514-2516`) as P0's first use of flux4's output. No code changes for this package.

The director accepted the plan and both defaults on 2026-11-26.

## What changes from p0-20261123

[`tools/gen_p0e1.py`](tools/gen_p0e1.py) generates every output from the bound P0 files, each pinned by sha256, by
counted replacements. Every count is asserted. It also asserts that no `flux3`, `61861637`, old root or old S remains
outside the new headers.

1. **The clone and pins.** The clone moves to S = `2415e8d66d1a9160e724d426eaeb54d458d4b4f7`. P0's 14 pins are
   compared row by row with flux4's connect, and each of flux4's is re-read at S through `git show`. Exactly four move,
   the files #1308 changed:

   | pin | p0-20261123 | p0e1 |
   |---|---|---|
   | `nd-unfolding/fd_rpd_reco.py` | `7302cc1d` | `12f68102` |
   | `nd-unfolding/fd_rpd_reco_custody.py` | `634670b3` | `6428dead` |
   | `nd-unfolding/tests/test_fd_rpd_reco.py` | `e1b92ef0` | `eee5ae4c` |
   | `nd-unfolding/tests/fd_rpd_reco_mutation.py` | `f2612369` | `8dfdeaf1` |

2. **The config** (`production-config.ready.json`, `f92d034d…`) is flux4's bound `f53a86f6` with exactly two leaves
   filled:
   - `flux_extract/sha256` = `060d4401…`;
   - `flux_custody/sha256` = `819bb7b9…`.

   Both are run-62051670's committed records. Against P0's `3b2afde4`, the leaf diff is asserted to be:
   - the two record paths (flux3's root to flux4's);
   - the two digests;
   - the added `true_energy` block: the sidecar, lat_zero's digest, and the 12 omnifile pins at c2's sha256s.

   The selection digest stays `75c2a1f4…`, as flux4's extract records it.
3. **The in-place inputs** (`tools/p0_expected.json` `inputs`) are flux4's extract, custody record and 12 factor
   products under `/pscratch/sd/j/josephrb/rpd-reco-flux4-20261126/run/`, at run-62051670's committed sha256s. The
   connect's step 5 reads them with O_NOATIME and STOPs on any difference, as before. Its record is now named
   `flux4-inputs.txt`.
4. **The fences.**
   - **The step-2 sacct block** is flux4's: geanttw* is added to cov2d*, t2a* and rpd*. The generator asserts that the
     block is byte-identical to flux4's connect.
   - **The launcher's ack guard** is flux4's three-lane guard (`gen_flux4.LAUNCH_ACK3`) in place of flux3's one-lane
     guard. It takes three lines, `ACK-UTC <time> <lane>`, for cov2d, tier3-design and minerva-lib in that order, each at
     most 6 h old and at most 5 min ahead, then non-empty ack text.
   - **The overlap fence** (`tools/fence_overlap.py`) is flux4's, at the new root. It also lists the 12 omnifiles,
     because p0 stages them for part 2. On the real config with a clone at S, it reads 70 originals (flux4's 58 plus
     12), with the one allowed exception (the NuE constraint) and `CLEAR`
     ([`tests/fence_overlap_real_config.out.txt`](tests/fence_overlap_real_config.out.txt)).
5. **The retention stat** (default (a)). The connect's step 6 also stats the 12 RDX omnifiles and the true-energy
   sidecar. It never opens them, so no atime moves.
   - Each is compared with the size and inode the sidecar probe recorded on 2026-11-26
     (`../sidecar-probe-20261126/run-20261126/probe.json`).
   - A missing file, or a different size or inode, STOPs before anything is staged.
   - S1's 27 entries are unchanged.
   - `tools/p0_checks.py`'s code is unchanged. Only its wording changes: the docstring, and the verdicts "same as
     recorded" and "DIFFERS from the record".
6. **ibu-chi** (default (b)) is messaged before the connect but is not in the ack file. P0 runs in the numerical
   environment and opens no MAT file and no NuE file.

**Unchanged:**
- `tools/p0_supervise.py`, byte for byte (`6ad0f68f…`);
- the runner, except its root;
- the 7200 s deadline and the 8e9 B RSS cap;
- the fetch, except its root and the inputs record's name;
- the write boundary (the root and `/dev/shm/limres-rpd-flux1`);
- `-B` on every Python call, asserted again;
- the package's script names (`rpd_p0_*.sh`) and the runner's name. The new root is
  `/pscratch/sd/j/josephrb/rpd-reco-p0e1-20261126`.

## C-JOIN part 2 (amendment 1 section 4; in the bound code)

In each of `p0 --dry-run` and `p0`, `omnifile_spot_check` does the following for each playlist:
- it requires `lat_<PL>`'s MCgen to be float32;
- it takes the spot rows from flux4's pinned join record and requires them to be:
  - sorted and distinct;
  - inclusive of the first and last rows;
  - at least min(64, rows);
  - with one (run, subrun, event) and one Eν per row;
- it requires the product's `energy` column at those rows to equal the recorded Eν, bitwise;
- it stages the pinned omnifile with an O_NOATIME copy (`Inputs.copy`, with a sha256 check);
- it reads `mc_signal_reco`'s six branches with uproot, never ROOT;
- for each spot row it requires that:
  - the event occurs exactly once;
  - `truthx_enu / 1000` equals the recorded Eν, bitwise;
  - `float32(MC)` and `float32(MC_pz)` equal MCgen's two columns, bitwise.

A failed check is guard `C_JOIN`. A failure inside the staging or product load raises that function's own guard
instead (`Inputs.copy`'s, `pinned_flux_factors`'s). Either way it is a STOP: the step fails, and the runner STOPs before
the next step. Nothing downstream
reads flux4's factors unless P0 passes.

## The price ([`price/`](price/))

- **0 node-h:** login node only, no job.
- **Part 2's peak RSS, upper bound: 1.232 GB** on macOS, 15% of the 8e9 B cap. `price/part2_probe.py` makes 12 passes
  at 1M's size (5,916,895 rows):
  - all six branches are 8-byte, read through the bound `uproot_tree_reader` (imported from `fd_rpd_reco.py` at S);
  - the MCgen is float32 (rows, 5);
  - the product is five float64 arrays;
  - each pass's arrays are rebound, not deleted, as in `omnifile_spot_check`, so two passes' arrays can coexist (the
    agy read's note; deleting them gave 1.108 GB).

  For calibration, the old P0's macOS estimate was 0.189 GB against 0.143 GB measured on the node.
- **Time, upper bound:**
  - about 30 s for part 2's reads;
  - about 29.5 s per pass to stage the omnifiles, at flux4's measured 250 MB/s;
  - about 2.5 min for the whole chain, dry and run, against the 7200 s deadline.
- **Disk:** the 12 omnifiles total 7,373,436,509 bytes (the probe's sizes; the largest is 1M's, 1.32 GB).
  `p0 --dry-run` runs `p0()` in full (`fd_rpd_reco.py:3437-3439`), and each run directory stages its own copies, so
  `dry/staged` and `run/staged` hold **14.75 GB** of omnifile copies. They sit beside the factor-product and dump copies
  P0 already staged.

## Purge exposure

The step-6 stat prints the earliest purge exposure, the oldest atime plus 56 days, over all 40 files. On 2026-11-26
the probe recorded atimes of 2026-11-17 for the 12 omnifiles and the sidecar, which puts their exposure at 2027-01-12.
P0 does not read `lat_zero.npz`, whose exposure begins 2026-12-25T08:53:42Z.

## After the receipts: removal through the director

When P0's receipts merge, `/pscratch/sd/j/josephrb/rpd-reco-p0e1-20261126` holds:
- the clone;
- `dry/staged` and `run/staged`, which include the 14.75 GB of omnifile copies;
- the step records.

Removing it, the omnifile copies first, is a post-receipt step through the director under flux3's precedent, after
d2-predict + step0 no longer needs P0's records there.

flux4's lane, `/pscratch/sd/j/josephrb/rpd-reco-flux4-20261126`, is on the same list. P0 reads flux4's extract, custody
record and 12 products there in place, so it stays until P0's receipts merge. Its removal also goes through the
director (the director, 2026-11-26, at #1403's merge `d6b0f1e8`).

## Checks on these bytes ([`tests/`](tests/))

| suite | result |
|---|---|
| `test_sacct_fence.sh` (flux4's, cut from `rpd_p0_connect.sh`) | all cases, mutants 18/18 killed |
| `test_launch.sh` (flux4's three-lane guard, against P0's launcher) | all cases, mutants 16/16 killed |
| `test_connect_start.sh` | all cases, mutants 6/6 killed |
| `test_runner.sh` | all cases, mutants 22/22 killed |
| `test_fetch.sh` | all cases, mutants 12/12 killed |
| `test_p0_supervise.py` | 17 passed |
| `test_p0_checks.py` (adds the stat table's 27 + 13 against P0's table and probe.json, and the config's paths) | 7 passed |
| `test_fence_omnifiles.sh` (the omnifiles in the overlap fence; real config 70 CLEAR, two STOP cases) | PASS, mutant killed |

Each `*.out.txt` beside its suite is that run's output. The five shell suites and `test_p0_supervise.py` are
p0-20261123's and flux4's, with the root, the inputs record's name and the script names substituted.
`test_p0_checks.py`'s new tests are in the file.

**Reproducible:** `python3 -I -B tools/gen_p0e1.py <repo>` rewrites the eight outputs byte for byte, and prints their
sha256 and the runner's (below).

## Reads

- agy (gemini-4-hydrogen-high), 2026-11-26: **VERDICT: GO**, five non-blocking notes ([`reads/agy/`](reads/agy/):
  prompt, report, model). Taken:
  - the guard wording for failures inside staging and the product load (above);
  - the probe's docstring line range;
  - the probe now rebinds arrays as the code does: 1.232 GB, up from 1.108 GB.

  Left as they are:
  - the tests read the repository layout, not the read's bundle;
  - the read's diff left one fence root unfolded (presentation only).

## Files and shas

| file | sha256 |
|---|---|
| `production-config.ready.json` | `f92d034df0db5bf487f689b0efc1eb8862396303647fa1172ad5e6eaa3f4c47a` |
| `rpd_p0_connect.sh` | `5016f37822af9c43e52b8fe9379757306c8dd47948115d9dad566d88ab242434` |
| `rpd_p0_fetch.sh` | `d52f3576192b25672f892808c0f740accfb392813ef525e4ffad5ea3da03b35b` |
| `rpd_p0_launch.sh` | `4ffd4a596e5339476cd129306dc7d34c0a51ea5b68718568520c3d4421588efd` |
| `tools/p0_checks.py` | `bcdc1b99aa4aff1e645e8000b7630d38d3bcafda74f70b43869195dc64071008` |
| `tools/p0_expected.json` | `c9d5e9567eba82818616c2b25c0162f113026e5feec8d2971dbe8f18d5f3dee9` |
| `tools/p0_supervise.py` | `6ad0f68fb309a7b83adc0f65ed709e5e2412e650e115075fe41ebbc7a070134f` |
| `tools/fence_overlap.py` | `940fb7598c782c77c2b3dd0e677f80568f0fdb31fd033e8e8988404049f38810` |
| the runner, as the connect's heredoc writes it | `f145f41f32741119ae016b815e5a2b00f9da9ad55cb8bc053e7e7d52ade8902f` |
