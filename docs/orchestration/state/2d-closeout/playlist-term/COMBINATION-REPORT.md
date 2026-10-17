# S5 production total + playlist-consistency block: report (Stage F F9)

**Owner:** the paper-tighten lane, as director. Run on 2026-10-17 under the frozen
[`COMBINATION.md`](COMBINATION.md) (PR #148, merge `ecf971f1`).

**CITABLE FOR:** the sizes of S5, C_PL and S5 + C_PL on the 205 cells, the integral and the 30 projections; the
effect of adding C_PL; and the DESIGN §4 χ² rows against S5 and S5 + C_PL.
**NOT CITABLE FOR:** an adoption, a coverage statement, a claim or a publication change. S5 + C_PL is a **candidate**
for Joseph's decision (checklist J2). The production REPORT and its F4 verification are still pending, and
`driver_p1.py` has not reached main (F6).

## 1. Run and review

| field | value |
|---|---|
| Script | [`scripts/combine_s5.py`](scripts/combine_s5.py) `0c6ac3a0…`, deployed byte-identical. Run with `python3 -I` in root_6_28 on `login04`; rc 0; 0 node-h |
| Inputs | S5 `production_cov.npz` `6689d2fc…` (`s5_rollup.py` `6c437004`, S5 PASS); `playlist_term.npz` `c1723cb5…`; the period-unfold pins of `playlist_term.py` |
| Outputs | [`outputs/combination/combination.json`](outputs/combination/combination.json) `050e2560…`; [`outputs/combination/run.log.txt`](outputs/combination/run.log.txt) `75b7ed1b…`. `s5_plus_playlist.npz` `8ccb4d72…` is gitignored; it is in `/global/cfs/cdirs/m3246/josephrb/2d-closeout-playlist-combination-20261017/` with `SHA256SUMS` (`sha256sum -c` OK), and in `/pscratch/sd/j/josephrb/tmp-playlist-combination-20261017/out/` |
| Pre-run review | fresh read-only verifier: APPROVE WITH CHANGES (1 MATERIAL, 5 MINOR), all applied before the freeze |
| Recompute | **REPRODUCED.** A fresh verifier wrote its own code and did not open the script. It reused only the earlier verifier's ROOT reader. Every group agrees: budget and effect to ≤ 2.2e-16; the 32 χ² values to ≤ 4.0e-14; ranks equal. Its files are in [`outputs/combination/recompute/`](outputs/combination/recompute/), byte-identical to `/pscratch/sd/j/josephrb/tmp-playlist-combination-recompute-20261017/`, with `SHA256SUMS` |
| Who | the director wrote and ran it. Both verifiers are Claude Opus 5.5 on the claude-school account, the same model |

**Every STOP check passed:**

| check | result |
|---|---|
| S5 total = universe + stat + c08; symmetry; min eig / max | 0; 5.6e-17; +1.2e-12 |
| cells: npz = work_cov = nonzero `E_U`; x (S5 / npz / work_cov); functionals; area | equal; 0; 0; 0 |
| npz r_X vs the reloaded runs; C_PL rebuilt | 0; 0 |
| Q symmetry; min eig / max | 5.5e-17; +1.2e-12 |
| control: `b_PB_dr` and frozen `bias_PB` p_∥ χ² vs VL175 and VL175 + C_PL | bit-equal to `playlist_term.json` |

The ranks of the S5 total and of Q are both 197 at rcond 1e-10.

## 2. Budget

Relative σ, in percent of `E_U`:

| matrix | cell median | cell p84 | cell max | integral | p_∥ projections | p_T projections | median cell σ / VL175 |
|---|---|---|---|---|---|---|---|
| VL175 (currently adopted) | 6.09 | 9.02 | 23.1 | 4.23 | 4.24–14.9 | 4.28–7.25 | 1 |
| S5 universe | 5.97 | 8.73 | 20.3 | 4.33 | | | |
| S5 stat | 0.68 | 1.71 | 18.0 | 0.061 | | | |
| S5 c08 (seed main effect) | 0.057 | 0.14 | 0.72 | 0.0025 | | | |
| **S5 total** | **6.04** | 8.95 | 23.3 | **4.33** | 4.30–13.7 | 4.36–7.27 | 1.015 |
| C_PL | 2.14 | 3.31 | 5.69 | 1.97 | 1.24–3.36 | 1.17–2.72 | 0.345 |
| **S5 total + C_PL** | **6.45** | 9.18 | 23.6 | **4.75** | 4.77–13.8 | 4.73–7.77 | 1.083 |

- **S5 against VL175:** S5 is close to VL175. The median cell σ is 6.04% against 6.09%, the median per-cell ratio
  is 1.015, and the integral is 4.33% against 4.23%. That difference is the whole recipe change, and S5 is the matrix
  the closeout built to replace VL175. Production DESIGN §8 lists the blocks: R5's three bootstrap streams, c08 in
  place of the ML seed scan, and X02, X03 and the background-separable arm reported but not added.
- **Adding C_PL to S5:**
  - Per-cell σ rises by a median of 5.4%, with a maximum of 34.5%.
  - The integral rises by 9.9%, from 4.33% to 4.75%.
  - The largest rise among the 31 functionals is 21.2%, in the p_∥ 6–7 GeV/c projection. The p_∥ projections rise
    most at 5–8 GeV/c (18%, 21% and 15%), and least at the ends of p_∥ (0.9% and 1.6%). The p_T projections rise
    by 2–10%.
  - C_PL carries a median 9.9% of the per-cell variance and 17.1% of the integral's. The share is larger for the
    integral because C_PL's leading mode is normalization-like (REPORT §2).

## 3. χ² rows (DESIGN §4; no pass/fail, no coverage reading)

| vector | marginal | vs VL175 | vs VL175 + C_PL | vs S5 | vs S5 + C_PL | first-order bound |
|---|---|---|---|---|---|---|
| `b_PB_dr` (1G–1M, reference 1A–1F) | p_∥ | 33.1 | 0.677 | 35.6 | 0.679 | 0.683 |
| | p_T | 2.85 | 0.557 | 2.58 | 0.541 | |
| `b_PC_dr` (1N–1P) | p_∥ | 2.86 | 0.306 | 3.54 | 0.314 | 0.340 |
| | p_T | 0.81 | 0.245 | 0.75 | 0.239 | |
| frozen raw `bias_PB` | p_∥ | 33.8 | 1.98 | 34.8 | 1.97 | — |
| | p_T | 1.96 | 0.60 | 2.17 | 0.65 | |
| frozen raw `bias_PC` | p_∥ | 2.62 | 0.40 | 3.42 | 0.41 | — |
| | p_T | 0.62 | 0.21 | 0.57 | 0.21 | |

- **The dr rows** lie in C_PL's span to first order. Against any total that contains C_PL they sit at or below the
  e-only bound, whatever the data. This is algebra, not evidence.
- **The raw rows** are mostly outside C_PL's span, so they are informative as a sensitivity, and only as that. They
  also include the MC-predicted flux difference that DESIGN §2 calls legitimate.
- **Replacing VL175 by S5** changes none of these readings. The 1G–1M p_∥ step is about as far outside S5 alone
  (33.1 → 35.6 for dr, 33.8 → 34.8 raw) as outside VL175 alone. With C_PL added, its raw p_∥ χ² falls to about 2 in both cases. That is a sensitivity
  reading, not a coverage test.

## 4. Limits (carried)

- **C_PL's own limits** (DESIGN §3, REPORT §3) travel with it:
  - three groups give about 1.8 effective degrees of freedom, so its size is uncertain at the order of 100%;
  - shrinkage by the regularization is uncorrected;
  - the noise is not subtracted;
  - the cause is unknown, and so is which period, if any, is correct.
- **S5's limits** (production DESIGN §8) travel with it:
  - G2 is carried, not repaired;
  - `NormDISCC` is null;
  - C07′ is omitted;
  - the background/signal-miss overlap was not measured;
  - learner dependence is omitted;
  - c08 has few degrees of freedom.
- **No coverage** of S5 or of S5 + C_PL has been tested (KI-85).
- **Pending dependencies:** the production REPORT and its F4 verifier are not yet on main. If F4 changes S5's
  bytes, this report is re-run against the new pin.

## 5. Next

- The disclosures, revision 2 (F10), take their numbers from this report and from the production REPORT.
- Joseph decides on J2: adopt S5 + C_PL, adopt S5 alone, or adopt something else.
