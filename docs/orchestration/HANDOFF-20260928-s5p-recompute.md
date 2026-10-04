# s5p Stage 6: independent recomputation of the joint-inference p-values and decisions — handoff (2026-09-28)

**CITABLE FOR:** where the independent evaluator is, what it was tested against, the readings it takes of the
frozen specification (ambiguities), and the exact command that performs the final verification once production is
terminal. **NOT CITABLE FOR:** any p-value, rejection, power statement, grade or adoption; **the final
verification has NOT been performed** (production was at calibration batch 0 when this was written). Agreement,
when it is measured, verifies the calculation from the products; it does not establish the scientific adequacy of
the calibration (the nuisance model, the pseudo-experiment process, the conditions of amendment 7 `claims`).

Task pointer: `docs/orchestration/HANDOFF-20260928-s5p-parallel-tasks.md` §1 (at `origin/main` `12991771`).
Branch `s5p-parallel-recompute-20260928`, worktree `../MINERvA-OmniFold-s5p-recompute` (created from `12991771`).
Cluster scratch (mine only): `/pscratch/sd/j/josephrb/s5p-parallel-recompute/`.
**Commits (updated 2026-09-29, s5p-F4 correction, §5.6):**
- **`0142a228` is the reviewed executable code and the deployment target.** It is the final reviewed commit of the
  s5p-F4 correction: a fresh independent read-only review, CHANGES REQUIRED at `04a1d313`, then fixes verified YES
  at `0142a228` (`REVIEW-20260929-s5p-recompute-f4-correction.md`). The comparer in it is byte-identical to
  `1bfd8910`. Deploy from this commit only (§5.2). Every later commit on this branch must be documentation only
  (`git diff 0142a228 <tip> -- nd-unfolding/` empty); §5.2 refuses otherwise.
- **`1bfd8910` is SUPERSEDED as the deployment target.** It was the final reviewed commit of the comparer (three
  review rounds, fixes verified YES), and its comparer is unchanged. Its evaluator restricts the calibration
  ensemble to a seed range (withdrawn A13, finding s5p-F4) and must not be deployed.
- **`04a1d313` is an intermediate, not a deployment target:** the first F4 correction, whose look loop the review
  found defective (F1 MEDIUM).
- **`4a772838` is a historical checkpoint, not the deployment target.**

**STATUS: FINAL VERIFICATION PENDING.** Production was non-terminal when this was last updated (2026-09-29
~17:00Z: 0/5 final statuses, 8 s5p cal/pow jobs queued, batch 1 running, no `joint-evaluate.json`). Nothing below
is a verification result.

## 1. Source and contracts verified (2026-09-28)

- `4f5a613f` is "Amendment 7 FROZEN"; it is an ancestor of `55a41765`, which is an ancestor of `12991771`.
- `docs/orchestration/state/s5p/prod/design.json` sha256 `404446eb2a77…6285` at all three commits; the production
  controllers' status files record the same `design_sha256` and `v_sha256 35979ef7…`.
- `git diff 4f5a613f 12991771` over `contract*.json`, the exception, the three reviews, `nd-unfolding/s5p_*.py`,
  `prod/design.json`, `stage1/` and `s5c/contract.json`: only `nd-unfolding/s5p_requeue.py` (+52 lines, the
  scheduling change) differs.
- Specification read: `state/s5p/contract.json`; amendments 1, 5, 6, 6b, 8, 7; the exception
  `EXCEPTION-20260927-s5p-pilot-negative-rate-resubmission.md` (it governs product construction — negative-ratio
  clipping — and has no evaluator content); the three reviews; the implementation conventions of the task pointer.
- The production modules `s5p_joint.py`, `s5p_inference.py`, `s5p_seqstop.py` were read **only** through an AST
  dump of their module/function docstrings and signatures (as the pointer permits), plus the string-literal key
  names that `s5p_joint.main/test_null` and `s5p_seqstop.main` write (to map the comparison; no code bodies).

## 2. What was built (this branch)

| file | role |
|---|---|
| `nd-unfolding/s5p_recompute.py` | the evaluator: J geometry, surrogates, statistics, variants, claim p, Holm with determinacy, κ = 3 flag, power, implied size, observed-jitter p, sequential-rule re-evaluation at every look; CLI `evaluate` / `compare` |
| `nd-unfolding/s5p_recompute_compare.py` | compares a recompute output with production's `joint-evaluate.json`; lists every production numeric leaf it could not map |
| `nd-unfolding/tests/test_s5p_recompute.py`, `tests/s5p_recompute_toy.py` | 58 controls (below, §3.1, §3.2, §5.5); a synthetic world in the production file formats |

Tests (`python3 -m pytest -q nd-unfolding/tests/test_s5p_recompute.py`: **67 passed** at `0142a228`, ~30 s; 58 at
`1bfd8910`; the nine added by the F4 correction are listed in §5.6):
no import of the three production modules (AST); Clopper–Pearson closed form and the reviews' own numbers
(review 1: `[0.0057, 0.0148]` at p = 0.01, B = 1999; review 2 M3: determined k at 0.005 is `{0}` at B = 800 and
`{0..3}` at B = 1999, rank rule `{0..3}` at 800); statistics (total = inverse quadratic form; shape invariant to
the dropped cell, to normalization and to a unit change); rank ties counted (`>=`); **size under
exchangeability** (P(p ≤ 0.05) within 3 SE of 0.05 for both tests, claim never less conservative); variant sets
and the claim = largest count; the bias-aligned shift (positive along b; zero when the pairs are anti-aligned);
**Holm with determinacy** (rejected / undetermined-stop / not-rejected-stop, inheritance, point Holm differing from
determined); **sequential rule** (the review-described stops at B = 200/400/1200, straddling, T7 precision
branch, m-dependence of the smallest threshold, `min_B` respected, looks paired with status files); end-to-end on
the toy: a brute-force known answer without surrogates, the GiBUU `pz_lt_6` domain, **incomplete products**
(missing seeds, a partial file, a product beyond the final B — kept, count ≠ final B — all reported, not repaired),
**budget-terminal** stops (B = 0 → p = 1, "not calibrated", undetermined at its step; a budget stop at B < max
uses the B reached), draws keyed by seed (independent of which other products exist), refusal of a pseudo-seed
mismatch and of a wrong declared digest, determinism (two runs byte-identical), rejection of a tilted truth,
an incomplete power set, power at 0.005 identically zero below B = 736; the comparer's agreement and its
detection of a changed count, statistic and decision, and of an unlocatable null.

Checks on the real frozen inputs (read-only; `nd-unfolding/s5p_recompute_inputcheck.py`, run in my scratch):
MnvTune J integrals equal `ratios/nullsJ/null-mnvtune_v1-J.json` `numerator_cell_integrals` exactly (max rel 0.0);
for all four external generators δ_M1 = f(fine) − f(mid) of the `units.json` asimov inputs reproduces
`stage3/m1/fine-minus-mid-<g>.npz` `D_J` to ≤ 2.5e-13 relative; the 20-jitter rounding SD has median 0.228% (review
1: 0.228%); the lateral Δ_b medians equal V's recorded `lateral_symmetry.median_abs_delta_rel` to 1e-16;
V's names equal the s5c supported J cells; GiBUU domain 72 cells.

**Batch-0 smoke run — a preliminary consistency check only; NOT evidence about the metric or the surrogates.**
On the calibration products present at batch 0 (27–47 per null; `smoke/products_smoke_full.json` and
`smoke/dryrun-nonterminal.json` in my scratch) every statistic is finite, and every product's meta carries the five
design lateral bands. The CLI `evaluate` ran all five nulls in 3 s. BLAS is pinned to one thread in the module
(under login-node thread contention one 109-cell null took 72 s instead of 0.3 s). `--require-terminal` exited 4
and wrote nothing. p-values at these B mean nothing and are not quoted.

⚠ **WITHDRAWN 2026-09-28: the sentence "the mean null T equals the prefreeze lambda plus the cell count for every
null".** It appeared in this file's first version and in the message of commit `27c7ff37`. It was stated without
a sampling uncertainty, and with one the agreement fails. Its reference quantity is also not the expectation of T:

| null | B | cells n | mean null T_total ± SE (SD/√B) | λ (units.json) + n | z | \|b̂\|²_W (ensemble) | mean − \|b̂\|²_W |
|---|---:|---:|---:|---:|---:|---:|---:|
| MnvTune_v1 | 27 | 109 | 44.6 ± 2.4 | 0 + 109 | −26.6 | 3.7 | 40.9 |
| GENIE_2_12_10_CV | 40 | 109 | 523.2 ± 8.5 | 559.2 | −4.2 | 421.2 | 102.0 |
| GENIE_2_12_10_MEC | 47 | 109 | 405.3 ± 4.8 | 426.7 | −4.5 | 313.0 | 92.3 |
| NuWro_21_09 | 36 | 109 | 6347.0 ± 28.1 | 6453.0 | −3.8 | 6224.7 | 122.3 |
| GiBUU_2019 | 33 | 72 | 1776.1 ± 13.5 | 1783.6 | −0.6 | 1734.0 | 42.1 |

