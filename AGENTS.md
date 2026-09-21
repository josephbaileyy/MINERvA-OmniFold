# MINERvA-OmniFold scientific front door

This is the shared orientation surface for Codex and Claude. It summarizes the current scientific
picture but is **not evidence or authorization**. Before quoting a result, changing code, launching
compute, or deciding a gate, open the routed canonical artifact and re-measure any volatile state.

## Objective and publication scope

This repository develops MINERvA ME-FHC inclusive charged-current cross sections with unbinned
OmniFold: the finalized 2D `(p_T, p_parallel)` reproduction of arXiv:2106.16210, a 3D
`E_avail` extension, scalar 4D/5D extensions through `q3` and `W`, and PET/FPS full-event studies.
**PET is diagnostic and method-development, not a publication uncertainty product** — ruled by Joseph
on 2026-08-20; it must read that way in note, primer *and* paper.
Publication completion requires a ratified central value and uncertainty construction, supported
reproduction paths, clean note/primer/paper builds, and no unresolved publication blocker.

## Scientific picture

The controlled states below apply to result components, not whole workstreams. A workstream may have
a validated central value and a quarantined covariance at the same time.

| Result component | State | Safe current statement | Decisive qualification | Evidence route |
|---|---|---|---|---|
| 2D central value and Phase-18.2 pipeline | `VALIDATED` | The 5-iteration MEFHC result is frozen at `3.073e-38 cm2/nucleon`, 1.11% above the paper total; closure, completeness, and iteration controls pass. | The paper+ours combined-covariance chi-square double-counts shared systematics and is not the standalone validation claim. | `2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md`; `VALIDATION_LEDGER.md` |
| 2D standalone uncertainty construction | `VALIDATED` | The MAT-conformant, flux-fixed 187-universe construction plus statistical and ML blocks gives a 6.87% median relative budget. | Quote only the committed matched-CV construction; predecessor covariance rollups are superseded. | 2D status; `2d-unfolding/2D_OMNIFOLD_REFERENCE.md`; ledger |
| 3D central value, marginal anchor, and closure | `VALIDATED` | The 3D `E_avail` result is complete; its marginal normalization recovers 2D and the injected-shape closure passes. | There is no published 3D reference; the anchor and closure validate the central result, not the old covariance-dependent significances. | `3d-unfolding/3D_OMNIFOLD_STATUS.md`; ledger |
| Historical 3D covariance and generator significances | `QUARANTINED` | No historical rank-247 block-sum covariance chi-square or significance is a publication number. | The quotable covariance must be projected from the adopted trunk `3d7465f6…` (row below), carrying that adoption's four measurements; no historical product is revived by its existence. | 3D status, “covariance-gate override” |
| Scalar 4D/5D central values and closures | `VALIDATED` | The 4D and 5D central results pass their dimensional anchors and injected-variable closures. | This does not revive superseded unified covariance products or dependent significances. | `nd-unfolding/ND_OMNIFOLD_STATUS.md`; ledger |
| **Adopted scalar-5D covariance (the publication trunk)** | `ADOPTED UNDER EXCEPTION` | One digest is adopted: `3d7465f6…` (`uq_5d/z_pilot_20260916_a5/z-cv.npz`, **890,500,272** B, `variant: "cv"`), Joseph 2026-09-20, as **publication-under-exception** under the executed, **byte-scoped** §6.4 amendment. Its `(E_avail,W)` projection `835828bf…` is built and its pairing verified by **digest identity**. | **FOUR MEASUREMENTS TRAVEL WITH IT AND ARE NOT CAVEATS** — read them at the adoption record §4 before quoting anything built from it; `M1` is `s_proj = 6.145%` against a `5%` bound, and `M3`'s *"lower bound"* wording is **WITHDRAWN**: the five seed-pinned bands are **unprobed in either direction**. The product's own fields stay `NON-PASSING` / `adoptable: false` and **do not become PASS labels because an adoption exists**. **Cause 3 is NOT discharged**: `M(i)` `UNRESOLVED` on `4c`, `C3` **predeclared and not computed** for this digest, and **no declared boundary was evaluated in production** (all seven `read_by_production: no`). Clause (c) is **disposed**, with the ordering defect **ratified, not cured**. The exception covers **these bytes and nothing else**. | `VALIDATION_LEDGER.md` `VL142`–`VL144`; `docs/orchestration/DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md`; `CORRECTION-20260920-lower-bound-inference-withdrawn.md`; `DECISION-20260920-joseph-rules-clause-c-disposition.md`; `OPERATIVE-SHEET-scalar5d.md` |
| Other corrected scalar 5D covariance candidates | `QUARANTINED` | Background-aware corrected block-sum and unified-throw candidates exist, and **none of them is a publication uncertainty product**. | Their ledger values remain measurements, not adoption. **Nothing here is inherited from the adopted digest above** — the §6.4 exception attaches to BYTES and explicitly excludes `361090f9…` and `7e4636a3…`, which are graded, recorded and **not** adopted. Mean-centering alone is disqualified and enforced in code: `project_cov_nd.py --expect-variant` is required with no default, and `--run-class publication` from `variant: "mean"` is refused — the mean-centered `z-mean.npz` measures `√tr` **7.13%** below the CV-centered product while being structurally identical to it. | `VALIDATION_LEDGER.md`, corrected 5D UQ quarantine; exact `nd-unfolding/uq_5d/` receipts |
| Historical unified 4D/FPS and PET uncertainty products | `QUARANTINED` | Old unified 4D/FPS covariances, old PET precision comparisons, `(E_avail,W)` covariance, and dependent significances are unquotable. | No full-event PET total covariance is adopted. The corrected recoil-only PET budget is a legacy representation cross-check and cannot satisfy or feed the full-event DAG. | `nd-unfolding/PET_UQ_REMEDIATION_STATUS.md`, “Legacy boundary”; `KNOWN_ISSUES.md` |
| PET central/statistical pairing (`C_stat`) | `EXISTS — UNVERIFIED, PAIRING DECLINED` | A 50-member partial covariance artifact exists; it is not independently verified, and `OI-126` was RULED on 2026-08-20 to decline the pairing and demote the result. | The ruling is a fourth move, not a choice among the three refuted branches. Reconsideration needs estimator-equivalence **plus coverage**, and coverage is a different object from verifying the construction. | `VALIDATION_LEDGER.md` `VL132`; `docs/OPEN_ITEMS.md` `OI-126`; its exact rulings |
| PET ML covariance / Gate 6 | `BLOCKED` | No `C_ML` is constructed and Gate 6 remains blocked. | Before any action read the exact `prohibitions_applied` keys in `docs/orchestration/state/gate6-member-trajectories-result-56847059.json`; do not paraphrase them. | Gate-6 receipt; N-D status |
| Standard-P4 and related adoption candidates | `EXISTS — UNVERIFIED` | Mechanical, code, or packet checks may pass without making a candidate adoptable. | A matching hash, successful construction, or worker agreement is not independent verification or adoption. | `docs/CURRENT_WORK.md`; exact governing `OI-*` record and receipt |

