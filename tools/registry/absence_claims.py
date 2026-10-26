#!/usr/bin/env python3
"""Absence claims must carry their search.

    absence_claims.py [--repo DIR]            # check the STAGED diff (pre-commit); exit 1 on a bare absence claim
    absence_claims.py --base REF [--repo DIR] # check what HEAD adds since REF (CI: a pull request against its base)
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

--base REF (the CI mode; nothing is staged there). The judged lines are those `git diff <merge-base> HEAD` adds or
changes, where <merge-base> is `git merge-base REF HEAD`, read from HEAD's files. As in a merge, a line whose text
is already in REF's or the merge-base's version of the file is not judged: it is not new in this pull request. On
a pull request's merge commit (what GitHub Actions checks out), REF = the base branch tip = the merge-base, so the
judged lines are exactly what the merge would add to the base.
"""
from __future__ import annotations

import argparse
import os
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
# "has had no X" needs a test or measurement noun: "we have no further run planned" is a schedule, not a claim.
TEST_NOUN = r"(?:tests?|measurements?|coverage|closures?|validations?)"
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
    ("had-no-test", rf"\b(?:has|have|had)\s+(?:had\s+)?no\s+(?:{W}\s+)?{TEST_NOUN}\b"
                    rf"|\bneither\b[^.;]{{0,80}}?\b(?:has|have)\s+had\s+an?\s+(?:{W}\s+)?{TEST_NOUN}\b",
     "Neither block has had a coverage test."),
    ("does-not-exist", r"\b(?:does|do|did)\s+not\s+exist\b|\bnon-?existent\b",
     "A development-scale interval for R does not exist."),
    ("nothing-measured", r"\bnothing\s+(?:has\s+been\s+|was\s+|is\s+)?(?:measured|tested|run|computed)\b",
     "Nothing was measured for this estimator."),
)
_PATS = [(n, re.compile(rx, re.I), ex) for n, rx, ex in ABSENCE_PATTERNS]
SEARCH_LINE = re.compile(r"\bSearch:\s*\S.*?@\s*([0-9a-f]{7,40})\b")
# The in-paragraph waiver for a SCOPING statement (about a projection or a method parameter) that is not a claim that
# a result does not exist: `<!-- absence-ok: <reason> -->` in .md, `% absence-ok: <reason>` in .tex. The reason is
# required; an empty one is rejected. Waivers are counted in the summary line.
WAIVER_MD = re.compile(r"<!--\s*absence-ok:(.*?)-->")
WAIVER_TEX = re.compile(r"(?<!\\)%\s*absence-ok:(.*)$")
HTML_COMMENT = re.compile(r"<!--.*?-->")
# Sentences the patterns must NOT fire on (the self-test runs them).
UNRELATED = ("We have no further run planned this week.", "No change was needed in the driver.", "There is no reason to rerun it.",
             "The estimator has no free parameters.", "No, the review found nothing to fix.",
             "It does not change the result.", "The ten hypotheses are not rejected by the test.")


def in_scope(path: str) -> bool:
    return path not in GENERATED and any(rx.fullmatch(path) for rx in SCOPE)


def printed(path: str, line: str) -> str:
    """The text judged as a claim: a .tex line without its comment; a .md line without its `code spans` (a quoted
    pattern or command is not a claim)."""
    return TEX_COMMENT.sub("", line) if path.endswith(".tex") else CODE_SPAN.sub("", HTML_COMMENT.sub("", line))


def matches(text: str) -> list[str]:
    return [n for n, rx, _ in _PATS if rx.search(text)]


def commit_exists(repo: Path, sha: str) -> bool:
    out = subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{sha}^{{commit}}"], capture_output=True,
                         env=reglib.git_env(repo), cwd=str(repo))
    return out.returncode == 0


