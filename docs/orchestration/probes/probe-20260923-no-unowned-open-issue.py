#!/usr/bin/env python3
"""No unowned open issue: every OPEN row of KNOWN_ISSUES.md carries a named blocker.

    probe-20260923-no-unowned-open-issue.py [--self-test]

The goal condition Joseph added on 2026-09-23: every OPEN row is either fixed and closed with evidence,
or carries a named blocker. The format was agreed with the known-issues session on 2026-09-23. It is one
line, starting at column 0, in the row's detail file when the row links one (`docs/known-issues/...`),
and otherwise in the row's own text:

    **Blocker:** D7 — <the work-order limit>
    **Blocker:** JOSEPH — <the decision reserved to him>
    **Blocker:** OWNER — <the lane or author who must act>

The check refuses (exit 1), listing each case:
  * an OPEN row with no blocker line;
  * a blocker line whose kind is not D7, JOSEPH or OWNER, or whose text after the dash is empty;
  * a row whose status is not OPEN but still carries a blocker line (a fixed row still claiming a blocker);
  * a status word it does not recognise;
  * an id used by more than one row;
  * a linked detail file that does not exist.
Exit 0 = none of these. Exit 2 = it could not read the index.

It reads the tables with markdown-it-py, as GitHub does. It does NOT judge whether a blocker is TRUE; a
human does. It judges only that each open row names one.
"""
import os
import re
import subprocess
import sys

try:
    from markdown_it import MarkdownIt
except ImportError:
    print("[owned] CANNOT LOOK :: markdown-it-py is not installed")
    sys.exit(2)

STATUSES = ("OPEN", "FIXED", "CLOSED", "RESOLVED", "WONTFIX", "RETRACTED", "DETECTION")
BLOCKER = re.compile(r"^\*\*Blocker:\*\*\s+(\S+)\s+—\s*(.*)$")
BLOCKER_ANY = re.compile(r"\*\*Blocker:\*\*|(?<!\w)Blocker:\s")
LINK = re.compile(r"\]\((docs/known-issues/[^)\s]+)\)")


def rows_of(text):
    """(id, status, cells-as-source, line) for every body row of every table whose header begins `id`."""
    md = MarkdownIt("commonmark").enable(["table"])
    toks = md.parse(text)
    lines = text.split("\n")
    out, i = [], 0
    while i < len(toks):
        if toks[i].type != "table_open":
            i += 1
            continue
        header, body, cur, j = None, [], None, i + 1
        while toks[j].type != "table_close":
            t = toks[j]
            if t.type == "tr_open":
                cur = (t.map[0] if t.map else None, [])
            elif t.type == "inline" and cur is not None:
                cur[1].append(t.content)
            elif t.type == "tr_close" and cur is not None:
                (body.append(cur) if header is not None else None)
                header = header if header is not None else cur[1]
                cur = None
            j += 1
        if header and header[0].strip().lower() == "id":
            for ln, cells in body:
                if len(cells) < 3:
                    continue
                out.append((cells[0].strip(), cells[2], cells, (ln or 0) + 1, lines[ln] if ln is not None else ""))
        i = j + 1
    return out


def check(text, exists=os.path.exists, read=lambda p: open(p, encoding="utf-8").read()):
    problems, seen = [], {}
    for rid, status, cells, line, raw in rows_of(text):
        seen.setdefault(rid, []).append(line)
        word = re.sub(r"[*`_]", "", status).strip().split(" ")[0].upper().rstrip(".,—-")
        if word not in STATUSES:
            problems.append(f"line {line}: id {rid}: status word {word!r} is not one of {', '.join(STATUSES)}")
            continue
        m = LINK.search(raw)
        if m:
            path = m.group(1)
            if not exists(path):
                problems.append(f"line {line}: id {rid}: links {path}, which does not exist")
                continue
            source, where = read(path), path
        else:
            source, where = raw, "its index row"
        if m:
            blockers = [BLOCKER.match(l) for l in source.split("\n") if l.startswith("**Blocker:**")]
            stray = [l for l in source.split("\n") if BLOCKER_ANY.search(l) and not l.startswith("**Blocker:**")]
        else:
            blockers = [BLOCKER.match(s.strip()) for s in re.findall(r"\*\*Blocker:\*\*[^|]*", source)]
            stray = []
        for b in blockers:
            if b is None or b.group(1) not in ("D7", "JOSEPH", "OWNER") or not b.group(2).strip():
                problems.append(f"line {line}: id {rid}: a malformed blocker line in {where}")
        for s in stray:
            problems.append(f"line {line}: id {rid}: a blocker not at column 0 in {where}: {s.strip()[:60]!r}")
        good = [b for b in blockers if b and b.group(1) in ("D7", "JOSEPH", "OWNER") and b.group(2).strip()]
        if word == "OPEN" and not good:
            problems.append(f"line {line}: id {rid}: OPEN with no blocker line in {where} (UNOWNED)")
        if word != "OPEN" and blockers:
            problems.append(f"line {line}: id {rid}: status {word} but {where} still carries a blocker line")
    for rid, where in seen.items():
        if len(where) > 1:
            problems.append(f"id {rid} is used by {len(where)} rows (lines {', '.join(map(str, where))})")
    return problems


