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

# NARROWED 2026-08-21, on this check's own instruction ("narrow this check rather than deleting
# it") after the 6c negweight gate made it FAIL on five values that were ALL digit coincidences,
# verified by eye in both outward PDFs:
#     0.13 -> the arXiv id `2110.13372`      1.4  -> figure axis ticks `1.45`, `1.40`
#     12.6 -> the generator version `2.12.6`  6.8  -> the LIVE values `6.87 %` / `6.86 %`
#     0.3  -> figure axis ticks `0.25 < p_T < 0.33` and a bare tick `x 0.3`
# TWO INDEPENDENT NARROWINGS, because either alone still misfires:
#   (1) TOKEN BOUNDARY. The old test was `v in txt`, a substring, so `6.8` matched `6.87` -- it
#       reported a struck value leaking when what was present was a DIFFERENT, LIVE number that
#       happens to start with the same digits. A struck literal now has to appear as a whole
#       number token, with no digit or `.` adjacent on either side.
#   (2) MINIMUM SIGNIFICANT DIGITS. Boundary matching alone still fails on `0.3`, because a bare
#       `0.3` is a real axis tick in a document full of plots. The existing comment above already
#       reasons this way about bare integers ("far too collision-prone"); two significant digits
#       is the same problem one step along. Values below the threshold are NOT dropped silently --
#       they are reported in the same named coverage-gap line as integer-only bodies, so the gap
#       stays legible and the source stage still guards them.
# WHAT THIS DELIBERATELY DOES NOT DO: it does not weaken coverage of any value that can actually
# discriminate. Every 6b/6a literal stays covered -- 94.1, 77.6, 98.5, 1.006, 3.0727e-38, 0.9987,
# 0.986, 0.982, 0.999, 1.000, 10.9 all carry three or more significant digits.
SIG_MIN = 3

#: A GATE SCOPED TO ONE FILE CANNOT REACH A USAGE IN ANOTHER, and the 6c gate proved it: all 16
#: `\nw*` macros were struck in `app_negweight.tex` and the gate was recorded as complete, while
#: `sec_method.tex` quoted `\nwPctTot` LIVE the whole time. Found by the negweight durability lane,
#: not by this checker, which is the gap being closed here. Same mechanism as OI-146's derived
#: descendants: enumerate the USAGES, never one file's usages.
#: THE GATED SET IS DECLARED, NOT INFERRED, so ungating is a deliberate act that has to edit this
#: list. The four synthetic-toy values (nwToyNeg, nwToyPur, nwToyBias, nwToySeed) were never in it:
#: they are attested by a committed deterministic producer.
#:
#: EMPTIED 2026-08-21 BY THE NEGWEIGHT DURABILITY LANE, on Joseph's ruling, and empty rather than
#: deleted so the next gating has somewhere to go. The twelve real-data/production values were gated
#: because they rested on untracked scratch; their 247 backing ROOTs are now on tape, digest-verified
#: server-side, confirmed by a full read off tape, and RESTORED end to end -- 247 of 247 recovered,
#: digest-matched and reopened -- by a committed, adversarially tested route.
#: nwSystResid and nwStatResid leave with them because they are \fpeval-DERIVED from nwSystRatio and
#: nwStatRatio (OI-146): a descendant cannot be gated independently of its parent without the gate
#: asserting two different things about one number.
#: Evidence: docs/orchestration/RECEIPT-20260821-negweight-hpss-durability.md and
#: docs/orchestration/state/negweight-hpss-durability-20260821.json.
#: WHAT UNGATING DID NOT DO: it did not make negative-weight injection a supported production path
#: and it changed no default. That is a claim about the note's PROSE, which this checker does not and
#: should not police -- do not add a keyword rule here for it.
#: AN EMPTY SET MAKES THIS CHECK INERT, WHICH IS WHY IT NOW HAS A TEST. With no gated names the
#: detector iterates over nothing and reports success by looking at nothing -- this repo's most
#: repeated defect shape, and installing it silently would be worse than the gap it replaced.
#: test_build_all.py::GatedMacroDetectorTest exercises it against a synthetic note directory in both
#: directions, so the mechanism stays proven while the production set is empty.
GATED_NW_MACROS = ()


