
### Uncertainties: Step 0 protected the wrong two-thirds, then Step 1 produced a real number

With `56415634` sitting in the queue, the unblocked half of "central value **and** uncertainties" is the
budget. `PLAN-20260806-niter3-budget-and-J28-reroll.md` already had predeclared decision rules, so this
was execution, not a new decision.

**Step 0 — and I got it wrong the first time.** Protect the throw slabs the J28 re-roll consumes; a
`/pscratch` purge turns a two-minute rescale into a re-throw campaign. First pass protected **365 of
542** files and printed "365 readable, 0 unreadable", which reads as complete. The filter was
`"slab" in filename`, and the entire **block** ensemble is named `block5d_flux_17.npz`,
`blockfps_*.npz`, `block4d_0.npz` — no "slab" in the filename, only in the directory.
`rescale_flux_universes.py` rebuilds `C_blocksum` from exactly those, so a purge would have left Step 1
unrunnable while the manifest asserted the inputs were safe. **Filed BEN-032.** What makes it worth a
finding rather than a shrug: the count of what was checked is not the count of what exists, and nothing
inside the result set could reveal the missing third — the denominator had to come from somewhere else
(`find -name '*slab*'` vs `-path '*slab*'` differ by 49%). Found by asking what Step 1 *consumes*, not
by re-reading Step 0.

Corrected: 548 files / 8.1 GiB (542 slabs + 3 bank `flux_univ_ratio.npy` + 3 `cv.npz`), all readable via
`np.load` with every array materialised, every destination file re-hashed, and the copy re-verified
against the **CFS root** — the restore path — not just the source. The check has power: one flipped byte
yields `*** SLAB SET DIVERGED ***`. Excluded deliberately: the banks' 89 GB of per-universe
`sig_*`/`td_*` arrays, which are re-**throw** inputs, not inputs to this rescale. The plan's own "365"
precondition came from the same filter, so it inherited the gap it was written to close.

**Step 1 — the exact re-roll, job `56417324`, ~2 minutes on one CPU node.** Two blockers resolved en
route: ROOT segfaults under the absolute-path interpreter (cling cannot resolve the conda toolchain's
include paths) so it needs `source setup_salloc_env.sh`; and the adopted ensemble had to be *identified*
rather than guessed — `block_slabs_5d` holds 8 files and `block_slabs_5d_sb` holds 36, and re-rolling
the wrong one yields a confidently wrong number. Two independent sources agree on `_sb`.

    sqrt_tr_flux_block     3.892270e-39 -> 1.622406e-38   +316.83%
    sqrt_tr_blocksum       3.403264e-38 -> 3.750055e-38    +10.19%
    sqrt_tr_unified        4.343878e-38 -> 4.312442e-38     -0.72%
    sqrt_tr_cross          2.699457e-38 -> 2.129377e-38    -21.12%
    joint_mean_shift_norm  1.535143e-38 -> 1.885299e-38    +22.81%
    g_mean mean-centered   1.0565550    -> 1.0295687        -2.55%
    g_mean CV-centered     1.1117482    -> 1.1186232        +0.62%

**The defect was backwards from how it had been framed.** Dividing each universe by `Φ_CV` instead of
its own `Φu` *removes* the normalization spread the flux universes exist to carry, so J28
**understated** the Flux block — by ~4.2× on its sqrt-trace — rather than inflating it. Correcting it
raises the block sum toward a nearly unchanged unified total, which is why the cross term collapses 21%
and `g` falls toward 1.

Both predeclared rules fired, which is the only reason this reads as a result. **Rule 1:** the
first-order "+3–4% upward / ~+6% on the block" estimate is superseded and was **not** confirmed — exact
is +10.19% on the block sum and *down* 0.72% on the unified total. **Rule 2:** the `g` direction is
**convention-dependent** — `mean_shift` grew 22.81%, CV-centering adds `shift²`, so mean-centered
`g_mean` falls 2.55% while CV-centered `g_mean` *rises* 0.62%. "The correction reduces the inflation
factor" is true under one convention and false under the other, and the F7 choice is still open. Rule 3:
`g_max` falling ~23% is one bin out of 10,694 with no interval; `n = 122` throws.

