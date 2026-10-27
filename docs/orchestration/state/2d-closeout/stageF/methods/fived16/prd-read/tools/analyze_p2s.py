"""Tabulate the Q3 pairwise runs: for each pair, model, order and replicate, which variant won and how strongly.
Fails loudly on a missing or unparseable run."""
import re, sys, collections
X = sys.argv[1]
PAIRS = [("i", "ii"), ("i", "iii"), ("ii", "iii")]
rows, tally = [], collections.defaultdict(lambda: collections.Counter())
for m in ("sol2", "gemini"):
    for a, b in PAIRS:
        for o in ("AB", "BA"):
            for r in (1, 2):
                f = f"{X}/runs/P2S__{a}v{b}-{o}__{m}__r{r}.md"
                t = open(f).read()
                w = re.findall(r"^\**\s*WINNER:\**\s*\**\s*([AB])\b", t, re.M)
                s = re.findall(r"^\**\s*STRENGTH:\**\s*\**\s*([123])\b", t, re.M)
                if len(w) != 1 or len(s) != 1:
                    sys.exit(f"UNPARSEABLE {f}")
                docA = a if o == "AB" else b
                docB = b if o == "AB" else a
                win = docA if w[0] == "A" else docB
                reasons = re.findall(r"^\s*([123])\.\s*(.+)$", t.split("REASONS", 1)[-1], re.M)
                rows.append((m, f"{a}v{b}", o, r, win, int(s[0]), w[0], [x[1] for x in reasons]))
                tally[(m, f"{a}v{b}")][win] += 1
for m, p, o, r, win, s, slot, rs in rows:
    print(f"{m:7s} {p:6s} {o} r{r}  winner=({win}) slot={slot} strength={s} | {rs[0][:150] if rs else ''}")
print()
for (m, p), c in sorted(tally.items()):
    print(f"{m:7s} {p:6s} " + ", ".join(f"({k}) {v}/4" for k, v in sorted(c.items())))
wins = collections.Counter()
for m, p, o, r, win, s, slot, rs in rows:
    wins[(m, win)] += 1
print()
for m in ("sol2", "gemini"):
    print(m, "total wins:", {k: wins[(m, k)] for k in ("i", "ii", "iii")}, "of 8 appearances each")
slots = collections.Counter((m, slot) for m, p, o, r, win, s, slot, rs in rows)
print("slot wins:", dict(slots))
