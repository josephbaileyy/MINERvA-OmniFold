# Follow-up integration: two-d-path, SB1 preparation and D-ID, 2026-10-10

**CITABLE FOR:**
- what the three records establish and what they leave conditional;
- the correction to the two-d-path stage-T argument;
- the SB1 package's checked launch chain, its two test repairs, and its final pin and manifest digest;
- the D-ID interpretation checked against its verification;
- the shared-record changes;
- the dispatch table for the next two owned reports.

**NOT CITABLE FOR:**
- any cross section, uncertainty, coverage or calibration result;
- an adoption, a re-quote, a narrowed claim scope or a changed gate;
- a measured transfer between estimators;
- SB1 performance on Perlmutter;
- compute authority.

**Nothing here adopts a measurement, narrows a claim, lifts KI-85 or authorizes production.** The
publication-ready measurement is not achieved.

| field | content |
|---|---|
| `Lane` | follow-up integration owner (two-d-path, sb1-prep, d-id) |
| `Decision` | Can these records and packages land without treating design completion as scientific admission or changing the publication objective? |
| `Branch` / `Base` / `Head` | `integrate/followup-20261010` / `a16d578646936a0cc6eca41e3e0350e756ee0dca` (= `origin/main`, 2026-10-10T17:03Z) / the commit carrying this revision; reviewed commits in §9 |
| `Owned files` | `Q/integration-followup/`; narrow repairs to `Q/two-d-path/REPORT.md` (§3.1) and to SB1's `tests/test_launch_chain.py`, `checks/mutation.py` and `REPORT.md` (§4); `KNOWN_ISSUES.md` row 88 (one annotation); `docs/orchestration/CATALOG.md`; `docs/orchestration/MANIFEST-overrides.tsv` (three rows); generated `docs/orchestration/MANIFEST.tsv` |
| `Pinned inputs` | §1 |
| `Resources` | §11. Cluster, GPU, training, toys, event loops, real `sbatch`: **0** |
| `Review` | §9 |
| `Model / effort` | Claude Opus 5.5 (`claude-opus-5-5`), Claude Code; effort not observable to the session |
| `Disposition` | §12 |
| `Next action` | §13 |

`Q` = `docs/orchestration/state/next-preparation-20261009`; `P` = `Q/sb1-prep`.

## 0. Setup

One owner (this session) and one fresh read-only reviewer, with one initial review and at most one
focused re-review. Terminal conditions: PASS, FAIL or INCONCLUSIVE as defined in the integration
prompt. Budget: 6 active hours, 3 local CPU core-hours, two compute threads per command, 8 GiB RAM and
3 GiB new scratch. Cluster, GPU and training: zero. Every local `sbatch`, `scancel`, `sacct` and
`squeue` was shadowed by a tripwire stub that records any call. It recorded **0** calls.

## 1. Inputs

`origin/main` was `a16d5786` at 2026-10-10T17:03Z, the base of all three branches, with no intervening
delta. Each remote head equals the one the prompt names. Each lane's report and preserved reviews were
read at that head.

| lane | head | last reviewed commit | delta after it |
|---|---|---|---|
| two-d-path | `2a28a13d49eee9b2b27a92ef805bfa1f9ef00907` | `0a2e0f41` (re-review PASS WITH CHANGES, N1/N2 MATERIAL) | `b38c909c`, `2a28a13d`: N1–N7 text, the N5 JSON field (`XR_stage_T.admitted_range` 63.2–292.9 → 15.3–227.8), the preserved re-review. Not re-reviewed |
| sb1-prep | `b7c951b301ee2142119d3db8fa4201e768f6bf42` | `1ac7cec3` (re-review PASS WITH CHANGES, finding 9 not resolved) | `4aa6ca79`, `df7c1536`, `b7c951b3`: the failed-`sbatch` fix (N1), the full-commit and two-value authorization rule (N2), the environment check moved into each batch script (N5), record text. Not re-reviewed |
| d-id | `7d173bd0bad495c4dcbb404ae769cab718fb928c` | admission ADMIT at `0e32c018`; numerical verification PASS at `d03a2c72` | `7d173bd0`: the verification record and the disposition |

