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

---

## RESULT — 2026-08-10, job `56563761` COMPLETED 06:00:36, exit `0:0`

**Verdict: FINDING — the two code paths disagree.** Row 2 of the reading table above, fixed before the run.

    arm                       push             dev            vs window [-0.021724, -0.001724]
    production nominal        1.0840529523     -0.035608971    OUTSIDE (by 0.013885)
    production floor          1.0841954573     -0.035482196    OUTSIDE (by 0.013758)
    diagnostic 56534117       1.1109012167     -0.011724321    (the expectation)
    non-annealed baseline     0.7367462501     -0.344578627    (33 band-widths away, as predicted)

**The scatter measurement — the point of running both arms — is decisive.**

    MEASURED annealed scatter |dev_nominal - dev_floor| = 0.000126775
    gap to expectation                                  = 0.023884650   = 188.4x the scatter
    predeclared band 0.010                              = 79x WIDER than the real spread
    annealed scatter vs the 08-08 non-annealed pair     = 26.7x TIGHTER

So the §"Why ±0.010" reasoning was **conservative in the safe direction and wrong in magnitude**: it
scaled from a *non-annealed* pair because that was the only measurement available, and the annealed
configuration is 26.7× more reproducible than that. Had the band been scaled correctly the finding would
have fired at 188σ-equivalent rather than 2.39 band-widths. **The band being too loose is the reason this
result is safe to believe** — a too-tight band is what would have made it suspect.

**The discriminator did its job on its first production use.** `lr_policy_realized` in both arms:
`n_fits_base_lr 2, n_fits_annealed 4, verified_from_optimizer True`, realized rate lists byte-identical.
So the anneal **happened**, and row 3 of the table is excluded. Without that field rows 2 and 3 would be
indistinguishable — which is the argument for making the assertion a precondition rather than a follow-up.

**The alternative explanation was tested and refuted.** Before reporting a code-path defect I checked
whether the two numbers are even the same estimator — the BEN-077 failure mode, and the one hypothesis that
would dissolve this finding into my own error of expectation. Five candidate definitions computed on the
production artifact against the diagnostic's `1.1109012167`: none within `0.026`; the closest is the
ratio-of-sums production already reports; the unweighted mean is off by `0.183`. Same estimator, real
difference. Recorded so that nobody re-opens it as a units question.

**Scope honoured:** the recovery quantity this document explicitly declined to predeclare was not computed,
claimed, or implied. Baseline `58f664cdef266d09` verified UNCHANGED before and after. No promotion, no
threshold touched, no extraction, no cross section, Branch C closed, `niter` = 3.

Detail and the ruled-out mechanisms: `KNOWN_ISSUES.md`, *"Two code paths implementing the same LR anneal
produce different estimators"*.

## PROVENANCE NOTE on the `niter` line in Governance, added 2026-08-10

The governance section above says *"`niter` unchanged at 3."* Stating precisely what backs that, because the
oversight lane audited the claim *"`niter` is Joseph's pin"* — which **I** had asserted to it — and could not
verify it. It was right not to be able to:

- **What the artifacts support.** `niter=3` is pinned in `NOMINAL_SEED_POLICY` (`train_fullevent_nominal.py`),
  in `validate_pet_nominal_gate4.py`, and in this document's governance section; the 2026-08-06 handoff records
  it as settled. **CLM-010 states the origin explicitly: "the stopping point at `k=3` is set by cost and the
  literature default, NOT chosen by measurement"** — and records that measurement actually prefers `k=4`,
  deliberately overridden.
- **What backs the *unchanged* constraint** is a line in Joseph's adoption directive to this session. That is
  first-hand, but it was **never written into the run log as an attributed instruction**, so no one else can
  check it, and I should not have relayed it as *"pinned by Joseph explicitly."*
- **The defensible form:** pinned in code, in the gate, and in this document's governance; recorded as settled
  in the 08-06 handoff; and carried as a constraint in the adoption directive.

**No conclusion changes.** `niter` stays at 3 — it is pinned in code regardless of who pinned it, and the
oversight lane's ceiling re-derivation (a `k=1` configuration would need 121% of its own ceiling to match
production's `0.5126033`, against a 103% largest-ever measured overshoot) argues for 3 independently of
provenance. This is a citation correction, not a decision.

Recorded here rather than only in the log because this document is what a reader consults for what was
authorized, and an unsourced attribution in a governance section is exactly the thing that gets quoted back.
