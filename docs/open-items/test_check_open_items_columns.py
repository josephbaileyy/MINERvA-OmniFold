#!/usr/bin/env python3
"""Tests for check_open_items_columns.py.

    python3 -m pytest docs/open-items/test_check_open_items_columns.py -q

TWO LAYERS, and the second is the one that would have caught the defect this check exists for.

  (1) THE RULE, in three arms -- fires on a short row, SILENT on a good tree, fires on the opposite
      (long) malformation. A guard shown only to fire proves nothing, and a guard shown only to pass
      proves less; the silent-on-good arm is what carries the `.githooks/pre-commit:11` admitting
      rule, "a committer who did nothing wrong can always make it pass".

  (2) THE SELF-TEST'S POWER, by mutating the checker and asserting `--self-test` goes RED. `--self-test`
      is the artifact a hook would run, and a self-test that cannot fail is the exact shape of the
      OI-148 defect one level up: an assert nothing reaches. `test_self_test_*` break one line of the
      checker in a scratch copy and require a non-zero exit; without them, arms could be vacuous.
      `test_self_test_catches_a_one_directional_guard` is the specific historical shape -- `b2d7d4ca`,
      where a `<`-style coverage guard waved an over-length input through and the gate exited 0.

The index path is exercised END TO END against real `git init` + `git add` in a tmp_path repo, not by
stubbing subprocess: `CONVENTION-lane-worktrees.md` records that `merge_guard.sh`'s one false pass was
caught end-to-end and NOT by its self-test.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CHECKER = HERE / "check_open_items_columns.py"
PARSER = HERE / "verify_open_items_restructure.py"
OPEN_ITEMS = ROOT / "docs/OPEN_ITEMS.md"

sys.path.insert(0, str(HERE))
import check_open_items_columns as mod  # noqa: E402


# --------------------------------------------------------------------------------------------------
# Fixtures come from the PRODUCER -- the real committed file -- and are mutated. A table written to
# satisfy the rule cannot disagree with it, and a synthetic `| a | b |` fixture would not carry the
# escaped pipes that five real rows depend on.
# --------------------------------------------------------------------------------------------------
def real_lines() -> list[str]:
    return OPEN_ITEMS.read_text(encoding="utf-8").splitlines()


def pipe_indices(lines: list[str]) -> list[int]:
    return [i for i, line in enumerate(lines) if line.startswith("|")]


def swap_row(lines: list[str], index: int, new: str) -> str:
    edited = list(lines)
    edited[index] = new
    return "\n".join(edited) + "\n"


def first_data_index(lines: list[str]) -> int:
    """By POSITION, not by "a row that happens to be 7 wide" -- selecting the fixture with the
    predicate under test is how a fixture stops being able to fail."""
    return pipe_indices(lines)[2]


# --------------------------------------------------------------------------------------------------
# Layer 1 -- the three arms.
# --------------------------------------------------------------------------------------------------
def test_silent_on_a_good_tree():
    """ARM 2 of 3. The committed file, untouched. If this fails the tree is malformed, not the check --
    and that distinction is what decided the check_canonical_designation.py decline."""
    assert mod.violations(OPEN_ITEMS.read_text(encoding="utf-8")) == []


def test_fires_on_a_short_row():
    """ARM 1 of 3. A dropped delimiter merges two fields: 7 -> 6."""
    lines = real_lines()
    i = first_data_index(lines)
    row = lines[i]
    cut = row.find("|", row.find("|", 1) + 1)
    found = mod.violations(swap_row(lines, i, row[:cut] + row[cut + 1:]))
    assert len(found) == 1 and "6 fields" in found[0], found


def test_fires_on_a_long_row():
    """ARM 3 of 3, the OPPOSITE direction, and it is the malformation the four OI-148 rows actually
    had: an unescaped `|` inside a narrative cell adds a field, 7 -> 8."""
    lines = real_lines()
    i = first_data_index(lines)
    row = lines[i]
    j = row.find("|", 1) + 1
    found = mod.violations(swap_row(lines, i, row[:j] + " a|b " + row[j:]))
    assert len(found) == 1 and "8 fields" in found[0], found


@pytest.mark.parametrize("width", [3, 5, 6, 8, 11, 14])
def test_every_off_by_n_width_fires_in_both_directions(width):
    """`widths == {7}` is a set equality, so it is symmetric by construction -- but OI-148 records
    that control_plane_lint still passes a 5-wide and an 11-wide row, so symmetry is asserted rather
    than assumed. Both named widths are in this list."""
    lines = real_lines()
    i = first_data_index(lines)
    row = "|" + "|".join(f" c{n} " for n in range(width)) + "|"
    found = mod.violations(swap_row(lines, i, row))
    assert len(found) == 1 and f"{width} fields" in found[0], (width, found)


# --------------------------------------------------------------------------------------------------
# The header assert, which the width rule cannot see.
# --------------------------------------------------------------------------------------------------
def test_fires_on_a_renamed_header_at_the_same_width():
    lines = real_lines()
    i = pipe_indices(lines)[0]
    renamed = lines[i].replace("| next action |", "| next_action |")
    assert renamed != lines[i]
    found = mod.violations(swap_row(lines, i, renamed))
    assert len(found) == 1 and "header labels differ" in found[0], found


def test_fires_on_a_reordered_header():
    """Same labels, same width -- only the ORDER moved, which is precisely what breaks a tool reading
    by column index while leaving the table rendering correctly."""
    lines = real_lines()
    i = pipe_indices(lines)[0]
    swapped = "| id | state | lane/owner | blocker | detail | next action | as_of |"
    found = mod.violations(swap_row(lines, i, swapped))
    assert len(found) == 1 and "header labels differ" in found[0], found


def test_header_contract_matches_the_source_of_the_extraction():
    """The extracted constant must equal the literal in verify_table, or the two checks disagree about
    what the columns are called. Read from the source text rather than trusted from memory."""
    text = PARSER.read_text(encoding="utf-8")
    literal = 'assert rows[0] == ["id", "state", "lane/owner", "blocker", "next action", "detail", "as_of"]'
    assert literal in text, "verify_table's header assert changed; re-derive HEADER"
    assert mod.HEADER == ["id", "state", "lane/owner", "blocker", "next action", "detail", "as_of"]
    assert mod.WIDTH == 7


# --------------------------------------------------------------------------------------------------
# The innocent direction: legal content must never redden. This is the half of the admitting rule a
# fires-on-bad test cannot reach.
# --------------------------------------------------------------------------------------------------
def test_an_escaped_pipe_is_one_field():
    lines = real_lines()
    i = first_data_index(lines)
    row = lines[i]
    j = row.find("|", 1) + 1
    assert mod.violations(swap_row(lines, i, row[:j] + " a\\|b " + row[j:])) == []


def test_the_real_file_actually_exercises_escaped_pipes():
    """Guards the test above from becoming decorative: if no real row carried `\\|`, the escaping rule
    would be untested by the tree and free to rot."""
    assert sum(1 for line in real_lines() if line.startswith("|") and "\\|" in line) > 0


def test_the_parser_is_imported_not_vendored():
    """A second copy of split_pipe_row is a second escaping rule that drifts silently."""
    import verify_open_items_restructure as vor

    assert mod.split_pipe_row is vor.split_pipe_row
    assert Path(vor.__file__).resolve() == PARSER


def executable_text(path: Path) -> str:
    """The file with comments and string literals (so, docstrings) removed. A raw substring search
    cannot express "not in the CODE" -- this test's first version failed on the checker's own
    docstring, which names the pin precisely in order to explain why it is excluded. Prose that
    names a thing and code that reaches it are different claims."""
    import io
    import tokenize

    kept = []
    for token in tokenize.generate_tokens(io.StringIO(path.read_text(encoding="utf-8")).readline):
        if token.type not in (tokenize.COMMENT, tokenize.STRING):
            kept.append(token.string)
    return " ".join(kept)


def test_the_ratchet_is_not_reachable_from_the_checker():
    """THE EXCLUSION IS ASSERTED, not just documented. A hand-maintained count pin fails the admitting
    rule, so no pin may be reachable from the extracted check -- otherwise wiring this file quietly
    wires the pin too. Measured on the executable text, and the positive control below proves that
    stripping the docstrings did not strip the test's power."""
    code = executable_text(CHECKER)
    for pin in ("OVER_LIMIT_PINNED", "LONGEST_LINE_PINNED", "LONG_LINE_BYTES"):
        assert pin not in code, f"{pin} is reachable from the extracted check"
    for pin in ("OVER_LIMIT_PINNED", "LONGEST_LINE_PINNED", "LONG_LINE_BYTES"):
        assert not hasattr(mod, pin)
    # The import surface too: importing the parser must not drag the pin in as a module attribute.
    import verify_open_items_restructure as vor

    assert not hasattr(vor, "OVER_LIMIT_PINNED"), "the pin became module-level and is now importable"


