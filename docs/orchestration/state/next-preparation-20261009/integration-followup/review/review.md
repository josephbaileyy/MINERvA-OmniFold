# Independent review: follow-up integration (two-d-path, sb1-prep, d-id), fixed commit `ae0bfb76`

| field | value |
|---|---|
| Reviewer | fresh read-only Claude subagent (Claude Opus 5.5, `claude-opus-5-5`, Claude Code). I wrote none of the reviewed work. Same model family as the owner, so this is not a cross-provider review |
| Fixed commit | `ae0bfb76bafb8aea03a8a611ddf0e8e1031516e7` on `integrate/followup-20261010`; base `a16d578646936a0cc6eca41e3e0350e756ee0dca` |
| Time | 2026-10-10T17:45:51Z to about 18:05Z (about 20 min) |
| CPU | about 0.15 core-h, estimated from the per-command user+sys times (SB1 suites 96 s; three clone runs about 140 s; D-ID 52 s; ratchets 58 s; producer 39 s; inventory 18 s; bindings, manifest and lint about 60 s). At most one compute command at a time, `OMP/OPENBLAS/VECLIB_*_THREADS=1` |
| RAM / scratch | peak RSS measured 0.50 GB (D-ID controls); scratch peak 508 MB (the shared clone was 424 MB) |
| Worktree | `scratchpad/fu/review-wt`, detached at `ae0bfb76`. Start: `--porcelain --untracked-files=all` 0 lines, `--ignored` 0 lines. End, before removal: `--untracked-files=all` 0 lines; `--ignored` 10 lines, all `__pycache__/` directories created by my test runs. Removed afterwards with `git worktree remove --force` |
| Tripwire `hits.log` | start: absent (0 lines). End: absent (0 lines). `which sbatch scancel sacct squeue` resolved to the tripwire stubs for every test command |

## Verdict: **PASS WITH CHANGES**

The records and packages can land without design completion being treated as scientific admission,
and without any change to the publication objective. I found no MATERIAL defect.

- Assembly is exact.
- No publication source changed.
- The preserved reviews are untouched.
- Every consequential number I recomputed agrees.
- The SB1 pin and digest are correct.
- The owner's two SB1 controls are real: both fail under the mutants that the report names.

Three MINOR findings need text-level repairs (F1–F3). Each one is a record saying more than its
operand supports. None of them changes a number, a verdict or an authorization.

## Findings

