# PREDECLARATION 2026-08-11 — does the Branch C iteration-dynamics defect survive the LR anneal?

**Owner:** Session C (PET), quarantine cause 5 lane.
**Predeclared before any run.** The launcher is `nd-unfolding/pet/sbatch_step1_trajectory_annealed.sh`
and this file must be committed before it is submitted.

## The question, and why it has not been asked

Job `56525829` measured the per-iteration step-1 trajectory and localized a training defect to
**iteration dynamics after initial feedback**. That measurement was taken on the artifact at
`pet/fullevent_nominal/` — job `56445883`, trained **2026-08-08**, i.e. **before** the fit-time LR
anneal was adopted on 2026-08-10.

`KNOWN_ISSUES.md:407-443` records the reason that matters: the engine's per-iteration anneal is dead
code, so in the pre-anneal configuration *every* step-1 and step-2 fit runs at the full learning rate
with warm-started weights, and that entry names it a **candidate mechanism for the degradation** — the
regime in which a warm-started classifier's high-ratio tail is reshaped hard enough to collapse
(`p95` 4.6474 → 1.4682 across the three iterations of `56525829`).

An annealed **production** artifact now exists (`pet/fullevent_nominal_annealed/`, job `56563761`,
2026-08-10) and **nobody has run the trajectory decomposition on it.** So the campaign does not know
whether the Branch C defect is a property of the estimator or a property of the LR policy that has
since changed. That is the single cheapest unasked question in this lane: it needs **no training**,
because the annealed artifact carries the same per-iteration checkpoint inventory as the pre-anneal
one and the trajectory harness resolves its checkpoint folder from the artifact's own
`inference_contract["weights_folder"]`.

**Verified before predeclaring, from the artifacts' own contents rather than from a launcher or from
memory:**

| | pre-anneal (`fullevent_nominal/`) | annealed (`fullevent_nominal_annealed/`) |
|---|---|---|
| `fold_forward_sum_w_push_reco` | 736746.2709517315 | 1084052.9829474115 |
| `fold_forward_sum_w_reco` | 1000000.0282607947 | 1000000.0282607947 |
| ratio | 0.7367462 | 1.0840530 |
| dev vs `R = 1.1240802949941018` | **−0.34458** | **−0.03561** |
| `inputs_sha256` | `fa6b3463…` | `fa6b3463…` (identical) |
| `seed_policy` core | seed 42, subsample 0, niter 3, epochs 8, 2e6 events, batch 512 | identical |
| `lr_policy_realized` | absent (no anneal) | `verified_from_optimizer: True`, 2 fits @1e-4, 4 @1e-5 |
| `cap_saturation_frac` | 0.0 | 0.0 |
| per-iteration checkpoints | iter0/1/2 step1+step2, `iter2_*_final` | same inventory |
| `.done` marker | — | `job 56563761`, `marked_at 2026-08-10T18:00:43Z` |

The two artifacts differ in **exactly one policy dimension** and agree on input hash and seed policy,
which is what makes this a controlled comparison rather than two unrelated runs.

## What the run does — two arms, and the first is a positive control

**Arm 1 (CONTROL, pre-anneal).** Run `step1_increment_trajectory.py` on the pre-anneal artifact,
gated against the **committed** receipt `STEP1_DECOMPOSITION.slurm-56445883.json`. This must reproduce
`56525829`'s three anchors. Its purpose is not the physics — it is to prove **the instrument is intact
in this environment before the treatment arm is believed.** Two runs of a broken instrument agreeing
is determinism, not corroboration (BEN-088 rule vi), so the control is gated against a *committed*
anchor rather than against itself.

**Arm 2 (TREATMENT, annealed).** `gate_ab_push_provenance.py` → `step1_pull_push_decomposition.py` →
`step1_increment_trajectory.py`, all on the annealed artifact. The annealed arm has no committed
decomposition receipt, so its trajectory gate is a **same-session self-consistency check, not a
reproduction of an independent anchor.** That is strictly weaker than Arm 1's gate and is stated here
so no reader mistakes the two for the same standard of evidence. Arm 1 is what licenses believing
Arm 2's instrument.

## THE BRANCH SET — predeclared, three outcomes, UNRESOLVED is real

Read on `end_to_end_achieved_over_required` and `end_to_end_sign_is_wrong`, **not** on
`r1_achieved_over_required_FIRST_LEG_ONLY_NOT_LIKE_FOR_LIKE`. This is stated first because the
existing ledger row for `56525829` quotes the first-leg field under a like-for-like heading, which is
BEN-077's class and is being corrected in the same commit series as this file.

