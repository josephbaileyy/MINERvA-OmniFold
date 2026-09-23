#!/usr/bin/env python3
"""No unowned open issue: every OPEN row of KNOWN_ISSUES.md carries a named blocker.

    probe-20260923-no-unowned-open-issue.py [--self-test]

The goal condition Joseph added on 2026-09-23: every OPEN row is either fixed and closed with evidence,
or carries a named blocker. The format was agreed with the known-issues session on 2026-09-23. It is a
paragraph of its own beginning with a bold `Blocker:`, in the detail file the row's DETAIL cell links
(`docs/known-issues/...`), and otherwise anywhere in the row's own cells:

    **Blocker:** D7 — <the work-order limit>
    **Blocker:** JOSEPH — <the decision reserved to him>
    **Blocker:** OWNER — <the lane or author who must act>

The check refuses (exit 1), listing each case:
  * an OPEN row with no blocker;
  * a blocker whose kind is not D7, JOSEPH or OWNER, or whose text after the dash is empty;
  * a blocker in a detail file that is not its own top-level paragraph (inside a blockquote or a list);
  * a row whose status is not OPEN but still carries a blocker (a fixed row still claiming a blocker);
  * a status that does not begin with OPEN, FIXED, CLOSED, RESOLVED, WONTFIX or RETRACTED;
  * an id, as rendered, used by more than one row;
  * a detail cell linking a `docs/known-issues/` file that does not exist.
Exit 0 = none of these. Exit 2 = it could not read the index.

It reads the index AND the detail files with markdown-it-py, as GitHub renders them: a blocker inside a
code block, a code span or an HTML comment is not a blocker (⚠ the first version matched raw strings, took
the first `docs/known-issues/` link anywhere in the row, and misread `#anchor` and `./` links; review
#21b). It does NOT judge whether a blocker is TRUE; a human does. It judges only that each open row names one.
"""
import os
import re
import subprocess
import sys
from urllib.parse import unquote

try:
    from markdown_it import MarkdownIt
except ImportError:
    print("[owned] CANNOT LOOK :: markdown-it-py is not installed")
    sys.exit(2)

# ⚠ No `DETECTION`: it once sat here only so that row 52 ("DETECTION FIXED …; RESIDUAL BELOW") parsed, which
# exempted an issue that still has open residuals and said so nowhere (review #21b). A status is one of these.
STATUSES = ("OPEN", "FIXED", "CLOSED", "RESOLVED", "WONTFIX", "RETRACTED")
KINDS = ("D7", "JOSEPH", "OWNER")
BLOCKER_TEXT = re.compile(r"^\s+(\S+)\s+\u2014\s*(.*)$", re.S)     # after the bold `Blocker:`: " KIND — text"
MD = MarkdownIt("commonmark").enable(["table"])


def visible(inline):
    """What a reader sees of an inline token: text and code, never raw HTML."""
    return "".join(c.content for c in (inline.children or []) if c.type in ("text", "code_inline")).strip()


def blockers_in_inline(inline):
    """(kind, text) for each bold `Blocker:` in this inline token, as RENDERED -- not raw source, so a blocker
    inside a code span or an HTML comment is not one (review #21b)."""
    ch, out, k = inline.children or [], [], 0
    while k < len(ch):
        if (ch[k].type == "strong_open" and k + 2 < len(ch) and ch[k + 1].type == "text"
                and ch[k + 1].content.strip() == "Blocker:" and ch[k + 2].type == "strong_close"):
            j, rest = k + 3, []
            while j < len(ch) and ch[j].type in ("text", "code_inline", "softbreak") and not (
                    ch[j].type == "text" and "Blocker:" in ch[j].content):
                rest.append(" " if ch[j].type == "softbreak" else ch[j].content)
                j += 1
            m = BLOCKER_TEXT.match("".join(rest))
            out.append((m.group(1), m.group(2).strip()) if m else (None, ""))
            k = j
        else:
            k += 1
    return out


def detail_blockers(text):
    """(top-level blockers, nested blockers) in a detail file, read from its markdown-it parse. A blocker counts
    only as its own top-level paragraph; one in a blockquote or list is nested (flagged); one in a code block or
    an HTML comment is not rendered as a blocker at all, so it is ignored (review #21b)."""
    top, nested = [], []
    toks = MD.parse(text)
    for i, tk in enumerate(toks):
        if tk.type != "inline" or not tk.children:
            continue
        found = blockers_in_inline(tk)
        if not found:
            continue
        ch = [c for c in tk.children if not (c.type == "text" and not c.content.strip())]   # markdown-it leads with ''
        starts = len(ch) > 1 and ch[0].type == "strong_open" and ch[1].content.strip() == "Blocker:"
        para_top = i > 0 and toks[i - 1].type == "paragraph_open" and toks[i - 1].level == 0
        (top if (starts and para_top) else nested).extend(found)
    return top, nested


