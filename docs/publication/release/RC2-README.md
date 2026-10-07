# MINERvA-OmniFold article release: release candidate 2 (NOT RELEASED)

**Status:** a local release candidate for review. It has not been deposited, tagged, uploaded or sent anywhere.
Publishing it is a separate decision for Joseph (DECISION-20261006 item 6: "Public deposit, release tagging,
submission ... remain separately authorized").

## What this package lets you reproduce

The calibrated joint tests of five generator predictions on the five-observable unbinned unfolding of MINERvA
medium-energy charged-current inclusive data (the article's Sec. VI and Table I). From the files here alone you can
recompute, with numpy and scipy only:

1. **The frozen joint-test result.** Every Monte Carlo p-value, k and B, Holm-with-determinacy decision, κ = 3
   robustness label and power figure of the recorded evaluation (`expected/joint-evaluate.json`).
2. **The lost-seed resolution, reading (a), report-only.** The same quantities with the 277 recovered
   pseudo-experiments added (`expected/resolved-evaluate.json`).
3. **The matched coarse-projection comparison (W1, report-only).** All 40 projected claim p-values and the criterion
   outcome (`expected/W1-RESULT-20261006.json`).
4. **The article's Figs. 1–3 and the numbers it quotes from them.** `data/figs/fig_arrays.npz` (640 KB) is
   exported from the committed producers' own loaders, and its manifest carries the sha256 of every source file.
   - `code/figs/fig_numbers.py` recomputes each quoted number and checks it against the printed value in
     `expected/values.tex`, the article's macro file, to within half a unit of its last printed digit. Covered: the
     2D total and its ratio, bins within 10%, the residual mean and RMS, χ²/ndf against the published covariance,
     the published median uncertainty, and the Fig. 3 generator ratios and ranges.
   - `code/figs/make_figs.py` regenerates the three figures. They show the same quantities as the article but are
     not pixel-identical; the article's Fig. 3 itself is drawn by this script.
   - `code/figs/plot_joint_null_distributions.py` regenerates Fig. 4 (the calibrated null distributions) from
     `data/frozen/`.

Run from this directory:

```
python3 code/verify_rc.py        # exit 0 and "VERIFY: PASS" if every replay and figure check agrees
```

or the individual steps. The last two write only to a scratch directory, so the package tree keeps matching
`SHA256SUMS`:

```
python3 code/replay_inference.py --npz data/frozen/inference_sufficient.npz --compare expected/joint-evaluate.json
python3 code/replay_inference.py --npz data/recovery-union/inference_sufficient.npz --compare expected/resolved-evaluate.json
OUT=$(mktemp -d)
python3 code/make_reading_b.py --frozen data/frozen/inference_sufficient.npz \
    --union data/recovery-union/inference_sufficient.npz --out $OUT/recovery-frozenS/inference_sufficient.npz
python3 code/w1_projected_tests.py --npz data/recovery-union/inference_sufficient.npz \
    --npz $OUT/recovery-frozenS/inference_sufficient.npz --recorded expected/joint-evaluate.json --out $OUT/w1.json
```

**How to check the W1 output** against `expected/W1-RESULT-20261006.json`:
- every claim `k`, `B` and `p`, and every criterion boolean, must be equal (they are all `false`);
- the reading labels (`group`, `reading`) and the `npz` paths are expected to differ, because they record where
  and how the inputs were built.

`verify_rc.py` performs exactly this comparison.

**Runtime:** `verify_rc.py` took between about 2 and 11 minutes in the tests made so far, on laptops and a login
node. numpy uses several threads, and the W1 and figure steps dominate. Each individual replay takes a few minutes or
less.

**Tested with:**
- Python 3.11.14 / numpy 1.26.4 / scipy 1.16.3 (Linux);
- numpy 1.26.4 / scipy 1.15.2 (macOS), with the system Python 3 and with Python 3.12.2 (conda-forge).

The last was run by an independent outside-reader test from an empty directory.

**Comparison tolerance:** relative 1e-12 on floats. Integers and decisions must match exactly.

## Contents

| path | what it is |
|---|---|
| `data/frozen/inference_sufficient.npz` (+ `.manifest.json`) | Per null hypothesis, the J-cell vectors of every calibration pseudo-experiment after the declared lateral, normalization and numerical terms (`F__<null>`), their pseudo-seeds, the prediction and its MC variance, the test domain, and the variant shift vectors. Globally: the frozen metric V, the observed data vector, the 20 data rounding jitters, the 109 supported-cell indices and the fine-to-J map. Power alternatives are included. The manifest records the frozen code and design digests and the sha256 of every one of the ~7,000 source products. |
| `data/recovery-union/…` | The same, with the 277 recovered lost seeds added (reading (a) of the report-only resolution) |
| `code/replay_inference.py` | Standalone replay of the frozen rules (statistics, rank p-value with exact Clopper–Pearson interval, claim rule over variants, Holm with determinacy, κ = 3 labels, power) |
| `code/make_reading_b.py`, `code/w1_projected_tests.py` | The reading-(b) builder and the W1 projected tests |
| `data/figs/fig_arrays.npz` (+ `.manifest.json`) | The arrays behind Figs. 1–3, on their reporting binnings, with source digests |
| `code/figs/fig_numbers.py`, `code/figs/make_figs.py` | The quoted-number check and the figure regeneration |
| `expected/values.tex` | The article's printed values, the authority for `fig_numbers.py` |
| `code/verify_rc.py` | Runs all of the above against `expected/` |
| `expected/` | The frozen evaluator's outputs and the committed W1 result |

**Absolute paths:** the `/pscratch/...` paths inside the manifests and `expected/` files record provenance only. No
step reads them.

**`jitters`:** the frozen evaluator used the 20 data rounding jitters to report the observed-p stability
(`observed_jitter_p` in `expected/`). The replay does not recompute that field, and the array is included for
completeness.

## What these tests are, and the conditions that travel with them

For each prediction G, H₀(G) is the simple fine-grid hybrid null that the calibration simulates. There are 10
tests, total and shape for each G, at familywise α = 0.05.

All ten are rejected, under these conditions:
1. the fine-grid residual is unconverged, and enters as declared variants;
2. the detector model is the simulation's, varied only by the drawn bands. **There is no calorimetric
   recoil-response band.** An exploratory ±4% sensitivity leaves every rejection in place;
3. the interaction-model prior is the analysis band set, with negative weights clipped per universe;
4. there is a half-MC process shift, bounded by a declared variant;
5. GiBUU lacks E_ν > 20 GeV;
6. the predictions' finite MC is included.

**The metric V sets power only. It is not a measurement covariance.** These are tests of specified predictions.
**They are not a cross-section measurement with uncertainties**, and no five-dimensional measurement with qualified
uncertainties exists for this analysis.

## Reproduction levels and access boundaries

| level | status |
|---|---|
| **Sufficient-input replay** (this package) | Complete for the joint tests, the resolution reading (a) and W1. Public. |
| **Extraction from products** (`extract_inference_sufficient.py` in the source repository) | Needs the ~7,000 calibration products and the frozen deploy, on NERSC `/pscratch`. Not public; the products could be released separately, which is an author decision. |
| **Event processing** (event loop, unfolding, pseudo-experiment production) | Needs the MINERvA open-data AnaTuples, released under CC0 (DOI 10.15484/3022562), in the earlier production analysed here, plus the generator samples produced for this analysis. **Not reproducible from this package.** |

**Not in this package:**
- the article's 6.87% median uncertainty, which needs the covariance rollup (VL172 in the source repository);
- the E_ν ≥ 20 GeV share statements, which need per-E_ν predictions;
- the comparison with Ascencio *et al.*;
- the five-dimensional central-value release (a separate package, `release-package-20260922`);
- the W2 shifted data products;
- reading (b) as a file (it is rebuilt by `make_reading_b.py`).

**Source:** github.com/josephbaileyy/MINERvA-OmniFold, branch `docs/publication-decision-20261005`. The
receipts are `docs/publication/release/RECEIPT-20261006-inference-sufficient-*.json`.
