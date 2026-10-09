# Dispatch packet — Session A: 2D engineering and estimator pairing

Prepared by E, the integration owner, on 2026-10-09 UTC. Paste this whole file as the session's goal.
It is a preparation task. It grants no compute and authorizes no experiment.

## Dispatch facts (measured by E; re-measure anything volatile)

- **Agreed base commit for A, B, C and D:** `f8e2bf8535a90d7ed1315530cff3b80860ef9f9c` on `prep/uncertainty-e-20261008`. It is the plan pin `ad2716d8`
  plus E's coordination commit (the plan, five `MANIFEST-overrides.tsv` rows, one `CATALOG.md` section,
  `P/e/integration.json`). No scientific source, product, receipt or governing record differs from the
  pin; `git diff --name-only ad2716d8 f8e2bf85` prints exactly those four paths.
- Remote `main` was checked once, at 2026-10-09T05:51:13Z, and equals the pin. Do not track moving
  `main` or rebase onto it. E reconciles any later upstream change at integration.
- The plan text after the divider is copied verbatim from `git show f8e2bf85:docs/orchestration/PLAN-20261008-uncertainty-investigation-preparation.md` (blob
  `fbbc0d65`). If the two ever disagree, the blob governs.
- E's baseline and ownership snapshot is `P/e/integration.json` at the base. `P` is `docs/orchestration/state/uncertainty-preparation-20261008/`.

## Setup

1. Measure free disk with `df -h` (45 GiB free at dispatch; a checkout is 0.4 GiB). Then:

       git -C /Users/josephbailey/local-research/MINERvA-OmniFold-uncertainty-planner-20261008 fetch origin
       git -C /Users/josephbailey/local-research/MINERvA-OmniFold-uncertainty-planner-20261008 worktree add -b prep/uncertainty-a-pairing-20261008 /Users/josephbailey/local-research/MINERvA-OmniFold-uncprep-a-20261008 f8e2bf8535a90d7ed1315530cff3b80860ef9f9c

   Work only in that worktree. Never edit the shared checkout `/Users/josephbailey/local-research/MINERvA-OmniFold/`.
2. Use a dedicated temporary directory and the thread cap:

       export TMPDIR=/private/tmp/minerva-uncprep-a-20261008/tmp && mkdir -p "$TMPDIR"
       export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4

   Copy any log you cite into `P/a/` before deleting only that directory.
3. Commit as `git -c user.name="uncprep lane A" -c user.email="uncprep-a@minerva-omnifold.invalid" commit ...`.
   Without it the commit takes the repository's unattributed fallback identity. Stage explicit paths
   only, never `-A`, `-u`, `.` or a directory, and read `git diff --cached --name-only` before each commit.
4. The pre-commit hook runs from the shared checkout's `.githooks`; all 13 of its checks pass at the
   base. E pre-registered every new `docs/orchestration/*.md` deliverable's overrides row and
   `CATALOG.md` entry, so do not edit `MANIFEST-overrides.tsv`, `MANIFEST.tsv` or `CATALOG.md`.
   `MANIFEST.tsv` is already out of date at the pin; leave it. A JSON file under `P/` that pairs
   `path`, `file` or `script` with `sha256` (or `<role>_path` with `<role>_sha256`) counts as a new
   receipt binding, and the hook refuses the changed inventory. Record digests in TSV or Markdown,
   or under unpaired keys as `P/e/integration.json` does. If a digest should be a verified receipt
   binding, raise it with E. Never edit `verify_hash_bindings.py`'s expected constants.
5. Deliver by pushing the branch: `git push -u origin prep/uncertainty-a-pairing-20261008`. Do not force push, open a PR
   or merge. E integrates.

## Ownership at dispatch

- You write only:
  - `docs/orchestration/ASSESSMENT-20261008-2d-estimator-pairing.md`
  - `P/a/pairings.tsv`, `P/a/verification.md`
  - conditionally, narrow edits to `2d-unfolding/unfold_2d_omnifold_unbinned.py`, `2d-unfolding/uq/analyze_uq.py`, `2d-unfolding/uq/analyze_universes.py`, `2d-unfolding/uq/rollup_vl170_adoption.sh` and `2d-unfolding/tests/test_bootstrap_completeness_ki84.py`, under the release rule below
- Do not edit the other lanes' surfaces in the writer table below; the publication follow-up's
  `docs/analysis-note/`, `publication/release/`, `docs/publication/corrections-20261008/` and
  `MANIFEST.tsv`; E's surfaces; or anything on the plan's "No owner edits" list.
