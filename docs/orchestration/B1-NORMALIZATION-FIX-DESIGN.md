# B1 normalization fix — design and rationale

**Status: IMPLEMENTED 2026-07-29** (code-only; `R` still unmeasured until the 2026-08-03
restore). All of §2 plus the §4 tests landed as one patch set. Four receipt-frozen files
changed — `fullevent_fps_dataloader.py`, `gate2_target_runtime.py`,
`train_fullevent_nominal.py`, `validate_pet_nominal_gate4.py` — voiding five bindings across
three receipts, as `RESTORE-2026-08-03.md` Steps 2 and 2b schedule. See §8 for what the
implementation changed about this design.

*(Historical status line, retained so the diff reads: "proposed, not implemented. Three
receipt-frozen files change; none has been touched." The count was three because §2d's
plumbing requirement — the driver — had not yet been recognised as an edit.)*
**Supersedes:** recommendation item 6 of `AUDIT-FINDINGS-20260728.md` and the
`normalize=False`-on-both variant recorded in the 2026-07-29 run-log entry.
**Read first:** the "Addendum — adversarial re-verification of B1 (2026-07-29)" in
`AUDIT-FINDINGS-20260728.md`.

---

## 1. The defect, in one paragraph

`fullevent_fps_dataloader.py:613` (MC) and `:658` (measured) both pass `normalize=True`.
`omnifold_nn/omnifold/dataloader.py:110-113` rescales each loader's `pass_reco` weight sum
**in place** to 1e6, and `omnifold_nn/omnifold/omnifold.py:176-177` uses exactly those arrays
as the two step-1 class weight blocks. So at iteration 0 both class totals are 1e6, `W1/W0`
is identically 1, and the physical POT-scaled data/MC rate ratio `R` is erased. Nothing
restores it. The promoted Gate-2 receipt records both sides: `runtime_target.refined_sum =
4006527.656` before, `learned_refined_normalized_sum = 1000000.37792753` after.

This is **not** a recoverable overall scale. `omnifold.py:185` hard-codes `1` as the
off-acceptance weight in the correct and the broken run alike, so the loop is not
scale-equivariant: step 2's optimum is `push'(z) = 1 + a(z)(R-1)` against `push(z) = 1`, with
`a(z)` the local reco acceptance. Completeness (`pet_systematics_5d.py:146-152,161`) is built
from `w_truth` only and is identical either way, so the per-bin cross-section ratio is
`1 + a(bin)*(R-1)` — acceptance-coupled, worst in the low-completeness extension cells that
are this measurement's novelty. Area-normalizing does not remove it.

---

## 2. The change

### 2a. Loader — two call sites

Keep the **MC** loader at `normalize=True` (factor 1e6, unchanged). Pass an explicit
normalization factor to the **measured** loader:

```python
# fullevent_fps_dataloader.py:658 (negweight-refined nominal)
data = DataLoader(reco=meas_cloud_all, weight=w_refined.astype(np.float32),
                  normalize=True, normalization_factor=1.0e6 * R,
                  reco_evt=event_meas_all)
