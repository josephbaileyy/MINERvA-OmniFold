# s5p Stage-6 recompute lane: independent read-only review of the comparer (2026-09-29)

**CITABLE FOR:** the independent reviewer's findings on `nd-unfolding/s5p_recompute_compare.py` at `4a772838`, quoted
verbatim below. The five areas: required-field coverage, metadata exclusions, B = 0 handling, variant-family
membership, and verdict/exit-code behaviour. The follow-up verification of the fixes is quoted in Round 2 below. **NOT CITABLE FOR:** any repair (the responses
are in `HANDOFF-20260928-s5p-recompute.md` §5.5), any p-value or decision.

- Requested by the owner, 2026-09-29.
- Reviewer: an independent agent with no authorship of the reviewed code.
- Worktree: the read-only detached worktree `../MINERvA-OmniFold-s5p-recompute-review1` at `4a772838`, left clean
  (`git status --porcelain` empty).
- The reviewer did not read the production evaluator bodies.
- It used no cluster, ran no scientific compute, and ran no Slurm job.
- Scratch probes and outputs: `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/af747db6-96ed-4487-90e9-4ed640a884a3/scratchpad/review-comparer/`
  (`common.py`, `negative_cases.py`, `b0_cases.py`, `list_cases.py`, `exit_cases.py`, `exit_cli.sh`, and their `.out`
  files). These are session-local, not durable. The case table below is the durable record.

## Round 1: review of `4a772838` (verbatim)

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

## Round 2: verification of the fixes at `6c7c7b9f` (verbatim)

The same reviewer, resumed with its round-1 context, in the same read-only worktree moved to `6c7c7b9f`, left clean.

**Disclosure.** For production's output layout the reviewer read the frozen production end-to-end test
`nd-unfolding/tests/test_s5p_joint_e2e.py`, lines 96–114. That file is unchanged since `4f5a613f`, and it is not one
of the four modules excluded from reading. It gives the output layout, not statistical logic.

Scratch: `scratchpad/review-verify/` (session-local).

Fixes verified at 6c7c7b9f: NO. The fixes hold on my original probes: 98 of 100 give the expected verdict, and the two others (M4, X9) are the author's dispositions, which I accept. But the fixes introduce new defects. The most important one means a correct production output could never reach AGREE.

**Reviewer:** independent agent, no authorship of the code under review.
**Worktree:** `/Users/josephbailey/local-research/MINERvA-OmniFold-s5p-recompute-review1`
**HEAD:** `6c7c7b9ff2536407c484f9976aec053dc1207f0a` (checked before and after)
**Scratch:** `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/af747db6-96ed-4487-90e9-4ed640a884a3/scratchpad/review-verify/`
**`git -C <worktree> status --porcelain`:** empty output, rc=0.
**Test suite:** `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider nd-unfolding/tests/test_s5p_recompute.py` gives **55 passed** in 25.07 s.
**Production modules:** I did not read `s5p_joint.py`, `s5p_inference.py`, `s5p_seqstop.py` or `s5p_robust_labels.py`. For the production layout I used the assertions of the production end-to-end test, `nd-unfolding/tests/test_s5p_joint_e2e.py` lines 96–114. That file and `s5p_joint.py` have no commits in `4f5a613f..6c7c7b9f`, so they are unchanged since the freeze.
**Author's re-run:** I did not read or use `review-rerun/`.

### (1) Verdict per finding

| Finding | Status | Evidence |
|---|---|---|
| F-1 missing required quantity gives AGREE | **PARTIAL** | M1–M3 and M5–M11 now give INCOMPLETE; M4 is the accepted disposition. New gap ND-2: the contents of two containers the docstring lists as required are not required (P1–P4 give AGREE). |
| F-2 labels-document fields optional | **FIXED** | L3–L7 give INCOMPLETE, naming the missing field. |
| F-3 lax types | **FIXED** | A16 (`True`→`1`), A17 (p as a string) and F5 (family given as a dict) give DISCREPANT. Integral floats are still accepted (N4 gives AGREE). |
| F-4 exclusion by key name at any depth | **FIXED** | X1–X5 and X8 give INCOMPLETE. Exclusions are anchored patterns on scalar leaves (lines 56–72, 211–218), and the excluded paths are listed. |
| F-5 exclusion reasons rest on an optional digest | **FIXED** | M14, X6 and X7 give INCOMPLETE; D2 and D3 give DISCREPANT. Open item: the frozen e2e test never shows a top-level `design_sha256` or `v_sha256` in `joint-evaluate.json` (it does not show their absence either). |
| F-6 dict `not_calibrated` marker | **FIXED** | Z6 gives DISCREPANT. New issue ND-3 (LOW): a dict marker now gives DISCREPANT rather than INCOMPLETE. |
| F-7 keep-both member in the robust slot | **FIXED** | F8b gives INCOMPLETE; `robustness_variants` is matched only against the ruled m1 ±3 members. |
| F-8 exit codes and stale report | **PARTIAL** | Fixed: a missing labels file exits 2 (CLI). An unreadable `--mine` exits 3 and writes an ERROR report over the earlier AGREE file. A malformed production file now gives DISCREPANT (exit 1), by design. Still open: an `--out` in a missing directory exits 1 with a traceback (N7, ND-5). |

