# AUTHORIZATION 2026-08-17 — a SECOND, data-only `C_stat` ensemble, 151 A100-h

**Joseph, 2026-08-17, verbatim: "Do it. I authorize both."** In response to a costed proposal to
publish **two** statistical covariances: a **data-only** one that is comparable with other
neutrino–nucleus cross-section measurements, and the **existing three-stream** one as the
methodologically richer object.

**This authorization is for SPEND. It is not a licence to deviate from a specification, to touch a
pinned file, or to skip a predeclaration.** Those are separate and are handled below.

## What was authorized, and the measurement behind it

| | |
|---|---|
| per replica | **3.0235 A100-h** — measured from `56857233`, 50/50 COMPLETED, sum 151.175 A100-h |
| 50-replica ensemble | **151.17 A100-h** + ~**4.666 CPU node-h** for the target leg (`56857232`) |
| against the mediator's grant | **6.30×** the 24 A100-h grant — hence Joseph's, not a quorum's |

The three-stream family already exists, so **"both" costs one new family, not two.**

## Why a data-only ensemble — the research argument, which is external

`C_stat` as built is **total** statistics (three streams), specified at the DAG in Gate 5 F7:
*"apply signal factors everywhere signal MC is used."* Lane C ruled that correct **by internal
design** — there is no `C_MCstat` component anywhere, and `C_syst` varies physics parameters not
sample size, so if `C_stat` did not carry the MC Poisson **nothing in the declared budget would**.

That argument is about the budget's internal consistency and is silent on **external comparability**,
which is Joseph's constraint and is a hard one:

```
counting-floor VARIANCE share of the three-stream C_stat
  data             11.94%
  signal MC         1.00%
  background MC    87.06%      <- dominant, and the smallest inventory (564,591 rows)
  not data         88.06%
  sigma_stat(three-stream) / sigma_stat(data-only) = 2.89x
```

**A published "statistical" uncertainty that is ~88% MC statistics by variance is not comparable to
any other neutrino cross-section measurement's `sigma_stat`**, cannot be profiled as a nuisance term
in a global fit, and is *reducible by generating more MC* — which is precisely what `sigma_stat` is
not supposed to be.

*Limit, stated: these are raw `1/sqrt(N)` counting fractions. The background enters as a negative
injection and the signal MC through the estimator, so neither propagates with unit leverage. **The
set of contributing streams is certain; the variance shares are indicative.***

## What the same run also settles, at no extra cost

- **`OI-60`** — E measured both roads re-run the family at **151.175 A100-h**. *This is that run.*
  The loader telemetry fix rides it, per `BEN-326`'s rule that the fix must not **motivate** a
  re-issue but may **ride** one. Publication comparability is the independent reason.
- **`OI-61`** — does not split (`BEN-386`); both halves ride whatever `OI-60` rides.
- **`OI-126` — THE DECISIVE TEST.** A data-only ensemble has **no nominal/replica training
  asymmetry**: every replica trains on the same MC as the nominal, at full statistics. Under
  Poisson(1) MC resampling each replica instead sees `N_eff = N/2` and only `1 − 1/e = 63.2%` of
  distinct rows. **If the nominal sits INSIDE the data-only family, the non-containment was
  MC-thinning. If it is still outside, both surviving conjectures die at once.**

## WHAT THIS AUTHORIZATION DOES NOT DO

1. **It does not authorize deviating from Gate 5 F7.** A data-only ensemble *contradicts* the
   specified construction. It must be framed as a **SECOND PRODUCT UNDER ITS OWN SPECIFICATION**,
   not as a correction of the first, and the existing three-stream family is **not** superseded,
   discarded, or re-verdicted. Lane C rules on the framing before anything is written.
2. **It does not authorize touching a pinned file.** The data-only factors require a change at or
   near `coherent_bootstrap_factors` (`fullevent_fps_dataloader.py:614-625`) — a file E's sweep
   found **PINNED with 25 digest sites**, the most exposed on the list. `BEN-384` governs: grep
   against the pin sites and run `verify_hash_bindings.py` against the intended diff **before
   writing**. `BEN-386` governs what any sweep may conclude: it can establish an item is expensive
   and **never** that it is cheap.
3. **It does not skip predeclaration.** This campaign predeclares before running. The ensemble gets
   a predeclaration naming the construction, the comparison, and the `OI-126` decision rule
   **before submission** — and per `BEN-403`, the decision rule must be **derived from the mechanism
   rather than read off the observation it would explain**, or it cannot fail.
4. **It lifts none of the standing prohibitions.** `gate6traj-reconcile-56847059` frozen; no
   `scancel`/`scontrol`; no repin of any receipt-bound launcher; `P4_VERIFIER_PASS` never set by
   hand; the five Gate-6 prohibitions at `19585b7`; `C_ML` construction prohibited; nothing enters
   `docs/analysis-note/`.
5. **`BEN-381`** — the lane that modifies the instrument must not grade the leg it measures.

## Sequence

1. **C** — rule on framing: second product under its own spec, or a Gate 5 F7 amendment. Nothing
   is written until this lands.
2. **E** — establish the code route to data-only factors and its pin exposure. `BEN-384` first.
3. **Predeclaration**, including the `OI-126` decision rule, derived not observed.
4. **Second key** reviews the predeclaration **before** submission.
5. Only then, submit.

**Authorized by Joseph. Recorded by the mediator. Nothing submitted at the time of writing.**

---

## AMENDMENT 1 — 2026-08-17: the CPU unit, authorized separately

**Joseph, verbatim: "Yes I authorize CPU hours, too."**

The original authorization covered **151.17 A100-hours**. The eighth site (`BEN-420`) established that
`C_stat^data` requires **its own target family** — reusing the existing 50 would leave the background
Poisson *inside* the family while `P3` asserts unity, which is the largest MC contribution the product
exists to exclude, asserted falsely in the artifact under a guard the implementing lane wrote.

**That stage is CPU, and it was surfaced rather than absorbed:**

| | |
|---|---|
| target family | **~46.3 CPU node-hours** (50 × 0.9256), **ZERO additional A100-hours** |
| measured from | `56344268` — `00:55:32`, 256 CPU, 1 node, **no GPU** |
| training family | 151.17 A100-hours, unchanged |

**Why it was surfaced rather than spent:** the campaign's standing discipline is that every run is
reported with its unit, and an A100 grant does not silently cover CPU node-hours. The same discipline
caught the inverse error earlier today — `OI-60`'s Gate-2 re-run was recorded as GPU and is a **CPU**
job, so *"an A100 grant cannot buy it"* in the direction nobody expected.

**Also amended, and it happened before this authorization rather than because of it:** the motivating
figure was corrected from `σ_total/σ_data = 2.89×` to **`1.18×` on measured injected leverage**, and
Joseph ruled *"this will generate a result that can be compared to existing results more cleanly …
do it"* **on the corrected number**. The case is *"~18% too large and reducible by generating more MC
rather than more data"* — definitional rather than magnitude-based, and it is the form authorized.

**Nothing else in the original authorization changes.** All five non-authorizations stand: no Gate 5
F7 deviation, no pinned-file edit, no skipped predeclaration, no lifted prohibition, and `BEN-381`.
