#!/usr/bin/env python3
"""Inventory the analysis note's record appendices at a BASE tree and probe that a NEW tree lost none of them.

DECISION-20261021-joseph-da-and-note-records.md item 2: the analysis note posted as supplementary material is not a
records ledger. Its record appendices (provenance, superseded values and withdrawn results, and the record parts of
the release and codebase appendices) leave the posted build for the separately built, never-posted records document
main_records.tex. This script proves that the move lost nothing and left nothing behind.

usage:
  check_note_records.py inventory <base-note-dir> <out.json> [--sha SHA]   # freeze the base inventory
  check_note_records.py probe <base-note-dir | inventory.json> <new-note-dir> [--ledger LEDGER.md]
  check_note_records.py --self-test <base-note-dir | inventory.json> <new-note-dir> [--ledger LEDGER.md]
  check_note_records.py pin [note-dir]          # the NoteRecords2026 pin (build_all.sh runs this)
  check_note_records.py --self-test-pin         # the pin check fires and skips where it should (build_all.sh)
  check_note_records.py redit-digest <file.tex>  # each printed paragraph's sha256, for an R-EDIT row
  check_note_records.py entry-numbers [--check | --check-aux] [note-dir]   # N2-1: write / check the generated
                                                 # records_entry_numbers.tex; --check-aux compares main_records.aux
  check_note_records.py --self-test-entry-numbers  # stale file and aux mismatch fail; generator = label hook

The base is docs/analysis-note at the commit before the move (or the inventory frozen from it); the new tree is the
same directory after it. The new tree carries main_records.tex, whose \\input closure is the records document, and
main_note.tex, whose closure is the posted note. Everything is derived from the sources; the only hand-entered facts
are the line ranges of the record parts of the release and codebase appendices (RECORD_RANGES), and the inventory
fails if a range no longer starts with its heading. The ledger defaults to <new-note-dir>/records-move-ledger.md.

Inventory (base):                                    Probes (new):
  I1 every \\label in the four appendix files          P1 each label defined exactly once over note+records,
                                                         and no record label left in the posted note
  I2 every App. G tag (table rows and see-below)       P2 every tag still in the records' app_provenance.tex
  I3 every \\dead{} body in app_history.tex (multiset)  P3 the same multiset in the records closure; zero \\dead
                                                         in the posted note's closure
  I4 every \\repopath in App. G                         P4 every one still in the records closure
  I5 every printed paragraph of G, J and the record    P5 each RECORD paragraph verbatim (normalized) in the
     ranges of H and I (comment-stripped, collapsed)     records closure, or edited under an R-EDIT row (below),
                                                         and NOT in the posted note; each READER
                                                         paragraph in the note, unless the ledger lists its hash
  I6 every printed pointer into App. G (note closure)  P6 every App. G tag pointer survives: in the posted note
                                                         as a \\cite{NoteRecords2026} naming the same tag, or, if
                                                         its paragraph moved, as the same \\ref in the records,
                                                         or is a DROP the ledger lists (D: probe, below); a file
                                                         with a whole-appendix pointer still cites the records or
                                                         the ledger lists its (whole) drop
                                                     P7 every ledger row carries a probe, and every probe holds:
                                                         N:<file>::<text> prints in the posted note's <file>,
                                                         X:<file>::<text> no longer prints there,
                                                         R:<file>::<text> prints in the records closure's <file>,
                                                         D:<file>::<key> names a dropped citation whose target
                                                         still exists in the records (see THE THINNING)
                                                     P8 (THE THINNING) every NoteRecords2026 citation of the
                                                         posted note at THIN_BASE is still printed, or is a DROP
                                                         the ledger lists, and the ledger lists no drop of a
                                                         citation that is still printed
                                                     P9 every App. G table row parses into cells; every tag
                                                         the posted note cites has a full-width entry
                                                         (\\item[\\texttt{<tag>}.], which the records number);
                                                         and an entry whose tag's row has a record other than
                                                         "see below" contains that row's record cell(s),
                                                         normalized, so a repeated record cannot drift

THE THINNING (DECISION-20261022-joseph-note-records-refs-and-stop.md item 1). The posted note keeps a records
citation only where a reader needs the record to check a number or claim printed there; every other citation is
dropped, and each drop is listed in the ledger as a probe D:<file>::<key>, where <key> is the citation's target:
\\texttt{<tag>} (an App. G tag), the heading words the citation printed ("superseded values: retired material",
"identities already fixed"; parts separated by ": "), or (whole) for a citation of the whole records document. P7
requires the target to exist, in the new tree's records sources and, in the canonical checkout, at HEAD: a tag must be
a tag of app_provenance.tex (where every tag is defined; app_history.tex defines none), and each part of a heading
key must be words of a section, subsection or paragraph heading of the records files (app_provenance, app_history,
app_release_records, app_codebase_records, main_records). So no dropped citation leaves a record unreachable. P8
compares the citations, keyed the same way, with those printed at THIN_BASE (origin/main before the thinning), read
from git; outside the canonical checkout P8 cannot run, P6 and P7 still hold, and the verdict word is SKIP (exit 0, as
for RECORDS-PIN), never PASS. Every kept citation has a ledger row whose N: probe pins it to its sentence, so a
citation moved to another sentence of its file fails P7.

R-EDIT (director ruling 2026-10-26). A RECORD paragraph may change only in its pointer tokens, and only under a
ledger row
  | R-EDIT-<n> | <old sha256> | <new sha256> | <reason> | <authority> |
where each sha256 is the digest of the paragraph as P5 reads it (printed text, comments removed, whitespace collapsed:
`redit-digest <file>` prints them). P5 then accepts the base paragraph whose digest is <old> if:
  - <old> is the digest of a base RECORD paragraph of the inventory;
  - that paragraph no longer prints verbatim in the records (otherwise the row is stale);
  - a records paragraph has the digest <new> (otherwise the edit is lost, or its text is not the row's);
  - with every pointer token masked, the old and new paragraphs are identical. The pointer tokens are \\S, \\S\\S
    (never the start of \\SI or \\SIrange), \\ref{..}, \\ref*{..}, \\nsec{..}, \\napp{..}, and a section number
    written after a section sign. A bare number is not a pointer token: a value is never an R-EDIT;
  - the two paragraphs have the same number of pointer tokens in each class (section signs; \\ref, \\ref*,
    \\nsec, \\napp; section numbers): an edit retargets a pointer and never deletes or adds one.
Reason and authority are required. Each failure names its row.

R-FIX (Joseph, DECISION-20261027-joseph-absence-audit-items-3-4.md item 2). A RECORD paragraph that is false as read is
corrected in place to the current fact; its history goes to the internal ledger, never into the note. Such an edit,
beyond pointer tokens, is accepted only under a ledger row
  | R-FIX-<n> | <old sha256> | <new sha256> | <reason> | <authority> |
with the digests as for R-EDIT. P5 then accepts the base paragraph whose digest is <old> if:
  - <old> is the digest of a base RECORD paragraph of the inventory;
  - that paragraph no longer prints verbatim in the records (otherwise the row is stale);
  - a records paragraph has the digest <new> (otherwise the edit is lost, or its text is not the row's);
  - <authority> names an existing decision record, a file DECISION-<...>.md under docs/ of this repository.
An R-FIX has no pointer-only constraint; an R-EDIT keeps its. Each failure names its row.

THE PIN (plan commit 3, 2026-10-21). The posted note cites the records as NoteRecords2026 (technote.bib), whose URL
names one full commit sha. `pin` requires, in the canonical repository:
  Q1 the entry names a full 40-hex commit sha (never a branch such as tree/main);
  Q2 that commit exists in this clone and is an ancestor of HEAD, so it cannot be rebased away from under the note;
  Q3 the records' app_provenance.tex and app_history.tex exist at that commit, and every App. G tag the posted note
     cites with NoteRecords2026 is a tag of app_provenance.tex there;
  Q4 every heading the posted note names after the citation (", superseded values: retired material", ", identities
     already fixed", ...) is, part by part, words of a section, subsection or paragraph heading of the records files
     at that commit (app_provenance, app_history, app_release_records, app_codebase_records, main_records).
The canonical repository is a git checkout whose top level holds this directory as docs/analysis-note. Anywhere else
-- the standalone note repository (this directory is its top level), an export with no git, a scratch copy -- the
check reports SKIP and exits 0, as check_sec4_receipts.py does; the canonical build enforces it. --self-test-pin
builds a synthetic repository and requires Q1-Q4 each to fire, a good pin to pass, and both skip layouts to skip.

--self-test first requires the probe to be SILENT on the given (base, new) pair -- the delivered move -- and then
plants one defect at a time in a copy of the new tree (a dropped strike, a dropped and an edited record paragraph, a
record paragraph left in the note, an edited reader paragraph, a renamed tag, a lost path, a G and a J label left in
the note, a struck value in the note, a lost tag pointer, a false ledger probe) and requires the named probe to fire
on each. Since the thinning it also plants an unlisted tag, heading and whole-document drop (P6, P8 must fire), the
same tag and heading drops listed in the ledger (the probe must stay SILENT), a listed drop of a tag or of a heading
the records do not have and a listed drop whose tag left the records (P7 must fire), and a listed drop of a citation
that is still printed (P8 must fire), and a kept citation moved to another sentence of its file (P7 must fire).
For R-EDIT it plants, on one record paragraph: an unrecorded pointer edit (P5 must fire), a recorded pointer edit
(SILENT, the control), a row with a wrong old digest, a row whose new digest is not the edited text's, a recorded
word change and a recorded number change (each must fire as more than pointer tokens), a recorded pointer deletion
and a recorded pointer insertion (each must fire as deleting or adding pointer tokens), a deleted paragraph with a
row (must fire as lost), and a row whose paragraph is unchanged (must fire as stale). It also requires a row
whose new digest is wrong only in its last hex digit to fail with both digests printed in full and different
(R-EDIT messages print full digests). For R-FIX it plants, on the same paragraph, a word change: recorded (SILENT, the
control), and with a row that has no authority, a row whose authority names a decision record that does not exist, a
wrong old digest, new text that is not the row's, a deleted paragraph and an unchanged paragraph (each must fire). For P9 it drifts a repeated record from its table row (P9 must fire). Exit 0 only if every plant
behaves as named and the real pair is silent. The thinning plants
need THIN_BASE from git, so the self-test runs in the canonical checkout.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
import tempfile
from collections import Counter
from pathlib import Path

COMMENT = re.compile(r"(?<!\\)%[^\n]*")
APPS = ("app_provenance", "app_release", "app_codebase", "app_history")
# Line ranges (1-based, inclusive) of the RECORD parts of Apps. H and I at the base (4ba0dd2f): the identity table
# and the construction and audit record of the release appendix, and the test-suite discipline of the codebase
# appendix. The inventory refuses a base on which a range no longer starts with its heading.
RECORD_RANGES = {"app_release": [(122, 173, r"\subsection{Identities already fixed}"),
                                 (244, 287, r"\subsection{Construction and audit record")],
                 "app_codebase": [(55, 72, r"\paragraph{Test-suite discipline")]}
# A record range that moved keeps its pointers in this file of the records document.
MOVED_TO = {"app_release_records.tex": "app_release.tex", "app_codebase_records.tex": "app_codebase.tex"}
CITE = "NoteRecords2026"
LEDGER = "records-move-ledger.md"
# origin/main immediately before the records-citation thinning (DECISION-20261022-joseph-note-records-refs-and-stop.md).
THIN_BASE = "563715b839217e0e4e55993f42e1b223fa2432fb"


def printed(text: str) -> str:
    return COMMENT.sub("", text)


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def closure(driver: Path) -> list[Path]:
    out, seen = [], set()

    def walk(p: Path) -> None:
        if p in seen or not p.exists():
            return
        seen.add(p)
        out.append(p)
        for name in re.findall(r"\\(?:input|include)\{([^}]+)\}", printed(p.read_text(errors="replace"))):
            walk(p.parent / (name if name.endswith(".tex") else name + ".tex"))
    walk(driver)
    return out


def paragraphs(text: str) -> list[str]:
    """Printed paragraphs: blank-line separated, comments removed, whitespace collapsed, >= 8 words."""
    paras = [norm(p) for p in re.split(r"\n\s*\n", printed(text))]
    return [p for p in paras if len(p.split()) >= 8]


def dead_bodies(text: str) -> list[str]:
    t, out = printed(text), []
    for m in re.finditer(r"\\dead\s*\{", t):
        i, depth = m.end() - 1, 0
        for j in range(i, len(t)):
            depth += {"{": 1, "}": -1}.get(t[j], 0)
            if depth == 0:
                out.append(norm(t[i + 1:j]))
                break
    return out


def g_tags(prov: str) -> list[str]:
    p = printed(prov)
    return sorted(set(re.findall(r"^\\texttt\{([a-z0-9-]+)\} &", p, re.M))
                  | set(re.findall(r"\\item\[\\texttt\{([a-z0-9-]+)\}", p)))


def pointers(files: list[Path], tags: set[str], target: str) -> Counter:
    """(file, tag) counts of printed pointers of form `target` over `files`; a pointer naming no tag is (whole)."""
    c: Counter = Counter()
    for f in files:
        t = printed(f.read_text(errors="replace"))
        for m in re.finditer(target, t):
            win = t[m.end():m.end() + 260]
            stop = min([x for x in (win.find(")"), win.find(". ")) if x >= 0] or [len(win)])
            # a citation names its tag as \texttt{<tag>} or, since N2-1, as \recentry{<tag>} (printed as its number)
            named = [x for x in re.findall(r"\\(?:texttt|recentry)\{([a-z0-9-]+)\}", win[:stop]) if x in tags] or ["(whole)"]
            for x in named:
                c[(MOVED_TO.get(f.name, f.name), x)] += 1
    return c


def inventory(base: Path) -> dict:
    src = {a: (base / f"{a}.tex").read_text(errors="replace") for a in APPS}
    lines = {a: src[a].splitlines() for a in APPS}
    rec, rdr = [], []
    for a in APPS:
        if a in ("app_provenance", "app_history"):
            rec += paragraphs(src[a])
            continue
        taken: set[int] = set()
        for lo, hi, head in RECORD_RANGES.get(a, []):
            if not lines[a][lo - 1].startswith(head):
                raise SystemExit(f"FAIL {a}.tex:{lo} does not start with {head!r}; the record range moved")
            taken |= set(range(lo, hi + 1))
            rec += paragraphs("\n".join(lines[a][lo - 1:hi]))
        rdr += paragraphs("\n".join(l for n, l in enumerate(lines[a], 1) if n not in taken))
    tags = g_tags(src["app_provenance"])
    ptr = pointers(closure(base / "main_note.tex"), set(tags), r"\\ref\{app:provenance\}")
    rec_labels = re.findall(r"\\label\{([^}]+)\}", printed(src["app_provenance"] + src["app_history"]))
    for a, ranges in RECORD_RANGES.items():
        for lo, hi, _ in ranges:
            rec_labels += re.findall(r"\\label\{([^}]+)\}", printed("\n".join(lines[a][lo - 1:hi])))
    return {
        "labels": sorted(l for a in APPS for l in re.findall(r"\\label\{([^}]+)\}", printed(src[a]))),
        "record_labels": sorted(rec_labels),
        "tags": tags,
        "dead": sorted(dead_bodies(src["app_history"])),
        "repopaths": sorted(set(re.findall(r"\\repopath\{([^}]+)\}", printed(src["app_provenance"])))),
        "record_paragraphs": rec,
        "reader_paragraphs": rdr,
        "g_pointers": {f"{f}|{t}": n for (f, t), n in sorted(ptr.items())},
    }


def load_base(base: Path) -> dict:
    if base.is_file():
        inv = json.loads(base.read_text())
        return {k: v for k, v in inv.items() if not k.startswith("_")}
    return inventory(base)


def ledger_rows(ledger: Path) -> list[tuple[str, list[str]]]:
    """(row id, probes) for every table row whose first cell starts with `L`."""
    rows = []
    if not ledger.exists():
        return rows
    for line in ledger.read_text().splitlines():
        if not line.startswith("| L"):
            continue
        cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip()[1:-1])]
        probes = [p.strip().strip("`") for p in cells[-2].split(" && ")] if len(cells) >= 2 else []
        rows.append((cells[0], [p for p in probes if p]))
    return rows


# R-EDIT: the pointer tokens a RECORD paragraph may change (docstring, "R-EDIT"). A section number counts only after
# a section sign, so a value can never pass as a pointer.
POINTER_TOKEN = re.compile(r"\\S\\S(?![A-Za-z])|\\S(?![A-Za-z])|\\(?:ref\*?|nsec|napp)\{[^}]*\}"
                           r"|\u00a7\u00a7?\s*[A-Z]?\d+(?:\.\d+)*")  # \S, never the start of \SI or \SIrange
REDIT_ROW = re.compile(r"\|\s*(R-EDIT-\d+)\s*\|")


def digest(paragraph: str) -> str:
    return hashlib.sha256(paragraph.encode()).hexdigest()


def unpointed(paragraph: str) -> str:
    return norm(POINTER_TOKEN.sub(" ", paragraph))


def redit_rows(ledger: Path) -> list[tuple[str, list[str]]]:
    """(row id, cells) for every ledger table row whose first cell is R-EDIT-<n>."""
    if not ledger.exists():
        return []
    return [(m.group(1), [c.strip() for c in line.strip()[1:-1].split("|")])
            for line in ledger.read_text().splitlines() if (m := REDIT_ROW.match(line))]


def pointer_counts(paragraph: str) -> Counter:
    """Pointer tokens per class. Masking alone would let an edit delete or add a pointer: a loss of record content."""
    return Counter("section sign" if t.startswith("\\S") else "reference" if t.startswith("\\") else "section number"
                   for t in POINTER_TOKEN.findall(paragraph))


def _first_difference(old: str, new: str) -> str:
    a, b = unpointed(old).split(), unpointed(new).split()
    i = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
    return f"{' '.join(a[i:i + 6])!r} -> {' '.join(b[i:i + 6])!r}"


def redit_accepted(inv: dict, rtext: dict[str, str], rall: str, ledger: Path, fails: list[str]) -> set[str]:
    """The base RECORD paragraphs an R-EDIT row accounts for; each row that does not hold appends its failure."""
    base = {digest(p): p for p in inv["record_paragraphs"]}
    now = {digest(p): p for t in rtext.values() for p in paragraphs(t)}
    accepted = set()
    for rid, cells in redit_rows(ledger):
        if (len(cells) != 5 or not all(re.fullmatch(r"[0-9a-f]{64}", c) for c in cells[1:3])
                or not cells[3] or not cells[4]):
            fails.append(f"P5 R-EDIT row {rid}: malformed (want | id | old sha256 | new sha256 | reason | authority |)")
            continue
        old_d, new_d = cells[1], cells[2]
        old = base.get(old_d)
        if old is None:
            fails.append(f"P5 R-EDIT row {rid}: old digest {old_d} is the digest of no base RECORD paragraph")
            continue
        if old in rall:
            fails.append(f"P5 R-EDIT row {rid}: stale: base paragraph {old_d} still prints verbatim in the "
                         f"records: {old[:60]!r}")
            continue
        new_p = now.get(new_d)
        if new_p is None:
            near = [p for p in now.values() if unpointed(p) == unpointed(old)]
            if near:
                fails.append(f"P5 R-EDIT row {rid}: the edited paragraph is not the row's new text: its digest is "
                             f"{digest(near[0])}, the row's {new_d}: {near[0][:60]!r}")
            else:
                fails.append(f"P5 R-EDIT row {rid}: base paragraph {old_d} is lost: no records paragraph has "
                             f"the row's new digest {new_d} or the base paragraph's words: {old[:60]!r}")
            continue
        if unpointed(new_p) != unpointed(old):
            fails.append(f"P5 R-EDIT row {rid}: the edit changes more than pointer tokens: "
                         f"{_first_difference(old, new_p)}")
            continue
        if pointer_counts(new_p) != pointer_counts(old):
            a, b = pointer_counts(old), pointer_counts(new_p)
            fails.append(f"P5 R-EDIT row {rid}: the edit deletes or adds pointer tokens: " + ", ".join(
                f"{k} {a[k]} -> {b[k]}" for k in sorted(set(a) | set(b)) if a[k] != b[k]))
            continue
        accepted.add(old)
    return accepted


RFIX_ROW = re.compile(r"\|\s*(R-FIX-\d+)\s*\|")
DECISION_NAME = re.compile(r"DECISION-[A-Za-z0-9._-]+?\.md")
REPO_ROOT = Path(__file__).resolve().parents[2]


def rfix_rows(ledger: Path) -> list[tuple[str, list[str]]]:
    """(row id, cells) for every ledger table row whose first cell is R-FIX-<n>."""
    if not ledger.exists():
        return []
    return [(m.group(1), [c.strip() for c in line.strip()[1:-1].split("|")])
            for line in ledger.read_text().splitlines() if (m := RFIX_ROW.match(line))]


def decision_exists(name: str) -> bool:
    return any(REPO_ROOT.glob(f"docs/**/{name}"))


def rfix_accepted(inv: dict, rtext: dict[str, str], rall: str, ledger: Path, fails: list[str]) -> set[str]:
    """The base RECORD paragraphs an R-FIX row accounts for (docstring, "R-FIX"); each row that does not hold appends
    its failure."""
    base = {digest(p): p for p in inv["record_paragraphs"]}
    now = {digest(p): p for t in rtext.values() for p in paragraphs(t)}
    accepted = set()
    for rid, cells in rfix_rows(ledger):
        if len(cells) != 5 or not all(re.fullmatch(r"[0-9a-f]{64}", c) for c in cells[1:3]) or not cells[3]:
            fails.append(f"P5 R-FIX row {rid}: malformed (want | id | old sha256 | new sha256 | reason | authority |)")
            continue
        if not cells[4]:
            fails.append(f"P5 R-FIX row {rid}: no authority: an R-FIX must name the decision record that rules it")
            continue
        names = DECISION_NAME.findall(cells[4])
        if not names or not all(decision_exists(n) for n in names):
            fails.append(f"P5 R-FIX row {rid}: its authority names no existing decision record: {cells[4]!r}")
            continue
        old_d, new_d = cells[1], cells[2]
        old = base.get(old_d)
        if old is None:
            fails.append(f"P5 R-FIX row {rid}: old digest {old_d} is the digest of no base RECORD paragraph")
            continue
        if old in rall:
            fails.append(f"P5 R-FIX row {rid}: stale: base paragraph {old_d} still prints verbatim in the "
                         f"records: {old[:60]!r}")
            continue
        if now.get(new_d) is None:
            words = set(unpointed(old).split())
            near = [p for d, p in now.items() if d not in base
                    and len(words & set(unpointed(p).split())) >= 0.5 * max(len(words), 1)]
            if near:
                fails.append(f"P5 R-FIX row {rid}: the edited paragraph is not the row's new text: its digest is "
                             f"{digest(near[0])}, the row's {new_d}: {near[0][:60]!r}")
            else:
                fails.append(f"P5 R-FIX row {rid}: base paragraph {old_d} is lost: no records paragraph has "
                             f"the row's new digest {new_d}, or resembles the base paragraph: {old[:60]!r}")
            continue
        accepted.add(old)
    return accepted


def _split_top(text: str, sep: str) -> list[str]:
    """Split at `sep` outside braces, never at an escaped one (\\& or a \\\\ inside \\shortstack{...} stays)."""
    out, depth, cur, k = [], 0, [], 0
    while k < len(text):
        ch = text[k]
        if ch == "\\" and text.startswith(sep, k) and depth == 0 and sep == "\\\\":
            out.append("".join(cur)); cur = []; k += 2; continue
        if ch == "\\":  # an escaped character or a control sequence: copy it whole
            cur.append(text[k:k + 2]); k += 2; continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        elif ch == sep and depth == 0:
            out.append("".join(cur)); cur = []; k += 1; continue
        cur.append(ch); k += 1
    out.append("".join(cur))
    return out


TABLE_ROW = re.compile(r"^\s*\\texttt\{([a-z0-9-]+)\}\s*&", re.M)
ENTRY_LABEL = re.compile(r"\\item\[\\texttt\{([a-z0-9-]+)\}\.?\]")


def table_records(prov: str) -> dict[str, list[str]]:
    """tag -> the record cell(s) of its App. G table row (every cell after "Cited at"), normalized, printed text."""
    out = {}
    for table in re.findall(r"\\begin\{longtable\}(.*?)\\end\{longtable\}", printed(prov), re.S):
        for row in _split_top(table.split("\\endlastfoot", 1)[-1], "\\\\"):
            cells = [norm(c) for c in _split_top(row, "&")]
            m = re.fullmatch(r"\\texttt\{([a-z0-9-]+)\}", cells[0]) if cells else None
            if m and len(cells) >= 3:
                out[m.group(1)] = [c for c in cells[2:] if c]
    return out


def full_width_entries(prov: str) -> dict[str, str]:
    """tag -> the normalized printed text of its full-width entry (\\item[\\texttt{<tag>}.] to the next item)."""
    parts = ENTRY_LABEL.split(norm(printed(prov)))
    return {parts[i]: re.split(r"\\end\{description\}", parts[i + 1])[0] for i in range(1, len(parts) - 1, 2)}


def repeat_fails(prov: str, cited: set[str]) -> tuple[list[str], int]:
    """P9. (i) Every table row line parses; (ii) every tag the posted note cites has a full-width entry; (iii) an entry
    whose row's record is not "see below" contains that record. Returns the failures and how many records (iii)
    checked."""
    rows, entries = table_records(prov), full_width_entries(prov)
    fails = [f"P9 the App. G table row of {t} did not parse into cells" for t in TABLE_ROW.findall(printed(prov))
             if t not in rows]
    fails += [f"P9 tag {t} is cited by the posted note or recorded as an added entry, but has no full-width App. G "
              "entry" for t in sorted(cited - set(entries))]
    checked = 0
    for tag in sorted(set(rows) & set(entries)):
        if any(c.lower() == "see below" for c in rows[tag]):
            continue
        checked += 1
        for c in rows[tag]:
            if c not in entries[tag]:
                fails.append(f"P9 App. G entry {tag} does not contain its table row's record cell: {c[:80]!r}")
    return fails, checked


def probe_fails(inv: dict, new: Path, ledger: Path, thin: Counter | None = None,
                head: dict[str, str] | None = None, info: dict | None = None) -> list[str]:
    """Every failure of P0-P8. `thin` is the citation inventory at THIN_BASE (None: P8 is skipped); `head` the records
    files at HEAD (None: D targets are checked in the new tree only). `info`, if given, receives what ran."""
    fails: list[str] = []
    info = {} if info is None else info
    note = closure(new / "main_note.tex")
    recs = closure(new / "main_records.tex")
    if len(recs) <= 1:
        return ["P0 main_records.tex absent or inputs nothing; there is no records closure to probe"]
    ntext = {p.name: printed(p.read_text(errors="replace")) for p in note}
    rtext = {p.name: printed(p.read_text(errors="replace")) for p in recs}
    nall, rall = norm(" ".join(ntext.values())), norm(" ".join(rtext.values()))
    # P1 labels
    defs = Counter(l for d in (ntext, rtext) for t in d.values() for l in re.findall(r"\\label\{([^}]+)\}", t))
    for l in inv["labels"]:
        if defs[l] != 1:
            fails.append(f"P1 label {l} defined {defs[l]} times over note+records (want exactly 1)")
    for l in inv["record_labels"]:
        for n, t in ntext.items():
            if f"\\label{{{l}}}" in t:
                fails.append(f"P1 record label {l} is still defined in the posted note ({n})")
    # P2/P4 tags and paths
    prov = rtext.get("app_provenance.tex", "")
    fails += [f"P2 tag {t} missing from the records' app_provenance.tex" for t in inv["tags"]
              if not re.search(r"\\texttt\{" + re.escape(t) + r"\}", prov)]
    fails += [f"P4 repository path {p} missing from the records closure" for p in inv["repopaths"]
              if f"\\repopath{{{p}}}" not in rall]
    # P3 struck values
    got = Counter(b for t in rtext.values() for b in dead_bodies(t))
    want = Counter(inv["dead"])
    if got - want or want - got:
        fails.append(f"P3 \\dead multiset changed: lost {dict(want - got)}, added {dict(got - want)}")
    leaked = {n: dead_bodies(t) for n, t in ntext.items() if dead_bodies(t)}
    if leaked:
        fails.append(f"P3 the posted note's closure still strikes values: {leaked}")
    # P5 paragraphs
    edited = redit_accepted(inv, rtext, rall, ledger, fails) | rfix_accepted(inv, rtext, rall, ledger, fails)
    for p in inv["record_paragraphs"]:
        if p not in rall and p not in edited:
            fails.append(f"P5 RECORD paragraph not verbatim in the records closure: {p[:90]!r}")
        if p in nall:
            fails.append(f"P5 RECORD paragraph still printed in the posted note: {p[:90]!r}")
    rewritten = ledger.read_text() if ledger.exists() else ""
    for p in inv["reader_paragraphs"]:
        h = hashlib.sha256(p.encode()).hexdigest()[:12]
        if p not in nall and h not in rewritten:
            fails.append(f"P5 READER paragraph {h} neither in the note nor in the ledger as REWRITE: {p[:90]!r}")
    # The ledger's listed drops (D: probes), keyed as citation_keys keys them; validated under P7.
    rows = ledger_rows(ledger)
    drops: Counter = Counter()
    for rid, probes in rows:
        for pr in probes:
            m = re.match(r"D:([\w.]+)::(.+)$", pr, re.S)
            if m:
                drops[(m.group(1), drop_key(m.group(2)))] += 1
    info["drops"] = sum(drops.values())
    # P6 pointers
    tags = set(inv["tags"])
    after = pointers(note, tags, r"\\cite\{" + CITE + r"\}") + pointers(recs, tags, r"\\ref\{app:provenance\}")
    whole_files = set()
    for key, n in inv["g_pointers"].items():
        f, t = key.split("|")
        if t == "(whole)":
            whole_files.add(f)
        elif after[(f, t)] + drops[(f, "tag:" + t)] < n:
            fails.append(f"P6 {f}: {n} pointer(s) to tag {t} before, {after[(f, t)]} after ({CITE} citation in "
                         f"the note, or the same reference in the records) and {drops[(f, 'tag:' + t)]} listed as "
                         "dropped in the ledger")
    for f in sorted(whole_files):
        if (f in ntext and f"\\cite{{{CITE}}}" not in ntext[f] and not any(k[0] == f for k in after)
                and not drops[(f, "(whole)")]):
            fails.append(f"P6 {f}: carried a whole-appendix pointer to App. G and cites {CITE} nowhere after, and the "
                         "ledger lists no (whole) drop for it")
    # P7 ledger probes
    rec_heads = headings([rtext.get(n, "") for n in RECORD_FILES])
    rec_tags = set(g_tags(rtext.get("app_provenance.tex", "")))
    head_heads = headings(list(head.values())) if head is not None else None
    head_tags = set(g_tags(head.get("app_provenance.tex", ""))) if head is not None else None
    info["head"] = head is not None
    for rid, probes in rows:
        if not probes:
            fails.append(f"P7 ledger row {rid} carries no probe")
        for pr in probes:
            m = re.match(r"([NXRD]):([\w.]+)::(.+)$", pr, re.S)
            if not m:
                fails.append(f"P7 ledger row {rid}: malformed probe {pr[:80]!r}")
                continue
            kind, fname, text = m.groups()
            if kind == "D":
                fails += [f"P7 ledger row {rid}: {x}" for x in
                          drop_target_fails(fname, text, ntext, rec_tags, rec_heads, head_tags, head_heads)]
                continue
            pool = rtext if kind == "R" else ntext
            body = norm(pool.get(fname, ""))
            if fname not in pool:
                fails.append(f"P7 ledger row {rid}: {fname} is not in the {'records' if kind == 'R' else 'note'} "
                             "closure")
            elif (kind == "X") == (norm(text) in body):
                fails.append(f"P7 ledger row {rid}: probe {kind}:{fname}::{text[:60]!r} does not hold")
    # P8 the thinning: base citations = printed + listed drops, exactly
    info["thin"] = thin is not None
    if thin is not None:
        now = citation_keys(ntext)
        info["thin_base"], info["thin_now"] = sum(thin.values()), sum(now.values())
        for k in sorted(set(thin) | set(drops)):
            f, key = k
            gone = max(thin[k] - now[k], 0)
            if gone > drops[k]:
                fails.append(f"P8 {f}: {thin[k]} citation(s) of {key} at THIN_BASE {THIN_BASE[:8]}, {now[k]} now, "
                             f"and the ledger lists {drops[k]} drop(s): an unlisted drop")
            elif drops[k] > gone:
                fails.append(f"P8 {f}: the ledger lists {drops[k]} drop(s) of {key}, but only {gone} of the "
                             f"{thin[k]} citation(s) at THIN_BASE {THIN_BASE[:8]} are gone")
    # P9 the App. G rows parse, every cited tag has a numbered entry, and a repeated record stays its row's
    cited = {k[4:] for (_, k) in citation_keys(ntext) if k.startswith("tag:")}
    # an entry the records-move ledger records as added must keep its label, cited or not (director, n2)
    added = set(re.findall(r"Section R1 entry \\texttt\{([a-z0-9-]+)\}", ledger.read_text() if ledger.exists() else ""))
    p9, info["repeats"] = repeat_fails(rtext.get("app_provenance.tex", ""), cited | added)
    info["cited_tags"], info["added_entries"] = len(cited), len(added)
    fails += p9
    return fails


def verdict(fails: list[str], info: dict) -> str:
    """FAIL on any failure; SKIP when P0-P7 are clean but P8 could not run (no THIN_BASE in git: an unlisted heading
    drop would then be guarded by nothing, so the word must not read as PASS); PASS only when every probe ran."""
    return "FAIL" if fails else ("PASS" if info.get("thin") else "SKIP")


def report(inv: dict, fails: list[str], info: dict | None = None) -> str:
    info = info or {}
    thin = (f"; thinning: {info.get('thin_base')} citation keys at {THIN_BASE[:8]}, {info.get('thin_now')} now, "
            f"{info.get('drops', 0)} listed drops, targets checked {'in the tree and at HEAD' if info.get('head') else 'in the tree only (no HEAD)'}"
            if info.get("thin") else f"; P8 SKIP (THIN_BASE {THIN_BASE[:8]} not readable from git here), "
            f"{info.get('drops', 0)} listed drops checked in the tree only")
    return (f"RECORDS-MOVE :: {verdict(fails, info)} ({len(inv['labels'])} labels, {len(inv['tags'])} "
            f"tags, {len(inv['dead'])} struck bodies, {len(inv['repopaths'])} paths, {len(inv['record_paragraphs'])} "
            f"record and {len(inv['reader_paragraphs'])} reader paragraphs, {sum(inv['g_pointers'].values())} App. G "
            f"pointers{thin}; P9: entries required for {info.get('cited_tags', 0)} cited tags and "
            f"{info.get('added_entries', 0)} added entries, {info.get('repeats', 0)} repeated records checked; "
            f"{len(fails)} failure(s))")


def probe(base: Path, new: Path, ledger: Path) -> int:
    inv = load_base(base)
    info: dict = {}
    fails = probe_fails(inv, new, ledger, thin_base_citations(new), records_at_head(new), info)
    for f in fails:
        print("  FAIL " + f)
    print(report(inv, fails, info))
    # SKIP exits 0, as RECORDS-PIN's SKIP does: outside the canonical checkout (a build copy, an export) the probe
    # cannot read THIN_BASE, and build_all.sh's scratch builds must not fail for that. The verdict word says SKIP.
    return 1 if fails else 0


# ---------------------------------------------------------------------------------------------------------------
# The pin of the NoteRecords2026 citation (plan commit 3).

import os
import subprocess

PIN_URL_RE = re.compile(r"github\.com/josephbaileyy/MINERvA-OmniFold/(?:tree|blob)/([0-9A-Za-z._/-]+?)/docs/analysis-note")
SHA_RE = re.compile(r"[0-9a-f]{40}")
RECORD_FILES = ("app_provenance.tex", "app_history.tex", "app_release_records.tex", "app_codebase_records.tex",
                "main_records.tex")
REQUIRED_AT_PIN = ("app_provenance.tex", "app_history.tex")
HEADING_RE = re.compile(r"\\(?:section|subsection|subsubsection|paragraph)\*?\{")


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    """git in `cwd` with every GIT_* variable removed, so an inherited GIT_DIR cannot point the check elsewhere."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    try:
        return subprocess.run(["git", *args], cwd=str(cwd), env=env, capture_output=True, text=True)
    except FileNotFoundError:
        return subprocess.CompletedProcess(["git", *args], 127, "", "git not found")


