# 3D OmniFold (Eavail) run log

Append-only chronology of Workstream C — the available-energy 3D extension of
the 2D unbinned OmniFold measurement. Newest entries at the bottom of each
dated section. For headline numbers and current state see
`3D_OMNIFOLD_STATUS.md`; for orientation + how-to-run see `README.md`; for
durable workflow invariants (shared with 2D) see
`../2d-unfolding/2D_OMNIFOLD_REFERENCE.md` (§ "3D OmniFold extension").

---

## 2026-05-29 — C1: Eavail branches in the event loop

Added the third axis to `runEventLoopOmniFold.cpp`. Truth
`MC_eavail = GetEAvailableTrue()/1000` (GeV; arXiv:2312.16631 Eq. 4 — Σ proton
KE + Σ π± KE + Σ π⁰/γ total E, excludes n/μ); reco `sim_eavail` /
`sim_background_eavail` / `measured_eavail` = `NewEavail()/1000` (tracker+ECAL
×1.17). Both accessors added **standalone** to `event/CVUniverse.h` rather than
via `#include` of the MAT calculators, because `LowRecoilPionFunctions.h`
redefines `GetVertex()` (conflict at `CVUniverse.h:116`). Branch availability
verified in the MasterAnaDev tuples (`blob_recoil_E_*`, `muon_fuzz_*`,
`mc_FSPart*` present in BOTH MC and data; the spline `recoilE_SplineCorrected`
is absent — confirming `NewEavail` as the correct reco estimator). Build +
single-file smoke passed (truth med 0.95 GeV, reco 0.66 GeV, no NaN, misses
−9999). Committed `8ca52cc`.

## 2026-05-30 — C1: 12-playlist re-run + hadd

`sbatch_evloop_array_3d.sh` (SLURM 53601666, array 1-12, shared QOS,
non-destructive → `runEventLoopOmniFold_3D_{1A..1P}.root`). All 12 COMPLETED,
no log errors; `hadd` → `runEventLoopOmniFold_MEFHC_3D.root` (2.8 GB).
Full-stats Eavail sanity: truth mean 1.93 GeV (0→92 GeV DIS tail), matched reco
1.15 GeV, data 1.54 GeV; `sim_eavail`=−9999 for the 12.35M/32.85M truth-signal
events failing reco (8.99M of those are the Phase-17 truth-only-miss appends).

## 2026-05-30 — C2: 3D driver

`unfold_3d_omnifold_unbinned.py` — eavail-aware 3D TTree readers, 3-column
feature `column_stack`, and `xsec_3d.py` for extraction / Eavail-marginal / 1D
projections. Reuses the 2D driver's flux/POT/nucleon/phase-space-gate helpers
via `import unfold_2d_omnifold_unbinned`; **CV-only** (the universe /
alt-model / bootstrap machinery is the deferred 3D-UQ campaign). Default Eavail
edges `[0,0.1,0.2,0.4,0.8,1.5,3.0,100]` GeV — the 100-GeV **catch bin is
required** so the Eavail-marginal captures the full CC-inclusive recoil tail and
equals the 2D result (Σ_k xsec·ΔE_k = 2D only if every truth event lands in a
bin). Marginal written as TH2D `hXSec2D` so `compare_to_paper_fullcov.py --ours`
is drop-in. Smoke (2 iter): c=1.0000, 3D integral ≡ marginal integral
(2.905e-38). Committed `685ffce`.

## 2026-05-30 — C3: full-stats unfold + Eavail-marginal anchor

Ran `unfold_3d_omnifold_unbinned.py` on the full MEFHC omnifile (5 iter lgbm,
seed 1, `--use-weights`) — ~14 min on the interactive node (256 CPU), c=1.0000.
Output `xsec_3d_MEFHC_5iter_lgbm.root`.

- **Eavail spectrum physical**: dσ/dE_avail falls monotonically 2.19e-38
  (low-recoil [0,0.1] peak) → 6.8e-41 (catch bin).
- **Normalization anchor PASS**: marginal total σ +0.95 % vs paper; 3D integral
  ≡ marginal integral; per-bin marginal/2D ratio median 1.0016.
- **Shape anchor ELEVATED**: marginal vs paper full-cov χ²/ndf = **4.98**
  (stat-only 12.48) vs frozen 2D 3.66 (default) / 2.65 (lgbm-CV); ~4.4 % per-bin
  scatter. Genuine reweighting effect, not a normalization/pipeline bug.