**Branch REPAIRED** — for **both** iterations 1 and 2: `end_to_end_sign_is_wrong == False` **and**
`|end_to_end_achieved_over_required − 1| ≤ 0.10`. Reading: the dead LR anneal was the dominant
mechanism of the Branch C defect, and the defect is a property of the retired LR policy rather than of
iteration dynamics as such.

**Branch PERSISTS** — at least one of iterations 1, 2 has `end_to_end_sign_is_wrong == True`, i.e. the
end-to-end achieved factor moves *against* its required direction, at an iteration where the sign
carries information (see the domain-of-validity guard below). Reading: the defect is in iteration
dynamics and survives the anneal; the anneal reduced the *magnitude* of the fold-forward deficit
(−34.46% → −3.56%) without repairing the mechanism.

**Branch UNRESOLVED** — anything else, and specifically each of these, none of which may be re-read as
the nearer of the other two:
1. **Domain-of-validity failure.** Any iteration where `|r1_required_mean − 1| < 0.02`. Near
   `push ≈ R` the required correction goes to 1 and **sign stops discriminating** — the criterion
   returns *no information*, not *pass*. This is failure mode (3) of
   `FINDING-20260810-criteria-that-answer-a-different-question.md`, recorded there against this exact
   criterion, and the annealed arm sits at `push = 1.0840530` against `R = 1.1240803`, i.e. much
   closer to the no-information point than the pre-anneal arm ever was. **This is the most likely
   single outcome of this run and it is predeclared as UNRESOLVED, not as a pass.**
2. Signs correct at both iterations but `|e2e/required − 1| > 0.10` at either.
3. Split outcome: iteration 1 correct-signed, iteration 2 wrong-signed, or the reverse.
4. Arm 1's reproduction gate fails (`rel_dev > REPRO_RTOL = 0.02` on any of `increment1`,
   `push_prev`, `push_final`). Then the instrument is not established and **Arm 2 is not read at
   all**, whatever it printed.
5. Arm 2's Gate A fails (`A1_mc_indices_bit_exact` or `A2_truth_norm_bit_exact` false). The
   decomposition driver fails closed here by design and that is the correct behaviour.

**Materiality floor.** `REPRO_RTOL` is 0.02 and the best-epoch-vs-final checkpoint gap is ~1.3%
(BEN-043), so no difference below 2% between the two arms is claimed as an effect regardless of which
branch fires.

**What this run cannot do, stated up front.** It does not lift Branch C, it is not a cross section, it
produces no uncertainty and it discharges no quarantine cause. It also does **not** license promoting
the annealed artifact: that is a publication-grade promotion decision, it is Joseph's, and the
authorization basis for it is currently UNRESOLVED (Session A, 2026-08-11, measured against the
`[MNV-AUTO]` thread).

**Instrument-family constraint, checked rather than assumed.** The 2026-08-11 retraction
(`KNOWN_ISSUES.md:503-522`) imposes a standing constraint: any diagnostic run through the
`diagnose_step1_annealed_lr.py` wrapper family is **one draw from an sd ≈ 0.025 distribution** and may
not be quoted as a point value. **That constraint does not reach this run, and the reason is
structural, not a judgement call:** that family monkeypatches `omnifold.MultiFold` with a six-override
instrumentation subclass and *trains*, so each invocation is a fresh draw. This chain trains nothing —
it loads saved `.weights.h5` checkpoints and evaluates them through
`extract_fullevent_fps._engine_reweighter`, so repeated runs differ only by GPU inference
nondeterminism, which BEN-043 measured as negligible against the quantities here. Arm 1 tests exactly
this: if inference were a meaningful draw, the committed-anchor gate would not reproduce.

## Provenance the run must bind (BEN-083)

The harness must print, and the receipts must carry, the resolved sha256 of every driver actually
imported — `train_fullevent_nominal.py`, `extract_fullevent_fps.py`, `step1_increment_trajectory.py`,
`step1_pull_push_decomposition.py`, `gate_ab_push_provenance.py` — hashed from `module.__file__` after
import, not from the path the launcher set. `sys.path[0]` is the executed script's directory and
outranks `PYTHONPATH`, so a pin on a path proves nothing about which copy was imported.

## Receipt-ingredient requirement (BEN-077, CONVENTION-receipt-ingredients.md)

Every derived quantity ships its operands, so the reported numbers can contradict each other. For each
iteration of each arm the receipt carries `push_prev_mean_w_reco`, `r1_mean_w_reco`,
`r1_required_mean`, `push_mean_w_reco`, `push_dev_vs_R`, the end-to-end achieved factor, the ratio
percentiles, `r1_cap_saturated_frac` and the checkpoint tier — which is what
`step1_increment_trajectory.py` already emits. No verdict is reported without them.