## Quarantined and superseded traps

- `OI-132` forbids quoting its historical divergence split until every member is reclassified with
  `bootstrap_seed` present. Do not reproduce the prohibited values in summaries.
- `C_stat` must never be shortened to “verified,” “adopted,” or “the statistical uncertainty.” Its
  existence, digest, and ledger row do not supply the missing independent check or central pairing.
- Gate 6 is controlled by five exact receipt keys. Route to the receipt rather than translating them.
- Legacy pre-MINOS-fix 1D outputs, pre-Phase-18 2D outputs, and superseded covariance families remain
  diagnostic or historical only.
- `OI-126`'s ruling does **not** invalidate the row's measurements. **CORRECTED 2026-08-20: the two
  sentences that stood here were false, and their falsehood was a DROPPED QUALIFIER, not a typo.**
  Joseph's ruling text, quoted verbatim at `docs/OPEN_ITEMS.md` `OI-126`, **does** contain the phrase
  *"a large, spatially coherent bootstrap-centering/bias anomaly whose coverage has not been
  validated"* — so it is his, it **is** part of the ruling, and a session told otherwise will
  wrongly "correct" a faithful quotation. What may not be quoted as his is that phrase **as a
  determined cause**: the row's own measured history refutes both mechanisms this campaign named, so
  the MECHANISM is not established even though the WORDS are Joseph's. Read the operative content as
  *a large, spatially coherent anomaly whose coverage has not been validated*, and never cite
  "bootstrap-centering" as a settled mechanism. `live-state.json`'s blocker kept the
  "as a determined cause" qualifier; this front door had dropped it, which is how a true caution
  became a false claim about what Joseph said.