def added_lines(repo: Path, since: str | None = None) -> dict[str, list[int]]:
    """path -> 1-based line numbers of lines the diff adds or changes: the staged diff (index against HEAD, line
    numbers in the staged file), or, with `since`, `git diff <since> HEAD` (line numbers in HEAD's file)."""
    which = ("--cached",) if since is None else (since, "HEAD")
    raw = reglib.git(repo, "diff", *which, "-U0", "--no-color", "--diff-filter=AMR", "--no-ext-diff").decode(
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


def merge_parents(repo: Path) -> list[str]:
    """During a merge (MERGE_HEAD present), every parent of the commit being made: HEAD and each MERGE_HEAD line.
    Otherwise []: the staged diff against HEAD already names exactly the new lines."""
    path = reglib.git(repo, "rev-parse", "--git-path", "MERGE_HEAD").decode().strip()
    p = Path(path) if os.path.isabs(path) else repo / path
    if not p.exists():
        return []
    heads = [l.strip() for l in p.read_text().splitlines() if l.strip()]
    return ["HEAD"] + heads


def new_against_parents(repo: Path, path: str, text: str, linenos: list[int], parents: list[str]) -> list[int]:
    """In a merge, keep only the lines whose text is in NO parent's version of the file: a line that either side
    already had is not new in this commit and is not judged."""
    if not parents:
        return linenos
    seen: set[str] = set()
    for rev in parents:
        try:
            seen |= set(reglib.git(repo, "show", f"{rev}:{path}").decode("utf-8", errors="replace").split("\n"))
        except RuntimeError:
            pass  # the file is new on that side
    lines = text.split("\n")
    return [n for n in linenos if 1 <= n <= len(lines) and lines[n - 1] not in seen]


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


def paragraph_key(path: str, para: list[str]) -> tuple[str, frozenset[str]]:
    """(the paragraph's printed text with whitespace collapsed, its support: the Search-line shas and waiver
    reasons it carries)."""
    text = " ".join(" ".join(printed(path, l) for l in para).split())
    rx = WAIVER_TEX if path.endswith(".tex") else WAIVER_MD
    support = {m.group(1) for l in para for m in [SEARCH_LINE.search(l)] if m}
    support |= {"waiver:" + m.group(1).strip() for l in para for m in [rx.search(l)] if m}
    return text, frozenset(support)


def prior_paragraphs(repo: Path, path: str, revs: list[str]) -> dict[str, list[frozenset[str]]]:
    """For a .tex source: printed paragraph text -> the supports it had, over every paragraph of `path` at each of
    `revs`. A TeX reflow (DECISION-20261026-joseph-fps-scope-r04-sensitivity-and-tex-reflow.md section 3) changes
    every line of a paragraph but none of its printed text; such a paragraph is not new and is not re-judged, as
    long as it keeps every Search line and waiver it had. Markdown keeps the stricter rule: a re-wrap is judged."""
    out: dict[str, list[frozenset[str]]] = {}
    if not path.endswith(".tex"):
        return out
    for rev in revs:
        try:
            old = reglib.git(repo, "show", f"{rev}:{path}").decode("utf-8", errors="replace").split("\n")
        except RuntimeError:
            continue
        para: list[str] = []
        for line in old + [""]:
            if line.strip():
                para.append(line)
            elif para:
                k, sup = paragraph_key(path, para)
                out.setdefault(k, []).append(sup)
                para = []
    return out


def waiver(path: str, para: list[str]) -> tuple[bool, bool]:
    """(an absence-ok waiver is present, it gives a non-empty reason) for one paragraph."""
    rx = WAIVER_TEX if path.endswith(".tex") else WAIVER_MD
    # A waiver quoted in a `code span` (documentation of the syntax) is not a waiver.
    reasons = [m.group(1).strip() for l in para for m in [rx.search(l if path.endswith(".tex") else CODE_SPAN.sub("", l))]
               if m]
    return bool(reasons), any(reasons)


def judge(repo: Path, path: str, text: str, linenos: list[int], stats: dict | None = None,
          prior: dict[str, list[frozenset[str]]] | None = None) -> list[str]:
    """Bare absence claims touching an added/changed line. Each paragraph holding an added line is judged once,
    on its joined text; a match counts if any line it spans was added or changed. With `prior`
    (prior_paragraphs), a .tex paragraph whose printed text a parent already printed, with no less support, is
    skipped: it was reflowed, not written."""
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
        if prior:
            key, sup = paragraph_key(path, para)
            if any(old <= sup for old in prior.get(key, [])):
                if stats is not None:
                    stats["reflowed"] = stats.get("reflowed", 0) + 1
                continue
        shas = [m.group(1) for l in para for m in [SEARCH_LINE.search(l)] if m]
        if any(commit_exists(repo, sh) for sh in shas):
            continue
        has_waiver, has_reason = waiver(path, para)
        if has_reason:
            if stats is not None:
                stats["waived"] = stats.get("waived", 0) + len(found)
            continue
        why = ("its paragraph's search line names no commit of this repository (" + ", ".join(shas) + ")" if shas
               else "its absence-ok waiver gives no reason" if has_waiver
               else "its paragraph carries no 'Search: <terms> @ <sha>' line and no absence-ok waiver")
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
    fails, nfiles, nlines, stats = [], 0, 0, {"waived": 0, "reflowed": 0}
    parents = merge_parents(repo)
    for path, linenos in sorted(added_lines(repo).items()):
        text = index.text(path)
        if text is None:
            continue
        linenos = new_against_parents(repo, path, text, linenos, parents)
        nfiles += 1
        nlines += len(linenos)
        fails += judge(repo, path, text, linenos, stats, prior_paragraphs(repo, path, parents or ["HEAD"]))
    for f in fails:
        print("  FAIL " + f)
    if fails:
        print("  fix: run `python3 tools/registry/whatis.py \"<estimator or term>\"`, read what it finds, and put its "
              "last line ('Search: ... @ <sha>') in the same paragraph (in a .tex source, as a % comment). If the "
              "sentence is a scoping statement about a projection or a method parameter, not a claim that a result "
              "does not exist, mark the paragraph `<!-- absence-ok: <reason> -->` (.md) or `% absence-ok: <reason>` "
              "(.tex). Keep the sentence: an honest qualifier is what this check protects.")
    merge = f"; merge: lines already in any of {len(parents)} parents not judged" if parents else ""
    print(f"ABSENCE-CLAIMS :: {nlines} added/changed lines in {nfiles} staged in-scope files checked against "
          f"{len(_PATS)} patterns; {len(fails)} bare absence claim(s); {stats['waived']} waived (absence-ok); "
          f"{stats['reflowed']} reflowed TeX paragraph(s) whose printed text and support a parent already had{merge}")
    return 1 if fails else 0


def base_fails(repo: Path, base: str, stats: dict | None = None) -> tuple[list[str], int, int, str, str]:
    """(failures, files checked, lines judged, base sha, merge-base sha) for --base: the lines HEAD adds since
    `git merge-base BASE HEAD`, minus every line whose text BASE's or the merge-base's file already holds."""
    tip = reglib.git(repo, "rev-parse", "--verify", f"{base}^{{commit}}").decode().strip()
    mb = reglib.git(repo, "merge-base", tip, "HEAD").decode().strip()
    parents = [tip] if tip == mb else [tip, mb]
    fails, nfiles, nlines = [], 0, 0
    for path, linenos in sorted(added_lines(repo, mb).items()):
        text = reglib.git(repo, "show", f"HEAD:{path}").decode("utf-8", errors="replace")
        linenos = new_against_parents(repo, path, text, linenos, parents)
        nfiles += 1
        nlines += len(linenos)
        fails += judge(repo, path, text, linenos, stats, prior_paragraphs(repo, path, parents))
    return fails, nfiles, nlines, tip, mb


def check_base(repo: Path, base: str) -> int:
    stats = {"waived": 0, "reflowed": 0}
    try:
        fails, nfiles, nlines, tip, mb = base_fails(repo, base, stats)
    except RuntimeError as exc:
        print(f"ABSENCE-CLAIMS :: CANNOT CHECK against --base {base}: {exc}".rstrip())
        return 2
    for f in fails:
        print("  FAIL " + f)
    if fails:
        print("  fix: as for a staged claim -- put `whatis.py`'s 'Search: ... @ <sha>' line in the paragraph, or, for a "
              "scoping statement, an absence-ok waiver with a reason. Keep the sentence.")
    print(f"ABSENCE-CLAIMS :: {nlines} lines HEAD adds or changes since merge-base {mb[:12]} of --base {base} "
          f"({tip[:12]}), in {nfiles} in-scope files, checked against {len(_PATS)} patterns (lines already in the "
          f"base not judged); {len(fails)} bare absence claim(s); {stats['waived']} waived (absence-ok); "
          f"{stats['reflowed']} reflowed TeX paragraph(s) whose printed text and support the base already had")
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
        out.unlink()
        g("rm", "-q", "--cached", "docs/other/NOTE.md")
        # The absence-ok waiver, both ways.
        stats = {"waived": 0}
        f = staged(md=base + "\nThe projection is unmeasured beyond k = 20.\n<!-- absence-ok: scoping of the "
                   "projection's range, not a missing result -->\n")
        expect("absence-ok waiver with a reason", bool(f), False)
        rec.write_text(base + "\nThe projection is unmeasured beyond k = 20.\n<!-- absence-ok: scoping -->\n")
        g("add", "-A")
        judge(t, "docs/orchestration/RECORD-x.md", reglib.Index(t).text("docs/orchestration/RECORD-x.md"),
              added_lines(t).get("docs/orchestration/RECORD-x.md", []), stats)
        g("reset", "-q", "--hard", "HEAD")
        expect("... and the waiver is counted", stats["waived"] == 0, False, f"waived={stats['waived']}")
        f = staged(md=base + "\nThe projection is unmeasured beyond k = 20.\n<!-- absence-ok: -->\n")
        expect("absence-ok waiver with an EMPTY reason", bool(f), True, f[0][-90:] if f else "")
        f = staged(md=base + "\nThe projection is unmeasured beyond k = 20; mark it with `<!-- absence-ok: x -->`.\n")
        expect("a waiver quoted in a `code span` does not waive", bool(f), True)
        f = staged(tx="Old prose.\nThe projection is unmeasured beyond k = 20.\n% absence-ok: scoping, not a result\n")
        expect("absence-ok waiver with a reason in a .tex % comment", bool(f), False)
        # A REAL merge: a claim that only the other parent had is silent; a claim new in the resolution fires.
        g("checkout", "-q", "-b", "side")
        rec.write_text(base + "\nOn the side branch, the coverage study has not been run.\n")
        g("commit", "-qam", "side adds a claim")
        g("checkout", "-q", "-")
        tex.write_text("Old prose.\nMain moves on.\n")
        g("commit", "-qam", "main moves on")
        g("merge", "-q", "--no-commit", "--no-ff", "side")
        parents = merge_parents(t)
        idx = reglib.Index(t)
        fm = [x for p, ln in added_lines(t).items()
              for x in judge(t, p, idx.text(p), new_against_parents(t, p, idx.text(p), ln, parents))]
        expect("merge: a claim only from the other parent", bool(fm), False, f"parents={len(parents)}")
        rec.write_text(rec.read_text() + "\nThe resolution adds: this closure was never measured.\n")
        g("add", "-A")
        idx = reglib.Index(t)
        fm = [x for p, ln in added_lines(t).items()
              for x in judge(t, p, idx.text(p), new_against_parents(t, p, idx.text(p), ln, parents))]
        expect("merge: a claim new in the merge resolution", bool(fm), True, fm[0][:80] if fm else "")
        g("merge", "--abort")
        # --base (CI): what a branch adds since its merge-base with the base, read from HEAD; nothing staged.
        trunk = g("rev-parse", "--abbrev-ref", "HEAD")
        g("checkout", "-q", "-b", "pr")
        rec.write_text(rec.read_text() + "\nNo coverage result for configuration (z) exists.\n")
        g("commit", "-qam", "pr adds a bare claim")
        fb = base_fails(t, trunk)[0]
        expect("--base: a bare claim the branch adds", bool(fb), True, fb[0][:80] if fb else "")
        fs = [x for p, ln in added_lines(t).items() for x in judge(t, p, reglib.Index(t).text(p), ln)]
        expect("... which the staged mode cannot see once committed (why CI needs --base)", bool(fs), False)
        g("checkout", "-q", "--detach", trunk)
        g("merge", "-q", "--no-ff", "-m", "merge pr", "pr")
        fb = base_fails(t, "HEAD^1")[0]
        expect("--base HEAD^1 on the pull request's MERGE commit (the CI checkout)", bool(fb), True,
               fb[0][:80] if fb else "")
        g("checkout", "-q", "pr")
        g("reset", "-q", "--hard", trunk)
        rec.write_text(rec.read_text() + "\nCopied into a new paragraph:\nAn old line: this was never measured.\n")
        g("commit", "-qam", "pr copies an existing claim line")
        raw = [x for p, ln in added_lines(t, g("merge-base", trunk, "HEAD")).items()
               for x in judge(t, p, g("show", f"HEAD:{p}") + "\n", ln)]
        expect("... (precondition: unfiltered, the copied base line IS in the diff and fires)", bool(raw), True)
        fb = base_fails(t, trunk)[0]
        expect("--base: a claim line already in the base, copied by the branch into a new paragraph", bool(fb), False)
        g("checkout", "-q", trunk)
        rec.write_text(rec.read_text() + "\nBoth sides: this closure was never measured.\n")
        g("commit", "-qam", "base adds a claim after the fork")
        g("checkout", "-q", "pr")
        rec.write_text(rec.read_text() + "\nBoth sides: this closure was never measured.\n")
        g("commit", "-qam", "pr adds the same line")
        fb = base_fails(t, trunk)[0]
        expect("--base: a claim line the base tip already holds (added there after the fork)", bool(fb), False)
        rec.write_text(rec.read_text() + "\nThe projection is unmeasured beyond k = 20.\n<!-- absence-ok: scoping of "
                       "the projection's range, not a missing result -->\n")
        g("commit", "-qam", "pr adds a waived scoping statement")
        st = {"waived": 0}
        fb = base_fails(t, trunk, st)[0]
        expect("--base: a waiver with a reason passes, and is counted", bool(fb) or st["waived"] != 1, False,
               f"waived={st['waived']}")
        rec.write_text(rec.read_text() + f"\nNo coverage result exists for (y).\nSearch: (y) @ {sha[:12]}\n")
        g("commit", "-qam", "pr adds a searched claim")
        fb = base_fails(t, trunk)[0]
        expect("--base: a claim with a search line at a real commit passes", bool(fb), False)
        # A TeX reflow (one line per paragraph): unchanged printed text and support is not re-judged; any change is.
        tpath = "docs/analysis-note/sec_x.tex"
        tex.write_text("Old prose.\n\nNeither block has had\na coverage test.\n\nThe study has not been\nrun "
                       f"again.\n% Search: study @ {sha[:12]}\n")
        g("commit", "-qam", "a wrapped bare TeX claim and a wrapped searched one, grandfathered")

        def reflowed(tx: str) -> list[str]:
            tex.write_text(tx)
            g("add", "-A")
            idx = reglib.Index(t)
            got = [x for p, ln in added_lines(t).items()
                   for x in judge(t, p, idx.text(p), ln, None, prior_paragraphs(t, p, ["HEAD"]))]
            g("reset", "-q", "--hard", "HEAD")
            return got

        keep = f"\n\nThe study has not been run again.\n% Search: study @ {sha[:12]}\n"
        f = reflowed("Old prose.\n\nNeither block has had a coverage test." + keep)
        expect("reflow: a grandfathered bare TeX claim joined onto one line", bool(f), False)
        f = reflowed("Old prose.\n\nNeither block has had a full coverage test." + keep)
        expect("reflow that also changes a word in the claim's paragraph", bool(f), True, f[0][:70] if f else "")
        f = reflowed("Old prose.\n\nNeither block has had a coverage test.\n\nThe study has not been run again.\n")
        expect("reflow that drops the paragraph's Search line", bool(f), True, f[0][:70] if f else "")
        tex.write_text("Old prose.\n\nNeither block has had a coverage test." + keep)
        g("add", "-A")
        raw = [x for p, ln in added_lines(t).items() for x in judge(t, p, reglib.Index(t).text(p), ln)]
        g("reset", "-q", "--hard", "HEAD")
        expect("... (precondition: the same reflow judged without prior FIRES)", bool(raw), True)
        rec.write_text(rec.read_text().replace("An old line: this was never measured.",
                                               "An old line: this was never\nmeasured."))
        g("add", "-A")
        fmd = [x for p, ln in added_lines(t).items()
               for x in judge(t, p, reglib.Index(t).text(p), ln, None, prior_paragraphs(t, p, ["HEAD"]))]
        g("reset", "-q", "--hard", "HEAD")
        expect("a Markdown re-wrap of a bare claim is still judged with prior (the exemption is TeX-only)",
               bool(fmd), True)
    print("ABSENCE-CLAIMS self-test :: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", type=Path, default=None)
    ap.add_argument("--count-existing", nargs="?", const="HEAD", default=None, metavar="REV")
    ap.add_argument("--base", default=None, metavar="REF",
                    help="judge the lines HEAD adds since `git merge-base REF HEAD` instead of the staged diff (CI)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    repo = reglib.repo_root(a.repo or Path.cwd())
    if a.count_existing:
        return count_existing(repo, a.count_existing)
    if a.base is not None:  # an empty --base must not fall back to the staged mode
        return check_base(repo, a.base)
    return check_staged(repo)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
