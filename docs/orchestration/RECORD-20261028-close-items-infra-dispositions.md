# RECORD — close-items dispositions and the director's rulings (2026-10-28)

The close-items session wrote this record under the director's routing of 2026-10-28. The director
routed nine items whose owning lanes no session runs any more. This record disposes of the four
whose state can be settled from the repository: two are retired, and two are deferred to a named
trigger. It also retires four unassigned tooling items from the backlog triage (OI-1, OI-96,
OI-150, OI-186), whose next actions are already done. It changes no science, runs no compute and edits no execution-surface file.

The other five were not disposed of by this session alone. OI-73 and OI-123 are cited by later
decisions of Joseph's (see "Dependency check"), and OI-93, OI-125 and OI-130 touch publication. All
five went to the director as proposals. The director's rulings of 2026-10-28 on OI-73 and OI-130 are
recorded below. The rulings on OI-93, OI-123 and OI-125 land in a later change, because they reduce
the promoted queue below the policy floor (`policy.json` `current_work_min`) and the director must
first choose rows to promote.

The same change promotes OI-136, on the director's ruling, to keep the promoted queue at the
floor of 10 rows.

Measured at `origin/main` `fce1f5d95` unless stated.

## OI-70 — retired

**Next action in the register:** *"Fix manifest tracking semantics so ignored and merely intended
paths cannot masquerade as committed repository inventory."*

**Why it is moot.** Every defect the row files is discharged by a named commit:

| Defect the row files | Discharged by | Measured now |
|---|---|---|
| The generator walked the filesystem, so ignored `__pycache__`/`.pyc`/`.DS_Store` rows entered the committed manifest | `3d518f271` (2026-08-18): the inventory is `git ls-files` plus `--others --exclude-standard` | 0 cache rows in `MANIFEST.tsv` |
| An untracked file was indistinguishable from a committed one | `3d518f271`: `tracking` is column 2 | every row reads `tracked` |
| A default run on a shared checkout let foreign untracked paths into the table and its counts | `18e942ee5` (2026-08-20): `--committed-only`; `--at-sha REV` reads every byte from one commit | CI runs `--check --at-sha HEAD` |
| Three rows named a successor document called `None` | `18e942ee5` | 0 `None` cells |
| A document landing without an overrides row is born `ARCHIVAL` and no check sees it | `1fc239448` (2026-09-23) classified the 106 row-less documents, and `live_doc_indexed.py --unrowed` became a hard pre-commit and CI check | `--unrowed`: 0 row-less documents |

What remains, stated so the retirement is not over-read: `--unrowed` makes a declaration
mandatory, not correct, so a document declared `ARCHIVAL` that should be `LIVE` still passes. That is
the author's judgement, and `live_doc_indexed.py` says so in its header. The citation counts that
foreign untracked files could move are, as of the manifest change routed with this item
(`infra/manifest-derived-on-demand-20261028`), no longer committed at all.

## OI-127 — retired

**Next action in the register:** *"Make unresolved role-keyed hashes visible as a separate cell in
integrity-check accounting."*

**Why it is moot.** Done at `18e942ee5`. That was tier (1) of the row's own three-tier answer:
printed, not gated, with `collect()` not widened, so no past `ALL BINDINGS INTACT` was
reclassified. `verify_hash_bindings.py` prints the cell on every run. Measured now:

    32618 receipt hash keys are UNPAIRED across 2657 receipts
    111 of those, across 63 receipts, carry a role name that denotes repo CODE

The row's other tiers were never this action. Tier (3), rewriting the existing receipts, is
forbidden by the row itself. Tier (2), a sibling path key on *new* receipts with a lint, is a
forward convention that no lane took up. It is recorded here as not adopted, not as a defect.
Re-raise it as a new item if role-keyed pins start to matter for a gate. The row's one-line side
finding (a code comment pointing at a nonexistent `OI-66`) is gone: `verify_hash_bindings.py` no
longer mentions `OI-66`.
Search: OI-66 in docs/orchestration/verify_hash_bindings.py (0 hits); rows starting `| OI-66 ` in docs/OPEN_ITEMS.md (0) @ 9a18ddda4

## OI-128 — deferred

**Next action in the register:** *"Put the adopter on the protected execution surface and move the
gate-name constant to the shared protected module."*

**State.** The second half is done at `18e942ee5`: `BAND_COMPLETENESS_GATE` lives in
`nd-unfolding/p4_lib.py:700`, which is on the standard-P4 execution surface, and
`p4_adopt_standard.py:21` imports it. The first half was declined there with its cost measured:
`STANDARD_P4_ENTRYPOINTS` (`p4_lib.py:946`) lists what the driver invokes, and the adopter is never
invoked (it prints "would promote"). Adding it would make that list's comment false. The row's own
next action is conditional: *"once adoption is wired"*. Adoption is not wired, and standard-P4
adoption has no authorization (`AGENTS.md`, "Standard-P4 and related adoption candidates",
`EXISTS — UNVERIFIED`).

**Trigger.** Reactivate when `p4_adopt_standard.py` is invoked by any driver or launcher, or when a
standard-P4 adoption is authorized. At that point also check the residual the row names and no one
has examined: whether `require_band_set_completeness` is itself sound, not only that it ran.

## OI-129 — deferred

**Next action in the register:** *"Digest the projected covariance and read back the closed-file
row-index object before recording its digest."*

**State.** Not done, and correctly so. The two-line fix is in `nd-unfolding/p4_project_4d.py`, which is on
the standard-P4 execution surface. Rule 4b invalidates the repair-11 verdict on any in-scope edit,
and the row itself queues the fix until a re-verification can absorb it. No standard-P4 projection
is authorized now. The adopted trunk's projection goes through `project_cov_nd.py`
(`DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md:114`), and `p4_project_4d.py` is
named nowhere under `docs/analysis-note/` or `docs/publication/`. So no publication product is known
to depend on this write path.

