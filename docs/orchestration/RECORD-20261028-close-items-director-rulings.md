# RECORD — the director's 2026-10-28 rulings, second batch

The close-items session proposed these dispositions, and the director (paper-tighten lane, session
`8d862e`) ruled them on 2026-10-28. This record applies the rulings. It follows
`RECORD-20261028-close-items-infra-dispositions.md`, and it is separate because these five rulings
take the promoted queue below `policy.json`'s `current_work_min`, so they land together with the
promotions that restore it. The same change applies the director's rulings on the six publication
rows of the backlog triage (OI-6, OI-30, OI-59, OI-137, OI-172, OI-184). It changes no science, runs no compute and edits no launcher.

Measured at `9a18ddda4` unless stated.

## OI-93 — retired

**Next action in the register:** *"Require every truncated C_stat consumer to declare effective
rank, ensemble size, precision-bias treatment, and the PPP diagnostic."*

**Why it is moot.** The row's own re-triage of 2026-08-20, after the `OI-126` ruling, says there is
no publication consumer that inverts a truncated `C_stat`. `VL132` is unpaired, and no PET total
covariance is adopted (`AGENTS.md`, rows "PET central/statistical pairing" and "Historical unified
4D/FPS and PET uncertainty products"). The part that is generic to any finite-ensemble covariance
inverted in a truncated subspace was refiled as **`OI-137`**. That row stays active and carries the
hazard. Joseph's Ruling 7 (`DECISION-20260822-joseph-b1-lift-and-clause-c.md:186-200`) scopes it.

**Dependency.** `DECISION-20260822-joseph-b1-lift-and-clause-c.md:232` points to *"the corrected
OI-93/OI-137 record"*. That pointer still resolves: retiring keeps OI-93's text in
`docs/OPEN_ITEMS.md`, with a dated prefix.

## OI-123 — deferred

**Next action in the register:** *"Choose frozen per-leg checkouts or re-issue the affected
launchers with their owning receipts before the next run."*

**State.** The hazard is still in the tree. Three launchers pin `step1_increment_trajectory.py` at
`48f8353d…`, while the repository copy is now `ca2128ac…`:

- `nd-unfolding/pet/sbatch_gate6_member_trajectory_array.sh:66`
- `nd-unfolding/pet/sbatch_pet_fullevent_floor_replicate_array.sh:116`
- `nd-unfolding/pet/sbatch_pet_fullevent_legx_2x2_array.sh:177`

It **fails closed**: the pin check is a `die … 3` at task start, before any GPU work, so a run from
a current checkout stops at **exit 3** with `code hash mismatch: step1_increment_trajectory.py` and
costs nothing. No Gate-6 or PET run is authorized (`AGENTS.md`: Gate 6 `BLOCKED`, PET diagnostic).

**Trigger.** Reactivate on the next authorization of a Gate-6 or PET run, or on any edit to those
three launchers. Five decisions of 2026-08-22 to 2026-09-01 cite this row as the route for
superseding a pin. Deferral keeps the row, so those citations still resolve.

## OI-125 — deferred behind OI-71

**Next action in the register:** *"Record the end-of-run fold-forward scalar, not the neighbouring
consumption-time reduction, and bind the like-for-like result."*

**State.** `AUTHORIZATION-20260815-foldforward-closure-run.md:58` names the item that run closes as
*"`OI-71` (G4) and `OI-125`"*. `OI-71` is `WAITING-JOSEPH`: *"Decide whether recovery evidence may be
quoted without a measurement at the promoted configuration."* PET is diagnostic. The fold-forward
scalar is printed neither in the posted note nor in the PET note. Searched `docs/analysis-note/*.tex`
for `fold.?forward`, `0.7367`, `1.0114` and `1.0108`, and the only hits are two receipt paths in the
never-posted `records_results_index.tex`.
Search: fold.?forward; 0.7367; 1.0114; 1.0108 in docs/analysis-note/*.tex @ 9a18ddda4

**Trigger.** Reactivate when `OI-71` is ruled. If that ruling makes the recovery evidence quotable,
this row's like-for-like scalar is needed. Otherwise it can be retired.

## OI-17 — retired (unassigned backlog)

**Next action:** *"Choose between rethrowing slabs 31 through 39 and labeling the replacement as a
122-throw product."*

**Why it is moot.** The rethrow happened. `VALIDATION_LEDGER.md` (the provenance paragraph at about
`:1211`) records that regeneration `56427580` (array tasks 30–39, all `COMPLETED 0:0`) restored the 38
lost throws to **160/160**. It also records that the corrected ROOT
`nd-unfolding/uq_5d/unified_throw_cov_5d_fluxfix_20260806_full160.root` carries `n_throws = 160`,
read back from the file. Nothing here changes that product's quarantine status (`AGENTS.md`, "Other
corrected scalar 5D covariance candidates").

## OI-18 — retired (unassigned backlog)

**Next action:** *"Rebuild the Eavail-W covariance with per-universe flux normalization."*

**Why it is moot.** `KNOWN_ISSUES.md` row 36 is **RESOLVED 2026-09-23**. The flux fix is in code
(`nd-unfolding/eavailW_covariance.py:161-174,317`, guarded by `tests/test_flux_universe_fix.py`).
The publication `(E_avail,W)` covariance is the projection `VL143` (`835828bf…`) of the adopted 5D
product. KNOWN_ISSUES cites this subject by its own row number, not as `OI-18`, so row 36 was read
directly. It is resolved, and nothing open depends on it.

## Promotions to restore the floor

The five rulings above take three promoted rows out of the queue (OI-93, OI-123, OI-125), leaving
7 against `current_work_min` = 10. The director picked OI-181, OI-152 and OI-160 for promotion, with
the close-items session as owner. OI-160 is classification only, never deletion. OI-6 and OI-172
are promoted too, because their rulings give them next actions. The queue ends at 11.

## OI-181 — retired instead of promoted

The director picked OI-181 for promotion. On checking it before writing its row, I found it moot,
so it is retired here and the director was told. Its next action asks that `live-state.json`'s
`current_dag_node` either decompose into verifiable fields or be marked UNVERIFIABLE. The field no
longer exists. It was removed at `8f8149ad1` (2026-09-03, "define live-state measurement schema"),
and `generate_live_state.py:45-47` lists it among `LEGACY_PROSE_FIELDS`, which the loader refuses
(`:134-138`: *"legacy authored operational prose is forbidden"*). The live config's keys are now
`schema_version`, `measurement_ttl_seconds`, `route_registry`, `evidence_routes`, `jobs` and `wake`.
Dependency check: 0 hits.

## OI-6 — kept, narrowed, owner the paper rewrite lane

2D is done. `DECISION-20261024-joseph-adopt-re2-2d-refined.md` item 1 adopts `E_R` and `Q_R`, and
`app_negweight.tex:126` records the 2D revisit as carried out. The same sentence says that for the
configuration-(a) five-dimensional central value, *"which still uses purity, the revisit is open"*.
The row is narrowed to that. Retiring it needs a note edit, so the trigger is the note no longer
reporting (a), or recording the (a) revisit as carried out.

## OI-30, OI-59, OI-137 — kept, owner Joseph

- **OI-30:** which `E_avail` truth definition the analysis adopts (the row: *"NOTHING ADOPTED —
  Joseph's call"*). The materiality projection is analysis work for a measurement owner.
- **OI-59:** whether the freeze permits the Ascencio super-grid recompute (the row: *"Joseph's call
  whether the freeze permits it"*). The disclosure is already in `CLAIMS-20261005-claim-to-evidence.md`.
- **OI-137:** Joseph's Ruling 7 (`DECISION-20260822-joseph-b1-lift-and-clause-c.md:186-200`)
  assigns the rest to *"the scalar-5D adoption/statistics owner"*. No session holds that role, so
  the row waits on Joseph to designate one. **It must not go to the measurement lane or the PET
  C_stat lane** (the ruling's own words).

These three stay in the backlog with queue `WAITING-JOSEPH`. They are not promoted.

## OI-172 — kept, owner the paper rewrite lane

The row's question was answered by `DECISION-20260901-joseph-oi172-oi173-magnitude-legs.md`
ruling 1: *"MATERIAL ENOUGH TO NEED ITS OWN STATEMENT IN THE NOTE"*. The wording and placement were
left to drafting. The open act is drafting that statement, after the paper lane's n4 and r21 work.
I did not find the statement by `git grep` over `docs/analysis-note/*.tex` for `cause 1`, `per-band
ratio` and `oi172`. That is not proof it is absent, so the owner should read the note first.
Search: cause.?1; per-band ratio; oi172; oi-172 in docs/analysis-note/*.tex (one hit, `paper_body.tex:75`, where `cause.?1` matches "because 10") @ fb4cd395b

## OI-184 — retired

- (b) is settled: `docs/publication/LITERATURE-20261005-comparison.md:27` verified the arXiv
  abstract of `2504.06857` verbatim (*"mock data study"*, simulation only), and
  `docs/analysis-note/sec_intro.tex:18` calls it *"a mock-data unfolding"*.
- (a): the sentence that read as an exhaustive survey was rewritten at `66d357060`.

The paper lane may veto, if it wants the six uncited measurements cited.

## Dependency check

`git grep -E "OI-<n>([^0-9]|$)" -- KNOWN_ISSUES.md 'docs/known-issues/*' 'docs/**/DECISION-*'
'docs/**/RULING-*' 'docs/**/AUTHORIZATION-*' 'docs/**/OPERATIVE-*' 'docs/publication/**'`:

| Item | Hits | Read |
|---|---|---|
| OI-93 | `DECISION-20260822-joseph-b1-lift-and-clause-c.md:232` | a pointer to the row's text, which is kept |
| OI-123 | five decisions, 2026-08-22 to 2026-09-01 | cite it as the pin-supersession route; the row is kept (deferred) |
| OI-125 | `AUTHORIZATION-20260815-foldforward-closure-run.md:58`; `DECISION-20260815-joseph-oi6-oi8-oi126.md:262` | the first ties it to OI-71 (hence the trigger); the second says it is *"untouched by any of this"* |
| OI-17 | 0 | — |
| OI-18 | 0 by id; `KNOWN_ISSUES.md` row 36 by subject | row 36 is resolved |
| OI-181 | 0 | — |
| OI-184 | 0 | — |
| OI-152 | 0 | — |
| OI-160 | `RULING-20260902-quoted-column-permanence-is-p-scoped.md:601` | an inventory of ids in use, not a dependency |
