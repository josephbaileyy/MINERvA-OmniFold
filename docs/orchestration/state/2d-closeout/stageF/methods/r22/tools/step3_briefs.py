"""Write r22 Step 3's per-piece writer lists: step3/briefs/Bxx.md, one per note piece with an in-scope gap.

usage: python3 -I step3_briefs.py R22_DIR
Each list gives the piece's source files (step2_briefs.py's FILES), its in-scope gaps from step3/gaps.tsv with the
change to make (gemini's for ALLOW, the reviewer's narrowed form for ALLOW-NARROW), the reviewer's reason and the two
classifications that had kept the gap out, and the piece's held sentences from step3/held.tsv, which stay exactly as
they are. The common instructions are step3/WRITER-BRIEF.md."""
import csv
import re
import sys
from pathlib import Path

R = Path(sys.argv[1])
src = (R / "tools" / "step2_briefs.py").read_text()
FILES = eval(re.search(r"FILES = (\{.*?\})\n", src, re.S).group(1))   # one mapping, step2_briefs.py's
gaps = list(csv.DictReader(open(R / "step3" / "gaps.tsv"), delimiter="\t"))
held = list(csv.DictReader(open(R / "step3" / "held.tsv"), delimiter="\t"))
cls = {}
for side in ("lane", "indep"):
    for r in csv.DictReader(open(R / "gap" / f"class-{side}-after522.tsv"), delimiter="\t"):
        cls.setdefault(r["id"], {})[side] = f"{r['class']} [{r['item']}]: {r['reason']}"
WAIVE = "<!-- absence-ok: quotes the raters' quoted sentences and requested changes; not a claim that a result is absent -->"
(R / "step3" / "briefs").mkdir(parents=True, exist_ok=True)
for p, files in FILES.items():
    mine = [r for r in gaps if r["piece"] == p]
    if not mine:
        continue
    keep = [r for r in held if r["piece"] == p]
    L = [f"# r22 Step 3, piece {p}: the writer's list", "",
         f"**Your files** (in `docs/analysis-note/`): {', '.join('`' + f + '`' for f in files)}. Edit only these.",
         f"**Rated text** (the blinded PDF extract of the current note): `step2/pieces/{p}.txt`.", "",
         f"## In scope: fix these ({len(mine)} gaps)", "",
         "Each quote is from the PDF extract; find its sentence in your .tex sources. Make the CHANGE TO MAKE, and no "
         "more: for an ALLOW-NARROW gap it is the independent reviewer's narrowed form, not the rater's original "
         "request, which is shown only so that you know what was refused.", ""]
    for r in mine:
        c = cls.get(r["id"], {})
        L += [f"### {r['id']} ({r['verdict']}, protection group {r['group']}"
              + ("; **ABSTRACT PAIR: propose, do not edit main_note.tex**" if r["joseph_pair"] else "") + ")",
              f"- QUOTE: \"{r['quote']}\""]
        if r["carried"]:
            L.append(f"- Carried to the current note: {r['carried']}")
        L += [f"- PROBLEM (the rater): {r['problem']}",
              f"- CHANGE TO MAKE: {r['effective_change']}",
              f"- Why the reviewer allowed it: {r['review_reason']}"]
        if r["verdict"] == "ALLOW-NARROW":
            L.append(f"- The rater's original request (NOT to be made beyond the narrowed form): {r['gemini_change']}")
        L += [f"- Classification that kept it out (lane): {c.get('lane', '')}",
              f"- Classification that kept it out (independent): {c.get('indep', '')}", WAIVE, ""]
    L += [f"## Held: leave these sentences exactly as they are ({len(keep)})", "",
          "A rater asked to change each of these, and Joseph's ruling keeps it (a KEEP verdict or an earlier "
          "protection). Do not edit, move or delete these sentences, even when a gap above seems to cover them; "
          "tools/check_held_note.py fails the round if one no longer prints exactly.", ""]
    for r in keep:
        L.append(f"- {r['id']}: \"{r['quote']}\"")
    L.append(WAIVE)
    (R / "step3" / "briefs" / f"{p}.md").write_text("\n".join(L) + "\n")
    print(p, "in", len(mine), "held", len(keep), files)
