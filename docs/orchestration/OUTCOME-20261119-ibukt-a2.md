# IBUKT A2 known-truth recovery, run d

The run completed its 35 paired recoveries and produced a scoring PASS
receipt. A2 compares signed-target binned IBU with Stay-Positive
refined-target OmniFold on the same pseudo-data draws. The seven truths use
five fixed Poisson draws each, one fixed simulated bank, the nominal response
and the frozen learner seeds. The [original declaration §6](state/2d-closeout/IBUKT-DECLARATION.md)
defines the coarse-cell readings and [A2](state/2d-closeout/IBUKT-DECLARATION-A2.md)
applies them to these two complete workflows, including their differing
target treatment.

## Controls and execution

- **Admissibility and signed identity, A2 §§3 and 5.** All 36 signed targets
  passed the fit-free checks across the full 224-cell reco grid. The signed
  identity covers 205 supported truth columns and 205 supported reco rows.
  The nominal histogram matched response row sums to a maximum relative
  difference of 6.64 × 10⁻¹⁴. At K=5 and K=10 the largest relative
  discrepancy against the nominal prior across RooUnfold and NumPy was
  1.16 × 10⁻¹³, and the largest RooUnfold–NumPy discrepancy was
  9.15 × 10⁻¹⁵. The bound threshold is 10⁻⁹.
- **Noise-free nominal, A2 §3.** The maximum absolute K=5 residual over the
  205 reporting cells was 1.708252% for refined-target OmniFold and
  8.37108 × 10⁻¹²% for signed-target IBU. Both passed the 2% engineering
  control. This is the gateway to the recovery ensemble.
- **Runtime preflight, original §7 and A2 accounting.** The screen passed
  the [one-pair forecast](state/2d-closeout/ibukt-a2/screen-forecast.json)
  and completed all 35 pairs. The timed pair recorded 408 seconds. At
  admission, 7,344 seconds were projected for the remaining pairs, with
  17,843 seconds available under the governing limit. The screen PASS
  receipt binds the forecast, admissibility, nominal control and pairs.

## Coarse-cell readings

The [per-cell classifications](state/2d-closeout/ibukt-a2/cell-readings.tsv)
give each ordered K=5 pair in OmniFold, IBU order for all 1,435 truth/cell
combinations, followed by the secondary IBU K=10 classification. The
[full scoring readout](state/2d-closeout/ibukt-a2/readout.json) gives the five
signed residuals in trial order, mean, descriptive noise guard and
coarse-bin truth departure for every method and cell. Join arrays by the
truth's ordered `cells` vector.

W means within tolerance, O outside tolerance, and U unresolved. Each
method column reports W/O/U counts over 205 cells.

| Truth | OmniFold K=5 | IBU K=5 | IBU K=10, secondary |
|---|---:|---:|---:|
| nominal | 196/0/9 | 117/0/88 | 80/0/125 |
| genie_mec | 109/38/58 | 79/10/116 | 59/4/142 |
| nuwro | 101/49/55 | 75/23/107 | 58/15/132 |
| bump | 179/7/19 | 102/4/99 | 77/0/128 |
| tilt | 186/0/19 | 129/3/73 | 88/1/116 |
| within_plus | 98/64/43 | 61/40/104 | 35/37/133 |
| within_minus | 103/68/34 | 60/36/109 | 38/29/138 |

The primary method readings combine as follows.

| Truth | Both W | OmniFold W / IBU O | OmniFold O / IBU W | Both O | Any U |
|---|---:|---:|---:|---:|---:|
| nominal | 117 | 0 | 0 | 0 | 88 |
| genie_mec | 69 | 1 | 0 | 9 | 126 |
| nuwro | 57 | 2 | 7 | 18 | 121 |
| bump | 102 | 0 | 0 | 3 | 100 |
| tilt | 128 | 1 | 0 | 0 | 76 |
| within_plus | 57 | 0 | 0 | 39 | 109 |
| within_minus | 57 | 0 | 0 | 35 | 113 |

