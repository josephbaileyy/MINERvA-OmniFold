# COV2D control 9.5: the block code reproduces part B's S5_R blocks. **CONTROL-95 PASS** (run 2, 2026-11-04)

**By** the `cov2d` session. Section 9.5 of `COV2D-DECLARATION.md`, with the director's R2 of 2026-11-04: "a login
connect in root_6_28 before the pilot, sha first, threads capped".
- **MEASURES:** whether the amendment's block code reproduces part B's products, on part B's own products. The code is
  `2d-unfolding/cov2d/cov2d_blocks.py`, not yet bound, which imports re2c_rollup's functions.
- **CANNOT AUTHORIZE:** binding 2, the pilot, or any toy.
- **Why it ran before binding 2:** to validate the blocks on real products. The (2a) failure showed what synthetic tests
  cannot see.

## Run 2: PASS

- **Connect:** `connect-95-run2.sh`, sha256 `c1872353e6ff0a606fb4513b9e8390f3a50d46139692b78d34217b1eb44c4e95`, approved.
  - On login02 its digest was compared before launch (DIGEST_MATCH) and launched in a separate step.
  - It ran 2026-11-04T17:48:14Z to 17:48:58Z, 0 node-h, no job. control95 itself took 5.5 s.
- **Code:** M = `0bb6bca8f9944f28ec494231dc53fb282f741ab2`, on branch `code/cov2d-amendment-20261104`.
- **Blobs, 9 of 9, before and after** (`run2_blobs.{before,after}.txt`):
  - the five bound ones: re2_driver `97f26a1d`, cov2d `7dafdd3f`, cov2d_receipt `d5718bf4`, writer `bb3892e5` (A1),
    fd_1b_null `1810161d`;
  - re2c_rollup `e41940cb` and build_cmodel `7a987e25`, byte-identical to part C's deploy `903fb78b`;
  - cov2d_blocks `7c656f4a`;
  - fd_rpd_inputs `7c2e018f`, the same as at `8727c63e`.
- **Environment:**
  - the shared checkout's `setup_salloc_env.sh` was sourced, as part C's rollup step was (`re2c_run.sh:33`;
    `re2c_rollup.py:48`). TMPDIR and the thread caps were re-exported after it;
  - nice 19, `taskset -c 8-11`, a fresh /dev/shm clone, porcelain 0 before and after;
  - Python 3.11.14, numpy 1.26.4, ROOT 6.28/12.

**Section 9.5** (`run2_control95.json`, sha256 `a7ace72e…`):
- all 44 `band_<b>` keys of part B's `s5/production_cov.npz` (sha256 `631cf255…`, RE2-PARTC-REPORT.md:131) compared,
  none missing; the worst band differs by 4.59e-16 relative;
- universe 4.97e-17, stat 0.0 (exactly equal), against the tolerance of 1e-12;
- E_R's x equals `cells_x_EU`;
- E_R's 205 reported cells equal `cmodel_2d.json`'s 205 cells, in flat order;
- 486 part B products read: 175 universes, 10 laterals (with X01), 300 replicas and E_R. Each was checked against part
  B's committed sums;
- none of the rollup's own `check()`s failed.

**The pinned MAT environment** (the director's ruling: one standard with RPD's binding 2 A1):
- **Before sourcing:** `fd_rpd_inputs.run_check_mat_setup` (omnifold_py310, no ROOT) passed the six setup-script
  digests.
- **In the control's process:** `fd_rpd_inputs.mat_environment`, imported unchanged, ran before the rollup was imported
  and raised nothing. Its record:
  - 6 setup scripts and 3 MAT files at RPD's pinned digests;
  - `libMATDict.so` resolves to `libMAT.so`;
  - the files mapped from MINERvA101/opt are exactly
    `{/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/lib/libMAT.so}`;
  - `PlotUtils::MnvH1D` has a dictionary.
- **The MnvH1D preflight:** an O_NOATIME copy of `runEventLoopMC_1A.root` (sha256 `d54d2a2c…`) holds
  `pTmu_reweightedflux_integrated` as a `PlotUtils::MnvH1D` with 14 bins.

**The open audit** (the director's request, 2026-11-04):
- builtins.open, io.open, os.open and ROOT.TFile.Open were wrapped before the rollup import;
- **1,603 opens logged, refused list empty;**
- the bypass scan of re2c_rollup, build_repair, build_cmodel, pv2d_lib and report_tables found no subprocess, os.system
  or os.popen, no TFile constructor and no copied upper-case constant. A plain grep agrees (`bypass_scan_local.txt`);
- every imported module (cov2d, cov2d_blocks, re2c_rollup, build_repair, build_cmodel, fd_rpd_inputs) resolved inside
  the clone;
- **atime:** checked on 516 inputs, 0 moved;
- **the audit's measured limit:** a `ROOT.TFile(path)` constructor call skips `TFile.Open`, which a local test showed.
  Opens inside ROOT's C++ are not visible to Python wrappers. The zero-hit scan covers the first limit.
- **A gap in the record:** it stores the first 20 distinct guarded paths, all O_NOATIME reads since none was refused,
  not the total guarded-open count the director asked for. That count is not estimated here. The code will record it
  for later runs.

**Removals** (`run2_removal.log.txt`):
- the clone (1.2G), by the script;
- `/dev/shm/josephrb-cov2d-95` (996K) and the script (`c1872353…`, checked first), rc 0, after the logs were fetched
  and their sha256 matched (`run2_node_listing.txt`);
- `ps` and /dev/shm then hold nothing of the run. A count of 2 from `grep -c` was the check matching itself; a
  `[c]ov2d-95` count gives 0.

**The launch:** the first attempt to launch this connect never started. The ssh master died during a NERSC sshproxy
certificate renewal, and both calls exited 255. A listing of login02's /dev/shm and processes showed no file and no
process before the launch above.

## Run 1: INVALID (a crash, not a STOP; the director accepted it)

- **Connect:** `connect-95-run1.sh`, sha256 `a407fecf…`, M = `6efd7a18`, approved. It ran 2026-11-04T05:07:01Z to
  05:07:34Z on login02.
- **What failed:** control95 crashed in `re2c_rollup.flux_weights` at `f.Get(BR.FLUX_HIST)` with `TypeError: 'PlotUtils'
  is not a known C++ class`. The per-playlist flux files hold `PlotUtils::MnvH1D`, and root_6_28 activated by prefix has
  no MAT dictionaries. No comparison ran and no record was written (`run1_control95.log.txt`).
- **The cause is my preparation.** My memory from RPD stage S (2026-11-03) names this exact failure, and I did not
  consult it.
- **The fix is run 2:** part C's route, then the MAT pinning the director required, the MnvH1D preflight and the
  module-path STOP.
- **Removals** (`run1_removal.log.txt`): the clone, the directory and the script, all rc 0.
- **The STOP count stays at one.**

## Files

| file | what |
|---|---|
| `connect-95-run1.sh`, `connect-95-run2.sh` | the two connects as run |
| `run1_*.txt` | run 1's logs, blobs and removal |
| `run2_control95.json` | run 2's full record: section 9.5, mat_environment, open_audit, modules, inputs |
| `run2_connect-95.log.txt`, `run2_control95.log.txt`, `run2_blobs.*.txt` | run 2's logs and blobs |
| `run2_node_listing.txt`, `run2_removal.log.txt` | the node's digests; the removal |
| `bypass_scan_local.txt` | the local AST scan and the plain grep of the five modules |
