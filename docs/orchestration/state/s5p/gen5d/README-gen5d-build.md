# gen5d build: truth-level 5D generator predictions (s5p, 2026-09-26)

**Status: built and validated on Perlmutter. Uncommitted, so not yet quotable.** The machine receipt
is `gen5d-build.json`, which sits next to this file. It was generated on the cluster from the
products' own meta files; no numbers were hand-transcribed into it.

## What was built

The quantity is `d^5 sigma/(dpT dp|| dEavail dq3 dW)` in cm^2/nucleon/(GeV/c)^2/GeV^3. It is
computed on the scalar-5D fine grid in C order (pt 14, pz 16, eavail 7, q3 7, W 6), which gives
**65856 cells**. The edges are asserted equal to `u3d.PT/PZ/EAVAIL_EDGES` and
`gen_to_xsec_eavailW.py:40-41`. The q3 edges match `nd-unfolding/unfold_nd_omnifold_unbinned.py:106`.

**Outputs.** Each generator has an `<gen>_xsec5d.npz` under `/pscratch/sd/j/josephrb/s5p-20260926/gen5d/`.
- **Arrays:** `xsec_flat`, `sumw2_flat` (finite-sample variance of `xsec_flat`, in density units),
  `nevt_flat` (raw event count per cell), `n_events` and `edges_*`.
- **Metadata:** `meta_json` is stored inside the npz, and a sidecar `<gen>_xsec5d.meta.json` holds the
  same content. It records every input with its sha256, the definitions, the normalisation constants,
  range accounting, diagnostics, validation, and the sha256 of every code file.

The four products are listed below. The npz sha256 values are in `gen5d-build.json`.

| file | generator | events in grid |
|---|---|---:|
| `genie_cv_xsec5d.npz` | GENIE 2.12.10 CV (no MEC), `genie_mefhc_cv_ALL.gst.root` | 938,141 |
| `genie_mec_xsec5d.npz` | GENIE 2.12.10 + Valencia MEC, `genie_mefhc_mec_ALL.gst.root` | 960,128 |
| `nuwro_cv_xsec5d.npz` | NuWro 21.09, `nuwro_flat5d/nuwro_flat5d_p{1..8}.root` | 1,261,997 |
| `gibuu_cv_xsec5d.npz` | GiBUU 2019, `work_gibuu_arr/task*/FinalEvents.dat` (80 files) | 910,378 |

**New code.** Two new files were written, and nothing tracked was edited.
- `3d-unfolding/genie/gen_to_xsec5d.py`, sha256 `1608acd5…`.
  - It imports the existing converters' functions: `eavail_true`, `flux_avg_sigma_cc_per_nucleon`,
    `w_true`, `in_truth_phase_space` and `read_gst`.
  - Where the existing converters compute inline, it restates them statement by statement.
- `3d-unfolding/genie/nuwro_to_flat_5d.C`, sha256 `01e89fb2…`.
  - It is `nuwro_to_flat.C` plus the branches `Enu`, `Q2`, `q0`, `q3`, `dyn` and `hitnuc`.

**How it ran.** The job ran from a `git archive` export of `81d94a95` placed at
`gen5d/code/tree`. All 12 imported files are sha256-identical to `deploy/18337b8c` and to the
canonical cluster checkout.

## Definitions (file:line)

- **E_avail:** `CVUniverse::GetEAvailableTrue`, `MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h:361-374`.
  - The rule is: gamma adds E, pi+- adds E-135 MeV, pi0 adds E, and p adds E-938.27 MeV.
  - The converters implement it at `genie_to_xsec3d.py:42-57`, `nuwro_to_flat.C` (loop) and
    `gibuu_to_xsec3d.py:108-116`.
  - For GENIE, the 5D build computes it in an RDataFrame C++ Define. A 20,000-event parity check
    through the existing `read_gst` + `eavail_true` + `w_true` path gave **0 mismatches** (bitwise).
- **q3:** PlotUtils `Getq3True` is `calcq3(GetQ2True(), GetEnuTrue(), GetElepTrue())`.
  - Sources: `MAT-MINERvA/calculators/TruthFunctions.h:37-47` (cluster `MINERvA101/`, git
    `50d7631`, sha `e6df3503…`) and `MAT/PlotUtils/BaseUniverse.cxx:77-83` (git `35097b6`).
  - Formula: `q3 = sqrt(mc_Q2 + (Enu-Elep)^2)`.
  - **Measured:** in a MasterAnaDev tuple (Playlist1A run 110000, 14,858 true CC numu), `mc_Q2`
    equals the lab-frame `-(k-k')^2` from `mc_incomingPartVec` and `mc_primFSLepton`.
    - The maximum relative difference is `2.2e-10`, and this holds for every `mc_intType`, 2p2h included.
    - The output is `gen5d/_probe_mad_q2.out`.
  - Each generator therefore uses `Q2 = -(k-k')^2`, built from its own lab-frame neutrino and muon.
  - For GENIE, this equals the gst `Q2` branch with a max difference of **0.0**.
