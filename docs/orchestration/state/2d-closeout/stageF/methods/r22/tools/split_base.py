"""Cut the whole note into r22's P1N base pieces, from the note's pdftotext dump, blinded as in the earlier rounds.

usage: python3 -I split_base.py NOTE_TXT OUTDIR

The pieces follow the 2026-10-22 whole-note grouping (note-rating/P1N-rerating-compare.txt, 14 pieces), with the
sixteen-cell section (Sec. 10, new since then) as its own piece and App. I with Apps. G-H:
  B01 Abstract, Executive summary, Sec. 1   B06 Sec. 7    B11 Secs. 12-13
  B02 Secs. 2-3                             B07 Sec. 8    B12 Guide to the appendices, App. A
  B03 Sec. 4                                B08 Sec. 9    B13 Apps. B-C
  B04 Sec. 5                                B09 Sec. 10   B14 Apps. D-F
  B05 Sec. 6                                B10 Sec. 11   B15 Apps. G-I
Dropped: the title block, the table of contents, the Acknowledgments and the References. The cleaning is
note-n4/tools/split_front.py's clean(), copied (that file runs on import): the repository URL, the deposit placeholder
clause (here also when pdftotext wraps it across a line), author e-mail lines, and a bare page number before a form feed. In addition, bare page numbers and the next
section's number or letter line at a piece's end are dropped. Each heading must be found, in order; the script
fails if a piece still holds an author name, an affiliation, an e-mail address, the repository owner or a hold."""
import json
import re
import sys
from pathlib import Path

src, out = Path(sys.argv[1]), Path(sys.argv[2])
L = src.read_text(encoding="utf-8").split("\n")


def find(rx, lo=0):
    hits = [i for i in range(lo, len(L)) if re.match(rx, L[i].lstrip("\f").strip())]
    if not hits:
        sys.exit(f"FAIL: heading {rx!r} not found after line {lo + 1}")
    return hits[0]


h = {}
h["abs"] = find(r"^Abstract$")
h["toc"] = find(r"^Contents$", h["abs"])
order = [("s1", r"^Introduction and motivation$"), ("s2", r"^The MINERvA experiment, data and simulation samples$"),
         ("s3", r"^The unbinned OmniFold procedure$"), ("s4", r"^Uncertainty quantification: constructing"),
         ("s5", r"^Validation of the two-dimensional measurement$"), ("s6", r"^Results$"),
         ("s7", r"^Higher-dimensional extensions: available energy and momentum"), ("s8", r"^Fifth axis: W and the"),
         ("s9", r"^Five-dimensional estimator: validation and uncertainty$"),
         ("s10", r"^The sixteen-cell five-observable measurement$"),
         ("s11", r"^Calibrated joint tests of generator predictions$"), ("s12", r"^Extended fiducial phase-space study$"),
         ("s13", r"^Summary and outlook$"), ("ack", r"^Acknowledgments$"), ("guide", r"^Guide to the appendices$"),
         ("A", r"^Statistical methods and the 2D comparison$"),
         ("B", r"^Statistical methods for the multidimensional results and inference$"),
         ("C", r"^Unbinned background subtraction by negative-weight injection$"),
         ("D", r"^Detector-response-mismatch closure"), ("E", r"^The MINERvA measurement-dimensionality survey$"),
         ("F", r"^Future work: point-cloud representations$"), ("G", r"^Result package and reproduction limits$"),
         ("H", r"^Codebase layout and terminology$"), ("refs", r"^References$")]
lo = h["toc"]
for k, rx in order:
    h[k] = find(rx, lo + 1)
    lo = h[k]
PIECES = [("B01", "Abstract, Executive summary, Sec. 1", [(h["abs"], h["toc"]), (h["s1"], h["s2"])]),
          ("B02", "Secs. 2-3", [(h["s2"], h["s4"])]), ("B03", "Sec. 4", [(h["s4"], h["s5"])]),
          ("B04", "Sec. 5", [(h["s5"], h["s6"])]), ("B05", "Sec. 6", [(h["s6"], h["s7"])]),
          ("B06", "Sec. 7", [(h["s7"], h["s8"])]), ("B07", "Sec. 8", [(h["s8"], h["s9"])]),
          ("B08", "Sec. 9", [(h["s9"], h["s10"])]), ("B09", "Sec. 10", [(h["s10"], h["s11"])]),
          ("B10", "Sec. 11", [(h["s11"], h["s12"])]), ("B11", "Secs. 12-13", [(h["s12"], h["ack"])]),
          ("B12", "Guide to the appendices, App. A", [(h["guide"], h["B"])]), ("B13", "Apps. B-C", [(h["B"], h["D"])]),
          ("B14", "Apps. D-F", [(h["D"], h["G"])]), ("B15", "Apps. G-I", [(h["G"], h["refs"])])]


def clean(lines):
    s = "\n".join(lines)
    s = re.sub(r"\n[ \t]*\d{1,3}[ \t]*\n(?=\s*\f)", "\n", s)
    s = re.sub(r"https?://\S*josephbaileyy\S*|github\.com/josephbaileyy\S*", "[repository]", s)
    s = s.replace(", identified at deposit: [snapshot identifier pending deposit]", "")
    # the clause, also when wrapped, and after the URL substitution above has taken its comma
    s = re.sub(r",?\s*identified at deposit: \[snapshot\s+identifier pending deposit\]", "", s)
    return "\n".join(l for l in s.split("\n") if not re.search(r"@stanford\.edu", l))


def trim_tail(lines):
    """Drop trailing blank lines, bare page numbers and the next heading's section number or appendix letter."""
    lines = list(lines)
    while lines and re.fullmatch(r"\f?\s*(\d{1,3}|[A-I])?\s*", lines[-1]):
        lines.pop()
    return lines


IDENT = re.compile(r"Bailey|Nachman|Stanford|SLAC|josephbaileyy|@\S+\.(edu|gov|org)|\[HOLD|pending deposit|"
                   r"funding statement pending")
out.mkdir(parents=True, exist_ok=True)
meta, bad = [], []
for pid, title, ranges in PIECES:
    txt = clean([l for s, e in ranges for l in trim_tail(L[s:e])])
    for m in IDENT.finditer(txt):
        bad.append(f"{pid}: {txt[max(0, m.start() - 40):m.end() + 40]!r}")
    (out / f"{pid}.txt").write_text(txt)
    meta.append({"id": pid, "title": title, "lines": [[s + 1, e + 1] for s, e in ranges],
                 "words": sum(1 for w in txt.split() if re.search(r"[A-Za-z0-9]", w))})
json.dump(meta, open(out / "pieces.json", "w"), indent=1)
for m in meta:
    print(m["id"], m["words"], m["title"], m["lines"])
print("total words", sum(m["words"] for m in meta))
if bad:
    print("FAIL: identifying text left in a piece:", *bad, sep="\n  ")
    sys.exit(1)
