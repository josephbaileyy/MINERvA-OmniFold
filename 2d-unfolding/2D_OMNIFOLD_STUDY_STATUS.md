# 2D OmniFold Study — Status

**Last updated**: 2026-05-14 (Phase 17 code complete, validation pending; numbers below are Phase-16 production)

Companion docs: `2D_OMNIFOLD_REFERENCE.md` (workflow invariants and gotchas),
`2D_OMNIFOLD_RUN_LOG.md` (timestamped chronology), `PLOT_GUIDE.md` (PNG index
and naming convention).

---

## Goal

Reproduce arXiv:2106.16210 (Ruterbories et al., Phys. Rev. D 106, 032001) —
MINERvA ME FHC d²σ/(dp_T dp_||) CC inclusive — with 2D **unbinned** OmniFold
in place of D'Agostini IBU. Validated on playlist 1A, then run on full
12-playlist ME FHC.

---

## Current state

**Phase 16 closed (2026-05-09): post-fix re-run reproduces the paper
total to 0.5 % and collapses the low-p_|| gradient.** The residual the
study had been chasing for ~3 weeks was a missing OmniFold input-
completeness correction in the local cross-section formula, not a
generator-config, flux-file, selection, or reweighter issue.

The unfold script had divided `hUnfold2D` by (Φ · N · POT · ΔpT · Δp_||)
with no rescaling from the OmniFold-input truth subset
(`mc_signal_reco` truth-pass, 24.46M events) up to the full truth phase
space (`mc_truth_denom`, 32.85M). OmniFold's step-1 miss regression
handles within-input misses (`sim_pass = False` events in
`mc_signal_reco`) but cannot recover events absent from the input
entirely — the 8.4M-event difference, preferentially at low p_||.

Fix verified end-to-end against the paper:

| | pre-fix | predicted | post-fix |
|---|---|---|---|
| σ_total / paper | 0.752 | 0.989 | **1.0049** |
| Global completeness c | n/a | 0.745 | 0.7503 |
| Strict-interior χ²/ndf (185 bins, full cov) | 17.4 | — | **3.188** |
| 205-bin χ²/ndf (full cov) | 20.6 | — | **3.289** |
| Median bin ratio (ours/paper, strict interior) | 0.897 | — | 1.0049 |
| Bins within 5 % of paper (strict interior) | ~0 % at low p_|| | — | 82.7 % |

The fix in `unfold_2d_omnifold_unbinned.py`:
- `compute_efficiency_2d` now uses `mc_truth_denom` for `hEffDen`
  (canonical Truth-tree denominator). `hEffNum` keeps the standard
  semantics (`sim_pass = true`), so `hEff2D` remains the paper-Fig.-5-
  comparable absolute selection efficiency for diagnostics.
- New `compute_omnifold_completeness_2d` writes `hOFCompleteness2D =
  hOFInputTruth2D / hOFTruthDenom2D` — the OmniFold input completeness
  c = N(`mc_signal_reco` truth-pass) / N(`mc_truth_denom`).
- `extract_cross_section_2d` divides by `hOFCompleteness2D` (not by the
  absolute selection efficiency, which would over-correct because
  OmniFold has already absorbed the within-input inefficiency through
  miss regression).
- Closure mode (`--closure`) sets completeness ≡ 1 so the legacy
  in-sample closure behaviour is preserved.

What this overturns (no longer suspect):
- "Flux-CV file" (Phase 14) — already ruled out by Phase 15; still
  ruled out.
- "AnaTuple generator-config provenance" (Phase 15) — local truth
  with MnvTune-v1 reweighters applied agrees with the paper MnvTune-v1
  ancillary to ≤ 1 % across p_|| = 1.5 – 9 GeV/c when the proper
  denominator is used. The 1.43× low-p_|| feature in the prior
  diagnostic was an artifact of comparing the `mc_signal_reco`-derived
  `hTruth2D` to the paper's full-truth model.
