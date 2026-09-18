# The hadronic endpoint: specification, scoring domain, reference calibration

**CITABLE FOR:** the design of a hadronic powered-closure endpoint for the matched
comparison, and for the demonstration that the pT endpoint's calibration does not
transfer to it.
**NOT CITABLE FOR:** any threshold as ratified, any result, or any adoption.

**Every scientific threshold in this document is UNRATIFIED.** §7 lists them in one
place. Nothing here is launched.

---

## 1. Why a new endpoint, in one paragraph

The predeclared powered closure injects a clipped exponential tilt in **truth muon pT**
(`closure_powered_truth_reweight.py:10-33`). Our event block is 13 muon and vertex
features conditioning the transformer through FiLM, so that tilt can be transported
almost entirely by the muon pathway. Two configurations that differ **only** in how they
represent the hadronic cloud — which is precisely what the Gregor comparison varies — can
therefore both score well on it. An endpoint that the treatment cannot move is not a
weak endpoint; it is the wrong one.

---

## 2. The injected variable

**Truth available energy, `E_avail`.** It is already in the estimator's input as
`truth_scalars` column 2, written from `MC_eavail` (`dump_pointcloud_inputs.py:79`), so
it requires **no new export and no C++ change**. It is the quantity a hadronic
representation exists to encode, which is what makes it the variable the comparison is
sensitive to.

Pre-registered alternate: `q3` (`truth_scalars` col 3). Truth hadronic angle
`MC_hadangle` is in the ROOT and dropped by the loader; recoverable if an angular tilt is
later wanted.

**Injection form** — the pT protocol with one variable changed, so the two differ in
exactly one thing:

* clipped exponential tilt, `tilt = exp(a·z)/mean(exp(a·z))`, `z = clip((x − p50)/IQR, ±c)`;
* applied to **truth-passing rows only**, because a truth-level reweighting is undefined
  where no truth record exists;
* **rate-preserving** over that population, so a pure normalization fix cannot look like
  shape recovery;
* two **disjoint** deterministic halves, 2,000,000 each, split seed 7;
* step-1 rows `pass_reco & pass_truth` on both sides.

Amplitude `a` and clip `c` are **UNRATIFIED** (§7). They cannot simply be copied from the
pT injection: the same amplitude in a different variable with a different IQR produces a
different displacement, and the displacement is what the endpoint measures.

---

## 3. Scoring domain

**Score where you injected.** The primary scoring domain is a **one-dimensional truth
`E_avail` binning**, not the (pT, p‖) reporting grid.

The reason is not convenience. Recovery is `1 − E_w[|1 − r_b|]` over cells `b`; if the
injection is in `E_avail` and the cells are (pT, p‖), then the displacement in each cell
is *induced* through the correlation between `E_avail` and muon kinematics. Whatever that
correlation is, the endpoint then measures a mixture of hadronic shape transport and that
correlation, and a configuration difference in the first can be diluted arbitrarily by the
second. Scoring on the injected variable removes the dilution by construction.

**Co-reported, not primary:** the same run also scores on the canonical 285-cell
(pT, p‖) grid, because that is the reporting grid the campaign uses everywhere else and a
result nobody can place against the existing record is less useful. The two are reported
side by side; the (pT, p‖) figure is a diagnostic and carries no decision weight.

**Both domains need their own acceptance map**, and the same formula serves both:

```
a_b = sum(w_truth | pass_truth & pass_reco) / sum(w_truth | pass_truth)
```

on the cells of that domain (`acceptance_map_fullevent_fps.json` `definition`;
`extract_fullevent_fps.completeness_2d:390-404`). Computing it on an `E_avail` binning is
a CPU read of the existing npz and introduces no new quantity.

**Binning is UNRATIFIED** (§7) and must be fixed before any comparative number exists.

**It must not be chosen to hide poorly accepted regions.** An earlier draft of mine said
the binning "should be chosen so that no bin is prior-dominated" — that is exactly the
error: dropping or merging away low-acceptance bins would raise the reference value and
flatter both arms while removing from the endpoint the region where a better hadronic
representation is most likely to matter. The (pT, p‖) grid has 37 cells below 0.01
acceptance holding 25.9 % of truth mass; the `E_avail` binning will have an analogous
low-acceptance region and it stays in.

The rules instead are: choose bin edges on **physics and resolution** grounds; **retain**
low-acceptance bins; let the reference model account for them, since it already does —
a bin with acceptance 0 contributes 0 reachable displacement at any `k`; and **report
stratified by acceptance, each stratum against its own reference value**, per BEN-038's
rule that a stratification must be by the quantity the mechanism depends on. A binning
change after seeing any comparative number is a criterion change, not a refinement.

---

## 4. Reference calibration — a model, not a bound — and why the pT value cannot be inherited

**The reference is a MODEL, NOT A PROVEN BOUND, and that qualification travels with every
number derived from it.** The construction assumes displacement reaches a cell only
through that cell's own acceptance. A smooth learner can transport a tilt across cells
(`omnifold.py:218-220`), and BEN-038 measured a band at `E_w[r] = 1.0333` — above the
modelled reachable value. `FINDING-20260806-niter4-decision.md` grades it **ASSUMED**.
So recovery is reported *relative to a reference*; a value above it is possible and is
not evidence of an error.

The reference value models the fraction of the injected displacement reachable after `k`
iterations:

```
ceiling(k, w) = Σ_b w_b · (1 − (1 − a_b)^k) / Σ_b w_b
```

