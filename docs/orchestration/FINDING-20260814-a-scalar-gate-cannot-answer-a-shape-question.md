# FINDING 2026-08-14 — a gate that reduces to a scalar fixes forever which failures its record can express

**BEN-252.** Lane D (verifier), from the VL100 fold-forward falsification test. Receipt:
[`state/vl100-foldforward-shape-test-20260814.json`](state/vl100-foldforward-shape-test-20260814.json).

## The situation

A number quoted in front of a decision — `VL100 = 0.512603276`, the injected-reweight recovery
Joseph's arm choice rests on — was defended on the grounds that it is computed on **unit-normalized**
spectra, so the ~34% fold-forward normalization deficit divides out. **That defence holds if and only
if the deficit is a pure overall scale.**

The obvious place to check is the gate that measures the deficit,
`pet_diagnostic_quarantine.measured_fold_forward_dev`. It reads two fields from the artifact:

```python
num = _npz_scalar(z, "fold_forward_sum_w_push_reco")   # scalar
den = _npz_scalar(z, "fold_forward_sum_w_reco")        # scalar
dev = abs((num / den) / R - 1.0)
```

**Both are sums over the entire reco leg.** The shape information is integrated away *before the
recorded number exists.* So the gate's field is not imprecise about scale-versus-shape — it is
**structurally silent**. No care in reading it, and no improvement in its precision, could ever
distinguish the two.

> **Check:** a gate that reduces its evidence to a scalar has fixed, permanently, the set of
> questions its record can answer. At design time, ask **which failure modes the recorded quantity
> is capable of expressing** — not just whether the threshold is right. A tolerance on an integrated
> quantity cannot detect a redistribution that leaves the integral unchanged.

## Why the question was answerable anyway, and it was luck

The per-event operands happened to survive in the same artifact — `weights_push` (2,000,000,) and
`mc_indices` — so the recorded scalars could be **decomposed** per cell using the producer's own
definition (`train_fullevent_nominal.py:576-577`):

```
ratio[c] = sum_c(w_reco * push) / sum_c(w_reco)      the w_reco-weighted mean push in cell c
```

A pure scale deficit makes that constant. Measured on the 285-cell grid VL100 lives on: it runs
**0.173 to 1.420**, relative sd **47.0%**, against a sampling-noise expectation of **0.69%** —
**68.4x** the noise. Corroborated on the reco grid at 36.3x. The variation is dominated by
`p_parallel` (marginal 0.272 → 1.321, a factor of 4.9), not pT.

**Had the artifact stored only the two sums, the question would have been unanswerable from disk
and would have required a re-run.** That is the part worth designing for: the gate's scalar is what
gets checked, but the operands are what let a *later, unanticipated* question be answered at all.

## The near-miss that makes the answer trustworthy

The trainer does not use the NPZ's raw `w_reco`; it uses the loader's `mc.weight_reco`
(`:564-565`). The first decomposition was therefore **31.6% off on both sums**, and the probe's
control refused to report — correctly, because it was not decomposing the gate's quantity.

The per-cell ratios need only that the two weights differ by a **global scale**, under which
`num/den` per cell is invariant. **That was tested rather than assumed:** `k` was fixed from the
**denominator alone** (1.462888717614880), and the **numerator** then had to reproduce under that
same `k`. It did, to a residual of **2.0e-13**.

This is not a tautology, and the reason matters: **the numerator weights each event by `push` and
the denominator does not**, so a per-event discrepancy would break one and not the other. Without
that step the result would have been a plausible number resting on an unexamined premise — which is
the exact shape of the thing the test was commissioned to look for.

## A gap in this finding's own receipt, caught by the convention

The first receipt published the per-cell ratio array but **not `n_eff`**, while its summary
statistics were reduced over cells with `n_eff >= 50`. The mediator recomputed from the published
array and got a different mean (0.800 vs 0.717) and max (1.533 vs 1.420) — **correctly**, because
the reduction was not derivable from what had been shipped.

Fixed by publishing `per_cell_n_eff` and `per_cell_in_summary` alongside, plus the naive all-live
reduction, so both are on the record and the verdict is visibly robust to either (44.97% vs 47.02%
relative sd, both against sub-1% noise). **`BEN-077` working exactly as intended: the summary was
contradicted from its own operands, which is only possible because the operands were shipped.**

## Family

- `BEN-250` — a *check* whose strongest statement could not fail.
- `BEN-251` — *operations* that could not report.
- **`BEN-252`** — a *recorded quantity* that cannot express the failure mode it is later asked about.

All three are the same defect at different points in the chain: **the artifact everyone consults is
disconnected from the property it appears to speak to.** `BEN-250`'s check ran and said nothing;
`BEN-251`'s operations returned and said nothing; here the field is read correctly, is accurate, and
still says nothing about the question — because the question was integrated out before the number
was written.