- Per-reweighter decomposition (Phase 13) — the column ratios are still
  numerically what was measured but described the shape of the
  `mc_signal_reco` subset under each reweighter, not a physical
  low-p_|| pull from any reweighter.

Outreach to MINERvA collaboration is no longer needed — there is no
missing-input hypothesis left to ask about. The remaining ~3 χ²/ndf
residual is dominated by sub-2 % shape disagreement in the highest p_||
tails, consistent with the truth-shape diagnostic.

For the full chronology, see `2D_OMNIFOLD_RUN_LOG.md` (Phase 16 closeout
subsection has the post-fix numbers and plot inventory).

### Phase 17 (code complete, validation pending, 2026-05-14): replace c with native OmniFold misses

After review with BN, the per-bin c correction is being replaced with
native OmniFold step-2 miss handling. The c factor was needed only
because the event-loop's `LoopAndFillUnbinnedMCSelectedSignalReco` walks
the AnaTuple Data/reco tree, so the 8.4M fiducial-truth events with no
reco-tree entry never entered `mc_signal_reco`.

**Implemented (Option A in run log):** event-ID matching on
`(mc_run, mc_subrun, mc_nthEvtInFile)` packed into a `uint64_t` hash key.
The reco walk now populates the set; the truth-denom walk consults it
and appends a miss entry to `mc_signal_reco` for each truth-pass event
not in the set. Output ROOT file carries `hasTruthOnlyMisses` /
`nTruthOnlyMisses` `TParameter`s; the unfold pipeline reads them, prints
a Phase-17 status line, and warns if `c_global` deviates from 1.0
(which would indicate a matching bug). The c-division code path is
unchanged — when the new miss entries are present `c ≈ 1` so the
division becomes a no-op, and pre-Phase-17 inputs still work.

Validation pending: re-run event loop on 1A as closure, then full MEHFC,
then re-run unfold and check `c_global ≈ 1` and σ_total / per-bin
agreement with the Phase-16 production
(3.055e-38 cm²/nucleon, χ²/ndf = 3.289). Until that re-run completes,
the production output is still the Phase-16 file
(`2d_crossSection_omnifold_MEHFC_5iter_postfix.root`).

See `2D_OMNIFOLD_RUN_LOG.md` Phase 17 for the full implementation notes
and resume checklist.

---

## Key reference numbers (full ME FHC, patched MINOS, 5-iter production, **post Phase-16 fix**)

Output: `2d_crossSection_omnifold_MEHFC_5iter_postfix.root` (job 52729573,
finished 2026-05-09 19:42 UTC after ~18 h 43 m wall on shared QOS).

| Quantity | Value |
|---|---|
| mcPOT (sum of 12 playlists) | 4.978e21 |
| dataPOT (sum of 12 playlists) | 1.057e21 |
| potScale (data/MC) | 0.2124 |
| Weighted full-MEHFC flux integral | 8.7407e-7 /cm²/POT |
| N fiducial nucleons | 3.2353e30 (tracker geometry constant) |
| Selected data events (reco) | 4,091,707 |
| `hMeasSub2D` integral (data − bkg) | 4.07664e6 |
| `hTruth2D` / `hUnfold2D` integrals | 4.33620e6 / 4.87974e6 |
| `hOFInputTruth2D` / `hOFTruthDenom2D` integrals | 4.3362e6 / 5.7796e6 |
| Global OmniFold input completeness c | **0.7503** |
| Step-2 weight stats | mean 1.1212, range [0.7383, 3.5332] |
| Total xsec (p_T projection = p_|| projection) | **3.055e-38 cm²/nucleon** |
| σ_total(ours) / σ_total(paper) | **1.0049** |
| Strict-interior χ²/ndf vs paper (185 bins, full cov) | **3.188** |
| All-reported-bins χ²/ndf (205 bins, full cov) | **3.289** |
| 205-bin shape χ²/ndf (total cov) | 3.269 |
| 185-bin strict-interior shape χ²/ndf (total cov) | 3.160 |
| Pull mean / RMS (205 reported bins, full cov) | −0.001 / 0.565 |
| Median bin ratio (ours/paper, strict interior) | **1.0049** |
| Bins within 5 % / 10 % / 20 % of paper (185 strict interior) | 82.7 % / 94.6 % / 98.4 % |

