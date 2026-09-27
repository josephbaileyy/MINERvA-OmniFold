# gen5d flux fix: exact flux reweight of the GENIE CV, GENIE+MEC and NuWro 5D predictions (s5p, 2026-09-27)

**Status: built and checked on Perlmutter. Uncommitted, so not yet quotable.** It repairs
`KNOWN_ISSUES.md` row 83 (s5p review round 1, F1). The machine receipt, `gen5d-fluxfix.json`, sits
next to this file. The cluster generated it from the products' own meta; no numbers were
hand-transcribed into it. The numbers below were copied from that receipt. Where they differ, the
receipt wins.

## What was built

The repaired products live in `/pscratch/sd/j/josephrb/s5p-20260926/gen5d_fluxfix/`:
- `genie_cv_xsec5d.npz`, `genie_mec_xsec5d.npz` and `nuwro_cv_xsec5d.npz`. Each has the same arrays
  as the gen5d originals: `xsec_flat`, `sumw2_flat`, `nevt_flat`, `n_events`, `edges_*`, `shape` and
  `meta_json`. Each has a `.meta.json` sidecar and a `_checks.json` file.
- `phi_t.npz` and `phi_t.json`: the data flux.
- `gibuu_flux_check.json`.
- `gen5d_fluxfix_marginals.npz` and `gen5d_fluxfix_marginals.json`.

The originals in `gen5d/` were not touched; their sha256 values still match `gen5d-build.json`. GiBUU
was not rebuilt.

**Code.** The code is the new file `3d-unfolding/genie/gen5d_flux_reweight.py`. It ran from the copy
`gen5d_fluxfix/code/gen5d_flux_reweight.py`; the receipt's `code_copy` field records that copy's
sha256.
- It imports `gen_to_xsec5d.py` and the converters from the sha-pinned export
  `gen5d/code/tree` (`81d94a95`) that the gen5d build ran from.
- It uses that module's event extraction, its binning and its arithmetic. It adds only the
  per-event weight and the new normalization.

**Environment.** The analysis env `root_6_28` (ROOT 6.28/12), loaded via `setup_salloc_env.sh`,
plus PlotUtils (`MINERvA101/opt/lib`) for the flux. It ran single-process on login nodes, with no
Slurm; each step took under about 2 min.

## Formulas

- **phi_s**, the density the generators actually sampled. For flux bin i of the generation range,
  `phi_s = c_i / (w_i * sum_range c)`.
  - GENIE uses [0, 50] GeV. gevgen clones `flux_numu` and zeroes bins whose upper edge exceeds
    50, then samples with `TH1::GetRandom` (`gEvGen.cxx:491-499`, GENIE v2_12_10c source on cvmfs).
  - NuWro uses [0.5, 50] GeV. That range is the non-zero bins of `flux_mefhc_numu_nuwro.root`,
    sampled with `EnergyProfile::shoot`. The E-weighted RES/DIS proposal is undone by `bias`
    (`nuwro.cc:836-839`, NuWro 21.09.1 source on cvmfs).
- **phi_t** is the flux the data normalization integrates. It is built as
  `sum_p POT_p * PlotUtils::flux_reweighter("minervame<p>", 14, nuE=true, 100).GetFluxReweighted(14) / sum_p POT_p`.
  - This is the call chain of `util/GetFluxIntegral.cpp`, with the settings from
    `runEventLoop.cpp:348-351`.
  - The histogram is `flux_E_cvweighted` of `flux-gen2thin-pdg14-minervame{1D,1M,1N}_rearrangedUniverses.root`,
    after the nu-e Constrainer, averaged over the 12 ME FHC playlists by data POT.
  - `Phi_t` is its integral over 0-100 GeV.
- **Per-event weight:** `r(E) = (phi_t(E)/Phi_t) / phi_s(E)`. It is piecewise constant on the 128
  flux bins, with 1st/50th/99th percentile 0.90 / 0.97 / 6.08 in phase space and a maximum of about
  94 in the widest bins.