Reading:
- E[T] = |b|²_W + tr(W⁻¹Σ). Here Σ is the covariance of these experiments' residuals, and W = V + diag Var μ is
  not Σ. The MnvTune null (b ≈ 0) measures its trace term at about 41, not 109.
- λ in `units.json` is |b|²_W of a full-MC noise-free asimov, a different operand from the half-MC calibration
  ensemble.
- So "λ + n" was never the expected value. With B = 27–47 the SEs above assume independent draws, and the SDs are
  themselves uncertain by about 1/√(2B) ≈ 11–14%.
- What the smoke run does establish: the pipeline loads and evaluates the real products, and the orders of
  magnitude are sensible (external nulls dominated by their bias term).
- It is not a check of the metric, the surrogates or production's calculation. Only the final comparison
  (§5) is.

## 3. Ambiguities: governing text, readings, consequences

Every reading used is embedded in each output (`ambiguities`). **None was chosen by looking at production output.**
"Alt. computed" says whether the competing reading is computed beside the primary one in the same run. **2026-09-29:** A7 is
ruled by the owner. A6 and A8 are assessed by this lane as resolved by the frozen text (assessment document), with
no owner ruling. The primary readings are unchanged, and the alternatives stay computed as labelled diagnostics. A
reading is never swapped to match production.