def bib_pin(note: Path) -> tuple[str | None, str]:
    """(ref named by NoteRecords2026's URL, the entry text) from technote.bib."""
    bib = (note / "technote.bib").read_text(errors="replace")
    m = re.search(r"@misc\{NoteRecords2026,(.*?)\n\}", bib, re.S)
    if not m:
        return None, ""
    u = PIN_URL_RE.search(m.group(1))
    return (u.group(1) if u else None), m.group(1)


def mask_math(text: str) -> str:
    """Each $...$ becomes one opaque word, so commas and backslashes inside math neither end nor alter a phrase."""
    return re.sub(r"\$([^$]*)\$", lambda m: " m" + hashlib.sha1(re.sub(r"\s+", "", m.group(1)).encode()).hexdigest()[:10] + " ",
                  text)


def plain(text: str) -> str:
    """Heading or phrase text compared as words: math masked, \\texttt{x} -> x, other commands and braces dropped."""
    t = mask_math(text)
    t = re.sub(r"\\texttt\{([^{}]*)\}", r"\1", t)
    t = re.sub(r"\\[A-Za-z]+\*?", " ", t)
    t = re.sub(r"[{}~]", " ", t)
    return re.sub(r"\s+", " ", t).strip().lower()


def headings(texts: list[str]) -> list[str]:
    out = []
    for text in texts:
        t = printed(text)
        for m in HEADING_RE.finditer(t):
            depth, j = 1, m.end()
            while j < len(t) and depth:
                depth += {"{": 1, "}": -1}.get(t[j], 0)
                j += 1
            out.append(plain(t[m.end():j - 1]))
    return out


