# FINDING 2026-08-06 — the exact J28 flux re-roll: the Flux block was understated fourfold, and `g` moves in a convention-dependent direction

*Step 1 of [`PLAN-20260806-niter3-budget-and-J28-reroll.md`](PLAN-20260806-niter3-budget-and-J28-reroll.md),
run against its predeclared rules (§5). This is a **measurement**, not an adoption:
`rescale_flux_universes.py` writes its own output and adopts nothing. No number here is quotable as a
published uncertainty until adoption lands, and the ledger quarantine stays in force.*

Owning items: `KNOWN_ISSUES.md` J28; ledger quarantine `VALIDATION_LEDGER.md:74-96`; `CLAIMS.md` CLM-010.

> ## CORRECTION 2026-08-06, later the same day — this re-roll covers 122 of the adopted 160 throws
>
> The first version of this document said the inputs were "the ensemble the **adopted**
> `unified_throw_cov_5d.root` was built from." **That is wrong.** Read directly from the adopted ROOT
> this turn: `n_throws = 160`, `sqrt_tr_unified = 4.4607819710748654e-38`,
> `joint_mean_shift_norm = 1.654393237996853e-38`. My re-roll processed **122 throws**, with a "before"
> `sqrt_tr_unified` of 4.343878e-38 — **−2.62%** against the adopted value, and −7.21% on the mean shift.
>
> **Why:** run F was `[0-39%40]` at 4 throws/task = 40 slabs = 160 throws, and
> `uq_5d/uthrow_slabs_5d_sb/` now holds only slabs **0–30**. Slabs **31–39 are gone** — 9 slabs,
> ~38 throws. 30 slabs × 4 + one 2-throw slab = 122, and 122 + 38 = 160. The adopted covariance was
> built while they existed; they have been lost since (scratch is purgeable), and **Step 0's protection
> came too late for them** — it protected what survived, which is exactly the loss Step 0 exists to
> prevent, realised before I got there.
>
> **What still stands, and what does not.** The before → after comparison is computed from the *same*
> 122 slabs on both sides, so it is a controlled measurement of the **correction's effect** and every
> *relative* change below is sound. What does **not** follow is that the corrected absolute numbers are
> drop-in replacements for the adopted ones — they are a 76.2% subsample of that ensemble. Replacing the
> adopted covariance exactly requires re-throwing slabs 31–39; otherwise the replacement is a 122-throw
> product and must be labelled as one.
>
> The J28 magnitudes are unaffected by this: `+316.83%` on the flux block and `+10.19%` on the block sum
> are ratios within one consistent slab set.

## What was run