**Adopts nothing.** The quarantine stays in force. And these are the **5-iteration GBDT** slabs, not the
PET lane whose policy moved 2 → 3 — Step 1 was deliberately `niter`-agnostic, so this is complete on its
own terms but does **not** discharge item (d). Landed in all three homes §6 requires plus the plan.

### Step 2: the classification, a sixth J28 site, and a correction I owe on the end-goal question

Fresh-context review before landing, per the 15:22Z standing condition. It corrected **two of my seven
findings**, and both corrections matter more than the classification did.

**Item (d) is misframed for the PET lane.** There is no full-event PET covariance to *recompute* —
`products/pet/fullevent_fps/` holds two non-covariance files, `PET_UQ_PRODUCTION_STATUS.md` contains
**zero** occurrences of "full-event", and no full-event counterpart to any `bkgsub` covariance launcher
exists. The work is a **BUILD**, which item 6 already required.

**Correction 1 — what is being written off is ~3× what I said.** Not "a C_stat plus a pilot" but a
complete assembled budget: C_syst 2.970e-38, C_retrain 2.190e-38, C_stat 7.439e-39, C_ml 8.036e-39,
C_lateral 4.690e-39, C_total 3.878e-38, plus a *newer* 42-replica interim C_stat and six combined ROOTs.
Conclusion unchanged; the inventory in the record was wrong.

**Correction 2 — `niter` IS recorded, and that makes the case stronger.** I had written that the
provenance "was never written down." `sbatch_pet_nominal_bkgsub.sh:42` pins `NITER=2`, `:29` states
`iters = 2`, and `:14` banners **"QUARANTINED RECOIL-ONLY CROSS-CHECK LAUNCHER — NOT a publication
path"**. So those components are disqualified by three *positive* facts — `niter=2`, a non-publication
path, a 10550-bin recoil domain against 10694 — which is exactly what rule 5 asks for, instead of by an
absence. I had committed the wrong version and corrected `KNOWN_ISSUES.md` in place; the real remaining
debt is the missing **stamp**, since none of that is visible from the artifact a reader would open.

**My "transfers" argument was the forbidden form, and I rewrote it.** "Different estimator family,
therefore irrelevant" is a *disjointness assertion* — what I would have written whether or not a hidden
dependency existed. The positive form: the 5D GBDT covariance is a **closed function of an enumerated
input list containing no PET quantity** (`adopt_unified_5d.py:75,78`; `--iters 5` on `bank_uthrow_5d`),
and `NOMINAL_SEED_POLICY['niter']` is read by exactly one driver that writes nothing any 5D GBDT product
reads. Falsifiable by one new dependency, which is the point. The dependency that *does* exist runs the
other way — PET C_syst consumes `bank_uthrow_5d` — so today's re-roll is a **prerequisite** for the PET
build rather than independent of it.

**A sixth J28 site: `eavailW_covariance.py`.** Absent from `081ae4a`'s twelve files and unscoped by the
audit. `:104` loads `flux_bins` once from the CV histogram; `:232` passes it into
`extract_cross_section_nd` on every call with no per-universe override; `_y_band` (`:259`) has no flux
parameter; `:274-276` runs all 100 PPFX universes through it into `C_flux`. The fixed
`unified_throw_cov_5d.py:67` threads `d["flux"] if flux is None else flux` for exactly this reason. So
`C_flux` is understated by the mechanism I measured today. I confirmed it at the mechanism level myself
rather than taking the review's word — but it is a **code read, not run**, so no magnitude.

