# Phase C/D Feature and Resource Inventory

## Step 1 Candidate Quantities (Detector side)

*   **Reconstructed E_avail / recoil energy**:
    *   Exists in PRODUCED files: `G2_FPS_MEFHC_P12.npz` under `reco_scalars` column 2 (index 2).
    *   Population: Signal reco, background reco, and data reco. Row-aligned with the inventory.
    *   Units: GeV.
    *   Analysis definition: The 3D E_avail pipeline defines reconstructed E_avail as `sim_eavail` (via `recoCV->NewEavail() / 1000.0` in `runEventLoopOmniFold.cpp`). The underlying AnaTuple branch corresponding to recoil energy is `MasterAnaDev_hadron_recoil`.
*   **Muon kinematics**:
    *   Exists in PRODUCED files: `G2_FPS_MEFHC_P12.npz` under `reco_muon` (and `data_muon`, `bkg_muon`).
    *   Fields: 7 columns (px, py, pz, E, phi, qp, minos_ok).
    *   Population: Signal reco, background reco, and data reco. Row-aligned with the inventory.
*   **Pre-truncation whole-event energy sums and multiplicities**:
    *   Exists in PRODUCED files: Extracted via `extract_r4_slim.py` and built by `build_theirs_inputs.py` into the `globals` block.
    *   Fields: 16 global columns, including `log hadron_recoil`, `improved_nmichel`, `charged_pion_prong_count`, and 6 energy sums by PID (`log sum E pid=2` through `pid=7`).
    *   Population: Built for signal, background, and data. Row-aligned with the identity join (`row_index` via `join_sig.npz`).
*   **Overflow energy/count beyond the token cap**:
    *   Exists in PRODUCED files: Built by `build_theirs_inputs.py` into the `tokens` array as `aggregate_blob` (PID code 6) and `aggregate_prong` (PID code 7) when the number of objects exceeds the cap (`keep_b < n_blob` or `keep_p < n_prong`). Their sum is also recorded in the `globals` energy sums (indices 14 and 15).

## Step 2 Candidate Quantities (Truth side)

*   **True E_avail, q3, and similar**:
    *   Exists in PRODUCED files: `G2_FPS_MEFHC_P12.npz` under `truth_scalars` column 2 (E_avail) and column 3 (q3).
    *   Population: Truth denominator (`pass_truth`). Row-aligned with the inventory.

## Phase D Event Budget

*   Total signal-MC rows (truth denominator): 49,150,928
*   Total pass-reco rows: 20,573,521
*   Events used by the comparison: ~600k per half (600,130 for half A, 600,111 for half B).
*   Number of fully independent, identity-disjoint draws of size ~600k possible: `20,573,521 / 600,130` ≈ 34 draws.
