# Exploratory IBU convention replay

The three rows of the original comparison are in `replay.txt`. All use the same observed data, fiducial generated denominator, released bin edges and ten iterations of signed IBU.

| Output row | Counting convention |
|---|---|
| `unchanged in_grid` | Count selected events reconstructed in the analysis grid in the efficiency numerator. |
| `unchanged anywhere` | Extend that numerator to all selected reconstructed destinations, including overflow. |
| `all_in_grid_true_muons anywhere` | Also move saved selected negative tracks from νμ charged-current interactions with a true vertex outside the fiducial volume and true muon kinematics in the grid from background into migration and the numerator. Each event contributes once. |

This is a partial replay. The added tracks cover reco p∥ ≥ 20 GeV/c and reco p_T < 4.5 GeV/c. The target efficiency was digitized from MINERvA Fig. 5. Its product with our generated count is an estimate for comparison. Production IBU and OmniFold are unchanged. This record makes no causal claim.

The original script, output, per-bin table and working notes are preserved byte for byte. `INPUTS.sha256` lists every direct input by repository-relative path. The files are already tracked at receipt commit `411ac910e5f9913b49d120764033b0815c7b6339`. See `README.txt` for the replay command and references.
