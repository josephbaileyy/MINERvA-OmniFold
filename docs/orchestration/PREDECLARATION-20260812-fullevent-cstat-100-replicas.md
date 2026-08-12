# PREDECLARATION 2026-08-12 — the 100-replica `C_stat` is declared against the FULL-EVENT estimator, and is NOT launched

**Owner:** Session C (PET). **Authority:** Joseph, 2026-08-12, relayed by Session A, verbatim:

> *"Keep the existing 20-replica `C_stat` only for the disclosed, quarantined recoil-PET diagnostic; do
> not spend compute enlarging that superseded estimator. Predeclare and run 100 replicas for the
> eventual full-event publication `C_stat`. Close the old conditional deferral by supersession, not by
> declaring 20 publication-grade."*

**NOTHING IS LAUNCHED BY THIS FILE AND NOTHING MAY BE.** The estimator it targets does not exist: there
is no full-event PET nominal from which replicas could be drawn (`KNOWN_ISSUES.md` #19 — *no full-event
FPS **result** exists*). This is the predeclaration written now so that the eventual run is
pre-registered rather than designed after its own first look. Its launch is gated below.

## 1. What was refused, and why it is not the binary anyone proposed

Two options were put to Joseph — leave `C_stat` at 20, or spend the compute to reach 100. **He refused
both**, and the refusal is the substance:

- **Not 100 on the recoil estimator.** That is compute spent enlarging a **superseded** estimator. Every
  pre-2026-08-01 PET number is a different estimator; a tighter statistical term on it does not become a
  publication number by being tighter.
- **Not 20 declared publication-grade.** The 2026-07-14 deferral (`KNOWN_ISSUES.md` #15) was conditional
  — *"deferred to POST-presentation, to be scoped alongside the full-stats FPS training"* — and this lane
  reported that the condition had expired. **An expired conditional deferral does not convert into a
  blessing by expiring.** It closes **by supersession**: the obligation moves to the successor estimator
  and the old number is retained only as the disclosed diagnostic it already is.

**This lane recommended "leave at 20" and that recommendation is superseded.** It was not wrong about
the note — `sec_pet.tex:110-112` already self-discloses *"based on **20** coherent replicas … more
limited than the 100-replica **target**"*, and no PET `C_stat` magnitude appears in any `.tex`. It was
wrong about the **disposition**: "leave at 20" reads as *20 is what we ship*, which is precisely the
blessing the decision refuses.

## 2. Status of the existing 20-replica `C_stat` — unchanged, and now explicitly bounded

`products/pet/bkgsub/pet_cstat_bkgsub_5d.npz`, 20 replicas, per-bin 7.85%, √tr `7.439e-39`
(`docs/orchestration/STEP2-20260806-niter3-budget-classification.md:37`). It **remains**:

- a **recoil-only** product, inside the 2026-07-12 quarantine, on the disclosed diagnostic path;
- **not** enlarged, **not** re-run, **not** promoted;
- **not quotable as a full-event statistical term**, by the same scope limit that governs the
  joint-vs-additive measurement (`DETERMINATION-20260811-cause5-binding-half.md` §3.3: *"No magnitude
  here is quotable and none transfers to the full-event budget"*).

## 3. THE PREDECLARATION — fixed before any full-event replica exists

**Estimator.** `pet-fullevent-fps-v1` only. If the canonical full-event nominal changes after this file
is written, **this predeclaration does not follow it** — it is re-issued against the new one, and the
re-issue says so. A predeclaration that silently retargets is not a predeclaration.

**Count.** `n_replicas = 100`, declared **before** any is drawn. The number is not to be revised
downward on observing the spread; if 100 proves unaffordable the run is **not** shipped at 60 with a
note, it is re-predeclared with the reason stated and the shortfall named as a limitation.

**Construction, inherited from the corrected recoil `C_stat` and re-asserted here** so the successor
cannot quietly relax it (`KNOWN_ISSUES.md` #15's corrected form):

1. Data and MC fluctuated **coherently** per replica.
2. Retrain at **fixed estimator seed** — the replica index varies the data draw, never the network init.
3. The **same MC draw applied during extraction** as during training.
4. **Complete manifests**; a replica missing from the manifest is a failed replica, not an absent one.
5. Centre on the **replica mean**, not on the nominal.
6. Pilot-vs-floor check retained.

**Read-out, declared now.** The reported quantity is √tr of the assembled `C_stat` and the per-bin
median fractional term, both against the **full-event** central vector. The **20-replica recoil value
`7.439e-39` is not a comparator** and no ratio to it is to be reported: they are different estimators,
which is the whole reason this file exists.

**Pre-registered failure branches, so "it worked" is falsifiable:**

- **INSUFFICIENT** — fewer than 100 complete manifests at assembly. Not repaired by rescaling.
- **NON-PSD** — assembled `C_stat` not positive semi-definite in 5D or in the 4D marginal.
- **SEED LEAK** — any replica whose estimator seed differs from the fixed value; fail closed, do not drop
  the replica and continue.
- **CENTRING ERROR** — centred on nominal rather than replica mean. This is the defect the corrected
  recoil `C_stat` was built to fix and it is the one most likely to recur.
- **PASS** — 100 complete, PSD in both, seeds uniform, centred on the replica mean.

## 4. LAUNCH GATE — all four, and none is satisfied today

1. A canonical **full-event PET nominal exists** and is promoted (today: none — `KNOWN_ISSUES.md` #19).
2. **Quarantine cause 5 is discharged** by the joint full-event construction — Joseph's option (a),
   2026-08-12. Cause 5 is currently **kept quarantined**, option (b).
3. **Branch C is lifted.** Job `56691812` did not lift it and said so.
4. **Explicit launch authorization**, referencing this file by name. *This file is not that
   authorization* and the standing 12-hour compute approval does not reach it: a 100-replica retraining
   campaign is not a single job under 12 hours.

## 5. Cost, stated so the gate is honest rather than decorative

`FULL_EVENT_FEATURE_CONTRACT.md:233` sizes coherent replicas at **~1.2 h each**, so 100 replicas is
**~120 GPU-hours** before extraction and assembly, plus the merge. That is the reason this is gated
rather than queued, and it is why "predeclare now, launch later" is the right shape rather than a delay.
