# RECORD — OI-148: both steps closed, and the row narrowed to PR-P6, which is Joseph's call (2026-10-30)

**By** the close-items session, on the director's ruling of 2026-10-30 (cross-session): *"(a). Keep OI-148 open,
narrowed to PR-P6, Joseph's call to renumber the OI ids or waive the contiguity assert. Record steps 1 and 2 as closed
(#548, #554)."*

**CITABLE FOR:** the closure of OI-148's two steps; its remaining scope and owner; the counts in §2, measured at
`9fbdc5d78`.

**NOT CITABLE FOR:** a renumbering, a waiver, or any change to `verify_open_items_restructure.py`. Those are Joseph's.

## 1. What closed

| step | closed by | record |
|---|---|---|
| 1. put the seven-column check on a path that something runs | #548: `.githooks/pre-commit` and `record-checks.yml`, tested by `test_open_items_wiring.py`; the long-line pin is reset to 147 and can only fall | [`DECISION-20261030-joseph-canonical-checkout-and-table-check.md`](DECISION-20261030-joseph-canonical-checkout-and-table-check.md), item 2 |
| 2. a field-count check in `control_plane_lint` | retired as met by the director, since the lint runs in the same hook and CI; #554 fixed the lint's state-cell split instead | [`RECORD-20261030-close-items-oi148-lint-state-cell.md`](RECORD-20261030-close-items-oi148-lint-state-cell.md) |

## 2. What stays open: PR-P6

**Why the row was not retired.** The director ruled retirement once both steps closed. The dependency check then found
a residual that two LIVE documents route to OI-148:
- [`PUBLICATION-READINESS-20260822.md`](PUBLICATION-READINESS-20260822.md):
  - PR-J10 (`:428`): *"`OI-148` residual: renumber the `OI-*` ids, or waive the check"*;
  - PR-P6 (`:1139`), owner **Joseph** (renumber or waive);
- [`POST_PUBLICATION_REORG_PLAN.md`](../POST_PUBLICATION_REORG_PLAN.md) `:262`: *"`OI-145`: its remaining checker failure
  belongs to `OI-148`, which stays active."*

No ruling on PR-P6 or PR-J10 was found. Search: `git grep 'PR-P6\|PR-J10'` and `git grep -i renumber` over
`docs/orchestration/DECISION-*` and `docs/OPEN_ITEMS.md` @ `dc1d7adbb`.

**The residual, measured at `9fbdc5d78`.** `python3 docs/open-items/verify_open_items_restructure.py` exits 1 with an
`AssertionError` at `verify_table` `:252`. That assert requires the data ids to be exactly `OI-1..OI-N`. The table has
142 data rows and 140 distinct ids, and they are not contiguous. The script's comment at `:215-216` calls this
*"unsatisfiable without renumbering ids cited in pushed commits"*.

**Waiving the contiguity assert alone would not turn the script green.** The asserts after `:252` fail too, on this
table:

| assert | line | rows that fail it |
|---|---|---|
| state in `CONTROLLED_STATES` | `:253` | 135 |
| next action ends in `.` | `:254` | 39 |
| detail cell has a link | `:259` | 38 |

These were counted by running each assert's own condition over `split_pipe_row`'s rows; the script stops at the first
failure. The comment at `:216-217` names the same three rules (74, 15 and 15 rows at `46993255`). So the counts have
grown since, and the choice Joseph faces covers all four asserts, not one. **Nothing runs the script's `main`, so none
of this gates a commit.**

## 3. The row now

OI-148: `active`, `WAITING-JOSEPH`, owner `joseph`, with this record as its authority. The director is putting PR-P6
to Joseph alongside the OI-74 question.
