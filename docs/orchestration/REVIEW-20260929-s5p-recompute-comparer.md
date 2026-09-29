# s5p Stage-6 recompute lane: independent read-only review of the comparer (2026-09-29)

**CITABLE FOR:** the independent reviewer's findings on `nd-unfolding/s5p_recompute_compare.py` at `4a772838`, quoted
verbatim below. The five areas: required-field coverage, metadata exclusions, B = 0 handling, variant-family
membership, and verdict/exit-code behaviour. **NOT CITABLE FOR:** any repair (the responses are in
`HANDOFF-20260928-s5p-recompute.md` §5.5 and the commit that follows this file), any p-value or decision.

- Requested by the owner, 2026-09-29.
- Reviewer: an independent agent with no authorship of the reviewed code.
- Worktree: the read-only detached worktree `../MINERvA-OmniFold-s5p-recompute-review1` at `4a772838`, left clean
  (`git status --porcelain` empty).
- The reviewer did not read the production evaluator bodies.
- It used no cluster, ran no scientific compute, and ran no Slurm job.
- Scratch probes and outputs: `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/af747db6-96ed-4487-90e9-4ed640a884a3/scratchpad/review-comparer/`
  (`common.py`, `negative_cases.py`, `b0_cases.py`, `list_cases.py`, `exit_cases.py`, `exit_cli.sh`, and their `.out`
  files). These are session-local, not durable. The case table below is the durable record.

## Report (verbatim)

Five areas reviewed; four have findings, two of them HIGH. The main problem is that the comparer checks only the production fields that are present: a required p-value, count, variant or digest that is missing, or hidden under an excluded key name, still gives AGREE.

**Reviewer:** independent agent, no authorship of the code under review.
**Worktree:** `/Users/josephbailey/local-research/MINERvA-OmniFold-s5p-recompute-review1`
**HEAD:** `4a772838acd646e89358cd5b5fd1712b7b444994` (checked before and after the review)
**Scratch:** `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/af747db6-96ed-4487-90e9-4ed640a884a3/scratchpad/review-comparer/`
**`git -C <worktree> status --porcelain`:** empty output, rc=0. No `__pycache__` or `.pytest_cache` in the worktree.
**Production modules:** I did not read `s5p_joint.py`, `s5p_inference.py`, `s5p_seqstop.py` or `s5p_robust_labels.py`.
**Test suite:** `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider nd-unfolding/tests/test_s5p_recompute.py` gives **53 passed** in 22.83 s.

### Verdict table

| Area | Result |
|---|---|
| 1. Required-field coverage | **FINDING HIGH** (F-1); MEDIUM (F-2); LOW (F-3) |
| 2. Metadata exclusions | **FINDING HIGH** (F-4); MEDIUM (F-5) |
| 3. B = 0 handling | **FINDING LOW** (F-6). The core rule is confirmed in both directions. |
| 4. Variant-family membership | **FINDING LOW** (F-7). Parsing, swap detection and truncation detection are confirmed. |
| 5. Verdict and exit codes | **FINDING MEDIUM** (F-8). The precedence of the three verdicts is confirmed. |

### Setup

The shared fixture is `common.py` in scratch. Its `rich()` world is the `Compare` test's `production_like()`, plus:
- production-form `variants` and `robustness_variants`, with names `0.0`, `0.5`, `1.0`, `m1±2` and `m1±3`;
- `unshifted` and `interval` for each test;
- a power set `P1` (10 of 12 products);
- a top-level `design_sha256`.

The unmodified world gives AGREE with 180 rows, 0 unresolved leaves and 0 not located.

Run every script as `cd <scratch> && PYTHONDONTWRITEBYTECODE=1 python3 <script>`. Outputs are in `negative_cases.out`, `b0_cases.out` and `list_cases.out`.

### Findings