def self_test():
    head = "| id | severity | status | one-sentence failure | detail | updated |\n|---|---|---|---|---|---|\n"
    files = {"docs/known-issues/ISSUE-2-x.md": "# x\n\n**Blocker:** JOSEPH — the hook is his\n",
             "docs/known-issues/ISSUE-3-x.md": "# x\n\nno blocker here\n",
             "docs/known-issues/ISSUE-4-x.md": "# x\n\n**Blocker:** MAYBE — someone\n",
             "docs/known-issues/ISSUE-5-x.md": "# x\n\n  **Blocker:** OWNER — indented\n"}
    ex, rd = (lambda p: p in files), (lambda p: files[p])
    shapes = [  # (name, table rows, how many problems wanted)
        ("OPEN row, blocker in its text", "| 1 | LOW | OPEN | x **Blocker:** OWNER — lane B | row | d |\n", 0),
        ("OPEN row, blocker in its detail file", "| 2 | LOW | OPEN | x | [d](docs/known-issues/ISSUE-2-x.md) | d |\n", 0),
        ("OPEN row, detail file with no blocker", "| 3 | LOW | OPEN | x | [d](docs/known-issues/ISSUE-3-x.md) | d |\n", 1),
        ("OPEN row, no blocker anywhere", "| 1 | LOW | OPEN | x | row | d |\n", 1),
        ("blocker of an unknown kind", "| 4 | LOW | OPEN | x | [d](docs/known-issues/ISSUE-4-x.md) | d |\n", 2),
        ("blocker not at column 0", "| 5 | LOW | OPEN | x | [d](docs/known-issues/ISSUE-5-x.md) | d |\n", 2),
        ("FIXED row still carrying a blocker", "| 1 | LOW | FIXED 2026-09-23 at abc | x **Blocker:** D7 — y | row | d |\n", 1),
        ("FIXED row without a blocker", "| 1 | LOW | FIXED 2026-09-23 at abc | x | row | d |\n", 0),
        ("status word unknown", "| 1 | LOW | PENDING | x | row | d |\n", 1),
        ("duplicate id", "| 1 | LOW | FIXED | x | row | d |\n| 1 | LOW | FIXED | y | row | d |\n", 1),
        ("detail file missing", "| 6 | LOW | OPEN | x | [d](docs/known-issues/ISSUE-6-x.md) | d |\n", 1),
        ("blocker with empty text", "| 1 | LOW | OPEN | x **Blocker:** OWNER — | row | d |\n", 2),
        ("status in bold, OPEN with a qualifier", "| 1 | LOW | **OPEN — DO NOT FIX** | x **Blocker:** D7 — z | row | d |\n", 0),
    ]
    wrong = []
    for name, body, want in shapes:
        got = check(head + body, ex, rd)
        if len(got) != want:
            wrong.append(f"{name}: wanted {want} problem(s), got {len(got)}: {got}")
    for w in wrong:
        print(f"  *** WRONG *** {w}")
    print(f"[owned self-test] {'FAIL' if wrong else 'PASS'} :: {len(shapes)} shapes")
    return 1 if wrong else 0


def main():
    if "--self-test" in sys.argv:
        return self_test()
    root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
    if not root:
        print("[owned] CANNOT LOOK :: not inside a git work tree")
        return 2
    os.chdir(root)
    try:
        text = open("KNOWN_ISSUES.md", encoding="utf-8").read()
    except OSError as e:
        print(f"[owned] CANNOT LOOK :: {e}")
        return 2
    rows = rows_of(text)
    if not rows:
        print("[owned] CANNOT LOOK :: no issue rows parsed")
        return 2
    problems = check(text)
    for p in problems:
        print(f"  {p}")
    n_open = sum(1 for r in rows if re.sub(r"[*`_]", "", r[1]).strip().upper().startswith("OPEN"))
    print(f"\n[owned] {'FAIL' if problems else 'PASS'} :: {len(rows)} rows, {n_open} OPEN, {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
