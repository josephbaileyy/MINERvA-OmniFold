# CENTER2D: the code (tier3-design, 2026-11-28)

**Authority:** [`CENTER2D-DECLARATION.md`](CENTER2D-DECLARATION.md), merged in #1446 at main `f5c6db0e`, and the
director's rulings on the PR (issuecomment-7235721166).

**Status:** code only. Nothing has run on any input except the tests below. Before part R or any connect, three things
come first: mutation testing, the director's binding, and the director's GO on the fetch package.

**CANNOT AUTHORIZE:** what the declaration excludes. That is any covariance or convention change, any note, paper or
Overleaf text, a coverage statement, a cause, and any separation of physical asymmetry from training noise.

## Files

| file | sha256 | what |
|---|---|---|
| `center2d.py` | `554ee0bcd3d5335685927b9f5b9c99351d4651d08d4a6a8f9d408b032718b27d` | the driver; modes `expected`, `rehearsal` (part R), `main` (parts T and D) |
| `center2d_fetch.sh` | `b89dd3a02592bec9604c823e0bb6d63329366e2b41ae8f388234b3526b79d98a` | the launch wrapper: local gates, cert, fence, one ssh, verifier |
| `center2d_fetch_remote.py` | `dd1215a1bdef87c046bb538eaadd61811734660bf62d3961c019faad1cbe79e6` | the remote reader, piped on stdin; the 16 paths are fixed in it |
| `center2d_fetch_verify.py` | `e3385e8e8b869f672be9aeccc4a4cae27c355826fa82ee319e0681a18cd048b9` | the laptop verifier |
| `center2d_fence.py` | `ee696ee63877cd2ee52719d42fa63fcfa79dee8d1b6f5c3d9c8cd7fa588db9d6` | the fence decision on the sacct and squeue rows |
| `test_center2d.py` | `883781aed703679f4bde30fd66b53ced5fa2788fc256f80dc99d6db3da39cff1` | 40 tests, OK (`receipts/test_center2d.txt`) |
| `mutants_center2d.py` | `e0d97ef08e6caf7ff5b3551981e90ed6fa17af34639a6be30f6d28d86b53db27` | the mutation runner (62 mutants; its receipt follows in `receipts/mutation.txt`) |
| `test_center2d_fetch.py` | `8ff1e88459ff17cf0e954dab196198c671d45d3087722d59f4c0a761bf4895cb` | 32 tests, OK (`receipts/test_center2d_fetch.txt`) |

**The wrapper pins:**
- remote `dd1215a1…`, verify `e3385e8e…`, fence `ee696ee6…` and driver `554ee0bc…`;
- the sha256 of `center2d.py expected`'s output, `5e50af9b841c0c115bb4b152bc5c6b9b64158c3d7ef37c33d1a67a11bb826fe6`.
  That output lists the 16 fetched files' digests, each taken from a committed record: G2R's `data_g2r.json` and
  `score_g2r_<T>.json`, partc-r2's `SHA256SUMS`, part B's sums, and S5_R's `s5.json`.

Every pin was computed by command.

## How the director's code-PR requirements are met

1. **If ndf < 140, the third rank band is printed empty, and the labels are applied over the non-empty bands only.**
   `rank_slices` returns `None` for an empty band, `readings` prints its mean as `null` with the band `[140, null]`,
   and `label` skips `None`. Tests: `Rules.test_rank_slices` (ndf 205, 140, 139, 120 and 50),
   `Rules.test_empty_rank_bands_are_ignored`, and `Readings.test_singular_c_drops_the_null_ranks` (a rank-120 C).
