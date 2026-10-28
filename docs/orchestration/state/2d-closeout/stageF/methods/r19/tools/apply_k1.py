r"""usage: python3 -I apply_k1.py ANALYSIS_NOTE_DIR -- r19 variant B, K1: Sec. I's third paragraph keeps the definition of
coverage. Its sentences on test calibration leave the paper; they print in the note's N1 paragraph (sec_joint.tex,
landed at ac1508ec), so no fact is absent from both documents at any commit (director, 2026-10-28). The paragraph's
first two sentences (P02) are unchanged. The edit must match exactly once."""
import re, sys
D = sys.argv[1]
def pat(s): return re.compile(r"\s+".join(re.escape(w) for w in s.split()))
p = f"{D}/paper_body.tex"; t = open(p, encoding="utf-8").read()
E = [("K1", r"Two properties must be distinguished.  The coverage of unfolded intervals is the rate at which they contain the true cross section.  The calibration of a test is the rate at which it rejects a true hypothesis.  Calibration can be obtained without validated intervals by simulating the whole analysis chain at the hypothesis, so that the estimator's bias enters the simulated null distribution.  A calibration obtained in this way is valid to the extent that the simulated chain reproduces the analysis of the data.",
      r"The coverage of unfolded intervals is the rate at which they contain the true cross section."),
     ("K1 comment", r"% Framing: RECORD-20260927-s5p-stage2-exit.md sec. 5 (the estimator's bias under G is part of the simulated null).",
      r"% Framing: RECORD-20260927-s5p-stage2-exit.md sec. 5 (the estimator's bias under G is part of the simulated null). Register round r19 (variant B, K1): the definition of test calibration and its validity condition left with the tests; they print in the note's N1 paragraph at the head of sec_joint.tex.")]
for k, old, new in E:
    m = list(pat(old).finditer(t))
    if len(m) != 1: sys.exit(f"{k}: {len(m)} matches")
    t = t[:m[0].start()] + new + t[m[0].end():]
open(p, "w", encoding="utf-8").write(t); print("K1 applied")