Paper total (reported): 3.039e-38 cm²/nucleon. Pre-fix headline numbers
(σ/paper = 0.752, χ²/ndf = 17.4 / 20.6, median ratio 0.897) are
preserved in the run log for historical reference; the corresponding
ROOTs and PNGs live under `archive_pre_phase16/`.

### Playlist 1A validation set (post-MINOS-fix, **pre Phase-16 numbers**)

The 1A iter-scan ROOTs live in `archive_pre_phase16/` and have not
been re-run with the post-Phase-16 fix; their absolute σ is low by
the input-completeness factor c ≈ 0.75. Iter-stability (the reason
the table exists) is unaffected by Phase 16 — the fix is downstream
of OmniFold and does not change the relative iteration-to-iteration
behaviour of `step2_weights`. Re-run on 1A is not currently planned
since MEHFC has been validated end-to-end; if needed, re-run with
the postfix script.

| Quantity | Value |
|---|---|
| 1A mcPOT / dataPOT / potScale | 4.069e20 / 8.973e19 / 0.2205 |
| 1A 5-iter total xsec (pre-fix) | 2.328e-38 cm²/nucleon |
| 1A 5-iter strict-interior χ²/ndf vs paper (pre-fix) | 18.4 |
| In-sample closure median ratio / RMS | 1.0000 / 0.0000 |

### Iteration convergence (1A, corrected pre-MINOS-fix scan)

| iter | hUnfold2D | xsec (cm²/nucleon) | rel RMS vs 10-iter |
|---|---|---|---|
| 1 | 448,066 | 2.4775e-38 | 6.95% |
| 3 | 448,958 | 2.4825e-38 | 3.71% |
| 5 | 449,273 | 2.4842e-38 | 2.11% |
| 8 | 449,507 | 2.4855e-38 | 0.78% |
| 10 | 449,649 | 2.4863e-38 | 0.00% |

Production uses **5 iterations** (0.08 % bias on total xsec vs 10-iter;
~17 h runtime saved).

### Post-fix χ² vs p_||-min cut (MEHFC, strict interior, full cov)

The pre-fix monotonic strip gradient (1.5–2 GeV/c at 0.572, 20–40 at
0.984) is gone post-fix. χ² as a function of p_||-min cut is now
approximately p_||-flat:

| p_|| ≥ (GeV/c) | N bins | χ² | χ²/ndf | median ratio | %<5% |
|---|---|---|---|---|---|
| 1.5 | 185 | 589.71 | 3.188 | 1.0049 | 82.7 % |
| 2.0 | 179 | 543.26 | 3.035 | 1.0031 | 83.8 % |
| 2.5 | 171 | 461.21 | 2.697 | 1.0037 | 84.2 % |
| 3.0 | 162 | 408.87 | 2.524 | 1.0034 | 84.0 % |
| 3.5 | 152 | 397.07 | 2.612 | 1.0053 | 82.9 % |
| 4.0 | 141 | 371.43 | 2.634 | 1.0053 | 81.6 % |

Low-p_|| bins no longer dominate the comparison — the truth-shape
diagnostic at the proper denominator (Phase 16) confirms `paper /
weighted` ≈ 0.99–1.00 across p_|| = 1.5–9 GeV/c, so there is no
residual low-p_|| pathology to chase.

---

## Residual disagreement — attribution

### Truth-shape attribution against the proper denominator (2026-05-08)

`diagnose_truth_shape_unweighted.py` reads `mc_truth_denom` directly from
`runEventLoopOmniFold_MEHFC.root` (32.8M events) and projects it onto the
paper (p_T, p_||) grid both unweighted (w_truth = 1) and MnvTune-v1
weighted, then compares each to the paper's MnvTune-v1 ancillary. Both
shape-normalized over the 185-bin strict interior. Result, paper /
local-weighted strip ratios:

