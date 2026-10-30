# RECORD — OI-175 and OI-176 repaired to seven fields, and the numbers behind OI-148's wiring question (2026-10-30)

**By** the close-items session, on the director's order of 2026-10-30 (backlog candidate 1): *"(a) the format-only
repair of OI-175 and OI-176's cells, checked by split_pipe_row, and (b) the numbers record for Joseph's wiring
question. Moving the ratchet pin and wiring the check stay his."* Measured at `origin/main` `776bc811b`.

**CHANGES:** eight backslashes in `docs/OPEN_ITEMS.md`, one in OI-175 and seven in OI-176, plus a dated prefix on
OI-148. No checker, pin, hook, test or other row is edited.

**CITABLE FOR:** what each OPEN_ITEMS check reads on main and after the repair, and since when.

**NOT CITABLE FOR:**
- a decision to wire any check, or to move or retire the ratchet pin. Those are Joseph's (§3);
- anything about the content of OI-175 or OI-176. Both stay DISCHARGED and their text is unchanged.

## 1. The repair

**Both rows had unescaped `|` characters inside code spans.** Each one split a cell, so every tool that reads the
table by column got the wrong fields. Counted by `split_pipe_row`, imported from
`docs/open-items/verify_open_items_restructure.py`:

| row | line | fields on main | the unescaped pipes | introduced by | fields after |
|---|---:|---:|---|---|---:|
| OI-175 | 104 | 8 | one, the shell pipe in `` `scrontab -l \| grep -c mnv-dashboard` `` | `077d81750` (2026-08-30, *"[f17b] Re-capture the F-17 operands under the canonical quiesce"*), in the REMEDIATED prefix it added. The row was born at 7 in `228d8da48` | 7 |
| OI-176 | 101 | 14 | seven, the regex alternations in `` `MNV_*(FORCE\|REDO\|OVERWRITE\|NOSKIP\|IGNORE)*` `` and `` `quarantin\|resume\|skip\|existing product` `` | `d3742e93b` (2026-08-30), which filed the row at 14 | 7 |