- **W:** the build keeps the existing converters' `w_true`, `gen_to_xsec_eavailW.py:49-61`.
  - This is the same code as `gibuu_to_xsec_eavailW.py:87-93` and `nuwro_to_flat.C`.
  - Formula: `W^2 = M_n^2 + 2 M_n (Enu-Emu) - 4 Enu Emu sin^2(theta/2)`, with `M_n = 0.939565`,
    and W is set to 0 when `W^2 <= 0`.
  - This is `CVUniverse::GetTrueExperimentersW` (`CVUniverse.h:385-410`) with one difference.
    CVUniverse uses the **struck-nucleon** mass (`M_n`/`M_p`/average, `:39-41`, `:95-97`) and
    returns NaN when `W^2 < 0`.
  - The measured effect of that difference on in-PS events is below.

    | generator | W-bin changes | NaN under CVUniverse |
    |---|---|---:|
    | GENIE CV | 1,438 / 938,141 | 29 |
    | GENIE MEC | 1,449 / 960,128 | 37 |
    | NuWro | 1,757 / 1,261,997 | 37 |
    | GiBUU | not evaluable (no struck-nucleon id) | – |

  - The existing convention was kept deliberately. Switching it would break exact agreement with
    the committed `(E_avail,W)` predictions.
- **Phase space:** `unfold_2d_omnifold_unbinned.py:48-64`. It requires CC, pT in [0,4.5] and p|| in
  [1.5,60] GeV/c (both inclusive), and `atan2(pT,p||) < 20 deg`.
  - GENIE uses `math.atan2` per event, as its converters do.
  - NuWro and GiBUU use the vectorised form of their converters (`nuwro_to_xsec3d.py:59-61`,
    `gibuu_to_xsec3d.py:130-132`).
- **Normalisation:** each generator uses its own converter's arithmetic.
  - GENIE CV: `sigma_totcc(C12+H1)/13` from `xsec_graphs.root` ⊗ `flux_mefhc_numu.root:flux_numu`
    = `3.86755e-38`, times `N_bin/N_cc`, where `N_cc = 1,484,189`
    (`genie_to_xsec3d.py:145`, `gen_to_xsec_eavailW.py:110`).
  - GENIE MEC: the same sigma divided by `N_nonMEC = 1,452,626` (`genie_mec_to_xsec3d.py:102`).
  - NuWro: `sum(weight)/N_total`, with `N_total = 2,000,000` (`nuwro_to_xsec3d.py:71`).
  - GiBUU: `sum(perweight)/M x 1e-38`, with `M = 80` (`gibuu_to_xsec3d.py:139`).
  - `sumw2_flat` is `sum(w_i^2)/dV^2`, with the normalisation constants treated as exact.

## Validation

For each generator, the build recomputes the existing 3D and (E_avail,W) arrays from the same event
arrays, using the existing expressions. It then compares them, and the 5D marginals, against the
committed ROOT files: `{genie_cv,genie_mec_cv,nuwro_cv,gibuu_cv}_xsec3d.root:hXSec3D` and
`{genie_cv,genie_mec,nuwro_cv,gibuu_cv}_xsec_eavailW.root:hXSec_eavailW`.

| generator | recomputed 3D | recomputed (Ea,W) | 5D marginal vs 3D, max rel | 5D marginal vs (Ea,W), max rel |
|---|---|---|---|---|
| GENIE CV | **different sample** | bitwise | 5.0e-16 vs own 3D; committed 3D is Stage-A (see below) | 1.3e-15 |
| GENIE MEC | bitwise | bitwise | 5.4e-16 | **2.96e-2** as committed; 1.4e-15 after `x N_nonMEC/N_cc` |
| NuWro | bitwise | bitwise | 1.9e-13 | 1.7e-12 |
| GiBUU | bitwise | bitwise | 5.2e-15 | 1.3e-14 |