def gated_macro_usages(note_dir):
    r"""Every usage of a GATED macro outside values.tex, with whether it is inside `\dead{}`.

    Returns `(live, struck)` as lists of "file:line". A macro NAMED as text -- e.g.
    `\texttt{\textbackslash nwSigPur}` in a provenance notice -- is not a usage and is excluded,
    because printing a macro's NAME is how a gate notice explains itself without defeating itself.
    """
    live, struck = [], []
    for path in sorted(note_dir.glob("*.tex")):
        if path.name == "values.tex":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        spans = []
        for m in DEAD_RE.finditer(text):
            body = match_braced(text, m.end() - 1)
            if body is not None:
                spans.append((m.start(), text.index(body, m.end() - 1) + len(body)))
        for name in GATED_NW_MACROS:
            for m in re.finditer(r"\\" + name + r"(?![A-Za-z])", text):
                # `\textbackslash nwFoo` is the macro's NAME in prose, not a use of it
                before = text[max(0, m.start() - 40):m.start()]
                if "textbackslash" in before:
                    continue
                where = f"{path.name}:{text.count(chr(10), 0, m.start()) + 1}"
                inside = any(a <= m.start() <= b for a, b in spans)
                (struck if inside else live).append(f"{where} \\{name}")
    return live, struck


def sig_digits(v: str) -> int:
    """Significant digits in a decimal literal: leading zeros are not significant."""
    return len(v.replace(".", "").lstrip("0"))


def token_hit(value: str, text: str) -> bool:
    """True only if `value` appears as a complete number token, not inside a longer number."""
    return re.search(r"(?<![\d.])" + re.escape(value) + r"(?![\d.])", text) is not None


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
    all_nums = set(NUM_RE.findall(expanded))
    nums = {v for v in all_nums if sig_digits(v) >= SIG_MIN}
    thin = sorted(all_nums - nums)
    if thin:
        unresolved.append(
            " ".join(body.split()) + f"  [PDF-uncoverable: {', '.join(thin)} "
            f"-- under {SIG_MIN} significant digits, indistinguishable from an axis tick or a "
            f"version number in a rendered PDF; source check only]")
    if not all_nums:
        # No decimal literal, so the PDF stage cannot search for this one. Usually an
        # integer-only body (`\approx\!70\%`): a bare integer collides with page numbers, bin
        # counts and years in a rendered PDF, so searching for it would produce false failures.
        # Report the body verbatim -- naming the LaTeX commands inside it would describe the
        # wrong thing, and this line's whole job is to make the coverage gap legible.
        unresolved = [" ".join(body.split()) or "<empty>"]
    return nums, unresolved


