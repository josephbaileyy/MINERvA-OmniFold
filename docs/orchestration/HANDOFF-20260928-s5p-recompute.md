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
Evaluator: **the recorded evaluator checkpoint is `4a772838`** (owner, 2026-09-29). Its statistical code (every
p-value, decision, family, stop verdict and power) is unchanged since. The commit after the comparer review adds
only `provenance` fields: the shift files' paths, digests, mode and κ values, which the comparer checks against
production's echoes. The comparer's status is in §5.5.

**STATUS: FINAL VERIFICATION PENDING.** Production was non-terminal (calibration batch 0) when this was written.
Nothing below is a verification result.

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
| `nd-unfolding/tests/test_s5p_recompute.py`, `tests/s5p_recompute_toy.py` | 55 controls (below, §3.1, §3.2, §5.5); a synthetic world in the production file formats |

Tests (`python3 -m pytest -q nd-unfolding/tests/test_s5p_recompute.py`: **55 passed**; ~25 s on an idle machine):
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
(missing seeds, a `.partial-` file, a product beyond the final B, count ≠ final B — all reported, not repaired),
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
| A13 | design `calibration_n`; `calibration_count` / `product_files` docstrings | finished products with seed in [base, base + final B); mismatches reported | every finished product; refuse on mismatch | B, every p | only if production's product set differs from the final B (reported by `count_matches_final_B`) | partial exclusion: yes; mismatch handling: no | the mismatch is reported, not repaired |
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

**5.1 Terminal checks.** Each exit status is read on its own, never through a pipe. The condition holds only if
all four lines read `5/5`, `squeue rc=0`, `queued s5p cal/pow jobs: 0` and `joint-evaluate.json present`:

```bash
ssh -o BatchMode=yes saul.nersc.gov 'bash -s' <<'EOF'
R=/pscratch/sd/j/josephrb/s5p-20260926; S=/pscratch/sd/j/josephrb/s5p-parallel-recompute
n=0; for k in MnvTune_v1 GENIE_2_12_10_CV GENIE_2_12_10_MEC NuWro_21_09 GiBUU_2019; do
  if [ -f "$R/runs/prod/status/$k-final.json" ]; then n=$((n+1)); else echo "MISSING final status: $k"; fi; done
echo "final statuses: $n/5"
squeue -h --me -o %j > "$S/squeue-terminal-check.txt"; echo "squeue rc=$?"
echo "queued s5p cal/pow jobs: $(grep -cE '^s5p-s5p_(cal|pow)_' "$S/squeue-terminal-check.txt")"
if [ -f "$R/stage7/joint/joint-evaluate.json" ]; then echo "joint-evaluate.json present"; sha256sum "$R/stage7/joint/joint-evaluate.json"; else echo "joint-evaluate.json MISSING"; fi
if [ -f "$R/stage7/joint/robust-labels.json" ]; then echo "robust-labels.json present"; sha256sum "$R/stage7/joint/robust-labels.json"; else echo "robust-labels.json MISSING"; fi
for d in "$R"/runs/prod/pow/*; do echo "power $(basename "$d"): $(ls "$d" | grep -v partial | grep -c 'npz$')"; done
EOF
```

`robust-labels.json` (the ruled A7 label, produced by the campaign after the evaluation) is needed only for the A7
label comparison. If it is missing, `compare` reports it as not located (exit 2) and the rest of the comparison
still stands; rerun `compare` when it appears. A `squeue` failure (rc ≠ 0) means UNKNOWN, not "no jobs". An incomplete power set does not block the
verification (amendment 7 records it); report it.

**5.2 Deploy the committed evaluator** from the pushed branch tip, not a working tree, and record the sha:

```bash
W=/Users/josephbailey/local-research/MINERvA-OmniFold-s5p-recompute; S=/pscratch/sd/j/josephrb/s5p-parallel-recompute
git -C "$W" fetch origin s5p-parallel-recompute-20260928 && SHA=$(git -C "$W" rev-parse FETCH_HEAD) && echo "deploying $SHA"
mkdir -p /tmp/s5p-recompute-deploy && for f in nd-unfolding/s5p_recompute.py nd-unfolding/s5p_recompute_compare.py \
  docs/orchestration/state/s5p/prod/design.json; do git -C "$W" show "$SHA:$f" > "/tmp/s5p-recompute-deploy/$(basename "$f")"; done
git -C "$W" show "$SHA:docs/orchestration/state/s5c/contract.json" > /tmp/s5p-recompute-deploy/s5c_contract.json
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
EOF
```

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
- power per set at 0.05 and 0.005 (rank unshifted, rank claim, determined claim, n present against declared).

For any disagreement between a primary reading and its diagnostic that moves a decision or a stop verdict, record
it and route it to the owner. Do not re-read the
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

**Downstream reader.** The reproduction harness (branch `s5p-parallel-reproduction-20260928`, config key
`joint.independent_compare`) records `/pscratch/sd/j/josephrb/s5p-parallel-recompute/final/compare.json` by sha256
only. If this route changes, follow "Steps to incorporate the final joint result" in
`HANDOFF-20260928-s5p-reproduction-harness.md` on that branch.