Every file the three lanes changed is inside its own `Q/` subtree. Open PRs: #69 (two-d-path, draft),
#70 (sb1-prep, draft), #71 (d-id).

## 2. Assembly

Three `--no-ff` merges onto `a16d5786`: `930f1107` (two-d-path), `1867ca31` (sb1-prep) and `7184e436`
(d-id), with no textual conflict. Every lane file is blob-identical to its lane head in the merged tree,
and all three heads are ancestors of the integration head. `MANIFEST.tsv` is regenerated from source
once, after this session's files exist (§10).

## 3. two-d-path

### 3.1 Correction: different central values do not imply different nuisance deltas

The post-review §10 stage-T "Assurance" bullet said:

> Two different estimators cannot meet that null: their centrals already differ by median 0.136 σ_tot.

The sentence restates the rationale of the re-review's N1, which is preserved verbatim in
`two-d-path/review/review-cycle1.md` and is not edited. The inference is invalid. Take
x_u^X = x_u^L + c for every universe u and the CV, with c the same everywhere. The centrals then
differ by c, but every delta is equal:

δ_u^X = x_u^X − x_CV^X = x_u^L − x_CV^L = δ_u^L.

The 0.136 σ_tot central difference is therefore no evidence about the deltas in either direction.

The record now carries a dated correction at that bullet in `two-d-path/REPORT.md` §10, quoting the
original sentence. **The conclusions stand on other grounds:**

- **The transfer stays unmeasured.** No exact universe unfold has run, so no exact delta exists to
  compare.
- **Stage T's assurance stays unestablished.** Its false-fail rate and power under the
  decision-relevant null, "the widths transfer within tolerance", are not quantified. §3.6's
  cross-sweep scatter is LightGBM-to-LightGBM, not a between-estimator measurement.

No number moves.

### 3.2 Integrated disposition: a design, not an endpoint

- **L42's proposed 303–1,131 admitted node-h program is for narrowed claims.** It is not an accepted
  publication-ready endpoint.
  - Those claims (two-d-path §2) drop empirical total-interval coverage and a validated
    model-dependence bound, and replace the successor proposal's toy coverage of the total.
  - Accepting that narrowing is Joseph's decision, and he has not taken it.
  - The lane's own "PASS: L42" is the lane's verdict on its design question. It is **not** carried
    into any shared status surface.
- **Conditions that remain open in the L42 program:**
  - **Split-sample assurance.** The independence of random half-splits and the n_eff values are
    assumptions (§7, §13). The halves share bin mappers and row-count constraints (re-review N3). The
    SE formula is assumed.
  - **Half-to-full scaling.** It is assumed for both streams (§13).
  - **Model-bias treatment.** B± is a development envelope, reported beside `C_tot`, never inside it.
    There is **no untouched validation domain** (§7), and the model-dependence validation stage is
    NO-GO.
  - **Systematic reuse.** `purity_newomni` is chosen. Its 62 % Flux-universe background change is
    uninspected, and a frozen fallback exists (§3.5). The reproducible displacements of 6 bands and
    the non-reproducible variance of 36 bands (§3.6) have no established mechanism.
- **Synthetic seed-mechanism evidence is not independence.**
  - §3.3's LightGBM and sklearn runs are small synthetic checks of where the seed acts.
  - They are not a proof that `C_ML`, `C_S` and the universe deltas are independent or non-overlapping
    blocks on production inputs.
  - The two-d-path register proposal §11 item 3, which would annotate C's Audit 4 with "that mechanism
    gives no seed-noise overlap", is **not applied** for that reason (§7).
- **XR remains unrun.** XR is specified (≤ 6.4 node-h). Its X1 arm is a one-seed `P09b` that needs a
  specific ruling. Its N2 manifest repair is not re-reviewed.