def detail_href(cell_inline):
    """The FIRST link in the DETAIL cell, as markdown-it resolves it (so `<…>`, a title and `%20` are handled),
    normalised: anchor and query dropped, `./` removed. The whole row was once searched, so a row citing another
    issue's detail file inherited that issue's blocker (review #21b)."""
    for c in cell_inline.children or []:
        if c.type == "link_open":
            href = unquote(c.attrs.get("href", ""))
            return os.path.normpath(re.split(r"[#?]", href)[0])
    return None


def rows_of(text):
    """(id, status, detail-cell inline, all cell inlines, line) for every body row of every table whose header
    begins `id`. The id is compared as RENDERED, so `**46**` and `46` are one id (review #21b)."""
    toks = MD.parse(text)
    out, i = [], 0
    while i < len(toks):
        if toks[i].type != "table_open":
            i += 1
            continue
        header, j, cur = None, i + 1, None
        while toks[j].type != "table_close":
            tk = toks[j]
            if tk.type == "tr_open":
                cur = (tk.map[0] if tk.map else 0, [])
            elif tk.type == "inline" and cur is not None:
                cur[1].append(tk)
            elif tk.type == "tr_close" and cur is not None:
                if header is None:
                    header = [visible(c).lower() for c in cur[1]]
                elif header and header[0] == "id" and len(cur[1]) >= 5:
                    cells = cur[1]
                    out.append((visible(cells[0]), visible(cells[2]), cells[4], cells, cur[0] + 1))
                cur = None
            j += 1
        i = j + 1
    return out


def status_word(status):
    return status.strip().split(" ")[0].upper().rstrip(".,")


def check(text, exists=os.path.exists, read=lambda p: open(p, encoding="utf-8").read()):
    problems, seen = [], {}
    for rid, status, detail, cells, line in rows_of(text):
        seen.setdefault(rid, []).append(line)
        word = status_word(status)
        if word not in STATUSES:
            problems.append(f"line {line}: id {rid}: status {status[:40]!r} does not begin with one of {', '.join(STATUSES)}")
            continue
        href = detail_href(detail)
        if href and href.startswith("docs/known-issues/"):
            if not exists(href):
                problems.append(f"line {line}: id {rid}: its detail cell links {href}, which does not exist")
                continue
            blockers, nested = detail_blockers(read(href))
            where = href
            for k_, t_ in nested:
                problems.append(f"line {line}: id {rid}: a blocker in {where} that is not its own top-level paragraph")
        else:
            blockers = [b for c in cells for b in blockers_in_inline(c)]
            where = "its index row"
        for k_, t_ in blockers:
            if k_ not in KINDS or not t_:
                problems.append(f"line {line}: id {rid}: a malformed blocker in {where} (kind {k_!r}, text {t_[:20]!r})")
        good = [b for b in blockers if b[0] in KINDS and b[1]]
        if word == "OPEN" and not good:
            problems.append(f"line {line}: id {rid}: OPEN with no blocker in {where} (UNOWNED)")
        if word != "OPEN" and blockers:
            problems.append(f"line {line}: id {rid}: status {word} but {where} still carries a blocker")
    for rid, where in seen.items():
        if len(where) > 1:
            problems.append(f"id {rid} is used by {len(where)} rows (lines {', '.join(map(str, where))})")
    return problems


