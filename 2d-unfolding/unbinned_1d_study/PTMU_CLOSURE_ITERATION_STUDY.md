# pTmu closure and iteration-scan study guide

## What this study is for

This study is the next clean step after establishing that the unbinned OmniFold pipeline runs stably.
It answers three questions:

1. `Does the 1D unfolding implementation close?`
2. `Does unfolding actually improve the reco-level bias?`
3. `Which iteration count is justified by closure, rather than chosen by habit?`

The new driver for this study is:

- `Documents/ptmu_closure_iteration_study.py`

It is intentionally separate from the production script so the main physics pipeline stays untouched.

## What the script actually does

This implementation is a **signal-only split-sample closure test in event-count units**.
That choice is deliberate.
It isolates the unfolding behavior from background-subtraction choices and from later cross-section normalization steps.

### Step 1: read the current OmniFold inputs

The script reads:

- `Documents/runEventLoopOmniFold.root`
- `Documents/runEventLoopData.root`

The first file provides the signal MC entries used for the closure study.
The second file is used only to get the standard `pTmu` binning from `pTmu_data`.

### Step 2: split the signal MC into two statistically independent halves

The `mc_signal_reco` tree is split by entry parity:

- `even` entries become the **train/response** sample, or
- `odd` entries become the **pseudo-data** sample,

with the opposite choice used for the complementary half.

This matters because a closure test is much more convincing when the pseudo-data events are not the same events used to build the response sample.

### Step 3: build the pseudo-data truth and reco targets

From the pseudo-data half, the script builds:

- `hPseudoTruth`: the known truth target
- `hPseudoReco`: the reconstructed pseudo-data before unfolding

This is the key comparison:

- `hPseudoReco` tells you what detector smearing and inefficiency did.
- `hPseudoTruth` tells you what the unfolded answer should recover.

### Step 4: optionally stress the pseudo-data truth

The script supports several truth-level morphs applied **only** to the pseudo-data half:

- `nominal`
- `tilt`
- `bump`
- `tail`

This is how you separate two physics statements:

- `nominal closure` tests correctness of the implementation.
- `stressed closure` tests usefulness of unfolding under a controlled truth mismatch.

### Step 5: unfold the same pseudo-data with two methods

The script compares:

- `Reco-only` (no unfolding)
- `IBU` using `RooUnfoldBayes`
- `Unbinned OmniFold`

IBU is built from a standard `RooUnfoldResponse` filled from the train half.
Unbinned OmniFold is trained on the same train half and then compared to the pseudo-data truth target.

### Step 6: scan iteration counts

For each iteration in the requested list, the script computes:

- `integral_ratio = unfolded / truth`
- `mean_abs_frac_bias = mean(|U - T| / T)`
- `max_abs_frac_bias = max(|U - T| / T)`
- `pull_mean`
- `pull_rms`
- `chi2 / ndf`
- `prev_frac_change_rms = RMS(|U_n / U_{n-1} - 1|)`

This gives you both:

- a closure-quality curve, and
- a stability-with-iteration curve.

### Step 7: choose a recommended iteration

The script writes a markdown summary and, by default, chooses the iteration with the smallest `chi2/ndf`.
That is a reasonable first automatic rule, but you should still inspect the plots.

The real goal is not a magical single number.
The goal is to identify a **stable iteration region** where:

- closure has plateaued,
- pull widths are sensible,
- and increasing the iteration count no longer changes the answer much.

## What the outputs mean

The study writes four kinds of outputs into `Documents/ptmu_closure_study_outputs/`:

- `ptmu_closure_iteration_study.root`
  - closure histograms and per-iteration unfolding results
- `ptmu_closure_iteration_metrics.csv`
  - machine-readable metrics table
- `ptmu_closure_iteration_summary.md`
  - human-readable summary with recommended iterations
- `ptmu_closure_best_iteration.{png,pdf}` and `ptmu_closure_iteration_metrics.{png,pdf}`
  - quick-look plots for interpretation and writeup

## Recommended first commands

### Nominal closure