**Arithmetic, re-run here.**
- `design_arith.py --self-test` PASS.
- `design_arith.py --write` reproduces `design_arith.json` byte for byte. Stage T is 15.3–227.8 and
  L42 complete 302.9–1,130.8 admitted node-h.
- The post-review stage-T range is 16 exact universe unfolds × 0.667 or 9.91 node-h × 1.15 / 0.8.

## 4. SB1 package

### 4.1 The three post-review changes, checked

| change | what was checked | result |
|---|---|---|
| failed `sbatch` cancels what was queued (c1 N1) | `submit()` returns non-zero on a failed or non-numeric reply. The assignment in the parent then fails, errexit runs the parent's ERR trap, and the trap cancels every id already set. The trap is not inherited by the `$(…)` subshell (no `set -E`), so it runs once | correct. The lane's control covers a failure at the 3rd call. **Repair (§4.2):** added the 1st and 6th calls and a non-numeric reply, whose `^[0-9]+$` check had no control |
| environment sourcing (c1 N5) | every batch script runs `sb1_check_env`, which refuses with exit 3 on a changed digest, and then sources the setup at top level. Receipts record the **submission-time** digest from `run.env`, not a fresh hash of the sourced file | **gap:** the lane's control changes the setup before H0, so H0 refuses and `afterok` cancels the rest. Removing the check from `sb1_unfold.sbatch` (UL and SL) left all 27 chain tests green. **Repair (§4.2)** |
| exact authorization binding (c1 N2) | `sb1_admit.check` requires a full 40-character `package_commit` that is an ancestor of HEAD; no difference under `P`, the executed modules or the guard between it and HEAD; and the authorization's text naming both the commit and the manifest's sha256. An abbreviated commit would otherwise pass, because it is a substring of the full id | correct, with controls (`test_an_abbreviated_package_commit_is_refused`, the commit-only and manifest-only subtests); the lane's mutants `authorization-needs-only-one-value` and `package-binding-unchecked` are caught |

### 4.2 Repairs (`62e55530`, tests and mutants only)

- `test_every_job_refuses_an_environment_changed_after_submission`: after a good submission the setup
  changes, and each of the six queued jobs is run directly. Each must exit 3 with "changed since
  submission" and leave its job directory empty.
- `test_a_failed_first_or_last_sbatch_or_a_non_numeric_id_stops_the_submission`: fail at call 1 (none
  queued) and at call 6 (five queued, all cancelled), and an `sbatch` that prints a non-numeric reply.
  Each must exit non-zero with no `submission.json`.
- Two mutants are added to `checks/mutation.py`: `unfold-env-unchecked` and
  `submit-accepts-non-numeric-id`. Measured before adding them: the first mutant failed the new
  environment test's UL and SL subtests, the second failed its non-numeric subtest, and the 27 existing
  chain tests passed under the first.
- No script, module, launch spec or manifest changed. `manifest/expected-code.json` is byte-identical
  to the lane's (sha256 `f060df81338b17069a31a0a2cc7a3430ed81c91ce64de6d6f3d54b80e08eb15a`).

### 4.3 Verification with fake Slurm only

Every `sbatch`, `scancel`, `sacct` and `squeue` resolved either to `tests/fake_slurm.py` or to a
tripwire stub, which recorded **0** calls. No real Slurm client exists on this machine (`which`: not
found).

| suite (`venv313`: Python 3.13.7, PyROOT 6.36.000, numpy 2.4.4) | merged tree `7184e436` | package pin `d4335d3b` tree | skips |
|---|---|---|---|
| `tests/test_branch_select.py` | 16 OK | 16 OK | 0 |
| `tests/test_sb1_guarded.py` | 10 OK | 10 OK | 0 |
| `tests/test_launch_chain.py` (the submit script and all six batch scripts against `fake_slurm.py`) | 27 OK | 29 OK | 0 |
| `tests/test_package_consistency.py` (also under conda Python 3.12) | 7 OK | 7 OK | 0 |

