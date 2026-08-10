# PREDECLARATION — D2 powered closure on the annealed-LR configuration (shape validation)

**Written and committed BEFORE the run.** Authorized by Joseph 2026-08-09/10
(`authorize_annealed_shape_validation`, option b). Purpose: settle whether the annealed learning rate
buys its normalization repair at the cost of shape recovery.

## The risk being tested, stated as a mechanism

The dead LR anneal (`KNOWN_ISSUES`, 2026-08-09) means every fit trains at full `self.LR = 1e-4`.
Restoring the intended anneal (`1e-4` for iteration 0, then `1e-5`) took the fold-forward deficit from
**−34.46% to −1.17%** (arm `warm_fixed_annealed_lr`, job `56534117`). The obvious worry is that it does so
by **under-updating**: a 10× smaller learning rate after iteration 0 moves the classifier less, which
would keep the normalization near its already-good iteration-1 value while failing to transport the
*shape* information that later iterations exist to add. Normalization would improve precisely because
less is happening.

The D2 powered closure measures exactly that. It injects a known truth-level tilt on one half of a
disjoint A/B split and asks how much of the induced spectrum displacement the estimator recovers —
`recovery = 1 − Σ_b|unfolded_b − target_b| / Σ_b|prior_b − target_b|`. It is a **shape** measure, over
cells, and it is insensitive to a pure normalization fix by construction (the criterion's own docstring
records that this is why it was chosen).

## The criterion — ADOPTED, UNCHANGED, NOT TOUCHED

    recovery >= f * ceiling = 0.80 * 0.618228 = 0.494582

This is the CLM-012 criterion adopted 2026-08-09. **No threshold is modified by this run.** The frozen
contract is read, not written.

**Baseline for comparison:** the nominal (warm model / fixed split, full-LR) powered closure measured
**recovery = 0.546853**, margin +0.052271 over the threshold.

## THE READING, FIXED IN ADVANCE

Let `rec_ann` be the annealed configuration's recovery, `rec_base = 0.546853`.

| Outcome | Reading |
|---|---|
| `rec_ann > rec_base + 0.02` | **REAL REPAIR.** The anneal fixes normalization *and* improves shape. Strongest possible result for the arm. |
| `|rec_ann − rec_base| <= 0.02` | **NO INFORMATION on shape.** Normalization repair is not paid for in shape, but shape is not improved either. The arm survives; it is a normalization fix with shape held. |
| `rec_ann < rec_base − 0.02` **and** `rec_ann >= 0.494582` | **TRADE-OFF CONFIRMED. ARM REJECTED** as a repair. It buys normalization with shape, which is the failure mode this run exists to detect. |
| `rec_ann < 0.494582` | **FAILS THE ADOPTED CRITERION OUTRIGHT.** Arm rejected, and more strongly. |

**The ±0.02 band is an ASSUMPTION, not a measurement, and is declared as such.** The powered closure has
never been repeated at fixed configuration, so its run-to-run floor is unmeasured. 0.02 absolute (~3.7%
relative) is a conservative scaling of the ~1.3% GPU floor that BEN-043 measured on the fold-forward
ratio. It is declared now so it cannot be chosen after seeing the number. Per BEN-025, a difference
inside this band **does not** overturn anything.

**A secondary quantity, recorded but NOT decision-bearing:** the closure's own fold-forward deviation
under the anneal. If shape holds and normalization also holds here, that is corroboration; it is not
part of the reading above.

## What this run does NOT authorize — stated because the temptation is real

**A clean shape result does NOT authorize touching `omnifold.py`.** Repairing the anneal in shared engine
code would change **every published number**, including everything Gate-4 was re-issued against on
2026-08-09. That promotion decision is separate, larger, and **Joseph's**. This run produces evidence for
that decision; it does not make it, and no part of this predeclaration should be read as pre-authorizing
it.

Also unchanged by any outcome: **Branch C stays closed** — no product is quoted while any leg is red.

## Governance

- Isolated non-publication namespace: `nd-unfolding/pet/annealed_shape_validation/`
- Every artifact carries `NONQUOTABLE-DIAGNOSTIC` in its filename
- A self-declaring rejection manifest via `pet_diagnostic_quarantine.build_diagnostic_manifest`, whose
  non-quotability is **proven** (recomputed physics, plus the laundered-copy power test), not asserted
- **No engine edit.** The anneal is applied by a `MultiFold` subclass that overrides `CompileModel` at
  fit time only, mirroring the other lane's verified `diagnose_step1_annealed_lr.py`. `omnifold.py` is
  read-only for this run and its sha is recorded.
- **The anneal must be PROVEN to have taken effect**: every fit-time learning rate is read back off the
  optimizer and asserted against the intended `1e-4` (iteration 0) / `1e-5` (iterations > 0) pattern. A
  mismatch is a hard failure, so the run cannot silently report "annealing does not help" when the
  anneal never happened. This is the defect I flagged before the other lane's arm ran and they guarded
  it the same way.
- No promotion, no threshold change, no retry loosening.
- A `wakerctl` watch is armed at submission.

## Provenance of the numbers quoted above

- `rec_base = 0.546853`, threshold `0.494582`, ceiling `0.618228`, `f = 0.80` — `CLM-012`,
  `validate_pet_nominal_gate4.FROZEN["powered_closure"]`
- annealed fold-forward `−1.17%` (push `1.1109012166615733` vs `R = 1.1240802949941018`) — job `56534117`
- baseline fold-forward `−34.46%` (push `0.7367462501305516`) — job `56445883`