| # | governing text | reading used (primary) | competing reading(s) | affected outputs | decision could change? | resolved by an authoritative record? | alt. computed |
|---|---|---|---|---|---|---|---|
| A1 | am. 5 `nuisance_model.surrogates`; handoff §1 conventions (terms listed, composition not stated) | lateral, then ×(1+0.014z) (scales lateral), then rounding noise | ×(1+0.014z) applied to f only, or last | every simulated T (second order: 0.014 × ~2% lateral) | only via a rank flip at a near-tie; not expected | no | no (a diagnostic if T disagree) |
| A2 | handoff §1 "noise on each experiment's J cells" | draw 109 cells in V order, then restrict | draw only the domain cells | GiBUU simulated T only | yes for GiBUU in principle (a different random stream changes every draw) | no | no |
| A3 | am. 5 "N(0, diag s_num²)" | `standard_normal(109)` × SD | `multivariate_normal` (different stream consumption) | all simulated T | as A2 | distribution yes, stream no | no |
| A4 | `s5p_inference` docstring (Jacobian at f); am. 5 "residual gets −eps" | shape: p(f) vs p(μ+eps) | p(f−eps) vs p(μ) | simulated T_shape | only at a near-tie | Jacobian at f: yes; eps placement: no | no |
| A5 | `s5p_joint.shift_vector` docstring (b = ensemble mean − μ; a, se over F4 pairs) | b from surrogated f without eps; se = SD(ddof 1)/√16; one S for both tests | eps included in b; ddof 0; a separate S for the shape test | S → the c-variant p-values | **yes**: through the claim p when a c-variant is the argmax near a Holm threshold | b, a, se: yes; eps, ddof, shape S: no | no |
| **A6** | am. 7 `claims.rejection` "process-shift variants … AND the sub-fine-residual variants F ± 2δ_M1" | UNION: {cS} ∪ {±κδ} (5 variants) | cross product cS + sκδ (9 variants; larger combined shifts → larger claim p) | claim p of the four external nulls, Holm decisions, power at GENIE CV, sequential looks | **yes** (usually a rejection becoming undetermined or not rejected; since Holm with determinacy is not monotone in k across unequal B (§3.2), rarely the reverse), bounded: cS is 0.024–0.068 null SD beside 0.55–2.0 for 2δ | **yes, by text**. Revised 2026-09-29: this lane's assessment `ASSESSMENT-20260929-s5p-recompute-A6-A8.md` §1 agrees with the campaign's clarification. **No owner ruling.** | **yes**: `product_reading`, `family.holm_product_variant_reading`, `decisions_changed_by_product_reading` (labelled diagnostic) |
| **A7** | am. 7 "Every rejection is also flagged 'robust to the sub-fine residual' or not at kappa = 3 (report only)" | **RULED 2026-09-29**: the full Holm re-run at κ = 3; labels "robust to the sub-fine residual" / "not robust" / "not applicable" (§3.2) | (b) per test at the rejecting step's threshold (non-adopted) | the reported label only | no claim decision (report only) | **yes: owner ruling** `RULING-20260929-s5p-A7-robustness-flag.md` (origin/main `4a1d931c`), for the procedure and the labels | the ruled labels; (b) as a labelled diagnostic |
| **A7-VS** | the κ = 3 **variant family**; the frozen text (am. 7 "…at kappa = 3"; `kappa_robust 3`; prefreeze "3 M1 (the robustness variant)") does not fix it | **RULED 2026-09-29 ~04:33Z, report only: REPLACE**, i.e. {cS} ∪ F ± 3δ_M1; full Holm re-run (§3.2) | *keep both* (claim variants ∪ F ± 3δ_M1, the frozen implementation as the campaign reports it) | the reported κ = 3 label | the label only, never a claim | **yes: owner ruling**, an explicit clarification made then, **not** a recovered pre-production definition (`RULING-20260929-s5p-A7-VS-kappa3-variant-set.md`; campaign record on origin/main `67eadf25`) | ruled: `family.robust_labels`, `holm_at_kappa_robust`; diagnostics: `keep_both_kappa3_diagnostic`, `frozen_boolean_equivalent_diagnostic`; `kappa3.tests_where_the_sets_differ` |
| **A8** | am. 7 `sequential_rule`; `sequential_decision` docstring "(b) meets the T7 precision at the point estimate" | half-width on the 99.5% look interval; "contains" closed | (i) half-width on the 95% interval; (ii) open containment; (iii) both | whether each look should have stopped (the sequential verification verdict), not the p at production's B | the verdict on production's stop: **yes**, only at B ≤ 800 and only through (i) (§3.1); (ii) at no B = 1..1999 | **level: yes, by text**. Revised 2026-09-29: assessment §2 agrees with the clarification. Closure: not by text, immaterial at every B. **No owner ruling.** | **yes**: `sequential.a8_sensitivity` (labelled readings; only the primary gives `stop_verdict`) |
| A9 | am. 7 "a budget stop at B = 0 leaves the null 'not calibrated' (it stays in the Holm family with p = 1)" | interval [0, 1] → 'undetermined' at its step, labelled 'not calibrated' | 'not rejected' at its step | labels of that null (and of equal-p tests after it) | no rejection can change (p = 1 is last) | label and p: yes; step outcome: no | no |
| A10 | none (ties unaddressed) | family order (design null order; total before shape) | any other stable order | Holm labels at exactly equal claim p | only with equal p and different B | no | no |
| A11 | `power_determined` docstring (k = largest count over null variants); design `power.*.surrogate_seed0` | alternatives unshifted, own surrogates, eps keyed by the set's seed0 | variants applied to the alternative too | power | — | yes, in substance | no |
| A12 | `s5p_joint` docstring "null draws shifted by c D against the unshifted ensemble" | full unshifted ensemble (draw's own unshifted T included) | leave-one-out | implied size; the "not calibrated for the data process" flag (> 0.08 at c = ½) | the flag near 0.08: yes; claims: no | no | no |
| A13 | am. 7 `sequential_rule` "the finished products (partials excluded)"; `product_files` / `calibration_count` docstrings | **REVISED 2026-09-29 (s5p-F4, §5.6):** every finished product of the null's glob (a name containing `.partial` excluded), **no seed-range restriction**; B = its count; a count ≠ the final status's B is reported (`count_mismatch`), never repaired; missing seeds are a separate diagnostic over the submitted-batch span (`seed_gaps`) | refuse on a count mismatch (production's evaluator is said to) | B, every p, every look, power | only if production's product set differs from the final B (reported) | ensemble: **yes, by text**; mismatch handling: no | the mismatch is reported, not repaired. **WITHDRAWN reading** (in force at `1bfd8910`): "finished products with seed in [base, base + final B)"; kept in the code as `A13_withdrawn_20260929` |
| A14 | am. 7 `non_rejection` (B ≥ 1200 floor so 0.005 is attainable) | power against the null's final ensemble | power as the sequential procedure would behave on alternative data (review 4 F4 option) | power at 0.005 | — | yes (the floor was the adopted remedy) | no |
| — | am. 7 "a k = 0 decision needs B >= 737" | exact two-sided 95% CP: B ≥ 736 suffices | — | none (the floor is 1200) | no | arithmetic | — |

### 3.1 A8 sensitivity (computed; the primary reading unchanged)

The stopping condition is now a pure function `stop_condition(look, precision, p, thresholds, boundary)`. It is
evaluated under four labelled readings (`A8_READINGS`): `primary` (precision on the 99.5% look interval,
closed), `A8_alt_precision_95`, `A8_alt_open_boundaries` and `A8_alt_precision_95_open`. Condition (a), no
threshold in the 99.5% look interval, is the same in all of them.

The primary output is **identical** to that of the committed evaluator (sha256 `707421ee…`) at all 22,098
(k, B) points checked (m = 4 and 10; B = 1, 37, 200, …, 1800, 1999; every k).

Each look of the sequential verification records every alternative reading's `rule_stops` and
`differs_from_primary`. Per null the output adds `first_look_where_rule_stops` and a `stop_verdict_by_reading`
against the final status (`stop_verdict`: 'rule met' needs the first stop exactly at the final B; 'maximum
reached' / 'batches exhausted' / 'budget' need no earlier stop). Only `primary` feeds the `stop_verdict` field.

Where the readings differ (m = 10, every k; reproduce with `python3 nd-unfolding/s5p_recompute.py a8-map --out
<file>`, about 1 s):

| look B | k where (i) stops and the primary continues | point p ranges | the reverse |
|---:|---:|---|---:|
| 200 | 22 | 0.109–0.139, 0.866–0.935 | 0 |
| 400 | 262 | 0.145–0.469, 0.534–0.858 | 0 |
| 600 | 305 | 0.248–0.754 | 0 |
| 800 | 53 | 0.468–0.533 | 0 |
| 1000–1999 | 0 | — | 0 |

- Reading (ii), open containment, changes the stop at **no** (k, B) for **any** B = 1..1999. This was re-scanned
  2026-09-29. The first version of this line covered only the batch-edge B above; a look between them occurs when
  seeds are lost. The one exact endpoint equality (B = 2, k = 2) fails the T7 precision under either reading, and
  the closest approach for B ≥ 100 is 4.5e-9. The synthetic endpoint cases show it would matter only at an exact
  equality.
- Reading (iii) equals (i).
- (i) can only make a null stop **earlier**, never later.
- MnvTune and GENIE CV may not stop before B = 1200, so **A8 can bind only for GENIE MEC, NuWro and GiBUU at a
  stop at B ≤ 800.** There a primary verdict of "INCONSISTENT" alongside a "consistent" under (i), or the
  reverse, is routed for a ruling and is not resolved by this lane.
- The p-values and decisions at the B production reached do not depend on A8.

Synthetic boundary controls (`A8Sensitivity`, 7 tests):
- the primary defaults equal the primary reading;
- the precision-level split at B = 200 (k = 179) and B = 400 (k = 119);
- a threshold in the look interval blocks every reading;
- no difference from B = 1000 on, and (i) never stops later;
- open vs closed with a threshold exactly at either end;
- the inclusive T7 bounds and the strict small-p bound;
- the verdict mapping;
- an end-to-end run carrying and labelling the readings.

**Status of the decision-relevant items (2026-09-29):**
- **A7** is RULED (procedure, labels), and so is **A7-VS** (family: *replace*; report only, ~04:33Z) (§3.2).
- **A6** (union) and **A8** (99.5% level) are resolved by the frozen text in this lane's assessment, in agreement
  with the campaign's clarification. **Neither has an owner ruling.**
- Should a diagnostic reading disagree with the primary on a decision (A6), or on a stop verdict (A8: MEC, NuWro or
  GiBUU at B ≤ 800), the disagreement is reported as such for the owner. It does not change the primary. A1–A5 matter for bit-level agreement. Each needs a ruling only if production
reads it differently and a decision moves. That is diagnosed at the final comparison by computing the
competing reading as a labelled diagnostic.

### 3.2 A7 and A7-VS as ruled (2026-09-29)

**A7** (`RULING-20260929-s5p-A7-robustness-flag.md`, origin/main `4a1d931c`, ~01:22Z) fixes the procedure, a full
Holm re-run at κ = 3, and the labels. **A7-VS** fixes the variant family: *replace*.
- Record: `RULING-20260929-s5p-A7-VS-kappa3-variant-set.md` on this branch, received in this session just before
  04:33:56Z. The campaign's record of the same ruling is on origin/main `67eadf25`.
- It is an explicit **report-only clarification made then**, **not** a recovered pre-production definition.
- The frozen records at `4f5a613f` do not fix the family. Everything searched: am. 7 `claims.rejection` "at kappa =
  3"; `calibration.m1_shift` "kappa_robust 3"; design `kappa_robust: 3`; the `s5p_prefreeze` docstring "3 M1 (the
  robustness variant)"; amendments 1, 5, 6, 6b, 8; spec; the reviews.
- At 04:33:57Z only the five B = 0 looks existed, and `stage7/joint/` did not.

**Reported (ruled).**
- Family per test: {c·S : c ∈ 0, ½, 1} ∪ {F ± 3δ_M1}. MnvTune, with no M1 variant, uses its c-variants, so its
  robust claim is its claim.
- Robust claim = the largest p over that family. `family.holm_at_kappa_robust` is `holm_determined` over the ten
  robust claims.
- `family.robust_labels`: a primary rejection is "robust to the sub-fine residual" iff also rejected there, else
  "not robust"; every primary non-rejection is "not applicable".

**Separately named diagnostics (preserved).**
- `family.keep_both_kappa3_diagnostic` (`holm`, `labels`): the family keeping ±2δ and ±3δ. This is the frozen
  evaluator's `decisions_robust_kappa` as the campaign reports the frozen code.
- `family.frozen_boolean_equivalent_diagnostic`: the frozen boolean `robust_to_the_sub_fine_residual`, meaning equal
  decision labels in the primary and the keep-both re-run.
- `family.kappa3.<set>.A7b_per_test_robust_diagnostic`: the per-test reading.
- `family.kappa3.tests_where_the_sets_differ`: the tests on which the ruled and keep-both labels differ, measured at
  the final evaluation. The difference has no guaranteed direction: Holm with determinacy is not monotone in k across
  unequal B (3 of 20,000 random ten-test configurations gained a rejection when a k rose).

**Production labeler.** It is updated by its owner, the campaign: `nd-unfolding/s5p_robust_labels.py` at `67eadf25`,
sha256 prefix `e08b76083b7abd0a`, schema `s5p-robust-labels/2`.
- This lane has not read its code.
- The comparer maps its fields as the campaign describes them: `labels` and `decisions_kappa3_replace` (the ruled
  family), `family_members`, `diagnostics.frozen_boolean_robust_to_the_sub_fine_residual`,
  `diagnostics.keep_both.{family, labels}`, `evaluate_sha256`, `design_sha256` and `alpha_family`. `code_sha256`,
  `ruling` and `schema` are excluded as identity/citation.
- Variant names are matched through an explicit parser (`c=0.5` ≡ `0.5`; `m1=+3` ≡ `m1+3`). An unparsable name stays
  UNRESOLVED and is never guessed.
  - The campaign states (2026-09-29) that the frozen names are exactly `0.0`, `0.5`, `1.0`, `m1+2`, `m1-2` in
    `variants`, and `m1+3`, `m1-3` in `robustness_variants` (`{}` for MnvTune). Its `family_members` are
    `["0.0", "0.5", "1.0", "m1+3", "m1-3"]` (MnvTune: the three c-names; a null stopped at B = 0: `[]`). All
    parse; a control pins them.
- A null stopped at B = 0 appears in the frozen output as `{"not_calibrated": …}` with no statistic. The comparer
  locates it and agrees only if the recompute also has B = 0 for it. Before this fix it would have been
  "not located", leaving the verdict INCOMPLETE.

Tests: `A7Ruling` (4), and the comparer's controls for the labels document (a wrong ruled label, a keep-both family
reported as the ruled one, an unparsable member name, provenance, an unknown field).

If a discrepancy appears, diagnose it by computing the alternative reading as a labelled diagnostic and report
both; do **not** change the primary reading to make the numbers agree.

## 4. Missing inputs (at 2026-09-28T21:00Z)

- `runs/prod/status/<null>-final.json` for all five nulls. Only `-B0.json` files existed, with 26–47 products per
  null across two readings about 20 min apart.
- Every look's `<null>-B<B>.json` (the sequential verification pairs each look with its file).
- Power products: 6 sets × 200 (only `P1_a1.0` had started: 46–48 products).
- Production's `stage7/joint/joint-evaluate.json` (and its committed copy
  `docs/orchestration/state/s5p/stage7/joint/joint-evaluate.json`).

## 5. The final verification — PENDING; run only when production is terminal

No polling from this lane. Resume when the production worker reports terminal readiness, then run these checks
before anything else.

**5.1 Terminal checks** (extended 2026-09-29 at the owner's request: the power queue's terminal disposition and the
meter's open concurrency, the campaign's own terminal definition, `HANDOFF-20260929-s5p-campaign-cold-start.md` §8).
Run them independently when the campaign reports terminal; its report is a trigger, not the evidence. Each exit status
is read on its own, never through a pipe. **Production is terminal only if ALL of these read:**
1. `final statuses: 5/5`;
2. the power queue is terminal: `pow runner 'queue done' lines: 1` or more in the LIVE runner's log, **or** a budget / incomplete pow outcome
   that the printed pow runner lines themselves show (a `refusing` / force-stop line) and the campaign has recorded.
   A pow runner that is still waiting or running is **not** terminal;
3. `squeue rc=0` and `queued s5p cal/pow jobs: 0`;
4. `meter budget sha256` equal to the ledger's latest `budget` record, `meter rc=0` and `meter open concurrency:
   cpu 0.0 gpu 0.0`;
5. `joint-evaluate.json present` (and, for the A7 label comparison, `robust-labels.json present`).

```bash
ssh -o BatchMode=yes saul.nersc.gov 'bash -s' <<'EOF'
R=/pscratch/sd/j/josephrb/s5p-20260926; S=/pscratch/sd/j/josephrb/s5p-parallel-recompute
n=0; for k in MnvTune_v1 GENIE_2_12_10_CV GENIE_2_12_10_MEC NuWro_21_09 GiBUU_2019; do
  if [ -f "$R/runs/prod/status/$k-final.json" ]; then n=$((n+1)); else echo "MISSING final status: $k"; fi; done
echo "final statuses: $n/5"
P=$R/runs/queue-prod-r3-pow.log   # the live pow runner since transition r3 (r2, r1 and unsuffixed logs are historical)
echo "pow runner 'queue done' lines: $(grep -c 'queue done' "$P")"
echo "pow runner refusal/stop lines:"; grep -nE 'refus|STOPPED the queue|force-stop' "$P" | tail -5
echo "pow runner last lines:"; tail -3 "$P" | cut -c1-200
squeue -h --me -o %j > "$S/squeue-terminal-check.txt"; echo "squeue rc=$?"
echo "queued s5p cal/pow jobs: $(grep -cE '^s5p-s5p_(cal|pow)_' "$S/squeue-terminal-check.txt")"
# the meter's measure reads the ledger, sacct and squeue and writes only --out (here: this lane's scratch); run it from
# the deploy whose budget.json the ledger is bound to (transition r3: e0d7b04a; rc 5 = binding mismatch = wrong deploy)
M=$R/deploy/e0d7b04a; echo "meter budget sha256 $(sha256sum < $M/docs/orchestration/state/s5p/budget.json | cut -c1-12)"
/usr/bin/python3.11 -c 'import json,sys; b=[json.loads(l) for l in open(sys.argv[1]) if l.strip() and json.loads(l).get("kind") == "budget"][-1]; print("ledger budget sha256", b["budget_sha256"][:12])' "$R/ledger/admissions.jsonl"
(cd "$M" && /usr/bin/python3.11 nd-unfolding/s5c_meter.py --budget docs/orchestration/state/s5p/budget.json \
  --ledger "$R/ledger/admissions.jsonl" measure --out "$S/meter-terminal-check.json" > /dev/null); echo "meter rc=$?"
/usr/bin/python3.11 -c 'import json,sys; s=json.load(open(sys.argv[1]))["summary"]; print("meter open concurrency: cpu", s["cpu"]["open_concurrency"], "gpu", s["gpu"]["open_concurrency"])' "$S/meter-terminal-check.json"
if [ -f "$R/stage7/joint/joint-evaluate.json" ]; then echo "joint-evaluate.json present"; sha256sum "$R/stage7/joint/joint-evaluate.json"; else echo "joint-evaluate.json MISSING"; fi
if [ -f "$R/stage7/joint/robust-labels.json" ]; then echo "robust-labels.json present"; sha256sum "$R/stage7/joint/robust-labels.json"; else echo "robust-labels.json MISSING"; fi
for d in "$R"/runs/prod/pow/*; do echo "power $(basename "$d"): $(ls "$d" | grep -v partial | grep -c 'npz$')"; done
EOF
```

- A `squeue` or meter failure (rc ≠ 0; the meter exits nonzero on an unregistered campaign job, and 5 on a budget
  binding mismatch) means UNKNOWN, not "no jobs" or "no concurrency".
- **Transition r2 (2026-09-30T22:44Z; origin/main `74c681ef`, `RUNBOOK-20260930-s5p-transition-r2-budget-rev6.md`):**
  the ledger was rebound to budget revision 6 (sha256 `b9260acd…`, production 209.647), and the six runners moved to
  deploy `c754f3cd` with `prod/queues-r2/`, logging to `runs/queue-prod-r2-<lane>.log`.
  - Checked by this lane 22:47Z: the meter from `c754f3cd` gave rc 0 (open cpu 2.0, gpu 0.0); from `55a41765` it
    gave rc 5 ("budget sha256 f29db3899610 differs from the ledger's b9260acd2fbd").
  - `git diff 55a41765 c754f3cd` over the meter, the task tables, the design and the three production evaluator
    modules is `budget.json` only.
  - The cluster task tables are identical across the deploys.
  - If the campaign moves the runners or rebinds again, re-point `P` and `M` to what it names, and re-check both
    lines above before reading any verdict.
- **Transition r3 (2026-10-04T04:46–04:47Z):** an owner decision, `DECISION-20261004-s5p-production-budget-extension.md`
  (origin/main `80a85324`). Budget revision 7, ledger bound to `be29f2c3…`; the six runners moved to deploy
  `e0d7b04a` with `prod/queues-r3/`, logging to `runs/queue-prod-r3-<lane>.log`.
  - Checked by this lane 04:50Z:
    - `e0d7b04a` is at that HEAD, its budget sha256 `be29f2c3009e` = the ledger's latest record;
    - the meter from `e0d7b04a` gave rc 0 (open cpu 2.0, gpu 0.0), and from `c754f3cd` rc 5;
    - six r3 runner logs exist (pow waiting on P3g, no `queue done`);
    - the cluster task tables are identical;
    - `git diff c754f3cd e0d7b04a` over the meter, tables, design, the three evaluator modules, the queue and array
      scripts and `s5p_nullexp.py` is `budget.json` only.
  - The campaign reports shared-node timeouts near 25% of tasks since about 10-02, so expect about 7% missing seeds
    per batch in the later batches. That raises L in §5.8; it changes no definition.
- **Transition r4 stage 1 (2026-10-04T16:20Z; origin/main `6c730f0f`, plan at `b93445c4`):** NuWro's runner moved to
  throttle 5. The campaign relays this as owner-instructed. New runner PID 669349 on login33, deploy `b93445c4`,
  `prod/queues-r4/cal-NuWro_21_09.q`, log `runs/queue-prod-r4-NuWro_21_09.log`; the other four lanes stay on r3, and
  pow ended "queue done" in the r3 log at 15:42Z.
  - Checked by this lane at 16:25Z:
    - (a) the deploy's `validate_deploy_r4.py`, byte-identical to the committed one, run with
      `GIT_OPTIONAL_LOCKS=0`: rc 0, VALID;
    - (b) the r4 queue from the b5 wait line equals the r3 queue line for line once `--throttle` is normalized
      (8 lines: 2 → 5);
    - (c) the budget sha256 `be29f2c3009e` = the ledger's latest record (no rebind);
    - (d) 669349 has PPID 1 and PGID = PID, and its cmdline is `s5c_queue.sh … queues-r4/cal-NuWro_21_09.q`; the
      old 1047840 is gone, and the other four r3 runners are alive;
    - (e) the r4 b6 line has table `cal-NuWro_21_09-b6.tsv`, 34 tasks, throttle 5; the table holds 200 contiguous
      seeds 1261200–1261399 and is byte-identical to `4f5a613f`;
    - `nd-unfolding/`, the budget, the design and the tables are byte-identical between `e0d7b04a` and `b93445c4`.
  - **Open, checked at terminal from the ledger (no polling):** NuWro b6 and later submissions must show
    `--array=0-33%5` with the frozen b<b> table.
  - Stage 2 (throttle 16) is only planned. The campaign will message before it, and it gets the same five checks.
  - Throttle is scheduling, not science: it changes neither which seeds a batch holds nor any rule.
  - The meter is valid from either `e0d7b04a` or `b93445c4` (identical budget). §5.1 keeps `M=e0d7b04a` and
    `P` = the r3 pow log, where pow's `queue done` is.
- Nonzero open concurrency means a reservation is still open, so production is not terminal.
- `robust-labels.json` (the ruled A7 label, produced by the campaign after the evaluation) is needed only for the A7
  label comparison. If it is missing, `compare` reports it as not located (exit 2) and the rest of the comparison
  still stands; rerun `compare` when it appears.
- An incomplete power set does not block the verification (amendment 7 records it); report it, with its seed
  disposition (§5.4).
- Dry-run 2026-09-29 ~17:40Z on the non-terminal state: the block read `0/5`, pow `queue done` 0 (the runner waiting on
  P2), `squeue rc=0` with 8 queued jobs, `meter rc=0` with open concurrency cpu 2.0 / gpu 0.0, both JSON files
  missing. Every added line reported non-terminal, as it should.

**5.2 Deploy the reviewed executable code: commit `0142a228`, never the branch tip or a working tree** (updated
2026-09-29; `1bfd8910` is superseded, §5.6). The deployment refuses if the tip's code has moved away from
`0142a228`, because that code would be unreviewed:

```bash
W=/Users/josephbailey/local-research/MINERvA-OmniFold-s5p-recompute; S=/pscratch/sd/j/josephrb/s5p-parallel-recompute
REVIEWED=0142a228b637e4a7e88dba70ddc7744a2fd23c19
git -C "$W" fetch origin s5p-parallel-recompute-20260928 || exit 1
git -C "$W" cat-file -e "$REVIEWED^{commit}" || { echo "reviewed commit missing"; exit 1; }
git -C "$W" diff --quiet "$REVIEWED" FETCH_HEAD -- nd-unfolding/ \
  || { echo "REFUSED: code at the tip differs from the reviewed commit; a code change needs its bounded re-review"; exit 1; }
rm -rf /tmp/s5p-recompute-deploy && mkdir -p /tmp/s5p-recompute-deploy
for f in nd-unfolding/s5p_recompute.py nd-unfolding/s5p_recompute_compare.py docs/orchestration/state/s5p/prod/design.json; do
  git -C "$W" show "$REVIEWED:$f" > "/tmp/s5p-recompute-deploy/$(basename "$f")"; done
git -C "$W" show "$REVIEWED:docs/orchestration/state/s5c/contract.json" > /tmp/s5p-recompute-deploy/s5c_contract.json
# the report-side seed-disposition script (§5.4; NOT part of the reviewed code; pinned by content, not by commit)
for f in s5p_recompute_seed_disposition.py s5p_recompute_missingness_bounds.py; do
  git -C "$W" show "FETCH_HEAD:docs/orchestration/state/s5p/recompute/$f" > "/tmp/s5p-recompute-deploy/$f"; done
shasum -a 256 /tmp/s5p-recompute-deploy/*
# expect: s5p_recompute.py 05664adbfb19cb17a527bff6a26efec7031d70cc2e0715a117f21ff4f5db82ac
#         s5p_recompute_compare.py 2cef96881dee75b84e568cb67a864a2db760b5a5c0064d4a7d24a296a5881ed4
#         design.json 404446eb2a770dc4412012c5e182e57a77afa2edd332c75de399a9281f536285
#         s5p_recompute_seed_disposition.py bdc19179cbd64debf13c0368b63a4140ecb82ff7c560d6d25606c59e6f1cec77
#         s5p_recompute_missingness_bounds.py d5fdb27cb992084405c12b4b55cfb3205ebf8b21df366d048c4312781168c6c4
scp -o BatchMode=yes /tmp/s5p-recompute-deploy/* saul.nersc.gov:$S/code/
```

**5.3 Run and compare** (login node, minutes; no Slurm job):

```bash
ssh -o BatchMode=yes saul.nersc.gov 'bash -s' <<'EOF'
module load python; S=/pscratch/sd/j/josephrb/s5p-parallel-recompute; cd "$S/code" && mkdir -p ../final
sha256sum s5p_recompute.py s5p_recompute_compare.py design.json s5c_contract.json   # design.json must be 404446eb...
python s5p_recompute.py evaluate --require-terminal --design design.json \
  --v /pscratch/sd/j/josephrb/s5p-20260926/stage3/V/V-s3v.npz --s5c-contract s5c_contract.json \
  --out ../final/recompute.json; echo "evaluate rc=$?"
python s5p_recompute.py compare --mine ../final/recompute.json \
  --production /pscratch/sd/j/josephrb/s5p-20260926/stage7/joint/joint-evaluate.json \
  --robust-labels /pscratch/sd/j/josephrb/s5p-20260926/stage7/joint/robust-labels.json \
  --out ../final/compare.json; echo "compare rc=$?"
# the seed disposition (§5.4), immediately after evaluate so both see the same products
R=/pscratch/sd/j/josephrb/s5p-20260926
T=docs/orchestration/state/s5p/prod/tables
diff -rq $R/deploy/4f5a613f/$T $R/deploy/55a41765/$T && diff -rq $R/deploy/55a41765/$T $R/deploy/c754f3cd/$T \
  && diff -rq $R/deploy/c754f3cd/$T $R/deploy/e0d7b04a/$T && diff -rq $R/deploy/e0d7b04a/$T $R/deploy/b93445c4/$T; echo "tables diff rc=$?"
# r4: NuWro's batches from b6 on must have been submitted at throttle 5 with the frozen tables (from the ledger)
/usr/bin/python3.11 -c 'import json,sys; [print(r["utc"], [a for a in r["argv"] if a.startswith("--array") or a.endswith(".tsv")]) for r in map(json.loads, open(sys.argv[1])) if r.get("kind") == "open" and any("nuwro_21_09_b" in a for a in r.get("argv", []))]' $R/ledger/admissions.jsonl
ids=$(/usr/bin/python3.11 -c 'import json,sys; print(",".join(sorted({str(json.loads(l)["job_id"]) for l in open(sys.argv[1]) if l.strip() and json.loads(l).get("kind") == "job"})))' $R/ledger/admissions.jsonl)
sacct -X -n -P -o JobID,State -j "$ids" > ../final/sacct-dispositions.txt; echo "sacct rc=$?"
/usr/bin/python3.11 s5p_recompute_seed_disposition.py --design design.json \
  --tables $R/deploy/e0d7b04a/$T --ledger $R/ledger/admissions.jsonl \
  --logs $R/runs/prod/logs --sacct ../final/sacct-dispositions.txt --recompute ../final/recompute.json \
  --out ../final/seed-disposition.json; echo "disposition rc=$?"
# the missing-experiment bounds (§5.8; report only; imports the reviewed s5p_recompute beside it)
python s5p_recompute_missingness_bounds.py --recompute ../final/recompute.json \
  --disposition ../final/seed-disposition.json --out ../final/missingness-bounds.json; echo "bounds rc=$?"
EOF
```

- `tables diff rc` must be 0. The submitting deploys carry the same task tables (checked for `4f5a613f`,
  `55a41765`, `c754f3cd` (2026-09-30), `e0d7b04a` and `b93445c4` (2026-10-04)). If the runners are moved again, add the new deploy to the diff first.
- `sacct rc` ≠ 0 leaves every no-log task `submitted_task_no_log_unverified`; rerun it before describing anything.
- `bounds rc`: 0 = complete; 3 = written but INCOMPLETE (listed in `incomplete`: not terminal, a count mismatch, a
  disposition that differs from the recompute, an incoherent claim, or not-established seeds counted as lost); 2 =
  an input is unreadable.

Exit codes:
- `evaluate`: 0 = written; 4 = not terminal (a final status is missing). Any other code is an error.
- `compare` prints and records a **verdict**:
  - 0 = **AGREE**: every row agrees, every **required** item is located, and **no production leaf is unresolved**.
  - 1 = **DISCREPANT**: a row disagrees, including a type mismatch. `compare.json` gives both values and the
    production path.
  - 2 = **INCOMPLETE**: nothing disagrees, but a required item is not located (`not_located`), or a production leaf
    is unresolved (`unresolved_production_leaves`). A missing `robust-labels.json` falls here.
  - 3 = **ERROR**: an input could not be read or processed. The report records the error.
  - `--out` is removed before comparing, so a failed run never leaves an earlier report in place.

The comparer enforces **both directions** (after the independent review, §5.5):
- **Required items are derived from the recompute and the owner-stated schema**, not from what production
  contains. The full list is in the comparer's module docstring, including:
  - both digests;
  - per null: the statistics, claims, every claim variant and every ruled κ = 3 M1 member;
  - a scalar `not_calibrated` marker (or claims with B = 0) for a null at B = 0;
  - the four family fields per test;
  - power per set, test, level and rule;
  - the nine `robust-labels.json` fields.
- **Every production leaf is accounted for.** It is consumed by a row, or excluded by an **anchored path pattern**
  that only a scalar leaf can match (`EXCLUDED_SCOPE`: `schema`, `utc`, `code_sha256`, `files_first_last`,
  `lateral_symmetry/*/*`, `shrinkage` and `median_rel_sd` in `joint-evaluate.json`; `schema`, `code_sha256`,
  `ruling` and `evaluate` in `robust-labels.json`; each with its reason). Otherwise it is unresolved.
  - The excluded paths are listed in `excluded_by_scope.paths`.
  - An empty container counts as a leaf.
  - The shift-file digests, paths, mode and κ values are compared against the recompute's enforced inputs, not
    excluded.
- **Types are strict:** a bool is not a number, and a string is not a p-value.
- **Variant names are parsed.** `robustness_variants` may hold only the ruled m1 ±3 members.

Then:
- check that the committed copy of `joint-evaluate.json` has the same sha256 as the cluster file.

**5.4 Report and record.** Report each of the following against production:
- every p-value of the 10 tests (per variant, claim, unshifted);
- each Holm decision with its threshold and interval;
- the ruled A7 label (`family.robust_labels`) against `robust-labels.json`, and **separately**
  `frozen_boolean_equivalent_diagnostic` against the frozen `robust_to_the_sub_fine_residual`;
- **A7-VS**: the ruled labels against `robust-labels.json` `labels` / `decisions_kappa3_replace` /
  `family_members`; the keep-both and frozen-boolean diagnostics against `diagnostics.*` and the frozen
  `decisions_robust_kappa` / `robust_to_the_sub_fine_residual`; and `family.kappa3.tests_where_the_sets_differ`
  (which tests the ruling changed relative to keep-both), reported as a measurement;
- the labelled diagnostics: `decisions_changed_by_product_reading` (A6), the A7(b) and replacing-set labels (A7), and
  `a8_sensitivity` (A8);
- the sequential verification per look (`nulls.<null>.sequential`: the rule's stop against the status file's
  `stop`/`reason`, `first_look_where_rule_stops` against the final B, `stop_verdict`) and the A8 readings
  (`sequential.a8_sensitivity.stop_verdict_by_reading`, `looks_where_a_reading_differs`);
- power per set at 0.05 and 0.005 (rank unshifted, rank claim, determined claim, n present against declared);
- **the missing seeds, qualified by their submission records** (`seed-disposition.json`, owner request 2026-09-29).
  The recompute's `seed_gaps` is inferred from the look files, and a batch refused before submission can read as 200
  "missing" seeds. So:
  - **never describe a recompute gap as lost work until it has been compared with the submission records.** Report
    the three classes separately, per null and per power set:
    - *lost work*: submitted and missing: `submitted_interrupted`, `submitted_never_started`,
      `submitted_task_no_log` (with `sacct` terminal), `submitted_failed_rc`, `submitted_finished_no_product`;
    - *not submitted*: `not_submitted_no_admission` (no meter admission: refused before submission, or never
      reached), `not_submitted_released`;
    - *not established*: `submitted_task_not_yet_run`, `submitted_task_no_log_unverified`,
      `submitted_unaccounted`. At terminal each of these is itself a finding: resolve it with a per-task `sacct -j
      <id>_<i>` before saying anything about it.
  - `recompute_missing_seeds_equal` must be true (run immediately after `evaluate`). Any difference is reported with
    `recompute_missing_not_disposed` and `disposed_not_in_recompute_missing`, never reconciled.
  - **the missing-experiment bounds** (`missingness-bounds.json`, §5.8), per population: the certificate verdict;
    each rejection's `s_min`, threshold and worst upper end; the decisions changed in the corner and one-at-a-time
    runs, labelled "not proven extremal"; and the power bounds. A rejection that is not certified is reported as such
    and routed to the owner. **It never relabels a primary decision.**
  - Set the lost-work counts beside the campaign's lost-seed record
    (`RECORD-20260929-s5p-lost-seed-runtime-diagnostic.md` and its successors). A difference is reported as a
    measurement;
- per null, the calibration record of the F4 correction (§5.6): `products_used`, `count_matches_final_B` and
  `count_mismatch` (a mismatch is reported, never repaired), `seed_gaps` (missing seeds by batch, span and its basis,
  `seeds_outside_submitted_batches`), `partials_excluded`; and in `sequential`: `final_look_is_final_B`,
  `batches_adding_no_product`, `status_files_without_a_look`. A `final_look_is_final_B` of false, or a status file
  without a look, is reported as such and routed; at a B = 0 budget stop `final_look_is_final_B` reads true with no
  look (review NOTE; there is nothing to look at).

For any disagreement between a primary reading and its diagnostic that moves a decision or a stop verdict, record
it and route it to the owner.

**Carried into the final report (owner, 2026-09-29).** Report each of these explicitly, whether or not it is
encountered. If one is encountered, record its disposition. Never relax a comparison requirement merely to obtain
AGREE, and a code fix needs the bounded re-review (§5.5) before it is used:
- **R1:** a MnvTune `{total,shape}_robust` record carrying fields beyond `p`, `k` and `B` gives INCOMPLETE, with the
  leaves listed. It fails safe, and is not a pass.
- **R6:** two production entries naming the same parsed variant can supply `k`/`p` and the implied size separately.
  If found, report it as a layout outside the owner-stated names.
- **R8:** decision nodes without `threshold`/`interval` are not required to carry them. The report states the
  recompute's threshold and interval for each decision regardless.
- **P4 evidence limitation:** requiring the implied size only for the process-shift variants c > 0 rests on this
  lane's quotation of the frozen `s5p_joint` docstring ("per variant c > 0") and the frozen e2e test. The reviewer
  could not verify the quotation, because reading that file is barred. An M1 implied size present in production is
  compared; its absence is not a failure. Do not re-read the
specification to agree. Commit `recompute.json`, `compare.json` and a report beside this file. Only then may the
verification be called complete. Agreement verifies the calculation, not the adequacy of the calibration.

**5.5 Independent comparer review (2026-09-29) and responses.**
- The report is `REVIEW-20260929-s5p-recompute-comparer.md`, verbatim. The reviewer was an independent agent in the
  read-only detached worktree `../MINERvA-OmniFold-s5p-recompute-review1` at `4a772838`, left clean.
- It found 8 findings: F-1 and F-4 HIGH; F-2, F-5 and F-8 MEDIUM; F-3, F-6 and F-7 LOW.
- The fixes are in the commit after that file. The **final reviewed commit** is recorded at the end of this section.
- Check after the fixes: the reviewer's own probes were re-run against the fixed comparer, using copies in scratch
  (`review-rerun/`).
  - Two adaptations only: the fixture adapter `_old_layout` rebuilds the 4a772838 layout, and two report-schema field
    reads were updated. The mutation cases are unchanged.
  - **99 of 101 cases now give the reviewer's expected verdict**, including every case that was a DEFECT at
    `4a772838` except M4. The exit-code probes were re-run too.
  - The two remaining differences are deliberate, and are listed in the table below.

| finding | response |
|---|---|
| F-1 missing required quantity → AGREE | **fixed**: required items derived from the recompute record (not located → INCOMPLETE); power per set, test, level and rule |
| F-2 labels-document fields optional | **fixed**: all nine owner-stated fields required, and each per-test key |
| F-3 lax types | **fixed**: strict types; a dict or list where a scalar is expected is a discrepancy, consuming nothing beneath it |
| F-4 exclusion by key name at any depth | **fixed**: anchored path patterns, scalar leaves only; excluded paths listed; empty containers are leaves |
| F-5 exclusion reasons rest on an optional digest | **fixed**: `design_sha256` and `v_sha256` required; shift digests, paths, mode and κ compared with the recompute's enforced inputs (new `provenance` fields) |
| F-6 dict `not_calibrated` marker | **fixed**: scalar marker only; a B = 0 null without a marker needs claims with B = 0, whose p, k and B (and T if present) are compared |
| F-7 keep-both member in the robust slot | **fixed**: `robustness_variants` matched only against the ruled m1 ±3 members, both required |
| F-8 missing labels file exit 1; stale report | **fixed**: missing labels → INCOMPLETE (2); any exception → ERROR (3); `--out` removed first. `pending_ruling` (dead) removed |
| M4 (missing per-test `unshifted`) still AGREE | **disposition, not adopted**: the unshifted quantity is required and compared as the `0.0` variant (k, p). A separate per-test `unshifted` key is compared if present, but not required, because production may not write one. |
| X9 (scalar under `path` in the labels document) now INCOMPLETE | **stricter than the reviewer's control, kept**: exclusions are anchored to owner-stated fields, and `path` is not one |

**Round 2: verification of `6c7c7b9f`.** Result: NO. F-2, F-3, F-4, F-5, F-6 and F-7 FIXED; F-1 and F-8 PARTIAL;
M4 and X9 ACCEPTED; five new items (report, Round 2). Responses in the next commit:

| item | response |
|---|---|
| ND-1 (MEDIUM): implied size required at the null level, while the frozen e2e test puts it in each variant entry | **fixed**: located in either layout, including `variants/<v>/implied_size_of_unshifted_test/<t>/power` |
| ND-2 (MEDIUM): contents of required containers optional | **fixed**: the jitter `min`, `median`, `max` and `n` are required per test; the implied size is required for each process-shift variant c > 0 per test |
| ND-2, P4 (deleting `implied_size…/m1+2/shape` gives AGREE) | **disposition, not adopted**: the frozen `s5p_joint` docstring says the implied size is reported "per variant c > 0". An M1 variant's value is compared where present, but not required. |
| ND-3 (LOW): a dict marker gives DISCREPANT | **fixed**: a marker of unstated shape gives INCOMPLETE; a false or empty scalar marker gives DISCREPANT |
| ND-4 (LOW): `argmax` not parsed | **fixed**: compared as a set of parsed names (for the claim and the keep-both robust claim) |
| ND-5 (LOW): an unwritable `--out` exits 1 | **fixed**: failing to remove or write the report gives ERROR (3) |
| N2: `tests/<null>/{total,shape}_robust` unmapped | **fixed**: compared, when present, with the keep-both robust claim (for MnvTune, the claim) |
| F-5 open item: where the top-level digests live is not evidenced | **kept as a requirement**; the location is inferred from production's key names; if the digests sit elsewhere the verdict is INCOMPLETE until the mapping is extended |

After these fixes the reviewer's round-2 probes were re-run from copies in `scratchpad/review-verify2/` (paths
repointed only). Results, in both layouts:
- all 77 negative, 15 B = 0 and 8 list cases give the expected verdict except M4 and X9 (accepted);
- the new-defect probes N1–N7 all do;
- of the partial-requirement probes, P1–P3 do and P4 differs (the disposition above).

**Round 3: verification of `1bfd8910`.** **Fixes verified at `1bfd8910`: YES.** ND-1 to ND-5 and N2 are fixed; F-1
and F-8 are fully fixed; P4 is accepted.

**Final reviewed commit (comparer): `1bfd8910`.** The commit that records round 3 changes documentation only. The
comparer, evaluator and test code at the branch tip were then byte-identical to `1bfd8910`. **Superseded
2026-09-29:** the evaluator and tests changed with the s5p-F4 correction (§5.6; final reviewed commit `0142a228`);
the comparer is still byte-identical to `1bfd8910`.

**Open LOW items, deliberately not changed.** A change now would itself be unreviewed and would void the final
reviewed commit. Each is to be acted on only if it binds at the final comparison:
- **R1 (fail-safe).** A MnvTune `{total,shape}_robust` record that carries fields beyond `p`, `k` and `B` would be
  INCOMPLETE, with those leaves listed. The fix, if it binds: fall back to the full claim record.
- **R6.** Two production entries naming the same variant (e.g. `0.5` and `c=0.5`) can supply `k`/`p` and the
  implied size separately. This is outside the owner-stated names. The fix, if it binds: take the implied size from
  the selected entry, and treat a duplicate as unresolved.
- **R8 (observation).** A decision node without `threshold` or `interval` is not required to carry them. §5.4 reports
  the recompute's threshold and interval regardless.

A fix to any of these after the final verification needs its own review round before it is used.

**5.6 Correction of finding s5p-F4 (2026-09-29): the calibration ensemble.**

*Source.* The campaign session's handoff `HANDOFF-20260929-s5p-recompute-seed-gap-correction.md` (origin/main
`04b9c6b9`). This lane treated its diagnosis and proposed correction as claims and checked them.

*Verification of the finding (this lane, against the frozen text only).*
- Amendment 7 `calibration.sequential_rule`: "before each batch s5p_seqstop.py evaluates both claim p-values on the
  finished products (partials excluded)" and "the p-value stays valid at the B reached". It sets no seed range, and
  so the withdrawn A13 reading ("seed in [base, base + final B)") departs from it. **Confirmed.**
- It binds now. The real look `GENIE_2_12_10_CV-B193.json` has `B = 193` with `files_first_last` `s1220000` …
  `s1220199`, so seeds are missing inside batch 0 and a final ensemble restricted to [base, base + B) drops valid
  products.
- The `product_files` docstring (AST, as permitted) says a killed task leaves `*.partial-<pid>.npz`, never counted.
  The handoff's statements about production code bodies (line numbers, `B = len(files)`, a refusal on a count
  mismatch, the `.partial` substring rule) were **not** verified: reading them is barred for this lane. The partial
  rule was widened to any `.partial` name; on the documented `.partial-<pid>` names it is identical.
- At `1bfd8910` on the handoff's gap world the evaluator gives B = 394, power `B_null` 394, and looks
  `[198, 394 × 9]`: a short ensemble made the old look loop repeat the last B up to the maximum. That is a second
  symptom, not listed in the handoff.

*What changed (evaluator only; the comparer is unchanged).*
- A13 revised to the frozen definition; the old reading kept, dated, as `A13_withdrawn_20260929`.
- `calibration`: `count_mismatch`; `seed_gaps` (missing seeds over the submitted-batch span, from the per-look status
  files with stop false, or from the products when no status file exists; a product outside the span is listed and
  kept). The gap report is diagnostic only: a batch refused by the meter after a continuing look counts as
  submitted, and a whole-batch loss after a continuing look shares one status file and is not counted.
- `sequential`: looks run batch by batch until every product has been looked at, never beyond the final B, and do
  not depend on how many status files exist. A batch that adds no product while later ones do gets no look of its
  own (`batches_adding_no_product`); `final_look_is_final_B`; `status_files_without_a_look`.
- A smoke run on the real non-terminal products (scratch `f4-smoke/`, not quoted) found the duplicate-look defect
  of the first version: a batch submitted but still running repeated the last look's B. That was fixed before the
  review.

*Readings preserved.* On gap-free toy worlds (terminal with power, non-terminal, B = 0 budget) the output is
byte-identical to `1bfd8910` outside the calibration record, the `ambiguities` text and the new sequential fields
(this lane's probe and the reviewer's, both rounds). No other reading (A1–A12, A14) changed; A6 and A8 stay as
assessed; the comparer and its required items are unchanged.

*Tests added (58 → 67).* Class `SeedGaps`:
- the handoff's two-batch world: +5, +17 and +203 missing, a partial at +17, final B = 397;
  - 397 used, including +397 … +399; the count matches;
  - looks 198 and 397, each paired with its status file;
  - gaps exactly {+5, +17, +203}; the partial excluded;
  - unshifted k, B and p against a brute force written from the specification (surrogates off);
  - power `B_null` 397;
- a mutation control: the withdrawn selection goes red at 394;
- any `.partial` name excluded;
- a product outside the submitted batches listed and kept;
- a trailing batch without products (running, or budget-refused);
- one and two batches lost whole;
- looks without a B0 file.

The toy writes the B = 0 look, as production does (all five nulls have `-B0.json`). One pre-existing test changed
by the definition itself: the product beyond the final B is now kept (58 → 59), with a count mismatch.

*Deviation from the handoff §4.* The handoff asks that k, B and p "agree with the frozen `s5p_joint` on the same
files". Running or reading production code is barred for this lane, so a brute force from the specification is used
instead. The reviewer assessed this as adequate for a selection defect, but it does **not** establish agreement with
`s5p_joint`: not the partial rule, not the selection, not the statistic. That agreement is established only by the
final comparison (§5.3) on the real products.

*Review.*
- Fresh independent read-only agent, detached worktree `../MINERvA-OmniFold-s5p-recompute-review-f4`, left clean.
  Report verbatim: `REVIEW-20260929-s5p-recompute-f4-correction.md`.
- Round 1 at `04a1d313`: CHANGES REQUIRED.
  - F1 MEDIUM: the look loop was bounded by the look-file count, so a whole-batch loss dropped the final looks.
  - F2 LOW: the loop depended on the B0 file.
  - F3 LOW: gap-diagnostic batch count.
  - F4 LOW: a seed below base enters every look (loud).
  - F5, F6 NOTE: the control models the old selection, not the old loop; the brute force is not a production
    comparison.
- Round 2 at `0142a228`: **fixes verified YES**, no new finding at LOW or above. One NOTE: `final_look_is_final_B`
  reads true at a B = 0 budget stop; recorded in §5.4 and not changed.
- **Final reviewed commit: `0142a228`.**

*Open items, deliberately not changed* (a change would void the review; act only if one binds at the final
comparison, with its own review round): F4 (a seed below base, reported loudly), the F3 gap-count caveat, the B = 0
NOTE, and the earlier R1, R6 and R8 (§5.5).

*Timing.* The correction was made after production outputs became visible: the five batch-0 looks with k = 0 at
every null, and batch-1 products appearing during the work. It is a definitional alignment with the frozen text. No
production job, product, budget, status, rule or schedule was touched; the only cluster writes were to this lane's
scratch (`f4-smoke/`, `squeue-terminal-check.txt`).

**5.7 Terminal checklist and seed disposition added (2026-09-29, owner request; documentation and a report-side
script only).**
- §5.1 now includes the campaign's full terminal definition: the pow queue's disposition and the meter's open
  concurrency (read with `s5c_meter.py measure`, which reads the ledger, `sacct` and `squeue` and writes only its
  `--out`; checked in its source on origin/main).
- The new `docs/orchestration/state/s5p/recompute/s5p_recompute_seed_disposition.py` (sha256 `bdc19179…`) classifies
  every missing seed against the submission records:
  - the frozen task tables;
  - the meter ledger's `open` / `job` / `release` records;
  - the Slurm task logs (the header, the per-seed `rc` lines, the cancellation line);
  - `sacct` task states.
- It is **not** part of the reviewed evaluator or comparer, and feeds no p-value, decision or verdict. It lives
  outside `nd-unfolding/`, so the §5.2 guard and the reviewed commit `0142a228` are unchanged. It had no independent
  code review (the owner asked for none).
- Its evidence is a known-answer control on the real records (2026-09-29 ~17:35Z, non-terminal, scratch
  `f4-smoke/disposition-control.json`).
  - Batch 0 of every null and P1 matches the campaign's independent 16:33Z table exactly (interrupted / never
    started):

    | CV | MEC | GiBUU | MnvTune | NuWro | P1 |
    |---|---|---|---|---|---|
    | 4 / 3 | 2 / 5 | 3 / 2 | 4 / 1 | 3 / 0 | 4 / 3 |

    Lost work is 34 seeds in total (20 interrupted, 14 never started).
  - Without `sacct`, the first version counted pending tasks of the running batch 1 as lost. This is why `sacct` is
    required and no-log tasks without a state are `unverified`.
  - Two P2 tasks had no log and no `sacct -X` row. They are unverified and not counted, consistent with the
    campaign's record that tasks split off while pending can lack an `sacct` row.

*Observation 2026-10-04 (campaign incident 17:15Z, `campaign-state.json` at `eed3a7c0`): the first non-TIMEOUT task
failure.*
- `59321575_0` (MEC b6 task 0) is `sacct` FAILED 129:0: the interpreter segfaulted in finalization (ROOT
  `TClass::LoadClassInfo`) after its work.
- Checked by this lane, read-only: its log has six `rc 0` lines and none nonzero. Each of seeds 1241200–1241205 has
  exactly one product, with no `.partial`; each zip tests clean; each `xsec_flat` holds 65,856 finite values; each
  `pseudo_seed` matches.
- So these are finished products. They are in the ensemble and are not missing seeds.
- In general, the seed disposition classifies missing seeds by product absence, so a FAILED task whose seeds all
  have products contributes nothing. A FAILED task that does leave seeds missing gives `submitted_unaccounted`: it
  has a log but no cancellation line. That is "not established" and fails closed (§5.4, §5.8). Resolve it from the
  log and `sacct` before describing it.

**5.8 Missing-experiment sensitivity bounds (2026-09-30; report only; not reviewed code).**

*Requested and scoped.* Requested by a Codex coordination session that relays the owner's request; that relay is not
an owner ruling and is recorded as such. Scope: no change to the reviewed code (`nd-unfolding/` still equals
`0142a228`), to production, or to any primary output, rule or label. Nothing is gated on it.

*Files and procedure.*
- Files: `docs/orchestration/state/s5p/recompute/s5p_recompute_missingness_bounds.py` (sha256 `d5fdb27cb9920844…`) and
  its tests `test_s5p_recompute_missingness_bounds.py` (9).
- The procedure and the CP interval are **imported** from the reviewed module, not retyped. Holm uses the 95% level;
  the 99.5% look interval belongs to the stopping rule and is not used here.

*The bound.* For a null with retained k and B, and L missing, the claim count k' (the largest over the frozen
variants) lies in [k, k + L] at B' = B + L.
- Populations:
  - (a) interrupted plus not-established;
  - (b) all lost work plus not-established.
- Not-established seeds are counted as lost (**fail closed**), and the run is marked INCOMPLETE.
- **Not-submitted seeds are excluded**: amendment 7 makes p valid at the B reached.
- Coherence is checked before bounding:
  - claim k = the largest variant k;
  - p = (k + 1)/(B + 1);
  - the family reproduces from its entries.
- Terminal completeness: final statuses, count = final B, disposition = the recompute's missing seeds.

*The certificate (group separation, step-aware).*
- (i) max over R of the worst p < min over the tests outside R of the best p;
- (ii) each R test's worst upper end < alpha/(m − s_min(i)), where s_min(i) counts the R tests whose worst p is
  strictly below its best p.
- The Codex coordination form "each R worst upper < alpha/m" is the special case s_min = 0. It is also sufficient
  and is reported as `simple_alpha_over_m`. Alone it is too strict: on the toy family it fails with **no** missing
  experiment, because two rejections sit at Holm steps 2–3 with upper 0.018 > 0.0125.
- Without the certificate, the corners and one-at-a-time runs are reported as **not proven extremal**, because Holm
  with determinacy is not monotone in k.

*Validation.*
- Exhaustive soundness: in 500 random 4-test families, for every certified case, every assignment (each count
  raised by 0..L) keeps every primary rejection. This holds for both forms.
- The step-aware form certifies every L = 0 rejection (exact there).
- Two mutants go red: dropping the separation condition, and loosening the step threshold by one step.
- End to end on the toy: (a) certified; (b) with 5 lost MnvTune experiments **not** certified, and correctly so: the
  all-worst run moves GiBUU to step 0, where it is undetermined.
- Fail-closed, not-submitted exclusion, coherence, non-terminal and power-denominator controls.

*Second coordination cycle (2026-09-30), the same day.*
- **Identity before certification:** the design sha256 (`404446eb…`), the five frozen nulls in order, each null's
  frozen variant family and the union mode. A mismatch gives INCOMPLETE.
- **No zero-loss defaults:** a missing power disposition gives INCOMPLETE, and so do product counts that differ from
  the recompute's or power counts that do not add up to `n` declared.
- Power bounds are labelled `conditional_on_retained_null_ensemble: true` and
  `certifies_power_robustness: false`.
- Both certificate forms are reported. A method that uses only the simple α/m form is compared with
  `simple_alpha_over_m`; step-aware YES with simple NO is not a disagreement.
- Tests 7 → 9. Two further mutants go red: the power-disposition check silenced, and the design-digest check
  silenced.

*The campaign's independent counterpart and the comparison at terminal.* `nd-unfolding/s5p_missing_sensitivity.py`
(origin/main `d0cca826`, sha256 `34768e47c2bd…`, 13 tests). It writes `$NS/stage7/joint/missing-sensitivity.json` and
`seed-states.json`; their sha256 come in the terminal packet. The campaign confirmed definitions (1)–(5) on
2026-09-30. Compare **only** what both compute:

| quantity | this lane (`missingness-bounds.json`) | campaign (`missing-sensitivity.json`) |
|---|---|---|
| population (a) | `a_interrupted` | `interrupted_or_unestablished` |
| population (b) | `b_all_lost` | all submitted-and-missing |
| certificate | `certificate.simple_alpha_over_m` (**not** `holds`) | its certificate on the primary family |
| corners | (a) `all_worst`; (b) `all_worst`, `all_best` | `worst_interrupted`; `worst_all_missing`, `best_all_missing` |
| power bounds | `rank_unshifted`, `rank_claim`, `determined_claim` | `unshifted`, `claim_rule`, `claim_rule_determined` |
| INCOMPLETE | exit 3 | exit 4 |

- **Not compared, because it is computed on one side only:**
  - this lane's step-aware `holds` (a YES with simple NO is not a disagreement) and its one-at-a-time runs;
  - the campaign's κ = 3 replace-family certificate and its robust-label gating.
- A corner is a realizable assignment, so a decision flipped there is a real counterexample on either side.
- A difference in any compared quantity is reported, with both values, and is not reconciled.

*What it does not establish.* It does not establish ignorable missingness; it bounds the decisions without that
assumption. It does not bound the effect of missing **null** experiments on power, which needs each alternative's
count. Production's own computation, if the campaign makes one, should be compared with this output and not
substituted for it.

**Downstream reader.** The reproduction harness (branch `s5p-parallel-reproduction-20260928`, config key
`joint.independent_compare`) records `/pscratch/sd/j/josephrb/s5p-parallel-recompute/final/compare.json` by sha256
only. If this route changes, follow "Steps to incorporate the final joint result" in
`HANDOFF-20260928-s5p-reproduction-harness.md` on that branch.
