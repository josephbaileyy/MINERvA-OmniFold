# Signed-target IBU on the recorded 2D data

The login-node study passed under the [signed-data declaration](state/2d-closeout/IBU-SIGNED-DATA-DECLARATION.md)
and [execution binding](state/2d-closeout/IBUKT-BINDING-2.md).
It held the response, truth prior, extraction, and published covariance fixed
and substituted the signed data-minus-background target for the archived
Stay-Positive refined target. The 224 in-grid reco bins passed admissibility.
The replay reproduced the archived truth prior and the reported K=5 and K=10
cross-section vectors exactly. For the signed target, RooUnfold and NumPy
agreed to maximum relative differences of 2.54 × 10⁻¹⁵ at K=5
and 4.51 × 10⁻¹⁵ at K=10 on the 205 reporting cells.

## Distances on the published covariance

| Comparison | K | Signed χ² | Refined χ² | ndf | Signed χ²/ndf | Refined χ²/ndf | Signed minus refined χ²/ndf |
|---|---:|---:|---:|---:|---:|---:|---:|
| IBU versus publication | 5 | 167.248429 | 170.139110 | 205 | 0.815846 | 0.829947 | −0.014101 |
| IBU versus publication | 10 | 197.079065 | 210.447935 | 205 | 0.961361 | 1.026575 | −0.065214 |
| Recorded OmniFold E_R versus IBU | 5 | 332.279207 | 332.759801 | 205 | 1.620874 | 1.623219 | −0.002344 |
| Recorded OmniFold E_R versus IBU | 10 | 628.504822 | 639.689282 | 205 | 3.065877 | 3.120436 | −0.054558 |

The recorded E_R distance to the publication was 465.415272 / 205 = 2.270318.
The signed-target IBU estimate moved toward the publication at both fixed
iterations. The E_R–IBU distances changed by about 0.14% at K=5 and 1.75% at
K=10 relative to their refined-target distances. These are descriptive
sensitivities for the tested target substitution under the published metric.
The declaration limits interpretation to that substitution and metric.
Causal attribution, estimator accuracy, uncertainty, statistical significance,
publication adoption, and manuscript changes are outside that scope.

## Previously selected control cells

The declaration fixed 14 cells using the failed nominal run-c control. In
cross-section units, the largest absolute signed-minus-refined shift was
8.64 × 10⁻⁴² at K=5 and 1.64 × 10⁻⁴¹ at K=10, both in
zero-based global cell 145. This subset is descriptive because the earlier
control selected it.

Relative shift is `100 × (signed − refined) / refined`. Each denominator
is the refined cross section for the same cell and K in the digest-verified
product. The median uses the 14 signed relative shifts at each K.

| Global cell | (pT, p∥) bin indices | K=5 relative shift (%) | K=10 relative shift (%) |
|---:|:---:|---:|---:|
| 15 | (0, 15) | +1.54951 | +2.79573 |
| 31 | (1, 15) | -0.08449 | -0.35331 |
| 47 | (2, 15) | +0.28982 | +0.42552 |
| 63 | (3, 15) | +0.09693 | +0.10235 |
| 79 | (4, 15) | -0.01861 | -0.08589 |
| 95 | (5, 15) | +0.03891 | +0.05905 |
| 111 | (6, 15) | -0.10020 | -0.18313 |
| 127 | (7, 15) | +0.12981 | +0.30578 |
| 143 | (8, 15) | -0.05021 | +0.00405 |
| 159 | (9, 15) | -0.19395 | -0.24811 |
| 175 | (10, 15) | -0.25618 | -0.36062 |
| 191 | (11, 15) | -0.35159 | -0.60152 |
| 128 | (8, 0) | -3.73797 | -7.05035 |
| 145 | (9, 1) | -1.60045 | -3.05338 |
| Median | | -0.06735 | -0.13451 |

## Evidence and resources

The study used commit `853371c63ae390426351fd307391c46bfc4017ba` and the
historical REF-C2C1 checkout at `77d76cfc2d621f8faa010b75006811868494652a`.
Its terminal receipt is
`ibukt-signed-data-a2.aOBfm4/out/readout.json` under the campaign's scratch root,
SHA-256 `a4ec72c1369d763469af1105839c944bee5487d8a69ecd6947d92fac6912317c`.
The receipt binds `out/study/signed_data.npz` by SHA-256
`7a35b7e22e3d7aee4a21e81223dbe9a34a7c236ded143d9fbc6e8c31d730d11b`.
The guarded worker used 213.127 seconds wall time, 9,698,736 KiB peak RSS
(9.249 GiB), one numerical-library thread, and zero allocated node-hours.
