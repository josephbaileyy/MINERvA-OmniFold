# RECORD — OI-148: the lint field-count step retired as met, and the lint's state-cell split fixed (2026-10-30)

**By** the close-items session, on the director's ruling of 2026-10-30 (cross-session):
- *"OI-148: retire step 2 as met by #548's wiring."*
- *"Then take item 3 alone (the source_oi_rows escaped-pipe fix via split_pipe_row, with a two-direction test) as its
  own small PR after OI-74. Record the two row digests that change."*

**CITABLE FOR:** the retirement of OI-148's step 2 and its ground; the fix to `control_plane_lint.py`'s state-cell
split; the two digests that change; the tests and mutation checks below, measured at base `6dd415391`.

**NOT CITABLE FOR:** any change to a lifecycle, queue or owner. The state cell routes nothing
(`control_plane_lint.py` module docstring), and none moved.

## 1. Step 2, retired as met

OI-148's next action had two steps: put the seven-column check on a path that something runs, then give
`control_plane_lint` a field-count check. **#548** (merged as `eac51ab2e`) did the first:
- `.githooks/pre-commit:255` runs `check_open_items_columns.py --check`;
- `record-checks.yml:132` runs it in CI.

`control_plane_lint.py` runs in the same two places, `.githooks/pre-commit` and `record-checks.yml`. So a field count
inside the lint would gate no commit that the wired check does not already gate. The director ruled step 2 met on that
ground. **No code is added for it.**

## 2. The fix: the lint's state cell is split by the gate's own parser

**The defect.** `source_oi_rows` took each row's state cell with the regex `^\|\s*(OI-\d+)\s*\|\s*(.*?)\s*\|`. That
regex ends the cell at the first `|`, escaped or not. At `6dd415391`, 2 of 142 rows were cut short at an escaped `\|`:

| row | regex cell | true cell |
|---|---|---|
| OI-74 | 1,217 chars | 4,385 chars |
| OI-125 | 588 chars | 1,443 chars |

Only `state_cell_digest` and the 120-character display prefix read this cell. Both are report-only.

**The change** (`control_plane_lint.py`):
- `source_oi_rows` keeps the same regex to select rows, and takes the cell from a new `state_cell(line)`.
- `state_cell` calls `split_pipe_row` from `docs/open-items/verify_open_items_restructure.py`, the parser the
  seven-column gate imports. It is loaded by path, not copied. A row with no closing `|` is given one, so the lint reads
  a malformed row rather than raising on it.
- The new code sits below `tracked_paths`, so `:230`, where the git census in `test_mnv_guarded_run.py` cites the
  `git ls-files` call, still points at that call.

## 3. The two digests that change

`state_cell_digest` at `6dd415391`, before and after the fix:

| row | before | after | declared in `work-items.tsv` |
|---|---|---|---|
| OI-74 | `sha256:d1b6daa917a4f17751c973d98d69a73f78c3977dfeff0aadb984e461c4bec7da` | `sha256:4da69224bc950fe2eb904be5b747c15dc6f165a8862154a8bd8042fa5a20a061` | `sha256:22c968a5…` |
| OI-125 | `sha256:469a16eb98b92b429588d02d2776857020f2ec164049f47d809ec96d8920830f` | `sha256:84ce0b7f71575c67d04bd0a0a879b59953e0d15b057a1de90402393965a0df57` | `-` |

**No other row's digest changes** (140 of 142 are equal before and after). **The drift count does not change either.**
OI-74's declared digest matches neither value, so it is reported as drifted both before and after. OI-125 declares
`-`, which is never compared. The lint reports 16 state cells changed since declaration, both before and after.

OI-74's state cell is edited again by #553. Once #553 merges, its digest is a third value, which this record does not
fix.
<!-- absence-ok: digests computed over all 142 rows at 6dd415391; the remaining 140 compared equal -->

## 4. Tests

**The self-test gains a fixture in both directions:**
- `| OI-1 | OPEN \| still the state | x |`: the escaped pipe stays in the cell;
- `| OI-2 | OPEN | x | x |`: an unescaped pipe still ends it.

The check is `escaped_states == ["OPEN \\| still the state", "OPEN"]`.

**Results at the PR head:**
- `control_plane_lint.py --self-test`: PASS.
- `control_plane_lint.py` (`--check`): PASS. Its generated views are byte-identical to the tracked ones, since both cut
  points lie past the 120-character display prefix.
- `test_mnv_guarded_run.py -k TheGitAllowlistIsMEASURED`: 3 passed.

**Mutation checks.** Each made the self-test FAIL at the new check (index 9), and was then reverted:
1. the call site restored to the old `match.group(2)`;
2. `state_cell` replaced by a naive `line.split("|")[2]`.

## 5. What is left of OI-148

Both steps of its next action are closed: step 1 by #548, step 2 by the ruling above. The parse defect found on the way
is fixed here. Whether OI-148 now retires is the director's call.
