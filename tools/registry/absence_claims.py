#!/usr/bin/env python3
"""Absence claims must carry their search.

    absence_claims.py [--repo DIR]            # check the STAGED diff (pre-commit); exit 1 on a bare absence claim
    absence_claims.py --count-existing [REV]  # information only: how many lines at REV (default HEAD) would match
    absence_claims.py --self-test             # every pattern fires, the exemption holds, unrelated "no" is silent

THE RULE (docs/orchestration/RECORDS-RULES.md, rule 4). A sentence that asserts a result does not exist -- "no
coverage exists", "never measured", "has not been run", "untested", ... -- is a claim about the whole repository
and is only as good as the search behind it. In an ADDED or CHANGED line of a staged
  * docs/orchestration/**/*.md record, or
  * docs/analysis-note/*.tex source (printed text only: a TeX comment is not checked as a claim),
a match of ABSENCE_PATTERNS fails the commit unless the same paragraph (the run of non-blank lines around it, in
the staged file) carries a search line of the form

    Search: <the aliases or terms searched, separated by ";"> @ <commit sha, 7-40 hex>

whose sha names a commit in this repository. In a .tex source the search line goes in a comment
(`% Search: ... @ <sha>`), so it never prints. `tools/registry/whatis.py "<estimator>"` prints exactly such a line
for every alias of the estimator. A paragraph is judged on its JOINED text (a claim wrapped across lines is seen),
and a match counts only if a line it spans is added or changed in the staged diff (`git diff --cached`, the index
against HEAD): lines already in HEAD are not re-judged.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reglib  # noqa: E402

SCOPE = (re.compile(r"docs/orchestration/.+\.md"), re.compile(r"docs/analysis-note/[^/]+\.tex"))
# Generated renderings are mechanical, not prose; their generator's own --check governs them.
GENERATED = {"docs/analysis-note/records_results_index.tex", "docs/analysis-note/records_estimators.tex"}
CODE_SPAN = re.compile(r"`[^`]*`")
TEX_COMMENT = re.compile(r"(?<!\\)%.*")
W = r"[\w$\\{}().,'`-]+"  # one word of prose, TeX or markdown
RESULT = r"(?:results?|measurements?|coverage|closures?|tests?|runs?|stud(?:y|ies)|estimates?|receipts?|evidence|data)"
# The explicit pattern list. Each entry: (name, regex, one sentence it must fire on). The self-test runs every
# example, so a pattern cannot be added without a demonstration that it fires.
ABSENCE_PATTERNS = (
    ("no-X-exists", rf"\bno\s+(?:{W}\s+){{0,5}}?{RESULT}\s+(?:{W}\s+){{0,4}}?(?:exists?|existed|is\s+available|was\s+found|has\s+been\s+(?:run|made|done|measured|recorded))\b",
     "No coverage result for configuration (e) exists."),
    ("never-measured", r"\bnever\s+(?:been\s+)?(?:measured|tested|run|computed|evaluated|assessed|validated|checked)\b",
     "Its intervals were never measured."),
    ("has-not-been-run", r"\b(?:has|have|had|was|were|is|are)\s+not\s+(?:yet\s+)?(?:been\s+)?(?:run|measured|tested|computed|evaluated|assessed|validated)\b",
     "The coverage study has not been run."),
    ("untested", r"\b(?:untested|unmeasured|unassessed|unevaluated)\b",
     "Coverage under configuration (e) is untested."),
    ("no-coverage", r"\bno\s+(?:{W}\s+)?(?:coverage|closure)\s+(?:test|study|result|measurement|run|check)s?\b".replace("{W}", W),
     "There is no coverage test of these intervals."),
    ("had-no-test", rf"\b(?:has|have|had)\s+(?:had\s+)?no\s+(?:{W}\s+)?{RESULT}\b"
                    rf"|\bneither\b[^.;]{{0,80}}?\b(?:has|have)\s+had\s+an?\s+(?:{W}\s+)?{RESULT}\b",
     "Neither block has had a coverage test."),
    ("does-not-exist", r"\b(?:does|do|did)\s+not\s+exist\b|\bnon-?existent\b",
     "A development-scale interval for R does not exist."),
    ("nothing-measured", r"\bnothing\s+(?:has\s+been\s+|was\s+|is\s+)?(?:measured|tested|run|computed)\b",
     "Nothing was measured for this estimator."),
)
_PATS = [(n, re.compile(rx, re.I), ex) for n, rx, ex in ABSENCE_PATTERNS]
SEARCH_LINE = re.compile(r"\bSearch:\s*\S.*?@\s*([0-9a-f]{7,40})\b")
# Sentences the patterns must NOT fire on (the self-test runs them).
UNRELATED = ("No change was needed in the driver.", "There is no reason to rerun it.",
             "The estimator has no free parameters.", "No, the review found nothing to fix.",
             "It does not change the result.", "The ten hypotheses are not rejected by the test.")


def in_scope(path: str) -> bool:
    return path not in GENERATED and any(rx.fullmatch(path) for rx in SCOPE)


def printed(path: str, line: str) -> str:
    """The text judged as a claim: a .tex line without its comment; a .md line without its `code spans` (a quoted
    pattern or command is not a claim)."""
    return TEX_COMMENT.sub("", line) if path.endswith(".tex") else CODE_SPAN.sub("", line)


def matches(text: str) -> list[str]:
    return [n for n, rx, _ in _PATS if rx.search(text)]


def commit_exists(repo: Path, sha: str) -> bool:
    out = subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{sha}^{{commit}}"], capture_output=True,
                         env=reglib.git_env(repo), cwd=str(repo))
    return out.returncode == 0


def added_lines(repo: Path) -> dict[str, list[int]]:
    """path -> 1-based line numbers (in the staged file) of lines the staged diff adds or changes."""
    raw = reglib.git(repo, "diff", "--cached", "-U0", "--no-color", "--diff-filter=AMR", "--no-ext-diff").decode(
        "utf-8", errors="replace")
    out: dict[str, list[int]] = {}
    path = None
    for line in raw.splitlines():
        if line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else None
        elif line.startswith("@@") and path:
            m = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", line)
            start, count = int(m.group(1)), int(m.group(2) or "1")
            out.setdefault(path, []).extend(range(start, start + count))
    return {p: v for p, v in out.items() if in_scope(p)}


def claims(path: str, lines: list[str], lo: int, hi: int):
    """(first line, last line, pattern names, matched text) of every absence-pattern match in the paragraph
    lines[lo:hi+1], judged on its JOINED printed text, so a claim wrapped across lines ("has not / been run") is
    seen. Line numbers are 1-based."""
    parts, spans, pos = [], [], 0
    for i in range(lo, hi + 1):
        t = printed(path, lines[i])
        parts.append(t)
        spans.append((pos, pos + len(t), i + 1))
        pos += len(t) + 1
    joined = " ".join(parts)
    out = []
    for name, rx, _ in _PATS:
        for m in rx.finditer(joined):
            on = [ln for a, b, ln in spans if a <= m.end() - 1 and m.start() <= b]
            if on:
                out.append((on[0], on[-1], name, m.group(0)))
    return out


def paragraph_bounds(lines: list[str], i: int) -> tuple[int, int]:
    lo = i
    while lo > 0 and lines[lo - 1].strip():
        lo -= 1
    hi = i
    while hi + 1 < len(lines) and lines[hi + 1].strip():
        hi += 1
    return lo, hi


def judge(repo: Path, path: str, text: str, linenos: list[int]) -> list[str]:
    """Bare absence claims touching an added/changed line. Each paragraph holding an added line is judged once,
    on its joined text; a match counts if any line it spans was added or changed."""
    lines = text.split("\n")
    added = {n for n in linenos if 1 <= n <= len(lines)}
    fails, seen = [], set()
    for n in sorted(added):
        if not lines[n - 1].strip():
            continue
        lo, hi = paragraph_bounds(lines, n - 1)
        if (lo, hi) in seen:
            continue
        seen.add((lo, hi))
        found = [c for c in claims(path, lines, lo, hi) if any(a in added for a in range(c[0], c[1] + 1))]
        if not found:
            continue
        para = lines[lo:hi + 1]
        shas = [m.group(1) for l in para for m in [SEARCH_LINE.search(l)] if m]
        if any(commit_exists(repo, sh) for sh in shas):
            continue
        why = ("its paragraph's search line names no commit of this repository (" + ", ".join(shas) + ")" if shas
               else "its paragraph carries no 'Search: <terms> @ <sha>' line")
        by_line: dict[tuple[int, int], list[str]] = {}
        for a, b, name, txt in found:
            by_line.setdefault((a, b), []).append(name)
        for (a, b), names in sorted(by_line.items()):
            where = f"{a}" if a == b else f"{a}-{b}"
            fails.append(f"{path}:{where}: absence claim [{', '.join(sorted(set(names)))}] -- {why}: "
                         f"{' '.join(l.strip() for l in lines[a - 1:b])[:140]!r}")
    return fails


def check_staged(repo: Path) -> int:
    index = reglib.Index(repo)
    fails, nfiles, nlines = [], 0, 0
    for path, linenos in sorted(added_lines(repo).items()):
        text = index.text(path)
        if text is None:
            continue
        nfiles += 1
        nlines += len(linenos)
        fails += judge(repo, path, text, linenos)
    for f in fails:
        print("  FAIL " + f)
    if fails:
        print("  fix: run `python3 tools/registry/whatis.py \"<estimator or term>\"`, read what it finds, and put its "
              "last line ('Search: ... @ <sha>') in the same paragraph (in a .tex source, as a % comment) -- or "
              "drop the claim.")
    print(f"ABSENCE-CLAIMS :: {nlines} added/changed lines in {nfiles} staged in-scope files checked against "
          f"{len(_PATS)} patterns; {len(fails)} bare absence claim(s)")
    return 1 if fails else 0


def count_existing(repo: Path, rev: str) -> int:
    """Information only: how many absence-pattern matches the files at REV hold, judged as the check judges an
    added paragraph (joined text, comments and code spans removed), and how many sit beside a search line."""
    paths = [p for p in reglib.git(repo, "ls-tree", "-r", "--name-only", rev).decode().splitlines() if in_scope(p)]
    total, exempt, files = 0, 0, set()
    per = {n: 0 for n, _, _ in _PATS}
    for p in paths:
        lines = reglib.git(repo, "show", f"{rev}:{p}").decode("utf-8", errors="replace").split("\n")
        i = 0
        while i < len(lines):
            if not lines[i].strip():
                i += 1
                continue
            lo, hi = paragraph_bounds(lines, i)
            found = {(a, b) for a, b, name, _ in claims(p, lines, lo, hi)}
            for a, b, name, _ in claims(p, lines, lo, hi):
                per[name] += 1
            if found:
                files.add(p)
                total += len(found)
                if any(SEARCH_LINE.search(x) for x in lines[lo:hi + 1]):
                    exempt += len(found)
            i = hi + 1
    print(f"ABSENCE-CLAIMS (information) :: at {rev}: {total} distinct claim spans in {len(files)} of {len(paths)} "
          f"in-scope files match; {exempt} of them sit in a paragraph with a search line. Pattern matches: "
          + ", ".join(f"{n} {c}" for n, c in per.items()))
    return 0


def self_test() -> int:
    ok = True

    def expect(name: str, got: bool, want: bool, detail: str = "") -> None:
        nonlocal ok
        ok &= got == want
        print(f"  self-test {'ok' if got == want else 'WRONG':<5} {name}: {'FIRES' if got else 'silent'} "
              f"(want {'FIRES' if want else 'silent'}){' ' + detail if detail else ''}")

    for n, rx, ex in _PATS:
        expect(f"pattern {n} on its example {ex!r}", bool(rx.search(ex)), True)
    for s in UNRELATED:
        expect(f"unrelated {s!r}", bool(matches(s)), False, ",".join(matches(s)))
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        env = reglib.clean_env()  # a throwaway repository: never the hook's GIT_INDEX_FILE

        def g(*a: str) -> str:
            return subprocess.run(["git", "-C", str(t), *a], check=True, capture_output=True, env=env,
                                  cwd=str(t), text=True).stdout.strip()

        g("init", "-q")
        g("config", "user.name", "self-test")
        g("config", "user.email", "self-test@invalid")
        rec = t / "docs/orchestration/RECORD-x.md"
        tex = t / "docs/analysis-note/sec_x.tex"
        rec.parent.mkdir(parents=True)
        tex.parent.mkdir(parents=True)
        rec.write_text("# Record\n\nAn old line: this was never measured.\n")
        tex.write_text("Old prose.\n")
        g("add", "-A")
        g("commit", "-q", "-m", "base")
        sha = g("rev-parse", "HEAD")

        def staged(md: str | None = None, tx: str | None = None) -> list[str]:
            if md is not None:
                rec.write_text(md)
            if tx is not None:
                tex.write_text(tx)
            g("add", "-A")
            fails = []
            idx = reglib.Index(t)
            for path, linenos in added_lines(t).items():
                fails += judge(t, path, idx.text(path), linenos)
            g("reset", "-q", "--hard", "HEAD")
            return fails

        base = "# Record\n\nAn old line: this was never measured.\n"
        f = staged(md=base + "\nNo coverage result for configuration (e) exists.\n")
        expect("staged bare absence claim in a .md record", bool(f), True, f[0][:90] if f else "")
        f = staged(md=base + f"\nNo coverage result for configuration (e) exists.\nSearch: configuration (e); R @ {sha[:12]}\n")
        expect("same claim with a search line at a real commit", bool(f), False)
        f = staged(md=base + "\nNo coverage result for configuration (e) exists.\nSearch: configuration (e) @ deadbeef00\n")
        expect("same claim, search line names a commit that does not exist", bool(f), True)
        f = staged(md=base + "\nNo coverage result exists.\n\nSearch: R @ " + sha[:12] + "\n")
        expect("search line in a DIFFERENT paragraph does not exempt", bool(f), True)
        f = staged(md=base + "\nThe coverage study has not\nbeen run on the fresh seeds.\n")
        expect("staged claim wrapped across two lines ('has not' / 'been run')", bool(f), True, f[0][:90] if f else "")
        f = staged(md=base.replace("An old line: this was never measured.", "An old line: this was never\nmeasured."))
        expect("a re-wrap that moves an old claim onto a changed line is judged (it is a changed line)", bool(f), True)
        f = staged(md=base + "\nNo change was needed; there is no reason to rerun it.\n")
        expect("staged unrelated 'no'", bool(f), False)
        f = staged(md=base.replace("# Record", "# Record, retitled"))
        expect("an existing absence line, unchanged, while another line changes", bool(f), False)
        f = staged(md=base + "\nThe rule flags sentences such as `no coverage result exists`.\n")
        expect("an absence phrase quoted in a `code span`", bool(f), False)
        f = staged(tx="Old prose.\n% the coverage study has not been run\n")
        expect("absence words inside a TeX comment", bool(f), False)
        f = staged(tx="Old prose.\nNeither block has had a coverage test.\n")
        expect("absence claim in printed TeX prose", bool(f), True)
        f = staged(tx=f"Old prose.\nNeither block has had a coverage test.\n% Search: coverage; (e) @ {sha[:10]}\n")
        expect("TeX claim with a commented search line", bool(f), False)
        out = t / "docs/other/NOTE.md"
        out.parent.mkdir(parents=True)
        out.write_text("No coverage result exists.\n")
        g("add", "-A")
        fails = [x for p, ln in added_lines(t).items() for x in judge(t, p, reglib.Index(t).text(p), ln)]
        expect("out-of-scope path (docs/other/)", bool(fails), False)
    print("ABSENCE-CLAIMS self-test :: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", type=Path, default=None)
    ap.add_argument("--count-existing", nargs="?", const="HEAD", default=None, metavar="REV")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    repo = reglib.repo_root(a.repo or Path.cwd())
    if a.count_existing:
        return count_existing(repo, a.count_existing)
    return check_staged(repo)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