def claims_in_text(text: str) -> list[tuple[list[str], list[str]]]:
    """(tags, heading parts) for every NoteRecords2026 citation printed in `text` (comments already stripped)."""
    out = []
    t = norm(text)
    for m in re.finditer(r"\\cite\{NoteRecords2026\}", t):
        rest = t[m.end():m.end() + 300]
        win = rest[:min([x for x in (rest.find(")"), rest.find(". ")) if x >= 0] or [len(rest)])]
        tags = re.findall(r"\\(?:texttt|recentry)\{([a-z0-9-]+)\}", win)
        parts: list[str] = []
        if rest.startswith(", "):
            phrase = mask_math(rest[2:])
            phrase = re.split(r"\)|;|,|\. |\\\\|\\texttt|\\recentry", phrase)[0]
            phrase = re.sub(r"\s+and\s*$", "", phrase).strip()
            if phrase and phrase[0].islower() and not phrase.startswith("which"):
                parts = [plain(x) for x in phrase.split(": ") if plain(x)]
        out.append((tags, parts))
    return out


def cited_claims(note: Path) -> list[tuple[str, list[str], list[str]]]:
    """(file, tags, heading parts) for every NoteRecords2026 citation printed in the posted note's closure."""
    return [(f.name, tags, parts) for f in closure(note / "main_note.tex")
            for tags, parts in claims_in_text(printed(f.read_text(errors="replace")))]