Cleanup: the bare `compare_to_paper_fullcov.py` call clobbered the tracked 2D
pull plot via its default out-prefix; restored from git, regenerated the 3D one
as `eavail_marginal_vs_paper_pull_full.png`. Committed `2cb4cde`, `69f0958`.

## 2026-05-30 — C3: reweight closure (PASS)

Added `--closure` / `--closure-reweight-eavail` to the 3D driver (commit
`27564a8`). CV self-closure is exact (degenerate — pseudo-data == MC reco).
Full-stats **Eavail-reweight closure**: injected a +30 % Gaussian bump in
*truth* Eavail (center 0.3 GeV, σ 0.15) into the pseudo-data; OmniFold recovers
it (step2 mean weight 1.048 ≈ injected 1.0485). Residuals (unfold/truth-ref):
**Eavail-marginal median 0.9999, std 0.0006, max\|dev\| 0.0021**; 3D-bin std
0.032; Eavail-1D 0.963–1.025. Output `closure_3d_MEFHC_eavail_bump.root`.

**Conclusion.** The marginal closes to 0.06 % — ~70× tighter than the 4.4 %
data-vs-2D scatter — so that scatter (and the χ²=4.98) is real data↔MC structure
the Eavail axis exposes, NOT a method bias. Workstream C framework validated
end-to-end. Committed `c73ce30`. Deferred: full 3D systematic-UQ campaign.

## 2026-05-31 — GENIE truth-generation scaffold + first model overlay (genie/)

Built `genie/` to generate truth-level GENIE events and compare to the unfolded
3D result (no detector sim needed — comparison is at truth level). Scaffold
committed `87cd16e`; see `genie/README.md`. Env solved without a container:
GENIE 2.12.10c from CVMFS via UPS `-H` SL7-flavor override + a 4-lib compat shim
(glibc forward-compat on SLES15). Two bring-up bugs fixed: the MINERvA flux is a
`PlotUtils::MnvH1D` GENIE reads as integral-zero → convert to plain TH1D
(`make_flux_for_genie.py`); reduced the 850 MB spline file to the C12+H1 subset
(`reduce_splines.sh`, 4 MB).

First result (2M base-CV events, 8 parallel gevgen × 250k ~9 min, hadd'd):
1.48M CC, 938k in phase space; flux-averaged ⟨σCC⟩/nucleon = 3.98e-38 cm²;
total-in-PS 2.52e-38 vs unfolded 3.08e-38. **GENIE 2.12 CV tracks the data
shape on (pT, p‖, Eavail) but runs ~10-18 % low in normalisation**
(`genie_vs_unfolded.png`) — expected base-CV behaviour before the MINERvA
Tune v1 reweights.

## 2026-05-31 — GENIE Stage B: MINERvA Tune v1 3D prediction

Done the robust way rather than reimplementing the tune reweights on gevgen
events: the analysis MC already carries the full Tune v1. `mc_truth_denom`'s
`w_truth` = flux CV × RPA × low-recoil 2p2h × non-res-π suppression
(mean 0.83 ≠ 1). `model_tune_xsec3d.py` bins the truth weighted by `w_truth` and
normalises with the unfold's flux/POT/nucleon machinery (completeness = 1, since
a model prediction needs no efficiency correction) → `model_tunev1_xsec3d.root`.
**Validation gate PASSED**: reproduces the shipped ancillary
`model_ptpl…Tune_v1.txt` to 0.01 % in normalisation (σ_tot/data 0.9125 vs
shipped 0.9124); χ²(ours vs shipped)/ndf = 1.57 (MC-stat-limited, not a model
difference); data-vs-tune χ²/ndf 33.0 for both. Totals-in-PS: base CV 2.52e-38,
Tune v1 2.71e-38, unfolded 3.08e-38 (tune raises GENIE ~7 %, still ~12 % low).

Three-way overlay `genie_tunes_vs_unfolded.png` (base CV + Tune v1 + unfolded):
on (pT, p‖) the tune barely moves GENIE; on **Eavail** the tune acts at low
recoil (RPA suppresses the QE peak, Tune v1 below base CV in the lowest bin) yet
still underpredicts the data there — the model-discrimination the 3D axis
enables. Workstream C + GENIE comparison complete. Remaining follow-ups:
NuWro/NEUT/GiBUU (one reader each), full 3D systematic UQ.
