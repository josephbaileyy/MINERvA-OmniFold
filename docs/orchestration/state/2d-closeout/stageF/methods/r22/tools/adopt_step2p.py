"""Apply r22 Step 2's paper adoption rule (STEP2-PLAN.md section 4, the paper rule, as r21; committed before any score).

usage: python3 -I adopt_step2p.py BASE_P1_DIR RUNS_DIR [BASE_P1_PATTERN]
The paper is adopted if, and only if, all three hold:
  1. NEW beats the base in at least 3 of the 4 blind P2 runs (sol2 and gemini, each in both orders); a run without a
     WINNER line (failed both attempts) counts as a loss for NEW;
  2. sol2 picks the same version in both orders;
  3. NEW's 3 sol2 P1 runs have a mean at least the base's mean and a lowest run at least the base's lowest run (base:
     BASE_P1_DIR/P1__base-paper-f47b1b4a__sol2__r{1,2,3}.txt, or BASE_P1_PATTERN with {k} for the run number: pass 2
     of STEP2-PAPER.md section 5 judges against the merged paper, whose P1 runs are step2p/runs/P1.paper.sol2.r{k}.txt).
Writes RUNS_DIR/adoption.tsv and prints it. AB: A = base, B = NEW; BA: A = NEW, B = base."""
import re
import statistics as st
import sys
from pathlib import Path


def winner(p):
    m = re.search(r"WINNER:\s*\**\s*([AB])", p.read_text()) if p.exists() else None
    return m.group(1) if m else None


def rating(p):
    m = re.search(r"^RATING:\s*\**\s*([0-9.]+)", p.read_text(), re.M) if p.exists() else None
    return float(m.group(1)) if m else None


B, D = Path(sys.argv[1]), Path(sys.argv[2])
v = {}
for m in ("sol2", "gemini"):
    for o in ("AB", "BA"):
        w = winner(D / f"P2.paper.{m}.{o}.md")
        v[f"{m}.{o}"] = None if w is None else ("NEW" if (o == "AB") == (w == "B") else "OLD")
wins = sum(x == "NEW" for x in v.values())
noflip = v["sol2.AB"] is not None and v["sol2.AB"] == v["sol2.BA"]
new = [rating(D / f"P1.paper.sol2.r{k}.md") for k in (1, 2, 3)]
pat = sys.argv[3] if len(sys.argv) > 3 else "P1__base-paper-f47b1b4a__sol2__r{k}.txt"
base = [rating(B / pat.format(k=k)) for k in (1, 2, 3)]
p1ok = None not in new and None not in base and st.mean(new) >= st.mean(base) and min(new) >= min(base)
adopt = wins >= 3 and noflip and p1ok
fmt = lambda xs: ",".join("-" if x is None else f"{x:g}" for x in xs)  # noqa: E731
head = "sol2.AB\tsol2.BA\tgemini.AB\tgemini.BA\tNEW_wins\tsol2_noflip\tP1_new\tP1_base\tP1_ok\tADOPT"
row = "\t".join([str(v[k]) for k in ("sol2.AB", "sol2.BA", "gemini.AB", "gemini.BA")]
                + [str(wins), str(noflip), fmt(new), fmt(base), str(p1ok), "YES" if adopt else "NO"])
(D / "adoption.tsv").write_text(head + "\n" + row + "\n")
print(head)
print(row)