# ---------------------------------------------------------------------------------------------------------------
# The thinning (DECISION-20261022-joseph-note-records-refs-and-stop.md item 1): listed drops and the THIN_BASE count.

def citation_keys(texts: dict[str, str]) -> Counter:
    """(file, key) counts over {file name: printed text}: one key per tag (tag:<t>), one per heading named
    (head:<parts joined by ': '>), and (whole) for a citation that names neither."""
    c: Counter = Counter()
    for name, text in texts.items():
        for tags, parts in claims_in_text(text):
            keys = [f"tag:{x}" for x in tags] + ([f"head:{': '.join(parts)}"] if parts else [])
            for k in keys or ["(whole)"]:
                c[(name, k)] += 1
    return c


def drop_key(text: str) -> str:
    """The key of a D: probe's target: \\texttt{tag} -> tag:tag, (whole) -> (whole), else heading words."""
    text = norm(text)
    m = re.fullmatch(r"\\texttt\{([a-z0-9-]+)\}", text)
    if m:
        return "tag:" + m.group(1)
    if text == "(whole)":
        return "(whole)"
    return "head:" + ": ".join(plain(x) for x in mask_math(text).split(": ") if plain(x))


def drop_target_fails(fname: str, text: str, ntext: dict[str, str], rec_tags: set[str], rec_heads: list[str],
                      head_tags: set[str] | None, head_heads: list[str] | None) -> list[str]:
    """Why a listed drop D:<fname>::<text> is invalid: its file is not a posted file, or its target is missing from
    the records sources of the new tree or (when known) of HEAD."""
    out = []
    if fname not in ntext:
        out.append(f"D:{fname}: {fname} is not in the posted note's closure")
    key = drop_key(text)
    where = [("the new tree", rec_tags, rec_heads)] + ([("HEAD", head_tags, head_heads)] if head_tags is not None else [])
    for label, tags, heads in where:
        if key.startswith("tag:"):
            if key[4:] not in tags:
                out.append(f"D:{fname}::{text}: tag {key[4:]} is not a tag of app_provenance.tex in {label}, so the "
                           "dropped citation's record would be unreachable")
        elif key.startswith("head:"):
            for part in key[5:].split(": "):
                if not part or not any(part in h for h in heads):
                    out.append(f"D:{fname}::{text}: {part!r} is no heading's words in the records files in {label}")
        elif key != "(whole)":
            out.append(f"D:{fname}::{text}: unreadable target")
    return out


def _repo_note(new: Path) -> Path | None:
    """The canonical checkout's top level when `new` is its docs/analysis-note, else None."""
    top = git(new.resolve(), "rev-parse", "--show-toplevel")
    if top.returncode != 0:
        return None
    toplevel = Path(top.stdout.strip()).resolve()
    return toplevel if toplevel / "docs" / "analysis-note" == new.resolve() else None


def records_at_head(new: Path) -> dict[str, str] | None:
    """The records files at HEAD, or None outside the canonical checkout."""
    top = _repo_note(new)
    if top is None:
        return None
    out = {}
    for name in RECORD_FILES:
        shown = git(top, "show", f"HEAD:docs/analysis-note/{name}")
        if shown.returncode == 0:
            out[name] = shown.stdout
    return out


def thin_base_citations(new: Path) -> Counter | None:
    """citation_keys of the posted note's closure at THIN_BASE, read from git; None where THIN_BASE is not readable."""
    top = _repo_note(new)
    if top is None or git(top, "cat-file", "-e", THIN_BASE + "^{commit}").returncode != 0:
        return None
    texts: dict[str, str] = {}

    def walk(name: str) -> None:
        if name in texts:
            return
        shown = git(top, "show", f"{THIN_BASE}:docs/analysis-note/{name}")
        if shown.returncode != 0:
            return
        texts[name] = printed(shown.stdout)
        for inc in re.findall(r"\\(?:input|include)\{([^}]+)\}", texts[name]):
            walk(inc if inc.endswith(".tex") else inc + ".tex")
    walk("main_note.tex")
    return citation_keys(texts) if texts else None