**Range accounting.** No in-PS event has a non-finite value or falls outside the grid on q3 or W, for
any generator.
- q3 lies in [0.011, 47.5] GeV, and there are no q3 sentinels (NuWro `-9999` count is 0).
- NuWro W sentinels: 0.
- GiBUU has **3,481 in-PS events with E_avail < 0** (min -0.056 GeV, from nucleon energies below the
  proton mass). They are dropped by the committed 3D/(Ea,W) histograms and by the 5D alike, which
  gives 913,859 in PS and 910,378 in the grid.

**Integrated sigma in the 5D grid** (cm^2/nucleon; stat rel. error in parentheses):

| generator | 5D grid | ledger row | ledger integrated sigma | 5D/ledger |
|---|---|---|---|---|
| GENIE CV | 2.444640e-38 (0.10%) | VL35 | 2.4446e-38 | 1.00002 |
| GENIE MEC | 2.556298e-38 (0.10%) | VL36 | 2.4829e-38 | 1.02956 (0.99999 after `x0.971285`) |
| NuWro | 2.344398e-38 (0.09%) | VL37 | 2.3444e-38 | 1.00000 |
| GiBUU | 2.222721e-38 (0.51%) | VL38 | 2.2227e-38 | 1.00001 |

## Deviations and uncertainties that are not closed

1. **GENIE-CV 3D is a different production.**
   - The committed `genie_cv_xsec3d.root` has `nCCtotal = 1,484,896` and a total of `2.516697e-38`.
     It is the Stage-A `work_p*` gevgen (seeds 11-18), whose gst files **no longer exist on disk**;
     a search of `/pscratch/sd/j/josephrb` to depth 7 found none.
   - The only surviving GENIE-CV events are `work_seed*` (the band sample), so the 5D is built from
     them. It matches VL35 and the committed (Ea,W) exactly.
   - Against Stage-A 3D the 5D total is `0.97137x`. After scaling Stage-A to the same total, the
     shape-only chi2 is **1287.8/1273** (approximate, equal-statistics errors;
     `_genie_cv_stageA_shape.out`), so the two agree in shape.
   - The README records Stage-A <sigma_CC>/nucleon as 3.98e-38; the current `xsec_graphs.root`
     (dated 2026-06-03, after Stage-A) gives 3.8676e-38.
   - The normalisation difference is therefore not reconciled here, and no mechanism is claimed.
2. **GENIE+MEC: the two committed predictions disagree on normalisation** by exactly
   `N_nonMEC/N_cc = 0.9712852`. The (Ea,W) band ran `gen_to_xsec_eavailW.py`, which divides by all CC.
   - `xsec_flat` uses the 3D (`genie_mec_to_xsec3d.py`) convention, which is the one `sec_3d` describes.
   - `meta.normalisation.factor_to_eavailW_band_convention` converts to the band convention.
   - This confirms the lead in `state/s5c/deliv/R21-fix-plan.md` "Adjacent leads". The VL36 ratio
     1.579 and `genie_mec_xsec_eavailW.root` are affected; they were not touched.
3. **W nucleon mass.** The build uses the converter convention (`M_n`), not the CVUniverse
   struck-nucleon mass; the size of the difference is in Definitions above.
4. **GiBUU flux cap (observed, not investigated).**
   - In-PS p|| reaches only 19.90 GeV/c, and `task1` has max Enu 19.97 GeV, even though the jobcard's
     `MINERvA_MEflux.dat` extends to 94.75 GeV.
   - The GiBUU 5D, like its committed 3D, is therefore empty above ~20 GeV/c in p||.

## Compute and scratch

- All work ran single-core on login nodes; nothing was submitted to Slurm.
- The NuWro re-flatten took about 30-60 s per file in the NuWro UPS env, 8 files in all.
- Each 5D build took 15-140 s.
- The scratch probes are `gen5d/_probe_mad_q2.py/.out`, `_genie_cv_stageA_shape.py/.out`,
  `_summarize.py`, `_make_receipt.py`, `_dump_existing.py` and `_probe_branches.py`.
- **Not done:** regenerating the Stage-A GENIE-CV sample to reproduce the committed 3D bitwise.
  - That needs batch compute: 8 x `run_gevgen.sh 250000 <11..18> p<i>` + hadd, roughly 8 cores for
    about 10 min, a few GB of memory, and around 1.5 GB of output.
  - Even then it would be bitwise only if the flux, spline and `xsec_graphs.root` inputs of
    2026-05-30 were unchanged, and `xsec_graphs.root` is newer.