def self_test():
    head = "| id | severity | status | one-sentence failure | detail | updated |\n|---|---|---|---|---|---|\n"
    files = {"docs/known-issues/ISSUE-2-x.md": "# x\n\n**Blocker:** JOSEPH — the hook is his\n",
             "docs/known-issues/ISSUE-3-x.md": "# x\n\nno blocker here\n",
             "docs/known-issues/ISSUE-4-x.md": "# x\n\n**Blocker:** MAYBE — someone\n",
             "docs/known-issues/ISSUE-5-x.md": "# x\n\n> **Blocker:** OWNER — in a blockquote\n",
             "docs/known-issues/ISSUE-7-x.md": "# x\n\n```\n**Blocker:** OWNER — in a fence\n```\n",
             "docs/known-issues/ISSUE-8-x.md": "# x\n\n<!--\n**Blocker:** OWNER — in a comment\n-->\n",
             "docs/known-issues/ISSUE-9-x.md": "# x\n\n  **Blocker:** OWNER — indented two spaces, still a paragraph\n",
             "docs/known-issues/ISSUE-10-x.md": "# x\n\nThe row had no Blocker: field before.\n"}
    ex, rd = (lambda p: p in files), (lambda p: files[p])
    link = lambda n: f"[d](docs/known-issues/ISSUE-{n}-x.md)"
    shapes = [  # (name, body -- rows or a whole document --, problems wanted)
        ("OPEN row, blocker in its text", "| 1 | LOW | OPEN | x **Blocker:** OWNER — lane B | row | d |\n", 0),
        ("OPEN row, blocker in its detail file", f"| 2 | LOW | OPEN | x | {link(2)} | d |\n", 0),
        ("OPEN row, detail file with no blocker", f"| 3 | LOW | OPEN | x | {link(3)} | d |\n", 1),
        ("OPEN row, no blocker anywhere", "| 1 | LOW | OPEN | x | row | d |\n", 1),
        ("blocker of an unknown kind", f"| 4 | LOW | OPEN | x | {link(4)} | d |\n", 2),
        ("blocker inside a blockquote", f"| 5 | LOW | OPEN | x | {link(5)} | d |\n", 2),
        ("blocker only inside a code fence", f"| 7 | LOW | OPEN | x | {link(7)} | d |\n", 1),
        ("blocker only inside an HTML comment", f"| 8 | LOW | OPEN | x | {link(8)} | d |\n", 1),
        ("blocker indented two spaces (renders as a paragraph)", f"| 9 | LOW | OPEN | x | {link(9)} | d |\n", 0),
        ("FIXED row whose detail prose says 'Blocker:'", f"| 10 | LOW | FIXED | x | {link(10)} | d |\n", 0),
        ("FIXED row still carrying a blocker", "| 1 | LOW | FIXED 2026-09-23 at abc | x **Blocker:** D7 — y | row | d |\n", 1),
        ("FIXED row without a blocker", "| 1 | LOW | FIXED 2026-09-23 at abc | x | row | d |\n", 0),
        ("status word unknown", "| 1 | LOW | PENDING | x | row | d |\n", 1),
        ("status DETECTION FIXED is not a status", "| 1 | LOW | DETECTION FIXED | x | row | d |\n", 1),
        ("lowercase open still needs a blocker", "| 1 | LOW | open | x | row | d |\n", 1),
        ("OPEN. with a full stop still needs a blocker", "| 1 | LOW | OPEN. | x | row | d |\n", 1),
        # shapes whose count DIFFERS under the mutation they pin -- the three above give 1 either way (review #21b)
        ("lowercase fixed is a status", "| 1 | LOW | fixed | x | row | d |\n", 0),
        ("FIXED. with a full stop is a status", "| 1 | LOW | FIXED. | x | row | d |\n", 0),
        ("an unknown status is reported once, not also as a stray blocker",
         "| 1 | LOW | PENDING | x **Blocker:** OWNER — y | row | d |\n", 1),
        ("duplicate id", "| 1 | LOW | FIXED | x | row | d |\n| 1 | LOW | FIXED | y | row | d |\n", 1),
        ("duplicate id, one in bold", "| 1 | LOW | FIXED | x | row | d |\n| **1** | LOW | FIXED | y | row | d |\n", 1),
        ("detail file missing", "| 6 | LOW | OPEN | x | [d](docs/known-issues/ISSUE-6-x.md) | d |\n", 1),
        ("detail link with an anchor", "| 2 | LOW | OPEN | x | [d](docs/known-issues/ISSUE-2-x.md#blocker) | d |\n", 0),
        ("detail link with ./ and angle brackets", "| 2 | LOW | OPEN | x | [d](<./docs/known-issues/ISSUE-2-x.md>) | d |\n", 0),
        ("another issue's file cited in the FAILURE cell does not lend its blocker",
         f"| 1 | LOW | OPEN | same class as {link(2)} | [log](nd/RUN_LOG.md) | d |\n", 1),
        ("blocker with empty text", "| 1 | LOW | OPEN | x **Blocker:** OWNER — | row | d |\n", 2),
        ("blocker with a plain hyphen, not an em dash", "| 1 | LOW | OPEN | x **Blocker:** OWNER - lane | row | d |\n", 2),
        ("blocker inside a code span is not a blocker", "| 1 | LOW | OPEN | x `**Blocker:** OWNER — y` | row | d |\n", 1),
        ("status in bold, OPEN with a qualifier", "| 1 | LOW | **OPEN — DO NOT FIX** | x **Blocker:** D7 — z | row | d |\n", 0),
        ("an OPEN row in a SECOND table is checked",
         "| 1 | LOW | FIXED | x | row | d |\n\n## Resolved\n\n" + head + "| 2 | LOW | OPEN | x | row | d |\n", 1),
        ("a table whose header is not `id` is not an index",
         "| 1 | LOW | FIXED | x | row | d |\n\n| name | a | status | b | c | d |\n|---|---|---|---|---|---|\n| z | L | OPEN | x | row | d |\n", 0),
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
    n_open = sum(1 for r in rows if status_word(r[1]) == "OPEN")
    print(f"\n[owned] {'FAIL' if problems else 'PASS'} :: {len(rows)} rows, {n_open} OPEN, {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
