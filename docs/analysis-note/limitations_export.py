#!/usr/bin/env python3
"""Keep the limitations register's note rows located in the posted note.

usage: limitations_export.py [--note-dir DIR] [--tsv FILE] [--write] [--check]

limitations-export.tsv holds one row per note-anchored row of the limitations register (the claude.ai artifact
"OmniFold Limitations Register", collection `limitations`), with header
    row_id  file  quote  reanchor_file  reanchor_quote  note
`quote` is a literal substring of the row's sentence at 2fe070fec. A row is LOCATED when its quote, or its re-anchor,
occurs in a file of main_note.tex's input closure. If neither occurs, the tool looks the quote up in every lane's
move manifest (history-cuts/move-manifest-*.tsv); a verbatim move whose destination file now holds the quote becomes
the re-anchor. Anything else is marked REVIEW, with the best-matching window of the closure as a candidate re-anchor
for a person to check: the tool never accepts a reworded sentence on its own.

A row may also be located in the RECORDS: its re-anchor (or its original quote) appears verbatim in a file of
main_records.tex's input closure that the posted note does not also input. No printed note pointer is required and the
file named in reanchor_file is informational only, so records blocks may move between records files
(DECISION-20261121b: Joseph dropped the note-to-records pointers; this replaces DECISION-20261120a item 5's pointer rule).

--write rewrites the TSV with the re-anchors it found; --check exits 1 if any row is REVIEW (the freeze gate);
--self-test runs planted rows through the locator (each status, and each records failure) and exits 1 on any surprise.
Written by the limitation-resolver lane, 2026-11-18, for the note's structural rewrite and freeze_checks.py.
"""
import argparse
import difflib
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HEADER = ["row_id", "file", "quote", "reanchor_file", "reanchor_quote", "note"]


def closure(note_dir: Path, driver: str = "main_note") -> dict[str, str]:
    """main_note.tex (or another driver) and every file it inputs, recursively, as {file name: text}."""
    seen, stack, out = set(), [driver], {}
    while stack:
        name = stack.pop()
        path = note_dir / f"{name}.tex"
        if name in seen or not path.exists():
            continue
        seen.add(name)
        text = path.read_text(encoding="utf-8")
        out[path.name] = text
        stack += re.findall(r"\\(?:input|include)\{([^}]+)\}", text)
    return out


def manifest_moves(note_dir: Path) -> list[tuple[str, str, str]]:
    """(id, destination, sentence) for every row of every lane's move manifest."""
    moves = []
    for path in sorted((note_dir / "history-cuts").glob("move-manifest-*.tsv")):
        for line in path.read_text(encoding="utf-8").split("\n")[1:]:
            cells = line.split("\t")
            if len(cells) > 5:
                moves.append((cells[0], cells[2], cells[5]))
    return moves


def best_window(quote: str, files: dict[str, str]) -> tuple[float, str, str]:
    """The closure window, of the quote's length in words, most similar to the quote."""
    n, best = len(quote.split()), (0.0, "", "")
    for name, text in files.items():
        for line in text.split("\n"):
            if line.lstrip().startswith("%"):
                continue
            words = line.split()
            for start in range(0, max(1, len(words) - n + 1), 2):
                cand = " ".join(words[start:start + n])
                ratio = difflib.SequenceMatcher(None, cand, quote).ratio()
                if ratio > best[0]:
                    best = (ratio, name, cand)
    return best


POINTER = re.compile(r"\[pointer: (.+?)\]")


