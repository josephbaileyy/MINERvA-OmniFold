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
Evaluator as described here: commit `27c7ff37` on that branch (`nd-unfolding/s5p_recompute.py` sha256 `707421ee…`, the
copy the real-input dry run used); the branch is local (not pushed) at the time of writing.

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

Smoke evaluation on the calibration products present at batch 0 (27–47 per null; `smoke/products_smoke_full.json`
and `smoke/dryrun-nonterminal.json` in my scratch; mechanical only — p-values at these B mean nothing and are not
quoted): every statistic finite; the five design lateral bands in every product's meta; the mean null T_total is 44.6
(MnvTune, 109 cells), 523 (GENIE CV), 405 (MEC), 6347 (NuWro), 1776 (GiBUU, 72 cells), against the prefreeze
non-centralities plus the domain size (`units.json`: 450 + 109, 318 + 109, 6344 + 109, 1712 + 72) — an independent
check of the metric, the surrogates and the calibration operand; the bias-aligned shift's a/se is −0.96, −0.62,
+0.51, −2.36, −1.30 (units.json, whose bias is the asimov's rather than the ensemble mean (A5): −0.56 GENIE CV,
+0.51 MEC, −2.36 NuWro, −1.36 GiBUU), NuWro's magnitude 0 as in units.json. The CLI `evaluate` ran on all five nulls
in 3 s (single-threaded BLAS, pinned in the module: under login-node thread contention one 109-cell null took 72 s
instead of 0.3 s); `--require-terminal` exited 4 and wrote nothing.

## 3. Ambiguities (the reading used; alternatives computed where a decision could move)

The same list is embedded in every output (`ambiguities`). None was resolved by looking at production output.

- **A1** surrogate order: lateral, then ×(1 + 0.014 z) (scales the lateral term), then rounding noise.
- **A2** rounding noise and eps drawn over all 109 cells (V order), then restricted (matters only for GiBUU).
- **A3** `standard_normal(109)` scaled per cell (≡ `normal(0, sd)`; not `multivariate_normal`).
- **A4** eps perturbs the prediction: shape compares p(f) with p(μ + eps); Jacobian at the experiment's f.
- **A5** bias b = mean surrogated calibration f (no eps) − μ, recomputed at every look; u = b/|b|_W;
  a_j = d_j' W⁻¹ u; se = SD(ddof 1)/√16; one S (total metric) shifts both tests.
- **A6** variant set = UNION {c S, c ∈ 0, ½, 1} ∪ {±κ δ_M1}; the 9-variant cross product is computed beside it and
  `family.decisions_changed_by_product_reading` lists any decision it would change.
- **A7** κ = 3 flag: robust iff the κ = 3 claim's interval lies below the threshold of the step that rejected it; a
  full Holm re-run at κ = 3 is reported beside it (`family.holm_at_kappa_robust`; production writes
  `decisions_robust_kappa`, apparently the latter reading — compare both).
- **A8** the sequential T7 half-width is measured on the 99.5% look interval; "contains" is closed.
- **A9** B = 0: p = 1, interval [0, 1], "undetermined" at its Holm step, labelled "not calibrated".
- **A10** Holm ties ordered by family order (design null order; total before shape).
- **A11** power experiments are unshifted observations with their own surrogates and eps keyed by the power set's
  `surrogate_seed0`; variants shift the null ensemble only.
- **A12** implied size of a variant = fraction of shifted calibration draws with rank p ≤ 0.05 against the full
  unshifted ensemble.
- **A13** the calibration ensemble = finished products with seed in [1200000 + 20000 i, … + final B); mismatches
  reported.
- **A14** power against the null's final ensemble.
- **Spec text:** amendment 7 says a k = 0 decision at 0.005 "needs B ≥ 737"; the exact two-sided 95% interval
  gives B ≥ 736 (upper 0.0049995 at 736). Immaterial (the powered nulls' floor is 1200); recorded, not "fixed".

If a discrepancy appears, diagnose it by computing the alternative reading as a labelled diagnostic and report
both; do **not** change the primary reading to make the numbers agree.

## 4. Missing inputs (at 2026-09-28T21:00Z)

- `runs/prod/status/<null>-final.json` for all five nulls (only `-B0.json` files existed; 26–46 products per null).
- Every look's `<null>-B<B>.json` (the sequential verification pairs each look with its file).
- Power products: 6 sets × 200 (only `P1_a1.0` had started: 46 products).
- Production's `stage7/joint/joint-evaluate.json` (and its committed copy
  `docs/orchestration/state/s5p/stage7/joint/joint-evaluate.json`).

## 5. The final verification (run only when terminal)

Terminal condition (both parts, each with its own exit status read — not through a pipe):

```bash
ssh saul.nersc.gov 'ls /pscratch/sd/j/josephrb/s5p-20260926/runs/prod/status/*-final.json'   # expect 5 files
ssh saul.nersc.gov 'squeue -h --me -o %j > /tmp/$USER-sq.txt; echo rc=$?; grep -cE "^s5p-s5p_(cal|pow)_" /tmp/$USER-sq.txt'
# expect rc=0 and count 0; also require stage7/joint/joint-evaluate.json to exist
```

Then, from this worktree at the committed evaluator (record the sha you deploy):

```bash
W=../MINERvA-OmniFold-s5p-recompute; S=/pscratch/sd/j/josephrb/s5p-parallel-recompute
scp $W/nd-unfolding/s5p_recompute.py $W/nd-unfolding/s5p_recompute_compare.py \
    $W/docs/orchestration/state/s5p/prod/design.json saul.nersc.gov:$S/code/
scp $W/docs/orchestration/state/s5c/contract.json saul.nersc.gov:$S/code/s5c_contract.json
ssh saul.nersc.gov "module load python; cd $S/code && sha256sum *.py design.json && mkdir -p ../final && \
  python s5p_recompute.py evaluate --require-terminal --design design.json \
    --v /pscratch/sd/j/josephrb/s5p-20260926/stage3/V/V-s3v.npz --s5c-contract s5c_contract.json \
    --out ../final/recompute.json && \
  python s5p_recompute.py compare --mine ../final/recompute.json \
    --production /pscratch/sd/j/josephrb/s5p-20260926/stage7/joint/joint-evaluate.json --out ../final/compare.json"
```

`evaluate --require-terminal` exits 4 if any final status is missing. `compare` exits 0 (every mapped item agrees),
1 (discrepancies, listed in `compare.json` with both values and the production path) or 2 (a null or the
decisions could not be located — extend the mapping; never read it as agreement). Also read
`unmapped_production_leaves` (quantities production reports that the comparer did not map, e.g. the implied size
or jitter summaries) and compare them by hand against `recompute.json`. Expected run time: minutes on a login node
(no Slurm job; nothing named `s5p-*` is ever submitted from this lane).

Report: every p-value (10 tests: raw per variant, claim, unshifted), each Holm decision with its threshold and
interval, the κ = 3 flag, the sequential verification per look (`nulls.<null>.sequential`: the rule's stop at each
look vs the status file's `stop`/`reason`, `first_look_where_rule_stops` vs the final B), and power per set at
0.05 and 0.005 (rank unshifted, rank claim, determined claim, n present vs declared), each against production.
Commit `recompute.json`, `compare.json` and a report beside this file; only then may the verification be called
complete.
