r"""usage: python3 -I apply_b4_q2.py ANALYSIS_NOTE_DIR -- r19, agy-b4 Q2 (after the measurement copy a1702535 was built):
the scope paragraph's "They show no evidence of gain over matched coarse projections." becomes "They show no evidence
of additional discrimination beyond matched coarse projections." agy read "gain" as broader than what the tests show,
and the note says "no evidence of discrimination beyond matched coarse projections" (main_note.tex:72). The protected
abstract's "with no evidence of gain over matched coarse projections" stays unedited and is a (d) item.
The edit must match exactly once."""
import sys
D = sys.argv[1]
p = f"{D}/paper_body.tex"; t = open(p, encoding="utf-8").read()
o = "They show no evidence of gain over matched coarse projections."
if t.count(o) != 1: sys.exit("Q2: %d matches" % t.count(o))
open(p, "w", encoding="utf-8").write(t.replace(o, "They show no evidence of additional discrimination beyond matched coarse projections.", 1))
print("agy-b4 Q2 applied")