### (2) Re-run of the original cases

The case scripts `negative_cases.py`, `b0_cases.py`, `list_cases.py` and `exit_cases.py` are byte-identical copies of the 4a772838 scripts (checked with `cmp`). I adapted only the fixture, in `common.py`, whose docstring records these adaptations:
- **A1:** `production_like()` now writes flat `"<null>:<test>"` decision keys. The fixture nests them so the unchanged mutation paths still address them. With `LAYOUT=flat`, `run()` flattens them again after the mutation. Both layouts were run and give identical verdicts for all 100 cases.
- **A2:** `mine["inputs"]["design_sha256"] = "d"*64`, as the new `Compare.setUp` does.
- **A3:** in the B = 0 world, the null's new `{"not_calibrated": ...}` record is replaced by the 4a772838 statistics record, so case Z0 keeps its meaning. Cases Z1–Z12 overwrite it themselves.
- **A4:** `enrich()` no longer rebuilds `variants` and `robustness_variants`, which now come from `production_like()`. It adds only the per-test `unshifted` and `interval`, and the power set.
- **A5:** the TestCase is built with an existing method name, because `test_exit_codes` was renamed.
- **Harness:** the `cd` target in `exit_cli.sh` points at `review-verify/exit`. `base_check.py` reads `excluded_by_scope.paths` instead of `counts`.

Results (`*.nested.out`, `*.flat.out`):
- There are 100 cases: 77 negative, 15 B = 0 or family-slot, and 8 list cases.
- The baseline gives AGREE, with 216 rows.
- **98 give the expected verdict.** The two others are M4 (AGREE, expected INCOMPLETE) and X9 (INCOMPLETE, expected AGREE), the two dispositions judged in (3).
- Every other case that was a DEFECT at 4a772838 now gives the expected verdict: M1–M3, M5–M11, L3–L7, A16, A17, X1–X8, F5, F8b, Z6, Z8, Z9.

Exit codes: `compare_files` returns 0, 2 and 1 for agree, no labels, and discrepant plus unresolved. The CLI returns 0 when all agree, 2 for a nonexistent labels file, 1 for a malformed production file (now a type discrepancy), and 3 for a missing `--mine`, writing the ERROR report.

### (3) The two dispositions not adopted

- **M4: ACCEPT.** In the recompute, `c["unshifted"] = c["variants"]["c=0"]` (`s5p_recompute.py:700`), so the unshifted test is the same object as the c = 0 variant. The "0.0" variant's `k` and `p` are required for each test: M5 and M6 give INCOMPLETE. The frozen e2e test asserts `ok["variants"]["0.0"]["total"]["p"]` and no per-test `unshifted` key. Requiring a second copy would block a correct output.
- **X9: ACCEPT.** `path` is not an owner-stated field of `robust-labels.json`, and the contract makes an unstated leaf unresolved. The result is stricter than my control and fails safe, and it can be resolved by a commit.

### (4) New defects in the five areas

Probes: `new_defect_probes.py` (flat layout) and `partial_requirement_probes.py`; outputs in the matching `.out` files.

**ND-1 (MEDIUM, area 1): a correct production output cannot reach AGREE.**
- The fixed comparer requires `tests/<null>/implied_size_of_unshifted_test` (lines 334–336).
- The frozen e2e test (line 99) puts it inside each variant entry: `ok["variants"]["1.0"]["implied_size_of_unshifted_test"]["total"]["power"]`.
- **N1:** correct values in that layout give INCOMPLETE. The item is not located for both nulls, and `tests/*/variants/*/implied_size_of_unshifted_test/*/power` is unresolved.
- **Fix:** map and require the per-variant `implied_size_of_unshifted_test/<t>/power`.

**ND-2 (MEDIUM, area 1): contents of required containers are optional.**
- For `observed_jitter_p` and `implied_size_of_unshifted_test`, only the container's presence is required.
- **P1–P4 give AGREE** after deleting `observed_jitter_p/shape`, `observed_jitter_p/total/median`, `implied_size…/0.5`, or `implied_size…/m1+2/shape`.
- **Fix:** require, for each test, `min`, `median`, `max` and `n` for the jitter summary, and each recompute implied-size label.