**Trigger.** Reactivate before the next run of `p4_project_4d.py`, or with the next authorized edit to
the standard-P4 execution surface. Make the fix in that same change, so it costs no extra
re-verification. Existing receipts stay as written (the row forbids retro-fitting them).

## OI-1, OI-96, OI-150, OI-186 — retired (unassigned backlog, tooling)

| Item | Next action in the register's source row | Discharged by | Measured now |
|---|---|---|---|
| OI-1 | *"Implement repository CI before scheduling the no-pipeline-debt standard."* | `f96949944` (2026-10-23): `.github/workflows/record-checks.yml` runs the record checks on every PR to `main` | the workflow is tracked; it ran on #459–#462 |
| OI-96 | Pin the FIELD, not the file, for the `RECORD-FROZEN` receipts | `8a34f12c5` (2026-08-17, "OI-96 DONE"); `verify_hash_bindings.py` `FIELD_PIN_FILE` | `44 canonical-namespace FIELD pins verified (floor 30) over 17 of 22 RECORD-FROZEN JSON receipts` |
| OI-150 | Decide whether the classifier should read a structured field rather than prose | `4e296f06a` (2026-09-03): routing is read from the declared register and the prose classifier is deleted | `control_plane_lint.py --self-test` asserts `source_classification` and `ordered_rules` are absent from the policy |
| OI-186 | Stop `uq_math.py` pairing 4.69x/4.83x with the adopted ensemble | `c9ba1b274` (2026-09-18) | `nd-unfolding/uq_math.py:125-131` quotes VL33's `5.3478x` and names the superseded text |

OI-1's second clause (scheduling the no-pipeline-debt standard) is a separate act with no row of its
own. CI no longer blocks it. OI-186 changes only a code comment; no quoted number moves.

## OI-136 — promoted, owner close-items

On the director's ruling of 2026-10-28, OI-136 moves from the unassigned backlog to the promoted
queue (`NOW`, safety/P2), owned by the close-items session (a new `close_items` row in
`control-plane/owners.tsv`). It is the fail-open `sys.path[0]` import defect that `AGENTS.md` lists
under "Quarantined and superseded traps". The next step is to re-measure it with
`state/probe-oi136-sys-path-hijack-20260826.py`, since `AGENTS.md` says never to quote its count.

## OI-73 — kept, owner close-items

The director ruled on 2026-10-28 to keep OI-73 and make the close-items session its owner. Its code
half was discharged at `18e942ee5`: `state/live-state.json` reads `LIVE / open / immutable no`, and
`LIVE-STATE.md` reads `LIVE / generated`. What stays open is the hold two Joseph decisions place on
this item's owner:

- `DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md:234`: *"regeneration is withheld
  pending `OI-73`'s owner"*;
- `DECISION-20260906-joseph-authorizes-z-specification-only.md:120`: *"`OI-73`'s hold stands"*.

**This assignment is the owner those two decisions wait on.** The director's ruling permits the
owner to regenerate `LIVE-STATE.md` under its existing rules (`AGENTS.md`, "What is happening
now?"). The register's next action is now that regeneration.

## OI-130 — kept, owner the paper rewrite lane

The director ruled on 2026-10-28 to keep OI-130 and assign it to the paper rewrite lane (a new
`paper_rewrite` row in `owners.tsv`), to start after that lane's current work (n4, then r21). Partial
coverage, measured at `fce1f5d95` and again at `9a18ddda4`: 16 of the 144 `\newcommand`s in `docs/analysis-note/values.tex`
cite a row of the RE-2 integration ledger
(`state/2d-closeout/stageF/methods/re2-integration/ledger.tsv`). The 2026-10-08 release-audit
records (`docs/publication/corrections-20261008/RECORD-20261008-release-audit-corrections.md:250`)
say explicitly that they do not close OI-130, so the class-level enumeration is still unmeasured.
Search: OI-130 in docs/publication/**, DECISION-* and RECORD-* (3 hits, all "NOT CITABLE FOR ... closing `OI-130`" or "does **not** close `OI-130`") @ 9a18ddda4

## Dependency check

Searched at `fce1f5d95` with
`git grep -E "OI-<n>([^0-9]|$)" -- KNOWN_ISSUES.md 'docs/known-issues/*' 'docs/**/DECISION-*'
'docs/**/RULING-*' 'docs/**/AUTHORIZATION-*' 'docs/**/OPERATIVE-*' 'docs/publication/**'`:

| Item | Hits | Effect on this record |
|---|---|---|
| OI-70 | 0 | retired |
| OI-127 | 0 | retired |
| OI-128 | 0 | deferred |
| OI-129 | 0 | deferred |
| OI-1, OI-96, OI-150, OI-186 | 0 each | retired |
| OI-73 | `DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md:234` ("regeneration is withheld pending `OI-73`'s owner"); `DECISION-20260906-joseph-authorizes-z-specification-only.md:120` ("`OI-73`'s hold stands") | **not disposed of here**; sent to the director |
| OI-123 | five decisions of 2026-08-22 to 2026-09-01 cite it as the route for superseding a pin | **not disposed of here**; sent to the director |

No `KNOWN_ISSUES.md` row cites any of the six. The search matches `OI-<n>` tokens only. A
dependency stated without the id would not be found, and none was searched for by other means.

## What this record does not do

It edits no launcher, receipt or execution-surface file. It deletes no row: each row's text stays
in `docs/OPEN_ITEMS.md`, with a dated prefix pointing here. It rules nothing that is reserved for
Joseph or the director.
