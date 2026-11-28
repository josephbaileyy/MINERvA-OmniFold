# Result against NEXT.md

**Original count comparison: unavailable locally.** The local filename search returned zero candidate files. The release ROOT file contains the measured cross section and covariance matrices. The downloaded tutorial ROOT file has one-dimensional p_T efficiency histograms. Neither supplies the original two-dimensional `h_pzmu_ptmu_CC` and `h_pzmu_ptmu_truth_CC` for the 40–60 GeV/c slice. The search scope, local paths, file digests and ROOT key inventories are recorded in [local-inventory.txt](local-inventory.txt). No cluster was accessed. <!-- absence-ok: bounded local search with paths and inspected ROOT keys in local-inventory.txt -->

For the declared selected-anywhere convention, [me1a-counts.csv](me1a-counts.csv) gives our counts separately in all fourteen true p_T bins. Per 10²⁰ MC POT, the original selected-anywhere contribution sums to 1,484.195 and the selected tracks added from the saved scan sum to 99.196. The partial selected numerator is 1,583.391 and the fiducial generated denominator is 1,788.024. Agreement with original counts remains unmeasured. The digitized Fig. 5 efficiency was not used as a substitute. <!-- absence-ok: the local original-histogram search and the keys inspected are itemized in local-inventory.txt; the outcome concerns only this comparison. -->

**Zeroing-order check: passed.** The supplied [review](report.md) is preserved verbatim. Two zero-generated truth columns (zero-based indices 144 and 161) had positive migration entries after the all-in-grid reclassification. Those columns now have zero prior and response before iteration one. The toy test assigns the full yield to supported truth. All real selected-count vectors match the separately implemented generated-denominator iteration, with maximum absolute difference below 4 × 10⁻¹⁰ weighted events. The other four diagnostic rows reproduce the frozen numbers. [Verification output](zeroing-check.txt)

| Affected all-in-grid variant | Corrected partial χ²/205 (saved scan) | True 40–60 column ratio to published |
|---|---:|---:|
| In-grid numerator | 0.34925865 | 1.09367341 |
| Selected-anywhere numerator | 0.37259493 | 1.02573016 |

Both revised rows reproduce the supplied review at its printed precision. The replay uses the same observed data, background transfer, generated denominator, exposure and covariance as the frozen record. The added tracks cover reco p∥ ≥ 20 GeV/c and reco p_T < 4.5 GeV/c. The outputs describe the partial scan and establish no cause. Production IBU, OmniFold and note text are unchanged. [Six replay rows](replay.txt) · [Per-bin replay](true_40_60.csv)

From this directory, the following commands reproduce the numerical outputs on a checkout of this branch with NumPy, pandas and uproot installed.

```sh
python3 me1a_counts.py
OPENBLAS_NUM_THREADS=1 python3 verify_zeroing.py "$(git rev-parse --show-toplevel)" > zeroing-check.txt
```
