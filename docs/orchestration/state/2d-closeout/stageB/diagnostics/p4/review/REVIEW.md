# Review: P4 G1 census package (2D closeout Stage B diagnostics)

**Reviewer:** a fresh read-only Claude Opus 5.5 session, 2026-10-12. **Same-model caveat:** the author is the
same model family. Separate sessions of one model are not independent review from another provider.
**Scope:** the package at `MINERvA-OmniFold-closeout-diag-20261012/docs/orchestration/state/2d-closeout/stageB/diagnostics/p4/`
(untracked), its NERSC copy and builds under `/pscratch/sd/j/josephrb/2d-closeout-stageB-diag-20261012/p4/`,
checked against grant `AUTHORIZATION-20261012-2d-closeout-stageB-diagnostics.md` (origin/main `9fac0ca0`,
sha256 `ac1bce59…df008`) and Stage B REPORT §2.10. I edited nothing in the package, committed nothing and
submitted no Slurm job. My login-node re-runs live only in `review-p4/`.

## Verdict: **APPROVE WITH CHANGES**

The C++ patch is correct and isolated, and I approve it as built: patched binary sha256
`d1a7cf346bed88d60e7edc360ca4836ee46a968dc6a7abd4400e066bc4a9c9e0`. No finding needs a code change or a
rebuild. Before the first job, fix **M1** (resources and cost) and **M3** (commit the pre-declaration). Fix
**M2** before the analysis runs. The MINOR items should be done before the analysis runs too.

`PATCHED_SHA` (sbatch_p4.sh:26) must be set to **`d1a7cf346bed88d60e7edc360ca4836ee46a968dc6a7abd4400e066bc4a9c9e0`**,
which I re-measured on NERSC today. Do not re-run `build.sh` after this review: it deletes and rebuilds both
build directories.

## Answers to the seven questions

1. **Census correctness: correct.** In the production CV configuration, a selected MC reco entry lands in
   one of three places:
   - `mc_background`, if it is not (signal && PS) by the reco tree;
   - `mc_signal_reco`, if its key is in `recoIDs`;
   - nowhere, otherwise.

   The hook sits at the only `continue` that drops selected entries from the background loop (`:1597-1604`).
   It tests membership in the signal loop's own `recoIDs`, filled at prod `:1288`, using the same
   `makeEventKey(mc_run, mc_subrun, mc_nthEvtInFile)` read from the same entry of the same chain.
   `AppendTruthOnlyMisses` takes `recoIDs` as `const` (prod `:689`), so miss rows cannot hide a G1 key. So
   the census catches every route into "neither", including one where the truth-mode `isSignal` in the
   signal loop disagrees with the reco-mode one in the background loop. That route would surface as
   `truth_status` 2.
   - Weight: `cvWeight` is the reco-mode CV model weight, the same value written as `w_bkg`, and the same
     construction as `mc_signal_reco`'s `w_reco`. Correct.
   - Duplicates: a double-filled duplicate whose first copy was kept is correctly treated as covered.
   - Truth classification: sound and documented. Status 0 lumps together "truth row not fiducial" and "no
     truth row". `passes()` changes only the census's own `m_TotalPassed` (MAT `Cut.h:91-98`).
   - Binning: `reported_cells.PT_EDGES/PZ_EDGES` (14×16, GeV), `GetMuonPT/Pz` in GeV. Correct.

   **Not a gap:** the converse class (reco tree not signal-in-PS, truth tree passes). It is subtracted as
   background and counted as a miss, which is self-consistent, so it does not need a census.
