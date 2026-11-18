#!/usr/bin/env python3
r"""The note's caption rule: print each caption's first sentence, and fail where a figure caption lacks its stamp.

The rule (the note's measurement rewrite, 2026-11-18):
  1. Sentence 1 states the takeaway, a finding the body already states. A development figure's caption begins
     "Development check:".
  2. Sentence 2 of a figure caption is the error-model stamp, exactly one of STAMPS below.
  3. The panel guide and definitions come next, then the remaining caveats. A prohibitive caveat (CAVEATS below)
     belongs in sentence 1 or 2; one found later is reported as a warning, not a failure.

Whether sentence 1 states the takeaway is a reading, and no script can check it. This script prints sentence 1 of
every figure and table caption in the posted note, in print order and numbered as LaTeX numbers them, so that a
meaning read can check them all. It fails on rule 2 and on rule 1's prefix, which are mechanical.

  python3 check_caption_rule.py            # report every caption; exit 1 on a rule 1 or rule 2 failure
  python3 check_caption_rule.py --report   # the same report, always exit 0 (for a caption pass in progress)
  python3 check_caption_rule.py --self-test

WHICH CAPTIONS. Every \caption reached from main_note.tex by \input or \include, recursively, in input order. One in
a figure environment is a figure caption; one in table, longtable or xltabular is a table caption. Comments are
removed first, and a caption's optional short title, \caption[short]{long}, is skipped.

WHERE THE STAMP APPLIES. To every figure caption, except a figure whose label caption-rule.tsv lists as "exempt",
with its reason (for example, a figure that draws no measured quantity). caption-rule.tsv also lists the
"development" figures, whose caption must begin "Development check:"; "development+exempt" is both. A label the file names that no figure caption
carries fails the check, so the file cannot go stale silently.
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DRIVER = "main_note.tex"
RULES = "caption-rule.tsv"

STAMPS = (
    "Bars: reported covariance.",
    "Bars: weight statistics only, not the covariance.",
    "No uncertainty drawn: no covariance exists.",
)
DEV_PREFIX = "Development check:"
CAVEATS = ("not a pull", "descriptive", "configuration~(a)", "Configuration~(a)", "configuration (a)",
           "Configuration (a)")

# Tokens after which a period does not end a sentence.
ABBREV = {"fig", "figs", "ref", "refs", "tab", "tabs", "eq", "eqs", "app", "apps", "sec", "secs", "e.g", "i.e",
          "vs", "al", "cf", "approx", "no", "resp", "ch", "max", "min", "std"}

INPUT_RE = re.compile(r"\\(?:input|include)\{([^{}]+)\}")
BEGIN_RE = re.compile(r"\\(begin|end)\{(figure\*?|table\*?|longtable|xltabular)\}")
CAPTION_RE = re.compile(r"\\caption(?![A-Za-z])")
LABEL_RE = re.compile(r"\\label\{([^{}]+)\}")


def strip_comments(text: str) -> str:
    """Remove LaTeX comments (an unescaped % to the end of its line), keeping line count."""
    return "\n".join(re.sub(r"(?<!\\)%.*", "", line) for line in text.split("\n"))


def balanced(text: str, i: int, open_: str = "{", close: str = "}") -> tuple[str, int]:
    """text[i] is open_; return the enclosed text and the index after the matching close."""
    depth, j = 0, i
    while j < len(text):
        c = text[j]
        if c == "\\":
            j += 2
            continue
        if c == open_:
            depth += 1
        elif c == close:
            depth -= 1
            if depth == 0:
                return text[i + 1:j], j + 1
        j += 1
    raise ValueError(f"unbalanced {open_} at offset {i}")


def closure(root: Path, driver: str = DRIVER) -> list[Path]:
    """The files the driver reaches by \\input or \\include, in input order (the driver first)."""
    out: list[Path] = []

    def walk(path: Path) -> None:
        out.append(path)
        text = strip_comments(path.read_text())
        for m in INPUT_RE.finditer(text):
            name = m.group(1).strip()
            sub = root / (name if name.endswith(".tex") else name + ".tex")
            if sub.exists():
                walk(sub)

    walk(root / driver)
    return out


def captions(root: Path, driver: str = DRIVER) -> list[dict]:
    """Every caption in print order: kind, number, label, file, line and its text, comments removed.

    The driver's \\input lines are expanded in place, so environments and numbering follow print order."""
    items: list[dict] = []
    counters = {"figure": 0, "table": 0}

    def scan(path: Path) -> None:
        text = strip_comments(path.read_text())
        stack: list[str] = []
        pos = 0
        events = []
        for m in INPUT_RE.finditer(text):
            events.append((m.start(), "input", m))
        for m in BEGIN_RE.finditer(text):
            events.append((m.start(), "env", m))
        for m in CAPTION_RE.finditer(text):
            events.append((m.start(), "caption", m))
        events.sort(key=lambda e: e[0])
        for start, what, m in events:
            if start < pos:
                continue
            if what == "input":
                name = m.group(1).strip()
                sub = root / (name if name.endswith(".tex") else name + ".tex")
                if sub.exists():
                    scan(sub)
            elif what == "env":
                env = m.group(2).rstrip("*")
                kind = "figure" if env == "figure" else "table"
                if m.group(1) == "begin":
                    stack.append(kind)
                elif stack:
                    stack.pop()
            else:
                j = m.end()
                while j < len(text) and text[j] in " \t\n":
                    j += 1
                if j < len(text) and text[j] == "[":
                    _, j = balanced(text, j, "[", "]")
                    while j < len(text) and text[j] in " \t\n":
                        j += 1
                if j >= len(text) or text[j] != "{":
                    continue
                body, end = balanced(text, j)
                kind = stack[-1] if stack else "table"
                counters[kind] += 1
                # The label is the first \label inside the caption or after it, before the next caption or environment end.
                rest = text[end:end + 400]
                stop = min([k for k in (rest.find("\\caption"), rest.find("\\end{")) if k >= 0] or [len(rest)])
                lab = LABEL_RE.search(body) or LABEL_RE.search(rest[:stop])
                items.append({
                    "kind": kind, "number": counters[kind], "label": lab.group(1) if lab else "",
                    "file": path.name, "line": text.count("\n", 0, start) + 1,
                    "text": re.sub(r"\s+", " ", LABEL_RE.sub("", body)).strip(),
                })
                pos = end

    scan(root / driver)
    return items