Mutation run 5 (`checks/mutation.py` at `62e55530`, `P/logs/mutation-results-run5-62e55530.json`):
the unmutated clone passed every targeted test (7 + 3 + 17, no skips), then **29 of 29** mutants were
caught. That is the lane's 27 plus the two added here.

**The pin.** The admission binds a launch to "the last commit that changes `P`". After §4.2 that commit
is `d4335d3b9bc2502002f93390f9555d07e134855f`, which records the repairs in SB1's §11 and redefines
the package commit in its §7.2. Nothing under `P`, the executed modules or the guard changes after it
on this branch: `git diff --name-only d4335d3b HEAD` over those paths is empty (§6).

### 4.4 Relevance, as Joseph stated it on 2026-10-09

SB1's own §10 and §16 say it matters "only if option (b) … or option (c)'s matched seed-1 sweep is to
be priced". Joseph's statement is broader: SB1's potential value includes pricing a prospective
matched LightGBM measurement procedure, not only a transfer campaign. Only its preparation was
dispatched, and the real cluster benchmark remains unauthorized. SB1's §10 and §16 are not rewritten.
The dispatch table (§8) carries his statement.

## 5. D-ID

- **Numbers preserved.** `outputs/` (`results.json`, `tables.npz`, the manifests and the run record)
  is byte-identical to the lane head. The calculation was not repeated. The 29 synthetic controls in
  `test_did.py` pass (0 skipped).
- **Interpretation against the verification.** The verification (`d-id/verification.md`) reproduced,
  with the reviewer's own code, the reductions and labels and all three pooled branch outcomes. It
  found C in J, EW and H2 with the exact eligible counts and shares, with and without W2. §11's
  outcome statements match it:
  - J 121 of 144 C-counted, 117 with finite widths;
  - the finite-width C shares are J 0.812, EW 0.696 and H2 0.333, so **H2 is uninformative**: its C
    rests on two acceptance-hole functionals of three;
  - the resolution-sensitive exclusions are 232 of 376 (J), 129 of 152 (EW) and 63 of 66 (H2).
- **Two narrative points go beyond the verification.** They are recorded here rather than edited into
  the lane's report:
  - "The GBDT's median residual equals exact binned and fine-grid IBU's at K = 5". The tabulated medians
    are close, not equal: GiBUU 9.5 / 8.3 / 8.6 %, q3 4.3 / 5.3 / 4.0 %. The fine-grid (T3) trajectories
    were not reproduced.
  - The "much of it removed by longer exact iteration" reading rests on last iterates of runs that do
    not converge at run level.

  Neither decides a branch.
- **Limits that travel with every D-ID statement:**
  - binned, signal-only, fixed detector response;
  - historical development truths, with no untouched departure;
  - resolution-sensitive functionals excluded from every branch;
  - H2 uninformative;
  - Fisher widths are local, binned and optimistic;
  - no interval validated;
  - no bearing on the 2D pairing;
  - a same-family reviewer.
- **The next decision is Joseph's alone** (gbdt §10.3): move the scalar-5D endpoint to identified
  functionals, or record the J-cell joint endpoint as a binned no-go. Branch C authorizes nothing.

## 6. Checks

All on the integrated tree, with one thread per command (two for none), a scratch `TMPDIR`, and the
Slurm tripwire on `PATH`.

