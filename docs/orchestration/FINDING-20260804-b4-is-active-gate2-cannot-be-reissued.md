# FINDING 2026-08-04 — B-4 is **ACTIVE**. The first real post-restore Gate-2 run answered it, and Gate-2 cannot be re-issued until it is resolved.

*Measured on Perlmutter 2026-08-04, job 56320955, 56 minutes on `nid004156`. This is the answer the
code was written to extract, not a failure of the run. **Nothing was published; the 2026-07-19
products are byte-identical to how they were found.***

> **DECIDED 2026-08-04; implementation pending.** Step 1 will use `w_reco`; Step 2 and
> truth-space yields will use `w_truth`. The single PET `mc.weight` must be split by leg rather
> than globally replaced. Canonical rationale and the re-issue transaction are in
> [`DECISION-20260804-B4-STEP3-RECEIPTS.md`](DECISION-20260804-B4-STEP3-RECEIPTS.md#d1--b-4-use-the-weight-belonging-to-each-omnifold-leg).
> This finding remains the canonical measurement evidence; it is not a repair or receipt.

## The result

```
RuntimeError: B-4 is ACTIVE: w_reco differs from w_truth on 20573521 pass_reco rows,
so the reco leg is fed the wrong weight and R would move by a factor 1.01887079577071
```

* **All 20,573,521 `pass_reco` rows differ** — every single one, not a subset. So `w_reco` and
  `w_truth` are systematically different quantities over the whole reco leg, not a handful of edge
  cases. (20,573,521 is independently the `pass_reco` count measured for Step 7b, which
  corroborates the row accounting.)
* `reco_leg_weight_used` is `"w_truth"` (`fullevent_fps_dataloader.py:955`) — the reco leg is
  currently fed the truth weight.
* `R_shift_factor_if_B4_fixed = 1.01887079577071`. R appears with `sum_w_mc_reco_raw` in its
  denominator, and the `w_reco` sum is smaller by that factor, so **R moves by ≈ +1.9%** if the
  reco leg is switched to `w_reco`.
* The step-1 target is `1e6 · R`, so a 1.9% move in R is a 1.9% move in the publication nominal's
  step-1 normalization.

## The 20.5M-row difference is a calibration, not corruption — measured 2026-08-04

"Every single row differs" has two readings: a systematic reco-vs-truth calibration, or a corrupted
/ mis-joined weight array. D1 rests on the first. Its published rationale cites
`MINERvA101/opt/include/PlotUtils/MINOSEfficiencyReweighter.h:30` for the mechanism, but **that
path does not exist in this repository** — only the `#include` at
`runEventLoopOmniFold.cpp:70` and the `MnvTunev1.emplace_back(... MINOSEfficiencyReweighter ...)`
at `:1749` are here. So the mechanism claim is not checkable from this tree. The *substance* is,
and was measured directly off the dump rather than argued:

| quantity | measured |
|---|---|
| `pass_reco` rows | 20,573,521 |
| `w_truth` ≤ 0, `w_reco` < 0, or either zero | **0** |
| rows with `w_reco == w_truth` | **0** |
| ratio `w_reco/w_truth` | min **0.931130**, median 0.985569, max **0.997680** |
| `sum(w_truth)/sum(w_reco)` over `pass_reco` | **1.01887079577071** |

Two things follow.

1. **The sum ratio reproduces `R_shift_factor_if_B4_fixed` to all 12 printed digits**, by a
   different code path (direct npz read, no validator). The measurement above is independently
   confirmed.
2. **The ratio is strictly sub-unity and saturating in muon momentum** — mean ratio 0.943868 in
   the lowest `p_mu` bin (1.10–1.98 GeV), rising monotonically, then flat at 0.987518–0.987519 from
   `p_mu ≈ 6.2` GeV to the 123.5 GeV endpoint. A bounded, positive, few-percent factor that dies
   away at low momentum and plateaus at high momentum is the shape of an **efficiency correction**,
   not of a corrupted array. Corruption does not respect a monotone momentum profile.

This repo independently characterises the reweighter the same way, from a June audit that had no
stake in B-4 — `2d-unfolding/2D_OMNIFOLD_REFERENCE.md:301` (KNOWN_ISSUES #5, 2026-06-10):

> the `MINOSEfficiencyReweighter` (**intensity-dependent** data/MC matching efficiency, **few-%**)
> IS already applied in our MnvTune stack

"few-%" is the measured 1.9% mean and 0.93–1.00 range. That is corroboration from inside the tree,
so D1's conclusion does **not** depend on the missing header.

**Stated limit, because the stronger version of the claim failed.** If the MINOS efficiency were
the *only* reweighter differing between modes, the ratio would be a pure function of `p_mu` and
would collapse to zero spread within momentum bins. It does not: over 60 equal-count `p_mu` bins
the worst within-bin relative spread is **1.27e-2**, with 10,260,305 distinct ratio values. So
"among the five CV reweighters, the difference is the MINOS efficiency correction" is **supported
in magnitude and shape but not established as exclusive.** The documented *intensity* dependence
would produce exactly this residual — intensity is not held fixed by a `p_mu` binning, and the dump
carries no per-signal-event intensity field (only `bkg_current`) to bin on, so the two-variable
test cannot be run here. Nothing in D1 needs exclusivity; it needs the correction to belong to the
detector leg, which the momentum profile establishes.

*Method: `w_reco`, `w_truth`, `pass_reco`, `reco_scalars` read directly from
`G2_FPS_MEFHC_P12.npz`; `p_mu = sqrt(pt² + pz²)` from `reco_scalars[:,0:2]`; 60 quantile bins,
bins with <100 rows dropped. No ROOT, no validator, no TF.*

## This was designed to happen on exactly this run

`fullevent_fps_dataloader.py:832-846` says so in terms:

> `THE w_truth-vs-w_reco ASSUMPTION -- audit finding B-4, UNRESOLVED as of 2026-07-29.` … `That is
> why R is DERIVED here and never frozen as a constant: when B-4 is answered, this one` … `the
> w_reco-vs-w_truth comparison at runtime, so the first 08-03 run answers B-4 as a side effect.`

And `2026-07-31` converted B-4 from a note into a hard gate — `gate2_target_runtime.py` around the
B-4 block records why:

> B-4 is GATED here, not merely recorded. … Emitting that into `step1_class_ratio.b4_note` while
> the receipt says status PASS made the gate contradict its own telemetry, because every consumer
> reads `status`, not a note.

So the restore's first Gate-2 run did precisely its job. The gate that previously passed while
recording "resolve B-4 before freezing R" in a note now stops.

## What this says about the published 2026-07-19 PASS

The published receipt `G2_GATE2_TARGET_RUNTIME_RECEIPT.json` carries `status: PASS` and verdict
`GATE2_CANONICAL_RUNTIME_PASS_INDEPENDENT_PROMOTION_PENDING`. It was produced **before** B-4 was
gated, so its PASS was obtained under a validator that only wrote B-4 into a note whose own text
said not to freeze R yet. That PASS therefore does not certify the current definition of the gate.

This compounds with the units defect resolved the same day
([FINDING-20260804-gate2-units-resolved-gev](FINDING-20260804-gate2-units-resolved-gev.md)): the
same receipt's "independent binned check" was also vacuous. Two independent reasons the 07-19 PASS
should not be leaned on.

## The units patch is separately confirmed CORRECT by this run

Worth stating because it is easy to lose in the failure: the run got **past** the units fix, the
domain guard, the step-1 sum check, the signed-sum-vs-telemetry check and the R-numerator
corroboration, and died only at B-4.

That is positive evidence, not merely absence of complaint. With `/1000.0` removed, if the dump
were MeV the values would sit at ~1e4–1e5, far outside `[0,30] × [0,120]`, and the domain guard at
`:515` would have died loudly on the very next statement. It did not. **The dump is GeV and
removing the divide is right**, now established against the real input by the gate's own guard
rather than by inspecting maxima.

What the run did *not* reach: the receipt write, so the occupied-bin count (expected 231/285 vs the
old degenerate 1/285) and the weights-vs-published comparison are still unmeasured.

## Why I stopped here

Resolving B-4 meant deciding whether the reco leg should be fed `w_reco` instead of `w_truth`.
That decision has now been made in the record linked above. No implementation or gate re-issue
was performed as part of recording it.

## Consequences for the restore chain

Gate-2 is now blocked by B-4, and Step 3 is independently blocked by an environment conflict
([FINDING-20260804-step3-closure-needs-root-and-tf-in-one-interpreter](FINDING-20260804-step3-closure-needs-root-and-tf-in-one-interpreter.md)):

```
D1 implementation pending -> Gate-2 re-issue blocked
D2 implementation pending -> Step 2b blocked -> Step 4 precondition unreachable
```

Step 4's unattended-launch authorisation was conditional on every gate passing. Two independent
walls mean that condition is not met, so **not launching is the correct execution of that
authorisation.**

## State of the published artifacts — unchanged

Verified before and after the run:

| artifact | sha256 | bytes |
|---|---|---|
| `G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy` | `1ef7e0d2fa8c36a6f9eabd86a21f0b41617cc7d0bb4cd6bee96d74d5334074b6` | 18,723,004 |
| `G2_GATE2_TARGET_RUNTIME_RECEIPT.json` | `f09db8fc4b2aa177d188f456bd53fccc0e965f1ea319e0764c355051e92f8c44` | — |

No pin was edited and no product was retired. `test_no_new_broken_hash_bindings` remains red, which
is still correct behaviour.

**Mismatch accounting, reconciled 2026-08-04 after D3.** This run left five mismatches; the
verifier now reports **four**, all owned by still-live Gate-2 sources (two from
`G2_GATE2_TARGET_RUNTIME_RECEIPT.json`, two from `run_gate2_target_validator.sh`'s
`EXPECTED_*_SHA` guards), and all four resolve when Gate-2 re-runs. The fifth was
`test_fullevent_fps.py`, retired by D3's supersession. Note the construction receipt's other two
bindings were never separately counted: `test_fullevent_gate2.py` still **matches** its at-issue
digest, and its loader pin carried the same `want` as the runtime receipt's, so
`verify_hash_bindings.py:186` deduped them (`key = (rel, want, src if src.endswith(".sh") else "")`
collapses non-shell sources). D3 was right to move the whole three-file block regardless — a live
`files` block on a superseded receipt is what `test_superseded_receipts_hold_no_live_bindings`
forbids — but "two mismatches retired" was one; only one was ever counted.

## Cost

56 minutes on one shared CPU node (~15 CPU-hours). Note the refiner ran roughly 5× slower than the
07-19 run's 671 s — single-threaded at ~95% of one core, RSS 3.8 GB against that run's 11.1 GB
peak. Worth setting thread counts explicitly before the next attempt rather than inheriting them.
