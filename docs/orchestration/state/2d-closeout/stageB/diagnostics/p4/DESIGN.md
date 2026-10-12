# P4 — G1 census: design (DRAFT, not submitted)

**Grant:** [`AUTHORIZATION-20261012-2d-closeout-stageB-diagnostics.md`](../../../../../AUTHORIZATION-20261012-2d-closeout-stageB-diagnostics.md)
(sha256 `ac1bce59…`), item P4, ≤ 12 instrumented event loops. **Owner:** 2D closeout executor (2d closer).
**Status:** patch, build, login-node smoke test, no-op control and positive control done on one MC file.
- Review ([`review/REVIEW.md`](review/REVIEW.md), sha256 `f2cc6aaf…`): APPROVE WITH CHANGES, with the patched
  binary `d1a7cf34…c9e0` approved as built. The changes are applied below with no C++ change and no rebuild.
- No Slurm job has been submitted.

**Order of events (review M3).** The materiality rule (§6) and `analyze_p4.py` were written about 2–3 minutes
*after* the one-file smoke result nG1 = 0 (§4); the file mtimes are 09:23–09:24 against the result at 09:21.
The thresholds were not tuned to that result: they are set from the repaired σ, not from any G1 number. The
rule is frozen by the commit that lands this package, before the first `sbatch`. The diagnostics REPORT cites
that commit as the pre-declaration.

## 1. What is measured

G1 (Stage B §2.10): an MC reco-tree entry that **passes the reco selection** and is **signal in the 2D phase space
by the reco tree's own `mc_*` branches**, but is **not a row of `mc_signal_reco`**, so it is in neither tree:
- the signal-reco loop keeps a phase-space entry only if its key is in the truth-tree set `truthDenomIDs`
  (`runEventLoopOmniFold.cpp:1210-1212` at sha256 `57792e42…` = `main` `3921dec4`);
- the background loop skips every selected entry that is signal and in phase space (`:1454-1456`).

The census is taken where it can be complete: in the background loop, at the skip. Every selected entry that
the loop skips as signal-in-phase-space is looked up in the signal loop's own key set `recoIDs`. An entry
whose key is absent is a G1 row. This catches every route into "neither tree", not only the
`truthAgrees` route. A cross-check counter in the signal loop (`inPhaseSpace && !truthAgrees`, with and
without `passesReco`) measures the `truthAgrees` route on its own.

Per G1 row the census records:
- the key (`mc_run`, `mc_subrun`, `mc_nthEvtInFile`);
- the reco (pT, p∥) and the CV reco-mode weight, the same weight a selected row carries in
  `mc_signal_reco` or `mc_background`;
- the reco tree's true (pT, p∥);
- a truth-tree classification:
  - `truth_status` 2: the key is in `truthDenomIDs`, i.e. the truth row passes, yet the key is absent from
    the reco tree;
  - `truth_status` 1: a fiducial truth-tree row (ZRange && Apothem) failing signal && PS was seen, and
    its 8-bit mask of passed constraints is recorded. The constraints are IsNeutrino, IsCC, ZRange,
    Apothem, MuonAngle 20°, PZMuMin 1500, MaxPzMu 60000, MaxPtMu 4500, evaluated with the census's own
    instances at weight 0;
  - `truth_status` 0: neither.