**ND-3 (LOW, area 3): a dict marker is reported as a disagreement.**
- **N3:** with the recompute at B = 0, `{"not_calibrated": {"reason": "budget", "B": 0}}` gives DISCREPANT.
- The owner has not stated the marker's value type, so an unknown marker shape is a mapping gap, not a disagreement. It should give INCOMPLETE.

**ND-4 (LOW, area 4; present before the fixes, not introduced by them): a correct `argmax` gives a false DISCREPANT.**
- **N6:** a claim `argmax` written with production variant names (`"0.0"`) gives DISCREPANT against the recompute's `"c=0"`.
- `same_names` compares it as an exact list and never parses the names.

**ND-5 (LOW, area 5): a failed report write still exits 1.**
- **N7:** an `--out` in a missing directory raises `FileNotFoundError` outside the `try` (line 562). The exit code is 1, the DISCREPANT code, with a traceback.

**Observation, not a regression (N2):**
- The frozen e2e test (line 111) shows `tests/<null>/total_robust` (and presumably `shape_robust`, which it does not assert).
- These are unmapped, so the real output will be INCOMPLETE. The recompute has matching keep-both values.
- This fails safe, but it needs a mapping before the final verification.

**Strictness checks that are fine:** integral floats as counts and an int p (N4), and dict decision nodes (N5), all give AGREE.

### Verdict table

| Area | Result |
|---|---|
| 1. Required-field coverage | F-1 PARTIAL; F-2 FIXED; new ND-1 MEDIUM and ND-2 MEDIUM |
| 2. Metadata exclusions | F-4 FIXED; F-5 FIXED (open item: where the top-level digests live is not evidenced) |
| 3. B = 0 handling | F-6 FIXED; new ND-3 LOW |
| 4. Variant-family membership | F-7 FIXED; ND-4 LOW (present before the fixes) |
| 5. Verdict and exit codes | F-8 PARTIAL; new ND-5 LOW |
| Dispositions | M4 ACCEPT; X9 ACCEPT |

Fixes verified at 6c7c7b9f: NO (open items: ND-1, ND-2, ND-5, and the F-5 digest location; also ND-3, ND-4, and the unmapped `total_robust`/`shape_robust`)

## Round 3: verification of the fixes at `1bfd8910` (verbatim)

The same reviewer, in the same read-only worktree moved to `1bfd8910`, left clean. It again used the frozen e2e test
for the layout, and read no production module, docstrings included.

Scratch: `scratchpad/review-verify3/` (session-local).

Fixes verified at 1bfd8910: YES. All round-2 items (ND-1 to ND-5, N2) are fixed, and F-1 and F-8 are now fully fixed. This round's fixes introduce two new LOW items, R1 and R6; neither blocks the final verification.

**Reviewer:** independent agent, no authorship of the code under review.
**Worktree:** `/Users/josephbailey/local-research/MINERvA-OmniFold-s5p-recompute-review1`
**HEAD:** `1bfd89109dc4edf7f849d935b3e171b72760939f` (checked before and after)
**Scratch:** `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/af747db6-96ed-4487-90e9-4ed640a884a3/scratchpad/review-verify3/`
**`git -C <worktree> status --porcelain`:** empty output, rc=0.
**Test suite:** `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider nd-unfolding/tests/test_s5p_recompute.py` gives **58 passed** in 21.62 s.
**Production modules:** I did not read `s5p_joint.py`, `s5p_inference.py`, `s5p_seqstop.py` or `s5p_robust_labels.py`, docstrings included. For the production layout I again used the frozen e2e test assertions (`nd-unfolding/tests/test_s5p_joint_e2e.py` lines 96–114). I did not read the author's `review-verify2/` outputs.

### (1) Round-2 items

