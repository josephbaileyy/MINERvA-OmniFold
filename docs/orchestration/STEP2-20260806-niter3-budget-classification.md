# STEP 2 (2026-08-06) — what must be re-thrown at `niter=3`, and what transfers

*Step 2 of [`PLAN-20260806-niter3-budget-and-J28-reroll.md`](PLAN-20260806-niter3-budget-and-J28-reroll.md),
under its rule 5: a "transfers unchanged" claim needs a **positive** argument — a stated reason the
component cannot depend on the estimator — never the absence of a reason to doubt it. Reviewed by a
fresh-context session before landing, per Joseph's 2026-08-06 15:22Z standing condition; that review
corrected two of the seven findings this document originally rested on, and both corrections are folded
in below rather than footnoted.*

## 1. The headline: item (d) is misframed for the PET lane

`OPEN_ITEMS.md` item (d) says the budget must be **RECOMPUTED** at `niter=3`. For the full-event PET
lane there is nothing to recompute, because **no full-event PET covariance component exists**:

- `products/pet/fullevent_fps/` holds exactly two files — `acceptance_map_fullevent_fps.json` and
  `closure_fullevent_fps.json`. No covariance.
- `PET_UQ_PRODUCTION_STATUS.md` contains **zero** occurrences of `fullevent`/`full-event`; its scope
  (`:3-7`) is the background-subtracted **recoil** target, and `:15-17` declares that campaign
  "COMPLETE for the present analysis note" with the 100-replica ensemble planned and not run.
- There is no full-event counterpart to `sbatch_pet_clateral_bkgsub.sh`,
  `sbatch_csyst_prelim_bkgsub.sh`, `sbatch_phase7_retrain.sh`, or the bootstrap array.

So the work is a **BUILD**, not a recompute — which is what `OPEN_ITEMS.md:427-428` already required
through item 6. Item (d)'s wording should be read as "the budget must exist at `niter=3`", not "the
existing budget must be recomputed."

## 2. What is being written off (corrected inventory)

The recoil `bkgsub` budget is **complete and assembled** — not, as this document first claimed, "a
C_stat plus a pilot." All of it is recoil-schema and none of it is full-event, so the conclusion is
unchanged, but the inventory being discarded is roughly three times larger than first stated:

| component | sqrt_trace | source |
|---|---|---|
| C_syst (vertical, 13 bands) | 2.970e-38 | `pet_csyst_prelim_bkgsub_5d.summary.json` |
| C_retrain (rank 6, material bands) | 2.190e-38 | `pet_cretrain_bkgsub_5d.summary.json` |
| C_stat (20 replicas) | 7.439e-39 | `pet_cstat_bkgsub_5d.summary.json` |
| C_ml (12 members, 4×3 grid) | 8.036e-39 | `pet_cml_bkgsub_5d.summary.json` |
| C_lateral | 4.690e-39 | `pet_clateral_bkgsub_5d.npz` |
| **C_total** | **3.878e-38** | `pet_ctotal_bkgsub_5d_final.summary.json` |

Plus a **newer 42-replica interim C_stat** (`pet_cstat_bkgsub_5d_interim_42rep.summary.json`,
sqrt_trace 7.246e-39, with PSD gates) that supersedes the 20-replica file, and six combined ROOTs at
`products/pet/` (`pet_4d_covariance_combined{,_wlat,_rebank}.root`,
`pet_5d_covariance_combined{,_wlat,_unified_wlat}.root`).

**Positive disqualification, three independent axes** (rule 5 satisfied): every one of these hangs off
`pet/sbatch_pet_nominal_bkgsub.sh`, which (i) pins `NITER="${PET_NITER:-2}"` at `:42` and states
`iters = 2` at `:29`; (ii) carries the banner **"QUARANTINED RECOIL-ONLY CROSS-CHECK LAUNCHER — NOT a
publication path"** at `:14`, naming `fullevent_fps_dataloader.py` as the publication route; and (iii)
produces a **10550-bin** recoil reported domain against **10694** for the 5D lane. Its `:15-17` states
that "C_stat, C_ml, and systematic blocks all reference THIS nominal", so the disqualification applies
to the whole block at once. This is a stated reason they cannot serve the `niter=3` budget, not an
absence of evidence that they can.

## 3. The 5D GBDT lane transfers — stated positively

The claim is **not** "the PET `niter` switch is irrelevant because they are different estimators."
That is a disjointness assertion, which is precisely the form rule 5 forbids: it is what one would
write whether or not a hidden dependency existed. The positive form:

> The 5D GBDT covariance is a **closed function of an enumerated input list that contains no PET
> quantity.** `adopt_unified_5d.py:75,78` take exactly `uq_5d/unified_throw_cov_5d.root` and
> `products/5d/xsec_5d_MEFHC_5iter_lgbm.root`; `g` is built at `:88-102` from the `C_unified` /
> `C_blocksum` diagonals of that throw file alone. `sbatch_uthrow_combine_5d_fast.sh:19` fixes that
> file's estimator at `--iters 5` on `bank_uthrow_5d`. And `NOMINAL_SEED_POLICY['niter']`
> (`train_fullevent_nominal.py:51`) is read by exactly one driver, which writes nothing that any 5D
> GBDT product reads.

**This is falsifiable, which is the point:** one new file dependency in `adopt_unified_5d.py`, or one
PET artifact appearing in the combine's inputs, breaks it. The argument is attached to the input list,
not to the conclusion, so it can be re-checked mechanically.

