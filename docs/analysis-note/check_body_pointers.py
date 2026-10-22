#!/usr/bin/env python3
"""Fail if the analysis note's BODY prints an internal-only pointer.

The note is to be depositable: a reader outside the analysis repository must be able to follow every printed
statement in the body. Tracker identifiers, repository paths, file names, commit or file digests and
"tracked in the known-issues log" pointers are therefore routed to the provenance part of the internal records
document (app_provenance.tex, input by main_records.tex since 2026-10-21, DECISION-20261021-joseph-da-and-note-records.md
item 2), which keeps them; the body states the substance and cites the record by its tag, in the form
"(Ref.~\\cite{NoteRecords2026}, \\texttt{tag})".

  python3 check_body_pointers.py              # exit 0 only if no body file prints an internal pointer
  python3 check_body_pointers.py --self-test  # the patterns fire on planted body pointers and stay silent on
                                              # the appendices, on comments and on the routed form

WHICH FILES ARE THE BODY. The population is derived, not listed: every file reached by \\input or \\include from
main_note.tex between \\title (or \\begin{document} if there is none) and \\appendix, recursively, plus main_note.tex's own
printed lines in that range (title block, abstract, acknowledgments). A new section added to the driver is therefore checked without editing
this file, and nothing after \\appendix is checked.

WHAT IS "PRINTED". LaTeX comments are removed; the arguments of \\label, \\ref, \\cite, \\includegraphics, \\input
and similar commands, which never print, are removed; zero-argument macros defined in preamble.tex, values.tex,
values_inference.tex and the driver are expanded (so a digest printed through a macro is seen), and the text of
each file is joined so that a pointer broken across two source lines is still one match.
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DRIVER = "main_note.tex"
MACRO_SOURCES = ("preamble.tex", "values.tex", "values_inference.tex")

# Each pattern names one kind of internal pointer. They are matched against printed text after `\_` -> `_` and
# `~` -> space, case-sensitively unless marked (?i).
PATTERNS = {
    "tracker-id": r"\b(?:VL|OI|KI)[- ]?\d+\b|\bKNOWN_?ISSUES\b|\bVALIDATION_?LEDGER\b",
    "known-issues-log": r"(?i)known[- ]issues|issues\s+log|validation\s+ledger",
    "record-name": r"\b(?:RECORD|DECISION|OUTCOME|PREREG|RECEIPT|REVIEW|AUDIT|EVIDENCE|CORRECTION|AUTHORIZATION"
                   r"|EXCEPTION|RULING|PLAN|DESIGN|REPORT|PROCEDURE|DELIVERY|INDEX)-\d{8}\b",
    "campaign-id": r"\bs5[a-z]\b|\bamendment \d+\b",
    "file-name": r"\b[\w.-]+\.(?:py|md|json|npz|npy|root|txt|tsv|csv|sh|yaml|yml|h5|ipynb|cpp|log|gz)\b",
    "repo-path": r"(?<![\w/])(?:docs|state|orchestration|nd-unfolding|2d-unfolding|3d-unfolding|publication"
                 r"|reproduction|tools|uq|stageC|stageF|minerva_paper_anc)/",
    "repo-url": r"github\.com/\S*/(?:blob|tree|commit)/|\\repopath\b",
    # A commit or file digest: 7-64 lowercase hex characters with at least one letter and one digit.
    "digest": r"\b(?=[0-9a-f]*[a-f])(?=[0-9a-f]*\d)[0-9a-f]{7,64}\b",
}
COMPILED = {k: re.compile(v) for k, v in PATTERNS.items()}

# Commands whose (first) brace argument never prints.
NONPRINTING = r"label|ref|eqref|pageref|autoref|cref|Cref|cite|citep|citet|nocite|includegraphics|input|include" \
              r"|addbibresource|bibliography|graphicspath|hypersetup|usepackage|documentclass|newif|setcounter" \
              r"|addcontentsline|begin|end|definecolor|ifthenelse"
NONPRINTING_RE = re.compile(r"\\(?:%s)\*?(?:\[[^\]]*\])*\{[^{}]*\}" % NONPRINTING)
DEF_RE = re.compile(r"\\(?:re)?(?:newcommand|providecommand)\*?\{?\\([A-Za-z@]+)\}?\s*\{")
DEFX_RE = re.compile(r"\\def\\([A-Za-z@]+)\s*\{")
INPUT_RE = re.compile(r"\\(?:input|include)\{([^{}]+)\}")


def strip_comment(line: str) -> str:
    m = re.search(r"(?<!\\)%", line)
    return line[:m.start()] if m else line


def balanced(text: str, i: int) -> tuple[str, int]:
    """The brace group whose opening brace is text[i-1]; returns (contents, index after the closing brace)."""
    depth, j = 1, i
    while j < len(text) and depth:
        if text[j] == "{" and text[j - 1] != "\\":
            depth += 1
        elif text[j] == "}" and text[j - 1] != "\\":
            depth -= 1
        j += 1
    return text[i:j - 1], j


def zero_arg_macros(paths: list[Path]) -> dict[str, str]:
    macros: dict[str, str] = {}
    for p in paths:
        if not p.exists():
            continue
        src = "\n".join(strip_comment(l) for l in p.read_text(errors="replace").splitlines())
        for rx in (DEF_RE, DEFX_RE):
            # The patterns require the body's brace right after the name, so a macro with arguments
            # (\newcommand{\x}[1]{...}) never matches and is never expanded.
            for m in rx.finditer(src):
                body, _ = balanced(src, m.end())
                macros.setdefault(m.group(1), body)
    return macros


def expand(text: str, macros: dict[str, str]) -> str:
    if not macros:
        return text
    rx = re.compile(r"\\(%s)(?![A-Za-z@])" % "|".join(re.escape(k) for k in sorted(macros, key=len, reverse=True)))
    for _ in range(6):
        new = rx.sub(lambda m: macros[m.group(1)], text)
        if new == text:
            break
        text = new
    return text


def printed_lines(path: Path) -> list[tuple[int, str]]:
    out = []
    for n, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
        out.append((n, strip_comment(line)))
    return out


def body_population(root: Path, driver: str = DRIVER) -> list[tuple[Path, int, int]]:
    """(file, first line, last line) for every body file; the driver contributes only its document range."""
    drv = root / driver
    lines = printed_lines(drv)
    start = next((n for n, l in lines if re.search(r"\\title\b", l)), None) or next((n for n, l in lines if "\\begin{document}" in l), None)
    stop = next((n for n, l in lines if re.search(r"\\appendix\b", l)), None)
    if start is None or stop is None:
        raise SystemExit(f"FAIL {drv}: cannot find \\begin{{document}} and \\appendix; the body cannot be delimited")
    pop: list[tuple[Path, int, int]] = [(drv, start, stop - 1)]
    seen = {drv.resolve()}

    def walk(path: Path, lo: int, hi: int) -> None:
        for n, l in printed_lines(path):
            if n < lo or n > hi:
                continue
            for m in INPUT_RE.finditer(l):
                name = m.group(1).strip()
                child = root / (name if name.endswith(".tex") else name + ".tex")
                if not child.exists():
                    raise SystemExit(f"FAIL {path.name}:{n}: \\input{{{name}}} names no file; the body is incomplete")
                if child.resolve() in seen:
                    continue
                seen.add(child.resolve())
                pop.append((child, 1, 10 ** 9))
                walk(child, 1, 10 ** 9)

    walk(drv, start, stop - 1)
    return pop


def scan(root: Path, driver: str = DRIVER) -> list[str]:
    macros = zero_arg_macros([root / s for s in MACRO_SOURCES] + [root / driver])
    hits: list[str] = []
    for path, lo, hi in body_population(root, driver):
        chunks, linemap, pos = [], [], 0
        for n, l in printed_lines(path):
            if n < lo or n > hi:
                continue
            l = NONPRINTING_RE.sub(" ", l)
            l = expand(l, macros)
            l = NONPRINTING_RE.sub(" ", l)
            l = l.replace("\\_", "_").replace("~", " ").replace("\\allowbreak", "").replace("\\-", "")
            chunks.append(l)
            linemap.append((pos, n))
            pos += len(l) + 1
        # Joined with single spaces of the same length as the newlines, so a match offset maps back to its line
        # and a pointer broken across two source lines is still one match.
        text = " ".join(chunks)
        for name, rx in COMPILED.items():
            for m in rx.finditer(text):
                line = max((n for p, n in linemap if p <= m.start()), default=lo)
                hits.append(f"{path.name}:{line}: [{name}] {m.group(0)!r}")
    return hits


# ---------------------------------------------------------------------------------------------------------------
# Self-test: the patterns must fire in the direction they act and stay silent in the other.

PLANTS = {
    "tracker-id": r"the band (labelled \texttt{VL170} in the appendices)",
    "known-issues-log": "the defect is tracked in the analysis repository's known-issues\nlog.",
    "record-name": r"see \texttt{RECORD-20261005-s5p-joint-5d-inference-result}",
    "campaign-id": "the campaign s5p, frozen as amendment~7,",
    "file-name": r"the central value (\texttt{2d\_xsec\_MEFHC\_5iter\_lgbm\_uni\_full\_CV.root})",
    "repo-path": r"the mapping in \texttt{minerva\_paper\_anc/bin\_mapping}",
    "repo-url": r"\href{https://github.com/x/y/blob/7d173bd/docs/z}{the record}",
    "digest": r"sha256 \texttt{4f5a1b6d}\ldots",
}
DIGEST_MACRO_PLANT = r"(\texttt{sha256}~\fakeDigest\ldots)"
SILENT_IN_BODY = [
    r"% a comment may keep KNOWN_ISSUES row 85, VL170 and docs/orchestration/RECORD-20261005-x.md",
    r"(Ref.~\cite{NoteRecords2026}, \texttt{joint-5d}; Ref.~\cite{NoteRecords2026}, \texttt{z-adoption})",
    r"(Ref.~\cite{NoteRecords2026}, superseded values: retired material)",
    r"\includegraphics[width=\linewidth]{figures/gbdt_recovery.pdf}",
    r"\label{sec:uq-boot} \ref{app:history-vl175} \cite{JointTestRecord2026}",
    r"GENIE~2.12.10, $\lambda=4.36\times10^{-92}$, \num{890500272} bytes, 1.4\% and 0.07 null SD",
    r"\texttt{numpy.linalg.matrix\_rank} and \texttt{negweight-refined}; Fig.~3 and e.g. this",
]


def _tree(tmp: Path, body: str, appendix: str, rows: str = "") -> Path:
    (tmp / "preamble.tex").write_text("\\newcommand{\\repourl}{https://github.com/x/y}\n")
    (tmp / "values.tex").write_text("\\newcommand{\\fakeDigest}{3d7465f6}  % first 8 of a sha256\n")
    (tmp / DRIVER).write_text(
        "\\documentclass{article}\n\\input{preamble}\n\\input{values}\n\\begin{document}\n"
        "\\input{sec_a}\n\\appendix\n\\input{app_g}\n\\end{document}\n")
    (tmp / "sec_a.tex").write_text("Body text.\n\\input{rows_a}\n" + body + "\n")
    (tmp / "rows_a.tex").write_text(rows + "\n")
    (tmp / "app_g.tex").write_text(appendix + "\n")
    return tmp


def self_test() -> int:
    failures = []
    every_plant = "\n".join(PLANTS.values()) + "\n" + DIGEST_MACRO_PLANT
    with tempfile.TemporaryDirectory() as d:
        root = _tree(Path(d), "", every_plant)
        hits = scan(root)
        if hits:
            failures.append(f"the appendix must stay silent, but fired: {hits}")
    for name, plant in PLANTS.items():
        with tempfile.TemporaryDirectory() as d:
            hits = scan(_tree(Path(d), plant, ""))
            if not any(f"[{name}]" in h for h in hits):
                failures.append(f"{name}: a planted body pointer did not fire: {plant!r} -> {hits}")
        with tempfile.TemporaryDirectory() as d:  # the same plant in a NESTED body file (discovery, not a list)
            hits = scan(_tree(Path(d), "", "", rows=plant))
            if not any(f"[{name}]" in h and "rows_a.tex" in h for h in hits):
                failures.append(f"{name}: a pointer in a body file reached only by a nested \\input did not fire")
    with tempfile.TemporaryDirectory() as d:
        hits = scan(_tree(Path(d), DIGEST_MACRO_PLANT, ""))
        if not any("[digest]" in h and "3d7465f6" in h for h in hits):
            failures.append(f"a digest printed through a values.tex macro did not fire: {hits}")
    for text in SILENT_IN_BODY:
        with tempfile.TemporaryDirectory() as d:
            hits = scan(_tree(Path(d), text, ""))
            if hits:
                failures.append(f"false positive on {text!r}: {hits}")
    n = 1 + 2 * len(PLANTS) + 1 + len(SILENT_IN_BODY)
    if failures:
        print("BODY-POINTERS SELF-TEST :: FAIL")
        for f in failures:
            print("  " + f)
        return 1
    print(f"BODY-POINTERS SELF-TEST :: PASS ({n} cases: the appendix silent; {len(PLANTS)} patterns fire in a body file "
          f"and in a nested body file; a macro-printed digest fires; {len(SILENT_IN_BODY)} legitimate forms silent)")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    root = HERE
    rest = [a for a in argv if not a.startswith("--")]
    if rest:
        root = Path(rest[0]).resolve()
    hits = scan(root)
    files = len(body_population(root))
    if hits:
        print(f"BODY-POINTERS :: FAIL ({len(hits)} internal pointer(s) printed in the body; route each to "
              f"the records document (Ref.~\\cite{{NoteRecords2026}}, \\texttt{{tag}}) and state the substance in the body)")
        for h in hits:
            print("  " + h)
        return 1
    print(f"BODY-POINTERS :: PASS (0 internal pointers in {files} body files)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
