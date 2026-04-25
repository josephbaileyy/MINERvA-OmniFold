# Binned OmniFold pTmu debug matrix — advisor notes (2026-03-26)

## Background

The unbinned OmniFold unfolding for MINERvA pTmu works correctly and produces
physics-quality results that agree well with the MINERvA IBU baseline extraction.
That pipeline is frozen and ready for the writeup.

The **binned** OmniFold path, however, has a persistent normalization failure: when
we unfold the background-subtracted data spectrum through the binned
RooUnfoldOmnifold machinery, the unfolded result comes out roughly **5x too low**
in total yield. This has been observed across multiple earlier attempts but was
never systematically isolated.

Today's study sets up a rigorous one-factor-at-a-time debug matrix to determine
whether the failure is caused by MC event weights, the choice of unfolding engine,
or the response-matrix weight convention — or whether it is structural to the
binned algorithm itself.

## What was tested

Starting from the Playlist 1A MINERvA Open Data inputs
(`runEventLoopOmniFold.root`), we ran the binned unfolding script four times, each
time changing exactly one factor from the nominal configuration:

| # | Run label | What changed | Config |
|---|-----------|-------------|--------|
| 0 | `nominal-weighted-repro` | *(baseline)* | 5 iters, wrapper engine, truth response-weight, `--use-weights` |
| 1 | `unweighted-wrapper` | Disabled MC event weights | same as #0 but no `--use-weights` |
| 2 | `weighted-helper` | Switched engine | same as #0 but `--engine helper` (Python `binned_omnifold()` + efficiency correction) |
| 3 | `weighted-legacy-mixed` | Changed response weight convention | same as #0 but `--response-weight-mode legacy-mixed` (Fill/Fake use w_reco, Miss uses w_truth) |

All four runs used the same input files, the same reference binning (from the
baseline data histogram), the same POT scaling (data/MC = 0.2205), and 5 OmniFold
iterations.

## Results

The two key diagnostic ratios are:

- **data-bkg / response.Hmeasured**: measures how well the response matrix's
  reco-side projection matches the background-subtracted data. Values near 1.0 mean
  the inputs are well-matched; deviations indicate the response doesn't fully cover
  the measured spectrum.

- **data-bkg / unfolded**: measures the overall normalization of the unfolded
  result. A correct unfolding should give a value near 1.0 (unfolded total yield
  matches the measured-minus-background total).

| Run | data-bkg / resp.Hmeas | data-bkg / unfolded | Unfolded integral |
|-----|-----------------------|---------------------|-------------------|
| Nominal weighted | 1.126 | **5.23** | 85,786 |
| Unweighted | 0.938 | **12.0** | 37,410 |
| Helper engine | 1.126 | **5.23** | 85,786 |
| Legacy-mixed | 1.152 | **10.6** | 42,559 |

For reference, the target (data - background) in-range integral is **449,024 events**.

## What this tells us

### 1. The failure is engine-independent

The RooUnfoldOmnifold C++ wrapper and the standalone Python `binned_omnifold()`
helper produce **identical** unfolded integrals (85,786) and identical
normalization ratios (5.23x). This rules out a bug specific to either code path —
both implementations of the binned OmniFold algorithm behave the same way.

### 2. MC event weights are not the cause (and actually help)

Disabling event weights makes the under-normalization **worse** (12x instead of
5.2x). The weights partially compensate for whatever is going wrong. This means
the failure is not caused by pathological weight values, weight clipping, or
weight-handling bugs. (We also confirmed: zero bad weights, zero skipped weights
in all runs.)

### 3. Response weight conventions matter but don't fix the problem

The legacy-mixed mode (using reco-side weights for Fill/Fake, truth-side for Miss)
introduces a 2% internal inconsistency in the response truth projection and makes
the failure worse (10.5x). The truth-only mode is the most self-consistent choice,
but it still fails at 5.2x. No weight convention fixes the collapse.

### 4. The ~11% input-side mismatch is expected and not the root cause

The data-bkg integral (449,024) exceeds the response's reco-side projection
(398,745) by about 11%. This is expected: the response is built from
POT-scaled MC signal, which doesn't perfectly match data after background
subtraction. A well-functioning unfolding algorithm should handle this mismatch
gracefully. The 5x collapse during iteration is far beyond what this input
mismatch could explain.

### 5. The problem is structural to binned OmniFold iteration

Since the failure persists across both engines, with and without weights, and
across response-weight conventions, the root cause is in **how the binned OmniFold
algorithm's iterative reweighting interacts with the histogram representation**.

The unbinned path works because OmniFold was designed for per-event reweighting
with ML classifiers. The binned path replaces that with histogram ratio
reweighting, and something about how those ratios compound across iterations
causes the total yield to collapse.

## Practical implications

- The **unbinned OmniFold pipeline remains the correct production path** for the
  MINERvA pTmu cross-section result.
- The binned path should not be used for physics results in its current form.
- Understanding *why* binned iteration collapses the normalization may still be
  valuable for the field (other experiments may encounter similar issues if they
  try binned OmniFold on data with non-trivial efficiency and background).

## Recommended next steps

1. **Iteration scan**: run the nominal weighted config for iterations 1 through 8
   and plot the unfolded integral vs iteration number. This will show whether the
   normalization monotonically shrinks, oscillates, or converges to the wrong
   fixed point.

2. **Binned closure test**: use MC truth as pseudo-data with no background
   subtraction, so the response and target are perfectly self-consistent. If the
   closure test also fails, the binned algorithm is fundamentally unable to
   preserve normalization even in the ideal case. If it passes, the failure is
   driven by the data/response mismatch being amplified by iteration.

3. **Algorithm trace**: step through `binned_omnifold()` iteration-by-iteration,
   printing the reweight factors and intermediate histograms, to identify exactly
   where the yield is lost.

## File locations

All run outputs are archived under `Documents/binned_study/runs/`:

```
runs/2026-03-26_nominal-weighted-repro/   # baseline reproduction
runs/2026-03-26_unweighted-wrapper/       # weights disabled
runs/2026-03-26_weighted-helper/          # helper engine
runs/2026-03-26_weighted-legacy-mixed/    # legacy-mixed response weights
```

Each directory contains `command.txt`, `stdout.log`, `summary.md`, and
`outputs/omnifold_ptmu_unfold.root`.