Three candidate couplings were checked and found absent: a shared `g` (no — no PET input on any code
path), a shared lateral block (no — GBDT laterals come from the 18-universe 5D detector sweep, the PET
lateral is PET-native shifted-W), and a cross-lane comparison consumed as an uncertainty (no — the
PET-vs-GBDT summaries render verdict strings and ratios that nothing consumes as a covariance
component; `sec_eavailw.tex:122-124` says explicitly that it borrows the frozen-reweighter *technique*
"— not the PET covariance matrix, which is never applied to this GBDT central value").

**The dependency that does exist runs the other way:** `pet_csyst_prelim_bkgsub_5d.summary.json`
records `"bank": ".../bank_uthrow_5d"` — the PET vertical block consumes the GBDT throw bank. So the
J28 re-roll (job `56417324`) propagates **into** any future PET budget, not out of it. Direction is
safe for this claim, and it means the re-roll is a prerequisite for the PET build rather than
independent of it.

**One real `niter` coupling, on the central value rather than the covariance:** `sec_pet.tex:47`
discloses "The PET run used a 2M-event, two-iteration training." If full-event PET moves to `niter=3`,
`\petRatio` (0.912, used at `sec_pet.tex:42,59`) and `\petClosure` change. That is a quoted-number
dependency in the PET section, not a 5D GBDT budget dependency.

## 4. Do not inherit the J28 exemption list

The plan's §2 warns that "unaffected by J28" is not "unaffected by `niter`". The seven items on the
ledger's quotable list (`VALIDATION_LEDGER.md:82-83` — central cross sections, corrected 4D block-sum
core, closure, dimensional anchors, statistical and ML covariance, detector laterals, finalized 2D
covariance) are a **J28** list. Each still needs its own positive `niter` argument. In practice §3's
closed-input argument covers all of them in one stroke, because all seven are GBDT-lane products —
but the stroke has to be written, not inherited.

## 5. Unclassified items this step surfaced

1. **`eavailW_covariance.py` is a sixth J28 site**, absent from `081ae4a`'s twelve files and unscoped
   by `AUDIT-FINDINGS-20260731.md`. Confirmed at the mechanism level and recorded in `KNOWN_ISSUES.md`.
   Code read, **not run** — direction is fixed, magnitude is not. Neither in scope nor explicitly
   excluded by the plan.
2. **The (E_avail,W) covariance** sits downstream: `eavailW_covariance.py:281-304` builds its `C_stat`
   as `M C_5D M^T` from `uq_cov_stat_5d.root` (the bootstrap, which J28 does not reach), but its
   *systematic* block is built from the universe family just corrected. Not in the plan at all.
3. **The 4D lane.** `CORRECTED_UQ_PRODUCTION_STATUS.md:78-83` records 4D unified-throw as BLOCKED
   (missing 3D omnifile) with three options open, and `sweep_bank.py:254` is one of the five known J28
   sites, so the 4D sweep carries the defect. Its comparison metrics are already withdrawn
   (`values.tex:50-51`).
4. **The FPS model-dependence block.** `products/pet/fps_envelope_5d/fps_modeldep_cov_5d.root` (868 MB,
   plus an `_xps2` variant) is a covariance product on neither this list nor the plan's exemption list.
   It is GBDT-prior-derived (`fps_gbdt_prior_xsec_5d.npz`) so `niter` does not reach it, but
   `OPEN_ITEMS.md:424-426` requires the FPS prior envelope be recomputed for the full-event estimator
   regardless. Classified explicitly here rather than by omission.

## 6. The decision this step actually exposes — and it is Joseph's

The cost of the full-event PET budget was previously reported as the main gap to "a cross section for
the full phase space and a measure of uncertainty." **That framing needs correcting, because the note
does not currently quote any PET covariance:**

- `sec_pet.tex:1` titles the section "Recoil-point-cloud representation cross-**check**"; `:6` calls
  PET "a low-level-representation cross-check".
- `values.tex:69-71` defines `\petTotalMedian` (15.10), `\petTotalTrace` (3.878e-38) and
  `\petFourMedian` (12.37), each marked `QUARANTINED` — and **all three are referenced 0 times** in
  the tex tree. Only `\petRatio` (2 uses) and `\petClosure` (3 uses) appear.
- The quoted headline budget is the **GBDT 5D lane** (`values.tex:57-60`).

So the note is already internally consistent **without** a full-event PET budget, and the
~100+ GPU-h (see below) buys a PET precision comparison the note presently, deliberately, declines to
make. `sec_pet.tex:100` does say the replacement "belongs to the full-event PET estimator and receives
a fresh statistical and ML ensemble", so such a budget is *planned* — but whether it is
**publication-blocking or discretionary is recorded nowhere**, and that question is worth more than the
rest of this classification. It is Joseph's call, and it has been escalated.

**On the cost figure:** the previously-quoted "~170–250 GPU-h" is **not verified**. What is grounded:
`sbatch_pet_nominal_bkgsub.sh:31` prices one recoil train at "~1 h on 1 GPU" (2M events, `niter=2`);
the target is 100 replicas (`combine_cstat_bkgsub_100rep.py`, `PET_UQ_PRODUCTION_STATUS.md:15-17`); and
full-event at `niter=3` is strictly more per train. So C_stat alone is **≥100 GPU-h** before the eight
other products in `OPEN_ITEMS.md:420-428`. Order-of-magnitude consistent with the earlier figure;
treat ≥100 GPU-h as the defensible floor and the 170–250 band as an estimate, not a measurement.