def test_the_ratchet_detector_can_actually_fire():
    """POSITIVE CONTROL for the test above. `executable_text` strips strings; if it stripped too much
    the assertion would pass on a checker that really did carry a pin. These names ARE in the parser's
    code, so a detector that cannot see them is broken."""
    code = executable_text(PARSER)
    for pin in ("OVER_LIMIT_PINNED", "LONGEST_LINE_PINNED", "LONG_LINE_BYTES"):
        assert pin in code, f"{pin} not found in verify_open_items_restructure.py's code"


def test_a_file_with_no_table_is_reported_not_crashed():
    assert len(mod.violations("no table here\n")) == 1


# --------------------------------------------------------------------------------------------------
# End to end against a real index.
# --------------------------------------------------------------------------------------------------
def scratch_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "docs" / "open-items").mkdir(parents=True)
    shutil.copy(OPEN_ITEMS, root / "docs" / "OPEN_ITEMS.md")
    for name in (CHECKER.name, PARSER.name):
        shutil.copy(HERE / name, root / "docs" / "open-items" / name)
    # A second TRACKED file, so the attribution arms can commit by pathspec. A pathspec naming an
    # untracked path makes git refuse before the hook runs -- which the first version of those arms
    # mistook for the hook blocking the commit.
    (root / "other.txt").write_text("v1\n", encoding="utf-8")
    for args in (
        ["init", "-q", "."],
        ["add", "-A"],
        ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base"],
    ):
        assert subprocess.run(["git", *args], cwd=root, capture_output=True).returncode == 0
    return root


