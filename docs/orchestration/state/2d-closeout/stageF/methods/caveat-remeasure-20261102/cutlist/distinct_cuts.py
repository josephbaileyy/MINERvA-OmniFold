"""distinct_cuts.py -- the paper's distinct caveats, classed, and the moves that would lower their number.

usage: python3 -I distinct_cuts.py INV.tsv BLIND.txt WORDS PAPERDIR OUT_PREFIX [--self-test]

INV.tsv is a coded inventory of the paper (caveat-study CODEBOOK.md), BLIND.txt the blinded text it was coded on, WORDS
its blinded word count, PAPERDIR the docs/analysis-note directory it was built from. A caveat is the caveat study's
distinct unit, (kind, issue label case-folded), numbered C01... in order of first appearance in INV.

classes.tsv gives every caveat a class:
  R      resolvable by a campaign, which `campaign` names (or says none is declared);
  M      could live only in the note, which keeps the fact (`note`: the note register row, or NOTE FIRST);
  merge  it and the caveats named in the same move are one issue that can be stated once;
  K      inherent.
moves.tsv gives each M or merge move: its caveats, the distinct caveats it removes, where the single statement goes,
the proposed statement (`proposal`), the text that must stay from a sentence the move rewrites (`retain`), and flags.
The run FAILS if classes.tsv and INV disagree on any caveat, if a caveat is classed M or merge without a move, or if a
move names a caveat whose class does not point back to it.

Words saved by a move = words of the sentences that state its caveats (outside the abstract, which is protected), less
the proposal and the retained text. A sentence that also states a caveat outside the move cannot leave, so it is not
counted. A join-only merge (no proposal) and figure text count 0 words. The saving is a sentence-level estimate: the
paper lane must read every proposal against the sentences it replaces, so that no fact leaves paper plus note.
Moves are ranked by distinct caveats removed, then words saved; the cumulative distinct caveats per 1,000 words are
reported in that order. Writes OUT_PREFIX.json and OUT_PREFIX.md.
"""
import collections
import csv
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLASSES = {"R", "M", "merge", "K"}