def sentences(text: str) -> list[str]:
    """Split caption text into sentences. A period ends one when followed by space and then a capital, a backslash
    command, math or a digit, and not after an abbreviation or before a tilde (Fig.~3)."""
    out, start, i, depth = [], 0, 0, 0
    math = False
    while i < len(text):
        c = text[i]
        if c == "\\" and i + 1 < len(text):
            i += 2
            continue
        if c == "$":
            math = not math
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        elif c in ".?!" and not math and depth == 0:
            nxt = text[i + 1:i + 3]
            if nxt[:1] == " " and nxt[1:2] and (nxt[1].isupper() or nxt[1] in "\\$(" or nxt[1].isdigit()):
                word = re.search(r"([A-Za-z.]+)$", text[start:i])
                tok = word.group(1).lower() if word else ""
                if tok not in ABBREV and not re.fullmatch(r"[a-z]", tok):
                    out.append(text[start:i + 1].strip())
                    start = i + 1
        i += 1
    tail = text[start:].strip()
    if tail:
        out.append(tail)
    return out


def load_rules(root: Path) -> dict[str, tuple[str, str]]:
    path = root / RULES
    rules: dict[str, tuple[str, str]] = {}
    if not path.exists():
        return rules
    for n, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip() or line.startswith("#"):
            continue
        cols = line.split("\t")
        if len(cols) < 3 or cols[1] not in ("exempt", "development", "development+exempt") or not cols[2].strip():
            raise SystemExit(f"{RULES}:{n}: want label<TAB>exempt|development|development+exempt<TAB>reason, got {line!r}")
        rules[cols[0]] = (cols[1], cols[2].strip())
    return rules


def check(root: Path, driver: str = DRIVER, out=sys.stdout) -> tuple[int, int]:
    """Print the report; return (failures, warnings)."""
    items = captions(root, driver)
    rules = load_rules(root)
    fails = warns = 0
    seen = set()
    for it in items:
        s = sentences(it["text"])
        first = s[0] if s else ""
        verdict = []
        if it["kind"] == "figure":
            seen.add(it["label"])
            rule = rules.get(it["label"], ("", ""))[0]
            if rule.startswith("development") and not first.startswith(DEV_PREFIX):
                verdict.append(f"FAIL rule 1: a development figure begins \"{DEV_PREFIX}\"")
            if not rule.endswith("exempt"):
                second = s[1] if len(s) > 1 else ""
                if second not in STAMPS:
                    verdict.append("FAIL rule 2: sentence 2 is not a stamp" + (f" (it reads: {second[:70]!r})"
                                                                                 if second else " (no sentence 2)"))
            late = [c for c in CAVEATS if c in " ".join(s[2:]) and c not in " ".join(s[:2])]
            if late:
                verdict.append(f"WARN rule 3: caveat after sentence 2: {', '.join(sorted(set(late)))}")
        fails += sum(v.startswith("FAIL") for v in verdict)
        warns += sum(v.startswith("WARN") for v in verdict)
        tag = "Figure" if it["kind"] == "figure" else "Table"
        print(f"{tag} {it['number']}  [{it['label'] or 'no label'}]  {it['file']}:{it['line']}", file=out)
        print(f"    1: {first}", file=out)
        for v in verdict:
            print(f"    {v}", file=out)
    for lab, (rule, _) in sorted(rules.items()):
        if lab not in seen:
            print(f"FAIL {RULES}: {lab} ({rule}) is no figure caption's label", file=out)
            fails += 1
    nfig = sum(it["kind"] == "figure" for it in items)
    print(f"CAPTION-RULE :: {'PASS' if not fails else 'FAIL'} ({nfig} figure and {len(items) - nfig} table captions; "
          f"{fails} failure(s), {warns} warning(s))", file=out)
    return fails, warns


