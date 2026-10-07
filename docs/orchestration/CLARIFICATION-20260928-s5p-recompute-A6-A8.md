# s5p (`OI-193`): the recomputation's ambiguities A6–A8 — governing text, frozen implementation, production use (2026-09-28)

**CITABLE FOR:** what the pre-production governing text says, what the frozen code does, and whether any production
decision has used either, for items A6–A8 of `HANDOFF-20260928-s5p-recompute.md` §3
(`origin/s5p-parallel-recompute-20260928` at `9b8f94a3`); the exact rulings prepared for the specification owner.
**NOT CITABLE FOR:** a ruling (none is given here); any change to the evaluator, the stopping rule, a terminal status or a
running job (none is made).

## Timing (recorded as required)

This clarification is written on 2026-09-28 at about 21:50Z, **after production outputs became visible**:
- Production began at 16:11–16:12Z, when the five `runs/prod/status/<null>-B0.json` files were written.
- Calibration and power products (about 250 at 21:45Z) have been readable since then.

What has and has not been seen:
- The controller has run only the B = 0 looks. Each B0 file reads `"reason": "no calibration product yet"`; none carries a
  statistic, p-value or decision.
- The production evaluator (`s5p_joint.py evaluate`) has not run.
- This review computed no observed statistic.
- I cannot certify what other sessions computed. The recomputation lane's `s5p_recompute_inputcheck.py` reads the observed
  data central only as a scale for median ratios.

Correction: the scheduling-change incident of 20:50Z in `state/s5p/campaign-state.json` says "made after observed p-values
became visible to the controllers". No controller had computed an observed p-value at 20:50Z; a correcting incident is
added beside it (history unedited).

Sources: the governing text is at the freeze commit `4f5a613f`, and the deployed `nd-unfolding/` code at `4f5a613f` and
`55a41765` is byte-identical (`git diff --stat 4f5a613f 55a41765 -- nd-unfolding/` lists only `s5p_requeue.py` and its test).

## A8 — the confidence level of the stopping rule's precision condition

**Governing pre-production text:**
- Amendment 1, `T7_p_value_precision`: "Monte Carlo p-values (k+1)/(B+1) with exact 95% Clopper-Pearson intervals …
  half-width <= 0.05 for p >= 0.05 and <= 0.5 p for 0.01 <= p < 0.05; below 0.01 only a one-sided bound …; a valid
  sequential stopping rule … may replace a fixed B if frozen at Stage 3".
- Amendment 5, `p_value` and `precision`: reporting at 95%, "B = 1999 meets T7".
- **Amendment 7, `calibration.sequential_rule`** (frozen): "stops the null when `s5p_inference.sequential_decision` stops
  both (99.5% Clopper-Pearson look interval: no decision threshold straddled, T7 precision at the point estimate, or an
  upper end below every threshold)".
- Amendment 8, `not_changed`: the sequential rule.

**Frozen implementation (fact):**
- `nd-unfolding/s5p_inference.py:89-111` at `4f5a613f` evaluates all three conditions on ONE interval, the Clopper-Pearson
  interval at `look_level = 0.995`. Its docstring says the same, "(Bonferroni over at most ten looks)".
- The tier comes from the point estimate p = (k+1)/(B+1).
- Boundaries:
  - straddle is `lo < th <= hi`;
  - the one-sided branch is `hi < min(thresholds)`;
  - precision is `half <= bound`.
- `s5p_seqstop.py:64-70` applies it to the CLAIM k, B of each test, with thresholds {0.05/j, j = 1..10} ∪ {0.01, 0.05},
  and with the B ≥ `min` floor (1200 for MnvTune and GENIE CV).

**Production use:** none yet. No look with B > 0 exists.

**Resolved by an authoritative record: yes, the level.**
- The frozen admission defines the stop operationally as "when `s5p_inference.sequential_decision` stops both".
- Its parenthetical places all three conditions after the colon of "99.5% Clopper-Pearson look interval:".
- T7 fixes the 95% level of the *reported* p-value's precision. Every rule stop meets it: Clopper-Pearson intervals are
  nested, so the 95% interval lies inside the 99.5% one, and a 99.5% half-width within the bound implies a 95% one within
  it.
- So the 99.5% reading is the authorized text, and the implementation agrees with it. The recomputation's primary A8
  reading (half-width on the 99.5% look interval) already matches.