# ---------------------------------------------------------------------------------------------------------------
# N2-1 (director rulings 2026-10-26): the posted note cites a records entry by its number, R1.<n>, through
# \recentry{<tag>}. The numbers are GENERATED from app_provenance.tex into records_entry_numbers.tex, which preamble.tex
# inputs, so the posted note never reads the records build. The counting rule is the label hook's in main_records.tex:
# every full-width item \item[\texttt{<tag>}.] of app_provenance.tex, in file order, numbered within the records
# section that app_provenance.tex opens.

ENTRY_FILE = "records_entry_numbers.tex"
ENTRY_DEF = re.compile(r"\\@namedef\{recentry@([a-z0-9-]+)\}\{([^}]*)\}")
RECLABEL = re.compile(r"\\newlabel\{rec:([a-z0-9-]+)\}\{\{([^}]*)\}")


def records_section(main_records: str) -> int:
    """The number of the records section that app_provenance.tex opens: one more than the \\section commands that
    main_records.tex prints before it inputs app_provenance (app_provenance.tex begins with its \\section)."""
    text = printed(main_records)
    i = text.find("\\input{app_provenance}")
    return 1 + len(re.findall(r"\\section\{", text[:i if i >= 0 else 0]))


def entry_numbers(prov: str, section: int) -> dict[str, str]:
    """tag -> "R<section>.<n>", in the label hook's order."""
    out: dict[str, str] = {}
    for n, tag in enumerate(ENTRY_LABEL.findall(norm(printed(prov))), 1):
        out.setdefault(tag, f"R{section}.{n}")
    return out


def render_entry_numbers(numbers: dict[str, str]) -> str:
    lines = ["% GENERATED by `python3 check_note_records.py entry-numbers` from app_provenance.tex; never edit by hand.",
             "% The number of every full-width records entry, as main_records.tex's label hook numbers it, so the",
             "% posted note can cite an entry as \\recentry{<tag>} without reading the records build.",
             "% `entry-numbers --check` fails if this file is stale; `entry-numbers --check-aux` (build_all.sh, after",
             "% the records build) fails if a number differs from main_records.aux.",
             "\\makeatletter",
             "\\providecommand{\\recentry}[1]{\\@ifundefined{recentry@#1}{\\PackageError{records_entry_numbers}{no",
             "  records entry is numbered for the tag #1}{Regenerate with check_note_records.py entry-numbers.}}%",
             "  {\\@nameuse{recentry@#1}}}"]
    lines += [f"\\@namedef{{recentry@{t}}}{{{n}}}" for t, n in numbers.items()]
    return "\n".join(lines + ["\\makeatother", ""])


def generated_entry_numbers(note: Path) -> str:
    return render_entry_numbers(entry_numbers((note / "app_provenance.tex").read_text(errors="replace"),
                                              records_section((note / "main_records.tex").read_text(errors="replace"))))


def posted_entry_numbers(note: Path) -> dict[str, str]:
    f = note / ENTRY_FILE
    return dict(ENTRY_DEF.findall(f.read_text())) if f.exists() else {}


def entry_numbers_cmd(note: Path, mode: str) -> int:
    fresh = generated_entry_numbers(note)
    target = note / ENTRY_FILE
    if mode == "write":
        target.write_text(fresh)
        print(f"ENTRY-NUMBERS :: wrote {ENTRY_FILE} ({len(ENTRY_DEF.findall(fresh))} entries)")
        return 0
    if mode == "check":
        ok = target.exists() and target.read_text() == fresh
        print(f"ENTRY-NUMBERS :: {'PASS' if ok else 'FAIL'} ({ENTRY_FILE} "
              f"{'equals a fresh generation' if ok else 'is missing or stale: run check_note_records.py entry-numbers'}"
              f"; {len(ENTRY_DEF.findall(fresh))} entries)")
        return 0 if ok else 1
    aux = note / "main_records.aux"
    if not aux.exists():
        print("ENTRY-NUMBERS-AUX :: FAIL (main_records.aux is missing: run after the records build)")
        return 1
    built, posted = dict(RECLABEL.findall(aux.read_text(errors="replace"))), posted_entry_numbers(note)
    bad = [f"{t}: posted {posted.get(t)!r}, records {built.get(t)!r}" for t in sorted(set(built) | set(posted))
           if built.get(t) != posted.get(t)]
    for b in bad:
        print("  FAIL " + b)
    print(f"ENTRY-NUMBERS-AUX :: {'PASS' if not bad else 'FAIL'} ({len(posted)} posted numbers, {len(built)} "
          f"records labels; {len(bad)} mismatch(es))")
    return 1 if bad else 0


def entry_numbers_self_test(note: Path) -> int:
    """A stale numbers file fails --check; a records label that differs fails --check-aux; and, where pdflatex is
    installed, the generator and main_records.tex's label hook agree on a fixture with a \\shortstack row and an item
    whose label has no final period (the two cases the review of the records commit found)."""
    failures, done, skipped = [], [], []
    hook = re.search(r"\\newcounter\{recentry\}.*?\\textbf\{\\therecentry\}\\enspace #1\}",
                     (note / "main_records.tex").read_text(), re.S)
    fixture_prov = ("\\section{Provenance}\n{\\small\\begin{longtable}{@{}lll@{}}\n"
                    "\\texttt{tag-a} & \\shortstack[l]{x,\\\\ y} & see below \\\\\n\\end{longtable}}\n"
                    "\\begin{description}[leftmargin=0pt]\n  \\item[\\texttt{tag-a}.] A.\n"
                    "  \\item[\\texttt{tag-b}] B, no final period.\n\\end{description}\n"
                    "\\begin{description}[leftmargin=0pt]\n  \\item[\\texttt{tag-c}.] C.\n\\end{description}\n")
    fixture_main = ("\\section{Front}\n\\input{app_provenance}\n")
    with tempfile.TemporaryDirectory() as d:
        w = Path(d)
        (w / "app_provenance.tex").write_text(fixture_prov)
        (w / "main_records.tex").write_text(fixture_main)
        gen = entry_numbers(fixture_prov, records_section(fixture_main))
        if gen != {"tag-a": "R2.1", "tag-b": "R2.2", "tag-c": "R2.3"}:
            failures.append(f"generator on the fixture gave {gen}")
        else:
            done.append("generator numbers the fixture R2.1-R2.3")
        (w / ENTRY_FILE).write_text(generated_entry_numbers(w))
        import contextlib, io
        with contextlib.redirect_stdout(io.StringIO()):
            fresh_ok = entry_numbers_cmd(w, "check") == 0
            (w / ENTRY_FILE).write_text((w / ENTRY_FILE).read_text().replace("{R2.2}", "{R2.3}"))
            stale_fails = entry_numbers_cmd(w, "check") == 1
            (w / ENTRY_FILE).write_text(generated_entry_numbers(w))
            (w / "main_records.aux").write_text("\\newlabel{rec:tag-a}{{R2.1}{1}}\n\\newlabel{rec:tag-b}{{R2.3}{1}}\n"
                                                "\\newlabel{rec:tag-c}{{R2.3}{1}}\n")
            aux_fails = entry_numbers_cmd(w, "check-aux") == 1
        for ok, what in ((fresh_ok, "a fresh file passes --check"), (stale_fails, "a stale file fails --check"),
                         (aux_fails, "a records label that differs fails --check-aux")):
            (done if ok else failures).append(what if ok else f"NOT: {what}")
        if hook is None:
            failures.append("main_records.tex has no label hook to test")
        elif shutil.which("pdflatex") is None:
            skipped.append("the LaTeX agreement test: pdflatex is not installed (it runs in build_all.sh)")
        else:
            (w / "t.tex").write_text("\\documentclass{article}\\usepackage{enumitem}\\usepackage{longtable}\n"
                                     "\\renewcommand{\\thesection}{R\\arabic{section}}\n" + hook.group(0) +
                                     "\n\\begin{document}\n\\section{Front}\n\\begingroup\n"
                                     "\\setlist[description]{format=\\recentrylabel}\n\\input{app_provenance}\n"
                                     "\\endgroup\n\\end{document}\n")
            run = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "t.tex"], cwd=w,
                                 capture_output=True, text=True)
            built = dict(RECLABEL.findall((w / "t.aux").read_text())) if (w / "t.aux").exists() else {}
            if run.returncode == 0 and built == gen:
                done.append("the label hook, built with pdflatex, numbers the fixture as the generator does")
            else:
                failures.append(f"label hook and generator disagree: hook {built}, generator {gen} (rc {run.returncode})")
    for x in done:
        print("  ok     " + x)
    for x in skipped:
        print("  SKIP   " + x)
    for f in failures:
        print("  FAIL " + f)
    print(f"ENTRY-NUMBERS SELF-TEST :: {'PASS' if not failures else 'FAIL'} ({len(done)} checks as expected"
          f"{f', {len(skipped)} skipped' if skipped else ''})")
    return 1 if failures else 0