**F-1 (HIGH): a missing required quantity in `joint-evaluate.json` still gives AGREE.**
- **Defect:** almost every comparison is guarded on production having the key: `same_names` iterates production's keys; the variant, `T_obs`, power and `unshifted` blocks all run only `if ... is not None`.
- **What is enforced:** only these give "not located": a whole null, each per-test entry of `decisions`, `holm_point`, `decisions_robust_kappa` and `robust_to_the_sub_fine_residual`, and a whole power set name. An empty dict produces no leaf in `walk`, so it cannot be unresolved.
- **Consequence:** AGREE does not mean the 10 tests' p-values were compared (handoff §5.4).
- **Reproduction:** `negative_cases.py`, cases M1–M11. `b0_cases.py`, cases Z8 and Z9.
- **Observed AGREE where INCOMPLETE is expected**, after each of these changes:
  - deleting the claim `p`, or its `k` and `B`, or the whole `tests.G.total`;
  - deleting `unshifted`;
  - deleting all of `variants`, or only `m1-2`, or only `m1+2.total.p`;
  - setting `robustness_variants = {}` for GiBUU;
  - reducing `tests.G` to `{T_total_obs}`;
  - setting `power.P1 = {}`, or deleting `power.P1.shape`.
- **Suggested fix:** derive the required production leaves from the recompute record: per null and test, `p`, `k` and `B` for the claim, `unshifted` and every variant in both families, plus per-power-set rule and level. Report every one not found as not located.

**F-2 (MEDIUM): required fields of `robust-labels.json` are optional.**
- **Defect:** `per_test` returns silently when a field is absent, and the three provenance rows are written only `if pk in doc`. Only `labels` is required.
- **Reproduction:** `negative_cases.py`, cases L3–L7.
- **Observed AGREE where INCOMPLETE is expected**, after deleting `decisions_kappa3_replace`, `family_members`, `diagnostics`, `evaluate_sha256`, or `decisions_kappa3_replace[G:total].p`.
- **Consequence:** the ruled family's membership and the binding of the labels file to the evaluate file are not required.
- **Suggested fix:** list the schema-/2 fields the owner stated, and each per-test key under them, as required, reporting them as not located when missing.

**F-3 (LOW): lax type matching lets a type change pass.**
- The `exact` check uses `a == b`, so `True == 1` agrees. The `p` and `stat` checks call `float()`, so a string p-value agrees.
- When a dict is compared as a whole, its path is consumed, which hides everything under it.
- **Reproduction:** `negative_cases.py`, cases A16, A17 and F5.
- **Observed AGREE where DISCREPANT or INCOMPLETE is expected:**
  - a boolean `True` replaced by `1`;
  - a p-value given as a string;
  - `family_members[G:total]` given as `{name: {"k": 999}}`. Iterating the dict yields its keys, which parse, and the `k: 999` values are never looked at.
- **Suggested fix:** also require the same type (bool, number, string, list); for `names`-kind fields require a list of strings.

**F-4 (HIGH): exclusion by key name at any depth drops whole subtrees.**
- **Defect:** `excluded(path)` tests every element of a leaf's path. Any subtree under a key named `kappa`, `ruling`, `evaluate`, `reason`, `mode`, `path`, `sha256` and so on is removed wholesale, however deep it sits.
- **Reproduction:** `negative_cases.py`, cases X1–X5 and X8.
- **Observed AGREE where INCOMPLETE is expected**, for each of these inserted subtrees:
  - `tests.G.total.kappa = {p: 0.9, k: 55}`;
  - a top-level `ruling: {decisions: ...}`;
  - an `evaluate: {tests: ...}` wrapper;
  - `tests.G.reason = "budget"`;
  - `tests.G.mode = {..: {p: 0.5}}`;
  - wrong labels under `diagnostics.keep_both.ruling` in `robust-labels.json`.
- **Suggested fix:** exclude only when the excluded key is the leaf's own key and its value is a scalar, or pin each exclusion to a path pattern. Report the excluded paths, not only counts.

