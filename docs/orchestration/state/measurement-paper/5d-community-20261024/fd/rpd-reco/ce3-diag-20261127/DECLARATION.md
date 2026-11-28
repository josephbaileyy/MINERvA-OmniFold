# C-E3 tail diagnostic for e1: declaration (2026-11-27, before it runs)

**By** limitation-resolver, under the director's ruling of 2026-11-27, after d2s0e1's C-E3 STOP with true Eν
(`../d2s0e1-20261127/run-20261127/`). In [8, 15) the median was 0.000987 (gate 0.002) and the 99th percentile 0.030147
(gate 0.03).

**The ruling:** no new gate and no new formula yet. First, one read-only, MC-only diagnostic, declared before it runs,
to find where the [8, 15) tail comes from with true Eν. The STOP stands on record whatever this finds.

## What it computes

Per p∥ stratum, [1.5, 8), [8, 15) and [15, 60], on reconstructed p∥, as C-E3 strata it. It uses exactly the rows and
weights C-E3 controls: signal rows with `w_reco · pass_reco` > 0, finite Eν and Eν ≥ Eμ.

It reports the weighted median, 99th and 99.9th percentiles of |q₃′/q₃ − 1| for:

1. **(i) C-E3's formula as bound:** q₃′² = 4 Eν Eμ sin²(θ/2) + (Eν − Eμ)². This is `energy_statistics` at
   2415e8d6, copied verbatim into the script.
   - `test_ce3_diag.py` checks the copy against the bound `energy_statistics` and `weighted_quantiles`, bit for bit,
     on fixtures.
   - On the node, (i) must **reproduce d2s0e1's STOP record bit for bit**: median 0.0009871258308031816 and q99
     0.0301471583174564 in 8:15. [1.5, 8) must also pass C-E1 and C-E3, as the STOP shows it did.
   - If either fails, the run reports **SELF-CHECK-FAILED**, exits 9, and gives no reading.
2. **(ii) the exact kinematics:** Q² = 2Eν(Eμ − |pμ| cosθ) − mμ² and q₃² = Q² + (Eν − Eμ)². This is the identity
   q₃² = Eν² + |pμ|² − 2Eν|pμ|cosθ.
   - (i) differs from it in two ways: |pμ| is replaced by Eμ, and mμ² is dropped.
   - The test checks that (ii) reproduces an exactly built q₃ to 1e-10.
3. **(iii) (i) with MCgen's float32 rounding.** MCgen stores p_T and p∥ in float32. The error of (i) is computed at
   the four corners p_T ± h, p∥ ± h, with h half the float32 spacing at each value. From these it reports:
   - the quantiles of the row-wise minimum and maximum, which bound each quantile under the rounding;
   - the largest shift.

It also reports C-E1's kinematic fraction in every stratum, including [15, 60], which the STOP never reached.

**Where the failing tail sits.** For the rows over the 0.03 gate in (i), per stratum:
- their count and weight fraction;
- weighted 5/50/95% quantiles of truth p_T, truth p∥, reconstructed p∥, Eν, Eμ, truth q₃, θ, Q² and (ii)'s error;
- their weight share across bins of p_T, p∥, Eν and q₃;
- how many have Eν within 1% of Eμ (|Eν/Eμ − 1| ≤ 0.01), with the same fraction for the whole stratum.

## The readings, stated now (the director's)

The gate is C-E3's own: median ≤ 0.002 and q99 ≤ 0.03 in each stratum, as in `evaluate_energy_controls`.

- **R-A.** If (ii) passes the gate in every stratum, with no nonfinite row, the tail comes from the control's massless
  approximation, not from the Eν source or the join. An amendment-2 proposal then goes to the director and Joseph. It
  will give the reason, and it keeps both C-E3 FAILs on record: 11-24 inverted and 11-27 true Eν.
- **R-B.** If (ii) does not pass every stratum, the STOP is reported as it stands, and e1's d2 ends there.
- **(iii)** is a quantification, not a reading. If its bounds on [8, 15)'s q99 straddle 0.03, that is reported as "the
  float32 rounding alone can move the verdict". Otherwise it is reported as not the cause.
- **The tail location** is descriptive only.

The script prints the verdict line `R-A …` or `R-B …` from (ii)'s gates. The readings above are what it means.

## Blinding, inputs, writes, cost

- **Blinding:** MC only. It reads only the keys MCreco, MCgen, w_reco, pass_reco and pass_truth from the dumps, and
  `energy` from flux4's products. The measured key is never read (asserted). No prediction is formed.
- **Inputs:** each file is opened O_NOATIME|O_NOFOLLOW through a no-symlink descriptor walk and read once into memory.
  Its sha256 is checked against the pins, and its atime is checked unchanged.
  - The 12 S1 dumps `fd-rpd-20261103/dumps/lat_<PL>.npz`, pinned by `fd/rpd-reco/INPUTS.sha256`.
  - flux4's 12 products `rpd-reco-flux4-20261126/run/flux-factors-<PL>.npz`, pinned by p0e1's committed `p0.json`.
  - `build_diag.py` fills the pins from those committed files. Nothing is typed.
- **Writes:** none on the cluster. The report is one JSON object on stdout.
- **Run:** one login02 session, `ssh saul.nersc.gov "ssh -o BatchMode=yes login02 'bash -s'" < ce3-diag.sh`.
  - `ce3-diag.sh` checks the embedded script's sha256 on the node.
  - It runs the script once at nice 19 with one thread, under d2-predict's interpreter (omnifold_py310).
- **Cost:** 0 node-h. A few minutes on the login node. Peak RSS is estimated at about 4 GB: the pooled controlled rows
  of 13 float64 columns plus one playlist's arrays.
- **Fence round:** cov2d, tier3-design and minerva-lib ack before it runs, and ibu-chi is told. The script's sha256
  goes to the director before it runs, and nothing runs without the director's GO.

## Files

| file | role |
|---|---|
| `ce3_diag.py` | the script (template; `PINS` empty) |
| `build_diag.py` | fills `PINS` from committed records, writes `ce3_diag_remote.py` and `ce3-diag.sh`; `--check` |
| `ce3_diag_remote.py` | the script that runs, which differs from the template only in its `PINS` line (tested) |
| `ce3-diag.sh` | the node wrapper |
| `test_ce3_diag.py`, `tests.txt` | the tests and their output |
