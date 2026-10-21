"""Parse every rater output in runs/, verify P3 (and P1) quotes against the rated document, compute statistics.

usage: python3 -I analyze.py CALDIR      writes CALDIR/results.json and prints tables
Quote verification: a quote counts as occurring when its letters and digits (NFKC, case-folded, every other
character removed) form a contiguous substring of the document's letters and digits. Whitespace, line-break
hyphenation, quote marks and punctuation are therefore ignored; any changed, added or dropped word fails.
"""
import json, math, re, statistics as st, sys, unicodedata
from pathlib import Path

C = Path(sys.argv[1])
DOCS = ["anchorA", "anchorB", "anchorC", "ours-current", "ours-old", "ours-holds"]
MODELS = ["sol", "gemini"]


def key(s):
    s = unicodedata.normalize("NFKC", s).casefold()
    return "".join(ch for ch in s if ch.isalnum())


doc_text = {d: (C / "docs" / f"{d}.blind.txt").read_text(encoding="utf-8") for d in DOCS}
doc_key = {d: key(t) for d, t in doc_text.items()}
doc_words = {d: len(t.split()) for d, t in doc_text.items()}


def parse_rating_p1(t):
    m = re.search(r"RATING:\s*\**\s*([0-5](?:\.\d+)?)", t)
    return float(m.group(1)) if m else None


def parse_rating_p0(t):
    # isolate the answer to question 2
    m = re.search(r"(?ms)^\W*(?:\*\*)?(?:Q?2[.):]|2\s*[-–—]|#+\s*2\b).*?(?=^\W*(?:\*\*)?(?:Q?3[.):]|3\s*[-–—]|#+\s*3\b))", t)
    sec = m.group(0) if m else t
    pats = [r"(?i)rat(?:ing|e)[^0-9\n]{0,25}([1-5](?:\.\d)?)\s*(?:/\s*5|out of 5)?",
            r"([1-5](?:\.\d)?)\s*/\s*5", r"([1-5](?:\.\d)?)\s*out of\s*5"]
    for p in pats:
        mm = re.search(p, sec)
        if mm:
            return float(mm.group(1)), sec[max(0, mm.start() - 60): mm.end() + 20].replace("\n", " ")
    return None, sec[:200].replace("\n", " ")


def quotes_p3(t):
    out = []
    for line in t.splitlines():
        m = re.match(r'^\s*(?:[-*\d.]+\s*)?\[([^\]]+)\]\s*[“"](.*)[”"]\s*$', line.strip())
        if m:
            out.append((m.group(1).strip().lower(), m.group(2)))
    return out


def quotes_p1(t):
    return [m.group(1) for m in re.finditer(r'QUOTE:\s*\**\s*[“"](.*?)[”"]\s*\**\s*\n\s*\**\s*REWRITE', t, re.S)]


def locate(d, q):
    """(start, end, kind). kind 'exact': the quote's letters/digits form one contiguous run of the document's.
    kind 'gapped': they occur as at most 4 contiguous pieces (first >= 20 chars, others >= 6), every later piece
    within 5000 characters of the first, in either order -- the sentence is in the text, but pdftotext interleaved
    a float, a footnote or the other column inside it."""
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


runs = {}
for f in sorted((C / "runs").glob("*.md")):
    parts = f.stem.split("__")
    if len(parts) != 4:
        continue
    p, d, m, r = parts
    runs[f.stem] = dict(prompt=p, doc=d, model=m, run=r, text=f.read_text(encoding="utf-8", errors="replace"))

res = {"cells": {}, "runs": {}}
for rid, R in runs.items():
    p, d, m, t = R["prompt"], R["doc"], R["model"], R["text"]
    rec = {"prompt": p, "doc": d, "model": m, "run": R["run"]}
    if p == "P1":
        rec["score"] = parse_rating_p1(t)
        qs = quotes_p1(t)
        rec["quotes"] = [{"q": q, "span": locate(d, q)} for q in qs]
    elif p in ("P0", "P0n"):
        rec["score"], rec["snippet"] = parse_rating_p0(t)
    elif p == "P3":
        qs = quotes_p3(t)
        seen, kept, bad, dup = set(), [], [], 0
        for cat, q in qs:
            k = key(q)
            if k in seen:
                dup += 1; continue
            seen.add(k)
            sp = locate(d, q)
            (kept if sp else bad).append({"cat": cat, "q": q, "span": sp})
        rec.update(n_listed=len(qs), n_dup=dup, n_verified=len(kept), n_unverified=len(bad),
                   n_exact=sum(1 for x in kept if x["span"][2] == "exact"), score_exact=1000 * sum(1 for x in kept if x["span"][2] == "exact") / doc_words[d],
                   score=1000 * len(kept) / doc_words[d], quotes=kept, rejected=bad,
                   has_end=bool(re.search(r"(?m)^\s*END\s*$", t)))
    elif p == "P2":
        w = re.search(r"WINNER:\s*\**\s*([AB])\b", t)
        s = re.search(r"STRENGTH:\s*\**\s*([123])\b", t)
        rec["winner"] = w.group(1) if w else None
        rec["strength"] = int(s.group(1)) if s else None
        rec["score"] = None
    res["runs"][rid] = rec

# cells
cells = {}
for rid, rec in res["runs"].items():
    if rec["prompt"] == "P2":
        continue
    cells.setdefault((rec["prompt"], rec["model"], rec["doc"]), []).append((rec["run"], rec["score"]))
for (p, m, d), v in sorted(cells.items()):
    v = sorted(v)
    xs = [s for _, s in v if s is not None]
    res["cells"][f"{p}|{m}|{d}"] = dict(runs=[s for _, s in v], n=len(xs), mean=st.mean(xs) if xs else None,
                                       sd=st.stdev(xs) if len(xs) > 1 else None)
(C / "results.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
for k, c in res["cells"].items():
    fmt = lambda x: "-" if x is None else f"{x:.2f}"
    print(f"{k:40s} runs={[None if s is None else round(s, 2) for s in c['runs']]} mean={fmt(c['mean'])} sd={fmt(c['sd'])}")
for rid, rec in sorted(res["runs"].items()):
    if rec["prompt"] == "P2":
        print(rid, rec["winner"], rec["strength"])
    if rec["prompt"] == "P3":
        print(rid, f"listed={rec['n_listed']} dup={rec['n_dup']} ok={rec['n_verified']} (exact {rec['n_exact']}) bad={rec['n_unverified']} END={rec['has_end']}")
