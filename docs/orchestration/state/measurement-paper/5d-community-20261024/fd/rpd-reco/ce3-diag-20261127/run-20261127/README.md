# C-E3 tail diagnostic for e1, 2026-11-27 (login02): reading R-B

**By** limitation-resolver, under the declaration [`../DECLARATION.md`](../DECLARATION.md), merged in #1418 as
3db37378 before the run. The director gave the GO for these shas: `ce3-diag.sh` `9d2e6b45`, `ce3_diag_remote.py`
`81a06992`.

**Result: reading R-B holds.** The exact form (ii) does not pass every stratum.
- Under the declared readings, d2s0e1's C-E3 STOP stands, and e1's d2 ends there. The director accepted this on
  2026-11-27.
- It is a finding, and nothing was loosened.
- Both C-E3 FAILs stay on record: 11-24 with inverted Eν, and 11-27 with true Eν.

- **CITABLE FOR:** the per-stratum quantiles below, as a diagnostic of C-E3's operands. Also that C-E3's massless
  approximation and MCgen's float32 rounding do not account for the failure.
- **NOT CITABLE FOR:** any RPD-RECO result, any cause of the tail, or note wording.

## The run

- **Setup:** a clean checkout at 3db37378, with both files re-hashed equal to the GO's shas. The cert was re-read at
  05:25:05Z (`TZ=UTC ssh-keygen -L`), valid to 2026-11-28T02:05:18Z.
- **Acks:** cov2d (05:13:31Z), tier3-design (05:13:32Z) and minerva-lib (05:13:37Z), verbatim in [`acks/`](acks/).
  ibu-chi was told. END followed at 05:27Z.
- **The session:** one login02 session, 05:25:05Z to 05:26:24Z, ssh rc 0 and script rc 0
  ([`launcher.txt`](launcher.txt), [`diag.err.txt`](diag.err.txt)). It used 72.3 s of compute, under omnifold_py310
  (python 3.10.19, numpy 2.2.6).
- **Inputs:** all 24 (12 S1 dumps and 12 flux4 products) were read O_NOATIME. Each sha256 matched its pin, and each
  atime was unchanged. Nothing was written on the cluster.
- **The report:** [`diag.json`](diag.json), sha256 `4176ab0b…`.
- **Self-check: PASS.** (i) reproduced the STOP record bit for bit in 8:15: `[0.0009871258308031816,
  0.0301471583174564]`. [1.5, 8) passed C-E1 and C-E3.

## The quantiles of |q₃′/q₃ − 1| (weighted: median, 99th, 99.9th percentile)

The gates are C-E3's: median ≤ 0.002 and q99 ≤ 0.03.

| stratum | rows | C-E1 | (i) as bound | (ii) exact | (iii) float32 bounds on (i)'s q99 |
|---|---:|---|---|---|---|
| [1.5, 8) | 17,508,038 | 1.0 | 0.001293, 0.023992, 0.054071 (PASS) | 0.000960, 0.023773, 0.053672 (PASS) | 0.023992 to 0.023993 |
| [8, 15) | 1,990,998 | 1.0 | 0.000987, **0.030147**, 0.069939 (FAIL) | 0.000939, **0.0301465**, 0.069867 (**FAIL**) | 0.0301461 to 0.0301476 |
| [15, 60] | 903,501 | 1.0 | 0.000673, **0.050618**, 0.136730 (FAIL) | 0.000664, **0.050643**, 0.136772 (**FAIL**) | 0.050616 to 0.050620 |

(ii) has no nonfinite row and no negative Q² in any stratum. The largest float32 shift of a single row's error is
2.4e-5.

## What it shows

1. **The massless approximation is not the cause.** The exact form moves [8, 15)'s q99 by 7e-7, and [15, 60]'s up
   slightly.
2. **The float32 rounding is not the cause.** Its bounds on [8, 15)'s q99 lie entirely above 0.03.
3. **[15, 60] fails too, and by more** (q99 0.0506 under both forms). The bound run stopped at [8, 15) and never
   reached it.

## Observation (no cause claimed)

| | [1.5, 8) | [8, 15) | [15, 60] |
|---|---|---|---|
| tail rows (error > 0.03) | 134,306 | 26,925 | 23,435 |
| tail weight fraction | 0.56% | 1.01% | 2.50% |
| tail weight with Eν within 1% of Eμ | 20.6% | 47.4% | 56.9% |
| the stratum's weight with Eν within 1% of Eμ | 0.44% | 1.88% | 3.19% |
| tail median q₃ (GeV) | 0.27 | 0.31 | 0.52 |
| tail median θ (mrad) | 41 | 27 | 15 |
| tail median (ii) error | 0.038 | 0.040 | 0.045 |

The tail is concentrated at small q₀ = Eν − Eμ and small θ, where q₃ is small. (ii) is the exact identity q₃² = Eν² +
|pμ|² − 2Eν|pμ|cosθ. So a remaining median error near 4% on those rows means MCgen's q₃ column is not reproduced from
(Eν, p_T, p∥) for them.

This run did not establish why. The director records it as a possible v2 question about how MCgen's q₃ was computed.
The full quantiles of p_T, p∥, Eν, Eμ, q₃, θ, Q² and (ii)'s error in the tail, and the tail's weight shares by bin, are
in `diag.json`.

## What follows

- e1's d2 ends at the C-E3 STOP, and nothing downstream is packaged.
- The director assigned the removal of the now-unused e1 roots, under Joseph's 2026-11-27 rule "remove things that
  are unused". It happens after this PR merges, through a manifest and a listing-sha handshake with the director, by
  literal paths only:
  - `rpd-reco-p0e1-20261126/`, the omnifile copies first;
  - `rpd-reco-flux4-20261126/`;
  - `rpd-reco-d2s0e1-20261127/`.
- The RDX sidecar, the omnifiles, lat_zero and the S1 dumps are not ours, and they stay.

[`SHA256SUMS`](SHA256SUMS) covers every file in this directory except itself.