**Not resolved by text (implementation fact only): the closure of the boundaries.**
- The admission does not say whether "straddled" and "below" are closed or open.
- Closure matters only where an interval end equals a threshold, or a half-width equals its bound, exactly. A scan of
  every k at every B = 1..1999, at the 99.5% level, against the twelve thresholds finds:
  - one exact equality, at B = 2, k = 2 (lo = √0.0025 = 0.05);
  - for B ≥ 100, a closest approach of 4.5e-9 (B = 1507, k = 24, lower end vs 0.05/6);
  - a closest approach of a half-width to its T7 bound of 3.5e-8.
- So no look with B ≥ 100 can be decided by the closure. A ruling is needed only if a look at B < 100 ever occurs (it
  would need more than 100 of a batch's 200 seeds lost).

**If the owner nevertheless read T7's 95% into the look (optional ruling R8):**
- Text: "The precision condition of the sequential rule is evaluated on the 95% Clopper-Pearson interval of k/B; the
  straddle and one-sided conditions remain on the 99.5% look interval."
- Consequences:
  - The 95% reading stops at every look where production stops, and possibly earlier. For example, at p ≈ 0.5 it is
    precise from B = 600, against 1000 under the 99.5% reading, on the 200-grid. So production can never make a
    terminal stop that this reading forbids.
  - Production would continue past looks where this reading stops. That costs up to about 400 experiments per affected
    null (about 10 CPU node-h at 720 s each) and changes the final B, not the validity of p at the B reached (amendment 7).
  - No running job would need to change. The recomputation's verdict on each look would record "continued past a
    permitted stop".

## A6 — union versus cross product of the process-shift and M1 variants

**Governing pre-production text:**
- **Amendment 7, `claims.rejection`**: "the CLAIM p-values: the largest p over the process-shift variants (bias-aligned
  upper-bound D, c in 0, 1/2, 1) AND the sub-fine-residual variants F +- 2 delta_M1 (kappa = 2; …)".
- Amendment 7 `calibration.m1_shift`: "kappa 2 (claim), kappa_robust 3 (report); MnvTune: none".
- Amendment 7 `conditions_stated_with_every_claim[0]`: "its effect enters the claim rule as the kappa = 2 variants and its
  size in null-T units … is committed before the first look".
- Confirmation review F5, required change 5: "Recommended: an M1 variant F ± κ·δ_M1 inside the claim rule, with κ
  declared".
- The size committed before the first look ("the M1 claim variant 0.5–2.0 null SD", freeze commit `4f5a613f` message;
  `state/s5p/stage3/prefreeze/units.json`) is computed by `s5p_prefreeze.py:51` as max over ±2δ_M1 alone, with no D term.

**Frozen implementation (fact):**
- `s5p_joint.py:228-233, 239-258` builds the UNION: {c·S : c ∈ (0, ½, 1)} ∪ {+2δ_M1, −2δ_M1}. That is five variant
  ensembles per external null, and three for MnvTune (`m1_shift` = `none`).
- claim p = the largest p over them.
- The same five ensembles are the null set of the claim-rule power (`s5p_joint.py:370-376`).
- `tests/test_s5p_joint_e2e.py:109` pins a fixture's variant set to {"0.0", "m1+2", "m1-2"}.

**Production use:** none yet. It is used at every look of GENIE CV, MEC, NuWro and GiBUU (`s5p_seqstop.py:64-68` reads
the claim k, B), and by the evaluation's decisions and claim-rule power; no look with B > 0 exists and the evaluation has
not run.

**Resolved by an authoritative record: yes, in the frozen text's own terms (a textual reading).**
- The text names two sets of variants and takes the largest p over both.
- Each M1 variant is written as "F ± 2 δ_M1", the calibration ensemble shifted by the M1 residual alone.
- A combined shift F + c·S ± 2δ_M1 belongs to neither named set.
- The review's formula is the same, and the only M1 size committed before the first look is that of the uncombined
  variant.
- The implementation agrees. The recomputation's primary A6 reading (union) matches.

This is my reading of the authorized text, not a ruling. An independent reviewer found it ambiguous, so the owner may
confirm or overrule it (R6).

