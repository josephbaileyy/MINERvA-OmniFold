# CENTER2D: the code (tier3-design, 2026-11-28)

**Authority:** [`CENTER2D-DECLARATION.md`](CENTER2D-DECLARATION.md), merged in #1446 at main `f5c6db0e`, and the
director's rulings on the PR (issuecomment-7235721166).

**Status:** bound (CENTER2D-BINDING-1). Part R has run on the committed pre-G2R blocks, and the director accepted it
(below). The read and parts T and D wait for the director's GO, cov2d's ack, the cert check and LR START.

**CANNOT AUTHORIZE:** what the declaration excludes. That is any covariance or convention change, any note, paper or
Overleaf text, a coverage statement, a cause, and any separation of physical asymmetry from training noise.

## Files

| file | sha256 | what |
|---|---|---|
| `center2d.py` | `1dc764e7bea23dfa53cad37a733729d672f2543d120f82af033ce09cf351c8e1` | the driver; modes `expected`, `rehearsal` (part R), `main` (parts T and D) |
| `center2d_fetch.sh` | `e4ab0552f97eb2d8df04d12ed514596f5b3d71bd2c2a81038cd9f9e92722d502` | the launch wrapper: local gates, cert, fence, one ssh, verifier |
| `center2d_fetch_remote.py` | `dd1215a1bdef87c046bb538eaadd61811734660bf62d3961c019faad1cbe79e6` | the remote reader, piped on stdin; the 16 paths are fixed in it |
| `center2d_fetch_verify.py` | `e3385e8e8b869f672be9aeccc4a4cae27c355826fa82ee319e0681a18cd048b9` | the laptop verifier |
| `center2d_fence.py` | `ee696ee63877cd2ee52719d42fa63fcfa79dee8d1b6f5c3d9c8cd7fa588db9d6` | the fence decision on the sacct and squeue rows |
| `test_center2d.py` | `bbd14fe1cf447e8ebb7df0d7429e958f3b56a7fe185dbedb3d2849fa5eea817b` | 50 tests, OK (`receipts/test_center2d.txt`) |
| `mutants_center2d.py` | `10edbb2a1067caae3d27a9934bbb23486bbe05309db9db92b419b14511d0945e` | the mutation runner (71 mutants; receipt `receipts/mutation.txt`) |
| `test_center2d_fetch.py` | `8ff1e88459ff17cf0e954dab196198c671d45d3087722d59f4c0a761bf4895cb` | 32 tests, OK (`receipts/test_center2d_fetch.txt`) |

**The wrapper pins:**
- remote `dd1215a1…`, verify `e3385e8e…`, fence `ee696ee6…` and driver `1dc764e7…`;
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

- **The interpretation of §6 C-ID** (accepted by the director, 2026-11-28): "max |V_nom|" is read as each band's own
  max |V_nom|. A null band, one below 1e-12 of the largest band's max |V_nom|, is scored at that global max. This is
  the rule §6 already gives for C-RECON's null bands ("null bands at the total's scale, as S5's control does").
  - NormDISCC is the only null band.
  - At its own scale its rounding residual is 5.5e-4 at AR23 and 1.1e-3 at G18, so a strict own-scale C-ID would
    STOP every run.
  - The worst-case leak into M is about 1e-12 of the largest band.

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

## The independent read (Grok, 2026-11-28)

**The read:** the director asked for it, and codex-school2 was out of quota. Grok `grok-4.7` ran at reasoning effort
high with `--sandbox read-only`, on a read-only `git archive` of `ad355355`, with stdin closed. stderr is empty: there
was no "sandbox could not be applied". The prompt, the report (verbatim), stderr, the version and the run line are in
`reads/grok-20261128/`. It found three findings it classed as blocking, (a) to (c), and five class (d) notes.

**The blocking findings:**
- **(a) R6 dropped zero-variance cells.** Fixed. R6's `median_abs_b_over_sigma_band` is now the declared median over
  all cells. It is `null` when any cell has zero band variance, and the record carries the counts (`b` zero or
  nonzero) with the positive-variance-only median beside it, labelled as such.
- **(b) C-PSD passed a matrix whose largest eigenvalue is ≤ 0.** Fixed. The check no longer divides:
  λ_min ≥ −1e-12·max(λ_max, 0). For C it also needs λ_max > 0 and a positive diagonal, so every R2 ratio is defined.
  `part_tune` now catches what `part_data` does (Stop, OSError, KeyError, ValueError), so an exception becomes a STOP
  record, not a crash.