2. **Isolation: verified.** With `MNV101_G1_CENSUS` unset, every hook is `if(gG1)` with `gG1 == nullptr`.
   The only other differences are header includes, a static pointer and literal, and an empty
   `unique_ptr`. Census-on mode uses its own constraint instances (never the Cutter), restores
   `SetTruth(false)`, and writes its file only after `outFile->Close()`.
   - The self-test needs both `MNV101_G1_CENSUS` and `MNV101_G1_CENSUS_SELFTEST>0`, and it changes only the
     census's own view.
   - `SELFTEST` alone is inert: I ran it, and the output is identical with no census file.
   - The sbatch unsets both variables before exporting the census path.
   - The unpatched production binary cannot trigger any of this.
3. **patch.diff: exact.** `diff -u prod patched` matches the body of `patch.diff` byte for byte (182+/1−), and
   `patch` applied to the production source gives the patched copy exactly.
4. **sbatch: mostly right, but the cost is wrong (M1).** Checked:
   - account m3246, `qos=shared`, `-C cpu`, walltime 5 h < 12 h;
   - names `2dc_B4_<tag>` set on the CLI loop;
   - outputs under the namespace, binary sha guard, refusal if output exists;
   - absolute paths only, no `BASH_SOURCE`/`$0`, no `set -u`, no `--export`. `setup_salloc_env.sh` reads its
     own `BASH_SOURCE`, which is correct for a sourced file.

   The enforced worst case is **1.52 node-h, not 1.0** (M1).
5. **analyze_p4.py: the logic matches DESIGN §6**, but the script cannot run as deployed (M2) and the
   outcome gate is thin (m4). compare_outputs.py compares what it claims for these files (m7).
6. **Materiality rule: sensible and conservative.**
   - Cell threshold σ_rel/3: median 2.03%, minimum 1.37%.
   - Integral threshold 0.5%, about σ_int/8.5 (σ_int = 4.23%).
   - The σ used, universe ⊕ boot_vl170 ⊕ ml, reproduces the c04-repair block-sum per-cell median of 6.09%
     exactly, so calling it "total" is right.

   It is **not yet fixed before data** (M3).
7. **Smoke evidence: reproduced** (see "Verified myself").

## Findings

**M1 — MAJOR — sbatch_p4.sh:7-9, DESIGN.md §5 "Cost": billing is 6 CPUs, not 4, and the worst case with P5 can pass the 3.0 node-h ceiling.**
- The shared partition (`shared_milan_ss11`) has `MaxMemPerCPU=1905`. `--mem=8G` therefore forces
  ceil(8192/1905) = 5 CPUs, and whole-core rounding makes that 6.
- Precedent: array 55985231 asked for 16G and got `AllocCPUS=10, billing=10`.
- Enforced worst case: 13 × 5 h × 6/256 = **1.52 node-h**, over Stage B's 0.9 price for P4. Add P5's upper
  price of 1.5 and the total is 3.02 > **3.0**.

Fix:
- `--mem=7600M` (≤ 4 × 1905 MB) keeps billing at 4 CPUs.
- `--time=02:00:00`: the largest playlist, 1M, is 98 files × ~17–30 s ≈ 0.5–0.8 h.
- That gives 13 × 2 × 4/256 = **0.41 node-h**.
- Projected peak RSS for 1M is about 4–5 GB: the 1.3 GB smoke, plus the truth-denom cache (~1.7 GB), the
  key sets, and the census map (~6.2 M entries, ~0.25 GB). 7.6 GB is enough. If 1M's May MaxRSS is on
  record, check it.
- Correct DESIGN §5 ("billing ≈ 4", "1.0 node-h", and "the production array used 2 CPUs and 8 GB", which
  would have been allocated 6 CPUs).

**M2 — MAJOR — analyze_p4.py:46-48: the import fails on the deployed checkout.**
- `REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold` is checked out at `32e403b8` (2026-08-29) and has **no**
  `2d-unfolding/uq/reported_cells.py`, so `from reported_cells import …` raises `ImportError`.
- Fix: import from a pinned checkout that has the file (e.g.
  `/pscratch/sd/j/josephrb/2d-closeout-c04repair-20261012/repo/2d-unfolding/uq`) and assert that file's
  sha256 against origin/main's blob. Or vendor the two edge arrays and assert them against that blob.