def pdf_text(pdf: Path, tmp: Path) -> str | None:
    """Extract searchable text without allowing an unavailable backend to skip the PDF gate."""
    if not pdf.exists():
        return None
    dest = tmp / (pdf.stem + ".txt")
    pdftotext = shutil.which("pdftotext")
    gs = shutil.which("gs")
    if pdftotext:
        command = [pdftotext, "-q", str(pdf), str(dest)]
    elif gs:
        # NERSC's TeX module has Ghostscript but not Poppler.  txtwrite supplies
        # the non-empty rendered-PDF text this literal-containment gate needs.
        command = [
            gs,
            "-q",
            "-dSAFER",
            "-dBATCH",
            "-dNOPAUSE",
            "-sDEVICE=txtwrite",
            f"-sOutputFile={dest}",
            str(pdf),
        ]
    else:
        return None
    try:
        subprocess.run(command, check=True)
    except (subprocess.CalledProcessError, OSError):
        return None
    if not dest.exists():
        return None
    # AN EMPTY EXTRACTION IS NOT A SEARCH. A PDF extractor can SUCCEED and produce nothing -- an
    # image-only or outlined PDF. Returning "" made `v in txt` false for every struck literal, so
    # an outward build reported "0 of 17 struck literals": literally true, completely uninformative,
    # and indistinguishable in the output from a real clean result. The note side was protected by
    # its positive control; the outward builds, which are the ones this check exists to protect,
    # were not. Found by Session D on 98b926a with a fake pdftotext that succeeded empty for
    # main_paper.pdf only, so the note control still passed and the run still exited 0.
    # LATENT, NOT OCCUPIED: D could not produce it from latexmk with a real PDF, only by simulating
    # an extractor. Same distinction as spaced (emitted by the build today) vs comment (not).
    # Returning None routes it into the existing strict-fatal path with no new mechanism.
    text = dest.read_text(encoding="utf-8", errors="replace")
    return text if text.strip() else None


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
                    help="DIAGNOSTIC MODE. Downgrade a missing/unreadable/empty PDF stage from FAIL "
                         "to a note. build_all.sh MUST NEVER pass this. Contract, worded to "
                         "match the code rather than wider than it: exit 0 means the source "
                         "stage passed AND the PDF stage RAN over every literal it can cover. "
                         "It does not mean every struck body was PDF-checked -- bodies with no "
                         "decimal literal are uncoverable by construction and are reported as a "
                         "named coverage gap, not silently. This flag is for a human debugging "
                         "without a TeX install, not so CI can look green without PDFs.")
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

    # BUILDS is hardcoded, so a fourth outward-facing driver added later would be silently
    # unchecked -- BEN-095's corpus shape, where the instrument's scope is narrower than its claim
    # and nothing says so. Assert the dict against the tree rather than deriving it: derivation
    # would make a new driver checked-but-unnamed, and an outward build should not become
    # load-bearing here without someone writing down what audience it is for. (Session D's scope
    # note on 98b926a; complete at the time, which is exactly when to pin it.)
    on_disk = {p.stem for p in sorted(note_dir.glob("*.tex"))
               if "\\documentclass" in p.read_text(encoding="utf-8", errors="replace")}
    if on_disk != set(BUILDS):
        failures.append(
            f"BUILDS is stale: drivers on disk {sorted(on_disk)} != BUILDS {sorted(BUILDS)}. "
            f"Unlisted={sorted(on_disk - set(BUILDS))}, listed-but-absent="
            f"{sorted(set(BUILDS) - on_disk)}. An unlisted driver is an UNCHECKED build; add it to "
            f"BUILDS with its audience label rather than deleting this assert.")

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

    # THE CROSS-FILE GATE CHECK. Scoped to the USAGES, not to one file.
    gated_live, gated_struck = gated_macro_usages(note_dir)
    if gated_live:
        failures.append(
            f"{len(gated_live)} GATED \\nw* usage(s) are NOT inside \\dead{{}}: "
            f"{gated_live}. A gate recorded as complete while a usage survives in another file is "
            f"the 6c defect verbatim -- either strike these or remove the macro from "
            f"GATED_NW_MACROS deliberately.")
    elif not GATED_NW_MACROS:
        # Say INERT, not PASS. "all 0 gated usages are inside \dead{}" is true of any tree and would
        # read as coverage in a log skimmed months later.
        notes.append("GATED_NW_MACROS is EMPTY -- the gated-macro check is inert by declaration, not "
                     "passing on evidence. Nothing is currently gated; see this file's comment for "
                     "who emptied it and why. The detector itself stays covered by "
                     "test_build_all.py::GatedMacroDetectorTest.")
    else:
        notes.append(f"all {len(gated_struck)} gated \\nw* usage(s) are inside \\dead{{}}, across "
                     f"every .tex in the closure -- not just app_negweight.tex")

    if unresolved:
        uncovered = sorted(set(unresolved))
        notes.append(f"PDF stage does NOT cover {len(uncovered)} \\dead{{}} bod(ies) -- no decimal "
                     f"literal, or none with >={SIG_MIN} significant digits, so only the source "
                     f"check guards these: "
                     + "; ".join(uncovered))

    # ---- PDF-level ------------------------------------------------------------------------
    # CONTRACT CHANGED 2026-08-12 on Joseph's decision: "exit 0 must mean both the source and PDF
    # stages ran and passed. Missing PDFs or a supported text extractor must be nonzero in
    # build_all.sh." Previously
    # every skip below was a `note` and the run still returned 0, so on a machine without
    # a text extractor the check was silently HALF a check -- and worst of all it was machine-dependent,
    # passing here and skipping there with no difference in output status. A skip is now a FAILURE
    # unless --source-only is passed explicitly.
    _skip = notes.append if not strict else failures.append

    def _skipped(msg: str) -> None:
        _skip(msg + ("" if not strict else "  [PDF stage did not run; exit 0 would misreport it. "
                                           "Build the PDFs, install pdftotext or Ghostscript, or pass "
                                           "--source-only to accept a source-only check]"))

    if not struck_values:
        _skipped("no struck literals derived -- PDF stage cannot run")
    else:
        note_txt = pdf_text(note_dir / "main_note.pdf", tmp)
        if note_txt is None:
            _skipped("main_note.pdf absent, no PDF text extractor available, or the PDF extracted EMPTY -- "
                      "PDF stage did not run")
        else:
            seen_in_note = sorted(v for v in struck_values if token_hit(v, note_txt))
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
                        _skipped(f"{driver}.pdf absent, unreadable, or extracted EMPTY -- {label} build "
                                 f"NOT PDF-checked, and this is an outward-facing build the "
                                 f"whole check exists to protect")
                        continue
                    hits = sorted(v for v in seen_in_note if token_hit(v, txt))
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
