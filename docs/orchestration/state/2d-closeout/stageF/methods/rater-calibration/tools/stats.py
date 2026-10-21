"""Summary statistics from results.json (written by analyze.py). usage: python3 -I stats.py CALDIR > stats.md"""
import json, math, statistics as st, sys
from pathlib import Path

C = Path(sys.argv[1]); R = json.loads((C / "results.json").read_text())
cells, runs = R["cells"], R["runs"]
A = ["anchorA", "anchorB", "anchorC"]
f = lambda x, n=2: "–" if x is None else f"{x:.{n}f}"


def cell(p, m, d):
    return cells.get(f"{p}|{m}|{d}")


def pooled_sd(p, m, docs):
    vs = [(c["n"] - 1, c["sd"] ** 2) for d in docs if (c := cell(p, m, d)) and c["sd"] is not None]
    dof = sum(k for k, _ in vs)
    return math.sqrt(sum(k * v for k, v in vs) / dof) if dof else None, dof


print("## Per-cell scores\n")
print("| prompt | model | document | runs | mean | sd |\n|---|---|---|---|---|---|")
for k, c in cells.items():
    p, m, d = k.split("|")
    print(f"| {p} | {m} | {d} | {', '.join(f(s) for s in c['runs'])} | {f(c['mean'])} | {f(c['sd'])} |")

print("\n## Absolute prompts: separation, revision sensitivity, holds, framing\n")
print("Sign convention: every difference below is oriented so that POSITIVE = the direction a better-written text should go "
      "(higher rating; fewer P3 flags). z = difference / (pooled sd x sqrt(1/n1 + 1/n2)); 'resolved' means z >= 2.\n")
print("| prompt | model | pooled sd (dof) | anchors mean | ours-current | separation (anchors - ours)/sd | ours-old | current - old (z) | resolved? | holds - hold-free (z) | runs/round for a 0.5-pt change |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
out = {}
for p in ["P1", "P3", "P0", "P0n"]:
    for m in ["sol", "gemini"]:
        docs = [d for d in A + ["ours-current", "ours-old", "ours-holds"] if cell(p, m, d)]
        if not docs:
            continue
        sd, dof = pooled_sd(p, m, docs)
        sign = -1 if p == "P3" else 1
        an = [cell(p, m, d)["mean"] for d in A if cell(p, m, d)]
        amean = st.mean(an) if an else None
        cur = cell(p, m, "ours-current"); old = cell(p, m, "ours-old"); hol = cell(p, m, "ours-holds")
        def z(a, b):
            if not (a and b): return None, None
            dlt = sign * (a["mean"] - b["mean"])
            if not sd: return dlt, math.inf if dlt else 0.0
            return dlt, dlt / (sd * math.sqrt(1 / a["n"] + 1 / b["n"]))
        sep = None if amean is None or cur is None else (sign * (amean - cur["mean"]) / sd if sd else (math.inf if amean != cur["mean"] else 0))
        dco, zco = z(cur, old); dho, zho = z(hol, cur)
        nrun = None if (sd is None or p == "P3") else max(1, math.ceil(32 * sd ** 2))
        out[f"{p}|{m}"] = dict(sd=sd, dof=dof, anchors=amean, cur=cur and cur["mean"], sep=sep, d_cur_old=dco, z_cur_old=zco,
                               d_hold=dho, z_hold=zho, n_for_half=nrun)
        print(f"| {p} | {m} | {f(sd)} ({dof}) | {f(amean)} | {f(cur and cur['mean'])} | {f(sep)} | {f(old and old['mean'])} | "
              f"{f(dco)} ({f(zco, 1)}) | {'yes' if zco is not None and zco >= 2 else ('no' if zco is not None else '–')} | "
              f"{f(dho)} ({f(zho, 1)}) | {nrun if nrun else '–'} |")

print("\n## Framing effect (P0n - P0; positive = neutral framing scores higher)\n")
print("| model | document | P0 runs | P0n runs | P0n - P0 | z |\n|---|---|---|---|---|---|")
for m in ["sol", "gemini"]:
    sd, _ = pooled_sd("P0", m, ["ours-current", "anchorA"])
    sd2, _ = pooled_sd("P0n", m, ["ours-current", "anchorA"])
    s = math.sqrt(((sd or 0) ** 2 + (sd2 or 0) ** 2) / 2)
    for d in ["ours-current", "anchorA"]:
        a, b = cell("P0", m, d), cell("P0n", m, d)
        if a and b:
            dd = b["mean"] - a["mean"]
            zz = dd / (s * math.sqrt(1 / a["n"] + 1 / b["n"])) if s else (math.inf if dd else 0)
            print(f"| {m} | {d} | {', '.join(f(x,1) for x in a['runs'])} | {', '.join(f(x,1) for x in b['runs'])} | {f(dd)} | {f(zz,1)} |")

print("\n## P2 pairwise (blind, both orders)\n")
print("| model | opponent | AB: A=ours-current | BA: B=ours-current | ours wins | order-consistent? |\n|---|---|---|---|---|---|")
tot = {"sol": [0, 0, 0], "gemini": [0, 0, 0]}
for m in ["sol", "gemini"]:
    for o in A + ["ours-old"]:
        ab = runs.get(f"P2__pair-cur-{o}-AB__{m}__r1"); ba = runs.get(f"P2__pair-cur-{o}-BA__{m}__r1")
        if not (ab and ba): continue
        w1 = ab["winner"] == "A"; w2 = ba["winner"] == "B"
        tot[m][0] += w1 + w2; tot[m][1] += 2; tot[m][2] += (ab["winner"] == "A") + (ba["winner"] == "A")
        print(f"| {m} | {o} | {ab['winner']}{ab['strength']} ({'ours' if w1 else o}) | {ba['winner']}{ba['strength']} ({'ours' if w2 else o}) | {int(w1)+int(w2)}/2 | {'yes' if w1 == w2 else 'NO (position decided)'} |")
for m, (w, n, a) in tot.items():
    if n: print(f"\n{m}: ours-current won {w}/{n}; 'A' chosen in {a}/{n} runs (position bias = {a/n - 0.5:+.2f} vs 0.5).")
(C / "stats.json").write_text(json.dumps(out, indent=1))