def run_checker(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "docs/open-items/check_open_items_columns.py", *args],
        cwd=root, capture_output=True, text=True,
    )


def malform(root: Path) -> None:
    path = root / "docs" / "OPEN_ITEMS.md"
    lines = path.read_text(encoding="utf-8").split("\n")
    i = [n for n, l in enumerate(lines) if l.startswith("|")][2]
    j = lines[i].find("|", 1) + 1
    lines[i] = lines[i][:j] + " a|b " + lines[i][j:]
    path.write_text("\n".join(lines), encoding="utf-8")


def test_end_to_end_clean_index_exits_zero(tmp_path):
    root = scratch_repo(tmp_path)
    done = run_checker(root, "--check")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "OK" in done.stdout and "115" in done.stdout


def test_end_to_end_staged_malformation_exits_one(tmp_path):
    root = scratch_repo(tmp_path)
    malform(root)
    subprocess.run(["git", "add", "docs/OPEN_ITEMS.md"], cwd=root, capture_output=True)
    done = run_checker(root, "--check")
    assert done.returncode == 1, done.stdout + done.stderr
    assert "8 fields" in done.stdout


def test_an_unstaged_malformation_does_not_block_the_index(tmp_path):
    """THE SHARED-CHECKOUT CASE, and the reason `--check` reads the index. Three lanes commit through
    one tree; a worktree read would let lane A's uncommitted edit block lane B's unrelated commit,
    which is the admitting rule failing from the direction that matters. `--worktree` still sees it."""
    root = scratch_repo(tmp_path)
    malform(root)  # on disk only -- never staged
    assert run_checker(root, "--check").returncode == 0
    disk = run_checker(root, "--worktree")
    assert disk.returncode == 1 and "8 fields" in disk.stdout


def test_self_test_passes_on_a_clean_tree(tmp_path):
    root = scratch_repo(tmp_path)
    done = run_checker(root, "--self-test")
    assert done.returncode == 0, done.stdout + done.stderr


# --------------------------------------------------------------------------------------------------
# ATTRIBUTION. Added after a peer objected that reading the index only NARROWS the shared-checkout
# hole rather than closing it: a STAGED row is uncommitted too, so a pathspec commit would be refused
# over a row it does not contain. The objection is sound in form; the prediction does not reproduce,
# and these arms are why. Nothing above covers "the path is staged by someone else and is absent from
# this commit" -- the suite was strong on malformation SHAPES and silent on WHOSE row it is.
#
# They run the checker as a REAL installed pre-commit hook, because the whole question is what the
# hook process sees: git hands a partial commit a temporary index through GIT_INDEX_FILE, and that is
# invisible to any probe run outside the hook.
# --------------------------------------------------------------------------------------------------
HOOK_BODY = """#!/bin/bash
cd "$(git rev-parse --show-toplevel)" || exit 2
exec python3 docs/open-items/check_open_items_columns.py --check
"""


