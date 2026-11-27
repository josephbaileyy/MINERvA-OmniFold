# PTMC confirm-read dispositions (r4 at 643d1adbc → the amended r4)

All three class findings are ACCEPTED and fixed. The NOTES are answered in wording.

| finding | class | what it said | fix |
|---|---|---|---|
| 1 | (a) | calling the identity measured on the driver's population exceeds the receipt, because the script's 20° cut uses `np.arctan2` and the driver's `math.atan2`, and the two masks were not compared | §2.2 now scopes the measurement to the script's reproduction of the loaders' rules, names the angle-function difference, and says the measurement is evidence that the gate will pass, not the gate itself. The binding gate is C-COUPLE on the driver's own arrays in `p_off_c` and `p_R_c`, which fails closed |
| 2 | (c) | 1.5 × (10 t_R) + o on five nodes reserves about 14.7 node-h, over the 12.1 left, so the submit rule would stop a run that passes the projection | §7: L = min(1.5 × (10 t_R) + o, cap left / 5), rounded down; launch only if L ≥ 1.1 × (10 t_R + o), otherwise STOP. At the scoped timing L ≈ 2 h 25 min against ≈ 1 h 57 min of runtime, and the five reservations stay within the cap left |
| 3 | (b) | a replica could inject a retained background entry twice and pass, because C-DRAW-R derives the expected injection from that replica's own fill record | C-MOVE now compares each R replica's ordered fill records (entry, p_T, p∥, w × POT) with `p_off_b1`'s minus the rows file's entries, order and multiplicity preserved. The expected injection is derived from that filtered reference. The scorer implements it (code PR) |
| NOTES | — | the coupling is a value-preserving pairing (no event IDs), and sums can differ by summation order; C-NORM's edges against hUnfold's axes; C-NORM's anchor | §2.2 already says "1 up to summation order". C-NORM now names its anchor (C-BASE, with C-FIX for `p_R_c`) and says C-GRID covers the bin widths |
