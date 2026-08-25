#!/usr/bin/env python3
"""Guard: every pipe-table row in docs/OPEN_ITEMS.md has exactly 7 fields, and the header names them.

    python3 docs/open-items/check_open_items_columns.py --check       # the gate (index content)
    python3 docs/open-items/check_open_items_columns.py --worktree    # same rule, file on disk
    python3 docs/open-items/check_open_items_columns.py --self-test   # both directions, 9 arms

WHAT THIS IS. The seven-column check of `verify_open_items_restructure.verify_table` -- `widths == {7}`
plus the header-row assert -- lifted onto a path something can take. `47a9e3b6` named this as the
extraction target after that file's own comment block first named the wrong one; the naming is also
`OI-148`'s next-action cell, "put the seven-column check on a path something takes".

WHY THE RATCHET IS NOT HERE, and this is the load-bearing exclusion rather than an oversight.
`verify_table` also carries `OVER_LIMIT_PINNED` / `LONGEST_LINE_PINNED`, a hand-maintained count pin.
A pin cannot be hooked: `.githooks/pre-commit:11` admits a check "iff a committer who did nothing
wrong can always make it pass", and a committer who files one legitimate narrative row -- the format
this file is *designed* around -- pushes the count past the pin and is blocked until they edit a
constant. That is the same failure the dispatcher already declined `check_canonical_designation.py`
for ("wiring it installs a check that reddens on an innocent edit"). The pin stays in
`verify_open_items_restructure.py`, unwired, for a reviewer. It is deliberately NOT importable from
here, so that wiring this file cannot drag it along.

WHY THIS ONE PASSES THE ADMITTING RULE, in both directions:
  * a well-formed row always passes -- there is no pin, no inventory, no count to maintain, and
    nothing tree-global that another lane can flip underneath you; and
  * the only way to fail is to emit a row that is not 7 fields wide, which IS the defect. Four rows
    in this file were structurally malformed (`OI-148`), and every tool that reads them by column got
    the wrong fields.

MEASURED BEFORE PROPOSING, not recalled, because that measurement is what decided the
`check_canonical_designation.py` decline ("not because the check is wrong, but because the tree is"):
`46993255` -> 115 table lines, 115 at width 7, zero non-7, header exact. Re-measured at `57d9f3fb`
(this file's parent): identical. So there is no inherited debt for a lane to be blocked on, and the
decline ground does not apply. Do not trust those two numbers -- run `--check`, it prints its own.

IT READS THE INDEX, NOT THE WORKING TREE, and on this checkout that is not a detail. Three lanes
commit through one tree, so a worktree read would let lane A's unsaved edit block lane B's unrelated
commit -- an innocent committer who cannot make it pass, i.e. the admitting rule failing from the
direction that matters. Use `--worktree` to see what is on disk (useful while editing, wrong here).

  A PEER OBJECTED THAT THE INDEX READ ONLY NARROWS THAT HOLE RATHER THAN CLOSING IT -- a STAGED row
  is uncommitted too, and lanes stage constantly -- so a pathspec commit (`git commit -- other.txt`)
  would be refused over another lane's staged row that the commit does not contain. THE OBJECTION IS
  SOUND IN FORM AND THE PREDICTION DOES NOT REPRODUCE, measured from inside a real installed hook on
  git 2.39.3 rather than by reasoning about it. GIT HANDS A PARTIAL COMMIT ITS OWN INDEX:

    lane B: <malform docs/OPEN_ITEMS.md> && git add docs/OPEN_ITEMS.md
    lane A: git commit -m x -- other.txt
      in the hook: GIT_INDEX_FILE=.git/next-index-<pid>.lock   <- a TEMPORARY index, not the shared one
                   git show :docs/OPEN_ITEMS.md   -> the GOOD row
                   git diff --cached --name-only  -> other.txt        (OPEN_ITEMS.md absent)
      the commit lane A produced: the GOOD row.  This check stays SILENT. Correctly.

  `git show` and `git cat-file` honour `GIT_INDEX_FILE`, and this module shells out without scrubbing
  the environment, so it inherits that index automatically. Do not "fix" that by passing an explicit
  index path -- the inheritance is what makes the pathspec case correct.

  INDEPENDENTLY REPRODUCED, and this paragraph's earlier "recorded as a disagreement to settle" is
  now stale and replaced. The objecting lane re-ran it from inside a real hook on the SAME git
  (2.39.3, Apple Git-146) and got the same two rows: pathspec -> next-index-<pid>.lock, GOOD, hook
  silent; plain commit -> .git/index, MALFORMED, and the commit contained MALFORMED. So it was never
  a machine difference. THE CAUSE IS WORTH MORE THAN THE RESULT: their first probe ran ALONGSIDE the
  commit rather than INSIDE the hook, and those are two different subjects. A pre-commit hook is not
  a shell standing next to git; it is a child git configures on purpose, so any claim about what a
  hook can see is only measurable in that child. Both readings were real and both commands were
  correct -- they just answered about different processes.

  THE RESIDUAL IS REAL BUT IT IS NOT A FALSE BLOCK. On a plain `git commit` (no pathspec) or
  `git commit -a`, the hook does see a peer's staged malformed row -- and measurement confirms the
  resulting commit CONTAINS that row. So the check fires on a defect the committer is genuinely about
  to publish under their own name. That is the shared-checkout hazard already recorded in this
  campaign (a no-pathspec `git commit` commits the other lane's staged work); this check makes it
  loud instead of silent. It can still be someone else's row, which is why the failure output says so
  and points at `git diff --cached` rather than letting the author hunt for a mistake they did not
  make. A diagnostic that misdirects costs more than the block.

THE PARSER IS IMPORTED, NOT COPIED. `split_pipe_row` comes from `verify_open_items_restructure` so
that the two cannot disagree about what a field is -- a vendored copy would be a second escaping rule
that drifts silently, and five rows in this file already carry an escaped `\\|` whose handling decides
their width. Arm 8 asserts the import resolved to that file and not to something else on sys.path.

WHAT IT DOES NOT DO, so a green run is not over-read: it counts FIELDS and checks the header LABELS.
It says nothing about what is in a field -- not the states, not the ids, not the pointers, not line
length. `expected_ids`, `CONTROLLED_STATES`, the terminal-period rule and the per-row detail pointer
stay in `verify_open_items_restructure.py` and are all currently unsatisfiable on this tree; that is
why the whole file cannot be hooked and only this slice can.
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REL = "docs/OPEN_ITEMS.md"

# The header IS the field-name contract; a tool reading by column index is reading this list.
HEADER = ["id", "state", "lane/owner", "blocker", "next action", "detail", "as_of"]
WIDTH = len(HEADER)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_open_items_restructure import split_pipe_row  # noqa: E402


def table_rows(text: str) -> list[tuple[int, list[str]]]:
    """Every pipe-table line, as (1-based source line number, fields). Same selection as verify_table:
    a line is a table line iff it starts with `|`, which is why the delimiter row is included and
    counted -- `|---|---|...|` is 7 fields wide too, and a lane that deletes a dash cell breaks the
    render exactly like a malformed data row does."""
    rows = []
    for number, line in enumerate(text.splitlines(), start=1):
        if line.startswith("|"):
            rows.append((number, split_pipe_row(line)))
    return rows


def violations(text: str) -> list[str]:
    """[] means the rule holds. Never raises on a malformed table -- a guard that dies on its own
    defect prints a traceback instead of the row that caused it."""
    rows = table_rows(text)
    if len(rows) < 3:
        return [f"{REL}: found {len(rows)} pipe-table line(s); expected a header, a delimiter and rows"]

    out = []
    for number, cells in rows:
        if len(cells) != WIDTH:
            # cells[0] is the id for a data row; it is `id` for the header and `---` for the delimiter.
            label = cells[0][:24] if cells and cells[0] else "(empty first field)"
            out.append(
                f"{REL}:{number}: {len(cells)} fields, expected {WIDTH} "
                f"[{label}] -- an unescaped `|` adds a field, a missing one merges two; "
                "escape it as `\\|`"
            )

    number, cells = rows[0]
    if cells != HEADER:
        if len(cells) == WIDTH:
            diff = ", ".join(
                f"col {i}: {got!r} != {want!r}" for i, (got, want) in enumerate(zip(cells, HEADER)) if got != want
            )
            out.append(f"{REL}:{number}: header labels differ ({diff})")
        else:
            out.append(f"{REL}:{number}: header row is not the {WIDTH} field names {HEADER}")
    return out


def read_index() -> str:
    """The content this commit will record. Status is read from the completed process, never from a
    pipeline tail, and a missing path is detected by cat-file -e rather than by a sentinel string --
    `git show` prints its own argument on some failures, which reads as content."""
    probe = subprocess.run(
        ["git", "cat-file", "-e", f":{REL}"], cwd=ROOT, capture_output=True, text=True
    )
    if probe.returncode != 0:
        raise SystemExit(f"{REL} is not in the index (returncode {probe.returncode}): {probe.stderr.strip()}")
    shown = subprocess.run(
        ["git", "show", f":{REL}"], cwd=ROOT, capture_output=True, text=True
    )
    if shown.returncode != 0:
        raise SystemExit(f"git show :{REL} failed (returncode {shown.returncode}): {shown.stderr.strip()}")
    return shown.stdout


def check(source: str = "index") -> int:
    started = time.time()
    if source == "index":
        text = read_index()
    else:
        text = (ROOT / REL).read_text(encoding="utf-8")
    bad = violations(text)
    rows = table_rows(text)
    elapsed = time.time() - started
    if bad:
        print(f"OPEN_ITEMS COLUMNS :: FAIL -- {len(bad)} violation(s) in the {source}")
        for line in bad:
            print("  " + line)
        if source == "index":
            # THE ROW MAY NOT BE YOURS, and saying so is the point. Three lanes stage into one index,
            # and a no-pathspec `git commit` commits the other lane's staged work -- so a committer
            # who touched nothing here can be stopped by a row they did not write. Sending them to
            # hunt for their own mistake is the expensive failure; name the possibility and hand them
            # the command that settles it in one line.
            print(
                "\n  This reads the INDEX -- the content your commit will record, not your editor "
                "buffer.\n"
                "  If you did not write that row, it is another lane's staged work and a plain "
                "`git commit`\n"
                "  would publish it under your name. Settle it, then choose:\n"
                f"    git diff --cached -- {REL}      # is the malformed row in what you are about to commit?\n"
                f"    git log -1 --format=%an -- {REL}  # who last touched it on HEAD\n"
                "  Yours     -> fix the row; an unescaped `|` in a narrative cell must be written `\\|`.\n"
                "  Theirs    -> commit BY PATHSPEC (`git commit -- <your paths>`); git gives a partial\n"
                "               commit its own index, so this check then sees your content, not theirs.\n"
                "  Do NOT --no-verify: on a plain commit the malformed row really is in your commit."
            )
        return 1
    print(
        f"OPEN_ITEMS COLUMNS :: OK -- {len(rows)} table line(s), all {WIDTH} fields, "
        f"header exact ({source}, {elapsed:.3f} s)"
    )
    return 0


def self_test() -> int:
    """THREE ARMS AT MINIMUM, and the fixtures come from the PRODUCER rather than from the rule: every
    arm below starts from the real committed `OPEN_ITEMS.md` and mutates one real row. A fixture
    written to satisfy the rule cannot disagree with it, and a synthetic `| a | b |` table would not
    exercise the escaped pipes that five real rows carry.

    The two directions are NOT symmetric in origin, which is why both are here: an unescaped `|` in a
    narrative cell ADDS a field (8), a dropped delimiter MERGES two (6). A one-directional guard would
    wave one of them straight through -- the shape that let an over-length diagonal pass at
    `b2d7d4ca`. Arms 4 and 5 exist because `widths == {7}` is blind to header content, so the header
    assert has to be shown live on its own.
    """
    started = time.time()
    fails: list[str] = []

    def arm(label: str, ok: bool, detail: str = "") -> None:
        print(("  PASS  " if ok else "  FAIL  ") + label + (" :: " + detail if detail else ""))
        if not ok:
            fails.append(label)

    good = (ROOT / REL).read_text(encoding="utf-8")
    lines = good.splitlines()
    # A fixed, named target: the first data row. Chosen by POSITION, not by "a row that is 7 wide" --
    # selecting the fixture with the predicate under test is how a fixture stops being able to fail.
    data_indices = [i for i, line in enumerate(lines) if line.startswith("|")][2:]
    target = data_indices[0]
    row = lines[target]

    def with_row(new: str) -> str:
        edited = list(lines)
        edited[target] = new
        return "\n".join(edited) + "\n"

    # 1. SILENT ON A GOOD TREE. The real file, unmutated. If this fires the tree is broken, not the check.
    arm("the real OPEN_ITEMS.md passes untouched", violations(good) == [],
        "; ".join(violations(good))[:200])

    # 2. FIRES on the merge direction: drop one interior delimiter -> 6 fields.
    cut = row.find("|", row.find("|", 1) + 1)  # the delimiter closing field 2
    six = with_row(row[:cut] + row[cut + 1:])
    v6 = violations(six)
    arm("a row with a DROPPED delimiter (6 fields) is caught",
        len(v6) == 1 and "6 fields" in v6[0], v6[0][:160] if v6 else "no violation reported")

    # 3. FIRES on the opposite direction: an unescaped `|` inside a narrative cell -> 8 fields. This is
    #    the malformation the four OI-148 rows actually had.
    inject = row.find("|", 1) + 1
    eight = with_row(row[:inject] + " a|b " + row[inject:])
    v8 = violations(eight)
    arm("a row with an UNESCAPED pipe (8 fields) is caught",
        len(v8) == 1 and "8 fields" in v8[0], v8[0][:160] if v8 else "no violation reported")

    # 4. The header assert is LIVE and independent of the width rule: still 7 fields, wrong label.
    header_index = [i for i, line in enumerate(lines) if line.startswith("|")][0]
    renamed = list(lines)
    renamed[header_index] = renamed[header_index].replace("| next action |", "| next_action |")
    vh = violations("\n".join(renamed) + "\n")
    arm("a RENAMED header column is caught although the width is still 7",
        len(vh) == 1 and "header labels differ" in vh[0], vh[0][:160] if vh else "no violation reported")

    # 5. And to ORDER, not just to the set of names -- a swap keeps every label and every width.
    swapped = list(lines)
    swapped[header_index] = "| id | state | lane/owner | blocker | detail | next action | as_of |"
    vs = violations("\n".join(swapped) + "\n")
    arm("a REORDERED header (same labels, same width) is caught",
        len(vs) == 1 and "header labels differ" in vs[0], vs[0][:160] if vs else "no violation reported")

    # 6. THE INNOCENT DIRECTION, and it is the one that decides hook membership: an escaped `\|` is a
    #    legal field character. If it split, the guard would redden on a correct row.
    escaped_rows = sum(1 for line in lines if line.startswith("|") and "\\|" in line)
    injected = row.find("|", 1) + 1
    legal = with_row(row[:injected] + " a\\|b " + row[injected:])
    arm(f"an ESCAPED pipe stays one field ({escaped_rows} real rows rely on this)",
        violations(legal) == [] and escaped_rows > 0)

    # 7. A table too small to have a header is reported, not crashed through.
    arm("a file with no table is reported rather than IndexError",
        len(violations("no table here\n")) == 1)

    # 8. The parser is the one in verify_open_items_restructure.py, not a same-named import.
    import verify_open_items_restructure as vor
    arm("split_pipe_row comes from verify_open_items_restructure.py",
        split_pipe_row is vor.split_pipe_row
        and Path(vor.__file__).resolve() == (ROOT / "docs/open-items/verify_open_items_restructure.py"))

    # 9. NEGATIVE CONTROL ON THE FIXTURE MACHINERY. Arms 2/3/6 mean nothing if `with_row` silently
    #    produced the original text; assert each mutation actually changed the file and only that row.
    arm("each mutation changed exactly its target row",
        six != good and eight != good and legal != good
        and six.splitlines()[target] != row
        and len(six.splitlines()) == len(lines) == len(eight.splitlines()))

    elapsed = time.time() - started
    print()
    if fails:
        print(f"SELF-TEST :: FAILED -> {fails}")
        return 1
    print(f"SELF-TEST :: 9/9 PASS in {elapsed:.3f} s (fixtures mutated from the real file; nothing written)")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:] or ["--check"]
    if "--self-test" in args:
        raise SystemExit(self_test())
    if "--worktree" in args:
        raise SystemExit(check(source="worktree"))
    raise SystemExit(check(source="index"))
