# REF-G1 ADDENDUM A1: G-IBU1's thread environment, read discipline, the bars and the calendar (2026-11-05)

**Amends** [`REF-G1-DECLARATION.md`](REF-G1-DECLARATION.md), bound at step one by
[`REF-G1-BINDING-1.md`](REF-G1-BINDING-1.md) and at step two by [`REF-G1-BINDING-2.md`](REF-G1-BINDING-2.md)
(M = `609d8f24`). **For** the audit (coverage-5b-audit) and the director's binding. Nothing re-runs before both.
Written by limitations-catalog at the director's request, under the director's rulings of 2026-11-05 (items 1-4
below are the director's A1 items, in order). Every path:line is at M unless another sha is named; the REF-G1 files,
`ibu1.py`, `s1_assemble.py`, `s5p_universe.py`, `flux_universe.py` and `s5c_unfold.py` have the same blobs at
origin/main `72e27f76`.

**CITABLE FOR:** what the read STOP and the atime check found, what changes in the code and the run, and the order of
the connects. **NOT CITABLE FOR:** any reading. None exists: the read stopped before Δ was formed (#792).

## 0. What happened

- **The read STOPped on G-IBU1** (`fd/receipts-ref-g1/read/README.txt`, #792): `ks` equal, `F_fold` and `F_sub` not
  equal between the batch's `gibu1.npz` (`70bb60d0…`) and IBU-1's `D_N.npz` (`a160dbea…`).
- **The diagnosis** (`fd/receipts-ref-g1/diag-gibu1/README.txt`, `diag.json` `4e34f809…`, #795): 35 of 1071 `F_fold`
  and 36 of 1071 `F_sub` elements differ, by at most 2 ulps (max|a−b|/max|b| 6.5e-19 and 1.3e-18). IBU-1's `D_N` ran
  at OMP/OPENBLAS/MKL = 1 on 2 CPUs; `gibu1` ran at 32 threads. numpy 1.26.4 on both sides.
- **The atime check** (`fd/receipts-ref-g1/atime/README.txt`, #795): REF-G1's own plain reads moved the atimes of 669
  bank and 32 detector-dump files (the universe units), of `of_inputs_5d.npz`, `bkg_dump.npz` and the three ratio
  files (the batch), and of every (e) product and `D_N.npz` (the read's controls, 15:18:14-16Z). The declaration
  required the opposite: "Reads use O_NOATIME. Files are never touched to reset exposure."
  (`REF-G1-DECLARATION.md:254`).

## 1. G-IBU1 keeps its bitwise rule; gibu1 re-runs in IBU-1's thread environment

**The rule stands.** G-IBU1 is array equality of every array (`REF-G1-DECLARATION.md:97-98`). A bound control is not
relaxed after it fails.

**IBU-1's recorded environment for `D_N`:**
- `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1`: `nd-unfolding/ibu1/sbatch_ibu1.sh:25` at its deploy
  `7ea30e3d`.
- One `srun` step per task with `-c "$CPT"` (`sbatch_ibu1.sh:37`); `CPT` was 2 (`ibu1/BINDING-C.md:32`, "2 CPUs /
  11G per step"), and Slurm recorded it: step `60130813.0`, `D_N`, `cpu=2`
  (`docs/orchestration/state/2d-closeout/stageF/methods/ibu1/receipts/sacct.txt:5`).
- The interpreter and Python version are already pinned (`config.json` `gibu1_environment`, from
  `ibu1/receipts/inventory/D_N.jsonl:1`).

**The change.**
- `config.json` `gibu1_environment` gains `thread_env` {OMP_NUM_THREADS: "1", OPENBLAS_NUM_THREADS: "1",
  MKL_NUM_THREADS: "1"} and `cpus` 2, each with its source above.
- `gibu1_environment()` (`ref_g1.py:277-284`) also requires those three variables exactly and a CPU affinity of exactly
  2 (`os.sched_getaffinity`), **for the gibu1 unit only**. It fails closed as before (rc 4), and the unit records what
  it saw. A test fires on each (a wrong thread value, a wrong CPU count) and is silent on the match; each guard has a
  REQUIRED mutant.
- The unit's environment record also carries `threadpoolctl.threadpool_info()` where it can be imported (the pools
  actually loaded, not only the variables asked for) and `root_loaded`. The gibu1 unit runs with no ROOT library
  loaded: the TFile guard is installed only for a unit set with a Flux universe, and otherwise the run fails if
  anything imports ROOT (§2.3). So a G-IBU1 STOP cannot come from a ROOT load (coverage-5b-audit's L2 and L3 on
  #806).
- The gibu1 unit re-runs with `srun -c 2` or `taskset` on two cores, at those three values, into a **new** directory.
  The batch's directory and its `SHA256SUMS` `6a4c1929…` are not touched.
- **The other 232 units stay as they ran.** Their products are bound by `SHA256SUMS` `6a4c1929…`. They do not re-run.
- **The re-run's product is given to the read, not put in `config.json`** (the director's ruling on coverage-5b-audit's
  B1 on #806, option (a)). `ref_g1_read.py read` takes `--gibu1-product PATH --gibu1-sha256 SHA`; the sha comes from
  the re-run's done-marker, recorded in connect 1's receipt and committed with `bars.json`. G-IBU1 checks the
  product against it on its staged copy, and no longer reads `<run>/gibu1.npz`. The read refuses without both
  arguments, and the readout and `STOP.json` record them. `config.json` stays exactly as the bars recorded it: the
  bars pin `config_sha256`, and a pin merged into `config.json` between the bars and the read would make the read
  refuse (a test runs bars, then the pin's merge, then the read, and checks that the changed-config form refuses).

**If gibu1 is still not bitwise at IBU-1's threads**, that is a STOP to the director. A tolerance would be a separate
decision with its post hoc label.

## 2. Read discipline

### 2.1 The defects (every plain read of a declared input on REF-G1's run path, at M)

| # | where | what it reads | how |
|---|---|---|---|
| D1 | `Run.bank_cv`, `ref_g1.py:202-206` | the bank's `cv.npz` (2.16 GB) | `np.load` |
| D2 | `Run.universe`, `ref_g1.py:236-238` → `s5p_universe.weights`, `s5p_universe.py:89-100` (`:94`) | the bank and detector-dump weight files | `np.load(mmap_mode="r")`, then `sha256` |
| D3 | `ref_g1_read.py:477-478` → `s1_assemble.flux_weights`, `s1_assemble.py:133-144` | the flux constraint file | `require_sha` (`:76-77`), then `read_text` (`:137`) |
| D4 | `ibu1.sha256` (`ibu1.py:53-58`, used as `G.sha256`) and `s1_assemble.sha256` (`:68-73`) | every pinned input they hash | `open(path, "rb")` |
| D5 | `main` → `ibu1.load_inputs`, `ibu1.py:544-551` → `s5c_unfold.load_inputs`, `s5c_unfold.py:98` | `of_inputs_5d.npz`, `bkg_dump.npz` | `sha256`, then `np.load` |
| D6 | `load_ratio`, `ref_g1.py:163-170` | the four L-5D-PV ratio JSONs | `sha256`, then `read_text` |
| D7 | `Run.universe`, `ref_g1.py:240-243` → `flux_universe.read_flux_universe_table`, `flux_universe.py:133` | the flux-universe ROOT file | `sha256`, then `ROOT.TFile.Open` |
| D8 | the reader's controls and bars: `e_cells` (`ref_g1_read.py:68-70`), `reading_r2` (`:378`), `g_ibu1` (`:399-404`), `g_cells` (`:411-415`), `g_pair` (`:433`, and `check_meta`/`check_universe`, `s1_assemble.py:194-197, 219`), `Paired.digest` (`:115-125`) | every (e) product, `D_N.npz`, `s1_assembly.npz` | `sha256`, then `np.load` |

D1-D4 are the four the director named first; D5-D8 complete the set the closure grep (§2.4) finds.

### 2.2 The fix

**One rule.** Every file outside the repository and outside REF-G1's own output directories is read once, through
O_NOATIME, into a copy whose sha256 is taken in the same pass and compared with its pin. All later reads, hashes and
`np.load`/`ROOT` opens use the copy. REF-G1's own products (the run directory, the re-run's directory) are its own and
are read in place, as the director ruled for #787's reader.

- **`open_noatime`** refuses where the platform has no O_NOATIME, and raises an EPERM rather than retrying a plain read.
  Tests substitute the flag explicitly. A REQUIRED mutant restores a `getattr(os, "O_NOATIME", 0)` fallback.
- **`copy_noatime(src, dest)`** writes with `"xb"` (never over an existing file) and returns the same-pass digest. The
  copy's own digest must equal it.
- **The units** stage into a fresh `$TMPDIR/ref-g1-stage-*/in/`, removed at exit:
  - `of_inputs_5d.npz` and `bkg_dump.npz` (about 1.5 GB) before `ibu1.load_inputs`, which then hashes and loads the
    copies, unchanged;
  - `cv.npz` once per process (M checked no pin for it and A1 adds none; `check_alignment` checks its content, as
    before);
  - a universe's weight files into `stage/<tag>/`, then `s5p_universe.weights(stage/<tag>, tag)` unchanged, the
    digests recorded from the copy pass (the same `weight_sha256` meta G-pair compares). The tag's directory is deleted
    after the unit. `weight_keys` stays on the original directory: `Path.exists` is a stat and moves no atime;
  - the flux-universe file, then `universe_inputs` on the copy;
  - the ratio JSONs, then `load_ratio` on the copy.
- **The reader** stages into `<read dir>/inputs-bars/` or `<read dir>/inputs-read/`, which must not exist (a re-run reads into a new directory): every
  (e) product it opens, `D_N.npz`, `s1_assembly.npz`, the flux constraint, and the re-run's `gibu1.npz`. Then
  `e_cells`, `reading_r2`, `g_ibu1`, `g_cells`, `g_pair`, `check_meta`, `check_universe` and `flux_weights` run
  unchanged on the copies. `Paired.digest` takes the (e) files' digests from the copy pass, so `products_digest`
  covers the same bytes in the same order. A test pins that equality on a fixture.
- **Shared modules stay unchanged.** `ibu1.py`, `s1_assemble.py`, `s5p_universe.py`, `flux_universe.py` and
  `s5c_unfold.py` are pinned by `config.json` `code_sha256` and used by other bound work. They are handed copies, not
  edited.
- **ROOT** (D7) cannot take O_NOATIME. It opens only the staged copy, under the TFile guard below.

**The cost.** The gibu1 re-run stages about 1.5 GB once. The reader stages about 25 MB. No universe unit re-runs.

### 2.3 The runtime guard

`read_guards(protected, allowed, root)` is active for each unit's whole run and for the reader's `bars` and `read`.
- **An audit hook on Python opens** (`sys.addaudithook`, event `open`, whose arguments carry the open's flags). Any open
  for reading of a path under `/pscratch` or `/global/cfs` that is outside the allowed roots and lacks O_NOATIME raises
  `GateFailure`. The allowed roots are the checkout, the run's output directory, the stage directory and the read
  directory. `np.load`, `open`, `Path.read_text`, `read_bytes`, `mmap` (through its `open`) and `sha256` all pass
  through it.
- **A TFile guard, only where ROOT is needed.** With `root` (a unit set with a Flux universe), `ROOT.TFile.Open` in any
  mode is refused outside the allowed roots (REF-G1 writes no ROOT file,
  and `UPDATE` or `READ_WITHOUT_GLOBALREGISTRATION` also read; coverage-5b-audit's note on #787). The audit hook does
  not see C-level opens. Where ROOT cannot be imported no TFile open can happen, and nothing is patched. Without
  `root` (the gibu1 unit and the reader), ROOT is not imported for the guard, and the block fails if anything imports
  it, since a ROOT open would then have been unguarded.
- **The residual, named.** A C extension or ctypes call that opens a file below both layers is not seen. A grep of the
  23 closure files for `ctypes`, `cffi`, `uproot`, `os.open(`, `io.open`, `codecs.open`, `gzip.open`, `h5py` and
  `tables.open` finds one hit, A1's own `os.open` with O_NOATIME (`open_noatime`). numpy opens files through Python's
  `open`, which the hook sees; ROOT opens them through `TFile::Open`, which the TFile guard covers.
- **Tests:**
  - the hook fires on a plain `np.load`, `open`, `read_bytes` and `sha256` of a protected path;
  - it is silent on an O_NOATIME read, a write, an allowed root and an unprotected path, and inert outside the block;
  - the TFile guard fires outside the roots and is silent inside;
  - the reader fixture's bars and read, and the universe, vertex and unit-input tests, run under the guards with
    their inputs as the protected set; the staged set must equal the code's enumeration.
- **REQUIRED mutants:** the hook disabled; the TFile guard admitting opens outside its roots; the O_NOATIME fallback
  restored; a staging directory reused; and one per staged read, each reverting it to its original path (D1 `cv.npz`,
  D2 the weights, D3 the constraint, D5 the units' inputs, D6 a ratio, D8 the (e) central and `D_N.npz`). The guard
  fires on each, so the integration tests kill them. D4 is the hashing those reads did; it moves with them. D7 (the
  flux-universe file) has no local test: it needs ROOT and a Flux bank fixture, and no Flux universe re-runs under A1.
  <!-- absence-ok: scopes this receipt's own test coverage of D7 (harness.txt lists every mutant), not a claim that a result does not exist -->

### 2.4 The closure grep

The grep covers REF-G1's import closure for `open(`, `np.load`, `read_text`, `read_bytes`, `mmap`, `TFile` and
`uproot.open`.
- **The closure, from the code** (`closure-files.txt`): 28 files, every repository module reached by an `import`
  anywhere in `ref_g1.py`, `ref_g1_read.py` and `did.py` (which `ibu1.py:80-81` loads by path), transitively,
  stdlib names excluded. That includes five modules imported only inside functions REF-G1 does not call
  (`unfold_2d_omnifold_unbinned`, `unfold_nd_omnifold_unbinned`, `seed_offset_policy`, `s5e_geometry`,
  `s5p_converge`; coverage-5b-audit's L1 on #806). Two names are outside it: `did.py`'s path-loaded GBDT
  `comparator.py` (`load_comparator`, not reached) and `omnifold`, ambiguous between two checkouts and imported only
  inside the two `unfold_*` mains.
- **At M, 99 hits.** 15 read a declared input (D1-D8 above); 10 read the repository or REF-G1's own outputs; 74 sit
  in functions REF-G1's run path does not call.
- **At A1's revision, 108 hits.** Every hit, with its function and disposition, is in
  `fd/receipts-ref-g1/addendum-a1/closure-reads.tsv`:
  - 14 are declared reads, now each through a staged copy;
  - 2 are plain digest helpers (`ibu1.sha256`, `s1_assemble.sha256`), reached only on staged copies, repository files
    and REF-G1's own outputs;
  - 18 are the read-discipline code itself, read the repository or REF-G1's outputs, write, or are docstrings;
  - 74 are not called from REF-G1's run path.
- **The "not called" class is checked at run time** (`closure-trace.txt`). The suite runs under `sys.monitoring` LINE
  events, and a hit counts as reached only when a REF-G1 production frame (`ref_g1.py`, `ref_g1_read.py`) is on the
  stack. Result: 0 of the 74 reached from the run path. One runs from the test file's own fixture only
  (`pvl_lib.sha256_path`, hashing a ratio the fixture writes). The check has power: relabelling two run-path hits
  (`ibu1.py:55`, `s5p_universe.py:94`) as "not reached" makes it fail on both (`closure-trace-control.txt`).
- **The trace's limit:** it sees only what the suite's fixtures exercise. A function the fixtures never call is
  "not-run" in the trace whatever its class, so the "not called" claim for those rests on the call graph by name.

## 3. The bars are re-made; the read re-runs in a new directory

- `bars.json` (`de12c674…`, on main) is valid only while its recorded `products_digest`, `reader_sha256` and
  `config_sha256` match (`ref_g1_read.py:275-284`). A1 changes the reader and the config, so **the bars are re-made
  by the new reader** (connect 1), merged with the gibu1 pin, and only then read (connect 2). `config.json` does not
  change between them (§1). The old bars are not hand-carried.
- The products are the same batch, so the new `products_digest` should equal the old one. A difference is reported,
  not repaired.
- The read writes into a new directory, so its `inputs/` is new and the old `STOP.json` stays as it was.

## 4. The calendar

- **The deadline** is the earliest exposure (atime + 56 days) among the files REF-G1 still reads: the gibu1 re-run's
  inputs and the reader's staged set. It is re-measured by `stat` at A1's first connect.
- **The read set comes from the code.** A new `ref_g1_read.py reads` prints every non-repository path the gibu1 unit
  and the reader stage (`unit_reads` and `reader_reads`, which call the rules the staging calls). Tests require the
  staged set to equal the enumeration, for a unit and for a whole read. The connect stats exactly those paths.
- **Earlier values, for reference only:**
  - #795 (`atime/atime_groups.txt`): the (e) products and `D_N.npz` are now exposed from 2026-12-31T15:18Z;
    `of_inputs_5d.npz` and `bkg_dump.npz` from 2026-12-31T14:42Z.
  - #779's `ref_g1_followup` group (`fd/receipts-ref-c2c1/preconditions/check.log:53`): `tune_v1.json`,
    `s1_assembly.npz`, the flux-universe file and the constraint, 4 of 4 present and equal to pin, oldest atime
    2026-10-24T18:15:37Z, exposed from 2026-12-19T18:15:37Z. REF-G1's reads have since moved some of them (the
    constraint at 15:01Z, by the bars connect).
- **`D_N.npz` still goes to HPSS after 2026-11-06 17:00**, per the director.

## 5. The order

1. The audit of A1 and its code (coverage-5b-audit), then the director's binding at the merged sha M'.
2. Connect 1, by limitation-resolver, priced to the director first:
   - a fresh clean clone at M', run with `-B`, porcelain `--ignored` reported before and after;
   - the `stat` of `ref_g1_read.py reads`' set;
   - the gibu1 re-run at 1/1/1 threads on 2 CPUs into a new directory;
   - the bars, by the new reader, into a new read directory.
3. The merge of the new `bars.json` and connect 1's receipt, which records the gibu1 product's path and sha256 from
   its done-marker. `config.json` is not changed.
4. Connect 2: the read, in that read directory, with `--gibu1-product` and `--gibu1-sha256` from that receipt.

A STOP of any control comes to the director unrepaired (`REF-G1-BINDING-2.md` ruling 6).

## 6. Unchanged

The estimator, the readings and their bars' construction, the controls' definitions, the 232 batch products, the
compute cap, and the declaration's text. A1 governs where it differs.
