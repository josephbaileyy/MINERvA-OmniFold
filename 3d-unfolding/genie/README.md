# GENIE truth-generation for 3D model comparison

Generate truth-level neutrino-interaction events and histogram them into
`d³σ/(dpT dp‖ dEavail)` on the analysis binning, for overlay on the unfolded
OmniFold result (`../xsec_3d_MEFHC_5iter_lgbm.root`). No detector simulation:
the unfolded result is already detector-corrected, so model comparison is a
truth-level operation.

Generator-agnostic by design — `gst_reader.py` defines a common event schema;
adding NuWro/NEUT/GiBUU is one reader each.

## Environment (the tricky part, solved)

GENIE is on CVMFS (`genie v2_12_10c` + `genie_xsec v2_12_10`, splines
pre-built) but built for SL7 (glibc 2.17); Perlmutter is SLES15 (glibc 2.38).
`setup_genie.sh`:
- scrubs the analysis conda ROOT (it clashes with GENIE's UPS ROOT);
- forces the SL7 flavor with `ups setup -H Linux64bit+3.10-2.17` (glibc
  forward-compat runs the binaries);
- shims **only** the 4 missing OS libs (`libpcreposix`, `libpcre`,
  `libssl.so.10`, `libcrypto.so.10`) from the MINERvA SL6 container into
  `$HOME/.genie_compatlibs` — never the container's libc.

No container runtime needed (shifter/podman exist but aren't used). Verified:
`gevgen` generates events end-to-end this way.

## Inputs (pinned in setup_genie.sh)
- Tune (base CV): `DefaultPlusValenciaMEC` — this is **MINERvA Tune v1 before the
  MINERvA reweights** (Stage B adds those).
- Splines: `…/genie_xsec/v2_12_10/NULL/DefaultPlusValenciaMEC/data/gxspl-FNALbig.xml.gz`.
- Flux: MINERvA ME FHC νμ `flux_E_unweighted` from `CentralizedFluxAndReweightFiles`.
- Target: CH (C12 0.9225 / H1 0.0775 by mass); per-nucleon = /13.

## Files
- `setup_genie.sh` — sourceable env setup (above).
- `run_gevgen.sh N SEED TAG` — gevgen (νμ-CH, flux, splines) → `gntpc -f gst`
  → `work_<TAG>/genie_mefhc_<TAG>.gst.root`.
- `sbatch_gevgen_mefhc.sh` — SLURM wrapper for a high-statistics run.
- `gst_reader.py` — generator-agnostic reader (GENIE gst → common schema).
- `genie_to_xsec3d.py` — events → d³σ: muon (pT,p‖); truth Eavail (replicates
  `CVUniverse::GetEAvailableTrue()`); truth phase space; `--norm splines`
  (absolute, splines⊗flux ÷13) or `--norm shape`. Writes `hXSec3D`,
  Eavail-marginal `hXSec2D`, `hXSec_pt/pz/eavail`.
- `overlay_generators.py` — overlay generator(s) on the unfolded result (3 axes).
- `overlay_generators_band.py` — same overlay WITH the full uncertainty band and a
  covariance χ². Reads the completed 3D UQ covariance
  (`uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root`,
  `hCov_combined3d_total` = C_syst+C_stat+C_ML), projects it onto each 1D axis via
  the exact `project_axis` linear operator (J C Jᵀ; a machine-precision self-check
  asserts J·cv == the stored `hXSec_<axis>`), draws the total band, and reports
  `chi2_cov/ndf` per axis (+ stat-only lower bound if `--band` given). Writes
  `generators_vs_unfolded_band.png`.
- `compare_3d_fullcov.py` — rigorous full-3D goodness-of-fit: data vs each
  generator on all 1431 reported bins with `hCov_combined3d_total`, via a
  TRUNCATED-SPECTRAL χ² (keep eigenmodes λ>tol·λmax; never raw-pinv a
  rank-deficient cov — see the script header). Reports χ²/ndf over a truncation
  sweep, the diagonal-only χ² (robust reference), the captured ||r||² fraction,
  and a spectrum + GoF-vs-truncation plot `compare_3d_fullcov.png`.
- `run_fsi_reweight.sh GHEP [DIAL NTWK MIN MAX OUT NEV]` — GENIE single-param
  reweight (`grwght1p`) on a GHEP file for one GSyst dial (default `FrInel_pi`),
  scanning `NTWK` tweak values in `[MIN,MAX]` σ. Output TTree `<DIAL>` with
  `eventnum`/`weights[NTWK]`/`twkdials[NTWK]`; `eventnum == gst iev`.
- `run_parallel_fsi.sh [DIAL NTWK MIN MAX]` — fan `grwght1p` across the 8 CV
  shards (`work_p1..8/gntp.*.ghep.root`) → `work_p<i>/weights_<DIAL>.root`.
- `fsi_variation_xsec3d.py` — apply the per-event weights to the CV gst events
  and rebuild d³σ at each dial value. FSI conserves the total CC σ, so each dial
  is normalised by its own weighted CC sum (sigma_nuc × w_bin/w_allCC) → the
  dial=0 column reproduces CV exactly (built-in closure); off-CV columns are the
  ±Nσ variations. Writes `hXSec3D/2D/_pt/_pz/_eavail_d{k}` (+ `_cv/_lo/_hi`
  aliases, `twkdials`) and a `_summary.txt` with the per-Eavail-bin shift table.

## Run
```bash
# generate (interactive; ~minutes for a few hundred k events) or via sbatch
bash run_gevgen.sh 2000000 1 cv

# events -> d3sigma  (analysis env; setup_genie.sh exports GENIE_FLUX/_HIST)
source ../../setup_salloc_env.sh
python genie_to_xsec3d.py --gst work_cv/genie_mefhc_cv.gst.root \
    --out genie_cv_xsec3d.root --norm splines \
    --flux "$GENIE_FLUX" --flux-hist "$GENIE_FLUX_HIST"

# overlay on the unfolded 3D result
python overlay_generators.py --unfolded ../xsec_3d_MEFHC_5iter_lgbm.root \
    --generator GENIE-CV:genie_cv_xsec3d.root --out genie_vs_unfolded

# --- FSI dial variation (FrInel_pi etc.): reweight the SAME CV events ---
bash run_parallel_fsi.sh FrInel_pi 3 -1 1        # -> work_p*/weights_FrInel_pi.root
source ../../setup_salloc_env.sh
python fsi_variation_xsec3d.py --shards 'work_p*' --dial FrInel_pi \
    --flux flux_mefhc_numu.root --flux-hist flux_numu \
    --out genie_fsi_FrInel_pi_xsec3d.root      # + _summary.txt (Eavail shifts)
```
(`genie_to_xsec3d.py` needs `$GENIE_SPLINES` set for the splines normalisation —
source `setup_genie.sh` once to export it, or pass `--graphs`.)

## Status / stages
- **Stage 0 + A: DONE** (2026-05-31). 2M base-GENIE-CV events (8 parallel
  gevgen × 250k, ~9 min on a 256-core node, hadd'd); analyzer → `genie_cv_xsec3d.root`;
  overlay → `genie_vs_unfolded.png`. Result: 1.48M CC events, 938k in phase
  space; flux-averaged ⟨σCC⟩/nucleon = 3.98e-38 cm² (physical); total-in-PS
  2.52e-38 vs unfolded 3.08e-38. **GENIE 2.12 CV tracks the data shape on all
  three axes (pT, p‖, Eavail) but runs ~10-18 % low in normalisation** — the
  expected base-CV behaviour before the MINERvA Tune v1 reweights (Stage B).
- **Stage B: DONE** (2026-05-31), via the robust route: instead of
  reimplementing the MINERvA tune reweights on gevgen events, extract the tuned
  prediction directly from the analysis MC — `mc_truth_denom`'s `w_truth` already
  carries the full Tune v1 (RPA + 2p2h + non-res-π; mean 0.83). `model_tune_xsec3d.py`
  bins it and normalises with the unfold's flux/POT/nucleon machinery (c=1, no
  efficiency correction) → `model_tunev1_xsec3d.root`. **Validated**: reproduces
  the shipped `model_ptpl…Tune_v1.txt` to 0.01 % in normalisation (σ/data 0.9125
  vs 0.9124); χ²(ours vs shipped)/ndf = 1.57 (MC-stat-limited). Three-way overlay
  `genie_tunes_vs_unfolded.png`: on (pT, p‖) the tune barely moves GENIE
  (both ~10 % low); on **Eavail** the tune acts at low recoil (RPA suppresses the
  QE peak) yet still underpredicts the data at the lowest Eavail — model
  discrimination the 3D axis enables. (`model_tune_xsec3d.py`.)
- **NuWro 21.09: DONE** (2026-05-31) — first genuinely independent generator
  (not a GENIE tune). From CVMFS (`nuwro v21_09_1`), same UPS `-H` SL7 trick +
  compat shim (+ `libxxhash` from conda). Three NuWro-specific gotchas, all
  solved (see `setup_nuwro.sh`): (i) use the **e20:debug** build — the prof
  build segfaults inside the flux-driven test-event phase on this platform;
  (ii) invoke via a local `nuwro_home_dbg/{bin,data}` symlink dir because NuWro
  derives `data_dir = <bin>/../data` which the UPS layout breaks; (iii) flux
  histogram x-axis in **GeV**, range-restricted to [0.5,50] GeV
  (`flux_mefhc_numu_nuwro.root`) to avoid an edge crash. Target C12 (~92 % of CH
  by nucleons; documented approximation). Files: `setup_nuwro.sh`,
  `run_nuwro.sh`, `run_parallel_nuwro.sh`, `nuwro_to_flat.C` (event-class →
  flat obs, run in NuWro's ROOT), `nuwro_to_xsec3d.py` (conda; weight =
  flux-avg σCC/nucleon). 2M events (8×250k parallel, ~5 min); flux-avg
  ⟨σCC⟩/nucleon = 3.72e-38; total-in-PS 2.34e-38 (lowest of the models:
  NuWro 2.34 < GENIE CV 2.52 < Tune v1 2.71 < data 3.08).
- **Four-way overlay** `generators_vs_unfolded.png` (GENIE CV + Tune v1 + NuWro
  + unfolded data): all three track the (pT, p‖) shape; on **Eavail** both NuWro
  and Tune v1 suppress the low-recoil QE peak below GENIE CV (RPA/nuclear
  effects), and the data sits above all three at lowest Eavail.
- **Systematic band added 2026-06-02** (`generators_vs_unfolded_band.png`, via
  `overlay_generators_band.py`): the 3D UQ campaign covariance projected onto each
  axis gives a ~6%/bin total band (≫ the 0.2–0.3% stat band it replaces). With
  the honest covariance the data–model tension drops by ~2–3 orders of magnitude
  vs stat-only but stays significant: integrated Eavail rate (catch bin dropped)
  data 2.42e-38 ± 1.3e-39 vs GENIE-CV −7.2% (1.3σ), Tune-v1 −9.5% (1.8σ), NuWro
  −15.3% (2.9σ). Per-axis cov χ²/ndf is still ≫1 (shape tension beyond
  normalization), Tune-v1 the closest on pT/pz, all three comparable on Eavail.
- **Full-3D goodness-of-fit (2026-06-02, `compare_3d_fullcov.py`):** data vs
  generator χ² on all 1431 reported bins with the combined covariance (hard rank
  247; tol=1e-10 keeps exactly the non-null modes). All three generators are
  **excluded, p≈0**. Tune-v1 is dramatically the best; GENIE-CV and NuWro are
  comparably poor:
    - diagonal-only χ²/ndf (robust, no correlations): Tune-v1 **4.8**, GENIE-CV
      **34**, NuWro **36**.
    - well-determined-modes χ²/ndf (tol=1e-6, 160 modes): Tune-v1 77, GENIE-CV
      300, NuWro 345; full rank-247 amplifies via off-diagonal structure
      (Tune-v1 131, GENIE-CV 1512, NuWro 1287). Residual is 98–99.9% inside the
      constrained subspace (not a null-space artifact). Consistent with the
      per-axis projected χ² and the integrated-Eavail offsets (−7 to −15%).
  This is gated on the stat-block resolution (see `../2d-unfolding/`): our
  bootstrap stat block is genuinely smaller than the paper's (OmniFold
  efficiency, confirmed by the data/MC split), so using our own combined
  covariance for the ours-only χ² is the internally-correct choice.
- **FSI dials don't explain the low-Eavail excess (2026-06-03).** Both pion-FSI
  knobs are sub-percent on dσ/dEavail: `FrInel_pi` ≤0.74% (peak in 0.10–0.20 GeV),
  `FrAbs_pi` ≤0.82% (peak in the lowest [0,0.10] GeV bin), total in-PS σ shift
  ±0.02–0.03% at ±1σ. A <1% knob cannot bridge the 7–15% data excess at low
  recoil, so the excess is **not** pion FSI — it points to the initial-state /
  nuclear model (2p2h/MEC, RPA), the high-leverage low-recoil physics (2p2h is
  the 2nd-largest band in the 3D syst budget). Files: `genie_fsi_FrInel_pi_xsec3d.root`,
  `genie_fsi_FrAbs_pi_xsec3d.root` (+ `_summary.txt`).
- **GiBUU 2019 added (2026-06-03).** Runs **natively** on Perlmutter (no
  container) off the NOvA CVMFS build
  (`/cvmfs/nova.opensciencegrid.org/externals/gibuu/v2019`); five sequential
  blockers cleared and documented in `setup_gibuu.sh`: (i) ROOT libs from the
  conda `root_6_28/lib`; (ii) `libgfortran.so.3` from gcc `v6_3_0` lib64; (iii)
  put the conda lib **before** the gcc lib on `LD_LIBRARY_PATH` so the newer
  `libstdc++` wins the `GLIBCXX` clash; (iv) a writable `buuinput_local/` mirror
  (read-only CVMFS can't be opened) that **keeps the `.bz2`** sentinels
  (`input.f90:446` dir-existence check) alongside the decompressed `.dat`; (v) a
  short symlink `/pscratch/sd/j/josephrb/gbi` to dodge GiBUU's fixed-length
  Fortran filename truncation (~93 chars). Jobcard `work_gibuu/gibuu_mefhc_numu.job`
  (CC νμ on C12, all channels, numEnsembles=4000, num_runs_SameEnergy=1, MINERvA
  ME flux). Generation: 80-task array (`sbatch_gibuu_mefhc.sh`, shared QOS),
  unique seed per task → `work_gibuu_arr/task*/FinalEvents.dat` (~1.9M events,
  914k in-PS combined). `gibuu_to_xsec3d.py` parses FinalEvents.dat (muon = ID
  902 cols 9–12; FS hadrons = perweight≠0 non-lepton; Eavail = proton KE + π± E−mπ
  + π0/γ E to match `GetEAvailableTrue()`). **Normalization:** GiBUU bakes
  1/numEnsembles into `perweight`, so each run's Σperweight is already a full σ
  estimate; combining M independent runs just averages → divide by **number of
  files**, not numEnsembles. flux-avg ⟨σCC⟩/nucleon = 3.61e-38; total-in-PS
  2.22e-38 (lowest model overall). Output `gibuu_cv_xsec3d.root`.
- **Four-generator results (2026-06-03, band + full-cov rerun with GiBUU):**
  integrated Eavail rate (catch bin dropped) data 2.42e-38 ± 1.3e-39 vs GENIE-CV
  −7.2% (1.3σ), Tune-v1 −9.5% (1.8σ), NuWro −15.3% (2.9σ), **GiBUU −21.9%
  (4.1σ)** — GiBUU is the most normalization-deficient. Full-3D truncated χ²:
  diagonal χ²/ndf GiBUU **32.4** (comparable to GENIE-CV 34, NuWro 36; Tune-v1
  best at 4.8), but the truncated-spectral metric is **worst** for GiBUU because
  23.5% of its residual sits **outside** the rank-247 constrained subspace (its
  3D shape differs in directions the covariance barely constrains) on top of the
  large normalization offset. Plots: `generators_vs_unfolded_band.png`,
  `compare_3d_fullcov.png`.
- **2p2h is the right shape AND size for the low-Eavail excess (2026-06-03,
  `mode_decomp_eavail.py`).** This base GENIE CV was generated with **no MEC**
  (`mec==0` for all 1.48M CC events; modes are QE 11%, RES 22%, DIS 66%, COH
  0.9%), so 2p2h would be *added*, not reweighted. Decomposing the committed CV
  dσ/dEavail by mode (exact: per-bin mode count-fractions × the CV bin value)
  and overlaying the unfolded data localises the excess: bin [0.10,0.20) is
  **+3.9σ**, [0.20,0.40) **+2.3σ**, while the QE-dominated [0,0.10) already
  matches (+0.8σ) and [0.40,1.50) match to ±0.4σ. **57% of the deficit sits at
  Eavail ≤ 0.4 GeV — the QE-Δ dip where 2p2h lives.** Closing the integrated
  −7.2% deficit needs a 2p2h ≈ **43% of the QE rate** (62% locally in the dip) —
  the standard empirical/Valencia-MEC magnitude, vs the **sub-percent** pion-FSI
  dials. The one excess 2p2h can't explain is bin [1.50,3.00) (+2.2σ, high-Eavail
  DIS tail → separate DIS-modeling issue). Plot `mode_decomp_eavail.png` (stacked
  by mode + data + the 2p2h-shaped gap).
- **CONFIRMED: enabling Valencia 2p2h fills ~half the dip (2026-06-03).**
  Regenerated the GENIE CV with the empirical 2p2h on
  (`--event-generator-list Default+CCMEC`, via the new `GEVGEN_LIST` hook in
  `run_gevgen.sh`; `sbatch_gevgen_mec.sh` = 2M events, 8×250k). The base spline's
  Nieves-Simo-Vacas MEC channel is present and nonzero, but **absent from the
  gspl2root `tot_cc` graph** (`mec_cc`==0), so the new `genie_mec_to_xsec3d.py`
  normalises by the **non-MEC CC count** (anchors QE+RES+DIS+COH to the known
  `tot_cc`, lets MEC add on top by 1/(1−f_mec); f_mec=2.87%). Result
  (`genie_mec_cv_xsec3d.root`, `compare_mec_eavail.py`): MEC sits in the QE-Δ
  dip and moves GENIE toward the data — bin [0,0.10) now lands on data
  (+0.8σ→−0.04σ), [0.10,0.20) +3.9σ→+2.85σ, [0.20,0.40) +2.3σ→+1.0σ. **MEC fills
  46% of the data−CV gap in the dip (Eavail≤0.4) and 27% of the integrated
  deficit** (CV −7.2% → CV+MEC −5.2%). Full-3D truncated χ²/ndf **1512 → 1145
  (−24%)** (`compare_3d_fullcov_mec.png`) — a real improvement, but still ≫
  Tune-v1 (131), since Tune-v1 layers MINERvA's empirical low-recoil 2p2h
  enhancement + RPA on top of stock Valencia MEC. The high-Eavail [1.5,3.0)
  excess is untouched (no MEC there — a DIS-tail issue). Plot
  `compare_mec_eavail.png`. (`xsec_graphs.root` for the normalisation is a
  gspl2root product of `gxspl_CH.xml.gz`; regenerate with
  `gspl2root -f $GENIE_SPLINES -p 14 -t 1000060120 -o xsec_graphs.root -e 50`
  then again for `-t 1000010010`.)
- Remaining generator: NEUT (not openly available; +1 reader/converter if a
  build becomes accessible).