- At dispatch no worktree had uncommitted edits to any A-E surface and no live unmerged branch
  touched one. Recheck your own paths before the first edit.

## Sequencing

- Start at once on reading evidence, building `pairings.tsv`, and the checks the goal names (inspect each test before running it).
- Hold edits to the five conditional 2D paths until `[uncprep-D] INVENTORY` is on `origin/prep/uncertainty-d-navigation-20261008`. Each path that inventory does not claim is then released without asking anyone. A path it does claim stays deferred: record the conflict under a `## For E` heading in `P/a/verification.md` and carry on with the rest.
- Push `[uncprep-A] CONTRACT`, the frozen estimator contract section of your assessment, as soon as the evidence supports it. B and C find it by that subject marker and build on it.
- D routes proposed reference corrections to you for a factual check. Answer in `P/a/verification.md`; D stays the writer of the reference.
- If you hand D one of at most two existing non-frozen source files for a structural edit, record the exact path and the base commit of the handoff in `P/a/verification.md`.

Lanes coordinate through pushed commits on their own branches, not messages. Read another lane's
work with `git fetch origin` and `git show origin/<branch>:<path>`. Commit subjects that start with
these markers are the handoffs: `[uncprep-D] INVENTORY`, `[uncprep-A] CONTRACT`,
`[uncprep-B] PROVISIONAL`, `[uncprep-C] PROVISIONAL`, and `[uncprep-<lane>] FREEZE` for a lane's final
delivery. E integrates only `FREEZE` commits or terminal missing-dependency records. Anything for E
goes under a `## For E` heading in your own `P/a/` record; the affected item stays deferred and you
continue with the rest.

## Session record

Owner/reviewer setup (CAMPAIGN-REVIEW-20260929 §1): you own this lane, and the single independent
review happens in E. Do not spawn reviewers or worker agents. Recommended starting point, advisory
under CAMPAIGN-REVIEW-20260929 §5: Opus 5.5 as the scientific owner. In your terminal report, record the actual
model and version, effort, full session id, base and output commits, and resources measured against
your budget row, in addition to everything the common contract's terminal report requires.

---

## Baseline and evidence corrections