| p_|| (GeV/c) | paper / weighted | weighted / unweighted |
|---|---|---|
| 1.5–2.0  | **0.99** | 0.96 |
| 2.0–2.5  | 1.00 | 0.95 |
| 2.5–3.0  | 1.00 | 0.95 |
| 3.0–3.5  | 1.00 | 0.95 |
| 4.0–4.5  | 1.00 | 0.95 |
| 5.0–6.0  | 0.99 | 0.99 |
| 7.0–8.0  | 0.99 | 1.05 |
| 10–15    | 1.02 | 1.22 |
| 15–20    | 1.05 | 1.24 |
| 20–40    | 1.10 | 1.32 |
| 40–60    | 1.15 | 1.60 |

Interpretations:
- The local truth + MnvTune-v1 chain reproduces the paper's MnvTune-v1
  prediction to ≤ 1 % across p_|| = 1.5 – 9 GeV/c. There is no
  generator-config or selection-cut mismatch driving the low-p_||
  residual.
- The reweighter chain moves the prior in the correct direction (column
  3): MnvTune-v1 suppresses low-p_|| by ~5 % and enhances high-p_|| by
  20 – 60 %.
- Residual in the 10 – 60 GeV/c tails (paper / weighted up to 1.15 at
  the highest bin) is small and consistent with MC stat noise / a
  minor reweighter detail at high E_ν; it does not drive the cross-
  section gradient and is left as a future improvement.

The 1.43× low-p_|| feature seen against the OLD `hTruth2D` came from
that histogram being filled from `mc_signal_reco` (24.5M events, the
reco-tree subset of truth-passing events) instead of from the canonical
`mc_truth_denom` (32.8M events). Reco-tree presence correlates with
muon kinematics — events that produce no reconstructable activity are
absent from the reco tree but present in the Truth tree, and they are
preferentially at low p_|| / high θ. So the subset's shape is depleted
at low p_|| relative to the paper, and that depletion is what the prior
diagnostic was reporting.

### Per-reweighter decomposition (historical — superseded by 2026-05-08)

Per-reweighter decomposition (`decompose_truth_weights.py`, with the
`MNV101_DUMP_COMPONENTS` truth-tree dump branches) shows the low-p_||
shape is carried entirely by the `FluxAndCV` weight column. Relative to
the high-p_|| plateau:

| p_|| (GeV/c) | combined truth | FluxAndCV | GENIE | 2p2h | MINOSEff | RPA |
|---|---|---|---|---|---|---|
| 1.5–2.0 | 0.666 | **0.672** | 0.992 | 1.000 | 1.000 | 0.998 |
| 5–6     | 0.679 | **0.704** | 0.961 | 1.016 | 1.000 | 0.987 |
| 10–15   | 0.837 | **0.844** | 0.993 | 1.004 | 1.000 | 0.995 |
| 20–40   | 0.899 | **0.899** | 1.000 | 0.998 | 1.000 | 1.000 |
| 40–60   | 1.101 | **1.101** | 1.000 | 1.002 | 1.000 | 1.000 |

`FluxAndCV` is `PlotUtils::flux_reweighter().GetFluxCVWeight(E_ν, pdg)` —
the nu-e-constrained CV flux divided by the Geant4 baseline. Local files
used:
`opt/lib/data/flux/flux-{gen2thin,g4numiv6}-pdg{14,-14,12,-12}-minervame{1D,1M,1N}_rearrangedUniverses.root`.

### Flux-CV file ruled out (2026-05-05)

Phase 15 compared our local CV flux (POT-weighted across the 12 ME FHC
playlists, mapped to 3 unique flux files via the `playlistString()`
table 1A..1F→1D, 1G/1L/1M→1M, 1N..1P→1N) against the arXiv:1906.00111 /
PRD 100 092001 ancillary CV flux (`MINERvA_Flux_pdg14_500MeVBins.csv`,
the paper-era nu-e-constrained ME FHC flux that arXiv:2106.16210 cites).
Result, paper / local across 1.5–10 GeV:

| E_ν (GeV) | paper / local |
|---|---|
| 1.65 | 1.00 |
| 2.50 | 0.89 |
| 3.50 | 0.89 |
| 5.00 | 0.90 |
| 7.00 | 0.91 |
| 9.00 | 0.93 |

The ratio is ~0.90 and approximately flat. There is no low-E_ν shape
feature that would project into a low-p_|| muon strip. Furthermore, a
flat scale on `flux_E_cvweighted` **cancels exactly** in the cross-section
ratio: the per-event `FluxAndCV` truth weight and the integrated flux
denominator (`pTmu_reweightedflux_integrated`, built by
`FluxReweighter::GetIntegratedFluxReweighted` from the same histogram)
scale together, so adopting the 2019 release would not move the
unfolded cross section in either normalization or shape (modulo small
~few-% kinematic-distribution effects from the slight E_ν dependence of
the ratio). The flux-CV file is therefore not the source of the residual
1.41× low-p_|| truth shape ratio nor of the ~16.6 % global xsec deficit.

`compare_flux_to_paper_2019.py` reproduces this comparison and emits
`compare_flux_to_paper_2019.{png,csv}`.

### Updated attribution (2026-05-08): missing OmniFold input-completeness correction

The cross section was computed as
σ = `hUnfold2D` / (Φ · N · POT · ΔpT · Δp||) — i.e., no rescaling from
the OmniFold-input truth subset to the full truth phase space. The
script's docstring claimed step-1 miss regression handled the
correction, which is partially true: it handles within-input misses
(`sim_pass = False` events in `mc_signal_reco`). It does not handle
truth events absent from the input entirely. The unfold script only
loads `mc_signal_reco` (24.5M truth-pass events that also have a
reco-tree entry); the full Truth-tree denominator `mc_truth_denom` has
32.85M, so 8.4M truth events are entirely outside OmniFold's view.

Consequence: `hUnfold2D` represents inferred truth-level data over the
mc_signal_reco subset only. To get the inclusive cross section, divide
by the **input-completeness ratio**
c = (`mc_signal_reco` truth-pass events) / (`mc_truth_denom`),
**not** by the standard absolute selection efficiency
ε = (`sim_pass = True`) / (`mc_truth_denom`). Dividing by ε
over-corrects because OmniFold has already absorbed the within-input
inefficiency — verified numerically: σ / ε ≈ 1.25 × paper, σ / c ≈
0.989 × paper.

Numerical chain (`verify_eff_fix_predicted_xsec.py`):
- c_global = 0.7503 (matches 24.5M/32.8M = 0.745).
- σ_pre_fix / paper = 0.745.
- σ_post_fix / paper = (σ_pre_fix / paper) / c_global = 0.989.

Per-strip post-fix σ / paper ratios collapse from 0.572–0.984 across
p_|| to ~1.00–1.14, consistent with the truth-shape comparison
(which already showed `paper / weighted` agreement to ≤ 1 % across
1.5–9 GeV/c when the proper denominator is used).

What this rules out (no longer suspect):
- AnaTuple generator-config mismatch: the local truth + reweighters
  reproduces the paper MnvTune-v1 ancillary in shape.
- Truth-side selection mismatch: cuts in
  `MAT-MINERvA/calculators/CCInclusiveSignal.h::GetCCInclusive2DPhaseSpace`
  were re-audited against the paper.
- Reweighter-chain version: weighted/unweighted shape moves in the
  expected direction and magnitude.
- Flux-CV files: ruled out in Phase 15.

**Decision (2026-05-08)**: hold all collaboration outreach (slide deck,
email to Callum) pending a re-run of the unfold with the fixed denom.
This is most likely an in-house pipeline bug rather than a missing
input from MINERvA.