def pin_check(note: Path) -> tuple[str, list[str]]:
    """("PASS" | "FAIL" | "SKIP", messages)."""
    note = note.resolve()
    top = git(note, "rev-parse", "--show-toplevel")
    if top.returncode != 0:
        return "SKIP", [f"{note} is not in a git checkout (an export or a scratch copy); enforced by the canonical build"]
    toplevel = Path(top.stdout.strip()).resolve()
    if toplevel / "docs" / "analysis-note" != note:
        return "SKIP", [f"{note} is not <repo>/docs/analysis-note of its checkout {toplevel} (the standalone note "
                        "repository); enforced by the canonical build"]
    fails: list[str] = []
    ref, entry = bib_pin(note)
    if not entry:
        return "FAIL", ["Q1 technote.bib has no @misc{NoteRecords2026} entry"]
    if ref is None or not SHA_RE.fullmatch(ref):
        return "FAIL", [f"Q1 NoteRecords2026 names {ref!r}, not a full 40-hex commit sha: a branch moves, so the "
                        "citation would not identify the records the note cites"]
    if git(note, "cat-file", "-e", ref + "^{commit}").returncode != 0:
        return "FAIL", [f"Q2 pinned commit {ref} is not in this clone (a shallow or partial clone cannot verify it)"]
    anc = git(note, "merge-base", "--is-ancestor", ref, "HEAD")
    if anc.returncode == 1:
        fails.append(f"Q2 pinned commit {ref} is not an ancestor of HEAD: a rebase or an unmerged branch can lose it")
    elif anc.returncode != 0:
        fails.append(f"Q2 cannot decide whether {ref} is an ancestor of HEAD: {anc.stderr.strip()}")
    at_pin = {}
    for name in RECORD_FILES:
        shown = git(note, "show", f"{ref}:docs/analysis-note/{name}")
        if shown.returncode == 0:
            at_pin[name] = shown.stdout
        elif name in REQUIRED_AT_PIN:
            fails.append(f"Q3 docs/analysis-note/{name} does not exist at {ref}")
    tags = set(g_tags(at_pin.get("app_provenance.tex", "")))
    heads = headings(list(at_pin.values()))
    # N2-1: the number a \recentry{<tag>} prints (records_entry_numbers.tex) must be the tag's number at the pin,
    # generated from the pinned app_provenance.tex and main_records.tex, not from the working tree.
    pin_numbers = entry_numbers(at_pin.get("app_provenance.tex", ""), records_section(at_pin.get("main_records.tex", "")))
    posted = posted_entry_numbers(note)
    n_numbered = 0
    for f in closure(note / "main_note.tex"):
        for tag in re.findall(r"\\recentry\{([a-z0-9-]+)\}", printed(f.read_text(errors="replace"))):
            n_numbered += 1
            if posted.get(tag) != pin_numbers.get(tag):
                fails.append(f"Q3 {f.name} cites {tag} as {posted.get(tag)!r}, but at the pin {ref[:12]} its records "
                             f"entry is numbered {pin_numbers.get(tag)!r}")
    claims = cited_claims(note)
    n_tags = n_parts = 0
    for fname, ctags, parts in claims:
        for tag in ctags:
            n_tags += 1
            if tag not in tags:
                fails.append(f"Q3 {fname} cites tag {tag} with NoteRecords2026, but app_provenance.tex at {ref[:12]} "
                             "has no such tag")
        for part in parts:
            n_parts += 1
            if not any(part in h for h in heads):
                fails.append(f"Q4 {fname} names {part!r} after NoteRecords2026, which is no heading's words in the "
                             f"records at {ref[:12]}")
    if not claims:
        fails.append("Q3 the posted note cites NoteRecords2026 nowhere: there is nothing to pin, or the citation "
                     "form changed and this check no longer sees it")
    summary = (f"{len(claims)} citations, {n_tags} tag ({n_numbered} by number) and {n_parts} heading references, "
               f"pinned to {ref}, "
               f"{len(tags)} tags, {len(pin_numbers)} numbered entries and {len(heads)} headings at the pin")
    return ("FAIL" if fails else "PASS"), fails + [summary]


def pin(note: Path) -> int:
    status, msgs = pin_check(note)
    for msg in msgs[:-1] if status != "SKIP" else []:
        print("  FAIL " + msg)
    print(f"RECORDS-PIN :: {status} -- {msgs[-1]}")
    return 1 if status == "FAIL" else 0


def pin_self_test() -> int:
    """A synthetic repository: a good pin passes; Q1-Q4 each fire; the standalone and no-git layouts skip."""
    failures, fired = [], 0
    prov = ("\\section{Provenance}\n\\label{app:provenance}\n{\\small\\begin{longtable}{@{}ll@{}}\n"
            "\\texttt{tag-a} & see below \\\\\n\\end{longtable}}\n"
            "\\begin{description}\n  \\item[\\texttt{tag-b}.] A record.\n\\end{description}\n")
    hist = ("\\section{Superseded values and withdrawn results}\n\\label{app:history}\n"
            "\\subsection{Struck values}\n\\subsubsection{The earlier direct $(\\Eavail,W)$ block sum}\nText.\n")
    good_body = ("Text (Ref.~\\cite{NoteRecords2026}, \\texttt{tag-a}) and (Ref.~\\cite{NoteRecords2026}, superseded "
                 "values: struck values) and (Ref.~\\cite{NoteRecords2026}, superseded values: the earlier direct "
                 "$(\\Eavail, W)$ block sum).\n")

    def bib(ref: str) -> str:
        return ("@misc{NoteRecords2026,\n  title = {{Records}},\n  howpublished = {\\url{https://github.com/josephbaileyy/"
                f"MINERvA-OmniFold/tree/{ref}/docs/analysis-note}}}}\n}}\n")

    with tempfile.TemporaryDirectory() as d:
        repo = Path(d) / "repo"
        note = repo / "docs" / "analysis-note"
        note.mkdir(parents=True)
        g = lambda *a: git(repo, "-c", "user.name=pin-self-test", "-c", "user.email=pin@self.test.invalid", *a)
        if g("init", "-q").returncode != 0:
            print("RECORDS-PIN SELF-TEST :: FAIL (git init failed: git is required)")
            return 1
        (note / "app_provenance.tex").write_text(prov)
        (note / "app_history.tex").write_text(hist)
        (note / "main_note.tex").write_text("\\documentclass{article}\n\\begin{document}\n\\input{sec_a}\n\\end{document}\n")
        (note / "sec_a.tex").write_text(good_body)
        (note / "technote.bib").write_text(bib("main"))

        def commit(parent: str | None) -> str:
            g("add", "-A")
            tree = g("write-tree").stdout.strip()
            args = ["commit-tree", tree, "-m", "pin self-test"] + (["-p", parent] if parent else [])
            return g(*args).stdout.strip()
        a = commit(None)
        g("update-ref", "HEAD", a)
        (note / "technote.bib").write_text(bib(a))
        b = commit(a)
        g("update-ref", "HEAD", b)
        side = commit(None)                     # same tree, no parent: never an ancestor of HEAD

        def case(name: str, want: str, bib_ref: str, body: str = good_body) -> None:
            nonlocal fired
            (note / "technote.bib").write_text(bib(bib_ref))
            (note / "sec_a.tex").write_text(body)
            status, msgs = pin_check(note)
            ok = (status == want == "PASS") or (status == want == "SKIP") or (
                status == "FAIL" and want not in ("PASS", "SKIP") and any(x.startswith(want) for x in msgs))
            if ok:
                fired += 1
                print(f"  {'fired ' if want not in ('PASS', 'SKIP') else 'ok    '} {name:42} -> {status}: {msgs[0][:90]}")
            else:
                failures.append(f"{name}: expected {want}, got {status}: {msgs[:2]}")

        case("good pin passes", "PASS", a)
        case("branch name instead of a sha (tree/main)", "Q1", "main")
        case("non-ancestor sha", "Q2 pinned commit", side)
        case("unknown sha", "Q2 pinned commit", "0" * 40)
        case("pin lacking a cited tag", "Q3 sec_a.tex cites tag tag-c", a,
             good_body + "Also (Ref.~\\cite{NoteRecords2026}, \\texttt{tag-c}).\n")
        case("heading the records do not have", "Q4 sec_a.tex names 'retired material'", a,
             good_body + "Also (Ref.~\\cite{NoteRecords2026}, superseded values: retired material).\n")
        case("no citation at all", "Q3 the posted note cites", a, "No citation.\n")
        # N2-1: tag-b is entry R1.1 at the pin a. A consistent numbers file passes; an entry inserted before it after
        # the pin, with the numbers file regenerated from the working tree, makes the posted number differ.
        (note / "records_entry_numbers.tex").write_text(render_entry_numbers({"tag-b": "R1.1"}))
        case("number cited as at the pin passes", "PASS", a,
             good_body + "And (Ref.~\\cite{NoteRecords2026}, \\recentry{tag-b}).\n")
        (note / "app_provenance.tex").write_text(prov.replace("  \\item[\\texttt{tag-b}.]",
                                                                "  \\item[\\texttt{tag-z}.] New.\n  \\item[\\texttt{tag-b}.]"))
        (note / "records_entry_numbers.tex").write_text(generated_entry_numbers(note) if (note / "main_records.tex").exists()
                                                        else render_entry_numbers(entry_numbers(
                                                            (note / "app_provenance.tex").read_text(), 1)))
        case("entry renumbered after the pin", "Q3 sec_a.tex cites tag-b as 'R1.2'", a,
             good_body + "And (Ref.~\\cite{NoteRecords2026}, \\recentry{tag-b}).\n")
        (note / "app_provenance.tex").write_text(prov)
        (note / "records_entry_numbers.tex").unlink()
        # The standalone note repository: this directory is the top level of its own checkout.
        standalone = Path(d) / "standalone"
        shutil.copytree(note, standalone)
        git(standalone, "init", "-q")
        status, msgs = pin_check(standalone)
        if status == "SKIP":
            fired += 1
            print(f"  ok     {'standalone note repository skips':42} -> SKIP: {msgs[0][:90]}")
        else:
            failures.append(f"standalone layout: expected SKIP, got {status}: {msgs[:2]}")
        plain_copy = Path(d) / "export" / "docs" / "analysis-note"
        shutil.copytree(note, plain_copy)
        status, msgs = pin_check(plain_copy)
        if status == "SKIP":
            fired += 1
            print(f"  ok     {'copy outside any git checkout skips':42} -> SKIP: {msgs[0][:90]}")
        else:
            failures.append(f"no-git layout: expected SKIP, got {status}: {msgs[:2]}")
    for f in failures:
        print("  FAIL " + f)
    print(f"RECORDS-PIN SELF-TEST :: {'PASS' if not failures else 'FAIL'} ({fired} of 11 cases as expected: a good pin "
          "passes; a branch, a non-ancestor, an unknown sha, a missing tag, a missing heading and no citation fail; "
          "a number cited as at the pin passes and an entry renumbered after the pin fails; "
          "the standalone and no-git layouts skip)")
    return 1 if failures else 0


# ---------------------------------------------------------------------------------------------------------------
# Self-test: silent on the delivered move, and each planted defect fires its own probe.

def _drop_paragraph(path: Path, head: str) -> None:
    t = path.read_text()
    i = t.index(head)
    j = t.find("\n\n", i)
    path.write_text(t[:i] + t[j if j >= 0 else len(t):])


_R_ANCHOR = r"\paragraph{From \S\ref{sec:invert}, rank deficiency"  # app_history.tex: a record paragraph
_R_POINTER = _R_ANCHOR.replace("sec:invert", "sec:chisq")


_RF_AUTH = "DECISION-20261027-joseph-absence-audit-items-3-4.md"
_RF_NEW = _R_ANCHOR.replace("rank deficiency", "rank loss")


def _rfix_row(inv: dict, new: str, anchor: str = _R_ANCHOR, old_digest: str | None = None,
              authority: str = _RF_AUTH) -> str:
    """A planted R-FIX row for the base record paragraph holding `anchor`, corrected to hold `new` instead."""
    hits = [p for p in inv["record_paragraphs"] if anchor in p]
    if len(hits) != 1:
        raise SystemExit(f"self-test plant: {anchor!r} is in {len(hits)} base RECORD paragraphs, not 1")
    old = hits[0]
    return (f"| R-FIX-90 | {old_digest or digest(old)} | {digest(old.replace(anchor, new))} | planted | "
            f"{authority} |")


