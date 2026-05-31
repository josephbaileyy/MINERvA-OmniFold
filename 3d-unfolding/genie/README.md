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
- Remaining generators: NEUT / GiBUU (+1 reader/converter each).
