# V_F (C_e^infl) readings, Phases 1 and 2: OLD -> C_e^infl

Read by `vf_readings.py`; readings go to the director first; nothing here is note wording.

## 1. Decision-rule outcome changes (first, each on its own)

**Control D:** holds, every event under a named ruling (the tool exits nonzero otherwise). Every non-float leaf of every swept readout, OLD -> V_F, both arms (`sweep()`): 2129 changes, 250 of them in decision-rule fields; 4 control D events, 4 under a named ruling.

**Headline: every decision-rule change, from the sweep (anything not named holds), then the derived lines:**

- **CONTROL D** gover `/quadrants/QD/2D/printed_only_without_C_PL5D/outcome`: "agree" -> "agree below a correlation" (an outcome string changes, not toward agreement): *named exception:* the director, 2026-11-26: a named, disclosed exception to control D; a weakened printed agreement label (rho* crosses 1, the knife edge); no outcome reads this sub-record; the note's printed label follows the V_F value; Joseph sees it with the readings
- **CONTROL D** cr `/quadrants/QD/2D/printed_only_without_C_PL5D/outcome`: "agree" -> "agree below a correlation" (an outcome string changes, not toward agreement): *named exception:* the director, 2026-11-26: a named, disclosed exception to control D; a weakened printed agreement label (rho* crosses 1, the knife edge); no outcome reads this sub-record; the note's printed label follows the V_F value; Joseph sees it with the readings
- **CONTROL D** prr `/readings/PR-3/C25/new_flags`: ["A7_nuwro", "W3", "stage0c_gibuu"] -> ["A7_nuwro", "W3", "q3", "stage0c_gibuu"] (gains ['q3']): *named exception:* the director, 2026-11-26: a reference shift, not a new flag (q3 is flagged at this level under both OLD and V_F; it appears new only because B0's own q3 flag clears under V_F)
- **CONTROL D** prr `/readings/PR-3/O2/new_flags`: ["A7_genie_cv", "A7_nuwro", "W1", "W3", "closure_nuwro", "stage0c_gibuu"] -> ["A7_nuwro", "W1", "W3", "closure_nuwro", "q3", "stage0c_gibuu"] (gains ['q3']): *named exception:* the director, 2026-11-26: a reference shift, not a new flag (q3 is flagged at this level under both OLD and V_F; it appears new only because B0's own q3 flag clears under V_F)
- cr QD 2D, the printed-only arm without C_PL5D: a weakened printed agreement label, "agree" -> "agree below a correlation"; rho* 1.00353 -> 0.999854, at the knife edge of rho* = 1; no outcome reads this sub-record (its label: "printed only, no outcome is read from it: the sixteen-cell matrix without C_PL5D against Q, which includes C_PL; not a like-for-like pair")
- gover QD 2D, the printed-only arm without C_PL5D: a weakened printed agreement label, "agree" -> "agree below a correlation"; rho* 1.00349 -> 0.999993, at the knife edge of rho* = 1; no outcome reads this sub-record (its label: "printed only, no outcome is read from it: the sixteen-cell matrix without C_PL5D against Q, which includes C_PL; not a like-for-like pair")
- **A printed conclusion changes (for Joseph):** RSN SM: "a fake-data conclusion changes under SM" -> "the fake-data conclusions survive SM"
- E2's largest change moves: nopl/genie_mec/shape_only -> nopl/genie_mec/total (Delta_max 6.07 -> 10.81)
- cr `/quadrants/QA/2D/printed_only_without_C_PL5D/outcome`: "agree below a correlation" -> "agree"
- cr `/quadrants/QB/2D/outcome`: "agree below a correlation" -> "agree"
- f0 `/triggers/all_graded/cells_abs_z_gt_2`: 4 -> 2
- f0 `/triggers/all_graded/truths_p_lt_0.01`: 4 -> 1
- f0 `/triggers/by_group/non-vertex/by_family/q3/truths_p_lt_0.01`: 1 -> 0
- f0 `/triggers/by_group/non-vertex/truths_p_lt_0.01`: 1 -> 0
- f0 `/triggers/by_group/vertex-family/by_family/gibuu/cells_abs_z_gt_2`: 4 -> 2
- f0 `/triggers/by_group/vertex-family/by_family/gibuu/truths_p_lt_0.01`: 2 -> 1
- f0 `/triggers/by_group/vertex-family/by_family/nuwro/truths_p_lt_0.01`: 1 -> 0
- f0 `/triggers/by_group/vertex-family/cells_abs_z_gt_2`: 4 -> 2
- f0 `/triggers/by_group/vertex-family/truths_p_lt_0.01`: 3 -> 1
- f0 `/triggers/listed[*]/cells`: ["R02", "R06", "R07"] -> ["R02", "R06"] x1 (A7_gibuu)
- f0 `/triggers/listed[*]/cells`: ["R06"] -> null x1 (stage0c_gibuu)
- f0 `/triggers/listed[*]/cells`: [] -> null x2 (W3, q3)
- f0 `/triggers/listed[*]/p_lt_0.01`: true -> null x3 (W3, q3, stage0c_gibuu)
- f0 `/truths[*]/grade/cells_abs_z_gt_2`: ["R02", "R06", "R07"] -> ["R02", "R06"] x1 (A7_gibuu)
- f0 `/truths[*]/grade/cells_abs_z_gt_2`: ["R06"] -> [] x1 (stage0c_gibuu)
- f0 `/truths[*]/grade/cells_abs_z_gt_2`: ["R07"] -> [] x1 (P2g)
- f0 `/truths[*]/grade/p_lt_0.01`: true -> false x6 (P1r, P2g, P2r, W3, q3, stage0c_gibuu)
- f0 `/truths[*]/in_sample/cells_abs_z_gt_2`: ["R07"] -> [] x1 (P2g)
- f0 `/truths[*]/in_sample/p_lt_0.01`: true -> false x3 (P1r, P2g, W3)
- f0 `/truths[*]/listed`: true -> false x3 (W3, q3, stage0c_gibuu)
- f0 `/truths[*]/p_parallel_lt_4p5/p_lt_0.01`: true -> false x1 (stage0c_gibuu)
- f0 `/truths[*]/sensitivity/p_lt_0.01`: true -> false x1 (q3)
- f0b `/triggers/all_graded/truths_p_lt_0.01`: 2 -> 1
- f0b `/triggers/by_group/non-vertex/by_family/q3/truths_p_lt_0.01`: 1 -> 0
- f0b `/triggers/by_group/non-vertex/truths_p_lt_0.01`: 1 -> 0
- f0b `/triggers/listed[*]/cells`: [] -> null x1 (q3)
- f0b `/triggers/listed[*]/p_lt_0.01`: true -> null x1 (q3)
- f0b `/truths[*]/grade/cells_abs_z_gt_2`: ["R07"] -> [] x1 (P2g)
- f0b `/truths[*]/grade/p_lt_0.01`: true -> false x4 (P1r, P2g, P2r, q3)
- f0b `/truths[*]/in_sample/cells_abs_z_gt_2`: ["R07"] -> [] x1 (P2g)
- f0b `/truths[*]/in_sample/p_lt_0.01`: true -> false x1 (P1r)
- f0b `/truths[*]/listed`: true -> false x1 (q3)
- f0b `/truths[*]/sensitivity/p_lt_0.01`: true -> false x1 (q3)
- f0b[nopl] `/triggers/all_graded/cells_abs_z_gt_2`: 4 -> 2
- f0b[nopl] `/triggers/all_graded/truths_p_lt_0.01`: 2 -> 1
- f0b[nopl] `/triggers/by_group/non-vertex/by_family/q3/truths_p_lt_0.01`: 1 -> 0
- f0b[nopl] `/triggers/by_group/non-vertex/truths_p_lt_0.01`: 1 -> 0
- f0b[nopl] `/triggers/by_group/vertex-family/by_family/gibuu/cells_abs_z_gt_2`: 4 -> 2
- f0b[nopl] `/triggers/by_group/vertex-family/cells_abs_z_gt_2`: 4 -> 2
- f0b[nopl] `/triggers/listed[*]/cells`: ["R02", "R06", "R07"] -> ["R02", "R06"] x1 (A7_gibuu)
- f0b[nopl] `/triggers/listed[*]/cells`: ["R06"] -> null x1 (stage0c_gibuu)
- f0b[nopl] `/triggers/listed[*]/cells`: [] -> null x1 (q3)
- f0b[nopl] `/triggers/listed[*]/p_lt_0.01`: false -> null x1 (stage0c_gibuu)
- f0b[nopl] `/triggers/listed[*]/p_lt_0.01`: true -> null x1 (q3)
- f0b[nopl] `/truths[*]/grade/cells_abs_z_gt_2`: ["R02", "R06", "R07"] -> ["R02", "R06"] x1 (A7_gibuu)
- f0b[nopl] `/truths[*]/grade/cells_abs_z_gt_2`: ["R06"] -> [] x1 (stage0c_gibuu)
- f0b[nopl] `/truths[*]/grade/cells_abs_z_gt_2`: ["R07"] -> [] x1 (P2g)
- f0b[nopl] `/truths[*]/grade/p_lt_0.01`: true -> false x4 (P1r, P2g, P2r, q3)
- f0b[nopl] `/truths[*]/in_sample/cells_abs_z_gt_2`: ["R07"] -> [] x1 (P2g)
- f0b[nopl] `/truths[*]/in_sample/p_lt_0.01`: true -> false x1 (P1r)
- f0b[nopl] `/truths[*]/listed`: true -> false x2 (q3, stage0c_gibuu)
- f0b[nopl] `/truths[*]/sensitivity/p_lt_0.01`: true -> false x1 (q3)
- f1 `/triggers/all_graded/truths_p_lt_0.01`: 2 -> 1
- f1 `/triggers/by_group/non-vertex/by_family/q3/truths_p_lt_0.01`: 1 -> 0
- f1 `/triggers/by_group/non-vertex/truths_p_lt_0.01`: 1 -> 0
- f1 `/triggers/listed[*]/cells`: [] -> null x1 (q3)
- f1 `/triggers/listed[*]/p_lt_0.01`: true -> null x1 (q3)
- f1 `/truths[*]/grade/cells_abs_z_gt_2`: ["R07"] -> [] x1 (P2g)
- f1 `/truths[*]/grade/p_lt_0.01`: true -> false x4 (P1r, P2g, P2r, q3)
- f1 `/truths[*]/in_sample/cells_abs_z_gt_2`: ["R07"] -> [] x1 (P2g)
- f1 `/truths[*]/in_sample/p_lt_0.01`: true -> false x1 (P1r)
- f1 `/truths[*]/listed`: true -> false x1 (q3)
- f1 `/truths[*]/sensitivity/p_lt_0.01`: true -> false x1 (q3)
- f1[nopl] `/triggers/all_graded/cells_abs_z_gt_2`: 4 -> 2
- f1[nopl] `/triggers/all_graded/truths_p_lt_0.01`: 2 -> 1
- f1[nopl] `/triggers/by_group/non-vertex/by_family/q3/truths_p_lt_0.01`: 1 -> 0
- f1[nopl] `/triggers/by_group/non-vertex/truths_p_lt_0.01`: 1 -> 0
- f1[nopl] `/triggers/by_group/vertex-family/by_family/gibuu/cells_abs_z_gt_2`: 4 -> 2
- f1[nopl] `/triggers/by_group/vertex-family/cells_abs_z_gt_2`: 4 -> 2
- f1[nopl] `/triggers/listed[*]/cells`: ["R02", "R06", "R07"] -> ["R02", "R06"] x1 (A7_gibuu)
- f1[nopl] `/triggers/listed[*]/cells`: ["R06"] -> null x1 (stage0c_gibuu)
- f1[nopl] `/triggers/listed[*]/cells`: [] -> null x1 (q3)
- f1[nopl] `/triggers/listed[*]/p_lt_0.01`: false -> null x1 (stage0c_gibuu)
- f1[nopl] `/triggers/listed[*]/p_lt_0.01`: true -> null x1 (q3)
- f1[nopl] `/truths[*]/grade/cells_abs_z_gt_2`: ["R02", "R06", "R07"] -> ["R02", "R06"] x1 (A7_gibuu)
- f1[nopl] `/truths[*]/grade/cells_abs_z_gt_2`: ["R06"] -> [] x1 (stage0c_gibuu)
- f1[nopl] `/truths[*]/grade/cells_abs_z_gt_2`: ["R07"] -> [] x1 (P2g)
- f1[nopl] `/truths[*]/grade/p_lt_0.01`: true -> false x4 (P1r, P2g, P2r, q3)
- f1[nopl] `/truths[*]/in_sample/cells_abs_z_gt_2`: ["R07"] -> [] x1 (P2g)
- f1[nopl] `/truths[*]/in_sample/p_lt_0.01`: true -> false x1 (P1r)
- f1[nopl] `/truths[*]/listed`: true -> false x2 (q3, stage0c_gibuu)
- f1[nopl] `/truths[*]/sensitivity/p_lt_0.01`: true -> false x1 (q3)
- gover `/quadrants/QA/2D/outcome`: "agree below a correlation" -> "agree"
- gover `/quadrants/QA/2D/printed_only_without_C_PL5D/outcome`: "agree below a correlation" -> "agree"
- gover `/quadrants/QB/2D/outcome`: "agree below a correlation" -> "agree"
- prr `/ibu/*/*/s*/grade/cells_abs_z_gt_2`: ["R02", "R06", "R07", "R10", "R13", "R14", "R15"] -> ["R02", "R06", "R07", "R10", "R13", "R14"] x3 (K20/A7_gibuu/s994001, K20/A7_gibuu/s994003, K20/A7_gibuu/s994004)
- prr `/ibu/*/*/s*/grade/cells_abs_z_gt_2`: ["R02", "R06", "R10", "R15"] -> ["R06", "R15"] x1 (K1/stage0c_gibuu/s991000)
- prr `/ibu/*/*/s*/grade/cells_abs_z_gt_2`: ["R02", "R06", "R10"] -> ["R02", "R06"] x3 (K2/A7_gibuu/s991000, K2/A7_gibuu/s994002, K2/A7_gibuu/s994003)
- prr `/ibu/*/*/s*/grade/cells_abs_z_gt_2`: ["R02", "R06"] -> ["R06"] x1 (K10/stage0c_gibuu/s991000)
- prr `/ibu/*/*/s*/grade/cells_abs_z_gt_2`: ["R03", "R06", "R10"] -> ["R06"] x1 (K20/A7_nuwro/s991000)
- prr `/ibu/*/*/s*/grade/cells_abs_z_gt_2`: ["R03", "R06", "R13", "R14"] -> ["R13", "R14"] x4 (K5/A7_gibuu/s991000, K5/A7_gibuu/s994001, K5/A7_gibuu/s994002, K5/A7_gibuu/s994003)
- prr `/ibu/*/*/s*/grade/cells_abs_z_gt_2`: ["R06", "R07"] -> ["R06"] x1 (K200/W1/s991000)
- prr `/ibu/*/*/s*/grade/cells_abs_z_gt_2`: ["R06", "R13", "R14"] -> ["R13", "R14"] x1 (K5/A7_gibuu/s994004)
- prr `/ibu/*/*/s*/grade/cells_abs_z_gt_2`: ["R06"] -> [] x2 (K10/W3/s991000, K20/W1/s991000)
- prr `/ibu/*/*/s*/grade/cells_abs_z_gt_2`: ["R07", "R14"] -> ["R14"] x3 (K3/A7_gibuu/s994003, K3/A7_gibuu/s994004, K4/A7_gibuu/s994004)
- prr `/ibu/*/*/s*/grade/flagged`: true -> false x18 (K1/W3/s991000, K1/q3/s991000, K10/A7_genie_cv/s991000, K10/q3/s991000, K2/q3/s991000, K2/stage0c_gibuu/s991000, K20/A7_genie_cv/s991000, K20/W1/s991000, K200/A7_genie_mec/s991000, K200/W2/s991000, K3/q3/s991000, K4/A7_nuwro/s991000, K4/W3/s991000, K4/closure_nuwro/s991000, K4/q3/s991000, K5/W3/s991000, K5/stage0c_gibuu/s991000, K50/A7_genie_mec/s991000)
- prr `/readings/PR-3/IBU_K5/new_flags`: ["A7_nuwro", "W3", "closure_nuwro", "stage0c_gibuu"] -> ["A7_nuwro", "closure_nuwro"]
- prr `/readings/PR-3/K2/new_flags`: ["A7_nuwro", "W3", "stage0c_gibuu"] -> []
- prr `/readings/PR-3/O4/new_flags`: ["A7_nuwro"] -> []
- prr `/table/*/*/s*/grade/cells_abs_z_gt_2`: ["R02", "R06", "R07"] -> ["R02", "R06"] x6 (K20/A7_gibuu/s991000, K20/A7_gibuu/s994001, K20/A7_gibuu/s994002, K20/A7_gibuu/s994003, K20/A7_gibuu/s994004, K50/A7_gibuu/s991000)
- prr `/table/*/*/s*/grade/cells_abs_z_gt_2`: ["R05", "R06", "R07"] -> ["R05"] x1 (O2/A7_nuwro/s991000)
- prr `/table/*/*/s*/grade/cells_abs_z_gt_2`: ["R05", "R06", "R10"] -> ["R06"] x1 (O2/W3/s991000)
- prr `/table/*/*/s*/grade/cells_abs_z_gt_2`: ["R06", "R07", "R08"] -> ["R07", "R08"] x2 (C25/q3/s991000, O2/q3/s991000)
- prr `/table/*/*/s*/grade/cells_abs_z_gt_2`: ["R06"] -> [] x1 (K2/stage0c_gibuu/s991000)
- prr `/table/*/*/s*/grade/flagged`: true -> false x16 (B0/q3/s991000, C1000/q3/s991000, C400/q3/s991000, K10/q3/s991000, K2/A7_nuwro/s991000, K2/W3/s991000, K2/q3/s991000, K2/stage0c_gibuu/s991000, K20/q3/s991000, K50/q3/s991000, MCq/q3/s991000, O2/A7_genie_cv/s991000, O3/q3/s991000, O4/A7_nuwro/s991000, O4/q3/s991000, O4r/q3/s991000)
- rsn `/arms/G6/P1/listed`: ["q3", "A7_gibuu"] -> ["A7_gibuu"]
- rsn `/arms/G6/P1/listed_nominal`: ["q3", "A7_gibuu"] -> ["A7_gibuu"]
- rsn `/arms/G6/P2/by_group/non-vertex/by_family/q3/truths_p_lt_0.01`: 1 -> 0
- rsn `/arms/G6/P2/by_group/non-vertex/truths_p_lt_0.01`: 1 -> 0
- rsn `/arms/G6/P2/by_group_nominal/non-vertex/by_family/q3/truths_p_lt_0.01`: 1 -> 0
- rsn `/arms/G6/P2/by_group_nominal/non-vertex/truths_p_lt_0.01`: 1 -> 0
- rsn `/arms/SM/P1/class`: "more flagged" -> "unchanged"
- rsn `/arms/SM/P1/listed`: ["q3", "A7_nuwro", "A7_gibuu"] -> ["A7_gibuu"]
- rsn `/arms/SM/P1/listed_nominal`: ["q3", "A7_gibuu"] -> ["A7_gibuu"]
- rsn `/arms/SM/P2/by_group/non-vertex/by_family/q3/truths_p_lt_0.01`: 1 -> 0
- rsn `/arms/SM/P2/by_group/non-vertex/truths_p_lt_0.01`: 1 -> 0
- rsn `/arms/SM/P2/by_group/vertex-family/by_family/nuwro/truths_p_lt_0.01`: 1 -> 0
- rsn `/arms/SM/P2/by_group/vertex-family/truths_p_lt_0.01`: 2 -> 1
- rsn `/arms/SM/P2/by_group_nominal/non-vertex/by_family/q3/truths_p_lt_0.01`: 1 -> 0
- rsn `/arms/SM/P2/by_group_nominal/non-vertex/truths_p_lt_0.01`: 1 -> 0
- rsn `/arms/SM/verdict`: "a fake-data conclusion changes under SM" -> "the fake-data conclusions survive SM"
- rsn `/arms/WR/P7/q3/flag_equal_weights`: true -> false
- rsn `/arms/WR/P7/q3/flag_weighted`: true -> false
- rsnregrade `/arms/G6/by_group/non-vertex/by_family/q3/truths_p_lt_0.01`: 1 -> 0
- rsnregrade `/arms/G6/by_group/non-vertex/truths_p_lt_0.01`: 1 -> 0
- rsnregrade `/arms/G6/listed`: ["q3", "A7_gibuu"] -> ["A7_gibuu"]
- rsnregrade `/arms/G6/records[*]/grade/cells_abs_z_gt_2`: ["R07"] -> [] x1 (P2g)
- rsnregrade `/arms/G6/records[*]/grade/p_lt_0.01`: true -> false x4 (P1r, P2g, P2r, q3)
- rsnregrade `/arms/G6/records[*]/in_sample/cells_abs_z_gt_2`: ["R07"] -> [] x1 (P2g)
- rsnregrade `/arms/G6/records[*]/in_sample/p_lt_0.01`: true -> false x2 (P1r, P2r)
- rsnregrade `/arms/G6/records[*]/listed`: true -> false x1 (q3)
- rsnregrade `/arms/G6/records[*]/sensitivity/p_lt_0.01`: true -> false x1 (q3)
- rsnregrade `/arms/SM/by_group/non-vertex/by_family/q3/truths_p_lt_0.01`: 1 -> 0
- rsnregrade `/arms/SM/by_group/non-vertex/truths_p_lt_0.01`: 1 -> 0
- rsnregrade `/arms/SM/by_group/vertex-family/by_family/nuwro/truths_p_lt_0.01`: 1 -> 0
- rsnregrade `/arms/SM/by_group/vertex-family/truths_p_lt_0.01`: 2 -> 1
- rsnregrade `/arms/SM/listed`: ["q3", "A7_nuwro", "A7_gibuu"] -> ["A7_gibuu"]
- rsnregrade `/arms/SM/records[*]/grade/cells_abs_z_gt_2`: ["R07"] -> [] x1 (P2g)
- rsnregrade `/arms/SM/records[*]/grade/p_lt_0.01`: true -> false x5 (A7_nuwro, P1r, P2g, P2r, q3)
- rsnregrade `/arms/SM/records[*]/in_sample/cells_abs_z_gt_2`: ["R07"] -> [] x1 (P2g)
- rsnregrade `/arms/SM/records[*]/in_sample/p_lt_0.01`: true -> false x4 (A7_nuwro, P1r, P2g, P2r)
- rsnregrade `/arms/SM/records[*]/listed`: true -> false x2 (A7_nuwro, q3)
- rsnregrade `/arms/SM/records[*]/sensitivity/p_lt_0.01`: true -> false x1 (q3)
- rsnregrade `/arms/nominal/by_group/non-vertex/by_family/q3/truths_p_lt_0.01`: 1 -> 0
- rsnregrade `/arms/nominal/by_group/non-vertex/truths_p_lt_0.01`: 1 -> 0
- rsnregrade `/arms/nominal/listed`: ["q3", "A7_gibuu"] -> ["A7_gibuu"]
- rsnregrade `/arms/nominal/records[*]/grade/cells_abs_z_gt_2`: ["R07"] -> [] x1 (P2g)
- rsnregrade `/arms/nominal/records[*]/grade/p_lt_0.01`: true -> false x4 (P1r, P2g, P2r, q3)
- rsnregrade `/arms/nominal/records[*]/in_sample/cells_abs_z_gt_2`: ["R07"] -> [] x1 (P2g)
- rsnregrade `/arms/nominal/records[*]/in_sample/p_lt_0.01`: true -> false x1 (P1r)
- rsnregrade `/arms/nominal/records[*]/listed`: true -> false x1 (q3)
- rsnregrade `/arms/nominal/records[*]/sensitivity/p_lt_0.01`: true -> false x1 (q3)
- rsnregrade `/wr_directions/q3/equal_weights/p_lt_0.01`: true -> false
- rsnregrade `/wr_directions/q3/weighted/p_lt_0.01`: true -> false
- vatlas `/readings/V-ATLAS/per_truth/q3/p_lt_0.01`: true -> false

**F0/F0b/F1 listings** (p < 0.01 or any |z| > 2): STOPs 0; changes:

- f0 W3: listed True -> False; |z|>2 cells - -> -; p 0.00273 -> 0.478
- f0 q3: listed True -> False; |z|>2 cells - -> -; p 5.59e-07 -> 0.0196
- f0 stage0c_gibuu: listed True -> False; |z|>2 cells R06 -> -; p 0.00313 -> 0.389
- f0 A7_gibuu: listed True -> True; |z|>2 cells R02 R06 R07 -> R02 R06; p 0 -> 9.34e-16
- f0 P2g: listed False -> False; |z|>2 cells R07 -> -; p 0.000959 -> 0.299
- with/f0b q3: listed True -> False; |z|>2 cells - -> -; p 9.15e-06 -> 0.129
- with/f0b P2g: listed False -> False; |z|>2 cells R07 -> -; p 0.00251 -> 0.358
- with/f1 q3: listed True -> False; |z|>2 cells - -> -; p 9.15e-06 -> 0.129
- with/f1 P2g: listed False -> False; |z|>2 cells R07 -> -; p 0.00251 -> 0.358
- nopl/f0b q3: listed True -> False; |z|>2 cells - -> -; p 6.44e-06 -> 0.12
- nopl/f0b stage0c_gibuu: listed True -> False; |z|>2 cells R06 -> -; p 0.0621 -> 0.681
- nopl/f0b A7_gibuu: listed True -> True; |z|>2 cells R02 R06 R07 -> R02 R06; p 7.96e-29 -> 7.09e-13
- nopl/f0b P2g: listed False -> False; |z|>2 cells R07 -> -; p 0.00153 -> 0.332
- nopl/f1 q3: listed True -> False; |z|>2 cells - -> -; p 6.44e-06 -> 0.12
- nopl/f1 stage0c_gibuu: listed True -> False; |z|>2 cells R06 -> -; p 0.0621 -> 0.681
- nopl/f1 A7_gibuu: listed True -> True; |z|>2 cells R02 R06 R07 -> R02 R06; p 7.96e-29 -> 7.09e-13
- nopl/f1 P2g: listed False -> False; |z|>2 cells R07 -> -; p 0.00153 -> 0.332

**PRR (PR-3, p < 0.01 or any |z| > 2):** flags set under V_F: 0; flags cleared: 34; PR-1 unchanged: True; labels unchanged: True.

- K2: does not clear at these truths ['A7_nuwro', 'W3', 'stage0c_gibuu'] -> does not clear at these truths []
- C25: does not clear at these truths ['A7_nuwro', 'W3', 'stage0c_gibuu'] -> does not clear at these truths ['A7_nuwro', 'W3', 'q3', 'stage0c_gibuu']
  - *q3 here is a reference shift, not a new flag:* q3 is flagged at this level under both OLD and V_F; it appears "new" only because B0's own q3 flag clears under V_F (the director, 2026-11-26).
- O4: does not clear at these truths ['A7_nuwro'] -> does not clear at these truths []
- O2: does not clear at these truths ['A7_genie_cv', 'A7_nuwro', 'W1', 'W3', 'closure_nuwro', 'stage0c_gibuu'] -> does not clear at these truths ['A7_nuwro', 'W1', 'W3', 'closure_nuwro', 'q3', 'stage0c_gibuu']
  - *q3 here is a reference shift, not a new flag:* q3 is flagged at this level under both OLD and V_F; it appears "new" only because B0's own q3 flag clears under V_F (the director, 2026-11-26).
- IBU_K5: does not clear at these truths ['A7_nuwro', 'W3', 'closure_nuwro', 'stage0c_gibuu'] -> does not clear at these truths ['A7_nuwro', 'closure_nuwro']

**RSN regrade** (listed truths; triggers by group):

- nominal: listed ['q3', 'A7_gibuu'] -> ['A7_gibuu']; trigger counts: prior p<0.01 0 -> 0; vertex-family p<0.01 1 -> 1; non-vertex p<0.01 1 -> 0; held-out p<0.01 0 -> 0
- G6: listed ['q3', 'A7_gibuu'] -> ['A7_gibuu']; trigger counts: prior p<0.01 0 -> 0; vertex-family p<0.01 1 -> 1; non-vertex p<0.01 1 -> 0; held-out p<0.01 0 -> 0
- SM: listed ['q3', 'A7_nuwro', 'A7_gibuu'] -> ['A7_gibuu']; trigger counts: prior p<0.01 0 -> 0; vertex-family p<0.01 2 -> 1; non-vertex p<0.01 1 -> 0; held-out p<0.01 0 -> 0

**RSN conclusions and arm verdicts:**

- P1: unchanged
- P2: unchanged
- P3: unchanged
- P4: unchanged
- P5: unchanged
- P6: unchanged
- P7: unchanged
- P8: unchanged
- G6: unchanged
- SM: a fake-data conclusion changes under SM -> the fake-data conclusions survive SM
- WR: unchanged
- TR: unchanged

**V-ATLAS:** valid ['R00', 'R01', 'R03', 'R04', 'R05', 'R07', 'R08', 'R09', 'R10', 'R11', 'R12', 'R13', 'R14', 'R15'] -> ['R00', 'R01', 'R03', 'R04', 'R05', 'R07', 'R08', 'R09', 'R10', 'R11', 'R12', 'R13', 'R14', 'R15']; A3 fails ['R02', 'R06'] -> ['R02', 'R06']; V-PRIOR unchanged: True.

**gover labels:** QA 2D agree below a correlation -> agree; QB 2D agree below a correlation -> agree (3D unchanged in every quadrant)
**cr labels:** QB 2D agree below a correlation -> agree (3D unchanged in every quadrant)
**gover printed-only arm (2D, without C_PL5D; no outcome is read from it):** QA agree below a correlation -> agree; QD agree -> agree below a correlation
**cr printed-only arm (2D, without C_PL5D; no outcome is read from it):** QA agree below a correlation -> agree; QD agree -> agree below a correlation

**X agreement (p >= 0.05 and every |z| <= 2.50):**

- primary: agree -> agree; r0 chi2_4 1.160 -> 0.828, p 0.885 -> 0.935; r1 chi2_4 1.232 -> 0.878, p 0.873 -> 0.928
- Q_R_alone: agree -> agree; r0 chi2_4 0.780 -> 0.491, p 0.941 -> 0.974; r1 chi2_4 0.925 -> 0.515, p 0.921 -> 0.972
- C_PL_pair_zero: agree -> agree; r0 chi2_4 0.792 -> 0.696, p 0.939 -> 0.952; r1 chi2_4 1.156 -> 0.787, p 0.885 -> 0.940

**E2:** within seed variation False -> False; Delta_max 6.07 -> 10.81; the 2.3 flag 5.56 (True) -> 7.93 (True); largest change at nopl/genie_mec/shape_only -> nopl/genie_mec/total.

**gdefs seed flags:** unchanged in every record

## 1c. The sweep's descriptive changes (not decision-rule fields; every one in vf_readings.json)

| readout | path pattern | changes |
|---|---|---|
| diag | `/blocks/extra` | 1 |
| diag | `/predictions[]/comparisons[]/absolute/modes_by_chi2[]/mode` | 51 |
| diag | `/predictions[]/comparisons[]/absolute/modes_needed/50%` | 2 |
| diag | `/predictions[]/comparisons[]/absolute/modes_needed/90%` | 3 |
| diag | `/predictions[]/comparisons[]/absolute/modes_needed/99%` | 3 |
| diag | `/predictions[]/comparisons[]/absolute/removed[]/removed` | 5 |
| diag | `/predictions[]/comparisons[]/absolute/top_modes[]/dominant` | 11 |
| diag | `/predictions[]/comparisons[]/absolute/top_modes[]/mode` | 7 |
| diag | `/predictions[]/comparisons[]/matrix` | 5 |
| diag | `/predictions[]/comparisons[]/relative_to_f/modes_by_chi2[]/mode` | 54 |
| diag | `/predictions[]/comparisons[]/relative_to_f/modes_needed/50%` | 1 |
| diag | `/predictions[]/comparisons[]/relative_to_f/modes_needed/90%` | 5 |
| diag | `/predictions[]/comparisons[]/relative_to_f/modes_needed/99%` | 4 |
| diag | `/predictions[]/comparisons[]/relative_to_f/removed[]/removed` | 5 |
| diag | `/predictions[]/comparisons[]/relative_to_f/top_modes[]/dominant` | 13 |
| diag | `/predictions[]/comparisons[]/relative_to_f/top_modes[]/mode` | 8 |
| diag[nopl] | `/blocks/extra` | 1 |
| diag[nopl] | `/predictions[]/comparisons[]/absolute/modes_by_chi2[]/mode` | 54 |
| diag[nopl] | `/predictions[]/comparisons[]/absolute/modes_needed/50%` | 1 |
| diag[nopl] | `/predictions[]/comparisons[]/absolute/modes_needed/90%` | 3 |
| diag[nopl] | `/predictions[]/comparisons[]/absolute/modes_needed/99%` | 5 |
| diag[nopl] | `/predictions[]/comparisons[]/absolute/removed[]/removed` | 5 |
| diag[nopl] | `/predictions[]/comparisons[]/absolute/top_modes[]/dominant` | 9 |
| diag[nopl] | `/predictions[]/comparisons[]/absolute/top_modes[]/mode` | 7 |
| diag[nopl] | `/predictions[]/comparisons[]/matrix` | 5 |
| diag[nopl] | `/predictions[]/comparisons[]/relative_to_f/modes_by_chi2[]/mode` | 50 |
| diag[nopl] | `/predictions[]/comparisons[]/relative_to_f/modes_needed/50%` | 2 |
| diag[nopl] | `/predictions[]/comparisons[]/relative_to_f/modes_needed/90%` | 4 |
| diag[nopl] | `/predictions[]/comparisons[]/relative_to_f/modes_needed/99%` | 4 |
| diag[nopl] | `/predictions[]/comparisons[]/relative_to_f/removed[]/removed` | 5 |
| diag[nopl] | `/predictions[]/comparisons[]/relative_to_f/top_modes[]/dominant` | 14 |
| diag[nopl] | `/predictions[]/comparisons[]/relative_to_f/top_modes[]/mode` | 8 |
| dp | `/code_sha256/fd_cpl_addition.py` | 1 |
| dp | `/code_sha256/fd_vf_addition.py` | 1 |
| dp | `/correlation_of` | 1 |
| dp | `/labels/block` | 1 |
| dp | `/labels/context_5a_5b` | 1 |
| dp | `/labels/context_dr_pair` | 1 |
| dp | `/labels/covariance` | 1 |
| dp | `/labels/decision` | 1 |
| dp | `/labels/not_citable_for` | 1 |
| dp | `/labels/what` | 1 |
| dp | `/schema` | 1 |
| e2 | `/reading/sentence` | 1 |
| f0 | `/code_sha256/fd_f0_regrade.py` | 1 |
| f0 | `/extra_block/file` | 1 |
| f0 | `/extra_block/key` | 1 |
| f0 | `/extra_block/label` | 1 |
| f0 | `/extra_block/name` | 1 |
| f0 | `/extra_block/sha256` | 1 |
| f0 | `/labels/grade_matrix` | 1 |
| f0 | `/labels/what` | 1 |
| f0 | `/schema` | 1 |
| f0 | `/triggers/listed[]/truth` | 3 |
| f0 | `/truths[]/grade/p_below_floor` | 1 |
| f0 | `/truths[]/grade_matrix` | 18 |
| f0 | `/truths[]/p_parallel_lt_4p5/p_below_floor` | 1 |
| f0 | `/truths[]/sensitivity/matrix` | 2 |
| f0b | `/extra_block/file` | 1 |
| f0b | `/extra_block/key` | 1 |
| f0b | `/extra_block/name` | 1 |
| f0b | `/extra_block/sha256` | 1 |
| f0b | `/labels/grade_matrix` | 1 |
| f0b | `/labels/what` | 1 |
| f0b | `/triggers/listed[]/truth` | 1 |
| f0b | `/truths[]/grade_matrix` | 18 |
| f0b | `/truths[]/sensitivity/matrix` | 2 |
| f0b[nopl] | `/code_sha256/fd_f0_regrade.py` | 1 |
| f0b[nopl] | `/extra_block/file` | 1 |
| f0b[nopl] | `/extra_block/key` | 1 |
| f0b[nopl] | `/extra_block/name` | 1 |
| f0b[nopl] | `/extra_block/sha256` | 1 |
| f0b[nopl] | `/labels/grade_matrix` | 1 |
| f0b[nopl] | `/labels/what` | 1 |
| f0b[nopl] | `/triggers/listed[]/truth` | 2 |
| f0b[nopl] | `/truths[]/grade_matrix` | 18 |
| f0b[nopl] | `/truths[]/sensitivity/matrix` | 2 |
| f1 | `/extra_block/file` | 1 |
| f1 | `/extra_block/key` | 1 |
| f1 | `/extra_block/name` | 1 |
| f1 | `/extra_block/sha256` | 1 |
| f1 | `/labels/grade_matrix` | 1 |
| f1 | `/labels/what` | 1 |
| f1 | `/triggers/listed[]/truth` | 1 |
| f1 | `/truths[]/grade_matrix` | 22 |
| f1 | `/truths[]/sensitivity/matrix` | 6 |
| f1[nopl] | `/extra_block/file` | 1 |
| f1[nopl] | `/extra_block/key` | 1 |
| f1[nopl] | `/extra_block/name` | 1 |
| f1[nopl] | `/extra_block/sha256` | 1 |
| f1[nopl] | `/labels/grade_matrix` | 1 |
| f1[nopl] | `/labels/what` | 1 |
| f1[nopl] | `/triggers/listed[]/truth` | 2 |
| f1[nopl] | `/truths[]/grade_matrix` | 22 |
| f1[nopl] | `/truths[]/sensitivity/matrix` | 6 |
| fboot | `/constants/reported_matrix` | 1 |
| fboot | `/labels/units` | 1 |
| fboot[nopl] | `/constants/reported_matrix` | 1 |
| fboot[nopl] | `/labels/units` | 1 |
| fup | `/r04/item3_correlation_with_R04/rank/C_resp + C_PL5D` | 1 |
| fup | `/r04/item3_correlation_with_R04/rank/C_resp + C_PL5D + DeltaC_e` | 1 |
| fup | `/r04/item3_correlation_with_R04/rank/C_total + C_resp + C_PL5D` | 1 |
| fup | `/r04/item3_correlation_with_R04/rank/C_total + C_resp + C_PL5D + DeltaC_e` | 1 |
| fup | `/r04/item3_correlation_with_R04/under_prediction/genie_cv/matrix` | 1 |
| fup | `/r04/item3_correlation_with_R04/under_prediction/genie_mec/matrix` | 1 |
| fup | `/r04/item3_correlation_with_R04/under_prediction/mnvtune_v1/matrix` | 1 |
| fup | `/r04/item3_correlation_with_R04/under_prediction/nuwro/matrix` | 1 |
| fup | `/r04/item4_stage_g/genie_cv/matrix` | 1 |
| fup | `/r04/item4_stage_g/genie_mec/matrix` | 1 |
| fup | `/r04/item4_stage_g/gibuu/matrix` | 1 |
| fup | `/r04/item4_stage_g/mnvtune_v1/matrix` | 1 |
| fup | `/r04/item4_stage_g/nuwro/matrix` | 1 |
| fup | `/r04/item5_search/keys_searched/extra_block` | 1 |
| fup | `/r04/provenance_g_diag_top_modes/genie_cv[]/mode` | 2 |
| fup | `/r04/provenance_g_diag_top_modes/genie_cv[]/rank_of_R04_by_abs_loading` | 3 |
| fup | `/r04/provenance_g_diag_top_modes/genie_mec[]/mode` | 1 |
| fup | `/r04/provenance_g_diag_top_modes/genie_mec[]/rank_of_R04_by_abs_loading` | 3 |
| fup | `/r04/provenance_g_diag_top_modes/mnvtune_v1[]/mode` | 2 |
| fup | `/r04/provenance_g_diag_top_modes/mnvtune_v1[]/rank_of_R04_by_abs_loading` | 2 |
| fup | `/r04/provenance_g_diag_top_modes/nuwro[]/mode` | 3 |
| fup | `/r04/provenance_g_diag_top_modes/nuwro[]/rank_of_R04_by_abs_loading` | 3 |
| fup | `/sens/records[]/modes_needed/50%` | 16 |
| fup | `/sens/records[]/modes_needed/90%` | 31 |
| fup | `/sens/records[]/modes_needed/99%` | 35 |
| fup | `/sens/records[]/top_mode/leading_cells[]/cell` | 128 |
| fup | `/sens/records[]/top_mode/mode` | 21 |
| fup | `/sens/reported_matrix` | 1 |
| fup | `/sens/unchanged` | 1 |
| fup[nopl] | `/r04/item3_correlation_with_R04/rank/C_resp` | 1 |
| fup[nopl] | `/r04/item3_correlation_with_R04/rank/C_resp + DeltaC_e` | 1 |
| fup[nopl] | `/r04/item3_correlation_with_R04/rank/C_total + C_resp` | 1 |
| fup[nopl] | `/r04/item3_correlation_with_R04/rank/C_total + C_resp + DeltaC_e` | 1 |
| fup[nopl] | `/r04/item3_correlation_with_R04/under_prediction/genie_cv/matrix` | 1 |
| fup[nopl] | `/r04/item3_correlation_with_R04/under_prediction/genie_mec/matrix` | 1 |
| fup[nopl] | `/r04/item3_correlation_with_R04/under_prediction/mnvtune_v1/matrix` | 1 |
| fup[nopl] | `/r04/item3_correlation_with_R04/under_prediction/nuwro/matrix` | 1 |
| fup[nopl] | `/r04/item4_stage_g/genie_cv/matrix` | 1 |
| fup[nopl] | `/r04/item4_stage_g/genie_mec/matrix` | 1 |
| fup[nopl] | `/r04/item4_stage_g/gibuu/matrix` | 1 |
| fup[nopl] | `/r04/item4_stage_g/mnvtune_v1/matrix` | 1 |
| fup[nopl] | `/r04/item4_stage_g/nuwro/matrix` | 1 |
| fup[nopl] | `/r04/item5_search/keys_searched/extra_block` | 1 |
| fup[nopl] | `/r04/provenance_g_diag_top_modes/genie_cv[]/mode` | 1 |
| fup[nopl] | `/r04/provenance_g_diag_top_modes/genie_cv[]/rank_of_R04_by_abs_loading` | 3 |
| fup[nopl] | `/r04/provenance_g_diag_top_modes/genie_mec[]/mode` | 2 |
| fup[nopl] | `/r04/provenance_g_diag_top_modes/genie_mec[]/rank_of_R04_by_abs_loading` | 3 |
| fup[nopl] | `/r04/provenance_g_diag_top_modes/mnvtune_v1[]/mode` | 2 |
| fup[nopl] | `/r04/provenance_g_diag_top_modes/mnvtune_v1[]/rank_of_R04_by_abs_loading` | 2 |
| fup[nopl] | `/r04/provenance_g_diag_top_modes/nuwro[]/mode` | 1 |
| fup[nopl] | `/r04/provenance_g_diag_top_modes/nuwro[]/rank_of_R04_by_abs_loading` | 2 |
| fup[nopl] | `/sens/records[]/modes_needed/50%` | 15 |
| fup[nopl] | `/sens/records[]/modes_needed/90%` | 34 |
| fup[nopl] | `/sens/records[]/modes_needed/99%` | 37 |
| fup[nopl] | `/sens/records[]/top_mode/leading_cells[]/cell` | 92 |
| fup[nopl] | `/sens/records[]/top_mode/mode` | 14 |
| fup[nopl] | `/sens/reported_matrix` | 1 |
| fup[nopl] | `/sens/unchanged` | 1 |
| g | `/extra_block/file` | 1 |
| g | `/extra_block/key` | 1 |
| g | `/extra_block/name` | 1 |
| g | `/extra_block/sha256` | 1 |
| g | `/labels/covariance` | 1 |
| g | `/labels/reported` | 1 |
| g | `/predictions[]/reported_covariance` | 5 |
| g | `/predictions[]/shape_only/matrix` | 5 |
| g | `/predictions[]/total/matrix` | 5 |
| g | `/predictions[]/variant/label` | 5 |
| g0 | `/extra_block/file` | 1 |
| g0 | `/extra_block/key` | 1 |
| g0 | `/extra_block/name` | 1 |
| g0 | `/extra_block/sha256` | 1 |
| g0 | `/labels/covariance` | 1 |
| g0 | `/labels/reported` | 1 |
| g0 | `/predictions[]/reported_covariance` | 5 |
| g0 | `/predictions[]/shape_only/matrix` | 5 |
| g0 | `/predictions[]/total/matrix` | 5 |
| g0 | `/predictions[]/variant/label` | 5 |
| g0[nopl] | `/extra_block/file` | 1 |
| g0[nopl] | `/extra_block/key` | 1 |
| g0[nopl] | `/extra_block/name` | 1 |
| g0[nopl] | `/extra_block/sha256` | 1 |
| g0[nopl] | `/labels/covariance` | 1 |
| g0[nopl] | `/labels/reported` | 1 |
| g0[nopl] | `/predictions[]/reported_covariance` | 5 |
| g0[nopl] | `/predictions[]/shape_only/matrix` | 5 |
| g0[nopl] | `/predictions[]/total/matrix` | 5 |
| g0[nopl] | `/predictions[]/variant/label` | 5 |
| g[nopl] | `/extra_block/file` | 1 |
| g[nopl] | `/extra_block/key` | 1 |
| g[nopl] | `/extra_block/name` | 1 |
| g[nopl] | `/extra_block/sha256` | 1 |
| g[nopl] | `/labels/covariance` | 1 |
| g[nopl] | `/labels/reported` | 1 |
| g[nopl] | `/predictions[]/reported_covariance` | 5 |
| g[nopl] | `/predictions[]/shape_only/matrix` | 5 |
| g[nopl] | `/predictions[]/total/matrix` | 5 |
| g[nopl] | `/predictions[]/variant/label` | 5 |
| gch | `/generators/gibuu/CH/chi2/reported/shape_only/matrix` | 1 |
| gch | `/generators/gibuu/CH/chi2/reported/total/matrix` | 1 |
| gch | `/generators/gibuu/CH/chi2/without_C_PL5D/shape_only/matrix` | 1 |
| gch | `/generators/gibuu/CH/chi2/without_C_PL5D/total/matrix` | 1 |
| gch | `/generators/gibuu/CH_alt_weight/chi2/reported/shape_only/matrix` | 1 |
| gch | `/generators/gibuu/CH_alt_weight/chi2/reported/total/matrix` | 1 |
| gch | `/generators/gibuu/CH_alt_weight/chi2/without_C_PL5D/shape_only/matrix` | 1 |
| gch | `/generators/gibuu/CH_alt_weight/chi2/without_C_PL5D/total/matrix` | 1 |
| gch | `/generators/gibuu/CH_genie_hydrogen/chi2/reported/shape_only/matrix` | 1 |
| gch | `/generators/gibuu/CH_genie_hydrogen/chi2/reported/total/matrix` | 1 |
| gch | `/generators/gibuu/CH_genie_hydrogen/chi2/without_C_PL5D/shape_only/matrix` | 1 |
| gch | `/generators/gibuu/CH_genie_hydrogen/chi2/without_C_PL5D/total/matrix` | 1 |
| gch | `/generators/gibuu/carbon/chi2/reported/shape_only/matrix` | 1 |
| gch | `/generators/gibuu/carbon/chi2/reported/total/matrix` | 1 |
| gch | `/generators/gibuu/carbon/chi2/without_C_PL5D/shape_only/matrix` | 1 |
| gch | `/generators/gibuu/carbon/chi2/without_C_PL5D/total/matrix` | 1 |
| gch | `/generators/nuwro/CH/chi2/reported/shape_only/matrix` | 1 |
| gch | `/generators/nuwro/CH/chi2/reported/total/matrix` | 1 |
| gch | `/generators/nuwro/CH/chi2/without_C_PL5D/shape_only/matrix` | 1 |
| gch | `/generators/nuwro/CH/chi2/without_C_PL5D/total/matrix` | 1 |
| gch | `/generators/nuwro/CH_genie_hydrogen/chi2/reported/shape_only/matrix` | 1 |
| gch | `/generators/nuwro/CH_genie_hydrogen/chi2/reported/total/matrix` | 1 |
| gch | `/generators/nuwro/CH_genie_hydrogen/chi2/without_C_PL5D/shape_only/matrix` | 1 |
| gch | `/generators/nuwro/CH_genie_hydrogen/chi2/without_C_PL5D/total/matrix` | 1 |
| gch | `/generators/nuwro/carbon/chi2/reported/shape_only/matrix` | 1 |
| gch | `/generators/nuwro/carbon/chi2/reported/total/matrix` | 1 |
| gch | `/generators/nuwro/carbon/chi2/without_C_PL5D/shape_only/matrix` | 1 |
| gch | `/generators/nuwro/carbon/chi2/without_C_PL5D/total/matrix` | 1 |
| gdefs | `/generators/genie_cv/CH/analysis_definitions/chi2/reported/shape_only/matrix` | 1 |
| gdefs | `/generators/genie_cv/CH/analysis_definitions/chi2/reported/total/matrix` | 1 |
| gdefs | `/generators/genie_cv/CH/analysis_definitions/chi2/without_C_PL5D/shape_only/matrix` | 1 |
| gdefs | `/generators/genie_cv/CH/analysis_definitions/chi2/without_C_PL5D/total/matrix` | 1 |
| gdefs | `/generators/genie_cv/CH/generator_definitions/chi2/reported/shape_only/matrix` | 1 |
| gdefs | `/generators/genie_cv/CH/generator_definitions/chi2/reported/total/matrix` | 1 |
| gdefs | `/generators/genie_cv/CH/generator_definitions/chi2/without_C_PL5D/shape_only/matrix` | 1 |
| gdefs | `/generators/genie_cv/CH/generator_definitions/chi2/without_C_PL5D/total/matrix` | 1 |
| gdefs | `/generators/genie_mec/CH/analysis_definitions/chi2/reported/shape_only/matrix` | 1 |
| gdefs | `/generators/genie_mec/CH/analysis_definitions/chi2/reported/total/matrix` | 1 |
| gdefs | `/generators/genie_mec/CH/analysis_definitions/chi2/without_C_PL5D/shape_only/matrix` | 1 |
| gdefs | `/generators/genie_mec/CH/analysis_definitions/chi2/without_C_PL5D/total/matrix` | 1 |
| gdefs | `/generators/genie_mec/CH/generator_definitions/chi2/reported/shape_only/matrix` | 1 |
| gdefs | `/generators/genie_mec/CH/generator_definitions/chi2/reported/total/matrix` | 1 |
| gdefs | `/generators/genie_mec/CH/generator_definitions/chi2/without_C_PL5D/shape_only/matrix` | 1 |
| gdefs | `/generators/genie_mec/CH/generator_definitions/chi2/without_C_PL5D/total/matrix` | 1 |
| gdefs | `/generators/gibuu/CH/analysis_definitions/chi2/reported/shape_only/matrix` | 1 |
| gdefs | `/generators/gibuu/CH/analysis_definitions/chi2/reported/total/matrix` | 1 |
| gdefs | `/generators/gibuu/CH/analysis_definitions/chi2/without_C_PL5D/shape_only/matrix` | 1 |
| gdefs | `/generators/gibuu/CH/analysis_definitions/chi2/without_C_PL5D/total/matrix` | 1 |
| gdefs | `/generators/gibuu/CH/generator_definitions/chi2/reported/shape_only/matrix` | 1 |
| gdefs | `/generators/gibuu/CH/generator_definitions/chi2/reported/total/matrix` | 1 |
| gdefs | `/generators/gibuu/CH/generator_definitions/chi2/without_C_PL5D/shape_only/matrix` | 1 |
| gdefs | `/generators/gibuu/CH/generator_definitions/chi2/without_C_PL5D/total/matrix` | 1 |
| gdefs | `/generators/gibuu/carbon/analysis_definitions/chi2/reported/shape_only/matrix` | 1 |
| gdefs | `/generators/gibuu/carbon/analysis_definitions/chi2/reported/total/matrix` | 1 |
| gdefs | `/generators/gibuu/carbon/analysis_definitions/chi2/without_C_PL5D/shape_only/matrix` | 1 |
| gdefs | `/generators/gibuu/carbon/analysis_definitions/chi2/without_C_PL5D/total/matrix` | 1 |
| gdefs | `/generators/gibuu/carbon/generator_definitions/chi2/reported/shape_only/matrix` | 1 |
| gdefs | `/generators/gibuu/carbon/generator_definitions/chi2/reported/total/matrix` | 1 |
| gdefs | `/generators/gibuu/carbon/generator_definitions/chi2/without_C_PL5D/shape_only/matrix` | 1 |
| gdefs | `/generators/gibuu/carbon/generator_definitions/chi2/without_C_PL5D/total/matrix` | 1 |
| gdefs | `/generators/nuwro/CH/analysis_definitions/chi2/reported/shape_only/matrix` | 1 |
| gdefs | `/generators/nuwro/CH/analysis_definitions/chi2/reported/total/matrix` | 1 |
| gdefs | `/generators/nuwro/CH/analysis_definitions/chi2/without_C_PL5D/shape_only/matrix` | 1 |
| gdefs | `/generators/nuwro/CH/analysis_definitions/chi2/without_C_PL5D/total/matrix` | 1 |
| gdefs | `/generators/nuwro/CH/generator_definitions/chi2/reported/shape_only/matrix` | 1 |
| gdefs | `/generators/nuwro/CH/generator_definitions/chi2/reported/total/matrix` | 1 |
| gdefs | `/generators/nuwro/CH/generator_definitions/chi2/without_C_PL5D/shape_only/matrix` | 1 |
| gdefs | `/generators/nuwro/CH/generator_definitions/chi2/without_C_PL5D/total/matrix` | 1 |
| gdefs | `/generators/nuwro/carbon/analysis_definitions/chi2/reported/shape_only/matrix` | 1 |
| gdefs | `/generators/nuwro/carbon/analysis_definitions/chi2/reported/total/matrix` | 1 |
| gdefs | `/generators/nuwro/carbon/analysis_definitions/chi2/without_C_PL5D/shape_only/matrix` | 1 |
| gdefs | `/generators/nuwro/carbon/analysis_definitions/chi2/without_C_PL5D/total/matrix` | 1 |
| gdefs | `/generators/nuwro/carbon/generator_definitions/chi2/reported/shape_only/matrix` | 1 |
| gdefs | `/generators/nuwro/carbon/generator_definitions/chi2/reported/total/matrix` | 1 |
| gdefs | `/generators/nuwro/carbon/generator_definitions/chi2/without_C_PL5D/shape_only/matrix` | 1 |
| gdefs | `/generators/nuwro/carbon/generator_definitions/chi2/without_C_PL5D/total/matrix` | 1 |
| gnat | `/analysis_definitions/native_chi2/reported/shape_only/matrix` | 1 |
| gnat | `/analysis_definitions/native_chi2/reported/total/matrix` | 1 |
| gnat | `/analysis_definitions/native_chi2/without_C_PL5D/shape_only/matrix` | 1 |
| gnat | `/analysis_definitions/native_chi2/without_C_PL5D/total/matrix` | 1 |
| gnat | `/generator_definitions/combination_chi2/reported/shape_only/matrix` | 1 |
| gnat | `/generator_definitions/combination_chi2/reported/total/matrix` | 1 |
| gnat | `/generator_definitions/combination_chi2/without_C_PL5D/shape_only/matrix` | 1 |
| gnat | `/generator_definitions/combination_chi2/without_C_PL5D/total/matrix` | 1 |
| gnat | `/generator_definitions/native_chi2/reported/shape_only/matrix` | 1 |
| gnat | `/generator_definitions/native_chi2/reported/total/matrix` | 1 |
| gnat | `/generator_definitions/native_chi2/without_C_PL5D/shape_only/matrix` | 1 |
| gnat | `/generator_definitions/native_chi2/without_C_PL5D/total/matrix` | 1 |
| prr | `/ibu/K20/A7_nuwro/s991000/grade/p_below_floor` | 1 |
| prr | `/ibu/K20/closure_nuwro/s991000/grade/p_below_floor` | 1 |
| prr | `/ibu/K20/q3/s991000/grade/p_below_floor` | 1 |
| prr | `/ibu/K20/stage0c_gibuu/s991000/grade/p_below_floor` | 1 |
| prr | `/ibu/K4/A7_gibuu/s991000/grade/p_below_floor` | 1 |
| prr | `/ibu/K4/A7_gibuu/s994001/grade/p_below_floor` | 1 |
| prr | `/ibu/K4/A7_gibuu/s994002/grade/p_below_floor` | 1 |
| prr | `/ibu/K4/A7_gibuu/s994003/grade/p_below_floor` | 1 |
| prr | `/ibu/K4/A7_gibuu/s994004/grade/p_below_floor` | 1 |
| prr | `/ibu/K50/A7_nuwro/s991000/grade/p_below_floor` | 1 |
| prr | `/ibu/K50/W3/s991000/grade/p_below_floor` | 1 |
| prr | `/table/K2/A7_gibuu/s991000/grade/p_below_floor` | 1 |
| prr | `/table/O2/A7_nuwro/s991000/grade/p_below_floor` | 1 |
| prr | `/table/O2/stage0c_gibuu/s991000/grade/p_below_floor` | 1 |
| prr | `/table/O3/A7_gibuu/s991000/grade/p_below_floor` | 1 |
| prr | `/table/O4/A7_gibuu/s991000/grade/p_below_floor` | 1 |
| rsn | `/arms/WR/P6/top_directions[]/rank` | 2 |
| rsn | `/arms/WR/P7/nuwro/change_top_directions[]/rank` | 1 |
| rsn | `/arms/WR/P7/q3/change_top_directions[]/rank` | 2 |
| rsnregrade | `/arms/SM/records[]/grade/p_below_floor` | 1 |
| rsnregrade | `/arms/SM/records[]/in_sample/p_below_floor` | 1 |
| rsnregrade | `/wr_directions/data/directions/top[]/rank` | 2 |
| rsnregrade | `/wr_directions/nuwro/change/top[]/rank` | 1 |
| rsnregrade | `/wr_directions/q3/change/top[]/rank` | 2 |
| rsnregrade | `/wr_directions/tune_v1/change/top[]/rank` | 3 |
| sens2 | `/flux_top_mode_shares/predictions/genie_cv/0.1/dominant` | 1 |
| sens2 | `/flux_top_mode_shares/predictions/genie_cv/0/dominant` | 1 |
| sens2 | `/flux_top_mode_shares/predictions/genie_cv/alpha_0_mode_at_0.1/dominant` | 1 |
| sens2 | `/flux_top_mode_shares/predictions/genie_mec/0/dominant` | 1 |
| sens2 | `/flux_top_mode_shares/predictions/mnvtune_v1/0/dominant` | 1 |
| sens2 | `/flux_top_mode_shares/predictions/mnvtune_v1/0/mode` | 1 |
| sens2 | `/flux_top_mode_shares/predictions/nuwro/0.1/dominant` | 1 |
| sens2 | `/flux_top_mode_shares/predictions/nuwro/0.1/mode` | 1 |
| sens2 | `/flux_top_mode_shares/predictions/nuwro/0/dominant` | 1 |
| sens2 | `/flux_top_mode_shares/predictions/nuwro/0/mode` | 1 |
| sens2 | `/flux_top_mode_shares/predictions/nuwro/alpha_0_mode_at_0.1/dominant` | 1 |
| sens2 | `/referenced/g_followup_readout` | 1 |
| sens2 | `/sens/records[]/modes_needed/50%` | 23 |
| sens2 | `/sens/records[]/modes_needed/90%` | 60 |
| sens2 | `/sens/records[]/modes_needed/99%` | 58 |
| sens2 | `/sens/records[]/top_mode/leading_cells[]/cell` | 162 |
| sens2 | `/sens/records[]/top_mode/mode` | 20 |
| sens2 | `/sens/reported_matrix` | 1 |
| sens2 | `/sens/unchanged/detector` | 1 |
| sens2 | `/sens/unchanged/flux` | 1 |
| sens2 | `/sens/unchanged/lateral` | 1 |
| sens2[nopl] | `/flux_top_mode_shares/predictions/genie_cv/0.1/dominant` | 1 |
| sens2[nopl] | `/flux_top_mode_shares/predictions/genie_cv/0/dominant` | 1 |
| sens2[nopl] | `/flux_top_mode_shares/predictions/genie_cv/alpha_0_mode_at_0.1/dominant` | 1 |
| sens2[nopl] | `/flux_top_mode_shares/predictions/genie_mec/0/dominant` | 1 |
| sens2[nopl] | `/flux_top_mode_shares/predictions/mnvtune_v1/0/dominant` | 1 |
| sens2[nopl] | `/flux_top_mode_shares/predictions/nuwro/0.1/dominant` | 1 |
| sens2[nopl] | `/flux_top_mode_shares/predictions/nuwro/0/dominant` | 1 |
| sens2[nopl] | `/referenced/g_followup_readout` | 1 |
| sens2[nopl] | `/sens/records[]/modes_needed/50%` | 24 |
| sens2[nopl] | `/sens/records[]/modes_needed/90%` | 59 |
| sens2[nopl] | `/sens/records[]/modes_needed/99%` | 60 |
| sens2[nopl] | `/sens/records[]/top_mode/leading_cells[]/cell` | 130 |
| sens2[nopl] | `/sens/records[]/top_mode/mode` | 10 |
| sens2[nopl] | `/sens/reported_matrix` | 1 |
| sens2[nopl] | `/sens/unchanged/detector` | 1 |
| sens2[nopl] | `/sens/unchanged/flux` | 1 |
| sens2[nopl] | `/sens/unchanged/lateral` | 1 |

## 1b. make_values_fived16's guards that fail under V_F (each a note-side follow-up)

The V_F run uses a copy of the module whose assert statements record instead of raise (an in-process AST rewrite; no file changed); the OLD run uses the module unchanged, every guard passing.

- make_values_fived16.py:325: the method sentence's figures changed
- make_values_fived16.py:443: (no message) `assert big[1:] == ("nopl", "genie_mec", "shape_only") and abs(big[0] - e2["delta_max_abs"]) < 1e-12`
- make_values_fived16.py:455: GiBUU's rise no longer comes from C_model's carbon shape ratios
- make_values_fived16.py:583: sec_fived16 :47's readings changed: QA at every rho, the others below a correlation
- make_values_fived16.py:325: the method sentence's figures changed
- make_values_fived16.py:443: (no message) `assert big[1:] == ("nopl", "genie_mec", "shape_only") and abs(big[0] - e2["delta_max_abs"]) < 1e-12`
- make_values_fived16.py:455: GiBUU's rise no longer comes from C_model's carbon shape ratios
- make_values_fived16.py:583: sec_fived16 :47's readings changed: QA at every rho, the others below a correlation
- make_values_fived16.py:1367: B0 flags exactly the two flagged truths
- make_values_fived16.py:1377: K2
- make_values_fived16.py:1377: K10
- make_values_fived16.py:1377: K20
- make_values_fived16.py:1377: K50
- make_values_fived16.py:1377: C400
- make_values_fived16.py:1377: C1000
- make_values_fived16.py:1377: MCq
- make_values_fived16.py:1377: O4r
- make_values_fived16.py:1377: O4
- make_values_fived16.py:1377: O3
- make_values_fived16.py:1612: (no message) `assert sm["P1"]["class"] == "more flagged" and set(sm["P1"]["listed"]) - set(sm["P1"]["listed_nominal"]) == {"A7_nuwro"}`
- make_values_fived16.py:1614: flagged by p alone, no cell beyond 2 sigma
- make_values_fived16.py:1634: the RSN values differ from the approved draft: ['rsn-g6-sig-hi', 'rsn-g6-sig-lo', 'rsn-sm-nuwro-p', 'rsn-sm-sig-hi', 'rsn-sm-sig-lo', 'rsn-sm-sig-med', 'rsn-wr-sig-max']

## 2. Every moved \fvval key, OLD -> V_F (with print sites)

1804 of 4031 keys move; 698 of them are printed.

| key | OLD | V_F | printed at |
|---|---|---|---|
| `corr-R01-R00` | 0.69 | 0.70 | appC_supplementary.tex:193, sec_fived16.tex:181 |
| `corr-R02-R01` | 0.30 | 0.31 | appC_supplementary.tex:194, sec_fived16.tex:182 |
| `corr-R03-R00` | 0.53 | 0.51 | appC_supplementary.tex:195, sec_fived16.tex:183 |
| `corr-R03-R02` | 0.81 | 0.77 | appC_supplementary.tex:195, sec_fived16.tex:183 |
| `corr-R04-R02` | 0.15 | 0.16 | appC_supplementary.tex:196, sec_fived16.tex:184 |
| `corr-R05-R01` | 0.70 | 0.67 | appC_supplementary.tex:197, sec_fived16.tex:185 |
| `corr-R05-R02` | $-$0.03 | $-$0.00 | appC_supplementary.tex:197, sec_fived16.tex:185 |
| `corr-R05-R03` | $-$0.14 | $-$0.11 | appC_supplementary.tex:197, sec_fived16.tex:185 |
| `corr-R05-R04` | 0.57 | 0.56 | appC_supplementary.tex:197, sec_fived16.tex:185 |
| `corr-R06-R00` | 0.36 | 0.34 | appC_supplementary.tex:198, sec_fived16.tex:186 |
| `corr-R06-R01` | 0.51 | 0.47 | appC_supplementary.tex:198, sec_fived16.tex:186 |
| `corr-R06-R02` | 0.64 | 0.61 | appC_supplementary.tex:198, sec_fived16.tex:186 |
| `corr-R06-R03` | 0.57 | 0.52 | appC_supplementary.tex:198, sec_fived16.tex:186 |
| `corr-R06-R04` | 0.59 | 0.55 | appC_supplementary.tex:198, sec_fived16.tex:186 |
| `corr-R06-R05` | 0.43 | 0.41 | appC_supplementary.tex:198, sec_fived16.tex:186 |
| `corr-R07-R00` | 0.41 | 0.38 | appC_supplementary.tex:199, sec_fived16.tex:187 |
| `corr-R07-R01` | 0.40 | 0.38 | appC_supplementary.tex:199, sec_fived16.tex:187 |
| `corr-R07-R02` | 0.40 | 0.37 | appC_supplementary.tex:199, sec_fived16.tex:187 |
| `corr-R07-R03` | 0.75 | 0.74 | appC_supplementary.tex:199, sec_fived16.tex:187 |
| `corr-R07-R04` | 0.55 | 0.51 | appC_supplementary.tex:199, sec_fived16.tex:187 |
| `corr-R07-R05` | 0.19 | 0.20 | appC_supplementary.tex:199, sec_fived16.tex:187 |
| `corr-R07-R06` | 0.64 | 0.62 | appC_supplementary.tex:199, sec_fived16.tex:187 |
| `corr-R08-R00` | 0.66 | 0.64 | appC_supplementary.tex:200, sec_fived16.tex:188 |
| `corr-R08-R01` | 0.30 | 0.31 | appC_supplementary.tex:200, sec_fived16.tex:188 |
| `corr-R08-R02` | 0.24 | 0.23 | appC_supplementary.tex:200, sec_fived16.tex:188 |
| `corr-R08-R03` | 0.31 | 0.29 | appC_supplementary.tex:200, sec_fived16.tex:188 |
| `corr-R08-R04` | 0.73 | 0.72 | appC_supplementary.tex:200, sec_fived16.tex:188 |
| `corr-R08-R05` | 0.13 | 0.15 | appC_supplementary.tex:200, sec_fived16.tex:188 |
| `corr-R08-R06` | 0.31 | 0.27 | appC_supplementary.tex:200, sec_fived16.tex:188 |
| `corr-R08-R07` | 0.40 | 0.37 | appC_supplementary.tex:200, sec_fived16.tex:188 |
| `corr-R09-R00` | 0.19 | 0.20 | appC_supplementary.tex:201, sec_fived16.tex:189 |
| `corr-R09-R02` | $-$0.24 | $-$0.22 | appC_supplementary.tex:201, sec_fived16.tex:189 |
| `corr-R09-R03` | $-$0.07 | $-$0.05 | appC_supplementary.tex:201, sec_fived16.tex:189 |
| `corr-R09-R04` | 0.77 | 0.78 | appC_supplementary.tex:201, sec_fived16.tex:189 |
| `corr-R09-R05` | 0.65 | 0.62 | appC_supplementary.tex:201, sec_fived16.tex:189 |
| `corr-R09-R06` | 0.42 | 0.39 | appC_supplementary.tex:201, sec_fived16.tex:189 |
| `corr-R09-R07` | 0.48 | 0.44 | appC_supplementary.tex:201, sec_fived16.tex:189 |
| `corr-R09-R08` | 0.40 | 0.41 | appC_supplementary.tex:201, sec_fived16.tex:189 |
| `corr-R10-R00` | 0.37 | 0.36 | appC_supplementary.tex:202, sec_fived16.tex:190 |
| `corr-R10-R01` | 0.13 | 0.14 | appC_supplementary.tex:202, sec_fived16.tex:190 |
| `corr-R10-R02` | 0.73 | 0.70 | appC_supplementary.tex:202, sec_fived16.tex:190 |
| `corr-R10-R03` | 0.42 | 0.39 | appC_supplementary.tex:202, sec_fived16.tex:190 |
| `corr-R10-R06` | 0.56 | 0.47 | appC_supplementary.tex:202, sec_fived16.tex:190 |
| `corr-R10-R07` | 0.21 | 0.16 | appC_supplementary.tex:202, sec_fived16.tex:190 |
| `corr-R10-R09` | $-$0.06 | $-$0.04 | appC_supplementary.tex:202, sec_fived16.tex:190 |
| `corr-R11-R01` | 0.07 | 0.06 | appC_supplementary.tex:203, sec_fived16.tex:191 |
| `corr-R11-R02` | $-$0.40 | $-$0.37 | appC_supplementary.tex:203, sec_fived16.tex:191 |
| `corr-R11-R03` | $-$0.43 | $-$0.39 | appC_supplementary.tex:203, sec_fived16.tex:191 |
| `corr-R11-R05` | 0.46 | 0.43 | appC_supplementary.tex:203, sec_fived16.tex:191 |
| `corr-R11-R07` | $-$0.15 | $-$0.14 | appC_supplementary.tex:203, sec_fived16.tex:191 |
| `corr-R11-R08` | 0.16 | 0.17 | appC_supplementary.tex:203, sec_fived16.tex:191 |
| `corr-R11-R10` | 0.14 | 0.17 | appC_supplementary.tex:203, sec_fived16.tex:191 |
| `corr-R12-R00` | 0.02 | 0.01 | appC_supplementary.tex:204, sec_fived16.tex:192 |
| `corr-R12-R04` | 0.73 | 0.72 | appC_supplementary.tex:204, sec_fived16.tex:192 |
| `corr-R12-R05` | 0.22 | 0.21 | appC_supplementary.tex:204, sec_fived16.tex:192 |
| `corr-R12-R06` | 0.35 | 0.32 | appC_supplementary.tex:204, sec_fived16.tex:192 |
| `corr-R12-R07` | 0.26 | 0.25 | appC_supplementary.tex:204, sec_fived16.tex:192 |
| `corr-R12-R08` | 0.60 | 0.58 | appC_supplementary.tex:204, sec_fived16.tex:192 |
| `corr-R12-R09` | 0.51 | 0.52 | appC_supplementary.tex:204, sec_fived16.tex:192 |
| `corr-R12-R10` | 0.29 | 0.28 | appC_supplementary.tex:204, sec_fived16.tex:192 |
| `corr-R13-R00` | 0.03 | 0.02 | appC_supplementary.tex:205, sec_fived16.tex:193 |
| `corr-R13-R02` | $-$0.26 | $-$0.25 | appC_supplementary.tex:205, sec_fived16.tex:193 |
| `corr-R13-R03` | $-$0.38 | $-$0.37 | appC_supplementary.tex:205, sec_fived16.tex:193 |
| `corr-R13-R04` | 0.51 | 0.50 | appC_supplementary.tex:205, sec_fived16.tex:193 |
| `corr-R13-R05` | 0.50 | 0.48 | appC_supplementary.tex:205, sec_fived16.tex:193 |
| `corr-R13-R06` | 0.13 | 0.12 | appC_supplementary.tex:205, sec_fived16.tex:193 |
| `corr-R13-R10` | 0.34 | 0.33 | appC_supplementary.tex:205, sec_fived16.tex:193 |
| `corr-R13-R11` | 0.92 | 0.89 | appC_supplementary.tex:205, sec_fived16.tex:193 |
| `corr-R13-R12` | 0.46 | 0.45 | appC_supplementary.tex:205, sec_fived16.tex:193 |
| `corr-R14-R00` | 0.24 | 0.25 | appC_supplementary.tex:206, sec_fived16.tex:194 |
| `corr-R14-R01` | 0.52 | 0.51 | appC_supplementary.tex:206, sec_fived16.tex:194 |
| `corr-R14-R03` | 0.21 | 0.20 | appC_supplementary.tex:206, sec_fived16.tex:194 |
| `corr-R14-R04` | 0.74 | 0.75 | appC_supplementary.tex:206, sec_fived16.tex:194 |
| `corr-R14-R05` | 0.65 | 0.63 | appC_supplementary.tex:206, sec_fived16.tex:194 |
| `corr-R14-R06` | 0.65 | 0.59 | appC_supplementary.tex:206, sec_fived16.tex:194 |
| `corr-R14-R07` | 0.48 | 0.44 | appC_supplementary.tex:206, sec_fived16.tex:194 |
| `corr-R14-R08` | 0.38 | 0.40 | appC_supplementary.tex:206, sec_fived16.tex:194 |
| `corr-R14-R09` | 0.72 | 0.73 | appC_supplementary.tex:206, sec_fived16.tex:194 |
| `corr-R14-R10` | 0.26 | 0.25 | appC_supplementary.tex:206, sec_fived16.tex:194 |
| `corr-R14-R11` | 0.11 | 0.12 | appC_supplementary.tex:206, sec_fived16.tex:194 |
| `corr-R15-R02` | 0.61 | 0.58 | appC_supplementary.tex:207, sec_fived16.tex:195 |
| `corr-R15-R03` | 0.43 | 0.40 | appC_supplementary.tex:207, sec_fived16.tex:195 |
| `corr-R15-R04` | 0.52 | 0.51 | appC_supplementary.tex:207, sec_fived16.tex:195 |
| `corr-R15-R05` | 0.11 | 0.10 | appC_supplementary.tex:207, sec_fived16.tex:195 |
| `corr-R15-R06` | 0.71 | 0.65 | appC_supplementary.tex:207, sec_fived16.tex:195 |
| `corr-R15-R07` | 0.41 | 0.37 | appC_supplementary.tex:207, sec_fived16.tex:195 |
| `corr-R15-R08` | 0.32 | 0.30 | appC_supplementary.tex:207, sec_fived16.tex:195 |
| `corr-R15-R09` | 0.20 | 0.21 | appC_supplementary.tex:207, sec_fived16.tex:195 |
| `corr-R15-R10` | 0.83 | 0.81 | appC_supplementary.tex:207, sec_fived16.tex:195 |
| `corr-R15-R11` | $-$0.04 | $-$0.02 | appC_supplementary.tex:207, sec_fived16.tex:195 |
| `corr-R15-R12` | 0.54 | 0.53 | appC_supplementary.tex:207, sec_fived16.tex:195 |
| `corr-R15-R14` | 0.52 | 0.51 | appC_supplementary.tex:207, sec_fived16.tex:195 |
| `cr-QA-nopl-reading` | agree below a correlation | agree | sec_fived16.tex:67 |
| `cr-QA-nopl-rhostar` | 0.9999 | 1.0010 | sec_fived16.tex:67 |
| `cr-QA-rhostar` | 1.0003 | 1.0023 | sec_fived16.tex:67 |
| `cr-QA-sig16` | 0.5464 | 0.5693 | sec_fived16.tex:67 |
| `cr-QA-z0` | +0.015 | +0.014 | sec_fived16.tex:67 |
| `cr-QB-nopl-rhostar` | 1.0115 | 1.0049 | sec_fived16.tex:68 |
| `cr-QB-reading` | agree below a correlation | agree | sec_fived16.tex:68 |
| `cr-QB-rhostar` | 0.9997 | 1.0005 | appC_supplementary.tex:212, records_r05_sixteen.tex:244, sec_fived16.tex:56 ... |
| `cr-QB-sig16` | 0.3276 | 0.3406 | sec_fived16.tex:68 |
| `cr-QB-z0` | -0.032 | -0.031 | sec_fived16.tex:68 |
| `cr-QC-nopl-rhostar` | 0.9904 | 0.9895 | sec_fived16.tex:69 |
| `cr-QC-rhostar` | 0.9902 | 0.9921 | appC_supplementary.tex:212, records_r05_sixteen.tex:244, sec_fived16.tex:56 ... |
| `cr-QC-sig16` | 0.3565 | 0.3698 | sec_fived16.tex:69 |
| `cr-QC-z0` | -0.202 | -0.198 | sec_fived16.tex:69 |
| `cr-QD-nopl-reading` | agree | agree below a correlation | sec_fived16.tex:70 |
| `cr-QD-nopl-rhostar` | 1.0035 | 0.9999 | sec_fived16.tex:70 |
| `cr-QD-rhostar` | 0.9982 | 0.9981 | sec_fived16.tex:70 |
| `cr-QD-sig16` | 0.5036 | 0.5228 | sec_fived16.tex:70 |
| `cr-QD-z0` | +0.092 | +0.090 | sec_fived16.tex:70 |
| `diag-gcv-reported-modes50` | 2 | 3 | sec_fived16_gen.tex:124 |
| `diag-gcv-reported-modes90` | 6 | 8 | sec_fived16_gen.tex:124 |
| `diag-gcv-reported-modes99` | 11 | 13 | sec_fived16_gen.tex:124 |
| `diag-gcv-reported-top-block` | interaction | [PLACEHOLDER label for C_resp + C_PL5D + DeltaC_e] | sec_fived16_gen.tex:124 |
| `diag-gcv-reported-top-share` | 31.8 | 24.7 | sec_fived16_gen.tex:124 |
| `diag-gcv-reported-top-sigma` | 3.24 | 4.25 | sec_fived16_gen.tex:124 |
| `diag-gibuu-reported-modes90` | 5 | 4 | sec_fived16_gen.tex:127 |
| `diag-gibuu-reported-modes99` | 7 | 6 | sec_fived16_gen.tex:127 |
| `diag-gibuu-reported-top-share` | 37.5 | 37.1 | sec_fived16_gen.tex:127 |
| `diag-gibuu-reported-top-sigma` | 14.02 | 14.61 | sec_fived16_gen.tex:127 |
| `diag-gmec-reported-modes90` | 5 | 7 | sec_fived16_gen.tex:125 |
| `diag-gmec-reported-modes99` | 9 | 11 | sec_fived16_gen.tex:125 |
| `diag-gmec-reported-top-block` | interaction | [PLACEHOLDER label for C_resp + C_PL5D + DeltaC_e] | sec_fived16_gen.tex:125 |
| `diag-gmec-reported-top-share` | 44.9 | 39.4 | sec_fived16_gen.tex:125 |
| `diag-gmec-reported-top-sigma` | 1.18 | 1.57 | sec_fived16_gen.tex:125 |
| `diag-nuwro-reported-modes90` | 7 | 8 | sec_fived16_gen.tex:126 |
| `diag-nuwro-reported-top-block` | interaction | [PLACEHOLDER label for C_resp + C_PL5D + DeltaC_e] | sec_fived16_gen.tex:126 |
| `diag-nuwro-reported-top-share` | 24.7 | 21.8 | sec_fived16_gen.tex:126 |
| `diag-nuwro-reported-top-sigma` | 2.19 | 7.45 | sec_fived16_gen.tex:126 |
| `diag-tune-reported-modes90` | 5 | 6 | sec_fived16_gen.tex:128 |
| `diag-tune-reported-modes99` | 10 | 12 | sec_fived16_gen.tex:128 |
| `diag-tune-reported-top-block` | detector | [PLACEHOLDER label for C_resp + C_PL5D + DeltaC_e] | sec_fived16_gen.tex:128 |
| `diag-tune-reported-top-share` | 30.1 | 42.8 | sec_fived16_gen.tex:128 |
| `diag-tune-reported-top-sigma` | 1.13 | 1.46 | sec_fived16_gen.tex:128 |
| `e2-dmax` | 6.07 | 10.81 | records_r05_sixteen.tex:396, records_r05_sixteen.tex:403 |
| `e2-nopl-gcv-shape_only-ch` | 109.68 | 60.27 | sec_fived16_gen.tex:195 |
| `e2-nopl-gcv-shape_only-dch` | -0.64 | -2.84 | sec_fived16_gen.tex:195 |
| `e2-nopl-gcv-shape_only-x0` | 126.64 | 71.99 | sec_fived16_gen.tex:195 |
| `e2-nopl-gcv-shape_only-x1` | 110.32 | 63.12 | sec_fived16_gen.tex:195 |
| `e2-nopl-gcv-shape_only-x2` | 107.82 | 61.64 | sec_fived16_gen.tex:195 |
| `e2-nopl-gcv-total-ch` | 110.40 | 62.58 | sec_fived16_gen.tex:194 |
| `e2-nopl-gcv-total-dch` | -0.82 | -2.68 | sec_fived16_gen.tex:194 |
| `e2-nopl-gcv-total-x0` | 126.90 | 73.52 | sec_fived16_gen.tex:194 |
| `e2-nopl-gcv-total-x1` | 111.22 | 65.26 | sec_fived16_gen.tex:194 |
| `e2-nopl-gcv-total-x2` | 108.86 | 63.91 | sec_fived16_gen.tex:194 |
| `e2-nopl-gibuu-shape_only-ch` | 20.61 | 18.39 | sec_fived16_gen.tex:201 |
| `e2-nopl-gibuu-shape_only-dch` | -4.05 | -2.32 | sec_fived16_gen.tex:201 |
| `e2-nopl-gibuu-shape_only-x0` | 143.87 | 84.41 | sec_fived16_gen.tex:201 |
| `e2-nopl-gibuu-shape_only-x1` | 24.66 | 20.71 | sec_fived16_gen.tex:201 |
| `e2-nopl-gibuu-shape_only-x2` | 21.20 | 17.49 | sec_fived16_gen.tex:201 |
| `e2-nopl-gibuu-total-ch` | 57.73 | 50.40 | sec_fived16_gen.tex:200 |
| `e2-nopl-gibuu-total-dch` | -3.68 | -1.82 | sec_fived16_gen.tex:200 |
| `e2-nopl-gibuu-total-x0` | 175.39 | 110.73 | sec_fived16_gen.tex:200 |
| `e2-nopl-gibuu-total-x1` | 61.41 | 52.22 | sec_fived16_gen.tex:200 |
| `e2-nopl-gibuu-total-x2` | 58.95 | 50.08 | sec_fived16_gen.tex:200 |
| `e2-nopl-gmec-shape_only-ch` | 257.67 | 148.58 | sec_fived16_gen.tex:197 |
| `e2-nopl-gmec-shape_only-dch` | -6.07 | -10.26 | sec_fived16_gen.tex:197 |
| `e2-nopl-gmec-shape_only-x0` | 297.63 | 179.28 | sec_fived16_gen.tex:197 |
| `e2-nopl-gmec-shape_only-x1` | 263.74 | 158.84 | sec_fived16_gen.tex:197 |
| `e2-nopl-gmec-shape_only-x2` | 258.24 | 154.98 | sec_fived16_gen.tex:197 |
| `e2-nopl-gmec-total-ch` | 273.15 | 153.57 | sec_fived16_gen.tex:196 |
| `e2-nopl-gmec-total-dch` | -4.79 | -10.81 | sec_fived16_gen.tex:196 |
| `e2-nopl-gmec-total-x0` | 316.63 | 186.62 | sec_fived16_gen.tex:196 |
| `e2-nopl-gmec-total-x1` | 277.94 | 164.38 | sec_fived16_gen.tex:196 |
| `e2-nopl-gmec-total-x2` | 271.63 | 160.18 | sec_fived16_gen.tex:196 |
| `e2-nopl-nuwro-shape_only-ch` | 183.18 | 114.56 | sec_fived16_gen.tex:199 |
| `e2-nopl-nuwro-shape_only-dch` | +2.66 | +0.20 | sec_fived16_gen.tex:199 |
| `e2-nopl-nuwro-shape_only-x0` | 192.38 | 116.66 | sec_fived16_gen.tex:199 |
| `e2-nopl-nuwro-shape_only-x1` | 180.52 | 114.36 | sec_fived16_gen.tex:199 |
| `e2-nopl-nuwro-shape_only-x2` | 179.84 | 114.04 | sec_fived16_gen.tex:199 |
| `e2-nopl-nuwro-total-ch` | 183.20 | 116.05 | sec_fived16_gen.tex:198 |
| `e2-nopl-nuwro-total-dch` | +2.58 | +0.21 | sec_fived16_gen.tex:198 |
| `e2-nopl-nuwro-total-x0` | 192.42 | 118.44 | sec_fived16_gen.tex:198 |
| `e2-nopl-nuwro-total-x1` | 180.62 | 115.84 | sec_fived16_gen.tex:198 |
| `e2-nopl-nuwro-total-x2` | 179.93 | 115.47 | sec_fived16_gen.tex:198 |
| `e2-sig-nopl-fall` | 9.5 | 8.9 | records_r05_sixteen.tex:290 |
| `e2-sig-with-carbon` | 0.1405 | 0.1444 | records_r05_sixteen.tex:290 |
| `e2-sig-with-ch` | 0.1273 | 0.1316 | records_r05_sixteen.tex:290 |
| `e2-sig-with-fall` | 9.4 | 8.9 | records_r05_sixteen.tex:290 |
| `e2-with-gcv-shape_only-ch` | 101.58 | 57.04 | sec_fived16_gen.tex:185 |
| `e2-with-gcv-shape_only-dch` | -0.54 | -2.26 | sec_fived16_gen.tex:185 |
| `e2-with-gcv-shape_only-x0` | 118.10 | 68.18 | sec_fived16_gen.tex:185 |
| `e2-with-gcv-shape_only-x1` | 102.11 | 59.30 | sec_fived16_gen.tex:185 |
| `e2-with-gcv-shape_only-x2` | 99.69 | 57.81 | sec_fived16_gen.tex:185 |
| `e2-with-gcv-total-ch` | 106.27 | 61.69 | sec_fived16_gen.tex:184 |
| `e2-with-gcv-total-dch` | -0.92 | -2.33 | records_r05_sixteen.tex:396, sec_fived16_gen.tex:184 |
| `e2-with-gcv-total-x0` | 121.76 | 72.04 | sec_fived16_gen.tex:184 |
| `e2-with-gcv-total-x1` | 107.18 | 64.01 | sec_fived16_gen.tex:184 |
| `e2-with-gcv-total-x2` | 104.98 | 62.67 | sec_fived16_gen.tex:184 |
| `e2-with-gibuu-shape_only-ch` | 18.61 | 16.81 | sec_fived16_gen.tex:191 |
| `e2-with-gibuu-shape_only-dch` | -3.58 | -2.11 | sec_fived16_gen.tex:191 |
| `e2-with-gibuu-shape_only-x0` | 139.76 | 82.88 | sec_fived16_gen.tex:191 |
| `e2-with-gibuu-shape_only-x1` | 22.19 | 18.92 | sec_fived16_gen.tex:191 |
| `e2-with-gibuu-shape_only-x2` | 19.00 | 15.87 | sec_fived16_gen.tex:191 |
| `e2-with-gibuu-total-ch` | 45.10 | 40.35 | sec_fived16_gen.tex:143, sec_fived16_gen.tex:190 |
| `e2-with-gibuu-total-dch` | -2.68 | -1.45 | records_r05_sixteen.tex:396, sec_fived16_gen.tex:190 |
| `e2-with-gibuu-total-x0` | 166.83 | 104.69 | records_r05_sixteen.tex:408, sec_fived16_gen.tex:190 |
| `e2-with-gibuu-total-x1` | 47.78 | 41.80 | records_r05_sixteen.tex:408, sec_fived16_gen.tex:190 |
| `e2-with-gibuu-total-x2` | 45.50 | 39.66 | sec_fived16_gen.tex:190 |
| `e2-with-gmec-shape_only-ch` | 223.33 | 132.40 | sec_fived16_gen.tex:187 |
| `e2-with-gmec-shape_only-dch` | -5.67 | -7.93 | sec_fived16_gen.tex:187 |
| `e2-with-gmec-shape_only-x0` | 261.03 | 160.13 | sec_fived16_gen.tex:187 |
| `e2-with-gmec-shape_only-x1` | 229.00 | 140.33 | sec_fived16_gen.tex:187 |
| `e2-with-gmec-shape_only-x2` | 223.82 | 136.51 | sec_fived16_gen.tex:187 |
| `e2-with-gmec-total-ch` | 223.53 | 132.41 | sec_fived16_gen.tex:186 |
| `e2-with-gmec-total-dch` | -5.56 | -7.93 | records_r05_sixteen.tex:396, sec_fived16_gen.tex:186 |
| `e2-with-gmec-total-x0` | 261.54 | 160.25 | sec_fived16_gen.tex:186 |
| `e2-with-gmec-total-x1` | 229.09 | 140.34 | sec_fived16_gen.tex:186 |
| `e2-with-gmec-total-x2` | 223.88 | 136.51 | sec_fived16_gen.tex:186 |
| `e2-with-nuwro-shape_only-ch` | 108.07 | 75.71 | sec_fived16_gen.tex:189 |
| `e2-with-nuwro-shape_only-dch` | +0.54 | +0.13 | sec_fived16_gen.tex:189 |
| `e2-with-nuwro-shape_only-x0` | 120.84 | 78.33 | sec_fived16_gen.tex:189 |
| `e2-with-nuwro-shape_only-x1` | 107.52 | 75.58 | sec_fived16_gen.tex:189 |
| `e2-with-nuwro-shape_only-x2` | 106.77 | 75.19 | sec_fived16_gen.tex:189 |
| `e2-with-nuwro-total-ch` | 127.86 | 91.48 | sec_fived16_gen.tex:188 |
| `e2-with-nuwro-total-dch` | +0.17 | +0.16 | records_r05_sixteen.tex:396, sec_fived16_gen.tex:188 |
| `e2-with-nuwro-total-x0` | 140.25 | 94.77 | sec_fived16_gen.tex:188 |
| `e2-with-nuwro-total-x1` | 127.69 | 91.32 | sec_fived16_gen.tex:188 |
| `e2-with-nuwro-total-x2` | 126.87 | 90.81 | sec_fived16_gen.tex:188 |
| `eav-cellmax` | 0.19 | 0.17 | records_r02_method.tex:82, sec2_method.tex:59, sec_3d.tex:36 |
| `eav-cellmax-nopl` | 0.21 | 0.19 | records_r04_higherdim.tex:56 |
| `eav-coherent` | 0.42 | 0.32 | records_r02_method.tex:82, records_r04_higherdim.tex:64, sec_3d.tex:36 |
| `eav-coherent-nopl` | 0.42 | 0.32 | records_r04_higherdim.tex:56 |
| `f0-A7_genie_cv-chi2` | 17.37 | 6.38 | sec_q3_fived16.tex:18 |
| `f0-A7_genie_cv-p` | 0.36 | 0.98 | sec_q3_fived16.tex:18 |
| `f0-A7_genie_mec-chi2` | 16.18 | 5.76 | sec_q3_fived16.tex:19 |
| `f0-A7_genie_mec-p` | 0.44 | 0.99 | sec_q3_fived16.tex:19 |
| `f0-A7_gibuu-cells` | R02, R06, R07 | R02, R06 | sec_q3_fived16.tex:26 |
| `f0-A7_gibuu-chi2` | 246.75 | 108.32 | sec_q3_fived16.tex:26 |
| `f0-A7_gibuu-p` | <10^{-30} | 9.3\times10^{-16} | sec_q3_fived16.tex:26 |
| `f0-A7_mnvtune-chi2` | 0.01 | 0.00 | sec_q3_fived16.tex:17 |
| `f0-A7_nuwro-chi2` | 29.96 | 13.91 | sec_q3_fived16.tex:21 |
| `f0-A7_nuwro-p` | 0.018 | 0.61 | sec_q3_fived16.tex:21 |
| `f0-W1-chi2` | 5.69 | 2.97 | sec_q3_fived16.tex:22 |
| `f0-W1-p` | 0.99 | 1.00 | sec_q3_fived16.tex:22 |
| `f0-W2-chi2` | 0.77 | 0.35 | sec_q3_fived16.tex:20 |
| `f0-W3-chi2` | 36.19 | 15.65 | sec_q3_fived16.tex:23 |
| `f0-W3-p` | 0.0027 | 0.48 | sec_q3_fived16.tex:23 |
| `f0-closure_nuwro-chi2` | 13.08 | 5.74 | sec_q3_fived16.tex:24 |
| `f0-closure_nuwro-p` | 0.67 | 0.99 | sec_q3_fived16.tex:24 |
| `f0-q3-chi2` | 59.83 | 29.70 | sec_q3_fived16.tex:27 |
| `f0-q3-p` | 5.6\times10^{-7} | 0.02 | sec_q3_fived16.tex:27 |
| `f0-stage0c_gibuu-cells` | R06 | --- | sec_q3_fived16.tex:25 |
| `f0-stage0c_gibuu-chi2` | 35.75 | 16.94 | sec_q3_fived16.tex:25 |
| `f0-stage0c_gibuu-p` | 0.0031 | 0.39 | sec_q3_fived16.tex:25 |
| `f0b-A7_genie_cv-chi2` | 15.58 | 6.09 | sec_q3_fived16.tex:18 |
| `f0b-A7_genie_cv-chi2-nopl` | 16.14 | 6.20 | sec_q3_fived16.tex:18 |
| `f0b-A7_genie_cv-p` | 0.48 | 0.99 | sec_q3_fived16.tex:18 |
| `f0b-A7_genie_cv-p-nopl` | 0.44 | 0.99 | sec_q3_fived16.tex:18 |
| `f0b-A7_genie_mec-chi2` | 13.65 | 5.27 | sec_q3_fived16.tex:19 |
| `f0b-A7_genie_mec-chi2-nopl` | 14.54 | 5.40 | sec_q3_fived16.tex:19 |
| `f0b-A7_genie_mec-in_sample-chi2` | 10.89 | 4.32 | records_r04_higherdim.tex:593 |
| `f0b-A7_genie_mec-in_sample-p` | 0.82 | 1.00 | records_r04_higherdim.tex:593 |
| `f0b-A7_genie_mec-p` | 0.62 | 0.99 | sec_q3_fived16.tex:19 |
| `f0b-A7_genie_mec-p-nopl` | 0.56 | 0.99 | sec_q3_fived16.tex:19 |
| `f0b-A7_gibuu-cells-nopl` | R02, R06, R07 | R02, R06 | sec_q3_fived16.tex:26, sec_q3_fived16.tex:33 |
| `f0b-A7_gibuu-chi2` | 171.01 | 92.14 | appC_supplementary.tex:234, sec_q3_fived16.tex:26 |
| `f0b-A7_gibuu-chi2-nopl` | 175.13 | 92.96 | sec_q3_fived16.tex:26 |
| `f0b-A7_gibuu-in_sample-chi2` | 138.83 | 76.28 | records_r04_higherdim.tex:600 |
| `f0b-A7_gibuu-in_sample-p` | 1.2\times10^{-21} | 7.7\times10^{-10} | records_r04_higherdim.tex:600 |
| `f0b-A7_gibuu-p` | 5.3\times10^{-28} | 1.0\times10^{-12} | appC_supplementary.tex:234, sec_q3_fived16.tex:26 |
| `f0b-A7_gibuu-p-nopl` | 8.0\times10^{-29} | 7.1\times10^{-13} | sec_q3_fived16.tex:26 |
| `f0b-A7_mnvtune-chi2-nopl` | 0.01 | 0.00 | sec_q3_fived16.tex:17 |
| `f0b-A7_nuwro-chi2` | 23.86 | 12.71 | sec_q3_fived16.tex:21 |
| `f0b-A7_nuwro-chi2-nopl` | 24.92 | 12.92 | sec_q3_fived16.tex:21 |
| `f0b-A7_nuwro-in_sample-chi2` | 23.85 | 12.68 | records_r04_higherdim.tex:595 |
| `f0b-A7_nuwro-in_sample-p` | 0.093 | 0.70 | records_r04_higherdim.tex:595 |
| `f0b-A7_nuwro-p` | 0.093 | 0.69 | sec_q3_fived16.tex:21 |
| `f0b-A7_nuwro-p-nopl` | 0.071 | 0.68 | sec_q3_fived16.tex:21 |
| `f0b-P1g-chi2` | 75.53 | 36.00 | records_r04_higherdim.tex:593 |
| `f0b-P1g-p` | 1.1\times10^{-9} | 0.0029 | records_r04_higherdim.tex:593 |
| `f0b-P1r-chi2` | 38.93 | 19.49 | records_r04_higherdim.tex:590 |
| `f0b-P1r-p` | 0.0011 | 0.24 | records_r04_higherdim.tex:590 |
| `f0b-P2g-chi2` | 36.45 | 17.44 | records_r04_higherdim.tex:594 |
| `f0b-P2g-p` | 0.0025 | 0.36 | records_r04_higherdim.tex:594 |
| `f0b-P2r-chi2` | 33.89 | 17.72 | records_r04_higherdim.tex:591 |
| `f0b-P2r-p` | 0.0056 | 0.34 | records_r04_higherdim.tex:591 |
| `f0b-P3g-chi2` | 21.60 | 8.64 | records_r04_higherdim.tex:595 |
| `f0b-P3g-p` | 0.16 | 0.93 | records_r04_higherdim.tex:595 |
| `f0b-P3r-chi2` | 2.09 | 1.19 | records_r04_higherdim.tex:592 |
| `f0b-W1-chi2` | 4.82 | 2.35 | sec_q3_fived16.tex:22 |
| `f0b-W1-chi2-nopl` | 5.01 | 2.41 | sec_q3_fived16.tex:22 |
| `f0b-W1-in_sample-chi2` | 4.82 | 2.33 | records_r04_higherdim.tex:596 |
| `f0b-W2-chi2` | 0.50 | 0.22 | sec_q3_fived16.tex:20 |
| `f0b-W2-chi2-nopl` | 0.57 | 0.23 | sec_q3_fived16.tex:20 |
| `f0b-W2-in_sample-chi2` | 0.33 | 0.18 | records_r04_higherdim.tex:594 |
| `f0b-W3-chi2` | 27.41 | 14.61 | sec_q3_fived16.tex:23 |
| `f0b-W3-chi2-nopl` | 30.83 | 15.49 | sec_q3_fived16.tex:23 |
| `f0b-W3-in_sample-chi2` | 26.43 | 13.91 | records_r04_higherdim.tex:597 |
| `f0b-W3-in_sample-p` | 0.048 | 0.61 | records_r04_higherdim.tex:597 |
| `f0b-W3-p` | 0.037 | 0.55 | sec_q3_fived16.tex:23 |
| `f0b-W3-p-nopl` | 0.014 | 0.49 | sec_q3_fived16.tex:23 |
| `f0b-closure_nuwro-chi2` | 10.66 | 5.42 | sec_q3_fived16.tex:24 |
| `f0b-closure_nuwro-chi2-nopl` | 11.60 | 5.61 | sec_q3_fived16.tex:24 |
| `f0b-closure_nuwro-in_sample-chi2` | 10.56 | 5.36 | records_r04_higherdim.tex:598 |
| `f0b-closure_nuwro-in_sample-p` | 0.84 | 0.99 | records_r04_higherdim.tex:598 |
| `f0b-closure_nuwro-p` | 0.83 | 0.99 | sec_q3_fived16.tex:24 |
| `f0b-closure_nuwro-p-nopl` | 0.77 | 0.99 | sec_q3_fived16.tex:24 |
| `f0b-grp-non-vertex-ptruths` | 1 | 0 | records_r04_higherdim.tex:539 |
| `f0b-nlisted` | 2 | 1 | appC_supplementary.tex:232, records_r05_sixteen.tex:149, sec5_multidim.tex:103 ... |
| `f0b-nlisted-nopl` | 3 | 1 | sec_q3_fived16.tex:33 |
| `f0b-nunlisted` | 10 | 11 | sec_q3_fived16.tex:33 |
| `f0b-q3-chi2` | 52.48 | 22.46 | appC_supplementary.tex:234, sec_q3_fived16.tex:27 |
| `f0b-q3-chi2-nopl` | 53.42 | 22.78 | sec_q3_fived16.tex:27 |
| `f0b-q3-p` | 9.1\times10^{-6} | 0.13 | appC_supplementary.tex:234, sec_q3_fived16.tex:27, sec_q3_fived16.tex:33 |
| `f0b-q3-p-nopl` | 6.4\times10^{-6} | 0.12 | sec_q3_fived16.tex:27 |
| `f0b-stage0c_gibuu-cells-nopl` | R06 | --- | sec_q3_fived16.tex:25 |
| `f0b-stage0c_gibuu-chi2` | 24.57 | 12.69 | sec_q3_fived16.tex:25 |
| `f0b-stage0c_gibuu-chi2-nopl` | 25.46 | 12.88 | sec_q3_fived16.tex:25 |
| `f0b-stage0c_gibuu-in_sample-chi2` | 22.10 | 11.36 | records_r04_higherdim.tex:599 |
| `f0b-stage0c_gibuu-in_sample-p` | 0.14 | 0.79 | records_r04_higherdim.tex:599 |
| `f0b-stage0c_gibuu-p` | 0.078 | 0.70 | sec_q3_fived16.tex:25 |
| `f0b-stage0c_gibuu-p-nopl` | 0.062 | 0.68 | sec_q3_fived16.tex:25 |
| `f0b-stage0c_gibuu-zmax` | 1.76 | 1.54 | appC_supplementary.tex:257, sec_q3_fived16.tex:33 |
| `f0b-stage0c_gibuu-zmax-nopl` | 2.01 | 1.70 | appC_supplementary.tex:257, sec_q3_fived16.tex:33 |
| `f1-ar23-chi2` | 14.06 | 6.61 | records_r04_higherdim.tex:606 |
| `f1-ar23-p` | 0.59 | 0.98 | records_r04_higherdim.tex:606 |
| `f1-ar23-sens-chi2` | 18.79 | 8.12 | records_r04_higherdim.tex:606 |
| `f1-ar23-sens-p` | 0.28 | 0.95 | records_r04_higherdim.tex:606 |
| `f1-ar23-zmax` | 0.61 | 0.55 | records_r04_higherdim.tex:606 |
| `f1-bsig-ceil` | 0.62 | 0.60 | appC_supplementary.tex:234, records_r04_higherdim.tex:571, sec5_multidim.tex:130 ... |
| `f1-closure-ar23-chi2` | 13.43 | 6.25 | records_r04_higherdim.tex:606 |
| `f1-closure-ar23-p` | 0.64 | 0.99 | records_r04_higherdim.tex:606 |
| `f1-closure-ar23-sens-chi2` | 17.22 | 7.45 | records_r04_higherdim.tex:606 |
| `f1-closure-ar23-sens-p` | 0.37 | 0.96 | records_r04_higherdim.tex:606 |
| `f1-closure-ar23-zmax` | 0.57 | 0.51 | records_r04_higherdim.tex:606 |
| `f1-closure-g18-chi2` | 9.14 | 4.65 | records_r04_higherdim.tex:606 |
| `f1-closure-g18-p` | 0.91 | 1.00 | records_r04_higherdim.tex:606 |
| `f1-closure-g18-sens-chi2` | 11.07 | 5.30 | records_r04_higherdim.tex:606 |
| `f1-closure-g18-sens-p` | 0.81 | 0.99 | records_r04_higherdim.tex:606 |
| `f1-closure-g18-zmax` | 0.60 | 0.58 | records_r04_higherdim.tex:606 |
| `f1-g18-chi2` | 9.26 | 4.90 | records_r04_higherdim.tex:606 |
| `f1-g18-p` | 0.90 | 1.00 | records_r04_higherdim.tex:606 |
| `f1-g18-sens-chi2` | 11.55 | 5.67 | records_r04_higherdim.tex:606 |
| `f1-g18-sens-p` | 0.77 | 0.99 | records_r04_higherdim.tex:606 |
| `f1-g18-zmax` | 0.61 | 0.60 | records_r04_higherdim.tex:606 |
| `fb-gcv-hi` | 110 | 65 | records_r05_sixteen.tex:336 |
| `fb-gcv-lo` | 104 | 63 | records_r05_sixteen.tex:336 |
| `fb-gcv-offset` | 0.26 | 0.08 | records_r05_sixteen.tex:336 |
| `fb-gibuu-hi` | 48 | 42 | records_r05_sixteen.tex:336 |
| `fb-gibuu-lo` | 47 | 41 | records_r05_sixteen.tex:336 |
| `fb-gibuu-offset` | 0.07 | 0.03 | records_r05_sixteen.tex:336 |
| `fb-gmec-hi` | 235 | 142 | records_r05_sixteen.tex:336 |
| `fb-gmec-lo` | 222 | 138 | records_r05_sixteen.tex:336 |
| `fb-gmec-offset` | 0.32 | 0.14 | records_r05_sixteen.tex:336 |
| `fb-nuwro-hi` | 130 | 92 | records_r05_sixteen.tex:336 |
| `fb-nuwro-lo` | 126 | 91 | records_r05_sixteen.tex:336 |
| `fb-nuwro-offset` | 0.20 | 0.04 | records_r05_sixteen.tex:336 |
| `fb-tune-hi` | 272 | 159 | records_r05_sixteen.tex:336 |
| `fb-tune-lo` | 253 | 153 | records_r05_sixteen.tex:336 |
| `fb-tune-offset` | 1.00 | 0.34 | records_r05_sixteen.tex:336 |
| `g-gcv-pull-R00` | 1.49 | 1.43 | sec_fived16_gen.tex:40 |
| `g-gcv-pull-R01` | 1.48 | 1.43 | sec_fived16_gen.tex:41 |
| `g-gcv-pull-R02` | -0.88 | -0.86 | sec_fived16_gen.tex:42 |
| `g-gcv-pull-R04` | 1.75 | 1.70 | sec_fived16_gen.tex:44 |
| `g-gcv-pull-R05` | 1.73 | 1.65 | sec_fived16_gen.tex:45 |
| `g-gcv-pull-R06` | -2.28 | -2.04 | sec_fived16_gen.tex:46 |
| `g-gcv-pull-R07` | -0.23 | -0.21 | sec_fived16_gen.tex:47 |
| `g-gcv-pull-R08` | 2.77 | 2.65 | sec_fived16_gen.tex:48 |
| `g-gcv-pull-R09` | 0.94 | 0.92 | sec_fived16_gen.tex:49 |
| `g-gcv-pull-R10` | 0.84 | 0.80 | sec_fived16_gen.tex:50 |
| `g-gcv-pull-R12` | 2.31 | 2.21 | sec_fived16_gen.tex:52 |
| `g-gcv-pull-R13` | 0.37 | 0.35 | sec_fived16_gen.tex:53 |
| `g-gcv-pull-R14` | 2.97 | 2.87 | sec_fived16_gen.tex:54 |
| `g-gcv-pull-R15` | 0.53 | 0.51 | sec_fived16_gen.tex:55 |
| `g-gcv-shape_only-chi2` | 102.11 | 59.30 | sec5_multidim.tex:163, sec_fived16_gen.tex:17 |
| `g-gcv-shape_only-chi2-nopl` | 110.32 | 63.12 | sec_fived16_gen.tex:17 |
| `g-gcv-total-chi2` | 107.18 | 64.01 | sec5_multidim.tex:163, sec_fived16_gen.tex:17 |
| `g-gcv-total-chi2-nopl` | 111.22 | 65.26 | sec_fived16_gen.tex:17 |
| `g-gcv-total-chi2int` | 107 | 64 | records_r05_sixteen.tex:336 |
| `g-gibuu-carbon-shape_only-chi2` | 24.94 | 21.44 | sec5_multidim.tex:167, sec_fived16_gen.tex:23, sec_fived16_gen.tex:167 |
| `g-gibuu-carbon-shape_only-chi2-nopl` | 27.86 | 23.61 | sec_fived16_gen.tex:23, sec_fived16_gen.tex:167 |
| `g-gibuu-carbon-total-chi2` | 45.49 | 39.70 | records_r05_sixteen.tex:378, sec5_multidim.tex:167, sec_fived16_gen.tex:23 ... |
| `g-gibuu-carbon-total-chi2-nopl` | 58.65 | 49.82 | sec_fived16_gen.tex:23, sec_fived16_gen.tex:167 |
| `g-gibuu-chrise` | 2.3 | 2.1 | records_r05_sixteen.tex:384, records_r05_sixteen.tex:394, sec_fived16_gen.tex:140 |
| `g-gibuu-gen-carbon-shape_only-chi2` | 24.75 | 21.35 | sec_fived16_gen.tex:169 |
| `g-gibuu-gen-carbon-shape_only-chi2-nopl` | 27.69 | 23.54 | sec_fived16_gen.tex:169 |
| `g-gibuu-gen-carbon-total-chi2` | 45.25 | 39.58 | records_r05_sixteen.tex:280, sec_fived16_gen.tex:169 |
| `g-gibuu-gen-carbon-total-chi2-nopl` | 58.46 | 49.74 | sec_fived16_gen.tex:169 |
| `g-gibuu-gen-ch-shape_only-chi2` | 22.01 | 18.84 | sec_fived16_gen.tex:170 |
| `g-gibuu-gen-ch-shape_only-chi2-nopl` | 24.49 | 20.64 | sec_fived16_gen.tex:170 |
| `g-gibuu-gen-ch-total-chi2` | 47.55 | 41.69 | sec_fived16_gen.tex:170 |
| `g-gibuu-gen-ch-total-chi2-nopl` | 61.22 | 52.15 | sec_fived16_gen.tex:170 |
| `g-gibuu-genieh-shape_only-chi2` | 21.95 | 18.60 | records_r05_sixteen.tex:313 |
| `g-gibuu-genieh-shape_only-chi2-nopl` | 24.37 | 20.35 | records_r05_sixteen.tex:313 |
| `g-gibuu-genieh-total-chi2` | 44.19 | 38.46 | records_r05_sixteen.tex:280, records_r05_sixteen.tex:313 |
| `g-gibuu-genieh-total-chi2-nopl` | 56.68 | 48.00 | records_r05_sixteen.tex:313 |
| `g-gibuu-pull-R00` | 2.66 | 2.56 | sec_fived16_gen.tex:40 |
| `g-gibuu-pull-R01` | 3.96 | 3.83 | sec_fived16_gen.tex:41 |
| `g-gibuu-pull-R02` | 3.70 | 3.60 | sec_fived16_gen.tex:42 |
| `g-gibuu-pull-R03` | 3.52 | 3.33 | sec_fived16_gen.tex:43 |
| `g-gibuu-pull-R08` | 3.49 | 3.35 | sec_fived16_gen.tex:48 |
| `g-gibuu-pull-R09` | 2.70 | 2.63 | sec_fived16_gen.tex:49 |
| `g-gibuu-pull-R10` | 4.45 | 4.24 | sec_fived16_gen.tex:50 |
| `g-gibuu-pull-R11` | 1.31 | 1.28 | sec_fived16_gen.tex:51 |
| `g-gibuu-shape_only-chi2` | 22.19 | 18.92 | records_r05_sixteen.tex:378, sec_fived16_gen.tex:168 |
| `g-gibuu-shape_only-chi2-nopl` | 24.66 | 20.71 | sec_fived16_gen.tex:168 |
| `g-gibuu-total-chi2` | 47.78 | 41.80 | appC_supplementary.tex:216, records_r05_sixteen.tex:378, sec_fived16_gen.tex:168 |
| `g-gibuu-total-chi2-nopl` | 61.41 | 52.22 | sec_fived16_gen.tex:168 |
| `g-gibuu-total-chi2int` | 48 | 42 | records_r05_sixteen.tex:336 |
| `g-gmec-pull-R00` | 0.12 | 0.11 | sec_fived16_gen.tex:40 |
| `g-gmec-pull-R01` | 1.45 | 1.40 | sec_fived16_gen.tex:41 |
| `g-gmec-pull-R02` | -1.11 | -1.08 | sec_fived16_gen.tex:42 |
| `g-gmec-pull-R03` | 0.10 | 0.09 | sec_fived16_gen.tex:43 |
| `g-gmec-pull-R04` | -0.53 | -0.51 | sec_fived16_gen.tex:44 |
| `g-gmec-pull-R05` | 2.11 | 2.01 | sec_fived16_gen.tex:45 |
| `g-gmec-pull-R06` | -2.87 | -2.57 | sec_fived16_gen.tex:46 |
| `g-gmec-pull-R07` | 0.17 | 0.15 | sec_fived16_gen.tex:47 |
| `g-gmec-pull-R08` | 2.22 | 2.12 | sec_fived16_gen.tex:48 |
| `g-gmec-pull-R09` | 0.90 | 0.88 | sec_fived16_gen.tex:49 |
| `g-gmec-pull-R10` | 0.73 | 0.69 | sec_fived16_gen.tex:50 |
| `g-gmec-pull-R11` | 0.26 | 0.25 | sec_fived16_gen.tex:51 |
| `g-gmec-pull-R12` | 1.76 | 1.68 | sec_fived16_gen.tex:52 |
| `g-gmec-pull-R13` | 0.26 | 0.25 | sec_fived16_gen.tex:53 |
| `g-gmec-pull-R14` | 2.71 | 2.62 | sec_fived16_gen.tex:54 |
| `g-gmec-pull-R15` | 0.37 | 0.36 | sec_fived16_gen.tex:55 |
| `g-gmec-shape_only-chi2` | 229.00 | 140.33 | sec5_multidim.tex:164, sec_fived16_gen.tex:18 |
| `g-gmec-shape_only-chi2-nopl` | 263.74 | 158.84 | sec_fived16_gen.tex:18 |
| `g-gmec-total-chi2` | 229.09 | 140.34 | sec5_multidim.tex:164, sec_fived16_gen.tex:18 |
| `g-gmec-total-chi2-nopl` | 277.94 | 164.38 | sec_fived16_gen.tex:18 |
| `g-gmec-total-chi2int` | 229 | 140 | records_r05_sixteen.tex:336 |
| `g-nuwro-carbon-shape_only-chi2` | 112.93 | 79.56 | sec5_multidim.tex:165, sec_fived16_gen.tex:19, sec_fived16_gen.tex:161 |
| `g-nuwro-carbon-shape_only-chi2-nopl` | 187.39 | 119.18 | sec_fived16_gen.tex:19, sec_fived16_gen.tex:161 |
| `g-nuwro-carbon-total-chi2` | 129.98 | 92.20 | appC_supplementary.tex:216, records_r05_sixteen.tex:378, sec5_multidim.tex:165 ... |
| `g-nuwro-carbon-total-chi2-nopl` | 187.42 | 119.69 | appC_supplementary.tex:216, sec_fived16_gen.tex:19, sec_fived16_gen.tex:161 |
| `g-nuwro-carbon-total-chi2int` | 130 | 92 | sec5_multidim.tex:172 |
| `g-nuwro-carbon-total-chi2int-nopl` | 187 | 120 | sec5_multidim.tex:172 |
| `g-nuwro-gen-carbon-shape_only-chi2` | 113.73 | 80.03 | sec_fived16_gen.tex:163 |
| `g-nuwro-gen-carbon-shape_only-chi2-nopl` | 188.00 | 119.59 | sec_fived16_gen.tex:163 |
| `g-nuwro-gen-carbon-total-chi2` | 130.68 | 92.61 | sec_fived16_gen.tex:163 |
| `g-nuwro-gen-carbon-total-chi2-nopl` | 188.03 | 120.09 | sec_fived16_gen.tex:163 |
| `g-nuwro-gen-ch-shape_only-chi2` | 108.40 | 76.07 | sec_fived16_gen.tex:164 |
| `g-nuwro-gen-ch-shape_only-chi2-nopl` | 181.13 | 114.76 | sec_fived16_gen.tex:164 |
| `g-nuwro-gen-ch-total-chi2` | 128.41 | 91.72 | records_r05_sixteen.tex:285, sec_fived16_gen.tex:164 |
| `g-nuwro-gen-ch-total-chi2-nopl` | 181.21 | 116.22 | sec_fived16_gen.tex:164 |
| `g-nuwro-genieh-shape_only-chi2` | 101.20 | 70.70 | records_r05_sixteen.tex:308 |
| `g-nuwro-genieh-shape_only-chi2-nopl` | 168.98 | 106.71 | records_r05_sixteen.tex:308 |
| `g-nuwro-genieh-total-chi2` | 120.47 | 85.84 | records_r05_sixteen.tex:308 |
| `g-nuwro-genieh-total-chi2-nopl` | 169.10 | 108.27 | records_r05_sixteen.tex:308 |
| `g-nuwro-native-ana-shape_only-chi2` | 112.01 | 78.95 | records_r05_sixteen.tex:310 |
| `g-nuwro-native-ana-shape_only-chi2-nopl` | 194.35 | 122.42 | records_r05_sixteen.tex:310 |
| `g-nuwro-native-ana-total-chi2` | 134.71 | 95.94 | records_r05_sixteen.tex:310 |
| `g-nuwro-native-ana-total-chi2-nopl` | 194.46 | 123.90 | records_r05_sixteen.tex:310 |
| `g-nuwro-native-gen-shape_only-chi2` | 111.98 | 78.64 | records_r05_sixteen.tex:309 |
| `g-nuwro-native-gen-shape_only-chi2-nopl` | 193.29 | 121.62 | records_r05_sixteen.tex:309 |
| `g-nuwro-native-gen-total-chi2` | 134.02 | 95.28 | records_r05_sixteen.tex:285, records_r05_sixteen.tex:309 |
| `g-nuwro-native-gen-total-chi2-nopl` | 193.37 | 123.04 | records_r05_sixteen.tex:309 |
| `g-nuwro-pull-R00` | 2.18 | 2.09 | sec_fived16_gen.tex:40 |
| `g-nuwro-pull-R01` | 1.17 | 1.13 | sec_fived16_gen.tex:41 |
| `g-nuwro-pull-R02` | 0.83 | 0.81 | sec_fived16_gen.tex:42 |
| `g-nuwro-pull-R03` | -0.44 | -0.41 | sec_fived16_gen.tex:43 |
| `g-nuwro-pull-R04` | 2.41 | 2.34 | sec_fived16_gen.tex:44 |
| `g-nuwro-pull-R05` | -0.16 | -0.15 | sec_fived16_gen.tex:45 |
| `g-nuwro-pull-R06` | 1.45 | 1.29 | sec_fived16_gen.tex:46 |
| `g-nuwro-pull-R07` | -1.10 | -0.99 | sec_fived16_gen.tex:47 |
| `g-nuwro-pull-R08` | 4.36 | 4.16 | sec_fived16_gen.tex:48 |
| `g-nuwro-pull-R09` | 2.60 | 2.54 | sec_fived16_gen.tex:49 |
| `g-nuwro-pull-R10` | 2.27 | 2.16 | sec_fived16_gen.tex:50 |
| `g-nuwro-pull-R11` | 0.90 | 0.87 | sec_fived16_gen.tex:51 |
| `g-nuwro-pull-R12` | 3.34 | 3.21 | sec_fived16_gen.tex:52 |
| `g-nuwro-pull-R13` | 1.09 | 1.04 | sec_fived16_gen.tex:53 |
| `g-nuwro-pull-R14` | 4.08 | 3.94 | sec_fived16_gen.tex:54 |
| `g-nuwro-pull-R15` | 2.15 | 2.05 | sec_fived16_gen.tex:55 |
| `g-nuwro-shape_only-chi2` | 107.52 | 75.58 | records_r05_sixteen.tex:378, sec_fived16_gen.tex:162 |
| `g-nuwro-shape_only-chi2-nopl` | 180.52 | 114.36 | sec_fived16_gen.tex:162 |
| `g-nuwro-total-chi2` | 127.69 | 91.32 | appC_supplementary.tex:216, records_r05_sixteen.tex:378, sec_fived16_gen.tex:162 |
| `g-nuwro-total-chi2-nopl` | 180.62 | 115.84 | sec_fived16_gen.tex:162 |
| `g-nuwro-total-chi2int` | 128 | 91 | records_r05_sixteen.tex:336 |
| `g-tune-pull-R00` | 0.85 | 0.81 | sec_fived16_gen.tex:40 |
| `g-tune-pull-R01` | 1.72 | 1.66 | sec_fived16_gen.tex:41 |
| `g-tune-pull-R02` | -0.27 | -0.26 | sec_fived16_gen.tex:42 |
| `g-tune-pull-R03` | 1.20 | 1.13 | sec_fived16_gen.tex:43 |
| `g-tune-pull-R04` | 0.52 | 0.50 | sec_fived16_gen.tex:44 |
| `g-tune-pull-R05` | 2.27 | 2.16 | sec_fived16_gen.tex:45 |
| `g-tune-pull-R06` | -1.52 | -1.36 | sec_fived16_gen.tex:46 |
| `g-tune-pull-R07` | 1.62 | 1.46 | sec_fived16_gen.tex:47 |
| `g-tune-pull-R08` | 3.24 | 3.09 | sec_fived16_gen.tex:48 |
| `g-tune-pull-R09` | 1.70 | 1.66 | sec_fived16_gen.tex:49 |
| `g-tune-pull-R10` | 1.92 | 1.83 | sec_fived16_gen.tex:50 |
| `g-tune-pull-R11` | 1.29 | 1.26 | sec_fived16_gen.tex:51 |
| `g-tune-pull-R12` | 2.16 | 2.07 | sec_fived16_gen.tex:52 |
| `g-tune-pull-R13` | 1.55 | 1.48 | sec_fived16_gen.tex:53 |
| `g-tune-pull-R14` | 3.41 | 3.29 | sec_fived16_gen.tex:54 |
| `g-tune-pull-R15` | 1.65 | 1.58 | sec_fived16_gen.tex:55 |
| `g-tune-shape_only-chi2` | 261.88 | 155.39 | sec5_multidim.tex:166, sec_fived16_gen.tex:20 |
| `g-tune-shape_only-chi2-nopl` | 311.19 | 184.06 | sec_fived16_gen.tex:20 |
| `g-tune-total-chi2` | 262.06 | 155.79 | sec5_multidim.tex:166, sec_fived16_gen.tex:20 |
| `g-tune-total-chi2-nopl` | 329.72 | 188.44 | sec_fived16_gen.tex:20 |
| `g-tune-total-chi2int` | 262 | 156 | records_r05_sixteen.tex:336 |
| `g3d-zmax` | 0.17 | 0.16 | appC_supplementary.tex:68, records_r05_sixteen.tex:164, sec_fived16.tex:105 |
| `gdef-dmax` | 0.063 | 0.059 | records_r05_sixteen.tex:361 |
| `gdef-seedmax` | 0.052 | 0.049 | records_r05_sixteen.tex:361 |
| `gs-gcv-shape_only-chi2` | 100.57 | 58.34 | app_devhistory.tex:177 |
| `gs-gcv-shape_only-chi2-nopl` | 108.51 | 62.06 | app_devhistory.tex:177 |
| `gs-gcv-total-chi2` | 105.42 | 62.88 | app_devhistory.tex:177 |
| `gs-gcv-total-chi2-nopl` | 109.35 | 64.13 | app_devhistory.tex:177 |
| `gs-gmec-shape_only-chi2` | 223.46 | 137.54 | app_devhistory.tex:178 |
| `gs-gmec-shape_only-chi2-nopl` | 258.07 | 156.00 | app_devhistory.tex:178 |
| `gs-gmec-total-chi2` | 223.55 | 137.54 | app_devhistory.tex:178 |
| `gs-gmec-total-chi2-nopl` | 272.12 | 161.46 | app_devhistory.tex:178 |
| `ibu16-dsig-R05` | 1.4 | 1.3 | records_r04_higherdim.tex:628 |
| `ibu16-dsig-R06` | 2.8 | 2.5 | appC_supplementary.tex:333, records_r04_higherdim.tex:628 |
| `ibu16-dsig-max` | 2.8 | 2.5 | records_r04_higherdim.tex:628 |
| `pl-cellrise-max` | 14.1 | 13.1 | records_r05_sixteen.tex:131 |
| `pl-cellrise-med` | 4.8 | 4.3 | records_r05_sixteen.tex:131 |
| `pl-chi2fall-shape_only-hi` | 40.4 | 33.9 | records_r05_sixteen.tex:131, records_r05_sixteen.tex:139 |
| `pl-chi2fall-shape_only-lo` | 7.4 | 6.0 | records_r05_sixteen.tex:131, records_r05_sixteen.tex:139 |
| `pl-chi2fall-total-hi` | 29.3 | 21.2 | records_r05_sixteen.tex:131, records_r05_sixteen.tex:139 |
| `pl-chi2fall-total-lo` | 3.6 | 1.9 | records_r05_sixteen.tex:131, records_r05_sixteen.tex:139 |
| `pl-medrise` | 7.8 | 7.0 | records_r05_sixteen.tex:134, records_r05_sixteen.tex:144, sec_fived16.tex:225 |
| `pl-share-max` | 23.2 | 21.8 | records_r05_sixteen.tex:131 |
| `pl-share-med` | 9.0 | 8.1 | records_r05_sixteen.tex:131 |
| `prr-chi2-e-gibuu` | 175.0 | 94.1 | records_r04_higherdim.tex:457 |
| `prr-chi2-e-q3` | 54.9 | 23.3 | records_r04_higherdim.tex:458 |
| `prr-chi2-ibu-gibuu` | 457.1 | 210.9 | records_r04_higherdim.tex:457 |
| `prr-chi2-ibu-q3` | 31.6 | 19.3 | records_r04_higherdim.tex:458 |
| `prr-ibu5-nnew-word` | four | two | appC_supplementary.tex:244, sec_q3_fived16.tex:91 |
| `prr-ibu5-q3-p` | 0.011 | 0.255 | sec_q3_fived16.tex:91 |
| `prr-lev-C25-nnew` | 3 | 4 | records_r04_higherdim.tex:463 |
| `prr-lev-K2-nnew` | 3 | 0 | records_r04_higherdim.tex:463 |
| `r04-corr-max` | 0.77 | 0.78 | records_r04_higherdim.tex:349 |
| `r04-sigma-total` | 4.80 | 4.96 | records_r04_higherdim.tex:349, records_r04_higherdim.tex:352 |
| `rsn-sm-nuwro-p` | 0.0049 | 0.38 | records_r04_higherdim.tex:539 |
| `rsn-wr-sig-max` | 0.09 | 0.08 | records_r02_method.tex:202, sec_method.tex:17 |
| `sens-c_e_systematic-gcv-a0.1` | 69.00 | 48.28 | sec_fived16_gen.tex:97 |
| `sens-c_e_systematic-gcv-a0.25` | 55.05 | 41.00 | sec_fived16_gen.tex:97 |
| `sens-c_e_systematic-gcv-a0.5` | 45.66 | 35.85 | sec_fived16_gen.tex:97 |
| `sens-c_e_systematic-gcv-a1` | 41.91 | 34.08 | sec_fived16_gen.tex:97 |
| `sens-c_e_systematic-gibuu-a0.1` | 43.23 | 38.99 | sec_fived16_gen.tex:100 |
| `sens-c_e_systematic-gibuu-a0.25` | 43.21 | 39.03 | sec_fived16_gen.tex:100 |
| `sens-c_e_systematic-gibuu-a0.5` | 47.99 | 42.73 | sec_fived16_gen.tex:100 |
| `sens-c_e_systematic-gibuu-a1` | 75.67 | 62.49 | sec_fived16_gen.tex:100 |
| `sens-c_e_systematic-gmec-a0.1` | 125.93 | 89.78 | sec_fived16_gen.tex:98 |
| `sens-c_e_systematic-gmec-a0.25` | 86.12 | 65.54 | sec_fived16_gen.tex:98 |
| `sens-c_e_systematic-gmec-a0.5` | 61.63 | 49.34 | sec_fived16_gen.tex:98 |
| `sens-c_e_systematic-gmec-a1` | 45.40 | 37.80 | sec_fived16_gen.tex:98 |
| `sens-c_e_systematic-nuwro-a0.1` | 82.48 | 64.76 | sec_fived16_gen.tex:99 |
| `sens-c_e_systematic-nuwro-a0.25` | 65.58 | 53.94 | sec_fived16_gen.tex:99 |
| `sens-c_e_systematic-nuwro-a0.5` | 57.35 | 48.43 | sec_fived16_gen.tex:99 |
| `sens-c_e_systematic-nuwro-a1` | 65.06 | 53.66 | sec_fived16_gen.tex:99 |
| `sens-c_e_systematic-tune-a0.1` | 136.69 | 96.54 | sec_fived16_gen.tex:101 |
| `sens-c_e_systematic-tune-a0.25` | 91.79 | 69.45 | sec_fived16_gen.tex:101 |
| `sens-c_e_systematic-tune-a0.5` | 66.60 | 53.18 | sec_fived16_gen.tex:101 |
| `sens-c_e_systematic-tune-a1` | 57.56 | 46.90 | sec_fived16_gen.tex:101 |
| `sens-detector-gcv-a0.1` | 96.12 | 60.04 | sec_fived16_gen.tex:85 |
| `sens-detector-gcv-a0.25` | 86.81 | 56.15 | sec_fived16_gen.tex:85 |
| `sens-detector-gcv-a0.5` | 78.39 | 52.15 | sec_fived16_gen.tex:85 |
| `sens-detector-gcv-a1` | 70.27 | 47.82 | sec_fived16_gen.tex:85 |
| `sens-detector-gibuu-a0.1` | 47.44 | 41.75 | sec_fived16_gen.tex:88 |
| `sens-detector-gibuu-a0.25` | 47.25 | 41.83 | sec_fived16_gen.tex:88 |
| `sens-detector-gibuu-a0.5` | 47.53 | 42.25 | sec_fived16_gen.tex:88 |
| `sens-detector-gibuu-a1` | 49.41 | 43.91 | sec_fived16_gen.tex:88 |
| `sens-detector-gmec-a0.1` | 205.48 | 130.35 | sec_fived16_gen.tex:86 |
| `sens-detector-gmec-a0.25` | 181.78 | 119.12 | sec_fived16_gen.tex:86 |
| `sens-detector-gmec-a0.5` | 156.96 | 106.01 | sec_fived16_gen.tex:86 |
| `sens-detector-gmec-a1` | 129.91 | 90.16 | sec_fived16_gen.tex:86 |
| `sens-detector-nuwro-a0.1` | 116.06 | 85.13 | sec_fived16_gen.tex:87 |
| `sens-detector-nuwro-a0.25` | 106.45 | 79.50 | sec_fived16_gen.tex:87 |
| `sens-detector-nuwro-a0.5` | 97.29 | 73.88 | sec_fived16_gen.tex:87 |
| `sens-detector-nuwro-a1` | 88.46 | 68.20 | sec_fived16_gen.tex:87 |
| `sens-detector-tune-a0.1` | 232.46 | 144.61 | sec_fived16_gen.tex:89 |
| `sens-detector-tune-a0.25` | 204.63 | 131.82 | sec_fived16_gen.tex:89 |
| `sens-detector-tune-a0.5` | 176.12 | 116.98 | sec_fived16_gen.tex:89 |
| `sens-detector-tune-a1` | 146.19 | 99.72 | sec_fived16_gen.tex:89 |
| `sens-detlat-fall-max` | 18 | 11 | records_r05_sixteen.tex:336 |
| `sens-flux-fall-hi` | 38 | 31 | appC_supplementary.tex:216, records_r05_sixteen.tex:274, records_r05_sixteen.tex:336 ... |
| `sens-flux-fall-lo` | 23 | 15 | appC_supplementary.tex:216, records_r05_sixteen.tex:274, records_r05_sixteen.tex:336 ... |
| `sens-flux-gcv-a0.1` | 82.27 | 54.58 | sec_fived16_gen.tex:79 |
| `sens-flux-gcv-a0.25` | 67.10 | 47.54 | sec_fived16_gen.tex:79 |
| `sens-flux-gcv-a0.5` | 54.97 | 41.39 | sec_fived16_gen.tex:79 |
| `sens-flux-gcv-a1` | 45.86 | 36.76 | sec_fived16_gen.tex:79 |
| `sens-flux-gibuu-a0.1` | 45.68 | 40.69 | sec_fived16_gen.tex:82 |
| `sens-flux-gibuu-a0.25` | 45.17 | 40.52 | sec_fived16_gen.tex:82 |
| `sens-flux-gibuu-a0.5` | 47.36 | 42.31 | sec_fived16_gen.tex:82 |
| `sens-flux-gibuu-a1` | 59.63 | 51.50 | sec_fived16_gen.tex:82 |
| `sens-flux-gmec-a0.1` | 151.92 | 101.78 | sec_fived16_gen.tex:80 |
| `sens-flux-gmec-a0.25` | 109.98 | 78.43 | sec_fived16_gen.tex:80 |
| `sens-flux-gmec-a0.5` | 80.36 | 60.62 | sec_fived16_gen.tex:80 |
| `sens-flux-gmec-a1` | 56.70 | 45.49 | sec_fived16_gen.tex:80 |
| `sens-flux-nuwro-a0.1` | 90.88 | 69.40 | sec_fived16_gen.tex:81 |
| `sens-flux-nuwro-a0.25` | 72.77 | 58.15 | sec_fived16_gen.tex:81 |
| `sens-flux-nuwro-a0.5` | 60.86 | 50.65 | sec_fived16_gen.tex:81 |
| `sens-flux-nuwro-a1` | 57.17 | 48.83 | sec_fived16_gen.tex:81 |
| `sens-flux-tune-a0.1` | 161.75 | 107.62 | sec_fived16_gen.tex:83 |
| `sens-flux-tune-a0.25` | 114.12 | 81.07 | sec_fived16_gen.tex:83 |
| `sens-flux-tune-a0.5` | 83.50 | 62.89 | sec_fived16_gen.tex:83 |
| `sens-flux-tune-a1` | 64.25 | 51.29 | sec_fived16_gen.tex:83 |
| `sens-interaction-gcv-a0.1` | 93.42 | 58.54 | sec_fived16_gen.tex:73 |
| `sens-interaction-gcv-a0.25` | 84.01 | 54.97 | sec_fived16_gen.tex:73 |
| `sens-interaction-gcv-a0.5` | 75.61 | 51.74 | sec_fived16_gen.tex:73 |
| `sens-interaction-gcv-a1` | 68.96 | 49.82 | sec_fived16_gen.tex:73 |
| `sens-interaction-gibuu-a0.1` | 47.10 | 41.53 | sec_fived16_gen.tex:76 |
| `sens-interaction-gibuu-a0.25` | 46.39 | 41.18 | sec_fived16_gen.tex:76 |
| `sens-interaction-gibuu-a0.5` | 45.55 | 40.71 | sec_fived16_gen.tex:76 |
| `sens-interaction-gibuu-a1` | 44.70 | 40.20 | sec_fived16_gen.tex:76 |
| `sens-interaction-gmec-a0.1` | 209.08 | 132.53 | sec_fived16_gen.tex:74 |
| `sens-interaction-gmec-a0.25` | 190.39 | 125.88 | sec_fived16_gen.tex:74 |
| `sens-interaction-gmec-a0.5` | 169.49 | 118.39 | sec_fived16_gen.tex:74 |
| `sens-interaction-gmec-a1` | 149.11 | 112.04 | sec_fived16_gen.tex:74 |
| `sens-interaction-nuwro-a0.1` | 113.76 | 84.26 | sec_fived16_gen.tex:75 |
| `sens-interaction-nuwro-a0.25` | 104.56 | 79.67 | sec_fived16_gen.tex:75 |
| `sens-interaction-nuwro-a0.5` | 95.69 | 75.06 | sec_fived16_gen.tex:75 |
| `sens-interaction-nuwro-a1` | 89.53 | 71.96 | sec_fived16_gen.tex:75 |
| `sens-interaction-tune-a0.1` | 240.57 | 148.71 | sec_fived16_gen.tex:77 |
| `sens-interaction-tune-a0.25` | 217.78 | 140.39 | sec_fived16_gen.tex:77 |
| `sens-interaction-tune-a0.5` | 190.31 | 129.67 | sec_fived16_gen.tex:77 |
| `sens-interaction-tune-a1` | 157.90 | 116.02 | sec_fived16_gen.tex:77 |
| `sens-joint-chi2-min` | 41 | 34 | records_r05_sixteen.tex:336, records_r05_sixteen.tex:341 |
| `sens-lateral-gcv-a0.1` | 88.07 | 57.02 | sec_fived16_gen.tex:91 |
| `sens-lateral-gcv-a0.25` | 77.31 | 52.10 | sec_fived16_gen.tex:91 |
| `sens-lateral-gcv-a0.5` | 69.88 | 48.11 | sec_fived16_gen.tex:91 |
| `sens-lateral-gcv-a1` | 66.18 | 45.20 | sec_fived16_gen.tex:91 |
| `sens-lateral-gibuu-a0.1` | 43.64 | 39.06 | sec_fived16_gen.tex:94 |
| `sens-lateral-gibuu-a0.25` | 40.65 | 36.83 | sec_fived16_gen.tex:94 |
| `sens-lateral-gibuu-a0.5` | 38.35 | 34.99 | sec_fived16_gen.tex:94 |
| `sens-lateral-gibuu-a1` | 36.82 | 33.69 | sec_fived16_gen.tex:94 |
| `sens-lateral-gmec-a0.1` | 194.16 | 128.07 | sec_fived16_gen.tex:92 |
| `sens-lateral-gmec-a0.25` | 171.44 | 117.78 | sec_fived16_gen.tex:92 |
| `sens-lateral-gmec-a0.5` | 152.95 | 107.88 | sec_fived16_gen.tex:92 |
| `sens-lateral-gmec-a1` | 138.34 | 98.18 | sec_fived16_gen.tex:92 |
| `sens-lateral-nuwro-a0.1` | 117.68 | 85.45 | sec_fived16_gen.tex:93 |
| `sens-lateral-nuwro-a0.25` | 110.10 | 81.15 | sec_fived16_gen.tex:93 |
| `sens-lateral-nuwro-a0.5` | 102.88 | 77.07 | sec_fived16_gen.tex:93 |
| `sens-lateral-nuwro-a1` | 110.21 | 77.99 | sec_fived16_gen.tex:93 |
| `sens-lateral-tune-a0.1` | 223.84 | 146.01 | sec_fived16_gen.tex:95 |
| `sens-lateral-tune-a0.25` | 200.25 | 136.39 | sec_fived16_gen.tex:95 |
| `sens-lateral-tune-a0.5` | 179.78 | 125.96 | sec_fived16_gen.tex:95 |
| `sens-lateral-tune-a1` | 165.30 | 115.75 | sec_fived16_gen.tex:95 |
| `sig-C_total_resp-R00` | 7.10 | 7.40 | appC_supplementary.tex:157, sec_fived16.tex:20 |
| `sig-C_total_resp-R01` | 7.10 | 7.39 | appC_supplementary.tex:158, sec_fived16.tex:21 |
| `sig-C_total_resp-R02` | 14.00 | 14.39 | appC_supplementary.tex:159, sec_fived16.tex:22 |
| `sig-C_total_resp-R03` | 12.64 | 13.38 | appC_supplementary.tex:160, sec_fived16.tex:23 |
| `sig-C_total_resp-R04` | 4.20 | 4.38 | appC_supplementary.tex:162, sec_fived16.tex:24 |
| `sig-C_total_resp-R05` | 7.47 | 7.92 | appC_supplementary.tex:163, sec_fived16.tex:25 |
| `sig-C_total_resp-R06` | 5.89 | 6.76 | appC_supplementary.tex:164, sec_fived16.tex:26 |
| `sig-C_total_resp-R07` | 7.98 | 8.98 | appC_supplementary.tex:165, sec_fived16.tex:27 |
| `sig-C_total_resp-R08` | 6.25 | 6.55 | appC_supplementary.tex:167, sec_fived16.tex:28 |
| `sig-C_total_resp-R09` | 6.26 | 6.45 | appC_supplementary.tex:168, sec_fived16.tex:29 |
| `sig-C_total_resp-R10` | 8.59 | 9.03 | appC_supplementary.tex:169, sec_fived16.tex:30 |
| `sig-C_total_resp-R11` | 13.69 | 14.07 | appC_supplementary.tex:170, sec_fived16.tex:31 |
| `sig-C_total_resp-R12` | 6.63 | 6.95 | appC_supplementary.tex:172, sec_fived16.tex:32 |
| `sig-C_total_resp-R13` | 11.07 | 11.57 | appC_supplementary.tex:173, sec_fived16.tex:33 |
| `sig-C_total_resp-R14` | 5.27 | 5.48 | appC_supplementary.tex:174, sec_fived16.tex:34 |
| `sig-C_total_resp-R15` | 7.94 | 8.34 | appC_supplementary.tex:175, sec_fived16.tex:35 |
| `sig-reported-R00` | 7.11 | 7.42 | appC_supplementary.tex:157, sec5_multidim.tex:27, sec_fived16.tex:20 |
| `sig-reported-R01` | 7.59 | 7.87 | appC_supplementary.tex:158, sec5_multidim.tex:28, sec_fived16.tex:21 |
| `sig-reported-R02` | 14.05 | 14.44 | appC_supplementary.tex:159, sec5_multidim.tex:29, sec_fived16.tex:22 |
| `sig-reported-R03` | 12.73 | 13.47 | appC_supplementary.tex:160, sec5_multidim.tex:30, sec_fived16.tex:23 |
| `sig-reported-R04` | 4.80 | 4.96 | appC_supplementary.tex:162, sec5_multidim.tex:32, sec_fived16.tex:24 |
| `sig-reported-R05` | 8.12 | 8.53 | appC_supplementary.tex:163, sec5_multidim.tex:33, sec_fived16.tex:25 |
| `sig-reported-R06` | 6.56 | 7.35 | appC_supplementary.tex:164, sec5_multidim.tex:34, sec_fived16.tex:26 |
| `sig-reported-R07` | 8.45 | 9.41 | appC_supplementary.tex:165, sec5_multidim.tex:35, sec_fived16.tex:27 |
| `sig-reported-R08` | 6.26 | 6.56 | appC_supplementary.tex:167, sec5_multidim.tex:37, sec_fived16.tex:28 |
| `sig-reported-R09` | 6.85 | 7.02 | appC_supplementary.tex:168, sec5_multidim.tex:38, sec_fived16.tex:29 |
| `sig-reported-R10` | 8.69 | 9.12 | appC_supplementary.tex:169, sec5_multidim.tex:39, sec_fived16.tex:30 |
| `sig-reported-R11` | 13.89 | 14.26 | appC_supplementary.tex:170, sec5_multidim.tex:40, sec_fived16.tex:31 |
| `sig-reported-R12` | 6.98 | 7.28 | appC_supplementary.tex:172, sec5_multidim.tex:42, sec_fived16.tex:32 |
| `sig-reported-R13` | 11.38 | 11.87 | appC_supplementary.tex:173, sec5_multidim.tex:43, sec_fived16.tex:33 |
| `sig-reported-R14` | 5.68 | 5.88 | appC_supplementary.tex:174, sec5_multidim.tex:44, sec_fived16.tex:34 |
| `sig-reported-R15` | 8.29 | 8.67 | appC_supplementary.tex:175, sec5_multidim.tex:45, sec_fived16.tex:35 |
| `sigmed-C_total_resp` | 7.29 | 7.66 | appC_supplementary.tex:177, records_r05_sixteen.tex:134, records_r05_sixteen.tex:144 ... |
| `sigmed-reported` | 7.86 | 8.20 | appC_supplementary.tex:177, records_r05_sixteen.tex:134, records_r05_sixteen.tex:144 ... |
| `sigratio-max` | 1.220 | 1.278 | records_r05_sixteen.tex:171, sec5_multidim.tex:60, sec_fived16.tex:137 |
| `sigratio-med` | 1.048 | 1.103 | records_r05_sixteen.tex:171, sec_fived16.tex:137 |
| `sigratio-min` | 1.011 | 1.051 | records_r05_sixteen.tex:171, sec_fived16.tex:137 |
| `x-QA-rho0` | 0.92 | 0.88 | appC_supplementary.tex:212, records_r05_sixteen.tex:250, sec_fived16.tex:92 |
| `x-QA-rho1` | 0.99 | 0.95 | appC_supplementary.tex:212, records_r05_sixteen.tex:250, sec_fived16.tex:92 |
| `x-QA-z0` | +0.051 | +0.042 | sec_fived16.tex:92 |
| `x-QA-z1` | +0.162 | +0.065 | sec_fived16.tex:92 |
| `x-QB-rho0` | 0.91 | 0.88 | sec_fived16.tex:93 |
| `x-QB-rho1` | 0.99 | 0.95 | sec_fived16.tex:93 |
| `x-QB-z0` | -0.106 | -0.088 | sec_fived16.tex:93 |
| `x-QB-z1` | -0.311 | -0.141 | sec_fived16.tex:93 |
| `x-QC-rho0` | 0.77 | 0.74 | appC_supplementary.tex:212, records_r05_sixteen.tex:250, sec_fived16.tex:94 |
| `x-QC-rho1` | 0.96 | 0.92 | appC_supplementary.tex:212, records_r05_sixteen.tex:250, sec_fived16.tex:94 |
| `x-QC-z0` | -0.414 | -0.384 | sec_fived16.tex:94 |
| `x-QC-z1` | -0.981 | -0.707 | sec_fived16.tex:94 |
| `x-QD-rho0` | 0.89 | 0.86 | sec_fived16.tex:95 |
| `x-QD-rho1` | 0.98 | 0.95 | sec_fived16.tex:95 |
| `x-QD-z0` | +0.275 | +0.237 | sec_fived16.tex:95 |
| `x-QD-z1` | +0.688 | +0.389 | sec_fived16.tex:95 |
| `x-nopair-chi2-r0` | 0.792 | 0.696 | sec_fived16.tex:99 |
| `x-nopair-chi2-r1` | 1.156 | 0.787 | sec_fived16.tex:99 |
| `x-nopair-p-r0` | 0.939 | 0.952 | sec_fived16.tex:99 |
| `x-nopair-p-r1` | 0.885 | 0.940 | sec_fived16.tex:99 |
| `x-nopair-zmax` | 0.467 | 0.424 | sec_fived16.tex:99 |
| `x-prim-chi2-r0` | 1.160 | 0.828 | appC_supplementary.tex:212, records_r05_sixteen.tex:250, sec_fived16.tex:97 |
| `x-prim-chi2-r1` | 1.232 | 0.878 | appC_supplementary.tex:212, appC_supplementary.tex:212, records_r05_sixteen.tex:250 ... |
| `x-prim-p-r0` | 0.885 | 0.935 | records_r05_sixteen.tex:250, sec_fived16.tex:97 |
| `x-prim-p-r1` | 0.873 | 0.928 | records_r05_sixteen.tex:250, sec_fived16.tex:97 |
| `x-prim-zmax` | 0.981 | 0.707 | appC_supplementary.tex:212, sec_fived16.tex:97 |
| `x-qr-chi2-r0` | 0.780 | 0.491 | sec_fived16.tex:98 |
| `x-qr-chi2-r1` | 0.925 | 0.515 | sec_fived16.tex:98 |
| `x-qr-p-r0` | 0.941 | 0.974 | sec_fived16.tex:98 |
| `x-qr-p-r1` | 0.921 | 0.972 | sec_fived16.tex:98 |
| `x-qr-zmax` | 0.714 | 0.547 | sec_fived16.tex:98 |
| `x-zmax` | 0.981 | 0.707 | records_r05_sixteen.tex:250 |

Moved but not printed: 1106 keys (in vf_readings.json).

## 3. The printed-xk check (A4)

With this Mac's OLD replay in place of the committed k.json, every generated value equals its committed-k.json value: True (all 3944 generated keys compared, xk-dependent or not; 0 differ).

## 4. The S1/C_resp sigma rows both ways, and the per-cell sigma

The C_e form is the OLD value; the C_e^infl form is from the V_F data product (phase1_readings.py, its section 3, has all sixteen cells). Joseph's open question (declaration section 4.3).

## 5. Follow-ups for other lanes (after the director's review)

- make_values_fived16.py: READOUTS, NOPL_READOUTS (the V_F files above), ARMS (VF_ARMS), MATRIX_KEYS; its literal "C_total_plus_C_resp" (:678, :689) and the C_PL5D label (:700-702) as supplied here; make_values_landed.py's "vr".
- make_supplemental.py, fived16_headline, fived16_genresidual, the EA2 redraw, valid_region.py's COV_KEY.

Shims in the V_F run (the note's literal names): BLOCK[<V_F block name>] := a PLACEHOLDER label, so a diagnostic whose dominant component is the V_F block prints; the label itself is note wording (JE/Joseph) | dp.relative_sigma.C_total_plus_C_resp := the V_F C_total + C_resp + DeltaC_e sigma (make_values_fived16 :678, :689); cresp.relative_sigma.C_total_resp := the same values (that row's V_F form) | without-C_PL5D arm: dp.correlation := the correlation of C_total + C_resp + DeltaC_e (M_ij/sqrt(M_ii M_jj) from the V_F product's own matrix), correlation_of := its name, as the OLD nopl product carries for its arm | dp.labels.block := C_PL5D's label from the pinned with-cpl product (:700-702 parse it; V_F's own is kept as block_DeltaC_e)

NOT CITABLE FOR: a validated size for C_e^infl; a coverage or calibration statement; any note wording.