- **GENIE CV:** `pred = <sigma_CC>_t,<50 * sum_bin r / sum_{all CC} r`.
  - `<sigma_CC>_t,<50 = int_0^50 phi_t sigma_CC / Phi_t = 4.1829e-38` cm²/nucleon.
  - `sigma_CC` is the (C12+H1) `tot_cc` graphs divided by 13, integrated exactly within each bin
    (the graphs are piecewise linear).
- **GENIE+MEC:** `pred = sum_bin r * <sigma_CC>_t,<50 / sum_{nonMEC CC} r`.
  - The band-convention factor becomes `sum_{nonMEC CC} r / sum_{CC} r = 0.97365` (it was 0.97129
    unweighted).
- **NuWro:** `pred = sum_bin w_e r_e / N_total`.
- **Other arrays:**
  - `sumw2_flat` is the sum of squared per-event contributions divided by dV², with the
    normalization constants treated as exact (the gen5d convention). A delta-method variance that
    includes the normalization-sum fluctuation differs by at most 0.8%.
  - `nevt_flat` holds the raw counts, unchanged.
  - The per-cell effective N is `xsec_flat²/sumw2_flat`.

## Checks

| # | check | result |
|---|---|---|
| 1 | Sampling model: E_nu per flux bin vs `N * phi_s * int_bin sigma`, plus uniform-times-sigma within bins (5 sub-bins). The pass rule is p ≥ 1e-3 for both, with no event outside the generation bins. | **PASS for every population.** GENIE CV (strict, own graphs): across p=0.83, within p=0.31. GENIE MEC non-MEC CC (strict): 0.28 / 0.53. MEC events (proxy): 0.11 / 0.74. NuWro CC (proxy): 0.21 / 0.60. NuWro RES/DIS: 0.45 / 0.71. NuWro QEL/COH/MEC: 0.36 / 0.017. **Power:** the other reading (bin mass ∝ density × width) gives chi2 = 126,044/121 for GENIE CV and 48,558/117 for NuWro. |
| 2 | Identity: r ≡ 1 with the old constants reproduces the pre-fix `xsec_flat`, `sumw2_flat` and `nevt_flat`. | **Bitwise, for all three generators.** |
| 3 | phi_t identity | `Phi_t` = 6.243343e-4 m⁻²/POT = `hFluxCV` (every pT bin equal), rel. diff 5.2e-16. Each playlist's integral equals its stored `pTmu_reweightedflux_integrated` exactly (rel. diff 0.0). `flux_numu` is bitwise the cvmfs `flux_E_unweighted`. |
| 4 | p∥ ratio to MnvTune, integrated σ, fraction with p∥ ≥ 6 | See the tables below. |
| 5 | GiBUU flux | Report only; see below. |
| 6 | 3D and (E_avail,W) marginals, and ratios to the committed predictions | Written to `gen5d_fluxfix_marginals.{npz,json}` for the VL35–VL38 re-examination. |

**How to read the check 1 modes.**
- *Strict* means the generator's own `tot_cc` graphs, with no free shape.
- *Proxy* means the GENIE graph σ multiplied by a smooth `exp(poly3(log E))` factor. NuWro's σ(E)
  is not available, and the MEC graph in `xsec_graphs.root` is zero.
- The proxy tests the flux-bin structure, not σ.

**Normalization cross-check (GENIE).** The unnormalized form `<sigma_CC>_s * sum_bin r / N` divided
by the self-normalized form is a single global constant:
- GENIE CV: 0.99897 ± 0.00110 (pull −0.93).
- GENIE MEC: 1.00059 ± 0.00113 (pull +0.52).

**Normalization cross-check (NuWro).** The primary form divided by a self-normalized form that uses
the GENIE-C12 σ shape as a proxy gives 1.0030 ± 0.0010 (pull +3.0). This is attributed to the
difference between the NuWro and GENIE σ(E) shapes; that attribution is inferred, not tested.

**Old normalization.** The old content-weighted `<sigma_CC>` (3.86755e-38) equals the correctly
integrated `<sigma_CC>_s` over the sampled spectrum (3.86736e-38). So the old normalization was
consistent with the sampled spectrum. The defect was the spectrum itself: wide bins under-weighted,
plus the non-PPFX shape.