**Outcome (2026-05-09)**: post-fix re-run (job 52729573) reproduces
σ_total / paper = 1.0049 and strict-interior χ²/ndf = 3.188, confirming
the diagnosis. No outreach needed — the discrepancy was an in-house
pipeline bug (missing input-completeness correction) and is now fixed.
See run-log "Phase 16 closeout" for the full post-fix number set.

**Method-blindness check (2026-05-10)**: re-ran the advisor's IBU 1D-
projection cross-check after applying the analogous Phase-16 fix to
`ibu_1d_projection/build_1d_ibu_inputs.py` (the same input-completeness
bug existed there). On the same Phase-16-corrected inputs, IBU and 2D
OmniFold both reproduce the paper: IBU/paper integrals 0.988 (p_T) and
0.976 (p_||); OmniFold-2D 1D-projected integrals 1.005. The two
unfolders agree to ~1.7 %, ruling out method-specific OmniFold
pathology. See run-log "Phase-16 follow-up: IBU 1D-projection
cross-check".

---

## Paper binning (arXiv:2106.16210)

Authoritative: `minerva_paper_anc/bin_mapping.txt`. The TH2D axis labels in
the ancillary ROOT file are **cosmetic rounding** (0.075, 0.325, 0.475) —
do not copy them into `util/Binning.h`.

```python
pt_edges = [0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
            0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50]         # 14 bins
pz_edges = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
            6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0]  # 16 bins
```

Phase space: θ_μ < 20°, p_T < 4.5 GeV/c, 1.5 < p_|| < 60 GeV/c.
Paper reports 205/224 bins (19 diagonal bins with pt/p|| > tan 20° are
unreported).

---

## Runtime notes

| Task | Resource | Wall time |
|---|---|---|
| C++ event loop, one playlist | shared QOS, 1 task | ~3.5 h |
| Event loop, all 12 playlists | 11-task array | ~3.7 h (parallel) |
| 2D OmniFold, 5-iter, 1A stats | shared QOS, 2 CPU, 8 GB | ~1.4 h |
| 2D OmniFold, 5-iter, full stats | shared QOS, 4 CPU, 32 GB | ~20 h |

---

## Active code

### C++ event loop (`MINERvA101/MINERvA-101-Cross-Section/`)
- `runEventLoopOmniFold.cpp` — per-playlist event loop; writes 4 TTrees
  (`mc_truth_denom`, `mc_signal_reco`, `mc_background`, `data`) with both
  `p_T` and `p_||` branches. Per-reweighter dump branches behind
  `MNV101_DUMP_COMPONENTS`. Does **not** write `pTmu_fiducial_nucleons`
  (was hadd-corrupted).
- `cuts/MaxPtMu.h`, `util/Binning.h` — paper phase-space cut and binning.
- `event/CVUniverse.h` — kinematic getters and patched MINOS-match
  override (`isMinosMatchTrack && _minos_trk_is_ok`).

### Python (`2d-unfolding/`)
- `unfold_2d_omnifold_unbinned.py` — 2D unbinned OmniFold. Masks data to
  phase space, subtracts background, fills `hUnfold2D` with
  `step2_weights * truth_w_in`, divides by **`hOFCompleteness2D`**
  (post-Phase-16 input-completeness correction). `hEff2D` is kept as
  a paper-Fig.-5-comparable diagnostic, **not** used in the cross-
  section formula.
- `plot_2d_cross_section.py` — slice grids, projections, efficiency map.
- `plot_2d_paper_comparison.py` — same overlaid with paper MINERvA-Tune-v1.
- `plot_2d_threeway_fig13.py` — Fig.-13-style paper / OmniFold / MC overlay.
- `plot_efficiency_fig5_style.py` — Fig.-5-style efficiency map.
- `plot_closure_2d.py` — closure diagnostic.
- `plot_iter_convergence.py` — iter-scan summary.
- `compare_to_paper_fullcov.py` — full-cov χ² on all 205 reported bins.
- `compare_to_paper_interior.py` — strict-interior χ² on 185 bins.
- `normalize_xsec_shape.py` — produces the self-normalized shape ROOT
  (`*_shape.root`) used by `plot_2d_paper_comparison_shape.py`; also
  emits 205-bin and 185-bin shape χ² with paper TotalCovariance
  propagated through the unit-area Jacobian.
