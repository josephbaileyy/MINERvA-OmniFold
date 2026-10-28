"""Per clause, the four runs' verdicts (sol2 and gemini, each in both list orders), their agreement, and Q4's choice."""
import re, sys, collections
X = sys.argv[1]
CL = [l.rstrip("\n").split("\t") for l in open(f"{X}/inputs/clauses.tsv")]
RUNS = [f"PQ__{o}__{m}" for m in ("sol2", "gemini") for o in ("fwd", "rev")]
V = {}
for r in RUNS:
    t = open(f"{X}/runs/{r}.txt").read()
    for cid, _ in CL:
        m = re.search(rf"^\**{cid}\**:\s*\**VERDICT:\**\s*\**(AS-WRITTEN|BRIEFER|COMPANION|OMIT)\b(.*?)(?=^\**C\d\d\**:|^\**T\**:)", t, re.M | re.S)
        if not m:
            sys.exit(f"UNPARSEABLE {r} {cid}")
        bf = re.search(r"BRIEFER-FORM:\**\s*(.*)", m.group(2)); rs = re.search(r"REASON:\**\s*(.*)", m.group(2))
        V[(r, cid)] = (m.group(1), (bf.group(1).strip() if bf else ""), (rs.group(1).strip() if rs else ""))
    tq = re.search(r"^\**T\**:\s*\**CHOICE:\**\s*\**(INTEGER|ONE-DECIMAL|TWO-DECIMALS)", t, re.M)
    V[(r, "T")] = (tq.group(1) if tq else "UNPARSED", "", re.search(r"^\**T\**:.*?\n\**REASON:\**\s*(.*)", t, re.M | re.S).group(1).split("\n")[0])
out = []
for cid, text in CL + [["T", "Q4 chi-square precision"]]:
    vs = [V[(r, cid)][0] for r in RUNS]
    c = collections.Counter(vs)
    agree = "4/4 " + vs[0] if len(c) == 1 else ("models agree" if (vs[0] == vs[1] and vs[2] == vs[3] and vs[0] == vs[2]) else " / ".join(f"{k} {n}" for k, n in c.most_common()))
    out.append(f"{cid}\t{' | '.join(vs)}\t{agree}\t{text[:90]}")
print("clause\tsol2-fwd | sol2-rev | gemini-fwd | gemini-rev\tagreement\ttext")
print("\n".join(out))
if len(sys.argv) > 2:
    for cid, text in CL + [["T", ""]]:
        print(f"\n## {cid} {text}")
        for r in RUNS:
            v, bf, rs = V[(r, cid)]
            print(f"- {r}: {v}" + (f" | BRIEFER: {bf}" if bf and bf != "-" else "") + f" | {rs}")