Remote `main` initially matched the supplied `b612ee3ac9b517c56e1153223576b7c3f5dcd32a`. It advanced during planning to `dd0515feeb5fee51972bc124e4ef1d3a7d7ed0bf` (PR #56), then at the dispatch follow-up to **`ad2716d8b7ac826c5c06690a5b7459ef04fa701b`** (PR #57). The last delta changes only the editorial record and publication package manifest. Use this refreshed common planning baseline, subject to E's dispatch check. The intervening changes concern the article, figures, release, and publication records; none changes the preparation's governing scientific routes. The shared checkout's unrelated untracked files were left untouched. Planning used a detached sibling worktree at `dd0515fe`; the later delta was inspected without changing that worktree's HEAD.

At dispatch, E checks remote `main` once and inspects its delta from this pin. All four owners use one agreed commit. An unrelated delta need not restart planning; a relevant change requires a written input reconciliation before dependent work. Do not independently track moving `main` in each lane.

The following corrections are inputs to preparation, not new scientific findings:

- `KNOWN_ISSUES.md` 84, ledger `VL170`/`VL172`, and their receipts establish that completeness was repaired and the rebuilt statistical band adopted. `VL169` failed the superseded `VL162` band; it does not grade `VL170`.
- Issue 85 and `DECISION-RULE-20261006-ki85-bootstrap-diagnostic.md`, with `state/ki85-diag-20261006/ki85_result.json`, support bootstrap faithfulness on same-event pseudo-data only. The held-out-MC retest remains deferred and unregistered. Preparing its design does not lift that ruling.
- `DELIVERY-20261006-s5p-campaign-terminal.md` and `OPEN_ITEMS.md` OI-193 establish that s5p is terminal. It adds no reportable measurement uncertainty. Completed scalar and PET campaigns stay closed.
- The October 5 successor proposal predates those events. Its outstanding algebraic completeness repair and active-campaign descriptions need reconciliation. Its total-uncertainty proposal, numerical criteria, and conditional pilot are proposals, not inherited authority or automatically appropriate statistical-test criteria.
- The 2D status names the frozen production backend differently in different passages. The reference's bootstrap item 4 also gives ambiguous seed instructions. Resolve these against actual producers and artifacts; do not choose a label by majority vote among documents.
- `README.md` routes the explicit rooted-import ruling to `AUTHORIZATION-20260903-oi136-failopen-repair.md` §2. The insert must remain inside `main()` and the pinned OmniFold implementation must retain its digest. The issue-84 edit does not authorize changing that ruling or advancing Gate-2 pins.

## Common contract — paste with every goal

Answer the assigned decision and finish autonomously within the limits below. A demonstrated defect, missing dependency, or scientifically justified no-go is a completed preparation outcome. Do not require a favorable physics result. Read `AGENTS.md`, `docs/orchestration/CAMPAIGN-REVIEW-20260929.md`, `docs/CURRENT_WORK.md`, the relevant governing rows, `KNOWN_ISSUES.md`, both 2D status/reference files, the October 5 successor proposal, the s5p terminal delivery, `README.md`, `docs/POST_PUBLICATION_REORG_PLAN.md`, and `docs/LOCAL_CHECKOUTS_AND_STORAGE.md`. Follow their targeted routes; never ingest orchestration wholesale.

Use an isolated sibling worktree and scoped branch, preserving the shared checkout and every unrelated file. Record input commit, relevant artifact digests, environment, commands, exit codes, test skips, limitations, and final output commit. Session owners may make routine implementation and documentation choices, run the permitted local checks, and prepare scoped commits and a branch push for their assigned work without repeated confirmation when this goal is dispatched. Follow the repository's delivery skill, hooks, and applicable ownership rules. No force push, merge to `main`, publication tag, release, external message, or gate-owner repin is included. If a delivery operation is refused, retain a concrete diff and terminal record; do not bypass the guard or repeatedly request permission.

Permitted execution is source/dependency inspection, reads of existing evidence, local deterministic reductions and design arithmetic, synthetic regression fixtures without scientific training, and affected lint/tests. Existing remote metadata or small receipts may be read through available access; no allocation, login-node analysis workload, training, event-loop production, toy generation, ensemble, or deployment is allowed. Do not reuse an idle allocation or unused campaign budget. Tests must be inspected before execution so a test command cannot launch training or consume real validation samples.

Keep behavior fixes and structural changes in separate commits. Preserve frozen scripts, historical receipts, published product bytes, independent numerical implementations, source pins, and supported reproduction paths. Do not update an old receipt to match current code. A pin that no longer matches is an observed constraint with an owner, not an invitation to make the checker green. No manuscript/source edit under `docs/analysis-note/` is in scope; any later such work carries the separate three-build and standalone commit/push synchronization requirement.

One writer owns each surface. A owns scientific implementation; D owns navigation and bounded structural work; E owns integration and shared scientific-status routing. B and C own their designs. Reviewers are read-only. Record the actual owner/reviewer model and effort in the existing handoff; use a capable scientific owner and a fresh consequential-review context, without treating historical model preferences as mandates. A–D perform their own checks; the single independent review is in E. Do not spawn additional reviewers or worker agents.

If evidence or access is missing, make one targeted retrieval attempt through its canonical route and at most one retry for a diagnosed transient failure. Record the exact missing path/digest/operand, why it matters, the affected claim, the owner/decision needed, and the least costly way to resolve it. Complete unaffected work, then close the dependent item as UNRESOLVED/INCONCLUSIVE. Do not wait indefinitely, invent substitute evidence, or consume untouched samples to unblock a design. Missing PyROOT or an unavailable producer environment is a verification limitation; skipped tests never count as passes.

Every terminal report gives: decision; PASS/FAIL/INCONCLUSIVE or feasible/no-go disposition; evidence and reproducible commands; consequential unresolved items; actual resource use; fixed output commits; exact next decision and cost, if any; and what the outcome cannot authorize. No preparation PASS validates coverage, changes adoption, grants compute, changes publication scope, or reopens a terminal campaign.

## Dependency and ownership tables

E is the integration owner from dispatch, but conducts final integration only after A–D freeze. E's early role is baseline and ownership coordination, not a second scientific implementation lane.

**Dispatch checkpoint, added after the concurrency/file-volume check:** E starts first and inspects live session metadata, worktrees, uncommitted paths and branch deltas. Process/socket liveness does not establish exclusive ownership, and an isolated worktree does not prevent conflicting future merges. In the inspected snapshot, the publication follow-up owns `docs/analysis-note/` build/receipt checks, `publication/release/` preservation/reproduction work, associated publication records, and a `docs/orchestration/MANIFEST.tsv` change. Leave those surfaces with that owner; integrate generated retention metadata serially from its proper source after refreshing upstream, not by overwriting or blindly merging an old generated file. No live edits to A's proposed 2D scientific files were observed, but recheck at dispatch. A named session can change scope after this observation. No peer message or intervention is authorized by this read-only checkpoint.

Then D performs an **initial inventory of at most one active hour, charged to its existing six-hour budget**, before A or D edits shared scientific code. It supplies the immediate dependency map, supported-entrypoint list, protected/frozen paths, and exact proposed write ownership. A–C may read evidence and draft concurrently. At the checkpoint, release nonoverlapping scoped edits; an unresolved ownership conflict defers only the affected edits. D continues its remaining improvements alongside A–C. This is E → D's initial inventory → parallel A/B/C/D work → E's final integration, not a requirement to complete broad cleanup before scientific planning.

The measured baseline contains 1,144 `.py`, 475 `.sh`, and 818 `.md` tracked files. Concentrations include 399 Python and 159 shell files under `nd-unfolding/pet/`, and 476 Markdown files under `docs/orchestration/`. These counts demonstrate the scale of the navigation problem, not disposability. D must prioritize duplicated scientific decisions, unnecessary supported entrypoints, and misleading current routes; wholesale consolidation/removal still requires the dependency and authority evidence specified below. Re-measure rather than using these counts as a cleanup target.

| Session | Can start immediately | Dependency before freeze | Output used by |
|---|---|---|---|
| A | Producer/consumer and pairing audit; bounded fixes | D's measured caller inventory for any overlapping structural proposal | B estimator/sampling contract; C component matching; E |
| B | Independent-population inventory and provisional design | A's pinned estimator contract; C's relevant per-experiment cost inputs | C validation workload; E |
| C | Source inventory and timing evidence | A's pairings and B's experimental procedure/counts for final cost | B affordability check; E |
| D | Dependency inventory and navigation improvements | A's explicit file handoff before scientific shared-code edits | A caller constraints; E supported-workflow checks |
| E | Pin baseline; assign ownership | Fixed A–D commits or explicit terminal missing-dependency records | A specifically named next authorization request |

B and C exchange a provisional procedure/count/cost table once, then reconcile once after A freezes; neither waits for the other's final document before doing independent work. If agreement cannot be reached within budget, expose the differing assumptions and close the affected conclusion as not ready.

All paths below are repository-relative. `P` abbreviates `docs/orchestration/state/uncertainty-preparation-20261008/`; it holds compact preparation evidence, not scientific products or another dashboard.

| Writer | Exact owned deliverables and permitted existing surfaces |
|---|---|
| A | `docs/orchestration/ASSESSMENT-20261008-2d-estimator-pairing.md`; `P/a/pairings.tsv`, `P/a/verification.md`. Conditional narrow edits to `2d-unfolding/unfold_2d_omnifold_unbinned.py`, `uq/analyze_uq.py`, `uq/analyze_universes.py`, `uq/rollup_vl170_adoption.sh`, and `tests/test_bootstrap_completeness_ki84.py` (the remaining four paths are relative to `2d-unfolding/`). Hash-bound restrictions still apply. No wholesale rewrite or automatic product rerun. |
| B | `docs/orchestration/DESIGN-20261008-2d-independent-statistical-validation.md`; `P/b/populations.tsv`, `P/b/assurance.py`, `P/b/assurance.json`. Any exact additional operand fixture is listed in B's report. No edit to historical coverage code or preregistration. |
| C | `docs/orchestration/ASSESSMENT-20261008-2d-total-uncertainty-feasibility.md`; `P/c/components.tsv`, `P/c/costs.json`, `P/c/costs.py`. No covariance or production edits. |
| D | `README.md`, `2d-unfolding/2D_OMNIFOLD_REFERENCE.md`, `docs/POST_PUBLICATION_REORG_PLAN.md`; `P/d/dependencies.tsv`, `P/d/disposition.md`. D may also improve an existing workstream README after naming it in its disposition. At most two existing non-frozen source files may be structurally edited after exact ownership transfer from A; otherwise deliver a deferred patch design. |
| E | `docs/orchestration/PROPOSAL-20261005-scalar-measurement-successor.md`; final `docs/orchestration/DELIVERY-20261008-uncertainty-preparation.md`; `P/e/integration.json`, `P/e/review.md`, `P/e/recompute/`. E alone updates necessary `KNOWN_ISSUES.md` index entries, 2D STATUS/RUN_LOG, `docs/orchestration/CATALOG.md`, and required retention metadata. Scientific ledger additions only if a qualifying measured result actually needs one. |

No owner edits `AGENTS.md`, policy, existing OI rulings, frozen receipts, or queue state to create authority. `docs/CURRENT_WORK.md` is generated, not hand-edited. Findings needing a new governing record are supplied as concrete proposals to the current control-plane owner, not silently installed. E can incorporate scientific issue-index updates serially before final integration; this does not give it ownership of unrelated issues. D routes proposed reference corrections to A for factual checking, but D remains the writer. The fresh reviewer writes only external scratch and returns findings; E preserves the review and independently written recomputation with attribution and digests.

## Explicit preparation budgets

These are new preparation ceilings for the dispatched tasks, not transfers from historical compute grants. “Active hours” means cumulative working time across resumptions, excluding time while a session is closed. Review and repair are included. Stop scope expansion at 75% consumption and use the remainder for verification and terminal delivery.

| Session | Active working-time ceiling | Local CPU core-hours | Peak RAM | New scratch/output ceiling | Review/repair allowance |
|---|---:|---:|---:|---:|---|
| A | 6 h | 4 | 8 GiB | 2 GiB | Initial checks plus at most two focused repairs; reserve 1 core-h |
| B | 6 h | 2 | 4 GiB | 0.5 GiB | One provisional/final reconciliation; at most two E-requested repairs; reserve 0.5 core-h |
| C | 4 h | 1 | 4 GiB | 0.5 GiB | Same reconciliation/repair limit; reserve 0.25 core-h |
| D | 6 h | 3 | 8 GiB | 1 GiB | At most three implemented improvements, two source files, two repairs; reserve 0.75 core-h |
| E, including reviewer | 8 h | 4 | 8 GiB | 2 GiB | One initial fresh review plus at most two focused repair/review cycles; reserve 2 core-h for independent verification |
| Total | 30 h | 14 | 24 GiB aggregate concurrent cap | 6 GiB beyond checkout files | No automatic extensions |

All sessions: **zero cluster node-hours, zero GPU-hours, zero scientific training/toys**. Limit local execution to four threads per process and eight concurrent CPU threads across lanes; serialize checks if memory or disk capacity is insufficient. Measure available disk before creating worktrees; do not delete other sessions' files to make room. Avoid copying heavy ROOT inputs. Use a dedicated `TMPDIR` and preserve logs before cleaning only that task's disposable test scratch according to storage policy. At most one environment repair attempt, within budget; no platform rebuild to rescue a check. If a governing contract requires additional review, identify it and terminate as not ready rather than abbreviating it or silently expanding this budget.

## Paste-ready goal A — 2D engineering and estimator pairing

**Decision:** Determine whether each central-value/uncertainty pairing describes the same intended 2D estimator, and whether any allowed engineering repair is needed before designing a new statistical test. Do not presume seed-1 statistics and seed-42 systematics are compatible or incompatible.

**Inputs:** Common contract and pin; ledger `VL162`, `VL169`, `VL170`, `VL172` and the Active 2D Result; `state/ki84-rebuild-20261006/` and `state/ki84-adopt-20261006/`; issue-85 decision/result; actual driver, bootstrap scale-up launcher, full-universe and matched-CV launchers, seedscan producer/analyzer, `uq/analyze_uq.py`, `uq/analyze_universes.py`, and `uq/rollup_vl170_adoption.sh`. Follow each product to its exact producing revision and flags. Read the OI-136 ruling and hash bindings before editing. Use D's inventory, but independently inspect callers affected by a proposed driver change.

**Work:** Build `pairings.tsv` with one row per central/statistical/systematic/ML/combined/projection pairing. Record input digests, source commit, command, event population and identity keys, duplicate/miss/fake handling, bin edges and ordered row mask, flux/POT/target/bin-area normalization, completeness semantics, backend and hyperparameters, iteration/seed/thread settings, bootstrap streams and conditioning, covariance center/denominator, and consumer. Distinguish a historical filename, a launcher default, and evidence of the bytes actually executed. Inspect both producer imports and consumer imports; runtime-origin proof must use the executed module's path/digest or be marked unavailable. Static searches and mocked imports alone cannot prove a historical runtime origin.

Compare exact GBT, LightGBM, nominal seed, sweep CV, statistical mean, and quoted central only where artifacts justify the comparison. A small observed central difference is not proof of covariance transfer. A seed transfer requires a declared observable/tolerance and actual supporting evidence; otherwise mark PAIRING UNRESOLVED and price the missing comparison for C. Do not retrain to obtain it.

Verify the repaired completeness path and its regression coverage. Inspect and, where dependencies permit, run `2d-unfolding/tests/test_bootstrap_completeness_ki84.py`, including its pre-fix negative control; distinguish the expected old-code failures from new-code regressions. The test stubs the classifier, so it verifies extraction behavior, not scientific coverage. Inspect production rebuild operands separately. Check `nd-unfolding/tests/test_oi136_rooted_insert_ratchet.py` and relevant shared callers. Preserve the rooted insert inside `main()` and the digest of `unbinned_unfolding/python/omnifold.py`; do not repin Gate 2 or rewrite historical run records.

Implement only narrow, evidenced fixes within the owned paths and existing restrictions. A fix that changes the intended estimator or uncertainty model is a proposed patch/design with consequences and cost, not an adopted replacement. Keep behavior fixes separate from structural commits; let D own navigation. If no further code defect is found, an evidence-backed no-change conclusion is sufficient.

**Deliver/verify:** Compact assessment, complete pairing table, changed-path/caller list, reproducible checks with skips explicit, and a frozen estimator contract for B/C. Every required pairing is VERIFIED, DISPROVED, or UNRESOLVED with a consequence and exact missing operand. Independently check row ordering, units, and key covariance reductions where existing operands fit budget. State which comparisons remain unmeasured.

**Terminal:** PASS means all pairings required by the proposed next experiment are established and necessary engineering checks pass; FAIL means a pairing is disproved or a reproducible implementation defect remains; INCONCLUSIVE means necessary evidence/checks are missing. Report mixed row outcomes rather than collapsing them into a global scientific grade. Apply A's finite budget and missing-dependency rule. No outcome authorizes seed transfer without evidence, changing the frozen estimator, rerunning production, replacing a band, or lifting the held-out-test deferral.

## Final integration rubric

| Gate | Evidence required for readiness | Terminal consequence if unmet |
|---|---|---|
| Current authority and baseline | Common source pin; current governing restrictions; relevant upstream delta reconciled | NOT READY if a conflict affects the named step |
| Estimator identity | Actual producer/consumer evidence for backend, settings, seeds, imports, populations, normalization, bins and completeness | Disproved match: NOT READY; missing operands: NOT READY/INCONCLUSIVE |
| Engineering behavior | Completeness regression and negative control; affected shared callers; protected import/pin behavior; explicit skips | Essential missing check or regression blocks dependent step |
| Population independence | Disjoint event identities and roles; no preprocessing leakage; justified outer sampling law and MC-size equivalence | Missing independent populations: no-go for the claimed experiment |
| Procedure and claim | Explicit fixed-band versus reconstructed-interval choice; fixed truth; backgrounds/conditioning; per-experiment operations; finite-domain limitations | Ambiguous or circular design: NOT READY |
| Statistical assurance | Prospective tolerances, complete functional/case family, coverage and accuracy sizing, stopping/failure rules, independently checked arithmetic | Insufficient assurance: redesign request or INFEASIBLE at the resource ceiling |
| Feasibility | Complete procedure cost, measured/extrapolated split, storage/memory/concurrency, protected verification and retries | Unpriced essential work: NOT READY; demonstrated unaffordability: INFEASIBLE |
| Total-uncertainty boundary | C's explicit component dispositions, dependencies and missing model/response/dependence work | Statistical-only readiness remains labeled statistical-only |
| Supported workflow and preservation | D's four navigation tasks reproducible; relevant equivalence/link/hash checks; frozen paths/checks retained | Material supported-workflow regression: NOT READY |
| Independent review and delivery | Fixed reviewed refs, operands independently recomputed, material findings resolved within two repairs, durable scoped delivery | Residual material finding or unavailable review: NOT READY |

Preparation can autonomously finish with evidence audits, safe scoped engineering/navigation changes, proposed validation criteria, costed designs, and a reviewed no-go. Later Joseph decisions remain separate: lifting the held-out-test deferral, admitting a named experiment and its resources, changing scientific gates or the estimator/uncertainty model, publication adoption/scope, protected-path migration, historical-family removal, and any external release or communication. No favorable preparation label supplies those decisions.
