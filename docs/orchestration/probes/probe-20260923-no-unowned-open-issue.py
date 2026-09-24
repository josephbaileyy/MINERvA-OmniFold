#!/usr/bin/env python3
"""No unowned open issue: every OPEN row of KNOWN_ISSUES.md has exactly one line in the blocker registry.

    probe-20260923-no-unowned-open-issue.py [--self-test | --mutations]

`--mutations` applies each single-change mutation in MUTATIONS to a copy of this file and requires the copy's
self-test to FAIL. A claim that "every mutation turns the self-test red" was twice made about a mutation set
that lived only in scratch space, so nobody could re-run it (reviews #22a, #23a); the set is committed here.

The goal condition Joseph added on 2026-09-23: every OPEN row is either fixed and closed with evidence, or
names a blocker. Blockers live in ONE plain file, `docs/known-issues/BLOCKERS.tsv`, one line per OPEN row:

    <id> TAB <D7 | JOSEPH | OWNER> TAB <free text>

Blank lines and lines beginning `#` are ignored. The check refuses (exit 1), listing each case:
  * an OPEN row with no registry line, or with more than one;
  * a registry line naming an id that is not an OPEN row (fixed, or absent from the index);
  * a registry line that is not exactly three tab-separated fields, or whose kind is not D7, JOSEPH or
    OWNER, or whose text is empty;
  * an index status that does not BEGIN, after any bold markers, with a plain status word: OPEN, FIXED,
    CLOSED, RESOLVED, WONTFIX or RETRACTED. Markup before the word (`~~`, `<del>`, a backtick) is refused,
    not interpreted;
  * an index id that is not plain letters and digits, or used by more than one row;
  * a table whose header begins with `id` but is not exactly `id`;
  * a line of the index that begins with `|` but was not parsed as part of any table -- a row cut off by a
    stray blank line, an indent or an unclosed code fence is otherwise never seen (reviews #24b, #26b). This
    FAILS CLOSED on a pipe-led line inside a code block, such as a shell pipeline, which must be rewritten.
    A cut-off row WITHOUT a leading pipe, or inside a blockquote, is not detected; the index always uses
    leading pipes.
Exit 0 = none of these. Exit 2 = it could not read the index.

⚠ WHY A REGISTRY. The first versions read blocker lines written as Markdown, in detail files or index rows.
Independent reviews #21b, #22b and #23b found 6, 7 and 11 defects, most of them about which Markdown forms
a blocker could take (links, emphasis, strikethrough, `<del>`, hard breaks, a second issue's file cited in the
same cell, root-absolute links); the rest were about status vocabulary and self-test power. On the real index
the check was exact at #22b's and #23b's shas, but not at #21b's, where `DETECTION` exempted a row with an open
residual. The SURFACE was the main problem, so it was removed rather than patched a fourth time. (⚠ This said
*"every one about … Markdown forms"* and *"exact on the real index each time"*; review #24a.) Markdown is now parsed only to split the index
table into rows, and only the id and status cells are read. It does NOT judge whether a blocker is TRUE; a
human does.
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

STATUSES = ("OPEN", "FIXED", "CLOSED", "RESOLVED", "WONTFIX", "RETRACTED")
KINDS = ("D7", "JOSEPH", "OWNER")
REGISTRY = "docs/known-issues/BLOCKERS.tsv"
MD = MarkdownIt("commonmark").enable(["table"])
STATUS_RE = re.compile(r"^[\s*_]*([A-Za-z]+)(?![A-Za-z])")     # bold markers, then the word; nothing else first
ID_RE = re.compile(r"^[\s*_]*([A-Za-z0-9]+)[\s*_]*$")


def index_rows(text):
    """(id source, status source, line) for each body row of each table whose header's first cell is `id`, plus a
    list of problems: headers that begin with `id` without being exactly `id`, and `|`-led lines outside every
    parsed table."""
    toks, rows, problems, i = MD.parse(text), [], [], 0
    lines, covered = text.split("\n"), set()
    # ⚠ NO line is excused for sitting in a code block. Excusing FENCED blocks (to stop refusing a shell pipeline,
    # review #25b) let one unclosed ``` hide every row after it -- markdown-it runs an unclosed fence to the end of
    # the file -- so an unowned OPEN row PASSED (review #26b). A false refusal is safe; a false pass is not.
    while i < len(toks):
        if toks[i].type != "table_open":
            i += 1
            continue
        if toks[i].map:
            covered.update(range(toks[i].map[0], toks[i].map[1]))
        header, cur, j = None, None, i + 1
        while toks[j].type != "table_close":
            tk = toks[j]
            if tk.type == "tr_open":
                cur = (tk.map[0] + 1 if tk.map else 0, [])
            elif tk.type == "inline" and cur is not None:
                cur[1].append(tk.content)
            elif tk.type == "tr_close" and cur is not None:
                if header is None:
                    header = cur[1][0].strip().lower() if cur[1] else ""
                    if header != "id" and header.startswith("id"):
                        problems.append(f"line {cur[0]}: a table header begins {cur[1][0]!r}, not exactly `id`")
                elif header == "id" and len(cur[1]) >= 3:
                    rows.append((cur[1][0], cur[1][2], cur[0]))
                cur = None
            j += 1
        i = j + 1
    for n, l in enumerate(lines):          # every `|`-led line must lie inside SOME parsed table (review #24b)
        if l.lstrip().startswith("|") and n not in covered:
            problems.append(f"line {n + 1}: a table-row line that is not part of any parsed table: {l.strip()[:50]!r}")
    return rows, problems


def read_registry(text):
    """{id: [(kind, text, line)]} and a list of problems."""
    reg, problems = {}, []
    text = text[1:] if text.startswith("\ufeff") else text      # a UTF-8 BOM (#24b), stripped where a shape can pin it (#25b)
    for n, line in enumerate(text.split("\n"), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        f = line.split("\t")
        if len(f) != 3:
            problems.append(f"{REGISTRY}:{n}: {len(f)} tab-separated field(s), not 3: {line[:60]!r}")
            continue
        rid, kind, body = f[0].strip(), f[1].strip(), f[2].strip()
        if kind not in KINDS:
            problems.append(f"{REGISTRY}:{n}: id {rid}: kind {kind!r} is not one of {', '.join(KINDS)}")
        if not body:
            problems.append(f"{REGISTRY}:{n}: id {rid}: empty blocker text")
        reg.setdefault(rid, []).append((kind, body, n))
    return reg, problems


def check(index_text, registry_text):
    rows, problems = index_rows(index_text)
    reg, rp = read_registry(registry_text if registry_text is not None else "")
    problems += rp
    open_ids, seen = set(), {}
    for id_src, status_src, line in rows:
        m = ID_RE.match(id_src)
        if not m:
            problems.append(f"line {line}: id {id_src.strip()[:20]!r} is not plain letters and digits")
            continue
        rid = m.group(1)
        seen.setdefault(rid, []).append(line)
        s = STATUS_RE.match(status_src)
        if not s or s.group(1).upper() not in STATUSES:
            problems.append(f"line {line}: id {rid}: status {status_src.strip()[:40]!r} does not begin with a plain "
                            f"status word ({', '.join(STATUSES)})")
            continue
        if s.group(1).upper() == "OPEN":
            open_ids.add(rid)
    for rid, lines in seen.items():
        if len(lines) > 1:
            problems.append(f"id {rid} is used by {len(lines)} rows (lines {', '.join(map(str, lines))})")
    for rid in sorted(open_ids):
        # only a VALID line owns a row: a malformed one is reported, and once also counted as the owner (#24a)
        n = len([e for e in reg.get(rid, []) if e[0] in KINDS and e[1]])
        if n != 1:
            problems.append(f"id {rid}: OPEN with {n} registry line(s) in {REGISTRY}, not 1"
                            + (" (UNOWNED)" if n == 0 else ""))
    for rid, entries in sorted(reg.items()):
        if rid not in open_ids:
            where = "is not an id in the index" if rid not in seen else "is not OPEN"
            problems.append(f"{REGISTRY}:{entries[0][2]}: id {rid!r} {where}, but has a registry line")   # !r: a BOM shows (#26b)
    return problems, len(rows), len(open_ids)


def self_test():
    head = "| id | severity | status | failure | detail | updated |\n|---|---|---|---|---|---|\n"
    shapes = [  # (name, index rows, registry, problems wanted)
        ("OPEN row with one registry line", "| 1 | L | OPEN | x | d | u |\n", "1\tOWNER\tlane B\n", 0),
        ("OPEN row with no registry line", "| 1 | L | OPEN | x | d | u |\n", "", 1),
        ("OPEN row with two registry lines", "| 1 | L | OPEN | x | d | u |\n", "1\tOWNER\ta\n1\tD7\tb\n", 1),
        ("a registry line for a FIXED row", "| 1 | L | FIXED | x | d | u |\n", "1\tOWNER\ta\n", 1),
        ("a registry line for an id not in the index", "| 1 | L | FIXED | x | d | u |\n", "9\tOWNER\ta\n", 1),
        ("an unknown kind: malformed, and the row stays unowned", "| 1 | L | OPEN | x | d | u |\n", "1\tMAYBE\ta\n", 2),
        ("empty blocker text: malformed, and the row stays unowned", "| 1 | L | OPEN | x | d | u |\n", "1\tOWNER\t \n", 2),
        ("two fields, not three", "| 1 | L | OPEN | x | d | u |\n", "1\tOWNER lane B\n", 2),
        ("comments and blank lines are ignored", "| 1 | L | OPEN | x | d | u |\n", "# c\n\n1\tJOSEPH\tt\n", 0),
        ("status in bold with a qualifier", "| 1 | L | **OPEN — DO NOT FIX** | x | d | u |\n", "1\tD7\tt\n", 0),
        ("status FIXED: with a colon, in bold", "| 1 | L | **FIXED:** 2026 at `abc` | x | d | u |\n", "", 0),
        ("lowercase open still needs a line", "| 1 | L | open | x | d | u |\n", "", 1),
        ("status struck with ~~ is refused, not read", "| 1 | L | ~~OPEN~~ FIXED | x | d | u |\n", "", 1),
        ("status in <del> is refused", "| 1 | L | <del>FIXED</del> OPEN | x | d | u |\n", "", 1),
        ("status in a code span is refused", "| 1 | L | `FIXED` | x | d | u |\n", "", 1),
        ("status word unknown", "| 1 | L | PENDING | x | d | u |\n", "", 1),
        ("REOPENED is not OPEN", "| 1 | L | REOPENED | x | d | u |\n", "", 1),
        # counts that DIFFER under the mutation each pins (a count equal either way pins nothing)
        ("OPENED is not OPEN, and its registry line is stray", "| 1 | L | OPENED | x | d | u |\n", "1\tOWNER\ta\n", 2),
        ("lowercase open with its registry line", "| 1 | L | open | x | d | u |\n", "1\tOWNER\ta\n", 0),
        ("four fields, not three", "| 1 | L | OPEN | x | d | u |\n", "1\tOWNER\ta\tb\n", 2),
        ("a bold id is the same id", "| 1 | L | FIXED | x | d | u |\n| **1** | L | FIXED | y | d | u |\n", "", 1),
        ("an id with markup is refused", "| <span>1</span> | L | FIXED | x | d | u |\n", "", 1),
        ("an OPEN row in a SECOND table is checked",
         "| 1 | L | FIXED | x | d | u |\n\n## R\n\n" + head + "| 2 | L | OPEN | x | d | u |\n", "", 1),
        ("a table whose header is not id is not an index",
         "| 1 | L | FIXED | x | d | u |\n\n| name | a | status |\n|---|---|---|\n| z | L | OPEN |\n", "", 0),
        ("a header beginning `id` but not `id` is refused",
         "| 1 | L | FIXED | x | d | u |\n\n| id (x) | a | status |\n|---|---|---|\n| 2 | L | OPEN |\n", "", 1),
        # --- review #24b: the real index's letter ids and status words, and rows the parser would not see
        ("a letter id J36, OPEN with its line", "| J36 | L | OPEN | x | d | u |\n", "J36\tOWNER\ta\n", 0),
        *[(f"status {w} needs no line", f"| 1 | L | {w} 2026 | x | d | u |\n", "", 0)
          for w in ("CLOSED", "RESOLVED", "WONTFIX", "RETRACTED")],
        ("an id with trailing text is refused", "| 51 (reopened) | L | FIXED | x | d | u |\n", "", 1),
        ("spaces around the registry id and kind are accepted", "| 1 | L | OPEN | x | d | u |\n", " 1 \t OWNER \ta\n", 0),
        ("an upper-case ID header is still an index", "", "", 0),
        ("a row cut off by a blank line is refused",
         "| 1 | L | FIXED | x | d | u |\n\n| 2 | L | OPEN | x | d | u |\n", "", 1),
        ("a pipe-led line inside a fenced code block is refused (fail closed)",
         "| 1 | L | FIXED | x | d | u |\n\n```sh\ngrep x f \\\n  | sort\n```\n", "", 1),
        ("an unclosed fence does not hide an OPEN row after it",
         "| 1 | L | FIXED | x | d | u |\n\n```\n\n" + head + "| 2 | L | OPEN | x | d | u |\n", "", 3),
        ("a BOM before a data line", "| 1 | L | OPEN | x | d | u |\n", "\ufeff1\tOWNER\ta\n", 0),
        ("a registry beginning with a UTF-8 BOM", "| 1 | L | OPEN | x | d | u |\n", "\ufeff# c\n1\tOWNER\ta\n", 0),
        ("a row cut off by an indent is refused",
         "| 1 | L | FIXED | x | d | u |\n\n    | 2 | L | OPEN | x | d | u |\n", "", 1),
        ("CRLF registry lines", "| 1 | L | OPEN | x | d | u |\n", "1\tOWNER\ta\r\n", 0),
    ]
    wrong = []
    for name, body, reg, want in shapes:
        doc = (head.replace("| id |", "| ID |", 1) + "| 1 | L | OPEN | x | d | u |\n") if "upper-case ID" in name else head + body
        reg = "1\tOWNER\ta\n" if "upper-case ID" in name else reg
        got, _, _ = check(doc, reg)
        if len(got) != want:
            wrong.append(f"{name}: wanted {want} problem(s), got {len(got)}: {got}")
    for w in wrong:
        print(f"  *** WRONG *** {w}")
    print(f"[owned self-test] {'FAIL' if wrong else 'PASS'} :: {len(shapes)} shapes")
    return 1 if wrong else 0


# (label, text in this file, replacement). Each must make the self-test fail. `--mutations` refuses (exit 2) if a
# text is not found exactly once, so a mutation cannot silently stop applying when the code moves.
MUTATIONS = [
    ("the registry-count check dropped", "        if n != 1:\n", "        if False:\n"),
    ("more than one line accepted", "        if n != 1:\n", "        if n == 0:\n"),
    ("stray registry lines accepted", "        if rid not in open_ids:\n", "        if False:\n"),
    ("any kind accepted", "        if kind not in KINDS:\n", "        if False:\n"),
    ("empty text accepted", "        if not body:\n", "        if False:\n"),
    ("a fourth field accepted", "        if len(f) != 3:\n", "        if len(f) not in (3, 4):\n"),
    ("comment lines read as entries", 'line.lstrip().startswith("#")', 'False'),
    ("markup before the status word read through", 'STATUS_RE = re.compile(r"^[\\s*_]*', 'STATUS_RE = re.compile(r"^[\\s*_~<>/a-z`]*'),
    ("a status read as a prefix (OPENED as OPEN)", '([A-Za-z]+)(?![A-Za-z])")', '(OPEN|FIXED|[A-Za-z]+)")'),
    ("status read case-sensitively", 's.group(1).upper() not in STATUSES', 's.group(1) not in STATUSES'),
    ("ids with markup accepted", 'ID_RE = re.compile(r"^[\\s*_]*([A-Za-z0-9]+)[\\s*_]*$")', 'ID_RE = re.compile(r"^.*?([A-Za-z0-9]+).*$")'),
    ("bold ids not merged", 'ID_RE = re.compile(r"^[\\s*_]*([A-Za-z0-9]+)[\\s*_]*$")', 'ID_RE = re.compile(r"^\\s*([*_]*[A-Za-z0-9]+[*_]*)\\s*$")'),
    ("duplicates unchecked", "        if len(lines) > 1:\n", "        if False:\n"),
    ("second table ignored", "        i = j + 1\n    for n, l in enumerate(lines):", "        break\n    for n, l in enumerate(lines):"),
    ("any table read as an index", '                elif header == "id" and len(cur[1]) >= 3:', '                elif len(cur[1]) >= 3:'),
    ("near-`id` headers unrefused", '                    if header != "id" and header.startswith("id"):', '                    if False:'),
    ("letter ids refused", 'ID_RE = re.compile(r"^[\\s*_]*([A-Za-z0-9]+)[\\s*_]*$")', 'ID_RE = re.compile(r"^[\\s*_]*([0-9]+)[\\s*_]*$")'),
    *[(f"{w} dropped", 'STATUSES = ("OPEN", "FIXED", "CLOSED", "RESOLVED", "WONTFIX", "RETRACTED")', 'STATUSES = ("OPEN", "FIXED", "CLOSED", "RESOLVED", "WONTFIX", "RETRACTED")'.replace(f', "{w}"', "")) for w in ("CLOSED", "RESOLVED", "WONTFIX", "RETRACTED")],
    ("registry id unstripped", "rid, kind, body = f[0].strip(), f[1].strip()", "rid, kind, body = f[0], f[1].strip()"),
    ("registry kind unstripped", "rid, kind, body = f[0].strip(), f[1].strip()", "rid, kind, body = f[0].strip(), f[1]"),
    ("header case-sensitive", "header = cur[1][0].strip().lower() if cur[1] else", "header = cur[1][0].strip() if cur[1] else"),
    ("id with trailing text read", 'ID_RE = re.compile(r"^[\\s*_]*([A-Za-z0-9]+)[\\s*_]*$")', 'ID_RE = re.compile(r"^[\\s*_]*([A-Za-z0-9]+)")'),
    ("a malformed line owns its row", "if e[0] in KINDS and e[1]])", "if True])"),
    ("fenced blocks excused", '    lines, covered = text.split("\\n"), set()',
     '    lines, covered = text.split("\\n"), set()\n    covered.update(x for tk in toks if tk.type == "fence" and tk.map for x in range(*tk.map))'),
    ("a BOM not stripped", 'text = text[1:] if text.startswith("\\ufeff") else text', 'text = text'),
    ("rows outside tables unseen", '        if l.lstrip().startswith("|") and n not in covered:', '        if False:'),
]


def mutations():
    import tempfile
    src = open(__file__, encoding="utf-8").read()
    body = src[:src.index("# (label, text in this file, replacement).")]    # mutate the CODE, not this list
    alive, broken = [], []
    with tempfile.TemporaryDirectory() as td:
        for label, a, b in MUTATIONS:
            if body.count(a) != 1:
                broken.append(f"{label}: its text occurs {body.count(a)} times in the code, not once")
                continue
            p = os.path.join(td, "m.py")
            open(p, "w", encoding="utf-8").write(src.replace(a, b, 1))
            r = subprocess.run([sys.executable, p, "--self-test"], capture_output=True, text=True)
            # KILLED only if the self-test ran and reported a failed shape: a SyntaxError prints no "Traceback"
            # and was once counted as red (review #24b)
            if r.returncode == 0:
                alive.append(label)
            elif "[owned self-test] FAIL" not in r.stdout:
                broken.append(f"{label}: the mutated file did not run its self-test to a FAIL (it crashed)")
    for x in broken:
        print(f"  ?? {x}")
    for x in alive:
        print(f"  *** SURVIVED *** {x}")
    print(f"[owned mutations] {'FAIL' if alive or broken else 'PASS'} :: {len(MUTATIONS)} mutations, "
          f"{len(MUTATIONS) - len(alive) - len(broken)} turn the self-test red")
    return 2 if broken else 1 if alive else 0


def main():
    if "--self-test" in sys.argv:
        return self_test()
    if "--mutations" in sys.argv:
        return mutations()
    root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
    if not root:
        print("[owned] CANNOT LOOK :: not inside a git work tree")
        return 2
    os.chdir(root)
    try:
        index = open("KNOWN_ISSUES.md", encoding="utf-8").read()
    except OSError as e:
        print(f"[owned] CANNOT LOOK :: {e}")
        return 2
    registry = open(REGISTRY, encoding="utf-8").read() if os.path.exists(REGISTRY) else None
    problems, n_rows, n_open = check(index, registry)
    if not n_rows:
        print("[owned] CANNOT LOOK :: no issue rows parsed")
        return 2
    if registry is None:
        problems.insert(0, f"{REGISTRY} does not exist")
    for p in problems:
        print(f"  {p}")
    print(f"\n[owned] {'FAIL' if problems else 'PASS'} :: {n_rows} rows, {n_open} OPEN, {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
