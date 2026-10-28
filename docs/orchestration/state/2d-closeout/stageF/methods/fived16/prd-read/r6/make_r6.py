"""Build prd-read/r6/input.txt: the three composites (A1, A2, H1) exactly as they print, and P02 as printed, the
control (ACCEPT 3 of 3 in rounds 4 and 5). Director, 2026-10-28, accepting 1bcccc38: a composite is an untested
reading (ruling 2), so each is read as it prints before (d). The items come from make_r5.py run on the worktree, so
nothing is retyped: OLD from 22314565, NEW as printed.
usage: python3 make_r6.py <worktree> <out>"""
import re, subprocess, sys, tempfile
W, out = sys.argv[1], sys.argv[2]
R5 = f"{W}/docs/orchestration/state/2d-closeout/stageF/methods/fived16/prd-read/r5/make_r5.py"
with tempfile.NamedTemporaryFile("r", suffix=".txt") as f:
    subprocess.run([sys.executable, "-I", R5, W, "22314565", f.name], check=True, capture_output=True)
    src = open(f.name).read()
items = {m.group(1): m.group(0) for m in re.finditer(r"^(A1|A2|H1|P02) \([^)]*\)\. OLD: .*\nNEW: .*$", src, re.M)}
assert sorted(items) == ["A1", "A2", "H1", "P02"], sorted(items)
txt = ("BACKGROUND. The paper reports a sixteen-cell, five-observable neutrino cross section with a covariance. Its "
       "intervals' coverage has not been validated. A new study unfolded pseudo-data at two GENIE v3 tunes that no part "
       "of the analysis used, to test the estimator's bias against the reported covariance; it is a bias test, not a "
       "coverage test. A1 and A2 are the paper's and the note's abstract sentence, and H1 a new paragraph of the "
       "paper's fake-data section (OLD: none). P02 is a sentence of the paper's introduction.\n\n"
       + "\n\n".join(items[k] for k in ("A1", "A2", "H1", "P02")) + "\n")
open(out, "w").write(txt)
print(len(txt.split()), "words")