Implemented and self-validating in `reference_calibration.py`: with `w` = truth mass it
reproduces the committed `ideal_recovery_percell_truthmass_weighted_by_k` field of
`products/pet/fullevent_fps/acceptance_map_fullevent_fps.json` **to machine precision at
k = 1…4** (max deviation 1.1e-16). A reimplementation that could not reproduce a
committed number would not be usable, so that check is a test, not a comment.

**The weight is the injected displacement `|prior_b − target_b|`, so the ceiling is a
property of the injection, not of the grid.** How much does that matter? Measured on the
committed acceptance map at k = 3, varying only the weighting
(`receipts/reference-calibration.json`):

| weighting | ceiling at k=3 |
|---|---:|
| mass in cells with acceptance ≥ 0.5 | 0.973 |
| mass × acceptance | 0.934 |
| uniform over populated cells | 0.768 |
| **truth mass** | **0.609** |
| mass × (1 − acceptance) | 0.371 |
| mass in cells with acceptance < 0.05 | 0.017 |

**Range 0.017 to 0.973 — essentially the whole interval.** The pT endpoint's adopted
reference (0.618228) sits near the truth-mass value, but that is a fact about the pT tilt's
displacement field, not a property of the estimator or the grid. Carrying it to an
`E_avail` injection would not be conservative; it would be arbitrary. The same argument
disposes of inheriting the pT **scatter** and **tolerance**: both are properties of where
the displacement sits, and low-acceptance cells are prior-dominated and noisy.

**Procedure, executable once the injection is fixed:**

1. compute the acceptance map on the chosen scoring domain from the existing npz;
2. compute the injected displacement field `|prior_b − target_b|` on that domain from the
   frozen tilt;
3. `ceiling = reference_calibration.ceiling(acceptance, displacement, k=3)`;
4. record both the ceiling and the displacement field in the freeze, so the number can be
   re-derived rather than re-trusted.

Steps 1 and 2 need one CPU read of `G2_FPS_MEFHC_P12.npz`. That read is **not authorized
by anything currently in force** and is the smallest next authorization this endpoint
needs (§8).

---

## 5. What the statistic is, and what travels with it

* **Primary:** `recovery = 1 − E_w[|1 − r_b|]` on the `E_avail` domain, against the
  ceiling calibrated for *this* injection.
* **Mandatory decomposition, per BEN-038:** the signed response `E_w[r]` and the scatter
  penalty `E_w[|1−r|] − |1−E_w[r]|`. On the pT endpoint 97.8 % of the baseline's gap to
  its ceiling was scatter and only −0.0019 was bias, so an arm can win the aggregate by
  being less noisy per cell. That is a real advantage and will be named as one.
* **Co-reported:** the same statistic on the (pT, p‖) grid, as a diagnostic.
* **Adequacy** is asked against the calibrated reference for the domain the arm is scored
  on, never against the pT criterion 0.494582 — and because the reference is a model
  rather than a bound, an adequacy criterion built on it is a convention, not a proof of
  sufficiency.

---

## 6. The pT endpoint is retained, as a control

`V3` keeps the pT injection **unchanged** — same code path, same protocol — as a
muon-side control and as continuity with the campaign record. If the two endpoints
disagree about which arm is better, that is a finding about where each representation
helps, not a problem to average away.

---

## 7. UNRATIFIED — every scientific threshold, in one place

None of these is adopted. Each needs Joseph's ratification before it can enter a freeze.

| # | item | proposal | why it is not settled here |
|---|---|---|---|
| U1 | injected variable | truth `E_avail` | it determines what the comparison is sensitive to — a scientific choice, not an implementation detail |
| U2 | tilt amplitude and clip | to be set so the induced displacement is measurable on the scoring domain | the pT values (0.35, ±3) do not transfer: a different variable has a different IQR and a different displacement |
| U3 | scoring domain and binning | 1-D truth `E_avail`, binning TBD | must avoid building a prior-dominated floor into the endpoint |
| U4 | reference value | computed by §4 once U1–U3 are fixed, and reported as a **model, not a bound** | **the pT value 0.618228 does not transfer** — demonstrated in §4 |
| U5 | adequacy criterion `f` | `f = 0.80` by analogy with CLM-012 | the analogy is to a *different* endpoint and is an assumption, not an inheritance |
| U6 | non-inferiority margin δ | **as a fraction of the calibrated reference**, not an absolute. `δ = 0.0275 × reference` reproduces 0.017 at the pT reference | an absolute δ in recovery units means different things against different ceilings; the fractional form is at least dimensionally transferable, and it is still a judgement |
| U7 | switching threshold δ_switch | `> δ`, proposed `0.0324 × reference` (0.02 at the pT reference) | it encodes adoption cost, which is a policy about what we will pay, **not a property of either estimator** |
| U8 | seed scatter σ | **must be measured on this endpoint** | the pT scatter does not transfer for the same reason the reference does not |

---

## 8. What this endpoint needs that is not yet available

| id | need | cost | blocked on |
|---|---|---|---|
| **E-1** | acceptance map on the `E_avail` domain, from the existing npz | one CPU read, order 1 core-hour | **authorization** — no current approval covers it |
| **E-2** | the induced displacement of a candidate tilt on both domains | same read | same authorization |
| **E-3** | ratification of U1–U8 | none | **Joseph** |
| E-4 | the fold-forward recorder (`OI-125`), ~8 lines, new file, not an edit to the pinned driver | none to write; one run to exercise | folded into the calibration stage |

E-1 and E-2 are the same job and should be one request. Until they run, the reference for
this endpoint is **undefined**, and any δ stated in absolute recovery units is
uninterpretable — which is why §7 states δ as a fraction of it.
