# RECORD — the director's 2026-10-28 rulings, third batch

The close-items session proposed these dispositions. The director ruled them on 2026-10-28, after
#472, and this record applies them. It also uses the director's standing promotion list to keep
the promoted queue at `policy.json`'s `current_work_min` of 10 as items finish. Measured at
`ec36984bd`. It changes no science and runs no compute.

## Retired

| Item | Why it is moot |
|---|---|
| OI-11 | `KNOWN_ISSUES.md` row J36 is *"CLOSED 2026-09-23 with a measured bound (Joseph's choice)"*: per-playlist POT scaling is not implemented, and its shape effect is at most 0.15% (`VALIDATION_LEDGER.md:2264-2295`). The row duplicates a closed KI row. |
| OI-162 | `DECISION-20260830-joseph-accept-forward-only-rehearsal.md` takes the row's preferred option. The redeploy and re-freeze at `7ac0edec` were done at `3994b4c65`. |
| OI-173 | `DECISION-20260902-joseph-applies-oi173-cause4-m.md` (`6fe34a73b`) applies cause 4's M grade, and `SCOREBOARD-20260817-quarantine-seven-causes.md:78` is annotated. Disposing of "Reading B" was optional in the row and was not pursued. |
| OI-183 | **Subject to the paper rewrite lane's veto this round** (the director has told that lane). `66d357060` removed both phrases from the note. Neither *"records no analysis that has yet used it"* nor *"have so far avoided the problem"* appears in `docs/analysis-note/`. The Letter's only ATLAS mention (`paper_body.tex:14`) is the 24-observable Z+jets measurement, so the claim that `DECISION-20260901-joseph-oi187-upgrade-not-blocker.md:62` placed "in the Letter" is not in either document. |
| OI-44 | Objectless. `RECEIPT-20260818-p3f-hpss-to-cfs-migration.md` (at tag `evidence/prepublication-2026-08-20-0b329e8a`): *"`HPSS_DELETE_ISSUED` for 240/240 objects. The CFS copy is now the only copy."* No tape copy is left to hashverify. **The live question is `OI-131(a)`** (`WAITING-JOSEPH`): whether an irreplaceable subset of the CFS-only objects warrants a second copy. |
| OI-49 | Objectless, by the same receipt: "already protected on HPSS" no longer has an object to measure. **`OI-131(a)` stays live**, as for OI-44. |
| OI-152 | Done by #471 (`9236db44b`): the three habits and their checks are in `docs/LOCAL_CHECKOUTS_AND_STORAGE.md`, "Working beside other sessions". |
| OI-43 | **Folded into `OI-75`.** "Lift the cluster P4 hold" is the same standing no-run hold that `OI-75` asks Joseph to reconcile with the unrecorded standard-P4 Stage-3 run. `AUTHORIZATION-20260815-p4-stages456-on-pass.md` (at the evidence tag) led to stages 4-6 running at `fc97e7069`, but no record lifts the hold. That is now one question, carried by `OI-75`, whose row gains a pointer to OI-43. |

## Reassigned

| Item | Change |
|---|---|
| OI-50 | Owner `joseph`, `WAITING-JOSEPH`. `RECEIPT-20260820-oi50-hashverify.md` is PASS, 36/36 md5 OK, rc 0, and its line 7 says closing the item *"is a claim for Joseph"*. |
| OI-52 | Owner `joseph`, `WAITING-JOSEPH`. The row's premise (*"Only he can read Iris"*) is false: lanes read `/opt/nersc/pe/bin/iris`, and a committed reading exists (`state/measurement-scoping/iris-20261023.txt`, `315c0459a`). The director ruled it retired and placed it on Joseph's queue. Because a retired row has no queue, it is recorded here as Joseph's to confirm, and the row is kept. |

## Deferred

| Item | Trigger |
|---|---|
| OI-135 | The watcher swap for job `57266000` ran at `f3cb21cdf`, and that job is terminal (`FAILED=1`, measured on `login28` on 2026-10-28). `RULING-20260819-lanec-issue54-frozen-deployment.md:224` records *"OI-135 step (f)"* as inert until `profiles.json` and `waker-config.json` deploy. Reactivate on that deployment. |

## Promoted (the director's standing list)

| Item | Owner | Why now |
|---|---|---|
| OI-161 | close-items | first on the director's standing list; replaces OI-152 in the promoted queue |

## Dependency check

`git grep -E "OI-<n>([^0-9]|$)" -- KNOWN_ISSUES.md 'docs/known-issues/*' 'docs/**/DECISION-*'
'docs/**/RULING-*' 'docs/**/AUTHORIZATION-*' 'docs/**/OPERATIVE-*' 'docs/publication/**'`:

| Item | Hits | Read |
|---|---|---|
| OI-11, OI-44, OI-49, OI-52, OI-152, OI-162 | 0 | — |
| OI-173 | three Joseph decisions (2026-09-01, 2026-09-02 ×2) | they are the resolution the retirement cites |
| OI-183 | `DECISION-20260901-joseph-oi187-upgrade-not-blocker.md:62` | read above; the wording it names is gone |
| OI-135 | `KNOWN_ISSUES.md` row 53 (FIXED); `RULING-20260819-…:224` | the ruling's step (f) is why OI-135 is deferred, not retired |
| OI-43 | 0 | folded, with a pointer in OI-75 |

No row text is deleted. Each changed row gains a dated prefix that points here.