**Flux shape.** phi_t relative to the unweighted flux, both normalized, is 0.92 below 2 GeV, 0.95
at 2–5, 1.02 at 5–10, 1.17 at 10–15, 1.29 at 15–20, 1.18 at 20–30, 1.40 at 30–50 and 1.53 at
50–100. The per-bin ratios are in `phi_t.json`.

## Results (the receipt's `marginals` and `products.*.integrated_sigma_cm2`)

Integrated σ in the 5D grid (cm²/nucleon), and the fraction of σ with p∥ ≥ 6 GeV/c:

| | before | after | after/before | frac p∥≥6 before → after |
|---|---|---|---|---|
| GENIE CV | 2.4446e-38 | 2.7478e-38 (±0.19%) | 1.1240 | 0.177 → 0.271 |
| GENIE MEC | 2.5563e-38 | 2.8589e-38 (±0.19%) | 1.1184 | 0.181 → 0.274 |
| NuWro | 2.3444e-38 | 2.6467e-38 (±0.17%) | 1.1289 | 0.179 → 0.277 |
| MnvTune v1 | | 2.7057e-38 | | 0.281 |

Ratio of each generator's p∥ spectrum to MnvTune v1, by p∥ bin:

| p∥ (GeV/c) | 1.5–2 | 3–3.5 | 5–6 | 7–8 | 8–9 | 9–10 | 10–15 | 15–20 | 20–40 | 40–60 |
|---|---|---|---|---|---|---|---|---|---|---|
| GENIE CV before | 1.062 | 1.070 | 0.970 | 0.794 | 0.620 | 0.317 | 0.138 | 0.090 | 0.039 | 0.002 |
| GENIE CV after | 1.024 | 1.041 | 1.017 | 0.989 | 0.997 | 1.025 | 1.015 | 0.966 | 0.892 | 0.206 |
| GENIE MEC after | 1.038 | 1.068 | 1.071 | 1.037 | 1.060 | 1.065 | 1.066 | 1.007 | 0.915 | 0.317 |
| NuWro after | 1.008 | 0.986 | 0.974 | 0.973 | 0.971 | 0.981 | 0.970 | 0.985 | 0.941 | 0.395 |
| GiBUU (not rebuilt) | 0.829 | 0.895 | 0.858 | 0.835 | 0.828 | 0.819 | 0.630 | 0.323 | 0.000 | 0.000 |

In the highest E_avail bin (> 3 GeV), the ratio to MnvTune moved as follows:
- GENIE CV: 0.511 → 0.977.
- GENIE MEC: 0.513 → 0.979.
- NuWro: 0.572 → 1.044.

**Statistics at high p∥.** The fix reweights events; it does not add any. The receipt gives raw
counts and effective N per p∥ bin. For GENIE CV, the 20–40 GeV/c bin has 997 raw events and an
effective N of 485, for a 4.5% statistical error. The 40–60 bin has 8 events (35%).

## GiBUU (check 5, report only)

- **The flux is PPFX-like.** GiBUU read its own `MINERvA_MEflux.dat`, which has 190 points of equal
  0.5 GeV width. Its shape agrees with phi_t to within 0.7–2.5% below 20 GeV (ratio 1.025 / 1.014 /
  0.987 / 0.993 in the 0–2, 2–5, 5–10 and 10–20 GeV bands). It is not the non-PPFX generation
  flux: the ratio to that flux is 1.19 at 10–20 GeV.
- **The same width defect is absent**, so GiBUU was not rebuilt.
- **But the jobcard cuts the flux.** It sets `Enu_upper_cut = 20.0`. `esample.read_fluxfile`
  (`esample.f90:155`) zeroes the flux above the cut and renormalizes over what remains, and the maximum E_nu in all 80
  `FinalEvents.dat` files is 19.99988 GeV.
- **That cut has two consequences:**
  - GiBUU's normalization is high by the in-cut flux fraction relative to the data convention. That
    fraction is 0.9873 with its own flux shape and 0.9891 with phi_t.
  - About 5.2% of phi_t-averaged σ_CC lies above 20 GeV (GENIE σ shape) and is absent from GiBUU.
