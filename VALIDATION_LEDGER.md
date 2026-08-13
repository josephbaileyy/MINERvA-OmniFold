# MINERvA-OmniFold Validation Ledger

## 2026-08-11 adopted products now carry their construction contract — VERIFIED by an independent reader

Job `56695424` (`sbatch_stamp_verify.sh`), `COMPLETED` 2:54. `adopt_unified_5d.py` propagates the
upstream contract into every adopted product and **asserts the six stamps read back from the output
before printing anything**, so a COMPLETED job is itself the verification. Read again afterwards by a
**separate process** — the in-process assertion and an external read are different instruments
(BEN-088 rule vi):

| id | key | new product | the same arm built by the pre-fix code |
| --- |---|---|---|
| VL1 | `sqrt_tr_old` | `4.357790406860002e-38` | `4.357790406860002e-38` |
| VL2 | `sqrt_tr_new` | `5.269625166386846e-38` | `5.269625166386846e-38` |
| VL3 | `fixed_seed_null_norm_checked` | `1` | **ABSENT** |
| VL4 | `upstream_fixed_seed_null_norm` | `5.8223488501140625e-50` | **ABSENT** |
| VL5 | `joint_mean_shift_norm_checked` | `1` | **ABSENT** |
| VL6 | `upstream_joint_mean_shift_norm` | `1.878696733368378e-38` | **ABSENT** |
| VL7 | `n_throws_checked` | `1` | **ABSENT** |
| VL8 | `upstream_n_throws` | `160` | **ABSENT** |
| VL9 | `centering_convention` | `mean-centered` | **ABSENT** |
| VL10 | `uthrow_source` | `unified_throw_cov_5d_fluxfix_20260806_full160.root` | **ABSENT** |
| VL11 | `combined_source` | `uq_universe_5d_covariance_combined_bkgaware.root` | **ABSENT** |

**The two sqrt-traces are bit-identical across the pair, so the change is numerically inert** — it adds
provenance and moves no number. The nine `ABSENT`s are the before/after control that makes the eleven
`present`s mean something.

**Scope, and it is the whole of what this does and does not establish.** The provenance leg of causes
2, 3 and 4 is MET **for the footing-matched candidate** — a product written by the new code. The
currently-quoted X, the July `…_bkgaware_uthrow.root` behind `\gbdtFiveAdoptTrace` `5.81e-38`, predates
the stamping and **carries none of them**, which the same read confirms. So: MET for the artifact that
would replace X, OPEN for X as it stands. **No cause is discharged**, and cause 2 — which now reads four
METs — is routed rather than declared, because declaring the first discharge of the 2026-07-12
quarantine has publication consequences and because the F7 *presentation* half is still recorded open in
`CORRECTED_UQ_PRODUCTION_STATUS.md`.

## 2026-08-11 cause 1's code leg: X's build path enumerated and audited — VERIFIED-CODE

The criterion asked for *"a static audit naming every module X's build invokes, with the call site and
the convention for each — not a claim that the sweep covered it"*. Done, and committed as **executable
tests** (`Cause1PathAuditTests`) so it re-runs rather than decaying.

Transitive import closure from the four production entry points (`sweep_bank_5d`,
`analyze_universes_5d`, `unified_throw_cov_5d`, `adopt_unified_5d`) is **11 modules**. Four construct a
covariance:

| id | site | construction | convention |
| --- |---|---|---|
| VL12 | `uq_math.py:96-104` | `mat_covariance` | universe-mean centered, MAT biased `1/N` ✓ |
| VL13 | `unified_throw_cov.py:355,400,407` | `joint_throw_covariance`; `mat_covariance` over the knob ± pair and the 100 flux universes | mean-centered, shift stored separately ✓ |
| VL14 | `analyze_universes_5d.py:97-98` | `Z = D - D.mean(axis=0, keepdims=True)`; `(Z.T @ Z) / D.shape[0]` | **the same convention, inlined rather than calling `uq_math`** ✓ |
| VL15 | `analyze_universes_5d.py:107-109` | `np.outer(v, v)`, `v = 0.014 · x_CV` | the documented rank-1 target-nucleon norm add-on (`app_statmethods` eq:normband) ✓ — a legitimate outer product, not a one-sided band |

**Both one-sided sites the 2026-07-12 sweep found and did not fix are provably OFF this path**:
`pet_unified_throw_5d.py:108-111` and `pet_lateral_correction.py:118` are `pet_*` modules and **no
`pet_*` module is reachable**. They belong to the PET budget, i.e. cause 5. **`unified_throw.py:391` is
also off-path** — it uses an unbiased `1/(N−1)` rather than the MAT `1/N`, but it is a 3D legacy path
(`hXSec3D`) that nothing on X's build imports.

**So cause 1's C leg is MET for X. The audit's real yield is a hole it found in this session's own
cause-1 TEST:** that test pins `uq_math.mat_covariance`, and `analyze_universes_5d` does not call it —
it reimplements it — so the guard would have stayed green while the convention on the site that
actually built X's sweep `C_syst` changed. Now pinned directly, and mutation-verified: CV-centering that
inlined site fails the new test.

## 2026-08-11 background-aware footing re-adoption — VERIFIED-NUMERIC; both controls reproduce exactly

Job `56693207` (`sbatch_readopt_5d_bkgaware_footing.sh`), `COMPLETED`, ~14 min, four arms from **one
unchanged** throw ROOT — nothing re-thrown, nothing re-combined. Whole stream at
`nd-unfolding/uq_5d/readopt_footing_56693207.out` (no `tail`/`head`). Predeclared, with a pre-registered
value, at `docs/orchestration/PREDECLARE-20260811-bkgaware-footing-readopt.md`.
**NOTHING IS ADOPTED. The 2026-07-12 quarantine stands at zero of seven for this artifact and
`values.tex` is untouched.** This produces the footing-matched *candidate*, ready for whenever the gate
opens.

**Hash binding complete.** Read-only batch verifier `56695130` (`COMPLETED 0:0`, 1:37) stable-read and
SHA-256-bound the corrected throw ROOT, both combined-footing inputs, all four arm products, and the
whole-stream log. The eight-record receipt is
`docs/orchestration/state/readopt-footing-hash-receipt-56695130.json`; its own SHA-256 is
`b6cecc62ec97fc5db2d97b5ed7027fed3a9ebf190f0f1b16cb81f6b23703dd3d`, and it binds the committed
launcher at `cc77d8ca…`. This completes the receipt promised by the predeclaration without recomputation
or adoption; it changes no number or B2 verdict.

| id | arm | `--combined` | `sqrt_tr_old` | **`sqrt_tr_new`** | ×  | median frac/bin | PSD most-neg/max |
| --- |---|---|---|---:|---:|---|---:|
| VL16 | **A1** bkgaware, mean-centered | bkgaware | 4.3578e-38 | **5.2696e-38** | 1.209 | 13.36% → 13.57% | −3.19e-16 |
| VL17 | **A2** bkgaware, CV-centered | bkgaware | 4.3578e-38 | **5.6743e-38** | 1.302 | 13.36% → 14.02% | −3.23e-16 |
| VL18 | **C1** control, mean-centered | non-bkgaware | 4.3455e-38 | **5.2600e-38** | 1.210 | 13.43% → 13.61% | −4.87e-16 |
| VL19 | **C2** control, CV-centered | non-bkgaware | 4.3455e-38 | **5.6609e-38** | 1.303 | 13.43% → 14.09% | −3.92e-16 |

**BOTH CONTROLS REPRODUCE THE ORIGINAL RUN DIGIT FOR DIGIT** — `5.2600e-38` / `5.6609e-38`, their
`×1.210` / `×1.303`, their medians `13.43% → 13.61%` / `→ 14.09%`, and their PSD minima
`−9.351e-91` / `−8.674e-91`, all matching job `56429334`. **Branch B3 is excluded**, so the footing
diagnosis is safe and A1/A2 are legitimate candidates. The `g` census is identical across footings
(mean-centered 2805 bins >1, 26.2%, median 1.000, max 17.47; CV-centered 6526, 61.0%, 1.047, 17.65)
because `g` comes from the throw ROOT and not from `--combined` — an internal consistency check that had
to hold and does.

**The run printed BOTH block-sum medians itself, which independently confirms `\gbdtFiveBlockMedian`:**
`old=13.36%` on the bkgaware arms and `old=13.43%` on the controls. `13.36` is the background-aware
value, exactly as `sec_systematics.tex:162` says.

**The 2 × 2 completed, mean-centered, and the interaction is the result:**

| id | | non-background-aware | background-aware | **footing effect** |
| --- |---|---|---|---:|
| VL20 | **pre-J28 throws** | 5.802416e-38 | 5.807716e-38 | **+0.0914%** |
| VL21 | **J28 throws** | 5.259971e-38 | **5.2696e-38** | **+0.1831%** |
| VL22 | **J28 effect** | **−9.3486%** | **−9.2655%** | |

**The footing effect on the adopted value DOUBLES after the flux correction — ×2.004.** The
pre-registered no-interaction prediction was **5.264776e-38**; measured **5.2696e-38**, high by
**+0.0916%**, which is the pre-J28 footing effect over again — i.e. the deviation *is* the doubling and
not noise. Mechanism, consistent with the numbers: the adopted covariance is
`lateral+stat+ML + G C_vert G`, and correcting the flux drove `g` toward 1 (inflation `×1.335 → ×1.210`),
so `C_comb` carries a larger share of the total and a change to it transmits more directly — measured
transmission of the `+0.2839%` block-sum footing change rose from **32%** to **65%**.

**So the two corrections are NOT independent, and a footing-matched replacement cannot be obtained by
scaling.** Anyone applying the pre-J28 `+0.0914%` to the J28 value gets `5.2648e-38` and is wrong by
half the effect. CV-centered behaves the same way: `5.660864e-38 → 5.6743e-38`, **+0.2373%**.

**Predeclaration honesty, recorded because it bears on how the verdict was reached.** Branches B1 and B2
were both phrased against *"the +0.30% bkgaware refinement"* — which is the **block-sum** figure, while
the quantity being predicted is the **adopted** one. That is the same block-sum-vs-adopted conflation
this session found in `sec_systematics.tex:170-173`, committed in my own predeclaration. **Those two
prose thresholds are withdrawn as decision criteria**; the verdict rests on the *pre-registered numeric
value*, which was well posed and which the measurement missed by a structured, explicable amount.
**Verdict: B2 — a real interaction, escalated rather than quietly adopted.**

## 2026-08-11 the Branch C iteration-dynamics defect does NOT survive the LR anneal — VERIFIED DIAGNOSTIC, predeclared branch REPAIRED

Job `56691812` COMPLETED `0:0` in 21:45. Predeclared three-branch **before submission** at `831043d`
(`docs/orchestration/PREDECLARATION-20260811-annealed-step1-trajectory.md`), launcher
`nd-unfolding/pet/sbatch_step1_trajectory_annealed.sh`. **No training** — both arms load saved
per-iteration checkpoints and evaluate them.

**The question:** job `56525829` localized the defect to iteration dynamics on the artifact trained
2026-08-08, which predates the fit-time LR anneal adopted 2026-08-10. `KNOWN_ISSUES.md:407-443` names
that dead anneal a candidate mechanism. Nobody had run the trajectory on the annealed artifact.

### ARM 1 — CONTROL (pre-anneal `56445883`), gated on the COMMITTED `56445883` decomposition receipt

Reproduction gate **bit-exact**: `increment1` 0.648331, `push_prev` 0.967659, `push_final` 0.736746, all
`rel_dev = 0.000e+00`. So the instrument is established against a committed anchor, not against itself.

| id | it | push_prev | **e2e achieved** | required | **e2e ach/req** | sign | push | push dev | first-leg (not like-for-like) |
| --- |---:|---:|---:|---:|---:|---|---:|---:|---:|
| VL23 | 0 | 1.000000 | 1.092736 | 1.124080 | **0.9721** | ok | 1.092736 | −0.0279 | 1.0974 |
| VL24 | 1 | 1.092736 | 0.885537 | 1.028684 | **0.8608** | **WRONG** | 0.967659 | −0.1392 | 0.8896 |
| VL25 | 2 | 0.967659 | 0.761370 | 1.161650 | **0.6554** | **WRONG** | 0.736746 | −0.3446 | 0.5581 |

Verdict `RIGHT_SIGN_AT_ITER0_INVERTS_LATER`. **This supplies the end-to-end numbers the 2026-08-09 row
never had, and the wrong-sign claim at iterations 1 and 2 now holds END-TO-END, not only on the first-leg
field.** It also shows the first-leg field's bias is **not one-directional**: at iteration 0 it reports an
*overshoot* (1.0974) where end-to-end is an *undershoot* (0.9721) — it inverts the sign of the deviation
— while at iteration 2 it overstates the shortfall (0.5581 vs 0.6554) and at iteration 1 understates it
(0.8896 vs 0.8608).

### ARM 2 — TREATMENT (annealed `56563761`)

Gate A/B **`GATE_AB_PASSED`**: `A1_mc_indices_bit_exact` true (0 differing rows), `A2_truth_norm_bit_exact`
true, `B(ii)` 72/72, and **`B(i) max rel dev = 0.000000e+00`** — the saved checkpoints reproduce the
stored `weights_push` exactly, so these are the run's own weights, not a checkpoint reconstruction. (The
pre-anneal artifact's B(i) failed at 0.866 when BEN-043 was written.) Fold-forward agrees three ways:
telemetry 1.084053, recomputed from stored push 1.084053, recomputed from checkpoint 1.084053.
Trajectory gate bit-exact against its own decomposition (`0.839106 / 1.161072 / 1.084053`, all
`rel 0.000e+00`) — a **same-session self-consistency check**, weaker than ARM 1's, as predeclared.

| id | it | push_prev | **e2e achieved** | required | **e2e ach/req** | sign | push | push dev | first-leg (not like-for-like) |
| --- |---:|---:|---:|---:|---:|---|---:|---:|---:|
| VL26 | 0 | 1.000000 | 1.247812 | 1.124080 | **1.1101** | ok | 1.247812 | **+0.1101** | 1.1318 |
| VL27 | 1 | 1.247812 | 0.930486 | 0.900841 | **1.0329** | ok | 1.161072 | **+0.0329** | 1.1811 |
| VL28 | 2 | 1.161072 | 0.933666 | 0.968140 | **0.9644** | ok | 1.084053 | **−0.0356** | 0.8667 |

### The predeclared branch: REPAIRED, and the guard that would have voided it did not fire

Evaluated mechanically against the predeclaration's own criteria:

| id | predeclared test | annealed arm |
| --- |---|---|
| VL29 | iterations 1 **and** 2 sign-correct **and** `|e2e/req − 1| ≤ 0.10` | **True** (0.0329, 0.0356) |
| VL30 | any of iterations 1, 2 wrong-signed | **False** |
| VL31 | any iteration in the NO-INFORMATION band `|required − 1| < 0.02` | **False** — 0.1241 / 0.0992 / 0.0319, all discriminating |

**The predeclaration named UNRESOLVED-via-the-domain-of-validity-guard as the MOST LIKELY single
outcome**, because the annealed arm sits near `push ≈ R`. It did not fire: the tightest iteration is
`|required − 1| = 0.0319`, above the 0.02 floor. So REPAIRED is a measured branch, not the nearer of two.

**The decisive contrast is the shape of the trajectory, not one number.** Pre-anneal `push dev` runs
**−2.79% → −13.92% → −34.46%**, monotonically diverging. Annealed runs **+11.01% → +3.29% → −3.56%**, a
damped oscillation converging to within 3.6% of R. Cap saturation is **0.0 at all six iterations across
both arms**, so nothing here is a clipping artifact.

**Reading.** The defect job `56525829` localized to iteration dynamics is a property of the **retired
full-LR policy**, not of iterating as such. This is the first measurement that discriminates those two,
and it is exactly what `KNOWN_ISSUES.md:430-439` proposed as the missing fourth arm.

### Scope — what this does NOT do

Not a cross section, not an uncertainty, and it **does not by itself lift Branch C**, which is a
quotability governance state rather than a number. It discharges **no** quarantine cause; cause 5 is
untouched. It is **not** a promotion and does not authorize one. What is new at iteration 0 is a **+11.01%
overshoot** in the annealed arm, larger than the pre-anneal arm's −2.79% there — the anneal converts a
monotonic divergence into a damped oscillation rather than removing all deviation, and that overshoot is
unexplained. The ~1.3% best-vs-final checkpoint caveat (BEN-043) applies to iterations 0 and 1 in both
arms; only iteration 2 carries `final` weights. ARM 2's gate is self-consistency, so ARM 1 is what
licenses believing the instrument.

