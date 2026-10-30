"""Build agy's BEFORE/AFTER pairs for r22 Step 2 (STEP2-PLAN.md §3, step 4), with a planted control per chunk.

usage: python3 -I make_agy_pairs.py <worktree> <base-rev> <outdir> [--chunk N] [--paper]
--paper (the paper round, STEP2-PAPER.md section 3): the batch is paper_body.tex (ids PB<n>), and the prompt says
"paper" where it says "analysis note"; nothing else changes.
For each batch file of step2/check_ledger.py, the base and current printed sentences are aligned (difflib, no autojunk);
every replaced block becomes one pair: BEFORE = the base sentences, AFTER = the current ones. Cut and inserted blocks
are not paired (cuts are covered by the fact ledger's probes and the two-direction review). Pairs are split into
chunks of N (default 40); each chunk gets a control copy in which three pairs' AFTER carry a planted change of meaning:
a negation removed ("not " / "no " deleted once), so a correct check must flag them DIFFERS. Pass rule, fixed before
any run: agy marks at least 2 of the 3 planted pairs DIFFERS in each control. Writes <outdir>/chunk<k>/{pairs.txt,
pairs-control.txt, KEY.txt} and prompt.txt."""
import difflib
import random
import re
import sys
from pathlib import Path

W, BASE, O = Path(sys.argv[1]).resolve(), sys.argv[2], Path(sys.argv[3])
N = int(sys.argv[sys.argv.index("--chunk") + 1]) if "--chunk" in sys.argv else 40
PAPER = "--paper" in sys.argv
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "step2"))
import check_ledger as cl  # noqa: E402
BATCH = {"paper_body.tex": "PB"} if PAPER else cl.PREFIX
DOC = "paper" if PAPER else "analysis note"

PROMPT = """Do not use any tools, commands or files: everything you need is in this message. Answer directly, in text, in full.

You are checking proposed rewordings of a physics {doc}. Each numbered pair has a BEFORE passage, whose content is accepted as correct, and an AFTER passage, a proposed rewording of it in the note's LaTeX source. For each pair, compare AFTER with BEFORE only, and say:
(a) whether AFTER states anything that BEFORE does not support, or states it more strongly or more broadly;
(b) whether AFTER drops any fact, number, qualifier or limitation that BEFORE states;
(c) whether AFTER is ambiguous in a way that could mislead a reader about what was measured or what holds.
A fact BEFORE states may be missing from AFTER only because the rewording moved it to a neighbouring passage; say so in DETAIL if you suspect that, but still answer DIFFERS.

Answer in this format, one block per pair, in order:
Qn: VERDICT: SAME or DIFFERS
DETAIL: <one or two sentences; if DIFFERS, quote the words concerned>
End with a line: END
""".replace("{doc}", DOC)

pairs = []
for f in BATCH:
    old = cl.sentences(cl.printed(cl.git_show(W, BASE, f"docs/analysis-note/{f}")))
    new = cl.sentences(cl.printed((W / "docs/analysis-note" / f).read_text()))
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes():
        if tag == "replace":
            pairs.append((f, i1, " ".join(old[i1:i2]), " ".join(new[j1:j2])))
O.mkdir(parents=True, exist_ok=True)
(O / "prompt.txt").write_text(PROMPT)
rng = random.Random(22)
chunks = [pairs[k:k + N] for k in range(0, len(pairs), N)]
for c, ch in enumerate(chunks, 1):
    d = O / f"chunk{c:02d}"
    d.mkdir(exist_ok=True)
    head = (f"(Each pair is one passage of a physics {DOC}, BEFORE and AFTER a register rewrite. Judge AFTER "
            "against BEFORE.)\n\n")
    real = [f"Q{n}. [{f} {BATCH[f]}{i}]\nBEFORE: {b}\nAFTER: {a}\n" for n, (f, i, b, a) in enumerate(ch, 1)]
    (d / "pairs.txt").write_text(head + "\n".join(real))
    cand = [n for n, (_, _, _, a) in enumerate(ch, 1) if re.search(r"\b(not|no) ", a)]
    plant = sorted(rng.sample(cand, min(3, len(cand))))
    ctl = []
    for n, (f, i, b, a) in enumerate(ch, 1):
        if n in plant:
            a = re.sub(r"\b(not|no) ", "", a, count=1)
        ctl.append(f"Q{n}. [{f} {BATCH[f]}{i}]\nBEFORE: {b}\nAFTER: {a}\n")
    (d / "pairs-control.txt").write_text(head + "\n".join(ctl))
    (d / "KEY.txt").write_text("planted (negation removed in AFTER): " + " ".join(f"Q{n}" for n in plant) + "\n")
    print(f"chunk{c:02d}: {len(ch)} pairs, planted {plant}, {sum(len(b) + len(a) for _, _, b, a in ch)} chars")
print("pairs", len(pairs), "chunks", len(chunks))
