# RE-1 report 2: C2, P3, P4, the movement table and F (record)

**Run by** the re-1 lane (Claude) for the director, 2026-10-22. It ran under
[`RE1-AMENDMENT-DECLARATION.md`](RE1-AMENDMENT-DECLARATION.md), as bound in
[`RE1-AMENDMENT-BINDING.md`](RE1-AMENDMENT-BINDING.md) (PR #251) and
[`RE1-AMENDMENT-BINDING-F.md`](RE1-AMENDMENT-BINDING-F.md) (PR #263). It follows [`../RE1-REPORT.md`](../RE1-REPORT.md).
Six jobs charged **1.627 of the 6.0 CPU node-h** cap. Readouts, receipts, logs and figures are in [`run2/`](run2/).
The products are on pscratch under `/pscratch/sd/j/josephrb/methods-paper/re1-20261022/out/`.

**Outcome:**
- **K1-2D and K1-ND both pass.**
- **C2 is FLAG under the declared rule.** In 14 of the 205 cells, the mean refined − purity difference exceeds
  1 σ_stat. The rule says that this "flags it for Joseph's decision on the adopted 2D result".
  - The integral clause does not fire: −0.198 % against the 0.5 % bar.
  - In the 14 cells, the purity arm's mean residual against truth is +0.78 to +5.89 σ_stat. The refined arm's is
    within ±0.44 σ_stat (§2).
- **P3 and P4 exist in configuration (e).** The movement table covers 2D, 3D, 4D and 5D (§3). In 5D, in the
  adopted trunk's total σ, the per-cell maximum is 0.857 for (e) − (c) and 0.786 for (e) − (a). DECISION-20260920's
  M4 travels with these: the estimator seed alone moves single 5D bins by up to 49.8 % of σ.
- **F:**
  - Five of the eight figures in the declared research list are regenerated from P3/P4.
  - fig:eavail-marg (K3 failed), fig:q3excess and the PET-vs-GBDT figure are not regenerated.
  - The printed 3D numbers are re-evaluated (§4), and thirteen of them change at their printed precision. One
    side finding is for the director: the note's "+0.95 % total σ" is computed against the published 2D result's
    reported bins, not against "the 2D result of §results" that the note names.

**CITABLE FOR:**
- the C2 readout and its verdict under the declared rule;
- the controls;
- the movement table;
- the regenerated figures and numbers, with the labels given here;
- the ledger.

**NOT CITABLE FOR:**
- a change to the adopted 2D result or its uncertainty (Joseph's decision);
- a covariance or coverage for configuration (e). C2 is a nominal-truth closure with 20 seeds, not a coverage test;
- a verdict on the background-treatment obligation (OI-6). The movement table is descriptive;
- any deliverable edit (the director integrates).

---

## Code, inputs and environment

**Code.**
- J1–J3 and the readouts ran from a clean clone detached at the declared `ec829e28`.
- F ran from clean clones at the report branch's commits. Each clone was checked as clean at its sha before and after
  its job:
  - F1 at `b3d89421`;
  - F1b at `1e92657c`;
  - F2 at `e4886f90`;
  - the C2 supplement at `651163e9`.
- Nothing was written under any checkout. The shared checkout was not touched.

| new file since the declaration (all under the lane's file set) | sha256 |
|---|---|
| `nd-unfolding/re1/re1_to_root.py` (P3/P4 container conversion) | `f3bc6cf968191212b343a5cddd85d3fa9ca9971845232d5cf7ac19877bbbae84` |
| `nd-unfolding/re1/re1_f_numbers.py` (printed 3D numbers, K3 per number) | `34d52217823c1eb0204390242beb3791f0a7db0c6968c35513f496eef57c7abe` |
| `nd-unfolding/re1/re1_cmp_fig.py` (K3 figure comparison) | `4acb4fa9a4e0ad83290694dd9f1dff2e9980a6cf9760e3570f707879bf64a258` |
| `nd-unfolding/re1/redraw_central_only_p3.py` (F-R1 copy) | `ee694e1d40c37b3919118c957d8d22f6292f6899fcf7ede99de604e2c1ea3188` |
| `nd-unfolding/re1/redraw_central_only_p4.py` (F-R1 copy) | `85039894d760a299b52561c7dff900ea25c42d1f3dc73ef2fcdad028b1bd0d57` |
| `2d-unfolding/re1/re1_c2_supplement.py` (the director's C2 additions) | `53cf457499648ddaabcd58af31bca4b40601fd9f99c6c59aa35453ce0f9872fd` |
| `2d-unfolding/re1/re1_c2_cells.py` (per-cell C2/D2 table, SE counts; review round) | `fd303cc44a7deef9f95abe88ea2c3eaa528d0202bfb9466d428c3fa14f9042c9` |
| `nd-unfolding/re1/re1_report2_extras.py` (3D totals, marginal scatter, 5D (c) − (a) in trunk σ; review round) | `a8ee2d2cfc3da741c82cd7e1818c953b03cc1f88368e9786288a3c7234a1f112` |
| `run2/launch/readouts/` (the login-node wrappers that ran the readouts, the supplement's invocation, the review-round runner) | `re1_mv.sh` `02018679…`, `re1_2dro.sh` `7a178c62…` (equal to the copies run on pscratch) |
| `run2/launch/re1_f_env.sh`, `re1_f1.sbatch`, `re1_f1b.sbatch`, `re1_f2.sbatch`, `re1_ledger.sh` | `734e3d64…`, `91b5d90a…`, `a7cdc9d3…`, `0a1541f0…`, `eb586b0d…` |

The declared code that produced results is unchanged: `re1_2d.py` `b9c7e1da…`, `re1_2d_analyze.py` `8bd96760…`,
`re1_nd_movement.py` `c562e365…`. One declared file was modified after the results:
`nd-unfolding/re1/tests/test_re1_readouts.py`, from `6727ff2a…` (declared) to `7f90a9a3…` (651163e9). The change adds
one test for the supplement; the readout tests pass 10/10 locally.

**F-R1 copies.** Each copy differs from `docs/analysis-note/redraw_central_only.py` (`0961fc06…`, unchanged) in one
data pin only. The full `git diff --no-index` outputs are [`run2/f-r1/`](run2/f-r1/) (`de4b55b3…`, `099f3948…`).
Quoted:

```
-    "xsec_3d_MEFHC_5iter_lgbm.root": "0dd94830821576a3b060fae2d4a20564610c535ed06046cd1eb05cd11885dd59",
+    "xsec_3d_MEFHC_5iter_lgbm.root": "c16b622b4970800121b1d92dad91407878e0f4546375bfe27cdd3257d46d8c63",
```
```
-    "xsec_4d_MEFHC_5iter_lgbm.root": "1fb8250820c00428fc547cb05aa95535023146723acdccb61f615f3fa763f9d2",
+    "xsec_4d_MEFHC_5iter_lgbm.root": "ece4055e29756eeef81932b93199d507ca69296bbe7a90b2776c0c39a330998e",
```

Both copies still refuse other bytes. On the current 3D and 4D products, each exited 1 with
`sha256 0dd94830… != recorded c16b622b…` (respectively `1fb82508… != ece4055e…`) and wrote nothing (login node,
before F2).

**Inputs.**
- The inputs are the declaration's §3 table, each re-hashed by the job that read it.
- The new intermediates are in [`run2/receipts/SHA256SUMS.inputs`](run2/receipts/SHA256SUMS.inputs):

| file | sha256 |
|---|---|
| 2D cache `2d/cache.npz` | `eb1e3477ac84a92d2498c2df6aad25e745f7f439a4cea3f784f6ef5a412d0652` |
| `3d/of_inputs_3d.npz` | `ecbff9f888ab19b5b9f7575ab41a27f83ab094f80efd4463790978c0145c318d` |
| `3d/bkg_3d.npz` | `b99a19ef65f904fe9b57e43fa4a57d3d259d92eea9c2b31c25df491c4c8ef826` |
| `4d/of_inputs_4d.npz` | `a15cc6905f1273365f0116a973b0cbb28034b49a4d455da338ff9e5d8462b166` |
| `4d/bkg_4d.npz` | `2c3cc1a870302240b90b5f9e96e3a2ad5dc2765cfcd733b4fc8a2a0214d3ab8d` |

The dumpers' built-in check passed for both 3D and 4D (J1 exit 0). It requires `s5c_dump_bkg.py` to reproduce the
npz's purity weights and measured coordinates exactly.

**Environment.**
- Software: `root_6_28` (Python 3.11.14, numpy 1.26.4, LightGBM 4.6.0).
- J3: every 2D product records its affinity: 64 CPUs, `joblib_cpu_count` 64, `OMP_NUM_THREADS` 64, host nid006698.
- J2: the s5 path fixes LightGBM `num_threads` at 32 in its recorded estimator parameters. Its products record that
  value, not an affinity. The affinity of each J2 step is in `sacct`: 42 CPUs, `--cpu-bind=cores`. This is a
  deviation from the binding's "each product records its affinity" (see Deviations).
- Figures were rendered on Perlmutter (matplotlib 3.10.8, the version recorded in the current PDFs).

## 1. Controls

| control | result |
|---|---|
| **K1-ND** | **PASS.** The P5 rerun's `xsec_flat` (65,856 entries) equals P5 `fb5cc679…` bit for bit (`tobytes` equal). The s5 modules' recorded digests equal P5's: `s5n_pseudo` `8981f97b…`, `s5c_pseudo` `d81d4f46…`, `s5c_unfold` `510d749a…`, `s5e_candidate` `bda8c48c…`, `s5e_deform` `6726ff99…`, `omnifold_nn_core` `24f87f11…`, `xsec_nd` `454001f3…`. So does the refinement override (400/31). The 2D driver's recorded digest differs (`74a4ed69…` now, `8ebe0277…` for P5). P5 also records `s5e_trace.py` and `s5p_numerics.py`, its wrapper, which the rerun does not use. The declared condition names only the s5 modules, and the result is bitwise. |
| **K1-2D** | **PASS.** The purity data unfold equals `E_U`'s `hXSec2D` on the 205 reported cells: max relative difference 2.3e-13 (median 2.4e-14), same cell set, tolerance 1e-8. It is not bitwise. |
| **dumpers** | passed (above) |
| **K2** | reported only: no recorded 2D purity closure with background exists (RE1-REPORT §2) |
| **K3, figures** | Six figures from four producer runs on the current inputs, compared with `docs/analysis-note/figures/*.pdf` at `b3d89421`. The PDF `/CreationDate` value was normalized, length-preserving; nothing else was. **Five are bitwise equal:** `eavail_spectrum`, `generators_vs_unfolded_band_central`, `mode_decomp_eavail_central`, `compare_mec_eavail_central`, `ascencio_fullcov_compare_central`. **`eavail_marginal_vs_paper_pull_full` fails.** Its text and printed values are identical (pull mean 0.16, rms 0.83, χ²/ndf 4.98), but the panel geometry differs, and the committed PDF dates from 2026-07-03. PNGs were not compared. [`run2/f/k3/k3_compare.jsonl`](run2/f/k3/k3_compare.jsonl) |
| **K3, numbers** | §4: each printed number is taken under the definition that reproduces it on the current product, or it is not regenerated |
| **conversion** | P3 → `xsec_3d_p3.root` `c16b622b…`. The 3D driver's writers were used, and the control reproduces the current product's stored `hXSec2D`, `hXSec_pt`, `hXSec_pz` and `hXSec_eavail` bit for bit. P4 → `xsec_4d_p4.root` `ece4055e…` (`write_thnd`; the current product round-trips bit for bit). Both readbacks are bitwise, read back by `re1_to_root.py`'s own reader, not by each producer's loader (Deviation 7). In 3D, only `hXSec3D` is read back; the projections are written from the same array. The producers' own reads are the F2 runs, whose `[input]` lines show the pinned digests. [`run2/f/new/conv3.json`](run2/f/new/conv3.json), [`conv4.json`](run2/f/new/conv4.json) |

The refinement, as recorded in each product (400 trees, 31 leaves, `random_state` 45):

| product | clipped fraction | refined / signed sum |
|---|---|---|
| P3 | 1.24e-4 | 1.0000023 |
| P4 | 4.41e-4 | 1.0000174 |
| P5 rerun | 4.56e-4 | 1.0000184 |
| D2 (2D data) | 0 | 0.9999996 |

## 2. C2: the 2D closure

**What it is.** Pseudo-experiments at **nominal truth** (the truth model equals the prior), with background included:
- They are drawn as in s5n, in 2D: keyed signal and background splits and Poisson(2w) draws.
- Pseudo-seeds 1–20 were used, both arms on the same pseudo-data and template D.
- The truth is identical across the seeds (max relative spread 7.2e-16).

C2 is a closure with 20 seeds. It is **not** a coverage test. The yardsticks are:
- σ_stat: `sqrt(diag(stat))` of the S5 production covariance `6689d2fc…`;
- σ_total: `sqrt(diag(total_plus_C_PL))` of Q `8ccb4d72…`, the adopted 2D uncertainty;
- both on `E_U`'s 205 reported cells.

The sources are [`run2/readouts/readout_2d_full.json`](run2/readouts/readout_2d_full.json) (declared readout) and
[`c2_supplement.json`](run2/readouts/c2_supplement.json) / [`.tsv`](run2/readouts/c2_supplement.tsv) (the director's
additions).

**Verdict under the declared rule: FLAG.** The flag goes to Joseph through the director. The rule is: FLAG if any
cell's mean arm difference exceeds 1 σ_stat, or the integrated difference exceeds 0.5 %.
- **Per-cell clause: fires.** 14 cells exceed 1 σ_stat. The largest is −5.45 σ_stat (SE 0.46), at gid 128.
- **Integral clause: does not fire.** The integrated mean arm difference is −0.198 % of the integrated truth
  (SE 0.002 %).

**Summary over the 205 cells (mean over 20 seeds):**

| quantity | median abs | p84 abs | max abs (gid) | cells > 1 | cells > 0.5 |
|---|---|---|---|---|---|
| arm difference (ii − i), σ_stat | 0.124 | 0.387 | 5.45 (128) | 14 | 20 |
| arm difference (ii − i), σ_total | 0.013 | 0.036 | 1.13 (128) | 1 | 2 |
| purity arm − truth, σ_stat | 0.088 | 0.350 | 5.89 (128) | 13 | 21 |
| purity arm − truth, σ_total | 0.010 | 0.032 | 1.22 (128) | 1 | 2 |
| refined arm − truth, σ_stat | 0.082 | 0.187 | 0.44 (128) | 0 | 0 |
| refined arm − truth, σ_total | 0.009 | 0.020 | 0.09 (128) | 0 | 0 |

**Seed spread against the yardstick.** This is each arm's per-cell SD across the 20 seeds, divided by σ_stat:
- purity arm: median 0.46 (range 0.06–2.38);
- refined arm: median 0.58 (range 0.06–1.46).

In the median cell, the pseudo-experiment spread is therefore about half of σ_stat. The SE of a 20-seed mean is
SD/√20: a median of 0.10 σ_stat (purity) and 0.13 σ_stat (refined). In the flagged cells, the purity SD/σ_stat ranges
from 0.74 to 2.38 (table below).

The source of this factor of about 2 between the pseudo-experiment spread and σ_stat is not established here. The
two differ in construction: σ_stat is the adopted data-statistics covariance, while the pseudo-experiments draw
Poisson(2w) from half-samples of the MC. The FLAG rule uses σ_stat as declared.

**Each arm against its own SE** (|mean| / SE over the 20 seeds; [`c2_cells.json`](run2/readouts/c2_cells.json)).
About 9.3 cells beyond 2 SE are expected by chance if every mean is zero:

| | cells > 2 SE | cells > 3 SE | max |t| |
|---|---|---|---|
| purity arm − truth | 57 | 29 | 14.7 |
| refined arm − truth | 11 | 1 | 3.09 |
| arm difference (ii − i) | 114 | 74 | 29.0 |

The refined arm's largest is 3.09 SE at gid 49, which is not flagged. Among the flagged cells, its largest are
2.35 SE at gid 48 and 2.10 SE at gid 128 (from the readout's per-cell SE). So "within ±0.44 σ_stat" is a statement in
σ_stat, not a statement that the refined arm's mean is zero.

**The flagged cells.** Columns:
- gid = ix·16 + iy; pT and p∥ are in GeV/c;
- B/D is the purity background fraction of the cell's reco bin, from the driver's reco histograms in the cache;
- its rank is out of 205, with 1 the largest.

| gid | pT | p∥ | B/D (rank) | purity − truth, σ_stat / σ_total | refined − truth, σ_stat / σ_total | ii − i, σ_stat (SE) / σ_total | purity SD/σ_stat |
|---|---|---|---|---|---|---|---|
| 0 | 0–0.07 | 1.5–2.0 | 0.464 (1) | +2.54 / +0.59 | −0.21 / −0.05 | −2.75 (0.11) / −0.64 | 1.19 |
| 16 | 0.07–0.15 | 1.5–2.0 | 0.331 (2) | +4.56 / +0.50 | +0.04 / +0.00 | −4.52 (0.16) / −0.49 | 1.42 |
| 32 | 0.15–0.25 | 1.5–2.0 | 0.187 (6) | +2.80 / +0.24 | +0.07 / +0.01 | −2.73 (0.12) / −0.23 | 0.93 |
| 48 | 0.25–0.33 | 1.5–2.0 | 0.114 (12) | +2.42 / +0.16 | +0.35 / +0.02 | −2.06 (0.09) / −0.14 | 0.74 |
| 64 | 0.33–0.40 | 1.5–2.0 | 0.087 (20) | +2.19 / +0.14 | +0.19 / +0.01 | −1.99 (0.09) / −0.13 | 0.83 |
| 80 | 0.40–0.47 | 1.5–2.0 | 0.075 (30) | +2.30 / +0.14 | −0.15 / −0.01 | −2.45 (0.08) / −0.15 | 0.95 |
| 96 | 0.47–0.55 | 1.5–2.0 | 0.071 (32) | +2.75 / +0.15 | −0.06 / −0.00 | −2.80 (0.12) / −0.15 | 1.01 |
| 112 | 0.55–0.70 | 1.5–2.0 | 0.106 (16) | +3.24 / +0.34 | +0.22 / +0.02 | −3.02 (0.15) / −0.32 | 1.22 |
| 128 | 0.70–0.85 | 1.5–2.0 | 0.289 (4) | +5.89 / +1.22 | +0.44 / +0.09 | −5.45 (0.46) / −1.13 | 2.38 |
| 129 | 0.70–0.85 | 2.0–2.5 | 0.075 (29) | +4.11 / +0.47 | +0.32 / +0.04 | −3.79 (0.27) / −0.44 | 1.86 |
| 145 | 0.85–1.00 | 2.0–2.5 | 0.217 (5) | +1.89 / +0.29 | −0.06 / −0.01 | −1.95 (0.36) / −0.30 | 1.86 |
| 146 | 0.85–1.00 | 2.5–3.0 | 0.054 (51) | +0.78 / +0.09 | −0.23 / −0.03 | −1.01 (0.17) / −0.12 | 0.82 |
| 162 | 1.00–1.25 | 2.5–3.0 | 0.141 (9) | +1.35 / +0.17 | −0.05 / −0.01 | −1.40 (0.26) / −0.18 | 1.37 |
| 163 | 1.00–1.25 | 3.0–3.5 | 0.052 (55) | +1.18 / +0.14 | −0.03 / −0.00 | −1.21 (0.17) / −0.14 | 0.87 |

**Where the flagged cells sit, and the background fraction (descriptive, from the existing inputs; no new compute).**
- **Location.** The flagged cells are:
  - the whole lowest-p∥ row, 1.5–2.0 GeV/c (gid 0–128);
  - five cells along the high-pT, low-p∥ boundary (129, 145, 146, 162, 163).
- **Coincidence with high B/D: partial.**
  - Every flagged cell has B/D above 0.05. The median is 0.110 for flagged cells and 0.024 for the others.
  - 7 of the 14 flagged cells are among the 14 cells with the largest B/D.
  - Seven high-B/D cells are not flagged: gid 216 (0.295), 179, 1, 15, 217, 222 and 221.
- **Rank correlation.** Spearman's ρ between B/D and |mean residual| in σ_stat is 0.43 for the purity arm and 0.04
  for the refined arm.
- **Caveat.** B/D is a reco-level property of the cell's reco bin. Truth and reco share the (pT, p∥) binning.
- **The known purity-bias record does not match this population.** `KNOWN_ISSUES.md` 75 and
  [`OUTCOME-20260925-s5c-purity-background-bias-at-high-W`](../../../../../OUTCOME-20260925-s5c-purity-background-bias-at-high-W.md)
  measure a nominal-truth bias of the purity method in the **5D** result, in (E_avail, W) projection cells. They also
  show that removing the background removes it. That is the same class of test (nominal-truth, background-inclusive
  closure of the purity treatment), but its population is 5D (E_avail, W) functionals, not the 2D (pT, p∥) cells. No
  record measures the 2D cells.

**Read alone, each line above is descriptive.** In the 14 flagged cells:
- the purity arm's mean residual against truth is +0.78 to +5.89 σ_stat;
- the refined arm's is within ±0.44 σ_stat.

No judgement on the adopted 2D result is made here.

## 3. The movement table (descriptive, for the background-treatment revisit)

Definitions:
- (e) is configuration (e), refined at 400/31.
- (c) is the same deterministic estimator with purity weights on the same npz, so (e) − (c) is the background
  treatment alone.
- (a) is the deliverables' current central value.

The cells are those where all three central values are positive. Percentages are relative per cell; the integral is
over bin volumes.

| dim (cells) | difference | median abs | p84 abs | p98 abs | max abs | cells > 1 % | cells > 2 % | integral |
|---|---|---|---|---|---|---|---|---|
| 3D (1,431) | (e) − (c) | 0.81 % | 2.18 % | 6.17 % | 10.8 % | 592 | 265 | −0.180 % |
| | (e) − (a) | 0.70 % | 2.34 % | 4.98 % | 9.6 % | 543 | 276 | −0.188 % |
| | (c) − (a) | 0.47 % | 1.20 % | 4.75 % | 8.8 % | 308 | 103 | −0.008 % |
| 4D (4,830) | (e) − (c) | 0.72 % | 2.20 % | 6.86 % | 16.5 % | 1,880 | 886 | −0.169 % |
| | (e) − (a) | 0.85 % | 2.27 % | 5.57 % | 11.8 % | 2,082 | 950 | −0.164 % |
| | (c) − (a) | 0.66 % | 1.81 % | 4.56 % | 9.7 % | 1,717 | 659 | +0.005 % |
| 5D (10,694) | (e) − (c) | 0.77 % | 2.32 % | 5.55 % | 16.5 % | 4,354 | 2,069 | −0.172 % |
| | (e) − (a) | 0.77 % | 2.41 % | 5.48 % | 13.0 % | 4,400 | 2,171 | −0.162 % |
| | (c) − (a) | 0.57 % | 1.43 % | 3.64 % | 11.0 % | 3,011 | 872 | +0.010 % |

**5D in the adopted trunk's total σ.**
- The trunk is `3d7465f6…`, `hCov_combined5d_total_uthrow`, on its 10,694-cell support.
- Its central value equals the current 5D product (checked by the readout).
- The four measurements of DECISION-20260920 §4 travel with these numbers (listed below the table).

| difference | median abs | p84 abs | p98 abs | max abs | cells > 1 σ | cells > 2 σ |
|---|---|---|---|---|---|---|
| (e) − (c) | 0.052 | 0.150 | 0.359 | 0.857 | 0 | 0 |
| (e) − (a) | 0.053 | 0.154 | 0.372 | 0.786 | 0 | 0 |
| (c) − (a) † | 0.038 | 0.101 | 0.199 | 0.414 | 0 | 0 |

† The declared readout `re1_nd_movement.py` gives (e) − (c) and (e) − (a) in trunk σ only. The (c) − (a) row is from
`re1_report2_extras.py` ([`report2_extras.json`](run2/readouts/report2_extras.json)), which uses the readout's own
`pair` (Deviation 8).

**The four measurements** of
[`DECISION-20260920` §4](../../../../../DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md) travel with
these rows:
- M1: `s_proj` = 6.145 % against a 5 % bound;
- M2: that value is a reproducible property of the estimator;
- M3: five bands lie outside what the seed variation probes;
- M4: the estimator seed alone moves the central values. On the projections it moves them by at most 6.0 % of their
  uncertainty. **Per single 5D bin it moves them by a median of 3.77 % of σ, p90 13.6 %, max 49.8 %.**

The per-cell maxima above, 0.857 and 0.786 σ, are single-bin statements and carry M4's per-bin figures.

**2D: D2 − K1-2D, on data** (refined − purity with the adopted estimator; K1 passed, so K1-2D is `E_U`):

| unit | median abs | p84 abs | max abs (gid) | cells > 1 | cells > 0.5 |
|---|---|---|---|---|---|
| σ_total (Q) | 0.060 | 0.139 | 0.497 (0) | 0 | 0 |
| σ_stat | 0.51 | 1.19 | 4.26 (16) | 43 | 106 |
| relative | 0.44 % | 1.13 % | 10.1 % (0) | 38 | 92 |

The integral changes by −0.139 %. The per-cell tables are:
- [`movement_{3d,4d,5d}.tsv`](run2/readouts/);
- [`c2_d2_cells.tsv`](run2/readouts/c2_d2_cells.tsv), with D2 per cell in both σ next to C2.

No 3D or 4D covariance is quotable, so those rows are relative only (decision D4).

## 4. F: figures and numbers from P3/P4

**Regenerated figures** (F2, `run2/f/new/`, PDF sha256):

| figure | producer | PDF |
|---|---|---|
| fig:eavail | `plot_eavail_spectrum.py` on P3 (the current `hXSec_eavail` has zero bin errors, as P3's does) | `d2ae66c4…` |
| fig:3dmodels | `redraw_central_only_p3.py --only generators` | `48210da2…` |
| fig:modedecomp | `redraw_central_only_p3.py --only modedecomp` | `009a26be…` |
| fig:mec | `redraw_central_only_p3.py --only mec` | `09e2b824…` |
| fig:ascencio | `redraw_central_only_p4.py --only ascencio` | `9bd4316e…` |

**Not regenerated:**

| figure | why | missing input |
|---|---|---|
| fig:eavail-marg | K3 failed: the producer no longer reproduces the committed PDF bitwise; text and values are identical, the geometry is not. The P3 output (`49a475b6…`) exists only for its χ² (below); it is not a regeneration. | — |
| fig:q3excess | `q3_excess_projection.py:66` reads `hUnfoldND_flat`. The (e) product carries only `xsec_flat`. | `hUnfoldND_flat` |
| PET vs GBDT | `pet/pet_vs_gbdt.py:88` reads `hCompletenessND_flat` | `hCompletenessND_flat` |

**Printed numbers.** "K3" means the stated source reproduces the printed value on the current product at its printed
precision. Numbers marked † are labelled: they come from no producer in the declared list (computed by RE-1, as
stated).

| printed (where) | source | current | K3 | from P3/P4 | changes at printed precision |
|---|---|---|---|---|---|
| 2.19e-38, first E_avail bin (`sec_3d.tex:116`) | `hXSec_eavail`, `re1_f_numbers.py` | 2.1852e-38 | yes | 2.1810e-38 | **2.18e-38** |
| 6.8e-41, catch bin (`:117`) | same | 6.809e-41 | yes | 6.742e-41 | **6.7e-41** |
| +0.95 % total σ, marginal vs 2D (`:134`) | `compare_to_paper_fullcov.py`'s printout: [ours] content sum over all 224 bins / [paper] content sum over its reported bins (3.7243e-37 / 3.6892e-37). `re1_f_numbers.py`'s three area-weighted definitions do not reproduce it (vs paper −0.70 %, `E_U` +0.19 %, `E_C` +0.18 %) | +0.951 % | yes | 3.7182e-37 / 3.6892e-37 = +0.786 % | **+0.79 %** |
| 1.0016, median marginal/2D (`:134`) | vs `E_U` on its 205 cells | 1.00162 | yes | 0.99998 | **1.0000** |
| ~4.4 % per-bin scatter of the marginal (`:138`; also `:156`, `:166`) | † SD of `hXSec2D` / `E_U` on `E_U`'s 205 cells (`re1_report2_extras.py`; the same definition gives the status record's median 1.0016 and mean 1.008) | 4.42 % | yes | 3.52 % | **3.5 %** |
| marginal scatter "~70× tighter" (`:165`) | † 4.4 % / 0.06 % (the closure's 0.06 % is not an RE-1 product and is unchanged) | 74 | yes | 3.52 / 0.06 = 59 | **~60×** |
| χ²/ndf 4.98 (`:136`) | `compare_to_paper_fullcov.py`; figure not regenerated (BINDING-F ruling 3) | 4.981 | yes | 4.520 | **4.52** |
| 7.2 / 9.5 / 12.8 / 22.2 % below data (`:300-301`) | `redraw_central_only --only generators` | 7.2 / 9.5 / 12.8 / 22.2 | yes | 7.2 / 9.5 / 12.8 / 22.3 | **GiBUU 22.3** |
| 70 % of the deficit at E_avail ≤ 0.4 (`:358`) | `--only modedecomp` | 70 | yes | 69 | **69** |
| ≈ 45 % of QE; 68–71 % in the dip bins (`:360-361`) | `--only modedecomp` | 45; 0.71, 0.68 | yes | 45; 0.71, 0.68 | no |
| 8–36 % excess over GENIE CV below 0.4 GeV (`:336`) | † (data − CV)/CV in the three bins below 0.4 GeV of the modedecomp printout | 8.2–35.5 % | yes | 8.0–35.5 % | no |
| 52 % and 63 % (`:374`) | `--only mec` | 52, 63 | yes | 52, 63 | no |
| CV −7.2 % → −2.6 % (`:375`; the −2.6 also at `:379`) | `--only mec` | −7.2 → −2.6 | yes | −7.2 → −2.7 | **−2.7** |
| data/CV 1.09, "about 9 %" in [1.50, 3.00) (`:386`) | † ratio of the modedecomp printout's data and CV in that bin | 4.163/3.807 = 1.094 | yes | 4.173/3.807 = 1.096 | **1.10, "about 10 %"** |
| 9.2 % and 6.3 % above Ascencio (`:493`) | `--only ascencio` | 9.2, 6.3 | yes | 9.2, 6.0 | **6.0** |
| data total 3.08e-38 (`:274`) | † `hXSec3D.Integral("width")` (`re1_report2_extras.py`) | 3.0789e-38 | yes | 3.0731e-38 | **3.07e-38** |
| q3-marginal data/Tune v1 1.21, 1.01, 1.16–1.23, 1.13 (`:453-455`); 1.03–1.19 and 0.66 (`:463`, `:466`) | `q3_excess_projection.py` (fig:q3excess), which needs `hUnfoldND_flat` | — | — | — | not regenerated |

The 10–28 % range at `:275` is a ratio of rounded generator totals to the data total. With 3.07e-38 it stays 10–28 %
(†, arithmetic only). `paper_body.tex:480-484` says that the marginal normalizations "agree at the approximately
1–2 % level". No producer in the list computes that statement. For reference, the 3D marginal's area-weighted total
against `E_U` is +0.19 % on the current product and +0.001 % on P3 (`numbers.json`). It is not re-evaluated further.

**Side finding for the director.** The note's sentence at `sec_3d.tex:130-134` names "the 2D result of §results".
The printed +0.95 % reproduces only as a plain sum of bin contents: our 224 bins against the *published* 2D result's
reported bins. It does not reproduce against `E_U`, the adopted 2D result. The producers' full printouts, current and P3/P4, are in
[`run2/f/k3/`](run2/f/k3/) and [`run2/f/new/`](run2/f/new/).

## Ledger

[`run2/ledger.tsv`](run2/ledger.tsv) is from `sacct -X` via `re1_ledger.sh`. Charge = ElapsedRaw/3600 × billing/256.

| JobID | name | QOS | state | elapsed | projected / limit | charge (node-h) |
|---|---|---|---|---|---|---|
| 60129317 | re1-inputs | regular | COMPLETED | 428 s | 1.5 h / 1:52 | 0.1189 |
| 60129318 | re1-nd | regular | COMPLETED | 913 s | 0.75 h / 0:56 | 0.2536 |
| 60129319 | re1-2d | regular | COMPLETED | 3,264 s | 1.75 h / 2:11 | 0.9067 |
| 60143725 | re1-f1 | debug | **TIMEOUT** | 672 s | F: 0.3 h / 0:22 (set to 0:11) | 0.1867 |
| 60144049 | re1-f1b | debug | COMPLETED | 205 s | — / 0:10 (BINDING-F) | 0.0569 |
| 60144186 | re1-f2 | debug | COMPLETED | 375 s | — / 0:22 (BINDING-F) | 0.1042 |
| | | | | | **total** | **1.627** of 6.0 |

- F as a whole took 1,252 s and 0.348 node-h. That is inside the 0:22 and 0.367 node-h declared for F; the approved
  worst case was 0.72.
- No other job was resubmitted.
- The submissions are in [`run2/receipts/submissions.log`](run2/receipts/submissions.log).
- Nothing was written to CFS. The covariances were read from CFS, read-only.
- The measurement session's and the validation lane's jobs were not touched.

## Receipts (pscratch `/pscratch/sd/j/josephrb/methods-paper/re1-20261022/out/`, 4.4 GB)

| product | sha256 |
|---|---|
| `5d/k1_p5_rerun.npz` (P5 rerun, = P5 bitwise in `xsec_flat`) | `e36f3b25459e068cec9dba941f7b3aea8f48c6e22c931fde7c9d315e7b1e8de2` |
| `5d/p5c.npz` | `1fa60dfcb929fc4fe9b88cc64aa9c87f1ee971af751bde08ec69a7d6837462c7` |
| `3d/p3.npz` (P3) | `8bc7e2d3bae0f14b2f4d87f326e262993d8c14281d37f88c391306fda3d268cb` |
| `3d/p3c.npz` | `c3a55a278d6febbad9bad2c3febeb35f06c919582f98b24fa03d9982c12549c3` |
| `4d/p4.npz` (P4) | `2a18599f952eb497acddaad596668a04b32b1bf7f6ac3842a4475e8dbdfb2bdf` |
| `4d/p4c.npz` | `7cf0b3aedfc9369dcc660943eec03ddd547702213d9cdfd573f6dfb8cf19da9a` |
| `2d/k1_data_purity.npz` (K1-2D) | `b80a24b049a7ca966e82e35b0ca017638481a0f99bc5b5edc56d40b5abb44cf1` |
| `2d/d2_data_refined.npz` (D2) | `71ca3e5fc97cfc0625d84484d9c1f4a59476feacfd3813cdc98d89782329488a` |
| `2d/c2/nominal_s{1..20}.npz` | [`run2/receipts/SHA256SUMS.2d`](run2/receipts/SHA256SUMS.2d) (22 lines) |
| `f/new/xsec_3d_p3.root`, `f/new/xsec_4d_p4.root` | `c16b622b…`, `ece4055e…`; with every K3 and F figure in [`run2/f/SHA256SUMS.f1`](run2/f/SHA256SUMS.f1), [`SHA256SUMS.f2`](run2/f/SHA256SUMS.f2) |
| readouts (also committed here) | [`run2/readouts/SHA256SUMS.movement`](run2/readouts/SHA256SUMS.movement); `readout_2d_full.json` `ac759b03…`; `c2_supplement.json` `445b630c…`; `c2_d2_cells.tsv` `70ee3649…` (regenerated byte for byte by `re1_c2_cells.py`); `c2_cells.json` `ba9cf8c1…`; `report2_extras.json` `1cfeee2b…` |
| the 20 C2 products, committed | `run2/readouts/nominal_s{1..20}.npz`, equal to `SHA256SUMS.2d` |

The intermediates (the 2D cache and the 3D/4D npz and background dumps, most of the 4.4 GB) stay on pscratch until this
report merges. Deleting or keeping them is then raised with the director (declaration §6).

## Deviations

1. **F1's limit was 0:11, not the declared 0:22.**
   - The lane split F into two jobs and gave each half of F's declared limit. The declaration's 0:22 was for F as a
     whole. The split was not put to the director.
   - F1 ran its four K3 producer runs one after another (2.0–2.6 min each) and was stopped by Slurm at 0:11, before
     its conversion steps.
   - The director bound F1b and a serial F2 (BINDING-F). Both completed.
2. **F's worst-case charge rose to 0.72 node-h**, against the 0.367 declared (BINDING-F ruling 4). It actually
   charged 0.348 node-h in 1,252 s, inside the declared F figures.
3. **F1 was submitted before the 2D readouts** (the declaration's table says F comes after the readouts). By then the
   ND readouts and K1-ND, the controls for P3/P4, were complete. F's inputs do not depend on any 2D product.
4. **The F-R1 redraw copies.** §5.3 says F uses "the existing producers, with only the input product changed".
   `redraw_central_only.py` pins its input digests, so it refuses P3/P4 unchanged. The two copies change that one
   data pin each and nothing else (diffs above).
   - The director approved them as F-R1, by message, before F.
   - BINDING-F ruling 2 records them as bound ("The F-R1 redraw copies are committed with their diffs before F2,
     as bound").
   - F-R1's conditions, as the lane received them:
     - the `git diff --no-index` is committed and quoted;
     - each copy's sha256 is recorded;
     - K3 runs first, bitwise against the current figure;
     - nothing is written under a checkout;
     - the originals are untouched;
     - each copy still refuses other bytes.
   All six are met (§Code; [`run2/f-r1/refusal.txt`](run2/f-r1/refusal.txt)).
5. **J2 products do not record their affinity themselves.** The s5 path records LightGBM `num_threads` 32, fixed in
   its estimator parameters. Each J2 step's 42-CPU allocation is in `sacct`, and `--cpu-bind=cores` is in the
   sbatch.
6. **Additions after the results, not in the declaration.** The binding says that "no change may follow a result".
   These additions are descriptive and change no declared code path, readout, rule or verdict:
   - the C2 supplement (`re1_c2_supplement.py`, committed 22:13 PDT, after J3 and the declared readout);
   - the per-cell C2/D2 table (`re1_c2_cells.py`; the table was first written inline and is now regenerated byte for
     byte by committed code);
   - the review-round extras (`re1_report2_extras.py`).
   The director requested the supplement by message (quoted in the appendix). The extras answer this report's
   independent review. They are recorded so the director can rule on them in the PR.
7. **Conversion readback.** §5.3 asks for the readback "through each producer's own loader". `re1_to_root.py` reads
   back with its own reader, and in 3D it checks only `hXSec3D`. The producers then read the files in F2.
8. **The 5D (c) − (a) row in trunk σ** is not computed by the declared readout. It comes from
   `re1_report2_extras.py`, with the readout's own `pair`.
9. **Labelled numbers (†)** come from no declared producer: the 3D total, the marginal scatter and its ratio to the
   closure, the 8–36 % range, the data/CV ratio and the 10–28 % range. The χ² of fig:eavail-marg is reported from P3
   while its figure is not regenerated (BINDING-F ruling 3).
10. **The 2D readout ran twice.** The first run was K1 only, as soon as the K1 product existed
    (`readout_2d_k1only.json`). The second was the declared full readout. Both runs give the same K1 numbers.
11. **A stale development checkout** is at `/pscratch/sd/j/josephrb/methods-paper/re1-20261022/dev/` (at
    `7f509004`, with local edits). No job used it. It is the lane's own scratch, and it is listed for deletion with
    the intermediates.

These results are not a live record until this report and `run2/` are committed and merged.

## Review record

**Reviewer.** A fresh Claude agent, given the code and the evidence but not the author's conclusions. It read-only
reviewed the branch at `2af68acc`, in two directions:
- report → evidence: every claim checked against its artifact;
- declaration/evidence → report: what is required, omitted or worded beyond a rule.

It found no blocker, five major findings and twelve minor or nit findings. It independently re-derived, among other
things:
- the C2 verdict from the 20 committed products and the CFS covariances;
- all six summary rows and all 14 flagged-cell rows;
- K1-2D, K1-ND, D2, the movement table and the 5D trunk-σ rows;
- the F-R1 diffs, the K3 results, the F2 shas and the ledger.

| finding (severity) | disposition |
|---|---|
| +0.95 % is reproduced by the producer's printout, and is +0.79 % on P3 (MAJOR) | fixed: §4 row and side finding |
| printed `sec_3d.tex` numbers missing: ~4.4 %, 8–36 %, the q3-marginal ratios (MAJOR) | fixed: rows added; the q3 ratios are not regenerated (fig:q3excess) |
| `c2_d2_cells.tsv` had no committed producer (MAJOR) | fixed: `re1_c2_cells.py` regenerates it byte for byte |
| the outcome's "does not close / does" went beyond the rule (MAJOR) | fixed: numbers only |
| authority for the supplement and the F-R1 copies not on record; F-R1 not in Deviations (MAJOR) | fixed: Deviations 4 and 6; the director's message is quoted below; the director rules in the PR |
| the test file was declared, then modified (MINOR) | fixed: §Code |
| no 5D (c) − (a) row in trunk σ (MINOR) | fixed: row added, Deviation 8 |
| DECISION-20260920 §4 named but not stated (MINOR) | fixed: M1–M4 stated and linked in §3 |
| conversion readback not through each producer's loader (MINOR) | fixed: Deviation 7 |
| readout wrappers not committed (MINOR) | fixed: `run2/launch/readouts/` |
| purity-arm significance given only for flagged cells (MINOR) | fixed: SE counts in §2 |
| "five of seven" figures (MINOR) | fixed: five of eight |
| the 0.72 node-h worst case not under Deviations (MINOR) | fixed: Deviation 2 |
| the factor ~2 between the seed spread and σ_stat unexplained (NIT) | fixed: caveat in §2 |
| nits: number count, "about 10 %", D2's refined/signed, P5's extra recorded modules, "six producers", comparator for 0.86, `paper_body` 1–2 % | fixed |
| the † totals and the F-R1 refusal had no artifact (NIT) | fixed: `report2_extras.json`, `run2/f-r1/refusal.txt` |
| BINDING-F link resolves only after a rebase onto main (NIT) | the branch is rebased before the PR |
| stale `dev/` checkout on pscratch (NIT) | Deviation 11 |

Two of the reviewer's values were corrected on re-derivation: the refined arm's 2.4 SE at gid 48 is 2.35, and its
largest t is 3.09 at gid 49, an unflagged cell. The reviewer could not check:
- whether each clone was clean before and during its job (only after);
- `--cpu-bind=cores` beyond the sbatch;
- the F-R1 refusal itself (re-running it would write on the cluster);
- the director's requests made outside the repository.

A second read-only pass by the same reviewer checked the fixes (below).

## Appendix: the director's C2-supplement request (cross-session message, 2026-10-22, verbatim)

> Director: C2 FLAG received; I'll take it to Joseph from the reviewed REPORT-2, not from this message. For REPORT-2,
> please add (descriptive, no judgement): (1) each arm's mean residual against truth in σ_total (Q) units as well as
> σ_stat, per flagged cell and summarized over 205; (2) the pseudo-experiment spread: per-cell SD of each arm across
> the 20 seeds against σ_stat, so a reader can see whether σ_stat is the right yardstick for a 20-seed mean; (3)
> whether the flagged region (lowest-p∥ row, high-pT boundary) coincides with the cells where the purity background
> fraction is largest — read it from the existing inputs, no new compute; cite the record of the known purity
> background bias if one applies (e.g. KNOWN_ISSUES 75 / OUTCOME-20260925-s5c-purity-background-bias-at-high-W) only
> where its population matches 2D; (4) state plainly that C2 is a nominal-truth closure with 20 seeds, not a coverage
> test. Keep the outcome wording to the declared rule ("flags it for Joseph's decision on the adopted 2D result").
> Then the independent two-direction review, then the PR to me.