**The correction I owe on "how far are we."** I told him the full-event PET budget was the main gap to a
cross section plus an uncertainty. **The note quotes no PET covariance at all**:
`\petTotalMedian`/`\petTotalTrace`/`\petFourMedian` are `QUARANTINED` and referenced **0 times** in the
tex tree; only `\petRatio` (2×) and `\petClosure` (3×) are used; `sec_pet.tex:1` titles the section a
cross-**check**; the headline budget is the GBDT 5D lane. So that build buys a precision comparison the
note presently *declines* to make, and whether it is publication-blocking or discretionary is recorded
nowhere. That is a bigger question than the classification, and it is his. Also: **"170–250 GPU-h" is
not verified** — the defensible floor is **≥100 GPU-h** for C_stat alone (one train ~1 h/GPU at
`sbatch_pet_nominal_bkgsub.sh:31`, 100 replicas, full-event at `niter=3` strictly more per train).

### Two corrections to this morning's re-roll, both from reading the product instead of the launcher

Nothing was unblocked this cycle — nominal still PENDING, no reply, Steps 3–5 gated on Joseph — so
instead of idling I went back at the two things I had escalated. Both turned out to be wrong in my
favour and against it respectively.

**1. The re-roll covers 122 of the adopted 160 throws (BEN-033).** I had written, in the finding, the
ledger, the RUN_LOG and a STATUS one-liner, that its inputs were "the ensemble the **adopted**
`unified_throw_cov_5d.root` was built from." The ROOT itself says **`n_throws = 160`**;
job `56417324` processed **122**. `uthrow_slabs_5d_sb/` holds slabs **0–30** and slabs **31–39 are
gone** (~38 throws), lost from purgeable scratch after the combine ran. So the "before" sits **−2.62%**
below the adopted `sqrt_tr_unified` (and −7.21% on the mean shift).

What survives: the before→after comparison uses the *same* 122 slabs on both sides, so it is a
controlled measurement of the correction and the +316.83% / +10.19% / −0.72% figures hold. What does
not: the corrected *absolute* numbers are a 76.2% subsample, **not** drop-in replacements for the
adopted covariance. Exact replacement needs slabs 31–39 re-thrown → `OPEN_ITEMS.md` (g).

The lesson is sharper than the slip. I had *cross-checked two independent sources* — the fast combine's
globs and a STATUS run-F entry — and they agreed. But both were the wrong **kind** of source: a launcher
says what it *would* consume, the product records what it *did*, and they diverge precisely when inputs
have been lost since. Agreement between two same-kind sources bought nothing; one `TFile.Open` +
`Get("n_throws")` would have caught it in seconds. Also worth stating plainly:
`--expected-throws 0-159` resolving to 122 files is a **failed precondition**, not a detail. And Step 0
can only ever protect survivors — it does not mitigate a loss that already happened.

**2. F7 was never an open decision, and I was wrong to escalate it to Joseph as one.**
`CORRECTED_UQ_PRODUCTION_STATUS.md:73-78` predeclared the criterion before the data existed: `~floor` →
mean-centered acceptable; `>> floor` → **also produce the CV-centered variant**, report the shift either
way, **never silently drop it**. Measured on the adopted ensemble:

    ||mean_shift|| = 1.6544e-38   sampling floor sqrt_tr/sqrt(160) = 3.5266e-39   ratio 4.69x
      -> 37.1% of sqrt_tr against a 7.9% floor;  after the correction, 4.83x / 43.7%

That is `>> floor` on any reading, and the 37% is not my interpretation — `:325` recorded exactly that
figure as "NON-negligible, FEED Fable-F7 adopt decision" when the headline landed on 07-13. So
**quoting mean-centered alone is disqualified**, the CV-centered variant must exist, and the operative
`g` change is CV-centered **+0.62%** — the corrected inflation edges slightly **up**. My "g falls toward
1" emphasis described the variant the rule rules out. Only *presentation* (sole headline vs both side by
side) is genuinely his.

Net: one of the two decisions I escalated last cycle answers itself from a rule the repo wrote in
advance. That is the campaign's own standard working — and the reason to re-read the predeclaration
before escalating, not after.
