"""Build r22's G1b inputs (the paper diagnosis with one gap per passage) and its planted control.

usage: python3 -I make_g1b_inputs.py R22_DIR

Reads R22_DIR/anchors/paper/, R22_DIR/base/paper-d84124c5.blind.txt and R22_DIR/prompts/. Writes R22_DIR/g1b/inputs/:
  paper/      reference-1..3.txt (anchors A, B, C, blinded) and manuscript.txt (the paper at d84124c5, blinded)
  paper-ctl/  the same, with the three PLANTS (tools/plants.py, unchanged) in manuscript.txt
The plants use G1's placement rule (each on its own line, after the first line ending in a period at or after a
fraction of the text) at new fractions, 12.5 %, 37.5 % and 62.5 %: G1's 25/50/75 % moved back by one eighth.
Asserts:
  - G1b's scale lines are byte-identical to P1's and G1's, and G1b differs from G1 only in the question and format;
  - each plant occurs exactly once in the control copy and never in the real input;
  - the control copy minus its three plant lines equals the real input;
  - no G1b plant site is within 100 lines of a G1 site.
Writes only under g1b/inputs/, which it replaces; never import it."""
import re
import shutil
import sys
from pathlib import Path

R = Path(sys.argv[1])
P = R / "prompts"
G = R / "g1b" / "inputs"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from plants import PLANTS  # noqa: E402

G1_FRACTIONS, G1B_FRACTIONS = [0.25, 0.50, 0.75], [0.125, 0.375, 0.625]


def scale(t):
    return [l for l in t.splitlines() if re.match(r"^[1-5] = ", l)] + [l for l in t.splitlines() if l.startswith("Scale")]


p1, g1, g1b = [(P / n).read_text() for n in ("P1.prompt.txt", "G1.prompt.txt", "G1b.prompt.txt")]
assert len(scale(p1)) == 6 and scale(g1b) == scale(p1) == scale(g1), "scale differs"
head = lambda t: t.split("The question:")[0]
assert head(g1b) == head(g1), "G1b differs from G1 before the question"


def sites(text, fractions):
    total, pos, k, out = len(text), 0, 0, []
    for n, l in enumerate(text.split("\n")):
        pos += len(l) + 1
        if k < 3 and pos >= fractions[k] * total and l.rstrip().endswith("."):
            out.append(n)
            k += 1
    assert k == 3, "fewer than three plant sites"
    return out


def plant(text, fractions):
    at = sites(text, fractions)
    lines, out = text.split("\n"), []
    for n, l in enumerate(lines):
        out.append(l)
        if n in at:
            out.append(PLANTS[at.index(n)])
    t = "\n".join(out)
    for pl in PLANTS:
        assert t.count(pl) == 1
    assert "\n".join(l for l in t.split("\n") if l not in PLANTS) == text
    return t


paper = (R / "base" / "paper-d84124c5.blind.txt").read_text()
old, new = sites(paper, G1_FRACTIONS), sites(paper, G1B_FRACTIONS)
assert min(abs(a - b) for a in old for b in new) >= 100, (old, new)
if G.exists():
    shutil.rmtree(G)
for d in ("paper", "paper-ctl"):
    (G / d).mkdir(parents=True)
    for k, a in enumerate("ABC", 1):
        (G / d / f"reference-{k}.txt").write_text((R / "anchors" / "paper" / f"anchor{a}.blind.txt").read_text())
(G / "paper" / "manuscript.txt").write_text(paper)
(G / "paper-ctl" / "manuscript.txt").write_text(plant(paper, G1B_FRACTIONS))
assert not any(pl in paper for pl in PLANTS), "a plant is in the real input"
print("G1 sites (after line):", [n + 1 for n in old], " G1b sites:", [n + 1 for n in new])
for d in ("paper", "paper-ctl"):
    print(f"  {d:10s}", " ".join(f"{f.name}={len(f.read_text().split())}w" for f in sorted((G / d).iterdir())))
