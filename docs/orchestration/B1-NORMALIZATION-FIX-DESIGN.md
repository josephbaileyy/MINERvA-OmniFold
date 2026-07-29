# B1 normalization fix — design and rationale

**Status:** proposed, not implemented. Three receipt-frozen files change; none has been
touched. `R` is unmeasured until the 2026-08-03 restore.
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
through acceptance and require it reproduce the background-subtracted data yield,

```
pot_scale * sum(w_truth * push over pass_reco)  ==  n_data - pot_scale * sum(w_bkg)
```

within tolerance. This has an exact target that is measured rather than modelled, it is the
physical statement "the result, folded back, reproduces what we saw," and — decisively — **it
fails the current broken result while passing a corrected one.** It converts Gate-4 from
tolerating this defect into detecting its whole class.

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

Can the Gate-2 re-issue be **validator-only**? The refiner runs upstream of the
normalization, so `signed_target_hash` should be unchanged and `w_refined` bit-identical — in
which case only the assertion target moves and no canonical refiner re-run is needed. This
has not been confirmed. The role best placed to answer, `agy-g2-gate-verifier`, is stranded
until its session is recovered per `RESTORE-2026-08-03.md` Step 6.

## 7. Provenance

Mechanism confirmed by four adversarial referees, each instructed to default to REFUTED, plus
direct verification of `omnifold.py:185`, `dataloader.py:110-113` (by executing the vendored
module), and the Gate-2 receipt values. The `1e6·R` shape of 2a and the partial-fix hazard in
section 5 came from `agy-pubjudgement-handoff-20260729`, improving on the `normalize=False`
variant proposed earlier. The truth-level-vs-reco-level correction in 2d is not from any
referee; it corrects an error in my own earlier recommendation to "retarget Gate-4 to ≈R".