| id | severity | file:line | finding | evidence | suggested repair |
|---|---|---|---|---|---|
| F1 | MINOR | `docs/orchestration/CATALOG.md:85`, against `Q/integration-followup/REPORT.md:271` and §5 "Limits that travel with every D-ID statement" | The integration report says no D-ID "PASS label, branch outcome or narrowed endpoint enters a shared status surface". The owner's new CATALOG D-ID row does state the branch outcome: "branch C, binned, signal-only, simulation-only; H2 uninformative". That row also drops limits that §5 says must travel with every D-ID statement: the outcome covers only the resolution-stable functionals (62 % of J's > 2 % residuals are excluded), the truths are historical development truths, and no interval is validated. Stating a verified diagnostic outcome is not an adoption, and the row routes to the report. But the report's own claim about the shared surfaces is false at the fixed commit, and the row reads as a stronger result than §5 allows. | `git diff 7184e436 ae0bfb76 -- docs/orchestration/CATALOG.md`. The old row said "not admitted; its branch-B route is unreviewed" | Either remove "branch C" from the row (for example "run and verified 2026-10-10; outcome and limits in its §11"), or keep it with the limits ("resolution-stable functionals only, development truths, no interval validated") and correct REPORT §7's sentence to match |
| F2 | MINOR | `Q/two-d-path/REPORT.md:507-509`; compare `Q/integration-followup/REPORT.md:88-90` | The owner's correction says "the conclusions below do not rest on it". The very next bullet still reads: "η carries between-estimator scatter … §3.6 shows such scatter exists." §3.6 compares two LightGBM sweeps. The re-review's own wording was "§3.6 shows such scatter exists **for LightGBM**", and the integration report §3.1 itself says §3.6 "is LightGBM-to-LightGBM, not a between-estimator measurement". So the lane record keeps an overreach that the integration found and corrected only in its own report. The conclusion ("not quantified") survives, because it does not need §3.6. | `git show b116f3b7`; `review/review-cycle1.md:55` (N1 row) | Extend the dated correction by one clause: "§3.6 shows run-to-run scatter between two LightGBM sweeps, which would enter η on the LightGBM side; no between-estimator scatter has been measured." |
| F3 | MINOR | `Q/sb1-prep/launch/sb1_submit.sh:58-64`; described in `Q/integration-followup/REPORT.md:135,145` and `Q/sb1-prep/REPORT.md:613,634` | `submit()` refuses an unparseable reply, but it cannot cancel a job that `sbatch` actually queued before the reply failed to parse. A real `sbatch` can also exit non-zero after queuing, for example on a socket timeout. The raw reply is discarded, so the refusal names no id. **Measured:** in a scratch clone, a wrapper that queues through `fake_slurm.py` and then prints `Submitted batch job <id>` gave exit 1 with job `1000` left `PENDING`, `cancelled` = none, and stderr `cancelling: H0= UL= … H1=`. **Inferred consequence, bounded:** at call 1 an orphaned H0 hash job would run. At calls 2–5 the orphan depends `afterok` on a cancelled job, so `--kill-on-invalid-dep=yes` removes it. At call 6 an orphaned H1 (`afterany`) would run and fail on the missing `submission.json`. That is small, but N1's stated purpose was that a partial submission must not leave charged jobs queued. The owner's non-numeric subtest uses an `sbatch` that queues nothing, so it cannot see this. | probe `test_probe_queued_then_unparseable_reply` (scratch only, removed): `PROBE rc 1 jobs {'1000': 'PENDING'} cancelled None` | Record-level (keeps the pin): state this residual in SB1 §7.2/§12 and the integration §4.1. The operator then checks `squeue --me --name=sb1_H0,…,sb1_H1` after any refused submission. Code-level (moves the pin and needs a re-pin record): echo the raw reply to stderr, and have `on_error` also cancel by job name and user |
| F4 | NOTE | `Q/sb1-prep/REPORT.md:380`, `:742` | The owner redefined the package commit in §7.2. Two pointers still describe the old route: §7.2 begins "after this branch is merged", but `prep/sb1-ready-20261009` will be superseded and not merged, and §16 says "The PR's final comment names the package commit". If someone takes `b7c951b3` from PR #70, `check` refuses it, because P differs after it. So this fails closed. It is still a stale route. | text | Point both lines to integration REPORT §8 |
| F5 | NOTE | `Q/sb1-prep/sb1_admit.py:129-145`; `Q/sb1-prep/REPORT.md:384` | "The last commit that changes P" is not what `check` enforces. It accepts any full id that is an ancestor of HEAD and has no later difference under P, the modules or the guard. A later commit such as `ae0bfb76`, or the future merge commit, would also pass. After a `--no-ff` merge, `git log --first-parent -- P` on main would name the merge commit, not `d4335d3b`. Nothing unsafe follows, because the bytes are identical. The definition is still looser in code than in prose. | code reading | Say "`d4335d3b…` (any later commit with no difference under P, the modules or the guard is byte-equivalent and also passes `check`)" |
| F6 | NOTE | `Q/sb1-prep/launch/*.sbatch` (`sb1_check_env` then `source`) | The digest check and the `source` read the file twice, a negligible TOCTOU window. The digest also covers only the top-level setup file, not the conda hook or the two `setup.sh` files it sources. Receipts record the submission-time digest, as the integration report says, and not a hash of the bytes that were actually sourced. The integration describes this accurately. | code reading | None needed beyond the existing disclosure. Optionally have H0 record `python -c 'import ROOT, lightgbm'` versions (re-review N5's alternative) |
| F7 | NOTE | `Q/two-d-path/REPORT.md:504` | Wording: "a constant additive offset … changes both centrals equally" is ambiguous. What is meant is that it shifts the CV and every universe value of one estimator by the same c. The math is correct, and the integration REPORT §3.1 states it cleanly. The quote of the original sentence is faithful, byte for byte apart from the line wrap. | `git show b116f3b7`; `git show 2a28a13d:…/REPORT.md` | Optional: "shifts the CV and every universe value of one estimator by the same c" |
| F8 | NOTE | `docs/orchestration/CATALOG.md:87`; `KNOWN_ISSUES.md` row 88 | (a) The CATALOG says the three reports "landed on `main` together". That is prospective at the fixed commit, where `main` is still `a16d5786`. It becomes true at merge. (b) KI-88 quotes "303–1,131" without naming the declared tier. A regional alternative of 149–570 exists. (c) `generate_manifest.py --check` reports `unused_overrides=2`: the pre-registered `two-d-followup` and `sb1-run` rows, which are intended. | measured | (a) is acceptable if the branch merges as is. For (b), optionally add "(declared tier)" |
| F9 | NOTE | `Q/integration-followup/REPORT.md:160` | The column headed "package pin `d4335d3b` tree" is backed by committed logs in `logs/final-dcae1a3a/`. P is identical between those two commits (measured: empty `git diff --name-only d4335d3b ae0bfb76 -- P <modules> <guard>`), so this is cosmetic. | measured | Optionally name `dcae1a3a` (P-identical to `d4335d3b`) |

The checklist items that are not listed above passed with no finding.

## What I verified

### 1. Assembly and scope
- **Ancestry.** `2a28a13d`, `b7c951b3` and `7d173bd0` are all ancestors of `ae0bfb76`. Each one's merge base with the base is `a16d5786`.
- **Merges.** `git diff --name-only a16d5786 7184e436` (65 paths) equals the union of the three lanes' changed paths. The merges add nothing else, and no lane deleted a file. Every lane path is blob-identical to its lane head in `7184e436`.
- **Lane files changed later.** At `ae0bfb76` every lane file is blob-identical to its lane head except four:
  - `two-d-path/REPORT.md` (`b116f3b7`);
  - `sb1-prep/REPORT.md`, `sb1-prep/checks/mutation.py` and `sb1-prep/tests/test_launch_chain.py` (`62e55530`, `d4335d3b`).

  All four are inside the owner's declared scope.
- **Other owner changes after the merges:**
  - `KNOWN_ISSUES.md`, only row 88;
  - `CATALOG.md`;
  - `MANIFEST-overrides.tsv`, +3 rows;
  - `MANIFEST.tsv`, generated;
  - new files under `Q/integration-followup/`;
  - new `sb1-prep/logs/mutation-results-run5-62e55530.json`.

  `docs/OPEN_ITEMS.md` and KI rows 89/90 are unchanged. No driver, helper, adopted product, publication source or control-plane source changed.
- **Preserved reviews.** `two-d-path/review/{review,review-cycle1}.md`, `sb1-prep/review/{review,review-cycle1}.md`, `d-id/review-admission.md` and `d-id/verification.md` are blob-identical to their lane heads.
- **Publication sources.** `git diff --stat a16d5786 ae0bfb76 -- docs/analysis-note docs/publication publication`: empty.
- **Remote-tracking refs** (local refs, not a live fetch): `origin/main` = `a16d5786`; lane refs = `2a28a13d` / `b7c951b3` / `7d173bd0`; `origin/integrate/followup-20261010` = `ae0bfb76`.
- **Logs.** No local paths or e-mail in the committed integration logs or in mutation run 5.

### 2. two-d-path
- **Post-review delta `0a2e0f41..2a28a13d`.** This is report text for N1–N7. The N5 JSON change drops the 50-replica `boot50` arm from `XR_stage_T`, so 63.2–292.9 becomes 15.3–227.8. The `T_syst_false_fail` field is renamed and gains `"not quantified"`. The cell-126 `(7, 14)` field is added. The report quotes the new range everywhere I checked (`:392`, `:476`, `:625`, `:688`), and no stale 63–293 remains.
- **Re-run.** `design_arith.py --self-test` gave PASS (rc 0). `--write x.json` followed by `cmp` against `design_arith.json`: IDENTICAL.
- **My own arithmetic** (admitted = runs × rate × 1.15 / 0.8):
  - **Stage T:** 16 × 0.66711 × 1.4375 = **15.343**, and 16 × 9.90611 × 1.4375 = **227.84**. Both rates trace to `speed/results/costs.json` `exact_backend_unit_rates.universe_p1` / `universe_now_safe`.
  - **L42 complete, declared tier:** runs = 2 × (2R + R) with R = 540, so 3,240.
    - Optimistic: (300 × 0.0591 × 1.15 + 1.3 + 3,246 × 0.0591 × 1.15) / 0.8 = **302.88**.
    - Conservative: (300 × 0.216 × 1.15 + 23.8 + 3,246 × 0.216 × 1.15) / 0.8 = **1,130.78**.
  - **Regional tier:** 149.45 / 570.02.
  - **Rate operands:** 0.0591 and 0.216 are in speed REPORT:82–83 (`59410433`, `59409026_1`). S-b 1.3 / 23.8 is uncertainty-preparation `c/costs.json` `setup_items[2]` 1.3242 / 23.75, rounded.
  - **R = 540:** my approximation of var(ln σ̂), (1/(2(n−1)) + γ/(4n)) per arm with γ = 0.024, requires n ≈ 541 for (z_a + z_b) se ≤ ln 1.25. That is consistent with the code's 540 (se 0.04325 ≤ 0.04326).
- **Correction `b116f3b7`.**
  - The quoted sentence matches the post-review original.
  - The counterexample is correct. With x_u^X = x_u^L + c for every u and the CV, the centrals differ and every delta is equal. A central-value difference therefore says nothing about the deltas.
  - "The transfer remains unmeasured" is supported: no exact universe unfold exists.
  - "Stage T's assurance unestablished" is supported: the false-fail rate and power under the width-equivalence null are uncomputed, and the JSON says "not quantified".
  - A grep for `0.136` and "centrals" in the two-d-path REPORT, the integration REPORT, KI-88, CATALOG and `design_arith.py` finds no other passage that relies on "different centrals imply different deltas". `:195`, `:196` and `:211` quote the central difference only as a continuity cost.
  - The one remaining overreach is F2.

### 3. Integrated disposition
- **Integration §3.2, KI-88 and CATALOG.** All three present L42's 303–1,131 as a proposed program for narrowed claims that Joseph has not accepted. They list four conditions as open: split-sample assurance, half-to-full scaling, the model-bias treatment (B± beside `C_tot`, no untouched domain) and systematic reuse (62 % Flux change, frozen fallback). They label the seed-mechanism evidence synthetic, and they keep §11 item 3 unapplied.
- **Labels.** No PASS or adoption label, and no narrowed claim, appears on KI-88 or CATALOG for the 2D design. The lane's "PASS: L42" stays in the lane report only.
- **Checked against two-d-path.** I checked these against two-d-path §2 (narrowing, not claimed), §11 and §15. The D-ID CATALOG wording is F1.

### 4. SB1
- **Lane delta `1ac7cec3..b7c951b3`.** I read all of it.
  - **`submit()`.** `local id` and the assignment are separate statements, so `|| return 1` sees the status of `$(…)`. The non-numeric check follows.
  - **Failure path.** A non-zero `submit` fails the top-level assignment, `set -e` runs the `ERR` trap once, and the trap is not inherited into `$(…)` (no `set -E`).
  - **Failure after all six are queued** (the post-submission `python` writing `submission.json`): the trap cancels all six ids, which fails closed.
  - **Unparseable reply after a real enqueue:** F3.
- **Environment.** All four batch scripts run `sb1_check_env` and then `source "${SB1_ENV_SETUP}"` at top level. A mismatch gives exit 3 under `set -e`, and a missing file gives an empty hash, which also refuses. Receipts record `SB1_ENV_SETUP_SHA256` from `run.env`. Residuals are in F6.
- **Authorization binding.**
  - `re.fullmatch(r"[0-9a-f]{40}")`;
  - `merge-base --is-ancestor`;
  - `git diff --name-only pkg HEAD -- P ∪ modules ∪ guard` must be empty;
  - the authorization text must contain both the 40-hex id and the 64-hex manifest sha.

  All four are correct. The definition looseness is F5.
- **Owner delta `b7c951b3..d4335d3b`.** Tests, two mutants, the run-5 log and REPORT text. No script, module, launch spec or manifest changed.
- **Suites** (venv313 + PyROOT, tripwire on `PATH`, scratch `TMPDIR`):

  | suite | result | skips |
  |---|---|---|
  | `test_branch_select` | Ran 16, OK | 0 |
  | `test_sb1_guarded` | Ran 10, OK | 0 |
  | `test_launch_chain` | Ran 29, OK | 0 |
  | `test_package_consistency` | Ran 7, OK | 0 |
- **Negative controls in a `git clone --shared` scratch copy at `ae0bfb76`:**
  - **Removed `sb1_check_env` from `launch/sb1_unfold.sbatch`.** `test_launch_chain` ran 29 with `FAILED (failures=2)`: `test_every_job_refuses_an_environment_changed_after_submission` [sb1_UL] and [sb1_SL]. The other 27 pre-existing tests passed, which confirms the gap the owner reported.
  - **Removed the `^[0-9]+$` line from `sb1_submit.sh`.** `FAILED (failures=1)`: `test_a_failed_first_or_last_sbatch_or_a_non_numeric_id_stops_the_submission` [non-numeric id].
  - The clone was restored after each mutation.
  - **My own extra probe:** a job queued and then an unparseable reply. See F3.
- **Pin.**
  - `git log -3 ae0bfb76 -- P`: `d4335d3b`, `62e55530`, `b7c951b3`, so the last commit changing P is `d4335d3b9bc2502002f93390f9555d07e134855f`.
  - `git diff --name-only d4335d3b ae0bfb76 -- P <24 manifest modules + guard paths>`: empty.
  - No bound module changed between `a16d5786` and `ae0bfb76`.
  - sha256 of `P/manifest/expected-code.json` is `f060df81338b17069a31a0a2cc7a3430ed81c91ce64de6d6f3d54b80e08eb15a` at `ae0bfb76`, at `d4335d3b` and at the lane head `b7c951b3`.
- **SB1 REPORT §7.2 and the integration note.** Both are accurate apart from F4 and F5. Nothing in SB1's record implies authorization: "the cluster benchmark remains unauthorized", and dispatch §8 says "SB1 authority: none yet".
- **Mutation run 5** (`logs/mutation-results-run5-62e55530.json`):
  - commit `62e55530`; verdict "29 of 29 caught";
  - baseline 7 + 3 + 17, rc 0, `skipped: False`;
  - 28 mutants were caught by targeted-test FAILED;
  - `restore-addresses-dropped` was caught by a ROOT segfault (rc 129). `mutation.py:9` declares a crash as caught. That rule predates this integration, and the baseline passes, so I raise no finding.

### 5. D-ID
- **Outputs and controls.** `git diff --stat 7d173bd0 ae0bfb76 -- Q/d-id` is empty, so `outputs/` is byte-identical. `pytest -q -p no:cacheprovider -rs Q/d-id/test_did.py`: **29 passed, 0 skipped** (12 warnings), 54.7 s, RSS 0.50 GB. I did not re-run the real-input calculation.
- **Integration §5 against `verification.md` and D-ID REPORT §9.2/§9.3/§11:**

  | quantity | integration §5 | source |
  |---|---|---|
  | J C-counted | 121 / 144 | 0.840 × 144 = 121 |
  | J finite widths | 117 | 121 − 4 acceptance holes |
  | finite-width C shares | 0.812 / 0.696 / 0.333 | 117/144, 16/23, 1/3; verification (c)2 |
  | exclusions | 232/376, 129/152, 63/66 | verification (c)1; REPORT §9.2 table |
  | medians | 9.5/8.3/8.6 and 4.3/5.3/4.0 | REPORT §9.3 table, GiBUU and q3 columns |

  - **Not reproduced by the verifier:** T3 and split-half trajectories, which matches "not reproduced".
  - **Convergence:** no T2 run converges, and only 12 of 121 meet the per-functional criterion. That supports the "last iterates" remark.
  - **Limits preserved:** binned, signal-only, development truths, resolution-sensitive exclusions, H2 uninformative, and no interval validated.
  - **Minor omission:** §5 drops the qualifier "of the |r_GBDT| > 2 % functionals" from the exclusion counts. It is not misleading in context.

### 6. Shared checks (on the fixed tree, tripwire on `PATH`)

| check | result | skips |
|---|---|---|
| OI-136 ratchets, both files | Ran 17, OK | 0 |
| `guard/inventory.py` | AST 17, all listed; fail-open 16 `7aa29431…`; 0 unlisted; candidates 144. Same as the integration log | — |
| `verify_hash_bindings.py` | ALL BINDINGS INTACT (rc 0) | — |
| `generate_manifest.py --check --at-sha HEAD` | OK (rows 2,038; `unused_overrides=2`) | — |
| `generate_manifest.py --check` | OK, `tree=clean` | — |
| `live_doc_indexed.py --unrowed` | 0 unrowed | — |
| `control_plane_lint.py` | CONTROL-PLANE PASS | — |
| optional: n2 `test_producer_*.py` (venv313) | Ran 31, OK | 0 |

None of these commands modified the worktree (`--porcelain` stayed empty).

### 7. Registration and dispatch
- **Overrides.** `MANIFEST-overrides.tsv` has `MACHINE open ""` rows for `integration-followup/REPORT.md`, `two-d-followup/REPORT.md` and `sb1-run/REPORT.md`. CATALOG routes the integration report and lists both next owned reports. It states that registration grants no compute, experiment, adoption or claim-scope authority.
- **Dispatch §8.** It states:
  - the tested main pin;
  - the SB1 pin and digest, in full;
  - SB1 authority "none yet";
  - one owner per subtree, with write scopes;
  - that shared records stay with the integration owner.

  It grants no authority.
- **Open routes.** KI-90 and OI-136 are kept as open routes (REPORT §7, §8) and are not repaired. Their KI rows 89/90 are unchanged.

### 8. Other
- **Unreviewed deltas are labeled as such.** The integration report §1 and SB1 REPORT label the lane post-review deltas and the owner's repairs as not re-reviewed. None is silently treated as reviewed.
- I found no misquoted number.
- No required check was skipped.
- I found no regression.

## Cleanup

My worktree `scratchpad/fu/review-wt` and the scratch clone were removed after this record was
written. No other worktree, branch, ref or config was touched. Nothing was committed, pushed or
messaged.