#### AMENDED 2026-08-12 — the iteration-0 overshoot is no longer "unexplained", and it is a caveat ON this verdict

Raised by the orchestrator against the text above; the answer changed the reading, so it is amended
rather than left. **The word "unexplained" is withdrawn.** Three things, in order of consequence.

**(1) `|1.1101 − 1| = 0.1101` exceeds the `≤ 0.10` window the REPAIRED branch itself uses.** The
predeclaration scopes that window to iterations 1 and 2, so iteration 0 was never tested against it and
the branch fired lawfully. But the margin is 1.01 percentage points on the branch's *own* threshold, so
had iteration 0 been in scope the verdict would have been UNRESOLVED via the predeclaration's clause 2,
not REPAIRED. **The exclusion is principled for the question asked and incidental to the question read.**
`56525829` localized the defect to *"iteration dynamics after initial feedback"*, and iteration 0 was the
correct-signed reference against which iterations 1-2 were the symptom — so a branch set built to ask
*does the defect persist* had no reason to test it. That is not the same as a branch set built to ask
*is the annealed trajectory healthy*, which is how REPAIRED invites being read.

**(2) The anneal DOES NOT ENGAGE at iteration 0, so it cannot be the cause.**
`train_fullevent_nominal.py:63-65` declares `schedule = "fit-time-anneal-after-iteration-0"`,
`applies_from_iteration = 1`; `_AnnealedMultiFold.CompileModel` (`:429-431`) forces the fit-time compile
to `fixed=True` **only** when `self._ann_iter > self.start`; and the run's own optimizer readback printed
`[gate4] LR anneal VERIFIED from the optimizer: 2 fit(s) at 0.0001, 4 at 1e-05`
(`nd-unfolding/AUTONOMOUS_LOG_20260805.md:3312`) — 6 fits over 3 iterations × 2 steps, so the 2 base-rate
fits are **iteration 0's step 1 and step 2**. Iteration 0 of the treatment artifact was therefore trained
in the *pre-anneal* configuration, at the same `1e-4`, on the same seed 42 / subsample 0 / `inputs_sha256
fa6b3463…` / 8 epochs / 2e6 events / batch 512 as the control. Sourced from the printed gate line rather
than from this lane's own predeclaration prose (BEN-087).

**(3) So iteration 0 is a DE FACTO NULL CONTROL for the treatment, and it did not reproduce.**
`push` reads **1.092736** (control) vs **1.247812** (annealed) — a gap of **0.155** at a position where
the two runs differ in *no* declared policy dimension. That is not an anneal effect; it is run-to-run
variation between two separately-trained artifacts, or an uncontrolled difference the predeclaration's
comparability table did not capture. **Nobody designated iteration 0 as a control, which is why a failed
control read as a result.**

**How big is that variation? There is no production-side answer, and this is the honest limit.** The only
committed scatter at this position is the *diagnostic* family's three byte-identical-code, identical-seed
runs, whose iteration-0 `push_mean_w_reco` are **1.0107 / 1.4555 / 1.0240** (`KNOWN_ISSUES.md:503-522`,
range 0.4448). Both arms sit inside that range and their gap is about a third of it — **suggestive, and
not an error bar for this comparison**, because the same retraction distinguishes a *"wildly unstable
diagnostic"* configuration from a *"stable production"* one and forbids quoting the diagnostic family as
a point value. And production's *"reproducible to 1.3e-4"* was established on the **endpoint** fold-forward
`dev`, not on an intermediate iteration. **No production-side reproducibility estimate exists at
iteration 0.** That gap is the reason this is a caveat and not a correction; the mechanism of the
underlying instability is recorded as OPEN in the same entry.

**What this does and does not do to REPAIRED.** Iterations 1 and 2 are computed *downstream* of iteration
0, so the same unreplicated draw is inside them. **The sign result survives and is what the verdict rests
on**: two wrong signs with monotone divergence (−2.79 → −13.92 → −34.46%) against three correct signs with
damped oscillation (+11.01 → +3.29 → −3.56%) is a qualitative difference in trajectory shape, far larger
than any draw the bracket above admits. **The MAGNITUDE of the repair does not survive as a measurement**:
it is n = 1 training run per arm, with an unmeasured between-run term of at least 0.155 in `push` at the
one position where it can be seen. So REPAIRED stands **on the signs, not on the numbers**, and no figure
in this entry may be quoted as the size of the improvement. Separating the two needs replicate trainings
at fixed policy — not run, not scheduled, and out of proportion to what the verdict is being used for.
Filed as **BEN-137**.

Receipts (all committed, digests verified equal to the cluster copies):
`STEP1_TRAJECTORY.control-prenneal.slurm-56691812.json` `d560fec7…`,
`STEP1_TRAJECTORY.slurm-56691812.json` `30b9ea3c…`,
`STEP1_DECOMPOSITION.slurm-56691812.json` `c84717e5…`,
`GATE_AB_PUSH_PROVENANCE.slurm-56691812.json` `cdffe6a1…`, under
`nd-unfolding/pet/fullevent_nominal_annealed/`.

**One harness defect found by running it on a configuration that fails the other way**: ARM 2's emitted
label is `UNDER_ACHIEVES_AT_ITER0_SAME_SIGN` with reading *"step 1 under-achieves at iteration 0"*, while
iteration 0's `e2e ach/req` is **1.1101** — it **over**-achieves by 11%. The label's third branch
(`step1_increment_trajectory.py:296-300`) keys on `|dev| > 0.10` and is **direction-blind**, so it prints
"under-achieves" for an overshoot. The trajectory numbers are unaffected; the *label* on this arm should
not be quoted. Filed as
`docs/orchestration/FINDING-20260811-trajectory-label-is-direction-blind.md`.

## 2026-08-11 F7 mean-shift ratio on the ADOPTED ensemble — VERIFIED-NUMERIC, corrects "4.83×" to 5.35×

Recomputed from the committed receipt's operands (`uq_5d/receipt_construction_contract_5d.json`) while
giving quarantine cause 2 its test leg. **The conclusion is unchanged and strengthened; the reported
number was wrong.**

| id | basis | ‖mean_shift‖ | √Tr | N | **ratio to the floor** |
| --- |---|---|---|---:|---:|
| VL32 | full-160, **pre**-J28 | 1.654393237996853e-38 | 4.4607819710748654e-38 | 160 | **4.6912×** |
| VL33 | full-160, **post**-J28 — the adopted ensemble | 1.878696733368378e-38 | 4.443673650575504e-38 | 160 | **5.3478×** |
| VL34 | 122-throw morning re-roll, post | 1.885299e-38 | 4.312442e-38 | **122** | **4.8288×** |

**`4.6912×` reproduces the campaign's `4.69×` exactly** — an independent confirmation of the F7
measurement from the receipt operands. **`4.83×` does not come from the adopted ensemble: it is the
122-throw morning re-roll** (`4.8288×`, matching to three significant figures). So the recorded
*"4.69× → 4.83×"* pairs a **160**-throw "before" with a **122**-throw "after". The like-for-like
post-J28 value on the adopted ensemble is **5.3478×**.

**This is the ledger's own warning going unapplied to a number that inherited it.** Lines just below
already say the 122-throw re-roll's *"corrected **absolute** values are a 76.2% subsample and are **not**
drop-in replacements for the adopted covariance"*, and that only the **relative** changes are controlled.
The F7 ratio is an absolute quantity and was carried across anyway.

**No verdict moves.** `5.3478 > 4.8288 > 2.0`, so the predeclared F7 rule still disqualifies a
mean-centered-only budget — more strongly than reported, not less. Supporting operands so this can be
contradicted: sampling floor `√Tr/√N = 3.513032e-39`; `‖mean_shift‖/√Tr = 42.28%` against a floor of
`100/√160 = 7.91%` (the campaign's "37.1% vs 7.9%" is the pre-J28 pair, `1.6544/4.4608 = 37.09%`, which
also reproduces).

Codified as `uq_math.mean_shift_over_floor` / `f7_cv_centered_required` with the threshold
`F7_FLOOR_MULTIPLE = 2.0`. **That threshold is a codification, not a repo decision** — the predeclared
rule is qualitative (*"~floor"* vs *"≫floor"*) and no number was ever recorded. `2.0` is placed so a shift
*at* the floor is unambiguously below it and the measured ratios unambiguously above, and deliberately
not tuned to sit just under the measured value. Routed for confirmation.

## 2026-08-11 (E_avail,W) four-generator corner ratios — VERIFIED-NUMERIC, GiBUU recovered

The one uncomputed generator ratio in `docs/INTEGRATION_CHECKLIST.md` #6 is recovered.
`3d-unfolding/genie/overlay_eavailW_band.py` re-run with all four `--gen` inputs on **one** data file;
whole stream at `3d-unfolding/genie/eavailW_band_20260811_allfour.log` (2,498 bytes, never piped through
`tail`). Predeclared at `docs/orchestration/PREDECLARE-20260811-gibuu-corner-ratio.md`; **branch G1**.

**Not gated by the 2026-07-12 quarantine, and the reason is structural rather than a judgement.** The
corner ratio is `sum_corner(data·dEa·dW) / sum_corner(gen·dEa·dW)` — a ratio of two **central-value**
integrals over 3×3 = 9 cells (`overlay_eavailW_band.py:88-108`). **No covariance enters it.** The
quarantine's own scope preserves central cross sections, and the checklist gates the `(E_avail,W)`
**significances**, which are covariance-dependent, separately. **The significances remain gated.**

| id | generator | corner integral | data corner | **data/gen** | note had | integrated σ |
| --- |---|---|---|---:|---:|---|
| VL35 | GENIE-CV | 8.7918e-39 | 1.3497e-38 | **1.535** | 1.54 | 2.4446e-38 |
| VL36 | GENIE+MEC | 8.5484e-39 | 1.3497e-38 | **1.579** | 1.58 | 2.4829e-38 |
| VL37 | NuWro | 8.6369e-39 | 1.3497e-38 | **1.563** | 1.56 | 2.3444e-38 |
| VL38 | **GiBUU** | 8.3893e-39 | 1.3497e-38 | **1.609** | **UNCOMPUTED** | 2.2227e-38 |
| VL39 | data | — | 1.3497e-38 | — | — | 3.0699e-38 |

**GiBUU lands OUTSIDE the note's 1.54–1.58 band**, so per that paragraph's own predeclared rule
(*"widen the span only if it lands outside"*) the corner span becomes **54–61%** and the band
**1.54–1.61**. `sec_eavailw.tex` updated in this commit; the `W∈[2.2,3.0)` claim extends from three
generators at 23–25% to four at **23–26%** (GiBUU 25.81% below data).

**Why it was uncomputed, measured not guessed:** `gibuu_cv_xsec_eavailW.root` is dated **2026-06-09**,
**one day after** the 2026-06-08 three-generator run — its input did not exist yet — and
`overlay_eavailW_band.py:97-98` **fails open** on a missing `--gen` file (`print MISSING` then
`continue`), so the script has always been able to emit a complete-looking three-generator table.

**The three reproduce AT THE PRECISION THE NOTE QUOTES; identity is NOT established.** The only surviving
record of the 2026-06-08 values is `ND_OMNIFOLD_RUN_LOG.md:988-990` at three significant figures, and the
data file (`excess_eavail_W.root`, **2026-07-14**) postdates them by five weeks — so a third-decimal shift
is masked by rounding. Per BEN-086, agreement at printed precision is not identity: **do not re-quote
these at more digits against the 2026-06-08 lineage.** This is why all four were recomputed *together*
rather than GiBUU alone being appended to three older numbers.

**Controls that reproduce exactly**, which is what makes the set trustworthy rather than merely printed:
GiBUU integrated `2.2227e-38` and data `3.0699e-38` against the note's own `2.22` / `3.07` and
`values.tex \sigData`; and `sec_3d.tex:151`'s ordering GiBUU `2.2227e-38` < NuWro `2.3444e-38` <
GENIE CV `2.4446e-38`.

**A normalization inconsistency was found while closing this and is deliberately NOT changed here.**
`sec_eavailw.tex` states two deficits two sentences apart in two different normalizations, both as a bare
percentage: *"underpredict … by 54–61%"* is **generator**-relative (`data/gen − 1`) while *"sit 23–26%
below the data"* is **data**-relative (`1 − gen/data`). Each matches its own arithmetic. But in a common
normalization the corner deficit is **34.9–37.8%** data-relative (or the high-W deficit is **29.8–33.6%**
generator-relative), so a reader comparing `54–61%` against `23–26%` infers a contrast of ~2.4× where the
consistent answer is ~1.5×. Choosing the convention is an authorial decision about a physics claim, so it
is routed rather than silently resolved. The ratios above are unaffected either way.

## 2026-08-11 construction-contract receipt for the 5D GBDT covariance — VERIFIED-CODE + VERIFIED-NUMERIC

Read-only stamp read, no compute, nothing adopted, `values.tex` untouched. Receipt
`nd-unfolding/uq_5d/receipt_construction_contract_5d.json` (67 KB, every key reported
present-with-value **or explicitly absent** — never omitted). Script
`nd-unfolding/receipt_construction_contract_5d.py`. Predeclared at
`docs/orchestration/PREDECLARE-20260811-construction-contract-receipt.md`; **verdict B1** on the
artifacts the branch set named.

**Why it exists.** The stamps proving the 2026-07-12 corrected contract were written by the production
code but live only in `.gitignore`d ROOTs, so *"built under the corrected contract"* was unfalsifiable
from the repository. This commits them. Provenance leg of quarantine causes 2, 3 and 4 — see
`docs/orchestration/CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md` §3, §4.7.

| id | stamp | pre-J28 throw ROOT | J28-corrected throw ROOT |
| --- |---|---|---|
| VL40 | `fixed_seed_null_norm` | **present** `1.9706093906025077e-50` | **present** `5.8223488501140625e-50` |
| VL41 | `n_throws` | `160` | `160` |
| VL42 | `joint_mean_shift_norm` | `1.654393237996853e-38` | `1.878696733368378e-38` |
| VL43 | `hJointMeanShift` | `TH1D[10694]`, separate object | `TH1D[10694]`, separate object |
| VL44 | `sqrt_tr_unified` / `sqrt_tr_block` | `4.4607819710748654e-38` / `3.4032639007214586e-38` | `4.443673650575504e-38` / `3.750054526403914e-38` |
| VL45 | estimator seed | one seed **`1000`** over 40 throw + 36 block slabs; 160-throw union contiguous | same slabs |