- `plot_2d_paper_comparison_shape.py` — shape-mode paper-comparison
  plots (slice grids and pull map) on the 205 reported / 185 strict-
  interior bins.
- `combine_flux_MEHFC.py` — POT-weighted MEHFC flux from per-playlist
  baseline-flux ROOTs.
- `compare_flux_to_paper_2019.py` — Phase 15 ruleout of paper-era flux
  files vs local CV flux.
- `diagnose_truth_shape_unweighted.py` — Phase 16 truth-shape attribution
  on the canonical mc_truth_denom denominator (unweighted vs MnvTune-v1
  weighted vs paper). Replaces the earlier `diagnose_truth_shape_vs_paper.py`.
- `verify_eff_fix_predicted_xsec.py` — applies the post-fix completeness
  formula to a stored pre-fix `hUnfold2D` to predict post-fix totals
  without re-unfolding (used to verify Phase 16 before the rerun).

### SLURM (`2d-unfolding/`)
- `sbatch_evloop_array.sh` — per-playlist event-loop array.
- `sbatch_unfold_2d.sh` / `sbatch_unfold_2d_fullstats.sh` — 2D unfold (1A / MEHFC, pre-Phase-16 baselines kept for comparison).
- `sbatch_unfold_2d_fullstats_postfix.sh` — post-Phase-16 MEHFC unfold; writes to `*_postfix.root` so the pre-fix file is preserved.
- `sbatch_iter_scan_2d.sh` — iter-scan array.
- `sbatch_finalize_MEHFC.sh` — full-cov + interior χ² and plot regen.
- `sbatch_validate_1A_corrected.sh` — end-to-end 1A validation.
- `sbatch_runEventLoop_baseline_flux_array.sh` — regen baseline flux per playlist.
- `download_playlist.sh` + `sbatch_download_playlist.sh` — xrdcp via xfer QOS.

### Data / outputs
- `runEventLoopOmniFold_MEHFC.root` (2.17 GB, hadd of per-playlist).
- `runEventLoopOmniFold_{1M,1N}.root` — per-playlist intermediates kept
  on disk for spot-check use; the rest were removed after the MEHFC hadd
  was confirmed byte-clean.
- `2d_crossSection_omnifold_MEHFC_5iter_postfix.root` — **post-Phase-16
  production output** (job 52729573, finished 2026-05-09 19:42 UTC,
  ~18 h 43 m wall). σ/paper = 1.0049, χ²/ndf = 3.188 (185 strict
  interior, full cov). All 14 production PNGs in `PLOT_GUIDE.md` are
  regenerated from this file.
- `2d_crossSection_omnifold_MEHFC_5iter_postfix_shape.root` — shape-
  normalized derivative produced by `normalize_xsec_shape.py` for the
  shape-mode comparisons.
- `archive_pre_phase16/` — pre-Phase-16 unfold outputs and derived plots,
  preserved for comparison. Includes the pre-fix MEHFC ROOT, the 1A
  patched-MINOS iter-scan ROOTs, and all `MEHFC_5iter_*.png` that derived
  from the pre-fix output. Pre-fix σ_total is 0.752 × paper; these files
  document that historical state.
- `baseline_flux/` — per-playlist baseline + `runEventLoopMC_MEHFC.root`
  (POT-weighted MEHFC flux).
- `minerva_paper_anc/` — arXiv ancillary release (TH2D, 4 cov matrices,
  bin_mapping.txt, data CSV, model predictions).
- `MINERvA_Flux_pdg14_500MeVBins_arXiv1906_00111.csv` — paper-era 2019
  ancillary flux release (input to `compare_flux_to_paper_2019.py`).

### Manifests (`2d-unfolding/playlist_manifests/`)
- `1{A..P}_{MC,Data}.txt` — per-playlist local paths.