- Also pin the inputs:
  - `EU` (:51) to sha256 `4f5a1b6d…eb2c`, which I verified matches DECISION-20261011;
  - the `sigma_json` argument to `4e48f639…0ef8` (main's `c04-repair/products/sigma_abs_205_repaired.json`;
    the NERSC build copy is identical).
- Read `hXSec2D` with `reported_cells.grid_hist_to_array`, which checks the edges. I checked them by hand
  and they are correct today.

**M3 — MAJOR — process: the materiality rule is not yet pre-declared in any durable sense.**
- DESIGN.md and analyze_p4.py are untracked files in a local worktree.
- Their mtimes (09:23–09:24) are *after* the one-file smoke result nG1 = 0 (09:21). The thresholds do not
  look tuned to that result, but the order should be disclosed.
- Fix: commit the package to origin, with `PATCHED_SHA` filled in and M1 applied, **before** the first
  `sbatch`. Cite that commit in the diagnostics REPORT as the pre-declaration. Copy `sbatch_p4.sh` and
  `analyze_p4.py` to the NERSC namespace from that commit and check their sha256 (neither is on NERSC yet).

**m4 — MINOR — analyze_p4.py:151-155: the outcome is gated only on the no-op control.**
Add explicit `INCONCLUSIVE (<reason>)` outcomes, instead of exceptions or silent passes, for:
- a missing job output, or `provenance.txt` without `rc=0`, or a bin sha different from the reviewed one;
- `selftestN != 0` or `nSelftestInjected != 0` in any census file;
- a counter identity failure: `nBkgSkipped != nBkgSkippedInReco + nG1 + nG1DupKey`.

Also report `nSigLoopNoTruthPassReco` against `nG1` as the check that truth-mode and reco-mode classification
agree.

**m5 — MINOR — runEventLoopOmniFold_g1census.cpp:254; sbatch_p4.sh:57-60: a failed census write exits 0.**
`WriteG1Census` returns silently when it cannot open its file. Rather than patching the code (which would
mean a rebuild and re-review), add to the sbatch, for `T<12`:
`[ -s g1_census.root ] || { echo "REFUSE: no census file"; exit 3; }`.

**m6 — MINOR — analyze_p4.py:101,133-137: G1 outside the grid is invisible.**
`np.histogram2d` drops rows outside PT/PZ_EDGES. Report the census `wG1` total next to `G.sum()`, plus the
out-of-grid weight. State that `integral_f_S` covers the grid (all 224 cells), not only the 205 reported
ones.

**m7 — MINOR — compare_outputs.py:31-36,98-102: unknown object classes compare vacuously equal.**
`scalar_value` returns `None` for any class other than TNamed or TParameter, so `None == None` passes. This
is not live: I checked both the smoke outputs and the May 1L file, and they contain only TTree, TParameter
and TNamed. Fix: treat unhandled classes as DIFFERENT, or compare `TBufferFile` bytes of the streamed
object.

**m8 — MINOR — sbatch_p4.sh:10,13-15: a plain `sbatch sbatch_p4.sh` breaks the naming rule.**
The header `--array=0-12` means a plain submission runs 13 tasks under the default job name. Add
`[ "$SLURM_JOB_NAME" = "2dc_B4_$TAG" ] || { echo "REFUSE: job name"; exit 2; }` after the `TAG` is set.

**m9 — MINOR — grant reading: 13 loops against "≤ 12 instrumented event loops".**
`ctl1L` is uninstrumented (the unpatched binary), so I read it as allowed. Record that reading in the
diagnostics REPORT, or have the director confirm it. Under M1 the cost question goes away either way.

**n10 — NIT — analyze_p4.py:27 says bits 4-7, but :105-107 takes the first failure over bits 0-7.** Make the
docstring match the code.