**F-5 (MEDIUM): the stated reason for several exclusions depends on a comparison that is optional.**
- **Defect:** `mode`, `kappa`, `kappa_robust`, `lateral_symmetry`, `shrinkage` and `median_rel_sd` are excluded because "the design's / V's sha256 is compared". That comparison happens only if production has top-level `design_sha256` or `v_sha256`. A nested `sha256` is itself excluded.
- **Reproduction:** `negative_cases.py`, cases X6, X7 and M14.
- **Observed AGREE:**
  - with a wrong digest under `provenance.V.sha256`, and top-level `v_sha256` removed;
  - with a wrong digest under `inputs.design.sha256`, and top-level `design_sha256` removed;
  - with both top-level digests deleted.
- **Suggested fix:** require a design digest and a V digest to be located and compared somewhere; otherwise mark the verdict INCOMPLETE. Do not exclude `sha256` where it sits beside a `V` or `design` key.

**F-6 (LOW): a `not_calibrated` marker whose value is a dict hides its contents.**
- **Defect:** the marker agrees when its value is `not in (None, False)`, and its path is then consumed as a whole.
- **Reproduction:** `b0_cases.py`, case Z6.
- **Observed AGREE** for `tests.G = {"not_calibrated": {"B": 7, "p": 0.3, "k": 2}}` with a recompute at B = 0.
- **Suggested fix:** accept only a scalar marker (true or a string), or walk a dict value and require its fields to be consumed.
- **Confirmed in both directions:**
  - Z2: recompute B = 5 against a marker gives DISCREPANT.
  - Z3: recompute B = 0 against calibrated statistics with B = 60 gives DISCREPANT.
  - Z4: calibrated recompute against a marker gives DISCREPANT.
  - Z5: the null absent in production gives INCOMPLETE.
  - Z7: a marker value of `false` gives DISCREPANT.
  - Z10: the top-level `not_calibrated` list mismatched gives DISCREPANT.
- The remaining gap is F-1: Z8 has neither a marker nor a B in production and gives AGREE.

**F-7 (LOW): a keep-both member is accepted in the ruled `robustness_variants` slot.**
- **Defect:** production `robustness_variants` entries are matched against the recompute's retain (keep-both) variants, which contain all 7 names, `m1±2` included.
- **Reproduction:** `b0_cases.py`, case F8b.
- **Observed AGREE** where INCOMPLETE or DISCREPANT is expected, for `robustness_variants = {m1+2: <m1+2 values>}` with `m1±3` removed.
- **Suggested fix:** match `robustness_variants` only against `m1±3`, i.e. the replace family minus the c-variants, and require both entries for nulls that have an M1 shift.
- **Parser note:** a bare `"2"` or `"3"` parses as a c-coefficient; with no matching recompute variant it would stay UNRESOLVED.
- **Confirmed:** the parser and family matching behave as specified:
  - Parser: `m1=3`, `-0.5` and `1.` give None, never a guess.
  - F1: swapping the ruled and keep-both families gives DISCREPANT.
  - F3, F4: a truncated or duplicated member list gives DISCREPANT.
  - F6, F7: an unparsable name, or a string in place of a list, gives INCOMPLETE.
  - F10: a missing per-test key gives INCOMPLETE.
  - F11: `m1+3` placed in `variants` gives INCOMPLETE.

**F-8 (MEDIUM): a missing labels file exits 1, the code for DISCREPANT, and leaves the old report in place.**
- **Defect:** `compare_files` reads `labels_path` without checking that it exists, so a missing file raises `FileNotFoundError`, which exits 1. Handoff §5.1 says a missing file gives not located, exit 2, and the §5.3 command always passes `--robust-labels`. Any other exception also exits 1; for example, a dict where `T_total_obs` should be raises `TypeError`.
- **Stale output:** on a crash, the previous `--out` file is not replaced. My earlier AGREE `cli.json` survived; the downstream harness records `compare.json` by sha256.
- **Reproduction:** `exit_cases.py`, then `bash exit_cli.sh`.
- **Observed return codes:** 0 when all agree; 1 with a missing labels file; 1 with a malformed production file.
- **Suggested fix:**
  - treat a nonexistent labels path as not located (exit 2);
  - catch exceptions in `compare_files` and exit with a distinct error code (for example 3);
  - unlink or overwrite `out_path` before comparing.