| Item | Status | Evidence |
|---|---|---|
| ND-1 implied size in the variant entries | **FIXED** | N1 (e2e layout, correct values) gives AGREE. R5 (per-null layout keyed test-first) gives AGREE. R4 (e2e layout, `0.5/shape` missing) gives INCOMPLETE. |
| ND-2 contents of required containers | **FIXED**, P4 excepted | P1–P3 give INCOMPLETE. P4 gives AGREE, which is the disposition judged in (3). |
| ND-3 dict marker | **FIXED** | N3 gives INCOMPLETE, with `not_calibrated (a scalar marker; found dict)` not located and its leaves unresolved. Z7 (marker `false`) still gives DISCREPANT. |
| ND-4 argmax names | **FIXED** | N6 (production names) gives AGREE. R10 (unparsable name) gives INCOMPLETE. R9 (a scalar name) gives DISCREPANT. |
| ND-5 unwritable `--out` | **FIXED** | N7 (missing directory) exits 3. An `--out` that is a directory exits 3 ("cannot remove the earlier report"). |
| N2 `*_robust` unmapped | **FIXED for GiBUU; PARTIAL for MnvTune** | N2 and R2 (GiBUU with `p`, `k`, `B`, `interval`, `argmax`) give AGREE; R2b (`k` altered) gives DISCREPANT. R1 (MnvTune): see new item R1. |
| F-1 | **Fully fixed**: every item the docstring lists as required is enforced | M1–M3, M5–M11, P1–P3, Z8 and Z9 give INCOMPLETE; M4 and P4 are the accepted dispositions. |
| F-8 | **Fully fixed** | Missing labels file exits 2. Missing `--mine` exits 3 and overwrites the earlier AGREE report with ERROR. An unwritable or unremovable `--out` exits 3. |

### (2) Re-run from `review-verify3/`

Because `production_like()` did not change between `6c7c7b9f` and `1bfd8910`, no layout adaptation was forced:
- All `.py` files are byte-identical to the round-2 copies (checked with `cmp`).
- The only edit is the `cd` path in `exit_cli.sh`, which now points at `review-verify3/exit`.
- The fixture adaptations A1–A5 from round 2 still apply unchanged.

| Script | Cases | Result | Differences from expected |
|---|---|---|---|
| `negative_cases` | 77 | 75 as expected | M4 and X9 (accepted in round 2) |
| `b0_cases` | 15 | all as expected | none |
| `list_cases` | 8 | all as expected | none |
| `partial_requirement_probes` | 4 | 3 as expected | P4 (the disposition) |
| `new_defect_probes` | N1–N7 | all as expected | none |
| exit harness | — | as expected | none |

- Every case table gives identical verdicts in the nested and flat layouts.
- The exit harness gives, for `compare_files`: 0 when all agree, 2 without labels, 1 for discrepant plus unresolved.
- For the CLI: 0 when all agree, 2 for a nonexistent labels file, 1 for a malformed production file (a type discrepancy).
- Two new files: `exit_extra.sh` (stale-report and `--out` checks) and `round3_probes.py`.

### (3) Disposition P4 (an M1 variant's implied size compared where present, not required)

**ACCEPT.**
- The required set, "per variant c > 0", matches what the frozen e2e test asserts: only `variants["1.0"]["implied_size_of_unshifted_test"]["total"]["power"]` (line 99).
- The implied size of every c > 0 variant is still required (R4, P3).
- The M1 value is compared whenever production writes it.
- Caveat: I did not verify the quoted `s5p_joint` docstring myself, because the rules forbid reading that file. The acceptance rests on the quote plus the e2e evidence.

### (4) New defects from this round's fixes (`round3_probes.py`, flat layout)

**Can a correct production output still never reach AGREE?** Only in the MnvTune case R1 (LOW):
- The fallback robust record for a null without M1 is `{"p", "k", "B"}` only.
- A correct `tests/MnvTune_v1/{total,shape}_robust` that also carries `interval` or `argmax` therefore gives INCOMPLETE, with those leaves unresolved.
- This fails safe. The e2e test asserts only `bad["total_robust"]["p"]`, so whether production writes those fields is not evidenced.
- **Fix:** fall back to the full claim record `mt`, not only its `p`, `k` and `B`.

**Can the dual-layout lookup satisfy a required value from the wrong entry?** Yes, in one non-conforming layout (R6, LOW):
- In the e2e layout, if the implied size of `0.5` sits in a second entry keyed `c=0.5` (the same parsed variant), the verdict is AGREE.
- The `k`/`p` rows come from the `0.5` entry, while the implied size comes from `c=0.5`.
- Two entries naming one variant are outside the owner-stated names, which is why this is LOW.
- **Fix:** take the implied size from the same entry that `_compare_variant_family` selected, and treat any second entry with the same parsed name as unresolved in full.

**Checks that behave correctly:**
- R3: both layouts present, with the per-variant copy wrong, gives INCOMPLETE; the extra copy is unresolved, never agreed.
- R6b: a duplicate `0.50` entry with a different `k` gives INCOMPLETE.
- R7: an implied-size dict without `power` gives DISCREPANT, consistent with the strict-type rule.

**Observation, not a regression (R8):** a decision node written as `{decision, p}` without `threshold` or `interval` gives AGREE. The docstring requires only the decision label for each test, while §5.4 asks for each decision to be reported with its threshold and interval.

Fixes verified at 1bfd8910: YES (open items, both new and LOW: R1 MnvTune `*_robust` fallback; R6 split duplicate variant entry. Observation: R8)