def install_hook(root: Path) -> None:
    hook = root / ".git" / "hooks" / "pre-commit"
    hook.write_text(HOOK_BODY, encoding="utf-8")
    hook.chmod(0o755)


def commit(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-c", "user.name=a", "-c", "user.email=a@a", "commit", *args],
        cwd=root, capture_output=True, text=True,
    )


def peer_stages_a_malformed_row(root: Path) -> None:
    """Lane B's edit, staged into the shared index. Lane A never touched this file."""
    malform(root)
    subprocess.run(["git", "add", "docs/OPEN_ITEMS.md"], cwd=root, capture_output=True)


def test_a_pathspec_commit_is_not_blocked_by_another_lanes_staged_row(tmp_path):
    """THE PEER'S ARM: fires-and-should-not, if it fired. It does not. Git builds a temporary index
    for a partial commit and exports it as GIT_INDEX_FILE, so the hook reads what the commit will
    record -- lane B's staged row is simply not in it."""
    root = scratch_repo(tmp_path)
    install_hook(root)
    peer_stages_a_malformed_row(root)
    (root / "other.txt").write_text("lane A's own work\n", encoding="utf-8")

    done = commit(root, "-m", "lane A, unrelated", "--", "other.txt")
    assert done.returncode == 0, "an innocent pathspec commit was blocked:\n" + done.stdout + done.stderr

    # And the commit really does exclude the malformed row -- otherwise passing would be the bug.
    recorded = subprocess.run(
        ["git", "show", "HEAD:docs/OPEN_ITEMS.md"], cwd=root, capture_output=True, text=True
    ).stdout
    assert mod.violations(recorded) == []


def test_git_gives_a_partial_commit_its_own_index(tmp_path):
    """PINS THE GIT BEHAVIOUR THE ARM ABOVE DEPENDS ON. The correctness of the pathspec case is not a
    property of this check -- it is a property of git. If a future git stops exporting a temporary
    index, the false block returns and the test above would still pass for the wrong reason until it
    didn't. Fail loudly here instead."""
    root = scratch_repo(tmp_path)
    probe = root / ".git" / "hooks" / "pre-commit"
    probe.write_text(
        '#!/bin/bash\ncd "$(git rev-parse --show-toplevel)" || exit 2\n'
        '{ echo "INDEX=${GIT_INDEX_FILE:-<unset>}"; '
        'echo "STAGED=$(git diff --cached --name-only | tr \'\\n\' \' \')"; } > probe.out\n'
        "exit 0\n",
        encoding="utf-8",
    )
    probe.chmod(0o755)
    peer_stages_a_malformed_row(root)
    (root / "other.txt").write_text("lane A\n", encoding="utf-8")
    commit(root, "-m", "partial", "--", "other.txt")

    seen = (root / "probe.out").read_text(encoding="utf-8")
    assert "next-index" in seen, f"git no longer isolates a partial commit's index:\n{seen}"
    assert "docs/OPEN_ITEMS.md" not in seen, f"the peer's row leaked into the partial index:\n{seen}"


def test_scrubbing_git_index_file_reintroduces_the_false_block(tmp_path):
    """NEGATIVE CONTROL for the two arms above, and the reason they are not vacuous. The pathspec case
    is correct only because this module inherits GIT_INDEX_FILE; that inheritance is invisible in the
    source -- there is no line to read -- so a future author could scrub the environment "for
    hygiene" and silently restore the false block. Drop the variable and the innocent pathspec commit
    IS refused. If this test ever passes-by-not-blocking, the arms above prove nothing."""
    root = scratch_repo(tmp_path)
    target = root / "docs" / "open-items" / CHECKER.name
    text = target.read_text(encoding="utf-8")
    anchor = "def read_index() -> str:\n"
    assert anchor in text
    target.write_text(
        text.replace(anchor, anchor + '    import os as _os; _os.environ.pop("GIT_INDEX_FILE", None)\n', 1),
        encoding="utf-8",
    )
    install_hook(root)
    peer_stages_a_malformed_row(root)
    (root / "other.txt").write_text("lane A's own work\n", encoding="utf-8")

    done = commit(root, "-m", "lane A, unrelated", "--", "other.txt")
    assert done.returncode != 0, "scrubbing GIT_INDEX_FILE no longer changes the outcome"
    assert "8 fields" in done.stdout + done.stderr


