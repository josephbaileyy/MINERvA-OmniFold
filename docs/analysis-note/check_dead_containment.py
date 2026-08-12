#!/usr/bin/env python3
"""Assert that struck (retracted) values reach the NOTE build and no other.

WHY THIS EXISTS, AND WHY IT IS NOT A BUILD FLAG
-----------------------------------------------
`\\dead{}` (preamble.tex) renders a retracted value struck-through and grey. Strike-not-erase is
right for an internal audit trail and wrong for anything outward-facing.

The oversight session reported that the macro "renders in all three builds" and recommended making
it build-conditional on `\\ifPAPER`. That premise was WRONG and the recommendation would have made
things worse. Measured 2026-08-11: the five struck magnitudes appear 8x in main_note.pdf and 0x in
main_paper.pdf / main_primer.pdf. The macro is DEFINED in the shared preamble but USED only in
`app_statmethods.tex` and `sec_pet.tex`, and those two files are `\\input` by main_note ONLY. A
build-conditional would have been a conditional guarding a case that cannot occur -- and an
unnecessary conditional is one more gate that can silently fail the wrong way.

But the containment is INCIDENTAL, not enforced: it holds because of which files the paper happens
to include. Add `app_statmethods` to paper_body, or write one `\\dead{}` into paper_body.tex, and
struck retracted numbers appear in a paper-bound PDF with nothing complaining. This test converts
that accident into an invariant.

BOTH DIRECTIONS ARE CHECKED ON PURPOSE
    paper/primer: no `\\dead{}` in the include closure   (the containment)
    note:         `\\dead{}` IS present, and the values DO appear in its PDF  (the positive control)
A test that only asserted absence would pass if `\\dead{}` vanished from the repo entirely, or if
the note quietly stopped marking its retractions. That is this repo's most-repeated defect shape --
a gate that cannot fail -- so the positive control is not optional.

The struck values are DERIVED from the sources, never hardcoded: a hardcoded list silently stops
covering anything added after it was written. Macro-valued `\\dead{\\petRatio}` bodies are resolved
through values.tex, and any body this script cannot reduce to a literal is REPORTED rather than
skipped quietly.

Usage:  python3 check_dead_containment.py [--dir <analysis-note dir>]
Exit 0 = invariant holds. Exit 1 = violation or an unresolvable input.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

BUILDS = {"main_note": "note", "main_paper": "paper", "main_primer": "primer"}
STRUCK_ALLOWED_IN = "main_note"

INPUT_RE = re.compile(r"\\(?:input|include)\{([^}]+)\}")
# `\s*` is load-bearing and BEN-090 is the reason. This read `r"\\dead\{"` from 4f75e50 until
# 2026-08-12: enforcement landed and was evadable by one character, because `\dead {x}` renders
# identically and did not match. The evasion form is NOT hypothetical and not an imagined careless
# author -- LaTeX EMITS it. `sec_pet.tex:91` is `$\dead{\petRatio}$`, unspaced, and `\newlabel`
# serialises it into `main_note.aux:345` as `\dead {\petRatio }`. So the string this regex could not
# match is the string LaTeX writes when it round-trips its own input. Consequence worth keeping:
# the natural "robust" way to build an include closure is to read the build's own .aux or .fls
# instead of regex-parsing \input, and any check that does so reads precisely the form the old
# pattern was blind to -- the better instrument walks straight into the hole.
# `match_braced(text, m.end() - 1)` still holds: the match ends at `{` whatever precedes it.
#
# AND `\s*` ALONE IS STILL NOT ENOUGH. Session D demonstrated the residual end to end on a copy:
#
#     \noindent CommentEvade: $\dead%c
#     {9.87654}$ here.
#
# checker PASS exit 0, `latexmk -pdf main_paper` exit 0, and `pdftotext main_paper.pdf` line 1013
# reads "CommentEvade: 9.87654 here." TeX skips a comment AND its terminating newline while scanning
# for an undelimited argument, so `\dead%<comment>\n{x}` is the same token stream as `\dead{x}` --
# and `%` is not whitespace, so `\s*` does not reach it. Comments are therefore stripped BEFORE
# matching, and the negative lookbehind is load-bearing: without it `\dead{50\%}` would be corrupted
# by the strip and the check would stop finding a body that exists.
#
# Occupied vs latent, because they are not the same risk: the SPACED form is emitted by the build
# today (`\newlabel` serialises `\dead{\petRatio}` into `main_note.aux:345` as `\dead {\petRatio }`).
# Nothing emits the COMMENT form today. Both are covered; only one is currently occupied.
COMMENT_RE = re.compile(r"(?<!\\)%[^\n]*")  # `[^\n]*`, not `.*?\n`, so line positions are preserved
DEAD_RE = re.compile(r"\\dead\s*\{")


def strip_comments(text: str) -> str:
    """Remove TeX comments, honouring an escaped `\\%`. Newlines are preserved."""
    return COMMENT_RE.sub("", text)


def dead_spans(text: str) -> list[str]:
    """Bodies of every `\\dead{...}` in `text`, across whitespace and comment separation."""
    scanned = strip_comments(text)
    out = []
    for m in DEAD_RE.finditer(scanned):
        body = match_braced(scanned, m.end() - 1)
        if body is not None:
            out.append(body)
    return out
NEWCMD_RE = re.compile(r"\\newcommand\{\\([A-Za-z]+)\}\{([^}]*)\}")
# a decimal literal with at least one digit after the point -- bare integers are far too
# collision-prone to search for in a rendered PDF
NUM_RE = re.compile(r"\d+\.\d+")


def resolve_closure(root: Path, seen: set[Path] | None = None) -> list[Path]:
    """Transitive \\input/\\include closure of a driver .tex, in discovery order."""
    if seen is None:
        seen = set()
    out: list[Path] = []
    if root in seen or not root.exists():
        return out
    seen.add(root)
    out.append(root)
    for name in INPUT_RE.findall(root.read_text(encoding="utf-8", errors="replace")):
        child = root.parent / (name if name.endswith(".tex") else name + ".tex")
        out.extend(resolve_closure(child, seen))
    return out


def match_braced(text: str, open_idx: int) -> str | None:
    """Return the balanced-brace body starting at the '{' at open_idx."""
    depth = 0
    for i in range(open_idx, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[open_idx + 1 : i]
    return None


def dead_bodies(path: Path) -> list[str]:
    return dead_spans(path.read_text(encoding="utf-8", errors="replace"))


def macro_table(note_dir: Path) -> dict[str, str]:
    values = note_dir / "values.tex"
    if not values.exists():
        return {}
    return dict(NEWCMD_RE.findall(values.read_text(encoding="utf-8", errors="replace")))


def literals_from(body: str, macros: dict[str, str]) -> tuple[set[str], list[str]]:
    """Decimal literals implied by a \\dead{} body. Returns (literals, unresolved macro names)."""
    expanded = body
    unresolved = []
    for name in re.findall(r"\\([A-Za-z]+)", body):
        if name in macros:
            expanded += " " + macros[name]
    nums = set(NUM_RE.findall(expanded))
    if not nums:
        # No decimal literal, so the PDF stage cannot search for this one. Usually an
        # integer-only body (`\approx\!70\%`): a bare integer collides with page numbers, bin
        # counts and years in a rendered PDF, so searching for it would produce false failures.
        # Report the body verbatim -- naming the LaTeX commands inside it would describe the
        # wrong thing, and this line's whole job is to make the coverage gap legible.
        unresolved = [" ".join(body.split()) or "<empty>"]
    return nums, unresolved


def pdf_text(pdf: Path, tmp: Path) -> str | None:
    if not pdf.exists() or not shutil.which("pdftotext"):
        return None
    dest = tmp / (pdf.stem + ".txt")
    try:
        subprocess.run(["pdftotext", "-q", str(pdf), str(dest)], check=True)
    except (subprocess.CalledProcessError, OSError):
        return None
    return dest.read_text(encoding="utf-8", errors="replace") if dest.exists() else None


_OLD_DEAD_RE = re.compile(r"\\dead\{")  # the pre-2026-08-12 pattern, kept ONLY as a power control


def self_test() -> int:
    """Power test for DEAD_RE. Every positive case must FAIL against the old pattern.

    A test that passes against both patterns is not a power test -- it would have shipped green
    beside the defect it exists to catch, which is the shape of the gate this repairs.
    """
    # THE BATTERY IS THE FORM SET, NOT ONE VARIANT (Session D). The first version of this suite
    # covered whitespace only: it passed against `\s*` and failed against the old pattern, so it
    # looked like a real power test while `\dead%c\n{` was still live and rendering. Every
    # separator TeX accepts between an undelimited control sequence and its argument belongs here.
    # (label, text, must_match)
    cases = [
        ("unspaced, the form already in the tree", r"$\dead{\petRatio}$", True),
        ("one space -- the BEN-090 evasion", r"$\dead {\petRatio}$", True),
        ("LaTeX \\newlabel serialisation, verbatim from main_note.aux:345",
         r"The PET/GBDT total ratio is $\dead {\petRatio }$", True),
        ("multiple spaces", r"\dead   {0.912}", True),
        ("tab", "\\dead\t{0.912}", True),
        ("newline", "\\dead\n{0.912}", True),
        ("newline + indent", "\\dead\n    {0.912}", True),
        ("comment -- D's demonstrated evasion, renders in main_paper.pdf",
         "\\dead%c\n{9.87654}", True),
        ("comment after a space", "\\dead %c\n{9.87654}", True),
        ("two consecutive comment lines", "\\dead%a\n%b\n{9.87654}", True),
        ("ESCAPED PERCENT must still be FOUND -- a naive comment strip breaks this",
         r"\dead{50\%}", True),
        ("negative control: a longer command name must NOT match", r"\deadline{2026}", False),
        ("negative control: prose mentioning the macro", r"the \\dead marker", False),
        ("negative control: no brace", r"\dead", False),
        ("negative control: the whole use is inside a comment", "% \\dead{0.912}\n", False),
    ]
    failures, powerless = [], []
    for label, text, must_match in cases:
        got = bool(dead_spans(text))
        if got != must_match:
            failures.append(f"{label}: expected match={must_match}, got {got}")
        # A positive case is only a POWER case if the old pattern misses it.
        if must_match and bool(_OLD_DEAD_RE.search(text)):
            powerless.append(label)

    # Matching is not enough: the BODY must survive comment-stripping intact, or the PDF stage
    # searches for the wrong literal and reports a clean paper because it looked for nothing.
    body_cases = [
        (r"\dead{50\%}", r"50\%"),
        ("\\dead%c\n{9.87654}", "9.87654"),
        (r"$\dead {\petRatio }$", r"\petRatio "),
    ]
    for text, want in body_cases:
        got_bodies = dead_spans(text)
        if got_bodies != [want]:
            failures.append(f"body extraction: {text!r} -> {got_bodies!r}, expected [{want!r}]")

    # Both directions: the negative controls must also be negative under the old pattern, or they
    # are not telling us anything about the change.
    if len(powerless) == len([c for c in cases if c[2]]):
        failures.append("NO positive case discriminates: every one also matches the old pattern, "
                        "so this suite would have passed before the fix and proves nothing")
    # And the fix must not have been achieved by matching everything.
    if not any(not c[2] for c in cases):
        failures.append("no negative controls present")

    for label, text, must_match in cases:
        mark = "power" if (must_match and label not in powerless) else "     "
        print(f"  {mark}  {'match ' if must_match else 'reject'}  {label}")
    n_power = len([c for c in cases if c[2]]) - len(powerless)
    print(f"  {n_power} of {len([c for c in cases if c[2]])} positive cases discriminate against "
          f"the pre-2026-08-12 pattern")
    for f in failures:
        print(f"  FAIL {f}")
    print("SELF-TEST :: " + ("PASS" if not failures else "FAIL"))
    return 0 if not failures else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=str(Path(__file__).resolve().parent))
    ap.add_argument("--tmp", default="/tmp")
    ap.add_argument("--self-test", action="store_true",
                    help="run the DEAD_RE power test and exit; checks no documents")
    ap.add_argument("--source-only", action="store_true",
                    help="DIAGNOSTIC MODE. Downgrade a missing/unreadable PDF stage from FAIL to a "
                         "note. build_all.sh MUST NEVER pass this: under the 2026-08-12 contract "
                         "exit 0 means BOTH the source and PDF stages ran and passed, and this "
                         "flag exists so that a human debugging without a TeX install has a way "
                         "to run the source half -- not so that CI can look green without PDFs.")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    strict = not args.source_only
    note_dir = Path(args.dir).resolve()
    tmp = Path(args.tmp)
    tmp.mkdir(parents=True, exist_ok=True)

    macros = macro_table(note_dir)
    failures: list[str] = []
    notes: list[str] = []

    # ---- source-level: exact, and the hard invariant ---------------------------------------
    struck_values: set[str] = set()
    unresolved: list[str] = []
    for driver, label in BUILDS.items():
        closure = resolve_closure(note_dir / f"{driver}.tex")
        if len(closure) <= 1:
            failures.append(f"{driver}: include closure did not resolve ({len(closure)} file) -- "
                            f"the check cannot vouch for this build")
            continue
        users = []
        for path in closure:
            # the definition itself lives in preamble.tex and is not a use
            if path.name == "preamble.tex":
                continue
            bodies = dead_bodies(path)
            if bodies:
                users.append((path.name, bodies))
        n_uses = sum(len(b) for _, b in users)
        if driver == STRUCK_ALLOWED_IN:
            if n_uses == 0:
                failures.append(
                    "main_note: ZERO \\dead{} uses. Either the retraction marking was removed, or "
                    "this test is now vacuous. A containment test whose positive control is empty "
                    "proves nothing.")
            else:
                notes.append(f"note: {n_uses} \\dead{{}} uses across "
                             f"{', '.join(n for n, _ in users)}")
                for _, bodies in users:
                    for body in bodies:
                        nums, unres = literals_from(body, macros)
                        struck_values |= nums
                        unresolved.extend(unres)
        elif n_uses:
            for name, bodies in users:
                failures.append(f"{driver} ({label} build) reaches {n_uses} \\dead{{}} use(s) via "
                                f"{name}: {bodies[:3]}{'...' if len(bodies) > 3 else ''} -- struck "
                                f"retracted values would render in an outward-facing PDF")
        else:
            notes.append(f"{label}: clean, 0 \\dead{{}} in a {len(closure)}-file closure")

    if unresolved:
        uncovered = sorted(set(unresolved))
        notes.append(f"PDF stage does NOT cover {len(uncovered)} \\dead{{}} bod(ies) -- no decimal "
                     f"literal to search for, so only the source check guards these: "
                     + "; ".join(uncovered))

    # ---- PDF-level ------------------------------------------------------------------------
    # CONTRACT CHANGED 2026-08-12 on Joseph's decision: "exit 0 must mean both the source and PDF
    # stages ran and passed. Missing PDFs or pdftotext must be nonzero in build_all.sh." Previously
    # every skip below was a `note` and the run still returned 0, so on a machine without
    # `pdftotext` the check was silently HALF a check -- and worst of all it was machine-dependent,
    # passing here and skipping there with no difference in output status. A skip is now a FAILURE
    # unless --source-only is passed explicitly.
    _skip = notes.append if not strict else failures.append

    def _skipped(msg: str) -> None:
        _skip(msg + ("" if not strict else "  [PDF stage did not run; exit 0 would misreport it. "
                                           "Build the PDFs, install pdftotext, or pass "
                                           "--source-only to accept a source-only check]"))

    if not struck_values:
        _skipped("no struck literals derived -- PDF stage cannot run")
    else:
        note_txt = pdf_text(note_dir / "main_note.pdf", tmp)
        if note_txt is None:
            _skipped("main_note.pdf absent or pdftotext unavailable -- PDF stage skipped")
        else:
            seen_in_note = sorted(v for v in struck_values if v in note_txt)
            if not seen_in_note:
                failures.append(
                    f"none of the {len(struck_values)} derived struck literals appear in "
                    f"main_note.pdf -- the derivation is broken, so absence elsewhere means nothing")
            else:
                notes.append(f"note.pdf carries {len(seen_in_note)}/{len(struck_values)} struck "
                             f"literals (positive control OK)")
                for driver, label in BUILDS.items():
                    if driver == STRUCK_ALLOWED_IN:
                        continue
                    txt = pdf_text(note_dir / f"{driver}.pdf", tmp)
                    if txt is None:
                        _skipped(f"{driver}.pdf absent -- {label} build NOT PDF-checked, and this "
                                 f"is the outward-facing build the whole check exists to protect")
                        continue
                    hits = sorted(v for v in seen_in_note if v in txt)
                    if hits:
                        failures.append(
                            f"{driver}.pdf contains struck literal(s) {hits} that main_note.pdf "
                            f"also carries as \\dead{{}} -- verify by eye before treating as a "
                            f"digit coincidence, then narrow this check rather than deleting it")
                    else:
                        notes.append(f"{label}.pdf: 0 of {len(seen_in_note)} struck literals")

    for n in notes:
        print(f"  ok   {n}")
    for f in failures:
        print(f"  FAIL {f}")
    print("RESULT :: " + ("PASS" if not failures else "FAIL"))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
