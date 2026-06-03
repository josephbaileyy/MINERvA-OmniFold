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
- Remaining generators: NEUT (not openly available) / GiBUU (on NOvA CVMFS,
  `/cvmfs/nova.opensciencegrid.org/externals/gibuu/v2019`; +1 reader/converter).
