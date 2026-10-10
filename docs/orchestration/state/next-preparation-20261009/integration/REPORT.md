# Integration of the next-preparation batch (six lanes), 2026-10-09

**CITABLE FOR:** what the combined tree contains and how it was assembled; which lane statements are
reviewed results and which are unreviewed or future designs; the two guard-minor repairs and their
controls; the guard × structure dependency check; the shared-register dispositions applied here; the
publication build and source-equivalence checks; the three registered next-session report paths.
**NOT CITABLE FOR:** any scientific result, uncertainty, coverage, adoption, gate or compute authority.
Integrating these lanes does **not** achieve the publication-ready measurement (a reproducible central
estimator, a matched uncertainty construction and validation supporting the claims actually made).

| field | content |
|---|---|
| `Lane` | integration owner for the completed next-preparation batch (publication, guard, structure, speed, gbdt, pet) |
| `Decision` | Can the six completed lanes be integrated without regressions, with correct shared records and synchronized publication sources? |
| `Branch` / `Base` / `Head` | `integrate/next-preparation-20261009` / `5ac9706a21e8a5ac8863a65fd7623d8ab8d22269` (= `origin/main` at 2026-10-10T02:58Z, the six lanes' common base) / the commit that carries this revision; the reviewed commits are in §8 |
| `Owned files` | this report and `Q/integration/` (`checks/`, `logs/`); `fixed_truth_toy.py` and `n2/harness.py` (R1, R2 only), with their tests `n2/test_producer_provenance.py`, `n2/test_n2_harness.py` and the new `n2/test_producer_final_dependencies.py` (all under `2d-unfolding/uq/coverage_fixed_truth/`); `KNOWN_ISSUES.md` rows 89–90; `docs/OPEN_ITEMS.md` `OI-136` (one dated append); generated `docs/orchestration/control-plane/source-record-inventory.tsv`; `docs/orchestration/CATALOG.md` (routes); `docs/orchestration/MANIFEST-overrides.tsv` (four rows); generated `docs/orchestration/MANIFEST.tsv` |
| `Pinned inputs` | §1: the six delivered heads, the standalone branch `6a7fa2f2…`, and the governing records |
| `Resources` | §10. Cluster, GPU, training, toys and event loops: **0** |
| `Review` | §8 |
| `Model / effort` | owner: Claude Opus 5.5 (`claude-opus-5-5`), Claude Code; effort not observable to the session |
| `Disposition` | §11 |
| `Next action` | §12 |

`Q` = `docs/orchestration/state/next-preparation-20261009`.

## 0. Setup (campaign review §1, §5)

- **Roles.** One owner (this session, Opus 5.5) and one fresh read-only reviewer on a fixed combined
  commit. The reviewer gets one initial review and one focused re-review after a single repair batch.
  CAMPAIGN-REVIEW §5 suggests Astra High for consequential review, which is not reachable from this
  session; the reviewer is a fresh Claude subagent, so the review is not cross-provider independent.
- **Terminal conditions.** PASS: the integration is checked, reviewed, merged and synchronized, with
  the remaining scientific limits explicit. FAIL: a demonstrated material regression remains.
  INCONCLUSIVE: required evidence, environment, review or remote delivery is unavailable.
- **Budget.** 6 active hours including review, 3 local CPU core-hours, two compute threads per
  command, 8 GiB peak RAM and 3 GiB scratch beyond worktrees. No scientific compute.

## 1. Inputs and ownership

- `git fetch origin --prune` at 2026-10-10T02:58Z: `origin/main` = `5ac9706a`, equal to the octopus
  merge base of the six branches. There was no upstream delta to reconcile.
- Each remote head equals the one the integration prompt names, and each lane's `REPORT.md` and
  preserved review records were read at that head:

  | lane | head | report | last reviewed commit | delta after it (§3) |
  |---|---|---|---|---|
  | publication | `78837efe8adbb980970b18c6751dd605c6b3ddde` | `Q/publication/REPORT.md` | `b7f4c065` (re-review PASS) | `11c753b7`: one sentence in `app_statmethods.tex` (N1), plus records |
  | guard | `63257cd4d03d02e1a09bb86e9df7bd987c0fd217` | `Q/guard/REPORT.md` | `a778f67a` (re-review PASS, R1/R2 open) | report only |
  | structure | `0f4a059fb4588ac0fb262e12907c6a09d6999b16` | `Q/structure/REPORT.md` | `90788f5f` (cycle 2 ACCEPT) | report and the preserved cycle-2 review only |
  | speed | `318d3e45db6dba2263479385bc9cdf1916549e7f` | `Q/speed/REPORT.md` | `ce224e7f` (cycle 1, no MATERIAL left) | report and preserved reviewer files only |
  | gbdt | `d6652270a5f755cd5f33ae6ffcbb43e30d4750fc` | `Q/gbdt/REPORT.md` | `31517ad7` (round 2) | **content:** `reduce_saved_outputs.py`, `results.json` and the branch-B route (N1, #7, #8) |
  | pet | `d9a460c61e9e1e5756025dd3be63324398f2aaeb` | `Q/pet/REPORT.md` | `7658ad80` (cycle 2, all RESOLVED) | report only (minors A, B; tracked-bytes figure) |

- Standalone `MINERvA-OmniFold-Analysis-Note`: `origin/main` = `ad3fb8000a8d373a796856bdbc4c050b9970fc30`;
  `sync-publication-correction-20261009` = `6a7fa2f20c3404695623a77279ca1ab3c5867003`, one commit
  ahead of `main`.
- Governing records read: `AGENTS.md`; `CAMPAIGN-REVIEW-20260929.md`; `docs/CURRENT_WORK.md`;
  `docs/LOCAL_CHECKOUTS_AND_STORAGE.md`; `Q/DISPATCH.md`; `Q/closeout/REPORT.md` (Joseph's ruling, §11).
- **Ownership, measured 2026-10-10T03:05Z.** All 25 worktrees had no uncommitted change to any path
  this session edits. Of 215 local and `origin` refs, the only ones with commits since 2026-10-08
  touching those paths were the six lanes themselves. Open PRs: #62–#67, one per lane, none merged.

## 2. Assembly

- Six `--no-ff` merges in dispatch order onto `5ac9706a`: `7de78719` (publication), `954a3cf7`
  (guard), `f84ddeaf` (structure), `3d24c5e6` (speed), `85571d60` (gbdt), `dd73de73` (pet). No textual
  conflict at the current heads. The lanes' changed-path sets are disjoint.
- **Byte identity.** Every path a lane changed relative to `5ac9706a` (153 paths, excluding the
  generated manifest) is blob-identical in the merged tree to that lane's delivered head. All six heads
  are ancestors of the integration head, so every pinned commit stays reachable.
- **Manifest.** `generate_manifest.py --check` was OUT OF DATE after the six merges, as each lane
  predicted. It is regenerated from source once, after this session's own files exist. No row is
  hand-merged (§9).

## 3. What each lane established, and what it did not

The lanes' frozen numerical records are not rewritten. This section separates **recorded results**
(reviewed measurements or reductions) from **admitted designs** (none here) and **proposed future
designs** (everything that would need a new authorization).

| lane | recorded result (reviewed) | unreviewed after the last review | proposed, not admitted |
|---|---|---|---|
| publication | note, primer and paper disclose the unmeasured 2D transfer and correct "pinned seeds"; readiness **not achieved** | `11c753b7`: "vary that seed" → "vary the GBDT seed (seeds 1--10)" in `app_statmethods.tex` (N1). Inspected here: one clause, no number moved, rendered in the note | none |
| guard | producer repair, provenance guards, ratchets 17/17, a synthetic-only N2 harness | none in code | N2 itself, and any real admission |
| structure | reported-cell identity in the UQ producers; superseded rollup refused; the adopted chain's cells equal | none in code | §5 patch for two publication consumers; P1–P3 |
| speed | where the cost goes; D1 PASS bounded to full-node LightGBM universe unfolds; D2/D3 INCONCLUSIVE; D4 FAIL | F10 header, F11a, N1, N2, N4 (record corrections) | SB1; every exact-backend price is a forecast |
| gbdt | saved-output reductions E1–E8; D2 FAIL; D3 FAIL against proposed targets | **the branch-B downstream route (N1) and the cost repairs (#7, #8)** | D-ID; I1; I2 |
| pet | saved-output diagnosis at study scale; (3) FAIL at the declared endpoint | minors A, B (wording and one table row) | E1; S1–S6 |

**Three distinctions the combined record must keep.**

1. **GBDT branch B is unreviewed, and integrating the record admits nothing.** D-ID's measurement design
   is reviewed (ACCEPT-WITH-REPAIRS at `31517ad7`). The route that a branch-B outcome would take
   (read from the existing s5p study-K traces; extending them is a re-run of terminal s5p study K at
   ≈ 8.7 admitted node-h) was repaired after that review and has had no independent review. The lane
   itself labels it INCONCLUSIVE for review (gbdt REPORT §13). The cost repair is checked here
   arithmetically. The subtotal is 0.053 + 2.004 + 0.196 + 0.664 + 0.1 = 3.018 core-h, so the admitted
   range is (3.018 + 1)/0.8 = 5.02 to (6.036 + 1)/0.8 = 8.80 core-h. The committed
   `reduce_saved_outputs.py` reproduces `results.json` byte for byte (24 s, one thread). **D-ID is not
   admitted.** It needs Joseph's resource decision, and its branch-B route needs a review before any
   branch-B outcome is acted on (§7).
2. **PET's operating characteristics and event counts belong to PET's specified design, not to
   simulation in general.** The 101–127× and 225× inventory multiples (pet REPORT §8) are products of
   the following:
   - the declared point estimator E\* (H2S1T24, K = 5, the mean of six Poisson-bootstrap members);
   - its §9 interval;
   - the **proposed, unratified** 0.63 / 0.92 lower bounds;
   - per-decision versus joint sizing over m = 32 decisions (four cases × four regions × two levels);
   - the full-domain endpoint with independent inputs;
   - 11.6 M rows per data-size experiment, which is 9.6 M pseudo-truth plus a 2 M-row prior that
     `design_cost.json` labels an assumption.

   The lane's own table shows the dependence. At 24, 120 or 300 replicates per case the multiple is
   5.7×, 28× or 71×. A different estimator, interval, tolerance, endpoint (fiducial, or conditional on
   the DEV bank) or prior size changes the count. These numbers are not a statement about the scalar
   or 2D programs, or about what any other PET design would need.
3. **Speed's PET figure prices a different procedure from the PET lane's.**
   - Speed's "PET repair" row (≈ 3,182 A100-h, ≈ 1.6 k at a hypothetical 2×) prices the older
     H2S1T24 repair iteration from `final_design/resources/cost_fb_look1-20260930.json`: 720 DEV plus
     1,080 RB unfoldings.
   - It is **not** the cost of the PET lane's complete data-scale validation. That is 142–150 k
     A100-h under per-decision sizing, or 238–246 k joint, at a 2 M prior (pet REPORT §8). The PET
     lane's first discriminating step, E1 look 1, is a forecast ≈ 575 A100-h.
   - Both figures stand as recorded. They must not be compared as one quantity, and speed's 1.4 %
     share of the GPU balance is not a price for the PET endpoint.

Also carried, not re-litigated:

- Speed's memory-bound exact-transfer price (`P05` ≈ 530 / 927 / 1,853 node-h by packing policy,
  ≈ 125 with prototype 1) is a forecast that depends on SB1. A's and C's records are closed and are
  not annotated here. The correction lives in speed REPORT §6 and §13.
- GBDT §9's speed sensitivity was written before speed's result was pushed. Its f and s values are
  labelled hypotheticals, not speed's measurements.

## 4. Guard repairs and the guard × structure dependency check

### 4.1 The two repairs (scope: R1 and R2 only)

| item | commit | change | negative control |
|---|---|---|---|
| R1 | `21c97390` | `fixed_truth_toy.py` `load_code`: a module path that resolves outside the checkout raises `ProvenanceRefusal` (exit 3) instead of `ValueError` (exit 1) | `test_a_module_symlinked_outside_the_checkout_is_a_refusal_not_a_crash`: toy design, driver and helper each replaced by a symlink into checkout B → exit 3, the refusal message, no traceback, no output |
| R2 | `98382f86` | `n2/harness.py` `check_admission`: the authorization path is resolved against the checkout root, and the `docs/orchestration/` prefix and name rules apply to the normalized path | `test_the_authorization_path_is_normalized_before_its_prefix_test`: the canonical record still admits ("admission holds"); a committed `AUTHORIZATION-` file outside `docs/orchestration/` reached through `..`, and one outside the checkout, are refused. All three state the file's true digest |

No change to `nd-unfolding/mnv_guarded_run.py`, `n2/execution.py`, the probe, the 2D driver, the pinned
`omnifold.py` or any receipt-bound file. Neither repair found a binding that blocked it.

### 4.2 The real analyzer's final dependency set

**The gap.** The guard lane's producer tests stub `analyze_uq.py` with a module that imports only
`technote_style`. After structure, the real `analyze_uq.py:46` also does
`from reported_cells import …`. On the merged tree `dd73de73` the 25 producer tests passed, but no test
executed the real analyzer or `reported_cells.py`.

**What protects it.** Discovery in `n2/execution.py` is generic: `finalize` sweeps `sys.modules` for
every module whose file is inside the checkout. Strict mode therefore requires `reported_cells.py` to be
stated and committed, with no code change. `n2/test_producer_final_dependencies.py` (`b19b5e91`) now
shows this on the real files. The fixture holds the real `analyze_uq.py`, `reported_cells.py` and
`technote_style.py`, and runs `ki85_compare` under `mnv_guarded_run.py --require-provenance`:

- **Positive.** The full final set and the final commit are stated. Exit 0; every executed file is
  recorded at HEAD; and the median equals the pure function's.
- **Refused (exit 3, no output):**
  - `reported_cells.py` or `technote_style.py` unstated;
  - a changed `reported_cells.py`, stated with its old digest or with its new, uncommitted one;
  - the commit before the final implementation;
  - a module that `reported_cells.py` starts to import and that no expectation names. Once stated,
    that module runs, so the check is a sweep, not a list of known import patterns.

**Strict expectations at this integration** (sha256 of the committed bytes; `commit` must be the
admitted checkout's HEAD, which must contain `b19b5e91`):

| producer | executed repository modules | sha256 |
|---|---|---|
| `ki85_compare.py` | `2d-unfolding/uq/coverage_fixed_truth/ki85_compare.py` | `f396cf82f0d206101bec21c8feee0426e377b77e7ea71d592df6b3b20c3cbf4e` |
| | `2d-unfolding/uq/analyze_uq.py` | `f0f29ca1e3b9a8c3b44213d6fda418aadd2655cad51d92fad5a3b5bcff181d94` |
| | `2d-unfolding/uq/reported_cells.py` (**new dependency**) | `2ddf7c9fbe4c0ffc236c3f82e4b81b12204d17005f90b2dcc0f7a5db5e501594` |
| | `technote_style.py` | `95be4ff792be6e37ece8bd0382d520a551ac67314d3b52008a5ff48d0c490252` |
| | `…/n2/__init__.py`, `…/n2/execution.py` | `65c577a8…`, `f35dacc6…` |
| `fixed_truth_toy.py` | `…/fixed_truth_toy.py` (**changed by R1**) | `8bd28807f79cdee56d4f519d30a6ee8be0207d660a1beff0fbd9ab4eaeab05ff` |
| | `…/toy_design.py`; `2d-unfolding/unfold_2d_omnifold_unbinned.py`; `unbinned_unfolding/python/omnifold.py` | `f37d4d99…`; `3cc5adc7…` (unchanged); `e96234124a31…` (unchanged) |
| | `…/n2/__init__.py`, `…/n2/execution.py` | as above |

A real run also states its input digests (toy: `omnifile`, `mcfile`; KI-85: `interim`, `purity`).

### 4.3 Mutation controls

[`checks/mutation.py`](checks/mutation.py) applies each mutant in a fresh `git clone --shared` of
`b19b5e91`. The unmutated clone passed every targeted command first, with no skips. Record:
[`logs/mutation-results.json`](logs/mutation-results.json).

| mutant | targeted test | result |
|---|---|---|
| R1 reverted (bare `relative_to`) | R1 test | red (3 subtest failures) |
| R2 reverted (string prefix) | R2 test | red (2 subtest failures) |
| `unrecorded_repo_modules` returns `[]` | dependency tests | red (7 failures) |
| strict mode ignores unstated modules | dependency tests | red (3) |
| strict mode ignores bytes not at HEAD | dependency tests | red (1) |
| stated commit not compared | dependency tests | red (1) |

**6 of 6 caught.**

### 4.4 Test results (every count from the runner's own output; skips counted)

Environment: `python3` is conda 3.12.2 (numpy 1.26.4, no PyROOT, which fails to load there).
`venv313` is a scratch venv over Homebrew Python 3.13.7, with PyROOT 6.36.000 from
`root-config --libdir`, numpy 2.4.4, matplotlib 3.10.1 and pytest 8.3.4. Every run used
`OMP_NUM_THREADS=1` and a scratch `TMPDIR`.

| suite | interpreter | merged tree `dd73de73` | final code head (§8) | skips |
|---|---|---|---|---|
| `n2` producer provenance (`test_producer*.py`) | venv313 | 25 OK | 31 OK (+1 R1, +5 dependency) | 0 |
| `n2` harness (`test_n2*.py`) | python3 | 21 OK | 22 OK (+1 R2) | 0 |
| `test_coverage_fixed_truth.py` | python3 | 20 passed | 20 passed | 0 |
| OI-136 ratchets (both files) | python3 | 17 OK | 17 OK | 0 |
| `test_reported_cells.py` | venv313 | 18 passed | 18 passed | 0 |
| `test_final_rollup_full_refusal.py` | python3 | 3 passed | 3 passed | 0 |
| KI-84 `test_bootstrap_completeness_ki84.py` (`-W error::ResourceWarning`) | venv313 | 15 OK | 15 OK | 0 |
| `verify_hash_bindings.py` | python3 | ALL BINDINGS INTACT | ALL BINDINGS INTACT | — |
| `test_hash_bindings.py` | python3 | 33 passed | 33 passed | 0 |
| OI-136 inventory (`guard/inventory.py`) | python3 | — | AST 17 listed, fail-open 16 `7aa29431…`, 0 unlisted, 0 adjacent | — |

The reported-cell suite was run with PyROOT and matplotlib, so none of its ten ROOT-gated script tests
skipped. Run without them it skips ten (structure REPORT §8), and that count is not used here. The
inventory's probe candidates rose 143 → 144 between the guard head and the integrated tree.
The one addition is structure's `checks/census.py`, which contains the literal but no insert, so it adds
no fail-open site. Logs: [`logs/`](logs/).

## 5. Shared registers (applied in `47cc98f7`)

- **`KNOWN_ISSUES.md` 89 → RESOLVED for the ratchets; the hazard class stays open under `OI-136`.**
  - Counts re-measured on the integrated tree.
  - Names R1/R2, the 10 older exceptions and the families not re-measured (`.sh`, `MNV_REPO`, gate6).
  - Names the three unchanged unguarded launchers
    `coverage_fixed_truth/sbatch_{fixed_truth_toys,equivalence,ki85_arms}.sh`, and the final strict
    KI-85 dependency set.
- **`KNOWN_ISSUES.md` 90 stays OPEN.**
  - The producers are fixed by structure.
  - The two publication consumers, `compare_to_paper_fullcov.py` and
    `uq/plot_uncertainty_fig6_7_style.py`, still align by count.
  - The row records structure REPORT §5's patch as the follow-up, owned by the publication owner or
    Joseph. No pinned producer was changed here.
- **`docs/OPEN_ITEMS.md` `OI-136`: one dated append.**
  - It notes that the row's 59/58 predate the 2026-09-03 authorization.
  - It records the re-measured counts, what moved, and what stays open.
  - It says "This row is not solved".
  - `control_plane_lint.py --write` regenerated `source-record-inventory.tsv`; `CURRENT_WORK.md` is
    unchanged.

**Proposed by lanes and not applied here (outside this integration's register scope):**

- speed §13's `KNOWN_ISSUES` row on whole-file universe reads;
- PET §13's status patch for `PET_UQ_REMEDIATION_STATUS.md`;
- structure §13 item 4's optional 2D-status line;
- annotations to A's and C's closed records.

Each stays in its lane report for the owners of those files.

## 6. Publication

- **Source equivalence** ([`checks/source_equivalence.sh`](checks/source_equivalence.sh)). All 120
  tracked files under canonical `docs/analysis-note/` at the integrated head are blob-identical to
  standalone `6a7fa2f2`. The standalone has two more, its own `.gitignore` and `AGENTS.md`. The base
  pair (`5ac9706a` against standalone `ad3fb800`) gives the same result, as a control.
- **Build** (`docs/analysis-note/build_all.sh` at `b19b5e91`, clean tree):
  - rc 0; `RESULT :: PASS :: head=b19b5e91… tree=clean`;
  - containment self-test PASS (17 perturbations rejected); `SEC4-RECEIPTS :: PASS (14/14)`;
  - note 123 pp, primer 9 pp, paper 11 pp, as in the publication lane's build;
  - no unresolved references after one latexmk invocation per target, and no `??` in `pdftotext` of
    any PDF.
- **Rendered passages** (`pdftotext`, whitespace-flattened):
  - "pinned seeds" appears in none of the three PDFs.
  - The paper says "with an unpinned seed".
  - The note says scikit-learn's `random_state` "was None" and that the transfer is "not a
    demonstration that the quoted uncertainty is wrong".
  - The fixed-truth test "tests the LightGBM statistical estimator".
  - The primer says the rebuilt bars "have not been re-tested".
  - The unsourced "seed-ensemble mean … agrees … to 0.28 %" is absent. The remaining `0.28` hits are
    unrelated quantities.
- The "not publication-ready" conclusion is preserved in `CLAIMS-20261005` §H, the
  `PACKAGE-MANIFEST-20261006` 2026-10-09 note and `KNOWN_ISSUES.md` 88. No figure, value or numerical
  product changed.

## 7. Next sessions, registered (not launched)

Pre-registered as `MACHINE open` in `MANIFEST-overrides.tsv` and routed from `CATALOG.md` § Current
work. Each path is absent until its session pushes it. One owner per subtree: the session dispatched to
it writes only `Q/<subtree>/`, and claims anything else in its report before editing. This session
launches none of them and does not wait for them. Their later integration is a separate bounded action.

| report path | subject | inputs | preconditions it cannot waive |
|---|---|---|---|
| `Q/two-d-path/REPORT.md` | the 2D publication path after keep-and-disclose: the `KNOWN_ISSUES.md` 88 pairing | closeout §11 (Joseph's ruling); publication REPORT §8; `DELIVERY-20261008-uncertainty-preparation.md` §6; A's pairing assessment; speed §6–§7 for the forecast prices | measuring the transfer, a LightGBM re-quote, a changed central estimator, N2 and a KI-85 lift are each Joseph's decision; speed's exact-backend prices are forecasts until SB1 |
| `Q/sb1-prep/REPORT.md` | preparation for speed's SB1: prototype-1 branch lists for the truth, background and data loaders, with local byte-equality tests (speed review N3) | speed REPORT §4, §9, §15, `speed/proto/`, `speed/bench/` | local only; the 2D driver is claimed by no lane and stays unedited; running SB1 (≈ 1.3, cap 2.0 CPU node-h) needs Joseph's authorization |
| `Q/d-id/REPORT.md` | the 5D GBDT diagnostic D-ID | gbdt REPORT §6, §10, §14, `results.json`, `comparator.py` | Joseph's resource decision (5.02–8.80 local core-h, a ≤ 1.44 GiB read-only copy whose digest is to be re-measured, 0 GPU, 0 training); an independent review of the post-review branch-B route (N1, #7, #8) before a branch-B outcome is acted on; extending s5p study K needs its own authorization |

## 8. Independent review

**Pending.** One fresh read-only reviewer on a fixed commit of this branch. It gets one initial review,
and one focused re-review if a repair batch is needed. Its scope is the integration delta and
cross-lane behaviour, not a restart of the six completed reviews. Numerical checks inspect operands and
independently reproduce the consequential changed calculations. This section is completed after the
review, with the reviewed commit, findings and dispositions.

## 9. Delivery

**Pending review.** The plan follows Joseph's authorization in the integration prompt:

1. Refresh `origin/main`, and reconcile any new delta before merging.
2. Merge this branch into canonical `main` through a PR, using a merge commit.
3. Merge standalone `sync-publication-correction-20261009` into standalone `main` through a PR, using a
   merge commit, and build the standalone `main`.
4. Close superseded lane PRs #62–#67 only once their exact heads are reachable from `main`, with a
   reference to the integration PR.

No force-push, and no evidence branch or tag deletion. The resulting remote heads are recorded on the
merged PR and in the session's final report.

## 10. Resources (to the review freeze)

| item | measured | cap |
|---|---|---|
| active time | 2026-10-10T02:58Z → freeze (§8); about 0.5 h before the review | 6 h |
| local CPU | ≈ 0.15 core-h of timed commands (baseline suites 270 s, mutation run 77 s, build 34 s, inventory 19 s, GBDT re-run 24 s, dependency tests 12 s, manifest check ≈ 60 s), plus ≈ 0.05 untimed (hooks, git) | 3 core-h |
| threads | one per test command; two for the build (`OMP_NUM_THREADS=2`) | 2 |
| peak RAM | build ≈ 0.14 GB max RSS; tests below 0.5 GB | 8 GiB |
| scratch | ≈ 0.1 GB (`venv313` 83 MB, logs, test temp directories removed per run) | 3 GiB |
| tracked bytes added by this session | ≈ 40 KiB (this report, `checks/`, `logs/`, two tests, the generated manifest rows) | — |
| cluster / GPU / training / toys / event loops | 0 / 0 / 0 / 0 / 0 | 0 |

## 11. Disposition (proposed, before review)

| decision | proposed | reason |
|---|---|---|
| six lanes integrated without regressions | PASS, if the review finds no material defect | disjoint changes, byte identity, all suites green with 0 skips on the final code, the cross-lane gap closed by a test, 6/6 mutants caught |
| guard R1 and R2 | PASS | both repaired in scope, each with a negative control that a revert turns red |
| shared records correct | PASS | KI-89, KI-90 and OI-136 carry re-measured counts and exact routes; OI-136 is not solved, and KI-90 is not closed |
| publication sources synchronized | PASS, if delivery succeeds | 120/120 files blob-identical; three builds PASS; rendered passages checked |
| publication-ready measurement | **NOT ACHIEVED** | KI-88's transfer is unmeasured; VL170 coverage is not re-tested (KI-85 deferred); this integration changes no scientific product |

## 12. Next action

- **Joseph:** none of the three registered sessions is launched.
  - `two-d-path` and `d-id` each need his decision before any compute.
  - `sb1-prep` is local preparation, but SB1 itself needs his authorization.
- **Publication owner, or Joseph:** structure REPORT §5's identity patch for the two count-only
  publication consumers (KI-90).
- **Owner of the `OI-136` route:**
  - wire the ratchets into the hook;
  - replace the three unguarded coverage launchers before any admitted run;
  - re-measure the `.sh`, `MNV_REPO` and gate6 families.
