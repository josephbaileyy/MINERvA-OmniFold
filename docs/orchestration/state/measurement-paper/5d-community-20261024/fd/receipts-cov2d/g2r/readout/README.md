# COV2D-G2R readout: data, G18 and AR23 (2026-11-14)

**By** the `cov2d` session, under COV2D-G2R addendum J1 (code at M = `401733bce290ce122cfbf38f1526e120f174b3ec`).
One dir per phase (`data/`, `G18/`, `AR23/`), each with its README, connect, connect log, launch records, overlap check,
readout log, records and digests. `d1/` holds the reading below: the fetch, the node sha256 list, `dump_d1.py` and its
output.

**CANNOT AUTHORIZE:** adopting the rebuilt covariance, or any paper or note wording. D1's adoption is Joseph's
(`DECISION-20261112-joseph-consult-d1-d7.md`:20-25; COV2D-G2R-BINDING-1.md:141-144). This README states figures as
read and the rules as written. It draws no outcome.

- **Launcher:** `launch-g2r.sh` `1f719ba321b9c0388464615cf70a534a5c6c42691efb77d77106f2f6751fc24e`. It is the batch
  launcher `ebf576f5…` (`../D_Uc/launch-g2r.sh`) plus one arm, `readout-data|readout-G18|readout-AR23`, and the usage
  lines (`launch-g2r-readout-vs-ebf576f5.diff.txt`). Its tests: `test_launch_g2r.1f719ba3.out.txt`
  (`../envtest/test_launch_g2r.sh`: LAUNCH-G2R TEST PASS) and `test_launch_readout_arms.out.txt` (each arm with a dummy
  digest is REFUSED, rc 2). The connects' place, verdict and copy-out blocks were tested by `test_readout_place.sh`
  (`test_readout_place.out.txt`) before coverage-5b-audit's review of rev 2 (M1 and M2 closed, no blocker or major).
- **Overlap with LL5D** (the director's condition): `readout_ovl.py` stats every file under `$O`, the MAT preflight
  file and the MAT setup scripts, against LL5D's 1146 protected paths (the bulk's atime-pre `908d3922…`), by realpath
  and device:inode. Each phase's `readout-ovl-<PH>.out.txt` reads `hits []`.
- **Order:** data 03:53:34Z–03:54:39Z, G18 04:00:54Z–04:07:05Z, AR23 04:09:13Z–04:15:36Z, each after the previous
  phase's DONE, PASS and verified outputs. The LL5D rc-129 rerun job 61255888 was pending throughout.

## The D1 reading, as read

The figures come from `score_g2r_<T>.json` and `data_g2r.json` here, and from COV2D's committed
`../../readout/<T>/score_<T>.json`, printed side by side by `d1/dump_d1.py` (`d1/dump_d1.out.txt`). Rule citations are
file:line at origin/main `07cc59a05df4e4c04fe0ea37ecfea8ea8c7f51e2`.

**The rule** (COV2D-DECLARATION.md:257-273, applied unchanged by COV2D-G2R-DECLARATION.md:126-134):
- A cell under-covers if #{t : |e_tc| ≤ σ_c} ≤ k_c(T), the largest k with P(Bin(300, p_c(T)) ≤ k) < 0.025/205,
  against the draw-matched null (:269).
- Joint under-coverage is #{χ²_t in region} ≤ k_J(T), the largest k with P(Bin(300, q(T)) ≤ k) < 0.025 (:270).

**G18**, G2R (C_T′) beside COV2D (C_T):
- The cells with count ≤ k_cell are [29] under both, equal to `flagged_cells`. Cell 29: count 148, k_cell 174 (C_T′)
  and 175 (C_T).
- `joint_count` 0 of 300 under both; `k_joint` 192 under both.
- Verdict UNDER-COVERS under both; ndf 205.

**AR23**, G2R (C_T′) beside COV2D (C_T):
- The cells with count ≤ k_cell are [29, 56] under both. Cell 29: count 164, k_cell 174. Cell 56: count 148,
  k_cell 174. Both sides read the same.