| check | result | skips |
|---|---|---|
| SB1 suites (§4.3) | 16 / 10 / 29 / 7 OK; mutation 29 of 29 | 0 |
| D-ID `test_did.py` (pytest) | 29 passed | 0 |
| two-d-path `design_arith.py --self-test` / `--write` | PASS / byte-identical to `design_arith.json` | — |
| `n2` producer provenance (venv313) | 31 OK | 0 |
| `n2` harness | 22 OK | 0 |
| `test_coverage_fixed_truth.py` | 20 passed | 0 |
| OI-136 ratchets (both) | 17 OK | 0 |
| OI-136 inventory (`guard/inventory.py`) | AST 17, all listed; fail-open 16 `7aa29431…`; 0 unlisted; candidates 144 (unchanged: the new `.py` files carry no root literal) | — |
| `test_reported_cells.py` (venv313) | 18 passed | 0 |
| `test_final_rollup_full_refusal.py` | 3 passed | 0 |
| KI-84 `test_bootstrap_completeness_ki84.py` | 15 OK | 0 |
| `verify_hash_bindings.py` | ALL BINDINGS INTACT | — |
| `test_hash_bindings.py` | 33 passed | 0 |
| `control_plane_lint.py`; `live_doc_indexed.py --unrowed` | PASS; 0 unrowed | — |
| `generate_manifest.py --check --at-sha HEAD` after the one regeneration | OK (§10) | — |
| SB1 binding precondition: `git diff --name-only d4335d3b HEAD -- P <modules> <guard>` | empty | — |

Logs: [`logs/`](logs/) (redacted runner output).

No publication source changed (`git diff --stat a16d5786 -- docs/analysis-note docs/publication publication`
is empty), so no build or standalone merge is needed. No adopted product, production driver or helper
changed.

## 7. Shared records

**Applied:**
- **`KNOWN_ISSUES.md` 88.** One factual annotation:
  - the 2D design exists, and L42's 303–1,131 node-h program is for claims Joseph has not accepted;
  - its open conditions are listed, and its seed-mechanism evidence is labelled synthetic;
  - the transfer stays unmeasured, and stage T's assurance is unestablished;
  - nothing is authorized, re-quoted or adopted.

  The row stays OPEN.
- **`CATALOG.md`.** The three rows now describe their delivered state, replacing the stale "D-ID: not
  admitted". It also routes to this report, and adds the next-owned-reports table.
- **`MANIFEST-overrides.tsv`.** Three `MACHINE open` rows: this report, `two-d-followup` and `sb1-run`.

**Not applied:**
- two-d-path §11 items 1–6:
  - item 1 is applied only in the factual form above;
  - item 2, a new KI row, is a descriptive measurement for the 2D lane to file;
  - item 3 would promote synthetic evidence (§3.2);
  - items 4–6 annotate closed lanes' records with design conclusions;
- sb1-prep §13 items 2–4:
  - the speed KI row and the speed annotation are outside this batch's need;
  - the `n2/harness.py` refactor would broaden code scope;
- D-ID's results: no PASS label, branch outcome or narrowed endpoint enters a shared status surface.

**Follow-up routes kept, not repaired here:**
- **KI-90.** The identity patch for `compare_to_paper_fullcov.py` and
  `uq/plot_uncertainty_fig6_7_style.py` (structure REPORT §5), owned by the publication owner or
  Joseph.
- **OI-136.** The OI-136 owner must:
  - wire the ratchets into the hook;
  - replace `coverage_fixed_truth/sbatch_{fixed_truth_toys,equivalence,ki85_arms}.sh` with the
    guarded strict form before any admitted run;
  - re-measure the `.sh`, `MNV_REPO` and gate6 families.

  Route: integration REPORT §5 and §12.

## 8. Dispatch table for the next owned reports

