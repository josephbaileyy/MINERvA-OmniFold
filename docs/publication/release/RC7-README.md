# MINERvA-OmniFold article release: release candidate 7 (NOT RELEASED)

**Status:** a local release candidate for review. It has not been deposited, tagged, uploaded or sent anywhere.
Publishing it is a separate decision for Joseph (DECISION-20261006 item 6: "Public deposit, release tagging,
submission ... remain separately authorized").

**RC7 supersedes RC6.**
- RC6 (`71e2b7a4fc952ecd3494f75d4454f7add7ee01eb08aeb77ade5bc62d45c1461e`) is reproducible from source commit
  `35146cc1` and is preserved on CFS (`rc6/`).
- RC7 differs from it in the figure code only. Joseph asked on 2026-10-08 for the article's hard-to-read figures to be
  redrawn (editorial pass, `docs/publication/EDITORIAL-20261008-prd-presentation-pass.md` §9):
  - `code/figs/make_figs.py` now draws Figs. 1–3 at journal size, and **the article prints its output**. Fig. 1 gains
    ratio panels with the published ±1σ band, and its residual map has bin-edge labels. Fig. 2 has bin-edge axes,
    labelled colour bars, a value printed in each cell, and its panels stacked for one column. Fig. 3 drops the
    multiple-slash units and uses the article's generator labels.
  - The figure PDFs carry no timestamp. With the versions in `requirements-lock.txt`, `make_figs.py` reproduces the
    article's figure files byte for byte (sha256 below). Other versions give the same quantities, not the same bytes.
  - The article's macro files (`expected/values*.tex`) and every data file are unchanged from RC6.

| article figure file (`docs/analysis-note/figures/`) | `make_figs.py` output | sha256 (requirements-lock.txt versions) |
|---|---|---|
| `paper_fig1_validation.pdf` | `fig1_validation.pdf` | `938c4fc955c57e6ed95e3343755f1513e063817d497d09c6f63095d066127572` |
| `paper_fig2_joint.pdf` | `fig2_joint_localization.pdf` | `57f3cc601281950cf9251b04a627efa3e0d803eca6620178839c48f9d4b0782a` |
| `paper_fig3_generators.pdf` | `fig3_generator_context.pdf` | `e9d1bb01fc79e061b95b6e058a2aa2a03275429db5c4531b5e3d9ec63d65fa93` |

**Inherited from RC6** (its differences from RC5): the `observed_jitter_p` statement, the `fig_numbers.py` negative
control, `requirements-lock.txt`, and the reviewed macro wording.

**What changed from RC4** (PRD release audit `ea939701`; corrections record
`docs/publication/corrections-20261008/RECORD-20261008-release-audit-corrections.md` in the source repository):

- **Dependencies.** matplotlib is now documented, because the figure steps need it. The versions are pinned in
  `requirements.txt`. RC4's README listed only numpy and scipy, and with exactly those `verify_rc.py` failed its two
  figure steps.
- **Condition (i).** Its fine-grid L2 ratios (0.50–0.86) are recomputable: `data/m1f2/` and
  `code/m1_f2_norm_ratio.py` are new, and `verify_rc.py` checks the result.
- **Fig. 1.** The inset prints the article's 2D median ("This work", from `expected/values.tex`) instead of
  "pending VL170".
- **Sec. V numbers.** Its printed ratios are `values.tex` macros, which `fig_numbers.py` reads, so it no longer
  checks against a hard-coded copy.
- **AnaTuple identities.** The file names, sizes and modification times of the analysed AnaTuples are in
  `data/anatuple-inventory.tsv`. Checksums are not included.
- **Article sources.** `expected/values.tex` and `expected/values_inference.tex` are the article's macro files at the
  corrected source commit.
- **Data files.** The sufficient-input and figure-array files are **byte-identical to RC4's**.

**RC4 and RC5 are preserved unchanged.** RC4 (sha256 `46f801bf05bbd18d1fcfe8c8bf5b0e361cd8e352211de641b434547be1680e88`)
and RC5 are at `/global/cfs/cdirs/m3246/josephrb/prd-release-preservation-20261008/rc4/` and `rc5/`.

## What this package lets you reproduce

The calibrated joint tests of five generator predictions on the five-observable unbinned unfolding of MINERvA
medium-energy charged-current inclusive data (the article's Sec. VI and Table I). From the files here alone you can
recompute, with numpy, scipy and matplotlib:

1. **The frozen joint-test result.** Every Monte Carlo p-value, k and B, Holm-with-determinacy decision, κ = 3
   robustness label and power figure of the recorded evaluation (`expected/joint-evaluate.json`).
2. **The lost-seed resolution, reading (a), report-only.** The same quantities with the 277 recovered
   pseudo-experiments added (`expected/resolved-evaluate.json`).
3. **The matched coarse-projection comparison (W1, report-only).** All 40 projected claim p-values and the criterion
   outcome (`expected/W1-RESULT-20261006.json`). W1 uses the recovery-union readings, B = 1400 (1800 for NuWro).
4. **The article's Figs. 1–4 and the numbers it quotes from Figs. 1–3.**
   - `code/figs/fig_numbers.py` recomputes each quoted number from `data/figs/fig_arrays.npz` and checks it against
     the printed value in `expected/values.tex`, to within half a unit of its last printed digit. That includes the
     Sec. V generator ratios, the Fig. 2 ratio ranges and verbal shares, and the Fig. 3 caption's 9–12 %.
   - `code/figs/make_figs.py` regenerates Figs. 1–3 as printed: the article's figure files are this script's output
     (byte-identical with the `requirements-lock.txt` versions; see the table above).
   - `code/figs/plot_joint_null_distributions.py` regenerates Fig. 4.
5. **Condition (i)'s fine-grid L2 ratios.**
   - `code/m1_f2_norm_ratio.py` computes ‖D_M1/f_mid‖ / ‖D_F2/f_coarse‖ per generator from `data/m1f2/`:
     0.759, 0.857, 0.542 and 0.504. That gives the printed 0.50–0.86. The norm is the L2 norm of the per-cell
     *relative* differences; the raw L2 ratio does not reproduce the printed range.
   - `verify_rc.py` also checks that the released M1 shifts equal the frozen evaluator's `d1` vectors.

Run from this directory, after `python3 -m pip install -r requirements.txt` in a fresh environment:

```
python3 code/verify_rc.py        # exit 0 and "VERIFY: PASS" if every replay and figure check agrees
```

or the individual steps. The last two write only to a scratch directory, so the package tree keeps matching
`SHA256SUMS`:

```
python3 code/replay_inference.py --npz data/frozen/inference_sufficient.npz --compare expected/joint-evaluate.json
python3 code/replay_inference.py --npz data/recovery-union/inference_sufficient.npz --compare expected/resolved-evaluate.json
python3 code/figs/fig_numbers.py --npz data/figs/fig_arrays.npz --values expected/values.tex
python3 code/m1_f2_norm_ratio.py data/m1f2
OUT=$(mktemp -d)
python3 code/make_reading_b.py --frozen data/frozen/inference_sufficient.npz \
    --union data/recovery-union/inference_sufficient.npz --out $OUT/recovery-frozenS/inference_sufficient.npz
python3 code/w1_projected_tests.py --npz data/recovery-union/inference_sufficient.npz \
    --npz $OUT/recovery-frozenS/inference_sufficient.npz --recorded expected/joint-evaluate.json --out $OUT/w1.json
```

**How to check the W1 output** against `expected/W1-RESULT-20261006.json`:
- every claim `k`, `B` and `p`, and every criterion boolean, must be equal (they are all `false`);
- the reading labels and the `npz` paths are expected to differ.

`verify_rc.py` performs exactly this comparison.

**Runtime:** about 2–11 minutes in the tests made so far. numpy uses several threads, and the W1 and figure steps
dominate.

**Tested with** `requirements.txt`, which resolved to the exact versions in `requirements-lock.txt`: Python 3.11.15, numpy 1.26.4, scipy 1.15.2, matplotlib 3.11.2 (macOS arm64,
fresh virtual environment, empty directory). The earlier candidates were also run with numpy 1.26.4 and scipy
1.16.3 on Linux (Python 3.11.14), and with scipy 1.15.2 on macOS (Python 3.12.2, conda-forge).

**Comparison tolerance:** relative 1e-12 on floats. Integers and decisions must match exactly.

**`jitters` and `observed_jitter_p`.**
- The frozen evaluator used the 20 data rounding jitters (included as the `jitters` array) to report the stability of
  the observed p-values (`observed_jitter_p` in `expected/joint-evaluate.json`).
- `replay_inference.py` does not recompute or compare that field. The article's statement that rounding changes only
  NuWro's shape test (2/1752 to 3/1752) is therefore not checked by `verify_rc.py`.
- It is reproducible from the `jitters` array: the release audit's check script, `checks/agentC_checks.py` on the audit
  branch, recomputed it exactly.

## How this package is built

The tarball is byte-reproducible from the source repository and the RC4 data files:

```
python3 publication/release/build_rc.py --payload <dir holding data/frozen, data/recovery-union, data/figs> \
    --payload-sums docs/publication/release/RC4-SHA256SUMS.txt --name minerva-omnifold-article-release-rc7 --out <dir>
```

- `build_rc.py` takes code, expected outputs, `requirements.txt` and this README from the repository, and the three
  data files from `--payload`, checking each against RC4's checksums.
- It writes sorted entries with fixed mtimes, owners and modes, and an un-timestamped gzip, so the same inputs give
  the same sha256.
- The simplest payload is the extracted RC4 tarball, which has exactly that `data/...` layout.
- The CFS copy of the same files under `pscratch/sd/j/josephrb/pub-release-20261006/` uses a different layout
  (`frozen/`, `union/`, `figs/`), so it must be arranged as `data/frozen`, `data/recovery-union` and `data/figs`
  before use.
- `docs/publication/release/RC7-SHA256SUMS.txt` records the tarball's digest and the contents' checksums.

## Contents

| path | what it is |
|---|---|
| `data/frozen/inference_sufficient.npz` (+ `.manifest.json`) | Per null hypothesis: the J-cell vectors of every calibration pseudo-experiment after the declared lateral, normalization and numerical terms (`F__<null>`), their pseudo-seeds, the prediction and its MC variance, the test domain and the variant shift vectors. Globally: the frozen metric V, the observed data vector, the 20 data rounding jitters, the 109 supported-cell indices and the fine-to-J map. Power alternatives are included. The manifest records the frozen code and design digests and the sha256 of every source product. |
| `data/recovery-union/…` | The same, with the 277 recovered lost seeds added (reading (a)) |
| `data/figs/fig_arrays.npz` (+ `.manifest.json`) | The arrays behind Figs. 1–3, on their reporting binnings, with source digests |
| `data/m1f2/` | The four F2 (fine minus coarse) and four M1 (fine minus twofold-merged) noise-free asimov differences, with `MANIFEST.json`, which gives each file's receipt and inputs |
| `data/anatuple-inventory.tsv` | Name, size and modification time of each of the 2,374 analysed open-data files (an earlier production of the open-data release, 11,523,656,218,592 bytes). Checksums are not recorded. |
| `code/` | `replay_inference.py`, `make_reading_b.py`, `w1_projected_tests.py`, `m1_f2_norm_ratio.py`, `figs/`, and `verify_rc.py`, which runs all of them against `expected/` |
| `expected/` | The frozen evaluator's outputs, the committed W1 result, and the article's macro files `values.tex` and `values_inference.tex` |
| `requirements.txt`, `requirements-lock.txt` | The tested top-level versions, and every resolved dependency |

**Absolute paths:** the `/pscratch/...` paths inside the manifests record provenance only. No step reads them.

## What these tests are, and the conditions that travel with them

For each prediction G, H₀(G) is the simple fine-grid hybrid null that the calibration simulates. There are 10
tests, total and shape for each G, at familywise α = 0.05.

All ten are rejected, under these conditions:
1. the fine-grid residual is unconverged and enters as declared variants. The proxy convergence rate behind those
   variants is a design-review value whose calculation is not recorded;
2. the detector model is the simulation's, varied only by the drawn bands. **There is no calorimetric
   recoil-response band.** An exploratory ±4 % data-side sensitivity leaves every rejection in place;
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
| **Sufficient-input replay** (this package) | Complete for the joint tests, the resolution reading (a), W1, condition (i)'s L2 ratios, and the figure numbers. |
| **Extraction from products** (`extract_inference_sufficient.py` in the source repository) | Needs the ~7,000 calibration products (archived on NERSC CFS, `s5p-archive-20261006`, SHA256SUMS `1a72cb43…`) and the frozen code. Not public. |
| **Event processing** | Needs the MINERvA open-data AnaTuples (CC0, DOI 10.15484/3022562) in the earlier production listed in `data/anatuple-inventory.tsv`, plus the generator samples produced for this analysis. **Not reproducible from this package.** |

**Article numbers this package does NOT reproduce.** Their authority is the records named in the source repository.

- **2D uncertainty and coverage** (VL169, VL170, VL172; rescoring `state/ki84-rebuild-20261006/rescore_vl169_toys_vl170.json`):
  - 6.87 % median;
  - 0.674 % statistical median;
  - 91.2 % / 0.679;
  - 97.7 % / 78.1 %.
- **Closure and bias studies:**
  - 4 %, 0.3 %, 1 % and 1.4 % (VL149, VL151, VL152);
  - 74 % (VL151);
  - 16–31 % and "about half" (VL154, with the joint-test estimator);
  - "about fifteen-fold" (VL149/VL151; computation in the corrections record).
- **Low-recoil comparisons:**
  - 52 % (VL160);
  - under 1 % for pion FSI (`3d-unfolding/genie/genie_fsi_*_summary.txt`);
  - "within 10 %" of Ascencio *et al.* (the ledger's 2026-06-10 Ascencio entry), together with its truth-definition
    caveat (`docs/EAVAIL_DEFINITION.md` §4, OI-59).
- **E_ν ≥ 20 GeV shares** (VL161).
- **Recoil-response sensitivity (W2)** (`publication/w2/W2B-REPORT-20261006.md` and its 2026-10-08 addendum):
  - the 11 % shift;
  - NuWro shape k = 3, p = 0.0023.
- **Proxy convergence rate** 0.45–0.76 per halving (amendment 7 `claims.rejection`). Its calculation is not recorded.
- **Covariance-status measurements:**
  - 6.145 % (`GRADE-20260920-cause3-two-member.json`, control VL146);
  - 6.02 % / 6.02 % (`SEED-EFFECT-20260920.json`);
  - 20.91 % → 7.57 % and 1.467 (the FLOOR JSONs);
  - 26.0 % (`EVIDENCE-20260919-lateral-bands-are-seed-pinned.md`);
  - 6.02 % / 1.06 % (`CENTRAL-VALUE-VS-SIGMA-20260920.json`);
  - the adoption itself (VL142–VL144).
- **Event counts and exposure:** 4.12 M data events, 32.8 M true signal events, 1.057e21 POT.
- **The five-dimensional central-value release** (a separate package, `release-package-20260922`).
- **The W2 shifted data products**, and reading (b) as a file (`make_reading_b.py` rebuilds it).

**Source:** github.com/josephbaileyy/MINERvA-OmniFold, branch `fix/prd-release-audit-corrections-20261008`.