- **(b) C-ID judged a null band at the global scale. Not changed; for the director.**
  - §6 says "zero to 1e-12 of max |V_nom|". The code uses each band's own max |V_nom|. Only when that is below 1e-12
    of the largest max |V_nom| across all bands (a null band) does it use the global one.
  - So every band meets the declaration's bound at the global max, and non-null bands meet a stricter one.
  - A strict own scale for a null band would STOP on rounding. Its b is about 1e-13 of X0, so μ − X0 keeps only a few
    significant digits.
  - Grok's scenario leaks at most about 1e-12 of the largest band into M.
  - **Measured on the committed tune blocks:**
    - NormDISCC is the one null band: its max |V_nom| is 2.4e-24 (AR23) and 1.8e-24 (G18) of the largest band's, and
      max |b|/X0 is 1.6e-12 and 1.5e-11.
    - At its own scale its rounding residual is 5.5e-4 (AR23) and 1.1e-3 (G18), so a strict own-scale C-ID would STOP
      every run.
    - Every other band is judged at its own scale, with a worst of 2.2e-13.

**The class (d) notes:**
- R6 now divides by X0_c, as declared, not |X0_c|, and a zero X0 cell is a C-FINITE STOP.
- An empty set of rank bands refuses, rather than labelling.
- The top-five keys name the declared bands (`ranks_140_ndf`).
- `write` serializes before creating the file, and a non-finite record becomes a STOP record with rc 3.
- The NEGLIGIBLE sentence stays, per the director's ruling (C) on #1446.

**Tests:** 50 for the driver, 32 for the fetch. The final mutation run is on these sources (see Mutants).

## Mutants

`mutants_center2d.py` applies one exact-text edit per mutant to a temp-dir copy, never to the files in place. Each
mutant must make its suite fail: `test_center2d.py` for driver mutants, and `test_center2d_fetch.py`'s Fetch and Fence
classes for mutants of the reader, the verifier and the fence. The wrapper is not mutated: its tests need the git
worktree, and it is pinned by sha.

- **The final run** (`receipts/mutation.txt`, `833ff47773b6fbe55205f6ce0113b2a56f1ad4756d4e44413209d054f62026c6`), on the final sources (driver `1dc764e7…`):
  - 2026-11-28T08:28:17Z to 08:44:47Z, one process, BLAS threads 1, started at the director's go;
  - the baseline passed;
  - **71 of 71 killed**;
  - the sources hashed identically before and after.
- **Superseded runs**, kept as history:
  - `receipts/mutation-run1-superseded.txt`: 61 of 62 killed. The survivor `verify-count-off` showed that no test gave
    the verifier a consistent 15-file set, so that test was added.
  - `receipts/mutation-run2-superseded.txt`: 62 of 62 killed, on the sources before the Grok fixes.

## Part R: the rehearsal on the committed pre-G2R blocks (2026-11-28)

**Authority:** CENTER2D-BINDING-1 (issuecomment-7237048152) and the director's GO for part R only. The bound files were
checked by shasum before the run (`run-rehearsal/bound_shas.txt`): driver `1dc764e7…`, wrapper `e4ab0552…`, remote
`dd1215a1…`, verify `e3385e8e…`, fence `ee696ee6…`.

**The run:**
- a fresh worktree at `cdda5317`;
- `python3 -I -B center2d.py rehearsal --out run-rehearsal/center2d_rehearsal.json`, with OMP, OpenBLAS, MKL and vecLib
  threads at 1;
- 2026-11-28T09:09:46Z to 09:09:47Z;
- rc 0; stdout `R:AR23: OK`, `R:G18: OK`, `CENTER2D OK`; stderr empty.

**The record:** `run-rehearsal/center2d_rehearsal.json`,
`ac08d3f8a1cea1b6e611f60377cce2d0a8fb83916a7b10881bf7d2b5c2c935c8`. Status OK, with noise term "not separable,
disclosed". Every control passed at both tunes:
- C-PIN, C-FINITE (43 bands) and the C-X0 mask (205 cells);
- C-FLUX, equal to the logged sum and n_eff exactly;
- C-ID, worst 1.2e-13 (AR23) and 2.2e-13 (G18);
- C-RECON: C_univ 6.5e-21 and 5.6e-21, C_lat 0, C_T as its block sum 0;
- C-PSD for C and M;
- C-ADD, at most 7.1e-16.

The readings went to the director first, who accepted part R on 2026-11-28.

**Part R carries no label, as declared.** Its numbers describe a superseded matrix, the pre-G2R C_T. R5's per-subset
label strings in the leave-one-band-out entries, and the label list in their range, are descriptive outputs of the
bound code and decide nothing (director, 2026-11-28). The label is decided only at part D.

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
