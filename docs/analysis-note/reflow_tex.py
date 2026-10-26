#!/usr/bin/env python3
"""Reflow hand-written LaTeX sources so that each prose paragraph is one source line and each block of consecutive
full-line comments is one comment line (DECISION-20261026-joseph-fps-scope-r04-sensitivity-and-tex-reflow.md §3).

    reflow_tex.py [--check] [--map OUT.json] [--keep-comments-in-place FILE ...] FILE ...
    reflow_tex.py --note [--check]        # every hand-written source of docs/analysis-note, with its fixed lists

CI runs `--note --check`: a hard-wrapped paragraph in a note source fails it.

A pure formatting transform: every join is one TeX already treats as equivalent, so the typeset output must not
change. That is proved outside this tool, by building every PDF before and after and comparing the extracted text.

Joining rules (a line is joined onto the line before it only inside one paragraph, i.e. a run of non-blank lines):
  * A line ending in a newline joins with one space, which is what TeX reads the end of a line as.
  * A line whose code ends in an unescaped `%` comment: the comment ate the newline. If the code before `%` ends in
    whitespace the join is one space, otherwise none; a control word followed by a letter gets one space, which TeX
    skips after a control word, so that two tokens never fuse into one name.
  * A trailing comment on a line that is joined onto is moved to its own comment line right after the joined line,
    in order; a trailing comment on the last line of a run stays where it is.
  * A full-line comment inside a paragraph is moved after the paragraph's text line, unless the file is listed in
    --keep-comments-in-place, where it stays, and the content runs on either side are joined separately.
Lines never joined, nor joined onto:
  * every line inside a line-sensitive environment (tables, alignments, displayed math, verbatim, pictures), and
    inside \\[ ... \\];
  * a line opening or closing an environment, a sectioning command, \\label, \\input/\\include, \\centering,
    \\includegraphics, a definition (\\newcommand, \\def, ...) with everything up to its balanced closing brace, a
    line ending in \\\\ (a forced break) or one starting with `&`;
  * \\item, \\caption and \\paragraph start a new line, and their continuation lines join onto them.
Comment lines are joined only with comment lines of the same indentation and marker; a separator rule, a commented-
out command (text starting with `\\`), a bullet, a `Search:` line and an `absence-ok:` waiver each start a new line.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PROTECTED_ENVS = {
    "tabular", "tabular*", "tabularx", "longtable", "longtable*", "array", "align", "align*", "alignat", "alignat*",
    "eqnarray", "eqnarray*", "gather", "gather*", "multline", "multline*", "equation", "equation*", "split", "cases",
    "matrix", "pmatrix", "bmatrix", "verbatim", "Verbatim", "lstlisting", "minted", "alltt", "picture",
    "tikzpicture", "displaymath", "math",
}
OWN_LINE = re.compile(
    r"^\s*\\(begin|end|part|chapter|section|subsection|subsubsection|appendix|label|input|include|centering|"
    r"includegraphics|newcommand|renewcommand|providecommand|DeclareRobustCommand|NewDocumentCommand|def|edef|gdef|"
    r"let|newif|newcounter|setcounter|setlength|addtolength|usepackage|documentclass|bibliography|printbibliography|"
    r"maketitle|tableofcontents|newpage|clearpage|FloatBarrier|vspace|hypersetup|setlist|definecolor|"
    r"externaldocument|addbibresource|graphicspath|pagestyle|thispagestyle|raggedbottom|newgeometry|"
    r"restoregeometry|frontmatter|mainmatter|backmatter|onecolumngrid|twocolumngrid|bigskip|medskip|smallskip|"
    r"noindent\s*$|makeatletter|makeatother|if[A-Z][A-Za-z]*|else|fi)\b")
STARTS_LINE = re.compile(r"^\s*\\(item|caption|paragraph|subparagraph|bibitem)\b")
DEFINITION = re.compile(r"^\s*\\(newcommand|renewcommand|providecommand|DeclareRobustCommand|NewDocumentCommand|def|"
                        r"edef|gdef|newenvironment|renewenvironment|setlist|hypersetup)\b")
SEPARATOR = re.compile(r"^[\s\-=*#~_+.]{4,}$")
BULLET = re.compile(r"^\s*([-*\u2022]|\d+[.)]|\([a-z0-9]+\))\s")
ENV = re.compile(r"\\(begin|end)\{([^}]*)\}")
CONTROL_WORD_END = re.compile(r"\\[A-Za-z@]+$")


def split_comment(line: str) -> tuple[str, str | None]:
    """(code, comment) where comment includes its leading `%`, or None. A `%` preceded by an odd number of
    backslashes is escaped."""
    i = 0
    while True:
        j = line.find("%", i)
        if j < 0:
            return line, None
        k, n = j - 1, 0
        while k >= 0 and line[k] == "\\":
            n, k = n + 1, k - 1
        if n % 2 == 0:
            return line[:j], line[j:]
        i = j + 1


def is_comment_line(line: str) -> bool:
    return line.lstrip().startswith("%")


def brace_depth(code: str) -> int:
    d, i = 0, 0
    while i < len(code):
        c = code[i]
        if c == "\\":
            i += 2
            continue
        d += c == "{"
        d -= c == "}"
        i += 1
    return d


def join_code(left: str, right: str, left_had_comment: bool) -> str:
    r = right.lstrip()
    if left_had_comment and left and not left[-1].isspace():
        if CONTROL_WORD_END.search(left) and r[:1].isalpha():
            return left + " " + r
        return left + r
    if left.endswith("\\ "):  # a control space must survive
        return left + r
    return left.rstrip() + " " + r


class Reflow:
    def __init__(self, lines: list[str], move_comments: bool):
        self.src = lines
        self.move = move_comments
        self.out: list[str] = []
        self.map: list[int] = []  # map[i] = 0-based output line holding source line i

    def emit(self, text: str, sources: list[int]) -> None:
        for s in sources:
            self.map[s] = len(self.out)
        self.out.append(text)

    def run(self) -> list[str]:
        self.map = [0] * len(self.src)
        stack: list[str] = []
        in_display = False
        i, n = 0, len(self.src)
        cur: str | None = None
        cur_src: list[int] = []
        cur_comment: str | None = None  # trailing comment on the last line joined into cur
        cur_had = False  # cur's last code line ended in a comment that has already been moved out
        moved: list[tuple[str, int]] = []  # comment lines to emit after cur
        crun: tuple[str, str, str] | None = None  # (indent, marker, text) of the open comment line
        crun_src: list[int] = []

        def flush_comment():
            nonlocal crun, crun_src
            if crun is not None:
                ind, mark, txt = crun
                self.emit(f"{ind}{mark} {txt}".rstrip() if txt else f"{ind}{mark}", crun_src)
                crun, crun_src = None, []

        def flush():
            nonlocal cur, cur_src, cur_comment, moved, cur_had
            if cur is not None:
                self.emit(cur + (cur_comment or ""), cur_src)
                for text, s in moved:
                    self.emit(text, [s])
            cur, cur_src, cur_comment, moved, cur_had = None, [], None, [], False

        def move_trailing():
            nonlocal cur_comment, cur_had
            if cur_comment is not None:
                ind = re.match(r"\s*", self.src[cur_src[0]]).group(0)
                moved.append((ind + cur_comment.strip(), cur_src[-1]))
                cur_comment, cur_had = None, True

        def protected() -> bool:
            return in_display or any(e in PROTECTED_ENVS for e in stack)

        def track(code: str) -> None:
            nonlocal in_display
            for m in ENV.finditer(code):
                if m.group(1) == "begin":
                    stack.append(m.group(2))
                elif stack and stack[-1] == m.group(2):
                    stack.pop()
                elif m.group(2) in stack:
                    while stack and stack.pop() != m.group(2):
                        pass
            if "\\[" in code and "\\]" not in code.split("\\[")[-1]:
                in_display = True
            if "\\]" in code and in_display:
                in_display = "\\[" in code.split("\\]")[-1]

        while i < n:
            line = self.src[i]
            # verbatim copy: inside a protected environment or display, or a blank line
            if protected() or not line.strip():
                flush_comment()
                flush()
                code, _ = split_comment(line)
                track(code)
                self.emit(line, [i])
                i += 1
                continue
            if is_comment_line(line):
                if cur is not None and not self.move:
                    flush()
                stripped = line.lstrip()
                ind = line[:len(line) - len(stripped)]
                mark = re.match(r"%+", stripped).group(0)
                txt = stripped[len(mark):].strip()
                if cur is not None and self.move:
                    # a comment inside a paragraph waits until the paragraph's text line is emitted
                    move_trailing()
                    moved.append((line.rstrip("\n"), i))
                    i += 1
                    continue
                fresh = (crun is None or crun[0] != ind or crun[1] != mark or not txt or SEPARATOR.match(txt)
                         or txt.startswith("\\") or BULLET.match(txt) or txt.startswith(("Search:", "absence-ok:"))
                         or not crun[2] or SEPARATOR.match(crun[2]))
                if fresh:
                    flush_comment()
                    crun, crun_src = (ind, mark, txt), [i]
                else:
                    crun = (ind, mark, crun[2] + " " + txt)
                    crun_src.append(i)
                i += 1
                continue
            flush_comment()
            code, comment = split_comment(line)
            if DEFINITION.match(line):
                flush()
                depth, j = brace_depth(code), i
                while depth > 0 and j + 1 < n:
                    j += 1
                    depth += brace_depth(split_comment(self.src[j])[0])
                for k in range(i, j + 1):
                    track(split_comment(self.src[k])[0])
                    self.emit(self.src[k], [k])
                i = j + 1
                continue
            own = bool(OWN_LINE.match(line)) or line.lstrip().startswith("&")
            starts = bool(STARTS_LINE.match(line))
            if own or starts or cur is None:
                flush()
                track(code)
                if own or protected():
                    self.emit(line, [i])
                else:
                    cur, cur_src, cur_comment = code.rstrip("\n"), [i], comment
                    if cur.rstrip().endswith("\\\\") or re.search(r"\\\\\[[^\]]*\]\s*$", cur):
                        flush()
                i += 1
                continue
            # join onto cur
            track(code)
            move_trailing()
            cur = join_code(cur, code, cur_had)
            cur_src.append(i)
            cur_comment, cur_had = comment, False
            if protected() or cur.rstrip().endswith("\\\\") or re.search(r"\\\\\[[^\]]*\]\s*$", cur):
                flush()
            i += 1
        flush_comment()
        flush()
        return self.out


def reflow_text(text: str, move_comments: bool) -> tuple[str, list[int]]:
    trailing_nl = text.endswith("\n")
    lines = text.split("\n")
    if trailing_nl:
        lines = lines[:-1]
    r = Reflow(lines, move_comments)
    out = r.run()
    return "\n".join(out) + ("\n" if trailing_nl else ""), r.map


NOTE_DIR = Path(__file__).resolve().parent
#: Written by generators, which own their layout: results_index.py and check_note_records.py entry-numbers.
GENERATED = {"records_results_index.tex", "records_estimators.tex", "records_entry_numbers.tex"}
#: The records closure. check_note_records.py P5 splits record paragraphs at comment-only lines, so a comment there
#: keeps its line.
KEEP_IN_PLACE = {"app_provenance.tex", "app_release_records.tex", "app_codebase_records.tex", "app_history.tex",
                 "main_records.tex"}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", nargs="*", type=Path)
    ap.add_argument("--note", action="store_true", help="every hand-written .tex of docs/analysis-note")
    ap.add_argument("--keep-comments-in-place", nargs="*", default=[], type=Path)
    ap.add_argument("--map", type=Path, help="write {file: [new 1-based line for each old line]}")
    ap.add_argument("--check", action="store_true", help="exit 1 if any file would change; write nothing")
    a = ap.parse_args(argv)
    if a.note:
        a.files = sorted(p for p in NOTE_DIR.glob("*.tex") if p.name not in GENERATED)
        a.keep_comments_in_place = [NOTE_DIR / n for n in KEEP_IN_PLACE]
    if not a.files:
        ap.error("no files (give FILE ... or --note)")
    keep = {p.resolve() for p in a.keep_comments_in_place}
    maps, changed = {}, []
    for f in a.files:
        text = f.read_text()
        new, m = reflow_text(text, f.resolve() not in keep)
        maps[str(f)] = [x + 1 for x in m]
        if new != text:
            changed.append(f)
            if not a.check:
                f.write_text(new)
        if new != text or not a.check:
            print(f"{f.name}: {text.count(chr(10))} -> {new.count(chr(10))} lines"
                  f"{'' if new != text else ' (unchanged)'}{' WOULD CHANGE' if a.check and new != text else ''}")
    if a.check:
        print(f"TEX-REFLOW :: {'FAIL' if changed else 'PASS'} -- {len(a.files)} sources, {len(changed)} with a "
              "paragraph or comment block split over several lines"
              + ("; run `python3 docs/analysis-note/reflow_tex.py --note`, check the typeset text is unchanged, "
                 "and commit" if changed else ""))
    if a.map:
        a.map.write_text(json.dumps(maps))
    return 1 if (a.check and changed) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