**Format only.** The script that made the edit asserts that the only change to each line is a `\` inserted directly
before a `|`: 1 in OI-175, 7 in OI-176. `git diff --stat` reads 2 lines changed.

**After the repair:**
- all 144 table lines are 7 fields wide;
- `check_open_items_columns.py --worktree` prints *"OK -- 144 table line(s), all 7 fields, header exact"*, and
  `--self-test` passes 9/9;
- the suite `docs/open-items/test_check_open_items_columns.py` goes from **16 failed, 17 passed** on main to
  **33 passed** (pytest 8.3.4, `TMPDIR` in the scratchpad).

`tools/developer/REVIEW_RESOLUTION.md` (`6c8435b50`, 2026-09-28) recorded that suite at 18 failed, naming these two
rows, with *"separate disposition pending"*. Of its 18, 16 fail here on main. The other two,
`test_git_gives_a_partial_commit_its_own_index` and `test_scrubbing_git_index_file_reintroduces_the_false_block`, pass
on main in this environment. Why they failed there was not investigated. That record is left unchanged.

## 2. The numbers

**The ratchet.** `verify_open_items_restructure.py` passes `repin` and `conservation`, then exits 1 in
`verify_table`: *"147 lines exceed 400 bytes, pinned at 112"*. The longest line is 23,503 bytes, exactly its pin. The
repair is ratchet-neutral: 147 before and after, because both rows were already over 400 bytes.

The count's history, from every commit to `docs/OPEN_ITEMS.md` since 2026-08-20:
- **112:** set at `afa8447f4` (2026-08-21), the OI-148 reconstruction;
- **113:** first over the pin at `f0bd77e5f` (2026-08-24), when OI-138 was filed;
- **147:** at `3b578ba87` (2026-10-29), the last commit to change it.

After the pin was set, 26 commits raised the count, by 35 lines in all. They came from many lanes, this one included: the last two increments,
`6bf056b56` and `3b578ba87`, are this lane's. Filing or extending a narrative row is the file's normal use, so the pin
falls behind whenever the file is used. The checker's own comment, `verify_open_items_restructure.py:181-184`, makes
this point.

**The seven-column check, over the same commits:**

| from | widths | cause |
|---|---|---|
| `afa8447f4` (2026-08-21) | {7} | the four-row reconstruction |
| `32e403b84` (2026-08-29) | {7, 9} | a 9-field row, repaired at `228d8da48` (2026-08-30) |
| `228d8da48` (2026-08-30) | {7} | |
| `077d81750` (2026-08-30) | {7, 8} | OI-175 |
| `d3742e93b` (2026-08-30) to `776bc811b` | {7, 8, 14} | OI-176 |
| this repair | {7} | |

So the check had been red on main for two months, from 2026-08-30 until this repair.

**What `verify_table` reads past the ratchet.** A scratch copy with one line changed, `OVER_LIMIT_PINNED = 112` to
`147`, passes the width and header asserts on the repaired file. It then stops at `expected_ids`
(`verify_open_items_restructure.py:245`). The remaining clauses were counted on the repaired file with the checker's
own expressions, and its imported `split_pipe_row` and `CONTROLLED_STATES`:

| clause | at OI-148's 2026-08-21 count | now |
|---|---|---|
| data rows | 113 | 142 |
| `expected_ids`, rows `OI-1`..`OI-n` in order | unsatisfiable | unsatisfiable: ids span OI-1 to OI-193, in no position equal to the expected list; 140 distinct, because OI-64 and OI-65 each appear twice (the recorded lane-A/lane-C collision, `BEN-159`) |
| state cells outside `CONTROLLED_STATES` | 73 | 135 |
| next actions without a terminal period | 15 | 39 |
| rows with no `detail` pointer | 16 | 38 |
| unresolved pointers | 0 | 0 |

The checker's comment, `:210-214`, names these four clauses as what blocks the whole file from a hook. All four still do.

## 3. The wiring question, as it stands

**The seven-column slice already exists on a runnable path.** `docs/open-items/check_open_items_columns.py`
(`eeb0760c4`, 2026-08-22) is the extraction OI-148's next action asked for. It reads the index, imports
`split_pipe_row` rather than copying it, and leaves the ratchet out on purpose. OI-148's row predates it, and its
cells still describe the check as having no runnable path. This record does not edit those cells.

**Nothing calls it.**
Search: `git grep -n -E "verify_open_items|check_open_items_columns" -- .githooks .github` @ `776bc811b`, rc 1, no output.
The only other callers are its own test file and the opt-in suite entry in `tools/developer/suites.json`. So it is in
neither the pre-commit hook's run list nor its declined list. That is the same state the hook header's *"an unlisted
check is not a decision"* warns about.

**What changed today.** The column gate's declared precondition, a green tree, held at `46993255` and `57d9f3fb` in
August and has failed since 2026-08-30. It holds again after this repair. The index read stays red until the repair
is committed: `--check` on this worktree's index reported the two rows before staging, and *"OK -- 144 table line(s), all 7
fields, header exact (index)"* after.

**Joseph's decisions, unchanged by this record:**
1. **The column gate:** wire `check_open_items_columns.py --check` into `.githooks/pre-commit`, or list it there as
   declined, with a reason.
2. **The ratchet:** move `OVER_LIMIT_PINNED` from 112 with a stated reason, or retire it. It cannot be hooked under the
   admitting rule, as the checker and the column gate both say.
3. **`control_plane_lint`:** OI-148's second step, a field-count check there. Not re-measured here.

## 4. Limits

- The two non-reproducing suite failures in §1 are noted, not explained.
- The 2026-08-21 column of §2 is quoted from OI-148's detail cell, not re-measured at that commit.
- OI-148 stays open, and its owner column is unchanged.
