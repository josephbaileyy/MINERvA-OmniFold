#!/usr/bin/env python3
"""Recount the note's caveat density and words, the cost list's measure (note-n3/content-reduction.md §2, §5).

usage: recount.py NOTEDIR PDF INV.tsv [INV.tsv ...] [--json OUT]

NOTEDIR is a docs/analysis-note directory; PDF is its built main_note.pdf; INV are the caveat study's inventories of
the note (caveat-study/inv/ours-note-body.tsv, ours-note-app.tsv). For each inventory row it finds the longest run
of the quote's alphabetic tokens in the note's TeX sources (comments and macro names stripped): "found" if the run
covers >= 80% of the quote (and >= 4 tokens), "partial" if it covers >= 6 tokens or >= half, else "gone". It reports:
  - live statements (found; found + partial) and live distinct (kind, issue) pairs on each basis;
  - restatements per distinct caveat;
  - TeX words of the source files (comment-stripped, tokens holding a letter or digit) and blinded PDF words
    (pdftotext, then the caveat study's blinding: abstract, body and appendices; no title block, contents,
    acknowledgments, references, e-mail lines or page numbers);
  - statements and distinct caveats per 1,000 blinded words.
The method is the cost list's; this file ports it from that list's scratch tools (locate.py and impact.py) with paths
as arguments (director, 2026-10-27).
"""
import collections
import csv
import json
import os
import re
import subprocess
import sys
import tempfile

FILES = ("main_note sec_execsummary result_status_rows sec_intro sec_experiment selection_features sec_method "
         "sec_systematics sec_validation sec_results sec_3d scalar_kinematics sec_eavailw sec_5d sec_joint sec_fps "
         "sec_summary app_guide app_statmethods app_statmethods_nd app_negweight app_response_mismatch app_landscape "
         "app_pet_pointer app_release app_codebase").split()
TOK = re.compile(r"[a-z]+")


def stream_of(notedir):
    stream, words = [], 0
    for f in FILES:
        for i, line in enumerate(open(os.path.join(notedir, f + ".tex"), encoding="utf-8"), 1):
            line = re.sub(r"(?<!\\)%.*", "", line)
            words += sum(1 for x in line.split() if re.search(r"[A-Za-z0-9]", x))
            for t in TOK.findall(re.sub(r"\\[A-Za-z]+", " ", line).lower()):
                stream.append((t, f, i))
    return stream, words


def classify(rows, stream):
    toks = [s[0] for s in stream]
    idx = collections.defaultdict(list)
    for k in range(len(toks) - 3):
        idx[tuple(toks[k:k + 4])].append(k)
    out = []
    for r in rows:
        qt = TOK.findall(r["quote"].lower().replace("’", "'"))
        best = 0
        for j in range(len(qt) - 3):
            for k in idx.get(tuple(qt[j:j + 4]), []):
                n = 0
                while j + n < len(qt) and k + n < len(toks) and toks[k + n] == qt[j + n]:
                    n += 1
                best = max(best, n)
        n = len(qt)
        status = ("found" if n and best >= max(4, int(0.8 * n))
                  else "partial" if best >= 6 or (n and best >= 0.5 * n) else "gone")
        out.append((r, status))
    return out


def blinded_words(pdf):
    with tempfile.TemporaryDirectory() as d:
        txt = os.path.join(d, "note.txt")
        subprocess.run(["pdftotext", pdf, txt], check=True)
        L = open(txt, encoding="utf-8", errors="replace").read().split("\n")
    idx = lambda rx, lo=0: next(i for i in range(lo, len(L)) if re.match(rx, L[i].lstrip("\f")))
    a = idx(r"Abstract$") + 1
    t0 = idx(r"Contents$")
    t1 = idx(r"Introduction and motivation$", t0 + 10)
    k0 = idx(r"Acknowledgments$", t1)
    g = idx(r"Guide to the appendices$", k0)
    r = idx(r"References$", g)
    keep = [l for l in L[a:t0] + L[t1:k0] + L[g:r] if not re.match(r"^\s*\d{1,3}\s*$", l) and "@stanford.edu" not in l]
    return sum(1 for x in " ".join(keep).split() if re.search(r"[A-Za-z0-9]", x))


def main(argv):
    out_json = None
    if "--json" in argv:
        i = argv.index("--json"); out_json = argv[i + 1]; del argv[i:i + 2]
    notedir, pdf, invs = argv[0], argv[1], argv[2:]
    rows = [r for p in invs for r in csv.DictReader(open(p, encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE)]
    stream, tex_words = stream_of(notedir)
    cls = classify(rows, stream)
    bw = blinded_words(pdf)
    key = lambda r: (r["kind"], r["issue"].strip().lower())
    res = {"inventory_rows": len(rows), "tex_words": tex_words, "blinded_words": bw}
    for basis, ok in (("found", {"found"}), ("found_partial", {"found", "partial"})):
        live = [r for r, s in cls if s in ok]
        distinct = {key(r) for r in live}
        res[basis] = {"statements": len(live), "distinct": len(distinct),
                      "restatements_per_caveat": round(len(live) / max(len(distinct), 1), 3),
                      "statements_per_1000": round(1000 * len(live) / bw, 2),
                      "distinct_per_1000": round(1000 * len(distinct) / bw, 2)}
    res["status_counts"] = dict(collections.Counter(s for _, s in cls))
    print(f"RECOUNT :: {notedir}")
    print(f"  inventory rows {len(rows)}: {res['status_counts']}")
    print(f"  words: TeX {tex_words}, blinded PDF {bw}")
    for basis in ("found", "found_partial"):
        v = res[basis]
        print(f"  {basis:14} statements {v['statements']:4}  distinct {v['distinct']:4}  restatements/caveat "
              f"{v['restatements_per_caveat']:.3f}  statements/1000 {v['statements_per_1000']:.2f}  "
              f"distinct/1000 {v['distinct_per_1000']:.2f}")
    if out_json:
        json.dump(res, open(out_json, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
