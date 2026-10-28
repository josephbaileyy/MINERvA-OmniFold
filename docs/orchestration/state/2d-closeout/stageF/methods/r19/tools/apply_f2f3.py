r"""usage: python3 -I apply_f2f3.py ANALYSIS_NOTE_DIR -- r19, the second review's F2 and F3 (director, 2026-10-28).
- F2: sec_5d.tex's "Calibration asks whether the resulting intervals contain their specified target" becomes
  "Coverage asks". N1 now defines a test's calibration beside interval coverage, so the interval sense of the word
  would contradict it. The six other interval-sense sites go to the n4 round as an open item (r19/outline.md).
- F3: Fig. 36 (fig:coverage-5d-paper, N3) gets its own final appendix section, with one sentence pointing back to
  sec:coverage-5d. The section is the last, so no existing appendix, section, figure or table number changes.
Every edit must match exactly once."""
import sys
D = sys.argv[1]
p = f"{D}/sec_5d.tex"; t = open(p, encoding="utf-8").read()
o = "Calibration asks whether the resulting intervals contain their specified target at the stated rate"
if t.count(o) != 1: sys.exit("F2: %d matches" % t.count(o))
open(p, "w", encoding="utf-8").write(t.replace(o, "Coverage asks whether the resulting intervals contain their specified target at the stated rate", 1))
p = f"{D}/app_codebase.tex"; t = open(p, encoding="utf-8").read()
o = "% Register round r19 (variant B, N3;"
if t.count(o) != 1: sys.exit("F3: %d matches" % t.count(o))
sec = ("\\section{Supplementary figure: coverage of a purity-subtracted variant}\n\\label{app:coverage-fig}\n\n"
       "Figure~\\ref{fig:coverage-5d-paper} shows, integral by integral, the coverage test of \\S\\ref{sec:coverage-5d} "
       "under the reduction of the signal rate.\n\n")
open(p, "w", encoding="utf-8").write(t.replace(o, sec + o, 1))
print("F2 and F3 applied")
