#!/usr/bin/env python3
"""Fail if the posted note still names an estimator by its legacy letter (a)-(f).

The director's ruling of 2026-11-19 (from Joseph): descriptive names (estimator_names.tex) replace the configuration
letters in the posted text; the letters survive only in the "Legacy alias" column of tab:estimators-matrix, for
traceability to the records. This check reads the printed text (comments removed) of main_note.tex's input closure and
lists every estimator-letter reference outside that column. Patterns (the forms the note used):
  - "configuration (e)", "configuration~(e)", "configuration-(a)", "configurations (c)--(e)", "configurations (d) and (e)";
  - "as (c)" and "the learner of (a)" (the old table's cross-references);
  - an estimator-table cell or row label that starts with a bare letter: "& (f), ..." or "{(e) joint-test estimator}".
Exempt: the legacy-alias cells of tab:estimators-matrix (the last cell of each of its rows).
usage: check_estimator_letters.py [--note-dir DIR] [--self-test]; exit 1 if any reference remains.
"""
import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMMENT = re.compile(r"(?<!\\)%.*")
PATTERNS = [
    ("configuration letter", re.compile(r"[Cc]onfigurations?[~\s-]*\([a-f]\)")),
    ("cross-reference", re.compile(r"\b(?:as|learner of)\s+\([a-f]\)")),
    ("table cell", re.compile(r"(?:&|\{)\s*\([a-f]\)[,\s]")),
]


def closure(note_dir: Path) -> list[Path]:
    seen, out, stack = set(), [], ["main_note"]
    while stack:
        name = stack.pop()
        p = note_dir / (name if name.endswith(".tex") else name + ".tex")
        if p in seen or not p.exists():
            continue
        seen.add(p)
        out.append(p)
        text = "\n".join(COMMENT.sub("", l) for l in p.read_text(encoding="utf-8", errors="replace").split("\n"))
        stack += re.findall(r"\\(?:input|include)\{([^}]+)\}", text)
    return out


def legacy_cell(line: str) -> bool:
    """A row of tab:estimators-matrix whose only letter is in its last cell (the legacy alias)."""
    cells = line.rstrip().rstrip("\\").split("&")
    return len(cells) >= 7 and all(not re.search(r"\([a-f]\)", c) for c in cells[:-1])


def scan(files: list[Path]) -> list[str]:
    hits = []
    for p in files:
        in_matrix = False
        for n, raw in enumerate(p.read_text(encoding="utf-8", errors="replace").split("\n"), start=1):
            line = COMMENT.sub("", raw)
            if "\\label{tab:estimators-matrix}" in line:
                in_matrix = True
            if in_matrix and "\\end{table}" in line:
                in_matrix = False
            if in_matrix and legacy_cell(line):
                continue
            for name, rx in PATTERNS:
                for m in rx.finditer(line):
                    hits.append(f"{p.name}:{n}: {name}: ...{line[max(0, m.start() - 40):m.end() + 30].strip()}...")
    return hits


def self_test() -> int:
    good = scan_text("The \\estMultiD{} gives the result.\n")
    bad = scan_text("uses configuration~(e) here; configurations (c)--(e); as (c); & (f), LightGBM \\\\\n")
    alias = scan_text("\\label{tab:estimators-matrix}\n a & b & c & d & e & f & (e) joint-test estimator \\\\\n\\end{table}\n")
    ok = not good and len(bad) == 4 and not alias
    print(f"ESTIMATOR-LETTERS SELF-TEST :: {'PASS' if ok else 'FAIL'} (clean {len(good)}, planted {len(bad)} of 4, legacy cell {len(alias)})")
    return 0 if ok else 1


def scan_text(text: str) -> list[str]:
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "main_note.tex"
        p.write_text(text)
        return scan([p])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--note-dir", type=Path, default=HERE)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    hits = scan(closure(a.note_dir))
    for h in hits:
        print("  " + h)
    print(f"ESTIMATOR-LETTERS :: {'FAIL' if hits else 'PASS'} ({len(hits)} legacy-letter reference(s) outside the alias column)")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