- **The GiBUU/MnvTune deficit is not explained by this.** The 0.82–0.91 ratio at p∥ below 10 GeV/c is
  not a flux-sampling defect. Above about 10 GeV/c the deficit is the 20 GeV cut (`KNOWN_ISSUES` 82).

## Limitations

1. **Energies outside the generation range are absent and not patched.** With phi_t and GENIE
   graphs:
   - E > 50 GeV carries 0.44% of σ_CC for GENIE. The graph ends at 50 GeV, so σ above that is
     `TGraph::Eval`'s linear extrapolation.
   - For NuWro (C12 proxy), E > 50 carries 0.44% and E < 0.5 carries 0.011%.
   - This is why the 40–60 GeV/c p∥ bin stays at 0.2–0.4 of MnvTune.
2. **Weights are large in the wide bins.** The in-phase-space effective N is 281,530 of 938,141
   events (GENIE CV), 286,981 of 960,128 (MEC) and 345,893 of 1,261,997 (NuWro). High-p∥ and
   high-E_avail cells rest on few raw events. A regeneration with a correctly sampled PPFX flux and
   no 50 GeV cap (the row-83 remedy) would remove both this limitation and limitation 1.
3. **σ shape is not the generator's own for NuWro and the MEC events.** Check 1 for those
   populations used the GENIE graph σ with a smooth free factor. A sampling defect that were itself
   smooth in log E would not be caught. The width-scaling defect is not smooth; it was rejected at
   chi2 of 5,564–126,044.
4. **phi_t is piecewise constant on the flux bins**, which is the convention of the data integral
   (`Integral(..., "width")`). The MnvTune MC event weights use `Interpolate` within bins
   (`GetFluxCVWeight`); that difference was not evaluated.
5. **The GENIE CV committed 3D is still the Stage-A sample** (gen5d README deviation 1). Its
   repaired/committed ratio (integrated 1.0918) mixes the fix with that sample difference. The
   marginals file also gives the ratio to the pre-fix 5D marginal, which isolates the fix.

## Round 2 (2026-09-27): E_nu > 50 GeV supplements, full predictions, GiBUU flux convention

The machine receipt for this round is `gen5d-fluxfix-2.json`, next to this file. The numbers below
were copied from it; where they differ, the receipt wins.

**Code.** Everything ran from `/pscratch/sd/j/josephrb/s5p-20260926/gen5d_fluxfix/code/`. The
receipt's `code` field records each sha256.
- `gen5d_flux_supplement.py` is new. It imports `gen5d_flux_reweight.py`, which is unchanged.
- `run_gen5d_supplement.sh` is new. It repeats the gevgen/gntpc lines of `run_gevgen.sh` and the
  `params.txt` of `run_nuwro.sh`. It changes only the event count, `-e 50,100`, the flux file, the
  seed and the work directory, plus `Default+CCMEC` for MEC, as `sbatch_gevgen_mec.sh` does.
- `run_gevgen.sh` itself cannot be reused: `setup_genie.sh` hard-sets the flux, and the script
  hard-codes `-e 0,50`.
- The other files are unchanged: the same `setup_genie.sh` (GENIE v2_12_10c, `gxspl_CH.xml.gz`,
  whose splines extend to 400 GeV, and the CH mix), the same `setup_nuwro.sh` (NuWro 21.09.1
  e20:debug, C12), and the gen5d copy of `nuwro_to_flat_5d.C`.
- Nothing ran on Slurm. Each step was a single process on a login node: gevgen took 4 min per
  100k events, NuWro 2 min, and each merge step under 1 min.

**Supplement flux.** `supp/flux_phi_t_50_100.root:flux_numu` has the same 128 bins as
`flux_numu`. Its content is phi_t density × bin width on [50, 100] GeV and 0 elsewhere.
- GENIE and NuWro draw a bin by content, so this samples phi_t exactly.
- Every merge step checks the file bitwise against phi_t × width. The file itself was written
  once, by an earlier version of the script, and is never overwritten.