- `OI-136`: a `.py` file that puts the hardcoded cluster root at `sys.path[0]` imports another
  checkout's modules while deployment parity truthfully reports every pinned file `CURRENT`. This
  cost 3 h 08 m of A100 on `57266000_0`. `PYTHONPATH` cannot outrank position 0 and a re-deploy does
  not fix it. The fail-open set was 59, then 45; **36 were repaired under
  `AUTHORIZATION-20260903-oi136-failopen-repair.md` and 9 remain** (three probe records, the
  published 2D arm, five receipt-bound files) — re-measure with
  `docs/orchestration/state/probe-oi136-sys-path-hijack-20260826.py`, never quote a count from here.
  Route new compute through `nd-unfolding/mnv_guarded_run.py`.

## Complete work that should not be repeated

- The 2D Phase-18.2 production, closure, completeness, iteration, model-comparison, and literature
  validation campaigns are complete. Reopen them only for new evidence or an explicit question.
- The 3D framework, central unfold, marginal anchor, injected-shape closure, and generator comparison
  are complete. The covariance override does not invalidate those components.
- Scalar 4D/5D central-value anchors and closures are complete. Current uncertainty and adoption gates
  are narrower than repeating those central campaigns.
- The 1D binned study is a closed equivalence/debug cross-check, not a publication result; recover
  its complete workspace at `evidence/prepublication-2026-08-20-0b329e8a:2d-unfolding/binned_study/`.

## Principal unresolved scientific question

**`OI-126` is no longer it — Joseph ruled it on 2026-08-20 and it has left the routed queue.** The
P5A nominal does lie outside its own bootstrap family, spatially organized, and those measurements
stand; what the ruling settles is that the pairing is declined and PET is demoted rather than any
branch being chosen. Do not reopen it, and do not restart the completed containment, tail-geometry,
target-factor, extraction, or occupancy probes.

**Nor is it the ADOPTION of a scalar-5D covariance: Joseph adopted `3d7465f6…` on 2026-09-20 as
publication-under-exception, and the `(E_avail,W)` projection built from it is verified.** It is now
**the estimator-seed sensitivity of that trunk, which exceeds its own declared limit** —
`s_proj = 6.145%` against a `5%` bound fixed before production, flat in `N`, so a property of the
estimator and not of the ensemble's resolution. **That is why no generator significance is quoted.**
⚠ It is **not** a licence to re-open the declined member campaign, the completed central-value
studies, or PET (2026-09-19 §7 stopping rule), and it is **not** bounded below — the *"lower bound"*
reading was **withdrawn 2026-09-20**. Read the routed `OI-*` end-state and
`OPERATIVE-SHEET-scalar5d.md`, never an older paragraph or a generated summary.

## Next-action discipline