**Code-history check.** The production CV omnifiles (2026-05-14 to 05-18, behind `E_U`'s `43f8cc16…`) were
made by the code committed as `d1bc8813` (2026-05-18, sha256 `89d85664…`). The G1 logic there is the same
(`d1bc8813:…:381-383` gate, `:444-445` skip). The current source adds branches and objects but not
selection logic on this path; §5's bridge tests that on the outputs.

## 2. The patch

| file | sha256 |
|---|---|
| production source `MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp` (main `3921dec4`; identical on NERSC) | `57792e42fe3f5a663016f94b91a5631fc50349135c92b35a08eaefcb85812be3` |
| diagnostic copy [`runEventLoopOmniFold_g1census.cpp`](runEventLoopOmniFold_g1census.cpp) | `fb23240e971fd78d8117c274a02eb375714906a88e7a6f2fad54652342ad00f8` |
| [`patch.diff`](patch.diff) (182 added lines, 1 removed) | see SHA256SUMS |

- **Off by default.** Everything is behind `MNV101_G1_CENSUS=<path>`. With it unset, the global `gG1` is
  null and every hook is `if(gG1)`.
- **Hooks**, five in all:
  - the truth loop, before the `!activePassesTruth` skip, stores the fiducial-failure masks;
  - the signal loop, after `truthAgrees`, keeps the cross-check counters;
  - the background loop, at the skip, runs the census;
  - in `main`, the census is set up after `mycuts`; it refuses the full phase space, truth-only mode,
    missing-miss mode and the active-universe mode;
  - in `main`, the census file is written after `outFile->Close()`.
- **Isolation.** The census never calls the Cutter, so the printed Cutter statistics are unchanged. It
  writes only a separate ROOT file, after the main file is closed, so `gDirectory` is never moved during
  the loops.
- **Positive control (test only).** `MNV101_G1_CENSUS_SELFTEST=N` makes the census treat every skipped key
  with key % N == 0 as absent from the reco tree. The census must then record exactly those keys, as
  status 2. It changes only the census's own view, never `recoIDs` or an output tree.

## 3. Build ([`build.sh`](build.sh))

- An unpatched and a patched copy of the source tree are built in
  `/pscratch/sd/j/josephrb/2d-closeout-stageB-diag-20261012/p4/{src,build}/`. The build uses the production
  cache's compiler, flags and package directories (`build/flags.txt`) and only the target
  `runEventLoopOmniFold`. It never touches `opt/build_MINERvA101` or `opt/bin`.
- Login node, about 10 s each.
- The unpatched copy rebuilds reproducibly: `1ab7525e…` both times. It is 392,032 B, the same size as the
  production binary `opt/bin/runEventLoopOmniFold` (`61d7dfbf…`, 2026-07-18); the byte difference is not
  characterised. Nothing depends on it: the jobs use the rebuilt copies, and the control compares rebuilt
  against rebuilt. Both link the same `MINERvA101/opt/lib` MAT libraries (reviewer: RPATH and `ldd`).
- `build.sh` deletes and rebuilds both build directories, so it must **not** be re-run after the review.
- Patched binary: `d1a7cf34…` (the current patch).

## 4. Smoke test, no-op control, positive control ([`smoke.sh`](smoke.sh); login node, 2026-10-12)

One 1A MC file (`run00110018`, 15.2 GB) and one 1A data file. Each variant took about 17–27 s, with 1.3 GB RSS.

| variant | result |
|---|---|
| patched, census unset, vs unpatched | trees (data 1,981; mc_background 1,133; mc_signal_reco 57,862; mc_truth_denom 57,862 entries; every branch), all objects and stdout **IDENTICAL** |
| patched, census set, vs unpatched (main output) | **IDENTICAL** (strict); census file written |
| patched, census + SELFTEST=7, vs unpatched (main output) | **IDENTICAL**; census recorded 5,285 rows = the 5,285 injected keys, all status 2, every key ≡ 0 mod 7: **PASS** |
| census on the real file | **nG1 = 0**; 37,440 skipped signal-in-PS entries, all in the reco tree; signal-loop `inPhaseSpace && !truthAgrees` = 0; 62,982 fiducial truth-failure masks stored |

So on this one file the comment's "~1.8%" class is empty. That comment describes the reco-side surplus that
the Phase-18 gate removed. The question P4 answers is whether any *selected* entry falls through, in any
playlist.

Not tested by the smoke: the status-1 mask path on a real G1 row, since none exists in this file.

**Analysis smoke (review M2).** `analyze_p4.py` ran end to end on these outputs, using a layout
(`analyze_smoke/make_layout.sh` on NERSC) that links 1A to the census-on output and `ctl1A` to the unpatched
one, with `provenance.txt` reconstructed from the smoke run.
- **Real census:** outcome `MEASURED; below the pre-declared materiality bound`.
  - The pins hold: `reported_cells.py` `2ddf7c9f…`, E_U `4f5a1b6d…`, σ JSON `4e48f639…`, both binaries.
  - No-op control `ctl1A` vs `1A`: IDENTICAL.
  - G1 = 0; nBkgSkipped = nBkgSkippedInReco = 37,440.
  - Bridge 1A: DIFFERENT, as expected for one file against the full May playlist.
- **Self-test census as input:** outcome `INCONCLUSIVE (1A: self-test active …)`, the gate firing as
  designed.
  - Its numbers exercise the non-empty path: census wG1 4,273.9 = 4,257.6 binned on the grid + 16.4 out of
    the grid.
  - integral f_S = 0.1405, against the expected ≈ 1/7.
  - All rows are status 2.

## 5. Jobs ([`sbatch_p4.sh`](sbatch_p4.sh); DRAFT)

- **Shape.** 13 single-task jobs, `2dc_B4_<tag>`:
  - tags 1A…1P run the patched binary with the census on, in the production CV configuration;
  - `ctl1L` runs the unpatched copy on 1L, the smallest playlist (6 MC files).
- **Resources.** Shared QOS, `-C cpu`, 4 CPUs, `--mem=7600M`, walltime 2 h.
  - **Billing rule.** The shared CPU partition sets `MaxMemPerCPU=1905` (MB). A job is allocated, and
    billed for, max(CPUs, ⌈mem / 1905 MB⌉) CPUs, rounded up to whole cores.
  - So 8 GB would have forced ⌈8192/1905⌉ = 5 → 6 billed CPUs. Precedent: array 55985231 asked for 16 GB
    and got `AllocCPUS=10`. The same rule applies to the May production event-loop array's "2 CPUs,
    8 GB": it would have been billed 6 CPUs.
  - 7600 MB ≤ 4 × 1905 keeps billing at 4.
  - Projected peak RSS for the largest playlist (1M, 98 files) is about 4–5 GB: the 1.3 GB smoke, plus
    the truth-denom cache (~1.7 GB), the key sets, and the census map (~6.2 M entries, ~0.25 GB).
  - 1M's expected wall time is 98 × 17–30 s ≈ 0.5–0.8 h, inside 2 h.
- **Output.** Only to `…/p4/out/<tag>/`. `out/` must exist before submission, since it holds the Slurm logs.
- **Retry procedure (re-review r2).** The driver opens its output file before the loops, so a killed or
  failed job leaves `runEventLoopOmniFold.root` behind, and the job's refusal blocks a resubmission. To
  retry:
  - move `out/<tag>` aside to `out/<tag>.failed-<jobid>`, and record the move (from, to, reason, time) in the
    diagnostics REPORT;
  - retry only after a diagnosed infrastructure cause (node failure, filesystem error, scheduler kill not
    caused by the job's own limits), never because of a scientific result;
  - keep the `sacct`-recomputed total for P4 + P5, retries included, within the grant's 3.0 node-h ceiling.
- **Refusals.** A job refuses if:
  - its binary's sha256 differs from the reviewed one (`PATCHED_SHA` = `d1a7cf34…c9e0`; unpatched
    `1ab7525e…`);
  - its output exists;
  - its job name is not `2dc_B4_<tag>`;
  - for a census job, the census file is missing or empty after rc 0 (exit 3).
- **Provenance.** Each job records the manifests' sha256, the environment, the sha256 of the spooled script
  that ran, rc, and the output sha256.
- **Instrumented-loop count (grant: "≤ 12 instrumented event loops").** `ctl1L` runs the *unpatched*
  binary, so it is not an instrumented loop. The jobs are 12 instrumented loops plus 1 uninstrumented
  control. That reading is the reviewer's (m9) and is put to the director for confirmation.
- **Controls at scale** (analysis step 1):
  - no-op: `ctl1L` vs `1L` main output, strict tree content, must be IDENTICAL, or P4 is INCONCLUSIVE;
  - bridge: each playlist's main output vs the May production `2d-unfolding/runEventLoopOmniFold_<PL>.root`
    on common branches. Equality ties the census to `E_U`'s input; a difference is reported, not hidden.
- **Cost.** 489 MC files over the 12 playlists, at about 20–30 s per 15 GB file (smoke), is about
  3.4 core-h of event loop.
  - At billing 4 that is about 0.05–0.15 node-h, including the data loops and the control.
  - The enforced worst case is 13 × 2 h × 4/256 = **0.41 node-h**. The draft's 8 GB / 5 h would have been
    13 × 5 × 6/256 = 1.52 node-h (review M1).
  - Stage B priced P4 at 0.9 node-h, against the grant's 3.0 for P4+P5.
  - The earlier array 55985231 (`ev5d_active`, shared, 10 CPUs, 16 GB, 1.2–4.9 h) was the 5D active-universe
    loop, which is far heavier than this CV loop, so its timing is not reused.

## 6. Analysis ([`analyze_p4.py`](analyze_p4.py)) and what implicates `E_U`

- **Binning.** G1 rows are binned on reco (pT, p∥) over the analysis edges, weighted by `w_reco`.
- **Denominators**, from the same jobs:
  - S_c, the `mc_signal_reco` rows with `sim_pass == 1`;
  - B_c, `mc_background`;
  - D_c, data with `measured_pass == 1`.
  MC is summed over playlists and scaled by Σ data POT / Σ MC POT, the driver's hadd convention.
- **Reported per cell and integral:** f_S = G1/S, f_SB = G1/(S+B) and f_D = scale·G1/D.
  - The integrals cover the whole 224-cell grid, not only the 205 reported cells.
  - The census total `wG1` is reported next to the binned sum; the difference is the out-of-grid weight.
  - Also the status breakdown, the lowest-numbered failing truth constraint for status-1 rows, and
    reco − true medians.
  - `nSigLoopNoTruthPassReco` (the truth-key route, with truth-mode classification) is reported against
    `nG1` (all routes, reco-mode classification).
- **INCONCLUSIVE (with the reason)** if any of these fails:
  - a job output is missing or empty;
  - `provenance.txt` lacks `rc=0`;
  - a binary sha256 differs from the reviewed one;
  - `selftestN` or `nSelftestInjected` is nonzero;
  - the counter identity nBkgSkipped = nBkgSkippedInReco + nG1 + nG1DupKey fails;
  - the no-op control is not IDENTICAL;
  - the σ JSON's cells are not E_U's reported cells.
- **Pins checked at start:** `reported_cells.py`, imported from the `09c8bae0` archive at
  `/pscratch/sd/j/josephrb/2d-closeout-c04repair-20261012/repo`, has origin/main's sha256 `2ddf7c9f…`; the
  production checkout at `32e403b8` lacks it. E_U is `4f5a1b6d…`, read with `grid_hist_to_array`, which
  checks the edges. The σ JSON is `4e48f639…`.
- **Pre-declared materiality.**
  - An unsubtracted G1 row enters data − background at its reco-cell fraction, so f_S is a first-order
    proxy for the central-value bias in the matching truth cell. It is not an unfolded shift.
  - **IMPLICATES_E_U** if the integral f_S ≥ 0.5%, or if any reported cell has f_S ≥ σ_rel,c / 3, where
    σ_rel,c is the repaired per-cell total relative σ (c04-repair `sigma_abs_205_repaired.json` ÷ `E_U`).
    That outcome is reported to the director at once and changes nothing by itself (grant).
  - Otherwise: MEASURED, below the bound.
  - Any failed gate above makes the outcome INCONCLUSIVE.
  - A scientific result is never a reason to retry.

## 7. Open points for the reviewer and the director

1. **Key packing: closed.** `makeEventKey` packs (run·1e8 + subrun)·1e8 + nth into `uint64_t`, which wraps
   for the 6-digit MC run numbers (1.1e21 > 1.8e19), so keys are taken mod 2^64.
   - The reviewer (n14) checked every Δrun from 1 to 2,000,000: (Δrun·10¹⁶ mod 2⁶⁴) stays more than 10¹²
     from 0.
   - So no wrapped collision is possible while subrun < 10⁴ and nth < 10⁸.
   - The census uses the same packing.
2. **Bridge.** Whether the current source reproduces the May per-playlist outputs on common branches is
   unmeasured until the jobs run. If it does not, the census still measures the mechanism, but its number
   for `E_U` needs that caveat.
3. **Status-1 path.** The status-1 classification path has no real-data exercise yet (the smoke file has
   no G1 rows).
4. **Duplicate G1 keys (n11).** Their weight is not kept, only their count `nG1DupKey`, which is reported.
   It matters only for the 1E double-fill. If the C++ is ever touched again, add `wG1DupKey`.
5. **Production binary (n12).** The relation of the rebuilt unpatched binary to the July production binary
   is "same size", not byte-characterised (§3).