def test_a_plain_commit_is_blocked_and_the_block_is_correct(tmp_path):
    """THE RESIDUAL, and it is NOT a false block. With no pathspec the commit really would contain the
    peer's row -- measured, not assumed -- so refusing it is the check working. On a shared checkout a
    no-pathspec `git commit` commits the other lane's staged work; this makes that loud."""
    root = scratch_repo(tmp_path)
    peer_stages_a_malformed_row(root)
    (root / "other.txt").write_text("lane A\n", encoding="utf-8")
    subprocess.run(["git", "add", "other.txt"], cwd=root, capture_output=True)

    assert run_checker(root, "--check").returncode == 1

    # Prove the block is right: with the hook OFF, the commit does carry the malformed row.
    done = commit(root, "-m", "plain, no pathspec", "--no-verify")
    assert done.returncode == 0, done.stdout + done.stderr
    recorded = subprocess.run(
        ["git", "show", "HEAD:docs/OPEN_ITEMS.md"], cwd=root, capture_output=True, text=True
    ).stdout
    assert mod.violations(recorded) != [], "the block would have been spurious"


def test_the_failure_message_does_not_misdirect_the_committer(tmp_path):
    """A blocked author reading only "6 fields, expected 7" hunts for their own mistake. When the row
    is another lane's, that search is unbounded and the check has cost more than it saved."""
    root = scratch_repo(tmp_path)
    peer_stages_a_malformed_row(root)
    out = run_checker(root, "--check").stdout.lower()
    assert "git diff --cached" in out
    assert "another lane" in out
    assert "pathspec" in out
    assert "--no-verify" in out


def test_the_worktree_mode_carries_no_index_advice(tmp_path):
    """The advice is index-specific; printing it in --worktree mode would be false. The other-lane
    story does not apply to a file you are editing on disk."""
    root = scratch_repo(tmp_path)
    malform(root)
    out = run_checker(root, "--worktree").stdout
    assert "8 fields" in out
    assert "git diff --cached" not in out


# --------------------------------------------------------------------------------------------------
# Layer 2 -- mutation tests. These are the ones that make layer 1 mean something.
# --------------------------------------------------------------------------------------------------
def mutated_checker(tmp_path: Path, old: str, new: str) -> subprocess.CompletedProcess:
    root = scratch_repo(tmp_path)
    target = root / "docs" / "open-items" / CHECKER.name
    text = target.read_text(encoding="utf-8")
    assert old in text, f"mutation anchor not found: {old!r}"
    target.write_text(text.replace(old, new, 1), encoding="utf-8")
    return run_checker(root, "--self-test")


def test_self_test_catches_a_dead_width_rule(tmp_path):
    done = mutated_checker(tmp_path, "        if len(cells) != WIDTH:", "        if False:")
    assert done.returncode == 1
    assert "DROPPED delimiter" in done.stdout and "UNESCAPED pipe" in done.stdout


def test_self_test_catches_a_one_directional_guard(tmp_path):
    """`b2d7d4ca`'s shape: the guard fires on the short side and waves the long side through, and the
    gate exits 0. If the self-test only ever built a short row this mutation would survive."""
    done = mutated_checker(tmp_path, "        if len(cells) != WIDTH:", "        if len(cells) < WIDTH:")
    assert done.returncode == 1
    assert "UNESCAPED pipe" in done.stdout


def test_self_test_catches_the_opposite_one_directional_guard(tmp_path):
    done = mutated_checker(tmp_path, "        if len(cells) != WIDTH:", "        if len(cells) > WIDTH:")
    assert done.returncode == 1
    assert "DROPPED delimiter" in done.stdout


def test_self_test_catches_a_deleted_header_assert(tmp_path):
    done = mutated_checker(tmp_path, "    if cells != HEADER:", "    if False:")
    assert done.returncode == 1
    assert "RENAMED header" in done.stdout and "REORDERED header" in done.stdout


def test_self_test_catches_an_always_failing_check(tmp_path):
    """The other way a guard is useless: it fires on everything, including a good tree. That check
    trains lanes to --no-verify, which is what the dispatcher's two standing exclusions exist to
    avoid."""
    done = mutated_checker(tmp_path, "    rows = table_rows(text)\n    if len(rows) < 3:",
                           "    rows = table_rows(text)\n    if True:")
    assert done.returncode == 1
    assert "passes untouched" in done.stdout