Both null norms **present** (not absent-and-assumed-fine, which is cause 4's live trap) and 38 orders
below the `1e-12` tolerance. `1.878696733368378e-38` reads back matching this ledger digit for digit.

**THE FOOTING MISMATCH IS NOW PROVEN FROM THE PRODUCTS, not from a launcher.**
`adopt_unified_5d.py:166` stamps `sqrt_tr_old` = the √Tr of the `--combined` input it was actually given,
so each adopted product records its own background footing:

| id | adopted product | `sqrt_tr_old` → footing | `sqrt_tr_new` |
| --- |---|---|---|
| VL46 | `…_bkgaware_uthrow.root` → `\gbdtFiveAdoptTrace` | **4.357790406860002e-38 → bkgaware** | **5.807716496958672e-38** |
| VL47 | `…_bkgaware_uthrow_cvcentered.root` → `\gbdtFiveCVTrace` | **4.357790406860002e-38 → bkgaware** | **6.236702327843976e-38** |
| VL48 | `adopted_meancentered_20260806_full160.root` → proposed | **4.345454363683128e-38 → NON-bkgaware** | **5.25997091000714e-38** |
| VL49 | `adopted_cvcentered_20260806_full160.root` → proposed | **4.345454363683128e-38 → NON-bkgaware** | **5.660863966183672e-38** |
| VL50 | `universe_stage2_5d/…_uthrow.root` (July, superseded) | **4.345454363683128e-38 → NON-bkgaware** | **5.802415620046235e-38** |

Three of the four cells of a 2 × 2 in (footing × J28) therefore already exist, and the two effects
separate exactly:

    block-sum footing effect        4.345454e-38 -> 4.357790e-38        +0.2839%
    ADOPTED mean-centered footing effect, pre-J28 (5.802416 -> 5.807716) +0.0914%
    J28 effect, FOOTING-MATCHED (both non-bkgaware, 5.802416 -> 5.259971) -9.3486%
    J28 effect as PROCEDURE §4 computed it (mixed footings)               -9.4313%

**Two consequences for anything quoting these.** (i) The correct footing-matched J28 change is
**−9.3486%**, not −9.4313%. (ii) `sec_systematics.tex:170-173`'s **`0.30%`** is the **block-sum** figure
(exactly `+0.2839%`) and the effect on the **adopted** covariance is **`+0.0914%`** — the adoption's
per-bin `max()` inflation transfer damps it about threefold. Applying the note's `0.30%` to an adopted
scale overstates the footing effect by ~3×; they are two different quantities.

**Not discharged, and not a candidate.** The empty cell (bkgaware × J28) is being filled by job
`56693207` (`sbatch_readopt_5d_bkgaware_footing.sh`, four arms, controls first), predeclared with a
pre-registered value at `docs/orchestration/PREDECLARE-20260811-bkgaware-footing-readopt.md`. No scale
here is quotable; the 2026-07-12 quarantine stands with **zero** of seven causes discharged for this
artifact.

**Gap the receipt found in itself.** Every construction stamp is **ABSENT from every adopted product**
(`fixed_seed_null_norm`, `joint_mean_shift_norm`, `n_throws` all `{"present": false}` on all six), because
`adopt_unified_5d.py:166-167` writes only the two traces. So the contract is provable for the throw ROOT
and **not** for the covariance the note would publish. BEN-106.

## 2026-08-11 cause 5's construction defect sized — VERIFIED DIAGNOSTIC, recoil, NOT QUOTABLE

**Preservation gate — VERIFIED, no scientific promotion.** HPSS transfer job `56692312` archived all
**120 selection-complete full-event detector endpoint ROOTs and their 120 Gate-3 receipts**. Manifest
`HPSS_ARCHIVE_MANIFEST.slurm-56692312.json` reports `complete=true`, **240/240** server-side HPSS MD5
matches plus size readbacks, and an empty `not_archived` list; independent reconciliation also required
240 unique names, 120 `.root` plus 120 `.json`, positive matching sizes, matching 32-hex digests, and
zero marker/log failures. Receipt:
`docs/orchestration/state/hpss-protect-p3f-complete-56692312.json`. This protects the already-satisfied
detector-sample half of cause 5 from scratch purge. It does **not** repair or discharge the still-open
joint nuisance/retraining construction half and adopts no covariance.

Cause 5 of the 2026-07-12 quarantine (below, `:65-88`) requires a **joint** nuisance/retraining
construction: `δ_u = x_u^{varied+retrained} − x_CV` as one object. The historical recoil-PET
assembly instead sums `C_syst` (from `s_u = x_frozen − CV`) and `C_retrain` (from
`Δ_u = x_retrain − x_frozen`), which keeps `outer(s,s) + outer(Δ,Δ)` and **drops the two cross
terms**. Every operand is stored per bin, so the omission is measurable.

Measured by `nd-unfolding/pet/measure_joint_vs_additive_nuisance_retrain.py` on the six committed
Phase-7 response arrays; receipt `nd-unfolding/products/pet/bkgsub/pet_joint_vs_additive_retrain.json`.
No training, no re-unfold — inference-free arithmetic on frozen arrays.

| id | universe | ‖s‖ | ‖Δ‖ | ‖joint δ‖ | additive √(‖s‖²+‖Δ‖²) | additive/joint | cos(s,Δ) |
| --- |---|---|---|---|---|---:|---:|
| VL51 | `2p2h:1` | 7.73741e-39 | 5.11033e-39 | 8.53834e-39 | 9.27270e-39 | **1.0860** | −0.165 |
| VL52 | `CCQEPauliSupViaKF:1` | 7.59828e-39 | 6.16815e-39 | 4.09545e-39 | 9.78672e-39 | **2.3897** | −0.843 |
| VL53 | `LowQ2:1` | 8.69552e-39 | 8.25841e-39 | 4.09574e-39 | 1.19922e-38 | **2.9280** | −0.885 |
| VL54 | `MaCCQE:1` | 1.02987e-38 | 1.28115e-38 | 9.48537e-39 | 1.64377e-38 | **1.7330** | −0.683 |
| VL55 | `MaRES:1` | 1.36324e-38 | 1.32354e-38 | 1.01691e-38 | 1.90005e-38 | **1.8685** | −0.714 |

**Knob-band aggregate: additive √tr `3.093207e-38` vs joint √tr `1.731571e-38` → the additive
construction OVERSTATES the joint covariance by `1.786`×.** The cross term is negative in **every**
universe, so cause 5's defect is not sign-neutral: the quarantined budget is inflated by its own
construction. Realized per-universe range **1.086–2.928** — a realized range over 5 universes, not a
fitted interval (BEN-025).

**Ingredients, so the numbers can contradict each other.** `δ` is recomputed from `x_retrain − cv`,
never from `s + Δ`; the identity `‖δ‖² = ‖s‖² + ‖Δ‖² + 2 s·Δ` holds to max relative residual
**5.144e-15** and the tool fails closed if it does not. Independent corroborations: the measurement
returns cos **−0.714** / Pearson **−0.711** for MaRES:+1 against Phase 7's separately recorded
`corr(Δ,s) = −0.71`; and the integral-level record (frozen `+1.83%` → retrained `+0.89%`, retraining
reabsorbing about half the frozen shift) independently implies a joint shift *smaller* than the frozen
one, which is what a negative cross term predicts. Tool power-tested both directions on synthetic
operands: orthogonal → 1.000000, cos −0.71 → 1.856953, cos +0.71 → 0.764719, exact cancellation →
`nan` rather than a silent pass.

**Non-comparability named here rather than in a footnote.** `flux:55` and `null` are excluded from the
aggregate. `C_syst`'s flux block is built over 100 PPFX universes, so one flux universe's `‖s‖` is not a
term in it — measurably: `flux:55`'s `‖s‖` = 2.80e-38 alone **exceeds** the published whole-flux block
√tr of 1.0604e-38. `null` is the identity-retrain training-noise control (`s ≡ 0`). The pooled value is
kept in the receipt under `all_pooled_DO_NOT_QUOTE`.

**Scope — nothing here is quotable and nothing is discharged.** These are **recoil**-representation
products, and per the 2026-08-01 full-event landing every pre-08-01 PET number is a **different
estimator**, so no magnitude transfers to the full-event budget; what transfers is the sign and rough
size of the omitted cross term, as a design input. Only the 5 knob endpoint-universes that stored both
operands are covered, against `C_syst`'s 13 bands over both endpoints, so this is **not** a restatement
of the published `C_total`. Cause 5 remains **OPEN**. Full determination, including a written discharge
criterion for cause 5 (there was none recorded anywhere):
`docs/orchestration/DETERMINATION-20260811-cause5-binding-half.md`.

## 2026-08-11 2D vs GENIE MINERvA Tune v1 chi2/ndf — VERIFIED-NUMERIC, both note values reproduce

`sec_results.tex:167` quoted "data vs tune 33.0, ours vs tune 26.5". The 33.0 was sourced
(`3d-unfolding/3D_OMNIFOLD_RUN_LOG.md:112`); **26.5 appeared nowhere else in the repo**.
Both now recomputed on frozen inputs — no unfold re-run — by
`2d-unfolding/receipt_model_chi2_2d.py`; full ingredient receipt with input SHA-256s in
`2d-unfolding/receipt_model_chi2_2d.json`.

| id | comparison | chi2 | ndf | **chi2/ndf** | quoted | reproduces |
| --- |---|---:|---:|---:|---:|---|
| VL56 | ours vs data (control) | 750.49 | 205 | **3.661** | 3.661 | yes |
| VL57 | data vs tune (control) | 6773.05 | 205 | **33.039** | 33.0 | yes |
| VL58 | ours vs tune (target) | 5430.64 | 205 | **26.491** | 26.5 | yes |

Method is unchanged from `compare_to_paper_fullcov.py:chi2_with_cov`: published
`TotalCovariance`, reported-bin mask from a positive `StatOnlyCovariance` diagonal
(205/224), `np.linalg.pinv`, ndf = n_reported = 205.

**Provenance of the gap.** 26.5 was always computed by the committed
`2d-unfolding/compare_to_models.py`, but its chi2 rows were printed by the imported
`chi2_with_cov`'s bare `print()` rather than the script's own `emit()` closure, so they never
reached `model_comp_report.txt` — which is why that committed report ends at its
"--- chi^2 in paper TotalCov ---" header with no rows. Fixed in this commit; the regenerated
report carries all three rows and independently gives 26.491.

**ndf checked, not assumed** (it is dimension-conditional in this repo). The rank-truncation
scan reproduces `2D_OMNIFOLD_RUN_LOG.md:37` exactly for ours-vs-data
(r=50 → 0.69, 73 → 1.42, 100 → 2.35, 139 → 2.79, 180 → 3.30, 205 → 3.66) and rises smoothly
with no cliff for all three comparisons. The smallest eigen-direction carries ≤0.06 % of chi2
and the smallest 10 carry 2.6–3.6 % (matching `diagnose_tension.py`'s "~3 %"), so effective
rank is **not** far below n_reported and ndf = 205 holds here.

Supporting operands (so the numbers can contradict each other): sigma_tot ours/data
`1.0115` and tune/data `0.9124`, both matching `model_comp_report.txt`, and 0.9124 matching
the shipped-ancillary normalisation the 3D tune script was validated against; pull mean/RMS
`0.089/0.598` (ours-vs-data) matching the STATUS headline; eigen-decomposition chi2 agrees
with the pinv value to ≤3.5e-9. Note `pinv`'s default rcond drops **zero** of 205 singular
values (cond 1.47e12), so the run log's "rank 204/205" is a `matrix_rank`-tolerance statement,
not what the chi2 inverse actually used.

Scope: recomputation only. This does not revalidate the unfold, and says nothing about the
covariance's adequacy — chi2/ndf ≈ 26–33 means the tune is strongly disfavored by the
published covariance, which is the note's claim, not a goodness-of-fit endorsement.

## 2026-08-09 full-event Step-1 increment trajectory — VERIFIED DIAGNOSTIC

Job `56525829` completed `0:0` in 7m55s. The hash-bound trajectory artifact
(`032f548f1b7b85fe...`) passed an independent schema/arithmetic audit and reproduced the three
committed decomposition anchors bit-exactly.

> **CORRECTED 2026-08-11 (PET lane, own row). The verdict label below is RETIRED and the
> `achieved/required` column was mislabelled — it is a FIRST-LEG-ONLY quantity that the harness itself
> marks NOT comparable to `required`.** Both corrections come from the committed
> `nd-unfolding/pet/step1_increment_trajectory.py` on `origin/main`, not from a re-run:
>
> - **`CORRECT_AT_ITER0_DEGRADES_LATER` was retired 2026-08-10** and renamed
>   **`RIGHT_SIGN_AT_ITER0_INVERTS_LATER`**. The script carries the retirement in its own
>   `verdict_label_history` (`:304-308`): *"'CORRECT' overstated a correction that end-to-end
>   UNDERSHOOTS by ~2.8% at iteration 0; the load-bearing claim was always the SIGN. Same meaning,
>   honest name."* This receipt predates the rename, carries the old string, and **means exactly the new
>   one** — it is not re-run and not rewritten.
> - **The column values 1.09735 / 0.88965 / 0.55811 are the field `r1_achieved_over_required`, which the
>   current harness renames `r1_achieved_over_required_FIRST_LEG_ONLY_NOT_LIKE_FOR_LIKE` (`:249`).** It
>   divides a first-leg average `mean_w(r1)` by an END-TO-END requirement, omitting a covariance term and
>   step 2's re-estimation (measured at +4.22% and +5.85% on the annealed arm). That is BEN-077's class
>   and it **inflates the apparent shortfall**. The like-for-like field is
>   `end_to_end_achieved_over_required`, and at iteration 0 it is **0.9721** — so **step 1 does NOT
>   overshoot at iteration 0; it undershoots by ~2.8% with the correct sign.** Anyone reading 1.09735 as
>   an overshoot is reading the wrong quantity.
> - **The end-to-end values for iterations 1 and 2 are absent from this receipt**, because the schema
>   that emitted it had no such field. They are being measured by job **56691812** (predeclared
>   `docs/orchestration/PREDECLARATION-20260811-annealed-step1-trajectory.md`), whose ARM 1 re-runs this
>   exact artifact against this exact committed decomposition receipt under the current harness. Until
>   that lands, **the wrong-sign claim at iterations 1 and 2 rests on the first-leg field** — which is
>   the field this correction says is not like-for-like. The SIGN is the surviving claim; the magnitudes
>   1.09735 / 0.88965 / 0.55811 are not to be quoted as achieved/required ratios.
>
> The scope sentence below is unaffected: this localizes a training defect to iteration dynamics after
> initial feedback, and it is not a cross section. Also unaffected: the four **operand** columns (prior
> push, achieved Step-1 ratio, required ratio) are raw measurements and stand as written — only the
> derived ratio and the label were wrong. Indexed at
> `docs/orchestration/INDEX-retracted-and-superseded-values.md`.

Verdict as originally written: **`CORRECT_AT_ITER0_DEGRADES_LATER`** — read as
`RIGHT_SIGN_AT_ITER0_INVERTS_LATER` per the correction above.

| id | iteration | prior push | achieved Step-1 ratio | required ratio | ~~achieved/required~~ **first-leg only, NOT like-for-like** | sign |
| --- |---:|---:|---:|---:|---:|---|
| VL59 | 0 | 1.000000 | **1.233512** | **1.124080** | ~~1.09735~~ (end-to-end **0.9721**) | correct |
| VL60 | 1 | 1.092736 | **0.915166** | **1.028684** | ~~0.88965~~ (end-to-end pending 56691812) | wrong |
| VL61 | 2 | 0.967659 | **0.648331** | **1.161650** | ~~0.55811~~ (end-to-end pending 56691812) | wrong |

Cap-saturated weight fraction is zero at all three iterations. Iterations 0 and 1 use checkpoint files
labelled best-epoch, but their history minima are epoch 8/8, so those are also the actual last-epoch
models; iteration 2 uses the explicit BEN-043 final checkpoint. Thus the step-1 trajectory is fully
last-epoch-faithful. Scope: this localizes a training defect to **iteration dynamics after initial
feedback**; it is not a cross section and does not lift Branch C.

## 2026-07-12 uncertainty-remediation quarantine

The entries below preserve the exact historical record, but the old 4D/5D/FPS
unified-throw adoptions, PET statistical/total budgets and precision
comparisons, `(E_avail,W)` covariance, and every significance derived from
those objects are **SUPERSEDED AND UNQUOTABLE**. Their construction used one or
more of: one-sided endpoint interpolation, CV centering, varying estimator
seeds, scalar jitter subtraction, frozen PET weights, incomplete statistical
projection, or CV-support-limited lateral selection.

Corrected 5D GBDT non-lateral/support-limited candidate products are recorded
immediately below. **Updated 2026-08-07: the selection-complete lateral
replacement now EXISTS and passed its full gate chain** — see
"2026-08-07 selection-complete five-band FPS active lateral" below. That
discharges the specific precondition this paragraph named ("CV-support-limited
lateral selection"); it does **not** by itself lift this quarantine, whose other
listed causes and whose PET / 4D-FPS / significance scope are untouched, and no
scale in this section becomes quotable on the strength of it. The recoil-PET
budget is quarantined pending a joint
nuisance--retraining construction and selection-complete detector samples. The
4D/FPS replacements and covariance-dependent generator significances remain
quarantined. Central cross
sections, closure tests, dimensional anchors, and the finalized Phase-18.2 2D
result were never invalidated by this quarantine.

### The seven causes, WITH THE ARTIFACT EACH IS DISCHARGED FOR — added 2026-08-11

**Read this table instead of the "one or more of" sentence above, which is a statement about a CLASS of
products.** A class has no construction, so a cause cannot be discharged for one: **discharge is a
property of a (cause × artifact) pair**, and the same cause can be discharged for one product and open
for another. The column was added because the flat list read as *"one down, six to go"* on whatever
product the reader had in mind, and that reading came one edit from deleting a live publication gate
(BEN-100). Criteria, four legs each, and the honest per-leg state:
[`docs/orchestration/CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md`](docs/orchestration/CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md).

| id | # | cause | state, **and for which artifact** | owner |
| --- |---|---|---|---|
| VL62 | 1 | one-sided endpoint interpolation | **OPEN** for the adopted 5D GBDT covariance (10,694 reported bins of `GRID_NBINS = 65856`) | uncertainty construction |
| VL63 | 2 | CV centering | **DISCHARGED 2026-08-12 for the footing-matched, stamp-verified candidate ONLY** (`stamped_bkgaware_meancentered_20260812.root`, sha256 `4f168e83…`; CV variant `dbcd5359…`; job `56720356`) — **still OPEN for the adopted 5D GBDT covariance that `values.tex` quotes**, which carries none of the stamps. Joseph's decision, item 1 of five; F7's presentation half settled in the same decision: mean-centered headline, CV-centered conservative variant. Counts: **1 of 7 for the candidate, 0 of 7 for the quoted artifact.** | uncertainty construction |
| VL64 | 3 | varying estimator seeds | **OPEN** for the same artifact | uncertainty construction |
| VL65 | 4 | scalar jitter subtraction | **OPEN** for the same artifact | uncertainty construction |
| VL66 | 5 | frozen PET weights | **OPEN** for the recoil-PET budget | PET |
| VL67 | 6 | incomplete statistical projection | **OPEN**, and furthest — no `(E_avail,W)` product has been rebuilt at all, and the 5D→4D coverage guard is still one-directional (BEN-064) | uncertainty construction |
| VL68 | 7 | CV-support-limited lateral selection | **DISCHARGED 2026-08-07 — for the FPS covariance ONLY**: `uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined_activelat.root`, **266** reported bins, job `56431823`, gate chain PASSED (entry below). **NOT discharged for the 5D GBDT covariance**, which is a different object on a different grid — 266 ≠ 10,694 — and whose **P4-5D lateral has not been built** (`docs/OPEN_ITEMS.md:92-101`) | FPS / P4 |

**So for the artifact the four `\gbdtFive*` macros quote, the count is ZERO of seven, not one of seven.**
Nothing in this table changes any status; it names the subject each status was always about.

## 2026-08-07 selection-complete five-band FPS active lateral — VERIFIED-NUMERIC, gate chain PASSED

Job `56431823` (`sbatch_fps_active_lateral_chain.sh`), 53:56, all four steps rc=0, on the ten
`negweight-refined` publication-footing endpoint unfolds from `56430128`. Bands: `BeamAngleX`,
`BeamAngleY`, `MuonResolution`, `Muon_Energy_MINERvA`, `Muon_Energy_MINOS` (the five genuinely
kinematic ones; `MinosEfficiency` and `GEANT_*` are weight-only and were correctly left as ordinary
universe bands).

| id | quantity | value |
| --- |---|---|
| VL69 | active lateral total, sqrt-trace | **8.10399e-39** |
| VL70 | support-limited block it replaces | 7.30356e-39 |
| VL71 | **ratio** | **1.10960 (+10.96%)** |
| VL72 | combined FPS budget before | 8.040779e-39 |
| VL73 | combined FPS budget after | **8.774217e-39 (+9.1215%)** |
| VL74 | per-bin σ ratio, 266 reported bins | min 0.7897, median 1.0071, max 1.4402 |
| VL75 | pure-sum vs subtraction residual | 3.45e-16 (tol 1e-9) |

Per band: `Muon_Energy_MINERvA` 7.8043e-39 dominates, then `Muon_Energy_MINOS` 2.1341e-39,
`MuonResolution` 4.3796e-40, `BeamAngleX` 1.1493e-40, `BeamAngleY` 9.3351e-41; total == sum of the
five (rollup identity PASS).

p4 validation `RESULT PASS` with zero fails: 266×266, finite, PSD (min/max eig −3.87e-16),
`rel_asymmetry` 0.0, dim tied to the recomputed canonical mask `23b2a2f4…`, exact 5 active + 5
support band inventories.

Receipt chain (all committed; the ROOTs are `.gitignore`d as `*.root`): manifest
`303e6ff7d6205e2c…` → `receipt_component_build.json` → `receipt_p4_validation.json` →
`receipt_active_adoption.json`; active cov `c82c6610e4943fe1…`, adopted product
`3039183cf81d8d8f…` at
`nd-unfolding/uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined_activelat.root`.

**Scope.** These are verified measurements of the lateral replacement itself. The
+9.12% is the change to the *pre-uthrow* combined FPS covariance; it is **not** a
statement about the final quoted budget, and the `+10.96%` must not be applied as
a uniform scale — the per-bin spread above (0.79 to 1.44) is the reason. The
2026-07-12 quarantine above is **not** lifted by this entry.

## 2026-08-05 Gate-2 re-issued under D1/D2 — VERIFIED, promotion still pending

Job 56344268, 55:32 on `nid004178`, `status: PASS`,
verdict `GATE2_CANONICAL_RUNTIME_PASS_INDEPENDENT_PROMOTION_PENDING`.

| id | quantity | value |
| --- |---|---|
| VL76 | `R` (step-1 class ratio) | **1.1240802949941018** |
| VL77 | R denominator | `pot_scale * sum(w_reco[pass_reco])` — the RECO leg (D1) |
| VL78 | `R_if_reco_leg_used_w_truth` (pre-D1 value) | 1.103260884167167 |
| VL79 | `R_shift_factor_vs_legacy_w_truth` | 1.018870795770713 |
| VL80 | `sum(w_reco[pass_reco])` | 16,780,549.17866151 |
| VL81 | `sum(w_truth[pass_reco])` | 17,097,211.49513244 |
| VL82 | `pass_reco` rows | 20,573,521 |
| VL83 | B-4 | RESOLVED; the legs differ on **all** 20,573,521 rows, which is expected |
| VL84 | measured target normalization | 1e6 * R = 1,124,080.5876521247 |
| VL85 | `occupied_cells` | **231** of 285 (15 pT x 18 p‖) |
| VL86 | `negative_signed_cells` | 0 |
| VL87 | refined target sha256 | `544b2f6a2451480abfe867aede35d31a07178d518754428f43b00b26793d54c9` |
| VL88 | refined target rows / bytes | 4,680,719 / 18,723,004 |
| VL89 | receipt sha256 | `336e8e27fc8afce813f3ee743c6466ea047243c6e4f457e1d040868d5800792f` |
| VL90 | refiner | `u2d.refine_stay_positive`, `refinement_is_learned_production: true` |

**Two corroborations worth recording, because each closes a way this could have been wrong.**

1. The `R` shift matches the value measured directly off the dump on 2026-08-04 — 1.018870795770713
   vs 1.01887079577071 — to twelve digits, by an independent code path (a direct npz read, no
   validator). D1's +1.887% was therefore not an artefact of the validator.
2. `occupied_cells = 231` against the pre-fix degenerate **1** of 285. The units repair is confirmed
   by the gate's own independent binned check rather than by inspecting maxima. A stray `/1000.0`
   had collapsed the grid while both guards reported success, because the domain check tests range
   membership and both grids start at 0.0, and the metrics scaled both histograms identically.

**Not quotable as a cross section.** This certifies the CONSTRUCTION of the measured target only.
Gate-4 must separately prove the nominal consumes this exact array (audit J04), and Gate-4 cannot
PASS until the D2 powered recovery closure exists — see `docs/OPEN_ITEMS.md`.

**The r1 run is bit-identical.** Job 56342333 produced the SAME target digest `544b2f6a...`, and was
superseded only because its receipt pinned a loader hash the audit repairs then moved. That is direct
evidence the loader edit was semantically inert for this path, which is why it was re-run rather than
argued about. Both superseded runs are archived under `nd-unfolding/g2_fullevent/gate2/final/`.

## 2026-07-14 corrected 5D GBDT covariance — CANDIDATE; final lateral replacement pending

- The full background-aware re-quote contains 169 vertical universes, 18
  detector/lateral universes, and one matched CV. Relative to the
  background-frozen build, `C_syst` changes by **+0.14%** in sqrt-trace and the
  combined systematic+statistical+ML covariance by **+0.2839%** (`+0.30%` as
  originally written here). This closes
  KNOWN_ISSUES #13 as a numerically negligible refinement, not a central-value
  change.
  **AMENDED 2026-08-12 per Joseph (→ Session A → Session B, item 3, BEN-082(v)):
  `+0.2839%` is the BLOCK-SUM effect and must not be read as the adopted-value
  effect, which is `+0.0914%` pre-J28 and `+0.1831%` post-J28** — the adoption's
  per-bin `max()` inflation transfer damps the block-sum change about threefold
  before J28, about 1.5-fold after. The rounded `+0.30%` is what
  `sec_systematics.tex` quoted and what BEN-111 anchored a predeclared branch set
  to, deciding a factor-of-two interaction as "no interaction"; it is spelled to
  four figures here so the two quantities cannot be silently interchanged again.
> ## ✅ J28 RESOLVED 2026-08-07 — the flux defect is corrected on the full 160-throw ensemble
>
> **The quarantine notice below is retained deliberately, not deleted** — it records why these scales were
> unquotable and what was done about it. What has changed is that the numbers are now **replaced** rather
> than merely quarantined, which is the only sanctioned way to lift it (`PLAN-20260806-…` step 5).
>
> **Provenance.** Regeneration `56427580` (array tasks 30–39, all `COMPLETED 0:0`) restored the 38 throws
> lost from purgeable scratch, taking the ensemble back to **160/160**; adoption `56429334` (31m23s, rc=0)
> then rescaled *only* the pre-J28 half and combined it with the natively-corrected half. Its fail-closed
> gate verified the split before doing any work: `160/160 throws present; unstamped 0-29, stamped 30-39`.
> The corrected ROOT `nd-unfolding/uq_5d/unified_throw_cov_5d_fluxfix_20260806_full160.root` carries
> `n_throws = 160`, read back from the file.
>
> **Full-160 before → after** (both at n=160, so this is a like-for-like comparison — the 2026-08-06
> morning pass could not provide one, having covered 122/160):
>
> | quantity | original (Φ_CV) | corrected (Φu) | change |
> |---|---|---|---|
> | `sqrt_tr_unified` | 4.4607819710748654e-38 | 4.443673650575504e-38 | **−0.38%** |
> | `joint_mean_shift_norm` | 1.654393237996853e-38 | 1.878696733368378e-38 | **+13.6%** |
>
> **Adopted totals, both mean-shift conventions** (F7 requires the CV-centered variant to exist and the
> shift to be reported either way; both are given, and both are PSD):
>
> | convention | old combined | new combined | factor | median frac/bin | bins with g>1 |
> |---|---|---|---|---|---|
> | mean-centered | 4.3455e-38 | **5.2600e-38** | ×1.210 | 13.43% → 13.61% | 2805 (26.2%), median g 1.000 |
> | CV-centered | 4.3455e-38 | **5.6609e-38** | ×1.303 | 13.43% → 14.09% | 6526 (61.0%), median g 1.047 |
>
> **⚠ FOOTING MISMATCH, measured 2026-08-11 — these two numbers are NOT drop-in replacements for the two
> in `values.tex`, and the difference is not only J28.** The pair differs in **two** inputs, one of them
> silent:
>
> | | launcher | `--uthrow` | `--combined` | block-sum √Tr, median/bin |
> |---|---|---|---|---|
> | `5.81e-38` / `6.24e-38` (`values.tex:58-59`) | `sbatch_finalize_5d_bkgaware_gpu.sh:31-40` | pre-J28 `unified_throw_cov_5d.root` | **passed** = bkgaware | **4.3578e-38**, **13.359%** |
> | `5.2600e-38` / `5.6609e-38` (this table) | `sbatch_j28_adopt_5d.sh:109,111` | J28-corrected ✓ | **NOT passed** → default = **non**-bkgaware (`adopt_unified_5d.py:76-77`) | **4.3455e-38**, **13.432%** |
>
> Verified: `grep -n -- '--combined' nd-unfolding/sbatch_j28_adopt_5d.sh` returns nothing; both summary
> files are committed under `nd-unfolding/uq_5d/universe_stage2_5d{,_bkgaware}/uq_universe_5d_summary.txt`.
> Consequences: (a) the footing-matched J28 change is `5.2600/5.80 − 1 = −9.31%`, not the `−9.47%` computed
> against the bkgaware `5.81e-38`; (b) `\gbdtFiveBlockMedian` `13.36` **is** the bkgaware median `13.359%`
> and its non-bkgaware counterpart is `13.43`, so it is not a fourth macro that can be left alone;
> (c) `sec_systematics.tex:162` says *"the **background-aware** block sum"* and `:170-173` quotes the
> `0.30%` bkgaware refinement — writing non-bkgaware values under either sentence is BEN-087's trap with a
> **sample-and-footing** attribution rather than a file one. **Found by failing to derive `13.36` from
> `13.43`** — BEN-077's receipt-ingredients heuristic, working as designed. Resolution is UNRESOLVED
> between re-adopting with `--combined` on the bkgaware product (a job well under 12 h) and adopting
> non-bkgaware with rewritten prose; that choice is not a bookkeeping one. Neither is done here and
> `values.tex` is untouched. Full chain:
> [`docs/orchestration/CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md`](docs/orchestration/CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md) §4.3.
>
> **Separately (§4.5): `sbatch_j28_adopt_5d.sh:109,111` pipe both adoptions through `| tail -25`**, so the
> only log of these two numbers was truncated at write time — BEN-026, in the launcher that produced the
> proposed replacements. The launcher is deliberately left byte-unchanged so it stays faithful to the run
> it documents; re-run step 4 alone from the existing corrected ROOT with the stream redirected whole
> before adopting.
>
> **The corrected totals are ~9% SMALLER than the values currently in `values.tex`** (`\gbdtFiveAdoptTrace`
> 5.81e-38 → 5.26e-38; `\gbdtFiveCVTrace` 6.24e-38 → 5.66e-38). That is not in tension with the Flux block
> having grown 4.2×; it **is** the mechanism. Correcting the flux raised the block-sum toward a nearly
> unchanged unified total, which drove the nonlinearity inflation `g` down toward 1 — mean-centered `g` now
> has median exactly 1.000 with only 26.2% of bins above it. The adopted covariance is
> `lateral+stat+ML + G C_vert G`, so a smaller `G` inflates the vertical block less. **The old 5.81e-38 was
> overstated precisely because the understated Flux block had inflated `g`.**
>
> **STILL NOT FINAL, and not on J28 grounds.** This section's own heading reads *"CANDIDATE; final lateral
> replacement pending"*, and lines 13-14 state that final adoption waits for the **selection-complete
> lateral**. That remains true and is unaffected by J28. `values.tex` is therefore **not** updated here;
> replacing published macros is a publication decision, not a bookkeeping one.
>
> **How far off that is, corrected by BEN-036 (2026-08-07, concurrent laterals session).** Read literally,
> "full five-band coverage remains the publication gate" sizes the remainder as the 120-task, ~700 GB
> `MNV101_ACTIVE_UNIVERSE` event-loop campaign. It is not: that campaign is **already complete on disk**
> (120/120 P3F *and* P3S per-playlist ROOTs, all ten 74.8 GB merged endpoint omnifiles, merged-input receipt
> `run_id 56090877` re-verified 10/10). The real blocker is a **footing** mismatch — the ten FPS endpoint
> unfolds ran under the driver default `--bkg-mode=purity` while the publication footing is
> `negweight-refined` — and re-running only the unfolds (~1h32m per wave of 5) reuses all 748 GB. So the
> remaining distance to a defensible `values.tex` update is **hours, not a campaign**; `56430128_[0-9]` is
> that step.
>
> **Underpinning verification:** the post-hoc rescale was shown to be an *identity* against an independent
> native computation — agreement to 1.377e-12 / 6.708e-12 max relative over all 10,694 bins on throws 120
> and 121 (`nd-unfolding/validate_rescale_identity.py`). Without that, replacing these numbers would be a
> substitution rather than a correction.

> ## ⚠ QUARANTINED 2026-07-31 — every covariance scale in this section is NOT QUOTABLE
>
> **Do not cite any sqrt-trace or median-uncertainty number below until the flux re-roll runs.**
> The PPFX flux universes feeding these products were divided by the **CV** flux integral instead
> of each universe's own `Φu` (`AUDIT-FINDINGS-20260731.md` J28 — five sites plus a fail-open).
> The Flux block inside the background-aware sweep is therefore misnormalized, and the
> unified-throw products are wrong **twice**: once through that block and again through the
> per-bin inflation `g`, which `adopt_unified_5d.py` derives from the same misnormalized throws.
>
> **What is NOT affected and remains quotable:** all central cross sections, the corrected 4D
> block-sum core, closure, the dimensional anchors, statistical and ML covariance, detector
> laterals, and the finalized 2D covariance (the 2D path always divided by `Φu` correctly).
>
> **Status.** The code fix is committed (`081ae4a`), fail-closed, and mutation-tested; new slabs
> carry a `flux_normalized` stamp and `--combine` refuses unstamped ones.
>
> **THE EXACT CORRECTED NUMBERS NOW EXIST as of 2026-08-06** (Perlmutter job `56417324`, 31 throw
> slabs / **122 throws** + 36 block units, `bank_uthrow_5d`; receipt
> `nd-unfolding/uq_5d/rescaled_20260806/j28_reroll_20260806.json`).
>
> **SCOPE, corrected later the same day — this is 122 of the adopted 160 throws (76.2%).** Read from the
> adopted ROOT directly: `n_throws = 160`, `sqrt_tr_unified = 4.4607819710748654e-38`,
> `joint_mean_shift_norm = 1.654393237996853e-38`. Slabs **31–39 of `uthrow_slabs_5d_sb/` are lost**
> (9 slabs, ~38 throws; only 0–30 survive), so the re-roll's "before" sits **−2.62%** below the adopted
> `sqrt_tr_unified` and −7.21% below its mean shift. The before → after comparison is computed from the
> same 122 slabs on both sides, so every **relative** change below is a controlled measurement of the
> correction; the corrected **absolute** values are a 76.2% subsample and are **not** drop-in
> replacements for the adopted covariance. Replacing it exactly requires re-throwing slabs 31–39.
>
> **THE RESCALE IS AN IDENTITY — VERIFIED NUMERICALLY ON PRODUCTION THROWS, 2026-08-06.** The whole J28
> remediation, and therefore any lift of this quarantine, rests on `rescale_flux_universes.py`'s claim that
> `x_corrected[i_pt,...] = x_saved[i_pt,...] / r_u[i_pt]` is an *identity* rather than an approximation.
> That claim had never been checked against an independent computation. Regenerating the lost throws
> supplied the experiment for free: array task 30 recomputed throws 120 and 121 **natively**, with a driver
> that divides by each universe's own `Φu`, while `uq_5d/rescaled_20260806/` already held the **post-hoc
> rescaled** version of the same two throws. Across all **10,694** reported bins:
>
> | throw | flux universe | max \|rel diff\| | median |
> |---|---|---|---|
> | 120 | 5 (both forms) | 1.377e-12 | 3.952e-14 |
> | 121 | 13 (both forms) | 6.708e-12 | 8.393e-13 |
>
> Agreement at floating-point noise, so the post-hoc correction reproduces a from-scratch corrected
> unfold. Two things follow. (1) The rescaled numbers above are not an approximation of the right answer,
> they *are* it — which is what makes replacing the quarantined scales legitimate rather than a
> substitution. (2) The flux universes **match** in both forms (5 and 13), which independently confirms
> that `unified_throw_cov.py:222-223` seeds per *global* throw index — so regeneration reproduces the
> original draws, verified empirically and not merely read from the source. Re-runnable:
> `nd-unfolding/validate_rescale_identity.py`.
>
> Sqrt-traces, before → after (same 122 slabs both sides):
>
> | quantity | before | after | change |
> |---|---|---|---|
> | `sqrt_tr_flux_block` | 3.892270e-39 | 1.622406e-38 | **+316.83%** |
> | `sqrt_tr_blocksum` | 3.403264e-38 | 3.750055e-38 | **+10.19%** |
> | `sqrt_tr_unified` | 4.343878e-38 | 4.312442e-38 | −0.72% |
> | `sqrt_tr_cross` | 2.699457e-38 | 2.129377e-38 | −21.12% |
> | `joint_mean_shift_norm` | 1.535143e-38 | 1.885299e-38 | +22.81% |
> | `g_mean` (mean-centered) | 1.0565550 | 1.0295687 | −2.55% |
> | `g_mean` (CV-centered) | 1.1117482 | 1.1186232 | **+0.62%** |
> | `g_max` | 22.302611 | 17.202930 | −22.87% |
>
> **The quarantine STAYS IN FORCE**, because these numbers are a *measurement*, not an adoption:
> `rescale_flux_universes.py` writes its own output and adopts nothing, and the ensemble is a 76.2%
> subsample of the adopted one. Lift it by adopting, in a commit that replaces the numbers — not by
> deleting the notice.
>
> **F7 is settled by its own predeclared rule, not open.** `CORRECTED_UQ_PRODUCTION_STATUS.md`, item 1
> of *"Pending decisions / gates"* — the paragraph beginning *"mean_shift convention (Fable F7)"* — cited
> by content because that file is prepend-ordered and every line-number citation into it decays; this one
> read `:73-78`, correct when written and pointing at unrelated text by 2026-08-11 (see
> `orchestration/CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md` §4.4). It
> fixed the criterion before the data: `~floor` → mean-centered OK; `>> floor` → also produce the
> CV-centered variant and report the shift either way, never silently drop it. On the adopted ensemble
> `||mean_shift||` is **4.69×** the sampling floor `sqrt_tr/√160` (37.1% of `sqrt_tr` against a 7.9%
> floor — the same 37% `:325` flagged as NON-negligible on 07-13), and the flux correction pushes it to
> **4.83×**. So **quoting the mean-centered variant alone is disqualified**, and the operative `g` change
> is the CV-centered **+0.62%**, not the mean-centered −2.55%. What remains open is presentation only
> (CV-centered as sole headline vs both side by side).
>
> **The first-order estimate is superseded and was not confirmed.** It suggested "a few percent
> upward" and ~+6% on the combined block; the exact block sum moved **+10.19%** and the flux block
> **+317%**, and the *total* unified sqrt-trace moved **down** 0.72%. Per the plan's predeclared
> rule 1, the exact number replaces the estimate rather than being corroborated by it.
> Interpretation, which is the physics and not just bookkeeping: dividing every universe by `Φ_CV`
> instead of its own `Φu` **removes the normalization spread the flux universes exist to carry**, so
> the Flux block was severely *understated*. Correcting it raises the block sum toward the (nearly
> unchanged) unified total, which is why the finite-throw cross term collapses 21% and `g` — a ratio
> of unified to block variance — falls toward 1. Direction is **convention-dependent**: `mean_shift`
> grew 22.8%, and CV-centering adds `shift²`, so mean-centered `g_mean` falls 2.55% while
> CV-centered `g_mean` *rises* 0.62%. Written up in
> [`FINDING-20260806-j28-reroll-exact.md`](docs/orchestration/FINDING-20260806-j28-reroll-exact.md).
>
> Sequenced jointly with the `niter=3` budget recompute (`OPEN_ITEMS.md` item (d)) so the budget is
> not built twice — see
> [`docs/orchestration/PLAN-20260806-niter3-budget-and-J28-reroll.md`](docs/orchestration/PLAN-20260806-niter3-budget-and-J28-reroll.md).
> Note the slab precondition it records was **542 files, not 365** (BEN-032).

- On 10,694 reported 5D bins, the corrected block sum has systematic
  sqrt-trace **4.3515e-38** *(quarantined)* and median relative uncertainty
  **13.235%** *(quarantined)*; after adding corrected statistical and split-ML
  blocks the corresponding values are **4.3578e-38** and **13.359%**
  *(both quarantined)*.
- The corrected unified-throw candidate uses actual asymmetric endpoints,
  one fixed estimator seed, throw-mean centering, MAT `1/N`, exact manifests,
  and no scalar jitter subtraction. The candidate mean-centered covariance is PSD
  with sqrt-trace **5.8077e-38** *(quarantined — see notice above)*. The joint
  mean shift has norm **1.654e-38** *(quarantined; the CV-centered variant's
  stored shift is itself flux-misnormalized)* and is reported separately. The
  CV-centered PSD variant, sqrt-trace **6.2367e-38** *(quarantined)*, is retained
  as a conservative alternative rather than the headline.
  `docs/analysis-note/values.tex:58` (`\gbdtFiveAdoptTrace`) quotes `5.81e-38`
  from this line and inherits the quarantine.
- Artifacts:
  `nd-unfolding/uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware{,_uthrow,_uthrow_cvcentered}.root`
  and `uq_universe_5d_summary.txt`. The dedicated estimator-only seed scan is an
  auxiliary robustness check and is not part of this candidate budget.

## 2026-07-14 recoil-PET 5D uncertainty campaign — QUARANTINED

- All five blocks share the exact corrected background-subtracted PET nominal,
  10,550-bin reported mask, and CV. The final PSD block sum has sqrt-trace
  **3.8777e-38** and median relative uncertainty **15.103%**. Its width-weighted
  4D marginal is PSD on 4,790 bins with median relative uncertainty **12.365%**.
- Component `(sqrt-trace, median relative uncertainty)` values are:
  `C_syst` (**2.9704e-38**, **7.584%**), `C_retrain`
  (**2.1896e-38**, **4.181%**), `C_ML` (**8.0364e-39**, **2.348%**),
  `C_stat` (**7.4390e-39**, **7.851%**), and `C_lateral`
  (**4.6902e-39**, **2.111%**).
- The predeclared six-band targeted retraining test found all six material.
  `C_retrain` is rank six and the identical-seed null response is only **0.008%**
  of the CV norm. However, decomposing the full endpoint shift into
  `x_frozen-CV` and `x_retrain-x_frozen` does not make their covariances
  independent. Adding the two covariance matrices omits both cross terms. The
  reported total is therefore a historical diagnostic, not a publication
  covariance.
- The detector block propagates shifted detector weights/observables through the
  corrected nominal point-cloud sample with the PET map frozen. It is therefore
  a detector-response block for the completed campaign, not a claim of
  per-universe PET retraining or shifted-cloud membership regeneration.
- The current statistical block contains 20 coherent replicas. This is complete
  for the present campaign, but the pre-publication plan is to increase it to
  100 replicas; that expansion has **not** been run.
- Artifacts and exact checks:
  `nd-unfolding/products/pet/bkgsub/pet_ctotal_bkgsub_5d_final.summary.json` and
  `pet_cretrain_bkgsub_5d.summary.json`; array products use the matching `.npz`
  names. These artifacts close the historical recoil-only campaign but are not
  quotable uncertainties. The full-event replacement requires joint
  varied+retrained endpoint shifts, a fresh statistical/ML budget, and
  selection-complete per-lateral samples.

Validation pass started 2026-06-06. Scope: whole repository, with priority on
technote-cited active results. Criterion: recompute from existing ROOT/NPZ/text
outputs where possible; rerun heavy production only when a check fails and the
smallest required rerun is clear.

## Delta pass 2026-07-02 (backfill of undocumented 2026-06-14 → 2026-07-01 work)

Numbers below are read directly from the saved artifacts (no rerun). This
pass backfills documentation for the PET capstone campaign, the truth-cloud
coverage fix, the 5D GBDT systematic covariance, and the PET 5D uncertainty
comparison — all of which had landed on disk but were never written up.

- **Truth-cloud coverage fix, full-spectrum projection (2026-06-28/29,
  commits 8cc54e9/8e79ebf/ddf4a7d)**: **PASS**.
  `nd-unfolding/products/pet/fullcloud/pointcloud_projection_summary.json`:
  event census N=**32,849,103** (pass_truth_and_reco 20,404,292,
  truth_only_miss 12,444,811); **has_cloud 32,848,929 / empty_cloud 174**
  (99.9995% coverage, up from ~72.6% pre-fix). E_avail truth-cloud
  projection vs the published unfold: frac_within **0.98784** (98.78%), RMS
  **0.08222**. W projection: frac_within **0.19694** (19.7%), RMS
  **3.23862** GeV — the cloud is NOT usable for a W projection (12-hadron
  truncation is fine for E_avail, not for W). Saturated
  (exactly-12-hadron) rows: **frac_saturated 0.023074** (2.31%,
  757,968/32,848,929 events), median E_avail bias in saturated rows
  **−0.035493**.
- **5D GBDT systematic covariance campaign (completed 2026-06-29)**:
  **PASS**. `nd-unfolding/uq_5d/universe_stage2_5d/uq_universe_5d_summary.txt`
  (written 2026-06-29): reported bins **10694/65856**; total systematic
  **sqrt-trace 4.3391e-38, median 13.298%/bin**; combined (+stat+ML)
  **sqrt-trace 4.3460e-38, median 13.433%/bin**. Per-band-group
  sqrt-trace sums: Models **9.013e-38**, Hadronic response 3.885e-38,
  Muon reconstruction 2.742e-38, Normalization 4.507e-39, **Flux
  3.875e-39**. Adding the W axis flips the dominant systematic group from
  Flux (2D/3D/4D) to GENIE Models/2p2h — Flux is now sub-dominant by more
  than an order of magnitude in trace. Coda: the 5D unified-throw check
  subsequently landed and was ADOPTED 2026-07-01/02 (jitter-corrected
  trace ratio **1.539**, far milder than 4D's 2.01); adopted covariance
  `uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined_uthrow.root`,
  adopted median per-bin fraction **13.69%** over the 10550 bins PET also
  reports (per `products/pet/unified5d/pet_vs_gbdt_uncertainty_5d_summary.json`).
- **PET 5D vs GBDT uncertainty comparison (2026-06-29/30) — INDICATIVE,
  2M-train anchor**: **PASS (comparison recomputed from saved
  covariances)**.
  `nd-unfolding/products/pet/pet_vs_gbdt_uncertainty_5d_summary.json`
  (block-sum, both engines): on the **10550** common 5D bins (GBDT reports
  144 extra), median per-bin fractional uncertainty **14.8%** (PET
  headline: clean block-sum C_syst+C_stat+C_ML + PET-native shifted-W
  lateral) vs **13.3%** (GBDT); median ratio **1.1921**; PET tighter in
  only **38.4%** of bins; vertical-only (no lateral) PET reads **14.7%**
  (not lateral-driven). **VERDICT: WORSE** — contrast the 4D verdict,
  COMPARABLE (11.8% vs 13.4%, ratio 0.9496, PET tighter in 53.6% of 4796
  bins; `pet_vs_gbdt_uncertainty_summary.json`). Both PET covariance is
  anchored to the 2M-train reweight (`pet_weights_full.npz`), which still
  carries the PET-vs-GBDT CV training gap, so this comparison is
  indicative of the method, not a final full-stats uncertainty.
  **FLAGGED, NOT ADOPTED**:
  `products/pet/pet_5d_covariance_combined_unified_wlat_summary.json`
  reports PET's own unified-throw study (160 throws, frozen reweighter)
  gives sqrt-tr unified **1.5933e-37** vs sqrt-tr block **2.7897e-38** —
  **unified/block ratio 5.711** (median per-bin sigma ratio 1.216), far
  larger than the GBDT-side 5D ratio (1.539) or the qualitative 4D
  precedent. This is a frozen-reweighter lower bound (omits the
  retraining-response nonlinearity) and is explicitly not adopted into any
  published PET 5D uncertainty pending investigation of why it is so much
  larger than the GBDT-side check.

## Delta pass 2026-06-09 (post-06-06 results, for the analysis note)

All results that landed after the 2026-06-06 pass, recomputed from saved
artifacts on the login node. All PASS; no rerun required.

- **(E_avail,W) W-resolved lateral covariance (2026-06-13, interactive job
  54391533)**: **KNOWN_ISSUES #4 CLOSED.** Rebuilt the 42-bin (E_avail,W)
  covariance with the lateral block computed DIRECTLY from the 18-universe 5D
  detector sweep (9 bands × ±1σ: Muon_Energy_MINERvA/MINOS, MuonResolution,
  MinosEfficiency, BeamAngleX/Y, GEANT_Neutron/Pion/Proton) + matched CV,
  re-inferred on the five-axis grid — replacing the 4D-marginalised transfer.
  W-resolved lateral median **2.36%/bin** (√tr 9.52e-40) vs transferred
  **1.80%** (7.99e-40): the proper block is LARGER, so adopted. C_total √tr
  8.667e-39, median **14.9%/bin**; sweep-CV vs frozen-CV marginal
  max|ratio−1|=**0.007** (validation gate). Full-cov generator significances
  (published transferred → W-resolved): full plane GENIE-CV 16.7→**19.3**σ,
  +MEC 16.1→19.0, NuWro 31.2→35.9, GiBUU >37→>40; high-W DIS corner (12 bins)
  GENIE 9.0→**8.9**, +MEC 9.2→9.2, NuWro 10.5→**15.6**, GiBUU 18.2→**22.4**σ.
  The W-resolved covariance DEEPENS the DIS-corner deficit for NuWro/GiBUU and
  leaves GENIE essentially unchanged — the physics conclusion strengthens.
  Technote (`sec_eavailw`, `sec_execsummary`) + table
  updated and rebuilt (64 pp, clean). Artifact
  `products/5d/eavailW_covariance_wlat.root` (pre-fix file untouched).
- **Merged 5D omnifile integrity**: **PASS**.
  `nd-unfolding/runEventLoopOmniFold_5D_MEFHC_universes_full.root` (133 GB) has
  no ROOT recovery flag and all four trees match the sum over the 12
  per-playlist inputs exactly (`mc_truth_denom`/`mc_signal_reco` 32,849,103;
  `mc_background` 658,227; `data` 4,119,797). The cancelled `hadd5d_uni` job
  54221741 (2026-06-09, 0s elapsed) was a duplicate submission, not a failure.
- **4D unified-throw adoption**: **PASS**. `uq_4d/unified_throw_cov_4d.root`:
  160 throws, sqrt-tr unified `3.3924e-38` vs block `1.6858e-38`, ratio
  **2.012** (documented ~2.01). Adopted combined covariance
  `uq_4d/universe_stage2_4d/uq_universe_4d_covariance_combined_uthrow.root`:
  4830 reported bins, exactly symmetric, PSD (min eig at numerical zero,
  −2.3e−16 of max), stored `sqrt_tr_new=3.8529e-38` equals the recomputed
  sqrt-trace; `sqrt_tr_old=2.0996e-38` matches the pre-adoption block sum.
- **(E_avail,W) covariance**: **PASS**. `products/5d/eavailW_covariance.root`:
  42 bins (7×6), median rel sigma **14.79%**/bin; sqrt-traces C_syst
  `8.578e-39`, C_stat `7.912e-40`, C_lateral `7.992e-40`, C_total `8.652e-39`.
  CV cross-check vs the frozen 5D product: E_avail marginal max rel diff
  **0.080%**, W marginal max **0.118%** (the "~0.1%" claim).
- **(E_avail,W) generator significances**: **PASS**. Recomputed from the saved
  covariance + generator files: high-W DIS corner (E_avail≥0.4, W≥1.8 GeV, 12
  bins) z = **8.99 / 9.20 / 10.52 / 18.22** for GENIE-CV / GENIE+MEC / NuWro /
  GiBUU (documented 9.0/9.2/10.5/18.2). Data integrated sigma `3.070e-38`;
  GiBUU integral **2.223e-38** = most deficient (regenerated GiBUU, array
  54190920).
- **PET absolute milestone**: **PASS**. PET absolute total `2.7958e-38` vs
  GBDT 4D total `3.0665e-38`, ratio **0.9117**; the `_hi` retrain gives
  `2.7507e-38` (0.8970), both as documented in `ND_OMNIFOLD_RUN_LOG.md`.
  Gate-3 closure recovered/truth **0.9884** is taken from the run log (its
  denominator is the MC-truth total, which requires the full dump; not
  recomputed here).
- **PET 4D combined budget**: **PASS**.
  `products/pet/pet_4d_covariance_combined.root` median frac per reported bin:
  C_syst 18.31%, C_stat 4.18%, C_ML 3.32%, C_lateral (transferred) 4.03%,
  **C_total 23.02%** (the "23.0% total").
- **Control plots / migration figures (new, 2026-06-09)**: generated by
  `nd-unfolding/make_control_plots.py` from the CV 5D omnifile
  (`runEventLoopOmniFold_5D_MEFHC.root`, POT scale 0.212405). Reco-level
  data/MC(sig+bkg) = **1.1203** uniformly across all five axes (rising with
  pT from 0.88 to ~1.2) — consistent with the truth-level Tune-v1 deficit.
  Truth→reco diagonal purity medians: pt 0.583, pz 0.590, eavail 0.591,
  q3 0.614, W 0.595. Products: `products/5d/control_plots.png`,
  `products/5d/migration_resolution.png`.
- **FPS pilot (new, 2026-06-09)**: full-phase-space 1A pilot chain (jobs
  54232749/54232780/54233015) — see `nd-unfolding/FPS_PILOT.md`. Driver
  regression smoke **PASS** (default path untouched). **Anchor PASS**: FPS
  unfold restricted to the published-PS block reproduces the control to
  integral 0.9995, median per-cell 1.0005, median |Δ| 0.65% (185 cells).
  Acceptance: 33.6% of fiducial CC truth rate outside published cuts
  (22.4% p∥<1.5, 11.2% θ>20°); eff<2% cells carry 27.7%. Prior swap
  (tune vs bare GENIE, after the exact 1/pot_scale no-weights correction):
  published cells median 3.0%, new cells median 5.1% / p90 22.7%.
  KNOWN QUIRK: no-`--use-weights` driver mode is globally low by pot_scale
  (unscaled MC weights into OmniFold vs scaled binning weights) — corrected
  in `fps_pilot_compare.py`, flagged as code debt.
- **FPS MEFHC battery (2026-06-10, job 54244120)**: full-statistics campaign
  stage — **anchor gate PASS**: FPS unfold restricted to the published-PS
  block vs control: integral 0.9994, per-cell median 1.0013, median |Δ|
  0.57% (185 cells). Control unfold total 3.073e-38 = the frozen production
  2D number exactly. **FPS total cross section 4.502e-38 cm²/nucleon** over
  the full tracker-fiducial muon phase space (+46% vs restricted). MEFHC
  acceptance fractions match the 1A pilot (66.4% inside, 22.3% p∥<1.5,
  11.3% θ>20°; dead-cell share 27.7%). Prior swap (corrected): published
  cells median 2.86%/p90 7.5%; extension cells median 6.27%/p90 25.4%/max
  42%. Plain closure on the extended grid: recovered/truth = 1.0000 in every
  cell (no bookkeeping/normalization bias; degenerate self-closure — the
  informative extrapolation tests are the prior swap + injected closures).
  UQ stage launched on this gate (array 54254627 → merge 54254628).
- **FPS 3-prior envelope (2026-06-10, job 54244178)**: totals MnvTune
  4.502e-38 / NuWro-shaped 4.475e-38 / bare-GENIE (corrected) 4.367e-38 —
  total spread ±1.5%. Per-cell half-spread/mean: published-PS cells median
  **2.91%** (p90 14.3%); extension cells median **7.88%**, p90 **62%**, max
  81% — large spread confined to the dead cells (catch rows/columns, lowest
  p∥ strip), the quantitative basis for tier-2 flagging.
  `products/5d/fps_prior_envelope_MEFHC.png`.
- **FPS coverage toys (2026-06-12, array 54326694 + analysis 54351540)**:
  **PASS — the FPS campaign's last validation gate.** 200 closure+bootstrap
  toys (`coverage_toy_nd.py`, npz 2D-recipe mirror) over 266 reported bins:
  mean coverage **68.93%** (target 68.27%), median 69.00%, ⟨|r|⟩ **0.792**
  (target 0.798), signed r −0.005, 16 bins <65%. Region split: published
  185 bins mean **68.46%** (14 <65%); extension 81 bins mean **70.01%**
  (slightly conservative, 2 <65%). The bootstrap band is correctly
  calibrated in BOTH regions — together with the hidden-variable closure
  PASS, the extension region is validated for two-tier reporting.
- **Ascencio fine-grid stage-1 comparison (2026-06-12, jobs 54351853 +
  `compare_ascencio_fine.py`)**: dedicated re-unfold on the UNION of their
  44-cell edges (13 E_avail × 7 q3 incl. catch bins; their per-column
  binnings tile it exactly; 4D integral 3.07e-38 = frozen anchor). All 44
  cells compared (pz<20 muon gate): ours/theirs median **1.077** (consistent
  with the super-grid 1.09/1.06), per-cell pulls vs THEIR errors median
  +0.99 with **5/44 beyond 2σ** (worst −3.2σ), diag-only χ²/ndf 81.9/44.
  Their-cov-only full χ² (6064/44) is an uninterpretable upper bound: their
  strong correlations amplify the coherent ~8% offset that OUR covariance
  absorbs (super-grid full-cov χ²/ndf 1.68/2 stands as the quantitative
  consistency statement). Stage 2 (sweep on this binning) required before
  quoting a fine-grid χ². Artifacts:
  `products/4d/xsec_4d_MEFHC_ascencio_fine.root`,
  `products/4d/ascencio_fine_compare.png`.
- **FPS combined covariance + unified-throw adoption (2026-06-12, jobs
  54314362/54325576-79, throws 54314368-71)**: the full-phase-space UQ stage
  is COMPLETE. Block-sum: C_syst median 7.27%/bin (rank 144/266, √tr
  8.027e-39; per-bin medians Flux-led at 5.01%, but the TRACE is dominated by
  Muon_Energy_MINERvA √tr 7.0e-39 — the energy scale moving the large low-p∥
  extension cross section, an FPS-specific feature); + norm 1.4% + C_stat
  0.669% (100 bootstraps) + C_ML 0.357% (24 splits) → combined median
  7.33%/bin, rank 222/266, √tr 8.040e-39. Unified throw (160 joint throws on
  the validated miss-pinned bank): √tr ratio unified/block **1.301 raw /
  1.295 jitter-corrected** (vs ×2.01 in 4D); cross-term 83.2% of block;
  jitter floor ×10 below signal. **ADOPTED** (4D-style per-bin max()
  σ-inflation onto the sweep's vertical block): median g=1.000, 39.5% of
  bins inflated, max g=5.93; final covariance **median 8.19%/bin**, √tr
  9.724e-39 (×1.209), PSD exact (0 negative eigenvalues). Artifacts:
  `uq_fps/universe_stage2_fps/uq_universe_fps_covariance_combined[_uthrow].root`,
  `uq_fps/unified_throw_cov_fps.root`.
- **PET-bank reassessment (2026-06-12, jobs 54330164/54330166)**: **KNOWN_ISSUES
  #12 PET residual CLOSED.** `bank_uthrow` regenerated from the merged 5D file
  with the post-fix dump (miss-row rhos pinned to 1.0); alignment gate PASS
  (w_truth bit-identical over all 32,849,103 rows). `pet_systematics.py` re-run,
  everything else unchanged: C_syst median **18.31% → 8.24%** (the old bank's
  mangled miss-row ratios had inflated it ×2.2); C_stat 4.18% and C_ML 3.32%
  IDENTICAL to the published file (bank-independent blocks = control); clean
  C_total **11.66%** vs published 23.02% (rebank file carries no lateral block;
  adding the transferred 4.03% lateral ⇒ ≈12.3%). Direction: the published
  budget was conservative (over-covered) — no result invalidated, but the
  technote PET-budget numbers should be revised to the rebank values.
  Artifact `products/pet/pet_4d_covariance_combined_rebank.root` (published
  file untouched).
- **LE→ME beam-evolution shape comparison (2026-06-11, qualitative)**:
  `compare_le_evolution.py`, shapes only (fluxes differ — no χ²). Filkins
  2002.12496 vs our 4D-product marginals: LE/ME shape ratio median 1.196
  (pT, 13/13 bins) and 1.265 (p∥, 12/12 bins) — the ME shape is harder in
  p∥, as expected from ⟨Eν⟩ 3.5→6 GeV. Rodrigues 1511.05944 (E_avail,q3)
  rebinned onto our coarse grid (edges nest exactly; strict coverage mask):
  per-bin LE/ME shape ratios 0.89/1.14/0.94 (q3 0.4–0.6, LE-covered
  E_avail<0.4) and 0.73/0.97/1.11/0.90 (q3 0.6–0.8, full 0–0.8) — LE softer
  at low E_avail in the highest-q3 slice. q3<0.4 has too little complete LE
  coverage after rebinning to compare. Data: `nd-unfolding/reference_le/`;
  figure `products/4d/le_evolution_compare.png`.
- **FPS hidden-variable closure (2026-06-11, job 54326695)**: **PASS.**
  Gaussian truth bump injected in true E_avail (A=0.3, c=0.3 GeV, s=0.15 GeV;
  injected mean factor 1.0360) on closure pseudo-data; the 2D FPS unfold
  (extended grid, blind to E_avail) recovers it per cell
  (hXSecND/hClosureRefND): published-PS cells (185) median |dev| **0.17%**,
  p90 0.65%, max 2.93%; extension cells (81 nonzero of 100) median **0.77%**,
  p90 3.04%, max **4.05%** — both regions well inside the tier-2 3-prior band
  (medians 2.9%/7.9%). Whole-grid closure median 1.0011, max|dev| 4.05%.
  Driver hidden-axis mode + `fps_extension_validation.py` region split;
  artifact `products/5d/closure_2d_FPS_hidden_eavail_MEFHC.root`.
- **Ascencio bin-identical cross-check (2026-06-10)**: **PASS (consistent)**.
  Supplemental data found in the public arXiv source tarball of 2110.13372
  (44 cells + full covariance → `3d-unfolding/genie/
  ascencio_2110.13372_supplemental.txt`, cov exactly symmetric).
  `compare_ascencio_fullcov.py`: maximal common grid = 2 super-cells
  (Eavail<0.4 in q3 [0.4,0.6) and [0.6,1.2)); ours/Ascencio = 1.092 and
  1.063 (pulls 1.29σ, 0.86σ); full-cov χ²/ndf = **1.68/2, p = 0.432**
  (diag-only 2.40/2). Our side: frozen 4D product + adopted unified-throw
  combined covariance, (pT,pz)-marginalised with pz<20 GeV mirroring the
  Ascencio muon gate. Caveats recorded in the script header (shared MINERvA
  systematics treated as independent; pμ≈pz at the 20 GeV edge).
  `products/4d/ascencio_fullcov_compare.png`.
- **Driver no-weights normalization fix verification (2026-06-10, job
  54271042)**: **PASS — KNOWN_ISSUES #1 closed.** Driver now always passes
  the POT-scaled weights to OmniFold (no-`--use-weights` mode previously fed
  unit weights, letting the classifier absorb the normalization gap while
  the binning re-applied pot_scale → globally low by pot_scale). Both
  bare-GENIE FPS unfolds re-run with the fixed driver and the 1/pot_scale
  corrections REMOVED from `fps_pilot_compare.py`/`fps_prior_envelope.py`:
  1A anchor 0.9995/0.65% reproduced; MEFHC tune/genie totals 4.502e-38 /
  4.369e-38 (was 4.367e-38 corrected — ML-jitter level); envelope medians
  2.90% published / 7.86% extension (was 2.91%/7.88%). The ledger entries
  above describing the correction are historical records of the pre-fix
  pipeline; post-fix artifacts need no correction.
- **PET-native lateral band (2026-06-10, job 54284039)**: cross-check of the
  GBDT-transferred lateral block in the PET 4D budget, via the event-aligned
  5D join (`pet_lateral_band.py`; PC↔5D row alignment asserted over all
  32.85M rows, 4 truth columns + w_truth exact; CV-path consistency 0).
  18 detector universes, frozen PET push weights, miss rows pinned to CV
  (KNOWN_ISSUES #12), reco-weight ratio in the completeness numerator.
  **Native lateral median 1.74%/bin vs transferred 4.03%; total budget
  22.5% vs published 23.0%.** Band ordering: MinosEfficiency (sqrt-tr
  2.7e-39) > Muon_Energy_MINOS (3.4e-40) > GEANT_Neutron (5.6e-40 — same
  order) > GEANT_Proton/Pion > BeamAngle/MuonResolution (≲5e-42). The
  frozen-push scheme cannot carry per-universe retraining response, so the
  native band is the optimistic bound and the published transfer the
  conservative one — **the published 23.0% budget stands**; the true
  lateral lies in [1.74%, 4.03%].
  `products/pet/pet_4d_covariance_combined_wlat.root`.
- **Standing checks rerun**: **PASS**. `xsec_nd.py` self-tests all pass;
  `check_4d_anchors.py` reproduces 0.38%/0.64%/1.68% medians and 4D/3D
  integral ratio 0.9960; `check_5d_anchors.py` 5D/4D total 1.0011, W marginal
  PASS; `compare_3d_fullcov.py` reproduces the historical candidate's
  sqrt-trace 5.724e-39, rank 247/1431, and Tune-v1/GiBUU ordering. These
  covariance-dependent numbers are quarantined pending the final 5D-to-3D
  projection.

## Environment And Test Harness

- `python -m pytest unbinned_unfolding/test -q`: **BLOCKED**. The active
  `root_6_28` Python does not have `pytest` installed.
- `python 3d-unfolding/xsec_3d.py`: **PASS**. Eavail marginal recovers 2D
  cross section to max relative difference `3.84e-16`; 1D projections integrate
  to the same total.
- `python nd-unfolding/xsec_nd.py`: **PASS**. N-D extraction reproduces frozen
  `xsec_3d.py` to `<1e-12`; 4D q3 marginal recovers 3D cross section to max
  relative difference `3.8e-16`; all 1D projections integrate to the same total.

## Known Audit Findings

- Point-cloud PET: **REFRESHED AS A SHAPE/METHOD CROSS-CHECK**. The stale
  `ExtraEnergyClusters_*` PET artifact was replaced after confirming
  `CVUniverse::GetRecoClusters()` reads `cluster_energy`, `cluster_pos`,
  `cluster_z`, and filters `cluster_isMuontrack`. The corrected point-cloud
  chain rebuilt `runEventLoopOmniFold_PC_MEFHC.root` and `of_inputs_pc.npz`,
  then PET training job 54033990 and comparison job 54033991 completed with
  exit `0:0`. The regenerated `pet_vs_gbdt.png` reports area-normalized
  PET-vs-GBDT median shape differences of 3.86% (pT), 2.36% (pz), 2.63%
  (Eavail), and 2.33% (q3). This remains a shape-only comparison because the
  PET run uses a 2M-event subsample.
- Ascencio low-q3 data: **STAGED ONLY** unless a gated data file is supplied.
  Local scripts can produce our-side spectra and synthetic checks, but the real
  2110.13372 numerical overlay is not complete from public in-session data.

## Active 2D Result

- `compare_to_paper_fullcov.py` with the frozen 2D result and paper covariance:
  **PASS**. Recomputed paper full-covariance chi2/ndf is `3.661` on 205 bins.
- Combined paper+ours check: **PASS** when using
  `uq_universe_covariance_full_matcorr_fluxfix.root:hCov_combined` plus
  `uq_covariance_ml.root:hCov2D_reported`. Recomputed combined chi2/ndf is
  `1.481`; log-normal combined chi2/ndf is `1.468`; pull mean/RMS is
  `0.051/0.409`.
- Covariance-file contract: `hCov_combined` already includes the bootstrap
  covariance. Adding `uq_covariance_boot300.root:hCov2D_reported` separately
  double-counts bootstrap and changes the combined chi2/ndf to `1.341`.
- Comparison to GENIE MINERvA Tune v1 (paper `TotalCovariance`, 205 bins):
  data vs tune `33.039`, ours vs tune `26.491`. Both **VERIFIED-NUMERIC**
  2026-08-11 — see the dated entry at the top of this file and the ingredient
  receipt `2d-unfolding/receipt_model_chi2_2d.json`.

## Active 3D And 4D Results — central anchors valid; covariance products gated

- `compare_3d_fullcov.py` with GENIE, Tune v1, NuWro, and GiBUU reproduces the
  historical candidate: sqrt-trace `5.724e-39`, hard rank `247/1431`, and the
  same generator ordering. **DIAGNOSTIC ONLY** — the final quotable 3D
  covariance and generator comparison require the adopted selection-complete
  5D-to-3D projection.
- `check_4d_anchors.py`: **PASS**. 4D total is `3.0665e-38`; 4D/3D
  2D-marginal integral ratio is `0.9960`; median projection differences are
  `0.38%` for pT, `0.64%` for pz, and `1.68%` for Eavail.
- `compare_ascencio_q3.py`: **PASS for our-side spectra only**. It produces
  `d sigma/dq3` and low-q3 `Eavail` slices; no real Ascencio chi2 is computed
  without the external gated data file.
- `compare_mlsplit_combined.py`: **PASS as a historical-component diagnostic**.
  Train/test-split ML band is `1.24x` the seed-only band, but the historical
  combined 3D sqrt-trace moves only `+0.04%`; final adoption remains gated.

## Validation Diagnostics

- `bottom_line_test.py --dim 2 --mode closure`: **PASS**. Feature-bin residual
  is `1.6875%` vs injected `17.202%`, ratio `0.0981`.
- `bottom_line_test.py --dim 3 --mode closure`: **PASS**. Feature-bin residual
  is `1.8408%` vs injected `18.061%`, ratio `0.1019`.
- `classifier_calibration.py --n 200000`: **PASS**. GBDT AUC/Brier
  `0.5374/0.2486`; MLP AUC/Brier `0.5338/0.2500`; binned ratio recovery
  median `4.72%` for GBDT and `20.90%` for MLP; GBDT/MLP binned correlation
  `0.9159`.
- `unbinned_gof.py` using stored 3D weights with `--max-per-class 200000`:
  **DESCRIPTIVE DIAGNOSTIC ONLY**. Prior acc/AUC `0.5196/0.5314`; unfolded
  acc/AUC `0.5013/0.5022`. The historical analytic `z` and `p` values are not
  calibrated because the OmniFold weights were not cross-fitted and the null
  does not repeat the full pipeline.
- Same-ensemble pull diagnostic: **REPRODUCED 2026-06-11** (the 200-toy
  ROOTs were missing from the checkout). Regen arrays 54273493/54273495 rebuilt
  all 200 toys in `2d-unfolding/uq/coverage/`; `uq/coverage_toys.py` reproduces
  the historical result exactly: fraction with $|r|\leq1$
  `68.71%`, median `68.50%`, `<|r|> = 0.794` (target 0.798), signed residual
  `+0.006 +/- 0.082`, `97.56%` of the 205 reported bins above the 65% target
  (same 5 bins below). Because the same toys determine and are scored by their
  standard deviation, these are Gaussianity/pull checks, not coverage.

### 2026-07-16 — Corrected 4D UQ (P6-4D), non-lateral core (support-limited lateral)

These supersede the quarantined June `uq_4d/` products for the NON-LATERAL contract. The
FINAL adopted 4D covariance additionally needs the unified-throw inflation + Agent A's
selection-complete standard lateral block (both pending); numbers below are the corrected
combined (block-sum) covariance and validations.
- 4D throw bank (from-5D reconstruction, `assemble_bank_4d_from5d.py`) CV reproduces the
  frozen 4D central: reported bins `4830` (mask identical), total `3.0679e-38` vs central
  `3.0664e-38` (rel `4.8e-4`), per-bin median `0.65%`. PASS. [pilot_cv_check_4d.py]
- Corrected combined 4D covariance (reported bins 4830; symmetric, finite, PSD min-eig/max
  `-2.8e-16`): C_syst √tr `2.0931e-38` (median `13.37%`/bin, rank 142); +norm 1.4%; +C_stat
  √tr `1.2117e-39` (median `0.92%`); +C_ML √tr `1.0499e-39` (median `0.74%`); COMBINED √tr
  `2.0992e-38` (median `13.47%`/bin, rank 264). [uq_4d/corrected/universe_stage2_4d/
  uq_universe_4d_covariance_combined.root; summary .../uq_universe_4d_covariance_combined.summary.json]
- P7 5D→4D marginal (DRY-RUN candidate on the current committed adopted 5D; NOT a
  publication number — final gated): 4830-bin PSD projection, √tr `2.41e-38`, 5 orphan
  4D-reported bins receive no 5D source (flagged). [project_cov_nd.py]

### 2026-07-16 — Statistical-validation repair (Agent C WS1 coverage; integrated into the note by Agent D)

Coverage audit and FPS split-sample truth-containment diagnostic
(Gaussian nominal 68.27%). Reuse-only on the existing toy stacks
(`coverage_valid_nd.py`, estimator seed 42):
- 2D: **NO COVERAGE NUMBER.** The 200 ROOT toys fluctuate stored
  `hTruthXSec2D` through the MC bootstrap; all 205 reported bins vary, with a
  maximum relative range of 1.048 across toys. The attempted 68.80% result used
  their all-toy mean and is withdrawn because that is not an independent fixed
  truth. A valid independent reference or redesigned ensemble is required.
  [`2d-unfolding/uq/coverage_valid_2d_audit.json`]
- FPS: **68.67%** of evaluation bin--toy cells (200 cov_fps toys split 100/100,
  266 bins). Variant-A independent `C_stat` band contains **77.6%** of closure
  bin--toy cells and is wider than the closure-toy spread. The estimator seed is
  fixed, so these diagnose the statistical closure-toy stream rather than the
  full adopted band.
  [`nd-unfolding/uq_fps/corrected/coverage_valid_fps.json`]
- The OLD same-ensemble "coverage" (2D `68.71%` / FPS `68.9%`, ⟨|r|⟩≈`0.794` vs √(2/π)=`0.798`,
  `97.6%` bins ≥65%) is a standardized-pull/Gaussianity self-consistency diagnostic, NOT
  frequentist coverage → RELABELED, retained under that label. No aggregate
  binomial uncertainty is quoted because bins within each toy are correlated
  and the calibration widths are estimated.

C2ST (WS2): analytic p-values (`z=1.4, p=0.17`; `p≈5e-244`) and "statistically indistinguishable"
REMOVED from the note; retained as a descriptive held-out-AUC drop (≈0.535→≈0.501); no calibrated
p-value (valid null = hundreds of cross-fitted OmniFold pipelines, unaffordable; unbinned GoF open).
WS3: ours-vs-paper χ² (`\chiPaper` 3.66 / `\chiCombined` 1.481) relabeled an INDICATIVE distance
(shared systematics + no OmniFold↔paper cross-covariance → not a calibrated GoF); Ascencio kept
shape-level/descriptive; generator significances remain gated until the selection-complete
higher-dimensional covariance is adopted and the values are recomputed.
Agent C's full WS2/WS3 RUN_LOG/STATUS + the paired-C_delta OF-vs-IBU test land under their commit gate.

FPS P4/P6 (2026-07-18, 2nd fail-closed repair round): the ten FPS active-endpoint unfolds are PURITY
CONTROLS (both launchers omitted --bkg-mode → unfold default `purity`), quarantined and NOT publication
inputs; the selected footing is `negweight-refined`. No covariance was built or adopted. The negweight
preflight is hardened: a hash-bound v2 publication manifest requiring the canonical 266/285 reported-mask
fingerprint (23b2a2f4…, recomputed not trusted) + full merged-input SHA256 (reused from the validated
orchestrator receipt p4-merged-20260718, no re-hash) + a PASS receipt bound at every covariance
transition; mandatory hJointMeanShift; transactional endpoint launchers. 41/41 ROOT-free gate tests
PASS. Production remains gated on an `fps-adopt-verifier` PASS of this patch; no physics numbers change.

FPS P4/P6 (2026-07-18, repair-3): the chain is now mutually executable + hash-recomputing. Every
consumer runs its manifest/receipt/hash gates BEFORE importing ROOT (login-safe) and RECOMPUTES every
referenced artifact hash (strict lowercase 64-hex; canonical paths for unfold/input/config/source/
launcher/central/audit) — a substituted same-size ROOT, non-hex hash, or missing path fails. P4 gating
is unconditional; a schema-versioned hash-bound receipt chain (component_build → p4_validation →
active_adoption → unified_adoption) binds each predecessor artifact; two-field PASS objects are rejected.
Unified adoption requires the production CV sha + canonical 266/285 mask from the manifest and
hJointMeanShift(expected_dim=n) with its hash bound. Both endpoint launchers sit behind one strict
validator (fps_endpoint_receipt.py) that attributes the launcher actually used. Tests: 49/49 ROOT-free
unit + 9/9 REAL-CLI integration negatives PASS. ND_OMNIFOLD_STATUS.md remains a pre-existing PG0 dirty
file with no durable writer receipt (not repaired here). Production gated on fps-adopt-verifier PASS.

## 2026-07-18 G2 full-event extended-FPS dump — playlist-1A runtime smoke VERIFIED

First runtime validation of the G2 full-event point-cloud dump. Binary
`runEventLoopOmniFold` sha256 `61d7dfbf7ee38f39e51c656b48702056c773c3d1c5d1b2d9bf08a6da42d2e19b`,
built from source `486e53e` (G2 source byte-identical through HEAD `53de3f4`).
Playlist-1A, canonical manifests (`1A_Data.txt` sha256 `b74d8965…`, `1A_MC.txt`
sha256 `4100dca4…`), env `MNV101_DUMP_POINTCLOUD=1 MNV101_FULL_PHASE_SPACE=1`.
Validator PASS **50/50, 0 failed**:
- `mc_truth_denom == mc_signal_reco = 4,073,230` (Phase-18.2 completeness c-invariant, exact by construction)
- `mc_background = 44,900`; `data = 360,123`; native truth-only misses = `1,596,619`
- `mcPOTUsed = 4.0692592418996086e20`; `dataPOTUsed = 8.972756120489268e19`
- schema `petSchemaVersion=g2-fullevent-v1`, `hasFullEventSchema=1`, `fullPhaseSpace=1`
- native misses: `sim_pass=0`, reco muon/vertex `-9999` sentinels, empty reco clouds, valid cached truth id/muon
- distinct data/reco/truth schemas; no forbidden truth-detector/data-truth counterparts; equal E/pos/z/view/time cloud lengths; bkg cloud + `w_bkg` present; `cluster_view/time` + `ev_run/ev_subrun/ev_gate` populated

Published ROOT `nd-unfolding/pet/g2_smoke/runEventLoopOmniFold_G2_FPS_1A.root`
(9,419,026,130 B, sha256 `51e46fddd061cae37704c64604f73df8bb3d739cd5420bfd21cb0d2c89db320f`);
receipt `nd-unfolding/pet/g2_smoke/G2_1A_VALIDATION_RECEIPT.json` (sha256
`0aae83d84af77b2520dec83439e7a061176debc5e0d81e18019ac43a5a697867`); validation
receipt v2 sha256 `776addeb3453445bcb1e6fa45f81ed41ffe7f713a1cb2da0eac729eccf007b25`.
INTERFACE/INFRASTRUCTURE validation only — NOT a cross-section result. 12-playlist
production launcher staged, NOT submitted.

## 2026-07-19 G2 retained-domain recovery — playlists 1D and 1E VERIFIED (conditional)

Two full-event production loops completed but the 20,000-row sampled validator
encountered native upstream-corrupt muons outside the declared extended-FPS
retained domain. Exact source-AnaTuple comparisons confirmed that the G2 writer
copied the corrupt values faithfully. An additive exhaustive validator, accepted
by the persistent independent Gemini verifier after three fail-closed repairs,
composed the base structural suite and bound every excluded row.

- 1D: PASS, 2,643 out-of-domain rows bound; recovered ROOT 14,150,286,041 B,
  sha256 `06be7e6875f357af91b7e9d8d875e9b9759118c5c59002f5ac1fd205dc282b56`.
- 1E: PASS, 2,162 out-of-domain rows bound; recovered ROOT 11,651,881,243 B,
  sha256 `6ab0ac90d75aa843e99f33d8a817dab27b418273cbef298f641e7344724394dc`.
- Both publications returned rc=0, used the unchanged canonical binary/base
  validator/production launcher hashes, and passed independent post-publication
  SHA-256 checks.

This is interface/input evidence, not a physics result. It is valid only if the
next full-schema builder enforces `0<=pT<=30 GeV` and
`0<=p_parallel<=120 GeV` before training. All twelve array pairs and that
downstream exclusion still require their own committed gates. Canonical receipt:
`docs/orchestration/state/g2-domain-recovery-20260719.json`.

## 2026-07-19 G2 retained-domain recovery — playlists 1F and 1P VERIFIED (conditional)

The same committed, independently verified exhaustive recovery gate was applied
to two later sampled-validator failures without rerunning their completed event
loops. All non-superseded structural checks passed, and every excluded row was
identity/value-bound.

- 1F: PASS, 3,183 out-of-domain rows bound; recovered ROOT 16,299,560,962 B,
  sha256 `b5e7c28f40325015841e12c0f3e11987389eed61979e103effbf6f70473190fc`.
- 1P: PASS, 985 out-of-domain rows bound; recovered ROOT 4,631,598,593 B,
  sha256 `e986dab2bc64fb801eac0532df2a1539b7c409d3ccb46d8e6364feabc779ef4f`.
- Both no-clobber publications returned rc=0 and independently recomputed final
  ROOT hashes matched their receipt hashes.

This remains conditional interface/input evidence, not a physics result. The
next full-schema builder must enforce `0<=pT<=30 GeV` and
`0<=p_parallel<=120 GeV`; all twelve pairs still require one terminal committed
Gate-1 reconciliation. Canonical receipt:
`docs/orchestration/state/g2-domain-recovery-r4-20260719.json`.

## 2026-07-19 G2 Gate 1A — all 12 full-schema playlist pairs VERIFIED

Independent terminal validation of the complete per-playlist production set:

- 12/12 canonical playlist ROOT/receipt pairs PASS; zero validation failures.
- Total ROOT bytes: **113,500,285,444**; every ROOT SHA-256 recomputed and matched.
- `mc_truth_denom = mc_signal_reco = 49,906,108` exactly.
- `mc_background = 566,036`; `data = 4,119,797`; native truth-only misses =
  `20,361,799`.
- `mcPOTUsed = 4.978198462880827e21`; `dataPOTUsed = 1.057394261158926e21`.
- Eight normal production receipts passed 50/50 sampled validation. Four
  recovery receipts (1D/1E/1F/1P) bind exhaustive finite out-of-domain censuses,
  zero fatal/non-superseded failures, and the exact reviewed recovery chain.
- The same persistent Gemini verifier returned PASS and authorized commit.

This closes the per-playlist Gate 1A interface/input subgate, not Gate 1B or a
physics result. The merged ROOT and aligned three-inventory full-schema NPZ are
still required, and the downstream reader must enforce
`0<=pT<=30 GeV`, `0<=p_parallel<=120 GeV` before training. Canonical summary:
`docs/orchestration/state/g2-gate1-all12-validation-20260719.json` (sha256
`23b652d69460d61f2c347d0ec50c883043df83e0aa3fab3eda56b18b7364911f`).

## 2026-07-19 G2 Gate 1B — MEFHC merge VERIFIED

The twelve Gate-1A ROOTs were merged in canonical playlist order with an explicit
4-TiB TTree limit. ROOT's additive merge changed the semantic boolean
`hasTruthOnlyMisses` from twelve input ones to 12; a fail-closed normalization
required exactly 12 and rewrote only that field to 1 before validation.

- Merged ROOT: 113,496,440,965 bytes; SHA-256
  `9a16331f1c02103e3b5de5e6c00139aa39393ee11eb34881bea0b9a890344e2f`.
- Counts exactly match Gate 1A: truth = signal = 49,906,108; background 566,036;
  data 4,119,797; native misses 20,361,799.
- Exhaustive retained-domain validation: PASS, zero fatal/non-superseded
  structural failures; 21,797 finite out-of-domain rows censused and bound.
- Publication was no-clobber and receipt-last.

This is merged interface/input evidence, not a PET or physics result. Canonical
receipt: `nd-unfolding/g2_fullevent/merged/G2_MEFHC_MERGE_RECEIPT.json`.

## 2026-07-19 G2 Gate 1B — full-schema P=12 NPZ VERIFIED

Recovery job `56120687` completed `0:0` and receipt-last published
`nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz`: 9,897,374,636 bytes,
SHA-256 `fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625`.
The hash-bound inventories contain 49,152,885 signal rows, 4,116,128 data rows,
and 564,591 background rows; signal masks contain 20,573,521 reco-pass and
49,150,928 truth-pass rows.

Independent validation reproduced the 42-member headers, exact
`g2-fullevent-v1` schema, canonical extended-FPS edges, POT scale, retained
`[0,30] x [0,120]` GeV domain, miss sentinel guards, and all three ordered
identity hashes with zero failures. Receipt:
`docs/orchestration/state/g2-gate1b-npz-validation-20260719.json`. This closes
G2 Gate 1 only; it does not validate a refined target or PET result.

## 2026-07-19 G2 Gate 2 — literal `negweight-refined` target VERIFIED

The exact target-only runtime used the frozen 9,897,374,636-byte Gate-1 NPZ
(`fa6b3463...`), canonical `u2d.refine_stay_positive`, master seed 42 and
refinement seed 45. It consumed all 4,116,128 data rows plus 564,591 literal
POT-scaled negative-background rows and receipt-last published 4,680,719
normalized `float32` weights (SHA-256 `1ef7e0d2...`).

- Raw data/background/signed sums: 4,116,128.0 / 109,599.399384 / 4,006,528.600616.
- Learned refined target: finite and nonnegative; 20 floored-zero rows;
  normalized sum 1,000,000.377928 (float32 accumulation tolerance).
- Exact configuration hash: `dbe2854785cbff5a710c97acf43d8d91bcc43f906a00ad59c3f187e8ca2d4c16`.
- Independent 15x19 extended-grid reconstruction: zero negative signed cells;
  learned-vs-normalized-clipped L1 fraction `3.7793e-7`, cosine 1.0.
- Independent validation rehashed the full input, weights and participating
  code and reproduced signed-target identity `04a79a8...` and all telemetry.
- The preserved agy Gate-2 verifier returned PASS and found no Agent-B receipt
  correction necessary.

This verifies the measured-side Gate-2 target, not a PET training result. PET
training did not start. Canonical receipts:
`nd-unfolding/g2_fullevent/gate2/final/G2_GATE2_TARGET_RUNTIME_RECEIPT.json`,
`docs/orchestration/state/g2-gate2-runtime-independent-validation-20260719.json`,
and `docs/orchestration/state/g2-gate2-verifier-20260719.json`.

## 2026-07-20 P3F-scalar interface inventory — VERIFIED

Complete historical validation of the selection-shifted scalar FPS inputs passed
for the exact five-band x two-endpoint x twelve-playlist inventory: 120/120
files, zero missing/extras/failures, 120 distinct ROOT SHA-256 values, and 120
unique recomputed producer-log hashes. Producer accounting is exactly job
`55961845`: 1 file and job `55972324`: 119 files, with every file bound to
`COMPLETED/0:0`.

The 120 ROOTs total 748,222,225,235 bytes. Repeated-endpoint interface counts
are `mc_truth_denom == mc_signal_reco = 499,061,080`, background 5,660,367,
and data 41,197,970. The four-field aggregate migration census is truth
entrants/exits 0/0 and reco entrants/exits 9,421/9,686. Identity, schema, POT,
completeness, miss metadata, point-cloud contracts, per-file hashes, and all ten
endpoint aggregates passed independent reconstruction. The preserved Gemini
verifier returned PASS.

The promoted canonical manifest has SHA-256
`8f957bf251728a7de57d4fe2ea8d00c2010c23d151e6c9c0a96d3ec31d4e60a8`.
This is a P3F-scalar interface prerequisite, not a PET or physics result;
P3F-PET generation and PET training did not start in this wake. Canonical
receipt:
`docs/orchestration/state/p3f-scalar-fullaudit-promotion-20260720.json`.

## 2026-08-09 Standard 5D endpoint set — re-unfold reproduction VERIFIED-NUMERIC

**Claim.** The ten standard 5D lateral-endpoint unfolds published by job `56495756` reproduce the
2026-07-18 reference set to within the declared content tolerance, on all ten endpoints.

**Numbers** (evidence job `56532439`, code_rev `7053f68`, 10 694 reported 5D bins per endpoint):

| id | quantity | value | tolerance | margin |
| --- |---|---|---|---|
| VL91 | worst per-bin relative difference | **1.831e-11** | 1e-9 | 54.6x |
| VL92 | worst integral relative difference | **2.874e-12** | 1e-11 | 3.48x |
| VL93 | endpoints within tolerance | **10 / 10** | — | — |

Per-endpoint values are in `active_universe_5d/standard/evidence/p4_standard_manifest.json` under
`endpoint_reproduction`. The worst of each is `BeamAngleY_1`.

**Why this is content comparison and not hash identity.** These ROOTs are **not bit-reproducible**
(KNOWN_ISSUES #24): 0 of 10 sha256 match across a correct re-run, because LightGBM/OpenMP
reduction order depends on thread count. sha256 remains a storage-integrity property here and is
not read as derivation identity.

**Structural note on the integral leg — do not widen it again.** Its coherent ceiling is 1.831e-11
(the worst per-bin deviation) and its incoherent floor is 1.770e-13 (that / sqrt(10 694)), so the
entire range it can resolve is **103.4x**. The observation sits inside that band: 16.2x above the
floor, 6.37x below the ceiling, i.e. N_eff = 40.6 independent groups rather than 10 694 —
consistent with the recorded 0.4594 positive fraction (26.6 sigma from 0.5), since a different
OpenMP partition is a different *deterministic* rounding path. The 3.48x margin is therefore not
slack, and the 2.874e-12 observation **would have failed the 1e-12 tolerance in force before
2026-08-08**. Response to a future breach is pre-specified at `p4_lib.REPRO_RTOL_INTEGRAL` and
turns on sign balance and content correlation, never on magnitude.

**Status.** VERIFIED-NUMERIC. This certifies the endpoint set only. The covariance candidate built
2026-08-09 was produced without a `standard-p4-verifier` PASS, self-declares
`publication_gate_rejects_this: true`, and is **not quotable**.

## 2026-08-09 Full-event PET Step-1 dynamics controls — VERIFIED DIAGNOSTIC

Changed array `56534116` and annealed-LR job `56534117` completed `0:0`. The r2 launcher commit is
`783e674`; the OmniFold import preflight, launcher hashes, wrapper/driver/loader/engine, Gate-2
target and receipt, and Gate-3 manifest all pass their frozen hashes. Each result is COMPLETE,
diagnostic-only, collision-isolated, and independently checked against the predeclared iteration-2
repair rule: **correct sign and achieved/required >= 0.90**.

| id | control | iteration-2 sign | achieved/required | frozen gate |
| --- |---|---:|---:|---|
| VL94 | warm model / fresh split | wrong | 0.6636878 | FAIL |
| VL95 | cold model / fixed split | correct | 0.7883825 | FAIL (<0.90) |
| VL96 | cold model / fresh split | wrong | 25.0654103 | FAIL |
| VL97 | warm/fixed with effective post-iteration `1e-5` LR | wrong | 0.8958691 | FAIL |

**Formal predeclared verdict:** no factorial arm repairs, and the annealed arm does not repair the
iteration-2 increment gate. That formal route leaves intrinsic push feedback / representation-tail
contraction. Thresholds were not changed.

**Independent end-state cross-check:** the increment gate and publication normalization ask different
questions near the target. Against `R = 1.1240802`, the annealed arm is already only 0.239% low after
iteration 1 and ends 1.172% low after iteration 2 (`push = 1.1109012`), inside the separate frozen 5%
fold-forward tolerance and a 29.39x improvement over the baseline's 34.46% deficit. Thus “wrong-sign
increment” does not imply “bad end state” here: the required increment has collapsed to approximately
unity. This does **not** establish correct unfolded shape, and the arm's proposer explicitly declared a
conflict of interest. The predeclaration is not overruled; both readings are escalated to Joseph.

These are diagnostic mechanism results, not a cross section: Branch C remains and no product is
quotable. Receipts:
`docs/orchestration/state/step1-dynamics-r2-complete-56534116.json` and
`docs/orchestration/state/step1-annealed-lr-r2-complete-56534117.json`.

## 2026-08-10 Annealed-LR powered-closure shape validation — PRIMARY PASS / SECONDARY TRADE-OFF

Changed job `56552326` completed its three-iteration/six-fit powered closure. Independent arithmetic
on the persisted 285-cell spectra gives:

| id | quantity | value | criterion / comparison | reading |
| --- |---|---:|---:|---|
| VL98 | injected gap | 0.234270363 | >= 0.15 | PASS |
| VL99 | floor/gap | 0.045875515 | <= 0.10 | PASS |
| VL100 | recovery | **0.512603276** | PRIMARY >= 0.494582400 | **PASS by 0.018020876** |
| VL101 | recovery vs baseline | -0.034249724 | SECONDARY 0.546853 +/- 0.02 | **TRADE-OFF / ARM REJECTED** |

The fit-time anneal is proven by six records: two iteration-0 fits at `1e-4`, followed by four fits
at `1e-5`. The Slurm `3:0` status is a post-training launcher artifact: the driver still returns 3
against its retired absolute 0.80 self-check, so `set -e` stopped before the quarantine-manifest step.
The report and artifact are complete and hash-bound. Per the predeclaration amendment, the adopted
PRIMARY criterion decides and the PRIMARY/SECONDARY disagreement is itself the finding.

CPU finalizer `56562169` subsequently completed `0:0`. Its authoritative full-dump/artifact
re-derivation passed all 31 powered-closure checks and all 47 total checks, with zero failures; the
largest reported-versus-rederived spectrum difference is `5.898e-12` against `1e-9`. All 14 code/data
hash pins, the disjoint `2M+2M` split, Gate-2 identity, source digest, producer receipt, and six fit-time
LR records pass. The committed quarantine manifest was reused without overwrite and independently
re-established both publication rejection conditions, including the physics-only rejection.

This remains diagnostic and non-quotable. No engine edit, threshold change, promotion, or Branch C
reopening is authorized. Receipts:
`docs/orchestration/state/annealed-shape-r2-terminal-56552326.json` and
`docs/orchestration/state/annealed-shape-finalizer-complete-56562169.json`.

## 2026-08-10 Annealed production nominal reproduction — ~~VERIFIED FINDING~~ **RETRACTED 2026-08-11**

> ### ⚠ RETRACTED — DO NOT QUOTE THE VERDICT OR THE `188.4x` FROM THIS SECTION
>
> **The verdict below ("FINDING — code paths disagree") is REFUTED, and the `188.4x` is computed against the wrong
> population.** Retracted at `535668d`; detail in `KNOWN_ISSUES.md` (struck-through entry) and
> `docs/orchestration/PREDECLARATION-20260810-designA-diagnostic-reproduction.md` §RESULT.
>
> A third run of the **diagnostic** configuration (`56611394`) gave three points on byte-identical code at identical seeds:
> `-0.011724321` / `-0.007386682` / `-0.052174875`, i.e. **mean `-0.023761959`, sd `0.024701703`, range `0.044788193`**.
> The **production value `-0.035546` sits INSIDE that range**, `0.48` diagnostic sd from the diagnostic mean. The gap by
> denominator: `188.4x` (production scatter — the wrong population) → `6.0x` (a two-point difference) → **`0.48x`
> (three-point sd, the first honest denominator).** **There is no established code-path difference.**
>
> **What in this section STILL STANDS, quotable:** the production numbers themselves — `1.0840529523` / `-0.035608971`
> and `1.0841954573` / `-0.035482196`, the pair scatter `0.000126775`, the baseline SHA `58f664cdef266d09` unchanged
> before and after, and the optimizer readback proving the anneal ran (two fits at `1e-4`, four at `1e-5`).
> Production is reproducible to `1.3e-4` and is unaffected by the retraction.
>
> **What is DEAD:** the verdict; the `188.4x`; and the row labelled *"diagnostic expectation"* — `-0.011724321` was
> **one draw**, never an expectation, and the standing constraint is that no one-shot measurement through that wrapper
> family may be quoted as a point value.
>
> Left in place rather than deleted, per this repo's retraction convention: a reader who follows a citation here must
> find the correction, not an absence.


Job `56563761` completed `0:0` and atomically published both the production nominal and matched-floor
artifacts. The canonical 2026-08-08 baseline SHA-256 remains `58f664cdef266d09...` before and after.

| id | arm | fold-forward ratio | deviation from R | frozen reproduction window |
| --- |---|---:|---:|---|
| VL102 | production nominal | 1.0840529523 | **-0.035608971** | OUTSIDE |
| VL103 | production matched floor | 1.0841954573 | **-0.035482196** | OUTSIDE |
| VL104 | diagnostic expectation (`56534117`) | 1.1109012167 | -0.011724321 | expected |

Here `R = 1.1240802949941018`; the predeclared window is
`[-0.021724,-0.001724]`. The production-pair scatter is **0.000126775**, while the nominal gap to
the expected `-0.011724` is **0.023884971 = 188.4x the measured scatter**. Both artifacts prove from
optimizer readback that the anneal ran: two fits at `1e-4`, followed by four at `1e-5`; their seed
policies and realized LR records agree exactly. The frozen verdict is therefore **FINDING — code paths
disagree**, not anneal failure.

This verifies the reproduction finding, not an estimator promotion or physics result. Recovery was not
evaluated, no band was changed, and no extraction or cross section was run. The production value still
passes the separate absolute 0.05 normalization tolerance, but the diagnostic `-1.17%` value must not be
quoted as production. Canonical receipt:
`docs/orchestration/state/annealed-nominal-complete-56563761.json`.

## 2026-08-09 J36 global-POT-scale mixture error — SHAPE effect BOUNDED, VERIFIED-NUMERIC

**Claim.** The J36 defect (one global `sum(D_p)/sum(M_p)` POT scale in place of per-playlist
`D_p/M_p`) changes the 2D analysis' reco **shape** by **≤ 0.15 %**, and by **≤ 0.04 %** in the
low-pT peak ridge where the paper-comparison tension is localised.

**Measured** from the 12 per-playlist event-loop outputs, on the analysis' own 14 pT / 16 p∥ edges,
comparing `R_glob * Σ_p MC_p` against `Σ_p R_p MC_p`, shape taken after renormalising to unit
yield-weighted mean:

| id | | pT | p∥ |
| --- |---|---|---|
| VL105 | normalisation shift | +0.119 % | +0.118 % |
| VL106 | **shape max abs** | **0.073 %** | **0.143 %** |
| VL107 | shape rms | 0.035 % | 0.087 % |
| VL108 | shape peak-to-peak | 0.105 % | 0.281 % |

pT bins 2 / 7 / 10 (16 / 11 / 12 % of the χ²): **+0.010 % / +0.017 % / −0.033 %**.
Low-pT ridge (pT ≤ 0.4 GeV/c): max **0.032 %**.

The per-playlist ratios span 0.1707–0.2371, `max/min − 1 = 38.90 %`, reproducing J36's spread
exactly from the files — the error is large in the weights and small in the shape, because the
twelve playlists are nearly shape-identical in reco pT and a large reweighting of shape-similar
components is almost pure normalisation.

**Consequence.** The `app_statmethods.tex` statement that tight bin-to-bin correlation in the
flux/Muon_Energy region leaves little freedom to absorb a coherent ~1–2 % shape difference
**SURVIVES**: the mixture error there is 14–30× smaller. The sentence takes a caveat, not a rebuild.

**Scope.** Pre-unfolding bound on the MC prediction; MC signal-reco sample (background is ~2 % of
entries); pT and p∥ only — it does not bound 5D/ND quantities. **Status: VERIFIED-NUMERIC.** The
defect is not thereby correct; it is bounded.