| item | value |
|---|---|
| tested main pin | base `a16d578646936a0cc6eca41e3e0350e756ee0dca`, plus this branch at the reviewed head (§9). The post-merge `main` head is recorded in the merged PR's delivery comment. A next session starts from that head |
| SB1 package pin | `d4335d3b9bc2502002f93390f9555d07e134855f` |
| SB1 manifest digest | sha256 of `P/manifest/expected-code.json` = `f060df81338b17069a31a0a2cc7a3430ed81c91ce64de6d6f3d54b80e08eb15a` |
| SB1 authority | none yet. A run needs a committed `docs/orchestration/AUTHORIZATION-<date>-sb1.md` that names both values above in full (SB1 §7.2, §10). Cap 2.0 node-h; ceilings 1.699; no retries |
| `Q/two-d-followup/REPORT.md` | owner: the 2D methodology and XR owner. Writes only `Q/two-d-followup/`. May compare routes and specify XR. May not run XR, measure the transfer, re-quote, adopt, narrow the claims, or lift KI-85 without Joseph's separate rulings |
| `Q/sb1-run/REPORT.md` | owner: the SB1 execution owner. Writes only `Q/sb1-run/` plus the run's own `outroot`. Runs only under that authorization, from a fresh detached cluster worktree at its commit, and must not edit `P`, which would break the pin |
| shared records | `KNOWN_ISSUES.md`, `docs/OPEN_ITEMS.md`, `CATALOG.md`, `MANIFEST-overrides.tsv`, generated `MANIFEST.tsv` and the control plane stay with the integration owner. A next owner proposes text in its own report |
| open routes, not assigned to either owner | KI-90's two-consumer identity patch; the OI-136 launch restrictions (§7) |

## 9. Independent review

**Pending.** One fresh read-only reviewer on a fixed commit of this branch: one initial review of the combined integration and the post-review changes, then at most one focused re-review after a single repair batch.

## 10. Delivery

**Pending review.**
1. Refresh `origin/main` and inspect any intervening delta.
2. Merge this branch into canonical `main` through a PR, with a merge commit.
3. Record the resulting head in the PR's delivery comment.

No standalone-note merge is needed, because no publication source changed. Superseded PRs #69–#71 are
closed only after their heads are reachable from `main`, with a reference to the integration PR. No
force-push, and no deletion of evidence.

## 11. Resources

| item | measured (to the review freeze) | cap |
|---|---|---|
| active time | 2026-10-10T17:03Z → about 17:45Z | 6 h |
| local CPU | ≈ 0.55 core-h. SB1 mutation run 5: 1,013 s. SB1 suites, three passes: ≈ 120 s each. Manual mutants, three runs: ≈ 65 s each. Shared suites: ≈ 300 s. D-ID controls: 54 s. Ratchets: 2 × 60 s. Hash bindings, manifest and lint: ≈ 100 s. | 3 core-h |
| threads | one per command; at most two commands at once | 2 |
| peak RAM | ≈ 0.55 GB (D-ID controls) | 8 GiB |
| new scratch | < 0.5 GB (the mutation clones were removed per mutant) | 3 GiB |
| cluster / GPU / training / real Slurm calls | 0 / 0 / 0 / 0 | 0 |

## 12. Disposition

| decision | proposed (before review) | reason |
|---|---|---|
| the three records land without design completion being treated as admission | PASS, if review finds no material defect | every record is scoped in §3–§5, shared surfaces carry no PASS, adoption or narrowed-claim label, and no publication objective changed |
| two-d-path correction | PASS | invalid inference corrected with a dated note; conclusions unchanged; reviews verbatim |
| SB1 package ready, pinned and locally verified | PASS | three post-review changes checked; two missing controls added (29 of 29 mutants); pin `d4335d3b`, manifest `f060df81…`; fake Slurm only |
| D-ID numbers and limits preserved | PASS | outputs byte-identical; outcome matches the verification; two narrative overstatements recorded |
| publication-ready measurement | **NOT ACHIEVED** | nothing here is executed, adopted or ruled |

## 13. Next action

Each item below is Joseph's decision. None is launched here.
- **2D: whether to accept the narrowed claim scope.** XR needs ≤ 6.4 node-h and a specific ruling for
  its one-seed `P09b` arm. Stage T stays unready until its assurance is computed.
- **SB1: whether to authorize the run at the pin above.**
- **D-ID: the endpoint-scope decision of gbdt §10.3.**
- **Routes that stay open:** KI-90 and OI-136 (§7).