def _redit_row(inv: dict, new: str, anchor: str = _R_ANCHOR, old_digest: str | None = None) -> str:
    """A planted R-EDIT row for the base record paragraph holding `anchor`, edited to hold `new` instead."""
    hits = [p for p in inv["record_paragraphs"] if anchor in p]
    if len(hits) != 1:
        raise SystemExit(f"self-test plant: {anchor!r} is in {len(hits)} base RECORD paragraphs, not 1")
    old = hits[0]
    return (f"| R-EDIT-90 | {old_digest or digest(old)} | {digest(old.replace(anchor, new))} | planted | "
            "self-test |")


PLANTS = [
    # (name, probe that must fire, file, old, new[, ledger row appended[, ledger row ids removed]])  -- old=None appends
    # `new`; a callable edits
    # the file; a probe of None means the plant must leave the probe SILENT (no failure at all)
    ("dropped strike", "P3 \\dead multiset", "app_history.tex", r"$\dead{0.406}$", "$0.406$"),
    ("dropped record paragraph", "P5 RECORD paragraph not verbatim", "app_release_records.tex",
     lambda p: _drop_paragraph(p, r"\paragraph{Conditioning.}"), None),
    ("edited record paragraph", "P5 RECORD paragraph not verbatim", "app_codebase_records.tex",
     "as five rules rather than", "as six rules rather than"),
    ("record paragraph left in the note", "P5 RECORD paragraph still printed", "app_codebase.tex",
     lambda p: p.write_text(p.read_text() + "\n" + (p.parent / "app_codebase_records.tex").read_text()), None),
    # The plant must edit a reader paragraph that still prints verbatim from the base. The release appendix's
    # archive paragraph, the first anchor, was rewritten by the register pass (batch bhi, director F6, 2026-10-21),
    # so the plant moved to the codebase appendix's PET paragraph. The note consolidation (DECISION-20261027 item 1,
    # cost-list R10; records-move-ledger.md L-con-R10) rewrote that one too, so the plant moved to the release
    # appendix's scope heading: of the 20 base reader paragraphs it is the one still verbatim. app_release.tex was then
    # a protected file; it was released to the lanes on 2026-10-28 (DECISION-20261028-joseph-protections-n4-release-
    # retrospective.md item 3). Round r22 Step 2 rewrote that heading too (records-move-ledger.md L-r22-1), so no
    # base reader paragraph still prints verbatim and a note-side edit has no target. The plant therefore makes the
    # other half of the same condition false: it drops the heading's REWRITE row hash from the ledger, so a reader
    # paragraph that is no longer printed verbatim has no REWRITE record and P5 must fire.
    ("edited reader paragraph", "P5 READER paragraph", LEDGER,
     "READER 2e4dfdaf3190", "READER (hash removed)"),
    ("renamed tag (every occurrence)", "P2 tag joint-5d", "app_provenance.tex",
     lambda p: p.write_text(p.read_text().replace(r"\texttt{joint-5d}", r"\texttt{joint-5e}")), None),
    # Every copy of one path is lost: since n2 two paths print twice in App. G (a table row and the full-width entry
    # that repeats it, P9), so losing only the first copy would leave the path in the records.
    ("lost repository path", "P4 repository path", "app_provenance.tex", lambda p: p.write_text(
        p.read_text().replace(_first_repopath(p), _first_repopath(p).replace("\\repopath{", "\\texttt{"))), None),
    ("G label left in the note", "P1 record label tab:prov-paths", "app_guide.tex", None,
     "\n\\label{tab:prov-paths}\n"),
    ("J label left in the note", "P1 record label app:history-errata", "app_guide.tex", None,
     "\n\\label{app:history-errata}\n"),
    ("struck value in the note", "P3 the posted note's closure still strikes", "sec_intro.tex", None,
     "\nWas $\\dead{9.876}$.\n"),
    # The thinning dropped sec_joint.tex's only citation (ledger L-thin-C41), so this plant moved to a kept one.
    ("lost tag pointer", "P6 app_statmethods_nd.tex", "app_statmethods_nd.tex", r"\cite{NoteRecords2026}",
     r"\cite{AnalysisNote2026}"),
    ("false ledger probe", "P7 ledger row", LEDGER, None,
     "\n| L99 | planted | - | `N:sec_intro.tex::this sentence is not printed anywhere` | planted |\n"),
    # The thinning (DECISION-20261022): a drop is accepted only when the ledger lists it and its target exists.
    ("unlisted tag drop", "P6 sec_systematics.tex: 1 pointer(s) to tag flux-index", "sec_systematics.tex",
     r" (Ref.~\cite{NoteRecords2026}, \recentry{flux-index})", ""),
    ("unlisted tag drop, P8", "P8 sec_systematics.tex: 1 citation(s) of tag:flux-index", "sec_systematics.tex",
     r" (Ref.~\cite{NoteRecords2026}, \recentry{flux-index})", ""),
    ("listed tag drop (silent)", None, "sec_systematics.tex",
     r" (Ref.~\cite{NoteRecords2026}, \recentry{flux-index})", "",
     "| L98 | planted | DROP | R1 | `D:sec_systematics.tex::\\texttt{flux-index}` | planted |", ["L-thin-C64"]),
    ("unlisted heading drop", "P8 app_statmethods.tex: 1 citation(s) of head:superseded values at",
     "app_statmethods.tex", " (Ref.~\\cite{NoteRecords2026}, superseded values).", "."),
    ("listed heading drop (silent)", None, "app_statmethods.tex",
     " (Ref.~\\cite{NoteRecords2026}, superseded values).", ".",
     "| L98 | planted | DROP | R4 | `D:app_statmethods.tex::superseded values` | planted |", ["L-thin-C22"]),
    ("unlisted whole-document drop", "P6 app_guide.tex: carried a whole-appendix pointer", "app_guide.tex",
     "document, Ref.~\\cite{NoteRecords2026};", "document;"),
    ("listed drop of a tag the records lack", "P7 ledger row L98: D:sec_validation.tex::\\texttt{coverage-fixed-truths}",
     "sec_validation.tex", r"(Ref.~\cite{NoteRecords2026}, \recentry{coverage-fixed-truth})", "",
     "| L98 | planted | DROP | R1 | `D:sec_validation.tex::\\texttt{coverage-fixed-truths}` | planted |"),
    ("listed drop whose tag left the records", "P7 ledger row L98: D:sec_systematics.tex::\\texttt{flux-index}: tag",
     "app_provenance.tex", lambda p: (p.write_text(p.read_text().replace(r"\texttt{flux-index}", r"\texttt{flux-idx}")),
                                      _unlink_cite(p.parent / "sec_systematics.tex", r"\recentry{flux-index}")), None,
     "| L98 | planted | DROP | R1 | `D:sec_systematics.tex::\\texttt{flux-index}` | planted |"),
    # n3 (2026-10-27): the sec_systematics ten-seed citation these two plants used left the note (L-thin-C62, director
    # ruling (e)); they now use citations that still print, in both the base and the delivered App. A and App. B.
    ("listed drop of a heading the records lack", "P7 ledger row L98: D:app_statmethods.tex::superseded values: "
     "retired materials", "app_statmethods.tex",
     r"was in force when the tests were graded (Ref.~\cite{NoteRecords2026}, superseded values: retired material)",
     "was in force when the tests were graded",
     "| L98 | planted | DROP | R4 | `D:app_statmethods.tex::superseded values: retired materials` | planted |"),
    ("kept citation moved within its file (C13)", "P7 ledger row L-thin-C13", "app_statmethods_nd.tex",
     lambda p: p.write_text(_move_cite(p.read_text(), " (\\recentry{rank-inversion})",
                                       "The 2D methods and their worked examples are in App.~\\ref{app:statmethods}.")), None),
    # P9 (n2): a repeated record drifts from its table row
    ("repeated record drifts from its row", "P9 App. G entry flux-index does not contain", "app_provenance.tex",
     r"\texttt{KNOWN\_ISSUES.md} row 91: the flux-universe", r"\texttt{KNOWN\_ISSUES.md} row 92: the flux-universe"),
    ("cited tag's entry deleted", "P9 tag flux-index is cited by the posted note", "app_provenance.tex",
     lambda p: p.write_text(re.sub(r"\n  \\item\[\\texttt\{flux-index\}\.\].*?(?=\n  \\item)", "", p.read_text(),
                                   count=1, flags=re.S)), None),
    ("added entry's label renamed", "P9 tag july-sweep is cited by the posted note or recorded as an added entry",
     "app_provenance.tex", "\\item[\\texttt{july-sweep}.]", "\\item[\\texttt{july-sweep-x}.]"),
    # a row whose cell holds a line break (\shortstack{...\\...}) is still parsed and compared
    ("record put into a row with a broken cell", "P9 App. G entry flux-repair does not contain", "app_provenance.tex",
     "App.~\\ref{app:release-schema}, App.~\\ref{app:history}} &\n  see below \\\\",
     "App.~\\ref{app:release-schema}, App.~\\ref{app:history}} &\n  a planted record \\\\"),
    ("table row that no longer parses", "P9 the App. G table row of flux-index did not parse", "app_provenance.tex",
     "the quoted universe block counts it once \\\\\n\\texttt{flux-index} &",
     "the quoted universe block counts it once\n\\texttt{flux-index} &"),
    ("listed drop still printed", "P8 sec_systematics.tex: the ledger lists 1 drop(s) of tag:flux-index", LEDGER, None,
     "\n| L98 | planted | DROP | R1 | `D:sec_systematics.tex::\\texttt{flux-index}` | planted |\n"),
    # R-EDIT (director ruling 2026-10-26), all on one record paragraph of app_history.tex. A callable ledger row is
    # built from the inventory, so its digests are those of the real base paragraph.
    ("unrecorded pointer edit", "P5 RECORD paragraph not verbatim", "app_history.tex", _R_ANCHOR, _R_POINTER),
    ("recorded pointer edit (control)", None, "app_history.tex", _R_ANCHOR, _R_POINTER,
     lambda inv: _redit_row(inv, _R_POINTER)),
    ("R-EDIT row with a wrong old digest", "P5 R-EDIT row R-EDIT-90: old digest", "app_history.tex", _R_ANCHOR,
     _R_POINTER, lambda inv: _redit_row(inv, _R_POINTER, old_digest="0" * 64)),
    ("R-EDIT new text not the row's", "P5 R-EDIT row R-EDIT-90: the edited paragraph is not the row's new text",
     "app_history.tex", _R_ANCHOR, _R_POINTER,
     lambda inv: _redit_row(inv, _R_ANCHOR.replace("sec:invert", "sec:pull"))),
    ("recorded word change", "P5 R-EDIT row R-EDIT-90: the edit changes more than pointer tokens", "app_history.tex",
     _R_ANCHOR, _R_ANCHOR.replace("rank deficiency", "rank loss"),
     lambda inv: _redit_row(inv, _R_ANCHOR.replace("rank deficiency", "rank loss"))),
    ("recorded number change", "P5 R-EDIT row R-EDIT-90: the edit changes more than pointer tokens",
     "app_history.tex", "($N=50$ replicas", "($N=60$ replicas",
     lambda inv: _redit_row(inv, "($N=60$ replicas", anchor="($N=50$ replicas")),
    ("recorded pointer deletion", "P5 R-EDIT row R-EDIT-90: the edit deletes or adds pointer tokens",
     "app_history.tex", _R_ANCHOR, _R_ANCHOR.replace(r"\S\ref{sec:invert}", ""),
     lambda inv: _redit_row(inv, _R_ANCHOR.replace(r"\S\ref{sec:invert}", ""))),
    ("recorded pointer insertion", "P5 R-EDIT row R-EDIT-90: the edit deletes or adds pointer tokens",
     "app_history.tex", _R_ANCHOR, _R_ANCHOR.replace(r"\S\ref{sec:invert}", r"\S\ref{sec:invert} \S\ref{sec:chisq}"),
     lambda inv: _redit_row(inv, _R_ANCHOR.replace(r"\S\ref{sec:invert}", r"\S\ref{sec:invert} \S\ref{sec:chisq}"))),
    ("deleted paragraph with a row", "P5 R-EDIT row R-EDIT-90: base paragraph", "app_history.tex",
     lambda p: _drop_paragraph(p, _R_ANCHOR), None, lambda inv: _redit_row(inv, _R_POINTER)),
    ("R-EDIT row, paragraph unchanged", "P5 R-EDIT row R-EDIT-90: stale", LEDGER, None, "",
     lambda inv: _redit_row(inv, _R_POINTER)),
    # R-FIX (Joseph, DECISION-20261027 item 2): a word change of the same record paragraph, under an R-FIX row.
    ("recorded fix (control)", None, "app_history.tex", _R_ANCHOR, _RF_NEW, lambda inv: _rfix_row(inv, _RF_NEW)),
    ("R-FIX row with no authority", "P5 R-FIX row R-FIX-90: no authority", "app_history.tex", _R_ANCHOR, _RF_NEW,
     lambda inv: _rfix_row(inv, _RF_NEW, authority="")),
    ("R-FIX naming a missing decision record", "P5 R-FIX row R-FIX-90: its authority names no existing decision",
     "app_history.tex", _R_ANCHOR, _RF_NEW,
     lambda inv: _rfix_row(inv, _RF_NEW, authority="DECISION-20991231-nobody-no-such-record.md")),
    ("R-FIX row with a wrong old digest", "P5 R-FIX row R-FIX-90: old digest", "app_history.tex", _R_ANCHOR, _RF_NEW,
     lambda inv: _rfix_row(inv, _RF_NEW, old_digest="0" * 64)),
    ("R-FIX new text not the row's", "P5 R-FIX row R-FIX-90: the edited paragraph is not the row's new text",
     "app_history.tex", _R_ANCHOR, _RF_NEW,
     lambda inv: _rfix_row(inv, _R_ANCHOR.replace("rank deficiency", "rank shortfall"))),
    ("deleted paragraph with an R-FIX row", "P5 R-FIX row R-FIX-90: base paragraph", "app_history.tex",
     lambda p: _drop_paragraph(p, _R_ANCHOR), None, lambda inv: _rfix_row(inv, _RF_NEW)),
    ("R-FIX row, paragraph unchanged", "P5 R-FIX row R-FIX-90: stale", LEDGER, None, "",
     lambda inv: _rfix_row(inv, _RF_NEW)),
]


