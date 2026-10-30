"""Build r22's gap-prompt inputs (G1 for the paper, G1N for the note) and their planted controls.

usage: python3 -I make_gap_inputs.py R22_DIR

Reads R22_DIR/anchors/, R22_DIR/base/ and R22_DIR/prompts/. Writes R22_DIR/gap/inputs/:
  paper/        reference-1..3.txt (anchors A, B, C, blinded) and manuscript.txt (the paper at d84124c5, blinded)
  paper-ctl/    the same, with the three PLANTS in manuscript.txt
  note-refs/    reference-1..4.txt (anchor pieces AT1, AT2, AP1, AP2)
  B01..B15/     chapter.txt (the note's base pieces)
  B09-ctl/      chapter.txt of the control piece, with the three PLANTS. B09 is the piece of median word count.
Each plant is its own sentence on its own line, placed after the first line ending in a period at or after 25%, 50%
and 75% of the text. Asserts:
  - G1's and G1N's scale lines are byte-identical to P1's and P1N's, and G1N's genre sentences are P1N's;
  - each plant occurs exactly once in its control copy and never in any real input;
  - the control copy minus its three plant lines equals the real input."""
import json
import re
import shutil
import sys
from pathlib import Path

R = Path(sys.argv[1])
P = R / "prompts"
G = R / "gap" / "inputs"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plants import PLANTS  # noqa: E402


def scale(t):
    return [l for l in t.splitlines() if re.match(r"^[1-5] = ", l)] + [l for l in t.splitlines() if l.startswith("Scale")]


p1, p1n = (P / "P1.prompt.txt").read_text(), (P / "P1N.prompt.txt").read_text()
g1, g1n = (P / "G1.prompt.txt").read_text(), (P / "G1N.prompt.txt").read_text()
assert len(scale(p1)) == 6 and scale(g1) == scale(p1) and scale(g1n) == scale(p1n) == scale(p1), "scale differs"
for s in ["Judge ONLY language and register: how closely the prose reads like a well-edited long technical write-up in "
          "particle physics, such as a long PRD or JINST paper, a technical design report, or a detailed supplement.",
          'Throughout the scale and the instructions below, "PRD paper" and "PRD register" mean such a well-edited long '
          'technical write-up and its register; length, depth of detail and specialist density appropriate to that '
          'genre are not departures.',
          "Do not judge the science, the results, the completeness of the study, or the typesetting."]:
    assert s.replace("Judge ONLY", "Rate ONLY its") in p1n or s in p1n, s[:60]
    assert s in g1n, s[:60]


def plant(text):
    lines = text.split("\n")
    total, pos, out, k = len(text), 0, [], 0
    targets = [0.25, 0.50, 0.75]
    for l in lines:
        out.append(l)
        pos += len(l) + 1
        if k < 3 and pos >= targets[k] * total and l.rstrip().endswith("."):
            out.append(PLANTS[k])
            k += 1
    assert k == 3, "fewer than three plant sites"
    t = "\n".join(out)
    for pl in PLANTS:
        assert t.count(pl) == 1
    assert "\n".join(l for l in t.split("\n") if l not in PLANTS) == text
    return t


def put(d, name, text):
    (G / d).mkdir(parents=True, exist_ok=True)
    (G / d / name).write_text(text, encoding="utf-8")


if G.exists():
    shutil.rmtree(G)
paper = (R / "base" / "paper-d84124c5.blind.txt").read_text()
for k, a in enumerate("ABC", 1):
    t = (R / "anchors" / "paper" / f"anchor{a}.blind.txt").read_text()
    put("paper", f"reference-{k}.txt", t)
    put("paper-ctl", f"reference-{k}.txt", t)
put("paper", "manuscript.txt", paper)
put("paper-ctl", "manuscript.txt", plant(paper))
for k, a in enumerate(["AT1", "AT2", "AP1", "AP2"], 1):
    put("note-refs", f"reference-{k}.txt", (R / "anchors" / "note" / f"{a}.txt").read_text())
meta = json.loads((R / "base" / "pieces" / "pieces.json").read_text())
words = sorted((m["words"], m["id"]) for m in meta)
ctl = words[len(words) // 2][1]
for m in meta:
    put(m["id"], "chapter.txt", (R / "base" / "pieces" / f"{m['id']}.txt").read_text())
put(f"{ctl}-ctl", "chapter.txt", plant((R / "base" / "pieces" / f"{ctl}.txt").read_text()))
real = [f for f in G.rglob("*.txt") if "-ctl" not in f.parent.name]
assert not any(pl in f.read_text() for f in real for pl in PLANTS), "a plant leaked into a real input"
print("control piece (median words):", ctl, "; inputs:", len(list(G.rglob("*.txt"))), "files")
for d in sorted(p.name for p in G.iterdir()):
    print(f"  {d:10s}", " ".join(f"{f.name}={len(f.read_text().split())}w" for f in sorted((G / d).iterdir())))