**n11 — NIT — runEventLoopOmniFold_g1census.cpp:227: the weight of duplicate G1 keys is not kept.** It
matters only for the 1E double-fill. If the code is ever touched, add `wG1DupKey`. Otherwise report
`nG1DupKey`.

**n12 — NIT — DESIGN.md §3: "the sha256 differs only by build paths" is unverified.** Say "same size; the
byte difference is not characterised". Nothing depends on it, since the jobs use the rebuilt copies and the
control compares rebuilt against rebuilt. Both binaries link the same `MINERvA101/opt/lib` MAT libraries
(RPATH and `ldd` checked).

**n13 — NIT — sbatch_p4.sh:48-53: provenance does not record the script that ran.** Add `sha256sum "$0"` to
`provenance.txt`. `$0` is the spool copy, which is exactly the script that ran.

**n14 — NIT — DESIGN.md §7.1: the key-packing risk can be closed, not just "not expected".** For every Δrun
from 1 to 2,000,000, (Δrun·10¹⁶ mod 2⁶⁴) stays more than 10¹² from 0. So no wrapped collision is possible
while subrun < 10⁴ and nth < 10⁸.

## Verified myself

- **Production source.** sha256 `57792e42…12be3` on origin/main (`3921dec4`) and in the NERSC checkout.
  `src/unpatched` differs from the production tree (build dirs excluded) in no file. `src/patched` differs
  from `src/unpatched` only in `runEventLoopOmniFold.cpp` (`fb23240e…`).
- **Patch.** Body identical to `diff -u`; applies exactly.
- **Binaries.** On NERSC today: unpatched `1ab7525e…50ae`, patched `d1a7cf34…c9e0`. Both have the same RPATH
  and load the same MAT libraries.
- **Flag-off identity, re-run.** In `review-p4/`, with no `MNV101_*` in the environment, I ran four
  variants on the same 1A MC file (`run00110018`) and data file: unpatched, patched with the census unset,
  patched with the census on, and patched with `SELFTEST=7` only. Each took about 17 s with 1.31 GB RSS. I
  compared each patched variant to unpatched in two ways:
  - with my own entry-by-entry, leaf-by-leaf comparator (`indep_cmp.py`, which does not reuse
    compare_outputs.py), over the trees data 1,981, mc_background 1,133, mc_signal_reco 57,862 and
    mc_truth_denom 57,862, plus all 12 objects: **IDENTICAL** for all three variants;
  - with compare_outputs.py `--strict`: IDENTICAL.

  Stdout is identical for census-unset and SELFTEST-only; census-on adds only its two `[G1]` lines. Program
  stderr, before the `/usr/bin/time` block, is identical.
- **Census counters on that file.** nBkgSkipped = nBkgSkippedInReco = 37,440, which equals the independent
  count of `mc_signal_reco` rows with `sim_pass==1` (37,440). Also nG1 = 0, nSigLoopNoTruth = 0,
  nTruthFail = 417,388, nTruthFidFailStored = 62,982, selftestN = 0.
- **Analysis inputs.** E_U sha256 matches DECISION-20261011. `hXSec2D` is 14×16 on the grid with 205 cells
  > 0. The set of sigma-JSON `cells` equals E_U > 0 and is in C order. Per-cell σ_rel has median 6.09%,
  minimum 4.10% and maximum 23.1%.
- **Code history.** The `d1bc8813` source has sha256 `89d85664…` and the same gate and skip at `:381-383` and
  `:444-445`, as DESIGN says.
- **Slurm.** `MaxMemPerCPU=1905` on the shared CPU partition. Array 55985231 shows the CPU rounding.
- **Not verified.** Build reproducibility (re-running `build.sh` would delete the reviewed builds), full-playlist
  memory and time, the status-1 path on a real G1 row, and the bridge to the May products.

## sha256 of every file reviewed

