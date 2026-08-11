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
DEAD_RE = re.compile(r"\\dead\{")
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
    text = path.read_text(encoding="utf-8", errors="replace")
    bodies = []
    for m in DEAD_RE.finditer(text):
        body = match_braced(text, m.end() - 1)
        if body is not None:
            bodies.append(body)
    return bodies


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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=str(Path(__file__).resolve().parent))
    ap.add_argument("--tmp", default="/tmp")
    args = ap.parse_args()
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

    # ---- PDF-level: secondary, and only meaningful if the PDFs are built ------------------
    if not struck_values:
        notes.append("no struck literals derived -- PDF stage skipped")
    else:
        note_txt = pdf_text(note_dir / "main_note.pdf", tmp)
        if note_txt is None:
            notes.append("main_note.pdf absent or pdftotext unavailable -- PDF stage skipped "
                         "(source stage above is the authoritative check)")
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
                        notes.append(f"{driver}.pdf absent -- not PDF-checked")
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