def _first_repopath(path: Path) -> str:
    """The first \\repopath{...} of `path`, in full (a plant removes every copy of it)."""
    return re.search(r"\\repopath\{[^}]*\}", path.read_text()).group(0)


def _move_cite(text: str, cite: str, sentence: str) -> str:
    """Move the one occurrence of `cite` to the end of `sentence` (a planted change of a kept citation's position)."""
    if text.count(cite) != 1 or text.count(sentence) != 1:
        raise SystemExit(f"self-test plant: {cite!r} or {sentence!r} is not unique")
    return text.replace(cite, "").replace(sentence, sentence + cite)


def _unlink_cite(path: Path, tag: str) -> None:
    """Remove the one citation of `tag` (as printed: \\recentry{<tag>} since N2-1) from `path` (a planted drop)."""
    t = path.read_text()
    old = f" (Ref.~\\cite{{NoteRecords2026}}, {tag})"
    if t.count(old) != 1:
        raise SystemExit(f"self-test plant: {old!r} occurs {t.count(old)} times in {path.name}")
    path.write_text(t.replace(old, ""))


def _digest_message_check(inv: dict, new: Path, ledger: Path, thin: Counter | None, head: dict[str, str] | None) -> bool:
    """A recorded pointer edit whose row's new digest is the real one with its last hex digit changed must fail with a
    message that prints both digests in full, and they must differ (12-character prefixes printed them as equal)."""
    with tempfile.TemporaryDirectory() as d:
        work = Path(d) / "digest-message"
        shutil.copytree(new, work, ignore=shutil.ignore_patterns("*.pdf", "*.aux", "*.log", "*.bcf", "*.bbl", "*.fls",
                                                                 "*.fdb_latexmk", "*.out", "*.toc", "*.run.xml",
                                                                 "*.blg", "figures", "archive", "release-package-*",
                                                                 "__pycache__"))
        hist = work / "app_history.tex"
        hist.write_text(hist.read_text().replace(_R_ANCHOR, _R_POINTER, 1))
        row = _redit_row(inv, _R_POINTER)
        real = row.split("|")[3].strip()
        wrong = real[:-1] + ("0" if real[-1] != "0" else "1")
        led = Path(d) / "digest-message.ledger.md"
        led.write_text(ledger.read_text() + "\n" + row.replace(real, wrong) + "\n")
        got = [f for f in probe_fails(inv, work, led, thin, head) if "is not the row's new text" in f]
        shown = re.findall(r"[0-9a-f]{64}", got[0]) if got else []
        ok = len(shown) == 2 and shown[0] == real and shown[1] == wrong and shown[0] != shown[1]
        print(f"  {'fired ' if ok else 'FAILED'} R-EDIT digest message          -> "
              f"{'two distinct full digests: ' + real[-6:] + ' vs ' + wrong[-6:] if ok else got[:1]}")
        return ok


def self_test(base: Path, new: Path, ledger: Path) -> int:
    inv = load_base(base)
    failures, fired, silent = [], 0, 0
    thin, head = thin_base_citations(new), records_at_head(new)
    if thin is None or head is None:
        failures.append(f"THIN_BASE {THIN_BASE[:8]} or HEAD is not readable from git for {new}: the thinning plants "
                        "need the canonical checkout (run the self-test there)")
    real = probe_fails(inv, new, ledger, thin, head)
    if real:
        failures.append(f"the delivered move is not silent ({len(real)} failure(s)): {real[:3]}")
    with tempfile.TemporaryDirectory() as d:
        for name, want, fname, old, repl, *extra in PLANTS:
            work = Path(d) / re.sub(r"\W+", "-", name)
            shutil.copytree(new, work, ignore=shutil.ignore_patterns("*.pdf", "*.aux", "*.log", "*.bcf", "*.bbl",
                                                                     "*.fls", "*.fdb_latexmk", "*.out", "*.toc",
                                                                     "*.run.xml", "*.blg", "figures", "archive",
                                                                     "release-package-*", "__pycache__"))
            led = work / LEDGER if ledger == new / LEDGER else Path(d) / (work.name + ".ledger.md")
            if led != work / LEDGER:
                shutil.copyfile(ledger, led)
            target = led if fname == LEDGER else work / fname
            text = target.read_text()
            if callable(old):
                old(target)
            elif old is None:
                target.write_text(text + repl)
            elif old not in text:
                failures.append(f"{name}: UNAPPLIED, anchor {old!r} not found in {fname}")
                continue
            else:
                target.write_text(text.replace(old, repl, 1))
            if extra:
                # a real listed drop also retires the kept citation's position row (extra[1]), so the plant does too
                kept = [l for l in led.read_text().splitlines()
                        if not any(l.startswith(f"| {rid} |") for rid in (extra[1] if len(extra) > 1 else []))]
                row = extra[0](inv) if callable(extra[0]) else extra[0]
                led.write_text("\n".join(kept) + "\n" + row + "\n")
            got = probe_fails(inv, work, led, thin, head)
            if want is None:
                if got:
                    failures.append(f"{name}: expected SILENT, got {got[:3]}")
                else:
                    silent += 1
                    print(f"  silent {name:36} -> no failure")
            elif not any(f.startswith(want) for f in got):
                failures.append(f"{name}: expected a failure starting {want!r}, got {got[:3]}")
            else:
                fired += 1
                print(f"  fired  {name:36} -> {next(f for f in got if f.startswith(want))[:100]}")
    if not _digest_message_check(inv, new, ledger, thin, head):
        failures.append("R-EDIT digest message: a new digest wrong only in its last digit did not print as two distinct "
                        "full digests")
    for f in failures:
        print("  FAIL " + f)
    n_fire = sum(1 for p in PLANTS if p[1] is not None)
    print(f"RECORDS-MOVE SELF-TEST :: {'PASS' if not failures else 'FAIL'} (delivered move silent: {not real}; "
          f"{fired} of {n_fire} planted defects fired their probe; {silent} of {len(PLANTS) - n_fire} listed drops "
          "and recorded pointer edits or fixes stayed silent)")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    args = list(argv)
    ledger = None
    if "--ledger" in args:
        i = args.index("--ledger")
        ledger = Path(args[i + 1])
        del args[i:i + 2]
    if len(args) >= 3 and args[0] == "inventory":
        inv = inventory(Path(args[1]))
        if "--sha" in args:
            inv = {"_base_sha": args[args.index("--sha") + 1],
                   "_derived_by": "docs/analysis-note/check_note_records.py inventory", **inv}
        Path(args[2]).write_text(json.dumps(inv, indent=1) + "\n")
        print({k: (len(v) if not isinstance(v, str) else v) for k, v in inv.items()})
        return 0
    if args and args[0] == "pin" and len(args) <= 2:
        return pin(Path(args[1]) if len(args) == 2 else Path(__file__).resolve().parent)
    if args == ["--self-test-pin"]:
        return pin_self_test()
    if args and args[0] == "entry-numbers":
        flags = [a for a in args[1:] if a.startswith("--")]
        rest = [a for a in args[1:] if not a.startswith("--")]
        note = Path(rest[0]) if rest else Path(__file__).resolve().parent
        mode = {(): "write", ("--check",): "check", ("--check-aux",): "check-aux"}.get(tuple(flags))
        if mode is None or len(rest) > 1:
            print(__doc__)
            return 2
        return entry_numbers_cmd(note, mode)
    if args == ["--self-test-entry-numbers"]:
        return entry_numbers_self_test(Path(__file__).resolve().parent)
    if len(args) == 2 and args[0] == "redit-digest":
        for para in paragraphs(Path(args[1]).read_text(errors="replace")):
            print(digest(para), para[:80])
        return 0
    if len(args) == 3 and args[0] in ("probe", "--self-test"):
        base, new = Path(args[1]), Path(args[2])
        ledger = ledger or new / LEDGER
        return (probe if args[0] == "probe" else self_test)(base, new, ledger)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
