"""Count every new source in repin_list.tsv at a #977 head (argv[1]). Run from any checkout of the repo. Writes nothing.
LaTeX comments (an unescaped % to the end of the line) are stripped and whitespace runs collapse, as the re-pinned build
will read. resource rows must count 1; fd16row rows must each be a row of tab:fd16 with \\newline read as a space; keys
rows must each be printed (\\fvval{key} at least once); term rows (old|new) need new printed and old absent;
drop and code rows are listed only. Exit 1 if any resource,
fd16row, keys or term check fails."""
import os, re, subprocess, sys

N = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = {"paper": "paper_body.tex", "supplement": "supplemental_body.tex", "abstract": "main_paper.tex"}


def text(doc):
    raw = subprocess.run(["git", "show", f"{N}:docs/analysis-note/{DOCS[doc]}"], capture_output=True, text=True,
                         check=True).stdout
    return re.sub(r"\s+", " ", re.sub(r"(?m)(?<!\\)%.*$", "", raw)).strip()


norm = lambda s: re.sub(r"\s+", " ", s).strip()
cache, bad = {}, 0
rows = [l.split("\t") for l in open(os.path.join(HERE, "repin_list.tsv")).read().splitlines()
        if l and not l.startswith("#") and not l.startswith("id\t")]
print(f"#977 head {N}; {len(rows)} rows")
for rid, ruled, resp, sites, action, doc, quote, note in rows:
    if action in ("resource", "code") and doc in DOCS and quote != "-":
        t = cache.setdefault(doc, text(doc))
        c = t.count(norm(quote))
        ok = c == 1
        bad += (not ok) and action == "resource"
        print(f"{'OK ' if ok else 'BAD'} {rid:6} {action:8} {doc:10} count={c}  {quote[:70]}")
    elif action == "fd16row":
        t = cache.setdefault(doc, text(doc))
        i = t.find(r"\label{tab:fd16}")
        b, e = t.rfind(r"\begin{table", 0, i), t.find(r"\end{table", i)
        tab = re.sub(r"\\newline\s*", " ", t[b:e]) if i >= 0 else ""
        for q in quote.split("|"):
            ok = bool(re.search(r"(^|\\\\|\\midrule|\\toprule)\s*" + re.escape(q) + r"\s*&", tab))
            bad += not ok
            print(f"{'OK ' if ok else 'BAD'} {rid:6} fd16row  {doc:10} {q}")
    elif action == "term":
        t = cache.setdefault(doc, text(doc))
        old, new = quote.split("|")
        co, cn = t.lower().count(old.lower()), t.lower().count(new.lower())
        ok = cn >= 1 and co == 0
        bad += not ok
        print(f"{'OK ' if ok else 'BAD'} {rid:6} term     {doc:10} old={co} new={cn}  {old} -> {new}")
    elif action == "keys":
        t = cache.setdefault(doc, text(doc))
        for k in quote.split("|"):
            c = t.count("\\fvval{%s}" % k)
            ok = c >= 1
            bad += not ok
            print(f"{'OK ' if ok else 'BAD'} {rid:6} keys     {doc:10} printed={c}  \\fvval{{{k}}}")
    else:
        print(f"--  {rid:6} {action:8} {sites}  {note[:80]}")
print("REPIN-CHECK", "PASS" if not bad else f"FAIL ({bad})")
sys.exit(1 if bad else 0)
