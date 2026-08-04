# FINDING 2026-08-04 — RESTORE Step 2 resolved: the dump is GeV, and Gate-2's independent check has been vacuous since 2026-07-19

*Measured on Perlmutter against the real dump, 2026-08-04, after the restore. This is the
answer Step 2 asked for. **No code was patched and no receipt was touched** — the fix requires
deliberately re-running Gate-2 and re-issuing its receipt, which is a user decision.*

## The answer: GeV

`RESTORE-2026-08-03.md` Step 2 gave the discriminator as *"p∥ max ~O(100) ⇒ GeV, the `/1000.0`
is WRONG. ~O(1e5) ⇒ MeV, keep it."* Measured, on `G2_FPS_MEFHC_P12.npz`:

| array | column | min | median | p99 | max |
|---|---|---|---|---|---|
| `measured_scalars` (4,116,128 × 4, float32) | `pt` | 0.0005 | 0.6623 | 3.0739 | **29.9998** |
| | `p∥` | 1.0369 | 5.1080 | 36.3159 | **119.8773** |
| `bkg_reco_scalars` (564,591 × 4) | `pt` | 0.0017 | 0.7512 | 5.0209 | 29.9215 |
| | `p∥` | 1.1223 | 5.3125 | 42.0585 | 119.9762 |

Zero non-finite values in either. `p∥` max is 119.88 and `pt` max is 30.0 — both sitting exactly
on the canonical grid's top edge. **The dump is in GeV**, so
`gate2_target_runtime.py:492-493` dividing by `1000.0` is wrong.

The grid confirms it independently, and it ships *inside the dump*: `edges_0` runs
`[0, 0.07, 0.15, 0.25, … 1.5, 2.5, 4.5, 30.0]` and `edges_1` runs `[0, 0.75, 1.5, 2, … 20, 40,
60, 120]`, identical to `fed.CANONICAL_PT_EDGES` / `CANONICAL_PPARALLEL_EDGES` — which the
loader's own comment sources to "the 2026-07-16 measurement-domain contract."

## Scope — narrower than feared, and this is the part to get right

**The `/1000.0` appears nowhere except `gate2_target_runtime.py:492-493.`** Swept both files:
`fullevent_fps_dataloader.py` does not scale `measured_scalars` or `bkg_reco_scalars` anywhere
(it consumes them raw at 1151-1157, 1284-1304). Its only mention of a thousandth is a comment at
line 78 explicitly *rejecting* one for a different array: *"Recoil-token hit time is dumped in ns
over a window of order ±50; /1000 would push it to 1e-2."*

So:

* **No trained product is misscaled.** The estimator path reads GeV and histograms against GeV
  edges. P5A, the closures, and the extractor are unaffected by this.
* **What is broken is the certification.** The gate's own independent re-derivation — the thing
  whose entire purpose is to catch a loader defect by computing the histogram a second way — has
  been comparing degenerate histograms since the 2026-07-19 receipt.

That is the audit-B2 family again: not a wrong number, but a check that cannot fail.

## The damage, measured

Binning `measured_scalars` against the canonical grid both ways:

| | rows binned | occupied bins | lowest bin |
|---|---|---|---|
| as-is (GeV) | 4,116,128 | **231 / 285** | 0 (0.00%) |
| `/1000.0` | 4,116,128 | **1 / 285** | 4,116,128 (**100.00%**) |

The divide collapses the entire two-dimensional distribution into a single bin.

## Why neither guard catches it

Both mechanisms are defeated for different reasons, which is why this survived a PASS:

1. **The domain guard tests range membership, not distribution.** `gate2_target_runtime.py:513-516`
   dies only when `in_domain_data != measured.shape[0]`. Both canonical grids start at **0.0**, so
   GeV/1000 values (~5e-4 to 0.12) are still inside `[0,30] × [0,120]`. Membership is perfectly
   preserved; only the distribution is destroyed. Measured: 100.000% retained either way, so the
   guard reports success in both worlds.
2. **The comparison metrics divide both sides identically.** `measured` and `background` are each
   scaled by the same `1000.0` at 492-493, so `rel_l1` / `max_rel` / `cosine` compare two
   identically-wrong histograms and agree. This is why the failure is symmetric across the two
   histograms, exactly as the runbook predicted.

Worth noting the code contradicts its own comment. Three lines above the division:
*"Independent binned checks use **raw** input scalars…"* — and then it scales them.

## Remediation — Step 2, and not done here

`gate2_target_runtime.py` is bound by
`nd-unfolding/g2_fullevent/gate2/final/G2_GATE2_TARGET_RUNTIME_RECEIPT.json`, and editing it
voids the loader's binding too, because the receipt that froze the loader is no longer the receipt
that passed. So the patch means **deliberately re-running Gate-2 and re-issuing the receipt —
never hand-editing a hash.** That also closes the five mismatch sites Step 0 reports, which Step 2
already owns.

Two things to add while the receipt is open, because the current guards demonstrably cannot catch
this class:

1. **Cross-check the module's edges against the dump's own `edges_0`/`edges_1`.** They ship in
   every dump and matched here. A gate that histograms against `fed.CANONICAL_*` without ever
   comparing them to the arrays travelling with the data has two sources of truth and checks
   neither against the other.
2. **Add an occupancy floor, not just a membership test.** `231/285` occupied versus `1/285` is
   the signal that was available and unused. Any assertion of the form "more than one bin is
   occupied" — or better, a comparison to the construction telemetry's own occupied-bin count —
   would have failed loudly in 2026-07-19 instead of passing.

## Provenance

Found by running Step 2's own prescribed diagnostic on the real dump for the first time, which was
impossible during the 07-22→08-03 outage. The runbook had correctly predicted both the
discriminator and the failure mode ("the gate passes while being wrong") from a 2026-07-26
known-units experiment; this confirms it against the production input and adds the mechanism —
that both grids beginning at 0.0 is what makes the domain guard blind.
