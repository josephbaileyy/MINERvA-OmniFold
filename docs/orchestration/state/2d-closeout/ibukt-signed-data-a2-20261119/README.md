# Signed-target IBU on the recorded 2D data: the terminal readout

`readout.json` is the study's terminal receipt, committed byte-identical so the analysis note's values file can read it
(DECISION-20261119g item 5: the four values of the note's one sentence come from this readout, never typed).

| | |
|---|---|
| SHA-256 | `a4ec72c1369d763469af1105839c944bee5487d8a69ecd6947d92fac6912317c` |
| Origin | `ibukt-signed-data-a2.aOBfm4/out/readout.json` under the campaign's scratch root, as [`OUTCOME-20261119-ibu-signed-data.md`](../../../OUTCOME-20261119-ibu-signed-data.md) records it |
| Copied from | the local audit copy, checked against the SHA-256 above before the copy |
| Declaration | [`IBU-SIGNED-DATA-DECLARATION.md`](../IBU-SIGNED-DATA-DECLARATION.md); execution binding [`IBUKT-BINDING-2.md`](../IBUKT-BINDING-2.md) |

The readout binds `out/study/signed_data.npz` by `product_sha256`
(`7a35b7e22e3d7aee4a21e81223dbe9a34a7c236ded143d9fbc6e8c31d730d11b`). That product is not committed here, because the
note's values need only the readout's distances.

## What the note reads

`distances/5` and `distances/10`, keys `er_vs_refined` and `er_vs_signed`, field `chi2_ndf` (ndf 205): the descriptive
χ²/ndf between the recorded OmniFold E_R and IBU results on the published covariance. These are OUTCOME rows 19–20.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the values the outcome reports, within the declaration's scope and DECISION-20261119g's.
- **Not citable for:**
  - any claim of cause, estimator accuracy, uncertainty or significance;
  - the known-truth screen, F-B or F-C;
  - any paper or manuscript wording.