```

`normalization_factor` already exists as a DataLoader argument (`dataloader.py:13`); no change
to the vendored engine. The purity-control branch at `:621` is a labelled regression control,
not the publication nominal, and is out of scope.

### 2b. `R`, computed internally from the full inventory

```
R = (n_data - pot_scale * sum(w_bkg)) / (pot_scale * sum(w_truth_full[pass_reco_full]))
```

Numerator = the signed measured inventory, i.e. unit-weight data minus POT-scaled
background. It is receipt-verified: `independent_binned_checks.raw_signed_sum =
4006528.6006158064`.

Denominator = the POT-scaled signal-MC reco-level prediction over the **full** inventory —
`w_truth_full` at `:551`, *before* the `imc` subsample — not the subsampled `w_truth` at
`:608`.

**The `pot_scale` trap.** `w_truth` in the G2 npz is the RAW literal ROOT per-event MC
weight, NOT POT-scaled (`:551` comment; convention stated at
`dump_pointcloud_inputs.py:183-186`, "Consumers apply pot_scale"). Tracing `:551 → :608 →
:613` there is no `pot_scale` multiplication anywhere. Omitting it inflates `R` by
`1/pot_scale ≈ 4.7x`. Two independent reviewers arrived at the formula without it.
`check_step1_class_ratio.py` prints both conventions for exactly this reason.

Under bootstrap, `R` must be recomputed from that replica's `data_factor` / `bkg_factor` /
`sig_factor`, which are already in scope at the call site.

**`R`'s denominator depends on finding B-4, so B-4 must be settled first.**
`AUDIT-FINDINGS-20260729-B.md` B-4 establishes that `w_reco` — carried by the G2 contract
(`dump_pointcloud_inputs.py:201`, required at `:299`/`:540`) and used as a separate leg by the
validated 2D path (`unfold_2d_omnifold_unbinned.py:1715-1716`) — is **never read** by the
full-event loader (`grep -c w_reco` → 0); the one `w_truth` vector at `:551` drives both
`omnifold.py:176-177` (step 1, reco) and `:196-197` (step 2, truth). The denominator above uses
`w_truth` because that is what the reco leg is actually fed, so it is self-consistent with the
code as it exists. But if B-4 is fixed, the physical denominator becomes
`pot_scale * sum(w_reco[pass_reco])` and `R` moves by
`sum(w_truth[pass_reco]) / sum(w_reco[pass_reco])`.

Consequence for sequencing: **do not freeze a measured `R` before B-4 is resolved**, or `R`
gets certified against a denominator the corrected loader no longer uses.
`check_step1_class_ratio.py` now reports both denominators, the shift factor, and the
`w_reco`-vs-`w_truth` comparison that is B-4's own minimal check — one pass over the dump
answers both. Bit-identical over `pass_reco` ⇒ B-4 inactive for the CV and this section stands
unchanged; that must be re-checked per systematic endpoint before P5B.

### 2c. Gate-2 — retarget the constant, do not delete the assertion

`gate2_target_runtime.py:411-412` and `:442-443` assert the step-1 target sums to exactly
`NORMALIZATION = 1_000_000.0` (`rtol=3e-6, atol=2.0`). Both become `1e6 * R`.

**The validator must recompute `R` itself** from the npz, not read it from the loader's
`meta`. Otherwise the gate certifies the loader against the loader's own claim. Two
independent computations agreeing is the whole point of the gate.

`:445` (`clipped_norm = clipped_hist * (NORMALIZATION / clipped_hist.sum())`) and the
`learned_vs_normalized_clipped_{l1_fraction,max_relative,cosine}` telemetry at `:448` are
**invariant** under this change: both histograms are renormalized to the same constant and
`rel_l1` divides by it, so the diagnostic content survives verbatim. Nothing is lost.

### 2d. Gate-4 — replace the check, do not merely widen it

`check_normalization` (`validate_pet_nominal_gate4.py:107-110`, tol `1e-3` at `:61`) requires
`|sum_w_push/sum_w - 1| <= 1e-3`, where `normalization=(sum_w_push, sum_w)` (`:160`) is a
**truth-level** pair.

**Correcting an earlier statement of mine: the fix is not "retarget this to ≈R."** At truth
level, over the full truth population including off-acceptance events where `push == 1`, the
expected ratio in a *correct* unfold is

```
sum(w * push) / sum(w)  ->  1 + <a>_w * (R - 1)
```

not `R`. With row-fraction acceptance `20,404,292/32,849,103 = 0.621`
(`products/pet/bkgsub/pet_nominal_bkgsub_5d_xsec.summary.json:17-18`) and `R-1 ≈ 0.135` that
is ≈1.08 — a number that depends on the acceptance, i.e. on the very thing being measured.
Asserting `≈R` would fail a correct unfold; asserting `≈1` fails it worse.

The right check is a **reco-level folded-forward closure**: fold the unfolded truth back
through acceptance and require it reproduce the background-subtracted data yield. State it as a
**ratio**, not an absolute yield:

```
sum(w_truth * push over pass_reco) / sum(w_truth over pass_reco)  ==  R
```

i.e. *the reco-weighted mean of `push` equals `R`*. This is exactly `R` by construction:
dividing the absolute fold-forward identity
`pot_scale * sum(w_truth * push over pass_reco) == n_data - pot_scale * sum(w_bkg)` by
`pot_scale * sum(w_truth over pass_reco)` reproduces §2b's definition of `R` on the
right-hand side.

**Why the ratio and not the absolute form** (correcting the first version of this section, per
`AUDIT-FINDINGS-20260729-B.md` §7). The nominal trains on a 2M subsample of 49,152,885 rows, so
`push` exists only for the subsample while the measured yield is a full-inventory quantity. The
absolute form therefore fails a *correct* unfold by ≈ N/n_sub ≈ 24 — the same class of trap as
the `pot_scale` trap two sections above. The ratio needs no subsample factor. Restricting the
mask to `pass_reco` is also what removes the acceptance dependence that makes `≈R` wrong at
truth level: the earlier objection was right, the absolute form was an over-reaction to it, and
the mask change was sufficient.

The target is measured rather than modelled, it is the physical statement "the result, folded
back, reproduces what we saw," and — decisively — **it fails the current broken result while
passing a corrected one.** It converts Gate-4 from tolerating this defect into detecting its
whole class.

**This is not a pure mask change — the validator cannot see the inputs.** Gate-4's CLI
(`:210-231`) loads only the driver's weights npz and forwards `weights_push` and `mc_indices`.
Neither `w_truth` nor `pass_reco` is in scope anywhere in `validate_pet_nominal_gate4.py`, so
neither form of the check is computable today; `check_normalization`'s existence at `:107-110`
is necessary but not sufficient. Two options, and the choice matters:

- **Validator opens the G2 dump** and recomputes both sums plus `R` itself. Preferred. It has
  dump access at P5A runtime anyway, and it preserves the independence property — the same
  reason §2c insists the Gate-2 validator recompute `R` rather than read it from `meta`.
- **Driver persists** `(Σ w_truth·push, Σ w_truth, R)` over `pass_reco ∩ subsample` into the
  weights npz. Cheaper, but the gate would then certify the driver's own arithmetic. Acceptable
  only as a *supplement* to the above, never as a replacement.

**Tolerance — three terms, and it cannot inherit `1e-3`.** The check is not exact even for a
correct unfold:

1. *Structural floor.* Because `omnifold.py:185` pins off-acceptance `pull` to 1, step 2
   regresses across both acceptance classes at once and smooths `pass_reco` pushes toward 1.
   This does **not** vanish with more iterations — it is a property of the estimator, not of
   finite `niter`, and it sets the irreducible floor.
2. *Finite iteration.* At `niter = 2` the reco-level sum under `push` differs from that under
   `pull`.
3. *Subsample sampling.* The ratio is subsample-invariant in expectation, not algebraically:
   both sums run over the 2M draw, so a sampling term enters.

Term 1 caps the check's power and must be quantified before the tolerance is frozen, or the
gate is either toothless or fails a correct unfold. All three come out of the closure run
required in §4.

This is on top of the separate B2 defect: the Gate-4 CLI passes no `normalization=` at all
(`:223-229`), so today the check never executes regardless of its target.

---

## 3. Why this design

**1. The class ratio becomes right, and stays right.** At iteration 0, MC total = 1e6 and
data total = 1e6·R, so `W1/W0 = R`. At iteration *i*, MC total = `1e6 * <w_push>` while the
data total is fixed, so the ratio is `R / <w_push>` — the *remaining* disagreement, which
converges to 1 as the reweighting succeeds. That is the correct dynamic. Under the current
bug the ratio starts at 1, so there is never any rate discrepancy to learn.

**2. Subsample invariance is free.** Normalizing MC to 1e6 removes all dependence on how many
rows the `imc` draw took; `R` uses the full inventory and is likewise draw-independent. The
nominal trains on a bounded 2M MC subsample (`validate_pet_nominal_gate4.py:55-56`) against a
full measured inventory (`:645-659`), so this matters: it is precisely why the naive
`normalize=False` alternative fails.

**3. Weight magnitudes stay conditioned.** Both class blocks total ~1e6 regardless of dataset
size, so per-row weights stay ~1e6/N and gradient scales are unchanged from the
currently-working configuration. `R ≈ 1.1` introduces a ~10% class imbalance — far from the
regime `_balance_weights` warns about (`omnifold_nn_core.py:158-169`), where an MLP on badly
imbalanced totals collapsed to the trivial bias solution at ~1e-6 of the GBDT result.

**4. `R` is derived, never piped.** Computing it inside the loader from data already in hand
means no constant in a frozen file to go stale, and correct behaviour per bootstrap replica —
each has its own yield ratio, so a hardcoded `R` would be wrong for every replica but the
nominal.

**5. It is small.** Two loader call sites, two Gate-2 constants, one Gate-4 check. No change
to the vendored engine, no new machinery, and Gate-2's diagnostic telemetry is bit-preserved.

### Alternatives, and why each is worse

| Alternative | Why rejected |
|---|---|
| Restore the yield ratio post-hoc at extraction | **Refuted.** `omnifold.py:185` pins off-acceptance weights to 1 in both runs, so the bias is `1 + a(bin)(R-1)` — acceptance-coupled, not scalar-recoverable. Leaves a few-percent distortion correlated with completeness, worst in the extension cells. Area-normalizing does not remove it. |
| Delete `normalize=True` from both loaders | Class ratio becomes the arbitrary MC **sampling fraction** (~1/24 at 2M of 49M), not `R` — strictly worse than 1. |
| `normalize=False` + `pot_scale * subsample_scale` on MC | Works, but needs `subsample_scale` plumbed explicitly (`pet_vs_gbdt.py:68-77`) and lets absolute weight magnitudes float with physical yields (~4e6), changing gradient scales for no benefit. Strictly more moving parts than 2a. |
| In-loop restoration per step, as `omnifold_nn_core.py:246` | Unnecessary here. That path re-balances every step so its ratio must be recomputed every step; the DataLoader normalization is a one-time scale choice and `w_push` already carries the iteration dynamics (see reason 1). |
| Hardcode a measured `R` in the loader | Wrong for every bootstrap replica but the nominal; goes stale silently in a frozen file. |
| Widen Gate-4's `normalization_dev_max` | Widening past 13.5% makes the check detect nothing. See 2d. |

---

## 4. Risks, and what must be tested

- **Training dynamics are empirical, not provable.** Reason 3 argues a 10% imbalance is safe;
  it does not prove it. Required: a closure run confirming the corrected configuration trains
  and recovers an injected rate change.
- **`R` is unmeasured.** Everything above is correct in form for any `R > 0`, but the
  *severity* scales with `R-1`. If `R` comes back near 1.0, the defect is far less serious
  than the recoil-only evidence suggests. Measure first: `check_step1_class_ratio.py`.
- **The current closure cannot detect this class of bug**, which is why it went unnoticed.
  Required: a closure that injects a known truth-level rate change and verifies recovery. This
  is the single highest-value test to write, and it needs no cluster.
- **Required unit test:** the new Gate-2 assertion must **fail** a 1e6-normalized target and
  **pass** a `1e6·R` one. Without it the re-issued gate is unverified.

## 5. Sequencing, and the one hazard that matters

Land 2a, 2c, 2d and the tests **as a single coherent patch set**. The dominant 08-03 failure
mode is a *partial* fix: correct the loader but leave the hardcoded Gate-2 and Gate-4
assertions in place, so the corrected ~13.5% shift aborts the pipeline inside the tight
restore window. All of section 2 is code-only and can be done before the restore; only
measuring `R` and re-running the gate require `/pscratch`.

Order on 08-03: measure `R` → re-run Gate-2 (678.7 s, CPU, zero GPU-hr) → re-issue receipts →
4-rank GPU host-memory probe → P5A.

## 6. Open question

**Can the expensive canonical refiner re-run be skipped?** The refiner runs upstream of the
normalization, so `w_refined` should be bit-identical and `signed_target_hash` unchanged — in
which case only the assertion target moves.

*(This was first written as "can the Gate-2 re-issue be validator-only?", which is
mis-framed — `AUDIT-FINDINGS-20260729-B.md` §7. The Gate-2 receipt binds four code paths
jointly: `unfold_2d_omnifold_unbinned.py`, `fullevent_fps_dataloader.py`,
`omnifold_nn/omnifold/dataloader.py`, and `gate2_target_runtime.py`. §2a edits the second of
those, so the **receipt moves regardless**. The live question is only whether the re-run behind
it can be avoided.)*

Note that `dataloader.py` being in that bound set is a second reason §2a routes through the
existing `normalization_factor` argument rather than editing the vendored loader: the argument
already exists, so the one vendored file Gate-2 *does* freeze stays byte-identical. (Per
`AUDIT-FINDINGS-20260729-B.md` B-1, `net.py` and `omnifold.py` are bound by nothing at all —
the freeze covers the vendored engine's plumbing but not its physics.)

This has not been confirmed. The role best placed to answer, `agy-g2-gate-verifier`, is stranded
until its session is recovered per `RESTORE-2026-08-03.md` Step 6.

## 7A. What the implementation changed about this design (2026-07-29)

Recorded here rather than by silently editing the sections above, so the design and what was
actually built can be compared.

**§2c understated the retarget, twice, and missed a file.** It says `:411-412` and `:442-443`
"both become `1e6 * R`" and that the `learned_vs_normalized_clipped_*` telemetry at `:445`/`:448`
is *invariant*. Two corrections:

1. The telemetry is invariant only **if `:445` and `:448` are retargeted too**. `refined_hist` now
   sums to `1e6*R`; leaving `clipped_norm` at `1e6` compares two differently-scaled histograms and
   inflates `rel_l1` by exactly `R`. Four sites, not two.
2. `max_relative` is **not** invariant as originally written, even after that. Its zero-guard
   `denom = np.maximum(clipped_norm, 1e-12)` is an *absolute* constant, while `occupied`
   deliberately admits cells with `clipped_norm == 0` and `refined_hist > 0` — there the
   denominator pins to the floor while the numerator scales, so `max_relative` scales by exactly
   `R`. The floor is now a fixed *fraction* of the normalization (`EPS_NORM_FRAC = 1e-18`, which
   reproduces `1e-12` bit-for-bit at `R == 1`). Benign on the frozen grid today
   (`negative_signed_cells == 0`) but the pending MeV/GeV units fix is expected to create exactly
   those cells, in the same restore window.

**And §2c's file list was incomplete.** `validate_gate2_target_receipt.py` — the *independent*
Gate-2 receipt validator, named in the Gate-2 verifier's file set — carried the bare `1e6` at four
places and was not among the files the first patch touched. Left alone it would have hard-failed a
correct post-B1 product at `:104` (a ~13.5% miss on `rtol=3e-6`) and inflated its own
`l1_fraction` by `R`: the §5 "partial fix aborts inside the restore window" failure mode, one file
to the left of where the patch looked. Retargeted, with `R` read from the receipt and corroborated
against ingredients that file derives from the dump itself — it cannot import
`step1_class_ratio` without breaking the independence charter in its own docstring, so it falsifies
the receipt's `R` rather than re-deriving it through a duplicate formula.

Both found by adversarial review of `b3751cc`, 2026-07-29.

**§2d's `check_normalization` could not be replaced in place.** The frozen launch-code test
`test_pet_nominal_gate4_validator.py` binds its two-argument signature and `ratio ≈ 1` semantics,
and editing that test would void two further bindings for no necessary reason. It was instead
generalized (`target_ratio=1.0` default — the frozen test still passes) into a primitive, and the
gate now wires a new `check_fold_forward_ratio`. Retiring the legacy entry point is queued for
the Step 2b re-issue, which re-freezes that test anyway.

**§2d asked for a tolerance and could not say what it should be.** It is now bracketed rather
than invented. With acceptance statistically independent of the truth features — the worst case,
because step 2's regressor then cannot separate the acceptance classes at all — the recursion has
a closed form:

```
push_k = R - (1-a)^k (R-1)        =>   dev_k = (1-a)^k (R-1)/R
```

**§2d's "structural floor" is a misnomer, and the closed form above refutes it.** §2d asserts
term 1 "does **not** vanish with more iterations — it is a property of the estimator, not of
finite `niter`". Wrong: `(1-a)^k → 0`. `omnifold.py:184-187` forms
`weights_pull = weights_push * new_weights`, so off-acceptance events *retain the previous push*
and catch up each iteration; only `new_weights` is pinned to 1, not `pull`. Measured deviations
9.23% / 3.69% / 0.59% at `k = 1/2/4` (R=1.30, a=0.60) — converging, not flooring. At the frozen
`niter = 2` the **value** is unchanged and the tolerance bracket stands, but it is a
finite-iteration residual and must not be cited as irreducible: that argument would justify a
permanently loose gate, and it would also mean more iterations could not improve the rate closure
when in fact they can. Corrected after adversarial review of `b3751cc`.

which `closure_b1_rate_injection.py` confirms empirically (observed vs predicted 1.1734/1.1800,
1.2577/1.2520, 1.2773/1.2923 at R=1.30/a=0.60/k=1,2,4). At the nominal (`a=0.621`, `R≈1.135`,
`niter=2`) that bound is **1.71%**, and the defect the gate must detect is **11.9%**.
`fold_forward_ratio_dev_max = 0.05` sits between them with ~2x headroom either side, and is
marked `PROVISIONAL_PENDING_CLOSURE_MEASUREMENT` in the frozen contract and in every receipt it
produces. A second, **parameter-free** check rides alongside it — the result must land nearer `R`
than `1` — which carries the broken-vs-corrected discrimination with no invented threshold, so
the gate has power even before the measurement lands.

**A trap §4's closure will spring on 08-03.** `epochs` is not the unit of optimization; steps
are, and steps scale with `N/batch_size`. At the nominal's `epochs=8` a small closure run is
optimization-limited, not floor-limited, and reads as though the fix underperforms — measured
deviation 2.6–6.7% at N=8,000, 1.8–3.4% at N=30,000, 1.4–1.6% at N=120,000, converging onto the
1.71% closed form from above. The 2M-row nominal sits far to the right of that. This is written
up at length in the closure script's docstring.

**Three §2d defects the first patch shipped, all found by adversarial review and all now fixed
with regression tests.** Recorded because each is a variant of the same failure the section exists
to prevent — a check that does not bite:

- **`R == 1` failed a correct unfold outright.** The parameter-free discriminator is
  `|ratio − R| < |ratio − 1|`; at `R == 1` that is `x < x`, False for every possible input,
  including a correct no-change result with `push == 1`. §4 explicitly contemplates `R` coming back
  near 1.0, so this was reachable. Now skipped when `|R − 1| <= tol`, where it decides nothing
  anyway, leaving the tolerance check — which is exact in that regime — to carry the gate.
- **The validator never checked it was given the dump the result was trained on.** The driver
  records `inputs_path`; nothing compared it to `--inputs`, so a different dump could silently
  supply every reference sum. The independence of the reference data is the whole point of §2d.
- **Skipping the check produced a green verdict.** `--allow-missing-fold-forward` returned
  `verdict: PASS` and exit 0, with only a buried `promotable: false` dissenting. That is B2 exactly
  one level up. It now yields `FAIL_NORMALIZATION_NOT_CHECKED` and exit 1.

**§6's open question is unchanged and still open** — whether the canonical refiner re-run can be
skipped on `w_refined` being bit-identical. §2a does not touch the refiner, and the patch leaves
`w_refined` byte-identical: the `1e6*R` factor is applied by the vendored DataLoader *after*
refinement, so `signed_target_hash` should be unmoved. That is an argument for the skip, not a
demonstration of it.

## 7. Provenance

Mechanism confirmed by four adversarial referees, each instructed to default to REFUTED, plus
direct verification of `omnifold.py:185`, `dataloader.py:110-113` (by executing the vendored
module), and the Gate-2 receipt values. The `1e6·R` shape of 2a and the partial-fix hazard in
section 5 came from `agy-pubjudgement-handoff-20260729`, improving on the `normalize=False`
variant proposed earlier. The truth-level-vs-reco-level correction in 2d is not from any
referee; it corrects an error in my own earlier recommendation to "retarget Gate-4 to ≈R".