def self_test() -> int:
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "main_note.tex").write_text(
            "\\begin{document}\n\\input{body}\n\\end{document}\n")
        (root / "body.tex").write_text(r"""
\begin{figure}\caption[Short]{The ratio is flat within Fig.~3's range. Bars: reported covariance. Left: $p_T$.}
\label{fig:good}\end{figure}
\begin{figure}\caption{The shift is small, e.g. below 1\%. Panels show cells. Bars: reported covariance.}
\label{fig:nostamp}\end{figure}
% \begin{figure}\caption{A commented-out figure. No stamp.}\label{fig:comment}\end{figure}
\begin{figure}\caption{Development check: recovery at 5 iterations. No uncertainty drawn: no covariance exists.
Left is descriptive.}\label{fig:dev}\end{figure}
\begin{figure}\caption{Recovery at 5 iterations. Bars: weight statistics only, not the covariance.}\label{fig:devbad}
\end{figure}
\begin{figure}\caption{A survey of measurements.}\label{fig:survey}\end{figure}
\begin{figure}\caption{Development check: the bias falls. Bars: standard error of the mean.}\label{fig:devex}\end{figure}
\begin{table}\caption{Values of the cells. The units are \si{cm^2}.}\label{tab:vals}\end{table}
\begin{xltabular}{\textwidth}{X}\caption{A long table.}\label{tab:long}\\ x \end{xltabular}
""")
        (root / RULES).write_text("fig:dev\tdevelopment\tthe estimator's development tests\n"
                                  "fig:devbad\tdevelopment\tthe estimator's development tests\n"
                                  "fig:survey\texempt\tdraws no measured quantity\n"
                                  "fig:devex\tdevelopment+exempt\ta closure with standard-error bars\n")
        import io
        buf = io.StringIO()
        fails, warns = check(root, out=buf)
        rep = buf.getvalue()
        cases = [
            ("six figures and two tables found, the commented one skipped",
             "6 figure and 2 table captions" in rep and "fig:comment" not in rep),
            ("an abbreviation (Fig.~3, e.g.) does not end sentence 1",
             "1: The ratio is flat within Fig.~3's range." in rep and "1: The shift is small, e.g. below 1\\%." in rep),
            ("the good figure passes", "fig:good" in rep and rep.split("[fig:good]")[1].split("Figure")[0].count("FAIL") == 0),
            ("a stamp in sentence 3 fails rule 2", "sentence 2 is not a stamp (it reads: 'Panels show cells.')" in rep),
            ("a development figure without the prefix fails rule 1", rep.count("FAIL rule 1") == 1),
            ("a caveat after sentence 2 warns", "WARN rule 3: caveat after sentence 2: descriptive" in rep),
            ("an exempt figure needs no stamp", rep.split("[fig:survey]")[1].split("Table")[0].count("FAIL") == 0),
            ("tables are numbered and printed, without the stamp rule",
             "Table 2  [tab:long]" in rep and rep.split("[tab:vals]")[1].count("FAIL rule 2") == 0),
            ("a development+exempt figure needs the prefix but no stamp",
             rep.split("[fig:devex]")[1].split("Table")[0].count("FAIL") == 0),
            ("the totals", fails == 2 and warns == 1),
        ]
        (root / RULES).write_text("fig:gone\texempt\ta figure that left the note\n")
        buf = io.StringIO()
        fails2, _ = check(root, out=buf)
        cases.append(("a rules row naming no figure fails", "fig:gone (exempt) is no figure caption's label"
                      in buf.getvalue()))
        (root / RULES).write_text("fig:good\texempt\n")
        try:
            load_rules(root)
            cases.append(("a rules row without a reason is refused", False))
        except SystemExit:
            cases.append(("a rules row without a reason is refused", True))
    for name, good in cases:
        print(f"  {'ok  ' if good else 'FAIL'} {name}")
        ok &= good
    print("CAPTION-RULE SELF-TEST ::", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    if argv not in ([], ["--report"]):
        print(__doc__)
        return 2
    fails, _ = check(HERE)
    return 0 if (fails == 0 or argv == ["--report"]) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