**Differential coarse-cell licence, original §6 and A2.** At K=5,
OmniFold was within and IBU outside at GENIE+MEC cell 57, NuWro cells
22 and 95, and tilt cell 216. The reverse reading occurred at NuWro
cells 19, 40, 56, 65, 87, 113 and 151. These are zero-based global
cell indices on the bound bank. Neither fractional-pT within-bin tilt
produced the IBU-outside/OmniFold-within combination. The declaration's
specific within-cell model-dependence licence was unused.

**Both-within, both-outside, and unresolved licences, original §6 and A2.**
The both-within cells recovered their tested coarse integrals under the
fixed bank, seeds and tolerance. For both-outside cells, both workflows'
guarded residuals exceed the 2% tolerance. For a comparison with any
unresolved member, the five draws did not resolve the tolerance comparison.
These readings apply cell by cell, including for the two within-bin tilts
with conserved coarse truth integrals.

**Secondary reading, original §6.** The IBU K=10 results are descriptive
and retain the same per-cell thresholds and five-draw guard. The primary
comparisons use K=5. The outcome licences are conditional on these truths,
draws and workflows. Coverage, global estimator ranking, causal attribution
for the measured data difference, and manuscript changes are outside this
study's scope.

## Resources and terminal records

| Slurm job | Stage | Allocation state | Elapsed seconds on one CPU node |
|---|---|---|---:|
| 61556304 | Earlier prepare | FAILED | 638 |
| 61559122 | Run c prepare | COMPLETED | 832 |
| 61567091 | Run c screen | FAILED | 466 |
| 61575832 | Run d prepare | COMPLETED | 721 |
| 61576631 | Run d screen | COMPLETED | 9,020 |
| 61589874 | Run d score | TIMEOUT | 365 |

The full charge is **12,042 seconds = 3.345 CPU node-hours** against the
6.50 cap, including the complete elapsed time of the score allocation.
The signed-data study, rehearsal and envstage each used zero allocated
node-hours.

**Score allocation timeout.** Slurm recorded the parent allocation as
TIMEOUT at 365 seconds against a 360-second limit, with exit code 0:0.
The producer step completed in 220 seconds. The director confirmed the
readout was written at 18:46:45 UTC and the worker wrote PASS at
18:47:56 UTC after its output checks. The allocation ended at 18:47:58 UTC.
The director accepted that worker PASS and ordered the full 365-second
charge. The [scheduler step record](state/2d-closeout/ibukt-a2/sacct-steps.txt)
preserves the parent allocation's TIMEOUT and the completed steps.

## Evidence identities

The deployment was `0bb36240a320bbbdb7fad685fbabd4acca491223`. The
[execution binding](state/2d-closeout/IBUKT-BINDING-2.md) and the launcher
at `853371c63ae390426351fd307391c46bfc4017ba` control the run. The
scratch run root is `ibukt-20261119-d`.

| Receipt or product | SHA-256 |
|---|---|
| Envstage PASS | `3641f411f0d967771cb0d4382709f1596ce7578a523148cc5e63da88970c65da` |
| Prepare PASS | `6a908c96a5bc84713c746eaa909788b032555f01282563e929b9ebedb2b69704` |
| Screen PASS | `c7c61254053201a7fc8b368de82cc2c9796e767d00ec24c67feeda95ecf6c5fa` |
| Screen forecast | `384af4b0393d065fe83a635daca274adc6614cb9bef8ce01c5ed2b56166e0f1f` |
| Signed-target admissibility | `da68dbf5643d474254896612b418a1c8126ee0e639dd8d8d845a8e8db8c7dec1` |
| [Score worker PASS](state/2d-closeout/ibukt-a2/PASS.json) | `03f007b8cd2730f2d8b0a188e81e5cdc0e72a7c72fd501dfea74381b78dc297c` |
| Score readout | `dfae50f595ac37b5179722a6a9d264f758cce91c163ca6cc1ab3b03462da8da6` |

The committed readout matches the received score product byte for byte.
The cell index and tables reproduce the classification from the five
residuals at each truth, method and cell using the declared formula.
The [separate signed-data outcome](OUTCOME-20261119-ibu-signed-data.md)
covers the target substitution on recorded data.