- **Confirmed:** DISCREPANT takes precedence over INCOMPLETE (a changed `k` plus an unknown field gives exit 1); omitting the labels file gives 2 via both `compare_files` and the CLI.
- **Dead field:** `pending_ruling` is never populated; there is no `pending.append` in the module.

### Negative cases run

The expected and observed verdicts are listed in `*.out`. "DEFECT" means the observed verdict differs from the expected one.

| ID | Mutation | Observed |
|---|---|---|
| B0 | rich baseline | AGREE |
| M1–M11 | missing: claim `p`; `k`+`B`; whole test; `unshifted`; all variants; `m1-2`; `robustness_variants={}`; variant `p`; null reduced to `T_obs`; `power.P1={}`; `power.P1.shape` | **AGREE (DEFECT)** |
| M12, M13 | missing `decisions.G.total`; missing top-level `power` | INCOMPLETE |
| M14 | both top-level digests deleted | AGREE |
| L1, L2, L8 | labels: `labels` deleted; one label deleted; no document | INCOMPLETE |
| L3–L7 | labels: `decisions_kappa3_replace`, `family_members`, `diagnostics`, `evaluate_sha256`, a replace `p` deleted | **AGREE (DEFECT)** |
| A1–A15 | altered: count, p, variant p, robust-variant k, T statistic, decision, `holm_point`, `decisions_robust_kappa`, frozen boolean, label, keep-both label, replace k, power count, power n, labels frozen boolean | DISCREPANT |
| A16, A17 | `True`→`1`; p as a string | **AGREE (DEFECT)** |
| U1–U12 | unknown field at: top level, test record, null record, variant/test, variant level, power set, deep in power, labels top level, labels replace entry, labels `keep_both`; plus an extra null and a decision given as a dict | INCOMPLETE |
| X1–X5, X8 | value hidden under `kappa` / `ruling` / `evaluate` / `reason` / `mode`, and labels `keep_both.ruling` | **AGREE (DEFECT)** |
| X6, X7 | wrong nested V / design digest, with no top-level digest | **AGREE (DEFECT)** |
| X9, D5 | control: excluded `path`; changed `code_sha256` | AGREE |
| F1, F3, F4 | families swapped; truncated; duplicate member | DISCREPANT |
| F2 | ruled and keep-both labels swapped (identical in this toy, a control) | AGREE |
| F5 | `family_members` given as a dict | **AGREE (DEFECT)** |
| F6, F7, F9, F10, F11 | unparsable member; string list; unparsable variant; missing member key; `m1+3` in `variants` | INCOMPLETE |
| F8b | `m1+2` in the robust slot, `m1±3` gone | **AGREE (DEFECT)** |
| D1–D4 | labels `evaluate_sha256`; top-level `v_sha256`; top-level `design_sha256`; labels `design_sha256` | DISCREPANT |
| D6 | no `prod_sha256` given, labels carry `evaluate_sha256` | INCOMPLETE |
| Z0, Z1 | B = 0 on both sides (statistics, or a string marker) | AGREE |
| Z2, Z3, Z4, Z7, Z10, Z11, Z12 | B = 0 mismatch in each direction; marker `false`; `not_calibrated` list; non-empty family for a B = 0 null; marker `1` | DISCREPANT |
| Z5 | B = 0 null absent in production | INCOMPLETE |
| Z6 | marker dict hiding B = 7 | **AGREE (DEFECT)** |
| Z8, Z9 | production has `T_obs` only, recompute at B = 0 / B = 60 | **AGREE (DEFECT)** |
| S1–S4, S8 | interval gets an extra element; interval end altered; `names` shortened; `names` reversed; power interval altered | DISCREPANT |
| S5, S6 | unknown list-of-scalars field; unknown mixed list | INCOMPLETE |
| S7 | unknown empty dict (produces no leaf) | AGREE |
| Exit codes | `compare_files`: all agree 0, no labels file 2, discrepant plus unresolved 1. CLI: all agree 0, missing labels file **1**, malformed production **1**; the stale AGREE output survives | see F-8 |