2. **Part R exercises every control, and a test makes C-RECON fail on purpose.**
   - **What part R runs, per tune:** C-PIN, C-FINITE, C-X0 (the 205-cell mask), C-FLUX, C-ID, C-RECON (C_univ, C_lat and
     C_T as the sum of its blocks), C-PSD (C and M) and C-ADD.
   - **C-FETCH has no fetch to act on in part R.** It is exercised before any connect by `test_center2d_fetch.py`
     (the reader on a fake tree, the verifier against tampering, missing manifests, moved atimes and wrong committed
     digests) and by the wrapper's `--check-only` run (a real local gate pass, no connect).
   - **`CommittedControls`** runs the controls alone, never a reading, on the committed pre-G2R blocks.

   On the committed pre-G2R blocks, from `receipts/test_center2d.txt`:

   | tune | C-RECON C_univ | C-RECON C_lat | C-RECON C_T | C-ID worst | C-FLUX |
   |---|---|---|---|---|---|
   | AR23 | 6.5e-21 | 0 | 0 | 1.2e-13 | sum 211.01200325082078 and n_eff 19.060534772246488, exactly the logged values |
   | G18 | 5.6e-21 | 0 | 0 | 2.2e-13 | the same |

   A 1e-9 relative change to one MaRES universe entry makes `C-RECON:R:G18:C_univ` fail. A 1e-9 change to one
   `minos_x` entry makes `C-RECON:R:AR23:C_lat` fail. The synthetic data part fails C-RECON on a 1e-9 change to the
   X01 scale and on a 1e-9 change to C_new, and fails C-X0 on a 1e-15 change to x.

   **C-ID's margin is the narrowest.** Its residual is ordinary rounding in V_nom − V_mean − b bᵀ, at about 1e-13
   across many bands, so it sits a factor 4.5–8 under the declared 1e-12. If the data's residual exceeds 1e-12, the
   control STOPs as declared, and the change comes back to the director.
3. **The fetch package goes to the director with its shas before any connect.** The shas are the table above.

## ERRATA

- **§6 C-FLUX of the declaration:** the "`data_g2r.json`'s logged" sum and n_eff are in
  `fd/receipts-cov2d/g2r/readout/data/connect.log.txt:14`
  (`957750e57a6bc43ac62b629d6d140cd0b9479c2db93744937b29a1555a3e21c3`):
  `[PASS] weights_equal_vl175_build_json {'sum': 211.01200325082078, 'n_eff': 19.060534772246488}`. The values and
  the exact-equality rule are unchanged, and the code pins that line. The merged declaration is not edited (director,
  2026-11-28).

## The fetch is all or nothing

The declaration's §6 C-FETCH says that if a part-D file is missing or differs, part D STOPs and the tunes continue.
The reader is stricter.
- Any missing, changed, symlinked, foreign-owned or empty file among the 16 makes it exit 9 before `MANIFEST.tsv` is
  written, so the whole fetch refuses.
- A refused fetch comes to the director. A tunes-only fetch would need a separate GO with its own file list.
- The driver keeps the per-part C-FETCH split for a fetch that verified but holds a file with a wrong digest. That case
  cannot pass the verifier, so the split is a second line of defence.

## The fence

- **Families:** ruling 5's (cov2d*, t2a*, rpd*, precharge_c, geanttw_, oofvc_, covfix_, ibuchi_, ptmc_), plus `rdx_`
  from cov2d's condition-B list and this lane's `center2d`. Job names are matched by case-insensitive prefix.
- **sacct:** `sacct -X -n -P -u josephrb -S now-14days -o JobID,JobName,State`, without `-s`. With `-s`, sacct
  selects jobs that held a state at any time in the window, so it would refuse on jobs that have since ended (the
  director's review of `ca091751`). `center2d_fence.py` refuses on a fenced-family row whose State is not terminal.
  The terminal states are COMPLETED, FAILED, CANCELLED*, TIMEOUT, OUT_OF_MEMORY, NODE_FAIL, PREEMPTED, BOOT_FAIL,
  DEADLINE and REVOKED. An unknown state refuses, and so does a malformed row.
- **squeue:** `squeue -h -u josephrb -o "%i|%j|%T"`. It lists only live jobs, so any fenced-family row refuses.
- **Unreadable fence files** make the helper exit non-zero with no count, and the wrapper refuses.

## How it reads and writes

- **Committed inputs** are read with `git cat-file blob origin/main:<path>`, and each is checked against its sha256
  before parsing.
- **E_R** is the local verified copy (`a5c13fc3…`), checked by sha256.
- **`hXSec2D`** is read with uproot, with the (pT 14, p∥ 16) edge check that C2-EFF uses.
- **`build_repair.wcov`** is reimplemented in numpy, because `build_repair` imports ROOT. C-RECON shows the
  reimplementation reproduces the committed blocks to the rounding level.
- **`cov2d.py`** (numpy only) is imported unchanged at its pinned sha, for the band lists.
- **The records** are written with exclusive creation (`open(..., "x")`) and `allow_nan=False`. The driver prints
  statuses only.