- `joint_count` 0 of 300 under both; `k_joint` 190 under both.
- Verdict UNDER-COVERS under both; ndf 204.

**Part (a), at the data** (COV2D-G2R-DECLARATION.md §3 :95-115; the outcome table's part (a) rows :229-232; controls
:192, :206):
- `data_g2r.json` reads verdict PASS, `controls_failed` [], `stop` [], `atime_moved` [], G6 pass (worst_rel 4.59e-16)
  and G10 pass. `products.tsv` has 177 rows.
- **ε**, against C_rep: 25.833 on the retained 205 directions, 5.999 on the largest 73 and 15.376 on the largest 139.
  The coupling to the discarded directions is at most 3.1e-41.
- **Correlations:** the largest |Δρ| is 0.12995; the median is 0.007895.
- **Rank:** 205 before, 205 after.
- **Uncertainties:** the median per-bin relative σ goes from 6.41367 % to 6.46302 %; the integrated σ from 4.75917 %
  to 4.75912 %.
- **Noise floor** (:112-114): neither floor universe reproduced part B bitwise (Flux:23 and MaRES:0 both False). Their
  ε is printed as the floor: 2.59e-10 on the retained directions, 7.88e-11 on 73 and 1.48e-10 on 139.

**"The held-out constructions validate"** (D1's condition): the G2R declaration, binding 1, amendment 1 and addendum
J1 define no separate rule for this. The nearest declared reading is part (+) VALID or INVALID (COV2D-G2R-DECLARATION.md
:268-270), with INVALID at a tune exactly when a control fails (COV2D-DECLARATION.md:273; G2R :192, :206). At both
tunes:
- `controls_failed` [] and `stop` [];
- G6 pass (C_T, C_T_minus and C_univ bitwise);
- G7 pass (chi2_rel_diff 0.0);
- `section_9_8` pass;
- `atime_moved` [];
- 175 products each.

No document fixes how D1's word maps onto this reading. That mapping is the director's and Joseph's.

**Descriptive, no verdict** (as emitted):
- **Attribution:** every flagged cell is driven by "bias".
  - G18 R29: pull_mean −0.959 ± 0.038, pull_sd 0.663.
  - AR23 R29: −0.848 ± 0.037, pull_sd 0.634.
  - AR23 R56: +1.037 ± 0.041, pull_sd 0.707.
- **s_c:** G18 cell 29 1.340; AR23 cell 29 1.160 and cell 56 1.311.
- **Mean χ²/ndf:** G18 25.03 ± 0.41 (C_T: 24.17 ± 0.37); AR23 16.41 ± 0.16 (C_T: 16.55 ± 0.17).
- **Outlier cell 216,** not flagged: count 261 against k 173 at G18, 247 against k 173 at AR23.
- **Weakened passes:** 10 cells at G18 and 53 at AR23, the same lists as COV2D's.
- **Leave out MEC:** `flagged_under_minus` is [29, 30] at G18 and [29, 30, 56] at AR23; it is printed with "no reading
  (the tune under-covers under C_T)".
- **Tune ε (C_T′ against C_T):**
  - G18: 6.681 on the retained directions, 1.838 on 73, 3.897 on 139; max |Δρ| 0.0349.
  - AR23: 7.476, 1.974 and 4.331; max |Δρ| 0.0414.

**Not produced, reported unrepaired:**
- What the declaration asks for: COV2D-G2R-DECLARATION.md:135-137 lists T2A's decomposition (ēᵀC_T⁺ē and tr(C_T⁺S))
  and its joint test truncated to the 73 and 139 largest eigenpairs among the regrade's descriptive readouts, and the
  §10 "unchanged" row (:241) replaces "the decomposition's parts and the truncated counts" with the regrade's.
- What the records and code show: neither tune's record holds them. `g2r_readout.py` at M does not import
  `t2a_split`, and `RANKS = (73, 139)` in `g2r.py` serves only the ε truncations.
- No verdict or count above depends on them.