Perlmutter job `56417324`, one CPU node, ~2 minutes wall. Inputs are the ensemble the **adopted**
`uq_5d/unified_throw_cov_5d.root` was built from, identified from two independent sources that agree —
`sbatch_uthrow_combine_5d_fast.sh:16-19` (the FAST-path combine's own globs) and the run-F entry at
`CORRECTED_UQ_PRODUCTION_STATUS.md:266-268` (`uthrow5d_combF` → that ROOT):

| input | value |
|---|---|
| throw slabs | `uq_5d/uthrow_slabs_5d_sb/uthrow5d_slab_*.npz` — 31 slabs (indices 0–30), **122 throws — the surviving 76.2% of the adopted 160**; slabs 31–39 are lost, see the correction above |
| block units | `uq_5d/block_slabs_5d_sb/block5d_*.npz` — 36 files, **100 flux block units corrected** |
| bank | `bank_uthrow_5d`, 100 flux universes, **max \|r_u − 1\| = 0.1371** |
| CV | `products/5d/xsec_5d_MEFHC_5iter_lgbm.root` |
| reported bins | 10,694 |

Two facts about scope worth recording before the numbers. **Knob endpoints were correctly left
untouched** — every `block5d_knob_*.npz` reports `0/2 corrected`, which is the intended behaviour
(a knob universe does not move the flux integral, so `Φ_CV` was always the right denominator there);
seeing `0/2` is the tool working, not failing. And the adopted combine ran `--expected-throws 0-159`
while only **122** throw rows exist in these slabs, so the adopted covariance was built from 122
throws, not 160 — worth knowing before anyone reasons about its finite-throw noise.

## The result

| quantity | before | after | change |
|---|---|---|---|
| `sqrt_tr_flux_block` | 3.892270e-39 | 1.622406e-38 | **+316.83%** |
| `sqrt_tr_blocksum` | 3.403264e-38 | 3.750055e-38 | **+10.19%** |
| `sqrt_tr_unified` | 4.343878e-38 | 4.312442e-38 | **−0.72%** |
| `sqrt_tr_cross` | 2.699457e-38 | 2.129377e-38 | −21.12% |
| `joint_mean_shift_norm` | 1.535143e-38 | 1.885299e-38 | +22.81% |
| `g_mean` mean-centered | 1.0565550 | 1.0295687 | **−2.55%** |
| `g_mean` CV-centered | 1.1117482 | 1.1186232 | **+0.62%** |
| `g_max` mean-centered | 22.302611 | 17.202930 | −22.87% |
| `g_max` CV-centered | 22.627878 | 17.358363 | −23.29% |

Receipt: `nd-unfolding/uq_5d/rescaled_20260806/j28_reroll_20260806.json`.

## Why it moves this way

Dividing each Flux universe by `Φ_CV` instead of its own `Φu` **removes the normalization spread the
flux universes exist to carry**. So the defect *understated* the Flux block — by a factor of ~4.2 on
its sqrt-trace — rather than inflating it. That single fact drives everything else:

- the **block sum** rises 10.19%, because its Flux term was the understated piece;
- the **unified** total barely moves (−0.72%), because the unified throw ensemble draws flux and knobs
  jointly and was always dominated by the joint spread;
- therefore the **cross term** `C_unified − C_blocksum` collapses 21.12% — the block sum has risen to
  meet a nearly unchanged unified total;
- and `g = √max(v_uni, v_block)/√v_block` falls toward 1 wherever `v_block` grew into `v_uni`.

**This was the wrong sign to expect from the first-order estimate**, which is exactly the case the
plan's rule 2 predeclared as a finding rather than a number to adopt quietly. The estimate suggested
a few percent *upward* on the combined scale (`5.81e-38 → 6.0e-38`, +3–4%) and ~+6% on the combined
block; the exact block sum moved **+10.19%** — 70% larger than predicted — while the total unified
sqrt-trace moved **down**. Per rule 1 the exact numbers replace the estimate; they do not corroborate
it, and the estimate should not be cited again.

## The part that resists a one-line summary

**The direction of the adopted-scale change depends on the F7 mean-shift convention.**
`joint_mean_shift_norm` grew **+22.81%**, and CV-centering adds `shift²` to the variance:

- mean-centered: `g_mean` **falls** 2.55%
- CV-centered: `g_mean` **rises** 0.62%

So "the correction reduces the inflation factor" is true under one convention and false under the
other. Both conventions agree that `g_max` falls ~23%, i.e. the extreme tail bin is less inflated. The
two must not be mixed across a single budget.

> ### F7 IS NOT ACTUALLY OPEN — the rule was predeclared and the data answers it
>
> This was escalated to Joseph as an open choice. It should not have been:
> `CORRECTED_UQ_PRODUCTION_STATUS.md:73-78` states the criterion **in advance of the data**, which is
> the standard this campaign holds itself to:
>
> > "measure `||mean_shift||` vs sampling floor `sigma/sqrt(160)`. If ~floor → mean-centered OK.
> > If >> floor → **also produce CV-centered variant** (`C_unified + outer(mean_shift)`); report shift
> > either way. **Do NOT silently drop.**"
>
> Applying it to the adopted ensemble (values read from the ROOT this turn):
>
> | ensemble | sampling floor `sqrt_tr/√N` | `\|\|mean_shift\|\|` | ratio | `\|\|ms\|\|/sqrt_tr` vs floor `1/√N` |
> |---|---|---|---|---|
> | **adopted, N=160** | 3.5266e-39 | 1.6544e-38 | **4.69×** | **37.1%** vs 7.9% |
> | re-roll before, N=122 | 3.9328e-39 | 1.5351e-38 | 3.90× | 35.3% vs 9.1% |
> | re-roll after, N=122 | 3.9043e-39 | 1.8853e-38 | **4.83×** | 43.7% vs 9.1% |
>
> `||mean_shift||` is **4.69× the sampling floor** on the adopted ensemble and the flux correction makes
> it *worse* (4.83×). That is ">> floor" on any reading. Note the 37.1% is not a new interpretation —
> `CORRECTED_UQ_PRODUCTION_STATUS.md:325` recorded "joint_mean_shift_norm 1.654e-38 (**=37% of sqrt_tr →
> NON-negligible**, FEED Fable-F7 adopt decision … may need CV-centered variant)" when the headline
> landed on 07-13.
>
> **Consequence: quoting the mean-centered variant alone is disqualified by the predeclared rule.** The
> CV-centered variant must be produced and the shift reported either way. So the operative `g` change is
> the CV-centered **+0.62%**, not the mean-centered −2.55% — i.e. the corrected inflation goes very
> slightly **up**, and my earlier emphasis on "g falls toward 1" described the disqualified variant.
>
> What remains genuinely Joseph's: whether CV-centered becomes the sole published headline or both are
> reported side by side. The rule settles that mean-centered-only is not an option; it does not settle
> presentation.

Per rule 3, note what is **not** claimed: `g_max` is a single-bin extremum over 10,694 bins with no
interval attached, so the ~23% fall is a point observation about one bin, not a spread claim. And
`n_throws = 122` is the real `n` behind every number above.

## What this does and does not settle

**Settles.** The exact corrected covariance for these slabs exists, so J28 no longer blocks on being
sized. The re-roll needed no re-unfolding, as designed — the correction is an identity along `pT`.

**Does not settle.** (1) **Adoption**, which is a separate decision and needs the F7 convention fixed
first. (2) **`niter`.** These slabs are the **5-iteration GBDT 5D** lane (`--iters 5`, CV
`xsec_5d_MEFHC_5iter_lgbm.root`), not the PET lane whose policy moved 2 → 3. The plan's Step 1 is
deliberately `niter`-agnostic — the flux rescale does not care which `niter` produced a slab — so this
result is complete on its own terms, but it is **not** the `niter=3` budget, and nothing here
discharges `OPEN_ITEMS.md` item (d). Step 2 (classifying what transfers vs what must be re-thrown)
is still open, and rule 5 governs it: a "transfers unchanged" claim needs a positive argument that the
component cannot depend on the estimator.
