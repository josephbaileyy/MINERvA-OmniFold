# Discharge criteria for quarantine causes 1, 2, 3, 4 and 6

**Written 2026-08-11 by Session B (uncertainty construction), BEFORE any remediation work, and routed
to Session A for review before remediation begins.** The instruction that produced this document is the
right one and worth restating: *a remediation whose success condition was invented after the fact is not
a remediation.* Nothing here adopts anything, and nothing here lifts the 2026-07-12 quarantine.

Subject: the seven construction causes at `VALIDATION_LEDGER.md:65-88`. Causes 1, 2, 3, 4, 6 are this
session's; cause 5 (frozen PET weights) is Session C's; cause 7 is discussed in §1 only because its
recorded discharge does not cover the artifact this lane is gated on.

---

## 0. The framing decision, which is why no criterion could be written before

The quarantine paragraph says the old products *"used **one or more of**"* seven listed causes. That is a
statement about a **class** of products, and a class has no construction — so there was no subject for a
criterion to be about. Every attempt to write "what would discharge cause 1?" fails at the same place:
discharge for *which* matrix?

**So: discharge is a property of a (cause × artifact) pair, never of a cause alone.** A criterion below is
always read as *"cause N is discharged **for artifact X**"*, and the same cause can be discharged for one
product and open for another. §1 fixes X. This is not a technicality — §4.1 shows cause 7's recorded
discharge is for a different product than the one these macros quote, and reading the tally as a flat
"1 of 7 done" is what obscures that.

**Each criterion has four legs. All four must hold; any one failing leaves the cause OPEN.**

| leg | question | why it is separate |
|---|---|---|
| **C — code** | Is the construction path that produced X free of the defect, at a pinned revision? | Necessary, and the only leg the repo currently has for most causes. |
| **P — provenance** | Is X provably the **output** of that path — by stamp, receipt or hash — rather than merely contemporaneous with it? | The whole of BEN-083: *"prove the artifact under test is the artifact you loaded."* A code fix plus a same-week product is not evidence the product used the fix. §4.2 finds this leg is currently unsatisfiable from committed artifacts for causes 1–4. |
| **M — magnitude** | Is the numerical difference between the defective and corrected construction **measured on X's own inputs**? | This is the leg everyone skips, and it is the one that makes discharge falsifiable. Without M you cannot distinguish *"we fixed it and it did not matter"* from *"we fixed it and never ran it"* — those look identical in every document. It is also the leg with a track record: the J28 first-order estimate said "a few percent upward" and the exact answer was **+317%** on the flux block (`VALIDATION_LEDGER.md:289, 312-315`). |
| **T — test** | Is there a **power-tested** regression guard that fails if the defect is reintroduced **and** fails if the guarded object disappears? | Both directions are required. A guard asserting the *absence* of a bad construct passes vacuously when the file is deleted or renamed — the null-as-absent shape (PB2). Presence assertions are as load-bearing as absence assertions. |

**M does not require the corrected number to be small.** A measured large difference discharges the cause
just as well as a measured small one; what is forbidden is an unmeasured one. Conversely a *small* measured
difference is not a licence to skip P — a correct number produced by an unprovable path is BEN-088's
*"being right without evidence"*.

**UNRESOLVED is a permitted verdict per leg**, and must not be re-read as the nearer of PASS/FAIL.

---

## 1. The artifact, fixed before the criteria

The four `\gbdtFive*` macros are consumed in exactly one prose block, `sec_systematics.tex:162-173`
(verified: `:162`, `:164`, `:165`, `:167` — the counts in `PROCEDURE-gbdtFive-macro-update.md §1` are
right). They describe **one** object:

> **X = the adopted 5D GBDT covariance**, background-aware footing, on the 5D GBDT reported grid —
> **10,694 reported bins of `GRID_NBINS = 65856`** (`nd-unfolding/p4_lib.py:22`), currently
> `uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware{,_uthrow,_uthrow_cvcentered}.root`.

The macro values and their committed source, so the identification can be contradicted rather than trusted:

| macro | value | committed source | quantity |
|---|---|---|---|
| `\gbdtFiveBlockMedian` | `13.36` | `nd-unfolding/uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_summary.txt` → `combined sqrt-trace=4.3578e-38 median rel=13.359%`; also `VALIDATION_LEDGER.md:333` | **background-aware** syst+stat+ML block-sum median/bin |
| `\gbdtFiveAdoptTrace` | `5.81e-38` | `KNOWN_ISSUES.md` #13 (`adopted mean 5.80→5.81e-38`) | background-aware adopted mean-centered √Tr |
| `\gbdtFiveCVTrace` | `6.24e-38` | `KNOWN_ISSUES.md` #13 (`CV-centered 6.23→6.24e-38`) | background-aware CV-centered variant |
| `\gbdtFiveMeanShift` | `1.65e-38` | `VALIDATION_LEDGER.md:197` (`1.654393237996853e-38`) | joint mean-shift norm |

**This settles the open question flagged in the brief and in `PROCEDURE §4`.** `\gbdtFiveBlockMedian`
`13.36` is **not** an unsourced number and it is **not** the ledger's `13.43% → 13.61%`: it is the
background-aware block-sum median `13.359%`, and `13.43%` is that same quantity on the **non**-background-
aware sweep (`nd-unfolding/uq_5d/universe_stage2_5d/uq_universe_5d_summary.txt` → `median rel=13.432%`).
The note's own prose agrees — `sec_systematics.tex:162` says *"the **background-aware** block sum has
median per-bin uncertainty `\gbdtFiveBlockMedian`"*. So the correct conclusion is stronger than "not
established as the same quantity": **they are established as different quantities**, and the consequence
is in §4.3.

**X is not the FPS covariance.** The five-band active lateral adopted 2026-08-07 is
`uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined_activelat.root` on **266**
reported bins (`VALIDATION_LEDGER.md:105, 112`). 266 ≠ 10,694; they are different objects on different
grids. See §4.1.

---

## 2. The criteria

Notation: **C** code, **P** provenance, **M** magnitude, **T** test, as defined in §0. "Receipt" means a
committed JSON/text artifact, not a ROOT — ROOTs are `.gitignore`d as `*.root`, which is the whole of §4.2.

### Cause 1 — one-sided endpoint interpolation

**The defect.** A per-band covariance formed as a CV-centered outer product of a single endpoint,
`outer(x_{+1σ} − CV)`, instead of the mean-centered MAT form over **both** endpoints,
`mat_covariance([x_−, x_+])`; and an asymmetric nuisance interpolated from one branch only. For a ±pair
the CV-centered form adds a spurious rank-1 term that mean-centering correctly kills
(`app_statmethods.tex:300-306, 1462`).

