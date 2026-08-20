# MINERvA-OmniFold scientific front door

This is the shared orientation surface for Codex and Claude. It summarizes the current scientific
picture but is **not evidence or authorization**. Before quoting a result, changing code, launching
compute, or deciding a gate, open the routed canonical artifact and re-measure any volatile state.

## Objective and publication scope

This repository develops MINERvA ME-FHC inclusive charged-current cross sections with unbinned
OmniFold: the finalized 2D `(p_T, p_parallel)` reproduction of arXiv:2106.16210, a 3D
`E_avail` extension, scalar 4D/5D extensions through `q3` and `W`, and PET/FPS full-event studies.
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
| Historical 3D covariance and generator significances | `QUARANTINED` | No historical rank-247 block-sum covariance chi-square or significance is a publication number. | The quotable covariance must be projected from the final adopted, selection-complete 5D trunk. | 3D status, “covariance-gate override” |
| Scalar 4D/5D central values and closures | `VALIDATED` | The 4D and 5D central results pass their dimensional anchors and injected-variable closures. | This does not revive superseded unified covariance products or dependent significances. | `nd-unfolding/ND_OMNIFOLD_STATUS.md`; ledger |
| Corrected scalar 5D covariance | `VALIDATED` | The background-aware corrected 5D GBDT covariance is the current scalar-5D uncertainty product. | Adoption and provenance of later standard-P4/PET-derived candidates remain separate decisions; read the exact current item before use. | N-D status; `nd-unfolding/uq_5d/`; ledger |
| Historical unified 4D/FPS and PET uncertainty products | `QUARANTINED` | Old unified 4D/FPS covariances, old PET precision comparisons, `(E_avail,W)` covariance, and dependent significances are unquotable. | Corrected 5D and PET records supersede only the scopes they explicitly name; no replacement is implied for every historical component. | N-D status, “Quarantined historical results”; `KNOWN_ISSUES.md` |
| PET central/statistical pairing (`C_stat`) | `EXISTS — UNVERIFIED` | A 50-member `C_stat` artifact exists, but it is not independently verified and is not paired with a ratified central value. | The nominal lies outside its replica family over a decision-bearing region; construction is not scientific adoption. | `docs/orchestration/LIVE-STATE.md`; `docs/OPEN_ITEMS.md` `OI-126`; ledger `VL132` |
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

## Complete work that should not be repeated

- The 2D Phase-18.2 production, closure, completeness, iteration, model-comparison, and literature
  validation campaigns are complete. Reopen them only for new evidence or an explicit question.
- The 3D framework, central unfold, marginal anchor, injected-shape closure, and generator comparison
  are complete. The covariance override does not invalidate those components.
- Scalar 4D/5D central-value anchors and closures are complete. Current uncertainty and adoption gates
  are narrower than repeating those central campaigns.
- The 1D binned study is a closed equivalence/debug cross-check, not a publication result.

## Principal unresolved scientific question

The publication-limiting question is whether the PET estimator's nominal-versus-bootstrap displacement
represents an uncertainty that should be published as estimator instability, or shows that the current
bootstrap/central pairing is scientifically invalid and must be replaced. This is `OI-126`; engineering
defects and scheduler activity are subordinate unless they change the evidence available for that
decision.

## Next three scientific actions

1. Independently verify the existing `C_stat` ingredients and re-derive the nominal-versus-family
   containment and tail geometry, producing one `OI-126` decision packet without new training. Rebuild
   `OI-132`'s partition only if that packet relies on its divergence-coverage classification.
2. Resolve `OI-126` from that packet: ratify an honest central/statistical pairing or specify the
   replacement construction and the evidence it must supply.
3. Authorize new compute only if the named decision cannot be answered from existing products; bind
   any run to the unresolved quantity it measures and state what a terminal result cannot authorize.

## Decisions reserved for Joseph

- The `OI-126` scientific interpretation and resulting central/statistical pairing.
- Any publication adoption or replacement that changes the central estimator, uncertainty model, or
  claims in the note.
- Construction of `C_ML`, changed Gate-6 compute beyond existing authorization, and material resource
  commitments not already covered by a standing grant.

## Minimal integrity rules

- A scientific result is live only after its evidence and required ledger/RUN_LOG/STATUS records land
  in a commit. Uncommitted or merely relayed results are not quotable.
- Worker agreement is not independence. Trace agreeing statements to their first measurement and count
  shared origins once.
- Generated state is a view, not truth. Run its freshness check, then observe the governing source or
  scheduler before acting.
- Audit and review work is read-only. Use isolated worktrees, inspect status afterward, and never freeze
  an auditor's silent edit into a receipt.
- Do not delete, rename, or reorganize provenance-bearing material before an approved evidence epoch,
  a tested recovery path, and explicit authorization for the exact removal family.
- Domain-specific contracts live behind task routes. Do not reconstruct a pipeline from this summary.

## Evidence routes

| Task | Read next |
|---|---|
| What is happening now? | `docs/orchestration/LIVE-STATE.md`; run `python3 docs/orchestration/generate_live_state.py --check-freshness`, then query the scheduler/source directly |
| What should happen next? | `docs/CURRENT_WORK.md`, then the exact cited row in `docs/OPEN_ITEMS.md`; consult `docs/CURRENT_WORK_BACKLOG.md` when reprioritizing |
| Quote a number | `VALIDATION_LEDGER.md`, then its exact product summary or receipt |
| Assess a physics claim | `docs/orchestration/CLAIMS.md`, then the claim's original evidence and independent check |
| Change code | `KNOWN_ISSUES.md`, the relevant `*_STATUS.md` and reference, callers, tests, and hash bindings |
| Run 2D/3D/N-D/PET | The relevant workstream status; `2d-unfolding/2D_OMNIFOLD_REFERENCE.md`; for PET also `nd-unfolding/PET_UQ_REMEDIATION_STATUS.md` |
| Launch or monitor compute | Fresh live state, direct scheduler observation, the exact runbook/launcher receipt, and environment rules routed by the workstream reference |
| Apply process rules | `docs/orchestration/PLAYBOOK.md`; open `FINDINGS.md` only by routed `BEN-*` id |
| Understand history | The relevant append-only `*_RUN_LOG.md` or exact frozen evidence path; never load the orchestration directory wholesale |
| Build deliverables | `docs/analysis-note/`; `build_all.sh` must build note, primer, and paper |
