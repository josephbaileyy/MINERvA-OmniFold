"""Covering check for the App. G tracker rows: does each row's subject still print under each of its body pointers?

usage: python3 -I tracker_pointer_check.py <base commit> <new commit>   (run from the repository top level)

For every row of the records' tracker table (docs/analysis-note/app_provenance.tex) that points into the note body
with \\S\\ref{...}, take up to six content words of the row's last cell. For each pointer, count how many of them print
in the pointed section (from its \\label to the next \\label of a section, subsection or subsubsection, comments
removed) at the base and at the new commit. A row is flagged when the new count is lower than the base count, and a
pointer whose label no longer exists is flagged as missing. The tracker table is read at the new commit.
A heuristic, not a proof: a flagged row is checked by hand, and an unflagged one only keeps its words.
"""
import re
import subprocess
import sys

STOP = {"which", "their", "quoted", "block", "these", "there", "under", "every", "about", "count", "counts", "table",
        "value", "values"}
LABEL = re.compile(r"\\label\{([^}]+)\}")
HEADING = re.compile(r"\\(?:sub)*section\*?\{")


def show(rev: str, path: str) -> str:
    return subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, text=True, check=True).stdout


def sections(rev: str) -> dict[str, str]:
    """label -> printed text from that label to the next sectioning label, over every note .tex file."""
    names = subprocess.run(["git", "ls-tree", "--name-only", rev, "docs/analysis-note/"], capture_output=True,
                           text=True, check=True).stdout.split()
    out = {}
    for name in (n for n in names if n.endswith(".tex")):
        text = re.sub(r"(?<!\\)%[^\n]*", "", show(rev, name))
        # a label belongs to the sectioning command before it; any label (also one not directly after a heading)
        # starts a span that runs to the next heading
        heads = [m.start() for m in HEADING.finditer(text)] + [len(text)]
        for m in LABEL.finditer(text):
            end = next(h for h in heads if h > m.end())
            out.setdefault(m.group(1), re.sub(r"\s+", " ", text[m.start():end]).lower())
    return out


def main(base: str, new: str) -> int:
    old_s, new_s = sections(base), sections(new)
    prov = show(new, "docs/analysis-note/app_provenance.tex")
    rows = re.findall(r"\\texttt\{([a-z0-9-]+)\} & ((?:\\S\\ref\{[^}]+\}(?:, )?)+) &\s*(.*?)&\s*(.*?)\\\\", prov,
                      re.S)
    flagged = 0
    for tag, refs, _source, what in rows:
        words = [w for w in re.findall(r"[A-Za-z][A-Za-z0-9]{4,}", re.sub(r"\\[a-zA-Z]+", "", what))
                 if w.lower() not in STOP][:6]
        for label in re.findall(r"\\ref\{([^}]+)\}", refs):
            hb = sum(w.lower() in old_s.get(label, "") for w in words)
            hn = sum(w.lower() in new_s.get(label, "") for w in words)
            note = " MISSING LABEL" if label not in new_s else (" <-- fewer subject words" if hn < hb else "")
            flagged += bool(note)
            print(f"{tag:24s} {label:28s} base {hb}/{len(words)} new {hn}/{len(words)}{note}")
    print(f"TRACKER-POINTERS :: {len(rows)} rows with body pointers; {flagged} pointer(s) flagged")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
