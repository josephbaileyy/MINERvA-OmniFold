"""Parse every P1N rater output in note-cal/runs/, verify its quotes against the rated piece, tabulate scores.

usage: python3 -I analyze.py NOTECAL      writes NOTECAL/results.json and prints tables
Quote verification is the calibration's rule (cal/tools/analyze.py): a quote occurs when its letters and digits
(NFKC, case-folded, all else removed) are a contiguous substring of the piece's ('exact'), or occur as at most 4
contiguous pieces (first >= 20 chars, others >= 6) within 5000 characters ('gapped': pdftotext interleaving).
"""
import json, re, statistics as st, sys, unicodedata
from pathlib import Path

C = Path(sys.argv[1])
meta = {m["id"]: m for m in json.loads((C / "pieces" / "pieces.json").read_text())}


def key(s):
    s = unicodedata.normalize("NFKC", s).casefold()
    return "".join(ch for ch in s if ch.isalnum())


doc_key, doc_words = {}, {}
for d in sorted(p.name for p in (C / "inputs").iterdir() if p.is_dir()):
    t = (C / "inputs" / d / "chapter.txt").read_text(encoding="utf-8")
    doc_key[d], doc_words[d] = key(t), len(t.split())


def locate(d, q):
    k, dk = key(q), doc_key[d]
    if len(k) < 10:
        return None
    i = dk.find(k)
    if i >= 0:
        return (i, i + len(k), "exact")
    rest, anchor, pieces, lo_all, hi_all = k, None, 0, None, None
    while rest and pieces < 4:
        lo, hi, best = (6 if pieces else 20), len(rest), None
        w0 = 0 if anchor is None else max(0, anchor - 5000)
        while lo <= hi:
            mid = (lo + hi) // 2
            j = dk.find(rest[:mid], w0, None if anchor is None else anchor + 5000 + mid)
            if j >= 0: best, lo = (j, mid), mid + 1
            else: hi = mid - 1
        if not best:
            return None
        j, n = best
        if anchor is None: anchor = j
        lo_all = j if lo_all is None else min(lo_all, j); hi_all = j + n if hi_all is None else max(hi_all, j + n)
        rest, pieces = rest[n:], pieces + 1
    return None if rest else (lo_all, hi_all, "gapped")


def parse(t):
    m = re.search(r"RATING:\s*\**\s*([0-5](?:\.\d+)?)", t)
    score = float(m.group(1)) if m else None
    j = re.search(r"JUSTIFICATION:\s*(.*)", t)
    qs = []
    for m in re.finditer(r'QUOTE:\s*\**\s*[“"](.*?)[”"]\s*\**\s*\n\s*\**\s*REWRITE:\s*(.*?)(?=\n\s*\d+\.\s*QUOTE:|\Z)', t, re.S):
        qs.append((m.group(1), " ".join(m.group(2).split())))
    return score, (j.group(1).strip() if j else ""), qs


runs = {}
for f in sorted((C / "runs").glob("P1N__*.md")):
    p, d, m, r = f.stem.split("__")
    t = f.read_text(encoding="utf-8", errors="replace")
    score, just, qs = parse(t)
    runs[f.stem] = dict(doc=d, model=m, run=r, score=score, justification=just,
                        quotes=[dict(q=q, rewrite=rw, span=locate(d, q)) for q, rw in qs])
cells = {}
for rid, R in runs.items():
    cells.setdefault((R["doc"], R["model"]), []).append((R["run"], R["score"]))
out = {"runs": runs, "cells": {}}
for (d, m), v in sorted(cells.items()):
    xs = [s for _, s in sorted(v) if s is not None]
    out["cells"][f"{d}|{m}"] = dict(runs=[s for _, s in sorted(v)], mean=st.mean(xs) if xs else None)
(C / "results.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))

fmt = lambda x: "-" if x is None else f"{x:.2f}"
print("doc\twords\tsol runs\tsol mean\tgemini\tquotes ok/total")
for d in sorted(doc_key):
    s = out["cells"].get(f"{d}|sol", {}); g = out["cells"].get(f"{d}|gemini", {})
    qq = [q for R in runs.values() if R["doc"] == d for q in R["quotes"]]
    print(f"{d}\t{doc_words[d]}\t{s.get('runs')}\t{fmt(s.get('mean'))}\t{g.get('runs')}\t{sum(1 for q in qq if q['span'])}/{len(qq)}")
bad = [(rid, q["q"][:90]) for rid, R in runs.items() for q in R["quotes"] if not q["span"]]
print(f"\nunverified quotes: {len(bad)}")
for b in bad:
    print("  ", b)
short = [rid for rid, R in runs.items() if R["score"] is None or len(R["quotes"]) != 3]
print("runs with missing score or != 3 quotes:", short)
