# RECORD — PR-P6: `verify_open_items_restructure.py`'s row rules retired, and OI-148 retired (2026-10-30)

**By** the close-items session, under
[`DECISION-20261030-joseph-oi74-second-run-and-pr-p6.md`](DECISION-20261030-joseph-oi74-second-run-and-pr-p6.md)
(#558), item 2. Joseph's answer, verbatim: *"Retire its row rules (Recommended)"*. The option it accepts: *"The live
column check (now in the hook and CI) covers table shape; record the old row rules as retired. No ids renumbered, no
rows rewritten."*

**CITABLE FOR:** which rules are retired and which stand; where the retirement is recorded; the retirement of OI-148
and its dependency check.

**NOT CITABLE FOR:** a renumbering or a rewrite of any row; any change to what the script asserts. The rules stay in
the code as they stood.

## 1. What is retired, and what stands

In `docs/open-items/verify_open_items_restructure.py` `verify_table()`, at `29fdf6b49`:

| rule | line | rows failing it at `29fdf6b49` | now |
|---|---|---|---|
| data ids are exactly `OI-1..OI-N` | `:252` | not contiguous: 142 rows, 140 distinct ids (`OI-64` and `OI-65` twice each) | **retired** |
| state in `CONTROLLED_STATES` | `:253` | 135 | **retired** |
| next action ends in `.` | `:254` | 39 | **retired** |
| the detail cell has a link, and each local link resolves | `:260`, `:266` | 38 have no link; 0 unresolved | **retired** |
| 7 fields per line, exact header | `:247-248` | 0 | stands; gated live by `check_open_items_columns.py` (#548) |
| long-line pin, `OVER_LIMIT_PINNED = 147` | — | — | stands; pinned by `test_open_items_wiring.py` (#548) |
| `verify_conservation`, `verify_canonical_homes` | — | PASS | stand |

**In the script,** a six-line comment above `data = rows[2:]` names the four retired rules, the decision and this
record. Nothing else in the script changes, so the retired rules now start at `:258`. The script still exits 1 at the
first of them, as before. Nothing runs its `main`.

**`tools/developer/suites.json`** re-admits the edited file. Its `reviewed_sha256` goes from `eae6654f…` to
`18663c3a7a4c653deb25d8af338c4c547697d7faed6ae0ae6891b45697ec0005`. The comment is the only change. Tests at this
head: `test_check_open_items_columns.py` passes, `test_open_items_wiring.py` passes 11/11, and
`check_open_items_columns.py --self-test` passes 9/9.

**A correction to #557's record, beside it (that record is not edited).**
[`RECORD-20261030-close-items-oi148-narrowed-to-pr-p6.md`](RECORD-20261030-close-items-oi148-narrowed-to-pr-p6.md)
§2 cites the detail-link assert as `:259`. It is `:260` at both `9fbdc5d78` and `29fdf6b49`. Its row count, 38, stands.

## 2. Beside the documents that route PR-P6

None of these documents is edited. This record stands beside them, and its CATALOG row is how they are found:
- **`PUBLICATION-READINESS-20260822.md`**:
  - PR-J10 (`:428`), *"`OI-148` residual: renumber the `OI-*` ids, or waive the check"*: decided. The check's row rules
    are retired; no id is renumbered.
  - PR-P6 (`:1139`), owner Joseph, *"renumber or waive"*: decided, the same way.
- **`POST_PUBLICATION_REORG_PLAN.md:262`**, *"`OI-145`: its remaining checker failure belongs to `OI-148`, which stays
  active."* That failure is the retired row rules above. OI-148 is retired below, so that clause no longer describes
  the register.

## 3. OI-148 retired

**Its ground:**
- Step 1, wire the seven-column check, closed by #548
  ([`DECISION-20261030-joseph-canonical-checkout-and-table-check.md`](DECISION-20261030-joseph-canonical-checkout-and-table-check.md),
  item 2).
- Step 2, a field count in `control_plane_lint`, retired as met; #554 fixed the lint's state-cell split instead
  ([`RECORD-20261030-close-items-oi148-lint-state-cell.md`](RECORD-20261030-close-items-oi148-lint-state-cell.md)).
- PR-P6, the residual it was narrowed to by #557
  ([`RECORD-20261030-close-items-oi148-narrowed-to-pr-p6.md`](RECORD-20261030-close-items-oi148-narrowed-to-pr-p6.md)),
  decided by #558 and recorded here.

**The dependency check.** Search: `git grep -n 'OI-148'` over the tree @ `29fdf6b49`. The routes to OI-148 as open
work are PR-J10, PR-P6 and `POST_PUBLICATION_REORG_PLAN.md:262`, all answered in §2. The other hits are history:
- docstrings in `check_open_items_columns.py`, `test_check_open_items_columns.py`, `test_open_items_wiring.py` and
  `verify_open_items_restructure.py`;
- the CI step name `record-checks.yml:136`;
- `HOLD-20260821-clause-c-verification.md`;
- `ISSUE-71`, which names *"a check with no caller"* as a catalogued shape.

None of them waits on the row.

**The row now:** OI-148 is `retired`, with no queue, owner `close_items` and this record as authority, as OI-152 was
retired on 2026-10-28.