**Ruling R6, if the owner does not accept the union reading.**
- Text: "The claim variants of an external null are F + c·S + s·2δ_M1 for c ∈ {0, ½, 1} and s ∈ {−1, 0, +1} (nine), and
  the claim p is the largest p over them; the κ = 3 report uses s·3δ_M1 in the same way."
- Consequences:
  - For every external null the claim p is ≥ the union claim p (the nine include the five). A rejection can become
    'undetermined' or 'not rejected'; claim-rule power at GENIE CV cannot rise.
  - The frozen controller evaluates the union at every look. A look can therefore stop a null under the union that the
    cross product would continue, and a stop is terminal.
  - Adopting R6 changes the frozen claim rule after production outputs became visible. It needs a new amendment, a
    controller change and runner restarts, none of which this request authorizes.
- Deadline (containment): a ruling other than the frozen union should land BEFORE the first look with B > 0 of GENIE MEC,
  NuWro or GiBUU (no B floor). GENIE CV cannot stop before B = 1200, and MnvTune has no M1 variant. Estimate from the finished products at 21:50Z and
  the last 3 h rate (batch 0, throttle 2): MEC 52/200 at ~11/h, so its look falls near 2026-09-29T11Z at the earliest;
  GiBUU 37 at ~9/h (~T15Z); NuWro 37 at ~8/h (~T19Z). A batch's look waits for its slowest task, so these are lower
  bounds.
- If no ruling lands by then, production continues on the frozen union, which the text supports. No containment action
  is recommended while the implementation and the text agree.

## A7 — the κ = 3 robustness flag: per test or a Holm re-run

**Governing pre-production text:**
- Amendment 7, `claims.rejection`: "Every rejection is also flagged 'robust to the sub-fine residual' or not at kappa = 3
  (report only, frozen now)".
- Amendment 7 `calibration.m1_shift`: "kappa_robust 3 (report)".
- Confirmation review F5: "Minimum: a frozen 'robust to the sub-fine residual' flag, otherwise 'rejected conditional on
  the fine-grid null'".

**Frozen implementation (fact):**
- `s5p_joint.py:233, 252-260`: robust claim p = the largest p over the claim variants ∪ {+3δ_M1, −3δ_M1}. The ±3δ are
  alone, not combined with c·S, so this is the union again (A6). MnvTune's robust p is its claim p.
- `s5p_joint.py:346-351`: `holm_determined` is re-run on the ten robust claim p's (`decisions_robust_kappa`).
- `robust_to_the_sub_fine_residual[test]` = (the decision label in `decisions` == the label in `decisions_robust_kappa`),
  for all ten tests. For a rejection it is true iff the test is also 'rejected' in the re-run.
- `tests/test_s5p_joint_e2e.py:112` pins only the field's presence.

**Production use:** none. The controller never reads it (`s5p_seqstop.py` uses only the claim p), so it cannot affect
stopping. The evaluation has not run.

**Resolved by an authoritative record: no.** The text fixes κ = 3, "every rejection" and "report only". It does not fix
the procedure (a Holm re-run or a per-test comparison), nor what a non-rejection's field means. That the code re-runs
Holm is an implementation fact, not an authorized interpretation.

**Ruling R7 (needed; exact alternatives):**
- **(a) Holm re-run (the frozen implementation):** "A rejection is robust to the sub-fine residual iff it is 'rejected'
  by `holm_determined` applied to the ten κ = 3 robust claim p-values (claim variants ∪ F ± 3δ_M1); the flag is reported
  for rejections only (the field's value for other tests is not a flag)."
- **(b) Per test:** "A rejection at Holm step i of `decisions` (threshold α/(m−i)) is robust iff the 95% Clopper-Pearson
  interval of its κ = 3 robust claim k/B lies entirely below that same threshold."

Consequences, both report-only (no claim decision, no stop, no status changes under either):
- (a) lets another test's κ = 3 p block a rejection: an earlier step turns 'undetermined', and the step-down stops.
- (a) also lets reordering move a test to a different threshold.
- (b) isolates each rejection at its own step.
- So the two can disagree in either direction on the flag of a given rejection.
- Under both, the robust variant set is the union unless R6 rules otherwise.

## What this record changes

Nothing in code, queues, statuses or jobs. It adds the correcting incident noted above to `state/s5p/campaign-state.json`.