- phi_t ends at 100 GeV, so E_nu > 100 GeV remains absent.

**Samples.** Each supplement has 100k events:

| sample | seed | CC events | normalising population |
|---|---:|---:|---:|
| GENIE CV | 50001 | 75,433 | 75,433 CC |
| GENIE+MEC | 51001 | 75,286 | 75,060 non-MEC CC |
| NuWro | 52001 | 99,900 | all 100,000 events (no crash at these energies) |

**Size criterion.** Call a p∥ bin *affected* if the supplement's share of the full prediction is at
least 1%; those are 10–15, 15–20, 20–40 and 40–60 GeV/c. In those bins the supplement's statistical
error is at most 1.28% (CV), 1.30% (MEC) and 1.12% (NuWro).

**Normalisation.** The weight is `r = int_50^100 phi_t / Phi_t = 4.8375e-4`, a constant.
- GENIE: `supp = S * N_bin / N_pop` with
  `S = int_50^100 phi_t sigma_CC dE / Phi_t = 1.8417e-40` cm²/nucleon.
- sigma_CC comes from `supp/xsec_graphs_regen_e100.root`, a `gspl2root` of the same splines.
- The same `gspl2root` at `-e 50` reproduces `xsec_graphs.root` bitwise.
- The `-e 100` graph agrees with it to 3.3e-5 above 5 GeV.
- The old graph's linear extrapolation is within 0.35% of the spline up to 100 GeV.
- NuWro: `supp = sum_bin w r / N_total`. NuWro's own `<sigma>` over its 50–100 GeV spectrum gives
  `S = 1.7759e-40`, against 1.8886e-40 from the GENIE C12 graph.
- **Merge:** full = the <50 GeV product plus the supplement; `sumw2` and `nevt` add.
- **Check on the <50 GeV part:** rebuilding it from the per-event weights reproduces its `xsec_flat`
  bitwise, for all three generators.

**Checks.**
- **Sampling model on the supplements: all pass.**

  | population | across-bin | within-bin | alternative reading |
  |---|---|---|---|
  | GENIE CV, CC (strict) | p = 0.999 | p = 0.61 | chi2 7,695/4 |
  | GENIE+MEC, non-MEC CC (strict) | p = 0.017 | p = 0.82 | chi2 7,988/4 |
  | GENIE+MEC, MEC events (226) | p = 0.47 | p = 0.019 | — |
  | NuWro, CC (proxy) | p = 0.21 | p = 0.99 | chi2 951/1 |
  | NuWro, RES/DIS | p = 0.20 | p = 0.98 | — |
  | NuWro, QEL/COH/MEC | p = 0.71 | p = 0.62 | — |

- **Continuity across 50 GeV.** The implied σ/E_ν in cm²/nucleon/GeV:

  | generator | 40–45 (main) | 45–50 (main) | 50–55 (supp) | 55–60 (supp) |
  |---|---|---|---|---|
  | GENIE CV | 6.21e-39 ± 11% | 5.31e-39 ± 15% | 6.64e-39 ± 0.5% | 6.62e-39 ± 0.8% |
  | GENIE+MEC | 6.11e-39 | 5.76e-39 | 6.67e-39 | 6.66e-39 |
  | NuWro | 7.59e-39 ± 8% | 6.67e-39 ± 11% | 6.39e-39 | 6.35e-39 |

  - For GENIE CV, σ divided by the graph expectation is 0.93 / 0.80 (main) against 1.000 / 0.998
    (supplement).
  - The mean muon p∥/E_ν in CC events is 0.49 / 0.39 (main) against 0.52 / 0.52 (supplement).
  - All of these agree within the main sample's errors.
  - **The main sample holds only 84 and 47 GENIE CV events in 40–45 and 45–50 GeV.** That is the
    original defect's under-sampling, which the reweight does not undo.