def _mod(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def norm(t):
    t = t.replace("­", "")
    t = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", t)
    return re.sub(r"\s+", " ", t).strip()


def sentence(text_n, quote):
    q = norm(quote)
    i = text_n.find(q)
    if i < 0:
        return q
    a = max(text_n.rfind(". ", 0, i), text_n.rfind("? ", 0, i))
    a = 0 if a < 0 else a + 2
    b = text_n.find(". ", i + len(q) - 1)
    return text_n[a:len(text_n) if b < 0 else b + 1]


def words(t):
    return sum(1 for x in t.split() if re.search(r"[A-Za-z0-9]", x))


def read_tsv(p):
    with open(p, encoding="utf-8") as f:
        return [{k: (v or "").strip() for k, v in r.items()} for r in csv.DictReader(f, delimiter="\t",
                                                                                     quoting=csv.QUOTE_NONE)]


def build(inv, blind, nwords, paperdir, prefix, classes=HERE / "classes.tsv", moves=HERE / "moves.tsv", locate=True):
    nwords = int(nwords)
    groups = collections.OrderedDict()
    for r in read_tsv(inv):
        groups.setdefault((r["kind"], r["issue"].lower()), []).append(r)
    keys = list(groups)
    cls = read_tsv(classes)
    mv = {m["move"]: m for m in read_tsv(moves)}
    errors = []
    if len(cls) != len(keys):
        errors.append(f"classes.tsv has {len(cls)} rows, the inventory {len(keys)} caveats")
    for i, (c, k) in enumerate(zip(cls, keys), 1):
        if c["cid"] != f"C{i:02d}" or (c["kind"], c["issue"].lower()) != k:
            errors.append(f"row {i}: classes.tsv says {c['cid']} {c['kind']}|{c['issue']}, the inventory {k}")
        if c["cls"] not in CLASSES:
            errors.append(f"{c['cid']}: class {c['cls']!r}")
        if c["cls"] in ("M", "merge") and c["move"] not in mv:
            errors.append(f"{c['cid']}: class {c['cls']} names no move in moves.tsv ({c['move']!r})")
    by_cid = {c["cid"]: c for c in cls}
    for m in mv.values():
        for cid in m["caveats"].split():
            if by_cid.get(cid, {}).get("move") != m["move"]:
                errors.append(f"{m['move']}: names {cid}, whose class row does not point back to it")
    if errors:
        print("CUT LIST FAILED:\n  " + "\n  ".join(errors))
        sys.exit(1)

    text_n = norm(Path(blind).read_text(encoding="utf-8", errors="replace"))
    where = lambda q: None
    if locate:
        loc = _mod(HERE.parents[1] / "limitations-register" / "locate.py", "locate")
        stream, _ = loc.stream_of(paperdir, "main_paper")
        idx = collections.defaultdict(list)
        toks = [s[0] for s in stream]
        for k in range(len(toks) - 3):
            idx[tuple(toks[k:k + 4])].append(k)

        def where(q):
            f, line, cov = loc.locate(q, stream, idx)
            return (f"{f}.tex:{line}" + ("" if cov >= 0.8 else " (partial)")) if f else "not in the TeX (figure text?)"

    caveats, sent_owner = [], collections.defaultdict(set)
    for i, k in enumerate(keys, 1):
        cid = f"C{i:02d}"
        st = []
        for r in groups[k]:
            s = sentence(text_n, r["quote"])
            st.append({"loc": r["loc"], "tex": where(r["quote"]), "quote": r["quote"], "sentence": s})
            if r["loc"] != "abstract":
                sent_owner[s].add(cid)
        c = by_cid[cid]
        caveats.append({"cid": cid, "kind": k[0], "issue": k[1], "statements": len(st), "class": c["cls"],
                        "q": c["q"], "move": c["move"], "campaign": c["campaign"], "note": c["note"],
                        "comment": c["comment"], "where": st})
    cav = {c["cid"]: c for c in caveats}

    out_moves = []
    for m in mv.values():
        ids = set(m["caveats"].split())
        sents, shared = [], []
        for cid in sorted(ids):
            for s in cav[cid]["where"]:
                if s["loc"] == "abstract" or s["sentence"] in sents or s["sentence"] in shared:
                    continue
                (sents if sent_owner[s["sentence"]] <= ids else shared).append(s["sentence"])
        join_only = m["type"] == "merge" and not m["proposal"]
        figure = all(s["tex"].startswith("not in the TeX") for cid in ids for s in cav[cid]["where"]) if locate else False
        saved = 0 if (join_only or figure) else words(" ".join(sents)) - words(m["proposal"]) - words(m["retain"])
        out_moves.append({"move": m["move"], "type": m["type"], "caveats": m["caveats"].split(),
                          "removes": int(m["removes"]), "home": m["home"], "proposal": m["proposal"],
                          "retain": m["retain"], "flags": m["flags"], "words_saved": saved,
                          "sentences_replaced": len(sents), "shared_sentences_kept": shared,
                          "q": sorted({q for cid in ids for q in cav[cid]["q"].split()})})
    out_moves.sort(key=lambda m: (-m["removes"], -m["words_saved"]))
    d, w, cum = len(keys), nwords, []
    for m in out_moves:
        d -= m["removes"]
        w -= m["words_saved"]
        m["after"] = {"distinct": d, "words": w, "distinct_per_1k": round(d / w * 1000, 2)}
    clean = [m for m in out_moves if "NOTE FIRST" not in m["flags"] and "figure" not in m["flags"]]
    dc = len(keys) - sum(m["removes"] for m in clean)
    wc = nwords - sum(m["words_saved"] for m in clean)
    r_cav = [c for c in caveats if c["class"] == "R"]
    summary = {"inventory": str(inv), "words": nwords, "distinct": len(keys),
               "distinct_per_1k": round(len(keys) / nwords * 1000, 2),
               "classes": dict(collections.Counter(c["class"] for c in caveats)),
               "all_moves": {"moves": len(out_moves), "removes": sum(m["removes"] for m in out_moves),
                             "words_saved": sum(m["words_saved"] for m in out_moves),
                             "after": out_moves[-1]["after"] if out_moves else None},
               "moves_without_prerequisite": {"moves": len(clean), "distinct": dc, "words": wc,
                                              "distinct_per_1k": round(dc / wc * 1000, 2)},
               "plus_R_if_every_campaign_resolves": {
                   "R_caveats": len(r_cav),
                   "distinct_per_1k": round((out_moves[-1]["after"]["distinct"] - len(r_cav)) /
                                            out_moves[-1]["after"]["words"] * 1000, 2) if out_moves else None},
               "target_4_5_needs_distinct_at_most": int(4.5 * (out_moves[-1]["after"]["words"] if out_moves else nwords) / 1000),
               "K": sum(c["class"] == "K" for c in caveats)}
    Path(f"{prefix}.json").write_text(json.dumps({"summary": summary, "moves": out_moves, "caveats": caveats},
                                                 indent=1, ensure_ascii=False) + "\n")
    md = ["| rank | move | type | caveats (q) | removes | words saved | distinct /1k after | goes to | flags |",
          "|---|---|---|---|---|---|---|---|---|"]
    for i, m in enumerate(out_moves, 1):
        md.append(f"| {i} | {m['move']} | {m['type']} | {' '.join(m['caveats'])} ({', '.join(m['q']) or '–'}) | "
                  f"{m['removes']} | {m['words_saved']} | {m['after']['distinct_per_1k']} | {m['home']} | {m['flags'] or ''} |")
    md += ["", "| caveat | kind | issue | statements | class | q | move | campaign / note row | first location |",
           "|---|---|---|---|---|---|---|---|---|"]
    for c in caveats:
        first = next((s["tex"] for s in c["where"] if s["loc"] != "abstract"), c["where"][0]["tex"])
        md.append(f"| {c['cid']} | {c['kind']} | {c['issue']} | {c['statements']} | {c['class']} | {c['q'] or '–'} | "
                  f"{c['move'] or '–'} | {c['campaign'] or c['note'] or '–'} | {first} |")
    Path(f"{prefix}.md").write_text("\n".join(md) + "\n")
    print(json.dumps(summary, indent=1))


def self_test():
    import contextlib, io, tempfile
    d = Path(tempfile.mkdtemp())
    (d / "blind.txt").write_text("Intro. The band is not validated. The band fails at high W. We assume a flat flux.")
    (d / "inv.tsv").write_text("n\tkind\tloc\tpolarity\tquant\tassigned\tissue\tquote\n"
                               "1\tc\tinline\tneg\tno\tno\tband\tThe band is not validated.\n"
                               "2\tc\tinline\tneg\tno\tno\tband high w\tThe band fails at high W.\n"
                               "3\tc\tinline\tpos\tno\tno\tflux\tWe assume a flat flux.\n")
    hdr = "cid\tkind\tissue\tcls\tq\tmove\tcampaign\tnote\tcomment\n"
    good = hdr + "C01\tc\tband\tmerge\t\tMV1\t\t\t\nC02\tc\tband high w\tmerge\t\tMV1\t\t\t\nC03\tc\tflux\tK\t\t\t\t\t\n"
    (d / "moves.tsv").write_text("move\ttype\tcaveats\tremoves\thome\tproposal\tretain\tflags\n"
                                 "MV1\tmerge\tC01 C02\t1\there\tThe band is not validated and fails at high W.\t\t\n")
    ok = True
    for text, want in ((good, 0), (good.replace("C03\tc\tflux\tK", "C03\tc\tflux\tM"), 1),
                       (good.replace("C02\tc\tband high w", "C02\tc\tother"), 1)):
        (d / "classes.tsv").write_text(text)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                build(d / "inv.tsv", d / "blind.txt", 1000, d, d / "out", d / "classes.tsv", d / "moves.tsv", False)
            code = 0
        except SystemExit as e:
            code = e.code
        ok &= code == want
    (d / "classes.tsv").write_text(good)
    with contextlib.redirect_stdout(io.StringIO()):
        build(d / "inv.tsv", d / "blind.txt", 1000, d, d / "out", d / "classes.tsv", d / "moves.tsv", False)
    m = json.load(open(d / "out.json"))["moves"][0]
    ok &= m["words_saved"] == (5 + 6) - 10 and m["after"]["distinct"] == 2
    print("SELF-TEST ::", "PASS" if ok else "FAIL", "(a consistent table passes; an M caveat with no move fails; a class "
          "row that disagrees with the inventory fails; words saved = replaced sentences less the proposal)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    self_test() if "--self-test" in sys.argv else build(*sys.argv[1:6])
