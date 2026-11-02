# REPORT 1B staged method coverage, stage 1: STOP at the receipt, N1's composite above 10 on the declared draws (2026-11-02)

**By** the measurement session `coverage-5b`, for `coverage-5b-audit` and the director, and through the director for
Joseph.

**Under:**
- [`FD-1B-STAGED-DECLARATION.md`](FD-1B-STAGED-DECLARATION.md) (revision 2) §4 and §8–§12, with its code in
  [`FD-1B-STAGED-AMENDMENT-1.md`](FD-1B-STAGED-AMENDMENT-1.md) (revision 3), bound by
  [`FD-1B-STAGED-BINDING-2.md`](FD-1B-STAGED-BINDING-2.md) at M2 = `24c83ab8`;
- `DECISION-20261101-joseph-1b-staged-method-coverage.md` (#663);
- the director's acceptance of the STOP and its rulings on connects 33 and 34 (2026-11-02, by message; to be
  recorded in the director's review).

**The reading: STOP, under binding 2's ruling 3.** The receipt's exact pass over the 900 declared draws finds rows
whose composite |a_D| / max_j |a_uj| exceeds N1's bound of 10, in three of the four arrays:

| array | rows above over all draws | all-draws max | declared draws: rows evaluated | declared max | **declared rows above 10** |
|---|---:|---:|---:|---:|---:|
| `wt` (truth weight) | 2,477 | 269.52 | 2,477 | 255.02 | **161** |
| `wr` (reco weight) | 17,835 | 276.91 | 17,835 | 251.75 | **799** |
| `bkgw` (background weight) | 465 | 26.46 | 465 | 23.64 | **24** |
| `denom` (per cell) | 0 | 7.158 | 0 | – | 0 |

- **Every row was evaluated.** The cap of 250,000 rows per array did not fire, so this is the composite and not the
  cap.
- **Stage 1 stops at 0 node-h.** S1-0 was not submitted. No job ran and no product exists (§1).
- **The bound was fixed before the read** (binding 2, rulings 3 and 4). Nothing here proposes a new bound or a
  repair. The redesign Joseph approved comes separately, on grounds stated independently of these values, with
  the bound kept at 10.
- **What fired** (§3, descriptive): the rows above are of two kinds.
  - **Most are rows with an ordinary CV weight.** In `wr`, 702 of 799 rows (88 %) have |a_CV| ≥ 0.01, against an
    all-row median of 0.18. They carry no large single ratio (largest r median 2.13), and they sit just above 10
    (median 10.93). They are there because about 34 universes with r > 1 multiply across the 38 bands.
  - **The rest are N1's premise:** |a_CV| < 0.01 with one large ratio, mostly LowQ2 or HighQ2. That is 95 of 161 rows
    in `wt`, 97 in `wr` and 3 in `bkgw`, and they give the maxima of about 255.
- **The paper is unchanged** (declaration §12: "Stage 0 FAIL, PARTIAL without Joseph's go-ahead, INVALID, or no
  result: the paper is unchanged, and the stopped-attempt disclosure stays"). The director has told Joseph of the
  STOP under ruling 9.
- **Access times:** none moved. The receipt's own record shows 706 files opened through `O_NOATIME`, none moved.
  The 1,513-path stat list is unchanged after the receipt (connect 33) and after the attribution (connect 34).
- **A defect in binding 2's bound code, masked by the STOP (D2, §5; found by `coverage-5b-audit`).** A toy draws its
  pseudo-data with `rng.poisson`, which refuses a negative mean. Two universes, LowQ2_1 and HighQ2_1, carry negative
  weights, and the product rule keeps the sign. So 684 of the 900 declared toys would have refused. Had N1 passed,
  the bulk would have failed on most of its toys.
- **Deviations and errata:** §5.
  - My amendment under-stated the receipt's read volume (erratum E1). The receipt read 68.4 GB of universe files, not
    26.6 GB, five times by the code, with about 208 GB measured.
  - I0's and I2's `load_s1` read the staged S1 assembly without `O_NOATIME` (erratum E2, ruling 8).
- **HPSS:** deferred until NERSC's maintenance ends on 2026-11-06 at 17:00
  (`RECORD-20261102-director-hpss-deferral.md`, #685). Nothing of stage 1 is archived yet. The pscratch originals
  stay until each copy is verified.

**MEASURES:** N1's composite on the real bank, over every possible draw and over the 900 declared draws, per array;
the single-universe ratios (descriptive); the attribution of the rows above (descriptive).

**CANNOT SUPPORT:**
- anything about coverage, at either tune or at the plug-in: no toy was drawn and no block remade;
- that S1's covariance is right or wrong. N1 concerns the toys' composite weights, which S1 never formed;
- a bound other than 10, chosen from these values;
- a redesign. That is a separate proposal, routed to the audit, then the director, then Joseph.

## 1. What ran

| connect | when (UTC) | node | what | outcome |
|---|---|---|---|---|
| 32 | 16:15:34–17:43:36 | login37 | balance, deploy at M2, stat-before, `stage-flux`, `receipt`; tables and S1-0 gated on the receipt | receipt STOP; the script stopped before the second stat, the tables and the sbatch, as written |
| 33 | 19:12:19–19:12:20 | login23 | read-only: `squeue`, `sacct`, the stat-after against stat-before, the lane's own digests, then `scp` | no fd1b job; 1,513 stats unchanged; local copies match their cluster digests |
| 34 | 19:25:38–20:29:03 | login23 | descriptive attribution (`attrib/n1_attrib.py`) at `nice 19` | rc 0; reproduces the receipt exactly (mismatches []); atime and the 1,513 stats unchanged |

**Connect 32** (`stage1/connect32-s1-0.sh`, blob `4d9464a4`, sha256 `4164eaf0…`, approved by the director at
`30ec6675`). It was placed in the new `$W1 = $W/stage1` (binding 2 ruling 7, as the director ruled on it) and run
detached on login37 under `setsid nohup`, as approved. The launcher's PID was 1451853, with init as its parent. The
log ends `end=2026-11-02T17:43:36Z`.
- **Balance:** `iris` gives m3246 charged 17,949.1 of 20,000.0, so the balance is 2,050.9 node-h. Half is 1,025.5,
  against the 73.0 cap: the gate passed.
- **Deploy:** a fresh clone at M2 `24c83ab8`, with 0 porcelain lines. Binding 2's seven blobs are equal, and
  `fd_1b_mc.py` has sha256 `1a2f825fe4a7…`. The receipt's `code_sha256` also records `fd_1b_mc.py 1a2f825fe4a7`.
- **Environment:** the jobs' own, `setup_salloc_env.sh`, Python 3.11.
- **The stat list, before the first read:** 1,513 unique paths. These are the 701 pinned weight files (pins.json's
  `files`, read through `O_NOATIME`), 7 named inputs (inputs npz, background, pins, flux constraint, flux ROOT table,
  F1's two prep ratios), the 397 files under `$V/i0/in` and the 408 under `$V/i2/unf`.
- **`stage-flux`:** rc 0, 0:09.50 wall, peak RSS 183 MB. The source sha256 is `5eecae84…`, which the audit
  identified as the committed HFLUXCV pin (`3d-unfolding/genie/gen5d_v3.py:62`). n_ref 14, n_univ 100. The staged
  table is `in/flux_universes.npz`, sha256 `cdc3da78…`.
- **`receipt`:** rc 0 and verdict STOP. Wall 1:26:25, peak RSS 11.76 GB (11,764,112 KiB), 95 % of one CPU. NERSC's
  login limits did not end it, so ruling 5's fallback job was not needed. Its output is `receipt.json`, sha256
  `c8fcd7f9…`.

**Connect 33** (`stage1/connect33-post-stop.sh`, approved by the director as read-only, with nothing written on the
cluster). `squeue` and `sacct` since 16:00 show no fd1b job. The stat-after is printed in full into the local `.out`
only, and is identical to connect 32's stat-before in atime, mtime and size for all 1,513 paths. That includes
`stage-flux`'s read of the flux ROOT table, which the receipt's own record does not cover. The lane's outputs were
digested on the cluster and copied with `scp`, and every local digest matches (`stage1/connect32/`).

**Connect 34** (`stage1/connect34-attrib.sh` sha256 `09cf5ba8…`, `attrib/n1_attrib.py` sha256 `954b44c8…`, approved
by the director at `1ef3d855`). It was placed in the new `$W1/attrib` and run detached on login23 under `setsid nohup`, from connect 32's
deploy, which was re-checked clean at M2. The launcher's PID was 474779, with init as its parent. The log ends
`end=2026-11-02T20:29:03Z`.
- **Guards:** `fd_1b_mc.py` `1a2f825f`; `n1_attrib.py` `954b44c8` against the committed digest; `receipt.json`
  `c8fcd7f9`; `flux_universes.npz` `cdc3da78`.
- **Run:** rc 0, wall 1:03:19, peak RSS 10.97 GB, 272,582,136 input blocks.
- **The repetition's check:** `mismatches: []`. Its all-draws and declared-draw numbers equal the receipt's exactly.
- **Atime:** `atime moved: []`. The 1,513 stats are unchanged before and after, and both equal connect 32's
  stat-before (`e1dbc376`).
- **Output:** `n1_attrib.json`, sha256 `c7da3aa4…`. It and the logs were copied with `scp`, and they match
  `connect34/SHA256SUMS.cluster`.
- **The script's review.** `coverage-5b-audit` found no code defect, but 8 of its 13 mutants survived on the quoted
  fields. Four tests were added, with the code unchanged:
  - `test_n1_attrib.py` (8 passed) recomputes every quoted field from `_single` on the fixture, including a strict
    subset of draws and the 900 declared labels;
  - `mutation_attrib.out` (the audit's 14 mutants) reads 14 of 14 killed.

  The audit confirmed this at `942a10ba`. The launch came before that review, on the director's go; it was read-only,
  and that is recorded.

**Cost:** 0 node-h. Everything ran on login nodes. Nothing was submitted.

## 2. The receipt

**The composite** (binding 2 ruling 3; amendment §3). Every draw holds one universe of every band.
- **Where a_CV ≠ 0,** the composite over a draw is |a_D| / max_j |a_uj| = Π_j r_j / max_j r_j, with
  r_j = |a_uj / a_CV|. Its largest value over all draws is exactly Π_b R_b / max_b R_b, where R_b is the largest r_j
  in band b.
- **Where a_CV = 0,** the composite is |Σ_j a_uj| / max_j |a_uj|. It is at most the number of bands with a non-zero
  weight on that row.
- **The exact pass.** Rows whose all-draws value exceeds 10 are evaluated over the 900 declared draws (G18's, AR23's
  and the plug-in's 300 seeds each).

The table above is the receipt's `composite` block, verbatim to the precision shown. `n_draws` is 900, `bound` 10.0
and `candidate_cap` 250,000.

**The single-universe ratios** (descriptive only, ruling 3). These are per universe, over all rows:

| array | largest single max |a_u / a_CV| | next | then | rows above 10, summed over universes |
|---|---|---|---|---:|
| `wt` | HighQ2_1 429.59 (25 rows) | LowQ2_0 158.08 (102) | LowQ2_1 156.08 (86); the largest Flux is Flux_60 at 31.35 | 2,409 |
| `wr` | HighQ2_1 429.59 (25) | LowQ2_0 158.08 (102) | LowQ2_1 156.08 (86); GEANT_Neutron_1 66.51 (85) | 2,496 |
| `bkgw` | LowQ2_0 44.77 (5) | LowQ2_1 42.77 (4) | Flux_60 31.35 (143) | 650 |

- `cv_zero_u_nonzero` and `cv_negative` are 0 in every universe and array.
- `u_negative` sums to 561 for `wt`, 561 for `wr` and 55 for `bkgw`.
- `u_nonfinite` is 36 in `wr` and 0 elsewhere. The receipt reads with `"keep"`. The jobs' loader uses `"zero"`.
- Every detector universe's `denom_nd` equals the CV's.

## 3. What fired (descriptive; connect 34)

Descriptive only. `attrib/summarize_attrib.py` produces these numbers from the committed
`connect34/n1_attrib.json` (`c7da3aa4…`), and its output is `attrib/summarize_attrib.out`. r_j = |a_uj / a_CV| is a
universe's single ratio on the row. "Worst" is the row's largest composite over the 900 declared draws, at the first
declared draw that attains it. No row above has a_CV = 0.

**By CV weight.** The split at |a_CV| = 0.01 is `coverage-5b-audit`'s, chosen after the attribution was read. It
describes the rows and decides nothing. In every array the all-row median of |a_CV| is about 0.18.

| array | rows above | kind | rows | worst: median (max) | largest r: median (max) | universes with r > 1: median (range) |
|---|---:|---|---:|---|---|---|
| `wt` | 161 | small-CV | 95 | 18.90 (255.02) | 21.39 (429.59) | 36 (6–38) |
| | | ordinary | 66 | 10.77 (24.77) | 2.46 (17.21) | 14.5 (7–38) |
| `wr` | 799 | small-CV | 97 | 18.32 (251.75) | 21.39 (429.59) | 34 (7–38) |
| | | ordinary | **702** | 10.93 (28.92) | 2.13 (27.90) | 34 (6–38) |
| `bkgw` | 24 | small-CV | 3 | 13.06 (23.64) | 42.64 (44.77) | 11 (11–36) |
| | | ordinary | 21 | 10.74 (17.31) | 2.41 (4.82) | 33 (13–37) |

**Two mechanisms.**
- **(a) N1's premise.** A small, non-zero CV weight carries a large single ratio, which then multiplies the others.
  These are the small-CV rows, and they give every array's maximum. Their largest ratios are in LowQ2 and HighQ2:
  - LowQ2's R_b is above 10 on 72 rows above in `wt` and 73 in `wr`;
  - HighQ2's is above 10 on 25 in each;
  - these are the bands whose single maxima are 158.08 and 429.59 (§2).
- **(b) Compounding.** Rows with an ordinary CV weight and no large ratio carry many modest ratios above 1, which
  multiply across 38 bands to just above 10. These are most of the count: 702 of 799 rows in `wr`, 66 of 161 in
  `wt` and 21 of 24 in `bkgw`. The amendment had expected this of the all-draws bound ("1.1³⁹ ≈ 41", §3). On the
  declared draws it is what fills `wr`.

**Which bands.** The band of the largest r_j in the worst draw, then of the second, over the rows above:

| array | largest-r band (rows) | second-r band (rows) | top pairs (of N distinct) |
|---|---|---|---|
| `wt` | LowQ2 81, 2p2h 19, MaRES 15, HighQ2 15, MFP_pi 10 | 2p2h 42, HighQ2 39, LowQ2 31, FrCEx_pi 16 | top 10 of 23: LowQ2+2p2h 42, LowQ2+HighQ2 39, 2p2h+LowQ2 16, HighQ2+LowQ2 15 |
| `wr` | GEANT_Neutron 129, MFP_pi 113, FrAbs_pi 95, MaRES 88, LowQ2 83, 2p2h 80, FrCEx_pi 74 | FrAbs_pi 152, FrCEx_N 138, GEANT_Neutron 95, FrCEx_pi 79, MFP_pi 74 | top 10 of 84: 2p2h+FrCEx_N 56, MFP_pi+FrAbs_pi 51, LowQ2+2p2h 43, LowQ2+HighQ2 40 |
| `bkgw` | GEANT_Neutron 7, FrAbs_pi 5, LowQ2 3 | FrAbs_pi 8, MFP_pi 5, HighQ2 3 | top 10 of 15: GEANT_Neutron+FrAbs_pi 4, LowQ2+HighQ2 3 |

`band_max_r_on_rows_above` is each band's R_b: its largest r over all its universes on the row, not only the worst
draw's (the audit's reading note). Only LowQ2, HighQ2 and, on one `wr` row, GEANT_Neutron (27.9) reach R_b > 10.

**By truth** (the truth whose seed gives the worst draw):
- `wt`: G18 65, plug-in 49, AR23 47;
- `wr`: 283, 276, 240;
- `bkgw`: 3, 11, 10.

The draws are the same construction at every truth, so this is the draws' spread, not a truth effect.

**What this does not say:**
- that either mechanism is a defect in the bank: S1's own single-universe arrays hold these ratios (§2), and k = 1
  is S1's universe;
- anything about coverage;
- a bound or a remedy.

## 4. Price: the receipt's read volume (erratum E1)

| | my amendment | measured or counted (connect 32) |
|---|---|---|
| the bank the receipt reads | "the 26.6 GB bank" (§5.3) | **68.4 GB** of universe files alone: 700 pinned files (66.24 GB bank, 2.13 GB detector dump). With the 2.16 GB bank CV and the 1.55 GB inputs, 72.1 GB (sizes from the stat list) |
| passes over it | "one or two" (§5.3); "about four" (§4) | **five** by the code: one in the singles (`universe_weights`), and two in each composite pass, because `_weights` hashes each universe's four files and then loads them |
| bytes read (`/usr/bin/time` "File system inputs" × 512 B) | 27–106 GB | **208.1 GB** (406,519,308 blocks), about 3.0 volumes of the 68.4 GB of universe files. Connect 34, four passes by the code: 139.6 GB (272,582,136 blocks), about 2.0 volumes |
| wall | not estimated | 1:26:25 |
| peak RSS | not estimated | 11.76 GB |

- **Two errors, both mine.**
  - The 26.6 GB is stage 0's interaction subset (268 files, connect 25). Stage 1 reads every pinned universe:
    all 175 universes S1 unfolded: 100 Flux, 67 interaction and 8 detector.
  - The pass count left out the pin hashing (§5.3) or under-counted it (§4).
  - The audit's "about 8 times the 26.6 GB bank" used my 26.6. The audit records that error as its own as well.
- **The unit.** "File system inputs" is `getrusage`'s `ru_inblock`, which Linux counts in 512-byte blocks. On
  Lustre it may count differently, so the 208 GB is an estimate of the bytes read (the audit's caution), not a
  measurement of them.
- **Measured against counted.** Five passes would nominally read about 342 GB, and the measurement is 208 GB. A read
  served from the page cache is not counted in `ru_inblock`, which is consistent with the difference. That is an
  inference; I did not measure the page cache.
- **Its effect.** The stop costs 0 node-h either way, so it changes no gate. A redesign that keeps a receipt should
  be priced from the measured wall and volume, not from my estimate.

## 5. Deviations and errata

1. **(E1) The read volume** (§4): my amendment gave the wrong bank size (26.6 GB against 68.4 GB) and too few
   passes (one or two against five). About 208 GB was measured. This is the audit's item 3.
2. **(E2) I0's and I2's `load_s1`** (binding 2, ruling 8). The bound I2 code (`fd_1b_inv.py:310`, `:652`) calls
   `fd_1b_score.load_s1`, which reads `$V/i0/in/s1/s1_assembly.npz` with a plain sha256 and a plain `np.load`. It
   also passes the staged `flux_constraint.txt` to `fs.derivation_blocks`, which reads it through `flux_weights`.
   - The I2 report's atime records (its 204 sidecars and the 272-path stat list) cover neither file. Its statement
     that no file moved is true of the set it tracked, not of these two.
   - Their numbers are digest-checked and unaffected.
   - Stage 1's own code reads both through `via_noatime` (amendment §2 (vi)). Stage 0's instance is stage 0's
     deviation 5.
3. **Connect 32 stopped before its second stat,** because the receipt gate comes first in the script. Connect 33
   took the stat-after instead, read-only and unchanged.
4. **Connect 32's poll changed login node.** Connect 33 answered from login23, where connect 32 had run on login37.
   pscratch is shared, so the stat reads the same inodes. The detached processes ran wholly on the node that started
   them.
5. **(D2) A defect in binding 2's bound code, masked by the STOP** (`coverage-5b-audit`'s review of #696 and #697,
   issuecomment-6588835818; verified here).
   - **The path.** Every toy draws pseudo-data with `rng.poisson` (`fd_1b_toys.build_full`, `fd_1b_toys.py:284–287`
     at M2, through `fd_1b_mc.toy_experiment`). numpy raises `ValueError` on a negative mean.
   - **The weights.** In the receipt (§2), only LowQ2_1 and HighQ2_1 carry negative weights: 462 and 99 rows in `wt`
     and `wr`, 50 and 5 in `bkgw`. Declaration §4.2 keeps negative weights, and the product rule carries their sign
     into the composite.
   - **The toys.** By the audit's recount with `draw_for_seed`, 684 of the 900 declared draws hold LowQ2_1 or
     HighQ2_1. That is consistent with each pair band at either endpoint with probability ½. Each such toy would
     have refused (rc 4).
   - **Why nothing caught it.**
     - The central, seed, block and stat roles draw at the mean (`_MeanRNG`) or use the real data. So do S1's own
       universe unfolds, which is why S1 ran with these weights.
     - S1-0's pilot holds one toy (G18 3,620,000). The plug-in pilot has no AR23 toy. The S1-0 readout would have
       shown it only if that seed drew either universe.
     - No test sends a negative composite through `toy_experiment`.
   - **Its standing.** A defect, reported unrepaired. It does not change the STOP, which comes first. Any redesign must
     state what a toy does with a negative expected count. That is a method choice for the director and Joseph (the
     redesign proposal, #697). The audit had acknowledged #673 without it, and says so.

## 6. For the audit and the director

- **The audit's five items:**
  - 1, the stat-after: §1, connect 33;
  - 2, the attribution: §3;
  - 3, the price: §4;
  - 4, the errata and Joseph: §5 and the reading;
  - 5, the bound: the reading's third point and CANNOT SUPPORT.
- **Receipts:** `fd/receipts-1b/staged/stage1/`:
  - connect 32's script, launcher and copied outputs (`connect32/`);
  - connect 33's script and `.out`;
  - connect 34's script, launcher, `attrib/` (the script, its tests, the mutation receipt and `summarize_attrib.py`
    with its `.out`) and copied outputs (`connect34/`).
- **Next:** the stage-1 redesign Joseph approved. It is a separate proposal, with N1's bound at 10 and a price, and
  goes to the audit, then the director, then Joseph before binding.
