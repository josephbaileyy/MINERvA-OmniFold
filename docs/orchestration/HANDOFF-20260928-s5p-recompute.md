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
Evaluator as described here: `nd-unfolding/s5p_recompute.py` sha256 `707421ee…` (first committed at `27c7ff37`; the
copy the real-input dry run used; unchanged since). The branch is pushed to `origin` for durability and is **not
merged** into `main`.

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
| `nd-unfolding/tests/test_s5p_recompute.py`, `tests/s5p_recompute_toy.py` | 32 controls (below); a synthetic world in the production file formats |

Tests (`python3 -m pytest -q nd-unfolding/tests/test_s5p_recompute.py`: **32 passed**, ~15 s):
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
"Alt. computed" says whether the competing reading is computed beside the primary one in the same run. Items marked
**RULING** need an explicit ruling from the specification owner if the final comparison shows that the readings
disagree on a decision. The primary reading stays in force until then. It is never swapped to match production.

| # | governing text | reading used (primary) | competing reading(s) | affected outputs | decision could change? | resolved by an authoritative record? | alt. computed |
|---|---|---|---|---|---|---|---|
| A1 | am. 5 `nuisance_model.surrogates`; handoff §1 conventions (terms listed, composition not stated) | lateral, then ×(1+0.014z) (scales lateral), then rounding noise | ×(1+0.014z) applied to f only, or last | every simulated T (second order: 0.014 × ~2% lateral) | only via a rank flip at a near-tie; not expected | no | no (a diagnostic if T disagree) |
| A2 | handoff §1 "noise on each experiment's J cells" | draw 109 cells in V order, then restrict | draw only the domain cells | GiBUU simulated T only | yes for GiBUU in principle (a different random stream changes every draw) | no | no |
| A3 | am. 5 "N(0, diag s_num²)" | `standard_normal(109)` × SD | `multivariate_normal` (different stream consumption) | all simulated T | as A2 | distribution yes, stream no | no |
| A4 | `s5p_inference` docstring (Jacobian at f); am. 5 "residual gets −eps" | shape: p(f) vs p(μ+eps) | p(f−eps) vs p(μ) | simulated T_shape | only at a near-tie | Jacobian at f: yes; eps placement: no | no |
| A5 | `s5p_joint.shift_vector` docstring (b = ensemble mean − μ; a, se over F4 pairs) | b from surrogated f without eps; se = SD(ddof 1)/√16; one S for both tests | eps included in b; ddof 0; a separate S for the shape test | S → the c-variant p-values | **yes**: through the claim p when a c-variant is the argmax near a Holm threshold | b, a, se: yes; eps, ddof, shape S: no | no |
| **A6** | am. 7 `claims.rejection` "process-shift variants … AND the sub-fine-residual variants F ± 2δ_M1" | UNION: {cS} ∪ {±κδ} (5 variants) | cross product cS + sκδ (9 variants; larger combined shifts → larger claim p) | claim p of the four external nulls, Holm decisions, power at GENIE CV, sequential looks | **yes** (a rejection can become undetermined or not rejected) | **no** (production key names `variants` / `robustness_variants` do not decide it) | **yes**: `product_reading`, `family.holm_product_variant_reading`, `decisions_changed_by_product_reading` — **RULING** |
| **A7** | am. 7 "Every rejection is also flagged 'robust to the sub-fine residual' or not at kappa = 3 (report only)" | per rejected test: κ=3 claim interval below the threshold of the step that rejected it | a full Holm re-run at κ = 3 (production writes `decisions_robust_kappa`) | the robustness flag only | no claim decision (report only); the flag itself: **yes** | no | **yes**: `family.holm_at_kappa_robust` — **RULING** |
| **A8** | am. 7 `sequential_rule`; `sequential_decision` docstring "(b) meets the T7 precision at the point estimate" | half-width on the 99.5% look interval; "contains" closed | half-width on a 95% interval; open boundaries | whether each look should have stopped (the sequential verification verdict), not the p at production's B | the verdict on production's stop: **yes**; p-values at the B reached: no | threshold condition: yes; precision interval level: no | no (cheap to add as a diagnostic) — **RULING** if my look verdict disagrees with a production stop |
| A9 | am. 7 "a budget stop at B = 0 leaves the null 'not calibrated' (it stays in the Holm family with p = 1)" | interval [0, 1] → 'undetermined' at its step, labelled 'not calibrated' | 'not rejected' at its step | labels of that null (and of equal-p tests after it) | no rejection can change (p = 1 is last) | label and p: yes; step outcome: no | no |
| A10 | none (ties unaddressed) | family order (design null order; total before shape) | any other stable order | Holm labels at exactly equal claim p | only with equal p and different B | no | no |
| A11 | `power_determined` docstring (k = largest count over null variants); design `power.*.surrogate_seed0` | alternatives unshifted, own surrogates, eps keyed by the set's seed0 | variants applied to the alternative too | power | — | yes, in substance | no |
| A12 | `s5p_joint` docstring "null draws shifted by c D against the unshifted ensemble" | full unshifted ensemble (draw's own unshifted T included) | leave-one-out | implied size; the "not calibrated for the data process" flag (> 0.08 at c = ½) | the flag near 0.08: yes; claims: no | no | no |
| A13 | design `calibration_n`; `calibration_count` / `product_files` docstrings | finished products with seed in [base, base + final B); mismatches reported | every finished product; refuse on mismatch | B, every p | only if production's product set differs from the final B (reported by `count_matches_final_B`) | partial exclusion: yes; mismatch handling: no | the mismatch is reported, not repaired |
| A14 | am. 7 `non_rejection` (B ≥ 1200 floor so 0.005 is attainable) | power against the null's final ensemble | power as the sequential procedure would behave on alternative data (review 4 F4 option) | power at 0.005 | — | yes (the floor was the adopted remedy) | no |
| — | am. 7 "a k = 0 decision needs B >= 737" | exact two-sided 95% CP: B ≥ 736 suffices | — | none (the floor is 1200) | no | arithmetic | — |

**Items needing an explicit ruling if they bind: A6 (can change a rejection), A7 (the robustness flag), A8 (the
verdict on a production stop).** A1–A5 matter for bit-level agreement. Each needs a ruling only if production
reads it differently and a decision moves. That is diagnosed at the final comparison by computing the
competing reading as a labelled diagnostic.

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
for d in "$R"/runs/prod/pow/*; do echo "power $(basename "$d"): $(ls "$d" | grep -v partial | grep -c 'npz$')"; done
EOF
```

A `squeue` failure (rc ≠ 0) means UNKNOWN, not "no jobs". An incomplete power set does not block the
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
  --production /pscratch/sd/j/josephrb/s5p-20260926/stage7/joint/joint-evaluate.json --out ../final/compare.json; echo "compare rc=$?"
EOF
```

Exit codes:
- `evaluate`: 0 = written; 4 = not terminal (a final status is missing). Any other code is an error.
- `compare`: 0 = every mapped item agrees; 1 = discrepancies, listed in `compare.json` with both values and the
  production path; 2 = a null or the decisions could not be located. On 2, extend the mapping; never read it as
  agreement.

Then:
- Read `unmapped_production_leaves` in `compare.json` (for example the implied size or the jitter summaries) and
  compare them by hand against `recompute.json`.
- Check that the committed copy of `joint-evaluate.json` has the same sha256 as the cluster file.

**5.4 Report and record.** Report each of the following against production:
- every p-value of the 10 tests (per variant, claim, unshifted);
- each Holm decision with its threshold and interval, and the κ = 3 flag;
- the ambiguity alternatives: `decisions_changed_by_product_reading` (A6) and `holm_at_kappa_robust` (A7);
- the sequential verification per look (`nulls.<null>.sequential`: the rule's stop against the status file's
  `stop`/`reason`, and `first_look_where_rule_stops` against the final B);
- power per set at 0.05 and 0.005 (rank unshifted, rank claim, determined claim, n present against declared).

For any disagreement on a **RULING** item (§3), record it and route it for a ruling. Do not re-read the
specification to agree. Commit `recompute.json`, `compare.json` and a report beside this file. Only then may the
verification be called complete. Agreement verifies the calculation, not the adequacy of the calibration.