```bash
python3 Documents/ptmu_closure_iteration_study.py \
  --omnifile Documents/runEventLoopOmniFold.root \
  --datafile Documents/runEventLoopData.root \
  --datahist pTmu_data \
  --iterations 1,2,3,4,5,6,7,8 \
  --train-split even \
  --stress-mode nominal \
  --tag nominal
```

### Stressed closure with a localized bump

```bash
python3 Documents/ptmu_closure_iteration_study.py \
  --omnifile Documents/runEventLoopOmniFold.root \
  --datafile Documents/runEventLoopData.root \
  --datahist pTmu_data \
  --iterations 1,2,3,4,5,6,7,8 \
  --train-split even \
  --stress-mode bump \
  --bump-amplitude 0.35 \
  --tag bump
```

### Cross-check with swapped train/data halves

```bash
python3 Documents/ptmu_closure_iteration_study.py \
  --omnifile Documents/runEventLoopOmniFold.root \
  --datafile Documents/runEventLoopData.root \
  --datahist pTmu_data \
  --iterations 1,2,3,4,5,6,7,8 \
  --train-split odd \
  --stress-mode nominal \
  --tag nominal_swapped
```

## How to interpret the study

### What good nominal closure looks like

You want to see:

- `Reco-only` visibly displaced from truth in at least some bins
- `IBU` and `OmniFold` both closer to truth than reco-only
- `integral_ratio` near `1`
- `pull_mean` near `0`
- `pull_rms` near `1`
- `chi2/ndf` decreasing relative to reco-only and then stabilizing with iteration

### What good stressed closure looks like

You want to see:

- the pseudo-data truth distortion is not trivially identical to the train-half truth
- reco-only is biased with respect to the distorted truth
- unfolding corrects a meaningful fraction of that bias
- higher iteration counts eventually stop helping, or begin to fluctuate more strongly

That is the actual quantitative argument for usefulness.

## How to write this up

### Short correctness statement

You can write something like:

> We performed a split-sample closure test in which the OmniFold response was trained on one half of the signal MC sample and evaluated against the truth distribution of the complementary half. In the nominal closure test, both IBU and unbinned OmniFold reduced the reco-level bias, and the unfolded spectra remained stable over a finite range of iteration counts.

### Short usefulness statement

For a stressed closure:

> To quantify the usefulness of 1D unfolding beyond same-model closure, we applied controlled truth-level distortions to the pseudo-data half of the MC sample while keeping the response half unchanged. In this stressed closure test, the unfolded spectra recovered the distorted truth distribution substantially better than the reco-level spectrum, demonstrating that the unfolding corrects detector-induced bias rather than simply reproducing the nominal prior.

### Short iteration-choice statement

> We selected the nominal iteration count from the region where the closure metrics had plateaued, the pull widths were reasonable, and the change between successive iterations was small. This avoids both under-iterating, which leaves detector bias in place, and over-iterating, which amplifies fluctuations without improving closure.

## What figures and tables to include

A compact analysis note or paper section should usually include:

1. A closure comparison figure:
   - truth target
   - reco-only
   - IBU
   - OmniFold
   - ratio-to-truth panel
2. An iteration-scan summary figure:
   - `chi2/ndf`
   - mean absolute fractional bias
   - pull RMS
   - change relative to previous iteration
3. A table of per-iteration metrics
4. One nominal closure result and one stressed closure result

## Important caveats

- This implementation is intentionally **signal-only**.
  - That is not a weakness.
  - It is the cleanest way to quantify the unfolding itself.
- This implementation stays in **event-count units**.
  - That is also intentional.
  - Flux normalization and cross-section conversion should be added only after the unfolding behavior is understood.
- A future extension can add a full measured-side background-subtraction study, but that should be treated as a second layer after the signal-only closure is understood.

## Practical bottom line

If you want to make a convincing quantitative statement, do not stop at nominal closure.
Use this study in the following order:

1. `nominal` split-sample closure
2. `stressed` split-sample closure
3. iteration scan on both
4. choose a stable iteration window
5. write the conclusion in terms of bias reduction and iteration stability

That sequence is strong enough for a talk, an internal note, or the beginning of a paper section.
