# PREDECLARATION — the annealed production nominal must REPRODUCE the annealed arm

**Committed BEFORE the job is submitted.** Confirmation, not permission: ~6 GPU-h is inside the standing
under-12-h rule. Authorized by Joseph 2026-08-10 with the reproduction test as a precondition.

## Why a reproduction test is required rather than assumed

The measured annealed behaviour came from a **`MultiFold` subclass inside a diagnostic script**
(`diagnose_step1_annealed_lr.py`, job `56534117`). Production is the **driver**
(`train_fullevent_nominal.py`), which now carries its own subclass. **Those are two different code paths
to the same intended policy**, and "they agree" is a claim, not a fact. Joseph's point exactly: it has to
be checked.

## SCOPE CORRECTION — recovery is NOT reproducible by this run, and predeclaring it would be vacuous

Joseph's instruction named both the fold-forward deviation (~−1.17%) and the recovery (~0.5126). Checked
before committing:

- **`train_fullevent_nominal.py` contains ZERO mentions of `recovery`.** Recovery is a *closure* quantity —
  `1 − Σ|unfolded−target| / Σ|prior−target|` over an A/B split with an **injected truth tilt** — computed by
  `closure_powered_truth_reweight.py`. A nominal training run has no injection and no A/B halves, so it
  cannot produce it.
- The two numbers come from **different jobs**: fold-forward `−1.17%` from `56534117` (`fe_s1lr2`),
  recovery `0.5126033` from `56552326` (`ann_shape`, the powered closure).

So this predeclaration covers **fold-forward only**. Reproducing recovery under the production path would be
a *second* run — the powered closure invoked through the production driver rather than the diagnostic
wrapper — and is **not** authorized or launched here. Flagged now rather than silently dropped, because a
predeclaration listing a quantity the run cannot emit is worse than one that says why.

## THE TEST, fixed in advance

    quantity   fold-forward deviation  dev = (sum_w_push_reco / sum_w_reco) / R - 1
    expected   -0.011724               (annealed arm 56534117: push 1.1109012166615733, R 1.1240802949941018)
    BAND       +/- 0.010 absolute      ->  PASS window  [-0.021724, -0.001724]

### Why ±0.010, justified rather than picked

- The **only** measured run-to-run scatter available is the 2026-08-08 matched nominal/floor pair at
  identical seeds: push `0.7367462501305516` vs `0.740546`, i.e. `0.003800` absolute, which is `0.003380`
  in deviation. One pair gives a scale, not a distribution.
- `±0.010` is **~3× that scatter**, which is the widest I can justify from a single pair without pretending
  to know the tail.
- It is still sharply discriminating: the non-annealed baseline sits at `−0.3446`, which is **33 band-widths
  away**. So the band cannot confuse "annealed" with "not annealed".
- And it stays comfortably inside FROZEN's `fold_forward_ratio_dev_max = 0.05`, so a PASS here is also a
  pass of the normalization gate rather than a separate standard.

## THE READING, and a disagreement is a FINDING

| outcome | reading |
|---|---|
| dev inside `[-0.021724, -0.001724]` | **REPRODUCED.** The driver's code path and the diagnostic's agree. |
| dev outside the band but `|dev| < 0.05` | **FINDING — the two code paths disagree.** The anneal happened (see the discriminator below) but production and diagnostic do not produce the same estimator. Report it; do **not** average it, re-run past it, or widen the band. |
| dev ≈ `−0.34` | **FINDING — the anneal did not take effect in production**, despite the driver's own assertion. Escalate immediately: this would mean the assertion is defective. |

**Explicitly forbidden by this predeclaration:** averaging two runs, re-running until one lands in the band,
or widening the band after seeing the number. A second run is only for measuring the scatter, and then both
values are reported.

## The discriminator is what separates the two failure modes

If `dev` disagrees, `seed_policy.lr_policy` + `lr_policy_realized` answer *whether the anneal happened*:

- realized rates present, optimizer-verified, matching `1e-4 / 1e-5` → **the anneal happened**, so a
  disagreement is a code-path difference and not a policy failure.
- realized rates absent or contradicting → **the artifact should not exist at all**: the driver refuses to
  write on mismatch, so its presence would itself be a finding about the assertion.

That is the discriminator built on 2026-08-10 doing the job it was built for, on its first real use.

## Governance

- Nothing else authorized: **no extraction, no cross section, no promotion of any other arm**, no threshold
  change, Branch C stays closed.
- `niter` unchanged at 3.
- A `wakerctl` watch is armed at submission (currently zero armed).
- The reproduction is reported against this document **before anything downstream**.

## Provenance

- expected dev, push `1.1109012166615733` — job `56534117`
- `R = 1.1240802949941018` — `target.step1_class_ratio`, the artifact's own
- scatter pair `0.7367462501305516` / `0.740546` — job `56445883` nominal + matched floor repeat
- `fold_forward_ratio_dev_max = 0.05` — `validate_pet_nominal_gate4.FROZEN["tolerances"]`