| file | sha256 |
|---|---|
| p4/DESIGN.md | d4d99d7f314f96b3320e6661283874a1bb5f1422b6bc05302371bdfdf0ee1f73 |
| p4/runEventLoopOmniFold_g1census.cpp | fb23240e971fd78d8117c274a02eb375714906a88e7a6f2fad54652342ad00f8 |
| p4/patch.diff | 6e9171fefe1691e42dafe9ad85e0a0f6c5b7e98459f7887713aa5681ab44bc48 |
| p4/build.sh | da5a8a582f5273abd0f4549837723ac8ae4b1deffb04e437fa64bebacaf9bce9 |
| p4/smoke.sh | b19419ea352d03ae6a368a1efc6694aae1ea265b029cc9cbb842fad292be1bcd |
| p4/sbatch_p4.sh | 1715b46bbaa507d932b4d464aa52b765a007dd790613ca5c2ac89a6250256116 |
| p4/compare_outputs.py | 9f955f067393d722f296dc1c0241e911d513134c6ba2f375693512c3e800c19f |
| p4/analyze_p4.py | e6bc80186977051e4b518f73673a540da063cfb0e564f6a78d9443c9f5a6e4c0 |
| p4/SHA256SUMS | 0baef1f9d4e0fe62395a30f3841672b67430893e2c3a3ab0acf0be60ee369611 |
| p4/evidence/cmp_patched_{off,on,self}.txt | b01beaff036a0273ac9fcbc72cb5d9bfd47d298a963e725ac1e202ac17a06b37 (all three) |
| p4/evidence/flags.txt | a42a484928a37c4c61b39f9949cb724829d14ee26f68dea6ac2a93164eef30bf |
| p4/evidence/SHA256SUMS.nersc | d8eb7fb5b825a3dd52ce3e1c18f7551ca5f1f854b5b18bcfe05878ea98353e27 |
| p4/evidence/smoke_run.txt | f83243b1283bc950e39a93012872fa65d22936c17d4d2c654aa9d8b51b23d27b |
| p4/evidence/source.sha256 | 58c6b505810c9388c6cea369780053529fee40ca1d04d15374acd6f0c52c2a77 |
| production `runEventLoopOmniFold.cpp` (main 3921dec4 and NERSC) | 57792e42fe3f5a663016f94b91a5631fc50349135c92b35a08eaefcb85812be3 |
| NERSC p4/build/patched/runEventLoopOmniFold | d1a7cf346bed88d60e7edc360ca4836ee46a968dc6a7abd4400e066bc4a9c9e0 |
| NERSC p4/build/unpatched/runEventLoopOmniFold | 1ab7525e41c4a16eba728ac29dac8bfdcbfa792cc16bb8ca2ba141a24eb950ae |
| grant AUTHORIZATION-20261012-2d-closeout-stageB-diagnostics.md (origin/main) | ac1bce590be2606da9ccfb81637ca659348161851c283c093af258b2d10df008 |
| stageB/REPORT.md (origin/main) | 3cf11a34734dc0139b806efe49481ef0e081e34a947c76d8a23f22401719e424 |
| E_U `2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root` | 4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c |
| sigma_abs_205_repaired.json (main and NERSC c04repair build) | 4e48f6392c9e84a5ad2f9b32bf01ac854f5b63ce2003d3b366a1956b8ee80ef8 |
| reviewer tool review-p4/indep_cmp.py | 2247f49de1a73baa9921e5033f91ef5c0bde4e13c92ea7d6f066758064d13ee2 |
| review-p4 re-run outputs: unpatched / patched_off / patched_on / selftest_only `runEventLoopOmniFold.root` | a1200111… / 55506f4a… / 36e18d1c… / de213c05… (the ROOT files carry a timestamp and UUID, so these differ; contents are identical as above) |
| review-p4/patched_on/g1_census.root | fd22c8f9270b6e581146e9162521668a610aa60ed364a98a597e3cf9ca4d4fac |
