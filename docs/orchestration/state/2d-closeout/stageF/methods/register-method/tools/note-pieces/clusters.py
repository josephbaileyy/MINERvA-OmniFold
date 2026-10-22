"""Group the verified note quotes into distinct passages (span overlap) and complaint types (labels.py).

usage: python3 -I clusters.py NOTECAL     prints tables; writes NOTECAL/complaints.json
Each quote gets the labels of the label whose prefix occurs EARLIEST in it (letters/digits match). The script
fails if any note quote matches no label, or any label matches no quote.
"""
import json, sys, unicodedata
from collections import defaultdict
from pathlib import Path

C = Path(sys.argv[1])
sys.path.insert(0, str(C / "tools"))
from labels import LABELS  # noqa: E402


def key(s):
    return "".join(ch for ch in unicodedata.normalize("NFKC", s).casefold() if ch.isalnum())


R = json.loads((C / "results.json").read_text())["runs"]
items, used = [], set()
for rid, r in sorted(R.items()):
    if not r["doc"].startswith("N"):
        continue
    for qi, q in enumerate(r["quotes"]):
        assert q["span"], (rid, q["q"][:60])
        kq = key(q["q"]); best = None
        for li, (d, pre, labs) in enumerate(LABELS):
            if d == r["doc"]:
                j = kq.find(key(pre))
                if j >= 0 and (best is None or j < best[0]):
                    best = (j, li)
        assert best, f"unlabelled quote {rid} q{qi + 1}: {q['q'][:80]}"
        used.add(best[1])
        items.append(dict(run=rid, doc=r["doc"], model=r["model"], q=" ".join(q["q"].split()), s=q["span"][0],
                          e=q["span"][1], labels=LABELS[best[1]][2], label_id=best[1]))
unused = [LABELS[i][:2] for i in range(len(LABELS)) if i not in used]
assert not unused, f"labels matching no quote: {unused}"

# distinct passages: overlapping spans within a piece
passages = []
for d in sorted({i["doc"] for i in items}):
    its = sorted((i for i in items if i["doc"] == d), key=lambda i: i["s"])
    for it in its:
        if passages and passages[-1]["doc"] == d and it["s"] < passages[-1]["e"]:
            p = passages[-1]; p["items"].append(it); p["e"] = max(p["e"], it["e"])
        else:
            passages.append(dict(doc=d, s=it["s"], e=it["e"], items=[it]))
for p in passages:
    p["runs"] = sorted({i["run"] for i in p["items"]}); p["models"] = sorted({i["model"] for i in p["items"]})
    p["labels"] = []
    for i in p["items"]:
        for l in i["labels"]:
            if l not in p["labels"]: p["labels"].append(l)
    p["primary"] = p["items"][0]["labels"][0]
    p["rep"] = min(p["items"], key=lambda i: len(i["q"]))["q"]

print(f"{len(items)} verified note quotes from {len({i['run'] for i in items})} runs; {len(passages)} distinct passages")
types = ["HIST", "BOOK", "CODE", "HEDGE", "JARG", "PROC", "META", "DENSE"]
rows = []
for t in types:
    qi = [i for i in items if t in i["labels"]]; qp = [i for i in items if i["labels"][0] == t]
    ps = [p for p in passages if t in p["labels"]]; pp = [p for p in passages if p["primary"] == t]
    rows.append((t, len(qi), len(qp), len(ps), len(pp), len({p["doc"] for p in ps}),
                 sum(1 for i in qi if i["model"] == "sol"), sum(1 for i in qi if i["model"] == "gemini")))
rows.sort(key=lambda r: (-r[1], -r[3]))
print("type\tquotes(any)\tquotes(primary)\tpassages(any)\tpassages(primary)\tpieces\tsol quotes\tgemini quotes")
for r in rows:
    print("\t".join(map(str, r)))
print("\nper piece: passages flagged by >=2 runs")
for p in sorted(passages, key=lambda p: (p["doc"], -len(p["runs"]))):
    print(f"{p['doc']}\t{len(p['runs'])} runs ({','.join(p['models'])})\t{'/'.join(p['labels'])}\t{p['rep'][:150]}")
(C / "complaints.json").write_text(json.dumps(dict(items=items, passages=passages, types=rows), indent=1,
                                              ensure_ascii=False))