- **C.** Every `C_syst` builder on X's path forms band covariances via `uq_math.mat_covariance` over both
  endpoints, and every asymmetric ratio goes through `uq_math.interpolate_asymmetric_ratio`. Enumerated
  by the 2026-07-12 convention-consistency sweep (`CORRECTED_UQ_PRODUCTION_STATUS.md`, *"CONVENTION FIX
  (user review round 2, 2026-07-12)"*): fixed — `eavailW_covariance.py`, `pet_systematics.py`,
  `pet_systematics_5d.py`; already correct — `analyze_universes_{nd,5d}`, `pet_lateral_band{,_5d}`,
  `unified_throw_cov`, `combine_seedscan_split`, fps. **Two sites that sweep found and did NOT fix must
  be proven OFF X's path or fixed: `pet_unified_throw_5d.py:108-111` and `pet_lateral_correction.py:118`.**
  *Satisfied by:* a committed static audit naming every module X's build invokes, with the call site and
  the convention for each — not a claim that "the sweep covered it".
- **P.** X's receipt records a passing `uq_math.require_truth_ratio_bank` inventory: **both** ± endpoints
  present for every band and an exact contiguous 100-universe flux bank.
- **M.** √Tr and per-bin median of X built both ways on **X's own bank** — one-sided CV-centered vs
  mean-centered — reported as a distribution, not a max (BEN-064). *This number does not exist anywhere.*
- **T.** Extend the existing pair-covariance test in `nd-unfolding/tests/test_uq_remediation.py` with
  (i) reintroduce the one-sided form → must FAIL; (ii) delete/rename `mat_covariance` → must FAIL rather
  than skip.

### Cause 2 — CV centering

**The defect.** Covariance taken about the CV rather than the throw/universe mean, which silently folds
the ensemble mean shift into the variance instead of reporting it.

- **C.** `uq_math.joint_throw_covariance` returns `(mat_covariance(X), mean − cv)` — the shift is
  separated by construction, not by discipline (`nd-unfolding/uq_math.py:107-117`).
- **P.** X carries the shift as its own object: `hJointMeanShift` and `TParameter joint_mean_shift_norm`
  (`unified_throw_cov.py:481`), and the CV-centered variant is a **separate file** rather than a
  silently-overwritten default (`sbatch_j28_adopt_5d.sh` passes `--out` explicitly, twice, and says why).
- **M. THIS ONE ALREADY HAS A PREDECLARED CRITERION AND IT IS SATISFIED — see §4.4 for why nobody can
  find it.** The rule was fixed *before the data* in `CORRECTED_UQ_PRODUCTION_STATUS.md`, item 1 of
  "Pending decisions / gates" (*"mean_shift convention (Fable F7)"*): measure `‖mean_shift‖` against the
  sampling floor `√Tr/√N`; `~floor` → mean-centered alone is acceptable; `≫floor` → the CV-centered
  variant must also be produced and the shift reported either way, never silently dropped. **Measured:
  4.69× the floor on the adopted ensemble, 4.83× after the flux correction — 37.1% of √Tr against a 7.9%
  floor** (`VALIDATION_LEDGER.md:303-310`). So mean-centered-only is disqualified, both variants exist,
  both are PSD, and the shift is reported. M is **MET**.
- **T.** *Absent, and this is cause 2's only real gap.* Required: a guard that the adopt path **cannot**
  emit a mean-centered-only product when `‖mean_shift‖ > k·√Tr/√N`, with `k` stated. Power-test both ways:
  suppress the CV-centered output → FAIL; remove `hJointMeanShift` entirely → FAIL (not skip).

### Cause 3 — varying estimator seeds

**The defect.** Per-throw or per-universe unfolds drawn with different estimator seeds, so run-to-run
estimator noise enters the covariance as if it were systematic spread.

- **C.** One seed threaded and stamped by `do_throws`/`do_blockunits`; `do_combine` **rejects mixed-seed
  slabs** (`unified_throw_cov.py:330-331, 370-371`).
- **P.** X's receipt records the single seed value, and `fixed_seed_null_norm` is **PRESENT** in X and
  ≤ tol. *Present*, not *absent-or-small* — see §0's T leg and §4.2.
- **M.** Two numbers, and they are different questions. (i) The **null**: repeating the CV at the
  identical seed must give exactly zero — recorded as `null 1.97e-50 << 1e-12` for the July 160-throw
  combine (`CORRECTED_UQ_PRODUCTION_STATUS.md`, `02:20 PDT 07-13` entry). **This has not been read off the
  J28-corrected full-160 product, which is the artifact that would actually be adopted.** (ii) The
  **magnitude of what varying seeds would have contributed**, which is what the criterion is about, and is
  measurable from the fixed-data estimator-seed scan already in `values.tex`
  (`\gbdtAiEstTrace` `1.306e-39`, 12 seeds) — but the ledger explicitly holds that scan *"an auxiliary
  robustness check … not part of this candidate budget"* (`VALIDATION_LEDGER.md:347-348`), so using it as
  the M leg is a decision, not a lookup. **Flagged UNRESOLVED rather than assumed.**
- **T.** Mixed-seed rejection has a test in the 16-test suite. Needs power-testing, plus a presence
  assertion on `fixed_seed_null_norm` and on the seed stamp.

### Cause 4 — scalar jitter subtraction

**The defect.** A scalar run-to-run "jitter floor" subtracted from the covariance or its trace to
compensate estimator noise — an unjustified deflation that need not preserve PSD, and which hides a
non-zero fixed-seed null instead of failing on it.

- **C.** No subtraction term anywhere on X's path; the corrected contract replaces it with a hard
  requirement that the fixed-seed null be **exactly** zero (`unified_throw_cov.py:437-447`, `--null`).
- **P.** X carries `fixed_seed_null_norm` ≤ tol **and** the launcher provably passed `--null`.
  `unified_throw_cov.py:482-483` writes the key **only if `--null` was given**, so a product built without
  the flag has no key — and a criterion phrased as *"the null norm is not large"* passes on that product
  vacuously. **This is the null-as-absent shape (PB2) sitting live inside cause 4's own evidence.** The
  criterion is therefore: *key present, and ≤ tol, with tol and its source both stated.*
- **M.** How much the old jitter subtraction was removing. A historical number exists — the 2026-07-01/02
  5D GBDT jitter-matched study gave a **jitter-corrected trace ratio 1.539** vs 4D's 2.01 and FPS's 1.295,
  with per-bin median σ ratio 0.830 (`docs/OPEN_ITEMS.md`, item 11) — but it is a *different* ensemble from
  X and cannot be transferred. **UNRESOLVED, and it is likely to stay that way for a stated reason: the
  counterfactual is not defined by any surviving specification.** The retired procedure subtracted *a
  scalar*, and no committed document records which scalar or how it was estimated. Constructing one now
  and calling the difference a measurement would be precisely the *"success condition invented after the
  fact"* this document exists to prevent.

  **BOUNDED INSTEAD, 2026-08-11, which is weaker than a measurement and is labelled as such.** Any such
  scalar can only have been an estimator-noise term, and the largest estimator-noise quantity anywhere in
  this budget is `\gbdtAiEstTrace` `1.306e-39`, the 12-seed fixed-data estimator scan (`values.tex:62`).
  Removed in quadrature from the adopted `A1 = 5.2696e-38` that is **−0.0307%** of the sqrt-trace; from
  the unified throw's `4.443674e-38`, **−0.0432%**. Taking the deliberately over-generous bound of
  estimator **and** ML-split (`\gbdtMlSplitTrace` `1.493e-39`) together, `1.9836e-39` in quadrature, gives
  **−0.0709%**. So whatever the retired subtraction did, **its effect on X is bounded below 0.1% of the
  sqrt-trace** — three orders below the J28 correction's `−9.35%` and two below the footing effect.
  Independently, the **measured** fixed-seed null on this product is `5.8223e-50`, i.e. `1.31e-12` of the
  sqrt-trace: at the fixed seed there is no jitter left to subtract, which is the corrected contract
  working as designed. **A bound is not the M leg**; it is the statement that closing M exactly would
  change nothing at the precision the note quotes, offered so the remaining gap can be priced.
- **T.** Absent in the required form. A test asserting the string `jitter` does not appear in the source
  passes if the file is deleted. Required: (i) a synthetic combine whose fixed-seed null is non-zero must
  ABORT; (ii) removing the `--null` requirement must FAIL the test; (iii) an artifact **missing**
  `fixed_seed_null_norm` must FAIL, not pass.

### Cause 6 — incomplete statistical projection

**The defect, and it has two legs that the repo's own to-do conjoins.** `docs/OPEN_ITEMS.md:62-63`:
*"Rerun the five-axis statistical replicas **and** project the full covariance as `M C_5D Mᵀ` before
rebuilding `(E_avail,W)` significances."* So:

- **6a — the operator.** A marginalized covariance built by combining per-cell standard deviations, or by
  a diagonal-only or partially-covered projection, instead of the exact linear map `C_low = M C_high Mᵀ`
  which carries every variance **and** correlation term. The corrected code states the rule in its own
  comment: *"Never sum standard deviations across marginalized cells"*
  (`nd-unfolding/eavailW_covariance.py:316-341`), and hard-fails on a shape mismatch against the reported
  mask.
- **6b — the ensemble.** The five-axis statistical replica ensemble being projected must itself be
  complete.

- **C.** `uq_math.project_covariance` (`uq_math.py:119-129`) with a full `M`, used at
  `eavailW_covariance.py:339`. **Plus a coverage guard in BOTH directions**, which is where the live hole
  is: `build_projection_M` checks 5D→4D coverage and **never 4D→5D**, so five orphan 4D-reported bins
  receive no 5D source and a one-directional guard let them win a `max` and mask a 62%-of-bins result
  (BEN-064, `FINDING-20260809-stage6-central-gate-cannot-pass.md`; the orphan bins are also recorded at
  `VALIDATION_LEDGER.md:767`). **This is an unrepaired instance of cause 6 in current code**, and any
  criterion that omits it discharges the cause while the defect is live.
- **P.** A product built by that code from a **corrected** `C_5D` statistical input exists and its receipt
  names both. **Currently unmet on both legs:** no `(E_avail,W)` covariance has been rebuilt since the fix
  (`KNOWN_ISSUES.md:357`), and the same script's own J28 flux site is code-fixed with **no number
  produced** (`KNOWN_ISSUES.md:338-349` — the sixth site, `081ae4a` touched 12 files and this was not one).
- **M.** √Tr and per-bin median of the marginalized covariance under (i) summed standard deviations and
  (ii) `M C Mᵀ`, on identical inputs; plus the orphan-bin count and the fraction of √Tr they carry.
  *Absent.*
- **T.** Projection is covered in the 16-test suite. Required additions: a fixture with a deliberate
  orphan bin in **each** direction must FAIL; and a fixture where `M` is replaced by its diagonal must
  FAIL.

---

## 3. Honest state per cause, for X

Legs are graded **MET / OPEN / UNRESOLVED**. A cause is discharged only with four METs.

**UPDATED 2026-08-11 after the construction-contract receipt** — `nd-unfolding/uq_5d/receipt_construction_contract_5d.json`, verdict **B1** against
[`PREDECLARE-20260811-construction-contract-receipt.md`](PREDECLARE-20260811-construction-contract-receipt.md).
The Provenance leg moved for causes 2, 3 and 4, but **only one hop up the chain** — see §4.7.

| cause | C | P | M | T | verdict |
|---|---|---|---|---|---|
| 1 one-sided endpoint interpolation | **MET** — path enumerated and audited: 11 modules, **no `pet_*` and no `unified_throw` on it**, so both unfixed one-sided sites are provably OFF X's path (§4.8) | PARTIAL — MAT mean-centered `1/N` printed by the combine and the ± bank inventory passed, but no committed per-band endpoint census | **OPEN for the adopted product**; the pair-level defect is now quantified in the test (one-sided overstates on an asymmetric pair) | **MET** — power-tested, mutations N1/N2 | **OPEN — C and M** |
| 2 CV centering | MET | **MET** — verified 2026-08-11 in the **adopted product** by an independent reader: `centering_convention='mean-centered'`, `upstream_joint_mean_shift_norm=1.878696733368378e-38` (job `56695424`) | **MET, on a CORRECTED number** — **5.3478×** the floor, not the recorded `4.83×`, which is the 122-throw subsample (BEN-109) | **MET** — `f7_cv_centered_required`, threshold pinned by name; N3/N4 | **OPEN — provenance only** |
| 3 varying estimator seeds | MET | **MET** — one seed `1000` across 40 throw + 36 block slabs, and `upstream_n_throws=160` now read back **from the adopted product** (job `56695424`) | **MET** — null read off **both** products: `1.9706e-50` pre-J28, `5.8223e-50` J28-corrected, tol `1e-12` | **MET** — both directions in one case (one seed accepted, mixed rejected); N5 | **OPEN — provenance only** |
| 4 scalar jitter subtraction | MET | **MET** — `fixed_seed_null_norm_checked=1` and `upstream_fixed_seed_null_norm=5.8223488501140625e-50` read back **from the adopted product** (job `56695424`) | UNRESOLVED — `1.539` is a different ensemble | **MET** — `fixed_seed_null_checked` written unconditionally; N6 caught it and nothing else did | **OPEN — M and provenance** |
| 6 incomplete statistical projection | **PARTIAL** — the `(E_avail,W)` projector's unguarded all-zero rows are now detected and reported (BEN-110); the ensemble leg and the corrected upstream input are untouched | **OPEN — no product rebuilt at all** | OPEN | **MET** for the coverage guard — numeric + static + pre-fix control; P1/P2 | **OPEN, and still furthest** |

**UPDATED 2026-08-11 after job `56695424`. READ THE PRODUCT COLUMN BEFORE READING THE VERDICTS —
the P legs above are MET for the FOOTING-MATCHED CANDIDATE, not for the product the note quotes.**
The stamps were verified in a ROOT written by the new `adopt_unified_5d.py`. The currently-quoted
X — the July `…_bkgaware_uthrow.root` behind `\gbdtFiveAdoptTrace` `5.81e-38` — was built before
the stamping existed and **carries none of them**, confirmed in the same read: all nine keys
`ABSENT`. So the honest statement is *the P leg is MET for the artifact that would replace X, and
OPEN for X as it stands.* That is §0's own (cause × artifact) rule applied to my own result, and
it is the second time today the rule has caught a claim of mine rather than someone else's.

> ## ✅ CAUSE 2 DISCHARGED 2026-08-12 — for the candidate only, by Joseph's decision
>
> Authorization: Joseph → Session A → Session B, item 1 of five (BEN-082(v)). His words:
> *"Declare Cause 2 discharged only for the footing-matched, stamp-verified J28 candidate, identified
> by exact artifact path/hash. It remains open for the currently quoted July product. Use the
> mean-centered result as headline and the CV-centered result as a conservative variant. This does not
> lift the overall quarantine."*
>
> **The artifact, by exact path and hash** — job `56720356`, COMPLETED `00:05:20`, exit `0:0`, receipt
> `nd-unfolding/uq_5d/readopt_20260811_footing/STAMPED_HASH_RECEIPT.slurm-56720356.json`:
>
> | role | path | sha256 |
> |---|---|---|
> | **headline**, mean-centered | `nd-unfolding/uq_5d/readopt_20260811_footing/stamped_bkgaware_meancentered_20260812.root` | `4f168e83eaeb4bc7191a4e13e219c7ff06556e5ad30b9df4fcc249e6720c7ec2` |
> | **conservative variant**, CV-centered | `nd-unfolding/uq_5d/readopt_20260811_footing/stamped_bkgaware_cvcentered_20260812.root` | `dbcd5359c76e5c12b97ec8819980cb11c492f051f054a50d9b0bca2bd02fb9dd` |
> | input, unified throw | `nd-unfolding/uq_5d/unified_throw_cov_5d_fluxfix_20260806_full160.root` | `4cb02ae767c887b5fc43554a8f2c4a1821d25fdf547aeeeedbe8b3d57f8b4281` |
> | input, bkgaware combined | `nd-unfolding/uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root` | `9f7b2f55d7581bb687e214e7f5a38235fd07b6d9522c2223fa3a3395c803c92a` |
>
> Launcher `nd-unfolding/sbatch_adopt_stamped_footing.sh`, executed sha256
> `18c7e4ce5a537132aded0954239800f9174184b973abbec2ebd11271479eaaab`, **verified equal to the committed
> blob before submission** because the cluster tree is 114 commits behind.
>
> **Why these artifacts had to be made rather than named.** At the moment of the instruction *no file
> satisfied it*: `adopted_*_20260811_footing.root` (A1/A2) were footing-matched and hashed but predate
> BEN-106's stamp propagation, and `STAMPTEST2` was stamped but unhashed, mean-centered only, and
> test-named. Declaring on A1/A2 while citing stamps verified on a different file is the
> invented-after-the-fact closure this document exists to prevent, so the arms were regenerated with
> stamps under adoption names. **No value moved:** predeclared `5.2696e-38` / `5.6743e-38`, measured
> `5.2696e-38` (×1.209) / `5.6743e-38` (×1.302) — branch **S1** of
> [the predeclaration](PREDECLARE-20260812-stamped-footing-adoption-candidate.md), which also allowed
> S2 (reproduction failure → discharge does **not** proceed) and S3 (UNRESOLVED). Both products stamp
> and **read back** `n_throws=160`, `joint_mean_shift_norm=1.878696733368378e-38`,
> `fixed_seed_null_norm=5.8223488501140625e-50`.
>
> **BOTH COUNTS, because one of them is the one that gets misread.**
>
> | artifact | causes discharged |
> |---|---|
> | this footing-matched, stamp-verified candidate | **1 of 7** |
> | the July product `values.tex` actually quotes | **0 of 7** |
>
> **The overall quarantine is NOT lifted, `values.tex` is untouched, and the four `\gbdtFive*` macros
> remain gated.** This is the first discharge of the 2026-07-12 quarantine and it is scoped to an
> artifact the note does not yet cite. *"One down, six to go"* is a misreading of the left-hand row.
>
> **Reason (i) for my earlier refusal is honoured, not overruled** — the P leg holds for the candidate
> and not for the quoted product, which is exactly the scope above. **Reason (ii) is settled by Joseph
> in the same decision:** mean-centered is the headline, CV-centered the conservative variant, which
> closes F7's presentation half. The row below is superseded for cause 2 and left as written for the
> record.

**NO CAUSE IS DISCHARGED, and cause 2 is the one to interrogate rather than celebrate.** On the
row above it reads four METs, which by §0 is the discharge condition. I am **not** declaring it
discharged, for two reasons that are mine to state and not mine to resolve: (i) the P leg holds
for the candidate and not for the quoted product, per the paragraph above; (ii) the F7 rule's
*presentation* half — CV-centered as sole headline versus both side by side — is recorded as
**still open** in `CORRECTED_UQ_PRODUCTION_STATUS.md`, and while my criterion did not make it a
leg, discharging a quarantine cause while the campaign's own status file says a piece of that
cause is open would be exactly the invented-after-the-fact closure this document exists to
prevent. **Declaring the first discharge of the 2026-07-12 quarantine is a decision with
publication consequences and is routed, not taken.**

**Every T leg is MET and mutation-verified.** What remains is concentrated:
causes 2, 3 and 4 need only **provenance in the adopted product**, which is one edit — BEN-106's stamp
propagation — closing the same leg for all three at once. Cause 4 additionally needs its magnitude. Cause 1
needs a static audit of X's path plus one measurement. Cause 6 needs a cluster rebuild it has never had.
**Nothing here makes adoption nearer** — `values.tex` is untouched and the quarantine stands at **zero of
seven** for this artifact.

**Cost order, cheapest first — recommended remediation sequence:** 2 → 4 → 3 → 1 → 6. Cause 2 needs one
artifact read and one test. Causes 3 and 4 need the same artifact read plus power-tested guards. Cause 1
needs a static audit and one measurement. Cause 6 needs a cluster run, a corrected upstream input, and a
code repair to the coverage guard — and its `(E_avail,W)` leg is also what gates the generator ratios this
lane owns, so it is on the critical path for two deliverables at once.

**This does not make adoption nearer than it was.** Five causes remain open for X, cause 5 is Session C's,
and §4.1 finds cause 7 is not discharged for X either. Per `PROMPTS §3` and `a0285c4`, no verification pass
changes that, and this document is not one.

---

## 4. Findings surfaced while establishing the criteria

Each is sourced to a command or a committed file, and each is stated so it can be contradicted.
BEN ids and the namespace question are in §6.

### 4.1 Cause 7's discharge is for a different product than the one these macros quote

The 2026-08-07 five-band active lateral is adopted into the **FPS** covariance, `266` reported bins
(`VALIDATION_LEDGER.md:105, 112`, `…_activelat.root`). X is the **5D GBDT** covariance, `10,694` reported
bins of `65,856` (`p4_lib.py:22`; both committed summaries state `reported bins: 10694/65856`).
`docs/OPEN_ITEMS.md:92-101` states it directly: the activelat product is the FPS covariance and *"the only
`*activelat*` product on scratch"*, while *"the **5D GBDT covariance is a different object** on a different
grid … its P4-5D lateral **has not been built**."*

Nobody claimed otherwise — the ledger's own scope note says the +9.12% is *"the change to the pre-uthrow
combined **FPS** covariance"* and that the quarantine is not lifted. **The defect is in the tally, not in
any claim.** Written as a flat list of seven with one marked DISCHARGED, it reads as *"one down, six to
go"* on whatever product the reader has in mind — and for X it is **zero of seven**, because X's lateral
replacement does not exist. That is the same shape as BEN-080: a true statement about one lane's object
read as progress on another's. **Recommendation: the cause list carries a per-artifact column, or the
DISCHARGED row names the FPS product in the row itself.** Routed to A; the ledger row is the GBDT lane's.

### 4.2 No committed artifact can prove the construction contract for X — the stamps exist only in the ROOT

Causes 1–4 are all provable **in principle** from X: `fixed_seed_null_norm`, `joint_mean_shift_norm`,
`n_throws`, `hJointMeanShift` and the per-slab seed stamps are all written
(`unified_throw_cov.py:479-484`). But `*.root` is `.gitignore`d, and the committed evidence is two summary
text files that carry **only magnitudes**:

    nd-unfolding/uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_summary.txt
      → CV, glob, reported bins, total syst √Tr, combined √Tr, five category √Tr

No seed. No null norm. No centering convention. No endpoint inventory. `git grep -l fixed_seed_null_norm`
over tracked files returns the writer, its test, one status doc and three verifier transcripts — **no
receipt for any product.** So the P leg of causes 1–4 is not merely unchecked, it is **currently
unsatisfiable from the repository**, and satisfying it requires either a cluster read of the ROOT or a
committed receipt that did not have to exist.

This is `CONVENTION-receipt-ingredients.md` (BEN-077) pointed at a construction contract rather than at a
derived number: X's √Tr ships without the ingredients that prove **how** it was built, so no reader can
contradict the claim that it was built correctly. **The cheap fix is a receipt, not a re-run** — dump the
existing `TParameter`s and slab seed stamps from X into a committed JSON. That single artifact moves the P
leg of four causes at once and is the highest-leverage item in this document.

### 4.3 The proposed J28 replacement values are footed on a different background sweep than the values they would replace

> **DECIDED 2026-08-12 by Joseph** (→ Session A → Session B, item 3; authorization path recorded per
> BEN-082(v)). **Retain background-aware.** *"When the adoption gate opens, use the footing-matched
> candidates, approximately `5.2696e-38` mean-centered and `5.6743e-38` CV-centered, subject to their
> exact receipt values. Do not rewrite the prose around a non-background-aware product."*
>
> **The §4.3 correction he specified: distinguish the block-sum effect from the adopted-value effect.**
> All three verified against `VALIDATION_LEDGER.md` in the same turn as this edit, not transcribed from
> the routing message:
>
> | quantity | effect | source |
> |---|---|---|
> | **block-sum** √Tr, non-bkgaware → bkgaware | **+0.2839%** (`4.345454e-38 → 4.357790e-38`) | ledger `:409` |
> | **adopted** mean-centered, **pre-J28** | **+0.0914%** (`5.802416e-38 → 5.807716e-38`) | ledger `:108`, `:410` |
> | **adopted** mean-centered, **post-J28** | **+0.1831%** (`5.259971e-38 → 5.2696e-38`) | ledger `:109` |
>
> The adoption's per-bin `max()` inflation transfer damps the block-sum change ~3× before J28 and ~1.5×
> after; equivalently the transmission rose from 32% to 65% (ledger `:118`). **Conflating these is not
> hypothetical — it is BEN-111**, where my own predeclared branch set was anchored on the `+0.30%`
> block-sum figure while predicting the adopted quantity, and would have recorded "no interaction" for a
> measured factor-of-two interaction. `sec_systematics.tex` and `VALIDATION_LEDGER.md:723` are corrected
> in the same commit as this note; the rounded `0.30%` is retired in favour of `0.2839%` at both sites
> **and both now carry the adopted-value numbers beside the block-sum one**, so a reader cannot pick up
> one and apply it to the other.
>
> **`subject to their exact receipt values` is his phrase and is load-bearing.** The `5.2696e-38` /
> `5.6743e-38` above are the values *printed* by job `56693207`; the artifacts that will carry them into
> the note are being regenerated with provenance stamps as job `56720356`
> ([predeclaration](PREDECLARE-20260812-stamped-footing-adoption-candidate.md)), and the adoption must
> quote that job's receipt rather than this paragraph.

Measured from committed artifacts, and it is arithmetic on operands rather than a judgement:

| | non-background-aware | background-aware |
|---|---|---|
| combined block-sum √Tr | **4.3455e-38** | **4.3578e-38** |
| combined median rel/bin | **13.432%** | **13.359%** |
| source | `uq_5d/universe_stage2_5d/uq_universe_5d_summary.txt` | `uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_summary.txt` |
| adopted mean-centered | 5.80e-38 | **5.81e-38** ← `values.tex:58` |
| adopted CV-centered | 6.23e-38 | **6.24e-38** ← `values.tex:59` |

(the 5.80/5.81 and 6.23/6.24 pairs are `KNOWN_ISSUES.md` #13's own before/after.)

The J28 replacement table (`VALIDATION_LEDGER.md:202-205`) has `old combined` = **4.3455e-38** and
`median frac/bin` starting at **13.43%** — i.e. it starts from the **non**-background-aware sweep.

**Mechanism, read from the two committed launchers rather than inferred. The two number-pairs differ in
TWO inputs, not one:**

| | launcher | `--uthrow` | `--combined` |
|---|---|---|---|
| `5.81e-38` / `6.24e-38` — what `values.tex:58-59` quotes | `sbatch_finalize_5d_bkgaware_gpu.sh:31-40` | `uq_5d/unified_throw_cov_5d.root` (pre-J28) | **passed explicitly** = the bkgaware combined |
| `5.2600e-38` / `5.6609e-38` — the proposed replacements | `sbatch_j28_adopt_5d.sh:109,111` | `…_fluxfix_20260806_full160.root` (J28-corrected ✓) | **NOT PASSED** → defaults to `uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined.root`, the **non**-bkgaware product (`adopt_unified_5d.py:76-77`) |

Verified: `grep -n -- '--combined' nd-unfolding/sbatch_j28_adopt_5d.sh` returns nothing. So one input
changed deliberately and correctly (the flux fix) and a second changed silently by falling through to a
default. The `−9.47%` reported for this pair is the sum of both changes.

**How this was found, because the method is the transferable part:** not by reading the launchers, but by
failing to reconcile `13.36` (`values.tex`) against `13.43` (ledger) as the same quantity, and then
finding that the operands `4.3578e-38` and `4.3455e-38` come from two different committed summary files.
That is BEN-077's receipt-ingredients heuristic working exactly as advertised — the defect was found by a
number failing to derive from published operands, with nobody suspecting one.

**Three consequences.**

1. Writing `5.2600e-38` / `5.6609e-38` over `5.81e-38` / `6.24e-38` conflates **two** changes: the J28
   flux correction *and* a reversion of the background footing from background-aware to CV-frozen. The
   numerical size of the second is small (+0.30% on the block sum) but it is not zero and it is not what
   the edit would claim to be doing. The footing-matched J28 change is `5.2600/5.80 − 1 = −9.31%`, not the
   `−9.47%` in `PROCEDURE §4`.
2. `\gbdtFiveBlockMedian` `13.36` would be left beside two numbers footed on a different sweep — its
   non-bkgaware counterpart is `13.43`, not `13.36`. **So it is not a macro that "may not need to change";
   it is a macro that needs to change for a reason unrelated to J28, or the other two need re-deriving on
   the bkgaware footing.** A session applying "the ledger's three replacement values" and leaving the
   fourth alone gets an internally inconsistent block either way.
3. **`sec_systematics.tex:162` contains attribution language that `PROCEDURE §2` concluded was absent.**
   §2 searched for `from / summary / rollup / artifact / ledger / taken / \ref` and correctly found none.
   But the sentence reads *"the **background-aware** block sum has median per-bin uncertainty
   `\gbdtFiveBlockMedian`"* — an attribution to a **sample and footing** rather than to a file. Swapping in
   non-bkgaware values under it is exactly BEN-087's trap, in the sentence chain BEN-087(iii) named as the
   forward-looking instance. **`PROCEDURE §2`'s "no source claim can be silently re-pointed" is wrong for
   this block and should be corrected**; §170-173's *"Repeating all 188 universe unfolds … only 0.30%"* is a
   second sentence whose subject would no longer be the adopted product.

**Predeclared, and not yet resolved:** whether the correct repair is (a) re-run the adoption with
`--combined` pointed at the bkgaware product, (b) adopt on the non-bkgaware footing and rewrite the prose
to say so, or (c) UNRESOLVED pending a footing decision that is not this session's. (a) is a job well under
12 h. I am **not** running it before A has this document, because it would be remediation before criteria —
and the choice between (a) and (b) is a defensible-alternatives question of exactly the kind §0 of the
prompts routes to Joseph.

### 4.4 The only predeclared discharge criterion any of these five causes has is cited by a line number that no longer contains it

Cause 2's F7 rule is the single instance in the repo of a discharge criterion fixed **before** the data.
Four documents cite it as `CORRECTED_UQ_PRODUCTION_STATUS.md:73-78`:

    VALIDATION_LEDGER.md:303
    docs/orchestration/FINDING-20260806-j28-reroll-exact.md:108
    docs/orchestration/PLAN-20260806-niter3-budget-and-J28-reroll.md:119
    nd-unfolding/CORRECTED_UQ_PRODUCTION_STATUS.md:47   (self-citation)

**Lines 73-78 today are the GPT doc-guardrails / code-merge paragraph.** The rule is at **112-118**.
Measured drift, one line number per commit that touched the file:

    82968d4  rule at line 66
    09e415e  rule at line 73   <- the citation was CORRECT when written
    5b7b59f  rule at line 84
    47deee6  rule at line 98
    6af0464  rule at line 108
    28d43aa  rule at line 112
    HEAD     rule at line 112

Command: `for c in …; do git show $c:nd-unfolding/CORRECTED_UQ_PRODUCTION_STATUS.md | grep -n 'mean_shift convention (Fable F7)'; done`.

**Mechanism.** That file is **prepend-ordered** — each campaign one-liner is added at the top — so *every*
line-number citation into it decays monotonically, and the citation was accurate on the day it was
written. Nobody edited anything into falsehood; five prepends did it.

**Why this is the finding and not a typo.** A reader sent to `:73-78` finds unrelated text and concludes
the criterion does not exist. That is very close to the premise this session was handed — *"five of these
causes have no recorded discharge criterion anywhere in the repo"* — which is **off by one**: cause 2 has
one, it is predeclared, and it is satisfied. Four citations pointing at the wrong text is a sufficient
explanation for why it reads as zero. Same family as BEN-087 (an attribution decaying without an edit) with
a different carrier: **the line number rather than the value**.

**Rules.** (i) Never cite a prepend-ordered document by line number; quote a unique string or add an
anchor. (ii) A citation being correct when written is not a property that survives — for an append/prepend
log, cite content. (iii) Before concluding a criterion does not exist, `grep` the *content* of the thing
you were sent to find, not only the coordinates you were given.

### 4.5 A committed launcher truncates the only log of the two numbers proposed for adoption

`nd-unfolding/sbatch_j28_adopt_5d.sh` runs both adoptions as
`python3 adopt_unified_5d.py … 2>&1 | tail -25`. The `#SBATCH --output` file therefore received **25 lines
per convention** and the rest of each adoption's stdout was destroyed at write time. This is BEN-026
verbatim, in the launcher that produced `5.2600e-38` and `5.6609e-38` — the two values every downstream
document now proposes writing into the paper.

Whether the per-bin `g` distribution, PSD eigenvalues and bin counts survived depends on where in the
output they sit, which is checkable and is not yet checked. **Cheap and worth doing before any adoption:
re-run step 4 alone from the existing corrected ROOT with the stream redirected whole.** Minutes, not
hours — the ROOT exists (`uq_5d/unified_throw_cov_5d_fluxfix_20260806_full160.root`) and `adopt_unified_5d.py`
reads only diagonals. I am not renaming or editing the launcher: it is cited provenance
(`RUNBOOK-20260807-gbdt-closeout.md:36`, ledger, RUN_LOG) and `CLAUDE.md` forbids that.

### 4.6 The `INTEGRATION_CHECKLIST` row I was told to strike as stale is LIVE, and striking it would have removed a live publication gate

This is §4.1's mechanism arriving at a concrete edit, so it belongs here rather than as a separate note.

The instruction to this session was: *"INTEGRATION_CHECKLIST.md's GATED list has at least one STALE row:
it still gates the 5D lateral on five-band coverage, which ledger :90 discharged on 2026-08-07. Verify
before editing, then fix it."* **Verified. That row is not stale.** Chain, each link from a file:

1. `docs/INTEGRATION_CHECKLIST.md:54` — *"**5D lateral**: support-limited until #16 five-band coverage."*
2. `#16` resolves to `KNOWN_ISSUES.md` item 16, *"Dump-all lateral universes are CV-support-limited"*,
   whose own status column reads **OPEN** — *"full 5-band coverage remains pending … Bank-derived
   corrected covariances must be labeled support-limited until bounded."*
3. `docs/ESTIMATOR_REGISTRY.md:29` attaches the **identical** #16 caveat to `omnifold-5d-lgbm`, naming
   its adopted covariance `uq_5d/universe_stage2_5d_bkgaware/…_bkgaware_uthrow.root` — i.e. **X**. So
   "5D lateral" means X's lateral block.
4. The 2026-08-07 discharge is on the **FPS** product, **266** reported bins
   (`VALIDATION_LEDGER.md:105, 112`). X has **10,694**. `266 ≠ 10694`.
5. `docs/OPEN_ITEMS.md:92-101` states X's *"P4-5D lateral **has not been built**"*, and its intended
   lateral inputs are purity-footed, unreceipted, from a retired launcher (`KNOWN_ISSUES` #20).

**So the row is the live publication gate on the exact product this lane is trying to unblock, and the
instructed edit would have deleted it.** The instruction was not careless — it is the predictable
reading of a seven-row cause list with one row marked DISCHARGED and no per-artifact column, which is
why §4.1 asks for the column rather than for more care.

**A genuinely stale row does exist, and it is a different one:** *"χ²/ndf 1.699 (appendix) (#4):
reconcile vs ledger 1.481 — needs recompute."* The recompute landed 2026-07-16 and **the same file
records it twice** — issue #4 is marked DONE in the table, and the Deliverables list says so explicitly.
Verified in the note rather than inferred: `values.tex:35-37` defines `\chiCombined` `1.481`,
`\chiCombinedLog` `1.468`, `\chiCombinedSubStat` `11.56`, consumed at ten sites across
`app_statmethods.tex` and `sec_results.tex`; and `grep -rn '1\.699' docs/analysis-note/*.tex` returns
exactly one hit — the `values.tex:39` comment saying the value is superseded. Struck, with the evidence,
in this commit. A third row (**FPS covariance-dependent**) had a decayed *reason* but a standing
*verdict*, and its reason is corrected in place.

**The rule.** *"Verify before editing"* was the right instruction and it is what caught this — but the
verification that worked was not re-reading the row. It was **resolving the row's own cross-reference
(`#16`) and then checking the bin counts of the two candidate products.** A row that names a gate by a
short id cannot be judged stale without following the id; and when two products' gates are described in
the same words, the discriminator has to be a number neither description contains.

### 4.7 The receipt's result, and the leg my own branch set could not see

Ran 2026-08-11 against
[`PREDECLARE-20260811-construction-contract-receipt.md`](PREDECLARE-20260811-construction-contract-receipt.md).
Receipt: `nd-unfolding/uq_5d/receipt_construction_contract_5d.json`.
**Verdict: B1 — stamps present and consistent** — on the artifacts the branch set actually named.

| stamp | pre-J28 throw ROOT | J28-corrected throw ROOT |
|---|---|---|
| `fixed_seed_null_norm` | **present**, `1.9706093906025077e-50` | **present**, `5.8223488501140625e-50` |
| `n_throws` | present, `160` | present, `160` |
| `joint_mean_shift_norm` | present, `1.654393237996853e-38` | present, `1.878696733368378e-38` |
| `hJointMeanShift` | present, `TH1D[10694]` — **separate object, not folded in** | present, `TH1D[10694]` |
| `sqrt_tr_unified` / `sqrt_tr_block` | `4.4607819710748654e-38` / `3.4032639007214586e-38` | `4.443673650575504e-38` / `3.750054526403914e-38` |
| slab seed census | one seed, **`1000`**, 40 throw + 36 block slabs, 160-throw union contiguous | same slabs (union of rescaled + native halves) |

Both null norms are **present** and 38 orders below the `1e-12` tolerance, on **both** products — so the
B2 trap did not fire, and cause 4's criterion (*key present AND ≤ tol*) is satisfied at this level rather
than passing vacuously. `1.878696733368378e-38` read back from the ROOT matches the ledger digit for digit.

**THE LEG MY BRANCH SET COULD NOT SEE, and it is the more useful half.** Every construction stamp is
**ABSENT from every adopted product** — `fixed_seed_null_norm`, `joint_mean_shift_norm` and `n_throws` are
all `{"present": false}` on all six adopted ROOTs, because `adopt_unified_5d.py:166-167` writes only
`sqrt_tr_old` and `sqrt_tr_new`. **The contract is provable for the throw ROOT and not for the covariance
the note would publish.** A consumer holding the adopted product — which *is* the publication artifact —
cannot verify causes 2, 3 or 4 from it at all; they must know to walk one hop upstream to a file whose name
appears in no receipt. That is why the table in §3 says *"MET at the throw ROOT"* rather than MET.

**My branch set was incomplete and the shape of the gap is worth stating.** B1–B4 were written over *"does
the artifact carry the stamp"*, which silently assumed **one** artifact. The chain has two hops, and the
stamps stop at the first. A branch set that enumerates outcomes for a single object cannot express *"present
upstream, absent downstream"* — so this outcome was not one of my four, and I recorded it as a finding rather
than forcing it into B1. **Predeclaring outcomes does not protect you from predeclaring them over the wrong
object**, which is the same failure as `FINDING-20260810-criteria-that-answer-a-different-question.md` one
level out: there a criterion was applied to the wrong quantity; here a branch set was scoped to the wrong
number of them. The fix is cheap and belongs to the adopt step: propagate the upstream stamps into the
adopted product, so the publication artifact carries its own contract. BEN-106.

**Two corrections to my own earlier claims, both against me.**

1. **§4.5's data-loss claim is REFUTED as a consequence, though the mechanism stands.** I said the
   `| tail -25` truncation may have destroyed the ingredients of `5.2600e-38` / `5.6609e-38`. Read whole,
   `uq_5d/j28_adopt_56429334.out` (10,000 bytes, 138 lines) **contains the entire adopt block for both
   conventions** — `bins = 10694`, the `g` census (`bins>1 2805 (26.2%) median=1.000 max=17.47` and
   `6526 (61.0%) median=1.047 max=17.65`), both `sqrt-trace old/new`, both `median frac/bin`, and both PSD
   checks (`min eig -9.351e-91`, `most-neg/max -4.87e-16` and `-3.92e-16`). Nothing needed was lost. The
   25-line window covered it **with about seven lines of margin**, which is luck rather than design — nine
   `RooUnfold` rootmap warnings alone consume nine of the twenty-five. So: **BEN-026 mechanism real, harm
   not realized, margin thin.** I was right to flag it and wrong about the outcome, and the correct
   disposition is unchanged — reproduce the stage with the stream whole rather than edit the launcher.
2. **Two of my predeclared paths were wrong, and the existence check is why that surfaced as a typo rather
   than as a purge.** I wrote `uq_5d/rescaled_20260806/adopted_*_20260806_full160.root`; the launcher sets
   `TAG="20260806_full160"` and `RESCALED="uq_5d/rescaled_${TAG}"`, so the real directory is
   `rescaled_20260806_full160`. I hand-expanded a shell variable and dropped the suffix. The first probe
   reported both files **ABSENT**, which on purgeable scratch is exactly branch B4 — *"the evidence has been
   destroyed by retention policy"* — and I was one report away from filing that. **A predeclared path
   obtained by expanding shell variables by eye is a guess, and B4 is the branch a wrong guess lands in.**
   Predeclare the `ls` as well as the path.

---

## 5. What I am asking Session A to do with this

1. **Approve or amend §0's four-leg structure and §1's identification of X** before remediation starts.
   If the four legs are wrong, everything below them is wrong in the same direction.
2. **Route §4.3 to Joseph if A agrees it is his.** It is a choice between defensible alternatives
   (re-adopt on the bkgaware footing, or adopt non-bkgaware and rewrite the prose) with no consensus,
   which is A's stated bar for mailing him. It is not a status item.
3. **Route §4.1's tally correction to the GBDT lane**, which owns that ledger row. I have not edited it.
4. **Confirm the BEN id block in §6.** The documented ranges are exhausted and that is a shared-namespace
   decision, not mine to take unilaterally.
5. **Note that §4.2's receipt is the highest-leverage single item here** — one committed JSON moves the
   provenance leg of four causes, and it needs a cluster read, not a re-run.
6. **§4.6 contradicts one instruction I was given and I want that read rather than skimmed:** the
   `INTEGRATION_CHECKLIST` row I was told to strike as stale is a **live publication gate on the exact
   product this lane is unblocking**, and I have strengthened it instead of striking it. A different row
   was genuinely stale and is struck with its evidence. If A or Joseph disagrees with that reading, the
   discriminator is one number — `266` vs `10,694` reported bins — and I would rather be corrected on it
   than have it stand unexamined.

## 6. BEN id allocation — the documented ranges are exhausted

`FINDINGS.md`'s header assigns *"the GBDT/P4 lane takes 060+; the PET/nd-unfolding lane takes 070+."*
Measured this turn: `grep -oE '^\| BEN-[0-9]{3}' docs/orchestration/FINDINGS.md | sort -u` returns
**001–046 and 060–088 continuous** — so both ranges are fully consumed and **there is no in-range id left
to take.** The two ranges have also already overlapped, which is why 070+ is occupied by both lanes.

Taking `089` is `max(existing)+1`, which is precisely the allocation the header forbids and which has
already produced one renumber (`BEN-077→061 …`) and one near-collision. So:

**RESOLVED 2026-08-11: the orchestrator bounded the blocks — `D = 090-099`, `B = 100-129`, `C = 130-159`.** The buffer this section proposed at 089–099 became D's block and is in use; nothing collided, which BEN-105 records as luck with a good outcome rather than a working process.

**This session allocated from `BEN-100+`, leaving 089–099 as a deliberate unused buffer so the block
boundary is visible rather than inferred.** Stated here rather than done silently, and routed to A for
confirmation. The six findings in §4 will take `BEN-100`–`BEN-105` once A confirms; they are written up
here in full so that nothing is lost if the block is reassigned.

BEN-080's own conclusion applies and is worth repeating rather than re-deriving: the honest form of this is
*"we are choosing to leave the BEN namespace protected by attentiveness, having noticed that it is"* — and
this document is the second time that choice has been paid for.