- **p∥ ratio to MnvTune, 40–60 GeV/c, after the merge:**
  - GENIE CV: 0.206 → 0.790.
  - GENIE+MEC: 0.317 → 0.915.
  - NuWro: 0.395 → 0.978.
  - The 20–40 GeV/c bin goes to 0.986 / 1.009 / 1.030.
- **Integrated σ, full over <50 GeV:**
  - GENIE CV: 1.00605 (2.7646e-38 cm²).
  - GENIE+MEC: 1.00584 (2.8756e-38).
  - NuWro: 1.00608 (2.6628e-38).
  - The fraction with p∥ ≥ 6 GeV/c is 0.275 / 0.278 / 0.281, against 0.281 for MnvTune.

**GiBUU (`gibuu_cv_xsec5d_fluxfix.npz`).**
- **Why the reweight is exact.** In `initNeutrino.f90`, each nucleon draws
  `flux_enu = userFlux()`. That is `eneut`: a content-proportional point, then E uniform within
  ±0.25 GeV, from the flux zeroed above `Enu_upper_cut = 20` and renormalized. Then
  `perweight = sigma/numtry` at that energy, with no flux factor. So the per-event
  `r(E) = (phi_t/Phi_t) / phi_gibuu` (1st/50th/99th percentile 0.83 / 0.99 / 1.22) reweights exactly.
- **Identity:** r ≡ 1 reproduces `gen5d/gibuu_cv_xsec5d.npz` bitwise.
- **Sampling check, revised after seeing the data:**
  - The pre-registered form tested all energies, uniform within points, on counts. It failed only
    through the three points below 1.5 GeV (within-bin chi2/4 = 1086, 104, 24).
  - There, the probability that a draw is kept (it is dropped below `sigmacut` or when Pauli
    blocked) rises through threshold inside a point. That shapes the counts, not the proposal.
  - A second population, in-PS counts, was dropped because acceptance depends on E.
  - Final tests, both passing: counts for E ≥ 1.5 GeV, across p = 0.18 and within p = 0.14; and an
    edge-jump test, in which the count density at each point boundary jumps by the content ratio,
    chi2 43.0/36, p = 0.20.
- **Results:**
  - Integrated σ goes from 2.2227e-38 to 2.2152e-38 (×0.99660).
  - The p∥ ratio to MnvTune after the fix is 0.82–0.90 below 10 GeV/c, 0.620 at 10–15, 0.313 at
    15–20, and 0 above.
- **The part above 20 GeV is still absent:**
  - 5.21% of phi_t-averaged σ_CC (GENIE CH graphs to 100 GeV).
  - In the other generators' full products, E_ν > 20 GeV supplies 6.8–7.4% of the in-grid σ, and
    0.92–1.05% of the p∥ < 6 GeV/c part.

**The v1 receipt was regenerated.** `gen5d-fluxfix.json` was rebuilt through its own producer
(`gen5d_flux_reweight.cmd_receipt`, unchanged) and then rewritten by
`gen5d_flux_supplement.py receipt`, because it contained a placeholder path.
- The two `phi_t` text fields now spell out the three rearranged-universe flux files and the POT
  files as full paths.
- The timestamp, environment, argv and a `regenerated` block also differ.
- No product and no number changed.

**Limitations of round 2.**
1. **The high-p∥ statistics of the full products are limited by the <50 GeV sample, not by the
   supplement.** In 40–60 GeV/c the <50 GeV part is 26% (CV), 35% (MEC) or 40% (NuWro) of the full
   prediction and rests on 8, 12 and 22 raw events. The full-product statistical errors there are
   9.2%, 10.0% and 8.6% (20–40: 4.1%, 4.2%, 3.5%). A 20–50 GeV supplement, or a regeneration, would
   fix this; either needs a merge that replaces the main sample's E ≥ 20 GeV events rather than
   adding to them. That is a design choice for the campaign, not made here.
2. **E_ν > 100 GeV is absent from every product**, as it is from the data flux integral.
3. **The GiBUU sampling test was revised after seeing the data** (above). The GENIE and NuWro
   supplement tests were run as specified before the data were seen.

## Round 3 (2026-09-27): per-mode GENIE E_avail figures on the repaired flux