def locate(rows: list[list[str]], files: dict[str, str], moves,
           records: dict[str, str] | None = None) -> tuple[list[list[str]], dict[str, int]]:
    text = "\n".join(files.values())
    records = records or {}
    rec_only = {k: v for k, v in records.items() if k not in files}
    counts = {"present": 0, "reanchor": 0, "moved": 0, "records": 0, "review": 0}
    out = []
    for row in rows:
        rid, fname, quote, rfile, rquote, note = (row + [""] * 6)[:6]
        note = note.split(" || ")[0]
        if quote in text:
            counts["present"] += 1
            out.append([rid, fname, quote, "", "", note])
            continue
        if rquote and rquote in text:
            counts["reanchor"] += 1
            out.append([rid, fname, quote, rfile, rquote, note])
            continue
        hits = [m for m in moves if quote in m[2]]
        m = re.match(r"([A-Za-z0-9_]+\.tex)", hits[0][1]) if hits else None
        dest = m.group(1) if m else ""
        if hits and quote in files.get(dest, ""):
            counts["moved"] += 1
            out.append([rid, fname, quote, dest, quote, f"{note} || moved verbatim ({hits[0][0]})"])
            continue
        hit = next(((k, name) for k in (rquote, quote) if k for name, body in rec_only.items() if k in body), None)
        if hit:
            counts["records"] += 1
            out.append([rid, fname, quote, hit[1], hit[0], note])
            continue
        ratio, bfile, bwin = best_window(quote, files)
        counts["review"] += 1
        extra = f"; manifest {hits[0][0]} -> {hits[0][1]}, destination text not present yet" if hits else ""
        out.append([rid, fname, quote, bfile, bwin, f"{note} || REVIEW: not found; best window {ratio:.2f}{extra}"])
    return out, counts


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--note-dir", type=Path, default=HERE)
    ap.add_argument("--tsv", type=Path, default=HERE / "limitations-export.tsv")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    lines = a.tsv.read_text(encoding="utf-8").rstrip("\n").split("\n")
    if lines[0].split("\t") != HEADER:
        sys.exit(f"LIMITATIONS-EXPORT :: FAIL ({a.tsv.name} header is not {HEADER})")
    rows, counts = locate([l.split("\t") for l in lines[1:]], closure(a.note_dir), manifest_moves(a.note_dir),
                          closure(a.note_dir, "main_records"))
    summary = ", ".join(f"{k} {v}" for k, v in counts.items())
    if a.write:
        a.tsv.write_text("\n".join(["\t".join(HEADER)] + ["\t".join(r) for r in rows]) + "\n", encoding="utf-8")
    for r in rows:
        if "REVIEW" in r[5]:
            print(f"  REVIEW {r[0]} ({r[1]}): {r[2][:90]}")
    if counts["review"]:
        print(f"LIMITATIONS-EXPORT :: {'FAIL' if a.check else 'REVIEW'} ({summary})")
        return 1 if a.check else 0
    print(f"LIMITATIONS-EXPORT :: PASS ({len(rows)} rows located: {summary})")
    return 0


def self_test() -> int:
    """Planted rows through locate(): every status, and the records rule (verbatim anywhere in the records closure)."""
    note = {"sec_a.tex": "The note keeps the headline limit.", "values.tex": "A shared value file."}
    rec = {"records_x.tex": "Its full qualifier sentence, moved verbatim.", "values.tex": "A shared value file."}
    Q = "Its full qualifier sentence, moved verbatim"
    cases = [
        ("present in the note", ["r1", "sec_a.tex", "keeps the headline limit", "", "", ""], "present"),
        ("records, verbatim, no pointer", ["r2", "sec_a.tex", "old wording", "records_x.tex", Q, ""], "records"),
        ("records, block moved to another records file", ["r3", "sec_a.tex", "old wording", "records_y.tex", Q, ""], "records"),
        ("records, original quote itself in the records", ["r4", "sec_a.tex", Q, "", "", ""], "records"),
        ("text in neither closure", ["r5", "sec_a.tex", "a sentence that is not there", "records_x.tex", "nor is this", ""], "review"),
        ("text only in a file the note also inputs", ["r6", "sec_a.tex", "A shared value file", "", "", ""], "present"),
    ]
    bad = 0
    for name, row, want in cases:
        _, counts = locate([row], note, [], rec)
        got = next(k for k, v in counts.items() if v)
        ok = got == want
        bad += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {name}: {got} (want {want})")
    print(f"LIMITATIONS-EXPORT SELF-TEST :: {'PASS' if not bad else 'FAIL'} ({len(cases) - bad} of {len(cases)} cases as expected)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