There is no standing authorization here for a new scientific analysis. Read `docs/CURRENT_WORK.md`
for the exact authorized action and terminal-event posture, then the governing `OI-*` record;
`LIVE-STATE.md` is a measurement and route-health view and carries no authored action. In particular:

1. Do not repeat the completed `OI-126` containment, tail-geometry, target-factor, extraction, or
   signal-MC occupancy probes; their surviving conclusions and retractions are already recorded.
2. Treat independent verification of the existing `C_stat` construction as distinct from scientific
   adoption or pairing, and perform it only under the exact current authorization.
3. Launch new compute only after Joseph authorizes the named decision and the run states both the
   quantity it measures and what a terminal result cannot authorize.

## Decisions reserved for Joseph

- The `OI-126` scientific interpretation and resulting central/statistical pairing.
- Any publication adoption or replacement that changes the central estimator, uncertainty model, or
  claims in the note.
- Construction of `C_ML`, changed Gate-6 compute beyond existing authorization, and material resource
  commitments not already covered by a standing grant.

## Minimal integrity rules

- This front door and generated state are views, never evidence or authorization.
- A result is live only after its evidence and required ledger/RUN_LOG/STATUS records land
  in a commit. Uncommitted or merely relayed results are not quotable.
- Worker agreement is not independence. Trace agreeing statements to their first measurement and count
  shared origins once.
- Generated state is a view, not truth. Run its freshness check, then observe the governing source or
  scheduler before acting.
- Audit and review work is read-only. Use isolated worktrees, inspect status afterward, and never freeze
  an auditor's silent edit into a receipt.
- Pre-freeze provenance may leave `main` only through the pushed evidence tag, tested recovery, an
  exact removal-family authorization, and a surviving discovery route.
- Domain-specific contracts live behind task routes. Do not reconstruct a pipeline from this summary.

## Evidence routes

| Task | Read next |
|---|---|
| What is happening now? | `docs/orchestration/LIVE-STATE.md` (measurements and route health only; the authorized action lives in `docs/CURRENT_WORK.md`); on Perlmutter run `/usr/bin/python3.11 docs/orchestration/generate_live_state.py --check-freshness` from canonical main (task worktrees do not inherit main's regenerated view), then query the scheduler/source directly |
| What should happen next? | `docs/CURRENT_WORK.md`, then the exact cited row in `docs/OPEN_ITEMS.md`; consult `docs/CURRENT_WORK_BACKLOG.md` when reprioritizing |
| Quote a number | `VALIDATION_LEDGER.md`, then its exact product summary or receipt |
| Assess a physics claim | `docs/orchestration/CLAIMS.md`, then the claim's original evidence and independent check |
| Change code | `KNOWN_ISSUES.md`, the relevant `*_STATUS.md` and reference, callers, tests, and hash bindings |
| Run 2D/3D/N-D/PET | The relevant workstream status; `2d-unfolding/2D_OMNIFOLD_REFERENCE.md`; for PET also `nd-unfolding/PET_UQ_REMEDIATION_STATUS.md` |
| Launch or monitor compute | Fresh live state, direct scheduler observation, the exact runbook/launcher receipt, and environment rules routed by the workstream reference |
| Apply process rules | `docs/orchestration/PLAYBOOK.md`; open `FINDINGS.md` only by routed `BEN-*` id |
| Understand or recover pre-freeze history | `evidence/prepublication-2026-08-20-0b329e8a`, then the old path; never load the orchestration directory wholesale |
| Build deliverables | `docs/analysis-note/`; `build_all.sh` must build note, primer, and paper; then synchronize, build, commit, and push the standalone `MINERvA-OmniFold-Analysis-Note` repository |

## Deliverable synchronization

A change under `docs/analysis-note/` is incomplete until the corresponding source files are also
committed and pushed to the standalone `MINERvA-OmniFold-Analysis-Note` repository. Build and verify
the standalone checkout before declaring the note work complete, and record both remote heads.