The machine receipt for this round is `gen5d-fluxfix-3.json`, next to this file. The numbers below
were copied from it; where they differ, the receipt wins.

**What was built.** The code is `3d-unfolding/genie/gen5d_mode_components.py`, which is new. It ran
from `/pscratch/sd/j/josephrb/s5p-20260926/gen5d_fluxfix/code/`, and the receipt's `code` field
records the sha256 of every file used.
- **Outputs** are in `/pscratch/sd/j/josephrb/s5p-20260926/stage7/genfig/3d-unfolding/genie/`:
  - `genie_cv_xsec3d_modes.root` and `genie_mec_cv_xsec3d.root`, which use the committed histogram
    names;
  - the plots `compare_mec_eavail.png` and `mode_decomp_eavail.png`;
  - `*_before.png` for the same scripts on their committed inputs;
  - a `.log` for each run.
- The coordinator's `genie_cv_xsec3d.root` there was not touched. My `hXSec_eavail` is bitwise
  identical to it, as is the MEC file's to `genie_mec_xsec3d.root`.
- **How the histograms are made:**
  - `hXSec3D/2D/pt/pz/eavail` are the `_full` products' marginals, computed with
    `gen5d_to_rootpreds.integrate`.
  - The components `hXSec_eavail_{mec,nomec,qel,res,dis,coh,charm}` are σ-weighted sums over the
    same in-phase-space events: the main sample with its r(E) weights plus the 50–100 GeV supplement.
  - Those sums reproduce `hXSec_eavail` to 4.5e-13.
  - 67 CV events and 87 MEC events belong to none of QE/RES/DIS/COH/MEC. They are other GENIE
    channels, worth 0.04% and 0.19% of σ.
- **Producers:** `compare_mec_eavail.py` and `mode_decomp_eavail.py` were run unchanged, from the
  deploy export of `4e4b4f56` (their sha256 equal the cluster checkout's). Every path was passed
  absolute, because both scripts resolve relative paths against their own directory.
- **The mode-decomposition wrapper** replaces `mode_decomp_eavail.mode_counts` with a σ-weighted
  version and runs the script's own `main()`. The script shares dσ_CV[b] among modes by
  N_mode[b]/N_tot[b]; with unequal per-event weights, the exact analogue is W_mode[b]/W_tot[b].
  Weights are scaled to mean 1, so the script's `np.maximum(tot, 1)` has no effect: the smallest
  bin total is 54,825.

**What the scripts print (catch bin dropped).**

| quantity | before (committed inputs) | after (repaired) |
|---|---|---|
| CV deficit | −7.2% | −7.2% |
| CV+MEC deficit | −5.2% | −2.6% |
| "MEC added … of the integrated deficit" | 27% | 63% |
| "in the dip MEC fills … of the data−CV gap" | 46% | 52% |
| 2p2h needed, as a fraction of the QE rate | 44% | 45% |
| share of the positive deficit at E_avail ≤ 0.4 GeV | 57% | 70% |

**Reading the "before" column.** It is not a like-for-like comparison. Its CV file is the Stage-A
sample (gen5d README deviation 1). The non-MEC part of the MEC file is only 0.9714 of it, a
normalization offset that is not the MEC component.
- The script's "MEC added" is the MEC file minus the CV file, so it absorbs that offset.
- Measured with the MEC-only histogram, MEC covers 64% of the integrated deficit before the fix
  and 63% after.
- Measured the same way, the dip fill is 62% before and 53% after.
- After the fix, the non-MEC part equals the CV to 1.0001, so the script's difference is the MEC
  component.
- The MEC-only integral itself changes by −1.3%, from 1.113e-39 to 1.099e-39.

**Limitations of round 3.**
1. The CV deficit is −7.2% both before and after, but on different samples: the Stage-A file
   before, and the repaired seed sample after. The equality is a numerical coincidence of their
   normalizations, not a sign that the fix leaves the CV unchanged. That is inferred from the
   Stage-A/seed-sample normalization difference (0.9714), not tested.
2. The high-E_avail statistics are limited by the <50 GeV sample, as in round 2.
